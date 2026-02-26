--[[
    IrisRecipeIndex.lua - Recipe 인덱스
    
    OnGameStart 이벤트에서 1회만 빌드.
    다른 훅 포인트 사용 금지 (재현성 보장).
    
    인덱스 구조:
    - fullType -> Set<{role, category}>
    - GetItemTypes 그룹 -> Set<item> (allowlist 기반 필터)
]]

local IrisRecipeIndex = {}

-- 인덱스 데이터
IrisRecipeIndex._itemRoles = {}      -- fullType -> {{role, category}, ...}
IrisRecipeIndex._getItemTypes = {}   -- groupName -> {fullType, ...}
IrisRecipeIndex._built = false

-- GetItemTypes allowlist (폭주 방지)
local ALLOWED_GET_ITEM_TYPES = {
    "CanOpener"
}

--- 인덱스 빌드 (OnGameStart에서 1회만 호출)
function IrisRecipeIndex.build()
    if IrisRecipeIndex._built then
        return
    end
    
    -- getAllRecipes가 존재하는지 확인
    if not getAllRecipes then
        print("[IrisRecipeIndex] WARNING: getAllRecipes not available")
        IrisRecipeIndex._built = true
        return
    end
    
    -- 모든 레시피 순회
    local ok, allRecipes = pcall(getAllRecipes)
    if not ok or not allRecipes then
        print("[IrisRecipeIndex] WARNING: getAllRecipes() failed")
        IrisRecipeIndex._built = true
        return
    end
    
    -- size 메서드가 있는지 확인
    if not allRecipes.size then
        print("[IrisRecipeIndex] WARNING: allRecipes has no size method")
        IrisRecipeIndex._built = true
        return
    end
    
    local recipeCount = allRecipes:size()
    for i = 0, recipeCount - 1 do
        local recipe = allRecipes:get(i)
        if recipe then
            local category = "Unknown"
            if recipe.getCategory then
                local catOk, cat = pcall(function() return recipe:getCategory() end)
                if catOk and cat then category = cat end
            end
            
            -- 레시피 이름 추출
            local recipeName = "Unknown"
            if recipe.getName then
                local nameOk, name = pcall(function() return recipe:getName() end)
                if nameOk and name then recipeName = tostring(name) end
            end
            
            -- input 역할 아이템들
            if recipe.getSource then
                local srcOk, inputs = pcall(function() return recipe:getSource() end)
                if srcOk and inputs and inputs.size then
                    for j = 0, inputs:size() - 1 do
                        local source = inputs:get(j)
                        if source and source.getItems then
                            local itemsOk, items = pcall(function() return source:getItems() end)
                            if itemsOk and items and items.size then
                                for k = 0, items:size() - 1 do
                                    local itemType = items:get(k)
                                    if itemType then
                                        IrisRecipeIndex._addRole(tostring(itemType), "input", category, recipeName)
                                    end
                                end
                            end
                        end
                    end
                end
            end
            
            -- keep 역할 아이템들
            if recipe.getKeep then
                local keepOk, keep = pcall(function() return recipe:getKeep() end)
                if keepOk and keep and keep.size then
                    for j = 0, keep:size() - 1 do
                        local keepItem = keep:get(j)
                        if keepItem then
                            IrisRecipeIndex._addRole(tostring(keepItem), "keep", category, recipeName)
                        end
                    end
                end
            end
            
            -- require 역할 아이템들 (도구)
            if recipe.getRequire then
                local reqOk, require = pcall(function() return recipe:getRequire() end)
                if reqOk and require and require.size then
                    for j = 0, require:size() - 1 do
                        local reqItem = require:get(j)
                        if reqItem then
                            IrisRecipeIndex._addRole(tostring(reqItem), "require", category, recipeName)
                        end
                    end
                end
            end
        end
    end
    
    -- GetItemTypes 그룹 빌드 (안전하게)
    if Recipe and Recipe.GetItemTypes then
        for _, groupName in ipairs(ALLOWED_GET_ITEM_TYPES) do
            local ok2, items = pcall(function() return Recipe.GetItemTypes[groupName] end)
            if ok2 and items and type(items) == "table" then
                IrisRecipeIndex._getItemTypes[groupName] = {}
                for fullType, _ in pairs(items) do
                    table.insert(IrisRecipeIndex._getItemTypes[groupName], fullType)
                end
            end
        end
    end
    -- 인덱스 통계 출력
    local rolesCount = 0
    for _ in pairs(IrisRecipeIndex._itemRoles) do
        rolesCount = rolesCount + 1
    end
    print("[IrisRecipeIndex] Build complete: " .. rolesCount .. " items indexed")
    
    IrisRecipeIndex._built = true
end

--- 내부: role 추가 (중복 방지 포함)
function IrisRecipeIndex._addRole(fullType, role, category, recipeName)
    if not IrisRecipeIndex._itemRoles[fullType] then
        IrisRecipeIndex._itemRoles[fullType] = {}
        IrisRecipeIndex._itemRoles[fullType]._dedup = {} -- 중복 방지용
    end
    
    local bucket = IrisRecipeIndex._itemRoles[fullType]
    local key = tostring(role) .. "|" .. tostring(category) .. "|" .. tostring(recipeName)
    
    -- 중복이면 스킵
    if bucket._dedup[key] then return end
    bucket._dedup[key] = true
    
    table.insert(bucket, {
        role = role,
        category = category,
        recipe = recipeName
    })
end

--- 아이템의 Recipe 역할 조회
--- @param fullType string
--- @return table {{role, category}, ...}
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
