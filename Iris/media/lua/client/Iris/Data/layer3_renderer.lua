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
local loadStatusLogged = false


--- 데이터 로드 (최초 1회)
local function ensureData()
    if dataLoaded then return end
    dataLoaded = true
    
    local ok, data = pcall(function()
        if IrisLayer3Data then
            return IrisLayer3Data
        end
        local loadOk, loaded = pcall(require, "Iris/Data/IrisLayer3Data")
        if loadOk and loaded then
            if not IrisLayer3Data then
                IrisLayer3Data = loaded
            end
            return loaded
        end
        if not loadStatusLogged and not loadOk then
            loadStatusLogged = true
            print("[Iris:Layer3] Failed to require IrisLayer3Data: " .. tostring(loaded))
        end
        return IrisLayer3Data
    end)
    
    if ok and data then
        layer3Data = data
        if not loadStatusLogged then
            loadStatusLogged = true
            print("[Iris:Layer3] Loaded IrisLayer3Data")
        end
    end
end


--- fulltype에 대한 3계층 텍스트를 반환한다.
---@param fullType string 아이템의 FullType
---@param options table|nil consumer option table
---@return string|nil 3계층 텍스트 또는 nil (침묵)
local function getEntry(fullType)
    ensureData()

    if not layer3Data or not fullType then
        return nil
    end

    local ok, result = pcall(function()
        return layer3Data[fullType]
    end)

    if ok then
        return result
    end

    -- pcall 실패 시 조용히 nil 반환
    return nil
end

function Layer3Renderer.getPublishState(fullType)
    local entry = getEntry(fullType)
    if entry and entry.publish_state then
        return entry.publish_state
    end
    return nil
end

function Layer3Renderer.getRawText(fullType)
    local entry = getEntry(fullType)
    if entry and entry.text_ko then
        return entry.text_ko
    end
    return nil
end

function Layer3Renderer.getText(fullType, options)
    local entry = getEntry(fullType)
    if not entry then
        return nil
    end

    local publishState = entry.publish_state
    local includeInternalOnly = options and options.include_internal_only == true
    if publishState == "internal_only" and not includeInternalOnly then
        return nil
    end

    if entry.text_ko then
        return entry.text_ko
    end
    return nil
end


return Layer3Renderer
