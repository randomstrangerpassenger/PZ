--[[
    combat_2c.lua - 단둔기 (Short Blunt)
    
    필수 증거: Type=Weapon AND Categories contains Blunt AND NOT TwoHandWeapon
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-C.ShortBlunt",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.contains("Categories", "Blunt"),
            Ast.not_has("TwoHandWeapon"),
        }),
        add = { "Combat.2-C" },
        reason = "EvidenceTable:Combat.2-C.BluntOneHand",
    },
}
