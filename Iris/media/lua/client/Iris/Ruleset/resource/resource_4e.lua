--[[
    resource_4e.lua - 전자부품 (Electronics)
    
    필수 증거: Recipe role=input AND category(Electronics/Electrical)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Resource.4-E.InputElectronics",
        when = Ast.recipe_matches({ role = "input", category = "Electronics" }),
        add = { "Resource.4-E" },
        reason = "EvidenceTable:Resource.4-E.RecipeInputElectronics",
    },
    {
        id = "Resource.4-E.InputElectrical",
        when = Ast.recipe_matches({ role = "input", category = "Electrical" }),
        add = { "Resource.4-E" },
        reason = "EvidenceTable:Resource.4-E.RecipeInputElectrical",
    },
}
