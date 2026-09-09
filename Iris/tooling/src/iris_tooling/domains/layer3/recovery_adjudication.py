"""Question-local source attribution, retaining separate unfinished work.

Route observations are evidence inputs, never the blocker decision. Each rule
states which part of an exact axis/scope those observations answer and which
consumer boundary still owns its residual. Attribution does not mean recovery
is complete; available but unimplemented interpretations stay in remaining_work.
"""
from collections import defaultdict
from copy import deepcopy
import re

from . import semantic_model as model
from . import semantic_results as semantic
from . import recovery_sources as sources


NATIVE_FIELDS = {
    'activity:ingestion': ('Type', 'CantEat', 'CustomContextMenu', 'CustomMenuOption', 'HungerChange', 'ThirstChange',
                           'BoredomChange', 'UnhappyChange', 'StressChange', 'Poison', 'PoisonDetectionLevel',
                           'OnEat', 'RequireInHandOrInventory', 'DangerousUncooked'),
    'activity:reading': ('Type', 'CanBeWrite', 'SkillTrained', 'LvlSkillTrained', 'NumLevelsTrained',
                         'NumberOfPages', 'TeachedRecipes', 'BoredomChange', 'UnhappyChange', 'StressChange'),
    'activity:wearing': ('Type', 'BodyLocation', 'CanBeEquipped', 'ClothingItemExtra', 'ClothingItemExtraOption'),
    'activity:combat': ('Type', 'Ranged', 'AmmoType', 'MagazineType', 'Categories', 'CanBePlaced',
                        'ExplosionPower', 'FirePower', 'SmokeRange', 'NoiseRange', 'OnWeaponSwing', 'OnWeaponHit'),
    'activity:storage': ('Type', 'Capacity', 'AcceptItemFunction', 'CanBeEquipped', 'OnlyAcceptCategory'),
    'activity:expenditure': ('Type', 'UseDelta', 'IsWaterSource', 'ReplaceOnDeplete', 'OnCreate', 'OnEat'),
    'activity:cooking': ('Type', 'EvolvedRecipe'),
}
CONSUMERS = {
    'activity:ingestion': semantic.EAT, 'activity:reading': semantic.READ,
    'activity:wearing': semantic.WEAR, 'activity:combat': sources.FIREARM,
    'activity:storage': semantic.TRANSFER, 'activity:expenditure': semantic.DRINK,
    'activity:crafting': semantic.CRAFT, 'activity:cooking': semantic.COOK,
    'activity:world_work': semantic.PROPS, 'item:direct': semantic.MENU,
}

# Exact untagged melee declarations examined against the selected inventory,
# hotbar, campfire and registered context dispatch. Capability-bearing tools
# (fitness weights, barricading tools, plumbing wrench) are separate families.
PLAIN_MELEE_ITEMS = {'Base.' + name for name in (
    'LeadPipe', 'Nightstick', 'MetalBar', 'MetalPipe', 'MeatCleaver', 'HandScythe', 'PipeWrench',
    'Saxophone', 'Trumpet', 'Violin', 'Drumstick', 'Plunger', 'Flute', 'ChairLeg',
    'PickAxeHandle', 'PickAxeHandleSpiked', 'TableLeg', 'BadmintonRacket', 'TennisRacket',
    'Wrench', 'RollingPin', 'Pan', 'GridlePan', 'Chainsaw', 'Golfclub', 'Katana',
    'Banjo', 'GuitarAcoustic', 'Plank', 'PlankNail', 'Poolcue', 'HockeyStick',
    'IceHockeyStick', 'LaCrosseStick', 'CanoePadel', 'CanoePadelX2', 'BaseballBat',
    'BaseballBatNails', 'FishingRodBreak', 'LeafRake', 'Rake', 'GuitarElectricBassBlack',
    'GuitarElectricBassBlue', 'GuitarElectricBassRed', 'Keytar', 'GuitarElectricBlack',
    'GuitarElectricBlue', 'GuitarElectricRed', 'IcePick', 'LetterOpener', 'Scalpel',
    'Stake', 'ClosedUmbrellaBlue', 'ClosedUmbrellaRed', 'ClosedUmbrellaBlack',
    'ClosedUmbrellaWhite', 'WoodenLance')}
PLAIN_MELEE_FIELDS = {
    'AimingMod', 'AlwaysKnockdown', 'AttachmentType', 'BaseSpeed', 'BreakSound', 'Categories',
    'CloseKillMove', 'ConditionLowerChanceOneIn', 'ConditionMax', 'CritDmgMultiplier', 'CriticalChance',
    'DamageCategory', 'DamageMakeHole', 'DisplayCategory', 'DisplayName', 'DoorDamage', 'DoorHitSound',
    'EnduranceMod', 'HitAngleMod', 'HitFloorSound', 'HitSound', 'Icon', 'IdleAnim', 'ImpactSound',
    'IsAimedHandWeapon', 'KnockBackOnNoDeath', 'KnockdownMod', 'MaxDamage', 'MaxHitCount', 'MaxRange',
    'MetalValue', 'MinAngle', 'MinDamage', 'MinRange', 'MinimumSwingTime', 'PushBackMod',
    'RequiresEquippedBothHands', 'RunAnim', 'SoundMap', 'SplatBloodOnNoDeath', 'SplatNumber', 'SplatSize',
    'SubCategory', 'SwingAmountBeforeImpact', 'SwingAnim', 'SwingSound', 'SwingTime', 'Tooltip',
    'TreeDamage', 'TwoHandWeapon', 'Type', 'WeaponLength', 'WeaponSprite', 'Weight', 'critDmgMultiplier'}


def reassess(base, payload, audit):
    location_source = base['reader'].read(sources.BODY_LOCATIONS).decode('utf-8-sig')
    exclusive_pairs = re.findall(r'^group:setExclusive\("([^"]+)",\s*"([^"]+)"\)', location_source, re.M)
    hidden_pairs = re.findall(r'^group:setHideModel\("([^"]+)",\s*"([^"]+)"\)', location_source, re.M)
    facts = {f['fact_id']: f for f in payload['facts']}
    by_question = defaultdict(list)
    for binding in payload['fact_question_bindings']:
        by_question[tuple(binding['question_key'])].append(binding)
    attempts = defaultdict(dict)
    for ref, attempt in payload['attempts'].items():
        attempts[attempt['item_id']][attempt['route']] = (ref, attempt)
    observations = payload['observations']
    results = {model.question_key(r): r for r in payload['results']}
    for row in audit:
        if row['attribution_status'] == 'attributed':
            continue  # The independently reviewed writable-note branch.
        key = tuple(row['question_key'])
        item, axis, scope = key
        result = results[key]
        records = base['declarations'].get(item, [])
        fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
        related = [facts[b['fact_ref']] for b in by_question[key]]
        partial_refs = sorted(f['fact_id'] for f in related)
        route = {'activity:crafting': 'B', 'activity:cooking': 'C', 'activity:world_work': 'D',
                 'item:direct': 'E'}.get(scope, 'A')
        attempt_ref, attempt = attempts[item][route]
        refs = sorted(set(attempt['observation_refs']) | {
            oid for f in related for p in f['provenance_refs'] for oid in payload['provenance'][p]['observation_refs']})
        applied = {'declarations': [{'path': r['path'], 'line': r['line'], 'end_line': r['end_line']} for r in records],
                   'field_values': {k: fields[k] for k in NATIVE_FIELDS.get(scope, ()) if k in fields},
                   'field_conflicts': {k: v for k, v in conflicts.items() if k in NATIVE_FIELDS.get(scope, ())},
                   'consumer': CONSUMERS[scope], 'route_observation_ref': attempt_ref,
                   'participation': deepcopy(attempt['finding']) if route in 'BCD' else None}
        answered = [{'fact_ref': f['fact_id'], 'fact_kind': f['fact_kind'], 'payload': f['payload']} for f in related]
        result['provenance_refs'] = sorted(set(result['provenance_refs']) |
                                           {p for f in related for p in f['provenance_refs']})
        residual, work, failure = None, None, False
        terminal_reason = None
        if len(records) != 1:
            failure = True
            residual = {'meaning': axis + ' in ' + scope,
                        'required_input': 'an exact runtime declaration binding for ' + item,
                        'reason': ('No exact declaration exists in the bound raw script snapshot.' if not records else
                                   'Multiple raw declarations remain; their load order/winner is not established by this snapshot.')}
        elif applied['field_conflicts']:
            failure = True
            residual = {'meaning': axis + ' interpretation of ' + ', '.join(applied['field_conflicts']),
                        'required_input': 'consumer-compatible resolution of the conflicting scalar properties',
                        'reason': 'The listed exact relevant properties conflict; unrelated repeated properties do not block this question.'}
        elif result['state'] == 'evidence_backed_not_applicable':
            if scope == 'activity:ingestion' and axis in {'operation', 'effects'} and fields.get('Type') == 'Food' and fields.get('CantEat', '').lower() == 'true':
                terminal_reason = 'The exact Food/CantEat=true declaration is excluded by the native eating menu predicate; transformed forms and independent direct actions remain separate.'
            else:
                raise ValueError('historical negative requires new scoped exclusion evidence')
        elif scope == 'item:direct':
            context_refs = base.get('inventory_context_sources', {})
            refs = sorted(set(refs) | set(context_refs.values()))
            applied['registered_inventory_consumers'] = {
                'source_observation_refs': context_refs,
                'ContextRadio': {'declared_type': fields.get('Type'), 'required_runtime_class': 'Radio'},
                'ContextMovable': {'declared_type': fields.get('Type'), 'required_runtime_class': 'Moveable',
                                  'selection': 'main inventory and not held; radio/world-model exception is retained'},
                'ContextMedia': {'declared_media_category': fields.get('MediaCategory'),
                                'selection': 'recorded media, main inventory, assigned translated extra text'},
                'general_management': 'Favorite, ordinary transfer/drop/holding and debug/admin deletion are general inventory management. Item-specific effects and functional held-state prerequisites remain separate.',
                'limit': 'These are the examined local registered consumers, not a claim that an unknown runtime registry is empty.'}
            if any(f['item_id'] == item and f['payload'] == {'function': 'wash_carried_equipment'} for f in facts.values()):
                washing_paths = {sources.WORLD_MENU, sources.WASH_CLOTHING, sources.TAKE_WATER}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in washing_paths})
                applied['shared_equipment_washing'] = {
                    'exact_type': fields.get('Type'), 'source_paths': sorted(washing_paths),
                    'selection': 'Carried bloody Weapon or nonhidden bloody/dirty Clothing/Container; same-building reachable manual water source, ten water units per action.',
                    'answered': 'The direct function and blood-clearing effect retain full water, optional-soap and interruption predicates. Clothing additionally has dirt-clearing and fully-wet effects; nonclothing container dirt is not claimed cleared.',
                    'independence': 'This shared state-changing consumer is included even for previously reviewed spear/clock/strap families. It does not alone close other direct operations or other activity scopes.'}
            if any(f['item_id'] == item and f['payload'].get('function') in {
                    'receive_garment_patch', 'remove_garment_patch', 'apply_garment_patch', 'unpick_garment_patch'} for f in facts.values()):
                patch_paths = {semantic.MENU, sources.GARMENT_UI, sources.PATCH_GARMENT, sources.REMOVE_PATCH, semantic.CLOTHING}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in patch_paths})
                applied['shared_garment_patching'] = {
                    'source_paths': sorted(patch_paths),
                    'declaration': {k: fields.get(k) for k in ('Type', 'BloodLocation', 'FabricType', 'Tags')},
                    'entry': 'The active Inspect entry requires covered parts, transfers the garment and opens ISGarmentUI. Its part list filters covered parts by available textures; the legacy direct patch-menu invocation is commented out.',
                    'answered': 'Exact needle/type-tag, three fabrics and Thread selection; existing-patch exclusion/removal, hole versus padding, transfer/continued inventory guards, walking/running interruptions, fabric/thread use and tailoring XP are represented.',
                    'batch': 'Patch-all uses actual part iteration, fabric count and thread-array accounting; individual actions retain their own validity. The supplied nil-fabric/thread fallback dereferences nil, so it is not represented as successful fallback recovery.',
                    'native_boundary': 'Clothing covered-part/fabric binding, canFullyRestore/addPatch protection and restoration, and returned fabric mapping/factory after removePatch remain native dependencies. The tooltip reads native defense values rather than computing them.'}
            residual = {'meaning': ('item-specific direct functions and state changes still awaiting local attribution' if axis == 'operation'
                                    else 'conditions of item-specific direct functions still awaiting local attribution'),
                        'required_input': 'Question-local interpretation of the bound selected-item menu, registered context handlers and hotbar consumers for ' + item,
                        'reason': 'These local sources are available but their applicability to this exact question is not yet fully adjudicated. This is unfinished investigation, not evidence that a hypothetical runtime registry or variable game state blocks the question.',
                        'boundary_kind': 'available_local_work'}
            # Comparison and question completion are independent obligations.
            # Only the specific rules below can name an examined native limit.
            work = 'Reassess this exact axis/scope against applicable selected-item branches and called consumers, and complete its independent predecessor-claim comparison.'
            medical_fields = {'DisplayCategory', 'Type', 'UseDelta', 'UseWhileEquipped', 'DisplayName', 'Icon',
                              'Weight', 'AlcoholPower', 'Tooltip', 'Medical', 'WorldStaticModel', 'Tags', 'ConsolidateOption'}
            if (item == 'Base.AlarmClock' and fields.get('Type') == 'Weapon'
                    and fields.get('PhysicsObject') == 'NoiseGenerator' and not conflicts):
                paths = {semantic.MENU, sources.FIREARM, sources.DEVICE_TIMER, sources.DEVICE_PLACE,
                         sources.WORLD_MENU, sources.DEVICE_TAKE}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'noise_device_controls'
                applied['direct_scope'] = {
                    'identity': 'Base.AlarmClock is the obsolete Weapon/NoiseGenerator, not the AlarmClock-class Base.AlarmClock2.',
                    'answered': 'Positive timer setter, inventory-guarded current-square placement and conditional world-trap retrieval are represented with interruptions and item transfers.',
                    'native_boundary': 'IsoTrap owns countdown, sound and post-activation item retention; OBSOLETE availability is not inferred.',
                    'attack': 'attackHook checks attack-started/player authorization and the non-ranged vehicle restriction, then passes chargeDelta or zero to DoAttack. It does not interpret PhysicsObject, SwingAnim=Throw or UseSelf. This is not admitted as a melee hit.',
                    'selected_item': 'The positive timer and placement fields select the represented menus. There is no declared remote-control capability, magazine, weapon attachment, clothing form, light activation or health capability in this exact record. General inventory management is excluded under the adopted scope.'}
                work = None
                residual = {'meaning': ('Delayed sound, post-activation reuse and the NoiseGenerator throwing/consumption outcome' if axis == 'operation' else
                                       'Native countdown/reuse and PhysicsObject/UseSelf execution conditions'),
                            'required_input': 'IsoTrap/NoiseGenerator and DoAttack interpretation of PhysicsObject=NoiseGenerator, SwingAnim=Throw and UseSelf=TRUE; obsolete-item availability',
                            'reason': 'The exact local placement, retrieval, timer and weapon dispatch paths are interpreted. Native device execution, throwing/consumption and obsolete availability remain; raw zero damage and reusable fields do not establish negative combat effects or guaranteed reuse.',
                            'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.SPEAR_ITEMS and not conflicts
                    and fields.get('AttachmentType') == 'Shovel'
                    and any(f['item_id'] == item and f['payload'] == {'function': 'fish_with_spear'} for f in facts.values())):
                paths = {semantic.MENU, sources.FIREARM, sources.WORLD_MENU, sources.FISHING_UI,
                         sources.FISHING_ACTION, sources.FISHING_PROPERTIES, semantic.GROUPS,
                         semantic.FIX, 'scripts/fixing.txt', sources.HOTBAR, sources.HOTBAR_SLOTS,
                         sources.HOTBAR_ATTACH}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'spear_attack_fishing_and_transformation'
                applied['direct_scope'] = {
                    'declaration': {k: fields.get(k) for k in ('Type', 'Categories', 'SwingAnim', 'DamageCategory', 'Tags', 'AttachmentType')},
                    'attack': 'The non-ranged attack hook checks authorization, attack-started state and vehicle/shove restrictions before DoAttack. The conditional dispatch is represented; SwingAnim=Spear does not establish that every attack is a thrust.',
                    'fishing': 'The inventory predicate, native spear classification, adjacent-water search, hand equipment, continued primary-hand identity, interruptions, fish selection and actual spear-condition loss branch are interpreted. Breaking removes the spear from the hands and stops the action, without creating a broken fishing-rod form.',
                    'transformations': base.get('spear_recipe_sources', {}).get(item, []),
                    'callback_scope': 'CreateSpear, UpgradeSpear and DismantleSpear condition assignments and their selected-item roles are represented. Callback wear/removal uses the existing direct operation axis; crafting role/condition questions retain their own bindings.',
                    'hotbar': 'AttachmentType=Shovel maps to Shovel Back in Back slots and Shovel Back with Bag under the Bag replacement. Availability, broken-item rejection, replacement and attach/remove/quick retrieval are ordinary equipment management, excluded by the adopted P4 clarification. This does not establish slot provision or a unique spear capability, and does not discharge predecessor compatibility claims.',
                    'repair': 'Exact fixing records exist for SpearCrafted and twelve attached forms, but not SpearFork. Existing repair-target and world-work facts preserve those records and action conditions. ISFixAction delegates condition/material outcome to FixingManager.',
                    'other_entries': 'These exact Weapon declarations have no ranged ammunition, remote-control, light, health, clothing, radio or recorded-media capability selecting an additional examined menu branch.'}
                has_repair = any(f['item_id'] == item and f['payload'] == {'role': 'repair_target'} for f in facts.values())
                work = None
                residual = {'meaning': ('Native spear attack and fishing outcome beyond the represented dispatch and condition assignments' if axis == 'operation' else
                                       'Native attack resolution and spear classification/creation conditions beyond the represented local guards'),
                            'required_input': 'DoAttack interpretation of spear animation, hit and damage; WeaponType spear classification and fishing item factory delivery; RecipeManager result creation' + ('; FixingManager repair outcome and material use' if has_repair else ''),
                            'reason': 'The selected local attack, fishing, transformation, applicable repair and hotbar branches have been interpreted. The named native executors remain distinct from answered conditional functions and callback state changes; changing current condition, skill or fish availability is not itself a blocker.',
                            'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Soap2', 'Base.CleaningLiquid2'} and not conflicts
                    and fields.get('Type') == 'Drainable'
                    and any(f['item_id'] == item and f['payload'] == {'function': 'wash_body'} for f in facts.values())):
                paths = {semantic.MENU, sources.WORLD_MENU, sources.WASH_BODY, sources.WASH_CLOTHING,
                         sources.TAKE_WATER, sources.CONSOLIDATE}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'washing_supply_and_consolidation'
                applied['direct_scope'] = {
                    'declaration': fields,
                    'selection': 'The water-source menu collects Soap2 and CleaningLiquid2 by inventory type; same-building context and walk-adjacent guards are interpreted. Washers/dryers are excluded from this manual-washing entry.',
                    'washing': 'Body and equipment actions clear actual blood/dirt fields, spend supply for blood only, send water-use commands and have distinct validity/time branches. Body washing removes four makeup slots; clothes become wet. Insufficient soap does not forbid washing. All these qualifications are represented.',
                    'consolidation': ('CleaningLiquid2 reaches canConsolidate and same-type receiver selection; actual progressive fraction transfer, inventory guard, interruption and depleted donor Use are represented.' if item == 'Base.CleaningLiquid2' else
                                      'Soap2 explicitly declares cantBeConsolided=TRUE. No positive consolidation fact is admitted; the native canConsolidate interpretation of that field remains the specific eligibility boundary.'),
                    'other_entries': 'These exact drainables declare no water-source/replacement, light activation, bandage/alcohol, wearable, media, map, weapon, remote or special named menu capability. UseWhileEquipped is false. General management is excluded; expenditure and any recipe participation retain their own questions.'}
                work = None
                residual = {'meaning': ('Native supply depletion and exact consolidation eligibility/outcome' if axis == 'operation' else
                                       'Native remaining-use and consolidation type/field interpretation'),
                            'required_input': 'DrainableComboItem remaining-use/Use depletion and canConsolidate' + ('/same-type receiver matching' if item == 'Base.CleaningLiquid2' else ' interpretation of cantBeConsolided=TRUE'),
                            'reason': 'The local washing selection, field assignments, time calculation, supply-use and consolidation branches are interpreted. Native depletion and the exact named consolidation eligibility remain; variable water, blood, dirt or supply amounts are expressed conditions rather than blockers.',
                            'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.PLAIN_OBJECT_LABELS and fields.get('Type') == 'Normal'
                    and set(fields) <= sources.PLAIN_OBJECT_FIELDS and not conflicts
                    and ({'provide_campfire_tinder', 'supply_campfire_fuel'} | set(base.get('heat_control_sources', {}).get(item, {}).get('functions', []))) == {
                        f['payload']['function'] for f in facts.values() if f['item_id'] == item and f['fact_kind'] == 'direct_function'}):
                paths = {semantic.MENU, sources.CAMP_MENU, sources.CAMP_FUEL, sources.CAMP_LIGHT,
                         sources.CAMP_ADD, sources.CAMP_CLIENT, sources.CAMP_SERVER, sources.CAMP_COMMANDS,
                         sources.CAMP_OBJECT, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'plain_objects_with_exact_campfire_entries'
                applied['direct_scope'] = {'declaration': fields, 'fuel': sources.CAMP_FUEL_USE,
                    'tinder': sources.CAMP_TINDER_USE,
                    'other_dispatch': 'These strict plain Normal declarations have exact positive fuel and tinder entries, unlike the no-entry plain objects. Their names do not additionally select card-game, currency or napkin-washing actions. Common typed medical/water/weapon/wear/media/activation handlers have no matching capability field; independent recipe roles and general inventory management remain separate.'}
                work = None
                residual = {'meaning': 'Native exact inventory removal and campfire object/command delivery',
                    'required_input': 'Native inventory membership/removal and campfire persistent object binding for the represented fuel/tinder action',
                    'reason': 'Exact positive fuel/tinder registry and all local menu, timed consumption and server fuel/light conditions are represented. Current fire/fuel/igniter states are conditions, not local investigation blockers.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.OBJECT_LABELS and fields.get('Type') == 'Normal'
                    and set(fields) <= sources.PLAIN_OBJECT_FIELDS and not conflicts and not partial_refs):
                paths = {records[0]['path'], semantic.MENU, semantic.CLOTHING, sources.CONTEXT_MANAGER,
                         sources.CONTEXT_INVENTORY, sources.CONTEXT_LOADER, sources.CONTEXT_ELEMENT,
                         sources.CONTEXT_RADIO, sources.CONTEXT_MOVABLE, sources.CONTEXT_MEDIA,
                         sources.HOTBAR, sources.HOTBAR_SLOTS, sources.TUTORIAL_MENU, sources.LEGACY_RELOAD,
                         sources.PLACE_OBJECT, sources.DROP_OBJECT, sources.CAMP_FUEL, sources.CAMP_MENU,
                         sources.RADIO_MEDIA, sources.LEGACY_MEDIA_MENU}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_plain_object_dispatch'
                applied['direct_scope'] = {
                    'definition': 'Direct asks about functions/state changes not captured by other activity/native questions; it does not ask whether the object has any purpose in the entire game.',
                    'declaration': fields,
                    'selected_dispatch': 'The exact Normal declaration is neither the selected Food/Literature/Clothing/Weapon/Container/Map/Radio/AlarmClock class nor any named key, generator, corpse, battery/charger, towel or Pills prefix branch. It has no water replacement, bandage, dye, makeup, activation, remote, magazine/ammo or extra-form capability field.',
                    'delegated_dispatch': 'ClothingRecipesDefinitions has only Sheet and Clothing fabric routes. Legacy reload registration lists firearm/clip types, not these exact objects. Tutorial inventory entries require DeadMouse, HandWeapon, InventoryContainer or Clothing. The registered inventory elements are Radio, Movable and Media; these exact plain Normal fields select none of their item-specific operations.',
                    'shared_operations': 'WorldStaticModel admits the ordinary 3D-placement menu: the cursor transfers and unequips items, then queues ISDropWorldItemAction with position/rotation. This is the approved general drop/positioning management, not a unique decoration effect. Hotbar attachment requires AttachmentType, absent here. Favorites, holding, moving, dropping and debug/admin mutation are excluded.',
                    'activity_boundaries': 'Recipe/evolved-recipe and fixing menus remain in the independently attributed crafting/cooking/world-work scopes. Campfire type registries have no exact entry for these objects and category fallbacks are Clothing/Literature, not Normal; DisplayCategory=Junk/animal labels do not change that category predicate.',
                    'scope_limit': 'This closes the examined bound residual dispatch scope, not future extensions, hypothetical mods, acquisition, or all possible uses.'}
                if item in sources.PLAIN_OBJECT_LABELS:
                    applied['direct_scope']['family_comparison'] = 'Sports/game pieces have no Weapon or game-action fields; toiletries have no dye/makeup/medical or washing-supply selection; tableware has no food, container capacity or water-replacement fields; stationery has no writer tag or writable field; wallets have no storage capacity. The actual common menu and registered contexts therefore supply no item-specific direct action for these exact declarations. Names alone are not dispatch predicates.'
                work = None
                if item in {'Base.Disc', 'Base.VHS'}:
                    applied['direct_scope']['media'] = 'These generic declarations have no MediaCategory. The old world-media body is entirely commented out. Active RWMMedia drag/drop uses isRecordedMedia/getMediaType; joypad lookup explicitly selects Disc_Retail/VHS_Retail/VHS_Home. Their names/icons cannot supply a recording.'
                    residual = {'meaning': ('Whether this generic media form has an assigned playable/readable recording' if axis == 'operation' else
                                           'Recorded-media assignment and type compatibility for this generic form'),
                                'required_input': 'Native recorded-media index/assignment and isRecordedMedia/getMediaType for ' + item,
                                'reason': 'The exact generic declaration and actual active/inactive media consumers are distinguished. Local joypad lookup excludes these exact forms, while drag/drop and label reading depend on native recorded-media state not established by their declaration. Retail/home siblings are not aliases.',
                                'boundary_kind': 'examined_native_dependency'}
                else:
                    terminal_reason = ('No item-specific direct operation is selected for this exact plain object by the bound dispatch and delegated predicates after excluding general inventory management. Other activity questions remain independent.' if axis == 'operation' else
                                       'Within the same bound direct scope, the exact plain object has no applicable item-specific operation whose eligibility or meaning-changing prerequisite needs a conditions answer. This follows the examined operation applicability, not its predecessor text disposition; conditions of excluded general management and other activities are outside this key.')
                    result.update(state='evidence_backed_not_applicable', fact_refs=[], scope_complete=True,
                                  negative_scope=list(key), exclusion_predicate=terminal_reason,
                                  closed_source_refs=sorted(paths))
            elif item in base.get('item_map_sources', {}):
                paths = {semantic.MENU, sources.MAP_VIEW, sources.MAP_SYMBOLS, sources.MAP_TEXT,
                         sources.MAP_DEFINITIONS, sources.CONTEXT_MEDIA}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'item_map_view_annotations_and_knowledge'
                applied['direct_scope'] = {
                    'binding': base['item_map_sources'][item],
                    'view': 'Transfer precedes opening when needed; continued inventory possession controls window lifetime. Pan, zoom and reset operate the viewer. Missing initialization logs and returns without preventing window creation.',
                    'annotations': 'The item-bound symbols API receives add-text/add-texture, removal and edit/move operations. The actual editor checks Pen/Pencil/RedPen/BluePen tag or type; edit/move additionally needs an eraser. Text confirmation trims and rejects empty content.',
                    'knowledge': 'ISMap first update initializes by native getMapID and then calls revealKnownArea. Named callbacks set exact town or Louisville grid bounds; setKnownInSquares receives those bounds. This does not mark physical visitation or compute routes.',
                    'stash': 'onCheckMap invokes map:doBuildingStash after viewer creation; the supplied Lua does not implement that native stash operation.',
                    'other_entries': 'Selected maps also support the represented name dialog. Their exact declarations contain no other food, wearable, weapon, power, radio or recorded-media capability. Ordinary inventory management remains outside scope.'}
                work = None
                residual = {'meaning': ('Native map binding, map-data rendering and any assigned building-stash behavior' if axis == 'operation' else
                                       'Runtime MapID/content binding and building-stash execution prerequisites'),
                            'required_input': 'MapItem.getMapID and doBuildingStash; UIWorldMap data rendering/symbol persistence and WorldMapVisited storage' + ('; initialization of generic Map without a declared Map token' if not fields.get('Map') else ''),
                            'reason': 'Available viewer, annotation and named initialization consumers are interpreted through their calls and state assignments. The remaining native binding, persistence and stash execution are specific dependencies; current possession or implement availability is already expressed as a condition.',
                            'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Dirtbag', 'Base.Gravelbag', 'Base.Sandbag'} and fields.get('Type') == 'Drainable'
                    and not conflicts and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'UseWhileEquipped', 'UseDelta',
                        'DisplayName', 'Icon', 'ReplaceOnDeplete', 'ReplaceInSecondHand', 'ReplaceInPrimaryHand', 'WorldStaticModel', 'Tooltip'}
                    and fields.get('UseWhileEquipped', '').lower() == 'false'
                    and fields.get('ReplaceOnDeplete') == 'EmptySandbag'
                    and {'fill_ground_bag', 'pour_ground_cover', 'extinguish_fire', 'consolidate_drainable_supplies'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.WORLD_MENU, sources.GROUND_MENU, sources.GROUND_CURSOR, sources.SHOVEL_GROUND,
                         sources.NATURAL_FLOOR, sources.OBJECT_COMMANDS, sources.FIRE_FIGHTING, sources.EXTINGUISH_CURSOR,
                         sources.PUT_OUT_FIRE, sources.CONSOLIDATE, semantic.BUILD_OBJECT, semantic.BUILD_ACTION}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'ground_bag_fill_pour_extinguish_consolidate'
                applied['direct_scope'] = {'ground': base['ground_bag_relations'][item],
                    'pour': 'Exact type selection and existing-floor, plant/water/same-type exclusions precede addFloor, restoration metadata and Use; there is no extra shovel or remaining-use guard.',
                    'fire': 'The actual one-use supply branch, cursor visibility/selection and per-affected-square action are represented.',
                    'consolidation': 'Conditional canConsolidate and same-type receiver lookup lead to progressive fractional transfer, not an unconditional merge.',
                    'other_entries': 'These exact declarations have no activation, Food/Clothing/Weapon, recorded-media, container capacity or water-source capability. Construction materials retain their independent world-work roles.'}
                work = None
                residual = {'meaning': 'Native ground/item transformation and fire/depletion outcomes' if axis == 'operation' else 'Native capacity, consolidation eligibility and exact object-result prerequisites',
                    'required_input': 'InventoryItem used-delta/canConsolidate/Use and EmptySandbag replacement; Inventory.AddItem, square.addFloor and StopBurning/stopFire outcomes for the bound calls',
                    'reason': 'All selected ground, extinguishing and consolidation Lua consumers for these exact declarations are represented with their actual guards. Local inventory change and server terrain change are not treated as atomic, and native results remain individually bounded.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Rope', 'Base.SheetRope'} and fields.get('Type') == 'Normal' and fields.get('Tags') == 'Rope'
                    and not conflicts and set(fields) <= {'Type', 'DisplayCategory', 'DisplayName', 'Weight', 'Icon',
                        'WorldStaticModel', 'SurvivalGear', 'Tags', 'Tooltip'}
                    and {'supply_escape_rope', 'remove_installed_escape_rope', 'start_escape_rope_ascent'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.WORLD_MENU, sources.ADD_ROPE, sources.REMOVE_ROPE,
                         sources.CLIMB_ROPE, sources.OBJECT_COMMANDS, semantic.GROUPS, semantic.CLOTHING}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'escape_rope_consumers'
                applied['direct_scope'] = {
                    'declaration': {k: fields.get(k) for k in ('Type', 'Tags', 'SurvivalGear', 'Tooltip')},
                    'installation': 'Actual above-ground window/frame/hoppable admission, window barricade exclusion, nails, one sufficient rope type and adjacent transfer. SheetRope has priority; counts are not mixed. Timed validity rechecks attachment eligibility and either rope count, not nails. Server accepts the actual window/thumpable/frame/hoppable object and calls native addSheetRope with selected type.',
                    'removal': 'Current haveSheetRope and adjacent approach feed a separate interruptible action; the server checks index/type before native removeSheetRope. Return count, condition and form are not inferred.',
                    'climbing': 'The world menu selects down=false after canClimbSheetRope and Strength>=0, walks to the square and rechecks there before native ascent. The action defines a down branch but the supplied menu does not invoke it; traversal, descent entry and fall/rope state belong to the named native remainder.',
                    'other_consumers': 'The Rope tag is used by the recipe group; log-binding/output callbacks and exact construction participation remain on their independent crafting/world-work/acquisition questions. These plain Normal declarations do not dispatch the food, wearable, weapon, radio/media, light activation or health branches. Ordinary inventory handling is outside the adopted direct scope.'}
                work = None
                residual = {'meaning': ('Native rope attachment, return and installed traversal' if axis == 'operation' else
                                       'Exact native rope counts, attachment eligibility and installed traversal prerequisites'),
                            'required_input': 'Window/IsoWindowFrame/hoppable countAddSheetRope, addSheetRope/removeSheetRope consumption and returned form; character installed-rope ascent/descent execution',
                            'reason': 'The local menu, transfer, timed guards, type selection and server dispatch are interpreted with their actual asymmetries. Native attachment/count/return and traversal execution remain exact dependencies; current supplies or rope presence are represented conditions, not generic blockers.',
                            'boundary_kind': 'examined_native_dependency'}
            elif (fields.get('Type') == 'Moveable' and fields.get('WorldObjectSprite') and not conflicts
                    and (not fields.get('Tags') or (item in sources.BROKEN_GLASS_ITEMS and fields.get('Tags') == 'BrokenGlass'
                         and any(f['item_id'] == item and f['payload'] == {'function': 'pickup_floor_glass'} for f in facts.values())))
                    and set(fields) <= {'Type', 'DisplayCategory', 'DisplayName', 'Weight', 'Icon', 'WorldObjectSprite', 'Tags'}
                    and {'place_moveable_furniture', 'remove_placed_furniture'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.CONTEXT_MOVABLE, sources.MOVE_CURSOR, semantic.PROPS,
                         semantic.MOVE, semantic.MOVE_ACTION, sources.OBJECT_COMMANDS}
                if item in sources.BROKEN_GLASS_ITEMS:
                    paths.update({sources.WORLD_MENU, sources.PICKUP_GLASS, sources.WINDOW_GLASS, sources.MOVE_TOOLS, semantic.GROUPS})
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'moveable_sprite_consumers'
                applied['direct_scope'] = {
                    'declared_sprite': fields['WorldObjectSprite'],
                    'inventory_entry': 'ContextMovable requires the exact context inventory and neither hand holding the item, then opens place mode and tries that item. Radio uses its separate registered handler; these exact declarations are plain Moveable without radio/media, food, wearable or weapon fields.',
                    'property_read': 'ISMoveableSpriteProps.new calls getSprite(exact WorldObjectSprite) and reads IsMoveAble, IsoType, MoveType, Facing/faces, grid, Material, CanScrap, tools/skills, CustomItem and placement properties. Type=Moveable alone does not supply those values.',
                    'represented': 'Conditional sprite placement and pickup retain complete parts, contents, capacity, support, water/fire/window, tool/skill, reach, permissions and breakage limits. Neither returning an intact item nor returning the original item type is guaranteed.',
                    'rotation': 'Cursor selects declared sprite faces or the IsoMannequin direction branch. canRotateMoveable checks movable/faces/type, empty containers, complete multi-sprite grids, tabletops, separating walls and newly occupied placement squares. Perform either replaces sprites/rebuilds the grid or sends object.rotate; the server direction command accepts only IsoMannequin. No exact sprite rotation is asserted without its native properties.',
                    'scrapping': 'CanScrap and valid material select the exact scrap definition. Checks cover complete grids, empty containers, table support, barricades, occupied door/window frames, protected stair-top floors and water collectors. Required tools and optional skill chance remain separate. Completion removes the object (or changes ground floor), uses custom dismantling recipes where present, otherwise material/modData need: returns, and can use a blowtorch. No fixed yield or scrap capability is inferred for an unbound sprite.',
                    'action_conditions': 'Place/pickup/rotate/scrap require the same floor, reachable square within 1.6 on each axis and safehouse permission; scrapping additionally verifies that the object still exists. Walking/running interrupts.',
                    'installed_type': 'placeMoveableInternal dispatches from native sprite/object properties to containers, mannequins, radios/TV, stove/fireplace, jukebox/multimedia, lighting, doors/windows or generic objects. The specific installed appliance, storage, resting or display function requires that exact binding; the inventory display name is not used as its proof.',
                    'independence': 'Predecessor layout/taxonomy adjudication and crafting/world-work roles are separate. Generic Moveable without a declared sprite is excluded; exact BrokenGlass forms require their additional consumer below.'}
                if item in sources.BROKEN_GLASS_ITEMS:
                    applied['direct_scope']['floor_glass'] = {
                        'selection': 'The world menu selects IsoBrokenGlass and walks adjacent. The glove/fingerless restrictions in the menu are commented out. ISPickupBrokenGlass.isValid returns true; walking/running interrupts.',
                        'pickup': 'Movable sprite and successful instanceItem are required. The dedicated action forces pickup, bypassing normal pickup eligibility/break checks; the actual IsoBrokenGlass branch can scratch a random hand when hands clothing is absent (ZombRand(3)==0), and embed glass in the same hand on its nested ZombRand(5)==0. These conditional setters are represented.',
                        'other_paths': 'Inventory placement remains sprite-bound; the constructor dispatches IsoBrokenGlass from IsoType. Recipe.GetItemTypes.BrokenGlass uses the exact tag and is not by itself a use. Window-frame removal has its own smashed/not-glass-removed guard and native window:removeBrokenGlass call, not this inventory shard use.',
                        'remaining': 'Exact sprite/placed-object and returned-item binding remain native. Pickup hand injury does not establish injury from merely approaching or stepping on the placed glass.'}
                work = None
                residual = {'meaning': ('Exact sprite capability and installed-object behavior' if axis == 'operation' else
                                       'Exact sprite-dependent placement, rotation, scrapping and installed-object prerequisites'),
                            'required_input': 'getSprite(' + fields['WorldObjectSprite'] + ') property/grid/face and IsoType binding; native Moveable/placed-object construction and corresponding object executor',
                            'reason': 'The finite selected inventory and four moveable cursor routes have been interpreted through their real consumers. The exact declared sprite is read by a native property API and supplies the still-unbound capability/type selection. This is a concrete missing sprite binding, not a claim that variable world state or a hypothetical extension prevents answering the represented conditional placement/pickup functions.',
                            'boundary_kind': 'examined_native_dependency'}
                if item in sources.BROKEN_GLASS_ITEMS:
                    residual['required_input'] += '; native contact/foot-injury execution for the placed IsoBrokenGlass form'
            elif (item in sources.PILL_ITEMS and fields.get('Type') == 'Drainable' and not conflicts
                    and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'UseDelta', 'UseWhileEquipped', 'DisplayName',
                        'Icon', 'Tooltip', 'StaticModel', 'WorldStaticModel', 'Medical', 'FatigueChange'}
                    and {'take_pills', 'consolidate_drainable_supplies'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, semantic.PILLS, sources.CONSOLIDATE}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'pill_taking_and_consolidation'
                applied['direct_scope'] = {'declaration': fields, 'taking': sources.PILL_TAKING,
                    'consolidation': sources.MEDICAL_CONSOLIDATION,
                    'other_consumers': 'These five drainables have no BandagePower, AlcoholPower, CanStoreWater, activation, firearm, food, clothing, media or storage capability. UseWhileEquipped is false. Medical and display labels do not select an extra health-panel treatment; FatigueChange is not interpreted by the Lua pill action.'}
                work = None
                residual = {'meaning': 'Exact native medication effects, timing and depletion',
                    'required_input': 'BodyDamage.JustTookPill for this FullType including fatigue, pain, panic, unhappiness, sleep, delayed action and consumption; canConsolidate/same-type lookup/Use semantics',
                    'reason': 'The actual selected-pill action and progressive consolidation are represented with guards and interruptions. Claimed medicinal effects and onset are owned by the named native call, not inferred from display names or the vitamin FatigueChange sign.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.BANDAGE_ITEMS and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= {'DisplayCategory', 'CanBandage', 'Weight', 'AlwaysWelcomeGift', 'Alcoholic', 'Type',
                        'DisplayName', 'ReplaceOnUse', 'Icon', 'BandagePower', 'Tooltip', 'FabricType', 'WorldStaticModel', 'Count', 'Medical'}
                    and {'apply_bandage', 'remove_applied_bandage'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                if ((float(fields['BandagePower']) < 2 or 'clean_burn' in functions)
                        and ('Dirty' not in item or 'wash_bandaging_material' in functions)
                        and (item != 'Base.RippedSheets' or {'apply_splint', 'remove_applied_splint'} <= functions)):
                    paths = {semantic.MENU, sources.HEALTH, semantic.BANDAGE, sources.CLEAN_BURN, sources.SPLINT,
                             sources.WORLD_MENU, sources.CLEAN_BANDAGE, sources.TAKE_WATER, sources.OBJECT_COMMANDS,
                             sources.GARMENT_UI, sources.PATCH_GARMENT, sources.REMOVE_PATCH, semantic.CLOTHING,
                             sources.CAMP_FUEL, sources.CAMP_MENU, sources.CAMP_ADD, sources.CAMP_LIGHT,
                             sources.CAMP_CLIENT, sources.CAMP_SERVER, sources.CAMP_COMMANDS, sources.CAMP_OBJECT}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'bandage_treatment_and_cleaning'
                    applied['direct_scope'] = {'declaration': fields,
                        'application': sources.BANDAGE_APPLICATION, 'removal': sources.BANDAGE_REMOVAL,
                        'life_and_infection': [sources.BANDAGE_LIFE, sources.BANDAGE_INFECTION],
                        'burn_cleaning': sources.BURN_CLEANING if float(fields['BandagePower']) >= 2 else 'BandagePower below two fails the burn-cleaning material selector.',
                        'washing': base.get('bandage_washing_results', {}).get(item),
                        'splinting': [sources.SPLINTING, sources.SPLINT_REMOVAL] if item == 'Base.RippedSheets' else 'Not an exact RippedSheets support binder.',
                        'other_consumers': 'Exact clean fabric patch supplies and registered campfire fuel/tinder entries retain their own interpreted conditions. Dirty names do not supply FabricType or infection evidence. These plain Normal forms have no water storage, activation, food, clothing, device, firearm, media or container dispatch. Cleaning/sterilization recipes retain their independent crafting/acquisition questions.'}
                    work = None
                    residual = {'meaning': 'Native bandage/healing state and replacement interpretation',
                        'required_input': 'BandagePower/isAlcoholic/isInfected getter binding and BodyDamage.SetBandaged/body-part state evolution; returned recorded bandage type and depleted Use; dirty-to-clean result factory and water debit where applicable; garment material restoration and registered campfire native state',
                        'reason': 'Both distinct application menus, removal, actual life/panic/infection setters, eligible burn cleaning and exact dirty-material washing are interpreted. Native healing and replacement are separate from the represented local state assignments; neither Dirty nor Alcoholic names prove efficacy.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.' + name for name in ('223Box', '308Box', '556Box', 'Bullets38Box', 'Bullets44Box',
                        'Bullets45Box', 'Bullets9mmBox', 'ShotgunShellsBox', 'NailsBox', 'ScrewsBox', 'PaperclipBox', 'BoxOfJars')}
                    and fields.get('Type') == 'Normal' and set(conflicts) <= {'DisplayCategory'}
                    and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'DisplayName', 'Icon', 'WorldStaticModel',
                        'MetalValue', 'AlwaysWelcomeGift', 'SurvivalGear', 'PlaceOneSound', 'PlaceMultipleSound'}
                    and base.get('package_opening_results', {}).get(item)
                    and all(not r['ammunition_receivers'] for r in base['package_opening_results'][item])):
                openings = base['package_opening_results'][item]
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.FIREARM, sources.LOAD_MAGAZINE,
                         sources.PLACE_OBJECT, sources.DROP_OBJECT, sources.LEGACY_RELOAD,
                         *(r['path'] for r in openings), *(p for r in openings for p in r['receiver_source_paths'])}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_box_opening_and_ammunition_selection'
                applied['direct_scope'] = {'declaration': fields, 'conflicts': conflicts, 'opening': openings,
                    'ammunition': 'DisplayCategory Ammo can select a box as the ammunition-menu argument, but a receiver requires AmmoType equal to that exact box FullType. The bound declaration inventory supplies no such receiver. A box is not a loose round merely because of its category or contents.',
                    'other_dispatch': 'These exact Normal fields select no magazine capacity, weapon attack, activation, water storage, health, wearable, container or media operation. Placing and gift labels remain general management or metadata. MetalValue is a native property boundary, not an inferred local melting function.',
                    'packing': 'Independent packing recipes do not imply a reversible opening process. In particular NailsBox opening declares Nails=20, whereas packing consumes Nails=100.',
                    'scope': 'Recipe participation retains its separate questions. BoxOfJars repeated DisplayCategory values do not affect its exact recipe identity; category precedence is retained as a native binding uncertainty.'}
                work = None
                residual = {'meaning': 'Exact native recipe result delivery, callback creation and box property binding',
                    'required_input': 'RecipeManager eligibility, consumption and declared result/count delivery; InventoryItemFactory/AddItems creation; MetalValue property interpretation' + ('; repeated DisplayCategory loader precedence' if conflicts else ''),
                    'reason': 'The complete opening recipe and called callback are interpreted, including extra jar lids and the absence of a matching boxed-ammunition receiver in the bound declarations. Native result creation and property interpretation remain separate from those local functions.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= {'DisplayCategory', 'Type', 'DisplayName', 'Icon', 'Weight', 'SurvivalGear', 'WorldStaticModel'}
                    and (item in base.get('seed_sources', {}) or any(
                        r['result_item'] in base.get('seed_sources', {}) for r in base.get('package_opening_results', {}).get(item, [])))):
                loose = item in base['seed_sources']
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.FARM_MENU, sources.SEED_ACTION,
                         sources.FARM_CLIENT, sources.FARM_SYSTEM, sources.FARM_COMMANDS, sources.PLANT, sources.SEED_DEFINITIONS}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'configured_crop_seed_and_packet'
                applied['direct_scope'] = {'declaration': fields, 'loose_seed': base['seed_sources'].get(item),
                    'packet': base.get('package_opening_results', {}).get(item, []), 'sowing': sources.SOWING,
                    'packing': sources.SEED_PACKING if loose else 'The unopened packet must first yield its configured loose seed form before the sowing path applies.',
                    'other_dispatch': 'Exact Normal gardening declarations select neither Food eating nor medication, wearable, weapon, water, activation or media operations. Seed names are matched to the actual crop seedName registry; display labels alone do not establish a species. Crafting roles and seed-packet production retain separate questions.'}
                work = None
                residual = {'meaning': 'Native loose-seed/packet item creation, consumption and persistent planted-state binding',
                    'required_input': 'RecipeManager packet result identity/count, configured seed inventory lookup/removal, farming command delivery and persistent plant object state',
                    'reason': 'Configured crop counts, exact packet opening and reverse seed packing, local sowing possession checks and server still-plowed guard are represented. Consumption preceding server rejection is not hidden by a guarantee of planting, growth or harvest.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item == 'Base.Fertilizer' and not conflicts and fields.get('Type') == 'Drainable'
                    and set(fields) <= {'DisplayCategory', 'Type', 'DisplayName', 'Icon', 'Weight', 'UseDelta',
                        'UseWhileEquipped', 'Tooltip', 'WeightEmpty', 'WorldStaticModel'}
                    and any(f['item_id'] == item and f['payload'] == {'function': 'apply_fertilizer'} for f in facts.values())):
                paths = {semantic.MENU, sources.FARM_MENU, sources.FERTILIZE_ACTION, sources.FARM_CLIENT,
                         sources.FARM_SYSTEM, sources.FARM_COMMANDS, sources.PLANT, sources.CONSOLIDATE}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'fertilizer_application_and_consolidation'
                applied['direct_scope'] = {'declaration': fields, 'application': sources.FERTILIZING,
                    'growth': sources.FERTILIZER_GROWTH, 'rot': sources.FERTILIZER_ROT,
                    'consolidation': sources.MEDICAL_CONSOLIDATION,
                    'other_dispatch': 'No water source/replacement, activation, wearable, weapon, wound medication or media field is declared. FertilizerEmpty removal in the action does not establish a returned empty package; WeightEmpty is not ReplaceOnDeplete. Compost collection belongs to the separate CompostBag form.'}
                work = None
                residual = {'meaning': 'Native fertilizer depletion, consolidation and planted-state persistence',
                    'required_input': 'Drainable Use/WeightEmpty/default depleted behavior, inventory Remove(string) and canConsolidate; farming persistent object and command delivery',
                    'reason': 'Available application, counter/schedule/rot setters and consolidation are interpreted. Existing application count is a represented outcome condition rather than a local-work blocker, and empty-package return is not inferred.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Paintbrush', 'Base.Mop', 'Base.Splint'} and fields.get('Type') == 'Normal'
                    and not conflicts and set(fields) <= sources.PLAIN_OBJECT_FIELDS | {'StaticModel', 'Tooltip', 'MetalValue', 'Medical'}
                    and {'Base.Paintbrush': {'paint_supported_surface', 'paint_wall_sign'}, 'Base.Mop': {'clean_world_blood'},
                         'Base.Splint': {'apply_splint', 'remove_applied_splint'}}[item] <= {
                             f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.WORLD_MENU, sources.PAINT_MENU, sources.PAINT_CURSOR,
                         sources.PAINT_ACTION, sources.SIGN_ACTION, sources.CLEAN_CURSOR, sources.CLEAN_BLOOD,
                         sources.HEALTH, sources.SPLINT, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_plain_work_tool_consumers'
                applied['direct_scope'] = {'declaration': fields, 'consumer': {
                    'Base.Paintbrush': [sources.PAINT_ACTIONS], 'Base.Mop': [sources.BLOOD_CLEANING],
                    'Base.Splint': [sources.SPLINTING, sources.SPLINT_REMOVAL]}[item],
                    'selection': 'The exact named consumer supplies the only item-specific action in these complete plain fields. The paintbrush and mop are not consumed by their actions; the finished splint is consumed on application, and removal returns the recorded support type subject to native creation. Recipe/construction roles and ordinary inventory handling remain independent.'}
                work = None
                residual = {'meaning': 'Native selected surface/body state persistence and consumed/returned item binding',
                    'required_input': {'Base.Paintbrush': 'Exact surface mapping and sprite/color persistence',
                        'Base.Mop': 'Bleach Use semantics and square blood persistence/synchronization',
                        'Base.Splint': 'Fracture healing, splint factor persistence and recorded support item construction'}[item],
                    'reason': 'Actual menu/cursor/action guards, timing, interruption, state mutation and consumption are interpreted. The remaining outcome is the specific native executor boundary rather than an unimplemented local branch.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.LogStacks2', 'Base.LogStacks3', 'Base.LogStacks4', 'Base.Frog', 'Base.BrokenFishingNet'}
                    and fields.get('Type') == 'Normal' and not conflicts and set(fields) <= sources.PLAIN_OBJECT_FIELDS
                    and any(f['item_id'] == item and f['payload'].get('function') in {
                        'unbundle_logs', 'prepare_frog_meat', 'process_broken_fish_net'} for f in facts.values())):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.WORLD_MENU,
                         sources.CAMP_MENU, sources.CAMP_FUEL, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_plain_form_preparation'
                applied['direct_scope'] = {'declaration': fields,
                    'transformation': sources.LOG_BINDING if item.startswith('Base.LogStacks') else
                                      sources.FROG_PREPARATION if item == 'Base.Frog' else sources.WIRE_RECOVERY,
                    'dispatch': 'The exact plain Normal form has no additional native food, water/storage, weapon, wearable, radio/media, activation or treatment field. Recipe transformation is represented with its exact input; the resulting item function is not transferred back to this form. General inventory management remains excluded.'}
                work = None
                residual = {'meaning': 'Native exact recipe eligibility, input consumption and result delivery',
                    'required_input': 'RecipeManager result/parser execution and inventory factory; supplied-item order and stored rope metadata for log stacks; exact Result:Wire;3 interpretation for the broken net',
                    'reason': 'Available complete recipe declarations, action validity and actual callbacks are interpreted. The result/item runtime boundary remains, including the unnormalized broken-net result spelling; it does not hide available local callback work.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.MATERIAL_OBJECT_ITEMS and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.MATERIAL_OBJECT_FIELDS and not partial_refs):
                paths = {semantic.MENU, sources.WORLD_MENU, semantic.CLOTHING, semantic.GROUPS, semantic.CRAFT,
                         sources.HEALTH, sources.CLOCK_CHARACTER, sources.CAMP_MENU, sources.CAMP_FUEL,
                         sources.HOTBAR, sources.HOTBAR_SLOTS, sources.LEGACY_RELOAD, sources.TUTORIAL_MENU,
                         sources.PLACE_OBJECT, sources.DROP_OBJECT, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_plain_material_and_legacy_forms'
                applied['direct_scope'] = {'declaration': fields,
                    'inventory': 'Complete Normal fields provide no body location, storage capacity, Food class, water/replacement capability, radio device class, activation, weapon, remote trigger, medical power or selected grooming/washing type. Optional metal/color/display/obsolete/count fields do not supply those consumers.',
                    'exact_forms': 'Belt and obsolete jewelry/underwear are not their Clothing siblings; DigitalWatch is not DigitalWatch2 or wrist watches. Radio is not a Type Radio device. Soap/CleaningLiquid are not Soap2/CleaningLiquid2. Umbrella is not a typed folding weapon. WaterDish and empty cans lack CanStoreWater and capacity. Mold, sensor, receiver and timer part names are not installed-device operation predicates.',
                    'activities': 'Exact recipe assembly, baking, jarring, log/material and smithing participants and carpentry/welding/fixing supplies retain separate activity questions. No standalone direct action is added from being an input or output. The inspected campfire registry has no entry for these exact forms; ordinary holding, model placement, sorting and discarding are excluded.',
                    'limits': 'Applicability is limited to these exact bound declarations and dispatch. OBSOLETE is not itself evidence that an action is absent or that the item cannot exist; native availability remains independent.'}
                work = None
                terminal_reason = ('No item-specific direct operation remains applicable to this exact plain Normal form after the selected and delegated dispatch and independent activity boundary are interpreted.' if axis == 'operation' else
                                   'The exact plain Normal form has no applicable item-specific direct operation in the examined scope; conditions of independent recipe/construction activities and ordinary inventory management are not transferred into this key.')
                result.update(state='evidence_backed_not_applicable', fact_refs=[], scope_complete=True,
                              negative_scope=list(key), exclusion_predicate=terminal_reason, closed_source_refs=sorted(paths))
            elif (item in {'Base.CottonBalls', 'Base.Plantain', 'Base.Comfrey', 'Base.WildGarlic', 'Base.Hairspray'}
                    and not conflicts and fields.get('Type') == 'Normal'
                    and set(fields) <= sources.PLAIN_OBJECT_FIELDS | {'Tooltip', 'Medical'} and not partial_refs):
                paths = {semantic.MENU, sources.WORLD_MENU, sources.HEALTH, sources.DISINFECT,
                         sources.CLOCK_CHARACTER, sources.HAIR_CUT, sources.MAKEUP_UI, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_plain_plant_cotton_aerosol_dispatch'
                applied['direct_scope'] = {'declaration': fields,
                    'selection': 'CottonBalls is not AlcoholWipes; the health panel does not select these Normal raw herbs as poultices or disinfectants. WildGarlic is distinct from the Food declaration WildGarlic2. Hairspray has no HairDye/MakeUpType or active grooming type predicate; its trap tooltip does not add a direct action. Complete plain fields select no water, power, radio, weapon or wearable branch. Recipe inputs remain separate crafting questions.'}
                work = None
                terminal_reason = ('No item-specific direct operation is selected for this exact Normal form within the examined inventory, health, grooming and registered context dispatch.' if axis == 'operation' else
                                   'The independently examined operation applicability supplies no item-specific direct operation whose prerequisites would apply to this exact Normal form; recipe conditions remain separate.')
                result.update(state='evidence_backed_not_applicable', fact_refs=[], scope_complete=True,
                              negative_scope=list(key), exclusion_predicate=terminal_reason, closed_source_refs=sorted(paths))
            elif (not conflicts and fields.get('Type') in {'Normal', 'Drainable'}
                    and set(fields) <= sources.PLAIN_OBJECT_FIELDS | {'MetalValue', 'SurvivalGear', 'Medical', 'Tags',
                        'Tooltip', 'StaticModel', 'UseDelta', 'UseWhileEquipped', 'ConsolidateOption'}
                    and item in {'Base.Needle', 'Base.Thread', 'Base.SutureNeedle', 'Base.SutureNeedleHolder',
                                 'Base.Tweezers', 'Base.PlantainCataplasm', 'Base.ComfreyCataplasm', 'Base.WildGarlicCataplasm'}):
                required = {'Base.Needle': {'stitch_wound', 'apply_garment_patch', 'unpick_garment_patch'},
                            'Base.Thread': {'stitch_wound', 'apply_garment_patch', 'consolidate_drainable_supplies'},
                            'Base.SutureNeedle': {'stitch_wound'},
                            'Base.SutureNeedleHolder': {'assist_stitching', 'remove_embedded_glass', 'remove_embedded_bullet'},
                            'Base.Tweezers': {'remove_embedded_glass', 'remove_embedded_bullet'}}.get(item, {'apply_poultice'})
                if required <= {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}:
                    paths = {semantic.MENU, sources.HEALTH, sources.STITCH, sources.REMOVE_GLASS,
                             sources.REMOVE_BULLET, *sources.POULTICES.values(), sources.GARMENT_UI,
                             sources.PATCH_GARMENT, sources.REMOVE_PATCH, semantic.CLOTHING, sources.CONSOLIDATE}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_medical_and_sewing_consumers'
                    applied['direct_scope'] = {'declaration': fields, 'stitching': sources.STITCHING,
                        'holder': sources.SUTURE_ASSISTANCE, 'glass': sources.GLASS_REMOVAL,
                        'bullet': sources.BULLET_REMOVAL, 'poultice': sources.POULTICE_USE,
                        'sewing': [sources.GARMENT_PATCHING, sources.GARMENT_PATCH_REMOVAL],
                        'consolidation': sources.MEDICAL_CONSOLIDATION if item == 'Base.Thread' else None,
                        'scope': 'Only each exact selected tool or consumed material receives its applicable action. Ordinary inventory management and recipe participation are independent; names, Medical and SurvivalGear do not add an action.'}
                    work = None
                    residual = {'meaning': 'Native wound/factor evolution, garment patch outcome and item depletion',
                        'required_input': 'BodyPart stitched/factor/injury persistence and healing; addPatch/canFullyRestore and patch return mapping where sewing applies; Use/canConsolidate and multiplayer command delivery',
                        'reason': 'The complete selected Lua actions, actual possession asymmetries, random/XP/pain/panic branches and sewing supply consumption are represented. Exact downstream wound healing and item construction remain native dependencies.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (not conflicts and fields.get('Type') in {'Normal', 'Drainable'}
                    and set(fields) <= sources.PLAIN_OBJECT_FIELDS | {'MetalValue', 'StaticModel', 'Tags', 'UseDelta',
                        'UseWhileEquipped', 'HairDye', 'ColorRed', 'ColorGreen', 'ColorBlue', 'MakeUpType'}
                    and (fields.get('HairDye', '').lower() == 'true' or item in {'Base.Hairgel', 'Base.Razor',
                        'Base.Mirror', 'Base.MakeupEyeshadow', 'Base.MakeupFoundation', 'Base.Lipstick'})):
                required = ({'dye_hair_or_beard', 'consolidate_drainable_supplies'} if fields.get('HairDye', '').lower() == 'true' else
                            {'Base.Hairgel': {'groom_hair', 'consolidate_drainable_supplies'},
                             'Base.Razor': {'groom_hair', 'groom_beard'}, 'Base.Mirror': {'support_makeup_mirror'},
                             'Base.MakeupEyeshadow': {'apply_eye_makeup', 'remove_registered_makeup'},
                             'Base.MakeupFoundation': {'apply_makeup', 'remove_registered_makeup'},
                             'Base.Lipstick': {'apply_lip_makeup', 'remove_registered_makeup'}}[item])
                if required <= {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}:
                    paths = {semantic.MENU, semantic.DYE, sources.CLOCK_CHARACTER, sources.HAIR_CUT,
                             sources.BEARD_TRIM, sources.MAKEUP_UI, sources.MAKEUP_DEFINITIONS,
                             sources.CONSOLIDATE, semantic.WEAR, sources.WORLD_MENU}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_appearance_consumers'
                    applied['direct_scope'] = {'declaration': fields, 'dye': sources.DYE_APPLICATION,
                        'hair': sources.HAIR_GROOMING, 'beard': sources.BEARD_GROOMING,
                        'makeup': sources.MAKEUP_LIFECYCLE, 'consolidation': sources.MEDICAL_CONSOLIDATION,
                        'scope': 'Only the exact HairDye, Razor, Hairgel, Mirror or MakeUpType selection applies. Recipe inputs and ordinary inventory handling remain separate. Cosmetic names do not establish physiological or protective effects.'}
                    work = None
                    residual = {'meaning': 'Native style, cosmetic item, color and visual binding or depletion',
                        'required_input': 'Exact hair/beard style registry, dye RGB getters and Use/canConsolidate, makeup factory/BodyLocation and model/visual synchronization as applicable',
                        'reason': 'Selected local menus, temporary worn preview, apply/remove behavior, time/interruption, missing continuous guards and style-specific consumption are interpreted. Actual native model/color rendering and item depletion remain separate.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (not conflicts and item in {'Base.BathTowel', 'Base.DishCloth', 'Base.BathTowelWet', 'Base.DishClothWet'}
                    and set(fields) <= sources.PLAIN_OBJECT_FIELDS | {'UseDelta', 'UseWhileEquipped', 'ReplaceOnDeplete',
                        'Tooltip', 'cantBeConsolided', 'Wet', 'WetCooldown', 'ItemWhenDry'}):
                wet = item.endswith('Wet')
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                if (wet and fields.get('Type') == 'Normal' and fields.get('Wet', '').lower() == 'true'
                        and fields.get('ItemWhenDry') == item[:-3]) or (
                        not wet and fields.get('Type') == 'Drainable' and fields.get('cantBeConsolided', '').lower() == 'true'
                        and {'dry_the_body', 'clean_world_blood'} <= functions):
                    paths = {semantic.MENU, sources.DRY_BODY, sources.WORLD_MENU, sources.CLEAN_CURSOR,
                             sources.CLEAN_BLOOD, sources.CONSOLIDATE, *base['inventory_context_sources']}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_dry_and_wet_towel_forms'
                    applied['direct_scope'] = {'declaration': fields, 'body': sources.BODY_DRYING,
                        'world_blood': sources.BLOOD_CLEANING,
                        'selection': 'The body and blood actions select dry BathTowel/DishCloth, never their Wet siblings. Drying spends towel uses; blood cleaning changes bleach only. Dry declarations disallow consolidation. Wet normal forms declare Wet/WetCooldown/ItemWhenDry for native processing, without a selected Lua dry-towel action. Recipes and generic inventory handling are independent.'}
                    work = None
                    residual = {'meaning': 'Native towel wet-state transition, timed drying and reusable output' if wet else 'Native body wetness and depleted towel replacement',
                        'required_input': 'InventoryItem Wet/WetCooldown/ItemWhenDry processing for this exact form; Drainable Use/ReplaceOnDeplete and BodyDamage.decreaseBodyWetness where selected',
                        'reason': 'Exact dry versus wet dispatch, tick schedule, final extra use, interruptions and bleach-only blood-cleaning consumption are interpreted. The declared wet-item processing has no supplied Lua executor; its resulting form and timing are bounded native dependencies.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item.startswith('Base.Paint') and fields.get('Type') == 'Drainable' and not conflicts
                    and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'ReplaceOnDeplete', 'UseWhileEquipped',
                        'UseDelta', 'DisplayName', 'Icon', 'Tooltip', 'StaticModel', 'WorldStaticModel'}
                    and {'paint_supported_surface', 'paint_wall_sign', 'dump_contents', 'consolidate_drainable_supplies'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.PAINT_MENU, sources.PAINT_CURSOR, sources.PAINT_ACTION,
                         sources.SIGN_ACTION, semantic.BUILD_OBJECT, sources.DUMP_CONTENTS, sources.CONSOLIDATE}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_paint_surface_sign_and_disposal'
                applied['direct_scope'] = {'declaration': fields, 'painting': sources.PAINT_ACTIONS,
                    'emptying': base.get('container_emptying_relations', {}).get(item),
                    'consolidation': sources.MEDICAL_CONSOLIDATION,
                    'other_dispatch': 'Exact registered paint names join the active paint cursor. These fields do not select water, personal hair dye/makeup, weapon, medicine, wearable, remote, light or media controls. Ordinary placement of the paint tin is general management. Paint labels do not establish protective durability.'}
                work = None
                residual = {'meaning': 'Native paint consumption/replacement, mapping and color/sprite persistence',
                    'required_input': 'Drainable Use and canConsolidate/type lookup, native wall/sprite mapping and color/overlay synchronization',
                    'reason': 'Surface painting, sign overlays, blood clearing, transfer, missing continuing validity checks, cheat exceptions, disposal and consolidation have source-bound local interpretations. Native remaining-use and replacement delivery remain distinct.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'camping.CampfireKit', 'camping.CampingTentKit', 'camping.CampingTent',
                           'camping.Flint', 'camping.SteelAndFlint', 'camping.TentPeg'}
                    and fields.get('Type') == 'Normal' and not conflicts and set(fields) <= sources.PLAIN_OBJECT_FIELDS):
                paths = {semantic.MENU, sources.WORLD_MENU, sources.CAMP_MENU, sources.CAMP_FUEL,
                         sources.CAMP_LIGHT, sources.CAMP_CLIENT, sources.CAMP_SERVER, sources.CAMP_COMMANDS,
                         sources.CAMP_OBJECT, semantic.BUILD_OBJECT, semantic.BUILD_ACTION,
                         *sources.CAMP_PLACEMENT_SOURCES, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_camping_item_dispatch'
                applied['direct_scope'] = {'declaration': fields,
                    'selection': 'The active camping menu selects CampfireKit and CampingTentKit; CampingTent, Flint, SteelAndFlint and TentPeg are not aliases. Actual light-fire paths select other igniters and tinder/fuel predicates, not a generic flint/tool display name. The strict Normal field set supplies no water, weapon, activation, media, medical, wearable or attachment capability. General inventory placement remains excluded; kit recipes have separate crafting questions.',
                    'installation': sources.CAMP_PLACEMENT,
                    'campfire': sources.CAMPFIRE_PLACEMENT,
                    'tent': sources.TENT_PLACEMENT, 'placed_tent_rest': sources.TENT_REST,
                    'destruction': 'Tent need fields describe random destruction returns and do not select loose TentPeg or Tarp as additional installation inputs.'}
                if item in {'camping.CampfireKit', 'camping.CampingTentKit'} and any(
                        f['item_id'] == item and f['payload'].get('function') in {'place_campfire', 'pitch_tent'} for f in facts.values()):
                    work = None
                    residual = {'meaning': 'Native camping placement, inventory lookup/removal and world persistence' +
                                ('; native sleep/endurance effects' if item == 'camping.CampingTentKit' else ''),
                        'required_input': 'Native grid/obstruction and item/object factories, Remove(type), command delivery and persistent object binding' +
                                          ('; updateEnduranceWhileSitting and sleeping event' if item == 'camping.CampingTentKit' else ''),
                        'reason': 'Actual cursor/build/zero-time/server and removal paths are interpreted, including missing continuing checks, held-stone-hammer wear, new-kit returns and partial two-cell placement. Local state prerequisites are represented, not deferred as investigation.',
                        'boundary_kind': 'examined_native_dependency'}
                elif not partial_refs:
                    work = None
                    terminal_reason = ('The exact inactive camping form has no item-specific direct operation selected by the reviewed common and camping consumers; display-name resemblance is not an active alias.' if axis == 'operation' else
                                       'Within the same reviewed direct scope no applicable item-specific operation selects this exact inactive camping form, so it has no corresponding direct-operation prerequisites. Independent crafting roles remain separate.')
                    result.update(state='evidence_backed_not_applicable', fact_refs=[], scope_complete=True,
                                  negative_scope=list(key), exclusion_predicate=terminal_reason,
                                  closed_source_refs=sorted(paths))
            elif (item in base.get('water_container_sources', {}) and not conflicts
                    and fields.get('Type') in {'Normal', 'Drainable'}
                    and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'DisplayName', 'Icon', 'WorldStaticModel',
                        'CanStoreWater', 'IsWaterSource', 'ReplaceOnDeplete', 'ReplaceOnUseOn', 'ReplaceTypes',
                        'RainFactor', 'Tooltip', 'ToolTip', 'StaticModel', 'EatType', 'SurvivalGear', 'Tags', 'MetalValue',
                        'UseDelta', 'UseWhileEquipped', 'CustomContextMenu', 'CustomEatSound', 'IsCookable',
                        'FillFromDispenserSound', 'FillFromTapSound', 'ConditionMax'}
                    and set(fields.get('Tags', '').split(';')) <= {'', 'CoffeeMaker', 'HasMetal'}
                    and 'PetrolSource' not in fields.get('ReplaceTypes', '')):
                source = base['water_container_sources'][item]
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                required = {'store_water', 'receive_poured_water'}
                if source['is_filled_source']:
                    required |= {'pour_water_into_container', 'supply_world_water_storage', 'water_seeded_crop',
                                 'wash_vehicle_blood', 'drink_stored_water', 'dump_water', 'extinguish_fire'}
                if required <= functions:
                    paths = {semantic.MENU, sources.WORLD_MENU, sources.TAKE_WATER, sources.TRANSFER_WATER,
                             sources.ADD_WATER, semantic.DRINK, semantic.TRANSFER, sources.DUMP_WATER,
                             sources.CONSOLIDATE, sources.OBJECT_COMMANDS, sources.FIRE_FIGHTING,
                             sources.EXTINGUISH_CURSOR, sources.PUT_OUT_FIRE, sources.FARM_MENU, sources.WATER_PLANT,
                             sources.FARM_CLIENT, sources.FARM_SYSTEM, sources.FARM_COMMANDS, sources.PLANT,
                             sources.VEHICLE_USE_MENU, sources.WASH_VEHICLE, sources.VEHICLE_COMMANDS,
                             semantic.CRAFT, semantic.GROUPS, semantic.COOK}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'water_vessel_consumers'
                    applied['direct_scope'] = {'declaration': fields, 'binding': source,
                        'filling': sources.WATER_STORAGE, 'inventory_transfer': sources.WATER_TRANSFER,
                        'filled_consumers': [sources.WORLD_WATER_TRANSFER, sources.CROP_WATERING, sources.VEHICLE_WASHING,
                            sources.WATER_DRINKING, sources.WATER_EMPTYING, sources.EXTINGUISH_CONDITIONS,
                            sources.MEDICAL_CONSOLIDATION] if source['is_filled_source'] else [],
                        'auto_drink': 'The selected carried water item exposes AutoDrinkOn/Off, but both callbacks set the global Core option and ignore the item argument. This is general user preference management, not a per-item setting or hydration guarantee.',
                        'cooking': 'Exact normal/Drainable vessels are not assumed to be Food. Recipe and evolved-recipe ingredients/base/result bindings retain their separate scopes. Bowl portion receipt is already represented where supported. CoffeeMaker and HasMetal tags are not independent proof of brewing or heat effects.',
                        'remaining_fields': 'RainFactor, IsCookable, metal/thermal tags and native water getters/replacement mapping remain explicit loader/engine boundaries. No local rain collection, safe purification or microwave compatibility is inferred from tooltip wording.',
                        'other_dispatch': 'This strict field set has no petrol mapping, weapon, activation, light, medical, clothing, storage-capacity, remote or recorded-media capability. Named filled water bottles are not petroleum forms. General placement/inventory management remains excluded.'}
                    work = None
                    residual = {'meaning': 'Native water-vessel and thermal/rain binding, replacement/depletion and world/client synchronization',
                        'required_input': 'InventoryItem water getters, getReplaceType, UseDelta/Use and factory initialization; world water capacity and RainFactor/IsCookable/HasMetal interpretation where declared; world-inventory water synchronization; vehicle blood setter and farming persistent state delivery',
                        'reason': 'Available filling, receiver replacement, transfers, drinking, emptying, extinguishing, crop watering and vehicle washing consumers are interpreted with their actual partial-application and validity differences. Native quantity/property binding and explicitly missing synchronization remain; changing current water, crop or blood amounts does not create a local-work blocker.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in {'farming.GardeningSprayMilk', 'farming.GardeningSprayCigarettes'} and not conflicts
                    and fields.get('Type') == 'Drainable' and set(fields) <= {'DisplayCategory', 'Type', 'DisplayName',
                        'Icon', 'Weight', 'UseDelta', 'ReplaceOnDeplete', 'UseWhileEquipped', 'StaticModel', 'WorldStaticModel'}
                    and any(f['item_id'] == item and f['payload'].get('function') in {'treat_crop_mildew', 'treat_crop_flies'} for f in facts.values())):
                paths = {semantic.MENU, sources.FARM_MENU, sources.CURE_MILDEW, sources.CURE_FLIES,
                         sources.FARM_CLIENT, sources.FARM_SYSTEM, sources.FARM_COMMANDS, sources.PLANT,
                         sources.CONSOLIDATE, sources.DUMP_CONTENTS}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'crop_spray_treatment'
                applied['direct_scope'] = {'declaration': fields, 'treatment': sources.SPRAY_TREATMENT,
                    'consolidation': sources.MEDICAL_CONSOLIDATION,
                    'emptying': base.get('container_emptying_relations', {}).get(item),
                    'other_dispatch': 'Neither spray declares IsWaterSource: do not infer watering, drinking, water-transfer or fire-extinguishing from its bottle. Replacement reaches the exact empty spray; treatment preparation and acquisition have independent recipe questions. No activation, wearable, weapon, medical wound or recorded-media selector matches these fields.'}
                work = None
                residual = {'meaning': 'Native spray depletion/replacement, consolidation eligibility and farming state delivery',
                    'required_input': 'Drainable remaining uses, Use replacement and canConsolidate; persistent crop-state delivery after the separate client consumption and server treatment calls',
                    'reason': 'Both exact disease consumers, their live guards, actual five-point setter, over-treatment and level-100 consumption gap are interpreted. The bottles do not gain water or general-pesticide functions from their names.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.KEY_ITEMS | {'Base.Padlock', 'Base.CombinationPadlock'}
                    and fields.get('Type') == 'Key' and not conflicts
                    and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'DisplayName', 'Icon', 'MetalValue',
                        'WorldStaticModel', 'Padlock', 'DigitalPadlock', 'Tooltip'}
                    and {'rename_selected_item', ('operate_door_lock' if item in sources.KEY_ITEMS else
                        'install_padlock' if item == 'Base.Padlock' else 'install_combination_padlock')} <= {
                            f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.NAME_DIALOG, sources.WORLD_MENU, sources.PADLOCK_ACTION,
                         sources.DOOR_LOCK, sources.DIGITAL_CODE, semantic.BUILD_UTIL, sources.INVENTORY_PAGE,
                         sources.VEHICLE_USE_MENU, sources.VEHICLE_START, sources.VEHICLE_DASHBOARD,
                         sources.VEHICLE_COMMANDS, sources.VEHICLE_CALLBACKS, sources.VEHICLE_MECHANICS,
                         *sources.VEHICLE_DOOR_ACTIONS}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'key_and_lock_consumers'
                applied['direct_scope'] = {'declaration': fields,
                    'keys': [sources.DOOR_KEY_USE, sources.PADLOCK_KEY_USE, sources.VEHICLE_KEY_USE,
                             sources.KEY_ALARM, sources.KEY_MECHANICS] if item in sources.KEY_ITEMS else [],
                    'padlock': sources.PADLOCK_USE if item == 'Base.Padlock' else None,
                    'combination': [sources.CODE_LOCK_USE, sources.CODE_UNLOCK] if item == 'Base.CombinationPadlock' else [],
                    'container_ui': 'ISInventoryPage disables locked-to-character container controls through a native predicate; a padlocked object with haveThisKeyId gets an unlocked icon, which does not itself enable the controls or remove a padlock.',
                    'vehicle_lock': 'The exterior menu selects a usable installed door and delegates to canUnlockDoor/canLockDoor. Unlock action calls toggleLockedDoor, stops if still locked, otherwise sends setDoorLocked in multiplayer and force-completes. The lock action sends its command after its door-state validity guard. Server setDoorLocked rejects absent door and does not mutate a broken lock; native key permission is not supplied by the Key display name.',
                    'other_dispatch': 'Key category admits naming. Exact declarations supply no food, wearable, water, medical, activation, weapon, magazine or recorded-media function. Padlock flags identify their named world consumers; MetalValue remains a native property, not a local melting action. General placement and inventory management are excluded.'}
                work = None
                residual = {'meaning': 'Native key identity, lock/code enforcement, vehicle permission and created-item binding',
                    'required_input': 'haveThisKeyId and key-ID assignment, NumberOfKey defaults, IsoDoor/IsoThumpable locked-to-character enforcement; BaseVehicle canLockDoor/canUnlockDoor/toggleLockedDoor, ignition/door-key transfer and tryStartEngine; inventory item creation/removal and MetalValue binding',
                    'reason': 'Available door, padlock, code dialog, vehicle request/alarm/mechanics and container UI consumers are interpreted. Key compatibility and enforcement are exact native dependencies; current possession and movement are represented guards, not blanket local-work blockers. Unvalidated code text and missing fresh padlock-key lookup remain explicitly described source failure paths.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.TrapBox', 'Base.TrapCage', 'Base.TrapCrate', 'Base.TrapMouse', 'Base.TrapSnare', 'Base.TrapStick'}
                    and fields.get('Type') == 'Normal' and fields.get('Trap', '').lower() == 'true'
                    and not conflicts and set(fields) <= sources.MATERIAL_OBJECT_FIELDS | {'Trap'}
                    and {'place_animal_trap', 'catch_trap_animal', 'manage_animal_trap'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.TRAP_MENU, sources.TRAP_BUILD, sources.TRAP_DEFINITIONS,
                    sources.TRAP_CLIENT, sources.TRAP_CLIENT_OBJECT, sources.TRAP_SYSTEM, sources.TRAP_OBJECT,
                    sources.TRAP_COMMANDS, sources.TRAP_BAIT, *sources.TRAP_ACTIONS,
                    semantic.BUILD_OBJECT, semantic.BUILD_ACTION, sources.CAMP_FUEL, sources.CAMP_MENU,
                    *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_animal_trap_lifecycle'
                applied['direct_scope'] = {'declaration': fields, 'paths': [sources.TRAP_PLACEMENT, sources.TRAP_CATCH,
                    sources.TRAP_CONTROLS, sources.TRAP_LIFECYCLE],
                    'other_dispatch': 'Exact registered Trap=True Normal forms join the installed global object. They are not physics explosive traps or FishingNet. Their complete fields select no additional food, weapon, water, light, medical or garment action; independent crafting roles remain separate.'}
                work = None
                residual = {'meaning': 'Native trap object persistence, freshness, random catch/destruction and inventory delivery',
                    'required_input': 'The streamed global-object lifecycle, native freshness/random functions, item creation and client/server delivery for the exact registered trap',
                    'reason': 'Available placement, baiting, retrieval, hourly capture/destruction and sound callbacks are interpreted. Loaded-square exclusion and current bait/animal state remain represented conditions rather than unfinished local work.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.FishingRod', 'Base.FishingRodTwineLine', 'Base.CraftedFishingRod', 'Base.CraftedFishingRodTwineLine',
                          'Base.FishingTackle', 'Base.FishingTackle2'} and not conflicts
                    and ((fields.get('Type') == 'Weapon' and fields.get('Tags') == 'FishingRod'
                          and set(fields) <= PLAIN_MELEE_FIELDS | {'Tags', 'SurvivalGear'})
                         or (fields.get('Type') == 'Normal' and fields.get('FishingLure', '').lower() == 'true'
                             and set(fields) <= sources.MATERIAL_OBJECT_FIELDS | {'FishingLure'}))):
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                required = {'fish_with_rod', 'melee_attack', 'wash_carried_equipment'} if fields['Type'] == 'Weapon' else {'bait_rod_fishing'}
                if required <= functions:
                    paths = {semantic.MENU, sources.WORLD_MENU, sources.FISHING_UI, sources.FISHING_ACTION,
                        sources.FISHING_PROPERTIES, sources.FIREARM, semantic.CRAFT, semantic.GROUPS,
                        sources.WASH_CLOTHING, sources.TAKE_WATER, sources.CAMP_FUEL, sources.CAMP_MENU,
                        *base['inventory_context_sources']}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_rod_and_artificial_lure'
                    applied['direct_scope'] = {'declaration': fields, 'required_functions': sorted(required),
                        'fishing': [sources.ROD_FISHING, sources.FISHING_EXECUTION, sources.FISHING_LURES,
                                    sources.FISHING_MATCHES, sources.FISHING_LURE_LOSS, sources.ROD_LINE_BREAK],
                        'other_dispatch': 'Rod melee and blood washing are separately represented; line repair/form changes are independently interpreted recipes. Artificial lure selection follows the registered plastic flag, not Food or Trap bait capability. Neither line supplies nor a broken rod select this intact-rod control.'}
                    work = None
                    residual = {'meaning': 'Native fishing registry/classification, random stock/line/catch execution and returned item identity',
                        'required_input': 'WeaponType and FishingLure field binding, current fish/lure registration, random/zone persistence and InventoryItemFactory/hand delivery',
                        'reason': 'All available UI, timed action, recursive fish selection, line replacement, continued casting and lure loss branches are interpreted. Random catches and source recursion do not become guaranteed results.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Jack', 'Base.LugWrench', 'Base.EngineParts'} and fields.get('Type') == 'Normal'
                    and not conflicts and set(fields) <= sources.MATERIAL_OBJECT_FIELDS | {'MechanicsItem'}
                    and item in base.get('equipment_control_sources', {})):
                source = base['equipment_control_sources'][item]
                refs = sorted(set(refs) | set(source['observation_refs']))
                applied['direct_rule'] = 'exact_vehicle_service_supply'
                applied['direct_scope'] = {'declaration': fields, 'paths': source['predicates'],
                    'templates': base.get('vehicle_tool_sources', {}).get(item),
                    'other_dispatch': 'These complete Normal declarations select no food, weapon, water, clothing, medical, activation or camping-fuel action. Jack/LugWrench are kept template tools, not installed parts. EngineParts are consumed by repair but output-only in engine salvage. General inventory placement is not mechanical lifting or restored engine performance.'}
                work = None
                residual = {'meaning': 'Native part eligibility, successful mechanical state change and supply delivery',
                    'required_input': 'BaseVehicle canInstallPart/canUninstallPart and condition/performance binding, native key/access and inventory/client-server execution',
                    'reason': 'Actual template tools, entry, transfer, action validity, server rolls and repair arithmetic are interpreted. This does not conflate declared keep tools with the part being installed or guarantee repair.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Corkscrew', 'Base.MortarPestle', 'Base.TinOpener', 'Base.Paperclip', 'Base.Screws',
                          'Base.SharpedStone', 'Base.FertilizerEmpty', 'Base.CakeBatter', 'Base.PieDough'}
                    and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.MATERIAL_OBJECT_FIELDS | {'Tags', 'Carbohydrates', 'Proteins', 'Lipids', 'Calories'}
                    and set(filter(None, fields.get('Tags', '').split(';'))) <= {'Corkscrew', 'MortarPestle', 'CanOpener'}):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, semantic.PROPS, sources.MOVE_TOOLS,
                    sources.FERTILIZE_ACTION, sources.FARM_MENU, sources.CAMP_MENU, sources.CAMP_FUEL,
                    *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_plain_material_and_recipe_implement'
                applied['direct_scope'] = {'declaration': fields,
                    'recipe_boundary': 'Exact recipe/group inputs are independently interpreted, including CanOpener package opening, MortarPestle preparation and SharpedStone random loss in spear creation. Corkscrew/MortarPestle/CanOpener tags are recipe selectors, not arbitrary wine opening, grinding or food consumption.',
                    'world_boundary': 'Moveable material and cutter tool roles remain their own world-work questions. FertilizerEmpty occurs as a string removal request after another fertilizer is used, not as an applied fertilizer. CakeBatter and PieDough are Normal despite declared nutrition, so the Food consumption dispatch does not select them.',
                    'negative_dispatch': 'The complete declarations have no additional water, weapon, garment, activation, medical-power, radio or fuel/tinder selector. General inventory handling and result appearances do not supply an intrinsic use.'}
                work = None
                residual = {'meaning': 'Native item field binding and recipe/material execution beyond the interpreted exact selectors',
                    'required_input': 'Script Normal/Tag/nutrition interpretation, RecipeManager eligibility and delivery, native moveable material dispatch, and inventory string-removal semantics where selected',
                    'reason': 'Available exact recipe and world references are independently attributed and direct typed controls are excluded by complete declarations. Unsupported eating or arbitrary tool functions are not inferred from display names.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item == 'Base.SheetMetal' and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.MATERIAL_OBJECT_FIELDS
                    and {f['payload']['function'] for f in facts.values()
                         if f['item_id'] == item and f['fact_kind'] == 'direct_function'} == {'build_metal_barricade'}):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.WORLD_MENU,
                    sources.BARRICADE, sources.OBJECT_COMMANDS, semantic.BUILD, semantic.STAGE,
                    semantic.MOVE, semantic.PROPS, sources.CAMP_MENU, sources.CAMP_FUEL,
                    *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_metal_sheet_barricade_supply'
                applied['direct_scope'] = {'declaration': fields, 'selected_control': sources.METAL_BARRICADE,
                    'other_dispatch': 'The exact Normal sheet supplies one metal sheet to the approached compatible barricade target with a torch. It is not the MetalBar weapon, a wearable or water container. Independent welding, crafting and moveable material roles remain on their own activity questions. Complete fields select no additional food, medical, activation, radio or hearth-fuel branch; ordinary inventory handling is excluded.'}
                work = None
                residual = {'meaning': 'Native barricade creation/strength, sheet consumption and command delivery',
                    'required_input': 'BarricadeAble native metal installation and inventory removal delivery for the exact target',
                    'reason': 'The menu, approach, timed validity, torch use and server material request are interpreted with their distinct guards. This does not promise barricade strength or atomic delivery, or import welding-menu mask/learning requirements.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Sheet', 'Base.BlowTorch'} and not conflicts
                    and ((item == 'Base.Sheet' and fields.get('Type') == 'Normal'
                          and set(fields) <= sources.MATERIAL_OBJECT_FIELDS)
                         or (item == 'Base.BlowTorch' and fields.get('Type') == 'Drainable'
                             and set(fields) <= sources.FUEL_FIELDS | {'KeepOnDeplete'}))
                    and item in base.get('equipment_control_sources', {})):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.WORLD_MENU,
                    sources.OBJECT_COMMANDS, semantic.BUILD_UTIL, semantic.BUILD, semantic.STAGE,
                    sources.MOVE_TOOLS, sources.CAMP_MENU, sources.CAMP_FUEL, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_curtain_supply_or_welding_torch'
                applied['direct_scope'] = {'declaration': fields,
                    'selected_controls': [sources.CURTAIN_USE] if item == 'Base.Sheet' else
                        [sources.BURNT_VEHICLE_USE, sources.METAL_BARRICADE, sources.METAL_UNBARRICADE],
                    'separate_scopes': 'Exact recipe, construction and moveable roles remain separately interpreted. Sheet does not select clothing or water collection. BlowTorch is not a StartFire/Petrol item and KeepOnDeplete does not replenish fuel; the torch supplies welding uses rather than a generic weapon attack.'}
                work = None
                residual = {'meaning': 'Native installed-object binding, consumption and command delivery',
                    'required_input': 'Native addSheet/removeSheet/toggle and visibility or barricade/vehicle removal implementations, plus Drainable Use/depletion where selected',
                    'reason': 'Available exact declaration and called Lua paths are interpreted. Installed effects, returned identity and non-atomic material/world updates retain their concrete native boundary.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.CompostBag', 'Base.Extinguisher', 'Base.Tissue', 'Base.ToiletPaper',
                          'Base.BucketConcreteFull', 'Base.BucketPlasterFull'}
                    and fields.get('Type') == 'Drainable' and not conflicts
                    and set(fields) <= sources.FUEL_FIELDS | {'EatType'}):
                required = {'Base.CompostBag': {'apply_fertilizer', 'transfer_compost', 'consolidate_drainable_supplies'},
                    'Base.Extinguisher': {'extinguish_fire'},
                    'Base.Tissue': {'consolidate_drainable_supplies', 'provide_campfire_tinder', 'supply_campfire_fuel'},
                    'Base.ToiletPaper': {'consolidate_drainable_supplies', 'provide_campfire_tinder', 'supply_campfire_fuel'},
                    'Base.BucketConcreteFull': {'dump_contents', 'consolidate_drainable_supplies'},
                    'Base.BucketPlasterFull': {'dump_contents', 'consolidate_drainable_supplies', 'plaster_supported_structure'}}[item]
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                if required <= functions:
                    paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.CONSOLIDATE,
                        sources.WORLD_MENU, sources.CAMP_MENU, sources.CAMP_FUEL, sources.CAMP_ADD, sources.CAMP_LIGHT,
                        sources.CAMP_SERVER, sources.CAMP_COMMANDS, sources.CAMP_OBJECT, sources.HEALTH,
                        sources.DUMP_CONTENTS, sources.FIRE_FIGHTING, sources.EXTINGUISH_CURSOR, sources.PUT_OUT_FIRE,
                        sources.FARM_MENU, sources.FERTILIZE_ACTION, sources.FARM_CLIENT, sources.FARM_SYSTEM,
                        sources.FARM_COMMANDS, sources.PLANT, *base['inventory_context_sources']}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_drainable_household_and_world_supply'
                    applied['direct_scope'] = {'declaration': fields, 'required_functions': sorted(required),
                        'consolidation_and_emptying': 'Same-type progressive consolidation remains native canConsolidate-gated; Extinguisher explicitly forbids it. Concrete/plaster have a finite declared replacement chain to the empty water bucket, selecting dump_contents, not Food consumption. There is no exact BucketConcreteFull input dispatch in the supplied Lua or recipes.',
                        'selected_paths': [sources.EXTINGUISH_CONDITIONS] if item == 'Base.Extinguisher' else
                            [sources.FERTILIZING, sources.FERTILIZER_GROWTH, sources.FERTILIZER_ROT, sources.COMPOST_TRANSFER] if item == 'Base.CompostBag' else
                            [sources.PLASTER_USE] if item == 'Base.BucketPlasterFull' else
                            [sources.CAMP_FUEL_USE, sources.CAMP_TINDER_USE] if item in {'Base.Tissue', 'Base.ToiletPaper'} else [],
                        'other_dispatch': 'These exact fields do not select firearm, garment, light, media, battery, petrol, wound-alcohol or water-source behavior. Tissue/ToiletPaper tooltip names do not implement native sneeze/cough suppression. Compost input is distinct from the container producing it, and plaster is distinct from paint or structural reinforcement. Recipe/construction uses remain independently attributed.'}
                    work = None
                    residual = {'meaning': 'Native supply depletion/default use amount, selected world effect and delivery',
                        'required_input': 'Drainable Use/canConsolidate/replacement initialization; native fire/compost/plaster/farming setters and synchronization where selected; body-damage sneeze/cough handling for Tissue/ToiletPaper',
                        'reason': 'Available exact menus, called actions and separate recipe participation are interpreted. Missing native consumers, declared default use amounts and non-atomic world delivery remain concrete boundaries, not unperformed local work.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.UmbrellaBlack', 'Base.UmbrellaBlue', 'Base.UmbrellaRed', 'Base.UmbrellaWhite'}
                    and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.MATERIAL_OBJECT_FIELDS | {'primaryAnimMask', 'secondaryAnimMask', 'ProtectFromRainWhenEquipped', 'EquippedNoSprint'}
                    and any(f['item_id'] == item and f['payload'] == {'function': 'fold_umbrella'} for f in facts.values())):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.WEAPON_EQUIP,
                    sources.CAMP_MENU, sources.CAMP_FUEL, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_open_umbrella_form'
                applied['direct_scope'] = {'declaration': fields,
                    'form_change': 'The exact close recipe and callback preserve source condition and select result hand placement. Normal open forms do not select HandWeapon attack; closed forms have their own Weapon declaration and opening action.',
                    'native_fields': 'ProtectFromRainWhenEquipped, EquippedNoSprint and primary/secondary animation masks are handed to native item/equipment behavior. No supplied Lua consumer implements their rain or sprint result. Ordinary equip/drop controls do not prove that effect.'}
                work = None
                residual = {'meaning': 'Native held-umbrella rain protection, sprint restriction and form/equipment binding',
                    'required_input': 'ProtectFromRainWhenEquipped and EquippedNoSprint native consumers, item initialization and recipe result hand/model delivery',
                    'reason': 'Available form transformation and direct dispatch are interpreted; the remaining weather/sprint semantics belong to the exact declared native fields rather than unknown present weather.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item == 'Base.Saucepan' and fields.get('Type') == 'Weapon' and not conflicts
                    and set(fields) <= PLAIN_MELEE_FIELDS | {'CanStoreWater', 'ReplaceOnUseOn', 'RainFactor', 'StaticModel'}
                    and {'melee_attack', 'wash_carried_equipment', 'store_water', 'receive_poured_water'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.WORLD_MENU,
                    sources.TAKE_WATER, sources.TRANSFER_WATER, sources.WASH_CLOTHING, sources.FIREARM,
                    sources.CAMP_MENU, sources.CAMP_FUEL, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'weapon_water_vessel'
                applied['direct_scope'] = {'declaration': fields, 'water': [sources.WATER_STORAGE, sources.WATER_TRANSFER],
                    'weapon': [sources.MELEE, sources.WASH_TARGET],
                    'boundary': 'The empty Saucepan is a Weapon and water receiver, while WaterSaucepan is a distinct Drainable. Evolved-recipe/base/result and rice/pasta recipes retain their own interpretation. RainFactor tooltip does not implement rain collection, and filling does not preserve the empty weapon as a simultaneous water source.'}
                work = None
                residual = {'meaning': 'Native weapon outcome, water/replacement and RainFactor binding',
                    'required_input': 'HandWeapon combat execution, water-vessel factory/getters and native world-inventory rain collection',
                    'reason': 'The exact mixed weapon/water declaration selects both independently represented controls; native runtime outcomes are not inferred from the cooking display category.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item == 'Base.Nails' and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.MATERIAL_OBJECT_FIELDS
                    and {'anchor_escape_rope', 'build_wooden_barricade'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, semantic.BUILD, semantic.STAGE, semantic.BUILD_UTIL, semantic.BUILD_OBJECT,
                    semantic.PROPS, sources.MOVE_TOOLS, sources.WORLD_MENU, sources.BARRICADE,
                    sources.ADD_ROPE, sources.OBJECT_COMMANDS, sources.CAMP_MENU, sources.CAMP_FUEL}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_nail_fastening'
                applied['direct_scope'] = {'declaration': fields, 'direct': [sources.WOOD_BARRICADE, sources.ESCAPE_ROPE_INSTALL],
                    'independent_activities': 'All explicit recipe/build/stage/moveable material uses retain their own interpreted activities. Trap debris is output-only. Count five is item declaration metadata, not five nails consumed by every use; rope and barricade paths have their different guards and consumption boundaries.'}
                work = None
                residual = {'meaning': 'Native escape-rope and barricade material handling and client/server delivery',
                    'required_input': 'Native addSheetRope nail consumption and barricade/part creation plus inventory removal delivery',
                    'reason': 'Available exact direct nail selection and separate construction/recipe participation are interpreted without inventing a generic nailed-structure operation.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.PETROL_ITEMS | sources.EMPTY_PETROL_ITEMS | {'Base.PropaneTank', 'Base.Coal', 'Base.Charcoal', 'Base.Bellows'}
                    and not conflicts and set(fields) <= sources.FUEL_FIELDS
                    and item in base.get('heat_control_sources', {})):
                source = base['heat_control_sources'][item]
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                required = set(source['functions'])
                if fields.get('CanStoreWater', '').lower() == 'true':
                    required.add('store_water')
                if required <= functions:
                    paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.CONSOLIDATE,
                             sources.CAMP_FUEL, sources.CAMP_MENU, *base['inventory_context_sources']}
                    refs = sorted(set(refs) | set(source['observation_refs']) |
                                  {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_fuel_and_heat_dispatch'
                    applied['direct_scope'] = {'declaration': fields, 'required_functions': sorted(required),
                        'interpreted_paths': source['predicates'],
                        'separate_capabilities': 'CanStoreWater selects the independently represented water-container controls; it is absent from EmptyPetrolCan. Drainable consolidation remains conditional on native canConsolidate, and PropaneTank explicitly forbids it. PetrolBleachBottle also declares a water-source replacement. Recipes, fixing and construction participation retain their independently interpreted activity questions.',
                        'negative_selection': 'These complete Normal/Drainable forms have no Food, garment, weapon, radio, battery, light or medical-power selector. Coal is declared obsolete. World furnace/drum/barbecue state is a required target, not an inventory identity inferred from a name.',
                        'source_limits': 'Pump completion adds the remainder whereas progress subtracts it; vehicle actions have permissive ongoing validity; industrial petrol ignition consumes neither input. These source behaviors are preserved rather than repaired in the recovery interpretation.'}
                    work = None
                    residual = {'meaning': 'Native fuel/container binding, heat/ignition and inventory or command delivery',
                        'required_input': 'Drainable Use and replacement creation, piped-fuel methods, vehicle container capacity/setters, native furnace/barbecue/generator fire and heat methods, and client/server delivery for the represented paths',
                        'reason': 'Available exact dispatch and called Lua actions are interpreted, including partial transfer, replacement identity, arithmetic and disabled client ignition. Current charge/target state is represented as a condition; missing native execution is not hidden unfinished Lua interpretation.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Log', 'Base.TreeBranch', 'Base.WoodenStick', 'Base.PercedWood',
                          'Base.Pinecone', 'Base.Twigs', 'Base.UnusableWood'}
                    and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.PLAIN_OBJECT_FIELDS and item in base.get('heat_control_sources', {})):
                source = base['heat_control_sources'][item]
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                required = set(source['functions']) | {'supply_campfire_fuel'}
                if item in {'Base.TreeBranch', 'Base.WoodenStick'}:
                    required |= {'apply_splint', 'remove_applied_splint', 'light_campfire_by_friction'}
                if item == 'Base.PercedWood':
                    required.add('light_campfire_by_friction')
                if required <= functions:
                    paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.CAMP_FUEL, sources.CAMP_MENU,
                        sources.CAMP_ADD, sources.CAMP_LIGHT, sources.CAMP_KINDLE_LIGHT, sources.CAMP_SERVER,
                        sources.CAMP_COMMANDS, sources.CAMP_OBJECT, sources.HEALTH, sources.SPLINT, semantic.BUILD,
                        *base['inventory_context_sources']}
                    refs = sorted(set(refs) | set(source['observation_refs']) |
                                  {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_wood_fuel_dispatch'
                    applied['direct_scope'] = {'declaration': fields, 'required_functions': sorted(required),
                        'heat_paths': source['predicates'],
                        'campfire': [sources.CAMP_FUEL_USE, sources.CAMP_FRICTION, sources.CAMP_TINDER_USE],
                        'independent_activities': 'Exact recipe inputs and construction participation are independently interpreted. Branch/stick splinting is separately represented; no held melee capability follows from these Normal declarations. Only the actual fuel/tinder table membership selects each fire route. Log-to-drum supply does not imply guaranteed charcoal.',
                        'other_fields': 'These complete plain Normal declarations contain no additional tags, water, medical power, clothing, weapon, light, radio or activation capability.'}
                    work = None
                    residual = {'meaning': 'Native world fire, splint state, item removal and output delivery for the exact selected paths',
                        'required_input': 'Native campfire/hearth/furnace state and random execution, medical splint binding where selected, and inventory/client-server delivery',
                        'reason': 'Available exact direct selectors and called actions are interpreted independently of the completed crafting and construction questions; state-dependent conditions are represented and source failure branches remain explicit.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item == 'Base.MetalDrum' and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.MATERIAL_OBJECT_FIELDS):
                paths = {semantic.MENU, semantic.PROPS, sources.BLACKSMITH_MENU, *sources.DRUM_SOURCES,
                         *sources.INDUSTRIAL_ACTIONS, sources.CAMP_MENU, sources.CAMP_FUEL,
                         *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'carried_metal_drum_world_binding_limit'
                applied['direct_scope'] = {'declaration': fields,
                    'world_object': 'The global-object system recognizes an IsoThumpable named MetalDrum, initialized by map sprites or ISMetalDrum. Its rain update collects tainted water and its lit-log ticks make charcoal. Those are installed-object actions.',
                    'missing_join': 'Base.MetalDrum is Normal, DisplayCategory Hidden, without WorldObjectSprite. The furnace/anvil/drum construction menu is inside disableFurnaceAnvil=false, but that variable is true. The onMetalDrum need:Base.MetalDrum assignment is commented out. Moveable pickup creates a Moveables identity, not Base.MetalDrum. No reviewed live caller consumes this carried declaration to create the world object.',
                    'other_dispatch': 'The complete declaration has no food, water-container, weapon, clothing, activation or medical capability and no camping registry selection. General carry/drop is not water collection or charcoal production.'}
                work = None
                residual = {'meaning': 'A supported binding from carried Base.MetalDrum to the installed water/charcoal drum',
                    'required_input': 'An active exact FullType consumer or native item-to-world mapping for Base.MetalDrum',
                    'reason': 'Available construction, map initialization, moveable identity and global-object controls were interpreted. None supplies the required carried-item join; disabled/commented construction is not promoted to a live function.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.DRAINABLE_MATERIALS and fields.get('Type') == 'Drainable'
                    and fields.get('UseWhileEquipped', '').lower() == 'false' and not conflicts
                    and set(fields) <= sources.DRAINABLE_MATERIAL_FIELDS
                    and set(filter(None, fields.get('Tags', '').split(';'))) <= {'Flour', 'Glue'}
                    and any(f['item_id'] == item and f['payload'] == {'function': 'consolidate_drainable_supplies'} for f in facts.values())):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.CONSOLIDATE,
                         sources.WORLD_MENU, sources.CAMP_FUEL, sources.CAMP_MENU, semantic.BUILD,
                         semantic.PROPS, *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_drainable_material_dispatch'
                applied['direct_scope'] = {'declaration': fields, 'consolidation': sources.MEDICAL_CONSOLIDATION,
                    'selected_dispatch': 'These exact Drainable declarations select conditional same-type consolidation. They have no water, food consumption, medical, light, radio, remote, weapon, garment or battery capability. Flour/Glue tags are recipe-group selectors, not intrinsic consumption or application controls. UseWhileEquipped is false; UseDelta and WeightEmpty remain native item-state fields.',
                      'activity_boundary': 'All exact recipe inputs are separately interpreted in crafting questions. Fixing, log-wall binding, forge and welding material use remain their world-work questions. A trap returning Twine does not select an action on carried Twine. The complete camping tables have no exact entry for these selected types and their category fallback excludes Drainable.'}
                work = None
                residual = {'meaning': 'Native consolidation eligibility, same-type lookup and depleted-item handling',
                    'required_input': 'canConsolidate, inventory same-type lookup, Drainable remaining-use/weight binding and Use execution for this exact form',
                    'reason': 'The selected progressive transfer action is interpreted, including possession, interruption and depletion. Recipe and construction consumption remains independently attributed; no food use or functional adhesive effect is inferred from the material name.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Saw', 'Base.GardenSaw'} and fields.get('Type') == 'Normal'
                    and fields.get('Tags') == 'Saw' and not conflicts
                    and set(fields) <= sources.MATERIAL_OBJECT_FIELDS | {'Tags'}
                    and any(f['item_id'] == item and f['payload'] == {'function': 'dismantle_built_object'} for f in facts.values())):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, semantic.BUILD,
                         sources.CAMP_FUEL, sources.CAMP_MENU, *sources.RULES['thumpable_tools']['source_refs'],
                         *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_saw_dispatch'
                applied['direct_scope'] = {'declaration': fields, 'dismantling': sources.THUMPABLE_SCRAP,
                    'independent_activities': 'Saw-group and exact Saw recipes are separately interpreted, including their different shotgun applicability. The build action may choose Sawing sound from the Saw tag; that is not a required additional material or output effect. Movable tool definitions retain their separate world-work attribution. No weapon, medical, water or activation field and no camping fuel/tinder entry selects another direct action.'}
                work = None
                residual = {'meaning': 'Native dismantlable world-object, inventory and removal delivery',
                    'required_input': 'IsoThumpable state/sprite and native inventory factory/removal after the represented cursor action',
                    'reason': 'Actual fallback tool selection and execution are interpreted without treating the inactive legacy menu as live or turning random returns into guaranteed salvage.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item == 'Base.FishingNet' and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.MATERIAL_OBJECT_FIELDS
                    and {'place_fishing_net', 'check_fishing_net', 'remove_fishing_net'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.CAMP_FUEL, sources.CAMP_MENU,
                         *sources.RULES['net_controls']['source_refs'], *base['inventory_context_sources']}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_fishing_net_controls'
                applied['direct_scope'] = {'declaration': fields, 'placement': sources.NET_PLACEMENT,
                    'checking': sources.NET_CHECKING, 'removal': sources.NET_REMOVAL,
                    'other_dispatch': 'The exact Normal net selects its named water menu, not the FishingRod/FishingLure or Trap item predicates. Crafting and general item management remain independent.'}
                work = None
                residual = {'meaning': 'Native net placement, random item returns and source menu binding',
                    'required_input': 'The actual storeWater menu object, native square/object and InventoryItemFactory delivery, random rolls and shared timestamp state',
                    'reason': 'The reachable local placement/check/removal code is interpreted, including captured elapsed-time validity, break-first branch, non-atomic returns and square-scoped timestamp. Current hours are a condition, not unfinished local investigation.',
                    'boundary_kind': 'examined_native_dependency'}
            elif item in base.get('electrical_control_sources', {}):
                source = base['electrical_control_sources'][item]
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                required = set(source['functions'])
                if item == 'Base.Battery':
                    required |= {'use_as_radio_battery', 'supply_portable_device_charge'}
                if required <= functions:
                    paths = set(sources.RULES['electrical_controls']['source_refs']) | {
                        sources.RADIO_POWER, sources.RADIO_ACTION, sources.RADIO_PANEL,
                        semantic.CRAFT, semantic.GROUPS, sources.CAMP_FUEL, sources.CAMP_MENU,
                        sources.HOTBAR, sources.HOTBAR_SLOTS}
                    refs = sorted(set(refs) | set(source['observation_refs']) |
                                  {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_electrical_component_consumers'
                    applied['direct_scope'] = {'declaration': fields, 'required_functions': sorted(required),
                        'lamp': [sources.LAMP_BULB] if item in sources.LIGHT_BULBS else
                                [sources.LAMP_BATTERY, sources.PILLAR_BATTERY, sources.BATTERY_INSERTION, sources.BATTERY_INSERT] if item == 'Base.Battery' else None,
                        'vehicle_battery': [sources.VEHICLE_BATTERY_EXCHANGE, sources.VEHICLE_BATTERY_CYCLE, sources.CHARGER_CONTROLS]
                            if item in {'Base.CarBattery1', 'Base.CarBattery2', 'Base.CarBattery3'} else None,
                        'charger': [sources.CHARGER_PLACEMENT, sources.CHARGER_CONTROLS] if item == 'Base.CarBatteryCharger' else None,
                        'generator': [sources.GENERATOR_CONTROL, sources.GENERATOR_REPAIR, sources.GENERATOR_REFUEL,
                                      sources.GENERATOR_HANDLING, sources.GENERATOR_INSPECTION] if item == 'Base.Generator' else None,
                        'scrap': [sources.LAMP_CONVERSION, sources.GENERATOR_REPAIR] if item == 'Base.ElectronicsScrap' else None,
                        'vehicle_bulb': sources.VEHICLE_BULB_EXCHANGE if item == 'Base.LightBulb' else None,
                        'other_dispatch': 'These exact complete Normal/Drainable declarations have no Food, weapon, worn storage, activated portable-light or remote-device selector. CarBattery and Battery explicitly disable consolidation. Recipes and vehicle/construction material or tool participation remain independently attributed. The examined campfire registry has no exact entry for these forms; ordinary inventory/placement is not substituted for an installed-object function.',
                        'installed_boundary': 'Generator controls require its installed IsoGenerator form, charger controls require IsoCarBatteryCharger, and vehicle parts require runtime compatible binding. A field or name alone is not the installed identity or actual electrical effect.'}
                    work = None
                    residual = {'meaning': 'Native electrical component binding, emitted/supplied power and delivery after the interpreted controls',
                        'required_input': 'IsoLightSwitch add/remove and light/color/power methods; IsoThumpable fuel handling; IsoCarBatteryCharger charge progression; IsoGenerator electricity/range/fuel/toxicity methods; vehicle exact-part compatibility, battery charge and tryStartEngine; factory and client/server inventory delivery, as applicable to the represented paths',
                        'reason': 'Actual control menus, actions, setters and local callbacks are interpreted with their different continued-validity guards and arithmetic. Unused legacy recharge code is not a supported entry point. Native effect uncertainty remains distinct from the completed local work.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.LIGHT_ITEMS and fields.get('Type') == 'Drainable' and not conflicts
                    and set(fields) <= sources.LIGHT_FIELDS):
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                required = set()
                if float(fields.get('LightStrength', '0')) > 0 or item == 'Base.Candle':
                    required.add('control_portable_light')
                if item in {'Base.Torch', 'Base.HandTorch', 'Base.Rubberducky2'}:
                    required |= {'accept_battery_charge', 'remove_device_battery'}
                if item == 'Base.Candle':
                    required.add('light_candle')
                if item == 'Base.CandleLit':
                    required |= {'extinguish_candle', 'extinguish_on_unequip', 'light_campfire'}
                if item == 'Base.Lighter':
                    required |= {'toggle_activation', 'light_campfire'}
                if item == 'Base.Matches':
                    required |= {'consolidate_drainable_supplies', 'light_campfire'}
                if required <= functions:
                    paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.LIGHT_RADIAL, sources.LIGHT_BINDING,
                             sources.CONSOLIDATE, sources.CAMP_MENU, sources.CAMP_LIGHT, sources.CAMP_PETROL_LIGHT,
                             sources.CAMP_CLIENT, sources.CAMP_SERVER, sources.CAMP_COMMANDS, sources.CAMP_OBJECT, sources.CAMP_FUEL}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_portable_light_and_candle_controls'
                    applied['direct_scope'] = {'declaration': fields,
                        'controls': sources.LIGHT_CONTROL if 'control_portable_light' in required else 'No positive light strength/Candle identity selects the light radial; DisplayCategory does not substitute for that predicate.',
                        'battery': [sources.BATTERY_INSERTION, sources.BATTERY_REMOVAL_RECIPE] if 'accept_battery_charge' in required else 'No reviewed battery recipe for this exact type.',
                        'candle': [sources.CANDLE_LIGHT_RECIPE] if item == 'Base.Candle' else [sources.CANDLE_EXTINGUISH_RECIPE, sources.CANDLE_UNEQUIP] if item == 'Base.CandleLit' else [],
                        'ignition': sources.CAMP_IGNITER if 'light_campfire' in required else 'No StartFire tag or exact igniter type selects this campfire route.',
                        'consolidation': sources.MEDICAL_CONSOLIDATION if item == 'Base.Matches' else 'cantBeConsolided is true; no positive consolidation function is inferred.',
                        'other_dispatch': 'These exact drainables have no water replacement, medical, Food, weapon, wearable, storage, remote, radio or recorded-media capability. A rubber-duck name does not implement sound; its actual charge replacement/removal remains represented. Native light and depletion fields are not local executable results.'}
                    work = None
                    residual = {'meaning': 'Native light/activation/charge and exact transformed-item delivery',
                        'required_input': 'canEmitLight, canBeActivated, light geometry and equipped/unequipped drain defaults; RecipeManager/InventoryItem factory and hand delivery' +
                            ('; unbound startFireTypes[types] menu key, parallel tinder/fuel binding, campfire command delivery and native Use' if 'light_campfire' in required else ''),
                        'reason': 'All selected local UI/key, battery and candle callbacks are interpreted with their differing predicates and hand updates. Light emission, result factory and the explicitly identified campfire menu execution limits remain separate; current charge is a condition, not unperformed local work.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.AMMUNITION_ITEMS and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.AMMUNITION_FIELDS
                    and any(f['item_id'] == item and f['payload'] == {'predicate': sources.AMMUNITION_LOADING_PATHS} for f in facts.values())):
                paths = {semantic.MENU, sources.FIREARM, sources.FIREARM_RADIAL, sources.LOAD_MAGAZINE,
                         *sources.RELOAD_ACTIONS, *sources.LEGACY_RELOAD_SOURCES, sources.CAMP_MENU, sources.CAMP_FUEL}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_ammunition_receiver_loading'
                applied['direct_scope'] = {'declaration': fields, 'loading': sources.AMMUNITION_LOADING_PATHS,
                    'other_dispatch': 'These eight strict Normal ammunition declarations have no magazine capacity of their own, weapon attack, activation, water, medical, wearable, storage, radio or media capability. The legacy registry names receivers/clips rather than these ammunition objects. Actual packaging, dismantling and casting recipes retain independent crafting questions. Campfire type/category tables have no entry for these exact ammunition items.',
                    'identity': 'The source consumer compares exact AmmoType and FullType. DisplayCategory selects the menu but does not establish native compatibility, bullet stack quantity or projectile damage.'}
                work = None
                residual = {'meaning': 'Native exact ammunition inventory/capacity interpretation and receiver execution',
                    'required_input': 'AmmoType/current/max-count and factory getters, animation events, legacy receiver modData/difficulty execution, unbound bullets global and .223 magazine GunType lookup',
                    'reason': 'Available ammunition-menu and modern/legacy receiver consumers have been interpreted with distinct guards and identified undefined-reference branches. Count/MetalValue and ammunition names are not substituted for native delivery or effect.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.THROWN_DEVICE_ITEMS and fields.get('Type') == 'Weapon'
                    and fields.get('SwingAnim') == 'Throw' and not conflicts and set(fields) <= sources.THROWN_DEVICE_FIELDS):
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                required = {'request_physics_attack', 'wash_carried_equipment'}
                if float(fields.get('ExplosionTimer', '0')) > 0:
                    required.add('set_device_timer')
                if fields.get('CanBePlaced', '').lower() == 'true':
                    required |= {'place_trigger_device', 'retrieve_placed_device'}
                if fields.get('CanBeRemote', '').lower() == 'true':
                    required |= {'link_remote_device', 'reset_remote_id'}
                if required <= functions:
                    paths = {semantic.MENU, sources.FIREARM, sources.DEVICE_TIMER, sources.DEVICE_PLACE, sources.DEVICE_TAKE,
                             sources.WORLD_MENU, sources.WASH_CLOTHING, sources.TAKE_WATER, sources.OBJECT_COMMANDS,
                             sources.CAMP_MENU, sources.CAMP_FUEL, *sources.LEGACY_RELOAD_SOURCES}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_physics_device_dispatch'
                    applied['direct_scope'] = {'declaration': fields, 'attack': sources.PHYSICS_ATTACK,
                        'timer': sources.DEVICE_TIMER_CONTROL if 'set_device_timer' in required else 'No positive ExplosionTimer declaration selects the timer-setting menu; TriggerExplosionTimer is a distinct raw field.',
                        'placement': sources.DEVICE_WORLD_PLACEMENT if 'place_trigger_device' in required else 'No CanBePlaced declaration selects the placement entry. A PlacedSprite alone is not placement permission.',
                        'retrieval': sources.DEVICE_RETRIEVAL if 'retrieve_placed_device' in required else 'World retrieval needs a surviving IsoTrap with an item; no inventory placement route is inferred.',
                        'remote': [sources.REMOTE_LINK, sources.REMOTE_RESET] if 'link_remote_device' in required else 'No CanBeRemote declaration selects local linking/reset controls.',
                        'other_dispatch': 'The exact fields select no ranged reload, weapon-part receiver, food, medical, water, activated light, clothing, radio or media operation. The six-type legacy firearm registry excludes these types. Common blood washing is represented; campfire type/category tables have no entry for them. Crafting remains independently attributed.'}
                    work = None
                    residual = {'meaning': 'Native physics object, attack and device outcome for the exact declaration',
                        'required_input': 'DoAttack/PhysicsObject projectile creation, collision, UseSelf and OtherHandUse/OtherHandRequire handling; IsoTrap construction, timer/sensor/remote activation, declared fire/explosion/noise/smoke behavior and CanBeReused retention',
                        'reason': 'Every selected local timer, placement, retrieval, remote ID and attack request is interpreted separately. Variant names and raw effect fields do not prove an effect or its absence, range units, successful throwing or post-activation recovery.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.REMOTE_CONTROLLER_ITEMS and fields.get('Type') == 'Normal' and not conflicts
                    and fields.get('RemoteController', '').lower() == 'true' and set(fields) <= sources.REMOTE_CONTROLLER_FIELDS
                    and {'link_remote_device', 'reset_remote_id', 'send_remote_trigger'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.OBJECT_COMMANDS, sources.CAMP_MENU, sources.CAMP_FUEL}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'exact_remote_controller_dispatch'
                applied['direct_scope'] = {'declaration': fields, 'link': sources.REMOTE_LINK,
                    'reset': sources.REMOTE_RESET, 'trigger': sources.REMOTE_TRIGGER,
                    'other_dispatch': 'The three plain Normal controllers have no declared power drain, radio signal, weapon attack, activation, water, medical, clothing, storage or media capability. MetalValue is a native field; crafting is independently attributed. Their exact types have no campfire table entry.'}
                work = None
                residual = {'meaning': 'Native remote ID and range binding and matching trap execution',
                    'required_input': 'InventoryItem remote ID/range getters and setters; IsoTrap.triggerRemote matching, distance and actual activation',
                    'reason': 'The local menu and immediate ID assignment/reset plus command receiver are interpreted. Range declarations and matching IDs do not guarantee a deployed device, transmission result or effect.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in sources.MAGAZINE_ITEMS and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= {'DisplayCategory', 'CanStack', 'Weight', 'Type', 'DisplayName', 'Icon',
                        'MaxAmmo', 'AmmoType', 'StaticModel', 'GunType', 'WorldStaticModel'}
                    and {'fill_magazine', 'empty_magazine'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.FIREARM, sources.LOAD_MAGAZINE, sources.INSERT_MAGAZINE,
                         sources.LEGACY_RELOAD, *sources.RELOAD_ACTIONS}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'magazine_ammunition_and_receiver_controls'
                applied['direct_scope'] = {'declaration': fields, 'fill': sources.MAGAZINE_FILL,
                    'empty': sources.MAGAZINE_EMPTY, 'insertion': sources.MAGAZINE_LOADING if item != 'Base.223Clip' else
                        'No active MagazineType declaration binds this .223 magazine to a receiver. Its own loading/unloading menu remains valid without GunType. The ammunition-item tooltip instead calls CreateItem(getGunType()) and dereferences its result without a nil guard.',
                    'experience': 'InsertBullet grants Reloading XP conditionally: below level five, ZombRand(2)==0 gives four; otherwise ZombRand(5)==0 gives one. Magazine insertion uses ZombRand(1)/four below five and ZombRand(3)/one otherwise.',
                    'selection': 'The selected-magazine menu is not itself gated by isNewReloading; a selected firearm using the new-reloading branch clears the magazine selection. The legacy fixed clip registry has two BerettaClip entries, neither matching these seven FullTypes; getClipData matches clipType exactly. Existing reloadClass modData is a separate legacy saved-state binding.',
                    'sound': 'The optional insertAmmoStart event tests the magazine sound getter but reads self.gun, which this action does not define. None of these declarations sets that sound; native getter/default and event delivery determine whether the faulty branch is entered.',
                    'other_consumers': 'These plain Normal items have no attack, light, water, food, medical, wearable, storage or media capability. Recipe material/output roles remain independently investigated.'}
                work = None
                residual = {'meaning': 'Native ammunition capacity, factory identity, animation and receiver state binding',
                    'required_input': 'InventoryItem MaxAmmo/AmmoType/current-count and sound getter defaults; matching-round inventory operations, InventoryItemFactory creation, animation events and saved legacy reloadClass binding' +
                        ('; authoritative receiver/GunType for Base.223Clip and unguarded ammunition-menu tooltip lookup' if item == 'Base.223Clip' else '; native receiver MagazineType and chamber state'),
                    'reason': 'Own-magazine load/unload consumers and the exact available receiver connection are interpreted with actual event guards and partial retention. The absent .223 receiver is not fabricated, and new-item ejection does not prove preservation of the original magazine.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (fields.get('Type') == 'WeaponPart' and not conflicts
                    and set(fields) <= {'AimingTimeModifier', 'AngleModifier', 'DamageModifier', 'DisplayCategory',
                        'DisplayName', 'HitChanceModifier', 'Icon', 'MaxRangeModifier', 'MetalValue', 'MinRangeModifier',
                        'MountOn', 'PartType', 'RecoilDelayModifier', 'ReloadTimeModifier', 'StaticModel', 'Tooltip',
                        'Type', 'Weight', 'WeightModifier', 'WorldStaticModel'}
                    and {'attach_weapon_part', 'remove_weapon_part'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.WEAPON_UPGRADE, sources.WEAPON_REMOVAL}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'weapon_part_attachment_and_recovery'
                applied['direct_scope'] = {'declaration': fields,
                    'attachment': sources.WEAPON_ATTACHMENT, 'removal': sources.WEAPON_PART_REMOVAL,
                    'selection': 'The inventory menu enumerates top-level WeaponPart-category items, deduplicates by part name and selects the six actual slots. Broken weapons are not rejected by its isHandWeapon predicate. Attachment compatibility is checked in the menu but not repeated by the timed action.',
                    'other_consumers': 'These declarations select neither Weapon attack nor activation, light, food, medical, clothing, water, storage or recorded-media controls. GunLight, Laser and Bayonnet names do not establish illumination, aiming or melee effects. Recipe participation retains independent questions.'}
                work = None
                residual = {'meaning': 'Native weapon-part compatibility and installed modifier effects',
                    'required_input': 'WeaponPart MountOn/PartType loader and HandWeapon attachWeaponPart/detachWeaponPart interpretation of the exact declared modifiers, model and resulting weapon state',
                    'reason': 'The actual selection, equipment, asymmetric timed guards and same-part recovery are interpreted. Modifier declarations are retained without turning names or numerical fields into demonstrated performance effects.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.BarBell', 'Base.DumbBell'} and fields.get('Type') == 'Weapon'
                    and not conflicts and set(fields) <= PLAIN_MELEE_FIELDS | {'CanBarricade'}):
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                exercise_functions = {'exercise_barbell_curl'} if item == 'Base.BarBell' else {'exercise_dumbbell_press', 'exercise_biceps_curl'}
                if exercise_functions | {'melee_attack', 'wash_carried_equipment'} <= functions:
                    paths = {sources.HEALTH, sources.WORLD_MENU, *sources.FITNESS_SOURCES, sources.FIREARM,
                             semantic.MENU, sources.WASH_CLOTHING, sources.TAKE_WATER}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'fitness_weight_consumers'
                    applied['direct_scope'] = {'declaration': fields, 'exercises': sorted(exercise_functions),
                        'selection_and_loop': sources.WEIGHT_EXERCISE,
                        'loop_details': 'The switch counter starts at five, decrements per ActiveAnimLooped and switches at one before resetting to five. showHandModel is not called by start. The runtime hand assignments move the currently held item; continuing action validity does not rebind the declared weight.',
                        'other_consumers': 'Exact melee dispatch and shared Weapon blood washing are represented. No water, health, firearm, activation, media or storage capability is declared. DumbBell CanBarricade is retained as an engine property; the examined normal world barricade selector uses a Hammer-tagged tool rather than this field.'}
                    work = None
                    residual = {'meaning': 'Native exercise outcomes and melee/property interpretation',
                                'required_input': 'Fitness.setCurrentExercise/exerciseRepeat/setFitnessSpeed interpretation of xpMod, stiffness, metabolic and regularity inputs; native DoAttack and CanBarricade property behavior',
                                'reason': 'Registered exercises, UI/equipment constraints and action/animation loops are interpreted. Native exercise repetition owns actual endurance/XP/strength/stiffness changes, separate from the answered ability to perform the named exercise.',
                                'boundary_kind': 'examined_native_dependency'}
            elif item in base.get('firearm_control_sources', {}):
                relation = base['firearm_control_sources'][item]
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                required = {'fire_ammunition', 'rack_firearm', 'wash_carried_equipment'}
                required |= {'receive_firearm_magazine', 'eject_firearm_magazine'} if fields.get('MagazineType') else {'load_firearm_rounds', 'unload_firearm_rounds'}
                if relation['compatible_parts']:
                    required |= {'receive_weapon_upgrade', 'detach_weapon_upgrade'}
                if relation['modes']:
                    required.add('change_firearm_mode')
                if item in sources.LEGACY_GUN_ITEMS:
                    required.add('use_alternate_reload_controls')
                if required <= functions:
                    paths = set(relation['source_paths']) | set(sources.LEGACY_RELOAD_SOURCES) | {sources.LEGACY_RELOAD, sources.WORLD_MENU, sources.WASH_CLOTHING,
                        sources.CAMP_MENU, sources.CAMP_FUEL, sources.HOTBAR, sources.HOTBAR_SLOTS, sources.HOTBAR_ATTACH}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'declared_firearm_controls'
                    applied['direct_scope'] = {**relation,
                        'firing': sources.GUN_FIRING_CYCLE,
                        'other_consumers': 'The exact ranged Weapon fields select no Food, wearable, water, medicine, remote/placed explosive, light or recorded-media action. Weapon is not a registered campfire category and none of these fourteen FullTypes appears in the fuel/tinder tables. Manual washing and ordinary hotbar management are accounted. Fixing, sawing transformations and other crafting roles remain independent questions.',
                        'legacy_selector': 'ISReloadUtil creates six weapon entries only when isNewReloading is false. Type names outside those six have no built-in setup entry; arbitrary mod-added reloadClass is outside the supplied vanilla declarations.'}
                    work = None
                    residual = {'meaning': 'Native firearm execution and declared property/part binding',
                        'required_input': 'DoAttack target, hit, range, damage, recoil and projectile interpretation; declared ammo/magazine/chamber defaults, factory results, event delivery, installed part modifiers and repeated ModelWeaponPart entries',
                        'reason': 'The actual modern firing, loading, unloading, magazine, racking, offered mode and compatible part consumers are interpreted with their different start/ongoing predicates. Raw combat or visual fields do not guarantee accuracy, damage, a specific part loader winner or original magazine return.',
                        'boundary_kind': 'examined_native_dependency'}
                    if item in sources.LEGACY_GUN_ITEMS:
                        applied['direct_scope']['legacy_controls'] = sources.LEGACY_GUN_CONTROLS
                        residual['required_input'] += '; isNewReloading selector and combined Hook dispatch, legacy global difficulty and modData binding, native ammo lookup with cleared AmmoType and subsequent weight debit'
                        residual['reason'] += ' The reachable legacy manager and all selected classes/actions are interpreted, including their unbound difficulty read, player-one difficulty references and ammo-nil lookup hazard. Their success or joint execution with modern hooks is not guaranteed or silently repaired.'
                    else:
                        residual['reason'] += ' The built-in legacy type registry has no entry for this exact gun.'
            elif (item in {'Base.' + name for name in (
                      'Axe', 'AxeStone', 'HandAxe', 'WoodAxe', 'HuntingKnife', 'KitchenKnife', 'Machete', 'FlintKnife', 'SmashedBottle', 'Screwdriver',
                    'BreadKnife', 'ButterKnife', 'Broom', 'Fork', 'Spoon', 'Scissors',
                    'Hammer', 'HammerStone', 'BallPeenHammer', 'ClubHammer', 'WoodenMallet', 'Crowbar',
                    'Sledgehammer', 'Sledgehammer2')} | sources.GROUND_TOOLS
                    and fields.get('Type') == 'Weapon'
                    and set(fields) <= PLAIN_MELEE_FIELDS | {'Tags', 'CanBarricade', 'CantAttackWithLowestEndurance', 'WeaponWeight', 'SurvivalGear'}
                    and set(conflicts) <= {'CriticalChance', 'CritDmgMultiplier', 'Weight'}):
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                tags = set(fields.get('Tags', '').split(';'))
                required = {'melee_attack', 'wash_carried_equipment'}
                for tag, name in (('ChopTree', 'chop_tree'), ('CutPlant', 'cut_bushes_and_vines'),
                                  ('Hammer', 'build_wooden_barricade'), ('RemoveBarricade', 'remove_barricade'),
                                  ('ClearAshes', 'clear_burnt_floor_ashes'), ('Sledgehammer', 'destroy_structure')):
                    if tag in tags:
                        required.add(name)
                if item == 'Base.Broom':
                    required.add('clean_world_blood')
                if item == 'Base.Screwdriver':
                    required |= {'convert_lamp_to_battery', 'dismantle_built_object', 'service_vehicle_parts', 'manage_weapon_attachments'}
                if item in {'Base.Fork', 'Base.Spoon'}:
                    required.add('serve_as_eating_utensil')
                if item == 'Base.Scissors':
                    required |= {'groom_hair', 'groom_beard'}
                if 'DigPlow' in tags:
                    required |= {'dig_furrow', 'remove_farm_plant'}
                if 'TakeDirt' in tags:
                    required.add('collect_ground_into_bag')
                if 'DigGrave' in tags:
                    required |= {'dig_grave', 'fill_grave'}
                if required <= functions:
                    paths = {semantic.MENU, sources.FIREARM, sources.WORLD_MENU, sources.HOTBAR,
                        sources.HOTBAR_SLOTS, sources.HOTBAR_ATTACH, sources.WASH_CLOTHING, sources.TAKE_WATER,
                        sources.CAMP_FUEL, sources.CAMP_MENU, sources.CAMP_ADD, sources.CAMP_LIGHT,
                        sources.CAMP_CLIENT, sources.CAMP_SERVER, sources.CAMP_COMMANDS, sources.CAMP_OBJECT,
                        semantic.GROUPS, semantic.CRAFT, semantic.CLOTHING, semantic.BUILD, semantic.PROPS}
                    if tags & {'ChopTree', 'CutPlant'}:
                        paths.update(sources.RULES['vegetation_tools']['source_refs'])
                    if tags & {'Hammer', 'RemoveBarricade'}:
                        paths.update(sources.RULES['barricade_controls']['source_refs'])
                    if 'Sledgehammer' in tags:
                        paths.update(sources.RULES['structure_destruction']['source_refs'])
                    if item == 'Base.Broom':
                        paths.update({sources.CLEAR_ASHES, sources.CLEAN_CURSOR, sources.CLEAN_BLOOD})
                    if item in {'Base.Spoon', 'Base.Fork'}:
                        paths.add(semantic.EAT)
                    if item == 'Base.Scissors':
                        paths.update({sources.CLOCK_CHARACTER, sources.HAIR_CUT, sources.BEARD_TRIM})
                    if item in sources.GROUND_TOOLS:
                        paths.update(sources.RULES['ground_tools']['source_refs'])
                        paths.add(sources.CLEAR_ASHES)
                    if item == 'Base.HammerStone':
                        paths.update(sources.RULES['thumpable_tools']['source_refs'])
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'exact_weapon_tool_consumers'
                    applied['direct_scope'] = {'declaration': fields, 'repeated_combat_values': conflicts,
                        'required_functions': sorted(required),
                        'farming': [sources.FURROW_DIGGING, sources.PLANT_REMOVAL] if 'DigPlow' in tags else None,
                        'ground_collection': sources.GROUND_FILL if 'TakeDirt' in tags else None,
                        'graves': [sources.GRAVE_DIGGING, sources.GRAVE_FILLING] if 'DigGrave' in tags else None,
                        'held_stone_hammer': sources.STONE_TOOL_WEAR if item == 'Base.HammerStone' else None,
                        'forestry': sources.CHOPPING if 'ChopTree' in tags else None,
                        'plants': sources.PLANT_CUTTING if 'CutPlant' in tags else None,
                        'barricades': [sources.WOOD_BARRICADE if 'Hammer' in tags else None,
                                       sources.WOOD_UNBARRICADE if 'RemoveBarricade' in tags else None],
                        'demolition': sources.STRUCTURE_DESTRUCTION if 'Sledgehammer' in tags else None,
                        'cleaning': [sources.ASH_CLEARING, sources.BLOOD_CLEANING] if item == 'Base.Broom' else None,
                        'utensils': sources.MEAL_UTENSIL if item in {'Base.Fork', 'Base.Spoon'} else None,
                        'grooming': [sources.HAIR_GROOMING, sources.BEARD_GROOMING] if item == 'Base.Scissors' else None,
                        'selection': 'Complete selected tags have separate meanings. CanBarricade without Hammer does not select plank installation; Hammer without RemoveBarricade does not select removal. SharpKnife/DullKnife and tool-group recipe participation remain in their completed crafting questions, not generic world cutting. Sledgehammer has no ChopTree tag despite positive TreeDamage.',
                        'independent_activities': 'Source-bound recipe/fixing, food preparation and moveable/construction tool roles keep their own activity questions. Clothing cutting and hair cutting are not conflated. Ordinary holding, hotbar model and placement actions remain excluded.',
                        'other_fields': 'These exact complete Weapon declarations have no firearm/physics, radio/media, water, activation/light, clothing or medical-power selector. Non-ranged attack and weapon blood washing retain their existing conditions; declared combat values do not establish native damage or combat benefits.'}
                    work = None
                    residual = {'meaning': 'Native combat/tool state, world mutation and delivery after the interpreted exact tool controls',
                        'required_input': 'Weapon stat binding and attack/animation effects; tree and world-object methods, factory and client/server delivery; native grooming visual state where selected; loader precedence for repeated combat scalars where present',
                        'reason': 'The exact tag/name menu selectors and their called local actions are interpreted independently from recipe and construction participation. Source-specific failure branches and conditional results remain in the accepted predicates; native outcomes are not inferred from tool names.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in PLAIN_MELEE_ITEMS and fields.get('Type') == 'Weapon'
                    and set(fields) <= PLAIN_MELEE_FIELDS
                    and set(conflicts) <= {'CriticalChance', 'CritDmgMultiplier', 'WeaponLength'}):
                item_facts = [f for f in facts.values() if f['item_id'] == item]
                functions = {f['payload'].get('function') for f in item_facts}
                if ({'melee_attack', 'wash_carried_equipment'} <= functions
                        and ('ClosedUmbrella' not in item or 'unfold_umbrella' in functions)
                        and (item != 'Base.PipeWrench' or 'plumb_external_water' in functions)
                        and (item != 'Base.Plank' or {'apply_splint', 'remove_applied_splint'} <= functions)):
                    paths = {semantic.MENU, sources.FIREARM, sources.HOTBAR, sources.HOTBAR_SLOTS,
                             sources.HOTBAR_ATTACH, sources.WORLD_MENU, sources.WASH_CLOTHING, sources.TAKE_WATER,
                             sources.CAMP_FUEL, sources.CAMP_MENU, sources.CAMP_ADD, sources.CAMP_LIGHT,
                             sources.CAMP_CLIENT, sources.CAMP_SERVER, sources.CAMP_COMMANDS, sources.CAMP_OBJECT}
                    if item == 'Base.Plank':
                        paths.update({sources.HEALTH, sources.SPLINT})
                    if item == 'Base.PipeWrench':
                        paths.update({sources.PLUMB_ACTION, sources.OBJECT_COMMANDS, semantic.BUILD_UTIL})
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'plain_melee_selected_consumers'
                    applied['direct_scope'] = {
                        'declaration': fields, 'repeated_combat_values': conflicts,
                        'attack': 'The registered hook clears queued actions, checks attack-started/player authorization and dispatches non-ranged DoAttack with supplied charge or zero outside a vehicle (or while shoving). onShoot returns immediately for non-ranged weapons; it does not consume ammunition for these forms.',
                        'washing': 'The carried bloody-Weapon path uses the existing manual water/optional-soap predicates and blood-clearing effect. Clothing dirt and wetness changes are not attributed to these weapons.',
                        'campfire': 'Exact type entries, when present, contribute their already represented fuel/tinder functions with favorite, transfer, reachability, interruption and server guards; Weapon has no general category-fuel fallback.',
                        'variants': 'Closed umbrella opening is separately bound to its exact recipe and form-copy callback. Neither a closed-form attack nor form conversion proves native rain protection.',
                        'plumbing': sources.PLUMBING if item == 'Base.PipeWrench' else 'No named PipeWrench selection.',
                        'splinting': [sources.SPLINTING, sources.SPLINT_REMOVAL] if item == 'Base.Plank' else 'No exact splint-support selection.',
                        'fishing': 'WoodenLance and FishingRodBreak have neither FishingRod nor FishingSpear tags, so the examined normal-world fishing selector rejects them; a test fixture constructing a fishing action does not establish a normal menu route.',
                        'exclusions': 'These exact untagged declarations select no firearm/ammo/remote, medical, activation, water replacement, clothing, recorded-media or named fitness/barricading branch. The separate exact PipeWrench plumbing selector is interpreted where applicable. AttachmentType provides ordinary hotbar placement under the adopted exclusion, not a new slot or special capability. Instrument and sports labels do not define playing effects.',
                        'independence': 'Exact recipe/fixing, food-preparation and construction-material/tool relations keep their own activity questions; those roles are not made complete by this direct attribution.'}
                    work = None
                    residual = {'meaning': 'Native melee execution, combat-stat binding and resulting damage/state changes',
                                'required_input': 'DoAttack target/hit, endurance, wear, animation, range, damage and handedness interpretation for the exact Weapon declaration' +
                                                  ('; loader precedence for repeated ' + ', '.join(sorted(conflicts)) if conflicts else '') +
                                                  ('; native fracture evolution and stored splint support creation' if item == 'Base.Plank' else '') +
                                                  ('; native umbrella result creation and weather protection' if 'ClosedUmbrella' in item else '') +
                                                  ('; native FindExternalWaterSource and actual external-water supply after setUsesExternalWaterSource' if item == 'Base.PipeWrench' else ''),
                                'reason': 'The exact selected attack, washing, applicable registered fuel/form-change and hotbar consumers are interpreted. Declared combat values and labels do not replace native execution; repeated combat scalars remain explicit without blocking unrelated local controls.',
                                'boundary_kind': 'examined_native_dependency'}
            elif (item in base.get('vehicle_running_sources', {}) and not conflicts
                    and set(fields) <= {'ChanceToSpawnDamaged', 'ConditionLowerOffroad', 'ConditionLowerStandard', 'ConditionMax',
                        'DisplayCategory', 'DisplayName', 'EngineLoudness', 'Icon', 'MaxCapacity', 'MechanicsItem',
                        'SuspensionCompression', 'SuspensionDamping', 'Type', 'VehicleType', 'Weight', 'WheelFriction',
                        'WorldStaticModel', 'brakeForce'}):
                source = base['vehicle_running_sources'][item]
                paths = {source['template'], sources.VEHICLE_MECHANICS, sources.VEHICLE_MENU, sources.VEHICLE_INSTALL,
                         sources.VEHICLE_UNINSTALL, sources.VEHICLE_CALLBACKS, sources.VEHICLE_COMMANDS}
                if source['kind'] == 'tire':
                    paths.update(sources.TIRE_ACTIONS)
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'installed_vehicle_running_part_consumers'
                applied['direct_scope'] = {
                    **source, 'wear': sources.BRAKE_WEAR if source['kind'] == 'brake' else sources.RUNNING_WEAR,
                    'tire_special': [sources.TIRE_WEAR, sources.TIRE_INFLATION, sources.TIRE_DEFLATION] if source['kind'] == 'tire' else [],
                    'creation': 'The template create callback delegates to createPartInventoryItem; tires additionally initialize randomized air. Init/install/uninstall callbacks set the native wheel-removed flag. This is not an acquisition guarantee.',
                    'repair': 'Inventory fixing and vehicle repair keep separate source relations and questions. The selected direct menu has no additional declared water, medical, activation, radio, clothing, storage or recorded-media capability.',
                    'limits': 'The reviewed raw vehicle stats do not define braking, suspension forces, traction or engine sound. Server wear/transmit/updatePartStats calls retain native setter and scheduling boundaries.'}
                work = None
                residual = {'meaning': 'Native ' + source['kind'] + ' physics, exact vehicle binding and applied state changes',
                            'required_input': 'VehicleScript template/VehicleType expansion; VehiclePart native item/condition/stat mapping and BaseVehicle ' +
                                              {'tire': 'WheelFriction, pressure clamping/inflation synchronization and wheel physics',
                                               'brake': 'brakeForce and brake-speed getter/stopping response',
                                               'suspension': 'SuspensionDamping/SuspensionCompression and condition-wear getter mapping',
                                               'muffler': 'EngineLoudness and condition-wear getter mapping'}[source['kind']],
                            'reason': 'Exact local exchange, prerequisite enforcement differences, update effects and applicable tire-pressure/removal consumers are interpreted. The named native binding and physics remain; no additional local work is hidden behind generic vehicle-state uncertainty.',
                            'boundary_kind': 'examined_native_dependency'}
            elif (item == 'Base.TirePump' and not conflicts and fields.get('Type') == 'Normal'
                    and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'DisplayName', 'Icon', 'MechanicsItem', 'WorldStaticModel'}
                    and any(f['item_id'] == item and f['payload'] == {'function': 'inflate_vehicle_tire'} for f in facts.values())):
                paths = {sources.VEHICLE_MECHANICS, sources.VEHICLE_MENU, sources.WORLD_MENU, sources.VEHICLE_COMMANDS, *sources.TIRE_ACTIONS}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'tire_pump_inflation_consumer'
                applied['direct_scope'] = {'declaration': fields, 'inflation': sources.TIRE_INFLATION,
                    'exclusions': 'Deflation requires no pump. The inflation callback does not Use or deplete the pump, and no other selected capability field or named branch matches this exact Normal record. This is not a claim about future mods or every possible world use.'}
                work = None
                residual = {'meaning': 'Applied tire pressure and synchronization beyond the pump action requests',
                            'required_input': 'VehiclePart.setContainerContentAmount pressure clamping and BaseVehicle.setTireInflation synchronization',
                            'reason': 'The actual equipment, target, interpolation, validity and server receiver are interpreted; named native setters own the applied pressure.',
                            'boundary_kind': 'examined_native_dependency'}
            elif (fields.get('Type') == 'Container' and not conflicts
                    and set(fields) <= {'AttachmentReplacement', 'BloodLocation', 'BodyLocation', 'CanBeEquipped', 'CanHaveHoles',
                        'Capacity', 'CloseSound', 'ClothingItem', 'ClothingItemExtra', 'ClothingItemExtraOption', 'DisplayCategory',
                        'DisplayName', 'Icon', 'IconsForTexture', 'Medical', 'MetalValue', 'OnlyAcceptCategory', 'OpenSound',
                        'PutInSound', 'ReplaceInPrimaryHand', 'ReplaceInSecondHand', 'RunSpeedModifier', 'SoundParameter',
                        'SurvivalGear', 'Tags', 'Tooltip', 'Type', 'Weight', 'WeightReduction', 'WorldStaticModel', 'clothingExtraSubmenu'}):
                item_facts = [f for f in facts.values() if f['item_id'] == item]
                functions = {f['payload'].get('function') for f in item_facts}
                if ({'store_and_retrieve_items', 'carry_stored_items', 'rename_selected_item', 'wash_carried_equipment'} <= functions
                        and (not fields.get('CanBeEquipped') or fields['CanBeEquipped'] == 'Back' and 'wear_container_on_back' in functions
                             or fields['CanBeEquipped'] in {'FannyPackBack', 'FannyPackFront'} and 'switch_declared_clothing_form' in functions)
                        and (not fields.get('Tags') or fields['Tags'] == 'HoldDirt' and 'fill_ground_bag' in functions)):
                    paths = {semantic.MENU, semantic.TRANSFER, semantic.WEAR, sources.BODY_LOCATIONS, sources.HOTBAR,
                             sources.HOTBAR_SLOTS, sources.WORLD_MENU, sources.WASH_CLOTHING, sources.TAKE_WATER}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'inventory_container_consumers'
                    applied['direct_scope'] = {
                        'declaration': fields,
                        'storage_fact_refs': [f['fact_id'] for f in item_facts if f['payload'].get('function') in {'store_and_retrieve_items', 'carry_stored_items'}],
                        'storage': 'The menu and transfer action use the contained inventory, isItemAllowed, hasRoomFor, source removal permission and no recursive self-containment. Existing-container, corpse-removal and multiplayer transaction/count restrictions retain their actual branches; ordinary transfer/drop UI remains excluded as a distinct item capability.',
                        'naming': sources.RENAME_ITEM,
                        'wear': ('Back selection, inventory guard, interruptions and removal from hands/setWornItem/refresh are represented.' if fields.get('CanBeEquipped') == 'Back' else
                                 'The two declared fanny-pack variants use their paired extra-form menus and replacement/copy/wear action; the Back-only menu is not generalized.' if fields.get('CanBeEquipped') else 'No wearable-container slot is declared.'),
                        'washing': 'Container blood removal is represented under the shared equipment-water predicate; clothing dirt-clearing is not attributed to a container.',
                        'ground': base.get('ground_bag_relations', {}).get(item),
                        'hotbar': 'AttachmentReplacement changes attachment placement for existing worn slots through getSlotDefReplacement. It does not declare an attachment-slot provider. This is the already excluded general hotbar placement behavior.',
                        'exclusions': 'Exact container fields declare no eating, drinking/water replacement, activation, dye, bandage, remote, reading or recorded-media selector. Medical and display labels are not substituted for CanBandage. Recipe and world material participation remain separate.'}
                    work = None
                    residual = {'meaning': ('Native container admission, carrying and worn-slot outcomes' if axis == 'operation' else
                                           'Native capacity, item-category admission, weight reduction and worn-slot interpretation'),
                                'required_input': 'InventoryContainer/ItemContainer capacity, WeightReduction, isItemAllowed' +
                                                  (' and OnlyAcceptCategory=' + fields['OnlyAcceptCategory'] if fields.get('OnlyAcceptCategory') else '') +
                                                  '; native setWornItem/slot exclusivity where wearable' +
                                                  ('; native filled-ground-bag creation and terrain setter' if fields.get('Tags') == 'HoldDirt' else ''),
                                'reason': 'The exact storage, naming, washing and applicable back/paired-form/ground-fill consumers have been interpreted. The declaration values feed named native inventory and slot APIs; no capacity formula, item admission or load reduction is invented from the raw values.',
                                'boundary_kind': 'examined_native_dependency'}
            elif (fields.get('Type') == 'Literature' and fields.get('CanBeWrite', '').lower() == 'true'
                    and not conflicts and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'DisplayName',
                        'Icon', 'CanBeWrite', 'PageToWrite', 'StaticModel', 'WorldStaticModel'}
                    and {'view_written_note_pages', 'record_written_notes', 'supply_campfire_fuel', 'provide_campfire_tinder'} <= {
                        f['payload'].get('function') for f in facts.values() if f['item_id'] == item}):
                paths = {semantic.MENU, sources.NOTE_EDITOR, sources.CAMP_FUEL, sources.CAMP_MENU,
                         sources.CAMP_ADD, sources.CAMP_LIGHT, sources.CAMP_CLIENT, sources.CAMP_SERVER,
                         sources.CAMP_COMMANDS, sources.CAMP_OBJECT}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'writable_note_and_fuel_consumers'
                applied['direct_scope'] = {'declaration': fields,
                    'note': 'The writable Literature menu selects read-only or editable journal entry using writer tags and the other-user lock. The existing independently attributed reading questions bind page/title save, read-only access and immediate ownership-lock changes. No normal skill-book ReadLiterature path is selected for CanBeWrite=true.',
                    'campfire': [sources.CAMP_FUEL_USE, sources.CAMP_TINDER_USE],
                    'other_consumers': 'Complete fields select neither Food, weapon, clothing, water, container, activation, radio/media, map nor alarm behavior. Dump-contents excludes Literature. Page and name edits belong to the represented journal; general inventory management and independent recipe participation are separate.'}
                work = None
                residual = {'meaning': 'Native journal storage and campfire fuel/light state execution',
                    'required_input': 'Literature page/title/ownership storage and native campfire object setters after the represented local controls',
                    'reason': 'The actual note editor and registered fuel/tinder consumers are interpreted. Direct attribution reuses those exact existing interpretations without changing the independently completed reading questions.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Pen', 'Base.Pencil', 'Base.RedPen', 'Base.BluePen', 'Base.Eraser'}
                    and not conflicts and ((fields.get('Type') == 'Weapon' and set(fields) <= PLAIN_MELEE_FIELDS | {'Tags', 'ColorRed', 'ColorGreen', 'ColorBlue'})
                        or (item == 'Base.Eraser' and fields.get('Type') == 'Normal' and set(fields) <= sources.PLAIN_OBJECT_FIELDS | {'Tags'}))
                    and set(filter(None, fields.get('Tags', '').split(';'))) <= {'Write', 'Pen', 'Pencil', 'RedPen', 'BluePen', 'Erase'}):
                required = {'erase_map_annotations'} if item == 'Base.Eraser' else {
                    'write_note_pages', 'annotate_map', 'melee_attack', 'wash_carried_equipment'}
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                if required <= functions:
                    paths = {semantic.MENU, sources.NOTE_EDITOR, sources.MAP_VIEW, sources.MAP_SYMBOLS,
                             sources.MAP_TEXT, sources.FIREARM, sources.HOTBAR, sources.HOTBAR_SLOTS,
                             sources.WORLD_MENU, sources.WASH_CLOTHING, sources.CAMP_FUEL, sources.CAMP_MENU}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'writing_and_map_implement_consumers'
                    applied['direct_scope'] = {'declaration': fields, 'required_functions': sorted(required),
                        'writing': sources.NOTE_IMPLEMENT if item != 'Base.Eraser' else 'Erase is not a Write/Pen/Pencil tag; this item cannot supply the journal writer predicate.',
                        'maps': sources.MAP_ERASURE if item == 'Base.Eraser' else sources.MAP_ANNOTATION,
                        'selection': 'Map erasure accepts the exact Base.Eraser name even though this declaration has Erase rather than Eraser. The four writing implements use exact supported color tags. Weapon forms additionally retain melee and manual blood washing; the Normal eraser does not.',
                        'other_consumers': 'These complete fields select no light/activation, water, treatment, radio/media, worn-provider or firearm control. Writing does not itself consume the implement. Recipe participation and ordinary inventory/hotbar handling remain independent.'}
                    work = None
                    residual = {'meaning': 'Native map annotation/journal storage' + (' and melee outcomes' if item != 'Base.Eraser' else ''),
                        'required_input': 'WorldMapSymbols add/remove/storage and Literature note storage' + ('; native DoAttack and declared weapon-stat interpretation' if item != 'Base.Eraser' else ''),
                        'reason': 'Writer/eraser entry, editing controls, named/tag compatibility and the applicable weapon consumers are interpreted; native persistence and attack outcomes remain separate.',
                        'boundary_kind': 'examined_native_dependency'}
            elif (item in {'Base.Camera', 'Base.CameraDisposable', 'Base.CameraExpensive', 'Base.CordlessPhone',
                           'Base.HomeAlarm', 'Base.Remote', 'Base.Speaker', 'Base.VideoGame'}
                    and fields.get('Type') == 'Normal' and not conflicts
                    and set(fields) <= sources.PLAIN_OBJECT_FIELDS | {'Tags', 'Tooltip', 'MetalValue'}
                    and set(filter(None, fields.get('Tags', '').split(';'))) <= {'Camera'}
                    and any(f['item_id'] == item and f['payload'] == {'function': 'dismantle_electronics'} for f in facts.values())):
                paths = {semantic.MENU, semantic.CRAFT, semantic.GROUPS, sources.CONTEXT_RADIO,
                         sources.CONTEXT_MEDIA, sources.CONTEXT_MOVABLE, sources.CAMP_FUEL, sources.CAMP_MENU,
                         sources.LEGACY_MEDIA_MENU, sources.LEGACY_RELOAD}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'normal_electronic_salvage_consumers'
                applied['direct_scope'] = {'declaration': fields, 'dismantling': sources.ELECTRONIC_SALVAGE,
                    'selection': 'The exact normal-device dismantling recipes and callbacks are already interpreted. Camera is a recipe-group tag. These declarations are not Radio/recorded-media objects, remote controllers, active alarms, weapons or powered/activated items. The Camera view-control names are unrelated to an inventory-camera operation.',
                    'other_consumers': 'No named photography, calling, video-game play, sound playback or remote-activation selector matches these complete Normal fields in the examined dispatch. Item labels do not supply those actions. Recipe input/output questions and general inventory management remain independent.'}
                work = None
                residual = {'meaning': 'Native dismantling eligibility, consumption and recovered-item delivery',
                    'required_input': 'RecipeManager participant selection/PerformMakeItem and inventory item creation for the exact bound dismantling recipe',
                    'reason': 'The available direct normal-device salvage path is interpreted, with actual kept-tool, favorite and callback conditions. Unsupported named-device operations are not invented from labels.',
                    'boundary_kind': 'examined_native_dependency'}
            elif (fields.get('Type') == 'Literature' and not conflicts
                    and set(fields) <= {'BoredomChange', 'DisplayCategory', 'DisplayName', 'Icon', 'LvlSkillTrained',
                        'NumLevelsTrained', 'NumberOfPages', 'ReplaceOnUse', 'SkillTrained', 'StaticModel', 'StressChange',
                        'TeachedRecipes', 'Tooltip', 'Type', 'UnhappyChange', 'Weight', 'WorldStaticModel'}):
                item_facts = [f for f in facts.values() if f['item_id'] == item]
                functions = {f['payload'].get('function') for f in item_facts}
                if ({'read_literature', 'supply_campfire_fuel', 'provide_campfire_tinder'} <= functions
                        and any(f['payload'] == {'predicate': sources.READ_SELECTION} for f in item_facts)):
                    paths = {semantic.MENU, semantic.READ, semantic.SKILLS, sources.CAMP_FUEL, sources.CAMP_MENU,
                             sources.CAMP_ADD, sources.CAMP_LIGHT, sources.CAMP_CLIENT, sources.CAMP_SERVER,
                             sources.CAMP_COMMANDS, sources.CAMP_OBJECT}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'nonwritable_literature_consumers'
                    applied['direct_scope'] = {
                        'declaration': fields,
                        'reading_fact_refs': [f['fact_id'] for f in item_facts if f['payload'].get('function') == 'read_literature'
                                              or f['admission']['rule_ref'] in {'literature_selection', 'reading_mood', 'reading_progress', 'reading_parameters'}],
                        'selection': sources.READ_SELECTION,
                        'effects': 'Positive-page progress and registered skill multipliers are separate from non-skill mood stabilization. The latter has no positive-page requirement. A taught-recipe completion marker is not the commented-out Lua known-recipe loop.',
                        'fuel': 'The declared Literature category reaches both positive campfire fuel and tinder category entries. Transfer, favorite restriction, reachability, item removal, ignition-item Use and actual server receiver are represented.',
                        'exclusions': 'No writable field is declared. Food, clothing, map, weapon, container, radio, alarm-clock and recorded-media selectors do not match this reviewed declaration. Dump-contents explicitly excludes Literature. No named key, medical, water, dye, activation, remote or provider-slot selector matches; ordinary inventory management is excluded.',
                        'independence': 'Reading effects/conditions and any recipe participation retain their own questions.'}
                    work = None
                    residual = {'meaning': ('Native literature completion and campfire state execution' if axis == 'operation' else
                                           'Native literature getter and completion/campfire execution conditions'),
                                'required_input': ('Literature default page/skill getters and getMaxLevelTrained; ' +
                                                   ('IsoGameCharacter.ReadLiterature mood, recipe-learning and replacement behavior; ' if not fields.get('SkillTrained') else '') +
                                                   'native campfire object fuel/light setters after the represented server guards'),
                                'reason': 'The exact local selected reading, action updates/completion and registered campfire consumers are interpreted. The named native getters/completion calls remain separate from represented conditional effects; changing reader or campfire state does not itself block these functions.',
                                'boundary_kind': 'examined_native_dependency'}
            elif (item in base.get('vehicle_storage_sources', {}) and not conflicts
                    and set(fields) <= {'DisplayCategory', 'Weight', 'Type', 'DisplayName', 'Icon', 'VehicleType', 'MaxCapacity',
                        'ConditionAffectsCapacity', 'ConditionMax', 'ChanceToSpawnDamaged', 'MechanicsItem', 'WorldStaticModel'}):
                source = base['vehicle_storage_sources'][item]
                paths = {source['template'], sources.VEHICLE_CALLBACKS, sources.INVENTORY_PAGE, semantic.TRANSFER,
                         sources.VEHICLE_MECHANICS, sources.VEHICLE_MENU, sources.VEHICLE_INSTALL, sources.VEHICLE_UNINSTALL,
                         sources.VEHICLE_COMMANDS, sources.VEHICLE_USE_MENU, *sources.VEHICLE_FUEL_ACTIONS}
                if source['override']:
                    paths.add(source['override'])
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                needed = ({'store_vehicle_fuel', 'transfer_vehicle_fuel', 'supply_vehicle_engine_fuel',
                           'install_vehicle_storage_part', 'remove_vehicle_storage_part'} if source['part'] == 'GasTank' else {'store_vehicle_items'})
                if source['family'] == 'NormalCarSeat':
                    needed |= {'use_vehicle_seat', 'install_vehicle_storage_part', 'remove_vehicle_storage_part'}
                    paths |= {sources.VEHICLE_SEAT_UI, *sources.VEHICLE_SEAT_ACTIONS, *sources.VEHICLE_DOOR_ACTIONS}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                if needed <= functions:
                    applied['direct_rule'] = 'vehicle_storage_and_fuel_consumers'
                    applied['direct_scope'] = {'binding': source,
                        'storage': 'The native vehicle container is exposed only through canAccessContainer; all named trunk/open-bed/glove-box callbacks and the transfer consumer are interpreted, without treating the loose item as a container.',
                        'exchange': 'GasTank has exact install/uninstall work tables with empty-tank removal and actual mechanics action/server conditions. Trunk and GloveBox templates have no such tables; no generic exchange function is invented for them.',
                        'fuel': 'Where applicable, engine fuel check/update, can/pump addition and siphoning retain their actual menu, progressive amount and server calls. Can-action validity is true; pump-action validity rechecks area. No atomic inventory/server result is inferred.',
                        'seating': 'For NormalCarSeat, exact seat UI entry/switch/exit and stored-item relocation are interpreted. Driver stop, passenger-moving-vehicle refusal, alternate door/seat reachability and actual animation-signal completion remain distinct; no rest or comfort effect is inferred.',
                        'other_entries': 'These exact mechanics declarations have no Food/Clothing/Weapon, direct container Capacity, power, water-source, recorded-media or activation fields. Repair membership stays in its separate world-work scope.'}
                    work = None
                    residual = {'meaning': 'Native installed part/container behavior' if axis == 'operation' else 'Native exact FullType binding and capacity/access prerequisites',
                        'required_input': 'VehiclePart.getItemType and installed inventory identity for the declared VehicleType; getItemContainer/canAccessContainer and capacity interpretation' +
                            ('; native fuel amount setter, engine callback dispatch and petrol replacement factory outcomes' if source['part'] == 'GasTank' else '') +
                            ('; isSeatInstalled/isSeatOccupied/canSwitchSeat/passenger entry/exit and animation completion' if source['family'] == 'NormalCarSeat' else ''),
                        'reason': 'The available template, override and Lua consumer paths are reconciled to source-bound functions and qualifiers. Native suffix/type binding, capacity/access and called-result behavior remain exact dependencies rather than substitutes for unperformed local investigation.',
                        'boundary_kind': 'examined_native_dependency'}
            elif item in base.get('vehicle_panel_sources', {}):
                panel = base['vehicle_panel_sources'][item]
                paths = {panel['template'], sources.VEHICLE_MECHANICS, sources.VEHICLE_MENU,
                         sources.VEHICLE_INSTALL, sources.VEHICLE_UNINSTALL,
                         sources.VEHICLE_COMMANDS, sources.VEHICLE_CALLBACKS,
                         sources.VEHICLE_USE_MENU, *sources.VEHICLE_DOOR_ACTIONS, semantic.FIX, semantic.MENU,
                         'scripts/vehicles/vehiclesfixing.txt'}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'vehicle_panel_exchange'
                applied['direct_scope'] = {
                    'binding': panel,
                    'exchange': 'Exact runtime FullType selection, client transfer/access, continued validity, actual server success/failure and selected install/uninstall callback are interpreted and represented.',
                    'prerequisites': 'Default tests check recipe/profession/trait, required items and key/access; skill rejection is commented out. Server success/failure uses install-table skills even for uninstall.',
                    'installed_controls': 'Door open/close actions and the actual lock/open server commands are interpreted. Front/RearWindow controls require an installed openable undestroyed window; fixed windshields are excluded. Smash dispatch reaches character:smashCarWindow after isHittable; its active Lua does not calculate the damage.',
                    'use_callbacks': 'Door use dispatches passenger entry, which also has an absent-door branch. Hood use exposes mechanics UI even without a hood. These shared vehicle UI operations are not admitted as abilities uniquely supplied by the item. Actual installed open/lock/window controls are represented.',
                    'repair': 'Existing repair-target facts retain exact fixing records and ISFixAction conditions. Installed repair is additionally gated by isRepairMechanic and a matching FixingManager rule. fixItem owns outcome/material use; the supplied action and server copy the resulting condition and update part stats.',
                    'other_selected_entries': 'The exact Normal/MechanicsItem declaration has no additional custom-use, wearable, radio, food, activation or attachment capability field. General inventory management is excluded under the adopted scope.'}
                work = None
                glass = panel['family'] in {'FrontWindow', 'RearWindow', 'Windshield', 'RearWindshield'}
                has_repair = any(f['item_id'] == item and f['payload'] == {'role': 'repair_target'} for f in facts.values())
                native_use = ('smashCarWindow/isHittable damage interpretation' if glass else
                              'canLockDoor/canUnlockDoor/toggleLockedDoor and vehicle alarm execution')
                residual = {'meaning': ('Exact vehicle compatibility and native ' + ('window damage outcome' if glass else 'lock/alarm behavior') if axis == 'operation' else
                                       'Template expansion, native installation eligibility and ' + ('window damage conditions' if glass else 'lock/alarm eligibility')),
                            'required_input': 'VehicleScript itemType/VehicleType and canInstallPart/canUninstallPart interpretation; ' + native_use + ('; FixingManager repair outcome/material use and installed repair eligibility' if has_repair else ''),
                            'reason': 'The exact exchange, installed controls, use callbacks and applicable repair dispatch have been interpreted. Raw template tokens do not prove suffix compatibility. Native eligibility and the named outcome executors remain distinct from the represented conditional controls and server state assignments.',
                            'boundary_kind': 'examined_native_dependency'}
            elif (fields.get('Type') == 'Food' and item in base.get('food_selected_sources', {})
                    and set(conflicts) <= {'ThirstChange', 'Tags', 'WorldStaticModel'}):
                food_fields = {'DisplayCategory', 'Type', 'DisplayName', 'Icon', 'Weight', 'HungerChange', 'DaysFresh',
                    'DaysTotallyRotten', 'Carbohydrates', 'Proteins', 'Lipids', 'Calories', 'StaticModel', 'WorldStaticModel',
                    'EvolvedRecipe', 'ThirstChange', 'FoodType', 'UnhappyChange', 'EvolvedRecipeName', 'IsCookable',
                    'MinutesToCook', 'MinutesToBurn', 'DangerousUncooked', 'Packaged', 'GoodHot', 'BadCold', 'Spice',
                    'BoredomChange', 'ReplaceOnUse', 'EatType', 'UseDelta', 'OBSOLETE', 'Obsolete', 'Count',
                    'RequireInHandOrInventory', 'StressChange', 'CustomContextMenu', 'CantBeFrozen', 'OnEat',
                    'CustomEatSound', 'CannedFood', 'Tags', 'CantEat', 'HerbalistType', 'Tooltip', 'BadInMicrowave',
                    'OnCreate', 'RemoveUnhappinessWhenCooked', 'FishingLure', 'Poison', 'PoisonDetectionLevel',
                    'PoisonPower', 'UseForPoison', 'CookingSound', 'FatigueChange', 'AlcoholPower', 'Alcoholic',
                    'ReplaceOnCooked', 'ReplaceOnRotten', 'FluReduction', 'ReduceFoodSickness', 'PainReduction',
                    'EnduranceChange', 'RemoveNegativeEffectOnCooked', 'WeightEmpty', 'UseWhileEquipped', 'ReduceInfectionPower', 'Medical', 'OnCooked'}
                source = base['food_selected_sources'][item]
                item_facts = [f for f in facts.values() if f['item_id'] == item]
                functions = {f['payload'].get('function') for f in item_facts}
                consumption_ok = (fields.get('CantEat', '').lower() == 'true' or bool(functions &
                    {'eat_food', 'consume_edible_food', 'drink_food_contents', 'smoke_cigarette', 'take_food_medicine'}))
                callbacks_ok = all(not fields.get(k) or fields[k] in source['callback_interpretations'] for k in ('OnCreate', 'OnCooked'))
                on_eat_ok = (not fields.get('OnEat') or fields['OnEat'] in {'OnEat_WildFoodGeneric', 'OnEat_Cigarettes'}
                    and any(payload['provenance'][p]['rule_ref'] == 'food_callbacks' for f in item_facts for p in f['provenance_refs']))
                bait_ok = (not source['trap_bait_selection']['admitted'] or 'supply_trap_bait' in functions)
                lure_ok = fields.get('FishingLure', '').lower() != 'true' or 'bait_rod_fishing' in functions or bool(source.get('lure_gap'))
                try:
                    health_ok = float(fields.get('AlcoholPower', '0')) <= 0 or 'disinfect_wound' in functions
                except ValueError:
                    health_ok = False
                if set(fields) <= food_fields and consumption_ok and callbacks_ok and on_eat_ok and bait_ok and lure_ok and health_ok:
                    paths = {semantic.MENU, semantic.EAT, semantic.TRANSFER, semantic.GROUPS, semantic.COOK,
                             sources.DUMP_CONTENTS, sources.FISHING_PROPERTIES, sources.TRAP_MENU, sources.TRAP_BAIT,
                             sources.TRAP_CLIENT, sources.TRAP_COMMANDS, sources.TRAP_OBJECT, sources.FISHING_UI,
                             sources.FISHING_ACTION, sources.WORLD_MENU, sources.HEALTH, sources.DISINFECT}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'food_selected_and_state_consumers'
                    applied['direct_scope'] = {'binding': source,
                        'consumption': 'Exact CantEat/custom-label, inventory/companion and start-state branches are represented in ingestion and direct facts where applicable. Known OnEat bodies retain their separate conditional state effects.',
                        'transfer': 'Generic transfer remains excluded as an operation, while its Food-specific chef setter is explicitly retained as a state effect; no XP award is inferred.',
                        'contents': base.get('container_emptying_relations', {}).get(item, {'meaning': 'No admitted water-storing terminal replacement chain for this exact food declaration.'}),
                        'naming': 'Known exact evolved-result forms retain three-extra-ingredient, nonempty/internal-length and actual name/custom-name setters. Other foods are not declared renameable merely because they are Food.',
                        'bait': 'The uncooked/no-extra/non-Drink top-level Food branch, hunger/Worm condition, trap-only validity, fractional consumption and server bait assignment are represented. Catch and animal compatibility are separate.',
                        'special_uses': 'Any declared FishingLure=true must join the registered lure and actual rod-fishing consumers; positive AlcoholPower must join the health-panel wound-disinfection consumer. These extra uses are retained independently of ingestion.',
                        'native_state_fields': {k: v for k, v in fields.items() if k not in {'DisplayName', 'Icon', 'StaticModel', 'WorldStaticModel', 'Tooltip'}},
                        'repeated_properties': conflicts,
                        'lure_registration_gap': source.get('lure_gap'),
                        'separate_scopes': 'Exact ordinary/evolved recipe participation and animal-fishing roles remain independently adjudicated; their pending questions are not completed by this direct-item rule.'}
                    work = None
                    residual = {'meaning': 'Native food-state evolution and exact callback/recipe entry behavior' if axis == 'operation' else 'Native food-state, transformation and getter prerequisites',
                        'required_input': 'Food.update aging/freezing/heating/cooking/burning and declared ReplaceOnCooked/ReplaceOnRotten/ReplaceOnUse behavior; IsoGameCharacter.Eat and exact callback dispatch; native recipe/result, food tag and hunger/poison getters for the retained declaration',
                        'reason': 'The available selected-item, registered-context, transfer-state, known callback, naming, dump and trap-bait Lua consumers are interpreted independently. Native state changes and transformation/getter behavior for the explicit declaration remain bounded; ordinary/evolved crafting work stays visible in its own questions.',
                        'boundary_kind': 'examined_native_dependency'}
                    if conflicts:
                        residual['required_input'] += '; native script-load precedence for the exact repeated ' + ', '.join(sorted(conflicts)) + ' declarations'
                        residual['reason'] += ' Those repeated properties do not change the independently admitted Type-based consumers; their conflicting values remain explicit and are not silently chosen.'
                    if source.get('lure_gap'):
                        residual['required_input'] += '; ' + source['lure_gap']['required_input']
                        residual['reason'] += ' The missing local lure entry and immediate .plastic dereference are a diagnosed source inconsistency, not a supported fishing operation or an unknown current game state.'
            elif (fields.get('Type') == 'Clothing' and item not in sources.STRAP_SPEED
                    and set(conflicts) <= {'BodyLocation', 'Weight', 'Icon'}):
                clothing_fields = {'DisplayCategory', 'Type', 'ClothingItem', 'BodyLocation', 'DisplayName', 'Icon',
                    'WorldStaticModel', 'Weight', 'BloodLocation', 'Insulation', 'WindResistance', 'FabricType',
                    'WorldRender', 'ScratchDefense', 'CanHaveHoles', 'Cosmetic', 'ChanceToFall', 'BiteDefense',
                    'RunSpeedModifier', 'ClothingItemExtra', 'ClothingItemExtraOption', 'clothingExtraSubmenu',
                    'WaterResistance', 'IconsForTexture', 'CombatSpeedModifier', 'ColorRed', 'ColorGreen', 'ColorBlue',
                    'NeckProtectionModifier', 'StompPower', 'ConditionLowerChanceOneIn', 'ConditionMax',
                    'RemoveOnBroken', 'Tags', 'AttachmentsProvided', 'BulletDefense', 'Tooltip', 'OBSOLETE'}
                functions = {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}
                destinations = [v.strip() for v in fields.get('ClothingItemExtra', '').split(';') if v.strip()]
                options = [v.strip() for v in fields.get('ClothingItemExtraOption', '').split(';') if v.strip()]
                variants = base.get('clothing_form_relations', {}).get(item, [])
                variants_ok = len(destinations) == len(options) == len(variants) and (not variants or 'switch_declared_clothing_form' in functions)
                slots_ok = not fields.get('AttachmentsProvided') or bool(functions & {'provide_belt_slots', 'provide_right_holster_slot', 'provide_paired_holster_slots'})
                patch_ok = (not fields.get('BloodLocation') or ('remove_garment_patch' in functions and
                            (not fields.get('FabricType') or 'receive_garment_patch' in functions)))
                fire_ok = not fields.get('FabricType') or {'supply_campfire_fuel', 'provide_campfire_tinder'} <= functions
                tag_scope = {'GasMask'} | ({'HazmatSuit'} if item == 'Base.HazmatSuit' else set()) | (
                    {'WeldingMask'} if item == 'Base.WeldingMask' else set())
                tags_ok = set(filter(None, fields.get('Tags', '').split(';'))) <= tag_scope
                if set(fields) <= clothing_fields and variants_ok and slots_ok and patch_ok and fire_ok and tags_ok and 'wash_carried_equipment' in functions:
                    paths = {semantic.MENU, semantic.CLOTHING, semantic.WEAR, sources.CLOTHING_EXTRA,
                             sources.BODY_LOCATIONS, sources.HOTBAR, sources.HOTBAR_SLOTS, sources.HOTBAR_ATTACH,
                             sources.GARMENT_UI, sources.PATCH_GARMENT, sources.REMOVE_PATCH, sources.WORLD_MENU,
                             sources.WASH_CLOTHING, sources.CAMP_MENU, sources.CAMP_FUEL, sources.CAMP_ADD,
                             sources.CAMP_LIGHT, sources.CAMP_SERVER, sources.CAMP_COMMANDS,
                             sources.TUTORIAL_MENU, sources.PLACE_OBJECT, sources.DROP_OBJECT}
                    refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                    applied['direct_rule'] = 'clothing_selected_and_shared_consumers'
                    applied['direct_scope'] = {
                        'declaration': fields, 'variants': variants, 'body_location_alternatives': conflicts.get('BodyLocation'),
                        'other_repeated_fields': {k: v for k, v in conflicts.items() if k != 'BodyLocation'},
                        'tag_scope': 'GasMask/HazmatSuit do not select a local treatment or activation control. WeldingMask participates in the separately attributed recipe, welding-construction and furniture-scrap tool contexts; it does not add an independent selected-clothing action.',
                        'scope': 'Wear-location/protection behavior retains its wearing questions. This direct result accounts for the remaining selected-item and shared state-changing consumers.',
                        'menu': 'The exact Clothing declaration selects wear/inspect, declared extra forms, manual washing and, when its fabric is eligible, the represented campfire fuel/tinder actions. Slot-provider behavior is represented when declared. The active inspection panel supplies patch/remove controls with their actual prerequisites.',
                        'inactive_path': 'doClothingRecipeMenu returns immediately with the explicit handled-by-recipes statement. Its old ISRipClothing path is not promoted to an active direct function; actual recipe participation/callback questions remain independent.',
                        'exclusions': 'Other selected Food/Literature/Map/Radio/AlarmClock/Weapon/Container and named-item branches do not match. The reviewed field set has no activation, water, dye, medical, remote or recorded-media capability. General holding/positioning and debug management are outside scope.',
                        'independent_comparison': 'Source applicability is judged independently of predecessor migration status; unresolved comparison work remains in the migration inventory.'}
                    work = None
                    dependencies = []
                    if conflicts.get('BodyLocation'):
                        dependencies.append('Native script-load precedence for the exact repeated BodyLocation alternatives; no worn location is selected implicitly')
                    if set(conflicts) & {'Weight', 'Icon'}:
                        dependencies.append('Native script-load precedence for the repeated Weight/Icon alternatives; no runtime weight or icon winner is inferred')
                    if fields.get('BloodLocation'):
                        dependencies.append('Clothing covered-part/fabric mapping and native patch restoration/protection or returned-fabric interpretation')
                    if variants:
                        dependencies.append('Declared alternate-form factory/visual creation and native destination worn-item replacement')
                    if fields.get('StompPower'):
                        dependencies.append('Native foot-stomp interpretation of the declared StompPower and its worn-shoe selection')
                    if fields.get('Tags') == 'GasMask':
                        dependencies.append('Native equipped GasMask-tag interpretation; no such functional consumer is present in the examined Lua dispatch')
                    if fields.get('OBSOLETE', '').lower() == 'true':
                        dependencies.append('Runtime availability of this explicitly obsolete clothing form')
                    if dependencies:
                        residual = {'meaning': ('The named native outcomes of this exact clothing form beyond represented conditional controls' if axis == 'operation' else
                                               'The named native form/part or equipped-state interpretation beyond represented local predicates'),
                                    'required_input': '; '.join(dependencies),
                                    'reason': 'All applicable local selected and shared clothing branches are accounted. The listed dependencies come from this exact declaration and accepted functions; variable contamination, supplies or current patch state is already expressed and does not block those conditional controls.',
                                    'boundary_kind': 'examined_native_dependency'}
                    else:
                        terminal_reason = ('The bound direct scope is answered by the represented manual-washing and any slot controls. Other actual clothing interactions belong to independently retained wearing/crafting questions or excluded general management. No remaining declared special capability selects another examined direct branch.' if axis == 'operation' else
                                           'The applicable direct functions retain their actual contamination, visibility, water, optional supply, inventory and interruption predicates, plus slot conditions where present. No unrepresented meaning-changing prerequisite remains in this bound direct scope; wearing and recipe conditions remain separate questions.')
            elif (item in sources.STRAP_SPEED and fields.get('Type') == 'Clothing'
                    and fields.get('BodyLocation') == 'AmmoStrap' and not conflicts
                    and any(f['item_id'] == item and f['payload'] == {'property': 'reload_speed_setting', 'direction': 'multiply_1_15'} for f in facts.values())):
                paths = {sources.FIREARM, sources.LOAD_MAGAZINE, sources.INSERT_MAGAZINE,
                         *sources.RELOAD_ACTIONS, semantic.MENU, semantic.WEAR, sources.BODY_LOCATIONS}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'ammo_strap_wear_and_speed'
                applied['direct_scope'] = {
                    'declaration': {k: fields.get(k) for k in ('Type', 'BodyLocation', 'ClothingItem', 'Tags')},
                    'wearing': 'The registered AmmoStrap location and actual wear action provide the worn state; the declaration has no extra-form or attachment-slot provider.',
                    'speed': 'All seven local callers use setReloadSpeed. The function tests primary-hand ammo, worn form or equipped tags, then multiplies by 1.15. Racking changes the skill/panic base; driver and animation factors follow.',
                    'other_entries': 'Other declared-type, custom-naming, activation, media and capability-field entries do not match these two exact clothing declarations. General inventory management is excluded under the adopted scope.'}
                work = None
                residual = {'meaning': ('How the represented ReloadSpeed assignment changes actual action timing' if axis == 'operation' else
                                       'Native animation/event timing and exact equipment replacement conditions beyond the represented speed/wear predicates'),
                            'required_input': 'ReloadSpeed animation/event consumer and setWornItem equipment replacement for AmmoStrap',
                            'reason': 'The exact clothing, primary-hand selection and full local speed calculation are interpreted. The multiplier is expressed rather than withheld. Native animation timing and worn-item replacement remain distinct from the answered Lua guards; variable current skill or panic does not block the conditional calculation.'}
            elif (item in {'Base.Disinfectant', 'Base.AlcoholWipes', 'Base.AlcoholedCottonBalls'}
                    and fields.get('Type') == 'Drainable' and fields.get('UseWhileEquipped', '').lower() == 'false'
                    and set(fields) <= medical_fields and not conflicts
                    and any(f['item_id'] == item and f['payload'] == {'property': 'wound_alcohol_level', 'direction': 'increase'} for f in facts.values())
                    and any(f['item_id'] == item and f['payload'] == {'property': 'additional_pain', 'direction': 'increase'} for f in facts.values())):
                paths = {semantic.MENU, sources.HEALTH, sources.DISINFECT, sources.CONSOLIDATE}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'medical_drainable_consumers'
                applied['direct_scope'] = {
                    'declaration': {k: fields.get(k) for k in ('Type', 'AlcoholPower', 'UseDelta', 'UseWhileEquipped', 'ConsolidateOption', 'Tags')},
                    'health_handler': 'Positive AlcoholPower selects HDisinfect. The full unbandaged injury/stitch/splint predicate, inventory transfer, patient movement exceptions and action interruptions are interpreted.',
                    'state_assignments': 'ISDisinfect increases body-part alcohol level and uses the drainable once. Additional pain changes only for non-None access; that constructor branch fixes doctor level to 10. These are represented separately from clinical healing.',
                    'consolidation': 'The DrainableComboItem selection reaches checkConsolidate. canConsolidate gates same-type inventory lookup; another receiver must be below full and absent from the prior water-pour list. The action requires both items in inventory, linearly transfers at most min(remaining supply, receiver space), interrupts on walk/run, copies tainted-water state on a positive transfer, and uses a depleted donor. ConsolidateOption changes the label, not the eligibility predicate.',
                    'other_local_entries': 'The exact declaration has no other named item-specific capability field. Distinct key/map/food/literature/clothing/radio/weapon/token branches were compared with these declarations. General management is excluded under the adopted scope; absence of a declared capability is not promoted to a negative about native initialization.',
                    'separate_scopes': 'Recipe material participation and drainable depletion retain their crafting/expenditure results; they are not substituted for this direct result.'}
                work = None
                residual = {
                    'meaning': (['Native applicability and item matching of the represented conditional consolidation operation',
                                 'Clinical wound response beyond the represented alcohol/pain assignments',
                                 'Any direct capability initialized natively beyond this exact declaration'] if axis == 'operation' else
                                ['Native canConsolidate and short-type lookup eligibility for this medical drainable',
                                 'Native wound-response conditions beyond the represented treatment action',
                                 'Initialization conditions for direct capabilities not declared by this exact item']),
                    'required_input': 'DrainableComboItem.canConsolidate/type lookup and item initialization for ' + item + '; BodyPart alcohol-state evolution',
                    'reason': 'The selected medical declaration and available health/consolidation consumers have been interpreted through their state assignments and eligibility branches. Conditional consolidation is represented; remaining quantities and movement are answered conditions, not blockers. The missing native capability calculation, exact lookup/initialization and wound evolution are the remaining dependencies; the custom Merge label alone does not establish unconditional consolidation support.'}
            elif fields.get('Type') == 'Radio' and 'Type' not in conflicts:
                paths = {sources.CONTEXT_RADIO, sources.RADIO_WINDOW, sources.RADIO_CHANNEL, sources.TV_CHANNEL,
                         sources.RADIO_VOLUME, sources.RADIO_MIC, sources.RADIO_SIGNAL, sources.RADIO_MEDIA,
                           sources.RADIO_ACTION, sources.RADIO_INTERACTIONS, sources.RADIO_POWER, sources.RADIO_GRID,
                           sources.RADIO_PRESET_EDITOR, sources.RADIO_GENERAL, sources.CONTEXT_MOVABLE,
                           semantic.PROPS, sources.MOVE_CURSOR, semantic.MOVE_ACTION}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                features = []
                if fields.get('NoTransmit', '').lower() != 'true':
                    features.append('television program reception' if fields.get('IsTelevision', '').lower() == 'true' else 'radio signal reception')
                    if fields.get('TwoWay', '').lower() == 'true':
                        features.append('microphone pickup and two-way signal transmission')
                if fields.get('AcceptMediaType') in {'0', '1'}:
                    features.append('assigned recorded-media playback')
                if features:
                    applied['direct_rule'] = 'radio_controls_and_native_signal_path'
                    applied['direct_scope'] = {'fields': {k: fields.get(k) for k in ('Type', 'IsTelevision', 'TwoWay', 'NoTransmit', 'AcceptMediaType')},
                          'controls': 'Registered device panel, channel/volume/microphone setters, power toggling and battery insertion/removal are separately represented where applicable.',
                        'signal': 'RWMSignal reads isReceivingSignal; OnDeviceText receives already-delivered text/codes. These consumers do not define radio propagation or receiver delivery.',
                        'media': 'The media action delegates StartPlayMedia/StopPlayMedia to device data.'}
                    residual = {'meaning': features if axis == 'operation' else ['Eligibility and propagation/recording prerequisites of ' + feature for feature in features],
                                'required_input': 'The exact device-data signal or recorded-media dispatch implementation for ' + ', '.join(features),
                                'reason': 'The declared device subtype selects these unanswered propositions. Lua control setters and received-signal displays do not define the corresponding native propagation, pickup, delivery or recording execution. Current power/channel values are conditions of the answered controls, not an inability to describe those conditional controls.'}
                    if not conflicts and set(fields) <= sources.RADIO_FIELDS:
                        required = {'open_device_controls', 'adjust_device_volume', 'toggle_device_power'}
                        if fields.get('UsesBattery', '').lower() == 'true':
                            required |= {'insert_device_battery', 'remove_device_battery'}
                        if fields.get('IsTelevision', '').lower() == 'true':
                            required.add('select_tv_channel')
                        elif fields.get('NoTransmit', '').lower() != 'true':
                            required |= {'tune_radio', 'edit_radio_presets'}
                        if fields.get('TwoWay', '').lower() == 'true':
                            required.add('toggle_radio_microphone')
                        if fields.get('AcceptMediaType') in {'0', '1'}:
                            required.add('control_device_media')
                        if fields.get('IsPortable', '').lower() == 'true' and fields.get('IsTelevision', '').lower() == 'false':
                            required.add('control_device_headphones')
                        if fields.get('WorldObjectSprite'):
                            required.add('place_radio_world_form')
                        if required <= {f['payload'].get('function') for f in facts.values() if f['item_id'] == item}:
                            work = None
                            applied['direct_scope'].update(declaration=fields,
                                window_lifetime=sources.RADIO_WINDOW_LIFETIME,
                                presets=sources.RADIO_PRESETS if 'edit_radio_presets' in required else None,
                                media=sources.RADIO_MEDIA_CONTROL if 'control_device_media' in required else None,
                                headphones=sources.RADIO_HEADPHONE_CONTROL if 'control_device_headphones' in required else None,
                                world_form=sources.RADIO_WORLD_FORM if fields.get('WorldObjectSprite') else None,
                                delivered_codes=sources.RADIO_CODE_EFFECTS,
                                remaining_fields='Declared ranges, tier, condition, battery/use and sprite values require native device/sprite binding. No other special item selector or capability field is present in this complete declaration. General inventory/hotbar management is excluded; exact recipe salvage and assembly retain independent questions.')
                            residual.update(boundary_kind='examined_native_dependency',
                                required_input=residual['required_input'] + '; exact preset/device-data persistence, sprite-to-world-device conversion, inventory return identity and native OnDeviceText association/delivery',
                                reason='All active local panels, timed controls, preset editing and declared world-form paths are interpreted. The delivered-code Lua decoder, its player/GUID/cooldown guards and stat/XP/recipe requests are represented; remaining propagation, native state delivery and assignment are distinct from those local operations.')
            elif any(f['item_id'] == item and f['payload'] == {'function': 'insert_recorded_media'} for f in facts.values()):
                paths = {sources.CONTEXT_MEDIA, sources.MEDIA_LOADER, sources.MEDIA_DATA, sources.MEDIA_INFO,
                         sources.RADIO_MEDIA, sources.RADIO_ACTION}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'recorded_media_assignment_and_playback'
                applied['direct_scope'] = {'declared_category': fields.get('MediaCategory'),
                    'loader': 'The catalog category is registered with native RecordedMedia, including extra text and coded lines.',
                    'answered': 'Conditional label display and compatible-device insertion are represented.',
                    'handoff': 'addMediaItem and StartPlayMedia execute in device data; no exact recording is assigned by the item declaration alone.'}
                residual = {'meaning': ('Playback of this item assigned recording and its audiovisual/learning/mood consequences' if axis == 'operation' else
                                       'Native category-to-media-type assignment and actual playback/effect eligibility for the assigned recording'),
                            'required_input': 'RecordedMedia item assignment/type mapping and DeviceData recording execution for category ' + fields['MediaCategory'],
                            'reason': 'The source category joins a catalog and conditional UI controls, but the native assignment and recording executor select the actual content and deliver its lines/effects. A category label does not answer those exact propositions. Unknown current recording state does not invalidate the already described conditional controls.'}
                if (not conflicts and fields.get('Type') == 'Normal' and set(fields) <= {
                        'DisplayCategory', 'Type', 'DisplayName', 'Icon', 'Weight', 'MediaCategory', 'WorldStaticModel'}):
                    work = None
                    applied['direct_scope'].update(declaration=fields, delivered_codes=sources.RADIO_CODE_EFFECTS,
                        other_dispatch='The exact recorded-media Normal declaration has no water, weapon, wearable, medication, activation or writable field. Registered label/insertion and delivered-code consumers are represented; general inventory management is excluded.')
                    residual.update(boundary_kind='examined_native_dependency',
                        reason='Assigned recording identity and native playback delivery remain unestablished. The available local catalog, controls and post-delivery code effects are interpreted with their exact conditions; no generic category-to-recording or guaranteed learning effect is inferred.')
            elif item in {'Base.Headphones', 'Base.Earbuds'} and any(
                    f['item_id'] == item and f['payload'] == {'function': 'connect_radio_headphones'} for f in facts.values()):
                paths = {sources.RADIO_VOLUME, sources.RADIO_PANEL, sources.RADIO_WINDOW, sources.RADIO_ACTION}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'headphone_connection_and_audio'
                applied['direct_scope'] = {'connection': 'Exact FullType verification, portable nontelevision panel, empty slot, access and run interruption are represented.',
                    'native_call': 'ISRadioAction.performAddHeadphones -> DeviceData.addHeadphones(selected item)',
                    'distinction': 'A variable current power or volume value is not a blocker. The missing source defines how headphone routing and audible output use those states.'}
                residual = {'meaning': ('Listening through the connected headphone item' if axis == 'operation' else
                                       'Device compatibility, power/reception and routing prerequisites of audible headphone playback beyond the admitted connection action'),
                            'required_input': 'DeviceData.addHeadphones and native radio audio-routing/playback implementation for the exact headphone type',
                            'reason': 'The reviewed Lua performs the connection handoff and exposes volume/power controls. It does not define whether/how that exact headphone binding routes audible output, or the complete playback prerequisites. This concrete audio proposition remains unanswered; no current-state value is required to describe the already accepted conditional connection function.'}
                if not conflicts and fields.get('Type') == 'Normal' and set(fields) <= sources.PLAIN_OBJECT_FIELDS:
                    work = None
                    applied['direct_scope'].update(declaration=fields, removal=sources.RADIO_HEADPHONE_CONTROL,
                        other_dispatch='These exact Normal headphone declarations select the radio panel but no other item-specific typed capability. Recipe dismantling has independent questions, and general inventory management is excluded.')
                    residual.update(boundary_kind='examined_native_dependency')
            elif fields.get('Type') in {'AlarmClock', 'AlarmClockClothing'} and 'Type' not in conflicts:
                paths = {semantic.MENU, sources.ALARM_DIALOG, sources.ALARM_STOP,
                         sources.CLOCK_PROMPT, sources.CLOCK_CHARACTER, sources.CLOTHING_EXTRA,
                         semantic.WEAR, sources.BODY_LOCATIONS}
                refs = sorted(set(refs) | {r for r, o in observations.items() if o['source_path'] in paths})
                applied['direct_rule'] = 'clock_display_binding'
                applied['direct_scope'] = {'declaration_type': fields['Type'], 'tags': fields.get('Tags'),
                    'alarm': 'Digital alarm set/stop dispatch is separately represented where its declared predicate is supported.',
                    'clock_ui': 'ButtonPrompt reads native clock visibility/geometry; CharacterScreen uses native isDateVisible for survival-time text. Neither links an exact inventory clock to time display.'}
                residual = {'meaning': ('Whether this exact clock form provides time-display access beyond its admitted alarm operations' if axis == 'operation' else
                                       'The held/worn/inventory selection rule enabling time display for this exact clock form'),
                            'required_input': 'UIManager Clock item-selection and display-eligibility implementation for the declared AlarmClock or AlarmClockClothing form',
                            'reason': 'The local UI consumers read the native clock state without specifying which item form enables it. The missing item-to-display selection rule blocks this exact proposition; a variable current time or alarm setting does not block description of conditional alarm operations.'}
                clock_fields = {'DisplayCategory', 'Type', 'DisplayName', 'ClothingItem', 'BodyLocation', 'Icon',
                                'Weight', 'ClothingItemExtra', 'ClothingItemExtraOption', 'clothingExtraSubmenu',
                                'Cosmetic', 'AlarmSound', 'SoundRadius', 'MetalValue', 'WorldStaticModel', 'Tags', 'Obsolete'}
                item_payloads = [f['payload'] for f in facts.values() if f['item_id'] == item]
                if (not conflicts and set(fields) <= clock_fields
                        and (not fields.get('ClothingItemExtra') or {'function': 'switch_declared_clothing_form'} in item_payloads)):
                    work = None
                    applied['direct_scope']['reviewed_local_controls'] = 'The complete declaration joins set/stop, worn-location and paired wrist-form consumers. Dialog position cancellation and the missing-player/alarm-square immediate-stop exception are represented. No other capability field or attachment-slot provider is declared; general inventory management is excluded.'
                    applied['direct_scope']['variant_and_salvage'] = 'Declared wrist variants retain actual copied alarm/appearance state and destination constraints. Any recipe dismantling operation has its independently represented callback and crafting scope; these do not prove native clock display or ringing.'
                    residual = {'meaning': ('Exact item-to-time-display binding, digital-menu eligibility and alarm sound execution' if axis == 'operation' else
                                           'Native display selection, isDigital eligibility, alarm triggering and destination wrist-form initialization conditions'),
                                'required_input': 'UIManager Clock item selection; AlarmClock/AlarmClockClothing isDigital and ringing implementation; declared alternate-form factory initialization' + ('; Obsolete item availability' if fields.get('Obsolete', '').lower() == 'true' else ''),
                                'reason': 'The exact local control and paired-wrist consumers are interpreted and expressed. Tags and type are retained as declarations, not substituted for isDigital. Native display/sound and destination initialization remain separate; clock time, position and alarm settings are answered conditional inputs rather than blockers.'}
        elif scope == 'activity:ingestion':
            residual = {'meaning': ('native consumption state changes' if axis in {'operation', 'effects'} else 'conditions that change the native consumption effects'),
                        'required_input': 'IsoGameCharacter.Eat interpretation for the listed food fields and any OnEat callback dispatch',
                        'reason': 'ISEatFoodAction checks inventory/companions/start state, then delegates nutrition and food-state effects to character:Eat; field signs alone do not establish all applied changes.'}
            if fields.get('CustomContextMenu', '') not in {'', 'Drink'} or fields.get('CustomMenuOption'):
                item_facts = [f for f in facts.values() if f['item_id'] == item]
                if any(f['payload'].get('function') in {'smoke_cigarette', 'take_food_medicine'} for f in item_facts):
                    applied['custom_consumption'] = {
                        'label': fields.get('CustomContextMenu'), 'callback': fields.get('OnEat'),
                        'meaning': 'Custom label shares native food dispatch; admitted smoking/taking and explicit callback effects retain their own qualifiers. Other Eat/ReduceInfectionPower effects remain engine-owned.'}
                else:
                    work = 'Interpret this exact custom consumption label/callback before completing its local operation and conditions.'
        elif scope == 'activity:reading':
            item_payloads = [f['payload'] for f in facts.values() if f['item_id'] == item]
            if (fields.get('SkillTrained') and not fields.get('TeachedRecipes')
                    and {'property': 'reading_page_progress', 'direction': 'update'} in item_payloads
                    and {'property': fields['SkillTrained'] + '_experience_multiplier', 'direction': 'increase'} in item_payloads):
                terminal_reason = ('The registered skill-book branch records/resets page progress and conditionally increases its skill multiplier. '
                                   'The native entry, literacy, skill/page/driving conditions and progress/multiplier restrictions are bound facts; '
                                   'the non-skill ReadLiterature branch is not invoked for this book.')
                if axis == 'conditions' and fields.get('LvlSkillTrained') and fields.get('NumLevelsTrained'):
                    terminal_reason = None
                    applied['skill_level_consumer'] = {
                        'lower_level': fields['LvlSkillTrained'], 'level_count': fields['NumLevelsTrained'],
                        'comparison': 'getLvlSkillTrained <= current perk level + 1 <= getMaxLevelTrained',
                        'effect_arguments': 'addXpMultiplier receives the two level getters',
                        'source': semantic.READ}
                    residual = {'meaning': 'The numeric upper endpoint of the supported skill-level interval for ' + fields['SkillTrained'],
                                'required_input': 'Literature.getMaxLevelTrained mapping of the exact LvlSkillTrained/NumLevelsTrained declaration',
                                'reason': 'The Lua lower/upper comparisons and multiplier dispatch have been interpreted, and their conditional behavior is represented. The native maximum-level getter is consumed rather than calculated in this source; its exact numeric mapping remains separate from the answered literacy, progress, possession and driving conditions.'}
            elif fields.get('SkillTrained'):
                residual = {'meaning': 'reading progress and skill-book conditions beyond the accepted multiplier facts',
                            'required_input': semantic.READ,
                            'reason': 'The Lua action records page progress and evaluates skill levels; these available branches must be represented before whole-scope closure.'}
                work = 'Admit and compose the remaining page-progress/reading-condition meanings from the bound action.'
            else:
                residual = {'meaning': ('non-skill literature effects' if axis in {'operation', 'effects'} else 'conditions changing non-skill literature effects'),
                            'required_input': 'IsoGameCharacter.ReadLiterature and recipe-learning dispatch for the exact declared fields',
                            'reason': 'The non-skill branch calls ReadLiterature; the bound Lua call does not define mood or learned-recipe changes.'}
        elif scope == 'activity:wearing':
            location = fields.get('BodyLocation', fields.get('CanBeEquipped'))
            applied['location_relations'] = {
                'location': location,
                'exclusive_declarations': [list(p) for p in exclusive_pairs if location in p],
                'hidden_model_declarations': [list(p) for p in hidden_pairs if location in p],
                'source': base['reader'].bindings[sources.BODY_LOCATIONS],
                'consumer_handoff': 'ISWearClothing.perform: character:setWornItem(location, item)',
            }
            if item in base.get('unsupported_wear', {}):
                applied['unsupported_location'] = base['unsupported_wear'][item]
                residual = {'meaning': 'wearing behavior at ' + fields['BodyLocation'],
                            'required_input': 'a verified runtime registration/interpretation for the obsolete declaration location ' + fields['BodyLocation'],
                            'reason': base['unsupported_wear'][item]['reason']}
            elif axis == 'operation' and any(f['payload'].get('state') == 'worn_location' for f in related):
                terminal_reason = 'The exact registered BodyLocation is passed to setWornItem by the native wear action; accepted wear/location facts answer the item operation. Protection and insulation are not inferred.'
            else:
                residual = {'meaning': 'runtime replacement and visual handling of the listed conflicting equipment locations',
                            'required_input': 'setWornItem/BodyLocationGroup interpretation for the exact location relations',
                            'reason': 'The raw location relation declarations and native inventory/action conditions were examined. Lua delegates actual replacement to setWornItem; tooltip replacement predictions are not fact-admission evidence.',
                            'exact_location_relations': applied['location_relations']}
                if not any(f['payload'] == {'predicate': sources.WEAR_ACTION} for f in related):
                    work = 'Bind the native wear-action conditions for this exact equipment form.'
        elif scope == 'activity:storage':
            residual = {'meaning': ('container acceptance/removal behavior' if axis == 'operation' else 'item admission and removal conditions'),
                        'required_input': 'container isItemAllowed/isRemoveItemAllowed interpretation and any exact AcceptItemFunction',
                        'reason': 'Transfer code proves conditional storage but delegates item admission/removal; the exact Capacity and acceptance fields above determine the unresolved question.'}
        elif scope == 'activity:combat':
            residual = {'meaning': ('attack outcome and affected state' if axis == 'operation' else 'target/hit and attack-effect conditions'),
                        'required_input': 'DoAttack/WeaponHit or IsoTrap interpretation for the exact weapon declaration',
                        'reason': 'Admitted firing/tree-use facts are bounded. Hit, damage and trap state changes are not defined by the attack dispatch calls.'}
        elif scope == 'activity:expenditure':
            residual = {'meaning': 'depletion/replacement outcome' if axis == 'operation' else 'conditions of depletion and replacement',
                        'required_input': 'InventoryItem.Use and the exact ReplaceOnDeplete dispatch',
                        'reason': 'Any accepted water effects remain supported; depletion and replacement are a separate engine handoff for the declared drainable form.'}
        else:
            finding = attempt['finding']
            if scope == 'activity:crafting':
                local = finding.get('participants', [])
                meaning = 'roles of the exact consumed/kept/result participants' if axis == 'role' else 'eligibility and callback conditions of those exact recipe participants'
                work = 'Lower the reviewed exact recipe participation to context-local roles/conditions where supported; keep is not automatically a tool.'
            elif scope == 'activity:cooking':
                local = {k: finding.get(k) for k in ('declared_entries', 'base_or_result_refs')}
                applied['previous_declared_entries'] = local['declared_entries']
                local['declared_entries'] = fields.get('EvolvedRecipe')
                applied['current_declared_entries'] = local['declared_entries']
                meaning = 'ingredient/base/result role' if axis == 'role' else 'accepted ingredient and food-state restrictions'
                work = 'Reconcile exact ingredient versus base/result membership and its caller filters before whole-scope closure.'
            else:
                local = {k: finding.get(k) for k in ('fixing', 'stages', 'building_candidates', 'moveable_tools')}
                meaning = 'context-local repair/construction/moveable roles' if axis == 'role' else 'conditions of those exact world-work participants'
                work = 'Reconcile each listed exact fixing/stage/tool relation with its already interpreted consumer and accepted facts.'
            residual = {'meaning': meaning, 'required_input': CONSUMERS[scope],
                        'reason': 'The exact participation is evidence for this axis; remaining local interpretation is explicitly unfinished, not a generic route-wide engine blocker.',
                        'exact_participation': local}
            if scope == 'activity:cooking':
                item_facts = [f for f in facts.values() if f['item_id'] == item]
                ingredient = any(f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'ingredient'}
                                 and facts[f['context_fact_ref']]['payload'] == {'activity': 'food_preparation'}
                                 for f in item_facts)
                conditions = any(f['payload'] == {'predicate': sources.COOKING_ACTION} for f in item_facts)
                ingredient_ok = (not local['declared_entries'] or (ingredient and conditions
                                 and fields.get('EvolvedRecipe') == local['declared_entries']
                                 and 'EvolvedRecipe' not in conflicts))
                base_relations = base.get('cooking_base_relations', {}).get(item, [])
                base_ok = all(any(r['path'] == observations[ref]['source_path']
                                 and r['clauses'] == observations[ref]['content'].get('clauses')
                                 for r in base_relations) for ref in local['base_or_result_refs'])
                if local['base_or_result_refs']:
                    base_ok = base_ok and any(f['payload'] == {'predicate': sources.COOKING_BASE} for f in item_facts)
                    applied['base_and_result_relations'] = base_relations
                if ingredient_ok and base_ok and (ingredient or base_relations):
                    work = None
                    residual.update(required_input='EvolvedRecipe.getEvolvedRecipe/getItemsCanBeUse/needToBeCooked/addItem for the exact declared roles',
                                    reason='Ingredient entries and each BaseItem/ResultItem relation are separately reconciled to accepted context-local roles and caller/action conditions. The explicit isResultItem continuation branch supports adding to prepared food; output membership alone is not treated as a use. Runtime food eligibility and transformation remain at the named engine methods. Source inventory, poisoning-policy and frozen/cooked filters were examined.')
            elif scope == 'activity:world_work':
                item_facts = [f for f in facts.values() if f['item_id'] == item]
                repairs = [f for f in item_facts if f['fact_kind'] == 'context_role'
                           and facts[f['context_fact_ref']]['payload'] == {'activity': 'repair'}]
                interpreted = []
                for link in local['fixing']:
                    original = observations[link['observation_ref']]
                    matching = [f for f in repairs if f['payload'] == {'role': link['role']}
                                and any(o == link['observation_ref'] or (
                                    observations[o]['source_path'] == original['source_path']
                                    and observations[o]['source_sha256'] == original['source_sha256']
                                    and original['content'].get('raw')
                                    and observations[o]['content'].get('raw', '').replace('\r\n', '\n') == original['content']['raw'].replace('\r\n', '\n'))
                                    for p in f['provenance_refs'] for o in payload['provenance'][p]['observation_refs'])]
                    if matching:
                        interpreted.append({'observation_ref': link['observation_ref'], 'role': link['role'],
                                            'role_fact_refs': sorted(f['fact_id'] for f in matching)})
                fixing_ok = len(interpreted) == len(local['fixing']) and (not local['fixing'] or
                            any(f['payload'] == {'predicate': sources.FIXING_ACTION} for f in item_facts))
                tool_relations = base.get('moveable_tool_relations', {}).get(item, [])
                tools_ok = all(any(all(r.get(k) == link.get(k) for k in ('definition', 'token', 'tag'))
                                  for r in tool_relations) for link in local['moveable_tools'])
                if local['moveable_tools']:
                    tools_ok = tools_ok and any(f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'tool'}
                                                and facts[f['context_fact_ref']]['payload'] == {'activity': 'moving_furniture'}
                                                for f in item_facts)
                    applied['interpreted_moveable_tools'] = tool_relations
                construction_roles = [f for f in item_facts if f['fact_kind'] == 'context_role'
                                      and facts[f['context_fact_ref']]['payload'] == {'activity': 'construction'}]
                interpreted_stages = []
                for link in local['stages']:
                    matching = [f for f in construction_roles if f['payload'] == {'role': link['role']}
                                and link['observation_ref'] in {
                                    o for p in f['provenance_refs'] for o in payload['provenance'][p]['observation_refs']}]
                    if matching:
                        interpreted_stages.append({'observation_ref': link['observation_ref'], 'role': link['role'],
                                                   'role_fact_refs': sorted(f['fact_id'] for f in matching)})
                stages_ok = len(interpreted_stages) == len(local['stages']) and (not local['stages'] or
                            any(f['payload'] == {'predicate': sources.STAGE_ACTION} for f in item_facts))
                interpreted_building = []
                for ref in local['building_candidates']:
                    factory = observations[ref]['content']['factory']
                    relation = next((r for r in base.get('factory_relations', {}).get(item, [])
                                     if r['observation_ref'] == ref), None)
                    if relation is not None:
                        role = facts.get(relation.get('role_fact_ref'))
                        if (relation['status'] == 'active_welding' and role and role['payload'] == {'role': relation['role']}
                                and facts[role['context_fact_ref']]['payload'] == {'activity': 'metal_welding_construction'}
                                and any(f['payload'] == {'predicate': sources.WELDING_CONSTRUCTION} for f in item_facts)):
                            interpreted_building.append(deepcopy(relation))
                            continue
                        if relation['status'] == 'no_active_menu_reference' or (
                                role and role['payload'] == {'role': 'material'}
                                and facts[role['context_fact_ref']]['payload'] == {'activity': 'carpentry_menu_construction'}
                                and any(f['payload'] == {'predicate': sources.CARPENTRY_MATERIAL} for f in item_facts)):
                            interpreted_building.append(deepcopy(relation))
                            continue
                    if factory in {'ISBuildMenu.onLogWall', 'ISBuildMenu.onWoodenCross'}:
                        matching = [f for f in construction_roles if f['payload'] == {'role': 'material'}
                                    and any(payload['provenance'][p]['rule_ref'] == 'construction' for p in f['provenance_refs'])]
                        if matching:
                            interpreted_building.append({'observation_ref': ref, 'factory': factory,
                                                         'role_fact_refs': sorted(f['fact_id'] for f in matching)})
                building_ok = len(interpreted_building) == len(local['building_candidates'])
                applied['interpreted_stage_relations'] = interpreted_stages
                applied['interpreted_building_relations'] = interpreted_building
                if fixing_ok and tools_ok and stages_ok and building_ok and any(local.values()):
                    applied['interpreted_fixing_relations'] = interpreted
                    work = None
                    boundaries = []
                    if local['fixing']:
                        boundaries.append('FixingManager runtime selection, consumption and repair outcome')
                    if local['moveable_tools']:
                        boundaries.append('object-specific pickup/place properties and permission state')
                    if local['stages']:
                        boundaries.append('MultiStageBuilding selection and doStage outcome for the exact previous-stage/skill declarations')
                    if local['building_candidates']:
                        boundaries.append('world placement, availability and runtime object construction for the exact active factory branches')
                    residual.update(required_input='; '.join(boundaries),
                                    reason='Every listed fixing, tool, stage and active-factory relation is reconciled separately to its scoped role and conditions. Repair inventory/vehicle exceptions, actual moveable FullType/tag membership, stage start/interruption/consumption and log-wall binding alternatives are retained where applicable. The named runtime selection or object-result boundary remains; no listed local relation is hidden by that boundary.')
            elif scope == 'activity:crafting':
                group_context = {'Recipe.GetItemTypes.CraftSheetRope': 'sheet_rope_making',
                                 'Recipe.GetItemTypes.RipSheets': 'fabric_recovery',
                                 'Recipe.GetItemTypes.RipClothing_Cotton': 'fabric_recovery',
                                 'Recipe.GetItemTypes.RipClothing_Denim': 'fabric_recovery',
                                 'Recipe.GetItemTypes.RipClothing_Leather': 'fabric_recovery'}
                interpreted = []
                crafting_roles = [f for f in facts.values() if f['item_id'] == item and f['fact_kind'] == 'context_role']
                material_roles = [f for f in facts.values() if f['item_id'] == item and f['fact_kind'] == 'context_role'
                                  and f['payload'] == {'role': 'material'}]
                opening_functions = [f for f in facts.values() if f['item_id'] == item
                                     and f['fact_kind'] in {'direct_function', 'context_role'}
                                     and any(payload['provenance'][p]['rule_ref'] in {'package_opening', 'umbrella_form', 'battery_receiver', 'electronic_salvage', 'radio_crafting', 'material_assembly'}
                                             for p in f['provenance_refs'])]
                for link in local:
                    if link['role'] == 'result':
                        interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'],
                                            'disposition': 'transformation output; not an intrinsic crafting-use role'})
                        continue
                    original = observations[link['observation_ref']]
                    baking = [f for f in crafting_roles if any(
                        payload['provenance'][p].get('contributor_rule_ref', payload['provenance'][p]['rule_ref']) in {'baking_preparation', 'bandage_materials', 'spear_crafting', 'fabric_conditions', 'smithing_parts', 'box_packing', 'bowl_portioning', 'seed_packing', 'jar_preparation', 'bandage_washing', 'crop_spray_preparation', 'camping_kit_preparation', 'shovel_smithing', 'poultice_preparation', 'metal_forging', 'welded_parts', 'log_binding', 'mattress_preparation', 'frog_preparation', 'wire_recovery', 'food_preparation_recipes', 'item_transformation_recipes'}
                        and any(observations[o]['source_path'] == original['source_path']
                                and observations[o]['source_sha256'] == original['source_sha256']
                                and observations[o]['content'].get('clauses') == original['content'].get('clauses')
                                for o in payload['provenance'][p]['observation_refs'])
                        for p in f['provenance_refs'])]
                    if baking:
                        interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'],
                                            'role_fact_refs': sorted(f['fact_id'] for f in baking),
                                            'disposition': 'Exact reviewed preparation role and conditions from its complete recipe clauses; raw numeric semantics remain native residual, without semicolon conversion.'})
                        continue
                    if link.get('numeric_suffix') or link.get('import_resolution'):
                        continue  # Unreviewed identity admission alone never resolves a role.
                    # These are already admitted, recipe-specific roles. Join
                    # their own provenance rather than generalizing input/keep.
                    established = []
                    for fact in crafting_roles:
                        activity = facts[fact['context_fact_ref']]['payload'].get('activity')
                        expected = None
                        if activity == 'woodworking' and link['role'] in {'input', 'keep'}:
                            expected = ('woodwork', 'tool' if link['role'] == 'keep' else 'material')
                        elif activity == 'portable_device_power' and link['role'] == 'destroy':
                            expected = ('battery_supply', 'power_supply')
                        if expected and fact['payload'] == {'role': expected[1]} and any(
                                payload['provenance'][p]['rule_ref'] == expected[0]
                                and link['observation_ref'] in payload['provenance'][p]['observation_refs']
                                for p in fact['provenance_refs']):
                            established.append(fact['fact_id'])
                    if established:
                        interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'],
                                            'role_fact_refs': sorted(established),
                                            'disposition': 'existing recipe-specific role with its bound eligibility condition'})
                        continue
                    opening = [f for f in opening_functions if any(
                        observations[o]['source_path'] == original['source_path']
                        and observations[o]['source_sha256'] == original['source_sha256']
                        and original['content'].get('clauses')
                        and observations[o]['content'].get('clauses') == original['content']['clauses']
                        for p in f['provenance_refs'] for o in payload['provenance'][p]['observation_refs'])]
                    if opening and (link['role'] in {'input', 'destroy'} or (
                            link['role'] == 'keep' and (link.get('group') in {'Recipe.GetItemTypes.CanOpener', 'Recipe.GetItemTypes.Screwdriver'}
                            or any(f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'tool'}
                                   and any(payload['provenance'][p]['rule_ref'] == 'material_assembly' for p in f['provenance_refs'])
                                   for f in opening)))):
                        interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'],
                                            'transformation_fact_refs': sorted(f['fact_id'] for f in opening),
                                            'disposition': 'reviewed transformation participant with its accepted eligibility conditions'})
                        continue
                    context = group_context.get(link.get('group'))
                    matching = [f for f in material_roles if facts[f['context_fact_ref']]['payload'] == {'activity': context}
                                and link['observation_ref'] in {
                                    obs for p in f['provenance_refs'] for obs in payload['provenance'][p]['observation_refs']}]
                    # Recovery uses a more precise locator and retains CRLF;
                    # join the same bound source and complete parsed clauses.
                    if context == 'sheet_rope_making' and not matching:
                        original = observations[link['observation_ref']]
                        clauses = original['content'].get('clauses')
                        matching = [f for f in material_roles if facts[f['context_fact_ref']]['payload'] == {'activity': context}
                                    and clauses and any(observations[o]['content'].get('clauses') == clauses
                                        and observations[o]['source_path'] == original['source_path']
                                        and observations[o]['source_sha256'] == original['source_sha256']
                                        for p in f['provenance_refs'] for o in payload['provenance'][p]['observation_refs'])]
                    if link['role'] == 'input' and matching:
                        interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'], 'group': link['group'],
                                            'role_fact_refs': sorted(f['fact_id'] for f in matching)})
                # Preserve completed per-relation work even when another
                # recipe for the same item still needs local interpretation.
                applied['interpreted_material_relations'] = interpreted
                suffixes = [deepcopy(link) for link in local if link.get('numeric_suffix')]
                if suffixes:
                    residual['uninterpreted_participation'] = suffixes
                    residual['numeric_semantics'] = 'Raw numeric operands, including their separator and spacing, are preserved; participation recovery does not infer consumption amounts or translate semicolon semantics into equals semantics.'
                imports = [deepcopy(link) for link in local if link.get('import_resolution')]
                if imports:
                    residual['imported_participation'] = imports
                    residual['import_semantics'] = 'Explicit import headers bind unique absent-local source identities; native runtime module resolution and participant selection remain separate from this source participation admission.'
                if local and len(interpreted) == len(local) and any(link['role'] != 'result' for link in local):
                    work = None
                    residual.update(required_input='RecipeManager runtime eligibility/selection/consumption for the exact reconciled recipes',
                                    reason='Every listed input, destroy or kept participant is reconciled to a source-bound material role or an explicitly reviewed transformation function and its conditions. Fabric recipes retain their fabric/state restrictions; package opening retains any CanOpener requirement; umbrella form changes and battery receivers retain their callback conditions. Result clauses are acquisition leads rather than intrinsic-use evidence. No arbitrary keep-to-tool inference is made. Runtime recipe eligibility and selected material state remain unresolved.')
                elif local and all(link['role'] == 'result' for link in local):
                    applied['output_only_relations'] = [
                        {'observation_ref': link['observation_ref'], 'clause': link['clause'],
                         'disposition': 'transformation output; not an intrinsic crafting-use role'} for link in local]
                    work = None
                    residual.update(required_input='Runtime recipe-group membership and RecipeManager participant selection beyond the exact output-only observations',
                                    reason='Every exact known participation for this item is a result clause. These observations describe how the item is produced; they do not establish a material/tool use or its conditions. No output role is relabeled as an intrinsic function. The supplied partial group expansion does not prove that runtime groups add no further input participation, so whole-scope N/A is not claimed.',
                                    parser_boundary='parser_limits/recipe_opaque and runtime group registration')
        if scope == 'item:direct' and item in base.get('heat_control_sources', {}):
            heat = base['heat_control_sources'][item]
            applied['shared_heat_controls'] = {'functions': heat['functions'], 'predicates': heat['predicates']}
            refs = sorted(set(refs) | set(heat['observation_refs']))
            if residual is not None:
                residual['additional_heat_boundary'] = 'Native target binding, fire/heat state and delivery remain separate from the interpreted fuel, tinder or ignition action; explicit source arithmetic and inactive client branches remain attached.'
        if scope == 'item:direct' and item in base.get('equipment_control_sources', {}):
            equipment = base['equipment_control_sources'][item]
            applied['shared_equipment_controls'] = {'functions': equipment['functions'], 'predicates': equipment['predicates']}
            refs = sorted(set(refs) | set(equipment['observation_refs']))
            if residual is not None:
                residual['additional_equipment_boundary'] = 'Native object/part binding, world mutation and inventory delivery remain separate from the exact additional equipment actions; their source-specific continued-validity and interruption rules are retained.'
        if applied.get('shared_garment_patching') and residual is not None:
            residual['additional_examined_dependency'] = applied['shared_garment_patching']['native_boundary']
        row.update(attribution_status='attribution_failure' if failure else 'attributed',
                   attribution_rule_ref='question_scope/1/' + scope + '/' + axis,
                   applied_inputs=applied, direct_evidence_refs=refs,
                   accepted_partial_fact_refs=partial_refs, answered_scope=answered,
                   remaining_scope=[] if terminal_reason else [residual], remaining_work=work,
                   effective_blocker_refs=[])
        if terminal_reason:
            if result['state'] != 'evidence_backed_not_applicable':
                result.update(state='resolved', fact_refs=partial_refs)
                for binding in by_question[key]:
                    binding['contribution'] = 'whole_scope'
            result.update(question_coverage='whole_scope', coverage_justification=terminal_reason,
                          blockers=[], next_source_dependency=None, transition_reason=terminal_reason)
            row['whole_scope_reason'] = terminal_reason
        else:
            blocker = model.identity('residual', [list(key), residual])
            row['effective_blocker_refs'] = [{'ref': blocker, 'remaining_scope': residual,
                                              'evidence_refs': refs, 'reason': residual['reason']}]
            result.update(state='investigated_unresolved', fact_refs=[], question_coverage='partial',
                          blockers=[blocker], next_source_dependency=residual['required_input'],
                          transition_reason=residual['reason'])
        row['successor_result'] = deepcopy(result)
    return audit


def reconcile_direct_claims(base, payload, audit, inventory):
    """Finish only the predecessor comparison named by the direct local work.

    Use the actual migrated clauses and their source adjudications. No result is
    made terminal, and a route's empty unfinished list alone is insufficient.
    """
    claims = defaultdict(list)
    unsegmented = defaultdict(list)
    for claim in inventory['claims']:
        claims[claim['item_id']].append(claim)
    for clause in inventory['clauses']:
        if clause['classification'] == 'unsegmented':
            unsegmented[clause['item_id']].append({'locale': clause['locale'], 'span': clause['span']})
    conservation = {c['predecessor_claim_id']: c for c in inventory['conservation']}
    for row in audit:
        key = tuple(row['question_key'])
        if key[2] != 'item:direct' or row['attribution_status'] != 'attributed' or not row.get('remaining_work'):
            continue
        item_claims = claims[key[0]]
        compared = []
        for claim in item_claims:
            conserved = conservation.get(claim['predecessor_claim_id'], {})
            if (claim['migration_disposition'] != 'pending_investigation' and not claim.get('remaining_work')
                    and conserved.get('conservation_status') in {'conserved', 'responsibility_removed', 'bounded_unresolved'}):
                compared.append({'claim_ref': claim['predecessor_claim_id'], 'meaning': claim.get('meaning'),
                                 'disposition': claim['migration_disposition'],
                                 'fact_refs': claim['candidate_successor_fact_refs'],
                                 'source_refs': claim['verified_source_refs'],
                                 'remaining_uncertainty': claim['remaining_uncertainty']})
        row['applied_inputs']['predecessor_comparison'] = {
            'compared': compared, 'unsegmented_surfaces': unsegmented[key[0]],
            'pending_claim_refs': sorted(c['predecessor_claim_id'] for c in item_claims
                                        if c['predecessor_claim_id'] not in {v['claim_ref'] for v in compared})}
        records = base['declarations'].get(key[0], [])
        if len(records) != 1 or sources.stable_properties(records[0])[1]:
            continue
        attempt = payload['attempts'][row['applied_inputs']['route_observation_ref']]
        if (not item_claims or len(compared) != len(item_claims) or unsegmented[key[0]]
                or attempt['unfinished_semantic_paths']):
            continue
        row['applied_inputs']['predecessor_comparison']['completion'] = 'complete'
        row['remaining_work'] = ('Predecessor comparison is complete. Independently establish which additional exact '
                                 'operation or condition propositions remain unanswered and which source dependency '
                                 'actually blocks each; conditional behavior must not be blocked merely by unknown current state.')
