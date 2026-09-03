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

local function evolvedActionKey(role, conditions)
    if type(conditions) ~= "table" then return nil end
    if #conditions == 0 and
        (role == "base_item" or role == "ingredient" or role == "spice") then
        return role .. ":none"
    end
    if #conditions == 1 and conditions[1] == "cooked" and
        (role == "ingredient" or role == "spice") then
        return role .. ":cooked"
    end
    return nil
end

local function groupEvolvedRows(rows)
    local grouped = {}
    local byAction = {}
    for _, row in ipairs(rows) do
        local group = byAction[row.actionKey]
        if not group then
            group = {
                kind = "group",
                identity = row.identity,
                identities = {row.identity},
                source = row.source,
                baseOrdinal = row.baseOrdinal,
                action = row.action,
                actionKey = row.actionKey,
                role = row.role,
                conditions = row.conditions,
                children = {row},
                relationCount = 1,
            }
            byAction[row.actionKey] = group
            table.insert(grouped, group)
        else
            table.insert(group.identities, row.identity)
            table.insert(group.children, row)
            group.relationCount = group.relationCount + 1
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
    local seenEvolvedOrdinals = {}
    local evolvedActions = {}
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
                    if relation.target_id ~= relation.food_type_id or
                        type(relation.source_full_type) ~= "string" or
                        relation.source_full_type == "" then
                        return fault("invalid_evolved_presentation_identity:" .. identity)
                    end
                    local canonicalOrdinal = relation.canonical_ordinal
                    if type(canonicalOrdinal) ~= "number" or canonicalOrdinal < 1 or
                        canonicalOrdinal % 1 ~= 0 or seenEvolvedOrdinals[canonicalOrdinal] then
                        return fault("invalid_evolved_ordinal:" .. identity)
                    end
                    seenEvolvedOrdinals[canonicalOrdinal] = true
                    local actionKey = evolvedActionKey(relation.role, relation.conditions)
                    if not actionKey or relation.action_key ~= actionKey then
                        return fault("invalid_evolved_action:" .. identity)
                    end
                    if relation.recipe_id or relation.recipe_nav_ref or relation.rule_id then
                        return fault("synthetic_evolved_navigation:" .. identity)
                    end
                    local targetByLocale = relation.target_label_by_locale
                    local actionByLocale = relation.action_by_locale
                    local displayByLocale = relation.display_by_locale
                    local target = type(targetByLocale) == "table" and
                        targetByLocale[locale] or nil
                    local action = type(actionByLocale) == "table" and
                        actionByLocale[locale] or nil
                    local display = type(displayByLocale) == "table" and displayByLocale[locale] or nil
                    if type(target) ~= "string" or target == "" or
                        type(action) ~= "string" or action == "" or
                        type(display) ~= "string" or display == "" then
                        return fault("missing_evolved_display:" .. identity)
                    end
                    if evolvedActions[actionKey] and evolvedActions[actionKey] ~= action then
                        return fault("inconsistent_evolved_action:" .. actionKey)
                    end
                    evolvedActions[actionKey] = action
                    local row = {
                        kind = "flat", identity = identity, identities = {identity},
                        source = "evolved_recipe", baseOrdinal = canonicalOrdinal,
                        canonicalOrdinal = canonicalOrdinal,
                        display = display, displayUnavailable = false,
                        targetLabel = target, action = action, actionKey = actionKey,
                        food_type_id = relation.food_type_id, target_id = relation.target_id,
                        source_full_type = relation.source_full_type, role = relation.role,
                        conditions = relation.conditions, sourceLine = relation,
                        relationCount = 1,
                    }
                    table.insert(evolvedRows, row)
                end
                table.sort(evolvedRows, function(left, right)
                    return left.canonicalOrdinal < right.canonicalOrdinal
                end)
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
    local evolvedDensity = Policy.density(evolvedTotal)
    local evolvedDisplayRows = evolvedDensity == "dense" and
        groupEvolvedRows(evolvedRows) or evolvedRows
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
        density = Policy.density(fixedTotal), evolvedDensity = evolvedDensity,
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
    local matched = {}
    for _, row in ipairs(projection.evolvedRows or {}) do
        if needle == "" or row.display:lower():find(needle, 1, true) then
            table.insert(matched, row)
        end
    end
    if projection.evolvedDensity == "dense" then
        return groupEvolvedRows(matched)
    end
    return matched
end

return IrisBrowserInteractionProjection
