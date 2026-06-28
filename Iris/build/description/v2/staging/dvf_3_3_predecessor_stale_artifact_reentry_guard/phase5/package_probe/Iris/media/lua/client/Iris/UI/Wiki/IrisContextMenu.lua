--[[
    IrisContextMenu.lua - 우클릭 메뉴 엔트리
    
    우클릭 메뉴에 Iris_Menu_ViewMore 엔트리 추가.
    클릭 시 위키 패널 오픈.
]]

local IrisContextMenu = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local ObjectAccess = require("Iris/Util/IrisObjectAccess")
local debug = bootstrap.debug
local warn = bootstrap.warn
local logError = bootstrap.logError

local tr = TranslationResolver.get

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
        local sizeOk, size = ObjectAccess.call(container, "size")
        if sizeOk and type(size) == "number" and size > 0 then
            local getOk, value = ObjectAccess.call(container, "get", 0)
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
        local itemsOk, nestedItems = ObjectAccess.call(candidate, "getItems")
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
        local sizeOk, size = ObjectAccess.call(items, "size")
        if sizeOk and type(size) == "number" and size > 0 then
            for i = 0, size - 1 do
                local getOk, value = ObjectAccess.call(items, "get", i)
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

--- 컨텍스트 메뉴에 Iris 엔트리 추가
--- @param player number
--- @param context ISContextMenu
--- @param items table
function IrisContextMenu.addMenuEntry(player, context, items)
    local item = resolveFirstInventoryItem(items)
    if not item then
        return
    end
    
    context:addOption(tr("Iris_Menu_ViewMore", "Iris: View More"), item, function(selectedItem)
        -- IrisBrowser 동적 로드 및 호출
        local browserOk, IrisBrowser = safeRequire("Iris/UI/Browser/IrisBrowser")
        if browserOk and IrisBrowser then
            IrisBrowser.openForItem(selectedItem)
        else
            logError("[IrisContextMenu] Failed to load IrisBrowser")
            -- 실패 시 WikiPanel로 대체 (안전장치)
            IrisWikiPanel.openForItem(selectedItem)
        end
    end)
end

--- 이벤트 훅 등록
function IrisContextMenu.hookContextMenu()
    debug("[Iris] hookContextMenu() called")
    
    if Events and Events.OnFillInventoryObjectContextMenu then
        debug("[Iris] OnFillInventoryObjectContextMenu exists - registering...")
        Events.OnFillInventoryObjectContextMenu.Add(IrisContextMenu.addMenuEntry)
        debug("[Iris] Context menu hook registered successfully")
    else
        warn("[Iris] Events.OnFillInventoryObjectContextMenu is nil")
    end
end

return IrisContextMenu

