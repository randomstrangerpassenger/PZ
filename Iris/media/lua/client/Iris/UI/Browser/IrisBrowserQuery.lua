--[[
    IrisBrowserQuery.lua

    Item lookup and search helpers for BrowserData.
]]

local IrisBrowserQuery = {}

local ItemAccess = require("Iris/Util/IrisItemAccess")
local Search = require("Iris/UI/Browser/IrisBrowserSearch")
local IrisBrowserClassificationIndex = require("Iris/UI/Browser/IrisBrowserClassificationIndex")
local instrumentationEnabled = false

local function newSearchMetrics()
    return {
        searchCalls = 0,
        totalScanRows = 0,
        lastScanRows = 0,
        prefixReuseCount = 0,
        locationLookupCount = 0,
        internalRowCopyCount = 0,
        publicRowCopyCount = 0,
        localeInvalidationCount = 0,
        generationInvalidationCount = 0,
        fullSortCount = 0,
    }
end

function IrisBrowserQuery.setInstrumentationEnabled(enabled)
    instrumentationEnabled = enabled == true
end

local function copyRows(rows, metrics, metricName)
    local copied = {}
    for index, row in ipairs(rows or {}) do
        local primary = row.primaryLocation
        copied[index] = {
            fullType = row.fullType,
            displayName = row.displayName,
            category = primary and primary.category or row.category,
            subcategory = primary and primary.subcategory or row.subcategory,
        }
    end
    if metrics and metricName then
        metrics[metricName] = (metrics[metricName] or 0) + #copied
    end
    return copied
end

local function refreshSearchSnapshot(cache, normalizedLocale)
    local refreshedRows = {}
    local refreshedByFullType = nil
    if cache.rowsByFullType then
        refreshedByFullType = {}
        for fullType, row in pairs(cache.rowsByFullType) do
            local displayName = ItemAccess.getDisplayName(row.item, fullType)
            local refreshedRow = {
                fullType = fullType,
                item = row.item,
                displayName = displayName,
                searchDocument = Search.document(fullType, displayName),
                primaryLocation = row.primaryLocation,
                primaryTag = row.primaryTag,
            }
            refreshedByFullType[fullType] = refreshedRow
            refreshedRows[#refreshedRows + 1] = refreshedRow
        end
    else
        -- Compatibility for isolated callers that still construct the older
        -- cache shape. Production Browser caches always use rowsByFullType.
        for fullType, item in pairs(cache.itemsByFullType or {}) do
            local legacyKeys = cache.searchSnapshot == nil and
                cache.searchKeysLocale == normalizedLocale and
                cache.searchKeysByFullType and
                cache.searchKeysByFullType[fullType] or nil
            local displayName = legacyKeys and legacyKeys.displayName or
                ItemAccess.getDisplayName(item, fullType)
            local primary = cache.primaryLocationByFullType and
                cache.primaryLocationByFullType[fullType] or nil
            refreshedRows[#refreshedRows + 1] = {
                fullType = fullType,
                displayName = displayName,
                searchDocument = Search.document(fullType, displayName),
                category = primary and primary.category or nil,
                subcategory = primary and primary.subcategory or nil,
            }
        end
    end
    table.sort(refreshedRows, Search.rowLess)
    return {
        rowsByFullType = refreshedByFullType,
        snapshot = {
            generation = cache.generation,
            locale = normalizedLocale,
            rows = refreshedRows,
        },
    }
end

function IrisBrowserQuery.ensureLocale(cache, locale)
    if not cache then return nil end
    local normalizedLocale = locale or "EN"
    local snapshot = cache.searchSnapshot
    if snapshot and snapshot.generation == cache.generation and
        snapshot.locale == normalizedLocale then
        return snapshot
    end

    local previousGeneration = snapshot and snapshot.generation or nil
    local previousLocale = snapshot and snapshot.locale or nil
    if cache.searchRefreshInProgress then
        error("Browser search snapshot refresh reentered")
    end
    local generation = cache.generation
    cache.searchRefreshInProgress = true
    local ok, refreshed = pcall(refreshSearchSnapshot, cache, normalizedLocale)
    cache.searchRefreshInProgress = nil
    if not ok then error(refreshed) end
    if cache.generation ~= generation or cache.searchSnapshot ~= snapshot then
        error("Browser search owner changed during snapshot refresh")
    end
    -- Publish only after the replacement row map and globally sorted source
    -- are complete. No engine callback occurs inside this publish sequence.
    if refreshed.rowsByFullType then
        cache.rowsByFullType = refreshed.rowsByFullType
    end
    cache.displayNameGroupsByGrouping = {}
    cache.foldedCountsByGrouping = {}
    cache.searchSnapshot = refreshed.snapshot
    cache.searchPrefixState = nil
    if instrumentationEnabled then
        cache.searchMetrics = cache.searchMetrics or newSearchMetrics()
        if previousLocale ~= nil and previousLocale ~= normalizedLocale then
            cache.searchMetrics.localeInvalidationCount =
                (cache.searchMetrics.localeInvalidationCount or 0) + 1
        end
        if previousGeneration ~= nil and previousGeneration ~= cache.generation then
            cache.searchMetrics.generationInvalidationCount =
                (cache.searchMetrics.generationInvalidationCount or 0) + 1
        end
        cache.searchMetrics.fullSortCount =
            (cache.searchMetrics.fullSortCount or 0) + 1
    end
    return cache.searchSnapshot
end

function IrisBrowserQuery.searchAll(cache, query, getItemLocation, locale)
    if not cache or not cache.itemsByFullType then
        return {}
    end
    local queryView = Search.query(query)
    if queryView.empty then
        cache.searchPrefixState = nil
        return {}
    end

    local normalizedLocale = locale or "EN"
    local snapshot = IrisBrowserQuery.ensureLocale(cache, normalizedLocale)

    local metrics = nil
    if instrumentationEnabled then
        metrics = cache.searchMetrics or newSearchMetrics()
        cache.searchMetrics = metrics
        metrics.searchCalls = (metrics.searchCalls or 0) + 1
    end

    local previous = cache.searchPrefixState
    local reusePrevious = previous and previous.snapshot == snapshot and
        Search.canNarrow(previous.query, queryView)
    local sourceRows = reusePrevious and previous.candidates or snapshot.rows
    if reusePrevious and metrics then
        metrics.prefixReuseCount = (metrics.prefixReuseCount or 0) + 1
    end
    local result, candidates = Search.rank(sourceRows, queryView, true)

    if metrics then
        metrics.lastScanRows = #sourceRows
        metrics.totalScanRows = (metrics.totalScanRows or 0) + #sourceRows
    end
    cache.searchPrefixState = {
        snapshot = snapshot,
        query = queryView,
        candidates = candidates,
    }
    local public = copyRows(result, metrics, "publicRowCopyCount")
    if not cache.rowsByFullType and getItemLocation then
        -- Legacy fixture adapter shares the matcher and never mutates rows.
        for _, row in ipairs(public) do
            if row.category == nil and row.subcategory == nil then
                row.category, row.subcategory = getItemLocation(row.fullType)
                if metrics then
                    metrics.locationLookupCount = (metrics.locationLookupCount or 0) + 1
                end
            end
        end
    end
    return public
end

-- Navigation consumes the just-completed global query's private candidates.
-- It neither repeats the search nor changes its public ranking/result shape.
function IrisBrowserQuery.getSearchLocation(cache, query, locale)
    local state = cache and cache.searchPrefixState
    local snapshot = cache and cache.searchSnapshot
    if not state or state.snapshot ~= snapshot or state.query.raw ~= query or
        snapshot.generation ~= cache.generation or snapshot.locale ~= locale then
        return nil, nil
    end
    local bestTier, category, subcategory, ambiguous = 3, nil, nil, false
    for _, row in ipairs(state.candidates) do
        local document = row.searchDocument
        -- Explicit full IDs identify navigation targets even when another
        -- item's display name equals that ID. Search ranking stays name-first.
        local tier = document.id == state.query.id and 0 or
            Search.relation(document, state.query, false)
        if tier and tier < 3 and tier <= bestTier then
            local location = row.primaryLocation or row
            if tier < bestTier then
                bestTier = tier
                category, subcategory = location.category, location.subcategory
                ambiguous = false
            end
            if not location.category or not location.subcategory or
                location.category ~= category or location.subcategory ~= subcategory then
                ambiguous = true
            end
        end
    end
    if ambiguous then return nil, nil end
    return category, subcategory
end

-- items are fresh VariantIndex projections, already isolated from the cache.
-- Only visible representatives match; their existing variants stay intact.
function IrisBrowserQuery.searchItems(cache, items, query, locale)
    local queryView = Search.query(query)
    if queryView.empty then return items end
    local snapshot = IrisBrowserQuery.ensureLocale(cache, locale)
    if not snapshot then return {} end
    local visible = {}
    for _, item in ipairs(items) do visible[item.fullType] = item end
    local source = {}
    for _, row in ipairs(snapshot.rows) do
        if visible[row.fullType] then source[#source + 1] = row end
    end
    local ranked = Search.rank(source, queryView, false)
    local projected = {}
    for _, row in ipairs(ranked) do projected[#projected + 1] = visible[row.fullType] end
    return projected
end

function IrisBrowserQuery.getItem(cache, fullType)
    if not cache or not cache.itemsByFullType or not fullType then
        return nil
    end
    local row = cache.rowsByFullType and cache.rowsByFullType[fullType] or nil
    return row and row.item or cache.itemsByFullType[fullType]
end

function IrisBrowserQuery.getItemLocation(cache, fullType, categoryOrder, subcategoryMap)
    if not cache or not fullType then
        return nil, nil
    end

    if cache.rowsByFullType then
        local row = cache.rowsByFullType[fullType]
        local primary = row and row.primaryLocation or nil
        if not primary then return nil, nil end
        return primary.category, primary.subcategory
    end

    if cache.primaryLocationByFullType then
        local primary = cache.primaryLocationByFullType[fullType]
        if not primary then return nil, nil end
        return primary.category, primary.subcategory
    end

    if not cache.classificationIndex then return nil, nil end

    return IrisBrowserClassificationIndex.chooseLocation(
        cache.classificationIndex,
        fullType,
        categoryOrder,
        subcategoryMap
    )
end

return IrisBrowserQuery
