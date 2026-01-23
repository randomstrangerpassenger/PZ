--[[
    combat_2b.lua - 장둔기 (Long Blunt)
    
    필수 증거: Type=Weapon AND Categories contains Blunt AND TwoHandWeapon exists
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-B.LongBlunt",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.contains("Categories", "Blunt"),
            Ast.has("TwoHandWeapon"),
        }),
        add = { "Combat.2-B" },
        reason = "EvidenceTable:Combat.2-B.BluntTwoHand",
    },
}
