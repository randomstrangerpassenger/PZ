--[[
    Area6DupCount.lua
    동일 틱 중복 호출 카운트
    
    v1.0 - Phase 5-1: Forensics
    
    [CONSTITUTION 준수]
    - 트리거로 사용 금지 (증거 전용)
    - incident 후 Lazy 수집
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area6DupCount 모듈
--------------------------------------------------------------------------------

local Area6DupCount = {}

-- 카운트 테이블 (틱 단위 wipe)
Area6DupCount.counts = {}
Area6DupCount.lastWipeTick = 0

local function ensureCurrentTick()
    local currentTick = Nerve.Area6TickCtx and Nerve.Area6TickCtx.tickId or 0
    
    if currentTick ~= Area6DupCount.lastWipeTick then
        NerveUtils.safeWipe(Area6DupCount.counts)
        Area6DupCount.lastWipeTick = currentTick
    end
end

-- 호출 기록
function Area6DupCount.record(eventName, listenerId)
    ensureCurrentTick()
    
    local key = eventName .. ":" .. tostring(listenerId)
    Area6DupCount.counts[key] = (Area6DupCount.counts[key] or 0) + 1
end

-- 카운트 조회
function Area6DupCount.getCount(eventName, listenerId)
    ensureCurrentTick()
    
    local key = eventName .. ":" .. tostring(listenerId)
    return Area6DupCount.counts[key] or 0
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6DupCount = Area6DupCount

return Area6DupCount
