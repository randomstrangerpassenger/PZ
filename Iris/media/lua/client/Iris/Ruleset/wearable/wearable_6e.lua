--[[
    wearable_6e.lua - 신발 (Feet)
    
    필수 증거: Type=Clothing AND BodyLocation=Feet
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Wearable.6-E.Shoes",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Feet"),
        }),
        add = { "Wearable.6-E" },
        reason = "EvidenceTable:Wearable.6-E.BodyLocationFeet",
    },
}
