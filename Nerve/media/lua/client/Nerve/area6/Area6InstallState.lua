--[[
    Area6InstallState.lua
    설치 상태 스냅샷 관리 모듈
    
    v1.0 - Phase 1: Foundation
    
    핵심 역할:
    - Applied / Partial / Bypassed 상태 관리
    - 상태 변경 시 1회 로그 출력 (레이트리밋)
    - 누적 통계 금지 (틱 단위 스냅샷만)
    
    [CONSTITUTION 준수]
    - 상시 계측 없음 (상태 스냅샷만)
    - Drop/Delay/Reorder 금지
]]

require "Nerve/NerveUtils"
require "Nerve/area6/Area6Guard"

--------------------------------------------------------------------------------
-- Area6InstallState 모듈
--------------------------------------------------------------------------------

local Area6InstallState = {}

-- 상태 상수 (Area6Guard에서 가져옴)
local STATE = Nerve.Area6Guard and Nerve.Area6Guard.INSTALL_STATE or {
    APPLIED = "Applied",
    PARTIAL = "Partial",
    BYPASSED = "Bypassed",
}

-- 현재 상태
Area6InstallState.current = STATE.APPLIED

-- 이벤트별 상태
Area6InstallState.eventStates = {}

-- 마지막 로그 출력 틱 (레이트리밋용)
Area6InstallState.lastLogTick = -1

--------------------------------------------------------------------------------
-- 상태 관리
--------------------------------------------------------------------------------

-- 이벤트 상태 설정
-- @param eventName: 이벤트 이름
-- @param success: 래핑 성공 여부
function Area6InstallState.setEventState(eventName, success)
    Area6InstallState.eventStates[eventName] = success
    Area6InstallState.recalculateState()
end

-- 전체 상태 재계산
function Area6InstallState.recalculateState()
    local successCount = 0
    local failCount = 0
    
    for _, success in pairs(Area6InstallState.eventStates) do
        if success then
            successCount = successCount + 1
        else
            failCount = failCount + 1
        end
    end
    
    local totalCount = successCount + failCount
    local previousState = Area6InstallState.current
    
    if totalCount == 0 then
        Area6InstallState.current = STATE.APPLIED
    elseif failCount == 0 then
        Area6InstallState.current = STATE.APPLIED
    elseif successCount == 0 then
        Area6InstallState.current = STATE.BYPASSED
    else
        Area6InstallState.current = STATE.PARTIAL
    end
    
    -- 상태 변경 시 로그 출력 (레이트리밋)
    if previousState ~= Area6InstallState.current then
        Area6InstallState.logStateOnce()
    end
end

-- 상태 로그 출력 (1회)
function Area6InstallState.logStateOnce()
    local currentTick = getTimestamp and getTimestamp() or 0
    
    -- 같은 틱에서 중복 로그 방지
    if currentTick == Area6InstallState.lastLogTick then
        return
    end
    Area6InstallState.lastLogTick = currentTick
    
    local successCount = 0
    local failCount = 0
    local failedEvents = {}
    
    for eventName, success in pairs(Area6InstallState.eventStates) do
        if success then
            successCount = successCount + 1
        else
            failCount = failCount + 1
            table.insert(failedEvents, eventName)
        end
    end
    
    -- 상태 출력
    NerveUtils.info("[Area6] installState=" .. Area6InstallState.current 
        .. " (success=" .. successCount .. ", fail=" .. failCount .. ")")
    
    if failCount > 0 then
        NerveUtils.warn("[Area6] Failed events: " .. table.concat(failedEvents, ", "))
    end
end

--------------------------------------------------------------------------------
-- 상태 조회
--------------------------------------------------------------------------------

-- 현재 상태 반환
function Area6InstallState.getState()
    return Area6InstallState.current
end

-- 스냅샷 반환 (로그/증거용)
function Area6InstallState.getSnapshot()
    local successCount = 0
    local failCount = 0
    
    for _, success in pairs(Area6InstallState.eventStates) do
        if success then
            successCount = successCount + 1
        else
            failCount = failCount + 1
        end
    end
    
    return {
        state = Area6InstallState.current,
        successCount = successCount,
        failCount = failCount,
    }
end

-- Bypassed 상태인지
function Area6InstallState.isBypassed()
    return Area6InstallState.current == STATE.BYPASSED
end

-- Partial 상태인지
function Area6InstallState.isPartial()
    return Area6InstallState.current == STATE.PARTIAL
end

--------------------------------------------------------------------------------
-- 초기화
--------------------------------------------------------------------------------

function Area6InstallState.reset()
    Area6InstallState.current = STATE.APPLIED
    NerveUtils.safeWipe(Area6InstallState.eventStates)
    Area6InstallState.lastLogTick = -1
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6InstallState = Area6InstallState

return Area6InstallState
