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

function Assert-RuntimeLookupIndexIdentity {
    param(
        [Parameter(Mandatory = $true)][string]$DataRoot,
        [Parameter(Mandatory = $true)][string]$IndexName
    )
    $indexPath = Join-Path $DataRoot $IndexName
    if (-not (Test-Path -LiteralPath $indexPath -PathType Leaf)) {
        throw "runtime_payload_lookup_index_missing: $indexPath"
    }
    $strictUtf8 = [System.Text.UTF8Encoding]::new($false, $true)
    $indexText = $strictUtf8.GetString([System.IO.File]::ReadAllBytes($indexPath))
    $indexText = $indexText.Replace("`r`n", "`n").Replace("`r", "`n")

    $isLayer3 = $IndexName -ceq 'IrisLayer3DataChunkIndex.lua'
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
        'Iris/Data/IrisLayer3DataChunks/Chunk'
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

Export-ModuleMember -Function Assert-RuntimeLookupIndexIdentity, Get-NormalizedUtf8EolSha256
