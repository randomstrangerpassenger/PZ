--[[
    IrisBrowserClassificationIndex.lua

    Classification index for BrowserData. This module only knows how to map
    precomputed Iris tags into Browser category/subcategory buckets.
]]

local IrisBrowserClassificationIndex = {}

local function parseTag(tag)
    if not tag or type(tag) ~= "string" then
        return nil, nil
    end

    local category, subcategory = tag:match("^([^%.]+)%.(.+)$")
    return category, subcategory
end

function IrisBrowserClassificationIndex.createEmpty(categoryOrder, subcategoryMap)
    local index = {
        categories = {},
        itemLocationsByFullType = {},
    }

    for _, catName in ipairs(categoryOrder or {}) do
        index.categories[catName] = {
            name = catName,
            subcategories = {},
        }

        local subcategories = (subcategoryMap and subcategoryMap[catName]) or {}
        for _, subName in ipairs(subcategories) do
            index.categories[catName].subcategories[subName] = {
                name = subName,
                items = {},
                count = 0,
            }
        end
    end

    return index
end

function IrisBrowserClassificationIndex.addItem(index, fullType, tags)
    if not index or not fullType or type(tags) ~= "table" then
        return false
    end

    local hasAnyTag = false
    for tag, _ in pairs(tags) do
        hasAnyTag = true

        local category, subcategory = parseTag(tag)
        if category and subcategory then
            local catData = index.categories[category]
            if catData and catData.subcategories and catData.subcategories[subcategory] then
                local subData = catData.subcategories[subcategory]
                if not subData.items[fullType] then
                    subData.items[fullType] = true
                    subData.count = subData.count + 1

                    local locations = index.itemLocationsByFullType[fullType]
                    if not locations then
                        locations = {}
                        index.itemLocationsByFullType[fullType] = locations
                    end
                    table.insert(locations, {
                        category = category,
                        subcategory = subcategory,
                    })
                end
            end
        end
    end

    return hasAnyTag
end

function IrisBrowserClassificationIndex.chooseLocation(index, fullType, categoryOrder, subcategoryMap)
    if not index or not fullType then
        return nil, nil
    end

    local locations = index.itemLocationsByFullType and index.itemLocationsByFullType[fullType]
    if not locations or #locations == 0 then
        return nil, nil
    end

    for _, catName in ipairs(categoryOrder or {}) do
        local subcategories = (subcategoryMap and subcategoryMap[catName]) or {}
        for _, subName in ipairs(subcategories) do
            for _, location in ipairs(locations) do
                if location.category == catName and location.subcategory == subName then
                    return location.category, location.subcategory
                end
            end
        end
    end

    return locations[1].category, locations[1].subcategory
end

return IrisBrowserClassificationIndex
