--[[
    IrisWikiPanel.lua - 위키 패널 (읽기 전용)
    
    중립적 정보 표시 (평가/추천/우선순위 금지).
    섹션: 태그 / 근거 / 연결 / 필드
]]

local IrisWikiPanel = {}

-- 의존성
local IrisWikiSections = require "Iris/UI/Wiki/IrisWikiSections"
local DetailViewModel = require("Iris/UI/Detail/IrisItemDetailViewModel")
local TextLayout = require("Iris/UI/Detail/IrisTextLayout")

local function addWrappedLabels(panel, text, x, yOffset, lineHeight, r, g, b, font, rightPadding)
    local width = math.max(1, panel.width - x - (rightPadding or 10))
    for _, line in ipairs(TextLayout.wrapLines(text, width, font)) do
        if line == "" then
            yOffset = yOffset + math.max(4, math.floor(lineHeight * 0.55))
        else
            local label = ISLabel:new(x, yOffset, lineHeight, line, r, g, b, 1, font, true)
            panel:addChild(label)
            yOffset = yOffset + lineHeight
        end
    end
    return yOffset
end

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
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local screenW = getCore():getScreenWidth()
    local screenH = getCore():getScreenHeight()
    local panelW = math.min(400, math.max(1, screenW - 20))
    local panelH = math.min(500, math.max(1, screenH - 20))
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
    panel.detailModel = model
    
    -- 제목
    local itemName = model.displayName or model.fullType or "Unknown"
    addWrappedLabels(panel, "Iris: " .. itemName, 10, 10, 25, 1, 1, 1,
        UIFont.Medium, 45)
    
    -- 닫기 버튼
    local closeBtn = ISButton:new(panelW - 30, 5, 25, 25, "X", panel, function()
        panel:close()
    end)
    closeBtn:initialise()
    panel:addChild(closeBtn)
    
    -- 섹션 렌더링
    local yOffset = 45
    
    -- A) 태그 목록
    local tagsSection = IrisWikiSections.renderTagsSection(model)
    if tagsSection then
        yOffset = addWrappedLabels(panel, tagsSection, 10, yOffset, 18,
            1, 1, 1, UIFont.Small) + 7
    end

    -- B.25) 3계층 본문
    local layer3Section = IrisWikiSections.renderLayer3Section(model)
    if layer3Section then
        yOffset = addWrappedLabels(panel, layer3Section, 10, yOffset, 18,
            0.9, 0.9, 0.9, UIFont.Small) + 7
    end
    
    local literatureSection = IrisWikiSections.renderLiteratureSection(model)
    if literatureSection then
        yOffset = addWrappedLabels(panel, literatureSection, 10, yOffset, 18,
            0.9, 0.9, 0.9, UIFont.Small) + 7
    end

    -- B.5) UseCase (빌드 산출물 표시 전용)
    local usecaseSection = IrisWikiSections.renderUseCaseSection(model)
    if usecaseSection then
        yOffset = addWrappedLabels(panel, usecaseSection, 10, yOffset, 18,
            0.9, 0.95, 0.8, UIFont.Small) + 7
    end
    
    -- C) 연결 시스템
    local connectionSection = IrisWikiSections.renderConnectionSection(model)
    if connectionSection then
        yOffset = addWrappedLabels(panel, connectionSection, 10, yOffset, 18,
            1, 1, 1, UIFont.Small) + 7
    end
    
    -- D) 상태 필드
    local fieldsSection = IrisWikiSections.renderFieldsSection(model)
    if fieldsSection then
        addWrappedLabels(panel, fieldsSection, 10, yOffset, 18,
            1, 1, 1, UIFont.Small)
    end
    
    -- 닫기 함수
    panel.close = function(self)
        self:setVisible(false)
        self:removeFromUIManager()
    end
    
    return panel
end

return IrisWikiPanel
