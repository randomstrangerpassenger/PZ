--[[
    combat_2a.lua - 도끼류 (Axes)
    
    필수 증거: Type=Weapon AND Categories contains Axe
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-A.Axe",
        when = Ast.allOf({
            Ast.eq("Type", "Weapon"),
            Ast.contains("Categories", "Axe"),
        }),
        add = { "Combat.2-A" },
        reason = "EvidenceTable:Combat.2-A.CategoriesAxe",
    },
}
