--[[
    IrisAPI.lua - Iris 아이템 분류 조회 API (읽기 전용)
    
    ⚠️ 헌법적 설계:
    - Iris는 "위키피디아형 모드"로서 정적 데이터 조회만 수행
    - 런타임 Rule Engine 없음 - 모든 분류는 빌드 시점에 사전 계산됨
    - IrisClassifications.lua에서 사전 계산된 태그 조회만 수행
]]

local IrisAPI = {}

-- 정적 데이터 (lazy load)
local IrisClassifications = nil
local IrisRecipeIndex = nil
local IrisMoveablesIndex = nil
local IrisFixingIndex = nil
local IrisContextOutcomes = nil
local IrisCapabilities = nil
local IrisUseCaseDescriptions = nil

local function ensureData()
    if not IrisClassifications then
        local ok, result = pcall(require, "Iris/Data/IrisClassifications")
        if ok then
            IrisClassifications = result
        else
            print("[IrisAPI] WARNING: IrisClassifications not found")
        end
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
    if not IrisContextOutcomes then
        local ok, result = pcall(require, "Iris/Data/IrisContextOutcomes")
        if ok then IrisContextOutcomes = result end
    end
    if not IrisCapabilities then
        local ok, result = pcall(require, "Iris/Data/IrisCapabilities")
        if ok then IrisCapabilities = result end
    end
    if not IrisUseCaseDescriptions then
        local ok, result = pcall(require, "Iris/Data/IrisUseCaseDescriptions")
        if ok then IrisUseCaseDescriptions = result end
    end
end

--- fullType 추출 헬퍼 (InventoryItem과 ScriptItem 둘 다 지원)
local function getFullTypeFromItem(item)
    if not item then return nil end
    if item.getFullType then
        local ok, result = pcall(function() return item:getFullType() end)
        if ok then return result end
    elseif item.getFullName then
        local ok, result = pcall(function() return item:getFullName() end)
        if ok then return result end
    end
    return nil
end

--- 아이템의 분류 태그 조회 (O(1) 정적 조회)
--- @param item InventoryItem|ScriptItem
--- @return table 태그 Set 또는 빈 테이블
function IrisAPI.getTagsForItem(item)
    if not item then return {} end
    
    ensureData()
    
    local fullType = getFullTypeFromItem(item)
    if not fullType then return {} end
    
    if not IrisClassifications then return {} end
    
    -- 정적 데이터에서 직접 조회
    local tags = IrisClassifications[fullType]
    if not tags then return {} end
    
    -- Array를 Set으로 변환
    local tagSet = {}
    for _, tag in ipairs(tags) do
        tagSet[tag] = true
    end
    return tagSet
end

--- fullType으로 태그 직접 조회
--- @param fullType string
--- @return table 태그 배열 또는 빈 테이블
function IrisAPI.getTags(fullType)
    if not fullType then return {} end
    
    ensureData()
    
    if not IrisClassifications then return {} end
    
    return IrisClassifications[fullType] or {}
end

--- 아이템이 특정 태그를 가지고 있는지 확인
--- @param fullType string
--- @param tag string
--- @return boolean
function IrisAPI.hasTag(fullType, tag)
    local tags = IrisAPI.getTags(fullType)
    for _, t in ipairs(tags) do
        if t == tag then return true end
    end
    return false
end

--- 아이템이 분류되었는지 확인
--- @param fullType string
--- @return boolean
function IrisAPI.isClassified(fullType)
    local tags = IrisAPI.getTags(fullType)
    return #tags > 0
end

--- 아이템의 Recipe 연결 정보 반환
--- @param item InventoryItem
--- @return table {{role, category}, ...} 배열
function IrisAPI.getRecipeConnectionsForItem(item)
    if not item then return {} end
    
    ensureData()
    
    if not IrisRecipeIndex then return {} end
    
    local fullType = getFullTypeFromItem(item)
    if not fullType then return {} end
    
    local ok, result = pcall(function()
        return IrisRecipeIndex.getRoles(fullType)
    end)
    
    if ok and result then return result end
    return {}
end

--- 아이템의 Moveables 연결 정보 반환
--- @param item InventoryItem
--- @return table {itemId_registered, moveablesTag}
function IrisAPI.getMoveablesInfoForItem(item)
    if not item then
        return { itemId_registered = false, moveablesTag = nil }
    end
    
    ensureData()
    
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
    if ok1 then registered = result1 end
    
    local ok2, result2 = pcall(function()
        return IrisMoveablesIndex.getMoveablesTag(fullType)
    end)
    if ok2 then tag = result2 end
    
    return { itemId_registered = registered, moveablesTag = tag }
end

--- 아이템의 Fixing 연결 정보 반환
--- @param item InventoryItem
--- @return table {isFixer}
function IrisAPI.getFixingInfoForItem(item)
    if not item then return { isFixer = false } end
    
    ensureData()
    
    if not IrisFixingIndex then return { isFixer = false } end
    
    local fullType = getFullTypeFromItem(item)
    if not fullType then return { isFixer = false } end
    
    local isFixer = false
    local ok, result = pcall(function()
        return IrisFixingIndex.isFixer(fullType)
    end)
    if ok then isFixer = result end
    
    return { isFixer = isFixer }
end


-- ============================================
-- Description Generator 연동 (Phase D2)
-- ============================================

local IrisDescGenerator = nil

local function ensureDescGenerator()
    if not IrisDescGenerator then
        local ok, result = pcall(require, "Pulse/Iris/Logic/IrisDesc/Generator")
        if ok then
            IrisDescGenerator = result
        else
            print("[IrisAPI] WARNING: IrisDescGenerator not found: " .. tostring(result))
        end
    end
end


--- 아이템의 설명 블록 배열 반환
--- @param fullType string 아이템 FullType
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return table 블록 문자열 배열
function IrisAPI.getDescriptionBlocks(fullType, primarySubcategory)
    print("[IrisAPI.getDescriptionBlocks] ========== START ==========")
    print("[IrisAPI.getDescriptionBlocks] fullType = " .. tostring(fullType))
    print("[IrisAPI.getDescriptionBlocks] primarySubcategory = " .. tostring(primarySubcategory))
    
    if not fullType then 
        print("[IrisAPI.getDescriptionBlocks] fullType is nil, returning empty")
        return {} 
    end
    
    print("[IrisAPI.getDescriptionBlocks] Calling ensureData()...")
    ensureData()
    print("[IrisAPI.getDescriptionBlocks] ensureData() complete")
    
    print("[IrisAPI.getDescriptionBlocks] Calling ensureDescGenerator()...")
    ensureDescGenerator()
    print("[IrisAPI.getDescriptionBlocks] ensureDescGenerator() complete")
    print("[IrisAPI.getDescriptionBlocks] IrisDescGenerator exists = " .. tostring(IrisDescGenerator ~= nil))
    
    if not IrisDescGenerator then 
        print("[IrisAPI.getDescriptionBlocks] IrisDescGenerator is nil, returning empty")
        return {} 
    end
    
    print("[IrisAPI.getDescriptionBlocks] Calling IrisAPI.getTags(" .. fullType .. ")...")
    local tags = IrisAPI.getTags(fullType)
    print("[IrisAPI.getDescriptionBlocks] getTags returned: " .. type(tags))
    if tags then
        print("[IrisAPI.getDescriptionBlocks] tags count = " .. #tags)
        for i, tag in ipairs(tags) do
            print("[IrisAPI.getDescriptionBlocks] tags[" .. i .. "] = '" .. tostring(tag) .. "'")
        end
    end
    
    if #tags == 0 then 
        print("[IrisAPI.getDescriptionBlocks] No tags found, returning empty")
        return {} 
    end
    
    print("[IrisAPI.getDescriptionBlocks] Calling IrisDescGenerator.generate()...")
    print("[IrisAPI.getDescriptionBlocks] IrisDescGenerator.generate exists = " .. tostring(IrisDescGenerator.generate ~= nil))
    
    local ok, result = pcall(function()
        return IrisDescGenerator.generate(fullType, tags, primarySubcategory)
    end)
    
    print("[IrisAPI.getDescriptionBlocks] generate pcall: ok=" .. tostring(ok))
    if not ok then
        print("[IrisAPI.getDescriptionBlocks] generate ERROR: " .. tostring(result))
        return {}
    end
    
    print("[IrisAPI.getDescriptionBlocks] result type = " .. type(result))
    if result then
        print("[IrisAPI.getDescriptionBlocks] result (blocks) count = " .. #result)
        for i, block in ipairs(result) do
            print("[IrisAPI.getDescriptionBlocks] block[" .. i .. "] = [[" .. tostring(block):sub(1, 100) .. "]]")
        end
    end
    
    print("[IrisAPI.getDescriptionBlocks] ========== END ==========")
    
    if ok and result then
        return result
    end
    return {}
end


--- 아이템의 설명 문자열 반환 (소분류 기반)
--- 소분류 템플릿(IrisDescGenerator)만 사용
--- @param fullType string 아이템 FullType
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return string 설명 문자열 또는 빈 문자열
function IrisAPI.getDescription(fullType, primarySubcategory)
    if not fullType then return "" end
    
    ensureData()
    ensureDescGenerator()
    
    if not IrisDescGenerator then
        return ""
    end
    
    local tags = IrisAPI.getTags(fullType)
    if #tags == 0 then
        return ""
    end
    
    local ok, result = pcall(function()
        return IrisDescGenerator.generate(fullType, tags, primarySubcategory)
    end)
    
    if ok and result and #result > 0 then
        return table.concat(result, "\n\n")
    end
    
    return ""
end


--- InventoryItem에서 설명 반환 (편의 함수)
--- @param item InventoryItem|ScriptItem
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return string 전체 설명 문자열
function IrisAPI.getDescriptionForItem(item, primarySubcategory)
    if not item then return "" end
    
    local fullType = getFullTypeFromItem(item)
    if not fullType then return "" end
    
    return IrisAPI.getDescription(fullType, primarySubcategory)
end


-- ============================================
-- UseCase Description Lines (빌드 산출물 표시 전용)
-- ============================================

--- UseCase description lines 반환 (빌드에서 결정된 데이터 그대로)
--- API 반환 형태 정규화: 항상 {lines={}, debug_lines={}} 반환. nil 반환 금지.
--- @param fullType string 아이템 FullType
--- @return table {lines={...}, debug_lines={...}}
function IrisAPI.getUseCaseLines(fullType)
    local EMPTY = { lines = {}, debug_lines = {} }
    if not fullType then return EMPTY end

    ensureData()

    if not IrisUseCaseDescriptions then return EMPTY end

    local entry = IrisUseCaseDescriptions[fullType]
    if not entry then return EMPTY end

    return {
        lines = entry.lines or {},
        debug_lines = entry.debug_lines or {},
    }
end


--- Context Outcome 조회 (v1.3)
--- @param fullType string
--- @return table outcome 배열
function IrisAPI.getOutcomes(fullType)
    if not fullType then return {} end
    
    ensureData()
    
    if not IrisContextOutcomes then return {} end
    
    return IrisContextOutcomes[fullType] or {}
end

--- 특정 Context Outcome 존재 확인 (v1.3)
--- @param fullType string
--- @param outcome string
--- @return boolean 존재 여부
function IrisAPI.hasOutcome(fullType, outcome)
    local outcomes = IrisAPI.getOutcomes(fullType)
    for _, o in ipairs(outcomes) do
        if o == outcome then return true end
    end
    return false
end


--- Right-Click Capability 조회
--- @param fullType string
--- @return table capability 배열
function IrisAPI.getCapabilities(fullType)
    if not fullType then return {} end
    
    ensureData()
    
    if not IrisCapabilities then return {} end
    
    return IrisCapabilities[fullType] or {}
end

--- 특정 Capability 존재 확인
--- @param fullType string
--- @param capability string
--- @return boolean 존재 여부
function IrisAPI.hasCapability(fullType, capability)
    local caps = IrisAPI.getCapabilities(fullType)
    for _, c in ipairs(caps) do
        if c == capability then return true end
    end
    return false
end



return IrisAPI

