[CmdletBinding()]
param(
    [string]$OutputRoot = '',
    [switch]$Clean,
    [switch]$Zip,
    [ValidateSet('', 'current_runtime_payload', 'rtc_certified_payload')]
    [string]$PackageApplicability = '',
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
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    throw 'runtime_package_explicit_output_root_required'
}
$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
Import-Module -Name (Join-Path $scriptRoot 'RuntimeLookupIndexIdentity.psm1') -Force

function Get-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Test-SameOrNestedPath {
    param(
        [Parameter(Mandatory = $true)][string]$Candidate,
        [Parameter(Mandatory = $true)][string]$Root
    )
    $candidateFull = (Get-FullPath $Candidate).TrimEnd('\', '/')
    $rootFull = (Get-FullPath $Root).TrimEnd('\', '/')
    return (
        $candidateFull.Equals($rootFull, [System.StringComparison]::OrdinalIgnoreCase) -or
        $candidateFull.StartsWith(
            $rootFull + [System.IO.Path]::DirectorySeparatorChar,
            [System.StringComparison]::OrdinalIgnoreCase
        )
    )
}

function Assert-ExternalPackageOutputRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Candidate,
        [Parameter(Mandatory = $true)][string[]]$ProtectedRoots
    )
    $candidateFull = (Get-FullPath $Candidate).TrimEnd('\', '/')
    $cursor = [System.IO.DirectoryInfo]::new($candidateFull)
    while ($null -ne $cursor) {
        if ($cursor.Exists -and (($cursor.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "runtime_package_output_root_reparse_component: $($cursor.FullName)"
        }
        $cursor = $cursor.Parent
    }
    $existing = Get-Item -Force -LiteralPath $candidateFull -ErrorAction SilentlyContinue
    if ($null -ne $existing -and -not $existing.PSIsContainer) {
        throw "runtime_package_output_root_not_directory: $candidateFull"
    }
    foreach ($protected in $ProtectedRoots) {
        if ((Test-SameOrNestedPath -Candidate $candidateFull -Root $protected) -or
            (Test-SameOrNestedPath -Candidate $protected -Root $candidateFull)) {
            throw "runtime_package_output_root_must_be_external: $candidateFull <-> $protected"
        }
    }
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

function Get-DecodedUtf8EolSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)

    $utf8 = New-Object System.Text.UTF8Encoding($false, $true)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $text = $utf8.GetString($bytes)
    $normalized = $text.Replace("`r`n", "`n").Replace("`r", "`n")
    $normalizedBytes = $utf8.GetBytes($normalized)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha256.ComputeHash($normalizedBytes)
    } finally {
        $sha256.Dispose()
    }
    return ([System.BitConverter]::ToString($hash)).Replace('-', '').ToLowerInvariant()
}

function Get-RuntimePayloadIdentity {
    param(
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$SourceRoot,
        [string]$PackageRoot = ''
    )
    $descriptorPath = Join-Path $RepositoryRoot 'Iris\_docs\round3\validated_naturalization_current_runtime_adoption\current_generation_descriptor.json'
    if (-not (Test-Path -LiteralPath $descriptorPath -PathType Leaf)) {
        throw 'runtime_payload_generation_descriptor_missing'
    }
    $descriptor = Get-Content -LiteralPath $descriptorPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (
        $descriptor.schema_version -ne 'validated-naturalization-materialized-generation-v1' -or
        $descriptor.authority_effect -ne 'current_runtime_adoption' -or
        [string]::IsNullOrWhiteSpace($descriptor.transaction_id)
    ) {
        throw 'runtime_payload_generation_descriptor_invalid'
    }
    $renderedPath = Join-Path $SourceRoot 'build\description\v2\output\dvf_3_3_rendered.json'
    $manifestPath = Join-Path $SourceRoot 'media\lua\client\Iris\Data\IrisLayer3DataChunks.lua'
    $chunksRoot = Join-Path $SourceRoot 'media\lua\client\Iris\Data\IrisLayer3DataChunks'
    $supportRelativePaths = @(
        'IrisLayer3DataChunkIndex.lua',
        'IrisLayer3DataLookup.lua',
        'UseCaseDescriptions/ChunkIndex.lua',
        'UseCaseDescriptions/LineCountIndex.lua',
        'IrisUseCaseDescriptionsLookup.lua',
        'IrisRuntimeLookupDiagnostics.lua',
        'IrisUseCaseDescriptions.lua',
        'UseCaseDescriptions/RequirementsLookup.lua'
    )
    $supportPaths = @($supportRelativePaths | ForEach-Object {
        Join-Path (Join-Path $SourceRoot 'media\lua\client\Iris\Data') $_
    })
    $candidatePath = Join-Path $RepositoryRoot $descriptor.candidate.path
    $factsPath = Join-Path $SourceRoot 'build\description\v2\data\dvf_3_3_facts.jsonl'
    $inputManifestPath = Join-Path $SourceRoot 'build\description\v2\data\dvf_3_3_input_manifest.json'
    foreach ($requiredPath in (@($renderedPath, $manifestPath, $chunksRoot, $candidatePath, $factsPath, $inputManifestPath) + $supportPaths)) {
        if (-not (Test-Path -LiteralPath $requiredPath)) {
            throw "runtime_payload_required_input_missing: $requiredPath"
        }
    }
    $liveDataRoot = Join-Path $SourceRoot 'media\lua\client\Iris\Data'
    Assert-RuntimeLookupIndexIdentity -DataRoot $liveDataRoot -IndexName 'IrisLayer3DataChunkIndex.lua'
    Assert-RuntimeLookupIndexIdentity -DataRoot $liveDataRoot -IndexName 'UseCaseDescriptions/ChunkIndex.lua'
    Assert-RuntimeLookupIndexIdentity -DataRoot $liveDataRoot -IndexName 'UseCaseDescriptions/LineCountIndex.lua'
    $renderedSha = Get-DecodedUtf8EolSha256 -Path $renderedPath
    $manifestSha = Get-DecodedUtf8EolSha256 -Path $manifestPath
    if ($renderedSha -ne $descriptor.rendered.sha256) { throw 'runtime_payload_rendered_freshness_failed' }
    if ($manifestSha -ne $descriptor.runtime_manifest.sha256) { throw 'runtime_payload_manifest_freshness_failed' }
    if ((Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $descriptor.candidate.sha256) { throw 'runtime_payload_candidate_freshness_failed' }
    if ((Get-FileHash -LiteralPath $factsPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $descriptor.source_pair.facts_sha256) { throw 'runtime_payload_facts_freshness_failed' }
    if ((Get-FileHash -LiteralPath $inputManifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $descriptor.source_pair.input_manifest_sha256) { throw 'runtime_payload_input_manifest_freshness_failed' }
    $declaredChunks = @($descriptor.ordered_chunks)
    $expectedChunkNames = @()
    foreach ($declared in $declaredChunks) {
        $normalizedPath = ([string]$declared.path).Replace('\', '/')
        $prefix = 'IrisLayer3DataChunks/'
        if (-not $normalizedPath.StartsWith($prefix, [System.StringComparison]::Ordinal)) {
            throw 'runtime_payload_chunk_descriptor_path_invalid'
        }
        $relativeName = $normalizedPath.Substring($prefix.Length)
        if (
            [string]::IsNullOrWhiteSpace($relativeName) -or
            $relativeName.Contains('/') -or
            $expectedChunkNames -ccontains $relativeName
        ) {
            throw 'runtime_payload_chunk_descriptor_path_invalid'
        }
        $expectedChunkNames += $relativeName
    }
    $chunkEntries = @(Get-ChildItem -LiteralPath $chunksRoot -Force)
    $unexpectedChunkEntries = @(
        $chunkEntries | Where-Object {
            $_.PSIsContainer -or -not ($expectedChunkNames -ccontains $_.Name)
        }
    )
    $actualChunks = @($chunkEntries | Where-Object { -not $_.PSIsContainer } | Sort-Object Name)
    if (
        $declaredChunks.Count -ne 11 -or
        $actualChunks.Count -ne 11 -or
        $unexpectedChunkEntries.Count -ne 0
    ) {
        throw 'runtime_payload_chunk_surface_mismatch'
    }
    $chunkRows = @()
    for ($index = 0; $index -lt $declaredChunks.Count; $index++) {
        $declared = $declaredChunks[$index]
        $expectedName = [System.IO.Path]::GetFileName($declared.path)
        $actual = $actualChunks[$index]
        if ($actual.Name -ne $expectedName) { throw 'runtime_payload_chunk_set_mismatch' }
        $actualSha = Get-DecodedUtf8EolSha256 -Path $actual.FullName
        if ($actualSha -ne $declared.sha256) { throw "runtime_payload_chunk_freshness_failed: $($actual.Name)" }
        $chunkRows += [ordered]@{ path = $declared.path; sha256 = $actualSha }
    }
    $result = [ordered]@{
        status = 'PASS'
        applicability = 'current_runtime_payload'
        transaction_id = $descriptor.transaction_id
        generation_descriptor_path = (Get-FullPath $descriptorPath)
        generation_descriptor_sha256 = Get-DecodedUtf8EolSha256 -Path $descriptorPath
        rendered_sha256 = $renderedSha
        manifest_sha256 = $manifestSha
        chunk_count = $chunkRows.Count
        chunks = $chunkRows
        support_files = @($supportRelativePaths | ForEach-Object {
            $supportPath = Join-Path (Join-Path $SourceRoot 'media\lua\client\Iris\Data') $_
            [ordered]@{
                path = $_
                sha256 = (Get-FileHash -LiteralPath $supportPath -Algorithm SHA256).Hash.ToLowerInvariant()
            }
        })
    }
    if (-not [string]::IsNullOrWhiteSpace($PackageRoot)) {
        $packageData = Join-Path $PackageRoot 'media\lua\client\Iris\Data'
        $packageManifest = Join-Path $packageData 'IrisLayer3DataChunks.lua'
        $packageChunks = Join-Path $packageData 'IrisLayer3DataChunks'
        Assert-RuntimeLookupIndexIdentity -DataRoot $packageData -IndexName 'IrisLayer3DataChunkIndex.lua'
        Assert-RuntimeLookupIndexIdentity -DataRoot $packageData -IndexName 'UseCaseDescriptions/ChunkIndex.lua'
        Assert-RuntimeLookupIndexIdentity -DataRoot $packageData -IndexName 'UseCaseDescriptions/LineCountIndex.lua'
        $liveNames = @('IrisLayer3DataChunks.lua') + @($chunkRows | ForEach-Object { $_.path }) + $supportRelativePaths
        $packageChunkEntries = @(Get-ChildItem -LiteralPath $packageChunks -Force)
        $unexpectedPackageChunkEntries = @(
            $packageChunkEntries | Where-Object {
                $_.PSIsContainer -or -not ($expectedChunkNames -ccontains $_.Name)
            }
        )
        if ($unexpectedPackageChunkEntries.Count -ne 0) {
            throw 'runtime_payload_package_chunk_surface_mismatch'
        }
        $packageChunkFiles = @(
            $packageChunkEntries |
                Where-Object { -not $_.PSIsContainer } |
                Sort-Object Name
        )
        $packageNames = @('IrisLayer3DataChunks.lua') + @($packageChunkFiles | ForEach-Object { 'IrisLayer3DataChunks/' + $_.Name }) + $supportRelativePaths
        $mismatchCount = 0
        foreach ($relative in $liveNames) {
            $livePath = Join-Path (Join-Path $SourceRoot 'media\lua\client\Iris\Data') $relative
            $packagePath = Join-Path $packageData $relative
            if (-not (Test-Path -LiteralPath $packagePath) -or (Get-FileHash -LiteralPath $livePath -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $packagePath -Algorithm SHA256).Hash) {
                $mismatchCount++
            }
        }
        $liveOnly = @($liveNames | Where-Object { $_ -notin $packageNames })
        $packageOnly = @($packageNames | Where-Object { $_ -notin $liveNames })
        $forbidden = @(
            (Join-Path $packageData 'IrisLayer3Data.lua'),
            (Join-Path $PackageRoot 'media\lua\shared\Iris\IrisDvfBridgeData.lua')
        ) | Where-Object { Test-Path -LiteralPath $_ }
        $result.bidirectional_file_set_equal = $liveOnly.Count -eq 0 -and $packageOnly.Count -eq 0
        $result.hash_mismatch_count = $mismatchCount
        $result.forbidden_file_count = @($forbidden).Count
        if (-not $result.bidirectional_file_set_equal -or $mismatchCount -ne 0 -or $result.forbidden_file_count -ne 0) {
            throw 'runtime_payload_package_identity_failed'
        }
    }
    return $result
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
Assert-ExternalPackageOutputRoot -Candidate $outputRootFull -ProtectedRoots @($repoRoot, $sourceRoot)
$packageRoot = Join-Path $outputRootFull 'Iris'
$manifestPath = Join-Path $outputRootFull 'Iris.package_manifest.sha256.json'
$zipPath = Join-Path $outputRootFull 'Iris.zip'
$registryCompatibilityValidator = Join-Path $repoRoot 'Iris\build\description\v2\tools\build\validate_dvf_3_3_registry_runtime_compatibility.py'
$defaultRequiredManifest = Join-Path $repoRoot 'Iris\_docs\round3\current_route_required_validations.json'
$registryCompatibilityResolutionMode = 'explicit'
$rtcArguments = @(
    $RegistryCompatibilityContext,
    $RegistryCompatibilityPolicy,
    $RegistryCompatibilityDisposition,
    $RegistryCompatibilityBindingManifest,
    $RegistryCompatibilityRequiredGateState
)
$rtcArgumentCount = @($rtcArguments | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
$anyRtcInput = $rtcArgumentCount -gt 0 -or $RegistryCompatibilityProbe -or -not [string]::IsNullOrWhiteSpace($RegistryCompatibilityRequiredManifest) -or -not [string]::IsNullOrWhiteSpace($RegistryCompatibilityReceipt)
$resolvedPackageApplicability = if ([string]::IsNullOrWhiteSpace($PackageApplicability)) {
    if ($anyRtcInput) { 'rtc_certified_payload' } else { 'current_runtime_payload' }
} else {
    $PackageApplicability
}
if ($resolvedPackageApplicability -eq 'current_runtime_payload' -and $anyRtcInput) {
    throw 'package_applicability_mixed_or_ambiguous'
}
if ($resolvedPackageApplicability -eq 'rtc_certified_payload' -and $rtcArgumentCount -ne $rtcArguments.Count) {
    throw 'rtc_package_requires_complete_compatibility_inputs'
}
$registryCompatibilityApplicable = $resolvedPackageApplicability -eq 'rtc_certified_payload'
$runtimePayloadPreflight = $null
if (-not $registryCompatibilityApplicable) {
    $runtimePayloadPreflight = Get-RuntimePayloadIdentity -RepositoryRoot $repoRoot -SourceRoot $sourceRoot
}

$compatibilityValues = @(
    $RegistryCompatibilityContext,
    $RegistryCompatibilityPolicy,
    $RegistryCompatibilityDisposition,
    $RegistryCompatibilityBindingManifest,
    $RegistryCompatibilityRequiredGateState
)
$explicitCompatibilityCount = @($compatibilityValues | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
if ($registryCompatibilityApplicable) {
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
}

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

if ($registryCompatibilityApplicable) {
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
} else {
    $runtimePayloadIdentity = Get-RuntimePayloadIdentity -RepositoryRoot $repoRoot -SourceRoot $sourceRoot -PackageRoot $packageRoot
    $runtimePayloadReceipt = Join-Path $outputRootFull 'runtime_payload_package_identity.json'
    Write-Utf8NoBomJson -Value $runtimePayloadIdentity -Path $runtimePayloadReceipt -Depth 8
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

$packageApplicabilityRecord = if ($registryCompatibilityApplicable) {
    [ordered]@{
        applicability = $resolvedPackageApplicability
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
} else {
    [ordered]@{
        applicability = $resolvedPackageApplicability
        runtime_payload_identity_receipt = $runtimePayloadReceipt
        runtime_payload_identity_receipt_sha256 = (Get-FileHash -LiteralPath $runtimePayloadReceipt -Algorithm SHA256).Hash.ToLowerInvariant()
        status = $runtimePayloadIdentity.status
    }
}
$manifest = [pscustomobject]@{
    schema_version = 'iris-package-manifest-v1'
    source_root = $sourceRoot
    package_root = $packageRootFull
    copied_roots = @('mod.info', 'poster.png if present', 'media/')
    excluded_roots = $excludedRootNames
    forbidden_files = $forbiddenPackageFiles
    applicability = $packageApplicabilityRecord
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
