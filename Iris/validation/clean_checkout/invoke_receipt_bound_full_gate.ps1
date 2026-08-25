[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepositoryRoot,
    [Parameter(Mandatory = $true)][string]$Commit,
    [Parameter(Mandatory = $true)][string]$ClaimId,
    [Parameter(Mandatory = $true)][string]$EnvironmentReceipt,
    [Parameter(Mandatory = $true)][string]$WorkRoot,
    [Parameter(Mandatory = $true)][string]$ResultRoot,
    [Parameter(Mandatory = $true)][string]$OrchestrationReceipt,
    [Alias('ExecutionContext')]
    [ValidateSet('standalone_full_gate', 'composite_baseline_admission_chain_stage_6')]
    [string]$BaselineAdmissionExecutionContext = 'standalone_full_gate',
    [string]$PredecessorStageReceiptSetSha256,
    [string]$QualificationContractSha256,
    [string]$PredecessorStageReceiptSet,
    [string]$QualificationContract,
    [string]$StdoutPath,
    [string]$StderrPath,
    [ValidateSet('none', 'required_environment_apply', 'environment_restore')]
    [string]$FailureInjection = 'none',
    [string]$EmptyStateFixtureVariable = ''
)

$ErrorActionPreference = 'Stop'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-Sha256([string]$Value) {
    return $Value -match '^[0-9a-f]{64}$'
}

function Quote-NativeArgument([string]$Value) {
    if ($Value.Length -eq 0) { return '""' }
    if ($Value -notmatch '[\s"]') { return $Value }
    $builder = New-Object System.Text.StringBuilder
    [void]$builder.Append('"')
    $backslashes = 0
    foreach ($character in $Value.ToCharArray()) {
        if ($character -eq '\') {
            $backslashes += 1
            continue
        }
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
    if ($backslashes -gt 0) {
        [void]$builder.Append(('\' * ($backslashes * 2)))
    }
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
    return [ordered]@{
        exit_code = $process.ExitCode
        stdout = $stdout
        stderr = $stderr
    }
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
        $stdoutStream = [System.IO.File]::Open(
            $RawStdoutPath,
            [System.IO.FileMode]::CreateNew,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::Read
        )
        $stderrStream = [System.IO.File]::Open(
            $RawStderrPath,
            [System.IO.FileMode]::CreateNew,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::Read
        )
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
    $json = $Payload | ConvertTo-Json -Depth 24
    $json = $json.Replace("`r`n", "`n")
    if (-not $json.EndsWith("`n")) { $json += "`n" }
    $temporary = Join-Path $parent ('.' + [System.IO.Path]::GetFileName($Path) + '.' + [guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [System.IO.File]::WriteAllText(
            $temporary,
            $json,
            (New-Object System.Text.UTF8Encoding($false))
        )
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
    if (
        -not [string]::IsNullOrEmpty($script:EmptyStateFixtureVariable) -and
        $Name.Equals($script:EmptyStateFixtureVariable, [System.StringComparison]::Ordinal)
    ) {
        return [ordered]@{ state = 'empty'; value = '' }
    }
    $value = [Environment]::GetEnvironmentVariable($Name, 'Process')
    if ($null -eq $value) {
        return [ordered]@{ state = 'absent'; value = $null }
    }
    if ($value.Length -eq 0) {
        return [ordered]@{ state = 'empty'; value = '' }
    }
    return [ordered]@{ state = 'value'; value = $value }
}

function Restore-EnvironmentState([string]$Name, [object]$State) {
    if ($State.state -eq 'absent') {
        Remove-Item -LiteralPath ("Env:" + $Name) -ErrorAction SilentlyContinue
    }
    else {
        [Environment]::SetEnvironmentVariable($Name, [string]$State.value, 'Process')
    }
}

function Test-EnvironmentStateEqual([object]$Left, [object]$Right) {
    return (
        [string]$Left.state -eq [string]$Right.state -and
        [string]$Left.value -eq [string]$Right.value
    )
}

$launchStatus = 'preflight_pending'
$launchStage = 'initialize'
$failureReason = $null
$exceptionType = $null
$exceptionMessage = $null
$nativeExitCode = $null
$plannedArgv = $null
$actualArgv = $null
$primaryFailure = $null
$secondaryFailures = @()
$receiptWriteStatus = 'pending'
$environmentConfigured = $false
$environmentRestored = $false
$environmentBefore = [ordered]@{}
$environmentApplied = [ordered]@{}
$environmentAfterRestore = [ordered]@{}
$identity = [ordered]@{}
$resultReceiptExists = $false
$resultReceiptHash = $null
$resultReceiptPath = $null
$script:NativeProcessStarted = $false
$resolvedOrchestrationReceipt = $OrchestrationReceipt
$resolvedStdout = $StdoutPath
$resolvedStderr = $StderrPath
$resolvedRepository = $RepositoryRoot
$resolvedResultRoot = $ResultRoot
$resolvedWorkRoot = $WorkRoot
$receiptWriteFailure = $null
$receiptPathApproved = $false
$script:EmptyStateFixtureVariable = $EmptyStateFixtureVariable

try {
    $launchStage = 'resolve_paths'
    if (
        -not [string]::IsNullOrEmpty($EmptyStateFixtureVariable) -and
        -not $ClaimId.StartsWith('fixture-', [System.StringComparison]::Ordinal)
    ) {
        throw 'empty-state fixture is restricted to fixture-* claims'
    }
    $resolvedRepository = [System.IO.Path]::GetFullPath($RepositoryRoot)
    $resolvedOrchestrationReceipt = Assert-ExternalPath $resolvedRepository $OrchestrationReceipt 'orchestration receipt'
    $receiptPathApproved = $true
    $resolvedWorkRoot = Assert-ExternalPath $resolvedRepository $WorkRoot 'work root'
    $resolvedResultRoot = Assert-ExternalPath $resolvedRepository $ResultRoot 'result root'
    $receiptParent = [System.IO.Path]::GetDirectoryName($resolvedOrchestrationReceipt)
    $streamParent = $receiptParent
    if ($receiptParent.TrimEnd('\', '/').Equals(
        $resolvedResultRoot.TrimEnd('\', '/'),
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        $resultParent = [System.IO.Path]::GetDirectoryName($resolvedResultRoot)
        $resultLeaf = [System.IO.Path]::GetFileName($resolvedResultRoot)
        $streamParent = Join-Path $resultParent ($resultLeaf + '.launcher')
    }
    if ([string]::IsNullOrWhiteSpace($resolvedStdout)) {
        $resolvedStdout = Join-Path $streamParent 'full-gate.stdout.bin'
    }
    else {
        $resolvedStdout = Assert-ExternalPath $resolvedRepository $resolvedStdout 'stdout path'
    }
    if ([string]::IsNullOrWhiteSpace($resolvedStderr)) {
        $resolvedStderr = Join-Path $streamParent 'full-gate.stderr.bin'
    }
    else {
        $resolvedStderr = Assert-ExternalPath $resolvedRepository $resolvedStderr 'stderr path'
    }
    [System.IO.Directory]::CreateDirectory($receiptParent) | Out-Null
    [System.IO.Directory]::CreateDirectory($streamParent) | Out-Null
    if ([System.IO.File]::Exists($resolvedOrchestrationReceipt)) { throw 'orchestration receipt already exists' }
    if ([System.IO.File]::Exists($resolvedStdout)) { throw 'stdout path already exists' }
    if ([System.IO.File]::Exists($resolvedStderr)) { throw 'stderr path already exists' }

    $launchStage = 'resolve_head'
    $headResult = Invoke-TextProcess 'git' @('-C', $resolvedRepository, 'rev-parse', 'HEAD') $resolvedRepository
    if ($headResult.exit_code -ne 0) { throw "failed to resolve repository HEAD: $($headResult.stderr.Trim())" }
    $head = $headResult.stdout.Trim()
    if ($head -ne $Commit) { throw "HEAD does not equal exact target commit: $head != $Commit" }
    $treeResult = Invoke-TextProcess 'git' @('-C', $resolvedRepository, 'rev-parse', ($Commit + '^{tree}')) $resolvedRepository
    if ($treeResult.exit_code -ne 0) { throw "failed to resolve repository tree: $($treeResult.stderr.Trim())" }
    $identity['subject'] = [ordered]@{ commit = $Commit; tree = $treeResult.stdout.Trim() }

    $launchStage = 'check_clean'
    $statusResult = Invoke-TextProcess 'git' @('-C', $resolvedRepository, 'status', '--porcelain=v1', '--untracked-files=all') $resolvedRepository
    if ($statusResult.exit_code -ne 0) { throw "working-tree clean check failed: $($statusResult.stderr.Trim())" }
    if (-not [string]::IsNullOrWhiteSpace($statusResult.stdout)) { throw 'full-gate source checkout is not clean' }

    $launchStage = 'resolve_identity'
    $runnerRelative = 'Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py'
    $commonRelative = 'Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py'
    $policyRelative = 'Iris/validation/clean_checkout/contracts/output_policy.json'
    $successorPolicyRelative = 'Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json'
    $evidencePolicyRelative = 'Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json'
    $evidencePredecessorRelative = 'Iris/_docs/refactor/repository_evidence_lightweighting/predecessor_subject_manifest.json'
    $evidenceOwnerApprovalRelative = 'Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json'
    $taxonomyRelative = 'Iris/_docs/round3/round3_test_taxonomy.json'
    $requiredValidationsRelative = 'Iris/_docs/round3/current_route_required_validations.json'
    $fullGateContractRelative = 'Iris/validation/clean_checkout/contracts/full_repository_gate.json'
    $evidenceAdoptionReceiptRelative = 'Iris/_docs/refactor/repository_evidence_lightweighting/required_validation_adoption_receipt.json'
    $evidenceAllocatorRelative = 'Iris/validation/clean_checkout/allocate_repository_runtime_lightweighting_roots.ps1'
    $environmentLocatorRelative = 'Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json'
    $launcherRelative = 'Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1'
    $runner = Join-Path $resolvedRepository $runnerRelative
    $common = Join-Path $resolvedRepository $commonRelative
    $policyPath = Join-Path $resolvedRepository $policyRelative
    $successorPolicyPath = Join-Path $resolvedRepository $successorPolicyRelative
    $evidencePolicyPath = Join-Path $resolvedRepository $evidencePolicyRelative
    $evidencePredecessorPath = Join-Path $resolvedRepository $evidencePredecessorRelative
    $evidenceOwnerApprovalPath = Join-Path $resolvedRepository $evidenceOwnerApprovalRelative
    $taxonomyPath = Join-Path $resolvedRepository $taxonomyRelative
    $requiredValidationsPath = Join-Path $resolvedRepository $requiredValidationsRelative
    $fullGateContractPath = Join-Path $resolvedRepository $fullGateContractRelative
    $evidenceAdoptionReceiptPath = Join-Path $resolvedRepository $evidenceAdoptionReceiptRelative
    $evidenceAllocatorPath = Join-Path $resolvedRepository $evidenceAllocatorRelative
    $environmentLocatorPath = Join-Path $resolvedRepository $environmentLocatorRelative
    $expectedLauncher = Join-Path $resolvedRepository $launcherRelative
    $actualLauncher = [System.IO.Path]::GetFullPath($MyInvocation.MyCommand.Path)
    if (-not $actualLauncher.Equals([System.IO.Path]::GetFullPath($expectedLauncher), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'launcher was loaded from a different checkout'
    }
    foreach ($path in @(
        $runner,
        $common,
        $policyPath,
        $successorPolicyPath,
        $evidencePolicyPath,
        $evidencePredecessorPath,
        $evidenceOwnerApprovalPath,
        $taxonomyPath,
        $requiredValidationsPath,
        $fullGateContractPath,
        $evidenceAdoptionReceiptPath,
        $evidenceAllocatorPath,
        $environmentLocatorPath,
        $actualLauncher
    )) {
        if (-not [System.IO.File]::Exists($path)) { throw "required implementation file is missing: $path" }
    }
    $blobRows = [ordered]@{}
    foreach ($row in @(
        @('runner', $runnerRelative, $runner),
        @('common', $commonRelative, $common),
        @('policy', $policyRelative, $policyPath),
        @('successor_policy', $successorPolicyRelative, $successorPolicyPath),
        @('evidence_policy', $evidencePolicyRelative, $evidencePolicyPath),
        @('evidence_predecessor', $evidencePredecessorRelative, $evidencePredecessorPath),
        @('evidence_owner_approval', $evidenceOwnerApprovalRelative, $evidenceOwnerApprovalPath),
        @('test_taxonomy', $taxonomyRelative, $taxonomyPath),
        @('required_validations', $requiredValidationsRelative, $requiredValidationsPath),
        @('full_gate_contract', $fullGateContractRelative, $fullGateContractPath),
        @('evidence_adoption_receipt', $evidenceAdoptionReceiptRelative, $evidenceAdoptionReceiptPath),
        @('evidence_allocator', $evidenceAllocatorRelative, $evidenceAllocatorPath),
        @('environment_authority', $environmentLocatorRelative, $environmentLocatorPath),
        @('launcher', $launcherRelative, $actualLauncher)
    )) {
        $blobResult = Invoke-TextProcess 'git' @('-C', $resolvedRepository, 'rev-parse', ($Commit + ':' + $row[1])) $resolvedRepository
        if ($blobResult.exit_code -ne 0) { throw "failed to resolve $($row[0]) Git blob: $($blobResult.stderr.Trim())" }
        $workingBlobResult = Invoke-TextProcess 'git' @('-C', $resolvedRepository, 'hash-object', ('--path=' + $row[1]), $row[2]) $resolvedRepository
        if ($workingBlobResult.exit_code -ne 0) { throw "failed to hash $($row[0]) working file: $($workingBlobResult.stderr.Trim())" }
        if ($workingBlobResult.stdout.Trim() -ne $blobResult.stdout.Trim()) { throw "$($row[0]) working file differs from the exact subject blob" }
        $blobRows[$row[0]] = [ordered]@{
            logical_path = $row[1]
            actual_path = ([System.IO.Path]::GetFullPath($row[2])).Replace('\', '/')
            git_blob_id = $blobResult.stdout.Trim()
            working_git_blob_id = $workingBlobResult.stdout.Trim()
            working_sha256 = Get-Sha256 $row[2]
        }
    }
    $identity['implementation'] = $blobRows

    $environmentLocator = Get-Content -Raw -Encoding UTF8 -LiteralPath $environmentLocatorPath | ConvertFrom-Json
    $environmentRecordPath = Join-Path $resolvedRepository ([string]$environmentLocator.record_path)
    if (-not [System.IO.File]::Exists($environmentRecordPath)) { throw 'current environment authority record is missing' }
    if ((Get-Sha256 $environmentRecordPath) -ne [string]$environmentLocator.record_sha256) { throw 'current environment authority record hash mismatch' }
    $environmentRecord = Get-Content -Raw -Encoding UTF8 -LiteralPath $environmentRecordPath | ConvertFrom-Json
    $expectedEnvironment = $environmentRecord.environment_contract
    $resolvedEnvironmentReceipt = [System.IO.Path]::GetFullPath($EnvironmentReceipt)
    if (-not [System.IO.File]::Exists($resolvedEnvironmentReceipt)) { throw 'immutable environment receipt is missing' }
    if (-not $resolvedEnvironmentReceipt.Equals([System.IO.Path]::GetFullPath([string]$expectedEnvironment.immutable_environment_receipt_path), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'environment receipt path differs from the owner binding'
    }
    $environmentReceiptHash = Get-Sha256 $resolvedEnvironmentReceipt
    if ($environmentReceiptHash -ne [string]$expectedEnvironment.immutable_environment_receipt_sha256) { throw 'environment receipt hash differs from the owner binding' }
    $environmentReceiptPayload = Get-Content -Raw -Encoding UTF8 -LiteralPath $resolvedEnvironmentReceipt | ConvertFrom-Json
    $pythonExe = [System.IO.Path]::GetFullPath([string]$environmentReceiptPayload.interpreter.path)
    if (-not [System.IO.File]::Exists($pythonExe)) { throw 'receipt interpreter is missing' }
    $pythonHash = Get-Sha256 $pythonExe
    if ($pythonHash -ne [string]$expectedEnvironment.interpreter_sha256) { throw 'receipt interpreter hash differs from the owner binding' }
    $identity['interpreter'] = [ordered]@{ path = $pythonExe.Replace('\', '/'); sha256 = $pythonHash }
    $identity['environment_receipt'] = [ordered]@{ path = $resolvedEnvironmentReceipt.Replace('\', '/'); sha256 = $environmentReceiptHash }

    $plannedArguments = @(
        '-B', '-s', $runner, 'full-gate',
        '--repo', $resolvedRepository,
        '--commit', $Commit,
        '--python', $pythonExe,
        '--environment-receipt', $resolvedEnvironmentReceipt,
        '--work-root', $resolvedWorkRoot,
        '--result-root', $resolvedResultRoot
    )
    if ($BaselineAdmissionExecutionContext -eq 'composite_baseline_admission_chain_stage_6') {
        if (-not (Test-Sha256 $PredecessorStageReceiptSetSha256) -or -not (Test-Sha256 $QualificationContractSha256)) {
            throw 'composite baseline-admission context requires lowercase predecessor-stage and qualification-contract SHA-256 values'
        }
        if ([string]::IsNullOrWhiteSpace($PredecessorStageReceiptSet) -or [string]::IsNullOrWhiteSpace($QualificationContract)) { throw 'composite baseline-admission context requires predecessor-stage receipt-set and qualification-contract files' }
        $resolvedStageReceiptSet = Assert-ExternalPath $resolvedRepository $PredecessorStageReceiptSet 'predecessor-stage receipt set'
        $resolvedQualificationContract = Assert-ExternalPath $resolvedRepository $QualificationContract 'qualification contract'
        if (-not [System.IO.File]::Exists($resolvedStageReceiptSet) -or -not [System.IO.File]::Exists($resolvedQualificationContract)) { throw 'composite baseline-admission identity input file is missing' }
        if ((Get-Sha256 $resolvedStageReceiptSet) -ne $PredecessorStageReceiptSetSha256 -or (Get-Sha256 $resolvedQualificationContract) -ne $QualificationContractSha256) { throw 'composite baseline-admission identity input hash mismatch' }
        $plannedArguments += @(
            '--execution-context', $BaselineAdmissionExecutionContext,
            '--predecessor-stage-receipt-set-sha256', $PredecessorStageReceiptSetSha256,
            '--qualification-contract-sha256', $QualificationContractSha256
            '--predecessor-stage-receipt-set', $resolvedStageReceiptSet,
            '--qualification-contract', $resolvedQualificationContract
        )
    }
    $plannedArgv = @($pythonExe) + $plannedArguments

    $launchStage = 'configure_environment'
    $policy = Get-Content -Raw -Encoding UTF8 -LiteralPath $policyPath | ConvertFrom-Json
    $requiredNames = @($policy.required_environment.PSObject.Properties.Name)
    $clearedNames = @($policy.cleared_ambient_environment)
    $allNames = @($requiredNames + $clearedNames | Sort-Object -Unique)
    foreach ($name in $allNames) { $environmentBefore[$name] = Get-EnvironmentState $name }
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

    $launchStage = 'invoke_gate'
    $actualArgv = @($plannedArgv)
    $nativeExitCode = Invoke-RawProcess $pythonExe $plannedArguments $resolvedRepository $resolvedStdout $resolvedStderr
    if ($nativeExitCode -eq 0) {
        $launchStatus = 'gate_exit_zero_pending_inner_receipt'
        $launchStage = 'verify_inner_receipt_identity'
    }
    else {
        $launchStatus = 'gate_failed'
        $failureReason = 'native_gate_exit_nonzero'
        $primaryFailure = [ordered]@{ kind = 'native_gate_exit_nonzero'; native_exit_code = $nativeExitCode }
    }
}
catch {
    if ($null -eq $primaryFailure) {
        $primaryFailure = [ordered]@{
            kind = 'exception'
            stage = $launchStage
            exception_type = $_.Exception.GetType().FullName
            exception_message = $_.Exception.Message
        }
        $failureReason = $launchStage
        $exceptionType = $_.Exception.GetType().FullName
        $exceptionMessage = $_.Exception.Message
        $launchStatus = if ($launchStage -eq 'invoke_gate') { 'exception' } else { 'preflight_failed' }
    }
    else {
        $secondaryFailures += [ordered]@{
            stage = $launchStage
            exception_type = $_.Exception.GetType().FullName
            exception_message = $_.Exception.Message
        }
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
            $launchStatus = 'environment_restore_failed'
            if ($restoreFailures.Count -gt 1) {
                $secondaryFailures += @($restoreFailures[1..($restoreFailures.Count - 1)])
            }
        }
        else {
            $secondaryFailures += @($restoreFailures)
        }
    }

    try {
        $resultReceiptPath = Join-Path $resolvedResultRoot 'full_run_receipt.json'
        if ([System.IO.File]::Exists($resultReceiptPath)) {
            $resultReceiptExists = $true
            $resultReceiptHash = Get-Sha256 $resultReceiptPath
            $inner = Get-Content -Raw -Encoding UTF8 -LiteralPath $resultReceiptPath | ConvertFrom-Json
            if ([string]$inner.status -ne 'PASS') { throw 'inner receipt is not PASS' }
            if ([string]$inner.subject.commit -ne [string]$identity.subject.commit -or [string]$inner.subject.tree -ne [string]$identity.subject.tree) {
                throw 'inner receipt subject differs from launcher subject'
            }
            if ([string]$inner.execution_context -ne $BaselineAdmissionExecutionContext) { throw 'inner execution context differs from launcher context' }
            if ($BaselineAdmissionExecutionContext -eq 'composite_baseline_admission_chain_stage_6' -and ([string]$inner.predecessor_stage_receipt_set_sha256 -ne $PredecessorStageReceiptSetSha256 -or [string]$inner.qualification_contract_sha256 -ne $QualificationContractSha256)) { throw 'inner composite execution context identity differs from launcher binding' }
            if ([System.IO.Path]::GetFullPath([string]$inner.python_executable_path) -ne [System.IO.Path]::GetFullPath([string]$identity.interpreter.path)) {
                throw 'inner receipt interpreter path differs from launcher interpreter'
            }
            if ([System.IO.Path]::GetFullPath([string]$inner.environment_receipt_path) -ne [System.IO.Path]::GetFullPath([string]$identity.environment_receipt.path)) {
                throw 'inner environment receipt path differs from launcher binding'
            }
            $expectedRunner = $identity.implementation.runner
            $actualRunner = $inner.implementation_identity.runner
            if ($null -eq $actualRunner -or
                [string]$actualRunner.git_blob_id -ne [string]$expectedRunner.git_blob_id -or
                [string]$actualRunner.working_sha256 -ne [string]$expectedRunner.working_sha256 -or
                -not ([System.IO.Path]::GetFullPath([string]$actualRunner.actual_path)).Equals([System.IO.Path]::GetFullPath([string]$expectedRunner.actual_path), [System.StringComparison]::OrdinalIgnoreCase)) {
                throw 'inner runner identity differs from launcher expectation'
            }
            if ($null -eq $inner.implementation_identity.imported_common) { throw 'inner receipt lacks actual imported common identity' }
            $expectedCommon = $identity.implementation.common
            $actualCommon = $inner.implementation_identity.imported_common
            if ([string]$actualCommon.git_blob_id -ne [string]$expectedCommon.git_blob_id -or
                [string]$actualCommon.working_sha256 -ne [string]$expectedCommon.working_sha256 -or
                -not ([System.IO.Path]::GetFullPath([string]$actualCommon.module_file)).Equals([System.IO.Path]::GetFullPath([string]$expectedCommon.actual_path), [System.StringComparison]::OrdinalIgnoreCase) -or
                -not ([System.IO.Path]::GetFullPath([string]$actualCommon.actual_path)).Equals([System.IO.Path]::GetFullPath([string]$expectedCommon.actual_path), [System.StringComparison]::OrdinalIgnoreCase)) {
                throw 'inner actual imported common identity differs from launcher expectation'
            }
            $identity['inner_actual_import'] = $actualCommon
            $innerCanonicalPath = [System.IO.Path]::GetFullPath([string]$inner.canonical_result.path)
            if (-not [System.IO.File]::Exists($innerCanonicalPath)) { throw 'inner canonical result is missing' }
            if ((Get-Sha256 $innerCanonicalPath) -ne [string]$inner.canonical_result.sha256) { throw 'inner canonical result hash mismatch' }
            if ($nativeExitCode -eq 0 -and $null -eq $primaryFailure -and $environmentRestored) {
                $launchStatus = 'succeeded'
            }
        }
        elseif ($nativeExitCode -eq 0) {
            throw 'native gate exited zero without an inner full-run receipt'
        }
    }
    catch {
        $bindingFailureStage = if ($nativeExitCode -eq 0) {
            'verify_inner_receipt_identity'
        }
        else {
            'bind_result_receipt'
        }
        if ($null -eq $primaryFailure) {
            $primaryFailure = [ordered]@{ kind = 'result_receipt_binding_failed'; stage = $bindingFailureStage; exception_message = $_.Exception.Message }
            $failureReason = $bindingFailureStage
            $launchStatus = 'result_receipt_binding_failed'
        }
        else {
            $secondaryFailures += [ordered]@{
                stage = $bindingFailureStage
                exception_type = $_.Exception.GetType().FullName
                exception_message = $_.Exception.Message
            }
        }
    }

    try {
        if (-not $receiptPathApproved) {
            throw 'orchestration receipt destination was not approved as repository-external'
        }
        $receiptWriteStatus = 'succeeded'
        $receiptPayload = [ordered]@{
            schema_version = 'iris-clean-checkout-orchestration-receipt-v1'
            claim_id = $ClaimId
            launch_status = $launchStatus
            launch_stage = $launchStage
            failure_reason = $failureReason
            exception_type = $exceptionType
            exception_message = $exceptionMessage
            primary_failure = $primaryFailure
            secondary_failures = $secondaryFailures
            native_exit_code = $nativeExitCode
            planned_argv = $plannedArgv
            actual_argv = if ($script:NativeProcessStarted) { $actualArgv } else { $null }
            raw_parameters = [ordered]@{
                repository_root = $RepositoryRoot
                commit = $Commit
                environment_receipt = $EnvironmentReceipt
                work_root = $WorkRoot
                result_root = $ResultRoot
                orchestration_receipt = $OrchestrationReceipt
                execution_context = $BaselineAdmissionExecutionContext
                predecessor_stage_receipt_set_sha256 = $PredecessorStageReceiptSetSha256
                qualification_contract_sha256 = $QualificationContractSha256
                predecessor_stage_receipt_set = $PredecessorStageReceiptSet
                qualification_contract = $QualificationContract
                stdout_path = $StdoutPath
                stderr_path = $StderrPath
                failure_injection = $FailureInjection
                empty_state_fixture_variable = $EmptyStateFixtureVariable
            }
            environment = [ordered]@{
                configured = $environmentConfigured
                restored = $environmentRestored
                before = $environmentBefore
                applied = $environmentApplied
                after_restore = $environmentAfterRestore
            }
            identity = $identity
            execution_context = $BaselineAdmissionExecutionContext
            predecessor_stage_receipt_set_sha256 = $PredecessorStageReceiptSetSha256
            qualification_contract_sha256 = $QualificationContractSha256
            stdout = [ordered]@{
                path = if ([System.IO.File]::Exists($resolvedStdout)) { $resolvedStdout.Replace('\', '/') } else { $null }
                sha256 = if ([System.IO.File]::Exists($resolvedStdout)) { Get-Sha256 $resolvedStdout } else { $null }
            }
            stderr = [ordered]@{
                path = if ([System.IO.File]::Exists($resolvedStderr)) { $resolvedStderr.Replace('\', '/') } else { $null }
                sha256 = if ([System.IO.File]::Exists($resolvedStderr)) { Get-Sha256 $resolvedStderr } else { $null }
            }
            result_receipt = [ordered]@{
                exists = $resultReceiptExists
                path = if ($resultReceiptExists) { $resultReceiptPath.Replace('\', '/') } else { $null }
                sha256 = $resultReceiptHash
            }
            receipt_write_status = 'succeeded'
            validation_ceiling = if ([string]::IsNullOrEmpty($EmptyStateFixtureVariable)) {
                'PowerShell parameter-binding failures occur before launcher receipt initialization and are outside the all-path receipt claim.'
            }
            else {
                'Test-fixture-only receipt: empty-state classification was simulated because Windows child-process environment transport normalizes an empty value to absent.'
            }
        }
        Write-JsonNoBomAtomic $resolvedOrchestrationReceipt $receiptPayload
    }
    catch {
        $receiptWriteStatus = 'failed'
        $receiptWriteFailure = $_
        $fallbackOperatorRecord = [ordered]@{
            schema_version = 'iris-clean-checkout-orchestration-writer-fallback-v1'
            receipt_write_status = 'failed'
            receipt_path = $resolvedOrchestrationReceipt
            writer_exception_type = $_.Exception.GetType().FullName
            writer_exception_message = $_.Exception.Message
            launch_status = $launchStatus
            native_exit_code = $nativeExitCode
            primary_failure = $primaryFailure
            secondary_failures = $secondaryFailures
            environment_restored = $environmentRestored
            validation_ceiling = 'The primary receipt could not be persisted; this structured stderr record is operator evidence, not a substitute receipt.'
        }
        try {
            [Console]::Error.WriteLine(($fallbackOperatorRecord | ConvertTo-Json -Compress -Depth 24))
        }
        catch {
            [Console]::Error.WriteLine('orchestration receipt writer and structured fallback serialization both failed')
        }
    }
}

if ($null -ne $receiptWriteFailure) { exit 125 }
if ($null -ne $primaryFailure) {
    if ($primaryFailure.kind -eq 'native_gate_exit_nonzero') { exit [int]$nativeExitCode }
    [Console]::Error.WriteLine(($primaryFailure | ConvertTo-Json -Compress -Depth 8))
    exit 1
}
exit 0
