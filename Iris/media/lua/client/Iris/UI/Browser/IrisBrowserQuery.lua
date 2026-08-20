--[[
    IrisBrowserQuery.lua

    Item lookup and search helpers for BrowserData.
]]

local IrisBrowserQuery = {}

local ItemAccess = require("Iris/Util/IrisItemAccess")
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

local function searchRowLess(a, b)
    if a.displayName ~= b.displayName then
        return a.displayName < b.displayName
    end
    return a.fullType < b.fullType
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
                folded = displayName:lower() .. "\0" .. fullType:lower(),
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
                folded = legacyKeys and legacyKeys.folded or
                    (displayName:lower() .. "\0" .. fullType:lower()),
                category = primary and primary.category or nil,
                subcategory = primary and primary.subcategory or nil,
            }
        end
    end
    table.sort(refreshedRows, searchRowLess)
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
    local refreshed = refreshSearchSnapshot(cache, normalizedLocale)
    -- Publish only after the replacement row map and globally sorted source
    -- are complete. No engine callback occurs inside this publish sequence.
    if refreshed.rowsByFullType then
        cache.rowsByFullType = refreshed.rowsByFullType
        cache.displayNameGroupsByGrouping = {}
        cache.foldedCountsByGrouping = {}
    end
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
    if not query or query == "" then
        cache.searchPrefixState = nil
        return {}
    end

    local normalizedLocale = locale or "EN"
    local snapshot = IrisBrowserQuery.ensureLocale(cache, normalizedLocale)

    local queryLower = query:lower()
    local result = {}
    local metrics = nil
    if instrumentationEnabled then
        metrics = cache.searchMetrics or newSearchMetrics()
        cache.searchMetrics = metrics
        metrics.searchCalls = (metrics.searchCalls or 0) + 1
    end

    local previous = cache.searchPrefixState
    local reusePrevious = previous and previous.generation == cache.generation and
        previous.locale == normalizedLocale and #queryLower > #previous.query and
        queryLower:sub(1, #previous.query) == previous.query
    local sourceRows = reusePrevious and previous.results or nil
    local scannedRows = 0

    if sourceRows then
        if metrics then
            metrics.prefixReuseCount = (metrics.prefixReuseCount or 0) + 1
        end
        for _, row in ipairs(sourceRows) do
            scannedRows = scannedRows + 1
            if row.folded:find(queryLower, 1, true) then
                table.insert(result, row)
            end
        end
    else
        for _, row in ipairs(snapshot.rows) do
            scannedRows = scannedRows + 1
            if row.folded:find(queryLower, 1, true) then
                local primary = row.primaryLocation
                local foundCat = primary and primary.category or row.category
                local foundSub = primary and primary.subcategory or row.subcategory
                local usedCompatibilityLocation = false
                if foundCat == nil and foundSub == nil and
                    not cache.rowsByFullType and getItemLocation then
                    -- Compatibility for callers constructing a pre-generation
                    -- cache fixture. Production caches always use the map.
                    foundCat, foundSub = getItemLocation(row.fullType)
                    usedCompatibilityLocation = true
                    if metrics then
                        metrics.locationLookupCount =
                            (metrics.locationLookupCount or 0) + 1
                    end
                end
                if usedCompatibilityLocation then
                    -- Compatibility fixtures may supply locations only via
                    -- the callback; keep that derived row private.
                    table.insert(result, {
                        fullType = row.fullType,
                        displayName = row.displayName,
                        folded = row.folded,
                        category = foundCat,
                        subcategory = foundSub,
                    })
                else
                    table.insert(result, row)
                end
            end
        end
    end

    if metrics then
        metrics.lastScanRows = scannedRows
        metrics.totalScanRows = (metrics.totalScanRows or 0) + scannedRows
    end
    cache.searchPrefixState = {
        generation = cache.generation,
        locale = normalizedLocale,
        query = queryLower,
        results = result,
    }
    return copyRows(result, metrics, "publicRowCopyCount")
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
