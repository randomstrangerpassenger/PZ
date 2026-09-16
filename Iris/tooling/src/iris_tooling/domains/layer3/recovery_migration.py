"""Predecessor claim adjudication; extraction remains a separate responsibility."""
from .recovery_claims import (
    re,
    defaultdict,
    model,
    sources,
    semantic,
    acquisition_expression,
    LEARNING_TOPICS,
    CLAUSES,
    PLACES,
    DISPLAY_LABELS,
    discovery_places,
    SKILLS,
    WEAR_PHRASES,
    spans,
    IDENTITY_MEANINGS,
    interpret,
    extract,
    WEAR_LOCATIONS,
    CLOTHING_LABEL_LOCATIONS,
    PREPARATION_ROLES,
)


def adjudicate(base, inventory, descriptions, semantic_payload):
    """Join reviewed atoms to source-admitted facts, never to similar prose.

    Unsupported atoms stay pending unless an actual bounded source boundary
    has been investigated. No item-level fallback can classify all its claims.
    """
    facts = {f['ref']: f for f in descriptions['facts']}
    per_item = defaultdict(list)
    for fact in facts.values():
        per_item[fact['item_id']].append(fact)
    previous = {(f['item_id'], f['fact_id']) for f in base['expression']['facts']}
    items = {i['item_id']: i for i in descriptions['items']}
    conservation = []
    source_assessments = {}
    # Reuse the actual reviewed transformation evidence. Output clauses stay
    # acquisition leads; source-confirmed input use cannot prove native output
    # identity. Each selected route retains its own local work; unrelated
    # alternatives do not block an existential claim about this route.
    reviewed_results = defaultdict(dict)
    result_recipes = defaultdict(set)
    recipe_outputs = {}
    for trace in base['acquisition']['traces'].values():
        if trace['family'] != 'transformation':
            continue
        clauses = trace.get('conditions', [])
        results = [c.split(':', 1)[1].strip().split('=')[0] for c in clauses if c.startswith('Result:')]
        if len(results) == 1:
            output = results[0] if '.' in results[0] else trace['module'] + '.' + results[0]
            key = (trace['source_path'], tuple(clauses))
            result_recipes[output].add(key)
            recipe_outputs.setdefault(key, set()).add(output)
    observations = semantic_payload['observations']
    semantic_facts = {f['fact_id']: f for f in semantic_payload['facts']}

    def has_recipe(fact, names):
        source = semantic_facts.get(fact['fact_id'])
        return bool(source and any(
            observations[o]['content'].get('recipe_name') in names
            or observations[o]['locator'].rsplit(':', 1)[-1].removeprefix('Base.') in names
            for p in source['provenance_refs']
            for o in semantic_payload['provenance'][p]['observation_refs']
            if observations[o]['content'].get('clauses')))

    for fact in semantic_payload['facts']:
        if fact['fact_kind'] not in {'direct_function', 'context_role'}:
            continue
        for pref in fact['provenance_refs']:
            provenance = semantic_payload['provenance'][pref]
            rule = provenance.get('contributor_rule_ref', provenance['rule_ref'])
            processes = set()
            if rule in {'radio_crafting', 'material_assembly', 'spear_crafting', 'woodwork'}:
                processes.add('craft')
            if rule in {'food_preparation_recipes', 'baking_preparation', 'frog_preparation'}:
                processes.add('prepare_food')
            if rule == 'item_transformation_recipes':
                processes.add('reviewed_transformation')
            if rule == 'seed_packing':
                processes.update({'pack_seeds', 'package_seeds'})
            if rule == 'log_binding':
                processes.add('tie_logs')
            if rule == 'bandage_materials':
                processes.add('prepare_bandaging_material')
            if rule == 'fabric_recovery':
                processes.add('recover_registered_fabric')
            if rule == 'sheet_rope':
                processes.add('craft_sheet_rope_from_sheet_or_cotton')
            if rule in {'smithing_parts', 'shovel_smithing', 'metal_forging', 'welded_parts'}:
                processes.add('metalworking')
            if rule == 'camping_kit_preparation':
                processes.add('craft')
            if rule == 'poultice_preparation':
                processes.add('process_medicinal_plants')
            if rule == 'jar_preparation':
                processes.add('jar_food')
            if rule == 'crop_spray_preparation':
                processes.add('assemble_gardening_spray')
            if rule == 'box_packing':
                processes.add('box_ammunition')
            if rule == 'bowl_portioning':
                processes.add('put_food_or_ingredients_in_bowl_or_pot')
            if rule in {'radio_crafting', 'electronic_salvage'}:
                processes.add('process_electronic_parts')
            if rule == 'package_opening':
                processes.add('reviewed_transformation')
                method = fact['payload'].get('function')
                process = {'unpack_ammunition': 'open_ammunition_box', 'unpack_seeds': 'open_seed_packet',
                           'unpack_canned_food': 'open_canned_food', 'unpack_eggs': 'open_egg_carton'}.get(method)
                if process:
                    processes.add(process)
            if not processes:
                continue
            for oid in provenance['observation_refs']:
                observation = observations[oid]
                clauses = observation['content'].get('clauses', [])
                result = [c.split(':', 1)[1].strip().split('=')[0] for c in clauses if c.startswith('Result:')]
                if len(result) != 1:
                    continue
                key = (observation['source_path'], tuple(clauses))
                outputs = recipe_outputs.get(key, set())
                if len(outputs) != 1:
                    continue
                output = next(iter(outputs))
                entry = reviewed_results[output].setdefault(key, {'observation_ref': oid, 'processes': set(), 'source_paths': set()})
                entry['processes'].update(processes)
                if rule == 'metal_forging' and output in {'Base.Bullets9mm', 'Base.ShotgunShells', 'Base.308Bullets', 'Base.223Bullets'}:
                    entry['processes'].add('cast_ammunition')
                if rule == 'food_preparation_recipes':
                    name = observation['content'].get('recipe_name')
                    process = {'Slice Bread': 'slice_bread', 'Slice Watermelon': 'slice_watermelon',
                        'Get Bacon Bits': 'cut_bacon_into_bits', 'Get Bacon Rashers': 'prepare_bacon',
                        'Make Halloween Pumpkin': 'process_pumpkin', 'Make Stake': 'shape_branch',
                        'Drill Plank': 'process_lumber', 'Slice Ham': 'cut_meat', 'Slice Salami': 'cut_meat',
                        'Butcher Small Animal': 'butcher_animal_carcass', 'Butcher Rabbit': 'butcher_animal_carcass',
                        'Butcher Bird': 'butcher_animal_carcass', 'Cut Fish': 'prepare_fish',
                        'Make Bowl of Cereal': 'put_food_or_ingredients_in_bowl_or_pot',
                        'Make Bowl of Oatmeal': 'put_food_or_ingredients_in_bowl_or_pot'}.get(name)
                    if process:
                        entry['processes'].add(process)
                if rule == 'item_transformation_recipes':
                    name = observation['content'].get('recipe_name')
                    process = {
                        'Gather Gunpowder': 'dismantle_ammunition', 'Smash Bottle': 'break_bottle',
                        'Saw Logs': 'saw_log', 'Make Sturdy Stick': 'saw_planks',
                        'Saw Off Shotgun': 'saw_off_shotgun', 'Saw Off Double Barrel Shotgun': 'saw_off_shotgun',
                        'Smash Watermelon': 'smash_watermelon', 'Light Candle': 'light_candle',
                        'Make Timer': 'modify_timer', 'Make Bowl of Beans': 'put_food_or_ingredients_in_bowl_or_pot',
                        'Make Bucket of Plaster': 'mix_ingredients', 'Place Cake in Baking Pan': 'mix_ingredients',
                        'Make Remote Controller V1': 'process_electronic_parts',
                        'Make Remote Controller V2': 'process_electronic_parts',
                        'Make Remote Controller V3': 'process_electronic_parts',
                        'Make Aerosol bomb': 'assemble',
                    }.get(name)
                    if process:
                        entry['processes'].add(process)
                    if name in {'Add Timer', 'Add Motion Sensor V1', 'Add Motion Sensor V2', 'Add Motion Sensor V3', 'Add Crafted Trigger'}:
                        entry['processes'].add('modify_explosive')
                    if name in {'Make Aerosol bomb', 'Make Flame bomb', 'Make Smoke Bomb', 'Make Noise Maker', 'Make Pipe bomb',
                                'Make Molotov Cocktail', 'Make Remote Trigger', 'Make Remote Controller V1',
                                'Make Remote Controller V2', 'Make Remote Controller V3', 'Make Newspaper Hat', 'Make Tin Foil Hat',
                                'Make Wooden Box Trap', 'Make Snare Trap', 'Make Trap Box', 'Make Stick Trap', 'Make Cage Trap'}:
                        entry['processes'].add('craft')
                recipe_name = observation['content'].get('recipe_name') or observation['locator'].rsplit(':', 1)[-1].removeprefix('Base.')
                process_names = {
                    'Slice Baloney': 'cut_meat', 'Slice Fillet': 'prepare_fish', 'Slice Frog': 'butcher_animal_carcass',
                    'Dismantle Speaker': 'dismantle_speaker', 'Dismantle TV Remote': 'dismantle_tv_remote',
                    'Open Box of Nails': 'open_nails_box',
                    'Make Bread Dough': 'mix_ingredients', 'Make Chocolate Chip Cookie Dough': 'mix_ingredients',
                    'Make Chocolate Cookie Dough': 'mix_ingredients', 'Make Oatmeal Cookie Dough': 'mix_ingredients',
                    'Make Shortbread Cookie Dough': 'mix_ingredients', 'Make Sugar Cookie Dough': 'mix_ingredients',
                    'Prepare Omelette': 'mix_ingredients', 'Place Pie in Baking Pan': 'mix_ingredients',
                    'Place Pasta in Cooking Pot': 'put_food_or_ingredients_in_bowl_or_pot',
                    'Place Pasta in Saucepan': 'put_food_or_ingredients_in_bowl_or_pot',
                    'Place Rice in Cooking Pot': 'put_food_or_ingredients_in_bowl_or_pot',
                    'Place Rice in Saucepan': 'put_food_or_ingredients_in_bowl_or_pot',
                }
                if recipe_name in process_names:
                    entry['processes'].add(process_names[recipe_name])
                if recipe_name in {'Make 223 Bullets Mold', 'Make 308 Bullets Mold', 'Make 9mm Bullets Mold',
                        'Make Shotgun Shells Mold', 'Build Spiked Baseball Bat', 'Build Spiked Plank', 'Smash Bottle', 'Make Stake'}:
                    entry['processes'].add('craft')
                if rule == 'electronic_salvage':
                    entry['processes'].add('dismantle_electronics')
                if rule == 'bandage_materials':
                    name = observation['content'].get('recipe_name')
                    process = {'Disinfect Bandage': 'disinfect_bandage', 'Disinfect Rag': 'disinfect_rag',
                               'Douse Cotton in Alcohol': 'wet_cotton_with_alcohol', 'Put Alcohol on Cotton': 'wet_cotton_with_alcohol'}.get(name)
                    if process:
                        entry['processes'].add(process)
                        if any(c.startswith('Heat:') for c in clauses) and process.startswith('disinfect_'):
                            entry['processes'].add(process.replace('disinfect_', 'boil_'))
                if rule == 'fabric_recovery':
                    if '[Recipe.GetItemTypes.RipSheets]' in clauses:
                        entry['processes'].add('rip_named_cloth')
                    elif '[Recipe.GetItemTypes.RipClothing_Cotton]' in clauses:
                        entry['processes'].add('rip_registered_clothing')
                    elif '[Recipe.GetItemTypes.RipClothing_Denim]' in clauses:
                        entry['processes'].add('rip_denim_clothing')
                    elif '[Recipe.GetItemTypes.RipClothing_Leather]' in clauses:
                        entry['processes'].add('rip_leather_clothing')
                entry['source_paths'].update(observations[o]['source_path'] for o in provenance['observation_refs'])
    base['reader'].read('docs/ARCHITECTURE.md')
    picker = 'lua/server/Items/ItemPicker.lua'
    picker_text = base['reader'].read(picker).decode('utf-8-sig')
    if not re.search(r'^ItemPicker\s*=\s*ItemPickerJava\s*$', picker_text, re.M):
        raise ValueError('loot consumer handoff changed')
    loot_traces = defaultdict(list)
    for trace_ref, trace in base['acquisition']['traces'].items():
        if trace['family'] in {'loot', 'vehicle'}:
            for token in set(trace.get('tokens', [])):
                loot_traces[token].append((trace_ref, trace))
    def retain_boundary(claim, paths, examined, dependency, reason, partial=()):
        uncertainty = {'meaning': claim['meaning'], 'examined': examined,
            'required_input': dependency, 'reason': reason}
        claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=list(partial),
            verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
            remaining_work=None, remaining_uncertainty=uncertainty, reason=reason,
            source_binding='source_bound', source_strength='reviewed_exact_consumer_boundary', review_state='reviewed')
        conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
            'successor_fact_refs': list(partial), 'locales': {}, 'residual': uncertainty,
            'conservation_status': 'bounded_unresolved'})

    for claim in inventory['claims']:
        meaning = claim.get('meaning')
        if not meaning:
            continue
        item = claim['item_id']
        if meaning in (['function', 'sort_empty_containers'], ['function', 'dispose_container']):
            records = base['declarations'].get(item, [])
            if len(records) == 1:
                reason = 'Remove generic sorting/disposal from Layer 3 under the adopted general inventory-management exclusion. This atom describes organizing or discarding carried objects; it does not state an item-specific transformation. Emptying contents, refilling and crafting reuse remain independent claims. No destination surface or relocation is claimed.'
                claim.update(migration_disposition='responsibility_removed', reason=reason,
                    verified_source_refs=[base['reader'].bindings[records[0]['path']], base['reader'].bindings['docs/ARCHITECTURE.md']],
                    remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                    source_strength='responsibility_boundary', review_state='reviewed',
                    owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': 'adopted P4 general inventory-management scope clarification', 'destination_presence': 'not_claimed'})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'responsibility_removed',
                    'successor_fact_refs': [], 'locales': {}, 'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
                continue
        if item in sources.PLAIN_OBJECT_LABELS or item in sources.MATERIAL_OBJECT_ITEMS:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            plain = fields.get('Type') == 'Normal' and not conflicts and set(fields) <= (
                sources.MATERIAL_OBJECT_FIELDS if item in sources.MATERIAL_OBJECT_ITEMS else sources.PLAIN_OBJECT_FIELDS)
            management = meaning[0] == 'function' and meaning[1] in {
                'carry_cash', 'carry_cards', 'carry_wallet', 'organize_paper', 'organize_household_items',
                'gather_household_supplies', 'use_tableware'}
            labels = (meaning in (['context_label', 'table_setting'], ['context_label', 'play'])
                      or (item in {'Base.String', 'Base.Yarn', 'Base.Pipe'} and meaning == ['role_unspecified_context', 'material']))
            if plain and (management or labels):
                reason = ('Remove this exact general carrying, organizing, supply-gathering or table-setting gloss under the adopted inventory-management exclusion; it asserts no item-specific transformation. Dedicated gameplay, storage and cleaning claims remain independent.' if management else
                          'Remove this standalone play/table-setting or unspecified-material label from Layer 3. It supplies only a general context/category, with no independently described operation; actual function and recipe claims remain separately adjudicated.')
                evidence = [base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, 'docs/ARCHITECTURE.md')]
                claim.update(migration_disposition='responsibility_removed', reason=reason, verified_source_refs=evidence,
                    remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                    source_strength='responsibility_boundary', review_state='reviewed',
                    owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': 'P4 general inventory-management exclusion and Layer 2 category responsibility', 'destination_presence': 'not_claimed'})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'responsibility_removed',
                    'successor_fact_refs': [], 'locales': {}, 'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
                continue
            absent_functions = {'play_sport', 'play_with_game_objects', 'attach_button_to_clothing_or_fabric',
                'comb_hair', 'groom_hair', 'dog_chew_toy', 'frame_photograph', 'frame_picture', 'equip_pet_dog_collar',
                'brush_teeth', 'write_documents', 'revise_documents', 'clean_body', 'clean_surroundings',
                'empty_container', 'reuse_container', 'wear_body', 'ring_bell', 'store_water',
                'toggle_device_power', 'tune_radio', 'receive_radio_signal', 'unfold_umbrella',
                'protect_from_rain', 'fold_umbrella', 'check_signals', 'operate_equipment'}
            absent = ((meaning[0] == 'function' and meaning[1] in absent_functions)
                      or meaning in (['condition', 'sport', 'game_rules'], ['effect', 'body_scent', 'add'], ['context', 'food_preparation']))
            supported_meaning = any((meaning[0] == 'function' and f['payload'] == {'function': meaning[1]})
                                    or (meaning == ['context', 'food_preparation'] and f['payload'].get('activity') in {'food_preparation', 'dough_preparation', 'batter_preparation'})
                                    for f in per_item[item])
            if plain and absent and not supported_meaning:
                paths = {records[0]['path'], semantic.MENU, semantic.CLOTHING, semantic.CRAFT, semantic.GROUPS,
                         sources.WORLD_MENU, sources.WASH_BODY, sources.WASH_CLOTHING, sources.CLEAN_BLOOD,
                         sources.CONTEXT_MANAGER, sources.CONTEXT_INVENTORY, sources.CONTEXT_LOADER,
                         sources.CONTEXT_ELEMENT, sources.CONTEXT_RADIO, sources.CONTEXT_MOVABLE, sources.CONTEXT_MEDIA,
                         sources.HOTBAR, sources.HOTBAR_SLOTS, sources.PLACE_OBJECT, sources.DROP_OBJECT,
                         sources.CAMP_FUEL, sources.CAMP_MENU, sources.LEGACY_RELOAD, sources.TUTORIAL_MENU}
                evidence = [base['reader'].bindings[p] for p in sorted(paths)]
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'selection': 'No exact named-item or capability-field predicate selects this claimed action in the bound inventory/registered dispatch. The normal model-placement and transfer routes are general management; a label is not an action implementation.',
                    'specific_exclusions': 'Sports/game items have no Weapon or game-control dispatch; toiletries have no dye/makeup/medical or actual Soap2/CleaningLiquid2/Bleach cleaning selection; plain tableware has no Food/capacity/water-replacement capability; stationery lacks writer tags and writable pages; pet/frame objects have no corresponding action selection. Any exact crafting relation remains separately attributed.'},
                    'required_input': 'An authoritative item-specific consumer implementing the claimed ' + '/'.join(map(str, meaning)) + ' for ' + item,
                    'reason': 'The available exact declaration and selected consumers do not establish the claimed dedicated operation, effect or rules. This is a bounded source gap for that proposition, not a claim that the object has no purpose anywhere or that a hypothetical extension blocks the answered dispatch question.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='examined_exact_dispatch_gap', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item in sources.OBJECT_LABELS and meaning in (
                ['identity_label', sources.OBJECT_LABELS[item]], ['context_label', 'leisure'], ['context_label', 'souvenir'],
                ['function', 'view_leisure_objects'], ['function', 'collect_leisure_objects']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Normal' and not conflicts and set(fields) <= sources.PLAIN_OBJECT_FIELDS:
                taxonomy = meaning[0] == 'identity_label' or meaning == ['context_label', 'souvenir']
                paths = {records[0]['path'], 'docs/ARCHITECTURE.md', semantic.MENU,
                         sources.CONTEXT_MEDIA, sources.RADIO_MEDIA, sources.LEGACY_MEDIA_MENU}
                for path in paths:
                    base['reader'].read(path)
                reason = ('Remove the standalone object taxonomy from Layer 3 under the existing Layer 2 classification responsibility. '
                          if taxonomy else
                          'Remove the generic leisure handling gloss: taking out, looking at ordinary objects and collecting them describe general inventory management within the adopted exclusion. '
                          'The sentence does not establish a dedicated photo viewer, a play-with-toy action, a mood effect or media playback. ')
                reason += 'This does not claim relocation or destination preservation; exact recorded-media functionality and every other direct question remain independently adjudicated.'
                claim.update(migration_disposition='responsibility_removed', reason=reason,
                    verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                    source_strength='responsibility_boundary', review_state='reviewed',
                    owner_presence_evidence={'path': 'docs/ARCHITECTURE.md',
                        'section': '정보 계층 / 2계층' if taxonomy else 'adopted P4 general inventory-management scope clarification',
                        'destination_presence': 'not_claimed', 'declaration': fields,
                        'media_distinction': 'The obsolete disks/tapes world-menu body is commented out. Active RWMMedia uses isRecordedMedia/getMediaType; joypad selection names Disc_Retail/VHS_Retail/VHS_Home, not these generic Disc/VHS declarations.'})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                    'migration_disposition': 'responsibility_removed', 'successor_fact_refs': [], 'locales': {},
                    'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
                continue
        if (item == 'Base.Apple' and meaning[0] in {'recipe_relation', 'recipe_requirement', 'recipe_menu',
                                                  'recipe_preparation', 'recipe_limit', 'recipe_sequence'}
                and meaning[1] in base.get('apple_recipe_relations', {})):
            relation = base['apple_recipe_relations'][meaning[1]]
            paths = {'docs/ARCHITECTURE.md', 'scripts/items_food.txt', relation['path'],
                     'scripts/recipes.txt', semantic.MENU, semantic.COOK, semantic.GROUPS}
            for path in paths:
                base['reader'].read(path)
            reason = ('Remove this concrete recipe relation, requirement, menu, preparation, limit or sequence from the Layer 3 description. '
                      'ARCHITECTURE assigns those exact interaction relationships to Layer 4. The independent Apple ingredient role and ingestion claims remain accounted. '
                      'This is responsibility removal, not verified relocation, a claim of destination presence, or certification of a native recipe limit/baking result.')
            claim.update(migration_disposition='responsibility_removed', reason=reason,
                verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                source_strength='responsibility_boundary', review_state='reviewed',
                owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': '정보 계층 / 4계층 - 상호작용 정보 계층',
                    'destination_presence': 'not_claimed', 'source_relation': relation,
                    'retained_layer3_scope': 'The independent food-preparation ingredient fact retains recipe acceptance for the selected base, current cooked/frozen eligibility, inventory transfer/retention, poisoning policy and interruption qualifiers. No unconditional addition or finished cooked-food outcome is asserted. Numeric per-recipe capacity and exact preparation/menu sequence are the removed relation detail; removal does not strip those truth-changing Layer 3 eligibility predicates.',
                    'examined': 'Apple names eight exact evolved recipes. Bowl/CakePrep/PiePrep/BakingTray_Muffin and the prepared Pancakes/Waffles/Oatmeal forms match their BaseItem declarations. Cake/pie/muffin preparation recipes retain actual inputs and callbacks. The menu transfers base/ingredient and ISAddItemInRecipe delegates getItemsCanBeUse/addItem; MaxItems and Cookable are raw source properties, not independently verified native limits or baking outcomes.'})
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                'migration_disposition': 'responsibility_removed', 'successor_fact_refs': [], 'locales': {},
                'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
            continue
        if (item == 'Base.Hammer' and meaning[0] in {'recipe_relation', 'recipe_requirement', 'recipe_menu', 'recipe_limit', 'recipe_sequence'}
                and meaning[1] == 'WoodenCross'):
            paths = {'docs/ARCHITECTURE.md', semantic.BUILD, semantic.BUILD_OBJECT, semantic.BUILD_ACTION, semantic.BUILD_UTIL}
            for path in paths:
                base['reader'].read(path)
            retained = [f['ref'] for f in per_item[item] if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'tool'}]
            if retained:
                reason = ('Remove the exact Wooden Cross recipe requirements and menu/placement walkthrough under the existing Layer 4 interaction responsibility. '
                          'The active miscellaneous menu calls canBuild(2,2,0,0,0,0), requires a hammer and selects onWoodenCross; that factory declares two Base.Plank, two Base.Nails and starts the placement cursor. '
                          'These are structure-specific relations, not universal carpentry requirements. The independently admitted construction tool role and its eligibility/placement qualifiers remain Layer 3. '
                          'This is responsibility removal, not verified destination presence or guaranteed world-object creation.')
                claim.update(migration_disposition='responsibility_removed', reason=reason,
                    verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                    source_strength='responsibility_boundary', review_state='reviewed',
                    owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': '정보 계층 / 4계층 - 상호작용 정보 계층',
                        'destination_presence': 'not_claimed', 'retained_layer3_fact_refs': retained,
                        'source_relation': 'ISBuildMenu.buildMiscMenu and ISBuildMenu.onWoodenCross'})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                    'migration_disposition': 'responsibility_removed', 'successor_fact_refs': [], 'locales': {},
                    'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
                continue
        if meaning[0] == 'condition' and meaning[-1] == 'near_anvil':
            selected = [entry for (_, clauses), entry in reviewed_results[item].items() if 'NearItem:Anvil' in clauses]
            if selected:
                retain_boundary(claim, {semantic.CRAFT, *(p for entry in selected for p in entry['source_paths'])},
                    {'recipe_observation_refs': [e['observation_ref'] for e in selected], 'field': 'NearItem:Anvil'},
                    'Native NearItem object recognition, recipe validity and exact result binding',
                    'The declared anvil condition belongs to the exact recipe creating this item, not an intrinsic action of the resulting ammunition/mold/tool. Its raw requirement and interpreted input path are retained; native matching and result delivery remain separate.')
                continue
        if item == 'Base.Molotov' and meaning == ['acquisition_alternative_materials', 'liquor_bottle', 'empty_bottle']:
            selected = [entry for (_, clauses), entry in reviewed_results[item].items()
                if 'destroy [Recipe.GetItemTypes.Liquor]' in clauses or 'WineEmpty/WineEmpty2/WhiskeyEmpty/BeerEmpty' in clauses]
            if len(selected) >= 2:
                retain_boundary(claim, {semantic.CRAFT, semantic.GROUPS, *(p for entry in selected for p in entry['source_paths'])},
                    {'recipe_observation_refs': [e['observation_ref'] for e in selected]},
                    'Native full-liquor classification, separate recipe input selection and result delivery',
                    'Full liquor and an empty bottle with a petrol use are different complete recipes, each requiring cloth. Their alternatives cannot be treated as interchangeable bottles without the different fullness and fuel requirements.')
                continue
        if meaning[0] in {'acquisition_material', 'acquisition_tool', 'acquisition_alternative_materials'}:
            token_aliases = {
                'iron_ingot': {'IronIngot'}, 'Hammer': {'[Recipe.GetItemTypes.Hammer]', 'BallPeenHammer'},
                'hammer': {'[Recipe.GetItemTypes.Hammer]', 'BallPeenHammer'}, 'tongs': {'Tongs'},
                'saw': {'[Recipe.GetItemTypes.Saw]', 'Saw', 'GardenSaw'},
                'bladed_tool': {'[Recipe.GetItemTypes.SharpKnife]', 'MeatCleaver'},
                'cord': {'Twine'}, 'gasoline': {'PetrolCan', '[Recipe.GetItemTypes.Petrol]'},
                'hairspray': {'Hairspray'}, 'fireworks_material': {'Sparklers'},
                'stick_material': {'TreeBranch', 'WoodenStick', 'Plank'},
                'empty_bottle': {'WineEmpty', 'WineEmpty2', 'WhiskeyEmpty', 'BeerEmpty', 'WaterBottleEmpty'},
                'empty_liquor_bottle': {'WhiskeyEmpty'}, 'empty_beer_bottle': {'BeerEmpty'},
                'liquor_bottle': {'WhiskeyFull'}, 'alarm_clock': {'AlarmClock', 'AlarmClock2'},
            }
            selected = []
            for (_, clauses), entry in reviewed_results[item].items():
                inputs = [c for c in clauses if ':' not in c]
                if meaning[0] == 'acquisition_tool':
                    inputs = [c for c in inputs if c.startswith('keep ')]
                else:
                    inputs = [c for c in inputs if not c.startswith('keep ')]
                alternatives = [set(re.sub(r'[=;][0-9.]+$', '', c.removeprefix('keep ').removeprefix('destroy ')).split('/')) for c in inputs]
                expected = [token_aliases.get(t, {t}) for t in meaning[1:]]
                if (meaning[0] == 'acquisition_alternative_materials' and any(all(tokens & values for tokens in expected) for values in alternatives)
                        or meaning[0] != 'acquisition_alternative_materials' and any(expected[0] & values for values in alternatives)):
                    selected.append(entry)
            if selected:
                paths = {semantic.CRAFT, semantic.GROUPS, *(p for entry in selected for p in entry['source_paths'])}
                retain_boundary(claim, paths, {'recipe_observation_refs': [e['observation_ref'] for e in selected],
                    'input_role': meaning[0], 'result_fulltype': item},
                    'Native RecipeManager selected-input quantities, exact result identity and delivery',
                    'The claimed input/tool alternative matches an independently interpreted recipe for this exact result. Its retained clauses and callback preserve the actual other requirements; the input-use fact does not establish successful native acquisition or universal interchangeability.')
                continue
        rod_outputs = {'Base.CraftedFishingRod', 'Base.CraftedFishingRodTwineLine', 'Base.FishingRod', 'Base.FishingRodTwineLine'}
        rod_material = item in rod_outputs and meaning[0] in {'acquisition_material', 'acquisition_alternative_materials'}
        spear_outputs = {'Base.SpearCrafted', *('Base.' + result for _, _, result in sources.SPEAR_ATTACHMENTS)}
        spear_material = item in spear_outputs and meaning[0] in {'acquisition_material', 'acquisition_alternative_materials', 'acquisition_tool'}
        rod_repair = item == 'Base.FishingRodBreak' and meaning == ['function', 'repair_fishing_rod_with_line']
        radio_material = (item in {'Radio.RadioMakeShift', 'Radio.HamRadioMakeShift', 'Radio.WalkieTalkieMakeShift'}
                          and meaning[0] == 'acquisition_material' and meaning[1] in {'electronic_scrap', 'radio_parts', 'wire', 'aluminum'})
        if rod_material or rod_repair or spear_material or radio_material:
            output = 'Base.FishingRod' if rod_repair else item
            reviewed = reviewed_results[output]
            tokens = {'wooden_stick': 'WoodenStick', 'fishing_line': 'FishingLine', 'twine': 'Twine',
                      'broken_fishing_rod': 'FishingRodBreak', 'paperclip': 'Paperclip', 'nail': 'Nails'}
            tokens.update({token: token for token in ('SpearCrafted', 'DuctTape', 'Plank', 'TreeBranch',
                          *(attachment for _, attachment, _ in sources.SPEAR_ATTACHMENTS))})
            if radio_material:
                tokens.update(electronic_scrap='ElectronicsScrap', wire='Radio.ElectricWire', aluminum='Aluminum')
            selected = []
            for (_, clauses), entry in reviewed.items():
                inputs = [c for c in clauses if ':' not in c and not c.startswith(('keep ', 'destroy '))]
                bare = [re.sub(r'=\d+(?:\.\d+)?$', '', c) for c in inputs]
                if radio_material and meaning[1] == 'radio_parts':
                    matches = 'Radio.RadioReceiver' in bare and 'Amplifier' in bare
                elif meaning == ['acquisition_tool', 'spear_cutting_alternative']:
                    matches = 'keep [Recipe.GetItemTypes.SharpKnife]/SharpedStone/MeatCleaver' in clauses
                elif rod_repair:
                    matches = {'FishingRodBreak', 'FishingLine'} <= set(bare)
                elif meaning[0] == 'acquisition_alternative_materials':
                    matches = all(t in tokens for t in meaning[1:]) and any(set(c.split('/')) == {tokens[t] for t in meaning[1:]} for c in bare)
                else:
                    matches = meaning[1] in tokens and tokens[meaning[1]] in bare
                if matches:
                    selected.append(entry)
            if result_recipes[output] and selected:
                paths = {semantic.CRAFT, *(p for entry in selected for p in entry['source_paths'])}
                partial = [f['ref'] for f in per_item[item] if f['payload'] == {'role': 'material'}] if rod_repair else []
                uncertainty = {'meaning': meaning,
                    'examined': {'result_item': output, 'recipe_observation_refs': [e['observation_ref'] for e in selected],
                                 'input_interpretation': 'Exact input clauses and the paperclip/nail alternative are retained; crafting requires the learned recipe. The repair sentence omits that alternative and the full declared conditions.' if rod_repair else 'The stated material or alternative matches a source-reviewed input clause; amounts and other recipe requirements remain in that source observation.'},
                    'required_input': 'RecipeManager.PerformMakeItem result identity and delivery for the selected creation recipe',
                    'reason': 'The actual recipe inputs and Lua crafting consumer have been reconciled. Their source-bound material or tool role does not by itself establish the created result identity delivered by the native recipe manager.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)], remaining_work=None,
                    remaining_uncertainty=uncertainty, reason=uncertainty['reason'], source_binding='source_bound',
                    source_strength='reviewed_transformation_native_result_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if (meaning[:2] == ['acquisition_process', 'fill_ground_bag'] and item in base.get('ground_bag_relations', {})
                and {'Base.Dirtbag': 'dirt', 'Base.Gravelbag': 'gravel', 'Base.Sandbag': 'sand'}.get(item) == meaning[2]):
            relation = base['ground_bag_relations'][item]
            uncertainty = {'meaning': meaning, 'examined': relation,
                'required_input': 'Inventory.AddItem result identity for the specified Base bag and native used-delta/capacity state, plus the independent shovelGround server terrain operation',
                'reason': 'The registered menu, exact ground sprite selection, TakeDirt tool, empty HoldDirt replacement and matching partial-bag refill have been interpreted through their Lua consumers. A new bag starts at one use; this is not a guaranteed full bag. The local inventory transformation and server ground command are independent, and the native item creation/result remains bounded separately.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in relation['source_paths']],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='exact_ground_collection_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if item == 'camping.Flint' and meaning == ['function', 'make_spark']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if not conflicts and fields.get('Type') == 'Normal' and set(fields) <= sources.PLAIN_OBJECT_FIELDS:
                paths = {records[0]['path'], semantic.MENU, sources.CAMP_MENU, sources.CAMP_LIGHT,
                         sources.CAMP_FUEL, sources.CAMP_COMMANDS}
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'dispatch': 'The exact Normal Flint is not the selected active igniter, FlintKnife or SteelAndFlint. The camping light action consumes its selected fuel/igniter, not a display-name synonym.'},
                    'required_input': 'An authoritative active spark-making consumer selecting exact camping.Flint',
                    'reason': 'The declared name identifies flint but the bound active ignition dispatch does not corroborate its claimed spark-making use. This finite source comparison does not assert universal game-wide absence.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_camping_dispatch_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if ((item == 'Base.BucketEmpty' and meaning == ['acquisition_process', 'empty_water_bucket'])
                or (item == 'farming.GardeningSprayFull' and meaning == ['acquisition_process', 'fill_spray_with_chemicals'])):
            filled = 'Base.BucketWaterFull' if item == 'Base.BucketEmpty' else item
            source = base.get('water_container_sources', {}).get(filled)
            records = base['declarations'].get(filled, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if source and not conflicts:
                paths = {records[0]['path'], semantic.MENU, sources.WORLD_MENU, sources.TAKE_WATER, sources.DUMP_WATER}
                uncertainty = {'meaning': meaning, 'examined': {'filled_declaration': fields, 'water_binding': source,
                    'emptying': sources.WATER_EMPTYING if item == 'Base.BucketEmpty' else None},
                    'required_input': ('Native Use interpretation of Base.BucketWaterFull ReplaceOnDeplete=BucketEmpty and exact returned inventory identity'
                        if item == 'Base.BucketEmpty' else 'An authoritative chemical-filling producer for exact farming.GardeningSprayFull, distinct from its demonstrated water-source replacement and the two treatment-spray recipe results'),
                    'reason': ('The actual dump action reduces water and calls Use after depletion; the declaration names BucketEmpty. The local action does not itself create that exact returned item, so acquisition identity remains native.'
                        if item == 'Base.BucketEmpty' else 'This exact full spray is declared as a water source and is reached by the empty spray WaterSource replacement. Milk and Cigarettes treatments have different exact results. The predecessor chemical-filling claim is not corroborated by the bound water route and is not silently rewritten as one of those treatments.')}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_water_form_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if (meaning in (['acquisition_process', 'fill_water'], ['condition', 'fill_water', 'empty_container'])
                and item in base.get('water_filling_relations', {})):
            routes = base['water_filling_relations'][item]
            paths = {observations[r]['source_path'] for route in routes for r in route['observation_refs']}
            uncertainty = {'meaning': meaning, 'examined': routes,
                'required_input': 'Native getReplaceType(WaterSource) mapping and InventoryItemFactory result identity for the exact declared filled form; runtime water availability and delivery',
                'reason': 'The exact empty-form declarations, unbroken/same-building menu selection, transfer, start-time item replacement and progressive filling consumer are reconciled. The native replacement lookup/factory owns output identity. Partial fills and taint persistence remain explicit; filling is not assumed to create a full or purified container.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                         remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                         source_binding='source_bound', source_strength='exact_water_replacement_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        fuel_boundary = (item == 'Base.MetalDrum' and meaning in (
            ['function', 'collect_water'], ['function', 'burn_logs_to_charcoal']))
        fuel_acquisition = item in sources.PETROL_ITEMS and meaning[0] in {'acquisition_process', 'acquisition_container'}
        empty_fuel_state = item in sources.EMPTY_PETROL_ITEMS and (meaning in (
            ['state', 'container_contents', 'empty'], ['state_label', 'empty_container'], ['state_label', 'empty_reusable_container']))
        if fuel_boundary or fuel_acquisition or empty_fuel_state:
            records = base['declarations'].get(item, [])
            paths = {r['path'] for r in records}
            paths.update((sources.BLACKSMITH_MENU, semantic.PROPS, *sources.DRUM_SOURCES)
                if fuel_boundary else (sources.WORLD_MENU, sources.TAKE_FUEL, sources.VEHICLE_MENU, *sources.VEHICLE_FUEL_ACTIONS))
            uncertainty = {'meaning': meaning,
                'required_input': ('An active exact Base.MetalDrum-to-installed-object binding' if fuel_boundary else
                    'Native PetrolSource item creation, initial/depleted container state and actual source-to-result delivery'),
                'reason': ('The existing world drum rain/charcoal code is interpreted, but the carried Normal declaration has no WorldObjectSprite. The construction menu is disabled and its Base.MetalDrum requirement is commented out; moveables use another identity. Installed behavior therefore does not establish this carried-item claim.' if fuel_boundary else
                    'Actual pump and siphon actions replace an empty source using PetrolSource with a fallback, and subsequent transfer can be partial. The pump menu temporary replacement is not the action replacement. These control paths are represented, but native factory state/delivery and the acquisition outcome are not guaranteed from the item name. Acquisition facts remain under their existing authority.')}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='examined_fuel_binding_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        electrical = base.get('electrical_control_sources', {}).get(item)
        electrical_outcome = (electrical and (
            item == 'Base.CarBatteryCharger' and meaning == ['function', 'charge_vehicle_battery']
            or item in {'Base.CarBattery1', 'Base.CarBattery2', 'Base.CarBattery3'} and meaning in (
                ['function', 'supply_vehicle_starting_power'], ['function', 'supply_vehicle_electrical_power'])
            or item == 'Base.Generator' and meaning in (
                ['function', 'supply_generator_power'], ['target_scope', 'generator_power', 'nearby_devices'])))
        if electrical_outcome:
            paths = {observations[r]['source_path'] for r in electrical['observation_refs']}
            uncertainty = {'meaning': meaning, 'examined': electrical,
                'required_input': ('IsoCarBatteryCharger charge progression for the connected battery and actual power state'
                    if item == 'Base.CarBatteryCharger' else
                    'IsoGenerator electricity propagation, coverage and connected consumers'
                    if item == 'Base.Generator' else
                    'Native vehicle engine-start and electrical-consumer execution for the installed battery'),
                'reason': 'The actual installation, connection and control paths are interpreted separately from the claimed native result. Vehicle Lua charge adjustments are represented, including the helper applying its delta twice. Charger activation and generator state setters do not themselves implement successful charging, electrical supply or a guaranteed coverage area. The unused legacy recharge action is not treated as a live charging route.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='examined_electrical_execution_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        physics_outcome = (item in sources.THROWN_DEVICE_ITEMS and (
            meaning[0] == 'effect' and meaning[1] in {'world_fire', 'explosion'}
            or meaning[0] == 'conditional_effect' and meaning[1] in {'noise', 'smoke', 'world_noise', 'world_smoke'}
            or meaning == ['function', 'throw_item']))
        illumination = (item in sources.LIGHT_ITEMS and meaning in (
            ['function', 'illuminate_surroundings'], ['effect', 'illumination', 'provide'], ['condition', 'illumination', 'lit']))
        available_control = any(f['payload'].get('function') == ('request_physics_attack' if physics_outcome else 'control_portable_light') for f in per_item[item])
        if (physics_outcome or illumination) and available_control:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            paths = {records[0]['path'], semantic.MENU}
            paths.update({sources.FIREARM, sources.DEVICE_PLACE, sources.DEVICE_TIMER, sources.DEVICE_TAKE, sources.OBJECT_COMMANDS}
                         if physics_outcome else {sources.LIGHT_RADIAL, sources.LIGHT_BINDING, semantic.GROUPS, semantic.CRAFT})
            uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                'dispatch': sources.PHYSICS_ATTACK if physics_outcome else sources.LIGHT_CONTROL},
                'required_input': 'DoAttack/PhysicsObject and IsoTrap interpretation of the exact effect and activation fields' if physics_outcome else 'canEmitLight/light-strength geometry, charge drain and actual native emission for this exact light form',
                'reason': 'The applicable local controls and actual callbacks have been interpreted. Their declared native effect inputs and operation requests do not themselves establish this separate claimed outcome. No positive effect or negative immunity is inferred from names or zero-valued damage fields.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='examined_device_execution_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if meaning[0] == 'acquisition_process' and result_recipes[item]:
            reviewed = reviewed_results[item]
            # A claim that an item can be obtained through this route is
            # existential. Unrelated result recipes are separate obligations,
            # not a reason to postpone an already interpreted exact route.
            if any(meaning[1] in r['processes'] for r in reviewed.values()):
                selected = [r for r in reviewed.values() if meaning[1] in r['processes']]
                paths = {semantic.CRAFT, *(p for r in selected for p in r['source_paths'])}
                evidence = [base['reader'].bindings[p] for p in sorted(paths)]
                uncertainty = {'meaning': meaning, 'examined': {
                    'result_observation_refs': sorted(r['observation_ref'] for r in selected),
                    'consumer': semantic.CRAFT,
                    'local_reconciliation': 'The selected exact recipes match this claimed process and have source-reviewed input/callback conditions. Other result recipes are separate route obligations.'},
                    'required_input': 'RecipeManager.PerformMakeItem result identity, module resolution and delivery for these exact recipes',
                    'reason': 'The source supports the specified transformation route as a concrete acquisition lead. Its input roles and called Lua behavior have been interpreted, but ISCraftAction receives the created item from RecipeManager before delivery; input-use facts do not establish that native result identity. No output is relabeled as an intrinsic material role.'}
                if meaning[1] in {'rip_named_cloth', 'rip_registered_clothing', 'rip_denim_clothing', 'rip_leather_clothing'}:
                    fabric = {'rip_named_cloth': 'Sheet', 'rip_registered_clothing': 'Cotton', 'rip_denim_clothing': 'Denim', 'rip_leather_clothing': 'Leather'}[meaning[1]]
                    uncertainty['examined']['callback'] = 'Recipe.OnCreate.RipClothing uses items:get(0), the exact named Sheet or fabric definition, covered parts/tailoring, and dirt/blood selection. The nominal recipe result is removed; the callback creates and adds the selected material itself.'
                    uncertainty['examined']['material_identity'] = {'definition': fabric, 'full_type': item, 'dirty_branch': 'A dirty suffix is requested only when the script manager finds that form; otherwise the same full material type is created.'}
                    uncertainty['examined']['eligibility'] = 'Registered Clothing type and exact fabric membership exclude named-definition items. Separate IsWorn and IsNotWorn recipes preserve both states. Denim/Leather recipes additionally keep a Recipe.GetItemTypes.Scissors tool; these are recipe inputs, not the commented definition tools field.' if fabric != 'Sheet' else 'The RipSheets group admits non-Clothing items with a named material definition.'
                    uncertainty['required_input'] = 'RecipeManager callback dispatch and participant ordering for these recipes; runtime material/dirt selection and callback output delivery'
                    uncertainty['reason'] = 'The selected named-cloth or exact fabric route, its actual callback and full material name have been traced. The retained boundary is native callback invocation/selected participant delivery and conditional output. Separate worn/unworn selection and any scissors requirement remain on the exact recipes.'
                if meaning[1] in {'boil_bandage', 'boil_rag'}:
                    uncertainty['examined']['heat_requirement'] = 'The selected water-pot/saucepan recipes declare Heat:-0.22; raw semicolon water amounts are preserved.'
                    uncertainty['required_input'] += '; native interpretation of Heat:-0.22 relative to the claimed boiling temperature'
                    uncertainty['reason'] = 'The complete heated-water preparation recipes and their inputs have been interpreted. Their negative Heat field alone does not establish boiling temperature, and the created sterilized form is delivered by RecipeManager. Both exact limits are retained rather than calling the boiling claim recovered.'
                if meaning[1] == 'craft_sheet_rope_from_sheet_or_cotton':
                    uncertainty['examined']['input_group'] = 'CraftSheetRope admits Clothing with a registered fabric without noSheetRope, or a named ClothingRecipesDefinitions entry. Cotton and Sheet are admitted; Denim/Leather are excluded by noSheetRope. The exact recipe consumes that group and declares Result:SheetRope without a ripping callback.'
                    uncertainty['reason'] = 'The specified sheet/cotton material route is traced through its actual group, recipe and crafting consumer. The predecessor tearing wording is not substituted for Recipe.OnCreate.RipClothing, which is a different fabric-recovery recipe. Native RecipeManager still owns this exact result creation and delivery.'
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='reviewed_transformation_native_result_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning[0] == 'wear' and meaning[1] in WEAR_LOCATIONS:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if (fields.get('Type') == 'Clothing' and conflicts.get('BodyLocation')
                    and set(conflicts['BodyLocation']) <= WEAR_LOCATIONS[meaning[1]]):
                paths = {records[0]['path'], semantic.WEAR, sources.BODY_LOCATIONS}
                uncertainty = {'meaning': meaning, 'examined': {'BodyLocation': conflicts['BodyLocation'], 'consumer': semantic.WEAR},
                    'required_input': 'Native load precedence and worn-location binding for these repeated BodyLocation declarations',
                    'reason': 'The raw declaration contains competing location values. Both belong to the claimed body region, but the exact getter value passed to setWornItem is not selected from declaration order by this recovery. Independent washing and other clothing uses remain represented.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='repeated_location_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['hazard', 'food_poison']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Food' and (fields.get('PoisonPower') or fields.get('Poison')):
                paths = {records[0]['path'], semantic.MENU, semantic.EAT}
                uncertainty = {'meaning': meaning, 'examined': {k: fields.get(k) for k in ('Poison', 'PoisonPower', 'PoisonDetectionLevel', 'OnEat', 'OBSOLETE')},
                    'required_input': 'Native Food poison getters and IsoGameCharacter.Eat interpretation of this exact declared poison input',
                    'reason': 'The declared poison input and actual eating delegation are retained, but they do not establish a contact hazard, fixed poisoning outcome or dose. The independent hunger and any Lua callback effects remain separate.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_native_food_poison_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        records = base['declarations'].get(item, [])
        exact_fields, exact_conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
        native_form = None
        native_paths = {semantic.MENU}
        if ((item.startswith('Base.Umbrella') or item.startswith('Base.ClosedUmbrella'))
                and (meaning == ['function', 'protect_from_rain'] or meaning[:2] == ['condition', 'rain_protection'])):
            native_form = ('ProtectFromRainWhenEquipped and EquippedNoSprint native consumers and held/open-form mapping',
                'The exact open form declares native rain/sprint fields; opening/closing recipes represent form changes. Neither a held-item getter nor the recipe callback implements weather protection. The native field result remains distinct from the recovered form operation.')
            native_paths.update({semantic.GROUPS, semantic.CRAFT})
        elif item.startswith('Base.MakeUp_') and meaning[0] == 'visual_effect' and exact_fields.get('Type') == 'Clothing':
            native_form = ('Exact ClothingItem asset and native worn-slot rendering for ' + item,
                'The registered makeup result is a Clothing item with a makeup body location. The actual makeup UI previews and replaces that item; its name and slot do not prove the claimed visible color or pattern.')
            native_paths.update({sources.MAKEUP_UI, sources.MAKEUP_DEFINITIONS})
        elif item == 'Base.FertilizerEmpty' and meaning in (['function', 'empty_container'], ['function', 'reuse_container']):
            native_form = ('An exact consumer selecting Base.FertilizerEmpty as an emptying or reusable container input',
                'The Normal declaration has no capacity, CanStoreWater, replacement chain or drainable charge. The fertilizer action removes this exact empty item after using fertilizer; it does not provide a reuse or emptying action for the empty form.')
            native_paths.add(sources.FERTILIZE_ACTION)
        elif item == 'Base.WoodenLance' and meaning in (['function', 'thrust_attack'], ['function', 'shove_attack'], ['combat_property', 'reach']):
            native_form = ('Native HandWeapon animation/attack mode and MinRange/MaxRange/PushBackMod execution',
                'The Weapon declaration selects represented melee use and supplies Spear animation/range/pushback inputs. The Lua equip/control path does not determine the claimed thrust, shove or practical reach result.')
        elif item.startswith('farming.') and item.endswith('Seed') and meaning == ['function', 'unpack_seeds']:
            native_form = ('An exact opening consumer for this loose Seed form, distinct from its SeedBag counterpart',
                'The Normal loose-seed declaration and sowing action consume seeds. The independently reviewed packet-opening recipe consumes SeedBag and produces this form; its output must not be recast as an opening input.')
            native_paths.update({semantic.CRAFT, semantic.GROUPS, sources.FARM_MENU})
        if native_form and exact_fields and not exact_conflicts:
            native_paths.add(records[0]['path'])
            uncertainty = {'meaning': meaning, 'examined': {'declaration': exact_fields},
                'required_input': native_form[0], 'reason': native_form[1]}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(native_paths)],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='exact_form_consumer_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if item in base.get('unsupported_wear', {}) and (meaning[0] == 'wear' or meaning == ['function', 'wear_body']):
            boundary = base['unsupported_wear'][item]
            uncertainty = {'meaning': meaning, 'examined': boundary,
                           'required_input': 'verified runtime handling of the declared ' + boundary['location'] + ' body location',
                           'reason': boundary['reason']}
            claim.update(migration_disposition='unresolved', verified_source_refs=boundary['source_refs'],
                         reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                         source_binding='source_bound', source_strength='missing_registry_binding', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                 'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                 'conservation_status': 'bounded_unresolved'})
            continue
        if meaning[0] in {'skill_current_range', 'skill_effect_range'}:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if (fields.get('Type') == 'Literature' and fields.get('SkillTrained') == meaning[1]
                    and not {'Type', 'SkillTrained', 'LvlSkillTrained', 'NumLevelsTrained'} & conflicts.keys()):
                partial = [f['ref'] for f in per_item[item]
                           if f['payload'] == {'property': meaning[1] + '_experience_multiplier', 'direction': 'increase'}]
                paths = [records[0]['path'], semantic.READ, semantic.SKILLS]
                uncertainty = {'meaning': meaning,
                    'examined': {'declaration': {k: fields.get(k) for k in ('SkillTrained', 'LvlSkillTrained', 'NumLevelsTrained')},
                        'current_level_comparison': 'ISReadABook.update permits the multiplier branch when getLvlSkillTrained <= perkLevel + 1 <= getMaxLevelTrained and the reader is not Illiterate.',
                        'effect_range': 'checkMultiplier passes getLvlSkillTrained and getMaxLevelTrained to addXpMultiplier.',
                        'claimed_lower': meaning[2], 'claimed_upper': meaning[3]},
                    'required_input': 'The native Literature.getMaxLevelTrained mapping of LvlSkillTrained and NumLevelsTrained for the claimed numeric endpoints',
                    'reason': 'The conditional multiplier and its supported-level restriction are represented. The supplied Lua consumes the maximum-level getter but does not calculate that endpoint from the declared level count. The exact numeric interval is therefore retained separately rather than replaced by a generic level condition.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in paths], remaining_work=None,
                    remaining_uncertainty=uncertainty, reason=uncertainty['reason'], source_binding='source_bound',
                    source_strength='exact_numeric_getter_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.DigitalWatch2' and meaning[0] in {'acquisition_place', 'acquisition_method'}:
            paths = [r['path'] for r in base['acquisition']['source_bindings']
                     if 'Foraging/' in r['path'] or r['path'].endswith(('Distributions.lua', 'ItemPicker.lua'))]
            for path in paths:
                base['reader'].read(path)
            uncertainty = {'meaning': meaning,
                'examined': 'The bound foraging clothing table registers exact left/right WristWatch forms, not Base.DigitalWatch2. The bound distribution sources provide wristwatch leads but no DigitalWatch2 token. The exact DigitalWatch2 declaration is marked Obsolete.',
                'required_input': 'An exact Base.DigitalWatch2 acquisition producer or documented alias/availability mapping supporting the claimed route',
                'reason': 'The supplied route sources do not corroborate this obsolete FullType claim. Similar wristwatch names cannot be joined to it. This is an unconfirmed predecessor acquisition claim, not a claim that runtime acquisition is impossible.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in paths],
                reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                source_binding='source_bound', source_strength='exact_route_not_corroborated', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if item == 'Base.Hinge' and meaning[0] == 'acquisition_place' and meaning[1] in {'construction-material storage', 'workshops'}:
            forage_path = 'lua/shared/Foraging/forageDefinitions.lua'
            paths = {forage_path, semantic.MOVE, semantic.PROPS}
            texts = {p: base['reader'].read(p).decode('utf-8-sig') for p in paths}
            forage = sources.reader.mask(texts[forage_path], lua=True)
            definitions = sources.reader.mask(texts[semantic.MOVE], lua=True)
            if (re.search(r'Hinge\s*=\s*"Base.Hinge"', forage)
                    and 'generateJunkDefs();' in forage and 'for _, spawnTable in pairs(junkItems) do' in forage
                    and 'type = itemFullName' in forage and 'spawnFuncs = { doGenericItemSpawn }' in forage
                    and re.search(r'addScrapItem\(\s*"Door",\s*"Base.Hinge",\s*2,\s*80,\s*true\s*\)', definitions)):
                traced = {ref: t for token in (item, 'Hinge') for ref, t in loot_traces[token]}
                if not traced:
                    uncertainty = {'meaning': meaning, 'examined': {
                        'foraging': 'generateJunkDefs is called and registers common junk Hinge as Base.Hinge with Junk category and eight general zones, including TownZone. doGenericItemSpawn adjusts supplied-item uses/condition; it does not bind a workshop or construction-supply container.',
                        'disassembly': 'The active Door scrap definition lists two static-size Hinge rolls with base chance 80; the earlier WoodenDoor/100 definition is inside a block comment and is excluded. getScrapItemsList selects actual object materials; addScrapItemToList applies the skill modifier and random roll. This is a disassembly lead, not a discovery-place definition.',
                        'loot_vehicle': 'The bound acquisition trace set has no exact full or short Hinge loot/vehicle producer connection.'},
                        'required_input': 'An exact Hinge producer-to-room/container or zone-to-place connection supporting the claimed construction-material storage or workshop location',
                        'reason': 'The supplied exact-item leads establish general foraging registration and door disassembly alternatives but do not corroborate the predecessor discovery place. Neither TownZone nor an object material is silently equated with that place. This does not assert that Hinge acquisition is impossible.'}
                    claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                        remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                        source_binding='source_bound', source_strength='exact_route_not_corroborated', review_state='reviewed')
                    conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                        'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                    continue
        if meaning[0] == 'acquisition_place' and meaning[1] not in {'urban areas', 'trailer parks'}:
            # Short tokens are explicitly retained as leads, not silently
            # qualified to Base or joined case-insensitively to a fact.
            traced = {ref: t for token in (item, item.split('.', 1)[1]) for ref, t in loot_traces[token]}
            if traced and all(t.get('assessment') == 'assessed' for t in traced.values()):
                connections = [{'trace_ref': ref, 'source_path': t['source_path'], 'locator': t['locator'],
                                'address': t.get('address'),
                                'identity_match': 'exact_fulltype' if item in t.get('tokens', []) else 'unqualified_lead',
                                'selection_conditions': t.get('conditions'),
                                'consumer_connections': t.get('consumer_connections', [])}
                               for ref, t in sorted(traced.items())]
                paths = {picker, *(t['source_path'] for t in traced.values()),
                         *(c['source_path'] for t in traced.values() for c in t.get('consumer_connections', []))}
                source_hashes = {r['path']: r['sha256'] for r in base['acquisition']['source_bindings']}
                for path in paths:
                    if path not in base['reader'].bindings:
                        base['reader'].read(path, source_hashes[path])
                evidence = [base['reader'].bindings[p] for p in sorted(paths)]
                uncertainty = {'meaning': meaning, 'examined': connections,
                               'required_input': 'ItemPickerJava namespace/selection semantics and mapping of the exact raw room/container/vehicle tokens to the claimed place',
                               'reason': 'The raw producer lists and their room/container or vehicle references are retained for this exact item query. Lua aliases the consumer to ItemPickerJava. These declarations alone do not establish the claimed human-readable discovery place; an unrelated accepted foraging route does not conserve it.'}
                assessment_ref = model.identity('assessment', [item, 'loot_vehicle', sorted(traced)])
                source_assessments.setdefault(assessment_ref, {'item_id': item, 'producer_connections': connections,
                                                             'source_refs': evidence})
                uncertainty['examined'] = {'source_assessment_ref': assessment_ref}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='namespace_and_engine_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                                     'migration_disposition': 'unresolved', 'successor_fact_refs': [], 'locales': {},
                                     'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['acquisition_process', 'sack_produce'] and item in base.get('produce_sack_sources', {}):
            source = base['produce_sack_sources'][item]
            if not source['declared_result_leads']:
                records = base['declarations'][item]
                evidence = [base['reader'].bindings[p] for p in (records[0]['path'], source['opening_path'], semantic.MENU, semantic.GROUPS, semantic.CRAFT)]
                uncertainty = {'meaning': meaning, 'examined': source,
                    'consumer_boundary': 'The exact non-writable Food declaration uses the examined Food menu. OpenSackProduce consumes the existing sack, returns EmptySandbag and adjusts produce age; it is not a reverse packing operation. The bound recipe Result clauses supply no producer for this exact sack. Loot routes do not establish a packaging process.',
                    'required_input': 'An authoritative packing recipe or item-specific packing consumer that creates this exact SackProduce form from produce and a sack',
                    'reason': 'The claimed reverse process is not corroborated by the exact declaration, complete bound recipe-result leads and actual opening callback. This does not claim that the item is unobtainable or that every possible producer is absent.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='opening_not_reverse_packing', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        pill_meanings = {'Base.Pills': ['effect', 'pain', 'decrease'],
                         'Base.PillsBeta': ['effect', 'panic', 'decrease'],
                         'Base.PillsSleepingTablets': ['effect', 'sleep_onset', 'facilitate'],
                         'Base.PillsVitamins': ['effect', 'fatigue', 'decrease'],
                         'Base.PillsAntiDep': ['effect', 'unhappiness', 'decrease']}
        if (meaning == pill_meanings.get(item) or (item == 'Base.PillsAntiDep' and meaning == ['effect_timing', 'unhappiness', 'delayed'])):
            partial = [f['ref'] for f in per_item[item] if f['payload'] == {'function': 'take_pills'}]
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if partial and fields.get('Type') == 'Drainable' and not conflicts:
                evidence = [base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, semantic.PILLS)]
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields, 'action': sources.PILL_TAKING},
                    'required_input': 'BodyDamage.JustTookPill interpretation for ' + item + ', including effect and onset timing',
                    'reason': 'The exact pill selection and timed consumer call are represented. The active Lua calls JustTookPill without assigning the claimed medicinal effect or delay. Display names and vitamin FatigueChange do not establish those native outcomes.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=evidence, remaining_work=None, remaining_uncertainty=uncertainty,
                    reason=uncertainty['reason'], source_binding='source_bound', source_strength='exact_medication_native_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning[:2] == ['output_identity', 'exact_opened_item'] or (item == 'Base.BoxOfJars' and meaning == ['output_quantity', 'multiple_empty_jars']):
            routes = [r for r in base.get('package_opening_results', {}).get(item, [])
                      if (r['result_item'] == meaning[2] if meaning[0] == 'output_identity' else r['result_clause'] == 'EmptyJar=6')]
            if routes:
                paths = {semantic.CRAFT, semantic.GROUPS, *(r['path'] for r in routes)}
                uncertainty = {'meaning': meaning, 'examined': routes,
                    'required_input': 'RecipeManager.PerformMakeItem exact result identity/count and callback argument delivery',
                    'reason': 'The named contents match an independently bound opening Result clause. The admitted opening function and its tool/eligibility conditions do not alone prove the native result item delivered. Callback age/returned-vessel behavior remains attached to the exact recipe.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_opening_result_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        pill_labels = {'Base.Pills': ('진통제', 'Painkillers'), 'Base.PillsAntiDep': ('항우울제', 'Antidepressants'),
                       'Base.PillsBeta': ('긴장완화제', 'Beta Blockers'), 'Base.PillsSleepingTablets': ('수면제', 'Sleeping Tablets'),
                       'Base.PillsVitamins': ('비타민', 'Vitamins')}
        key_labels = {**{item: ('열쇠', 'Key') for item in sources.KEY_ITEMS if item != 'Base.KeyPadlock'},
                      'Base.KeyPadlock': ('자물쇠 열쇠', 'Key'), 'Base.CarKey': ('차량 열쇠', 'Car Key'),
                      'Base.Padlock': ('통자물쇠', 'Padlock'), 'Base.CombinationPadlock': ('번호 자물쇠', 'Combination Padlock')}
        key_category = item in key_labels and meaning == ['identity_label', key_labels[item][0]]
        garden_category = meaning == ['context_label', 'gardening'] and item in {
            'farming.GardeningSprayMilk', 'farming.GardeningSprayCigarettes', 'farming.GardeningSprayFull'}
        vessel_category = (item in base.get('water_container_sources', {}) and meaning[0] == 'identity_label'
                           and meaning[1] in {'물통', '물 용기', '조리 용기', '빈 분무기'})
        pill_category = item in pill_labels and meaning == ['identity_label', pill_labels[item][0]]
        fishing_category = meaning[0] == 'identity_label' and meaning[1] in {'낚싯대', 'fishing_rod', 'bait_fish'}
        artificial_category = meaning == ['state_label', 'artificial_lure']
        household_category = meaning == ['identity_label', '생활용품']
        scissors_category = (item == 'Base.Scissors' and meaning == ['identity_label', '생활 도구']
                             and any(f['payload'] == {'function': 'melee_attack'} for f in per_item[item]))
        alarm_category = meaning == ['identity_label', '알람 시계'] and item in {'Base.AlarmClock', 'Base.AlarmClock2'}
        household_clock_category = meaning == ['identity_label', '전자 기기'] and item == 'Base.AlarmClock2'
        obsolete_clock_category = meaning == ['identity_label', '전자 시계'] and item == 'Base.DigitalWatch2'
        panel_source = base.get('vehicle_panel_sources', {}).get(item)
        panel_category = (panel_source and meaning == ['identity_label', sources.PANEL_FORMS[panel_source['family']][2]])
        storage_source = base.get('vehicle_storage_sources', {}).get(item)
        storage_category = (storage_source and meaning[0] == 'identity_label' and meaning[1] in
                            {'트렁크 모듈', '소형 트렁크', '글러브 박스', '좌석 모듈', '연료 탱크'})
        running_source = base.get('vehicle_running_sources', {}).get(item)
        storage_category = storage_category or (running_source and meaning == ['identity_label', {
            'tire': '타이어', 'brake': '브레이크 부품', 'suspension': '서스펜션', 'muffler': '머플러'}[running_source['kind']]])
        map_category = meaning == ['identity_label', '지도'] and item in base.get('item_map_sources', {})
        construction_part_labels = {'Base.Stone': ('돌', 'Stone'), 'Base.Drawer': ('서랍', 'Drawer'),
                                    'Base.Doorknob': ('손잡이 부품', 'Doorknob'), 'Base.SheetRope': ('천 로프', 'Sheet Rope')}
        construction_part_category = (item in construction_part_labels and meaning == ['identity_label', construction_part_labels[item][0]])
        furniture_labels = {'서랍', '매트리스', '에어컨', '앤티크 스토브', '오락 기기', '의자', '휴지통', '정원 장식', '탁자',
                            '약품 수납장', '공구 수납장', '상자', '싱크대', '커피 머신', '믹서 설비', '게시판', '액자 증서',
                            '데스크톱 컴퓨터', '개집', '변기', '운동 기구', '깃발 장식', '냉장고', '묘비', '오븐', '조리 기기',
                            '벽 장식', '조명 기구', '우편함', '마네킹', '벽걸이 지도', '락커', '스툴', '마이크', '전자레인지',
                            '거울', '수혈 장비', '디스펜서', '푸톤', '액자 장식', '팔레트', '팝콘 기기', '포스터', '프로젝터',
                            '바비큐 그릴', '도로 차단물', '안전 콘', '위성 안테나', '체중계', '바구니', '표지판', '음료 기기',
                            '카메라 장비', '토스터', '소변기', '벽시계', '정수기', '깨진 유리'}
        furniture_category = ((meaning[0] == 'identity_label' and meaning[1] in furniture_labels
                               or (item in sources.BROKEN_GLASS_ITEMS and meaning == ['state_label', 'broken_glass']))
                              and any(f['payload'] == {'function': 'place_moveable_furniture'} for f in per_item[item]))
        cleaning_labels = {'Base.Soap2': '비누', 'Base.CleaningLiquid2': '세정액', 'Base.Bleach': '생활 소모품',
                           'Base.Broom': '생활 도구', 'Base.Mop': '대걸레', 'Base.DishCloth': '행주', 'Base.BathTowel': '목욕 수건'}
        cleaning_category = (meaning == ['identity_label', cleaning_labels.get(item)] and
                             any(f['payload'] in ({'function': 'wash_body'}, {'function': 'clean_world_blood'}) for f in per_item[item]))
        weapon_category = (meaning in (['identity_label', 'spear'], ['identity_label', '근접 무기'])
                           and any(f['payload'] == {'function': 'melee_attack'} for f in per_item[item]))
        wrist_labels = {
            'ClassicBlack': {'손목시계', '클래식 손목시계 (검은색)'},
            'ClassicBrown': {'손목시계', '클래식 손목시계 (갈색)'},
            'ClassicGold': {'금색 손목시계', '손목시계 (금)'},
            'ClassicMilitary': {'군용 손목시계'},
            'DigitalBlack': {'디지털 손목시계', '디지털 손목시계 (검은색)'},
            'DigitalRed': {'디지털 손목시계', '디지털 손목시계 (빨간색)'},
            'DigitalDress': {'디지털 손목시계', '디지털 손목시계 (메탈릭 드레스 스타일)'},
        }
        wrist_category = (meaning[0] == 'identity_label' and item.startswith(('Base.WristWatch_Left_', 'Base.WristWatch_Right_'))
                          and meaning[1] in wrist_labels.get(item.rsplit('_', 1)[-1], set()))
        disinfectant_category = (meaning == ['identity_label', '소독약'] and
                                 any(f['payload'] == {'function': 'disinfect_wound'} for f in per_item[item]))
        camping_category = ((item == 'camping.Flint' and meaning == ['identity_label', '부싯돌'])
                            or (item == 'camping.SteelAndFlint' and meaning == ['identity_label', '도구'])
                            or (item == 'camping.CampingTent' and meaning == ['context_label', 'camping']))
        media_category = (item in {'Base.Disc_Retail', 'Base.VHS_Retail', 'Base.VHS_Home'}
                          and meaning[0] == 'identity_label' and meaning[1] in {'CD', '비디오테이프', 'recorded_media'})
        radio_category = item.startswith('Radio.') and meaning == ['identity_label', '무전기']
        appearance_labels = {'Base.Hairgel': '헤어젤', 'Base.Razor': '면도기', 'Base.Mirror': '거울',
            'Base.MakeupEyeshadow': '아이 메이크업', 'Base.MakeupFoundation': '파운데이션', 'Base.Lipstick': '립스틱',
            'Base.BathTowelWet': '목욕 수건', 'Base.DishClothWet': '행주', 'Base.WildGarlic': '약재'}
        appearance_labels.update({'Base.' + name: label for name, label in {
            'Bell': '종', 'Belt': '허리띠', 'CleaningLiquid': '세정액', 'Soap': '비누', 'Dart': '다트',
            'CarvingFork': '고기 포크', 'GrillBrush': '그릴 브러시', 'Handle': '건설 재료',
            'EmptyJar': '조리 용기', 'JarLid': '조리 용기', 'MuffinTray': '머핀 쟁반', 'RoastingPan': '로스팅 팬',
            'Amplifier': '증폭기', 'MotionSensor': '동작 감지 센서', 'Radio': '휴대용 라디오',
            'Teabag': '티백', 'Umbrella': '우산', 'WaterDish': '물그릇'}.items()})
        appearance_labels.update({'Radio.ElectricWire': '전선', 'Radio.RadioReceiver': '무전 수신기',
                                  'Radio.RadioTransmitter': '무전 송신기'})
        appearance_category = (meaning == ['identity_label', appearance_labels.get(item)] or
                               item.startswith('Base.HairDye') and meaning == ['identity_label', '염색약'])
        # Reviewed standalone names/categories only. State-bearing names and
        # claims about material roles, powered operation or consumption stay out.
        reviewed_names = set('''건전지|전력 장치|전기 회로 부속|차량 배터리|전구|풀무|석탄|금속 드럼|솔방울|잔가지|.223 탄창|.308 탄창|.44 매그넘 탄창|.45 자동 탄창|5.56mm 탄창|9mm 탄창|D-E 권총|JS-2000 산탄총|M14 단발 자동소총|M16 자동소총|M1911 권총|M36 리볼버|M625 리볼버|M9 권총|nail|screw|soup_or_stew|가정용 소모품|고무 오리|공|공구 가방|광대 분장|눈가 분장|더블 배럴 산탄총|더플백|도시락통|라임|런치백|레몬|매그넘|번철 팬|병|볼링 가방|부용 큐브|비닐봉지|빨간 펜|사냥용 소총|사료 통조림|생활 도구|손잡이 냄비|수렵총|수박|식재료|아이섀도|안경류|양초|엔진 부품|연필|옥수수 가루|옥수수 분말|용기|우산|의료 가방|의료 도구|의료 보호구|의약품|인스턴트 팝콘|입술 화장|자루|잡동사니|장비 가방|전면 분장|전면 위장 분장|절구와 공이|조명 기구|종이봉투|종이클립|종이클립 상자|주전자|지갑 가방|지우개|총기 케이스|코르크 따개|토트백|톱|티백|티슈|파란 펜|펜|풋볼|프라이팬|플라스틱 컵|해골 분장|핸드백|허리 가방|화장지|휴대 가방|휴대 케이스'''.split('|'))
        reviewed_names.update({'건설 재료', '금속 재료', '목재 재료', '로프 재료', '기호품', '재료', '즉석 둔기', '창류 무기', '착용형 도구', 'alcoholic_drink', '음료'})
        reviewed_name = meaning[0] == 'identity_label' and meaning[1] in reviewed_names
        if ((meaning[0] == 'identity_label' and meaning[1] in {'식품', '의류', '액세서리', '기술 서적'} | CLOTHING_LABEL_LOCATIONS.keys() | DISPLAY_LABELS.keys())
                or reviewed_name or appearance_category or radio_category or media_category or camping_category or garden_category or vessel_category or key_category or pill_category or fishing_category or artificial_category or disinfectant_category or household_category or alarm_category or household_clock_category or wrist_category or obsolete_clock_category or panel_category or storage_category or weapon_category or map_category or cleaning_category or furniture_category or construction_part_category or scissors_category):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            expected_type = {'식품': 'Food', '기술 서적': 'Literature'}.get(meaning[1], 'Clothing')
            skill_label = meaning[1] != '기술 서적' or (fields.get('SkillTrained') and 'SkillTrained' not in conflicts)
            clothing_label = meaning[1] not in CLOTHING_LABEL_LOCATIONS or (
                fields.get('BodyLocation') in CLOTHING_LABEL_LOCATIONS[meaning[1]] and 'BodyLocation' not in conflicts
                and any(f['payload'] == {'state': 'worn_location', 'value': fields['BodyLocation']} for f in per_item[item]))
            display_label = fields.get('DisplayCategory') in DISPLAY_LABELS.get(meaning[1], set()) and 'DisplayCategory' not in conflicts
            native_label = meaning[1] in {'식품', '의류', '액세서리', '기술 서적'} | CLOTHING_LABEL_LOCATIONS.keys()
            fishing_label = ((meaning[1] in {'낚싯대', 'fishing_rod'} and 'FishingRod' in fields.get('Tags', '').split(';') and 'Tags' not in conflicts)
                             or (meaning[1] == 'bait_fish' and item == 'Base.BaitFish' and fields.get('Type') == 'Food' and 'Type' not in conflicts)
                             or (artificial_category and base.get('fishing_lure_properties', {}).get(item, {}).get('plastic') is True))
            household_label = household_category and fields.get('DisplayCategory') and 'DisplayCategory' not in conflicts
            alarm_label = ((alarm_category or household_clock_category) and fields.get('DisplayName') == 'Alarm Clock'
                           and not {'DisplayName', 'Type'} & conflicts.keys())
            alarm_label = alarm_label or (obsolete_clock_category and fields.get('Type') == 'AlarmClock'
                                         and fields.get('DisplayName') == 'Digital Watch' and not conflicts)
            wrist_label = (wrist_category and fields.get('Type') == 'AlarmClockClothing'
                           and fields.get('ClothingItem') == item.split('.', 1)[1] and not conflicts)
            weapon_label = weapon_category and (meaning[1] != 'spear' or 'Spear' in fields.get('Categories', '').split(';')) and 'Categories' not in conflicts
            furniture_label = furniture_category and fields.get('Type') == 'Moveable' and fields.get('WorldObjectSprite') and not conflicts
            construction_part_label = (construction_part_category and fields.get('Type') == 'Normal' and not conflicts
                                       and fields.get('DisplayName') == construction_part_labels[item][1])
            pill_label = (pill_category and fields.get('Type') == 'Drainable' and fields.get('DisplayCategory') == 'FirstAid'
                          and fields.get('DisplayName') == pill_labels[item][1] and not conflicts)
            key_label = key_category and fields.get('Type') == 'Key' and fields.get('DisplayName') == key_labels[item][1] and not conflicts
            key_label = key_label or (garden_category and fields.get('DisplayCategory') == 'Gardening' and not conflicts) or (vessel_category and fields.get('CanStoreWater', '').lower() == 'true' and not conflicts)
            key_label = key_label or (camping_category and fields.get('Type') == 'Normal' and not conflicts
                and fields.get('DisplayName') == {'camping.Flint': 'Flint', 'camping.SteelAndFlint': 'Flint and Steel',
                                                 'camping.CampingTent': 'Tent'}[item])
            key_label = key_label or (radio_category and fields.get('Type') == 'Radio' and not conflicts)
            key_label = key_label or (appearance_category and fields.get('Type') in {'Normal', 'Drainable'} and not conflicts
                and (item in appearance_labels or fields.get('HairDye', '').lower() == 'true'))
            key_label = key_label or (media_category and fields.get('Type') == 'Normal' and fields.get('MediaCategory')
                                      and not conflicts and any(f['payload'] == {'function': 'insert_recorded_media'} for f in per_item[item]))
            electrical_label = (item in base.get('electrical_control_sources', {}) and not conflicts and meaning[1] == {
                'Base.Battery': '건전지', 'Base.Generator': '전력 장치', 'Base.ElectronicsScrap': '전기 회로 부속',
                **{i: '차량 배터리' for i in ('Base.CarBattery1', 'Base.CarBattery2', 'Base.CarBattery3')},
                **{i: '전구' for i in sources.LIGHT_BULBS}}.get(item))
            electrical_label = electrical_label or (not conflicts and meaning[1] == {
                'Base.Bellows': '풀무', 'Base.Coal': '석탄', 'Base.Log': '건설 재료', 'Base.MetalDrum': '금속 드럼',
                'Base.Pinecone': '솔방울', 'Base.TreeBranch': '목재 재료', 'Base.Twigs': '잔가지',
                'Base.UnusableWood': '쓸모없는 목재', 'Base.PopBottleEmpty': '병', 'Base.WhiskeyEmpty': '병',
                'Base.WineEmpty': '병', 'Base.WineEmpty2': '병'}.get(item)
                and fields.get('Type') in {'Normal', 'Drainable'})
            reviewed_name_bound = reviewed_name and bool(fields.get('Type')) and not {'Type', 'DisplayName', 'DisplayCategory'} & conflicts.keys()
            if reviewed_name_bound or electrical_label or key_label or pill_label or display_label or fishing_label or disinfectant_category or household_label or alarm_label or wrist_label or panel_category or storage_category or weapon_label or cleaning_category or furniture_label or construction_part_label or (scissors_category and fields.get('Type') == 'Weapon' and fields.get('DisplayCategory') == 'Household' and not conflicts) or (map_category and fields.get('Type') == 'Map' and 'Type' not in conflicts) or (native_label and fields.get('Type') == expected_type and 'Type' not in conflicts and skill_label and clothing_label):
                reason = ('Remove the standalone taxonomy label from Layer 3: this exact label supplies only a category, '
                          'which ARCHITECTURE assigns to Layer 2 navigation. This is responsibility removal, not a '
                          'claim that a replacement classification surface was inspected or that function/state meanings '
                          'were relocated. Independent use, effect, location, and acquisition claims remain accounted separately.')
                evidence = [base['reader'].bindings[records[0]['path']], base['reader'].bindings['docs/ARCHITECTURE.md']]
                if artificial_category:
                    evidence.append(base['reader'].bindings[sources.FISHING_PROPERTIES])
                if disinfectant_category:
                    evidence.extend(base['reader'].bindings[p] for p in (sources.HEALTH, sources.DISINFECT))
                claim.update(migration_disposition='responsibility_removed', reason=reason,
                             verified_source_refs=evidence, remaining_work=None, remaining_uncertainty=None,
                             source_binding='source_and_owner_bound', source_strength='responsibility_boundary', review_state='reviewed',
                             owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': '정보 계층 / 2계층 and 3계층',
                                                      'destination_presence': 'not_claimed', 'declaration_type': fields.get('Type'),
                                                      'declared_display_category': fields.get('DisplayCategory'),
                                                      'declared_body_location': fields.get('BodyLocation')})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                                     'migration_disposition': 'responsibility_removed', 'successor_fact_refs': [],
                                     'locales': {}, 'residual': None, 'removal_reason': reason,
                                     'conservation_status': 'responsibility_removed'})
                continue
        candidates = per_item[item]
        if ((item.startswith('Base.LogStacks') and meaning == ['output_identity', 'logs'])
                or (item == 'Base.Frog' and meaning == ['output_identity', 'frog_meat'])
                or (item == 'Base.BrokenFishingNet' and meaning == ['function', 'recover_wire'])):
            selected = {'Base.Frog': 'prepare_frog_meat', 'Base.BrokenFishingNet': 'process_broken_fish_net'}.get(item, 'unbundle_logs')
            partial = [f for f in candidates if f['payload'] == {'function': selected}]
            if partial:
                evidence = sorted({o['source_path'] for f in partial for p in f['provenance_refs']
                                   for o in [semantic_payload['observations'][r] for r in semantic_payload['provenance'][p.split('/', 1)[-1]]['observation_refs']]})
                uncertainty = {'meaning': meaning,
                    'examined': sources.WIRE_RECOVERY if item == 'Base.BrokenFishingNet' else
                                sources.FROG_PREPARATION if item == 'Base.Frog' else sources.LOG_BINDING,
                    'required_input': 'Native RecipeManager exact result identity/count and inventory delivery' +
                                      (' including the unnormalized Result:Wire;3 parser behavior' if item == 'Base.BrokenFishingNet' else ''),
                    'reason': 'The source-confirmed transformation input and actual callback are represented, while the claimed returned item depends on the exact native result creation/delivery boundary. No returned item or numeric yield is invented from the display text.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=[f['ref'] for f in partial],
                    verified_source_refs=[base['reader'].bindings[p] for p in evidence], remaining_work=None,
                    remaining_uncertainty=uncertainty, reason=uncertainty['reason'], source_binding='source_bound',
                    source_strength='exact_recipe_result_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [f['ref'] for f in partial], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.WildGarlic' and meaning in (['function', 'disinfect_wound'], ['function', 'medicate_wound']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Normal' and not conflicts:
                paths = {records[0]['path'], semantic.MENU, sources.HEALTH, sources.DISINFECT, *sources.POULTICES.values()}
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'dispatch': 'Disinfection selects actual alcoholic/disinfectant supply, and poultice application selects WildGarlicCataplasm. The exact Normal WildGarlic raw plant matches neither, and Food WildGarlic2 is not an alias.'},
                    'required_input': 'An exact consumer selecting raw Base.WildGarlic for the claimed direct wound treatment',
                    'reason': 'The available health consumers do not establish direct disinfection or medication with the raw plant. Its hidden recipe input role is represented independently and cannot substitute for direct treatment.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='examined_exact_dispatch_gap', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if (item.startswith('Base.HairDye') and meaning[:2] == ['visual_effect', 'dye_color'] or
                item in {'Base.Lipstick', 'Base.MakeupEyeshadow'} and meaning[0] == 'visual_effect'):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if not conflicts and (fields.get('HairDye', '').lower() == 'true' or fields.get('MakeUpType') in {'Lips', 'Eyes'}):
                dye = fields.get('HairDye', '').lower() == 'true'
                paths = {records[0]['path'], semantic.MENU, semantic.DYE} if dye else {
                    records[0]['path'], semantic.MENU, sources.MAKEUP_UI, sources.MAKEUP_DEFINITIONS}
                partial = [f['ref'] for f in candidates if f['payload'].get('function') in {
                    'dye_hair_or_beard', 'apply_lip_makeup', 'apply_eye_makeup'}]
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'consumer': sources.DYE_APPLICATION if dye else sources.MAKEUP_LIFECYCLE},
                    'required_input': ('Native binding of declared RGB values to dye getters and visual color rendering; especially Ginger declares Strawberry Blonde, independently from Blonde' if dye else
                                       'Exact registered makeup item visual/texture binding and native worn-slot rendering'),
                    'reason': 'The actual color setter or cosmetic item replacement is represented. The predecessor named visible color is separate from its label and cannot be proved by a registry/item name without the exact native visual binding.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)], remaining_work=None,
                    remaining_uncertainty=uncertainty, reason=uncertainty['reason'], source_binding='source_bound',
                    source_strength='exact_visual_binding_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item in {'Base.BathTowelWet', 'Base.DishClothWet'} and meaning in (
                ['function', 'dry_towel'], ['function', 'dry_the_body'],
                ['condition', 'body_drying', 'after_towel_dries'], ['state_label', 'wet_towel']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Wet', '').lower() == 'true' and fields.get('ItemWhenDry') == item[:-3] and not conflicts:
                paths = {records[0]['path'], semantic.MENU, sources.DRY_BODY, sources.WORLD_MENU, sources.CLEAN_BLOOD}
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'dispatch': 'Exact dry BathTowel/DishCloth are selected for body drying and world blood cleaning. Wet siblings are not selected and have no Lua drying action. Wet, WetCooldown and ItemWhenDry are native item fields.'},
                    'required_input': 'Exact native Wet/WetCooldown/ItemWhenDry executor, returned item identity and remaining-use state before the represented dry-form body action',
                    'reason': 'The source declares a dry-form target but supplies no executor proving when the wet form dries or returns with usable supply. The predecessor automatic-drying/reuse implication remains bounded to that native transition; the dry-form action is independently represented.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_wet_item_executor_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['effect', 'garment_protection', 'increase'] and item == 'Base.LeatherStrips':
            partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'apply_garment_patch'}]
            if partial:
                uncertainty = {'meaning': meaning, 'partial_fact_refs': partial,
                    'examined': 'ISGarmentUI offers the selected LeatherStrips to repairClothing. Its tooltip calls native canFullyRestore/getScratchDefenseFromItem/getBiteDefenseFromItem; ISRepairClothing calls clothing:addPatch with the actual selected fabric.',
                    'required_input': 'Clothing.addPatch/canFullyRestore and fabric-to-scratch/bite-defense calculations for LeatherStrips and the selected garment part',
                    'reason': 'Patching/padding use and its material, thread, needle, part and interruption conditions are represented. The native garment/fabric calculation decides restoration versus protection and the resulting values; a leather label does not establish an unconditional defense increase.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in (sources.GARMENT_UI, sources.PATCH_GARMENT, semantic.MENU)],
                    reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                    source_binding='source_bound', source_strength='exact_native_patch_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.Bleach' and meaning == ['hazard', 'toxic_bleach']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Poison', '').lower() == 'true' and not {'Poison', 'PoisonPower', 'UseForPoison'} & conflicts.keys():
                uncertainty = {'meaning': meaning,
                    'examined': {k: fields.get(k) for k in ('Type', 'CustomContextMenu', 'Poison', 'PoisonPower', 'PoisonDetectionLevel', 'UseForPoison', 'ReplaceOnUse')},
                    'required_input': 'IsoGameCharacter.Eat and native evolved-recipe poisoning interpretation of this exact Bleach declaration',
                    'reason': 'The script declares Poison=true/PoisonPower=120 and the consumption action delegates to character:Eat. Evolved-recipe selection applies the explicit EnablePoisoning/Bleach policy. Those declarations and guards do not establish a contact hazard or quantify the resulting toxicity; native poisoning execution remains. The independent world-blood cleaning function is represented.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, semantic.EAT)],
                    reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                    source_binding='source_bound', source_strength='exact_native_poisoning_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['attack_form', 'thrust']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Weapon' and fields.get('SwingAnim') == 'Spear' and not {'Type', 'SwingAnim', 'Categories'} & conflicts.keys():
                partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'melee_attack'}]
                uncertainty = {'meaning': meaning,
                    'examined': {'SwingAnim': fields['SwingAnim'], 'Categories': fields.get('Categories'), 'DamageCategory': fields.get('DamageCategory'),
                                 'consumer': 'attackHook dispatches DoAttack through the non-ranged branch without interpreting the Spear animation token.'},
                    'required_input': 'DoAttack/Spear animation selection defining the actual thrust motion for this exact weapon',
                    'reason': 'Conditional melee use is represented. The Spear animation and sound labels are source leads, not the motion consumer; they do not independently identify the claimed thrust motion.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in (records[0]['path'], sources.FIREARM)],
                    reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                    source_binding='source_bound', source_strength='exact_attack_animation_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.AlarmClock' and meaning in (
                ['effect', 'device_sound', 'after_delay'], ['condition', 'device_sound', 'after_placement'],
                ['function', 'reuse_activated_device']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('PhysicsObject') == 'NoiseGenerator' and not conflicts:
                partial = [f['ref'] for f in candidates if f['payload'].get('function') in {
                    'set_device_timer', 'place_noise_device', 'retrieve_placed_device'}]
                paths = [records[0]['path'], semantic.MENU, sources.DEVICE_TIMER, sources.DEVICE_PLACE,
                         sources.WORLD_MENU, sources.DEVICE_TAKE]
                reuse = meaning == ['function', 'reuse_activated_device']
                uncertainty = {'meaning': meaning, 'examined': {
                    'declaration': {k: fields.get(k) for k in ('Type', 'PhysicsObject', 'NoiseRange', 'ExplosionTimer', 'CanBePlaced', 'CanBeReused', 'OBSOLETE')},
                    'consumer': 'The positive timer dialog saves a numeric setting; placement constructs IsoTrap. Retrieval returns trap:getItem only while an object and item remain. None of these Lua paths defines the sound event or post-activation item retention.'},
                    'required_input': ('IsoTrap activation/item retention and CanBeReused interpretation' if reuse else
                                       'IsoTrap countdown/NoiseGenerator sound execution after placement') + '; runtime availability of this OBSOLETE declaration',
                    'reason': ('Conditional retrieval is represented, but it does not establish survival through activation or repeat use. CanBeReused is a source lead whose native consumer is missing.' if reuse else
                               'The delay setter and placement are represented independently. The native IsoTrap executor determines when and whether the declared sound is emitted; timer and sound field names alone do not establish that effect.')}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in paths], reason=uncertainty['reason'],
                    remaining_uncertainty=uncertainty, remaining_work=None, source_binding='source_bound',
                    source_strength='exact_device_executor_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item in {'Base.SheetRope', 'Base.Rope'} and meaning == ['function', 'traverse_installed_rope']:
            records = base['declarations'].get(item, [])
            paths = {records[0]['path'], sources.WORLD_MENU, sources.ADD_ROPE, sources.REMOVE_ROPE,
                     sources.CLIMB_ROPE, sources.OBJECT_COMMANDS}
            partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'start_escape_rope_ascent'}]
            uncertainty = {'meaning': meaning,
                'examined': 'The active installed-rope menu passes down=false, walks to the rope square and queues the guarded native ascent call. ISClimbSheetRopeAction also contains a down=true branch, but this local menu does not select it. Add/remove actions and server attachment-type dispatch are independently interpreted.',
                'required_input': 'Native installed-rope traversal and descent entry, including current rope continuity, attachment, character eligibility and completion',
                'reason': 'Conditional ascent control is represented, but the broader up/down climbing statement includes native traversal and descent. Merely defining a down branch does not establish its active local selection or successful travel. The exact remainder is retained independently of the installation material role.'}
            claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                         verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                         remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                         source_binding='source_bound', source_strength='exact_installed_rope_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if item in sources.BROKEN_GLASS_ITEMS and meaning == ['caution', 'approaching_broken_glass']:
            records = base['declarations'].get(item, [])
            paths = {records[0]['path'], sources.WORLD_MENU, sources.PICKUP_GLASS, sources.WINDOW_GLASS,
                     sources.MOVE_TOOLS, semantic.PROPS}
            uncertainty = {'meaning': meaning,
                'examined': {'sprite': sources.stable_properties(records[0])[0].get('WorldObjectSprite'),
                    'pickup': 'The active pickup action and IsoBrokenGlass branch explicitly scratch/embed glass in an ungloved hand under random checks. These are pickup effects, not an approach or foot-contact trigger.',
                    'placement': 'Moveable placement constructs IsoBrokenGlass from native sprite IsoType; the Lua constructor caller does not execute contact/foot injury.',
                    'window': 'The separate window-frame removal action calls removeBrokenGlass on a smashed window and does not consume this shard item.'},
                'required_input': 'Native contact/foot-injury handling for the exact placed IsoBrokenGlass sprite, including actual triggering contact and footwear conditions',
                'reason': 'The predecessor approach warning is independent of the source-confirmed pickup hazard. Available placement and pickup Lua have been interpreted; they do not establish this contact effect or an approach radius. That specific engine behavior remains unresolved.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                         remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                         source_binding='source_bound', source_strength='exact_glass_contact_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        matched = []
        furniture_gloss = (meaning in (['context_label', 'equipment_layout'], ['context_label', 'decoration_layout'],
                                      ['context_label', 'indoor_furniture_layout'], ['context_label', 'storage_furniture_layout'],
                                      ['intended_use', 'area_marking'])
                           and any(f['payload'] == {'function': 'place_moveable_furniture'} for f in per_item[item]))
        construction_meanings = {'bed_construction': {'onBed'}, 'drawer_table_construction': {'onSmallWoodTableWithDrawer'},
            'door_construction': {'onWoodenDoor', 'onDoubleWoodenDoor'}, 'hinged_structure_construction': {'onWoodenDoor', 'onDoubleWoodenDoor'},
            'barbed_fence_construction': {'onBarbedFence'}, 'bag_barrier_construction': {'onSangBagWall', 'onGravelBagWall'}}
        construction_claim = (meaning[0] == 'role' and meaning[1] in construction_meanings and meaning[2] == 'material'
                              and any(r['factory'] in construction_meanings[meaning[1]] and r['status'] == 'active_material'
                                      for r in base.get('factory_relations', {}).get(item, [])))
        if item in sources.BROKEN_GLASS_ITEMS and meaning == ['caution', 'clearing_broken_glass']:
            matched = [f for f in candidates if f['payload'].get('direction') == 'apply_during_glass_pickup']
        elif construction_claim:
            matched = [f for f in candidates if f['payload'] == {'role': 'material'} and f['context_ref']
                       and (facts[f['context_ref']]['payload'] == {'activity': 'carpentry_menu_construction'}
                            or (meaning[1] == 'hinged_structure_construction'
                                and facts[f['context_ref']]['payload'] == {'activity': 'metal_welding_construction'}))]
        elif meaning == ['role', 'stone_hammer_crafting', 'material'] and item == 'Base.Stone':
            matched = [f for f in candidates if f['payload'] == {'role': 'material'} and f['context_ref']
                       and facts[f['context_ref']]['payload'] == {'activity': 'tool_crafting'}]
        elif item in {'Base.Plantain', 'Base.Comfrey'} and meaning == ['identity_label', '식품']:
            matched = [f for f in candidates if f['payload'] == {'role': 'material'} and f['context_ref']
                       and facts[f['context_ref']]['payload'] == {'activity': 'poultice_preparation'}]
        elif item == 'Base.MakeupFoundation' and meaning == ['cosmetic_role', 'base_layer']:
            matched = [f for f in candidates if f['payload'] == {'function': 'apply_makeup'}]
        elif furniture_gloss:
            matched = [f for f in candidates if f['payload'] in ({'function': 'place_moveable_furniture'}, {'function': 'remove_placed_furniture'})]
        elif ((item == 'Base.Thread' and meaning in (['role_unspecified_context', 'material'], ['role', 'fabric_crafting', 'material'], ['consumption_property', 'consumable']))
                or (item == 'Base.LeatherStrips' and meaning == ['material_form', 'leather_patch'])):
            matched = [f for f in candidates if f['payload'] == {'function': 'apply_garment_patch'}]
        elif meaning == ['intended_use', 'navigation_planning'] and item in base.get('item_map_sources', {}):
            # Correct the human-use gloss to the actual viewer operation. It does
            # not establish an automatic route planner or safe/accurate route.
            matched = [f for f in candidates if f['payload'] == {'function': 'view_item_map'}]
        elif item in sources.STRAP_SPEED and meaning in (
                ['effect', 'reload_speed', 'increase'], ['condition', 'reload_speed', 'worn'],
                ['condition', 'reload_speed', 'shotgun' if item.endswith('_Shells') else 'non_shotgun']):
            matched = [f for f in candidates if f['payload'] == (
                {'property': 'reload_speed_setting', 'direction': 'multiply_1_15'} if meaning[0] == 'effect' else
                {'predicate': sources.STRAP_SPEED[item]})]
        elif meaning == ['identity_label', '손상 낚싯대'] and item == 'Base.FishingRodBreak':
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.ROD_REPAIR_INPUT}]
        elif meaning[0] in {'acquisition_zone', 'acquisition_method'} or meaning in [['acquisition_place', 'urban areas'], ['acquisition_place', 'trailer parks']]:
            zone = (meaning[1] if meaning[0] == 'acquisition_zone' else
                    {'urban areas': 'TownZone', 'trailer parks': 'TrailerPark'}.get(meaning[1]))
            for fact in candidates:
                if fact['fact_kind'] != 'acquisition' or fact['payload']['route']['method'] not in {'foraging', 'foraging_crop_seed'}:
                    continue
                conditions = fact['payload']['conditions']
                item_zones = {z for z, w in acquisition_expression.weights(conditions['zones']) if float(w) > 0}
                category_zones = {z for c in conditions['category_conditions'].values()
                                  for z, w in acquisition_expression.weights(c['zoneChance']) if float(w) > 0}
                if (zone is None and meaning == ['acquisition_method', 'foraging']) or zone in item_zones & category_zones:
                    matched.append(fact)
        elif item in base.get('vehicle_storage_sources', {}) and meaning in (
                ['function', 'sit_on_vehicle_seat'], ['function', 'sit_in_vehicle']):
            matched = [f for f in candidates if f['payload'] == {'function': 'use_vehicle_seat'}]
        elif item in base.get('vehicle_storage_sources', {}) and meaning in (
                ['function', 'install_vehicle_part'], ['function', 'install_vehicle_seat']):
            matched = [f for f in candidates if f['payload'] == {'function': 'install_vehicle_storage_part'}]
        elif item in base.get('vehicle_storage_sources', {}) and meaning == ['function', 'store_items_on_vehicle_seat']:
            matched = [f for f in candidates if f['payload'] == {'function': 'store_vehicle_items'}]
        elif meaning == ['function', 'reuse_container']:
            matched = [f for f in candidates if f['payload'] == {'function': 'store_water'}]
        elif meaning[0] == 'function':
            matched = [f for f in candidates if f['payload'] == {'function': meaning[1]}]
            if meaning[1] in {'eat_food', 'drink_food'}:
                matched = [f for f in candidates if f['payload'].get('function') in
                    ({'eat_food', 'consume_edible_food', 'drink_food_contents'} if meaning[1] == 'eat_food'
                     else {'drink_food_contents'})]
            if meaning[1] == 'light_campfire' and item in sources.PETROL_ITEMS:
                matched = [f for f in candidates if f['payload'] == {'function': 'light_campfire_with_petrol'}]
            if meaning[1] == 'catch_animals' and item == 'Base.TrapStick':
                matched = [f for f in candidates if f['payload'] == {'function': 'catch_trap_animal'}]
            if meaning[1] == 'erase_item_map_annotations':
                matched = [f for f in candidates if f['payload'] == {'function': 'erase_map_annotations'}]
            if meaning[1] == 'insert_device_battery' and item == 'Base.Rubberducky2':
                matched = [f for f in candidates if f['payload'] == {'function': 'accept_battery_charge'}]
            if meaning[1] == 'light_campfire' and item == 'Base.PercedWood':
                matched = [f for f in candidates if f['payload'] == {'function': 'light_campfire_by_friction'}]
            if meaning[1] == 'fold_umbrella' and item.startswith('Base.ClosedUmbrella'):
                matched = [f for f in candidates if f['payload'] == {'function': 'unfold_umbrella'}]
            if item == 'Base.FishingNet' and meaning[1] == 'catch_bait_fish':
                matched = [f for f in candidates if f['payload'] == {'function': 'check_fishing_net'}]
            fuel_function = ({'blow_forge_air': 'use_furnace_bellows'} if item == 'Base.Bellows' else
                {'supply_charcoal_barbecue_fuel': 'supply_hearth_fuel'} if item == 'Base.Charcoal' else
                {'transfer_fuel': 'transfer_vehicle_fuel', 'refuel_vehicle': 'transfer_vehicle_fuel',
                 'supply_fuel': 'refuel_generator', 'carry_gasoline': 'transfer_vehicle_fuel'} if item in sources.PETROL_ITEMS else
                {'store_fuel': 'fill_petrol_container', 'carry_fuel': 'transfer_vehicle_fuel'} if item in sources.EMPTY_PETROL_ITEMS else {})
            if meaning[1] in fuel_function:
                matched = [f for f in candidates if f['payload'] == {'function': fuel_function[meaning[1]]}]
            if meaning[1] == 'wash_clothing' and item in {'Base.Soap2', 'Base.CleaningLiquid2'}:
                matched = [f for f in candidates if f['payload'] == {'function': 'wash_equipment'}]
            if meaning[1] == 'sew_fabric' and item == 'Base.Needle':
                matched = [f for f in candidates if f['payload'] == {'function': 'apply_garment_patch'}]
            panel = base.get('vehicle_panel_sources', {}).get(item)
            if panel and meaning[1] in {'remove_vehicle_panel_or_glass', 'install_vehicle_panel_or_glass',
                                        'refit_vehicle_' + panel['part_meaning']}:
                operation = 'remove' if meaning[1] == 'remove_vehicle_panel_or_glass' else 'install'
                matched = [f for f in candidates if f['payload'] == {'function': operation + '_vehicle_' + panel['part_meaning']}]
            if meaning[1] == 'read_or_consult':
                matched = [f for f in candidates if f['payload'] == {'function': 'read_literature'}]
            if meaning[1] in {'write_documents', 'revise_documents'}:
                matched = [f for f in candidates if f['payload'] == {'function': 'write_note_pages'}]
            elif meaning[1] == 'attack_as_weapon':
                matched = [f for f in candidates if f['payload'].get('function') in {'melee_attack', 'fire_ammunition'}]
            if meaning[1] == 'wear_body':
                matched = [f for f in candidates if f['payload'].get('function') in {'wear_on_body', 'wear_configured_clothing'}]
            elif meaning[1] == 'redistribute_container_contents':
                matched = [f for f in candidates if f['payload'] == {'function': 'store_and_retrieve_items'}]
            elif meaning[1] == 'replace_vehicle_suspension' and item in base.get('vehicle_running_sources', {}):
                matched = [f for f in candidates if f['payload'].get('function') in {'install_vehicle_suspension', 'remove_vehicle_suspension'}]
            elif meaning[1] == 'adjust_vehicle_tire_pressure' and item == 'Base.TirePump':
                matched = [f for f in candidates if f['payload'] == {'function': 'inflate_vehicle_tire'}]
            elif meaning[1] == 'sow_seeds':
                matched = [f for f in candidates if f['payload'].get('function') in {'sow_seeds', 'sow_extracted_seeds'}]
        elif item in sources.DRAINABLE_MATERIALS and meaning in (
                ['role_unspecified_context', 'material'], ['consumption_property', 'consumable']):
            matched = [f for f in candidates if f['fact_kind'] == 'context_role'
                       and f['payload'].get('role') in {'material', 'repair_material', 'ingredient'}]
        elif item in {'Base.Twine', 'Base.Wire'} and meaning == ['role', 'fishing_net_crafting', 'material']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'fishing_gear_crafting'} and has_recipe(f, {'Make Fishing Net'})]
        elif item == 'Base.DuctTape' and meaning in (['role', 'device_assembly', 'material'], ['role', 'spear_upgrade', 'material']):
            context = 'explosive_modification' if meaning[1] == 'device_assembly' else 'spear_upgrade'
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': context}]
        elif item == 'Base.Woodglue' and meaning == ['role', 'repair', 'repair_material']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'repair_material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'repair'}]
        elif item == 'Base.WeldingRods' and (meaning == ['role', 'welding_construction', 'material']
                or meaning in (['context_example', 'welding_construction', 'metal_fences'], ['context_example', 'welding_construction', 'metal_doors'])):
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'metal_welding_construction'}]
        elif item == 'Base.Vinegar' and meaning == ['role', 'food_preparation', 'ingredient']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'vegetable_jarring'}]
        elif item in {'Base.GravyMix', 'Base.PancakeMix'} and meaning in (
                ['condition', 'gravy_preparation', 'water'], ['condition', 'pancake_preparation', 'water']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FOOD_ASSEMBLY}
                       and has_recipe(f, {'Make Gravy' if item == 'Base.GravyMix' else 'Make Pancake'})]
        elif item == 'Base.Battery' and meaning in (
                ['role', 'portable_device_power', 'power_supply'], ['example_target', 'portable_device_power', 'flashlight']):
            matched = [f for f in candidates if f['payload'] == {'function': 'supply_portable_device_charge'}]
        elif meaning == ['condition', 'lighting', 'replaceable_bulb']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.LAMP_BULB}]
        elif item == 'Base.CarBatteryCharger' and meaning == ['condition', 'battery_charging', 'removed_from_vehicle']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.CHARGER_CONTROLS}]
        elif item == 'Base.Generator' and meaning == ['condition', 'generator_power', 'installed']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.GENERATOR_CONTROL}]
        elif meaning == ['power_source', 'battery']:
            matched = [f for f in candidates if f['payload'] == {'function': 'accept_battery_charge'}]
        elif meaning[0] == 'output_identity' and meaning[1] in {'electronic_scrap', 'electronic_parts'}:
            matched = [f for f in candidates if f['payload'] == {'function': 'dismantle_electronics'}
                       and any(facts[q]['payload'] == {'predicate': sources.SCRAP_RECOVERY} for q in f['qualifier_refs'])]
        elif meaning[0] == 'effect':
            matched = [f for f in candidates if f['payload'] == {'property': meaning[1], 'direction': meaning[2]}]
            if item in {'Base.Soap2', 'Base.CleaningLiquid2'} and meaning[1:] in (['blood', 'remove'], ['dirt', 'remove']):
                matched = [f for f in candidates if f['payload'] == {'property': 'washed_surface_' + meaning[1], 'direction': 'remove'}]
            if meaning[1:] == ['fishing_lure', 'may_break']:
                matched = [f for f in candidates if f['payload'] == {'predicate': sources.FISHING_LURE_LOSS}]
            if meaning[1:] in (['skill_knowledge', 'gain'], ['recipe_knowledge', 'gain']):
                records = base['declarations'].get(item, [])
                fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
                if fields.get('SkillTrained') and not fields.get('TeachedRecipes') and not {'SkillTrained', 'TeachedRecipes'} & conflicts.keys():
                    matched = [f for f in candidates if f['payload'] == {'property': fields['SkillTrained'] + '_experience_multiplier', 'direction': 'increase'}]
            if meaning[1:] == ['food_sickness', 'increase_if_poisonous']:
                matched = [f for f in candidates if f['payload'] == {'property': 'food_sickness', 'direction': 'increase'}
                           and any(facts[q]['payload'] == {'predicate': sources.POISONOUS_WILD_FOOD} for q in f['qualifier_refs'])]
        elif meaning[0] == 'conditional_effect':
            predicate = {'smoker': sources.SMOKER_EFFECT, 'nonsmoker': sources.NONSMOKER_EFFECT}.get(meaning[3])
            matched = [f for f in candidates if f['payload'] == {'property': meaning[1], 'direction': meaning[2]}
                       and any(facts[q]['payload'] == {'predicate': predicate} for q in f['qualifier_refs'])]
        elif meaning == ['role', 'spear_upgrade', 'attachment']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'attachment'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'spear_upgrade'}]
        elif meaning[0] == 'role' and meaning[1] in {'tool_crafting', 'splint_crafting', 'fishing_gear_crafting', 'furniture_crafting', 'tent_kit_making', 'campfire_kit_preparation', 'poultice_preparation', 'bandaging_material_preparation', 'metal_forging', 'welded_parts', 'mattress_preparation', 'vegetable_jarring'} and meaning[2] in {'material', 'tool'}:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': meaning[2]}
                       and facts[f['context_ref']]['payload'] == {'activity': meaning[1]}]
        elif meaning == ['condition', 'vegetable_jarring', 'with_empty_jar']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.JAR_PREPARATION}]
        elif meaning[0] == 'role' and meaning[1:] in (['radio_crafting', 'material_or_component'], ['radio_crafting', 'material']):
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'radio_crafting'}]
        elif meaning[0] == 'role' and meaning[1] in PREPARATION_ROLES:
            context, names = PREPARATION_ROLES[meaning[1]]
            role = 'fuel' if meaning[2] == 'fuel_supply' else meaning[2]
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': role}
                       and (context is None or facts[f['context_ref']]['payload'] == {'activity': context})
                       and has_recipe(f, names)]
        elif meaning[0] == 'role' and meaning[1] in {'dough_preparation', 'batter_preparation', 'cookie_preparation', 'plaster_preparation', 'trap_crafting', 'woodworking'}:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': meaning[2]}
                       and facts[f['context_ref']]['payload'] == {'activity': meaning[1]}]
        elif meaning[0] == 'role' and meaning[1:] in (['food_preparation', 'tool'], ['food_preparation', 'container']):
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': meaning[2]}
                       and facts[f['context_ref']]['payload'].get('activity') in {'food_preparation', 'dough_preparation', 'batter_preparation', 'cookie_preparation', 'food_portioning', 'fish_preparation', 'animal_butchery', 'grain_preparation'}]
        elif meaning == ['role', 'sawing', 'tool']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'tool'}
                       and facts[f['context_ref']]['payload'].get('activity') in {'woodworking', 'shotgun_modification'}]
        elif meaning[0] == 'role' and meaning[1:] == ['food_preparation', 'ingredient']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'ingredient'}
                       and facts[f['context_ref']]['payload'].get('activity') in {'food_preparation', 'dough_preparation', 'batter_preparation'}]
            if not matched:
                matched = [f for f in candidates if f['payload'] == {'function': 'prepare_opened_food_ingredient'}]
        elif meaning[0] == 'role' and meaning[1:] in (['fire_starting', 'tinder'], ['burning', 'fuel']):
            function = 'provide_campfire_tinder' if meaning[2] == 'tinder' else 'supply_campfire_fuel'
            matched = [f for f in candidates if f['payload'] == {'function': function}]
        elif meaning == ['context', 'food_preparation']:
            matched = [f for f in candidates if f['payload'].get('activity') in {'food_preparation', 'dough_preparation', 'batter_preparation'}]
        elif meaning == ['context_label', 'medical_use']:
            matched = [f for f in candidates if f['payload'].get('function') in {'apply_bandage', 'disinfect_wound'}]
        elif item in sources.PETROL_ITEMS and meaning == ['context_label', 'vehicle_maintenance']:
            matched = [f for f in candidates if f['payload'] == {'function': 'transfer_vehicle_fuel'}]
        elif (item == 'Base.Coal' and meaning == ['role', 'furnace_fueling', 'fuel']
              or item == 'Base.Pinecone' and meaning == ['role', 'other_fire_fueling', 'fuel']):
            matched = [f for f in candidates if f['payload'] == {'function':
                'supply_furnace_fuel' if item == 'Base.Coal' else 'supply_hearth_fuel'}]
        elif meaning[0] == 'role' and meaning[1:] == ['firearm_loading', 'ammunition']:
            matched = [f for f in candidates if f['payload'] == {'function': 'load_matching_ammunition'}]
        elif meaning[0] == 'wear':
            matched = [f for f in candidates if f['payload'].get('state') == 'worn_location'
                       and f['payload']['value'] in WEAR_LOCATIONS.get(meaning[1], set())]
        elif meaning[0] == 'state':
            matched = [f for f in candidates if f['payload'] == {'state': meaning[1], 'value': meaning[2]}]
        elif meaning == ['condition', 'package_opening', 'can_opener']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.CAN_OPENING}]
        elif meaning[:2] == ['condition', 'campfire_lighting']:
            predicate = (sources.CAMP_FRICTION if meaning[2] == 'branch_or_stick' and item == 'Base.PercedWood'
                         else sources.CAMP_IGNITER if meaning[2] in {'tinder', 'tinder_or_fuel'} else None)
            matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
        elif meaning == ['condition', 'radio', 'tuned_frequency']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.RADIO_TUNING}]
        elif meaning in (['condition', 'door_lock', 'matching_key'], ['condition', 'padlock', 'matching_key']):
            predicate = sources.DOOR_KEY_USE if meaning[1] == 'door_lock' else sources.PADLOCK_KEY_USE
            matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
        elif meaning == ['condition', 'vehicle', 'matching_key']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.VEHICLE_KEY_USE}]
        elif meaning == ['condition', 'skill_reading', 'literate']:
            matched = [f for f in candidates if f['payload'] == {'predicate': 'The character can read, is awake, meets any book skill requirement, and the reading action remains valid for possession, page state and driving state.'}]
        elif meaning[:2] == ['condition', 'skill_multiplier']:
            predicate = (sources.READ_MAXIMUM if meaning[2] == 'full_reading_progress' else
                         'Reading progress yields a multiplier above the current one, and the reader is within this book\'s supported training level range.')
            matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
        elif meaning == ['condition', 'blood_cleaning', 'bleach_and_tool']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.BLOOD_CLEANING}]
        elif meaning == ['consumption_property', 'blood_cleaning', 'bleach_used']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.BLOOD_CLEANING}]
        elif meaning[:2] == ['condition', 'body_drying'] and meaning[2] in {'wet_body', 'uses_remaining'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.BODY_DRYING}]
        elif meaning == ['condition', 'ash_clearing', 'unbroken_broom'] and item == 'Base.Broom':
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.ASH_CLEARING}]
        elif item in {'Base.Dirtbag', 'Base.Gravelbag', 'Base.Sandbag'} and meaning in (
                ['role_unspecified_context', 'material'], ['consumption_property', 'consumable'], ['material_form', 'bag_of_dirt']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.GROUND_POUR}]
        elif (item in sources.PETROL_ITEMS | {'Base.Charcoal', 'Base.PropaneTank'} and meaning in (
                ['role_unspecified_context', 'material'], ['consumption_property', 'consumable'])):
            predicates = ({sources.VEHICLE_CONTAINER, sources.GENERATOR_REFUEL, sources.HEARTH_PETROL, sources.INDUSTRIAL_PETROL}
                if item in sources.PETROL_ITEMS else {sources.HEARTH_FUEL, sources.FURNACE_FUEL} if item == 'Base.Charcoal'
                else {sources.PROPANE_BARBECUE})
            matched = [f for f in candidates if f['payload'].get('predicate') in predicates]
        elif item == 'Base.FishingNet' and (meaning[:2] == ['condition', 'net_fishing']
                or meaning == ['hazard', 'net_breakage_after_time']):
            predicate = sources.NET_PLACEMENT if meaning[-1] in {'water', 'near_water'} else sources.NET_CHECKING
            matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
        elif item == 'Base.TrapStick' and meaning in (['condition', 'trapping', 'bait'], ['target_scope', 'trapping', 'birds']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.TRAP_BIRD}]
        elif item in {'Base.Jack', 'Base.LugWrench'} and meaning[0] == 'role' and meaning[1] in {'vehicle_tire_exchange', 'vehicle_brake_exchange'}:
            matched = [f for f in candidates if f['payload'] == {'function': 'service_vehicle_parts'}]
        elif item in {'Base.BucketPlasterFull', 'Base.CompostBag', 'Base.Fertilizer'} and meaning == ['consumption_property', 'consumable']:
            predicates = {sources.PLASTER_USE} if item == 'Base.BucketPlasterFull' else {sources.FERTILIZING}
            matched = [f for f in candidates if f['payload'].get('predicate') in predicates]
        elif meaning == ['consumption_property', 'consumable']:
            matched = [f for f in candidates if f['payload'].get('predicate') in {sources.DISINFECTION_USE, sources.BANDAGE_APPLICATION, sources.DIRTY_BANDAGING, sources.SPRAY_TREATMENT, sources.WATER_DRINKING}]
        elif meaning[:2] in (['condition', 'crop_spray'], ['constraint', 'crop_spray']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.SPRAY_TREATMENT}]
        elif meaning == ['role', 'crop_spray_preparation', 'material']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'crop_spray_preparation'}]
        elif meaning == ['condition', 'bandaging', 'injured_unbandaged_health_menu']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.BANDAGE_APPLICATION}]
        elif meaning == ['state_label', 'dirty_bandaging_material']:
            matched = [f for f in candidates if f['payload'] == {'property': 'applied_bandage_life', 'direction': 'set_zero'}]
        elif meaning[:2] == ['condition', 'disinfection'] and meaning[2] in {'unbandaged', 'injured', 'health_panel_selection'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.DISINFECTION}]
        elif meaning[:2] == ['condition', 'splinting'] and meaning[2] in {'fracture', 'not_splinted', 'not_stitched', 'head_torso_excluded'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.SPLINTING}]
        elif meaning[0] in {'eligible_animal', 'bait_example', 'animal_time'}:
            predicates = set()
            if meaning[0] == 'eligible_animal':
                predicates = {'rabbit': {sources.TRAP_RABBIT_SQUIRREL}, 'squirrel': {sources.TRAP_RABBIT_SQUIRREL},
                              'bird': {sources.TRAP_BIRD}, 'mouse_or_rat': {sources.TRAP_RODENTS}}.get(meaning[1], set())
            elif meaning[0] == 'bait_example':
                predicates = {'apple': {sources.TRAP_RABBIT_SQUIRREL}, 'corn': {sources.TRAP_RABBIT_SQUIRREL, sources.TRAP_BIRD},
                              'worm': {sources.TRAP_BIRD}, 'bread': {sources.TRAP_BIRD},
                              'cheese': {sources.TRAP_RODENTS}, 'peanut_butter': {sources.TRAP_RODENTS}}.get(meaning[1], set())
            elif meaning[1] in {'rabbit', 'squirrel'} and meaning[2] == 'night':
                predicates = {sources.TRAP_RABBIT_SQUIRREL}
            matched = [f for f in candidates if f['payload'].get('predicate') in predicates]
        elif meaning == ['condition', 'animal_trapping', 'no_time_limit']:
            matched = [f for f in candidates if f['payload'].get('predicate') in {sources.TRAP_BIRD, sources.TRAP_RODENTS}]
        elif meaning[:2] == ['condition', 'animal_trapping'] and meaning[2] in {'bait', 'accepted_bait', 'zone', 'bait_freshness', 'player_proximity'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.TRAP_CATCH}]
        elif meaning[:2] == ['condition', 'fertilizing'] and meaning[2] in {'living_crop', 'farming_menu'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FERTILIZING}]
        elif meaning == ['condition', 'crop_rot', 'excess_fertilizer']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FERTILIZER_ROT}]
        elif meaning == ['condition', 'fertilizing_outcome', 'previous_applications']:
            matched = [f for f in candidates if f['payload'].get('predicate') in {sources.FERTILIZER_GROWTH, sources.FERTILIZER_ROT}]
        elif meaning == ['condition', 'rod_fishing', 'lure_examples']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FISHING_LURES}]
        elif meaning in (['condition', 'rod_fishing', 'baitfish_pike'], ['condition', 'rod_fishing', 'artificial_species'],
                         ['constraint', 'rod_fishing', 'artificial_excludes_pike_baitfish']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FISHING_MATCHES}]
        elif ((meaning[:2] == ['condition', 'rod_fishing'] and meaning[2] in {
                'unbroken_rod', 'rod_and_bait_carried', 'carried_with_rod', 'water_fishing_menu', 'bait_attached'})
              or (meaning[:2] == ['condition', 'fishing_outcome'] and meaning[2] in {'lure_type', 'time', 'season'})
              or meaning == ['constraint', 'fishing_outcome', 'catch_not_guaranteed']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.ROD_FISHING}]
        elif meaning == ['consumption_property', 'fishing_lure', 'may_be_spent_or_lost']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FISHING_LURE_LOSS}]
        elif meaning == ['condition', 'note_writing', 'writing_implement']:
            from . import recovery
            matched = [f for f in candidates if f['payload'] == {'predicate': recovery.NOTE_EDIT}]
        alias_note = None
        if not matched:
            role_aliases = {
                ('Base.CandyPackage', ('function', 'unpack_food')): {('package_opening', 'material')},
                ('Base.MeatCleaver', ('function', 'cut_food')): {('food_portioning', 'tool'), ('fish_preparation', 'tool')},
                ('Base.MeatCleaver', ('function', 'butcher_small_animals')): {('animal_butchery', 'tool')},
                ('Base.Watermelon', ('function', 'slice_fruit')): {('food_portioning', 'ingredient')},
                ('Base.Watermelon', ('function', 'smash_fruit')): {('watermelon_breaking', 'ingredient')},
                ('Base.Watermelon', ('output_purpose', 'portions_for_eating')): {('food_portioning', 'ingredient')},
                ('Base.Muffintray_Biscuit', ('function', 'portion_biscuits')): {('food_portioning', 'ingredient')},
                ('Base.Muffintray_Biscuit', ('role', 'biscuit_preparation', 'base')): {('food_portioning', 'ingredient')},
                ('Base.Handle', ('function', 'fit_tool_parts')): {('metal_forging', 'material'), ('shovel_smithing', 'material')},
                ('Base.Handle', ('function', 'shape_tool_parts')): {('metal_forging', 'material'), ('shovel_smithing', 'material')},
                ('Base.Handle', ('context', 'construction_or_crafting')): {('metal_forging', 'material'), ('shovel_smithing', 'material')},
                ('Base.Frog', ('role', 'food_preparation', 'ingredient')): {('frog_preparation', 'material')},
                ('Base.BakingPan', ('role', 'food_preparation', 'tool')): {('food_preparation', 'container')},
                ('Base.BakingTray', ('role', 'food_preparation', 'tool')): {('cookie_preparation', 'container')},
                ('Base.Coffee2', ('function', 'add_food_ingredients')): {('food_preparation', 'ingredient')},
                ('Base.Coffee2', ('role', 'coffee_preparation', 'ingredient')): {('food_preparation', 'ingredient')},
                ('Base.Teabag2', ('role', 'tea_preparation', 'ingredient')): {('food_preparation', 'ingredient')},
                ('Base.RoastingPan', ('role', 'roasting_preparation', 'base')): {('food_ingredient_addition', 'base')},
                ('Base.GridlePan', ('role', 'stir_fry_preparation', 'base')): {('food_ingredient_addition', 'base')},
                ('Base.Pan', ('role', 'stir_fry_preparation', 'base')): {('food_ingredient_addition', 'base')},
                ('Base.TinOpener', ('role', 'package_opening', 'tool')): {('package_opening', 'tool')},
                ('Base.TreeBranch', ('role', 'spear_crafting', 'material')): {('spear_crafting', 'material')},
                ('Base.SharpedStone', ('role', 'spear_crafting', 'tool')): {('spear_crafting', 'tool')},
                ('Base.Scotchtape', ('role', 'repair', 'repair_material')): {('repair', 'repair_material')},
                ('Base.ScrapMetal', ('role', 'metal_welding_construction', 'material')): {('metal_welding_construction', 'material')},
                ('Base.ScrapMetal', ('role', 'metalworking', 'material')): {('metal_welding_construction', 'material')},
                ('Base.MetalPipe', ('role', 'metalworking', 'material')): {('welded_parts', 'material'), ('metal_welding_construction', 'material')},
                ('Base.Nails', ('role', 'construction', 'material')): {('carpentry_menu_construction', 'material')},
                ('Base.Nails', ('role', 'crafting', 'material')): {('woodworking', 'material'), ('furniture_crafting', 'material'), ('trap_crafting', 'material')},
                ('Base.Rope', ('role', 'binding_crafting', 'material')): {('log_binding', 'material')},
                ('Base.Rope', ('role', 'connecting_crafting', 'material')): {('carpentry_menu_construction', 'material')},
                ('Base.Plank', ('role_unspecified_context', 'crafting_material')): {('woodworking', 'material'), ('construction', 'material')},
            }
            role_aliases.update({
                ('Base.FishingLine', ('identity_label', '낚시 소모품')): {('fishing_gear_crafting', 'material')},
                ('Base.Hairspray', ('identity_label', '폭발물 재료')): {('explosive_assembly', 'material')},
                ('Base.WaterBottleEmpty', ('identity_label', '폭발물 재료')): {('explosive_assembly', 'material')},
                ('Base.SharpedStone', ('identity_label', '석기 제작 도구')): {('tool_crafting', 'material')},
            })
            for trap_item in ('Base.BakingTray_Muffin', 'Base.BakingTray_Muffin_Recipe'):
                role_aliases[trap_item, ('function', 'remove_portioned_muffins')] = {('food_portioning', 'ingredient')}
            for tool_item in ('Base.Hammer', 'Base.HammerStone', 'Base.BallPeenHammer'):
                role_aliases[tool_item, ('condition', 'carpentry_menu_construction' if tool_item != 'Base.BallPeenHammer' else 'construction', 'nailed_structure' if tool_item != 'Base.BallPeenHammer' else 'wooden_structure_with_nails')] = {('construction', 'tool')}
                role_aliases[tool_item, ('role', 'carpentry_menu_construction' if tool_item != 'Base.BallPeenHammer' else 'construction', 'tool')] = {('construction', 'tool')}
            for tool_item in ('Base.BlowTorch', 'Base.WeldingMask'):
                role_aliases[tool_item, ('role', 'metalworking', 'tool')] = {('metal_welding_construction', 'tool')}
            for line_item in ('Base.FishingLine', 'Base.Paperclip'):
                for operation in ('fishing_rod_crafting', 'fishing_rod_repair'):
                    role_aliases[line_item, ('role', operation, 'material')] = {('fishing_gear_crafting', 'material')}
            selected_roles = role_aliases.get((item, tuple(meaning)), set())
            if selected_roles:
                matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['context_ref']
                    and (facts[f['context_ref']]['payload']['activity'], f['payload']['role']) in selected_roles]
                if item in {'Base.FishingLine', 'Base.Paperclip'}:
                    matched = [f for f in matched if has_recipe(f, {'Fix Fishing Rod'} if meaning[1] == 'fishing_rod_repair' else {'Make Fishing Rod'})]
                if matched:
                    alias_note = 'Reconcile the broad predecessor wording with this exact source-reviewed participation and its full attached eligibility/consumption conditions. A supplied ingredient/material, kept tool, vessel or transformation target retains that role; this does not infer a generic action, interchangeable role or guaranteed native result.'
            if not matched and item == 'Base.MetalBar' and meaning == ['role', 'metal_barricading', 'material']:
                matched = [f for f in candidates if f['payload'] == {'function': 'build_metal_barricade'}]
                alias_note = 'Metal-bar barricading consumes three bars and one torch use through its actual door/window path. It is distinct from welding-menu construction and does not require the welding-menu mask or learned recipes.'
            if not matched and item == 'Base.BucketPlasterFull' and meaning == ['role_unspecified_context', 'material']:
                matched = [f for f in candidates if f['payload'] == {'function': 'plaster_supported_structure'}]
                alias_note = 'Replace the unspecified material label with the exact plasterable-structure operation, its carpentry and approach conditions and one selected bucket use. This does not imply arbitrary construction, repair, painting or structural strengthening.'
            predicate_aliases = {
                ('Base.TinnedBeans', ('condition', 'bean_preparation', 'bowl')): sources.BEAN_PREPARATION,
                ('Base.Log', ('condition', 'log_sawing', 'saw')): sources.SAWN_WOOD,
                ('Base.Coffee2', ('condition', 'beverage_preparation', 'compatible_prepared_drink')): sources.COOKING_ACTION,
                ('Base.Paintbrush', ('condition', 'surface_painting', 'paint_and_compatible_surface')): sources.PAINT_ACTIONS,
                ('Base.BakingTray_Muffin', ('condition', 'remove_muffins', 'after_baking')): sources.MUFFIN_PORTIONING,
                ('Base.BakingTray_Muffin_Recipe', ('condition', 'remove_muffins', 'after_baking')): sources.MUFFIN_PORTIONING,
                ('Base.PlasterPowder', ('condition', 'plaster_preparation', 'water')): sources.PLASTER_MIXING,
                ('Base.CakeBatter', ('condition', 'cake_preparation', 'baking_pan')): sources.CAKE_PAN_PREPARATION,
                ('Base.PieDough', ('condition', 'pie_preparation', 'baking_pan')): sources.FOOD_ASSEMBLY,
            }
            predicate = predicate_aliases.get((item, tuple(meaning)))
            if not matched and predicate:
                matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
            if not matched and meaning == ['role', 'gardening', 'tool'] and item in {
                    'Base.GardenFork', 'Base.GardenHoe', 'Base.Shovel', 'Base.Shovel2', 'farming.HandShovel'}:
                matched = [f for f in candidates if f['payload'].get('function') in {'dig_furrow', 'remove_farm_plant'}]
                alias_note = 'Narrow gardening to the actual furrow/plant-removal operation and its target, tool, access and interruption predicates; the tool does not provide arbitrary gardening effects.'
            if not matched and item in {'Base.Bag_JanitorToolbox', 'Base.Bag_SurvivorBag'} and meaning == ['condition', 'carrying', 'worn_or_held']:
                matched = [f for f in candidates if f['payload'] == {'function': 'carry_stored_items'}]
                alias_note = 'Carrying requires inventory transfer/admission, not necessarily wearing or holding the container. Only the separately declared Back form supports back equipment. Preserve those distinct conditions instead of the predecessor universal worn-or-held restriction.'
            if not matched and item == 'Base.BlowTorch' and meaning == ['identity_label', '소모성 도구']:
                matched = [f for f in candidates if f['payload'] == {'predicate': sources.METAL_BARRICADE}]
                alias_note = 'The welding action spends torch uses; KeepOnDeplete retains the depleted tool. Replace an unscoped consumable-tool label with this actual consumption condition, not a claim that the entire torch disappears.'
            if not matched and item == 'Base.ShotgunShellsBox' and meaning == ['function', 'unpack_box_contents']:
                matched = [f for f in candidates if f['payload'] == {'function': 'unpack_ammunition'}]
            if not matched and item.startswith('Base.MakeUp_Lips') and meaning == ['function', 'apply_lip_makeup']:
                matched = [f for f in candidates if f['payload'] == {'function': 'wear_on_body'}]
                alias_note = 'This exact item is the registered Clothing makeup result, not the MakeUpType cosmetic supply that opens the makeup-selection UI. Retain its actual worn-slot behavior instead of claiming it applies another cosmetic; visible color remains separately unresolved.'
        if matched:
            refs = {f['ref'] for f in matched}
            for fact in matched:
                refs.update(fact['qualifier_refs'])
                if fact['context_ref']:
                    refs.add(fact['context_ref'])
            # Qualifier claims retain their actual parent behavior too.
            refs.update(r for f in matched for r in f['applies_to_refs'])
            pending = list(refs)
            while pending:
                fact = facts[pending.pop()]
                dependencies = set(fact['qualifier_refs']) | ({fact['context_ref']} if fact['context_ref'] else set())
                pending.extend(dependencies - refs)
                refs.update(dependencies)
            source_refs = sorted({p for r in refs for p in facts[r]['provenance_refs']})
            core_was_present = all((f['item_id'], f['fact_id']) in previous for f in matched)
            was_present = all((facts[r]['item_id'], facts[r]['fact_id']) in previous for r in refs)
            disposition = 'already_represented' if was_present else 'corrected' if core_was_present else 'recovered'
            narrowing = alias_note
            if alias_note:
                disposition = 'corrected'
            if item in sources.PETROL_ITEMS | sources.EMPTY_PETROL_ITEMS | {'Base.Charcoal', 'Base.PropaneTank', 'Base.Bellows'} and meaning[0] in {'function', 'role_unspecified_context', 'consumption_property'}:
                disposition = 'corrected'
                narrowing = 'Replace the broad fuel/material/carrying gloss with the exact represented target and operation. Vehicle transfer, pump replacement, generator refill, hearth fuel and industrial ignition have different guards and consumption rules; industrial petrol ignition does not consume either input. Native results and delivery remain separate.'
            if item in sources.DRAINABLE_MATERIALS and meaning in (
                    ['role_unspecified_context', 'material'], ['consumption_property', 'consumable']):
                disposition = 'corrected'
                narrowing = 'Replace the unscoped material/consumable assertion with its actual recipe, fixing or construction participation. Exact role conditions retain consumption and result boundaries; this is not an unconditional assertion that the carried item is used up or has a generic material effect.'
            if item == 'Base.Vinegar' and meaning == ['role', 'food_preparation', 'ingredient']:
                disposition = 'corrected'
                narrowing = 'Narrow the broad food-ingredient wording to the reviewed vegetable-jarring material role, with the exact recipe inputs and conditions. This does not make the Drainable vinegar a directly edible food or an arbitrary evolved-recipe ingredient.'
            if item == 'Base.DuctTape' and meaning == ['role', 'device_assembly', 'material']:
                disposition = 'corrected'
                narrowing = 'The specific role is attaching timer, sensor or trigger modifications to the reviewed explosive devices, not arbitrary electronic device assembly. Exact modification recipes and callbacks remain attached.'
            if item == 'Base.FishingNet' and meaning == ['function', 'catch_bait_fish']:
                disposition = 'corrected'
                narrowing = 'The checking action can return BaitFish through hourly random rolls. More than fifteen elapsed hours first permits net breakage; neither a catch nor survival of the net is guaranteed.'
            if meaning == ['function', 'fold_umbrella'] and item.startswith('Base.ClosedUmbrella'):
                disposition = 'corrected'
                narrowing = 'This exact closed umbrella is the input to opening, not folding. Replace the generic folding capability with its supported closed-to-open recipe, preserving condition copying and hand-placement constraints. Folding belongs to the distinct open form; rain protection remains independently unresolved.'
            if meaning == ['function', 'adjust_vehicle_tire_pressure'] and item == 'Base.TirePump':
                disposition = 'corrected'
                narrowing = 'The pump participates in inflation only. The deflation menu needs no pump. The retained inflation target, equipment, action validity and partial server requests do not promise arbitrary chosen pressure or rollback on cancellation.'
            if construction_claim and meaning[1] == 'hinged_structure_construction':
                disposition = 'corrected'
                narrowing = 'The open-ended hinged-structure wording is bounded to the active wooden-door and metal gate/locker/counter factories that declare this exact hinge material. Their carpentry or learned metal-welding requirements and consumption conditions remain attached; arbitrary hinged structures are not inferred from their names.'
            if item in sources.BROKEN_GLASS_ITEMS and meaning == ['caution', 'clearing_broken_glass']:
                disposition = 'corrected'
                narrowing = 'The general clearing warning is narrowed to the actual floor-glass pickup hand scratch and nested embedded-glass branches, with missing hands-slot clothing and random checks. Gloves do not gate menu admission, and neither window-frame removal nor approach/foot contact is substituted for pickup.'
            if furniture_gloss:
                disposition = 'corrected'
                narrowing = 'The layout/area-marking gloss is narrowed to the exact Moveable sprite placement and conditional pickup actions with their full space, parts, contents, tool/skill, reach, permission and breakage conditions. These actions do not establish an automatic marked area, an indoor-only restriction, or the installed appliance/storage/resting function; those require the actual placed-object properties. No unrelated world operation is completed by this comparison.'
            if item in {'Base.Plantain', 'Base.Comfrey'} and meaning == ['identity_label', '식품']:
                disposition = 'corrected'
                narrowing = 'The exact raw plant is declared Normal, not Food, and the inventory eating predicate does not select it. Replace the unsupported food label with its source-confirmed poultice ingredient role; consumption of a similarly named Food form is not inferred.'
            if item == 'Base.MakeupFoundation' and meaning == ['cosmetic_role', 'base_layer']:
                disposition = 'corrected'
                narrowing = 'Replace the unsupported base-layer claim with selection of the exact registered Foundation designs and its mirror exemption. Apply replaces the worn cosmetic and does not implement a base layer under other makeup or consume the foundation supply.'
            if meaning == ['function', 'reuse_container']:
                disposition = 'corrected'
                narrowing = 'The reuse claim is narrowed to the exact declared water-filling replacement and its admitted source/transfer/capacity conditions. It does not establish arbitrary reuse, guaranteed full filling or preservation of the old inventory identity.'
            if item in {'Base.Dirtbag', 'Base.Gravelbag', 'Base.Sandbag'} and meaning in (['role_unspecified_context', 'material'], ['consumption_property', 'consumable'], ['material_form', 'bag_of_dirt']):
                disposition = 'corrected'
                narrowing = 'The unspecified material/consumable or dirt-bag wording is narrowed to the exact bag selected for ground pouring, which calls Use after adding its matching floor and retains restoration metadata. Other construction and extinguishing roles remain separately represented; no generic ingredient role or guaranteed empty-form replacement is inferred.'
            if item == 'Base.Thread' and meaning in (['role_unspecified_context', 'material'], ['role', 'fabric_crafting', 'material'], ['consumption_property', 'consumable']):
                disposition = 'corrected'
                narrowing = 'The unspecified material/fabric-making/consumable wording is narrowed to the actual garment patching action, which requires Thread in inventory and calls its Use on completion. This does not establish arbitrary fabric manufacture or guaranteed empty-form removal; other crafting and wound-stitching scopes remain independent.'
            if item == 'Base.LeatherStrips' and meaning == ['material_form', 'leather_patch']:
                disposition = 'corrected'
                narrowing = 'The leather-patch phrase is represented by this exact LeatherStrips input selected for the guarded patching action. Native patch type/protection and full restoration are not inferred from its material name.'
            if meaning == ['function', 'sew_fabric'] and item == 'Base.Needle':
                disposition = 'corrected'
                narrowing = 'The generic sewing claim is narrowed to actual garment patching/padding with a fabric, thread and the represented garment/part prerequisites. Arbitrary fabric construction is not inferred from the needle name.'
            if item in {'Base.Soap2', 'Base.CleaningLiquid2'} and meaning[0] in {'function', 'effect'}:
                disposition = 'corrected'
                narrowing = 'The cleanser claim is expressed as participation in actual water-based body/equipment washing. Soap is used for blood, not dirt alone, and insufficient soap changes calculated time rather than preventing washing. Partial body coverage, clothing wetness and makeup removal remain explicit; this does not claim wound treatment or that soap alone causes the cleaning.'
            if meaning == ['intended_use', 'navigation_planning']:
                disposition = 'corrected'
                narrowing = 'The human navigation-planning gloss is narrowed to the actual map viewer with pan/zoom/reset and its inventory/initialization conditions. The source supplies no automatic route planner, route safety or content-accuracy guarantee; these are not implied by viewing the map.'
            if meaning == ['context_label', 'medical_use']:
                disposition = 'corrected'
                narrowing = 'The broad medical-use category is represented by the exact admitted bandage application or wound-disinfection action and its conditions; other medical uses are not inferred.'
            if meaning == ['state_label', 'dirty_bandaging_material']:
                disposition = 'corrected'
                narrowing = 'The exact Dirty type-name branch applies a bandage with zero bandage life. This is the supported dirty-bandage meaning; the separate infected-item flag and wound infection are not inferred from the label.'
            if meaning == ['identity_label', '손상 낚싯대']:
                disposition = 'corrected'
                narrowing = 'The exact declaration names a rod without line, and the two source-reviewed repairs use it as that input form. Replace the ambiguous damaged-rod label with this line-repair meaning; weapon ConditionMax=3 is not a declaration of zero current condition.'
            if meaning == ['effect', 'fishing_lure', 'may_break']:
                disposition = 'corrected'
                narrowing = 'Replace physical breakage wording with the observed lure Use/hand clearing and line-break inventory removal paths. Artificial tackle is not immune to loss, but these paths do not establish a decrease in its durability condition.'
            if meaning == ['function', 'read_or_consult']:
                disposition = 'corrected'
                narrowing = 'The broad read-or-consult statement is narrowed to the supplied literature reading action and its accepted conditions; no independent consultation function is inferred.'
            if meaning[0] == 'effect' and meaning[1:] in (['skill_knowledge', 'gain'], ['recipe_knowledge', 'gain']):
                disposition = 'corrected'
                narrowing = 'This exact registered skill book has no declared taught recipes. ISReadABook updates a conditional skill XP multiplier and skips the non-skill ReadLiterature call. Replace the generic skill/recipe-knowledge wording with that multiplier effect; direct skill-level gain and recipe learning are not represented.'
            if meaning[0] == 'function' and meaning[1] in {'write_documents', 'revise_documents'}:
                disposition = 'corrected'
                narrowing = 'The broad predecessor document-writing/editing use is narrowed to writable-note pages and titles. The exact implement-tag predicate and journal setters support this scope; arbitrary documents and paper organization are not admitted.'
            elif item in sources.STRAP_SPEED and meaning[0] in {'effect', 'condition'} and meaning[1] == 'reload_speed':
                disposition = 'corrected'
                narrowing = 'The consumer matches the primary-hand ammo type against Base.ShotgunShells, not a firearm model class. Replace the broad faster-reload wording with the represented conditional 1.15 multiplication of ReloadSpeed. Exact action duration and unrelated weapon handling are not inferred; the worn strap form and other speed factors remain explicit.'
            elif item in base.get('vehicle_panel_sources', {}) and meaning[0] == 'function' and meaning[1].startswith(('remove_vehicle_', 'install_vehicle_', 'refit_vehicle_')):
                disposition = 'corrected'
                narrowing = 'The panel/glass exchange is represented for this exact part form with runtime FullType compatibility, actual tool/access predicates and server success/failure conditions. The template token and VehicleType suffix are retained as leads, not silently expanded into compatibility. The predecessor unconditional wording is narrowed to this supported conditional operation.'
            elif meaning[0] == 'role' and meaning[1:] in (['fire_starting', 'tinder'], ['burning', 'fuel']):
                disposition = 'corrected'
                narrowing = 'The broad predecessor tinder/fuel use is narrowed to the exact registered campfire route and its selection, inventory, consumption and server-state conditions. Other fire or heating systems are not represented by this match.'
            elif meaning == ['condition', 'animal_trapping', 'player_proximity']:
                disposition = 'corrected'
                narrowing = 'The predecessor proximity wording is replaced with the actual checkForAnimal guard: a loaded trap square skips catching. No fixed player radius or equivalence between distance and square loading is inferred.'
            elif meaning == ['constraint', 'rod_fishing', 'artificial_excludes_pike_baitfish']:
                disposition = 'corrected'
                narrowing = 'The exclusion is bounded to the supplied fish/lure table and actual lure-matching consumer. It does not exclude future runtime registry additions or guarantee a catch of other species.'
            elif meaning == ['role', 'food_preparation', 'ingredient'] and any(f['payload'] == {'function': 'prepare_opened_food_ingredient'} for f in matched):
                disposition = 'corrected'
                narrowing = 'The broad ingredient claim is narrowed to the exact food contents after the supported package-opening transformation. The unopened package is not an ingredient; opening and the resulting food eligibility are both represented.'
            claim.update(candidate_successor_fact_refs=sorted(refs), verified_source_refs=source_refs,
                         migration_disposition=disposition,
                         reason=narrowing or ('The core proposition survives with corrected source-admitted qualifiers; dependent references use their new semantic identities.' if disposition == 'corrected' else
                                 'The reviewed proposition matches the source-admitted payload and its context/qualifiers; the predecessor text is not the admission evidence.'),
                         remaining_uncertainty=None, remaining_work=None,
                         source_binding='source_bound', source_strength='consumer_confirmed', review_state='reviewed')
            locales = {}
            for locale in ('ko', 'en'):
                rendered = items[item]['locales'][locale]
                expanded = sorted({e for r in refs for e in rendered['fact_expressions'].get(r, [])})
                missing = refs - set(rendered['expanded_represented_fact_refs'])
                compact = refs & set(rendered['s2']['represented_fact_refs'])
                detail_reasons = [d['reason'] for d in rendered['s2'].get('detail_fact_omissions', [])
                                  if d['fact_ref'] in refs - compact]
                locales[locale] = {'expanded_outcome': 'expression_failure' if missing or not expanded else 'represented',
                                   'expanded_refs': expanded, 'compact_fact_refs': sorted(compact),
                                   'compact_outcome': 'represented' if compact == refs else 'detail_omission',
                                   'compact_omitted_fact_refs': sorted(refs - compact),
                                   'compact_omission_reason': None if compact == refs else
                                   ' '.join(detail_reasons) if detail_reasons else
                                   'The omitted references remain accessible in expanded as ordinary execution/detail qualifiers or facts outside first-contact selection; they do not remove the expressed functional context or its meaning-changing scope.'}
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                                 'migration_disposition': claim['migration_disposition'], 'successor_fact_refs': sorted(refs),
                                 'locales': locales, 'residual': None,
                                 'conservation_status': 'conserved' if all(v['expanded_outcome'] == 'represented' for v in locales.values()) else 'expression_failure'})
            continue
        if meaning in (['function', 'receive_radio_signal'], ['function', 'transmit_radio_signal'], ['function', 'receive_tv_signal'],
                       ['function', 'play_recorded_media'], ['function', 'play_vhs'], ['function', 'play_cd_recording'],
                       ['condition', 'media_playback', 'compatible_player'], ['condition', 'recorded_media_playback', 'compatible_device']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            radio = fields.get('Type') == 'Radio' and not {'Type', 'TwoWay', 'IsTelevision', 'NoTransmit', 'AcceptMediaType'} & conflicts.keys()
            media = any(f['payload'] == {'function': 'insert_recorded_media'} for f in candidates)
            signal = radio and (
                (meaning == ['function', 'receive_radio_signal'] and fields.get('IsTelevision', '').lower() == 'false' and fields.get('NoTransmit', '').lower() != 'true')
                or (meaning == ['function', 'transmit_radio_signal'] and fields.get('TwoWay', '').lower() == 'true')
                or (meaning == ['function', 'receive_tv_signal'] and fields.get('IsTelevision', '').lower() == 'true'))
            playback = (media and meaning in (['function', 'play_recorded_media'], ['condition', 'media_playback', 'compatible_player'],
                                               ['condition', 'recorded_media_playback', 'compatible_device'])) or (
                radio and ((meaning == ['function', 'play_vhs'] and fields.get('IsTelevision', '').lower() == 'true' and fields.get('AcceptMediaType') == '1')
                           or (meaning == ['function', 'play_cd_recording'] and fields.get('AcceptMediaType') == '0')))
            if signal or playback:
                partial = [f['ref'] for f in candidates if f['payload'].get('function') in {
                    'open_device_controls', 'tune_radio', 'select_tv_channel', 'adjust_device_volume', 'toggle_radio_microphone',
                    'read_recorded_media_label', 'insert_recorded_media', 'control_device_media', 'edit_radio_presets'}]
                paths = [records[0]['path'], sources.RADIO_WINDOW, sources.RADIO_ACTION,
                         *( (sources.RADIO_SIGNAL, sources.RADIO_MIC, sources.RADIO_INTERACTIONS) if signal else
                            (sources.RADIO_MEDIA, sources.MEDIA_LOADER, sources.MEDIA_DATA, sources.CONTEXT_MEDIA, sources.RADIO_INTERACTIONS) )]
                uncertainty = {'meaning': meaning, 'examined': {
                    'fields': {k: fields.get(k) for k in ('Type', 'TwoWay', 'IsTelevision', 'NoTransmit', 'AcceptMediaType', 'MediaCategory')},
                    'control_fact_refs': partial,
                    'delivered_code_consumer': sources.RADIO_CODE_EFFECTS,
                    'boundary': ('Signal display reads native isReceivingSignal and interaction code receives delivered OnDeviceText. Channel/microphone setters do not implement signal transport.' if signal else
                                 'Media insertion checks recorded state and matching media type. TogglePlayMedia requires on/hasMedia and calls native StartPlayMedia/StopPlayMedia; the category loader registers records without assigning one to this item.')},
                    'required_input': ('Native device signal propagation, microphone pickup and receiver delivery for this declared subtype' if signal else
                                       'Native RecordedMedia assignment/type mapping and DeviceData playback/output for this exact media or accepting device'),
                    'reason': ('The exact declared device branch and local control consumers have been examined. A control setting or received-state display does not establish the actual claimed signal path; missing propagation/delivery implementation remains.' if signal else
                               'Conditional label/insertion or device controls are represented. The exact recording assignment and native executor still determine playable content and output; compatibility for insertion alone does not prove the complete playback claim.')}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                             verified_source_refs=[base['reader'].bindings[p] for p in paths], reason=uncertainty['reason'],
                             remaining_uncertainty=uncertainty, remaining_work=None, source_binding='source_bound',
                             source_strength='declared_device_and_exact_media_signal_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning in (['function', 'check_time'], ['function', 'listen_through_radio_headphones']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            clock = meaning[1] == 'check_time' and fields.get('Type') in {'AlarmClock', 'AlarmClockClothing'} and 'Type' not in conflicts
            headphone = meaning[1] == 'listen_through_radio_headphones' and item in {'Base.Headphones', 'Base.Earbuds'} and len(records) == 1
            if clock or headphone:
                if clock:
                    paths = [records[0]['path'], semantic.MENU, sources.ALARM_DIALOG,
                             'lua/client/ISUI/ISButtonPrompt.lua', 'lua/client/XpSystem/ISUI/ISCharacterScreen.lua']
                    examined = {'declaration': fields,
                        'menu': 'AlarmClock/AlarmClockClothing collection only reaches set/stop-alarm options when isDigital is true.',
                        'display': 'ButtonPrompt reads the native UIManager clock visibility and dimensions. CharacterScreen gates survival-time display on its isDateVisible result. Neither Lua consumer identifies which held/worn clock enables the time display.'}
                    dependency = 'UIManager Clock visibility/time-display selection and exact AlarmClock or AlarmClockClothing instance binding'
                    reason = 'The local alarm operations and native-clock UI consumers are examined separately. Setting an alarm does not prove time-display eligibility for this exact item; the item-to-clock-display selection is not supplied by those Lua consumers.'
                    partial = [f['ref'] for f in candidates if f['payload'].get('function') in {'set_alarm', 'stop_alarm'}]
                else:
                    paths = [records[0]['path'], sources.RADIO_VOLUME, sources.RADIO_PANEL, sources.RADIO_WINDOW, sources.RADIO_ACTION]
                    examined = {'declaration': fields, 'connection': 'RWMVolume verifies exact headphone FullTypes; ISRadioAction passes a selected item to DeviceData.addHeadphones for an empty slot.',
                                'playback': 'The Lua volume controls read device power and set volume; they do not define headphone audio routing or audible output.'}
                    dependency = 'DeviceData headphone binding and native radio audio routing/playback for the connected device'
                    reason = 'The connection action is represented. The actual selected device audio path, power/reception and headphone playback remain native state and cannot be inferred from the connection request.'
                    partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'connect_radio_headphones'}]
                for path in paths:
                    base['reader'].read(path)
                uncertainty = {'meaning': meaning, 'examined': examined, 'required_input': dependency, 'reason': reason}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                             verified_source_refs=[base['reader'].bindings[p] for p in paths], reason=reason,
                             remaining_uncertainty=uncertainty, remaining_work=None, source_binding='source_bound',
                             source_strength='exact_display_or_audio_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['function', 'shove']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Weapon' and 'Type' not in conflicts:
                uncertainty = {'meaning': meaning,
                    'examined': {'declaration': fields, 'consumer': sources.FIREARM,
                                'branch': 'attackHook sends isDoShove through the non-shooting DoAttack path, including its vehicle exception.'},
                    'required_input': 'DoAttack/isDoShove interpretation identifying the selected weapon contribution to a shove',
                    'reason': 'The Lua branch dispatches a character-controlled shove but does not establish whether or how this exact weapon contributes to it. Ordinary weapon attack facts remain separate; neither intrinsic shove use nor absence of such use is inferred.'}
                evidence = [base['reader'].bindings[records[0]['path']], base['reader'].bindings[sources.FIREARM]]
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='character_weapon_dispatch_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning in (['function', 'trigger_linked_device'], ['condition', 'remote_trigger', 'compatible_linked_device']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('RemoteController', '').lower() == 'true' and 'RemoteController' not in conflicts:
                partial = [f['ref'] for f in candidates if f['payload'].get('function') in {'link_remote_device', 'send_remote_trigger'}]
                if partial:
                    evidence = [base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, sources.OBJECT_COMMANDS)]
                    uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                        'linking': 'OnLinkRemoteController assigns an absent controller ID and copies it to the selected compatible item.',
                        'triggering': 'The active OnTriggerRemoteController sends object/triggerRemote with ID/range; Commands.object.triggerRemote passes both to IsoTrap.triggerRemote.',
                        'partial_fact_refs': partial},
                        'required_input': 'IsoTrap.triggerRemote matching, range and actual trap-effect interpretation',
                        'reason': 'ID assignment and request transmission are represented. The actual receiver delegates finding and triggering a matching placed trap to IsoTrap; neither an assigned ID nor its request proves that the linked device actually operates.'}
                    claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                                 verified_source_refs=evidence, reason=uncertainty['reason'], remaining_uncertainty=uncertainty,
                                 remaining_work=None, source_binding='source_bound', source_strength='exact_native_trap_handoff', review_state='reviewed')
                    conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                         'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                         'conservation_status': 'bounded_unresolved'})
                    continue
        if meaning[0] == 'effect' and meaning[1] in {'vehicle_traction', 'vehicle_engine_noise', 'vehicle_braking'}:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            field, template = {'vehicle_traction': ('WheelFriction', 'tire'),
                               'vehicle_engine_noise': ('EngineLoudness', 'muffler'),
                               'vehicle_braking': ('brakeForce', 'brake')}[meaning[1]]
            if fields.get('MechanicsItem', '').lower() == 'true' and field in fields and field not in conflicts:
                paths = [records[0]['path'], 'scripts/vehicles/template_' + template + '.txt',
                         'lua/client/Vehicles/ISUI/ISVehicleMechanics.lua',
                         'lua/client/Vehicles/ISUI/ISVehiclePartMenu.lua',
                         'lua/client/Vehicles/TimedActions/ISInstallVehiclePart.lua',
                         'lua/server/Vehicles/VehicleCommands.lua', 'lua/server/Vehicles/Vehicles.lua']
                for path in paths:
                    base['reader'].read(path)
                evidence = [base['reader'].bindings[p] for p in paths]
                uncertainty = {'meaning': meaning,
                    'examined': {'declaration': fields, 'template': paths[1],
                                'selection': 'ISVehicleMechanics matches runtime part:getItemType to exact FullType inventory entries with positive condition.',
                                'installation': 'The normal action transfers the item and sends vehicle/installPart. Its actual server handler conditionally sets the part inventory item; failure can damage or return it.',
                                'effect_boundary': 'The mechanical display reads part values. The supplied update callback handles condition loss or tire air/removal; it does not define how this declared stat changes traction or engine sound.'},
                    'required_input': 'VehicleScript itemType/VehicleType binding and VehiclePart/BaseVehicle interpretation of ' + field,
                    'reason': 'The exact mechanical field and actual client-to-server installation path have been examined. Neither the template token nor the mechanical UI number establishes the claimed vehicle effect; runtime type expansion and engine stat application remain unverified.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='vehicle_type_and_engine_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning[0] == 'effect' and meaning[1] in {'recipe_knowledge', 'makeshift_radio_recipe_knowledge'}:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if (fields.get('Type') == 'Literature' and fields.get('TeachedRecipes') and not fields.get('SkillTrained')
                    and fields.get('CanBeWrite', '').lower() != 'true' and not {'Type', 'TeachedRecipes', 'SkillTrained', 'CanBeWrite'} & conflicts.keys()
                    and (len(meaning) == 3 or (meaning[3] in LEARNING_TOPICS
                         and set(LEARNING_TOPICS[meaning[3]]) <= set(fields['TeachedRecipes'].split(';'))))):
                partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'read_literature'}]
                evidence = [base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, semantic.READ)]
                uncertainty = {'meaning': meaning, 'examined': {'teached_recipes': fields['TeachedRecipes'],
                    'claimed_topic_entries': list(LEARNING_TOPICS[meaning[3]]) if len(meaning) > 3 else fields['TeachedRecipes'].split(';'),
                    'reading_path': 'ISReadABook.perform adds the FullType to alreadyReadBook for nonempty TeachedRecipes, then calls character:ReadLiterature for this nonskill book.',
                    'excluded_code': 'The explicit getKnownRecipes():add loop below is commented out.', 'partial_fact_refs': partial},
                    'required_input': 'IsoGameCharacter.ReadLiterature interpretation of TeachedRecipes and known-recipe mutation',
                    'reason': 'Reading the book is represented, and its exact recipe list is retained. The active Lua records a read-book identity but delegates learning to ReadLiterature; the commented known-recipe loop cannot establish recipe learning as an active Lua effect.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                             verified_source_refs=evidence, reason=uncertainty['reason'], remaining_uncertainty=uncertainty,
                             remaining_work=None, source_binding='source_bound', source_strength='exact_native_reading_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.Coffee2' and meaning[0] in {'recipe_menu', 'recipe_relation'} and meaning[1] == 'coffee_preparation':
            records = base['declarations'][item]
            reason = 'Remove this exact coffee menu/recipe relation under the Layer 4 interaction responsibility. Coffee2 names the five HotDrink variants whose bases are water-filled mugs or teacup. The independently represented food-preparation ingredient role retains actual recipe acceptance and transfer/cooking/poisoning conditions; destination presence is not claimed.'
            claim.update(migration_disposition='responsibility_removed', reason=reason,
                verified_source_refs=[base['reader'].bindings[p] for p in (records[0]['path'], 'scripts/evolvedrecipes.txt', semantic.MENU, semantic.COOK, 'docs/ARCHITECTURE.md')],
                remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound', source_strength='responsibility_boundary', review_state='reviewed',
                owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': 'Layer 4 interaction information', 'destination_presence': 'not_claimed'})
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'responsibility_removed',
                'successor_fact_refs': [], 'locales': {}, 'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
            continue
        food_routes = [r for r in base.get('cooking_base_relations', {}).get(item, []) if r['field'] == 'ResultItem']
        food_route_claim = (meaning[0] == 'acquisition_process' and meaning[1] in {
            'boil_in_cup', 'boil_pasta', 'boil_rice', 'combine_ingredients', 'mix_ingredients',
            'put_food_or_ingredients_in_bowl_or_pot', 'pour_beer', 'pour_wine', 'pour_drink', 'cook_ingredients'}
            or meaning[0] in {'acquisition_container', 'preparation_form'}
            or meaning[0] == 'acquisition_material' and meaning[1] in {'water', 'ingredients'})
        if food_routes and food_route_claim:
            retain_boundary(claim, {semantic.MENU, semantic.COOK, *(r['path'] for r in food_routes)},
                {'exact_evolved_result_relations': food_routes, 'consumer': sources.COOKING_BASE},
                'Native evolved-recipe getItemsCanBeUse/addItem result identity, quantities and heating/state execution',
                'The exact base-to-result relation is source-bound and the ingredient-addition consumer is interpreted. Water-mug, tumbler, cup, wine glass and prepared-food bases remain distinct. A Cookable flag or Cooking category does not itself boil, bake or deliver the final food; the claimed result/form depends on native creation and state.')
            continue
        if meaning[0] == 'acquisition_process' and meaning[1] in {'cook_dough_or_ingredients', 'cook_ingredients'} and reviewed_results[item]:
            selected = list(reviewed_results[item].values())
            retain_boundary(claim, {semantic.CRAFT, semantic.GROUPS, *(p for r in selected for p in r['source_paths'])},
                {'reviewed_recipe_observation_refs': [r['observation_ref'] for r in selected]},
                'Native recipe result identity and any separate Food heating/cooking transition',
                'Actual preparation recipes for this exact result have been interpreted. For example scooping ice cream and coating/slicing ingredients do not execute heating merely because the predecessor says cooked. Their raw result and callback are retained without asserting a completed cooking outcome.')
            continue
        if meaning[0] in {'acquisition_place', 'acquisition_method'}:
            traced = {ref: t for token in (item, item.split('.', 1)[1]) for ref, t in loot_traces[token]}
            if not traced:
                paths = {r['path'] for r in base['acquisition']['source_bindings']
                    if r['path'].endswith(('Distributions.lua', 'ItemPicker.lua')) or '/Foraging/' in r['path']}
                paths.update(r['path'] for r in base['declarations'].get(item, []))
                for path in paths:
                    if path not in base['reader'].bindings:
                        base['reader'].read(path)
                retain_boundary(claim, paths, {'exact_fulltype': item, 'queried_tokens': [item, item.split('.', 1)[1]],
                    'loot_vehicle_connections': [], 'exact_declarations': base['declarations'].get(item, [])},
                    'An exact producer/alias and room/container/zone-to-place binding for the stated acquisition route',
                    'The bound loot/vehicle producer set has no connection for either exact or short token. Foraging registration and native selection are separate from similarly named wristwatches, jewelry or camping objects. No source supplied here corroborates this precise predecessor place/method; runtime impossibility is not asserted.')
                continue
        # Finite named residuals after positive fact/role reconciliation.
        records = base['declarations'].get(item, [])
        fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
        if item in {'Base.Bag_PistolCase', 'Base.Lemongrass', 'Base.NoiseMaker', 'Base.ShotgunCase1'} and len(records) != 1:
            paths = {r['path'] for r in records} or {r['path'] for r in base['semantic']['source_bindings'] if r['path'].startswith('scripts/')}
            retain_boundary(claim, paths, {'exact_fulltype': item, 'declarations': records},
                'An exact source declaration/alias binding' if not records else 'Native script loading and duplicate declaration precedence',
                'The complete bound item declarations have no exact definition for this predecessor identity.' if not records else
                'This exact FullType is declared twice. The declarations are retained independently; the historical model does not select a runtime winner. Similar or identical visible properties do not silently replace the required identity binding.')
            continue
        learning = {'generator_connection': 'Generator', 'generator_repair': 'Generator',
            'identify_poisonous_berries': 'Herbalist', 'identify_poisonous_mushrooms': 'Herbalist',
            'standard_vehicle_mechanics': 'Basic Mechanics', 'commercial_vehicle_mechanics': 'Intermediate Mechanics',
            'performance_vehicle_mechanics': 'Advanced Mechanics'}
        if meaning[0] == 'learning' and meaning[1] in learning and learning[meaning[1]] in fields.get('TeachedRecipes', '').split(';'):
            retain_boundary(claim, {records[0]['path'], semantic.READ, semantic.MENU, sources.WORLD_MENU, sources.VEHICLE_MENU},
                {'TeachedRecipes': fields['TeachedRecipes'], 'read_consumer': 'ISReadABook records alreadyReadBook, then calls native ReadLiterature; the explicit known-recipes loop is commented out.',
                 'selected_topic': learning[meaning[1]]},
                'Native ReadLiterature knowledge mutation and the exact learned-topic consumer',
                'The exact declared topic is bound to the actual reading branch. Generator menu gates and Herbalist poison labeling read known-recipe state; those checks do not implement the book granting it or guarantee every claimed repair/identification outcome.')
            continue
        food_thermal = fields.get('Type') == 'Food' and (
            meaning == ['function', 'bake_muffins'] or meaning == ['function', 'cook_rice_or_pasta']
            or meaning[0] == 'state_label' and meaning[1] in {'prepared_food', 'batter_filled_muffin_tray'})
        if food_thermal:
            retain_boundary(claim, {records[0]['path'], semantic.MENU, semantic.COOK, semantic.CRAFT, semantic.GROUPS},
                {'declaration': fields, 'evolved_relations': base.get('cooking_base_relations', {}).get(item, [])},
                'Native Food initialization/heating/cooking and RecipeManager result state',
                'The exact food declaration, ingredient-addition route and any independently represented portioning action are interpreted. IsCookable, times and a prepared-form name do not implement the claimed current cooked/batter state or guarantee successful baking. Portioning cooked food is separate from cooking it.')
            continue
        if (meaning[0] == 'output_identity' and item in base.get('package_opening_results', {})
                and (meaning[1] in {'ammunition', 'jarred_contents', 'vegetables'} or meaning == ['output_identity', 'food', 'tuna'])):
            routes = base['package_opening_results'][item]
            retain_boundary(claim, {semantic.CRAFT, semantic.GROUPS, *(r['path'] for r in routes)}, routes,
                'Native RecipeManager result identity/count and callback delivery',
                'The exact package-opening Result clauses identify the declared contents and their actual opening conditions. Native result creation remains separate; in particular the predecessor .556 label is not the source 5.56mm designation.')
            continue
        if meaning[0] == 'output_identity' and item in {'Base.CandyPackage', 'Base.Speaker', 'Base.HomeAlarm', 'Base.FishingNet'}:
            predicates = {'Base.CandyPackage': sources.CANDY_OPENING, 'Base.Speaker': sources.ELECTRONIC_SALVAGE,
                'Base.HomeAlarm': sources.ELECTRONIC_SALVAGE, 'Base.FishingNet': sources.NET_CHECKING}
            selected = [f for f in candidates if f['payload'] == {'predicate': predicates[item]}]
            if selected:
                paths = {observations[o]['source_path'] for f in selected
                    for p in semantic_facts[f['fact_id']]['provenance_refs'] for o in semantic_payload['provenance'][p]['observation_refs']}
                retain_boundary(claim, paths, {'actual_consumer': predicates[item]},
                    'Native result factory/count and conditional random inventory delivery',
                    'The exact opening, dismantling or net-checking source is interpreted. Candy declares five lollipops and its callback requests six mint candies; net checking is probabilistic. The source operation does not guarantee the claimed returned item delivery.')
                continue
        if item in {'Base.BucketConcreteFull', 'Base.ConcretePowder', 'Base.Screws', 'Base.Cornmeal', 'Base.IcePick', 'Base.Rake', 'Base.LeafRake'} and (
                meaning[0] in {'role', 'role_unspecified_context', 'context', 'consumption_property'}
                or item == 'Base.BucketConcreteFull' and meaning == ['acquisition_process', 'mix_ingredients']):
            paths = {records[0]['path'], semantic.MENU, semantic.CRAFT, semantic.GROUPS, semantic.BUILD, semantic.STAGE, semantic.MOVE, semantic.PROPS}
            retain_boundary(claim, paths, {'declaration': fields,
                'source_distinctions': 'ConcretePowder/BucketConcreteFull have no exact input/Result in the supplied recipes or active construction calls. Screws are breakage/salvage returns and box contents, not a demonstrated assembly/repair input. Cornmeal is the legacy Drainable, distinct from Food Cornflour. IcePick has weapon/spear-attachment use; Rake/LeafRake lack the gardening tags selected by the furrow menu.'},
                'An exact active input consumer for the separately claimed role or preparation',
                'The named role does not follow from display category, similarly named forms or output-only participation. Available exact consumers and independent roles were interpreted; the claim remains uncorroborated without asserting universal absence.')
            continue
        state_meaning = (meaning[0] in {'state', 'state_label'} and (
            meaning[1:] in (['container_contents', 'empty'], ['empty_container'], ['empty_reusable_container'], ['water_filled_container'])))
        if item == 'Base.BoxOfJars' and meaning == ['identity_label', '재료']:
            retain_boundary(claim, {records[0]['path'], semantic.MENU},
                {'declaration': records[0], 'conflicts': conflicts},
                'Native duplicate DisplayCategory assignment and category presentation',
                'The exact declaration assigns both Material and Cooking. Neither a declaration winner nor the predecessor material category is inferred. The separately represented opening operation remains intact; display-category ownership is not transferred into Layer 3.')
            continue
        empty_name = meaning[0] == 'identity_label' and meaning[1].startswith('빈 ')
        if records and len(records) == 1 and (state_meaning or empty_name):
            retain_boundary(claim, {records[0]['path'], semantic.MENU, sources.TAKE_WATER, sources.TRANSFER_WATER, sources.DUMP_CONTENTS},
                {'declaration': fields, 'represented_water_relation': base.get('water_container_sources', {}).get(item),
                 'emptying_relation': base.get('container_emptying_relations', {}).get(item)},
                'Native item factory, carried container contents and water/replacement initial state',
                'The exact empty or water form and its available filling/emptying paths were examined. A name or replacement target does not prove current contents, full quantity or general-purpose storage. Its separately represented water operation remains intact.')
            continue
        if item == 'Base.KeyRing' and meaning == ['storage_acceptance', 'keys'] and fields.get('OnlyAcceptCategory'):
            retain_boundary(claim, {records[0]['path'], semantic.TRANSFER, semantic.MENU},
                {'declaration': fields}, 'Native ItemContainer isItemAllowed and OnlyAcceptCategory interpretation',
                'The declaration supplies the Key category restriction and the transfer consumer delegates admission. The exact runtime category test remains separate from the represented storage/carrying operation.')
            continue
        if item.startswith('Base.Boilersuit') and meaning == ['visual_coverage', 'upper_and_lower_body']:
            retain_boundary(claim, {records[0]['path'], semantic.WEAR, sources.BODY_LOCATIONS}, {'declaration': fields},
                'Exact ClothingItem mesh/texture and native worn-body visual coverage',
                'The declared clothing and body slot are bound and wearing is represented. Slot identity or a garment name is not proof of its rendered upper/lower-body coverage.')
            continue
        if item in {'Base.Garter', 'Base.LongCoat_Bathrobe'} and meaning[0] == 'wear':
            retain_boundary(claim, {records[0]['path'], semantic.WEAR, sources.BODY_LOCATIONS}, {'declaration': fields},
                'A source-supported mapping from the exact body slot to the claimed underwear/outerwear layer',
                'The actual worn slot and its exclusivity are represented. The predecessor garment-layer term does not follow from that slot without the exact classification/visual binding.')
            continue
        if (item == 'Base.223Clip' and meaning == ['function', 'insert_matching_magazine']):
            retain_boundary(claim, {records[0]['path'], semantic.MENU, sources.FIREARM, sources.INSERT_MAGAZINE},
                {'declaration': fields, 'receiver': 'The VarmintRifle MagazineType=Base.223Clip line is commented out; active firearm declarations do not supply this exact magazine receiver.'},
                'An active compatible firearm MagazineType/native magazine binding for Base.223Clip',
                'Loading and unloading ammunition in this magazine are represented. A filled magazine does not by itself establish insertion into an active firearm, and the commented receiver is not an executable join.')
            continue
        if item in {'Base.FireWoodKit', 'Base.CompostBag', 'Base.Fertilizer', 'Base.Corkscrew'} and meaning in (
                ['context_label', 'camping'], ['context_label', 'gardening'], ['context_label', 'table_setting'], ['function', 'use_tableware']):
            reason = 'Remove this standalone activity/category or generic table-setting gloss under Layer 2 classification and the adopted general inventory-management exclusion. Exact preparation, fertilizing and recipe-tool participation remain separately accounted; no destination presence is claimed.'
            claim.update(migration_disposition='responsibility_removed', reason=reason,
                verified_source_refs=[base['reader'].bindings[records[0]['path']], base['reader'].bindings['docs/ARCHITECTURE.md']],
                remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound', source_strength='responsibility_boundary', review_state='reviewed',
                owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': 'Layer 2 category responsibility and P4 general inventory management', 'destination_presence': 'not_claimed'})
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'responsibility_removed',
                'successor_fact_refs': [], 'locales': {}, 'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
            continue
        if item in {'Base.Pot', 'Base.TinnedSoup', 'Base.CannedMushroomSoup'} and (
                meaning[0] == 'role' and meaning[1] == 'soup_preparation'
                or meaning[:2] == ['condition', 'soup_preparation']):
            retain_boundary(claim, {records[0]['path'], 'scripts/recipes.txt', 'scripts/evolvedrecipes.txt', semantic.CRAFT, semantic.GROUPS, semantic.COOK},
                {'legacy_source': 'All four Make Pot of Soup variants for opened/closed TinnedSoup and CannedMushroomSoup with Pot are inside the block comment at recipes.txt 195–243.',
                 'active_source': 'Opening cans is separate. Active Soup uses WaterPot as its evolved base and PotOfSoupRecipe as result.'},
                'An active exact canned-soup/Pot consumer for the claimed soup preparation',
                'The predecessor combination is present only in commented recipe text. It is not an active recipe or evidence that the closed can prepares soup. Opening and water-storage facts remain independently represented.')
            continue
        if item == 'Base.IronIngot' and meaning == ['role', 'metal_melting', 'material']:
            retain_boundary(claim, {records[0]['path'], sources.BLACKSMITH_MENU, semantic.CRAFT, semantic.GROUPS},
                {'menu': 'getMetal counts IronIngot drainable units for anvil construction, whose menu is disabled. Independent active smithing recipes consume ingot amounts; furnace lighting/fuel controls do not implement melting this carried ingot.'},
                'An exact active IronIngot melting consumer or native furnace input/execution binding',
                'The actual ingot forging and construction input routes were interpreted. Those roles cannot be renamed melting merely from a metal category or furnace presence.')
            continue
        if item == 'Base.Pipe' and meaning == ['negative_scope', 'crafting_use', 'Build 41']:
            retain_boundary(claim, {records[0]['path'], semantic.CRAFT, semantic.GROUPS, semantic.MOVE, semantic.PROPS},
                {'declaration': fields, 'identity': 'Normal Plastic Pipe, distinct from Weapon MetalPipe'},
                'Version-wide exact crafting/extension coverage sufficient for the stated negative',
                'The bound exact Plastic Pipe and supplied recipe/menu paths do not establish a universal no-crafting claim for all Build 41. The separate MetalPipe cannot be used as its alias.')
            continue
        if meaning[0] == 'identity_label' and item in {
                'Base.BrokenFishingNet', 'Base.LightBulbGreen', 'Base.CannedMushroomSoupOpen', 'Base.TinnedSoupOpen',
                'Base.Chainsaw', 'Base.UnusableWood', 'Base.UnusableMetal', 'Base.ShotgunSawnoff',
                'Base.DoubleBarrelShotgunSawnoff', 'Base.PickAxeHandleSpiked'} and len(records) == 1:
            retain_boundary(claim, {records[0]['path'], semantic.MENU, semantic.CRAFT, semantic.GROUPS},
                {'declaration': fields, 'claimed_name': meaning[1]},
                'Exact native item state/visual binding for the modifier in the predecessor name',
                'The declared form and its separately represented uses are retained. Broken/opened/sawn/spiked, green, powered and unusable wording is not expanded into guaranteed physical state, rendered color, engine operation or universal lack of utility merely from the display name.')
            continue
        legacy_food_routes = {'Base.BakingTrayBread', 'Base.Pancakes', 'Base.Toast', 'Base.Waffles',
            'Base.EggBoiled', 'Base.EggPoached', 'Base.GrilledCheese', 'Base.Guacamole', 'Base.Smore',
            'Base.DoughRolled', 'Base.FishRoe', 'Base.RamenBowl', 'Base.PotOfSoup',
            'Base.ColdCuppa', 'Base.ColdDrinkRed', 'Base.ColdDrinkSpiffo', 'Base.ColdDrinkWhite', 'Base.Mugfull', 'Base.TrapMouse'}
        if item in legacy_food_routes and meaning[0] == 'acquisition_process' and len(records) == 1:
            retain_boundary(claim, {records[0]['path'], 'scripts/recipes.txt', 'scripts/evolvedrecipes.txt', semantic.MENU, semantic.CRAFT, semantic.COOK, semantic.GROUPS},
                {'declaration': fields, 'reviewed_result_recipes': [r['observation_ref'] for r in reviewed_results[item].values()],
                 'evolved_relations': base.get('cooking_base_relations', {}).get(item, []),
                 'legacy_notes': 'Make Pot of Soup and EggBoiled replacement entries are commented out. PancakesCraft replaces to PancakesRecipe, not Base.Pancakes. Toast/Waffles evolved entries begin with existing food, not a producer from dough. No bound recipe produces the exact TrapMouse.'},
                'An active exact producer/callback or native food/replacement transition establishing the stated process',
                'The complete supplied recipe result set, evolved base/result relations and exact declared form were compared. Existing-form ingredient addition and similarly named results cannot establish this predecessor creation process. This is an uncorroborated route, not a claim that the item is globally unobtainable.')
            continue
        if item == 'Base.CompostBag' and meaning == ['acquisition_process', 'fill_ground_bag', 'compost']:
            retain_boundary(claim, {records[0]['path'], sources.WORLD_MENU, *sources.COMPOST_ACTIONS},
                {'consumer': sources.COMPOST_TRANSFER}, 'Native compost amount, empty-sack replacement and inventory delivery',
                'The compost menu/action fills the existing bag or replaces an empty sack with this exact bag using available compost. It may fill only partly and does not collect ordinary ground or create compost from food.')
            continue
        if item == 'Base.UnusableMetal' and meaning in (['negative_role', 'crafting', 'material'], ['acquisition_process', 'metal_dismantling']):
            retain_boundary(claim, {records[0]['path'], semantic.MOVE, semantic.PROPS, semantic.CRAFT, semantic.GROUPS},
                {'scrap_definitions': ['Fridge', 'MetalPlates', 'MetalPlatesAndBars', 'SmallMetalPlates'],
                 'consumer': 'getScrapItemsList checks each material. When no usable result was added and unusableItem exists, one or two random entries are appended; addAllScrapItems requests instanceItem and addOrDropItem.'},
                'Native material-to-object binding, random/factory delivery and any additional exact crafting consumer',
                'The supplied fallback can return this exact item when usable metal recovery fails. It is neither guaranteed metal salvage nor a proof that every crafting route excludes the item; the negative claim remains bounded to the supplied recipe/consumer snapshot.')
            continue
        reading_mood = meaning[0] == 'conditional_effect' and meaning[1] in {'boredom', 'stress', 'unhappiness'} and meaning[3] == 'reading'
        if reading_mood:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Literature' and not fields.get('SkillTrained') and fields.get('CanBeWrite', '').lower() != 'true':
                partial = [f['ref'] for f in candidates if f['payload'] == {'property': meaning[1], 'direction': 'cap_at_reading_start'}]
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields, 'consumer': semantic.READ,
                                                              'partial_fact_refs': partial},
                               'required_input': 'IsoGameCharacter.ReadLiterature completion interpretation for this exact book',
                               'reason': 'The Lua reading update can restore a mood value that rose above its starting snapshot. That bounded stabilization is represented separately and does not prove the predecessor claim of mood reduction by completed reading.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                             verified_source_refs=[base['reader'].bindings[records[0]['path']], base['reader'].bindings[semantic.READ]],
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='bounded_lua_and_engine_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if ((meaning[0] == 'effect' and meaning[1] in {'hunger', 'thirst', 'food_sickness', 'wound_infection'})
                or meaning == ['condition', 'raw_ingestion', 'hazard']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Food' and not {'Type', 'CantEat', 'OnEat'} & conflicts.keys():
                evidence = [{'path': r['path'], 'line': r['line'], 'end_line': r['end_line'],
                             'sha256': base['reader'].bindings[r['path']]['sha256']} for r in records]
                evidence.append(base['reader'].bindings[semantic.EAT])
                uncertainty = {'examined': {'declaration': fields, 'consumer': semantic.EAT,
                                             'handoff': 'self.character:Eat(self.item, self.percentage)'},
                               'meaning': meaning, 'required_input': 'the native Eat effect interpretation for this exact food form',
                               'reason': 'The bound Lua checks eligibility but delegates the food state changes, including raw-food harm, to Eat. The exact DangerousUncooked, poison, nutritional and callback fields are retained in the declaration above; their presence or sign does not independently establish the claimed effect.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='engine_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
    inventory['conservation'] = conservation
    inventory['source_assessments'] = source_assessments
    for item in inventory['items']:
        claim_rows = [c for c in inventory['claims'] if c['item_id'] == item['item_id']]
        item['nonempty_internal_delta'] = {
            'already_represented': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'already_represented'],
            'recovered': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'recovered'],
            'corrected': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'corrected'],
            'unresolved': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'unresolved'],
            'responsibility_removed': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'responsibility_removed'],
            'pending': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'pending_investigation']}
    return inventory
