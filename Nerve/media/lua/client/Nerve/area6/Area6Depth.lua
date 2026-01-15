--[[
    Area6Depth.lua
    체인 깊이 기록 (증거 전용)
    
    v1.0 - Phase 5-2: Forensics
    
    [CONSTITUTION 준수]
    - 트리거로 사용 금지 (증거 전용)
    - 깊이 기록만 (cap 도달 시 포화 표시)
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area6Depth 모듈
--------------------------------------------------------------------------------

local Area6Depth = {}

-- 최대 깊이 cap
local DEPTH_CAP = 100

-- 현재 틱의 최대 관측 깊이
Area6Depth.maxObserved = 0
Area6Depth.lastWipeTick = 0

local function ensureCurrentTick()
    local currentTick = Nerve.Area6TickCtx and Nerve.Area6TickCtx.tickId or 0
    
    if currentTick ~= Area6Depth.lastWipeTick then
        Area6Depth.maxObserved = 0
        Area6Depth.lastWipeTick = currentTick
    end
end

-- 현재 깊이 조회
function Area6Depth.getCurrentDepth()
    ensureCurrentTick()
    
    local TickCtx = Nerve.Area6TickCtx
    if TickCtx then
        return TickCtx.getChainDepth()
    end
    return 0
end

-- 깊이 기록 (호출마다)
function Area6Depth.record()
    ensureCurrentTick()
    
    local current = Area6Depth.getCurrentDepth()
    if current > Area6Depth.maxObserved then
        Area6Depth.maxObserved = math.min(current, DEPTH_CAP)
    end
end

-- 최대 관측 깊이
function Area6Depth.getMaxObserved()
    ensureCurrentTick()
    return Area6Depth.maxObserved
end

-- cap 도달 여부
function Area6Depth.isSaturated()
    return Area6Depth.maxObserved >= DEPTH_CAP
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6Depth = Area6Depth

return Area6Depth
