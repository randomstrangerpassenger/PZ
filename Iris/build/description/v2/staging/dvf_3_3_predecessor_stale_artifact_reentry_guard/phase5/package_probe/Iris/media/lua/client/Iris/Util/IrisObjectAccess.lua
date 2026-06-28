--[[
    IrisObjectAccess.lua

    Generic protected Java/Kahlua object method access helpers.
]]

local IrisObjectAccess = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local unpackArgs = unpack or (table and table.unpack)

local function callMethod(method, target, args)
    if unpackArgs then
        return method(target, unpackArgs(args))
    end
    return method(target, args[1], args[2], args[3], args[4], args[5])
end

function IrisObjectAccess.call(target, methodName, ...)
    if not target or not methodName then
        return false, nil
    end

    local method = target[methodName]
    if not method then
        return false, nil
    end

    local args = {...}
    return ProtectedCall.engine(function()
        return callMethod(method, target, args)
    end)
end

function IrisObjectAccess.invokeMethod(target, methodName, fallback, ...)
    local ok, result = IrisObjectAccess.call(target, methodName, ...)
    if ok and result ~= nil then
        return result
    end
    return fallback
end

return IrisObjectAccess
