--[[
    tool_1d.lua - 조리 (Cooking)
    
    필수 증거: Tags contains Cookware 또는 Recipe role+category(Cooking)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-D.Cookware",
        when = Ast.contains("Tags", "Cookware"),
        add = { "Tool.1-D" },
        reason = "EvidenceTable:Tool.1-D.TagsCookware",
    },
    {
        id = "Tool.1-D.RecipeCooking",
        when = Ast.recipe_matches({ role = "keep", category = "Cooking" }),
        add = { "Tool.1-D" },
        reason = "EvidenceTable:Tool.1-D.RecipeKeepCooking",
    },
}
