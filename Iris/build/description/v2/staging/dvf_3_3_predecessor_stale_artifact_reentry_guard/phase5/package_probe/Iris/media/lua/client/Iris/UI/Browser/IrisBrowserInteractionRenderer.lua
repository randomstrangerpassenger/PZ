--[[
    IrisBrowserInteractionRenderer.lua

    Interaction/usecase rendering for IrisBrowser detail panel.

    Change 9b: interaction *collection* moved to IrisBrowserInteractionCollector;
    this module keeps UI row rendering only and delegates collection. Public
    interface (IrisBrowserInteractionRenderer.render) and callers unchanged.
]]

require "ISUI/ISButton"
require "ISUI/ISLabel"

local IrisBrowserInteractionRenderer = {}
local RequirementPolicy = require("Iris/UI/Browser/IrisRequirementPolicy")
local Theme = require("Iris/UI/Browser/IrisBrowserTheme")
local Collector = require("Iris/UI/Browser/IrisBrowserInteractionCollector")

function IrisBrowserInteractionRenderer.render(browser, browserClass, fullType, item, yOffset, deps)
    local safeRequire = deps.safeRequire
    local tr = deps.tr
    local IrisAPI = deps.IrisAPI

    local ucDescData = nil
    local ucOk, ucResult = safeRequire("Iris/Data/IrisUseCaseDescriptions")
    if ucOk and ucResult then ucDescData = ucResult end

    local interactionItems = Collector.collectRecipeInteractions(fullType, item, IrisAPI, ucDescData)
    local capabilityItems = Collector.collectCapabilityInteractions(fullType, IrisAPI, tr)
    for _, capabilityItem in ipairs(capabilityItems) do
        table.insert(interactionItems, capabilityItem)
    end

    local totalCount = #interactionItems
    if totalCount <= 0 then
        return yOffset
    end

    table.sort(interactionItems, function(a, b) return a.sortKey < b.sortKey end)

    local expandKey = fullType .. "_interactions"
    local expanded = browser.recipeExpandedByFullType[expandKey] == true
    local arrow = expanded and " [-]" or " [+]"
    local interactionLabel = tr("Iris_Detail_Interaction", "Interactions")
    local headerText = interactionLabel .. " (" .. tostring(totalCount) .. ")" .. arrow

    local btn = ISButton:new(10, yOffset, 250, 18, headerText, browser, browserClass.onToggleRecipeSection)
    btn:initialise()
    btn.expandKey = expandKey
    btn.backgroundColor = Theme.color("transparent")
    btn.backgroundColorMouseOver = Theme.color("sectionButtonHover")
    btn.borderColor = Theme.color("transparent")
    btn.textColor = Theme.color("interactionButtonText")
    browser.detailPanel:addChild(btn)
    yOffset = yOffset + 20

    if not expanded then
        return yOffset
    end

    local prefixRecipe = tr("Iris_Prefix_Recipe", "[Recipe]")
    local prefixRightClick = tr("Iris_Prefix_RightClick", "[Action]")

    for _, itm in ipairs(interactionItems) do
        local r, g, b = 0.85, 0.85, 0.85
        local displayStr
        if itm.type == "rightclick" then
            r, g, b = 0.7, 0.9, 0.7
            displayStr = prefixRightClick .. " " .. itm.name
        else
            displayStr = prefixRecipe .. " " .. itm.name
        end

        local textW = getTextManager():MeasureStringX(UIFont.Small, displayStr)
        local lbl = ISLabel:new(20, yOffset, 16, displayStr, r, g, b, 1, UIFont.Small, true)
        browser.detailPanel:addChild(lbl)

        local curX = 20 + textW + 4

        if itm.recipe_nav_ref then
            local btnText = "[" .. tr("Iris_Nav_Go", "Go") .. "]"
            local btnW = getTextManager():MeasureStringX(UIFont.Small, btnText) + 8
            local goBtn = ISButton:new(curX, yOffset, btnW, 16,
                btnText, browser, browserClass.onRecipeGoToCrafting)
            goBtn:initialise()
            goBtn.recipe_nav_ref = itm.recipe_nav_ref
            goBtn.backgroundColor = Theme.color("transparent")
            goBtn.backgroundColorMouseOver = Theme.color("navButtonHover")
            goBtn.borderColor = Theme.color("navButtonBorder")
            goBtn.textColor = Theme.color("navButtonText")
            browser.detailPanel:addChild(goBtn)
            curX = curX + btnW + 4
        end

        if itm.recipe_requirements then
            local player = getSpecificPlayer(browser.playerNum or 0)
            for ri, req in ipairs(itm.recipe_requirements) do
                if ri > 1 then
                    local sep = ", "
                    local sepW = getTextManager():MeasureStringX(UIFont.Small, sep)
                    local sepLbl = ISLabel:new(curX, yOffset, 16, sep, 0.5, 0.5, 0.5, 0.6, UIFont.Small, true)
                    browser.detailPanel:addChild(sepLbl)
                    curX = curX + sepW
                end
                local color = RequirementPolicy.evalColor(req.check, player)
                local reqDisplay = RequirementPolicy.displayText(req, color, tr)
                local reqW = getTextManager():MeasureStringX(UIFont.Small, reqDisplay)
                local reqLbl = ISLabel:new(curX, yOffset, 16, reqDisplay, color.r, color.g, color.b, color.a, UIFont.Small, true)
                browser.detailPanel:addChild(reqLbl)
                curX = curX + reqW
            end
        end

        yOffset = yOffset + 16
    end

    return yOffset
end

return IrisBrowserInteractionRenderer
