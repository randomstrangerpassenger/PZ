--[[
    IrisItemAccess.lua - shared Iris item accessor helpers
]]

local IrisItemAccess = {}

local ItemKey = require("Iris/Util/ItemKey")
local ObjectAccess = require("Iris/Util/IrisObjectAccess")

local function normalizeString(value, fallback)
    if value ~= nil then
        local text = tostring(value)
        if text ~= "" then
            return text
        end
    end
    return fallback
end

function IrisItemAccess.getFullType(item, fallback)
    return normalizeString(ItemKey.getFullTypeFromItem(item), fallback)
end

function IrisItemAccess.getDisplayName(item, fallback)
    return normalizeString(ObjectAccess.invokeMethod(item, "getDisplayName", nil), fallback)
end

function IrisItemAccess.getType(item, fallback)
    local itemType = ObjectAccess.invokeMethod(item, "getType", nil)
    if itemType == nil then
        itemType = ObjectAccess.invokeMethod(item, "getTypeString", nil)
    end
    return normalizeString(itemType, fallback)
end

function IrisItemAccess.getModuleName(item, fallback)
    local moduleName = ObjectAccess.invokeMethod(item, "getModule", nil)
    if moduleName == nil then return fallback end

    local text = tostring(moduleName)
    if text:find("@", 1, true) then
        local resolved = ObjectAccess.invokeMethod(moduleName, "getName", nil)
        if resolved == nil then return fallback end
        text = tostring(resolved)
    end
    return normalizeString(text, fallback)
end

return IrisItemAccess
