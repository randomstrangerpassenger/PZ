--[[
    Area6Evidence.lua
    포렌식 증거 수집 오케스트레이터
    
    핵심 역할:
    - incident 발생 후 Lazy 증거 수집 조율
    - DupCount, Depth, Fanout, Repeat 수집
    - TopN/버킷 형태 요약 출력
    
    [CONSTITUTION 준수]
    - 상시 계측 금지: incident 후에만 수집
    - 증거는 트리거로 사용하지 않음
    - 틱 종료 시 wipe
]]

require "Nerve/NerveUtils"
require "Nerve/area6/Area6TickCtx"

--------------------------------------------------------------------------------
-- Area6Evidence 모듈
--------------------------------------------------------------------------------

local Area6Evidence = {}

-- 수집된 증거 (틱 단위 wipe)
Area6Evidence.collected = {}
Area6Evidence.lastCollectTick = 0

--------------------------------------------------------------------------------
-- 틱 관리
--------------------------------------------------------------------------------

local function ensureCurrentTick()
    local currentTick = Nerve.Area6TickCtx and Nerve.Area6TickCtx.tickId or 0
    
    if currentTick ~= Area6Evidence.lastCollectTick then
        NerveUtils.safeWipe(Area6Evidence.collected)
        Area6Evidence.lastCollectTick = currentTick
    end
end

--------------------------------------------------------------------------------
-- 증거 수집 (Lazy, Incident-Gated)
--------------------------------------------------------------------------------

-- 증거 수집 시작 (incident 발생 후에만 호출)
-- @param eventName: 이벤트 이름
-- @param listenerId: 리스너 식별자
-- @param incidentType: 'reentry' | 'error'
function Area6Evidence.collect(eventName, listenerId, incidentType)
    ensureCurrentTick()
    
    local TickCtx = Nerve.Area6TickCtx
    
    -- incident가 없으면 수집 안 함 (헌법: incident 후 Lazy만)
    if TickCtx and not TickCtx.hasIncident() then
        return nil
    end
    
    local evidence = {
        tickId = TickCtx and TickCtx.tickId or 0,
        eventName = eventName,
        listenerId = tostring(listenerId),
        incidentType = incidentType,
        
        -- 수집할 증거 필드
        dupCount = 0,
        chainDepth = 0,
        fanoutExecuted = 0,
        fanoutRegistered = nil,  -- 가능할 때만
        repeatCount = 0,
    }
    
    -- 각 증거 모듈에서 수집
    if Nerve.Area6DupCount then
        evidence.dupCount = Nerve.Area6DupCount.getCount(eventName, listenerId)
    end
    
    if Nerve.Area6Depth then
        evidence.chainDepth = Nerve.Area6Depth.getCurrentDepth()
    end
    
    if Nerve.Area6Fanout then
        local fanout = Nerve.Area6Fanout.getFanout()
        evidence.fanoutExecuted = fanout.executed
        evidence.fanoutRegistered = fanout.registered
    end
    
    if Nerve.Area6Repeat then
        evidence.repeatCount = Nerve.Area6Repeat.getCount(eventName, listenerId)
    end
    
    -- 수집된 증거 저장
    table.insert(Area6Evidence.collected, evidence)
    
    return evidence
end

--------------------------------------------------------------------------------
-- 증거 요약 출력
--------------------------------------------------------------------------------

-- 증거 버킷 생성
local function makeBucket(count)
    if count == 0 then return "0"
    elseif count <= 4 then return "1-4"
    elseif count <= 9 then return "5-9"
    elseif count <= 19 then return "10-19"
    else return "20+"
    end
end

-- 수집된 증거를 요약 출력
function Area6Evidence.emitSummary()
    if #Area6Evidence.collected == 0 then
        return
    end
    
    local latest = Area6Evidence.collected[#Area6Evidence.collected]
    
    -- [P3-2] 신뢰도 라벨 (InstallState)
    local reliability = "unknown"
    if Nerve.Area6InstallState then
        reliability = Nerve.Area6InstallState.getState()
    end
    
    NerveUtils.info("  [Evidence]")
    NerveUtils.info("    reliability: " .. reliability)
    NerveUtils.info("    dupCount: " .. latest.dupCount .. " (" .. makeBucket(latest.dupCount) .. ")")
    NerveUtils.info("    chainDepth: " .. latest.chainDepth)
    NerveUtils.info("    fanoutExecuted: " .. latest.fanoutExecuted .. " (" .. makeBucket(latest.fanoutExecuted) .. ")")
    
    if latest.fanoutRegistered then
        NerveUtils.info("    fanoutRegistered: " .. latest.fanoutRegistered)
    end
    
    NerveUtils.info("    repeatCount: " .. latest.repeatCount)
end

-- 현재 틱의 모든 증거 반환
function Area6Evidence.getAll()
    return Area6Evidence.collected
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6Evidence = Area6Evidence

return Area6Evidence
