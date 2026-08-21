local TemplatesEn = {}

local templates = {
    ["Tool.1-A"] = {header="Tool - Construction/Crafting",lines={"Used to make, assemble, or shape other objects during crafting."}},
    ["Tool.1-B"] = {header="Tool - Dismantling/Opening",lines={"Used to open closed objects or separate joined parts for dismantling."}},
    ["Tool.1-C"] = {header="Tool - Maintenance",lines={"Used to tighten or loosen joined parts and keep them adjusted."}},
    ["Tool.1-D"] = {header="Tool - Cooking",lines={"Used while preparing and handling food or drinks."}},
    ["Tool.1-E"] = {header="Tool - Farming/Foraging",lines={"Used to gather or manage resources in the natural environment."}},
    ["Tool.1-F"] = {header="Tool - Medical",lines={"Used for medical actions such as treating wounds or physical conditions."}},
    ["Tool.1-G"] = {header="Tool - Trapping",lines={"Used for trapping activities such as hunting or fishing."}},
    ["Tool.1-H"] = {header="Tool - Light/Ignition",lines={"Used to provide light or start a fire."}},
    ["Tool.1-I"] = {header="Tool - Communication",lines={"Used to receive broadcasts or exchange information with others.","It may also play recorded speech or music."}},
    ["Tool.1-J"] = {header="Tool - Power",lines={"Used to generate electricity and supply power to nearby devices."}},
    ["Tool.1-K"] = {header="Tool - Security",lines={"Used to control access to locked doors, vehicles, and containers."}},
    ["Tool.1-L"] = {header="Tool - Storage Container",lines={"Used to store or carry other items."}},

    ["Combat.2-A"] = {header="Combat - Axe",lines={"Damage varies with the Axe combat skill.","Used for close-range chopping and cutting attacks."}},
    ["Combat.2-B"] = {header="Combat - Long Blunt",lines={"Damage varies with the Long Blunt combat skill.","Used for close-range striking attacks."}},
    ["Combat.2-C"] = {header="Combat - Short Blunt",lines={"Damage varies with the Short Blunt combat skill.","Used for close-range striking attacks."}},
    ["Combat.2-D"] = {header="Combat - Long Blade",lines={"Damage varies with the Long Blade combat skill.","Used for close-range cutting or thrusting attacks."}},
    ["Combat.2-E"] = {header="Combat - Short Blade",lines={"Damage varies with the Short Blade combat skill.","Used for close-range cutting or thrusting attacks."}},
    ["Combat.2-F"] = {header="Combat - Spear",lines={"Damage varies with the Spear combat skill.","Used for close-range thrusting attacks."}},
    ["Combat.2-G"] = {header="Combat - Handgun",lines={"A firearm that consumes ammunition to attack targets at range.","Affected by Aiming and Reloading skill levels."}},
    ["Combat.2-H"] = {header="Combat - Rifle",lines={"A firearm that consumes ammunition to attack targets at medium or long range.","Affected by Aiming and Reloading skill levels."}},
    ["Combat.2-I"] = {header="Combat - Shotgun",lines={"A firearm that consumes ammunition and fires a spread at close range.","Affected by Aiming and Reloading skill levels."}},
    ["Combat.2-J"] = {header="Combat - Thrown/Explosive",lines={"A thrown weapon that produces an effect such as an explosion, fire, or smoke."}},
    ["Combat.2-K"] = {header="Combat - Ammunition",lines={"Used and consumed when firing a firearm."}},
    ["Combat.2-L"] = {header="Combat - Firearm Part",lines={"Attached to a firearm to add or alter functions such as aiming or firing.","A screwdriver is often used when attaching or removing it."}},

    ["Consumable.3-A"] = {header="Consumable - Food",lines={"Consumed to affect hunger or other character stats."}},
    ["Consumable.3-B"] = {header="Consumable - Drink",lines={"Consumed to affect thirst or other character stats."}},
    ["Consumable.3-C"] = {header="Consumable - Medicine",lines={"Used to treat physical conditions such as wounds, illness, infection, or pain."}},
    ["Consumable.3-D"] = {header="Consumable - Recreational",lines={"Used or consumed to affect mental-state values such as stress or mood."}},
    ["Consumable.3-E"] = {header="Consumable - Herb",lines={"A natural material obtained through foraging and used for herbal tea or treatment."}},

    ["Resource.4-A"] = {header="Resource - Construction Material",lines={"Used to make structures or furniture during construction and crafting."}},
    ["Resource.4-B"] = {header="Resource - Cooking Ingredient",lines={"Used while preparing or processing food."}},
    ["Resource.4-C"] = {header="Resource - Medical Material",lines={"Used to make treatment or medical items."}},
    ["Resource.4-D"] = {header="Resource - Fuel",lines={"Used as fuel for vehicles, generators, or heating equipment."}},
    ["Resource.4-E"] = {header="Resource - Electronic Part",lines={"Used to make or repair electronic devices."}},
    ["Resource.4-F"] = {header="Resource - General Material",lines={"Used as a general-purpose material in crafting or assembly."}},

    ["Literature.5-A"] = {header="Literature - Skill Book",lines={"A book associated with a specific skill.","After reading, it increases experience gain within the book's skill-level range."}},
    ["Literature.5-B"] = {header="Literature - Recipe Magazine",lines={"Reading it unlocks specific crafting recipes permanently."}},
    ["Literature.5-C"] = {header="Literature - Map",lines={"Reading it reveals information about the corresponding area on the in-game map."}},
    ["Literature.5-D"] = {header="Literature - General Book",lines={"Read to affect mental-state values such as boredom."}},

    ["Wearable.6-A"] = {header="Clothing - Hat/Helmet",lines={"Worn on the head for protection, warmth, or shelter from the environment."}},
    ["Wearable.6-B"] = {header="Clothing - Upper Body",lines={"Worn on the upper body for protection, warmth, or shelter from the environment."}},
    ["Wearable.6-C"] = {header="Clothing - Lower Body",lines={"Worn on the lower body for protection, warmth, or shelter from the environment."}},
    ["Wearable.6-D"] = {header="Clothing - Gloves",lines={"Worn on the hands for protection, warmth, or shelter from the environment."}},
    ["Wearable.6-E"] = {header="Clothing - Footwear",lines={"Worn on the feet for protection, warmth, or shelter from the environment."}},
    ["Wearable.6-F"] = {header="Clothing - Backpack",lines={"Worn to store possessions and reduce the burden of carrying them."}},
    ["Wearable.6-G"] = {header="Clothing - Accessory",lines={"Worn on the body for decoration or to support a function."}},

    ["Furniture.7-A"] = {header="Furniture - Movable",lines={"Can be removed from the world, placed in inventory, and installed elsewhere."}},
    ["Vehicle.8-A"] = {header="Vehicle - Running Gear",lines={"A major component that affects vehicle performance or operating condition."}},
    ["Vehicle.8-B"] = {header="Vehicle - Body/Accessory",lines={"A component of a vehicle's structure or exterior, such as the body, seat, door, window, or trunk."}},
    ["Misc.9-A"] = {header="Miscellaneous",lines={"A small general item that may be used or stored in different situations."}},
}

function TemplatesEn.getTemplate(subcatId)
    return templates[subcatId]
end

function TemplatesEn.getAllIds()
    local ids = {}
    for id, _ in pairs(templates) do table.insert(ids, id) end
    return ids
end

return TemplatesEn
