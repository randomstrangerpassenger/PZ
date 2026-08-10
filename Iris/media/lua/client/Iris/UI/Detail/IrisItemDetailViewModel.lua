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

local function groupApplicable(item, methodNames, group, category, itemType)
    local hints = capabilityHints(category, itemType)
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
    local useCaseData = safeUseCaseCall(IrisAPI and IrisAPI.UseCases, "getUseCaseLines", fullType, {lines={},debug_lines={}})
    local capabilities = safeUseCaseCall(IrisAPI and IrisAPI.UseCases, "getCapabilities", fullType, {})
    local Index = IrisAPI and IrisAPI.Index
    local layer3 = layer3Payload(fullType)
    local itemType = ItemAccess.getType(item)
    local weight = read(item, {"getActualWeight", "getWeight"}, "core")
    local category = read(item, {"getDisplayCategory", "getCategory"}, "core")
    local subcategory = read(item, {"getSubCategory"}, "core")
    local foodMethods = {
        "getHungerChange", "getThirstChange", "getStressChange",
        "getBoredomChange", "getCalories",
    }
    local weaponMethods = {
        "getMinDamage", "getMaxDamage", "getMinRange", "getMaxRange",
        "getCriticalChance", "getConditionMax",
    }
    local literatureMethods = {
        "getNumberOfPages", "getSkillTrained", "getLvlSkillTrained",
        "getNumLevelsTrained",
    }
    local moveableMethods = {
        "getCapacity", "getLightStrength", "isWaterproof", "getInsulation",
    }
    local foodApplicable = groupApplicable(item, foodMethods, "food", category, itemType)
    local weaponApplicable = groupApplicable(item, weaponMethods, "weapon", category, itemType)
    local literatureApplicable = groupApplicable(item, literatureMethods, "literature", category, itemType)
    local moveableApplicable = groupApplicable(item, moveableMethods, "moveable", category, itemType)

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
            hunger = readIfApplicable(foodApplicable, item, {"getHungerChange"}, "food"),
            thirst = readIfApplicable(foodApplicable, item, {"getThirstChange"}, "food"),
            stress = readIfApplicable(foodApplicable, item, {"getStressChange"}, "food"),
            boredom = readIfApplicable(foodApplicable, item, {"getBoredomChange"}, "food"),
            calories = readIfApplicable(foodApplicable, item, {"getCalories"}, "food"),
        },
        weapon = {
            minDamage = readIfApplicable(weaponApplicable, item, {"getMinDamage"}, "weapon"),
            maxDamage = readIfApplicable(weaponApplicable, item, {"getMaxDamage"}, "weapon"),
            minRange = readIfApplicable(weaponApplicable, item, {"getMinRange"}, "weapon"),
            maxRange = readIfApplicable(weaponApplicable, item, {"getMaxRange"}, "weapon"),
            criticalChance = readIfApplicable(weaponApplicable, item, {"getCriticalChance"}, "weapon"),
            conditionMax = readIfApplicable(weaponApplicable, item, {"getConditionMax"}, "weapon"),
        },
        literature = {
            numberOfPages = readIfApplicable(literatureApplicable, item, {"getNumberOfPages"}, "literature"),
            skillTrained = readIfApplicable(literatureApplicable, item, {"getSkillTrained"}, "literature"),
            level = readIfApplicable(literatureApplicable, item, {"getLvlSkillTrained"}, "literature"),
            levelCount = readIfApplicable(literatureApplicable, item, {"getNumLevelsTrained"}, "literature"),
        },
        moveable = {
            capacity = readIfApplicable(moveableApplicable, item, {"getCapacity"}, "moveable"),
            lightStrength = readIfApplicable(moveableApplicable, item, {"getLightStrength"}, "moveable"),
            waterproof = readIfApplicable(moveableApplicable, item, {"isWaterproof"}, "moveable"),
            insulation = readIfApplicable(moveableApplicable, item, {"getInsulation"}, "moveable"),
        },
        layer3 = layer3,
        connections = {
            recipes = safeIndexCall(Index, "getRecipeConnectionsForItem", item) or {},
            moveables = safeIndexCall(Index, "getMoveablesInfoForItem", item),
            fixing = safeIndexCall(Index, "getFixingInfoForItem", item),
        },
        useCases = useCaseData,
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
