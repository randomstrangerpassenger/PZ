-- Combines engine facts, Iris indexes, Layer 3, and interaction facts.
local Assembler = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local FactReader = require("Iris/UI/Detail/IrisItemFactReader")
local Layer3DisplayFormatter = require("Iris/UI/Layer3/IrisLayer3DisplayFormatter")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")

local instrumentationEnabled = false
local metrics = { fromItemCalls = 0, staticCacheHits = 0, staticCacheMisses = 0 }

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

local function readonlyFacts(group)
    local result = {}
    for fieldName, valueFact in pairs(group or {}) do
        result[fieldName] = readonly({
            state = valueFact.state,
            value = valueFact.value,
            method = valueFact.method,
        })
    end
    return readonly(result)
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
            (value.status == "available" or value.status == "verified_empty" or
                value.status == "fault") then
            return value
        end
        return {
            status = "fault", reason = "status_lookup_failed", fallback_used = false,
            entry = nil, lines = {}, exclusion_lines = {}, debug_lines = {},
        }
    end
    local legacy = safeUseCaseCall(
        UseCases,
        "getUseCaseLines",
        fullType,
        { lines = {}, debug_lines = {} }
    )
    local lines = legacy.lines or {}
    return {
        status = #lines > 0 and "available" or "fault",
        reason = "status_api_unavailable",
        fallback_used = true,
        entry = nil,
        lines = lines,
        exclusion_lines = {},
        debug_lines = legacy.debug_lines or {},
    }
end

local function layer3Payload(fullType, locale)
    local ok, renderer = safeRequire("Iris/Data/layer3_renderer")
    if not ok or not renderer or not renderer.getText or not fullType then
        return { available=false, adoptionState="unavailable", publishState=nil, raw=nil, display=nil }
    end
    local publishState = renderer.getPublishState and renderer.getPublishState(fullType) or nil
    local callOk, raw = ProtectedCall.data(function()
        return renderer.getText(fullType, { locale=locale })
    end)
    if not callOk or not raw or raw == "" then
        return {
            available=false,
            adoptionState=publishState or "unavailable",
            publishState=publishState,
            raw=nil,
            display=nil,
        }
    end
    return {
        available=true,
        adoptionState=publishState or "public_legacy",
        publishState=publishState,
        raw=raw,
        display=Layer3DisplayFormatter.format(raw),
    }
end

function Assembler.copyArray(values)
    local result = {}
    local index = 1
    while values and values[index] ~= nil do
        result[index] = values[index]
        index = index + 1
    end
    return result
end

function Assembler.arrayLength(values)
    local index = 1
    while values and values[index] ~= nil do index = index + 1 end
    return index - 1
end

function Assembler.isViewModel(value)
    return type(value) == "table" and value.__irisItemDetailViewModel == true
end

function Assembler.fromItem(item)
    if not item then return nil end
    if instrumentationEnabled then
        metrics.fromItemCalls = metrics.fromItemCalls + 1
        metrics.staticCacheMisses = metrics.staticCacheMisses + 1
    end

    local apiOk, IrisAPI = safeRequire("Iris/IrisAPI")
    if not apiOk then IrisAPI = nil end
    local facts = FactReader.read(item)
    local fullType = FactReader.value(facts.identity.fullType)
    local itemType = FactReader.value(facts.identity.itemType)
    local interactionState = safeInteractionState(IrisAPI and IrisAPI.UseCases, fullType)
    local useCaseData = {
        lines = interactionState.lines or {},
        debug_lines = interactionState.debug_lines or {},
        status = interactionState.status,
        reason = interactionState.reason,
        fallback_used = interactionState.fallback_used == true,
    }
    local capabilities = safeUseCaseCall(
        IrisAPI and IrisAPI.UseCases,
        "getCapabilities",
        fullType,
        {}
    )
    local Index = IrisAPI and IrisAPI.Index
    local locale = TranslationResolver.getLangKey("EN")
    local layer3 = layer3Payload(fullType, locale)
    local value = FactReader.value
    local values = {
        __irisItemDetailViewModel = true,
        sourceItem = item,
        locale = locale,
        fullType = fullType,
        displayName = FactReader.value(facts.identity.displayName),
        moduleName = FactReader.value(facts.identity.moduleName),
        itemType = itemType,
        weight = value(facts.core.weight),
        category = value(facts.core.category),
        subcategory = value(facts.core.subcategory),
        tags = sortedTags(IrisAPI, item),
        food = {}, weapon = {}, literature = {}, moveable = {},
        factStates = facts,
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
    for _, group in ipairs({ "food", "weapon", "literature", "moveable" }) do
        for fieldName, fieldFact in pairs(facts[group]) do
            values[group][fieldName] = value(fieldFact)
        end
    end
    values.availability = {
        food = facts.applicability.food == "known_capability",
        weapon = facts.applicability.weapon == "known_capability",
        literature = facts.applicability.literature == "known_capability",
        moveable = facts.applicability.moveable == "known_capability",
        layer3 = layer3.available,
        useCases = #(useCaseData.lines or {}) > 0 or #(useCaseData.debug_lines or {}) > 0,
        capabilities = #capabilities > 0,
    }
    values.revision = tostring(fullType) .. "|" .. tostring(locale)

    values.tags = readonlyArray(values.tags)
    for _, group in ipairs({ "food", "weapon", "literature", "moveable" }) do
        values[group] = readonly(values[group])
    end
    values.factStates = readonly({
        core = readonlyFacts(facts.core),
        identity = readonlyFacts(facts.identity),
        food = readonlyFacts(facts.food),
        weapon = readonlyFacts(facts.weapon),
        literature = readonlyFacts(facts.literature),
        moveable = readonlyFacts(facts.moveable),
        applicability = readonly(facts.applicability),
    })
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
    values.interactionState = readonly({
        status = values.interactionState.status,
        reason = values.interactionState.reason,
        fallback_used = values.interactionState.fallback_used == true,
        entry = values.interactionState.entry,
        lines = readonlyArray(values.interactionState.lines),
        exclusion_lines = readonlyArray(values.interactionState.exclusion_lines),
        debug_lines = readonlyArray(values.interactionState.debug_lines),
    })
    values.capabilities = readonlyArray(values.capabilities)
    values.availability = readonly(values.availability)
    return readonly(values)
end

function Assembler.ensure(itemOrModel)
    if Assembler.isViewModel(itemOrModel) then return itemOrModel end
    return Assembler.fromItem(itemOrModel)
end

function Assembler.getInstrumentation()
    local reader = FactReader.getInstrumentation()
    return {
        enabled = instrumentationEnabled,
        fromItemCalls = metrics.fromItemCalls,
        staticCacheHits = metrics.staticCacheHits,
        staticCacheMisses = metrics.staticCacheMisses,
        methodAttempts = reader.methodAttempts,
        methodSuccesses = reader.methodSuccesses,
        knownFacts = reader.known,
        unknownFacts = reader.unknown,
        notApplicableFacts = reader.notApplicable,
        groupAttempts = {}, groupSuccesses = {}, groupSkips = {},
        capabilityHintBuilds = 0, methodListAllocations = 0,
    }
end

function Assembler.resetInstrumentation()
    metrics = { fromItemCalls = 0, staticCacheHits = 0, staticCacheMisses = 0 }
    FactReader.resetInstrumentation()
end

function Assembler.setInstrumentationEnabled(enabled)
    instrumentationEnabled = enabled == true
    metrics = { fromItemCalls = 0, staticCacheHits = 0, staticCacheMisses = 0 }
    FactReader.setInstrumentationEnabled(instrumentationEnabled)
end

return Assembler
