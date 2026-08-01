[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [Parameter(Mandatory = $true)][string]$HarnessModule,
    [ValidateSet('pre_refactor_characterization','post_refactor_acceptance')][string]$TimeAxis = 'pre_refactor_characterization',
    [string]$RepositoryRoot,
    [string]$PzExecutable = 'G:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/ProjectZomboid64.exe',
    [string]$AcceptedOptionsPath = 'C:/Users/MW/Zomboid/options.ini',
    [int]$TimeoutSeconds = 240
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Get-RelativePath([string]$Root, [string]$Path) {
    $rootUri = New-Object System.Uri(([System.IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'))
    $pathUri = New-Object System.Uri([System.IO.Path]::GetFullPath($Path))
    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString())
}
function Get-TextSha([string]$Text) {
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try { return [System.BitConverter]::ToString($algorithm.ComputeHash($utf8NoBom.GetBytes($Text))).Replace('-','').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}

if (-not $RepositoryRoot) { $RepositoryRoot = (& git rev-parse --show-toplevel 2>&1 | Out-String).Trim() }
$RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\','/')
if (-not (Test-Path -LiteralPath $PzExecutable -PathType Leaf)) { throw "PZ executable missing: $PzExecutable" }
$subjectCommit = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
$subjectTree = (& git -C $RepositoryRoot rev-parse 'HEAD^{tree}').Trim()
$productionPatch = (& git -C $RepositoryRoot diff --binary -- 'Iris/media/lua/client/Iris' 2>&1 | Out-String)
$subjectPatchSha = if ([string]::IsNullOrEmpty($productionPatch)) { $null } else { Get-TextSha $productionPatch }
$statusLines = @(& git -C $RepositoryRoot status --porcelain=v1 -uall -- Iris)
$overlayRows = @()
foreach ($line in $statusLines) {
    if ($line.Length -lt 4) { continue }
    $path = $line.Substring(3).Replace('\','/')
    $full = Join-Path $RepositoryRoot $path
    $hash = if (Test-Path -LiteralPath $full -PathType Leaf) { (Get-FileHash -Algorithm SHA256 -LiteralPath $full).Hash.ToLowerInvariant() } else { $null }
    $overlayRows += "$($line.Substring(0,2))`t$path`t$hash"
}
[System.Array]::Sort($overlayRows, [System.StringComparer]::Ordinal)
$overlaySha = if ($overlayRows.Count -eq 0) { $null } else { Get-TextSha (($overlayRows -join "`n") + "`n") }
$producerState = if ($overlayRows.Count -eq 0) { 'clean' } elseif (@($statusLines | Where-Object { $_.StartsWith('??') }).Count -gt 0) { 'tracked_and_untracked_overlay' } else { 'tracked_overlay' }

$cacheRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('iris-core-refactor-pz-' + [guid]::NewGuid().ToString('N'))
$modRoot = Join-Path $cacheRoot 'mods/Iris'
New-Item -ItemType Directory -Path $modRoot -Force | Out-Null
try {
    if (Test-Path -LiteralPath $AcceptedOptionsPath -PathType Leaf) {
        Copy-Item -LiteralPath $AcceptedOptionsPath -Destination (Join-Path $cacheRoot 'options.ini')
    }
    Copy-Item -LiteralPath (Join-Path $RepositoryRoot 'Iris/mod.info') -Destination $modRoot
    Copy-Item -LiteralPath (Join-Path $RepositoryRoot 'Iris/media') -Destination $modRoot -Recurse
    Copy-Item -Path (Join-Path $RepositoryRoot 'Iris/_dev/media/*') -Destination (Join-Path $modRoot 'media') -Recurse -Force
    $configPath = Join-Path $modRoot 'media/lua/client/Iris/IrisConfig.lua'
    $configText = [System.IO.File]::ReadAllText($configPath)
    $injection = "IrisConfig.DEBUG = true`r`nIrisConfig.RUN_TESTS_ON_START = true`r`nIrisConfig.CORE_REFACTOR_HARNESS_MODULE = `"$HarnessModule`"`r`n`r`nreturn IrisConfig"
    if (-not $configText.Contains('return IrisConfig')) { throw 'candidate IrisConfig return anchor missing' }
    [System.IO.File]::WriteAllText($configPath, $configText.Replace('return IrisConfig', $injection), $utf8NoBom)
    $defaultPath = Join-Path $cacheRoot 'mods/default.txt'
    $defaultText = "VERSION = 1,`r`n`r`nmods`r`n{`r`n`tmod = Iris,`r`n}`r`n`r`nmaps`r`n{`r`n}`r`n"
    [System.IO.File]::WriteAllText($defaultPath, $defaultText, $utf8NoBom)
    $resetSentinel = Join-Path $cacheRoot 'mods/reset-mods-41_51.txt'
    [System.IO.File]::WriteAllText($resetSentinel, "If this file does not exist, default.txt will be reset to empty (no mods active).`r`n", $utf8NoBom)

    $arguments = @("-cachedir=$cacheRoot",'-nosteam','-nosound','-novoip','-debug')
    $process = Start-Process -FilePath $PzExecutable -ArgumentList $arguments -WorkingDirectory (Split-Path -Parent $PzExecutable) -WindowStyle Hidden -PassThru
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        try { $process.Kill() } catch {}
        throw "PZ harness timed out after $TimeoutSeconds seconds"
    }
    $consolePath = Join-Path $cacheRoot 'console.txt'
    if (-not (Test-Path -LiteralPath $consolePath -PathType Leaf)) { throw "PZ console.txt was not produced; process_exit=$($process.ExitCode)" }
    $consoleLines = Get-Content -LiteralPath $consolePath
    $rawRows = @()
    foreach ($line in $consoleLines) {
        if ($line -match 'IRIS_CORE_ROW\s*\t(\{.*\})\s*$') { $rawRows += $Matches[1] }
    }
    if ($rawRows.Count -eq 0) {
        $tail = ($consoleLines | Select-Object -Last 120) -join "`n"
        throw "PZ harness emitted no evidence rows`n$tail"
    }
    $evidenceRows = @()
    foreach ($json in $rawRows) {
        $raw = $json | ConvertFrom-Json
        $row = [ordered]@{
            schema_version=1;case_id=[string]$raw.case_id;axis=[string]$raw.axis;fixture_id=[string]$raw.fixture_id;status=[string]$raw.status
            expected=$raw.expected;observed=$raw.observed;time_axis=$TimeAxis;owner_change=[int]$raw.owner_change;baseline_denominator_included=$true
            subject_commit=$subjectCommit;subject_tree=$subjectTree;subject_worktree_patch_sha256_or_null=$subjectPatchSha
            producer_base_commit=$subjectCommit;producer_base_tree=$subjectTree;producer_worktree_state=$producerState;producer_overlay_sha256_or_null=$overlaySha
            lua_implementation='Project Zomboid Kahlua';lua_version='Kahlua B41';lua_executable_path=$PzExecutable.Replace('\','/');lua_version_output='Project Zomboid 41.78.20 / Kahlua'
            target_runtime_dialect='project_zomboid_b41_kahlua';execution_environment='project_zomboid_b41_41_78_20';dialect_sensitive=[bool]$raw.dialect_sensitive
            dialect_reasons=@($raw.dialect_reasons);evidence_role='runtime_behavior';stubbed_dependencies=@($raw.stubbed_dependencies);console_log_pointer=$consolePath.Replace('\','/')
        }
        $evidenceRows += $row
    }
    $resolvedOutput = if ([System.IO.Path]::IsPathRooted($OutputPath)) { [System.IO.Path]::GetFullPath($OutputPath) } else { [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath)) }
    $parent = Split-Path -Parent $resolvedOutput
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $jsonl = ($evidenceRows | ForEach-Object { $_ | ConvertTo-Json -Depth 50 -Compress }) -join "`n"
    [System.IO.File]::WriteAllText($resolvedOutput, $jsonl + "`n", $utf8NoBom)
    $evidenceSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedOutput).Hash.ToLowerInvariant()
    $relativeOutput = (Get-RelativePath $RepositoryRoot $resolvedOutput).Replace('\','/')
    $binding = [ordered]@{schema_version=1;evidence_path=$relativeOutput;evidence_sha256=$evidenceSha;evidence_schema_version=1;row_count=$evidenceRows.Count;subject_commit=$subjectCommit;subject_tree=$subjectTree;subject_worktree_patch_sha256_or_null=$subjectPatchSha;producer_base_commit=$subjectCommit;producer_base_tree=$subjectTree;producer_overlay_sha256_or_null=$overlaySha;time_axis=$TimeAxis;execution_environment='project_zomboid_b41_41_78_20'}
    $bindingPath = [System.IO.Path]::ChangeExtension($resolvedOutput, '.binding.json')
    [System.IO.File]::WriteAllText($bindingPath, (($binding | ConvertTo-Json -Depth 20) + "`n"), $utf8NoBom)
    if (@($evidenceRows | Where-Object status -ne 'pass').Count -ne 0) { throw "PZ evidence contains failed rows: $(@($evidenceRows | Where-Object status -ne 'pass').case_id -join ', ')" }
    Write-Output "PZ core refactor harness PASS: rows=$($evidenceRows.Count) evidence=$relativeOutput sha256=$evidenceSha"
}
finally {
    if (Test-Path -LiteralPath $cacheRoot) { Remove-Item -LiteralPath $cacheRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
