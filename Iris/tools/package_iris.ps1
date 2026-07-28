[CmdletBinding()]
param(
    [string]$OutputRoot = '',
    [switch]$Clean,
    [switch]$Zip,
    [ValidateSet('', 'candidate', 'canonical_durable')]
    [string]$RegistryCompatibilityContext = '',
    [string]$RegistryCompatibilityPolicy = '',
    [string]$RegistryCompatibilityDisposition = '',
    [string]$RegistryCompatibilityBindingManifest = '',
    [ValidateSet('', 'not_adopted', 'live_gate_adopted')]
    [string]$RegistryCompatibilityRequiredGateState = '',
    [switch]$RegistryCompatibilityProbe,
    [string]$RegistryCompatibilityRequiredManifest = '',
    [string]$RegistryCompatibilityReceipt = ''
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

function Write-Utf8NoBomJson {
    param(
        [Parameter(Mandatory = $true)][object]$Value,
        [Parameter(Mandatory = $true)][string]$Path,
        [int]$Depth = 10
    )
    $parent = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $json = $Value | ConvertTo-Json -Depth $Depth
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, $utf8NoBom)
}

function Invoke-RegistryCompatibilityValidator {
    param(
        [Parameter(Mandatory = $true)][string[]]$ValidatorArguments
    )
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if ($null -eq $uv) {
        throw 'compatibility_blocked_required_dependency: uv executable is missing'
    }
    & $uv.Source run python -B $script:registryCompatibilityValidator @ValidatorArguments
    if ($LASTEXITCODE -ne 0) {
        throw "registry_compatibility_validator_failed: exit=$LASTEXITCODE"
    }
}

function Assert-RegistryCurrentSourceAlignment {
    param(
        [Parameter(Mandatory = $true)][string]$RequiredManifest,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [switch]$IsolatedCandidateProbe
    )
    if (-not (Test-Path -LiteralPath $RequiredManifest -PathType Leaf)) {
        throw 'compatibility_policy_context_required: required-validation manifest is missing'
    }
    $payload = Get-Content -LiteralPath $RequiredManifest -Raw -Encoding UTF8 | ConvertFrom-Json
    $selection = $payload.registry_runtime_compatibility
    $alignment = $selection.current_source_alignment
    if ($null -eq $alignment -or $alignment.state -ne 'stale_requires_successor_rtc') {
        return
    }
    if ($IsolatedCandidateProbe) {
        if ($alignment.isolated_successor_candidate_probe_allowed -ne $true) {
            throw 'registry_runtime_compatibility_current_source_stale'
        }
        return
    }
    if (
        $alignment.applies_when_current_facts_path -ne 'Iris/build/description/v2/data/dvf_3_3_facts.jsonl' -or
        [string]::IsNullOrWhiteSpace($alignment.applies_when_current_facts_sha256)
    ) {
        throw 'registry_runtime_compatibility_current_source_alignment_invalid'
    }
    $currentFacts = Get-FullPath (Join-Path $RepositoryRoot $alignment.applies_when_current_facts_path)
    if (-not (Test-Path -LiteralPath $currentFacts -PathType Leaf)) {
        throw 'registry_runtime_compatibility_current_source_alignment_invalid'
    }
    $currentFactsSha256 = (Get-FileHash -LiteralPath $currentFacts -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($currentFactsSha256 -eq $alignment.applies_when_current_facts_sha256) {
        throw 'registry_runtime_compatibility_current_source_stale'
    }
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
$registryCompatibilityValidator = Join-Path $repoRoot 'Iris\build\description\v2\tools\build\validate_dvf_3_3_registry_runtime_compatibility.py'
$defaultRequiredManifest = Join-Path $repoRoot 'Iris\_docs\round3\current_route_required_validations.json'
$registryCompatibilityResolutionMode = 'explicit'

$compatibilityValues = @(
    $RegistryCompatibilityContext,
    $RegistryCompatibilityPolicy,
    $RegistryCompatibilityDisposition,
    $RegistryCompatibilityBindingManifest,
    $RegistryCompatibilityRequiredGateState
)
$explicitCompatibilityCount = @($compatibilityValues | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
if ($explicitCompatibilityCount -ne 0 -and $explicitCompatibilityCount -ne $compatibilityValues.Count) {
    throw 'partial_registry_compatibility_arguments_forbidden'
}

if ($explicitCompatibilityCount -eq 0) {
    $selectedRequiredManifest = if ([string]::IsNullOrWhiteSpace($RegistryCompatibilityRequiredManifest)) {
        $defaultRequiredManifest
    } else {
        Get-FullPath $RegistryCompatibilityRequiredManifest
    }
    if (-not (Test-Path -LiteralPath $selectedRequiredManifest -PathType Leaf)) {
        throw 'compatibility_policy_context_required: required-validation manifest is missing'
    }
    $requiredPayload = Get-Content -LiteralPath $selectedRequiredManifest -Raw -Encoding UTF8 | ConvertFrom-Json
    $selection = $requiredPayload.registry_runtime_compatibility
    if ($null -eq $selection -or $selection.policy_lifecycle_state -ne 'live_required_gate_adopted') {
        throw 'compatibility_policy_context_required: no live-gate-adopted Registry Runtime Compatibility selection'
    }
    $bundleRoot = Get-FullPath (Join-Path $repoRoot $selection.bundle_root)
    $RegistryCompatibilityContext = 'canonical_durable'
    $RegistryCompatibilityPolicy = Join-Path $bundleRoot 'registry_runtime_compatibility_policy.json'
    $RegistryCompatibilityDisposition = Join-Path $bundleRoot 'current_collision_disposition.json'
    $RegistryCompatibilityBindingManifest = Join-Path $bundleRoot 'candidate_contract_binding_manifest.json'
    $RegistryCompatibilityRequiredGateState = 'live_gate_adopted'
    $RegistryCompatibilityRequiredManifest = $selectedRequiredManifest
    $registryCompatibilityResolutionMode = 'post_adoption_live_manifest_default'
} else {
    $RegistryCompatibilityPolicy = Get-FullPath $RegistryCompatibilityPolicy
    $RegistryCompatibilityDisposition = Get-FullPath $RegistryCompatibilityDisposition
    $RegistryCompatibilityBindingManifest = Get-FullPath $RegistryCompatibilityBindingManifest
    if (-not [string]::IsNullOrWhiteSpace($RegistryCompatibilityRequiredManifest)) {
        $RegistryCompatibilityRequiredManifest = Get-FullPath $RegistryCompatibilityRequiredManifest
    }
}

$alignmentManifest = if ([string]::IsNullOrWhiteSpace($RegistryCompatibilityRequiredManifest)) {
    $defaultRequiredManifest
} else {
    $RegistryCompatibilityRequiredManifest
}
Assert-RegistryCurrentSourceAlignment `
    -RequiredManifest $alignmentManifest `
    -RepositoryRoot $repoRoot `
    -IsolatedCandidateProbe:($RegistryCompatibilityContext -eq 'candidate')

if ($RegistryCompatibilityContext -eq 'candidate') {
    if (-not $RegistryCompatibilityProbe) {
        throw 'candidate_package_requires_registry_compatibility_probe'
    }
    if ($RegistryCompatibilityRequiredGateState -ne 'not_adopted') {
        throw 'candidate_package_gate_state_invalid'
    }
    if ($Zip) {
        throw 'candidate_package_zip_forbidden'
    }
    $normalizedOutput = $outputRootFull.Replace('\', '/').ToLowerInvariant()
    if (-not $normalizedOutput.Contains('/staging/dvf_3_3_registry_runtime_compatibility/attempts/')) {
        throw 'candidate_package_output_outside_attempt_root'
    }
}
if ($RegistryCompatibilityContext -eq 'canonical_durable' -and $RegistryCompatibilityRequiredGateState -eq 'not_adopted') {
    if (-not $RegistryCompatibilityProbe -or $Zip) {
        throw 'package_guard_active_not_required_gate_adopted'
    }
}
if ($RegistryCompatibilityRequiredGateState -eq 'live_gate_adopted') {
    if ([string]::IsNullOrWhiteSpace($RegistryCompatibilityRequiredManifest)) {
        throw 'live_gate_required_manifest_missing'
    }
}
if (-not (Test-Path -LiteralPath $registryCompatibilityValidator -PathType Leaf)) {
    throw "compatibility_blocked_required_dependency: validator is missing: $registryCompatibilityValidator"
}

$requiredGateReceiptPath = ''
if ($RegistryCompatibilityRequiredGateState -eq 'live_gate_adopted') {
    $requiredGateReceiptPath = if ([string]::IsNullOrWhiteSpace($RegistryCompatibilityReceipt)) {
        Join-Path $outputRootFull 'registry_compatibility_required_gate_receipt.json'
    } else {
        (Get-FullPath $RegistryCompatibilityReceipt) + '.required.json'
    }
    Invoke-RegistryCompatibilityValidator -ValidatorArguments @(
        '--required-gate',
        '--required-manifest', $RegistryCompatibilityRequiredManifest,
        '--out', $requiredGateReceiptPath
    )
}

$contractReceiptPath = if ([string]::IsNullOrWhiteSpace($RegistryCompatibilityReceipt)) {
    Join-Path $outputRootFull 'registry_compatibility_contract_receipt.json'
} else {
    (Get-FullPath $RegistryCompatibilityReceipt) + '.contract.json'
}
Invoke-RegistryCompatibilityValidator -ValidatorArguments @(
    '--contract-only',
    '--policy-context', $RegistryCompatibilityContext,
    '--policy', $RegistryCompatibilityPolicy,
    '--disposition', $RegistryCompatibilityDisposition,
    '--binding-manifest', $RegistryCompatibilityBindingManifest,
    '--out', $contractReceiptPath
)

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

$v2Root = Join-Path $sourceRoot 'build\description\v2'
$sourceRuntimeData = Join-Path $sourceRoot 'media\lua\client\Iris\Data'
$packageRuntimeData = Join-Path $packageRoot 'media\lua\client\Iris\Data'
$factsPath = Join-Path $v2Root 'data\dvf_3_3_facts.jsonl'
$decisionsPath = Join-Path $v2Root 'data\dvf_3_3_decisions.jsonl'
$overlayPath = Join-Path $v2Root 'data\dvf_3_3_overlay_support.jsonl'
$renderedPath = Join-Path $v2Root 'output\dvf_3_3_rendered.json'
$runtimeManifestPath = Join-Path $sourceRuntimeData 'IrisLayer3DataChunks.lua'
$runtimeChunksPath = Join-Path $sourceRuntimeData 'IrisLayer3DataChunks'
$packageRuntimeManifestPath = Join-Path $packageRuntimeData 'IrisLayer3DataChunks.lua'
$packageRuntimeChunksPath = Join-Path $packageRuntimeData 'IrisLayer3DataChunks'
$surfaceInputPath = Join-Path $outputRootFull 'registry_compatibility_surface_inputs.json'
$resolvedCompatibilityReceipt = if ([string]::IsNullOrWhiteSpace($RegistryCompatibilityReceipt)) {
    Join-Path $outputRootFull 'registry_compatibility_receipt.json'
} else {
    Get-FullPath $RegistryCompatibilityReceipt
}

$surfaceInputs = [ordered]@{
    schema_version = 'rtc-compatibility-surface-input-v1'
    round_id = 'dvf_3_3_registry_runtime_compatibility'
    producer_attempt_id = $null
    resolution_mode = $registryCompatibilityResolutionMode
    binding_manifest_sha256 = (Get-FileHash -LiteralPath $RegistryCompatibilityBindingManifest -Algorithm SHA256).Hash.ToLowerInvariant()
    source = [ordered]@{
        facts = (Get-FullPath $factsPath)
        facts_sha256 = (Get-FileHash -LiteralPath $factsPath -Algorithm SHA256).Hash.ToLowerInvariant()
        decisions = (Get-FullPath $decisionsPath)
        decisions_sha256 = (Get-FileHash -LiteralPath $decisionsPath -Algorithm SHA256).Hash.ToLowerInvariant()
        overlay = (Get-FullPath $overlayPath)
        overlay_sha256 = (Get-FileHash -LiteralPath $overlayPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    rendered = [ordered]@{
        path = (Get-FullPath $renderedPath)
        path_sha256 = (Get-FileHash -LiteralPath $renderedPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    runtime = [ordered]@{
        manifest = (Get-FullPath $runtimeManifestPath)
        manifest_sha256 = (Get-FileHash -LiteralPath $runtimeManifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
        chunks = (Get-FullPath $runtimeChunksPath)
    }
    package = [ordered]@{
        manifest = (Get-FullPath $packageRuntimeManifestPath)
        manifest_sha256 = (Get-FileHash -LiteralPath $packageRuntimeManifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
        chunks = (Get-FullPath $packageRuntimeChunksPath)
    }
}
Write-Utf8NoBomJson -Value $surfaceInputs -Path $surfaceInputPath -Depth 8
Invoke-RegistryCompatibilityValidator -ValidatorArguments @(
    '--surface-validation',
    '--surface-input-manifest', $surfaceInputPath,
    '--policy-context', $RegistryCompatibilityContext,
    '--policy', $RegistryCompatibilityPolicy,
    '--disposition', $RegistryCompatibilityDisposition,
    '--binding-manifest', $RegistryCompatibilityBindingManifest,
    '--out', $resolvedCompatibilityReceipt
)
$compatibilityResult = Get-Content -LiteralPath $resolvedCompatibilityReceipt -Raw -Encoding UTF8 | ConvertFrom-Json
if ($compatibilityResult.status -ne 'PASS') {
    throw "registry_compatibility_package_guard_failed: $resolvedCompatibilityReceipt"
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
    registry_compatibility = [ordered]@{
        policy_context = $RegistryCompatibilityContext
        required_gate_state = $RegistryCompatibilityRequiredGateState
        resolution_mode = $registryCompatibilityResolutionMode
        probe = [bool]$RegistryCompatibilityProbe
        binding_manifest_sha256 = (Get-FileHash -LiteralPath $RegistryCompatibilityBindingManifest -Algorithm SHA256).Hash.ToLowerInvariant()
        contract_receipt = $contractReceiptPath
        required_gate_receipt = $requiredGateReceiptPath
        surface_input_manifest = $surfaceInputPath
        guard_receipt = $resolvedCompatibilityReceipt
        guard_receipt_sha256 = (Get-FileHash -LiteralPath $resolvedCompatibilityReceipt -Algorithm SHA256).Hash.ToLowerInvariant()
        status = $compatibilityResult.status
    }
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
