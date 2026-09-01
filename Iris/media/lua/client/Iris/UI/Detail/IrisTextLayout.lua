-- Width-aware display wrapping shared by Iris detail surfaces.
local IrisTextLayout = {}

local function characterEnds(text)
    local ends = {}
    for i = 1, #text do
        local following = text:byte(i + 1)
        if not following or following < 128 or following >= 192 then
            ends[#ends + 1] = i
        end
    end
    return ends
end

local function wrapPhysicalLine(text, width, manager, font, lines)
    if text == "" then
        lines[#lines + 1] = ""
        return
    end
    local ends = characterEnds(text)
    local first, startByte = 1, 1
    while first <= #ends do
        local low, high, fit = first, #ends, first - 1
        while low <= high do
            local middle = math.floor((low + high) / 2)
            if manager:MeasureStringX(font, text:sub(startByte, ends[middle])) <= width then
                fit = middle
                low = middle + 1
            else
                high = middle - 1
            end
        end
        if fit < first then fit = first end
        if fit < #ends then
            for i = fit, first, -1 do
                if text:sub(ends[i], ends[i]):match("%s") then
                    fit = i
                    break
                end
            end
        end
        lines[#lines + 1] = text:sub(startByte, ends[fit])
        startByte = ends[fit] + 1
        first = fit + 1
    end
end

function IrisTextLayout.wrapLines(text, width, font)
    if type(text) ~= "string" or text == "" or type(width) ~= "number" or width <= 0 then
        return {}
    end
    local manager = getTextManager()
    local lines = {}
    local normalized = text:gsub("\r\n", "\n"):gsub("\r", "\n")
    for physical in (normalized .. "\n"):gmatch("(.-)\n") do
        wrapPhysicalLine(physical, width, manager, font, lines)
    end
    return lines
end

return IrisTextLayout
