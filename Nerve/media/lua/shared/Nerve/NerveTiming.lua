--[[
    NerveTiming.lua
    틱 타이밍 단일 진입점
    
    v1.0 - Phase 4-A 보강
    
    핵심 원칙:
    - 단일 진입점으로 tick delta 제공
    - Pulse tick SPI 가용 시 우선
    - 아니면 os.clock 추세 신호 (정밀 계측 아님)
    - Java는 플랫폼/기반 health, Lua는 로컬 fallback
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- NerveTiming 모듈
--------------------------------------------------------------------------------

local NerveTiming = {}

-- 타이밍 상태
local timing = {
    lastTickClockMs = 0,
    currentTickDeltaMs = 0,
    tickCount = 0,
    
    -- 통계
    avgDeltaMs = 16.67,  -- 60fps 기준
    maxDeltaMs = 0,
    minDeltaMs = 9999,
    
    -- 느린 틱 기준
    slowThresholdMs = 50,  -- 20fps 미만
}

-- 재사용 버퍼 (GC 압력 최소화)
local REUSE_BUFFER = {}

--------------------------------------------------------------------------------
-- 틱 시작 처리
--------------------------------------------------------------------------------

function NerveTiming.onTickStart()
    local now = os.clock() * 1000  -- ms
    
    if timing.lastTickClockMs > 0 then
        timing.currentTickDeltaMs = now - timing.lastTickClockMs
        
        -- 통계 갱신
        timing.maxDeltaMs = math.max(timing.maxDeltaMs, timing.currentTickDeltaMs)
        timing.minDeltaMs = math.min(timing.minDeltaMs, timing.currentTickDeltaMs)
        
        -- 이동 평균 (alpha = 0.1)
        timing.avgDeltaMs = timing.avgDeltaMs * 0.9 + timing.currentTickDeltaMs * 0.1
    end
    
    timing.lastTickClockMs = now
    timing.tickCount = timing.tickCount + 1
end

--------------------------------------------------------------------------------
-- 단일 진입점 API
--------------------------------------------------------------------------------

-- 현재 틱 delta 조회 (ms)
-- ⚠️ os.clock()은 정밀 계측이 아닌 추세 판단용
function NerveTiming.getTickDelta()
    -- Pulse tick SPI 가용 시 우선 (향후 확장)
    if Nerve.hasPulse and Pulse and Pulse.Timing and Pulse.Timing.getTickDelta then
        local ok, delta = pcall(Pulse.Timing.getTickDelta)
        if ok and delta then
            return delta
        end
    end
    
    -- Fallback: Lua wall-clock delta
    return timing.currentTickDeltaMs
end

-- 현재 틱이 "느린" 상태인지 확인
function NerveTiming.isSlowTick()
    local threshold = timing.slowThresholdMs
    if NerveConfig and NerveConfig.timing and NerveConfig.timing.slowThresholdMs then
        threshold = NerveConfig.timing.slowThresholdMs
    end
    
    return NerveTiming.getTickDelta() > threshold
end

-- 평균 틱 delta 조회
function NerveTiming.getAvgDelta()
    return timing.avgDeltaMs
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function NerveTiming.getStats()
    -- 재사용 버퍼 활용 (GC 압력 최소화)
    REUSE_BUFFER.currentDeltaMs = timing.currentTickDeltaMs
    REUSE_BUFFER.avgDeltaMs = timing.avgDeltaMs
    REUSE_BUFFER.maxDeltaMs = timing.maxDeltaMs
    REUSE_BUFFER.minDeltaMs = timing.minDeltaMs
    REUSE_BUFFER.tickCount = timing.tickCount
    REUSE_BUFFER.isSlowTick = NerveTiming.isSlowTick()
    
    return REUSE_BUFFER
end

-- 통계 리셋
function NerveTiming.resetStats()
    timing.maxDeltaMs = 0
    timing.minDeltaMs = 9999
    timing.avgDeltaMs = 16.67
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Timing = NerveTiming

return NerveTiming
