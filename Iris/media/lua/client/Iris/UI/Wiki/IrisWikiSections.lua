--[[
    IrisWikiSections.lua - 위키 패널 섹션 렌더링
    
    필수 섹션:
    A) 기본 정보 (무게, 타입, 모듈)
    B) 태그 목록 (복수 태그) — 알파벳 정렬
    C) 음식/소모품 속성 (배고픔, 갈증, 스트레스 변화량)
    D) 무기/도구 속성 (데미지, 범위, 내구도)
    E) 연결 시스템 (Recipe/Moveables/Fixing)
]]

local IrisWikiSections = {}

-- 의존성 (lazy load)
local IrisAPI = nil
local IrisRuleExecutor = nil

local function ensureDeps()
    if not IrisAPI then
        local ok, result = pcall(require, "Iris/IrisAPI")
        if ok then IrisAPI = result end
    end
    if not IrisRuleExecutor then
        local ok, result = pcall(require, "Iris/Rules/engine/IrisRuleExecutor")
        if ok then IrisRuleExecutor = result end
    end
end

--- 안전하게 메서드 호출
local function safeCall(obj, methodName)
    if not obj then return nil end
    local method = obj[methodName]
    if not method then return nil end
    local ok, result = pcall(function() return method(obj) end)
    if ok then return result end
    return nil
end

--- 번역 텍스트 가져오기 (IrisTranslationLoader 사용)
local function getLabel(key)
    -- IrisTranslationLoader 전역 변수 확인
    if IrisTranslationLoader and IrisTranslationLoader.get then
        local result = IrisTranslationLoader.get(key)
        if result and result ~= key then
            return result
        end
    end
    -- 폴백: 키에서 Iris_Detail_ 제거하고 반환
    return key:gsub("Iris_Detail_", "")
end

--- A) 기본 정보 섹션 렌더링
function IrisWikiSections.renderBasicInfoSection(item)
    local parts = {}
    
    -- 무게
    local weight = safeCall(item, "getActualWeight") or safeCall(item, "getWeight")
    if weight and type(weight) == "number" then
        table.insert(parts, string.format("%s: %.1f", getLabel("Iris_Detail_Weight"), weight))
    end
    
    -- 타입
    local itemType = safeCall(item, "getType") or safeCall(item, "getTypeString")
    if itemType then
        table.insert(parts, getLabel("Iris_Detail_Type") .. ": " .. tostring(itemType))
    end
    
    -- 모듈 (이름만 추출)
    local moduleName = safeCall(item, "getModule")
    if moduleName then
        local modStr = tostring(moduleName)
        -- Java 객체 문자열에서 이름 추출 (zombie.scripting... 제거)
        if modStr:find("@") then
            -- ScriptModule@xxxx 형식이면 getName() 시도
            local nameMethod = moduleName.getName
            if nameMethod then
                local ok, name = pcall(function() return moduleName:getName() end)
                if ok and name then
                    modStr = tostring(name)
                else
                    modStr = nil -- 실패시 표시 안함
                end
            else
                modStr = nil
            end
        end
        if modStr and modStr ~= "" then
            table.insert(parts, getLabel("Iris_Detail_Module") .. ": " .. modStr)
        end
    end
    
    if #parts == 0 then
        return nil
    end
    return table.concat(parts, " | ")
end

--- B) 태그 섹션 렌더링
function IrisWikiSections.renderTagsSection(item)
    ensureDeps()
    
    if not IrisAPI or not IrisAPI.getTagsForItem then
        return nil
    end
    
    local ok, tags = pcall(function() return IrisAPI.getTagsForItem(item) end)
    if not ok or not tags then
        return nil
    end
    
    -- 태그를 정렬된 배열로 변환
    local sorted = {}
    if IrisRuleExecutor and IrisRuleExecutor.setToSortedArray then
        sorted = IrisRuleExecutor.setToSortedArray(tags)
    else
        for tag, _ in pairs(tags) do
            table.insert(sorted, tag)
        end
        table.sort(sorted)
    end
    
    if #sorted == 0 then
        return nil
    end
    return getLabel("Iris_Detail_Tags") .. ": " .. table.concat(sorted, ", ")
end

--- C) 음식/소모품 속성 섹션 렌더링
function IrisWikiSections.renderFoodSection(item)
    local parts = {}
    
    -- 배고픔 변화
    local hunger = safeCall(item, "getHungerChange")
    if hunger and type(hunger) == "number" and hunger ~= 0 then
        local sign = hunger < 0 and "" or "+"
        table.insert(parts, string.format("%s: %s%.0f", getLabel("Iris_Detail_Hunger"), sign, hunger * 100))
    end
    
    -- 갈증 변화
    local thirst = safeCall(item, "getThirstChange")
    if thirst and type(thirst) == "number" and thirst ~= 0 then
        local sign = thirst < 0 and "" or "+"
        table.insert(parts, string.format("%s: %s%.0f", getLabel("Iris_Detail_Thirst"), sign, thirst * 100))
    end
    
    -- 스트레스 변화
    local stress = safeCall(item, "getStressChange")
    if stress and type(stress) == "number" and stress ~= 0 then
        local sign = stress < 0 and "" or "+"
        table.insert(parts, string.format("%s: %s%.0f", getLabel("Iris_Detail_Stress"), sign, stress * 100))
    end
    
    -- 권태감 변화
    local boredom = safeCall(item, "getBoredomChange")
    if boredom and type(boredom) == "number" and boredom ~= 0 then
        local sign = boredom < 0 and "" or "+"
        table.insert(parts, string.format("%s: %s%.0f", getLabel("Iris_Detail_Boredom"), sign, boredom * 100))
    end
    
    -- 칼로리
    local calories = safeCall(item, "getCalories")
    if calories and type(calories) == "number" and calories > 0 then
        table.insert(parts, string.format("%s: %.0f", getLabel("Iris_Detail_Calories"), calories))
    end
    
    if #parts == 0 then
        return nil
    end
    return table.concat(parts, " | ")
end

--- D) 무기/도구 속성 섹션 렌더링
function IrisWikiSections.renderWeaponSection(item)
    local parts = {}
    
    -- 최소/최대 데미지
    local minDmg = safeCall(item, "getMinDamage")
    local maxDmg = safeCall(item, "getMaxDamage")
    if minDmg and maxDmg and type(minDmg) == "number" and type(maxDmg) == "number" then
        if minDmg > 0 or maxDmg > 0 then
            table.insert(parts, string.format("%s: %.1f~%.1f", getLabel("Iris_Detail_Damage"), minDmg, maxDmg))
        end
    end
    
    -- 사거리
    local minRange = safeCall(item, "getMinRange")
    local maxRange = safeCall(item, "getMaxRange")
    if minRange and maxRange and type(minRange) == "number" and type(maxRange) == "number" then
        if maxRange > 0 then
            table.insert(parts, string.format("%s: %.1f~%.1f", getLabel("Iris_Detail_Range"), minRange, maxRange))
        end
    end
    
    -- 크리티컬 확률
    local critChance = safeCall(item, "getCriticalChance")
    if critChance and type(critChance) == "number" and critChance > 0 then
        table.insert(parts, string.format("%s: %.0f%%", getLabel("Iris_Detail_Critical"), critChance))
    end
    
    -- 내구도
    local maxCondition = safeCall(item, "getConditionMax")
    if maxCondition and type(maxCondition) == "number" and maxCondition > 0 then
        table.insert(parts, string.format("%s: %.0f", getLabel("Iris_Detail_Durability"), maxCondition))
    end
    
    if #parts == 0 then
        return nil
    end
    return table.concat(parts, " | ")
end

--- E) 연결 시스템 섹션 렌더링
function IrisWikiSections.renderConnectionSection(item)
    ensureDeps()
    
    if not IrisAPI then
        return nil
    end
    
    local parts = {}
    
    -- Recipe
    local recipeOk, recipeInfo = pcall(function() return IrisAPI.getRecipeConnectionsForItem(item) end)
    if recipeOk and recipeInfo and #recipeInfo > 0 then
        table.insert(parts, getLabel("Iris_Detail_Recipe") .. ": " .. #recipeInfo)
    end
    
    -- Moveables
    local moveOk, moveablesInfo = pcall(function() return IrisAPI.getMoveablesInfoForItem(item) end)
    if moveOk and moveablesInfo then
        if moveablesInfo.itemId_registered then
            table.insert(parts, getLabel("Iris_Detail_Furniture") .. ": O")
        end
    end
    
    -- Fixing
    local fixOk, fixingInfo = pcall(function() return IrisAPI.getFixingInfoForItem(item) end)
    if fixOk and fixingInfo and fixingInfo.isFixer then
        table.insert(parts, getLabel("Iris_Detail_Fixer") .. ": O")
    end
    
    if #parts == 0 then
        return nil
    end
    return table.concat(parts, " | ")
end

--- F) 기타 속성 섹션 렌더링
function IrisWikiSections.renderMiscSection(item)
    local parts = {}
    
    -- 용량 (컨테이너)
    local capacity = safeCall(item, "getCapacity")
    if capacity and type(capacity) == "number" and capacity > 0 then
        table.insert(parts, string.format("%s: %.0f", getLabel("Iris_Detail_Capacity"), capacity))
    end
    
    -- 광원 강도
    local lightStr = safeCall(item, "getLightStrength")
    if lightStr and type(lightStr) == "number" and lightStr > 0 then
        table.insert(parts, string.format("%s: %.1f", getLabel("Iris_Detail_Light"), lightStr))
    end
    
    -- 방수 여부
    local isWaterproof = safeCall(item, "isWaterproof")
    if isWaterproof then
        table.insert(parts, getLabel("Iris_Detail_Waterproof"))
    end
    
    -- 보온 효과
    local insulation = safeCall(item, "getInsulation")
    if insulation and type(insulation) == "number" and insulation > 0 then
        table.insert(parts, string.format("%s: %.1f", getLabel("Iris_Detail_Insulation"), insulation))
    end
    
    if #parts == 0 then
        return nil
    end
    return table.concat(parts, " | ")
end

--- 모든 섹션을 배열로 반환 (nil이 아닌 것만)
function IrisWikiSections.getAllSections(item)
    local sections = {}
    
    local basicInfo = IrisWikiSections.renderBasicInfoSection(item)
    if basicInfo then table.insert(sections, basicInfo) end
    
    local tags = IrisWikiSections.renderTagsSection(item)
    if tags then table.insert(sections, tags) end
    
    local food = IrisWikiSections.renderFoodSection(item)
    if food then table.insert(sections, food) end
    
    local weapon = IrisWikiSections.renderWeaponSection(item)
    if weapon then table.insert(sections, weapon) end
    
    local connection = IrisWikiSections.renderConnectionSection(item)
    if connection then table.insert(sections, connection) end
    
    local misc = IrisWikiSections.renderMiscSection(item)
    if misc then table.insert(sections, misc) end
    
    return sections
end

-- 이전 호환성을 위한 레거시 함수
function IrisWikiSections.renderReasonSection(item)
    return nil
end

function IrisWikiSections.renderFieldsSection(item)
    return IrisWikiSections.renderMiscSection(item)
end

return IrisWikiSections
