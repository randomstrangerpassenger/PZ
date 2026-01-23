--[[
    literature_5d.lua - 일반 서적 (General Books)
    
    필수 증거: Type=Literature AND NOT (SkillTrained/TeachedRecipes/Map)
    잔여 분류 (다른 Literature 소분류에 해당하지 않는 경우)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Literature.5-D.GeneralBook",
        when = Ast.allOf({
            Ast.eq("Type", "Literature"),
            Ast.not_has("SkillTrained"),
            Ast.not_has("TeachedRecipes"),
            Ast.not_has("Map"),
        }),
        add = { "Literature.5-D" },
        reason = "EvidenceTable:Literature.5-D.GeneralLiterature",
    },
}
