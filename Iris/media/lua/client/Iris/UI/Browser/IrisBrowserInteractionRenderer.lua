require "ISUI/ISButton"
require "ISUI/ISLabel"
require "ISUI/ISTextEntryBox"

local Collector = require("Iris/UI/Browser/IrisBrowserInteractionCollector")
local Policy = require("Iris/UI/Browser/IrisBrowserInteractionPolicy")
local Projection = require("Iris/UI/Browser/IrisBrowserInteractionProjection")
local RequirementPolicy = require("Iris/UI/Browser/IrisRequirementPolicy")
local State = require("Iris/UI/Browser/IrisBrowserInteractionState")
local Theme = require("Iris/UI/Browser/IrisBrowserTheme")

local IrisBrowserInteractionRenderer = {}

local function addLabel(browser, x, y, text, r, g, b)
    local label = ISLabel:new(x, y, 16, text, r, g, b, 1, UIFont.Small, true)
    browser.detailPanel:addChild(label)
    return label
end

local function headerText(projection, tr)
    local interaction = tr("Iris_Detail_Interaction", "Interactions")
    local recipe = tr("Iris_Interaction_SourceRecipe", "Recipe")
    local rightclick = tr("Iris_Interaction_SourceRightClick", "Right-click")
    return interaction .. " " .. tostring(projection.total) ..
        "  |  " .. recipe .. " " .. tostring(projection.recipeCount) ..
        "  |  " .. rightclick .. " " .. tostring(projection.rightclickCount)
end

local function renderRequirements(browser, row, yOffset, deps, state, stateKey)
    local requirements = row.recipe_requirements or {}
    if #requirements == 0 then return yOffset end
    local defaultExpanded = deps.projection.density ~= "dense"
    local expanded = state.requirements[row.identity]
    if expanded == nil then expanded = defaultExpanded end
    local marker = expanded and "[-] " or "[+] "
    local text = marker .. deps.tr("Iris_Interaction_Requirements", "Requirements") ..
        " " .. tostring(#requirements)
    local button = ISButton:new(28, yOffset, 180, 16, text, browser,
        deps.browserClass.onToggleInteractionRequirements)
    button:initialise()
    button.interactionStateKey = stateKey
    button.interactionIdentity = row.identity
    button.defaultExpanded = defaultExpanded
    button.backgroundColor = Theme.color("transparent")
    button.backgroundColorMouseOver = Theme.color("sectionButtonHover")
    button.borderColor = Theme.color("transparent")
    browser.detailPanel:addChild(button)
    yOffset = yOffset + 16
    if not expanded then return yOffset end

    local player = getSpecificPlayer(browser.playerNum or 0)
    for _, requirement in ipairs(requirements) do
        local color = RequirementPolicy.evalColor(requirement.check, player)
        local display = RequirementPolicy.displayText(requirement, color, deps.tr, deps.locale)
        addLabel(browser, 36, yOffset, "- " .. display, color.r, color.g, color.b)
        yOffset = yOffset + 16
    end
    return yOffset
end

local function renderRow(browser, row, yOffset, deps, state, stateKey)
    local prefix = row.source == "recipe"
        and deps.tr("Iris_Prefix_Recipe", "[Recipe]")
        or deps.tr("Iris_Prefix_RightClick", "[Action]")
    local r, g, b = 0.85, 0.85, 0.85
    if row.source == "rightclick" then r, g, b = 0.7, 0.9, 0.7 end
    if row.displayUnavailable then r, g, b = 0.75, 0.55, 0.35 end
    local display = prefix .. " " .. row.display
    addLabel(browser, 20, yOffset, display, r, g, b)
    local currentX = 24 + getTextManager():MeasureStringX(UIFont.Small, display)
    if row.recipe_nav_ref then
        local buttonText = "[" .. deps.tr("Iris_Nav_Go", "Go") .. "]"
        local width = getTextManager():MeasureStringX(UIFont.Small, buttonText) + 8
        local button = ISButton:new(currentX, yOffset, width, 16, buttonText, browser,
            deps.browserClass.onRecipeGoToCrafting)
        button:initialise()
        button.recipe_nav_ref = row.recipe_nav_ref
        button.backgroundColor = Theme.color("transparent")
        button.backgroundColorMouseOver = Theme.color("navButtonHover")
        button.borderColor = Theme.color("navButtonBorder")
        button.textColor = Theme.color("navButtonText")
        browser.detailPanel:addChild(button)
    end
    yOffset = yOffset + 16
    return renderRequirements(browser, row, yOffset, deps, state, stateKey)
end

function IrisBrowserInteractionRenderer.render(browser, browserClass, fullType, item, yOffset, deps)
    local projection = Collector.collect(deps.model.interactionState, deps.model.locale, deps.tr)
    if projection.status == "fault" then
        addLabel(browser, 10, yOffset,
            deps.tr("Iris_Interaction_Unavailable", "Interaction data unavailable"),
            0.85, 0.4, 0.35)
        return yOffset + 20
    end

    addLabel(browser, 10, yOffset, headerText(projection, deps.tr), 0.65, 0.85, 1.0)
    yOffset = yOffset + 20
    if projection.status == "verified_empty" then
        addLabel(browser, 20, yOffset,
            deps.tr("Iris_Interaction_VerifiedEmpty", "No interactions in verified Iris data"),
            0.65, 0.65, 0.65)
        return yOffset + 18
    end

    local state, stateKey = State.forItem(
        browser, deps.browserGeneration, deps.model.locale, fullType, projection.density
    )
    if projection.density == "dense" then
        local modeText = state.full
            and deps.tr("Iris_Interaction_Compact", "Compact")
            or deps.tr("Iris_Interaction_Full", "Full")
        local modeButton = ISButton:new(10, yOffset, 110, 18, modeText, browser,
            browserClass.onToggleInteractionDensity)
        modeButton:initialise()
        modeButton.interactionStateKey = stateKey
        browser.detailPanel:addChild(modeButton)

        local search = ISTextEntryBox:new(state.query or "", 125, yOffset, 190, 18)
        search:initialise()
        search:instantiate()
        search.interactionStateKey = stateKey
        search.onTextChange = function()
            local value = search:getInternalText() or ""
            if state.query ~= value then
                state.query = value
                browser:showDetail(fullType, true)
            end
        end
        browser.detailPanel:addChild(search)
        yOffset = yOffset + 22
    end

    local visible = Projection.visibleRows(projection, state.full, state.query)
    addLabel(browser, 20, yOffset,
        deps.tr("Iris_Interaction_Visible", "Visible") .. " " .. tostring(#visible) ..
        "/" .. tostring(projection.total), 0.55, 0.65, 0.75)
    yOffset = yOffset + 16

    local visibleBySource = {recipe = {}, rightclick = {}}
    for _, row in ipairs(visible) do table.insert(visibleBySource[row.source], row) end
    local sourceLabels = {
        recipe = deps.tr("Iris_Interaction_SourceRecipe", "Recipe"),
        rightclick = deps.tr("Iris_Interaction_SourceRightClick", "Right-click"),
    }
    for _, source in ipairs(Policy.SOURCE_ORDER) do
        local sourceRows = projection.bySource[source]
        if #sourceRows > 0 then
            addLabel(browser, 20, yOffset,
                sourceLabels[source] .. " (" .. tostring(#sourceRows) .. ")",
                0.75, 0.8, 0.9)
            yOffset = yOffset + 16
            for _, row in ipairs(visibleBySource[source]) do
                yOffset = renderRow(browser, row, yOffset, {
                    tr = deps.tr, locale = deps.model.locale, browserClass = browserClass,
                    projection = projection,
                }, state, stateKey)
            end
        end
    end
    return yOffset
end

return IrisBrowserInteractionRenderer
