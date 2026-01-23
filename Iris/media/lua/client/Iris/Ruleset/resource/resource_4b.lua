--[[
    resource_4b.lua - 조리 재료 (Cooking Ingredients)
    
    필수 증거: Recipe role=input AND category=Cooking
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Resource.4-B.InputCooking",
        when = Ast.recipe_matches({ role = "input", category = "Cooking" }),
        add = { "Resource.4-B" },
        reason = "EvidenceTable:Resource.4-B.RecipeInputCooking",
    },
}
