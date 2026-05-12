--[[
    IrisProtectedCall.lua - shared protected-call boundary

    Runtime-facing modules route guarded engine/UI/data calls through this
    helper so error-boundary policy stays centralized.
]]

local IrisProtectedCall = {}

local configChecked = false
local devLogEnabled = false

local function isDevLogEnabled()
    if configChecked then
        return devLogEnabled
    end

    configChecked = true
    local ok, config = pcall(require, "Iris/IrisConfig")
    devLogEnabled = ok and config and config.DEBUG == true
    return devLogEnabled
end

local function emitDevFailure(boundary, err)
    if isDevLogEnabled() then
        print("[Iris][DEBUG] ProtectedCall." .. tostring(boundary) .. " failed: " .. tostring(err))
    end
end

local function callBoundary(boundary, fn, ...)
    local ok, result = pcall(fn, ...)
    if not ok then
        emitDevFailure(boundary, result)
    end
    return ok, result
end

function IrisProtectedCall.call(fn, ...)
    return pcall(fn, ...)
end

function IrisProtectedCall.require(moduleName)
    return callBoundary("require", require, moduleName)
end

function IrisProtectedCall.engine(fn, ...)
    return callBoundary("engine", fn, ...)
end

function IrisProtectedCall.ui(fn, ...)
    return callBoundary("ui", fn, ...)
end

function IrisProtectedCall.data(fn, ...)
    return callBoundary("data", fn, ...)
end

function IrisProtectedCall.compat(fn, ...)
    return callBoundary("compat", fn, ...)
end

return IrisProtectedCall
