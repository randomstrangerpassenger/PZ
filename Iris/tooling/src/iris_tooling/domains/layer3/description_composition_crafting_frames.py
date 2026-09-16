"""Crafting purpose frames; selection and consumption stay with the assembly."""
from .description_composition_frame_rules import (
    CONSTRUCTION_PREDICATES,
    detail_text,
    device_category,
    en,
    ko,
    lex,
    purpose_tokens,
    target_groups,
)


def render(state):
    compact = state.compact
    emit = state.emit
    emit_material = state.emit_material
    functions = state.functions
    locale = state.locale
    object_name = state.object_name
    output = state.output
    parallel_names = state.parallel_names
    plan = state.plan
    select = state.select
    units = state.units
    used = state.used
    water_handling = select({'store_water', 'carry_water', 'pour_water_into_container', 'supply_world_water_storage'})
    if not compact and functions >= {'store_water', 'carry_water', 'pour_water_into_container', 'supply_world_water_storage'}:
        emit(water_handling + select({'receive_poured_water'}), lex.pair(('물을 담아 보관하거나 운반하고, 다른 용기나 물 저장 시설로 옮길 수 있다', 'It can store and carry water and transfer it to other containers or water storage fixtures'), locale))

    # Recipe participants explain a field of use, not a catalogue of outputs.
    crafting_members, crafting_phrases = [], []
    for contexts, wording in (
        ({'fishing_gear_crafting', 'spear_crafting', 'trap_crafting', 'trap_preparation'}, ('사냥이나 낚시에 쓸 장비를 만드는 데 쓸 수 있다', 'It can be used to make hunting or fishing equipment')),
        ({'bomb_crafting', 'explosive_assembly'}, ('폭발 장치를 만드는 데 쓸 수 있다', 'It can be used to make explosive devices')),
        ({'pumpkin_carving'}, ('호박을 장식용으로 깎는 데 쓸 수 있다', 'It can be used to carve decorative pumpkins'))):
        members = [u for u in units if not used & set(u['fact_refs'])
                   and purpose_tokens(u) - {None} <= contexts and purpose_tokens(u) & contexts
                   and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'tool'}]
        if members and 'fishing_gear_crafting' in contexts:
            activities = set().union(*(purpose_tokens(u) for u in members))
            field = ('사냥과 낚시 장비', 'hunting and fishing equipment') if 'fishing_gear_crafting' in activities and activities & {'spear_crafting', 'trap_crafting', 'trap_preparation'} else ('낚시 장비', 'fishing equipment') if 'fishing_gear_crafting' in activities else ('사냥 장비', 'hunting equipment')
            wording = (field[0] + '를 만드는 데 쓸 수 있다', 'It can be used to make ' + field[1])
        if members:
            crafting_members += members
            crafting_phrases.append(wording)
    if crafting_members:
        if locale == 'ko':
            actions = [p[0].removesuffix(' 데 쓸 수 있다') for p in crafting_phrases]
            if all(a.endswith(' 만드는') for a in actions):
                nouns = [a.removesuffix(' 만드는') for a in actions]
                nouns = [n[:-1] if n.endswith(('을', '를')) else n for n in nouns]
                text = object_name(ko.alternatives(nouns)) + ' 만드는 데 쓸 수 있다'
            else:
                stems = [a.removesuffix('만드는') + '만들' if a.endswith('만드는') else a.removesuffix('는') for a in actions[:-1]]
                text = '거나 '.join(stems + actions[-1:]) + ' 데 쓸 수 있다'
        else:
            actions = [p[1].removeprefix('It can be used to ') for p in crafting_phrases]
            text = 'It can be used to ' + ('make ' + en.join([a.removeprefix('make ') for a in actions]) if all(a.startswith('make ') for a in actions) else en.join(actions))
        emit(crafting_members, text)

    if not compact:
        food_tasks = {'animal_butchery', 'fish_preparation', 'frog_preparation', 'food_portioning', 'food_preparation'}
        food_tools = [u for u in units if not used & set(u['fact_refs']) and purpose_tokens(u) - {None} <= food_tasks and purpose_tokens(u) & food_tasks
                      and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'tool'}]
        activities = set().union(*(purpose_tokens(u) for u in food_tools)) - {None}
        if len(activities) > 1:
            terms = []
            if activities & {'animal_butchery', 'frog_preparation'}: terms.append(('잡은 동물 손질', 'butchering caught animals'))
            if 'fish_preparation' in activities: terms.append(('생선살 손질', 'preparing fish fillets'))
            if 'food_portioning' in activities: terms.append(('음식 나누기', 'portioning food'))
            if 'food_preparation' in activities: terms.append(('조리 준비', 'preparing ingredients for cooking'))
            handling = []
            if activities & {'animal_butchery', 'frog_preparation'}: handling.append('잡은 동물')
            if 'fish_preparation' in activities: handling.append('생선')
            actions = [object_name('과 '.join(handling)) + ' 손질하'] if handling else []
            if 'food_portioning' in activities: actions.append('음식을 나누')
            if 'food_preparation' in activities: actions.append('조리할 재료를 준비하')
            korean = '거나 '.join(actions) + '는 데 쓸 수 있다'
            emit(food_tools, korean if locale == 'ko' else 'It can be used for ' + en.join([t[1] for t in terms]))
        for unit in units:
            if used & set(unit['fact_refs']) or purpose_tokens(unit) - {None} != {'woodworking'}: continue
            if {f['payload'].get('role') for f in unit['facts'] if f['fact_kind'] == 'context_role'} != {'tool'}: continue
            relations = unit.get('recipe_targets', [])
            if not relations or any(len(r['results']) != 1 or not r.get('inputs') for r in relations): continue
            # Same-purpose processing examples, not downstream uses of outputs.
            pairs = {}
            for rel in relations:
                inputs = rel['inputs']; result = rel['results'][0]
                key = tuple(i['item_id'] for i in inputs)
                entry = pairs.setdefault(key, {'inputs': inputs, 'results': {}})
                entry['results'][result['item_id']] = result
            clauses = []
            for entry in pairs.values():
                inputs, results = entry['inputs'], list(entry['results'].values())
                # Several source alternatives need not be used together.
                source_name = (inputs[0]['names'][locale] if locale == 'ko' else en.object_phrase(inputs[0])) if len(inputs) == 1 else (ko.alternatives([i['names'][locale] for i in inputs]) if locale == 'ko' else ' or '.join(en.object_phrase(i) for i in inputs))
                names = [r['names'][locale] if locale == 'ko' else en.object_phrase(r) for r in results]
                target = ko.alternatives(names) if locale == 'ko' else names[0] if len(names) == 1 else ' or '.join(names)
                clauses.append((object_name(source_name) + ' ' + ko.instrumental(target) + ' 가공') if locale == 'ko' else (source_name + ' into ' + target))
            text = ('하거나 '.join(clauses) + '하는 데 쓸 수 있다') if locale == 'ko' else 'It can be used to shape ' + ', or to shape '.join(clauses)
            emit([unit], text)

    # Resolve the player's use of a recipe participant before generic role
    # grammar. Declared result identities distinguish a processed target from
    # another material in the same activity; no item-specific prose is used.
    for unit in units:
        activities = purpose_tokens(unit) - {None}
        roles = {f['payload'].get('role') for f in unit['facts'] if f['fact_kind'] == 'context_role'}
        results = {x['item_id']: x for r in unit.get('recipe_targets', []) for x in r['results'] if x['kind'] == 'declared'}
        wording = None
        if activities == {'bandaging_material_preparation'} and roles == {'material'}:
            if set(results) == {'Base.AlcoholedCottonBalls'}:
                wording = ('소독솜을 만드는 데 쓸 수 있다', 'It can be used to make disinfected cotton balls')
            elif results and set(results) <= {'Base.AlcoholBandage', 'Base.AlcoholRippedSheets'} and select({'apply_bandage'}):
                continue  # An alternative preparation of the same bandaging use.
            elif results and set(results) <= {'Base.Bandage', 'Base.RippedSheets', 'Base.DenimStrips', 'Base.LeatherStrips'} and not select({'wash_bandaging_material'}):
                wording = ('오염되지 않은 물로 씻어 다시 붕대로 쓸 수 있다', 'It can be washed with untainted water for reuse as bandaging')
            elif not results or set(results) <= {'Base.AlcoholBandage', 'Base.AlcoholRippedSheets', 'Base.AlcoholedCottonBalls'}:
                wording = (('붕대 소독에 쓸 수 있다', 'It can be used to disinfect bandaging') if 'store_water' in functions else
                           ('천이나 솜을 소독하는 데 쓸 수 있다', 'It can be used to disinfect cloth or cotton'))
        elif activities & {'animal_butchery', 'fish_preparation', 'frog_preparation'} and roles <= {'ingredient', 'material'}:
            wording = ('손질해 고기를 얻을 수 있다', 'It can be butchered to obtain meat')
        elif activities == {'item_packaging'} and roles == {'material'} and set(results) == {'Base.EggCarton'}:
            wording = ('달걀곽에 모아 포장할 수 있다', 'It can be packed with other eggs into a carton')
        elif activities == {'poultice_preparation'} and roles <= {'ingredient', 'material'}:
            wording = ('약초 찜질제를 만드는 데 쓸 수 있다', 'It can be used to make herbal poultices')
        elif activities == {'poultice_preparation'} and roles == {'tool'}:
            wording = ('약초 찜질제를 만드는 도구로 쓸 수 있다', 'It can be used as a tool for making herbal poultices')
        if wording and wording[0] == '천이나 솜을 소독하는 데 쓸 수 있다' and select({'disinfect_wound'}):
            wounds = select({'disinfect_wound'})
            wound_effects = [u for u in units if not used & set(u['fact_refs']) and any(
                f['payload'].get('property') == 'wound_alcohol_level' and f['payload'].get('direction') == 'increase'
                for f in u['facts'])]
            emit([unit] + wounds + wound_effects, '천, 솜, 상처를 소독하는 데 쓸 수 있다' if locale == 'ko'
                 else 'It can be used to disinfect cloth, cotton or wounds')
            continue
        if wording:
            cooking_partners = [u for u in units if not used & set(u['fact_refs'])
                                and purpose_tokens(u) & {'food_preparation', 'food_ingredient_addition', 'grain_preparation'}
                                and any(f['payload'].get('role') in {'container', 'base'} for f in u['facts'])]
            if compact and wording[0] == '붕대 소독에 쓸 수 있다' and cooking_partners:
                emit([unit] + cooking_partners, lex.pair(('조리와 붕대 소독에 쓸 수 있다', 'It can be used for cooking and disinfecting bandaging'), locale))
            else:
                emit([unit], lex.pair(wording, locale))

    splint_materials = [u for u in units if not used & set(u['fact_refs']) and 'splint_crafting' in purpose_tokens(u)
                        and any(f['payload'].get('role') == 'material' for f in u['facts'])]
    if splint_materials and select({'apply_splint'}):
        members = splint_materials + select({'apply_splint'})
        wording = lex.pair(('골절을 고정하는 부목 재료로 쓸 수 있다',
                           'It can supply splinting material for fractures'), locale)
        if compact and not select({'apply_garment_patch'}):
            # Share the material role with other fields. Clothing/first-aid
            # participants still use their existing combined treatment frame.
            emit_material(members, [('action', lex.pair(('부목 제작', 'making splints'), locale))], wording)
        else:
            emit(members, wording)

    # Group by supplied purpose and role before realizing sentences. A named
    # result is covered only by an actually established parent category.
    for fn, label, wording in (
        ('convert_lamp_to_battery', ('장치 개조', 'modifying devices'),
         ('조명을 건전지용으로 개조하는 재료로 쓸 수 있다', 'It can supply material for converting lamps to battery power')),
        ('repair_generator', ('발전기 수리', 'repairing generators'),
         ('손상된 발전기를 수리하는 재료로 쓸 수 있다', 'It can supply repair material for damaged generators')),
    ):
        members = select({fn})
        if members and plan.get('source_traits', {}).get('DisplayCategory') != 'Tool':
            emit_material(members, [('action', lex.pair(label, locale))], lex.pair(wording, locale))
    restored = [r for r in plan.get('use_relations', []) if r.get('processing_role') == 'restoration_target']
    if restored:
        refs = {ref for r in restored for ref in r['fact_refs']}
        members = [u for u in units if refs & set(u['fact_refs']) and not used & set(u['fact_refs'])]
        results = {r['item_id']: r for rel in restored for r in rel['results']}
        labels = list(dict.fromkeys(r['names'][locale] if locale == 'ko' else en.object_phrase(r) for r in results.values()))
        text = '수리해 ' + ko.alternatives(labels) + '로 다시 쓸 수 있다' if locale == 'ko' else 'It can be repaired for reuse as ' + en.join(labels)
        emit(members, text, accepted_predicates={lex.source.MATERIAL_ASSEMBLY, lex.source.ROD_REPAIR_INPUT})

    if not compact:
        targets = plan.get('source_traits', {}).get('construction_targets', [])
        if targets and all(t['names'] for t in targets):
            members = [u for u in units if not used & set(u['fact_refs']) and purpose_tokens(u) - {None} <= {'carpentry_menu_construction', 'construction'} and purpose_tokens(u) & {'carpentry_menu_construction', 'construction'}
                       and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'material'}]
            labels = list(dict.fromkeys(t['names'][locale] for t in targets))
            name = ko.alternatives(labels) if locale == 'ko' else en.join(labels)
            emit(members, object_name(name) + ' 만드는 재료로 쓸 수 있다' if locale == 'ko' else 'It can be used as material for making ' + name)
        # Furniture result detail belongs to its own material relationship.
        # A remaining same-role woodworking overview already covers this
        # purpose; otherwise one confirmed result can provide useful detail.
        # Unrelated construction targets cannot enable or disable the result.
        material_work = [u for u in units if not used & set(u['fact_refs'])
                         and purpose_tokens(u) - {None} == {'woodworking'}
                         and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'material'}
                         and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} <= CONSTRUCTION_PREDICATES]
        furniture = [u for u in units if not used & set(u['fact_refs'])
                     and purpose_tokens(u) - {None} == {'furniture_crafting'}
                     and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'material'}]
        results = {r['item_id']: r for u in furniture for rel in u.get('recipe_targets', []) for r in rel['results']}
        if furniture and not material_work and len(results) == 1 and all(u.get('recipe_targets') for u in furniture):
            result = next(iter(results.values()))
            emit(furniture, object_name(result['names'][locale]) + ' 만드는 재료로 쓸 수 있다' if locale == 'ko' else 'It can be used as material for making ' + en.object_phrase(result))

    purpose_groups = (
        ({'woodworking', 'furniture_crafting', 'construction', 'carpentry_menu_construction', 'metal_welding_construction', 'welded_parts'}, ('목공과 건축에 쓰는', 'woodworking and construction')),
        ({'electronic_assembly', 'radio_crafting'}, ('전자 기기를 만드는', 'making electronic devices')),
        ({'explosive_assembly'}, None),
        ({'spear_crafting', 'trap_crafting', 'fishing_gear_crafting'}, ('사냥과 낚시 장비를 만드는', 'making hunting and fishing equipment')),
        ({'campfire_kit_preparation', 'mattress_preparation', 'tent_kit_making', 'camping_kit_preparation'}, ('야영 장비를 만드는', 'making camping equipment')),
        ({'tool_crafting', 'stone_tool_crafting'}, ('도구를 만드는', 'making tools')),
        ({'hat_crafting'}, ('모자를 만드는', 'making hats')),
        ({'splint_crafting'}, ('골절을 고정할 부목을 만드는', 'making splints for fractures')),
    )
    for contexts, label in purpose_groups:
        members = [u for u in units if not used & set(u['fact_refs'])
                   and purpose_tokens(u) - {None} <= contexts and purpose_tokens(u) & contexts
                   and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'material'}
                   and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} <= CONSTRUCTION_PREDICATES | {lex.source.WELDING_CONSTRUCTION} | ({lex.source.WELDED_PARTS} if compact else set())]
        if contexts == {'tool_crafting', 'stone_tool_crafting'}:
            members += [u for u in units if not used & set(u['fact_refs']) and purpose_tokens(u) - {None} == {'metal_forging'}
                        and any(f['payload'].get('role') == 'material' for f in u['facts']) and not u['qualifier_refs']
                        and u.get('recipe_targets') and all(r.get('declared_traits', {}).get('DisplayCategory') == 'Tool'
                            for rel in u['recipe_targets'] for r in rel['results'])]
        if not members:
            continue
        activities = set().union(*(purpose_tokens(u) for u in members))
        camping_purposes = {
            'campfire_kit_preparation': ('모닥불 도구', 'campfire kits'),
            'mattress_preparation': ('매트리스', 'mattresses'),
            'tent_kit_making': ('텐트', 'tents'),
        }
        if activities - {None} and activities - {None} <= camping_purposes.keys():
            purposes = [camping_purposes[a] for a in camping_purposes if a in activities]
            label = (object_name(' 및 '.join(p[0] for p in purposes)) + ' 만드는',
                     'making ' + en.join([p[1] for p in purposes]))
        if contexts == {'spear_crafting', 'trap_crafting', 'fishing_gear_crafting'}:
            label = (('사냥과 낚시 장비를 만드는', 'making hunting and fishing equipment') if 'fishing_gear_crafting' in activities and activities & {'spear_crafting', 'trap_crafting'} else
                     ('낚시 장비를 만드는', 'making fishing equipment') if 'fishing_gear_crafting' in activities else ('사냥 장비를 만드는', 'making hunting equipment'))
        building = activities & {'construction', 'carpentry_menu_construction', 'metal_welding_construction'}
        woodworking = activities & {'woodworking', 'furniture_crafting'}
        if 'woodworking' in contexts:
            if building and woodworking:
                label = ('목공과 건축에 쓰는', 'woodworking and construction')
            elif building and 'welded_parts' in activities:
                label = ('금속 부품 용접과 건축에 쓰는', 'metal-part welding and construction')
            elif 'metal_welding_construction' in activities:
                label = ('용접 건축에 쓰는', 'welded construction')
            elif building:
                label = ('건축에 쓰는', 'construction')
            elif woodworking:
                label = ('목공에 쓰는', 'woodworking')
            else:
                label = ('금속 부품을 용접하는', 'metal-part welding')
        if contexts == {'electronic_assembly', 'radio_crafting'}:
            results = {r['item_id']: r for u in members for rel in u.get('recipe_targets', []) for r in rel['results']}
            categories = {device_category(r, locale) or (r['names'][locale] if locale == 'ko' else en.object_phrase(r)) for r in results.values()}
            if len(categories) == 1:
                name = next(iter(categories))
                label = (object_name(name) + ' 만드는', 'making ' + name)
        if contexts == {'tool_crafting', 'stone_tool_crafting'} and all(u.get('recipe_targets') for u in members):
            results = {r['item_id']: r for u in members for rel in u['recipe_targets'] for r in rel['results']}
            # These declared results share stone-tool construction; the material
            # item itself need not be stone (cloth can bind the same tools).
            if len(results) == 1:
                result = next(iter(results.values()))
                label = (object_name(result['names']['ko']) + ' 만드는', 'making ' + en.object_phrase(result))
            elif results and results.keys() <= {'Base.FlintKnife', 'Base.AxeStone', 'Base.HammerStone'}:
                label = ('돌 도구를 만드는', 'making stone tools')
        barricades = select({'build_wooden_barricade', 'build_metal_barricade'}) if building else []
        members += barricades
        members += [u for u in units if u not in members and not used & set(u['fact_refs'])
                    and all(f['fact_kind'] == 'use_context' for f in u['facts'])
                    and any(u['branch_refs'] == other['branch_refs'] for other in members)]
        if label is None:
            labels = list(dict.fromkeys(device_category(r, locale) or r['names'][locale]
                         for u in members for rel in u.get('recipe_targets', []) for r in rel['results']))
            if not labels:
                continue
            # Each category states one use; never embed a growing list into
            # another list of unrelated camping, medical or building purposes.
            clauses = [object_name(word) + ' 만들 때 재료로 쓸 수 있다' if locale == 'ko' else
                       'It can be used as material for making ' + word for word in labels]
        else:
            phrase = lex.pair(label, locale)
            clauses = [(phrase.removesuffix('에 쓰는') + ' 재료로 쓸 수 있다' if phrase.endswith('에 쓰는') else phrase + ' 재료로 쓸 수 있다') if locale == 'ko' else 'It can be used as material for ' + phrase]
            if barricades and not compact:
                kind = '금속' if any('build_metal_barricade' in purpose_tokens(u) for u in barricades) else '판자'
                clauses[0] += ('. 문과 창문의 ' + kind + ' 바리케이드에도 재료로 쓸 수 있다') if locale == 'ko' else '. It can also supply window and door barricades'
        if contexts == {'splint_crafting'}:
            purposes = [('craft', lex.pair(('부목', 'splints'), locale))]
        elif contexts == {'spear_crafting', 'trap_crafting', 'fishing_gear_crafting'} and compact:
            purposes = [('craft', lex.pair(pair, locale)) for enabled, pair in (
                (bool(activities & {'spear_crafting', 'trap_crafting'}), ('사냥 장비', 'hunting equipment')),
                ('fishing_gear_crafting' in activities, ('낚시 장비', 'fishing equipment'))) if enabled]
        elif label is None:
            purposes = [('craft', word) for word in labels]
        elif locale == 'ko' and phrase.endswith(' 만드는'):
            noun = phrase.removesuffix(' 만드는')
            noun = noun[:-1] if noun.endswith(('을', '를')) else noun
            purposes = [('craft', noun)]
        elif locale == 'en' and phrase.startswith('making '):
            purposes = [('craft', phrase.removeprefix('making '))]
        else:
            action = ('금속 부품 용접' if phrase == '금속 부품을 용접하는' else phrase.removesuffix('에 쓰는')) if locale == 'ko' else phrase
            purposes = [('action', action)]
            if compact and 'woodworking' in contexts:
                actions = []
                if woodworking:
                    actions.append(lex.pair(('목공', 'woodworking'), locale))
                if 'welded_parts' in activities:
                    actions.append(lex.pair(('금속 부품 용접', 'metal-part welding'), locale))
                if building:
                    actions.append(lex.pair(('건축', 'construction') if building & {'construction', 'carpentry_menu_construction'} else ('용접 건축', 'welded construction'), locale))
                purposes = [('action', action) for action in actions]
        emit_material(members, purposes, '. '.join(clauses))


    for activity, role, wording in (
        ('repair', 'repair_material', ('다른 물품을 수리하는 재료로 쓸 수 있다', 'It can be used to repair items that accept this material')),
        ('blowtorch_refilling', 'fuel', ('토치에 프로판을 보충할 수 있다', 'It can supply propane for refilling blowtorches')),
    ):
        members = [u for u in units if not used & set(u['fact_refs']) and activity in purpose_tokens(u)
                   and any(f['payload'].get('role') == role for f in u['facts'])]
        # A context split from its role shares only that branch's purpose.
        members += [u for u in units if any(f['payload'].get('activity') == activity for f in u['facts'])
                    and all(f['fact_kind'] == 'use_context' for f in u['facts'])
                    and any(u['branch_refs'] == other['branch_refs'] for other in members)]
        if activity == 'repair' and members:
            targets = plan.get('source_traits', {}).get('repair_targets', [])
            labels = []
            for target in targets:
                fields = target.get('declared_traits', {})
                label = (lex.pair(('호환 차량 부품', 'compatible vehicle parts'), locale) if fields.get('DisplayCategory') == 'VehicleMaintenance' else
                         lex.pair(('총기', 'firearms'), locale) if fields.get('Ranged', '').lower() == 'true' else
                         lex.pair(('무기', 'weapons'), locale) if fields.get('Type') == 'Weapon' else
                         lex.pair(('도구', 'tools'), locale) if fields.get('DisplayCategory') == 'Tool' else target['names'][locale])
                if label not in labels:
                    labels.append(label)
            if labels:
                wording = (object_name(parallel_names(labels)) + ' 수리하는 재료로 쓸 수 있다',
                           'It can be used as repair material for ' + parallel_names(labels))
        if activity == 'repair' and members and labels:
            text = lex.pair(wording, locale)
            names = list(dict.fromkeys(t['names'][locale] for t in targets))
            # A firearm family (including its sawn-off form) is one coherent
            # target; mixed tools/weapons/parts need distinct named choices.
            homogeneous = all(t.get('declared_traits', {}).get('Ranged', '').lower() == 'true' for t in targets) or len(names) == 1
            inline = (object_name(parallel_names(names)) + ' 수리할 때 재료로 쓸 수 있다' if locale == 'ko'
                      else 'It can be used as repair material for ' + parallel_names(['the ' + name for name in names]))
            text = detail_text(text, '호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다' if locale == 'ko' else
                               'It can be used as repair material for compatible items from the following list', names,
                               compact=compact, relationship='homogeneous_targets' if homogeneous else 'compatibility_choices', inline=inline)
            before = len(output)
            emit_material(members, [('action', label + ' 수리' if locale == 'ko' else 'repairing ' + label) for label in labels], text)
            if not compact and not homogeneous and len(output) > before:
                output[-1]['target_groups'] = target_groups(targets, locale, text.split('\n', 1)[0])
        else:
            emit(members, lex.pair(wording, locale))

