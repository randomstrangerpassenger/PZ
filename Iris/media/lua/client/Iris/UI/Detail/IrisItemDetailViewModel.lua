--[[
    IrisItemDetailViewModel.lua

    Shared, read-only raw facts for Browser and Wiki detail surfaces. Labels,
    recommendations, navigation and interaction handlers remain UI-owned.
]]

local ViewModel = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local ItemAccess = require("Iris/Util/IrisItemAccess")
local ObjectAccess = require("Iris/Util/IrisObjectAccess")
local Layer3DisplayFormatter = require("Iris/UI/Layer3/IrisLayer3DisplayFormatter")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")

local CORE_WEIGHT_METHODS = { "getActualWeight", "getWeight" }
local CORE_CATEGORY_METHODS = { "getDisplayCategory", "getCategory" }
local CORE_SUBCATEGORY_METHODS = { "getSubCategory" }
local FOOD_METHODS = {
    "getHungerChange", "getThirstChange", "getStressChange",
    "getBoredomChange", "getCalories",
}
local WEAPON_METHODS = {
    "getMinDamage", "getMaxDamage", "getMinRange", "getMaxRange",
    "getCriticalChance", "getConditionMax",
}
local LITERATURE_METHODS = {
    "getNumberOfPages", "getSkillTrained", "getLvlSkillTrained",
    "getNumLevelsTrained",
}
local MOVEABLE_METHODS = {
    "getCapacity", "getLightStrength", "isWaterproof", "getInsulation",
}
local GET_HUNGER_CHANGE = { "getHungerChange" }
local GET_THIRST_CHANGE = { "getThirstChange" }
local GET_STRESS_CHANGE = { "getStressChange" }
local GET_BOREDOM_CHANGE = { "getBoredomChange" }
local GET_CALORIES = { "getCalories" }
local GET_MIN_DAMAGE = { "getMinDamage" }
local GET_MAX_DAMAGE = { "getMaxDamage" }
local GET_MIN_RANGE = { "getMinRange" }
local GET_MAX_RANGE = { "getMaxRange" }
local GET_CRITICAL_CHANCE = { "getCriticalChance" }
local GET_CONDITION_MAX = { "getConditionMax" }
local GET_NUMBER_OF_PAGES = { "getNumberOfPages" }
local GET_SKILL_TRAINED = { "getSkillTrained" }
local GET_LEVEL_SKILL_TRAINED = { "getLvlSkillTrained" }
local GET_NUM_LEVELS_TRAINED = { "getNumLevelsTrained" }
local GET_CAPACITY = { "getCapacity" }
local GET_LIGHT_STRENGTH = { "getLightStrength" }
local IS_WATERPROOF = { "isWaterproof" }
local GET_INSULATION = { "getInsulation" }

local instrumentationEnabled = false

local function newMetrics()
    return {
        fromItemCalls = 0,
        methodAttempts = 0,
        methodSuccesses = 0,
        groupAttempts = {},
        groupSuccesses = {},
        groupSkips = {},
        staticCacheHits = 0,
        staticCacheMisses = 0,
        capabilityHintBuilds = 0,
        methodListAllocations = 0,
    }
end

local metrics = newMetrics()

local function recordGroup(target, group)
    target[group] = (target[group] or 0) + 1
end

local function read(item, methodNames, group)
    local normalizedGroup = group or "core"
    for _, methodName in ipairs(methodNames or {}) do
        if instrumentationEnabled then
            metrics.methodAttempts = metrics.methodAttempts + 1
            recordGroup(metrics.groupAttempts, normalizedGroup)
        end
        local ok, value = ObjectAccess.call(item, methodName)
        if ok and value ~= nil then
            if instrumentationEnabled then
                metrics.methodSuccesses = metrics.methodSuccesses + 1
                recordGroup(metrics.groupSuccesses, normalizedGroup)
            end
            return value
        end
    end
    return nil
end

local function capabilityHints(category, itemType)
    if instrumentationEnabled then
        metrics.capabilityHintBuilds = metrics.capabilityHintBuilds + 1
    end
    local hints = {}
    -- Category/type text is positive evidence only. Matching canonical labels
    -- are not closed negative evidence because a mod item can expose hybrid
    -- fields while retaining a vanilla-looking category and type.
    local text = (tostring(category or "") .. " " .. tostring(itemType or "")):lower()
    if text:find("food", 1, true) then hints.food = true end
    if text:find("weapon", 1, true) then hints.weapon = true end
    if text:find("literature", 1, true) or text:find("book", 1, true) then
        hints.literature = true
    end
    if text:find("moveable", 1, true) or text:find("furniture", 1, true) then
        hints.moveable = true
    end

    return hints
end

local function groupApplicable(item, methodNames, group, hints)
    if hints[group] then return true end
    for _, methodName in ipairs(methodNames or {}) do
        local ok, method = pcall(function() return item[methodName] end)
        if ok and method ~= nil then return true end
    end
    if instrumentationEnabled then recordGroup(metrics.groupSkips, group) end
    return false
end

local function readIfApplicable(applicable, item, methodNames, group)
    if not applicable then return nil end
    return read(item, methodNames, group)
end

local function sortedTags(IrisAPI, item)
    local result = {}
    if not IrisAPI or not IrisAPI.Tags or not IrisAPI.Tags.getTagsForItem then return result end
    local ok, tags = ProtectedCall.data(function() return IrisAPI.Tags.getTagsForItem(item) end)
    if not ok or type(tags) ~= "table" then return result end
    for tag, present in pairs(tags) do
        if present then result[#result + 1] = tag end
    end
    table.sort(result)
    return result
end

local function safeIndexCall(Index, methodName, item)
    if not Index or not Index[methodName] then return nil end
    local ok, value = ProtectedCall.data(function() return Index[methodName](item) end)
    if ok then return value end
    return nil
end

local function safeUseCaseCall(UseCases, methodName, argument, fallback)
    if not UseCases or not UseCases[methodName] then return fallback end
    local ok, value = ProtectedCall.data(function() return UseCases[methodName](argument) end)
    if ok and value ~= nil then return value end
    return fallback
end

local function safeInteractionState(UseCases, fullType)
    if UseCases and UseCases._getDescriptionState then
        local ok, value = ProtectedCall.data(function()
            return UseCases._getDescriptionState(fullType)
        end)
        if ok and type(value) == "table" and
            (value.status == "available" or value.status == "verified_empty" or value.status == "fault") then
            return value
        end
        return {
            status = "fault", reason = "status_lookup_failed", fallback_used = false,
            entry = nil, lines = {}, exclusion_lines = {}, debug_lines = {},
        }
    end

    -- Compatibility for injected/older facades. Production Iris always owns
    -- the private status-bearing path; absence is not treated as verified empty.
    local legacy = safeUseCaseCall(
        UseCases, "getUseCaseLines", fullType, {lines={}, debug_lines={}}
    )
    local lines = legacy.lines or {}
    local debugLines = legacy.debug_lines or {}
    return {
        status = #lines > 0 and "available" or "fault",
        reason = "status_api_unavailable",
        fallback_used = true,
        entry = nil,
        lines = lines,
        exclusion_lines = {},
        debug_lines = debugLines,
    }
end

local function layer3Payload(fullType)
    local ok, renderer = safeRequire("Iris/Data/layer3_renderer")
    if not ok or not renderer or not renderer.getText or not fullType then
        return {available=false,adoptionState="unavailable",publishState=nil,raw=nil,display=nil}
    end
    local publishState = renderer.getPublishState and renderer.getPublishState(fullType) or nil
    local callOk, raw = ProtectedCall.data(function() return renderer.getText(fullType) end)
    if not callOk or not raw or raw == "" then
        return {available=false,adoptionState=publishState or "unavailable",publishState=publishState,raw=nil,display=nil}
    end
    return {available=true,adoptionState=publishState or "public_legacy",publishState=publishState,
        raw=raw,display=Layer3DisplayFormatter.format(raw)}
end

local function readonly(values)
    return setmetatable({}, {
        __index = values,
        __newindex = function() error("IrisItemDetailViewModel is read-only", 2) end,
        __metatable = "IrisItemDetailViewModel.readonly",
    })
end

local function readonlyArray(values)
    return readonly(values or {})
end

--- Return a mutable consumer-local copy of a read-only array field. This keeps
--- Lua 5.1/Kahlua iteration semantics out of the proxy contract.
function ViewModel.copyArray(values)
    local result = {}
    local index = 1
    while values and values[index] ~= nil do
        result[index] = values[index]
        index = index + 1
    end
    return result
end

function ViewModel.arrayLength(values)
    local index = 1
    while values and values[index] ~= nil do index = index + 1 end
    return index - 1
end

function ViewModel.isViewModel(value)
    return type(value) == "table" and value.__irisItemDetailViewModel == true
end

function ViewModel.fromItem(item)
    if not item then return nil end

    if instrumentationEnabled then
        metrics.fromItemCalls = metrics.fromItemCalls + 1
        metrics.staticCacheMisses = metrics.staticCacheMisses + 1
    end

    local apiOk, IrisAPI = safeRequire("Iris/IrisAPI")
    if not apiOk then IrisAPI = nil end
    local fullType = ItemAccess.getFullType(item)
    local interactionState = safeInteractionState(IrisAPI and IrisAPI.UseCases, fullType)
    local useCaseData = {
        lines = interactionState.lines or {},
        debug_lines = interactionState.debug_lines or {},
        status = interactionState.status,
        reason = interactionState.reason,
        fallback_used = interactionState.fallback_used == true,
    }
    local capabilities = safeUseCaseCall(IrisAPI and IrisAPI.UseCases, "getCapabilities", fullType, {})
    local Index = IrisAPI and IrisAPI.Index
    local layer3 = layer3Payload(fullType)
    local itemType = ItemAccess.getType(item)
    local weight = read(item, CORE_WEIGHT_METHODS, "core")
    local category = read(item, CORE_CATEGORY_METHODS, "core")
    local subcategory = read(item, CORE_SUBCATEGORY_METHODS, "core")
    local hints = capabilityHints(category, itemType)
    local foodApplicable = groupApplicable(item, FOOD_METHODS, "food", hints)
    local weaponApplicable = groupApplicable(item, WEAPON_METHODS, "weapon", hints)
    local literatureApplicable = groupApplicable(item, LITERATURE_METHODS, "literature", hints)
    local moveableApplicable = groupApplicable(item, MOVEABLE_METHODS, "moveable", hints)

    local values = {
        __irisItemDetailViewModel = true,
        sourceItem = item,
        locale = TranslationResolver.getLangKey("EN"),
        fullType = fullType,
        displayName = ItemAccess.getDisplayName(item, fullType or "Unknown"),
        moduleName = ItemAccess.getModuleName(item),
        itemType = itemType,
        weight = weight,
        category = category,
        subcategory = subcategory,
        tags = sortedTags(IrisAPI, item),
        food = {
            hunger = readIfApplicable(foodApplicable, item, GET_HUNGER_CHANGE, "food"),
            thirst = readIfApplicable(foodApplicable, item, GET_THIRST_CHANGE, "food"),
            stress = readIfApplicable(foodApplicable, item, GET_STRESS_CHANGE, "food"),
            boredom = readIfApplicable(foodApplicable, item, GET_BOREDOM_CHANGE, "food"),
            calories = readIfApplicable(foodApplicable, item, GET_CALORIES, "food"),
        },
        weapon = {
            minDamage = readIfApplicable(weaponApplicable, item, GET_MIN_DAMAGE, "weapon"),
            maxDamage = readIfApplicable(weaponApplicable, item, GET_MAX_DAMAGE, "weapon"),
            minRange = readIfApplicable(weaponApplicable, item, GET_MIN_RANGE, "weapon"),
            maxRange = readIfApplicable(weaponApplicable, item, GET_MAX_RANGE, "weapon"),
            criticalChance = readIfApplicable(weaponApplicable, item, GET_CRITICAL_CHANCE, "weapon"),
            conditionMax = readIfApplicable(weaponApplicable, item, GET_CONDITION_MAX, "weapon"),
        },
        literature = {
            numberOfPages = readIfApplicable(literatureApplicable, item, GET_NUMBER_OF_PAGES, "literature"),
            skillTrained = readIfApplicable(literatureApplicable, item, GET_SKILL_TRAINED, "literature"),
            level = readIfApplicable(literatureApplicable, item, GET_LEVEL_SKILL_TRAINED, "literature"),
            levelCount = readIfApplicable(literatureApplicable, item, GET_NUM_LEVELS_TRAINED, "literature"),
        },
        moveable = {
            capacity = readIfApplicable(moveableApplicable, item, GET_CAPACITY, "moveable"),
            lightStrength = readIfApplicable(moveableApplicable, item, GET_LIGHT_STRENGTH, "moveable"),
            waterproof = readIfApplicable(moveableApplicable, item, IS_WATERPROOF, "moveable"),
            insulation = readIfApplicable(moveableApplicable, item, GET_INSULATION, "moveable"),
        },
        layer3 = layer3,
        connections = {
            recipes = safeIndexCall(Index, "getRecipeConnectionsForItem", item) or {},
            moveables = safeIndexCall(Index, "getMoveablesInfoForItem", item),
            fixing = safeIndexCall(Index, "getFixingInfoForItem", item),
        },
        useCases = useCaseData,
        interactionState = interactionState,
        capabilities = capabilities,
    }
    values.availability = {
        food = values.food.hunger ~= nil or values.food.thirst ~= nil or values.food.calories ~= nil,
        weapon = values.weapon.minDamage ~= nil or values.weapon.conditionMax ~= nil,
        literature = values.literature.numberOfPages ~= nil or values.literature.skillTrained ~= nil,
        moveable = values.moveable.capacity ~= nil or values.connections.moveables ~= nil,
        layer3 = layer3.available,
        useCases = #(useCaseData.lines or {}) > 0 or #(useCaseData.debug_lines or {}) > 0,
        capabilities = #capabilities > 0,
    }
    values.revision = tostring(fullType) .. "|" .. tostring(values.locale)

    values.tags = readonlyArray(values.tags)
    values.food = readonly(values.food)
    values.weapon = readonly(values.weapon)
    values.literature = readonly(values.literature)
    values.moveable = readonly(values.moveable)
    values.layer3 = readonly(values.layer3)
    values.connections = readonly({
        recipes = readonlyArray(values.connections.recipes),
        moveables = values.connections.moveables and readonly(values.connections.moveables) or nil,
        fixing = values.connections.fixing and readonly(values.connections.fixing) or nil,
    })
    values.useCases = readonly({
        lines = readonlyArray(values.useCases.lines),
        debug_lines = readonlyArray(values.useCases.debug_lines),
        status = values.useCases.status,
        reason = values.useCases.reason,
        fallback_used = values.useCases.fallback_used,
    })
    local interactionEntry = values.interactionState.entry
    if interactionEntry then
        interactionEntry = readonly({
            lines = readonlyArray(interactionEntry.lines),
            exclusion_lines = readonlyArray(interactionEntry.exclusion_lines),
            debug_lines = readonlyArray(interactionEntry.debug_lines),
        })
    end
    values.interactionState = readonly({
        status = values.interactionState.status,
        reason = values.interactionState.reason,
        fallback_used = values.interactionState.fallback_used == true,
        entry = interactionEntry,
        lines = readonlyArray(values.interactionState.lines),
        exclusion_lines = readonlyArray(values.interactionState.exclusion_lines),
        debug_lines = readonlyArray(values.interactionState.debug_lines),
    })
    values.capabilities = readonlyArray(values.capabilities)
    values.availability = readonly(values.availability)
    return readonly(values)
end

local function copyCounts(source)
    local result = {}
    for key, value in pairs(source or {}) do result[key] = value end
    return result
end

function ViewModel.getInstrumentation()
    return {
        enabled = instrumentationEnabled,
        fromItemCalls = metrics.fromItemCalls,
        methodAttempts = metrics.methodAttempts,
        methodSuccesses = metrics.methodSuccesses,
        groupAttempts = copyCounts(metrics.groupAttempts),
        groupSuccesses = copyCounts(metrics.groupSuccesses),
        groupSkips = copyCounts(metrics.groupSkips),
        staticCacheHits = metrics.staticCacheHits,
        staticCacheMisses = metrics.staticCacheMisses,
        capabilityHintBuilds = metrics.capabilityHintBuilds,
        methodListAllocations = metrics.methodListAllocations,
    }
end

function ViewModel.resetInstrumentation()
    metrics = newMetrics()
end

function ViewModel.setInstrumentationEnabled(enabled)
    instrumentationEnabled = enabled == true
    ViewModel.resetInstrumentation()
end

function ViewModel.ensure(itemOrModel)
    if ViewModel.isViewModel(itemOrModel) then return itemOrModel end
    return ViewModel.fromItem(itemOrModel)
end

return ViewModel
