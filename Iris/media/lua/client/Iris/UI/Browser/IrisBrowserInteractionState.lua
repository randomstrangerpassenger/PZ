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
        state = {full = density ~= "dense", query = "", requirements = {}}
        browser._interactionStateByItem[key] = state
    end
    return state, key
end

function IrisBrowserInteractionState.toggleFull(browser, key)
    local state = browser._interactionStateByItem and browser._interactionStateByItem[key]
    if state then state.full = not state.full end
end

function IrisBrowserInteractionState.toggleRequirements(browser, key, identity, defaultValue)
    local state = browser._interactionStateByItem and browser._interactionStateByItem[key]
    if not state then return end
    local current = state.requirements[identity]
    if current == nil then current = defaultValue == true end
    state.requirements[identity] = not current
end

return IrisBrowserInteractionState
