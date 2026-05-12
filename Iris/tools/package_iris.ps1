[CmdletBinding()]
param(
    [string]$OutputRoot = (Join-Path $PSScriptRoot '..\build\package'),
    [switch]$Clean,
    [switch]$Zip
)

$ErrorActionPreference = 'Stop'

function Get-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Get-RelativePackagePath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $prefix = $Root.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $prefix = $prefix + [System.IO.Path]::DirectorySeparatorChar
    return $Path.Substring($prefix.Length).Replace('\', '/')
}

$sourceRoot = Get-FullPath (Join-Path $PSScriptRoot '..')
$outputRootFull = Get-FullPath $OutputRoot
$packageRoot = Join-Path $outputRootFull 'Iris'
$manifestPath = Join-Path $outputRootFull 'Iris.package_manifest.sha256.json'
$zipPath = Join-Path $outputRootFull 'Iris.zip'

$requiredPaths = @(
    (Join-Path $sourceRoot 'mod.info'),
    (Join-Path $sourceRoot 'media')
)

foreach ($path in $requiredPaths) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required Iris package input is missing: $path"
    }
}

if (Test-Path -LiteralPath $packageRoot) {
    if (-not $Clean) {
        throw "Package output already exists: $packageRoot. Re-run with -Clean to replace generated output."
    }
    Remove-Item -LiteralPath $packageRoot -Recurse -Force
}

if ($Clean) {
    foreach ($generatedFile in @($manifestPath, $zipPath)) {
        if (Test-Path -LiteralPath $generatedFile) {
            Remove-Item -LiteralPath $generatedFile -Force
        }
    }
}

New-Item -ItemType Directory -Path $packageRoot -Force | Out-Null

Copy-Item -LiteralPath (Join-Path $sourceRoot 'mod.info') -Destination $packageRoot -Force

$poster = Join-Path $sourceRoot 'poster.png'
if (Test-Path -LiteralPath $poster) {
    Copy-Item -LiteralPath $poster -Destination $packageRoot -Force
}

Copy-Item -LiteralPath (Join-Path $sourceRoot 'media') -Destination $packageRoot -Recurse -Force

$excludedPackageFiles = @(
    'media\lua\client\Iris\Data\IrisLayer3Data.lua'
)

foreach ($relativeFile in $excludedPackageFiles) {
    $candidate = Join-Path $packageRoot $relativeFile
    if (Test-Path -LiteralPath $candidate) {
        Remove-Item -LiteralPath $candidate -Force
    }
}

$excludedRootNames = @(
    '_archive',
    '_docs',
    'build',
    'evidence',
    'input',
    'output',
    'test',
    'lua',
    'Iris'
)

$violations = @()
foreach ($name in $excludedRootNames) {
    $candidate = Join-Path $packageRoot $name
    if (Test-Path -LiteralPath $candidate) {
        $violations += $candidate
    }
}

if ($violations.Count -gt 0) {
    throw "Forbidden Iris package path(s) were included: $($violations -join ', ')"
}

$packageRootFull = Get-FullPath $packageRoot
$files = Get-ChildItem -LiteralPath $packageRootFull -Recurse -File |
    Sort-Object FullName |
    ForEach-Object {
        [pscustomobject]@{
            path = Get-RelativePackagePath -Root $packageRootFull -Path $_.FullName
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            bytes = $_.Length
        }
    }

$manifest = [pscustomobject]@{
    schema_version = 'iris-package-manifest-v1'
    source_root = $sourceRoot
    package_root = $packageRootFull
    copied_roots = @('mod.info', 'poster.png if present', 'media/')
    excluded_roots = $excludedRootNames
    excluded_files = $excludedPackageFiles
    file_count = @($files).Count
    files = $files
}

New-Item -ItemType Directory -Path $outputRootFull -Force | Out-Null
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

if ($Zip) {
    if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
        Compress-Archive -LiteralPath $packageRootFull -DestinationPath $zipPath -Force
    } else {
        throw 'Compress-Archive is not available in this PowerShell environment.'
    }
}

Write-Host "Iris package staged: $packageRootFull"
Write-Host "Manifest written: $manifestPath"
if ($Zip) {
    Write-Host "Zip written: $zipPath"
}
