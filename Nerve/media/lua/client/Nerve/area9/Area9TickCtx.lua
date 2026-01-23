--[[
    Area9TickCtx.lua
    Per-tick 컨텍스트 관리 모듈 (네트워크/멀티 경계)
    
    [CONSTITUTION - 필수-1] tickId 단일 진실의 소스
    - tickId 갱신은 이 모듈에서만
    - 다른 모듈은 tickId 계산/추정 금지
    - tickId 변경 시 tick-local 상태 무조건 RESET
    
    핵심 역할:
    - 틱 단위 컨텍스트 생성/정리
    - 네트워크 경계 상태 추적
    - 철수(passthrough) 스코프 관리
    
    [헌법 준수]
    - 틱 종료 시 전부 wipe (누적 금지)
    - 상시 계측 없음
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area9TickCtx 모듈
--------------------------------------------------------------------------------

local Area9TickCtx = {}

-- 현재 틱 ID (유일한 갱신 지점)
Area9TickCtx.tickId = 0

-- 이전 틱 ID (tick 변경 감지용)
Area9TickCtx.prevTickId = 0

-- 철수 스코프 (동일 틱 pass-through 대상)
-- key: scopeKey (handler 또는 packetType+connKey)
Area9TickCtx.passthroughScopes = {}

-- Re-entrancy 상태
-- key: scopeKey, value: "ENTERED" | "BYPASS_THIS_TICK"
Area9TickCtx.reentryState = {}

-- Duplicate 카운터 (tick-local)
-- key: (packetType, connKey), value: count
Area9TickCtx.dupCounters = {}

-- Depth 상태 (domain별)
-- key: domain enum, value: depth
Area9TickCtx.depthState = {}

-- Incident 플래그
Area9TickCtx.incidentFlags = {
    hasReentry = false,
    hasError = false,
    hasShapeFail = false,
    hasDepthExceed = false,
}

-- 초기화 완료 여부
Area9TickCtx.initialized = false

--------------------------------------------------------------------------------
-- 틱 생명주기
--------------------------------------------------------------------------------

-- [필수-1] 틱 시작 - tickId 유일 갱신 지점
-- @param tickId: 외부에서 전달받은 틱 ID
function Area9TickCtx.onTickStart(tickId)
    -- tickId 변경 여부 확인
    local tickChanged = (tickId ~= Area9TickCtx.tickId)
    
    -- tickId 갱신 (유일한 갱신 지점)
    Area9TickCtx.prevTickId = Area9TickCtx.tickId
    Area9TickCtx.tickId = tickId
    Area9TickCtx.initialized = true
    
    -- tickId 변경 시 tick-local 상태 무조건 RESET
    if tickChanged then
        Area9TickCtx.resetTickLocalState()
    end
end

-- tick-local 상태 RESET (영구 quarantine/bypass 방지)
function Area9TickCtx.resetTickLocalState()
    NerveUtils.safeWipe(Area9TickCtx.passthroughScopes)
    NerveUtils.safeWipe(Area9TickCtx.reentryState)
    NerveUtils.safeWipe(Area9TickCtx.dupCounters)
    NerveUtils.safeWipe(Area9TickCtx.depthState)
    
    -- Incident 플래그 리셋
    Area9TickCtx.incidentFlags.hasReentry = false
    Area9TickCtx.incidentFlags.hasError = false
    Area9TickCtx.incidentFlags.hasShapeFail = false
    Area9TickCtx.incidentFlags.hasDepthExceed = false
end

-- 틱 종료
function Area9TickCtx.onTickEnd()
    Area9TickCtx.resetTickLocalState()
    Area9TickCtx.initialized = false
end

--------------------------------------------------------------------------------
-- 현재 틱 ID 조회 (읽기 전용)
--------------------------------------------------------------------------------

-- 다른 모듈은 이 함수로만 tickId 접근 (계산/추정 금지)
function Area9TickCtx.getCurrentTickId()
    return Area9TickCtx.tickId
end

--------------------------------------------------------------------------------
-- 철수(Pass-through) 스코프 관리
--------------------------------------------------------------------------------

-- 철수 스코프 등록
-- @param scopeKey: 스코프 식별자 (handler 또는 packetType+connKey)
function Area9TickCtx.markPassthrough(scopeKey)
    Area9TickCtx.passthroughScopes[scopeKey] = true
end

-- 철수 대상인지 확인
-- @param scopeKey: 스코프 식별자
-- @return: 철수 대상 여부
function Area9TickCtx.isPassthrough(scopeKey)
    return Area9TickCtx.passthroughScopes[scopeKey] == true
end

--------------------------------------------------------------------------------
-- Re-entrancy 상태 관리
--------------------------------------------------------------------------------

-- Re-entrancy 상태 조회
-- @param scopeKey: 스코프 식별자
-- @return: 상태 ("ENTERED" | "BYPASS_THIS_TICK" | nil)
function Area9TickCtx.getReentryState(scopeKey)
    return Area9TickCtx.reentryState[scopeKey]
end

-- Re-entrancy 상태 설정
-- @param scopeKey: 스코프 식별자
-- @param state: 상태 ("ENTERED" | "BYPASS_THIS_TICK")
function Area9TickCtx.setReentryState(scopeKey, state)
    Area9TickCtx.reentryState[scopeKey] = state
end

--------------------------------------------------------------------------------
-- Duplicate 카운터 관리
--------------------------------------------------------------------------------

-- Duplicate 카운트 증가
-- @param key: (packetType, connKey) 조합
-- @return: 현재 카운트
function Area9TickCtx.incDupCount(key)
    local count = (Area9TickCtx.dupCounters[key] or 0) + 1
    Area9TickCtx.dupCounters[key] = count
    return count
end

-- Duplicate 카운트 조회
function Area9TickCtx.getDupCount(key)
    return Area9TickCtx.dupCounters[key] or 0
end

--------------------------------------------------------------------------------
-- Depth 상태 관리
--------------------------------------------------------------------------------

-- Depth 증가
-- @param domain: domain enum (정수)
-- @return: 현재 depth
function Area9TickCtx.incDepth(domain)
    local depth = (Area9TickCtx.depthState[domain] or 0) + 1
    Area9TickCtx.depthState[domain] = depth
    return depth
end

-- Depth 감소 (음수 클램프)
-- @param domain: domain enum (정수)
-- @return: 현재 depth
function Area9TickCtx.decDepth(domain)
    local depth = (Area9TickCtx.depthState[domain] or 0) - 1
    if depth < 0 then depth = 0 end
    Area9TickCtx.depthState[domain] = depth
    return depth
end

-- Depth 조회
function Area9TickCtx.getDepth(domain)
    return Area9TickCtx.depthState[domain] or 0
end

--------------------------------------------------------------------------------
-- Incident 관리
--------------------------------------------------------------------------------

-- Incident 발생 여부 (단일 플래그 기반 - 필수-3)
function Area9TickCtx.hasIncident()
    return Area9TickCtx.incidentFlags.hasReentry
        or Area9TickCtx.incidentFlags.hasError
        or Area9TickCtx.incidentFlags.hasShapeFail
        or Area9TickCtx.incidentFlags.hasDepthExceed
end

-- Incident 플래그 설정
function Area9TickCtx.markIncident(type)
    if type == "reentry" then
        Area9TickCtx.incidentFlags.hasReentry = true
    elseif type == "error" then
        Area9TickCtx.incidentFlags.hasError = true
    elseif type == "shapeFail" then
        Area9TickCtx.incidentFlags.hasShapeFail = true
    elseif type == "depthExceed" then
        Area9TickCtx.incidentFlags.hasDepthExceed = true
    end
end

--------------------------------------------------------------------------------
-- 스코프 키 생성 헬퍼
--------------------------------------------------------------------------------

-- handler 단위 키 생성 (기본)
function Area9TickCtx.makeHandlerKey(handlerId)
    return "handler:" .. tostring(handlerId)
end

-- packetType + connKey 확장 키 생성 (config 명시 시에만)
function Area9TickCtx.makeExtendedKey(packetType, connKey)
    return "pkt:" .. tostring(packetType) .. ":conn:" .. tostring(connKey)
end

--------------------------------------------------------------------------------
-- 컨텍스트 스냅샷 (Forensic용)
--------------------------------------------------------------------------------

function Area9TickCtx.getSnapshot()
    return {
        tickId = Area9TickCtx.tickId,
        hasReentry = Area9TickCtx.incidentFlags.hasReentry,
        hasError = Area9TickCtx.incidentFlags.hasError,
        hasShapeFail = Area9TickCtx.incidentFlags.hasShapeFail,
        hasDepthExceed = Area9TickCtx.incidentFlags.hasDepthExceed,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9TickCtx = Area9TickCtx

return Area9TickCtx
