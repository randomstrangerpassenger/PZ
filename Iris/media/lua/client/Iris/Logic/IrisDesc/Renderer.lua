--[[
    IrisDesc Renderer
    
    블록 렌더링
    
    ⚠️ 헌법:
    - 헤더 형식: [{header}]
    - 본문: lines를 \n으로 결합 (변형 금지)
]]

local IrisDescRenderer = {}

local Logger = require("Iris/Logic/IrisDesc/Logger")


---단일 블록 렌더링
---@param template table TemplateBlock { header, lines }
---@return string 렌더링된 블록 문자열
function IrisDescRenderer.renderBlock(template)
    local debugEnabled = Logger.isDebugEnabled and Logger.isDebugEnabled()

    if debugEnabled then
        Logger.debug("[Renderer.renderBlock] ========== START ==========")
        Logger.debug("[Renderer.renderBlock] template = " .. tostring(template))
    end

    if not template then
        if debugEnabled then
            Logger.debug("[Renderer.renderBlock] template is nil, returning empty string")
            Logger.debug("[Renderer.renderBlock] ========== END ==========")
        end
        return ""
    end

    if debugEnabled then
        Logger.debug("[Renderer.renderBlock] template.header = '" .. tostring(template.header) .. "'")
        Logger.debug("[Renderer.renderBlock] template.lines type = " .. type(template.lines))
        if template.lines then
            Logger.debug("[Renderer.renderBlock] template.lines count = " .. #template.lines)
            for i, line in ipairs(template.lines) do
                Logger.debug("[Renderer.renderBlock] lines[" .. i .. "] = '" .. line .. "'")
                -- 바이트 확인 (인코딩 문제 진단용)
                local bytes = {}
                for j = 1, math.min(20, #line) do
                    bytes[#bytes + 1] = string.byte(line, j)
                end
                Logger.debug("[Renderer.renderBlock] lines[" .. i .. "] bytes (first 20) = " .. table.concat(bytes, ", "))
            end
        end
    end

    -- 헤더: [header]
    local header = "[" .. template.header .. "]"
    if debugEnabled then
        Logger.debug("[Renderer.renderBlock] formatted header = '" .. header .. "'")
    end

    -- 본문: lines를 \n으로 결합
    local body = table.concat(template.lines, "\n")
    if debugEnabled then
        Logger.debug("[Renderer.renderBlock] body length = " .. #body)
        Logger.debug("[Renderer.renderBlock] body = [[" .. body:sub(1, 100) .. "]]")
    end

    local result = header .. "\n" .. body
    if debugEnabled then
        Logger.debug("[Renderer.renderBlock] result length = " .. #result)
        Logger.debug("[Renderer.renderBlock] result = [[" .. result:sub(1, 150) .. "]]")
        Logger.debug("[Renderer.renderBlock] ========== END ==========")
    end

    return result
end


---블록 배열을 단일 문자열로 결합 (UI 호출용)
---@param blocks table 블록 문자열 배열
---@return string 빈 줄 1개로 구분된 전체 텍스트
function IrisDescRenderer.joinBlocks(blocks)
    return table.concat(blocks, "\n\n")
end


return IrisDescRenderer

