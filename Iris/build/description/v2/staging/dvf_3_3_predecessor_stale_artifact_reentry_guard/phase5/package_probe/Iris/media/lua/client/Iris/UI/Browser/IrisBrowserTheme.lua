--[[
    IrisBrowserTheme.lua

    Shared chrome colors and layout ratios for Iris Browser UI modules.
]]

local IrisBrowserTheme = {}

IrisBrowserTheme.COLUMNS = {
    category = 0.15,
    subcategory = 0.15,
    items = 0.15,
    detail = 0.55,
}

IrisBrowserTheme.COLORS = {
    panelBackground = {r=0.1, g=0.1, b=0.12, a=0.95},
    panelBorder = {r=0.3, g=0.4, b=0.5, a=1},
    closeButtonBorder = {r=0.5, g=0.5, b=0.5, a=0.5},
    detailPanelBackground = {r=0.05, g=0.08, b=0.1, a=0.8},
    detailPanelBorder = {r=0.3, g=0.4, b=0.5, a=0.5},
    transparent = {r=0, g=0, b=0, a=0},
    sectionButtonHover = {r=0.2, g=0.3, b=0.4, a=0.3},
    variantButtonText = {r=0.8, g=0.9, b=1.0, a=1},
    interactionButtonText = {r=0.9, g=0.9, b=0.9, a=1},
    navButtonHover = {r=0.3, g=0.5, b=0.7, a=0.4},
    navButtonBorder = {r=0.4, g=0.5, b=0.6, a=0.5},
    navButtonText = {r=0.5, g=0.8, b=1.0, a=1},
    detailScrollTrack = {r=0.1, g=0.12, b=0.15, a=0.5},
    detailScrollThumb = {r=0.4, g=0.5, b=0.7, a=0.7},
}

function IrisBrowserTheme.color(name)
    local color = IrisBrowserTheme.COLORS[name]
    if not color then
        return {r=1, g=1, b=1, a=1}
    end
    return {r=color.r, g=color.g, b=color.b, a=color.a}
end

function IrisBrowserTheme.drawRect(panel, x, y, width, height, colorName)
    local color = IrisBrowserTheme.COLORS[colorName]
    if not color then
        return
    end
    panel:drawRect(x, y, width, height, color.a, color.r, color.g, color.b)
end

return IrisBrowserTheme
