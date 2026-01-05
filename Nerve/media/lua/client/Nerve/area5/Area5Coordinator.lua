--[[
    Area5Coordinator.lua
    Area 5 통합 조율 모듈
    
    v0.1 Final
    
    핵심 역할:
    - 컴포넌트 초기화 순서 관리
    - 지연 초기화 재시도 (3회)
    - onTickStart/End 조율
    
    훅 지점:
    - onTickStart: Events.OnTick 시작부 (Area 6과 동일)
    - onTickEnd: Events.OnTickEven 또는 OnTick 말미
]]

require "Nerve/NerveUtils"
require "Nerve/area5/Area5Stats"
require "Nerve/area5/ContainerScanDedup"
require "Nerve/area5/UIRefreshCoalescer"
require "Nerve/area5/InventoryGuard"

local Area5Coordinator = {}

Area5Coordinator.initialized = false
Area5Coordinator.retryCount = 0

--------------------------------------------------------------------------------
-- 초기화
--------------------------------------------------------------------------------

function Area5Coordinator.init()
    -- 설정 체크
    if not NerveConfig.area5 or not NerveConfig.area5.enabled then
        NerveUtils.info("Area5: Disabled by config")
        return false
    end
    
    NerveUtils.info("----------------------------------------")
    NerveUtils.info("Area 5: UI/Inventory Stabilization")
    NerveUtils.info("\"Data immediate, visuals coalesced\"")
    NerveUtils.info("----------------------------------------")
    
    -- InventoryGuard 초기화 시도
    local success = Nerve.InventoryGuard.init()
    
    if not success then
        -- 지연 초기화 활성화
        if NerveConfig.area5.retryInit and NerveConfig.area5.retryInit.enabled then
            NerveUtils.info("Area5: InventoryGuard init failed, will retry...")
            Events.OnTick.Add(Area5Coordinator.retryInit)
        else
            NerveUtils.warn("Area5: InventoryGuard init failed (retry disabled)")
        end
    end
    
    Area5Coordinator.initialized = true
    NerveUtils.info("Area5: Initialization complete")
    
    return true
end

--------------------------------------------------------------------------------
-- 지연 초기화 재시도
--------------------------------------------------------------------------------

function Area5Coordinator.retryInit()
    Area5Coordinator.retryCount = Area5Coordinator.retryCount + 1
    
    local maxRetries = 3
    if NerveConfig.area5 and NerveConfig.area5.retryInit then
        maxRetries = NerveConfig.area5.retryInit.maxRetries or maxRetries
    end
    
    if Nerve.InventoryGuard.init() then
        Events.OnTick.Remove(Area5Coordinator.retryInit)
        NerveUtils.info("Area5: Late init successful (retry #" .. Area5Coordinator.retryCount .. ")")
    elseif Area5Coordinator.retryCount >= maxRetries then
        Events.OnTick.Remove(Area5Coordinator.retryInit)
        NerveUtils.warn("Area5: Init failed after " .. maxRetries .. " retries - vanilla mode")
    end
end

--------------------------------------------------------------------------------
-- 틱 처리
--------------------------------------------------------------------------------

-- 틱 시작 (훅 지점: Events.OnTick 시작부)
function Area5Coordinator.onTickStart()
    if not Area5Coordinator.initialized then return end
    
    -- 순서: 상태 초기화
    Nerve.InventoryGuard.onTickStart()
    Nerve.UIRefreshCoalescer.onTickStart()
    Nerve.ContainerScanDedup.onTickStart()
end

-- 틱 끝 (훅 지점: Events.OnTickEven 또는 OnTick 말미)
function Area5Coordinator.onTickEnd()
    if not Area5Coordinator.initialized then return end
    
    -- 순서 중요!
    -- 1. UIRefreshCoalescer flush (범용) - executeFn 없으면 NOP
    Nerve.UIRefreshCoalescer.flush()
    
    -- 2. InventoryGuard flush (특화)
    Nerve.InventoryGuard.flushPending()
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function Area5Coordinator.getStats()
    return {
        initialized = Area5Coordinator.initialized,
        retryCount = Area5Coordinator.retryCount,
        area5Stats = Area5Stats,
    }
end

function Area5Coordinator.printStatus()
    NerveUtils.info("========================================")
    NerveUtils.info("Area 5 Status")
    NerveUtils.info("========================================")
    NerveUtils.info("  Initialized: " .. tostring(Area5Coordinator.initialized))
    NerveUtils.info("  Retry count: " .. Area5Coordinator.retryCount)
    
    -- 통계 출력
    Area5Stats.print()
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area5 = Area5Coordinator

return Area5Coordinator
