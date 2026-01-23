--[[
    tool_1i.lua - 통신 (Communication)
    
    필수 증거: Type = Radio
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-I.Radio",
        when = Ast.eq("Type", "Radio"),
        add = { "Tool.1-I" },
        reason = "EvidenceTable:Tool.1-I.TypeRadio",
    },
}
