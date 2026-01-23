--[[
    literature_5a.lua - 스킬북 (Skill Books)
    
    필수 증거: Type=Literature AND SkillTrained exists
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Literature.5-A.SkillBook",
        when = Ast.allOf({
            Ast.eq("Type", "Literature"),
            Ast.has("SkillTrained"),
        }),
        add = { "Literature.5-A" },
        reason = "EvidenceTable:Literature.5-A.SkillTrained",
    },
}
