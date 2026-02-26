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

-- 번역 헬퍼 (PZ getText 사용)
-- Note: PZ Lua는 UTF-8 한글을 제대로 처리하지 못함
-- 따라서 Lua 파일 내 직접 한글 사용 대신 PZ 번역 시스템(getText) 사용 필요
-- PZ 번역 시스템이 작동하지 않으면 영어 fallback 사용
local TRANSLATIONS_KO = {
    -- 대분류
    Iris_Cat_Tool = "\235\143\132\234\181\172",  -- 도구
    Iris_Cat_Combat = "\236\160\132\237\136\172",  -- 전투
    Iris_Cat_Consumable = "\236\134\140\235\170\168\237\146\136",  -- 소모품
    Iris_Cat_Resource = "\236\158\144\236\155\144",  -- 자원
    Iris_Cat_Literature = "\235\172\184\237\151\140",  -- 문헌
    Iris_Cat_Wearable = "\236\157\152\235\165\152",  -- 의류
    Iris_Cat_Furniture = "\234\176\128\234\181\172",  -- 가구
    Iris_Cat_Vehicle = "\236\176\168\235\159\137",  -- 차량
    Iris_Cat_Misc = "\234\184\176\237\131\128",  -- 기타

    -- 소분류
    Iris_Sub_1A = "\234\177\180\236\132\164\47\236\160\156\236\158\145",  -- 건설/제작
    Iris_Sub_1B = "\235\182\132\237\149\180\47\234\176\156\235\176\169",  -- 분해/개방
    Iris_Sub_1C = "\236\160\149\235\185\132",  -- 정비
    Iris_Sub_1D = "\236\154\148\235\166\172",  -- 요리
    Iris_Sub_1E = "\235\134\141\236\151\133\47\236\177\132\236\167\145",  -- 농업/채집
    Iris_Sub_1F = "\236\157\152\235\163\140",  -- 의료
    Iris_Sub_1G = "\237\143\172\237\154\141",  -- 포획
    Iris_Sub_1H = "\234\180\145\236\155\144\47\236\160\144\237\153\148",  -- 광원/점화
    Iris_Sub_1I = "\237\134\181\236\139\160",  -- 통신
    Iris_Sub_1J = "\236\160\132\235\160\165",  -- 전력
    Iris_Sub_1K = "\235\179\180\236\149\136",  -- 보안
    Iris_Sub_1L = "\235\179\180\234\180\128\236\154\169\234\184\176",  -- 보관용기
    Iris_Sub_2A = "\235\143\132\235\129\188\235\165\152",  -- 도끼류
    Iris_Sub_2B = "\236\158\165\235\145\148\234\184\176",  -- 장둔기
    Iris_Sub_2C = "\235\139\168\235\145\148\234\184\176",  -- 단둔기
    Iris_Sub_2D = "\236\158\165\234\178\128\235\165\152",  -- 장검류
    Iris_Sub_2E = "\235\139\168\234\178\128\235\165\152",  -- 단검류
    Iris_Sub_2F = "\236\176\189\235\165\152",  -- 창류
    Iris_Sub_2G = "\234\182\140\236\180\157",  -- 권총
    Iris_Sub_2H = "\236\134\140\236\180\157",  -- 소총
    Iris_Sub_2I = "\236\130\176\237\131\132\236\180\157",  -- 산탄총
    Iris_Sub_2J = "\237\136\172\236\178\153\47\237\143\173\235\176\156",  -- 투척/폭발
    Iris_Sub_2K = "\237\131\132\236\149\189",  -- 탄약
    Iris_Sub_3A = "\236\139\157\237\146\136",  -- 식품
    Iris_Sub_3B = "\236\157\140\235\163\140",  -- 음료
    Iris_Sub_3C = "\236\157\152\236\149\189\237\146\136",  -- 의약품
    Iris_Sub_3D = "\234\184\176\237\152\184\237\146\136",  -- 기호품
    Iris_Sub_3E = "\236\149\189\236\180\136",  -- 약초
    Iris_Sub_4A = "\234\177\180\236\132\164\236\158\172\235\163\140",  -- 건설재료
    Iris_Sub_4B = "\236\161\176\235\166\172\32\236\158\172\235\163\140",  -- 조리 재료
    Iris_Sub_4C = "\236\157\152\235\163\140\236\158\172\235\163\140",  -- 의료재료
    Iris_Sub_4D = "\236\151\176\235\163\140",  -- 연료
    Iris_Sub_4E = "\236\160\132\236\158\144\235\182\128\237\146\136",  -- 전자부품
    Iris_Sub_5A = "\236\138\164\237\130\172\235\182\129",  -- 스킬북
    Iris_Sub_5B = "\235\160\136\236\139\156\237\148\188\236\158\161\236\167\128",  -- 레시피잡지
    Iris_Sub_5C = "\236\167\128\235\143\132",  -- 지도
    Iris_Sub_5D = "\236\157\188\235\176\152\236\132\156\236\160\129",  -- 일반서적
    Iris_Sub_6A = "\235\170\168\236\158\144\47\237\151\172\235\169\167",  -- 모자/헬멧
    Iris_Sub_6B = "\236\131\129\236\157\152",  -- 상의
    Iris_Sub_6C = "\237\149\152\236\157\152",  -- 하의
    Iris_Sub_6D = "\236\158\165\234\176\145",  -- 장갑
    Iris_Sub_6E = "\236\139\160\235\176\156",  -- 신발
    Iris_Sub_6F = "\235\176\176\235\130\173",  -- 배낭
    Iris_Sub_6G = "\236\149\161\236\132\184\236\132\156\235\166\172",  -- 액세서리
    Iris_Sub_7A = "\237\131\136\236\176\169\32\234\176\128\234\181\172",  -- 탈착 가구
    Iris_Sub_8A = "\236\163\188\237\150\137\234\179\132",  -- 주행계
    Iris_Sub_8B = "\236\176\168\236\178\180\47\235\182\128\236\134\141",  -- 차체/부속
    Iris_Sub_9A = "\236\158\161\237\153\148",  -- 잡화
}

-- 현재 언어 감지 (Translator 사용)
local function getCurrentLanguage()
    if Translator and Translator.getLanguage then
        local ok, lang = pcall(Translator.getLanguage)
        if ok and lang then
            return tostring(lang):upper()
        end
    end
    
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

local function tr(key, fallback)
    -- 1순위: 자체 번역 테이블 (TRANSLATIONS_KO)
    if TRANSLATIONS_KO and TRANSLATIONS_KO[key] then
        return TRANSLATIONS_KO[key]
    end

    -- 2순위: IrisTranslationLoader 사용
    if IrisTranslationLoader and IrisTranslationLoader.get then
        local result = IrisTranslationLoader.get(key, nil)
        if result and result ~= key then
            return result
        end
    end
    
    -- 3순위: PZ getText() 시도
    if getText and type(getText) == "function" then
        local ok, result = pcall(getText, key)
        if ok and result and result ~= key then
            return result
        end
    end
    
    -- fallback (영어)
    return fallback or key
end

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
    "Furniture",
    "Vehicle",
    "Misc",
}

-- 대분류 코드 → 번역키 + fallback 매핑
IrisBrowserData.CATEGORY_KEYS = {
    ["Tool"] = { key = "Iris_Cat_Tool", fallback = "Tool" },
    ["Combat"] = { key = "Iris_Cat_Combat", fallback = "Combat" },
    ["Consumable"] = { key = "Iris_Cat_Consumable", fallback = "Consumable" },
    ["Resource"] = { key = "Iris_Cat_Resource", fallback = "Resource" },
    ["Literature"] = { key = "Iris_Cat_Literature", fallback = "Literature" },
    ["Wearable"] = { key = "Iris_Cat_Wearable", fallback = "Wearable" },
    ["Furniture"] = { key = "Iris_Cat_Furniture", fallback = "Furniture" },
    ["Vehicle"] = { key = "Iris_Cat_Vehicle", fallback = "Vehicle" },
    ["Misc"] = { key = "Iris_Cat_Misc", fallback = "Misc" },
}

--- 대분류 라벨 가져오기 (번역 지원)
function IrisBrowserData.getCategoryLabel(catName)
    local entry = IrisBrowserData.CATEGORY_KEYS[catName]
    if entry then
        return tr(entry.key, entry.fallback)
    end
    return catName
end

-- 대분류 → 소분류 코드 매핑 (Ruleset 태그 형식)
IrisBrowserData.SUBCATEGORY_MAP = {
    ["Tool"] = {
        "1-A", "1-B", "1-C", "1-D", "1-E", "1-F", "1-G", "1-H", "1-I", "1-J", "1-K", "1-L"
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
        "6-A", "6-B", "6-C", "6-D", "6-E", "6-F", "6-G"
    },
    ["Furniture"] = {
        "7-A"
    },
    ["Vehicle"] = {
        "8-A", "8-B"
    },
    ["Misc"] = {
        "9-A"
    },
}

-- 소분류 코드 → 번역키 + fallback 매핑
-- Uses PZ getText() for localization, falls back to English
IrisBrowserData.SUBCATEGORY_KEYS = {
    -- Tool (1)
    ["1-A"] = { key = "Iris_Sub_1A", fallback = "Construction/Crafting" },
    ["1-B"] = { key = "Iris_Sub_1B", fallback = "Disassembly/Opening" },
    ["1-C"] = { key = "Iris_Sub_1C", fallback = "Maintenance" },
    ["1-D"] = { key = "Iris_Sub_1D", fallback = "Cooking" },
    ["1-E"] = { key = "Iris_Sub_1E", fallback = "Farming/Foraging" },
    ["1-F"] = { key = "Iris_Sub_1F", fallback = "Medical" },
    ["1-G"] = { key = "Iris_Sub_1G", fallback = "Trapping" },
    ["1-H"] = { key = "Iris_Sub_1H", fallback = "Light/Ignition" },
    ["1-I"] = { key = "Iris_Sub_1I", fallback = "Communication" },
    ["1-J"] = { key = "Iris_Sub_1J", fallback = "Electrical" },
    ["1-K"] = { key = "Iris_Sub_1K", fallback = "Storage Containers" },
    ["1-L"] = { key = "Iris_Sub_1L", fallback = "Bags" },
    -- Combat (2)
    ["2-A"] = { key = "Iris_Sub_2A", fallback = "Axes" },
    ["2-B"] = { key = "Iris_Sub_2B", fallback = "Long Blunt" },
    ["2-C"] = { key = "Iris_Sub_2C", fallback = "Short Blunt" },
    ["2-D"] = { key = "Iris_Sub_2D", fallback = "Long Blades" },
    ["2-E"] = { key = "Iris_Sub_2E", fallback = "Short Blades" },
    ["2-F"] = { key = "Iris_Sub_2F", fallback = "Spears" },
    ["2-G"] = { key = "Iris_Sub_2G", fallback = "Pistols" },
    ["2-H"] = { key = "Iris_Sub_2H", fallback = "Rifles" },
    ["2-I"] = { key = "Iris_Sub_2I", fallback = "Shotguns" },
    ["2-J"] = { key = "Iris_Sub_2J", fallback = "Explosives/Thrown" },
    ["2-K"] = { key = "Iris_Sub_2K", fallback = "Ammunition" },
    ["2-L"] = { key = "Iris_Sub_2L", fallback = "Gun Parts" },
    -- Consumable (3)
    ["3-A"] = { key = "Iris_Sub_3A", fallback = "Food" },
    ["3-B"] = { key = "Iris_Sub_3B", fallback = "Drinks" },
    ["3-C"] = { key = "Iris_Sub_3C", fallback = "Medicine" },
    ["3-D"] = { key = "Iris_Sub_3D", fallback = "Luxury Items" },
    ["3-E"] = { key = "Iris_Sub_3E", fallback = "Herbs" },
    -- Resource (4)
    ["4-A"] = { key = "Iris_Sub_4A", fallback = "Construction Material" },
    ["4-B"] = { key = "Iris_Sub_4B", fallback = "Cooking Ingredients" },
    ["4-C"] = { key = "Iris_Sub_4C", fallback = "Medical Supplies" },
    ["4-D"] = { key = "Iris_Sub_4D", fallback = "Fuel" },
    ["4-E"] = { key = "Iris_Sub_4E", fallback = "Electronics" },
    ["4-F"] = { key = "Iris_Sub_4F", fallback = "Misc Materials" },
    -- Literature (5)
    ["5-A"] = { key = "Iris_Sub_5A", fallback = "Skill Books" },
    ["5-B"] = { key = "Iris_Sub_5B", fallback = "Recipe Magazines" },
    ["5-C"] = { key = "Iris_Sub_5C", fallback = "Maps" },
    ["5-D"] = { key = "Iris_Sub_5D", fallback = "General Books" },
    -- Wearable (6)
    ["6-A"] = { key = "Iris_Sub_6A", fallback = "Hats/Helmets" },
    ["6-B"] = { key = "Iris_Sub_6B", fallback = "Tops" },
    ["6-C"] = { key = "Iris_Sub_6C", fallback = "Bottoms" },
    ["6-D"] = { key = "Iris_Sub_6D", fallback = "Gloves" },
    ["6-E"] = { key = "Iris_Sub_6E", fallback = "Footwear" },
    ["6-F"] = { key = "Iris_Sub_6F", fallback = "Backpacks" },
    ["6-G"] = { key = "Iris_Sub_6G", fallback = "Accessories" },
    -- Furniture (7)
    ["7-A"] = { key = "Iris_Sub_7A", fallback = "Moveables" },
    -- Vehicle (8)
    ["8-A"] = { key = "Iris_Sub_8A", fallback = "Drivetrain" },
    ["8-B"] = { key = "Iris_Sub_8B", fallback = "Body/Parts" },
    -- Misc (9)
    ["9-A"] = { key = "Iris_Sub_9A", fallback = "Miscellaneous" },
}

--- 소분류 라벨 가져오기 (번역 지원)
function IrisBrowserData.getSubcategoryLabel(subCode)
    local entry = IrisBrowserData.SUBCATEGORY_KEYS[subCode]
    if entry then
        return tr(entry.key, entry.fallback)
    end
    return subCode
end

--- 의존성 로드
local function ensureDeps()
    if not IrisAPI then
        local ok, result = pcall(require, "Iris/IrisAPI")
        if ok then IrisAPI = result end
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
                -- Note: next()를 pcall로 감싸면 Kahlua VM에서 오류 발생
                -- 대신 직접 테이블 순회로 확인
                local hasAnyTag = false
                for _ in pairs(tags) do
                    hasAnyTag = true
                    break
                end
                
                if hasAnyTag then
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
    
    -- 정적 분류 데이터 통계 (헌법적 설계: Rule Engine 없음)
    print("[IrisBrowserData] DEBUG: Static classifications used")
    
    IrisBrowserData._built = true
    print("[IrisBrowserData] Cache built: " .. itemCount .. " items scanned, " .. 
          taggedCount .. " tagged (static data)")
    
    return true
end

--- 대분류 목록 반환 (고정 순서)
--- @return table categories (name, subcategoryCount)
function IrisBrowserData.getCategories()
    print("[IrisBrowserData] getCategories() called")
    print("[IrisBrowserData] _built = " .. tostring(IrisBrowserData._built))
    
    if not IrisBrowserData._built then
        print("[IrisBrowserData] NOT BUILT, returning empty")
        return {}
    end
    
    print("[IrisBrowserData] _cache exists = " .. tostring(IrisBrowserData._cache ~= nil))
    print("[IrisBrowserData] CATEGORY_ORDER count = " .. #IrisBrowserData.CATEGORY_ORDER)
    
    local result = {}
    for _, catName in ipairs(IrisBrowserData.CATEGORY_ORDER) do
        local catData = IrisBrowserData._cache.categories[catName]
        if catData then
            local subCount = 0
            local totalItems = 0
            for subCode, subData in pairs(catData.subcategories) do
                subCount = subCount + 1
                totalItems = totalItems + (subData.count or 0)
            end
            print("[IrisBrowserData] Category '" .. catName .. "': " .. subCount .. " subcategories, " .. totalItems .. " items")
            table.insert(result, {
                name = catName,
                label = IrisBrowserData.getCategoryLabel(catName),
                subcategoryCount = subCount,
            })
        else
            print("[IrisBrowserData] Category '" .. catName .. "' NOT FOUND in cache")
        end
    end
    print("[IrisBrowserData] getCategories() returning " .. #result .. " categories")
    return result
end

--- 접기 후 아이템 개수 계산 (내부용)
--- DisplayName 기반 접기 + 차단 가드 적용 후 남는 개수
--- @param categoryName string
--- @param subCode string
--- @param subData table
--- @return number foldedCount
function IrisBrowserData._calculateFoldedCount(categoryName, subCode, subData)
    -- DisplayName별로 그룹화
    local itemsByDisplayName = {}
    
    for fullType, _ in pairs(subData.items) do
        local item = IrisBrowserData._cache.itemsByFullType[fullType]
        
        local displayName = fullType
        if item and item.getDisplayName then
            local ok, name = pcall(function() return item:getDisplayName() end)
            if ok and name then
                displayName = name
            end
        end
        
        -- 아이템 타입 가져오기
        local itemType = "Normal"
        if item and item.getType then
            local ok, t = pcall(function() return item:getType() end)
            if ok and t then itemType = tostring(t) end
        end
        
        -- 레시피 여부 확인
        local hasRecipe = false
        if IrisAPI and IrisAPI.getRecipeConnectionsForItem then
            local ok, list = pcall(function() return IrisAPI.getRecipeConnectionsForItem(item) end)
            if ok and list and #list > 0 then
                hasRecipe = true
            end
        end
        
        if not itemsByDisplayName[displayName] then
            itemsByDisplayName[displayName] = {}
        end
        
        table.insert(itemsByDisplayName[displayName], {
            itemType = itemType,
            hasRecipe = hasRecipe,
        })
    end
    
    -- 접기 후 개수 계산
    local foldedCount = 0
    
    for displayName, group in pairs(itemsByDisplayName) do
        if #group == 1 then
            foldedCount = foldedCount + 1
        else
            -- 차단 가드 확인
            local firstType = group[1].itemType
            local firstHasRecipe = group[1].hasRecipe
            local canFold = true
            
            for i = 2, #group do
                if group[i].itemType ~= firstType then
                    canFold = false
                    break
                end
                if group[i].hasRecipe ~= firstHasRecipe then
                    canFold = false
                    break
                end
            end
            
            if canFold then
                foldedCount = foldedCount + 1  -- 접힌 그룹 = 1개로 카운트
            else
                foldedCount = foldedCount + #group  -- 접기 불가 = 각각 카운트
            end
        end
    end
    
    return foldedCount
end

--- 특정 대분류의 소분류 목록 반환 (코드순 정렬)
--- @param categoryName string
--- @return table subcategories (code, label, itemCount)
function IrisBrowserData.getSubcategories(categoryName)
    print("[IrisBrowserData] getSubcategories('" .. tostring(categoryName) .. "') called")
    
    if not IrisBrowserData._built then
        print("[IrisBrowserData] NOT BUILT, returning empty")
        return {}
    end
    if not categoryName then
        print("[IrisBrowserData] categoryName is nil, returning empty")
        return {}
    end
    
    local catData = IrisBrowserData._cache.categories[categoryName]
    if not catData then
        print("[IrisBrowserData] Category '" .. categoryName .. "' NOT FOUND in cache")
        print("[IrisBrowserData] Available categories:")
        for k, _ in pairs(IrisBrowserData._cache.categories) do
            print("[IrisBrowserData]   - '" .. tostring(k) .. "'")
        end
        return {}
    end
    
    print("[IrisBrowserData] Found category, subcategories table exists = " .. tostring(catData.subcategories ~= nil))
    
    local result = {}
    for subCode, subData in pairs(catData.subcategories) do
        local label = IrisBrowserData.getSubcategoryLabel(subCode)
        
        -- v3.0.0: 접기 후 개수 계산 (DisplayName 기반)
        local foldedCount = IrisBrowserData._calculateFoldedCount(categoryName, subCode, subData)
        
        print("[IrisBrowserData]   Subcategory '" .. subCode .. "': raw=" .. tostring(subData.count) .. ", folded=" .. tostring(foldedCount))
        table.insert(result, {
            name = subCode,  -- 내부 코드 (태그 매칭용)
            label = label,  -- 표시 이름
            itemCount = foldedCount,  -- v3.0.0: 접기 후 개수
            rawCount = subData.count,  -- 원본 개수 (디버그용)
        })
    end
    
    -- 코드순 정렬 (1-A, 1-B, ... 2-A, 2-B, ...)
    table.sort(result, function(a, b)
        return a.name < b.name
    end)
    
    print("[IrisBrowserData] getSubcategories() returning " .. #result .. " subcategories")
    return result
end

--- 주 소분류 결정 헬퍼 함수 (내부용)
--- @param item InventoryItem
--- @param fullType string
--- @param currentTag string 현재 보고 있는 태그 (예: "Consumable.3-A")
--- @return boolean isPrimary
function IrisBrowserData._calculatePrimary(item, fullType, currentTag)
    local primaryTag = nil
    
    -- 1순위: IrisPrimarySubcategory에서 수동 고정 확인
    if IrisPrimarySubcategory and IrisPrimarySubcategory[fullType] then
        primaryTag = IrisPrimarySubcategory[fullType]
    -- 2순위: 태그 기반 자동 계산
    elseif IrisAPI and IrisAPI.getTagsForItem then
        local ok, tags = pcall(function() return IrisAPI.getTagsForItem(item) end)
        if ok and tags then
            -- 대분류 우선순위에 따라 주 소분류 결정
            local PRIORITY = { Tool = 1, Combat = 2, Consumable = 3, Resource = 4, Literature = 5, Wearable = 6 }
            local lowestPriority = 999
            local lowestCode = "ZZZ"
            
            for tag, _ in pairs(tags) do
                local cat, code = tag:match("^([^%.]+)%.(.+)$")
                if cat and code then
                    local priority = PRIORITY[cat] or 999
                    if priority < lowestPriority or 
                       (priority == lowestPriority and code < lowestCode) then
                        lowestPriority = priority
                        lowestCode = code
                        primaryTag = tag
                    end
                end
            end
        end
    end
    
    return primaryTag == currentTag
end

--- 특정 소분류의 아이템 목록 반환
--- 정렬 규칙:
---   1. 현재 소분류가 '주 소분류'인 아이템 → 먼저
---   2. 현재 소분류가 '보조 소분류'인 아이템 → 나중
---   3. 각 그룹 내에서는 DisplayName 알파벳순
--- @param categoryName string
--- @param subcategoryName string
--- @return table items (fullType, displayName, isPrimary)
function IrisBrowserData.getItems(categoryName, subcategoryName)
    print("[IrisBrowserData] getItems('" .. tostring(categoryName) .. "', '" .. tostring(subcategoryName) .. "') called")
    
    if not IrisBrowserData._built or not categoryName or not subcategoryName then
        print("[IrisBrowserData] getItems - not built or missing params")
        return {}
    end
    
    local catData = IrisBrowserData._cache.categories[categoryName]
    if not catData then
        print("[IrisBrowserData] getItems - category '" .. categoryName .. "' not found")
        return {}
    end
    
    if not catData.subcategories[subcategoryName] then
        print("[IrisBrowserData] getItems - subcategory '" .. subcategoryName .. "' not found in category")
        print("[IrisBrowserData] Available subcategories:")
        for k, _ in pairs(catData.subcategories) do
            print("[IrisBrowserData]   - '" .. k .. "'")
        end
        return {}
    end
    
    local subData = catData.subcategories[subcategoryName]
    print("[IrisBrowserData] Found subcategory, items count in set = " .. tostring(subData.count))
    
    -- 현재 소분류의 전체 태그 (예: "Consumable.3-B")
    local currentTag = categoryName .. "." .. subcategoryName
    
    -- =========================================================================
    -- DisplayName 기반 표현 접기 (v3.0.0)
    -- 목표: 같은 이름의 아이템을 목록에서 한 줄로 접는다
    -- 차단 가드: Type 다름, 레시피/우클릭 한쪽만 존재
    -- =========================================================================
    
    -- 1단계: 모든 아이템 수집 및 DisplayName 그룹화
    local itemsByDisplayName = {}  -- displayName -> { items[] }
    
    for fullType, _ in pairs(subData.items) do
        local item = IrisBrowserData._cache.itemsByFullType[fullType]
        
        local displayName = fullType
        if item and item.getDisplayName then
            local ok, name = pcall(function() return item:getDisplayName() end)
            if ok and name then
                displayName = name
            end
        end
        
        -- 아이템 타입 가져오기
        local itemType = "Normal"
        if item and item.getType then
            local ok, t = pcall(function() return item:getType() end)
            if ok and t then itemType = tostring(t) end
        end
        
        -- 레시피 여부 확인 (차단 가드용)
        local hasRecipe = false
        if IrisAPI and IrisAPI.getRecipeConnectionsForItem then
            local ok, list = pcall(function() return IrisAPI.getRecipeConnectionsForItem(item) end)
            if ok and list and #list > 0 then
                hasRecipe = true
            end
        end
        
        if not itemsByDisplayName[displayName] then
            itemsByDisplayName[displayName] = {}
        end
        
        table.insert(itemsByDisplayName[displayName], {
            fullType = fullType,
            item = item,
            itemType = itemType,
            hasRecipe = hasRecipe,
        })
    end
    
    -- 2단계: 그룹 내에서 차단 가드 적용 → 접기 여부 결정
    local result = {}
    
    for displayName, group in pairs(itemsByDisplayName) do
        if #group == 1 then
            -- 단일 아이템: 그냥 추가
            local e = group[1]
            local isPrimary = IrisBrowserData._calculatePrimary(e.item, e.fullType, currentTag)
            table.insert(result, {
                fullType = e.fullType,
                displayName = displayName,
                isPrimary = isPrimary,
                variants = nil,  -- 변형 없음
            })
        else
            -- 복수 아이템: 차단 가드 확인
            local firstType = group[1].itemType
            local firstHasRecipe = group[1].hasRecipe
            local canFold = true
            
            for i = 2, #group do
                -- 차단 가드 1: Type 다름
                if group[i].itemType ~= firstType then
                    canFold = false
                    break
                end
                -- 차단 가드 2: 레시피 존재 여부 다름
                if group[i].hasRecipe ~= firstHasRecipe then
                    canFold = false
                    break
                end
            end
            
            if canFold then
                -- 접기 허용: 대표 1개만 표시
                local representative = group[1]
                local variants = {}
                for _, e in ipairs(group) do
                    table.insert(variants, e.fullType)
                end
                table.sort(variants)  -- 사전순 정렬
                
                local isPrimary = IrisBrowserData._calculatePrimary(representative.item, representative.fullType, currentTag)
                table.insert(result, {
                    fullType = representative.fullType,
                    displayName = displayName,
                    isPrimary = isPrimary,
                    variants = variants,  -- 상세에서 표시용
                })
            else
                -- 접기 불가: 각각 개별 표시
                for _, e in ipairs(group) do
                    local isPrimary = IrisBrowserData._calculatePrimary(e.item, e.fullType, currentTag)
                    table.insert(result, {
                        fullType = e.fullType,
                        displayName = displayName,
                        isPrimary = isPrimary,
                        variants = nil,
                    })
                end
            end
        end
    end
    
    -- 정렬: isPrimary(true) 먼저, 그 다음 displayName 알파벳순, 그 다음 fullType
    table.sort(result, function(a, b)
        if a.isPrimary ~= b.isPrimary then
            return a.isPrimary  -- true가 먼저
        end
        if a.displayName ~= b.displayName then
            return a.displayName < b.displayName
        end
        return a.fullType < b.fullType
    end)
    
    print("[IrisBrowserData] getItems() returning " .. #result .. " items (DisplayName folding)")
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

--- 그룹의 변형 아이템 목록 반환
--- @param groupId string|nil 그룹 ID
--- @return table variants { fullType, displayName }[] or nil
function IrisBrowserData.getGroupVariants(groupId)
    if not groupId then return nil end
    if not IrisData or not IrisData.ItemGroups then return nil end
    
    local groupItems = IrisData.ItemGroups[groupId]
    if not groupItems then return nil end
    
    local result = {}
    for _, fullType in ipairs(groupItems) do
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
    
    -- DisplayName 정렬
    table.sort(result, function(a, b)
        return a.displayName < b.displayName
    end)
    
    return result
end

return IrisBrowserData
