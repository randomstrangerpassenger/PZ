--[[
    IrisBrowserCategoryIndex.lua

    Category and subcategory metadata for the Iris browser. This module keeps
    the canonical category list in one table and derives the legacy lookup
    tables that BrowserData exposes for compatibility.
]]

local IrisBrowserCategoryIndex = {}

IrisBrowserCategoryIndex.CATEGORY_DEFINITIONS = {
    {
        name = "Tool",
        key = "Iris_Cat_Tool",
        fallback = "Tool",
        subcategories = {
            "1-A", "1-B", "1-C", "1-D", "1-E", "1-F", "1-G", "1-H", "1-I", "1-J", "1-K", "1-L",
        },
    },
    {
        name = "Combat",
        key = "Iris_Cat_Combat",
        fallback = "Combat",
        subcategories = {
            "2-A", "2-B", "2-C", "2-D", "2-E", "2-F", "2-G", "2-H", "2-I", "2-J", "2-K", "2-L",
        },
    },
    {
        name = "Consumable",
        key = "Iris_Cat_Consumable",
        fallback = "Consumable",
        subcategories = {
            "3-A", "3-B", "3-C", "3-D", "3-E",
        },
    },
    {
        name = "Resource",
        key = "Iris_Cat_Resource",
        fallback = "Resource",
        subcategories = {
            "4-A", "4-B", "4-C", "4-D", "4-E", "4-F",
        },
    },
    {
        name = "Literature",
        key = "Iris_Cat_Literature",
        fallback = "Literature",
        subcategories = {
            "5-A", "5-B", "5-C", "5-D",
        },
    },
    {
        name = "Wearable",
        key = "Iris_Cat_Wearable",
        fallback = "Wearable",
        subcategories = {
            "6-A", "6-B", "6-C", "6-D", "6-E", "6-F", "6-G",
        },
    },
    {
        name = "Furniture",
        key = "Iris_Cat_Furniture",
        fallback = "Furniture",
        subcategories = {
            "7-A",
        },
    },
    {
        name = "Vehicle",
        key = "Iris_Cat_Vehicle",
        fallback = "Vehicle",
        subcategories = {
            "8-A", "8-B",
        },
    },
    {
        name = "Misc",
        key = "Iris_Cat_Misc",
        fallback = "Misc",
        subcategories = {
            "9-A",
        },
    },
}

IrisBrowserCategoryIndex.SUBCATEGORY_KEYS = {
    ["1-A"] = { key = "Iris_Sub_1A", fallback = "Construction/Crafting" },
    ["1-B"] = { key = "Iris_Sub_1B", fallback = "Disassembly/Opening" },
    ["1-C"] = { key = "Iris_Sub_1C", fallback = "Maintenance" },
    ["1-D"] = { key = "Iris_Sub_1D", fallback = "Cooking" },
    ["1-E"] = { key = "Iris_Sub_1E", fallback = "Farming/Foraging" },
    ["1-F"] = { key = "Iris_Sub_1F", fallback = "Medical" },
    ["1-G"] = { key = "Iris_Sub_1G", fallback = "Trapping" },
    ["1-H"] = { key = "Iris_Sub_1H", fallback = "Light/Ignition" },
    ["1-I"] = { key = "Iris_Sub_1I", fallback = "Communication" },
    ["1-J"] = { key = "Iris_Sub_1J", fallback = "Electrical" },
    ["1-K"] = { key = "Iris_Sub_1K", fallback = "Storage Containers" },
    ["1-L"] = { key = "Iris_Sub_1L", fallback = "Bags" },
    ["2-A"] = { key = "Iris_Sub_2A", fallback = "Axes" },
    ["2-B"] = { key = "Iris_Sub_2B", fallback = "Long Blunt" },
    ["2-C"] = { key = "Iris_Sub_2C", fallback = "Short Blunt" },
    ["2-D"] = { key = "Iris_Sub_2D", fallback = "Long Blades" },
    ["2-E"] = { key = "Iris_Sub_2E", fallback = "Short Blades" },
    ["2-F"] = { key = "Iris_Sub_2F", fallback = "Spears" },
    ["2-G"] = { key = "Iris_Sub_2G", fallback = "Pistols" },
    ["2-H"] = { key = "Iris_Sub_2H", fallback = "Rifles" },
    ["2-I"] = { key = "Iris_Sub_2I", fallback = "Shotguns" },
    ["2-J"] = { key = "Iris_Sub_2J", fallback = "Explosives/Thrown" },
    ["2-K"] = { key = "Iris_Sub_2K", fallback = "Ammunition" },
    ["2-L"] = { key = "Iris_Sub_2L", fallback = "Gun Parts" },
    ["3-A"] = { key = "Iris_Sub_3A", fallback = "Food" },
    ["3-B"] = { key = "Iris_Sub_3B", fallback = "Drinks" },
    ["3-C"] = { key = "Iris_Sub_3C", fallback = "Medicine" },
    ["3-D"] = { key = "Iris_Sub_3D", fallback = "Luxury Items" },
    ["3-E"] = { key = "Iris_Sub_3E", fallback = "Herbs" },
    ["4-A"] = { key = "Iris_Sub_4A", fallback = "Construction Material" },
    ["4-B"] = { key = "Iris_Sub_4B", fallback = "Cooking Ingredients" },
    ["4-C"] = { key = "Iris_Sub_4C", fallback = "Medical Supplies" },
    ["4-D"] = { key = "Iris_Sub_4D", fallback = "Fuel" },
    ["4-E"] = { key = "Iris_Sub_4E", fallback = "Electronics" },
    ["4-F"] = { key = "Iris_Sub_4F", fallback = "Misc Materials" },
    ["5-A"] = { key = "Iris_Sub_5A", fallback = "Skill Books" },
    ["5-B"] = { key = "Iris_Sub_5B", fallback = "Recipe Magazines" },
    ["5-C"] = { key = "Iris_Sub_5C", fallback = "Maps" },
    ["5-D"] = { key = "Iris_Sub_5D", fallback = "General Books" },
    ["6-A"] = { key = "Iris_Sub_6A", fallback = "Hats/Helmets" },
    ["6-B"] = { key = "Iris_Sub_6B", fallback = "Tops" },
    ["6-C"] = { key = "Iris_Sub_6C", fallback = "Bottoms" },
    ["6-D"] = { key = "Iris_Sub_6D", fallback = "Gloves" },
    ["6-E"] = { key = "Iris_Sub_6E", fallback = "Footwear" },
    ["6-F"] = { key = "Iris_Sub_6F", fallback = "Backpacks" },
    ["6-G"] = { key = "Iris_Sub_6G", fallback = "Accessories" },
    ["7-A"] = { key = "Iris_Sub_7A", fallback = "Moveables" },
    ["8-A"] = { key = "Iris_Sub_8A", fallback = "Drivetrain" },
    ["8-B"] = { key = "Iris_Sub_8B", fallback = "Body/Parts" },
    ["9-A"] = { key = "Iris_Sub_9A", fallback = "Miscellaneous" },
}

IrisBrowserCategoryIndex.CATEGORY_ORDER = {}
IrisBrowserCategoryIndex.CATEGORY_KEYS = {}
IrisBrowserCategoryIndex.SUBCATEGORY_MAP = {}

for _, definition in ipairs(IrisBrowserCategoryIndex.CATEGORY_DEFINITIONS) do
    table.insert(IrisBrowserCategoryIndex.CATEGORY_ORDER, definition.name)
    IrisBrowserCategoryIndex.CATEGORY_KEYS[definition.name] = {
        key = definition.key,
        fallback = definition.fallback,
    }

    local subcategories = {}
    for _, subcategory in ipairs(definition.subcategories or {}) do
        table.insert(subcategories, subcategory)
    end
    IrisBrowserCategoryIndex.SUBCATEGORY_MAP[definition.name] = subcategories
end

function IrisBrowserCategoryIndex.getCategoryLabel(catName, translate)
    local entry = IrisBrowserCategoryIndex.CATEGORY_KEYS[catName]
    if entry then
        if translate then
            return translate(entry.key, entry.fallback)
        end
        return entry.fallback
    end
    return catName
end

function IrisBrowserCategoryIndex.getSubcategoryLabel(subCode, translate)
    local entry = IrisBrowserCategoryIndex.SUBCATEGORY_KEYS[subCode]
    if entry then
        if translate then
            return translate(entry.key, entry.fallback)
        end
        return entry.fallback
    end
    return subCode
end

return IrisBrowserCategoryIndex
