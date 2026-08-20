function Get-NormalizedUtf8EolSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    $strictUtf8 = [System.Text.UTF8Encoding]::new($false, $true)
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    $text = $strictUtf8.GetString([System.IO.File]::ReadAllBytes($Path))
    $normalized = $text.Replace("`r`n", "`n").Replace("`r", "`n")
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $algorithm.ComputeHash($utf8NoBom.GetBytes($normalized))
        return ([System.BitConverter]::ToString($digest)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $algorithm.Dispose()
    }
}

function Get-UseCaseActualLineCounts {
    param([Parameter(Mandatory = $true)][string]$DataRoot)
    $counts = [System.Collections.Generic.Dictionary[string, int]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($chunkNumber in 1..9) {
        $relative = 'UseCaseDescriptions\Chunk{0:D3}.lua' -f $chunkNumber
        $targetPath = Join-Path $DataRoot $relative
        if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) {
            throw "runtime_payload_lookup_index_target_missing: UseCaseDescriptions/LineCountIndex.lua -> $relative"
        }
        $currentKey = $null
        $inLines = $false
        $currentLineCount = 0
        foreach ($line in (Get-Content -LiteralPath $targetPath)) {
            if ($line -match '^chunk\["([^"]+)"\] = \{$') {
                $currentKey = [string]$Matches[1]
                $inLines = $false
                $currentLineCount = 0
            }
            elseif ($null -ne $currentKey -and $line -ceq '    lines = {') {
                $inLines = $true
            }
            elseif ($inLines -and $line -ceq '    },') {
                if ($counts.ContainsKey($currentKey)) {
                    throw "runtime_payload_lookup_index_line_counts_invalid: duplicate chunk key $currentKey"
                }
                $counts.Add($currentKey, $currentLineCount)
                $currentKey = $null
                $inLines = $false
            }
            elseif ($inLines -and $line -match '^        \{') {
                $currentLineCount += 1
            }
        }
    }
    return $counts
}

function Get-Layer3GenerationPointerData {
    param([Parameter(Mandatory = $true)][string]$DataRoot)

    $pointerPath = Join-Path $DataRoot 'IrisLayer3DataCurrent.lua'
    if (-not (Test-Path -LiteralPath $pointerPath -PathType Leaf)) {
        # Offline mutation fixtures predate the product pointer and intentionally
        # materialize only the protected index/chunk surface. Product packaging
        # still requires the pointer before this validation helper is invoked.
        $legacyIndexPath = Join-Path $DataRoot 'IrisLayer3DataChunkIndex.lua'
        $legacyChunkRoot = Join-Path $DataRoot 'IrisLayer3DataChunks'
        if (
            -not (Test-Path -LiteralPath $legacyIndexPath -PathType Leaf) -or
            -not (Test-Path -LiteralPath $legacyChunkRoot -PathType Container)
        ) {
            throw 'runtime_payload_lookup_index_missing: IrisLayer3DataChunkIndex.lua'
        }
        return [pscustomobject]@{
            generation_id = 'offline-legacy-fixture'
            index_module = 'Iris/Data/IrisLayer3DataChunkIndex'
            index_path = $legacyIndexPath
            chunk_root = $legacyChunkRoot
            chunk_module_prefix = 'Iris/Data/IrisLayer3DataChunks/Chunk'
        }
    }
    $pointerText = Get-Content -LiteralPath $pointerPath -Raw -Encoding UTF8
    $generationMatch = [regex]::Match(
        $pointerText,
        'generation_id = "(?<generation>dvf33-[0-9a-f]{64})"'
    )
    $indexMatch = [regex]::Match(
        $pointerText,
        'index_module = "(?<module>Iris/Data/IrisLayer3Generations/(?<generation>dvf33-[0-9a-f]{64})/IrisLayer3DataChunkIndex)"'
    )
    if (
        -not $generationMatch.Success -or
        -not $indexMatch.Success -or
        $generationMatch.Groups['generation'].Value -cne $indexMatch.Groups['generation'].Value
    ) {
        throw 'runtime_payload_layer3_generation_pointer_invalid'
    }
    $generationId = [string]$generationMatch.Groups['generation'].Value
    $indexModule = [string]$indexMatch.Groups['module'].Value
    $generationRoot = Join-Path (Join-Path $DataRoot 'IrisLayer3Generations') $generationId
    $indexPath = Join-Path $generationRoot 'IrisLayer3DataChunkIndex.lua'
    $chunkRoot = Join-Path $generationRoot 'Chunks'
    if (
        -not (Test-Path -LiteralPath $indexPath -PathType Leaf) -or
        -not (Test-Path -LiteralPath $chunkRoot -PathType Container)
    ) {
        throw 'runtime_payload_layer3_generation_pointer_target_missing'
    }
    return [pscustomobject]@{
        generation_id = $generationId
        index_module = $indexModule
        index_path = $indexPath
        chunk_root = $chunkRoot
        chunk_module_prefix = "Iris/Data/IrisLayer3Generations/$generationId/Chunks/Chunk"
    }
}

function Get-RuntimeLookupActualKeys {
    param(
        [Parameter(Mandatory = $true)][string]$DataRoot,
        [Parameter(Mandatory = $true)][ValidateSet('layer3', 'usecase')][string]$Kind
    )
    $root = if ($Kind -ceq 'layer3') {
        (Get-Layer3GenerationPointerData -DataRoot $DataRoot).chunk_root
    }
    else {
        Join-Path $DataRoot 'UseCaseDescriptions'
    }
    $pattern = if ($Kind -ceq 'layer3') {
        '(?m)^    \["([^"]+)"\]\s*='
    }
    else {
        '(?m)^chunk\["([^"]+)"\]\s*='
    }
    $keys = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($path in @(Get-ChildItem -LiteralPath $root -File -Filter 'Chunk???.lua' | Sort-Object Name)) {
        $text = Get-Content -LiteralPath $path.FullName -Raw
        foreach ($match in [regex]::Matches($text, $pattern)) {
            $key = [string]$match.Groups[1].Value
            if (-not $keys.Add($key)) {
                throw "runtime_payload_lookup_package_duplicate_key: $Kind -> $key"
            }
        }
    }
    return $keys
}

function Get-Utf8StringSha256 {
    param([Parameter(Mandatory = $true)][string]$Value)
    $utf8 = [System.Text.UTF8Encoding]::new($false)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $algorithm.ComputeHash($utf8.GetBytes($Value))
        return ([System.BitConverter]::ToString($digest)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $algorithm.Dispose()
    }
}

function Assert-RuntimeLookupIndexIdentity {
    param(
        [Parameter(Mandatory = $true)][string]$DataRoot,
        [Parameter(Mandatory = $true)][string]$IndexName
    )
    $isLayer3 = $IndexName -ceq 'IrisLayer3DataChunkIndex.lua'
    $layer3Surface = if ($isLayer3) {
        Get-Layer3GenerationPointerData -DataRoot $DataRoot
    }
    else {
        $null
    }
    $indexPath = if ($isLayer3) {
        $layer3Surface.index_path
    }
    else {
        Join-Path $DataRoot $IndexName
    }
    if (-not (Test-Path -LiteralPath $indexPath -PathType Leaf)) {
        throw "runtime_payload_lookup_index_missing: $indexPath"
    }
    $strictUtf8 = [System.Text.UTF8Encoding]::new($false, $true)
    $indexText = $strictUtf8.GetString([System.IO.File]::ReadAllBytes($indexPath))
    $indexText = $indexText.Replace("`r`n", "`n").Replace("`r", "`n")

    $isUseCaseChunk = $IndexName -ceq 'UseCaseDescriptions/ChunkIndex.lua'
    $isUseCaseLineCount = $IndexName -ceq 'UseCaseDescriptions/LineCountIndex.lua'
    if (-not ($isLayer3 -or $isUseCaseChunk -or $isUseCaseLineCount)) {
        throw "runtime_payload_lookup_index_shape_invalid: $IndexName"
    }

    if ($isUseCaseLineCount) {
        $expectedSchema = 'iris_usecase_line_count_index_v1'
        $expectedEntryCount = 1631
        $entryCountMatch = [regex]::Match($indexText, 'entry_count = (?<count>\d+),')
        $lineCountPattern = '(?m)^        \["([^"]+)"\] = (\d+),$'
        $declaredLineCounts = @([regex]::Matches($indexText, $lineCountPattern))
        if (
            $indexText -notmatch ('schema_version = "' + $expectedSchema + '",') -or
            -not $entryCountMatch.Success -or
            [int]$entryCountMatch.Groups['count'].Value -ne $expectedEntryCount -or
            $declaredLineCounts.Count -ne $expectedEntryCount
        ) {
            throw "runtime_payload_lookup_index_shape_invalid: $IndexName"
        }
        $actualLineCounts = Get-UseCaseActualLineCounts -DataRoot $DataRoot
        if ($actualLineCounts.Count -ne $expectedEntryCount) {
            throw "runtime_payload_lookup_index_line_counts_invalid: $IndexName"
        }
        $declaredKeys = [System.Collections.Generic.HashSet[string]]::new(
            [System.StringComparer]::Ordinal
        )
        $previousKey = $null
        foreach ($match in $declaredLineCounts) {
            $key = [string]$match.Groups[1].Value
            $declaredCount = [int]$match.Groups[2].Value
            if (
                ($null -ne $previousKey -and [string]::CompareOrdinal($previousKey, $key) -ge 0) -or
                -not $declaredKeys.Add($key) -or
                -not $actualLineCounts.ContainsKey($key) -or
                $actualLineCounts[$key] -ne $declaredCount
            ) {
                throw "runtime_payload_lookup_index_line_counts_invalid: $IndexName -> $key"
            }
            $previousKey = $key
        }
        foreach ($key in $actualLineCounts.Keys) {
            if (-not $declaredKeys.Contains($key)) {
                throw "runtime_payload_lookup_index_line_counts_invalid: $IndexName -> $key"
            }
        }
        $canonicalLines = [System.Collections.Generic.List[string]]::new()
        $canonicalLines.Add('-- Auto-generated by convert_descriptions_to_lua.py')
        $canonicalLines.Add('-- Line-count routing metadata only; IrisUseCaseDescriptions remains the public facade.')
        $canonicalLines.Add('return {')
        $canonicalLines.Add(('    schema_version = "' + $expectedSchema + '",'))
        $canonicalLines.Add(('    entry_count = ' + $expectedEntryCount + ','))
        $canonicalLines.Add('    lineCounts = {')
        foreach ($match in $declaredLineCounts) {
            $canonicalLines.Add(
                '        ["' + [string]$match.Groups[1].Value + '"] = ' +
                [string]$match.Groups[2].Value + ','
            )
        }
        $canonicalLines.Add('    },')
        $canonicalLines.Add('}')
        $canonicalText = [string]::Join("`n", $canonicalLines) + "`n"
        if ($indexText -cne $canonicalText) {
            throw "runtime_payload_lookup_index_shape_invalid: $IndexName"
        }
        return
    }

    $expectedSchema = if ($isLayer3) {
        'iris_layer3_chunk_range_index_v1'
    }
    else {
        'iris_usecase_chunk_range_index_v1'
    }
    $expectedEntryCount = if ($isLayer3) { 2105 } else { 1631 }
    $expectedRowCount = if ($isLayer3) { 11 } else { 9 }
    $expectedModulePrefix = if ($isLayer3) {
        $layer3Surface.chunk_module_prefix
    }
    else {
        'Iris/Data/UseCaseDescriptions/Chunk'
    }
    if ($indexText -notmatch ('schema_version = "' + [regex]::Escape($expectedSchema) + '",')) {
        throw "runtime_payload_lookup_index_shape_invalid: $IndexName"
    }
    $rowPattern = '\{ count = (?<count>\d+), first = "(?<first>[^"]+)", last = "(?<last>[^"]+)", module = "(?<module>[^"]+)", sha256 = "(?<sha256>[0-9a-f]{64})" \},'
    $rows = @([regex]::Matches($indexText, $rowPattern))
    $entryCountMatch = [regex]::Match($indexText, 'entry_count = (?<count>\d+),')
    if ($rows.Count -ne $expectedRowCount -or -not $entryCountMatch.Success) {
        throw "runtime_payload_lookup_index_shape_invalid: $IndexName"
    }
    $rowEntryTotal = 0
    $seenModules = @{}
    $previousLast = $null
    $rowNumber = 0
    foreach ($row in $rows) {
        $rowNumber += 1
        $moduleName = [string]$row.Groups['module'].Value
        $expectedModuleName = $expectedModulePrefix + ('{0:D3}' -f $rowNumber)
        $rowEntryTotal += [int]$row.Groups['count'].Value
        if ($moduleName -cne $expectedModuleName -or $seenModules.ContainsKey($moduleName)) {
            throw "runtime_payload_lookup_index_module_invalid: $IndexName"
        }
        $first = [string]$row.Groups['first'].Value
        $last = [string]$row.Groups['last'].Value
        if (
            [string]::CompareOrdinal($first, $last) -gt 0 -or
            ($null -ne $previousLast -and [string]::CompareOrdinal($previousLast, $first) -ge 0)
        ) {
            throw "runtime_payload_lookup_index_range_invalid: $IndexName"
        }
        $previousLast = $last
        $seenModules[$moduleName] = $true
        $relative = $moduleName.Substring('Iris/Data/'.Length).Replace('/', '\') + '.lua'
        $targetPath = Join-Path $DataRoot $relative
        if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) {
            throw "runtime_payload_lookup_index_target_missing: $IndexName -> $relative"
        }
        if ((Get-NormalizedUtf8EolSha256 -Path $targetPath) -cne [string]$row.Groups['sha256'].Value) {
            throw "runtime_payload_lookup_index_hash_mismatch: $IndexName -> $relative"
        }
        $chunkText = Get-Content -Raw -LiteralPath $targetPath
        $keyPattern = if ($isLayer3) {
            '(?m)^    \["([^"]+)"\]\s*='
        }
        else {
            '(?m)^chunk\["([^"]+)"\]\s*='
        }
        $keys = @([regex]::Matches($chunkText, $keyPattern) | ForEach-Object {
            [string]$_.Groups[1].Value
        })
        if (
            $keys.Count -ne [int]$row.Groups['count'].Value -or
            $keys[0] -cne $first -or
            $keys[$keys.Count - 1] -cne $last
        ) {
            throw "runtime_payload_lookup_index_range_invalid: $IndexName -> $relative"
        }
    }
    if (
        $rowEntryTotal -ne [int]$entryCountMatch.Groups['count'].Value -or
        $rowEntryTotal -ne $expectedEntryCount
    ) {
        throw "runtime_payload_lookup_index_shape_invalid: $IndexName"
    }
    $canonicalLines = [System.Collections.Generic.List[string]]::new()
    if ($isLayer3) {
        $canonicalLines.Add('-- Auto-generated by export_dvf_3_3_lua_bridge.py.')
        $canonicalLines.Add('-- Routing metadata only; IrisLayer3DataChunks remains the public facade.')
    }
    else {
        $canonicalLines.Add('-- Auto-generated by convert_descriptions_to_lua.py')
        $canonicalLines.Add('-- Routing metadata only; IrisUseCaseDescriptions remains the public facade.')
    }
    $canonicalLines.Add('-- sha256 hashes strict UTF-8 text after CRLF/CR -> LF normalization.')
    $canonicalLines.Add('return {')
    $canonicalLines.Add(('    schema_version = "' + $expectedSchema + '",'))
    $canonicalLines.Add(('    entry_count = ' + $expectedEntryCount + ','))
    $canonicalLines.Add('    chunks = {')
    foreach ($row in $rows) {
        $canonicalLines.Add(
            '        { count = ' + [string]$row.Groups['count'].Value +
            ', first = "' + [string]$row.Groups['first'].Value +
            '", last = "' + [string]$row.Groups['last'].Value +
            '", module = "' + [string]$row.Groups['module'].Value +
            '", sha256 = "' + [string]$row.Groups['sha256'].Value + '" },'
        )
    }
    $canonicalLines.Add('    },')
    $canonicalLines.Add('}')
    $canonicalText = [string]::Join("`n", $canonicalLines) + "`n"
    if ($indexText -cne $canonicalText) {
        throw "runtime_payload_lookup_index_shape_invalid: $IndexName"
    }
}

function Assert-RuntimeLookupPackageParity {
    param(
        [Parameter(Mandatory = $true)][string]$DataRoot,
        [switch]$SkipManifestCheck
    )

    Assert-RuntimeLookupIndexIdentity -DataRoot $DataRoot -IndexName 'IrisLayer3DataChunkIndex.lua'
    Assert-RuntimeLookupIndexIdentity -DataRoot $DataRoot -IndexName 'UseCaseDescriptions/ChunkIndex.lua'
    Assert-RuntimeLookupIndexIdentity -DataRoot $DataRoot -IndexName 'UseCaseDescriptions/LineCountIndex.lua'

    $layer3Keys = Get-RuntimeLookupActualKeys -DataRoot $DataRoot -Kind 'layer3'
    $useCaseKeys = Get-RuntimeLookupActualKeys -DataRoot $DataRoot -Kind 'usecase'
    $lineCounts = Get-UseCaseActualLineCounts -DataRoot $DataRoot
    if ($layer3Keys.Count -ne 2105 -or $useCaseKeys.Count -ne 1631 -or $lineCounts.Count -ne 1631) {
        throw 'runtime_payload_lookup_package_denominator_mismatch'
    }
    foreach ($key in $useCaseKeys) {
        if (-not $lineCounts.ContainsKey($key)) {
            throw "runtime_payload_lookup_package_key_mismatch: $key"
        }
    }
    foreach ($key in $lineCounts.Keys) {
        if (-not $useCaseKeys.Contains($key)) {
            throw "runtime_payload_lookup_package_key_mismatch: $key"
        }
    }

    $layer3SortedKeys = [string[]]@($layer3Keys)
    $useCaseSortedKeys = [string[]]@($useCaseKeys)
    [System.Array]::Sort($layer3SortedKeys, [System.StringComparer]::Ordinal)
    [System.Array]::Sort($useCaseSortedKeys, [System.StringComparer]::Ordinal)

    $identityRows = [System.Collections.Generic.List[string]]::new()
    foreach ($key in $layer3SortedKeys) {
        $identityRows.Add("layer3`t$key")
    }
    foreach ($key in $useCaseSortedKeys) {
        $identityRows.Add("usecase`t$key`t$($lineCounts[$key])")
    }
    foreach ($indexName in @('IrisLayer3DataChunkIndex.lua', 'UseCaseDescriptions/ChunkIndex.lua')) {
        $indexPath = if ($indexName -ceq 'IrisLayer3DataChunkIndex.lua') {
            (Get-Layer3GenerationPointerData -DataRoot $DataRoot).index_path
        }
        else {
            Join-Path $DataRoot $indexName
        }
        $indexText = Get-Content -LiteralPath $indexPath -Raw
        $position = 0
        foreach ($match in [regex]::Matches($indexText, 'sha256 = "([0-9a-f]{64})"')) {
            $position += 1
            $identityRows.Add("chunk-hash`t$indexName`t$position`t$([string]$match.Groups[1].Value)")
        }
    }
    $sourceDigest = Get-Utf8StringSha256 -Value ([string]::Join("`n", $identityRows) + "`n")
    $identity = [ordered]@{
        schema_version = 'iris-runtime-lookup-package-parity-v1'
        generation_id = 'lookup-' + $sourceDigest.Substring(0, 16)
        source_digest = $sourceDigest
        layer3_entry_count = $layer3Keys.Count
        usecase_entry_count = $useCaseKeys.Count
        line_count_entry_count = $lineCounts.Count
        status = 'PASS'
    }
    if (-not $SkipManifestCheck) {
        $manifestPath = Join-Path $DataRoot 'IrisRuntimeLookupPackageIdentity.json'
        if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
            throw 'runtime_payload_lookup_package_manifest_missing'
        }
        $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if (
            $manifest.schema_version -cne 'iris-runtime-lookup-package-identity-v1' -or
            $manifest.generation_id -cne $identity.generation_id -or
            $manifest.source_digest -cne $identity.source_digest -or
            [int]$manifest.layer3_entry_count -ne $identity.layer3_entry_count -or
            [int]$manifest.usecase_entry_count -ne $identity.usecase_entry_count -or
            [int]$manifest.line_count_entry_count -ne $identity.line_count_entry_count
        ) {
            throw 'runtime_payload_lookup_package_generation_mismatch'
        }
    }
    return $identity
}

Export-ModuleMember -Function Assert-RuntimeLookupIndexIdentity, Assert-RuntimeLookupPackageParity, Get-NormalizedUtf8EolSha256
