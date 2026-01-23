--[[
    resource_4a.lua - 건설 재료 (Construction Materials)
    
    필수 증거: Recipe role=input AND category(Carpentry/MetalWelding/Masonry)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Resource.4-A.InputCarpentry",
        when = Ast.recipe_matches({ role = "input", category = "Carpentry" }),
        add = { "Resource.4-A" },
        reason = "EvidenceTable:Resource.4-A.RecipeInputCarpentry",
    },
    {
        id = "Resource.4-A.InputMetalWelding",
        when = Ast.recipe_matches({ role = "input", category = "MetalWelding" }),
        add = { "Resource.4-A" },
        reason = "EvidenceTable:Resource.4-A.RecipeInputMetalWelding",
    },
    {
        id = "Resource.4-A.InputMasonry",
        when = Ast.recipe_matches({ role = "input", category = "Masonry" }),
        add = { "Resource.4-A" },
        reason = "EvidenceTable:Resource.4-A.RecipeInputMasonry",
    },
}
