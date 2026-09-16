"""Supplies purpose frames; selection and consumption stay with the assembly."""
from .description_composition_frame_rules import (
    FUEL,
    TINDER,
    en,
    lex,
    purpose_tokens,
)


def render(state, *, compact_recovery, rope_uses):
    compact = state.compact
    emit = state.emit
    emit_material = state.emit_material
    locale = state.locale
    object_name = state.object_name
    plan = state.plan
    select = state.select
    units = state.units
    used = state.used
    # Supply roles are purposes; a different fireplace menu is not a new use.
    # Give grounded examples, not an exhaustive facility/eligibility table.
    fuel, tinder = select(FUEL), select(TINDER)
    fuel_fns = {f['payload']['function'] for u in fuel for f in u['facts']}
    tinder_fns = {f['payload']['function'] for u in tinder for f in u['facts']}
    shared_fire = ('supply_campfire_fuel' in fuel_fns and 'provide_campfire_tinder' in tinder_fns) or (
        'supply_hearth_fuel' in fuel_fns and 'provide_hearth_tinder' in tinder_fns)
    if fuel and tinder and shared_fire:
        example = ('모닥불', 'campfires') if 'supply_campfire_fuel' in fuel_fns and 'provide_campfire_tinder' in tinder_fns else ('벽난로', 'fireplaces')
        text = lex.pair((example[0] + ' 등의 연료나 불쏘시개로 쓸 수 있다',
                         'It can be used as fuel or tinder, for example in ' + example[1]), locale)
        if 'supply_furnace_fuel' in fuel_fns:
            text += lex.pair(('. 화로에는 연료로 쓸 수 있다', '. It can also fuel furnaces'), locale)
        emit(fuel + tinder, text)
    else:
        if fuel:
            if 'supply_campfire_fuel' in fuel_fns:
                target = ('모닥불이나 화로 등' if 'supply_furnace_fuel' in fuel_fns else '모닥불 등') if len(fuel_fns) > 1 else '모닥불'
                target_en = 'campfires and furnaces, for example' if 'supply_furnace_fuel' in fuel_fns else 'campfires, for example' if len(fuel_fns) > 1 else 'campfires'
            else:
                target, target_en = ('화로', 'furnaces') if fuel_fns == {'supply_furnace_fuel'} else ('벽난로 등', 'fireplaces, for example')
            emit(fuel, target + '의 연료로 쓸 수 있다' if locale == 'ko' else 'It can be used as fuel for ' + target_en)
        if tinder:
            only_drum = tinder_fns == {'provide_industrial_tinder'}
            target, target_en = ('금속 드럼', 'metal drums') if only_drum else ('모닥불 등', 'campfires, for example') if 'provide_campfire_tinder' in tinder_fns else ('벽난로 등', 'fireplaces, for example')
            emit(tinder, target + '의 불쏘시개로 쓸 수 있다' if locale == 'ko' else 'It can be used as tinder for ' + target_en)
    wearing = select({'wear_on_body', 'wear_configured_clothing'})
    locations = [u for u in units if not set(u['fact_refs']) & used and any(f['payload'].get('state') == 'worn_location' for f in u['facts'])]
    if wearing:
        location = None
        if locations:
            name = lex.pair(lex.source.BODY_LABELS[locations[0]['facts'][0]['payload']['value']], locale)
            location = lex.wearing(locations[0]['facts'][0]['payload']['value'], locale)
        emit(wearing + locations, (location if location else ('몸에 착용할 수 있다' if locale == 'ko' else 'It can be worn')))
    fabric = [u for u in units if not set(u['fact_refs']) & used and any(f['payload'].get('activity') == 'fabric_recovery' for f in u['facts'])]
    if fabric and any(f['payload'].get('role') == 'material' for u in fabric for f in u['facts']):
        fabric_type = plan.get('source_traits', {}).get('FabricType')
        needs_scissors = fabric_type in {'Denim', 'Leather'}
        # The recovered material is the use; dirt/quality variants are outcomes
        # of that same recovery, not additional L3 purposes.
        recovered = compact_recovery
        text = (('가위로 잘라 ' if needs_scissors else '찢어서 ') + object_name(recovered) + ' 얻을 수 있다') if locale == 'ko' else (
            ('It can be cut with scissors' if needs_scissors else 'It can be ripped') + ' to obtain ' + recovered)
        emit(fabric, text)
    rope_materials = [u for u in rope_uses if not used & set(u['fact_refs'])]
    if rope_materials:
        emit(rope_materials, '시트 로프를 만들 때 재료로 쓸 수 있다' if locale == 'ko'
             else 'It can be used' + ' as material for making sheet rope')
    friction = select({'light_campfire_by_friction', 'kindle_heat_sources'})
    if len(friction) == 2:
        text = ('나무를 비벼 불을 피우는 데 쓸 수 있다' if locale == 'ko' else
                'It can be used to attempt lighting fires by wood friction') if compact else (
                '나무를 비벼 모닥불 등에 불을 피우는 데 쓸 수 있다' if locale == 'ko' else
                'It can be used to light fires by wood friction, for example in campfires')
        emit(friction, text)
    plumbing = select({'plumb_external_water'})
    if plumbing:
        emit(plumbing, '실내 설비가 외부 수원을 쓰도록 배관을 연결하는 데 쓸 수 있다' if locale == 'ko' else
             'It can be used to plumb indoor fixtures that accept an external water source')

    # Named ignition branches retain method/target compatibility without the
    # movement, inventory, repeated validity and per-action use-count prose.
    from .description_composition_families import IGNITION, IGNITION_TARGETS
    corpses = select({'request_corpse_burning'})
    emit(corpses, lex.pair(('시신을 태우는 데 쓸 수 있다', 'It can be used to burn corpses'), locale))
    ignition = select(set(IGNITION))
    candle_tools = [u for u in units if any(f['payload'].get('activity') == 'candle_lighting' for f in u['facts'])
                    and any(f['payload'].get('role') == 'tool' for f in u['facts'])]
    is_igniter = any(f['payload'].get('function') == 'light_campfire' for member in ignition for f in member['facts'])
    if compact and ignition and is_igniter:
        emit(ignition + candle_tools, ('불을 붙이는 데 사용할 수 있다' if candle_tools else '불을 붙이는 데 쓸 수 있다') if locale == 'ko'
             else ('It can be used to light fires' if candle_tools else 'It can be used for lighting fires'))
    elif ignition:
        target_methods = {}
        for u in ignition:
            fn = u['facts'][0]['payload']['function']
            if fn == 'request_corpse_burning':
                targets, methods = ('corpse',), ('petrol',)
            else:
                _, targets, methods = IGNITION[fn]
            for target in targets:
                entry = target_methods.setdefault(target, (set(), []))
                entry[0].update(methods)
                entry[1].append(u)
        grouped = {}
        for target, (methods, members) in target_methods.items():
            entry = grouped.setdefault(tuple(sorted(methods)), ([], []))
            entry[0].append(target)
            entry[1].extend(u for u in members if u not in entry[1])
        is_igniter = any(f['payload'].get('function') == 'light_campfire' for member in ignition for f in member['facts'])
        clauses = []
        for methods, (targets, members) in grouped.items():
            target_names = [lex.pair(('시신', 'corpses') if t == 'corpse' else IGNITION_TARGETS[t], locale) for t in targets]
            if locale == 'ko':
                method = ' 또는 '.join('휘발유' if m == 'petrol' else '불쏘시개' for m in methods)
                clauses.append('·'.join(target_names) + '에 ' + method + '로 불을 붙이는 데 사용할 수 있다' if is_igniter
                               else '점화 도구와 함께 ' + '·'.join(target_names) + '에 불을 붙이는 연료로 사용할 수 있다')
            else:
                clauses.append('It can be used as an igniter for lighting ' + en.join(target_names) + ' with ' + ' or '.join(methods) if is_igniter
                               else 'It can supply petrol for lighting ' + en.join(target_names) + ' with an igniter')
        if is_igniter:
            emit(ignition + candle_tools, '불을 붙이는 데 사용할 수 있다' if locale == 'ko' else 'It can be used to light fires')
        else:
            example = '모닥불 등' if 'campfire' in target_methods else '벽난로 등' if 'fireplace' in target_methods else '시신' if set(target_methods) == {'corpse'} else '화로 등'
            example_en = 'campfires, for example' if 'campfire' in target_methods else 'fireplaces, for example' if 'fireplace' in target_methods else 'corpses' if set(target_methods) == {'corpse'} else 'furnaces, for example'
            emit(ignition, example + '에 불을 붙이는 연료로 쓸 수 있다' if locale == 'ko' else 'It can supply petrol for lighting ' + example_en)
        if candle_tools and not is_igniter:
            emit(candle_tools, '초에 불을 붙이는 데 사용할 수 있다' if locale == 'ko' else 'It can be used to light candles')
    # A result subtype or a second native entry point does not create a new
    # purpose. Keep independent roles and unchanged public conditions apart.
    dough = {'batter_preparation', 'cookie_preparation', 'dough_preparation'}
    # A grain input's preparation recipe supplies a cooking ingredient, not
    # a separate purpose named after the input. Vessel roles stay distinct.
    grain_ingredients = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
        and purpose_tokens(u) - {None} == {'grain_preparation'}
        and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'ingredient'}]
    emit(grain_ingredients, '요리 재료로 쓸 수 있다' if locale == 'ko' else 'It can be used as a cooking ingredient')
    # Preparing dough is included in a cooking-ingredient purpose for the same
    # item and role. Distinguishing input conditions and other roles stay apart.
    cooking_ingredients = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
        and purpose_tokens(u) - {None} == {'food_preparation'}
        and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'ingredient'}]
    included_dough = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
        and purpose_tokens(u) - {None} <= dough and purpose_tokens(u) & dough
        and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'ingredient'}]
    if cooking_ingredients:
        emit(cooking_ingredients + included_dough, '요리 재료로 쓸 수 있다' if locale == 'ko'
             else 'It can be used as a cooking ingredient',
             reason='same-item ingredient role: cooking includes dough preparation; all admitted references retained')
    for role in ('tool', 'ingredient', 'container'):
        members = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
                   and purpose_tokens(u) - {None} <= dough and purpose_tokens(u) & dough
                   and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {role}]
        if members:
            noun = {'tool': ('도구', 'a tool'), 'ingredient': ('재료', 'an ingredient'), 'container': ('용기', 'a container')}[role]
            activities = set().union(*(purpose_tokens(u) for u in members))
            preparation = 'dough and batter' if 'batter_preparation' in activities and activities & {'cookie_preparation', 'dough_preparation'} else 'batter' if 'batter_preparation' in activities else 'dough'
            emit(members, ('반죽을 만드는 재료로 쓸 수 있다' if role == 'ingredient' else '반죽을 만드는 데 사용할 수 있다' if role == 'tool' else '반죽을 담아 요리를 만드는 데 쓸 수 있다') if locale == 'ko'
                 else ('It can hold ' + preparation + ' for preparing food' if role == 'container' else 'It can be used as ' + noun[1] + ' for preparing ' + preparation))
    transfer = select({'pour_water_into_container', 'supply_world_water_storage'})
    if not compact and len(transfer) > 1:
        emit(transfer, '다른 물 용기나 물 저장 시설에 물을 옮길 수 있다' if locale == 'ko'
             else 'It can transfer water to other water containers or water storage fixtures')
    washing = select({'wash_bandaging_material'})
    if washing:
        matching = [u for u in units if not used & set(u['fact_refs'])
                    and 'bandaging_material_preparation' in purpose_tokens(u)
                    and any(r.get('activity') == 'bandaging_material_preparation' for r in u['recipe_targets'])]
        emit(washing + matching, '물로 씻어 다시 쓸 수 있다' if locale == 'ko'
             else 'It can be washed with water for reuse')
    log_members = [u for u in units if not used & set(u['fact_refs']) and 'log_binding' in purpose_tokens(u)]
    unbundle = select({'unbundle_logs'})
    if log_members or unbundle:
        emit(log_members + unbundle, ('묶음을 풀면 통나무와 묶을 때 쓴 재료를 돌려받을 수 있다' if unbundle else '모아서 묶을 수 있다' if select({'supply_drum_logs'}) else '통나무를 묶는 데 쓸 수 있다')
             if locale == 'ko' else ('It can be unbundled to recover logs and binding materials' if unbundle
                                      else 'It can be bundled with other logs' if select({'supply_drum_logs'}) else 'It can be used to bind logs'))
    light = select({'control_portable_light'})
    if compact:
        charcoal = select({'supply_drum_logs'})
        emit_material(charcoal, [('craft', lex.pair(('숯', 'charcoal'), locale))], lex.pair(('숯을 만드는 재료로 쓸 수 있다', 'It can supply material for making charcoal'), locale))
    own_lighting = select({'light_candle'})
    if light and own_lighting:
        targets = [u for u in units if not used & set(u['fact_refs'])
                   and any(f['payload'].get('activity') == 'candle_lighting' for f in u['facts'])
                   and any(f['payload'].get('role') == 'transformation_target' for f in u['facts'])]
        emit(light + own_lighting + targets, '발화 도구로 불을 붙여 휴대 조명으로 쓸 수 있다' if locale == 'ko'
             else 'It can be lit with a fire-starting item for use as a portable light')
    elif light:
        emit(light, '휴대 조명으로 쓸 수 있다' if locale == 'ko' else 'It can be used as a portable light')
