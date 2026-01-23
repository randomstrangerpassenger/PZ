--[[
    wearable_6f.lua - 배낭 (Back)
    
    필수 증거: Type=Clothing AND BodyLocation=Back
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Wearable.6-F.Backpack",
        when = Ast.allOf({
            Ast.eq("Type", "Clothing"),
            Ast.eq_bodyLocation("Back"),
        }),
        add = { "Wearable.6-F" },
        reason = "EvidenceTable:Wearable.6-F.BodyLocationBack",
    },
}
