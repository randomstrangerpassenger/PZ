--[[
    Area9Dispatcher.lua
    고정 실행 순서 디스패처
    
    [고정 순서]
    1. TickCtx 갱신
    2. Quarantine 체크 (선리턴 가능)
    3. Re-entrancy (BYPASS 표시만)
    4. Duplicate (카운트만)
    5. Shape (observe/guard 모드)
    6. Depth (상태 표시)
    7. Incident 조건(단일 플래그) → guardedPcall
    8. Forensic 기록
    
    [철수 트리거]
    - reasonCode 찍히면 그 키 그 틱 철수
    - 가중치/복합 조건/우선순위 금지
]]

require "Nerve/NerveUtils"
require "Nerve/area9/Area9TickCtx"
require "Nerve/area9/Area9InstallState"
require "Nerve/area9/Area9Forensic"
require "Nerve/area9/Area9Reentry"
require "Nerve/area9/Area9Duplicate"
require "Nerve/area9/Area9Shape"
require "Nerve/area9/Area9Depth"
require "Nerve/area9/Area9Call"
require "Nerve/area9/Area9Quarantine"

--------------------------------------------------------------------------------
-- Area9Dispatcher 모듈
--------------------------------------------------------------------------------

local Area9Dispatcher = {}

-- 마지막 처리 틱
Area9Dispatcher.lastDispatchTick = 0

--------------------------------------------------------------------------------
-- 디스패치 (고정 순서)
--------------------------------------------------------------------------------

-- 네트워크 경계 진입 시 디스패치
-- @param eventName: 이벤트 이름
-- @param originalCallback: 원본 콜백
-- @param ...: 콜백 인자
-- @return: 원본 콜백 반환값
function Area9Dispatcher.dispatch(eventName, originalCallback, ...)
    local TickCtx = Nerve.Area9TickCtx
    local InstallState = Nerve.Area9InstallState
    local Quarantine = Nerve.Area9Quarantine
    local Reentry = Nerve.Area9Reentry
    local Duplicate = Nerve.Area9Duplicate
    local Shape = Nerve.Area9Shape
    local Depth = Nerve.Area9Depth
    local Call = Nerve.Area9Call
    
    -- Area9 비활성화 시 원본 직접 호출
    if not NerveConfig or not NerveConfig.area9 or not NerveConfig.area9.enabled then
        return originalCallback(...)
    end
    
    -- InstallState 확인
    if InstallState and InstallState.getState() == "BYPASSED" then
        return originalCallback(...)
    end
    
    -- 스코프 키 생성
    local scopeKey = TickCtx and TickCtx.makeHandlerKey(tostring(originalCallback)) or "unknown"
    
    ----------------------------------------------------------------------------
    -- 1. TickCtx 갱신 (필수-1: 유일한 tickId 갱신 지점)
    ----------------------------------------------------------------------------
    -- [NOTE] TickCtx.onTickStart는 NerveMod.lua의 OnTick에서 호출됨
    -- 아래 폴백은 OnTick 전에 네트워크 이벤트가 먼저 발생하는 예외 케이스 대비
    -- TODO: 충분한 검증 후 이 폴백 제거 검토 (필수-1 엄격 준수)
    if TickCtx and not TickCtx.initialized then
        -- [FALLBACK] OnTick 전 첫 호출 시 임시 초기화
        -- 이 경로는 정상 상황에서는 타지 않아야 함
        NerveUtils.debug("[Area9Dispatcher] Fallback tick init (should be rare)")
        TickCtx.onTickStart(Area9Dispatcher.lastDispatchTick + 1)
    end
    Area9Dispatcher.lastDispatchTick = TickCtx and TickCtx.getCurrentTickId() or 0
    
    ----------------------------------------------------------------------------
    -- 2. Quarantine 체크 (선리턴 가능)
    ----------------------------------------------------------------------------
    if Quarantine and Quarantine.check(scopeKey) then
        -- Quarantine 상태 → 선리턴 (원본 호출 없이)
        NerveUtils.debug("[Area9Dispatcher] Quarantine skip: " .. scopeKey)
        return nil
    end
    
    ----------------------------------------------------------------------------
    -- 3. Re-entrancy (BYPASS 표시만)
    ----------------------------------------------------------------------------
    local isReentry = false
    if Reentry then
        isReentry = Reentry.checkEnter(scopeKey)
        -- Phase 2: 행동 금지 (표시만)
    end
    
    ----------------------------------------------------------------------------
    -- 4. Duplicate (카운트만, 스킵 금지)
    ----------------------------------------------------------------------------
    if Duplicate then
        local args = {...}
        local packetType = args[1] and type(args[1]) == "table" and args[1].module or "unknown"
        local connKey = args[2] or "unknown"
        Duplicate.check(packetType, connKey)
        -- Phase 2: 스킵 금지 (카운트만)
    end
    
    ----------------------------------------------------------------------------
    -- 5. Shape (observe/guard 모드)
    ----------------------------------------------------------------------------
    local shapeValid = true
    if Shape then
        local args = {...}
        local payload = args[1]  -- 첫 번째 인자를 payload로 가정
        shapeValid = Shape.check(payload, nil, scopeKey)
        
        -- guard 모드 + hard fail 시 Quarantine 등록
        if not shapeValid and Shape.isGuardMode(scopeKey) then
            if Quarantine and Quarantine.isOptIn(scopeKey) then
                Quarantine.enter(scopeKey)
            end
        end
    end
    
    ----------------------------------------------------------------------------
    -- 6. Depth (상태 표시)
    ----------------------------------------------------------------------------
    if Depth then
        Depth.enter(Depth.Domain.NETWORK)
    end
    
    ----------------------------------------------------------------------------
    -- 7. 콜백 실행 (incident 조건에 따라 fast/guarded)
    ----------------------------------------------------------------------------
    local success, result
    if Call then
        success, result = Call.call(originalCallback, scopeKey, ...)
    else
        success, result = true, originalCallback(...)
    end
    
    ----------------------------------------------------------------------------
    -- 8. 정리
    ----------------------------------------------------------------------------
    
    -- Depth 해제
    if Depth then
        Depth.exit(Depth.Domain.NETWORK)
    end
    
    -- Re-entrancy 해제
    if Reentry then
        Reentry.markExit(scopeKey)
    end
    
    -- 에러 발생 시 Quarantine 등록
    if not success and Quarantine and Quarantine.isOptIn(scopeKey) then
        Quarantine.enter(scopeKey)
    end
    
    return result
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Dispatcher = Area9Dispatcher

return Area9Dispatcher
