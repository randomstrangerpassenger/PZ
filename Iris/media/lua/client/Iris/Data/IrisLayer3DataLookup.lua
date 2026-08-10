-- Internal demand lookup. The complete IrisLayer3DataChunks facade remains public.
local IrisLayer3DataLookup = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local RuntimeLookupDiagnostics = require("Iris/Data/IrisRuntimeLookupDiagnostics")
local indexOk, index = safeRequire("Iris/Data/IrisLayer3DataChunkIndex")
local chunkCache = {}
local diagnostics = {
    requireCallCount = 0,
    loadedChunkCount = 0,
    lookupCount = 0,
    lookupMissCount = 0,
    fallbackCount = 0,
    fallbackReasons = {},
}

local function recordMiss()
    diagnostics.lookupMissCount = diagnostics.lookupMissCount + 1
    RuntimeLookupDiagnostics.recordMetric("layer3", "lookup_miss", 1)
    return nil, "lookup_miss"
end

local function recordFallback(reason)
    diagnostics.fallbackCount = diagnostics.fallbackCount + 1
    diagnostics.fallbackReasons[reason] = (diagnostics.fallbackReasons[reason] or 0) + 1
    RuntimeLookupDiagnostics.recordFallback("layer3", reason)
    return nil, reason
end

local function validRecord(record)
    return type(record) == "table" and type(record.first) == "string" and
        type(record.last) == "string" and record.first <= record.last and
        type(record.module) == "string" and
        type(record.count) == "number" and record.count > 0 and
        type(record.sha256) == "string" and #record.sha256 == 64
end

local function validIndex()
    if not indexOk or type(index) ~= "table" or
        index.schema_version ~= "iris_layer3_chunk_range_index_v1" or
        type(index.chunks) ~= "table" then
        return false, "index_shape_invalid"
    end
    local previousLast = nil
    local total = 0
    for _, record in ipairs(index.chunks) do
        if not validRecord(record) or (previousLast and record.first <= previousLast) then
            return false, "index_shape_invalid"
        end
        if record.module:match("^Iris/Data/IrisLayer3DataChunks/Chunk%d%d%d$") == nil then
            return false, "module_name_invalid"
        end
        previousLast = record.last
        total = total + record.count
    end
    if total ~= index.entry_count then return false, "index_shape_invalid" end
    return true, nil
end

local indexValid, indexInvalidReason = validIndex()

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
    local low, high = 1, #index.chunks
    while low <= high do
        local middle = math.floor((low + high) / 2)
        local record = index.chunks[middle]
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

function IrisLayer3DataLookup.get(fullType)
    diagnostics.lookupCount = diagnostics.lookupCount + 1
    if type(fullType) ~= "string" or fullType == "" then
        return recordMiss()
    end
    if not indexValid then
        return recordFallback(indexOk and indexInvalidReason or "router_unavailable")
    end
    local record = findRecord(fullType)
    if not record then return recordMiss() end

    local chunk = chunkCache[record.module]
    if not chunk then
        diagnostics.requireCallCount = diagnostics.requireCallCount + 1
        local ok, loaded = safeRequire(record.module)
        if not ok or type(loaded) ~= "table" then
            return recordFallback("target_module_load_failure")
        end
        if not validLoadedChunk(loaded, record) then
            return recordFallback("index_content_mismatch")
        end
        chunk = loaded
        chunkCache[record.module] = chunk
        diagnostics.loadedChunkCount = diagnostics.loadedChunkCount + 1
    end
    local entry = chunk[fullType]
    -- Range records deliberately cover the lexical gaps between real keys.
    -- Once the loaded chunk itself matches its index record, an absent key is
    -- an ordinary lookup miss rather than evidence of router corruption.
    if entry == nil then return recordMiss() end
    return entry, nil
end

function IrisLayer3DataLookup.getDiagnostics()
    local reasons = {}
    for reason, count in pairs(diagnostics.fallbackReasons) do reasons[reason] = count end
    local loadedChunkModules = {}
    for moduleName, _ in pairs(chunkCache) do table.insert(loadedChunkModules, moduleName) end
    table.sort(loadedChunkModules)
    return {
        indexValid = indexValid,
        requireCallCount = diagnostics.requireCallCount,
        loadedChunkCount = diagnostics.loadedChunkCount,
        loadedChunkModules = loadedChunkModules,
        lookupCount = diagnostics.lookupCount,
        lookupMissCount = diagnostics.lookupMissCount,
        fallbackCount = diagnostics.fallbackCount,
        fallbackReasons = reasons,
    }
end

function IrisLayer3DataLookup.reset()
    chunkCache = {}
    diagnostics.requireCallCount = 0
    diagnostics.loadedChunkCount = 0
    diagnostics.lookupCount = 0
    diagnostics.lookupMissCount = 0
    diagnostics.fallbackCount = 0
    diagnostics.fallbackReasons = {}
end

return IrisLayer3DataLookup
