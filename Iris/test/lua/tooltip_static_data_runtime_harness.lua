-- One fixture family for the T3 reader, rendering lifecycle, and Menu sources.
local root = assert(arg[1]):gsub("\\", "/")
local mode = arg[2] or "full"
package.path = root .. "/Iris/media/lua/client/?.lua;" .. package.path
-- Standard Lua provides next; PZ's Kahlua does not. Keep that engine boundary
-- in this existing fixture so desktop Lua cannot hide an unsupported dependency.
next = nil
local DATA = "Iris/Data/IrisTooltipStaticData"
local RECIPES = "Iris/Data/IrisTooltipRecipeVariants"
local READER = "Iris/Data/IrisTooltipStaticDataLookup"
local ALT = "Iris/UI/Tooltip/IrisAltTooltip"
local RESOLVER = "Iris/Util/IrisTranslationResolver"
local LOADER = "Iris/IrisTranslationLoader"
local function same(a, b)
    assert(type(a) == "table" and #a == #b, "row count")
    for i = 1, #b do assert(a[i] == b[i], "row content/order") end
end
local dataLoads = 0
package.preload[DATA] = function()
    dataLoads = dataLoads + 1
    return dofile(root .. "/Iris/media/lua/client/Iris/Data/IrisTooltipStaticData.lua")
end
local reader = require(READER)
assert(dataLoads == 0)
assert(reader.get("Base.223Clip", nil) == nil)
assert(reader.get("Base.223Clip", "FR") == nil)
assert(reader.get(nil, "en") == nil and dataLoads == 0)
local cases = {"Base.BaguetteDough", "Base.223Clip", "Base.223Box", "Base.223BulletsMold", "Base.223Bullets"}
for i, key in ipairs(cases) do assert(#assert(reader.get(key, "en")) == i - 1) end
assert(dataLoads == 1)
local payload = package.loaded[DATA]
local count, distribution = 0, {0, 0, 0, 0, 0}
for key, record in pairs(payload) do
    count = count + 1
    assert(type(key) == "string" and type(record) == "table")
    for locale in pairs(record) do assert(locale == "ko" or locale == "en") end
    for _, locale in ipairs({"ko", "en"}) do same(assert(reader.get(key, locale)), record[locale]) end
    distribution[#record.ko + 1] = distribution[#record.ko + 1] + 1
end
assert(count == 2280)
same(distribution, {367, 825, 895, 137, 56})
same(reader.get("Base.LemonGrass", "ko"), payload["Base.LemonGrass"].ko)
same(reader.get("Base.Lemongrass", "ko"), payload["Base.Lemongrass"].ko)
assert(payload["Base.LemonGrass"] ~= payload["Base.Lemongrass"])
assert(reader.get("base.223Clip", "en") == nil)
assert(reader.get(" Base.223Clip", "en") == nil)
local duplicate = reader.get("Base.223Bullets", "en")
assert(#duplicate == 4 and duplicate[3] == duplicate[4])
if mode == "smoke" then
    print("IRIS_TOOLTIP_T3_PASS mode=smoke exact_keys=2280")
    return
end

local recipeData = require(RECIPES)
local function expectedRows(key, language, index)
    local entry = recipeData[key]
    if not entry then return payload[key][language] end
    if #entry.variants == 0 then return entry.without_recipe[language] end
    return entry.variants[index or 1][language]
end
assert(recipeData["farming.Cabbage"].variants[1].id == "uc.recipe.make_jar_of_cabbage")
assert(recipeData["farming.Cabbage"].variants[1].ko[2] == "[레시피] 병에 양배추 절이기")
assert(recipeData["farming.Cabbage"].variants[1].en[2] == "[Recipe] Make Jar of Cabbage")
-- The behavior is dataset-wide, not a cabbage special case. Exercise every
-- generated choice in both locales through the real runtime lookup.
local recipeItems, recipeChoices = 0, 0
for key, entry in pairs(recipeData) do
    recipeItems=recipeItems+1
    if #entry.variants == 0 then
        local view=assert(reader.open(key, function() error("empty pool random call") end))
        same(view.ko, entry.without_recipe.ko); same(view.en, entry.without_recipe.en)
    else
        for index, expected in ipairs(entry.variants) do
            local view=assert(reader.open(key, function() return index end))
            assert(view.id == expected.id)
            same(view.ko, expected.ko); same(view.en, expected.en)
            recipeChoices=recipeChoices+1
        end
    end
end
assert(recipeItems == 349 and recipeChoices == 781)

local legacyCalls = 0
local forbidden = {
    "Iris/UI/Tooltip/IrisTooltipSummary", "Iris/UI/Detail/IrisItemDetailViewModel",
    "Iris/UI/Detail/IrisItemDetailModelAssembler", "Iris/UI/Detail/IrisItemDetailPresentation",
    "Iris/IrisAPI", "Iris/API/StaticData", "Iris/API/UseCases", "Iris/API/Tags",
    "Iris/Data/IrisRecipeIndex", "Iris/Data/IrisMoveablesIndex", "Iris/Data/IrisFixingIndex",
    "Iris/Data/IrisUseCaseDescriptions", "Iris/Data/IrisLayer3DataChunks",
    "Iris/Data/layer3_renderer", "Iris/Data/IrisClassifications",
    "Iris/Data/IrisUseCaseDescriptionsLookup", "Iris/Data/IrisLayer3DataLookup",
}
if mode ~= "menu" then
local badRecords = {
    false, "text", {[1]="one", [3]="three"}, {note="metadata"},
    {[1]="one", extra="mixed"}, {"one", 2}, {"1","2","3","4","5"},
    {""}, {" \t"}, {"\r"}, {"\n"}, {"one", "bad\nrow"}, {"\194\160"},
    {[0]="zero"}, {[1.5]="fraction"}, setmetatable({}, {__index=function() return "invented" end}),
}
for _, record in ipairs(badRecords) do
    payload["Fixture.Bad"] = {ko=record, en={"good"}}
    assert(reader.get("Fixture.Bad", "ko") == nil, "malformed record accepted")
    same(reader.get("Fixture.Bad", "en"), {"good"})
end
payload["Fixture.Bad"] = nil

-- Strict locale reads share the existing loader lifecycle; fallback API stays EN.
Translator = {getLanguage=function() return "KO" end}
package.loaded[RESOLVER], package.loaded[LOADER] = nil, nil
local resolver = require(RESOLVER)
local loader = require(LOADER)
assert(resolver.getDetectedLangKey() == "KO")
for _, language in ipairs({"EN", "FR", ""}) do
    Translator.getLanguage = function() return language end
    loader.init()
    assert(resolver.getDetectedLangKey() == (language ~= "" and language or nil))
end
Translator.getLanguage = function() return nil end
loader.init()
assert(resolver.getDetectedLangKey() == nil and resolver.getLangKey() == "EN")
Translator.getLanguage = function() error("language unavailable") end
loader.init()
assert(resolver.getDetectedLangKey() == nil and resolver.getLangKey() == "EN")
Translator = nil
loader.init()
assert(resolver.getDetectedLangKey() == nil)

for _, name in ipairs(forbidden) do
    package.loaded[name] = nil
    package.preload[name] = function() legacyCalls = legacyCalls + 1; error("legacy path: " .. name) end
end
local locale, alt, measureFailure, drawFailure = "EN", false, false, false
local randomCalls, randomResult = 0, 0
ZombRand = function(count)
    randomCalls = randomCalls+1
    return math.min(randomResult, count-1)
end
package.loaded[RESOLVER] = {getDetectedLangKey=function()
    if locale == "throw" then error("locale failure") end
    return locale
end}
UIFont = {Small="Small"}
getTextManager = function() return {
    getFontHeight=function() return 17 end,
    MeasureStringX=function(_, _, text)
        if measureFailure then error("measurement failure") end
        return #text * 6
    end,
} end
local screenWidth, screenHeight = 900, 700
getCore = function() return {
    getScreenWidth=function() return screenWidth end,
    getScreenHeight=function() return screenHeight end,
} end
isKeyDown = function(code) return alt and code == 56 end
local function tooltip()
    return {item={fullType="Base.223Clip"},height=30,width=300,x=10,y=10,drawn={},boxes=0,vanilla=0,
        getAbsoluteX=function(self) return self.x end, getAbsoluteY=function(self) return self.y end,
        setHeight=function() error("Iris must not resize vanilla") end,
        drawRect=function(self, x,y,w,h)
            if drawFailure then error("draw failure") end
            assert(self.x+x >= 0 and self.x+x+w <= screenWidth)
            assert(self.y+y >= 0 and self.y+y+h <= screenHeight)
            assert(x >= self.width or x+w <= 0 or y >= self.height or y+h <= 0, "vanilla overlap")
            self.panel = {x=x, y=y, width=w, height=h}
            self.boxes=self.boxes+1
        end,
        drawRectBorder=function() end,
        drawText=function(self, text) self.drawn[#self.drawn+1]=text end,
    }
end
local function fresh(kind)
    package.loaded[ALT], package.loaded[READER], package.loaded[DATA], package.loaded[RECIPES] = nil, nil, nil, nil
    local loads = 0
    package.preload[DATA] = function()
        loads=loads+1
        if kind == "load_failure" then error("absent payload") end
        if kind == "invalid_root" then return true end
        if kind == "malformed" then return {["Base.223Clip"]={en={"good", "bad\nrow"}}} end
        return payload
    end
    package.preload[RECIPES] = function()
        if kind == "recipe_load_failure" then error("absent recipe variants") end
        if kind == "stale_recipe" then
            return {["Base.223Clip"]={base={ko={"stale"},en={"stale"}},variants={}}}
        end
        if kind == "invalid_recipe" then
            return {["Base.223Clip"]={base=payload["Base.223Clip"],variants={
                {id="bad",ko={"1","2","3","4","5"},en={"bad"}}}}}
        end
        return recipeData
    end
    ISToolTipInv = {render=function(self) self.vanilla=self.vanilla+1 end,
        setVisible=function(self, visible) self.visible=visible end}
    local module = require(ALT)
    module.setInstrumentationEnabled(true)
    module.hookTooltip()
    local installed = ISToolTipInv.render
    module.hookTooltip()
    assert(installed == ISToolTipInv.render)
    assert(loads == 0)
    return module, function() return loads end
end
for _, kind in ipairs({"normal", "load_failure", "invalid_root", "malformed", "unknown",
                       "recipe_load_failure", "stale_recipe", "invalid_recipe"}) do
    local module, loads = fresh(kind)
    local tip = tooltip()
    if kind == "unknown" then tip.item.fullType="Unknown.Item" end
    alt=false
    ISToolTipInv.render(tip)
    assert(tip.vanilla == 1 and tip.boxes == 0 and tip.height == 30 and loads() == 0)
    local metrics=module.getDisplayLineCacheMetrics()
    assert(metrics.fullTypeResolutions == 0 and metrics.localeResolutions == 0 and metrics.staticLookups == 0)
    alt=true
    for _=1,3 do ISToolTipInv.render(tip) end
    assert(tip.vanilla == 4 and loads() == 1)
    if kind == "normal" then
        assert(tip.boxes == 3 and tip.height == 30 and tip.width == 300)
        assert(tip.panel.x == tip.width+4 and tip.panel.y == 0)
        local height, boxes = tip.height, tip.boxes
        module.addIrisOverlay(tip)
        assert(tip.boxes == boxes and tip.height == height)
        alt=false; ISToolTipInv.render(tip)
        assert(tip.height == 30 and tip.boxes == boxes)
        alt=true
        for _, key in ipairs(cases) do
            tip.item.fullType=key; tip.drawn={}; tip.boxes=0
            ISToolTipInv.render(tip)
            assert(table.concat(tip.drawn) == table.concat(expectedRows(key, "en")))
            assert(tip.boxes == (#expectedRows(key, "en") > 0 and 1 or 0))
        end
        tip.item.fullType="Base.223Clip"
        for _, lang in ipairs({"KO", "EN", "FR", "throw"}) do
            locale=lang; tip.drawn={}; tip.boxes=0; ISToolTipInv.render(tip)
            if lang == "EN" or lang == "KO" then
                assert(table.concat(tip.drawn) == table.concat(payload[tip.item.fullType][lang:lower()]))
            else assert(tip.boxes == 0 and tip.height == 30) end
        end
        locale=nil; tip.boxes=0; ISToolTipInv.render(tip); assert(tip.boxes == 0 and tip.height == 30)
        locale="EN"
        tip.item.fullType="Unknown.Item"; tip.boxes=0; ISToolTipInv.render(tip)
        assert(tip.boxes == 0 and tip.height == 30)
        tip.item=nil; ISToolTipInv.render(tip); assert(tip.height == 30)
        tip.item={fullType="Base.223Bullets"}; tip.x=820; tip.y=640; tip.boxes=0
        ISToolTipInv.render(tip); assert(tip.boxes == 1 and tip.panel.x+tip.panel.width == -4)
        -- Same panel family covers narrow vanilla, screen edges, fallback and reuse.
        payload["Fixture.Layout"] = {ko={string.rep("설명 ", 20)}, en={string.rep("long text ", 15)}}
        for _, placement in ipairs({
            {x=10, y=10, width=156, sw=900, sh=700, side="right", top=true},
            {x=700, y=10, width=156, sw=900, sh=700, side="left", top=true},
            {x=10, y=670, width=156, sw=900, sh=700, side="right"},
            {x=10, y=10, width=300, sw=640, sh=700, side="right", top=true, panelWidth=326},
            {x=0, y=10, width=156, sw=300, sh=700, side="below"},
            {x=0, y=650, width=156, sw=300, sh=700, side="above"},
            {x=0, y=0, width=156, sw=300, sh=30, side="hidden"},
        }) do
            for _, language in ipairs({"KO", "EN"}) do
                locale = language
                screenWidth, screenHeight = placement.sw, placement.sh
                tip.item.fullType = "Fixture.Layout"
                tip.x, tip.y, tip.width = placement.x, placement.y, placement.width
                tip.drawn, tip.boxes, tip.panel = {}, 0, nil
                ISToolTipInv.render(tip)
                assert(tip.height == 30 and tip.width == placement.width)
                if placement.side == "hidden" then
                    assert(tip.boxes == 0 and #tip.drawn == 0)
                else
                    assert(tip.boxes == 1)
                    same({table.concat(tip.drawn)}, payload["Fixture.Layout"][language:lower()])
                    local panel = tip.panel
                    if placement.side == "right" then assert(panel.x == tip.width+4)
                    elseif placement.side == "left" then assert(panel.x+panel.width == -4)
                    elseif placement.side == "below" then assert(panel.y == tip.height+4)
                    else assert(panel.y+panel.height == -4) end
                    if placement.top then assert(panel.y == 0) end
                    if placement.panelWidth then assert(panel.width == placement.panelWidth) end
                end
                alt=false; ISToolTipInv.render(tip)
                assert(tip.height == 30 and tip.width == placement.width)
                alt=true
            end
        end
        payload["Fixture.Layout"] = nil
        locale, screenWidth, screenHeight = "EN", 900, 700
        tip.item.fullType, tip.x, tip.width = "Base.223Bullets", 10, 300
        tip.y, tip.drawn = 10, {}
        randomCalls, randomResult = 0, 0
        ISToolTipInv.render(tip)
        local firstChoice = tip._irisOpening.view.id
        same({table.concat(tip.drawn)}, {table.concat(expectedRows("Base.223Bullets", "en", 1))})
        assert(randomCalls == 1)
        randomResult=1; tip.drawn={}; ISToolTipInv.render(tip)
        assert(tip._irisOpening.view.id == firstChoice and randomCalls == 1)
        locale="KO"; tip.drawn={}; ISToolTipInv.render(tip)
        same({table.concat(tip.drawn)}, {table.concat(expectedRows("Base.223Bullets", "ko", 1))})
        assert(randomCalls == 1, "locale must not reselect a recipe")
        ISToolTipInv.setVisible(tip, false)
        assert(tip._irisOpening == nil)
        ISToolTipInv.setVisible(tip, true)
        tip.drawn={}; ISToolTipInv.render(tip)
        assert(randomCalls == 2 and tip._irisOpening.view.id ~= firstChoice)
        alt=false; ISToolTipInv.render(tip); assert(tip._irisOpening == nil)
        alt=true; randomResult=0; ISToolTipInv.render(tip)
        assert(randomCalls == 3 and tip._irisOpening.view.id == firstChoice)
        tip.item={fullType="Base.223Bullets"}; ISToolTipInv.render(tip)
        assert(randomCalls == 4, "different item instance starts a new opening")
        ISContextMenu={instance={visibleCheck=true}}
        tip.boxes=0; ISToolTipInv.render(tip)
        assert(tip.boxes == 0 and tip._irisOpening == nil)
        ISContextMenu=nil
        -- No valid recipe names is an explicit producer disposition, not a
        -- fallback to the old generic sentence.
        payload["Fixture.NoRecipe"]={ko={"코어", "옛 문장"},en={"core", "old generic"}}
        recipeData["Fixture.NoRecipe"]={base=payload["Fixture.NoRecipe"],variants={},
            without_recipe={ko={"코어"},en={"core"}}}
        tip.item.fullType="Fixture.NoRecipe"; tip.drawn={}; ISToolTipInv.render(tip)
        same(tip.drawn, {"코어"})
        payload["Fixture.NoRecipe"],recipeData["Fixture.NoRecipe"]=nil,nil
        tip.item.fullType="Base.223Bullets"; locale="EN"
        tip.y=10; measureFailure=true; tip.boxes=0; ISToolTipInv.render(tip)
        assert(tip.boxes == 0 and tip.height == 30)
        measureFailure=false; drawFailure=true; ISToolTipInv.render(tip); assert(tip.height == 30)
        drawFailure=false
    else assert(tip.boxes == 0 and tip.height == 30) end
    assert(legacyCalls == 0)
end
-- Vanilla exceptions must not be swallowed by the Iris boundary.
package.loaded[ALT]=nil
ISToolTipInv={render=function() error("vanilla error") end}
require(ALT).hookTooltip()
local vanillaOk, vanillaError=pcall(ISToolTipInv.render, tooltip())
assert(not vanillaOk and tostring(vanillaError):find("vanilla error",1,true))
end

-- Menu relation uses actual producer data and consumer functions, without Tooltip IDs.
if mode == "full" or mode == "menu" then
    for _, name in ipairs(forbidden) do package.loaded[name]=nil; package.preload[name]=nil end
    package.loaded[RESOLVER]=nil; package.loaded[LOADER]=nil
    Translator={getLanguage=function() return "EN" end}
    local actualRequire=require
    local enRecords={}
    local enLoadFailure={}
    require=function(name)
        local ok,result=pcall(actualRequire,name)
        if not ok then
            if name:match("^Iris/Data/Layer3English/") then enLoadFailure[name]=true end
            error(result)
        end
        if name:match("^Iris/Data/Layer3English/Chunk%d+$") then
            return setmetatable({}, {__index=function(_,key)
                enRecords[key]=name
                return result[key]
            end})
        end
        return result
    end
    local ViewModel=require("Iris/UI/Detail/IrisItemDetailViewModel")
    local Collector=require("Iris/UI/Browser/IrisBrowserInteractionCollector")
    local koLookup=require("Iris/Data/IrisLayer3DataLookup")
    local enLookup=require("Iris/Data/IrisLayer3EnglishLookup")
    local koGet, enGet=koLookup.get, enLookup.get
    local koIndex=require("Iris/Data/IrisLayer3DataChunkIndex")
    local enIndex=require("Iris/Data/Layer3English/Index")
    local koObserved, enObserved={}, {}
    local koReasons, enCalled={}, {}
    koLookup.get=function(key)
        local entry,reason=koGet(key)
        if entry then koObserved[key]=entry end
        koReasons[key]=reason
        return entry,reason
    end
    enLookup.get=function(key)
        enCalled[key]=true
        local value=enGet(key)
        if value then enObserved[key]=value end
        return value
    end
    local function hex(value)
        return (value:gsub(".",function(byte) return string.format("%02x",string.byte(byte)) end))
    end
    local function activeRecord(index,key)
        local selected=nil
        for _,record in ipairs(index.chunks) do
            if key >= record.first and key <= record.last then
                assert(selected == nil,"overlapping active Menu index ranges")
                selected=record
            end
        end
        return selected
    end
    local koCount,enCount,l4Count=0,0,0
    local kinds={recipe=false,rightclick=false,both=false}
    for key in pairs(payload) do
        local item={fullType=key,getFullType=function() return key end}
        for _, lang in ipairs({"KO","EN"}) do
            koObserved[key],enObserved[key],enRecords[key]=nil,nil,nil
            koReasons[key],enCalled[key]=nil,nil
            Translator.getLanguage=function() return lang end
            require(LOADER).init()
            local vm=ViewModel.fromItem(item)
            local projection=Collector.collect(vm.interactionState, lang, function(_,fallback) return fallback end)
            if lang == "KO" and vm.layer3.available then
                assert(koObserved[key] and vm.layer3.raw == koObserved[key].text_ko)
                local record=assert(activeRecord(koIndex,key),"missing active KO index entry")
                assert(actualRequire(record.module)[key] == koObserved[key])
                print("MENU_L3\tKO\t"..key.."\t"..record.module.."\t"..hex(vm.layer3.raw))
                koCount=koCount+1
            end
            if lang == "EN" and vm.layer3.available then
                assert(enObserved[key] and enRecords[key] and vm.layer3.raw == enObserved[key])
                local record=assert(activeRecord(enIndex,key),"missing active EN index entry")
                assert(record.module == enRecords[key],"inactive EN chunk consumed")
                print("MENU_L3\tEN\t"..key.."\t"..enRecords[key].."\t"..hex(vm.layer3.raw))
                enCount=enCount+1
            end
            if not vm.layer3.available then
                local entry=koObserved[key]
                local reason=koReasons[key]
                if reason == nil and entry then
                    if entry.publish_state == "internal_only" then reason="internal_only"
                    elseif not entry.text_ko or entry.text_ko == "" then reason="no_public_body" end
                end
                if reason == nil and lang == "EN" then
                    local record=activeRecord(enIndex,key)
                    if record and enLoadFailure[record.module] then reason="target_module_load_failure"
                    elseif not enCalled[key] then reason="lookup_not_called"
                    else reason="lookup_miss" end
                end
                print("MENU_L3_ABSENT\t"..lang.."\t"..key.."\t"..(reason or "consumer_unavailable"))
            end
            if projection.status == "available" then
                if lang == "EN" then
                    l4Count=l4Count+1
                    if projection.recipeCount>0 and projection.rightclickCount>0 then kinds.both=true
                    elseif projection.recipeCount>0 then kinds.recipe=true else kinds.rightclick=true end
                end
                for _, row in ipairs(projection.rows) do
                    print("MENU_L4\t"..lang.."\t"..key.."\t"..row.identity.."\t"..row.source)
                end
            end
        end
    end
    koLookup.get, enLookup.get=koGet,enGet
    require=actualRequire
    assert(kinds.recipe and kinds.rightclick and kinds.both, "source kind coverage")
    print("MENU_SOURCE_COUNTS ko="..koCount.." en="..enCount.." l4="..l4Count)
    -- Optional predecessor data is read in this same final observation run.
    -- The Python caller binds every file to the saved initial subject first.
    if arg[3] then
        local baselineRoot=arg[3]:gsub("\\", "/")
        local baselineIndex=dofile(baselineRoot.."/Index.lua")
        local seen={}
        for _,record in ipairs(baselineIndex.chunks) do
            local name=assert(record.module:match("^Iris/Data/Layer3English/(Chunk%d+)$"))
            for key,text in pairs(dofile(baselineRoot.."/"..name..".lua")) do
                assert(not seen[key],"duplicate baseline EN record")
                assert(key >= record.first and key <= record.last)
                seen[key]=true
                print("MENU_BASELINE_EN\t"..key.."\t"..hex(text))
            end
        end
    end
end
print("IRIS_TOOLTIP_T3_PASS mode="..mode.." exact_keys=2280 legacy_calls="..legacyCalls)
