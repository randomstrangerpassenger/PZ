"""Ordered frame assembly and public compatibility helpers."""
from .description_composition_frame_rules import (
    deepcopy,
    re,
    lex,
    en,
    ko,
    FORGING_ACTIVITIES,
    MAINTENANCE,
    WASH_RESULTS,
    FUEL,
    TINDER,
    PURPOSE_NEIGHBORS,
    purpose_tokens,
    adjacent,
    SELF_FUNCTIONS,
    INTERNAL_PROPERTIES,
    SUPPORTING_PROPERTIES,
    INTERNAL_STATES,
    CONSTRUCTION_PREDICATES,
    TOOL_DETAIL_PREDICATES,
    device_category,
    activity_labels,
    tool_purposes,
    disposition,
    internal_reason,
    target_groups,
    grouped_detail,
    learning_groups,
    scoped_groups,
    detail_text,
)
from .description_composition_frame_state import FrameAssembly
from . import description_composition_crafting_frames as crafting_frames
from . import description_composition_cooking_frames as cooking_frames
from . import description_composition_media_frames as media_frames
from . import description_composition_medical_frames as medical_frames
from . import description_composition_supplies_frames as supplies_frames


def frames(plan, locale, links, compact):
    output, used = [], set()
    material_frames = []
    units = plan['units']
    from . import description_composition_families as families

    def select(functions):
        return [u for u in units if any(f['payload'].get('function') in functions for f in u['facts'])
                and not set(u['fact_refs']) & used]

    def emit(members, text, ordered=False, reason='role and confirmed result use; execution evidence retained internally', accepted_predicates=()):
        if not members:
            return
        allowed = set(accepted_predicates)
        if any(f['payload'].get('role') == 'tool' for u in members for f in u['facts']):
            allowed.update(TOOL_DETAIL_PREDICATES)
        by_function = {
            'toggle_radio_microphone': {'MIC_CONTROL'},
            'provide_equipped_rain_protection': {'EQUIPPED_RAIN_USE'},
            'reduce_foraging_rain_effect': {'EQUIPPED_RAIN_USE'},
            'place_fishing_net': {'NET_PLACEMENT'},
            'check_fishing_net': {'NET_CHECKING'},
            'remove_fishing_net': {'NET_REMOVAL'},
            'view_item_map': {'MAP_READING'},
            'reveal_item_map_area': {'MAP_REVEAL'},
            'annotate_item_map': {'MAP_ANNOTATION'},
            'erase_item_map_annotations': {'MAP_ERASURE'},
            'place_moveable_furniture': {'PLACEMENT'},
            'install_combination_padlock': {'CODE_LOCK_USE'},
            'remove_combination_padlock': {'CODE_UNLOCK'},
            'exercise_barbell_curl': {'WEIGHT_EXERCISE'},
            'exercise_dumbbell_press': {'WEIGHT_EXERCISE'},
            'exercise_biceps_curl': {'WEIGHT_EXERCISE'},
            'remove_placed_furniture': {'PICKUP', 'PICKUP_LOSS'},
            'supply_escape_rope': {'ESCAPE_ROPE_INSTALL'},
            'remove_installed_escape_rope': {'ESCAPE_ROPE_REMOVE'},
            'start_escape_rope_ascent': {'ESCAPE_ROPE_CLIMB'},
            'remove_embedded_glass': {'GLASS_REMOVAL'},
            'remove_embedded_bullet': {'BULLET_REMOVAL'},
            'clean_burn': {'BURN_CLEANING'},
            'unpick_garment_patch': {'GARMENT_PATCH_REMOVAL'},
            'pitch_tent': {'CAMP_PLACEMENT', 'TENT_PLACEMENT'},
            'rest_at_placed_tent': {'TENT_REST'},
            'light_candle': {'CANDLE_LIGHT_RECIPE'},
            'receive_portioned_food': {'BOWL_PORTIONING'},
            'set_alarm': {'ALARM_SETTING'},
            'stop_alarm': {'ALARM_STOPPING'},
            'salvage_vehicle_engine': {'ENGINE_SALVAGE'},
            'control_device_media': {'RADIO_MEDIA_CONTROL'},
            'insert_recorded_media': {'MEDIA_INSERT'},
            'tune_radio': {'RADIO_TUNING'},
            'select_tv_channel': {'TV_TUNING'},
            'write_note_pages': {'NOTE_IMPLEMENT'},
            'record_written_notes': {'NOTE_EDIT'},
            'annotate_map': {'MAP_ANNOTATION'},
            'wash_body': {'BODY_WASHING', 'WASHING_OUTCOME'},
            'wash_equipment': {'EQUIPMENT_WASHING', 'WASHING_OUTCOME'},
            'supply_campfire_fuel': {'CAMP_FUEL_USE'},
            'supply_hearth_fuel': {'HEARTH_FUEL'},
            'supply_furnace_fuel': {'FURNACE_FUEL'},
            'provide_campfire_tinder': {'CAMP_TINDER_USE'},
            'provide_hearth_tinder': {'HEARTH_TINDER'},
            'provide_industrial_tinder': {'INDUSTRIAL_TINDER'},
            'supply_drum_logs': {'DRUM_LOGS'},
            'wear_on_body': {'WEARING', 'WEAR_ACTION'},
            'wear_configured_clothing': {'WEARING', 'WEAR_ACTION'},
            'prepare_frog_meat': {'FROG_PREPARATION'},
            'unpack_ammunition': {'OPENING'},
            'unpack_canned_food': {'OPENING', 'CAN_OPENING'},
            'unpack_jarred_food': {'OPENING'},
            'unpack_box_contents': {'OPENING'},
            'unpack_produce': {'PRODUCE_SACK_OPENING', 'OPENING'},
            'unpack_seeds': {'OPENING', 'SEED_EXTRACTION'},
            'unpack_eggs': {'OPENING', 'EGG_CARTON_OPENING'},
            'dismantle_electronics': {'ELECTRONIC_SALVAGE', 'SCRAP_RECOVERY', 'RADIO_DISMANTLING'},
            'prepare_opened_food_ingredient': {'OPENED_FOOD', 'COOKING_ACTION'},
            'sow_extracted_seeds': {'SOWING', 'SEED_EXTRACTION'},
            'supply_trap_bait': {'FOOD_TRAP_BAIT'},
            'kindle_heat_sources': {'HEAT_FRICTION'},
            'light_campfire_by_friction': {'CAMP_FRICTION'},
            'plumb_external_water': {'PLUMBING'},
            'anchor_escape_rope': {'ESCAPE_ROPE_INSTALL'},
            'pack_into_box': {'BOX_PACKING'},
            'portion_into_bowls': {'BOWL_PORTIONING'},
            'build_wooden_barricade': {'WOOD_BARRICADE'},
            'remove_barricade': {'WOOD_UNBARRICADE'},
            'store_water': {'WATER_STORAGE'},
            'carry_water': {'WATER_STORAGE'},
            'receive_poured_water': {'WATER_TRANSFER'},
            'pour_water_into_container': {'WATER_TRANSFER'},
            'supply_world_water_storage': {'WORLD_WATER_TRANSFER'},
            'wash_bandaging_material': {'BANDAGE_WASHING'},
            'attach_weapon_part': {'WEAPON_ATTACHMENT'},
            'remove_weapon_part': {'WEAPON_PART_REMOVAL'},
            'insert_matching_magazine': {'MAGAZINE_LOADING'},
            'fill_magazine': {'MAGAZINE_FILL'},
            'convert_lamp_to_battery': {'LAMP_CONVERSION'},
            'repair_generator': {'GENERATOR_REPAIR'},
        }
        for u in members:
            for f in u['facts']:
                fn = f['payload'].get('function')
                allowed.update(families.FRAME_PREDICATES.get(fn, set()))
                if fn in {'store_vehicle_fuel', 'supply_vehicle_engine_fuel', 'transfer_vehicle_fuel'}:
                    allowed.update(families.FRAME_PREDICATES['vehicle_fuel'])
                if fn and fn.startswith('install_vehicle_'):
                    allowed.update(families.FRAME_PREDICATES['vehicle_exchange'])
                if fn == 'sow_extracted_seeds':
                    allowed.update(families.FRAME_PREDICATES['sowing'])
                if fn == 'read_literature' or f['payload'].get('direction') == 'cap_at_reading_start':
                    allowed.update(families.FRAME_PREDICATES['reading_mood'])
                if fn in families.IGNITION or fn == 'request_corpse_burning':
                    allowed.update(families.FRAME_PREDICATES['ignition'])
                if f['payload'].get('activity') == 'item_packaging':
                    allowed.add(lex.source.EGG_PACKING)
                if f['payload'].get('activity') == 'repair' or (u.get('context') or {}).get('activity') == 'repair':
                    allowed.update({lex.source.FIXING_ACTION,
                        'For a compatible damaged item and available repair materials; repair eligibility and outcome depend on the fixing rules.'})
                if f['payload'].get('activity') == 'blowtorch_refilling' or (u.get('context') or {}).get('activity') == 'blowtorch_refilling':
                    allowed.add(lex.source.TORCH_REFILL_RECIPE)
                if f['payload'].get('activity') == 'candle_lighting':
                    allowed.add(lex.source.CANDLE_LIGHT_RECIPE)
                if f['payload'].get('activity') == 'food_portioning':
                    allowed.update({lex.source.BOWL_PORTIONING, lex.source.FOOD_SLICING, lex.source.COOKED_SLICING, lex.source.DOUGH_SLICING, lex.source.PIZZA_SLICING, lex.source.MUFFIN_PORTIONING, lex.source.BISCUIT_PORTIONING})
                if f['payload'].get('activity') in {'ammunition_disassembly', 'bottle_breaking'}:
                    allowed.add(lex.source.SIMPLE_TRANSFORMATION)
                if f['payload'].get('activity') == 'package_opening':
                    allowed.update({lex.source.OPENING, lex.source.CAN_OPENING, lex.source.CANDY_OPENING})
                if f['payload'].get('activity') in {'electronic_salvage', 'radio_salvage'}:
                    allowed.update({lex.source.ELECTRONIC_SALVAGE, lex.source.SCRAP_RECOVERY, lex.source.RADIO_DISMANTLING})
                allowed.update(getattr(lex.source, n) for n in by_function.get(fn, set()))
                if f['payload'].get('activity') == 'metal_welding_construction':
                    allowed.add(lex.source.WELDING_CONSTRUCTION)
                if f['payload'].get('activity') == 'welded_parts':
                    allowed.add(lex.source.WELDED_PARTS)
                if f['payload'].get('activity') in {'construction', 'carpentry_menu_construction'} or (u.get('context') or {}).get('activity') in {'construction', 'carpentry_menu_construction'}:
                    allowed.update(CONSTRUCTION_PREDICATES)
                if f['payload'].get('activity') == 'fabric_recovery':
                    allowed.update({lex.source.FABRIC_ACTION, 'An eligible fabric or named sheet is supplied to the recipe; recovered material and quantity depend on fabric, covered parts, dirt/blood and tailoring state.'})
                if 'moving_furniture' in purpose_tokens(u):
                    allowed.add('The object requests this tool; inventory, reachability, world object and multiplayer permission checks must hold.')
                if f['payload'].get('activity') == 'spear_upgrade' or (u.get('context') or {}).get('activity') == 'spear_upgrade':
                    allowed.add(lex.source.SPEAR_CONDITIONS['spear_upgrade'])
                if f['payload'].get('activity') == 'sheet_rope_making':
                    allowed.add(lex.source.ROPE_MAKING)
                if f['payload'].get('activity') == 'food_preparation':
                    allowed.update({lex.source.BEAN_PREPARATION, lex.source.OATMEAL_PREPARATION, lex.source.OMELETTE_PREPARATION})
                if f['payload'].get('state') == 'worn_location':
                    allowed.update({families.WEARING, lex.source.WEARING, lex.source.WEAR_ACTION})
                if f['payload'].get('property') in {'burn_wash_requirement', 'additional_pain'}:
                    allowed.add(lex.source.BURN_CLEANING)
                if f['payload'].get('property') == 'bandage_patient_infection':
                    allowed.add(lex.source.BANDAGE_INFECTION)
                if f['payload'].get('property') == 'food_sickness':
                    allowed.add(lex.source.POISONOUS_WILD_FOOD)
                if f['payload'].get('property') == 'installed_tire_air_or_attachment':
                    allowed.add(lex.source.TIRE_WEAR)
                if f['payload'].get('property') == 'treatment_panic':
                    allowed.add(lex.source.MEDICAL_PANIC)
                if f['payload'].get('property') == 'delivered_media_code_outcome':
                    allowed.add(lex.source.RADIO_CODE_EFFECTS)
                if f['payload'].get('property') == 'reload_speed_setting':
                    allowed.update(lex.RELOAD_SCOPES)
        predicates = {plan['qualifiers'][q]['payload']['predicate'] for u in members for q in u['qualifier_refs']}
        if not predicates <= allowed:
            return
        # These frames express the admitted capability and selected structured
        # relationships, not the complete execution predicate.
        claims = [dict(u, qualifier_refs=[]) for u in (members if ordered else adjacent(members, purpose_tokens))]
        output.append({'text': text if '\n- ' in text else text + '.', **links(claims, plan), 'expression': 'public_use',
                       'placement_reason': reason,
                       'qualifier_dispositions': []})
        used.update(r for u in members for r in u['fact_refs'])

    def emit_material(members, purposes, text):
        before = len(output)
        emit(members, text)
        if len(output) > before and (compact or all(kind == 'craft' for kind, _ in purposes)):
            material_frames.append((output[-1], members, purposes))

    def parallel_names(values):
        values = list(dict.fromkeys(values))
        if locale != 'ko':
            return en.join(values)
        if len(values) < 2:
            return ''.join(values)
        return ', '.join(values[:-1]) + ' 및 ' + values[-1]

    def names(items):
        words = list(dict.fromkeys(i['names'][locale] for i in items))
        return '·'.join(words) if locale == 'ko' else en.join(words)

    def object_name(noun):
        return ko.object_name(noun)

    functions = {f['payload'].get('function') for u in units for f in u['facts']}
    assembly = FrameAssembly(plan, locale, links, compact, units, used, output, material_frames, functions, select, emit, emit_material, parallel_names, names, object_name)
    for unit in units:
        relations = unit.get('recipe_targets', [])
        if relations and len({r['item_id'] for rel in relations for r in rel['results']}) == 1 and all(r.get('processing_role') == 'weapon_modification_target' for r in relations):
            targets = list(dict.fromkeys(r['names'][locale] for rel in relations for r in rel['results']))
            name = '이나 '.join(targets) if locale == 'ko' else en.join([n.lower() for n in targets])
            emit([unit], name + ' 형태로 개조할 수 있다' if locale == 'ko' else 'It can be modified into ' + en.article(name))
    forms = select({'switch_declared_clothing_form'})
    options = set(plan.get('source_traits', {}).get('ClothingItemExtraOption', '').split(';'))
    form_actions = []
    for identifiers, phrase in (
        ({'UpHoodie'}, ('후드를 쓸 수 있다', 'Its hood can be raised')),
        ({'DownHoodie'}, ('후드를 벗을 수 있다', 'Its hood can be lowered')),
        ({'ReverseCap'}, ('뒤로 돌려 쓸 수 있다', 'It can be worn with the brim facing backwards')),
        ({'ForwardCap'}, ('앞으로 돌려 쓸 수 있다', 'It can be worn with the brim facing forwards')),
        ({'FannyPack_WearFront'}, ('몸 앞으로 돌려 찰 수 있다', 'It can be worn at the front')),
        ({'FannyPack_WearBack'}, ('몸 뒤로 돌려 찰 수 있다', 'It can be worn at the back')),
        ({'EyeRight'}, ('오른쪽 눈으로 옮겨 달 수 있다', 'It can be worn over the right eye')),
        ({'EyeLeft'}, ('왼쪽 눈으로 옮겨 달 수 있다', 'It can be worn over the left eye')),
        ({'TieBandana'}, ('묶어 머리에 쓸 수 있다', 'It can be tied around the head')),
        ({'UntieBandana'}, ('매듭을 풀 수 있다', 'The bandana can be untied')),
        ({'TieBandanaFace'}, ('얼굴을 덮을 수 있다', 'It can be worn over the face')),
        ({'PutOnEarlobe'}, ('귓불로 옮겨 달 수 있다', 'It can be worn on the earlobe')),
        ({'PutOnEartop'}, ('귀 위쪽으로 옮겨 달 수 있다', 'It can be worn on the upper ear')),
        ({'LeftWrist'}, ('왼쪽 손목으로 옮겨 찰 수 있다', 'It can be worn on the left wrist')),
        ({'RightWrist'}, ('오른쪽 손목으로 옮겨 찰 수 있다', 'It can be worn on the right wrist')),
        ({'LeftMiddleFinger', 'LeftRingFinger', 'RightMiddleFinger', 'RightRingFinger'}, ('다른 손가락으로 옮겨 낄 수 있다', 'It can be moved to another finger')),
    ):
        if options & identifiers:
            form_actions.append(lex.pair(phrase, locale))
    form_text = '. '.join(form_actions)
    fabric_wear = bool(functions & {'wear_on_body', 'wear_configured_clothing'}) and plan.get('source_traits', {}).get('FabricType') in {'Cotton', 'Denim', 'Leather'}
    traits = plan.get('source_traits', {})
    current_location = traits.get('BodyLocation') or traits.get('CanBeEquipped')
    locations = {r['location'] for r in traits.get('wearing_alternatives', [])} | {current_location}
    combined_wearing = None
    if locations == {'Hat', 'Mask'}:
        combined_wearing = ('머리에 쓰거나 얼굴을 가리는 형태로 바꿔 쓸 수 있다', 'It can be worn on the head or changed to cover the face')
    elif locations == {'LeftWrist', 'RightWrist'}:
        combined_wearing = ('왼쪽이나 오른쪽 손목에 골라 찰 수 있다', 'It can be worn on either wrist')
    elif locations == {'LeftEye', 'RightEye'}:
        combined_wearing = ('왼쪽이나 오른쪽 눈에 골라 달 수 있다', 'It can be worn over either eye')
    elif locations == {'FannyPackFront', 'FannyPackBack'}:
        combined_wearing = ('몸 앞이나 뒤로 위치를 바꿔 찰 수 있다', 'It can be worn at the front or back')
    elif compact and locations == {'Left_MiddleFinger', 'Left_RingFinger', 'Right_MiddleFinger', 'Right_RingFinger'}:
        combined_wearing = ('양손의 중지나 약지에 골라 낄 수 있다', 'It can be worn on either middle or ring finger')
    time_display = select({'check_carried_time'})
    if time_display and combined_wearing and locations == {'LeftWrist', 'RightWrist'}:
        combined_wearing = ('왼쪽이나 오른쪽 손목에 차거나 소지해 시간을 확인할 수 있다', 'It can be worn on either wrist or carried to check the time')
    if forms and combined_wearing:
        places = [u for u in units if not used & set(u['fact_refs']) and all(f['payload'].get('state') == 'worn_location' for f in u['facts'])]
        emit(forms + select({'wear_on_body', 'wear_configured_clothing'}) + places + time_display, lex.pair(combined_wearing, locale))
        forms = []
    emit(select({'check_carried_time'}), lex.pair(('소지해 시간을 확인할 수 있다', 'It can be carried to check the time'), locale))
    if forms and form_actions and not (compact and fabric_wear and functions & (FUEL.keys() | TINDER.keys())):
        emit(forms, form_text)
    if plan.get('source_traits', {}).get('FoodType') == 'Juice':
        emit(select({'eat_food', 'consume_edible_food'}), lex.pair(('섭취할 수 있다', 'It can be consumed'), locale))
    cleaning = select({'clean_world_blood'})
    cleaning_role = traits.get('blood_cleaning_role')
    if cleaning and cleaning_role and not compact:
        text = (('수건이나 청소 도구와 함께 바닥 혈흔을 지우는 세척 재료로 쓸 수 있다',
                 'It can be used with a towel or cleaning tool to remove bloodstains from floors') if cleaning_role == 'cleaning_supply' else
                ('표백제와 함께 바닥 혈흔을 닦는 도구로 쓸 수 있다',
                 'It can be used with bleach to wipe bloodstains from floors'))
        emit(cleaning, lex.pair(text, locale))
    mechanics = select({'learn_literature_mechanics'})
    learning_targets = traits.get('mechanic_learning_targets', [])
    if mechanics and learning_targets and not compact:
        noun = ko.alternatives([x['ko'] for x in learning_targets]) if locale == 'ko' else en.join([x['en'] for x in learning_targets])
        emit(mechanics + select({'read_literature'}), noun + '의 정비 방법을 읽어서 배울 수 있다' if locale == 'ko' else 'It can be read to learn maintenance procedures for ' + noun)
    lessons = select({fn for fn in functions if fn and fn.startswith('learn_literature_')})
    if lessons:
        learned = plan.get('source_traits', {}).get('learned_recipes', [])
        recipes = {r['key']: r for entry in learned for r in entry['recipes']}
        if recipes:
            overviews = []
            fields = {'engineer': ('장치', 'devices'), 'electrical': ('전자 장치', 'electronic equipment'),
                      'cooking': ('요리', 'food'), 'farming': ('작물 치료제', 'crop treatments'),
                      'fishing': ('낚시 장비', 'fishing equipment'), 'trapper': ('덫', 'traps'),
                      'welding': ('금속 물품', 'metal items'), 'smithing': ('금속 물품', 'metal items'),
                      'metalconstruction': ('금속 구조물', 'metal structures')}
            for entry in learned:
                topic = entry['function'].removeprefix('learn_literature_')
                operations = {r['operation'] for r in entry['recipes']}
                if operations <= {'make'}:
                    # Keep the admitted process (notably forging vs metalwork).
                    fact = next(f for u in lessons for f in u['facts'] if f['payload'].get('function') == entry['function'])
                    text = lex.core(fact, locale)
                    if topic == 'engineer':
                        text = lex.pair(('읽어서 장치 제작법을 배울 수 있다', 'It can be read to learn a device crafting recipe' if len(entry['recipes']) == 1 else 'It can be read to learn device crafting recipes'), locale)
                else:
                    noun = lex.pair(fields.get(topic, ('물품', 'items')), locale)
                    ordered = [op for op in ('make', 'repair', 'modify', 'recover', 'other') if op in operations]
                    if locale == 'ko':
                        labels = {'make': '제작', 'repair': '수리', 'modify': '개조', 'recover': '재료 회수', 'other': '관련 작업'}
                        text = '읽어서 ' + noun + ' ' + parallel_names([labels[op] for op in ordered]) + ' 방법을 배울 수 있다'
                    else:
                        related = [op for op in ('make', 'repair', 'modify') if op in operations]
                        phrases = [en.join(related) + ' ' + noun] if related else []
                        if 'recover' in operations:
                            phrases.append('recover materials')
                        if 'other' in operations:
                            phrases.append('work with ' + noun)
                        text = 'It can be read to learn how to ' + en.join(phrases)
                if locale == 'en' and len(entry['recipes']) == 1:
                    text = text.replace('learn electronic-device recipes', 'learn an electronic-device recipe')
                overviews.append(text)
            overview = '. '.join(dict.fromkeys(overviews))
            overview = detail_text(overview, overview, [r['names'][locale] for r in recipes.values()],
                                   compact=compact, relationship='learning_content')
            emit(lessons + select({'read_literature'}), overview)
            if not compact:
                detail = learning_groups(recipes.values(), locale, overview.split('\n', 1)[0])
                if detail:
                    output[-1]['target_groups'] = detail
        else:
            emit(lessons + select({'read_literature'}), '. '.join(lex.core(u['facts'][0], locale) for u in lessons))
    leisure = select({'read_for_morale'})
    if leisure:
        emit(leisure + select({'read_literature'}), lex.pair(('기분 전환을 위한 읽을거리로 쓸 수 있다', 'It can be read for a change of mood'), locale))

    # Scope is attached to each target group by the reviewed source adapter.
    for relation in plan.get('source_traits', {}).get('action_targets', []):
        members = select({relation['function']})
        if not members:
            continue
        groups = relation['groups']
        categories = list(dict.fromkeys(g['category'][locale] for g in groups))
        target_entries = [('일부 ' if g['scope'] == 'some' else '') + name[locale] if locale == 'ko'
                          else ('Some ' if g['scope'] == 'some' else '') + name[locale]
                          for g in groups for name in g['targets']]
        action = relation['action']
        if action == 'paint':
            summary = ('벽이나 가구 등을 칠할 수 있다' if locale == 'ko' else 'It can be used to paint walls or furniture, for example')
            # Categories are an overview of this evidenced target set, not a
            # claim that every object in those categories supports the action.
            if set(categories) != ({'벽', '가구'} if locale == 'ko' else {'walls', 'furniture'}):
                raise ValueError('unreviewed paint target categories')
            signs = select({'paint_wall_sign'}) if compact else []
            if signs:
                summary = '벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다' if locale == 'ko' else 'It can be used to paint walls or furniture, for example, and paint signs on walls'
            text = detail_text(summary, '다음 대상을 칠할 수 있다' if locale == 'ko' else 'It can be used to paint the following targets',
                               target_entries, compact=compact, relationship='scoped_target_groups')
            emit(members + signs, text)
            if not compact:
                output[-1]['target_groups'] = scoped_groups(groups, target_entries, locale, text.split('\n', 1)[0])

    dismantling = select({'dismantle_built_object'})
    targets = plan.get('source_traits', {}).get('dismantling_targets', [])
    if not compact and dismantling and targets:
        selected_targets = targets
        target_names = [t[locale] for t in selected_targets]
        text = (('' if compact else '톱과 드라이버로 ') + parallel_names(target_names) + ' 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다') if locale == 'ko' else (('It can be used to dismantle constructed objects such as ' if compact else 'A saw and screwdriver can be used to dismantle constructed objects such as ') + en.join(target_names) + ' and recover materials')
        emit(dismantling, text)
        if all(set(u['fact_refs']) <= used for u in dismantling):
            functions.discard('dismantle_built_object')

    battery_power = select({'supply_vehicle_electrical_power'})
    if battery_power:
        emit(battery_power + select({'install_vehicle_battery'}), lex.pair(('호환 차량의 시동과 전기 장치에 전력을 공급할 수 있다', 'It can supply power for starting a compatible vehicle and operating its electrical equipment'), locale))
    headlight = select({'provide_vehicle_headlight'})
    if headlight:
        emit(headlight + select({'install_vehicle_bulb'}), lex.pair(('호환 차량의 전조등에 달아 빛을 낼 수 있다', 'It can provide light in a compatible vehicle headlight'), locale))

    engine_salvage = select({'salvage_vehicle_engine'})
    emit(engine_salvage, lex.pair((
        '엔진에서 부품을 회수할 수 있다',
        'It can be used to salvage engine parts'), locale))
    if 'link_remote_device' in functions:
        controller = plan.get('source_traits', {}).get('RemoteController', '').lower() == 'true'
        emit(select({'link_remote_device', 'send_remote_trigger'}), lex.pair((
            '호환 장치를 연결해 원격으로 작동시킬 수 있다' if controller else '호환 조종기에 연결하면 원격으로 작동시킬 수 있다',
            'It can be linked to a compatible device and remotely activate that device' if controller else 'It can be activated remotely after linking it to a compatible controller'), locale))
    key_actions = {
        'operate_door_lock': ('문 잠금과 해제', 'locking and unlocking doors'),
        'remove_matching_padlock': ('구조물 자물쇠 제거', 'removing structure padlocks'),
        'request_matching_vehicle_start': ('차량 시동', 'starting vehicles'),
    }
    if compact and len(functions & key_actions.keys()) > 1:
        labels = [lex.pair(label, locale) for fn, label in key_actions.items() if fn in functions]
        verbs = {'operate_door_lock': ('맞는 문을 잠그거나 잠금을 풀', '맞는 문을 잠그거나 잠금을 풀'),
                 'remove_matching_padlock': ('구조물의 자물쇠를 제거하', '구조물의 자물쇠를 제거할'),
                 'request_matching_vehicle_start': ('차량 시동을 걸', '차량 시동을 걸')}
        actions = [verbs[fn] for fn in key_actions if fn in functions]
        text = (actions[0][1] + ' 수 있다. ' + '거나 '.join([v[0] for v in actions[1:-1]] + [actions[-1][1]]) + ' 수도 있다' if locale == 'ko' else
                'It can be used for ' + en.join(labels))
        if 'avoid_first_door_alarm_trigger' in functions:
            text += lex.pair(('. 차량 첫 개방 경보를 막지만 이미 울리는 경보는 끄지 못한다',
                              '. It prevents the first-entry vehicle alarm but cannot silence an active alarm'), locale)
        emit(select(set(key_actions) | {'avoid_first_door_alarm_trigger'}), text)
    elif {'request_matching_vehicle_start', 'avoid_first_door_alarm_trigger'} <= functions:
        emit(select({'request_matching_vehicle_start', 'avoid_first_door_alarm_trigger'}), lex.pair((
            '맞는 차량의 시동을 거는 데 쓸 수 있다. 차량 문을 처음 열 때 경보를 막지만 이미 울리는 경보는 끄지 못한다',
            'It can be used to start the matching vehicle. It prevents the alarm when first opening a vehicle door but cannot silence an active alarm'), locale))
    code_lock = select({'install_combination_padlock', 'remove_combination_padlock'})
    if len(code_lock) == 2:
        emit(code_lock, lex.pair((
            '제작한 나무 상자 같은 보관함을 비밀번호로 잠그거나 잠금을 해제할 수 있다. 문에는 쓸 수 없다',
            'It can lock or unlock storage containers such as crafted wooden crates with a code, except doors') if compact else (
            '제작한 나무 상자 같은 보관함에 비밀번호 잠금을 설정할 수 있다. 설정한 번호로 잠금을 해제할 수 있다. 문에는 쓸 수 없다',
            'It can secure storage containers such as crafted wooden crates with a chosen code. The configured code can unlock them. It cannot be used on doors'), locale))
    for activity in ('spear_upgrade', 'explosive_modification', 'crop_spray_preparation'):
        members = [u for u in units if activity in purpose_tokens(u) and not used & set(u['fact_refs'])
                   and any(f['payload'].get('role') in {'material', 'tool', 'container'} for f in u['facts'])]
        if not members:
            continue
        roles = {f['payload'].get('role') for u in members for f in u['facts']}
        if activity == 'spear_upgrade':
            wording = ('부착물을 달아 쓸 수 있다', 'It can be fitted with an attachment') if 'fish_with_spear' in functions else (
                ('창에 부착물을 다는 데 쓸 수 있다', 'It can be used to fit attachments to spears') if 'tool' in roles else
                ('창에 부착물을 다는 재료로 쓸 수 있다', 'It can be used as material for attaching items to spears'))
            if not compact and 'fish_with_spear' in functions:
                attachments = {i['item_id']: i for u in members for rel in u.get('recipe_targets', []) for i in rel.get('inputs', [])
                               if i['item_id'] != plan['item_id'] and i['declared_traits'].get('Type') == 'Weapon'}
                if attachments:
                    selected = list(attachments.values())
                    example = selected[:3]
                    ko_names = ', '.join(i['names']['ko'] for i in example)
                    en_names = en.join([en.object_phrase(i) for i in example])
                    wording = (ko_names + (' 등의 도구를' if len(selected) > 3 else ' 등을') + ' 부착해 쓸 수 있다',
                               'It can be fitted with tools such as ' + en_names)
        elif activity == 'explosive_modification':
            results = [r for u in members for rel in u.get('recipe_targets', []) for r in rel['results']]
            modes = []
            for result in results:
                fields = result.get('declared_traits', {})
                label = (('움직임 감지', 'motion sensing') if float(fields.get('SensorRange', 0)) > 0 else
                         ('원격 작동', 'remote activation') if fields.get('CanBeRemote', '').lower() == 'true' else
                         ('시간 지연', 'time delay') if float(fields.get('ExplosionTimer', 0)) > 0 else None)
                if label and lex.pair(label, locale) not in modes:
                    modes.append(lex.pair(label, locale))
            purpose = ('·'.join(modes) if locale == 'ko' else en.join(modes)) or lex.pair(('격발', 'triggering'), locale)
            traits = plan.get('source_traits', {})
            modification_roles = {rel.get('modification_role') for u in members for rel in u.get('recipe_targets', [])}
            target = modification_roles == {'target'}
            component = modification_roles == {'component'}
            categories = list(dict.fromkeys(device_category(r, locale) for r in results if device_category(r, locale)))
            device_scope = ((', '.join(categories[:-1]) + ' 및 ' + categories[-1] if len(categories) > 1 else categories[0]) if locale == 'ko' else en.join(categories)) if not compact and categories else lex.pair(('장치', 'devices'), locale)
            if locale == 'ko':
                text = (purpose + ' 기능을 더해 개조할 수 있다' if target else
                        device_scope + '에 달아 ' + purpose + ' 기능을 더하는 부품으로 쓸 수 있다' if component else
                        '장치에 ' + purpose + ' 기능을 더하는 ' + ('도구' if 'tool' in roles else '재료') + '로 쓸 수 있다')
                wording = (text, text)
            else:
                text = ('It can be modified for ' + purpose if target else
                        'It can serve as a component for adding ' + purpose + ' to ' + device_scope if component else
                        'It can be used as ' + ('a tool' if 'tool' in roles else 'material') + ' for adding ' + purpose + ' to devices')
                wording = (text, text)
        else:
            vessel = bool(functions & {'store_water', 'carry_water'}) and not functions & {'drink_food_contents', 'smoke_cigarette'}
            wording = ('작물 치료용 분무액을 만드는 용기로 쓸 수 있다', 'It can hold the mixture when making crop-treatment spray') if vessel else (
                '작물 치료용 분무액을 만드는 재료로 쓸 수 있다', 'It can be used as an ingredient for making crop-treatment spray')
        if activity in {'spear_upgrade', 'explosive_modification'} and 'tool' not in roles and not (activity == 'explosive_modification' and (target or component)) and not (activity == 'spear_upgrade' and 'fish_with_spear' in functions):
            purpose_label = lex.pair(('창 부착물 고정', 'attaching items to spears') if activity == 'spear_upgrade' else ('장치 개조', 'modifying devices'), locale)
            emit_material(members, [('action', purpose_label)], lex.pair(wording, locale))
        else:
            emit(members, lex.pair(wording, locale))

    electricity = select({'supply_nearby_electricity'})
    if electricity:
        pumps = select({'power_exterior_fuel_pumps'})
        text = lex.pair(('가동해 주변 전기 설비에 전원을 공급할 수 있다',
                         'It can be operated to power nearby electrical equipment'), locale)
        if not compact:
            # A setting-dependent target is evidence for the broader purpose,
            # not a reason to publish game configuration advice or promise it
            # works in every setting. Use confirmed indoor-appliance examples.
            text = lex.pair(('가동해 주변의 냉장고나 세탁기 등 전기 설비에 전원을 공급할 수 있다',
                             'It can be operated to power nearby electrical equipment such as refrigerators and washing machines'), locale)
        emit(electricity + pumps, text)

    def device_method():
        traits = plan.get('source_traits', {})
        def positive(key):
            value = traits.get(key, '')
            return bool(re.fullmatch(r'\d+(?:\.\d+)?', value)) and float(value) > 0
        if traits.get('CanBePlaced', '').lower() == 'true':
            # The purpose proof joins placement to the native effect. Keep the
            # separate physics dispatch as evidence without claiming a thrown
            # sensor/timer device activates through the instantaneous path.
            if positive('SensorRange'):
                return lex.pair(('설치한 뒤 움직임을 감지하면 작동한다',
                                 'Once placed and armed, it activates when movement is detected'), locale)
            if positive('ExplosionTimer'):
                return lex.pair(('시간을 맞춰 설치하면 지연 작동시킬 수 있다',
                                 'It can be placed with a timer for delayed activation'), locale)
            if (all(re.fullmatch(r'0+(?:\.0+)?', traits.get(key, '0'))
                    for key in ('SensorRange', 'ExplosionTimer'))
                    and traits.get('CanBeRemote', '').lower() != 'true'):
                return lex.pair(('설치하거나 던져서 사용할 수 있다',
                                 'It can be placed or thrown for use'), locale)
            return lex.pair(('설치해 사용할 수 있다', 'It can be placed for use'), locale)
        return lex.pair(('던져서 사용할 수 있다', 'It can be thrown'), locale)

    therapies = select({'poultice_fracture_recovery', 'poultice_wound_recovery', 'poultice_wound_infection'})
    if therapies:
        application = select({'apply_poultice'})
        emit(therapies + application, '. '.join(lex.core(u['facts'][0], locale).rstrip('.') for u in therapies))

    device_effects = select({'device_explosion_damage', 'device_start_fire', 'device_smoke_distraction'})
    if device_effects:
        throwing = select({'request_physics_attack'})
        sentences = [lex.core(u['facts'][0], locale) for u in device_effects]
        text = '. '.join(s.rstrip('.') for s in sentences)
        if throwing and not compact:
            text += '. ' + device_method()
        emit(device_effects + throwing, text)

    # The declared result supplies just enough purpose to explain a processing
    # role; the input is never described as applying the finished material.
    for unit in units:
        joined = [r for r in unit.get('recipe_targets', [])
                  if r.get('result_purpose', {}).get('function') == 'plaster_supported_structure']
        if joined and not used & set(unit['fact_refs']):
            roles = {r['input_role'] for r in joined}
            if roles == {'container'}:
                wording = ('도색할 구조물에 바를 석고를 섞는 용기로 쓸 수 있다',
                           'It can hold plaster being mixed to prepare structures for painting')
            elif roles <= {'material', 'ingredient'}:
                wording = ('도색할 구조물에 바를 석고를 만드는 재료로 쓸 수 있다',
                           'It can be used to make plaster for preparing structures for painting')
            else:
                continue
            emit([unit], lex.pair(wording, locale))

    if not compact:
        service = select({'service_vehicle_parts'})
        targets = plan.get('source_traits', {}).get('vehicle_service_roles', [])
        labels = {'tire': ('타이어', 'tires'), 'brake': ('브레이크', 'brakes'),
                  'suspension': ('서스펜션', 'suspension parts'), 'electrical': ('전기 부품', 'electrical parts'),
                  'seat': ('좌석', 'seats'), 'glazing': ('차량 유리', 'vehicle windows'),
                  'fuel_tank': ('연료 탱크', 'fuel tanks'), 'exhaust': ('배기 부품', 'exhaust parts'),
                  'bodywork': ('차체 부품', 'body panels')}
        if service and targets:
            sentences = []
            for role in ('direct', 'support'):
                selected = {t['category'] for t in targets if t['role'] == role}
                names = [lex.pair(labels[k], locale) for k in labels if k in selected]
                if not names:
                    continue
                noun = parallel_names(names)
                if locale == 'ko':
                    sentences.append(noun + (' 장착과 탈거에 작업 도구로 쓸 수 있다' if role == 'direct'
                                              else ' 장착과 탈거에 필요한 보조 도구로 쓸 수 있다'))
                else:
                    sentences.append(('It can be used to install and remove ' if role == 'direct'
                                      else 'It is a required supporting tool for installing and removing ') + noun)
            emit(service, '. '.join(sentences))

    noise = select({'emit_attracting_noise'})
    if noise:
        throwing = select({'request_physics_attack'})
        text = lex.pair(('소음을 내 좀비의 주의를 끄는 데 쓸 수 있다',
                         'It can produce noise to attract zombies'), locale)
        if throwing and not compact:
            text += '. ' + device_method()
        emit(noise + throwing, text)

    tent = select({'pitch_tent', 'rest_at_placed_tent'})
    if len(tent) == 2:
        emit(tent, lex.pair(('텐트를 설치해 쉬거나 잘 수 있다', 'It can be pitched as a tent for resting or sleeping'), locale))

    # The same welding implement can be debited by a recipe and kept by a
    # construction action; neither participation makes it a building material.
    if any('metal_welding_construction' in purpose_tokens(u) and any(f['payload'].get('role') == 'tool' for f in u['facts']) for u in units):
        welding = [u for u in units if not used & set(u['fact_refs']) and purpose_tokens(u) & {'construction', 'metal_welding_construction', 'welded_parts'}]
        wearable = bool(select({'wear_on_body', 'wear_configured_clothing'}))
        if wearable:
            places = [u for u in units if not used & set(u['fact_refs']) and all(f['payload'].get('state') == 'worn_location' for f in u['facts'])]
            emit(welding + select({'wear_on_body', 'wear_configured_clothing'}) + places, '용접 작업을 할 때 착용하는 장비다' if locale == 'ko' else 'It is equipment worn for welding work')
        else:
            emit(welding, lex.pair(('금속 부품을 만들거나 금속 구조물을 세울 때 용접 도구로 쓸 수 있다', 'It can be used as a tool for metal-part welding and welded construction'), locale))

    seat = select({'use_vehicle_seat', 'store_vehicle_items'})
    if functions >= {'use_vehicle_seat', 'store_vehicle_items'}:
        emit(seat + select({'install_vehicle_storage_part'}), lex.pair(('호환 차량에 장착해 앉거나 물품을 보관할 수 있다', 'It can be installed in a compatible vehicle for seating or item storage'), locale))
    tank = select({'store_vehicle_fuel', 'supply_vehicle_engine_fuel', 'transfer_vehicle_fuel'})
    if functions >= {'store_vehicle_fuel', 'supply_vehicle_engine_fuel', 'transfer_vehicle_fuel'}:
        emit(tank + select({'install_vehicle_storage_part'}), lex.pair((
            '차량에 장착해 연료를 보관하고 엔진에 공급할 수 있다',
            'It can be installed in a compatible vehicle to store fuel and supply the engine'), locale))
    doors = select({'operate_installed_vehicle_door', 'operate_installed_vehicle_lock', 'operate_installed_vehicle_window'})
    panel = [u for u in units if not used & set(u['fact_refs']) and any(f['payload'].get('function', '').startswith('install_vehicle_') for f in u['facts'])]
    if doors and len(panel) == 1:
        labels = []
        if functions & {'operate_installed_vehicle_door', 'operate_installed_vehicle_window'}:
            labels.append(('여닫을 수 있다', 'It can be opened and closed'))
        if 'operate_installed_vehicle_lock' in functions:
            labels.append(('잠그거나 잠금을 풀 수 있다', 'It can be locked and unlocked'))
        opening = lex.core(panel[0]['facts'][0], locale).rstrip('.')
        if compact:
            fn = panel[0]['facts'][0]['payload']['function']
            name = lex.pair(lex.source.PANEL_NAMES[fn.removeprefix('install_vehicle_')], locale)
            emit(panel + doors, '호환 차량의 ' + name + ' 교체 부품으로 쓸 수 있다' if locale == 'ko' else 'It can replace the ' + name + ' in a compatible vehicle')
        else:
            emit(panel + doors, opening + ('. 장착 후 ' + ('여닫거나 잠그고 잠금을 풀 수 있다' if len(labels) == 2 else labels[0][0]) if locale == 'ko' else '. Once installed, it can be opened, closed, locked or unlocked' if len(labels) == 2 else '. ' + labels[0][1]))
    replacement_names = {**lex.source.PANEL_NAMES,
        'tire': ('타이어', 'tire'), 'brake': ('브레이크', 'brake'),
        'suspension': ('서스펜션', 'suspension'), 'muffler': ('머플러', 'muffler')}
    for fn in sorted(f for f in functions if f and f.startswith('install_vehicle_')):
        key = fn.removeprefix('install_vehicle_')
        if key in replacement_names:
            name = lex.pair(replacement_names[key], locale)
            emit(select({fn}), '호환 차량의 ' + name + ' 교체 부품으로 쓸 수 있다' if locale == 'ko' else 'It can replace the ' + name + ' in a compatible vehicle')
    emit(select({'install_light_bulb'}), lex.pair(('호환 조명에 넣는 교체용 전구다', 'It can serve as a replacement bulb for compatible lamps'), locale))

    fuel_transfer = select({'fill_petrol_container', 'transfer_vehicle_fuel'})
    if len(fuel_transfer) == 2:
        emit(fuel_transfer, lex.pair(('주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다', 'It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle'), locale))
    embedded = select({'remove_embedded_glass', 'remove_embedded_bullet'})
    if len(embedded) == 2:
        embedded += [u for u in units if not used & set(u['fact_refs']) and all(f['fact_kind'] == 'effect' and f['payload'].get('property') in {'embedded_glass', 'embedded_bullet'} and f['payload'].get('direction') == 'remove' for f in u['facts'])]
        emit(embedded, lex.pair(('상처에 박힌 유리나 총알을 제거하는 데 쓸 수 있다', 'It can be used to remove glass or bullets embedded in wounds'), locale))
    patch = select({'apply_garment_patch', 'unpick_garment_patch'})
    if len(patch) == 2:
        emit(patch, lex.pair(('의류를 수선하거나 덧댄 천을 떼는 데 쓸 수 있다', 'It can be used to mend clothing or remove patches') if compact else ('의류의 구멍을 덧대거나 패딩을 붙이고, 덧댄 천을 떼어낼 수 있다. 떼어낸 천은 회수할 수도 있다', 'It can mend garment holes, add padding and remove patches, with a chance to recover the removed fabric'), locale))
    electronics_contexts = {'electronic_assembly', 'radio_crafting', 'electronic_salvage', 'radio_salvage'}
    electronics_tools = [u for u in units if not used & set(u['fact_refs'])
                         and purpose_tokens(u) & electronics_contexts
                         and any(f['payload'].get('role') == 'tool' for f in u['facts'])]
    electronics_activities = set().union(*(purpose_tokens(u) for u in electronics_tools)) if electronics_tools else set()
    if electronics_activities >= electronics_contexts:
        lamp = select({'convert_lamp_to_battery'})
        text = lex.pair(('전자기기를 만들거나 분해할 수 있다' if compact else
                         '전자 부품과 무전기를 만들 수 있다. 라디오와 TV를 포함한 전자기기를 분해해 부품을 회수할 수 있다',
                         'It can be used to make or dismantle electronic devices' if compact else
                         'It can be used to make electronic components and radios. It can be used to dismantle electronic devices, including radios and TVs, to recover parts'), locale)
        if lamp:
            if compact and locale == 'ko':
                text = text.removesuffix('할 수 있다') + '하고, 조명을 건전지용으로 개조할 수 있다'
            elif compact:
                text += ' and convert lamps to battery power'
            else:
                text += lex.pair(('. 조명을 건전지용으로 개조할 수 있다', '. It can convert lamps to battery power'), locale)
        emit(electronics_tools + lamp, text)
    if not compact:
        for contexts, wording in (({'woodworking', 'construction', 'carpentry_menu_construction'}, ('목공과 건축 작업에 쓸 수 있다', 'It can be used for woodworking and construction')),
                                  ({'electronic_assembly', 'radio_crafting'}, ('전자 부품이나 무전기를 만드는 데 쓸 수 있다', 'It can be used to make electronic components or radios'))):
            members = [u for u in units if not used & set(u['fact_refs']) and purpose_tokens(u) - {None} <= contexts and purpose_tokens(u) & contexts
                       and not any(f['payload'].get('role') in {'ingredient', 'attachment'} for f in u['facts'])]
            if len(set().union(*(purpose_tokens(u) for u in members)) - {None}) > 1 and any(f['payload'].get('role') == 'tool' for u in members for f in u['facts']):
                emit(members, lex.pair(wording, locale))

    if not compact:
        tires = [u for u in units if all(f['payload'].get('property') == 'installed_tire_air_or_attachment' for f in u['facts'])]
        emit(tires, lex.pair(('주행 중 공기압이 낮아지고 타이어가 닳을 수 있다. 공기압이 낮거나 많이 닳으면 타이어가 빠질 수 있다', 'Driving can reduce tire pressure and wear the tire; low pressure or poor condition can cause it to come off'), locale))
    crafting_frames.render(assembly)
    notes = select({'view_written_note_pages', 'record_written_notes'})
    if {f['payload'].get('function') for u in notes for f in u['facts']} == {'view_written_note_pages', 'record_written_notes'}:
        emit(notes, '메모를 읽고 적는 데 쓸 수 있다' if locale == 'ko' else 'It can be used for reading and writing notes')

    exercises = select({'exercise_barbell_curl', 'exercise_dumbbell_press', 'exercise_biceps_curl'})
    if compact and len(exercises) > 1:
        emit(exercises, lex.pair(('중량 운동에 쓸 수 있다', 'It can be used for weight training'), locale))

    attachment = select({'attach_weapon_part'})
    detachment = select({'remove_weapon_part'})
    attachment_purposes = select({fn for fn in functions if fn and fn.startswith('attachment_purpose_')})
    if attachment and attachment_purposes:
        # Native consumption refines the authored aiming-speed wording. Both
        # evidence paths remain linked; they are not two independent benefits.
        native_aiming = any(u['facts'][0]['payload']['function'] == 'attachment_purpose_movement_aim' for u in attachment_purposes)
        shown_purposes = [u for u in attachment_purposes if not (native_aiming and
                          u['facts'][0]['payload']['function'] == 'attachment_purpose_aiming')]
        emit(attachment_purposes + (attachment + detachment if compact else []),
             '. '.join(lex.core(u['facts'][0], locale) for u in shown_purposes))
        if compact:
            attachment, detachment = [], []
    if attachment and detachment:
        emit(attachment + detachment,
             '드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다' if locale == 'ko' else
             'With a screwdriver, it can be attached to a compatible firearm or detached and recovered')
    elif attachment:
        emit(attachment, '드라이버로 호환 총기에 장착할 수 있다' if locale == 'ko' else
             'It can be attached to a compatible firearm with a screwdriver')
    elif detachment:
        emit(detachment, '드라이버로 장착된 부품을 떼어 회수할 수 있다' if locale == 'ko' else
             'The installed part can be detached and recovered with a screwdriver')
    magazine = select({'insert_matching_magazine'})
    if magazine:
        filling = select({'fill_magazine'})
        emit(magazine + filling, ('호환 탄약을 담아 맞는 총기에 장전할 수 있다' if filling else '호환 총기에 끼워 사용할 수 있다') if locale == 'ko' else
             ('It can be filled with compatible ammunition and loaded into a matching firearm' if filling else 'It can be inserted into a compatible firearm'))

    # The condition explicitly names wearing and the affected firearm scope.
    # Share this frame on both surfaces before generic clothing or effects can
    # claim its members. Unknown operations/scopes retain the scoped fallback.
    slots = select({'provide_belt_slots', 'provide_right_holster_slot', 'provide_paired_holster_slots'})
    if len(slots) == 1:
        slot_fn = slots[0]['facts'][0]['payload']['function']
        wearing = select({'wear_on_body', 'wear_configured_clothing'})
        locations = [u for u in units if not used & set(u['fact_refs']) and all(f['payload'].get('state') == 'worn_location' for f in u['facts'])]
        emit(slots + wearing + locations, lex.pair(families.OVERVIEWS[slot_fn][1], locale))

    for unit in units:
        text = lex.reload_effect(unit, plan, locale, compact)
        if text is None:
            continue
        wear = select({'wear_on_body', 'wear_configured_clothing'})
        locations = [u for u in units if any(f['payload'].get('state') == 'worn_location'
                                           for f in u['facts'])]
        if not compact and wear and len(locations) == 1:
            location = lex.wearing(locations[0]['facts'][0]['payload']['value'], locale)
            if location not in {'착용할 수 있다', '몸에 착용할 수 있다', 'It can be worn'}:
                text = location + '. ' + text
        emit(wear + locations + [unit], text, ordered=True,
             reason='confirmed reload-speed multiplication with worn and ammunition scope; action duration is not inferred')

    # Recipe result groups refine the same forging purpose. Keep roles apart
    # and merge only when no distinguishing public condition remains.
    forging = FORGING_ACTIVITIES
    if compact:
        forge_materials = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
                           and purpose_tokens(u) - {None} <= forging and purpose_tokens(u) & forging
                           and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'material'}]
        emit_material(forge_materials, [('action', lex.pair(('금속 단조', 'metal forging'), locale))],
                 lex.pair(('금속을 단조할 때 재료로 쓸 수 있다', 'It can supply material for metal forging'), locale))
    for role in ('tool', 'material'):
        members = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
                   and (purpose_tokens(u) - {None}) <= forging
                   and purpose_tokens(u) & forging
                   and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {role}]
        activities = set().union(*(purpose_tokens(u) for u in members)) if members else set()
        if 'metal_forging' in activities and len(activities & forging) > 1:
            text = (('금속을 단조하는 데 사용할 수 있다' if role == 'tool' else '금속을 단조할 때 재료로 쓸 수 있다') if locale == 'ko'
                    else ('It can be used for metal forging' if role == 'tool' else 'It can be used as material for metal forging'))
            if compact and role == 'tool':
                wood = [u for u in units if not used & set(u['fact_refs'])
                        and purpose_tokens(u) - {None} <= {'woodworking', 'construction', 'carpentry_menu_construction'}
                        and purpose_tokens(u) & {'woodworking', 'construction', 'carpentry_menu_construction'}
                        and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'tool'}]
                if wood:
                    members += wood
                    text = lex.pair(('금속을 단조하거나 목재를 가공할 수 있다',
                                     'It can be used to forge metal or work wood'), locale)
            emit(members, text)

    for u in units:
        if used & set(u['fact_refs']):
            continue
        activities = purpose_tokens(u) - {None}
        if activities == {'item_packaging'} and any(
                plan['qualifiers'][q]['payload']['predicate'] == lex.source.EGG_PACKING for q in u['qualifier_refs']):
            text = ('달걀곽에 포장할 수 있다' if locale == 'ko' else 'The eggs can be packed into a carton')
            if not compact:
                text += ('. 익히지 않고 타지도 않은 달걀을 포장하며 냉동 상태도 허용한다' if locale == 'ko'
                         else '. The eggs must be neither cooked nor burnt; frozen eggs are accepted')
            emit([u], text)
        if activities == {'seed_packaging'} and not u['qualifier_refs']:
            emit([u], '씨앗을 봉투에 포장할 수 있다' if locale == 'ko' else 'The seeds can be packed into a packet')
        if activities == {'metal_forging'} and not u['qualifier_refs'] and any(
                f['payload'].get('role') == 'material' for f in u['facts']):
            results = {r['item_id']: r for relation in u['recipe_targets'] for r in relation['results']}
            if len(results) == 1:
                target = next(iter(results.values()))['names'][locale]
                emit([u], object_name(target) + ' 만들 때 재료로 쓸 수 있다' if locale == 'ko' else 'It can be used as material for making ' + target)

    fabric_result = plan.get('source_traits', {}).get('fabric_result')
    fabric_dirty = plan.get('source_traits', {}).get('fabric_dirty_result')
    recovered_name = fabric_result['names'][locale] if fabric_result else lex.pair(('옷감', 'fabric'), locale)
    # The recovered result identity owns the material name, including leather.
    compact_recovery = recovered_name
    if fabric_result:
        compact_recovery = lex.pair({
            'Base.RippedSheets': ('천 조각', 'cloth scraps'),
            'Base.DenimStrips': ('데님 조각', 'denim strips'),
            'Base.LeatherStrips': ('가죽 조각', 'leather strips'),
        }.get(fabric_result['item_id'], (fabric_result['names']['ko'], fabric_result['names']['en'].lower())), locale)

    # A wearable can provide recovered fabric, rope material and fire supplies.
    # Group these uses from their payloads, not a garment name or length budget.
    wearables = select({'wear_on_body', 'wear_configured_clothing'})
    fabric_uses = [u for u in units if any(f['payload'].get('activity') == 'fabric_recovery' for f in u['facts'])
                   and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'material'}]
    rope_uses = [u for u in units if any(f['payload'].get('activity') == 'sheet_rope_making' for f in u['facts'])
                 and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'material'}]
    recovery_overview = (object_name(compact_recovery) + ' 회수할 수 있다'
                         if locale == 'ko' else 'It can provide ' + compact_recovery)
    if compact and not wearables and fabric_uses and rope_uses and fabric_result:
        text = recovery_overview
        emit(fabric_uses + rope_uses, text)
    if compact and wearables and fabric_uses and fabric_result:
        places = [u for u in units if any(f['payload'].get('state') == 'worn_location' for f in u['facts'])]
        fuel, tinder = select(FUEL), select(TINDER)
        forms = select({'switch_declared_clothing_form'})
        wearing = '착용할 수 있다' if locale == 'ko' else 'It can be worn'
        if forms and form_text:
            wearing += '. ' + form_text if locale == 'ko' else '. It can be worn in alternate forms'
            if options and options <= {'UpHoodie', 'DownHoodie'}:
                wearing = '후드를 조절해 착용할 수 있다' if locale == 'ko' else 'It can be worn with the hood up or down'
        text = wearing + '. ' + recovery_overview
        if fuel or tinder:
            supplies = '나 '.join(word for members, word in ((fuel, '연료'), (tinder, '불쏘시개')) if members)
            supplies_en = en.join([word for members, word in ((fuel, 'fuel'), (tinder, 'tinder')) if members])
            text += '. ' + (supplies + '로도 쓸 수 있다' if locale == 'ko' else 'It can also be used as ' + supplies_en)
        emit(wearables + places + fabric_uses + rope_uses + fuel + tinder + (forms if fuel or tinder else []), text)

    # A confirmed food-preparation purpose contains dough preparation only
    # for the same participant role and without a separate public condition.
    # Role changes and scoped tasks such as slicing cooked food stay separate.
    cooking_frames.render(assembly)
    media_frames.render(assembly)
    openers = select({'unpack_canned_food'})
    opening_tools = [u for u in units if not used & set(u['fact_refs'])
        and any(f['payload'].get('activity') == 'package_opening' for f in u['facts'])
        and any(f['payload'].get('role') == 'tool' for f in u['facts'])]
    if openers and opening_tools:
        opening_tools += [u for u in units if not used & set(u['fact_refs'])
            and any(f['payload'].get('role') == 'tool' for f in u['facts'])
            and 'food_preparation' in purpose_tokens(u)
            and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.BEAN_PREPARATION}]
        text = '통조림을 열어 내용물을 꺼낼 수 있다' if locale == 'ko' else 'It can be used to open cans and retrieve their contents'
        emit(openers + opening_tools, text)

    water = select({'store_water', 'carry_water', 'receive_poured_water'})
    water_functions = {f['payload'].get('function') for u in water for f in u['facts']}
    if not compact and {'store_water', 'carry_water'} <= water_functions:
        text = ('물을 담아 보관하거나 운반할 수 있다' if locale == 'ko'
                else 'It can hold water for storage or carrying')
        emit(water, text)

    medical_frames.render(assembly)
    ropes = select({'supply_escape_rope', 'start_escape_rope_ascent', 'descend_installed_escape_rope'})
    if {'supply_escape_rope', 'start_escape_rope_ascent'} <= {f['payload'].get('function') for u in ropes for f in u['facts']}:
        has_descent = any(f['payload'].get('function') == 'descend_installed_escape_rope' for u in ropes for f in u['facts'])
        emit(ropes, lex.pair(('설치해 층 사이를 오르내리는 데 쓸 수 있다', 'It can be installed for climbing between floors') if has_descent else
                            ('설치해 위층으로 올라가는 데 사용할 수 있다', 'It can be installed for climbing to an upper floor'), locale))

    placed = select({fn for fn in functions if fn and fn.startswith('placed_purpose_')})
    if placed:
        salvage = [u for u in placed if u['facts'][0]['payload']['function'].startswith('placed_purpose_salvage_')]
        facilities = [u for u in placed if u not in salvage]
        placement = select({'place_moveable_furniture'})
        moving = select({'remove_placed_furniture'})
        if compact:
            prominent = [u for u in facilities if u['facts'][0]['payload']['function'] != 'placed_purpose_surface']
            shown = prominent or facilities
            text = '. '.join(lex.core(u['facts'][0], locale) for u in shown) if shown else lex.pair(
                ('분해해 재료를 회수할 수 있다', 'It can be dismantled to recover materials'), locale)
            emit(placed + placement + moving, text)
        else:
            # Each independent purpose has its own use unit. Placement is a
            # prerequisite already stated by the first concrete purpose.
            ordered = facilities + salvage
            for index, unit in enumerate(ordered):
                emit([unit] + (placement if index == 0 else []), lex.core(unit['facts'][0], locale))
            emit(moving, lex.pair(('집어 들어 다른 위치로 옮길 수 있다',
                                   'It can be picked up and moved to another location'), locale))
    furniture = select({'place_moveable_furniture', 'remove_placed_furniture'})
    if furniture:
        emit(furniture, lex.pair(('가구로 놓아 사용할 수 있다', 'It can be placed for use as furniture') if compact else
                                ('가구로 놓아 사용하거나 다른 위치로 옮길 수 있다', 'It can be placed for use as furniture or moved to another location'), locale))

    maps = select({'view_item_map', 'reveal_item_map_area', 'annotate_item_map', 'erase_item_map_annotations'})
    map_functions = {f['payload'].get('function') for u in maps for f in u['facts']}
    if {'view_item_map', 'annotate_item_map', 'erase_item_map_annotations'} <= map_functions:
        revealed = 'reveal_item_map_area' in map_functions
        text = (('지도를 읽어 그 지역을 세계 지도에서 확인할 수 있다' if revealed else '지도에 그려진 지역을 살펴볼 수 있다') +
                '. 필기구로 글·기호를 남기고 지우개로 지울 수 있다') if locale == 'ko' else (
                ('Reading it reveals the depicted area on the world map' if revealed else 'It can be used to examine the area shown on the map') +
                '. Notes or symbols can be added with a writing implement and removed with an eraser')
        if not compact:
            text += ('. 기존 주석을 수정하거나 옮기려면 필기구와 지우개가 모두 필요하다' if locale == 'ko'
                     else '. Editing or moving existing annotations needs both a writing implement and an eraser')
            if revealed:
                text += ('. 알려진 지역 표시는 직접 방문한 기록을 뜻하지 않는다' if locale == 'ko'
                         else '. Marking an area as known does not record a physical visit')
        if compact:
            emit(maps, text)
        else:
            viewing = [u for u in maps if purpose_tokens(u) & {'view_item_map', 'reveal_item_map_area'}]
            view_text = (('지도를 읽어 그 지역을 세계 지도에서 확인할 수 있다'
                          if revealed else '지도에 그려진 지역을 살펴볼 수 있다') if locale == 'ko' else
                         ('Reading it reveals the depicted area on the world map'
                          if revealed else 'It can be used to examine the area shown on the map'))
            emit(viewing, view_text)
            emit([u for u in maps if u not in viewing],
                 '필기구로 글·기호를 남기고 지우개로 지울 수 있다' if locale == 'ko'
                 else 'Notes or symbols can be added with a writing implement and removed with an eraser')

    nets = select({'place_fishing_net', 'check_fishing_net', 'remove_fishing_net'})
    if {f['payload'].get('function') for u in nets for f in u['facts']} == {'place_fishing_net', 'check_fishing_net', 'remove_fishing_net'}:
        text = ('물에 설치해 미끼 물고기를 잡을 수 있다' if locale == 'ko'
                else 'It can be placed in water to catch bait fish')
        if not compact:
            pass  # Retrieval is self-management; catching bait fish is the purpose.
        emit(nets, text)

    protection = select({'provide_equipped_rain_protection', 'reduce_foraging_rain_effect'})
    if len(protection) == 2:
        text = ('비를 가릴 수 있으며, 비가 야외 채집에 주는 불이익을 줄인다' if locale == 'ko'
                else 'It provides rain protection and reduces the penalty for foraging in the rain')
        emit(protection, text)

    writing = select({'write_note_pages', 'annotate_map'})
    if len(writing) == 2:
        if not compact:
            emit([u for u in writing if 'write_note_pages' in purpose_tokens(u)],
                 '메모를 적을 수 있다' if locale == 'ko' else 'It can be used to write notes')
            emit([u for u in writing if 'annotate_map' in purpose_tokens(u)],
                 '지도에 글이나 기호를 남길 수 있다' if locale == 'ko'
                 else 'It can be used to add map text or symbols')
        else:
            emit(writing, '메모를 적거나 지도에 글이나 기호를 남길 수 있다' if locale == 'ko'
                 else 'It can be used to write notes and add map text or symbols')

    if compact:
        welding_functions = {
            'build_metal_barricade': ('금속 바리케이드 설치', 'installing metal barricades'),
            'remove_metal_barricade': ('금속 바리케이드 철거', 'removing metal barricades'),
            'dismantle_burnt_vehicle': ('불타거나 파손된 차량 분해', 'dismantling burnt or smashed vehicles'),
        }
        welding_contexts = {
            'metal_welding_construction': ('금속 용접 건축', 'welded construction'),
            'welded_parts': ('금속 부품 용접', 'metal-part welding'),
            'construction': ('건축', 'construction'),
        }
        operations = select(welding_functions)
        if operations:
            for u in units:
                if set(u['fact_refs']) & used:
                    continue
                activities = {f['payload'].get('activity') for f in u['facts']} | {(u.get('context') or {}).get('activity')}
                matches = activities & welding_contexts.keys()
                if matches and not any(f['payload'].get('role') == 'material' for f in u['facts']):
                    operations.append(u)
            functions = {f['payload'].get('function') for u in operations for f in u['facts']}
            activities = {f['payload'].get('activity') for u in operations for f in u['facts']}
            activities |= {(u.get('context') or {}).get('activity') for u in operations}
            words = []
            if activities & {'metal_welding_construction', 'welded_parts'}:
                words.append(lex.pair(('금속 용접·건축', 'metal welding and construction') if 'construction' in activities or 'metal_welding_construction' in activities else ('금속 부품 용접', 'metal-part welding'), locale))
            elif 'construction' in activities:
                words.append(lex.pair(('건축', 'construction'), locale))
            if {'build_metal_barricade', 'remove_metal_barricade'} <= functions:
                words.append(lex.pair(('금속 바리케이드 설치와 철거', 'installing or removing metal barricades'), locale))
            else:
                words.extend(lex.pair(welding_functions[f], locale) for f in ('build_metal_barricade', 'remove_metal_barricade') if f in functions)
            if 'dismantle_burnt_vehicle' in functions:
                words.append(lex.pair(welding_functions['dismantle_burnt_vehicle'], locale))
            welding_order = ('construction', 'metal_welding_construction', 'welded_parts', 'build_metal_barricade', 'remove_metal_barricade', 'dismantle_burnt_vehicle')
            operations.sort(key=lambda u: min((welding_order.index(t) for t in purpose_tokens(u) if t in welding_order), default=len(welding_order)))
            if locale == 'ko':
                actions = {'금속 용접·건축': '금속을 용접해 건축하는', '금속 부품 용접': '금속 부품을 용접하는', '건축': '건축하는',
                           '금속 바리케이드 설치와 철거': '금속 바리케이드를 설치하거나 철거하는', '금속 바리케이드 설치': '금속 바리케이드를 설치하는',
                           '금속 바리케이드 철거': '금속 바리케이드를 철거하는', '불타거나 파손된 차량 분해': '불타거나 파손된 차량을 분해하는'}
                wording = '. '.join(actions[word] + ' 데 쓸 수 있다' for word in words)
            else:
                wording = 'It can be used for ' + en.join(words)
            emit(operations, wording, ordered=True)


    for fn, activity, wording in (
        ('portion_into_bowls', 'food_portioning', ('담긴 음식을 여러 그릇에 나눌 수 있다', 'Its contents can be divided into bowls')),
        ('pack_into_box', 'item_packaging', ('모아서 상자로 포장할 수 있다', 'It can be collected and packed into a box')),
    ):
        action = select({fn})
        if action:
            roles = [u for u in units if not set(u['fact_refs']) & used
                     and any(f['payload'].get('role') == 'material' for f in u['facts'])
                     and (activity in {f['payload'].get('activity') for f in u['facts']}
                          or (u.get('context') or {}).get('activity') == activity)]
            emit(action + roles, lex.pair(wording, locale))
    anchors = select({'anchor_escape_rope'})
    if anchors:
        emit(anchors, '위층 창문 등에 탈출용 로프를 고정할 수 있다' if locale == 'ko' else
             'It can be used to anchor an escape rope at an upper-floor window or similar attachment')

    storage = select({'store_and_retrieve_items', 'carry_stored_items'})
    if len(storage) == 2:
        emit(storage, '물건을 담아 보관하거나 운반할 수 있다' if locale == 'ko' else
             'It can be used to store and carry items')

    attachments = [u for u in units if not set(u['fact_refs']) & used
                   and any(f['payload'].get('role') == 'attachment' for f in u['facts'])
                   and ('spear_upgrade' in {f['payload'].get('activity') for f in u['facts']}
                        or (u.get('context') or {}).get('activity') == 'spear_upgrade')]
    if attachments and not compact:
        text = '제작한 창에 부착해 쓸 수 있다' if locale == 'ko' else 'It can be attached to a crafted spear'
        emit(attachments, text)

    if not compact:
        salvage_tools = [u for u in units if not set(u['fact_refs']) & used
                         and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'tool'}
                         and ({f['payload'].get('activity') for f in u['facts']} | {(u.get('context') or {}).get('activity')}) & {'electronic_salvage', 'radio_salvage'}]
        if salvage_tools:
            activities = {f['payload'].get('activity') for u in salvage_tools for f in u['facts']} | {(u.get('context') or {}).get('activity') for u in salvage_tools}
            both = {'electronic_salvage', 'radio_salvage'} <= activities
            target = ('전자기기(라디오·TV 포함)' if both else '라디오·TV' if 'radio_salvage' in activities else '전자기기') if locale == 'ko' else ('electronic devices, including radios and TVs,' if both else 'radios and TVs' if 'radio_salvage' in activities else 'electronic devices')
            text = (target + '를 분해해 부품을 회수할 수 있다' if locale == 'ko' else
                    'It can be used to dismantle ' + target + ' to recover parts')
            emit(salvage_tools, text)

    # The admitted tool registry is shared by PickUpTool and PlaceTool. It
    # licenses these operations only for furniture requesting this tool;
    # scrap uses a separate registry and is not inferred from this activity.
    for activity, wording in (
        ('moving_furniture', ('일부 가구를 집어 들거나 설치하는 데 사용할 수 있다',
                              'It can be used to pick up or place certain furniture')),
        ('fabric_recovery', ('데님이나 가죽 의류를 잘라 조각을 회수할 수 있다',
                             'It can be used to cut denim or leather clothing into strips')),
    ):
        members = [u for u in units if not set(u['fact_refs']) & used
                   and activity in purpose_tokens(u)
                   and {f['payload'].get('role') for f in u['facts']
                        if f['fact_kind'] == 'context_role'} == {'tool'}]
        if activity == 'fabric_recovery':
            # This admitted role comes from the kept-scissors Denim/Leather
            # recipes. Their callback quantities are not recipe_targets;
            # match the closed fabric predicate instead of inventing targets.
            members = [u for u in members if
                       {plan['qualifiers'][q]['payload']['predicate']
                        for q in u['qualifier_refs']} == {lex.source.FABRIC_ACTION}]
        if activity == 'fabric_recovery':
            emit(members, lex.pair(wording, locale))

    grooming = select({'groom_hair', 'groom_beard'})
    if len(grooming) == 2:
        emit(grooming, lex.pair(('머리와 수염을 손질할 수 있다', 'It can be used to groom hair and beards'), locale))

    moving_targets = traits.get('moving_tool_targets', [])
    if moving_targets:
        members = [u for u in units if not used & set(u['fact_refs']) and purpose_tokens(u) - {None} == {'moving_furniture'}
                   and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'tool'}]
        categories = []
        for target in moving_targets:
            ps = target['properties']; custom, group = ps.get('CustomName'), ps.get('GroupName')
            label = (('벽걸이 보관함', 'wall-mounted storage') if custom in {'Cabinet', 'Locker'} else
                     ('공조 설비', 'air-conditioning units') if custom in {'Conditioner', 'Blower'} else
                     ('오븐', 'ovens') if ps.get('IsoType') == 'IsoStove' else
                     ('위성 접시', 'satellite dishes') if (group, custom) == ('Satellite', 'Dish') else
                     ('묘비', 'gravestones') if custom == 'Gravestone' else
                     ('우편함', 'mailboxes') if (group, custom) == ('Mail', 'Box') else
                     ('세면대', 'sinks') if custom == 'Sink' else ('변기', 'toilets') if custom == 'Toilet' else None)
            if label and label not in categories: categories.append(label)
        if compact or not categories:
            text = '일부 가구나 설비를 옮기거나 설치하는 데 쓸 수 있다' if locale == 'ko' else 'It can be used to move or install certain furnishings and fixtures'
        else:
            noun = parallel_names([lex.pair(t, locale) for t in categories])
            text = noun + ' 같은 가구나 설비를 옮기거나 설치하는 데 쓸 수 있다' if locale == 'ko' else 'It can be used to move or install fixtures such as ' + noun
        modes = {t['mode'] for t in moving_targets}
        if modes == {'pickup'}:
            text = text.replace('옮기거나 설치할 때', '떼어 옮길 때').replace('moving or installing', 'removing')
        elif modes == {'place'}:
            text = text.replace('옮기거나 설치할 때', '설치할 때').replace('moving or installing', 'installing')
        emit(members, text)
    if compact:
        for unit in units:
            if used & set(unit['fact_refs']) or purpose_tokens(unit) - {None} != {'food_portioning'}: continue
            if {f['payload'].get('role') for f in unit['facts'] if f['fact_kind'] == 'context_role'} != {'tool'}: continue
            relations = unit.get('recipe_targets', [])
            inputs = {i['item_id']: i for r in relations for i in r.get('inputs', [])}
            if len(inputs) == 1:
                # Retain the actual input identity when no broader food field
                # is admitted; one recipe does not establish general cooking.
                other_food = any(u is not unit and purpose_tokens(u) & {'animal_butchery', 'fish_preparation', 'frog_preparation', 'food_preparation'} for u in units)
                if not other_food:
                    target = next(iter(inputs.values()))
                    name = target['names'][locale] if locale == 'ko' else en.object_phrase(target)
                    emit([unit], object_name(name) + ' 나누는 데 쓸 수 있다' if locale == 'ko' else 'It can be used to cut up ' + name)

    # Realize each admitted tool purpose independently, then coordinate only
    # compatible tool actions. Unknown purposes, roles and conditions stay out.
    if compact:
        coordinated = []
        domains = (
            ({'animal_butchery', 'fish_preparation', 'food_portioning', 'frog_preparation'}, ('음식 손질', 'prepare food')),
            ({'woodworking', 'construction', 'carpentry_menu_construction'}, ('목공과 건축 작업', 'work wood and build structures')),
            ({'electronic_assembly', 'radio_crafting'}, ('전자기기 제작', 'make electronic devices')),
            ({'electronic_salvage', 'radio_salvage'}, ('전자기기 분해와 부품 회수', 'dismantle electronic devices to recover parts')),
        )
        for activities, phrase in domains:
            members = [u for u in units if not used & set(u['fact_refs'])
                       and purpose_tokens(u) - {None} <= activities and purpose_tokens(u) & activities
                       and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'tool'}]
            if activities == {'woodworking', 'construction', 'carpentry_menu_construction'} and members:
                actual = set().union(*(purpose_tokens(u) for u in members)) - {None}
                if actual == {'woodworking'}: phrase = ('목재 가공', 'work wood')
                elif 'woodworking' not in actual: phrase = ('건축 작업', 'build structures')
            before = len(output)
            emit(members, phrase[0] + '에 쓸 수 있다' if locale == 'ko' else 'It can be used to ' + phrase[1])
            if len(output) > before: coordinated.append((output[-1], members, phrase))
        members = select({'dismantle_built_object'})
        before = len(output)
        emit(members, lex.pair(('설치물 해체에 쓸 수 있다', 'It can be used to dismantle constructed objects'), locale))
        if len(output) > before: coordinated.append((output[-1], members, ('설치물 해체', 'dismantle constructed objects')))
        if len(coordinated) > 1:
            text = (parallel_names([p[0] for _, _, p in coordinated]) + '에 쓸 수 있다' if locale == 'ko' else
                    'It can be used to ' + en.join([p[1] for _, _, p in coordinated]))
            members = [u for _, us, _ in coordinated for u in us]
            frames = [f for f, _, _ in coordinated]
            combined = {**frames[0], 'text': text + '.', **links([dict(u, qualifier_refs=[]) for u in members], plan)}
            output[:] = [combined if f is frames[0] else f for f in output if f is frames[0] or f not in frames]
        # Installation/removal is the same operation over separately named scopes.
        vehicle, weapon = select({'service_vehicle_parts'}), select({'manage_weapon_attachments'})
        if vehicle and weapon:
            emit(vehicle + weapon, lex.pair(('차량 부품과 호환 무기 부착물을 장착하거나 제거하는 데 쓸 수 있다',
                 'It can be used to install or remove vehicle parts and compatible weapon attachments'), locale))

    if compact and attachments and not any(set(u['fact_refs']) & used for u in attachments):
        melee = select({'melee_attack'})
        emit(attachments + melee, ('제작한 창에 부착하거나 무기로 쓸 수 있다' if locale == 'ko' else 'It can be attached to a crafted spear or used as a weapon') if melee else ('제작한 창에 부착해 쓸 수 있다' if locale == 'ko' else 'It can be attached to a crafted spear'))


    barricades = select({'build_wooden_barricade', 'remove_barricade'})
    if barricades:
        actions = {f['payload'].get('function') for u in barricades for f in u['facts']}
        both = len(actions) == 2
        text = (('문과 창문의 판자 바리케이드를 설치하거나 철거할 수 있다' if both else
                 '문과 창문에 판자 바리케이드를 설치할 수 있다' if 'build_wooden_barricade' in actions else '판자 바리케이드를 철거할 수 있다') if locale == 'ko' else
                ('It can be used to install or remove plank barricades on doors and windows' if both else
                 'It can be used to install plank barricades on doors and windows' if 'build_wooden_barricade' in actions else 'It can be used to remove plank barricades'))
        emit(barricades, text)

    bait = select({'supply_trap_bait'})
    if bait:
        eating = [u for u in select({'eat_food', 'consume_edible_food'}) if not u['qualifier_refs']]
        ingredients = [u for u in units if not set(u['fact_refs']) & used and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} <= {lex.source.BEAN_PREPARATION, lex.source.OATMEAL_PREPARATION, lex.source.OMELETTE_PREPARATION}
                       and any(f['payload'].get('role') == 'ingredient' for f in u['facts'])
                       and purpose_tokens(u) & {'food_preparation', 'grain_preparation'}]
        dough_ingredients = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs'] and purpose_tokens(u) & {'batter_preparation', 'cookie_preparation', 'dough_preparation'} and any(f['payload'].get('role') == 'ingredient' for f in u['facts'])]
        bases = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs'] and 'food_ingredient_addition' in purpose_tokens(u)]
        text = ('덫의 미끼로 쓸 수 있다' if locale == 'ko' else
                'It can be used as trap bait')
        if compact and eating and not ingredients:
            text = ('먹을 수 있다. 덫의 미끼로도 쓸 수 있다' if locale == 'ko' else
                    'It can be eaten. It can also be used as trap bait')
            bait = eating + bait
        if compact and eating and ingredients:
            text = ('먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다' if locale == 'ko' else
                    'It can be eaten or used as a cooking ingredient. It can also be used as trap bait')
            bait = eating + ingredients + bait
        if compact and eating and bases:
            text = ('먹거나 다른 재료를 더해 요리할 수 있다.' + (' 요리 재료로도 쓸 수 있다.' if ingredients else '') + ' 덫의 미끼로도 쓸 수 있다') if locale == 'ko' else ('It can be eaten or combined with ingredients to prepare food.' + (' It can also be used as a cooking ingredient.' if ingredients else '') + ' It can also be used as trap bait')
            bait = eating + ingredients + bases + select({'supply_trap_bait'})
        if compact and eating and dough_ingredients:
            dough_tokens = set().union(*(purpose_tokens(u) for u in dough_ingredients))
            dough_label = 'dough or batter' if 'batter_preparation' in dough_tokens and dough_tokens & {'cookie_preparation', 'dough_preparation'} else 'batter' if 'batter_preparation' in dough_tokens else 'dough'
            if not ingredients:
                text = ('먹거나 반죽 준비 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다') if locale == 'ko' else ('It can be eaten or used as an ingredient for ' + dough_label + ' preparation. It can also be used as trap bait')
            bait += dough_ingredients
        emit(bait, text)

    construction = [u for u in units if not set(u['fact_refs']) & used and (
        any(f['payload'].get('activity') in {'construction', 'carpentry_menu_construction'} for f in u['facts'])
        or (u.get('context') or {}).get('activity') in {'construction', 'carpentry_menu_construction'})]
    if construction:
        roles = sorted({f['payload']['role'] for u in construction for f in u['facts'] if f['fact_kind'] == 'context_role'})
        grammar = ko if locale == 'ko' else en
        text = grammar.role([lex.context('construction', locale)], roles) if roles else (
            '건축 작업에 쓸 수 있다' if locale == 'ko' else 'It can be used for construction')
        emit(construction, text)

    reading = select({'read_literature'})
    moods = [u for u in units if not set(u['fact_refs']) & used and all(
        f['fact_kind'] == 'effect' and f['payload'].get('direction') == 'cap_at_reading_start'
        and f['payload'].get('property') in {'boredom', 'stress', 'unhappiness'} for f in u['facts'])]
    if reading and moods:
        labels = {'boredom': ('지루함', 'boredom'), 'stress': ('스트레스', 'stress'), 'unhappiness': ('불행', 'unhappiness')}
        names = [lex.pair(labels[f['payload']['property']], locale) for u in moods for f in u['facts']]
        subject = '·'.join(names)
        particle = '이' if (ord(subject[-1]) - ord('가')) % 28 else '가'
        text = ('독서 중 ' + subject + particle + ' 더 심해지는 것을 막을 수 있다') if locale == 'ko' else (
            'Reading can keep ' + en.join(names) + ' from worsening beyond their starting levels')
        emit(reading + moods, text)

    if reading and not moods and not any(f['payload'].get('property', '').endswith('_experience_multiplier')
                                        for u in units for f in u['facts']):
        emit(reading, '읽을 수 있다' if locale == 'ko' else 'It can be read')

    installing = select({fn for fn in lex.FUNCTIONS if fn.startswith('install_vehicle_')})
    for unit in installing:
        emit([unit], lex.core(unit['facts'][0], locale))

    washing = select({'wash_body', 'wash_equipment'})
    if washing:
        functions = {f['payload'].get('function') for u in washing for f in u['facts']}
        targets = []
        if 'wash_body' in functions: targets.append(('몸', 'the body'))
        if 'wash_equipment' in functions: targets.extend([('의류', 'clothing'), ('장비', 'equipment')])
        emit(washing, ('몸과 의류, 장비를 물로 씻을 때 세척제로 사용할 수 있다' if len(targets) == 3 else '의류와 장비' if len(targets) == 2 else targets[0][0] + '를 물로 씻을 때 세척제로 사용할 수 있다')
             if locale == 'ko' else 'It can be used as a cleaning supply for washing ' + en.join([t[1] for t in targets]) + ' with water')
    supplies_frames.render(assembly, compact_recovery=compact_recovery, rope_uses=rope_uses)
    if len(material_frames) > 1:
        original_frames = material_frames
        if compact:
            # A general work field can represent material use in the overview.
            # Concrete recipe outputs stay in Expanded; they are not asserted
            # to be subtypes of construction or woodworking. Unknown purposes
            # do not acquire a lower display depth merely by being numerous.
            work_fields = {'woodworking', 'furniture_crafting', 'construction',
                           'carpentry_menu_construction', 'metal_welding_construction', 'welded_parts',
                           'metal_forging', 'shovel_smithing', 'smithing_parts'}
            product_fields = {'spear_crafting', 'trap_crafting', 'fishing_gear_crafting',
                              'campfire_kit_preparation', 'mattress_preparation', 'tent_kit_making',
                              'camping_kit_preparation', 'tool_crafting', 'stone_tool_crafting',
                              'metal_forging', 'hat_crafting', 'splint_crafting', 'supply_drum_logs'}
            def frame_tokens(frame):
                return set().union(*(purpose_tokens(u) for u in frame[1])) - {None}
            general_work = any(frame_tokens(frame) & work_fields and
                               all(kind == 'action' for kind, _ in frame[2]) for frame in material_frames)
            if general_work:
                material_frames = [frame for frame in material_frames if not (
                    frame[2] and all(kind == 'craft' for kind, _ in frame[2]) and
                    frame_tokens(frame) and frame_tokens(frame) <= product_fields)]
        purposes = [p for _, _, ps in material_frames for p in ps]
        crafting = list(dict.fromkeys(name for kind, name in purposes if kind == 'craft'))
        actions = list(dict.fromkeys(name for kind, name in purposes if kind == 'action'))
        if compact:
            # Related production and modification share their device domain.
            # A device-only material keeps its more informative product names.
            modification = lex.pair(('장치 개조', 'modifying devices'), locale)
            if modification in actions:
                device_frames = [frame for frame in material_frames if frame[2] and
                                 all(kind == 'craft' for kind, _ in frame[2]) and
                                 frame_tokens(frame) and frame_tokens(frame) <= {
                                     'electronic_assembly', 'radio_crafting', 'explosive_assembly'}]
                device_names = {name for frame in device_frames for _, name in frame[2]}
                if device_names:
                    crafting = [name for name in crafting if name not in device_names]
                    actions = [lex.pair(('장치 제작·개조', 'making and modifying devices'), locale)
                               if name == modification else name for name in actions]
            # Outdoor activities share a concrete purpose. General tools stay
            # outside this category, so its modifier cannot narrow their use.
            outdoor = {'spear_crafting', 'trap_crafting', 'fishing_gear_crafting',
                       'campfire_kit_preparation', 'mattress_preparation', 'tent_kit_making',
                       'camping_kit_preparation'}
            outdoor_frames = [frame for frame in material_frames if frame[2] and
                              all(kind == 'craft' for kind, _ in frame[2]) and
                              frame_tokens(frame) and frame_tokens(frame) <= outdoor]
            outdoor_names = {name for frame in outdoor_frames for _, name in frame[2]}
            if len(outdoor_names) > 1:
                # Place any unmodified tool category before the qualified
                # outdoor category; the latter must not qualify both nouns.
                crafting = [name for name in crafting if name not in outdoor_names]
                crafting.append(lex.pair(('야외 활동 장비', 'outdoor equipment'), locale))
        clauses = []
        if actions:
            clauses.append(parallel_names(actions) + '에 재료로 쓸 수 있다' if locale == 'ko' else 'It can be used as material for ' + en.coordinated_actions(actions))
        if crafting:
            clauses.append(object_name(parallel_names(crafting)) + (' 만들 때도 쓸 수 있다' if compact and actions else ' 만드는 재료로 쓸 수 있다') if locale == 'ko' else ('It can also be used to make ' if compact and actions else 'It can supply material for making ') + parallel_names(crafting))
        members = []
        for _, group, _ in material_frames:
            members.extend(u for u in group if u not in members)
        originals = [segment for segment, _, _ in original_frames]
        combined = {'text': '. '.join(clauses) + '.', **links([dict(u, qualifier_refs=[]) for u in members], plan),
                    'expression': 'public_use', 'placement_reason': ('representative work fields and related purpose domains; concrete recipe fields remain in Expanded' if compact else 'parallel material purposes share their role; no sequence or causal relation is implied'), 'qualifier_dispositions': []}
        combined['use_order'] = list(dict.fromkeys(r for _, group, _ in original_frames for u in group for r in u['fact_refs']))
        output = [combined if segment is originals[0] else segment for segment in output if segment is originals[0] or segment not in originals]
    return output, used


# These predicates describe availability, bookkeeping or the tautological
# requirement to meet the same named recipe. Their full evidence remains in
# the item record, but neither public surface repeats them as item utility.
INTERNAL_QUALIFIERS = {
    lex.source.BOX_PACKING, lex.source.SEED_PACKING, lex.source.MATTRESS_PREPARATION,
    lex.source.BANDAGE_RECIPE_WASHING, lex.source.GRAIN_VESSEL_PREPARATION,
    lex.source.LOG_BINDING, lex.source.MOLOTOV_ASSEMBLY, lex.source.PLASTER_MIXING,
    lex.source.POULTICE_PREPARATION, lex.source.SHOTGUN_SHORTENING,
    lex.source.SPRAY_PREPARATION, lex.source.OATMEAL_PREPARATION,
    lex.source.OMELETTE_PREPARATION, lex.source.CAKE_PAN_PREPARATION, lex.source.EGG_PACKING,
    lex.source.SPEAR_CONDITIONS['spear_upgrade'],
    lex.source.SPEAR_CONDITIONS['spear_crafting'],
    lex.source.MATERIAL_ASSEMBLY, lex.source.ROPE_MAKING,
    lex.source.MELEE, lex.source.PHYSICS_ATTACK,
    lex.source.WEIGHT_EXERCISE, lex.source.WOOD_SHAPING, lex.source.FOOD_SLICING,
    lex.source.SANDWICH_PREPARATION, lex.source.WELDING_CONSTRUCTION,
    lex.source.CARPENTRY_MATERIAL, lex.source.DEVICE_ASSEMBLY, lex.source.TRAP_ASSEMBLY, lex.source.ANIMAL_PREPARATION,
    lex.source.SAWN_WOOD, lex.source.TENT_KIT_PREPARATION, lex.source.BOWL_PORTIONING, lex.source.RADIO_CRAFTING, lex.source.SIMPLE_TRANSFORMATION,
    lex.source.FORGE_PREPARATION, lex.source.SHOVEL_SMITHING, lex.source.SMITHING_PARTS,
    lex.source.CARRYING, lex.source.WEARING, lex.source.WEAR_ACTION,
    lex.PILL_INVENTORY, lex.source.PILL_TAKING,
    lex.source.FOOD_ASSEMBLY, lex.source.CAMP_KIT_PREPARATION, lex.source.BAKING,
    lex.source.COOKING_BASE, lex.source.CHARGER_PLACEMENT, lex.source.GENERATOR_HANDLING,
    lex.source.CONSUMING, lex.source.COOKING_ACTION, lex.COOKING_ELIGIBILITY, lex.source.BATTER_TEST,
    lex.source.BANDAGE_MATERIALS, lex.source.NOTE_LIMITS,
    'The object requests this tool; inventory, reachability, world object and multiplayer permission checks must hold.',
    'A supported woodworking transformation must have its inputs, tools, skill and recipe eligibility requirements satisfied.',
    'The clothing is in the character inventory and is worn at its configured body location.',
}


def prepare(plan):
    public = deepcopy(plan)
    public['units'] = []
    public['dispositions'] = []
    functions = {f['payload'].get('function') for u in plan['units'] for f in u['facts']}
    # Splitting/serving an input food is processing detail, even when no
    # separate eating/cooking fact is admitted. This licenses no inferred
    # replacement use. Tool roles, receiving vessels and result relations stay.
    upper_food = bool(functions & {'eat_food', 'consume_edible_food', 'drink_food_contents'}) or any(
        purpose_tokens(u) & {'food_preparation', 'food_ingredient_addition'} for u in plan['units'])
    lower_food_refs = set()
    for relation in plan.get('use_relations', []):
        portion_input = relation.get('activity') == 'food_portioning' and (
            relation['input_role'] == 'ingredient' or
            (relation['input_role'] == 'material' and 'portion_into_bowls' in functions))
        opened_recipe = (relation.get('activity') == 'food_preparation' and
                         relation['input_role'] == 'ingredient' and 'unpack_canned_food' in functions)
        processing_input = relation.get('activity') in {'watermelon_breaking', 'pumpkin_carving'} and relation['input_role'] in {'ingredient', 'material'}
        if relation['function'] == 'recipe_use' and upper_food and (portion_input or processing_input or opened_recipe):
            lower_food_refs.update(relation['fact_refs'])
    welding_tool = any('metal_welding_construction' in purpose_tokens(u)
                       and any(f['payload'].get('role') == 'tool' for f in u['facts']) for u in plan['units'])
    for unit in deepcopy(plan['units']):
        # An item may repair another item and also be repairable itself.
        # Keep the material role while preserving the target role internally.
        targets = [f for f in unit['facts'] if f['payload'] == {'role': 'repair_target'}]
        others = [f for f in unit['facts'] if f['fact_kind'] == 'context_role' and f not in targets]
        if targets and others:
            refs = {f['fact_ref'] for f in targets}
            public['dispositions'].append({'fact_refs': sorted(refs), 'disposition': 'self-management',
                                          'reason': 'repair-target role is separate from the repair-material use'})
            unit['facts'] = [f for f in unit['facts'] if f not in targets]
            unit['fact_refs'] = [r for r in unit['fact_refs'] if r not in refs]
        category, reason = disposition(unit)
        supplied_functions = {f['payload'].get('function') for f in unit['facts']}
        if supplied_functions & {'operate_installed_vehicle_door', 'operate_installed_vehicle_lock', 'operate_installed_vehicle_window'}:
            category, reason = 'self-management', 'installed part operation does not add an independent replacement-part purpose'
        if supplied_functions == {'remove_placed_furniture'}:
            category, reason = 'self-management', 'moving this furnishing is a placement operation, not a separate use'
        evidence = plan.get('source_traits', {}).get('purpose_evidence', {})
        if supplied_functions == {'toggle_radio_microphone'} and evidence.get('speech_transmission'):
            category, reason = 'use', 'admitted two-way microphone control joins the reviewed native speech transmission and reception path'
        if supplied_functions & {'set_alarm', 'stop_alarm'} and evidence.get('digital_alarm') is False:
            category, reason = 'internal', 'reviewed native constructor makes the admitted isDigital condition false'
        if supplied_functions == {'supply_trap_bait'} and 'accepted_animals' in evidence and not evidence['accepted_animals']:
            category, reason = 'internal', 'bait insertion retained; no animal acceptance joins its exact transmitted type in the bound local definitions'

        furnishing = (plan.get('source_traits', {}).get('DisplayCategory') == 'Furniture'
                      and plan.get('source_traits', {}).get('Type') == 'Moveable'
                      and bool(plan.get('source_traits', {}).get('WorldObjectSprite'))
                      and 'pickup_floor_glass' not in functions)
        if supplied_functions & {'place_moveable_furniture', 'remove_placed_furniture'} and not furnishing:
            category, reason = 'self-management', 'placement or removal alone establishes no independent supplied purpose'
        if 'remove_installed_escape_rope' in supplied_functions:
            category, reason = 'self-management', 'removing the rope does not add a supplied climbing use'
        bowl_substep = (upper_food and 'portion_into_bowls' in functions and
                       ('food_portioning' in purpose_tokens(unit) or supplied_functions == {'portion_into_bowls'}))
        if set(unit['fact_refs']) <= lower_food_refs or bowl_substep:
            category, reason = 'internal', 'food input splitting/processing detail; independent admitted uses, tool roles and receiving vessels remain separate'
        if 'moving_furniture' in purpose_tokens(unit) and not plan.get('source_traits', {}).get('moving_tool_targets'):
            category, reason = 'internal', 'tool registry participation only; concrete PickUpTool/PlaceTool furniture mappings are unconfirmed in admitted repository inputs'
        if supplied_functions & {'serve_as_eating_utensil', 'satisfy_vehicle_mechanics_key'}:
            category, reason = 'internal', 'optional meal implement or mechanics prerequisite, not an independent supplied purpose'
        if all(f['payload'] == {'property': 'item_condition', 'direction': 'decrease'} for f in unit['facts']) and any(
                plan['qualifiers'][q]['payload']['predicate'] == lex.source.SPEAR_FISHING_WEAR for q in unit['qualifier_refs']):
            category, reason = 'internal', 'generic wear bookkeeping; unresolved relation remains unresolved'
        if 'install_vehicle_tire' in functions and any(
                f['payload'].get('function') in {'inflate_vehicle_tire', 'deflate_vehicle_tire'} for f in unit['facts']):
            category, reason = 'self-management', 'this installed tire receives air service; the pump retains its supplied inflation use'
        if 'control_installed_generator' in functions and any(
                f['payload'].get('function') in {'repair_generator', 'refuel_generator'} for f in unit['facts']):
            category, reason = 'self-management', 'the installed-generator subject is being serviced; supplied scrap and fuel keep their independent uses'
        if any(plan['qualifiers'][q]['payload']['predicate'] == lex.source.DISINFECTION_ADMIN_PAIN for q in unit['qualifier_refs']):
            category, reason = 'internal', 'administrative treatment override, not an ordinary supplied use'
        public['dispositions'].append({'fact_refs': unit['fact_refs'], 'disposition': category, 'reason': reason})
        if category in {'internal', 'self-management'}:
            continue
        retained = []
        for qref in unit['qualifier_refs']:
            q = plan['qualifiers'][qref]
            sheet_results = {result['item_id'] for relation in plan.get('use_relations', [])
                             if relation.get('function') == 'recipe_use' and set(relation['fact_refs']) <= set(unit['fact_refs'])
                             for result in relation.get('results', [])}
            roles = {f['payload'].get('role') for f in unit['facts']}
            unrelated_sheet_conversion = (q['payload']['predicate'] == lex.source.WELDED_PARTS
                                          and (welding_tool or 'tool' in roles or not sheet_results & {'Base.SheetMetal', 'Base.SmallSheetMetal'}))
            other_food_state = (q['payload']['predicate'] == lex.source.BEAN_PREPARATION
                                and 'ingredient' in roles and 'unpack_canned_food' not in functions)
            vessel_recipe_details = (roles & {'container', 'base'} and q['payload']['predicate'] in {
                lex.source.BEAN_PREPARATION, lex.source.OATMEAL_PREPARATION, lex.source.OMELETTE_PREPARATION,
                })
            tool_recipe_details = ('tool' in roles and q['payload']['predicate'] in {
                lex.source.COOKED_SLICING, lex.source.DOUGH_SLICING, lex.source.PIZZA_SLICING,
                lex.source.FISH_PREPARATION, lex.source.FROG_PREPARATION})
            if q['payload']['predicate'] in INTERNAL_QUALIFIERS | {lex.source.MIC_CONTROL} or unrelated_sheet_conversion or other_food_state or vessel_recipe_details or tool_recipe_details:
                public['dispositions'].append({'fact_refs': q['fact_refs'], 'disposition': 'internal',
                    'applies_to_fact_refs': unit['fact_refs'],
                    'reason': 'general execution or redundant named-activity eligibility, not a distinguishing use condition'})
            else:
                if q['payload']['predicate'] not in lex.USE_QUALIFIERS:
                    raise ValueError('unclassified public qualifier: ' + q['payload']['predicate'])
                retained.append(qref)
                public['dispositions'].append({'fact_refs': q['fact_refs'],
                    'applies_to_fact_refs': unit['fact_refs'],
                    'disposition': 'supporting detail' if lex.public_qualifier(q) else 'internal',
                    'reason': 'explicit consumption consequence' if lex.public_qualifier(q) else
                              'scoped evidence for use selection; eligibility, arithmetic and procedure are not public utility'})
        unit['qualifier_refs'] = retained
        unit['subject_names'] = plan.get('source_traits', {}).get('display_names', {})
        unit['public_disposition'] = category
        # The prior detail ranking hid independently admitted crafting uses.
        # Public results retain their own conditions instead of being promoted
        # only when there happens to be no other available text.
        unit['detail_reason'] = reason if category == 'supporting detail' else None
        unit['recipe_targets'] = [r for r in plan.get('use_relations', [])
                                  if r['function'] == 'recipe_use' and set(r['fact_refs']) <= set(unit['fact_refs'])]
        public['units'].append(unit)
    # Once purely procedural conditions are internal, a context and its roles
    # may have exactly the same remaining scope. Coalesce only that source
    # branch, retaining every anchor and relation rather than repeating it.
    merged = []
    taken = set()
    for n, unit in sorted(enumerate(public['units']), key=lambda entry:
            not any(f['fact_kind'] == 'use_context' for f in entry[1]['facts'])):
        if n in taken:
            continue
        contexts = {f['payload'].get('activity') for f in unit['facts'] if f['fact_kind'] == 'use_context'}
        siblings = []
        if contexts:
            siblings = [(m, other) for m, other in enumerate(public['units']) if m != n and m not in taken
                and other['branch_refs'] == unit['branch_refs'] and other['qualifier_refs'] == unit['qualifier_refs']
                and (other.get('context') or {}).get('activity') in contexts
                and any(f['fact_kind'] == 'context_role' for f in other['facts'])]
        for m, other in siblings:
            taken.add(m)
            unit['facts'].extend(other['facts'])
            for field in ('fact_refs', 'block_refs', 'branch_refs', 'relation_refs'):
                unit[field] = sorted(set(unit[field]) | set(other[field]))
        unit['recipe_targets'] = [r for r in plan.get('use_relations', [])
            if r['function'] == 'recipe_use' and set(r['fact_refs']) <= set(unit['fact_refs'])]
        merged.append(unit)
        taken.add(n)
    public['units'] = merged
    return public


def arrange(segments, plan):
    units = plan['units']
    def tokens(segment):
        return set().union(*(purpose_tokens(u) for u in units
                           if set(u['fact_refs']) & set(segment.get('use_order', segment['fact_refs'])))) - {None}
    arranged = adjacent(segments, tokens)
    forms = [s for s in arranged if tokens(s) == {'switch_declared_clothing_form'}]
    if forms:
        arranged = [s for s in arranged if s not in forms]
        at = next((n + 1 for n, s in enumerate(arranged) if tokens(s) & {'wear_on_body', 'wear_configured_clothing', 'worn_location'}), 0)
        arranged[at:at] = forms
    # Burning the item is a separate consumption context. Keep it after the
    # item's other uses, without splitting frames that summarize both.
    return sorted(arranged, key=lambda s: bool(tokens(s)) and tokens(s) <= FUEL.keys() | TINDER.keys())


def finish_units(segments, plan, locale):
    """Bind supporting clauses only to a confirmed purpose, before projection.

    References are evidence, not a reason to fuse independent activities.
    Unresolved relations never license a causal attachment.
    """
    facts = {f['fact_ref']: f for u in plan['units'] for f in u['facts']}
    support = {r for u in plan['units'] if u.get('public_disposition') == 'supporting detail'
               or any(f['payload'].get('property') == 'fishing_rod_form' for f in u['facts'])
               or (all(f['fact_kind'] == 'effect' for f in u['facts']) and any(
                   plan['qualifiers'][q]['payload']['predicate'] == lex.source.SPEAR_STONE_LOSS for q in u['qualifier_refs']))
               for r in u['fact_refs']}
    removed = set()
    following = {}
    for n, segment in enumerate(segments):
        anchors = set(segment['fact_refs']) & facts.keys()
        if not anchors or not anchors <= support:
            continue
        predicates = {plan['qualifiers'][q]['payload']['predicate'] for q in segment['qualifier_refs']}
        # These admitted predicates name the tool's own spear-crafting use;
        # the unresolved fishing wear predicate is intentionally excluded.
        activity = 'spear_crafting' if predicates & {lex.source.SPEAR_TOOL_WEAR, lex.source.SPEAR_STONE_LOSS} else None
        named_function = 'apply_bandage' if lex.source.BANDAGE_INFECTION in predicates else None
        if any(facts[r]['payload'].get('property') == 'fishing_rod_form' for r in anchors):
            named_function = 'fish_with_rod'
        candidates = []
        for m, other in enumerate(segments):
            if m == n or m in removed:
                continue
            other_anchors = set(other['fact_refs']) & facts.keys()
            if not other_anchors - support:
                continue
            linked = any(r['kind'] == 'result' and anchors <= set(r.get('fact_refs', []))
                         and other_anchors & set(r.get('fact_refs', [])) for r in plan['relations'])
            named = activity and any(facts[r]['payload'].get('activity') == activity for r in other_anchors)
            named = named or (named_function and any(facts[r]['payload'].get('function') == named_function for r in other_anchors))
            if linked or named:
                candidates.append(m)
        if len(candidates) == 1:
            segment['continues_use'] = True
            following.setdefault(candidates[0], []).append(segment)
            removed.add(n)
    output = [s for n, segment in enumerate(segments) if n not in removed
              for s in [segment, *following.get(n, [])]]
    # Put the original item's independent uses before these transformations.
    # This keeps recovered results from becoming the apparent subject of a
    # following use, without inventing an intact/unbroken prerequisite.
    transformed = {ref for relation in plan.get('use_relations', [])
                   if (relation.get('activity') in {'bottle_breaking', 'ammunition_disassembly', 'spear_reclaim'}
                       or relation['function'] == 'dismantle_electronics')
                   and relation['input_role'] == 'transformation_target'
                   for ref in relation['fact_refs']}
    transformed.update(ref for unit in plan['units'] if 'spear_reclaim' in purpose_tokens(unit)
                       and any(f['payload'].get('role') == 'transformation_target' for f in unit['facts'])
                       for ref in unit['fact_refs'])
    transformed.update(f['fact_ref'] for unit in plan['units'] for f in unit['facts']
                       if f['payload'].get('function', '').startswith('placed_purpose_salvage_'))
    groups = []
    for segment in output:
        if segment.get('continues_use') and groups:
            groups[-1].append(segment)
        else:
            groups.append([segment])
    groups.sort(key=lambda group: any(set(segment['fact_refs']) & transformed for segment in group))
    output = [segment for group in groups for segment in group]
    return output
