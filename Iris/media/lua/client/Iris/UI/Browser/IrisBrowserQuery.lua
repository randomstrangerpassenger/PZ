--[[
    IrisBrowserQuery.lua

    Item lookup and search helpers for BrowserData.
]]

local IrisBrowserQuery = {}

local ItemAccess = require("Iris/Util/IrisItemAccess")
local IrisBrowserClassificationIndex = require("Iris/UI/Browser/IrisBrowserClassificationIndex")

function IrisBrowserQuery.searchAll(cache, query, getItemLocation)
    if not cache or not cache.itemsByFullType or not query or query == "" then
        return {}
    end

    local queryLower = query:lower()
    local result = {}

    for fullType, item in pairs(cache.itemsByFullType) do
        local displayName = ItemAccess.getDisplayName(item, fullType)

        if displayName:lower():find(queryLower, 1, true) or
           fullType:lower():find(queryLower, 1, true) then
            local foundCat, foundSub = getItemLocation(fullType)

            table.insert(result, {
                fullType = fullType,
                displayName = displayName,
                category = foundCat,
                subcategory = foundSub,
            })
        end
    end

    table.sort(result, function(a, b)
        return a.displayName < b.displayName
    end)

    return result
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

function IrisBrowserQuery.getGroupVariants(cache, groupId)
    if not groupId then return nil end
    if not cache or not cache.itemsByFullType then return nil end
    if not IrisData or not IrisData.ItemGroups then return nil end

    local groupItems = IrisData.ItemGroups[groupId]
    if not groupItems then return nil end

    local result = {}
    for _, fullType in ipairs(groupItems) do
        local item = cache.itemsByFullType[fullType]
        table.insert(result, {
            fullType = fullType,
            displayName = ItemAccess.getDisplayName(item, fullType),
        })
    end

    table.sort(result, function(a, b)
        return a.displayName < b.displayName
    end)

    return result
end

return IrisBrowserQuery
