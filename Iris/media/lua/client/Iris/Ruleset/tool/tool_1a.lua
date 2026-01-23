--[[
    tool_1a.lua - 건설/제작 (Construction/Crafting)
    
    필수 증거: Recipe role(keep/require) AND category(Carpentry/MetalWelding/Masonry)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-A.RecipeCarpentry",
        when = Ast.anyOf({
            Ast.recipe_matches({ role = "keep", category = "Carpentry" }),
            Ast.recipe_matches({ role = "require", category = "Carpentry" }),
        }),
        add = { "Tool.1-A" },
        reason = "EvidenceTable:Tool.1-A.RecipeCarpentry",
    },
    {
        id = "Tool.1-A.RecipeMetalWelding",
        when = Ast.anyOf({
            Ast.recipe_matches({ role = "keep", category = "MetalWelding" }),
            Ast.recipe_matches({ role = "require", category = "MetalWelding" }),
        }),
        add = { "Tool.1-A" },
        reason = "EvidenceTable:Tool.1-A.RecipeMetalWelding",
    },
    {
        id = "Tool.1-A.RecipeMasonry",
        when = Ast.anyOf({
            Ast.recipe_matches({ role = "keep", category = "Masonry" }),
            Ast.recipe_matches({ role = "require", category = "Masonry" }),
        }),
        add = { "Tool.1-A" },
        reason = "EvidenceTable:Tool.1-A.RecipeMasonry",
    },
}
