-- One-level disclosure for producer-owned target groups; no gameplay inference.
require "ISUI/ISButton"
require "ISUI/ISLabel"
local Layout = require("Iris/UI/Detail/IrisTextLayout")
local View = {}

function View.render(panel, unit, x, y, font, locale, state, key, toggle, addText, rightPadding)
    local detail = unit.targetGroups
    if not detail then return addText(unit.text, x, y) end
    y = addText(detail.introduction, x, y) + 3
    for i = 1, detail.groupCount do
        local group = detail.groups[i]
        if group.presentation == "inline" then
            for n = 1, group.count do
                y = addText("- " .. group.entries[n].label, x + 10, y)
            end
            y = y + 4
        else
        local id = key .. ":" .. group.key
        local expanded = state[id] == true
        local title = (expanded and "[-] " or "[+] ") ..
            (locale == "KO" and "목록: " or "Listed: ") .. group.label .. " (" .. tostring(group.count) .. ")"
        local width = math.max(1, panel.width - x - (rightPadding or 10))
        local lines = Layout.wrapLines(title, math.max(1, width - 12), font)
        local height = math.max(26, #lines * 18 + 8)
        local button = ISButton:new(x, y, width, height, "", panel, function()
            state[id] = not expanded
            toggle()
        end)
        button:initialise()
        button.irisTargetGroupKey = id
        button.irisTargetGroupExpanded = expanded
        button.irisTargetGroupTitle = title
        panel:addChild(button)
        for n, line in ipairs(lines) do
            local label = ISLabel:new(6, 4 + (n - 1) * 18, 18, line, 0.8, 0.9, 1, 1, font, true)
            button:addChild(label)
        end
        y = y + height + 3
        if expanded then
            for n = 1, group.count do
                y = addText("- " .. group.entries[n].label, x + 10, y)
            end
            y = y + 4
        end
        end
    end
    return y
end
return View
