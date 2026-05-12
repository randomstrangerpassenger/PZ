--[[
    IrisBrowserInteractionRenderer.lua

    Interaction/usecase rendering for IrisBrowser detail panel.
]]

require "ISUI/ISButton"
require "ISUI/ISLabel"

local IrisBrowserInteractionRenderer = {}
local RequirementPolicy = require("Iris/UI/Browser/IrisRequirementPolicy")
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local Theme = require("Iris/UI/Browser/IrisBrowserTheme")

local function collectRecipeInteractions(fullType, item, IrisAPI, ucDescData)
    local interactionItems = {}
    local recipeNameSet = {}
    local hasOfflineRecipes = false

    if ucDescData and ucDescData[fullType] then
        local ucDesc = ucDescData[fullType]
        if ucDesc and ucDesc.lines then
            for _, line in ipairs(ucDesc.lines) do
                if line.surface == "recipe_ui" or line.surface == "both" then
                    local recipeName = line.recipe_translated_name
                        or line.recipe_original_name
                        or line.display_text
                    if not recipeNameSet[recipeName] then
                        recipeNameSet[recipeName] = true
                        hasOfflineRecipes = true
                        table.insert(interactionItems, {
                            type = "recipe",
                            name = recipeName,
                            label_key = line.label_key,
                            sortKey = "1_" .. (line.label_key or ""),
                            recipe_nav_ref = line.recipe_nav_ref,
                            recipe_requirements = line.recipe_requirements,
                        })
                    end
                end
            end
        end
    end

    if not hasOfflineRecipes then
        local recipeList = {}
        if IrisAPI and IrisAPI.Index and IrisAPI.Index.getRecipeConnectionsForItem then
            local ok, list = ProtectedCall.data(function() return IrisAPI.Index.getRecipeConnectionsForItem(item) end)
            if ok and list then recipeList = list end
        end
        for _, e in ipairs(recipeList) do
            local name = tostring(e.recipe or "Unknown")
            if not recipeNameSet[name] then
                recipeNameSet[name] = true
                local trName = nil
                if getText then
                    local trKey = "Recipe_" .. name:gsub(" ", "_")
                    local trOk, trResult = ProtectedCall.engine(getText, trKey)
                    if trOk and trResult and trResult ~= trKey then
                        trName = trResult
                    end
                end
                local fallbackReqs = nil
                if ucDescData and ucDescData._requirementsLookup then
                    fallbackReqs = ucDescData._requirementsLookup[name]
                end
                table.insert(interactionItems, {
                    type = "recipe",
                    name = trName or name,
                    sortKey = "1_" .. name,
                    recipe_nav_ref = {
                        original_name = name,
                        translated_name = trName,
                        category = nil,
                    },
                    recipe_requirements = fallbackReqs,
                })
            end
        end
    end

    return interactionItems
end

local function collectCapabilityInteractions(fullType, IrisAPI, tr)
    local capabilityList = {}
    if IrisAPI and IrisAPI.UseCases and IrisAPI.UseCases.getCapabilities then
        local ok, caps = ProtectedCall.data(function() return IrisAPI.UseCases.getCapabilities(fullType) end)
        if ok and caps then capabilityList = caps end
    end

    local capabilityLabelMap = {
        can_extinguish_fire = "Iris_Cap_ExtinguishFire",
        can_add_generator_fuel = "Iris_Cap_AddGeneratorFuel",
        can_scrap_moveables = "Iris_Cap_ScrapMoveables",
        can_open_canned_food = "Iris_Cap_OpenCannedFood",
        can_stitch_wound = "Iris_Cap_StitchWound",
        can_remove_embedded_object = "Iris_Cap_RemoveEmbeddedObject",
        can_attach_weapon_mod = "Iris_Cap_AttachWeaponMod",
    }

    local interactionItems = {}
    for _, capId in ipairs(capabilityList) do
        local labelKey = capabilityLabelMap[capId]
        local displayName = labelKey and tr(labelKey, capId) or capId
        table.insert(interactionItems, {type = "rightclick", name = displayName, sortKey = "0_" .. displayName})
    end
    return interactionItems
end

function IrisBrowserInteractionRenderer.render(browser, browserClass, fullType, item, yOffset, deps)
    local safeRequire = deps.safeRequire
    local tr = deps.tr
    local IrisAPI = deps.IrisAPI

    local ucDescData = nil
    local ucOk, ucResult = safeRequire("Iris/Data/IrisUseCaseDescriptions")
    if ucOk and ucResult then ucDescData = ucResult end

    local interactionItems = collectRecipeInteractions(fullType, item, IrisAPI, ucDescData)
    local capabilityItems = collectCapabilityInteractions(fullType, IrisAPI, tr)
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
