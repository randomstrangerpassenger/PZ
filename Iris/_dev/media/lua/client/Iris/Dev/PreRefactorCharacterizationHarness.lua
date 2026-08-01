local Harness = {}

local function isArray(value)
    if type(value) ~= "table" then return false end
    local count, maximum = 0, 0
    for key, _ in pairs(value) do
        if type(key) ~= "number" or key < 1 or key % 1 ~= 0 then return false end
        count = count + 1
        if key > maximum then maximum = key end
    end
    return count == maximum
end

local function escape(value)
    return tostring(value):gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("\n", "\\n"):gsub("\r", "\\r"):gsub("\t", "\\t")
end

local function encode(value)
    local kind = type(value)
    if value == nil then return "null" end
    if kind == "boolean" or kind == "number" then return tostring(value) end
    if kind == "string" then return '"' .. escape(value) .. '"' end
    if kind ~= "table" then return '"' .. escape(value) .. '"' end
    local parts = {}
    if isArray(value) then
        for i = 1, #value do parts[#parts + 1] = encode(value[i]) end
        return "[" .. table.concat(parts, ",") .. "]"
    end
    local keys = {}
    for key, _ in pairs(value) do keys[#keys + 1] = tostring(key) end
    table.sort(keys)
    for _, key in ipairs(keys) do parts[#parts + 1] = encode(key) .. ":" .. encode(value[key]) end
    return "{" .. table.concat(parts, ",") .. "}"
end

local failures = 0
local rows = 0
local function emit(caseId, axis, fixtureId, ownerChange, passed, expected, observed, dialectSensitive, reasons, stubs)
    rows = rows + 1
    if not passed then failures = failures + 1 end
    print("IRIS_CORE_ROW\t" .. encode({
        case_id=caseId, axis=axis, fixture_id=fixtureId, owner_change=ownerChange,
        status=passed and "pass" or "fail", expected=expected, observed=observed,
        dialect_sensitive=dialectSensitive == true, dialect_reasons=reasons or {}, stubbed_dependencies=stubs or {},
    }))
end

local function arrayCopy(values)
    local result = {}
    for _, value in ipairs(values or {}) do result[#result + 1] = value end
    return result
end

local function safeCall(target, method)
    local ok, value = pcall(function() return target[method](target) end)
    if ok then return value end
    return nil
end

local function collectLuaChildren(panel)
    local result = {}
    for _, child in ipairs((panel and panel.children) or {}) do result[#result + 1] = child end
    if #result == 0 then
        for key, child in pairs((panel and panel.children) or {}) do
            if type(key) == "number" and child then result[#result + 1] = child end
        end
    end
    if #result == 0 and panel and panel.getChildren then
        local ok, children = pcall(function() return panel:getChildren() end)
        if ok and children then
            for _, child in ipairs(children) do result[#result + 1] = child end
            if #result == 0 then
                for key, child in pairs(children) do
                    if type(key) == "number" and child then result[#result + 1] = child end
                end
            end
        end
    end
    table.sort(result, function(a, b) return (a.ID or 0) < (b.ID or 0) end)
    return result
end

function Harness.runAll()
    local Description = require("Iris/API/Description")
    for _, fullType in ipairs({"Base.Hammer", "Base.Pan", "Base.WhiskeyFull"}) do
        local okBlocks, blocks = pcall(Description.getDescriptionBlocks, fullType, nil)
        local okText, text = pcall(Description.getDescription, fullType, nil)
        local joined = okBlocks and table.concat(blocks, "\n\n") or ""
        emit("description." .. fullType:lower():gsub("[^a-z0-9]+", "_"), "description", fullType, 3,
            okBlocks and okText and text == joined and #blocks > 0,
            {relation="getDescription joins getDescriptionBlocks",nonempty=true},
            {block_count=okBlocks and #blocks or -1,joined_equal=okText and text == joined,text=okText and text or "error"},
            true,{"Kahlua_string_bytes","runtime_generator"},{})
    end
    local nilBlocks = Description.getDescriptionBlocks(nil, nil)
    emit("description.nil_fallback", "description", "nil_input", 3,
        #nilBlocks == 0 and Description.getDescription(nil, nil) == "" and Description.getDescriptionForItem(nil, nil) == "",
        {blocks=0,text="",item_text=""},{blocks=#nilBlocks,text=Description.getDescription(nil,nil),item_text=Description.getDescriptionForItem(nil,nil)},false,{},{})

    local BrowserData = require("Iris/UI/Browser/IrisBrowserData")
    local initialBuilt = BrowserData._built == true
    local buildAgain = BrowserData.build()
    local search = BrowserData.searchAll("hammer")
    emit("browser_build.pz_lifecycle", "browser_build", "startup_build_and_skip", 4,
        initialBuilt and buildAgain == true and BrowserData._built == true and #search > 0,
        {startup_built=true,second_build=true,search_nonempty=true},
        {startup_built=initialBuilt,second_build=buildAgain,built=BrowserData._built,search_count=#search},false,{}, {})

    local BrowserClass = {}
    require("Iris/UI/Browser/IrisBrowserListController").install(BrowserClass, {debug=function() end,logError=function() end,ensureDeps=function() end,getBrowserData=function() return BrowserData end})
    local function list(payload, selected)
        local value = {items={},selected=selected or 0}
        if payload then value.items[1] = {item=payload} end
        function value:clear() self.items = {} end
        return value
    end
    local browserStub = setmetatable({categoryList=list({name="selected"},1),subcategoryList=list(nil,0),itemList=list(nil,0)}, {__index=BrowserClass})
    function browserStub:loadSubcategories() end
    function browserStub:showDetail() end
    browserStub:onCategorySelected({item={name="event"}})
    local eventResult = browserStub.currentCategory
    browserStub.currentCategory = nil
    browserStub.categoryList = list({name="selected"},1)
    browserStub:onCategorySelected({})
    local selectedResult = browserStub.currentCategory
    emit("selection.pz_payloads", "selection", "event_and_selected_index", 4,
        eventResult == "event" and selectedResult == "selected",{event="event",fallback="selected"},{event=eventResult,fallback=selectedResult},false,{}, {"ISScrollingListBox payload shape"})

    local apple = BrowserData.getItem("Base.Apple")
    local WikiSections = require("Iris/UI/Wiki/IrisWikiSections")
    local foodOk = apple ~= nil
    local raw = {}
    if apple then
        raw.hunger = safeCall(apple, "getHungerChange")
        raw.thirst = safeCall(apple, "getThirstChange")
        raw.stress = safeCall(apple, "getStressChange")
        raw.boredom = safeCall(apple, "getBoredomChange")
        raw.food_renderer = WikiSections.renderFoodSection(apple)
        raw.core_renderer = WikiSections.renderCoreInfoSection(apple)
        foodOk = type(raw.food_renderer) == "string" and type(raw.core_renderer) == "string"
    end
    emit("detail.food_pz_units", "detail_raw_food", "Base.Apple", 5, foodOk,
        {capture="PZ getters and both renderer outputs"}, raw, true,{"Kahlua_numeric_format","Java_getters"},{})

    local IrisAPI = require("Iris/IrisAPI")
    local capabilities = IrisAPI.getCapabilities("Base.Hammer")
    local tags = IrisAPI.getTags("Base.Hammer")
    local Tooltip = require("Iris/UI/Tooltip/IrisTooltipSummary")
    local summary = Tooltip.get("Base.Hammer")
    emit("legacy.pz_surface", "legacy_surface", "Base.Hammer", 6,
        #capabilities > 0 and #tags > 0 and summary and #summary.tags > 0,
        {capability_nonempty=true,tags_nonempty=true,tooltip_tags_nonempty=true},
        {capabilities=arrayCopy(capabilities),tags=arrayCopy(tags),tooltip_tags=summary and arrayCopy(summary.tags) or {}},false,{}, {})

    local widgetPassed = false
    local widgetObserved = {error="not_run"}
    local widgetOk, widgetError = pcall(function()
        local IrisBrowser = require("Iris/UI/Browser/IrisBrowser")
        local hammer = BrowserData.getItem("Base.Hammer")
        assert(hammer, "Base.Hammer missing from BrowserData")
        IrisBrowser.openForItem(hammer)
        local browser = assert(IrisBrowser._instance, "browser instance missing")
        local beforeChildren = collectLuaChildren(browser.detailPanel)
        local beforeFirst = beforeChildren[1]
        local clickTargetCount = 0
        for _, child in ipairs(beforeChildren) do
            if child and child.target == browser then clickTargetCount = clickTargetCount + 1 end
        end
        browser:onDetailMouseWheel(1)
        local afterChildren = collectLuaChildren(browser.detailPanel)
        local afterFirst = afterChildren[1]
        local rebuilt = beforeFirst ~= nil and afterFirst ~= nil and not rawequal(beforeFirst, afterFirst)
        widgetPassed = #beforeChildren > 0 and #afterChildren > 0 and rebuilt and clickTargetCount > 0
        widgetObserved = {before_child_count=#beforeChildren,after_child_count=#afterChildren,first_child_rebuilt=rebuilt,click_target_count=clickTargetCount}
        browser:close()
    end)
    if not widgetOk then widgetObserved = {error=tostring(widgetError)} end
    emit("scroll_click.pz_pre_refactor", "scroll_click_widget", "Base.Hammer", 5, widgetPassed,
        {first_child_rebuilt=true,click_target_count_minimum=1}, widgetObserved, true,{"ISUI_child_identity","Kahlua_callback_target"},{})

    print("IRIS_CORE_SUMMARY\t" .. encode({row_count=rows,failure_count=failures}))
    local success = failures == 0
    local quitOk, quitError = pcall(function() getCore():quitToDesktop() end)
    if not quitOk then print("IRIS_CORE_QUIT_ERROR\t" .. tostring(quitError)) end
    return success
end

return Harness
