[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Baseline', 'Acceptance')]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Get-FileHash {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$LiteralPath,
        [ValidateSet('SHA256')][string]$Algorithm = 'SHA256'
    )

    $hasher = [System.Security.Cryptography.SHA256]::Create()
    $stream = $null
    try {
        $stream = [System.IO.File]::OpenRead($LiteralPath)
        $hash = $hasher.ComputeHash($stream)
        return [pscustomobject]@{ Algorithm = $Algorithm; Hash = ([System.BitConverter]::ToString($hash)).Replace('-', '').ToLowerInvariant(); Path = $LiteralPath }
    }
    finally {
        if ($null -ne $stream) { $stream.Dispose() }
        $hasher.Dispose()
    }
}

function Get-TextSha256([string]$Text) {
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [System.BitConverter]::ToString(
            $algorithm.ComputeHash($Utf8NoBom.GetBytes($Text))
        ).Replace('-', '').ToLowerInvariant()
    }
    finally { $algorithm.Dispose() }
}

function Get-RelativePath([string]$Root, [string]$Path) {
    $rootUri = New-Object System.Uri(([System.IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'))
    $pathUri = New-Object System.Uri([System.IO.Path]::GetFullPath($Path))
    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString()).Replace('\','/')
}

$RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\','/')
$GitRoot = (& git -C $RepositoryRoot rev-parse --show-toplevel 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or -not $RepositoryRoot.Equals(
    [System.IO.Path]::GetFullPath($GitRoot).TrimEnd('\','/'),
    [System.StringComparison]::OrdinalIgnoreCase
)) { throw 'RepositoryRoot identity mismatch' }

$LuaCommand = Get-Command lua -ErrorAction Stop
$LuaPath = $LuaCommand.Source
$LuaVersion = (& $LuaPath -v 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw 'lua -v failed' }
$SubjectCommit = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
$SubjectTree = (& git -C $RepositoryRoot rev-parse 'HEAD^{tree}').Trim()
$Scope = @(
    'Iris/media/lua/client/Iris',
    'Iris/test/lua/residual_refactor_acceptance_harness.lua',
    'Iris/test/run_residual_refactor_acceptance.ps1'
)
$PreviousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    $Patch = (& git -C $RepositoryRoot diff --binary -- @Scope 2>$null | Out-String)
}
finally {
    $ErrorActionPreference = $PreviousErrorActionPreference
}
if ($LASTEXITCODE -ne 0) { throw 'git diff failed while binding subject overlay' }
$StatusLines = @(& git -C $RepositoryRoot status --porcelain=v1 -uall -- @Scope)
if ($LASTEXITCODE -ne 0) { throw 'git status failed while binding subject overlay' }
$OverlayRows = @()
foreach ($StatusLine in $StatusLines) {
    if ($StatusLine.Length -lt 4) { continue }
    $StatusPath = $StatusLine.Substring(3).Replace('\','/')
    $StatusFullPath = Join-Path $RepositoryRoot $StatusPath
    $StatusHash = if (Test-Path -LiteralPath $StatusFullPath -PathType Leaf) {
        (Get-FileHash -Algorithm SHA256 -LiteralPath $StatusFullPath).Hash.ToLowerInvariant()
    } else { $null }
    $OverlayRows += "$($StatusLine.Substring(0,2))`t$StatusPath`t$StatusHash"
}
[System.Array]::Sort($OverlayRows, [System.StringComparer]::Ordinal)
$OverlayMaterial = $Patch + $(if ($OverlayRows.Count -gt 0) { ($OverlayRows -join "`n") + "`n" } else { '' })
$PatchSha = if ([string]::IsNullOrEmpty($OverlayMaterial)) { $null } else { Get-TextSha256 $OverlayMaterial }

$Harness = Join-Path $RepositoryRoot 'Iris/test/lua/residual_refactor_acceptance_harness.lua'
$RawOutput = @(& $LuaPath $Harness $RepositoryRoot $Mode 2>&1)
$LuaExit = $LASTEXITCODE
$Rows = @()
foreach ($Line in $RawOutput) {
    if ($Line -is [string] -and $Line.StartsWith("IRIS_RESIDUAL_ROW`t")) {
        $Raw = $Line.Substring(("IRIS_RESIDUAL_ROW`t").Length) | ConvertFrom-Json
        $Rows += [ordered]@{
            schema_version = 'iris-residual-runtime-row-v1'
            case_id = [string]$Raw.case_id
            axis = [string]$Raw.axis
            mode = $Mode
            status = [string]$Raw.status
            expected = $Raw.expected
            observed = $Raw.observed
            subject_commit = $SubjectCommit
            subject_tree = $SubjectTree
            subject_overlay_sha256_or_null = $PatchSha
            lua_executable = $LuaPath.Replace('\','/')
            lua_version = $LuaVersion
            evidence_role = 'current'
        }
    }
}
if ($Rows.Count -eq 0) { throw "residual harness emitted no rows`n$($RawOutput -join "`n")" }

$ResolvedOutput = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
    [System.IO.Path]::GetFullPath($OutputPath)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $RepositoryRoot $OutputPath))
}
$OutputParent = Split-Path -Parent $ResolvedOutput
if (-not (Test-Path -LiteralPath $OutputParent)) {
    New-Item -ItemType Directory -Path $OutputParent -Force | Out-Null
}
$Jsonl = ($Rows | ForEach-Object { $_ | ConvertTo-Json -Depth 30 -Compress }) -join "`n"
[System.IO.File]::WriteAllText($ResolvedOutput, $Jsonl + "`n", $Utf8NoBom)
$EvidenceSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ResolvedOutput).Hash.ToLowerInvariant()
$RelativeOutput = Get-RelativePath $RepositoryRoot $ResolvedOutput
$Binding = [ordered]@{
    schema_version = 'iris-residual-runtime-binding-v1'
    validation_status = if ($LuaExit -eq 0 -and @($Rows | Where-Object status -ne 'pass').Count -eq 0) { 'passed' } else { 'failed' }
    evidence_path = $RelativeOutput
    evidence_sha256 = $EvidenceSha
    row_count = $Rows.Count
    mode = $Mode
    subject_commit = $SubjectCommit
    subject_tree = $SubjectTree
    subject_overlay_sha256_or_null = $PatchSha
    producer_overlay_rows = $OverlayRows
    command = @($LuaPath.Replace('\','/'), $Harness.Replace('\','/'), $RepositoryRoot.Replace('\','/'), $Mode)
    lua_version = $LuaVersion
}
$BindingPath = [System.IO.Path]::ChangeExtension($ResolvedOutput, '.binding.json')
[System.IO.File]::WriteAllText($BindingPath, ($Binding | ConvertTo-Json -Depth 30) + "`n", $Utf8NoBom)
$BindingRelative = Get-RelativePath $RepositoryRoot $BindingPath
$BindingSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $BindingPath).Hash.ToLowerInvariant()
$EvidenceManifest = [ordered]@{
    schema_version = 'iris-residual-evidence-role-v1'
    role = 'current'
    created_at = [DateTime]::UtcNow.ToString('o')
    producer = 'Iris/test/run_residual_refactor_acceptance.ps1'
    producer_readpoint = 'iris-residual-refactor-plan-change-1'
    command = @('powershell','-ExecutionPolicy','Bypass','-File','Iris/test/run_residual_refactor_acceptance.ps1','-Mode',$Mode)
    subject = [ordered]@{commit=$SubjectCommit;tree=$SubjectTree;overlay_sha256_or_null=$PatchSha}
    inputs = @()
    outputs = @(
        [ordered]@{path=$RelativeOutput;sha256=$EvidenceSha;exists=$true},
        [ordered]@{path=$BindingRelative;sha256=$BindingSha;exists=$true}
    )
    mutable = $false
    supersedes = @()
    authority_claim = $false
}
$ManifestPath = $ResolvedOutput + '.evidence.json'
[System.IO.File]::WriteAllText($ManifestPath, ($EvidenceManifest | ConvertTo-Json -Depth 30) + "`n", $Utf8NoBom)

if ($Binding.validation_status -ne 'passed') {
    throw "residual runtime harness failed; lua_exit=$LuaExit"
}
Write-Output "residual runtime $Mode PASS: rows=$($Rows.Count) evidence=$RelativeOutput sha256=$EvidenceSha"
