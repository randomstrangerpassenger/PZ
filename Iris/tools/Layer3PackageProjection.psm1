Set-StrictMode -Version Latest

function Get-IrisLayer3PointerGenerationId {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$PointerPath)

    if (-not (Test-Path -LiteralPath $PointerPath -PathType Leaf)) {
        throw "layer3_package_pointer_missing: $PointerPath"
    }
    $text = [System.IO.File]::ReadAllText($PointerPath, [System.Text.Encoding]::UTF8)
    if ($text -notmatch 'schema_version\s*=\s*"iris_layer3_generation_pointer_v1"') {
        throw 'layer3_package_pointer_schema_invalid'
    }
    $matches = [regex]::Matches(
        $text,
        'generation_id\s*=\s*"(?<generation>dvf33-[0-9a-f]{64})"'
    )
    if ($matches.Count -ne 1) {
        throw 'layer3_package_pointer_generation_invalid'
    }
    $generationId = $matches[0].Groups['generation'].Value
    $generationReferences = @(
        [regex]::Matches($text, 'dvf33-[0-9a-f]{64}') |
            ForEach-Object { $_.Value } |
            Sort-Object -Unique
    )
    if ($generationReferences.Count -ne 1 -or $generationReferences[0] -cne $generationId) {
        throw 'layer3_package_pointer_reference_mismatch'
    }
    return $generationId
}

function Assert-IrisLayer3PackageProjection {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$DataRoot,
        [string]$ExpectedGenerationId = ''
    )

    $dataRootFull = [System.IO.Path]::GetFullPath($DataRoot)
    $pointerPath = Join-Path $dataRootFull 'IrisLayer3DataCurrent.lua'
    $pointerGenerationId = Get-IrisLayer3PointerGenerationId -PointerPath $pointerPath
    if (
        -not [string]::IsNullOrWhiteSpace($ExpectedGenerationId) -and
        $pointerGenerationId -cne $ExpectedGenerationId
    ) {
        throw "layer3_package_pointer_expected_generation_mismatch: $pointerGenerationId"
    }

    $legacyChunkRoot = Join-Path $dataRootFull 'IrisLayer3DataChunks'
    if (Test-Path -LiteralPath $legacyChunkRoot) {
        throw "layer3_package_legacy_fixed_chunks_present: $legacyChunkRoot"
    }

    $generationsRoot = Join-Path $dataRootFull 'IrisLayer3Generations'
    if (-not (Test-Path -LiteralPath $generationsRoot -PathType Container)) {
        throw "layer3_package_generations_root_missing: $generationsRoot"
    }
    $generationDirectories = @(
        Get-ChildItem -LiteralPath $generationsRoot -Directory |
            Sort-Object Name
    )
    if ($generationDirectories.Count -ne 1) {
        throw "layer3_package_generation_count_invalid: $($generationDirectories.Count)"
    }
    if ($generationDirectories[0].Name -cne $pointerGenerationId) {
        throw (
            'layer3_package_generation_pointer_mismatch: ' +
            $generationDirectories[0].Name + ' != ' + $pointerGenerationId
        )
    }

    $descriptorPath = Join-Path $generationDirectories[0].FullName 'generation_descriptor.json'
    if (-not (Test-Path -LiteralPath $descriptorPath -PathType Leaf)) {
        throw "layer3_package_descriptor_missing: $descriptorPath"
    }
    $descriptor = Get-Content -LiteralPath $descriptorPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (
        $descriptor.schema_version -ne 'dvf-3-3-complete-generation-v1' -or
        $descriptor.generation_id -cne $pointerGenerationId -or
        $descriptor.claims.authority_effect -ne 'none'
    ) {
        throw 'layer3_package_descriptor_identity_mismatch'
    }

    return [pscustomobject]@{
        status = 'PASS'
        generation_id = $pointerGenerationId
        generation_count = $generationDirectories.Count
        legacy_fixed_chunks_present = $false
        descriptor_path = $descriptorPath
    }
}

Export-ModuleMember -Function @(
    'Get-IrisLayer3PointerGenerationId',
    'Assert-IrisLayer3PackageProjection'
)
