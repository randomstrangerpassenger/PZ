--[[
    IrisAPI.lua - UI가 호출하는 단일 진입점 (읽기 전용)
    
    모든 Iris 데이터 접근은 이 API를 통해 이루어집니다.
    결과는 항상 Set(tags) 또는 읽기 전용 테이블입니다.
]]

local IrisAPI = {}

-- 의존성 (lazy load)
local IrisRuleLoader = nil
local IrisRuleExecutor = nil
local IrisRecipeIndex = nil
local IrisMoveablesIndex = nil
local IrisFixingIndex = nil

local function ensureDeps()
    if not IrisRuleLoader then
        local ok, result = pcall(require, "Iris/Rules/engine/IrisRuleLoader")
        if ok then IrisRuleLoader = result end
    end
    if not IrisRuleExecutor then
        local ok, result = pcall(require, "Iris/Rules/engine/IrisRuleExecutor")
        if ok then IrisRuleExecutor = result end
    end
    if not IrisRecipeIndex then
        local ok, result = pcall(require, "Iris/Data/IrisRecipeIndex")
        if ok then IrisRecipeIndex = result end
    end
    if not IrisMoveablesIndex then
        local ok, result = pcall(require, "Iris/Data/IrisMoveablesIndex")
        if ok then IrisMoveablesIndex = result end
    end
    if not IrisFixingIndex then
        local ok, result = pcall(require, "Iris/Data/IrisFixingIndex")
        if ok then IrisFixingIndex = result end
    end
end

--- fullType 추출 헬퍼 (InventoryItem과 ScriptItem 둘 다 지원)
--- @param item InventoryItem|ScriptItem
--- @return string|nil
local function getFullTypeFromItem(item)
    if not item then
        return nil
    end
    if item.getFullType then
        return item:getFullType()
    elseif item.getFullName then
        return item:getFullName()
    end
    return nil
end

-- 캐시: fullType -> finalTags (세션 캐시)
IrisAPI._cache = {}
IrisAPI._initialized = false

--- API 초기화 (Rule Engine 로드 확인)
function IrisAPI.ensureInitialized()
    if IrisAPI._initialized then
        return true
    end
    
    ensureDeps()
    
    -- Rule Engine 로드 확인
    if IrisRuleLoader and not IrisRuleLoader._loaded then
        local ok, err = pcall(function() IrisRuleLoader.load() end)
        if not ok then
            print("[IrisAPI] WARNING: RuleLoader.load() failed: " .. tostring(err))
        end
    end
    
    IrisAPI._initialized = true
    return true
end

--- @param item InventoryItem|ScriptItem
--- @return table Set(tags) 또는 빈 테이블
function IrisAPI.getTagsForItem(item)
    if not item then
        return {}
    end
    
    local fullType = getFullTypeFromItem(item)
    if not fullType then
        return {}
    end
    
    -- 캐시 확인
    if IrisAPI._cache[fullType] then
        return IrisAPI._cache[fullType]
    end
    
    -- 의존성 확인
    IrisAPI.ensureInitialized()
    
    -- Rule Engine 실행
    local tags = {}
    
    if IrisRuleExecutor and IrisRuleLoader then
        -- 규칙과 수동 오버라이드 로드
        local rules = IrisRuleLoader.getRules() or {}
        local overrides = IrisRuleLoader.getManualOverrides() or {}
        
        -- computeFinalTags 호출
        local ok, result = pcall(function()
            return IrisRuleExecutor.computeFinalTags(rules, overrides, item, fullType)
        end)
        if ok and result and type(result) == "table" then
            tags = result
        end
    end
    
    -- 캐시 저장
    IrisAPI._cache[fullType] = tags
    
    return tags
end

--- 아이템의 Recipe 연결 정보 반환
--- @param item InventoryItem
--- @return table {{role, category}, ...} 배열
function IrisAPI.getRecipeConnectionsForItem(item)
    if not item then
        return {}
    end
    
    ensureDeps()
    
    if not IrisRecipeIndex then
        return {}
    end
    
    local fullType = getFullTypeFromItem(item)
    if not fullType then
        return {}
    end
    
    local ok, result = pcall(function()
        return IrisRecipeIndex.getRoles(fullType)
    end)
    
    if ok and result then
        return result
    end
    
    return {}
end

--- 아이템의 Moveables 연결 정보 반환
--- @param item InventoryItem
--- @return table {itemId_registered, moveablesTag}
function IrisAPI.getMoveablesInfoForItem(item)
    if not item then
        return { itemId_registered = false, moveablesTag = nil }
    end
    
    ensureDeps()
    
    if not IrisMoveablesIndex then
        return { itemId_registered = false, moveablesTag = nil }
    end
    
    local fullType = getFullTypeFromItem(item)
    if not fullType then
        return { itemId_registered = false, moveablesTag = nil }
    end
    
    local registered = false
    local tag = nil
    
    local ok1, result1 = pcall(function()
        return IrisMoveablesIndex.isItemIdRegistered(fullType)
    end)
    if ok1 then
        registered = result1
    end
    
    local ok2, result2 = pcall(function()
        return IrisMoveablesIndex.getMoveablesTag(fullType)
    end)
    if ok2 then
        tag = result2
    end
    
    return { itemId_registered = registered, moveablesTag = tag }
end

--- 아이템의 Fixing 연결 정보 반환
--- @param item InventoryItem
--- @return table {isFixer}
function IrisAPI.getFixingInfoForItem(item)
    if not item then
        return { isFixer = false }
    end
    
    ensureDeps()
    
    if not IrisFixingIndex then
        return { isFixer = false }
    end
    
    local fullType = getFullTypeFromItem(item)
    if not fullType then
        return { isFixer = false }
    end
    
    local isFixer = false
    local ok, result = pcall(function()
        return IrisFixingIndex.isFixer(fullType)
    end)
    if ok then
        isFixer = result
    end
    
    return { isFixer = isFixer }
end

--- 캐시 초기화 (테스트/디버그용)
function IrisAPI.clearCache()
    IrisAPI._cache = {}
end

return IrisAPI
