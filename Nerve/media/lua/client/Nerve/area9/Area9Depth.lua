--[[
    Area9Depth.lua
    Chain Depth Guard
    
    [헌법 준수]
    - domain enum (정수)
    - enter/exit 헬퍼 고정
    - tick 리셋 + 음수 클램프
    - 히스테리시스 (enter/exit limit 분리)
]]

require "Nerve/NerveUtils"
require "Nerve/area9/Area9TickCtx"
require "Nerve/area9/Area9Forensic"

--------------------------------------------------------------------------------
-- Area9Depth 모듈
--------------------------------------------------------------------------------

local Area9Depth = {}

-- Domain enum (정수)
Area9Depth.Domain = {
    NETWORK = 1,    -- 네트워크 처리
    COMMAND = 2,    -- 명령 처리
    HANDLER = 3,    -- 핸들러 체인
}

-- 제한 설정 (히스테리시스)
Area9Depth.Limits = {
    [1] = { enterLimit = 5, exitLimit = 3 },  -- NETWORK
    [2] = { enterLimit = 10, exitLimit = 7 },  -- COMMAND
    [3] = { enterLimit = 8, exitLimit = 5 },   -- HANDLER
}

--------------------------------------------------------------------------------
-- Depth 관리
--------------------------------------------------------------------------------

-- 진입 (depth 증가)
-- @param domain: Domain enum
-- @return: currentDepth, isExceeded
function Area9Depth.enter(domain)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return 0, false
    end
    
    local depth = TickCtx.incDepth(domain)
    
    -- 제한 체크
    local limits = Area9Depth.Limits[domain] or { enterLimit = 10, exitLimit = 7 }
    local isExceeded = depth > limits.enterLimit
    
    if isExceeded then
        TickCtx.markIncident("depthExceed")
        
        -- Forensic 기록
        local Forensic = Nerve.Area9Forensic
        if Forensic then
            Forensic.recordDepthExceed(Forensic.ReasonCode.DEPTH_EXCEED_ENTER, domain, depth)
        end
    end
    
    return depth, isExceeded
end

-- 종료 (depth 감소, 음수 클램프)
-- @param domain: Domain enum
-- @return: currentDepth
function Area9Depth.exit(domain)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return 0
    end
    
    return TickCtx.decDepth(domain)
end

-- 현재 depth 조회
function Area9Depth.get(domain)
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return 0
    end
    
    return TickCtx.getDepth(domain)
end

-- 모든 domain의 depth 조회
function Area9Depth.getAll()
    local TickCtx = Nerve.Area9TickCtx
    if not TickCtx then
        return {}
    end
    
    local result = {}
    for name, domain in pairs(Area9Depth.Domain) do
        result[name] = TickCtx.getDepth(domain)
    end
    return result
end

-- 제한 초과 여부 확인 (히스테리시스 적용)
function Area9Depth.isExceeded(domain)
    local depth = Area9Depth.get(domain)
    local limits = Area9Depth.Limits[domain] or { enterLimit = 10, exitLimit = 7 }
    return depth > limits.enterLimit
end

-- 안전 영역 복귀 여부 (히스테리시스)
function Area9Depth.isRecovered(domain)
    local depth = Area9Depth.get(domain)
    local limits = Area9Depth.Limits[domain] or { enterLimit = 10, exitLimit = 7 }
    return depth <= limits.exitLimit
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Depth = Area9Depth

return Area9Depth
