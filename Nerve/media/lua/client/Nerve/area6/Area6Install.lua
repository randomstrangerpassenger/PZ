--[[
    Area6Install.lua
    Events.*.Add 전수 래핑 설치 모듈
    
    v1.0 - Phase 1: Foundation
    
    핵심 역할:
    - Events.*.Add 몽키패치 (멱등 래핑)
    - Chain-of-custody (원본 보존)
    - 설치 상태 스냅샷 (Applied/Partial/Bypassed)
    
    [CONSTITUTION 준수]
    - 자동 복구/자동 언랩 금지
    - 의미 변경 없음 (항상 원본 호출 경로 존재)
]]

require "Nerve/NerveUtils"
require "Nerve/area6/Area6Guard"
require "Nerve/area6/Area6InstallState"

--------------------------------------------------------------------------------
-- Area6Install 모듈
--------------------------------------------------------------------------------

local Area6Install = {}

-- 래핑 표식 키
local NERVE_WRAPPED_KEY = "__nerveArea6Wrapped"
local NERVE_ORIGINAL_ADD_KEY = "__nerveOriginalAdd"

-- 래핑된 콜백 캐시 (weak table)
Area6Install.wrappedCallbacks = setmetatable({}, { __mode = "k" })

-- 디스패처 참조 (Phase 6에서 설정)
Area6Install.dispatcher = nil

--------------------------------------------------------------------------------
-- 래핑 함수 생성
--------------------------------------------------------------------------------

-- 래퍼 콜백 생성
-- @param eventName: 이벤트 이름
-- @param originalCallback: 원본 콜백
-- @return: 래핑된 콜백
local function createWrappedCallback(eventName, originalCallback)
    return function(...)
        -- 디스패처가 없으면 원본 그대로 호출 (Phase 6 이전)
        if not Area6Install.dispatcher then
            return originalCallback(...)
        end
        
        -- 디스패처에 위임
        return Area6Install.dispatcher.dispatch(eventName, originalCallback, ...)
    end
end

--------------------------------------------------------------------------------
-- 이벤트 래핑
--------------------------------------------------------------------------------

-- 단일 이벤트 래핑
-- @param eventName: 이벤트 이름
-- @return: 성공 여부
function Area6Install.wrapEvent(eventName)
    -- Events 존재 확인
    if not Events then
        NerveUtils.warn("[Area6Install] Events table not found")
        Nerve.Area6InstallState.setEventState(eventName, false)
        return false
    end
    
    local eventObj = Events[eventName]
    
    -- 이벤트 존재 확인
    if not eventObj then
        NerveUtils.warn("[Area6Install] Event not found: " .. eventName)
        Nerve.Area6InstallState.setEventState(eventName, false)
        return false
    end
    
    -- 중복 래핑 방지 (멱등성)
    if eventObj[NERVE_WRAPPED_KEY] then
        NerveUtils.debug("[Area6Install] Already wrapped: " .. eventName)
        Nerve.Area6InstallState.setEventState(eventName, true)
        return true
    end
    
    -- Add 메서드 확인
    if not eventObj.Add or type(eventObj.Add) ~= "function" then
        NerveUtils.warn("[Area6Install] Event.Add not found: " .. eventName)
        Nerve.Area6InstallState.setEventState(eventName, false)
        return false
    end
    
    -- 다른 모드 래핑 감지 (휴리스틱)
    if eventObj.__customWrapped or eventObj.__modWrapped or eventObj.__wrapped then
        NerveUtils.warn("[Area6Install] CONFLICT: " .. eventName .. " already wrapped by another mod")
        Nerve.Area6InstallState.setEventState(eventName, false)
        return false
    end
    
    -- 원본 Add 보존 (chain-of-custody)
    local originalAdd = eventObj.Add
    eventObj[NERVE_ORIGINAL_ADD_KEY] = originalAdd
    
    -- 래핑된 Add 생성
    eventObj.Add = function(callback)
        -- 콜백 유효성 검사
        if type(callback) ~= "function" then
            return originalAdd(callback)
        end
        
        -- 이미 래핑된 콜백이면 재사용 (중복 래핑 방지)
        local cachedWrapper = Area6Install.wrappedCallbacks[callback]
        if cachedWrapper then
            return originalAdd(cachedWrapper)
        end
        
        -- 새 래핑 콜백 생성
        local wrapped = createWrappedCallback(eventName, callback)
        Area6Install.wrappedCallbacks[callback] = wrapped
        
        return originalAdd(wrapped)
    end
    
    -- 래핑 표식
    eventObj[NERVE_WRAPPED_KEY] = true
    
    NerveUtils.info("[Area6Install] OK: " .. eventName)
    Nerve.Area6InstallState.setEventState(eventName, true)
    return true
end

-- 대상 이벤트 전수 래핑
-- @return: { success: table, failed: table }
function Area6Install.wrapAllTargetEvents()
    local results = {
        success = {},
        failed = {},
    }
    
    -- 설정에서 대상 이벤트 조회
    local targetEvents = NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.targetEvents 
        or {}
    
    if #targetEvents == 0 then
        NerveUtils.warn("[Area6Install] No target events configured")
        return results
    end
    
    for _, eventName in ipairs(targetEvents) do
        if Area6Install.wrapEvent(eventName) then
            table.insert(results.success, eventName)
        else
            table.insert(results.failed, eventName)
        end
    end
    
    -- 최종 상태 로그
    Nerve.Area6InstallState.logStateOnce()
    
    return results
end

--------------------------------------------------------------------------------
-- 디스패처 연결 (Phase 6)
--------------------------------------------------------------------------------

function Area6Install.setDispatcher(dispatcher)
    Area6Install.dispatcher = dispatcher
    NerveUtils.debug("[Area6Install] Dispatcher connected")
end

--------------------------------------------------------------------------------
-- 무결성 확인
--------------------------------------------------------------------------------

function Area6Install.checkIntegrity()
    local issues = 0
    
    local targetEvents = NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.targetEvents 
        or {}
    
    for _, eventName in ipairs(targetEvents) do
        local eventObj = Events and Events[eventName]
        
        if eventObj and eventObj[NERVE_WRAPPED_KEY] then
            -- 래핑이 덮어씌워졌는지 확인
            local originalAdd = eventObj[NERVE_ORIGINAL_ADD_KEY]
            if not originalAdd then
                NerveUtils.warn("[Area6Install] Integrity: originalAdd lost for " .. eventName)
                issues = issues + 1
            end
        end
    end
    
    if issues > 0 then
        NerveUtils.warn("[Area6Install] Integrity issues: " .. issues)
    end
    
    return issues
end

--------------------------------------------------------------------------------
-- [P2-1] 언래핑 (안전 롤백)
--------------------------------------------------------------------------------

-- 단일 이벤트 언래핑
-- @param eventName: 이벤트 이름
-- @return: 성공 여부
function Area6Install.unwrapEvent(eventName)
    if not Events then
        return false
    end
    
    local eventObj = Events[eventName]
    if not eventObj then
        return false
    end
    
    -- 래핑되지 않았으면 스킵
    if not eventObj[NERVE_WRAPPED_KEY] then
        NerveUtils.debug("[Area6Install] Not wrapped: " .. eventName)
        return true
    end
    
    -- 원본 Add 복구
    local originalAdd = eventObj[NERVE_ORIGINAL_ADD_KEY]
    if not originalAdd then
        NerveUtils.warn("[Area6Install] Cannot unwrap: originalAdd lost for " .. eventName)
        return false
    end
    
    eventObj.Add = originalAdd
    eventObj[NERVE_WRAPPED_KEY] = nil
    eventObj[NERVE_ORIGINAL_ADD_KEY] = nil
    
    -- InstallState 갱신
    if Nerve.Area6InstallState then
        Nerve.Area6InstallState.setEventState(eventName, false)
    end
    
    NerveUtils.info("[Area6Install] UNWRAPPED: " .. eventName)
    return true
end

-- 전체 언래핑
-- @return: { success: table, failed: table }
function Area6Install.unwrapAll()
    local results = {
        success = {},
        failed = {},
    }
    
    local targetEvents = NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.targetEvents 
        or {}
    
    for _, eventName in ipairs(targetEvents) do
        if Area6Install.unwrapEvent(eventName) then
            table.insert(results.success, eventName)
        else
            table.insert(results.failed, eventName)
        end
    end
    
    -- 상태 로그
    if Nerve.Area6InstallState then
        Nerve.Area6InstallState.logStateOnce()
    end
    
    return results
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6Install = Area6Install

return Area6Install
