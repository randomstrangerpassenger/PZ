-- Exact, first-use access to the admitted T2 payload. No semantic fallback.
local Lookup = {}
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local attempted = false
local data = nil

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

return Lookup
