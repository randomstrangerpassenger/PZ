[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OutputPath,
    [string]$RepositoryRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Get-RelativePath([string]$Root, [string]$Path) {
    $rootUri = New-Object System.Uri(([System.IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'))
    $pathUri = New-Object System.Uri([System.IO.Path]::GetFullPath($Path))
    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString())
}

if (-not $RepositoryRoot) {
    $RepositoryRoot = (& git rev-parse --show-toplevel 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'cannot resolve repository root' }
}
$RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\', '/')
$gitRoot = [System.IO.Path]::GetFullPath(((& git -C $RepositoryRoot rev-parse --show-toplevel 2>&1 | Out-String).Trim())).TrimEnd('\', '/')
if (-not $RepositoryRoot.Equals($gitRoot, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'RepositoryRoot identity mismatch' }

$luaCommand = Get-Command lua -ErrorAction Stop
$luaPath = $luaCommand.Source
$luaVersionOutput = (& $luaPath -v 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw 'lua -v failed' }
if ($luaVersionOutput -notmatch 'Lua\s+([0-9.]+)') { throw 'unrecognized Lua version output' }
$luaVersion = $Matches[1]
if ($luaVersion -notlike '5.4.*' -and $luaVersion -notlike '5.1.*') { throw "unsupported standalone Lua version: $luaVersion" }

$subjectCommit = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
$subjectTree = (& git -C $RepositoryRoot rev-parse 'HEAD^{tree}').Trim()
$productionPatch = (& git -C $RepositoryRoot diff --binary -- 'Iris/media/lua/client/Iris' 2>&1 | Out-String)
$sha = [System.Security.Cryptography.SHA256]::Create()
function Get-TextSha([string]$Text) {
    return [System.BitConverter]::ToString($sha.ComputeHash($utf8NoBom.GetBytes($Text))).Replace('-', '').ToLowerInvariant()
}
$subjectPatchSha = if ([string]::IsNullOrEmpty($productionPatch)) { $null } else { Get-TextSha $productionPatch }
$statusLines = @(& git -C $RepositoryRoot status --porcelain=v1 -uall -- Iris)
$overlayRows = @()
foreach ($line in $statusLines) {
    if ($line.Length -lt 4) { continue }
    $path = $line.Substring(3).Replace('\','/')
    $full = Join-Path $RepositoryRoot $path
    $fileSha = if (Test-Path -LiteralPath $full -PathType Leaf) { (Get-FileHash -Algorithm SHA256 -LiteralPath $full).Hash.ToLowerInvariant() } else { $null }
    $overlayRows += "$($line.Substring(0,2))`t$path`t$fileSha"
}
[System.Array]::Sort($overlayRows, [System.StringComparer]::Ordinal)
$overlayText = ($overlayRows -join "`n") + $(if ($overlayRows.Count -gt 0) { "`n" } else { '' })
$overlaySha = if ($overlayRows.Count -eq 0) { $null } else { Get-TextSha $overlayText }
$producerState = if ($overlayRows.Count -eq 0) { 'clean' } elseif (@($statusLines | Where-Object { $_.StartsWith('??') }).Count -gt 0) { 'tracked_and_untracked_overlay' } else { 'tracked_overlay' }

$harnessPath = Join-Path $RepositoryRoot 'Iris/test/lua/pre_refactor_characterization_harness.lua'
$output = @(& $luaPath $harnessPath $RepositoryRoot 2>&1)
$luaExit = $LASTEXITCODE
$rawRows = @($output | Where-Object { $_ -is [string] -and $_.StartsWith("IRIS_CORE_ROW`t") })
if ($rawRows.Count -eq 0) { throw "standalone harness emitted no evidence rows`n$($output -join "`n")" }

$evidenceRows = @()
foreach ($line in $rawRows) {
    $raw = $line.Substring(("IRIS_CORE_ROW`t").Length) | ConvertFrom-Json
    $row = [ordered]@{
        schema_version = 1
        case_id = [string]$raw.case_id
        axis = [string]$raw.axis
        fixture_id = [string]$raw.fixture_id
        status = [string]$raw.status
        expected = $raw.expected
        observed = $raw.observed
        time_axis = 'pre_refactor_characterization'
        owner_change = [int]$raw.owner_change
        baseline_denominator_included = ([string]$raw.axis -ne 'scroll_click_widget')
        subject_commit = $subjectCommit
        subject_tree = $subjectTree
        subject_worktree_patch_sha256_or_null = $subjectPatchSha
        producer_base_commit = $subjectCommit
        producer_base_tree = $subjectTree
        producer_worktree_state = $producerState
        producer_overlay_sha256_or_null = $overlaySha
        lua_implementation = 'PUC-Rio Lua'
        lua_version = $luaVersion
        lua_executable_path = $luaPath.Replace('\','/')
        lua_version_output = $luaVersionOutput
        target_runtime_dialect = 'project_zomboid_b41_kahlua'
        execution_environment = 'auxiliary_standalone_puc_lua_5_4'
        dialect_sensitive = [bool]$raw.dialect_sensitive
        dialect_reasons = @($raw.dialect_reasons)
        evidence_role = 'auxiliary_standalone'
        stubbed_dependencies = @($raw.stubbed_dependencies)
    }
    if ($row.axis -eq 'scroll_click_widget') {
        $row.status = 'unvalidated_but_in_scope'
        $row.baseline_denominator_included = $false
    }
    $evidenceRows += $row
}

$resolvedOutput = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
$outputParent = Split-Path -Parent $resolvedOutput
if (-not (Test-Path -LiteralPath $outputParent)) { New-Item -ItemType Directory -Path $outputParent | Out-Null }
$jsonl = ($evidenceRows | ForEach-Object { $_ | ConvertTo-Json -Depth 50 -Compress }) -join "`n"
[System.IO.File]::WriteAllText($resolvedOutput, $jsonl + "`n", $utf8NoBom)
$evidenceSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedOutput).Hash.ToLowerInvariant()
$relativeOutput = (Get-RelativePath $RepositoryRoot $resolvedOutput).Replace('\','/')
$binding = [ordered]@{
    schema_version = 1
    evidence_path = $relativeOutput
    evidence_sha256 = $evidenceSha
    evidence_schema_version = 1
    row_count = $evidenceRows.Count
    subject_commit = $subjectCommit
    subject_tree = $subjectTree
    subject_worktree_patch_sha256_or_null = $subjectPatchSha
    producer_base_commit = $subjectCommit
    producer_base_tree = $subjectTree
    producer_overlay_sha256_or_null = $overlaySha
    time_axis = 'pre_refactor_characterization'
    execution_environment = 'auxiliary_standalone_puc_lua_5_4'
}
$bindingPath = [System.IO.Path]::ChangeExtension($resolvedOutput, '.binding.json')
[System.IO.File]::WriteAllText($bindingPath, (($binding | ConvertTo-Json -Depth 20) + "`n"), $utf8NoBom)
$sha.Dispose()

if ($luaExit -ne 0 -or @($evidenceRows | Where-Object { $_.baseline_denominator_included -and $_.status -ne 'pass' }).Count -ne 0) {
    throw "standalone characterization failed; lua_exit=$luaExit"
}
Write-Output "pre-refactor characterization PASS: rows=$($evidenceRows.Count) evidence=$relativeOutput sha256=$evidenceSha"
