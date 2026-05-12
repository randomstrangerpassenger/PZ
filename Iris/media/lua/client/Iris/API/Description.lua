--[[
    Description.lua - Iris description facade

    Description facade. Generates description blocks from frozen tags and the
    runtime description generator without rechecking evidence.
]]

local Description = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local ItemKey = require("Iris/Util/ItemKey")
local Tags = require("Iris/API/Tags")
local debug = bootstrap.debug
local warn = bootstrap.warn
local logError = bootstrap.logError

local configChecked = false
local devLogEnabled = false

local function isDevLogEnabled()
    if configChecked then
        return devLogEnabled
    end

    configChecked = true
    local ok, config = safeRequire("Iris/IrisConfig")
    devLogEnabled = ok and config and config.DEBUG == true
    return devLogEnabled
end

local IrisDescGenerator = nil
local IrisDescGeneratorLoadAttempted = false

local function ensureDescGenerator()
    if IrisDescGenerator or IrisDescGeneratorLoadAttempted then
        return
    end

    IrisDescGeneratorLoadAttempted = true
    local ok, result = safeRequire("Iris/Logic/IrisDesc/Generator")
    if ok then
        IrisDescGenerator = result
    else
        warn("[IrisAPI] IrisDescGenerator not found: " .. tostring(result))
    end
end

--- 아이템의 설명 블록 배열 반환
--- @param fullType string 아이템 FullType
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return table 블록 문자열 배열
function Description.getDescriptionBlocks(fullType, primarySubcategory)
    local devLog = isDevLogEnabled()
    if devLog then
        debug("[IrisAPI.getDescriptionBlocks] ========== START ==========")
        debug("[IrisAPI.getDescriptionBlocks] fullType = " .. tostring(fullType))
        debug("[IrisAPI.getDescriptionBlocks] primarySubcategory = " .. tostring(primarySubcategory))
    end

    if not fullType then
        if devLog then
            debug("[IrisAPI.getDescriptionBlocks] fullType is nil, returning empty")
        end
        return {}
    end

    if devLog then
        debug("[IrisAPI.getDescriptionBlocks] Calling ensureDescGenerator()...")
    end
    ensureDescGenerator()
    if devLog then
        debug("[IrisAPI.getDescriptionBlocks] ensureDescGenerator() complete")
        debug("[IrisAPI.getDescriptionBlocks] IrisDescGenerator exists = " .. tostring(IrisDescGenerator ~= nil))
    end

    if not IrisDescGenerator then
        if devLog then
            debug("[IrisAPI.getDescriptionBlocks] IrisDescGenerator is nil, returning empty")
        end
        return {}
    end

    if devLog then
        debug("[IrisAPI.getDescriptionBlocks] Calling Tags.getTags(" .. fullType .. ")...")
    end
    local tags = Tags.getTags(fullType)
    if devLog then
        debug("[IrisAPI.getDescriptionBlocks] getTags returned: " .. type(tags))
        if tags then
            debug("[IrisAPI.getDescriptionBlocks] tags count = " .. #tags)
            for i, tag in ipairs(tags) do
                debug("[IrisAPI.getDescriptionBlocks] tags[" .. i .. "] = '" .. tostring(tag) .. "'")
            end
        end
    end

    if #tags == 0 then
        if devLog then
            debug("[IrisAPI.getDescriptionBlocks] No tags found, returning empty")
        end
        return {}
    end

    if devLog then
        debug("[IrisAPI.getDescriptionBlocks] Calling IrisDescGenerator.generate()...")
        debug("[IrisAPI.getDescriptionBlocks] IrisDescGenerator.generate exists = " .. tostring(IrisDescGenerator.generate ~= nil))
    end

    local ok, result = ProtectedCall.data(function()
        return IrisDescGenerator.generate(fullType, tags, primarySubcategory)
    end)

    if devLog then
        debug("[IrisAPI.getDescriptionBlocks] generate protected call: ok=" .. tostring(ok))
    end
    if not ok then
        logError("[IrisAPI.getDescriptionBlocks] generate error: " .. tostring(result))
        return {}
    end

    if devLog then
        debug("[IrisAPI.getDescriptionBlocks] result type = " .. type(result))
        if result then
            debug("[IrisAPI.getDescriptionBlocks] result (blocks) count = " .. #result)
            for i, block in ipairs(result) do
                debug("[IrisAPI.getDescriptionBlocks] block[" .. i .. "] = [[" .. tostring(block):sub(1, 100) .. "]]")
            end
        end
        debug("[IrisAPI.getDescriptionBlocks] ========== END ==========")
    end

    if ok and result then
        return result
    end
    return {}
end

--- 아이템의 설명 문자열 반환 (소분류 기반)
--- 소분류 템플릿(IrisDescGenerator)만 사용
--- @param fullType string 아이템 FullType
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return string 설명 문자열 또는 빈 문자열
function Description.getDescription(fullType, primarySubcategory)
    if not fullType then return "" end

    ensureDescGenerator()

    if not IrisDescGenerator then
        return ""
    end

    local tags = Tags.getTags(fullType)
    if #tags == 0 then
        return ""
    end

    local ok, result = ProtectedCall.data(function()
        return IrisDescGenerator.generate(fullType, tags, primarySubcategory)
    end)

    if ok and result and #result > 0 then
        return table.concat(result, "\n\n")
    end

    return ""
end

--- InventoryItem에서 설명 반환 (편의 함수)
--- @param item InventoryItem|ScriptItem
--- @param primarySubcategory string|nil 주 소분류 메타 (선택)
--- @return string 전체 설명 문자열
function Description.getDescriptionForItem(item, primarySubcategory)
    if not item then return "" end

    local fullType = ItemKey.getFullTypeFromItem(item)
    if not fullType then return "" end

    return Description.getDescription(fullType, primarySubcategory)
end

return Description
