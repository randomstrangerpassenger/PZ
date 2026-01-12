--[[
    Area6Coordinator.lua
    Area 6 통합 조율 모듈
    
    v3.0 - Pure Observation Mode (헌법 준수)
    
    핵심 역할:
    - EventRecursionGuard, CascadeGuard 관측 관리
    - 단일 진입점 shouldProcess() API 제공 (관측 전용)
    - Drop/Delay/정책 일체 금지
    
    변경 사항 (v3.0):
    - 정책성 컴포넌트 제거 (SustainedPressureDetector, EarlyExitHandler, EventFormClassifier)
    - shouldProcess()는 항상 true 반환 (관측만 수행)
    - Drop 경로 완전 제거
]]

require "Nerve/NerveUtils"
require "Nerve/NerveTiming"
require "Nerve/NerveFailsoft"
require "Nerve/area6/ContextExtractors"
require "Nerve/area6/EventRecursionGuard"
require "Nerve/area6/CascadeGuard"
-- [REMOVED] 정책성 컴포넌트 제거 (헌법 준수)
-- require "Nerve/area6/EventFormClassifier"
-- require "Nerve/area6/SustainedPressureDetector"
-- require "Nerve/area6/EarlyExitHandler"

--------------------------------------------------------------------------------
-- Area6Coordinator 모듈
--------------------------------------------------------------------------------

local Area6Coordinator = {}

-- 컴포넌트 참조 (관측 전용)
Area6Coordinator.recursionGuard = Nerve.EventRecursionGuard
Area6Coordinator.cascadeGuard = Nerve.CascadeGuard
Area6Coordinator.contextExtractors = Nerve.ContextExtractors

--------------------------------------------------------------------------------
-- 틱 시작 처리
--------------------------------------------------------------------------------

function Area6Coordinator.onTickStart()
    -- NerveTiming 갱신
    if Nerve.Timing then
        Nerve.Timing.onTickStart()
    end
    
    -- RecursionGuard 초기화
    if Area6Coordinator.recursionGuard then
        Area6Coordinator.recursionGuard.onTickStart()
    end
    
    -- CascadeGuard 초기화
    if Area6Coordinator.cascadeGuard then
        Area6Coordinator.cascadeGuard.onTickStart()
    end
end

--------------------------------------------------------------------------------
-- 이벤트 처리 판단 (관측 전용 - 항상 통과)
--------------------------------------------------------------------------------

-- 이벤트를 처리해야 하는지 판단
-- @param eventName: 이벤트 이름
-- @param contextKey: 컨텍스트 키 (nil 허용)
-- @return: true (항상 통과 - Drop 금지 원칙)
function Area6Coordinator.shouldProcess(eventName, contextKey)
    -- Area6 비활성화 시 항상 처리
    if not NerveConfig 
        or not NerveConfig.area6 
        or not NerveConfig.area6.enabled then
        return true
    end
    
    -- 1. RecursionGuard 관측 (Drop 없음)
    if Area6Coordinator.recursionGuard 
        and NerveConfig.area6.recursionGuard 
        and NerveConfig.area6.recursionGuard.enabled then
        -- enter()는 항상 true 반환 (관측 전용)
        Area6Coordinator.recursionGuard.enter(eventName)
    end
    
    -- 2. CascadeGuard 관측 (Drop 없음)
    if Area6Coordinator.cascadeGuard then
        -- enter()는 observeOnly 모드에서 항상 true 반환
        Area6Coordinator.cascadeGuard.enter(eventName)
    end
    
    return true  -- [FIX] 항상 통과 (Drop 금지 원칙)
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
    }
    
    if Area6Coordinator.recursionGuard then
        stats.recursionGuard = Area6Coordinator.recursionGuard.getStats()
    end
    
    if Area6Coordinator.cascadeGuard then
        stats.cascadeGuard = Area6Coordinator.cascadeGuard.getStats()
    end
    
    return stats
end

-- 상태 출력
function Area6Coordinator.printStatus()
    NerveUtils.info("========================================")
    NerveUtils.info("Area 6 Status (Observe-Only)")
    NerveUtils.info("========================================")
    
    -- RecursionGuard 상태
    if Area6Coordinator.recursionGuard then
        local stats = Area6Coordinator.recursionGuard.getStats()
        NerveUtils.info("RecursionGuard:")
        NerveUtils.info("  Max Depth Observed: " .. stats.maxDepthObserved)
        NerveUtils.info("  Warning Count: " .. stats.blockCount)
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
