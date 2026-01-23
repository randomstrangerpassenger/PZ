--[[
    Area9Install.lua
    네트워크 경계 래핑 설치 모듈
    
    핵심 역할:
    - endpoints 래핑/언래핑
    - Chain-of-custody (원본 보존)
    - 무결성 체크 (충돌 감지)
    
    [헌법 준수]
    - wrapper overwrite/타모드 충돌 감지 시 즉시 disable + unwrap
    - endpoints 폐쇄 목록만 래핑
]]

require "Nerve/NerveUtils"
require "Nerve/area9/Area9InstallState"

--------------------------------------------------------------------------------
-- Area9Install 모듈
--------------------------------------------------------------------------------

local Area9Install = {}

-- 래핑 표식 키
local NERVE_AREA9_WRAPPED_KEY = "__nerve_area9_wrapped"
local NERVE_AREA9_ORIGINAL_ADD_KEY = "__nerve_area9_original_add"

-- 디스패처 참조
Area9Install.dispatcher = nil

--------------------------------------------------------------------------------
-- 래핑 함수 생성
--------------------------------------------------------------------------------

-- 래퍼 콜백 생성
-- @param eventName: 이벤트 이름
-- @param originalCallback: 원본 콜백
-- @return: 래핑된 콜백
local function createWrappedCallback(eventName, originalCallback)
    return function(...)
        -- 디스패처가 없으면 원본 그대로 호출
        if not Area9Install.dispatcher then
            return originalCallback(...)
        end
        
        -- 디스패처 통해 실행
        return Area9Install.dispatcher.dispatch(eventName, originalCallback, ...)
    end
end

--------------------------------------------------------------------------------
-- 이벤트 래핑
--------------------------------------------------------------------------------

-- 단일 이벤트 래핑
-- @param eventName: 이벤트 이름
-- @return: 성공 여부
function Area9Install.wrapEvent(eventName)
    local InstallState = Nerve.Area9InstallState
    
    -- Events 존재 확인
    if not Events then
        NerveUtils.warn("[Area9Install] Events table not found")
        InstallState.setEndpointState(eventName, false, nil)
        return false
    end
    
    local eventObj = Events[eventName]
    if not eventObj then
        NerveUtils.warn("[Area9Install] Event not found: " .. eventName)
        InstallState.setEndpointState(eventName, false, nil)
        return false
    end
    
    -- Add 메서드 확인
    if type(eventObj.Add) ~= "function" then
        NerveUtils.warn("[Area9Install] Event.Add not a function: " .. eventName)
        InstallState.setEndpointState(eventName, false, nil)
        return false
    end
    
    -- 이미 래핑되었는지 확인 (멱등성)
    if eventObj[NERVE_AREA9_WRAPPED_KEY] then
        NerveUtils.debug("[Area9Install] Already wrapped: " .. eventName)
        return true
    end
    
    -- 다른 모드가 이미 래핑했는지 확인 (충돌 감지)
    if eventObj.__nerve_wrapped or eventObj.__other_mod_wrapped then
        NerveUtils.warn("[Area9Install] Conflict detected: " .. eventName)
        InstallState.setDisabled(
            InstallState.DisabledReason.OVERWRITE,
            "Event already wrapped by another mod: " .. eventName
        )
        return false
    end
    
    -- 원본 Add 보존 (chain-of-custody)
    local originalAdd = eventObj.Add
    eventObj[NERVE_AREA9_ORIGINAL_ADD_KEY] = originalAdd
    
    -- 래핑된 Add 생성
    eventObj.Add = function(callback)
        -- 콜백 유효성 검사
        if type(callback) ~= "function" then
            return originalAdd(callback)
        end
        
        -- 래핑된 콜백 생성
        local wrapped = createWrappedCallback(eventName, callback)
        
        return originalAdd(wrapped)
    end
    
    -- 래핑 표식
    eventObj[NERVE_AREA9_WRAPPED_KEY] = true
    
    NerveUtils.info("[Area9Install] OK: " .. eventName)
    InstallState.setEndpointState(eventName, true, originalAdd)
    return true
end

-- 대상 이벤트 전수 래핑
-- @return: { success: table, failed: table }
function Area9Install.wrapAllTargetEvents()
    local results = {
        success = {},
        failed = {},
    }
    
    -- 설정에서 대상 이벤트 조회
    local targetEvents = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.targetEvents 
        or {}
    
    -- 빈 목록이면 아무것도 안 함 (Gate P0)
    if #targetEvents == 0 then
        NerveUtils.debug("[Area9Install] No target events configured")
        return results
    end
    
    for _, eventName in ipairs(targetEvents) do
        if Area9Install.wrapEvent(eventName) then
            table.insert(results.success, eventName)
        else
            table.insert(results.failed, eventName)
        end
    end
    
    return results
end

-- 디스패처 연결
function Area9Install.setDispatcher(dispatcher)
    Area9Install.dispatcher = dispatcher
    NerveUtils.debug("[Area9Install] Dispatcher connected")
end

--------------------------------------------------------------------------------
-- 무결성 확인
--------------------------------------------------------------------------------

function Area9Install.checkIntegrity()
    local issues = 0
    local InstallState = Nerve.Area9InstallState
    
    local targetEvents = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.targetEvents 
        or {}
    
    for _, eventName in ipairs(targetEvents) do
        if Events and Events[eventName] then
            local eventObj = Events[eventName]
            
            -- 래핑 표식 확인
            if not eventObj[NERVE_AREA9_WRAPPED_KEY] then
                NerveUtils.warn("[Area9Install] Integrity: not wrapped: " .. eventName)
                issues = issues + 1
            end
            
            -- 원본 보존 확인
            if not eventObj[NERVE_AREA9_ORIGINAL_ADD_KEY] then
                NerveUtils.warn("[Area9Install] Integrity: original lost: " .. eventName)
                issues = issues + 1
            end
        end
    end
    
    if issues > 0 then
        InstallState.setDisabled(
            InstallState.DisabledReason.INTEGRITY_FAIL,
            issues .. " integrity issues detected"
        )
    end
    
    return issues == 0
end

--------------------------------------------------------------------------------
-- 언래핑 (안전 롤백)
--------------------------------------------------------------------------------

-- 단일 이벤트 언래핑
-- @param eventName: 이벤트 이름
-- @return: 성공 여부
function Area9Install.unwrapEvent(eventName)
    if not Events then
        return false
    end
    
    local eventObj = Events[eventName]
    if not eventObj then
        return false
    end
    
    -- 래핑되지 않았으면 스킵
    if not eventObj[NERVE_AREA9_WRAPPED_KEY] then
        return true
    end
    
    -- 원본 복구
    local originalAdd = eventObj[NERVE_AREA9_ORIGINAL_ADD_KEY]
    if originalAdd then
        eventObj.Add = originalAdd
        eventObj[NERVE_AREA9_ORIGINAL_ADD_KEY] = nil
    end
    
    eventObj[NERVE_AREA9_WRAPPED_KEY] = nil
    
    -- 상태 업데이트
    if Nerve.Area9InstallState then
        Nerve.Area9InstallState.setEndpointState(eventName, false, nil)
    end
    
    NerveUtils.info("[Area9Install] UNWRAPPED: " .. eventName)
    return true
end

-- 전체 언래핑
-- @return: { success: table, failed: table }
function Area9Install.unwrapAll()
    local results = {
        success = {},
        failed = {},
    }
    
    local targetEvents = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.targetEvents 
        or {}
    
    for _, eventName in ipairs(targetEvents) do
        if Area9Install.unwrapEvent(eventName) then
            table.insert(results.success, eventName)
        else
            table.insert(results.failed, eventName)
        end
    end
    
    return results
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Install = Area9Install

return Area9Install
