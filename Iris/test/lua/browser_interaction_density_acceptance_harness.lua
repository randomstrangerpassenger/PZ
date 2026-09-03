local repositoryRoot = assert(arg[1], "repository root required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local Policy = require("Iris/UI/Browser/IrisBrowserInteractionPolicy")
local Projection = require("Iris/UI/Browser/IrisBrowserInteractionProjection")
local State = require("Iris/UI/Browser/IrisBrowserInteractionState")
local RequirementPolicy = require("Iris/UI/Browser/IrisRequirementPolicy")

local translations = {
    Iris_Interaction_Construction = "Construction",
    Iris_Interaction_WoodCutting = "Wood cutting",
    Iris_Interaction_EvolvedRecipe = "Freeform Cooking",
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
local function evolved(identity, foodTypeId, role, conditions, en, ko)
    return {
        relation_id = identity, food_type_id = foodTypeId, role = role,
        conditions = conditions, display_by_locale = {EN = en, KO = ko},
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

local evolvedOnly = Projection.build({status = "verified_empty", lines = {}}, {
    status = "available", relations = {
        evolved("qg.evolved_recipe.only", "Soup", "ingredient", {},
            "Can be added to soup as an ingredient", "수프에 재료로 넣을 수 있음"),
    },
}, "EN", tr)
assertEqual("available", evolvedOnly.status, "EvolvedRecipe-only projection is available")
assertEqual(0, evolvedOnly.recipeCount, "EvolvedRecipe-only fixed recipe count")
assertEqual(0, evolvedOnly.rightclickCount, "EvolvedRecipe-only right-click count")
assertEqual(1, evolvedOnly.evolvedRecipeCount, "EvolvedRecipe-only relation count")
local evolvedOnlyRows = Projection.visibleEvolvedRows(evolvedOnly, true, "")
assertEqual(1, #evolvedOnlyRows, "EvolvedRecipe-only row is visible")
assertEqual("qg.evolved_recipe.only", evolvedOnlyRows[1].identity,
    "EvolvedRecipe-only identity")
assertEqual(nil, evolvedOnlyRows[1].recipe_nav_ref,
    "EvolvedRecipe-only row remains non-clickable")

local definitionBases = Projection.build({status = "verified_empty", lines = {}}, {
    status = "available", relations = {
        evolved("qg.evolved_recipe.bowl_salad", "Salad", "base_item", {},
            "Can be used to prepare a salad", "샐러드 준비에 사용할 수 있음"),
        evolved("qg.evolved_recipe.bowl_fruit", "FruitSalad", "base_item", {},
            "Can be used to prepare fruit salad", "과일 샐러드 준비에 사용할 수 있음"),
    },
}, "KO", tr)
local definitionBaseRows = Projection.visibleEvolvedRows(definitionBases, true, "")
assertEqual(2, #definitionBaseRows, "definition BaseItem relations remain distinct")
assertEqual("base_item", definitionBaseRows[1].role,
    "definition BaseItem uses its own participation role")
assertEqual("샐러드 준비에 사용할 수 있음", definitionBaseRows[1].display,
    "definition BaseItem has a neutral Korean display")

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

local withEvolved = Projection.build(available({
    rightclick("uc.action.construction", {EN = "Construction", KO = "건설"}),
    recipe("uc.recipe.alpha", "alpha", "Alpha", "알파"),
}), {status = "available", relations = {
    evolved("qg.evolved_recipe.soup", "Soup", "ingredient", {},
        "Can be added to soup as an ingredient", "수프에 재료로 넣을 수 있음"),
    evolved("qg.evolved_recipe.stew", "Stew", "spice", {"cooked"},
        "Can be added to stew as seasoning after cooking",
        "스튜에 양념으로 넣으려면 먼저 익혀야 함"),
}}, "EN", tr)
assertEqual("available", withEvolved.status, "EvolvedRecipe collection is available")
assertEqual(4, withEvolved.total, "combined typed relation count")
assertEqual(1, withEvolved.recipeCount, "fixed recipe count is preserved")
assertEqual(1, withEvolved.rightclickCount, "right-click count is preserved")
assertEqual(2, withEvolved.evolvedRecipeCount, "EvolvedRecipe count")
assertEqual(2, withEvolved.fixedTotal, "fixed total stays separate from EvolvedRecipe")
assertEqual("small", withEvolved.density, "fixed density ignores EvolvedRecipe total")
assertEqual("small", withEvolved.evolvedDensity, "EvolvedRecipe owns separate density")
local withEvolvedRows = Projection.visibleRows(withEvolved, true, "")
assertEqual("uc.recipe.alpha", withEvolvedRows[1].identity, "fixed recipe ordering is preserved")
assertEqual("uc.action.construction", withEvolvedRows[2].identity,
    "right-click ordering is preserved")
assertEqual(2, #withEvolvedRows, "fixed visible rows exclude Evolved presentation state")
local withEvolvedOnlyRows = Projection.visibleEvolvedRows(withEvolved, true, "")
assertEqual("qg.evolved_recipe.soup", withEvolvedOnlyRows[1].identity,
    "EvolvedRecipe preserves its own order")
assertEqual(nil, withEvolvedOnlyRows[1].recipe_nav_ref, "EvolvedRecipe remains non-clickable")
assertEqual("spice", withEvolvedOnlyRows[2].role, "relation-local spice role")
assertEqual("cooked", withEvolvedOnlyRows[2].conditions[1], "relation-local cooked condition")

local withEvolvedKo = Projection.build(available({
    rightclick("uc.action.construction", {EN = "Construction", KO = "건설"}),
    recipe("uc.recipe.alpha", "alpha", "Alpha", "알파"),
}), {status = "available", relations = {
    evolved("qg.evolved_recipe.soup", "Soup", "ingredient", {},
        "Can be added to soup as an ingredient", "수프에 재료로 넣을 수 있음"),
    evolved("qg.evolved_recipe.stew", "Stew", "spice", {"cooked"},
        "Can be added to stew as seasoning after cooking",
        "스튜에 양념으로 넣으려면 먼저 익혀야 함"),
}}, "KO", tr)
local withEvolvedRowsKo = Projection.visibleRows(withEvolvedKo, true, "")
for index, row in ipairs(withEvolvedRows) do
    assertEqual(row.identity, withEvolvedRowsKo[index].identity,
        "fixed locale identity/order parity " .. index)
end
local withEvolvedOnlyRowsKo = Projection.visibleEvolvedRows(withEvolvedKo, true, "")
for index, row in ipairs(withEvolvedOnlyRows) do
    assertEqual(row.identity, withEvolvedOnlyRowsKo[index].identity,
        "Evolved locale identity/order parity " .. index)
end

local sameDisplay = Projection.build(available({
    rightclick("mod.action.one", {EN = "Same", KO = "같음"}),
    rightclick("mod.action.two", {EN = "Same", KO = "같음"}),
}), "EN", tr)
assertEqual(2, sameDisplay.total, "duplicate labels retain distinct identities")

local groupedEvolved = Projection.build(available({}), {
    status = "available", relations = {
        evolved("qg.evolved_recipe.rice_pan", "RicePan", "spice", {},
            "Can be added to rice as seasoning", "밥에 양념으로 넣을 수 있음"),
        evolved("qg.evolved_recipe.rice_pot", "RicePot", "spice", {},
            "Can be added to rice as seasoning", "밥에 양념으로 넣을 수 있음"),
    },
}, "KO", tr)
local groupedRows = Projection.visibleEvolvedRows(groupedEvolved, true, "")
assertEqual(2, groupedEvolved.evolvedRecipeCount,
    "grouping preserves raw EvolvedRecipe relation count")
assertEqual(1, #groupedRows, "identical locale/role/condition rows group for display")
assertEqual(2, groupedRows[1].relationCount, "display group preserves multiplicity")
assertEqual(2, #groupedRows[1].identities, "display group preserves exact identities")
assertEqual("qg.evolved_recipe.rice_pan", groupedRows[1].identities[1],
    "display group preserves first exact identity")
assertEqual("qg.evolved_recipe.rice_pot", groupedRows[1].identities[2],
    "display group preserves second exact identity")

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

local denseCombinedLines = {}
for index = 1, 8 do
    table.insert(denseCombinedLines,
        recipe("uc.recipe.combined" .. index, "combined" .. index,
            "Combined " .. index, "결합 " .. index))
end
local denseCombined = Projection.build(available(denseCombinedLines), {
    status = "available", relations = {
        evolved("qg.evolved_recipe.dense", "Soup", "ingredient", {},
            "Can be added to soup as an ingredient", "수프에 재료로 넣을 수 있음"),
    },
}, "EN", tr)
local fixedWithoutEvolved = Projection.build(available(denseCombinedLines), "EN", tr)
assertEqual("small", denseCombined.density, "EvolvedRecipe does not make fixed rows dense")
assertEqual(fixedWithoutEvolved.density, denseCombined.density,
    "fixed density is unchanged when EvolvedRecipe is added")
local fixedWithoutEvolvedRows = Projection.visibleRows(fixedWithoutEvolved, true, "")
local fixedWithEvolvedRows = Projection.visibleRows(denseCombined, true, "")
assertEqual(#fixedWithoutEvolvedRows, #fixedWithEvolvedRows,
    "fixed visible row count is unchanged when EvolvedRecipe is added")
for index, row in ipairs(fixedWithoutEvolvedRows) do
    assertEqual(row.identity, fixedWithEvolvedRows[index].identity,
        "fixed identity/order is unchanged by EvolvedRecipe " .. index)
    assertEqual(row.recipe_nav_ref.recipe_id,
        fixedWithEvolvedRows[index].recipe_nav_ref.recipe_id,
        "fixed navigation is unchanged by EvolvedRecipe " .. index)
end
assertEqual("single", denseCombined.evolvedDensity, "EvolvedRecipe density is independent")
local denseEvolvedSearch = Projection.visibleEvolvedRows(denseCombined, false, "Soup")
assertEqual(1, #denseEvolvedSearch, "search reveals matching EvolvedRecipe relation")
assertEqual("qg.evolved_recipe.dense", denseEvolvedSearch[1].identity,
    "search preserves EvolvedRecipe identity")

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

local syntheticEvolvedNav = evolved(
    "qg.evolved_recipe.bad_nav", "Soup", "ingredient", {}, "Soup", "수프")
syntheticEvolvedNav.recipe_nav_ref = {recipe_id = "invented"}
assertEqual("fault", Projection.build(available({}), {
    status = "available", relations = {syntheticEvolvedNav},
}, "EN", tr).status, "synthetic EvolvedRecipe navigation fails")
assertEqual("fault", Projection.build(available({}), {
    status = "available", relations = {
        evolved("qg.evolved_recipe.bad_condition", "Soup", "ingredient", {"frozen"},
            "Soup", "수프"),
    },
}, "EN", tr).status, "unknown EvolvedRecipe condition fails")
assertEqual("fault", Projection.build(available({
    recipe("uc.recipe.survives", "survives", "Survives", "유지"),
}), {status = "fault", reason = "bad_lookup", relations = {}}, "EN", tr).status,
    "EvolvedRecipe lookup fault does not silently fall back to fixed rows")

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

package.preload["ISUI/ISButton"] = function() return true end
package.preload["ISUI/ISLabel"] = function() return true end
package.preload["ISUI/ISTextEntryBox"] = function() return true end

UIFont = {Small = "Small", Medium = "Medium"}
ISButton = {}
function ISButton:new(x, y, width, height, title, target, onclick)
    return {
        kind = "button", x = x, y = y, width = width, height = height,
        title = title, target = target, onclick = onclick,
        initialise = function() end,
    }
end
ISLabel = {}
function ISLabel:new(x, y, height, text)
    return {kind = "label", x = x, y = y, height = height, text = text}
end
ISTextEntryBox = {}
function ISTextEntryBox:new(text, x, y, width, height)
    local entry = {
        kind = "search", text = text, x = x, y = y, width = width, height = height,
        initialise = function() end, instantiate = function() end,
    }
    function entry:getInternalText() return self.text end
    return entry
end
function getTextManager()
    return {MeasureStringX = function(_, _, text) return #tostring(text) * 6 end}
end

local Detail = require("Iris/UI/Browser/IrisBrowserDetail")
local Renderer = require("Iris/UI/Browser/IrisBrowserInteractionRenderer")
local BrowserClass = {onRecipeGoToCrafting = function() end}
Detail.install(BrowserClass, {safeRequire = function() return false, nil end, tr = tr})

local saltRecipes = {}
for index = 1, 4 do
    table.insert(saltRecipes, recipe(
        "uc.recipe.salt" .. index, "salt" .. index,
        "Salt Recipe " .. index, "소금 레시피 " .. index
    ))
end
local saltEvolved = {}
for index = 1, 21 do
    table.insert(saltEvolved, evolved(
        "qg.evolved_recipe.salt" .. index, "Dish" .. index, "spice",
        index == 7 and {"cooked"} or {},
        "Can be added to dish " .. index .. " as seasoning" ..
            (index == 7 and " after cooking" or ""),
        index == 7 and ("요리 " .. index .. "에 양념으로 넣으려면 먼저 익혀야 함") or
            ("요리 " .. index .. "에 양념으로 넣을 수 있음")
    ))
end

local uiBrowser = setmetatable({
    currentSelectedFullType = "Base.Salt",
    detailPanel = {
        width = 360,
        children = {},
        addChild = function(self, child) table.insert(self.children, child) end,
    },
}, {__index = BrowserClass})
local uiDeps = {
    model = {
        interactionState = available(saltRecipes),
        evolvedRecipeState = {status = "available", relations = saltEvolved},
        locale = "KO",
    },
    tr = tr,
    browserGeneration = 7,
}
local renderUi
renderUi = function()
    uiBrowser.detailPanel.children = {}
    Renderer.render(
        uiBrowser, BrowserClass, uiBrowser.currentSelectedFullType, {}, 0, uiDeps
    )
end
function uiBrowser:showDetail(fullType, forceRebuild)
    assertEqual(self.currentSelectedFullType, fullType,
        "section callback rebuilds selected item")
    assertEqual(true, forceRebuild, "section callback forces detail rebuild")
    renderUi()
end
local function findButton(title)
    for _, child in ipairs(uiBrowser.detailPanel.children) do
        if child.kind == "button" and child.title == title then return child end
    end
    return nil
end
local function findSearch()
    for _, child in ipairs(uiBrowser.detailPanel.children) do
        if child.kind == "search" then return child end
    end
    return nil
end
local function rowCount(kind)
    local count = 0
    for _, child in ipairs(uiBrowser.detailPanel.children) do
        local matchesEvolved = kind == "evolved_recipe" and
            child.interactionRowSource == "evolved_recipe"
        local matchesPrefix = kind ~= "evolved_recipe" and child.kind == "label" and
            child.text:find("^" .. kind, 1, false)
        if matchesEvolved or matchesPrefix then
            count = count + 1
        end
    end
    return count
end
local function rowTexts(prefix)
    local texts = {}
    for _, child in ipairs(uiBrowser.detailPanel.children) do
        if child.kind == "label" and child.text:find("^" .. prefix, 1, false) then
            table.insert(texts, child.text)
        end
    end
    return texts
end
local function navigationCount()
    local count = 0
    for _, child in ipairs(uiBrowser.detailPanel.children) do
        if child.kind == "button" and child.recipe_nav_ref then count = count + 1 end
    end
    return count
end
local function click(button, label)
    assertEqual(true, button ~= nil, label .. " exists")
    button.onclick(button.target, button)
end

uiDeps.model.evolvedRecipeState = {status = "verified_empty", relations = {}}
renderUi()
assertEqual(4, rowCount("%[Recipe%]"), "KO Salt fixed-only view shows four Recipe names")
assertEqual(4, navigationCount(), "Salt fixed-only rows expose four navigation controls")

uiDeps.model.locale = "EN"
renderUi()
local fixedOnlyTexts = rowTexts("%[Recipe%]")
assertEqual(4, #fixedOnlyTexts, "locale transition preserves four Recipe names")
click(findButton("[-] Recipe (4)"), "EN Recipe section collapse control")
assertEqual(0, rowCount("%[Recipe%]"), "EN Recipe click collapses Recipe rows")
assertEqual(0, navigationCount(), "collapsed EN Recipe section hides navigation controls")
click(findButton("[+] Recipe (4)"), "EN Recipe section expand control")
assertEqual(4, rowCount("%[Recipe%]"), "EN Recipe click restores Recipe rows")
assertEqual(4, navigationCount(), "expanded EN Recipe section restores navigation controls")

uiDeps.model.evolvedRecipeState = {status = "available", relations = saltEvolved}
renderUi()
local fixedWithEvolvedTexts = rowTexts("%[Recipe%]")
assertEqual(#fixedOnlyTexts, #fixedWithEvolvedTexts,
    "adding Evolved preserves rendered fixed Recipe count")
for index, text in ipairs(fixedOnlyTexts) do
    assertEqual(text, fixedWithEvolvedTexts[index],
        "adding Evolved preserves rendered fixed Recipe name/order " .. index)
end
assertEqual(4, navigationCount(), "adding Evolved preserves fixed navigation controls")
assertEqual(0, rowCount("evolved_recipe"), "dense freeform section starts collapsed")
click(findButton("[+] Freeform Cooking (21)"), "freeform section expand control")
assertEqual(4, rowCount("%[Recipe%]"), "Evolved expansion preserves fixed Recipe rows")
assertEqual(21, rowCount("evolved_recipe"), "freeform section shows twenty-one food rows")
assertEqual(4, navigationCount(), "Evolved rows add no navigation")
for _, child in ipairs(uiBrowser.detailPanel.children) do
    if child.interactionRowSource == "evolved_recipe" then
        assertEqual(nil, child.text:find("%[Evolved%]"),
            "freeform row exposes no Evolved prefix")
        assertEqual(nil, child.text:find("%(Dish%d+%)"),
            "freeform row exposes no internal food type ID")
    end
    if child.kind == "button" then
        assertEqual(nil, child.title:find("Evolved"),
            "user-facing controls expose no Evolved term")
    end
end
click(findButton("[-] Freeform Cooking (21)"), "freeform section collapse control")
assertEqual(4, rowCount("%[Recipe%]"), "Evolved collapse preserves fixed Recipe rows")
assertEqual(0, rowCount("evolved_recipe"), "freeform section collapses its rows")

local search = findSearch()
assertEqual(true, search ~= nil, "dense Evolved section exposes separate search")
search.text = "Dish 7"
search.onTextChange()
assertEqual(4, rowCount("%[Recipe%]"), "Evolved search preserves fixed Recipe rows")
assertEqual(1, rowCount("evolved_recipe"), "search reveals matching collapsed Evolved row")
local retainedState = State.forEvolved(uiBrowser, 7, "EN", "Base.Salt", "dense")
assertEqual(false, retainedState.expanded, "same-generation rebuild retains Evolved collapse")
assertEqual("Dish 7", retainedState.query, "same-generation rebuild retains search state")

uiDeps.model.interactionState = {status = "verified_empty", lines = {}}
uiDeps.model.evolvedRecipeState = {status = "available", relations = {
    evolved("qg.evolved_recipe.salt_beer", "Beer", "spice", {},
        "Can be added to beer in a tumbler as seasoning",
        "텀블러에 담긴 맥주에 양념으로 넣을 수 있음"),
}}
local saltTransitionState = State.forEvolved(
    uiBrowser, 7, "EN", "Base.Salt", "single"
)
saltTransitionState.expanded = true
saltTransitionState.query = "beer"
renderUi()
assertEqual(1, rowCount("evolved_recipe"),
    "Salt transition fixture renders its exact beer relation")

uiBrowser.currentSelectedFullType = "Base.MushroomGeneric1"
uiDeps.model.evolvedRecipeState = {status = "available", relations = {
    evolved("qg.evolved_recipe.mushroom_soup", "Soup", "ingredient", {},
        "Can be added to soup as an ingredient", "수프에 재료로 넣을 수 있음"),
}}
renderUi()
assertEqual("", saltTransitionState.query,
    "item transition clears the previous Evolved search state")
local mushroomText = ""
local mushroomIdentityCount = 0
for _, child in ipairs(uiBrowser.detailPanel.children) do
    if child.interactionRowSource == "evolved_recipe" then
        mushroomText = mushroomText .. child.text
        for _, identity in ipairs(child.interactionIdentities or {}) do
            assertEqual("qg.evolved_recipe.mushroom_soup", identity,
                "Mushroom render contains only its exact relation identity")
            mushroomIdentityCount = mushroomIdentityCount + 1
        end
    end
end
assertEqual(true, mushroomIdentityCount > 0,
    "Mushroom transition renders an exact relation identity")
assertEqual(nil, mushroomText:lower():find("beer", 1, true),
    "Salt beer text does not leak into Mushroom")
assertEqual(nil, mushroomText:lower():find("tumbler", 1, true),
    "Salt container text does not leak into Mushroom")

local longDisplay = "Can be used to prepare a deliberately long freeform cooking target"
local widthBrowser = setmetatable({
    currentSelectedFullType = "Base.Long",
    detailPanel = {
        width = 140,
        children = {},
        addChild = function(self, child) table.insert(self.children, child) end,
    },
}, {__index = BrowserClass})
Renderer.render(widthBrowser, BrowserClass, "Base.Long", {}, 0, {
    model = {
        interactionState = {status = "verified_empty", lines = {}},
        evolvedRecipeState = {status = "available", relations = {
            evolved("qg.evolved_recipe.long", "Long", "base_item", {},
                longDisplay, "아주 긴 자유 조리 대상 준비에 사용할 수 있음"),
        }},
        locale = "EN",
    },
    tr = tr,
    browserGeneration = 8,
})
local wrapped = {}
for _, child in ipairs(widthBrowser.detailPanel.children) do
    if child.interactionRowSource == "evolved_recipe" then
        table.insert(wrapped, child.text)
    end
end
assertEqual(true, #wrapped > 1, "freeform row wraps to available detail width")
assertEqual(longDisplay, table.concat(wrapped), "freeform wrapping does not truncate semantics")

print("PASS browser interaction density acceptance")
