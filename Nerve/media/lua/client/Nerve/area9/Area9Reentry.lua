--[[
    Area9Reentry.lua
    Re-entrancy Guard (tick-only 상태)
    
    [헌법 준수]
    - 경계: endpoints only
    - 키: conn/player 우선, 없으면 handler
    - 상태: ENTERED → BYPASS_THIS_TICK → RESET
    - Phase 2: 표시만 (행동 금지)
    
    [주의] BYPASS는 '표식'임, 선리턴은 Quarantine에서만 발생
]]

require "Nerve/NerveUtils"
require "Nerve/area9/Area9TickCtx"
require "Nerve/area9/Area9Forensic"

--------------------------------------------------------------------------------
-- Area9Reentry 모듈
--------------------------------------------------------------------------------

local Area9Reentry = {}

-- 상태 enum
Area9Reentry.State = {
    NONE = 0,
    ENTERED = 1,
    BYPASS_THIS_TICK = 2,
}

--------------------------------------------------------------------------------
-- Re-entrancy 체크 (표시만, 행동 금지)
--------------------------------------------------------------------------------

-- 진입 시 체크
-- @param scopeKey: 스코프 식별자
-- @return: isReentry (bool), state
function Area9Reentry.checkEnter(scopeKey)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return false, Area9Reentry.State.NONE
    end
    
    local currentState = TickCtx.getReentryState(scopeKey)
    
    if currentState == "ENTERED" then
        -- 재진입 감지!
        TickCtx.setReentryState(scopeKey, "BYPASS_THIS_TICK")
        TickCtx.markIncident("reentry")
        
        -- Forensic 기록
        local Forensic = Nerve.Area9Forensic
        if Forensic then
            Forensic.recordReentry(Forensic.ReasonCode.REENTRY_DETECTED, 0, 0)
        end
        
        return true, Area9Reentry.State.BYPASS_THIS_TICK
    elseif currentState == "BYPASS_THIS_TICK" then
        -- 이미 bypass 상태
        return true, Area9Reentry.State.BYPASS_THIS_TICK
    else
        -- 정상 진입
        TickCtx.setReentryState(scopeKey, "ENTERED")
        return false, Area9Reentry.State.ENTERED
    end
end

-- 종료 시 정리
-- @param scopeKey: 스코프 식별자
function Area9Reentry.markExit(scopeKey)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return
    end
    
    local currentState = TickCtx.getReentryState(scopeKey)
    
    -- BYPASS_THIS_TICK 상태면 유지 (다음 tick에 RESET)
    -- ENTERED 상태면 NONE으로 복귀
    if currentState == "ENTERED" then
        TickCtx.setReentryState(scopeKey, nil)
    end
end

-- 현재 상태 조회
function Area9Reentry.getState(scopeKey)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return Area9Reentry.State.NONE
    end
    
    local state = TickCtx.getReentryState(scopeKey)
    if state == "ENTERED" then
        return Area9Reentry.State.ENTERED
    elseif state == "BYPASS_THIS_TICK" then
        return Area9Reentry.State.BYPASS_THIS_TICK
    else
        return Area9Reentry.State.NONE
    end
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Reentry = Area9Reentry

return Area9Reentry
