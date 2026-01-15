--[[
    NerveConfig.lua
    Nerve 모드 설정 파일
    
    v0.2 - Area 5 제거됨 (폐기)
]]

NerveConfig = NerveConfig or {}

--------------------------------------------------------------------------------
-- 기본 설정
--------------------------------------------------------------------------------

-- Pulse 모드 ID (대소문자/폴더명 변경 대비)
NerveConfig.pulseModId = "Pulse"

-- 디버그 모드 (로그 상세 출력)
NerveConfig.debug = false

--------------------------------------------------------------------------------
-- Area 6: 이벤트 디스패치 안정화
--------------------------------------------------------------------------------

--[[
    ┌──────────────────────────────────────────────────────────────────────────┐
    │ CONSTITUTION: Area 6 Exclusions (Scope-Creep Prevention)                 │
    │                                                                          │
    │ ❌ Cascade/Depth as triggers (depth is evidence-only)                    │
    │ ❌ Cooldown recovery, consecutive-error counters, time-based cooldowns   │
    │ ❌ Performance KPIs (<1ms, <1MB, etc.) in verification                   │
    │ ❌ Nerve deciding exception re-propagation (follow vanilla, log only)    │
    │                                                                          │
    │ ✅ Triggers: Only (1) same-tick self-recursion, (2) exception            │
    │ ✅ Action: Only same-tick pass-through (withdrawal)                      │
    │ ✅ Evidence: Lazy collection ONLY after incident triggers                │
    └──────────────────────────────────────────────────────────────────────────┘
]]

NerveConfig.area6 = {
    -- 활성화 여부
    -- [SEALED] DEFAULT OFF: 바닐라 동일 보장 (헌법 준수)
    enabled = false,
    
    -- 래핑 대상 이벤트 목록 (최소 5~10개로 제한)
    -- "재현된 폭주가 확인된" 이벤트만 추가
    -- 과다 등록 금지: 전 이벤트 래핑은 그 자체가 리스크
    targetEvents = {
        "OnTick",
        "OnTickEvenPaused",
        "OnContainerUpdate",
        "OnInventoryUpdate",
        "OnObjectAdded",
        "OnObjectRemoved",
        -- 추후 관측 데이터 기반으로 확장
    },
    
    -- [REMOVED] deduplicateEvents: Drop 금지 원칙 위반 (중복 제거 = Drop)
    -- deduplicateEvents = {...} 삭제됨
    
    -- 트리거 설정 (2개 고정)
    triggers = {
        -- 트리거 1: same-tick self-recursion
        reentry = {
            enabled = true,
        },
        -- 트리거 2: exception (xpcall 격리)
        exception = {
            enabled = true,
        },
        -- [SEALED] 추가 트리거 금지
    },
    
    -- 액션 설정 (1개 고정)
    action = {
        -- 유일한 액션: 동일 틱 철수 (pass-through)
        type = "SAME_TICK_PASSTHROUGH",  -- 변경 금지
    },
    
    -- 증거 수집 설정 (incident 후 Lazy만)
    evidence = {
        -- 활성화 여부
        enabled = true,
        -- [SEALED] 상시 계측 금지 (incident 후에만)
        incidentGatedOnly = true,
    },
    
    -- seenThisTick 키 폭증 방지
    maxSeenEntriesPerTick = 1000,
    
    -- [REMOVED] 정책성 컴포넌트 설정 제거 (헌법 준수)
    -- sustainedPressure, earlyExit, cascadeGuard.strict는 더 이상 사용되지 않음
}

--------------------------------------------------------------------------------
-- Fail-soft 설정
--------------------------------------------------------------------------------

NerveConfig.failsoft = {
    -- 최대 연속 오류 횟수 (초과 시 컴포넌트 비활성화)
    maxErrors = 3,
    -- 비활성화 후 cooldown (ms)
    cooldownMs = 10000,  -- 10초
}

--------------------------------------------------------------------------------
-- 타이밍 설정
--------------------------------------------------------------------------------

NerveConfig.timing = {
    -- 느린 틱 판정 기준 (ms)
    slowThresholdMs = 50,  -- 20fps 미만
}

--------------------------------------------------------------------------------
-- 유틸리티
--------------------------------------------------------------------------------

-- 설정값 안전 조회
function NerveConfig.get(path, default)
    local parts = {}
    for part in string.gmatch(path, "[^.]+") do
        table.insert(parts, part)
    end
    
    local current = NerveConfig
    for _, part in ipairs(parts) do
        if type(current) ~= "table" then
            return default
        end
        current = current[part]
    end
    
    if current == nil then
        return default
    end
    return current
end

return NerveConfig
