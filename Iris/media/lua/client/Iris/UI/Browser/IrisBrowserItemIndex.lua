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
local instrumentationEnabled = false

local function nowMilliseconds()
    if getTimestampMs then
        local ok, value = ProtectedCall.engine(getTimestampMs)
        if ok and type(value) == "number" then return value end
    end
    if os and os.clock then return os.clock() * 1000 end
    return 0
end

local function emptyIndex()
    return {
        itemsByFullType = {},
        itemCount = 0,
        errorCount = 0,
        getAllItemsCallCount = 0,
        scannedItemCount = 0,
        elapsedMilliseconds = 0,
        failureReason = nil,
    }
end

local function failed(index, startedAt, reason)
    index.failureReason = reason
    if instrumentationEnabled then
        index.elapsedMilliseconds = math.max(0, nowMilliseconds() - startedAt)
    end
    return index, reason
end

function IrisBrowserItemIndex.setInstrumentationEnabled(enabled)
    instrumentationEnabled = enabled == true
end

function IrisBrowserItemIndex.build()
    local index = emptyIndex()
    local startedAt = instrumentationEnabled and nowMilliseconds() or 0

    if not getAllItems then
        warn("[IrisBrowserItemIndex] getAllItems not available")
        return failed(index, startedAt, "get_all_items_unavailable")
    end

    if instrumentationEnabled then
        index.getAllItemsCallCount = index.getAllItemsCallCount + 1
    end
    local allItemsOk, allItems = ProtectedCall.engine(getAllItems)
    if not allItemsOk or not allItems then
        warn("[IrisBrowserItemIndex] getAllItems() failed: " .. tostring(allItems))
        return failed(index, startedAt, "get_all_items_failed")
    end

    if not allItems.size then
        warn("[IrisBrowserItemIndex] allItems has no size method")
        return failed(index, startedAt, "item_collection_size_unavailable")
    end
    if not allItems.get then
        warn("[IrisBrowserItemIndex] allItems has no get method")
        return failed(index, startedAt, "item_collection_get_unavailable")
    end

    local sizeOk, itemsSize = ObjectAccess.call(allItems, "size")
    if not sizeOk or type(itemsSize) ~= "number" then
        warn("[IrisBrowserItemIndex] allItems:size() failed")
        return failed(index, startedAt, "item_collection_size_failed")
    end
    if itemsSize <= 0 then
        warn("[IrisBrowserItemIndex] allItems collection is empty")
        return failed(index, startedAt, "item_collection_empty")
    end

    local maxErrors = 5
    for i = 0, itemsSize - 1 do
        if instrumentationEnabled then
            index.scannedItemCount = index.scannedItemCount + 1
        end
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

    if instrumentationEnabled then
        index.elapsedMilliseconds = math.max(0, nowMilliseconds() - startedAt)
    end
    if index.itemCount == 0 then
        warn("[IrisBrowserItemIndex] no usable item was indexed")
        return failed(index, startedAt, "item_collection_unusable")
    end
    debug("[IrisBrowserItemIndex] Built " .. tostring(index.itemCount) .. " items, errors=" .. tostring(index.errorCount))
    return index
end

return IrisBrowserItemIndex
