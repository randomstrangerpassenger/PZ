--[[
    Area9Guard.lua
    CONSTITUTION 가드 - Echo 분석 구조 침투 방지
    
    ┌──────────────────────────────────────────────────────────────────────────┐
    │ ❌ FORBIDDEN: Area 9에서 절대 사용 금지                                   │
    │                                                                          │
    │ [Echo급 분석 구조]                                                        │
    │   - TrendAnalysis, TrendDirection                                        │
    │   - QualityScore, getQualityScore()                                      │
    │   - BottleneckDetector                                                   │
    │   - Priority 계산, priority 필드                                         │
    │   - Ratio 기반 판정                                                      │
    │   - weight/가중치 기반 결정                                              │
    │                                                                          │
    │ [Echo 모듈 참조]                                                          │
    │   - require "Echo/..."                                                   │
    │   - Echo.* 전역 참조                                                     │
    │                                                                          │
    │ [정책화 패턴]                                                             │
    │   - 복합 조건 (A and B and C)으로 행동 결정                               │
    │   - 추세/비율/빈도 기반 판정                                             │
    │   - 시계열 분석                                                          │
    │   - 자동 분석기                                                          │
    │                                                                          │
    │ [근거]                                                                    │
    │   - Philosophy.md: Hub & Spoke (모듈 간 직접 참조 금지)                  │
    │   - 7번 가이드: 포렌식은 "근거만 남기고, 폐기 가능한 수준"               │
    │   - 필수-3: incident 조건은 단일 플래그만                                │
    └──────────────────────────────────────────────────────────────────────────┘
    
    ✅ ALLOWED: Area 9에서 허용되는 것
    
    - 단일 플래그 체크 (hasIncident, isQuarantined)
    - 정수 enum (categoryId, reasonCode)
    - tick-local 카운터 (wipe 필수)
    - 고정 크기 링버퍼 (정수만)
    - observe/guard 모드 (opt-in)
]]

--------------------------------------------------------------------------------
-- Area9Guard 모듈
--------------------------------------------------------------------------------

local Area9Guard = {}

-- 금지 키워드 (코드 리뷰/린트용)
Area9Guard.FORBIDDEN_KEYWORDS = {
    -- Echo급 분석 구조
    "TrendAnalysis",
    "TrendDirection", 
    "QualityScore",
    "getQualityScore",
    "BottleneckDetector",
    "Priority",
    "priority",
    "Ratio",
    "weight",
    
    -- Echo 모듈 참조
    "Echo.",
    "require.*Echo",
    
    -- 정책화 패턴
    "analyze",
    "analysis",
    "detector",
    "timeSeries",
    "longTerm",
    "cumulative",
}

-- 허용 패턴 (Area 9에서 안전한 것)
Area9Guard.ALLOWED_PATTERNS = {
    "hasIncident",
    "isQuarantined",
    "isPassthrough",
    "categoryId",
    "reasonCode",
    "tickId",
    "scopeKey",
    "ringBuffer",
    "enum",
}

-- 위반 체크 (디버그/테스트용)
-- @param codeString: 검사할 코드 문자열
-- @return: { violations: table, isClean: bool }
function Area9Guard.checkViolations(codeString)
    local violations = {}
    
    for _, keyword in ipairs(Area9Guard.FORBIDDEN_KEYWORDS) do
        if string.find(codeString, keyword) then
            table.insert(violations, keyword)
        end
    end
    
    return {
        violations = violations,
        isClean = #violations == 0,
    }
end

-- 경고 메시지 출력
function Area9Guard.warnIfViolation(moduleName, codeString)
    local result = Area9Guard.checkViolations(codeString)
    
    if not result.isClean then
        local NerveUtils = NerveUtils or { warn = print }
        NerveUtils.warn("[Area9Guard] CONSTITUTION VIOLATION in " .. moduleName)
        for _, v in ipairs(result.violations) do
            NerveUtils.warn("  - Forbidden keyword: " .. v)
        end
        return false
    end
    
    return true
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Guard = Area9Guard

return Area9Guard
