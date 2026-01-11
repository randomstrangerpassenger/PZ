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
-- [P2-1 Fail-soft 예외 정책]
--   1. Nerve 부가 로직 오류 → pcall 삼킴 + fail-soft 기록 + 원본 호출
--   2. 원본(바닐라) 호출 오류 → 그대로 전파 (바닐라 동작 유지)
-- 이유: 디버깅 시 "Nerve가 촉발했다" 착시 방지, 책임소재 명확화
--------------------------------------------------------------------------------

function InventoryGuard.refreshWrapper(self)
    -- [Fail-soft] Nerve 로직 체크
    if Nerve.Failsoft and not Nerve.Failsoft.isEnabled("InventoryGuard") then
        -- Nerve 비활성화 → 원본 직접 호출
        return ISInventoryPage.__nerveOriginal_refreshBackpack(self)
    end
    
    -- Nerve 로직을 pcall로 보호
    local nerveOk, nerveErr = pcall(function()
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
            return "skip"  -- 스킵 신호
        end
        
        self.__nerve_refreshedThisTick = true
        Area5Stats.originalCalls = Area5Stats.originalCalls + 1
        return "proceed"
    end)
    
    -- Nerve 로직 오류 시 fail-soft 후 원본 실행
    if not nerveOk then
        if Nerve.Failsoft then
            Nerve.Failsoft.recordError("InventoryGuard", nerveErr)
        end
        -- 원본 호출 (Nerve 실패해도 기능은 유지)
        return ISInventoryPage.__nerveOriginal_refreshBackpack(self)
    end
    
    -- 스킵 신호면 리턴
    if nerveErr == "skip" then
        return
    end
    
    -- 원본 호출 (오류 시 그대로 전파 - 바닐라 동작 유지)
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
-- [P2-1 Fail-soft 정책] 정리 단계에서의 오류 삼킴:
--   - 이 함수는 "정리/보조" 단계 (데이터는 이미 반영됨)
--   - 원본 오류 발생 시 로그만 남기고 진행 (flush 실패가 다른 패널에 영향 X)
--   - 사용자 경험 연속성 유지 목적
function InventoryGuard.flushPending()
    for panel in pairs(InventoryGuard.registry) do
        -- javaObject만 체크 (isVisible 제거 - 정책 판단 금지)
        if panel.javaObject and panel.__nerve_pending then
            -- 원본 직접 호출 (래퍼 우회 → 루프 방지)
            -- [정책] pcall 삼킴: 정리 단계, 로그 기록 후 계속 진행
            local ok, err = pcall(ISInventoryPage.__nerveOriginal_refreshBackpack, panel)
            if ok then
                Area5Stats.pendingFlushed = Area5Stats.pendingFlushed + 1
            else
                -- 오류 기록만, 전파하지 않음 (정리 단계)
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
