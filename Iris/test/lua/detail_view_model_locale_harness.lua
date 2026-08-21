local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local locale = "EN"
local interactionLookupCount = 0
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
            _getDescriptionState=function()
                interactionLookupCount = interactionLookupCount + 1
                return {
                    status="verified_empty", reason="lookup_miss", fallback_used=false,
                    entry=nil, lines={}, exclusion_lines={}, debug_lines={},
                }
            end,
            getUseCaseLines=function() error("ViewModel must consume the status-bearing lookup") end,
            getCapabilities=function() return {} end,
        },
    }
end
package.preload["Iris/Data/layer3_renderer"] = function()
    return {
        getPublishState=function() return "published" end,
        getText=function(_, options)
            if options and options.locale == "EN" then return "English Layer 3 description" end
            return "한국어 3계층 설명"
        end,
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
assert(english.layer3.raw == "English Layer 3 description")
assert(korean.layer3.raw == "한국어 3계층 설명")
assert(english.layer3.display ~= nil)
assert(korean.layer3.display ~= nil)
assert(english.interactionState.status == "verified_empty")
assert(english.useCases.status == english.interactionState.status)
assert(english.useCases.reason == english.interactionState.reason)
assert(interactionLookupCount == 2)
assert(englishCore ~= koreanCore)
assert(Sections.renderFoodSection(english):find("%-1600") ~= nil)
assert(not pcall(function() english.fullType = "Base.Mutated" end))
assert(not pcall(function() english.food.hunger = 0 end))
assert(not pcall(function() english.tags[1] = "Mutated" end))

local englishLookup = require("Iris/Data/IrisLayer3EnglishLookup")
local hammerText = englishLookup.get("Base.HammerStone")
assert(hammerText and hammerText:find("construction", 1, true))
for index = 1, #hammerText do assert(string.byte(hammerText, index) < 128) end
local TemplatesKo = require("Iris/Logic/IrisDesc/Templates")
local TemplatesEn = require("Iris/Logic/IrisDesc/TemplatesEn")
assert(TemplatesKo.getTemplate("Combat.2-C").header ~= TemplatesEn.getTemplate("Combat.2-C").header)
assert(TemplatesEn.getTemplate("Combat.2-C").header == "Combat - Short Blunt")

print("IRIS_DETAIL_LOCALE_PASS localized_layer2=true localized_layer3=true availability_equal=true labels_differ=true nested_readonly=true interaction_lookup_once_per_build=true")
