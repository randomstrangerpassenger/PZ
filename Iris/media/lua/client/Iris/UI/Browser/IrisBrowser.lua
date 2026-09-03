--[[
    IrisBrowser.lua - Iris category browser entrypoint

    Owns the browser panel lifecycle and shared dependencies. Layout,
    detail rendering, recipe navigation, and list/search behavior are
    installed from split Browser modules.
]]

require "ISUI/ISPanel"

local IrisBrowser = ISPanel:derive("IrisBrowser")
local ItemAccess = require("Iris/Util/IrisItemAccess")
local BrowserBase = require("Iris/UI/Browser/IrisBrowserBase")
local Theme = require("Iris/UI/Browser/IrisBrowserTheme")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local debug = bootstrap.debug
local isDebugEnabled = bootstrap.isDebugEnabled
local warn = bootstrap.warn
local logError = bootstrap.logError

local IrisBrowserData = nil
local IrisWikiSections = nil

local function ensureDeps()
    if not IrisBrowserData then
        local ok, result = safeRequire("Iris/UI/Browser/IrisBrowserData")
        if ok then IrisBrowserData = result end
    end
    if not IrisWikiSections then
        local ok, result = safeRequire("Iris/UI/Wiki/IrisWikiSections")
        if ok then IrisWikiSections = result end
    end
end

local BrowserModuleContext = {
    debug = debug,
    warn = warn,
    logError = logError,
    safeRequire = safeRequire,
    isDebugEnabled = isDebugEnabled,
    ensureDeps = ensureDeps,
    getBrowserData = function() return IrisBrowserData end,
    getWikiSections = function() return IrisWikiSections end,
    tr = TranslationResolver.get,
}

local function installBrowserModule(moduleName)
    local ok, module = safeRequire(moduleName)
    if ok and module and module.install then
        module.install(IrisBrowser, BrowserModuleContext)
    else
        warn("[IrisBrowser] browser module install skipped: " .. tostring(moduleName))
    end
end

IrisBrowser._instance = nil

function IrisBrowser.openSearch()
    local debugEnabled = isDebugEnabled()
    debug("[IrisBrowser] ########## openSearch() START ##########")
    ensureDeps()

    if debugEnabled then
        debug("[IrisBrowser] IrisBrowserData exists = " .. tostring(IrisBrowserData ~= nil))
    end
    if debugEnabled and IrisBrowserData then
        local state = IrisBrowserData.getBuildState()
        debug("[IrisBrowser] BrowserData state=" .. tostring(state.state) ..
            " reason=" .. tostring(state.reason) ..
            " dependency=" .. tostring(state.dependency))
    end

    BrowserBase.ensureBrowserDataBuilt(
        BrowserModuleContext,
        debugEnabled and debug or nil
    )

    BrowserBase.closeVisibleInstance(IrisBrowser)

    local browser = BrowserBase.createCenteredPanel(
        IrisBrowser,
        debugEnabled and debug or nil
    )
    IrisBrowser._instance = browser
    debug("[IrisBrowser] ########## openSearch() END ##########")
end

function IrisBrowser.openForItem(item)
    ensureDeps()

    if not item then return end

    BrowserBase.ensureBrowserDataBuilt(BrowserModuleContext)

    BrowserBase.closeVisibleInstance(IrisBrowser)

    local browser = BrowserBase.createCenteredPanel(IrisBrowser)
    browser:selectItem(item)

    IrisBrowser._instance = browser
    if isDebugEnabled() then
        debug("[IrisBrowser] Opened for item: " .. tostring(ItemAccess.getFullType(item)))
    end
end

function IrisBrowser:new(x, y, width, height)
    local o = ISPanel:new(x, y, width, height)
    setmetatable(o, self)
    self.__index = self

    o.backgroundColor = Theme.color("panelBackground")
    o.borderColor = Theme.color("panelBorder")
    o.moveWithMouse = true

    o.currentCategory = nil
    o.currentSubcategory = nil
    o.currentSelectedFullType = nil
    o.currentSelectedVariants = nil
    o.recipeExpandedByFullType = {}

    o.detailScrollY = 0
    o.detailContentHeight = 0
    o.detailChildBaseY = {}
    o.detailBuiltFullType = nil
    o.detailBuiltLocale = nil
    o.detailBuiltGeneration = nil
    o.currentDetailModel = nil
    o._interactionStateOwner = nil
    o._interactionStateByItem = {}
    o._interactionActiveKey = nil
    o._evolvedInteractionStateOwner = nil
    o._evolvedInteractionStateByItem = {}
    o._evolvedInteractionActiveKey = nil

    return o
end

function IrisBrowser:initialise()
    ISPanel.initialise(self)
end

function IrisBrowser:update()
    ISPanel.update(self)
    self:refreshSearchOwner()
    self:refreshSearchInput()
end

function IrisBrowser:close()
    self:setVisible(false)
    self:removeFromUIManager()
    IrisBrowser._instance = nil
end

installBrowserModule("Iris/UI/Browser/IrisBrowserListController")
installBrowserModule("Iris/UI/Browser/IrisBrowserRecipeNav")
installBrowserModule("Iris/UI/Browser/IrisBrowserDetail")
installBrowserModule("Iris/UI/Browser/IrisBrowserLayout")

return IrisBrowser
