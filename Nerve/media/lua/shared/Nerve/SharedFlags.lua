--[[
    SharedFlags.lua
    Area 6 상태 플래그 공유 인터페이스
    
    v1.1 - Area 5 제거됨 (폐기)
    
    핵심 원칙:
    - 타 모듈 공유 필요 시 Pulse SPI 경유 (현 계획 범위 밖)
    - 직접 참조 없이 플래그만 공유
]]

--------------------------------------------------------------------------------
-- SharedFlags 모듈
--------------------------------------------------------------------------------

local SharedFlags = {}

-- Area 6 상태 (이벤트 디스패치)
SharedFlags.area6Sustained = false      -- Sustained Event Pressure 상태
SharedFlags.area6EarlyExitState = "PASSTHROUGH"  -- Early Exit 상태

--------------------------------------------------------------------------------
-- Area 6 → SharedFlags 업데이트
--------------------------------------------------------------------------------

function SharedFlags.setArea6Sustained(isSustained)
    SharedFlags.area6Sustained = isSustained
end

function SharedFlags.setArea6EarlyExitState(state)
    SharedFlags.area6EarlyExitState = state
end

--------------------------------------------------------------------------------
-- 상태 조회
--------------------------------------------------------------------------------

function SharedFlags.isArea6Sustained()
    return SharedFlags.area6Sustained
end

function SharedFlags.getArea6EarlyExitState()
    return SharedFlags.area6EarlyExitState
end

-- 통합 상태 조회
function SharedFlags.getAll()
    return {
        area6Sustained = SharedFlags.area6Sustained,
        area6EarlyExitState = SharedFlags.area6EarlyExitState,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.SharedFlags = SharedFlags

return SharedFlags
