--[[
    tool_1f.lua - 의료 (Medical)
    
    필수 증거: CustomContextMenu(Stitch/RemoveBullet/RemoveGlass) 또는 Tags(Medical)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-F.Stitch",
        when = Ast.contains("CustomContextMenu", "Stitch"),
        add = { "Tool.1-F" },
        reason = "EvidenceTable:Tool.1-F.CustomContextMenuStitch",
    },
    {
        id = "Tool.1-F.RemoveBullet",
        when = Ast.contains("CustomContextMenu", "RemoveBullet"),
        add = { "Tool.1-F" },
        reason = "EvidenceTable:Tool.1-F.CustomContextMenuRemoveBullet",
    },
    {
        id = "Tool.1-F.RemoveGlass",
        when = Ast.contains("CustomContextMenu", "RemoveGlass"),
        add = { "Tool.1-F" },
        reason = "EvidenceTable:Tool.1-F.CustomContextMenuRemoveGlass",
    },
    {
        id = "Tool.1-F.MedicalTag",
        when = Ast.contains("Tags", "Medical"),
        add = { "Tool.1-F" },
        reason = "EvidenceTable:Tool.1-F.TagsMedical",
    },
}
