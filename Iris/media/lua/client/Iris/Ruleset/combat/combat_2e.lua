--[[
    combat_2e.lua - 단검류 (Short Blade)
    
    필수 증거: Type=Weapon AND Categories contains Blade AND NOT TwoHandWeapon
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-E.ShortBlade",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.contains("Categories", "Blade"),
            Ast.not_has("TwoHandWeapon"),
        }),
        add = { "Combat.2-E" },
        reason = "EvidenceTable:Combat.2-E.BladeOneHand",
    },
}
