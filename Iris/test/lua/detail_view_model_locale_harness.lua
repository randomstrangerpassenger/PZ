local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

if arg[2] == "expanded" then
    local expected = dofile(assert(arg[3]))
    local locale = "KO"
    next = nil -- PZ/Kahlua boundary, not desktop Lua's extra API.
    package.loaded["Iris/Util/IrisTranslationResolver"] = {
        getLangKey=function() return locale end,
        get=function(_, fallback) return fallback end,
    }
    package.loaded["Iris/IrisAPI"] = {
        Tags={getTagsForItem=function() return { ["Material"]=true } end},
        UseCases={_getDescriptionState=function() return {status="verified_empty", lines={}, reason="fixture"} end},
    }
    local lookup = require("Iris/Data/IrisLayer3DataLookup")
    local renderer = require("Iris/Data/layer3_renderer")
    local Model = require("Iris/UI/Detail/IrisItemDetailViewModel")
    local Sections = require("Iris/UI/Wiki/IrisWikiSections")
    local current = require("Iris/Data/IrisLayer3DataCurrent")
    assert(current.product_id == expected.product_id and lookup.getDiagnostics().productId == expected.product_id)
    local function item(key)
        return {getFullType=function() return key end, getDisplayName=function() return key end,
                getActualWeight=function() return 1 end, getType=function() return "Normal" end}
    end
    local count = 0
    for key, row in pairs(expected.menu) do
        count = count + 1
        for _, lang in ipairs({"ko", "en"}) do
            locale = lang:upper()
            local value = assert(lookup.getLocale(key, lang))
            local source = row[lang]
            assert(value.state == source.state and value.text == source.text and #value.units == #source.units)
            local model = Model.fromItem(item(key))
            assert(model.layer3.productId == expected.product_id and model.layer3.state == source.state)
            assert(model.layer3.available == (source.state == "present") and model.weight == 1)
            local units = Sections.getLayer3Units(model)
            assert(#units == #source.units)
            for i, unit in ipairs(source.units) do
                assert(units[i] == unit.text and value.units[i].first_segment == unit.first_segment and
                    value.units[i].last_segment == unit.last_segment)
                assert(not pcall(function() model.layer3.units[i].text = "changed" end))
            end
            assert(model.interactionState.status == "verified_empty")
        end
    end
    assert(count == 2105)
    local facade = require("Iris/Data/IrisLayer3DataChunks")
    count = 0
    for key, entry in pairs(facade) do
        count = count + 1
        assert(entry == lookup.get(key) and entry.product_id == expected.product_id)
    end
    assert(count == 2105 and IrisLayer3Data == facade)
    assert(lookup.getLocale("Base.Plank", "fr") == nil and lookup.get("base.Plank") == nil)
    assert(renderer.getDisplay("Base.Plank", {locale="FR"}).state == "fault")
    assert(renderer.getText("Base.Plank", {locale="FR"}) == nil)
    assert(renderer.getRawText("Base.Plank", {locale="FR"}) == nil)
    -- A public fuel overview may now precede the compound construction unit.
    -- Exact source units and their ranges are compared for every item above.
    assert(#expected.menu["Base.Plank"].ko.units > 1 and #expected.menu["Base.Lipstick"].ko.units == 2)

    -- Engine widgets/fonts are the only layout stubs. Both actual consumers
    -- create their real labels and calculate scroll bounds from wrapped text.
    UIFont = {Small="Small", Medium="Medium"}
    getCore = function() return {getScreenWidth=function() return 800 end, getScreenHeight=function() return 600 end} end
    getTextManager = function() return {MeasureStringX=function(_, _, text) return #text * 6 end} end
    local Widget = {}
    Widget.__index = Widget
    function Widget:new(x,y,w,h) return setmetatable({x=x,y=y,width=w,height=h,children={}}, self) end
    function Widget:addChild(child) self.children[#self.children+1]=child end
    function Widget:removeChild(child) for i,v in ipairs(self.children) do if v==child then table.remove(self.children,i); return end end end
    function Widget:getChildren() return self.children end
    function Widget:getY() return self.y end
    function Widget:setY(y) self.y=y end
    function Widget:getX() return self.x end
    function Widget:getAbsoluteX() return self.x end
    function Widget:getAbsoluteY() return self.y end
    function Widget:setX(x) self.x=x end
    function Widget:setWidth(w) self.width=w end
    function Widget:setVisible(v) self.visible=v end
    function Widget:getIsVisible() return self.visible end
    function Widget:isVisible() return self.visible end
    function Widget:setScrollHeight(h) self.scrollHeight=h end
    for _, name in ipairs({"initialise","instantiate","setAnchorLeft","setAnchorTop","setAnchorRight","setAnchorBottom",
                          "setScrollChildren","addScrollBars","addToUIManager","removeFromUIManager"}) do Widget[name]=function() end end
    ISPanel=Widget
    ISLabel={new=function(_,x,y,h,text) local w=Widget:new(x,y,1,h); w.text=text; return w end}
    ISButton={new=function(_,x,y,w,h,text) local b=Widget:new(x,y,w,h); b.text=text; return b end}
    ISTextEntryBox={new=function(_,text,x,y,w,h) local b=Widget:new(x,y,w,h); b.text=text; return b end}
    function Widget:setText(text) self.text=text end
    function Widget:getInternalText() return self.text end
    for _, name in ipairs({"ISButton","ISLabel","ISTextEntryBox"}) do package.loaded["ISUI/"..name]=true end
    local Wiki = require("Iris/UI/Wiki/IrisWikiPanel")
    local Browser = setmetatable({}, {__index=Widget})
    Browser.__index=Browser
    require("Iris/UI/Browser/IrisBrowserDetail").install(Browser, {
        getBrowserData=function() return {getItem=function(key) return item(key) end, getBuildState=function() return {generation=1} end} end,
        getWikiSections=function() return Sections end,
        safeRequire=function(name) local ok,value=pcall(require,name); return ok,value end,
        tr=function(_,fallback) return fallback end,
    })
    local browser=Browser:new(0,0,220,180)
    browser.detailPanel=Widget:new(0,0,220,180)
    browser.detailScrollY=0; browser.recipeExpandedByFullType={}
    local function labels(panel)
        local texts={}
        for _, child in ipairs(panel.children) do if child.text then texts[#texts+1]=child.text end end
        return table.concat(texts," "):gsub("%s", "")
    end
    for _, key in ipairs(expected.samples) do
        for _, lang in ipairs({"KO","EN"}) do
            locale=lang
            browser:showDetail(key, true)
            local wiki=Wiki.createPanel(item(key))
            local content=wiki.children[#wiki.children]
            local source=expected.menu[key][lang:lower()]
            for _, panel in ipairs({browser.detailPanel, content}) do
                local bullets = 0
                for _, child in ipairs(panel.children) do
                    if child.text == "•" then bullets = bullets + 1 end
                end
                assert(bullets == #source.units, "One bullet per producer unit, not per wrapped line")
            end
            for _, unit in ipairs(source.units) do
                local compact=unit.text:gsub("%s", "")
                assert(labels(browser.detailPanel):find(compact,1,true), "Browser unit inaccessible")
                assert(labels(content):find(compact,1,true), "Wiki unit inaccessible")
            end
            for _, child in ipairs(content.children) do assert(child.y+child.height <= content.scrollHeight) end
            for _, child in ipairs(browser.detailPanel.children) do
                assert((browser.detailChildBaseY[child] or child.y)+child.height <= browser.detailContentHeight)
            end
            browser:onDetailMouseWheel(100000)
            assert(browser.detailScrollY == math.max(0,browser.detailContentHeight-browser.detailPanel.height))
            assert(browser.currentDetailModel.fullType==key and browser.currentDetailModel.locale==lang)
            Wiki.open(item(key)); Wiki.open(item(key)); assert(Wiki._panel.detailModel.locale==lang)
        end
    end
    -- Actual payload faults stay distinct from normal absent, including a
    -- stale global. Each injected mutation is restored within this process.
    local function reject(mutator, restore)
        mutator()
        package.loaded["Iris/Data/IrisLayer3DataLookup"]=nil
        package.loaded["Iris/Data/layer3_renderer"]=nil
        IrisLayer3Data={["Base.Plank"]={text_ko="predecessor"}}
        local bad=require("Iris/Data/layer3_renderer")
        assert(bad.getText("Base.Plank")==nil and bad.getDisplay("Base.Plank").state=="fault")
        restore()
    end
    local index=require(current.index_module)
    local id=index.product_id
    reject(function() index.product_id="wrong" end,function() index.product_id=id end)
    local schema=index.schema_version
    reject(function() index.schema_version="wrong" end,function() index.schema_version=schema end)
    local entry=lookup.get("Base.Plank")
    local saved=entry.locales.en
    reject(function() entry.locales.en=nil end,function() entry.locales.en=saved end)
    local first=entry.locales.ko.units[1]
    local last=first.last_segment
    reject(function() first.last_segment=0 end,function() first.last_segment=last end)
    local descriptor=require("Iris/Data/IrisLayer3ProductCurrent").descriptor_module
    local desc=require(descriptor)
    local descId=desc.product_id
    reject(function() desc.product_id="wrong"; package.loaded["Iris/Data/IrisLayer3DataCurrent"]=nil end,
           function() desc.product_id=descId; package.loaded["Iris/Data/IrisLayer3DataCurrent"]=current end)
    reject(function() package.loaded["Iris/Data/IrisLayer3DataCurrent"]={schema_version="iris_layer3_generation_pointer_v1"} end,
           function() package.loaded["Iris/Data/IrisLayer3DataCurrent"]=current end)
    print("IRIS_EXPANDED_MENU_PASS product="..expected.product_id.." states=4210 consumers=Browser,Wiki font=stub")
    return
end

local locale = "EN"
local interactionLookupCount = 0
package.preload["Iris/Util/IrisTranslationResolver"] = function()
    return {
        getLangKey=function() return locale end,
        get=function(key, fallback) return locale .. ":" .. (fallback or key) end,
    }
end
package.preload["Iris/IrisAPI"] = function()
    return {
        Tags={getTagsForItem=function() return { ["Consumable.3-A"]=true } end},
        Index={
            getRecipeConnectionsForItem=function() return {} end,
            getMoveablesInfoForItem=function() return nil end,
            getFixingInfoForItem=function() return nil end,
        },
        UseCases={
            _getDescriptionState=function()
                interactionLookupCount = interactionLookupCount + 1
                return {
                    status="verified_empty", reason="lookup_miss", fallback_used=false,
                    entry=nil, lines={}, exclusion_lines={}, debug_lines={},
                }
            end,
            getUseCaseLines=function() error("ViewModel must consume the status-bearing lookup") end,
            getCapabilities=function() return {} end,
        },
    }
end
package.preload["Iris/Data/layer3_renderer"] = function()
    return {
        getPublishState=function() return "published" end,
        getText=function(_, options)
            if options and options.locale == "EN" then return "English Layer 3 description" end
            return "한국어 3계층 설명"
        end,
    }
end

local item = {}
function item:getFullType() return "Base.LocaleFood" end
function item:getFullName() return "Base.LocaleFood" end
function item:getDisplayName() return "Locale Food" end
function item:getModule() return "Base" end
function item:getType() return "Food" end
function item:getActualWeight() return 0.2 end
function item:getHungerChange() return -16 end
function item:getThirstChange() return -7 end
function item:getStressChange() return 0 end
function item:getBoredomChange() return 0 end
function item:getCalories() return 10 end

local ViewModel = require("Iris/UI/Detail/IrisItemDetailViewModel")
local Presentation = require("Iris/UI/Detail/IrisItemDetailPresentation")
local Sections = require("Iris/UI/Wiki/IrisWikiSections")

locale = "EN"
local english = ViewModel.fromItem(item)
local englishCore = Sections.renderCoreInfoSection(english)
local browserSemantic = Presentation.semanticSnapshot(english)
local wikiSemantic = Sections.getSemanticSnapshot(english)
locale = "KO"
local korean = ViewModel.fromItem(item)
local koreanCore = Sections.renderCoreInfoSection(korean)

assert(english.locale == "EN" and korean.locale == "KO")
assert(english.fullType == korean.fullType and english.weight == korean.weight)
assert(english.food.hunger == korean.food.hunger and english.food.thirst == korean.food.thirst)
assert(english.availability.food == korean.availability.food)
assert(english.availability.layer3 == korean.availability.layer3)
assert(english.layer3.raw == "English Layer 3 description")
assert(korean.layer3.raw == "한국어 3계층 설명")
assert(english.layer3.display ~= nil)
assert(korean.layer3.display ~= nil)
assert(english.interactionState.status == "verified_empty")
assert(english.useCases.status == english.interactionState.status)
assert(english.useCases.reason == english.interactionState.reason)
assert(interactionLookupCount == 2)
assert(englishCore ~= koreanCore)
assert(Sections.renderFoodSection(english):find("%-1600") ~= nil)
assert(#browserSemantic == #wikiSemantic)
for index, row in ipairs(browserSemantic) do
    local wikiRow = wikiSemantic[index]
    assert(row.id == wikiRow.id and row.value == wikiRow.value and
        row.unit == wikiRow.unit and row.visible == wikiRow.visible)
end
assert(#Presentation.tooltipFacts(english, 99) <= 4)
assert(not pcall(function() english.fullType = "Base.Mutated" end))
assert(not pcall(function() english.food.hunger = 0 end))
assert(not pcall(function() english.tags[1] = "Mutated" end))

local function book(skill, level, count)
    local result = {}
    function result:getFullType() return "Base.BookCarpentry1" end
    function result:getType() return "Literature" end
    function result:getSkillTrained() return skill end
    function result:getLvlSkillTrained() return level end
    function result:getNumLevelsTrained() return count end
    return result
end

for _, lang in ipairs({ "EN", "KO" }) do
    locale = lang
    local text = Sections.renderLiteratureSection(ViewModel.fromItem(book("Carpentry", 1, 2)))
    assert(text:find(lang .. ":Skill_Carpentry", 1, true))
    assert(text:find(lang .. ":TrainingLevels: 1–2", 1, true))
    assert(text:find(lang .. ":ReadingLevels: 0–1", 1, true))
    assert(text:find(lang .. ":ReadingLiteracyCondition", 1, true))

    -- A known skill with an unavailable bound must not acquire a made-up range
    -- or the range-dependent reading conditions. Magazines are not skill books.
    local partial = Sections.renderLiteratureSection(ViewModel.fromItem(book("Carpentry", 1, nil)))
    assert(partial:find("Skill_Carpentry", 1, true))
    assert(not partial:find("TrainingLevels", 1, true))
    assert(not partial:find("ReadingLevels", 1, true))
    assert(Sections.renderLiteratureSection(ViewModel.fromItem(book(nil, 1, 2))) == nil)
    assert(Sections.renderLiteratureSection(ViewModel.fromItem(book("UnknownSkill", 1, 2))) == nil)
    assert(Sections.renderLiteratureSection(ViewModel.fromItem(book("Blacksmith", 1, 2))) == nil)
end

local englishLookup = require("Iris/Data/IrisLayer3EnglishLookup")
local hammerText = englishLookup.get("Base.HammerStone")
assert(hammerText and hammerText:find("construction", 1, true))
for index = 1, #hammerText do assert(string.byte(hammerText, index) < 128) end
local TemplatesKo = require("Iris/Logic/IrisDesc/Templates")
local TemplatesEn = require("Iris/Logic/IrisDesc/TemplatesEn")
assert(TemplatesKo.getTemplate("Combat.2-C").header ~= TemplatesEn.getTemplate("Combat.2-C").header)
assert(TemplatesEn.getTemplate("Combat.2-C").header == "Combat - Short Blunt")

print("IRIS_DETAIL_LOCALE_PASS localized_layer2=true localized_layer3=true availability_equal=true labels_differ=true nested_readonly=true interaction_lookup_once_per_build=true")
