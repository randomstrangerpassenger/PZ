from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil

from .dvf_3_3_generation_contract import (
    CANONICAL_INPUTS,
    canonical_input_identity,
    repository_path,
)
from .repository_context import require_repository_context


CURRENT_POINTER_RELATIVE_PATH = "Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"
CURRENT_GENERATION_ROOT_RELATIVE_PATH = (
    "Iris/media/lua/client/Iris/Data/IrisLayer3Generations"
)
TOOLTIP_T1_OWNER_OUTPUT_RELATIVE_PATH = (
    "Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json"
)
TOOLTIP_T1_D3_REGISTRY_RELATIVE_PATH = (
    "Iris/_docs/authority/dvf/tooltip_t1_d3_disposition_registry.json"
)


PRIMARY_USE_SOURCE_SHA256 = "b666b26a3f338cde19e57abfdb4356fa23092af206806f7e063953987afc6d66"

# This list is aligned with the sorted, distinct primary_use values in the
# current Layer 3 facts. The source hash prevents a changed fact set from being
# paired with stale localization.
PRIMARY_USE_EN = [
    "Junk with no specific crafting use in Build 41.",
    "A television used to watch broadcasts or play recorded VHS tapes.",
    "A television used to watch broadcasts.",
    "A chew toy for dogs.",
    "Canned beans opened or put in a bowl to prepare a bean dish.",
    "Canned mushroom soup opened or put in a pot to prepare soup.",
    "Canned soup opened or put in a pot to prepare soup.",
    "A can opened to obtain its potatoes.",
    "A can opened to obtain its fruit beverage.",
    "A can opened to obtain its fruit cocktail.",
    "Canned pet food that can be opened to obtain its contents.",
    "A can opened to obtain its carrots.",
    "A can opened to obtain its peaches.",
    "A can opened to obtain its bolognese contents.",
    "A can opened to obtain its condensed milk.",
    "A can opened to obtain its corn.",
    "A can opened to obtain its peas.",
    "A can opened to obtain its sardines.",
    "A can opened to obtain its tuna.",
    "A can opened to obtain its chili.",
    "A can opened to obtain its corned beef.",
    "A can opened to obtain its tomatoes.",
    "A can opened to obtain its pineapple.",
    "Used to shape or fit material into other tool parts during construction or crafting preparation.",
    "A rubber duck whose battery can be inserted or removed.",
    "A battery-powered flashlight used to illuminate the surroundings.",
    "A nail used in construction or crafting.",
    "Sporting equipment used according to the rules of a game or activity.",
    "A toy shaped like a rubber duck.",
    "A magazine that teaches knowledge required for work on performance vehicles.",
    "A splint used to immobilize a fracture.",
    "Handled when arranging a space by placing or removing decorations, exhibits, signs, or area markers.",
    "Medicine taken to reduce panic.",
    "Handled when placing or throwing a noise-making device as a distraction.",
    "A bulb used in lights that accept replacement bulbs.",
    "A tool used to destroy structures.",
    "An accessory worn on the upper ear.",
    "An accessory worn on the ears.",
    "Prepared food that can be divided into bowls for eating.",
    "A tool that can be used for melee attacks.",
    "An item that can be used for melee attacks.",
    "A tool that can be used for melee attacks.",
    "Usable for melee attacks or as a spear attachment.",
    "Used to thrust or push from a distance in close combat.",
    "Used to swing, strike, or push in close combat.",
    "A weapon used in close combat.",
    "A metal pipe used as material in metalworking.",
    "A small metal sheet used as material for producing metal sheets.",
    "A metal sheet used as material for producing smaller metal sheets.",
    "Used as material for metal structures and certain metal items.",
    "A tool used for metal forging.",
    "A metal bar used to make metal barricades.",
    "A magazine that teaches how to build metal walls and roofs.",
    "A magazine that teaches how to build metal containers.",
    "A magazine that teaches recipes for metal cutlery and cookware.",
    "A magazine that teaches how to build metal fences.",
    "A consumable material used when welding structures such as metal fences and doors.",
    "A tool used for joining metal.",
    "Used in metal crafting to melt or hammer material into other parts.",
    "Scrap left by metal dismantling that cannot be used as material.",
    "A magazine that teaches recipes for making metal sheets.",
    "A writing tool used for documents or map annotations.",
    "Cosmetics used as a base layer of makeup.",
    "A weapon that produces an explosion when triggered.",
    "A needle used to stitch deep wounds.",
    "Broken glass that requires care when approached or cleared.",
    "A cord-like material.",
    "A magazine that teaches how to craft wooden box and stick traps.",
    "Used with a branch or stick to kindle a campfire.",
    "A small fish used as bait when fishing with a rod.",
    "An artificial lure used when fishing with a rod.",
    "A magazine that teaches how to craft and repair fishing rods.",
    "Fishing line used to make or repair fishing rods.",
    "A material used to make and repair fishing rods.",
    "It can be repaired into a fishing rod by attaching line.",
    "A device used to play recorded CDs.",
    "Handled during play with boards, cards, pieces, or small toys.",
    "Eyewear worn over the eyes.",
    "Cosmetics used around the eyes.",
    "Face paint used to add a pattern around the eyes.",
    "Eye shadow used to add color around the eyes.",
    "An underwear accessory worn on the leg.",
    "Underwear worn on the legs.",
    "An herbal poultice applied to an injured body part.",
    "A ball used for throwing.",
    "Exercise equipment used for dumbbell presses and biceps curls.",
    "Material used to make traps and fishing nets.",
    "A portable container for carrying tools or other items.",
    "A tool.",
    "A stone used to make a stone hammer.",
    "A magazine that teaches how to attach motion sensors.",
    "A tool used to dig soil for cultivation.",
    "A radio used to listen to broadcasts or play recorded CDs.",
    "A material or component used to craft radios or two-way radios.",
    "An alcoholic drink that can be consumed or used as a cooking ingredient.",
    "Drinking it can reduce thirst.",
    "A wet towel that can be used to dry the body again once it has dried.",
    "Fabric used to make a mattress or campfire kit.",
    "A material used to make a mattress.",
    "Hair gel used to style hair.",
    "Clothing worn on the head or face.",
    "A comb used to arrange and groom hair.",
    "Hair dye used to change hair color.",
    "Clothing or an accessory worn on the head.",
    "Equipment worn on the head.",
    "A tray used to prepare muffin batter.",
    "A tray of batter used to bake muffins and remove them as portions.",
    "A soup or stew that can be eaten or divided into bowls.",
    "A tool used for shaving.",
    "Used as fuel for fires such as campfires.",
    "A piece of wood usable as campfire fuel.",
    "A kit used to place a campfire.",
    "A twig used to prepare campfire material.",
    "Fuel added to campfires or charcoal barbecues.",
    "Plank material used in carpentry and other crafting.",
    "Clothing worn around the neck.",
    "A long necklace worn around the neck.",
    "A necklace worn around the neck.",
    "An accessory worn around the neck.",
    "A robe worn on the body.",
    "Outerwear worn on the body.",
    "Worn on the body as part of an outfit or for a specific function.",
    "An accessory worn on the body.",
    "A medical tool used to remove embedded glass or bullets.",
    "Clothing worn on or around the body.",
    "A one-piece garment worn on the body.",
    "A full-body garment.",
    "A decorative tail worn on the body.",
    "Underwear worn on the body.",
    "Perfume used to add fragrance to the body.",
    "Used to dry the body or to remove blood stains with bleach.",
    "A cleanser used when washing blood and dirt from the body or clothing.",
    "Clothing worn over the torso.",
    "A vest worn over the torso.",
    "A magazine that teaches recipes for nails, hinges and small metal tools.",
    "A tool used to build wooden structures with nails.",
    "A hammer usable for building wooden structures with nails.",
    "Rope material used in crafting that requires tying or connecting.",
    "Untie the bundle to take out logs.",
    "Stationery used to write or revise documents or organize paper.",
    "Used to build structures that require hinges, such as doors or gates.",
    "A handle component used to build doors or drawers.",
    "A sack used to carry items.",
    "A portable container used to carry items.",
    "An ingredient mixed with water to make gravy.",
    "A material mixed with water to make a bucket of plaster.",
    "An ingredient mixed with water to make pancakes.",
    "A fishing net trap placed in water to catch bait fish.",
    "An empty container used to hold water or prepare crop-treatment sprays.",
    "A vessel used to hold water.",
    "A spray container used to store and supply water.",
    "An empty bottle used to carry water.",
    "A container used to carry water.",
    "An empty container that can be reused to carry water.",
    "A metal drum used to collect water or burn wood into charcoal.",
    "A fishing rod used with bait to catch fish.",
    "A baited trap used to catch birds.",
    "A baited trap used to catch mice and rats.",
    "A baited trap used to catch rabbits or squirrels.",
    "A tool usable for removing barricades.",
    "Exercise equipment used for barbell curls.",
    "A collar worn by a pet dog.",
    "An ingredient used in doughs and some fried dishes.",
    "A tool used to roll dough when preparing foods such as pies, pizzas and bread.",
    "A cooking utensil used to prepare foods such as dough and omelettes.",
    "Footwear worn on the feet.",
    "Socks worn on the feet.",
    "A magazine that teaches knowledge needed to connect and repair generators.",
    "An accessory worn at the navel.",
    "Used to secure structures that support combination padlocks.",
    "Used to chop or cut trees while logging.",
    "Open the jar to take out its vegetables.",
    "A jar opened to obtain cabbage.",
    "Handled to store, carry, or divide possessions and contents.",
    "Open the packet to obtain seeds for planting.",
    "Can be dismantled to recover a motion sensor.",
    "Can be dismantled to recover electronic scrap.",
    "Can be dismantled to recover an amplifier component.",
    "Flint used to make a spark.",
    "A bag of dirt that can be used to put out fires.",
    "A candle that provides light when lit.",
    "Can be burned as tinder or fuel.",
    "An incendiary weapon used to start fires.",
    "An extinguisher used to put out fires on squares or characters.",
    "A tray of dough used to bake biscuits and remove them as portions.",
    "Handled when emptying, sorting, reusing, or disposing of leftover cans and containers.",
    "An ingredient used to make doughs such as bread dough.",
    "A magazine that teaches recipes for bread dough, biscuits and pizza.",
    "A double-barrel shotgun used for shooting.",
    "A shotgun used for shooting.",
    "A rifle used for shooting.",
    "A firearm used for shooting.",
    "A frame used to hold a photograph or picture.",
    "Worn gear that increases reload speed for guns using non-shotgun ammunition.",
    "Worn gear that increases reload speed for guns using shotgun shells.",
    "A magazine that teaches knowledge required for work on commercial vehicles.",
    "Underwear worn on the upper body.",
    "A magazine that teaches how to craft box and cage traps.",
    "Open the box to take out .223 ammunition.",
    "Open the box to take out .308 ammunition.",
    "Open the box to take out .38 Special ammunition.",
    "Open the box to take out .44 Magnum ammunition.",
    "Open the box to take out .45 Auto ammunition.",
    "Open the box to take out .556 ammunition.",
    "Open the box to take out 9mm ammunition.",
    "Can be opened to remove screws.",
    "Can be opened to remove nails.",
    "Can be opened to remove several empty bottles.",
    "Open the box to take out shotgun shells.",
    "Open the box to take out paperclips.",
    "Medicine used to treat wound infections.",
    "A medical tool that assists with stitching wounds and removing embedded glass or bullets.",
    "A disinfectant used to disinfect wounds.",
    "A consumable used to disinfect wounds.",
    "Bandaging material used to cover wounds.",
    "Cloth material used to bandage wounds or make some tools and splints.",
    "A bandage applied to wounds.",
    "Dirty bandaging material that can be applied to wounds.",
    "Outerwear worn on the upper body.",
    "Clothing worn on the upper body.",
    "Clothing worn on the upper body.",
    "Clothing worn over the upper and lower body.",
    "Long underwear worn on the upper and lower body.",
    "Handled while cleaning the body or surroundings and gathering household consumables.",
    "A component used to build a small table with a drawer.",
    "Plaster used to finish structures that support plastering.",
    "A stone used to make stone tools or carve a spear.",
    "Handled when removing or reinstalling devices and fixed fixtures.",
    "A reusable device that makes a sound after a set delay.",
    "Consuming it can reduce hunger.",
    "Consuming it can reduce hunger. Eating it raw can be dangerous.",
    "Consuming it can reduce hunger. It is poisonous.",
    "Consuming it can reduce hunger. It is also used as a cooking ingredient.",
    "Consuming it can reduce hunger. It is also used as a cooking ingredient. Eating it raw can be dangerous.",
    "Consuming it can reduce hunger but increases thirst.",
    "Consuming it can reduce hunger but increases thirst. Eating it raw can be dangerous.",
    "Consuming it can reduce hunger but increases thirst. It is also used as a cooking ingredient.",
    "Eating it can reduce hunger and thirst; it can also be used as a cooking ingredient.",
    "Consuming it can reduce hunger and thirst.",
    "Consuming it can reduce hunger and thirst. It is also used as a cooking ingredient.",
    "Consuming it can reduce hunger and thirst. It is also used as a cooking ingredient. If poisonous, it increases food sickness.",
    "Consuming it can reduce hunger and thirst. It is also used as a cooking ingredient.",
    "A material used to make alcohol-soaked cotton balls.",
    "A small bell that makes sound.",
    "A magazine that teaches how to craft a noise maker.",
    "Handled when carrying cash, cards, and a wallet.",
    "Clothing worn on the hands.",
    "An umbrella that protects from rain when held and can be folded.",
    "Supplies power to battery-operated devices such as flashlights.",
    "It can be cut up to obtain frog meat.",
    "A pot used to prepare or hold soup.",
    "Medicine used to reduce unhappiness over time.",
    "A clock used to check the time or set an alarm.",
    "Used to cut ingredients or butcher small animals, and can also serve as a melee weapon.",
    "An electronic device used to check signals or operate equipment.",
    "Handled when moving chairs, tables, or resting furniture into position indoors.",
    "Handled when moving storage furniture or containers into position indoors.",
    "A water-filled cooking pot used to prepare rice or pasta dishes.",
    "A water-filled saucepan used to prepare rice or pasta dishes.",
    "Rice or pasta prepared for cooking and serving in bowls.",
    "A magazine that teaches how to identify poisonous wild berries and mushrooms.",
    "Opened for rain protection or folded for carrying outdoors.",
    "A tool used to grind herbs into poultices.",
    "Face paint used to add a pattern across the face.",
    "Equipment worn over the face and eyes.",
    "Clothing or equipment worn on the face.",
    "Material used to make an aerosol bomb.",
    "A material used to make an aerosol bomb.",
    "Handled during leisure when viewing or collecting photos, recordings, souvenirs, or toys.",
    "A magazine that teaches recipes for metal tools and containers.",
    "Used to transfer or add fuel.",
    "An empty container used to carry fuel.",
    "A magazine that teaches how to craft a smoke bomb.",
    "Material used to make a smoke bomb.",
    "Used to operate the lock of a matching door.",
    "Used to unlock a matching padlock.",
    "Used to operate the matching vehicle.",
    "A container used to carry keys.",
    "A ring worn on the right ring finger.",
    "An accessory worn on the right wrist.",
    "A magazine that teaches how to craft a snare trap.",
    "A button attached to clothing or fabric goods.",
    "Wine poured into a wine glass for drinking.",
    "A ring worn on the left ring finger.",
    "An accessory worn on the left wrist.",
    "Coal used as furnace fuel.",
    "A propane tank used to refill a welding torch.",
    "A magazine that teaches how to craft and attach remote triggers.",
    "An electronic component used to make a remote trigger.",
    "A magazine that teaches how to craft remote controllers.",
    "An adhesive used to assemble devices such as remote controllers and timers.",
    "An electronic component used to make a remote controller.",
    "A map referenced for navigation and route planning.",
    "A bowl used to hold food or mix dough.",
    "Used to disinfect or medicate wounds during treatment.",
    "Used to mend clothing or reinforce it with leather patches.",
    "Opened and referenced to check a location while planning travel.",
    "Toothpaste used to brush teeth.",
    "A toothbrush used to brush teeth.",
    "A magazine that teaches knowledge required for work on standard vehicles.",
    "A welding mask required for some metalworking tasks.",
    "An ingredient used in some doughs and fried dishes.",
    "Used to repair certain damaged weapons or tools.",
    "Reading material that can reduce boredom, stress and unhappiness.",
    "Reading material that can reduce boredom and stress.",
    "Reading it teaches the corresponding makeshift radio recipe.",
    "Cosmetics used to add color to the lips.",
    "Open the sack to take out its produce.",
    "Used to lock structures that support padlocks.",
    "A device that produces noise when triggered.",
    "A device that produces smoke when triggered.",
    "Fertilizer used to shorten the time to a crop's next growth stage.",
    "A spray used to reduce flies affecting crops.",
    "A spray used to reduce mildew in crops.",
    "A magazine that teaches recipes for mildew and pest treatment sprays for crops.",
    "A fruit that is sliced or smashed into portions for eating.",
    "Medicine taken to help with falling asleep.",
    "An adhesive material used to assemble devices or attach tools to spears.",
    "A material.",
    "A pan used to prepare ingredients for roasting.",
    "A pan used to prepare stir-fries by adding ingredients.",
    "A tool used to clear ashes or remove blood stains with bleach.",
    "Used to remove and plant seeds while preparing cultivation.",
    "A needle used for sewing.",
    "A skill book that increases Metalworking XP gain when read at the applicable level.",
    "A skill book that increases Fishing XP gain when read at the applicable level.",
    "A skill book that increases Farming XP gain when read at the applicable level.",
    "A skill book that increases Trapping XP gain when read at the applicable level.",
    "A skill book that increases Carpentry XP gain when read at the applicable level.",
    "A skill book that increases Cooking XP gain when read at the applicable level.",
    "A skill book that increases First Aid XP gain when read at the applicable level.",
    "A skill book that increases Tailoring XP gain when read at the applicable level.",
    "A skill book that increases Electrical XP gain when read at the applicable level.",
    "A skill book that increases Mechanics XP gain when read at the applicable level.",
    "A skill book that increases Foraging XP gain when read at the applicable level.",
    "Installed to supply electricity to nearby devices.",
    "Clothing worn over the whole body.",
    "Used with tinder or fuel to light a campfire.",
    "Consumable material used in crafting or repair.",
    "Handled during food preparation or cooking.",
    "Food used while preparing or eating a meal.",
    "An ingredient used in cooking.",
    "A screw used in assembly or repair.",
    "Handled with tableware and place-setting items during kitchen work or meal preparation.",
    "A radio used to tune in to broadcasts.",
    "A two-way radio used to transmit and receive on a tuned frequency.",
    "A branch used to make improvised tools, spears or splints.",
    "A tool used to erase map annotations.",
    "An ingredient used to make a plantain poultice.",
    "A spear used for thrusting melee attacks.",
    "A tire fitted to a vehicle wheel that affects traction.",
    "A replacement component for a vehicle's suspension.",
    "Parts used to repair the condition of a vehicle engine.",
    "Handled when removing or reinstalling a vehicle body panel or window.",
    "A brake component used for vehicle braking.",
    "Used to install or remove vehicle tires.",
    "Used to adjust the air pressure in vehicle tires.",
    "A vehicle seat used for sitting or holding items.",
    "A tank fitted to a vehicle to store fuel.",
    "A vehicle storage component used to hold items.",
    "Used to recharge a battery removed from a vehicle.",
    "A battery that supplies power for starting a vehicle and operating its electrical devices.",
    "A muffler component that affects vehicle engine noise.",
    "Material used to brew tea.",
    "Worn on the body as active clothing.",
    "A sheet rope installed at suitable windows or railings for climbing.",
    "An ingredient used to can vegetables.",
    "A lid used with an empty jar when canning vegetables.",
    "An empty jar used to can vegetables.",
    "Thread used to craft fabric items or stitch wounds together with a needle.",
    "A broken fish trap from which wire can be recovered.",
    "Used in carpentry work to build barbed-wire fences.",
    "Toxic bleach used with cleaning tools to remove blood stains.",
    "Handled when tuning a portable radio to listen to broadcasts.",
    "A part used to modify firearms.",
    "A magazine used to load a firearm.",
    "Paint used for coating or leaving marks.",
    "A material used to build a bed.",
    "An ingredient used to prepare coffee drinks.",
    "An ingredient used to make a comfrey poultice.",
    "Beer poured into a cup for drinking.",
    "A drink mixed from ingredients in a cup.",
    "A magazine that teaches recipes for cake, pie and cookie doughs.",
    "A flour ingredient used to make dough or batter for foods such as cakes and pies.",
    "A pan used to prepare cake or pie dough for baking.",
    "An accessory worn on the nose.",
    "A baking tray used to prepare cookie dough.",
    "An electronic component used to make a timer.",
    "A magazine that teaches how to craft and attach timers.",
    "Used to install or remove certain vehicle parts, such as tires and brakes.",
    "A mold used to cast ammunition.",
    "A magazine that teaches recipes for ammunition, molds and some metal weapons.",
    "Beer poured into a tumbler for drinking.",
    "A drink mixed from ingredients in a tumbler.",
    "A material used to make a tent kit.",
    "A kit used to pitch a tent.",
    "A log used to make planks with a saw or to craft a campfire kit.",
    "A sawing tool also used to shorten shotgun barrels.",
    "A saw used to cut logs into planks.",
    "A magazine that teaches how to craft a fishing net trap and reclaim its wire.",
    "A tool used to open cans of food.",
    "Medicine taken to relieve pain.",
    "Batter placed in a baking pan to prepare a cake.",
    "Dough placed in a baking pan to prepare a pie.",
    "A material used to make pipe bombs.",
    "Used with paint to color plastered walls or other paintable surfaces.",
    "Can be opened and held to provide protection from rain.",
    "A material used to build bag barriers or put out fires.",
    "Open the carton to take out its eggs.",
    "A package opened to obtain candy.",
    "A tool used with bleach to remove blood stains.",
    "Taken to reduce fatigue.",
    "A document in which notes can be written and kept using a writing tool.",
    "Underwear worn on the lower body.",
    "Long underwear worn on the lower body.",
    "Clothing worn on the lower body.",
    "A skirt worn on the lower body.",
    "Read or referenced to learn a skill or crafting recipe.",
    "Ammunition used to load guns that accept this ammunition type.",
    "A food that can reduce hunger but may increase thirst.",
    "A belt worn around the waist.",
    "A belt worn around the waist.",
    "Equipment worn at the waist.",
    "An adhesive used to repair compatible tools or weapons.",
    "Used with compatible radio devices to listen through headphones.",
    "A component used to modify compatible devices for remote triggering.",
    "A component used to add motion sensing to compatible devices.",
    "A controller used to remotely trigger compatible linked devices.",
    "Recorded media that can be played on a compatible device.",
    "A component used to add a timer to compatible devices such as explosives.",
    "Bellows used to raise a forge's temperature by forcing in air.",
    "A mirror used when applying makeup.",
    "Used to carry items by wearing or holding it.",
    "For smokers, it can reduce stress and unhappiness; for non-smokers, it increases food sickness."
]

SPECIAL_CONTEXT_SOURCE_SHA256 = "5fae7d734f02ca8cba57c3581926cbe0252ea7c4c6b1fb8d4431fc0bc3d4ebff"
SPECIAL_CONTEXT_EN = [
    "Junk with no specific crafting use in Build 41.",
    "Place it on a nearby water tile and check it after time has passed. It may yield bait fish, but a catch is not guaranteed and a net left out for a long time may break when checked.",
    "In the Health panel, select a fractured part that is not already splinted or stitched. The head and upper and lower torso are excluded from the splint menu.",
    "Select an injured, unbandaged body part in the Health panel, then choose it from the available items in the disinfect menu.",
    "Apply it using the bandage menu for an injured, unbandaged body part in the Health panel. An existing bandage can be removed through that panel's remove-bandage option.",
    "Used as material for metal structures and certain metal items.",
    "A portable container for carrying tools or other items.",
    "Drying requires a wet body and remaining uses in the towel. Cleaning blood stains also requires bleach.",
    "Used to build structures that require hinges, such as doors or gates.",
    "Use the beverage preparation menu on a water-filled mug or teacup to add coffee. Compatible prepared drinks can also receive ingredients allowed by that menu.",
    "Add bird bait such as worms, bread or corn. Birds have no time-of-day restriction, but location, bait freshness and player proximity restrict catches.",
    "Carry an unbroken rod and a lure, then use the fishing menu by the water. Lures include worms, crickets, grasshoppers, cockroaches, bait fish and either type of fishing tackle. Bait fish can attract pike; artificial tackle can attract trout, bass and catfish. Lure type, time and season affect the result, and a catch is not guaranteed.",
    "Carry it with an unbroken fishing rod and use the fishing menu by the water. Eligible fish include trout, bass and catfish; pike and bait fish do not take this artificial lure. A catch is not guaranteed, and the lure can break.",
    "Carry it with an unbroken fishing rod and use the fishing menu by the water. Pike are eligible catches with this bait. The bait can be consumed or lost, and a catch is not guaranteed.",
    "Add bait accepted by the target animal, such as an apple or corn. Rabbits and squirrels are eligible at night; location, bait freshness and player proximity restrict catches.",
    "Use the fertilize option on a living crop. The result depends on previous applications; excessive fertilizer rots the crop.",
    "For salad or fruit salad, carry a bowl and an apple and add the apple through the bowl's preparation menu. For cake, add it to cake batter placed in a baking pan; for sweet pie, add it to pie dough prepared with a baking pan and rolling pin. For muffins, use a tray containing muffin batter. For pancakes, waffles or oatmeal, prepare that food first and use its add-ingredient menu. Ingredient limits are six for salads, four for cake or sweet pie, three for pancakes, waffles or oatmeal, and one for muffins. Bake cake, sweet pie and muffins after adding ingredients.",
    "Used to mend clothing or reinforce it with leather patches.",
    "Used to repair certain damaged weapons or tools.",
    "Clearing ashes requires an unbroken broom. To remove blood stains, also carry bleach and use the cleaning option on a blood-stained area.",
    "Used to install or remove vehicle tires.",
    "Used to adjust the air pressure in vehicle tires.",
    "Used to recharge a battery removed from a vehicle.",
    "Applies while worn when reloading a gun that uses shotgun shells.",
    "Applies while worn when reloading a gun that uses ammunition other than shotgun shells.",
    "Used in carpentry work to build barbed-wire fences.",
    "Add mouse or rat bait such as cheese or peanut butter. There is no time-of-day restriction, but location, bait freshness and player proximity restrict catches.",
    "Used to install or remove certain vehicle parts, such as tires and brakes.",
    "A wooden cross requires two planks, two nails and a hammer. In the game's ground right-click menu, choose Carpentry, then Miscellaneous and Wooden Cross, and select a placement location. These material requirements apply to this structure; other carpentry structures do not necessarily share its materials or skill requirements.",
    "Used with paint to color plastered walls or other paintable surfaces.",
    "Carry bleach as well and use the cleaning option on a blood-stained area.",
    "Choose an amount in the treat-problem menu for a crop with flies. The spray needs remaining uses; mildew uses a separate spray.",
    "Use on a blood-stained area with a mop, an unbroken broom, a dish towel or a bath towel. Cleaning consumes bleach.",
    "Choose an amount in the treat-problem menu for a crop with mildew. The spray needs remaining uses; it is not a treatment for other crop diseases."
]

IDENTITY_ONLY_EN = {
    "수원": "A water source.",
    "물통": "A water container.",
    "잡동사니": "A miscellaneous item.",
    "조명 기구": "A light source.",
    "원예 소모품": "A gardening consumable.",
    "낚싯대": "A fishing rod.",
    "차량 정비 용품": "A vehicle-maintenance item.",
    "캠핑 용품": "Camping equipment.",
    "낚시 용품": "Fishing equipment.",
    "제작 무기": "A crafted weapon.",
    "통자물쇠": "A padlock.",
    "무전기": "A radio.",
    "기술 서적": "A skill book.",
    "음료": "A drink.",
}

# Acquisition prose is assembled from a limited product vocabulary. Longest
# phrases are replaced first, then the remaining Korean grammar is normalized.
TERMS_EN = {
    "공사 자재 보관 장소": "construction-material storage",
    "건축 자재 보관 장소": "building-material storage",
    "사냥 장비 보관 장소": "hunting-equipment storage",
    "가정 총기 보관 장소": "home firearm storage",
    "차고 총기 보관 장소": "garage firearm storage",
    "군용 무기 보관 장소": "military weapon storage",
    "경찰 무기 보관 장소": "police weapon storage",
    "경찰 총기 보관 장소": "police firearm storage",
    "총기 보관 장소": "firearm storage",
    "총기 취급 장소": "firearm areas",
    "특수 총기 진열대": "special-firearm displays",
    "무장 은신처 보관 장소": "armed safehouse storage",
    "전자 부품 보관 장소": "electronic-parts storage",
    "전기 부품 보관 장소": "electrical-parts storage",
    "전자 공구 보관 장소": "electronics-tool storage",
    "전기 공구 보관 장소": "power-tool storage",
    "전자용품 보관 장소": "electronics storage",
    "의료 물품 보관 장소": "medical-supply storage",
    "의료 보관 장소": "medical storage",
    "병원 보관 장소": "hospital storage",
    "군 의료 보관 장소": "military medical storage",
    "캠핑 장비 보관 장소": "camping-equipment storage",
    "생존 장비 보관 장소": "survival-equipment storage",
    "군용 장비 보관 장소": "military-equipment storage",
    "의류 보관 장소": "clothing storage",
    "겨울 의류 보관 장소": "winter-clothing storage",
    "스포츠 의류 장소": "sportswear areas",
    "코스튬 보관 장소": "costume storage",
    "의상 보관 장소": "outfit storage",
    "연습실 의상 보관 장소": "rehearsal-room costume storage",
    "식기 보관 장소": "tableware storage",
    "조리 도구 보관 장소": "cookware storage",
    "냉동 식품 보관 장소": "frozen-food storage",
    "침구 보관 장소": "bedding storage",
    "재봉 자재 보관 장소": "sewing-material storage",
    "재봉 도구 보관 장소": "sewing-tool storage",
    "공구 보관 장소": "tool storage",
    "공장 보관 장소": "factory storage",
    "학교 보관 장소": "school storage",
    "체육관 보관 장소": "gym storage",
    "소방 보관 장소": "fire-department storage",
    "경찰 보관 장소": "police storage",
    "군용 보관 장소": "military storage",
    "교도관 보관 장소": "corrections-officer storage",
    "농업 물품 상자": "farming-supply crates",
    "목공 공구 상자": "carpentry-tool crates",
    "공구 상자": "toolboxes",
    "스포츠 상자": "sports crates",
    "식기 상자": "tableware crates",
    "악기 상자": "instrument cases",
    "낚시 장비 상자": "fishing-equipment crates",
    "운동 장비 상자": "exercise-equipment crates",
    "당구 용품 상자": "billiards-supply crates",
    "바비큐 용품 상자": "barbecue-supply crates",
    "스피포 상품 상자": "Spiffo merchandise crates",
    "스피포 상품 진열대": "Spiffo merchandise displays",
    "스피포 상품 보관 장소": "Spiffo merchandise storage",
    "스피포 주방": "Spiffo kitchens",
    "스피포 차량": "Spiffo vehicles",
    "스피포 매장": "Spiffo restaurants",
    "총기 매장 진열대": "gun-store displays",
    "전당포 칼 진열대": "pawnshop knife displays",
    "밴드 굿즈 진열대": "band-merchandise displays",
    "지도 진열대": "map displays",
    "속옷 진열대": "underwear displays",
    "수영복 진열대": "swimwear displays",
    "조리 도구 진열대": "cookware displays",
    "무기 진열 장소": "weapon displays",
    "장신구 취급 장소": "jewelry retailers",
    "장신구 보관 장소": "jewelry storage",
    "캠핑 장비 취급 장소": "camping-supply retailers",
    "낚시 장비 취급 장소": "fishing-supply retailers",
    "원예 용품 취급 장소": "gardening-supply retailers",
    "무전 장비 취급 장소": "radio-equipment retailers",
    "야외 조리 장비 취급 장소": "outdoor-cooking retailers",
    "농사용품 판매 장소": "farming-supply stores",
    "재봉용품 판매 장소": "sewing-supply stores",
    "공구 판매 장소": "tool retailers",
    "휴가용품 판매 장소": "vacation-supply stores",
    "전자제품 매장": "electronics stores",
    "전자제품 매대": "electronics counters",
    "전자용품점": "electronics stores",
    "음향 기기 판매점": "audio-equipment stores",
    "주방용품 매장": "kitchenware stores",
    "생활용품 매장": "household-goods stores",
    "군용품점": "military-surplus stores",
    "총기 매장": "gun stores",
    "총기점": "gun stores",
    "스포츠 상점": "sporting-goods stores",
    "스포츠 매장": "sporting-goods stores",
    "원예 상점": "gardening stores",
    "공구점": "tool stores",
    "철물점": "hardware stores",
    "전당포": "pawnshops",
    "골동품점": "antique stores",
    "악기 상점": "music stores",
    "음악 상점": "music stores",
    "낚시용품점": "fishing-supply stores",
    "애완용품 판매점": "pet-supply stores",
    "장난감 판매점": "toy stores",
    "카메라 매장": "camera stores",
    "식료품점": "grocery stores",
    "제과점": "bakeries",
    "카페": "cafes",
    "약국": "pharmacies",
    "병원": "hospitals",
    "가정집": "homes",
    "주거지": "residences",
    "주거지 주방": "residential kitchens",
    "주방": "kitchens",
    "욕실": "bathrooms",
    "휴게 공간": "break areas",
    "사무 공간": "offices",
    "우편 업무 장소": "postal workplaces",
    "작업장": "workshops",
    "작업 현장": "work sites",
    "작업 장소": "work areas",
    "정비 작업장": "maintenance workshops",
    "목공 작업 장소": "carpentry areas",
    "금속 작업 장소": "metalworking areas",
    "금속 작업장": "metalworking workshops",
    "조리 작업 장소": "cooking areas",
    "청소 작업 장소": "cleaning areas",
    "세탁 작업 장소": "laundry areas",
    "도축 작업 장소": "butchering areas",
    "검시 작업 장소": "autopsy areas",
    "의료 작업 장소": "medical work areas",
    "전기공 작업 구역": "electrician work areas",
    "사진 자재 보관 장소": "photography-supply storage",
    "연료 보관 장소": "fuel storage",
    "안전 장비 보관 장소": "safety-equipment storage",
    "보안 장비 보관 장소": "security-equipment storage",
    "정비 보관 장소": "maintenance storage",
    "차량 정비 장소": "vehicle-maintenance areas",
    "차량 보관 장소": "vehicle storage",
    "차량 정비소 선반": "vehicle-shop shelves",
    "군 항공 보관 장소": "military-aviation storage",
    "은닉 보관 장소": "hidden stashes",
    "생존자 은닉처": "survivor safehouses",
    "무장 은신처": "armed safehouses",
    "실험 시설": "laboratories",
    "실험실": "laboratories",
    "약품 제조 시설": "pharmaceutical facilities",
    "의료 시설": "medical facilities",
    "경찰 시설": "police facilities",
    "숙박 시설": "lodging",
    "발전기실": "generator rooms",
    "교도소 수감자 구역": "prisoner areas",
    "학교 물품 장소": "school-supply areas",
    "사물함": "lockers",
    "학교 선반": "school shelves",
    "책상": "desks",
    "체육관": "gyms",
    "학교": "schools",
    "골프 보관함": "golf lockers",
    "골프 보관 장소": "golf storage",
    "볼링장 보관 장소": "bowling-alley storage",
    "볼링장 신발 보관 장소": "bowling-shoe storage",
    "패들 보관함": "paddle lockers",
    "라켓 보관함": "racket lockers",
    "스틱 보관함": "stick lockers",
    "연습실 보관함": "rehearsal-room storage",
    "폐기물 처리 장소": "waste-disposal areas",
    "의료 관련 장소": "medical areas",
    "시계 취급 장소": "watch retailers",
    "안경 취급 장소": "eyewear retailers",
    "잡화 보관 장소": "general-goods storage",
    "문구 보관 장소": "stationery storage",
    "사무용품 보관 장소": "office-supply storage",
    "사무용품 보관함": "office-supply cabinets",
    "학용품 보관 장소": "school-supply storage",
    "침구 취급 장소": "bedding retailers",
    "침구 보관 장소": "bedding storage",
    "세탁물 보관 장소": "laundry storage",
    "식음료 판매대": "food-and-drink counters",
    "담배 판매대": "tobacco counters",
    "문구 매대": "stationery counters",
    "의상 액세서리 매장": "fashion-accessory stores",
    "란제리 액세서리 매장": "lingerie-accessory stores",
    "란제리 매장": "lingerie stores",
    "장갑 매장": "glove stores",
    "가죽 장갑 매장": "leather-glove stores",
    "신발 매장": "shoe stores",
    "가죽 신발 매장": "leather-shoe stores",
    "운동화 매장": "sneaker stores",
    "부츠 매장": "boot stores",
    "양말 매장": "sock stores",
    "모자 매장": "hat stores",
    "셔츠 매장": "shirt stores",
    "정장 셔츠 매장": "dress-shirt stores",
    "바지 매장": "pants stores",
    "정장 바지 매장": "dress-pants stores",
    "청바지 매장": "jeans stores",
    "가죽 바지 매장": "leather-pants stores",
    "재킷 매장": "jacket stores",
    "정장 재킷 매장": "dress-jacket stores",
    "점퍼 매장": "jumper stores",
    "드레스 매장": "dress stores",
    "여름 의류 매장": "summer-clothing stores",
    "격식 의류 보관 장소": "formalwear storage",
    "수영장 보관 장소": "pool storage",
    "스트립 클럽 탈의실": "strip-club dressing rooms",
    "겨울 의류": "winter-clothing areas",
    "축제 물품 보관 장소": "festival-supply storage",
    "축제 물품": "festival-supply areas",
    "군용 전자 보관 장소": "military-electronics storage",
    "경비 보관 장소": "security-guard storage",
    "정비 차량": "maintenance vehicles",
    "작업 차량": "work vehicles",
    "생존 차량": "survival vehicles",
    "사냥 차량": "hunting vehicles",
    "경찰 차량": "police vehicles",
    "소방 차량": "fire-department vehicles",
    "구급 차량": "ambulances",
    "구급차": "ambulances",
    "의사 차량": "doctor vehicles",
    "골프 차량": "golf carts",
    "차량": "vehicles",
    "차고": "garages",
    "캠핑": "camping areas",
    "사냥 장비 장소": "hunting-equipment areas",
    "군용": "military areas",
    "군": "military areas",
    "경찰": "police areas",
    "시가지": "urban areas",
    "트레일러파크": "trailer parks",
    "초목 지대 채집": "foraging in vegetation zones",
    "채집": "foraging",
}

ACQUISITION_EXACT_EN = {
    "서점과 도서관, 학교, 주택 책장, 책 상자, 우체국과 우편 차량에서 발견된다": "Found in bookstores, libraries, schools, home bookshelves, book crates, post offices, and postal vehicles.",
    "TV 리모컨을 분해해 구한다": "Obtained by dismantling a TV remote.",
    "가죽 의류를 찢어 얻는다": "Obtained by tearing leather clothing.",
    "고기를 잘라 얻는다": "Obtained by cutting meat.",
    "권투 장비 보관 장소와 골동품점에서 발견된다": "Found in boxing-equipment storage and antique stores.",
    "권투 장비 보관 장소와 스포츠 상점에서 발견된다": "Found in boxing-equipment storage and sporting-goods stores.",
    "그릇이나 냄비에 음식 또는 재료를 담아 준비한다": "Prepared by placing food or ingredients in a bowl or pot.",
    "금속 가공으로 만든다": "Made through metalworking.",
    "금속 작업 장소와 공구점, 정비 장소에서 발견된다": "Found in metalworking areas, tool stores, and maintenance areas.",
    "나무 판재를 가공해 얻는다": "Obtained by processing lumber.",
    "나무막대와 끈, 종이클립이나 못으로 제작한다": "Crafted from a wooden stick, cord, and a paperclip or nail.",
    "나무막대와 낚싯줄, 종이클립이나 못으로 제작한다": "Crafted from a wooden stick, fishing line, and a paperclip or nail.",
    "나뭇가지를 칼날 도구로 깎아 만든다": "Made by shaping a branch with a bladed tool.",
    "나뭇가지와 깎인 돌, 천 조각으로 제작한다": "Crafted from a branch, chipped stone, and a ripped sheet.",
    "나뭇가지와 깎인 돌, 천 조각이나 끈으로 제작한다": "Crafted from a branch, chipped stone, and a ripped sheet or cord.",
    "나뭇가지와 돌, 천 조각으로 제작한다": "Crafted from a branch, stone, and a ripped sheet.",
    "냉찜질팩과 천 조각, 신문으로 제작한다": "Crafted from a cold pack, ripped sheets, and newspaper.",
    "데님 의류를 찢어 얻는다": "Obtained by tearing denim clothing.",
    "도축 작업 장소와 식기 보관 장소, 칼 제작 장소에서 발견된다": "Found in butchering areas, tableware storage, and knife-production areas.",
    "동물 사체를 손질해 얻는다": "Obtained by butchering an animal carcass.",
    "맥주를 따라 얻는다": "Obtained by pouring beer.",
    "모래를 담아 얻는다": "Obtained by filling it with sand.",
    "모루 근처에서 철괴와 망치, 집게로 제작한다": "Crafted near an anvil from an iron ingot with a hammer and tongs.",
    "모루 근처에서 철괴와 망치로 제작한다": "Crafted near an anvil from an iron ingot with a hammer.",
    "못 상자를 열어 구한다": "Obtained by opening a box of nails.",
    "물 양동이를 비워 구한다": "Obtained by emptying a bucket of water.",
    "물고기를 손질해 얻는다": "Obtained by preparing a fish.",
    "반죽이나 재료를 조리해 만든다": "Made by cooking dough or ingredients.",
    "배관 자재 장소와 차량에서 발견된다": "Found in plumbing-supply areas and vehicles.",
    "밴드 굿즈 진열대와 의류 매장에서 발견된다": "Found at band-merchandise displays and clothing stores.",
    "베이컨을 손질해 얻는다": "Obtained by preparing bacon.",
    "베이컨을 잘게 손질해 얻는다": "Obtained by cutting bacon into pieces.",
    "부러진 낚싯대를 끈과 종이클립이나 못으로 수리한다": "Made by repairing a broken fishing rod with cord and a paperclip or nail.",
    "분무기를 조합해 얻는다": "Obtained by assembling a gardening spray can.",
    "분무기에 약품을 채워 얻는다": "Obtained by filling a spray can with chemicals.",
    "붕대를 소독하거나 끓여서 만든다": "Made by disinfecting or boiling a bandage.",
    "빈 물병에 휘발유를 담아 만든다": "Made by filling an empty water bottle with gasoline.",
    "빈 술병이나 빈 맥주병을 깨뜨려 만든다": "Made by breaking an empty liquor or beer bottle.",
    "빈 연료통에 휘발유를 담아 만든다": "Made by filling an empty gas can with gasoline.",
    "빈 와인 병에 휘발유를 담아 만든다": "Made by filling an empty wine bottle with gasoline.",
    "빈 용기에 물을 담아 얻는다": "Obtained by filling an empty container with water.",
    "빈 용기에 물을 채워 얻는다": "Obtained by filling an empty container with water.",
    "빈 위스키 병에 휘발유를 담아 만든다": "Made by filling an empty whiskey bottle with gasoline.",
    "빈 음료수 병에 휘발유를 담아 만든다": "Made by filling an empty pop bottle with gasoline.",
    "빈 표백제 병에 휘발유를 담아 만든다": "Made by filling an empty bleach bottle with gasoline.",
    "빵을 잘라 얻는다": "Obtained by slicing bread.",
    "사무용품과 학용품 보관 장소, 의료 작업 장소에서 발견된다": "Found with office supplies, school-supply storage, and medical work areas.",
    "산탄총과 톱으로 절단해 만든다": "Made by cutting down a shotgun with a saw.",
    "서점 가방 진열대와 학교 물품 장소, 사물함에서 발견된다": "Found at bookstore bag displays, school-supply areas, and lockers.",
    "서점 가방 진열대와 학교 물품 장소, 학교 보관 장소에서 발견된다": "Found at bookstore bag displays, school-supply areas, and school storage.",
    "솜에 알코올을 묻혀 만든다": "Made by soaking cotton balls in alcohol.",
    "수박을 으깨 얻는다": "Obtained by crushing a watermelon.",
    "수박을 잘라 얻는다": "Obtained by slicing a watermelon.",
    "수신기와 전자 부품으로 만든다": "Made from a receiver and electronic parts.",
    "수확물을 포대에 담아 얻는다": "Obtained by placing harvested produce in a sack.",
    "술병이나 빈 병, 천 조각과 휘발유로 제작한다": "Crafted from a liquor or empty bottle, a ripped sheet, and gasoline.",
    "스포츠 매장과 야구 장비 보관 장소, 차량에서 발견된다": "Found in sporting-goods stores, baseball-equipment storage, and vehicles.",
    "스포츠 장비 장소에서 발견된다": "Found in sports-equipment areas.",
    "스포츠 장비 장소와 잡화 보관 장소, 골동품점에서 발견된다": "Found in sports-equipment areas, general-goods storage, and antique stores.",
    "스포츠 장비 장소와 코스튬 보관 장소, 골동품점에서 발견된다": "Found in sports-equipment areas, costume storage, and antique stores.",
    "스피커를 분해해 구한다": "Obtained by dismantling a speaker.",
    "스피포 상품 진열대와 의류 매장에서 발견된다": "Found at Spiffo merchandise displays and clothing stores.",
    "시계 판매점에서 발견된다": "Found in watch stores.",
    "시트나 면 의류를 찢어 만든다": "Made by tearing sheets or cotton clothing.",
    "식기 보관 장소와 생활용품 매장, 칼 제작 장소에서 발견된다": "Found in tableware storage, household-goods stores, and knife-production areas.",
    "식료품점이나 극장에서 발견된다": "Found in grocery stores or theaters.",
    "신문으로 제작한다": "Crafted from newspaper.",
    "쌀을 끓여 만든다": "Made by boiling rice.",
    "쌍열 산탄총과 톱으로 절단해 만든다": "Made by cutting down a double-barrel shotgun with a saw.",
    "씨앗 봉투를 열어 얻는다": "Obtained by opening a seed packet.",
    "씨앗을 봉투에 담아 얻는다": "Obtained by placing seeds in a packet.",
    "알루미늄으로 제작한다": "Crafted from aluminum.",
    "야구 방망이와 못, 망치로 제작한다": "Crafted from a baseball bat and nails with a hammer.",
    "야구 장비 보관 장소와 스포츠 상점, 골동품점에서 발견된다": "Found in baseball-equipment storage, sporting-goods stores, and antique stores.",
    "야구 장비 보관 장소와 스포츠 상점, 학교 보관 장소에서 발견된다": "Found in baseball-equipment storage, sporting-goods stores, and school storage.",
    "약초를 가공해 얻는다": "Obtained by processing herbs.",
    "양동이에 물을 담아 만든다": "Made by filling a bucket with water.",
    "양초에 불을 붙여 얻는다": "Obtained by lighting a candle.",
    "와인잔에 와인을 따라 만든다": "Made by pouring wine into a wine glass.",
    "욕실과 배관 자재 장소, 차고와 공구 상자에서 발견된다": "Found in bathrooms, plumbing-supply areas, garages, and toolboxes.",
    "욕실과 배관 자재 장소, 청소 작업 장소에서 발견된다": "Found in bathrooms, plumbing-supply areas, and cleaning areas.",
    "유리컵에 음료를 따라 만든다": "Made by pouring a drink into a glass.",
    "자갈을 담아 얻는다": "Obtained by filling it with gravel.",
    "재료를 그릇에 담아 만든다": "Made by placing ingredients in a bowl.",
    "재료를 병조림해 만든다": "Made by canning ingredients in a jar.",
    "재료를 섞어 얻는다": "Obtained by mixing ingredients.",
    "재료를 섞어 준비한다": "Prepared by mixing ingredients.",
    "재료를 조리해 만든다": "Made by cooking ingredients.",
    "재료를 조합해 만든다": "Made by combining ingredients.",
    "재봉 관련 장소나 의료 시설에서 발견된다": "Found in sewing-related areas or medical facilities.",
    "재봉 용품점이나 재봉 자재 보관 장소에서 발견된다": "Found in sewing-supply stores or sewing-material storage.",
    "전당포 칼 진열대와 무기 진열 장소, 취미품 진열대에서 발견된다": "Found at pawnshop knife displays, weapon displays, and hobby displays.",
    "전자 부품과 금속 파이프, 화약과 끈으로 제작한다": "Crafted from electronic parts, a metal pipe, gunpowder, and cord.",
    "전자 부품과 증폭기를 조합해 만든다": "Made by combining electronic parts and an amplifier.",
    "전자 부품을 가공해 얻는다": "Obtained by processing electronic parts.",
    "전자 스크랩과 무선 부품, 전선과 알루미늄으로 제작한다": "Crafted from electronic scrap, radio parts, wire, and aluminum.",
    "전자기기를 분해해 구한다": "Obtained by dismantling electronic devices.",
    "제과 작업 장소와 식기 보관 장소, 칼 제작 장소에서 발견된다": "Found in baking areas, tableware storage, and knife-production areas.",
    "제작으로 얻는다": "Obtained through crafting.",
    "제작한 창과 가위, 덕트 테이프로 제작한다": "Crafted from a crafted spear, scissors, and duct tape.",
    "제작한 창과 드라이버, 덕트 테이프로 제작한다": "Crafted from a crafted spear, screwdriver, and duct tape.",
    "제작한 창과 마체테, 덕트 테이프로 제작한다": "Crafted from a crafted spear, machete, and duct tape.",
    "제작한 창과 메스, 덕트 테이프로 제작한다": "Crafted from a crafted spear, scalpel, and duct tape.",
    "제작한 창과 버터칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, butter knife, and duct tape.",
    "제작한 창과 사냥칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, hunting knife, and duct tape.",
    "제작한 창과 손갈퀴, 덕트 테이프로 제작한다": "Crafted from a crafted spear, hand fork, and duct tape.",
    "제작한 창과 숟가락, 덕트 테이프로 제작한다": "Crafted from a crafted spear, spoon, and duct tape.",
    "제작한 창과 식빵칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, bread knife, and duct tape.",
    "제작한 창과 식칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, kitchen knife, and duct tape.",
    "제작한 창과 얼음송곳, 덕트 테이프로 제작한다": "Crafted from a crafted spear, ice pick, and duct tape.",
    "제작한 창과 편지칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, letter opener, and duct tape.",
    "제작한 창과 포크, 덕트 테이프로 제작한다": "Crafted from a crafted spear, fork, and duct tape.",
    "지도 진열대와 지도 상자, 차량 정비소 선반과 차량에서 발견된다": "Found at map displays, in map crates, on vehicle-shop shelves, and in vehicles.",
    "천 조각과 막대 재료로 제작한다": "Crafted from ripped sheets and stick material.",
    "천이나 의류를 찢어 얻는다": "Obtained by tearing fabric or clothing.",
    "컵에 물과 재료를 담아 끓여 만든다": "Made by boiling water and ingredients in a cup.",
    "컵에 음료를 담아 만든다": "Made by pouring a drink into a cup.",
    "타이머나 알람시계를 개조해 만든다": "Made by modifying a timer or alarm clock.",
    "탄약 상자를 열거나 모루 근처에서 주조해 얻는다": "Obtained by opening an ammunition box or casting near an anvil.",
    "탄약 상자를 열어 얻는다": "Obtained by opening an ammunition box.",
    "탄약을 분해해 구한다": "Obtained by dismantling ammunition.",
    "탄약을 상자에 담아 얻는다": "Obtained by placing ammunition in a box.",
    "통나무를 묶어 만든다": "Made by tying logs together.",
    "통나무를 톱으로 가공해 얻는다": "Obtained by sawing a log.",
    "퇴비를 담아 얻는다": "Obtained by filling it with compost.",
    "파스타를 끓여 만든다": "Made by boiling pasta.",
    "판자나 나뭇가지와 칼날 도구로 제작한다": "Crafted from a plank or branch with a bladed tool.",
    "판자를 톱질해 만든다": "Made by sawing planks.",
    "판자와 못, 망치로 제작한다": "Crafted from planks and nails with a hammer.",
    "폭발물을 개조해 얻는다": "Obtained by modifying an explosive.",
    "플라스틱 컵에 음료를 따라 만든다": "Made by pouring a drink into a plastic cup.",
    "헝겊을 소독하거나 끓여서 만든다": "Made by disinfecting or boiling a rag.",
    "헤어스프레이와 불꽃놀이 재료를 조합해 만든다": "Made by combining hairspray and fireworks material.",
    "호박을 가공해 만든다": "Made by processing a pumpkin.",
    "휘발유와 천 조각과 빈 병을 조합해 만든다": "Made by combining gasoline, a ripped sheet, and an empty bottle.",
    "흙을 담아 얻는다": "Obtained by filling it with soil.",
}


def _source_values(rows: list[dict[str, object]], field: str) -> list[str]:
    return sorted({str(row[field]) for row in rows if row.get(field)})


def _sha(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def primary_use_translations(rows: list[dict[str, object]]) -> dict[str, str]:
    values = _source_values(rows, "primary_use")
    if _sha(values) != PRIMARY_USE_SOURCE_SHA256 or len(values) != len(PRIMARY_USE_EN):
        raise RuntimeError("LAYER3_EN_PRIMARY_USE_SOURCE_MISMATCH")
    return dict(zip(values, PRIMARY_USE_EN, strict=True))


def special_context_translations(rows: list[dict[str, object]]) -> dict[str, str]:
    values = _source_values(rows, "special_context")
    if _sha(values) != SPECIAL_CONTEXT_SOURCE_SHA256 or len(values) != len(SPECIAL_CONTEXT_EN):
        raise RuntimeError("LAYER3_EN_SPECIAL_CONTEXT_SOURCE_MISMATCH")
    return dict(zip(values, SPECIAL_CONTEXT_EN, strict=True))


def _translate_terms(value: str) -> str:
    translated = value
    for korean, english in sorted(TERMS_EN.items(), key=lambda pair: len(pair[0]), reverse=True):
        translated = translated.replace(korean, english)
    translated = translated.replace("이나 ", " or ").replace("나 ", " or ")
    translated = translated.replace(" 또는 ", " or ")
    translated = translated.replace("과 ", ", ").replace("와 ", ", ")
    return translated


def translate_acquisition_hint(value: str) -> str | None:
    exact = ACQUISITION_EXACT_EN.get(value)
    if exact is not None:
        return exact
    for suffix, prefix in (
        ("에서 발견된다", "Found in "),
        ("에서 구할 수 있다", "Can be obtained from "),
        ("으로 구할 수 있다", "Can be obtained from "),
        ("로 구할 수 있다", "Can be obtained from "),
    ):
        if value.endswith(suffix):
            result = prefix + _translate_terms(value[: -len(suffix)]) + "."
            return result if re.search("[가-힣]", result) is None else None
    return None


def _lua_string(value: str) -> str:
    parts = ['"']
    for byte in value.encode("utf-8"):
        if byte == 34:
            parts.append('\\"')
        elif byte == 92:
            parts.append('\\\\')
        elif byte == 10:
            parts.append("\\n")
        elif byte == 13:
            parts.append("\\r")
        elif byte == 9:
            parts.append("\\t")
        elif 32 <= byte <= 126:
            parts.append(chr(byte))
        else:
            parts.append(f"\\{byte:03d}")
    parts.append('"')
    return "".join(parts)


def _write_runtime(entries: dict[str, str], output_root: Path, chunk_size: int = 200) -> None:
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)
    ordered = sorted(entries.items())
    chunks: list[dict[str, object]] = []
    for offset in range(0, len(ordered), chunk_size):
        rows = ordered[offset : offset + chunk_size]
        ordinal = len(chunks) + 1
        name = f"Chunk{ordinal:03d}"
        lines = ["-- Generated Layer 3 English localization payload.", "return {"]
        lines.extend(f"    [{_lua_string(full_type)}] = {_lua_string(text)}," for full_type, text in rows)
        lines.extend(["}", ""])
        (output_root / f"{name}.lua").write_text("\n".join(lines), encoding="utf-8", newline="\n")
        chunks.append({"first": rows[0][0], "last": rows[-1][0], "module": f"Iris/Data/Layer3English/{name}"})
    lines = ["-- Generated Layer 3 English localization range index.", "return {", "    chunks = {"]
    lines.extend(
        "        { first = %s, last = %s, module = %s },"
        % (_lua_string(str(row["first"])), _lua_string(str(row["last"])), _lua_string(str(row["module"])))
        for row in chunks
    )
    lines.extend(["    },", "}", ""])
    (output_root / "Index.lua").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _current_projection(repository_root: Path) -> tuple[dict[str, dict[str, object]], str]:
    pointer_path = repository_path(repository_root, CURRENT_POINTER_RELATIVE_PATH)
    pointer_text = pointer_path.read_text(encoding="utf-8")
    generation_matches = re.findall(
        r'^\s*generation_id\s*=\s*"(dvf33-[0-9a-f]{64})",?\s*$',
        pointer_text,
        re.MULTILINE,
    )
    if len(generation_matches) != 1:
        raise RuntimeError("LAYER3_EN_CURRENT_GENERATION_POINTER_INVALID")

    current_generation_id = generation_matches[0]
    descriptor_path = repository_path(
        repository_root,
        f"{CURRENT_GENERATION_ROOT_RELATIVE_PATH}/{current_generation_id}/generation_descriptor.json",
    )
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    if descriptor.get("generation_id") != current_generation_id:
        raise RuntimeError("LAYER3_EN_CURRENT_GENERATION_DESCRIPTOR_MISMATCH")
    required_input_paths = {CANONICAL_INPUTS[0], CANONICAL_INPUTS[6]}
    descriptor_inputs = {
        row.get("path"): row
        for row in descriptor.get("canonical_inputs", [])
        if row.get("path") in required_input_paths
    }
    current_inputs = {
        row["path"]: row
        for row in canonical_input_identity(repository_root)
        if row["path"] in required_input_paths
    }
    if descriptor_inputs != current_inputs:
        raise RuntimeError("LAYER3_EN_CURRENT_GENERATION_INPUT_MISMATCH")

    projection_path = repository_path(repository_root, CANONICAL_INPUTS[6])
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    entries = projection.get("entries")
    if not isinstance(entries, dict):
        raise RuntimeError("LAYER3_EN_CURRENT_PROJECTION_INVALID")
    return entries, current_generation_id


def approved_general_descriptions(
    repository_root: Path,
    facts_by_item: dict[str, dict[str, object]],
    rendered: dict[str, dict[str, object]],
    composed: dict | None = None,
) -> dict[str, dict[str, str]]:
    """Read bilingual edits from the already generation-bound approved input.

    The source fields retain their historical provenance. User adoption of
    these existing details is not an independent game-source verification.
    """
    projection = json.loads(repository_path(repository_root, CANONICAL_INPUTS[6]).read_text(encoding="utf-8"))
    adoption = projection.get("meta", {}).get("general_description_integration")
    if adoption is None:
        return {}
    if (not isinstance(adoption, dict)
            or adoption.get("decision") not in {
                "user_adopted_primary_use_with_context_detail_refinement",
                "user_adopted_build41_description_correction",
            }
            or adoption.get("source_slot") != "special_context"
            or not adoption.get("authority_ref")):
        raise RuntimeError("LAYER3_GENERAL_DESCRIPTION_ADOPTION_INVALID")
    facts_path = repository_path(repository_root, CANONICAL_INPUTS[0])
    if adoption.get("facts_sha256") != hashlib.sha256(facts_path.read_bytes()).hexdigest():
        raise RuntimeError("LAYER3_GENERAL_DESCRIPTION_INPUT_STALE")
    entries = adoption.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise RuntimeError("LAYER3_GENERAL_DESCRIPTION_ENTRIES_INVALID")
    result = {}
    for key, entry in entries.items():
        if composed is not None and key in composed:
            # Successor binding already validates all core and detail source slots.
            continue
        facts = facts_by_item.get(key, {})
        current = rendered.get(key, {})
        if not isinstance(entry, dict):
            raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_ENTRY_INVALID:{key}")
        for field, hash_field in (("primary_use", "primary_use_source_sha256"), ("special_context", "context_source_sha256")):
            value = facts.get(field)
            if not isinstance(value, str) or not value or hashlib.sha256(value.encode("utf-8")).hexdigest() != entry.get(hash_field):
                raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_SOURCE_MISMATCH:{key}:{field}")
        context_identity = {
            "item_id": key, "source_slot": "special_context",
            "fact_origin": entry.get("original_origin"),
            "source_value_hash": entry["context_source_sha256"],
        }
        context_id = "l3rf-" + hashlib.sha256(json.dumps(
            context_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")).hexdigest()
        if entry.get("original_origin") != "origin_missing" or entry.get("context_fact_id") != context_id:
            raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_CONTEXT_ID_MISMATCH:{key}")
        if current.get("role_material", {}).get("core_source_fact_ids") != [entry.get("primary_use_fact_id")]:
            raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_CORE_MISMATCH:{key}")
        localized = entry.get("localized_general_description")
        if (not isinstance(localized, dict) or set(localized) != {"ko", "en"}
                or any(not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value for value in localized.values())
                or (current.get("text_ko") or "").split("\n\n", 1)[0] != localized["ko"]):
            raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_LOCALE_MISMATCH:{key}")
        result[key] = localized
    return result


def build_english_entries(
    repository_root: Path,
) -> tuple[dict[str, str], str, dict[str, int]]:
    facts_path = repository_root / "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
    rows = [json.loads(line) for line in facts_path.read_text(encoding="utf-8").splitlines() if line]
    translations = primary_use_translations(rows)
    special = special_context_translations(rows)
    acquisition_values = _source_values(rows, "acquisition_hint")
    localized_acquisition = {
        value: translated
        for value in acquisition_values
        if (translated := translate_acquisition_hint(value)) is not None
    }
    unresolved = [value for value in acquisition_values if value not in localized_acquisition]
    if unresolved:
        raise RuntimeError(f"LAYER3_EN_ACQUISITION_UNRESOLVED:{len(unresolved)}")

    facts_by_item = {str(row["item_id"]): row for row in rows}
    rendered, generation_id = _current_projection(repository_root)
    from .compose_layer3_shared import approved_compositions
    composed = approved_compositions(repository_root, rendered)
    general_descriptions = approved_general_descriptions(repository_root, facts_by_item, rendered, composed)
    english_entries: dict[str, str] = {}
    for item_id, rendered_entry in rendered.items():
        if not isinstance(rendered_entry, dict):
            raise RuntimeError(f"LAYER3_EN_CURRENT_PROJECTION_ENTRY_INVALID:{item_id}")
        if not rendered_entry.get("text_ko"):
            continue
        if item_id in composed:
            english_entries[item_id] = composed[item_id]["menu"]["en"]
            continue
        facts = facts_by_item.get(item_id)
        if facts is None:
            raise RuntimeError(f"LAYER3_EN_CURRENT_PUBLIC_FACT_MISSING:{item_id}")
        primary_use = facts.get("primary_use")
        body = ""
        general_description = general_descriptions.get(item_id)
        if general_description:
            body = general_description["en"]
        elif primary_use:
            body = translations[str(primary_use)]
        else:
            body = IDENTITY_ONLY_EN[str(facts["identity_hint"])]
        if not general_description and facts.get("special_context"):
            body += " " + special[str(facts["special_context"])]
        if facts.get("acquisition_hint"):
            body += "\n\n" + localized_acquisition[str(facts["acquisition_hint"])]
        english_entries[item_id] = body
    return english_entries, generation_id, {
        "primary_use": len(translations),
        "special_context": len(special),
        "acquisition": len(localized_acquisition),
    }


def build_tooltip_t1_owner_entries(
    repository_root: Path,
) -> tuple[dict[str, dict[str, object]], str]:
    """Publish existing single-core DVF facts for the Tooltip T1 contract.

    The output is a projection of already-owned fact identities and localized
    primary-use surfaces.  It does not split rendered bodies, synthesize facts,
    or turn acquisition material into a core description.
    """

    facts_path = repository_root / "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
    rows = [json.loads(line) for line in facts_path.read_text(encoding="utf-8").splitlines() if line]
    translations = primary_use_translations(rows)
    facts_by_item = {str(row["item_id"]): row for row in rows}
    rendered, generation_id = _current_projection(repository_root)
    from .compose_layer3_shared import approved_compositions
    composed = approved_compositions(repository_root, rendered)
    entries: dict[str, dict[str, object]] = {}
    for item_id, rendered_entry in sorted(rendered.items()):
        if not isinstance(rendered_entry, dict):
            raise RuntimeError(f"TOOLTIP_T1_DVF_RENDERED_ENTRY_INVALID:{item_id}")
        role_material = rendered_entry.get("role_material")
        if not isinstance(role_material, dict):
            continue
        core_ids = role_material.get("core_source_fact_ids")
        if not isinstance(core_ids, list) or not all(isinstance(value, str) and value for value in core_ids):
            raise RuntimeError(f"TOOLTIP_T1_DVF_CORE_IDENTITY_INVALID:{item_id}")
        if not core_ids:
            continue
        if len(core_ids) != 1:
            raise RuntimeError(f"TOOLTIP_T1_DVF_MULTIPLE_CORE_FACTS_FORBIDDEN:{item_id}")
        facts = facts_by_item.get(item_id)
        if not isinstance(facts, dict) or not facts.get("primary_use"):
            raise RuntimeError(f"TOOLTIP_T1_DVF_CORE_SOURCE_MISSING:{item_id}")
        fact_id = core_ids[0]
        primary_use = str(facts["primary_use"])
        entries[item_id] = {
            "fact_id": fact_id,
            "fact_kind": "core_description",
            "source_fact_ids": [fact_id],
            "source_ref": f"Iris/build/description/v2/data/dvf_3_3_facts.jsonl#item_id={item_id};field=primary_use",
            "authority_ref": (
                f"{CURRENT_GENERATION_ROOT_RELATIVE_PATH}/{generation_id}/"
                f"dvf_3_3_rendered.json#entries/{item_id}/role_material/core_source_fact_ids"
            ),
            "upstream_readiness": "owner_approved",
            "tooltip_eligibility": "eligible",
            "localized_surfaces": composed[item_id]["core"] if item_id in composed else {
                "ko": primary_use,
                "en": translations[primary_use],
            },
        }
    return entries, generation_id


def _write_tooltip_t1_owner_output(
    repository_root: Path,
    entries: dict[str, dict[str, object]],
    generation_id: str,
) -> Path:
    registry_path = repository_root / TOOLTIP_T1_D3_REGISTRY_RELATIVE_PATH
    absence_entries: dict[str, dict[str, object]] = {}
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if registry.get("schema_version") != "iris-tooltip-t1-d3-disposition-registry-v1":
            raise RuntimeError("TOOLTIP_T1_D3_REGISTRY_SCHEMA_INVALID")
        registry_entries = registry.get("entries")
        if not isinstance(registry_entries, dict):
            raise RuntimeError("TOOLTIP_T1_D3_REGISTRY_ENTRIES_INVALID")
        if registry.get("target_count") != len(registry_entries) or registry.get("terminal_distribution") != {"A": 0, "B": len(registry_entries), "blocked": 0}:
            raise RuntimeError("TOOLTIP_T1_D3_REGISTRY_DISTRIBUTION_INVALID")
        for full_type, row in sorted(registry_entries.items()):
            if not isinstance(row, dict) or row.get("exact_full_type") != full_type:
                raise RuntimeError(f"TOOLTIP_T1_D3_REGISTRY_IDENTITY_INVALID:{full_type}")
            if row.get("intended_disposition") != "approved_legitimate_absence":
                continue
            absence_entries[full_type] = {
                "exact_full_type": full_type,
                "disposition": "approved_legitimate_absence",
                "absence_reason_code": row["absence_reason_code"],
                "owner": row["owner"],
                "acceptance_evidence": row["acceptance_evidence"],
                "applicable_scope": row["applicable_scope"],
                "reaudit_condition": row["reaudit_condition"],
                "authority_decision_ref": row["authority_decision_ref"],
            }
    from iris_tooling.domains.tooltip_t1.contract import canonical_bytes, sha256_bytes

    output_path = repository_root / TOOLTIP_T1_OWNER_OUTPUT_RELATIVE_PATH
    payload = {
        "schema_version": "iris-tooltip-t1-layer3-owner-input-v2",
        "producer": "iris_tooling.build.build_layer3_english_localization",
        "generation_id": generation_id,
        "absence_entries": absence_entries,
        "manifest": {
            "fact_entry_count": len(entries),
            "absence_entry_count": len(absence_entries),
            "total_owner_row_count": len(entries) + len(absence_entries),
            "fact_entries_sha256": sha256_bytes(canonical_bytes(entries)),
            "absence_entries_sha256": sha256_bytes(canonical_bytes(absence_entries)),
        },
        "entries": entries,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return output_path


def publish_tooltip_t1_owner_only(repository_root: Path) -> dict[str, object]:
    """Regenerate only the metadata owner projection, never locale runtime bytes."""

    tooltip_entries, generation_id = build_tooltip_t1_owner_entries(repository_root)
    output = _write_tooltip_t1_owner_output(repository_root, tooltip_entries, generation_id)
    payload = json.loads(output.read_text(encoding="utf-8"))
    return {
        "status": "BUILT",
        "generation_id": generation_id,
        "fact_entries": len(payload["entries"]),
        "absence_entries": len(payload["absence_entries"]),
        "tooltip_t1_owner_output": str(output),
        "runtime_locale_write_set": [],
    }


def main() -> int:
    repository_root = require_repository_context().repository_root
    english_entries, generation_id, metrics = build_english_entries(repository_root)
    tooltip_entries, tooltip_generation_id = build_tooltip_t1_owner_entries(repository_root)
    if tooltip_generation_id != generation_id:
        raise RuntimeError("TOOLTIP_T1_DVF_GENERATION_MISMATCH")

    output_root = repository_root / "Iris/media/lua/client/Iris/Data/Layer3English"
    _write_runtime(english_entries, output_root)
    tooltip_output = _write_tooltip_t1_owner_output(
        repository_root,
        tooltip_entries,
        generation_id,
    )
    print(json.dumps({
        "status": "BUILT",
        **metrics,
        "runtime_entries": len(english_entries),
        "tooltip_t1_owner_entries": len(tooltip_entries),
        "tooltip_t1_owner_output": str(tooltip_output),
        "generation_id": generation_id,
        "output_root": str(output_root),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
