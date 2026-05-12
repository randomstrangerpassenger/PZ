--[[
    IrisBrowserFilters.lua

    Read-only category/subcategory projections for BrowserData.
]]

local IrisBrowserFilters = {}

function IrisBrowserFilters.getCategories(cache, categoryOrder, getCategoryLabel, debug)
    local result = {}

    if not cache or not cache.categories then
        return result
    end

    for _, catName in ipairs(categoryOrder or {}) do
        local catData = cache.categories[catName]
        if catData then
            local subCount = 0
            local totalItems = 0
            for _, subData in pairs(catData.subcategories or {}) do
                subCount = subCount + 1
                totalItems = totalItems + (subData.count or 0)
            end
            if debug then
                debug("[IrisBrowserData] Category '" .. catName .. "': " .. subCount .. " subcategories, " .. totalItems .. " items")
            end
            table.insert(result, {
                name = catName,
                label = getCategoryLabel(catName),
                subcategoryCount = subCount,
            })
        elseif debug then
            debug("[IrisBrowserData] Category '" .. catName .. "' NOT FOUND in cache")
        end
    end

    return result
end

function IrisBrowserFilters.getSubcategories(cache, categoryName, getSubcategoryLabel, calculateFoldedCount, debug)
    local result = {}

    if not cache or not cache.categories then
        return result
    end

    local catData = cache.categories[categoryName]
    if not catData then
        if debug then
            debug("[IrisBrowserData] Category '" .. tostring(categoryName) .. "' NOT FOUND in cache")
            debug("[IrisBrowserData] Available categories:")
            for k, _ in pairs(cache.categories) do
                debug("[IrisBrowserData]   - '" .. tostring(k) .. "'")
            end
        end
        return result
    end

    if debug then
        debug("[IrisBrowserData] Found category, subcategories table exists = " .. tostring(catData.subcategories ~= nil))
    end

    for subCode, subData in pairs(catData.subcategories or {}) do
        local label = getSubcategoryLabel(subCode)
        local foldedCount = calculateFoldedCount(categoryName, subCode, subData)

        if debug then
            debug("[IrisBrowserData]   Subcategory '" .. subCode .. "': raw=" .. tostring(subData.count) .. ", folded=" .. tostring(foldedCount))
        end

        table.insert(result, {
            name = subCode,
            label = label,
            itemCount = foldedCount,
            rawCount = subData.count,
        })
    end

    table.sort(result, function(a, b)
        return a.name < b.name
    end)

    return result
end

return IrisBrowserFilters
