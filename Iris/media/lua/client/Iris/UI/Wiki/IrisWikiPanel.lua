--[[
    IrisWikiPanel.lua - 위키 패널 (읽기 전용)
    
    중립적 정보 표시 (평가/추천/우선순위 금지).
    섹션: 태그 / 근거 / 연결 / 필드
]]

local IrisWikiPanel = {}

-- 의존성
local IrisWikiSections = require "Iris/UI/Wiki/IrisWikiSections"

-- 패널 인스턴스
IrisWikiPanel._panel = nil

--- 위키 패널 열기
--- @param item InventoryItem
function IrisWikiPanel.open(item)
    if not item then
        return
    end
    
    -- 기존 패널 닫기
    if IrisWikiPanel._panel and IrisWikiPanel._panel:isVisible() then
        IrisWikiPanel._panel:close()
    end
    
    -- 새 패널 생성
    local panel = IrisWikiPanel.createPanel(item)
    panel:addToUIManager()
    panel:setVisible(true)
    IrisWikiPanel._panel = panel
end

--- 위키 패널 열기 (API 명세용 별칭)
--- 브라우저 경유 없이 즉시 위키 표시
--- @param item InventoryItem
function IrisWikiPanel.openForItem(item)
    IrisWikiPanel.open(item)
end

--- 패널 UI 생성
--- @param item InventoryItem
--- @return ISPanel
function IrisWikiPanel.createPanel(item)
    local screenW = getCore():getScreenWidth()
    local screenH = getCore():getScreenHeight()
    local panelW = 400
    local panelH = 500
    local x = (screenW - panelW) / 2
    local y = (screenH - panelH) / 2
    
    local panel = ISPanel:new(x, y, panelW, panelH)
    panel:initialise()
    panel:setAnchorLeft(true)
    panel:setAnchorTop(true)
    panel:setAnchorRight(false)
    panel:setAnchorBottom(false)
    panel.backgroundColor = {r=0.1, g=0.1, b=0.1, a=0.9}
    panel.borderColor = {r=0.4, g=0.4, b=0.4, a=1}
    panel.moveWithMouse = true
    
    -- 제목
    local itemName = item:getDisplayName() or item:getFullType()
    local titleLabel = ISLabel:new(10, 10, 25, "Iris: " .. itemName, 1, 1, 1, 1, UIFont.Medium, true)
    panel:addChild(titleLabel)
    
    -- 닫기 버튼
    local closeBtn = ISButton:new(panelW - 30, 5, 25, 25, "X", panel, function()
        panel:close()
    end)
    closeBtn:initialise()
    panel:addChild(closeBtn)
    
    -- 섹션 렌더링
    local yOffset = 45
    
    -- A) 태그 목록
    local tagsSection = IrisWikiSections.renderTagsSection(item)
    local tagsLabel = ISLabel:new(10, yOffset, 20, tagsSection, 1, 1, 1, 1, UIFont.Small, true)
    panel:addChild(tagsLabel)
    yOffset = yOffset + 25
    
    -- B) 근거
    local reasonSection = IrisWikiSections.renderReasonSection(item)
    local reasonLabel = ISLabel:new(10, yOffset, 20, reasonSection, 0.8, 0.8, 0.8, 1, UIFont.Small, true)
    panel:addChild(reasonLabel)
    yOffset = yOffset + 25
    
    -- B.5) UseCase (빌드 산출물 표시 전용)
    local usecaseSection = IrisWikiSections.renderUseCaseSection(item)
    if usecaseSection then
        local usecaseLabel = ISLabel:new(10, yOffset, 20, usecaseSection, 0.9, 0.95, 0.8, 1, UIFont.Small, true)
        panel:addChild(usecaseLabel)
        yOffset = yOffset + 25
    end
    
    -- C) 연결 시스템
    local connectionSection = IrisWikiSections.renderConnectionSection(item)
    local connectionLabel = ISLabel:new(10, yOffset, 20, connectionSection, 1, 1, 1, 1, UIFont.Small, true)
    panel:addChild(connectionLabel)
    yOffset = yOffset + 25
    
    -- D) 상태 필드
    local fieldsSection = IrisWikiSections.renderFieldsSection(item)
    local fieldsLabel = ISLabel:new(10, yOffset, 20, fieldsSection, 1, 1, 1, 1, UIFont.Small, true)
    panel:addChild(fieldsLabel)
    
    -- 닫기 함수
    panel.close = function(self)
        self:setVisible(false)
        self:removeFromUIManager()
    end
    
    return panel
end

return IrisWikiPanel
