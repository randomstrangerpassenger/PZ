--[[
    tool_1e.lua - 농업/채집 (Farming/Foraging)
    
    필수 증거: Recipe role+category(Farming)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-E.RecipeFarming",
        when = Ast.anyOf({
            Ast.recipe_matches({ role = "keep", category = "Farming" }),
            Ast.recipe_matches({ role = "require", category = "Farming" }),
        }),
        add = { "Tool.1-E" },
        reason = "EvidenceTable:Tool.1-E.RecipeFarming",
    },
}
