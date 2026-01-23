--[[
    combat_2f.lua - 창류 (Spears)
    
    필수 증거: Type=Weapon AND (Categories contains Spear OR SubCategory = Spear)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-F.Spear",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.anyOf({
                Ast.contains("Categories", "Spear"),
                Ast.eq("SubCategory", "Spear"),
            }),
        }),
        add = { "Combat.2-F" },
        reason = "EvidenceTable:Combat.2-F.Spear",
    },
}
