[CmdletBinding()]
param(
    [string]$OutputRoot = '',
    [switch]$Clean,
    [switch]$Zip
)

$ErrorActionPreference = 'Stop'
$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $scriptRoot '..\build\package'
}

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

function Convert-IrisNormalizedPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    $normalized = $Path.Replace('\', '/')
    if ($normalized.StartsWith('./')) {
        $normalized = $normalized.Substring(2)
    }
    return $normalized.ToLowerInvariant()
}

function Test-IrisDvfBridgeForbiddenPayload {
    param([Parameter(Mandatory = $true)][string]$Path)

    $staleDvfBridgeSha256 = 'c5ec93914f4a13c227bf1b3958908b860af768113700cecb4c4496b46ad411aa'
    $hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -eq $staleDvfBridgeSha256) {
        return 'exact_sha256'
    }

    $content = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    $requiredMarkers = @(
        'interaction-cluster-rendered-v0',
        'Base.CanOpener',
        'Base.ElectronicsScrap',
        'Base.GunpowderCan',
        'Base.ModKit',
        'Base.Tongs',
        'Base.WeldingTorch'
    )

    foreach ($marker in $requiredMarkers) {
        if (-not $content.Contains($marker)) {
            return ''
        }
    }
    if ($content -notmatch '\["total"\]\s*=\s*6') {
        return ''
    }
    if ($content -notmatch '\["active_composed"\]\s*=\s*6') {
        return ''
    }

    return 'legacy_6_entry_payload_shape'
}

function Assert-NoForbiddenIrisDvfBridgeSurface {
    param(
        [Parameter(Mandatory = $true)][string]$SearchRoot,
        [Parameter(Mandatory = $true)][string]$RelativeRoot,
        [Parameter(Mandatory = $true)][string]$SurfaceName
    )

    if (-not (Test-Path -LiteralPath $SearchRoot)) {
        return
    }

    $relativeRootFull = Get-FullPath $RelativeRoot
    $forbiddenRelativePaths = @(
        (Convert-IrisNormalizedPath -Path 'media/lua/shared/Iris/IrisDvfBridgeData.lua'),
        (Convert-IrisNormalizedPath -Path 'Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua')
    )
    $violations = @()

    Get-ChildItem -LiteralPath $SearchRoot -Recurse -File -Filter '*.lua' | ForEach-Object {
        $relativePath = Get-RelativePackagePath -Root $relativeRootFull -Path $_.FullName
        $normalizedRelativePath = Convert-IrisNormalizedPath -Path $relativePath
        $reasons = @()

        if ($_.Name -ieq 'IrisDvfBridgeData.lua') {
            $reasons += 'forbidden_filename'
        }
        if ($forbiddenRelativePaths -contains $normalizedRelativePath) {
            $reasons += 'forbidden_current_like_path'
        }

        $payloadReason = Test-IrisDvfBridgeForbiddenPayload -Path $_.FullName
        if (-not [string]::IsNullOrWhiteSpace($payloadReason)) {
            $reasons += $payloadReason
        }

        if ($reasons.Count -gt 0) {
            $violations += ('{0} [{1}]' -f $relativePath, ($reasons -join ','))
        }
    }

    if ($violations.Count -gt 0) {
        throw "Forbidden stale Iris DVF bridge artifact detected in ${SurfaceName}: $($violations -join '; ')"
    }
}

$sourceRoot = Get-FullPath (Join-Path $scriptRoot '..')
$repoRoot = Get-FullPath (Join-Path $sourceRoot '..')
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

$layer3MonolithRelativePath = 'media\lua\client\Iris\Data\IrisLayer3Data.lua'
$sourceLayer3MonolithPath = Join-Path $sourceRoot $layer3MonolithRelativePath
if (Test-Path -LiteralPath $sourceLayer3MonolithPath) {
    throw "Forbidden Iris Layer 3 monolith source file detected: $sourceLayer3MonolithPath. Use chunk manifest + chunk files instead."
}

Assert-NoForbiddenIrisDvfBridgeSurface -SearchRoot (Join-Path $repoRoot 'media') -RelativeRoot $repoRoot -SurfaceName 'repository root media'
Assert-NoForbiddenIrisDvfBridgeSurface -SearchRoot (Join-Path $sourceRoot 'media') -RelativeRoot $sourceRoot -SurfaceName 'Iris source media'

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

$forbiddenPackageFiles = @(
    $layer3MonolithRelativePath,
    'media\lua\shared\Iris\IrisDvfBridgeData.lua'
)

foreach ($relativeFile in $forbiddenPackageFiles) {
    $candidate = Join-Path $packageRoot $relativeFile
    if (Test-Path -LiteralPath $candidate) {
        if ($relativeFile -eq $layer3MonolithRelativePath) {
            throw "Forbidden Iris package monolith output detected: $candidate"
        }
        throw "Forbidden stale Iris DVF bridge package output detected: $candidate"
    }
}

Assert-NoForbiddenIrisDvfBridgeSurface -SearchRoot $packageRoot -RelativeRoot $packageRoot -SurfaceName 'Iris package output'

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
    forbidden_files = $forbiddenPackageFiles
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
