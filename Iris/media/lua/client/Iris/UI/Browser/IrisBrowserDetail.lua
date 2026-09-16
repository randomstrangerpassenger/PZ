--[[
    IrisBrowserDetail.lua

    Detail panel rendering and scrolling for IrisBrowser.
]]

require "ISUI/ISButton"
require "ISUI/ISLabel"

local InteractionRenderer = require("Iris/UI/Browser/IrisBrowserInteractionRenderer")
local BrowserBase = require("Iris/UI/Browser/IrisBrowserBase")
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local Theme = require("Iris/UI/Browser/IrisBrowserTheme")
local ObjectAccess = require("Iris/Util/IrisObjectAccess")
local ItemAccess = require("Iris/Util/IrisItemAccess")
local DetailViewModel = require("Iris/UI/Detail/IrisItemDetailViewModel")
local DetailPresentation = require("Iris/UI/Detail/IrisItemDetailPresentation")
local TextLayout = require("Iris/UI/Detail/IrisTextLayout")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local InteractionState = require("Iris/UI/Browser/IrisBrowserInteractionState")

local TargetGroupView = require("Iris/UI/Detail/IrisTargetGroupView")

local IrisBrowserDetail = {}

local DetailChildren = require("Iris/UI/Browser/IrisDetailChildren")
local removeDetailChildren = DetailChildren.removeDetailChildren
local captureDetailChildPositions = DetailChildren.captureDetailChildPositions
local applyDetailScrollOffset = DetailChildren.applyDetailScrollOffset
local snapshotDetailChildren = DetailChildren.snapshotDetailChildren
local captureDetailSection = DetailChildren.captureDetailSection
local removeDetailSection = DetailChildren.removeDetailSection
local shiftDetailSectionsAfter = DetailChildren.shiftDetailSectionsAfter

local function addMultilineLabels(panel, text, x, yOffset, height, r, g, b, font)
    local availableWidth = math.max(1, panel.width - x - 10)
    for _, line in ipairs(TextLayout.wrapLines(text, availableWidth, font)) do
        if line == "" then
            yOffset = yOffset + math.max(4, math.floor(height * 0.55))
        else
            local lineLabel = ISLabel:new(x, yOffset, height, line, r, g, b, 1, font, true)
            panel:addChild(lineLabel)
            yOffset = yOffset + height
        end
    end
    return yOffset
end

local function addSeparatedMultilineSection(panel, text, yOffset, r, g, b)
    if not text or text == "" then
        return yOffset
    end

    yOffset = yOffset + 5
    local sepLabel = ISLabel:new(10, yOffset, 14, "────────────────────────", 0.3, 0.4, 0.5, 1, UIFont.Medium, true)
    panel:addChild(sepLabel)
    yOffset = yOffset + 20
    yOffset = addMultilineLabels(panel, text, 10, yOffset, 18, r, g, b, UIFont.Medium)
    return yOffset + 10
end

local function resolveItemDisplayName(item, fallback)
    return ItemAccess.getDisplayName(item, fallback)
end

local function addVariantList(browser, browserClass, IrisBrowserData, fullType, yOffset)
    local variants = browser.currentSelectedVariants
    if not variants or #variants <= 1 then
        return yOffset
    end

    local expandKey = fullType .. "_variants"
    local expanded = browser.recipeExpandedByFullType[expandKey] == true
    local arrow = expanded and " [-]" or " [+]"
    local headerText = "Variants (" .. #variants .. ")" .. arrow

    local btn = ISButton:new(10, yOffset, 250, 18, headerText, browser, browserClass.onToggleRecipeSection)
    btn:initialise()
    btn.expandKey = expandKey
    btn.backgroundColor = Theme.color("transparent")
    btn.backgroundColorMouseOver = Theme.color("sectionButtonHover")
    btn.borderColor = Theme.color("transparent")
    btn.textColor = Theme.color("variantButtonText")
    browser.detailPanel:addChild(btn)
    yOffset = yOffset + 20

    if expanded then
        for _, variantFullType in ipairs(variants) do
            local variantItem = IrisBrowserData and IrisBrowserData.getItem(variantFullType)
            local variantDisplayName = resolveItemDisplayName(variantItem, variantFullType)

            local prefix = (variantFullType == fullType) and "▸ " or "  "
            local lbl = ISLabel:new(20, yOffset, 16, prefix .. variantDisplayName .. " [" .. variantFullType .. "]", 0.75, 0.85, 0.95, 1, UIFont.Small, true)
            browser.detailPanel:addChild(lbl)
            yOffset = yOffset + 16
        end
    end

    return yOffset
end

local function addMetaInfoSection(panel, metaInfo, yOffset)
    if not metaInfo or metaInfo == "" then
        return yOffset
    end

    yOffset = yOffset + 5
    for line in metaInfo:gmatch("[^\n]+") do
        local r, g, b = 0.6, 0.6, 0.6
        if line:find("───") then
            r, g, b = 0.3, 0.4, 0.5
        end
        yOffset = addMultilineLabels(panel, line, 10, yOffset, 16, r, g, b, UIFont.Small)
    end
    return yOffset
end

function IrisBrowserDetail.install(IrisBrowser, context)
    local safeRequire = context.safeRequire
    local tr = context.tr

    function IrisBrowser:updateDetailSearchEntries()
        if not self.detailPanel then return end
        local panelX = self.detailPanel.x or 0
        local panelY = self.detailPanel.y or 0
        local panelHeight = self.detailPanel.height or 0
        local slots = {"interactionSearchEntry", "evolvedSearchEntry"}
        for _, slot in ipairs(slots) do
            local entry = self[slot]
            if entry then
                local visible = entry.irisDetailActive == true
                if visible then
                    local targetY = panelY + (entry.irisDetailY or 0) -
                        (self.detailScrollY or 0)
                    entry:setX(panelX + (entry.irisDetailX or 0))
                    entry:setY(targetY)
                    entry:setWidth(entry.irisDetailWidth or entry.width)
                    visible = targetY + entry.height > panelY and
                        targetY < panelY + panelHeight
                end
                if entry:getIsVisible() ~= visible then
                    entry:setVisible(visible)
                end
            end
        end
    end

    local function renderSection(browser, name, order, yOffset, render)
        local before = snapshotDetailChildren(browser.detailPanel)
        local endY = render(yOffset)
        return captureDetailSection(browser, name, order, before, yOffset, endY)
    end

    local function renderLayer3(browser, yOffset)
        local state = browser.currentDetailContext
        local sections = state and state.wikiSections
        local model = browser.currentDetailModel
        if not sections or not sections.renderLayer3Section or not model then return yOffset end
        local units = sections.getLayer3Records(model)
        for index, unit in ipairs(units) do
            yOffset = yOffset + 7
            addMultilineLabels(browser.detailPanel, "•", 10, yOffset, 18,
                0.92, 0.92, 0.92, UIFont.Medium)
            yOffset = TargetGroupView.render(browser.detailPanel, unit, 25, yOffset, UIFont.Medium,
                model.locale, browser.targetGroupState, tostring(index), function()
                    browser:refreshDetailSection("layer3")
                end, function(text, x, y)
                    return addMultilineLabels(browser.detailPanel, text, x, y, 18, 0.92, 0.92, 0.92, UIFont.Medium)
                end)
        end
        return yOffset
    end

    local function renderInteraction(browser, yOffset)
        local state = browser.currentDetailContext
        if not state or not browser.currentDetailModel then return yOffset end
        return InteractionRenderer.render(
            browser, IrisBrowser, state.fullType, state.item, yOffset, {
                safeRequire = safeRequire,
                tr = tr,
                IrisAPI = state.api,
                model = browser.currentDetailModel,
                browserGeneration = state.browserGeneration,
            }
        )
    end

    local function renderVariants(browser, yOffset)
        local state = browser.currentDetailContext
        if not state then return yOffset end
        return addVariantList(
            browser, IrisBrowser, state.browserData, state.fullType, yOffset
        )
    end

    function IrisBrowser:refreshDetailSection(name)
        local renderers = {
            layer3 = renderLayer3,
            interaction = renderInteraction,
            variants = renderVariants,
        }
        local render = renderers[name]
        local previous = self.detailSections and self.detailSections[name]
        if not render or not previous or not self.currentDetailModel then
            self:showDetail(self.currentSelectedFullType, true)
            return
        end
        local startY, oldEnd, order = previous.startY, previous.endY, previous.order
        removeDetailSection(self, name)
        local newEnd = renderSection(self, name, order, startY, function(y)
            return render(self, y)
        end)
        local delta = newEnd - oldEnd
        shiftDetailSectionsAfter(self, order, delta)
        self.detailContentHeight = self.detailContentHeight + delta
        local maxScroll = math.max(0, self.detailContentHeight - self.detailPanel.height)
        self.detailScrollY = math.max(0, math.min(self.detailScrollY, maxScroll))
        applyDetailScrollOffset(self)
    end

    function IrisBrowser:rebuildDetailContent(fullType)
        removeDetailChildren(self.detailPanel)
        self.detailChildBaseY = {}
        self.detailChildSections = {}
        self.detailSections = {}
        self.currentDetailModel = nil
        self.currentDetailContext = nil
        self.detailBuiltFullType = fullType
        self.detailBuiltLocale = TranslationResolver.getLangKey("EN")
        for _, slot in ipairs({"interactionSearchEntry", "evolvedSearchEntry"}) do
            local entry = self[slot]
            if entry then entry.irisDetailActive = false end
        end

        if not fullType then
            self.detailContentHeight = 0
            self:updateDetailSearchEntries()
            return
        end

        local IrisBrowserData = BrowserBase.getBrowserData(context)
        local IrisWikiSections = BrowserBase.getWikiSections(context)
        local item = IrisBrowserData and IrisBrowserData.getItem(fullType)

        if not item then
            local errorLabel = ISLabel:new(10, 10, 20, tr("Iris_UI_ItemInfoNotFound", "Item information not found"), 0.8, 0.3, 0.3, 1, UIFont.Medium, true)
            self.detailPanel:addChild(errorLabel)
            self.detailContentHeight = 30
            captureDetailChildPositions(self)
            applyDetailScrollOffset(self)
            return
        end

        local model = DetailViewModel.fromItem(item)
        self.currentDetailModel = model
        if self.targetGroupRevision ~= model.revision then
            self.targetGroupRevision = model.revision
            self.targetGroupState = {}
        end
        self.currentDetailSemanticSnapshot = DetailPresentation.semanticSnapshot(model)
        self.detailBuiltLocale = model.locale
        local yOffset = 10
        local displayName = model.displayName

        local IrisAPI = nil
        local apiOk, apiResult = safeRequire("Iris/IrisAPI")
        if apiOk then IrisAPI = apiResult end
        local browserState = IrisBrowserData and IrisBrowserData.getBuildState and
            IrisBrowserData.getBuildState() or {generation = 0}
        self.currentDetailContext = {
            api = IrisAPI,
            browserData = IrisBrowserData,
            browserGeneration = browserState.generation,
            fullType = fullType,
            item = item,
            wikiSections = IrisWikiSections,
        }

        yOffset = renderSection(self, "identity", 1, yOffset, function(y)
            y = addMultilineLabels(self.detailPanel, displayName, 10, y, 25,
                0.6, 0.9, 1.0, UIFont.Medium) + 5
            if IrisWikiSections and IrisWikiSections.renderCoreInfoSection then
                local coreInfo = IrisWikiSections.renderCoreInfoSection(model)
                if coreInfo and coreInfo ~= "" then
                    y = addMultilineLabels(self.detailPanel, coreInfo, 10, y, 18,
                        0.7, 0.85, 0.9, UIFont.Medium) + 4
                end
            end
            if IrisAPI and IrisAPI.Description and IrisAPI.Description.getDescription then
                local descOk, descText = ProtectedCall.data(function()
                    return IrisAPI.Description.getDescription(fullType, nil, model.locale)
                end)
                if descOk then
                    y = addSeparatedMultilineSection(self.detailPanel, descText, y, 0.85, 0.85, 0.85)
                end
            end
            return y
        end)
        yOffset = renderSection(self, "layer3", 2, yOffset, function(y)
            return renderLayer3(self, y)
        end)
        yOffset = renderSection(self, "literature", 3, yOffset, function(y)
            if IrisWikiSections and IrisWikiSections.renderLiteratureSection then
                return addSeparatedMultilineSection(
                    self.detailPanel,
                    IrisWikiSections.renderLiteratureSection(model),
                    y,
                    0.85, 0.85, 0.85
                )
            end
            return y
        end)
        yOffset = renderSection(self, "interaction", 4, yOffset, function(y)
            return renderInteraction(self, y)
        end)
        yOffset = renderSection(self, "variants", 5, yOffset, function(y)
            return renderVariants(self, y)
        end)
        yOffset = renderSection(self, "meta", 6, yOffset, function(y)
            if IrisWikiSections and IrisWikiSections.renderMetaInfoSection then
                return addMetaInfoSection(
                    self.detailPanel,
                    IrisWikiSections.renderMetaInfoSection(model),
                    y
                )
            end
            return y
        end)

        self.detailContentHeight = yOffset + 20
        self.detailBuiltWidth = self.detailPanel.width
        local maxScroll = math.max(0, self.detailContentHeight - self.detailPanel.height)
        self.detailScrollY = math.max(0, math.min(self.detailScrollY, maxScroll))
        captureDetailChildPositions(self)
        applyDetailScrollOffset(self)
    end

    function IrisBrowser:showDetail(fullType, forceRebuild)
        local locale = TranslationResolver.getLangKey("EN")
        if self.detailBuiltFullType ~= fullType or self.detailBuiltLocale ~= locale then
            self.detailScrollY = 0
            self.targetGroupState = {}
        end
        local IrisBrowserData = BrowserBase.getBrowserData(context)
        local buildState = IrisBrowserData and IrisBrowserData.getBuildState and
            IrisBrowserData.getBuildState() or {generation = 0}
        if not forceRebuild and fullType and self.detailBuiltFullType == fullType and
            self.detailBuiltLocale == locale and self.detailBuiltGeneration == buildState.generation and
            self.detailBuiltWidth == self.detailPanel.width and self.currentDetailModel then
            applyDetailScrollOffset(self)
            return
        end
        self.detailBuiltGeneration = buildState.generation
        self:rebuildDetailContent(fullType)
    end

    function IrisBrowser:onDetailMouseWheel(del)
        if not self.detailPanel then return end

        local scrollAmount = 30
        local maxScroll = math.max(0, self.detailContentHeight - self.detailPanel.height)

        self.detailScrollY = self.detailScrollY + (del * scrollAmount)

        if self.detailScrollY < 0 then
            self.detailScrollY = 0
        elseif self.detailScrollY > maxScroll then
            self.detailScrollY = maxScroll
        end

        applyDetailScrollOffset(self)
    end

    function IrisBrowser:onToggleRecipeSection(button)
        local expandKey = button.expandKey
        if not expandKey then return end

        self.recipeExpandedByFullType[expandKey] = not (self.recipeExpandedByFullType[expandKey] == true)
        self:refreshDetailSection("variants")
    end

    function IrisBrowser:onToggleInteractionDensity(button)
        if not button.interactionStateKey then return end
        InteractionState.toggleFull(self, button.interactionStateKey)
        self:refreshDetailSection("interaction")
    end

    function IrisBrowser:onToggleFixedRecipeInteraction(button)
        if not button.interactionStateKey then return end
        InteractionState.toggleRecipe(self, button.interactionStateKey)
        self:refreshDetailSection("interaction")
    end

    function IrisBrowser:onToggleEvolvedInteraction(button)
        if not button.evolvedInteractionStateKey then return end
        InteractionState.toggleEvolved(self, button.evolvedInteractionStateKey)
        self:refreshDetailSection("interaction")
    end

    function IrisBrowser:onToggleInteractionRequirements(button)
        if not button.interactionStateKey or not button.interactionIdentity then return end
        InteractionState.toggleRequirements(
            self, button.interactionStateKey, button.interactionIdentity, button.defaultExpanded
        )
        self:refreshDetailSection("interaction")
    end
end

return IrisBrowserDetail
