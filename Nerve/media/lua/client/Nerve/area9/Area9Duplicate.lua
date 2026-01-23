--[[
    Area9Duplicate.lua
    Duplicate Guard (카운트만)
    
    [헌법 준수]
    - 키: (packetType, connKey) 조합
    - tick-local counter map (wipe 재사용)
    - Phase 2: 스킵/선리턴 금지 (관측만)
]]

require "Nerve/NerveUtils"
require "Nerve/area9/Area9TickCtx"
require "Nerve/area9/Area9Forensic"

--------------------------------------------------------------------------------
-- Area9Duplicate 모듈
--------------------------------------------------------------------------------

local Area9Duplicate = {}

-- 고카운트 경고 임계값
Area9Duplicate.HIGH_COUNT_THRESHOLD = 10

--------------------------------------------------------------------------------
-- Duplicate 체크 (카운트만, 스킵 금지)
--------------------------------------------------------------------------------

-- 중복 체크 및 카운트 증가
-- @param packetType: 패킷 타입
-- @param connKey: 연결 키
-- @return: count (현재 카운트), isHigh (임계값 초과 여부)
function Area9Duplicate.check(packetType, connKey)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return 1, false
    end
    
    -- 키 생성
    local key = tostring(packetType) .. ":" .. tostring(connKey)
    
    -- 카운트 증가
    local count = TickCtx.incDupCount(key)
    
    -- 고카운트 체크 (관측만, 스킵 금지)
    local isHigh = count >= Area9Duplicate.HIGH_COUNT_THRESHOLD
    
    if isHigh and count == Area9Duplicate.HIGH_COUNT_THRESHOLD then
        -- 첫 번째 임계값 도달 시에만 기록 (레이트리밋)
        local Forensic = Nerve.Area9Forensic
        if Forensic then
            Forensic.recordDuplicate(Forensic.ReasonCode.DUP_COUNT_HIGH, count, 0)
        end
    end
    
    return count, isHigh
end

-- 현재 카운트 조회
function Area9Duplicate.getCount(packetType, connKey)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return 0
    end
    
    local key = tostring(packetType) .. ":" .. tostring(connKey)
    return TickCtx.getDupCount(key)
end

-- 통계 조회
function Area9Duplicate.getStats()
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return { totalKeys = 0, maxCount = 0 }
    end
    
    local totalKeys = 0
    local maxCount = 0
    
    for _, count in pairs(TickCtx.dupCounters) do
        totalKeys = totalKeys + 1
        if count > maxCount then
            maxCount = count
        end
    end
    
    return {
        totalKeys = totalKeys,
        maxCount = maxCount,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Duplicate = Area9Duplicate

return Area9Duplicate
