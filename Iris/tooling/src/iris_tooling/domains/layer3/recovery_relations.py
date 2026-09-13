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

    def named(item, food=False):
        fields = declarations[item]
        # EvolvedRecipeName is an ingredient category, not the result item's
        # name: e.g. mushroom soup must not become a claim of plain mushrooms.
        english = fields.get('DisplayName') or item
        korean = labels.get(item, english)
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
                                 for k in ('FabricType',) if k in declarations.get(item_id, {})}
        if item_id in declarations:
            # Reuse the admitted declaration and existing locale reader for
            # the current subject as well as results. No name-based use rules.
            subject = named(item_id)
            item['source_traits']['display_names'] = subject['names']
            item['source_traits']['name_observation_ref'] = subject['observation_ref']
        recovered = named_fabrics.get(item_id.split('.', 1)[-1]) or fabric_results.get(item['source_traits'].get('FabricType'))
        if recovered in declarations:
            item['source_traits']['fabric_result'] = named(recovered)
            dirty = recovered + 'Dirty'
            if dirty in declarations and 'FindItem(materials[1] .. "Dirty")' in groups_text:
                item['source_traits']['fabric_dirty_result'] = named(dirty)
        relations = []
        functions = {f['payload'].get('function'): f for f in by_item[item_id]
                     if f['fact_kind'] == 'direct_function'}
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
        'fabric_path': fabric_path, 'fabric_sha256': hashlib.sha256(fabric_raw).hexdigest(),
        'producer_sha256': hashlib.sha256((root / 'Iris/tooling/src/iris_tooling/domains/layer3/recovery_relations.py').read_bytes()).hexdigest()}
    return composition
