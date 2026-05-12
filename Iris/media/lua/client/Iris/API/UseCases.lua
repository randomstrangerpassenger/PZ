--[[
    UseCases.lua - Iris use-case and capability facade

    Core fact facade with sealed display-payload passthrough. This module reads
    frozen build artifacts and does not generate new runtime prose.
]]

local UseCases = {}

local Array = require("Iris/Util/Array")
local StaticData = require("Iris/API/StaticData")

local function emptyUseCaseLines()
    return { lines = {}, debug_lines = {} }
end

--- UseCase description lines 반환 (빌드에서 결정된 데이터 그대로)
--- API 반환 형태 정규화: 항상 {lines={}, debug_lines={}} 반환. nil 반환 금지.
--- @param fullType string 아이템 FullType
--- @return table {lines={...}, debug_lines={...}}
function UseCases.getUseCaseLines(fullType)
    if not fullType then return emptyUseCaseLines() end

    local useCaseDescriptions = StaticData.get("useCaseDescriptions")
    if not useCaseDescriptions then return emptyUseCaseLines() end

    local entry = useCaseDescriptions[fullType]
    if not entry then return emptyUseCaseLines() end

    return {
        lines = entry.lines or {},
        debug_lines = entry.debug_lines or {},
    }
end

--- Context Outcome 조회 (v1.3)
--- @param fullType string
--- @return table outcome 배열
function UseCases.getOutcomes(fullType)
    if not fullType then return {} end

    local contextOutcomes = StaticData.get("contextOutcomes")
    if not contextOutcomes then return {} end

    return contextOutcomes[fullType] or {}
end

--- 특정 Context Outcome 존재 확인 (v1.3)
--- @param fullType string
--- @param outcome string
--- @return boolean 존재 여부
function UseCases.hasOutcome(fullType, outcome)
    return Array.contains(UseCases.getOutcomes(fullType), outcome)
end

--- Right-Click Capability 조회
--- @param fullType string
--- @return table capability 배열
function UseCases.getCapabilities(fullType)
    if not fullType then return {} end

    local capabilities = StaticData.get("capabilities")
    if not capabilities then return {} end

    return capabilities[fullType] or {}
end

--- 특정 Capability 존재 확인
--- @param fullType string
--- @param capability string
--- @return boolean 존재 여부
function UseCases.hasCapability(fullType, capability)
    return Array.contains(UseCases.getCapabilities(fullType), capability)
end

return UseCases
