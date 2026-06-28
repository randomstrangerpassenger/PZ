--[[
    IrisLogger.lua - Iris runtime logger

    Debug output is gated by IrisConfig.DEBUG. Config lookup is lazy so this
    module can be required early without creating a hard initialization cycle.
]]

local IrisLogger = {}
local safeRequire = require("Iris/Util/IrisRequire").safeRequire

local configChecked = false
local debugEnabled = false

local function resolveDebugEnabled()
    if configChecked then
        return debugEnabled
    end

    configChecked = true
    local ok, config = safeRequire("Iris/IrisConfig")
    if ok and config and config.DEBUG == true then
        debugEnabled = true
    else
        debugEnabled = false
    end
    return debugEnabled
end

local function emit(level, message)
    print("[Iris][" .. level .. "] " .. tostring(message))
end

function IrisLogger.debug(message)
    if resolveDebugEnabled() then
        emit("DEBUG", message)
    end
end

function IrisLogger.isDebugEnabled()
    return resolveDebugEnabled()
end

function IrisLogger.info(message)
    emit("INFO", message)
end

function IrisLogger.warn(message)
    emit("WARN", message)
end

function IrisLogger.error(message)
    emit("ERROR", message)
end

return IrisLogger
