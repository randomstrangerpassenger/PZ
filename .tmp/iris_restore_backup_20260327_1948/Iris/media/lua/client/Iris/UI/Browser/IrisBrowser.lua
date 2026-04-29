require "Iris/UI/Wiki/IrisWikiPanel"

local IrisBrowser = {}
IrisBrowser.instance = nil

function IrisBrowser.getOrCreate()
    if IrisBrowser.instance then
        return IrisBrowser.instance
    end

    local width = 820
    local height = 560
    local x = math.floor((getCore():getScreenWidth() - width) / 2)
    local y = math.floor((getCore():getScreenHeight() - height) / 2)

    local panel = IrisWikiPanel:new(x, y, width, height)
    panel:initialise()
    panel:instantiate()
    panel:setVisible(false)

    IrisBrowser.instance = panel
    return panel
end

function IrisBrowser.show()
    local panel = IrisBrowser.getOrCreate()
    panel:addToUIManager()
    panel:setVisible(true)
    return panel
end

function IrisBrowser.showItem(itemId)
    local panel = IrisBrowser.show()
    panel:applyFilter("")
    panel:selectItem(itemId)
    return panel
end

function IrisBrowser.toggle()
    local panel = IrisBrowser.getOrCreate()
    if panel:getIsVisible() then
        panel:setVisible(false)
        panel:removeFromUIManager()
    else
        IrisBrowser.show()
    end
end

_G.IrisBrowser = IrisBrowser

return IrisBrowser
