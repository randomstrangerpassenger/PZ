--[[
    combat_2l.lua - 총기부품 (Gun Parts)
    
    필수 증거: MountOn exists (총기 부품의 핵심 증거)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Combat.2-L.GunPart",
        when = Ast.has("MountOn"),
        add = { "Combat.2-L" },
        reason = "EvidenceTable:Combat.2-L.MountOnExists",
    },
}
