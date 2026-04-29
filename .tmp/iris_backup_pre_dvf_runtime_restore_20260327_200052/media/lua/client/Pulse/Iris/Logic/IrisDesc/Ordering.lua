--[[
    IrisDesc Ordering
    
    주 소분류 결정 (Anchor) 및 정렬
    
    ⚠️ 헌법:
    - 대분류 우선순위: Tool(1) < Combat(2) < Consumable(3) < Resource(4) < Literature(5) < Wearable(6)
    - anchor 맨 앞, 나머지도 대분류 번호 → 코드 순 정렬
    - meta anchor가 set에 없어도 보정/제거/대체 금지
]]

local TagParser = require("Pulse/Iris/Logic/IrisDesc/TagParser")

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


---주 소분류(anchor) 결정
---@param subcat_set table { [tag] = true } 형태
---@param meta_primary_opt string|nil 메타에서 지정된 주 소분류
---@return string|nil anchor 주 소분류 ID
function IrisDescOrdering.pickAnchor(subcat_set, meta_primary_opt)
    print("[Ordering.pickAnchor] ========== START ==========")
    print("[Ordering.pickAnchor] subcat_set = " .. tostring(subcat_set))
    print("[Ordering.pickAnchor] meta_primary_opt = " .. tostring(meta_primary_opt))
    
    local count = TagParser.count(subcat_set)
    print("[Ordering.pickAnchor] subcat_set count = " .. count)
    
    -- 소분류가 없으면 nil
    if count == 0 then
        print("[Ordering.pickAnchor] No subcategories, returning nil")
        print("[Ordering.pickAnchor] ========== END ==========")
        return nil
    end
    
    -- meta가 있고 set에 포함되어 있으면 그대로 사용
    if meta_primary_opt and subcat_set[meta_primary_opt] then
        print("[Ordering.pickAnchor] Using meta_primary_opt as anchor: " .. meta_primary_opt)
        print("[Ordering.pickAnchor] ========== END ==========")
        return meta_primary_opt
    end
    
    -- 없으면 대분류 번호 순 → 코드 순 첫 번째
    print("[Ordering.pickAnchor] No meta, sorting to find anchor...")
    local sorted = TagParser.toArray(subcat_set)
    for i, tag in ipairs(sorted) do
        print("[Ordering.pickAnchor] sorted (before)[" .. i .. "] = " .. tag)
    end
    
    table.sort(sorted, compareTags)
    
    for i, tag in ipairs(sorted) do
        print("[Ordering.pickAnchor] sorted (after)[" .. i .. "] = " .. tag)
    end
    
    local anchor = sorted[1]
    print("[Ordering.pickAnchor] Picked anchor = '" .. tostring(anchor) .. "'")
    print("[Ordering.pickAnchor] ========== END ==========")
    
    return anchor
end


---소분류 정렬
---anchor를 맨 앞으로 이동, 나머지는 대분류 번호 → 코드 순
---@param subcat_set table { [tag] = true } 형태
---@param anchor string|nil 주 소분류 ID
---@return table 정렬된 소분류 배열
function IrisDescOrdering.orderSubcategories(subcat_set, anchor)
    print("[Ordering.orderSubcategories] ========== START ==========")
    print("[Ordering.orderSubcategories] anchor = " .. tostring(anchor))
    
    -- set을 배열로 변환 후 정렬
    local sorted = TagParser.toArray(subcat_set)
    print("[Ordering.orderSubcategories] toArray result count = " .. #sorted)
    
    table.sort(sorted, compareTags)
    print("[Ordering.orderSubcategories] sorted result:")
    for i, tag in ipairs(sorted) do
        print("[Ordering.orderSubcategories]   sorted[" .. i .. "] = " .. tag)
    end
    
    -- anchor가 없거나 sorted에 없으면 그대로 반환
    if not anchor then
        print("[Ordering.orderSubcategories] No anchor, returning sorted as-is")
        print("[Ordering.orderSubcategories] ========== END ==========")
        return sorted
    end
    
    -- anchor를 맨 앞으로 이동
    print("[Ordering.orderSubcategories] Moving anchor to front...")
    local result = {}
    local anchorFound = false
    
    for _, tag in ipairs(sorted) do
        if tag == anchor then
            anchorFound = true
            print("[Ordering.orderSubcategories] Found anchor in sorted list")
        else
            table.insert(result, tag)
        end
    end
    
    -- anchor를 맨 앞에 삽입
    if anchorFound then
        table.insert(result, 1, anchor)
        print("[Ordering.orderSubcategories] Inserted anchor at front")
    else
        print("[Ordering.orderSubcategories] Anchor not found in list!")
    end
    
    print("[Ordering.orderSubcategories] Final result:")
    for i, tag in ipairs(result) do
        print("[Ordering.orderSubcategories]   result[" .. i .. "] = " .. tag)
    end
    print("[Ordering.orderSubcategories] ========== END ==========")
    
    return result
end


return IrisDescOrdering
