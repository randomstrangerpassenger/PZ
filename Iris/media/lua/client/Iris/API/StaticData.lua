--[[
    StaticData.lua - table-driven Iris static data loader

    Private helper for IrisAPI sub-facades. This module centralizes optional
    static data loading without becoming a public API surface.
]]

local StaticData = {}

local Array = require("Iris/Util/Array")
local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local warn = bootstrap.warn

local DEFINITIONS = {
    classifications = {
        module = "Iris/Data/IrisClassifications",
        warn = "[IrisAPI] IrisClassifications not found",
    },
    recipeIndex = {
        module = "Iris/Data/IrisRecipeIndex",
    },
    moveablesIndex = {
        module = "Iris/Data/IrisMoveablesIndex",
    },
    fixingIndex = {
        module = "Iris/Data/IrisFixingIndex",
    },
    contextOutcomes = {
        module = "Iris/Data/IrisContextOutcomes",
    },
    capabilities = {
        module = "Iris/Data/IrisCapabilities",
    },
    useCaseDescriptions = {
        module = "Iris/Data/IrisUseCaseDescriptions",
    },
    legacyData = {
        module = "Iris/Data/IrisData",
    },
}

local cache = {}
local warned = {}
local failures = {}

function StaticData.get(key)
    local definition = DEFINITIONS[key]
    if not definition then
        return nil
    end

    if cache[key] ~= nil then
        return cache[key]
    end
    if failures[key] ~= nil then
        return nil
    end

    local ok, result = safeRequire(definition.module)
    if ok then
        cache[key] = result
        failures[key] = nil
        return result
    end

    failures[key] = tostring(result)

    if definition.warn and not warned[key] then
        warned[key] = true
        warn(definition.warn .. ": " .. tostring(result))
    end
    return nil
end

--- Optional generated modules are session-stable; expose the cached reason so
--- callers and dev diagnostics can distinguish absent data from unknown keys.
function StaticData.getFailureReason(key)
    if not DEFINITIONS[key] then return "unknown_definition" end
    return failures[key]
end

--- Explicit dev/test reload hook. Production callers never retry on a tick.
function StaticData.reset(key)
    if key ~= nil then
        if not DEFINITIONS[key] then return false end
        cache[key] = nil
        failures[key] = nil
        warned[key] = nil
        return true
    end

    cache = {}
    failures = {}
    warned = {}
    return true
end

--- Compatibility-only loader for the historical IrisData global. New
--- consumers must use the focused generated modules above.
function StaticData.getLegacyIrisData()
    local loaded = StaticData.get("legacyData")
    if type(loaded) == "table" then return loaded end
    if type(IrisData) == "table" then return IrisData end
    return nil
end

function StaticData.arrayContains(values, value)
    return Array.contains(values, value)
end

return StaticData
