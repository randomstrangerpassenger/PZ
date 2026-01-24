--[[
    IrisContextMenu.lua - 우클릭 메뉴 엔트리
    
    우클릭 메뉴에 "Iris: 더보기" 추가.
    클릭 시 위키 패널 오픈.
]]

local IrisContextMenu = {}

-- 의존성
local IrisWikiPanel = require "Iris/UI/Wiki/IrisWikiPanel"

--- 컨텍스트 메뉴에 Iris 엔트리 추가
--- @param player number
--- @param context ISContextMenu
--- @param items table
function IrisContextMenu.addMenuEntry(player, context, items)
    -- 아이템 확인
    local item = nil
    for _, v in ipairs(items) do
        if instanceof(v, "InventoryItem") then
            item = v
            break
        elseif type(v) == "table" and v.items then
            for _, subItem in ipairs(v.items) do
                if instanceof(subItem, "InventoryItem") then
                    item = subItem
                    break
                end
            end
        end
    end
    
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
    
    if Events and Events.OnFillInventoryObjectContextMenu then
        print("[Iris] OnFillInventoryObjectContextMenu exists - registering...")
        Events.OnFillInventoryObjectContextMenu.Add(IrisContextMenu.addMenuEntry)
        print("[Iris] Context menu hook registered successfully")
    else
        print("[Iris] WARNING: Events.OnFillInventoryObjectContextMenu is nil")
    end
end

return IrisContextMenu

