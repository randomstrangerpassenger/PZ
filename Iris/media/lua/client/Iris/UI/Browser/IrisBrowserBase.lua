--[[
    IrisBrowserBase.lua

    Shared helpers for IrisBrowser modules. This module owns dependency access
    and panel lifecycle helpers only; it does not change Browser layout.
]]

local IrisBrowserBase = {}

function IrisBrowserBase.getBrowserData(context)
    if context and context.ensureDeps then
        context.ensureDeps()
    end
    if context and context.getBrowserData then
        return context.getBrowserData()
    end
    return nil
end

function IrisBrowserBase.getWikiSections(context)
    if context and context.ensureDeps then
        context.ensureDeps()
    end
    if context and context.getWikiSections then
        return context.getWikiSections()
    end
    return nil
end

function IrisBrowserBase.ensureBrowserDataBuilt(context, debug)
    local IrisBrowserData = IrisBrowserBase.getBrowserData(context)
    if IrisBrowserData and not IrisBrowserData._built then
        if debug then debug("[IrisBrowser] Building IrisBrowserData...") end
        IrisBrowserData.build()
        if debug then
            debug("[IrisBrowser] Build complete, _built = " .. tostring(IrisBrowserData._built))
        end
    end
    return IrisBrowserData
end

function IrisBrowserBase.closeVisibleInstance(IrisBrowser)
    if IrisBrowser._instance and IrisBrowser._instance:isVisible() then
        IrisBrowser._instance:close()
    end
end

function IrisBrowserBase.getCenteredPanelBounds()
    local screenW = getCore():getScreenWidth()
    local screenH = getCore():getScreenHeight()
    local panelW = math.min(1200, screenW - 100)
    local panelH = math.min(700, screenH - 100)
    local x = (screenW - panelW) / 2
    local y = (screenH - panelH) / 2
    return x, y, panelW, panelH
end

function IrisBrowserBase.createCenteredPanel(IrisBrowser, debug)
    local x, y, panelW, panelH = IrisBrowserBase.getCenteredPanelBounds()
    if debug then
        debug("[IrisBrowser] Creating browser panel: " .. panelW .. "x" .. panelH)
    end

    local browser = IrisBrowser:new(x, y, panelW, panelH)
    browser:initialise()
    browser:instantiate()
    browser:addToUIManager()
    browser:setVisible(true)
    browser:bringToTop()

    return browser
end

return IrisBrowserBase
