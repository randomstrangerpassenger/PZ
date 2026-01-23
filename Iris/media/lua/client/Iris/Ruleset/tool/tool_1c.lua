--[[
    tool_1c.lua - 정비 (Maintenance)
    
    필수 증거: Fixing.Fixer 또는 Recipe role+category(Mechanics)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-C.Fixer",
        when = Ast.fixing_role_eq("Fixer"),
        add = { "Tool.1-C" },
        reason = "EvidenceTable:Tool.1-C.Fixer",
    },
    {
        id = "Tool.1-C.RecipeMechanics",
        when = Ast.anyOf({
            Ast.recipe_matches({ role = "keep", category = "Mechanics" }),
            Ast.recipe_matches({ role = "require", category = "Mechanics" }),
        }),
        add = { "Tool.1-C" },
        reason = "EvidenceTable:Tool.1-C.RecipeMechanics",
    },
}
