--[[
    SustainedPressureDetector.lua
    Sustained Event Pressure 감지
    
    v1.1 - GC Pressure 보강
    
    핵심 원칙:
    - 동일 이벤트 + 짧은 시간 창 + 반복 + Tick 느린 상태 감지
    - 상태 인식 플래그만 생성 (제어 판단 X, 추천 X)
    - NerveTiming 단일 진입점 사용
    - GC 압력 최소화: tick당 {} 생성 금지, 재사용 버퍼 사용
]]

require "Nerve/NerveUtils"
require "Nerve/NerveTiming"

--------------------------------------------------------------------------------
-- SustainedPressureDetector 모듈
--------------------------------------------------------------------------------

local SustainedPressureDetector = {}

-- 상태
SustainedPressureDetector.isSustained = false
SustainedPressureDetector.pressureStartMs = 0

-- 이벤트 압력 추적 (재사용)
local pressure = {
    windowStartMs = 0,
    eventCounts = {},        -- eventName -> count in window
    entryCount = 0,          -- cap 체크용
    MAX_ENTRIES = 100,       -- 무한 성장 방지
}

-- 재사용 버퍼 (GC 압력 최소화)
local REUSE_RESULT = {
    isSustained = false,
    eventCount = 0,
    reason = "normal",
}

local REUSE_STATS = {
    isSustained = false,
    pressureStartMs = 0,
    tickDeltaMs = 0,
    entryCount = 0,
    windowStartMs = 0,
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
-- 틱 처리
--------------------------------------------------------------------------------

function SustainedPressureDetector.onTickStart()
    local now = os.clock() * 1000  -- ms
    
    -- NerveTiming에 위임 (별도 호출 필요 없음 - Area6Coordinator에서 호출)
    
    -- 창 만료 체크
    local config = getConfig()
    if now - pressure.windowStartMs > config.windowMs then
        -- 새 창 시작: 테이블 재사용 (GC 압력 최소화)
        NerveUtils.safeWipe(pressure.eventCounts)
        pressure.windowStartMs = now
        pressure.entryCount = 0
    end
end

-- NerveTiming 사용 (단일 진입점)
function SustainedPressureDetector.isSlowTick()
    if Nerve.Timing then
        return Nerve.Timing.isSlowTick()
    end
    -- Fallback (NerveTiming 미로드)
    return false
end

--------------------------------------------------------------------------------
-- 압력 감지
--------------------------------------------------------------------------------

-- 이벤트 발생 기록 및 압력 판단
-- @return 재사용 버퍼 (새 테이블 생성 안 함)
function SustainedPressureDetector.recordAndCheck(eventName)
    local config = getConfig()
    
    -- 비활성화 시 항상 정상
    if not config.enabled then
        REUSE_RESULT.isSustained = false
        REUSE_RESULT.eventCount = 0
        REUSE_RESULT.reason = "disabled"
        return REUSE_RESULT
    end
    
    -- 엔트리 cap 체크 (무한 성장 방지)
    if pressure.entryCount >= pressure.MAX_ENTRIES then
        if not pressure.eventCounts[eventName] then
            REUSE_RESULT.isSustained = false
            REUSE_RESULT.eventCount = 0
            REUSE_RESULT.reason = "cap_reached"
            return REUSE_RESULT
        end
    end
    
    -- 이벤트 카운트 증가
    local count = pressure.eventCounts[eventName]
    if count == nil then
        count = 0
        pressure.entryCount = pressure.entryCount + 1
    end
    count = count + 1
    pressure.eventCounts[eventName] = count
    
    -- Sustained 조건 체크
    local isHighCount = count >= config.threshold
    local isSlow = SustainedPressureDetector.isSlowTick()
    
    local wasSustained = SustainedPressureDetector.isSustained
    SustainedPressureDetector.isSustained = isHighCount and isSlow
    
    -- sustained 진입 시점 기록
    if SustainedPressureDetector.isSustained and not wasSustained then
        SustainedPressureDetector.pressureStartMs = os.clock() * 1000
        
        if NerveConfig and NerveConfig.debug then
            local delta = Nerve.Timing and Nerve.Timing.getTickDelta() or 0
            NerveUtils.debug("SUSTAINED PRESSURE: " .. eventName 
                .. " (count=" .. count .. ", tickDelta=" .. delta .. "ms)")
        end
    end
    
    -- 재사용 버퍼 반환 (GC 압력 최소화)
    REUSE_RESULT.isSustained = SustainedPressureDetector.isSustained
    REUSE_RESULT.eventCount = count
    REUSE_RESULT.reason = SustainedPressureDetector.isSustained 
        and "high_count_and_slow_tick" 
        or "normal"
    
    return REUSE_RESULT
end

-- 현재 sustained 상태 조회
function SustainedPressureDetector.checkPressure()
    local delta = Nerve.Timing and Nerve.Timing.getTickDelta() or 0
    REUSE_RESULT.isSustained = SustainedPressureDetector.isSustained
    REUSE_RESULT.eventCount = 0
    REUSE_RESULT.reason = SustainedPressureDetector.isSlowTick() and "slow_tick" or "normal"
    return REUSE_RESULT
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function SustainedPressureDetector.getStats()
    -- 재사용 버퍼 (단, eventCounts는 참조라 주의)
    REUSE_STATS.isSustained = SustainedPressureDetector.isSustained
    REUSE_STATS.pressureStartMs = SustainedPressureDetector.pressureStartMs
    REUSE_STATS.tickDeltaMs = Nerve.Timing and Nerve.Timing.getTickDelta() or 0
    REUSE_STATS.entryCount = pressure.entryCount
    REUSE_STATS.windowStartMs = pressure.windowStartMs
    return REUSE_STATS
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.SustainedPressureDetector = SustainedPressureDetector

return SustainedPressureDetector

