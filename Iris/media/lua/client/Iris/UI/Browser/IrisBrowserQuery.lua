--[[
    IrisBrowserQuery.lua

    Item lookup and search helpers for BrowserData.
]]

local IrisBrowserQuery = {}

local ItemAccess = require("Iris/Util/IrisItemAccess")
local IrisBrowserClassificationIndex = require("Iris/UI/Browser/IrisBrowserClassificationIndex")

local function copyRows(rows, metrics, metricName)
    local copied = {}
    for index, row in ipairs(rows or {}) do
        copied[index] = {
            fullType = row.fullType,
            displayName = row.displayName,
            category = row.category,
            subcategory = row.subcategory,
        }
    end
    if metrics and metricName then
        metrics[metricName] = (metrics[metricName] or 0) + #copied
    end
    return copied
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
    if cache.searchKeysLocale ~= normalizedLocale then
        local refreshed = {}
        for fullType, item in pairs(cache.itemsByFullType) do
            local displayName = ItemAccess.getDisplayName(item, fullType)
            refreshed[fullType] = {
                displayName = displayName,
                folded = displayName:lower() .. "\0" .. fullType:lower(),
            }
        end
        cache.searchKeysByFullType = refreshed
        cache.searchKeysLocale = normalizedLocale
        cache.searchPrefixState = nil
        cache.searchMetrics = cache.searchMetrics or {}
        cache.searchMetrics.localeInvalidationCount =
            (cache.searchMetrics.localeInvalidationCount or 0) + 1
    end

    local queryLower = query:lower()
    local result = {}
    local metrics = cache.searchMetrics or {
        searchCalls = 0,
        totalScanRows = 0,
        lastScanRows = 0,
        prefixReuseCount = 0,
        locationLookupCount = 0,
        internalRowCopyCount = 0,
        publicRowCopyCount = 0,
        localeInvalidationCount = 0,
        generationInvalidationCount = 0,
    }
    cache.searchMetrics = metrics
    metrics.searchCalls = metrics.searchCalls + 1

    local previous = cache.searchPrefixState
    if previous and previous.generation ~= cache.generation then
        metrics.generationInvalidationCount = (metrics.generationInvalidationCount or 0) + 1
    end
    local reusePrevious = previous and previous.generation == cache.generation and
        previous.locale == normalizedLocale and #queryLower > #previous.query and
        queryLower:sub(1, #previous.query) == previous.query
    local sourceRows = reusePrevious and previous.results or nil
    local scannedRows = 0

    if sourceRows then
        metrics.prefixReuseCount = metrics.prefixReuseCount + 1
        for _, row in ipairs(sourceRows) do
            scannedRows = scannedRows + 1
            local searchKeys = cache.searchKeysByFullType and cache.searchKeysByFullType[row.fullType]
            local folded = searchKeys and searchKeys.folded or
                (row.displayName:lower() .. "\0" .. row.fullType:lower())
            if folded:find(queryLower, 1, true) then
                table.insert(result, row)
            end
        end
    else
        for fullType, item in pairs(cache.itemsByFullType) do
            scannedRows = scannedRows + 1
            local searchKeys = cache.searchKeysByFullType and cache.searchKeysByFullType[fullType]
            local displayName = searchKeys and searchKeys.displayName or ItemAccess.getDisplayName(item, fullType)
            local folded = searchKeys and searchKeys.folded or
                (displayName:lower() .. "\0" .. fullType:lower())

            if folded:find(queryLower, 1, true) then
                local foundCat, foundSub = getItemLocation(fullType)
                metrics.locationLookupCount = (metrics.locationLookupCount or 0) + 1

                table.insert(result, {
                    fullType = fullType,
                    displayName = displayName,
                    category = foundCat,
                    subcategory = foundSub,
                })
            end
        end
    end

    table.sort(result, function(a, b)
        if a.displayName ~= b.displayName then
            return a.displayName < b.displayName
        end
        return a.fullType < b.fullType
    end)

    metrics.lastScanRows = scannedRows
    metrics.totalScanRows = metrics.totalScanRows + scannedRows
    cache.searchPrefixState = {
        generation = cache.generation,
        locale = normalizedLocale,
        query = queryLower,
        results = copyRows(result, metrics, "internalRowCopyCount"),
    }
    return copyRows(result, metrics, "publicRowCopyCount")
end

function IrisBrowserQuery.getItem(cache, fullType)
    if not cache or not cache.itemsByFullType or not fullType then
        return nil
    end
    return cache.itemsByFullType[fullType]
end

function IrisBrowserQuery.getItemLocation(cache, fullType, categoryOrder, subcategoryMap)
    if not cache or not cache.classificationIndex or not fullType then
        return nil, nil
    end

    return IrisBrowserClassificationIndex.chooseLocation(
        cache.classificationIndex,
        fullType,
        categoryOrder,
        subcategoryMap
    )
end

return IrisBrowserQuery
