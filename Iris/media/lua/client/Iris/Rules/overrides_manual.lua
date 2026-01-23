--[[
    overrides_manual.lua - 수동 오버라이드
    
    자동 분류 불가 아이템 수동 태깅.
    add 키만 허용 (remove/replace/override 금지).
    
    사용 조건:
    - 바닐라/모드 데이터에 증거가 구조적으로 누락된 경우
    - Evidence Table이 "자동 분류 불가"로 명시한 소분류
]]

return {
    -- Tool.1-J (전력) — 자동 분류 불가
    ["Base.Generator"] = { add = { "Tool.1-J" } },
    
    -- Combat.2-J (투척/폭발) — 자동 분류 불가
    ["Base.Molotov"] = { add = { "Combat.2-J" } },
    ["Base.PipeBomb"] = { add = { "Combat.2-J" } },
    ["Base.SmokeBomb"] = { add = { "Combat.2-J" } },
    
    -- Combat.2-K (탄약) — 자동 분류 불가
    ["Base.Bullets9mm"] = { add = { "Combat.2-K" } },
    ["Base.Bullets45"] = { add = { "Combat.2-K" } },
    ["Base.Bullets44"] = { add = { "Combat.2-K" } },
    ["Base.Bullets38"] = { add = { "Combat.2-K" } },
    ["Base.223Bullets"] = { add = { "Combat.2-K" } },
    ["Base.308Bullets"] = { add = { "Combat.2-K" } },
    ["Base.556Bullets"] = { add = { "Combat.2-K" } },
    ["Base.ShotgunShells"] = { add = { "Combat.2-K" } },
    
    -- Consumable.3-E (약초) — 자동 분류 불가
    ["Base.Lemongrass"] = { add = { "Consumable.3-E" } },
    ["Base.Comfrey"] = { add = { "Consumable.3-E" } },
    
    -- Resource.4-D (연료) — 자동 분류 불가
    ["Base.PetrolCan"] = { add = { "Resource.4-D" } },
    ["Base.PropaneTank"] = { add = { "Resource.4-D" } },
}
