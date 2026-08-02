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

local function call(item, methodName)
    local ok, value = pcall(function() return item[methodName](item) end)
    if ok then return value end
    return nil
end

local function collectChildren(panel)
    local result = {}
    local ok, children = pcall(function() return panel:getChildren() end)
    if not ok or not children then return result end
    local keys = {}
    for key, child in pairs(children) do
        if type(key) == "number" and child then keys[#keys + 1] = key end
    end
    table.sort(keys)
    for _, key in ipairs(keys) do result[#result + 1] = children[key] end
    return result
end

local function childY(child)
    local ok, value = pcall(function() return child:getY() end)
    if ok then return value end
    return child.y
end

local function sameIdentity(before, after)
    if #before ~= #after then return false end
    local present = {}
    for _, child in ipairs(after) do present[child] = true end
    for _, child in ipairs(before) do if not present[child] then return false end end
    return true
end

function Harness.runAll()
    local BrowserData = require("Iris/UI/Browser/IrisBrowserData")
    local DetailViewModel = require("Iris/UI/Detail/IrisItemDetailViewModel")
    local WikiSections = require("Iris/UI/Wiki/IrisWikiSections")
    local failures, rows = 0, 0
    local function emit(caseId, axis, fixtureId, passed, expected, observed, sensitive, reasons)
        rows = rows + 1
        if not passed then failures = failures + 1 end
        print("IRIS_CORE_ROW\t" .. encode({
            case_id=caseId,axis=axis,fixture_id=fixtureId,owner_change=5,
            status=passed and "pass" or "fail",expected=expected,observed=observed,
            dialect_sensitive=sensitive == true,dialect_reasons=reasons or {},stubbed_dependencies={},
        }))
    end

    local apple = BrowserData.getItem("Base.Apple")
    local appleModel = apple and DetailViewModel.fromItem(apple)
    local raw = appleModel and {
        hunger=appleModel.food.hunger,thirst=appleModel.food.thirst,
        stress=appleModel.food.stress,boredom=appleModel.food.boredom,
    } or {}
    local getterRaw = apple and {
        hunger=call(apple,"getHungerChange"),thirst=call(apple,"getThirstChange"),
        stress=call(apple,"getStressChange"),boredom=call(apple,"getBoredomChange"),
    } or {}
    local coreRenderer = appleModel and WikiSections.renderCoreInfoSection(appleModel) or nil
    local foodRenderer = appleModel and WikiSections.renderFoodSection(appleModel) or nil
    local wrapperCoreRenderer = apple and WikiSections.renderCoreInfoSection(apple) or nil
    local wrapperFoodRenderer = apple and WikiSections.renderFoodSection(apple) or nil
    emit("detail_acceptance.food_units", "detail_view_model", "Base.Apple",
        appleModel and raw.hunger == getterRaw.hunger and raw.thirst == getterRaw.thirst and
            raw.stress == getterRaw.stress and raw.boredom == getterRaw.boredom and coreRenderer and foodRenderer and
            wrapperCoreRenderer == coreRenderer and wrapperFoodRenderer == foodRenderer,
        {raw_equals_pz_getters=true,formatter_disposition="preserve_existing_behavior",item_wrapper_parity=true},
        {hunger=raw.hunger,thirst=raw.thirst,stress=raw.stress,boredom=raw.boredom,
            core_renderer=coreRenderer or "nil",food_renderer=foodRenderer or "nil",
            item_wrapper_parity=wrapperCoreRenderer == coreRenderer and wrapperFoodRenderer == foodRenderer},
        true, {"Java_getters","Kahlua_numeric_format"})

    local IrisBrowser = require("Iris/UI/Browser/IrisBrowser")
    IrisBrowser.openForItem(apple)
    local appleBrowser = IrisBrowser._instance
    local browserModel = appleBrowser and appleBrowser.currentDetailModel
    local wikiModel = DetailViewModel.fromItem(apple)
    local shared = browserModel and wikiModel and
        browserModel.fullType == wikiModel.fullType and browserModel.weight == wikiModel.weight and
        table.concat(browserModel.tags, "|") == table.concat(wikiModel.tags, "|") and
        browserModel.food.hunger == wikiModel.food.hunger and
        browserModel.availability.food == wikiModel.availability.food and
        browserModel.availability.layer3 == wikiModel.availability.layer3
    emit("detail_acceptance.browser_wiki_shared", "detail_view_model", "Base.Apple",
        shared == true,{shared_raw_and_availability=true},
        {full_type=browserModel and browserModel.fullType or "nil",weight_equal=browserModel and wikiModel and browserModel.weight == wikiModel.weight or false,
            tags_equal=browserModel and wikiModel and table.concat(browserModel.tags,"|") == table.concat(wikiModel.tags,"|") or false,
            food_available=wikiModel and wikiModel.availability.food or false,locale=wikiModel and wikiModel.locale or "nil"}, false)
    if appleBrowser then appleBrowser:close() end

    local adoptedItem = BrowserData.getItem("Base.223Box")
    local adoptedModel = adoptedItem and DetailViewModel.fromItem(adoptedItem)
    local layer3Renderer = require("Iris/Data/layer3_renderer")
    local unadoptedItem = nil
    for fullType, candidate in pairs((BrowserData._cache and BrowserData._cache.itemsByFullType) or {}) do
        if not layer3Renderer.getText(fullType) then
            unadoptedItem = candidate
            break
        end
    end
    local unadoptedModel = unadoptedItem and DetailViewModel.fromItem(unadoptedItem)
    emit("detail_acceptance.layer3_availability", "detail_view_model", "adopted_and_unadopted",
        adoptedModel and adoptedModel.availability.layer3 == true and adoptedModel.layer3.display ~= nil and
            unadoptedModel and unadoptedModel.availability.layer3 == false and WikiSections.renderLayer3Section(unadoptedModel) == nil,
        {adopted_available=true,unadopted_available=false},
        {adopted_full_type=adoptedModel and adoptedModel.fullType or "nil",
            adopted_available=adoptedModel and adoptedModel.availability.layer3 or false,
            adopted_state=adoptedModel and adoptedModel.layer3.adoptionState or "nil",
            unadopted_full_type=unadoptedModel and unadoptedModel.fullType or "nil",
            unadopted_available=unadoptedModel and unadoptedModel.availability.layer3 or false,
            unadopted_state=unadoptedModel and unadoptedModel.layer3.adoptionState or "nil"}, true, {"runtime_layer3_chunks"})

    local hammer = BrowserData.getItem("Base.Hammer")
    IrisBrowser.openForItem(hammer)
    local browser = IrisBrowser._instance
    local scrollPassed = false
    local scrollObserved = {error="browser_missing"}
    if browser and browser.detailPanel then
        local heightOk = pcall(function() browser.detailPanel:setHeight(120) end)
        if not heightOk then browser.detailPanel.height = 120 end
        local before = collectChildren(browser.detailPanel)
        local beforeFirstY = before[1] and childY(before[1]) or nil
        local beforeTargets = 0
        for _, child in ipairs(before) do if child.target == browser then beforeTargets = beforeTargets + 1 end end
        local beforeModel = browser.currentDetailModel
        browser:onDetailMouseWheel(1)
        local after = collectChildren(browser.detailPanel)
        local afterFirstY = after[1] and childY(after[1]) or nil
        local afterTargets = 0
        for _, child in ipairs(after) do if child.target == browser then afterTargets = afterTargets + 1 end end
        local firstIdentity = sameIdentity(before, after)
        local firstScroll = browser.detailScrollY
        browser:onDetailMouseWheel(1)
        local repeated = collectChildren(browser.detailPanel)
        local repeatedIdentity = sameIdentity(before, repeated)
        local maxScroll = math.max(0, browser.detailContentHeight - browser.detailPanel.height)
        local moved = beforeFirstY ~= nil and afterFirstY ~= nil and beforeFirstY - afterFirstY == firstScroll
        scrollPassed = #before > 0 and firstIdentity and repeatedIdentity and rawequal(beforeModel, browser.currentDetailModel) and
            beforeTargets > 0 and afterTargets == beforeTargets and firstScroll > 0 and browser.detailScrollY <= maxScroll and moved
        scrollObserved = {before_child_count=#before,after_child_count=#after,child_identity_preserved=firstIdentity,
            repeated_identity_preserved=repeatedIdentity,model_identity_preserved=rawequal(beforeModel,browser.currentDetailModel),
            click_target_count=afterTargets,scroll_after_first=firstScroll,scroll_after_second=browser.detailScrollY,
            max_scroll=maxScroll,first_child_moved_by_scroll=moved}
        browser:close()
    end
    emit("detail_acceptance.incremental_scroll", "scroll_click_widget", "Base.Hammer",
        scrollPassed,{child_identity_preserved=true,model_identity_preserved=true,click_target_count_minimum=1,scroll_positive=true},
        scrollObserved,true,{"ISUI_child_identity","Kahlua_callback_target","visual_scroll_range"})

    print("IRIS_CORE_SUMMARY\t" .. encode({row_count=rows,failure_count=failures}))
    local success = failures == 0
    pcall(function() getCore():quitToDesktop() end)
    return success
end

return Harness
