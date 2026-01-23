--[[
    IrisFactView.lua - Item Script "사실 뷰"
    
    Rule Engine이 읽는 값만 안정적으로 추출합니다.
    
    정규화 규칙:
    - 키 없음 / 타입 불일치 → nil
    - false, 0, "" → 원본 값 유지 ("존재"로 간주)
    - 리스트 필드(Tags/Categories/CustomContextMenu) → 항상 table로 정규화
    
    has(X) = FactView.get(X) ~= nil
]]

local IrisFactView = {}

--- 리스트 필드를 항상 table로 정규화
--- @param value any
--- @return table
local function normalizeList(value)
    if value == nil then
        return nil
    end
    if type(value) == "table" then
        return value
    end
    if type(value) == "string" then
        -- 단일 값이면 {value}로 변환
        return { value }
    end
    return nil
end
--- 안전하게 메서드 호출하는 헬퍼
--- @param obj any
--- @param methodName string
--- @return any
local function safeCall(obj, methodName, ...)
    if not obj then return nil end
    local method = obj[methodName]
    if not method then return nil end
    local ok, result = pcall(method, obj, ...)
    if ok then return result end
    return nil
end

--- 아이템에서 필드 값을 안정적으로 추출
--- @param item InventoryItem|ScriptItem
--- @param fieldName string
--- @return any 정규화된 값 또는 nil
function IrisFactView.get(item, fieldName)
    if not item then
        return nil
    end
    
    -- ScriptItem 추출 (InventoryItem이면 getScriptItem 호출, ScriptItem이면 그대로 사용)
    local scriptItem = nil
    if item.getScriptItem then
        -- InventoryItem인 경우
        local ok, result = pcall(function() return item:getScriptItem() end)
        if ok then scriptItem = result end
    elseif item.getType then
        -- ScriptItem인 경우 (getType 메서드가 있음)
        scriptItem = item
    end
    
    if not scriptItem then
        return nil
    end
    
    -- 필드별 추출 로직 (모든 호출을 pcall로 보호)
    if fieldName == "Type" then
        local typeEnum = safeCall(scriptItem, "getType")
        if typeEnum then
            return tostring(typeEnum)
        end
        return nil
        
    elseif fieldName == "SubCategory" then
        local subCat = safeCall(scriptItem, "getSubCategory")
        if subCat then
            return tostring(subCat)
        end
        return nil
        
    elseif fieldName == "Categories" then
        local cats = safeCall(scriptItem, "getCategories")
        return normalizeList(cats)
        
    elseif fieldName == "Tags" then
        local tags = safeCall(scriptItem, "getTags")
        return normalizeList(tags)
        
    elseif fieldName == "CustomContextMenu" then
        -- CustomContextMenu는 별도 처리 필요
        -- TODO: 실제 PZ API 확인 후 구현
        return nil
        
    elseif fieldName == "BodyLocation" then
        local loc = safeCall(scriptItem, "getBodyLocation")
        if loc then
            return tostring(loc)
        end
        return nil
        
    elseif fieldName == "AmmoType" then
        local ammo = safeCall(scriptItem, "getAmmoType")
        if ammo then
            return tostring(ammo)
        end
        return nil
        
    elseif fieldName == "Alcoholic" then
        return safeCall(scriptItem, "getAlcoholic")
        
    elseif fieldName == "CanStoreWater" then
        return safeCall(scriptItem, "getCanStoreWater")
        
    elseif fieldName == "TorchCone" then
        return safeCall(scriptItem, "getTorchCone")
        
    elseif fieldName == "ActivatedItem" then
        return safeCall(scriptItem, "isActivatedItem")
        
    elseif fieldName == "TwoWay" then
        return safeCall(scriptItem, "isTwoWay")
        
    elseif fieldName == "IsLiterature" then
        return safeCall(scriptItem, "isLiterature")
        
    elseif fieldName == "IsAimedFirearm" then
        return safeCall(scriptItem, "isAimedFirearm")
        
    elseif fieldName == "LightStrength" then
        local val = safeCall(scriptItem, "getLightStrength")
        if val and val > 0 then
            return val
        end
        return nil
        
    elseif fieldName == "LightDistance" then
        local val = safeCall(scriptItem, "getLightDistance")
        if val and val > 0 then
            return val
        end
        return nil
        
    elseif fieldName == "HungerChange" then
        local val = safeCall(scriptItem, "getHungerChange")
        if val then
            return val
        end
        return nil
        
    elseif fieldName == "ThirstChange" then
        local val = safeCall(scriptItem, "getThirstChange")
        if val then
            return val
        end
        return nil
        
    elseif fieldName == "StressChange" then
        local val = safeCall(scriptItem, "getStressChange")
        if val then
            return val
        end
        return nil
        
    elseif fieldName == "UnhappyChange" then
        local val = safeCall(scriptItem, "getUnhappyChange")
        if val then
            return val
        end
        return nil
        
    elseif fieldName == "TwoHandWeapon" then
        return safeCall(scriptItem, "isTwoHandWeapon")
        
    elseif fieldName == "MountOn" then
        local mount = safeCall(scriptItem, "getMountOn")
        if mount then
            return tostring(mount)
        end
        return nil
        
    elseif fieldName == "SkillTrained" then
        local skill = safeCall(scriptItem, "getSkillTrained")
        if skill then
            return tostring(skill)
        end
        return nil
        
    elseif fieldName == "TeachedRecipes" then
        local recipes = safeCall(scriptItem, "getTeachedRecipes")
        return normalizeList(recipes)
        
    elseif fieldName == "Map" then
        local map = safeCall(scriptItem, "getMap")
        if map then
            return tostring(map)
        end
        return nil
    end
    
    -- 알 수 없는 필드
    return nil
end

--- has() predicate 구현: 필드가 존재하는지 확인
--- @param item InventoryItem
--- @param fieldName string
--- @return boolean
function IrisFactView.has(item, fieldName)
    return IrisFactView.get(item, fieldName) ~= nil
end

return IrisFactView
