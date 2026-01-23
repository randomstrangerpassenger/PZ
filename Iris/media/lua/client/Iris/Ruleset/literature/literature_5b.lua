--[[
    literature_5b.lua - 레시피잡지 (Recipe Magazines)
    
    필수 증거: Type=Literature AND TeachedRecipes exists
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Literature.5-B.RecipeMagazine",
        when = Ast.allOf({
            Ast.eq("Type", "Literature"),
            Ast.has("TeachedRecipes"),
        }),
        add = { "Literature.5-B" },
        reason = "EvidenceTable:Literature.5-B.TeachedRecipes",
    },
}
