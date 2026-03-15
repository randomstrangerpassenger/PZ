--[[
    Layer 3 Renderer — 3계층 개별 아이템 설명 렌더
    
    ⚠️ 헌법:
    - text_ko가 있으면 출력, 없으면 건너뜀
    - 문장 수정/필터링/재정렬/추가/폴백 절대 금지
    - pcall로 감싸서 개별 실패 시 무시
]]

local Layer3Renderer = {}

-- 3계층 데이터 (빌드 시 dvf_3_3_rendered.json → IrisLayer3Data.lua로 변환)
-- 런타임 정규 소스: require("Iris/Data/IrisLayer3Data") → local table 반환
-- 중간 산출물(decisions, facts, sync_queue 등) 직접 참조 금지
local layer3Data = nil
local dataLoaded = false


--- 테이블 entry 수 카운트 (로그용)
local function countEntries(tbl)
    local n = 0
    for _ in pairs(tbl) do n = n + 1 end
    return n
end


--- 데이터 로드 (최초 1회, fail-loud)
local function ensureData()
    if dataLoaded then return end
    dataLoaded = true

    local ok, data = pcall(require, "Iris/Data/IrisLayer3Data")

    if ok and data and type(data) == "table" then
        layer3Data = data
        print("[Layer3Renderer] Loaded: " .. tostring(countEntries(data)) .. " entries")
    else
        -- fail-loud: 데이터 부재를 명시적으로 로그 (silent failure 방지)
        print("[Layer3Renderer] WARNING: IrisLayer3Data not available — layer 3 descriptions will be empty")
    end
end


--- fulltype에 대한 3계층 텍스트를 반환한다.
---@param fullType string 아이템의 FullType
---@return string|nil 3계층 텍스트 또는 nil (침묵)
function Layer3Renderer.getText(fullType)
    ensureData()
    
    if not layer3Data or not fullType then
        return nil
    end
    
    local ok, result = pcall(function()
        local entry = layer3Data[fullType]
        if entry and entry.text_ko then
            return entry.text_ko
        end
        return nil
    end)
    
    if ok then
        return result
    end
    
    -- pcall 실패 시 조용히 nil 반환
    return nil
end


return Layer3Renderer
