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

local IrisBrowserDetail = {}

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

local function removeDetailChildren(detailPanel)
    for _, child in ipairs(collectDetailChildren(detailPanel)) do
        if child then
            detailPanel:removeChild(child)
        end
    end
end

local function addMultilineLabels(panel, text, x, yOffset, height, r, g, b, font)
    for line in text:gmatch("[^\n]+") do
        local lineLabel = ISLabel:new(x, yOffset, height, line, r, g, b, 1, font, true)
        panel:addChild(lineLabel)
        yOffset = yOffset + height
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
        local metaLabel = ISLabel:new(10, yOffset, 18, line, r, g, b, 1, UIFont.Small, true)
        panel:addChild(metaLabel)
        yOffset = yOffset + 16
    end
    return yOffset
end

function IrisBrowserDetail.install(IrisBrowser, context)
    local safeRequire = context.safeRequire
    local tr = context.tr

    function IrisBrowser:showDetail(fullType)
        removeDetailChildren(self.detailPanel)

        if not fullType then
            return
        end

        local IrisBrowserData = BrowserBase.getBrowserData(context)
        local IrisWikiSections = BrowserBase.getWikiSections(context)
        local item = IrisBrowserData and IrisBrowserData.getItem(fullType)

        if not item then
            local errorLabel = ISLabel:new(10, 10, 20, tr("Iris_UI_ItemInfoNotFound", "Item information not found"), 0.8, 0.3, 0.3, 1, UIFont.Medium, true)
            self.detailPanel:addChild(errorLabel)
            return
        end

        local yOffset = 10 - self.detailScrollY
        local displayName = resolveItemDisplayName(item, fullType)

        local nameLabel = ISLabel:new(10, yOffset, 25, displayName, 0.6, 0.9, 1.0, 1.0, UIFont.Medium, true)
        self.detailPanel:addChild(nameLabel)
        yOffset = yOffset + 30

        if IrisWikiSections and IrisWikiSections.renderCoreInfoSection then
            local coreInfo = IrisWikiSections.renderCoreInfoSection(item)
            if coreInfo and coreInfo ~= "" then
                local coreLabel = ISLabel:new(10, yOffset, 18, coreInfo, 0.7, 0.85, 0.9, 1, UIFont.Medium, true)
                self.detailPanel:addChild(coreLabel)
                yOffset = yOffset + 22
            end
        end

        local IrisAPI = nil
        local apiOk, apiResult = safeRequire("Iris/IrisAPI")
        if apiOk then IrisAPI = apiResult end

        if IrisAPI and IrisAPI.Description and IrisAPI.Description.getDescription then
            local descOk, descText = ProtectedCall.data(function() return IrisAPI.Description.getDescription(fullType, nil) end)
            if descOk then
                yOffset = addSeparatedMultilineSection(self.detailPanel, descText, yOffset, 0.85, 0.85, 0.85)
            end
        end

        if IrisWikiSections and IrisWikiSections.renderLayer3Section then
            local layer3Text = IrisWikiSections.renderLayer3Section(item)
            yOffset = addSeparatedMultilineSection(self.detailPanel, layer3Text, yOffset, 0.92, 0.92, 0.92)
        end

        yOffset = InteractionRenderer.render(self, IrisBrowser, fullType, item, yOffset, {
            safeRequire = safeRequire,
            tr = tr,
            IrisAPI = IrisAPI,
        })

        yOffset = addVariantList(self, IrisBrowser, IrisBrowserData, fullType, yOffset)

        if IrisWikiSections and IrisWikiSections.renderMetaInfoSection then
            local metaInfo = IrisWikiSections.renderMetaInfoSection(item)
            yOffset = addMetaInfoSection(self.detailPanel, metaInfo, yOffset)
        end

        self.detailContentHeight = yOffset + self.detailScrollY + 20
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

        if self.currentSelectedFullType then
            self:showDetail(self.currentSelectedFullType)
        end
    end

    function IrisBrowser:onToggleRecipeSection(button)
        local expandKey = button.expandKey
        if not expandKey then return end

        self.recipeExpandedByFullType[expandKey] = not (self.recipeExpandedByFullType[expandKey] == true)
        self:showDetail(self.currentSelectedFullType)
    end
end

return IrisBrowserDetail
