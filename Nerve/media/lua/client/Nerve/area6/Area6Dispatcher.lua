--[[
    Area6Dispatcher.lua
    통합 실행 흐름 (The "Sealed" Flow)
    
    v1.0 - Phase 6: Dispatcher
    
    핵심 역할:
    - 아래 순서를 코드로 봉인 (변경 금지)
    
    [SEALED EXECUTION ORDER]
    1. if !area6.enabled -> original
    2. if passthroughThisTick(scope) -> original
    3. reentry check -> if hit: mark incident + passthrough(scope)
    4. xpcall listener -> if error: mark incident + passthrough(scope)
    5. if incident: lazy evidence collect + emit summary (rate-limited)
    6. return
    
    [CONSTITUTION 준수]
    - 철수는 동일 틱 한정
    - tick end에서 자동 초기화 (wipe)
    - Drop/Delay/Reorder 금지
]]

require "Nerve/NerveUtils"
require "Nerve/area6/Area6Guard"
require "Nerve/area6/Area6TickCtx"
require "Nerve/area6/Area6Reentry"
require "Nerve/area6/Area6FailSoft"
require "Nerve/area6/Area6Evidence"
require "Nerve/area6/Area6DupCount"
require "Nerve/area6/Area6Depth"
require "Nerve/area6/Area6Fanout"
require "Nerve/area6/Area6Repeat"

--------------------------------------------------------------------------------
-- Area6Dispatcher 모듈
--------------------------------------------------------------------------------

local Area6Dispatcher = {}

--------------------------------------------------------------------------------
-- [SEALED] 실행 흐름 (순서 변경 금지)
--------------------------------------------------------------------------------

-- 리스너 디스패치
-- @param eventName: 이벤트 이름
-- @param listener: 원본 리스너 함수
-- @param ...: 리스너 인자
-- @return: 리스너 반환값 또는 nil
function Area6Dispatcher.dispatch(eventName, listener, ...)
    local listenerId = tostring(listener)
    
    -- [STEP 1] enabled 체크 -> 비활성화면 원본 호출
    if not NerveConfig 
        or not NerveConfig.area6 
        or not NerveConfig.area6.enabled then
        return listener(...)
    end
    
    local TickCtx = Nerve.Area6TickCtx
    local Reentry = Nerve.Area6Reentry
    local FailSoft = Nerve.Area6FailSoft
    local Evidence = Nerve.Area6Evidence
    
    -- 스코프 키 생성
    local scopeKey = TickCtx and TickCtx.makeListenerScopeKey(eventName, listenerId) or nil
    
    -- [STEP 2] 이미 철수 대상이면 원본 호출 (동일 틱 pass-through)
    if TickCtx and scopeKey and TickCtx.isPassthrough(scopeKey) then
        return listener(...)
    end
    
    -- 체인 시작
    if TickCtx then
        TickCtx.startChain()
    end
    
    -- [STEP 3] 재진입 체크 -> hit 시 incident + passthrough
    if Reentry and Reentry.isEnabled() then
        local result = Reentry.checkReentry(eventName, listenerId)
        
        if result.isReentry then
            -- incident 표시 + 철수 등록
            Reentry.handleReentryTrigger(eventName, listenerId, result.depth)
            
            -- [STEP 5] incident 발생 -> 증거 수집
            if Evidence then
                Evidence.collect(eventName, listenerId, "reentry")
                Evidence.emitSummary()
            end
            
            -- 체인 종료
            if TickCtx then
                TickCtx.endChain()
            end
            
            -- 철수 후 원본 호출
            return listener(...)
        end
    end
    
    -- 리스너 진입 등록
    if TickCtx then
        TickCtx.enterListener(eventName, listenerId)
    end
    
    -- 증거 기록 (평시: 비용 최소)
    if Nerve.Area6DupCount then
        Nerve.Area6DupCount.record(eventName, listenerId)
    end
    if Nerve.Area6Depth then
        Nerve.Area6Depth.record()
    end
    if Nerve.Area6Fanout then
        Nerve.Area6Fanout.recordExecution()
    end
    if Nerve.Area6Repeat then
        -- targetId 없이 기본 기록
        Nerve.Area6Repeat.record(eventName, listenerId, nil)
    end
    
    -- [STEP 4] xpcall 격리 실행 -> 에러 시 incident + passthrough
    local success, result
    
    if FailSoft then
        success, result = FailSoft.executeIsolated(eventName, listenerId, listener, ...)
        
        if not success then
            -- [STEP 5] incident 발생 -> 증거 수집
            if Evidence then
                Evidence.collect(eventName, listenerId, "error")
                Evidence.emitSummary()
            end
        end
    else
        -- FailSoft 없으면 직접 호출 (폴백)
        success, result = pcall(listener, ...)
    end
    
    -- 리스너 종료 등록
    if TickCtx then
        TickCtx.exitListener(eventName, listenerId)
    end
    
    -- 체인 종료
    if TickCtx then
        TickCtx.endChain()
    end
    
    -- [STEP 6] 반환
    if success then
        return result
    else
        -- 에러 시 nil 반환 (철수 완료, 로그는 FailSoft에서 처리됨)
        return nil
    end
end

--------------------------------------------------------------------------------
-- 유틸리티
--------------------------------------------------------------------------------

-- Dispatcher 상태 조회
function Area6Dispatcher.getStatus()
    return {
        enabled = NerveConfig and NerveConfig.area6 and NerveConfig.area6.enabled or false,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6Dispatcher = Area6Dispatcher

return Area6Dispatcher
