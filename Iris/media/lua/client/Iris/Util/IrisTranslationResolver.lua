--[[
    IrisTranslationResolver.lua

    Shared UI translation fallback resolver.
]]

local IrisTranslationResolver = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")

local loaderAttempted = false
local loader = nil

local function getLoader()
    if not loaderAttempted then
        loaderAttempted = true
        local ok, result = safeRequire("Iris/IrisTranslationLoader")
        if ok then
            loader = result
        end
    end
    return loader or IrisTranslationLoader
end

function IrisTranslationResolver.get(key, fallback)
    local translationLoader = getLoader()
    if translationLoader and translationLoader.get then
        local result = translationLoader.get(key, nil)
        if result and result ~= key then
            return result
        end
    end

    if getText and type(getText) == "function" then
        local ok, result = ProtectedCall.engine(getText, key)
        if ok and result and result ~= key then
            return result
        end
    end

    return fallback or key
end

function IrisTranslationResolver.getLangKey(fallback)
    local translationLoader = getLoader()
    if translationLoader and translationLoader.getLangKey then
        local result = translationLoader.getLangKey()
        if result then
            return result
        end
    end
    return fallback or "EN"
end

return IrisTranslationResolver
