-- One fixture family for the T3 reader, rendering lifecycle, and Menu sources.
local root = assert(arg[1]):gsub("\\", "/")
local mode = arg[2] or "full"
package.path = root .. "/Iris/media/lua/client/?.lua;" .. package.path
local DATA = "Iris/Data/IrisTooltipT2Data"
local READER = "Iris/Data/IrisTooltipT2Lookup"
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
    return dofile(root .. "/Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua")
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
getCore = function() return {getScreenWidth=function() return 900 end, getScreenHeight=function() return 700 end} end
isKeyDown = function(code) return alt and code == 56 end
local function tooltip()
    return {item={fullType="Base.223Clip"},height=30,width=300,x=10,y=10,drawn={},boxes=0,vanilla=0,
        getAbsoluteX=function(self) return self.x end, getAbsoluteY=function(self) return self.y end,
        setHeight=function(self, h) self.height=h end,
        drawRect=function(self, x,y,w,h)
            if drawFailure then error("draw failure") end
            assert(self.x+x >= 0 and self.x+x+w <= 900)
            assert(self.y+y >= 0 and self.y+y+h <= 700)
            assert(y >= 30 or y+h <= 0, "vanilla overlap")
            self.boxes=self.boxes+1
        end,
        drawRectBorder=function() end,
        drawText=function(self, text) self.drawn[#self.drawn+1]=text end,
    }
end
local function fresh(kind)
    package.loaded[ALT], package.loaded[READER], package.loaded[DATA] = nil, nil, nil
    local loads = 0
    package.preload[DATA] = function()
        loads=loads+1
        if kind == "load_failure" then error("absent payload") end
        if kind == "invalid_root" then return true end
        if kind == "malformed" then return {["Base.223Clip"]={en={"good", "bad\nrow"}}} end
        return payload
    end
    ISToolTipInv = {render=function(self) self.vanilla=self.vanilla+1 end}
    local module = require(ALT)
    module.setInstrumentationEnabled(true)
    module.hookTooltip()
    local installed = ISToolTipInv.render
    module.hookTooltip()
    assert(installed == ISToolTipInv.render)
    assert(loads == 0)
    return module, function() return loads end
end
for _, kind in ipairs({"normal", "load_failure", "invalid_root", "malformed", "unknown"}) do
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
        assert(tip.boxes == 3 and tip.height > 30)
        local height, boxes = tip.height, tip.boxes
        module.addIrisOverlay(tip)
        assert(tip.boxes == boxes and tip.height == height)
        alt=false; ISToolTipInv.render(tip)
        assert(tip.height == 30 and tip.boxes == boxes)
        alt=true
        for _, key in ipairs(cases) do
            tip.item.fullType=key; tip.drawn={}; tip.boxes=0
            ISToolTipInv.render(tip)
            assert(table.concat(tip.drawn) == table.concat(payload[key].en))
            assert(tip.boxes == (#payload[key].en > 0 and 1 or 0))
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
        ISToolTipInv.render(tip); assert(tip.boxes == 1)
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
