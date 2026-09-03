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
    return {
        status = "fault", reason = reason, rows = {},
        bySource = {recipe = {}, rightclick = {}}, evolvedRows = {},
        evolvedDisplayRows = {},
        recipeCount = 0, rightclickCount = 0, evolvedRecipeCount = 0,
        fixedTotal = 0, total = 0, density = "empty", evolvedDensity = "empty",
    }
end

local function groupEvolvedDisplayRows(rows)
    local grouped = {}
    local byDisplayContract = {}
    for _, row in ipairs(rows) do
        local key = row.display .. "\0" .. row.role .. "\0" .. table.concat(row.conditions, ",")
        local displayRow = byDisplayContract[key]
        if not displayRow then
            displayRow = {
                identity = row.identity,
                identities = {row.identity},
                source = row.source,
                baseOrdinal = row.baseOrdinal,
                display = row.display,
                displayUnavailable = row.displayUnavailable,
                food_type_id = row.food_type_id,
                food_type_ids = {row.food_type_id},
                role = row.role,
                conditions = row.conditions,
                sourceLine = row.sourceLine,
                sourceLines = {row.sourceLine},
                relationCount = 1,
            }
            byDisplayContract[key] = displayRow
            table.insert(grouped, displayRow)
        else
            table.insert(displayRow.identities, row.identity)
            table.insert(displayRow.food_type_ids, row.food_type_id)
            table.insert(displayRow.sourceLines, row.sourceLine)
            displayRow.relationCount = displayRow.relationCount + 1
        end
    end
    return grouped
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

function IrisBrowserInteractionProjection.build(interactionState, evolvedRecipeState, locale, tr)
    -- Preserve the supported three-argument call used by existing consumers.
    if type(evolvedRecipeState) == "string" then
        tr = locale
        locale = evolvedRecipeState
        evolvedRecipeState = nil
    end
    if type(interactionState) ~= "table" then return fault("missing_interaction_state") end
    if interactionState.status == "fault" then return fault(interactionState.reason or "lookup_fault") end
    if interactionState.status ~= "available" and interactionState.status ~= "verified_empty" then
        return fault("invalid_interaction_state")
    end
    if type(interactionState.lines) ~= "table" then return fault("invalid_interaction_lines") end

    locale = normalizedLocale(locale)
    local rows = {}
    local bySource = {recipe = {}, rightclick = {}}
    local evolvedRows = {}
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

    local evolvedStatus = "unavailable"
    local evolvedReason = "lookup_not_provided"
    if type(evolvedRecipeState) == "table" then
        evolvedStatus = evolvedRecipeState.status or "fault"
        evolvedReason = evolvedRecipeState.reason
        if evolvedStatus == "available" then
            if type(evolvedRecipeState.relations) ~= "table" then
                evolvedStatus = "fault"
                evolvedReason = "invalid_evolved_relations"
            else
                for ordinal, relation in ipairs(evolvedRecipeState.relations) do
                    local identity = relation.relation_id
                    if type(identity) ~= "string" or identity == "" then
                        return fault("blank_evolved_identity")
                    end
                    if seen[identity] then return fault("duplicate_identity:" .. identity) end
                    seen[identity] = true
                    if type(relation.food_type_id) ~= "string" or relation.food_type_id == "" then
                        return fault("blank_evolved_food_type:" .. identity)
                    end
                    if relation.role ~= "base_item" and relation.role ~= "ingredient" and
                        relation.role ~= "spice" then
                        return fault("invalid_evolved_role:" .. identity)
                    end
                    if type(relation.conditions) ~= "table" then
                        return fault("invalid_evolved_conditions:" .. identity)
                    end
                    for _, condition in ipairs(relation.conditions) do
                        if condition ~= "cooked" then
                            return fault("invalid_evolved_condition:" .. identity)
                        end
                    end
                    if relation.role == "base_item" and #relation.conditions > 0 then
                        return fault("invalid_evolved_base_condition:" .. identity)
                    end
                    if relation.recipe_id or relation.recipe_nav_ref or relation.rule_id then
                        return fault("synthetic_evolved_navigation:" .. identity)
                    end
                    local displayByLocale = relation.display_by_locale
                    local display = type(displayByLocale) == "table" and displayByLocale[locale] or nil
                    if type(display) ~= "string" or display == "" then
                        return fault("missing_evolved_display:" .. identity)
                    end
                    local row = {
                        identity = identity, source = "evolved_recipe", baseOrdinal = ordinal,
                        display = display, displayUnavailable = false,
                        food_type_id = relation.food_type_id, role = relation.role,
                        conditions = relation.conditions, sourceLine = relation,
                    }
                    table.insert(evolvedRows, row)
                end
            end
        elseif evolvedStatus ~= "verified_empty" and evolvedStatus ~= "unavailable" and
            evolvedStatus ~= "fault" then
            evolvedStatus = "fault"
            evolvedReason = "invalid_evolved_state"
        end
    end

    if evolvedStatus == "fault" then
        return fault("evolved_lookup_fault:" .. tostring(evolvedReason or "unknown"))
    end
    local fixedTotal = #rows
    local evolvedTotal = #evolvedRows
    local evolvedDisplayRows = groupEvolvedDisplayRows(evolvedRows)
    local total = fixedTotal + evolvedTotal
    if total == 0 then
        return {
            status = "verified_empty", reason = "positive_lines_empty", rows = {}, total = 0,
            recipeCount = 0, rightclickCount = 0, evolvedRecipeCount = 0, fixedTotal = 0,
            bySource = bySource, evolvedRows = evolvedRows,
            evolvedDisplayRows = evolvedDisplayRows,
            density = "empty", evolvedDensity = "empty",
            evolvedStatus = evolvedStatus, evolvedReason = evolvedReason,
        }
    end
    return {
        status = "available", rows = rows, total = total,
        recipeCount = #bySource.recipe, rightclickCount = #bySource.rightclick,
        evolvedRecipeCount = evolvedTotal, fixedTotal = fixedTotal,
        bySource = bySource, evolvedRows = evolvedRows,
        evolvedDisplayRows = evolvedDisplayRows,
        density = Policy.density(fixedTotal), evolvedDensity = Policy.density(evolvedTotal),
        locale = locale,
        evolvedStatus = evolvedStatus, evolvedReason = evolvedReason,
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

function IrisBrowserInteractionProjection.visibleEvolvedRows(projection, expanded, query)
    if projection.status ~= "available" then return {} end
    local needle = tostring(query or ""):lower()
    if projection.evolvedDensity == "dense" and not expanded and needle == "" then return {} end
    local visible = {}
    for _, row in ipairs(projection.evolvedDisplayRows or projection.evolvedRows or {}) do
        if needle == "" or row.display:lower():find(needle, 1, true) then
            table.insert(visible, row)
        end
    end
    return visible
end

return IrisBrowserInteractionProjection
