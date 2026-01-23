--[[
    IrisWikiSections.lua - 위키 패널 섹션 렌더링
    
    필수 섹션:
    A) 태그 목록 (복수 태그) — 알파벳 정렬
    B) 근거 — REASON_LABELS 정적 사전으로 명사구 출력. 해석/평가 금지.
    C) 연결 시스템 (Recipe/Moveables/Fixing)
    D) 상태 필드 (표시만, 비교/평가 금지)
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

--- A) 태그 섹션 렌더링
function IrisWikiSections.renderTagsSection(item)
    ensureDeps()
    
    if not IrisAPI or not IrisAPI.getTagsForItem then
        return "[태그] (API 로드 실패)"
    end
    
    local ok, tags = pcall(function() return IrisAPI.getTagsForItem(item) end)
    if not ok or not tags then
        return "[태그] (조회 실패)"
    end
    
    if not IrisRuleExecutor or not IrisRuleExecutor.setToSortedArray then
        return "[태그] (정렬 실패)"
    end
    
    local sorted = IrisRuleExecutor.setToSortedArray(tags)
    
    if #sorted == 0 then
        return "[태그] 없음"
    end
    return "[태그] " .. table.concat(sorted, ", ")
end

--- B) 근거 섹션 렌더링
function IrisWikiSections.renderReasonSection(item)
    return "[근거] (태그 매칭 규칙 참조)"
end

--- C) 연결 시스템 섹션 렌더링
function IrisWikiSections.renderConnectionSection(item)
    ensureDeps()
    
    if not IrisAPI then
        return "[연결] (API 로드 실패)"
    end
    
    local parts = {}
    
    -- Recipe
    local recipeOk, recipeInfo = pcall(function() return IrisAPI.getRecipeConnectionsForItem(item) end)
    if recipeOk and recipeInfo and #recipeInfo > 0 then
        table.insert(parts, "Recipe: 있음")
    else
        table.insert(parts, "Recipe: 없음")
    end
    
    -- Moveables
    local moveOk, moveablesInfo = pcall(function() return IrisAPI.getMoveablesInfoForItem(item) end)
    if moveOk and moveablesInfo then
        if moveablesInfo.itemId_registered then
            table.insert(parts, "Moveables: 등록됨")
        elseif moveablesInfo.moveablesTag then
            table.insert(parts, "Moveables: " .. moveablesInfo.moveablesTag)
        else
            table.insert(parts, "Moveables: 없음")
        end
    else
        table.insert(parts, "Moveables: 없음")
    end
    
    -- Fixing
    local fixOk, fixingInfo = pcall(function() return IrisAPI.getFixingInfoForItem(item) end)
    if fixOk and fixingInfo and fixingInfo.isFixer then
        table.insert(parts, "Fixing: Fixer")
    else
        table.insert(parts, "Fixing: 없음")
    end
    
    return "[연결] " .. table.concat(parts, " | ")
end

--- D) 상태 필드 섹션 렌더링 (안전하게 접근)
function IrisWikiSections.renderFieldsSection(item)
    -- ScriptItem 가져오기
    local scriptItem = nil
    if item and item.getScriptItem then
        local ok, result = pcall(function() return item:getScriptItem() end)
        if ok then scriptItem = result end
    end
    
    if not scriptItem then
        return "[필드] 정보 없음"
    end
    
    local fields = {}
    
    -- 안전하게 필드 접근 (각 메서드가 존재하지 않을 수 있음)
    local function tryGetField(methodName)
        if scriptItem[methodName] then
            local ok, result = pcall(function() return scriptItem[methodName](scriptItem) end)
            if ok and result ~= nil then
                return result
            end
        end
        return nil
    end
    
    -- 각 필드 체크 (메서드가 없어도 에러 없음)
    if tryGetField("getHungerChange") then
        table.insert(fields, "HungerChange: 존재")
    end
    
    if tryGetField("getThirstChange") then
        table.insert(fields, "ThirstChange: 존재")
    end
    
    if tryGetField("getStressChange") then
        table.insert(fields, "StressChange: 존재")
    end
    
    -- getLightStrength는 존재하지 않을 수 있음 - 안전하게 처리
    local lightVal = tryGetField("getLightStrength")
    if lightVal and type(lightVal) == "number" and lightVal > 0 then
        table.insert(fields, "LightStrength: 존재")
    end
    
    if #fields == 0 then
        return "[필드] 특수 필드 없음"
    end
    return "[필드] " .. table.concat(fields, ", ")
end

return IrisWikiSections
