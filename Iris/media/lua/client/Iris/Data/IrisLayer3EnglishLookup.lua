local Lookup = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local index = nil
local chunkCache = {}

local function ensureIndex()
    if index then return index end
    local ok, loaded = safeRequire("Iris/Data/Layer3English/Index")
    if ok and type(loaded) == "table" and type(loaded.chunks) == "table" then
        index = loaded
    end
    return index
end

local function findRecord(fullType)
    local loaded = ensureIndex()
    if not loaded then return nil end
    local low, high = 1, #loaded.chunks
    while low <= high do
        local middle = math.floor((low + high) / 2)
        local record = loaded.chunks[middle]
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

function Lookup.get(fullType)
    if type(fullType) ~= "string" or fullType == "" then return nil end
    local ok, pointer = safeRequire("Iris/Data/IrisLayer3DataCurrent")
    if not ok then return nil end
    if type(pointer) == "table" and pointer.schema_version == "iris_layer3_product_compat_v1" then
        local loaded, product = safeRequire("Iris/Data/IrisLayer3DataLookup")
        if not loaded or type(product.getLocale) ~= "function" then return nil end
        local value = product.getLocale(fullType, "en")
        return value and value.text ~= "" and value.text or nil
    end
    local record = findRecord(fullType)
    if not record then return nil end
    local chunk = chunkCache[record.module]
    if not chunk then
        local ok, loaded = safeRequire(record.module)
        if not ok or type(loaded) ~= "table" then return nil end
        chunk = loaded
        chunkCache[record.module] = chunk
    end
    return chunk[fullType]
end

return Lookup
