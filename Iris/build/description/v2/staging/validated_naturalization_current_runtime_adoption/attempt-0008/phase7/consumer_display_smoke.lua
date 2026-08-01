package.path = "Iris/media/lua/client/?.lua;" .. package.path

local WikiSections = require("Iris/UI/Wiki/IrisWikiSections")

local function item(fullType)
    return { getFullType = function() return fullType end }
end

local keys = {
    "Base.223Box",
    "Base.223Bullets",
    "Base.Broom",
    "Base.LemonGrass",
    "Base.Lemongrass",
}

for _, key in ipairs(keys) do
    local value = WikiSections.renderLayer3Section(item(key))
    print(key .. "\t" .. (value or "__nil__"))
end
