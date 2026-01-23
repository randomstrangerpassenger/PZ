--[[
    wearable_6b.lua - 상의 (Torso)
    
    필수 증거: Type=Clothing AND BodyLocation in (Torso, Torso_Upper, Torso_Lower)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Wearable.6-B.TorsoMain",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Torso"),
        }),
        add = { "Wearable.6-B" },
        reason = "EvidenceTable:Wearable.6-B.BodyLocationTorso",
    },
    {
        id = "Wearable.6-B.TorsoUpper",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Torso_Upper"),
        }),
        add = { "Wearable.6-B" },
        reason = "EvidenceTable:Wearable.6-B.BodyLocationTorsoUpper",
    },
    {
        id = "Wearable.6-B.TorsoLower",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Torso_Lower"),
        }),
        add = { "Wearable.6-B" },
        reason = "EvidenceTable:Wearable.6-B.BodyLocationTorsoLower",
    },
}
