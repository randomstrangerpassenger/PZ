--[[
    UseCases.lua - Iris use-case and capability facade

    Core fact facade with sealed display-payload passthrough. This module reads
    frozen build artifacts and does not generate new runtime prose.
]]

local UseCases = {}

local Array = require("Iris/Util/Array")
local StaticData = require("Iris/API/StaticData")
local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local RuntimeLookupDiagnostics = require("Iris/Data/IrisRuntimeLookupDiagnostics")
local descriptionLookup = nil
local descriptionLookupAttempted = false
local AUTHORITATIVE_NEGATIVE = { lookup_miss = true }

local function getDescriptionLookup()
    if not descriptionLookupAttempted then
        descriptionLookupAttempted = true
        local ok, loaded = safeRequire("Iris/Data/IrisUseCaseDescriptionsLookup")
        if ok and loaded then descriptionLookup = loaded end
    end
    return descriptionLookup
end

local function emptyUseCaseLines()
    return { lines = {}, debug_lines = {} }
end

local function rawArray(datasetName, fullType)
    if not fullType then return nil end
    local dataset = StaticData.get(datasetName)
    if not dataset then return nil end
    return dataset[fullType]
end

--- UseCase description lines 반환 (빌드에서 결정된 데이터 그대로)
--- API 반환 형태 정규화: 항상 {lines={}, debug_lines={}} 반환. nil 반환 금지.
--- @param fullType string 아이템 FullType
--- @return table {lines={...}, debug_lines={...}}
function UseCases.getUseCaseLines(fullType)
    if not fullType then return emptyUseCaseLines() end

    local entry = nil
    local lookup = getDescriptionLookup()
    if lookup and lookup.get then
        local loaded, reason = lookup.get(fullType)
        if reason == nil then
            entry = loaded
        elseif AUTHORITATIVE_NEGATIVE[reason] then
            return emptyUseCaseLines()
        end
    else
        RuntimeLookupDiagnostics.recordFallback("usecase", "router_unavailable")
    end
    if not entry then entry = rawArray("useCaseDescriptions", fullType) end
    if not entry then return emptyUseCaseLines() end

    return {
        lines = Array.copy(entry.lines),
        debug_lines = Array.copy(entry.debug_lines),
    }
end

-- Internal runtime consumers use these focused adapters; public facade shapes above remain unchanged.
function UseCases._getDescriptionEntry(fullType)
    if not fullType then return nil end
    local entry = nil
    local lookup = getDescriptionLookup()
    if lookup and lookup.get then
        local loaded, reason = lookup.get(fullType)
        if reason == nil then
            entry = loaded
        elseif AUTHORITATIVE_NEGATIVE[reason] then
            return nil
        end
    else
        RuntimeLookupDiagnostics.recordFallback("usecase", "router_unavailable")
    end
    if not entry then entry = rawArray("useCaseDescriptions", fullType) end
    if not entry then return nil end
    return {
        lines = Array.copy(entry.lines),
        exclusion_lines = Array.copy(entry.exclusion_lines),
        debug_lines = Array.copy(entry.debug_lines),
    }
end

function UseCases._getRequirements(recipeName)
    local lookup = getDescriptionLookup()
    if lookup and lookup.getRequirements then
        local loaded, reason = lookup.getRequirements(recipeName)
        if reason == nil then return Array.copy(loaded) end
        if AUTHORITATIVE_NEGATIVE[reason] then return {} end
    else
        RuntimeLookupDiagnostics.recordFallback("usecase_requirements", "router_unavailable")
    end
    local facade = StaticData.get("useCaseDescriptions")
    return Array.copy(facade and facade._requirementsLookup and facade._requirementsLookup[recipeName])
end

function UseCases._getUseCaseLineCount(fullType)
    local lookup = getDescriptionLookup()
    if lookup and lookup.getLineCount then
        local count, reason = lookup.getLineCount(fullType)
        if reason == nil then return count end
        if AUTHORITATIVE_NEGATIVE[reason] then return 0 end
    else
        RuntimeLookupDiagnostics.recordFallback("usecase_line_count", "router_unavailable")
    end
    local entry = rawArray("useCaseDescriptions", fullType)
    return entry and entry.lines and #entry.lines or 0
end

--- Context Outcome 조회 (v1.3)
--- @param fullType string
--- @return table outcome 배열
function UseCases.getOutcomes(fullType)
    return Array.copy(rawArray("contextOutcomes", fullType))
end

--- 특정 Context Outcome 존재 확인 (v1.3)
--- @param fullType string
--- @param outcome string
--- @return boolean 존재 여부
function UseCases.hasOutcome(fullType, outcome)
    return Array.contains(rawArray("contextOutcomes", fullType), outcome)
end

--- Right-Click Capability 조회
--- @param fullType string
--- @return table capability 배열
function UseCases.getCapabilities(fullType)
    return Array.copy(rawArray("capabilities", fullType))
end

--- 특정 Capability 존재 확인
--- @param fullType string
--- @param capability string
--- @return boolean 존재 여부
function UseCases.hasCapability(fullType, capability)
    return Array.contains(rawArray("capabilities", fullType), capability)
end

return UseCases
