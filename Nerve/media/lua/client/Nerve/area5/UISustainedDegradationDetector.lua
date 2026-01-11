--[[
    UISustainedDegradationDetector.lua
    UI Sustained Degradation 감지
    
    v1.0 - Phase 2-B
    
    핵심 원칙:
    - 프레임이 이미 밀린 상태 + UI 갱신 연속 발생 감지
    - "느린 UI 상태가 유지됨" = degraded
    - UI가 병목이라는 상태 인식만 수행 (제어 판단 X)
    - os.clock()은 정밀 계측이 아닌 추세 판단용
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- UISustainedDegradationDetector 모듈
--------------------------------------------------------------------------------

local UISustainedDegradationDetector = {}

-- 상태
UISustainedDegradationDetector.isDegraded = false
UISustainedDegradationDetector.degradeStartMs = 0

-- 타이밍 추적
local timing = {
    lastUIUpdateMs = 0,
    consecutiveUpdates = 0,
    slowFrameThresholdMs = 50,  -- 느린 프레임 기준
}

-- UI 갱신 추적
local uiUpdates = {
    countThisTick = 0,
    threshold = 10,  -- 틱당 UI 갱신 임계값
}

--------------------------------------------------------------------------------
-- 공개 API
--------------------------------------------------------------------------------

-- 틱 시작 시 초기화
function UISustainedDegradationDetector.onTickStart()
    uiUpdates.countThisTick = 0
end

-- UI 갱신 기록 및 degradation 판단
-- @return { isDegraded = bool, updateCount = n, reason = string }
function UISustainedDegradationDetector.recordAndCheck()
    local now = os.clock() * 1000  -- ms
    uiUpdates.countThisTick = uiUpdates.countThisTick + 1
    
    -- 연속 갱신 감지
    local timeSinceLastUpdate = now - timing.lastUIUpdateMs
    if timeSinceLastUpdate < 16 then  -- ~60fps
        timing.consecutiveUpdates = timing.consecutiveUpdates + 1
    else
        timing.consecutiveUpdates = 1
    end
    timing.lastUIUpdateMs = now
    
    -- Degradation 조건:
    -- 1. 틱당 UI 갱신 임계값 초과
    -- 2. 또는 연속 갱신 폭주 (짧은 시간 내 다량)
    local isHighCount = uiUpdates.countThisTick >= uiUpdates.threshold
    local isConsecutiveFlooding = timing.consecutiveUpdates >= 5
    
    local wasDegraded = UISustainedDegradationDetector.isDegraded
    UISustainedDegradationDetector.isDegraded = isHighCount or isConsecutiveFlooding
    
    -- degraded 진입 시점 기록
    if UISustainedDegradationDetector.isDegraded and not wasDegraded then
        UISustainedDegradationDetector.degradeStartMs = now
        
        if NerveConfig and NerveConfig.debug then
            NerveUtils.debug("UI DEGRADED: count=" .. uiUpdates.countThisTick 
                .. ", consecutive=" .. timing.consecutiveUpdates)
        end
    end
    
    return {
        isDegraded = UISustainedDegradationDetector.isDegraded,
        updateCount = uiUpdates.countThisTick,
        consecutiveUpdates = timing.consecutiveUpdates,
        reason = UISustainedDegradationDetector.isDegraded 
            and (isHighCount and "high_update_count" or "consecutive_flooding")
            or "normal",
    }
end

-- 현재 degraded 상태 조회
function UISustainedDegradationDetector.checkDegradation()
    return {
        isDegraded = UISustainedDegradationDetector.isDegraded,
        degradeStartMs = UISustainedDegradationDetector.degradeStartMs,
        countThisTick = uiUpdates.countThisTick,
        consecutiveUpdates = timing.consecutiveUpdates,
    }
end

-- 통계 조회
function UISustainedDegradationDetector.getStats()
    return {
        isDegraded = UISustainedDegradationDetector.isDegraded,
        degradeStartMs = UISustainedDegradationDetector.degradeStartMs,
        countThisTick = uiUpdates.countThisTick,
        consecutiveUpdates = timing.consecutiveUpdates,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.UISustainedDegradationDetector = UISustainedDegradationDetector

return UISustainedDegradationDetector
