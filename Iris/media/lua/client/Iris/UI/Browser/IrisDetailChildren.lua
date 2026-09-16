-- Child collection, base positions and scroll offset for the Detail panel.
local ObjectAccess = require("Iris/Util/IrisObjectAccess")
local Children = {}

local function collectJavaDetailChildren(detailPanel)
    if detailPanel.javaObject and detailPanel.javaObject.getChildren then
        local ok, javaChildren = ObjectAccess.call(detailPanel.javaObject, "getChildren")
        if ok and javaChildren and javaChildren.size then
            local ok2, sz = ObjectAccess.call(javaChildren, "size")
            if ok2 and sz and sz > 0 then
                local children = {}
                for i = 0, sz - 1 do
                    local ok3, child = ObjectAccess.call(javaChildren, "get", i)
                    if ok3 and child then
                        table.insert(children, child)
                    end
                end
                return children
            end
        end
    end

    return {}
end

local function appendIpairsChildren(source, target)
    for _, child in ipairs(source) do
        table.insert(target, child)
    end
end

local function appendNumericPairsChildren(source, target)
    for k, child in pairs(source) do
        if type(k) == "number" then
            table.insert(target, child)
        end
    end
end

local function collectLuaDetailChildren(detailPanel)
    local ok, children = ObjectAccess.call(detailPanel, "getChildren")
    if not ok or not children then
        return {}
    end

    local collected = {}
    appendIpairsChildren(children, collected)
    if #collected == 0 then
        appendNumericPairsChildren(children, collected)
    end
    return collected
end

local DETAIL_CHILD_COLLECTORS = {
    collectJavaDetailChildren,
    collectLuaDetailChildren,
}

local function collectDetailChildren(detailPanel)
    for _, collector in ipairs(DETAIL_CHILD_COLLECTORS) do
        local children = collector(detailPanel)
        if #children > 0 then
            return children
        end
    end
    return {}
end

function Children.snapshotDetailChildren(detailPanel)
    local snapshot = {}
    for _, child in ipairs(collectDetailChildren(detailPanel)) do
        snapshot[child] = true
    end
    return snapshot
end

function Children.captureDetailSection(browser, name, order, before, startY, endY)
    browser.detailSections = browser.detailSections or {}
    browser.detailChildSections = browser.detailChildSections or {}
    local section = {name = name, order = order, startY = startY, endY = endY, children = {}}
    for _, child in ipairs(collectDetailChildren(browser.detailPanel)) do
        if not before[child] then
            table.insert(section.children, child)
            browser.detailChildSections[child] = name
            browser.detailChildBaseY[child] = child.y or 0
        end
    end
    browser.detailSections[name] = section
    return endY
end

function Children.removeDetailSection(browser, name)
    local section = browser.detailSections and browser.detailSections[name]
    if not section then return nil end
    for _, child in ipairs(section.children or {}) do
        browser.detailPanel:removeChild(child)
        browser.detailChildBaseY[child] = nil
        browser.detailChildSections[child] = nil
    end
    browser.detailSections[name] = nil
    return section
end

function Children.shiftDetailSectionsAfter(browser, order, delta)
    if delta == 0 then return end
    for _, section in pairs(browser.detailSections or {}) do
        if section.order > order then
            section.startY = section.startY + delta
            section.endY = section.endY + delta
            for _, child in ipairs(section.children or {}) do
                local baseY = browser.detailChildBaseY[child]
                if baseY ~= nil then browser.detailChildBaseY[child] = baseY + delta end
            end
        end
    end
end

function Children.removeDetailChildren(detailPanel)
    for _, child in ipairs(collectDetailChildren(detailPanel)) do
        if child then
            detailPanel:removeChild(child)
        end
    end
end

function Children.captureDetailChildPositions(browser)
    browser.detailChildBaseY = {}
    for _, child in ipairs(collectDetailChildren(browser.detailPanel)) do
        local fallbackY = child.y or 0
        browser.detailChildBaseY[child] = ObjectAccess.invokeMethod(child, "getY", fallbackY)
    end
end

function Children.applyDetailScrollOffset(browser)
    for child, baseY in pairs(browser.detailChildBaseY or {}) do
        local targetY = baseY - browser.detailScrollY
        local ok = ObjectAccess.call(child, "setY", targetY)
        if not ok then child.y = targetY end
    end
    if browser.updateDetailSearchEntries then
        browser:updateDetailSearchEntries()
    end
end

return Children
