--[[
    combat_2i.lua - 산탄총 (Shotguns)
    
    필수 증거: Type=Weapon AND SubCategory=Firearm AND 산탄총 탄약 타입
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-I.Shotgun",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.eq("SubCategory", "Firearm"),
            Ast.eq_ammoType("Base.ShotgunShells"),
        }),
        add = { "Combat.2-I" },
        reason = "EvidenceTable:Combat.2-I.AmmoTypeShotgun",
    },
}
