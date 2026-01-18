-- NerveUtils.lua - 공용 유틸리티 (v0.1)

NerveUtils = NerveUtils or {}

-- table.wipe polyfill

-- PZ Lua 환경에 table.wipe가 없을 수 있으므로 polyfill 설치
if not table.wipe then
    table.wipe = function(t)
        for k in pairs(t) do
            t[k] = nil
        end
    end
    print("[Nerve] table.wipe polyfill installed")
end

-- 안전한 테이블 초기화
function NerveUtils.safeWipe(t)
    if t == nil then return end
    
    if table.wipe then
        table.wipe(t)
    else
        for k in pairs(t) do
            t[k] = nil
        end
    end
end

-- 로깅 유틸리티 (NerveLogger 위임)

-- NerveLogger 초기화 확인
local function ensureLogger()
    if Nerve and Nerve.Logger then
        return Nerve.Logger
    end
    return nil
end

function NerveUtils.debug(...)
    local logger = ensureLogger()
    if logger then
        logger.debug(...)
    elseif NerveConfig and NerveConfig.debug then
        print("[Nerve:DEBUG]", ...)
    end
end

function NerveUtils.info(...)
    local logger = ensureLogger()
    if logger then
        logger.info(...)
    else
        print("[Nerve]", ...)
    end
end

function NerveUtils.warn(...)
    local logger = ensureLogger()
    if logger then
        logger.warn(...)
    else
        print("[Nerve] WARN:", ...)
    end
end

function NerveUtils.error(...)
    local logger = ensureLogger()
    if logger then
        logger.error(...)
    else
        print("[Nerve] ERROR:", ...)
    end
end

-- 안전한 함수 호출 (pcall 래퍼)
function NerveUtils.safeCall(fn, ...)
    if type(fn) ~= "function" then
        return nil
    end
    
    local ok, result = pcall(fn, ...)
    if ok then
        return result
    else
        NerveUtils.debug("safeCall failed:", result)
        return nil
    end
end

-- 객체 ID 추출
function NerveUtils.getObjectId(obj)
    if obj == nil then
        return nil
    end
    
    -- 여러 메서드명 시도
    local getId = obj.getID or obj.getId or obj.GetID or obj.getid
    if getId then
        local ok, id = pcall(getId, obj)
        if ok and id ~= nil then
            return tostring(id)
        end
    end
    
    -- getType 시도
    local getType = obj.getType or obj.GetType
    if getType then
        local ok, typeStr = pcall(getType, obj)
        if ok and typeStr ~= nil then
            return tostring(typeStr)
        end
    end
    
    return nil
end

return NerveUtils
