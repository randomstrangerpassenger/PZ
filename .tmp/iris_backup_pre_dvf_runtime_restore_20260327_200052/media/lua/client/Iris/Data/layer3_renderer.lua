--[[
    Layer 3 Renderer — 3계층 개별 아이템 설명 렌더
    
    ⚠️ 헌법:
    - text_ko가 있으면 출력, 없으면 건너뜀
    - 문장 수정/필터링/재정렬/추가/폴백 절대 금지
    - pcall로 감싸서 개별 실패 시 무시
]]

local Layer3Renderer = {}

-- 3계층 데이터 (빌드 시 생성된 JSON → Lua 테이블 변환)
local layer3Data = nil
local dataLoaded = false


--- 데이터 로드 (최초 1회)
local function ensureData()
    if dataLoaded then return end
    dataLoaded = true
    
    local ok, data = pcall(function()
        -- IrisLayer3Data는 convert_descriptions_to_lua 등으로 변환되어 로드됨
        -- 또는 JSON 파싱으로 로드
        if IrisLayer3Data then
            return IrisLayer3Data
        end
        return nil
    end)
    
    if ok and data then
        layer3Data = data
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
