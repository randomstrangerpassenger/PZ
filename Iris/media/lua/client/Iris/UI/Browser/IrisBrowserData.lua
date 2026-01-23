--[[
    IrisBrowserData.lua - Iris 브라우저 데이터 캐시
    
    Rule Engine 결과(Item → Set<Tag>)를 역인덱싱한 표현 전용 캐시
    
    규칙:
    - OnGameStart 1회 생성
    - 실시간 계산 ❌
    - 틱 훅 ❌
    - Ruleset 직접 접근 ❌
    
    구조: Category → Subcategory → ItemList
]]

local IrisBrowserData = {}

-- 의존성 (lazy load)
local IrisAPI = nil
local IrisRuleExecutor = nil

-- 캐시 데이터
IrisBrowserData._cache = nil
IrisBrowserData._built = false

-- 대분류 고정 순서 (정렬 규칙에 따라)
IrisBrowserData.CATEGORY_ORDER = {
    "Tool",
    "Combat", 
    "Consumable",
    "Resource",
    "Literature",
    "Wearable",
}

-- 대분류 → 소분류 코드 매핑 (Ruleset 태그 형식)
IrisBrowserData.SUBCATEGORY_MAP = {
    ["Tool"] = {
        "1-A", "1-B", "1-C", "1-D", "1-E", "1-F", "1-G", "1-H", "1-I", "1-J"
    },
    ["Combat"] = {
        "2-A", "2-B", "2-C", "2-D", "2-E", "2-F", "2-G", "2-H", "2-I", "2-J", "2-K", "2-L"
    },
    ["Consumable"] = {
        "3-A", "3-B", "3-C", "3-D", "3-E"
    },
    ["Resource"] = {
        "4-A", "4-B", "4-C", "4-D", "4-E", "4-F"
    },
    ["Literature"] = {
        "5-A", "5-B", "5-C", "5-D"
    },
    ["Wearable"] = {
        "6-A", "6-B", "6-C", "6-D", "6-E", "6-F", "6-G", "6-H"
    },
}

-- 소분류 코드 → 표시 이름 매핑 (REASON_LABELS 정적 사전)
IrisBrowserData.SUBCATEGORY_LABELS = {
    -- Tool (1)
    ["1-A"] = "건설/제작",
    ["1-B"] = "분해/개방",
    ["1-C"] = "정비",
    ["1-D"] = "조리",
    ["1-E"] = "농업/채집",
    ["1-F"] = "의료",
    ["1-G"] = "포획",
    ["1-H"] = "광원/점화",
    ["1-I"] = "통신",
    ["1-J"] = "전력",
    -- Combat (2)
    ["2-A"] = "도끼류",
    ["2-B"] = "장둔기",
    ["2-C"] = "단둔기",
    ["2-D"] = "장검류",
    ["2-E"] = "단검류",
    ["2-F"] = "창류",
    ["2-G"] = "권총",
    ["2-H"] = "소총",
    ["2-I"] = "산탄총",
    ["2-J"] = "투척/폭발",
    ["2-K"] = "탄약",
    ["2-L"] = "총기부품",
    -- Consumable (3)
    ["3-A"] = "식품",
    ["3-B"] = "음료",
    ["3-C"] = "의약품",
    ["3-D"] = "기호품",
    ["3-E"] = "약초",
    -- Resource (4)
    ["4-A"] = "건설 재료",
    ["4-B"] = "조리 재료",
    ["4-C"] = "의료 재료",
    ["4-D"] = "연료",
    ["4-E"] = "전자부품",
    ["4-F"] = "기타 재료",
    -- Literature (5)
    ["5-A"] = "스킬북",
    ["5-B"] = "레시피잡지",
    ["5-C"] = "지도",
    ["5-D"] = "일반 서적",
    -- Wearable (6)
    ["6-A"] = "모자/헬멧",
    ["6-B"] = "상의",
    ["6-C"] = "하의",
    ["6-D"] = "장갑",
    ["6-E"] = "신발",
    ["6-F"] = "배낭",
    ["6-G"] = "힙색",
    ["6-H"] = "액세서리",
}

--- 의존성 로드
local function ensureDeps()
    if not IrisAPI then
        local ok, result = pcall(require, "Iris/IrisAPI")
        if ok then IrisAPI = result end
    end
    if not IrisRuleExecutor then
        local ok, result = pcall(require, "Iris/Rules/engine/IrisRuleExecutor")
        if ok then IrisRuleExecutor = result end
    end
end

--- 태그에서 카테고리/소분류 추출
--- @param tag string (예: "Tool.Construction")
--- @return string|nil category
--- @return string|nil subcategory
local function parseTag(tag)
    if not tag or type(tag) ~= "string" then
        return nil, nil
    end
    
    local category, subcategory = tag:match("^([^%.]+)%.(.+)$")
    return category, subcategory
end

--- 캐시 초기화 (빈 구조)
local function initEmptyCache()
    local cache = {
        categories = {},
        itemsByFullType = {},  -- fullType → item 역참조
    }
    
    -- 고정 순서대로 카테고리 초기화
    for _, catName in ipairs(IrisBrowserData.CATEGORY_ORDER) do
        cache.categories[catName] = {
            name = catName,
            subcategories = {},
        }
        
        -- 서브카테고리 초기화 (빈 상태)
        local subcats = IrisBrowserData.SUBCATEGORY_MAP[catName] or {}
        for _, subName in ipairs(subcats) do
            cache.categories[catName].subcategories[subName] = {
                name = subName,
                items = {},  -- { fullType = true } 형태의 set
                count = 0,
            }
        end
    end
    
    return cache
end

--- 브라우저 데이터 빌드 (1회 호출)
--- @return boolean success
function IrisBrowserData.build()
    if IrisBrowserData._built then
        print("[IrisBrowserData] Already built, skipping")
        return true
    end
    
    print("[IrisBrowserData] Building cache...")
    print("[IrisBrowserData] DEBUG: Step 1 - ensureDeps()")
    ensureDeps()
    print("[IrisBrowserData] DEBUG: Step 1 OK - IrisAPI=" .. tostring(IrisAPI ~= nil))
    
    -- 캐시 초기화
    print("[IrisBrowserData] DEBUG: Step 2 - initEmptyCache()")
    IrisBrowserData._cache = initEmptyCache()
    print("[IrisBrowserData] DEBUG: Step 2 OK")
    
    -- IrisAPI 확인
    if not IrisAPI then
        print("[IrisBrowserData] WARNING: IrisAPI not available, cache empty")
        IrisBrowserData._built = true
        return true
    end
    
    -- getAllItems 존재 확인
    print("[IrisBrowserData] DEBUG: Step 3 - checking getAllItems")
    if not getAllItems then
        print("[IrisBrowserData] WARNING: getAllItems not available")
        IrisBrowserData._built = true
        return true
    end
    print("[IrisBrowserData] DEBUG: Step 3 OK - getAllItems exists")
    
    -- 모든 아이템 순회하여 역인덱싱
    print("[IrisBrowserData] DEBUG: Step 4 - calling getAllItems()")
    local allItemsOk, allItems = pcall(getAllItems)
    print("[IrisBrowserData] DEBUG: Step 4 result - ok=" .. tostring(allItemsOk) .. ", allItems=" .. tostring(allItems ~= nil))
    if not allItemsOk or not allItems then
        print("[IrisBrowserData] WARNING: getAllItems() failed - error=" .. tostring(allItems))
        IrisBrowserData._built = true
        return true
    end
    
    -- size 메서드 확인
    print("[IrisBrowserData] DEBUG: Step 5 - checking allItems.size")
    if not allItems.size then
        print("[IrisBrowserData] WARNING: allItems has no size method")
        IrisBrowserData._built = true
        return true
    end
    print("[IrisBrowserData] DEBUG: Step 5 OK")
    
    print("[IrisBrowserData] DEBUG: Step 6 - calling allItems:size()")
    local sizeOk, itemsSize = pcall(function() return allItems:size() end)
    print("[IrisBrowserData] DEBUG: Step 6 result - ok=" .. tostring(sizeOk) .. ", size=" .. tostring(itemsSize))
    if not sizeOk or not itemsSize then
        print("[IrisBrowserData] WARNING: allItems:size() failed")
        IrisBrowserData._built = true
        return true
    end
    
    print("[IrisBrowserData] DEBUG: Step 7 - starting loop, itemsSize=" .. tostring(itemsSize))
    
    local itemCount = 0
    local taggedCount = 0
    local errorCount = 0
    local maxErrors = 5  -- 최대 5개 에러만 로그
    
    for i = 0, itemsSize - 1 do
        -- 진행 상황 로그 (매 1000개마다)
        if i % 1000 == 0 then
            print("[IrisBrowserData] DEBUG: Processing item " .. i .. "/" .. itemsSize)
        end
        
        local getOk, item = pcall(function() return allItems:get(i) end)
        if not getOk then
            if errorCount < maxErrors then
                print("[IrisBrowserData] DEBUG: allItems:get(" .. i .. ") failed: " .. tostring(item))
            end
            errorCount = errorCount + 1
        elseif item then
            -- fullType 추출 (안전하게)
            local fullType = nil
            local nameOk, name = pcall(function() return item:getFullName() end)
            if not nameOk then
                if errorCount < maxErrors then
                    print("[IrisBrowserData] DEBUG: item:getFullName() failed at " .. i .. ": " .. tostring(name))
                end
                errorCount = errorCount + 1
            elseif name then
                fullType = tostring(name)
            end
            
            if fullType then
                itemCount = itemCount + 1
                
                -- 해당 아이템의 태그 가져오기
                local tags = {}
                local tagOk, tagResult = pcall(function() return IrisAPI.getTagsForItem(item) end)
                if not tagOk then
                    if errorCount < maxErrors then
                        print("[IrisBrowserData] DEBUG: IrisAPI.getTagsForItem() failed for " .. fullType .. ": " .. tostring(tagResult))
                    end
                    errorCount = errorCount + 1
                elseif tagResult and type(tagResult) == "table" then
                    tags = tagResult
                end
                
                -- 태그가 있으면 역인덱싱
                local nextOk, hasNext = pcall(function() return next(tags) end)
                if not nextOk then
                    if errorCount < maxErrors then
                        print("[IrisBrowserData] DEBUG: next(tags) failed for " .. fullType .. ": " .. tostring(hasNext))
                    end
                    errorCount = errorCount + 1
                elseif hasNext then
                    taggedCount = taggedCount + 1
                    IrisBrowserData._cache.itemsByFullType[fullType] = item
                    
                    for tag, _ in pairs(tags) do
                        local category, subcategory = parseTag(tag)
                        if category and subcategory then
                            local catData = IrisBrowserData._cache.categories[category]
                            if catData and catData.subcategories and catData.subcategories[subcategory] then
                                -- 중복 표시 정책: 모든 해당 소분류에 추가
                                if not catData.subcategories[subcategory].items[fullType] then
                                    catData.subcategories[subcategory].items[fullType] = true
                                    catData.subcategories[subcategory].count = 
                                        catData.subcategories[subcategory].count + 1
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    
    print("[IrisBrowserData] DEBUG: Loop completed, errors=" .. errorCount)
    
    -- 규칙 로드 상태 확인 (로그 끝에 출력되도록)
    local rulesCount = 0
    if IrisAPI and IrisAPI.ensureInitialized then
        IrisAPI.ensureInitialized()
    end
    local IrisRuleLoader = nil
    local loaderOk, loaderResult = pcall(require, "Iris/Rules/engine/IrisRuleLoader")
    if loaderOk and loaderResult then
        IrisRuleLoader = loaderResult
        local rules = IrisRuleLoader.getRules()
        if rules then
            rulesCount = #rules
        end
    end
    print("[IrisBrowserData] DEBUG: Rules loaded = " .. rulesCount)
    
    IrisBrowserData._built = true
    print("[IrisBrowserData] Cache built: " .. itemCount .. " items scanned, " .. 
          taggedCount .. " tagged, " .. rulesCount .. " rules")
    
    return true
end

--- 대분류 목록 반환 (고정 순서)
--- @return table categories (name, subcategoryCount)
function IrisBrowserData.getCategories()
    if not IrisBrowserData._built then
        return {}
    end
    
    local result = {}
    for _, catName in ipairs(IrisBrowserData.CATEGORY_ORDER) do
        local catData = IrisBrowserData._cache.categories[catName]
        if catData then
            local subCount = 0
            for _ in pairs(catData.subcategories) do
                subCount = subCount + 1
            end
            table.insert(result, {
                name = catName,
                subcategoryCount = subCount,
            })
        end
    end
    return result
end

--- 특정 대분류의 소분류 목록 반환 (코드순 정렬)
--- @param categoryName string
--- @return table subcategories (code, label, itemCount)
function IrisBrowserData.getSubcategories(categoryName)
    if not IrisBrowserData._built or not categoryName then
        return {}
    end
    
    local catData = IrisBrowserData._cache.categories[categoryName]
    if not catData then
        return {}
    end
    
    local result = {}
    for subCode, subData in pairs(catData.subcategories) do
        local label = IrisBrowserData.SUBCATEGORY_LABELS[subCode] or subCode
        table.insert(result, {
            name = subCode,  -- 내부 코드 (태그 매칭용)
            label = label,  -- 표시 이름
            itemCount = subData.count,
        })
    end
    
    -- 코드순 정렬 (1-A, 1-B, ... 2-A, 2-B, ...)
    table.sort(result, function(a, b)
        return a.name < b.name
    end)
    
    return result
end

--- 특정 소분류의 아이템 목록 반환 (DisplayName 알파벳순)
--- @param categoryName string
--- @param subcategoryName string
--- @return table items (fullType, displayName)
function IrisBrowserData.getItems(categoryName, subcategoryName)
    if not IrisBrowserData._built or not categoryName or not subcategoryName then
        return {}
    end
    
    local catData = IrisBrowserData._cache.categories[categoryName]
    if not catData or not catData.subcategories[subcategoryName] then
        return {}
    end
    
    local result = {}
    for fullType, _ in pairs(catData.subcategories[subcategoryName].items) do
        local item = IrisBrowserData._cache.itemsByFullType[fullType]
        local displayName = fullType
        if item and item.getDisplayName then
            local ok, name = pcall(function() return item:getDisplayName() end)
            if ok and name then
                displayName = name
            end
        end
        table.insert(result, {
            fullType = fullType,
            displayName = displayName,
        })
    end
    
    -- DisplayName 알파벳순 정렬
    table.sort(result, function(a, b)
        return a.displayName < b.displayName
    end)
    
    return result
end

--- 전체 검색 (DisplayName/fullType 기준)
--- @param query string
--- @return table items (fullType, displayName, category, subcategory)
function IrisBrowserData.searchAll(query)
    if not IrisBrowserData._built or not query or query == "" then
        return {}
    end
    
    local queryLower = query:lower()
    local result = {}
    
    for fullType, item in pairs(IrisBrowserData._cache.itemsByFullType) do
        local displayName = fullType
        if item and item.getDisplayName then
            local ok, name = pcall(function() return item:getDisplayName() end)
            if ok and name then
                displayName = name
            end
        end
        
        -- DisplayName 또는 fullType에서 검색
        if displayName:lower():find(queryLower, 1, true) or 
           fullType:lower():find(queryLower, 1, true) then
            -- 첫 번째 카테고리/소분류 찾기 (네비게이션용)
            local foundCat, foundSub = nil, nil
            for catName, catData in pairs(IrisBrowserData._cache.categories) do
                for subName, subData in pairs(catData.subcategories) do
                    if subData.items[fullType] then
                        foundCat, foundSub = catName, subName
                        break
                    end
                end
                if foundCat then break end
            end
            
            table.insert(result, {
                fullType = fullType,
                displayName = displayName,
                category = foundCat,
                subcategory = foundSub,
            })
        end
    end
    
    -- DisplayName 알파벳순 정렬
    table.sort(result, function(a, b)
        return a.displayName < b.displayName
    end)
    
    return result
end

--- 아이템 객체 반환
--- @param fullType string
--- @return InventoryItem|nil
function IrisBrowserData.getItem(fullType)
    if not IrisBrowserData._built or not fullType then
        return nil
    end
    return IrisBrowserData._cache.itemsByFullType[fullType]
end

return IrisBrowserData
