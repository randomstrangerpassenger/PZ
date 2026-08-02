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

local function read(item, methodNames)
    return ObjectAccess.firstValue(item, methodNames, nil)
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

    local apiOk, IrisAPI = safeRequire("Iris/IrisAPI")
    if not apiOk then IrisAPI = nil end
    local fullType = ItemAccess.getFullType(item)
    local useCaseData = safeUseCaseCall(IrisAPI and IrisAPI.UseCases, "getUseCaseLines", fullType, {lines={},debug_lines={}})
    local capabilities = safeUseCaseCall(IrisAPI and IrisAPI.UseCases, "getCapabilities", fullType, {})
    local Index = IrisAPI and IrisAPI.Index
    local layer3 = layer3Payload(fullType)

    local values = {
        __irisItemDetailViewModel = true,
        sourceItem = item,
        locale = TranslationResolver.getLangKey("EN"),
        fullType = fullType,
        displayName = ItemAccess.getDisplayName(item, fullType or "Unknown"),
        moduleName = ItemAccess.getModuleName(item),
        itemType = ItemAccess.getType(item),
        weight = read(item, {"getActualWeight", "getWeight"}),
        category = read(item, {"getDisplayCategory", "getCategory"}),
        subcategory = read(item, {"getSubCategory"}),
        tags = sortedTags(IrisAPI, item),
        food = {
            hunger = read(item, {"getHungerChange"}),
            thirst = read(item, {"getThirstChange"}),
            stress = read(item, {"getStressChange"}),
            boredom = read(item, {"getBoredomChange"}),
            calories = read(item, {"getCalories"}),
        },
        weapon = {
            minDamage = read(item, {"getMinDamage"}),
            maxDamage = read(item, {"getMaxDamage"}),
            minRange = read(item, {"getMinRange"}),
            maxRange = read(item, {"getMaxRange"}),
            criticalChance = read(item, {"getCriticalChance"}),
            conditionMax = read(item, {"getConditionMax"}),
        },
        literature = {
            numberOfPages = read(item, {"getNumberOfPages"}),
            skillTrained = read(item, {"getSkillTrained"}),
            level = read(item, {"getLvlSkillTrained"}),
            levelCount = read(item, {"getNumLevelsTrained"}),
        },
        moveable = {
            capacity = read(item, {"getCapacity"}),
            lightStrength = read(item, {"getLightStrength"}),
            waterproof = read(item, {"isWaterproof"}),
            insulation = read(item, {"getInsulation"}),
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

function ViewModel.ensure(itemOrModel)
    if ViewModel.isViewModel(itemOrModel) then return itemOrModel end
    return ViewModel.fromItem(itemOrModel)
end

return ViewModel
