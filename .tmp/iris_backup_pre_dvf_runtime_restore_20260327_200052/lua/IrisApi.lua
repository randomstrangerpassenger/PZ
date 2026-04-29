--[[
    Iris Classification API
    
    100% Lua Runtime - No external dependencies
    Generated data is loaded from IrisData.lua
    
    Usage:
        require("IrisData")  -- Load classification data
        require("IrisApi")   -- Load this API
        
        local tags = Iris.getTags("Base.Hammer")
        local isTool = Iris.hasTag("Base.Hammer", "Tool.1-B")
        local allTools = Iris.getItemsByTag("Tool.1-B")
]]

-- ============================================
-- Module Initialization
-- ============================================

Iris = Iris or {}

-- Ensure IrisData is loaded
if not IrisData or not IrisData.Classifications then
    print("[Iris] WARNING: IrisData.Classifications not found. Load IrisData.lua first.")
    IrisData = IrisData or {}
    IrisData.Classifications = IrisData.Classifications or {}
end


-- ============================================
-- Core API Functions
-- ============================================

---Get all classification tags for an item
---@param fullType string The item's FullType (e.g., "Base.Hammer")
---@return table|nil Array of tags, or nil if not classified
function Iris.getTags(fullType)
    if not fullType then return nil end
    
    local tags = IrisData.Classifications[fullType]
    if not tags then return nil end
    
    -- Return a copy to prevent modification
    local result = {}
    for i, tag in ipairs(tags) do
        result[i] = tag
    end
    return result
end


---Check if an item has a specific tag
---@param fullType string The item's FullType
---@param tag string The tag to check for
---@return boolean True if the item has the tag
function Iris.hasTag(fullType, tag)
    if not fullType or not tag then return false end
    
    local tags = IrisData.Classifications[fullType]
    if not tags then return false end
    
    for _, t in ipairs(tags) do
        if t == tag then
            return true
        end
    end
    return false
end


---Check if an item is classified at all
---@param fullType string The item's FullType
---@return boolean True if the item has any classification
function Iris.isClassified(fullType)
    if not fullType then return false end
    return IrisData.Classifications[fullType] ~= nil
end


---Get the major category for an item (first tag's prefix)
---@param fullType string The item's FullType
---@return string|nil Major category name (e.g., "Tool", "Combat")
function Iris.getMajorCategory(fullType)
    local tags = IrisData.Classifications[fullType]
    if not tags or #tags == 0 then return nil end
    
    -- Extract prefix from first tag (e.g., "Tool" from "Tool.1-A")
    local firstTag = tags[1]
    local dotPos = string.find(firstTag, "%.")
    if dotPos then
        return string.sub(firstTag, 1, dotPos - 1)
    end
    return nil
end


---Get all items that have a specific tag
---@param tag string The tag to search for
---@return table Array of FullType strings
function Iris.getItemsByTag(tag)
    local result = {}
    
    for fullType, tags in pairs(IrisData.Classifications) do
        for _, t in ipairs(tags) do
            if t == tag then
                table.insert(result, fullType)
                break
            end
        end
    end
    
    return result
end


---Get all items in a major category
---@param category string Major category name (e.g., "Tool", "Combat")
---@return table Array of FullType strings
function Iris.getItemsByCategory(category)
    local result = {}
    local prefix = category .. "."
    
    for fullType, tags in pairs(IrisData.Classifications) do
        for _, tag in ipairs(tags) do
            if string.sub(tag, 1, #prefix) == prefix then
                table.insert(result, fullType)
                break
            end
        end
    end
    
    return result
end


---Get statistics about classifications
---@return table Stats table with counts
function Iris.getStats()
    local stats = {
        totalItems = 0,
        tagCounts = {},
        categoryCounts = {},
    }
    
    for fullType, tags in pairs(IrisData.Classifications) do
        stats.totalItems = stats.totalItems + 1
        
        for _, tag in ipairs(tags) do
            -- Count by tag
            stats.tagCounts[tag] = (stats.tagCounts[tag] or 0) + 1
            
            -- Count by category
            local dotPos = string.find(tag, "%.")
            if dotPos then
                local category = string.sub(tag, 1, dotPos - 1)
                stats.categoryCounts[category] = (stats.categoryCounts[category] or 0) + 1
            end
        end
    end
    
    return stats
end


-- ============================================
-- Read-Only Protection (Metatable Lock)
-- ============================================

-- Protect the Classifications table from modification
local classificationsProxy = {}
local classificationsMeta = {
    __index = IrisData.Classifications,
    __newindex = function(_, key, value)
        error("[Iris] ERROR: IrisData.Classifications is read-only. Cannot modify: " .. tostring(key))
    end,
    __pairs = function(_)
        return pairs(IrisData.Classifications)
    end,
    __len = function(_)
        local count = 0
        for _ in pairs(IrisData.Classifications) do count = count + 1 end
        return count
    end,
}
setmetatable(classificationsProxy, classificationsMeta)

-- ⚠️ 헌법적 필수: Read-only 프록시로 교체 (외부 수정 봉인)
IrisData.Classifications = classificationsProxy


-- ============================================
-- Version Info
-- ============================================

Iris.VERSION = "1.0.0"
Iris.API_VERSION = "1.0"


-- ============================================
-- Debug Helpers
-- ============================================

---Print classification info for an item (debug)
---@param fullType string The item's FullType
function Iris.debug(fullType)
    print("[Iris Debug] " .. tostring(fullType))
    
    local tags = Iris.getTags(fullType)
    if tags then
        print("  Tags: " .. table.concat(tags, ", "))
        print("  Category: " .. tostring(Iris.getMajorCategory(fullType)))
    else
        print("  Not classified")
    end
end


print("[Iris] API loaded. Version: " .. Iris.VERSION)
