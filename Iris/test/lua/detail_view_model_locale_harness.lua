local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local locale = "EN"
package.preload["Iris/Util/IrisTranslationResolver"] = function()
    return {
        getLangKey=function() return locale end,
        get=function(key, fallback) return locale .. ":" .. (fallback or key) end,
    }
end
package.preload["Iris/IrisAPI"] = function()
    return {
        Tags={getTagsForItem=function() return { ["Consumable.3-A"]=true } end},
        Index={
            getRecipeConnectionsForItem=function() return {} end,
            getMoveablesInfoForItem=function() return nil end,
            getFixingInfoForItem=function() return nil end,
        },
        UseCases={
            getUseCaseLines=function() return {lines={},debug_lines={}} end,
            getCapabilities=function() return {} end,
        },
    }
end

local item = {}
function item:getFullType() return "Base.LocaleFood" end
function item:getFullName() return "Base.LocaleFood" end
function item:getDisplayName() return "Locale Food" end
function item:getModule() return "Base" end
function item:getType() return "Food" end
function item:getActualWeight() return 0.2 end
function item:getHungerChange() return -16 end
function item:getThirstChange() return -7 end
function item:getStressChange() return 0 end
function item:getBoredomChange() return 0 end
function item:getCalories() return 10 end

local ViewModel = require("Iris/UI/Detail/IrisItemDetailViewModel")
local Sections = require("Iris/UI/Wiki/IrisWikiSections")

locale = "EN"
local english = ViewModel.fromItem(item)
local englishCore = Sections.renderCoreInfoSection(english)
locale = "KO"
local korean = ViewModel.fromItem(item)
local koreanCore = Sections.renderCoreInfoSection(korean)

assert(english.locale == "EN" and korean.locale == "KO")
assert(english.fullType == korean.fullType and english.weight == korean.weight)
assert(english.food.hunger == korean.food.hunger and english.food.thirst == korean.food.thirst)
assert(english.availability.food == korean.availability.food)
assert(english.availability.layer3 == korean.availability.layer3)
assert(englishCore ~= koreanCore)
assert(Sections.renderFoodSection(english):find("%-1600") ~= nil)
assert(not pcall(function() english.fullType = "Base.Mutated" end))

print("IRIS_DETAIL_LOCALE_PASS raw_equal=true availability_equal=true labels_differ=true")
