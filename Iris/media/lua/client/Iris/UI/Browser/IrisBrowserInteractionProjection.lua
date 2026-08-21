local Policy = require("Iris/UI/Browser/IrisBrowserInteractionPolicy")

local IrisBrowserInteractionProjection = {}

local RIGHTCLICK_LABEL_KEYS = {
    ["uc.action.attach_weapon_part"] = "Iris_Interaction_AttachWeaponPart",
    ["uc.action.construction"] = "Iris_Interaction_Construction",
    ["uc.action.extinguish_fire"] = "Iris_Interaction_ExtinguishFire",
    ["uc.action.foreign_body_removal"] = "Iris_Interaction_ForeignBodyRemoval",
    ["uc.action.fuel"] = "Iris_Interaction_Fuel",
    ["uc.action.metal_cutting"] = "Iris_Interaction_MetalCutting",
    ["uc.action.open_can"] = "Iris_Interaction_OpenCan",
    ["uc.action.screw_disassembly"] = "Iris_Interaction_ScrewDisassembly",
    ["uc.action.wood_cutting"] = "Iris_Interaction_WoodCutting",
    ["uc.action.wound_suturing"] = "Iris_Interaction_WoundSuturing",
}

local function normalizedLocale(locale)
    if tostring(locale or "EN"):upper() == "KO" then return "KO" end
    return "EN"
end

local function fault(reason)
    return {status = "fault", reason = reason, rows = {}, bySource = {recipe = {}, rightclick = {}}}
end

local function rowDisplay(line, identity, source, locale, tr)
    local external = line.display_by_locale
    if type(external) == "table" then
        local value = external[locale]
        if type(value) == "string" and value ~= "" then return value, false end
        return tr("Iris_Interaction_RowUnavailable", "Display unavailable"), true
    end
    if source == "recipe" then
        local value = locale == "KO" and line.recipe_translated_name or line.recipe_original_name
        if type(value) == "string" and value ~= "" then return value, false end
        return tr("Iris_Interaction_RowUnavailable", "Display unavailable"), true
    end
    local translationKey = RIGHTCLICK_LABEL_KEYS[identity]
    if not translationKey then
        return tr("Iris_Interaction_RowUnavailable", "Display unavailable"), true
    end
    return tr(translationKey, "Display unavailable"), false
end

function IrisBrowserInteractionProjection.build(interactionState, locale, tr)
    if type(interactionState) ~= "table" then return fault("missing_interaction_state") end
    if interactionState.status == "fault" then return fault(interactionState.reason or "lookup_fault") end
    if interactionState.status == "verified_empty" then
        return {
            status = "verified_empty", reason = interactionState.reason, rows = {}, total = 0,
            recipeCount = 0, rightclickCount = 0,
            bySource = {recipe = {}, rightclick = {}}, density = "empty",
        }
    end
    if interactionState.status ~= "available" or type(interactionState.lines) ~= "table" then
        return fault("invalid_interaction_state")
    end

    locale = normalizedLocale(locale)
    local rows = {}
    local bySource = {recipe = {}, rightclick = {}}
    local seen = {}
    for ordinal, line in ipairs(interactionState.lines) do
        if line.line_kind ~= "exclusion" then
            local identity = line.label_key
            if type(identity) ~= "string" or identity == "" then return fault("blank_identity") end
            if seen[identity] then return fault("duplicate_identity:" .. identity) end
            seen[identity] = true

            local source = nil
            if line.surface == "recipe_ui" then source = "recipe" end
            if line.surface == "context_menu" then source = "rightclick" end
            if not source then return fault("unsupported_surface:" .. tostring(line.surface)) end
            if source == "recipe" then
                if type(line.recipe_id) ~= "string" or line.recipe_id == "" then
                    return fault("missing_recipe_id:" .. identity)
                end
                if type(line.recipe_nav_ref) ~= "table" or
                    line.recipe_nav_ref.recipe_id ~= line.recipe_id then
                    return fault("recipe_navigation_identity_mismatch:" .. identity)
                end
            end

            local display, displayUnavailable = rowDisplay(line, identity, source, locale, tr)
            local row = {
                identity = identity, source = source, baseOrdinal = ordinal,
                display = display, displayUnavailable = displayUnavailable,
                recipe_id = line.recipe_id, recipe_nav_ref = line.recipe_nav_ref,
                recipe_requirements = line.recipe_requirements or {}, sourceLine = line,
            }
            table.insert(rows, row)
            table.insert(bySource[source], row)
        end
    end

    local total = #rows
    if total == 0 then
        return {
            status = "verified_empty", reason = "positive_lines_empty", rows = {}, total = 0,
            recipeCount = 0, rightclickCount = 0, bySource = bySource, density = "empty",
        }
    end
    return {
        status = "available", rows = rows, total = total,
        recipeCount = #bySource.recipe, rightclickCount = #bySource.rightclick,
        bySource = bySource, density = Policy.density(total), locale = locale,
    }
end

function IrisBrowserInteractionProjection.visibleRows(projection, full, query)
    if projection.status ~= "available" then return {} end
    local needle = tostring(query or ""):lower()
    if projection.density == "dense" and not full and needle == "" then return {} end
    local visible = {}
    for _, source in ipairs(Policy.SOURCE_ORDER) do
        for _, row in ipairs(projection.bySource[source]) do
            if needle == "" or row.display:lower():find(needle, 1, true) then
                table.insert(visible, row)
            end
        end
    end
    return visible
end

return IrisBrowserInteractionProjection
