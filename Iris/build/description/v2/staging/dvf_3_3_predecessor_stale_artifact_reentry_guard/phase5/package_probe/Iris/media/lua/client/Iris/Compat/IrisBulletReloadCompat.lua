--[[
    IrisBulletReloadCompat.lua - vanilla bullet reload menu compatibility patch

    This module is intentionally separate from IrisContextMenu. It keeps the
    vanilla compatibility monkey patch out of Iris' wiki menu surface.
]]

local IrisBulletReloadCompat = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")

local function safeInvoke(candidate, methodName, ...)
    if not candidate then
        return nil
    end

    local method = candidate[methodName]
    if not method then
        return nil
    end

    local ok, result = ProtectedCall.compat(method, candidate, ...)
    if ok then
        return result
    end

    return nil
end

local function buildAmmoReloadTooltipDescription(item, currentAmmoCount, maxAmmoCount)
    local lines = {}
    local itemDisplayName = safeInvoke(item, "getDisplayName")
    if itemDisplayName then
        table.insert(lines, getText("ContextMenu_Magazine") .. ": " .. getText(itemDisplayName))
    end

    local gunType = safeInvoke(item, "getGunType")
    if gunType then
        local toolItem = InventoryItemFactory.CreateItem(gunType)
        local toolDisplayName = safeInvoke(toolItem, "getDisplayName")
        if toolDisplayName then
            table.insert(lines, getText("ContextMenu_GunType") .. ": " .. getText(toolDisplayName))
        end
    end

    table.insert(
        lines,
        getText("Tooltip_weapon_AmmoCount") .. ": " .. tostring(currentAmmoCount) .. "/" .. tostring(maxAmmoCount)
    )
    return table.concat(lines, "\n")
end

function IrisBulletReloadCompat.install()
    if not ISInventoryPaneContextMenu or ISInventoryPaneContextMenu._irisSafeBulletReloadPatchApplied then
        return true
    end

    ISInventoryPaneContextMenu._irisSafeBulletReloadPatchApplied = true
    ISInventoryPaneContextMenu.doReloadMenuForBullets = function(playerObj, bullet, context)
        local bulletFullType = safeInvoke(bullet, "getFullType")
        if not bulletFullType then
            return
        end

        local inventory = safeInvoke(playerObj, "getInventory")
        local inventoryItems = safeInvoke(inventory, "getItems")
        local itemCount = safeInvoke(inventoryItems, "size")
        if type(itemCount) ~= "number" then
            return
        end

        for i = 0, itemCount - 1 do
            local item = safeInvoke(inventoryItems, "get", i)
            if item then
                local itemAmmoType = safeInvoke(item, "getAmmoType")
                if itemAmmoType == bulletFullType then
                    if not instanceof(item, "HandWeapon") then
                        local currentAmmoCount = safeInvoke(item, "getCurrentAmmoCount") or 0
                        local maxAmmoCount = safeInvoke(item, "getMaxAmmo") or 0
                        if currentAmmoCount < maxAmmoCount then
                            local ammoCount = safeInvoke(inventory, "getItemCountRecurse", itemAmmoType) or 0
                            if ammoCount > maxAmmoCount then
                                ammoCount = maxAmmoCount
                            end
                            if ammoCount > maxAmmoCount - currentAmmoCount then
                                ammoCount = maxAmmoCount - currentAmmoCount
                            end
                            local insertOption = context:addOption(
                                getText("ContextMenu_InsertBulletsInMagazine", ammoCount),
                                playerObj,
                                ISInventoryPaneContextMenu.onLoadBulletsInMagazine,
                                item,
                                ammoCount
                            )
                            local tooltip = ISInventoryPaneContextMenu.addToolTip()
                            tooltip.description = buildAmmoReloadTooltipDescription(
                                item,
                                currentAmmoCount,
                                maxAmmoCount
                            )
                            insertOption.toolTip = tooltip
                        end
                    else
                        local magazineType = safeInvoke(item, "getMagazineType")
                        if not magazineType then
                            ISInventoryPaneContextMenu.doBulletMenu(playerObj, item, context)
                        end
                    end
                end
            end
        end
    end

    return true
end

return IrisBulletReloadCompat
