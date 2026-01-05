--[[
    InventoryGuard.lua
    ISInventoryPage.refreshBackpack 틱 단위 coalesce
    
    v0.1 Final
    
    핵심 기술:
    - WeakRef 레지스트리 (메모리 누수 방지)
    - 틱 단위 coalesce (ms 디바운스 아님!)
    - flush 시 원본 직접 호출 (래퍼 우회 → 루프 방지)
]]

require "Nerve/NerveUtils"
require "Nerve/area5/Area5Stats"

local InventoryGuard = {}

-- WeakRef 레지스트리 (GC 친화)
InventoryGuard.registry = setmetatable({}, { __mode = "k" })

--------------------------------------------------------------------------------
-- 초기화
--------------------------------------------------------------------------------

function InventoryGuard.init()
    if not NerveConfig.area5 or not NerveConfig.area5.inventoryGuard 
        or not NerveConfig.area5.inventoryGuard.enabled then
        NerveUtils.info("Area5: InventoryGuard disabled by config")
        return false
    end
    
    -- 이미 훅됨 체크 (중복 방지)
    if ISInventoryPage and ISInventoryPage.__nerveHooked then
        NerveUtils.info("Area5: InventoryGuard already hooked, skipping")
        return true
    end
    
    -- 대상 존재 체크 (Fail-soft)
    if not ISInventoryPage or not ISInventoryPage.refreshBackpack then
        NerveUtils.warn("Area5: ISInventoryPage.refreshBackpack not found")
        return false
    end
    
    -- 원본 보존
    ISInventoryPage.__nerveOriginal_refreshBackpack = ISInventoryPage.refreshBackpack
    
    -- 래핑
    ISInventoryPage.refreshBackpack = InventoryGuard.refreshWrapper
    
    -- 훅 완료 플래그
    ISInventoryPage.__nerveHooked = true
    
    NerveUtils.info("Area5: InventoryGuard initialized (hooked: refreshBackpack)")
    return true
end

--------------------------------------------------------------------------------
-- 래퍼
--------------------------------------------------------------------------------

function InventoryGuard.refreshWrapper(self)
    -- WeakRef 레지스트리 등록
    InventoryGuard.registry[self] = true
    
    -- 텔레메트리
    Area5Stats.wrapperCalls = Area5Stats.wrapperCalls + 1
    
    -- 틱 단위 coalesce
    if self.__nerve_refreshedThisTick then
        self.__nerve_pending = true
        Area5Stats.blockedCalls = Area5Stats.blockedCalls + 1
        
        if NerveConfig.debug then
            NerveUtils.debug("Area5: SKIP refreshBackpack (already refreshed this tick)")
        end
        return
    end
    
    self.__nerve_refreshedThisTick = true
    Area5Stats.originalCalls = Area5Stats.originalCalls + 1
    
    -- 원본 호출 (pcall 없이 - 에러는 그대로 전파)
    return ISInventoryPage.__nerveOriginal_refreshBackpack(self)
end

--------------------------------------------------------------------------------
-- 틱 처리
--------------------------------------------------------------------------------

-- 틱 시작: 플래그 초기화
function InventoryGuard.onTickStart()
    for panel in pairs(InventoryGuard.registry) do
        panel.__nerve_refreshedThisTick = nil
        -- pending은 유지 (flushPending에서 처리)
    end
end

-- 틱 끝: pending 플러시
function InventoryGuard.flushPending()
    for panel in pairs(InventoryGuard.registry) do
        -- javaObject만 체크 (isVisible 제거 - 정책 판단 금지)
        if panel.javaObject and panel.__nerve_pending then
            -- 원본 직접 호출 (래퍼 우회 → 루프 방지)
            local ok, err = pcall(ISInventoryPage.__nerveOriginal_refreshBackpack, panel)
            if ok then
                Area5Stats.pendingFlushed = Area5Stats.pendingFlushed + 1
            else
                NerveUtils.warn("Area5: flushPending error - " .. tostring(err))
            end
        end
        panel.__nerve_pending = nil
    end
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.InventoryGuard = InventoryGuard

return InventoryGuard
