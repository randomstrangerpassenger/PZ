--[[
    IrisBrowser.lua - Iris 카테고리 브라우저 메인 UI
    
    4열 레이아웃:
    - 대분류 (15%) → 소분류 (15%) → 아이템 (15%) → 설명 (55%)
    
    진입점:
    - IrisBrowser.openSearch() → 빈 상태의 검색 초기 화면
]]

require "ISUI/ISPanel"
require "ISUI/ISScrollingListBox"
require "ISUI/ISTextEntryBox"
require "ISUI/ISButton"
require "ISUI/ISLabel"

local IrisBrowser = ISPanel:derive("IrisBrowser")

-- 의존성 (lazy load)
local IrisBrowserData = nil
local IrisWikiSections = nil

local function ensureDeps()
    if not IrisBrowserData then
        local ok, result = pcall(require, "Iris/UI/Browser/IrisBrowserData")
        if ok then IrisBrowserData = result end
    end
    if not IrisWikiSections then
        local ok, result = pcall(require, "Iris/UI/Wiki/IrisWikiSections")
        if ok then IrisWikiSections = result end
    end
end

-- 싱글톤 인스턴스
IrisBrowser._instance = nil

-- 칸 크기 비율
local COL_CATEGORY = 0.15
local COL_SUBCATEGORY = 0.15
local COL_ITEMS = 0.15
local COL_DETAIL = 0.55

--- 브라우저 열기 (검색 초기 화면)
function IrisBrowser.openSearch()
    ensureDeps()
    
    -- 데이터 빌드 확인
    if IrisBrowserData and not IrisBrowserData._built then
        IrisBrowserData.build()
    end
    
    -- 기존 인스턴스 닫기
    if IrisBrowser._instance and IrisBrowser._instance:isVisible() then
        IrisBrowser._instance:close()
    end
    
    -- 새 인스턴스 생성
    local screenW = getCore():getScreenWidth()
    local screenH = getCore():getScreenHeight()
    local panelW = math.min(1200, screenW - 100)
    local panelH = math.min(700, screenH - 100)
    local x = (screenW - panelW) / 2
    local y = (screenH - panelH) / 2
    
    local browser = IrisBrowser:new(x, y, panelW, panelH)
    browser:initialise()
    browser:instantiate()
    browser:addToUIManager()
    browser:setVisible(true)
    browser:bringToTop()
    
    IrisBrowser._instance = browser
    print("[IrisBrowser] Opened in search mode")
end

--- 특정 아이템으로 브라우저 열기
--- @param item InventoryItem
function IrisBrowser.openForItem(item)
    ensureDeps()
    
    if not item then return end
    
    -- 데이터 빌드 확인
    if IrisBrowserData and not IrisBrowserData._built then
        IrisBrowserData.build()
    end
    
    -- 기존 인스턴스 닫기
    if IrisBrowser._instance and IrisBrowser._instance:isVisible() then
        IrisBrowser._instance:close()
    end
    
    -- 새 인스턴스 생성
    local screenW = getCore():getScreenWidth()
    local screenH = getCore():getScreenHeight()
    local panelW = math.min(1200, screenW - 100)
    local panelH = math.min(700, screenH - 100)
    local x = (screenW - panelW) / 2
    local y = (screenH - panelH) / 2
    
    local browser = IrisBrowser:new(x, y, panelW, panelH)
    browser:initialise()
    browser:instantiate()
    browser:addToUIManager()
    browser:setVisible(true)
    browser:bringToTop()
    
    -- 해당 아이템 찾기 및 선택
    browser:selectItem(item)
    
    IrisBrowser._instance = browser
    print("[IrisBrowser] Opened for item: " .. tostring(item:getFullType()))
end

--- 생성자
function IrisBrowser:new(x, y, width, height)
    local o = ISPanel:new(x, y, width, height)
    setmetatable(o, self)
    self.__index = self
    
    o.backgroundColor = {r=0.1, g=0.1, b=0.12, a=0.95}
    o.borderColor = {r=0.3, g=0.4, b=0.5, a=1}
    o.moveWithMouse = true
    
    -- 상태 (SSOT)
    o.currentCategory = nil
    o.currentSubcategory = nil
    o.currentSelectedFullType = nil  -- SSOT: 하나만 유지
    
    return o
end

--- 초기화
function IrisBrowser:initialise()
    ISPanel.initialise(self)
end

--- UI 생성
function IrisBrowser:createChildren()
    ISPanel.createChildren(self)
    
    local headerHeight = 40
    local listTop = headerHeight + 10
    local listHeight = self.height - listTop - 10
    
    -- 열 너비 계산
    local colCatW = self.width * COL_CATEGORY
    local colSubW = self.width * COL_SUBCATEGORY
    local colItemW = self.width * COL_ITEMS
    local colDetailW = self.width * COL_DETAIL
    
    local col1X = 5
    local col2X = col1X + colCatW + 5
    local col3X = col2X + colSubW + 5
    local col4X = col3X + colItemW + 5
    
    -- === 헤더 영역 ===
    
    -- 타이틀
    self.titleLabel = ISLabel:new(10, 10, 25, "Iris Browser", 0.6, 0.9, 1.0, 1.0, UIFont.Medium, true)
    self:addChild(self.titleLabel)
    
    -- 전체 검색창
    self.searchBar = ISTextEntryBox:new("", col4X, 8, colDetailW - 40, 24)
    self.searchBar:initialise()
    self.searchBar:instantiate()
    self.searchBar.onTextChange = function()
        self:onGlobalSearchChange()
    end
    self:addChild(self.searchBar)
    
    -- 닫기 버튼
    self.closeBtn = ISButton:new(self.width - 30, 5, 25, 25, "X", self, self.close)
    self.closeBtn:initialise()
    self.closeBtn.borderColor = {r=0.5, g=0.5, b=0.5, a=0.5}
    self:addChild(self.closeBtn)
    
    -- === 대분류 열 ===
    self.categoryLabel = ISLabel:new(col1X, listTop - 18, 16, "대분류", 0.7, 0.7, 0.7, 1, UIFont.Small, true)
    self:addChild(self.categoryLabel)
    
    self.categoryList = ISScrollingListBox:new(col1X, listTop, colCatW - 5, listHeight)
    self.categoryList:initialise()
    self.categoryList:instantiate()
    self.categoryList.onmousedown = function(list, item)
        self:onCategorySelected(item)
    end
    self.categoryList.font = UIFont.Small
    self.categoryList.fontHgt = getTextManager():getFontHeight(UIFont.Small)
    self.categoryList.itemheight = self.categoryList.fontHgt + 4
    self:addChild(self.categoryList)
    
    -- === 소분류 열 ===
    self.subcategoryLabel = ISLabel:new(col2X, listTop - 18, 16, "소분류", 0.7, 0.7, 0.7, 1, UIFont.Small, true)
    self:addChild(self.subcategoryLabel)
    
    self.subcategorySearchBar = ISTextEntryBox:new("", col2X, listTop, colSubW - 5, 20)
    self.subcategorySearchBar:initialise()
    self.subcategorySearchBar:instantiate()
    self.subcategorySearchBar.onTextChange = function()
        self:onSubcategorySearchChange()
    end
    self:addChild(self.subcategorySearchBar)
    
    self.subcategoryList = ISScrollingListBox:new(col2X, listTop + 25, colSubW - 5, listHeight - 25)
    self.subcategoryList:initialise()
    self.subcategoryList:instantiate()
    self.subcategoryList.onmousedown = function(list, item)
        self:onSubcategorySelected(item)
    end
    self.subcategoryList.font = UIFont.Small
    self.subcategoryList.fontHgt = getTextManager():getFontHeight(UIFont.Small)
    self.subcategoryList.itemheight = self.subcategoryList.fontHgt + 4
    self:addChild(self.subcategoryList)
    
    -- === 아이템 열 ===
    self.itemLabel = ISLabel:new(col3X, listTop - 18, 16, "아이템", 0.7, 0.7, 0.7, 1, UIFont.Small, true)
    self:addChild(self.itemLabel)
    
    self.itemSearchBar = ISTextEntryBox:new("", col3X, listTop, colItemW - 5, 20)
    self.itemSearchBar:initialise()
    self.itemSearchBar:instantiate()
    self.itemSearchBar.onTextChange = function()
        self:onItemSearchChange()
    end
    self:addChild(self.itemSearchBar)
    
    self.itemList = ISScrollingListBox:new(col3X, listTop + 25, colItemW - 5, listHeight - 25)
    self.itemList:initialise()
    self.itemList:instantiate()
    self.itemList.onmousedown = function(list, item)
        self:onItemSelected(item)
    end
    self.itemList.font = UIFont.Small
    self.itemList.fontHgt = getTextManager():getFontHeight(UIFont.Small)
    self.itemList.itemheight = self.itemList.fontHgt + 4
    self:addChild(self.itemList)
    
    -- === 상세 정보 열 ===
    self.detailLabel = ISLabel:new(col4X, listTop - 18, 16, "아이템 정보", 0.7, 0.7, 0.7, 1, UIFont.Small, true)
    self:addChild(self.detailLabel)
    
    self.detailPanel = ISPanel:new(col4X, listTop, colDetailW - 10, listHeight)
    self.detailPanel:initialise()
    self.detailPanel.backgroundColor = {r=0.05, g=0.08, b=0.1, a=0.8}
    self.detailPanel.borderColor = {r=0.3, g=0.4, b=0.5, a=0.5}
    self:addChild(self.detailPanel)
    
    -- 초기 데이터 로드
    self:loadCategories()
end

--- 대분류 로드
function IrisBrowser:loadCategories()
    self.categoryList:clear()
    
    ensureDeps()
    if not IrisBrowserData then return end
    
    local categories = IrisBrowserData.getCategories()
    for _, cat in ipairs(categories) do
        self.categoryList:addItem(cat.name, cat)
    end
end

--- 소분류 로드
function IrisBrowser:loadSubcategories(categoryName)
    self.subcategoryList:clear()
    
    ensureDeps()
    if not IrisBrowserData or not categoryName then return end
    
    local subcategories = IrisBrowserData.getSubcategories(categoryName)
    local filterText = self.subcategorySearchBar:getText():lower()
    
    for _, sub in ipairs(subcategories) do
        -- 검색 필터 적용 (코드와 라벨 둘 다 검색 가능)
        local labelLower = (sub.label or sub.name):lower()
        local codeLower = sub.name:lower()
        if filterText == "" or labelLower:find(filterText, 1, true) or codeLower:find(filterText, 1, true) then
            -- 빈 소분류도 (0) 표시 (숨김 금지)
            -- 라벨 형식: "코드 라벨 (개수)" 예: "1-A 건설/제작 (5)"
            local displayLabel = sub.name .. " " .. (sub.label or "") .. " (" .. sub.itemCount .. ")"
            self.subcategoryList:addItem(displayLabel, sub)
        end
    end
end

--- 아이템 로드
function IrisBrowser:loadItems(categoryName, subcategoryName)
    self.itemList:clear()
    
    ensureDeps()
    if not IrisBrowserData or not categoryName or not subcategoryName then return end
    
    local items = IrisBrowserData.getItems(categoryName, subcategoryName)
    local filterText = self.itemSearchBar:getText():lower()
    
    for _, item in ipairs(items) do
        -- 검색 필터 적용
        if filterText == "" or item.displayName:lower():find(filterText, 1, true) then
            self.itemList:addItem(item.displayName, item)
        end
    end
end

--- 상세 정보 표시
function IrisBrowser:showDetail(fullType)
    -- 기존 상세 정보 삭제
    for i = #self.detailPanel:getChildren(), 1, -1 do
        local child = self.detailPanel:getChildren()[i]
        self.detailPanel:removeChild(child)
    end
    
    if not fullType then
        -- placeholder
        local placeholderLabel = ISLabel:new(10, 10, 20, "아이템을 선택하세요", 0.5, 0.5, 0.5, 1, UIFont.Small, true)
        self.detailPanel:addChild(placeholderLabel)
        return
    end
    
    ensureDeps()
    local item = IrisBrowserData and IrisBrowserData.getItem(fullType)
    if not item then
        local errorLabel = ISLabel:new(10, 10, 20, "아이템 정보를 찾을 수 없습니다", 0.8, 0.3, 0.3, 1, UIFont.Small, true)
        self.detailPanel:addChild(errorLabel)
        return
    end
    
    -- IrisWikiSections 사용하여 상세 정보 표시
    local yOffset = 10
    
    -- 아이템 이름
    local displayName = item:getDisplayName() or fullType
    local nameLabel = ISLabel:new(10, yOffset, 25, displayName, 0.6, 0.9, 1.0, 1.0, UIFont.Medium, true)
    self.detailPanel:addChild(nameLabel)
    yOffset = yOffset + 30
    
    -- 태그 섹션
    if IrisWikiSections then
        local tagsText = IrisWikiSections.renderTagsSection(item)
        local tagsLabel = ISLabel:new(10, yOffset, 18, tagsText, 0.9, 0.9, 0.9, 1, UIFont.Small, true)
        self.detailPanel:addChild(tagsLabel)
        yOffset = yOffset + 22
        
        -- 근거 섹션
        local reasonText = IrisWikiSections.renderReasonSection(item)
        local reasonLabel = ISLabel:new(10, yOffset, 18, reasonText, 0.7, 0.7, 0.7, 1, UIFont.Small, true)
        self.detailPanel:addChild(reasonLabel)
        yOffset = yOffset + 22
        
        -- 연결 섹션
        local connectionText = IrisWikiSections.renderConnectionSection(item)
        local connectionLabel = ISLabel:new(10, yOffset, 18, connectionText, 0.9, 0.9, 0.9, 1, UIFont.Small, true)
        self.detailPanel:addChild(connectionLabel)
        yOffset = yOffset + 22
        
        -- 필드 섹션
        local fieldsText = IrisWikiSections.renderFieldsSection(item)
        local fieldsLabel = ISLabel:new(10, yOffset, 18, fieldsText, 0.9, 0.9, 0.9, 1, UIFont.Small, true)
        self.detailPanel:addChild(fieldsLabel)
    end
end

--- 이벤트 핸들러: 대분류 선택
function IrisBrowser:onCategorySelected(item)
    if not item then return end
    local catData = item.item
    if not catData then return end
    
    self.currentCategory = catData.name
    self.currentSubcategory = nil
    self.currentSelectedFullType = nil
    
    self:loadSubcategories(self.currentCategory)
    self.itemList:clear()
    self:showDetail(nil)
end

--- 이벤트 핸들러: 소분류 선택
function IrisBrowser:onSubcategorySelected(item)
    if not item then return end
    local subData = item.item
    if not subData then return end
    
    self.currentSubcategory = subData.name
    self.currentSelectedFullType = nil
    
    self:loadItems(self.currentCategory, self.currentSubcategory)
    self:showDetail(nil)
end

--- 이벤트 핸들러: 아이템 선택
function IrisBrowser:onItemSelected(item)
    if not item then return end
    local itemData = item.item
    if not itemData then return end
    
    -- SSOT: currentSelectedFullType 하나만 유지
    self.currentSelectedFullType = itemData.fullType
    self:showDetail(self.currentSelectedFullType)
end

--- 이벤트 핸들러: 전체 검색
function IrisBrowser:onGlobalSearchChange()
    local query = self.searchBar:getText()
    if query == "" then
        -- 검색어 없으면 일반 모드로 복귀
        self:loadCategories()
        return
    end
    
    ensureDeps()
    if not IrisBrowserData then return end
    
    local results = IrisBrowserData.searchAll(query)
    
    -- 1열/2열 비활성 (검색 모드)
    self.categoryList:clear()
    self.subcategoryList:clear()
    
    -- 3열에 검색 결과 표시
    self.itemList:clear()
    for _, result in ipairs(results) do
        self.itemList:addItem(result.displayName, result)
    end
end

--- 이벤트 핸들러: 소분류 검색
function IrisBrowser:onSubcategorySearchChange()
    if self.currentCategory then
        self:loadSubcategories(self.currentCategory)
    end
end

--- 이벤트 핸들러: 아이템 검색
function IrisBrowser:onItemSearchChange()
    if self.currentCategory and self.currentSubcategory then
        self:loadItems(self.currentCategory, self.currentSubcategory)
    end
end

--- 닫기
function IrisBrowser:close()
    self:setVisible(false)
    self:removeFromUIManager()
    IrisBrowser._instance = nil
end

--- 아이템 자동 선택
function IrisBrowser:selectItem(item)
    if not item then return end
    
    local fullType = item:getFullType()
    
    -- IrisBrowserData에서 아이템 정보 조회
    -- (IrisBrowserData에 역방향 조회 기능이 필요할 수도 있음)
    -- 현재 구조: _cache.categories[cat].subcategories[sub].items[fullType]
    
    local targetCat = nil
    local targetSub = nil
    
    -- 전체 검색하여 카테고리 찾기 (역인덱싱이 없으므로 순회)
    -- 성능 최적화를 위해 나중에 역인덱싱 추가 고려
    if IrisBrowserData and IrisBrowserData._cache and IrisBrowserData._cache.categories then
        for catName, catData in pairs(IrisBrowserData._cache.categories) do
            for subName, subData in pairs(catData.subcategories) do
                for _, itemData in ipairs(subData.items) do
                    if itemData.fullType == fullType then
                        targetCat = catName
                        targetSub = subName
                        break
                    end
                end
                if targetCat then break end
            end
            if targetCat then break end
        end
    end
    
    -- 카테고리를 찾지 못한 경우 (기타 또는 분류되지 않음)
    if not targetCat then
        targetCat = "기타" -- 기본값
        targetSub = "전체"
        print("[IrisBrowser] Could not find category for " .. fullType .. ", defaulting to 기타")
    end
    
    -- 카테고리 선택
    self:selectCategory(targetCat)
    
    -- 서브카테고리 선택 (UI가 갱신된 후)
    self:selectSubcategory(targetSub)
    
    -- 아이템 선택 (상세 정보 표시)
    -- 검색된 목록에서 해당 아이템 찾기
    for i, itemData in ipairs(self.filteredItems) do
        if itemData.fullType == fullType then
            self.selectedItemIndex = i
            self:updateDetailPanel()
            break
        end
    end
end

return IrisBrowser
