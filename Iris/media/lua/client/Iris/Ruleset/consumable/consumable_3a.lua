--[[
    consumable_3a.lua - 식품 (Food)
    
    필수 증거: Type=Food AND HungerChange exists (with guard)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Consumable.3-A.FoodHunger",
        when = Ast.allOf({
            Ast.eq("Type", "Food"),
            Ast.has("HungerChange"),
        }),
        add = { "Consumable.3-A" },
        reason = "EvidenceTable:Consumable.3-A.FoodHungerChange",
    },
}
