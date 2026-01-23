--[[
    tool_1b.lua - 분해/개방 (Disassembly/Opening)
    
    필수 증거: Moveables.ToolDefinition 등록 또는 Recipe.GetItemTypes.CanOpener
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-B.MoveablesItemId",
        when = Ast.moveables_itemId_registered(),
        add = { "Tool.1-B" },
        reason = "EvidenceTable:Tool.1-B.MoveablesItemId",
    },
    {
        id = "Tool.1-B.MoveablesTag",
        when = Ast.moveables_tag_in({ "Crowbar", "SharpKnife", "Hammer", "Screwdriver", "Saw", "Wrench" }),
        add = { "Tool.1-B" },
        reason = "EvidenceTable:Tool.1-B.MoveablesTag",
    },
    {
        id = "Tool.1-B.CanOpener",
        when = Ast.recipe_inGetItemTypes("CanOpener"),
        add = { "Tool.1-B" },
        reason = "EvidenceTable:Tool.1-B.CanOpener",
    },
}
