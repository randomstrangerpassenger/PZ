--[[
    IrisRequire.lua - shared safe require helper
]]

local IrisRequire = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")

function IrisRequire.safeRequire(moduleName)
    return ProtectedCall.require(moduleName)
end

return IrisRequire
