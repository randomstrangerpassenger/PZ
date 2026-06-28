--[[
    IrisDesc Ordering
    
    주 소분류 결정 (Anchor) 및 정렬
    
    ⚠️ 헌법:
    - 대분류 우선순위: Tool(1) < Combat(2) < Consumable(3) < Resource(4) < Literature(5) < Wearable(6)
    - anchor 맨 앞, 나머지도 대분류 번호 → 코드 순 정렬
    - meta anchor가 set에 없어도 보정/제거/대체 금지
]]

local TagParser = require("Iris/Logic/IrisDesc/TagParser")

local Logger = require("Iris/Logic/IrisDesc/Logger")

local IrisDescOrdering = {}


-- 대분류 우선순위 맵
local CATEGORY_PRIORITY = {
    Tool = 1,
    Combat = 2,
    Consumable = 3,
    Resource = 4,
    Literature = 5,
    Wearable = 6,
}


---태그에서 대분류 추출
---@param tag string 소분류 ID (예: "Tool.1-A")
---@return string|nil 대분류 (예: "Tool")
local function extractCategory(tag)
    local dotPos = string.find(tag, "%.")
    if dotPos then
        return string.sub(tag, 1, dotPos - 1)
    end
    return nil
end


---태그에서 코드 추출
---@param tag string 소분류 ID (예: "Tool.1-A")
---@return string|nil 코드 (예: "A")
local function extractCode(tag)
    local dashPos = string.find(tag, "%-")
    if dashPos then
        return string.sub(tag, dashPos + 1)
    end
    return nil
end


---정렬 키 생성: (대분류 우선순위, 코드)
---@param tag string 소분류 ID
---@return number priority 대분류 우선순위
---@return string code 코드
local function getSortKey(tag)
    local category = extractCategory(tag)
    local code = extractCode(tag) or ""
    local priority = CATEGORY_PRIORITY[category] or 999
    return priority, code
end


---두 태그 비교 (정렬용)
---@param a string 첫 번째 태그
---@param b string 두 번째 태그
---@return boolean a가 b보다 앞인지
local function compareTags(a, b)
    local priorityA, codeA = getSortKey(a)
    local priorityB, codeB = getSortKey(b)
    
    if priorityA ~= priorityB then
        return priorityA < priorityB
    end
    return codeA < codeB
end


local function sortedSubcategories(subcat_set)
    local sorted = TagParser.toArray(subcat_set)
    table.sort(sorted, compareTags)
    return sorted
end


local function moveAnchorToFront(sorted, anchor)
    if not anchor then
        return sorted
    end

    local result = {}
    local anchorFound = false

    for _, tag in ipairs(sorted) do
        if tag == anchor then
            anchorFound = true
        else
            table.insert(result, tag)
        end
    end

    if anchorFound then
        table.insert(result, 1, anchor)
        return result
    end

    return sorted
end


---주 소분류(anchor)와 정렬된 소분류 배열을 한 번에 결정
---@param subcat_set table { [tag] = true } 형태
---@param meta_primary_opt string|nil 메타에서 지정된 주 소분류
---@return string|nil anchor 주 소분류 ID
---@return table ordered 정렬된 소분류 배열
function IrisDescOrdering.resolveSubcategories(subcat_set, meta_primary_opt)
    Logger.debug("[Ordering.resolveSubcategories] ========== START ==========")
    Logger.debug("[Ordering.resolveSubcategories] meta_primary_opt = " .. tostring(meta_primary_opt))

    local sorted = sortedSubcategories(subcat_set)
    Logger.debug("[Ordering.resolveSubcategories] sorted result:")
    for i, tag in ipairs(sorted) do
        Logger.debug("[Ordering.resolveSubcategories]   sorted[" .. i .. "] = " .. tag)
    end

    local anchor = nil
    if #sorted == 0 then
        Logger.debug("[Ordering.resolveSubcategories] No subcategories")
    elseif meta_primary_opt and subcat_set[meta_primary_opt] then
        anchor = meta_primary_opt
        Logger.debug("[Ordering.resolveSubcategories] Using meta_primary_opt as anchor: " .. meta_primary_opt)
    else
        anchor = sorted[1]
        Logger.debug("[Ordering.resolveSubcategories] Picked anchor = '" .. tostring(anchor) .. "'")
    end

    local ordered = moveAnchorToFront(sorted, anchor)
    Logger.debug("[Ordering.resolveSubcategories] Final result:")
    for i, tag in ipairs(ordered) do
        Logger.debug("[Ordering.resolveSubcategories]   ordered[" .. i .. "] = " .. tag)
    end
    Logger.debug("[Ordering.resolveSubcategories] ========== END ==========")

    return anchor, ordered
end


---주 소분류(anchor) 결정
---@param subcat_set table { [tag] = true } 형태
---@param meta_primary_opt string|nil 메타에서 지정된 주 소분류
---@return string|nil anchor 주 소분류 ID
function IrisDescOrdering.pickAnchor(subcat_set, meta_primary_opt)
    Logger.debug("[Ordering.pickAnchor] ========== START ==========")
    Logger.debug("[Ordering.pickAnchor] subcat_set = " .. tostring(subcat_set))
    Logger.debug("[Ordering.pickAnchor] meta_primary_opt = " .. tostring(meta_primary_opt))
    
    local count = TagParser.count(subcat_set)
    Logger.debug("[Ordering.pickAnchor] subcat_set count = " .. count)
    
    -- 소분류가 없으면 nil
    if count == 0 then
        Logger.debug("[Ordering.pickAnchor] No subcategories, returning nil")
        Logger.debug("[Ordering.pickAnchor] ========== END ==========")
        return nil
    end
    
    -- meta가 있고 set에 포함되어 있으면 그대로 사용
    if meta_primary_opt and subcat_set[meta_primary_opt] then
        Logger.debug("[Ordering.pickAnchor] Using meta_primary_opt as anchor: " .. meta_primary_opt)
        Logger.debug("[Ordering.pickAnchor] ========== END ==========")
        return meta_primary_opt
    end
    
    -- 없으면 대분류 번호 순 → 코드 순 첫 번째
    Logger.debug("[Ordering.pickAnchor] No meta, sorting to find anchor...")
    local sorted = sortedSubcategories(subcat_set)
    for i, tag in ipairs(sorted) do
        Logger.debug("[Ordering.pickAnchor] sorted[" .. i .. "] = " .. tag)
    end
    
    local anchor = sorted[1]
    Logger.debug("[Ordering.pickAnchor] Picked anchor = '" .. tostring(anchor) .. "'")
    Logger.debug("[Ordering.pickAnchor] ========== END ==========")
    
    return anchor
end


---소분류 정렬
---anchor를 맨 앞으로 이동, 나머지는 대분류 번호 → 코드 순
---@param subcat_set table { [tag] = true } 형태
---@param anchor string|nil 주 소분류 ID
---@return table 정렬된 소분류 배열
function IrisDescOrdering.orderSubcategories(subcat_set, anchor)
    Logger.debug("[Ordering.orderSubcategories] ========== START ==========")
    Logger.debug("[Ordering.orderSubcategories] anchor = " .. tostring(anchor))
    
    -- set을 배열로 변환 후 정렬
    local sorted = sortedSubcategories(subcat_set)
    Logger.debug("[Ordering.orderSubcategories] sorted result count = " .. #sorted)
    Logger.debug("[Ordering.orderSubcategories] sorted result:")
    for i, tag in ipairs(sorted) do
        Logger.debug("[Ordering.orderSubcategories]   sorted[" .. i .. "] = " .. tag)
    end
    
    -- anchor가 없거나 sorted에 없으면 그대로 반환
    if not anchor then
        Logger.debug("[Ordering.orderSubcategories] No anchor, returning sorted as-is")
        Logger.debug("[Ordering.orderSubcategories] ========== END ==========")
        return sorted
    end
    
    -- anchor를 맨 앞으로 이동
    Logger.debug("[Ordering.orderSubcategories] Moving anchor to front...")
    local result = moveAnchorToFront(sorted, anchor)
    if result ~= sorted then
        Logger.debug("[Ordering.orderSubcategories] Inserted anchor at front")
    else
        Logger.debug("[Ordering.orderSubcategories] Anchor not found in list!")
    end
    
    Logger.debug("[Ordering.orderSubcategories] Final result:")
    for i, tag in ipairs(result) do
        Logger.debug("[Ordering.orderSubcategories]   result[" .. i .. "] = " .. tag)
    end
    Logger.debug("[Ordering.orderSubcategories] ========== END ==========")
    
    return result
end


return IrisDescOrdering

