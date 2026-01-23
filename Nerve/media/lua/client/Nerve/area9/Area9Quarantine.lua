--[[
    Area9Quarantine.lua
    Quarantine 상태 머신 (딱 1틱 철수)
    
    [필수-4] Quarantine 키 범위 강제
    - 전역 quarantine 키 금지
    - 기본: handler 단위
    - 확장(packetType+connKey)은 config 명시 시에만
    
    [헌법 준수]
    - ACTIVE → QUARANTINED_THIS_TICK → RESET_NEXT_TICK
    - until_tick[key] == tickId 1회 비교
    - 선리턴: 핸들러 직전 1회, 부분 실행 후 철수 금지
]]

require "Nerve/NerveUtils"
require "Nerve/area9/Area9TickCtx"
require "Nerve/area9/Area9Forensic"

--------------------------------------------------------------------------------
-- Area9Quarantine 모듈
--------------------------------------------------------------------------------

local Area9Quarantine = {}

-- Quarantine 상태 저장소
-- key: scopeKey, value: until_tick (이 tick까지 quarantine)
Area9Quarantine.untilTick = {}

--------------------------------------------------------------------------------
-- 키 생성 (필수-4 준수)
--------------------------------------------------------------------------------

-- 기본 키 생성 (handler 단위)
-- [필수-4] 전역 키 금지
function Area9Quarantine.makeKey(handlerId, packetType, connKey)
    -- config에서 확장 허용 목록 확인
    local allowedExtensions = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.quarantine 
        and NerveConfig.area9.quarantine.allowedExtensions 
        or {}
    
    local hasPacketType = false
    local hasConnKey = false
    
    for _, ext in ipairs(allowedExtensions) do
        if ext == "packetType" then hasPacketType = true end
        if ext == "connKey" then hasConnKey = true end
    end
    
    -- 기본: handler 단위
    local key = "handler:" .. tostring(handlerId)
    
    -- 확장 (config 명시 시에만)
    if hasPacketType and packetType then
        key = key .. ":pkt:" .. tostring(packetType)
    end
    if hasConnKey and connKey then
        key = key .. ":conn:" .. tostring(connKey)
    end
    
    return key
end

--------------------------------------------------------------------------------
-- Quarantine 체크 (선리턴 지점)
--------------------------------------------------------------------------------

-- Quarantine 상태 확인 (핸들러 직전 1회)
-- @param scopeKey: 스코프 키
-- @return: isQuarantined (선리턴 필요 여부)
function Area9Quarantine.check(scopeKey)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return false
    end
    
    local currentTick = TickCtx.getCurrentTickId()
    local untilTick = Area9Quarantine.untilTick[scopeKey]
    
    -- until_tick[key] == tickId 1회 비교
    if untilTick and untilTick >= currentTick then
        -- Quarantine 상태 → 선리턴
        return true
    end
    
    return false
end

--------------------------------------------------------------------------------
-- Quarantine 진입/해제
--------------------------------------------------------------------------------

-- Quarantine 진입 (동일 틱만)
-- @param scopeKey: 스코프 키
function Area9Quarantine.enter(scopeKey)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return
    end
    
    local currentTick = TickCtx.getCurrentTickId()
    
    -- 동일 틱만 quarantine (다음 틱 자동 복귀)
    Area9Quarantine.untilTick[scopeKey] = currentTick
    
    -- passthrough 등록
    TickCtx.markPassthrough(scopeKey)
    
    -- Forensic 기록
    local Forensic = Nerve.Area9Forensic
    if Forensic then
        Forensic.recordQuarantine(Forensic.ReasonCode.QUARANTINE_ENTER, 0, 0)
    end
end

-- Quarantine 해제 (수동, 보통은 tick 변경으로 자동 해제)
-- @param scopeKey: 스코프 키
function Area9Quarantine.exit(scopeKey)
    Area9Quarantine.untilTick[scopeKey] = nil
    
    -- Forensic 기록
    local Forensic = Nerve.Area9Forensic
    if Forensic then
        Forensic.recordQuarantine(Forensic.ReasonCode.QUARANTINE_EXIT, 0, 0)
    end
end

-- 만료된 quarantine 정리 (tick 변경 시)
function Area9Quarantine.cleanup()
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return
    end
    
    local currentTick = TickCtx.getCurrentTickId()
    
    for key, untilTick in pairs(Area9Quarantine.untilTick) do
        if untilTick < currentTick then
            Area9Quarantine.untilTick[key] = nil
        end
    end
end

-- opt-in 확인
function Area9Quarantine.isOptIn(scopeKey)
    local quarantine = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.optIn 
        and NerveConfig.area9.optIn.quarantine 
        or {}
    
    for _, key in ipairs(quarantine) do
        if key == scopeKey then
            return true
        end
    end
    
    return false
end

-- 통계 조회
function Area9Quarantine.getStats()
    local count = 0
    for _ in pairs(Area9Quarantine.untilTick) do
        count = count + 1
    end
    return { activeCount = count }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Quarantine = Area9Quarantine

return Area9Quarantine
