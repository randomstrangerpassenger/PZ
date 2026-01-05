--[[
    Area5Stats.lua
    Area 5 텔레메트리 (관측 지표)
    
    v0.1 Final
]]

Area5Stats = Area5Stats or {
    -- InventoryGuard 통계
    wrapperCalls = 0,       -- wrapper 총 호출 수
    originalCalls = 0,      -- 원본 실제 실행 수
    blockedCalls = 0,       -- coalesce로 차단된 수
    pendingFlushed = 0,     -- flush로 실행된 수
    
    -- UIRefreshCoalescer 통계
    overflowCount = 0,      -- overflow 발생 횟수
    
    -- ContainerScanDedup 통계
    scanRequests = 0,       -- 스캔 요청 총 수
    scanSkipped = 0,        -- 중복 스킵 수
}

-- coalesce_ratio = blockedCalls / wrapperCalls (관측 지표)
-- 비율이 높을수록 중복 갱신이 많이 차단됨

function Area5Stats.reset()
    Area5Stats.wrapperCalls = 0
    Area5Stats.originalCalls = 0
    Area5Stats.blockedCalls = 0
    Area5Stats.pendingFlushed = 0
    Area5Stats.overflowCount = 0
    Area5Stats.scanRequests = 0
    Area5Stats.scanSkipped = 0
end

function Area5Stats.getCoalesceRatio()
    if Area5Stats.wrapperCalls == 0 then
        return 0
    end
    return Area5Stats.blockedCalls / Area5Stats.wrapperCalls
end

function Area5Stats.print()
    NerveUtils.info("========================================")
    NerveUtils.info("Area 5 Statistics")
    NerveUtils.info("========================================")
    NerveUtils.info("  Wrapper calls:   " .. Area5Stats.wrapperCalls)
    NerveUtils.info("  Original calls:  " .. Area5Stats.originalCalls)
    NerveUtils.info("  Blocked calls:   " .. Area5Stats.blockedCalls)
    NerveUtils.info("  Pending flushed: " .. Area5Stats.pendingFlushed)
    NerveUtils.info("  Overflow count:  " .. Area5Stats.overflowCount)
    NerveUtils.info("  Coalesce ratio:  " .. string.format("%.2f%%", Area5Stats.getCoalesceRatio() * 100))
    NerveUtils.info("----------------------------------------")
    NerveUtils.info("  Scan requests:   " .. Area5Stats.scanRequests)
    NerveUtils.info("  Scan skipped:    " .. Area5Stats.scanSkipped)
    NerveUtils.info("========================================")
end

return Area5Stats
