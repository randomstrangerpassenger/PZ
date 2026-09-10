Set-StrictMode -Version Latest

function Get-IrisTooltipOwner {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$DataRoot)
    if (Test-Path -LiteralPath (Join-Path $DataRoot 'IrisTooltip.lock')) { throw 'tooltip_install_in_progress' }
    $path = Join-Path $DataRoot 'IrisTooltipOwner.json'
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    if ((Get-Item -LiteralPath $path).Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw 'tooltip_owner_reparse' }
    $owner = [System.IO.File]::ReadAllText($path) | ConvertFrom-Json
    $identity = $owner.identity_json | ConvertFrom-Json
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = ([System.BitConverter]::ToString($algorithm.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($owner.identity_json)))).Replace('-', '').ToLowerInvariant()
    } finally { $algorithm.Dispose() }
    $names = @('IrisTooltipStaticData.lua', 'IrisTooltipRecipeVariants.lua')
    if ($owner.schema_version -cne 'iris-tooltip-product-v1' -or $owner.owner -cne 'Tooltip' -or $owner.product_id -cnotmatch '^ttp-[0-9a-f]{64}$') { throw 'tooltip_owner_identity_invalid' }
    if ($owner.product_id -cne ('ttp-' + $digest)) { throw 'tooltip_owner_identity_hash_mismatch' }
    if (@(Compare-Object $names @($owner.files.PSObject.Properties.Name) -CaseSensitive).Count -ne 0) { throw 'tooltip_owner_members_invalid' }
    if ($identity.t1_input.s2_supply_sha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'tooltip_supply_binding_missing' }
    foreach ($name in $names) {
        $member = Join-Path $DataRoot $name
        if ((Get-Item -LiteralPath $member).Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw 'tooltip_member_reparse' }
        $sha = (Get-FileHash -LiteralPath $member -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($sha -cne $owner.files.$name -or $sha -cne $identity.files.$name) { throw "tooltip_member_hash_mismatch: $name" }
        $sourceName = 'Iris/media/lua/client/Iris/Data/' + $name
        if ($owner.predecessor_facades.$name -cne $identity.sources.$sourceName) { throw 'tooltip_predecessor_identity_mismatch' }
    }
    return $owner
}

function Get-IrisProductDescriptor {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$DataRoot)
    $pointerPath = Join-Path $DataRoot 'IrisLayer3ProductCurrent.lua'
    $pointer = [System.IO.File]::ReadAllText($pointerPath)
    $idMatch = [regex]::Matches($pointer, 'product_id = "(l3p-[0-9a-f]{64})"')
    if ($idMatch.Count -ne 1) { throw 'product_pointer_identity_invalid' }
    $id = $idMatch[0].Groups[1].Value
    $expectedPointer = "return {`n    schema_version = `"iris_layer3_product_pointer_v1`",`n    product_id = `"$id`",`n    descriptor_module = `"Iris/Data/IrisLayer3ProductGenerations/$id/Descriptor`",`n}`n"
    if ($pointer -cne $expectedPointer) { throw 'product_pointer_shape_invalid' }
    $root = Join-Path (Join-Path $DataRoot 'IrisLayer3ProductGenerations') $id
    foreach ($path in @($DataRoot, (Split-Path $root -Parent), $root)) {
        if ((Get-Item -LiteralPath $path).Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            throw 'product_reparse_path'
        }
    }
    $descriptorPath = Join-Path $root 'product_descriptor.json'
    $descriptor = [System.IO.File]::ReadAllText($descriptorPath) | ConvertFrom-Json
    if ($descriptor.schema_version -cne 'iris-layer3-product-v1' -or $descriptor.product_id -cne $id) {
        throw 'product_descriptor_identity_mismatch'
    }
    $expected = @('Descriptor.lua', 'Index.lua', 'Tooltip.lua', 'Recipe.lua') + @(1..11 | ForEach-Object { 'Chunks/Chunk{0:D3}.lua' -f $_ })
    $names = @($descriptor.members.PSObject.Properties.Name)
    if (@(Compare-Object $expected $names -CaseSensitive).Count -ne 0) { throw 'product_member_set_invalid' }
    foreach ($name in $expected) {
        $path = Join-Path $root $name
        if ((Get-Item -LiteralPath $path).Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw 'product_reparse_member' }
        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -cne $descriptor.members.$name) { throw "product_member_hash_mismatch: $name" }
    }
    $actual = @(Get-ChildItem -LiteralPath $root -Recurse -File | ForEach-Object { $_.FullName.Substring($root.Length + 1).Replace('\', '/') })
    if (@(Compare-Object ($expected + @('product_descriptor.json')) $actual -CaseSensitive).Count -ne 0) {
        throw 'product_member_inventory_mismatch'
    }
    $facades = @('IrisLayer3ProductCurrent.lua', 'IrisLayer3DataCurrent.lua', 'IrisLayer3DataChunkIndex.lua', 'IrisLayer3DataChunks.lua', 'IrisTooltipStaticData.lua', 'IrisTooltipRecipeVariants.lua')
    if (@(Compare-Object $facades @($descriptor.facades.PSObject.Properties.Name) -CaseSensitive).Count -ne 0) { throw 'product_facade_set_invalid' }
    $tooltip = Get-IrisTooltipOwner -DataRoot $DataRoot
    foreach ($name in $facades) {
        if ($null -ne $tooltip -and $name -cin @('IrisTooltipStaticData.lua', 'IrisTooltipRecipeVariants.lua')) {
            if ($tooltip.predecessor_facades.$name -cne $descriptor.facades.$name) { throw 'tooltip_predecessor_binding_mismatch' }
            continue
        }
        if ((Get-FileHash -LiteralPath (Join-Path $DataRoot $name) -Algorithm SHA256).Hash.ToLowerInvariant() -cne $descriptor.facades.$name) {
            throw "product_facade_hash_mismatch: $name"
        }
    }
    return [pscustomobject]@{ product_id = $id; root = $root; path = $descriptorPath; descriptor = $descriptor }
}

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
    $null = Get-IrisTooltipOwner -DataRoot $dataRootFull
    if (Test-Path -LiteralPath (Join-Path $dataRootFull 'IrisLayer3ProductCurrent.lua')) {
        $product = Get-IrisProductDescriptor -DataRoot $dataRootFull
        if ($ExpectedGenerationId -and $product.product_id -cne $ExpectedGenerationId) { throw 'product_expected_identity_mismatch' }
        $roots = @(Get-ChildItem -LiteralPath (Join-Path $dataRootFull 'IrisLayer3ProductGenerations') -Directory)
        if ($roots.Count -ne 1 -or $roots[0].Name -cne $product.product_id) { throw 'product_generation_count_invalid' }
        foreach ($legacy in @('IrisLayer3Generations', 'IrisLayer3DataChunks', 'Layer3English')) {
            if (Test-Path -LiteralPath (Join-Path $dataRootFull $legacy)) { throw "product_legacy_payload_present: $legacy" }
        }
        return [pscustomobject]@{ status = 'PASS'; generation_id = $product.product_id; generation_count = 1; legacy_fixed_chunks_present = $false; descriptor_path = $product.path }
    }
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
    'Get-IrisTooltipOwner',
    'Get-IrisProductDescriptor',
    'Get-IrisLayer3PointerGenerationId',
    'Assert-IrisLayer3PackageProjection'
)
