--[[
    Area6Guard.lua
    Area 6 헌법 경계선 봉인 모듈
    
    v1.0 - Phase 0: Constitution Enforcement
    
    핵심 역할:
    - 금지선 상수 선언 (외부 노출 없음)
    - 개발 중 헌법 위반 키워드 탐지 (dev-only 안전장치)
    - 스코프 확장 방지 (코드 레벨 봉인)
    
    [CONSTITUTION - IMMUTABLE]
    ✅ Triggers: Only (1) same-tick self-recursion, (2) exception
    ✅ Action: Only same-tick pass-through
    ✅ Evidence: Lazy collection ONLY after incident
    
    ❌ Cascade/Depth as triggers
    ❌ Cooldown, consecutive-error counters, time-based recovery
    ❌ Performance KPIs (<1ms, <1MB) as verification
    ❌ Nerve deciding exception re-propagation
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area6Guard 모듈
--------------------------------------------------------------------------------

local Area6Guard = {}

--------------------------------------------------------------------------------
-- [SEALED] 상수 정의 (내부 전용, 외부 수정 불가)
--------------------------------------------------------------------------------

-- 유일한 액션 (변경 금지)
Area6Guard.ACTION = {
    PASSTHROUGH_ONLY = "SAME_TICK_PASSTHROUGH",
}

-- 트리거 타입 (2개 고정)
Area6Guard.TRIGGER = {
    REENTRY = "reentry",        -- same-tick self-recursion
    EXCEPTION = "exception",    -- xpcall 격리 대상
}

-- 사건(incident) 타입
Area6Guard.INCIDENT = {
    REENTRY = "reentry",
    ERROR = "error",
}

-- 설치 상태
Area6Guard.INSTALL_STATE = {
    APPLIED = "Applied",        -- 정상 설치
    PARTIAL = "Partial",        -- 일부만 설치
    BYPASSED = "Bypassed",      -- 충돌로 철수
}

--------------------------------------------------------------------------------
-- [DEV-ONLY] 헌법 위반 키워드 감지 (개발자 안전장치)
--------------------------------------------------------------------------------

-- 금지 키워드 목록 (Echo 침범 방지)
local FORBIDDEN_KEYWORDS = {
    -- 시간 측정 관련
    "averageMs",
    "avgMs",
    "totalMs",
    "histogram",
    "history",
    "timeSeries",
    "cumulative",
    
    -- 정책 관련
    "priority",
    "importance",
    "weight",
    "threshold",
    "cooldown",
    "cooldownMs",
    "backoff",
    
    -- Drop/Delay 관련
    "drop",
    "skip",
    "delay",
    "defer",
    "reorder",
    "queue",
}

-- 문자열에서 금지 키워드 탐지
-- @param str: 검사할 문자열
-- @return: {found: boolean, keywords: table}
function Area6Guard.checkForbiddenKeywords(str)
    if type(str) ~= "string" then
        return { found = false, keywords = {} }
    end
    
    local foundKeywords = {}
    local strLower = string.lower(str)
    
    for _, keyword in ipairs(FORBIDDEN_KEYWORDS) do
        if string.find(strLower, string.lower(keyword)) then
            table.insert(foundKeywords, keyword)
        end
    end
    
    if #foundKeywords > 0 then
        return { found = true, keywords = foundKeywords }
    end
    
    return { found = false, keywords = {} }
end

-- 테이블 키 검사 (개발 중 경고용)
-- @param tbl: 검사할 테이블
-- @param prefix: 로그 출력용 접두사
function Area6Guard.auditTableKeys(tbl, prefix)
    if type(tbl) ~= "table" then return end
    
    prefix = prefix or "unknown"
    
    for key, value in pairs(tbl) do
        local keyStr = tostring(key)
        local result = Area6Guard.checkForbiddenKeywords(keyStr)
        
        if result.found then
            NerveUtils.warn("[CONSTITUTION] Forbidden keyword in " .. prefix 
                .. "." .. keyStr .. ": " .. table.concat(result.keywords, ", "))
        end
        
        -- 중첩 테이블 재귀 검사 (1레벨만)
        if type(value) == "table" and prefix:find("%.") == nil then
            Area6Guard.auditTableKeys(value, prefix .. "." .. keyStr)
        end
    end
end

--------------------------------------------------------------------------------
-- 헌법 준수 검증 (초기화 시 1회 호출)
--------------------------------------------------------------------------------

function Area6Guard.validateConstitution()
    local issues = {}
    
    -- 1. NerveConfig.area6 검사
    if NerveConfig and NerveConfig.area6 then
        local cfg = NerveConfig.area6
        
        -- 트리거가 2개를 초과하면 위반
        if cfg.triggers then
            local triggerCount = 0
            for _ in pairs(cfg.triggers) do
                triggerCount = triggerCount + 1
            end
            if triggerCount > 2 then
                table.insert(issues, "Triggers exceed 2 (found " .. triggerCount .. ")")
            end
        end
        
        -- 액션이 PASSTHROUGH가 아니면 위반
        if cfg.action and cfg.action.type ~= Area6Guard.ACTION.PASSTHROUGH_ONLY then
            table.insert(issues, "Action is not PASSTHROUGH_ONLY")
        end
        
        -- evidence.incidentGatedOnly가 false면 위반 (상시 계측)
        if cfg.evidence and cfg.evidence.incidentGatedOnly == false then
            table.insert(issues, "Evidence is not incident-gated (constant measurement)")
        end
    end
    
    if #issues > 0 then
        NerveUtils.warn("==========================================")
        NerveUtils.warn("[CONSTITUTION VIOLATION]")
        for i, issue in ipairs(issues) do
            NerveUtils.warn("  " .. i .. ". " .. issue)
        end
        NerveUtils.warn("==========================================")
        return false
    end
    
    NerveUtils.debug("[CONSTITUTION] Validation passed")
    return true
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6Guard = Area6Guard

return Area6Guard
