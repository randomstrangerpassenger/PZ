--[[
    Area6Coordinator.lua
    Area 6 통합 조율 모듈
    
    v1.2 - Critical Reinforcement
    
    핵심 역할:
    - EventDeduplicator, CascadeGuard 통합 관리
    - [Phase 1] EventFormClassifier, SustainedPressureDetector, EarlyExitHandler 통합
    - [Reinforcement] NerveTiming 단일 진입점, NerveFailsoft 보호
    - 단일 진입점 shouldProcess() API 제공
    - 컴포넌트 초기화/종료 조율
    
    EarlyExit 안전장치:
    - 첫 발생(First occurrence)은 절대 차단하지 않음
    - 동일 tick + 동일 contextKey 재진입만 대상
]]

require "Nerve/NerveUtils"
require "Nerve/NerveTiming"
require "Nerve/NerveFailsoft"
require "Nerve/area6/ContextExtractors"
require "Nerve/area6/EventDeduplicator"
require "Nerve/area6/CascadeGuard"
require "Nerve/area6/EventFormClassifier"
require "Nerve/area6/SustainedPressureDetector"
require "Nerve/area6/EarlyExitHandler"

--------------------------------------------------------------------------------
-- Area6Coordinator 모듈
--------------------------------------------------------------------------------

local Area6Coordinator = {}

-- 컴포넌트 참조
Area6Coordinator.deduplicator = Nerve.EventDeduplicator
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
    
    -- Deduplicator 초기화
    if Area6Coordinator.deduplicator then
        Area6Coordinator.deduplicator.onTickStart()
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
        
        -- Sustained 상태를 Early Exit Handler에 전달
        Area6Coordinator.earlyExitHandler.updateFromSustained(pressureResult.isSustained)
        
        -- [Phase 1-C] 이미 붕괴 상태 + contextKey 있음 → 추가 이벤트 개입 차단
        -- 의미 불변: 동일 틱·동일 contextKey만 대상
        if pressureResult.isSustained 
            and Area6Coordinator.earlyExitHandler.shouldIntervene()
            and contextKey ~= nil then
            -- 중복 경로 무음 탈락 (연쇄 이벤트 후속 처리)
            if Area6Coordinator.deduplicator 
                and Area6Coordinator.deduplicator.shouldSkip(eventName, contextKey) then
                return false
            end
        end
    end
    
    -- 1. Deduplicator 체크 (기존)
    if Area6Coordinator.deduplicator 
        and NerveConfig.area6.deduplicator 
        and NerveConfig.area6.deduplicator.enabled then
        
        if Area6Coordinator.deduplicator.shouldSkip(eventName, contextKey) then
            return false  -- 중복으로 스킵
        end
    end
    
    -- 2. CascadeGuard 체크
    if Area6Coordinator.cascadeGuard then
        if not Area6Coordinator.cascadeGuard.enter(eventName) then
            return false  -- 깊이 초과로 스킵
        end
        -- Note: CascadeGuard.exit()는 이벤트 완료 후 호출해야 하지만,
        -- v0.1에서는 observeOnly 모드이므로 생략해도 안전
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
        deduplicator = nil,
        cascadeGuard = nil,
        -- Phase 1
        formClassifier = nil,
        pressureDetector = nil,
        earlyExitHandler = nil,
    }
    
    if Area6Coordinator.deduplicator then
        stats.deduplicator = Area6Coordinator.deduplicator.getStats()
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
    
    -- Deduplicator 상태
    if Area6Coordinator.deduplicator then
        local stats = Area6Coordinator.deduplicator.getStats()
        NerveUtils.info("Deduplicator:")
        NerveUtils.info("  Total: " .. stats.totalCount)
        NerveUtils.info("  Skipped: " .. stats.skipCount)
        NerveUtils.info("  Entries: " .. stats.entryCount)
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
