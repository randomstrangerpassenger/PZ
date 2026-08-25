-- The only Detail module allowed to call Project Zomboid item methods.
local IrisItemFactReader = {}

local ObjectAccess = require("Iris/Util/IrisObjectAccess")
local ItemAccess = require("Iris/Util/IrisItemAccess")

local METHODS = {
    weight = { "getActualWeight", "getWeight" },
    category = { "getDisplayCategory", "getCategory" },
    subcategory = { "getSubCategory" },
    hunger = { "getHungerChange" },
    thirst = { "getThirstChange" },
    stress = { "getStressChange" },
    boredom = { "getBoredomChange" },
    calories = { "getCalories" },
    minDamage = { "getMinDamage" },
    maxDamage = { "getMaxDamage" },
    minRange = { "getMinRange" },
    maxRange = { "getMaxRange" },
    criticalChance = { "getCriticalChance" },
    conditionMax = { "getConditionMax" },
    numberOfPages = { "getNumberOfPages" },
    skillTrained = { "getSkillTrained" },
    level = { "getLvlSkillTrained" },
    levelCount = { "getNumLevelsTrained" },
    capacity = { "getCapacity" },
    lightStrength = { "getLightStrength" },
    waterproof = { "isWaterproof" },
    insulation = { "getInsulation" },
}

local GROUP_FIELDS = {
    food = { "hunger", "thirst", "stress", "boredom", "calories" },
    weapon = { "minDamage", "maxDamage", "minRange", "maxRange", "criticalChance", "conditionMax" },
    literature = { "numberOfPages", "skillTrained", "level", "levelCount" },
    moveable = { "capacity", "lightStrength", "waterproof", "insulation" },
}

local instrumentationEnabled = false
local metrics = nil

local function newMetrics()
    return {
        reads = 0,
        capabilityHintBuilds = 0,
        methodAttempts = 0,
        methodSuccesses = 0,
        known = 0,
        unknown = 0,
        notApplicable = 0,
    }
end

metrics = newMetrics()

local function record(state)
    if not instrumentationEnabled then return end
    if state == "known" then
        metrics.known = metrics.known + 1
    elseif state == "unknown" then
        metrics.unknown = metrics.unknown + 1
    else
        metrics.notApplicable = metrics.notApplicable + 1
    end
end

local function fact(state, value, methodName)
    record(state)
    return { state = state, value = value, method = methodName }
end

local function readKnownOrUnknown(item, methodNames)
    for _, methodName in ipairs(methodNames or {}) do
        if instrumentationEnabled then metrics.methodAttempts = metrics.methodAttempts + 1 end
        local ok, value = ObjectAccess.call(item, methodName)
        if ok and value ~= nil then
            if instrumentationEnabled then metrics.methodSuccesses = metrics.methodSuccesses + 1 end
            return fact("known", value, methodName)
        end
    end
    return fact("unknown", nil, nil)
end

local function hasMethod(item, methodName)
    local ok, method = pcall(function() return item[methodName] end)
    return ok and method ~= nil
end

local function groupApplicable(item, group, hints)
    if hints[group] then return true end
    for _, fieldName in ipairs(GROUP_FIELDS[group]) do
        for _, methodName in ipairs(METHODS[fieldName]) do
            if hasMethod(item, methodName) then return true end
        end
    end
    return false
end

local function capabilityHints(category, itemType)
    if instrumentationEnabled then
        metrics.capabilityHintBuilds = metrics.capabilityHintBuilds + 1
    end
    local hints = {}
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

local function readGroup(item, group, applicable)
    local result = {}
    for _, fieldName in ipairs(GROUP_FIELDS[group]) do
        if applicable then
            result[fieldName] = readKnownOrUnknown(item, METHODS[fieldName])
        else
            result[fieldName] = fact("not_applicable", nil, nil)
        end
    end
    return result
end

function IrisItemFactReader.read(item)
    if instrumentationEnabled then metrics.reads = metrics.reads + 1 end
    if not item then return nil end
    local fullType = ItemAccess.getFullType(item)
    local itemType = ItemAccess.getType(item)
    local moduleName = ItemAccess.getModuleName(item)
    local core = {
        weight = readKnownOrUnknown(item, METHODS.weight),
        category = readKnownOrUnknown(item, METHODS.category),
        subcategory = readKnownOrUnknown(item, METHODS.subcategory),
    }
    local hints = capabilityHints(core.category.value, itemType)
    local result = {
        identity = {
            fullType = fact(fullType ~= nil and "known" or "unknown", fullType, "ItemAccess.getFullType"),
            displayName = fact("known", ItemAccess.getDisplayName(item, fullType or "Unknown"), "ItemAccess.getDisplayName"),
            moduleName = fact(moduleName ~= nil and "known" or "unknown",
                moduleName, "ItemAccess.getModuleName"),
            itemType = fact(itemType ~= nil and "known" or "unknown", itemType, "ItemAccess.getType"),
        },
        core = core,
        applicability = {},
    }
    for _, group in ipairs({ "food", "weapon", "literature", "moveable" }) do
        local applicable = groupApplicable(item, group, hints)
        result.applicability[group] = applicable and "known_capability" or "not_applicable"
        result[group] = readGroup(item, group, applicable)
    end
    return result
end

function IrisItemFactReader.value(valueFact)
    if valueFact and valueFact.state == "known" then return valueFact.value end
    return nil
end

function IrisItemFactReader.getInstrumentation()
    local result = { enabled = instrumentationEnabled }
    for name, value in pairs(metrics) do result[name] = value end
    return result
end

function IrisItemFactReader.setInstrumentationEnabled(enabled)
    instrumentationEnabled = enabled == true
    metrics = newMetrics()
end

function IrisItemFactReader.resetInstrumentation()
    metrics = newMetrics()
end

return IrisItemFactReader
