--[[
    combat_2g.lua - 권총 (Handguns)
    
    필수 증거: Type=Weapon AND SubCategory=Firearm AND 권총 탄약 타입
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-G.Handgun",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.eq("SubCategory", "Firearm"),
            Ast.anyOf({
                Ast.eq_ammoType("Base.Bullets9mm"),
                Ast.eq_ammoType("Base.Bullets45"),
                Ast.eq_ammoType("Base.Bullets44"),
                Ast.eq_ammoType("Base.Bullets38"),
            }),
        }),
        add = { "Combat.2-G" },
        reason = "EvidenceTable:Combat.2-G.AmmoTypeHandgun",
    },
}
