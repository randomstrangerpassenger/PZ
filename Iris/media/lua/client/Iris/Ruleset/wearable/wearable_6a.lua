--[[
    wearable_6a.lua - 모자/헬멧 (Head)
    
    필수 증거: Type=Clothing AND BodyLocation=Head
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Wearable.6-A.HeadGear",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Head"),
        }),
        add = { "Wearable.6-A" },
        reason = "EvidenceTable:Wearable.6-A.BodyLocationHead",
    },
}
