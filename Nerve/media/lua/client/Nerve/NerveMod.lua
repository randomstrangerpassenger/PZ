--[[
    NerveMod.lua
    Nerve 모드 진입점
    
    v0.1 Final - 이벤트 디스패치 + UI/인벤토리 안정화
    
    핵심 기능:
    - Pulse 런타임 감지
    - 2중 초기화 훅 (OnGameBoot + OnInitGlobalModData)
    - Idempotent 이벤트 래핑 (__nerveWrapped)
    - 콜백 래핑 캐시 (weak table)
    - _listeners 안전 체크
    - Area 5: UI/Inventory coalesce
    - Area 6: Event deduplication
]]

-- 의존성 로드
require "Nerve/NerveUtils"
require "Nerve/area5/Area5Coordinator"

--------------------------------------------------------------------------------
-- Nerve 메인 모듈
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.VERSION = "0.1.0"
Nerve.hasPulse = false
Nerve.pulseVersion = nil

--------------------------------------------------------------------------------
-- 초기화 상태 관리 (2단계)
--------------------------------------------------------------------------------

local initState = "NONE"  -- NONE | STARTED | DONE

--------------------------------------------------------------------------------
-- 콜백 래핑 캐시 (weak table - GC 허용)
--------------------------------------------------------------------------------

local wrappedCallbacks = setmetatable({}, { __mode = "k" })

--------------------------------------------------------------------------------
-- Pulse 감지
--------------------------------------------------------------------------------

local function detectPulse()
    -- 방법 1: 전역 변수 확인 (더 안정적)
    if rawget(_G, "Pulse") and Pulse.VERSION then
        Nerve.hasPulse = true
        Nerve.pulseVersion = Pulse.VERSION
        NerveUtils.info("Pulse " .. Pulse.VERSION .. " detected - Full mode available")
        return
    end
    
    -- 방법 2: 모드 목록 확인 (폴백)
    local getActivatedMods = getActivatedMods
    if getActivatedMods then
        local activeMods = getActivatedMods()
        if activeMods and activeMods.contains then
            local pulseModId = NerveConfig and NerveConfig.pulseModId or "Pulse"
            if activeMods:contains(pulseModId) then
                Nerve.hasPulse = true
                NerveUtils.info("Pulse detected (mod list) - Full mode available")
                return
            end
        end
    end
    
    NerveUtils.info("Standalone mode (Lite)")
end

--------------------------------------------------------------------------------
-- 리스너 카운트 안전 조회
--------------------------------------------------------------------------------

local function getListenerCount(eventObj)
    if eventObj._listeners then
        return #eventObj._listeners
    elseif eventObj.listeners then
        return #eventObj.listeners
    end
    return nil  -- unknown
end

--------------------------------------------------------------------------------
-- 이벤트 래핑 (Idempotent)
--------------------------------------------------------------------------------

local function wrapEvent(eventName)
    local eventObj = Events[eventName]
    
    -- 이벤트 존재 확인
    if not eventObj then
        NerveUtils.warn("Event not found: " .. eventName)
        return false
    end
    
    -- 중복 래핑 방지
    if eventObj.__nerveWrapped then
        NerveUtils.debug("SKIP: Already wrapped: " .. eventName)
        return true  -- 이미 성공한 것으로 처리
    end
    
    -- Add 메서드 확인
    if not eventObj.Add then
        NerveUtils.warn("Event.Add not found: " .. eventName)
        return false
    end
    
    -- 기존 리스너 경고
    local listenerCount = getListenerCount(eventObj)
    if listenerCount and listenerCount > 0 then
        NerveUtils.warn(eventName .. " has " .. listenerCount 
            .. " existing listeners (uncontrolled)")
    elseif listenerCount == nil then
        NerveUtils.debug(eventName .. " listener count unknown")
    end
    
    -- 원본 Add 보존
    local originalAdd = eventObj.Add
    eventObj.__nerveOriginalAdd = originalAdd
    
    -- 래핑된 Add 함수
    local wrappedAdd = function(callback)
        -- 콜백 유효성 검사
        if type(callback) ~= "function" then
            return originalAdd(callback)
        end
        
        -- 이미 래핑된 콜백이면 재사용 (중복 리스너 폭증 방지)
        if wrappedCallbacks[callback] then
            return originalAdd(wrappedCallbacks[callback])
        end
        
        -- 새 래핑 콜백 생성
        local wrapped = function(...)
            -- Area6 Coordinator가 있으면 처리 위임
            if Nerve.Area6 and Nerve.Area6.shouldProcess then
                local contextKey = nil
                
                -- ContextExtractors가 있으면 키 추출
                if Nerve.ContextExtractors and Nerve.ContextExtractors.getContextKey then
                    contextKey = Nerve.ContextExtractors.getContextKey(eventName, ...)
                end
                
                if not Nerve.Area6.shouldProcess(eventName, contextKey) then
                    -- 스킵됨
                    return
                end
            end
            
            -- 원본 콜백 실행
            return callback(...)
        end
        
        -- 캐시에 저장
        wrappedCallbacks[callback] = wrapped
        
        return originalAdd(wrapped)
    end
    
    eventObj.Add = wrappedAdd
    eventObj.__nerveCurrentWrapper = wrappedAdd
    eventObj.__nerveWrapped = true
    
    NerveUtils.info("OK: Wrapped " .. eventName)
    return true
end

--------------------------------------------------------------------------------
-- 래퍼 무결성 체크 (디버그용)
--------------------------------------------------------------------------------

function Nerve.checkWrapperIntegrity()
    if not NerveConfig or not NerveConfig.area6 then return end
    
    local targetEvents = NerveConfig.area6.targetEvents or {}
    local issues = 0
    
    for _, eventName in ipairs(targetEvents) do
        local eventObj = Events[eventName]
        if eventObj and eventObj.__nerveWrapped then
            if eventObj.Add ~= eventObj.__nerveCurrentWrapper then
                NerveUtils.warn(eventName .. " wrapper was overwritten by another mod")
                issues = issues + 1
            end
        end
    end
    
    if issues > 0 then
        NerveUtils.warn("Wrapper integrity issues: " .. issues)
    else
        NerveUtils.debug("Wrapper integrity OK")
    end
    
    return issues
end

--------------------------------------------------------------------------------
-- 메인 초기화
--------------------------------------------------------------------------------

local function initializeNerve()
    -- 이미 완료된 경우 스킵
    if initState == "DONE" then
        return
    end
    
    -- 이전 초기화가 실패한 경우 재시도
    if initState == "STARTED" then
        NerveUtils.warn("Previous init incomplete, retrying...")
    end
    
    initState = "STARTED"
    
    -- 시작 배너
    NerveUtils.info("========================================")
    NerveUtils.info("Nerve v" .. Nerve.VERSION .. " - Event Dispatch Stabilizer")
    NerveUtils.info("\"The Event's meaning stays, only the form stabilizes\"")
    NerveUtils.info("========================================")
    
    -- Pulse 감지
    detectPulse()
    
    -- Area6 설정 확인
    if not NerveConfig or not NerveConfig.area6 or not NerveConfig.area6.enabled then
        NerveUtils.info("Area 6 disabled in config")
        initState = "DONE"
        return
    end
    
    -- 이벤트 래핑
    local targetEvents = NerveConfig.area6.targetEvents or {}
    local wrapResults = {
        success = {},
        failed = {}
    }
    
    for _, eventName in ipairs(targetEvents) do
        if wrapEvent(eventName) then
            table.insert(wrapResults.success, eventName)
        else
            table.insert(wrapResults.failed, eventName)
        end
    end
    
    -- 완료 로그
    NerveUtils.info("----------------------------------------")
    NerveUtils.info("Initialization complete")
    NerveUtils.info("Wrapped: " .. #wrapResults.success .. " events")
    
    if #wrapResults.failed > 0 then
        NerveUtils.warn("FAILED: " .. table.concat(wrapResults.failed, ", "))
    end
    
    NerveUtils.info("Mode: " .. (Nerve.hasPulse and "Full (Pulse)" or "Lite (Standalone)"))
    NerveUtils.info("========================================")
    
    -- Area 5 초기화 (UI/Inventory)
    if Nerve.Area5 and Nerve.Area5.init then
        Nerve.Area5.init()
    end
    
    initState = "DONE"
end

--------------------------------------------------------------------------------
-- 틱 핸들러
--------------------------------------------------------------------------------

local function onTickStart()
    -- Area6 틱 시작 처리
    if Nerve.Area6 and Nerve.Area6.onTickStart then
        Nerve.Area6.onTickStart()
    end
    
    -- Area5 틱 시작 처리
    if Nerve.Area5 and Nerve.Area5.onTickStart then
        Nerve.Area5.onTickStart()
    end
end

local function onTickEnd()
    -- Area6 틱 종료 처리
    if Nerve.Area6 and Nerve.Area6.onTickEnd then
        Nerve.Area6.onTickEnd()
    end
    
    -- Area5 틱 종료 처리
    if Nerve.Area5 and Nerve.Area5.onTickEnd then
        Nerve.Area5.onTickEnd()
    end
end

--------------------------------------------------------------------------------
-- 이벤트 등록 (2중 초기화 훅)
--------------------------------------------------------------------------------

-- 방법 1: OnGameBoot (일반적으로 빠름)
if Events.OnGameBoot then
    Events.OnGameBoot.Add(initializeNerve)
end

-- 방법 2: OnInitGlobalModData (더 빠를 수 있음)
if Events.OnInitGlobalModData then
    Events.OnInitGlobalModData.Add(initializeNerve)
end

-- 틱 시작 처리
if Events.OnTick then
    Events.OnTick.Add(onTickStart)
end

-- 틱 종료 처리
if Events.OnTickEven then
    Events.OnTickEven.Add(onTickEnd)
end

--------------------------------------------------------------------------------
-- 공개 API
--------------------------------------------------------------------------------

function Nerve.isInitialized()
    return initState == "DONE"
end

function Nerve.getStatus()
    return {
        version = Nerve.VERSION,
        initState = initState,
        hasPulse = Nerve.hasPulse,
        pulseVersion = Nerve.pulseVersion,
    }
end

return Nerve
