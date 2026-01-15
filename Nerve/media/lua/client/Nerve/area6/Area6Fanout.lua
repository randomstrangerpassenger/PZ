--[[
    Area6Fanout.lua
    Fan-out 기록 (증거 전용)
    
    v1.0 - Phase 5-3: Forensics
    
    [CONSTITUTION 준수]
    - 트리거로 사용 금지 (증거 전용)
    - incident 틱에서만 계산
    - 우선순위:
      1. chain-scope executed listeners (실제 실행된 수)
      2. event-scope registered listeners (가능할 때만)
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area6Fanout 모듈
--------------------------------------------------------------------------------

local Area6Fanout = {}

-- 실행된 리스너 카운트 (틱 단위)
Area6Fanout.executedCount = 0
Area6Fanout.lastWipeTick = 0

local function ensureCurrentTick()
    local currentTick = Nerve.Area6TickCtx and Nerve.Area6TickCtx.tickId or 0
    
    if currentTick ~= Area6Fanout.lastWipeTick then
        Area6Fanout.executedCount = 0
        Area6Fanout.lastWipeTick = currentTick
    end
end

-- 실행 기록
function Area6Fanout.recordExecution()
    ensureCurrentTick()
    Area6Fanout.executedCount = Area6Fanout.executedCount + 1
end

-- Fan-out 조회
-- @return: { executed: number, registered: number|nil }
function Area6Fanout.getFanout()
    ensureCurrentTick()
    
    return {
        executed = Area6Fanout.executedCount,
        registered = nil,  -- TODO: 가능할 때 이벤트 등록 리스너 수
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6Fanout = Area6Fanout

return Area6Fanout
