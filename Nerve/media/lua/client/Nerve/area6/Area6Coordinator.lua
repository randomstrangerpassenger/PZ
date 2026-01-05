--[[
    Area6Coordinator.lua
    Area 6 통합 조율 모듈
    
    v0.1 Final
    
    핵심 역할:
    - EventDeduplicator, CascadeGuard 통합 관리
    - 단일 진입점 shouldProcess() API 제공
    - 컴포넌트 초기화/종료 조율
]]

require "Nerve/NerveUtils"
require "Nerve/area6/ContextExtractors"
require "Nerve/area6/EventDeduplicator"
require "Nerve/area6/CascadeGuard"

--------------------------------------------------------------------------------
-- Area6Coordinator 모듈
--------------------------------------------------------------------------------

local Area6Coordinator = {}

-- 컴포넌트 참조
Area6Coordinator.deduplicator = Nerve.EventDeduplicator
Area6Coordinator.cascadeGuard = Nerve.CascadeGuard
Area6Coordinator.contextExtractors = Nerve.ContextExtractors

--------------------------------------------------------------------------------
-- 틱 시작 처리
--------------------------------------------------------------------------------

function Area6Coordinator.onTickStart()
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
    
    -- 1. Deduplicator 체크
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
    }
    
    if Area6Coordinator.deduplicator then
        stats.deduplicator = Area6Coordinator.deduplicator.getStats()
    end
    
    if Area6Coordinator.cascadeGuard then
        stats.cascadeGuard = Area6Coordinator.cascadeGuard.getStats()
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
