local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local function collection(items)
    local value = {items=items}
    function value:size() return #self.items end
    function value:get(index) return self.items[index + 1] end
    return value
end

local displayNameCalls = 0
local currentLocale = "EN"
local item = {fullType="Base.Hammer"}
function item:getFullType() return self.fullType end
function item:getFullName() return self.fullType end
function item:getDisplayName()
    displayNameCalls = displayNameCalls + 1
    return currentLocale == "KO" and "망치" or "Hammer"
end
function item:getType() return "Weapon" end
local handAxeItem = {fullType="Base.HandAxe"}
function handAxeItem:getFullType() return self.fullType end
function handAxeItem:getFullName() return self.fullType end
function handAxeItem:getDisplayName()
    displayNameCalls = displayNameCalls + 1
    return currentLocale == "KO" and "손도끼" or "Hand Axe"
end
local healthyGetAllItems = function() return collection({item}) end
getAllItems = healthyGetAllItems

local api = nil
package.preload["Iris/IrisAPI"] = function()
    if not api then error("standalone missing IrisAPI") end
    return api
end

local BrowserData = require("Iris/UI/Browser/IrisBrowserData")
local initial = BrowserData.getBuildState()
assert(initial.state == "uninitialized" and BrowserData._built == false)
local initialInstrumentation = BrowserData.getInstrumentation()
assert(initialInstrumentation.enabled == false)
assert(initialInstrumentation.getAllItemsCallCount == 0 and initialInstrumentation.scannedItemCount == 0)
BrowserData.setInstrumentationEnabled(true)

local missingReady, missingState = BrowserData.ensureReady()
assert(missingReady == false and missingState.state == "retryable_failed" and missingState.dependency == "Iris/IrisAPI")
assert(BrowserData._cache == nil and BrowserData._built == false)
assert(BrowserData.getInstrumentation().getAllItemsCallCount == 0)

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
local readyInstrumentation = BrowserData.getInstrumentation()
assert(readyInstrumentation.buildAttempts == 2 and readyInstrumentation.getAllItemsCallCount == 1)
assert(readyInstrumentation.scannedItemCount == 1 and readyInstrumentation.generation == 1)
assert(readyInstrumentation.lastBuildElapsedMilliseconds >= readyInstrumentation.lastScanElapsedMilliseconds)
assert(BrowserData.ensureReady() == true)
assert(BrowserData.getInstrumentation().getAllItemsCallCount == 1)

local realClassificationIndex = require("Iris/UI/Browser/IrisBrowserClassificationIndex")
package.loaded["Iris/UI/Browser/IrisBrowserData"] = nil
package.loaded["Iris/UI/Browser/IrisBrowserClassificationIndex"] = nil
package.preload["Iris/UI/Browser/IrisBrowserClassificationIndex"] = function()
    return {
        createEmpty = realClassificationIndex.createEmpty,
        addItem = function() error("standalone post-scan classification failure") end,
    }
end
local PostScanFailBrowserData = require("Iris/UI/Browser/IrisBrowserData")
PostScanFailBrowserData.setInstrumentationEnabled(true)
local postScanReady, postScanState = PostScanFailBrowserData.ensureReady()
assert(postScanReady == false and postScanState.state == "retryable_failed")
assert(postScanState.reason == "cache_build_failed" and PostScanFailBrowserData._cache == nil)
local postScanInstrumentation = PostScanFailBrowserData.getInstrumentation()
assert(postScanInstrumentation.buildAttempts == 1)
assert(postScanInstrumentation.getAllItemsCallCount == 1)
assert(postScanInstrumentation.scannedItemCount == 1)
package.preload["Iris/UI/Browser/IrisBrowserClassificationIndex"] = nil
package.loaded["Iris/UI/Browser/IrisBrowserClassificationIndex"] = realClassificationIndex
package.loaded["Iris/UI/Browser/IrisBrowserData"] = BrowserData

BrowserData.resetForReload()
BrowserData.resetInstrumentation()
getAllItems = nil
local absentReady, absentState = BrowserData.ensureReady()
assert(absentReady == false and absentState.state == "retryable_failed")
assert(absentState.reason == "get_all_items_unavailable" and BrowserData._cache == nil)
getAllItems = function() error("standalone getAllItems failure") end
local failedReady, failedState = BrowserData.ensureReady()
assert(failedReady == false and failedState.state == "retryable_failed")
assert(failedState.reason == "get_all_items_failed" and BrowserData._cache == nil)
getAllItems = healthyGetAllItems
local recoveredReady, recoveredState = BrowserData.ensureReady()
assert(recoveredReady == true and recoveredState.state == "ready")
local recoveryInstrumentation = BrowserData.getInstrumentation()
assert(recoveryInstrumentation.buildAttempts == 3 and recoveryInstrumentation.getAllItemsCallCount == 2)
assert(recoveryInstrumentation.scannedItemCount == 1 and recoveryInstrumentation.generation == 2)

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
    itemsByFullType={ ["Base.Hammer"]=item, ["Base.HandAxe"]=handAxeItem },
    searchKeysByFullType={
        ["Base.Hammer"]={displayName="Hammer",folded="hammer\0base.hammer"},
        ["Base.HandAxe"]={displayName="Hand Axe",folded="hand axe\0base.handaxe"},
    },
    searchKeysLocale="EN",
    generation=1,
    searchMetrics={searchCalls=0,totalScanRows=0,lastScanRows=0,prefixReuseCount=0},
}
displayNameCalls = 0
local first = Query.searchAll(cache, "HA", function() return "Tool", "1-A" end, "EN")
local second = Query.searchAll(cache, "HAM", function() return "Tool", "1-A" end, "EN")
assert(#first == 2 and #second == 1 and displayNameCalls == 0)
assert(cache.searchMetrics.prefixReuseCount == 1 and cache.searchMetrics.lastScanRows == 2)
second[1].displayName = "mutated"
local empty = Query.searchAll(cache, "", function() return "Tool", "1-A" end, "EN")
local afterEmpty = Query.searchAll(cache, "HAMM", function() return "Tool", "1-A" end, "EN")
assert(#empty == 0 and #afterEmpty == 1 and afterEmpty[1].displayName == "Hammer")
assert(cache.searchMetrics.prefixReuseCount == 1 and cache.searchMetrics.lastScanRows == 2)
local unrelated = Query.searchAll(cache, "AXE", function() return "Tool", "1-A" end, "EN")
assert(#unrelated == 1 and unrelated[1].displayName == "Hand Axe")
currentLocale = "KO"
local localeChanged = Query.searchAll(cache, "손도끼", function() return "Tool", "1-A" end, "KO")
assert(#localeChanged == 1 and localeChanged[1].displayName == "손도끼")
assert(cache.searchMetrics.lastScanRows == 2 and displayNameCalls == 2)
local noResult = Query.searchAll(cache, "ZZZ", function() return "Tool", "1-A" end, "KO")
assert(#noResult == 0 and cache.searchMetrics.lastScanRows == 2)
currentLocale = "EN"
Query.searchAll(cache, "HA", function() return "Tool", "1-A" end, "EN")
cache.generation = 2
local generationChanged = Query.searchAll(cache, "HAM", function() return "Tool", "1-A" end, "EN")
assert(#generationChanged == 1 and cache.searchMetrics.lastScanRows == 2)
assert(cache.searchMetrics.prefixReuseCount == 1)
assert(displayNameCalls == 4)

package.preload["Iris/UI/Tooltip/IrisTooltipSummary"] = function()
    return {
        get=function(fullType)
            return {fullType=fullType,tags={"Tool.1-A"},connections={"Recipe"},useCaseCount=1,revision="fixture-r1"}
        end,
    }
end
isKeyDown = function(code) return code == 56 end
UIFont = { Small = "Small" }
local AltTooltip = require("Iris/UI/Tooltip/IrisAltTooltip")
assert(AltTooltip.getDisplayLineCacheMetrics().enabled == false)
AltTooltip.setInstrumentationEnabled(true)
AltTooltip.resetDisplayLineCache()
local function tooltipFixture()
    local drawn = {}
    return {
        item=item,
        height=20,
        width=200,
        drawn=drawn,
        drawRect=function() end,
        drawRectBorder=function() end,
        drawText=function(self, text) table.insert(self.drawn, text) end,
        setHeight=function(self, height) self.height=height end,
    }
end
local tooltipA = tooltipFixture()
local tooltipB = tooltipFixture()
AltTooltip.addIrisOverlay(tooltipA)
AltTooltip.addIrisOverlay(tooltipB)
local tooltipMetrics = AltTooltip.getDisplayLineCacheMetrics()
assert(tooltipMetrics.misses == 1 and tooltipMetrics.hits == 1)
assert(#tooltipA.drawn == #tooltipB.drawn and #tooltipA.drawn <= 4)

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
    " optional_load_calls=" .. tostring(optionalLoadCalls) .. " folded_cache_entries=" .. tostring(repeatedGroupCount) ..
    " get_all_items_calls=" .. tostring(readyInstrumentation.getAllItemsCallCount) ..
    " recovery_get_all_items_calls=" .. tostring(recoveryInstrumentation.getAllItemsCallCount) ..
    " prefix_reuse_count=" .. tostring(cache.searchMetrics.prefixReuseCount) ..
    " tooltip_cache_hits=" .. tostring(tooltipMetrics.hits))
