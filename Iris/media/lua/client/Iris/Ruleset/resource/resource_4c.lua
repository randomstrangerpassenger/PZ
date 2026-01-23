--[[
    resource_4c.lua - 의료 재료 (Medical Supplies)
    
    필수 증거: Tags contains Medical (소모품으로서의 재료)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Resource.4-C.MedicalTag",
        when = Ast.contains("Tags", "Medical"),
        add = { "Resource.4-C" },
        reason = "EvidenceTable:Resource.4-C.TagsMedical",
    },
}
