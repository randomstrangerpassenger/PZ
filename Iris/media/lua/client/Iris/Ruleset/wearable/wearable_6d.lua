--[[
    wearable_6d.lua - 장갑 (Hands)
    
    필수 증거: Type=Clothing AND BodyLocation=Hands
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Wearable.6-D.Gloves",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Hands"),
        }),
        add = { "Wearable.6-D" },
        reason = "EvidenceTable:Wearable.6-D.BodyLocationHands",
    },
}
