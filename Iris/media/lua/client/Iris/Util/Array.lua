--[[
    Array.lua - small table-array helpers
]]

local Array = {}

function Array.contains(values, value)
    if not values then
        return false
    end

    for _, candidate in ipairs(values) do
        if candidate == value then
            return true
        end
    end
    return false
end

return Array
