--[[
    IrisBrowser.lua - Iris 카테고리 브라우저 메인 UI
    
    4열 레이아웃:
    - 대분류 (15%) → 소분류 (15%) → 아이템 (15%) → 설명 (55%)
    
    진입점:
    - IrisBrowser.openSearch() → 빈 상태의 검색 초기 화면
]]

require "ISUI/ISPanel"
require "ISUI/ISScrollingListBox"
require "ISUI/ISScrollPane"
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

-- 한국어 자체 번역 테이블 (UTF-8 바이트 이스케이프 시퀀스)
local TRANSLATIONS_KO = {
    Iris_UI_CategoryLabel = "\235\140\128\235\182\132\235\165\152",  -- 대분류
    Iris_UI_SubcategoryLabel = "\236\134\140\235\182\132\235\165\152",  -- 소분류
    Iris_UI_ItemLabel = "\236\149\132\236\157\180\237\133\156",  -- 아이템
    Iris_UI_DetailLabel = "\236\131\129\236\132\184\236\160\149\235\179\180",  -- 상세정보
    Iris_UI_SearchPlaceholder = "\234\178\128\236\131\137\46\46\46",  -- 검색...
    Iris_UI_Recipe = "\235\160\136\236\139\156\237\148\188",  -- 레시피
    
    -- 상호작용 섹션
    Iris_Detail_Interaction = "\236\131\129\237\152\184\236\158\145\236\154\169",  -- 상호작용
    Iris_Prefix_Recipe = "\91\235\160\136\236\139\156\237\148\188\93",  -- [레시피]
    Iris_Prefix_RightClick = "\91\236\154\176\237\129\180\235\166\173\93",  -- [우클릭]
    
    -- 우클릭 Capability 라벨
    Iris_Cap_ExtinguishFire = "\235\182\136\32\235\129\132\234\184\176",  -- 불 끄기
    Iris_Cap_AddGeneratorFuel = "\235\176\156\236\160\132\234\184\176\32\236\151\176\235\163\140\32\235\132\163\234\184\176",  -- 발전기 연료 넣기
    Iris_Cap_ScrapMoveables = "\234\176\128\234\181\172\32\237\149\180\236\178\180",  -- 가구 해체
    Iris_Cap_OpenCannedFood = "\236\186\148\32\235\148\176\234\184\176",  -- 캔 따기
    Iris_Cap_StitchWound = "\236\131\129\236\178\152\32\235\180\137\237\149\169",  -- 상처 봉합
    Iris_Cap_RemoveEmbeddedObject = "\235\176\149\237\158\140\32\235\172\188\236\178\180\32\236\160\156\234\177\176",  -- 박힌 물체 제거
    Iris_Cap_AttachWeaponMod = "\235\172\180\234\184\176\32\235\182\128\236\176\169\235\172\188\32\236\158\165\236\176\169",  -- 무기 부착물 장착

    -- 신규 대분류
    Iris_Cat_Furniture = "\234\176\128\234\181\172",  -- 가구
    Iris_Cat_Vehicle = "\236\176\168\235\159\137",  -- 차량
    Iris_Cat_Misc = "\234\184\176\237\131\128",  -- 기타

    -- 신규 소분류
    Iris_Sub_1K = "\235\179\180\236\149\136",  -- 보안
    Iris_Sub_1L = "\235\179\180\234\180\128\236\154\169\234\184\176",  -- 보관용기
    Iris_Sub_7A = "\237\131\136\236\176\169\32\234\176\128\234\181\172",  -- 탈착 가구
    Iris_Sub_8A = "\236\163\188\237\150\137\234\179\132",  -- 주행계
    Iris_Sub_8B = "\236\176\168\236\178\180\47\235\182\128\236\134\141",  -- 차체/부속
    Iris_Sub_9A = "\236\158\161\237\153\148",  -- 잡화
}

-- 현재 언어 감지 (간소화 - 항상 KO 시도)
local function getCurrentLanguage()
    return "KO"  -- 강제로 한국어 반환 (디버깅용)
end

-- 번역 헬퍼 (간소화 버전)
local function tr(key, fallback)
    -- 1순위: 자체 번역 테이블 (TRANSLATIONS_KO에 있으면 사용)
    if TRANSLATIONS_KO and TRANSLATIONS_KO[key] then
        return TRANSLATIONS_KO[key]
    end
    
    -- 2순위: PZ getText() 시도
    if getText and type(getText) == "function" then
        local ok, result = pcall(getText, key)
        if ok and result and result ~= key then
            return result
        end
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
    o.recipeExpandedByFullType = {}  -- 레시피 펼침 상태 저장
    
    -- 상세 패널 스크롤 상태
    o.detailScrollY = 0
    o.detailContentHeight = 0
    
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
    
    -- Detail 패널 (스크롤 가능)
    local scrollBarWidth = 13
    local detailPanelWidth = self.width - col4X - 10 - scrollBarWidth
    self.detailPanel = ISPanel:new(col4X, listTop, detailPanelWidth, listHeight)
    self.detailPanel:initialise()
    self.detailPanel.backgroundColor = {r=0.05, g=0.08, b=0.1, a=0.8}
    self.detailPanel.borderColor = {r=0.3, g=0.4, b=0.5, a=0.5}
    
    -- 마우스휠 이벤트 핸들러
    local browser = self
    self.detailPanel.onMouseWheel = function(self, del)
        browser:onDetailMouseWheel(del)
        return true
    end
    
    -- 클리핑(scissor) 적용 - 콘텐츠가 패널 영역 밖으로 나가지 않도록
    local originalPrerender = self.detailPanel.prerender
    self.detailPanel.prerender = function(self)
        if originalPrerender then originalPrerender(self) end
        -- 클리핑 영역 시작
        self:setStencilRect(0, 0, self.width, self.height)
    end
    
    local originalRender = self.detailPanel.render
    self.detailPanel.render = function(self)
        if originalRender then originalRender(self) end
        -- 클리핑 영역 종료
        self:clearStencilRect()
    end
    
    self:addChild(self.detailPanel)
    
    -- 스크롤바 패널 추가 (ISPanel 기반 커스텀)
    self.detailScrollBarPanel = ISPanel:new(col4X + detailPanelWidth, listTop, scrollBarWidth, listHeight)
    self.detailScrollBarPanel:initialise()
    self.detailScrollBarPanel.backgroundColor = {r=0, g=0, b=0, a=0}  -- 투명 배경
    self.detailScrollBarPanel.borderColor = {r=0, g=0, b=0, a=0}  -- 투명 테두리
    
    -- 스크롤바 렌더링
    local browserRef = self
    self.detailScrollBarPanel.render = function(scrollPanel)
        -- 아이템 미선택 또는 스크롤 불필요시 숨기기
        if not browserRef.currentSelectedFullType then
            return  -- 아이템 선택 안됨
        end
        
        local needsScroll = browserRef.detailContentHeight > browserRef.detailPanel.height
        if not needsScroll then
            return  -- 스크롤 불필요
        end
        
        -- 트랙 배경 그리기
        scrollPanel:drawRect(0, 0, scrollPanel.width, scrollPanel.height, 0.5, 0.1, 0.12, 0.15)
        
        -- 스크롤 썸 (thumb) 그리기
        local maxScroll = math.max(1, browserRef.detailContentHeight - browserRef.detailPanel.height)
        local ratio = browserRef.detailScrollY / maxScroll
        local trackHeight = scrollPanel.height - 4
        local thumbHeight = math.max(20, (browserRef.detailPanel.height / math.max(1, browserRef.detailContentHeight)) * trackHeight)
        local thumbY = 2 + ratio * (trackHeight - thumbHeight)
        
        -- Thumb 그리기
        scrollPanel:drawRect(2, thumbY, scrollBarWidth - 4, thumbHeight, 0.7, 0.4, 0.5, 0.7)
    end
    
    self:addChild(self.detailScrollBarPanel)
    
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
            -- v3.0.0: 숫자 표시 없이 이름만 표시
            self.itemList:addItem(item.displayName, item)
            addedCount = addedCount + 1
        end
    end
    print("[IrisBrowser] Added " .. addedCount .. " items to list")
end

--- 상세 정보 표시
function IrisBrowser:showDetail(fullType)
    -- 기존 상세 정보 삭제
    local childrenToRemove = {}
    
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
            end
        end
    end
    
    if #childrenToRemove == 0 then
        local children = self.detailPanel:getChildren()
        if children then
            for i, child in ipairs(children) do
                table.insert(childrenToRemove, child)
            end
            if #childrenToRemove == 0 then
                for k, child in pairs(children) do
                    if type(k) == "number" then
                        table.insert(childrenToRemove, child)
                    end
                end
            end
        end
    end
    
    for _, child in ipairs(childrenToRemove) do
        self.detailPanel:removeChild(child)
    end
    
    if not fullType then
        return
    end
    
    ensureDeps()
    
    local item = IrisBrowserData and IrisBrowserData.getItem(fullType)
    
    if not item then
        local errorLabel = ISLabel:new(10, 10, 20, "아이템 정보를 찾을 수 없습니다", 0.8, 0.3, 0.3, 1, UIFont.Medium, true)
        self.detailPanel:addChild(errorLabel)
        return
    end
    
    local yOffset = 10 - self.detailScrollY  -- 스크롤 오프셋 적용
    
    -- 아이템 이름 가져오기
    local displayName = fullType
    if item.getDisplayName then
        local ok, name = pcall(function() return item:getDisplayName() end)
        if ok and name and type(name) == "string" and #name > 0 then
            displayName = name
        end
    end
    
    local nameLabel = ISLabel:new(10, yOffset, 25, displayName, 0.6, 0.9, 1.0, 1.0, UIFont.Medium, true)
    self.detailPanel:addChild(nameLabel)
    yOffset = yOffset + 30
    
    -- [1] 기본 정보 (무게, 타입, 핵심 수치)
    if IrisWikiSections and IrisWikiSections.renderCoreInfoSection then
        local coreInfo = IrisWikiSections.renderCoreInfoSection(item)
        if coreInfo and coreInfo ~= "" then
            local coreLabel = ISLabel:new(10, yOffset, 18, coreInfo, 0.7, 0.85, 0.9, 1, UIFont.Medium, true)
            self.detailPanel:addChild(coreLabel)
            yOffset = yOffset + 22
        end
    end
    
    -- [2] 주 소분류 설명 (IrisDesc)
    local IrisAPI = nil
    local apiOk, apiResult = pcall(require, "Iris/IrisAPI")
    if apiOk then IrisAPI = apiResult end
    
    if IrisAPI and IrisAPI.getDescription then
        local descOk, descText = pcall(function() return IrisAPI.getDescription(fullType, nil) end)
        
        if descOk and descText and descText ~= "" then
            yOffset = yOffset + 5
            local sepLabel = ISLabel:new(10, yOffset, 14, "────────────────────────", 0.3, 0.4, 0.5, 1, UIFont.Medium, true)
            self.detailPanel:addChild(sepLabel)
            yOffset = yOffset + 20
            
            for line in descText:gmatch("[^\n]+") do
                local lineLabel = ISLabel:new(10, yOffset, 18, line, 0.85, 0.85, 0.85, 1, UIFont.Medium, true)
                self.detailPanel:addChild(lineLabel)
                yOffset = yOffset + 18
            end
            yOffset = yOffset + 10
        end
    end
    
    -- [3] 상호작용 섹션 (레시피 + 우클릭 행동 통합)
    local interactionItems = {}  -- { {type="recipe"|"rightclick", name=string, sortKey=string} }
    
    -- 레시피 수집
    local recipeList = {}
    if IrisAPI and IrisAPI.getRecipeConnectionsForItem then
        local ok, list = pcall(function() return IrisAPI.getRecipeConnectionsForItem(item) end)
        if ok and list then recipeList = list end
    end
    
    -- 레시피 이름 중복 제거 및 추가
    local recipeNameSet = {}
    for _, e in ipairs(recipeList) do
        local name = tostring(e.recipe or "Unknown")
        if not recipeNameSet[name] then
            recipeNameSet[name] = true
            table.insert(interactionItems, {type = "recipe", name = name, sortKey = "1_" .. name})
        end
    end
    
    -- 우클릭 Capability 수집
    local capabilityList = {}
    if IrisAPI and IrisAPI.getCapabilities then
        local ok, caps = pcall(function() return IrisAPI.getCapabilities(fullType) end)
        if ok and caps then capabilityList = caps end
    end
    
    -- Capability ID → 번역 키 매핑
    local capabilityLabelMap = {
        can_extinguish_fire = "Iris_Cap_ExtinguishFire",
        can_add_generator_fuel = "Iris_Cap_AddGeneratorFuel",
        can_scrap_moveables = "Iris_Cap_ScrapMoveables",
        can_open_canned_food = "Iris_Cap_OpenCannedFood",
        can_stitch_wound = "Iris_Cap_StitchWound",
        can_remove_embedded_object = "Iris_Cap_RemoveEmbeddedObject",
        can_attach_weapon_mod = "Iris_Cap_AttachWeaponMod",
    }
    
    for _, capId in ipairs(capabilityList) do
        local labelKey = capabilityLabelMap[capId]
        local displayName = labelKey and tr(labelKey, capId) or capId
        table.insert(interactionItems, {type = "rightclick", name = displayName, sortKey = "0_" .. displayName})
    end
    
    -- 총 개수
    local totalCount = #interactionItems
    
    if totalCount > 0 then
        -- 정렬 (우클릭 먼저, 그 다음 레시피, 각각 알파벳순)
        table.sort(interactionItems, function(a, b) return a.sortKey < b.sortKey end)
        
        local expandKey = fullType .. "_interactions"
        local expanded = self.recipeExpandedByFullType[expandKey] == true
        local arrow = expanded and " [-]" or " [+]"
        local interactionLabel = tr("Iris_Detail_Interaction", "Interactions")
        local headerText = interactionLabel .. " (" .. tostring(totalCount) .. ")" .. arrow
        
        -- 헤더 버튼
        local btn = ISButton:new(10, yOffset, 250, 18, headerText, self, IrisBrowser.onToggleRecipeSection)
        btn:initialise()
        btn.expandKey = expandKey
        btn.backgroundColor = {r=0, g=0, b=0, a=0}
        btn.backgroundColorMouseOver = {r=0.2, g=0.3, b=0.4, a=0.3}
        btn.borderColor = {r=0, g=0, b=0, a=0}
        btn.textColor = {r=0.9, g=0.9, b=0.9, a=1}
        self.detailPanel:addChild(btn)
        yOffset = yOffset + 20
        
        if expanded then
            local prefixRecipe = tr("Iris_Prefix_Recipe", "[Recipe]")
            local prefixRightClick = tr("Iris_Prefix_RightClick", "[Action]")
            
            for _, item in ipairs(interactionItems) do
                local prefix = item.type == "recipe" and prefixRecipe or prefixRightClick
                local r, g, b = 0.85, 0.85, 0.85
                if item.type == "rightclick" then
                    r, g, b = 0.7, 0.9, 0.7  -- 우클릭 행동은 녹색 계열
                end
                local lbl = ISLabel:new(20, yOffset, 16, prefix .. " " .. item.name, r, g, b, 1, UIFont.Small, true)
                self.detailPanel:addChild(lbl)
                yOffset = yOffset + 16
            end
        end
    end

    
    -- [4] 변형 목록 (v3.0.0 - DisplayName 기반 접기)
    local variants = self.currentSelectedVariants
    if variants and #variants > 1 then
        local expandKey = fullType .. "_variants"
        local expanded = self.recipeExpandedByFullType[expandKey] == true
        local arrow = expanded and " [-]" or " [+]"
        local headerText = "Variants (" .. #variants .. ")" .. arrow
        
        local btn = ISButton:new(10, yOffset, 250, 18, headerText, self, IrisBrowser.onToggleRecipeSection)
        btn:initialise()
        btn.expandKey = expandKey
        btn.backgroundColor = {r=0, g=0, b=0, a=0}
        btn.backgroundColorMouseOver = {r=0.2, g=0.3, b=0.4, a=0.3}
        btn.borderColor = {r=0, g=0, b=0, a=0}
        btn.textColor = {r=0.8, g=0.9, b=1.0, a=1}
        self.detailPanel:addChild(btn)
        yOffset = yOffset + 20
        
        if expanded then
            for _, variantFullType in ipairs(variants) do
                -- 각 변형의 DisplayName 가져오기
                local variantItem = IrisBrowserData and IrisBrowserData.getItem(variantFullType)
                local variantDisplayName = variantFullType
                if variantItem and variantItem.getDisplayName then
                    local ok, name = pcall(function() return variantItem:getDisplayName() end)
                    if ok and name then
                        variantDisplayName = name
                    end
                end
                
                local prefix = (variantFullType == fullType) and "▸ " or "  "
                local lbl = ISLabel:new(20, yOffset, 16, prefix .. variantDisplayName .. " [" .. variantFullType .. "]", 0.75, 0.85, 0.95, 1, UIFont.Small, true)
                self.detailPanel:addChild(lbl)
                yOffset = yOffset + 16
            end
        end
    end
    
    -- [5] 메타 정보 (분류 ID, 모듈)
    if IrisWikiSections and IrisWikiSections.renderMetaInfoSection then
        local metaInfo = IrisWikiSections.renderMetaInfoSection(item)
        if metaInfo and metaInfo ~= "" then
            yOffset = yOffset + 5
            for line in metaInfo:gmatch("[^\n]+") do
                local r, g, b = 0.6, 0.6, 0.6
                if line:find("───") then
                    r, g, b = 0.3, 0.4, 0.5
                end
                local metaLabel = ISLabel:new(10, yOffset, 18, line, r, g, b, 1, UIFont.Small, true)
                self.detailPanel:addChild(metaLabel)
                yOffset = yOffset + 16
            end
        end
    end
    
    -- 스크롤을 위해 총 콘텐츠 높이 저장 (스크롤 오프셋 빼기 전 기준)
    self.detailContentHeight = yOffset + self.detailScrollY + 20  -- 여유 공간 추가
end


--- 상세 패널 마우스 휠 핸들러
function IrisBrowser:onDetailMouseWheel(del)
    if not self.detailPanel then return end
    
    local scrollAmount = 30  -- 한 번에 스크롤할 픽셀
    local maxScroll = math.max(0, self.detailContentHeight - self.detailPanel.height)
    
    -- del > 0: 휠 위로 → 스크롤 위로 (scrollY 감소)
    -- del < 0: 휠 아래로 → 스크롤 아래로 (scrollY 증가)
    self.detailScrollY = self.detailScrollY + (del * scrollAmount)
    
    -- 범위 제한
    if self.detailScrollY < 0 then
        self.detailScrollY = 0
    elseif self.detailScrollY > maxScroll then
        self.detailScrollY = maxScroll
    end
    
    -- 현재 선택된 아이템에 대해 상세 정보 다시 표시
    if self.currentSelectedFullType then
        self:showDetail(self.currentSelectedFullType)
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
    self.detailScrollY = 0  -- 새 아이템 선택 시 스크롤 초기화
    self.currentSelectedFullType = itemData.fullType
    self.currentSelectedVariants = itemData.variants  -- v3.0.0: 변형 목록 저장
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

--- 레시피 섹션 접기/펼치기 토글
function IrisBrowser:onToggleRecipeSection(button)
    local expandKey = button.expandKey
    if not expandKey then return end
    
    -- 펼침 상태 토글
    self.recipeExpandedByFullType[expandKey] = not (self.recipeExpandedByFullType[expandKey] == true)
    
    -- 상세 패널 다시 그리기
    self:showDetail(self.currentSelectedFullType)
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
        self.detailScrollY = 0  -- 새 아이템 선택 시 스크롤 초기화
        self.currentSelectedFullType = fullType
        self:showDetail(fullType)
        
        print("[IrisBrowser] Selected item: " .. fullType .. " in " .. targetCat .. "." .. targetSub)
    else
        -- 분류되지 않은 아이템: 상세 정보만 표시
        self.detailScrollY = 0  -- 새 아이템 선택 시 스크롤 초기화
        self.currentSelectedFullType = fullType
        self:showDetail(fullType)
        print("[IrisBrowser] Item not classified: " .. fullType)
    end
end

return IrisBrowser
