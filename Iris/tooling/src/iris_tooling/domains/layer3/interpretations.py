"""Source interpretations used by the offline investigator, not a validator.

These are bounded semantic readings. A source inventory or literal hit is not
one of these readings. Unknown dispatches retain an explicit unfinished state.
"""
from __future__ import annotations

from . import source_reader as reader


RECIPE_FINDINGS = {
    'eligibility': 'ISCraftAction.isValid calls IsRecipeValid and rejects driving. Recipe clauses retain inputs, alternatives, keep/destroy, skill, learned-recipe and callback predicates; availability is not inferred from a recipe name or category.',
    'creation': 'PerformMakeItem crosses into RecipeManager. Lua then preserves food temperature/freezing and copies selected result fields for multiple outputs; its explicit comment says extra outputs do not each invoke OnCreate. Result membership is a transformation observation, not the output item\'s use.',
    'callbacks': 'Bound recipecode callbacks implement food portioning/age and container returns; battery charge transfer; fabric recovery; log binding recovery; spear condition transfer; electronic salvage and radio construction. Random yields, runtime input selection and RecipeManager dispatch remain conditions, not constant item effects.',
    'conflicts': 'Recipe.OnTest.FullLiquor is declared twice with different predicates (Liquor completeness and Petrol usedDelta); no winner is selected. Historical callback aliases are retained separately from definitions. No keep-to-tool or input-to-ingredient rule is applied globally.',
    'scope': 'The raw record and its consumer are examined even when no broad semantic proposition is admitted. A generic recipe label is not sufficient to assign an activity. Unsupported callback bodies remain not_investigated, rather than being hidden behind RecipeManager.',
}

# Explicit manual reading coverage, independent of function discovery. A newly
# declared callback does not enter this set just because its body was found.
CALLBACK_READINGS = {
    'food': {
        'callbacks': ['Recipe.OnCreate.' + name for name in (
            'AddBaseIngredientToCookingVessel', 'BeanBowl', 'CannedFood', 'CutAnimal', 'CutFish',
            'GetBiscuit', 'GetCookies', 'GetMuffin', 'MakeBowlOfSoup2', 'MakeBowlOfSoup4',
            'MakeBowlOfStew2', 'MakeBowlOfStew4', 'MakeOatmeal', 'OpenCandyPackage', 'OpenCannedFood',
            'OpenEggCarton', 'OpenSackProduce', 'PutCakeBatterInBakingPan', 'SliceBread', 'SliceBreadDough',
            'SliceHam', 'SlicePie', 'SlicePizza', 'SliceSalami', 'SliceWatermelon')],
        'finding': 'Reviewed recipecode food callbacks: portion/age/nutrient/condition transfer, cooked/burnt propagation and returned vessels; MakeOatmeal sets heat/cooked. These are transformation outcomes, not guaranteed nutritional effects of every participating item.'},
    'predicates': {
        'callbacks': ['Recipe.OnTest.' + name for name in ('CutFish', 'DismantleElectronics', 'FullLiquor',
            'FullPetrolBottle', 'IsNotWorn', 'IsWorn', 'NotTaintedWater', 'RefillBlowTorch', 'SliceBreadDough',
            'TorchBatteryInsert', 'TorchBatteryRemoval', 'WholeBreadSlices', 'WholeEgg', 'WholeMilk')]
          + ['Recipe.OnCanPerform.' + name for name in ('GetBiscuit', 'GetMuffin', 'SliceCooked', 'SlicePizza', 'Uncooked')],
        'finding': 'Reviewed freshness/fullness, cooked/burnt, weight, taint, favorite and worn-state predicates, plus torch/propane remaining-charge tests. Both conflicting FullLiquor bodies are retained; no load winner is inferred.'},
    'devices': {
        'callbacks': ['Recipe.OnCreate.' + name for name in ('Dismantle', 'DismantleFlashlight', 'DismantleRadio',
            'DismantleRadioHAM', 'DismantleRadioTV', 'DismantleRadioTwoWay', 'DismantleTVRemote', 'RadioCraft',
            'RefillBlowTorch', 'TorchBatteryInsert', 'TorchBatteryRemoval')],
        'finding': 'Reviewed charge transfer and bounded torch refilling; flashlights return residual-charge batteries; electrical/radio salvage and constructed device properties use skill/random/current device state. Alias calls remain dispatch dependencies.'},
    'materials': {
        'callbacks': ['Recipe.OnCreate.' + name for name in ('CreateLogStack', 'SplitLogStack', 'RipClothing',
            'CreateSpear', 'UpgradeSpear', 'DismantleSpear', 'SpikedBat', 'OpenBoxOfJars', 'OpenUmbrella', 'CloseUmbrella')]
          + ['BSItem_OnCreate', 'LightCandle_OnCreate', 'ExtinguishCandle_OnCreate'],
        'finding': 'Reviewed binding-material recovery, fabric/dirty/thread recovery, spear/bat condition transfer, jar lids, umbrella hand/condition transfer, smithing quality and candle activation/deactivation forms. keep is not globally a tool and result relation is not intrinsic function.'},
    'experience': {
        'callbacks': ['Recipe.OnGiveXP.' + name for name in ('Blacksmith10', 'Blacksmith15', 'Blacksmith20', 'Blacksmith25',
            'Cooking10', 'Cooking3', 'DismantleElectronics', 'DismantleRadio', 'MetalWelding10', 'MetalWelding25',
            'None', 'RadioCraft', 'SawLogs', 'WoodWork5')],
        'finding': 'Reviewed explicit AddXP callbacks, no-XP empty body, skill-dependent SawLogs and RadioCraft. Callback invocation/eligibility remains required; no universal item XP fact.'},
    'shotgun': {
        'callbacks': ['ShotgunSawnoff_OnCreate', 'DblBarrelhotgunSawnoff_OnCreate'],
        'finding': 'Reviewed ISShotgunWeapon callbacks: matching source gun transfers ammunition/chamber/modData and attempts compatible part attachment to the sawn-off result. Firing performance is not implemented by this callback.'},
}

# These class dispositions refer to the specific caller -> action edges in the
# inventory menu. They do not claim every method in a UI class was audited.
ACTION_READINGS = {
    'ISReadABook': 'Literature literacy/awake/skill/page checks -> read progress -> SkillBook XP multiplier only when progress exceeds current multiplier in the trained level range. Non-skill ReadLiterature remains engine-bound; writable notes are a separate branch.',
    'ISFixAction': 'Fixing Require/Fixer and menu required items -> inventory-valid repair -> FixingManager.fixItem, with vehicle-part condition synchronization when relevant. Success probability and repaired amount are engine-owned.',
    'ISGarmentUI': 'Inspection context joins Thread, Needle/SewingNeedle and RippedSheets/DenimStrips/LeatherStrips; a patch permits removal, an unpatched part permits adding. It delegates to the separately investigated repair/remove actions. Displayed defense numbers are not semantic evidence.',
    'ISMap': 'IsMap branch transfers the item and binds it to UIWorldMap API, displays its map and invokes doBuildingStash. Map presentation is supported; stash discovery/acquisition and cartographic accuracy remain outside non-acquisition conclusions.',
    'ISMakeUpUI': 'MakeUpType and mirror/vehicle/foundation prerequisites open makeup selection; selection creates/wears a configured cosmetic item, apply adds it and removes the previous makeup. Cosmetic registry and visual state determine appearance; no medical/protection inference.',
    'ISPlace3DItemCursor': 'Generic placement checks visibility, intervening walls/windows and usable surface; it walks, unequips and queues dropping with offsets/rotation. Excluded from intrinsic item function; no installation/device behavior is inferred.',
    'ISAddItemInRecipe': 'Inventory/base/ingredient eligibility is checked with getItemsCanBeUse; addItem crosses the EvolvedRecipe engine boundary, followed by food-temperature averaging in Lua.',
    'ISApplyBandage': 'Damaged-body-part menu -> inventory/patient validity -> SetBandaged and removal. Dirty material sets bandage life to zero; infection, hemophobia and Doctor XP are conditional. No universal healing claim.',
    'ISClothingExtraAction': 'ClothingItemExtra alternative creates a replacement, copies visuals and container contents and wears it. Extra-option registry and live receiver determine the variant; no generic protection effect.',
    'ISConsolidateDrainable': 'Compatible drainables transfer the minimum of available contents and destination space. Both must stay in inventory; destination can inherit taint. Drainable type alone does not establish fuel or nutrition.',
    'ISCraftAction': RECIPE_FINDINGS['creation'],
    'ISDrinkFromBottle': 'isWaterSource -> thirst > 0.1 -> queued drink. Positive-thirst portions reduce thirst with inventory checks; taint adds poison only below poison 20 and sickness 0.3. Constructor coercion of uses < 1 prevents a zero-use inference.',
    'ISDryMyself': 'Exact towel branch checks wetness and uses. update decreases body wetness and consumes uses, with inventory/body-wetness validity; not clothing drying.',
    'ISDumpContentsAction': 'Recursive ReplaceOnUse/ReplaceOnDeplete chain selects a water-storing final form, then uses/replaces the original. Missing/duplicate definitions and cycles prevent selecting a final form.',
    'ISDumpWaterAction': 'Water menu -> inventory validity -> usedDelta decreases, then becomes zero and Use runs. Replacement identity and engine depletion behavior remain conditional.',
    'ISDyeHair': 'HairDye getter selects the item; hair must exist and not be Bald, or beard must be nonempty. Inventory-valid action writes the corresponding visual color, consumes dye and synchronizes visuals.',
    'ISEatFoodAction': 'Inventory, companion-item and satiety checks precede character:Eat. Nutrition and OnEat dispatch cross into the engine; source fields are not unconditional numerical effects.',
    'ISEjectMagazine': 'Primary gun with clip -> unloadFinished animation -> create magazine with old ammo count, then clear gun clip and ammo state. Event delivery and current receiver state are required.',
    'ISInsertMagazine': 'Primary gun, absent clip and magazine in inventory -> loadFinished removes magazine and sets gun clip/ammo; it may queue racking. Ammo compatibility and animation dispatch remain prerequisites.',
    'ISLoadBulletsInMagazine': 'Inventory magazine and matching ammo -> InsertBullet event removes ammunition and increases count up to capacity. XP is random and is not an unconditional effect of ammunition.',
    'ISUnloadBulletsFromMagazine': 'Inventory magazine -> RemoveBullet event creates matching ammunition and decreases count until zero. Event execution is not implied by the script MaxAmmo field.',
    'ISUnloadBulletsFromFirearm': 'Unload animation events create ammunition and decrease count, one/all according to gun behavior. Empty/current chamber state and event delivery are runtime dependencies.',
    'ISReloadWeaponAction': 'Primary gun and available ammo -> loadFinished -> consume matching bullets and increase gun count to capacity; may queue racking. Recursion for insert-all is bounded by ammo/capacity in the source. Attack/damage semantics are not supplied here.',
    'ISRackFirearm': 'canRack checks jam/chamber/ammo/spent state. Animation events clear jams/spent states, eject eligible live rounds and chamber from stored ammo. No assertion of damage or universal firing eligibility.',
    'ISRemovePatch': 'Tailoring-dependent material recovery and XP precede removal of the selected clothing patch. Recovery is not guaranteed and protection arithmetic is engine-owned.',
    'ISRepairClothing': 'Inventory clothing/fabric/needle/thread and unpatched body part -> addPatch, remove fabric, use thread and random Tailoring XP. Patch effectiveness remains an engine dependency.',
    'ISRemoveWeaponUpgrade': 'Selected weapon part is detached and returned to inventory. Compatibility is resolved by the menu/engine; no weapon-performance effect is inferred from the part name.',
    'ISUpgradeWeapon': 'Selected compatible part is attached to weapon and removed from inventory. This proves attachment behavior only; effect magnitude remains with the weapon engine.',
    'ISRipClothing': 'The inventory doClothingRecipeMenu returns unconditionally before the old handler. This edge is inactive; current fabric recovery is investigated through recipecode instead.',
    'ISStopAlarmClockAction': 'Digital-alarm menu checks ringing; action stops and syncs it. The dialog stores enabled/hour/minute settings. Ring scheduling is engine-owned.',
    'ISTakePillAction': 'Pills name-prefix menu -> transfer -> inventory-valid action -> BodyDamage.JustTookPill. Taking pills is supported; specific drug effects are not implemented in the bound Lua consumer.',
    'ISTransferWaterAction': 'Water source and compatible destination space -> converted water-storage form if needed -> interpolate amounts and propagate taint; empty source invokes Use. Not arbitrary liquid mixing.',
    'ISPlaceTrap': 'CanBePlaced hand weapon -> valid inventory -> construct IsoTrap on square, add/sync world object and remove inventory/hand item. Detonation and sensor engine behavior are not proven by placement.',
    'ISPlaceCarBatteryChargerAction': 'Exact charger branch -> inventory-valid action -> carBatteryCharger/place command with coordinates and item. This establishes placement request; actual device charge behavior needs server/engine implementation.',
    'ISWearClothing': 'BodyLocation clothing -> inventory-valid wear action -> set worn item, refresh model. Protection, insulation and wetness effects are not derived from field names.',
    'ISInventoryTransferAction': 'Distinct accessible source/destination, room, admission and allowed removal are checked; perform removes and adds the item. Multiplayer permissions and transactions constrain storage.',
    'ISEquipWeaponAction': 'Generic inventory/hand manipulation, with damage/equipment prerequisites in the menu. This is not a distinguishing intrinsic item function or a proof of weapon use.',
    'ISEquipHeavyItem': 'Generic heavy-item handling queues unequip of occupied hands after walking to its container. Placement/electrical/corpse behavior is not inferred from equip success.',
    'ISUnequipAction': 'Generic equipment removal; lit candle has a separate extinguishing transformation before unequip. No item-specific benefit is inferred.',
    'ISItemEditorUI': 'Caller is explicitly debug or authorized-client item editing. Excluded as administrative mutation, not ordinary item use; no claim about editor internals.',
    'ISTextBox': 'Caller gathers rename text; mutation is in the bound menu callback. Generic dialog construction is not an item function.',
    'ISToolTip': 'Caller displays menu explanation/requirements; presentation does not admit semantic facts.',
    'ISToolTipInv': 'Caller displays item details; presentation does not admit semantic facts.',
    'ISBombTimerDialog': 'Caller accepts seconds; onSetBombTimerClick writes a positive explosion timer. Scheduling/explosion behavior remains the trap engine boundary.',
    'ISAlarmClockDialog': 'OK writes alarm enabled/hour/minute and synchronizes; it does not implement ringing or world sound propagation.',
    'ISUIWriteJournal': 'Dialog edits pages/title subject to editable/lock state; bound menu callback persists them. No XP/recipe learning implication.',
}

MENU_READINGS = {
    'activation': 'canBeActivated plus hand/attached state and remaining-use check -> setActivated(not isActivated). This establishes a toggle, not what the device does while active.',
    'remote': 'RemoteController/CanBeRemote and ID mismatch permit linking; link assigns controller ID, reset assigns -1. Trigger sends object/triggerRemote with ID/range; IsoTrap/server dispatch is outside this Lua body. Range/availability and blast effects are not inferred.',
    'fire_mode': 'Multiple fire-mode possibilities permit setting the selected mode. Reload classes have separate animation-event analysis; mode selection does not prove firing damage.',
    'selection': 'testItem is the selected inventory item in the loop; isHandWeapon is reset for multiselection. Other receiver variables may be inventory candidates, world objects, output items or player state and are not aliases for every target.',
    'extension': 'OnPreFillInventoryObjectContextMenu, OnFillInventoryObjectContextMenu and hotbar dispatch are explicit residual dependencies. A bound menu cannot enumerate an unknown runtime callback registry or mod/load ordering; literal absence is not closure.',
    'emptying': 'The recursive replacement predicate is traversed for each target with exact module identity and cycle/ambiguity stops; transfer/pour then crosses engine Use/replacement behavior. This is independent of whether the target participated in a recipe.',
}


def recipe_analysis(record, participants, callback_defs, callback_refs):
    props = reader.properties(record, ':')
    callbacks = {key: vals for key, vals in props.items() if key.startswith('On')}
    names = {name for values in callbacks.values() for name in values}
    reviewed = {name: key for key, row in CALLBACK_READINGS.items() for name in row['callbacks']}
    missing = sorted(names - (callback_defs & reviewed.keys()))
    return {'raw_participants': participants, 'declared_callbacks': callbacks,
            'callback_observation_refs': sorted({ref for name in names for ref in callback_refs.get(name, [])}),
            'consumer_interpretation': RECIPE_FINDINGS,
            'reviewed_callback_groups': sorted({reviewed[name] for name in names if name in reviewed and name in callback_defs}),
            'defined_but_unreviewed_callbacks': sorted((names & callback_defs) - reviewed.keys()),
            'state': 'not_investigated' if missing else 'investigated_unresolved',
            'unfinished_callbacks': missing,
            'residual': 'RecipeManager selection/consumption, runtime ingredients and callback receiver state; no whole-scope closure.'}


def replacement_chain(item, fields):
    """Investigate the menu's recursive emptying predicate without executing Lua."""
    visited, steps = set(), []
    current = item
    while current not in visited:
        visited.add(current)
        f = fields.get(current)
        if f is None: return {'steps': steps, 'boundary': 'missing_or_ambiguous_declaration', 'at': current}
        if steps and f.get('CanStoreWater', '').lower() == 'true':
            return {'steps': steps, 'boundary': 'water_storage_form', 'at': current}
        token = f.get('ReplaceOnUse') or (f.get('ReplaceOnDeplete') if f.get('Type') == 'Drainable' else None)
        if not token: return {'steps': steps, 'boundary': 'no_next_declared_replacement', 'at': current}
        nxt = reader.qualify(current.split('.', 1)[0], token)
        steps.append({'from': current, 'to': nxt})
        current = nxt
    return {'steps': steps, 'boundary': 'cycle', 'at': current}
