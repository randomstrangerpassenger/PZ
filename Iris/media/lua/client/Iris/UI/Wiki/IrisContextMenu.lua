--[[
    IrisContextMenu.lua - 우클릭 메뉴 엔트리
    
    우클릭 메뉴에 "Iris: 더보기" 추가.
    클릭 시 위키 패널 오픈.
]]

local IrisContextMenu = {}

-- 의존성
local IrisWikiPanel = require "Iris/UI/Wiki/IrisWikiPanel"

local function resolveIndexedContainerItem(container)
    if not container then
        return nil
    end

    if type(container) == "table" then
        return container[1]
    end

    local sizeMethod = container.size
    local getMethod = container.get
    if sizeMethod and getMethod then
        local sizeOk, size = pcall(function()
            return container:size()
        end)
        if sizeOk and type(size) == "number" and size > 0 then
            local getOk, value = pcall(function()
                return container:get(0)
            end)
            if getOk then
                return value
            end
        end
    end

    return nil
end

local function tryResolveInventoryItem(candidate)
    if not candidate then
        return nil
    end

    if instanceof(candidate, "InventoryItem") then
        return candidate
    end

    local stackItems = candidate.items
    local firstStackItem = resolveIndexedContainerItem(stackItems)
    if firstStackItem then
        local resolved = tryResolveInventoryItem(firstStackItem)
        if resolved then
            return resolved
        end
    end

    local getItems = candidate.getItems
    if getItems then
        local itemsOk, nestedItems = pcall(function()
            return candidate:getItems()
        end)
        if itemsOk and nestedItems then
            local firstNestedItem = resolveIndexedContainerItem(nestedItems)
            if firstNestedItem then
                local resolved = tryResolveInventoryItem(firstNestedItem)
                if resolved then
                    return resolved
                end
            end
        end
    end

    return nil
end

local function resolveFirstInventoryItem(items)
    if not items then
        return nil
    end

    local directItem = tryResolveInventoryItem(items)
    if directItem then
        return directItem
    end

    for _, v in ipairs(items) do
        local resolved = tryResolveInventoryItem(v)
        if resolved then
            return resolved
        end
    end

    local sizeMethod = items.size
    local getMethod = items.get
    if sizeMethod and getMethod then
        local sizeOk, size = pcall(function()
            return items:size()
        end)
        if sizeOk and type(size) == "number" and size > 0 then
            for i = 0, size - 1 do
                local getOk, value = pcall(function()
                    return items:get(i)
                end)
                if getOk then
                    local resolved = tryResolveInventoryItem(value)
                    if resolved then
                        return resolved
                    end
                end
            end
        end
    end

    return nil
end

local function safeInvoke(candidate, methodName, ...)
    if not candidate then
        return nil
    end

    local method = candidate[methodName]
    if not method then
        return nil
    end

    local ok, result = pcall(method, candidate, ...)
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

local function patchVanillaBulletReloadMenu()
    if not ISInventoryPaneContextMenu or ISInventoryPaneContextMenu._irisSafeBulletReloadPatchApplied then
        return
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
end

--- 컨텍스트 메뉴에 Iris 엔트리 추가
--- @param player number
--- @param context ISContextMenu
--- @param items table
function IrisContextMenu.addMenuEntry(player, context, items)
    local item = resolveFirstInventoryItem(items)
    if not item then
        return
    end
    
    -- "Iris: View More" 메뉴 추가
    context:addOption("Iris: View More", item, function(selectedItem)
        -- IrisBrowser 동적 로드 및 호출
        local browserOk, IrisBrowser = pcall(require, "Iris/UI/Browser/IrisBrowser")
        if browserOk and IrisBrowser then
            IrisBrowser.openForItem(selectedItem)
        else
            print("[IrisContextMenu] FAILED to load IrisBrowser")
            -- 실패 시 WikiPanel로 대체 (안전장치)
            IrisWikiPanel.openForItem(selectedItem)
        end
    end)
end

--- 이벤트 훅 등록
function IrisContextMenu.hookContextMenu()
    print("[Iris] hookContextMenu() called")

    patchVanillaBulletReloadMenu()
    
    if Events and Events.OnFillInventoryObjectContextMenu then
        print("[Iris] OnFillInventoryObjectContextMenu exists - registering...")
        Events.OnFillInventoryObjectContextMenu.Add(IrisContextMenu.addMenuEntry)
        print("[Iris] Context menu hook registered successfully")
    else
        print("[Iris] WARNING: Events.OnFillInventoryObjectContextMenu is nil")
    end
end

return IrisContextMenu

