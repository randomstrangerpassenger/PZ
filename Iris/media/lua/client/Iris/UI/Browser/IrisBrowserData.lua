--[[
    IrisBrowserData.lua - Iris 브라우저 데이터 캐시
    
    Rule Engine 결과(Item → Set<Tag>)를 역인덱싱한 표현 전용 캐시
    
    규칙:
    - Browser 최초 사용 시 generation당 1회 생성
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
local ItemAccess = require("Iris/Util/IrisItemAccess")
local StaticData = require("Iris/API/StaticData")
local IrisLogger = require("Iris/Util/IrisLogger")
local debug = bootstrap.debug
local warn = bootstrap.warn

-- 의존성 (lazy load)
local IrisAPI = nil
local tr = TranslationResolver.get

-- 캐시 데이터
IrisBrowserData._cache = nil
local buildState = "uninitialized"
local buildReason = "not_built"
local buildDependency = nil
local buildGeneration = 0
local instrumentation = {
    buildAttempts = 0,
    getAllItemsCallCount = 0,
    scannedItemCount = 0,
    lastBuildElapsedMilliseconds = 0,
    lastScanElapsedMilliseconds = 0,
    coldOpenCount = 0,
    warmReopenCount = 0,
    lastColdOpenElapsedMilliseconds = 0,
    lastWarmReopenElapsedMilliseconds = 0,
    generationInvalidationCount = 0,
}

local function nowMilliseconds()
    if getTimestampMs then
        local ok, value = ProtectedCall.engine(getTimestampMs)
        if ok and type(value) == "number" then return value end
    end
    if os and os.clock then return os.clock() * 1000 end
    return 0
end

local function finishBuildTiming(startedAt)
    instrumentation.lastBuildElapsedMilliseconds = math.max(0, nowMilliseconds() - startedAt)
end

local READY_STATES = {
    ready = true,
    degraded_ready = true,
}

local function setBuildState(state, reason, dependency)
    buildState = state
    buildReason = reason
    buildDependency = dependency
    IrisBrowserData._built = READY_STATES[state] == true
end

setBuildState("uninitialized", "not_built", nil)

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

local function stateSnapshot()
    local expectedBuilt = READY_STATES[buildState] == true
    if IrisBrowserData._built ~= expectedBuilt then
        error("[IrisBrowserData] compatibility state mismatch: state=" ..
            tostring(buildState) .. " _built=" .. tostring(IrisBrowserData._built))
    end
    return {
        state = buildState,
        reason = buildReason,
        dependency = buildDependency,
        generation = buildGeneration,
    }
end

--- 현재 build-state와 실패/저하 이유를 반환한다.
--- @return table stateInfo
function IrisBrowserData.getBuildState()
    return stateSnapshot()
end

--- query가 cache를 소비할 수 있는 상태인지 반환한다.
--- @return boolean ready
function IrisBrowserData.isReady()
    stateSnapshot()
    return READY_STATES[buildState] == true
end

local function createSearchKeys(itemIndex)
    local keys = {}
    for fullType, item in pairs(itemIndex.itemsByFullType or {}) do
        local displayName = ItemAccess.getDisplayName(item, fullType)
        keys[fullType] = {
            displayName = displayName,
            folded = displayName:lower() .. "\0" .. fullType:lower(),
        }
    end
    return keys
end

local function buildCandidateCache(itemIndex)
    local classificationIndex = IrisBrowserClassificationIndex.createEmpty(
        IrisBrowserData.CATEGORY_ORDER,
        IrisBrowserData.SUBCATEGORY_MAP
    )

    local candidate = {
        itemIndex = itemIndex,
        classificationIndex = classificationIndex,
        itemsByFullType = itemIndex.itemsByFullType,
        categories = classificationIndex.categories,
        itemLocationsByFullType = classificationIndex.itemLocationsByFullType,
        searchKeysByFullType = createSearchKeys(itemIndex),
        searchKeysLocale = TranslationResolver.getLangKey("EN"),
        foldedCountsByGrouping = {},
        displayNameGroupsByGrouping = {},
        searchMetrics = {
            searchCalls = 0,
            totalScanRows = 0,
            lastScanRows = 0,
            prefixReuseCount = 0,
        },
        generation = buildGeneration + 1,
    }

    local taggedCount = 0
    local errorCount = 0
    local maxErrors = 5

    for fullType, item in pairs(itemIndex.itemsByFullType or {}) do
        local tags = {}
        local tagOk, tagResult = ProtectedCall.data(function()
            return IrisAPI.Tags.getTagsForItem(item)
        end)
        if not tagOk then
            if IrisLogger.isDebugEnabled() and errorCount < maxErrors then
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
    
    return candidate, taggedCount, errorCount
end

local function recordItemIndexInstrumentation(itemIndex)
    if not itemIndex then return end
    instrumentation.getAllItemsCallCount = instrumentation.getAllItemsCallCount +
        (itemIndex.getAllItemsCallCount or 0)
    instrumentation.scannedItemCount = instrumentation.scannedItemCount +
        (itemIndex.scannedItemCount or 0)
    instrumentation.lastScanElapsedMilliseconds = itemIndex.elapsedMilliseconds or 0
end

--- 브라우저 cache를 필요한 경우 build/retry한다.
--- @return boolean ready
--- @return table stateInfo
function IrisBrowserData.ensureReady()
    local callStartedAt = nowMilliseconds()
    if READY_STATES[buildState] then
        instrumentation.warmReopenCount = instrumentation.warmReopenCount + 1
        instrumentation.lastWarmReopenElapsedMilliseconds = math.max(0, nowMilliseconds() - callStartedAt)
        return true, stateSnapshot()
    end
    if buildState == "building" then
        return false, stateSnapshot()
    end

    local buildStartedAt = nowMilliseconds()
    setBuildState("building", "build_in_progress", nil)
    instrumentation.buildAttempts = instrumentation.buildAttempts + 1
    if IrisLogger.isDebugEnabled() then
        debug("[IrisBrowserData] Building cache...")
    end
    ensureDeps()

    if not IrisAPI then
        finishBuildTiming(buildStartedAt)
        setBuildState("retryable_failed", "required_dependency_unavailable", "Iris/IrisAPI")
        warn("[IrisBrowserData] required dependency unavailable: Iris/IrisAPI")
        return false, stateSnapshot()
    end
    if not IrisAPI.Tags or not IrisAPI.Tags.getTagsForItem then
        finishBuildTiming(buildStartedAt)
        setBuildState("retryable_failed", "required_dependency_unavailable", "IrisAPI.Tags")
        warn("[IrisBrowserData] required dependency unavailable: IrisAPI.Tags")
        return false, stateSnapshot()
    end

    local itemIndexOk, itemIndex, itemIndexFailure = pcall(IrisBrowserItemIndex.build)
    if not itemIndexOk then
        finishBuildTiming(buildStartedAt)
        setBuildState("retryable_failed", "item_index_build_failed", "getAllItems")
        warn("[IrisBrowserData] item index build failed: " .. tostring(itemIndex))
        return false, stateSnapshot()
    end
    recordItemIndexInstrumentation(itemIndex)
    if itemIndexFailure then
        finishBuildTiming(buildStartedAt)
        setBuildState("retryable_failed", itemIndexFailure or "item_index_unavailable", "getAllItems")
        warn("[IrisBrowserData] item index unavailable: " .. tostring(itemIndexFailure))
        return false, stateSnapshot()
    end

    local buildOk, candidate, taggedCount, errorCount = pcall(buildCandidateCache, itemIndex)
    if not buildOk then
        finishBuildTiming(buildStartedAt)
        setBuildState("retryable_failed", "cache_build_failed", "IrisBrowserData.cache")
        warn("[IrisBrowserData] cache build failed: " .. tostring(candidate))
        return false, stateSnapshot()
    end
    IrisBrowserData._cache = candidate
    buildGeneration = candidate.generation
    finishBuildTiming(buildStartedAt)
    instrumentation.coldOpenCount = instrumentation.coldOpenCount + 1
    instrumentation.lastColdOpenElapsedMilliseconds = instrumentation.lastBuildElapsedMilliseconds

    if not IrisAPI.Index or not IrisAPI.Index.getRecipeConnectionsForItem then
        setBuildState("degraded_ready", "optional_dependency_unavailable", "IrisAPI.Index")
        warn("[IrisBrowserData] optional dependency unavailable: IrisAPI.Index")
    else
        setBuildState("ready", "build_complete", nil)
    end

    if IrisLogger.isDebugEnabled() then
        debug("[IrisBrowserData] Cache built: " .. tostring(candidate.itemIndex.itemCount) ..
            " items indexed, " .. taggedCount .. " tagged, errors=" .. errorCount ..
            ", state=" .. buildState)
    end
    return true, stateSnapshot()
end

--- Browser-open 재진입과 dev reload를 위한 명시적 reset.
function IrisBrowserData.resetForReload()
    IrisAPI = nil
    IrisBrowserData._cache = nil
    instrumentation.generationInvalidationCount = instrumentation.generationInvalidationCount + 1
    setBuildState("uninitialized", "explicit_reload_reset", nil)
end

--- Dev/test-only build and scan counters. Returned by value.
function IrisBrowserData.getInstrumentation()
    return {
        state = buildState,
        generation = buildGeneration,
        buildAttempts = instrumentation.buildAttempts,
        getAllItemsCallCount = instrumentation.getAllItemsCallCount,
        scannedItemCount = instrumentation.scannedItemCount,
        lastElapsedMilliseconds = instrumentation.lastBuildElapsedMilliseconds,
        lastBuildElapsedMilliseconds = instrumentation.lastBuildElapsedMilliseconds,
        lastScanElapsedMilliseconds = instrumentation.lastScanElapsedMilliseconds,
        coldOpenCount = instrumentation.coldOpenCount,
        warmReopenCount = instrumentation.warmReopenCount,
        lastColdOpenElapsedMilliseconds = instrumentation.lastColdOpenElapsedMilliseconds,
        lastWarmReopenElapsedMilliseconds = instrumentation.lastWarmReopenElapsedMilliseconds,
        generationInvalidationCount = instrumentation.generationInvalidationCount,
    }
end

function IrisBrowserData.resetInstrumentation()
    instrumentation = {
        buildAttempts = 0,
        getAllItemsCallCount = 0,
        scannedItemCount = 0,
        lastBuildElapsedMilliseconds = 0,
        lastScanElapsedMilliseconds = 0,
        coldOpenCount = 0,
        warmReopenCount = 0,
        lastColdOpenElapsedMilliseconds = 0,
        lastWarmReopenElapsedMilliseconds = 0,
        generationInvalidationCount = 0,
    }
end

--- 기존 boolean build API compatibility adapter.
--- @return boolean success
function IrisBrowserData.build()
    local ready = IrisBrowserData.ensureReady()
    return ready
end

--- 대분류 목록 반환 (고정 순서)
--- @return table categories (name, subcategoryCount)
function IrisBrowserData.getCategories()
    local debugEnabled = IrisLogger.isDebugEnabled()
    if debugEnabled then
        debug("[IrisBrowserData] getCategories() called")
        debug("[IrisBrowserData] state = " .. tostring(buildState))
    end
    if not IrisBrowserData.isReady() then
        if debugEnabled then debug("[IrisBrowserData] NOT BUILT, returning empty") end
        return {}
    end
    
    if debugEnabled then
        debug("[IrisBrowserData] _cache exists = " .. tostring(IrisBrowserData._cache ~= nil))
        debug("[IrisBrowserData] CATEGORY_ORDER count = " .. #IrisBrowserData.CATEGORY_ORDER)
    end

    local result = IrisBrowserFilters.getCategories(
        IrisBrowserData._cache,
        IrisBrowserData.CATEGORY_ORDER,
        IrisBrowserData.getCategoryLabel,
        debugEnabled and debug or nil
    )
    if debugEnabled then debug("[IrisBrowserData] getCategories() returning " .. #result .. " categories") end
    return result
end

--- 접기 후 아이템 개수 계산 (내부용)
--- DisplayName 기반 접기 + 차단 가드 적용 후 남는 개수
--- @param categoryName string
--- @param subCode string
--- @param subData table
--- @return number foldedCount
function IrisBrowserData._calculateFoldedCount(categoryName, subCode, subData)
    if not IrisBrowserData._cache then return 0 end
    local groupingKey = IrisBrowserVariantIndex.getFoldedCountCacheKey(subData)
    local cached = IrisBrowserData._cache.foldedCountsByGrouping[groupingKey]
    if cached ~= nil then return cached end
    local count = IrisBrowserVariantIndex.calculateFoldedCount(IrisBrowserData._cache, subData, IrisAPI)
    IrisBrowserData._cache.foldedCountsByGrouping[groupingKey] = count
    return count
end

--- 특정 대분류의 소분류 목록 반환 (코드순 정렬)
--- @param categoryName string
--- @return table subcategories (code, label, itemCount)
function IrisBrowserData.getSubcategories(categoryName)
    local debugEnabled = IrisLogger.isDebugEnabled()
    if debugEnabled then
        debug("[IrisBrowserData] getSubcategories('" .. tostring(categoryName) .. "') called")
    end
    
    if not IrisBrowserData.isReady() then
        if debugEnabled then debug("[IrisBrowserData] NOT BUILT, returning empty") end
        return {}
    end
    if not categoryName then
        if debugEnabled then debug("[IrisBrowserData] categoryName is nil, returning empty") end
        return {}
    end
    
    local result = IrisBrowserFilters.getSubcategories(
        IrisBrowserData._cache,
        categoryName,
        IrisBrowserData.getSubcategoryLabel,
        IrisBrowserData._calculateFoldedCount,
        debugEnabled and debug or nil
    )
    if debugEnabled then debug("[IrisBrowserData] getSubcategories() returning " .. #result .. " subcategories") end
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
    local debugEnabled = IrisLogger.isDebugEnabled()
    if debugEnabled then
        debug("[IrisBrowserData] getItems('" .. tostring(categoryName) .. "', '" .. tostring(subcategoryName) .. "') called")
    end
    
    if not IrisBrowserData.isReady() or not categoryName or not subcategoryName then
        if debugEnabled then debug("[IrisBrowserData] getItems - not built or missing params") end
        return {}
    end
    
    local result = IrisBrowserVariantIndex.getItems(
        IrisBrowserData._cache,
        categoryName,
        subcategoryName,
        IrisAPI,
        debugEnabled and debug or nil
    )
    if debugEnabled then
        debug("[IrisBrowserData] getItems() returning " .. #result .. " items (DisplayName folding)")
    end
    return result
end

--- 전체 검색 (DisplayName/fullType 기준)
--- @param query string
--- @return table items (fullType, displayName, category, subcategory)
function IrisBrowserData.searchAll(query)
    if not IrisBrowserData.isReady() then
        return {}
    end

    return IrisBrowserQuery.searchAll(
        IrisBrowserData._cache,
        query,
        IrisBrowserData.getItemLocation,
        TranslationResolver.getLangKey("EN")
    )
end

--- 아이템 객체 반환
--- @param fullType string
--- @return InventoryItem|nil
function IrisBrowserData.getItem(fullType)
    if not IrisBrowserData.isReady() or not fullType then
        return nil
    end
    return IrisBrowserQuery.getItem(IrisBrowserData._cache, fullType)
end

--- 아이템의 브라우저 위치 반환 (selectItem용 사전 빌드 reverse index)
--- @param fullType string
--- @return string|nil categoryName
--- @return string|nil subcategoryName
function IrisBrowserData.getItemLocation(fullType)
    if not IrisBrowserData.isReady() or not fullType then
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
    if not IrisBrowserData.isReady() then
        return nil
    end
    return IrisBrowserVariantIndex.getGroupVariants(
        IrisBrowserData._cache,
        groupId,
        StaticData.getLegacyIrisData()
    )
end

return IrisBrowserData
