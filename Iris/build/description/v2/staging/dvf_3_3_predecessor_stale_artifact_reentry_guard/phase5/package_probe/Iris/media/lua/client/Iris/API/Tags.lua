--[[
    Tags.lua - Iris classification tag facade

    Core facade. Reads frozen build-time classification data only.
]]

local Tags = {}

local Array = require("Iris/Util/Array")
local StaticData = require("Iris/API/StaticData")
local ItemKey = require("Iris/Util/ItemKey")

--- 아이템의 분류 태그 조회 (O(1) 정적 조회)
--- @param item InventoryItem|ScriptItem
--- @return table 태그 Set 또는 빈 테이블
function Tags.getTagsForItem(item)
    if not item then return {} end

    local fullType = ItemKey.getFullTypeFromItem(item)
    if not fullType then return {} end

    local classifications = StaticData.get("classifications")
    if not classifications then return {} end

    local tags = classifications[fullType]
    if not tags then return {} end

    local tagSet = {}
    for _, tag in ipairs(tags) do
        tagSet[tag] = true
    end
    return tagSet
end

--- fullType으로 태그 직접 조회
--- @param fullType string
--- @return table 태그 배열 또는 빈 테이블
function Tags.getTags(fullType)
    if not fullType then return {} end

    local classifications = StaticData.get("classifications")
    if not classifications then return {} end

    return classifications[fullType] or {}
end

--- 아이템이 특정 태그를 가지고 있는지 확인
--- @param fullType string
--- @param tag string
--- @return boolean
function Tags.hasTag(fullType, tag)
    return Array.contains(Tags.getTags(fullType), tag)
end

--- 아이템이 분류되었는지 확인
--- @param fullType string
--- @return boolean
function Tags.isClassified(fullType)
    local tags = Tags.getTags(fullType)
    return #tags > 0
end

return Tags
