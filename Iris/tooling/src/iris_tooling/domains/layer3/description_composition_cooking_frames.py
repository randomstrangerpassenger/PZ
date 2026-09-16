"""Cooking purpose frames; selection and consumption stay with the assembly."""
from .description_composition_frame_rules import (
    en,
    ko,
    lex,
    purpose_tokens,
)


def render(state):
    compact = state.compact
    emit = state.emit
    locale = state.locale
    names = state.names
    object_name = state.object_name
    plan = state.plan
    select = state.select
    units = state.units
    used = state.used
    for role, nouns in (('tool', ('도구', 'a tool')),):
        food = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
                and purpose_tokens(u) - {None} == {'food_preparation'}
                and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {role}]
        dough = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
                 and purpose_tokens(u) - {None} <= {'dough_preparation', 'cookie_preparation', 'batter_preparation'}
                 and purpose_tokens(u) & {'dough_preparation', 'cookie_preparation', 'batter_preparation'}
                 and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {role}]
        if food and dough:
            emit(food + dough, '반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다' if locale == 'ko'
                 else 'It can be used as a cooking tool, including for preparing dough',
                 reason='same-role food preparation includes dough preparation; distinct roles and public conditions remain separate')

    cooking_relations = plan.get('source_traits', {}).get('cooking_relations', [])
    additive = [u for u in units if not used & set(u['fact_refs']) and 'food_ingredient_addition' in purpose_tokens(u)
                and any(f['payload'].get('role') == 'base' for f in u['facts'])]
    if additive and cooking_relations:
        rows = {r['fields']['Name']: r for r in cooking_relations}
        drink_rows = [r for r in rows.values() if r['fields'].get('AddIngredientSound') == 'AddItemInBeverage']
        base_rows = [r for r in rows.values() if r['subject_role'] == 'base']
        text = None
        if drink_rows and len(drink_rows) == len(rows):
            poured = [r for r in drink_rows if r['fields']['Name'].startswith('Pour ')]
            mixed = [r for r in drink_rows if r not in poured]
            clauses = []
            if poured:
                # The source action names distinguish pouring beer/wine from
                # adding ingredients to a drink; their generic item labels do not.
                labels = [('맥주', 'beer') if r['fields']['Name'].endswith('Beer') else ('와인', 'wine') for r in poured]
                name = ko.alternatives(list(dict.fromkeys(x[0] for x in labels))) if locale == 'ko' else en.join(list(dict.fromkeys(x[1] for x in labels)))
                if base_rows:
                    clauses.append(object_name(name) + ' 따라 담는 데 쓸 수 있다' if locale == 'ko' else 'It can be used to hold poured ' + name)
                else:
                    clauses.append(object_name(name) + ' 마실 수 있다' if locale == 'ko' else 'It contains ' + name + ' that can be drunk')
            if mixed:
                hot = all(r['fields'].get('Cookable') == 'true' for r in mixed)
                noun = ('따뜻한 음료' if hot else '음료') if locale == 'ko' else ('hot drinks' if hot else 'drinks')
                clauses.append('재료를 더해 ' + object_name(noun) + ' 만들 수 있다' if locale == 'ko' else 'Ingredients can be added to prepare ' + noun)
            text = '. '.join(clauses)
        elif base_rows and (not compact or not any(f['payload'].get('role') == 'container' for u in units for f in u['facts'])):
            # Names here are recipe purposes, never names inferred from the item.
            labels = {
                'Prepare Soup': ('수프', 'soup'), 'Prepare Stew': ('스튜', 'stew'),
                'Make Salad': ('샐러드', 'salad'), 'Make Fruit Salad': ('과일 샐러드', 'fruit salad'),
                'Make Sandwich': ('샌드위치', 'sandwiches'), 'Prepare Burger': ('버거', 'burgers'),
                'Prepare Pie': ('파이', 'pies'), 'Prepare Sweet Pie': ('파이', 'pies'),
                'Prepare Cake': ('케이크', 'cakes'), 'Prepare Stir-fry': ('볶음 요리', 'stir-fries'),
                'Place Ingredients in Roasting Pan': ('구운 채소 요리', 'roasted vegetable dishes'),
                'Prepare Pasta': ('파스타', 'pasta'), 'Prepare Rice': ('쌀 요리', 'rice dishes'),
                'Taco': ('타코', 'tacos'), 'Burrito': ('부리토', 'burritos'),
            }
            if all(r['fields']['Name'] in labels for r in base_rows):
                nouns = list(dict.fromkeys(lex.pair(labels[r['fields']['Name']], locale) for r in base_rows))
                name = ko.alternatives(nouns) if locale == 'ko' else en.join(nouns)
                container = plan.get('source_traits', {}).get('Type') != 'Food'
                text = (('재료를 담아 ' + object_name(name) + ' 만드는 데 쓸 수 있다') if container else ('재료를 더해 ' + object_name(name) + ' 만드는 바탕으로 쓸 수 있다')) if locale == 'ko' else (
                    'It can hold ingredients for making ' + name if container else 'It can serve as a base for making ' + name)
        if text:
            members = list(additive)
            if drink_rows and not base_rows and poured:
                members += select({'drink_food_contents'})
            elif base_rows and not drink_rows and not compact:
                # A named dish refines the same cooking purpose. Preserve other
                # preparation relationships as an open cooking scope, and name
                # the independently confirmed dough-holding role explicitly.
                other = [u for u in units if not used & set(u['fact_refs'])
                         and purpose_tokens(u) - {None} <= {'food_preparation', 'grain_preparation', 'batter_preparation', 'cookie_preparation', 'dough_preparation'}
                         and any(f['payload'].get('role') in {'container', 'base'} for f in u['facts'])]
                if other:
                    members += other
                    if any(purpose_tokens(u) & {'food_preparation', 'grain_preparation'} for u in other):
                        text = (name + ' 등을 만들 때 재료를 담는 데 쓸 수 있다') if locale == 'ko' and container else text.replace('making ' + name, 'making dishes such as ' + name) if locale == 'en' else text
                    if any(purpose_tokens(u) & {'batter_preparation', 'cookie_preparation', 'dough_preparation'} for u in other):
                        text += '. 반죽을 담아 요리를 만드는 데도 쓸 수 있다' if locale == 'ko' else '. It can also hold dough or batter for preparing food'
            emit(members, text)

    cooking = [u for u in units if not used & set(u['fact_refs']) and
               purpose_tokens(u) & {'food_preparation', 'food_ingredient_addition', 'grain_preparation', 'batter_preparation', 'cookie_preparation', 'dough_preparation'}
               and any(f['payload'].get('role') in {'container', 'base'} for f in u['facts'])]
    bowls = select({'receive_portioned_food'})
    is_container = bool(bowls) or any(f['payload'].get('role') == 'container' for u in cooking for f in u['facts'])
    if compact and cooking and is_container:
        activities = set().union(*(purpose_tokens(u) for u in cooking))
        dough = bool(activities & {'batter_preparation', 'cookie_preparation', 'dough_preparation'})
        dough_en = 'dough or batter' if 'batter_preparation' in activities and activities & {'cookie_preparation', 'dough_preparation'} else 'batter' if 'batter_preparation' in activities else 'dough'
        food = bool(activities & {'food_preparation', 'food_ingredient_addition', 'grain_preparation'})
        purpose = ('요리' if food else '반죽 만들기') if locale == 'ko' else (
            'food preparation' if food else dough_en + ' preparation')
        members = list(cooking)
        text = ('재료를 담아 요리할 수 있다' if food else '반죽을 담아 요리를 만드는 데 쓸 수 있다') if locale == 'ko' else ('It can hold ingredients for cooking' if food else 'It can hold ' + dough_en + ' for preparing food')
        if bowls:
            members += bowls + [u for u in units if 'food_portioning' in purpose_tokens(u) and any(f['payload'].get('role') in {'material', 'container'} for f in u['facts'])]
            text = ('요리할 때 재료를 담거나 조리한 음식을 나누어 담는 데 쓸 수 있다' if food else '반죽이나 조리한 음식을 나누어 담는 데 쓸 수 있다') if locale == 'ko' else ('It can be used for ' + purpose + ' and for holding portions of prepared meals')
        emit(members, text)

    if not compact and cooking and is_container:
        food_members = [u for u in cooking if purpose_tokens(u) & {'food_preparation', 'food_ingredient_addition', 'grain_preparation'}]
        if food_members:
            food_members += [u for u in cooking if purpose_tokens(u) & {'batter_preparation', 'cookie_preparation', 'dough_preparation'}
                             and any(f['payload'].get('role') == 'container' for f in u['facts']) and not u['qualifier_refs']]
            additive = any('food_ingredient_addition' in purpose_tokens(u) for u in food_members)
            emit(food_members, ('재료를 더해 요리를 만들 수 있다' if additive else '재료를 담아 요리하는 데 사용할 수 있다') if locale == 'ko'
                 else ('Ingredients can be added to prepare food' if additive else 'It can hold ingredients for cooking'))
        dough_members = [u for u in cooking if not used & set(u['fact_refs']) and purpose_tokens(u) & {'batter_preparation', 'cookie_preparation', 'dough_preparation'}]
        if len(dough_members) > 1:
            has_batter = any('batter_preparation' in purpose_tokens(u) for u in dough_members)
            emit(dough_members, ('반죽을 담아 요리를 만드는 데 쓸 수 있다' if has_batter else '반죽을 담아 요리를 만드는 데 쓸 수 있다') if locale == 'ko'
                 else ('It can hold dough or batter for preparing food' if has_batter else 'It can hold dough for preparing food'))

    food_processing = [u for u in units if not used & set(u['fact_refs'])
        and purpose_tokens(u) - {None} <= {'food_portioning', 'watermelon_breaking'}
        and any(f['payload'].get('role') == 'ingredient' for f in u['facts'])]
    if {'food_portioning', 'watermelon_breaking'} <= set().union(*(purpose_tokens(u) for u in food_processing)):
        emit(food_processing, lex.pair(('자르거나 쪼개어 조각으로 나눌 수 있다', 'It can be sliced or smashed into pieces'), locale))
    for relation in plan.get('use_relations', []):
        if relation['function'] == 'recipe_use' and relation.get('activity') in {'ammunition_disassembly', 'bottle_breaking'} and relation['input_role'] == 'transformation_target':
            members = [u for u in units if set(relation['fact_refs']) & set(u['fact_refs']) and not used & set(u['fact_refs'])]
            result_name = names(relation['results']) if locale == 'ko' else en.join(list(dict.fromkeys(en.object_phrase(r) for r in relation['results'])))
            verb = ('분해해' if relation['activity'] == 'ammunition_disassembly' else '깨뜨려')
            verb_en = ('dismantled' if relation['activity'] == 'ammunition_disassembly' else 'broken')
            emit(members, verb + ' ' + object_name(result_name) + ' 얻을 수 있다' if locale == 'ko'
                 else 'It can be ' + verb_en + ' to obtain ' + result_name)
            continue
        if relation['function'] == 'recipe_use' and relation.get('activity') == 'food_portioning' and relation['input_role'] == 'ingredient':
            members = [u for u in units if set(relation['fact_refs']) & set(u['fact_refs']) and not used & set(u['fact_refs'])]
            primary = [r for r in relation['results'] if r['kind'] == 'declared']
            returned = [r for r in relation['results'] if r['kind'] == 'callback_unconditional']
            if members and primary:
                predicates = {plan['qualifiers'][q]['payload']['predicate'] for u in members for q in u['qualifier_refs']}
                result_name = names(primary) if locale == 'ko' else en.join([en.object_phrase(r) for r in primary])
                text = ('나누어 ' + object_name(result_name) + ' 얻을 수 있다' if locale == 'ko'
                        else 'It can be portioned to obtain ' + result_name)
                if lex.source.BISCUIT_PORTIONING in predicates:
                    text = ('구운 뒤 ' + object_name(result_name) + ' 꺼낼 수 있다' if locale == 'ko' else
                            'Once baked, ' + result_name + ' can be removed from the tray')
                for predicate in (lex.source.COOKED_SLICING, lex.source.DOUGH_SLICING, lex.source.PIZZA_SLICING, lex.source.MUFFIN_PORTIONING, lex.source.BISCUIT_PORTIONING):
                    if predicate in predicates:
                        if predicate == lex.source.BISCUIT_PORTIONING:
                            continue  # Baking is already attached to this use; burnt acceptance is not a separate purpose.
                        condition = {
                            lex.source.COOKED_SLICING: ('익었거나 탄 상태에서 나눌 수 있다', 'It must be cooked or burnt before portioning'),
                            lex.source.DOUGH_SLICING: ('익힌 상태에서 나눌 수 있다', 'It must be cooked before portioning'),
                            lex.source.PIZZA_SLICING: ('완성 피자 형식 외에는 익었거나 탄 상태여야 한다', 'Forms other than ready-made pizza must be cooked or burnt'),
                        }.get(predicate, lex.USE_QUALIFIERS[predicate])
                        text += '. ' + lex.pair(condition, locale)
                if relation['tools'] and not compact:
                    text += '. ' + lex.pair(('맞는 손질 도구가 필요하다', 'A suitable cutting tool is required'), locale)
                elif not compact and lex.source.FOOD_SLICING in predicates:
                    text += '. ' + lex.pair(('해당 음식을 자르는 데 맞는 도구가 필요하다', 'A suitable cutting tool is required'), locale)
                emit(members, text)
                continue
        if relation['function'] == 'recipe_use':
            continue  # Existing callback-specific packaging frames own these uses.
        refs = set(relation['fact_refs'])
        members = [u for u in units if refs & set(u['fact_refs']) and not used & set(u['fact_refs'])]
        if not members:
            continue
        fn = relation['function']
        if fn == 'dismantle_electronics' and any(
            plan['qualifiers'][q]['payload']['predicate'] == lex.source.RADIO_DISMANTLING
            for u in members for q in u['qualifier_refs']):
            continue  # Radio salvage varies by device/skill; the shared frame below owns it.
        activity = 'frog_preparation' if fn == 'prepare_frog_meat' else 'electronic_salvage' if fn == 'dismantle_electronics' else 'package_opening'
        members += [u for u in units if any(f['payload'].get('activity') == activity for f in u['facts'])
                    and any(f['payload'].get('role') in {'material', 'transformation_target'} for f in u['facts'])
                    and not used & set(u['fact_refs'])]
        results = relation['results']
        certain = [r for r in results if r['kind'] != 'callback_conditional']
        possible = [r for r in results if r['kind'] == 'callback_conditional']
        redundant_contents = en.package_identifies_results(plan.get('source_traits', {}).get('display_names', {}).get('en', ''), certain)
        result_name = names(certain) if locale == 'ko' else en.join(list(dict.fromkeys(en.object_phrase(r) for r in certain)))
        tool_groups = [(' 또는 ' if locale == 'ko' else ' or ').join(dict.fromkeys(i['names'][locale] if locale == 'ko' else en.object_phrase(i) for i in group['items'])) for group in relation['tools']]
        tool_text = (' 및 '.join(tool_groups) if locale == 'ko' else ' and '.join(tool_groups))
        if fn == 'prepare_frog_meat':
            tool_text = '칼' if locale == 'ko' else 'a knife'
        if locale == 'ko':
            method = ('' if not tool_text else ko.instrumental(tool_text) + ' ')
            action = '손질해' if fn == 'prepare_frog_meat' else '분해해' if fn == 'dismantle_electronics' else '개봉해'
            text = method + action + ' ' + object_name(result_name) + ' 얻을 수 있다'
            if relation['result_use'] == 'prepare_opened_food_ingredient':
                text = method + action + ' 꺼낸 ' + object_name(result_name) + ' 요리 재료로 쓸 수 있다'
            elif relation['result_use'] == 'sow_extracted_seeds':
                text = '봉지에 든 ' + object_name(result_name) + ' 밭에 심을 수 있다'
            if possible:
                text += '. ' + names(possible) + '도 나올 수 있다'
        else:
            action = 'prepared' if fn == 'prepare_frog_meat' else 'dismantled' if fn == 'dismantle_electronics' else 'opened'
            method = ' with ' + ('a ' if len(relation['tools']) == 1 and len(relation['tools'][0]['items']) == 1 and not tool_text.startswith(('a ', 'an ')) else '') + tool_text if tool_text else ''
            text = 'It can be ' + action + method + ' to obtain ' + result_name
            if relation['result_use'] == 'prepare_opened_food_ingredient':
                text += ' for use as a cooking ingredient'
            elif relation['result_use'] == 'sow_extracted_seeds':
                text = ('The seeds' if redundant_contents else 'The ' + en.join([r['names']['en'].lower() for r in certain])) + ' can be taken out and sown in a planting bed'
            if fn == 'unpack_produce' and redundant_contents:
                text = ('The produce can be taken out and used as cooking ingredients' if relation['result_use'] == 'prepare_opened_food_ingredient'
                        else 'The produce can be taken out of the sack')
            if possible:
                recovered = en.join(list(dict.fromkeys(en.object_phrase(r) for r in possible)))
                text += '. ' + recovered[:1].upper() + recovered[1:] + ' may also be recovered'
        if fn in {'unpack_canned_food', 'unpack_jarred_food', 'unpack_eggs'}:
            edible = select({'eat_food', 'consume_edible_food'})
            consumption = relation.get('result_consumption')
            # Only the known generic consumption condition is abstracted here;
            # an additional result eligibility condition must not disappear.
            result_edible = consumption and {q['payload']['predicate'] for q in consumption['qualifiers']} <= {lex.source.CONSUMING}
            if edible or result_edible:
                drinking = bool(result_edible and consumption['fact']['payload']['function'] == 'drink_food_contents')
                # Elide a result label only when the package already identifies
                # every food word. Unknown/generic packaging retains its result.
                contents = 'the contents' if redundant_contents else 'the ' + en.join([r['names']['en'].lower() for r in certain]) + ' inside'
                opening = (method + action + ' ' + object_name(result_name) +
                           (' 마실 수 있다' if drinking else ' 섭취할 수 있다' if any(r.get('food_type') == 'Juice' for r in certain) else ' 먹을 수 있다') if locale == 'ko' else
                           'It can be opened' + method + (' to drink ' if drinking else ' to consume ' if any(r.get('food_type') == 'Juice' for r in certain) else ' to eat ') + contents)
                cooking = (('꺼낸 ' + object_name(result_name) + ' 요리 재료로도 쓸 수 있다') if locale == 'ko'
                           else ('Its contents can also be used as a cooking ingredient'))
                if compact:
                    text = opening + ('. ' + cooking if relation['result_use'] == 'prepare_opened_food_ingredient' else '')
                    members += edible
                else:
                    emit(members + edible, opening)
                    if relation['result_use'] == 'prepare_opened_food_ingredient':
                        emit(members, cooking)
                    continue
        emit(members, text)

    if any(r['function'] in {'unpack_canned_food', 'unpack_jarred_food'} for r in plan.get('use_relations', [])):
        for unit in units:
            if used & set(unit['fact_refs']) or 'food_preparation' not in purpose_tokens(unit):
                continue
            if not any(f['payload'].get('role') == 'ingredient' for f in unit['facts']):
                continue
            targets = [r for rel in unit.get('recipe_targets', []) for r in rel['results'] if r['kind'] == 'declared']
            if targets and len({r['item_id'] for r in targets}) == 1:
                result_name = names(targets)
                emit([unit], (object_name(result_name) + ' 만드는 재료로 쓸 수 있다') if locale == 'ko'
                     else 'It can be used to make ' + result_name)

    if not compact:
        panic = [u for u in units if not used & set(u['fact_refs']) and all(
            f['payload'].get('property') == 'treatment_panic' for f in u['facts'])]
        medical_functions = {f['payload'].get('function') for u in units for f in u['facts']}
        if panic and medical_functions & {'apply_poultice', 'stitch_wound', 'remove_embedded_glass', 'remove_embedded_bullet'}:
            poultice_only = 'apply_poultice' in medical_functions and not medical_functions & {'stitch_wound', 'remove_embedded_glass', 'remove_embedded_bullet'}
            text = ('혈액공포증이 있는 치료자는 시술 중 공포를 느낄 수 있다' if locale == 'ko'
                    else 'A Hemophobic caregiver can panic during treatment')
            if poultice_only:
                text += ('; 찜질제를 적용하는 부위에 출혈이 있을 때 해당한다' if locale == 'ko'
                         else '; for poultice application, this requires bleeding at the treated part')
            emit(panic, text)

    poisonous = [u for u in units if not used & set(u['fact_refs']) and all(
        f['payload'] == {'property': 'food_sickness', 'direction': 'increase'} for f in u['facts'])
        and any(plan['qualifiers'][q]['payload']['predicate'] == lex.source.POISONOUS_WILD_FOOD for q in u['qualifier_refs'])]
    edible = select({'eat_food', 'consume_edible_food'})
    if poisonous and edible:
        emit(poisonous + edible, '먹을 수 있으며, 독성이 있는 경우 먹으면 식중독을 일으킬 수 있다' if locale == 'ko'
             else 'It can be eaten; poisonous food can cause food sickness when eaten')

    candy = [u for u in units if not used & set(u['fact_refs'])
             and any(f['payload'].get('activity') == 'package_opening' for f in u['facts'])
             and any(plan['qualifiers'][q]['payload']['predicate'] == lex.source.CANDY_OPENING for q in u['qualifier_refs'])]
    if candy:
        emit(candy, '포장을 열어 사탕을 꺼낼 수 있다' if locale == 'ko'
             else 'The package can be opened to retrieve candy')

    bowl_receivers = select({'receive_portioned_food'})
    if bowl_receivers:
        portion_materials = [u for u in units if not used & set(u['fact_refs'])
            and any(f['payload'].get('activity') == 'food_portioning' for f in u['facts'])
            and any(f['payload'].get('role') in {'material', 'container'} for f in u['facts'])]
        emit(bowl_receivers + portion_materials,
             '조리한 냄비 음식을 나누어 담을 수 있다' if locale == 'ko'
             else 'It can be used to divide prepared pot meals into portions')

