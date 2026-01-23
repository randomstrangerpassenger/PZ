--[[
    literature_5c.lua - 지도 (Maps)
    
    필수 증거: Type=Map 또는 (Type=Literature AND Map exists)
]]

local Ast = require "Iris/Rules/engine/IrisAst"

return {
    {
        id = "Literature.5-C.TypeMap",
        when = Ast.eq("Type", "Map"),
        add = { "Literature.5-C" },
        reason = "EvidenceTable:Literature.5-C.TypeMap",
    },
    {
        id = "Literature.5-C.LiteratureMap",
        when = Ast.allOf({
            Ast.eq("Type", "Literature"),
            Ast.has("Map"),
        }),
        add = { "Literature.5-C" },
        reason = "EvidenceTable:Literature.5-C.LiteratureMap",
    },
}
