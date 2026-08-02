local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local function collection(items)
    local value = {items=items}
    function value:size() return #self.items end
    function value:get(index) return self.items[index + 1] end
    return value
end

local displayNameCalls = 0
local item = {fullType="Base.Hammer"}
function item:getFullType() return self.fullType end
function item:getFullName() return self.fullType end
function item:getDisplayName() displayNameCalls = displayNameCalls + 1 return "Hammer" end
function item:getType() return "Weapon" end
getAllItems = function() return collection({item}) end

local api = nil
package.preload["Iris/IrisAPI"] = function()
    if not api then error("standalone missing IrisAPI") end
    return api
end

local BrowserData = require("Iris/UI/Browser/IrisBrowserData")
local initial = BrowserData.getBuildState()
assert(initial.state == "uninitialized" and BrowserData._built == false)

local missingReady, missingState = BrowserData.ensureReady()
assert(missingReady == false and missingState.state == "retryable_failed" and missingState.dependency == "Iris/IrisAPI")
assert(BrowserData._cache == nil and BrowserData._built == false)

local nested = nil
api = {
    Tags={getTagsForItem=function()
        if not nested then
            local ready, state = BrowserData.ensureReady()
            nested = {ready=ready,state=state.state}
        end
        return { ["Tool.1-A"]=true }
    end},
    Index={getRecipeConnectionsForItem=function() return {} end},
}
local ready, readyState = BrowserData.ensureReady()
assert(ready and readyState.state == "ready" and nested and nested.ready == false and nested.state == "building")
assert(BrowserData._built == true and BrowserData.getItem("Base.Hammer") == item)

local foldedSubcategory = BrowserData._cache.categories.Tool.subcategories["1-A"]
local firstFoldedCount = BrowserData._calculateFoldedCount("Tool", "1-A", foldedSubcategory)
local cachedGroupCount = 0
for _, _ in pairs(BrowserData._cache.foldedCountsByGrouping) do cachedGroupCount = cachedGroupCount + 1 end
local secondFoldedCount = BrowserData._calculateFoldedCount("Tool", "1-A", foldedSubcategory)
local repeatedGroupCount = 0
for _, _ in pairs(BrowserData._cache.foldedCountsByGrouping) do repeatedGroupCount = repeatedGroupCount + 1 end
assert(firstFoldedCount == 1 and secondFoldedCount == firstFoldedCount)
assert(cachedGroupCount == 1 and repeatedGroupCount == cachedGroupCount)

local Query = require("Iris/UI/Browser/IrisBrowserQuery")
local cache = {
    itemsByFullType={ ["Base.Hammer"]=item },
    searchKeysByFullType={ ["Base.Hammer"]={displayName="Hammer",displayNameLower="hammer",fullTypeLower="base.hammer"} },
}
displayNameCalls = 0
local first = Query.searchAll(cache, "HAMMER", function() return "Tool", "1-A" end)
local second = Query.searchAll(cache, "hammer", function() return "Tool", "1-A" end)
assert(#first == 1 and #second == 1 and displayNameCalls == 0)

local ListController = require("Iris/UI/Browser/IrisBrowserListController")
local event, eventReason = ListController.resolveSelectedPayload({items={},selected=0}, {item={name="event"}})
local fallback, fallbackReason = ListController.resolveSelectedPayload({items={{item={name="selected"}}},selected=1}, {})
local invalid, invalidReason = ListController.resolveSelectedPayload({items={},selected=2}, nil)
assert(event.name == "event" and eventReason == "event_item")
assert(fallback.name == "selected" and fallbackReason == "selected_index")
assert(invalid == nil and invalidReason == "selected_index_invalid")

package.loaded["Iris/API/StaticData"] = nil
package.loaded["Iris/Data/IrisCapabilities"] = nil
local optionalLoadCalls = 0
package.preload["Iris/Data/IrisCapabilities"] = function()
    optionalLoadCalls = optionalLoadCalls + 1
    error("standalone optional module absent")
end
local StaticData = require("Iris/API/StaticData")
assert(StaticData.get("capabilities") == nil)
assert(StaticData.get("capabilities") == nil)
assert(optionalLoadCalls == 1 and StaticData.getFailureReason("capabilities") ~= nil)
assert(StaticData.reset("capabilities") == true)
package.preload["Iris/Data/IrisCapabilities"] = function()
    optionalLoadCalls = optionalLoadCalls + 1
    return {fixture=true}
end
local recoveredOptional = StaticData.get("capabilities")
assert(recoveredOptional and recoveredOptional.fixture == true and optionalLoadCalls == 2)
package.preload["Iris/Data/IrisCapabilities"] = nil

print("IRIS_BROWSER_STANDALONE_PASS state=ready normalized_getter_calls=" .. tostring(displayNameCalls) ..
    " optional_load_calls=" .. tostring(optionalLoadCalls) .. " folded_cache_entries=" .. tostring(repeatedGroupCount))
