-- Stable public facade. IrisLayer3DataCurrent is the only generation switch.
local current = require("Iris/Data/IrisLayer3DataCurrent")
assert(current.schema_version == "iris_layer3_generation_pointer_v1")

local data = {}
for _, moduleName in ipairs(current.chunk_modules) do
    local chunk = require(moduleName)
    for fullType, entry in pairs(chunk) do
        data[fullType] = entry
    end
end

IrisLayer3Data = data
return data
