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

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local IrisBrowserCategoryIndex = require("Iris/UI/Browser/IrisBrowserCategoryIndex")
local IrisBrowserFilters = require("Iris/UI/Browser/IrisBrowserFilters")
local IrisBrowserItemIndex = require("Iris/UI/Browser/IrisBrowserItemIndex")
local IrisBrowserClassificationIndex = require("Iris/UI/Browser/IrisBrowserClassificationIndex")
local IrisBrowserQuery = require("Iris/UI/Browser/IrisBrowserQuery")
local IrisBrowserVariantIndex = require("Iris/UI/Browser/IrisBrowserVariantIndex")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local debug = bootstrap.debug
local warn = bootstrap.warn

-- 의존성 (lazy load)
local IrisAPI = nil
local tr = TranslationResolver.get

-- 캐시 데이터
IrisBrowserData._cache = nil
IrisBrowserData._built = false

IrisBrowserData.CATEGORY_DEFINITIONS = IrisBrowserCategoryIndex.CATEGORY_DEFINITIONS
IrisBrowserData.CATEGORY_ORDER = IrisBrowserCategoryIndex.CATEGORY_ORDER
IrisBrowserData.CATEGORY_KEYS = IrisBrowserCategoryIndex.CATEGORY_KEYS
IrisBrowserData.SUBCATEGORY_MAP = IrisBrowserCategoryIndex.SUBCATEGORY_MAP
IrisBrowserData.SUBCATEGORY_KEYS = IrisBrowserCategoryIndex.SUBCATEGORY_KEYS

--- 대분류 라벨 가져오기 (번역 지원)
function IrisBrowserData.getCategoryLabel(catName)
    return IrisBrowserCategoryIndex.getCategoryLabel(catName, tr)
end

--- 소분류 라벨 가져오기 (번역 지원)
function IrisBrowserData.getSubcategoryLabel(subCode)
    return IrisBrowserCategoryIndex.getSubcategoryLabel(subCode, tr)
end

--- 의존성 로드
local function ensureDeps()
    if not IrisAPI then
        local ok, result = safeRequire("Iris/IrisAPI")
        if ok then IrisAPI = result end
    end
end

--- 브라우저 데이터 빌드 (1회 호출)
--- @return boolean success
function IrisBrowserData.build()
    if IrisBrowserData._built then
        debug("[IrisBrowserData] Already built, skipping")
        return true
    end
    
    debug("[IrisBrowserData] Building cache...")
    ensureDeps()

    local itemIndex = IrisBrowserItemIndex.build()
    local classificationIndex = IrisBrowserClassificationIndex.createEmpty(
        IrisBrowserData.CATEGORY_ORDER,
        IrisBrowserData.SUBCATEGORY_MAP
    )

    IrisBrowserData._cache = {
        itemIndex = itemIndex,
        classificationIndex = classificationIndex,
        itemsByFullType = itemIndex.itemsByFullType,
        categories = classificationIndex.categories,
        itemLocationsByFullType = classificationIndex.itemLocationsByFullType,
    }

    if not IrisAPI then
        warn("[IrisBrowserData] IrisAPI not available, classification index empty")
        IrisBrowserData._built = true
        return true
    end

    if not IrisAPI.Tags or not IrisAPI.Tags.getTagsForItem then
        warn("[IrisBrowserData] IrisAPI.Tags not available, classification index empty")
        IrisBrowserData._built = true
        return true
    end

    local taggedCount = 0
    local errorCount = 0
    local maxErrors = 5

    for fullType, item in pairs(itemIndex.itemsByFullType or {}) do
        local tags = {}
        local tagOk, tagResult = ProtectedCall.data(function()
            return IrisAPI.Tags.getTagsForItem(item)
        end)
        if not tagOk then
            if errorCount < maxErrors then
                debug("[IrisBrowserData] DEBUG: IrisAPI.Tags.getTagsForItem() failed for " .. fullType .. ": " .. tostring(tagResult))
            end
            errorCount = errorCount + 1
        elseif tagResult and type(tagResult) == "table" then
            tags = tagResult
        end

        if IrisBrowserClassificationIndex.addItem(classificationIndex, fullType, tags) then
            taggedCount = taggedCount + 1
        end
    end
    
    IrisBrowserData._built = true
    debug("[IrisBrowserData] Cache built: " .. tostring(itemIndex.itemCount) ..
          " items indexed, " .. taggedCount .. " tagged, errors=" .. errorCount)
    
    return true
end

--- 대분류 목록 반환 (고정 순서)
--- @return table categories (name, subcategoryCount)
function IrisBrowserData.getCategories()
    debug("[IrisBrowserData] getCategories() called")
    debug("[IrisBrowserData] _built = " .. tostring(IrisBrowserData._built))
    
    if not IrisBrowserData._built then
        debug("[IrisBrowserData] NOT BUILT, returning empty")
        return {}
    end
    
    debug("[IrisBrowserData] _cache exists = " .. tostring(IrisBrowserData._cache ~= nil))
    debug("[IrisBrowserData] CATEGORY_ORDER count = " .. #IrisBrowserData.CATEGORY_ORDER)

    local result = IrisBrowserFilters.getCategories(
        IrisBrowserData._cache,
        IrisBrowserData.CATEGORY_ORDER,
        IrisBrowserData.getCategoryLabel,
        debug
    )
    debug("[IrisBrowserData] getCategories() returning " .. #result .. " categories")
    return result
end

--- 접기 후 아이템 개수 계산 (내부용)
--- DisplayName 기반 접기 + 차단 가드 적용 후 남는 개수
--- @param categoryName string
--- @param subCode string
--- @param subData table
--- @return number foldedCount
function IrisBrowserData._calculateFoldedCount(categoryName, subCode, subData)
    return IrisBrowserVariantIndex.calculateFoldedCount(IrisBrowserData._cache, subData, IrisAPI)
end

--- 특정 대분류의 소분류 목록 반환 (코드순 정렬)
--- @param categoryName string
--- @return table subcategories (code, label, itemCount)
function IrisBrowserData.getSubcategories(categoryName)
    debug("[IrisBrowserData] getSubcategories('" .. tostring(categoryName) .. "') called")
    
    if not IrisBrowserData._built then
        debug("[IrisBrowserData] NOT BUILT, returning empty")
        return {}
    end
    if not categoryName then
        debug("[IrisBrowserData] categoryName is nil, returning empty")
        return {}
    end
    
    local result = IrisBrowserFilters.getSubcategories(
        IrisBrowserData._cache,
        categoryName,
        IrisBrowserData.getSubcategoryLabel,
        IrisBrowserData._calculateFoldedCount,
        debug
    )
    debug("[IrisBrowserData] getSubcategories() returning " .. #result .. " subcategories")
    return result
end

--- 주 소분류 결정 헬퍼 함수 (내부용)
--- @param item InventoryItem
--- @param fullType string
--- @param currentTag string 현재 보고 있는 태그 (예: "Consumable.3-A")
--- @return boolean isPrimary
function IrisBrowserData._calculatePrimary(item, fullType, currentTag)
    return IrisBrowserVariantIndex.calculatePrimary(item, fullType, currentTag, IrisAPI)
end

--- 특정 소분류의 아이템 목록 반환
--- 정렬 규칙:
---   1. 현재 소분류가 주 소분류인 아이템 → 먼저
---   2. 현재 소분류가 보조 소분류인 아이템 → 나중
---   3. 각 그룹 내에서는 DisplayName 알파벳순
--- @param categoryName string
--- @param subcategoryName string
--- @return table items (fullType, displayName, isPrimary)
function IrisBrowserData.getItems(categoryName, subcategoryName)
    debug("[IrisBrowserData] getItems('" .. tostring(categoryName) .. "', '" .. tostring(subcategoryName) .. "') called")
    
    if not IrisBrowserData._built or not categoryName or not subcategoryName then
        debug("[IrisBrowserData] getItems - not built or missing params")
        return {}
    end
    
    local result = IrisBrowserVariantIndex.getItems(
        IrisBrowserData._cache,
        categoryName,
        subcategoryName,
        IrisAPI,
        debug
    )
    debug("[IrisBrowserData] getItems() returning " .. #result .. " items (DisplayName folding)")
    return result
end

--- 전체 검색 (DisplayName/fullType 기준)
--- @param query string
--- @return table items (fullType, displayName, category, subcategory)
function IrisBrowserData.searchAll(query)
    if not IrisBrowserData._built or not query or query == "" then
        return {}
    end

    return IrisBrowserQuery.searchAll(IrisBrowserData._cache, query, IrisBrowserData.getItemLocation)
end

--- 아이템 객체 반환
--- @param fullType string
--- @return InventoryItem|nil
function IrisBrowserData.getItem(fullType)
    if not IrisBrowserData._built or not fullType then
        return nil
    end
    return IrisBrowserQuery.getItem(IrisBrowserData._cache, fullType)
end

--- 아이템의 브라우저 위치 반환 (selectItem용 사전 빌드 reverse index)
--- @param fullType string
--- @return string|nil categoryName
--- @return string|nil subcategoryName
function IrisBrowserData.getItemLocation(fullType)
    if not IrisBrowserData._built or not fullType then
        return nil, nil
    end

    return IrisBrowserQuery.getItemLocation(
        IrisBrowserData._cache,
        fullType,
        IrisBrowserData.CATEGORY_ORDER,
        IrisBrowserData.SUBCATEGORY_MAP
    )
end

--- 그룹의 변형 아이템 목록 반환
--- @param groupId string|nil 그룹 ID
--- @return table variants { fullType, displayName }[] or nil
function IrisBrowserData.getGroupVariants(groupId)
    if not IrisBrowserData._built then
        return nil
    end
    return IrisBrowserQuery.getGroupVariants(IrisBrowserData._cache, groupId)
end

return IrisBrowserData
