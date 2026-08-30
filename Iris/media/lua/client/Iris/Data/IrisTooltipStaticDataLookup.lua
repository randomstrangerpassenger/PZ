-- Exact, first-use access to the admitted T2 payload. No semantic fallback.
local Lookup = {}
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local attempted = false
local data = nil
local variantsAttempted = false
local recipeData = nil

-- Lua 5.1's %s only covers ASCII; reject Unicode whitespace-only rows too.
local unicodeSpaces = {
    "\194\133", "\194\160", "\225\154\128", "\226\128\128", "\226\128\129",
    "\226\128\130", "\226\128\131", "\226\128\132", "\226\128\133", "\226\128\134",
    "\226\128\135", "\226\128\136", "\226\128\137", "\226\128\138", "\226\128\168",
    "\226\128\169", "\226\128\175", "\226\129\159", "\227\128\128",
}

local function validRows(rows)
    if type(rows) ~= "table" or getmetatable(rows) ~= nil then return false end
    local count, last = 0, 0
    -- PZ's Kahlua exposes pairs, but not the standard Lua global next.
    -- Metatables are rejected above, so every stored key is still checked.
    for key, value in pairs(rows) do
        if type(key) ~= "number" or key < 1 or key > 4 or key ~= math.floor(key) or
            type(value) ~= "string" or value:find("[\r\n]") then return false end
        local visible = value:gsub("%s", "")
        for _, space in ipairs(unicodeSpaces) do visible = visible:gsub(space, "") end
        if visible == "" then return false end
        count = count + 1
        if key > last then last = key end
    end
    return count == last
end

function Lookup.get(fullType, locale)
    if type(fullType) ~= "string" or fullType == "" or
        (locale ~= "ko" and locale ~= "en") then return nil end
    if not attempted then
        attempted = true
        local ok, loaded = ProtectedCall.call(require, "Iris/Data/IrisTooltipStaticData")
        if ok and type(loaded) == "table" and getmetatable(loaded) == nil then data = loaded end
    end
    if not data then return nil end
    local entry = rawget(data, fullType)
    if type(entry) ~= "table" or getmetatable(entry) ~= nil then return nil end
    local rows = rawget(entry, locale)
    if not validRows(rows) then return nil end
    -- Internal read-only consumer: no row copy/cache, mutation, or string repair.
    return rows
end

local function sameRows(left, right)
    if not validRows(left) or not validRows(right) or #left ~= #right then return false end
    for i=1,#left do if left[i] ~= right[i] then return false end end
    return true
end

-- Pick a complete bilingual view once per opening. The producer, not runtime,
-- owns recipe eligibility, names, row assembly, and preservation of other rows.
function Lookup.open(fullType, pick)
    local ko, en = Lookup.get(fullType, "ko"), Lookup.get(fullType, "en")
    if not ko or not en then return nil end
    if not variantsAttempted then
        variantsAttempted = true
        local ok, loaded = ProtectedCall.call(require, "Iris/Data/IrisTooltipRecipeVariants")
        if ok and type(loaded) == "table" and getmetatable(loaded) == nil then recipeData = loaded end
    end
    if not recipeData then return nil end
    local entry = rawget(recipeData, fullType)
    if entry == nil then return {ko=ko, en=en} end
    if type(entry) ~= "table" or getmetatable(entry) ~= nil or
        type(entry.base) ~= "table" or getmetatable(entry.base) ~= nil or
        not sameRows(entry.base.ko, ko) or not sameRows(entry.base.en, en) or
        type(entry.variants) ~= "table" or getmetatable(entry.variants) ~= nil then return nil end
    local count, last, seen = 0, 0, {}
    for key, variant in pairs(entry.variants) do
        if type(key) ~= "number" or key < 1 or key ~= math.floor(key) or
            type(variant) ~= "table" or getmetatable(variant) ~= nil or
            type(variant.id) ~= "string" or variant.id == "" or seen[variant.id] or
            not validRows(variant.ko) or not validRows(variant.en) or
            #variant.ko == 0 or #variant.ko ~= #variant.en then return nil end
        seen[variant.id] = true
        count, last = count+1, math.max(last, key)
    end
    if count ~= last then return nil end
    if count == 0 then
        local fixed = entry.without_recipe
        if type(fixed) ~= "table" or getmetatable(fixed) ~= nil or
            not validRows(fixed.ko) or not validRows(fixed.en) or #fixed.ko ~= #fixed.en then return nil end
        return fixed
    end
    local index = count == 1 and 1 or pick(count)
    if type(index) ~= "number" or index < 1 or index > count or index ~= math.floor(index) then return nil end
    return entry.variants[index]
end

return Lookup
