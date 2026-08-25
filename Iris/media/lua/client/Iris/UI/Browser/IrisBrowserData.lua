--[[
    Supported Browser data facade.

    Projection, lifecycle, and metrics are owned by dedicated modules. This
    module preserves the public query/result shapes used by Browser consumers.
]]

local IrisBrowserData = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local debug = bootstrap.debug
local IrisBrowserCategoryIndex = require("Iris/UI/Browser/IrisBrowserCategoryIndex")
local IrisBrowserFilters = require("Iris/UI/Browser/IrisBrowserFilters")
local IrisBrowserItemIndex = require("Iris/UI/Browser/IrisBrowserItemIndex")
local IrisBrowserQuery = require("Iris/UI/Browser/IrisBrowserQuery")
local IrisBrowserVariantIndex = require("Iris/UI/Browser/IrisBrowserVariantIndex")
local IrisBrowserLifecycle = require("Iris/UI/Browser/IrisBrowserLifecycle")
local IrisBrowserMetrics = require("Iris/UI/Browser/IrisBrowserMetrics")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local IrisLogger = require("Iris/Util/IrisLogger")
local tr = TranslationResolver.get

IrisBrowserData.CATEGORY_DEFINITIONS = IrisBrowserCategoryIndex.CATEGORY_DEFINITIONS
IrisBrowserData.CATEGORY_ORDER = IrisBrowserCategoryIndex.CATEGORY_ORDER
IrisBrowserData.CATEGORY_KEYS = IrisBrowserCategoryIndex.CATEGORY_KEYS
IrisBrowserData.SUBCATEGORY_MAP = IrisBrowserCategoryIndex.SUBCATEGORY_MAP
IrisBrowserData.SUBCATEGORY_KEYS = IrisBrowserCategoryIndex.SUBCATEGORY_KEYS

local metrics = IrisBrowserMetrics.create()
local lifecycle = IrisBrowserLifecycle.create({
    metrics = metrics,
    categoryOrder = IrisBrowserData.CATEGORY_ORDER,
    subcategoryMap = IrisBrowserData.SUBCATEGORY_MAP,
})

local function syncCompatibilityState()
    IrisBrowserData._cache = lifecycle.getCache()
    IrisBrowserData._built = lifecycle.isReady()
end

syncCompatibilityState()

function IrisBrowserData.getCategoryLabel(catName)
    return IrisBrowserCategoryIndex.getCategoryLabel(catName, tr)
end

function IrisBrowserData.getSubcategoryLabel(subCode)
    return IrisBrowserCategoryIndex.getSubcategoryLabel(subCode, tr)
end

function IrisBrowserData.getBuildState()
    syncCompatibilityState()
    return lifecycle.getState()
end

function IrisBrowserData.isReady()
    syncCompatibilityState()
    return lifecycle.isReady()
end

function IrisBrowserData.ensureReady()
    local ready, state = lifecycle.ensureReady()
    syncCompatibilityState()
    return ready, state
end

function IrisBrowserData.resetForReload()
    lifecycle.resetForReload()
    syncCompatibilityState()
end

function IrisBrowserData.getInstrumentation()
    local state = lifecycle.getState()
    return metrics.snapshot(state.state, state.generation)
end

function IrisBrowserData.resetInstrumentation()
    metrics.reset()
end

function IrisBrowserData.setInstrumentationEnabled(enabled)
    metrics.setEnabled(enabled)
    IrisBrowserQuery.setInstrumentationEnabled(metrics.isEnabled())
    IrisBrowserItemIndex.setInstrumentationEnabled(metrics.isEnabled())
end

-- Supported boolean compatibility adapter.
function IrisBrowserData.build()
    local ready = IrisBrowserData.ensureReady()
    return ready
end

function IrisBrowserData.getCategories()
    local debugEnabled = IrisLogger.isDebugEnabled()
    if debugEnabled then
        debug("[IrisBrowserData] getCategories() called")
        debug("[IrisBrowserData] state = " .. tostring(lifecycle.getState().state))
    end
    if not IrisBrowserData.isReady() then
        if debugEnabled then debug("[IrisBrowserData] NOT BUILT, returning empty") end
        return {}
    end
    local result = IrisBrowserFilters.getCategories(
        lifecycle.getCache(),
        IrisBrowserData.CATEGORY_ORDER,
        IrisBrowserData.getCategoryLabel,
        debugEnabled and debug or nil
    )
    if debugEnabled then
        debug("[IrisBrowserData] getCategories() returning " .. #result .. " categories")
    end
    return result
end

function IrisBrowserData._calculateFoldedCount(categoryName, subCode, subData)
    local cache = lifecycle.getCache()
    if not cache then return 0 end
    local groupingKey = IrisBrowserVariantIndex.getFoldedCountCacheKey(categoryName, subCode)
    local cached = cache.foldedCountsByGrouping[groupingKey]
    if cached ~= nil then return cached end
    local count = IrisBrowserVariantIndex.calculateFoldedCount(
        cache,
        categoryName,
        subCode,
        subData,
        lifecycle.getApi()
    )
    cache.foldedCountsByGrouping[groupingKey] = count
    return count
end

function IrisBrowserData.getSubcategories(categoryName)
    local debugEnabled = IrisLogger.isDebugEnabled()
    if not IrisBrowserData.isReady() or not categoryName then return {} end
    local cache = lifecycle.getCache()
    IrisBrowserQuery.ensureLocale(cache, TranslationResolver.getLangKey("EN"))
    return IrisBrowserFilters.getSubcategories(
        cache,
        categoryName,
        IrisBrowserData.getSubcategoryLabel,
        IrisBrowserData._calculateFoldedCount,
        debugEnabled and debug or nil
    )
end

function IrisBrowserData._calculatePrimary(item, fullType, currentTag)
    local cache = lifecycle.getCache()
    local row = cache and cache.rowsByFullType and cache.rowsByFullType[fullType] or nil
    return IrisBrowserVariantIndex.calculatePrimary(
        item,
        fullType,
        currentTag,
        lifecycle.getApi(),
        row
    )
end

function IrisBrowserData.getItems(categoryName, subcategoryName)
    if not IrisBrowserData.isReady() or not categoryName or not subcategoryName then
        return {}
    end
    local cache = lifecycle.getCache()
    IrisBrowserQuery.ensureLocale(cache, TranslationResolver.getLangKey("EN"))
    return IrisBrowserVariantIndex.getItems(
        cache,
        categoryName,
        subcategoryName,
        lifecycle.getApi(),
        IrisLogger.isDebugEnabled() and debug or nil
    )
end

function IrisBrowserData.searchAll(query)
    if not IrisBrowserData.isReady() then return {} end
    return IrisBrowserQuery.searchAll(
        lifecycle.getCache(),
        query,
        nil,
        TranslationResolver.getLangKey("EN")
    )
end

function IrisBrowserData.getItem(fullType)
    if not IrisBrowserData.isReady() or not fullType then return nil end
    return IrisBrowserQuery.getItem(lifecycle.getCache(), fullType)
end

function IrisBrowserData.getItemLocation(fullType)
    if not IrisBrowserData.isReady() or not fullType then return nil, nil end
    return IrisBrowserQuery.getItemLocation(lifecycle.getCache(), fullType)
end

-- Supported compatibility facade; W9 replaces the legacy data source.
function IrisBrowserData.getGroupVariants(groupId)
    if not IrisBrowserData.isReady() then return nil end
    return IrisBrowserVariantIndex.getGroupVariants(
        lifecycle.getCache(),
        groupId
    )
end

return IrisBrowserData
