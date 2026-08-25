-- Supported legacy table alias backed by focused generated current modules.
local Classifications = require("Iris/Data/IrisClassifications")
local ItemGroups = require("Iris/Data/IrisVariantGroups")

local adapter = type(IrisData) == "table" and IrisData or {}
adapter.Classifications = Classifications
adapter.ItemGroups = ItemGroups
IrisData = adapter

return adapter
