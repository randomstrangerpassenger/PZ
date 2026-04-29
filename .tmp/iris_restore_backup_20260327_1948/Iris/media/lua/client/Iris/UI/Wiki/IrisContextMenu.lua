local IrisContextMenu = {}

local function unwrapInventoryItem(entry)
    if not entry then
        return nil
    end
    if instanceof(entry, "InventoryItem") then
        return entry
    end
    if type(entry) == "table" then
        if entry.items and entry.items[1] then
            return unwrapInventoryItem(entry.items[1])
        end
        if entry[1] then
            return unwrapInventoryItem(entry[1])
        end
    end
    return nil
end

function IrisContextMenu.onFillInventoryObjectContextMenu(playerIndex, context, items)
    if not items or not context then
        return
    end

    local item = unwrapInventoryItem(items[1])
    if not item or not item.getFullType then
        return
    end

    local browserOk, IrisBrowser = pcall(require, "Iris/UI/Browser/IrisBrowser")
    if not browserOk or not IrisBrowser then
        print("[IrisContextMenu] FAILED to load IrisBrowser")
        return
    end

    local bridgeOk, IrisDvfBridge = pcall(require, "Iris/IrisDvfBridge")
    if not bridgeOk or not IrisDvfBridge then
        print("[IrisContextMenu] FAILED to load IrisDvfBridge")
        return
    end

    local itemId = item:getFullType()
    if not IrisDvfBridge.hasItem(itemId) then
        return
    end

    context:addOption("Iris Wiki", item, function(selectedItem)
        IrisBrowser.showItem(selectedItem:getFullType())
    end)
end

Events.OnFillInventoryObjectContextMenu.Add(IrisContextMenu.onFillInventoryObjectContextMenu)

return IrisContextMenu
