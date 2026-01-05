--[[
    ContainerScanDedup.lua
    컨테이너 스캔 중복 제거
    
    v0.1 Final
    
    원칙:
    - 틱 내 동일 스캔 스킵
    - 틱 경계에서 초기화 (캐시 금지)
]]

require "Nerve/NerveUtils"
require "Nerve/area5/Area5Stats"

local ContainerScanDedup = {}

ContainerScanDedup.scannedThisTick = {}

--------------------------------------------------------------------------------
-- 스캔 중복 체크
--------------------------------------------------------------------------------

-- 컨테이너 스캔 여부 판단
-- @param containerId: 컨테이너 식별자
-- @return: true (스캔 필요), false (이미 스캔됨)
function ContainerScanDedup.shouldScan(containerId)
    if not NerveConfig.area5 or not NerveConfig.area5.containerScan 
        or not NerveConfig.area5.containerScan.enabled then
        return true  -- 비활성화 시 항상 허용
    end
    
    Area5Stats.scanRequests = Area5Stats.scanRequests + 1
    
    if ContainerScanDedup.scannedThisTick[containerId] then
        Area5Stats.scanSkipped = Area5Stats.scanSkipped + 1
        if NerveConfig.debug then
            NerveUtils.debug("Area5: SKIP scan - " .. tostring(containerId))
        end
        return false
    end
    
    ContainerScanDedup.scannedThisTick[containerId] = true
    return true
end

--------------------------------------------------------------------------------
-- 틱 초기화
--------------------------------------------------------------------------------

function ContainerScanDedup.onTickStart()
    NerveUtils.safeWipe(ContainerScanDedup.scannedThisTick)
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.ContainerScanDedup = ContainerScanDedup

return ContainerScanDedup
