local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

if arg[2] == "d2-projection" then
    local supportPath = assert(arg[3], "D2 support input path is required")
    local classifications = require("Iris/Data/IrisClassifications")
    assert(type(classifications) == "table")

    local itemIndex = { itemsByFullType = {} }
    local ordered = {}
    for fullType in io.lines(supportPath) do
        assert(fullType ~= "" and itemIndex.itemsByFullType[fullType] == nil)
        local item = { fullType = fullType }
        function item:getFullType() return self.fullType end
        function item:getFullName() return self.fullType end
        function item:getDisplayName() return self.fullType end
        function item:getType() return "Normal" end
        itemIndex.itemsByFullType[fullType] = item
        ordered[#ordered + 1] = fullType
    end
    table.sort(ordered)

    local CategoryIndex = require("Iris/UI/Browser/IrisBrowserCategoryIndex")
    local ClassificationIndex = require("Iris/UI/Browser/IrisBrowserClassificationIndex")
    local ProjectionBuilder = require("Iris/UI/Browser/IrisBrowserProjectionBuilder")
    local metrics = {
        isEnabled = function() return false end,
        increment = function() end,
    }
    local candidate = ProjectionBuilder.build(itemIndex, {
        categoryOrder = CategoryIndex.CATEGORY_ORDER,
        subcategoryMap = CategoryIndex.SUBCATEGORY_MAP,
        metrics = metrics,
        currentGeneration = 0,
    })

    for _, fullType in ipairs(ordered) do
        local row = assert(candidate.rowsByFullType[fullType])
        local memberships = {}
        for _, location in ipairs(candidate.itemLocationsByFullType[fullType] or {}) do
            memberships[#memberships + 1] = location.category .. "." .. location.subcategory
        end
        table.sort(memberships)
        local primary = row.primaryLocation or {}
        local categoryEntry = CategoryIndex.CATEGORY_KEYS[primary.category] or {}
        local subcategoryEntry = CategoryIndex.SUBCATEGORY_KEYS[primary.subcategory] or {}
        local presentationCategory, presentationSubcategory = ClassificationIndex.chooseLocation(
            candidate.classificationIndex,
            fullType,
            CategoryIndex.CATEGORY_ORDER,
            CategoryIndex.SUBCATEGORY_MAP
        )
        local fields = {
            "IRIS_D2_ROW",
            fullType,
            table.concat(memberships, ","),
            primary.category or "",
            primary.subcategory or "",
            row.primaryTag or "",
            categoryEntry.key or "",
            subcategoryEntry.key or "",
            IrisPrimarySubcategory and IrisPrimarySubcategory[fullType] or "",
            presentationCategory or "",
            presentationSubcategory or "",
            tostring(#memberships),
        }
        print(table.concat(fields, "\t"))
    end
    print("IRIS_D2_PROJECTION_PASS count=" .. tostring(#ordered))
    return
end

local backingOne = { "Tool.1-A", "Combat.2-A" }
local backingTwo = { "Tool.1-A" }
local backing = {
    ["Base.One"] = backingOne,
    ["Base.Two"] = backingTwo,
}
package.preload["Iris/Data/IrisClassifications"] = function() return backing end
IrisPrimarySubcategory = {
    ["Base.One"] = "Combat.2-A",
}

local Tags = require("Iris/API/Tags")
local exported = {}
for key, value in pairs(Tags) do
    if type(value) == "function" then exported[#exported + 1] = key end
end
table.sort(exported)
assert(table.concat(exported, ",") == "getTags,getTagsForItem,hasTag,isClassified")

local item = { fullType = "Base.One" }
function item:getFullType() return self.fullType end
function item:getFullName() return self.fullType end
function item:getDisplayName() return "One" end
function item:getType() return "Normal" end

local publicArray = Tags.getTags("Base.One")
local publicSet = Tags.getTagsForItem(item)
publicArray[1] = "mutated"
publicSet["Tool.1-A"] = nil
assert(backingOne[1] == "Tool.1-A")
assert(Tags.getTags("Base.One")[1] == "Tool.1-A")
assert(Tags.getTagsForItem(item)["Tool.1-A"] == true)

local function collection(values)
    local result = { values = values }
    function result:size() return #self.values end
    function result:get(index) return self.values[index + 1] end
    return result
end
getAllItems = function() return collection({ item }) end
package.preload["Iris/IrisAPI"] = function()
    return {
        Tags = Tags,
        Index = { getRecipeConnectionsForItem = function() return {} end },
    }
end

local BrowserData = require("Iris/UI/Browser/IrisBrowserData")
assert(BrowserData.ensureReady() == true)
assert(BrowserData.getItem("Base.One") == item)
local category, subcategory = BrowserData.getItemLocation("Base.One")
assert(category == "Combat" and subcategory == "2-A")
assert(BrowserData._cache.rowsByFullType["Base.One"].primaryTag == "Combat.2-A")
assert(BrowserData._cache.categories.Tool.subcategories["1-A"].items["Base.One"] == true)
assert(BrowserData._cache.categories.Combat.subcategories["2-A"].items["Base.One"] == true)

local ProjectionBuilder = require("Iris/UI/Browser/IrisBrowserProjectionBuilder")
local CategoryIndex = require("Iris/UI/Browser/IrisBrowserCategoryIndex")
local metrics = { isEnabled = function() return false end, increment = function() end }
IrisPrimarySubcategory["Base.Two"] = "Combat.2-A"
local invalidItem = { fullType = "Base.Two" }
function invalidItem:getFullType() return self.fullType end
function invalidItem:getDisplayName() return "Two" end
function invalidItem:getType() return "Normal" end
local ok, failure = pcall(ProjectionBuilder.build, { itemsByFullType = { ["Base.Two"] = invalidItem } }, {
    categoryOrder = CategoryIndex.CATEGORY_ORDER,
    subcategoryMap = CategoryIndex.SUBCATEGORY_MAP,
    metrics = metrics,
    currentGeneration = 0,
})
assert(ok == false)
assert(tostring(failure):find("not an accepted membership", 1, true) ~= nil)
IrisPrimarySubcategory["Base.Two"] = nil

local seen = {}
local function assertBackingUnreachable(value)
    if type(value) ~= "table" or seen[value] then return end
    seen[value] = true
    assert(not rawequal(value, backing))
    assert(not rawequal(value, backingOne))
    assert(not rawequal(value, backingTwo))
    for key, nested in pairs(value) do
        assertBackingUnreachable(key)
        assertBackingUnreachable(nested)
    end
end
assertBackingUnreachable(BrowserData._cache)
assertBackingUnreachable(BrowserData.getItems("Tool", "1-A"))

print("IRIS_TAGS_PUBLIC_SURFACE_ISOLATION_PASS exported=" .. table.concat(exported, ","))
