--[[
    EventRecursionGuard.lua
    재귀/재진입 깊이 가드 (관측 전용)
    
    ┌──────────────────────────────────────────────────────────────────────────┐
    │ ⚠️ DEPRECATED - DO NOT USE                                              │
    │                                                                          │
    │ This module is superseded by Area6Reentry.lua                            │
    │ Kept only for backward compatibility. Will be removed in future version. │
    └──────────────────────────────────────────────────────────────────────────┘
    
    v0.3 - Pure Observation Mode (헌법 준수)
    
    핵심 원칙:
    - 항상 통과 (Drop 금지 원칙 준수)
    - 폭주 시 경고 로그만 출력
    - 틱 단위 중복은 더 이상 스킵하지 않음
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- EventRecursionGuard 모듈
--------------------------------------------------------------------------------

local EventRecursionGuard = {}

-- 상태
EventRecursionGuard.callStack = {}
EventRecursionGuard.maxDepthObserved = 0
EventRecursionGuard.blockCount = 0

-- 기본값
local DEFAULT_MAX_RECURSION = 5000

--------------------------------------------------------------------------------
-- 틱 시작 처리
--------------------------------------------------------------------------------

function EventRecursionGuard.onTickStart()
    -- 틱마다 콜스택 초기화
    NerveUtils.safeWipe(EventRecursionGuard.callStack)
end

--------------------------------------------------------------------------------
-- 진입 체크
--------------------------------------------------------------------------------

-- 이벤트 진입 체크
-- @param eventName: 이벤트 이름
-- @return: true (항상 통과 - 관측 전용)
function EventRecursionGuard.enter(eventName)
    local depth = (EventRecursionGuard.callStack[eventName] or 0) + 1
    EventRecursionGuard.callStack[eventName] = depth
    
    -- 최대 깊이 기록 (관측용)
    if depth > EventRecursionGuard.maxDepthObserved then
        EventRecursionGuard.maxDepthObserved = depth
    end
    
    -- 설정 조회
    local maxRecursion = NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.recursionGuard 
        and NerveConfig.area6.recursionGuard.maxDepth 
        or DEFAULT_MAX_RECURSION
    
    -- 폭주 감지 (관측 전용 - Drop 금지 원칙 준수)
    if depth >= maxRecursion then
        -- 경고 로그만 (차단 없음)
        NerveUtils.warn("RECURSION GUARD: " .. eventName 
            .. " depth=" .. depth .. "/" .. maxRecursion .. " (observe-only)")
        EventRecursionGuard.blockCount = EventRecursionGuard.blockCount + 1
    end
    
    return true  -- [FIX] 항상 통과 (Drop 금지 원칙)
end

--------------------------------------------------------------------------------
-- 종료 처리
--------------------------------------------------------------------------------

function EventRecursionGuard.exit(eventName)
    local depth = EventRecursionGuard.callStack[eventName] or 0
    if depth > 0 then
        EventRecursionGuard.callStack[eventName] = depth - 1
    end
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function EventRecursionGuard.getStats()
    return {
        maxDepthObserved = EventRecursionGuard.maxDepthObserved,
        blockCount = EventRecursionGuard.blockCount,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.EventRecursionGuard = EventRecursionGuard

return EventRecursionGuard
