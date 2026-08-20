-- Stable lookup facade. The pointer keeps this index on the public data generation.
local current = require("Iris/Data/IrisLayer3DataCurrent")
assert(current.schema_version == "iris_layer3_generation_pointer_v1")
return require(current.index_module)
