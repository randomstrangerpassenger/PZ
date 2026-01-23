--[[
    wearable_6c.lua - 하의 (Legs)
    
    필수 증거: Type=Clothing AND BodyLocation in (Legs, Groin)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Wearable.6-C.Legs",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Legs"),
        }),
        add = { "Wearable.6-C" },
        reason = "EvidenceTable:Wearable.6-C.BodyLocationLegs",
    },
    {
        id = "Wearable.6-C.Groin",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Groin"),
        }),
        add = { "Wearable.6-C" },
        reason = "EvidenceTable:Wearable.6-C.BodyLocationGroin",
    },
}
