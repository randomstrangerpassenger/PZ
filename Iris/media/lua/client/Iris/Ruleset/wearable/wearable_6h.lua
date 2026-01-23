--[[
    wearable_6h.lua - 액세서리 (Accessories)
    
    필수 증거: Type=Clothing AND BodyLocation in (Neck, Eyes)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Wearable.6-H.Neck",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Neck"),
        }),
        add = { "Wearable.6-H" },
        reason = "EvidenceTable:Wearable.6-H.BodyLocationNeck",
    },
    {
        id = "Wearable.6-H.Eyes",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Eyes"),
        }),
        add = { "Wearable.6-H" },
        reason = "EvidenceTable:Wearable.6-H.BodyLocationEyes",
    },
}
