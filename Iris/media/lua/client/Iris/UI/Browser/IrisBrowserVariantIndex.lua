--[[
    IrisBrowserVariantIndex.lua

    DisplayName-based list folding and primary subcategory selection for
    BrowserData item lists.
]]

local IrisBrowserVariantIndex = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local ItemAccess = require("Iris/Util/IrisItemAccess")
local CategoryIndex = require("Iris/UI/Browser/IrisBrowserCategoryIndex")

local function hasRecipeConnections(item, IrisAPI)
    if IrisAPI and IrisAPI.Index and IrisAPI.Index.getRecipeConnectionsForItem then
        local ok, list = ProtectedCall.data(function() return IrisAPI.Index.getRecipeConnectionsForItem(item) end)
        if ok and list and #list > 0 then
            return true
        end
    end
    return false
end

local function groupsCanFold(group)
    if #group <= 1 then
        return true
    end

    local firstType = group[1].itemType
    local firstHasRecipe = group[1].hasRecipe
    for i = 2, #group do
        if group[i].itemType ~= firstType then
            return false
        end
        if group[i].hasRecipe ~= firstHasRecipe then
            return false
        end
    end

    return true
end

local function groupingKey(subData)
    local fullTypes = {}
    for fullType, _ in pairs((subData and subData.items) or {}) do
        if type(fullType) ~= "string" or fullType == "" then
            error("Iris Browser grouping requires a non-empty fullType key")
        end
        fullTypes[#fullTypes + 1] = fullType
    end
    table.sort(fullTypes)
    return table.concat(fullTypes, "\0")
end

local function buildDisplayNameGroups(cache, subData, IrisAPI)
    local itemsByDisplayName = {}

    for fullType, _ in pairs((subData and subData.items) or {}) do
        local item = cache.itemsByFullType[fullType]
        local displayName = ItemAccess.getDisplayName(item, fullType)

        if not itemsByDisplayName[displayName] then
            itemsByDisplayName[displayName] = {}
        end

        table.insert(itemsByDisplayName[displayName], {
            fullType = fullType,
            item = item,
            itemType = ItemAccess.getType(item, "Normal"),
            hasRecipe = hasRecipeConnections(item, IrisAPI),
        })
    end

    for _, group in pairs(itemsByDisplayName) do
        table.sort(group, function(a, b)
            return a.fullType < b.fullType
        end)
    end

    return itemsByDisplayName
end

local function getDisplayNameGroups(cache, subData, IrisAPI)
    cache.displayNameGroupsByGrouping = cache.displayNameGroupsByGrouping or {}
    local key = groupingKey(subData)
    local cached = cache.displayNameGroupsByGrouping[key]
    if cached then
        return cached
    end
    local groups = buildDisplayNameGroups(cache, subData, IrisAPI)
    cache.displayNameGroupsByGrouping[key] = groups
    return groups
end

--- Canonical identity for a subcategory's grouping inputs. The owning cache is
--- generation-scoped, so identical keys are never reused across rebuilds.
function IrisBrowserVariantIndex.getFoldedCountCacheKey(subData)
    return groupingKey(subData)
end

function IrisBrowserVariantIndex.calculateFoldedCount(cache, subData, IrisAPI)
    if not cache or not cache.itemsByFullType or not subData then
        return 0
    end

    local foldedCount = 0
    local itemsByDisplayName = getDisplayNameGroups(cache, subData, IrisAPI)

    for _, group in pairs(itemsByDisplayName) do
        if #group == 1 or groupsCanFold(group) then
            foldedCount = foldedCount + 1
        else
            foldedCount = foldedCount + #group
        end
    end

    return foldedCount
end

function IrisBrowserVariantIndex.calculatePrimary(item, fullType, currentTag, IrisAPI)
    local primaryTag = nil

    if IrisPrimarySubcategory and IrisPrimarySubcategory[fullType] then
        primaryTag = IrisPrimarySubcategory[fullType]
    elseif IrisAPI and IrisAPI.Tags and IrisAPI.Tags.getTagsForItem then
        local ok, tags = ProtectedCall.data(function() return IrisAPI.Tags.getTagsForItem(item) end)
        if ok and tags then
            local lowestPriority = 999
            local lowestCode = "ZZZ"

            for tag, _ in pairs(tags) do
                local cat, code = tag:match("^([^%.]+)%.(.+)$")
                if cat and code then
                    local priority = CategoryIndex.getDescriptionPriority(cat)
                    if priority < lowestPriority or
                       (priority == lowestPriority and code < lowestCode) then
                        lowestPriority = priority
                        lowestCode = code
                        primaryTag = tag
                    end
                end
            end
        end
    end

    return primaryTag == currentTag
end

function IrisBrowserVariantIndex.getItems(cache, categoryName, subcategoryName, IrisAPI, debug)
    local result = {}

    if not cache or not cache.categories or not cache.itemsByFullType or not categoryName or not subcategoryName then
        return result
    end

    local catData = cache.categories[categoryName]
    if not catData then
        if debug then
            debug("[IrisBrowserData] getItems - category '" .. categoryName .. "' not found")
        end
        return result
    end

    if not catData.subcategories[subcategoryName] then
        if debug then
            debug("[IrisBrowserData] getItems - subcategory '" .. subcategoryName .. "' not found in category")
            debug("[IrisBrowserData] Available subcategories:")
            for k, _ in pairs(catData.subcategories or {}) do
                debug("[IrisBrowserData]   - '" .. k .. "'")
            end
        end
        return result
    end

    local subData = catData.subcategories[subcategoryName]
    if debug then
        debug("[IrisBrowserData] Found subcategory, items count in set = " .. tostring(subData.count))
    end

    local currentTag = categoryName .. "." .. subcategoryName
    local itemsByDisplayName = getDisplayNameGroups(cache, subData, IrisAPI)

    for displayName, group in pairs(itemsByDisplayName) do
        if #group == 1 then
            local entry = group[1]
            table.insert(result, {
                fullType = entry.fullType,
                displayName = displayName,
                isPrimary = IrisBrowserVariantIndex.calculatePrimary(entry.item, entry.fullType, currentTag, IrisAPI),
                variants = nil,
            })
        elseif groupsCanFold(group) then
            local representative = group[1]
            local variants = {}
            for _, entry in ipairs(group) do
                table.insert(variants, entry.fullType)
            end
            table.sort(variants)

            table.insert(result, {
                fullType = representative.fullType,
                displayName = displayName,
                isPrimary = IrisBrowserVariantIndex.calculatePrimary(representative.item, representative.fullType, currentTag, IrisAPI),
                variants = variants,
            })
        else
            for _, entry in ipairs(group) do
                table.insert(result, {
                    fullType = entry.fullType,
                    displayName = displayName,
                    isPrimary = IrisBrowserVariantIndex.calculatePrimary(entry.item, entry.fullType, currentTag, IrisAPI),
                    variants = nil,
                })
            end
        end
    end

    table.sort(result, function(a, b)
        if a.isPrimary ~= b.isPrimary then
            return a.isPrimary
        end
        if a.displayName ~= b.displayName then
            return a.displayName < b.displayName
        end
        return a.fullType < b.fullType
    end)

    return result
end

--- Public compatibility adapter for historical IrisData.ItemGroups callers.
--- The global/module boundary is resolved by StaticData, not query code.
function IrisBrowserVariantIndex.getGroupVariants(cache, groupId, legacyData)
    if not groupId or not cache or not cache.itemsByFullType then return nil end
    local itemGroups = legacyData and legacyData.ItemGroups
    local groupItems = itemGroups and itemGroups[groupId]
    if not groupItems then return nil end

    local result = {}
    for _, fullType in ipairs(groupItems) do
        local item = cache.itemsByFullType[fullType]
        result[#result + 1] = {
            fullType = fullType,
            displayName = ItemAccess.getDisplayName(item, fullType),
        }
    end
    table.sort(result, function(a, b)
        if a.displayName ~= b.displayName then return a.displayName < b.displayName end
        return a.fullType < b.fullType
    end)
    return result
end

return IrisBrowserVariantIndex
