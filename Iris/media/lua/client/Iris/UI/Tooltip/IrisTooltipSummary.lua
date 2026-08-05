--[[
    IrisTooltipSummary.lua

    FullType keyed tooltip summary built from precompiled Iris data tables.
]]

local IrisTooltipSummary = {}

local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local RuntimeLookupDiagnostics = require("Iris/Data/IrisRuntimeLookupDiagnostics")

local IrisClassifications = nil
local IrisRecipeIndex = nil
local IrisMoveablesIndex = nil
local IrisFixingIndex = nil
local IrisUseCaseDescriptions = nil
local IrisUseCaseDescriptionsLookup = nil
local loaded = false
local summaryByFullType = {}

local function copyArray(values)
    local result = {}
    for index, value in ipairs(values or {}) do
        result[index] = value
    end
    return result
end

local function copySummary(summary)
    return {
        fullType = summary.fullType,
        tags = copyArray(summary.tags),
        connections = copyArray(summary.connections),
        useCaseCount = summary.useCaseCount,
        revision = summary.revision,
    }
end

local function ensureData()
    if loaded then
        return
    end

    local ok, result = safeRequire("Iris/Data/IrisClassifications")
    if ok then IrisClassifications = result end

    ok, result = safeRequire("Iris/Data/IrisRecipeIndex")
    if ok then IrisRecipeIndex = result end

    ok, result = safeRequire("Iris/Data/IrisMoveablesIndex")
    if ok then IrisMoveablesIndex = result end

    ok, result = safeRequire("Iris/Data/IrisFixingIndex")
    if ok then IrisFixingIndex = result end

    ok, result = safeRequire("Iris/Data/IrisUseCaseDescriptionsLookup")
    if ok then IrisUseCaseDescriptionsLookup = result end

    loaded = true
end

local function copySortedTags(fullType)
    local tags = {}
    local sourceTags = IrisClassifications and IrisClassifications[fullType] or nil
    if sourceTags then
        for _, tag in ipairs(sourceTags) do
            table.insert(tags, tag)
        end
        table.sort(tags)
    end
    return tags
end

local function collectConnections(fullType)
    local connections = {}

    if IrisRecipeIndex and IrisRecipeIndex.getRoles then
        local ok, roles = ProtectedCall.data(function() return IrisRecipeIndex.getRoles(fullType) end)
        if ok and roles and #roles > 0 then
            table.insert(connections, "Recipe")
        end
    end

    local hasMoveable = false
    if IrisMoveablesIndex then
        if IrisMoveablesIndex.isItemIdRegistered then
            local ok, registered = ProtectedCall.data(function() return IrisMoveablesIndex.isItemIdRegistered(fullType) end)
            hasMoveable = hasMoveable or (ok and registered == true)
        end
        if IrisMoveablesIndex.getMoveablesTag then
            local ok, tag = ProtectedCall.data(function() return IrisMoveablesIndex.getMoveablesTag(fullType) end)
            hasMoveable = hasMoveable or (ok and tag ~= nil)
        end
    end
    if hasMoveable then
        table.insert(connections, "Moveables")
    end

    if IrisFixingIndex and IrisFixingIndex.isFixer then
        local ok, isFixer = ProtectedCall.data(function() return IrisFixingIndex.isFixer(fullType) end)
        if ok and isFixer == true then
            table.insert(connections, "Fixing")
        end
    end

    return connections
end

local function countUseCaseLines(fullType)
    if IrisUseCaseDescriptionsLookup and IrisUseCaseDescriptionsLookup.getLineCount then
        local count, reason = IrisUseCaseDescriptionsLookup.getLineCount(fullType)
        if reason == nil then return count end
    else
        RuntimeLookupDiagnostics.recordFallback("usecase_tooltip_line_count", "router_unavailable")
    end
    if not IrisUseCaseDescriptions then
        local ok, result = safeRequire("Iris/Data/IrisUseCaseDescriptions")
        if ok then IrisUseCaseDescriptions = result end
    end
    local entry = IrisUseCaseDescriptions and IrisUseCaseDescriptions[fullType] or nil
    if not entry or not entry.lines then
        return 0
    end
    return #entry.lines
end

function IrisTooltipSummary.get(fullType)
    if not fullType then
        return nil
    end

    local cached = summaryByFullType[fullType]
    if cached then
        return copySummary(cached)
    end

    ensureData()

    local summary = {
        fullType = fullType,
        tags = copySortedTags(fullType),
        connections = collectConnections(fullType),
        useCaseCount = countUseCaseLines(fullType),
    }
    summary.revision = table.concat({
        fullType,
        tostring(summary.useCaseCount),
        table.concat(summary.tags, "\0"),
        table.concat(summary.connections, "\0"),
    }, "|")
    summaryByFullType[fullType] = summary
    return copySummary(summary)
end

--- Explicit dev/test reload hook. Static generated data is otherwise session-stable.
function IrisTooltipSummary.reset()
    IrisClassifications = nil
    IrisRecipeIndex = nil
    IrisMoveablesIndex = nil
    IrisFixingIndex = nil
    IrisUseCaseDescriptions = nil
    IrisUseCaseDescriptionsLookup = nil
    loaded = false
    summaryByFullType = {}
end

return IrisTooltipSummary
