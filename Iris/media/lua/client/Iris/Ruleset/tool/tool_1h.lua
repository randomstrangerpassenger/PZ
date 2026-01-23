--[[
    tool_1h.lua - 광원/점화 (Light/Ignition)
    
    필수 증거:
    - LightStrength/LightDistance + 가드(ActivatedItem/TorchCone)
    - TorchCone 단독
    - Tags(StartFire/Lighter)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Tool.1-H.LightWithGuard",
        when = Ast.anyOf({
            -- LightStrength + 가드
            Ast.allOf({
                Ast.has("LightStrength"),
                Ast.anyOf({
                    Ast.eq("ActivatedItem", true),
                    Ast.eq("TorchCone", true),
                }),
            }),
            -- LightDistance + 가드
            Ast.allOf({
                Ast.has("LightDistance"),
                Ast.anyOf({
                    Ast.eq("ActivatedItem", true),
                    Ast.eq("TorchCone", true),
                }),
            }),
            -- TorchCone 단독 허용
            Ast.eq("TorchCone", true),
        }),
        add = { "Tool.1-H" },
        reason = "EvidenceTable:Tool.1-H.LightFieldsGuarded",
    },
    {
        id = "Tool.1-H.StartFire",
        when = Ast.contains("Tags", "StartFire"),
        add = { "Tool.1-H" },
        reason = "EvidenceTable:Tool.1-H.TagsStartFire",
    },
    {
        id = "Tool.1-H.Lighter",
        when = Ast.contains("Tags", "Lighter"),
        add = { "Tool.1-H" },
        reason = "EvidenceTable:Tool.1-H.TagsLighter",
    },
}
