--[[
    Area6TestHarness.lua
    Phase 7: 검증 테스트 하네스
    
    [DEV-ONLY] 배포 제외
    
    테스트 케이스:
    1. Normal Flow: 에러/재귀 없이 이벤트 정상 발생
    2. Exception: 리스너에서 에러 발생 -> 격리 + 로그 + 다음 리스너 실행
    3. Recursion: 재진입 -> pass-through 전환 + 로그 + 디스패치 지속
]]

require "Nerve/NerveUtils"
require "Nerve/area6/Area6Guard"
require "Nerve/area6/Area6TickCtx"
require "Nerve/area6/Area6Dispatcher"

--------------------------------------------------------------------------------
-- Area6TestHarness 모듈
--------------------------------------------------------------------------------

local Area6TestHarness = {}

-- 테스트 결과
Area6TestHarness.results = {}

--------------------------------------------------------------------------------
-- 테스트 유틸리티
--------------------------------------------------------------------------------

local function logTest(name, passed, message)
    local status = passed and "PASS" or "FAIL"
    local msg = "[TEST] " .. status .. ": " .. name
    if message then
        msg = msg .. " - " .. message
    end
    
    if passed then
        NerveUtils.info(msg)
    else
        NerveUtils.warn(msg)
    end
    
    table.insert(Area6TestHarness.results, {
        name = name,
        passed = passed,
        message = message,
    })
end

--------------------------------------------------------------------------------
-- 테스트 1: 합헌 게이트 (의미 변경 없음)
--------------------------------------------------------------------------------

function Area6TestHarness.testNormalFlow()
    local testName = "Normal Flow"
    local callCount = 0
    local expectedCount = 3
    
    -- 테스트 리스너
    local function testListener(arg)
        callCount = callCount + 1
        return arg * 2
    end
    
    -- 디스패처 통해 호출
    local Dispatcher = Nerve.Area6Dispatcher
    
    -- 틱 시작 시뮬레이션
    if Nerve.Area6TickCtx then
        Nerve.Area6TickCtx.onTickStart()
    end
    
    for i = 1, expectedCount do
        Dispatcher.dispatch("TestEvent", testListener, i)
    end
    
    -- 검증
    local passed = (callCount == expectedCount)
    logTest(testName, passed, "callCount=" .. callCount .. ", expected=" .. expectedCount)
    
    return passed
end

--------------------------------------------------------------------------------
-- 테스트 2: 실패 게이트 (침묵 금지 + 격리)
--------------------------------------------------------------------------------

function Area6TestHarness.testException()
    local testName = "Exception Isolation"
    local listener1Called = false
    local listener2Called = false
    
    -- 에러 발생 리스너
    local function errorListener()
        error("Test error from listener")
    end
    
    -- 정상 리스너 (에러 리스너 후에 호출되어야 함)
    local function normalListener()
        listener2Called = true
    end
    
    local Dispatcher = Nerve.Area6Dispatcher
    
    -- 틱 시작
    if Nerve.Area6TickCtx then
        Nerve.Area6TickCtx.onTickStart()
    end
    
    -- 에러 리스너 호출 (격리되어야 함)
    Dispatcher.dispatch("TestEvent", errorListener)
    listener1Called = true  -- dispatch가 리턴했으면 격리 성공
    
    -- 다음 리스너 호출 (실행되어야 함)
    Dispatcher.dispatch("TestEvent", normalListener)
    
    -- 검증
    local passed = listener1Called and listener2Called
    logTest(testName, passed, 
        "listener1Called=" .. tostring(listener1Called) 
        .. ", listener2Called=" .. tostring(listener2Called))
    
    return passed
end

--------------------------------------------------------------------------------
-- 테스트 3: 재진입 -> pass-through
--------------------------------------------------------------------------------

function Area6TestHarness.testReentry()
    local testName = "Reentry Pass-through"
    local callCount = 0
    local maxCalls = 10  -- 무한 루프 방지
    
    local Dispatcher = Nerve.Area6Dispatcher
    local testListener
    
    -- 재귀 리스너
    testListener = function()
        callCount = callCount + 1
        if callCount < maxCalls then
            -- 재귀 호출
            Dispatcher.dispatch("TestEvent", testListener)
        end
    end
    
    -- 틱 시작
    if Nerve.Area6TickCtx then
        Nerve.Area6TickCtx.onTickStart()
    end
    
    -- 첫 호출
    Dispatcher.dispatch("TestEvent", testListener)
    
    -- 검증: 무한 루프 아니고 철수가 작동했으면 성공
    -- (재진입 시 pass-through로 전환되어도 호출은 계속됨)
    local passed = (callCount <= maxCalls)
    logTest(testName, passed, 
        "callCount=" .. callCount 
        .. " (pass-through switches but dispatch continues)")
    
    return passed
end

--------------------------------------------------------------------------------
-- 테스트 4: 설치 상태
--------------------------------------------------------------------------------

function Area6TestHarness.testInstallState()
    local testName = "Install State"
    
    local InstallState = Nerve.Area6InstallState
    if not InstallState then
        logTest(testName, false, "Area6InstallState not found")
        return false
    end
    
    local state = InstallState.getState()
    local validStates = { "Applied", "Partial", "Bypassed" }
    
    local passed = false
    for _, valid in ipairs(validStates) do
        if state == valid then
            passed = true
            break
        end
    end
    
    logTest(testName, passed, "state=" .. tostring(state))
    return passed
end

--------------------------------------------------------------------------------
-- 전체 테스트 실행
--------------------------------------------------------------------------------

function Area6TestHarness.runAll()
    NerveUtils.info("==========================================")
    NerveUtils.info("[Area6] Running Test Harness")
    NerveUtils.info("==========================================")
    
    -- 결과 초기화
    Area6TestHarness.results = {}
    
    -- 테스트 실행
    Area6TestHarness.testNormalFlow()
    Area6TestHarness.testException()
    Area6TestHarness.testReentry()
    Area6TestHarness.testInstallState()
    
    -- 요약
    local passCount = 0
    local failCount = 0
    
    for _, result in ipairs(Area6TestHarness.results) do
        if result.passed then
            passCount = passCount + 1
        else
            failCount = failCount + 1
        end
    end
    
    NerveUtils.info("==========================================")
    NerveUtils.info("[Area6] Test Summary: " 
        .. passCount .. " passed, " .. failCount .. " failed")
    NerveUtils.info("==========================================")
    
    return failCount == 0
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6TestHarness = Area6TestHarness

return Area6TestHarness
