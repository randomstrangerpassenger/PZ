--[[
    IrisAltTooltip.lua - Iris 툴팁 오버레이
    
    동작 방식:
    1. 항상: "[Iris]" 라벨이 툴팁에 표시 (Alt 불필요)
    2. Alt 키 누름: "[Iris]" 아래에 상세 정보 표시
    
    ISToolTipInv 구조:
    - self.item: InventoryItem
    - self.tooltip: ObjectTooltip (실제 렌더링 담당)
]]

local IrisAltTooltip = {}

-- Alt 키코드 상수 (LWJGL 키보드 코드)
local KEY_LALT = 56
local KEY_RALT = 184

--- Alt 키 눌림 상태 확인
local function isAltPressed()
    if not isKeyDown then 
        return false 
    end
    local leftAlt = isKeyDown(KEY_LALT)
    local rightAlt = isKeyDown(KEY_RALT)
    return leftAlt or rightAlt
end

--- 아이템 툴팁에 Iris 정보 추가
--- @param tooltipInv ISToolTipInv
function IrisAltTooltip.addIrisOverlay(tooltipInv)
    -- 중복 삽입 가드
    if tooltipInv._irisRendered then
        return
    end
    tooltipInv._irisRendered = true
    
    local lineHeight = 16
    local x = 10
    local startY = tooltipInv.height
    
    -- 항상 표시되는 기본 라벨
    local baseLabel = "[Iris]"
    
    -- Alt 누름 상태에 따른 상세 정보
    local isAlt = isAltPressed()
    local detailLines = {}
    if isAlt and tooltipInv.item then
        -- IrisAPI에서 실제 태그 가져오기
        local IrisAPI = nil
        local ok, result = pcall(require, "Iris/IrisAPI")
        if ok then IrisAPI = result end
        
        if IrisAPI then
            -- 태그 라인 (최대 4줄 중 1줄)
            local tags = IrisAPI.getTagsForItem(tooltipInv.item) or {}
            local tagList = {}
            for tag, _ in pairs(tags) do
                table.insert(tagList, tag)
            end
            table.sort(tagList)
            
            if #tagList > 0 then
                local tagStr = table.concat(tagList, ", ")
                -- 너무 길면 자르기
                if #tagStr > 50 then
                    tagStr = tagStr:sub(1, 47) .. "..."
                end
                table.insert(detailLines, "태그: " .. tagStr)
            else
                table.insert(detailLines, "태그: (없음)")
            end
            
            -- 연결 라인 (최대 4줄 중 2줄)
            local recipeInfo = IrisAPI.getRecipeConnectionsForItem(tooltipInv.item) or {}
            local moveInfo = IrisAPI.getMoveablesInfoForItem(tooltipInv.item) or {}
            local fixInfo = IrisAPI.getFixingInfoForItem(tooltipInv.item) or {}
            
            local connections = {}
            if #recipeInfo > 0 then table.insert(connections, "Recipe") end
            if moveInfo.itemId_registered or moveInfo.moveablesTag then table.insert(connections, "Moveables") end
            if fixInfo.isFixer then table.insert(connections, "Fixing") end
            
            if #connections > 0 then
                table.insert(detailLines, "연결: " .. table.concat(connections, ", "))
            else
                table.insert(detailLines, "연결: 없음")
            end
            
            -- 더보기 안내 (최대 4줄 중 3줄)
            table.insert(detailLines, "더보기: 우클릭 > Iris")
        else
            detailLines = {
                "태그: (API 로드 실패)",
                "더보기: 우클릭 > Iris",
            }
        end
    end
    
    -- 전체 높이 계산
    local totalLines = 1 + #detailLines  -- "[Iris]" + 상세 정보
    local irisHeight = (lineHeight * totalLines) + 8
    
    -- 배경 색상 (어두운 시안)
    local bgR, bgG, bgB, bgA = 0.05, 0.15, 0.2, 0.9
    -- 라벨 색상 (밝은 시안)
    local labelR, labelG, labelB, labelA = 0.4, 0.8, 1.0, 1.0
    -- 상세 텍스트 색상 (밝은 회색)
    local txtR, txtG, txtB, txtA = 0.8, 0.9, 0.9, 1.0
    
    -- 배경 박스 그리기
    tooltipInv:drawRect(0, startY, tooltipInv.width, irisHeight, bgA, bgR, bgG, bgB)
    tooltipInv:drawRectBorder(0, startY, tooltipInv.width, irisHeight, 0.8, 0.4, 0.6, 0.7)
    
    -- "[Iris]" 라벨 (항상 표시)
    local currentY = startY + 4
    tooltipInv:drawText(baseLabel, x, currentY, labelR, labelG, labelB, labelA, UIFont.Small)
    currentY = currentY + lineHeight
    
    -- 상세 정보 (Alt 눌렀을 때만)
    for _, line in ipairs(detailLines) do
        tooltipInv:drawText("  " .. line, x, currentY, txtR, txtG, txtB, txtA, UIFont.Small)
        currentY = currentY + lineHeight
    end
    
    -- 높이 조정
    tooltipInv:setHeight(tooltipInv.height + irisHeight)
end

--- ISToolTipInv.render 후킹
local originalRender = nil
local hooked = false

function IrisAltTooltip.hookTooltip()
    print("[Iris:hookTooltip] === Starting tooltip hook ===")
    
    if hooked then
        print("[Iris:hookTooltip] Already hooked, skipping")
        return
    end
    
    if not ISToolTipInv then
        print("[Iris:hookTooltip] ERROR: ISToolTipInv is nil")
        return
    end
    
    if not ISToolTipInv.render then
        print("[Iris:hookTooltip] ERROR: ISToolTipInv.render is nil")
        return
    end
    
    print("[Iris:hookTooltip] ISToolTipInv.render found - hooking...")
    originalRender = ISToolTipInv.render
    
    ISToolTipInv.render = function(self)
        -- 매 프레임마다 플래그 리셋
        self._irisRendered = nil
        
        -- 원본 렌더 먼저
        originalRender(self)
        
        -- Iris 오버레이 추가 (항상, Alt 상태에 따라 상세 정보 추가)
        if self.item then
            IrisAltTooltip.addIrisOverlay(self)
        end
    end
    
    hooked = true
    print("[Iris:hookTooltip] SUCCESS: ISToolTipInv.render hooked!")
end

return IrisAltTooltip
