[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$CommandSpec
)

$ErrorActionPreference = 'Stop'

if (-not ('IrisRepositoryRuntimeFinalPath' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;

public static class IrisRepositoryRuntimeFinalPath {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateFile(
        string fileName,
        uint desiredAccess,
        uint shareMode,
        IntPtr securityAttributes,
        uint creationDisposition,
        uint flagsAndAttributes,
        IntPtr templateFile
    );

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandle(
        SafeFileHandle file,
        StringBuilder path,
        uint pathLength,
        uint flags
    );

    public static string Resolve(string path) {
        const uint ShareAll = 0x00000007;
        const uint OpenExisting = 3;
        const uint BackupSemantics = 0x02000000;
        using (SafeFileHandle handle = CreateFile(
            path, 0, ShareAll, IntPtr.Zero, OpenExisting, BackupSemantics, IntPtr.Zero
        )) {
            if (handle.IsInvalid) {
                throw new Win32Exception(Marshal.GetLastWin32Error(), "cannot open path for final-target resolution");
            }
            StringBuilder buffer = new StringBuilder(32768);
            uint length = GetFinalPathNameByHandle(handle, buffer, (uint)buffer.Capacity, 0);
            if (length == 0 || length >= buffer.Capacity) {
                throw new Win32Exception(Marshal.GetLastWin32Error(), "cannot resolve final path target");
            }
            string resolved = buffer.ToString();
            if (resolved.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase)) {
                resolved = @"\\" + resolved.Substring(8);
            } else if (resolved.StartsWith(@"\\?\", StringComparison.OrdinalIgnoreCase)) {
                resolved = resolved.Substring(4);
            }
            return Path.GetFullPath(resolved);
        }
    }
}
'@
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-BytesSha256([byte[]]$Bytes) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Quote-WindowsArgument([string]$Value) {
    if ($Value.Length -eq 0) { return '""' }
    if ($Value -notmatch '[\s"]') { return $Value }
    $builder = [System.Text.StringBuilder]::new()
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
        if ($backslashes -gt 0) { [void]$builder.Append(('\' * $backslashes)); $backslashes = 0 }
        [void]$builder.Append($character)
    }
    if ($backslashes -gt 0) { [void]$builder.Append(('\' * ($backslashes * 2))) }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function Invoke-RawProcess(
    [string]$Executable,
    [string[]]$Arguments,
    [string]$WorkingDirectory,
    [string]$StdoutPath,
    [string]$StderrPath
) {
    $info = [System.Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $Executable
    $info.Arguments = (($Arguments | ForEach-Object { Quote-WindowsArgument ([string]$_) }) -join ' ')
    $info.WorkingDirectory = $WorkingDirectory
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $info
    $stdout = $null
    $stderr = $null
    try {
        $stdout = [System.IO.File]::Open($StdoutPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
        $stderr = [System.IO.File]::Open($StderrPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
        if (-not $process.Start()) { throw "failed to start process: $Executable" }
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
        $process.WaitForExit()
        [void]$stdoutTask.GetAwaiter().GetResult()
        [void]$stderrTask.GetAwaiter().GetResult()
        return $process.ExitCode
    }
    finally {
        if ($null -ne $stdout) { $stdout.Dispose() }
        if ($null -ne $stderr) { $stderr.Dispose() }
        $process.Dispose()
    }
}

function Invoke-CapturedText([string]$Executable, [string[]]$Arguments, [string]$WorkingDirectory) {
    $info = [System.Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $Executable
    $info.Arguments = (($Arguments | ForEach-Object { Quote-WindowsArgument ([string]$_) }) -join ' ')
    $info.WorkingDirectory = $WorkingDirectory
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $info
    try {
        if (-not $process.Start()) { throw "failed to start support process: $Executable" }
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        return [ordered]@{ exit_code = $process.ExitCode; stdout = $stdout; stderr = $stderr }
    }
    finally { $process.Dispose() }
}

function Write-JsonNoBomAtomic([string]$Path, [object]$Payload) {
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $json = $Payload | ConvertTo-Json -Depth 32
    $json = $json.Replace("`r`n", "`n")
    if (-not $json.EndsWith("`n")) { $json += "`n" }
    $temporary = Join-Path $parent ('.' + [System.IO.Path]::GetFileName($Path) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    [System.IO.File]::WriteAllText($temporary, $json, ([System.Text.UTF8Encoding]::new($false)))
    if ([System.IO.File]::Exists($Path) -or [System.IO.Directory]::Exists($Path)) {
        [System.IO.File]::Delete($temporary)
        throw "receipt destination already exists: $Path"
    }
    [System.IO.File]::Move($temporary, $Path)
}

function Get-EnvironmentState([string]$Name) {
    $value = [Environment]::GetEnvironmentVariable($Name, 'Process')
    if ($null -eq $value) { return [ordered]@{ state = 'absent'; value = $null } }
    if ($value.Length -eq 0) { return [ordered]@{ state = 'empty'; value = '' } }
    return [ordered]@{ state = 'value'; value = $value }
}

function Restore-EnvironmentState([string]$Name, [object]$State) {
    if ([string]$State.state -eq 'absent') { [Environment]::SetEnvironmentVariable($Name, $null, 'Process') }
    else { [Environment]::SetEnvironmentVariable($Name, [string]$State.value, 'Process') }
}

function Test-SameOrNested([string]$Candidate, [string]$Root) {
    $candidatePath = [System.IO.Path]::GetFullPath($Candidate).TrimEnd('\', '/')
    $rootPath = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
    return (
        $candidatePath.Equals($rootPath, [System.StringComparison]::OrdinalIgnoreCase) -or
        $candidatePath.StartsWith($rootPath + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
    )
}

function Assert-NoReparseComponent([string]$Path, [string]$Label) {
    $cursor = [System.IO.Path]::GetFullPath($Path)
    while (-not [string]::IsNullOrWhiteSpace($cursor)) {
        if ([System.IO.File]::Exists($cursor) -or [System.IO.Directory]::Exists($cursor)) {
            $attributes = [System.IO.File]::GetAttributes($cursor)
            if (($attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "$Label traverses a reparse point: $cursor"
            }
        }
        $parent = [System.IO.Path]::GetDirectoryName($cursor)
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent.Equals($cursor, [System.StringComparison]::OrdinalIgnoreCase)) { break }
        $cursor = $parent
    }
}

function Get-FinalExistingPath([string]$Path, [string]$Label) {
    $full = [System.IO.Path]::GetFullPath($Path)
    if (-not [System.IO.File]::Exists($full) -and -not [System.IO.Directory]::Exists($full)) {
        throw "$Label is missing: $full"
    }
    return [IrisRepositoryRuntimeFinalPath]::Resolve($full).TrimEnd('\', '/')
}

function Assert-ExternalOutputPath([string]$Path, [string]$RepositoryRoot, [string]$Label) {
    $full = [System.IO.Path]::GetFullPath($Path)
    $parent = [System.IO.Path]::GetDirectoryName($full)
    if (-not [System.IO.Directory]::Exists($parent)) { throw "$Label parent is missing: $parent" }
    Assert-NoReparseComponent $full $Label
    $finalParent = Get-FinalExistingPath $parent "$Label parent"
    $final = Join-Path $finalParent ([System.IO.Path]::GetFileName($full))
    if ((Test-SameOrNested $full $RepositoryRoot) -or (Test-SameOrNested $final $RepositoryRoot)) {
        throw "$Label must be repository-external in lexical and resolved form"
    }
}

function Assert-ExternalExistingPath([string]$Path, [string]$RepositoryRoot, [string]$Label) {
    $full = [System.IO.Path]::GetFullPath($Path)
    Assert-NoReparseComponent $full $Label
    $final = Get-FinalExistingPath $full $Label
    if ((Test-SameOrNested $full $RepositoryRoot) -or (Test-SameOrNested $final $RepositoryRoot)) {
        throw "$Label must be repository-external in lexical and resolved form"
    }
}

function Get-GitPathSet([string]$WorkingDirectory, [string[]]$Arguments) {
    $git = (Get-Command git -ErrorAction Stop).Source
    $result = Invoke-CapturedText $git (@('-C', $WorkingDirectory) + $Arguments) $WorkingDirectory
    if ($result.exit_code -ne 0) { throw "Git checkout census failed: $($result.stderr.Trim())" }
    $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($path in ($result.stdout -split "`0")) {
        if (-not [string]::IsNullOrEmpty($path)) { [void]$set.Add($path.Replace('\', '/')) }
    }
    return $set
}

function Get-CheckoutCensus([string]$WorkingDirectory) {
    $root = [System.IO.Path]::GetFullPath($WorkingDirectory).TrimEnd('\', '/')
    $tracked = Get-GitPathSet $root @('ls-files', '-z')
    $untracked = Get-GitPathSet $root @('ls-files', '-z', '--others', '--exclude-standard')
    $ignored = Get-GitPathSet $root @('ls-files', '-z', '--others', '-i', '--exclude-standard')
    $rows = [ordered]@{}
    $unreadable = @()
    try {
        $files = Get-ChildItem -LiteralPath $root -Force -File -Recurse -ErrorAction Stop | Where-Object {
            $relativeCandidate = $_.FullName.Substring($root.Length).TrimStart('\', '/').Replace('\', '/')
            -not ($relativeCandidate -eq '.git' -or $relativeCandidate.StartsWith('.git/'))
        }
    }
    catch {
        $unreadable += [ordered]@{ path = $root.Replace('\', '/'); error_type = $_.Exception.GetType().FullName; error = $_.Exception.Message }
        $files = @()
    }
    foreach ($file in ($files | Sort-Object FullName)) {
        $relative = $file.FullName.Substring($root.Length).TrimStart('\', '/').Replace('\', '/')
        try {
            $state = if ($null -ne $tracked -and $tracked.Contains($relative)) { 'tracked' }
                elseif ($null -ne $ignored -and $ignored.Contains($relative)) { 'ignored' }
                elseif ($null -ne $untracked -and $untracked.Contains($relative)) { 'untracked' }
                else { 'filesystem_only' }
            $rows[$relative] = [ordered]@{
                size_bytes = $file.Length
                sha256 = Get-Sha256 $file.FullName
                vcs_state = $state
            }
        }
        catch {
            $unreadable += [ordered]@{ path = $relative; error_type = $_.Exception.GetType().FullName; error = $_.Exception.Message }
        }
    }
    $fingerprintRows = @()
    foreach ($key in @($rows.Keys)) {
        $fingerprintRows += [ordered]@{ path = $key; size_bytes = $rows[$key].size_bytes; sha256 = $rows[$key].sha256; vcs_state = $rows[$key].vcs_state }
    }
    $fingerprintJson = $fingerprintRows | ConvertTo-Json -Depth 6 -Compress
    return [ordered]@{
        root = $root.Replace('\', '/')
        file_count = $rows.Count
        unreadable_count = $unreadable.Count
        unreadable = $unreadable
        fingerprint_sha256 = Get-BytesSha256 (([System.Text.UTF8Encoding]::new($false)).GetBytes($fingerprintJson))
        rows = $rows
    }
}

function Compare-Census([object]$Before, [object]$After) {
    $allPaths = @((@($Before.rows.Keys) + @($After.rows.Keys)) | Sort-Object -Unique)
    $delta = @()
    foreach ($path in $allPaths) {
        $left = $Before.rows[$path]
        $right = $After.rows[$path]
        if ($null -eq $left) {
            $delta += [ordered]@{ path = $path; change = 'added'; vcs_state = $right.vcs_state; before = $null; after = $right }
        }
        elseif ($null -eq $right) {
            $delta += [ordered]@{ path = $path; change = 'removed'; vcs_state = $left.vcs_state; before = $left; after = $null }
        }
        elseif ($left.sha256 -ne $right.sha256 -or [long]$left.size_bytes -ne [long]$right.size_bytes -or $left.vcs_state -ne $right.vcs_state) {
            $delta += [ordered]@{ path = $path; change = 'changed'; vcs_state = $right.vcs_state; before = $left; after = $right }
        }
    }
    return [ordered]@{
        changed_count = $delta.Count
        tracked_delta_count = @($delta | Where-Object { $_.vcs_state -eq 'tracked' }).Count
        untracked_delta_count = @($delta | Where-Object { $_.vcs_state -eq 'untracked' }).Count
        ignored_delta_count = @($delta | Where-Object { $_.vcs_state -eq 'ignored' }).Count
        filesystem_only_delta_count = @($delta | Where-Object { $_.vcs_state -eq 'filesystem_only' }).Count
        unreadable_count = [int]$Before.unreadable_count + [int]$After.unreadable_count
        rows = $delta
    }
}

function Get-CensusReceiptSummary([object]$Census) {
    if ($null -eq $Census) { return $null }
    return [ordered]@{
        root = $Census.root
        file_count = $Census.file_count
        unreadable_count = $Census.unreadable_count
        unreadable = $Census.unreadable
        fingerprint_sha256 = $Census.fingerprint_sha256
    }
}

$specPath = [System.IO.Path]::GetFullPath($CommandSpec)
$specHash = $null
$spec = $null
$receiptPath = $null
$stdoutPath = $null
$stderrPath = $null
$start = [DateTimeOffset]::UtcNow
$end = $null
$nativeExit = $null
$semanticExit = 2
$terminalStatus = 'preflight_failed'
$disposition = 'failed'
$failure = $null
$actualArgv = $null
$environmentBefore = [ordered]@{}
$environmentAfter = [ordered]@{}
$environmentRestored = $false
$environmentDeltaIdentity = $null
$subjectIdentity = $null
$environmentIdentity = $null
$authorityPath = $null
$successorPolicyPath = $null
$implementationIdentity = $null
$invokedRepositoryFiles = @()
$assertion = [ordered]@{ kind = 'none'; status = 'not_run' }
$preCensus = $null
$postCensus = $null
$censusDelta = $null
$receiptWritable = $false

try {
    if (-not [System.IO.File]::Exists($specPath)) { throw "command spec is missing: $specPath" }
    $specHash = Get-Sha256 $specPath
    $spec = Get-Content -Raw -Encoding UTF8 -LiteralPath $specPath | ConvertFrom-Json
    if ([string]$spec.schema_version -ne 'iris_repository_runtime_lightweighting_command_spec_v1') { throw 'command spec schema mismatch' }
    foreach ($required in @('executable', 'argv', 'working_directory', 'subject_receipt', 'environment_receipt', 'environment_delta', 'claim_id', 'command_id', 'command_receipt', 'output_assertion')) {
        if ($null -eq $spec.$required) { throw "command spec field is missing: $required" }
    }
    if ([string]$spec.command_id -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$') { throw 'command ID is invalid' }
    if ([string]$spec.output_assertion -notin @('none', 'empty_git_porcelain', 'checkout_unchanged')) { throw "unsupported output assertion: $($spec.output_assertion)" }
    if ($null -ne $spec.prior_command_receipts -and $spec.prior_command_receipts -isnot [System.Array]) { throw 'prior_command_receipts must remain a JSON array' }
    $receiptPath = [System.IO.Path]::GetFullPath([string]$spec.command_receipt)
    $receiptParent = [System.IO.Path]::GetDirectoryName($receiptPath)
    if (-not [System.IO.Directory]::Exists($receiptParent)) { throw 'preallocated command receipt directory is missing' }
    if ([System.IO.File]::Exists($receiptPath) -or [System.IO.Directory]::Exists($receiptPath)) { throw 'command receipt already exists' }
    $stdoutPath = Join-Path $receiptParent ([string]$spec.command_id + '.stdout.bin')
    $stderrPath = Join-Path $receiptParent ([string]$spec.command_id + '.stderr.bin')
    if ([System.IO.File]::Exists($stdoutPath) -or [System.IO.File]::Exists($stderrPath)) { throw 'command stream path already exists' }

    $workingDirectory = [System.IO.Path]::GetFullPath([string]$spec.working_directory)
    if (-not [System.IO.Directory]::Exists($workingDirectory)) { throw 'working directory is missing' }
    Assert-NoReparseComponent $workingDirectory 'working directory'
    $executable = [System.IO.Path]::GetFullPath([string]$spec.executable)
    if (-not [System.IO.File]::Exists($executable)) { throw 'executable is missing' }

    $repositoryResult = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $workingDirectory, 'rev-parse', '--show-toplevel') $workingDirectory
    if ($repositoryResult.exit_code -ne 0) { throw 'working directory is not inside a Git checkout' }
    $repositoryRoot = Get-FinalExistingPath $repositoryResult.stdout.Trim() 'repository root'
    $finalWorkingDirectory = Get-FinalExistingPath $workingDirectory 'working directory'
    if (-not $finalWorkingDirectory.Equals($repositoryRoot, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'working directory must be the exact checkout root' }
    Assert-ExternalExistingPath $specPath $repositoryRoot 'command spec'
    Assert-ExternalOutputPath $receiptPath $repositoryRoot 'command receipt'
    Assert-ExternalOutputPath $stdoutPath $repositoryRoot 'command stdout stream'
    Assert-ExternalOutputPath $stderrPath $repositoryRoot 'command stderr stream'
    $receiptWritable = $true
    if ($spec.argv -isnot [System.Array]) { throw 'command spec argv must remain a JSON array' }
    $arguments = @($spec.argv | ForEach-Object { [string]$_ })
    $actualArgv = @($executable) + $arguments
    $expectedWrapper = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot 'Iris\validation\clean_checkout\invoke_repository_runtime_lightweighting_command.ps1'))
    $actualWrapper = [System.IO.Path]::GetFullPath($MyInvocation.MyCommand.Path)
    if (-not $actualWrapper.Equals($expectedWrapper, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'command wrapper was loaded from a different checkout' }

    $subjectPath = [System.IO.Path]::GetFullPath([string]$spec.subject_receipt)
    $environmentPath = [System.IO.Path]::GetFullPath([string]$spec.environment_receipt)
    $deltaPath = [System.IO.Path]::GetFullPath([string]$spec.environment_delta)
    foreach ($path in @($subjectPath, $environmentPath, $deltaPath)) {
        if (-not [System.IO.File]::Exists($path)) { throw "identity input is missing: $path" }
        Assert-ExternalExistingPath $path $repositoryRoot 'identity input'
    }
    $subject = Get-Content -Raw -Encoding UTF8 -LiteralPath $subjectPath | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace([string]$spec.claim_id)) { throw 'command claim ID is empty' }
    if ([string]::IsNullOrWhiteSpace([string]$subject.claim_id) -or [string]$subject.claim_id -ne [string]$spec.claim_id) { throw 'subject receipt claim mismatch' }
    if ([string]::IsNullOrWhiteSpace([string]$subject.subject_kind)) { throw 'subject receipt lacks subject_kind' }
    if ([string]::IsNullOrWhiteSpace([string]$subject.commit) -or [string]::IsNullOrWhiteSpace([string]$subject.tree)) { throw 'subject receipt lacks exact commit/tree' }
    $headResult = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'rev-parse', 'HEAD') $repositoryRoot
    $executionTreeResult = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'rev-parse', 'HEAD^{tree}') $repositoryRoot
    $treeResult = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'rev-parse', ([string]$subject.commit + '^{tree}')) $repositoryRoot
    if ($headResult.exit_code -ne 0 -or $executionTreeResult.exit_code -ne 0) { throw 'working checkout HEAD/tree is unresolved' }
    if ($treeResult.exit_code -ne 0 -or $treeResult.stdout.Trim() -ne [string]$subject.tree) { throw 'working checkout tree differs from command subject' }
    if ([string]$subject.subject_kind -eq 'physical_capacity_subject') {
        $ancestorResult = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'merge-base', '--is-ancestor', [string]$subject.commit, 'HEAD') $repositoryRoot
        if ($ancestorResult.exit_code -ne 0) { throw 'physical subject commit is not an ancestor of the current checkout' }
    }
    elseif ($headResult.stdout.Trim() -ne [string]$subject.commit) { throw 'validation checkout HEAD differs from exact command subject' }
    $subjectStatusResult = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'status', '--porcelain=v1', '-z', '--untracked-files=all') $repositoryRoot
    if ($subjectStatusResult.exit_code -ne 0) { throw 'command subject working-tree status is unresolved' }
    $subjectStatusSha = Get-BytesSha256 (([System.Text.UTF8Encoding]::new($false)).GetBytes($subjectStatusResult.stdout))
    if ($null -ne $subject.working_tree_status_sha256 -and [string]$subject.working_tree_status_sha256 -ne $subjectStatusSha) { throw 'command checkout working-tree status differs from subject receipt' }
    if ($null -ne $subject.physical_resolved_root -and -not ([System.IO.Path]::GetFullPath([string]$subject.physical_resolved_root).Equals($repositoryRoot, [System.StringComparison]::OrdinalIgnoreCase))) { throw 'physical subject root differs from command checkout' }
    if ($null -ne $subject.repository_root -and -not ([System.IO.Path]::GetFullPath([string]$subject.repository_root).Equals($repositoryRoot, [System.StringComparison]::OrdinalIgnoreCase))) { throw 'validation subject root differs from command checkout' }
    $executionCommit = $headResult.stdout.Trim()
    $executionTree = $executionTreeResult.stdout.Trim()
    $subjectIdentity = [ordered]@{ path = $subjectPath.Replace('\', '/'); sha256 = Get-Sha256 $subjectPath; subject_kind = $subject.subject_kind; claim_id = $spec.claim_id; repository_root = $repositoryRoot.Replace('\', '/'); commit = [string]$subject.commit; tree = [string]$subject.tree; execution_commit = $executionCommit; execution_tree = $executionTree; working_tree_status_sha256 = $subjectStatusSha }

    $authorityPath = Join-Path $repositoryRoot 'Iris\validation\clean_checkout\authority\phase0_ratification_attempt_0002.json'
    $successorPolicyPath = Join-Path $repositoryRoot 'Iris\validation\clean_checkout\contracts\repository_runtime_lightweighting_output_policy.json'
    foreach ($path in @($authorityPath, $successorPolicyPath)) {
        if (-not [System.IO.File]::Exists($path)) { throw "command authority input is missing: $path" }
    }
    $implementationIdentity = [ordered]@{}
    foreach ($row in @(
        @('wrapper', 'Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1', $actualWrapper),
        @('successor_policy', 'Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json', $successorPolicyPath),
        @('environment_authority', 'Iris/validation/clean_checkout/authority/phase0_ratification_attempt_0002.json', $authorityPath)
    )) {
        $blob = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'rev-parse', ($executionCommit + ':' + $row[1])) $repositoryRoot
        $workingBlob = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'hash-object', ('--path=' + $row[1]), $row[2]) $repositoryRoot
        if ($blob.exit_code -ne 0 -or $workingBlob.exit_code -ne 0 -or $blob.stdout.Trim() -ne $workingBlob.stdout.Trim()) { throw "$($row[0]) differs from exact execution commit" }
        $implementationIdentity[$row[0]] = [ordered]@{ logical_path = $row[1]; actual_path = ([System.IO.Path]::GetFullPath($row[2])).Replace('\', '/'); execution_commit = $executionCommit; git_blob_id = $blob.stdout.Trim(); working_sha256 = Get-Sha256 $row[2] }
    }

    $targetCandidates = @()
    if (Test-SameOrNested $executable $repositoryRoot) { $targetCandidates += $executable }
    foreach ($argument in $arguments) {
        $argumentValue = [string]$argument
        if ($argumentValue -notmatch '(?i)\.(py|ps1|lua)$') { continue }
        $candidate = if ([System.IO.Path]::IsPathRooted($argumentValue)) {
            [System.IO.Path]::GetFullPath($argumentValue)
        }
        else {
            [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot $argumentValue))
        }
        if ([System.IO.File]::Exists($candidate) -and (Test-SameOrNested $candidate $repositoryRoot)) {
            $targetCandidates += $candidate
        }
    }
    $moduleIndex = [Array]::IndexOf($arguments, '-m')
    if ($moduleIndex -ge 0 -and ($moduleIndex + 1) -lt $arguments.Count) {
        $moduleName = [string]$arguments[$moduleIndex + 1]
        if ($moduleName -eq 'unittest' -and $arguments -contains 'discover') {
            $startIndex = [Array]::IndexOf($arguments, '-s')
            $patternIndex = [Array]::IndexOf($arguments, '-p')
            if ($startIndex -lt 0 -or ($startIndex + 1) -ge $arguments.Count -or $patternIndex -lt 0 -or ($patternIndex + 1) -ge $arguments.Count) {
                throw 'unittest discover invocation lacks exact -s/-p implementation boundary'
            }
            $discoverRootValue = [string]$arguments[$startIndex + 1]
            $discoverRoot = if ([System.IO.Path]::IsPathRooted($discoverRootValue)) { [System.IO.Path]::GetFullPath($discoverRootValue) } else { [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot $discoverRootValue)) }
            if (-not [System.IO.Directory]::Exists($discoverRoot) -or -not (Test-SameOrNested $discoverRoot $repositoryRoot)) { throw 'unittest discover root is not an exact repository directory' }
            $discoveredTargets = @(Get-ChildItem -LiteralPath $discoverRoot -File -Recurse -Filter ([string]$arguments[$patternIndex + 1]) -ErrorAction Stop)
            if ($discoveredTargets.Count -eq 0) { throw 'unittest discover pattern resolves no repository implementation' }
            $targetCandidates += @($discoveredTargets | ForEach-Object { $_.FullName })
        }
        elseif ($moduleName -notin @('pytest', 'unittest')) {
            $moduleRelative = $moduleName.Replace('.', '/') + '.py'
            $moduleCandidates = @(
                (Join-Path $repositoryRoot $moduleRelative),
                (Join-Path $repositoryRoot ('Iris/build/description/v2/tools/build/' + [System.IO.Path]::GetFileName($moduleRelative))),
                (Join-Path $repositoryRoot ('Iris/build/description/v2/tools/' + [System.IO.Path]::GetFileName($moduleRelative)))
            )
            $resolvedModules = @($moduleCandidates | Where-Object { [System.IO.File]::Exists($_) } | ForEach-Object { [System.IO.Path]::GetFullPath($_) } | Sort-Object -Unique)
            if ($resolvedModules.Count -gt 1) { throw "Python -m repository module is ambiguous: $moduleName" }
            if ($resolvedModules.Count -eq 1) { $targetCandidates += $resolvedModules[0] }
        }
    }
    foreach ($targetPath in @($targetCandidates | Sort-Object -Unique)) {
        $relativeTarget = $targetPath.Substring($repositoryRoot.TrimEnd('\', '/').Length).TrimStart('\', '/').Replace('\', '/')
        $targetBlob = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'rev-parse', ($executionCommit + ':' + $relativeTarget)) $repositoryRoot
        $workingTargetBlob = Invoke-CapturedText (Get-Command git -ErrorAction Stop).Source @('-C', $repositoryRoot, 'hash-object', ('--path=' + $relativeTarget), $targetPath) $repositoryRoot
        if ($targetBlob.exit_code -ne 0 -or $workingTargetBlob.exit_code -ne 0 -or $targetBlob.stdout.Trim() -ne $workingTargetBlob.stdout.Trim()) {
            throw "invoked repository implementation differs from exact execution commit: $relativeTarget"
        }
        $invokedRepositoryFiles += [ordered]@{
            logical_path = $relativeTarget
            actual_path = $targetPath.Replace('\', '/')
            execution_commit = $executionCommit
            git_blob_id = $targetBlob.stdout.Trim()
            working_sha256 = Get-Sha256 $targetPath
        }
    }
    $authority = Get-Content -Raw -Encoding UTF8 -LiteralPath $authorityPath | ConvertFrom-Json
    $ownerEnvironment = $authority.implementation_contract_delta.'OR-06'
    if ([string]$ownerEnvironment.status -ne 'resolved') { throw 'environment_authority_unresolved' }
    if (-not $environmentPath.Equals([System.IO.Path]::GetFullPath([string]$ownerEnvironment.immutable_environment_receipt_path), [System.StringComparison]::OrdinalIgnoreCase)) { throw 'environment receipt path differs from owner authority' }
    $environmentHash = Get-Sha256 $environmentPath
    if ($environmentHash -ne [string]$ownerEnvironment.immutable_environment_receipt_sha256) { throw 'environment receipt hash differs from owner authority' }
    $environmentPayload = Get-Content -Raw -Encoding UTF8 -LiteralPath $environmentPath | ConvertFrom-Json
    $authorityInterpreter = [System.IO.Path]::GetFullPath([string]$environmentPayload.interpreter.path)
    if (-not [System.IO.File]::Exists($authorityInterpreter)) { throw 'authority interpreter is missing' }
    if ((Get-Sha256 $authorityInterpreter) -ne [string]$ownerEnvironment.interpreter_sha256) { throw 'authority interpreter hash mismatch' }
    $environmentIdentity = [ordered]@{ path = $environmentPath.Replace('\', '/'); sha256 = $environmentHash; interpreter_path = $authorityInterpreter.Replace('\', '/'); interpreter_sha256 = Get-Sha256 $authorityInterpreter }

    $delta = Get-Content -Raw -Encoding UTF8 -LiteralPath $deltaPath | ConvertFrom-Json
    if ([string]$delta.schema_version -ne 'iris_repository_runtime_lightweighting_environment_delta_v1') { throw 'environment delta schema mismatch' }
    if ($null -eq $delta.set -or $delta.set -isnot [System.Management.Automation.PSCustomObject] -or $delta.clear -isnot [System.Array]) { throw 'environment delta set/clear shape mismatch' }
    $environmentDeltaIdentity = [ordered]@{ path = $deltaPath.Replace('\', '/'); sha256 = Get-Sha256 $deltaPath }
    $successorPolicy = Get-Content -Raw -Encoding UTF8 -LiteralPath $successorPolicyPath | ConvertFrom-Json
    if ([string]$successorPolicy.schema_version -ne 'iris_repository_runtime_lightweighting_output_policy_v1') { throw 'successor output policy schema mismatch' }
    foreach ($property in @($successorPolicy.required_environment.PSObject.Properties)) {
        $actualProperties = @($delta.set.PSObject.Properties | Where-Object { [string]$_.Name -eq [string]$property.Name })
        if ($actualProperties.Count -ne 1 -or [string]$actualProperties[0].Value -ne [string]$property.Value) { throw "environment delta does not adopt required value: $($property.Name)" }
    }
    $clearedNames = @($delta.clear | ForEach-Object { [string]$_ })
    foreach ($name in @($successorPolicy.cleared_ambient_environment)) {
        if ($clearedNames -notcontains [string]$name) { throw "environment delta does not clear required variable: $name" }
    }

    if ($null -ne $spec.prior_command_receipts) {
        foreach ($priorPathValue in @($spec.prior_command_receipts)) {
            $priorPath = [System.IO.Path]::GetFullPath([string]$priorPathValue)
            if (-not [System.IO.File]::Exists($priorPath)) { throw "prior command receipt is missing: $priorPath" }
            $prior = Get-Content -Raw -Encoding UTF8 -LiteralPath $priorPath | ConvertFrom-Json
            if ([string]$prior.claim_id -ne [string]$spec.claim_id -or [string]$prior.subject_receipt.sha256 -ne [string]$subjectIdentity.sha256 -or [string]$prior.subject_receipt.execution_commit -ne $executionCommit -or [string]$prior.subject_receipt.execution_tree -ne $executionTree) { throw 'prior command receipt subject/claim/execution mismatch' }
            if ([string]$prior.terminal_status -ne 'pass') {
                $terminalStatus = 'not_run_due_to_prior_failure'
                $disposition = 'not_run_due_to_prior_failure'
                $semanticExit = 90
                throw 'prior command failed; target command was not run'
            }
        }
    }

    $environmentNames = @()
    foreach ($property in @($delta.set.PSObject.Properties)) { $environmentNames += [string]$property.Name }
    foreach ($name in @($delta.clear)) { $environmentNames += [string]$name }
    $environmentNames = @($environmentNames | Sort-Object -Unique)
    foreach ($name in $environmentNames) { $environmentBefore[$name] = Get-EnvironmentState $name }
    foreach ($name in @($delta.clear)) { [Environment]::SetEnvironmentVariable([string]$name, $null, 'Process') }
    foreach ($property in @($delta.set.PSObject.Properties)) { [Environment]::SetEnvironmentVariable([string]$property.Name, [string]$property.Value, 'Process') }

    if ([string]$spec.output_assertion -eq 'checkout_unchanged') { $preCensus = Get-CheckoutCensus $workingDirectory }
    Assert-ExternalOutputPath $receiptPath $repositoryRoot 'command receipt'
    Assert-ExternalOutputPath $stdoutPath $repositoryRoot 'command stdout stream'
    Assert-ExternalOutputPath $stderrPath $repositoryRoot 'command stderr stream'
    $nativeExit = Invoke-RawProcess $executable $arguments $workingDirectory $stdoutPath $stderrPath
    if ([string]$spec.output_assertion -eq 'checkout_unchanged') {
        $postCensus = Get-CheckoutCensus $workingDirectory
        $censusDelta = Compare-Census $preCensus $postCensus
        $assertion = [ordered]@{ kind = 'checkout_unchanged'; status = if ($censusDelta.changed_count -eq 0 -and $censusDelta.unreadable_count -eq 0) { 'pass' } else { 'fail' }; delta = $censusDelta }
    }
    elseif ([string]$spec.output_assertion -eq 'empty_git_porcelain') {
        $executableName = [System.IO.Path]::GetFileName($executable).ToLowerInvariant()
        if ($executableName -notin @('git', 'git.exe') -or $arguments -notcontains 'status' -or $arguments -notcontains '--porcelain=v1' -or $arguments -notcontains '-z') { throw 'empty_git_porcelain requires exact NUL-delimited Git status invocation' }
        $stdoutBytes = [System.IO.File]::ReadAllBytes($stdoutPath)
        $decoded = ([System.Text.UTF8Encoding]::new($false, $false)).GetString($stdoutBytes)
        $dirty = @($decoded -split "`0" | Where-Object { -not [string]::IsNullOrEmpty($_) })
        $assertion = [ordered]@{ kind = 'empty_git_porcelain'; status = if ($dirty.Count -eq 0) { 'pass' } else { 'fail' }; raw_sha256 = Get-BytesSha256 $stdoutBytes; dirty_entries = $dirty }
    }
    elseif ([string]$spec.output_assertion -eq 'none') {
        $assertion = [ordered]@{ kind = 'none'; status = 'pass' }
    }
    else { throw "unsupported output assertion: $($spec.output_assertion)" }

    if ($nativeExit -eq 0 -and [string]$assertion.status -eq 'pass') {
        $terminalStatus = 'pass'
        $disposition = 'executed'
        $semanticExit = 0
    }
    else {
        $terminalStatus = 'fail'
        $disposition = 'executed'
        $semanticExit = if ($nativeExit -ne 0) { [int]$nativeExit } else { 3 }
        $failure = [ordered]@{ kind = if ($nativeExit -ne 0) { 'native_exit_nonzero' } else { 'output_assertion_failed' }; native_exit_code = $nativeExit; assertion_status = $assertion.status }
    }
}
catch {
    if ($null -eq $failure) {
        $failure = [ordered]@{ kind = if ($terminalStatus -eq 'not_run_due_to_prior_failure') { 'prior_command_failed' } else { 'exception' }; exception_type = $_.Exception.GetType().FullName; exception_message = $_.Exception.Message }
    }
}
finally {
    foreach ($name in @($environmentBefore.Keys)) {
        try { Restore-EnvironmentState $name $environmentBefore[$name]; $environmentAfter[$name] = Get-EnvironmentState $name }
        catch { $failure = [ordered]@{ kind = 'environment_restore_failed'; variable = $name; exception_message = $_.Exception.Message }; $terminalStatus = 'fail'; $semanticExit = 4 }
    }
    $environmentRestored = $true
    foreach ($name in @($environmentBefore.Keys)) {
        if ([string]$environmentBefore[$name].state -ne [string]$environmentAfter[$name].state -or [string]$environmentBefore[$name].value -ne [string]$environmentAfter[$name].value) { $environmentRestored = $false }
    }
    if (-not $environmentRestored -and $environmentBefore.Count -gt 0) { $terminalStatus = 'fail'; $semanticExit = 4 }
    $end = [DateTimeOffset]::UtcNow
    if ($receiptWritable) {
        try {
            Assert-ExternalOutputPath $receiptPath $repositoryRoot 'command receipt'
            $receiptPayload = [ordered]@{
                schema_version = 'iris_repository_runtime_lightweighting_command_receipt_v1'
                command_id = if ($null -ne $spec) { [string]$spec.command_id } else { $null }
                command_receipt = if ($null -ne $receiptPath) { $receiptPath.Replace('\', '/') } else { $null }
                terminal_status = $terminalStatus
                disposition = $disposition
                failure = $failure
                claim_id = if ($null -ne $spec) { [string]$spec.claim_id } else { $null }
                command_spec = [ordered]@{ path = $specPath.Replace('\', '/'); sha256 = $specHash }
                executable = if ($null -ne $spec) { [System.IO.Path]::GetFullPath([string]$spec.executable).Replace('\', '/') } else { $null }
                decoded_argv = if ($null -ne $spec) { @($spec.argv | ForEach-Object { [string]$_ }) } else { @() }
                actual_argv = $actualArgv
                working_directory = if ($null -ne $spec) { [System.IO.Path]::GetFullPath([string]$spec.working_directory).Replace('\', '/') } else { $null }
                started_at = $start.ToString('o')
                ended_at = $end.ToString('o')
                native_exit_code = $nativeExit
                semantic_exit_code = $semanticExit
                stdout = [ordered]@{ path = if ($stdoutPath -and [System.IO.File]::Exists($stdoutPath)) { $stdoutPath.Replace('\', '/') } else { $null }; sha256 = if ($stdoutPath -and [System.IO.File]::Exists($stdoutPath)) { Get-Sha256 $stdoutPath } else { $null } }
                stderr = [ordered]@{ path = if ($stderrPath -and [System.IO.File]::Exists($stderrPath)) { $stderrPath.Replace('\', '/') } else { $null }; sha256 = if ($stderrPath -and [System.IO.File]::Exists($stderrPath)) { Get-Sha256 $stderrPath } else { $null } }
                subject_receipt = $subjectIdentity
                environment_receipt = $environmentIdentity
                environment_delta = $environmentDeltaIdentity
                environment_authority = if ($authorityPath -and [System.IO.File]::Exists($authorityPath)) { [ordered]@{ path = $authorityPath.Replace('\', '/'); sha256 = Get-Sha256 $authorityPath } } else { $null }
                successor_policy = if ($successorPolicyPath -and [System.IO.File]::Exists($successorPolicyPath)) { [ordered]@{ path = $successorPolicyPath.Replace('\', '/'); sha256 = Get-Sha256 $successorPolicyPath } } else { $null }
                implementation_identity = $implementationIdentity
                invoked_repository_files = $invokedRepositoryFiles
                environment = [ordered]@{ before = $environmentBefore; after_restore = $environmentAfter; restored = $environmentRestored }
                output_assertion = $assertion
                checkout_census = [ordered]@{ before = (Get-CensusReceiptSummary $preCensus); after = (Get-CensusReceiptSummary $postCensus); delta = $censusDelta }
            }
            Write-JsonNoBomAtomic $receiptPath $receiptPayload
        }
        catch {
            [Console]::Error.WriteLine((([ordered]@{ status = 'receipt_write_failed'; exception = $_.Exception.Message; intended_receipt = $receiptPath }) | ConvertTo-Json -Compress))
            exit 125
        }
    }
}

if ($semanticExit -ne 0) {
    if ($null -ne $failure) { [Console]::Error.WriteLine(($failure | ConvertTo-Json -Compress -Depth 8)) }
    exit $semanticExit
}
exit 0
