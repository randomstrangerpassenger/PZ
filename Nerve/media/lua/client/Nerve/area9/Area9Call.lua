--[[
    Area9Call.lua
    callFast/callGuarded 강제 분리
    
    [필수-3] Incident 조건은 단일 플래그만
    - reasonCode 존재 / quarantine 진입 같은 단일 플래그 기반만 허용
    - 빈도/비율/추세/가중치/복합 조건 금지
    
    [헌법 준수]
    - callFast: pcall 없음
    - callGuarded: pcall + opt-in만
    - 클로저 생성 금지!
    - Budget + TTL
]]

require "Nerve/NerveUtils"
require "Nerve/area9/Area9TickCtx"
require "Nerve/area9/Area9Forensic"

--------------------------------------------------------------------------------
-- Area9Call 모듈
--------------------------------------------------------------------------------

local Area9Call = {}

-- tick당 guarded 호출 카운터
Area9Call.guardedCountThisTick = 0
Area9Call.lastCountTick = 0

--------------------------------------------------------------------------------
-- 틱 관리
--------------------------------------------------------------------------------

local function ensureCurrentTick()
    local TickCtx = Nerve.Area9TickCtx
    local currentTick = TickCtx and TickCtx.getCurrentTickId() or 0
    
    if currentTick ~= Area9Call.lastCountTick then
        Area9Call.guardedCountThisTick = 0
        Area9Call.lastCountTick = currentTick
    end
end

--------------------------------------------------------------------------------
-- Budget/TTL 설정 조회
--------------------------------------------------------------------------------

local function getTickBudget()
    return NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.guardedPcall 
        and NerveConfig.area9.guardedPcall.tickBudget 
        or 10
end

local function getDefaultTTL()
    return NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.guardedPcall 
        and NerveConfig.area9.guardedPcall.defaultTTL 
        or 1
end

--------------------------------------------------------------------------------
-- callFast (pcall 없음)
--------------------------------------------------------------------------------

-- pcall 없이 직접 호출 (기본 경로)
-- @param fn: 실행할 함수
-- @param ...: 함수 인자
-- @return: 함수 반환값
function Area9Call.callFast(fn, ...)
    -- 단순 호출 (pcall 없음)
    return fn(...)
end

--------------------------------------------------------------------------------
-- callGuarded (pcall + opt-in만)
--------------------------------------------------------------------------------

-- pcall 격리 호출 (incident 조건 시에만)
-- [필수-3] incident 조건은 단일 플래그만
-- @param fn: 실행할 함수
-- @param scopeKey: 스코프 키
-- @param ...: 함수 인자
-- @return: success, result
function Area9Call.callGuarded(fn, scopeKey, ...)
    ensureCurrentTick()
    
    local TickCtx = Nerve.Area9TickCtx
    local Forensic = Nerve.Area9Forensic
    
    -- Budget 체크 (초과 시 callFast로 복귀)
    local budget = getTickBudget()
    if Area9Call.guardedCountThisTick >= budget then
        -- 예산 초과: callFast로 복귀 (폭주 방지)
        return true, Area9Call.callFast(fn, ...)
    end
    
    -- guarded 호출 카운트 증가
    Area9Call.guardedCountThisTick = Area9Call.guardedCountThisTick + 1
    
    -- pcall 실행
    local ok, result = pcall(fn, ...)
    
    if ok then
        return true, result
    end
    
    -- 에러 발생
    local errMsg = tostring(result)
    
    -- incident 표시 (단일 플래그)
    if TickCtx then
        TickCtx.markIncident("error")
        TickCtx.markPassthrough(scopeKey)
    end
    
    -- Forensic 기록
    if Forensic then
        Forensic.recordError(Forensic.ReasonCode.ERROR_PCALL, 0, 0)
    end
    
    -- 에러 로그 (레이트리밋은 Forensic에서)
    NerveUtils.warn("[Area9Call] Error in guarded call: " .. errMsg)
    
    return false, errMsg
end

--------------------------------------------------------------------------------
-- Incident 기반 경로 선택 (단일 플래그만)
--------------------------------------------------------------------------------

-- incident 발생 여부에 따라 callFast/callGuarded 선택
-- [필수-3] 단일 플래그 기반만 (복합 조건 금지)
-- @param fn: 실행할 함수
-- @param scopeKey: 스코프 키
-- @param ...: 함수 인자
-- @return: success, result
function Area9Call.call(fn, scopeKey, ...)
    local TickCtx = Nerve.Area9TickCtx
    
    -- opt-in 확인
    local isOptIn = Area9Call.isOptIn(scopeKey)
    
    -- [필수-3] 단일 플래그: incident 발생 여부만 체크
    local hasIncident = TickCtx and TickCtx.hasIncident()
    
    if isOptIn and hasIncident then
        -- incident 상태: guarded 경로
        return Area9Call.callGuarded(fn, scopeKey, ...)
    else
        -- 정상 상태: fast 경로
        return true, Area9Call.callFast(fn, ...)
    end
end

-- opt-in 확인
function Area9Call.isOptIn(scopeKey)
    local guardedPcall = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.optIn 
        and NerveConfig.area9.optIn.guardedPcall 
        or {}
    
    for _, key in ipairs(guardedPcall) do
        if key == scopeKey then
            return true
        end
    end
    
    return false
end

-- 통계 조회
function Area9Call.getStats()
    return {
        guardedCountThisTick = Area9Call.guardedCountThisTick,
        budget = getTickBudget(),
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Call = Area9Call

return Area9Call
