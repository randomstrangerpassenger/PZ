--[[
    IrisDesc Renderer
    
    블록 렌더링
    
    ⚠️ 헌법:
    - 헤더 형식: [{header}]
    - 본문: lines를 \n으로 결합 (변형 금지)
]]

local IrisDescRenderer = {}


---단일 블록 렌더링
---@param template table TemplateBlock { header, lines }
---@return string 렌더링된 블록 문자열
function IrisDescRenderer.renderBlock(template)
    print("[Renderer.renderBlock] ========== START ==========")
    print("[Renderer.renderBlock] template = " .. tostring(template))
    
    if not template then
        print("[Renderer.renderBlock] template is nil, returning empty string")
        print("[Renderer.renderBlock] ========== END ==========")
        return ""
    end
    
    print("[Renderer.renderBlock] template.header = '" .. tostring(template.header) .. "'")
    print("[Renderer.renderBlock] template.lines type = " .. type(template.lines))
    if template.lines then
        print("[Renderer.renderBlock] template.lines count = " .. #template.lines)
        for i, line in ipairs(template.lines) do
            print("[Renderer.renderBlock] lines[" .. i .. "] = '" .. line .. "'")
            -- 바이트 확인 (인코딩 문제 진단용)
            local bytes = {}
            for j = 1, math.min(20, #line) do
                bytes[#bytes + 1] = string.byte(line, j)
            end
            print("[Renderer.renderBlock] lines[" .. i .. "] bytes (first 20) = " .. table.concat(bytes, ", "))
        end
    end
    
    -- 헤더: [header]
    local header = "[" .. template.header .. "]"
    print("[Renderer.renderBlock] formatted header = '" .. header .. "'")
    
    -- 본문: lines를 \n으로 결합
    local body = table.concat(template.lines, "\n")
    print("[Renderer.renderBlock] body length = " .. #body)
    print("[Renderer.renderBlock] body = [[" .. body:sub(1, 100) .. "]]")
    
    local result = header .. "\n" .. body
    print("[Renderer.renderBlock] result length = " .. #result)
    print("[Renderer.renderBlock] result = [[" .. result:sub(1, 150) .. "]]")
    print("[Renderer.renderBlock] ========== END ==========")
    
    return result
end


---블록 배열을 단일 문자열로 결합 (UI 호출용)
---@param blocks table 블록 문자열 배열
---@return string 빈 줄 1개로 구분된 전체 텍스트
function IrisDescRenderer.joinBlocks(blocks)
    return table.concat(blocks, "\n\n")
end


return IrisDescRenderer
