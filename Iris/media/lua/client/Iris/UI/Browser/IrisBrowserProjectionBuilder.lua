-- Projects validated item/classification indexes into immutable-generation Browser rows.
local IrisBrowserProjectionBuilder = {}

local IrisBrowserCategoryIndex = require("Iris/UI/Browser/IrisBrowserCategoryIndex")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local ItemAccess = require("Iris/Util/IrisItemAccess")
local StaticData = require("Iris/API/StaticData")
local IrisLogger = require("Iris/Util/IrisLogger")
local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local debug = bootstrap.debug

local function createPresentationRanks(categoryOrder, subcategoryMap)
    local ranks = {}
    local rank = 0
    for _, categoryName in ipairs(categoryOrder or {}) do
        for _, subcategoryName in ipairs(subcategoryMap[categoryName] or {}) do
            rank = rank + 1
            ranks[categoryName .. "." .. subcategoryName] = rank
        end
    end
    return ranks
end

local function searchRowLess(a, b)
    if a.displayName ~= b.displayName then
        return a.displayName < b.displayName
    end
    return a.fullType < b.fullType
end

local function betterDescriptionTag(tag, currentTag, currentPriority, currentCode)
    local category = nil
    local code = nil
    if type(tag) == "string" then category, code = tag:match("^([^%.]+)%.(.+)$") end
    if not category or not code then
        return currentTag, currentPriority, currentCode
    end
    local priority = IrisBrowserCategoryIndex.getDescriptionPriority(category)
    if priority < currentPriority or
        (priority == currentPriority and code < currentCode) then
        return tag, priority, code
    end
    return currentTag, currentPriority, currentCode
end

function IrisBrowserProjectionBuilder.build(itemIndex, options)
    options = options or {}
    -- Resolve at build time so dev reload/test dependency replacement remains observable.
    local ClassificationIndex = require("Iris/UI/Browser/IrisBrowserClassificationIndex")
    local categoryOrder = options.categoryOrder or {}
    local subcategoryMap = options.subcategoryMap or {}
    local metrics = options.metrics
    local classificationIndex = ClassificationIndex.createEmpty(
        categoryOrder,
        subcategoryMap
    )
    local nextGeneration = (options.currentGeneration or 0) + 1
    local candidate = {
        itemIndex = itemIndex,
        classificationIndex = classificationIndex,
        itemsByFullType = itemIndex.itemsByFullType,
        rowsByFullType = {},
        categories = classificationIndex.categories,
        itemLocationsByFullType = classificationIndex.itemLocationsByFullType,
        searchSnapshot = nil,
        foldedCountsByGrouping = {},
        displayNameGroupsByGrouping = {},
        searchMetrics = metrics.isEnabled() and {
            searchCalls = 0,
            totalScanRows = 0,
            lastScanRows = 0,
            prefixReuseCount = 0,
            fullSortCount = 0,
        } or nil,
        generation = nextGeneration,
    }
    local taggedCount = 0
    local errorCount = 0
    local locationRanks = createPresentationRanks(categoryOrder, subcategoryMap)
    local searchRows = {}
    local classifications = StaticData.get("classifications")
    local classificationsMalformed = classifications ~= nil and
        type(classifications) ~= "table"

    metrics.increment("postIndexMaterializationPassCount")
    for fullType, item in pairs(itemIndex.itemsByFullType or {}) do
        local displayName = ItemAccess.getDisplayName(item, fullType)
        local row = {
            fullType = fullType,
            item = item,
            displayName = displayName,
            folded = displayName:lower() .. "\0" .. fullType:lower(),
            primaryLocation = nil,
            primaryTag = nil,
        }
        candidate.rowsByFullType[fullType] = row
        metrics.increment("materializedRowCount")
        metrics.increment("retainedItemReferenceCount")

        local rawTags = nil
        local tagReadFailed = classificationsMalformed
        if not classificationsMalformed and classifications then
            rawTags = classifications[fullType]
            tagReadFailed = rawTags ~= nil and type(rawTags) ~= "table"
        end
        if tagReadFailed then
            if IrisLogger.isDebugEnabled() and errorCount < 5 then
                debug("[IrisBrowserData] DEBUG: classification tags malformed for " .. fullType)
            end
            errorCount = errorCount + 1
        end

        local hasAnyTag = false
        local primaryLocationRank = math.huge
        local primaryPriority = math.huge
        local primaryCode = "\255"
        if type(rawTags) == "table" then
            for _, tag in ipairs(rawTags) do
                hasAnyTag = true
                local accepted = ClassificationIndex.addTag(
                    classificationIndex,
                    fullType,
                    tag
                )
                local rank = accepted and locationRanks[tag] or nil
                if rank and rank < primaryLocationRank then
                    local category, subcategory = tag:match("^([^%.]+)%.(.+)$")
                    primaryLocationRank = rank
                    row.primaryLocation = {
                        category = category,
                        subcategory = subcategory,
                    }
                end
                row.primaryTag, primaryPriority, primaryCode = betterDescriptionTag(
                    tag,
                    row.primaryTag,
                    primaryPriority,
                    primaryCode
                )
            end
        end
        local explicitPrimary = IrisPrimarySubcategory and IrisPrimarySubcategory[fullType] or nil
        if explicitPrimary ~= nil then
            local category, subcategory = nil, nil
            if type(explicitPrimary) == "string" then
                category, subcategory = explicitPrimary:match("^([^%.]+)%.([^%.]+)$")
            end
            if not category or not subcategory then
                error("malformed IrisPrimarySubcategory for " .. fullType .. ": " .. tostring(explicitPrimary))
            end
            local accepted = false
            for _, location in ipairs(classificationIndex.itemLocationsByFullType[fullType] or {}) do
                if location.category == category and location.subcategory == subcategory then
                    accepted = true
                    break
                end
            end
            if not accepted then
                error("IrisPrimarySubcategory is not an accepted membership for " .. fullType .. ": " .. explicitPrimary)
            end
            row.primaryTag = explicitPrimary
            row.primaryLocation = {
                category = category,
                subcategory = subcategory,
            }
        end
        searchRows[#searchRows + 1] = row
        if hasAnyTag then taggedCount = taggedCount + 1 end
    end

    table.sort(searchRows, searchRowLess)
    candidate.searchSnapshot = {
        generation = nextGeneration,
        locale = TranslationResolver.getLangKey("EN"),
        rows = searchRows,
    }
    if candidate.searchMetrics then
        candidate.searchMetrics.fullSortCount = 1
        metrics.increment("initialSearchSortCount")
    end
    return candidate, taggedCount, errorCount
end

return IrisBrowserProjectionBuilder
