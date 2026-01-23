--[[
    combat_2h.lua - 소총 (Rifles)
    
    필수 증거: Type=Weapon AND SubCategory=Firearm AND 소총 탄약 타입
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-H.Rifle",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.eq("SubCategory", "Firearm"),
            Ast.anyOf({
                Ast.eq_ammoType("Base.223Bullets"),
                Ast.eq_ammoType("Base.308Bullets"),
                Ast.eq_ammoType("Base.556Bullets"),
            }),
        }),
        add = { "Combat.2-H" },
        reason = "EvidenceTable:Combat.2-H.AmmoTypeRifle",
    },
}
