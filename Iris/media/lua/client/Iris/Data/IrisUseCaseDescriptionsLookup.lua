-- Internal demand lookup. The complete IrisUseCaseDescriptions facade remains public.
local IrisUseCaseDescriptionsLookup = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local RuntimeLookupDiagnostics = require("Iris/Data/IrisRuntimeLookupDiagnostics")
local chunkIndexOk, chunkIndex = safeRequire("Iris/Data/UseCaseDescriptions/ChunkIndex")
local lineCountIndexOk, lineCountIndex = safeRequire("Iris/Data/UseCaseDescriptions/LineCountIndex")
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

local function validChunkIndex()
    if not chunkIndexOk or type(chunkIndex) ~= "table" or
        chunkIndex.schema_version ~= "iris_usecase_chunk_range_index_v1" or
        type(chunkIndex.chunks) ~= "table" then
        return false, "index_shape_invalid"
    end
    local previousLast = nil
    local total = 0
    for _, record in ipairs(chunkIndex.chunks) do
        if not validRecord(record) or (previousLast and record.first <= previousLast) then
            return false, "index_shape_invalid"
        end
        if record.module:match("^Iris/Data/UseCaseDescriptions/Chunk%d%d%d$") == nil then
            return false, "module_name_invalid"
        end
        previousLast = record.last
        total = total + record.count
    end
    if total ~= chunkIndex.entry_count then return false, "index_shape_invalid" end
    return true, nil
end

local function validLineCountIndex()
    if not lineCountIndexOk or type(lineCountIndex) ~= "table" or
        lineCountIndex.schema_version ~= "iris_usecase_line_count_index_v1" or
        type(lineCountIndex.lineCounts) ~= "table" or
        type(lineCountIndex.entry_count) ~= "number" then
        return false, "index_shape_invalid"
    end
    local lineCountEntries = 0
    for fullType, count in pairs(lineCountIndex.lineCounts) do
        if type(fullType) ~= "string" or type(count) ~= "number" or
            count < 0 or count ~= math.floor(count) then
            return false, "index_shape_invalid"
        end
        lineCountEntries = lineCountEntries + 1
    end
    if lineCountEntries ~= lineCountIndex.entry_count then return false, "index_shape_invalid" end
    return true, nil
end

local chunkIndexValid, chunkIndexInvalidReason = validChunkIndex()
local lineCountIndexValid, lineCountIndexInvalidReason = validLineCountIndex()

if chunkIndexValid and lineCountIndexValid and
    chunkIndex.entry_count ~= lineCountIndex.entry_count then
    chunkIndexValid = false
    lineCountIndexValid = false
    chunkIndexInvalidReason = "index_content_mismatch"
    lineCountIndexInvalidReason = "index_content_mismatch"
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
    if not chunkIndexValid then
        return recordFallback(chunkIndexOk and chunkIndexInvalidReason or "router_unavailable")
    end
    if not lineCountIndexValid then
        return recordFallback(lineCountIndexOk and lineCountIndexInvalidReason or "router_unavailable")
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
    if not lineCountIndexValid then
        return recordFallback(
            lineCountIndexOk and lineCountIndexInvalidReason or "router_unavailable"
        )
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
    return {
        indexValid = chunkIndexValid and lineCountIndexValid,
        chunkIndexValid = chunkIndexValid,
        lineCountIndexValid = lineCountIndexValid,
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
    chunkCache = {}
    requirements = nil
    diagnostics.descriptionRequireCallCount = 0
    diagnostics.loadedDescriptionChunkCount = 0
    diagnostics.requirementsRequireCallCount = 0
    diagnostics.lookupCount = 0
    diagnostics.lookupMissCount = 0
    diagnostics.fallbackCount = 0
    diagnostics.fallbackReasons = {}
end

return IrisUseCaseDescriptionsLookup
