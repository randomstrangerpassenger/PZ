require "ISUI/ISButton"
require "ISUI/ISLabel"
require "ISUI/ISTextEntryBox"

local Collector = require("Iris/UI/Browser/IrisBrowserInteractionCollector")
local Policy = require("Iris/UI/Browser/IrisBrowserInteractionPolicy")
local Projection = require("Iris/UI/Browser/IrisBrowserInteractionProjection")
local RequirementPolicy = require("Iris/UI/Browser/IrisRequirementPolicy")
local State = require("Iris/UI/Browser/IrisBrowserInteractionState")
local TextLayout = require("Iris/UI/Detail/IrisTextLayout")
local Theme = require("Iris/UI/Browser/IrisBrowserTheme")

local IrisBrowserInteractionRenderer = {}

local SEARCH_ENTRY_SLOTS = {
    "interactionSearchEntry",
    "evolvedSearchEntry",
}

local function beginSearchEntryLayout(browser)
    for _, slot in ipairs(SEARCH_ENTRY_SLOTS) do
        local entry = browser[slot]
        if entry then entry.irisDetailActive = false end
    end
end

local function finishSearchEntryLayout(browser)
    for _, slot in ipairs(SEARCH_ENTRY_SLOTS) do
        local entry = browser[slot]
        if entry and not entry.irisDetailActive and entry:getIsVisible() then
            entry:setVisible(false)
        end
    end
    if browser.updateDetailSearchEntries then
        browser:updateDetailSearchEntries()
    end
end

local function ensureSearchEntry(browser, slot)
    local entry = browser[slot]
    if entry then return entry end

    entry = ISTextEntryBox:new("", 0, 0, 1, 18)
    entry:initialise()
    entry:instantiate()
    entry.onTextChange = function()
        if entry.irisSuppressTextChange then return end
        local state = entry.irisInteractionState
        local value = entry:getInternalText() or ""
        if state and state.query ~= value then
            state.query = value
            browser:showDetail(entry.irisFullType, true)
        end
    end
    browser:addChild(entry)
    browser[slot] = entry
    return entry
end

local function activateSearchEntry(browser, slot, state, stateKey, fullType, x, y, width)
    local entry = ensureSearchEntry(browser, slot)
    entry.irisDetailActive = true
    entry.irisInteractionState = state
    entry.irisInteractionStateKey = stateKey
    entry.irisFullType = fullType
    entry.irisDetailX = x
    entry.irisDetailY = y
    entry.irisDetailWidth = width

    local query = tostring(state.query or "")
    if (entry:getInternalText() or "") ~= query then
        entry.irisSuppressTextChange = true
        entry:setText(query)
        entry.irisSuppressTextChange = false
    end
    return entry
end

local function addLabel(browser, x, y, text, r, g, b)
    local label = ISLabel:new(x, y, 16, text, r, g, b, 1, UIFont.Small, true)
    browser.detailPanel:addChild(label)
    return label
end

local function headerText(projection, tr)
    local interaction = tr("Iris_Detail_Interaction", "Interactions")
    local recipe = tr("Iris_Interaction_SourceRecipe", "Recipe")
    local rightclick = tr("Iris_Interaction_SourceRightClick", "Right-click")
    local text = interaction .. " " .. tostring(projection.total) ..
        "  |  " .. recipe .. " " .. tostring(projection.recipeCount) ..
        "  |  " .. rightclick .. " " .. tostring(projection.rightclickCount)
    if projection.evolvedRecipeCount > 0 then
        local evolved = tr("Iris_Interaction_EvolvedRecipe", "Freeform Cooking")
        text = text .. "  |  " .. evolved .. " " .. tostring(projection.evolvedRecipeCount)
    end
    return text
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

local function renderEvolvedText(browser, row, display, x, yOffset, source, identities)
    local width = math.max(1, browser.detailPanel.width - 40)
    local lines = TextLayout.wrapLines(display, width, UIFont.Small)
    if #lines == 0 then lines = {display} end
    for _, line in ipairs(lines) do
        local label = addLabel(browser, x, yOffset, line, 0.9, 0.8, 0.55)
        label.interactionRowSource = source
        label.interactionIdentities = identities
        label.interactionAccessibleText = row.display
        yOffset = yOffset + 16
    end
    return yOffset
end

local function renderRow(browser, row, yOffset, deps, state, stateKey)
    if row.source == "evolved_recipe" then
        if row.kind == "group" then
            local heading = row.action .. " (" .. tostring(row.relationCount) .. ")"
            yOffset = renderEvolvedText(
                browser, row, heading, 20, yOffset,
                "evolved_recipe_group", row.identities
            )
            for _, child in ipairs(row.children or {}) do
                yOffset = renderEvolvedText(
                    browser, child, child.targetLabel, 28, yOffset,
                    "evolved_recipe", {child.identity}
                )
            end
            return yOffset
        end
        return renderEvolvedText(
            browser, row, row.display, 20, yOffset,
            "evolved_recipe", row.identities or {row.identity}
        )
    end

    local prefix = deps.tr("Iris_Prefix_RightClick", "[Action]")
    if row.source == "recipe" then
        prefix = deps.tr("Iris_Prefix_Recipe", "[Recipe]")
    end
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
    beginSearchEntryLayout(browser)
    local projection = Collector.collect(
        deps.model.interactionState,
        deps.model.evolvedRecipeState,
        deps.model.locale,
        deps.tr
    )
    if projection.status == "fault" then
        addLabel(browser, 10, yOffset,
            deps.tr("Iris_Interaction_Unavailable", "Interaction data unavailable"),
            0.85, 0.4, 0.35)
        finishSearchEntryLayout(browser)
        return yOffset + 20
    end

    addLabel(browser, 10, yOffset, headerText(projection, deps.tr), 0.65, 0.85, 1.0)
    yOffset = yOffset + 20
    if projection.status == "verified_empty" then
        addLabel(browser, 20, yOffset,
            deps.tr("Iris_Interaction_VerifiedEmpty", "No interactions in verified Iris data"),
            0.65, 0.65, 0.65)
        finishSearchEntryLayout(browser)
        return yOffset + 18
    end

    if projection.fixedTotal > 0 then
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

            activateSearchEntry(
                browser, "interactionSearchEntry", state, stateKey, fullType,
                125, yOffset, 190
            )
            yOffset = yOffset + 22
        end

        local visible = Projection.visibleRows(projection, state.full, state.query)
        local visibleBySource = {recipe = {}, rightclick = {}}
        for _, row in ipairs(visible) do table.insert(visibleBySource[row.source], row) end
        if state.recipeExpanded and tostring(state.query or "") == "" and
            #visibleBySource.recipe == 0 then
            visibleBySource.recipe = projection.bySource.recipe
        elseif not state.recipeExpanded then
            visibleBySource.recipe = {}
        end
        local visibleCount = #visibleBySource.recipe + #visibleBySource.rightclick
        addLabel(browser, 20, yOffset,
            deps.tr("Iris_Interaction_Visible", "Visible") .. " " ..
            tostring(visibleCount) .. "/" .. tostring(projection.fixedTotal),
            0.55, 0.65, 0.75)
        yOffset = yOffset + 16

        local sourceLabels = {
            recipe = deps.tr("Iris_Interaction_SourceRecipe", "Recipe"),
            rightclick = deps.tr("Iris_Interaction_SourceRightClick", "Right-click"),
        }
        for _, source in ipairs(Policy.SOURCE_ORDER) do
            local sourceRows = projection.bySource[source]
            if #sourceRows > 0 then
                local headerHeight = 16
                if source == "recipe" then
                    local marker = state.recipeExpanded and "[-] " or "[+] "
                    local button = ISButton:new(
                        20, yOffset, math.max(180, browser.detailPanel.width - 40), 18,
                        marker .. sourceLabels[source] .. " (" ..
                            tostring(#sourceRows) .. ")",
                        browser, browserClass.onToggleFixedRecipeInteraction
                    )
                    button:initialise()
                    button.interactionStateKey = stateKey
                    button.backgroundColor = Theme.color("transparent")
                    button.backgroundColorMouseOver = Theme.color("sectionButtonHover")
                    button.borderColor = Theme.color("transparent")
                    browser.detailPanel:addChild(button)
                    headerHeight = 20
                else
                    addLabel(browser, 20, yOffset,
                        sourceLabels[source] .. " (" .. tostring(#sourceRows) .. ")",
                        0.75, 0.8, 0.9)
                end
                yOffset = yOffset + headerHeight
                for _, row in ipairs(visibleBySource[source]) do
                    yOffset = renderRow(browser, row, yOffset, {
                        tr = deps.tr, locale = deps.model.locale, browserClass = browserClass,
                        projection = projection,
                    }, state, stateKey)
                end
            end
        end
    end

    if projection.evolvedRecipeCount > 0 then
        local evolvedState, evolvedStateKey = State.forEvolved(
            browser, deps.browserGeneration, deps.model.locale, fullType,
            projection.evolvedDensity
        )
        local evolvedVisible = Projection.visibleEvolvedRows(
            projection, evolvedState.expanded, evolvedState.query
        )
        local visiblyExpanded = evolvedState.expanded == true or
            (tostring(evolvedState.query or "") ~= "" and #evolvedVisible > 0)
        local marker = visiblyExpanded and "[-] " or "[+] "
        local sectionText = marker ..
            deps.tr("Iris_Interaction_EvolvedRecipe", "Freeform Cooking") ..
            " (" .. tostring(projection.evolvedRecipeCount) .. ")"
        local sectionButton = ISButton:new(
            20, yOffset, math.max(180, browser.detailPanel.width - 40), 18,
            sectionText, browser, browserClass.onToggleEvolvedInteraction
        )
        sectionButton:initialise()
        sectionButton.evolvedInteractionStateKey = evolvedStateKey
        sectionButton.backgroundColor = Theme.color("transparent")
        sectionButton.backgroundColorMouseOver = Theme.color("sectionButtonHover")
        sectionButton.borderColor = Theme.color("transparent")
        browser.detailPanel:addChild(sectionButton)
        yOffset = yOffset + 20

        if projection.evolvedDensity == "dense" then
            activateSearchEntry(
                browser, "evolvedSearchEntry", evolvedState, evolvedStateKey, fullType,
                20, yOffset, math.max(180, browser.detailPanel.width - 40)
            )
            yOffset = yOffset + 22
        end

        local visibleRelationCount = 0
        for _, row in ipairs(evolvedVisible) do
            visibleRelationCount = visibleRelationCount + (row.relationCount or 1)
        end
        addLabel(browser, 28, yOffset,
            deps.tr("Iris_Interaction_Visible", "Visible") .. " " ..
            tostring(visibleRelationCount) .. "/" .. tostring(projection.evolvedRecipeCount),
            0.55, 0.65, 0.75)
        yOffset = yOffset + 16
        for _, row in ipairs(evolvedVisible) do
            yOffset = renderRow(browser, row, yOffset, {
                tr = deps.tr, locale = deps.model.locale, browserClass = browserClass,
                projection = projection,
            }, evolvedState, evolvedStateKey)
        end
    end
    finishSearchEntryLayout(browser)
    return yOffset
end

return IrisBrowserInteractionRenderer
