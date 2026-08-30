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

local publicTagCalls = 0
api = {
    Tags={getTagsForItem=function()
        publicTagCalls = publicTagCalls + 1
        return { ["Tool.1-A"]=true }
    end},
    Index={getRecipeConnectionsForItem=function() return {} end},
}
local ready, readyState = BrowserData.ensureReady()
assert(ready and readyState.state == "ready")
assert(publicTagCalls == 0, "Browser build must not reconstruct public tag Sets")
assert(BrowserData._built == true and BrowserData.getItem("Base.Hammer") == item)
local readyInstrumentation = BrowserData.getInstrumentation()
assert(readyInstrumentation.buildAttempts == 2 and readyInstrumentation.getAllItemsCallCount == 1)
assert(readyInstrumentation.scannedItemCount == 1 and readyInstrumentation.generation == 1)
assert(readyInstrumentation.postIndexMaterializationPassCount == 1)
assert(readyInstrumentation.materializedRowCount == 1)
assert(readyInstrumentation.retainedItemReferenceCount == 1)
assert(readyInstrumentation.tagArrayToSetConversionCount == 0)
assert(readyInstrumentation.chooseLocationComparisonCount == 0)
assert(readyInstrumentation.lastBuildElapsedMilliseconds >= readyInstrumentation.lastScanElapsedMilliseconds)
assert(BrowserData.ensureReady() == true)
assert(BrowserData.getInstrumentation().getAllItemsCallCount == 1)

local realClassificationIndex = require("Iris/UI/Browser/IrisBrowserClassificationIndex")
package.loaded["Iris/UI/Browser/IrisBrowserData"] = nil
package.loaded["Iris/UI/Browser/IrisBrowserClassificationIndex"] = nil
local injectedAddTagCalls = 0
package.preload["Iris/UI/Browser/IrisBrowserClassificationIndex"] = function()
    return {
        createEmpty = realClassificationIndex.createEmpty,
        addTag = function()
            injectedAddTagCalls = injectedAddTagCalls + 1
            error("standalone post-scan classification failure")
        end,
    }
end
local PostScanFailBrowserData = require("Iris/UI/Browser/IrisBrowserData")
PostScanFailBrowserData.setInstrumentationEnabled(true)
local postScanReady, postScanState = PostScanFailBrowserData.ensureReady()
assert(postScanReady == false and postScanState.state == "retryable_failed")
assert(postScanState.reason == "cache_build_failed" and PostScanFailBrowserData._cache == nil)
assert(injectedAddTagCalls > 0, "addTag failure fixture did not reach the revised boundary")
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

local foldedSubcategory = BrowserData._cache.categories.Tool.subcategories["1-B"]
local firstFoldedCount = BrowserData._calculateFoldedCount("Tool", "1-B", foldedSubcategory)
local cachedGroupCount = 0
for _, _ in pairs(BrowserData._cache.foldedCountsByGrouping) do cachedGroupCount = cachedGroupCount + 1 end
local secondFoldedCount = BrowserData._calculateFoldedCount("Tool", "1-B", foldedSubcategory)
local repeatedGroupCount = 0
for _, _ in pairs(BrowserData._cache.foldedCountsByGrouping) do repeatedGroupCount = repeatedGroupCount + 1 end
assert(firstFoldedCount == 1 and secondFoldedCount == firstFoldedCount)
assert(cachedGroupCount == 1 and repeatedGroupCount == cachedGroupCount)

local Query = require("Iris/UI/Browser/IrisBrowserQuery")
local cache = {
    itemsByFullType={ ["Base.Hammer"]=item, ["Base.HandAxe"]=handAxeItem },
    rowsByFullType={
        ["Base.Hammer"]={fullType="Base.Hammer",item=item,displayName="Hammer",
            folded="hammer\0base.hammer",primaryLocation={category="Tool",subcategory="1-A"}},
        ["Base.HandAxe"]={fullType="Base.HandAxe",item=handAxeItem,displayName="Hand Axe",
            folded="hand axe\0base.handaxe",primaryLocation={category="Tool",subcategory="1-A"}},
    },
    generation=1,
    searchSnapshot={generation=1,locale="EN",rows={
        {fullType="Base.Hammer",displayName="Hammer",folded="hammer\0base.hammer",category="Tool",subcategory="1-A"},
        {fullType="Base.HandAxe",displayName="Hand Axe",folded="hand axe\0base.handaxe",category="Tool",subcategory="1-A"},
    }},
    searchMetrics={searchCalls=0,totalScanRows=0,lastScanRows=0,prefixReuseCount=0,fullSortCount=1},
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
local previousSnapshot = cache.searchSnapshot
local previousRowsByFullType = cache.rowsByFullType
local nativeSort = table.sort
local reentrantObservedOldSnapshot = false
table.sort = function(rows, comparator)
    local nested = Query.searchAll(cache, "HAM", function() return "Tool", "1-A" end, "EN")
    reentrantObservedOldSnapshot = cache.searchSnapshot == previousSnapshot and
        cache.rowsByFullType == previousRowsByFullType and
        #nested == 1 and nested[1].displayName == "Hammer"
    error("injected locale candidate sort failure")
end
local failedLocaleRefresh = pcall(function()
    Query.searchAll(cache, "손도끼", function() return "Tool", "1-A" end, "KO")
end)
table.sort = nativeSort
assert(failedLocaleRefresh == false and reentrantObservedOldSnapshot == true)
assert(cache.searchSnapshot == previousSnapshot and cache.rowsByFullType == previousRowsByFullType)
displayNameCalls = 0
local localeChanged = Query.searchAll(cache, "손도끼", function() return "Tool", "1-A" end, "KO")
assert(#localeChanged == 1 and localeChanged[1].displayName == "손도끼")
assert(cache.searchMetrics.lastScanRows == 2 and displayNameCalls == 2)
assert(cache.searchMetrics.fullSortCount == 2)
local noResult = Query.searchAll(cache, "ZZZ", function() return "Tool", "1-A" end, "KO")
assert(#noResult == 0 and cache.searchMetrics.lastScanRows == 2)
currentLocale = "EN"
Query.searchAll(cache, "HA", function() return "Tool", "1-A" end, "EN")
cache.generation = 2
local generationChanged = Query.searchAll(cache, "HAM", function() return "Tool", "1-A" end, "EN")
assert(#generationChanged == 1 and cache.searchMetrics.lastScanRows == 2)
assert(cache.searchMetrics.prefixReuseCount == 1)
assert(displayNameCalls == 6)
assert(cache.searchMetrics.fullSortCount == 4)

package.preload["Iris/UI/Tooltip/IrisTooltipSummary"] = function()
    error("Alt must not load legacy summary")
end
package.loaded["Iris/Util/IrisTranslationResolver"] = {getDetectedLangKey=function() return "EN" end}
package.preload["Iris/Data/IrisTooltipT2Data"] = function()
    return {["Base.Hammer"]={en={"Static row"},ko={"정적 행"}}}
end
getTextManager = function() return {getFontHeight=function() return 17 end,
    MeasureStringX=function(_,_,text) return #text*6 end} end
getCore = function() return {getScreenWidth=function() return 900 end,
    getScreenHeight=function() return 700 end} end
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
        getAbsoluteX=function() return 0 end,
        getAbsoluteY=function() return 0 end,
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
assert(tooltipMetrics.staticLookups == 2 and tooltipMetrics.retainedFullTypeEntries == 0)
assert(tooltipA.drawn[1] == "Static row" and tooltipMetrics.summaryGetCalls == 0)
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
    " tooltip_static_lookups=" .. tostring(tooltipMetrics.staticLookups))
