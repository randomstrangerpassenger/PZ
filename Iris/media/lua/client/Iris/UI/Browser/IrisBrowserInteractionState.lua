local IrisBrowserInteractionState = {}

local function ownerKey(generation, locale)
    return tostring(generation or 0) .. "|" .. tostring(locale or "EN")
end

function IrisBrowserInteractionState.forItem(browser, generation, locale, fullType, density)
    local owner = ownerKey(generation, locale)
    if browser._interactionStateOwner ~= owner then
        browser._interactionStateOwner = owner
        browser._interactionStateByItem = {}
        browser._interactionActiveKey = nil
    end
    local key = owner .. "|" .. tostring(fullType)
    if browser._interactionActiveKey and browser._interactionActiveKey ~= key then
        local previous = browser._interactionStateByItem[browser._interactionActiveKey]
        if previous then previous.query = "" end
    end
    browser._interactionActiveKey = key
    local state = browser._interactionStateByItem[key]
    if not state then
        state = {
            full = density ~= "dense",
            recipeExpanded = density ~= "dense",
            query = "",
            requirements = {},
        }
        browser._interactionStateByItem[key] = state
    end
    return state, key
end

function IrisBrowserInteractionState.toggleFull(browser, key)
    local state = browser._interactionStateByItem and browser._interactionStateByItem[key]
    if state then state.full = not state.full end
end

function IrisBrowserInteractionState.toggleRecipe(browser, key)
    local state = browser._interactionStateByItem and browser._interactionStateByItem[key]
    if state then state.recipeExpanded = not (state.recipeExpanded == true) end
end

function IrisBrowserInteractionState.forEvolved(
    browser, generation, locale, fullType, density
)
    local owner = ownerKey(generation, locale)
    if browser._evolvedInteractionStateOwner ~= owner then
        browser._evolvedInteractionStateOwner = owner
        browser._evolvedInteractionStateByItem = {}
        browser._evolvedInteractionActiveKey = nil
    end
    local key = owner .. "|" .. tostring(fullType)
    if browser._evolvedInteractionActiveKey and
        browser._evolvedInteractionActiveKey ~= key then
        local previous = browser._evolvedInteractionStateByItem[
            browser._evolvedInteractionActiveKey
        ]
        if previous then previous.query = "" end
    end
    browser._evolvedInteractionActiveKey = key
    local state = browser._evolvedInteractionStateByItem[key]
    if not state then
        state = {expanded = density ~= "dense", query = ""}
        browser._evolvedInteractionStateByItem[key] = state
    end
    return state, key
end

function IrisBrowserInteractionState.toggleEvolved(browser, key)
    local states = browser._evolvedInteractionStateByItem
    local state = states and states[key]
    if state then state.expanded = not (state.expanded == true) end
end

function IrisBrowserInteractionState.toggleRequirements(browser, key, identity, defaultValue)
    local state = browser._interactionStateByItem and browser._interactionStateByItem[key]
    if not state then return end
    local current = state.requirements[identity]
    if current == nil then current = defaultValue == true end
    state.requirements[identity] = not current
end

return IrisBrowserInteractionState
