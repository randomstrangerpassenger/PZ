local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
local mode = assert(arg and arg[2], "mode argument is required")
assert(mode == "Baseline" or mode == "Acceptance", "mode must be Baseline or Acceptance")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

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

local rowCount, failureCount = 0, 0
local function emit(caseId, axis, passed, expected, observed)
    rowCount = rowCount + 1
    if not passed then failureCount = failureCount + 1 end
    print("IRIS_RESIDUAL_ROW\t" .. jsonEncode({
        case_id = caseId,
        axis = axis,
        mode = mode,
        status = passed and "pass" or "fail",
        expected = expected,
        observed = observed,
    }))
end

local function resetLoaded(prefixes)
    local matched = {}
    for moduleName, _ in pairs(package.loaded) do
        for _, prefix in ipairs(prefixes) do
            if moduleName:sub(1, #prefix) == prefix then
                matched[#matched + 1] = moduleName
                break
            end
        end
    end
    for _, moduleName in ipairs(matched) do package.loaded[moduleName] = nil end
end

local function shallowCopy(values)
    local result = {}
    for i, value in ipairs(values or {}) do result[i] = value end
    return result
end

-- Presentation order remains a projection: nine Browser categories and six
-- Description priorities with the historical 999 fallback.
local CategoryIndex = require("Iris/UI/Browser/IrisBrowserCategoryIndex")
local browserOrder = shallowCopy(CategoryIndex.CATEGORY_ORDER)
local projectionOk, Projection = pcall(require, "Iris/Logic/CategoryPresentationOrder")
local descriptionPriority = {}
for _, name in ipairs({"Tool", "Combat", "Consumable", "Resource", "Literature", "Wearable", "Furniture"}) do
    descriptionPriority[name] = projectionOk and Projection.getDescriptionPriority(name) or
        (({Tool=1,Combat=2,Consumable=3,Resource=4,Literature=5,Wearable=6})[name] or 999)
end
emit("presentation.browser_and_description_order", "presentation_order",
    #browserOrder == 9 and descriptionPriority.Tool == 1 and descriptionPriority.Wearable == 6 and
        descriptionPriority.Furniture == 999,
    {browser_count=9,description_priorities={Tool=1,Wearable=6,Furniture=999}},
    {browser_order=browserOrder,description_priorities=descriptionPriority,neutral_projection_loaded=projectionOk})

-- Variant folding must choose the ordinal-smallest non-empty fullType no
-- matter which map insertion order produced the group.
package.preload["Iris/Util/IrisProtectedCall"] = function()
    return {
        data=function(callback) local ok, value = pcall(callback); return ok, value end,
        require=function(moduleName) return pcall(require, moduleName) end,
    }
end
package.preload["Iris/Util/IrisItemAccess"] = function()
    return {
        getFullType=function(item, fallback) return item and item.fullType or fallback end,
        getDisplayName=function(item, fallback) return item and item.displayName or fallback end,
        getType=function(item, fallback) return item and item.itemType or fallback end,
        getModuleName=function(item, fallback)
            if item and item.getModule then return item:getModule() end
            return fallback
        end,
    }
end
package.preload["Iris/Util/IrisObjectAccess"] = function()
    local access = {}
    function access.call(target, methodName, ...)
        local method = target and target[methodName]
        if type(method) ~= "function" then return false, nil end
        return pcall(method, target, ...)
    end
    function access.invokeMethod(target, methodName, fallback, ...)
            local method = target and target[methodName]
            if type(method) ~= "function" then return fallback end
            local ok, value = pcall(method, target, ...)
            if ok then return value end
            return fallback
    end
    function access.firstValue(target, methodNames, fallback)
        for _, methodName in ipairs(methodNames or {}) do
            local ok, value = access.call(target, methodName)
            if ok and value ~= nil then return value end
        end
        return fallback
    end
    return access
end
resetLoaded({"Iris/UI/Browser/IrisBrowserVariantIndex"})
local VariantIndex = require("Iris/UI/Browser/IrisBrowserVariantIndex")
local recipeLookupCalls = 0
local variantApi = {
    Index={getRecipeConnectionsForItem=function() recipeLookupCalls = recipeLookupCalls + 1; return {} end},
    Tags={getTagsForItem=function() return { ["Tool.1-A"]=true } end},
}
local cache = {categories={Tool={subcategories={}}},itemsByFullType={}}
for _, fullType in ipairs({"Base.Zed", "Base.Alpha", "Base.Middle"}) do
    cache.itemsByFullType[fullType] = {displayName="Shared",itemType="Normal"}
end
local representatives = {}
for index, order in ipairs({
    {"Base.Zed", "Base.Alpha", "Base.Middle"},
    {"Base.Middle", "Base.Zed", "Base.Alpha"},
    {"Base.Alpha", "Base.Middle", "Base.Zed"},
}) do
    local subData = {items={},count=3}
    for _, fullType in ipairs(order) do subData.items[fullType] = true end
    cache.categories.Tool.subcategories["1-A"] = subData
    local rows = VariantIndex.getItems(cache, "Tool", "1-A", variantApi, nil)
    representatives[index] = rows[1] and rows[1].fullType or "nil"
end
local deterministic = representatives[1] == "Base.Alpha" and representatives[2] == "Base.Alpha" and
    representatives[3] == "Base.Alpha"
local foldedCount = VariantIndex.calculateFoldedCount(cache, cache.categories.Tool.subcategories["1-A"], variantApi)
local emptyKeyOk = pcall(VariantIndex.getFoldedCountCacheKey, {items={[""]=true}})
local groupingDerivedOnce = recipeLookupCalls == 3 and foldedCount == 1
emit("browser.variant_representative_permutations", "browser_determinism",
    mode == "Baseline" or (deterministic and not emptyKeyOk and groupingDerivedOnce),
    mode == "Acceptance" and {representative="Base.Alpha",all_permutations_equal=true,
        empty_fulltype_fails_loud=true,grouping_derived_once=true} or
        {capture="pre-mutation representative identities"},
    {representatives=representatives,deterministic=deterministic,empty_fulltype_fails_loud=not emptyKeyOk,
        recipe_lookup_calls=recipeLookupCalls,folded_count=foldedCount,grouping_derived_once=groupingDerivedOnce})

-- Public frozen-data facades capture the current leak in Baseline and require
-- mutation isolation in Acceptance. Predicates are checked with a copy counter.
local frozen = {
    classifications={["Base.Sample"]={"Tool.1-A","Resource.4-A"}},
    useCaseDescriptions={["Base.Sample"]={lines={"line-1"},debug_lines={"debug-1"}}},
    contextOutcomes={["Base.Sample"]={"outcome-1"}},
    capabilities={["Base.Sample"]={"capability-1"}},
}
package.preload["Iris/API/StaticData"] = function()
    return {get=function(name) return frozen[name] end}
end
package.preload["Iris/Util/ItemKey"] = function()
    return {getFullTypeFromItem=function(item) return item and item.fullType end}
end
local publicCopyCalls = 0
package.preload["Iris/Util/Array"] = function()
    return {
        contains=function(values, needle)
            for _, value in ipairs(values or {}) do if value == needle then return true end end
            return false
        end,
        copy=function(values)
            publicCopyCalls = publicCopyCalls + 1
            local result = {}
            for index, value in ipairs(values or {}) do result[index] = value end
            return result
        end,
    }
end
resetLoaded({"Iris/API/Tags", "Iris/API/UseCases"})
local Tags = require("Iris/API/Tags")
local firstTags = Tags.getTags("Base.Sample")
firstTags[1] = "Mutated"
local tagsIsolated = Tags.getTags("Base.Sample")[1] == "Tool.1-A"
local UseCases = require("Iris/API/UseCases")
local firstLines = UseCases.getUseCaseLines("Base.Sample")
firstLines.lines[1] = "Mutated"
firstLines.debug_lines[1] = "Mutated"
local secondLines = UseCases.getUseCaseLines("Base.Sample")
local firstOutcomes = UseCases.getOutcomes("Base.Sample")
firstOutcomes[1] = "Mutated"
local firstCapabilities = UseCases.getCapabilities("Base.Sample")
firstCapabilities[1] = "Mutated"
local copyCallsBeforePredicates = publicCopyCalls
local predicatesUseRaw = Tags.hasTag("Base.Sample", "Tool.1-A") and
    Tags.isClassified("Base.Sample") and
    UseCases.hasOutcome("Base.Sample", "outcome-1") and
    UseCases.hasCapability("Base.Sample", "capability-1") and
    publicCopyCalls == copyCallsBeforePredicates
local predicateCopyDelta = publicCopyCalls - copyCallsBeforePredicates
local nestedIsolated = secondLines.lines[1] == "line-1" and secondLines.debug_lines[1] == "debug-1"
local outcomesIsolated = UseCases.getOutcomes("Base.Sample")[1] == "outcome-1"
local capabilitiesIsolated = UseCases.getCapabilities("Base.Sample")[1] == "capability-1"
emit("api.public_copy_on_read", "mutation_isolation",
    mode == "Baseline" or (tagsIsolated and nestedIsolated and outcomesIsolated and capabilitiesIsolated and predicatesUseRaw),
    mode == "Acceptance" and {all_isolated=true} or {capture="pre-mutation isolation exposure"},
    {tags=tagsIsolated,nested_lines=nestedIsolated,outcomes=outcomesIsolated,
        capabilities=capabilitiesIsolated,predicates_use_raw=predicatesUseRaw,
        predicate_copy_delta=predicateCopyDelta})

-- Tooltip summary cache records must be copied at the public edge.
package.preload["Iris/Util/IrisRequire"] = function()
    return {safeRequire=function(name)
        if name == "Iris/Data/IrisClassifications" then return true, { ["Base.Sample"]={"Tool.1-A"} } end
        if name == "Iris/Data/IrisRecipeIndex" then return true, {getRoles=function() return {"Input"} end} end
        if name == "Iris/Data/IrisUseCaseDescriptions" then return true, { ["Base.Sample"]={lines={"x"}} } end
        return false, nil
    end}
end
resetLoaded({"Iris/UI/Tooltip/IrisTooltipSummary", "Iris/Util/IrisRequire"})
local TooltipSummary = require("Iris/UI/Tooltip/IrisTooltipSummary")
local summaryA = TooltipSummary.get("Base.Sample")
summaryA.tags[1] = "Mutated"
summaryA.connections[1] = "Mutated"
summaryA.useCaseCount = 99
local summaryB = TooltipSummary.get("Base.Sample")
local summaryIsolated = summaryB.tags[1] == "Tool.1-A" and summaryB.connections[1] == "Recipe" and
    summaryB.useCaseCount == 1 and summaryA ~= summaryB
emit("tooltip.summary_copy_on_read", "mutation_isolation",
    mode == "Baseline" or summaryIsolated,
    mode == "Acceptance" and {record_and_nested_arrays_isolated=true} or {capture="pre-mutation cache exposure"},
    {isolated=summaryIsolated,second=summaryB})
package.loaded["Iris/Util/IrisRequire"] = nil
package.preload["Iris/Util/IrisRequire"] = nil

-- Wiki unit profile preserves current food (*100) and core (raw) outputs.
local runtimeLocale = "EN"
package.preload["Iris/Util/IrisTranslationResolver"] = function()
    local ko = {
        Iris_Detail_Hunger="허기",
        Iris_Detail_Thirst="갈증",
        Iris_Tooltip_Tags="태그",
        Iris_Tooltip_Connections="연결",
        Iris_Tooltip_UseCase="사용 사례",
        Iris_Tooltip_More="더보기",
        Iris_Tooltip_RightClickHint="우클릭 > Iris",
        Iris_Tooltip_ApiLoadFailed="API 로드 실패",
        Iris_Tooltip_None="없음",
        Iris_Tooltip_CountSuffix="개",
    }
    return {
        get=function(key, fallback)
            if runtimeLocale == "KO" and ko[key] then return ko[key] end
            return fallback or key
        end,
        getLangKey=function() return runtimeLocale end,
    }
end
resetLoaded({"Iris/UI/Wiki/IrisWikiSections", "Iris/UI/Wiki/IrisWikiUnitProfiles"})
local WikiSections = require("Iris/UI/Wiki/IrisWikiSections")
local foodItem = {fullType="Base.Food"}
function foodItem:getFullType() return self.fullType end
function foodItem:getFullName() return self.fullType end
function foodItem:getDisplayName() return "Food" end
function foodItem:getModule() return "Base" end
function foodItem:getType() return "Food" end
function foodItem:getActualWeight() return 0.2 end
function foodItem:getWeight() return 0.2 end
function foodItem:getHungerChange() return -0.15 end
function foodItem:getThirstChange() return -0.05 end
function foodItem:getStressChange() return -0.1 end
function foodItem:getBoredomChange() return -0.2 end
function foodItem:getCalories() return 95 end
local foodRendered = WikiSections.renderFoodSection(foodItem) or ""
local coreRendered = WikiSections.renderCoreInfoSection(foodItem) or ""
runtimeLocale = "KO"
local foodRenderedKo = WikiSections.renderFoodSection(foodItem) or ""
local coreRenderedKo = WikiSections.renderCoreInfoSection(foodItem) or ""
runtimeLocale = "EN"
local UnitProfiles = require("Iris/UI/Wiki/IrisWikiUnitProfiles")
local percentProfile = UnitProfiles.getProfile("percent_scaled")
local rawProfile = UnitProfiles.getProfile("raw")
local foodScaled = foodRendered:find("%-15") ~= nil and foodRendered:find("%-5") ~= nil
local coreRaw = coreRendered:find("Hunger: %-0") ~= nil and coreRendered:find("Thirst: %-0") ~= nil and
    coreRendered:find("%-15") == nil and coreRendered:find("%-5") == nil
local localeProfilesPreserved = foodRenderedKo:find("허기: %-15",1,false) ~= nil and
    coreRenderedKo:find("갈증: %-0",1,false) ~= nil and
    percentProfile.multiplier == 100 and percentProfile.format_string == "%.0f" and
    rawProfile.multiplier == 1 and rawProfile.format_string == "%.0f"
emit("wiki.current_unit_profiles", "wiki_units",
    foodScaled and coreRaw and localeProfilesPreserved,
    {food_multiplier=100,core_multiplier=1,format_string="%.0f",locales={"EN","KO"}},
    {characterizations={
        {source_field="hunger",profile="percent_scaled",multiplier=percentProfile.multiplier,
            format_string=percentProfile.format_string,locale_key="Iris_Detail_Hunger",input=-0.15,current_output=foodRendered},
        {source_field="hunger",profile="raw",multiplier=rawProfile.multiplier,
            format_string=rawProfile.format_string,locale_key="Iris_Detail_Hunger",input=-0.15,current_output=coreRendered},
    },food_renderer_ko=foodRenderedKo,core_renderer_ko=coreRenderedKo,
        food_scaled=foodScaled,core_raw=coreRaw,locale_profiles_preserved=localeProfilesPreserved})

-- Tooltip line assembly remains Tags -> Connections -> optional UseCase -> More.
local function tooltipLines(summary)
    resetLoaded({"Iris/UI/Tooltip/IrisAltTooltip", "Iris/Util/IrisModuleBootstrap", "Iris/Util/ItemKey"})
    package.preload["Iris/Util/IrisModuleBootstrap"] = function()
        return {create=function() return {safeRequire=function(name)
            if name == "Iris/IrisTranslationLoader" then return true, {get=function(_, fallback) return fallback end} end
            if name == "Iris/UI/Tooltip/IrisTooltipSummary" then
                if summary == false then return false, nil end
                return true, {get=function() return summary end}
            end
            return false, nil
        end,debug=function() end,warn=function() end,logError=function() end} end}
    end
    package.preload["Iris/Util/ItemKey"] = function() return {getFullTypeFromItem=function() return "Base.Sample" end} end
    isKeyDown = function() return true end
    UIFont = {Small="Small"}
    local lines = {}
    local tooltip = {height=10,width=200,item={}}
    function tooltip:drawRect() end
    function tooltip:drawRectBorder() end
    function tooltip:drawText(line) lines[#lines + 1] = line end
    function tooltip:setHeight(value) self.height = value end
    require("Iris/UI/Tooltip/IrisAltTooltip").addIrisOverlay(tooltip)
    return lines
end
local four = tooltipLines({tags={"Tool.1-A"},connections={"Recipe"},useCaseCount=1})
local three = tooltipLines({tags={"Tool.1-A"},connections={"Recipe"},useCaseCount=0})
local two = tooltipLines(false)
runtimeLocale = "KO"
local fourKo = tooltipLines({tags={"Tool.1-A"},connections={"Recipe"},useCaseCount=1})
runtimeLocale = "EN"
local tooltipContract = #four == 4 and #three == 3 and #two == 2 and
    four[1]:find("Tags",1,true) and four[2]:find("Connections",1,true) and
    four[3]:find("Use cases",1,true) and four[4]:find("More",1,true) and
    #fourKo == 4 and fourKo[1]:find("태그",1,true) and fourKo[2]:find("연결",1,true)
emit("tooltip.branch_matrix", "tooltip_lines", tooltipContract,
    {success_with_usecase=4,success_without_usecase=3,load_failure=2,
        order={"Tags","Connections","Use cases","More"},locale_refresh_without_fact_invalidation=true},
    {four=four,three=three,two=two,four_ko=fourKo})

-- Logger calls themselves and all debug-only iteration are gated when debug is
-- disabled. Warnings remain observable.
local debugCalls, warningCalls = 0, 0
package.preload["Iris/Logic/IrisDesc/Logger"] = function()
    return {
        isDebugEnabled=function() return false end,
        debug=function() debugCalls = debugCalls + 1 end,
        warn=function() warningCalls = warningCalls + 1 end,
        error=function() end,
    }
end
resetLoaded({"Iris/Logic/IrisDesc/Logger", "Iris/Logic/IrisDesc/TagParser",
    "Iris/Logic/IrisDesc/Ordering", "Iris/Logic/IrisDesc/Templates"})
local TagParser = require("Iris/Logic/IrisDesc/TagParser")
TagParser.collect({"Tool.1-A", "invalid"})
local Ordering = require("Iris/Logic/IrisDesc/Ordering")
Ordering.resolveSubcategories({["Tool.1-A"]=true}, nil)
local Templates = require("Iris/Logic/IrisDesc/Templates")
Templates.getTemplate("Tool.1-A")
local debugOffGated = debugCalls == 0
local warningPreserved = warningCalls == 1
package.preload["Iris/Logic/IrisDesc/Logger"] = function()
    return {
        isDebugEnabled=function() return true end,
        debug=function() debugCalls = debugCalls + 1 end,
        warn=function() warningCalls = warningCalls + 1 end,
        error=function() end,
    }
end
resetLoaded({"Iris/Logic/IrisDesc/Logger", "Iris/Logic/IrisDesc/TagParser",
    "Iris/Logic/IrisDesc/Ordering", "Iris/Logic/IrisDesc/Templates"})
TagParser = require("Iris/Logic/IrisDesc/TagParser")
TagParser.collect({"Tool.1-A", "invalid"})
Ordering = require("Iris/Logic/IrisDesc/Ordering")
Ordering.resolveSubcategories({["Tool.1-A"]=true}, nil)
Templates = require("Iris/Logic/IrisDesc/Templates")
Templates.getTemplate("Tool.1-A")
local debugOnPreserved = debugCalls > 0
local warningsInvariant = warningCalls == 2
emit("logging.debug_off_lazy", "lazy_debug",
    mode == "Baseline" or (debugOffGated and warningPreserved and debugOnPreserved and warningsInvariant),
    mode == "Acceptance" and {debug_off_calls=0,warnings_per_mode=1,debug_on_calls_positive=true} or
        {capture="pre-mutation eager debug calls"},
    {debug_off_gated=debugOffGated,debug_on_preserved=debugOnPreserved,
        warning_preserved=warningPreserved,warnings_invariant=warningsInvariant,
        total_debug_calls=debugCalls,total_warning_calls=warningCalls})

print("IRIS_RESIDUAL_SUMMARY\t" .. jsonEncode({mode=mode,row_count=rowCount,failure_count=failureCount}))
if failureCount > 0 then os.exit(1) end
