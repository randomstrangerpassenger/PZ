--[[
    Area9Shape.lua
    Shape Guard (observe/guard 모드)
    
    [헌법 준수]
    - hard/soft 스키마 분리
    - cheap→expensive 순서
    - 실패 이유: enum 코드만 (문자열 조립 금지)
    
    [모드 규칙]
    - observe (기본): hard fail도 증거만 남기고 통과
    - guard (opt-in): hard fail→철수 등록 (선리턴은 Dispatcher에서)
]]

require "Nerve/NerveUtils"
require "Nerve/area9/Area9TickCtx"
require "Nerve/area9/Area9Forensic"

--------------------------------------------------------------------------------
-- Area9Shape 모듈
--------------------------------------------------------------------------------

local Area9Shape = {}

-- 실패 이유 enum (정수만)
Area9Shape.FailReason = {
    NONE = 0,
    NIL_PAYLOAD = 1,
    TYPE_MISMATCH = 2,
    MISSING_REQUIRED = 3,
    INVALID_FORMAT = 4,
}

-- 스키마 타입
Area9Shape.SchemaType = {
    HARD = "hard",  -- 필수 (guard 모드 시 철수)
    SOFT = "soft",  -- 권장 (증거만)
}

--------------------------------------------------------------------------------
-- 스키마 정의 (cheap→expensive 순서)
--------------------------------------------------------------------------------

-- 기본 스키마 (네트워크 패킷용)
Area9Shape.defaultSchema = {
    -- 1. cheap 체크 (nil 체크)
    { field = "module", type = "string", required = true, schemaType = "hard" },
    { field = "command", type = "string", required = true, schemaType = "hard" },
    
    -- 2. 타입 체크
    { field = "player", type = "userdata", required = false, schemaType = "soft" },
    { field = "args", type = "table", required = false, schemaType = "soft" },
}

--------------------------------------------------------------------------------
-- Shape 체크
--------------------------------------------------------------------------------

-- payload 검증
-- @param payload: 검사할 데이터
-- @param schema: 스키마 (nil이면 기본 스키마)
-- @param scopeKey: 스코프 키 (guard 모드 확인용)
-- @return: isValid, failReason, failField
function Area9Shape.check(payload, schema, scopeKey)
    schema = schema or Area9Shape.defaultSchema
    
    -- nil 체크 (가장 cheap)
    if payload == nil then
        Area9Shape.recordFail(Area9Shape.FailReason.NIL_PAYLOAD, nil, scopeKey)
        return false, Area9Shape.FailReason.NIL_PAYLOAD, nil
    end
    
    -- 스키마 순회 (cheap→expensive 순서)
    for _, rule in ipairs(schema) do
        local value = payload[rule.field]
        
        -- 1. required 체크
        if rule.required and value == nil then
            if rule.schemaType == Area9Shape.SchemaType.HARD then
                Area9Shape.recordFail(Area9Shape.FailReason.MISSING_REQUIRED, rule.field, scopeKey)
                return false, Area9Shape.FailReason.MISSING_REQUIRED, rule.field
            end
        end
        
        -- 2. 타입 체크 (값이 있을 때만)
        if value ~= nil and rule.type then
            if type(value) ~= rule.type then
                if rule.schemaType == Area9Shape.SchemaType.HARD then
                    Area9Shape.recordFail(Area9Shape.FailReason.TYPE_MISMATCH, rule.field, scopeKey)
                    return false, Area9Shape.FailReason.TYPE_MISMATCH, rule.field
                end
            end
        end
    end
    
    return true, Area9Shape.FailReason.NONE, nil
end

-- 실패 기록 및 모드별 처리
function Area9Shape.recordFail(failReason, failField, scopeKey)
    local TickCtx = Nerve.Area9TickCtx
    local Forensic = Nerve.Area9Forensic
    
    -- Forensic 기록
    if Forensic then
        local reasonCode = (failReason == Area9Shape.FailReason.MISSING_REQUIRED)
            and Forensic.ReasonCode.SHAPE_HARD_FAIL
            or Forensic.ReasonCode.SHAPE_SOFT_FAIL
        Forensic.recordShapeFail(reasonCode, failReason, 0)
    end
    
    -- guard 모드 확인
    local isGuardMode = Area9Shape.isGuardMode(scopeKey)
    
    if isGuardMode and TickCtx then
        -- guard 모드: incident 표시 + quarantine 등록은 Dispatcher에서
        TickCtx.markIncident("shapeFail")
    end
end

-- guard 모드 확인
function Area9Shape.isGuardMode(scopeKey)
    -- config에서 기본 모드 확인
    local defaultMode = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.shape 
        and NerveConfig.area9.shape.defaultMode 
        or "observe"
    
    if defaultMode == "guard" then
        return true
    end
    
    -- opt-in 확인
    local guards = NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.optIn 
        and NerveConfig.area9.optIn.guards 
        or {}
    
    for _, key in ipairs(guards) do
        if key == scopeKey then
            return true
        end
    end
    
    return false
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Shape = Area9Shape

return Area9Shape
