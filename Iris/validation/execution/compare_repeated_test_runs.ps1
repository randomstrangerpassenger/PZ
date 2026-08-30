[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepositoryRoot,
    [Parameter(Mandatory = $true)][string]$Commit,
    [Parameter(Mandatory = $true)][string]$ClaimId,
    [Parameter(Mandatory = $true)][string]$EnvironmentReceipt,
    [Parameter(Mandatory = $true)][string]$RunAOrchestrationReceipt,
    [Parameter(Mandatory = $true)][string]$RunBOrchestrationReceipt,
    [Parameter(Mandatory = $true)][string]$AttemptRoot,
    [Alias('ExecutionContext')]
    [ValidateSet('standalone_full_gate', 'composite_baseline_admission_chain_stage_6')]
    [string]$BaselineAdmissionExecutionContext = 'standalone_full_gate',
    [ValidateSet('none', 'required_environment_apply', 'environment_restore')]
    [string]$FailureInjection = 'none'
)

$ErrorActionPreference = 'Stop'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-BytesSha256([byte[]]$Bytes) {
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant()
    }
    finally { $algorithm.Dispose() }
}

function ConvertTo-StableJsonBytes([object]$Payload) {
    $json = $Payload | ConvertTo-Json -Depth 24
    $json = $json.Replace("`r`n", "`n")
    if (-not $json.EndsWith("`n")) { $json += "`n" }
    return (New-Object System.Text.UTF8Encoding($false)).GetBytes($json)
}

function Quote-NativeArgument([string]$Value) {
    if ($Value.Length -eq 0) { return '""' }
    if ($Value -notmatch '[\s"]') { return $Value }
    $builder = New-Object System.Text.StringBuilder
    [void]$builder.Append('"')
    $backslashes = 0
    foreach ($character in $Value.ToCharArray()) {
        if ($character -eq '\') { $backslashes += 1; continue }
        if ($character -eq '"') {
            [void]$builder.Append(('\' * (($backslashes * 2) + 1)))
            [void]$builder.Append('"')
            $backslashes = 0
            continue
        }
        if ($backslashes -gt 0) {
            [void]$builder.Append(('\' * $backslashes))
            $backslashes = 0
        }
        [void]$builder.Append($character)
    }
    if ($backslashes -gt 0) { [void]$builder.Append(('\' * ($backslashes * 2))) }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function Invoke-TextProcess(
    [string]$FilePath,
    [string[]]$Arguments,
    [string]$WorkingDirectory
) {
    $info = New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName = $FilePath
    $info.Arguments = (($Arguments | ForEach-Object { Quote-NativeArgument $_ }) -join ' ')
    $info.WorkingDirectory = $WorkingDirectory
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $info
    if (-not $process.Start()) { throw "failed to start process: $FilePath" }
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    return [ordered]@{ exit_code = $process.ExitCode; stdout = $stdout; stderr = $stderr }
}

function Invoke-RawProcess(
    [string]$FilePath,
    [string[]]$Arguments,
    [string]$WorkingDirectory,
    [string]$RawStdoutPath,
    [string]$RawStderrPath
) {
    $info = New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName = $FilePath
    $info.Arguments = (($Arguments | ForEach-Object { Quote-NativeArgument $_ }) -join ' ')
    $info.WorkingDirectory = $WorkingDirectory
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $info
    $stdoutStream = $null
    $stderrStream = $null
    try {
        $stdoutStream = [System.IO.File]::Open($RawStdoutPath, 'CreateNew', 'Write', 'Read')
        $stderrStream = [System.IO.File]::Open($RawStderrPath, 'CreateNew', 'Write', 'Read')
        if (-not $process.Start()) { throw "failed to start process: $FilePath" }
        $script:NativeProcessStarted = $true
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdoutStream)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderrStream)
        $process.WaitForExit()
        [void]$stdoutTask.GetAwaiter().GetResult()
        [void]$stderrTask.GetAwaiter().GetResult()
        return $process.ExitCode
    }
    finally {
        if ($null -ne $stdoutStream) { $stdoutStream.Dispose() }
        if ($null -ne $stderrStream) { $stderrStream.Dispose() }
        $process.Dispose()
    }
}

function Write-JsonNoBomAtomic([string]$Path, [object]$Payload) {
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = Join-Path $parent ('.' + [System.IO.Path]::GetFileName($Path) + '.' + [guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [System.IO.File]::WriteAllBytes($temporary, (ConvertTo-StableJsonBytes $Payload))
        [System.IO.File]::Move($temporary, $Path)
    }
    finally {
        if ([System.IO.File]::Exists($temporary)) {
            [System.IO.File]::Delete($temporary)
        }
    }
}

function Assert-ExternalPath([string]$Repository, [string]$Candidate, [string]$Label) {
    $repo = [System.IO.Path]::GetFullPath($Repository).TrimEnd('\', '/')
    $path = [System.IO.Path]::GetFullPath($Candidate).TrimEnd('\', '/')
    if ($path.Equals($repo, [System.StringComparison]::OrdinalIgnoreCase) -or
        $path.StartsWith($repo + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase) -or
        $repo.StartsWith($path + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label must be disjoint from the repository: $path"
    }
    return $path
}

function Get-EnvironmentState([string]$Name) {
    $value = [Environment]::GetEnvironmentVariable($Name, 'Process')
    if ($null -eq $value) { return [ordered]@{ state = 'absent'; value = $null } }
    if ($value.Length -eq 0) { return [ordered]@{ state = 'empty'; value = '' } }
    return [ordered]@{ state = 'value'; value = $value }
}

function Restore-EnvironmentState([string]$Name, [object]$State) {
    if ($State.state -eq 'absent') { Remove-Item -LiteralPath ("Env:" + $Name) -ErrorAction SilentlyContinue }
    else { [Environment]::SetEnvironmentVariable($Name, [string]$State.value, 'Process') }
}

function Test-EnvironmentStateEqual([object]$Left, [object]$Right) {
    return (
        [string]$Left.state -eq [string]$Right.state -and
        [string]$Left.value -eq [string]$Right.value
    )
}

function Require-Equal([object]$Left, [object]$Right, [string]$Message) {
    if ([string]$Left -ne [string]$Right) { throw $Message }
}

function Resolve-RunChain(
    [string]$Label,
    [string]$ReceiptPath,
    [string]$ExpectedClaimId,
    [object]$ExpectedSubject,
    [object]$ExpectedInterpreter,
    [object]$ExpectedEnvironment,
    [object]$ExpectedImplementation
) {
    $ExpectedRunner = $ExpectedImplementation.runner
    $ExpectedCommon = $ExpectedImplementation.common
    $ExpectedSuccessorPolicy = $ExpectedImplementation.successor_policy
    $path = [System.IO.Path]::GetFullPath($ReceiptPath)
    if (-not [System.IO.File]::Exists($path)) { throw "$Label orchestration receipt is missing" }
    $receiptHash = Get-Sha256 $path
    $receipt = Get-Content -Raw -Encoding UTF8 -LiteralPath $path | ConvertFrom-Json
    Require-Equal $receipt.schema_version 'iris-clean-checkout-orchestration-receipt-v1' "$Label orchestration schema mismatch"
    Require-Equal $receipt.claim_id $ExpectedClaimId "$Label claim ID mismatch"
    Require-Equal $receipt.launch_status 'succeeded' "$Label orchestration did not succeed"
    Require-Equal $receipt.receipt_write_status 'succeeded' "$Label orchestration receipt write status mismatch"
    Require-Equal $receipt.native_exit_code 0 "$Label native exit is not zero"
    $receiptContext = if ([string]::IsNullOrEmpty([string]$receipt.execution_context)) { 'standalone_full_gate' } else { [string]$receipt.execution_context }
    Require-Equal $receiptContext $BaselineAdmissionExecutionContext "$Label orchestration execution context mismatch"
    if ($receipt.environment.configured -ne $true -or $receipt.environment.restored -ne $true) { throw "$Label environment lifecycle is incomplete" }
    Require-Equal $receipt.identity.subject.commit $ExpectedSubject.commit "$Label subject commit mismatch"
    Require-Equal $receipt.identity.subject.tree $ExpectedSubject.tree "$Label subject tree mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$receipt.identity.interpreter.path)) ([System.IO.Path]::GetFullPath([string]$ExpectedInterpreter.path)) "$Label interpreter path mismatch"
    Require-Equal $receipt.identity.interpreter.sha256 $ExpectedInterpreter.sha256 "$Label interpreter mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$receipt.identity.environment_receipt.path)) ([System.IO.Path]::GetFullPath([string]$ExpectedEnvironment.path)) "$Label environment receipt path mismatch"
    Require-Equal $receipt.identity.environment_receipt.sha256 $ExpectedEnvironment.sha256 "$Label environment receipt mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$receipt.identity.implementation.runner.actual_path)) ([System.IO.Path]::GetFullPath([string]$ExpectedRunner.actual_path)) "$Label runner path mismatch"
    Require-Equal $receipt.identity.implementation.runner.git_blob_id $ExpectedRunner.git_blob_id "$Label runner blob mismatch"
    Require-Equal $receipt.identity.implementation.runner.working_sha256 $ExpectedRunner.working_sha256 "$Label runner materialization mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$receipt.identity.implementation.common.actual_path)) ([System.IO.Path]::GetFullPath([string]$ExpectedCommon.actual_path)) "$Label common path mismatch"
    Require-Equal $receipt.identity.implementation.common.git_blob_id $ExpectedCommon.git_blob_id "$Label common blob mismatch"
    Require-Equal $receipt.identity.implementation.common.working_sha256 $ExpectedCommon.working_sha256 "$Label common materialization mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$receipt.identity.implementation.successor_policy.actual_path)) ([System.IO.Path]::GetFullPath([string]$ExpectedSuccessorPolicy.actual_path)) "$Label successor policy path mismatch"
    Require-Equal $receipt.identity.implementation.successor_policy.git_blob_id $ExpectedSuccessorPolicy.git_blob_id "$Label successor policy blob mismatch"
    Require-Equal $receipt.identity.implementation.successor_policy.working_sha256 $ExpectedSuccessorPolicy.working_sha256 "$Label successor policy materialization mismatch"
    foreach ($identityName in @(
        'evidence_policy',
        'evidence_predecessor',
        'evidence_owner_approval',
        'test_taxonomy',
        'required_validations',
        'full_gate_contract',
        'evidence_adoption_receipt'
    )) {
        $actualIdentity = $receipt.identity.implementation.$identityName
        $expectedIdentity = $ExpectedImplementation.$identityName
        if ($null -eq $actualIdentity -or $null -eq $expectedIdentity) { throw "$Label $identityName identity is missing" }
        Require-Equal ([System.IO.Path]::GetFullPath([string]$actualIdentity.actual_path)) ([System.IO.Path]::GetFullPath([string]$expectedIdentity.actual_path)) "$Label $identityName path mismatch"
        Require-Equal $actualIdentity.git_blob_id $expectedIdentity.git_blob_id "$Label $identityName blob mismatch"
        Require-Equal $actualIdentity.working_sha256 $expectedIdentity.working_sha256 "$Label $identityName materialization mismatch"
    }
    if ($receipt.result_receipt.exists -ne $true) { throw "$Label inner run receipt is absent" }
    $innerPath = [System.IO.Path]::GetFullPath([string]$receipt.result_receipt.path)
    if (-not [System.IO.File]::Exists($innerPath)) { throw "$Label inner run receipt file is missing" }
    $innerHash = Get-Sha256 $innerPath
    Require-Equal $innerHash $receipt.result_receipt.sha256 "$Label inner run receipt hash mismatch"
    $inner = Get-Content -Raw -Encoding UTF8 -LiteralPath $innerPath | ConvertFrom-Json
    Require-Equal $inner.status 'PASS' "$Label inner run receipt is not PASS"
    Require-Equal $inner.subject.commit $ExpectedSubject.commit "$Label inner subject commit mismatch"
    Require-Equal $inner.subject.tree $ExpectedSubject.tree "$Label inner subject tree mismatch"
    $innerContext = if ([string]::IsNullOrEmpty([string]$inner.execution_context)) { 'standalone_full_gate' } else { [string]$inner.execution_context }
    Require-Equal $innerContext $BaselineAdmissionExecutionContext "$Label inner execution context mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$inner.python_executable_path)) ([System.IO.Path]::GetFullPath([string]$ExpectedInterpreter.path)) "$Label inner interpreter path mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$inner.environment_receipt_path)) ([System.IO.Path]::GetFullPath([string]$ExpectedEnvironment.path)) "$Label inner environment receipt path mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$inner.implementation_identity.runner.actual_path)) ([System.IO.Path]::GetFullPath([string]$ExpectedRunner.actual_path)) "$Label inner runner path mismatch"
    Require-Equal $inner.implementation_identity.runner.git_blob_id $ExpectedRunner.git_blob_id "$Label inner runner blob mismatch"
    Require-Equal $inner.implementation_identity.runner.working_sha256 $ExpectedRunner.working_sha256 "$Label inner runner materialization mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$inner.implementation_identity.imported_common.actual_path)) ([System.IO.Path]::GetFullPath([string]$ExpectedCommon.actual_path)) "$Label actual-import common path mismatch"
    Require-Equal ([System.IO.Path]::GetFullPath([string]$inner.implementation_identity.imported_common.module_file)) ([System.IO.Path]::GetFullPath([string]$ExpectedCommon.actual_path)) "$Label actual-import common module_file mismatch"
    Require-Equal $inner.implementation_identity.imported_common.git_blob_id $ExpectedCommon.git_blob_id "$Label actual-import common blob mismatch"
    Require-Equal $inner.implementation_identity.imported_common.working_sha256 $ExpectedCommon.working_sha256 "$Label actual-import common materialization mismatch"
    $canonicalPath = [System.IO.Path]::GetFullPath([string]$inner.canonical_result.path)
    if (-not [System.IO.File]::Exists($canonicalPath)) { throw "$Label canonical result is missing" }
    $canonicalHash = Get-Sha256 $canonicalPath
    Require-Equal $canonicalHash $inner.canonical_result.sha256 "$Label canonical result hash mismatch"
    return [ordered]@{
        label = $Label
        orchestration_receipt = [ordered]@{ path = $path.Replace('\', '/'); sha256 = $receiptHash; claim_id = [string]$receipt.claim_id }
        inner_run_receipt = [ordered]@{ path = $innerPath.Replace('\', '/'); sha256 = $innerHash }
        canonical_result = [ordered]@{ path = $canonicalPath.Replace('\', '/'); sha256 = $canonicalHash }
        execution_context = $innerContext
    }
}

$status = 'preflight_pending'
$stage = 'initialize'
$failureReason = $null
$primaryFailure = $null
$secondaryFailures = @()
$nativeExitCode = $null
$plannedArgv = $null
$actualArgv = $null
$script:NativeProcessStarted = $false
$environmentBefore = [ordered]@{}
$environmentApplied = [ordered]@{}
$environmentAfterRestore = [ordered]@{}
$environmentRestored = $false
$environmentConfigured = $false
$identity = [ordered]@{}
$runChains = [ordered]@{}
$canonicalFingerprint = $null
$receiptWriteFailure = $null
$receiptWriteStatus = 'pending'
$resolvedAttemptRoot = $AttemptRoot
$receiptPath = $null
$stdoutPath = $null
$stderrPath = $null

try {
    $stage = 'resolve_paths'
    $repo = [System.IO.Path]::GetFullPath($RepositoryRoot)
    $resolvedAttemptRoot = Assert-ExternalPath $repo $AttemptRoot 'attempt root'
    [System.IO.Directory]::CreateDirectory($resolvedAttemptRoot) | Out-Null
    if (@([System.IO.Directory]::EnumerateFileSystemEntries($resolvedAttemptRoot)).Count -ne 0) { throw 'compare attempt root must be empty' }
    $receiptPath = Join-Path $resolvedAttemptRoot 'compare_receipt.json'
    $stdoutPath = Join-Path $resolvedAttemptRoot 'compare-results.stdout.bin'
    $stderrPath = Join-Path $resolvedAttemptRoot 'compare-results.stderr.bin'

    $stage = 'resolve_subject'
    $headResult = Invoke-TextProcess 'git' @('-C', $repo, 'rev-parse', 'HEAD') $repo
    if ($headResult.exit_code -ne 0) { throw "failed to resolve HEAD: $($headResult.stderr.Trim())" }
    Require-Equal $headResult.stdout.Trim() $Commit 'HEAD does not equal exact compare subject'
    $treeResult = Invoke-TextProcess 'git' @('-C', $repo, 'rev-parse', ($Commit + '^{tree}')) $repo
    if ($treeResult.exit_code -ne 0) { throw "failed to resolve tree: $($treeResult.stderr.Trim())" }
    $subject = [ordered]@{ commit = $Commit; tree = $treeResult.stdout.Trim() }
    $identity['subject'] = $subject
    $statusResult = Invoke-TextProcess 'git' @('-C', $repo, 'status', '--porcelain=v1', '--untracked-files=all') $repo
    if ($statusResult.exit_code -ne 0) { throw 'working-tree clean check failed' }
    if (-not [string]::IsNullOrWhiteSpace($statusResult.stdout)) { throw 'compare source checkout is not clean' }

    $stage = 'resolve_identity'
    $validatorRelative = 'Iris/validation/execution/validate_environment_and_results.py'
    $commonRelative = 'Iris/validation/execution/checkout_environment.py'
    $runnerRelative = 'Iris/validation/execution/run_repository_tests.py'
    $policyRelative = 'Iris/validation/execution/contracts/test_execution_output_policy.json'
    $successorPolicyRelative = 'Iris/validation/execution/contracts/isolated_command_output_policy.json'
    $evidencePolicyRelative = 'Iris/validation/execution/contracts/evidence_storage_output_policy.json'
    $evidencePredecessorRelative = 'Iris/_docs/refactor/repository_evidence_lightweighting/predecessor_subject_manifest.json'
    $evidenceOwnerApprovalRelative = 'Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json'
    $taxonomyRelative = 'Iris/_docs/round3/round3_test_taxonomy.json'
    $requiredValidationsRelative = 'Iris/validation/execution/required_validations.json'
    $fullGateContractRelative = 'Iris/validation/execution/contracts/repository_test_gate.json'
    $evidenceAdoptionReceiptRelative = 'Iris/_docs/refactor/repository_evidence_lightweighting/required_validation_adoption_receipt.json'
    $evidenceAllocatorRelative = 'Iris/validation/execution/allocate_external_workspaces.ps1'
    $environmentLocatorRelative = 'Iris/validation/execution/current_environment.json'
    $launcherRelative = 'Iris/validation/execution/compare_repeated_test_runs.ps1'
    $implementation = [ordered]@{}
    foreach ($row in @(
        @('validator', $validatorRelative),
        @('common', $commonRelative),
        @('runner', $runnerRelative),
        @('policy', $policyRelative),
        @('successor_policy', $successorPolicyRelative),
        @('evidence_policy', $evidencePolicyRelative),
        @('evidence_predecessor', $evidencePredecessorRelative),
        @('evidence_owner_approval', $evidenceOwnerApprovalRelative),
        @('test_taxonomy', $taxonomyRelative),
        @('required_validations', $requiredValidationsRelative),
        @('full_gate_contract', $fullGateContractRelative),
        @('evidence_adoption_receipt', $evidenceAdoptionReceiptRelative),
        @('evidence_allocator', $evidenceAllocatorRelative),
        @('environment_authority', $environmentLocatorRelative),
        @('launcher', $launcherRelative)
    )) {
        $physical = Join-Path $repo $row[1]
        if (-not [System.IO.File]::Exists($physical)) { throw "compare implementation file is missing: $physical" }
        $blobResult = Invoke-TextProcess 'git' @('-C', $repo, 'rev-parse', ($Commit + ':' + $row[1])) $repo
        if ($blobResult.exit_code -ne 0) { throw "failed to resolve $($row[0]) blob" }
        $workingBlobResult = Invoke-TextProcess 'git' @('-C', $repo, 'hash-object', ('--path=' + $row[1]), $physical) $repo
        if ($workingBlobResult.exit_code -ne 0) { throw "failed to hash $($row[0]) working file" }
        if ($workingBlobResult.stdout.Trim() -ne $blobResult.stdout.Trim()) { throw "$($row[0]) working file differs from the exact subject blob" }
        $implementation[$row[0]] = [ordered]@{
            logical_path = $row[1]
            actual_path = ([System.IO.Path]::GetFullPath($physical)).Replace('\', '/')
            git_blob_id = $blobResult.stdout.Trim()
            working_git_blob_id = $workingBlobResult.stdout.Trim()
            working_sha256 = Get-Sha256 $physical
        }
    }
    $identity['implementation'] = $implementation
    $actualLauncher = [System.IO.Path]::GetFullPath($MyInvocation.MyCommand.Path)
    Require-Equal $actualLauncher (Join-Path $repo $launcherRelative) 'compare launcher was loaded from another checkout'

    $environmentLocatorPath = Join-Path $repo $environmentLocatorRelative
    $environmentLocator = Get-Content -Raw -Encoding UTF8 -LiteralPath $environmentLocatorPath | ConvertFrom-Json
    $environmentRecordPath = Join-Path $repo ([string]$environmentLocator.record_path)
    if (-not [System.IO.File]::Exists($environmentRecordPath)) { throw 'current environment authority record is missing' }
    Require-Equal (Get-Sha256 $environmentRecordPath) ([string]$environmentLocator.record_sha256) 'current environment authority record hash mismatch'
    $environmentRecord = Get-Content -Raw -Encoding UTF8 -LiteralPath $environmentRecordPath | ConvertFrom-Json
    $expectedEnvironment = $environmentRecord.environment_contract
    $environmentPath = [System.IO.Path]::GetFullPath($EnvironmentReceipt)
    if (-not [System.IO.File]::Exists($environmentPath)) { throw 'environment receipt is missing' }
    $environmentHash = Get-Sha256 $environmentPath
    Require-Equal $environmentHash $expectedEnvironment.immutable_environment_receipt_sha256 'environment receipt hash mismatch'
    Require-Equal $environmentPath ([System.IO.Path]::GetFullPath([string]$expectedEnvironment.immutable_environment_receipt_path)) 'environment receipt path mismatch'
    $environmentPayload = Get-Content -Raw -Encoding UTF8 -LiteralPath $environmentPath | ConvertFrom-Json
    $pythonExe = [System.IO.Path]::GetFullPath([string]$environmentPayload.interpreter.path)
    if (-not [System.IO.File]::Exists($pythonExe)) { throw 'receipt interpreter is missing' }
    $pythonHash = Get-Sha256 $pythonExe
    Require-Equal $pythonHash $expectedEnvironment.interpreter_sha256 'receipt interpreter hash mismatch'
    $identity['interpreter'] = [ordered]@{ path = $pythonExe.Replace('\', '/'); sha256 = $pythonHash }
    $identity['environment_receipt'] = [ordered]@{ path = $environmentPath.Replace('\', '/'); sha256 = $environmentHash }

    $stage = 'bind_run_chains'
    $runChains['run_a'] = Resolve-RunChain 'Run A' $RunAOrchestrationReceipt $ClaimId $subject $identity.interpreter $identity.environment_receipt $implementation
    $runChains['run_b'] = Resolve-RunChain 'Run B' $RunBOrchestrationReceipt $ClaimId $subject $identity.interpreter $identity.environment_receipt $implementation
    if ([System.IO.Path]::GetFullPath([string]$runChains.run_a.orchestration_receipt.path).Equals([System.IO.Path]::GetFullPath([string]$runChains.run_b.orchestration_receipt.path), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Run A and Run B must use distinct orchestration receipt paths'
    }
    if ([System.IO.Path]::GetFullPath([string]$runChains.run_a.inner_run_receipt.path).Equals([System.IO.Path]::GetFullPath([string]$runChains.run_b.inner_run_receipt.path), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Run A and Run B must use distinct inner run receipt paths'
    }
    if ([System.IO.Path]::GetFullPath([string]$runChains.run_a.canonical_result.path).Equals([System.IO.Path]::GetFullPath([string]$runChains.run_b.canonical_result.path), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Run A and Run B must use distinct canonical result paths'
    }

    $arguments = @(
        '-B', '-s', $implementation.validator.actual_path,
        'compare-results',
        '--run-a', $runChains.run_a.canonical_result.path,
        '--run-b', $runChains.run_b.canonical_result.path,
        '--repo', $repo,
        '--commit', $Commit
    )
    $plannedArgv = @($pythonExe) + $arguments

    $stage = 'configure_environment'
    $policy = Get-Content -Raw -Encoding UTF8 -LiteralPath $implementation.policy.actual_path | ConvertFrom-Json
    $requiredNames = @($policy.required_environment.PSObject.Properties.Name)
    $clearedNames = @($policy.cleared_ambient_environment)
    foreach ($name in @($requiredNames + $clearedNames | Sort-Object -Unique)) { $environmentBefore[$name] = Get-EnvironmentState $name }
    foreach ($name in $clearedNames) {
        Remove-Item -LiteralPath ("Env:" + $name) -ErrorAction SilentlyContinue
        $environmentApplied[$name] = [ordered]@{ action = 'clear'; value = $null }
    }
    $requiredApplyCount = 0
    foreach ($name in $requiredNames) {
        $value = [string]$policy.required_environment.$name
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        $environmentApplied[$name] = [ordered]@{ action = 'set'; value = $value }
        $requiredApplyCount += 1
        if ($FailureInjection -eq 'required_environment_apply' -and $requiredApplyCount -eq 1) {
            throw 'injected required environment apply failure after first mutation'
        }
    }
    $environmentConfigured = $true

    $stage = 'invoke_compare'
    $actualArgv = @($plannedArgv)
    $nativeExitCode = Invoke-RawProcess $pythonExe $arguments $repo $stdoutPath $stderrPath
    if ($nativeExitCode -ne 0) {
        $primaryFailure = [ordered]@{ kind = 'native_compare_exit_nonzero'; native_exit_code = $nativeExitCode }
        $failureReason = 'native_compare_exit_nonzero'
        $status = 'compare_failed'
    }
    else {
        $status = 'compare_exit_zero_pending_output_validation'
        $stage = 'validate_compare_output'
    }
}
catch {
    if ($null -eq $primaryFailure) {
        $primaryFailure = [ordered]@{ kind = 'exception'; stage = $stage; exception_type = $_.Exception.GetType().FullName; exception_message = $_.Exception.Message }
        $failureReason = $stage
        $status = 'preflight_or_compare_exception'
    }
    else {
        $secondaryFailures += [ordered]@{ stage = $stage; exception_type = $_.Exception.GetType().FullName; exception_message = $_.Exception.Message }
    }
}
finally {
    $restoreFailures = @()
    foreach ($name in @($environmentBefore.Keys)) {
        try {
            if ($FailureInjection -eq 'environment_restore' -and $restoreFailures.Count -eq 0) {
                throw "injected environment restore failure for $name"
            }
            Restore-EnvironmentState $name $environmentBefore[$name]
            $environmentAfterRestore[$name] = Get-EnvironmentState $name
            if (-not (Test-EnvironmentStateEqual $environmentBefore[$name] $environmentAfterRestore[$name])) {
                throw "environment state did not round-trip for $name"
            }
        }
        catch {
            $restoreFailures += [ordered]@{
                stage = 'restore_environment'
                variable = $name
                exception_type = $_.Exception.GetType().FullName
                exception_message = $_.Exception.Message
            }
        }
    }
    $environmentRestored = ($restoreFailures.Count -eq 0)
    if (-not $environmentRestored) {
        if ($null -eq $primaryFailure) {
            $firstRestoreFailure = $restoreFailures[0]
            $primaryFailure = [ordered]@{
                kind = 'environment_restore_failed'
                stage = 'restore_environment'
                variable = $firstRestoreFailure.variable
                exception_type = $firstRestoreFailure.exception_type
                exception_message = $firstRestoreFailure.exception_message
            }
            $failureReason = 'restore_environment'
            $status = 'environment_restore_failed'
            if ($restoreFailures.Count -gt 1) {
                $secondaryFailures += @($restoreFailures[1..($restoreFailures.Count - 1)])
            }
        }
        else {
            $secondaryFailures += @($restoreFailures)
        }
    }

    try {
        if ($nativeExitCode -eq 0) {
            $comparison = Get-Content -Raw -Encoding UTF8 -LiteralPath $stdoutPath | ConvertFrom-Json
            Require-Equal $comparison.status 'PASS' 'compare validator output is not PASS'
            Require-Equal $comparison.subject.commit $identity.subject.commit 'actual compare subject commit mismatch'
            Require-Equal $comparison.subject.tree $identity.subject.tree 'actual compare subject tree mismatch'
            Require-Equal ([System.IO.Path]::GetFullPath([string]$comparison.implementation_identity.validator.actual_path)) ([System.IO.Path]::GetFullPath([string]$identity.implementation.validator.actual_path)) 'actual compare validator path mismatch'
            Require-Equal $comparison.implementation_identity.validator.git_blob_id $identity.implementation.validator.git_blob_id 'actual compare validator blob mismatch'
            Require-Equal $comparison.implementation_identity.validator.working_sha256 $identity.implementation.validator.working_sha256 'actual compare validator materialization mismatch'
            Require-Equal ([System.IO.Path]::GetFullPath([string]$comparison.implementation_identity.imported_common.actual_path)) ([System.IO.Path]::GetFullPath([string]$identity.implementation.common.actual_path)) 'actual compare common path mismatch'
            Require-Equal ([System.IO.Path]::GetFullPath([string]$comparison.implementation_identity.imported_common.module_file)) ([System.IO.Path]::GetFullPath([string]$identity.implementation.common.actual_path)) 'actual compare common module_file mismatch'
            Require-Equal $comparison.implementation_identity.imported_common.git_blob_id $identity.implementation.common.git_blob_id 'actual compare common blob mismatch'
            Require-Equal $comparison.implementation_identity.imported_common.working_sha256 $identity.implementation.common.working_sha256 'actual compare common materialization mismatch'
            if ($null -eq $primaryFailure -and $environmentRestored) {
                $status = 'succeeded'
            }
        }
    }
    catch {
        if ($null -eq $primaryFailure) {
            $primaryFailure = [ordered]@{ kind = 'compare_output_validation_failed'; stage = 'validate_compare_output'; exception_message = $_.Exception.Message }
            $failureReason = 'validate_compare_output'
            $status = 'compare_output_validation_failed'
        }
        else {
            $secondaryFailures += [ordered]@{ stage = 'validate_compare_output'; exception_type = $_.Exception.GetType().FullName; exception_message = $_.Exception.Message }
        }
    }

    try {
        $stdoutHash = if ($stdoutPath -and [System.IO.File]::Exists($stdoutPath)) { Get-Sha256 $stdoutPath } else { $null }
        $stderrHash = if ($stderrPath -and [System.IO.File]::Exists($stderrPath)) { Get-Sha256 $stderrPath } else { $null }
        $fingerprintPayload = [ordered]@{
            schema_version = 'iris-clean-checkout-compare-fingerprint-v1'
            claim_id = $ClaimId
            subject = $identity.subject
            run_a = [ordered]@{
                orchestration_receipt_sha256 = $runChains.run_a.orchestration_receipt.sha256
                inner_run_receipt_sha256 = $runChains.run_a.inner_run_receipt.sha256
                canonical_result_sha256 = $runChains.run_a.canonical_result.sha256
            }
            run_b = [ordered]@{
                orchestration_receipt_sha256 = $runChains.run_b.orchestration_receipt.sha256
                inner_run_receipt_sha256 = $runChains.run_b.inner_run_receipt.sha256
                canonical_result_sha256 = $runChains.run_b.canonical_result.sha256
            }
            stdout_sha256 = $stdoutHash
            stderr_sha256 = $stderrHash
            native_exit_code = $nativeExitCode
            validator_blob = $identity.implementation.validator.git_blob_id
            validator_working_sha256 = $identity.implementation.validator.working_sha256
            common_blob = $identity.implementation.common.git_blob_id
            common_working_sha256 = $identity.implementation.common.working_sha256
            successor_policy_blob = $identity.implementation.successor_policy.git_blob_id
            successor_policy_working_sha256 = $identity.implementation.successor_policy.working_sha256
            repository_evidence_lightweighting = [ordered]@{
                policy_blob = $identity.implementation.evidence_policy.git_blob_id
                policy_working_sha256 = $identity.implementation.evidence_policy.working_sha256
                predecessor_blob = $identity.implementation.evidence_predecessor.git_blob_id
                predecessor_working_sha256 = $identity.implementation.evidence_predecessor.working_sha256
                owner_approval_blob = $identity.implementation.evidence_owner_approval.git_blob_id
                owner_approval_working_sha256 = $identity.implementation.evidence_owner_approval.working_sha256
                taxonomy_blob = $identity.implementation.test_taxonomy.git_blob_id
                taxonomy_working_sha256 = $identity.implementation.test_taxonomy.working_sha256
                required_validations_blob = $identity.implementation.required_validations.git_blob_id
                required_validations_working_sha256 = $identity.implementation.required_validations.working_sha256
                full_gate_contract_blob = $identity.implementation.full_gate_contract.git_blob_id
                full_gate_contract_working_sha256 = $identity.implementation.full_gate_contract.working_sha256
                adoption_receipt_blob = $identity.implementation.evidence_adoption_receipt.git_blob_id
                adoption_receipt_working_sha256 = $identity.implementation.evidence_adoption_receipt.working_sha256
                allocator_blob = $identity.implementation.evidence_allocator.git_blob_id
                allocator_working_sha256 = $identity.implementation.evidence_allocator.working_sha256
            }
            interpreter_sha256 = $identity.interpreter.sha256
            environment_receipt_sha256 = $identity.environment_receipt.sha256
            execution_context = $BaselineAdmissionExecutionContext
        }
        $canonicalFingerprint = Get-BytesSha256 (ConvertTo-StableJsonBytes $fingerprintPayload)
        $receipt = [ordered]@{
            schema_version = 'iris-clean-checkout-compare-receipt-v1'
            status = $status
            failure_reason = $failureReason
            primary_failure = $primaryFailure
            secondary_failures = $secondaryFailures
            claim_id = $ClaimId
            subject = $identity.subject
            native_exit_code = $nativeExitCode
            planned_argv = $plannedArgv
            actual_argv = if ($script:NativeProcessStarted) { $actualArgv } else { $null }
            environment = [ordered]@{ configured = $environmentConfigured; before = $environmentBefore; applied = $environmentApplied; after_restore = $environmentAfterRestore; restored = $environmentRestored }
            identity = $identity
            execution_context = $BaselineAdmissionExecutionContext
            run_chains = $runChains
            stdout = [ordered]@{ path = if ($stdoutPath) { $stdoutPath.Replace('\', '/') } else { $null }; sha256 = $stdoutHash }
            stderr = [ordered]@{ path = if ($stderrPath) { $stderrPath.Replace('\', '/') } else { $null }; sha256 = $stderrHash }
            canonical_fingerprint_schema = 'iris-clean-checkout-compare-fingerprint-v1'
            canonical_fingerprint_sha256 = $canonicalFingerprint
            receipt_write_status = 'succeeded'
            validation_ceiling = 'PowerShell parameter-binding failures occur before compare receipt initialization and are outside the all-path receipt claim.'
            failure_injection = $FailureInjection
        }
        Write-JsonNoBomAtomic $receiptPath $receipt
        $receiptWriteStatus = 'succeeded'
    }
    catch {
        $receiptWriteStatus = 'failed'
        $receiptWriteFailure = $_
        $fallbackOperatorRecord = [ordered]@{
            schema_version = 'iris-clean-checkout-compare-writer-fallback-v1'
            receipt_write_status = 'failed'
            receipt_path = $receiptPath
            writer_exception_type = $_.Exception.GetType().FullName
            writer_exception_message = $_.Exception.Message
            status = $status
            native_exit_code = $nativeExitCode
            primary_failure = $primaryFailure
            secondary_failures = $secondaryFailures
            environment_restored = $environmentRestored
            validation_ceiling = 'The primary compare receipt could not be persisted; this structured stderr record is operator evidence, not a substitute receipt.'
        }
        try {
            [Console]::Error.WriteLine(($fallbackOperatorRecord | ConvertTo-Json -Compress -Depth 24))
        }
        catch {
            [Console]::Error.WriteLine('compare receipt writer and structured fallback serialization both failed')
        }
    }
}

if ($null -ne $receiptWriteFailure) { exit 125 }
if ($null -ne $primaryFailure) {
    if ($primaryFailure.kind -eq 'native_compare_exit_nonzero') { exit [int]$nativeExitCode }
    [Console]::Error.WriteLine(($primaryFailure | ConvertTo-Json -Compress -Depth 8))
    exit 1
}
exit 0
