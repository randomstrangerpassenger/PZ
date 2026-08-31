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

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local DetailViewModel = require("Iris/UI/Detail/IrisItemDetailViewModel")
local Presentation = require("Iris/UI/Detail/IrisItemDetailPresentation")

-- validation anchor: require, "Iris/Data/layer3_renderer"

local function getRuntimeLangKey()
    return TranslationResolver.getLangKey("EN")
end

local function getLabel(key)
    return TranslationResolver.get(key, key:gsub("Iris_Detail_", ""))
end

--- A) 기본 정보 섹션 렌더링
function IrisWikiSections.renderBasicInfoSection(item)
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local parts = {}
    
    -- 무게
    local weight = model.weight
    if weight and type(weight) == "number" then
        table.insert(parts, string.format("%s: %.1f", getLabel("Iris_Detail_Weight"), weight))
    end
    
    -- 타입
    local itemType = model.itemType
    if itemType then
        table.insert(parts, getLabel("Iris_Detail_Type") .. ": " .. tostring(itemType))
    end
    
    -- 모듈 (이름만 추출)
    if model.moduleName then
        table.insert(parts, getLabel("Iris_Detail_Module") .. ": " .. model.moduleName)
    end
    
    if #parts == 0 then
        return nil
    end
    return table.concat(parts, " | ")
end

--- B) 태그 섹션 렌더링
function IrisWikiSections.renderTagsSection(item)
    local model = DetailViewModel.ensure(item)
    if not model or DetailViewModel.arrayLength(model.tags) == 0 then return nil end
    return getLabel("Iris_Detail_Tags") .. ": " .. table.concat(DetailViewModel.copyArray(model.tags), ", ")
end

function IrisWikiSections.renderLayer3Section(item)
    local model = DetailViewModel.ensure(item)
    return model and model.layer3.display or nil
end

-- Only skills whose reading bonus is admitted for this presentation. The
-- legacy Blacksmith declaration alone does not settle its active B41 behavior.
local SKILL_LABELS = {
    Carpentry = "Iris_Detail_Skill_Carpentry",
    Cooking = "Iris_Detail_Skill_Cooking",
    Farming = "Iris_Detail_Skill_Farming",
    Fishing = "Iris_Detail_Skill_Fishing",
    Trapping = "Iris_Detail_Skill_Trapping",
    MetalWelding = "Iris_Detail_Skill_MetalWelding",
    FirstAid = "Iris_Detail_Skill_FirstAid",
    Electricity = "Iris_Detail_Skill_Electricity",
    Foraging = "Iris_Detail_Skill_Foraging",
    Mechanics = "Iris_Detail_Skill_Mechanics",
    Tailoring = "Iris_Detail_Skill_Tailoring",
}

-- Literature values come from FactReader through the model. These are the
-- levels being trained, not the player's current level: ISReadABook compares
-- its bounds with current perk level + 1 when updating the reading multiplier.
function IrisWikiSections.renderLiteratureSection(item)
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local literature = model.literature
    local skillLabel = literature and SKILL_LABELS[literature.skillTrained]
    if not skillLabel then return nil end

    local parts = {
        getLabel("Iris_Detail_TrainedSkill") .. ": " .. getLabel(skillLabel),
    }
    local level = literature.level
    local count = literature.levelCount
    if type(level) == "number" and type(count) == "number"
        and level >= 1 and count >= 1
        and level % 1 == 0 and count % 1 == 0 then
        table.insert(parts, string.format("%s: %d–%d",
            getLabel("Iris_Detail_TrainingLevels"), level, level + count - 1))
        table.insert(parts, string.format("%s: %d–%d",
            getLabel("Iris_Detail_ReadingLevels"), level - 1, level + count - 2))
        table.insert(parts, getLabel("Iris_Detail_ReadingLiteracyCondition"))
        table.insert(parts, getLabel("Iris_Detail_ReadingProgress"))
    end
    return table.concat(parts, "\n")
end

--- C) 음식/소모품 속성 섹션 렌더링
function IrisWikiSections.renderFoodSection(item)
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local food = model.food
    local parts = {}
    
    -- 배고픔 변화
    local hunger = food.hunger
    if hunger and type(hunger) == "number" and hunger ~= 0 then
        table.insert(parts, getLabel("Iris_Detail_Hunger") .. ": " ..
            Presentation.formatSigned(hunger, "percent_scaled"))
    end
    
    -- 갈증 변화
    local thirst = food.thirst
    if thirst and type(thirst) == "number" and thirst ~= 0 then
        table.insert(parts, getLabel("Iris_Detail_Thirst") .. ": " ..
            Presentation.formatSigned(thirst, "percent_scaled"))
    end
    
    -- 스트레스 변화
    local stress = food.stress
    if stress and type(stress) == "number" and stress ~= 0 then
        table.insert(parts, getLabel("Iris_Detail_Stress") .. ": " ..
            Presentation.formatSigned(stress, "percent_scaled"))
    end
    
    -- 권태감 변화
    local boredom = food.boredom
    if boredom and type(boredom) == "number" and boredom ~= 0 then
        table.insert(parts, getLabel("Iris_Detail_Boredom") .. ": " ..
            Presentation.formatSigned(boredom, "percent_scaled"))
    end
    
    -- 칼로리
    local calories = food.calories
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
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local weapon = model.weapon
    local parts = {}
    
    -- 최소/최대 데미지
    local minDmg = weapon.minDamage
    local maxDmg = weapon.maxDamage
    if minDmg and maxDmg and type(minDmg) == "number" and type(maxDmg) == "number" then
        if minDmg > 0 or maxDmg > 0 then
            table.insert(parts, string.format("%s: %.1f~%.1f", getLabel("Iris_Detail_Damage"), minDmg, maxDmg))
        end
    end
    
    -- 사거리
    local minRange = weapon.minRange
    local maxRange = weapon.maxRange
    if minRange and maxRange and type(minRange) == "number" and type(maxRange) == "number" then
        if maxRange > 0 then
            table.insert(parts, string.format("%s: %.1f~%.1f", getLabel("Iris_Detail_Range"), minRange, maxRange))
        end
    end
    
    -- 크리티컬 확률
    local critChance = weapon.criticalChance
    if critChance and type(critChance) == "number" and critChance > 0 then
        table.insert(parts, string.format("%s: %.0f%%", getLabel("Iris_Detail_Critical"), critChance))
    end
    
    -- 내구도
    local maxCondition = weapon.conditionMax
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
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local parts = {}
    
    -- Recipe
    local recipeInfo = model.connections.recipes
    local recipeCount = DetailViewModel.arrayLength(recipeInfo)
    if recipeCount > 0 then
        table.insert(parts, getLabel("Iris_Detail_Recipe") .. ": " .. recipeCount)
    end
    
    -- Moveables
    local moveablesInfo = model.connections.moveables
    if moveablesInfo then
        if moveablesInfo.itemId_registered then
            table.insert(parts, getLabel("Iris_Detail_Furniture") .. ": O")
        end
    end
    
    -- Fixing
    local fixingInfo = model.connections.fixing
    if fixingInfo and fixingInfo.isFixer then
        table.insert(parts, getLabel("Iris_Detail_Fixer") .. ": O")
    end
    
    if #parts == 0 then
        return nil
    end
    return table.concat(parts, " | ")
end

--- F) 기타 속성 섹션 렌더링
function IrisWikiSections.renderMiscSection(item)
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local moveable = model.moveable
    local parts = {}
    
    -- 용량 (컨테이너)
    local capacity = moveable.capacity
    if capacity and type(capacity) == "number" and capacity > 0 then
        table.insert(parts, string.format("%s: %.0f", getLabel("Iris_Detail_Capacity"), capacity))
    end
    
    -- 광원 강도
    local lightStr = moveable.lightStrength
    if lightStr and type(lightStr) == "number" and lightStr > 0 then
        table.insert(parts, string.format("%s: %.1f", getLabel("Iris_Detail_Light"), lightStr))
    end
    
    -- 방수 여부
    local isWaterproof = moveable.waterproof
    if isWaterproof then
        table.insert(parts, getLabel("Iris_Detail_Waterproof"))
    end
    
    -- 보온 효과
    local insulation = moveable.insulation
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
    local model = DetailViewModel.ensure(item)
    if not model then return {} end
    local sections = {}
    
    local basicInfo = IrisWikiSections.renderBasicInfoSection(model)
    if basicInfo then table.insert(sections, basicInfo) end
    
    local tags = IrisWikiSections.renderTagsSection(model)
    if tags then table.insert(sections, tags) end
    
    local layer3 = IrisWikiSections.renderLayer3Section(model)
    if layer3 then table.insert(sections, layer3) end
    
    local food = IrisWikiSections.renderFoodSection(model)
    if food then table.insert(sections, food) end
    
    local weapon = IrisWikiSections.renderWeaponSection(model)
    if weapon then table.insert(sections, weapon) end

    local literature = IrisWikiSections.renderLiteratureSection(model)
    if literature then table.insert(sections, literature) end
    
    local connection = IrisWikiSections.renderConnectionSection(model)
    if connection then table.insert(sections, connection) end
    
    local misc = IrisWikiSections.renderMiscSection(model)
    if misc then table.insert(sections, misc) end
    
    return sections
end

function IrisWikiSections.getSemanticSnapshot(item)
    return Presentation.semanticSnapshot(DetailViewModel.ensure(item))
end

-- 이전 호환성을 위한 레거시 함수
function IrisWikiSections.renderReasonSection(item)
    return nil
end

function IrisWikiSections.renderFieldsSection(item)
    return IrisWikiSections.renderMiscSection(item)
end

--- ================================================================
--- 새 순서 지원 함수 (v1.1)
--- [1] 기본 정보 → [2] 소분류 설명 → [3] 레시피 → [4] 메타 정보
--- ================================================================

--- [1] 기본 정보 섹션 (즉시 판단용)
--- ⚠️ 스코프 고정 (비대화 방지):
---   ✅ 포함: 무게, 타입, 데미지, 내구도, 갈증/허기 변화량
---   ❌ 제외: 내부 플래그, 조건부 효과 문장, 레시피/연결 정보
function IrisWikiSections.renderCoreInfoSection(item)
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local parts = {}
    
    -- 무게
    local weight = model.weight
    if weight and type(weight) == "number" then
        table.insert(parts, string.format("%s: %.1f", getLabel("Iris_Detail_Weight"), weight))
    end
    
    -- 타입
    local itemType = model.itemType
    if itemType then
        table.insert(parts, getLabel("Iris_Detail_Type") .. ": " .. tostring(itemType))
    end
    
    -- === 핵심 수치 (아이템 종류에 따라) ===
    
    -- 데미지 (무기류)
    local minDmg = model.weapon.minDamage
    local maxDmg = model.weapon.maxDamage
    if minDmg and maxDmg and type(minDmg) == "number" and type(maxDmg) == "number" then
        if minDmg > 0 or maxDmg > 0 then
            table.insert(parts, string.format("%s: %.1f~%.1f", getLabel("Iris_Detail_Damage"), minDmg, maxDmg))
        end
    end
    
    -- 내구도
    local maxCondition = model.weapon.conditionMax
    if maxCondition and type(maxCondition) == "number" and maxCondition > 0 then
        table.insert(parts, string.format("%s: %.0f", getLabel("Iris_Detail_Durability"), maxCondition))
    end
    
    -- 갈증 변화 (음식류) - PZ에서 이미 정수값으로 저장
    local thirst = model.food.thirst
    if thirst and type(thirst) == "number" and thirst ~= 0 then
        table.insert(parts, getLabel("Iris_Detail_Thirst") .. ": " ..
            Presentation.formatSigned(thirst, "percent_scaled"))
    end
    
    -- 허기 변화 (음식류) - PZ에서 이미 정수값으로 저장
    local hunger = model.food.hunger
    if hunger and type(hunger) == "number" and hunger ~= 0 then
        table.insert(parts, getLabel("Iris_Detail_Hunger") .. ": " ..
            Presentation.formatSigned(hunger, "percent_scaled"))
    end
    
    if #parts == 0 then
        return nil
    end
    return table.concat(parts, " | ")
end

--- [3] 레시피 정보 섹션
--- 레시피 0개면 nil 반환 (섹션 자체 미출력)
function IrisWikiSections.renderRecipeInfoSection(item)
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local recipeInfo = model.connections.recipes
    local recipeCount = DetailViewModel.arrayLength(recipeInfo)
    if recipeCount > 0 then
        return getLabel("Iris_Detail_Recipe") .. ": " .. recipeCount
    end
    
    -- 레시피 0개면 nil 반환 (빈 줄 표시 금지)
    return nil
end

--- [4] 메타 정보 섹션 (분류 ID, 모듈)
--- 시각적 구분선 포함
function IrisWikiSections.renderMetaInfoSection(item)
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local lines = {}
    
    -- 시각적 구분선
    table.insert(lines, "────────────────────")
    
    -- 분류 ID (태그)
    if DetailViewModel.arrayLength(model.tags) > 0 then
        table.insert(lines, getLabel("Iris_Detail_ClassificationID") .. ": " .. table.concat(DetailViewModel.copyArray(model.tags), ", "))
    end
    
    -- 모듈
    if model.moduleName then
        table.insert(lines, getLabel("Iris_Detail_Module") .. ": " .. model.moduleName)
    end
    
    -- 구분선만 있으면 nil 반환
    if #lines <= 1 then
        return nil
    end
    
    return table.concat(lines, "\n")
end

-- ============================================
-- UseCase Block 섹션 (빌드 산출물 표시 전용)
-- ============================================

local UseCaseLineRenderer = require("Iris/UI/Wiki/IrisWikiUseCaseLineRenderer")
local IrisConfig = nil

local function ensureUseCaseDeps()
    if not IrisConfig then
        local ok, result = safeRequire("Iris/IrisConfig")
        if ok then IrisConfig = result end
    end
end

--- UseCase line 구조체 → 표시 문자열 치환 (구현은 IrisWikiUseCaseLineRenderer로 이관)
local function renderUseCaseLine(lineObj)
    return UseCaseLineRenderer.renderLine(lineObj)
end


--- UseCase Block 섹션 렌더링
--- nil 책임 경계: API=빈 배열 정규화, UI 섹션=#lines==0→nil(미출력)
function IrisWikiSections.renderUseCaseSection(item)
    ensureUseCaseDeps()
    local model = DetailViewModel.ensure(item)
    if not model then return nil end
    local data = model.useCases
    local lines = DetailViewModel.copyArray(data.lines)
    local debug_lines = DetailViewModel.copyArray(data.debug_lines)

    if #lines == 0 and #debug_lines == 0 then
        return nil
    end

    local parts = {}
    table.insert(parts, "--- UseCase ---")

    -- main lines (순서 그대로, 재정렬 금지)
    for _, lineObj in ipairs(lines) do
        table.insert(parts, renderUseCaseLine(lineObj))
    end

    -- debug_lines: SHOW_DEBUG_USECASES일 때만 (DEBUG 혼용 금지)
    if IrisConfig and IrisConfig.SHOW_DEBUG_USECASES and #debug_lines > 0 then
        table.insert(parts, "  (debug)")
        for _, lineObj in ipairs(debug_lines) do
            table.insert(parts, "  " .. renderUseCaseLine(lineObj))
        end
    end

    -- lines가 비어있고 debug만 있는데 플래그 OFF면 미출력
    if #parts <= 1 then
        return nil
    end

    return table.concat(parts, "\n")
end

return IrisWikiSections
