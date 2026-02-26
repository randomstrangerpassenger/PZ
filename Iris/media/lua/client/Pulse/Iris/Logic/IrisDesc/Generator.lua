--[[
    IrisDesc Generator
    
    외부 API (진입점)
    파이프라인: TagParser → Ordering → Templates → Renderer
    
    ⚠️ 헌법:
    - 출력: blocks 배열 (각 원소는 렌더링된 블록 문자열)
    - 소분류 0개 → 빈 배열
    - 템플릿 없는 소분류 → 해당 블록 생략
    - 폴백/보정/기본 문구 금지
]]

local TagParser = require("Pulse/Iris/Logic/IrisDesc/TagParser")
local Ordering = require("Pulse/Iris/Logic/IrisDesc/Ordering")
local Templates = require("Pulse/Iris/Logic/IrisDesc/Templates")
local Renderer = require("Pulse/Iris/Logic/IrisDesc/Renderer")

local IrisDescGenerator = {}


---설명 블록 생성
---@param item_fulltype string 아이템 FullType (현재 사용 안 함, 확장용)
---@param tags table 소분류 태그 배열
---@param meta_primary_opt string|nil 주 소분류 메타 (선택)
---@return table blocks 렌더링된 블록 문자열 배열
function IrisDescGenerator.generate(item_fulltype, tags, meta_primary_opt)
    print("[IrisDescGenerator.generate] ========== START ==========")
    print("[IrisDescGenerator.generate] item_fulltype = " .. tostring(item_fulltype))
    print("[IrisDescGenerator.generate] tags type = " .. type(tags))
    if tags then
        print("[IrisDescGenerator.generate] tags count = " .. #tags)
        for i, t in ipairs(tags) do
            print("[IrisDescGenerator.generate] input tags[" .. i .. "] = '" .. tostring(t) .. "'")
        end
    end
    print("[IrisDescGenerator.generate] meta_primary_opt = " .. tostring(meta_primary_opt))
    
    -- 1. 태그 수집 (유효한 것만)
    print("[IrisDescGenerator.generate] Step 1: TagParser.collect()...")
    local tag_set = TagParser.collect(tags)
    print("[IrisDescGenerator.generate] tag_set type = " .. type(tag_set))
    if tag_set then
        print("[IrisDescGenerator.generate] tag_set contents:")
        for k, v in pairs(tag_set) do
            print("[IrisDescGenerator.generate]   tag_set['" .. tostring(k) .. "'] = " .. tostring(v))
        end
    end
    
    -- 2. 소분류 0개 → 빈 배열
    local tagCount = TagParser.count(tag_set)
    print("[IrisDescGenerator.generate] Step 2: TagParser.count() = " .. tostring(tagCount))
    
    if tagCount == 0 then
        print("[IrisDescGenerator.generate] No valid tags, returning empty blocks")
        print("[IrisDescGenerator.generate] ========== END (empty) ==========")
        return {}
    end
    
    -- 3. 주 소분류 결정
    print("[IrisDescGenerator.generate] Step 3: Ordering.pickAnchor()...")
    local anchor = Ordering.pickAnchor(tag_set, meta_primary_opt)
    print("[IrisDescGenerator.generate] anchor = '" .. tostring(anchor) .. "'")
    
    -- 4. 소분류 정렬
    print("[IrisDescGenerator.generate] Step 4: Ordering.orderSubcategories()...")
    local ordered = Ordering.orderSubcategories(tag_set, anchor)
    print("[IrisDescGenerator.generate] ordered type = " .. type(ordered))
    if ordered then
        print("[IrisDescGenerator.generate] ordered count = " .. #ordered)
        for i, subcat in ipairs(ordered) do
            print("[IrisDescGenerator.generate] ordered[" .. i .. "] = '" .. tostring(subcat) .. "'")
        end
    end
    
    -- 5. 템플릿 바인딩 + 블록 렌더링
    print("[IrisDescGenerator.generate] Step 5: Template binding + rendering...")
    local blocks = {}
    for i, subcat in ipairs(ordered) do
        print("[IrisDescGenerator.generate] Processing subcat[" .. i .. "] = '" .. subcat .. "'")
        
        local template = Templates.getTemplate(subcat)
        print("[IrisDescGenerator.generate]   template exists = " .. tostring(template ~= nil))
        
        if template then
            print("[IrisDescGenerator.generate]   template.headline = '" .. tostring(template.headline) .. "'")
            print("[IrisDescGenerator.generate]   template.bullet_count = " .. tostring(template.bullets and #template.bullets or 0))
            
            -- 템플릿 있음 → 블록 렌더링
            local block = Renderer.renderBlock(template)
            print("[IrisDescGenerator.generate]   rendered block (first 100 chars) = [[" .. tostring(block):sub(1, 100) .. "]]")
            
            table.insert(blocks, block)
        else
            print("[IrisDescGenerator.generate]   No template for '" .. subcat .. "', skipping")
        end
        -- 템플릿 없음 → 해당 블록 생략 (폴백 금지)
    end
    
    print("[IrisDescGenerator.generate] Final blocks count = " .. #blocks)
    for i, block in ipairs(blocks) do
        print("[IrisDescGenerator.generate] blocks[" .. i .. "] (first 80 chars) = [[" .. tostring(block):sub(1, 80) .. "]]")
    end
    
    print("[IrisDescGenerator.generate] ========== END ==========")
    return blocks
end


---설명을 단일 문자열로 반환 (UI 편의용)
---@param item_fulltype string 아이템 FullType
---@param tags table 소분류 태그 배열
---@param meta_primary_opt string|nil 주 소분류 메타 (선택)
---@return string 전체 설명 문자열
function IrisDescGenerator.generateString(item_fulltype, tags, meta_primary_opt)
    local blocks = IrisDescGenerator.generate(item_fulltype, tags, meta_primary_opt)
    return Renderer.joinBlocks(blocks)
end


return IrisDescGenerator
