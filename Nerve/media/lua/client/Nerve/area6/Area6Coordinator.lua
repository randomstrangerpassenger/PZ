--[[
    Area6Coordinator.lua
    Area 6 통합 조율 모듈
    
    v2.0 - EventRecursionGuard Refactoring
    
    핵심 역할:
    - EventRecursionGuard, CascadeGuard 통합 관리
    - [Phase 1] EventFormClassifier, SustainedPressureDetector, EarlyExitHandler 통합
    - [Reinforcement] NerveTiming 단일 진입점, NerveFailsoft 보호
    - 단일 진입점 shouldProcess() API 제공
    - 컴포넌트 초기화/종료 조율
    
    변경 사항 (v2.0):
    - EventDeduplicator 제거 → EventRecursionGuard 교체
    - 틱 중복 스킵 제거, 재귀 폭주 감지만 수행
]]

require "Nerve/NerveUtils"
require "Nerve/NerveTiming"
require "Nerve/NerveFailsoft"
require "Nerve/area6/ContextExtractors"
require "Nerve/area6/EventRecursionGuard"
require "Nerve/area6/CascadeGuard"
require "Nerve/area6/EventFormClassifier"
require "Nerve/area6/SustainedPressureDetector"
require "Nerve/area6/EarlyExitHandler"

--------------------------------------------------------------------------------
-- Area6Coordinator 모듈
--------------------------------------------------------------------------------

local Area6Coordinator = {}

-- 컴포넌트 참조
Area6Coordinator.recursionGuard = Nerve.EventRecursionGuard
Area6Coordinator.cascadeGuard = Nerve.CascadeGuard
Area6Coordinator.contextExtractors = Nerve.ContextExtractors
-- Phase 1 컴포넌트
Area6Coordinator.formClassifier = Nerve.EventFormClassifier
Area6Coordinator.pressureDetector = Nerve.SustainedPressureDetector
Area6Coordinator.earlyExitHandler = Nerve.EarlyExitHandler

--------------------------------------------------------------------------------
-- 틱 시작 처리
--------------------------------------------------------------------------------

function Area6Coordinator.onTickStart()
    -- [Reinforcement] NerveTiming 먼저 갱신 (단일 진입점)
    if Nerve.Timing then
        Nerve.Timing.onTickStart()
    end
    
    -- [Phase 1] 타이밍 추적
    if Area6Coordinator.pressureDetector then
        Area6Coordinator.pressureDetector.onTickStart()
    end
    
    -- [Phase 1] Early Exit 상태 갱신
    if Area6Coordinator.earlyExitHandler then
        Area6Coordinator.earlyExitHandler.onTickStart()
    end
    
    -- [Phase 1] Form Classifier 초기화
    if Area6Coordinator.formClassifier then
        Area6Coordinator.formClassifier.onTickStart()
    end
    
    -- RecursionGuard 초기화
    if Area6Coordinator.recursionGuard then
        Area6Coordinator.recursionGuard.onTickStart()
    end
    
    -- CascadeGuard 체크
    if Area6Coordinator.cascadeGuard then
        Area6Coordinator.cascadeGuard.onTickStart()
    end
end

--------------------------------------------------------------------------------
-- 이벤트 처리 판단
--------------------------------------------------------------------------------

-- 이벤트를 처리해야 하는지 판단
-- @param eventName: 이벤트 이름
-- @param contextKey: 컨텍스트 키 (nil 허용)
-- @return: true (처리), false (스킵)
function Area6Coordinator.shouldProcess(eventName, contextKey)
    -- Area6 비활성화 시 항상 처리
    if not NerveConfig 
        or not NerveConfig.area6 
        or not NerveConfig.area6.enabled then
        return true
    end
    
    -- [Phase 1] 이벤트 형태 기록
    if Area6Coordinator.formClassifier then
        Area6Coordinator.formClassifier.recordEvent(eventName)
    end
    
    -- [Phase 1] Sustained Pressure 체크 및 Early Exit 연동
    if Area6Coordinator.pressureDetector and Area6Coordinator.earlyExitHandler then
        local pressureResult = Area6Coordinator.pressureDetector.recordAndCheck(eventName)
        Area6Coordinator.earlyExitHandler.updateFromSustained(pressureResult.isSustained)
    end
    
    -- 1. RecursionGuard 체크 (크래시 방지용 최후 가드)
    if Area6Coordinator.recursionGuard 
        and NerveConfig.area6.recursionGuard 
        and NerveConfig.area6.recursionGuard.enabled then
        
        if not Area6Coordinator.recursionGuard.enter(eventName) then
            -- Invariant 검증: DROP 발생 기록
            if Nerve.EventInvariants then
                Nerve.EventInvariants.checkNoDropNoDelay(eventName, true, false)
            end
            return false  -- Strict + 폭주일 때만 도달
        end
    end
    
    -- 2. CascadeGuard 체크
    if Area6Coordinator.cascadeGuard then
        if not Area6Coordinator.cascadeGuard.enter(eventName) then
            -- Invariant 검증: DROP 발생 기록
            if Nerve.EventInvariants then
                Nerve.EventInvariants.checkNoDropNoDelay(eventName, true, false)
            end
            return false  -- 깊이 초과로 스킵
        end
    end
    
    return true  -- 처리
end

-- 이벤트 처리 완료 후 호출
function Area6Coordinator.afterProcess(eventName)
    -- CascadeGuard 종료
    if Area6Coordinator.cascadeGuard then
        Area6Coordinator.cascadeGuard.exit()
    end
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function Area6Coordinator.getStats()
    local stats = {
        recursionGuard = nil,
        cascadeGuard = nil,
        -- Phase 1
        formClassifier = nil,
        pressureDetector = nil,
        earlyExitHandler = nil,
    }
    
    if Area6Coordinator.recursionGuard then
        stats.recursionGuard = Area6Coordinator.recursionGuard.getStats()
    end
    
    if Area6Coordinator.cascadeGuard then
        stats.cascadeGuard = Area6Coordinator.cascadeGuard.getStats()
    end
    
    -- Phase 1 통계
    if Area6Coordinator.formClassifier then
        stats.formClassifier = Area6Coordinator.formClassifier.getStats()
    end
    
    if Area6Coordinator.pressureDetector then
        stats.pressureDetector = Area6Coordinator.pressureDetector.getStats()
    end
    
    if Area6Coordinator.earlyExitHandler then
        stats.earlyExitHandler = Area6Coordinator.earlyExitHandler.getStats()
    end
    
    return stats
end

-- 상태 출력
function Area6Coordinator.printStatus()
    NerveUtils.info("========================================")
    NerveUtils.info("Area 6 Status")
    NerveUtils.info("========================================")
    
    -- RecursionGuard 상태
    if Area6Coordinator.recursionGuard then
        local stats = Area6Coordinator.recursionGuard.getStats()
        NerveUtils.info("RecursionGuard:")
        NerveUtils.info("  Max Depth Observed: " .. stats.maxDepthObserved)
        NerveUtils.info("  Block Count: " .. stats.blockCount)
    end
    
    -- CascadeGuard 상태
    if Area6Coordinator.cascadeGuard then
        local stats = Area6Coordinator.cascadeGuard.getStats()
        NerveUtils.info("CascadeGuard:")
        NerveUtils.info("  Max Observed Depth: " .. stats.maxObservedDepth)
    end
    
    NerveUtils.info("========================================")
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6 = Area6Coordinator

return Area6Coordinator
