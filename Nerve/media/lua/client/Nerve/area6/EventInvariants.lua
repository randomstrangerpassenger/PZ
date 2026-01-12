--[[
    EventInvariants.lua
    이벤트 의미 불변 검증
    
    v0.2 - checkNoDropNoDelay 추가
    
    핵심 역할:
    - 디버그/테스트 시 의미 불변 검증
    - CRITICAL 이벤트 통과 확인
    - 무음 드롭 방지
    - Drop/Delay 금지 규칙 위반 감지
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- EventInvariants 모듈
--------------------------------------------------------------------------------

local EventInvariants = {}

-- 통계
EventInvariants.violations = 0
EventInvariants.checks = 0

--------------------------------------------------------------------------------
-- CRITICAL 이벤트 정의
--------------------------------------------------------------------------------

-- 절대 스킵되면 안 되는 이벤트 목록
local criticalEvents = {
    ["OnPlayerDeath"] = true,
    ["OnGameStart"] = true,
    ["OnGameBoot"] = true,
    ["OnSave"] = true,
    ["OnLoad"] = true,
    ["OnCreatePlayer"] = true,
    ["OnPlayerUpdate"] = true,
}

--------------------------------------------------------------------------------
-- 검증 함수
--------------------------------------------------------------------------------

-- CRITICAL 이벤트 스킵 검사
function EventInvariants.checkCriticalNotSkipped(eventName, wasSkipped)
    if not NerveConfig or not NerveConfig.debug then
        return  -- 디버그 모드에서만 검사
    end
    
    EventInvariants.checks = EventInvariants.checks + 1
    
    if criticalEvents[eventName] and wasSkipped then
        EventInvariants.violations = EventInvariants.violations + 1
        NerveUtils.error("INVARIANT VIOLATION: Critical event was skipped: " .. eventName)
        return false
    end
    
    return true
end

-- 무음 드롭 검사 (스킵 시 로그 있는지)
function EventInvariants.checkNoSilentDrop(eventName, wasSkipped, hasLog)
    if not NerveConfig or not NerveConfig.debug then
        return
    end
    
    EventInvariants.checks = EventInvariants.checks + 1
    
    if wasSkipped and not hasLog then
        EventInvariants.violations = EventInvariants.violations + 1
        NerveUtils.warn("INVARIANT WARN: Event skipped without log: " .. eventName)
        return false
    end
    
    return true
end

-- 순서 보존 검사 (v0.2에서 구현 예정)
function EventInvariants.checkOrderPreserved(eventName, sequence)
    -- v0.2에서는 순서 변경 기능이 없으므로 통과
    return true
end

--------------------------------------------------------------------------------
-- Drop/Delay 금지 규칙 검증
--------------------------------------------------------------------------------

-- [필수보완#3] Drop/Delay 금지 규칙 위반 감지
-- 호출 지점: Area6Coordinator.shouldProcess() (DROP 발생 시)
function EventInvariants.checkNoDropNoDelay(eventName, wasDropped, wasDelayed)
    EventInvariants.checks = EventInvariants.checks + 1
    
    if wasDropped then
        EventInvariants.violations = EventInvariants.violations + 1
        NerveUtils.error("[!] INVARIANT: Event DROPPED: " .. eventName)
        -- 철수 트리거만 (자동 조정 금지)
        return false
    end
    
    if wasDelayed then
        EventInvariants.violations = EventInvariants.violations + 1
        NerveUtils.error("[!] INVARIANT: Event DELAYED: " .. eventName)
        return false
    end
    
    return true
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function EventInvariants.getStats()
    return {
        checks = EventInvariants.checks,
        violations = EventInvariants.violations,
    }
end

function EventInvariants.printStats()
    NerveUtils.info("EventInvariants Stats:")
    NerveUtils.info("  Checks: " .. EventInvariants.checks)
    NerveUtils.info("  Violations: " .. EventInvariants.violations)
    
    if EventInvariants.violations > 0 then
        NerveUtils.warn("There were " .. EventInvariants.violations .. " invariant violations!")
    else
        NerveUtils.info("All invariants passed.")
    end
end

--------------------------------------------------------------------------------
-- CRITICAL 이벤트 등록 API
--------------------------------------------------------------------------------

function EventInvariants.registerCritical(eventName)
    criticalEvents[eventName] = true
    NerveUtils.debug("Registered critical event: " .. eventName)
end

function EventInvariants.isCritical(eventName)
    return criticalEvents[eventName] == true
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.EventInvariants = EventInvariants

return EventInvariants
