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
}

local cache = {}
local warned = {}

function StaticData.get(key)
    local definition = DEFINITIONS[key]
    if not definition then
        return nil
    end

    if cache[key] ~= nil then
        return cache[key]
    end

    local ok, result = safeRequire(definition.module)
    if ok then
        cache[key] = result
        return result
    end

    if definition.warn and not warned[key] then
        warned[key] = true
        warn(definition.warn .. ": " .. tostring(result))
    end
    return nil
end

function StaticData.arrayContains(values, value)
    return Array.contains(values, value)
end

return StaticData
