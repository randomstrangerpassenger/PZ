--[[
    combat_2d.lua - 장검류 (Long Blade)
    
    필수 증거: Type=Weapon AND Categories contains Blade AND TwoHandWeapon exists
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-D.LongBlade",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.contains("Categories", "Blade"),
            Ast.has("TwoHandWeapon"),
        }),
        add = { "Combat.2-D" },
        reason = "EvidenceTable:Combat.2-D.BladeTwoHand",
    },
}
