--[[
    Area9InstallState.lua
    설치 상태 추적 모듈 (네트워크/멀티 경계)
    
    핵심 역할:
    - 각 endpoint별 설치 상태 추적
    - Applied/Partial/Bypassed 상태 관리
    - DisabledReason enum 제공
    
    [헌법 준수]
    - wrapper overwrite/충돌 감지 시 즉시 disable
]]

--------------------------------------------------------------------------------
-- Area9InstallState 모듈
--------------------------------------------------------------------------------

local Area9InstallState = {}

--------------------------------------------------------------------------------
-- DisabledReason enum (권장 수정 반영)
--------------------------------------------------------------------------------

Area9InstallState.DisabledReason = {
    NONE = 0,           -- 비활성화되지 않음
    CONFIG_OFF = 1,     -- config에서 OFF
    OVERWRITE = 2,      -- 다른 모드가 wrapper 덮어씀
    PARTIAL_APPLY = 3,  -- 일부 endpoint만 적용됨
    INTEGRITY_FAIL = 4, -- 무결성 체크 실패
    MANUAL = 5,         -- 수동 비활성화
}

--------------------------------------------------------------------------------
-- 상태 저장소
--------------------------------------------------------------------------------

-- 각 endpoint별 상태
-- key: eventName, value: { applied: bool, originalAdd: func }
Area9InstallState.endpoints = {}

-- 전역 상태
Area9InstallState.globalState = "INIT"  -- "INIT" | "APPLIED" | "PARTIAL" | "BYPASSED"

-- 비활성화 사유
Area9InstallState.disabledReason = Area9InstallState.DisabledReason.NONE

-- 비활성화 상세 정보
Area9InstallState.disabledDetail = nil

--------------------------------------------------------------------------------
-- 상태 조회
--------------------------------------------------------------------------------

-- 전역 상태 조회
function Area9InstallState.getState()
    return Area9InstallState.globalState
end

-- 비활성화 사유 조회
function Area9InstallState.getDisabledReason()
    return Area9InstallState.disabledReason
end

-- 비활성화 사유 문자열 조회
function Area9InstallState.getDisabledReasonName()
    local reason = Area9InstallState.disabledReason
    for name, value in pairs(Area9InstallState.DisabledReason) do
        if value == reason then
            return name
        end
    end
    return "UNKNOWN"
end

-- 비활성화 상세 정보 조회
function Area9InstallState.getDisabledDetail()
    return Area9InstallState.disabledDetail
end

-- endpoint 상태 조회
function Area9InstallState.getEndpointState(eventName)
    local state = Area9InstallState.endpoints[eventName]
    if state then
        return state.applied
    end
    return false
end

--------------------------------------------------------------------------------
-- 상태 설정
--------------------------------------------------------------------------------

-- endpoint 상태 설정
-- @param eventName: 이벤트 이름
-- @param applied: 적용 여부
-- @param originalAdd: 원본 Add 함수 (적용 시)
function Area9InstallState.setEndpointState(eventName, applied, originalAdd)
    Area9InstallState.endpoints[eventName] = {
        applied = applied,
        originalAdd = originalAdd,
    }
    -- 전역 상태 재계산
    Area9InstallState.recalculateGlobalState()
end

-- 전역 상태 재계산
function Area9InstallState.recalculateGlobalState()
    local targetEvents = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.targetEvents 
        or {}
    
    if #targetEvents == 0 then
        Area9InstallState.globalState = "INIT"
        return
    end
    
    local appliedCount = 0
    for _, eventName in ipairs(targetEvents) do
        if Area9InstallState.getEndpointState(eventName) then
            appliedCount = appliedCount + 1
        end
    end
    
    if appliedCount == 0 then
        Area9InstallState.globalState = "BYPASSED"
    elseif appliedCount == #targetEvents then
        Area9InstallState.globalState = "APPLIED"
    else
        Area9InstallState.globalState = "PARTIAL"
        -- Partial은 잠재적 리스크
        if Area9InstallState.disabledReason == Area9InstallState.DisabledReason.NONE then
            Area9InstallState.disabledReason = Area9InstallState.DisabledReason.PARTIAL_APPLY
            Area9InstallState.disabledDetail = "Only " .. appliedCount .. "/" .. #targetEvents .. " endpoints applied"
        end
    end
end

-- 비활성화 설정
-- @param reason: DisabledReason enum 값
-- @param detail: 상세 정보 문자열
function Area9InstallState.setDisabled(reason, detail)
    Area9InstallState.globalState = "BYPASSED"
    Area9InstallState.disabledReason = reason
    Area9InstallState.disabledDetail = detail
end

-- 상태 초기화
function Area9InstallState.reset()
    Area9InstallState.endpoints = {}
    Area9InstallState.globalState = "INIT"
    Area9InstallState.disabledReason = Area9InstallState.DisabledReason.NONE
    Area9InstallState.disabledDetail = nil
end

--------------------------------------------------------------------------------
-- 스냅샷
--------------------------------------------------------------------------------

function Area9InstallState.getSnapshot()
    local endpointStates = {}
    for eventName, state in pairs(Area9InstallState.endpoints) do
        endpointStates[eventName] = state.applied
    end
    
    return {
        globalState = Area9InstallState.globalState,
        disabledReason = Area9InstallState.getDisabledReasonName(),
        disabledDetail = Area9InstallState.disabledDetail,
        endpoints = endpointStates,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9InstallState = Area9InstallState

return Area9InstallState
