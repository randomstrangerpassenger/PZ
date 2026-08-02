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

function Harness.runAll()
    local BrowserData = require("Iris/UI/Browser/IrisBrowserData")
    local BrowserBase = require("Iris/UI/Browser/IrisBrowserBase")
    local ListController = require("Iris/UI/Browser/IrisBrowserListController")
    local IrisAPI = require("Iris/IrisAPI")
    local failures, rows = 0, 0

    local function emit(caseId, axis, fixtureId, passed, expected, observed, sensitive, stubs)
        rows = rows + 1
        if not passed then failures = failures + 1 end
        print("IRIS_CORE_ROW\t" .. encode({
            case_id=caseId,axis=axis,fixture_id=fixtureId,owner_change=4,
            status=passed and "pass" or "fail",expected=expected,observed=observed,
            dialect_sensitive=sensitive == true,dialect_reasons=sensitive and {"Kahlua_state_reentry"} or {},
            stubbed_dependencies=stubs or {},
        }))
    end

    local startup = BrowserData.getBuildState()
    emit("browser_acceptance.pz_startup", "browser_build_state", "browser_open_startup",
        BrowserData.isReady() and startup.generation > 0 and BrowserData._built == true,
        {ready=true,compatibility_built=true,generation_minimum=1},
        {state=startup.state,reason=startup.reason,generation=startup.generation,compatibility_built=BrowserData._built}, false)

    local originalTags = IrisAPI.Tags
    local originalIndex = IrisAPI.Index
    local effectiveIndex = originalIndex or {getRecipeConnectionsForItem=function() return {} end}
    local nested = nil
    IrisAPI.Index = effectiveIndex
    IrisAPI.Tags = {
        getTagsForItem = function(item)
            if not nested then
                local nestedReady, nestedState = BrowserData.ensureReady()
                nested = {ready=nestedReady,state=nestedState.state,reason=nestedState.reason}
            end
            return originalTags.getTagsForItem(item)
        end,
    }
    BrowserData.resetForReload()
    local resetState = BrowserData.getBuildState()
    local reentrantReady, reentrantState = BrowserData.ensureReady()
    emit("browser_acceptance.state_machine", "browser_build_state", "uninitialized_building_ready",
        resetState.state == "uninitialized" and nested and nested.ready == false and nested.state == "building" and
            reentrantReady and reentrantState.state == "ready" and BrowserData._built == true,
        {initial="uninitialized",nested="building",final="ready",compatibility_built=true},
        {initial=resetState.state,nested=nested and nested.state or "missing",nested_ready=nested and nested.ready or false,
            final=reentrantState.state,compatibility_built=BrowserData._built}, true, {"temporary IrisAPI.Tags wrapper"})

    IrisAPI.Tags = nil
    BrowserData.resetForReload()
    local failedReady, failedState = BrowserData.ensureReady()
    local atomicCacheNil = BrowserData._cache == nil
    IrisAPI.Tags = originalTags
    IrisAPI.Index = effectiveIndex

    local IrisBrowser = require("Iris/UI/Browser/IrisBrowser")
    local browserOpenOk, browserOpenError = pcall(IrisBrowser.openSearch)
    local recoveredState = BrowserData.getBuildState()
    local browserCreated = IrisBrowser._instance ~= nil
    if browserCreated then IrisBrowser._instance:close() end
    emit("browser_acceptance.required_retry", "browser_build_state", "missing_tags_then_browser_open",
        failedReady == false and failedState.state == "retryable_failed" and failedState.dependency == "IrisAPI.Tags" and
            BrowserData._built == true and atomicCacheNil and browserOpenOk and browserCreated and recoveredState.state == "ready",
        {failed="retryable_failed",dependency="IrisAPI.Tags",atomic_cache_nil=true,recovered="ready",browser_created=true},
        {failed=failedState.state,dependency=failedState.dependency,atomic_cache_nil=atomicCacheNil,
            recovered=recoveredState.state,browser_created=browserCreated,browser_error=browserOpenOk and "none" or tostring(browserOpenError)},
        true, {"temporary IrisAPI.Tags absence"})

    IrisAPI.Index = nil
    BrowserData.resetForReload()
    local degradedReady, degradedState = BrowserData.ensureReady()
    emit("browser_acceptance.optional_degraded", "browser_build_state", "missing_optional_index",
        degradedReady and degradedState.state == "degraded_ready" and degradedState.dependency == "IrisAPI.Index" and BrowserData._built == true,
        {ready=true,state="degraded_ready",dependency="IrisAPI.Index",compatibility_built=true},
        {ready=degradedReady,state=degradedState.state,dependency=degradedState.dependency,compatibility_built=BrowserData._built},
        false, {"temporary IrisAPI.Index absence"})

    IrisAPI.Tags = originalTags
    IrisAPI.Index = originalIndex
    BrowserData.resetForReload()
    BrowserData.ensureReady()

    local eventPayload, eventReason = ListController.resolveSelectedPayload({items={},selected=0}, {item={name="event"}})
    local fallbackPayload, fallbackReason = ListController.resolveSelectedPayload({items={{item={name="selected"}}},selected=1}, {})
    local missingPayload, missingReason = ListController.resolveSelectedPayload({items={},selected=0}, nil)
    local invalidPayload, invalidReason = ListController.resolveSelectedPayload({items={{item={name="selected"}}},selected=2}, {})
    emit("browser_acceptance.selection_matrix", "selection", "event_fallback_invalid",
        eventPayload and eventPayload.name == "event" and eventReason == "event_item" and
            fallbackPayload and fallbackPayload.name == "selected" and fallbackReason == "selected_index" and
            missingPayload == nil and missingReason == "no_selection" and invalidPayload == nil and invalidReason == "selected_index_invalid",
        {event="event",fallback="selected",missing="no_selection",invalid="selected_index_invalid"},
        {event=eventPayload and eventPayload.name or "nil",event_reason=eventReason,
            fallback=fallbackPayload and fallbackPayload.name or "nil",fallback_reason=fallbackReason,
            missing=missingReason,invalid=invalidReason}, false, {"ISScrollingListBox payload shape"})

    local hammerResults = BrowserData.searchAll("hammer")
    local deterministic = true
    for i = 2, #hammerResults do
        local previous, current = hammerResults[i - 1], hammerResults[i]
        if previous.displayName > current.displayName or
            (previous.displayName == current.displayName and previous.fullType > current.fullType) then
            deterministic = false
        end
    end
    local firstPass = BrowserData.searchAll("hammer")
    emit("browser_acceptance.search_pz", "search", "hammer_casefold_repeat",
        #hammerResults > 0 and #firstPass == #hammerResults and deterministic,
        {nonempty=true,repeat_equal_count=true,deterministic=true},
        {search_count=#hammerResults,repeat_count=#firstPass,deterministic=deterministic,
            first=hammerResults[1] and hammerResults[1].fullType or "nil"}, false)

    local function foldedProjection(values)
        local projection = {}
        for _, value in ipairs(values) do
            projection[#projection + 1] = value.name .. "=" .. tostring(value.itemCount)
        end
        return table.concat(projection, "|")
    end
    local foldedFirst = BrowserData.getSubcategories("Tool")
    local foldedSecond = BrowserData.getSubcategories("Tool")
    local firstProjection = foldedProjection(foldedFirst)
    local secondProjection = foldedProjection(foldedSecond)
    emit("browser_acceptance.folded_count_pz", "folded_count", "tool_repeat",
        #foldedFirst > 0 and firstProjection == secondProjection,
        {nonempty=true,repeat_exact=true},
        {subcategory_count=#foldedFirst,repeat_exact=firstProjection == secondProjection,projection=firstProjection}, false)

    print("IRIS_CORE_SUMMARY\t" .. encode({row_count=rows,failure_count=failures}))
    local success = failures == 0
    pcall(function() getCore():quitToDesktop() end)
    return success
end

return Harness
