local Harness = {}

local function isArray(value)
    if type(value) ~= "table" then return false end
    local count, maximum = 0, 0
    for key, _ in pairs(value) do
        if type(key) ~= "number" or key < 1 or key % 1 ~= 0 then return false end
        count = count + 1
        if key > maximum then maximum = key end
    end
    return count == maximum
end

local function escape(value)
    return tostring(value):gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("\n", "\\n"):gsub("\r", "\\r"):gsub("\t", "\\t")
end

local function encode(value)
    local kind = type(value)
    if value == nil then return "null" end
    if kind == "boolean" or kind == "number" then return tostring(value) end
    if kind == "string" then return '"' .. escape(value) .. '"' end
    if kind ~= "table" then return '"' .. escape(value) .. '"' end
    local parts = {}
    if isArray(value) then
        for index = 1, #value do parts[#parts + 1] = encode(value[index]) end
        return "[" .. table.concat(parts, ",") .. "]"
    end
    local keys = {}
    for key, _ in pairs(value) do keys[#keys + 1] = tostring(key) end
    table.sort(keys)
    for _, key in ipairs(keys) do parts[#parts + 1] = encode(key) .. ":" .. encode(value[key]) end
    return "{" .. table.concat(parts, ",") .. "}"
end

local function quitToDesktop()
    pcall(function() getCore():quitToDesktop() end)
end

function Harness.runAll()
    local rows, failures = 0, 0
    local function emit(caseId, axis, fixtureId, passed, expected, observed, stubs)
        rows = rows + 1
        if not passed then failures = failures + 1 end
        print("IRIS_CORE_ROW\t" .. encode({
            case_id = caseId,
            axis = axis,
            fixture_id = fixtureId,
            owner_change = 11,
            status = passed and "pass" or "fail",
            expected = expected,
            observed = observed,
            dialect_sensitive = true,
            dialect_reasons = {"Project_Zomboid_B41_Kahlua", "runtime_module_and_ui_binding"},
            stubbed_dependencies = stubs or {},
        }))
    end

    local runOk, runError = pcall(function()
        local UseCases = require("Iris/API/UseCases")
        local Policy = require("Iris/UI/Browser/IrisBrowserInteractionPolicy")
        local Projection = require("Iris/UI/Browser/IrisBrowserInteractionProjection")
        local State = require("Iris/UI/Browser/IrisBrowserInteractionState")
        local RecipeNav = require("Iris/UI/Browser/IrisBrowserRecipeNav")
        require("Iris/UI/Browser/IrisBrowserInteractionRenderer")

        local function tr(key, fallback)
            local translated = getTextOrNull and getTextOrNull(key) or nil
            return translated or fallback
        end

        emit(
            "interaction_density.pz_policy",
            "density_policy",
            "zero_one_eight_nine",
            Policy.density(0) == "empty" and Policy.density(1) == "single" and
                Policy.density(8) == "small" and Policy.density(9) == "dense",
            {zero="empty", one="single", eight="small", nine="dense"},
            {zero=Policy.density(0), one=Policy.density(1), eight=Policy.density(8), nine=Policy.density(9)}
        )

        local moldState = UseCases._getDescriptionState("Base.223BulletsMold")
        local mold = Projection.build(moldState, "EN", tr)
        local moldRow = mold.rows and mold.rows[1] or nil
        emit(
            "interaction_density.pz_mold",
            "runtime_projection",
            "Base.223BulletsMold",
            mold.status == "available" and mold.density == "single" and mold.total == 1 and
                mold.recipeCount == 1 and moldRow and #moldRow.recipe_requirements == 3 and
                moldRow.recipe_id == moldRow.recipe_nav_ref.recipe_id,
            {status="available", density="single", total=1, recipe_count=1, requirement_count=3, stable_navigation=true},
            {status=mold.status, density=mold.density, total=mold.total, recipe_count=mold.recipeCount,
                requirement_count=moldRow and #moldRow.recipe_requirements or -1,
                stable_navigation=moldRow and moldRow.recipe_nav_ref and moldRow.recipe_id == moldRow.recipe_nav_ref.recipe_id or false}
        )

        local tongsState = UseCases._getDescriptionState("Base.Tongs")
        local tongs = Projection.build(tongsState, "EN", tr)
        local compactRows = Projection.visibleRows(tongs, false, "")
        local fullRows = Projection.visibleRows(tongs, true, "")
        emit(
            "interaction_density.pz_tongs",
            "runtime_projection",
            "Base.Tongs",
            tongs.status == "available" and tongs.density == "dense" and tongs.total == 33 and
                tongs.recipeCount == 33 and #compactRows == 0 and #fullRows == 33,
            {status="available", density="dense", total=33, recipe_count=33, compact_visible=0, full_visible=33},
            {status=tongs.status, density=tongs.density, total=tongs.total, recipe_count=tongs.recipeCount,
                compact_visible=#compactRows, full_visible=#fullRows}
        )

        local browser = {}
        local first = State.forItem(browser, 1, "EN", "Base.Tongs", "dense")
        first.query = "old"
        first.requirements["uc.recipe.make_223_bullets"] = true
        local second = State.forItem(browser, 1, "KO", "Base.Tongs", "dense")
        emit(
            "interaction_density.pz_state",
            "state_invalidation",
            "locale_generation_item",
            second.query == "" and second.full == false and next(second.requirements) == nil,
            {query="", full=false, requirements_empty=true},
            {query=second.query, full=second.full, requirements_empty=next(second.requirements) == nil}
        )

        local browserClass = {}
        RecipeNav.install(browserClass, {})
        local noRefOk = pcall(browserClass.onRecipeGoToCrafting, {}, nil)
        emit(
            "interaction_density.pz_navigation_binding",
            "ui_binding",
            "recipe_navigation_callback",
            type(browserClass.onRecipeGoToCrafting) == "function" and noRefOk,
            {callback="function", nil_reference_is_noop=true},
            {callback=type(browserClass.onRecipeGoToCrafting), nil_reference_is_noop=noRefOk},
            {"crafting UI activation omitted for nil reference"}
        )
    end)

    if not runOk then
        emit(
            "interaction_density.pz_unhandled",
            "runtime_harness",
            "module_execution",
            false,
            {runtime_error="none"},
            {runtime_error=tostring(runError)}
        )
    end

    print("IRIS_CORE_SUMMARY\t" .. encode({row_count=rows, failure_count=failures}))
    quitToDesktop()
    return runOk and failures == 0
end

return Harness
