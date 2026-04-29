local ok, payload = pcall(require, "Iris/IrisDvfBridgeData")

local data
if ok and type(payload) == "table" then
    data = payload
else
    print("[Iris] DVF bridge data missing or failed to load: " .. tostring(payload))
    data = {
        meta = {
            version = "missing-bridge-data",
        },
        entries = {},
    }
end

IrisDvfBridge = IrisDvfBridge or {}

local itemIds = nil

local function rebuildIndex()
    itemIds = {}
    for itemId, _ in pairs(data.entries or {}) do
        table.insert(itemIds, itemId)
    end
    table.sort(itemIds)
end

function IrisDvfBridge.getMeta()
    return data.meta
end

function IrisDvfBridge.getEntry(itemId)
    if not itemId then
        return nil
    end
    return (data.entries or {})[itemId]
end

function IrisDvfBridge.getText(itemId)
    local entry = IrisDvfBridge.getEntry(itemId)
    return entry and entry.text_ko or nil
end

function IrisDvfBridge.hasItem(itemId)
    return IrisDvfBridge.getEntry(itemId) ~= nil
end

function IrisDvfBridge.getEntryCount()
    return itemIds and #itemIds or 0
end

function IrisDvfBridge.listItemIds()
    if not itemIds then
        rebuildIndex()
    end

    local copy = {}
    for i = 1, #itemIds do
        copy[i] = itemIds[i]
    end
    return copy
end

rebuildIndex()

return IrisDvfBridge
