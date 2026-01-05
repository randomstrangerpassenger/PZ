--[[
    ContextExtractors.lua
    이벤트별 컨텍스트 키 추출기
    
    v0.1 Final
    
    핵심 원칙:
    - 추출 실패 시 nil 반환 (중복 체크 건너뛰기)
    - "global" 폴백 사용 금지 (Entity Event 안전)
    - 메서드명 여러 변형 시도
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- ContextExtractors 모듈
--------------------------------------------------------------------------------

local ContextExtractors = {}

--------------------------------------------------------------------------------
-- 이벤트별 추출기 정의
--------------------------------------------------------------------------------

-- 안전하게 컨텍스트 추출 가능한 이벤트만 등록
-- 추출기 없는 이벤트는 nil 반환 → 중복 체크 건너뛰기
local extractors = {
    
    -- 컨테이너 업데이트
    ["OnContainerUpdate"] = function(container, ...)
        return NerveUtils.getObjectId(container)
    end,
    
    -- 인벤토리 업데이트
    ["OnInventoryUpdate"] = function(inventory, ...)
        return NerveUtils.getObjectId(inventory)
    end,
    
    -- 오브젝트 추가
    ["OnObjectAdded"] = function(obj, ...)
        return NerveUtils.getObjectId(obj)
    end,
    
    -- 오브젝트 제거
    ["OnObjectRemoved"] = function(obj, ...)
        return NerveUtils.getObjectId(obj)
    end,
    
    -- 추후 관측 데이터 기반으로 확장
    -- 예시:
    -- ["OnZombieDead"] = function(zombie, ...)
    --     return NerveUtils.getObjectId(zombie)
    -- end,
}

--------------------------------------------------------------------------------
-- 공개 API
--------------------------------------------------------------------------------

-- 컨텍스트 키 추출
-- @param eventName: 이벤트 이름
-- @param ...: 이벤트 인자들
-- @return: 컨텍스트 키 문자열 또는 nil (식별 불가)
function ContextExtractors.getContextKey(eventName, ...)
    local extractor = extractors[eventName]
    
    if not extractor then
        -- 추출기 없음 → nil 반환 (중복 체크 건너뛰기)
        return nil
    end
    
    -- pcall로 안전하게 호출
    local ok, key = pcall(extractor, ...)
    
    if ok and key ~= nil then
        return tostring(key)
    end
    
    -- 추출 실패 → nil 반환 (중복 체크 건너뛰기)
    return nil
end

-- 추출기 등록 (외부에서 확장 가능)
function ContextExtractors.register(eventName, extractorFn)
    if type(extractorFn) ~= "function" then
        NerveUtils.warn("Invalid extractor for " .. eventName)
        return false
    end
    
    extractors[eventName] = extractorFn
    NerveUtils.debug("Registered extractor for " .. eventName)
    return true
end

-- 추출기 존재 여부 확인
function ContextExtractors.hasExtractor(eventName)
    return extractors[eventName] ~= nil
end

-- 등록된 추출기 목록
function ContextExtractors.getRegisteredEvents()
    local result = {}
    for eventName, _ in pairs(extractors) do
        table.insert(result, eventName)
    end
    return result
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.ContextExtractors = ContextExtractors

return ContextExtractors
