--[[
    NerveConfig.lua
    Nerve 모드 설정 파일
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
-- 로깅 설정
--------------------------------------------------------------------------------

NerveConfig.logging = {
    -- 파일에 로그 출력 (Zomboid/Lua/Nerve/nerve.log)
    toFile = true,
    
    -- 콘솔에도 로그 출력
    toConsole = true,
    
    -- 최소 로그 레벨 (1=DEBUG, 2=INFO, 3=WARN, 4=ERROR)
    minLevel = 2,
}

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
    -- [DEBUG] 임시로 활성화 - 문제 파악 후 false로 복구
    enabled = true,
    
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
-- Area 9: 네트워크/멀티 동기화 안정화
--------------------------------------------------------------------------------

--[[
    ┌──────────────────────────────────────────────────────────────────────────┐
    │ CONSTITUTION: Area 9 불변 전제 (Scope-Creep Prevention)                  │
    │                                                                          │
    │ 1. DEFAULT OFF                                                           │
    │ 2. 네트워크 경계에서만 (endpoints 폐쇄 allowlist)                         │
    │ 3. 대상/행동 모두 opt-in 분리                                             │
    │ 4. 동일 틱 한정 철수 + 다음 틱 자동 복귀                                  │
    │ 5. pcall만 (xpcall 가정 금지 - Kahlua)                                   │
    │ 6. 래핑/언래핑/무결성 체크 존재                                           │
    │ 7. 정책화 금지: Drop/Delay/Reorder/Queue/우선순위/가중치/복합조건 금지    │
    │                                                                          │
    │ [필수-1] tickId 갱신은 Area9TickCtx에서만                                 │
    │ [필수-2] endpoints는 네트워크 훅만 (OnTick/UI/렌더 추가 금지)             │
    │ [필수-3] incident 조건은 단일 플래그만 (추세/가중치/복합 금지)            │
    │ [필수-4] quarantine 키: 전역 금지, 확장은 config 명시로만                 │
    └──────────────────────────────────────────────────────────────────────────┘
]]

NerveConfig.area9 = {
    -- 활성화 여부 (DEFAULT OFF - 합헌)
    enabled = false,
    
    -- [필수-2] 허용 endpoints 폐쇄 목록 (네트워크 진입 훅만)
    -- OnTick/UI/렌더/기타 이벤트 추가 금지
    endpoints = {
        "OnClientCommand",
        "OnServerCommand",
    },
    
    -- 래핑 대상 이벤트 (endpoints와 동일하게 유지)
    targetEvents = {
        "OnClientCommand",
        "OnServerCommand",
    },
    
    -- opt-in 테이블 (대상/행동 분리)
    optIn = {
        -- 대상 opt-in
        guardedPcall = {},  -- guarded pcall 허용 대상
        quarantine = {},    -- quarantine 허용 대상
        skipDup = {},       -- duplicate 스킵 허용 대상 (Phase 5 이후 검토)
        
        -- 행동 opt-in (guards)
        guards = {},        -- guard 모드 활성화 대상
    },
    
    -- Shape Guard 설정
    shape = {
        -- 기본 모드: observe (hard fail도 증거만 남기고 통과)
        -- guard 모드: opt-in만 (hard fail→철수)
        defaultMode = "observe",
    },
    
    -- Quarantine 설정
    quarantine = {
        -- [필수-4] 기본 키: handler 단위 (전역 금지)
        keyMode = "handler",
        -- 확장 허용 목록 (config 명시로만)
        allowedExtensions = {},  -- 예: {"packetType", "connKey"}
    },
    
    -- Forensic 설정
    forensic = {
        -- 링버퍼 크기 (고정)
        ringBufferSize = 128,
        -- 출력 기본 OFF (수동 dump만)
        autoEmit = false,
    },
    
    -- Guarded pcall 설정
    guardedPcall = {
        -- tick당 budget (초과 시 callFast 복귀)
        tickBudget = 10,
        -- TTL (기본 1틱, 최대 3틱)
        defaultTTL = 1,
        maxTTL = 3,
    },
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
