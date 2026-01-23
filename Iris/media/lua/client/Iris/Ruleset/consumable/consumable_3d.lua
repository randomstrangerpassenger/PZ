--[[
    consumable_3d.lua - 기호품 (Luxury)
    
    필수 증거: Alcoholic=true 또는 (Type=Food AND StressChange/UnhappyChange exists)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Consumable.3-D.Alcoholic",
        when = Ast.eq("Alcoholic", true),
        add = { "Consumable.3-D" },
        reason = "EvidenceTable:Consumable.3-D.Alcoholic",
    },
    {
        id = "Consumable.3-D.FoodStress",
        when = Ast.allOf({
            Ast.eq("Type", "Food"),
            Ast.has("StressChange"),
        }),
        add = { "Consumable.3-D" },
        reason = "EvidenceTable:Consumable.3-D.FoodStressChange",
    },
    {
        id = "Consumable.3-D.FoodUnhappy",
        when = Ast.allOf({
            Ast.eq("Type", "Food"),
            Ast.has("UnhappyChange"),
        }),
        add = { "Consumable.3-D" },
        reason = "EvidenceTable:Consumable.3-D.FoodUnhappyChange",
    },
}
