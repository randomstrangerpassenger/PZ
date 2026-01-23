--[[
    consumable_3b.lua - 음료 (Beverage)
    
    필수 증거: 
    - Type=Food AND ThirstChange exists
    - Type=Drainable AND ThirstChange exists (Drainable 가드 적용)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Consumable.3-B.FoodThirst",
        when = Ast.allOf({
            Ast.eq("Type", "Food"),
            Ast.has("ThirstChange"),
        }),
        add = { "Consumable.3-B" },
        reason = "EvidenceTable:Consumable.3-B.FoodThirstChange",
    },
    {
        id = "Consumable.3-B.DrainableThirst",
        when = Ast.allOf({
            Ast.eq("Type", "Drainable"),
            Ast.has("ThirstChange"),  -- Drainable 가드: ThirstChange 필수
        }),
        add = { "Consumable.3-B" },
        reason = "EvidenceTable:Consumable.3-B.DrainableThirstChange",
    },
}
