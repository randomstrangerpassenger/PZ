--[[
    IrisBrowserInteractionCollector.lua

    Interaction collection for the IrisBrowser detail panel (recipe + capability).
    Split out of IrisBrowserInteractionRenderer (Change 9b) — collection logic
    only; UI row rendering stays in IrisBrowserInteractionRenderer.

    Pure-ish: all data deps are passed in (fullType/item/IrisAPI/ucDescData/tr);
    behaviour byte-identical to the former local functions.
]]

local IrisBrowserInteractionCollector = {}
local ProtectedCall = require("Iris/Util/IrisProtectedCall")

function IrisBrowserInteractionCollector.collectRecipeInteractions(fullType, item, IrisAPI, ucDescData)
    local interactionItems = {}
    local recipeNameSet = {}
    local hasOfflineRecipes = false

    if ucDescData and ucDescData[fullType] then
        local ucDesc = ucDescData[fullType]
        if ucDesc and ucDesc.lines then
            for _, line in ipairs(ucDesc.lines) do
                if line.surface == "recipe_ui" or line.surface == "both" then
                    local recipeName = line.recipe_translated_name
                        or line.recipe_original_name
                        or line.display_text
                    if not recipeNameSet[recipeName] then
                        recipeNameSet[recipeName] = true
                        hasOfflineRecipes = true
                        table.insert(interactionItems, {
                            type = "recipe",
                            name = recipeName,
                            label_key = line.label_key,
                            sortKey = "1_" .. (line.label_key or ""),
                            recipe_nav_ref = line.recipe_nav_ref,
                            recipe_requirements = line.recipe_requirements,
                        })
                    end
                end
            end
        end
    end

    if not hasOfflineRecipes then
        local recipeList = {}
        if IrisAPI and IrisAPI.Index and IrisAPI.Index.getRecipeConnectionsForItem then
            local ok, list = ProtectedCall.data(function() return IrisAPI.Index.getRecipeConnectionsForItem(item) end)
            if ok and list then recipeList = list end
        end
        for _, e in ipairs(recipeList) do
            local name = tostring(e.recipe or "Unknown")
            if not recipeNameSet[name] then
                recipeNameSet[name] = true
                local trName = nil
                if getText then
                    local trKey = "Recipe_" .. name:gsub(" ", "_")
                    local trOk, trResult = ProtectedCall.engine(getText, trKey)
                    if trOk and trResult and trResult ~= trKey then
                        trName = trResult
                    end
                end
                local fallbackReqs = nil
                if ucDescData and ucDescData._requirementsLookup then
                    fallbackReqs = ucDescData._requirementsLookup[name]
                end
                table.insert(interactionItems, {
                    type = "recipe",
                    name = trName or name,
                    sortKey = "1_" .. name,
                    recipe_nav_ref = {
                        original_name = name,
                        translated_name = trName,
                        category = nil,
                    },
                    recipe_requirements = fallbackReqs,
                })
            end
        end
    end

    return interactionItems
end

function IrisBrowserInteractionCollector.collectCapabilityInteractions(fullType, IrisAPI, tr)
    local capabilityList = {}
    if IrisAPI and IrisAPI.UseCases and IrisAPI.UseCases.getCapabilities then
        local ok, caps = ProtectedCall.data(function() return IrisAPI.UseCases.getCapabilities(fullType) end)
        if ok and caps then capabilityList = caps end
    end

    local capabilityLabelMap = {
        can_extinguish_fire = "Iris_Cap_ExtinguishFire",
        can_add_generator_fuel = "Iris_Cap_AddGeneratorFuel",
        can_scrap_moveables = "Iris_Cap_ScrapMoveables",
        can_open_canned_food = "Iris_Cap_OpenCannedFood",
        can_stitch_wound = "Iris_Cap_StitchWound",
        can_remove_embedded_object = "Iris_Cap_RemoveEmbeddedObject",
        can_attach_weapon_mod = "Iris_Cap_AttachWeaponMod",
    }

    local interactionItems = {}
    for _, capId in ipairs(capabilityList) do
        local labelKey = capabilityLabelMap[capId]
        local displayName = labelKey and tr(labelKey, capId) or capId
        table.insert(interactionItems, {type = "rightclick", name = displayName, sortKey = "0_" .. displayName})
    end
    return interactionItems
end

return IrisBrowserInteractionCollector
