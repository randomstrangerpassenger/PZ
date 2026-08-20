-- Internal demand lookup. The complete IrisUseCaseDescriptions facade remains public.
local IrisUseCaseDescriptionsLookup = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local RuntimeLookupDiagnostics = require("Iris/Data/IrisRuntimeLookupDiagnostics")
local chunkIndex = nil
local lineCountIndex = nil
local indexMetadataSnapshot = nil
local chunkCache = {}
local requirements = nil
local diagnostics = {
    descriptionRequireCallCount = 0,
    loadedDescriptionChunkCount = 0,
    requirementsRequireCallCount = 0,
    lookupCount = 0,
    lookupMissCount = 0,
    fallbackCount = 0,
    fallbackReasons = {},
    indexMetadataMaterializationCount = 0,
    chunkIndexRequireCallCount = 0,
    lineCountIndexRequireCallCount = 0,
    chunkIndexSelfValidationCount = 0,
    lineCountIndexSelfValidationCount = 0,
    indexEntryCountCrossCheckCount = 0,
}

local function recordMiss(surface)
    diagnostics.lookupMissCount = diagnostics.lookupMissCount + 1
    RuntimeLookupDiagnostics.recordMetric(surface or "usecase", "lookup_miss", 1)
    return nil, "lookup_miss"
end

local function recordFallback(reason)
    diagnostics.fallbackCount = diagnostics.fallbackCount + 1
    diagnostics.fallbackReasons[reason] = (diagnostics.fallbackReasons[reason] or 0) + 1
    RuntimeLookupDiagnostics.recordFallback("usecase", reason)
    return nil, reason
end

local function validRecord(record)
    return type(record) == "table" and type(record.first) == "string" and
        type(record.last) == "string" and record.first <= record.last and
        type(record.module) == "string" and
        type(record.count) == "number" and record.count > 0 and
        type(record.sha256) == "string" and #record.sha256 == 64
end

local function validChunkIndex(indexOk, index)
    if not indexOk or type(index) ~= "table" or
        index.schema_version ~= "iris_usecase_chunk_range_index_v1" or
        type(index.chunks) ~= "table" then
        return false, "index_shape_invalid"
    end
    local previousLast = nil
    local total = 0
    for _, record in ipairs(index.chunks) do
        if not validRecord(record) or (previousLast and record.first <= previousLast) then
            return false, "index_shape_invalid"
        end
        if record.module:match("^Iris/Data/UseCaseDescriptions/Chunk%d%d%d$") == nil then
            return false, "module_name_invalid"
        end
        previousLast = record.last
        total = total + record.count
    end
    if total ~= index.entry_count then return false, "index_shape_invalid" end
    return true, nil
end

local function validLineCountIndex(indexOk, index)
    if not indexOk or type(index) ~= "table" or
        index.schema_version ~= "iris_usecase_line_count_index_v1" or
        type(index.lineCounts) ~= "table" or
        type(index.entry_count) ~= "number" then
        return false, "index_shape_invalid"
    end
    local lineCountEntries = 0
    for fullType, count in pairs(index.lineCounts) do
        if type(fullType) ~= "string" or type(count) ~= "number" or
            count < 0 or count ~= math.floor(count) then
            return false, "index_shape_invalid"
        end
        lineCountEntries = lineCountEntries + 1
    end
    if lineCountEntries ~= index.entry_count then return false, "index_shape_invalid" end
    return true, nil
end

local function state(status, reason)
    return { status = status, reason = reason }
end

local function ensureIndexMetadataSnapshot()
    if indexMetadataSnapshot then return indexMetadataSnapshot end

    diagnostics.indexMetadataMaterializationCount =
        diagnostics.indexMetadataMaterializationCount + 1
    diagnostics.chunkIndexRequireCallCount =
        diagnostics.chunkIndexRequireCallCount + 1
    local chunkOk, loadedChunkIndex = safeRequire(
        "Iris/Data/UseCaseDescriptions/ChunkIndex"
    )
    diagnostics.lineCountIndexRequireCallCount =
        diagnostics.lineCountIndexRequireCallCount + 1
    local lineCountOk, loadedLineCountIndex = safeRequire(
        "Iris/Data/UseCaseDescriptions/LineCountIndex"
    )

    diagnostics.chunkIndexSelfValidationCount =
        diagnostics.chunkIndexSelfValidationCount + 1
    local chunkValid, chunkReason = validChunkIndex(chunkOk, loadedChunkIndex)
    diagnostics.lineCountIndexSelfValidationCount =
        diagnostics.lineCountIndexSelfValidationCount + 1
    local lineCountValid, lineCountReason = validLineCountIndex(
        lineCountOk,
        loadedLineCountIndex
    )

    local crossCheckState = state("not_applicable", nil)
    if chunkValid and lineCountValid then
        diagnostics.indexEntryCountCrossCheckCount =
            diagnostics.indexEntryCountCrossCheckCount + 1
        if loadedChunkIndex.entry_count == loadedLineCountIndex.entry_count then
            crossCheckState = state("valid", nil)
        else
            crossCheckState = state("invalid", "index_content_mismatch")
        end
    end

    local candidate = {
        chunkState = chunkValid and state("valid", nil) or state(
            "invalid",
            chunkOk and chunkReason or "router_unavailable"
        ),
        lineCountState = lineCountValid and state("valid", nil) or state(
            "invalid",
            lineCountOk and lineCountReason or "router_unavailable"
        ),
        crossCheckState = crossCheckState,
    }

    -- Publish references and the complete state together. No caller can see a
    -- partially refreshed pair, while each index keeps independent validity.
    chunkIndex = loadedChunkIndex
    lineCountIndex = loadedLineCountIndex
    indexMetadataSnapshot = candidate
    RuntimeLookupDiagnostics.recordMetric(
        "usecase_index_metadata",
        "materializations",
        1
    )
    return indexMetadataSnapshot
end

local function validLoadedChunk(chunk, record)
    local count = 0
    local first = nil
    local last = nil
    for fullType, entry in pairs(chunk) do
        if type(fullType) ~= "string" or type(entry) ~= "table" then
            return false
        end
        count = count + 1
        if first == nil or fullType < first then first = fullType end
        if last == nil or fullType > last then last = fullType end
    end
    return count == record.count and first == record.first and last == record.last
end

local function findRecord(fullType)
    local low, high = 1, #chunkIndex.chunks
    while low <= high do
        local middle = math.floor((low + high) / 2)
        local record = chunkIndex.chunks[middle]
        if fullType < record.first then
            high = middle - 1
        elseif fullType > record.last then
            low = middle + 1
        else
            return record
        end
    end
    return nil
end

function IrisUseCaseDescriptionsLookup.get(fullType)
    diagnostics.lookupCount = diagnostics.lookupCount + 1
    if type(fullType) ~= "string" or fullType == "" then
        return recordMiss("usecase")
    end
    local snapshot = ensureIndexMetadataSnapshot()
    if snapshot.chunkState.status ~= "valid" then
        return recordFallback(snapshot.chunkState.reason)
    end
    if snapshot.lineCountState.status ~= "valid" then
        return recordFallback(snapshot.lineCountState.reason)
    end
    if snapshot.crossCheckState.status ~= "valid" then
        return recordFallback(snapshot.crossCheckState.reason or "index_content_mismatch")
    end
    local record = findRecord(fullType)
    if not record then
        if lineCountIndex.lineCounts[fullType] ~= nil then
            return recordFallback("index_content_mismatch")
        end
        return recordMiss("usecase")
    end

    local chunk = chunkCache[record.module]
    if not chunk then
        diagnostics.descriptionRequireCallCount = diagnostics.descriptionRequireCallCount + 1
        local ok, loaded = safeRequire(record.module)
        if not ok or type(loaded) ~= "table" then
            return recordFallback("target_module_load_failure")
        end
        if not validLoadedChunk(loaded, record) then
            return recordFallback("index_content_mismatch")
        end
        chunk = loaded
        chunkCache[record.module] = chunk
        diagnostics.loadedDescriptionChunkCount = diagnostics.loadedDescriptionChunkCount + 1
    end
    local entry = chunk[fullType]
    local lineCount = lineCountIndex.lineCounts[fullType]
    if entry == nil and lineCount == nil then
        return recordMiss("usecase")
    end
    if entry == nil or lineCount == nil then
        return recordFallback("index_content_mismatch")
    end
    if type(entry.lines) ~= "table" or #entry.lines ~= lineCount then
        return recordFallback("index_content_mismatch")
    end
    return entry, nil
end

function IrisUseCaseDescriptionsLookup.getLineCount(fullType)
    local snapshot = ensureIndexMetadataSnapshot()
    if snapshot.lineCountState.status ~= "valid" then
        return recordFallback(snapshot.lineCountState.reason)
    end
    if snapshot.crossCheckState.status == "invalid" then
        return recordFallback(snapshot.crossCheckState.reason)
    end
    local count = lineCountIndex.lineCounts[fullType]
    -- A valid line-count index is authoritative for the negative case too.
    -- Missing description keys therefore cost zero chunk loads; the full
    -- description lookup keeps its reason-coded lookup_miss fallback contract.
    if count == nil then return 0, nil end
    return count, nil
end

function IrisUseCaseDescriptionsLookup.getRequirements(recipeName)
    if type(recipeName) ~= "string" or recipeName == "" then
        return recordMiss("usecase_requirements")
    end
    if requirements == nil then
        diagnostics.requirementsRequireCallCount = diagnostics.requirementsRequireCallCount + 1
        local ok, loaded = safeRequire("Iris/Data/UseCaseDescriptions/RequirementsLookup")
        if not ok or type(loaded) ~= "table" then
            return recordFallback("target_module_load_failure")
        end
        requirements = loaded
    end
    local result = requirements[recipeName]
    if result == nil then return recordMiss("usecase_requirements") end
    return result, nil
end

function IrisUseCaseDescriptionsLookup.getDiagnostics()
    local reasons = {}
    for reason, count in pairs(diagnostics.fallbackReasons) do reasons[reason] = count end
    local loadedDescriptionChunkModules = {}
    for moduleName, _ in pairs(chunkCache) do
        table.insert(loadedDescriptionChunkModules, moduleName)
    end
    table.sort(loadedDescriptionChunkModules)
    local snapshot = indexMetadataSnapshot
    local chunkStatus = snapshot and snapshot.chunkState.status or "unloaded"
    local lineCountStatus = snapshot and snapshot.lineCountState.status or "unloaded"
    local crossCheckStatus = snapshot and snapshot.crossCheckState.status or "not_applicable"
    return {
        indexValid = chunkStatus == "valid" and lineCountStatus == "valid" and
            crossCheckStatus == "valid",
        chunkIndexValid = chunkStatus == "valid",
        lineCountIndexValid = lineCountStatus == "valid",
        chunkIndexState = chunkStatus,
        chunkIndexReason = snapshot and snapshot.chunkState.reason or nil,
        lineCountIndexState = lineCountStatus,
        lineCountIndexReason = snapshot and snapshot.lineCountState.reason or nil,
        crossCheckState = crossCheckStatus,
        crossCheckReason = snapshot and snapshot.crossCheckState.reason or nil,
        indexMetadataMaterializationCount = diagnostics.indexMetadataMaterializationCount,
        chunkIndexRequireCallCount = diagnostics.chunkIndexRequireCallCount,
        lineCountIndexRequireCallCount = diagnostics.lineCountIndexRequireCallCount,
        chunkIndexSelfValidationCount = diagnostics.chunkIndexSelfValidationCount,
        lineCountIndexSelfValidationCount = diagnostics.lineCountIndexSelfValidationCount,
        indexEntryCountCrossCheckCount = diagnostics.indexEntryCountCrossCheckCount,
        descriptionRequireCallCount = diagnostics.descriptionRequireCallCount,
        loadedDescriptionChunkCount = diagnostics.loadedDescriptionChunkCount,
        loadedDescriptionChunkModules = loadedDescriptionChunkModules,
        requirementsRequireCallCount = diagnostics.requirementsRequireCallCount,
        lookupCount = diagnostics.lookupCount,
        lookupMissCount = diagnostics.lookupMissCount,
        fallbackCount = diagnostics.fallbackCount,
        fallbackReasons = reasons,
    }
end

function IrisUseCaseDescriptionsLookup.reset()
    chunkIndex = nil
    lineCountIndex = nil
    indexMetadataSnapshot = nil
    chunkCache = {}
    requirements = nil
    diagnostics.descriptionRequireCallCount = 0
    diagnostics.loadedDescriptionChunkCount = 0
    diagnostics.requirementsRequireCallCount = 0
    diagnostics.lookupCount = 0
    diagnostics.lookupMissCount = 0
    diagnostics.fallbackCount = 0
    diagnostics.fallbackReasons = {}
    diagnostics.indexMetadataMaterializationCount = 0
    diagnostics.chunkIndexRequireCallCount = 0
    diagnostics.lineCountIndexRequireCallCount = 0
    diagnostics.chunkIndexSelfValidationCount = 0
    diagnostics.lineCountIndexSelfValidationCount = 0
    diagnostics.indexEntryCountCrossCheckCount = 0
end

return IrisUseCaseDescriptionsLookup
