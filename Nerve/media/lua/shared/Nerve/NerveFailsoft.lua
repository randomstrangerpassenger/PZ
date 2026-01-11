--[[
    NerveFailsoft.lua
    컴포넌트별 Fail-soft 관리
    
    v1.0 - Phase 3-A 보강
    
    핵심 원칙:
    - Nerve 래핑/부가 로직이 터지면 → Fail-soft로 즉시 접기
    - 원본 바닐라 함수가 터지면 → 동일하게 터지게 하기
    - 연속 오류 N회 → 해당 컴포넌트 자동 비활성화
    - cooldown 후 자동 복귀
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- NerveFailsoft 모듈
--------------------------------------------------------------------------------

local NerveFailsoft = {}

-- 컴포넌트별 상태
NerveFailsoft.components = {}

-- 기본 설정
local DEFAULT_MAX_ERRORS = 3
local DEFAULT_COOLDOWN_MS = 10000  -- 10초

--------------------------------------------------------------------------------
-- 컴포넌트 등록
--------------------------------------------------------------------------------

function NerveFailsoft.register(componentName)
    if NerveFailsoft.components[componentName] then
        return  -- 이미 등록됨
    end
    
    NerveFailsoft.components[componentName] = {
        enabled = true,
        errorCount = 0,
        lastErrorMs = 0,
        disabledAt = 0,
        totalErrors = 0,
    }
end

--------------------------------------------------------------------------------
-- 오류 기록 및 비활성화 판단
--------------------------------------------------------------------------------

-- 오류 발생 시 호출
-- @return: true (계속 실행 가능), false (비활성화됨)
function NerveFailsoft.recordError(componentName, errorMsg)
    NerveFailsoft.register(componentName)
    local comp = NerveFailsoft.components[componentName]
    
    local now = os.clock() * 1000
    comp.errorCount = comp.errorCount + 1
    comp.totalErrors = comp.totalErrors + 1
    comp.lastErrorMs = now
    
    NerveUtils.warn("Failsoft: " .. componentName .. " error #" .. comp.errorCount 
        .. " - " .. tostring(errorMsg))
    
    -- 연속 오류 임계값 체크
    local maxErrors = DEFAULT_MAX_ERRORS
    if NerveConfig and NerveConfig.failsoft and NerveConfig.failsoft.maxErrors then
        maxErrors = NerveConfig.failsoft.maxErrors
    end
    
    if comp.errorCount >= maxErrors then
        comp.enabled = false
        comp.disabledAt = now
        NerveUtils.warn("Failsoft: " .. componentName .. " DISABLED (errors: " 
            .. comp.errorCount .. ")")
        return false
    end
    
    return true
end

--------------------------------------------------------------------------------
-- 컴포넌트 활성화 상태 확인
--------------------------------------------------------------------------------

-- 컴포넌트가 활성화되어 있는지 확인 (cooldown 복귀 포함)
function NerveFailsoft.isEnabled(componentName)
    NerveFailsoft.register(componentName)
    local comp = NerveFailsoft.components[componentName]
    
    -- 활성화 상태면 바로 반환
    if comp.enabled then
        return true
    end
    
    -- 비활성화 상태 + cooldown 체크
    local now = os.clock() * 1000
    local cooldownMs = DEFAULT_COOLDOWN_MS
    if NerveConfig and NerveConfig.failsoft and NerveConfig.failsoft.cooldownMs then
        cooldownMs = NerveConfig.failsoft.cooldownMs
    end
    
    if now - comp.disabledAt >= cooldownMs then
        -- cooldown 완료 → 자동 복귀
        comp.enabled = true
        comp.errorCount = 0  -- 오류 카운터 리셋
        NerveUtils.info("Failsoft: " .. componentName .. " re-enabled after cooldown")
        return true
    end
    
    return false
end

--------------------------------------------------------------------------------
-- 안전 실행 래퍼
--------------------------------------------------------------------------------

-- Nerve 로직을 안전하게 실행 (오류 시 fail-soft)
-- @param componentName: 컴포넌트 이름
-- @param fn: 실행할 함수
-- @param ...: 인자들
-- @return: 성공 시 함수 반환값, 실패 시 nil
function NerveFailsoft.safeExecute(componentName, fn, ...)
    if not NerveFailsoft.isEnabled(componentName) then
        return nil  -- 비활성화됨
    end
    
    local ok, result = pcall(fn, ...)
    
    if ok then
        -- 성공 시 오류 카운터 점진적 감소
        local comp = NerveFailsoft.components[componentName]
        if comp and comp.errorCount > 0 then
            comp.errorCount = math.max(0, comp.errorCount - 0.1)
        end
        return result
    else
        NerveFailsoft.recordError(componentName, result)
        return nil
    end
end

-- 원본 함수 호출 래퍼 (오류 시 재전파 - 바닐라 동작 유지)
-- @param componentName: 컴포넌트 이름 (로깅용)
-- @param fn: 원본 함수
-- @param ...: 인자들
-- @return: 함수 반환값 또는 오류 재전파
function NerveFailsoft.callOriginal(componentName, fn, ...)
    local ok, result = pcall(fn, ...)
    
    if ok then
        return result
    else
        -- 원본 오류 기록 후 재전파 (바닐라 동작 유지)
        NerveUtils.warn("Failsoft: Original " .. componentName .. " failed - " 
            .. tostring(result))
        error(result)  -- 예외 재전파
    end
end

--------------------------------------------------------------------------------
-- 통계 및 상태
--------------------------------------------------------------------------------

function NerveFailsoft.getStats()
    local stats = {}
    for name, comp in pairs(NerveFailsoft.components) do
        stats[name] = {
            enabled = comp.enabled,
            errorCount = comp.errorCount,
            totalErrors = comp.totalErrors,
        }
    end
    return stats
end

function NerveFailsoft.reset(componentName)
    if NerveFailsoft.components[componentName] then
        local comp = NerveFailsoft.components[componentName]
        comp.enabled = true
        comp.errorCount = 0
    end
end

function NerveFailsoft.resetAll()
    for name, _ in pairs(NerveFailsoft.components) do
        NerveFailsoft.reset(name)
    end
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Failsoft = NerveFailsoft

return NerveFailsoft
