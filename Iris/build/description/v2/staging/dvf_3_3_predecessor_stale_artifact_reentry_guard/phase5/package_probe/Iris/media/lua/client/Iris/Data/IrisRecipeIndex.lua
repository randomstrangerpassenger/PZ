--[[
    IrisRecipeIndex.lua - precompiled Recipe index wrapper

    Runtime code must not call PZ recipe scanners. The data table is generated
    by Iris/build/description/v2/tools/build/build_iris_recipe_index_data.py.
]]

local IrisRecipeIndex = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire

local ok, data = safeRequire("Iris/Data/IrisRecipeIndexData")
if not ok or not data then
    data = { itemRoles = {}, getItemTypes = {} }
end

IrisRecipeIndex._itemRoles = data.itemRoles or {}
IrisRecipeIndex._getItemTypes = data.getItemTypes or {}
IrisRecipeIndex._built = true
IrisRecipeIndex.version = data.version
IrisRecipeIndex.build_deprecated = true

--- @deprecated Precompiled data is loaded when this module is required.
function IrisRecipeIndex.build()
    return true
end

--- 아이템의 Recipe 역할 조회
--- @param fullType string
--- @return table {{role, category, recipe}, ...}
function IrisRecipeIndex.getRoles(fullType)
    return IrisRecipeIndex._itemRoles[fullType] or {}
end

--- 아이템이 특정 role+category 조합에 매칭되는지
--- @param fullType string
--- @param role string
--- @param category string
--- @return boolean
function IrisRecipeIndex.matches(fullType, role, category)
    local roles = IrisRecipeIndex._itemRoles[fullType]
    if not roles then
        return false
    end

    for _, entry in ipairs(roles) do
        if entry.role == role and entry.category == category then
            return true
        end
    end
    return false
end

--- 아이템이 GetItemTypes 그룹에 포함되는지
--- @param fullType string
--- @param groupName string
--- @return boolean
function IrisRecipeIndex.inGetItemTypes(fullType, groupName)
    local group = IrisRecipeIndex._getItemTypes[groupName]
    if not group then
        return false
    end

    for _, item in ipairs(group) do
        if item == fullType then
            return true
        end
    end
    return false
end

return IrisRecipeIndex
