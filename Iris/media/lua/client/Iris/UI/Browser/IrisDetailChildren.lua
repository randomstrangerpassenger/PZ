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

function Children.removeDetailChildren(detailPanel)
    for _, child in ipairs(collectDetailChildren(detailPanel)) do
        if child then
            detailPanel:removeChild(child)
        end
    end
end

function Children.captureDetailChildPositions(browser)
    browser.detailChildBaseY = {}
    for _, child in ipairs(collectLuaDetailChildren(browser.detailPanel)) do
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
