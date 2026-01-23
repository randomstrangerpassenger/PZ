--[[
    iris_ruleset.lua - Ruleset 엔트리 포인트
    
    디렉토리 스캔 금지.
    파일 추가 시 반드시 여기에 명시적 등록.
    require 루트: 상대 경로 기준 (Iris/Ruleset/...)
    
    로드 순서: allowlist → validator → 이 파일
]]

return {
    -- Tool (10개)
    require "Iris/Ruleset/tool/tool_1a",
    require "Iris/Ruleset/tool/tool_1b",
    require "Iris/Ruleset/tool/tool_1c",
    require "Iris/Ruleset/tool/tool_1d",
    require "Iris/Ruleset/tool/tool_1e",
    require "Iris/Ruleset/tool/tool_1f",
    require "Iris/Ruleset/tool/tool_1g",
    require "Iris/Ruleset/tool/tool_1h",
    require "Iris/Ruleset/tool/tool_1i",
    require "Iris/Ruleset/tool/tool_1j",  -- 빈 파일 (자동 분류 불가)
    
    -- Combat (12개)
    require "Iris/Ruleset/combat/combat_2a",
    require "Iris/Ruleset/combat/combat_2b",
    require "Iris/Ruleset/combat/combat_2c",
    require "Iris/Ruleset/combat/combat_2d",
    require "Iris/Ruleset/combat/combat_2e",
    require "Iris/Ruleset/combat/combat_2f",
    require "Iris/Ruleset/combat/combat_2g",
    require "Iris/Ruleset/combat/combat_2h",
    require "Iris/Ruleset/combat/combat_2i",
    require "Iris/Ruleset/combat/combat_2j",  -- 빈 파일 (투척/폭발)
    require "Iris/Ruleset/combat/combat_2k",  -- 빈 파일 (탄약)
    require "Iris/Ruleset/combat/combat_2l",
    
    -- Consumable (5개)
    require "Iris/Ruleset/consumable/consumable_3a",
    require "Iris/Ruleset/consumable/consumable_3b",
    require "Iris/Ruleset/consumable/consumable_3c",
    require "Iris/Ruleset/consumable/consumable_3d",
    require "Iris/Ruleset/consumable/consumable_3e",  -- 빈 파일 (약초)
    
    -- Resource (6개)
    require "Iris/Ruleset/resource/resource_4a",
    require "Iris/Ruleset/resource/resource_4b",
    require "Iris/Ruleset/resource/resource_4c",
    require "Iris/Ruleset/resource/resource_4d",  -- 빈 파일 (연료)
    require "Iris/Ruleset/resource/resource_4e",
    require "Iris/Ruleset/resource/resource_4f",
    
    -- Literature (4개)
    require "Iris/Ruleset/literature/literature_5a",
    require "Iris/Ruleset/literature/literature_5b",
    require "Iris/Ruleset/literature/literature_5c",
    require "Iris/Ruleset/literature/literature_5d",
    
    -- Wearable (8개)
    require "Iris/Ruleset/wearable/wearable_6a",
    require "Iris/Ruleset/wearable/wearable_6b",
    require "Iris/Ruleset/wearable/wearable_6c",
    require "Iris/Ruleset/wearable/wearable_6d",
    require "Iris/Ruleset/wearable/wearable_6e",
    require "Iris/Ruleset/wearable/wearable_6f",
    require "Iris/Ruleset/wearable/wearable_6g",
    require "Iris/Ruleset/wearable/wearable_6h",
}
