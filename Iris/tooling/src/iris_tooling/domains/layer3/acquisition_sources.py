"""Bounded acquisition source survey; never executes game Lua or promotes prose.

The six families are an L3-04 execution inventory, not a game-wide taxonomy.
Literal/declaration observations and engine-dependent leads are not facts.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

from . import investigation as inv
from . import source_reader as reader
from .semantic_model import identity

FAMILIES = ('loot', 'vehicle', 'foraging', 'fishing_trapping', 'dynamic', 'transformation')
PROC = 'lua/server/Items/ProceduralDistributions.lua'
DIST = 'lua/server/Items/Distributions.lua'
VEHICLE = 'lua/server/Vehicles/VehicleDistributions.lua'
FORAGE = 'lua/shared/Foraging/forageDefinitions.lua'
SYSTEM = 'lua/shared/Foraging/forageSystem.lua'
FISH = 'lua/shared/Fishing/fishing_properties.lua'
TRAP = 'lua/server/Traps/TrapDefinition.lua'
CREATE = re.compile(r'''\b(?:CreateItem|AddItems?|AddWorldInventoryItem|PerformMakeItem|newStash|addContainer)\s*\(|getInventory\(\):addItems?\s*\(|sendObjectChange\(\s*['"](?:addItem|addItemOfType)['"]''')
LIMITS = {
    'loot': 'ItemPicker.lua aliases ItemPickerJava. Room/container/procList and raw weights are observable; namespace lookup, loader precedence and spawning are engine boundaries. No token-only fact or probability.',
    'vehicle': 'Vehicle distribution tables, aliases and vehicle/container selection are observable; engine selection, namespace lookup and loader precedence remain open. Vehicle labels are raw tokens, not asserted vehicle/place names.',
    'foraging': 'populateItemDefs/importDef -> generateLootTable -> isForageable -> ISBaseIcon.getItemList -> ISForageAction/addOrDropItems. Runtime registry extensions, world population and custom callbacks outside reviewed definitions remain open.',
    'fishing_trapping': 'Fishing property registration -> ISFishingAction selection/CreateItem/AddItem; Animals -> STrapGlobalObject.checkForAnimal/removeAnimal -> server addItem. World eligibility/random draws and runtime additions remain conditional.',
    'dynamic': 'StashUtil registers descriptions for the engine. Static creation callers and their enclosing Lua functions are surveyed; indirect dispatch, constructed identifiers and engine implementations cannot be closed. Debug/admin/test callers are not ordinary acquisition evidence.',
    'transformation': 'Script result/replacement clauses and Lua creation consumers/callbacks surveyed. ISCraftAction delegates PerformMakeItem to RecipeManager; module resolution, callback output and engine-only transformations are not inferred from result text.',
}


def safe_files(root: Path, directory: str, suffix: str):
    """Check links before traversal/reading; never follow a source outside root."""
    base = inv.local_path(root, directory)
    if not base.exists():
        return []
    found = []
    for path in base.rglob('*'):
        inv.require(path.resolve().is_relative_to(root.resolve()), 'external source link')
        if path.is_file() and path.suffix == suffix:
            found.append(path.relative_to(root).as_posix())
    return sorted(found)


def table_region(text: str, start: int) -> tuple[str, int]:
    """Balanced literal table region. Strings/comments never change nesting."""
    hidden = reader.mask(text, lua=True, strings=True)
    inv.require(hidden[start] == '{', 'expected Lua table')
    depth = 0
    for end in range(start, len(hidden)):
        depth += (hidden[end] == '{') - (hidden[end] == '}')
        if not depth:
            return text[start:end + 1], end + 1
    raise ValueError('unclosed Lua table')


def fields(raw: str) -> dict:
    """Preserve raw values, including nested conditions; reject duplicate keys."""
    clean = reader.mask(raw, lua=True)
    result = {}
    for clause in lua_clauses(clean[1:-1]):
        match = re.fullmatch(r'(\w+|\["[^"\\]+"\])\s*=\s*(.*)', clause, re.S)
        if not match or match[1].strip('[]"') in result:
            raise ValueError('unsupported/duplicate Lua table field')
        result[match[1].strip('[]"')] = match[2].strip()
    return result


def lua_clauses(body: str) -> list[str]:
    hidden = reader.mask(body, lua=True, strings=True)
    depth, begin, parts = 0, 0, []
    for i, char in enumerate(hidden):
        if char in '{[(':
            depth += 1
        elif char in '}])':
            depth -= 1
        elif char in ',;' and depth == 0:
            if body[begin:i].strip():
                parts.append(body[begin:i].strip())
            begin = i + 1
    inv.require(depth == 0, 'unbalanced Lua field expression')
    if body[begin:].strip():
        parts.append(body[begin:].strip())
    return parts


def generated_forage_rows(text: str) -> list[dict]:
    """Expand only the ten reviewed literal map/template loops, without Lua eval."""
    clean = reader.mask(text, lua=True)
    rows = []
    for match in re.finditer(r'forageDefs\[itemName\]\s*=\s*\{', clean):
        loop = list(re.finditer(r'for itemName, itemFullName in pairs\((\w+(?:\.items)?)\) do', clean[:match.start()]))[-1]
        table_name = loop[1]
        grouped = table_name == 'spawnTable.items'
        if grouped:
            outer = list(re.finditer(r'for (?:_|rarity), spawnTable in pairs\((\w+)\) do', clean[:loop.start()]))[-1]
            table_name = outer[1]
        definitions = list(re.finditer(r'local\s+' + re.escape(table_name) + r'\s*=\s*\{', clean[:loop.start()]))
        inv.require(bool(definitions), 'unbound foraging generation table')
        table_raw, _ = table_region(clean, definitions[-1].end() - 1)
        groups = list(fields(table_raw).items()) if grouped else [('direct', table_raw)]
        template, _ = table_region(clean, match.end() - 1)
        for group, raw in groups:
            values = fields(raw) if grouped else {}
            mapping = fields(values['items'] if grouped else raw)
            for name, item in mapping.items():
                inv.require(literal(item) is not None, 'nonliteral foraging type mapping')
                expanded = re.sub(r'\bspawnTable\.(\w+)\b', lambda m: values[m[1]], template)
                expanded = re.sub(r'\bitemFullName\b', item, expanded)
                rows.append({'name': name, 'line': clean.count('\n', 0, match.start()) + 1,
                             'raw': {'template': template, 'group': group, 'bindings': {**{k: v for k, v in values.items() if k != 'items'},
                                                                                       'itemName': name, 'itemFullName': item}},
                             'fields': fields(expanded)})
    return rows


def function_regions(text: str) -> list[dict]:
    """Match Lua block tokens to keep nested branches inside their true function."""
    hidden = reader.mask(text, lua=True, strings=True)
    stack, regions = [], []
    for token in re.finditer(r'\b(function|if|for|while|do|repeat|until|end)\b', hidden):
        word = token[1]
        if word in {'function', 'if', 'for', 'while', 'repeat'}:
            stack.append({'kind': word, 'start': token.start(), 'await_do': word in {'for', 'while'}})
        elif word == 'do':
            if stack and stack[-1]['await_do']:
                stack[-1]['await_do'] = False
            else:
                stack.append({'kind': word, 'start': token.start(), 'await_do': False})
        elif stack:
            block = stack.pop()
            if block['kind'] == 'function':
                begin = block['start']
                signature = re.match(r'function\s*(?:([\w.:]+)\s*)?\(([^)]*)\)', text[begin:])
                if not signature:
                    continue
                name = signature[1]
                if not name:
                    line = text[text.rfind('\n', 0, begin) + 1:begin]
                    assigned = re.search(r'([\w.:]+)\s*=\s*$', line)
                    name = assigned[1] if assigned else 'anonymous'
                regions.append({'name': name, 'parameters': signature[2], 'start': begin,
                                'body_start': begin + signature.end(), 'end': token.end()})
    return sorted(regions, key=lambda r: (r['start'], r['end']))


# Source interpretation notes recorded during this execution. These are bounded
# investigation rules, not accepted-fact rules. Each trace also carries the
# actual function, output expressions, assignments, guards and source callers.
# No unknown path receives a reviewed label just from a family name.
CALLER_READINGS = {
    'forageDefinitions': 'Literal default/template maps populate forageDefs; ten generator loops bind itemFullName and group values. Spawn callbacks preserve the initial item, mutate state, or conditionally add mapped crop seeds. No weight is a probability.',
    'forageSystem': 'Registration/import defaults and month/zone/perk/trait/recipe/tag predicates feed icon selection. addOrDropItems preserves existing objects and chooses inventory versus ground by capacity. CreateItem elsewhere measures item hunger/size, not a separate spawn.',
    'ISBaseIcon': 'Icon preview creates an item object; getItemList independently creates min/max-count exact definition types and applies spawnFuncs. Collection passes this list through ISForageAction; previews alone are not acquisition.',
    'ISForageIcon': 'Search-focus reroll chooses eligible category/zone/month definition and updates the icon preview. Base icon list and the pickup action own actual delivery.',
    'ISSearchManager': 'CreateItem supplies icon preview/fallback Plank and replaces preview types during icon sync. No direct inventory delivery; follow ISBaseIcon/ISForageAction.',
    'ISFishingAction': 'Registered fishes/trashItems and lure selection -> successful getFish -> createFish/CreateItem -> selected inventory. Rod/lure validity, zone stock, time/weather attraction and line break constrain the route; invalid lure recursion is not executed.',
    'FishingNet': 'remove returns a net; check uses elapsed hours, possible break and random trials to return BaitFish or BrokenFishingNet. Trap square and hours are runtime arguments.',
    'STrapGlobalObject': 'Animals/traps/bait/zone/hour and fresh bait constrain capture. removeAnimal creates the exact animal.item and delivers to character/server; destruction drops configured destroyItem. State and object existence remain conditional.',
    'trappingCommands': 'Client command resolves exact trap at coordinates; remove returns trapType and removeAnimal delegates to the already inspected server object. No arbitrary identity inferred from trap name.',
    'ISRemoveBaitAction': 'Negative baitAmountMulti and existing trap bait return that runtime bait type with adjusted hunger/age; this returns pre-existing bait identity rather than a universal bait source.',
    'recipecode': 'Recipe callbacks receive engine-selected items/result/player. Bound script OnCreate links select functions; source bodies explicitly mutate result, return containers, recover batteries, unpack contents or add salvage under item/skill/random branches. Symbolic output/type and eligibility remain RecipeManager/argument dependencies when not closed.',
    'ISCraftAction': 'IsRecipeValid and driving guard -> PerformMakeItem; created result is added according to result count/floor rules. RecipeManager resolves module, input use and callback dispatch; result declarations alone do not prove exact output.',
    'ISAddItemInRecipe': 'CreateItem of extraItems/spices reads food metadata for naming; evolved recipe mutation is a separate engine operation, not those temporary objects becoming acquired items.',
    'ISCleanBandage': 'Valid cleaning removes dirty item, adds recipe.result type and consumes water; new() binds result from recipe. Unqualified recipe result lookup remains engine-dependent.',
    'ISApplyBandage': 'Removing a bandage recreates stored bodyPart bandage type; depleted bandage life invokes Use, potentially changing it. Applying consumes supplied material. Type/state is patient-dependent.',
    'ISSplint': 'Removal returns stored splint item and RippedSheets when the stored type is not Base.Splint; patient body-part state is required.',
    'ISRemovePatch': 'Successful tailoring roll maps current patch fabric through ClothingRecipesDefinitions to material, then adds it; engine fabric index and clothing state constrain output.',
    'ISRipClothing': 'Sheet rope or material count/type derives from supplied clothing materials; dirt/blood controls dirty variant/fallback. Tailoring/random rolls condition extra Thread. Unqualified material tokens are not automatically Base.',
    'ISClothingExtraAction': 'extra selected by caller is passed to CreateItem, visual/content/state copied, old clothing removed and new item added/worn. Variant identity depends on source extra option and script lookup.',
    'ISPadlockAction': 'Locking creates the padlock number of matching KeyPadlock keys; unlocking returns Padlock keyed to existing lock. Ownership/key state is a prerequisite.',
    'ISGetCompost': 'Compost-per-use and carried item validity; fills an existing bag or replaces other supplied item with Base.CompostBag and sets uses. No claim of a full bag without compost amount.',
    'ISTakeGenerator': 'Valid object removal adds Base.Generator, copying condition and equipping heavy item. World generator presence and action validity are necessary.',
    'ISTakeFuel': 'Empty container becomes getReplaceType(PetrolSource), falling back to Base.PetrolCan; existing cans refill. Fuel source and amount/transfer branches constrain state.',
    'ISTakeWaterAction': 'Adds caller-created replacement only when oldItem exists, then fills from available water and updates hands. Replacement type is supplied by world/inventory menu and engine item definition.',
    'ISTakeTrap': 'Returns the existing trap.getItem and removes world trap. Runtime trap identity is required; no item-global independent source is inferred.',
    'ISEjectMagazine': 'Ejection creates gun.getMagazineType, copies ammo state and adds it only with inserted magazine. Runtime gun/script defines exact type.',
    'ISRackFirearm': 'Removing a live round creates gun.getAmmoType and adds it; chamber/spent-round state decides whether this occurs.',
    'ISUnloadBulletsFromFirearm': 'Unload loop creates gun ammo type while ammo count positive and decrements gun count; clip/chamber paths remain weapon state dependent.',
    'ISUnloadBulletsFromMagazine': 'Animation unload event creates magazine ammo type only while current ammo count positive, then decrements it.',
    'ISReloadableMagazine': 'Legacy racking with positive capacity constructs Base plus ammoType, then syncs reduced capacity. Legacy dispatch/type data is not assumed current or aliased.',
    'ISShotgunWeapon': 'Legacy chambered round uses moduleName plus ammoType and drops only if created; unattached part returns to player. Attachability and legacy load route remain dependencies.',
    'ISSemiAutoWeapon': 'Legacy clip ejection and chamber rack create types from module/clip data, preserve capacity and add/drop them. Legacy dispatch and lookup remain open.',
    'stormysReload': 'Key-L test loadout behind hasWeapons; explicit starter/test injection, not general loot. Legacy registration and debug applicability are not assumed.',
    'ISInventoryTransferAction': 'Transfers the same existing object between validated source/destination containers; capacity/floor handling may move to ground. No new independent acquisition identity.',
    'ISGrabItemAction': 'Existing selected world object is removed from square and transferred; runtime world-item identity and action validity are required.',
    'ISGrabCorpseAction': 'Adds the supplied corpse object and equips it after world removal. This is a runtime object transfer, not evidence for an arbitrary corpse type spawning.',
    'ISDropItemAction': 'Drops an existing inventory object; source inventory ownership, coordinate and container state constrain relocation.',
    'ISDropWorldItemAction': 'Lit candle can revert to Base.Candle with copied uses; selected item moves to supplied square. This is a conditional transformation/relocation, not world spawn evidence.',
    'ISEquipWeaponAction': 'forceDropHeavyItems relocates existing primary/secondary heavy objects onto current square; no newly declared FullType.',
    'ISEquipHeavyItem': 'Moves existing heavy world object into player inventory and equips; visibility/ownership/action conditions apply.',
    'ISUnequipAction': 'Force-drop-heavy case removes existing item and places it on current square; ordinary unequip does not generate a new type.',
    'ISDestroyStuffAction': 'Destruction preserves container contents on ground and may return Sheet for curtain branches. Object sprite/state, validity and multisegment destruction control output.',
    'ISDismantleAction': 'Container contents are relocated; need: modData keys define returned types/count. Torch special case and current fuel are preserved. ModData and random recovery are runtime dependencies.',
    'ISScavengeAction': 'Legacy scavenge selection passes type/count to addOrDropItems; created preview selects bag, actual items are added or dropped by capacity. Legacy registry and action route remain explicit dependencies.',
    'ClientCommands': 'Server command dispatch resolves coordinates/objects. Removal of cuttable bush emits TreeBranch/Twigs under random branches; fuel/barricade/BBQ commands create or return typed parts. Object state, request arguments and command reachability are retained, not replaced by universal loot claims.',
    'SCampfireSystemCommands': 'Remove command returns camping.CampfireKit after resolving existing campfire; server/player delivery path and object state constrain it.',
    'SCampfireSystem': 'addContainer is an internal object-container operation, not item generation. Timed events and command dispatch delegate to the campfire object.',
    'SCampfireGlobalObject': 'Container creation attaches ItemContainer; transferItemsToGround relocates existing campfire contents when removed. No new FullType inferred from container creation.',
    'camping_tent': 'Tent removal returns kit through command path; destruction iterates need: material metadata and random loss before dropping surviving materials.',
    'MOGenerator': 'Map object conversion makes a Generator inventory item to instantiate IsoGenerator and transfers fuel/condition; world conversion itself is not inventory acquisition.',
    'MOLampOnPillar': 'Map lamp conversion creates Battery as light fuel with used delta and attaches it to world object; player acquisition would require a separate removal path.',
    'ISBuildUtil': 'Consumed nail boxes become nails for building material handling; amount depends on consumed box list. Ground/container removal and later building use constrain net acquisition.',
    'ISBuildingObject': 'onDestroy relocates container items and recovers need: materials under random destruction; exact types are modData-driven and are not inferred from object labels.',
    'ISBrushToolTileCursor': 'Tile placement uses a temporary Plank as moveable placement input; it is not a generated pickup or loot item.',
    'ISBuildMenu': 'ItemInstances factory creates cached metadata previews for build options; the preview is not added to player inventory.',
    'ISMultiStageBuild': 'Creates a Plank for override hand model during construction animation; stage result remains engine world-object mutation.',
    'ISShovelGround': 'Replaces empty bag with caller-selected newBag or fills supplied bag; digging may add Worm. Ground material, bag type and action state constrain result.',
    'ISPlowAction': 'After valid farming plow work, random branch adds Base.Worm. Soil/action validity and world state are prerequisites.',
    'ISRemoveDrum': 'Valid removal deletes the existing metal drum world object and adds Base.MetalDrum; no proof of world availability.',
    'ISFarmingMenu': 'CreateItem of GardeningSprayMilk is used for missing-item display name only, not item delivery.',
    'ISTakeEngineParts': 'Active code sends vehicle/takeEngineParts with mechanics skill minus script repair level. The local AddItems block is commented out. VehicleCommands owns actual server selection; no client generation inferred from the comment.',
    'VehicleCommands': 'OnClientCommand dispatches vehicle commands to Commands. takeEngineParts resolves vehicle and Engine, derives positive numParts from condition and randomized skill divisor, then sends exact Base.EngineParts via addItemOfType. Server message reception is engine code absent from this snapshot; no inventory receipt or local commented client generation inferred. Other commands mutate vehicle state or return runtime parts.',
    'SMetalDrumSystem': 'OnClientCommand resolves a drum by coordinates. removeLogs requests Base.Log; removeCharcoal requests Base.Charcoal only with haveCharcoal and clears that flag. Delivery is an addItemOfType engine object-change message; its receiver is unavailable here, so only the exact conditional send is confirmed.',
    'SFarmingSystem': 'harvest resolves farming_vegetableconf by seed type, derives numberOfVeg, sends props.vegetableName and conditional hasSeed props.seedName to the player, clears harvest flags and advances/removes crop. Plant/command state, computed yield and engine addItemOfType receiver remain explicit dependencies; raw type mapping alone is not inventory delivery.',
    'ISTakeGasolineFromVehicle': 'Empty fuel container is replaced by PetrolSource type or Base.PetrolCan, retaining hand slots; vehicle fuel/transfer state controls fill.',
    'ISRemoveBurntVehicle': 'Scrap roll lists pass unqualified material tokens to checkAddItem, which applies skill/random branch and world drop. Namespace lookup is not inferred.',
    'Vehicles': 'Part creation selects script itemType, saved chosen variants and part state before factory; uninstall returns existing part, failure may also return it. Tire/container loss drops existing objects. Vehicle definition/engine arguments remain binding dependencies.',
    'ISVehicleMenu': 'Door-key removal returns existing vehicle key and clears door/key state; inventory seat transfers are separate actions.',
    'ISVehicleMechanics': 'Factory calls obtain part/tool names for menus/tooltips. They are display objects, not acquired items; mechanics action code owns actual return.',
    'ISInventoryPage': 'Floor container population adds existing world inventory objects to a UI-facing floor container, not a new spawn.',
    'ISFitnessUI': 'Factory obtains required exercise item display name; missing item stays missing.',
    'ISTradingUI': 'Offer-list/network AddItem messages are trade proposal state, not independent spawning. Accepted network transfer is outside the static offer list.',
    'ISMakeUpUI': 'Selection creates a visual makeup preview; apply adds selected makeup and removes previous worn makeup. Visual registry/selection and application are necessary.',
    'ISWorldObjectContextMenu': 'Factories mix tool previews and WaterSource/PetrolSource replacements passed to timed actions. Door-key and combination-lock removals create matching keys/locks under existing door/code state.',
    'ISInventoryPaneContextMenu': 'Factories mostly create requirement/result previews; extinguishing returns Candle, fluid transfer creates target WaterSource replacement. Specific action dispatch/engine result lookup is retained.',
    'ISCraftingUI': 'ItemInstances factory caches previews. Debug source-item injection calls RecipeUtils then adds items; ordinary craft uses separate RecipeManager action.',
    'ISHealthPanel': 'onCheatItem is explicit health-panel cheat injection; no general gameplay acquisition is inferred.',
    'ISMoveableSpriteProps': 'Moveable pickup/disassembly resolves sprite/scrap definitions, random breakage and tools; adds/drops instantiated or existing items. Generator placement creates engine input; recipe-based scrap delegates to RecipeManager. Sprite metadata/runtime mapping prevents a global FullType claim.',
    'SpawnItems': 'Events.OnNewGame.Add(SpawnItems.OnNewGame) equips Belt2 and conditional StarterKit/difficulty items; server SpawnItems list injects configured strings. OnGameStart belt migration has gotNewBelt guard but registration names SpawnItems.onNewGame with different casing: this migration dispatch is unconfirmed. No arbitrary server configuration asserted.',
    'MainCreationMethods': 'Survivor creation equips a Base.BaseballBat in NPC inventory; player access and NPC/runtime creation remain separate unknowns.',
    'StashUtil': 'newStash/addContainer register exact stash/item/coordinate/container fields in StashDescriptions; engine StashSystem consumes these definitions, not a Lua inventory delivery.',
    'CharacterCreationMain': 'CreateItem provides selected outfit/clothing preview during character creation; spawn/equip transfer is a separate lifecycle step.',
    'CharacterCreationHeader': 'Factory supplies clothing preview item while building character appearance; not independent loot or inventory delivery.',
    'ISItemsListTable': 'Explicit admin item-list spawn requests deliver selected script FullName; privileged/debug injection is not general acquisition.',
    'ISPlayerStatsManageInvUI': 'Factory reconstructs remote inventory display entries; add-item controls are privileged management, not ordinary spawning evidence.',
    'TutorialHelperFunctions': 'fillContainer helper injects supplied tutorial item table into a selected container; requires tutorial caller and is not normal distribution evidence.',
    'ISFinalizeDealAction': 'Finalized trade adds the supplied existing itemsToReceive objects and removes itemsToGive; constructor binds both lists and other player. Network agreement/ownership is required, not independent item spawning.',
    'ISRemoveWeaponUpgrade': 'Valid action requires a nonbroken Screwdriver-tagged item, owned weapon and matching attached part. perform detaches that existing part and returns it to inventory; part FullType is supplied by the existing weapon, not inferred from an item-name hit.',
    'StashDebug': 'SPAWN button creates selected stash map, calls StashSystem.doStashItem and gives it to player; explicit debug injection, not general loot.',
    'AdminContextMenu': 'Privileged menu creates Key1 with supplied door key ID; this requires admin action rather than ordinary loot.',
    'DebugContextMenu': 'Debug actions inject keys or convert mannequin settings into a Moveables.Moveable inventory object; debug menu dispatch is required.',
    'ISAttachedItemsUI': 'Debug add control takes item type text, creates object and attaches it to selected character; no ordinary acquisition claim.',
    'WorldMapEditor': 'Base.Map is an editor model input owned by the map editor, not an inventory gift.',
    'WorldMapEditorMode_Stashes': 'Editor builds StashUtil source text/containers for a selected stash; code-generation strings are not executed acquisition paths.',
    'WorldMapEditorListBox': 'onAddItem is a UI list editing method, not InventoryItem creation or delivery.',
    'RecipeUtils': 'Test/debug helper builds sourceFullType recipe inputs, including water/uses; ordinary recipe validity never creates these supplied test sources.',
    'RecipeTests': 'Explicit test setup creates ingredient containers and calls recipes for tests; not a normal item acquisition surface.',
    'TimedActionsTests': 'Test setup instantiates player inventory/world objects under controlled test coordinates; no ordinary acquisition claim.',
    'Tutorial1': 'Tutorial character/world initialization supplies a prescribed outfit and container items. Tutorial scenario lifecycle is a required condition.',
    'Steps': 'Tutorial step enter/finish/reset functions supply demonstration food, pans, knives, shotgun and bag. Step sequencing is required and is not normal distribution spawning.',
    'LastStandSetup': 'getCore.isChallenge/current challenge ID selects AddPlayer loadout; saved challenge inventory restoration uses explicit item types. Requires that challenge lifecycle.',
    'Challenge1': 'Challenge1 registration/AddPlayer supplies a challenge loadout; not a normal sandbox loot source.',
    'EightMonthsLater': 'OnChallengeQuery registration and AddPlayer challenge initialization supply items; requires selected challenge and client player.',
    'Insomnia': 'Challenge startup/container setup supplies scenario-specific equipment. Challenge registration and world state are required.',
    'Studio': 'Studio challenge initialization supplies its own loadout and scene. Not a general acquisition path.',
    'ISChallenge2WeaponUpWindow': 'Challenge upgrade button item/item2 and cost govern inventory additions; requires Challenge2 shop context and button eligibility.',
    'ISChallenge2VariousItemWindow': 'Challenge upgrade purchase adds configured item after deducting challenge money; not an ordinary vendor/source claim.',
}


def caller_reading(path: str, text: str) -> tuple[str | None, str | None]:
    name = Path(path).stem
    if name in CALLER_READINGS:
        return name, CALLER_READINGS[name]
    # This shared rule is admitted by the actual registry construct in each
    # source, not by the directory name or item labels alone.
    if path.startswith('lua/client/DebugUIs/Scenarios/') and re.search(r'\bdebugScenarios(?:\.|\[)', text):
        return 'debug_scenario', 'Registered debugScenarios initializer supplies explicit inventory/world objects when that scenario is launched; scene configuration and start callback are required. These are not ordinary acquisition facts.'
    if path.startswith('lua/shared/StashDescriptions/') and 'StashUtil.newStash' in text:
        return 'stash_description', 'newStash arguments, spawnTable, daysToSpawn, building coordinates and addContainer fields register a conditional stash description. Follow StashUtil registration into engine StashSystem; exact spawn/lookup remains engine-dependent.'
    return None, None


def named_tables(text: str, name: str) -> list[dict]:
    clean = reader.mask(text, lua=True)
    match = re.search(r'(?m)^' + re.escape(name) + r'\s*=\s*\{', clean)
    if not match:
        return []
    raw, end = table_region(clean, match.end() - 1)
    rows = []
    offset = match.end()
    for clause in lua_clauses(raw[1:-1]):
        local = clean.find(clause, offset, end)
        inv.require(local >= 0, 'lost table locator')
        offset = local + len(clause)
        entry = re.fullmatch(r'(\w+|\["\w+"\])\s*=\s*(\{.*\})', clause, re.S)
        if entry:
            rows.append({'name': entry[1].strip('[]"'), 'line': clean.count('\n', 0, local) + 1,
                         'raw': entry[2], 'fields': fields(entry[2])})
    return rows


def literal(value: str):
    match = re.fullmatch(r'"([^"\\]*)"', value.strip())
    return match[1] if match else None


def table_nodes(text: str) -> list[dict]:
    """Structural table/alias observations, preserving duplicate declarations.

    This reader follows declaration references only. It cannot interpret an
    executable expression, pick a loader winner, or assign an item namespace.
    """
    clean = reader.mask(text, lua=True)
    hidden = reader.mask(clean, lua=True, strings=True)
    nodes = []

    def descend(raw, address, begin):
        values = []
        offset = begin + 1
        for ordinal, clause in enumerate(lua_clauses(raw[1:-1])):
            pos = clean.find(clause, offset)
            inv.require(pos >= 0, 'table field locator lost')
            offset = pos + len(clause)
            match = re.fullmatch(r'(\w+|\[\s*"[^"\\]+"\s*\])\s*=\s*(.*)', clause, re.S)
            key, value = (match[1].strip('[] \t"'), match[2]) if match else (str(ordinal), clause)
            values.append({'key': key, 'value': value, 'line': clean.count('\n', 0, pos) + 1})
            if value.startswith('{') and value.endswith('}'):
                nested = clean.find('{', pos)
                descend(value, address + [key], nested)
        nodes.append({'address': address, 'line': clean.count('\n', 0, begin) + 1, 'values': values})

    consumed = -1
    for m in re.finditer(r'(?m)^(?:local\s+)?([\w.]+)\s*=\s*\{', clean):
        if m.start() < consumed:
            continue
        begin = m.end() - 1
        raw, consumed = table_region(clean, begin)
        descend(raw, [m[1]], begin)
    for m in re.finditer(r'(?m)^([\w.]+)\s*=\s*([\w.]+)\s*;?\s*$', hidden):
        nodes.append({'address': [m[1]], 'line': hidden.count('\n', 0, m.start()) + 1, 'alias': m[2], 'values': []})
    return nodes


def interpretation_traces(texts: dict, declarations: dict) -> dict:
    """Perform the available distribution/selection/result connection tracing.

    A trace has an explicit assessed boundary. Collection alone never receives
    that status; unimplemented dynamic caller interpretation stays unreviewed.
    """
    traces = {}
    lua_clean = {p: reader.mask(t, lua=True) for p, t in texts.items() if p.endswith('.lua')}
    callbacks_by_name = defaultdict(list)
    for p, body in lua_clean.items():
        rule, reading = caller_reading(p, body)
        for region in function_regions(body):
            callbacks_by_name[region['name']].append({'source_path': p, 'locator': f"L{body.count(chr(10), 0, region['start']) + 1}",
                                                     'callback': region['name'], 'raw': body[region['start']:region['end']],
                                                     'assessment': 'assessed' if reading else 'unreviewed', 'review_rule': rule, 'reading': reading})
    tables = {p: table_nodes(texts[p]) for p in (PROC, DIST, VEHICLE)}
    proc_uses = defaultdict(list)
    for node in tables[DIST]:
        for value in node['values']:
            if value['key'] == 'name' and literal(value['value']):
                proc_uses[literal(value['value'])].append({'source_path': DIST, 'locator': f"L{node['line']}",
                                                          'address': node['address'], 'conditions': node['values']})
    vehicle_uses = defaultdict(list)
    for node in tables[VEHICLE]:
        for value in node['values']:
            for name in re.findall(r'\bVehicleDistributions\.(\w+)', value['value']):
                vehicle_uses[name].append({'source_path': VEHICLE, 'locator': f"L{value['line']}",
                                            'address': node['address'] + [value['key']], 'expression': value['value']})
        if node.get('alias'):
            vehicle_uses[node['alias']].append({'source_path': VEHICLE, 'locator': f"L{node['line']}",
                                               'address': node['address'], 'expression': node['alias']})
    for family, path in (('loot', PROC), ('loot', DIST), ('vehicle', VEHICLE)):
        for node in tables[path]:
            if node['address'][-1] != 'items':
                continue
            tokens = [literal(v['value']) for v in node['values'] if literal(v['value'])]
            parent = next((n for n in tables[path] if n['address'] == node['address'][:-1]), {})
            if path == PROC:
                consumers = proc_uses.get(node['address'][1], [])
            elif path == VEHICLE:
                name = node['address'][0].split('.')[-1]
                consumers, queue, seen = [], [name, 'VehicleDistributions.' + name], set()
                while queue:
                    current = queue.pop()
                    if current in seen:
                        continue
                    seen.add(current)
                    for use in vehicle_uses.get(current, []):
                        if use not in consumers:
                            consumers.append(use)
                        address = '.'.join(use['address'])
                        queue.extend((address, address.split('.')[-1], use['address'][0], use['address'][0].split('.')[-1]))
            else:
                consumers = [{'source_path': path, 'locator': f"L{node['line']}", 'address': node['address'][:-1],
                              'expression': 'distributionTable -> table.insert(Distributions, 1, distributionTable); SuburbsDistributions compatibility alias'}]
            trace = {'family': family, 'source_path': path, 'locator': f"L{node['line']}",
                     'tokens': tokens, 'address': node['address'],
                     'conditions': [v for v in parent.get('values', []) if v['key'] != 'items'],
                     'consumer_connections': consumers,
                     'assessment': 'assessed', 'method': 'item list -> containing distribution -> all declared room/container or vehicle selection references',
                     'finding': 'Declaration/consumer references traced; unreferenced declarations are retained as such.' if consumers else 'No declared consumer reference in these distribution inputs.',
                     'dependency': 'ItemPickerJava namespace lookup, selection and load precedence; no generated loot fact.'}
            traces[identity('trace', trace)] = trace
    for path, text in texts.items():
        if not path.startswith('scripts/'):
            continue
        for row in reader.declarations(text, path):
            if row['kind'] not in {'recipe', 'item', 'evolvedrecipe'}:
                continue
            clauses = [c for c in row['clauses'] if re.match(r'(?:Result\s*:|ReplaceOn\w+\s*=|OnCreate\s*:|OnGiveXP\s*:|LuaCreate\s*=)', c)]
            if not clauses:
                continue
            callbacks = [c.split(':', 1)[1].strip() for c in clauses if re.match(r'OnCreate\s*:', c)]
            definitions = []
            for callback in callbacks:
                definitions.extend(callbacks_by_name[callback])
            reviewed = not callbacks or (all(d['assessment'] == 'assessed' for d in definitions)
                                         and set(callbacks) <= {d['callback'] for d in definitions})
            # A callback name absent from this snapshot has been looked up but
            # cannot be interpreted; its definition is a genuine source boundary.
            missing_callbacks = sorted(set(callbacks) - {d['callback'] for d in definitions})
            if missing_callbacks:
                reviewed = all(d['assessment'] == 'assessed' for d in definitions)
            trace = {'family': 'transformation', 'source_path': path, 'locator': f"L{row['line']}",
                     'tokens': re.findall(r'\b[\w.]+\b', ' '.join(clauses)), 'module': row['module'], 'declaration': row['name'],
                     'raw': row['raw'], 'conditions': row['clauses'], 'callback_definitions': definitions,
                     'consumer_connections': [{'source_path': 'lua/client/TimedActions/ISCraftAction.lua', 'locator': 'L9-L67',
                                                'expression': 'IsRecipeValid -> PerformMakeItem -> getResult/GetFullType -> AddItem(s); callbacks execute inside engine boundary'}],
                     'assessment': 'assessed' if reviewed else 'unreviewed', 'missing_callbacks': missing_callbacks,
                     'method': 'result/replacement clauses and exact callback definition lookup',
                     'finding': 'Callback source lookup and output/mutation interpretation completed; missing definitions and symbolic engine result identity retained.' if reviewed else 'Callback body located but semantic interpretation remains unfinished.',
                     'dependency': 'RecipeManager/module resolution or native item replacement; callback semantics not inferred from its name.'}
            traces[identity('trace', trace)] = trace
    return traces


def creation_traces(texts: dict) -> dict:
    """Trace factory/delivery arguments through local assignments and callers.

    No generic callsite becomes reviewed merely because it was parsed. These
    detailed traces expose precisely which source interpretation remains work.
    """
    traces = {}
    cleaned = {p: reader.mask(t, lua=p.endswith('.lua')) for p, t in texts.items()}
    caller_cache = {}
    for path, text in texts.items():
        if not path.endswith('.lua'):
            continue
        clean = cleaned[path]
        definitions = function_regions(clean)
        review_rule, reading = caller_reading(path, clean)
        for call in CREATE.finditer(clean):
            definition = next((m for m in reversed(definitions) if m['start'] <= call.start() < m['end']), None)
            if definition and call.start() < definition['body_start']:
                continue  # A method declaration is not a creation invocation.
            start = definition['start'] if definition else 0
            end = definition['end'] if definition else len(clean)
            body = clean[start:end]
            argument_end = clean.find('\n', call.end())
            argument = clean[call.end():argument_end if argument_end >= 0 else len(clean)].strip()
            assignments = [{'name': m[1], 'expression': m[2].strip()} for m in re.finditer(r'(?m)^\s*(?:local\s+)?([\w.]+)\s*=\s*([^\n]+)', body)]
            guards = [m[1].strip() for m in re.finditer(r'\b(?:if|elseif|while)\s+([^\n]*?)(?:then|do)', body)]
            function = definition['name'] if definition else 'top-level/anonymous'
            caller_refs = []
            if definition:
                symbol = function.replace(':', '.')
                pattern = re.compile(r'(?<![\w])' + re.escape(symbol).replace(r'\.', r'[.:]') + r'\s*\(')
                if symbol not in caller_cache:
                    for caller_path, caller_text in cleaned.items():
                        for ref in pattern.finditer(caller_text):
                            caller_refs.append({'source_path': caller_path, 'locator': f'L{caller_text.count(chr(10), 0, ref.start()) + 1}'})
                    caller_cache[symbol] = caller_refs
                caller_refs = list(caller_cache[symbol])
            if path == 'lua/server/Vehicles/VehicleCommands.lua' and function == 'Commands.takeEngineParts':
                caller_refs.append({'source_path': 'lua/client/Vehicles/TimedActions/ISTakeEngineParts.lua',
                                    'locator': 'L30-L37', 'expression': "sendClientCommand('vehicle','takeEngineParts') -> Events.OnClientCommand -> Commands.takeEngineParts; commented local AddItems excluded"})
            trace = {'family': 'dynamic', 'source_path': path, 'locator': f'L{clean.count(chr(10), 0, call.start()) + 1}',
                     'function': function, 'parameters': definition['parameters'] if definition else None,
                     'creation_expression': call[0] + argument, 'local_assignments': assignments,
                     'branch_conditions': guards, 'consumer_connections': caller_refs,
                     'function_span': [clean.count(chr(10), 0, start) + 1, clean.count(chr(10), 0, end) + 1],
                     'tokens': re.findall(r'''["']([\w.]+)["']''', body),
                     'assessment': 'assessed' if reading else 'unreviewed', 'review_rule': review_rule,
                     'method': 'factory/delivery call -> enclosing function -> local assignments/guards -> named source callers -> reviewed source-specific interpretation',
                     'finding': reading or 'Source flow located. Branch meaning and reachable acquisition output require explicit interpretation.',
                     'dependency': 'Actual runtime arguments, engine lookup/dispatch and source-specific conditions remain bound to the traced expressions; no general positive/negative inferred.' if reading else 'Unreviewed source-specific creation/delivery semantics; not an engine-only unknown.'}
            traces[identity('trace', trace)] = trace
    return traces


def survey(root: Path, targets: list[str]) -> dict:
    """Read snapshot once, index exact identities and trace bounded consumers.

    Dynamic calls are explicit observations with function bodies and remaining
    dispatch dependencies. They cannot become accepted facts by this survey.
    """
    script_paths = safe_files(root, 'scripts', '.txt')
    lua_paths = safe_files(root, 'lua', '.lua')
    lua_text = {p: inv.local_path(root, p).read_text(encoding='utf-8-sig') for p in lua_paths}
    clean = {p: reader.mask(t, lua=True) for p, t in lua_text.items()}
    callers = {p for p, t in clean.items() if CREATE.search(t)}
    selected = {
        'loot': {PROC, DIST, 'lua/server/Items/SuburbsDistributions.lua', 'lua/server/Items/ItemPicker.lua'},
        'vehicle': {VEHICLE} | {p for p in lua_paths if 'VehicleDistributions' in clean[p]} | {p for p in script_paths if '/vehicles/' in p},
        'foraging': {p for p in lua_paths if '/Foraging/' in p},
        'fishing_trapping': {p for p in lua_paths if '/Fishing/' in p or '/Traps/' in p} | {'lua/client/ISUI/ISFishingUI.lua'},
        'dynamic': callers | {p for p in lua_paths if '/StashDescriptions/' in p},
        'transformation': set(script_paths) | callers | {'lua/server/recipecode.lua', 'lua/client/TimedActions/ISCraftAction.lua'},
    }
    connection_paths = {p for row in recovery_definitions() for p in [row[0], *row[4]]}
    connection_paths.add('lua/client/Vehicles/TimedActions/ISTakeEngineParts.lua')
    selected['dynamic'].update(connection_paths)
    selected['transformation'].update(connection_paths)
    # Follow actual require edges within the repository Lua snapshot. Missing
    # modules are recorded as runtime/engine dependencies, never silently read elsewhere.
    modules = defaultdict(set)
    for p in lua_paths:
        modules['/'.join(p.split('/')[2:])[:-4]].add(p)
    missing = defaultdict(set)
    for family, paths in selected.items():
        queue = list(paths)
        while queue:
            path = queue.pop()
            for module in re.findall(r'\brequire\s*\(?\s*["\']([^"\']+)', clean.get(path, '')):
                matches = modules.get(module, set())
                if not matches:
                    missing[family].add(module)
                for match in matches - paths:
                    paths.add(match)
                    queue.append(match)
    all_paths = sorted(set().union(*selected.values()))
    texts = {p: lua_text[p] if p in lua_text else inv.local_path(root, p).read_text(encoding='utf-8-sig') for p in all_paths}
    sources = [inv.binding(root, p) for p in all_paths]
    hashes = {s['path']: s['sha256'] for s in sources}
    observations, member_refs, hits = {}, {}, defaultdict(list)
    short = defaultdict(list)
    for item in targets:
        short[item.split('.', 1)[1]].append(item)
    target_set = set(targets)
    declarations = defaultdict(list)
    for path in script_paths:
        for row in reader.declarations(texts[path], path):
            if row['kind'] == 'item':
                declarations[row['module'] + '.' + row['name']].append(row)

    def observe(path, line, raw, role, **extra):
        row = {'source_path': path, 'source_sha256': hashes[path], 'locator': f'L{line}',
               'content': {'raw': raw, 'role': role, **extra}}
        oid = identity('obs', row)
        observations[oid] = row
        return oid

    for path, text in texts.items():
        body = clean.get(path, reader.mask(text))
        # Shared evidence includes all static creation callsites, enclosing
        # function identities and actual raw source scope, not just file hashes.
        functions = [(m.start(), m[1]) for m in re.finditer(r'\bfunction\s+([\w.:]+)\s*\(', body)]
        calls = []
        for m in CREATE.finditer(body):
            enclosing = next((n for pos, n in reversed(functions) if pos <= m.start()), 'top-level/anonymous')
            line = body.count('\n', 0, m.start()) + 1
            calls.append({'line': line, 'function': enclosing, 'expression': body[m.start():body.find('\n', m.start()) if '\n' in body[m.start():] else len(body)].strip()})
        member_refs[path] = observe(path, 1, body, 'bounded-member-survey',
                                   line_count=len(text.splitlines()), creation_calls=calls,
                                   method='all declarations/literals, creation callsites and require edges; no execution',
                                   nonordinary=bool(re.search(r'/Debug|/Tests?[/\.]|/Scenarios/|/Admin', path, re.I)))
        # Both exact and short-name leads are retained, but short-name leads
        # cannot qualify an item or produce an acquisition fact.
        pattern = r'''["']([A-Za-z_][\w.]*)["']''' if path.endswith('.lua') else r'(?<![\w.])([A-Za-z_][\w.]*)(?![\w.])'
        for m in re.finditer(pattern, body):
            token = m[1]
            items = [token] if token in target_set else short.get(token, [])
            for item in items:
                oid = observe(path, body.count('\n', 0, m.start()) + 1, token, 'identity-search-lead',
                              item_id=item, match_kind='exact' if token == item else 'unqualified-lead')
                hits[(path, item)].append(oid)
    families = {}
    for family in FAMILIES:
        members = sorted(selected[family])
        families[family] = {'members': members, 'observation_refs': [member_refs[p] for p in members],
                            'method': 'full bound members; declaration/literal and creation-call indexing; require closure; reviewed consumer boundary',
                            'finding': LIMITS[family], 'consumer_trace': LIMITS[family],
                            'missing_requires': sorted(missing[family]), 'closed_negative_capable': False,
                            'version_evidence': 'repository snapshot only; installed game build not verified'}
    print('Acquisition survey: source observations collected; interpreting consumer connections.', flush=True)
    traces = interpretation_traces(texts, declarations)
    traces.update(creation_traces(texts))
    # An unreviewed potentially dynamic output can affect any target. Do not
    # silently remove its obligation just because no item literal was found.
    for family in FAMILIES:
        own = [key for key, t in traces.items() if t['source_path'] in selected[family]]
        families[family]['trace_refs'] = sorted(own)
        families[family]['unreviewed_trace_refs'] = sorted(key for key in own if traces[key]['assessment'] != 'assessed')
    pairs = []
    for item in targets:
        for family in FAMILIES:
            refs = sorted({r for p in families[family]['members'] for r in hits.get((p, item), [])})
            pending = families[family]['unreviewed_trace_refs']
            pairs.append({'item_id': item, 'family_id': family, 'outcome': 'not_attempted' if pending else ('interpretation_unresolved' if refs else 'not_found'),
                          'attempt_ref': identity('attempt', [item, family]), 'observation_refs': refs,
                          'survey_ref': family, 'query': {'exact': item, 'unqualified_lead': item.split('.', 1)[1]},
                          'finding': 'Literal/declaration leads require interpretation.' if refs else 'No identity literal in the bound survey; indirect/constructed identifiers remain open.',
                          'dependency': LIMITS[family],
                          'not_attempted_reason': 'Required creation/callback semantic interpretation is not performed; source collection is not investigation completion.' if pending else None})
    return {'source_bindings': sources, 'families': families, 'observations': observations,
            'coverage': pairs, 'traces': traces, 'texts': texts, 'declarations': declarations, 'member_refs': member_refs}


def positive_paths(survey: dict, targets: list[str]) -> list[dict]:
    """Reviewed exact-identity foraging rule. Other routes remain observations.

    No inference of Base namespace, no arbitrary duplicate declaration winner.
    Fact conditions retain effective defaults and complete truth-changing fields.
    """
    text = survey['texts'][FORAGE]
    clean = reader.mask(text, lua=True)
    start = re.search(r'\bdefaultItemDef\s*=\s*\{', clean).end() - 1
    defaults = fields(table_region(clean, start)[0])
    cat_start = re.search(r'\bdefaultCatDef\s*=\s*\{', clean).end() - 1
    cat_defaults = fields(table_region(clean, cat_start)[0])
    categories = {r['name']: {**cat_defaults, **r['fields']} for r in named_tables(text, 'forageCategories')}
    callbacks = {'doPoisonItemSpawn', 'doRandomAgeSpawn', 'doWildFoodSpawn', 'doWildCropSpawn',
                 'doJunkWeaponSpawn', 'doGenericItemSpawn', 'doClothingItemSpawn', 'doDeadTrapAnimalSpawn'}
    truth_fields = ('minCount', 'maxCount', 'skill', 'perks', 'recipes', 'traits', 'itemTags', 'categories', 'zones',
                    'months', 'spawnFuncs', 'forceOutside', 'isOnWater', 'forceOnWater', 'canBeOnTreeSquare')
    results = []
    rows = named_tables(text, 'forageDefs') + generated_forage_rows(text)
    counts = defaultdict(int)
    for row in rows:
        counts[literal(row['fields'].get('type', ''))] += 1
    for row in rows:
        item = literal(row['fields'].get('type', ''))
        if item not in targets or counts[item] != 1 or len(survey['declarations'].get(item, [])) != 1:
            continue
        props = reader.unique_properties(survey['declarations'][item][0])
        if props is None or props.get('Obsolete', '').lower() == 'true':
            continue
        effective = {**defaults, **row['fields']}
        functions = set(re.findall(r'\bdo\w+\b', effective['spawnFuncs']))
        if functions - callbacks:
            continue
        # Require a literal non-empty month/zone definition and positive count.
        if not re.fullmatch(r'\d+', effective['minCount']) or int(effective['minCount']) < 1:
            continue
        conditions = {k: effective[k] for k in truth_fields}
        category_names = re.findall(r'"([^"]+)"', effective['categories'])
        if not category_names or any(c not in categories or categories[c].get('validFunc', 'nil') != 'nil' for c in category_names):
            continue
        conditions['category_conditions'] = {c: {k: v for k, v in categories[c].items()
                                                 if k in {'name', 'validFloors', 'validFunc', 'zoneChance', 'chanceToCreateIcon', 'chance'}} for c in category_names}
        conditions['eligibility'] = 'Definition registered and nonobsolete; zone/category has positive loot selection; valid month, averaged perks, known recipes, traits, tagged tools, square/floor eligibility; icon spotted, target container allows the item, adjacent square reachable, action valid with live manager/icon and unblocked square, not discarded. Lua registry unmodified by external extensions.'
        conditions['delivery'] = 'ISBaseIcon creates the exact type; reviewed spawn callbacks preserve that item and may alter state/add seeds; addOrDropItems adds to inventory or drops on square if full.'
        results.append({'item_id': item, 'family': 'foraging', 'rule': 'foraging', 'path': FORAGE,
                        'line': row['line'], 'raw': row['raw'], 'conditions': conditions,
                        'route': {'method': 'foraging', 'definition': row['name']},
                        'consumer_paths': [SYSTEM, 'lua/client/Foraging/ISBaseIcon.lua', 'lua/client/Foraging/ISForageAction.lua'],
                        'limitations': 'No chance, guaranteed spawn, freshness or nutrition claim. Generated definitions and runtime extensions are additional open routes.'})
    crop_match = re.search(r'local seedTable\s*=\s*\{', clean)
    seed_map = fields(table_region(clean, crop_match.end() - 1)[0])
    for path in list(results):
        if 'doWildCropSpawn' not in path['conditions']['spawnFuncs']:
            continue
        item = literal(seed_map.get(path['item_id'], ''))
        if item not in targets or len(survey['declarations'].get(item, [])) != 1:
            continue
        results.append({**path, 'item_id': item,
                        'route': {'method': 'foraging_crop_seed', 'crop_item': path['item_id'], 'definition': path['route']['definition']},
                        'raw': {'crop': path['raw'], 'seed_mapping': seed_map[path['item_id']]},
                        'conditions': {**path['conditions'], 'seed_branch': 'doWildCropSpawn: seedTable[crop type] exists and ZombRand(100)+1 <= 75; seedAmount=ZombRand(20)+1',
                                       'eligibility': path['conditions']['eligibility'] + ' The crop seed callback random branch also succeeds.'}})
    # Straight-line animal/fish property registrations. Keep every constraint
    # expression (including bait/lure/zone/time) without turning weights into odds.
    for path, registry, method, consumers, eligibility in (
        (FISH, 'fishes|trashItems', 'fishing', ['lua/client/Fishing/TimedActions/ISFishingAction.lua'],
         'Valid fishing action at water, fishing zone has stock, eligible lure or spear, successful attraction/selection and unbroken line for a fish; selected inventory capacity controls delivery.'),
        (TRAP, 'Animals', 'trapping', ['lua/server/Traps/STrapGlobalObject.lua', 'lua/server/Traps/trappingCommands.lua', 'lua/client/Traps/TimedActions/ISCheckTrapAction.lua'],
         'An undestroyed trap with fresh eligible bait, listed trap/zone, allowed hour and successful random checks catches the animal while not near a streamed square; animal remains present when player checks the trap.'),
    ):
        source = reader.mask(survey['texts'][path], lua=True)
        common_lures = []
        if method == 'fishing':
            common = re.search(r'local lureItems\s*=\s*\{', source)
            common_lures = re.findall(r'"([^"\\]+)"', table_region(source, common.end() - 1)[0])
        variables = {m[1] for m in re.finditer(r'table\.insert\((?:' + registry + r'),\s*(\w+)\)', source)}
        for name in sorted(variables):
            properties = list(re.finditer(r'(?m)^' + re.escape(name) + r'(?P<key>[.\[][^\n=]*?)\s*=\s*(?P<value>[^\n;]+);?', source))
            item_rows = [m for m in properties if m['key'] == '.item']
            if len(item_rows) != 1:
                continue
            item = literal(item_rows[0]['value'])
            if item not in targets or len(survey['declarations'].get(item, [])) != 1:
                continue
            conditions = {'eligibility': eligibility,
                          'definition': {m['key']: m['value'].strip() for m in properties},
                          'lure_entries': re.findall(r'table\.insert\(' + name + r'\.lure,\s*"([^"]+)"\)', source),
                          'runtime_boundary': 'Unmodified registered snapshot; world state/random outcome is a prerequisite, never a guaranteed catch.'}
            if method == 'fishing' and re.search(r'table\.insert\(fishes,\s*' + re.escape(name) + r'\)', source):
                conditions['lure_entries'] += common_lures
            results.append({'item_id': item, 'family': 'fishing_trapping', 'rule': method,
                            'path': path, 'line': source.count('\n', 0, item_rows[0].start()) + 1,
                            'raw': '\n'.join(m[0] for m in properties), 'conditions': conditions,
                            'route': {'method': method, 'definition': name}, 'consumer_paths': consumers,
                            'limitations': 'No chance, yield, size, freshness or nutritional claim; runtime extensions and other paths remain open.'})
    return results


def starter_paths(survey: dict, targets: list[str]) -> list[dict]:
    """Interpret the reviewed OnNewGame branch graph, including nested bag guards."""
    path = 'lua/client/Items/SpawnItems.lua'
    text = reader.mask(survey['texts'][path], lua=True)
    inv.require('Events.OnNewGame.Add(SpawnItems.OnNewGame)' in text, 'new game dispatch changed')
    begin = text.index('function SpawnItems.OnNewGame(')
    end = text.index('function SpawnItems.OnGameStart(')
    sections = [('default', begin), ('starter_kit', text.index('if SandboxVars.StarterKit then')),
                ('Easy', text.index('if getWorld():getDifficulty() == "Easy"')),
                ('Normal', text.index('elseif getWorld():getDifficulty() == "Normal"')),
                ('Hard', text.index('elseif getWorld():getDifficulty() == "Hard"')),
                ('server_configuration', text.index('if isClient() then'))]
    paths = []
    for m in re.finditer(r'(?m)^([^\n]*:AddItem\("([^"]+)"\)[^\n]*)', text[begin:end]):
        pos, item = begin + m.start(), m[2]
        if item not in targets or len(survey['declarations'].get(item, [])) != 1:
            continue
        section, section_start = next((n, p) for n, p in reversed(sections) if p <= pos)
        if section == 'server_configuration':
            continue
        conditions = {'eligibility': 'New player OnNewGame event invokes the registered SpawnItems.OnNewGame callback with a valid player inventory; snapshot registry and callback remain unmodified.',
                      'delivery': 'schoolbag inventory' if 'bag:getItemContainer()' in m[1] else 'player inventory'}
        if section == 'starter_kit':
            conditions['sandbox'] = 'SandboxVars.StarterKit is true'
        elif section != 'default':
            conditions['difficulty'] = section
        if section in {'Easy', 'Normal'}:
            block = text[section_start:pos]
            if 'if not bag then' in block and 'end;' not in block.split('if not bag then', 1)[1]:
                conditions['bag_guard'] = 'FindAndReturn("Base.Bag_Schoolbag") returned no bag at this branch'
        if section in {'starter_kit', 'Normal'} and item in {'Base.BaseballBat', 'Base.Hammer'}:
            conditions['initial_condition'] = 7 if item == 'Base.BaseballBat' else 5
        conditions['eligibility'] += ' All listed sandbox, difficulty and bag predicates hold; preceding callback steps succeed.'
        paths.append({'item_id': item, 'family': 'dynamic', 'rule': 'new_game', 'path': path,
                      'line': text.count('\n', 0, pos) + 1, 'raw': m[1].strip(),
                      'route': {'method': 'new_game', 'branch': section}, 'conditions': conditions,
                      'consumer_paths': [path], 'limitations': 'Conditional starting inventory only. Server SpawnItems values and the mismatched OnGameStart registration remain open.'})
    return paths


def recovery_definitions() -> list[tuple]:
    """Reviewed broad acquisition routes, not a Layer 4 action catalogue."""
    menu = 'lua/client/ISUI/ISWorldObjectContextMenu.lua'
    inventory = 'lua/client/ISUI/ISInventoryPaneContextMenu.lua'
    actions = 'lua/client/TimedActions/'
    fishing = 'lua/client/Fishing/TimedActions/ISFishingAction.lua'
    return [
        (actions + 'ISTakeGenerator.lua', 'Base.Generator', 'world_generator_recovery',
         'Existing world generator, object index not -1, not connected, adjacent square reachable, queued pickup completes without walking/running interruption. Condition and positive fuel are copied; item enters inventory and both hands after prior heavy items are dropped.', [menu]),
        ('lua/client/Farming/TimedActions/ISPlowAction.lua', 'Base.Worm', 'incidental_plowing',
         'Valid selected natural-floor farming plot: no prior farming object, square free, and hands uninjured if no tool. Queued plowing completes, farming plow command/changePlayer calls return, and ZombRand(5)==0. Worm is added to player inventory; no probability conversion or guaranteed output.',
         ['lua/server/Farming/BuildingObjects/farmingPlot.lua', 'lua/client/Farming/ISUI/ISFarmingMenu.lua']),
        ('lua/client/BuildingObjects/TimedActions/ISShovelGround.lua', 'Base.Worm', 'incidental_ground_digging',
         'Reachable selected ground with sprite and an owned bag; InventoryContainer bag is empty, and bag has HoldDirt tag or usedDelta<1. Ground-shoveling action and bag handling complete and ZombRand(5)==0. Adds Worm to inventory.', ['lua/server/BuildingObjects/ISShovelGroundCursor.lua']),
        (actions + 'ISGetCompost.lua', 'Base.CompostBag', 'compost_collection',
         'Reachable compost object and selected eligible empty sandbag transferred to player inventory. Compost amount >= 10/(1/scriptUseDelta), owned input type is not CompostBag, action completes. Input is removed; new bag enters inventory/primary hand with min(floor(amount/compostPerUse),usesPerBag) uses; compost is consumed.', [menu]),
        ('lua/client/Blacksmith/TimedActions/ISRemoveDrum.lua', 'Base.MetalDrum', 'world_drum_recovery',
         'Existing selected metal drum with square, adjacent square reachable, registered Blacksmith menu removal queued and completes. World drum is removed before exact item is added to inventory. No assertion that a drum exists in every world.', ['lua/client/Blacksmith/ISUI/ISBlacksmithMenu.lua']),
        (actions + 'ISPadlockAction.lua', 'Base.KeyPadlock', 'padlock_key_issue',
         'Reachable lockable selected object and owned padlock; lock=true action completes, supplied padlock numberOfKey>0. Matching key ID is copied to newly added keys and object; original padlock is consumed. Count depends on supplied padlock.', [menu]),
        (actions + 'ISPadlockAction.lua', 'Base.Padlock', 'padlock_recovery',
         'Reachable padlocked selected object and matching key in inventory; lock=false action completes. Recovered padlock copies key ID, numberOfKey=1; matching key is consumed and object lock cleared.', [menu]),
        (actions + 'ISSplint.lua', 'Base.RippedSheets', 'splint_material_recovery',
         'Health-panel removal of existing splint; patient has not moved, doIt=false, stored splint item exists and is not Base.Splint. RippedSheets and stored splint item are returned to doctor inventory; body-part splint is cleared.', ['lua/client/XpSystem/ISUI/ISHealthPanel.lua']),
        (actions + 'ISRipClothing.lua', 'Base.Thread', 'clothing_material_recovery',
         'Owned eligible clothing with valid ClothingRecipesDefinitions or FabricType material mapping; rip action completes with isSheetRope=false. ZombRand(7)<Tailoring+1. Thread is created, Use applied 10-max times where max=ZombRand(2, min(coveredParts,6)) or default 2, and remaining thread is added to inventory. Input clothing is consumed.', [inventory, 'lua/shared/Definitions/ClothingRecipesDefinitions.lua']),
        (actions + 'ISDestroyStuffAction.lua', 'Base.Sheet', 'curtain_material_recovery',
         'Existing selected destructible object within 1.6 on both X/Y, usable sledgehammer (or explicit build cheat), completed destruction. After wall/window selection, resulting object is an IsoWindow with curtains OR IsoCurtain with a square. Curtain is removed and exact Sheet dropped on that square; generic wall destruction alone does not suffice.', ['lua/server/BuildingObjects/ISDestroyCursor.lua']),
        (actions + 'ISDropWorldItemAction.lua', 'Base.Candle', 'placed_lit_candle_replacement',
         'Owned CandleLit selected for placement; target floor total item weight plus item weight<=50 and action completes. Replacement Candle copies usedDelta, condition and favorite state; old item removed and replacement placed on requested square.', [inventory]),
        (actions + 'ISInventoryTransferAction.lua', 'Base.Candle', 'transferred_lit_candle_replacement',
         'Valid accessible source/destination and capacity, consistent item transaction, not already transferred, dontAdd=false, favorite item allowed at destination. CandleLit in non-floor-to-world and non-world-item pickup branch is replaced in destination container; usedDelta, condition and favorite copied. Transfer must complete with no cancellation.', [inventory]),
        (fishing, 'Base.WoodenStick', 'crafted_rod_breakage',
         'Valid fishing action reaches brokeThisLine after selected-fish line-break branch succeeds under size, skill, twine, crafted-rod and spear modifiers. Pole type CraftedFishingRod or CraftedFishingRodTwineLine; exact WoodenStick enters inventory and rod/lure cleanup follows.', [menu]),
        (fishing, 'Base.FishingRodBreak', 'manufactured_rod_breakage',
         'Valid fishing action reaches brokeThisLine after selected-fish line-break branch succeeds under size, skill and twine modifiers. Pole type FishingRod or FishingRodTwineLine; exact FishingRodBreak enters inventory and rod/lure cleanup follows.', [menu]),
    ]


def recovery_paths(survey: dict, targets: list[str]) -> list[dict]:
    paths = []
    for path, item, method, conditions, consumers in recovery_definitions():
        if item not in targets or len(survey['declarations'].get(item, [])) != 1:
            continue
        props = reader.unique_properties(survey['declarations'][item][0])
        if props is None or props.get('Obsolete', '').lower() == 'true':
            continue
        text = reader.mask(survey['texts'][path], lua=True)
        matches = list(re.finditer(r'(?:CreateItem|AddItems?)\("' + re.escape(item) + r'"[^\n]*', text))
        inv.require(bool(matches), 'reviewed exact recovery source changed: ' + method)
        for match in matches:
            paths.append({'item_id': item, 'family': 'dynamic', 'rule': 'conditional_recovery', 'path': path,
                          'line': text.count('\n', 0, match.start()) + 1, 'raw': match[0],
                          'route': {'method': method}, 'conditions': {'eligibility': conditions,
                              'execution_boundary': 'Unmodified snapshot, successful valid action and existing target/input conditions; earlier callback operations succeed.'},
                          'consumer_paths': [path, *consumers],
                          'limitations': 'Conditional broad recovery/incidental output, not guaranteed world availability, efficiency, probability or a complete crafting/action procedure.'})
    return paths
