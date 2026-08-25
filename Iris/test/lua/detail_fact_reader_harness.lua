local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local FactReader = require("Iris/UI/Detail/IrisItemFactReader")
local Presentation = require("Iris/UI/Detail/IrisItemDetailPresentation")

local function base(itemType)
    local item = {}
    function item:getType() return itemType end
    return item
end

local food = base("Food")
function food:getHungerChange() return -0.2 end
local foodFacts = FactReader.read(food)
assert(foodFacts.food.hunger.state == "known" and foodFacts.food.hunger.value == -0.2)
assert(foodFacts.weapon.minDamage.state == "not_applicable")

local weapon = base("Weapon")
function weapon:getMinDamage() error("unavailable") end
function weapon:getMaxDamage() return 2 end
local weaponFacts = FactReader.read(weapon)
assert(weaponFacts.weapon.minDamage.state == "unknown")
assert(weaponFacts.weapon.maxDamage.state == "known")
assert(weaponFacts.weapon.minDamage.value == nil)

local literature = base("Literature")
function literature:getNumberOfPages() return 120 end
local literatureFacts = FactReader.read(literature)
assert(literatureFacts.literature.numberOfPages.state == "known")

local moveable = base("Moveable")
function moveable:getCapacity() return 25 end
local moveableFacts = FactReader.read(moveable)
assert(moveableFacts.moveable.capacity.state == "known")

local unknown = base("Normal")
local unknownFacts = FactReader.read(unknown)
assert(unknownFacts.food.hunger.state == "not_applicable")
assert(unknownFacts.weapon.minDamage.state == "not_applicable")
assert(unknownFacts.literature.numberOfPages.state == "not_applicable")
assert(unknownFacts.moveable.capacity.state == "not_applicable")

local model = {
    factStates = {
        core = { weight = {state="known"} },
        food = {
            hunger={state="known"}, thirst={state="unknown"},
            stress={state="not_applicable"}, boredom={state="not_applicable"},
            calories={state="unknown"},
        },
        weapon = {
            minDamage={state="unknown"}, maxDamage={state="known"},
            conditionMax={state="known"},
        },
        moveable = { capacity={state="known"} },
    },
    weight=0.5,
    food={hunger=-0.2,thirst=nil,stress=nil,boredom=nil,calories=nil},
    weapon={minDamage=nil,maxDamage=2,conditionMax=10},
    moveable={capacity=25},
}
local snapshot = Presentation.semanticSnapshot(model)
local tooltip = Presentation.tooltipFacts(model, 99)
assert(#tooltip <= 4)
for _, row in ipairs(snapshot) do
    if row.factState ~= "known" then assert(row.visible == false) end
end

print("IRIS_DETAIL_FACT_READER_PASS fixtures=5 tooltip_max=4 unknown_is_silent=true")
