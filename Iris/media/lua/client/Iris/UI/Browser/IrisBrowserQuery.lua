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
        local searchKeys = cache.searchKeysByFullType and cache.searchKeysByFullType[fullType]
        local displayName = searchKeys and searchKeys.displayName or ItemAccess.getDisplayName(item, fullType)
        local displayNameLower = searchKeys and searchKeys.displayNameLower or displayName:lower()
        local fullTypeLower = searchKeys and searchKeys.fullTypeLower or fullType:lower()

        if displayNameLower:find(queryLower, 1, true) or
           fullTypeLower:find(queryLower, 1, true) then
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
        if a.displayName ~= b.displayName then
            return a.displayName < b.displayName
        end
        return a.fullType < b.fullType
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

return IrisBrowserQuery
