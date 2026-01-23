--[[
    tool_1g.lua - 포획 (Trapping/Fishing)
    
    필수 증거: Recipe role+category(Trapping/Fishing)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-G.RecipeTrapping",
        when = Ast.anyOf({
            Ast.recipe_matches({ role = "keep", category = "Trapping" }),
            Ast.recipe_matches({ role = "require", category = "Trapping" }),
        }),
        add = { "Tool.1-G" },
        reason = "EvidenceTable:Tool.1-G.RecipeTrapping",
    },
    {
        id = "Tool.1-G.RecipeFishing",
        when = Ast.anyOf({
            Ast.recipe_matches({ role = "keep", category = "Fishing" }),
            Ast.recipe_matches({ role = "require", category = "Fishing" }),
        }),
        add = { "Tool.1-G" },
        reason = "EvidenceTable:Tool.1-G.RecipeFishing",
    },
}
