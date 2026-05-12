--[[
    Index.lua - Iris static index facade

    Core index facade. Returns frozen normalized lookup results only.
]]

local Index = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local ItemKey = require("Iris/Util/ItemKey")
local StaticData = require("Iris/API/StaticData")

--- 아이템의 Recipe 연결 정보 반환
--- @param item InventoryItem
--- @return table {{role, category}, ...} 배열
function Index.getRecipeConnectionsForItem(item)
    if not item then return {} end

    local recipeIndex = StaticData.get("recipeIndex")
    if not recipeIndex then return {} end

    local fullType = ItemKey.getFullTypeFromItem(item)
    if not fullType then return {} end

    local ok, result = ProtectedCall.data(function()
        return recipeIndex.getRoles(fullType)
    end)

    if ok and result then return result end
    return {}
end

--- 아이템의 Moveables 연결 정보 반환
--- @param item InventoryItem
--- @return table {itemId_registered, moveablesTag}
function Index.getMoveablesInfoForItem(item)
    if not item then
        return { itemId_registered = false, moveablesTag = nil }
    end

    local moveablesIndex = StaticData.get("moveablesIndex")
    if not moveablesIndex then
        return { itemId_registered = false, moveablesTag = nil }
    end

    local fullType = ItemKey.getFullTypeFromItem(item)
    if not fullType then
        return { itemId_registered = false, moveablesTag = nil }
    end

    local registered = false
    local tag = nil

    local ok1, result1 = ProtectedCall.data(function()
        return moveablesIndex.isItemIdRegistered(fullType)
    end)
    if ok1 then registered = result1 end

    local ok2, result2 = ProtectedCall.data(function()
        return moveablesIndex.getMoveablesTag(fullType)
    end)
    if ok2 then tag = result2 end

    return { itemId_registered = registered, moveablesTag = tag }
end

--- 아이템의 Fixing 연결 정보 반환
--- @param item InventoryItem
--- @return table {isFixer}
function Index.getFixingInfoForItem(item)
    if not item then return { isFixer = false } end

    local fixingIndex = StaticData.get("fixingIndex")
    if not fixingIndex then return { isFixer = false } end

    local fullType = ItemKey.getFullTypeFromItem(item)
    if not fullType then return { isFixer = false } end

    local isFixer = false
    local ok, result = ProtectedCall.data(function()
        return fixingIndex.isFixer(fullType)
    end)
    if ok then isFixer = result end

    return { isFixer = isFixer }
end

return Index
