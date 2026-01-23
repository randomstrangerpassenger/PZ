--[[
    IrisRuleExecutor.lua - Rule 실행기
    
    AST 평가 → 조건 매칭 시 태그 추가.
    결과는 항상 Set(tags).
    finalTags = union(autoTags, manualTags)
]]

local IrisRuleExecutor = {}

local IrisAst = require "Iris/Rules/engine/IrisAst"
local IrisFactView = require "Iris/Data/IrisFactView"
local IrisRecipeIndex = require "Iris/Data/IrisRecipeIndex"
local IrisMoveablesIndex = require "Iris/Data/IrisMoveablesIndex"
local IrisFixingIndex = require "Iris/Data/IrisFixingIndex"

--- 리스트에 값이 포함되어 있는지 확인
local function listContains(list, value)
    if type(list) ~= "table" then
        return false
    end
    for _, v in ipairs(list) do
        if v == value then
            return true
        end
    end
    return false
end

--- Set에 값 추가
local function setAdd(set, value)
    set[value] = true
end

--- Set을 배열로 변환 (알파벳 정렬)
local function setToSortedArray(set)
    local arr = {}
    for k, _ in pairs(set) do
        table.insert(arr, k)
    end
    table.sort(arr)
    return arr
end

--- 두 Set의 합집합
local function setUnion(set1, set2)
    local result = {}
    for k, _ in pairs(set1) do
        result[k] = true
    end
    for k, _ in pairs(set2) do
        result[k] = true
    end
    return result
end

--- 안전한 함수 호출 (pcall wrapper)
local function safeCall(func, ...)
    local args = {...}
    local ok, result = pcall(function()
        return func(unpack(args))
    end)
    if ok then
        return result
    end
    -- 에러 로깅
    print("[IrisRuleExecutor] ERROR in safeCall: " .. tostring(result))
    return nil
end

--- Predicate 평가 (재귀)
--- @param node table AST 노드
--- @param item InventoryItem
--- @param fullType string
--- @return boolean
function IrisRuleExecutor.evaluatePredicate(node, item, fullType)
    if not node or not node.type then
        return false
    end
    
    local nodeType = node.type
    
    -- eq(field, value)
    if nodeType == IrisAst.NODE_TYPES.EQ then
        local actual = safeCall(IrisFactView.get, item, node.field)
        return actual == node.value
    
    -- has(field)
    elseif nodeType == IrisAst.NODE_TYPES.HAS then
        local result = safeCall(IrisFactView.has, item, node.field)
        return result == true
    
    -- not_has(field)
    elseif nodeType == IrisAst.NODE_TYPES.NOT_HAS then
        local result = safeCall(IrisFactView.has, item, node.field)
        return result ~= true
    
    -- contains(field, token)
    elseif nodeType == IrisAst.NODE_TYPES.CONTAINS then
        local list = safeCall(IrisFactView.get, item, node.field)
        return listContains(list, node.token)
    
    -- eq_bodyLocation(value)
    elseif nodeType == IrisAst.NODE_TYPES.EQ_BODY_LOCATION then
        local actual = safeCall(IrisFactView.get, item, "BodyLocation")
        return actual == node.value
    
    -- eq_ammoType(value)
    elseif nodeType == IrisAst.NODE_TYPES.EQ_AMMO_TYPE then
        local actual = safeCall(IrisFactView.get, item, "AmmoType")
        return actual == node.value
    
    -- recipe.matches({ role, category })
    elseif nodeType == IrisAst.NODE_TYPES.RECIPE_MATCHES then
        local result = safeCall(IrisRecipeIndex.matches, fullType, node.role, node.category)
        return result == true
    
    -- recipe.inGetItemTypes(groupName)
    elseif nodeType == IrisAst.NODE_TYPES.RECIPE_IN_GET_ITEM_TYPES then
        local result = safeCall(IrisRecipeIndex.inGetItemTypes, fullType, node.groupName)
        return result == true
    
    -- moveables.itemId_registered()
    elseif nodeType == IrisAst.NODE_TYPES.MOVEABLES_ITEM_ID_REGISTERED then
        local result = safeCall(IrisMoveablesIndex.isItemIdRegistered, fullType)
        return result == true
    
    -- moveables.tag_in(tags)
    elseif nodeType == IrisAst.NODE_TYPES.MOVEABLES_TAG_IN then
        local result = safeCall(IrisMoveablesIndex.tagIn, fullType, node.tags)
        return result == true
    
    -- fixing.role_eq(role)
    elseif nodeType == IrisAst.NODE_TYPES.FIXING_ROLE_EQ then
        local result = safeCall(IrisFixingIndex.roleEq, fullType, node.role)
        return result == true
    
    -- allOf([...]) - AND
    elseif nodeType == IrisAst.NODE_TYPES.ALL_OF then
        for _, child in ipairs(node.children or {}) do
            if not IrisRuleExecutor.evaluatePredicate(child, item, fullType) then
                return false
            end
        end
        return true
    
    -- anyOf([...]) - OR
    elseif nodeType == IrisAst.NODE_TYPES.ANY_OF then
        for _, child in ipairs(node.children or {}) do
            if IrisRuleExecutor.evaluatePredicate(child, item, fullType) then
                return true
            end
        end
        return false
    end
    
    return false
end

--- 단일 규칙 실행
--- @param rule table
--- @param item InventoryItem
--- @param fullType string
--- @return table Set(tags) or {}
function IrisRuleExecutor.executeRule(rule, item, fullType)
    local result = {}
    
    -- 안전하게 조건 평가
    local ok, match = pcall(IrisRuleExecutor.evaluatePredicate, rule.when, item, fullType)
    
    if not ok then
        -- 에러 발생 시 로그
        print("[IrisRuleExecutor] ERROR in evaluatePredicate for rule: " .. tostring(result))
        return result -- 빈 결과 반환
    end
    
    if match then
        for _, tag in ipairs(rule.add) do
            setAdd(result, tag)
        end
    end
    
    return result
end

--- 모든 규칙 실행
--- @param rules table[]
--- @param item InventoryItem
--- @param fullType string
--- @return table Set(tags)
function IrisRuleExecutor.executeAllRules(rules, item, fullType)
    local autoTags = {}
    
    for _, rule in ipairs(rules) do
        local ruleTags = IrisRuleExecutor.executeRule(rule, item, fullType)
        autoTags = setUnion(autoTags, ruleTags)
    end
    
    return autoTags
end

--- 최종 태그 계산 (auto + manual union)
--- @param rules table[]
--- @param manualOverrides table
--- @param item InventoryItem
--- @param fullType string
--- @return table Set(tags)
function IrisRuleExecutor.computeFinalTags(rules, manualOverrides, item, fullType)
    -- 자동 분류
    local autoTags = IrisRuleExecutor.executeAllRules(rules, item, fullType)
    
    -- 수동 오버라이드 (add-only union)
    local manualTags = {}
    if manualOverrides[fullType] and manualOverrides[fullType].add then
        for _, tag in ipairs(manualOverrides[fullType].add) do
            setAdd(manualTags, tag)
        end
    end
    
    -- 합집합
    return setUnion(autoTags, manualTags)
end

--- Set을 정렬된 배열로 변환 (UI용)
IrisRuleExecutor.setToSortedArray = setToSortedArray

return IrisRuleExecutor
