--[[
    CategoryPresentationOrder.lua

    Neutral presentation projection shared by Browser and IrisDesc consumers.
    This module owns display ordering only; it does not decide taxonomy
    membership or classification meaning.
]]

local CategoryPresentationOrder = {}

local BROWSER_CATEGORY_ORDER = {
    "Tool",
    "Combat",
    "Consumable",
    "Resource",
    "Literature",
    "Wearable",
    "Furniture",
    "Vehicle",
    "Misc",
}

local DESCRIPTION_PRIORITY = {
    Tool = 1,
    Combat = 2,
    Consumable = 3,
    Resource = 4,
    Literature = 5,
    Wearable = 6,
}

function CategoryPresentationOrder.getBrowserCategoryOrder()
    local result = {}
    for index, category in ipairs(BROWSER_CATEGORY_ORDER) do
        result[index] = category
    end
    return result
end

function CategoryPresentationOrder.getDescriptionPriority(category)
    return DESCRIPTION_PRIORITY[category] or 999
end

return CategoryPresentationOrder
