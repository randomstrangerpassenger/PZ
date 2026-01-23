--[[
    IrisAst.lua - AST 노드 정의
    
    DSL의 모든 predicate와 combinator를 AST 노드로 정의.
    금지 노드(gt, lt, gte, lte, remove, priority)는 타입 자체가 없음.
]]

local IrisAst = {}

-- AST 노드 타입 상수
IrisAst.NODE_TYPES = {
    -- Item Script Predicate
    EQ = "eq",
    HAS = "has",
    NOT_HAS = "not_has",
    CONTAINS = "contains",
    EQ_BODY_LOCATION = "eq_bodyLocation",
    EQ_AMMO_TYPE = "eq_ammoType",
    
    -- Recipe Predicate
    RECIPE_MATCHES = "recipe.matches",
    RECIPE_IN_GET_ITEM_TYPES = "recipe.inGetItemTypes",
    
    -- Moveables Predicate
    MOVEABLES_ITEM_ID_REGISTERED = "moveables.itemId_registered",
    MOVEABLES_TAG_IN = "moveables.tag_in",
    
    -- Fixing Predicate
    FIXING_ROLE_EQ = "fixing.role_eq",
    
    -- Combinator
    ALL_OF = "allOf",
    ANY_OF = "anyOf",
}

--- eq(field, value) 노드 생성
--- @param field string
--- @param value any
--- @return table
function IrisAst.eq(field, value)
    return {
        type = IrisAst.NODE_TYPES.EQ,
        field = field,
        value = value,
    }
end

--- has(field) 노드 생성
--- @param field string
--- @return table
function IrisAst.has(field)
    return {
        type = IrisAst.NODE_TYPES.HAS,
        field = field,
    }
end

--- not_has(field) 노드 생성
--- @param field string
--- @return table
function IrisAst.not_has(field)
    return {
        type = IrisAst.NODE_TYPES.NOT_HAS,
        field = field,
    }
end

--- contains(field, token) 노드 생성
--- @param field string
--- @param token string
--- @return table
function IrisAst.contains(field, token)
    return {
        type = IrisAst.NODE_TYPES.CONTAINS,
        field = field,
        token = token,
    }
end

--- eq_bodyLocation(value) 노드 생성
--- @param value string
--- @return table
function IrisAst.eq_bodyLocation(value)
    return {
        type = IrisAst.NODE_TYPES.EQ_BODY_LOCATION,
        value = value,
    }
end

--- eq_ammoType(value) 노드 생성
--- @param value string
--- @return table
function IrisAst.eq_ammoType(value)
    return {
        type = IrisAst.NODE_TYPES.EQ_AMMO_TYPE,
        value = value,
    }
end

--- recipe.matches({ role, category }) 노드 생성
--- @param opts table { role, category }
--- @return table
function IrisAst.recipe_matches(opts)
    return {
        type = IrisAst.NODE_TYPES.RECIPE_MATCHES,
        role = opts.role,
        category = opts.category,
    }
end

--- recipe.inGetItemTypes(groupName) 노드 생성
--- @param groupName string
--- @return table
function IrisAst.recipe_inGetItemTypes(groupName)
    return {
        type = IrisAst.NODE_TYPES.RECIPE_IN_GET_ITEM_TYPES,
        groupName = groupName,
    }
end

--- moveables.itemId_registered() 노드 생성
--- @return table
function IrisAst.moveables_itemId_registered()
    return {
        type = IrisAst.NODE_TYPES.MOVEABLES_ITEM_ID_REGISTERED,
    }
end

--- moveables.tag_in(tags) 노드 생성
--- @param tags table
--- @return table
function IrisAst.moveables_tag_in(tags)
    return {
        type = IrisAst.NODE_TYPES.MOVEABLES_TAG_IN,
        tags = tags,
    }
end

--- fixing.role_eq(role) 노드 생성
--- @param role string
--- @return table
function IrisAst.fixing_role_eq(role)
    return {
        type = IrisAst.NODE_TYPES.FIXING_ROLE_EQ,
        role = role,
    }
end

--- allOf([...]) 노드 생성 (AND)
--- @param children table
--- @return table
function IrisAst.allOf(children)
    return {
        type = IrisAst.NODE_TYPES.ALL_OF,
        children = children,
    }
end

--- anyOf([...]) 노드 생성 (OR)
--- @param children table
--- @return table
function IrisAst.anyOf(children)
    return {
        type = IrisAst.NODE_TYPES.ANY_OF,
        children = children,
    }
end

return IrisAst
