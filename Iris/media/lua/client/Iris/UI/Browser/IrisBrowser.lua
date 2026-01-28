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

-- ===============================================================
-- 번역 시스템 디버그 (한번에 문제 파악용)
-- ===============================================================
local _translationDebugDone = false

local function debugTranslationSystem()
    if _translationDebugDone then return end
    _translationDebugDone = true
    
    print("===============================================================")
    print("[IrisBrowser] TRANSLATION SYSTEM DEBUG START")
    print("===============================================================")
    
    -- 1. getText 함수 존재 여부
    print("[DEBUG] 1. getText function exists: " .. tostring(getText ~= nil))
    print("[DEBUG]    getText type: " .. type(getText))
    
    -- 2. Translator 객체 확인 (PZ 내부)
    print("[DEBUG] 2. Translator object exists: " .. tostring(Translator ~= nil))
    if Translator then
        print("[DEBUG]    Translator type: " .. type(Translator))
        if Translator.getLanguage then
            local ok, lang = pcall(Translator.getLanguage)
            print("[DEBUG]    Translator.getLanguage(): ok=" .. tostring(ok) .. ", lang=" .. tostring(lang))
        end
    end
    
    -- 3. getCore() 언어 설정
    print("[DEBUG] 3. getCore() check:")
    if getCore then
        local ok, core = pcall(getCore)
        if ok and core then
            print("[DEBUG]    getCore() exists")
            if core.getOptionCurrentLanguage then
                local ok2, lang = pcall(function() return core:getOptionCurrentLanguage() end)
                print("[DEBUG]    Current language: ok=" .. tostring(ok2) .. ", lang=" .. tostring(lang))
            end
            if core.getOptionLanguage then
                local ok3, lang = pcall(function() return core:getOptionLanguage() end)
                print("[DEBUG]    Option language: ok=" .. tostring(ok3) .. ", lang=" .. tostring(lang))
            end
        else
            print("[DEBUG]    getCore() failed or nil")
        end
    else
        print("[DEBUG]    getCore not available")
    end
    
    -- 4. 테스트 번역 키 시도
    print("[DEBUG] 4. Translation key tests:")
    local testKeys = {
        "Iris_UI_CategoryLabel",
        "Iris_UI_SubcategoryLabel", 
        "Iris_Sub_1A",
        "IG_UI_Iris_UI_CategoryLabel",  -- 다른 가능한 형식
        "UI_Iris_CategoryLabel",        -- 또 다른 가능한 형식
    }
    
    for _, key in ipairs(testKeys) do
        if getText then
            local ok, result = pcall(getText, key)
            local status = "MISS"
            if ok and result and result ~= key then
                status = "HIT"
            end
            print("[DEBUG]    getText('" .. key .. "'): status=" .. status .. ", ok=" .. tostring(ok) .. ", result='" .. tostring(result) .. "'")
        end
    end
    
    -- 5. 기본 PZ 번역 키 테스트 (작동하는지 확인)
    print("[DEBUG] 5. Built-in PZ translation test:")
    local builtinKeys = {"UI_Yes", "UI_No", "UI_Ok", "UI_Cancel"}
    for _, key in ipairs(builtinKeys) do
        if getText then
            local ok, result = pcall(getText, key)
            print("[DEBUG]    getText('" .. key .. "'): ok=" .. tostring(ok) .. ", result='" .. tostring(result) .. "'")
        end
    end
    
    print("===============================================================")
    print("[IrisBrowser] TRANSLATION SYSTEM DEBUG END")
    print("===============================================================")
end

-- 한국어 자체 번역 테이블 (PZ 번역 시스템 fallback)
local TRANSLATIONS_KO = {
    Iris_UI_CategoryLabel = "대분류",
    Iris_UI_SubcategoryLabel = "소분류",
    Iris_UI_ItemLabel = "아이템",
    Iris_UI_DetailLabel = "상세정보",
    Iris_UI_SearchPlaceholder = "검색...",
}

-- 현재 언어 감지
local function getCurrentLanguage()
    if getCore then
        local ok, core = pcall(getCore)
        if ok and core and core.getOptionCurrentLanguage then
            local ok2, lang = pcall(function() return core:getOptionCurrentLanguage() end)
            if ok2 and lang then
                return tostring(lang):upper()
            end
        end
    end
    return "EN"
end

-- 번역 헬퍼 (PZ getText + 자체 번역 fallback)
local function tr(key, fallback)
    -- 첫 호출 시 디버그 출력
    debugTranslationSystem()
    
    -- 1순위: PZ getText() 시도
    if getText and type(getText) == "function" then
        local ok, result = pcall(getText, key)
        if ok and result and result ~= key then
            return result
        end
    end
    
    -- 2순위: 한국어면 자체 번역 테이블 사용
    local lang = getCurrentLanguage()
    if lang == "KO" and TRANSLATIONS_KO[key] then
        return TRANSLATIONS_KO[key]
    end
    
    -- 3순위: fallback
    return fallback or key
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
    print("[IrisBrowser] ########## openSearch() START ##########")
    ensureDeps()
    
    -- 데이터 빌드 확인
    print("[IrisBrowser] IrisBrowserData exists = " .. tostring(IrisBrowserData ~= nil))
    print("[IrisBrowser] IrisBrowserData._built = " .. tostring(IrisBrowserData and IrisBrowserData._built))
    
    if IrisBrowserData and not IrisBrowserData._built then
        print("[IrisBrowser] Building IrisBrowserData...")
        IrisBrowserData.build()
        print("[IrisBrowser] Build complete, _built = " .. tostring(IrisBrowserData._built))
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
    
    print("[IrisBrowser] Creating browser panel: " .. panelW .. "x" .. panelH)
    local browser = IrisBrowser:new(x, y, panelW, panelH)
    browser:initialise()
    browser:instantiate()
    browser:addToUIManager()
    browser:setVisible(true)
    browser:bringToTop()
    
    IrisBrowser._instance = browser
    print("[IrisBrowser] ########## openSearch() END ##########")
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
    
    -- 전체 검색창 (닫기 버튼 왼쪽에 배치)
    local closeBtnWidth = 25
    local closeBtnX = self.width - closeBtnWidth - 5
    local searchBarWidth = 200  -- 적절한 너비로 고정
    local searchBarX = closeBtnX - searchBarWidth - 10
    
    self.searchBar = ISTextEntryBox:new("", searchBarX, 8, searchBarWidth, 24)
    self.searchBar:initialise()
    self.searchBar:instantiate()
    self.searchBar.onTextChange = function()
        self:onGlobalSearchChange()
    end
    self:addChild(self.searchBar)
    
    -- 닫기 버튼 (검색창 오른쪽)
    self.closeBtn = ISButton:new(closeBtnX, 5, closeBtnWidth, 25, "X", self, self.close)
    self.closeBtn:initialise()
    self.closeBtn.borderColor = {r=0.5, g=0.5, b=0.5, a=0.5}
    self:addChild(self.closeBtn)
    
    -- === Category Column ===
    self.categoryLabel = ISLabel:new(col1X, listTop - 18, 16, tr("Iris_UI_CategoryLabel", "Category"), 0.7, 0.7, 0.7, 1, UIFont.Small, true)
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
    
    -- === Subcategory Column ===
    self.subcategoryLabel = ISLabel:new(col2X, listTop - 18, 16, tr("Iris_UI_SubcategoryLabel", "Subcategory"), 0.7, 0.7, 0.7, 1, UIFont.Small, true)
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
    
    -- === Items Column ===
    self.itemLabel = ISLabel:new(col3X, listTop - 18, 16, tr("Iris_UI_ItemLabel", "Items"), 0.7, 0.7, 0.7, 1, UIFont.Small, true)
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
    
    -- === Detail Column ===
    self.detailLabel = ISLabel:new(col4X, listTop - 18, 16, tr("Iris_UI_DetailLabel", "Details"), 0.7, 0.7, 0.7, 1, UIFont.Small, true)
    self:addChild(self.detailLabel)
    
    -- Detail 패널 너비를 창 경계 내에 맞춤
    local detailPanelWidth = self.width - col4X - 10
    self.detailPanel = ISPanel:new(col4X, listTop, detailPanelWidth, listHeight)
    self.detailPanel:initialise()
    self.detailPanel.backgroundColor = {r=0.05, g=0.08, b=0.1, a=0.8}
    self.detailPanel.borderColor = {r=0.3, g=0.4, b=0.5, a=0.5}
    self:addChild(self.detailPanel)
    
    -- 초기 데이터 로드
    self:loadCategories()
end

--- 대분류 로드
function IrisBrowser:loadCategories()
    print("[IrisBrowser] ========== loadCategories() START ==========")
    self.categoryList:clear()
    
    ensureDeps()
    if not IrisBrowserData then 
        print("[IrisBrowser] ERROR: IrisBrowserData is nil!")
        return 
    end
    
    print("[IrisBrowser] Calling IrisBrowserData.getCategories()...")
    local categories = IrisBrowserData.getCategories()
    print("[IrisBrowser] Got " .. #categories .. " categories")
    
    for i, cat in ipairs(categories) do
        local displayLabel = cat.label or cat.name
        print("[IrisBrowser] Adding category " .. i .. ": '" .. displayLabel .. "' (code=" .. cat.name .. ")")
        self.categoryList:addItem(displayLabel, cat)
    end
    
    print("[IrisBrowser] categoryList.items count = " .. #self.categoryList.items)
    print("[IrisBrowser] ========== loadCategories() END ==========")
end

--- 소분류 로드
function IrisBrowser:loadSubcategories(categoryName)
    print("[IrisBrowser] loadSubcategories called for: " .. tostring(categoryName))
    self.subcategoryList:clear()
    
    ensureDeps()
    if not IrisBrowserData or not categoryName then 
        print("[IrisBrowser] IrisBrowserData or categoryName missing")
        return 
    end
    
    local subcategories = IrisBrowserData.getSubcategories(categoryName)
    print("[IrisBrowser] getSubcategories returned: " .. #subcategories .. " items")
    
    local filterText = self.subcategorySearchBar:getText():lower()
    
    local addedCount = 0
    for _, sub in ipairs(subcategories) do
        -- 검색 필터 적용 (코드와 라벨 둘 다 검색 가능)
        local labelLower = (sub.label or sub.name):lower()
        local codeLower = sub.name:lower()
        if filterText == "" or labelLower:find(filterText, 1, true) or codeLower:find(filterText, 1, true) then
            -- 빈 소분류도 (0) 표시 (숨김 금지)
            -- 라벨 형식: "코드 라벨 (개수)" 예: "1-A 건설/제작 (5)"
            local displayLabel = sub.name .. " " .. (sub.label or "") .. " (" .. sub.itemCount .. ")"
            self.subcategoryList:addItem(displayLabel, sub)
            addedCount = addedCount + 1
        end
    end
    print("[IrisBrowser] Added " .. addedCount .. " subcategories to list")
end

--- 아이템 로드
function IrisBrowser:loadItems(categoryName, subcategoryName)
    print("[IrisBrowser] loadItems called: " .. tostring(categoryName) .. "." .. tostring(subcategoryName))
    self.itemList:clear()
    
    ensureDeps()
    if not IrisBrowserData or not categoryName or not subcategoryName then 
        print("[IrisBrowser] loadItems - missing params, returning")
        return 
    end
    
    local items = IrisBrowserData.getItems(categoryName, subcategoryName)
    print("[IrisBrowser] getItems returned " .. #items .. " items")
    
    local filterText = self.itemSearchBar:getText():lower()
    local addedCount = 0
    
    for _, item in ipairs(items) do
        -- 검색 필터 적용
        if filterText == "" or item.displayName:lower():find(filterText, 1, true) then
            self.itemList:addItem(item.displayName, item)
            addedCount = addedCount + 1
        end
    end
    print("[IrisBrowser] Added " .. addedCount .. " items to list")
end

--- 상세 정보 표시
function IrisBrowser:showDetail(fullType)
    print("[IrisBrowser:showDetail] ========== START ==========")
    print("[IrisBrowser:showDetail] fullType = " .. tostring(fullType))
    print("[IrisBrowser:showDetail] fullType type = " .. type(fullType))
    
    -- 기존 상세 정보 삭제 (ISPanel의 자식 목록 비우기)
    -- 방법 1: javaObject의 getChildren() 사용 (Java ArrayList)
    -- 방법 2: ISUIElement는 내부적으로 Lua table로 children 관리할 수 있음
    local childrenToRemove = {}
    
    -- 먼저 javaObject를 통한 Java ArrayList 접근 시도
    if self.detailPanel.javaObject and self.detailPanel.javaObject.getChildren then
        local ok, javaChildren = pcall(function() return self.detailPanel.javaObject:getChildren() end)
        if ok and javaChildren and javaChildren.size then
            local ok2, sz = pcall(function() return javaChildren:size() end)
            if ok2 and sz and sz > 0 then
                for i = 0, sz - 1 do
                    local ok3, child = pcall(function() return javaChildren:get(i) end)
                    if ok3 and child then
                        table.insert(childrenToRemove, child)
                    end
                end
                print("[IrisBrowser:showDetail] Found " .. #childrenToRemove .. " children via javaObject")
            end
        end
    end
    
    -- javaObject 방식이 실패하면 ISUIElement의 Lua children 접근
    if #childrenToRemove == 0 then
        local children = self.detailPanel:getChildren()
        if children then
            -- ipairs로 순회 (Lua 테이블 스타일)
            for i, child in ipairs(children) do
                table.insert(childrenToRemove, child)
            end
            -- 만약 ipairs가 실패하면 pairs로 시도
            if #childrenToRemove == 0 then
                for k, child in pairs(children) do
                    if type(k) == "number" then
                        table.insert(childrenToRemove, child)
                    end
                end
            end
            print("[IrisBrowser:showDetail] Found " .. #childrenToRemove .. " children via getChildren()")
        end
    end
    
    -- 수집한 자식들 삭제
    for _, child in ipairs(childrenToRemove) do
        self.detailPanel:removeChild(child)
    end
    print("[IrisBrowser:showDetail] Cleared " .. #childrenToRemove .. " children")
    
    if not fullType then
        print("[IrisBrowser:showDetail] fullType is nil/false, showing placeholder")
        -- placeholder
        local placeholderLabel = ISLabel:new(10, 10, 20, "아이템을 선택하세요", 0.5, 0.5, 0.5, 1, UIFont.Small, true)
        self.detailPanel:addChild(placeholderLabel)
        return
    end
    
    ensureDeps()
    print("[IrisBrowser:showDetail] IrisBrowserData exists = " .. tostring(IrisBrowserData ~= nil))
    print("[IrisBrowser:showDetail] IrisBrowserData.getItem exists = " .. tostring(IrisBrowserData and IrisBrowserData.getItem ~= nil))
    
    local item = IrisBrowserData and IrisBrowserData.getItem(fullType)
    print("[IrisBrowser:showDetail] item = " .. tostring(item))
    print("[IrisBrowser:showDetail] item type = " .. type(item))
    
    if item then
        -- 아이템 객체 상세 정보
        print("[IrisBrowser:showDetail] item is truthy, examining properties...")
        
        -- 메타테이블 확인
        local mt = getmetatable(item)
        print("[IrisBrowser:showDetail] item metatable = " .. tostring(mt))
        
        -- 주요 메서드 존재 여부
        print("[IrisBrowser:showDetail] item.getDisplayName = " .. tostring(item.getDisplayName))
        print("[IrisBrowser:showDetail] item.getFullName = " .. tostring(item.getFullName))
        print("[IrisBrowser:showDetail] item.getFullType = " .. tostring(item.getFullType))
        print("[IrisBrowser:showDetail] item.getScriptItem = " .. tostring(item.getScriptItem))
        
        -- tostring 결과
        local tostringResult = tostring(item)
        print("[IrisBrowser:showDetail] tostring(item) = " .. tostringResult)
        
        -- Java 클래스 이름 추출 시도
        if tostringResult:match("zombie%.") then
            print("[IrisBrowser:showDetail] Detected Java object: " .. tostringResult)
        end
    end
    
    if not item then
        print("[IrisBrowser:showDetail] item is nil, showing error message")
        local errorLabel = ISLabel:new(10, 10, 20, "아이템 정보를 찾을 수 없습니다", 0.8, 0.3, 0.3, 1, UIFont.Small, true)
        self.detailPanel:addChild(errorLabel)
        return
    end
    
    -- IrisWikiSections 사용하여 상세 정보 표시
    local yOffset = 10
    
    -- 아이템 이름 (안전하게 가져오기)
    local displayName = fullType
    print("[IrisBrowser:showDetail] Default displayName = " .. displayName)
    
    if item.getDisplayName then
        print("[IrisBrowser:showDetail] Calling item:getDisplayName()...")
        local ok, name = pcall(function() return item:getDisplayName() end)
        print("[IrisBrowser:showDetail] getDisplayName pcall result: ok=" .. tostring(ok) .. ", name=" .. tostring(name))
        
        if ok then
            print("[IrisBrowser:showDetail] name type = " .. type(name))
            if name then
                print("[IrisBrowser:showDetail] name length = " .. tostring(#name))
                -- 바이트 값 확인 (첫 20바이트)
                local bytes = {}
                for i = 1, math.min(20, #name) do
                    bytes[#bytes + 1] = string.byte(name, i)
                end
                print("[IrisBrowser:showDetail] name bytes (first 20) = " .. table.concat(bytes, ", "))
            end
        else
            print("[IrisBrowser:showDetail] getDisplayName pcall ERROR: " .. tostring(name))
        end
        
        if ok and name and type(name) == "string" and #name > 0 then
            displayName = name
            print("[IrisBrowser:showDetail] Using getDisplayName result: " .. displayName)
        else
            print("[IrisBrowser:showDetail] getDisplayName failed or returned invalid, using fullType")
        end
    else
        print("[IrisBrowser:showDetail] item.getDisplayName is nil/false")
    end
    
    print("[IrisBrowser:showDetail] Final displayName = " .. displayName)
    
    local nameLabel = ISLabel:new(10, yOffset, 25, displayName, 0.6, 0.9, 1.0, 1.0, UIFont.Medium, true)
    self.detailPanel:addChild(nameLabel)
    yOffset = yOffset + 30
    
    -- 태그 및 속성 섹션들 표시
    if IrisWikiSections and IrisWikiSections.getAllSections then
        local sections = IrisWikiSections.getAllSections(item)
        for _, sectionText in ipairs(sections) do
            if sectionText and sectionText ~= "" then
                local sectionLabel = ISLabel:new(10, yOffset, 18, sectionText, 0.9, 0.9, 0.9, 1, UIFont.Small, true)
                self.detailPanel:addChild(sectionLabel)
                yOffset = yOffset + 22
            end
        end
        
        -- 섹션이 없으면 기본 메시지
        if #sections == 0 then
            local noInfoLabel = ISLabel:new(10, yOffset, 18, "추가 정보 없음", 0.6, 0.6, 0.6, 1, UIFont.Small, true)
            self.detailPanel:addChild(noInfoLabel)
        end
    end
end

--- 이벤트 핸들러: 대분류 선택
function IrisBrowser:onCategorySelected(item)
    print("[IrisBrowser] onCategorySelected called")
    print("[IrisBrowser] item type: " .. type(item))
    
    if not item then 
        print("[IrisBrowser] item is nil, returning")
        return 
    end
    
    -- ISScrollingListBox에서 item 구조 확인
    if type(item) == "table" then
        for k, v in pairs(item) do
            print("[IrisBrowser] item." .. tostring(k) .. " = " .. tostring(v))
        end
    end
    
    local catData = item.item
    if not catData then 
        print("[IrisBrowser] catData is nil, trying self.categoryList.selected")
        -- ISScrollingListBox에서 selected 인덱스로 가져오기 시도
        local selectedIdx = self.categoryList.selected
        if selectedIdx and selectedIdx > 0 then
            local selectedItem = self.categoryList.items[selectedIdx]
            if selectedItem then
                catData = selectedItem.item
                print("[IrisBrowser] Got catData from selected: " .. tostring(catData and catData.name))
            end
        end
    end
    
    if not catData then
        print("[IrisBrowser] catData still nil, returning")
        return 
    end
    
    print("[IrisBrowser] Selected category: " .. tostring(catData.name))
    
    self.currentCategory = catData.name
    self.currentSubcategory = nil
    self.currentSelectedFullType = nil
    
    self:loadSubcategories(self.currentCategory)
    self.itemList:clear()
    self:showDetail(nil)
end

--- 이벤트 핸들러: 소분류 선택
function IrisBrowser:onSubcategorySelected(item)
    print("[IrisBrowser] onSubcategorySelected called")
    if not item then 
        print("[IrisBrowser] subitem is nil")
        return 
    end
    local subData = item.item
    if not subData then 
        print("[IrisBrowser] subData is nil, trying selected index")
        local selectedIdx = self.subcategoryList.selected
        if selectedIdx and selectedIdx > 0 then
            local selectedItem = self.subcategoryList.items[selectedIdx]
            if selectedItem then
                subData = selectedItem.item
                print("[IrisBrowser] Got subData from selected: " .. tostring(subData and subData.name))
            end
        end
    end
    
    if not subData then
        print("[IrisBrowser] subData still nil")
        return 
    end
    
    print("[IrisBrowser] Selected subcategory: " .. tostring(subData.name))
    
    self.currentSubcategory = subData.name
    self.currentSelectedFullType = nil
    
    self:loadItems(self.currentCategory, self.currentSubcategory)
    self:showDetail(nil)
end

--- 이벤트 핸들러: 아이템 선택
function IrisBrowser:onItemSelected(item)
    print("[IrisBrowser] onItemSelected called")
    print("[IrisBrowser] item = " .. tostring(item))
    print("[IrisBrowser] item type = " .. type(item))
    
    if not item then 
        print("[IrisBrowser] item is nil, returning")
        return 
    end
    
    -- ISScrollingListBox item 구조 확인
    if type(item) == "table" then
        for k, v in pairs(item) do
            print("[IrisBrowser] item." .. tostring(k) .. " = " .. tostring(v))
        end
    end
    
    local itemData = item.item
    print("[IrisBrowser] itemData = " .. tostring(itemData))
    print("[IrisBrowser] itemData type = " .. type(itemData))
    
    if not itemData then 
        print("[IrisBrowser] itemData is nil, trying selected index")
        -- ISScrollingListBox에서 selected 인덱스로 가져오기 시도
        local selectedIdx = self.itemList.selected
        print("[IrisBrowser] selectedIdx = " .. tostring(selectedIdx))
        if selectedIdx and selectedIdx > 0 then
            local selectedItem = self.itemList.items[selectedIdx]
            print("[IrisBrowser] selectedItem = " .. tostring(selectedItem))
            if selectedItem then
                itemData = selectedItem.item
                print("[IrisBrowser] Got itemData from selected: " .. tostring(itemData))
            end
        end
    end
    
    if not itemData then
        print("[IrisBrowser] itemData still nil, returning")
        return 
    end
    
    -- itemData 구조 확인
    if type(itemData) == "table" then
        for k, v in pairs(itemData) do
            print("[IrisBrowser] itemData." .. tostring(k) .. " = " .. tostring(v))
        end
    end
    
    print("[IrisBrowser] itemData.fullType = " .. tostring(itemData.fullType))
    
    -- SSOT: currentSelectedFullType 하나만 유지
    self.currentSelectedFullType = itemData.fullType
    print("[IrisBrowser] Set currentSelectedFullType = " .. tostring(self.currentSelectedFullType))
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
    local targetCat = nil
    local targetSub = nil
    
    -- 전체 검색하여 카테고리 찾기 (역인덱싱이 없으므로 순회)
    if IrisBrowserData and IrisBrowserData._cache and IrisBrowserData._cache.categories then
        for catName, catData in pairs(IrisBrowserData._cache.categories) do
            if catData.subcategories then
                for subName, subData in pairs(catData.subcategories) do
                    -- items는 { fullType = true } 형태의 set(딕셔너리)
                    if subData.items and subData.items[fullType] then
                        targetCat = catName
                        targetSub = subName
                        break
                    end
                end
            end
            if targetCat then break end
        end
    end
    
    -- 카테고리를 찾은 경우: 선택 및 상세 표시
    if targetCat and targetSub then
        -- 카테고리 선택
        self.currentCategory = targetCat
        self:loadSubcategories(targetCat)
        
        -- 소분류 선택
        self.currentSubcategory = targetSub
        self:loadItems(targetCat, targetSub)
        
        -- 상세 표시
        self.currentSelectedFullType = fullType
        self:showDetail(fullType)
        
        print("[IrisBrowser] Selected item: " .. fullType .. " in " .. targetCat .. "." .. targetSub)
    else
        -- 분류되지 않은 아이템: 상세 정보만 표시
        self.currentSelectedFullType = fullType
        self:showDetail(fullType)
        print("[IrisBrowser] Item not classified: " .. fullType)
    end
end

return IrisBrowser
