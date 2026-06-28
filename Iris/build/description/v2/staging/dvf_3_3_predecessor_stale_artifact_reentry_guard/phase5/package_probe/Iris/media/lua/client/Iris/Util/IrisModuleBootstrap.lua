--[[
    IrisModuleBootstrap.lua - shared runtime module bootstrap helpers

    Keeps module-local safeRequire and logger fallback setup in one place.
]]

local IrisModuleBootstrap = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire

local function noop()
end

local function makePrintFallback(level)
    return function(message)
        print("[Iris][" .. level .. "] " .. tostring(message))
    end
end

function IrisModuleBootstrap.create(options)
    options = options or {}

    local loggerOk, logger = safeRequire("Iris/Util/IrisLogger")
    if not loggerOk then
        logger = nil
    end

    local debugFallback = noop
    local infoFallback = options.printFallback and makePrintFallback("INFO") or noop
    local warnFallback = options.printFallback and makePrintFallback("WARN") or noop
    local errorFallback = options.printFallback and makePrintFallback("ERROR") or noop

    return {
        safeRequire = safeRequire,
        debug = logger and logger.debug or debugFallback,
        info = logger and logger.info or infoFallback,
        warn = logger and logger.warn or warnFallback,
        logError = logger and logger.error or errorFallback,
        error = logger and logger.error or errorFallback,
    }
end

IrisModuleBootstrap.safeRequire = safeRequire

return IrisModuleBootstrap
