-- Focused variant-group index. The generated current payload is empty; a
-- pre-existing supported IrisData global may seed compatibility groups.
local groups = {}
if type(IrisData) == "table" and type(IrisData.ItemGroups) == "table" then
    groups = IrisData.ItemGroups
end
return groups
