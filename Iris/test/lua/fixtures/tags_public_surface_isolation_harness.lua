local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local backingOne = { "Tool.1-A", "Combat.2-A" }
local backingTwo = { "Tool.1-A" }
local backing = {
    ["Base.One"] = backingOne,
    ["Base.Two"] = backingTwo,
}
package.preload["Iris/Data/IrisClassifications"] = function() return backing end

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
assert(category == "Tool" and subcategory == "1-A")

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
