--[[
    Area6Repeat.lua
    StateKey 반복 기록 (증거 전용)
    
    v1.0 - Phase 5-4: Forensics
    
    [CONSTITUTION 준수]
    - 트리거로 사용 금지 (증거 전용)
    - StateKey = eventId + listenerId + (targetId?)
    - 인자 값 비교 금지 (최소 형태 식별자만)
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area6Repeat 모듈
--------------------------------------------------------------------------------

local Area6Repeat = {}

-- 반복 카운트 테이블 (틱 단위 wipe)
Area6Repeat.counts = {}
Area6Repeat.lastWipeTick = 0

-- TopN 설정
local TOP_N = 5

local function ensureCurrentTick()
    local currentTick = Nerve.Area6TickCtx and Nerve.Area6TickCtx.tickId or 0
    
    if currentTick ~= Area6Repeat.lastWipeTick then
        NerveUtils.safeWipe(Area6Repeat.counts)
        Area6Repeat.lastWipeTick = currentTick
    end
end

-- StateKey 생성
-- @param eventName: 이벤트 이름
-- @param listenerId: 리스너 식별자
-- @param targetId: 대상 ID (optional)
function Area6Repeat.makeStateKey(eventName, listenerId, targetId)
    local key = eventName .. ":" .. tostring(listenerId)
    if targetId then
        key = key .. ":" .. tostring(targetId)
    end
    return key
end

-- 반복 기록
function Area6Repeat.record(eventName, listenerId, targetId)
    ensureCurrentTick()
    
    local key = Area6Repeat.makeStateKey(eventName, listenerId, targetId)
    Area6Repeat.counts[key] = (Area6Repeat.counts[key] or 0) + 1
end

-- 카운트 조회
function Area6Repeat.getCount(eventName, listenerId, targetId)
    ensureCurrentTick()
    
    local key = Area6Repeat.makeStateKey(eventName, listenerId, targetId)
    return Area6Repeat.counts[key] or 0
end

-- TopN 반복 조회
function Area6Repeat.getTopN()
    ensureCurrentTick()
    
    local sorted = {}
    for key, count in pairs(Area6Repeat.counts) do
        table.insert(sorted, { key = key, count = count })
    end
    
    table.sort(sorted, function(a, b) return a.count > b.count end)
    
    local result = {}
    for i = 1, math.min(TOP_N, #sorted) do
        table.insert(result, sorted[i])
    end
    
    return result
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6Repeat = Area6Repeat

return Area6Repeat
