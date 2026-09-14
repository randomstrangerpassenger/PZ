"""Expose named participants from admitted source observations, without changing r6.

This is an A source adapter. A recipe is considered only through an admitted
function's provenance; result uses require their own admitted function. Prose
consumers receive structured values and never interpret recipe text.
"""
from collections import defaultdict
from copy import deepcopy
import hashlib
import re

from . import source_reader as reader

FUNCTIONS = {'unpack_canned_food', 'unpack_produce', 'unpack_ammunition',
             'unpack_seeds', 'unpack_eggs', 'unpack_jarred_food',
             'unpack_box_contents', 'prepare_frog_meat', 'dismantle_electronics'}

VEHICLE_PART_CATEGORIES = {
    'Tire': 'tire', 'Brake': 'brake', 'Suspension': 'suspension',
    'Battery': 'electrical', 'Headlight': 'electrical', 'Radio': 'electrical',
    'Radio_HAM': 'electrical', 'Seat': 'seat', 'Window': 'glazing',
    'Windshield': 'glazing', 'GasTank': 'fuel_tank', 'Muffler': 'exhaust',
    'Door': 'bodywork', 'EngineDoor': 'bodywork', 'TrunkDoor': 'bodywork',
}


def vehicle_tool_roles(text, item_id):
    """Only paired installation/removal requirements license the shared frame."""
    text = reader.mask(text)
    roles = defaultdict(set)
    for match in re.finditer(r'\btable\s+(install|uninstall)\s*\{', text):
        start, end, depth = match.end(), match.end(), 1
        while end < len(text) and depth:
            depth += (text[end] == '{') - (text[end] == '}')
            end += 1
        if depth:
            raise ValueError('unclosed vehicle operation table')
        for body in re.findall(r'\{([^{}]*)\}', text[start:end-1], re.S):
            fields = reader.unique_properties({'clauses': reader.clauses(body)})
            if fields and fields.get('type') == item_id and fields.get('keep') == 'true':
                role = 'direct' if fields.get('equip') in {'primary', 'both'} else 'support'
                roles[role].add(match[1])
    return {role for role, operations in roles.items() if operations == {'install', 'uninstall'}}



def enrich(root, semantic, composition):
    observations = semantic['observations']
    declarations = {}
    declaration_refs = {}
    for ref, observation in observations.items():
        content = observation.get('content', {})
        if not isinstance(content, dict) or not content.get('raw', '').lstrip().startswith('item '):
            continue
        item = observation['locator'].rsplit(':', 1)[-1]
        if not re.fullmatch(r'\w+\.\w+', item) or content.get('property_conflicts'):
            continue
        props = reader.properties({'clauses': content.get('clauses', [])}, '=')
        declarations[item] = {k: v[0] for k, v in props.items() if len(v) == 1}
        declaration_refs[item] = ref
    locale_path = 'lua/shared/Translate/KO/ItemName_KO.txt'
    locale_raw = (root / locale_path).read_bytes()
    locale_text = locale_raw.decode('utf-16' if locale_raw[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-8-sig')
    labels = dict(re.findall(r'ItemName_([\w.]+)\s*=\s*"([^"]+)"', locale_text))
    recipe_locale_path = 'lua/shared/Translate/KO/Recipes_KO.txt'
    recipe_locale_raw = (root / recipe_locale_path).read_bytes()
    recipe_locale_text = recipe_locale_raw.decode('utf-16' if recipe_locale_raw[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-8-sig')
    recipe_labels = dict(re.findall(r'Recipe_([^\s=]+)\s*=\s*"([^"\r\n]*)"', recipe_locale_text))
    # Minimal display spelling corrections; source labels and recipe keys stay
    # available as evidence. These replacements never select a use or role.
    source_labels, source_recipe_labels = dict(labels), dict(recipe_labels)
    def corrected_label(value):
        for original, corrected in (('스크류드라이버', '드라이버'), ('쿠기', '쿠키'), ('봉합용 바늘 집개', '봉합용 바늘 집게')):
            value = value.replace(original, corrected)
        return value
    labels = {key: corrected_label(value) for key, value in labels.items()}
    recipe_labels = {key: corrected_label(value) for key, value in recipe_labels.items()}
    # Vanilla KO has no entry for this declared recipe key. Translate the
    # recipe label itself; do not substitute another trap recipe or item text.
    recipe_labels.setdefault('Make_Wooden_Box_Trap', '나무 상자 덫 만들기')
    # The actual fallback explicitly names stairs and lamp-on-pillar. Other
    # dismantable constructors alone do not resolve normal-moveable routing.
    target_sources = {
        'lua/server/BuildingObjects/ISWoodenStairs.lua': ('thumpable:setIsDismantable(true)', '목제 계단', 'wooden stairs'),
        'lua/server/BuildingObjects/ISLightSource.lua': ('o.dismantable = true', '기둥 조명', 'pillar lamps'),
    }
    props_path = 'lua/client/Moveables/ISMoveableSpriteProps.lua'
    props_raw = (root / props_path).read_bytes()
    props_text = props_raw.decode('utf-8-sig')
    if 'like stairs and lamp-on-pillar' not in props_text or 'return ISThumpableSpriteProps.new(_object)' not in reader.mask(props_text, lua=True):
        raise ValueError('reviewed dismantling fallback target examples changed')
    target_bindings = [{'path': props_path, 'sha256': hashlib.sha256(props_raw).hexdigest()}]
    for path, (token, _, _) in target_sources.items():
        raw = (root / path).read_bytes()
        if token not in reader.mask(raw.decode('utf-8-sig'), lua=True):
            raise ValueError('constructed dismantling target changed: ' + path)
        target_bindings.append({'path': path, 'sha256': hashlib.sha256(raw).hexdigest()})
    use_target_paths = (
        'lua/server/BuildingObjects/PaintingReference.lua',
        'lua/server/BuildingObjects/ISPaintCursor.lua',
        'lua/client/BuildingObjects/ISUI/ISPaintMenu.lua',
        'lua/server/BuildingObjects/ISWoodenContainer.lua',
        'lua/server/BuildingObjects/ISBuildUtil.lua',
        'lua/client/BuildingObjects/ISUI/ISBuildMenu.lua',
        'lua/client/ISUI/ISWorldObjectContextMenu.lua',
    )
    use_target_bindings = [{'path': path, 'sha256': hashlib.sha256((root / path).read_bytes()).hexdigest()}
                           for path in use_target_paths]
    paint_path = 'lua/server/BuildingObjects/PaintingReference.lua'
    paint_source = (root / paint_path).read_text(encoding='utf-8-sig')
    paint_groups = []
    for table, scope, category, names in (
        ('Painting', 'mapped', {'ko': '벽', 'en': 'walls'},
         {'wall': ('벽', 'Walls'), 'doorframe': ('문틀', 'Door frames'), 'windowsframe': ('창틀', 'Window frames'), 'pillar': ('기둥', 'Pillars')}),
        ('OtherPainting', 'some', {'ko': '가구', 'en': 'furniture'},
         {'door': ('문', 'doors'), 'chair': ('의자', 'chairs'), 'crates': ('상자', 'crates'), 'table': ('탁자', 'tables')}),
    ):
        observed = set(re.findall(r'^' + table + r'\["([^"\]]+)"\]\s*=\s*\{', paint_source, re.M))
        if observed != set(names):
            raise ValueError('reviewed paint target mapping changed')
        paint_groups.append({'scope': scope, 'category': category, 'source_path': paint_path,
                             'targets': [{'key': key, 'ko': pair[0], 'en': pair[1]} for key, pair in names.items()]})
    purpose_fields = ('Type', 'DisplayCategory', 'Categories', 'SubCategory', 'Tags', 'Ranged', 'Poison',
                      'ExplosionPower', 'FirePower', 'SmokeRange', 'NoiseRange',
                      'RemoteController', 'RemoteRange', 'SensorRange', 'ExplosionTimer',
                      'CanBeRemote', 'CanBePlaced', 'AcceptMediaType', 'MediaCategory', 'ClothingItemExtraOption', 'WorldObjectSprite', 'BodyLocation', 'CanBeEquipped')

    def named(item, food=False):
        fields = declarations[item]
        # EvolvedRecipeName is an ingredient category, not the result item's
        # name: e.g. mushroom soup must not become a claim of plain mushrooms.
        english = fields.get('DisplayName') or item
        korean = labels.get(item, english)
        if korean.endswith(' (수제작)'):
            korean = '수제 ' + korean.removesuffix(' (수제작)')
        if food:
            # The opening frame already states container opening. Remove only
            # that explicit container/state label, preserving every food word:
            # Mushroom Soup remains Mushroom Soup, never the Mushroom category.
            if english.startswith('Opened Canned '):
                english = english.removeprefix('Opened Canned ')
            elif english.startswith('Opened '):
                english = english.removeprefix('Opened ')
            if korean.endswith(' 통조림 (열림)'):
                korean = korean.removesuffix(' 통조림 (열림)')
        return {'item_id': item, 'names': {'en': english, 'ko': korean},
                'name_basis': 'DisplayName/ItemName',
                'source_names': {'en': english, 'ko': source_labels.get(item, english)},
                'declared_traits': {k: fields[k] for k in purpose_fields if k in fields},
                **({'food_type': fields['FoodType']} if food and fields.get('FoodType') else {}),
                'observation_ref': declaration_refs[item]}

    # Consumption belongs to the exact declared opened result, never to the
    # unopened input. Keep its fact and scoped conditions as separate evidence.
    consumption = {}
    for target in composition['items']:
        candidates = [f for b in target['blocks'] for branch in b['branches'] for f in branch['facts']
                      if f['fact_kind'] == 'direct_function' and f['payload'].get('function')
                      in {'eat_food', 'consume_edible_food', 'drink_food_contents'}]
        if len(candidates) == 1:
            fact = candidates[0]
            consumption[target['item_id']] = {'fact': deepcopy(fact),
                'qualifiers': deepcopy([q for q in target['qualifiers']
                                       if fact['fact_ref'] in q['applies_to_fact_refs']])}

    recipe_files = {}

    def recipe_record(observation):
        content = observation['content']
        if content.get('module'):
            return {'clauses': content['clauses'], 'module': content['module']}
        path = observation['source_path']
        if path not in recipe_files:
            raw = (root / path).read_bytes()
            if hashlib.sha256(raw).hexdigest() != observation['source_sha256']:
                raise ValueError('admitted recipe source drift: ' + path)
            recipe_files[path] = reader.declarations(raw.decode('utf-8-sig'), path)
        matches = [r for r in recipe_files[path] if r['kind'] == 'recipe' and r['raw'] == content['raw']]
        if len(matches) != 1:
            return None
        return matches[0]

    by_item = defaultdict(list)
    for fact in semantic['facts']:
        by_item[fact['item_id']].append(fact)
    groups_ref, groups_text = next(((ref, o['content']['source_text']) for ref, o in observations.items()
                        if isinstance(o.get('content'), dict) and o.get('source_path') == 'lua/server/recipecode.lua'
                        and 'source_text' in o['content']), (None, ''))
    groups = reader.groups(groups_text)
    fabric_path = 'lua/shared/Definitions/ClothingRecipesDefinitions.lua'
    fabric_raw = (root / fabric_path).read_bytes()
    fabric_text = re.sub(r'--[^\n]*', '', fabric_raw.decode('utf-8-sig'))
    fabric_results = dict(re.findall(r'ClothingRecipesDefinitions\["FabricType"\]\["([^"]+)"\]\.material\s*=\s*"([^"]+)"', fabric_text))
    named_fabrics = dict(re.findall(r'ClothingRecipesDefinitions\["([^"]+)"\]\s*=\s*\{materials="([\w.]+):\d+"', fabric_text))
    for item in composition['items']:
        item_id = item['item_id']
        item['source_traits'] = {k: declarations.get(item_id, {})[k]
                                 for k in ('FabricType', 'FoodType') + purpose_fields if k in declarations.get(item_id, {})}
        learned = []
        for fact in by_item[item_id]:
            fn = fact['payload'].get('function', '')
            if fn.startswith('learn_literature_') and fn not in {'learn_literature_mechanics', 'learn_literature_herbalist', 'learn_literature_generator'}:
                refs = sorted({ref for pid in fact['provenance_refs'] for ref in semantic['provenance'][pid]['observation_refs']})
                recipe_names = {observations[ref]['content'].get('name') for ref in refs
                                if isinstance(observations[ref].get('content'), dict) and observations[ref]['content'].get('kind') == 'recipe'}
                if fn == 'learn_literature_metalconstruction':
                    recipe_names.update({'Make Metal Walls', 'Make Metal Roof', 'Make Metal Containers', 'Make Metal Fences'})
                values = [x.strip() for x in declarations.get(item_id, {}).get('TeachedRecipes', '').split(';') if x.strip() in recipe_names]
                if values:
                    learned.append({'function': fn, 'fact_ref': fact['fact_id'], 'observation_refs': refs,
                        'recipes': [{'key': value, 'source_names': {'ko': source_recipe_labels.get(value.replace(' ', '_'), value), 'en': value}, 'operation': ('make' if value.startswith(('Make ', 'Craft ')) else 'repair' if value.startswith('Fix ') else 'modify' if value.startswith('Add ') else 'recover' if value.startswith('Get ') and value.endswith(' Back') else 'other'), 'names': {'ko': recipe_labels.get(value.replace(' ', '_'), value), 'en': value}} for value in dict.fromkeys(values)]})
        if learned:
            # Classify only the contents already admitted as learned recipes.
            # Declared results describe those contents, not new uses of inputs.
            for lesson in learned:
                for recipe in lesson['recipes']:
                    results = {}
                    for ref in lesson['observation_refs']:
                        observation = observations[ref]
                        content = observation.get('content', {})
                        if not isinstance(content, dict) or content.get('kind') != 'recipe' or content.get('name') != recipe['key']:
                            continue
                        record = recipe_record(observation)
                        # This is the declared result's category, not a claim
                        # about callback effects or a new result-use relation.
                        if record is None:
                            continue
                        participants, opaque = reader.recipe_participants(record, declarations, groups)
                        if opaque:
                            continue
                        for participant in participants:
                            if participant['role'] == 'result' and participant['item_id'] in declarations:
                                value = named(participant['item_id'])
                                value['recipe_observation_ref'] = ref
                                results[participant['item_id']] = value
                    recipe['declared_results'] = list(results.values())
            item['source_traits']['learned_recipes'] = learned
        if any(f['payload'].get('function') == 'paint_supported_surface' for f in by_item[item_id]):
            item['source_traits']['action_targets'] = [{'function': 'paint_supported_surface', 'action': 'paint',
                'role': 'painting_supply', 'coverage': 'mapped_categories', 'groups': deepcopy(paint_groups)}]
        if any(f['payload'].get('function') == 'dismantle_built_object' for f in by_item[item_id]):
            item['source_traits']['dismantling_targets'] = [{'ko': ko, 'en': en, 'source_path': path}
                for path, (_, ko, en) in target_sources.items()]
        if item_id in declarations:
            # Reuse the admitted declaration and existing locale reader for
            # the current subject as well as results. No name-based use rules.
            subject = named(item_id)
            item['source_traits']['display_names'] = subject['names']
            item['source_traits']['name_observation_ref'] = subject['observation_ref']
            fields = declarations[item_id]
            alternate_names = fields.get('ClothingItemExtra', '').split(';')
            alternate_options = fields.get('ClothingItemExtraOption', '').split(';')
            if len(alternate_names) == len(alternate_options):
                alternatives = []
                for target, option in zip(alternate_names, alternate_options):
                    if not target:
                        continue
                    if '.' not in target:
                        target = item_id.split('.')[0] + '.' + target
                    if target in declarations:
                        destination = declarations[target]
                        location = destination.get('BodyLocation') or destination.get('CanBeEquipped')
                        if location:
                            alternatives.append({'option': option, 'location': location, 'observation_ref': declaration_refs[target]})
                item['source_traits']['wearing_alternatives'] = alternatives
        recovered = named_fabrics.get(item_id.split('.', 1)[-1]) or fabric_results.get(item['source_traits'].get('FabricType'))
        if recovered in declarations:
            item['source_traits']['fabric_result'] = named(recovered)
            dirty = recovered + 'Dirty'
            if dirty in declarations and 'FindItem(materials[1] .. "Dirty")' in groups_text:
                item['source_traits']['fabric_dirty_result'] = named(dirty)
        relations = []
        repair_targets = {}
        for fact in by_item[item_id]:
            if fact['payload'] != {'role': 'repair_material'}:
                continue
            for provenance in fact['provenance_refs']:
                for ref in semantic['provenance'][provenance]['observation_refs']:
                    content = observations[ref].get('content', {})
                    if not isinstance(content, dict) or not content.get('raw', '').lstrip().startswith('fixing '):
                        continue
                    props = reader.properties({'clauses': content.get('clauses', [])}, ':')
                    for value in props.get('Require', []):
                        for token in value.split(';'):
                            target = token.strip()
                            if '.' not in target:
                                target = 'Base.' + target
                            if target in declarations:
                                repair_targets[target] = {**named(target), 'fixing_observation_ref': ref}
        item['source_traits']['repair_targets'] = [repair_targets[k] for k in sorted(repair_targets)]
        functions = {f['payload'].get('function'): f for f in by_item[item_id]
                     if f['fact_kind'] == 'direct_function'}
        if 'service_vehicle_parts' in functions:
            fact = functions['service_vehicle_parts']
            refs = sorted({r for p in fact['provenance_refs']
                           for r in semantic['provenance'][p]['observation_refs']})
            service_roles = {}
            categories = VEHICLE_PART_CATEGORIES
            for ref in refs:
                obs = observations[ref]
                path = obs['source_path']
                if not path.startswith('scripts/vehicles/template_'):
                    continue
                raw = (root / path).read_bytes()
                if hashlib.sha256(raw).hexdigest() != obs['source_sha256']:
                    raise ValueError('admitted vehicle template drift: ' + path)
                text = reader.mask(raw.decode('utf-8-sig'))
                template = re.search(r'\btemplate\s+vehicle\s+(\w+)', text)
                if not template or template[1] not in categories:
                    continue
                for role in vehicle_tool_roles(text, item_id):
                    key = (categories[template[1]], role)
                    service_roles.setdefault(key, []).append(ref)
            item['source_traits']['vehicle_service_roles'] = [
                {'category': category, 'role': role, 'observation_refs': sorted(set(refs))}
                for (category, role), refs in sorted(service_roles.items())]
        for fn in sorted(FUNCTIONS & functions.keys()):
            fact = functions[fn]
            evidence = sorted({r for p in fact['provenance_refs']
                               for r in semantic['provenance'][p]['observation_refs']})
            for ref in evidence:
                observation = observations[ref]
                content = observation.get('content', {})
                if not isinstance(content, dict) or not content.get('raw', '').lstrip().startswith('recipe '):
                    continue
                record = recipe_record(observation)
                if record is None:
                    continue
                participants, opaque = reader.recipe_participants(record, declarations, groups)
                if opaque or not any(p['item_id'] == item_id and p['role'] in {'input', 'destroy'} for p in participants):
                    continue
                outputs = [p for p in participants if p['role'] == 'result']
                if len(outputs) != 1 or outputs[0]['item_id'] not in declarations:
                    continue
                output = outputs[0]
                tools = defaultdict(list)
                for p in participants:
                    if p['role'] == 'keep' and p['item_id'] in declarations:
                        tool = named(p['item_id'])
                        if 'CanOpener' in declarations[p['item_id']].get('Tags', '').split(';'):
                            tool['names']['ko'] = '통조림 따개'
                        tools[p['ordinal']].append(tool)
                result = named(output['item_id'], food=fn in {'unpack_canned_food', 'unpack_produce', 'unpack_jarred_food'})
                result.update(kind='declared', count=output['clause'].split('=', 1)[1] if '=' in output['clause'] else '1')
                relation = {'function': fn, 'fact_refs': [fact['fact_id']], 'input_role': 'transformation_target',
                            'tools': [{'mode': 'any_of', 'consumed': False, 'items': tools[n]} for n in sorted(tools)],
                            'results': [result], 'observation_refs': evidence, 'result_use': None}
                use = 'sow_extracted_seeds' if fn == 'unpack_seeds' else 'prepare_opened_food_ingredient'
                if use in functions and fn.startswith('unpack_'):
                    relation['result_use'] = use
                    relation['fact_refs'].append(functions[use]['fact_id'])
                if fn == 'unpack_canned_food' and output['item_id'] in consumption:
                    relation['result_consumption'] = deepcopy(consumption[output['item_id']])
                    result_fact = relation['result_consumption']['fact']
                    relation['observation_refs'] = sorted(set(evidence) | {
                        ref for provenance in result_fact['provenance_refs']
                        for ref in semantic['provenance'][provenance]['observation_refs']})
                props = reader.properties(record, ':')
                if props.get('OnCreate') == ['Recipe.OnCreate.DismantleTVRemote']:
                    # This reviewed callback adds scrap outside the random branch.
                    # Battery construction/delivery remains conditional.
                    callback = groups_text.split('function Recipe.OnCreate.DismantleTVRemote(', 1)[-1].split('\nfunction ', 1)[0]
                    if 'player:getInventory():AddItem("Base.ElectronicsScrap");' in callback and 'if (ZombRand(0,100) < success)' in callback:
                        for target, kind in [('Base.ElectronicsScrap', 'callback_unconditional'), ('Base.Battery', 'callback_conditional')]:
                            if target in declarations:
                                relation['results'].append({**named(target), 'kind': kind, 'count': None})
                relations.append(relation)
        # Expose declared crafting targets through the same admitted recipe
        # observations. Callback-produced results need their existing specific
        # adapter; never treat a nominal callback result as a guaranteed output.
        local_facts = {f['fact_id']: f for f in by_item[item_id]}
        recipe_relations = {}
        for role_fact in by_item[item_id]:
            if role_fact['fact_kind'] != 'context_role':
                continue
            context = local_facts.get(role_fact.get('context_fact_ref'))
            if context is None or context['fact_kind'] != 'use_context':
                continue
            role = role_fact['payload']['role']
            if role not in {'tool', 'material', 'ingredient', 'attachment', 'container', 'transformation_target'}:
                continue
            evidence = sorted({r for f in (role_fact, context) for p in f['provenance_refs']
                               for r in semantic['provenance'][p]['observation_refs']})
            for ref in evidence:
                content = observations[ref].get('content', {})
                if not isinstance(content, dict) or not content.get('raw', '').lstrip().startswith('recipe '):
                    continue
                record = recipe_record(observations[ref])
                if record is None:
                    continue
                props = reader.properties(record, ':')
                callbacks = props.get('OnCreate', [])
                # These admitted callbacks change food properties, not the
                # declared result type/count. Optional returned vessels are
                # separate from the declared crafting target exposed here.
                fixed_result_callbacks = {'Recipe.OnCreate.' + name for name in (
                    'SliceWatermelon', 'SliceBread', 'SliceBreadDough', 'SliceHam',
                    'SliceSalami', 'SlicePie', 'CutFish', 'CutAnimal',
                    'PutCakeBatterInBakingPan', 'GetMuffin', 'GetBiscuit',
                    'GetCookies', 'SlicePizza', 'BeanBowl', 'MakeOatmeal')}
                if callbacks and (len(callbacks) != 1 or callbacks[0] not in fixed_result_callbacks
                                  or 'function ' + callbacks[0] + '(' not in groups_text):
                    continue
                participants, opaque = reader.recipe_participants(record, declarations, groups)
                expected = {'keep'} if role == 'tool' else {'input', 'destroy'}
                if opaque or not any(p['item_id'] == item_id and p['role'] in expected for p in participants):
                    continue
                outputs = [p for p in participants if p['role'] == 'result']
                if not outputs or any(p['item_id'] not in declarations for p in outputs):
                    continue
                tool_groups = defaultdict(list)
                if context['payload']['activity'] == 'food_portioning' and role == 'ingredient':
                    for participant in participants:
                        if participant['role'] == 'keep' and participant['item_id'] in declarations:
                            tool_groups[participant['ordinal']].append(named(participant['item_id']))
                key = (context['fact_id'], role_fact['fact_id'], ref)
                recipe_relations[key] = {
                    'function': 'recipe_use', 'activity': context['payload']['activity'],
                    'fact_refs': sorted([context['fact_id'], role_fact['fact_id']]),
                    'input_role': role, 'tools': [{'mode': 'any_of', 'consumed': False, 'items': tool_groups[n]} for n in sorted(tool_groups)], 'result_use': None,
                    'results': [{**named(p['item_id'], food=context['payload']['activity'] == 'package_opening'
                                        and declarations[p['item_id']].get('Type') == 'Food'), 'kind': 'declared',
                                 'count': p['clause'].split('=', 1)[1] if '=' in p['clause'] else '1'} for p in outputs],
                    'observation_refs': sorted({ref, groups_ref}) if callbacks else [ref],
                }
                # A processing material may explain the immediate result's
                # purpose. This bounded join does not inherit every later use.
                if role in {'material', 'ingredient', 'container'} and len(outputs) == 1:
                    purposes = [f for f in by_item[outputs[0]['item_id']]
                                if f['payload'].get('function') == 'plaster_supported_structure']
                    if len(purposes) == 1:
                        purpose = purposes[0]
                        recipe_relations[key]['result_purpose'] = {
                            'function': purpose['payload']['function'], 'fact_ref': purpose['fact_id'],
                            'observation_refs': sorted({r for p in purpose['provenance_refs']
                                                       for r in semantic['provenance'][p]['observation_refs']})}
                if context['payload']['activity'] == 'explosive_modification':
                    # The admitted Add recipes consume the device first,
                    # the fitted component second, then assembly supplies.
                    inputs = [p for p in participants if p['role'] in {'input', 'destroy'}]
                    ordinals = sorted({p['ordinal'] for p in inputs})
                    positions = {ordinals.index(p['ordinal']) for p in inputs if p['item_id'] == item_id}
                    if len(positions) == 1:
                        recipe_relations[key]['modification_role'] = {0: 'target', 1: 'component'}.get(next(iter(positions)), 'assembly_material')
                if callbacks == ['Recipe.OnCreate.SlicePizza']:
                    # The callback explicitly names the result as a slice;
                    # the KO base item label alone omits that distinction.
                    for result in recipe_relations[key]['results']:
                        if not result['names']['ko'].endswith(' 조각'):
                            result['names']['ko'] += ' 조각'
                        result['name_basis'] = 'DisplayName/ItemName with SlicePizza slice result'
                returned = {'Recipe.OnCreate.GetMuffin': 'Base.MuffinTray',
                            'Recipe.OnCreate.GetBiscuit': 'Base.MuffinTray',
                            'Recipe.OnCreate.GetCookies': 'Base.BakingTray'}.get(callbacks[0] if callbacks else None)
                if returned and returned in declarations:
                    body = groups_text.split('function ' + callbacks[0] + '(', 1)[1].split('\nfunction ', 1)[0]
                    if 'player:getInventory():AddItem("' + returned + '");' not in body:
                        raise ValueError('reviewed returned tray no longer present')
                    recipe_relations[key]['callback'] = callbacks[0]
                    recipe_relations[key]['results'].append({**named(returned), 'kind': 'callback_unconditional', 'count': '1'})
        relations.extend(recipe_relations[k] for k in sorted(recipe_relations))
        item['use_relations'] = relations
    composition['source']['relation_adapter'] = {'name': 'admitted source participants', 'locale_path': locale_path,
        'locale_sha256': hashlib.sha256(locale_raw).hexdigest(),
        'recipe_locale_path': recipe_locale_path, 'recipe_locale_sha256': hashlib.sha256(recipe_locale_raw).hexdigest(),
        'dismantling_target_sources': target_bindings,
        'paint_and_padlock_target_sources': use_target_bindings,
        'fabric_path': fabric_path, 'fabric_sha256': hashlib.sha256(fabric_raw).hexdigest(),
        'producer_sha256': hashlib.sha256((root / 'Iris/tooling/src/iris_tooling/domains/layer3/recovery_relations.py').read_bytes()).hexdigest()}
    return composition
