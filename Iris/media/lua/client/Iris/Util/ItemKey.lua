--[[
    ItemKey.lua - shared Iris item identity helpers
]]

local ItemKey = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")

local function callGetFullType(item)
    local ok, result = ProtectedCall.engine(function()
        return item:getFullType()
    end)
    if ok and result then
        return tostring(result)
    end
    return nil
end

local function callGetFullName(item)
    local ok, result = ProtectedCall.engine(function()
        return item:getFullName()
    end)
    if ok and result then
        return tostring(result)
    end
    return nil
end

local function readFullTypeField(item)
    local ok, result = ProtectedCall.engine(function()
        return item.fullType
    end)
    if ok and result then
        return tostring(result)
    end
    return nil
end

function ItemKey.getFullTypeFromItem(item)
    if not item then
        return nil
    end
    if type(item) == "string" then
        return item
    end
    if type(item) ~= "table" and type(item) ~= "userdata" then
        return nil
    end

    local fullType = nil
    if item.getFullType then
        fullType = callGetFullType(item)
        if fullType and fullType ~= "" then
            return fullType
        end
    end

    if item.getFullName then
        fullType = callGetFullName(item)
        if fullType and fullType ~= "" then
            return fullType
        end
    end

    fullType = readFullTypeField(item)
    if fullType and fullType ~= "" then
        return fullType
    end

    return nil
end

ItemKey.getFullType = ItemKey.getFullTypeFromItem

return ItemKey
