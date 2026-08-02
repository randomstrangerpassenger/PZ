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

function Array.copy(values)
    local result = {}
    for index, value in ipairs(values or {}) do
        result[index] = value
    end
    return result
end

return Array
