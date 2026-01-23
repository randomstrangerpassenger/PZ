--[[
    consumable_3c.lua - 의약품 (Medicine)
    
    필수 증거: CustomContextMenu(Disinfect/Bandage/Splint/CleanWound)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Consumable.3-C.Disinfect",
        when = Ast.contains("CustomContextMenu", "Disinfect"),
        add = { "Consumable.3-C" },
        reason = "EvidenceTable:Consumable.3-C.CustomContextMenuDisinfect",
    },
    {
        id = "Consumable.3-C.Bandage",
        when = Ast.contains("CustomContextMenu", "Bandage"),
        add = { "Consumable.3-C" },
        reason = "EvidenceTable:Consumable.3-C.CustomContextMenuBandage",
    },
    {
        id = "Consumable.3-C.Splint",
        when = Ast.contains("CustomContextMenu", "Splint"),
        add = { "Consumable.3-C" },
        reason = "EvidenceTable:Consumable.3-C.CustomContextMenuSplint",
    },
    {
        id = "Consumable.3-C.CleanWound",
        when = Ast.contains("CustomContextMenu", "CleanWound"),
        add = { "Consumable.3-C" },
        reason = "EvidenceTable:Consumable.3-C.CustomContextMenuCleanWound",
    },
}
