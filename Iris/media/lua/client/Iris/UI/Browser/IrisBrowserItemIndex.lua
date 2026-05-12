--[[
    IrisBrowserItemIndex.lua

    Whole item index for BrowserData. This module only knows how to scan
    Project Zomboid items and key them by fullType.
]]

local IrisBrowserItemIndex = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local ItemAccess = require("Iris/Util/IrisItemAccess")
local ObjectAccess = require("Iris/Util/IrisObjectAccess")
local debug = bootstrap.debug
local warn = bootstrap.warn

local function emptyIndex()
    return {
        itemsByFullType = {},
        itemCount = 0,
        errorCount = 0,
    }
end

function IrisBrowserItemIndex.build()
    local index = emptyIndex()

    if not getAllItems then
        warn("[IrisBrowserItemIndex] getAllItems not available")
        return index
    end

    local allItemsOk, allItems = ProtectedCall.engine(getAllItems)
    if not allItemsOk or not allItems then
        warn("[IrisBrowserItemIndex] getAllItems() failed: " .. tostring(allItems))
        return index
    end

    if not allItems.size then
        warn("[IrisBrowserItemIndex] allItems has no size method")
        return index
    end

    local sizeOk, itemsSize = ObjectAccess.call(allItems, "size")
    if not sizeOk or not itemsSize then
        warn("[IrisBrowserItemIndex] allItems:size() failed")
        return index
    end

    local maxErrors = 5
    for i = 0, itemsSize - 1 do
        if i % 1000 == 0 then
            debug("[IrisBrowserItemIndex] Processing item " .. i .. "/" .. itemsSize)
        end

        local getOk, item = ObjectAccess.call(allItems, "get", i)
        if getOk and item then
            local fullType = ItemAccess.getFullType(item)
            if fullType then
                index.itemsByFullType[fullType] = item
                index.itemCount = index.itemCount + 1
            end
        else
            if index.errorCount < maxErrors then
                debug("[IrisBrowserItemIndex] allItems:get(" .. i .. ") failed: " .. tostring(item))
            end
            index.errorCount = index.errorCount + 1
        end
    end

    debug("[IrisBrowserItemIndex] Built " .. tostring(index.itemCount) .. " items, errors=" .. tostring(index.errorCount))
    return index
end

return IrisBrowserItemIndex
