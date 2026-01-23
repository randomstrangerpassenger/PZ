--[[
    NerveMod.lua - Nerve 모드 진입점
    Pulse 감지, Idempotent 이벤트 래핑, Area 6 통합
]]

-- 의존성 로드
require "Nerve/NerveUtils"
require "Nerve/NerveLogger"

-- [Area9] 모듈 로드
require "Nerve/area9/Area9TickCtx"
require "Nerve/area9/Area9InstallState"
require "Nerve/area9/Area9Install"
require "Nerve/area9/Area9Forensic"
require "Nerve/area9/Area9Reentry"
require "Nerve/area9/Area9Duplicate"
require "Nerve/area9/Area9Shape"
require "Nerve/area9/Area9Depth"
require "Nerve/area9/Area9Call"
require "Nerve/area9/Area9Quarantine"
require "Nerve/area9/Area9Dispatcher"

--------------------------------------------------------------------------------
-- Nerve 메인 모듈
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.VERSION = "0.1.0"
Nerve.hasPulse = false
Nerve.pulseVersion = nil

-- 초기화 상태
local initState = "NONE"  -- NONE | STARTED | DONE

-- 콜백 래핑 캐시 (weak table)
local wrappedCallbacks = setmetatable({}, { __mode = "k" })

-- Pulse 감지
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

-- 리스너 카운트 안전 조회
local function getListenerCount(eventObj)
    if eventObj._listeners then
        return #eventObj._listeners
    elseif eventObj.listeners then
        return #eventObj.listeners
    end
    return nil  -- unknown
end

--------------------------------------------------------------------------------
-- Area6 철수 (Back-off)
--------------------------------------------------------------------------------

-- Area6 비활성화 (충돌 시 철수)
local function backoffArea6(reason)
    NerveUtils.warn("[!] Area6 BACK-OFF: " .. reason)
    if NerveConfig and NerveConfig.area6 then
        NerveConfig.area6.enabled = false
    end
end

-- 래핑 충돌 감지 (시작 시점)
local function checkWrapperConflict(eventName)
    local eventObj = Events[eventName]
    if not eventObj then return false end
    
    -- 이미 Nerve가 래핑함
    if eventObj.__nerveWrapped then
        return false
    end
    
    -- 다른 모드 래핑 감지 (휴리스틱)
    if eventObj.__customWrapped or eventObj.__modWrapped or eventObj.__wrapped then
        NerveUtils.warn("CONFLICT: " .. eventName .. " already wrapped by another mod")
        return true
    end
    
    return false
end

-- 이벤트 래핑 (Idempotent)
local function wrapEvent(eventName)
    local eventObj = Events[eventName]
    
    -- 이벤트 존재 확인
    if not eventObj then
        NerveUtils.warn("Event not found: " .. eventName)
        return false
    end
    
    -- 충돌 감지: 다른 모드가 이미 래핑한 경우 철수
    if checkWrapperConflict(eventName) then
        backoffArea6("Wrapper conflict on " .. eventName)
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
            -- Area6 활성화 여부 확인
            local area6Enabled = NerveConfig 
                and NerveConfig.area6 
                and NerveConfig.area6.enabled
            
            -- Area6 활성 + Dispatcher 존재 시에만 위임
            if area6Enabled 
                and Nerve.Area6Dispatcher 
                and Nerve.Area6Dispatcher.dispatch 
                and Nerve.Area6FailSoft then
                return Nerve.Area6Dispatcher.dispatch(eventName, callback, ...)
            end
            
            -- Area6 비활성 또는 모듈 미로드 시 원본 호출 (폴백)
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

-- 래퍼 무결성 체크
function Nerve.checkWrapperIntegrity()
    if not NerveConfig or not NerveConfig.area6 then return 0 end
    
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
        -- 충돌 발견 시 Area6 철수
        backoffArea6("Wrapper integrity compromised")
    else
        NerveUtils.debug("Wrapper integrity OK")
    end
    
    return issues
end

--------------------------------------------------------------------------------
-- Area9 초기화 (initializeNerve보다 먼저 정의되어야 함)
--------------------------------------------------------------------------------

local function initializeArea9()
    -- Area9 비활성화 시 스킵
    if not NerveConfig or not NerveConfig.area9 or not NerveConfig.area9.enabled then
        NerveUtils.info("Area 9 disabled in config")
        return
    end
    
    NerveUtils.info("----------------------------------------")
    NerveUtils.info("Area 9 initialization")
    
    local Area9Install = Nerve.Area9Install
    local Area9Dispatcher = Nerve.Area9Dispatcher
    local Area9InstallState = Nerve.Area9InstallState
    
    if not Area9Install or not Area9Dispatcher then
        NerveUtils.warn("Area9 modules not loaded")
        return
    end
    
    -- 디스패쳐 연결
    Area9Install.setDispatcher(Area9Dispatcher)
    
    -- 대상 이벤트 래핑
    local results = Area9Install.wrapAllTargetEvents()
    
    -- 결과 로그
    if #results.success > 0 then
        NerveUtils.info("Area9 wrapped: " .. table.concat(results.success, ", "))
    end
    
    if #results.failed > 0 then
        NerveUtils.warn("Area9 failed: " .. table.concat(results.failed, ", "))
    end
    
    -- 상태 확인
    if Area9InstallState then
        local state = Area9InstallState.getState()
        NerveUtils.info("Area9 state: " .. state)
    end
    
    NerveUtils.info("Area 9 initialization complete")
end

-- 메인 초기화
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
    
    -- 로거 초기화
    if Nerve.Logger and Nerve.Logger.init then
        Nerve.Logger.init()
    end
    
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
    
    -- targetEvents 이름 검증
    local rawEvents = NerveConfig.area6.targetEvents or {}
    local validatedEvents = {}
    for _, eventName in ipairs(rawEvents) do
        if Events[eventName] then
            table.insert(validatedEvents, eventName)
        else
            NerveUtils.warn("INVALID: '" .. eventName .. "' removed from targets")
        end
    end
    
    -- 이벤트 래핑
    local targetEvents = validatedEvents
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
    
    -- [NEW] Area9 초기화
    initializeArea9()
    
    initState = "DONE"
end

-- 틱 핸들러 (단일 진입점)
local function onTick()
    -- [필수-1] tickId 단일 진실의 소스
    -- Area6/Area9 모두 동일한 tick 기준 사용
    local currentTick = getTimestampMs and getTimestampMs() or os.time()
    
    -- Area6TickCtx 갱신
    if Nerve.Area6TickCtx and Nerve.Area6TickCtx.onTickStart then
        Nerve.Area6TickCtx.onTickStart()
    end
    
    -- [NEW] Area9TickCtx 갱신
    if NerveConfig and NerveConfig.area9 and NerveConfig.area9.enabled then
        if Nerve.Area9TickCtx and Nerve.Area9TickCtx.onTickStart then
            Nerve.Area9TickCtx.onTickStart(currentTick)
        end
        
        -- Quarantine 만료 정리
        if Nerve.Area9Quarantine and Nerve.Area9Quarantine.cleanup then
            Nerve.Area9Quarantine.cleanup()
        end
    end
end

-- 이벤트 등록 (2중 초기화 훅)

-- 방법 1: OnGameBoot (일반적으로 빠름)
if Events.OnGameBoot then
    Events.OnGameBoot.Add(initializeNerve)
end

-- 방법 2: OnInitGlobalModData (더 빠를 수 있음)
if Events.OnInitGlobalModData then
    Events.OnInitGlobalModData.Add(initializeNerve)
end

-- [FIX] 틱 처리 - 단일 핸들러만 등록
if Events.OnTick then
    Events.OnTick.Add(onTick)
end

-- 공개 API
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
