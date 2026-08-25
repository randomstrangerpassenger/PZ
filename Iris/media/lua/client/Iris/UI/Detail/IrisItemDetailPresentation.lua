-- Shared field visibility, units, and semantic projection for Browser/Wiki/Tooltip.
local Presentation = {}

local PROFILES = {
    raw = { multiplier = 1, format_string = "%.0f" },
    percent_scaled = { multiplier = 100, format_string = "%.0f" },
}

local function known(model, group, field)
    local facts = model and model.factStates and model.factStates[group]
    local valueFact = facts and facts[field] or nil
    return valueFact and valueFact.state == "known"
end

function Presentation.getProfile(profileName)
    local profile = assert(PROFILES[profileName], "unknown detail unit profile: " .. tostring(profileName))
    return { multiplier = profile.multiplier, format_string = profile.format_string }
end

function Presentation.formatSigned(value, profileName)
    local profile = assert(PROFILES[profileName], "unknown detail unit profile: " .. tostring(profileName))
    local sign = value < 0 and "" or "+"
    return sign .. string.format(profile.format_string, value * profile.multiplier)
end

function Presentation.semanticSnapshot(model)
    if not model then return {} end
    local rows = {}
    local function add(id, group, field, value, unit, visible)
        local valueFact = model.factStates[group][field]
        rows[#rows + 1] = {
            id = id,
            value = value,
            unit = unit,
            visible = visible == true and known(model, group, field),
            factState = valueFact.state,
        }
    end
    add("weight", "core", "weight", model.weight, "raw", type(model.weight) == "number")
    add("hunger", "food", "hunger", model.food.hunger, "percent_scaled",
        type(model.food.hunger) == "number" and model.food.hunger ~= 0)
    add("thirst", "food", "thirst", model.food.thirst, "percent_scaled",
        type(model.food.thirst) == "number" and model.food.thirst ~= 0)
    add("stress", "food", "stress", model.food.stress, "percent_scaled",
        type(model.food.stress) == "number" and model.food.stress ~= 0)
    add("boredom", "food", "boredom", model.food.boredom, "percent_scaled",
        type(model.food.boredom) == "number" and model.food.boredom ~= 0)
    add("calories", "food", "calories", model.food.calories, "raw",
        type(model.food.calories) == "number" and model.food.calories > 0)
    add("minDamage", "weapon", "minDamage", model.weapon.minDamage, "raw",
        type(model.weapon.minDamage) == "number")
    add("maxDamage", "weapon", "maxDamage", model.weapon.maxDamage, "raw",
        type(model.weapon.maxDamage) == "number")
    add("conditionMax", "weapon", "conditionMax", model.weapon.conditionMax, "raw",
        type(model.weapon.conditionMax) == "number" and model.weapon.conditionMax > 0)
    add("capacity", "moveable", "capacity", model.moveable.capacity, "raw",
        type(model.moveable.capacity) == "number" and model.moveable.capacity > 0)
    return rows
end

function Presentation.visibleRows(model)
    local result = {}
    for _, row in ipairs(Presentation.semanticSnapshot(model)) do
        if row.visible then result[#result + 1] = row end
    end
    return result
end

function Presentation.tooltipFacts(model, maxLines)
    local limit = math.min(4, math.max(0, maxLines or 4))
    local lines = {}
    for _, row in ipairs(Presentation.visibleRows(model)) do
        if #lines >= limit then break end
        local value = row.value
        if row.unit == "percent_scaled" then
            value = Presentation.formatSigned(value, row.unit)
        end
        lines[#lines + 1] = { id = row.id, value = value, unit = row.unit }
    end
    return lines
end

return Presentation
