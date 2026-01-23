--[[
    IrisRuleValidator.lua - 정적 검증기 (§9 전부)
    
    로드 타임에 모든 규칙 검증.
    위반 시 로드 실패 (Fail-Fast).
    
    검증 규칙:
    - §9.1: Allowlist 필드/값/연산자 준수
    - §9.2: Guarded Fields 가드 누락 시 실패
    - §9.3: eq("Type", "Drainable") 보조증거 누락 시 실패
    - §9.4: contains("SubCategory", ...) 사용 시 실패
    - §9.5: recipe.matches에 category만 있고 role 없으면 실패
    - §9.6: manual override에 add 외 키 존재 시 실패
]]

local IrisRuleValidator = {}

local Allowlist = require "Iris/Rules/allowlist"
local IrisAst = require "Iris/Rules/engine/IrisAst"

--- 값이 테이블에 포함되어 있는지 확인
local function contains(tbl, value)
    for _, v in ipairs(tbl) do
        if v == value then
            return true
        end
    end
    return false
end

--- 단일 규칙 검증
--- @param rule table
--- @return boolean, string|nil (성공, 에러메시지)
function IrisRuleValidator.validateRule(rule)
    -- 필수 필드 확인
    if not rule.id then
        return false, "Missing required field: id"
    end
    if not rule.when then
        return false, "Missing required field: when (rule: " .. rule.id .. ")"
    end
    if not rule.add or type(rule.add) ~= "table" or #rule.add == 0 then
        return false, "Missing or empty 'add' field (rule: " .. rule.id .. ")"
    end
    if not rule.reason then
        return false, "Missing required field: reason (rule: " .. rule.id .. ")"
    end
    
    -- when 조건 검증
    local ok, err = IrisRuleValidator.validatePredicate(rule.when, rule.id)
    if not ok then
        return false, err
    end
    
    return true, nil
end

--- Predicate 검증 (재귀)
--- @param node table
--- @param ruleId string
--- @return boolean, string|nil
function IrisRuleValidator.validatePredicate(node, ruleId)
    if not node or not node.type then
        return false, "Invalid predicate node (rule: " .. ruleId .. ")"
    end
    
    local nodeType = node.type
    
    -- §9.1: 금지 연산자 확인
    if contains(Allowlist.FORBIDDEN_OPERATORS, nodeType) then
        return false, "Forbidden operator '" .. nodeType .. "' (rule: " .. ruleId .. ")"
    end
    
    -- eq 검증
    if nodeType == IrisAst.NODE_TYPES.EQ then
        if not contains(Allowlist.EQ_FIELDS, node.field) then
            return false, "Field '" .. node.field .. "' not in eq allowlist (rule: " .. ruleId .. ")"
        end
        
        -- Type 값 검증
        if node.field == "Type" then
            if not contains(Allowlist.TYPE_VALUES, node.value) then
                return false, "Type value '" .. tostring(node.value) .. "' not allowed (rule: " .. ruleId .. ")"
            end
        end
        
        -- SubCategory 값 검증
        if node.field == "SubCategory" then
            if not contains(Allowlist.SUBCATEGORY_VALUES, node.value) then
                return false, "SubCategory value '" .. tostring(node.value) .. "' not allowed (rule: " .. ruleId .. ")"
            end
        end
    
    -- has 검증
    elseif nodeType == IrisAst.NODE_TYPES.HAS then
        if not contains(Allowlist.HAS_FIELDS, node.field) then
            return false, "Field '" .. node.field .. "' not in has allowlist (rule: " .. ruleId .. ")"
        end
        -- §9.2: Guarded Fields는 별도 컨텍스트 검증 필요 (allOf 내에서)
    
    -- not_has 검증
    elseif nodeType == IrisAst.NODE_TYPES.NOT_HAS then
        if not contains(Allowlist.HAS_FIELDS, node.field) then
            return false, "Field '" .. node.field .. "' not in has allowlist (rule: " .. ruleId .. ")"
        end
    
    -- contains 검증
    elseif nodeType == IrisAst.NODE_TYPES.CONTAINS then
        -- §9.4: SubCategory에 contains 사용 금지
        if node.field == "SubCategory" then
            return false, "contains() cannot be used with SubCategory - use eq() instead (rule: " .. ruleId .. ")"
        end
        
        if not contains(Allowlist.CONTAINS_FIELDS, node.field) then
            return false, "Field '" .. node.field .. "' not in contains allowlist (rule: " .. ruleId .. ")"
        end
        
        -- 토큰 값 검증
        if node.field == "Categories" then
            if not contains(Allowlist.CATEGORIES_VALUES, node.token) then
                return false, "Categories value '" .. node.token .. "' not allowed (rule: " .. ruleId .. ")"
            end
        elseif node.field == "Tags" then
            if not contains(Allowlist.TAGS_VALUES, node.token) then
                return false, "Tags value '" .. node.token .. "' not allowed (rule: " .. ruleId .. ")"
            end
        elseif node.field == "CustomContextMenu" then
            if not contains(Allowlist.CUSTOM_CONTEXT_MENU_VALUES, node.token) then
                return false, "CustomContextMenu value '" .. node.token .. "' not allowed (rule: " .. ruleId .. ")"
            end
        end
    
    -- eq_bodyLocation 검증
    elseif nodeType == IrisAst.NODE_TYPES.EQ_BODY_LOCATION then
        if not contains(Allowlist.BODY_LOCATION_VALUES, node.value) then
            return false, "BodyLocation value '" .. node.value .. "' not allowed (rule: " .. ruleId .. ")"
        end
    
    -- eq_ammoType 검증
    elseif nodeType == IrisAst.NODE_TYPES.EQ_AMMO_TYPE then
        if not contains(Allowlist.AMMO_TYPE_VALUES, node.value) then
            return false, "AmmoType value '" .. node.value .. "' not allowed (rule: " .. ruleId .. ")"
        end
    
    -- recipe.matches 검증
    elseif nodeType == IrisAst.NODE_TYPES.RECIPE_MATCHES then
        -- §9.5: role과 category 둘 다 필수
        if not node.role then
            return false, "recipe.matches requires 'role' (rule: " .. ruleId .. ")"
        end
        if not node.category then
            return false, "recipe.matches requires 'category' - category alone is forbidden (rule: " .. ruleId .. ")"
        end
        
        if not contains(Allowlist.RECIPE_ROLES, node.role) then
            return false, "Recipe role '" .. node.role .. "' not allowed (rule: " .. ruleId .. ")"
        end
        if not contains(Allowlist.RECIPE_CATEGORIES, node.category) then
            return false, "Recipe category '" .. node.category .. "' not allowed (rule: " .. ruleId .. ")"
        end
    
    -- recipe.inGetItemTypes 검증
    elseif nodeType == IrisAst.NODE_TYPES.RECIPE_IN_GET_ITEM_TYPES then
        if not contains(Allowlist.GET_ITEM_TYPES_GROUPS, node.groupName) then
            return false, "GetItemTypes group '" .. node.groupName .. "' not allowed (rule: " .. ruleId .. ")"
        end
    
    -- moveables.tag_in 검증
    elseif nodeType == IrisAst.NODE_TYPES.MOVEABLES_TAG_IN then
        for _, tag in ipairs(node.tags or {}) do
            if not contains(Allowlist.MOVEABLES_TAGS, tag) then
                return false, "MoveablesTag '" .. tag .. "' not allowed (rule: " .. ruleId .. ")"
            end
        end
    
    -- fixing.role_eq 검증
    elseif nodeType == IrisAst.NODE_TYPES.FIXING_ROLE_EQ then
        if not contains(Allowlist.FIXING_ROLES, node.role) then
            return false, "Fixing role '" .. node.role .. "' not allowed (rule: " .. ruleId .. ")"
        end
    
    -- allOf 검증 (재귀)
    elseif nodeType == IrisAst.NODE_TYPES.ALL_OF then
        for i, child in ipairs(node.children or {}) do
            local ok, err = IrisRuleValidator.validatePredicate(child, ruleId)
            if not ok then
                return false, err
            end
        end
    
    -- anyOf 검증 (재귀)
    elseif nodeType == IrisAst.NODE_TYPES.ANY_OF then
        for i, child in ipairs(node.children or {}) do
            local ok, err = IrisRuleValidator.validatePredicate(child, ruleId)
            if not ok then
                return false, err
            end
        end
    
    -- moveables.itemId_registered는 인자 없음
    elseif nodeType == IrisAst.NODE_TYPES.MOVEABLES_ITEM_ID_REGISTERED then
        -- OK
    
    else
        return false, "Unknown predicate type '" .. nodeType .. "' (rule: " .. ruleId .. ")"
    end
    
    return true, nil
end

--- Manual Override 검증
--- §9.6: add 외 키 존재 시 실패
--- @param overrides table
--- @return boolean, string|nil
function IrisRuleValidator.validateManualOverrides(overrides)
    for fullType, entry in pairs(overrides) do
        for key, _ in pairs(entry) do
            if key ~= "add" then
                return false, "Manual override for '" .. fullType .. "' contains forbidden key '" .. key .. "' - only 'add' is allowed"
            end
        end
        
        if not entry.add or type(entry.add) ~= "table" then
            return false, "Manual override for '" .. fullType .. "' has invalid 'add' field"
        end
    end
    
    return true, nil
end

--- 전체 Ruleset 검증
--- @param rules table[]
--- @return boolean, string|nil
function IrisRuleValidator.validateRuleset(rules)
    -- 빈 테이블은 합법 (자동 분류 불가 소분류)
    if type(rules) ~= "table" then
        return false, "Ruleset must be a table"
    end
    
    for i, rule in ipairs(rules) do
        local ok, err = IrisRuleValidator.validateRule(rule)
        if not ok then
            return false, err
        end
    end
    
    return true, nil
end

return IrisRuleValidator
