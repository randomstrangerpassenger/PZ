--[[
    EarlyExitHandler.lua
    Early Exit & Cooldown 제어
    
    v1.0 - Phase 1-D
    
    핵심 원칙 (Fuse 철학 차용, 구현은 Nerve):
    - sustained 진입 → ACTIVE 상태
    - 시간 경과 (activeMaxMs) → 무조건 PASSTHROUGH
    - cooldown 동안 재진입 차단
    
    상태명: PASSTHROUGH (Fuse 네이밍 통일)
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- EarlyExitHandler 모듈
--------------------------------------------------------------------------------

local EarlyExitHandler = {}

-- 상태 상수 (Fuse 통일)
EarlyExitHandler.State = {
    PASSTHROUGH = "PASSTHROUGH",  -- 개입 없음, 모두 통과
    ACTIVE = "ACTIVE",            -- 개입 중
    COOLDOWN = "COOLDOWN",        -- 쿨다운 중, 재진입 차단
}

-- 현재 상태
EarlyExitHandler.state = EarlyExitHandler.State.PASSTHROUGH
EarlyExitHandler.activeStartMs = 0
EarlyExitHandler.cooldownStartMs = 0

-- 통계
local stats = {
    activeCount = 0,       -- ACTIVE 진입 횟수
    earlyExitCount = 0,    -- 시간 초과로 PASSTHROUGH 복귀 횟수
    cooldownCount = 0,     -- COOLDOWN 진입 횟수
}

--------------------------------------------------------------------------------
-- 설정 조회
--------------------------------------------------------------------------------

local function getConfig()
    if not NerveConfig or not NerveConfig.area6 
        or not NerveConfig.area6.earlyExit then
        return {
            enabled = false,
            activeMaxMs = 500,
            cooldownMs = 1000,
        }
    end
    return NerveConfig.area6.earlyExit
end

--------------------------------------------------------------------------------
-- 상태 전이
--------------------------------------------------------------------------------

-- 틱 시작 시 상태 갱신
function EarlyExitHandler.onTickStart()
    local config = getConfig()
    
    -- 비활성화 시 항상 PASSTHROUGH
    if not config.enabled then
        EarlyExitHandler.state = EarlyExitHandler.State.PASSTHROUGH
        return
    end
    
    local now = os.clock() * 1000  -- ms
    
    -- ACTIVE 상태: 시간 초과 체크
    if EarlyExitHandler.state == EarlyExitHandler.State.ACTIVE then
        local elapsed = now - EarlyExitHandler.activeStartMs
        
        if elapsed >= config.activeMaxMs then
            -- 무조건 PASSTHROUGH (Early Exit)
            EarlyExitHandler.state = EarlyExitHandler.State.COOLDOWN
            EarlyExitHandler.cooldownStartMs = now
            stats.earlyExitCount = stats.earlyExitCount + 1
            
            if NerveConfig and NerveConfig.debug then
                NerveUtils.debug("EARLY EXIT: Active duration " .. elapsed .. "ms exceeded, entering COOLDOWN")
            end
        end
    end
    
    -- COOLDOWN 상태: 쿨다운 완료 체크
    if EarlyExitHandler.state == EarlyExitHandler.State.COOLDOWN then
        local elapsed = now - EarlyExitHandler.cooldownStartMs
        
        if elapsed >= config.cooldownMs then
            EarlyExitHandler.state = EarlyExitHandler.State.PASSTHROUGH
            
            if NerveConfig and NerveConfig.debug then
                NerveUtils.debug("COOLDOWN COMPLETE: Returning to PASSTHROUGH")
            end
        end
    end
end

-- Sustained 상태 반영
function EarlyExitHandler.updateFromSustained(isSustained)
    local config = getConfig()
    
    if not config.enabled then
        return
    end
    
    -- PASSTHROUGH 상태에서 sustained 진입 시 ACTIVE로 전환
    if EarlyExitHandler.state == EarlyExitHandler.State.PASSTHROUGH and isSustained then
        EarlyExitHandler.state = EarlyExitHandler.State.ACTIVE
        EarlyExitHandler.activeStartMs = os.clock() * 1000
        stats.activeCount = stats.activeCount + 1
        
        if NerveConfig and NerveConfig.debug then
            NerveUtils.debug("ENTERING ACTIVE: Sustained pressure detected")
        end
    end
end

--------------------------------------------------------------------------------
-- 공개 API
--------------------------------------------------------------------------------

-- 현재 상태가 개입을 허용하는지 확인
function EarlyExitHandler.shouldIntervene()
    return EarlyExitHandler.state == EarlyExitHandler.State.ACTIVE
end

-- 현재 상태가 PASSTHROUGH인지 확인
function EarlyExitHandler.isPassthrough()
    return EarlyExitHandler.state == EarlyExitHandler.State.PASSTHROUGH
end

-- 현재 상태가 COOLDOWN인지 확인
function EarlyExitHandler.isCooldown()
    return EarlyExitHandler.state == EarlyExitHandler.State.COOLDOWN
end

-- 상태 조회
function EarlyExitHandler.getState()
    return EarlyExitHandler.state
end

-- 통계 조회
function EarlyExitHandler.getStats()
    return {
        state = EarlyExitHandler.state,
        activeStartMs = EarlyExitHandler.activeStartMs,
        cooldownStartMs = EarlyExitHandler.cooldownStartMs,
        activeCount = stats.activeCount,
        earlyExitCount = stats.earlyExitCount,
        cooldownCount = stats.cooldownCount,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.EarlyExitHandler = EarlyExitHandler

return EarlyExitHandler
