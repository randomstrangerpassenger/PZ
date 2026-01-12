--[[
    EventRecursionGuard.lua
    재귀/재진입 깊이 가드 (크래시 방지 전용)
    
    v0.2 - Refactored from EventDeduplicator
    
    핵심 원칙:
    - Default(strict=false): Report-only (로그만, 차단 없음)
    - Strict opt-in: 폭주 시 차단 (=DROP, 로그 필수)
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
local DEFAULT_STRICT_MODE = false

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
-- @return: true (통과), false (차단 - Strict 모드 + 폭주일 때만)
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
    
    local strictMode = NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.recursionGuard 
        and NerveConfig.area6.recursionGuard.strict 
        or DEFAULT_STRICT_MODE
    
    -- 폭주 감지
    if depth >= maxRecursion then
        -- 항상 로그 (침묵 금지)
        NerveUtils.warn("RECURSION GUARD: " .. eventName 
            .. " depth=" .. depth .. "/" .. maxRecursion)
        
        -- Strict 모드에서만 실제 차단
        if strictMode then
            -- DROP임을 노골적으로 명시 (침묵 금지)
            NerveUtils.error("[!] LAST-RESORT DROP: " .. eventName 
                .. " (strict=true, crash prevention)")
            EventRecursionGuard.blockCount = EventRecursionGuard.blockCount + 1
            return false  -- 차단 (=DROP)
        end
    end
    
    return true  -- 기본: 항상 통과
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
