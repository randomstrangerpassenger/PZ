[CmdletBinding()]
param([string]$RepositoryRoot)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not $RepositoryRoot) { $RepositoryRoot = (& git rev-parse --show-toplevel 2>&1 | Out-String).Trim() }
$RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\','/')
$packageRoot = [System.IO.Path]::GetFullPath((Join-Path $RepositoryRoot 'Iris/build/package')).TrimEnd('\','/')
$packageScript = Join-Path $RepositoryRoot 'Iris/tools/package_iris.ps1'
$luac = (Get-Command luac -ErrorAction Stop).Source

function Get-TreeIdentity([string]$Root) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return @() }
    $rows = @()
    foreach ($file in Get-ChildItem -LiteralPath $Root -File -Recurse | Sort-Object FullName) {
        $relative = $file.FullName.Substring($Root.TrimEnd('\').Length + 1).Replace('\','/')
        $rows += "$relative`t$($file.Length)`t$((Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant())"
    }
    return $rows
}

$existingBefore = @(Get-TreeIdentity $packageRoot)
$candidateRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('iris-core-refactor-package-' + [guid]::NewGuid().ToString('N'))
$candidateFull = [System.IO.Path]::GetFullPath($candidateRoot).TrimEnd('\','/')
$repoPrefix = $RepositoryRoot + [System.IO.Path]::DirectorySeparatorChar
$packagePrefix = $packageRoot + [System.IO.Path]::DirectorySeparatorChar
if ($candidateFull -eq $RepositoryRoot -or $candidateFull.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or $candidateFull -eq $packageRoot -or $candidateFull.StartsWith($packagePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "candidate package root is not external: $candidateFull"
}
if (Test-Path -LiteralPath $candidateFull) { throw 'candidate root unexpectedly exists' }

try {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $packageScript -OutputRoot $candidateFull -Zip
    if ($LASTEXITCODE -ne 0) { throw "package_iris.ps1 failed: $LASTEXITCODE" }
    $candidateModRoot = Join-Path $candidateFull 'Iris'
    if (-not (Test-Path -LiteralPath $candidateModRoot -PathType Container)) { throw 'candidate Iris root missing' }
    $relativeLayer3Paths = @('IrisLayer3DataChunks.lua') + @(1..11 | ForEach-Object { 'IrisLayer3DataChunks/Chunk{0:D3}.lua' -f $_ })
    foreach ($relative in $relativeLayer3Paths) {
        $live = Join-Path $RepositoryRoot ('Iris/media/lua/client/Iris/Data/' + $relative)
        $candidate = Join-Path $candidateModRoot ('media/lua/client/Iris/Data/' + $relative)
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw "candidate runtime chunk missing: $relative" }
        $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $live).Hash
        $candidateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidate).Hash
        if ($liveHash -ne $candidateHash) { throw "candidate/live runtime identity mismatch: $relative" }
    }
    $detailViewModel = Join-Path $candidateModRoot 'media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua'
    if (-not (Test-Path -LiteralPath $detailViewModel -PathType Leaf)) { throw 'new detail view-model module missing from candidate package' }
    $forbidden = @(
        'media/lua/client/Iris/Data/IrisLayer3Data.lua',
        'build', '_dev', 'staging', 'probe'
    )
    foreach ($relative in $forbidden) {
        if (Test-Path -LiteralPath (Join-Path $candidateModRoot $relative)) { throw "forbidden package payload present: $relative" }
    }
    $luaFiles = @(Get-ChildItem -LiteralPath $candidateModRoot -Filter '*.lua' -File -Recurse)
    if ($luaFiles.Count -eq 0) { throw 'candidate contains no Lua files' }
    foreach ($file in $luaFiles) {
        & $luac -p $file.FullName
        if ($LASTEXITCODE -ne 0) { throw "candidate Lua syntax failed: $($file.FullName)" }
    }
    $existingAfter = @(Get-TreeIdentity $packageRoot)
    if (($existingBefore -join "`0") -cne ($existingAfter -join "`0")) { throw 'existing package peer changed during disposable validation' }
    Write-Output "disposable package PASS: candidate_lua=$($luaFiles.Count) layer3_files=$($relativeLayer3Paths.Count) existing_peer_rows=$($existingBefore.Count)"
}
finally {
    if (Test-Path -LiteralPath $candidateFull) { Remove-Item -LiteralPath $candidateFull -Recurse -Force -ErrorAction SilentlyContinue }
    if (Test-Path -LiteralPath $candidateFull) { throw "candidate cleanup failed: $candidateFull" }
}
