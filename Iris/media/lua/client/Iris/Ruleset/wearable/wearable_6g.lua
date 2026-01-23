--[[
    wearable_6g.lua - 힙색 (FannyPack/Waist)
    
    필수 증거: Type=Clothing AND BodyLocation in (FannyPack, Belt, BeltExtra, Waist)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Wearable.6-G.FannyPack",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("FannyPack"),
        }),
        add = { "Wearable.6-G" },
        reason = "EvidenceTable:Wearable.6-G.BodyLocationFannyPack",
    },
    {
        id = "Wearable.6-G.Belt",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Belt"),
        }),
        add = { "Wearable.6-G" },
        reason = "EvidenceTable:Wearable.6-G.BodyLocationBelt",
    },
    {
        id = "Wearable.6-G.BeltExtra",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("BeltExtra"),
        }),
        add = { "Wearable.6-G" },
        reason = "EvidenceTable:Wearable.6-G.BodyLocationBeltExtra",
    },
    {
        id = "Wearable.6-G.Waist",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Waist"),
        }),
        add = { "Wearable.6-G" },
        reason = "EvidenceTable:Wearable.6-G.BodyLocationWaist",
    },
}
