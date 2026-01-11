--[[
    SustainedPressureDetector.lua
    Sustained Event Pressure 감지
    
    v1.0 - Phase 1-B
    
    핵심 원칙:
    - 동일 이벤트 + 짧은 시간 창 + 반복 + Tick 느린 상태 감지
    - 상태 인식 플래그만 생성 (제어 판단 X, 추천 X)
    - "느림" 판정: Lua wall-clock delta (os.clock() 기반)
    - os.clock()은 정밀 계측이 아닌 추세 판단용으로만 사용
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- SustainedPressureDetector 모듈
--------------------------------------------------------------------------------

local SustainedPressureDetector = {}

-- 상태
SustainedPressureDetector.isSustained = false
SustainedPressureDetector.pressureStartMs = 0

-- 틱 타이밍 추적
local timing = {
    lastTickTime = 0,        -- os.clock() 기준
    tickDeltaMs = 0,         -- 마지막 틱 delta (ms)
    slowTickThresholdMs = 50,-- "느림" 판정 기준 (50ms = 20fps 미만)
}

-- 이벤트 압력 추적
local pressure = {
    windowStartMs = 0,
    eventCounts = {},        -- eventName -> count in window
}

--------------------------------------------------------------------------------
-- 설정 조회
--------------------------------------------------------------------------------

local function getConfig()
    if not NerveConfig or not NerveConfig.area6 
        or not NerveConfig.area6.sustainedPressure then
        return {
            enabled = false,
            windowMs = 100,
            threshold = 5,
        }
    end
    return NerveConfig.area6.sustainedPressure
end

--------------------------------------------------------------------------------
-- 틱 타이밍
--------------------------------------------------------------------------------

-- 틱 시작 시 호출
function SustainedPressureDetector.onTickStart()
    local now = os.clock() * 1000  -- ms 변환
    
    if timing.lastTickTime > 0 then
        timing.tickDeltaMs = now - timing.lastTickTime
    end
    timing.lastTickTime = now
    
    -- 창 만료 체크
    local config = getConfig()
    if now - pressure.windowStartMs > config.windowMs then
        -- 새 창 시작
        NerveUtils.safeWipe(pressure.eventCounts)
        pressure.windowStartMs = now
    end
end

-- 틱이 "느린" 상태인지 확인
-- ⚠️ os.clock()은 정밀 계측이 아닌 추세 판단용
function SustainedPressureDetector.isSlowTick()
    return timing.tickDeltaMs > timing.slowTickThresholdMs
end

--------------------------------------------------------------------------------
-- 압력 감지
--------------------------------------------------------------------------------

-- 이벤트 발생 기록 및 압력 판단
-- @return { isSustained = bool, eventCount = n, reason = string }
function SustainedPressureDetector.recordAndCheck(eventName)
    local config = getConfig()
    
    -- 비활성화 시 항상 정상
    if not config.enabled then
        return {
            isSustained = false,
            eventCount = 0,
            reason = "disabled",
        }
    end
    
    -- 이벤트 카운트 증가
    local count = (pressure.eventCounts[eventName] or 0) + 1
    pressure.eventCounts[eventName] = count
    
    -- Sustained 조건 체크:
    -- 1. 동일 이벤트가 threshold 이상
    -- 2. Tick이 느린 상태
    local isHighCount = count >= config.threshold
    local isSlow = SustainedPressureDetector.isSlowTick()
    
    local wasSustained = SustainedPressureDetector.isSustained
    SustainedPressureDetector.isSustained = isHighCount and isSlow
    
    -- sustained 진입 시점 기록
    if SustainedPressureDetector.isSustained and not wasSustained then
        SustainedPressureDetector.pressureStartMs = os.clock() * 1000
        
        if NerveConfig and NerveConfig.debug then
            NerveUtils.debug("SUSTAINED PRESSURE: " .. eventName 
                .. " (count=" .. count .. ", tickDelta=" .. timing.tickDeltaMs .. "ms)")
        end
    end
    
    return {
        isSustained = SustainedPressureDetector.isSustained,
        eventCount = count,
        reason = SustainedPressureDetector.isSustained 
            and "high_count_and_slow_tick" 
            or "normal",
    }
end

-- 현재 sustained 상태 조회 (플래그만, 제어 판단 X)
function SustainedPressureDetector.checkPressure()
    return {
        isSustained = SustainedPressureDetector.isSustained,
        pressureStartMs = SustainedPressureDetector.pressureStartMs,
        tickDeltaMs = timing.tickDeltaMs,
        isSlowTick = SustainedPressureDetector.isSlowTick(),
    }
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function SustainedPressureDetector.getStats()
    return {
        isSustained = SustainedPressureDetector.isSustained,
        pressureStartMs = SustainedPressureDetector.pressureStartMs,
        tickDeltaMs = timing.tickDeltaMs,
        eventCounts = pressure.eventCounts,
        windowStartMs = pressure.windowStartMs,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.SustainedPressureDetector = SustainedPressureDetector

return SustainedPressureDetector
