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

local TagParser = require("Iris/Logic/IrisDesc/TagParser")
local Ordering = require("Iris/Logic/IrisDesc/Ordering")
local Templates = require("Iris/Logic/IrisDesc/Templates")
local Renderer = require("Iris/Logic/IrisDesc/Renderer")

local Logger = require("Iris/Logic/IrisDesc/Logger")

local IrisDescGenerator = {}


---설명 블록 생성
---@param item_fulltype string 아이템 FullType (현재 사용 안 함, 확장용)
---@param tags table 소분류 태그 배열
---@param meta_primary_opt string|nil 주 소분류 메타 (선택)
---@return table blocks 렌더링된 블록 문자열 배열
function IrisDescGenerator.generate(item_fulltype, tags, meta_primary_opt)
    local debugEnabled = Logger.isDebugEnabled and Logger.isDebugEnabled()

    if debugEnabled then
        Logger.debug("[IrisDescGenerator.generate] ========== START ==========")
        Logger.debug("[IrisDescGenerator.generate] item_fulltype = " .. tostring(item_fulltype))
        Logger.debug("[IrisDescGenerator.generate] tags type = " .. type(tags))
        if tags then
            Logger.debug("[IrisDescGenerator.generate] tags count = " .. #tags)
            for i, t in ipairs(tags) do
                Logger.debug("[IrisDescGenerator.generate] input tags[" .. i .. "] = '" .. tostring(t) .. "'")
            end
        end
        Logger.debug("[IrisDescGenerator.generate] meta_primary_opt = " .. tostring(meta_primary_opt))
    end
    
    -- 1. 태그 수집 (유효한 것만)
    if debugEnabled then
        Logger.debug("[IrisDescGenerator.generate] Step 1: TagParser.collect()...")
    end
    local tag_set = TagParser.collect(tags)
    if debugEnabled then
        Logger.debug("[IrisDescGenerator.generate] tag_set type = " .. type(tag_set))
        if tag_set then
            Logger.debug("[IrisDescGenerator.generate] tag_set contents:")
            for k, v in pairs(tag_set) do
                Logger.debug("[IrisDescGenerator.generate]   tag_set['" .. tostring(k) .. "'] = " .. tostring(v))
            end
        end
    end
    
    -- 2. 소분류 0개 → 빈 배열
    local tagCount = TagParser.count(tag_set)
    if debugEnabled then
        Logger.debug("[IrisDescGenerator.generate] Step 2: TagParser.count() = " .. tostring(tagCount))
    end
    
    if tagCount == 0 then
        if debugEnabled then
            Logger.debug("[IrisDescGenerator.generate] No valid tags, returning empty blocks")
            Logger.debug("[IrisDescGenerator.generate] ========== END (empty) ==========")
        end
        return {}
    end
    
    -- 3. 주 소분류 결정 + 소분류 정렬
    if debugEnabled then
        Logger.debug("[IrisDescGenerator.generate] Step 3: Ordering.resolveSubcategories()...")
    end
    local anchor, ordered = Ordering.resolveSubcategories(tag_set, meta_primary_opt)
    if debugEnabled then
        Logger.debug("[IrisDescGenerator.generate] anchor = '" .. tostring(anchor) .. "'")
        Logger.debug("[IrisDescGenerator.generate] ordered type = " .. type(ordered))
        if ordered then
            Logger.debug("[IrisDescGenerator.generate] ordered count = " .. #ordered)
            for i, subcat in ipairs(ordered) do
                Logger.debug("[IrisDescGenerator.generate] ordered[" .. i .. "] = '" .. tostring(subcat) .. "'")
            end
        end
    end
    
    -- 4. 템플릿 바인딩 + 블록 렌더링
    if debugEnabled then
        Logger.debug("[IrisDescGenerator.generate] Step 4: Template binding + rendering...")
    end
    local blocks = {}
    for i, subcat in ipairs(ordered) do
        if debugEnabled then
            Logger.debug("[IrisDescGenerator.generate] Processing subcat[" .. i .. "] = '" .. subcat .. "'")
        end
        
        local template = Templates.getTemplate(subcat)
        if debugEnabled then
            Logger.debug("[IrisDescGenerator.generate]   template exists = " .. tostring(template ~= nil))
        end
        
        if template then
            if debugEnabled then
                Logger.debug("[IrisDescGenerator.generate]   template.headline = '" .. tostring(template.headline) .. "'")
                Logger.debug("[IrisDescGenerator.generate]   template.bullet_count = " .. tostring(template.bullets and #template.bullets or 0))
            end
            
            -- 템플릿 있음 → 블록 렌더링
            local block = Renderer.renderBlock(template)
            if debugEnabled then
                Logger.debug("[IrisDescGenerator.generate]   rendered block (first 100 chars) = [[" .. tostring(block):sub(1, 100) .. "]]")
            end
            
            table.insert(blocks, block)
        else
            if debugEnabled then
                Logger.debug("[IrisDescGenerator.generate]   No template for '" .. subcat .. "', skipping")
            end
        end
        -- 템플릿 없음 → 해당 블록 생략 (폴백 금지)
    end
    
    if debugEnabled then
        Logger.debug("[IrisDescGenerator.generate] Final blocks count = " .. #blocks)
        for i, block in ipairs(blocks) do
            Logger.debug("[IrisDescGenerator.generate] blocks[" .. i .. "] (first 80 chars) = [[" .. tostring(block):sub(1, 80) .. "]]")
        end
        Logger.debug("[IrisDescGenerator.generate] ========== END ==========")
    end
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

