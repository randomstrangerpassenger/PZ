--[[
    IrisAPI.lua - Iris public query API compatibility facade

    Iris is a 100% Lua wiki-style mod. This facade keeps the existing public
    Lua API surface while delegating ownership to smaller runtime facades:

    - IrisAPI.Tags: frozen classification tags
    - IrisAPI.Index: frozen recipe/moveables/fixing indexes
    - IrisAPI.Description: Layer 3 description generation
    - IrisAPI.UseCases: frozen use-case/outcome/capability artifacts
]]

local IrisAPI = {}

IrisAPI.Tags = require("Iris/API/Tags")
IrisAPI.Index = require("Iris/API/Index")
IrisAPI.Description = require("Iris/API/Description")
IrisAPI.UseCases = require("Iris/API/UseCases")

--- 아이템의 분류 태그 조회 (O(1) 정적 조회)
--- @param item InventoryItem|ScriptItem
--- @return table 태그 Set 또는 빈 테이블
function IrisAPI.getTagsForItem(item)
    return IrisAPI.Tags.getTagsForItem(item)
end

--- fullType으로 태그 직접 조회
--- @param fullType string
--- @return table 태그 배열 또는 빈 테이블
function IrisAPI.getTags(fullType)
    return IrisAPI.Tags.getTags(fullType)
end

--- 아이템이 특정 태그를 가지고 있는지 확인
--- @param fullType string
--- @param tag string
--- @return boolean
function IrisAPI.hasTag(fullType, tag)
    return IrisAPI.Tags.hasTag(fullType, tag)
end

--- 아이템이 분류되었는지 확인
--- @param fullType string
--- @return boolean
function IrisAPI.isClassified(fullType)
    return IrisAPI.Tags.isClassified(fullType)
end

--- 아이템의 Recipe 연결 정보 반환
--- @param item InventoryItem
--- @return table {{role, category}, ...} 배열
function IrisAPI.getRecipeConnectionsForItem(item)
    return IrisAPI.Index.getRecipeConnectionsForItem(item)
end

--- 아이템의 Moveables 연결 정보 반환
--- @param item InventoryItem
--- @return table {itemId_registered, moveablesTag}
function IrisAPI.getMoveablesInfoForItem(item)
    return IrisAPI.Index.getMoveablesInfoForItem(item)
end

--- 아이템의 Fixing 연결 정보 반환
--- @param item InventoryItem
--- @return table {isFixer}
function IrisAPI.getFixingInfoForItem(item)
    return IrisAPI.Index.getFixingInfoForItem(item)
end

--- 아이템의 설명 블록 배열 반환
--- @param fullType string 아이템 FullType
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return table 블록 문자열 배열
function IrisAPI.getDescriptionBlocks(fullType, primarySubcategory)
    return IrisAPI.Description.getDescriptionBlocks(fullType, primarySubcategory)
end

--- 아이템의 설명 문자열 반환 (소분류 기반)
--- @param fullType string 아이템 FullType
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return string 설명 문자열 또는 빈 문자열
function IrisAPI.getDescription(fullType, primarySubcategory)
    return IrisAPI.Description.getDescription(fullType, primarySubcategory)
end

--- InventoryItem에서 설명 반환 (편의 함수)
--- @param item InventoryItem|ScriptItem
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return string 전체 설명 문자열
function IrisAPI.getDescriptionForItem(item, primarySubcategory)
    return IrisAPI.Description.getDescriptionForItem(item, primarySubcategory)
end

--- UseCase description lines 반환 (빌드에서 결정된 데이터 그대로)
--- @param fullType string 아이템 FullType
--- @return table {lines={...}, debug_lines={...}}
function IrisAPI.getUseCaseLines(fullType)
    return IrisAPI.UseCases.getUseCaseLines(fullType)
end

--- Context Outcome 조회 (v1.3)
--- @param fullType string
--- @return table outcome 배열
function IrisAPI.getOutcomes(fullType)
    return IrisAPI.UseCases.getOutcomes(fullType)
end

--- 특정 Context Outcome 존재 확인 (v1.3)
--- @param fullType string
--- @param outcome string
--- @return boolean 존재 여부
function IrisAPI.hasOutcome(fullType, outcome)
    return IrisAPI.UseCases.hasOutcome(fullType, outcome)
end

--- Right-Click Capability 조회
--- @param fullType string
--- @return table capability 배열
function IrisAPI.getCapabilities(fullType)
    return IrisAPI.UseCases.getCapabilities(fullType)
end

--- 특정 Capability 존재 확인
--- @param fullType string
--- @param capability string
--- @return boolean 존재 여부
function IrisAPI.hasCapability(fullType, capability)
    return IrisAPI.UseCases.hasCapability(fullType, capability)
end

return IrisAPI

