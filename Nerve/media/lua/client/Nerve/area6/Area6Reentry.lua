--[[
    Area6Reentry.lua
    재진입(Self-Recursion) 트리거 모듈
    
    v1.0 - Phase 4: Reentry Trigger
    
    핵심 역할:
    - same-tick + same-listener wrapper 재진입 검출
    - 트리거 발생 시 incident 표시 + 동일 틱 철수
    
    [CONSTITUTION 준수]
    - 트리거 정의: same-tick self-recursion만 (A↔B 상호호출 제외)
    - 액션: 동일 틱 철수(pass-through) 단일
    - Drop 금지
]]

require "Nerve/NerveUtils"
require "Nerve/area6/Area6TickCtx"
require "Nerve/area6/Area6InstallState"

--------------------------------------------------------------------------------
-- Area6Reentry 모듈
--------------------------------------------------------------------------------

local Area6Reentry = {}

-- 레이트리밋 상태
Area6Reentry.rateLimitState = {}
Area6Reentry.lastWipeTick = 0

-- 레이트리밋 설정
local RATE_LIMIT_COUNT = 3

--------------------------------------------------------------------------------
-- 틱 관리
--------------------------------------------------------------------------------

local function ensureCurrentTick()
    local currentTick = Nerve.Area6TickCtx and Nerve.Area6TickCtx.tickId or 0
    
    if currentTick ~= Area6Reentry.lastWipeTick then
        NerveUtils.safeWipe(Area6Reentry.rateLimitState)
        Area6Reentry.lastWipeTick = currentTick
    end
end

--------------------------------------------------------------------------------
-- 재진입 체크
--------------------------------------------------------------------------------

-- 재진입 체크 (리스너 진입 전 호출)
-- @param eventName: 이벤트 이름
-- @param listenerId: 리스너 식별자
-- @return: { isReentry: boolean, depth: number }
function Area6Reentry.checkReentry(eventName, listenerId)
    local TickCtx = Nerve.Area6TickCtx
    
    if not TickCtx then
        return { isReentry = false, depth = 0 }
    end
    
    -- 현재 깊이 조회 (진입 전)
    local currentDepth = TickCtx.getListenerDepth(eventName, listenerId)
    
    -- 깊이 > 0 이면 same-tick self-recursion
    local isReentry = currentDepth > 0
    
    return {
        isReentry = isReentry,
        depth = currentDepth,
    }
end

-- 재진입 트리거 처리
-- @param eventName: 이벤트 이름
-- @param listenerId: 리스너 식별자
-- @param depth: 현재 깊이
function Area6Reentry.handleReentryTrigger(eventName, listenerId, depth)
    ensureCurrentTick()
    
    local TickCtx = Nerve.Area6TickCtx
    local InstallState = Nerve.Area6InstallState
    
    -- 1. incident 표시
    if TickCtx then
        TickCtx.markReentry()
    end
    
    -- 2. 동일 틱 철수 스코프 등록
    if TickCtx then
        local scopeKey = TickCtx.makeListenerScopeKey(eventName, listenerId)
        TickCtx.markPassthrough(scopeKey)
    end
    
    -- 3. 레이트리밋 체크
    local rateLimitKey = "reentry|" .. eventName .. "|" .. tostring(listenerId)
    local logCount = Area6Reentry.rateLimitState[rateLimitKey] or 0
    
    if logCount < RATE_LIMIT_COUNT then
        -- 4. 침묵 금지: 사건 로그 출력
        local installState = InstallState and InstallState.getState() or "unknown"
        
        NerveUtils.warn("==========================================")
        NerveUtils.warn("[Area6] INCIDENT: reentry")
        NerveUtils.warn("  eventId: " .. eventName)
        NerveUtils.warn("  listenerId: " .. tostring(listenerId))
        NerveUtils.warn("  depth: " .. tostring(depth))
        NerveUtils.warn("  installState: " .. installState)
        NerveUtils.warn("  action: SAME_TICK_PASSTHROUGH")
        NerveUtils.warn("==========================================")
        
        Area6Reentry.rateLimitState[rateLimitKey] = logCount + 1
    elseif logCount == RATE_LIMIT_COUNT then
        NerveUtils.warn("[Area6] Rate limit reached for reentry: " 
            .. eventName .. ":" .. tostring(listenerId))
        Area6Reentry.rateLimitState[rateLimitKey] = logCount + 1
    end
end

--------------------------------------------------------------------------------
-- 유틸리티
--------------------------------------------------------------------------------

-- 설정에서 reentry 트리거 활성화 여부
function Area6Reentry.isEnabled()
    if not NerveConfig or not NerveConfig.area6 then
        return false
    end
    
    local triggers = NerveConfig.area6.triggers
    if not triggers or not triggers.reentry then
        return false
    end
    
    return triggers.reentry.enabled == true
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6Reentry = Area6Reentry

return Area6Reentry
