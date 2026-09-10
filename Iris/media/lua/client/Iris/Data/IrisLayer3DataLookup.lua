-- Internal demand lookup. The complete IrisLayer3DataChunks facade remains public.
local IrisLayer3DataLookup = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local RuntimeLookupDiagnostics = require("Iris/Data/IrisRuntimeLookupDiagnostics")
local currentOk, current = safeRequire("Iris/Data/IrisLayer3DataCurrent")

-- Successor products use one session snapshot for both Menu locales. The
-- legacy router below retains its exact schema and module-name restrictions.
if not currentOk or (type(current) == "table" and current.schema_version == "iris_layer3_product_compat_v1") then
    local Product = { isProduct = true }
    local cache, records = {}, nil
    local reason = "product_pointer_invalid"
    local productId = currentOk and current.product_id or nil
    local prefix = type(productId) == "string" and
        ("Iris/Data/IrisLayer3ProductGenerations/" .. productId .. "/") or nil
    local function validId(value)
        return type(value) == "string" and #value == 68 and value:match("^l3p%-[0-9a-f]+$") ~= nil
    end
    if validId(productId) and current.index_module == prefix .. "Index" then
        local ok, loaded = safeRequire(current.index_module)
        if ok and type(loaded) == "table" and loaded.schema_version == "iris_layer3_product_index_v1" and
            loaded.product_id == productId and type(loaded.chunks) == "table" then
            local count, previous, valid = 0, nil, true
            for ordinal, record in ipairs(loaded.chunks) do
                if type(record) ~= "table" or type(record.first) ~= "string" or type(record.last) ~= "string" or
                    record.first > record.last or (previous and record.first <= previous) or
                    record.module ~= prefix .. string.format("Chunks/Chunk%03d", ordinal) or
                    type(record.count) ~= "number" or record.count < 1 or record.count ~= math.floor(record.count) or
                    type(record.sha256) ~= "string" or #record.sha256 ~= 64 or
                    record.sha256:match("^[0-9a-f]+$") == nil then
                    valid = false
                    break
                end
                previous, count = record.last, count + record.count
            end
            if valid and count == 2105 and count == loaded.entry_count then records, reason = loaded.chunks, nil end
        end
    end
    local function validEntry(key, entry)
        if type(entry) ~= "table" or entry.item_id ~= key or entry.product_id ~= productId or
            type(entry.locales) ~= "table" then return false end
        for _, locale in ipairs({"ko", "en"}) do
            local value = entry.locales[locale]
            if type(value) ~= "table" or type(value.text) ~= "string" or type(value.blocks) ~= "table" then return false end
            local count = 0
            for position, text in pairs(value.blocks) do
                if type(position) ~= "number" or position < 1 or position ~= math.floor(position) or
                    type(text) ~= "string" or text == "" then return false end
                count = count + 1
            end
            if count ~= #value.blocks or table.concat(value.blocks, "\n") ~= value.text then return false end
        end
        return true
    end
    function Product.get(fullType)
        if type(fullType) ~= "string" or fullType == "" then return nil, "lookup_miss" end
        if not records then return nil, reason end
        local low, high = 1, #records
        while low <= high do
            local middle = math.floor((low + high) / 2)
            local record = records[middle]
            if fullType < record.first then high = middle - 1
            elseif fullType > record.last then low = middle + 1
            else
                local chunk = cache[record.module]
                if not chunk then
                    local ok, loaded = safeRequire(record.module)
                    if not ok or type(loaded) ~= "table" then return nil, "product_chunk_unavailable" end
                    local count, first, last = 0, nil, nil
                    for key, entry in pairs(loaded) do
                        if type(key) ~= "string" or not validEntry(key, entry) then return nil, "product_chunk_invalid" end
                        count = count + 1
                        if not first or key < first then first = key end
                        if not last or key > last then last = key end
                    end
                    if count ~= record.count or first ~= record.first or last ~= record.last then return nil, "product_chunk_invalid" end
                    chunk, cache[record.module] = loaded, loaded
                end
                if not chunk[fullType] then return nil, "lookup_miss" end
                return chunk[fullType], nil
            end
        end
        return nil, "lookup_miss"
    end
    function Product.getLocale(fullType, locale)
        if locale ~= "ko" and locale ~= "en" then return nil, "locale_invalid" end
        local entry, failure = Product.get(fullType)
        return entry and entry.locales[locale] or nil, failure
    end
    function Product.getDiagnostics()
        local modules = {}
        for name, _ in pairs(cache) do modules[#modules + 1] = name end
        table.sort(modules)
        return { indexValid = records ~= nil, productId = productId, loadedChunkCount = #modules, loadedChunkModules = modules }
    end
    function Product.reset() cache = {} end
    return Product
end
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
        if record.module:match(
            "^Iris/Data/IrisLayer3Generations/dvf33%-%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x/Chunks/Chunk%d%d%d$"
        ) == nil then
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
