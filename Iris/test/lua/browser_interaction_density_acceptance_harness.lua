local repositoryRoot = assert(arg[1], "repository root required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local Policy = require("Iris/UI/Browser/IrisBrowserInteractionPolicy")
local Projection = require("Iris/UI/Browser/IrisBrowserInteractionProjection")
local State = require("Iris/UI/Browser/IrisBrowserInteractionState")
local RequirementPolicy = require("Iris/UI/Browser/IrisRequirementPolicy")

local translations = {
    Iris_Interaction_Construction = "Construction",
    Iris_Interaction_WoodCutting = "Wood cutting",
    Iris_Interaction_RowUnavailable = "Display unavailable",
}
local function tr(key, fallback) return translations[key] or fallback end
local function assertEqual(expected, actual, label)
    if expected ~= actual then error(label .. ": expected=" .. tostring(expected) .. " actual=" .. tostring(actual)) end
end
local function rightclick(identity, display)
    return {label_key = identity, surface = "context_menu", line_kind = "evidence", display_by_locale = display}
end
local function recipe(identity, recipeId, en, ko)
    return {
        label_key = identity, surface = "recipe_ui", line_kind = "evidence",
        recipe_id = recipeId, recipe_original_name = en, recipe_translated_name = ko,
        recipe_nav_ref = {recipe_id = recipeId, original_name = en},
    }
end
local function available(lines) return {status = "available", lines = lines} end

assertEqual("empty", Policy.density(0), "empty density")
assertEqual("single", Policy.density(1), "single density")
assertEqual("small", Policy.density(2), "small lower density")
assertEqual("small", Policy.density(8), "small upper density")
assertEqual("dense", Policy.density(9), "dense density")

local empty = Projection.build({status = "verified_empty", lines = {}}, "EN", tr)
assertEqual("verified_empty", empty.status, "verified empty")
local lookupFault = Projection.build({status = "fault", reason = "chunk_failure"}, "EN", tr)
assertEqual("fault", lookupFault.status, "fault distinct from empty")

local mixed = Projection.build(available({
    rightclick("uc.action.construction", {EN = "Construction", KO = "건설"}),
    recipe("uc.recipe.alpha", "alpha", "Alpha", "알파"),
    recipe("uc.recipe.beta", "beta", "Beta", "베타"),
}), "EN", tr)
assertEqual("available", mixed.status, "mixed projection status")
assertEqual(3, mixed.total, "total count")
assertEqual(2, mixed.recipeCount, "recipe count")
assertEqual(1, mixed.rightclickCount, "rightclick count")
local ordered = Projection.visibleRows(mixed, true, "")
assertEqual("uc.recipe.alpha", ordered[1].identity, "recipe source first")
assertEqual("uc.recipe.beta", ordered[2].identity, "recipe order preserved")
assertEqual("uc.action.construction", ordered[3].identity, "rightclick source second")
local mixedKo = Projection.build(available({
    rightclick("uc.action.construction", {EN = "Construction", KO = "건설"}),
    recipe("uc.recipe.alpha", "alpha", "Alpha", "알파"),
    recipe("uc.recipe.beta", "beta", "Beta", "베타"),
}), "KO", tr)
local orderedKo = Projection.visibleRows(mixedKo, true, "")
for index, row in ipairs(ordered) do
    assertEqual(row.identity, orderedKo[index].identity, "locale identity/order parity " .. index)
end

local sameDisplay = Projection.build(available({
    rightclick("mod.action.one", {EN = "Same", KO = "같음"}),
    rightclick("mod.action.two", {EN = "Same", KO = "같음"}),
}), "EN", tr)
assertEqual(2, sameDisplay.total, "duplicate labels retain distinct identities")

local denseLines = {}
for index = 1, 9 do
    table.insert(denseLines, recipe("uc.recipe.row" .. index, "row" .. index, "Row " .. index, "행 " .. index))
end
local dense = Projection.build(available(denseLines), "EN", tr)
assertEqual("dense", dense.density, "nine is dense")
assertEqual(0, #Projection.visibleRows(dense, false, ""), "compact has no arbitrary representatives")
local matched = Projection.visibleRows(dense, false, "Row 2")
assertEqual(1, #matched, "literal search match")
assertEqual("uc.recipe.row2", matched[1].identity, "literal search identity")
assertEqual(9, #Projection.visibleRows(dense, true, ""), "clear/full restores set")

local duplicate = Projection.build(available({
    recipe("uc.recipe.same", "same", "Same", "같음"),
    recipe("uc.recipe.same", "same", "Same", "같음"),
}), "EN", tr)
assertEqual("fault", duplicate.status, "duplicate identity fails")
local unknown = Projection.build(available({
    {label_key = "uc.raw", surface = "both", line_kind = "evidence"},
}), "EN", tr)
assertEqual("fault", unknown.status, "both surface fails")
local badNav = Projection.build(available({
    recipe("uc.recipe.bad", "bad", "Bad", "나쁨"),
}), "EN", tr)
badNav.rows[1].sourceLine.recipe_nav_ref.recipe_id = "other"
assertEqual("fault", Projection.build(available({badNav.rows[1].sourceLine}), "EN", tr).status,
    "navigation identity mismatch fails")

local external = Projection.build(available({
    rightclick("mod.action.normalized", {EN = "Normalized action"}),
}), "KO", tr)
assertEqual("mod.action.normalized", external.rows[1].identity, "external identity retained")
assertEqual(true, external.rows[1].displayUnavailable, "missing locale does not cross-language fallback")
local englishRequirement = RequirementPolicy.displayText(
    {display = "미습득", check = {type = "flag", flag_id = "NeedToBeLearn"}},
    RequirementPolicy.COLOR_UNKNOWN, tr, "EN"
)
assertEqual("Recipe must be learned", englishRequirement, "English requirement avoids Korean raw fallback")

local browser = {}
local stateA, keyA = State.forItem(browser, 1, "EN", "Base.A", "dense")
stateA.query = "old"
stateA.requirements["uc.recipe.row1"] = true
local stateB = State.forItem(browser, 1, "EN", "Base.B", "single")
assertEqual("", stateB.query, "new item query default")
assertEqual("", stateA.query, "old item query reset")
local stateLocale = State.forItem(browser, 1, "KO", "Base.A", "dense")
assertEqual(false, stateLocale.full, "locale invalidates density state")
assertEqual(nil, stateLocale.requirements["uc.recipe.row1"], "locale invalidates row state")
local stateGeneration = State.forItem(browser, 2, "KO", "Base.A", "dense")
assertEqual(false, stateGeneration.full, "generation invalidates density state")

print("PASS browser interaction density acceptance")
