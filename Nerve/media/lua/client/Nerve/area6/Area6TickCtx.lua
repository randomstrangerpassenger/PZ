--[[
    Area6TickCtx.lua
    Per-tick 컨텍스트 관리 모듈
    
    v1.0 - Phase 2: Context & Wrapper Standard
    
    핵심 역할:
    - 틱 단위 컨텍스트 생성/정리
    - callStack (재진입 검출용)
    - incidentFlags (사건 표식)
    - passthroughScopes (동일 틱 철수 스코프)
    
    [CONSTITUTION 준수]
    - 틱 종료 시 전부 wipe (누적 금지)
    - 상시 계측 없음
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area6TickCtx 모듈
--------------------------------------------------------------------------------

local Area6TickCtx = {}

-- 현재 틱 ID
Area6TickCtx.tickId = 0

-- 콜 스택 (eventName+listenerId -> depth)
Area6TickCtx.callStack = {}

-- 체인 ID 카운터
Area6TickCtx.chainIdCounter = 0

-- 현재 체인 컨텍스트 스택
Area6TickCtx.chainStack = {}

-- 사건 플래그 (이번 틱에 발생한 incident)
Area6TickCtx.incidentFlags = {
    hasReentry = false,
    hasError = false,
}

-- 철수 스코프 (동일 틱 pass-through 대상)
-- key: scopeKey (eventName + listenerId 또는 chainId)
Area6TickCtx.passthroughScopes = {}

-- 틱 초기화 완료 여부
Area6TickCtx.initialized = false

--------------------------------------------------------------------------------
-- 틱 생명주기
--------------------------------------------------------------------------------

-- 틱 시작
function Area6TickCtx.onTickStart()
    Area6TickCtx.tickId = Area6TickCtx.tickId + 1
    Area6TickCtx.chainIdCounter = 0
    Area6TickCtx.initialized = true
    
    -- 상태 wipe (누적 금지)
    NerveUtils.safeWipe(Area6TickCtx.callStack)
    NerveUtils.safeWipe(Area6TickCtx.chainStack)
    NerveUtils.safeWipe(Area6TickCtx.passthroughScopes)
    
    -- 사건 플래그 리셋
    Area6TickCtx.incidentFlags.hasReentry = false
    Area6TickCtx.incidentFlags.hasError = false
end

-- 틱 종료
function Area6TickCtx.onTickEnd()
    -- 전부 wipe (헌법: 누적 금지)
    NerveUtils.safeWipe(Area6TickCtx.callStack)
    NerveUtils.safeWipe(Area6TickCtx.chainStack)
    NerveUtils.safeWipe(Area6TickCtx.passthroughScopes)
    
    Area6TickCtx.incidentFlags.hasReentry = false
    Area6TickCtx.incidentFlags.hasError = false
    Area6TickCtx.initialized = false
end

--------------------------------------------------------------------------------
-- 콜 스택 관리
--------------------------------------------------------------------------------

-- 리스너 진입
-- @param eventName: 이벤트 이름
-- @param listenerId: 리스너 식별자 (함수 주소 등)
-- @return: 현재 깊이
function Area6TickCtx.enterListener(eventName, listenerId)
    local key = eventName .. ":" .. tostring(listenerId)
    local depth = (Area6TickCtx.callStack[key] or 0) + 1
    Area6TickCtx.callStack[key] = depth
    return depth
end

-- 리스너 종료
-- @param eventName: 이벤트 이름
-- @param listenerId: 리스너 식별자
function Area6TickCtx.exitListener(eventName, listenerId)
    local key = eventName .. ":" .. tostring(listenerId)
    local depth = Area6TickCtx.callStack[key] or 0
    if depth > 0 then
        Area6TickCtx.callStack[key] = depth - 1
    end
end

-- 현재 깊이 조회
function Area6TickCtx.getListenerDepth(eventName, listenerId)
    local key = eventName .. ":" .. tostring(listenerId)
    return Area6TickCtx.callStack[key] or 0
end

--------------------------------------------------------------------------------
-- 체인 관리
--------------------------------------------------------------------------------

-- 새 체인 시작
-- @return: 새 체인 ID
function Area6TickCtx.startChain()
    Area6TickCtx.chainIdCounter = Area6TickCtx.chainIdCounter + 1
    local chainId = Area6TickCtx.chainIdCounter
    
    -- 부모 체인 ID
    local parentChainId = Area6TickCtx.getCurrentChainId()
    
    table.insert(Area6TickCtx.chainStack, {
        id = chainId,
        parentId = parentChainId,
    })
    
    return chainId
end

-- 체인 종료
function Area6TickCtx.endChain()
    if #Area6TickCtx.chainStack > 0 then
        table.remove(Area6TickCtx.chainStack)
    end
end

-- 현재 체인 ID
function Area6TickCtx.getCurrentChainId()
    if #Area6TickCtx.chainStack > 0 then
        return Area6TickCtx.chainStack[#Area6TickCtx.chainStack].id
    end
    return 0
end

-- 현재 체인 깊이
function Area6TickCtx.getChainDepth()
    return #Area6TickCtx.chainStack
end

--------------------------------------------------------------------------------
-- 사건(Incident) 관리
--------------------------------------------------------------------------------

-- 재진입 사건 표시
function Area6TickCtx.markReentry()
    Area6TickCtx.incidentFlags.hasReentry = true
end

-- 에러 사건 표시
function Area6TickCtx.markError()
    Area6TickCtx.incidentFlags.hasError = true
end

-- 사건 발생 여부
function Area6TickCtx.hasIncident()
    return Area6TickCtx.incidentFlags.hasReentry 
        or Area6TickCtx.incidentFlags.hasError
end

-- 사건 플래그 조회
function Area6TickCtx.getIncidentFlags()
    return {
        hasReentry = Area6TickCtx.incidentFlags.hasReentry,
        hasError = Area6TickCtx.incidentFlags.hasError,
    }
end

--------------------------------------------------------------------------------
-- 철수(Pass-through) 스코프 관리
--------------------------------------------------------------------------------

-- 철수 스코프 등록
-- @param scopeKey: 스코프 식별자 (eventName:listenerId 또는 chainId)
function Area6TickCtx.markPassthrough(scopeKey)
    Area6TickCtx.passthroughScopes[scopeKey] = true
end

-- 철수 대상인지 확인
-- @param scopeKey: 스코프 식별자
-- @return: 철수 대상 여부
function Area6TickCtx.isPassthrough(scopeKey)
    return Area6TickCtx.passthroughScopes[scopeKey] == true
end

-- 리스너 스코프 키 생성
function Area6TickCtx.makeListenerScopeKey(eventName, listenerId)
    return eventName .. ":" .. tostring(listenerId)
end

--------------------------------------------------------------------------------
-- 컨텍스트 스냅샷
--------------------------------------------------------------------------------

-- 현재 컨텍스트 스냅샷 (증거용)
function Area6TickCtx.getSnapshot()
    return {
        tickId = Area6TickCtx.tickId,
        chainDepth = Area6TickCtx.getChainDepth(),
        currentChainId = Area6TickCtx.getCurrentChainId(),
        hasReentry = Area6TickCtx.incidentFlags.hasReentry,
        hasError = Area6TickCtx.incidentFlags.hasError,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6TickCtx = Area6TickCtx

return Area6TickCtx
