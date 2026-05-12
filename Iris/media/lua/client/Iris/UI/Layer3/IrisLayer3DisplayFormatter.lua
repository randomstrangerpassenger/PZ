--[[
    IrisLayer3DisplayFormatter.lua

    UI-only presentation formatter for Layer 3 display text.

    This module may add display line breaks for Browser/Wiki surfaces. It must
    not filter, reorder, summarize, or rewrite Layer 3 source text.
]]

local Formatter = {}

local function trimText(value)
    if not value then
        return ""
    end
    return tostring(value):gsub("^%s+", ""):gsub("%s+$", "")
end

local function isSentenceBoundary(text, index)
    local char = text:sub(index, index)
    if char ~= "." and char ~= "!" and char ~= "?" then
        return false
    end
    if char == "." then
        local prev = index > 1 and text:sub(index - 1, index - 1) or ""
        local next = index < #text and text:sub(index + 1, index + 1) or ""
        if prev:match("%d") and next:match("%d") then
            return false
        end
    end
    return true
end

local function splitSentences(text)
    local sentences = {}
    local startIndex = 1

    for i = 1, #text do
        if isSentenceBoundary(text, i) then
            local sentence = trimText(text:sub(startIndex, i))
            if sentence ~= "" then
                table.insert(sentences, sentence)
            end
            startIndex = i + 1
        end
    end

    local tail = trimText(text:sub(startIndex))
    if tail ~= "" then
        table.insert(sentences, tail)
    end

    return sentences
end

function Formatter.format(text)
    if not text or text == "" then
        return text
    end

    local formattedLines = {}
    for rawLine in tostring(text):gmatch("[^\n]+") do
        local line = trimText(rawLine)
        if line ~= "" then
            local sentences = splitSentences(line)
            if #sentences <= 2 then
                table.insert(formattedLines, line)
            else
                local chunkIndex = 1
                while chunkIndex <= #sentences do
                    local chunk = {sentences[chunkIndex]}
                    if sentences[chunkIndex + 1] then
                        table.insert(chunk, sentences[chunkIndex + 1])
                    end
                    table.insert(formattedLines, table.concat(chunk, " "))
                    chunkIndex = chunkIndex + 2
                end
            end
        end
    end

    if #formattedLines == 0 then
        return trimText(text)
    end

    return table.concat(formattedLines, "\n")
end

return Formatter
