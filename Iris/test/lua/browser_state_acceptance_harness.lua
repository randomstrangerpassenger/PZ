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
local Search = require("Iris/UI/Browser/IrisBrowserSearch")
local cache = {
    itemsByFullType={ ["Base.Hammer"]=item, ["Base.HandAxe"]=handAxeItem },
    rowsByFullType={
        ["Base.Hammer"]={fullType="Base.Hammer",item=item,displayName="Hammer",
            searchDocument=Search.document("Base.Hammer", "Hammer"),primaryLocation={category="Tool",subcategory="1-A"}},
        ["Base.HandAxe"]={fullType="Base.HandAxe",item=handAxeItem,displayName="Hand Axe",
            searchDocument=Search.document("Base.HandAxe", "Hand Axe"),primaryLocation={category="Tool",subcategory="1-A"}},
    },
    generation=1,
    searchSnapshot={generation=1,locale="EN",rows={
        {fullType="Base.Hammer",displayName="Hammer",searchDocument=Search.document("Base.Hammer", "Hammer"),category="Tool",subcategory="1-A"},
        {fullType="Base.HandAxe",displayName="Hand Axe",searchDocument=Search.document("Base.HandAxe", "Hand Axe"),category="Tool",subcategory="1-A"},
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
local normalizedGetterCalls = displayNameCalls

-- One integrated search contract exercise: production projection, Query, Data,
-- controller and loader. Constructed collision cases are not active-PZ evidence.
do
    local StaticData = require("Iris/API/StaticData")
    local Loader = require("Iris/IrisTranslationLoader")
    local originalGet, originalPrimary, originalTranslator = StaticData.get, IrisPrimarySubcategory, Translator
    local classifications = {}
    StaticData.get = function(key)
        if key == "classifications" then return classifications end
        return originalGet(key)
    end
    IrisPrimarySubcategory = nil
    Translator = {getLanguage=function() return currentLocale:lower() end}
    local function locale(value)
        currentLocale = value
        Loader.init()
        assert(Loader.getLangKey() == value)
    end
    local function makeItem(fullType, ko, en)
        return {
            getFullType=function() return fullType end,
            getFullName=function() return fullType end,
            getDisplayName=function() return currentLocale == "KO" and ko or en end,
            getType=function() return "Normal" end,
        }
    end
    local function install(items, locations)
        classifications = {}
        for _, value in ipairs(items) do
            local fullType = value:getFullType()
            classifications[fullType] = locations and locations[fullType] or {"Tool.1-A"}
        end
        getAllItems = function() return collection(items) end
        BrowserData.resetForReload()
        assert(BrowserData.ensureReady())
        assert(#BrowserData._cache.searchSnapshot.rows == #items)
    end
    local function identities(rows)
        local values = {}
        for _, row in ipairs(rows) do
            values[#values + 1] = row.fullType .. ":" .. row.displayName .. ":" ..
                tostring(row.isPrimary) .. ":" .. table.concat(row.variants or {}, ",")
        end
        return table.concat(values, "|")
    end
    local function equalFresh(query)
        local incremental = BrowserData.searchAll(query)
        local prefix = BrowserData._cache.searchPrefixState
        BrowserData._cache.searchPrefixState = nil
        local fresh = BrowserData.searchAll(query)
        assert(identities(incremental) == identities(fresh), "incremental/fresh divergence: " .. query)
        BrowserData._cache.searchPrefixState = prefix
        return incremental
    end

    -- Fixed input metadata, independently counted before implementation. Last
    -- exact-key occurrence wins; conflicting duplicates fail instead of hiding.
    local function readCorpus(path)
        local handle = assert(io.open(path, "rb"))
        local text = handle:read("*a")
        handle:close()
        if text:sub(1, 2) == string.char(254, 255) then
            -- The fixed KO source is UTF-16BE, with BMP characters only. This
            -- fixture decoder is not a runtime normalizer or PZ parser claim.
            assert(#text % 2 == 0, "truncated UTF-16 corpus")
            local decoded = {}
            for offset = 3, #text, 2 do
                local code = text:byte(offset) * 256 + text:byte(offset + 1)
                assert(code < 55296 or code > 57343, "unsupported corpus surrogate")
                if code < 128 then decoded[#decoded + 1] = string.char(code)
                elseif code < 2048 then decoded[#decoded + 1] = string.char(192 + math.floor(code / 64), 128 + code % 64)
                else decoded[#decoded + 1] = string.char(224 + math.floor(code / 4096),
                    128 + math.floor(code / 64) % 64, 128 + code % 64) end
            end
            text = table.concat(decoded)
        end
        return text
    end
    local corpusCounts = {KO={2017,2007,1661}, EN={1974,1974,1615}}
    for _, lang in ipairs({"KO", "EN"}) do
        locale(lang)
        local byType, byName, rawCount = {}, {}, 0
        local corpus = readCorpus(repositoryRoot .. "/lua/shared/Translate/" .. lang .. "/ItemName_" .. lang .. ".txt")
        for line in corpus:gmatch("[^\r\n]+") do
            local fullType, name = line:match('^%s*ItemName_(%S+)%s*=%s*"(.*)"%s*,?%s*$')
            if fullType then
                rawCount = rawCount + 1
                assert(not byType[fullType] or byType[fullType] == name, "conflicting translation key")
                byType[fullType] = name
                byName[name] = true
            end
        end
        local items, names = {}, {}
        for fullType, name in pairs(byType) do items[#items + 1] = makeItem(fullType, name, name) end
        for name in pairs(byName) do names[#names + 1] = name end
        table.sort(names)
        local counts = corpusCounts[lang]
        assert(rawCount == counts[1] and #items == counts[2] and #names == counts[3],
            lang .. " corpus counts: " .. rawCount .. "/" .. #items .. "/" .. #names)
        install(items)
        local source = BrowserData._cache.searchSnapshot
        for _, name in ipairs(names) do
            local expected = {}
            for fullType, displayName in pairs(byType) do
                if displayName:lower() == name:lower() then expected[#expected + 1] = fullType end
            end
            table.sort(expected, function(a, b)
                if byType[a] ~= byType[b] then return byType[a] < byType[b] end
                return a < b
            end)
            local rows = BrowserData.searchAll(name)
            assert(#rows >= #expected, lang .. " exact group missing: " .. name)
            for rank, fullType in ipairs(expected) do
                assert(rows[rank].fullType == fullType, lang .. " exact rank: " .. name .. " / " .. fullType)
            end
        end
        assert(BrowserData._cache.searchSnapshot == source, "query rebuilt corpus snapshot")
        print("SEARCH_CORPUS locale=" .. lang .. " raw=" .. rawCount .. " exact=" .. #items ..
            " queries=" .. #names .. " violations=0")
        if lang == "KO" then
            -- Read-only model of the inspected predecessor's literal filter and
            -- name/FullType order. This is not an executed predecessor/PZ build.
            local baseline = {}
            for fullType, name in pairs(byType) do
                baseline[#baseline + 1] = {fullType=fullType, displayName=name}
            end
            table.sort(baseline, function(a, b)
                if a.displayName ~= b.displayName then return a.displayName < b.displayName end
                return a.fullType < b.fullType
            end)
            for _, case in ipairs({
                {"망치", "Base.Hammer"}, {"  망치  ", "Base.Hammer"},
                {"대형 망치", "Base.Sledgehammer"}, {"대형  망치", "Base.Sledgehammer"},
                {"대형망치", "Base.Sledgehammer"}, {"망치 대형", "Base.Sledgehammer"},
                {"ㅁㅊ", "Base.Hammer"}, {"Hammer", "Base.Hammer"},
                {"Club Hammer", "Base.ClubHammer"}, {"   ", "Base.Hammer"},
            }) do
                local before, beforeRank, afterRank = {}, "absent", "absent"
                for _, row in ipairs(baseline) do
                    if (row.displayName:lower() .. "\0" .. row.fullType:lower()):find(case[1]:lower(), 1, true) then
                        before[#before + 1] = row
                        if row.fullType == case[2] then beforeRank = tostring(#before) end
                    end
                end
                local after = BrowserData.searchAll(case[1])
                for rank, row in ipairs(after) do if row.fullType == case[2] then afterRank = tostring(rank) end end
                print("SEARCH_CASE query=[" .. case[1] .. "] target=" .. case[2] .. " before_count=" .. #before ..
                    " before_rank=" .. beforeRank .. " after_count=" .. #after .. " after_rank=" .. afterRank)
            end
        end
    end

    locale("KO")
    local fixtures = {
        makeItem("Base.Hammer", "망치", "Hammer"),
        makeItem("Base.Sledgehammer", "대형 망치", "Sledgehammer"),
        makeItem("Base.Sledgehammer2", "대형 망치", "Sledgehammer"),
        makeItem("Base.ClubHammer", "클럽 해머", "Club Hammer"),
        makeItem("Fixture.Compact", "대형망치", "Large Hammer"),
        makeItem("Fixture.Partial", "망치 집", "Hammer Case"),
        makeItem("Fixture.IdName", "Base.Hammer", "Base.Hammer"),
        makeItem("Base.LemonGrass", "레몬그라스", "Lemongrass"),
        makeItem("Base.Lemongrass", "레몬그라스", "Lemongrass"),
        makeItem("Fixture.Punctuation", "A-1 (B)", "A-1 (B)"),
        makeItem("Fixture.Mango", "망고", "Mango"),
        makeItem("Fixture.Net", "철조망", "Wire Fence"),
    }
    install(fixtures)
    local quality = {
        {"망치", {"Base.Hammer"}}, {"  망치  ", {"Base.Hammer"}},
        {"대형 망치", {"Base.Sledgehammer", "Base.Sledgehammer2", "Fixture.Compact"}},
        {"대형  망치", {"Base.Sledgehammer", "Base.Sledgehammer2", "Fixture.Compact"}},
        {"대형망치", {"Fixture.Compact", "Base.Sledgehammer", "Base.Sledgehammer2"}},
        {"형", {"Base.Sledgehammer", "Base.Sledgehammer2", "Fixture.Compact"}},
        {"해머", {"Base.ClubHammer"}},
        {"Base.Hammer", {"Fixture.IdName", "Base.Hammer"}},
        {"A-1 (B)", {"Fixture.Punctuation"}},
        {"A1B", {}}, {"대형 망치 없음", {}}, {"ㅁㅊ", {}},
        {"망치 대형", {}}, {"Club Hammer", {}},
    }
    for _, case in ipairs(quality) do
        local rows = equalFresh(case[1])
        for rank, fullType in ipairs(case[2]) do
            assert(rows[rank] and rows[rank].fullType == fullType, "quality rank: " .. case[1])
        end
        if #case[2] == 0 then assert(#rows == 0, "unrelated result: " .. case[1]) end
        for _, row in ipairs(rows) do
            assert(row.searchDocument == nil and row.folded == nil and row.isPrimary == nil and row.variants == nil)
        end
    end
    assert(#BrowserData.searchAll("Hammer") == 5, "global ID retrieval or name-first scope changed")
    assert(#BrowserData.searchItems("Tool", "1-A", "Hammer") == 1, "local ID scope expanded")
    assert(#BrowserData.searchAll("base.lemongrass") == 2, "case-sensitive identity collision")
    local leaf = BrowserData._cache.rowsByFullType["Base.Hammer"]
    leaf.primaryTag = "Tool.1-B" -- Deliberately secondary, still lexical exact first.
    BrowserData._cache.rowsByFullType["Base.Sledgehammer"].primaryTag = "Tool.1-B"
    local localExact = BrowserData.searchItems("Tool", "1-A", "망치")
    assert(localExact[1].fullType == "Base.Hammer" and localExact[1].isPrimary == false)
    local localTie = BrowserData.searchItems("Tool", "1-A", "형")
    assert(localTie[1].fullType == "Base.Sledgehammer" and not localTie[1].isPrimary)
    assert(localTie[2].fullType == "Fixture.Compact" and localTie[2].isPrimary)
    assert(table.concat(localTie[1].variants, ",") == "Base.Sledgehammer,Base.Sledgehammer2")
    localTie[1].variants[1] = "caller mutation"
    localTie[1].displayName = "caller mutation"
    assert(BrowserData.searchItems("Tool", "1-A", "형")[1].variants[1] == "Base.Sledgehammer")
    assert(identities(BrowserData.searchItems("Tool", "1-A", "   ")) ==
        identities(BrowserData.getItems("Tool", "1-A")), "empty local browse ordering")
    assert(#BrowserData.searchItems("Combat", "2-A", "망치") == 0, "category scope leaked")
    local exported = BrowserData.searchAll("망치")
    exported[1].fullType, exported[1].displayName, exported[1].category = "changed", "changed", "changed"
    assert(BrowserData.searchAll("망치")[1].fullType == "Base.Hammer")
    assert(BrowserData.getItem("Base.Hammer") == fixtures[1])

    -- Membership and ranking must both equal a fresh query across these edits.
    for _, query in ipairs({"ㅁ", "망", "망치", "망", "", "대형", "대형  ", "대형 망치",
        " ", "망치", "Club", "Hammer", "Base.Hammer", "A-1 (B)"}) do equalFresh(query) end
    for _, lang in ipairs({"EN", "KO"}) do
        locale(lang)
        equalFresh("망치")
        assert(BrowserData._cache.searchSnapshot.locale == lang)
    end
    -- Extending a query changes which candidate is exact, reversing prior ranks.
    locale("EN")
    local broad = equalFresh("Hammer")
    assert(broad[1].fullType == "Base.Hammer")
    assert(equalFresh("Hammer Case")[1].fullType == "Fixture.Partial")
    locale("KO")

    -- Replacement failure, recursive refresh and changed generation cannot publish
    -- partial documents or relabel the old snapshot as the new owner.
    local oldSnapshot = BrowserData._cache.searchSnapshot
    local nativeDocument = Search.document
    Search.document = function() error("injected document failure") end
    assert(not pcall(Query.ensureLocale, BrowserData._cache, "KO"))
    Search.document = nativeDocument
    assert(BrowserData._cache.searchSnapshot == oldSnapshot)
    Search.document = function(...)
        Query.ensureLocale(BrowserData._cache, "KO")
        return nativeDocument(...)
    end
    assert(not pcall(Query.ensureLocale, BrowserData._cache, "KO"))
    Search.document = nativeDocument
    assert(BrowserData._cache.searchSnapshot == oldSnapshot)
    local generation = BrowserData._cache.generation
    Search.document = function(...)
        BrowserData._cache.generation = generation + 1
        return nativeDocument(...)
    end
    assert(not pcall(Query.ensureLocale, BrowserData._cache, "KO"))
    Search.document = nativeDocument
    assert(BrowserData._cache.searchSnapshot == oldSnapshot)
    BrowserData._cache.generation = generation
    assert(Query.ensureLocale(BrowserData._cache, "KO").locale == "KO")

    local Controller = require("Iris/UI/Browser/IrisBrowserListController")
    local methods = {}
    Controller.install(methods, {debug=function() end, logError=error, getBrowserData=function() return BrowserData end})
    local function list()
        return {items={}, selected=0,
            clear=function(self) self.items={}; self.selected=1 end,
            addItem=function(self, text, payload) self.items[#self.items + 1]={text=text,item=payload} end}
    end
    local function entry()
        return {text="", internal="", getText=function(self) return self.text end,
            getInternalText=function(self) return self.internal end,
            setText=function(self, text)
                if self.onTextChange then self:onTextChange() end
                self.text, self.internal = text, text
                if self.onTextChange then self:onTextChange() end
            end}
    end
    local function panel()
        return setmetatable({categoryList=list(), subcategoryList=list(), itemList=list(),
            searchBar=entry(), itemSearchBar=entry(), subcategorySearchBar=entry(),
            showDetail=function(self, fullType) self.detail=fullType end}, {__index=methods})
    end
    -- Model the reported engine boundary: callback before a completed edit,
    -- getText lagging behind the internal buffer, and paste with no callback.
    -- This fixture is not an assertion about every IME's composition events.
    local inputBrowser = panel()
    inputBrowser:loadCategories()
    inputBrowser:onCategorySelected({name="Tool"})
    inputBrowser:onSubcategorySelected({name="1-A"})
    inputBrowser.searchBar.onTextChange = function() inputBrowser:onGlobalSearchChange() end
    inputBrowser.searchBar:setText("망")
    local partialCount = #inputBrowser.itemList.items
    inputBrowser.searchBar.internal = "망치"
    inputBrowser:refreshSearchInput()
    assert(#inputBrowser.itemList.items < partialCount)
    assert(inputBrowser.itemList.items[1].item.fullType == "Base.Hammer")
    assert(#inputBrowser.categoryList.items > 0 and #inputBrowser.subcategoryList.items > 0)
    inputBrowser:onItemSelected(inputBrowser.itemList.items[1].item)
    local unchangedCalls = BrowserData._cache.searchMetrics.searchCalls
    inputBrowser:refreshSearchInput()
    inputBrowser:refreshSearchInput()
    inputBrowser:onGlobalSearchChange() -- Late duplicate event must not clear selection.
    assert(BrowserData._cache.searchMetrics.searchCalls == unchangedCalls)
    assert(inputBrowser.detail == "Base.Hammer")
    inputBrowser.searchBar.internal = "대형망치" -- Paste; rendered text still says 망.
    inputBrowser:refreshSearchInput()
    assert(inputBrowser.itemList.items[1].item.fullType == "Fixture.Compact")
    inputBrowser.searchBar.internal = "대형 망치 없음"
    inputBrowser:refreshSearchInput()
    assert(#inputBrowser.itemList.items == 0)
    inputBrowser.searchBar.internal = ""
    inputBrowser:refreshSearchInput()
    assert(inputBrowser.currentCategory == nil and inputBrowser.currentSubcategory == nil)
    assert(#inputBrowser.categoryList.items > 0 and #inputBrowser.subcategoryList.items == 0)
    assert(#inputBrowser.itemList.items == 0 and inputBrowser.categoryList.selected == 0)
    assert(inputBrowser.detail == nil and BrowserData._cache.searchPrefixState == nil)
    inputBrowser.searchBar:setText("망치")
    inputBrowser:onSubcategorySelected(inputBrowser.subcategoryList.items[1].item)
    inputBrowser:onGlobalSearchChange() -- Delayed SetText callback after navigation.
    inputBrowser:refreshSearchInput()
    assert(inputBrowser.searchBar:getInternalText() == "" and inputBrowser.currentSubcategory == "1-A")
    assert(#inputBrowser.itemList.items == #BrowserData.getItems("Tool", "1-A"))
    inputBrowser.searchBar:setText("망치")
    inputBrowser:onCategorySelected(inputBrowser.categoryList.items[1].item)
    assert(inputBrowser.currentCategory == "Tool" and inputBrowser.currentSubcategory == nil)
    assert(#inputBrowser.subcategoryList.items > 0 and inputBrowser.searchBar:getInternalText() == "")
    inputBrowser:refreshSearchInput()
    assert(#inputBrowser.itemList.items == 0)

    local unselected = panel()
    unselected:loadCategories()
    unselected.searchBar:setText("망") -- Partial input must not invent a browse target.
    unselected:onGlobalSearchChange()
    unselected.searchBar:setText("   ")
    unselected:onGlobalSearchChange()
    assert(unselected.currentCategory == nil and unselected.currentSubcategory == nil)
    assert(#unselected.itemList.items == 0 and #unselected.subcategoryList.items == 0)

    local browser = panel()
    browser:loadCategories()
    browser.searchBar:setText("망치")
    browser:onGlobalSearchChange()
    browser.itemList.selected = 2
    browser:onItemSelected(browser.itemList.items[1].item) -- Actual PZ raw callback payload.
    assert(browser.detail == "Base.Hammer" and browser.currentSelectedFullType == "Base.Hammer")
    browser.searchBar:setText("   ")
    browser:onGlobalSearchChange()
    assert(#browser.categoryList.items > 0 and #browser.subcategoryList.items == 0)
    assert(#browser.itemList.items == 0)
    assert(browser.itemList.selected == 0 and browser.detail == nil and browser.currentSelectedVariants == nil)
    assert(browser.currentCategory == nil and browser.currentSubcategory == nil)
    assert(BrowserData._cache.searchPrefixState == nil)
    browser:onCategorySelected({name="Tool"})
    browser:onSubcategorySelected({name="1-A"})
    browser.itemSearchBar:setText("大") -- Replacement with unrelated bytes.
    browser:onItemSearchChange()
    assert(#browser.itemList.items == 0)
    browser.itemSearchBar:setText("대형  망치")
    browser:onItemSearchChange()
    browser:onItemSelected(browser.itemList.items[1])
    assert(browser.detail == "Base.Sledgehammer" and #browser.currentSelectedVariants == 2)
    browser.itemSearchBar:setText("  ")
    browser:onItemSearchChange()
    assert(browser.detail == nil and browser.currentSelectedVariants == nil)
    assert(#browser.itemList.items == #BrowserData.getItems("Tool", "1-A"))
    browser.itemSearchBar:setText("망치")
    browser:onItemSearchChange()
    locale("EN")
    browser:refreshSearchOwner() -- Query is unchanged.
    assert(#browser.itemList.items == 0 and browser.currentCategory == "Tool")
    locale("KO")
    browser:refreshSearchOwner()
    assert(browser.itemList.items[1].item.fullType == "Base.Hammer")
    local calls = BrowserData._cache.searchMetrics.searchCalls
    browser:refreshSearchOwner()
    assert(BrowserData._cache.searchMetrics.searchCalls == calls, "unchanged owner queried again")
    browser.searchBar:setText("망치")
    browser:onGlobalSearchChange()
    locale("EN")
    browser:refreshSearchOwner()
    assert(#browser.itemList.items == 0)
    locale("KO")
    browser:refreshSearchOwner()
    assert(browser.itemList.items[1].item.fullType == "Base.Hammer")
    BrowserData.resetForReload()
    browser:refreshSearchOwner()
    assert(#browser.itemList.items == 0 and browser.detail == nil)
    install({makeItem("Fixture.New", "망치", "Hammer")})
    browser:refreshSearchOwner()
    assert(#browser.itemList.items == 1 and browser.itemList.items[1].item.fullType == "Fixture.New")
    assert(equalFresh("망치")[1].fullType == "Fixture.New")
    browser:onCategorySelected({name="Tool"})
    assert(Search.isEmpty(browser.searchBar:getText()) and BrowserData._cache.searchPrefixState == nil)
    local reopened = panel()
    reopened:loadCategories()
    assert(#reopened.itemList.items == 0 and reopened.detail == nil)
    reopened:selectItem(BrowserData.getItem("Fixture.New"))
    assert(reopened.detail == "Fixture.New")
    assert(reopened.categoryList.items[reopened.categoryList.selected].item.name == "Tool")
    assert(reopened.subcategoryList.items[reopened.subcategoryList.selected].item.name == "1-A")

    -- Paste navigation shares the completed query's documents and established
    -- item locations. Ambiguous names/IDs must not pick a category by row order.
    install(fixtures, {
        ["Base.Sledgehammer"]={"Combat.2-A"},
        ["Base.Sledgehammer2"]={"Combat.2-A"},
        ["Fixture.Compact"]={"Tool.1-B"},
        ["Fixture.Mango"]={"Consumable.3-A"},
        ["Fixture.IdName"]={"Combat.2-A"},
        ["Base.LemonGrass"]={"Consumable.3-A"},
        ["Base.Lemongrass"]={"Tool.1-B"},
    })
    local navigation = panel()
    navigation:loadCategories()
    navigation:onCategorySelected({name="Consumable"})
    navigation:onSubcategorySelected({name="3-A"})
    navigation.subcategorySearchBar.onTextChange = function() navigation:onSubcategorySearchChange() end
    navigation.subcategorySearchBar:setText("3-A") -- Hides the next target.
    local function pasted(query, category, subcategory)
        local expected = identities(BrowserData.searchAll(query))
        local snapshot = BrowserData._cache.searchSnapshot
        local searchCalls = BrowserData._cache.searchMetrics.searchCalls
        navigation.searchBar.internal = query -- No callback; getText is stale.
        navigation:refreshSearchInput()
        assert(navigation.currentCategory == category and navigation.currentSubcategory == subcategory,
            "paste location: " .. query)
        assert(navigation.categoryList.items[navigation.categoryList.selected].item.name == category)
        assert(navigation.subcategoryList.items[navigation.subcategoryList.selected].item.name == subcategory)
        local rows = {}
        for _, entry in ipairs(navigation.itemList.items) do rows[#rows + 1] = entry.item end
        assert(identities(rows) == expected, "navigation changed global results")
        assert(navigation.searchBar:getInternalText() == query and navigation.detail == nil)
        assert(BrowserData._cache.searchSnapshot == snapshot)
        assert(BrowserData._cache.searchMetrics.searchCalls == searchCalls + 1)
    end
    pasted("망치", "Tool", "1-A")
    assert(navigation.subcategorySearchBar:getText() == "")
    navigation:onSubcategorySearchChange() -- Late callback retains the highlight.
    assert(navigation.subcategoryList.items[navigation.subcategoryList.selected].item.name == "1-A")
    pasted("대형망치", "Tool", "1-B") -- Same category, different subcategory.
    pasted("대형 망치", "Combat", "2-A") -- Same-name distinct IDs, shared location.
    assert(#navigation.itemList.items == 3 and navigation.currentSelectedVariants == nil)
    pasted("대형  망치", "Combat", "2-A") -- Compact-name collision across locations: retain.
    pasted("망고", "Consumable", "3-A")
    pasted("레몬그라스", "Consumable", "3-A") -- Same raw name, different locations: retain.
    pasted("망", "Consumable", "3-A") -- Partial only: retain.
    pasted("없는 아이템", "Consumable", "3-A") -- No result: retain.
    pasted("  BASE.HAMMER  ", "Tool", "1-A") -- Exact ID wins navigation over an ID-like name.
    assert(navigation.itemList.items[1].item.fullType == "Fixture.IdName") -- Ranking stays name-first.
    pasted("base.lemongrass", "Tool", "1-A") -- Case-colliding IDs, different locations: retain.
    pasted("  망고  ", "Consumable", "3-A")
    assert(BrowserData.getSearchLocation("stale query") == nil)
    locale("EN")
    assert(BrowserData.getSearchLocation("  망고  ") == nil)
    locale("KO")
    navigation.itemSearchBar:setText("stale local filter")
    navigation.subcategorySearchBar:setText("3-A")
    navigation.searchBar.internal = ""
    navigation:refreshSearchInput()
    assert(navigation.currentCategory == nil and navigation.currentSubcategory == nil)
    assert(#navigation.categoryList.items > 0 and #navigation.subcategoryList.items == 0)
    assert(#navigation.itemList.items == 0 and navigation.detail == nil)
    assert(navigation.categoryList.selected == 0 and navigation.subcategoryList.selected == 0)
    assert(navigation.itemList.selected == 0 and navigation.currentSelectedVariants == nil)
    assert(navigation.itemSearchBar:getInternalText() == "" and navigation.subcategorySearchBar:getText() == "")
    assert(BrowserData._cache.searchPrefixState == nil)
    navigation:onGlobalSearchChange() -- Delayed clear callback cannot reopen old navigation.
    navigation:refreshSearchInput()
    assert(navigation.currentCategory == nil and #navigation.itemList.items == 0)
    BrowserData.resetForReload()
    assert(BrowserData.getSearchLocation("  망고  ") == nil)

    -- Empty/unusable engine collections remain retryable failures, not empty-ready.
    for _, items in ipairs({{}, {{}}}) do
        getAllItems = function() return collection(items) end
        BrowserData.resetForReload()
        local available, state = BrowserData.ensureReady()
        assert(not available and state.state == "retryable_failed" and BrowserData._cache == nil)
    end
    local emptyCache = {itemsByFullType={}, generation=1}
    assert(#Query.searchAll(nil, "망치", nil, "KO") == 0)
    assert(#Query.searchAll(emptyCache, "망치", nil, "KO") == 0)
    -- Older isolated cache callers adapt into the same document/matcher path.
    local legacy = {itemsByFullType={["Base.Hammer"]={}}, generation=1, searchKeysLocale="KO",
        searchKeysByFullType={["Base.Hammer"]={displayName="망치",folded="unused legacy key"}}}
    assert(Query.searchAll(legacy, "  망치  ", function() return "Tool", "1-A" end, "KO")[1].category == "Tool")

    StaticData.get, IrisPrimarySubcategory, Translator = originalGet, originalPrimary, originalTranslator
    currentLocale = "EN"
    Loader.init()
    getAllItems = healthyGetAllItems
    BrowserData.resetForReload()
    assert(BrowserData.ensureReady())
    print("SEARCH_CONTRACT quality=passed identity=passed transitions=passed controller=passed")
end

package.preload["Iris/UI/Tooltip/IrisTooltipSummary"] = function()
    error("Alt must not load legacy summary")
end
package.loaded["Iris/Util/IrisTranslationResolver"] = {getDetectedLangKey=function() return "EN" end}
package.preload["Iris/Data/IrisTooltipStaticData"] = function()
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

print("IRIS_BROWSER_STANDALONE_PASS state=ready normalized_getter_calls=" .. tostring(normalizedGetterCalls) ..
    " optional_load_calls=" .. tostring(optionalLoadCalls) .. " folded_cache_entries=" .. tostring(repeatedGroupCount) ..
    " get_all_items_calls=" .. tostring(readyInstrumentation.getAllItemsCallCount) ..
    " recovery_get_all_items_calls=" .. tostring(recoveryInstrumentation.getAllItemsCallCount) ..
    " prefix_reuse_count=" .. tostring(cache.searchMetrics.prefixReuseCount) ..
    " tooltip_static_lookups=" .. tostring(tooltipMetrics.staticLookups))
