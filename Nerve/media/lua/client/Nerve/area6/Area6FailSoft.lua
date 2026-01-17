--[[
    Area6FailSoft.lua
    Fail-Soft 격리 모듈 (xpcall 기반)
    
    핵심 역할:
    - 리스너 단위 xpcall 격리
    - 예외 발생 시 incident 표시 + 동일 틱 철수
    - 에러 서명 기반 레이트리밋 로그
    
    [CONSTITUTION 준수]
    - Nerve는 예외를 새로 만들거나 흐름을 바꾸지 않음
    - 침묵 금지: 사건 표식 + 로그 필수
    - 원본 경로 행위 보존
]]

require "Nerve/NerveUtils"
require "Nerve/area6/Area6TickCtx"
require "Nerve/area6/Area6ErrorSig"
require "Nerve/area6/Area6InstallState"

--------------------------------------------------------------------------------
-- Area6FailSoft 모듈
--------------------------------------------------------------------------------

local Area6FailSoft = {}

-- 레이트리밋 상태 (틱 단위 wipe)
Area6FailSoft.rateLimitState = {}
Area6FailSoft.lastWipeTick = 0

-- 레이트리밋 설정
local RATE_LIMIT_COUNT = 3  -- 동일 서명 최대 출력 횟수

--------------------------------------------------------------------------------
-- 틱 관리
--------------------------------------------------------------------------------

local function ensureCurrentTick()
    local currentTick = Nerve.Area6TickCtx and Nerve.Area6TickCtx.tickId or 0
    
    if currentTick ~= Area6FailSoft.lastWipeTick then
        NerveUtils.safeWipe(Area6FailSoft.rateLimitState)
        Area6FailSoft.lastWipeTick = currentTick
    end
end

--------------------------------------------------------------------------------
-- 격리된 리스너 실행
--------------------------------------------------------------------------------

-- 리스너를 pcall로 격리 실행 (PZ Kahlua에는 xpcall 없음)
-- @param eventName: 이벤트 이름
-- @param listenerId: 리스너 식별자
-- @param listener: 원본 리스너 함수
-- @param ...: 리스너 인자
-- @return: success, result 또는 error
function Area6FailSoft.executeIsolated(eventName, listenerId, listener, ...)
    ensureCurrentTick()
    
    -- listener nil 체크
    if type(listener) ~= "function" then
        NerveUtils.warn("[Area6FailSoft] Invalid listener: " .. tostring(listener))
        return false, "listener is not a function"
    end
    
    local TickCtx = Nerve.Area6TickCtx
    local InstallState = Nerve.Area6InstallState
    
    -- pcall 실행 (PZ Kahlua에는 xpcall이 없음)
    local ok, result = pcall(listener, ...)
    
    if ok then
        -- 정상 실행
        return true, result
    end
    
    -- 에러 발생
    local errMsg = tostring(result)
    
    -- 1. incident 표시
    if TickCtx then
        TickCtx.markError()
    end
    
    -- 2. 동일 틱 철수 스코프 등록
    if TickCtx then
        local scopeKey = TickCtx.makeListenerScopeKey(eventName, listenerId)
        TickCtx.markPassthrough(scopeKey)
    end
    
    -- 3. 에러 서명 추출
    local ErrorSig = Nerve.Area6ErrorSig
    local signature = ErrorSig and ErrorSig.extractSignature(errMsg) or "unknown"
    
    -- 4. 레이트리밋 체크
    local rateLimitKey = eventName .. "|" .. tostring(listenerId) .. "|" .. signature
    local logCount = Area6FailSoft.rateLimitState[rateLimitKey] or 0
    
    if logCount < RATE_LIMIT_COUNT then
        -- 5. 침묵 금지: 사건 로그 출력
        local installState = InstallState and InstallState.getState() or "unknown"
        
        NerveUtils.warn("==========================================")
        NerveUtils.warn("[Area6] INCIDENT: error")
        NerveUtils.warn("  eventId: " .. eventName)
        NerveUtils.warn("  listenerId: " .. tostring(listenerId))
        NerveUtils.warn("  signature: " .. signature)
        NerveUtils.warn("  installState: " .. installState)
        NerveUtils.warn("  action: SAME_TICK_PASSTHROUGH")
        
        -- 디버그 모드면 전체 스택
        if NerveConfig and NerveConfig.debug then
            NerveUtils.warn("  stack:")
            for line in string.gmatch(errMsg, "[^\n]+") do
                NerveUtils.warn("    " .. line)
            end
        end
        
        NerveUtils.warn("==========================================")
        
        Area6FailSoft.rateLimitState[rateLimitKey] = logCount + 1
    elseif logCount == RATE_LIMIT_COUNT then
        -- 레이트리밋 도달 알림
        NerveUtils.warn("[Area6] Rate limit reached for: " .. rateLimitKey)
        Area6FailSoft.rateLimitState[rateLimitKey] = logCount + 1
    end
    -- 이후 중복은 무시 (레이트리밋)
    
    return false, errMsg
end

--------------------------------------------------------------------------------
-- 유틸리티
--------------------------------------------------------------------------------

-- 현재 레이트리밋 상태 조회
function Area6FailSoft.getRateLimitStats()
    local count = 0
    for _ in pairs(Area6FailSoft.rateLimitState) do
        count = count + 1
    end
    return { uniqueErrors = count }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6FailSoft = Area6FailSoft

return Area6FailSoft
