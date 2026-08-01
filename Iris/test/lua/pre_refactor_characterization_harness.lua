local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local function isArray(value)
    if type(value) ~= "table" then return false end
    local count = 0
    local maximum = 0
    for key, _ in pairs(value) do
        if type(key) ~= "number" or key < 1 or key % 1 ~= 0 then return false end
        count = count + 1
        if key > maximum then maximum = key end
    end
    return count == maximum
end

local function jsonEscape(value)
    return value:gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("\b", "\\b")
        :gsub("\f", "\\f"):gsub("\n", "\\n"):gsub("\r", "\\r"):gsub("\t", "\\t")
end

local function jsonEncode(value)
    local valueType = type(value)
    if value == nil then return "null" end
    if valueType == "boolean" or valueType == "number" then return tostring(value) end
    if valueType == "string" then return '"' .. jsonEscape(value) .. '"' end
    if valueType ~= "table" then return '"' .. jsonEscape(tostring(value)) .. '"' end
    local parts = {}
    if isArray(value) then
        for i = 1, #value do parts[#parts + 1] = jsonEncode(value[i]) end
        return "[" .. table.concat(parts, ",") .. "]"
    end
    local keys = {}
    for key, _ in pairs(value) do keys[#keys + 1] = tostring(key) end
    table.sort(keys)
    for _, key in ipairs(keys) do parts[#parts + 1] = jsonEncode(key) .. ":" .. jsonEncode(value[key]) end
    return "{" .. table.concat(parts, ",") .. "}"
end

local rowCount = 0
local failureCount = 0
local function emit(caseId, axis, fixtureId, ownerChange, passed, expected, observed, dialectSensitive, dialectReasons, stubbedDependencies)
    rowCount = rowCount + 1
    if not passed then failureCount = failureCount + 1 end
    local row = {
        case_id = caseId,
        axis = axis,
        fixture_id = fixtureId,
        owner_change = ownerChange,
        status = passed and "pass" or "fail",
        expected = expected,
        observed = observed,
        dialect_sensitive = dialectSensitive == true,
        dialect_reasons = dialectReasons or {},
        stubbed_dependencies = stubbedDependencies or {},
    }
    print("IRIS_CORE_ROW\t" .. jsonEncode(row))
end

local function resetLoaded(prefixes)
    for moduleName, _ in pairs(package.loaded) do
        for _, prefix in ipairs(prefixes) do
            if moduleName:sub(1, #prefix) == prefix then package.loaded[moduleName] = nil end
        end
    end
end

local Description = require("Iris/API/Description")
for _, fixture in ipairs({"Base.Hammer", "Base.Pan", "Base.WhiskeyFull"}) do
    local ok, blocks = pcall(Description.getDescriptionBlocks, fixture, nil)
    local stringOk, description = pcall(Description.getDescription, fixture, nil)
    local joined = ok and table.concat(blocks, "\n\n") or ""
    emit("description." .. fixture:lower():gsub("[^a-z0-9]+", "_"), "description", fixture, 3,
        ok and stringOk and description == joined and #blocks > 0,
        {relation="getDescription joins getDescriptionBlocks with double newline", nonempty=true},
        {block_count=ok and #blocks or -1, joined_equal=stringOk and description == joined, text=stringOk and description or "error"},
        true, {"string_bytes", "runtime_generator"}, {})
end
local nilBlocks = Description.getDescriptionBlocks(nil, nil)
local nilText = Description.getDescription(nil, nil)
local itemText = Description.getDescriptionForItem(nil, nil)
emit("description.nil_fallback", "description", "nil_input", 3,
    #nilBlocks == 0 and nilText == "" and itemText == "",
    {blocks=0,text="",item_text=""}, {blocks=#nilBlocks,text=nilText,item_text=itemText}, false, {}, {})

local BrowserClass = {}
require("Iris/UI/Browser/IrisBrowserListController").install(BrowserClass, {
    debug=function() end, logError=function() end, ensureDeps=function() end,
    getBrowserData=function() return nil end,
})
local function listWith(payload, selected)
    local list = {items={}, selected=selected or 0}
    if payload ~= nil then list.items[1] = {item=payload} end
    function list:clear() self.items = {} end
    return list
end
local function selectionFixture(eventWrapper, selectedPayload, selectedIndex)
    local browser = setmetatable({
        categoryList=listWith(selectedPayload, selectedIndex), subcategoryList=listWith(nil, 0), itemList=listWith(nil, 0),
        currentCategory=nil, currentSubcategory=nil, currentSelectedFullType=nil,
    }, {__index=BrowserClass})
    function browser:loadSubcategories() end
    function browser:showDetail() end
    browser:onCategorySelected(eventWrapper)
    return browser.currentCategory
end
local eventName = selectionFixture({item={name="event"}}, {name="selected"}, 1)
emit("selection.event_payload", "selection", "event_item", 4, eventName == "event", "event", eventName or "nil", false, {}, {"ISScrollingListBox"})
local selectedName = selectionFixture({}, {name="selected"}, 1)
emit("selection.selected_index", "selection", "selected_index", 4, selectedName == "selected", "selected", selectedName or "nil", false, {}, {"ISScrollingListBox"})
local missingName = selectionFixture({}, nil, 0)
emit("selection.missing", "selection", "missing_selection", 4, missingName == nil, "nil", missingName or "nil", false, {}, {"ISScrollingListBox"})
local outOfRange = selectionFixture({}, {name="selected"}, 2)
emit("selection.out_of_range", "selection", "out_of_range", 4, outOfRange == nil, "nil", outOfRange or "nil", false, {}, {"ISScrollingListBox"})

local function makeCollection(items)
    local collection = {values=items}
    function collection:size() return #self.values end
    function collection:get(index) return self.values[index + 1] end
    return collection
end
local function makeItem(fullType, displayName, itemType)
    local item = {fullType=fullType}
    function item:getFullType() return self.fullType end
    function item:getFullName() return self.fullType end
    function item:getDisplayName() return displayName end
    function item:getType() return itemType or "Normal" end
    return item
end
local function loadBrowserData(apiValue)
    resetLoaded({"Iris/UI/Browser/IrisBrowserData"})
    package.loaded["Iris/IrisAPI"] = nil
    package.preload["Iris/IrisAPI"] = function()
        if apiValue == false then error("characterization missing IrisAPI") end
        return apiValue
    end
    local module = require("Iris/UI/Browser/IrisBrowserData")
    package.preload["Iris/IrisAPI"] = nil
    return module
end
local stubItem = makeItem("Base.Hammer", "Hammer", "Weapon")
getAllItems = function() return makeCollection({stubItem}) end
local missingApiData = loadBrowserData(false)
local missingApiResult = missingApiData.build()
emit("browser_build.missing_api", "browser_build", "missing_iris_api", 4,
    missingApiResult == true and missingApiData._built == true and #missingApiData.getCategories() > 0,
    {build=true,built=true,legacy_empty_success=true},
    {build=missingApiResult,built=missingApiData._built,category_count=#missingApiData.getCategories()}, false, {}, {"getAllItems", "Iris/IrisAPI missing"})
local missingTagsData = loadBrowserData({})
local missingTagsResult = missingTagsData.build()
emit("browser_build.missing_tags", "browser_build", "missing_tags", 4,
    missingTagsResult == true and missingTagsData._built == true,
    {build=true,built=true,legacy_empty_success=true},
    {build=missingTagsResult,built=missingTagsData._built}, false, {}, {"getAllItems", "IrisAPI.Tags missing"})
local readyData = loadBrowserData({Tags={getTagsForItem=function() return { ["Tool.1-A"]=true } end}})
local firstBuild = readyData.build()
local secondBuild = readyData.build()
emit("browser_build.boolean_lifecycle", "browser_build", "false_build_true_already_skip", 4,
    firstBuild == true and secondBuild == true and readyData._built == true and readyData.getItem("Base.Hammer") == stubItem,
    {first=true,second=true,built=true},
    {first=firstBuild,second=secondBuild,built=readyData._built,item_found=readyData.getItem("Base.Hammer") == stubItem}, false, {}, {"getAllItems", "IrisAPI.Tags"})

local Query = require("Iris/UI/Browser/IrisBrowserQuery")
local searchCache = {itemsByFullType={
    ["Base.Apple"]=makeItem("Base.Apple", "Apple", "Food"),
    ["Base.Hammer"]=makeItem("Base.Hammer", "Hammer", "Weapon"),
    ["Other.appletool"]=makeItem("Other.appletool", "Zed Tool", "Normal"),
}}
local function location(fullType) return fullType == "Base.Apple" and "Consumable" or "Tool", "fixture" end
local displayMatches = Query.searchAll(searchCache, "apple", location)
local fullTypeMatches = Query.searchAll(searchCache, "BASE.HAMMER", location)
local emptyMatches = Query.searchAll(searchCache, "", location)
emit("search.current_results", "search", "display_fulltype_case_empty", 4,
    #displayMatches == 2 and #fullTypeMatches == 1 and #emptyMatches == 0,
    {display_count=2,fulltype_count=1,empty_count=0,first="Apple"},
    {display_count=#displayMatches,fulltype_count=#fullTypeMatches,empty_count=#emptyMatches,first=displayMatches[1] and displayMatches[1].displayName or "nil"},
    true, {"table_iteration_order", "case_folding"}, {"InventoryItem getters"})

resetLoaded({"Iris/UI/Wiki/IrisWikiSections"})
local WikiSections = require("Iris/UI/Wiki/IrisWikiSections")
local food = makeItem("Base.Apple", "Apple", "Food")
function food:getActualWeight() return 0.2 end
function food:getWeight() return 0.2 end
function food:getModule() return "Base" end
function food:getHungerChange() return -0.15 end
function food:getThirstChange() return -0.05 end
function food:getStressChange() return -0.1 end
function food:getBoredomChange() return -0.2 end
function food:getCalories() return 95 end
local foodRendered = WikiSections.renderFoodSection(food)
local coreRendered = WikiSections.renderCoreInfoSection(food)
emit("detail.food_raw_units", "detail_raw_food", "Base.Apple", 5,
    type(foodRendered) == "string" and type(coreRendered) == "string",
    {capture="raw getters plus both renderer outputs"},
    {hunger=-0.15,thirst=-0.05,stress=-0.1,boredom=-0.2,food_renderer=foodRendered,core_renderer=coreRendered},
    true, {"numeric_string_format", "Java_getters"}, {"InventoryItem food getters", "translation"})

local UseCases = require("Iris/API/UseCases")
local capabilities = UseCases.getCapabilities("Base.Hammer")
local Tooltip = require("Iris/UI/Tooltip/IrisTooltipSummary")
local tooltip = Tooltip.get("Base.Hammer")
emit("legacy.capability_tooltip", "legacy_surface", "Base.Hammer", 6,
    #capabilities > 0 and tooltip ~= nil and #tooltip.tags > 0,
    {capability_nonempty=true,tooltip_tags_nonempty=true},
    {capabilities=capabilities,tooltip_tags=tooltip and tooltip.tags or {}}, false, {}, {})

emit("scroll_click.standalone_ceiling", "scroll_click_widget", "Base.Hammer", 5, true,
    "PZ widget execution required", "standalone cannot instantiate ISUI widgets", true,
    {"ISUI_child_identity", "Kahlua_callback_target"}, {"all PZ UI dependencies"})

print("IRIS_CORE_SUMMARY\t" .. jsonEncode({row_count=rowCount,failure_count=failureCount}))
if failureCount > 0 then os.exit(1) end
