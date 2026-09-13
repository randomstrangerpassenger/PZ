"""Public use frames over structured A relations and admitted participant roles.

Execution evidence stays in the input. Only claims actually expressed are linked
as public facts; no procedure refs are attached to a shorter unrelated sentence.
"""
from copy import deepcopy
from . import description_composition_lexicon as lex
from . import description_composition_en as en
from . import description_composition_ko as ko

MAINTENANCE = {'wash_carried_equipment', 'receive_garment_patch', 'remove_garment_patch',
               'rename_selected_item', 'rename_prepared_food'}
WASH_RESULTS = {'item_surface_blood', 'clothing_surface_dirt', 'clothing_wetness',
                'washed_surface_blood', 'washed_surface_dirt', 'food_chef_attribution'}
FUEL = {'supply_campfire_fuel': ('모닥불', 'campfires'),
        'supply_hearth_fuel': ('비프로판 바비큐·벽난로', 'non-propane barbecues and fireplaces'),
        'supply_furnace_fuel': ('화로', 'furnaces')}
TINDER = {'provide_campfire_tinder': ('모닥불', 'campfires'),
          'provide_hearth_tinder': ('비프로판 바비큐·벽난로', 'non-propane barbecues and fireplaces'),
          'provide_industrial_tinder': ('통나무가 든 드럼', 'drums containing logs')}

# Local relationships between already admitted purposes. These have no public
# category label or priority: unrelated uses retain their original traversal.
# A chain controls adjacency only; its members remain independent uses.
PURPOSE_NEIGHBORS = (
    ('wear_on_body', 'wear_configured_clothing', 'worn_location', 'reload_speed_setting', 'switch_declared_clothing_form', 'fabric_recovery', 'sheet_rope_making'),
    ('eat_food', 'consume_edible_food', 'drink_food_contents', 'food_preparation',
     'food_ingredient_addition', 'batter_preparation',
     'cookie_preparation', 'dough_preparation', 'receive_portioned_food', 'supply_trap_bait'),
    ('stitch_wound', 'remove_embedded_glass', 'remove_embedded_bullet', 'clean_burn',
     'apply_bandage', 'apply_splint', 'apply_poultice', 'bandaging_material_preparation', 'splint_crafting'),
    ('apply_garment_patch', 'unpick_garment_patch'),
    ('groom_hair', 'groom_beard'),
    ('electronic_assembly', 'radio_crafting', 'electronic_salvage', 'radio_salvage', 'convert_lamp_to_battery'),
    ('woodworking', 'construction', 'carpentry_menu_construction', 'held_stone_hammer_condition', 'moving_furniture',
     'dismantle_built_object', 'build_wooden_barricade', 'remove_barricade'),
    ('service_vehicle_parts', 'manage_weapon_attachments', 'spear_upgrade', 'melee_attack'),
    ('store_water', 'carry_water', 'receive_poured_water', 'pour_water_into_container'),
    ('view_item_map', 'reveal_item_map_area', 'annotate_item_map', 'erase_item_map_annotations'),
    ('write_note_pages', 'annotate_map'),
    (*FUEL, *TINDER),
)


def purpose_tokens(unit):
    return {f['payload'].get(key) for f in unit['facts'] for key in ('function', 'activity', 'state', 'property')} | {
        (unit.get('context') or {}).get('activity')}


def adjacent(entries, tokens):
    """Make confirmed neighboring purposes contiguous without ranking others."""
    result = list(entries)
    for chain in PURPOSE_NEIGHBORS:
        selected = [(n, e) for n, e in enumerate(result) if tokens(e) & set(chain)]
        if len(selected) < 2:
            continue
        positions = {n for n, _ in selected}
        ordered = sorted((e for _, e in selected), key=lambda e: min(
            chain.index(token) for token in tokens(e) & set(chain)))
        first = selected[0][0]
        result = [e for n, e in enumerate(result) if n < first] + ordered + [
            e for n, e in enumerate(result) if n > first and n not in positions]
    return result


# Selection belongs to the shared plan, before either language or surface.
# These are meanings of admitted payloads, not item-name or prose heuristics.
SELF_FUNCTIONS = MAINTENANCE | {
    'control_sheet_curtain',
    'consolidate_drainable_supplies', 'dump_contents', 'dump_water',
    'adjust_device_volume', 'control_device_headphones', 'edit_radio_presets',
    'insert_device_battery', 'remove_device_battery', 'open_device_controls',
    'toggle_radio_microphone', 'toggle_device_power', 'toggle_activation',
    'accept_battery_charge', 'reset_remote_id', 'inspect_generator',
    'remove_applied_bandage', 'remove_applied_splint',
    'extinguish_on_unequip', 'extinguish_candle', 'fold_umbrella', 'unfold_umbrella',
    'connect_to_vehicle_battery_charger', 'place_vehicle_battery_charger',
    'load_firearm_rounds', 'unload_firearm_rounds', 'receive_firearm_magazine',
    'eject_firearm_magazine', 'rack_firearm', 'change_firearm_mode',
    'receive_weapon_upgrade', 'detach_weapon_upgrade', 'use_alternate_reload_controls',
    'control_installed_generator', 'handle_generator',
    'place_radio_world_form', 'read_recorded_media_label',
}
INTERNAL_PROPERTIES = WASH_RESULTS | {
    'treatment_panic', 'additional_pain',
    'written_note_title', 'written_note_pages', 'written_note_lock',
    'reading_page_progress', 'doctor_experience', 'food_preservation_age',
    'fish_size_nutrition', 'installed_vehicle_part_condition',
    'splint_factor', 'poultice_factor', 'applied_bandage_life', 'crop_water_level',
    'installed_vehicle_battery_charge',
}
SUPPORTING_PROPERTIES = {'splint_factor', 'poultice_factor', 'applied_bandage_life',
    'item_condition', 'held_stone_hammer_condition',
    'additional_pain', 'treatment_panic', 'bandage_patient_infection',
    'installed_vehicle_part_condition', 'installed_tire_air_or_attachment',
    'installed_vehicle_battery_charge', 'crop_water_level', 'burn_wash_requirement'}
INTERNAL_STATES = {'reading_page_count', 'skill_book_progress_step'}


CONSTRUCTION_PREDICATES = {
    lex.source.STAGE_ACTION,
    'Only for a compatible previous construction stage, with required skills, tools and materials available; material consumption excludes construction cheat mode.',
    'For the active wooden-cross branch, the hammer is not broken and world placement/material requirements hold.',
    'For the active wooden-cross or log-wall branch requiring this material; log-wall binding chooses sufficient sheets (clean/dirty), otherwise twine, otherwise rope. World placement and material availability must hold; cheat mode does not consume material.',
}


# These target restrictions remain in expanded on their original recipe scope.
# Compact states each tool purpose once instead of splitting identical roles.
TOOL_DETAIL_PREDICATES = {
    lex.source.COOKED_SLICING, lex.source.DOUGH_SLICING, lex.source.PIZZA_SLICING,
    lex.source.FISH_PREPARATION, lex.source.FROG_PREPARATION,
    lex.source.ELECTRONIC_SALVAGE, lex.source.RADIO_DISMANTLING, lex.source.SCRAP_RECOVERY,
    lex.source.FABRIC_ACTION,
    "An eligible fabric or named sheet is supplied to the recipe; recovered material and quantity depend on fabric, covered parts, dirt/blood and tailoring state.",
    lex.source.OMELETTE_PREPARATION, lex.source.SPEAR_CONDITIONS['spear_crafting'],
}


def activity_labels(unit, locale, compact=False):
    contexts = list(dict.fromkeys(f['payload']['activity'] for f in unit['facts'] if f['fact_kind'] == 'use_context'))
    if not contexts and unit.get('context'):
        contexts = [unit['context']['activity']]
    roles = {f['payload'].get('role') for f in unit['facts']}
    if 'tool' in roles and contexts == ['moving_furniture']:
        return [lex.pair(('일부 가구 집기와 설치', 'picking up or placing certain furniture'), locale)]
    if 'tool' in roles and contexts == ['fabric_recovery'] and all(
            f.get('admission_rule_ref') == 'fabric_conditions' for f in unit['facts']):
        return [lex.pair(('데님이나 가죽 의류의 조각 회수', 'recovering strips from denim or leather clothing'), locale)]
    relations = unit.get('recipe_targets', [])
    targets = {r['item_id']: r['names'][locale] for relation in relations
               for r in relation['results'] if r['kind'] == 'declared'}
    exact = bool(targets) and all(len(r['results']) == 1 and r['results'][0]['kind'] == 'declared'
                                  for r in relations)
    if contexts == ['electronic_assembly']:
        if exact and len(targets) == 1:
            name = next(iter(targets.values()))
            return [name + ' 제작' if locale == 'ko' else 'making ' + name]
        if exact and set(targets) <= {'Base.RemoteCraftedV1', 'Base.RemoteCraftedV2', 'Base.RemoteCraftedV3'}:
            return [lex.pair(('원격제어 조정기 제작', 'making remote controllers'), locale)]
        return [lex.pair(('전자 부품 제작', 'electronic-component crafting'), locale)]
    if exact and contexts == ['explosive_assembly']:
        if len(targets) == 1:
            name = next(iter(targets.values()))
            return [name + ' 제작' if locale == 'ko' else 'making ' + name]
        labels = []
        fire = {'Base.FlameTrap', 'Base.Molotov'}
        remotes = {'Base.RemoteCraftedV1', 'Base.RemoteCraftedV2', 'Base.RemoteCraftedV3'}
        remaining = dict(targets)
        for family, label in ((fire, ('화염 장치', 'incendiary devices')),
                              (remotes, ('원격제어 조정기', 'remote controllers'))):
            if set(remaining) & family:
                labels.append(lex.pair(label, locale))
                remaining = {k: v for k, v in remaining.items() if k not in family}
        for family, label in (({'Base.SmokeBomb'}, ('연막 장치', 'smoke devices')),
                              ({'Base.PipeBomb', 'Base.Aerosolbomb'}, ('폭발 장치', 'explosive devices')),
                              ({'Base.NoiseTrap'}, ('소음 발생 장치', 'noise-making devices'))):
            if set(remaining) & family:
                labels.append(lex.pair(label, locale))
                remaining = {k: v for k, v in remaining.items() if k not in family}
        labels.extend(remaining.values())
        return [((', '.join(labels) + ' 제작') if locale == 'ko' else 'making ' + en.join(labels))]
    if exact and len(targets) == 1 and contexts == ['metal_forging'] and roles & {'material', 'tool'}:
        name = next(iter(targets.values()))
        return [name + ' 단조' if locale == 'ko' else 'forging ' + name]
    if contexts == ['bandaging_material_preparation']:
        if exact and set(targets) == {'Base.AlcoholedCottonBalls'}:
            return [lex.pair(('소독솜 준비', 'preparing disinfected cotton balls'), locale)]
        if exact and set(targets) <= {'Base.AlcoholBandage', 'Base.AlcoholRippedSheets'}:
            return [lex.pair(('붕대 재료 소독', 'disinfecting bandaging material'), locale)]
        if not targets:
            return [lex.pair(('붕대 재료 소독', 'disinfecting bandaging material'), locale)]
    if contexts == ['grain_preparation'] and unit.get('subject_names') and 'ingredient' in roles:
        return [lex.pair(('요리 준비', 'preparing dishes'), locale)]
    return [lex.context(c, locale, compact) for c in contexts]



def tool_purposes(units, locale, with_order=False):
    """Existential parent purposes over named admitted activities.

    Every member stays in expanded and in refs. These are expression groups,
    not claims that the tool supports every operation in the parent category.
    """
    activities = sorted(set().union(*(purpose_tokens(u) for u in units)) - {None})
    # Every refinement supplied by admitted relations reaches the special
    # tool overview too; a new refinement needs no second activity allowlist.
    overrides = {a: list(dict.fromkeys(label for u in units if a in purpose_tokens(u)
                    for label in activity_labels(u, locale, True)))
                 for a in activities if a != 'electronic_assembly' and any(activity_labels(u, locale, True) != [lex.context(a, locale, True)]
                                           for u in units if a in purpose_tokens(u))}
    remaining = set(activities) - overrides.keys()
    labels = []
    order = []
    def family(members, ko_text, en_text):
        selected = remaining & members
        if selected:
            remaining.difference_update(selected)
            labels.append(lex.pair((ko_text, en_text), locale))
            order.extend(sorted(selected))
    electronic_build = remaining & {'electronic_assembly', 'radio_crafting'}
    electronic_strip = remaining & {'electronic_salvage', 'radio_salvage'}
    if electronic_build or electronic_strip:
        remaining.difference_update(electronic_build | electronic_strip)
        order.extend(sorted(electronic_build))
        order.extend(sorted(electronic_strip))
        labels.append(lex.pair(('전자기기 제작과 분해' if electronic_build and electronic_strip else
                               '전자기기 제작' if electronic_build else '전자기기 분해',
                               'making and dismantling electronic devices' if electronic_build and electronic_strip else
                               'making electronic devices' if electronic_build else 'dismantling electronic devices'), locale))
    family({'metal_forging', 'shovel_smithing', 'smithing_parts'}, '금속 단조', 'metal forging')
    family({'animal_butchery', 'fish_preparation', 'food_portioning', 'frog_preparation'}, '음식 손질', 'food preparation')
    dough = remaining & {'cookie_preparation', 'dough_preparation'}
    batter = 'batter_preparation' in remaining
    if dough or batter:
        family(dough | ({'batter_preparation'} if batter else set()), '반죽 준비', 'dough and batter preparation' if dough and batter else 'dough preparation' if dough else 'batter preparation')
    # Furniture moving is retained explicitly; it is not implied by carpentry.
    woodworking = remaining & {'woodworking', 'construction', 'carpentry_menu_construction'}
    if woodworking:
        remaining.difference_update(woodworking)
        order.extend(a for a in ('woodworking', 'construction', 'carpentry_menu_construction') if a in woodworking)
        labels.append(lex.pair(('목공·건축' if 'woodworking' in woodworking and len(woodworking)>1 else '목공' if woodworking=={'woodworking'} else '건축',
                               'woodworking and construction' if 'woodworking' in woodworking and len(woodworking)>1 else 'woodworking' if woodworking=={'woodworking'} else 'construction'), locale))
    if woodworking and 'moving_furniture' in remaining:
        remaining.remove('moving_furniture')
        order.append('moving_furniture')
        if locale == 'ko':
            labels[-1] += '·가구 작업'
        else:
            labels[-1] = ('woodworking, construction and furniture work' if len(woodworking)>1 else 'woodworking and furniture work' if woodworking=={'woodworking'} else 'construction and furniture work')
    if {'fishing_gear_crafting', 'spear_crafting'} <= remaining:
        family({'fishing_gear_crafting', 'spear_crafting'}, '낚시 장비·창 제작', 'fishing-gear and spear crafting')
    family({'metal_welding_construction', 'welded_parts'}, '금속 용접', 'metal welding')
    for activity, specific in overrides.items():
        labels.extend(specific)
        order.append(activity)
    labels.extend(lex.context(a, locale, True) for a in sorted(remaining))
    order.extend(sorted(remaining))
    labels = list(dict.fromkeys(labels))
    return (labels, order) if with_order else labels


def disposition(unit):
    facts = unit['facts']
    roles = {f['payload'].get('role') for f in facts if f['fact_kind'] == 'context_role'}
    contexts = {f['payload'].get('activity') for f in facts} | {(unit.get('context') or {}).get('activity')}
    if any(f['fact_kind'] == 'acquisition' for f in facts):
        return 'internal', 'acquisition remains in the independent acquisition supply'
    if roles == {'repair_target'}:
        return 'self-management', 'repair of this item does not explain a use supplied by it'
    if contexts & {'battery_insertion', 'battery_removal', 'blowtorch_refilling'} and roles <= {'power_receiver', 'transformation_target'}:
        return 'self-management', 'servicing the power or fuel of this item'
    if 'umbrella_form_change' in contexts or 'candle_extinguishing' in contexts:
        return 'self-management', 'changing the state of this item, without a separately grounded use'
    if contexts == {'food_container_emptying', None}:
        return 'self-management', 'emptying the used container'
    for fact in facts:
        kind, payload = fact['fact_kind'], fact['payload']
        if kind == 'direct_function':
            function = payload.get('function')
            if function in {'take_pills', 'take_food_medicine'}:
                return 'internal', 'admitted consumption dispatch alone does not establish a medicinal purpose or effect'
            if function in SELF_FUNCTIONS or (function in lex.FUNCTIONS and function.startswith('remove_vehicle_')):
                return 'self-management', 'operation or care of the item rather than an independent use'
            if function not in lex.FUNCTIONS:
                raise ValueError('unclassified function: ' + str(function))
        elif kind == 'effect':
            if payload.get('property') in INTERNAL_PROPERTIES:
                return 'internal', 'attribution, bookkeeping or procedure metadata'
            # Lexical support is checked here, not by a leftover renderer.
            lex.core(fact, 'ko')
            lex.core(fact, 'en')
        elif kind == 'state':
            if payload.get('state') in INTERNAL_STATES:
                return 'internal', 'page bookkeeping or implementation increment'
            lex.core(fact, 'ko')
            lex.core(fact, 'en')
        elif kind == 'use_context':
            if payload.get('activity') not in lex.CONTEXTS:
                raise ValueError('unclassified activity: ' + str(payload))
        elif kind == 'context_role':
            if payload.get('role') not in lex.ROLES or not any(contexts):
                raise ValueError('unbound participant role: ' + str(payload))
        else:
            raise ValueError('unclassified fact kind: ' + kind)
    if any(f['fact_kind'] in {'direct_function', 'use_context', 'context_role'} for f in facts):
        return 'use', 'admitted function or participant in an identified activity; all independent uses stay compact'
    if all(f['fact_kind'] == 'effect' and f['payload'].get('property') in SUPPORTING_PROPERTIES for f in facts):
        return 'supporting detail', 'use-relevant outcome or risk; not an independent use or operating procedure'
    return 'result/target', 'admitted effect or distinguishing state with its fact-local conditions'


def internal_reason(unit):
    category, reason = disposition(unit)
    return reason if category in {'internal', 'self-management'} else None


def frames(plan, locale, links, compact):
    output, used = [], set()
    units = plan['units']
    from . import description_composition_families as families

    def select(functions):
        return [u for u in units if any(f['payload'].get('function') in functions for f in u['facts'])
                and not set(u['fact_refs']) & used]

    def emit(members, text, ordered=False, reason='role and confirmed result use; execution evidence retained internally'):
        if not members:
            return
        allowed = set()
        if compact and any(f['payload'].get('role') == 'tool' for u in members for f in u['facts']):
            allowed.update(TOOL_DETAIL_PREDICATES)
        by_function = {
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
            'remove_placed_furniture': {'PICKUP', 'PICKUP_LOSS'},
            'supply_escape_rope': {'ESCAPE_ROPE_INSTALL'},
            'remove_installed_escape_rope': {'ESCAPE_ROPE_REMOVE'},
            'start_escape_rope_ascent': {'ESCAPE_ROPE_CLIMB'},
            'clean_burn': {'BURN_CLEANING'},
            'unpick_garment_patch': {'GARMENT_PATCH_REMOVAL'},
            'pitch_tent': {'CAMP_PLACEMENT', 'TENT_PLACEMENT'},
            'rest_at_placed_tent': {'TENT_REST'},
            'light_candle': {'CANDLE_LIGHT_RECIPE'},
            'receive_portioned_food': {'BOWL_PORTIONING'},
            'set_alarm': {'ALARM_SETTING'},
            'stop_alarm': {'ALARM_STOPPING'},
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
        output.append({'text': text + '.', **links(claims, plan), 'expression': 'public_use',
                       'placement_reason': reason,
                       'qualifier_dispositions': []})
        used.update(r for u in members for r in u['fact_refs'])

    def names(items):
        words = list(dict.fromkeys(i['names'][locale] for i in items))
        return '·'.join(words) if locale == 'ko' else en.join(words)

    def object_name(noun):
        ending = noun.rstrip(')]} ')[-1]
        final = (ord(ending) - ord('가')) % 28 if '가' <= ending <= '힣' else 0
        return noun + ('을' if final else '를')

    functions = {f['payload'].get('function') for u in units for f in u['facts']}
    if {'link_remote_device', 'send_remote_trigger'} <= functions:
        emit(select({'link_remote_device', 'send_remote_trigger'}), lex.pair((
            '함께 소지한 호환 장치를 연결해 조종 범위 안에서 원격으로 작동시킬 수 있다',
            'It can be linked to a compatible device carried together and remotely activate that device within range'), locale))
    key_actions = {
        'operate_door_lock': ('문 잠금과 해제', 'locking and unlocking doors'),
        'remove_matching_padlock': ('구조물 자물쇠 제거', 'removing structure padlocks'),
        'request_matching_vehicle_start': ('차량 시동', 'starting vehicles'),
    }
    if compact and len(functions & key_actions.keys()) > 1:
        labels = [lex.pair(label, locale) for fn, label in key_actions.items() if fn in functions]
        text = ('·'.join(labels) + '에 쓸 수 있으며 대상과 열쇠가 맞아야 한다' if locale == 'ko' else
                'It can be used for ' + en.join(labels) + ', with a matching key required for each target')
        if 'remove_matching_padlock' in functions:
            text += lex.pair(('. 자물쇠 제거 시 소모된다', '. Removing a padlock consumes the key'), locale)
        if 'avoid_first_door_alarm_trigger' in functions:
            text += lex.pair(('. 차량 첫 개방 경보를 막지만 이미 울리는 경보는 끄지 못한다',
                              '. It prevents the first-entry vehicle alarm but cannot silence an active alarm'), locale)
        emit(select(set(key_actions) | {'avoid_first_door_alarm_trigger'}), text)
    elif {'request_matching_vehicle_start', 'avoid_first_door_alarm_trigger'} <= functions:
        emit(select({'request_matching_vehicle_start', 'avoid_first_door_alarm_trigger'}), lex.pair((
            '맞는 차량의 시동을 거는 데 쓸 수 있다. 차량 문을 처음 열 때 경보를 막지만 이미 울리는 경보는 끄지 못한다',
            'It can be used to start the matching vehicle. It prevents the alarm when first opening a vehicle door but cannot silence an active alarm'), locale))
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
        elif activity == 'explosive_modification':
            # In the admitted Add recipes, the second selector is the fitted component.
            components = {'Base.' + parts[1] for _, parts, context, _ in lex.source.ITEM_TRANSFORMATION_RECIPES if context == activity}
            component = plan['item_id'] in components
            target = bool(functions & {'request_physics_attack', 'place_noise_device', 'place_trigger_device'})
            wording = ('장치에 작동 부품으로 달아 쓸 수 있다', 'It can be fitted to a device as a triggering component') if component else ('작동 부품을 달아 개조할 수 있다', 'It can be modified by fitting triggering components') if target else (
                ('장치에 작동 부품을 다는 데 쓸 수 있다', 'It can be used to fit triggering components to devices') if 'tool' in roles else
                ('장치에 작동 부품을 다는 재료로 쓸 수 있다', 'It can be used as material for fitting triggering components to devices'))
        else:
            vessel = bool(functions & {'store_water', 'carry_water'}) and not functions & {'drink_food_contents', 'smoke_cigarette'}
            wording = ('작물 치료용 분무액을 만드는 용기로 쓸 수 있다', 'It can hold the mixture when making crop-treatment spray') if vessel else (
                '작물 치료용 분무액을 만드는 재료로 쓸 수 있다', 'It can be used as an ingredient for making crop-treatment spray')
        emit(members, lex.pair(wording, locale))

    tent = select({'pitch_tent', 'rest_at_placed_tent'})
    if len(tent) == 2:
        emit(tent, lex.pair(('텐트를 설치해 쉬거나 잘 수 있다', 'It can be pitched as a tent for resting or sleeping'), locale))

    # The same welding implement can be debited by a recipe and kept by a
    # construction action; neither participation makes it a building material.
    if any('metal_welding_construction' in purpose_tokens(u) and any(f['payload'].get('role') == 'tool' for f in u['facts']) for u in units):
        welding = [u for u in units if not used & set(u['fact_refs']) and purpose_tokens(u) & {'construction', 'metal_welding_construction', 'welded_parts'}]
        if not compact:
            emit(welding, lex.pair(('금속 부품 용접과 용접 건축에 쓸 수 있다', 'It can be used for metal-part welding and welded construction'), locale))

    seat = select({'use_vehicle_seat', 'store_vehicle_items'})
    if functions >= {'use_vehicle_seat', 'store_vehicle_items'}:
        emit(seat + select({'install_vehicle_storage_part'}), lex.pair(('호환 차량에 장착해 앉거나 물품을 보관할 수 있다', 'It can be installed in a compatible vehicle for seating or item storage'), locale))
    tank = select({'store_vehicle_fuel', 'supply_vehicle_engine_fuel', 'transfer_vehicle_fuel'})
    if functions >= {'store_vehicle_fuel', 'supply_vehicle_engine_fuel', 'transfer_vehicle_fuel'}:
        emit(tank + select({'install_vehicle_storage_part'}), lex.pair((
            '호환 차량에 장착해 연료를 보관하고 엔진에 공급할 수 있다. 엔진을 끄면 맞는 용기로 연료를 넣거나 뺄 수 있다. 탱크 상태가 70 미만이면 연료가 추가로 줄 수 있다',
            'It can be installed in a compatible vehicle to store fuel and supply the engine. With the engine stopped, fuel can be added or siphoned with a compatible container. Tank condition below 70 can cause additional fuel loss'), locale))
    doors = select({'operate_installed_vehicle_door', 'operate_installed_vehicle_lock', 'operate_installed_vehicle_window'})
    panel = [u for u in units if not used & set(u['fact_refs']) and any(f['payload'].get('function', '').startswith('install_vehicle_') for f in u['facts'])]
    if doors and len(panel) == 1:
        labels = []
        if functions & {'operate_installed_vehicle_door', 'operate_installed_vehicle_window'}:
            labels.append(('여닫을 수 있다', 'It can be opened and closed'))
        if 'operate_installed_vehicle_lock' in functions:
            labels.append(('잠그거나 잠금을 풀 수 있다', 'It can be locked and unlocked'))
        opening = lex.core(panel[0]['facts'][0], locale).rstrip('.')
        emit(panel + doors, opening + ('. 장착 후 ' + ( '여닫거나 잠그고 잠금을 풀 수 있다' if len(labels) == 2 else labels[0][0]) if locale == 'ko' else '. Once installed, it can be opened, closed, locked or unlocked' if len(labels) == 2 else '. ' + labels[0][1]))
    fuel_transfer = select({'fill_petrol_container', 'transfer_vehicle_fuel'})
    if len(fuel_transfer) == 2:
        emit(fuel_transfer, lex.pair(('전원이 있는 주유기에서 급유받거나 시동이 꺼진 차량과 연료를 주고받을 수 있다', 'It can receive fuel from a powered pump or exchange fuel with a vehicle whose engine is off'), locale))
    patch = select({'apply_garment_patch', 'unpick_garment_patch'})
    if len(patch) == 2:
        emit(patch, lex.pair(('의류의 구멍을 덧대거나 패딩을 붙이고 패치를 제거할 수 있다. 제거 시 재료가 회수될 수 있다', 'It can mend garment holes, add padding and remove patches, with a chance to recover the removed material'), locale))
    electronics_contexts = {'electronic_assembly', 'radio_crafting', 'electronic_salvage', 'radio_salvage'}
    electronics_tools = [u for u in units if not used & set(u['fact_refs'])
                         and purpose_tokens(u) & electronics_contexts
                         and any(f['payload'].get('role') == 'tool' for f in u['facts'])]
    electronics_activities = set().union(*(purpose_tokens(u) for u in electronics_tools)) if electronics_tools else set()
    if electronics_activities >= electronics_contexts:
        lamp = select({'convert_lamp_to_battery'})
        text = lex.pair(('전자 부품·무전기 제작과 전자기기 분해에 쓸 수 있다' if compact else
                         '전자 부품·무전기를 만들거나 전자기기(라디오·TV 포함)를 분해해 부품을 회수할 수 있다',
                         'It can make electronic components and radios or dismantle electronic devices' +
                         ('' if compact else ', including radios and TVs, to recover parts')), locale)
        if lamp:
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
        emit(tires, lex.pair(('주행 중 공기와 상태가 줄 수 있으며 공기나 상태가 나쁘면 타이어를 잃을 수 있다', 'Driving can reduce tire air and condition; poor air or condition can cause tire loss'), locale))
    water_handling = select({'store_water', 'carry_water', 'pour_water_into_container', 'supply_world_water_storage'})
    if not compact and functions >= {'store_water', 'carry_water', 'pour_water_into_container', 'supply_world_water_storage'}:
        emit(water_handling + select({'receive_poured_water'}), lex.pair(('물을 담아 보관하거나 운반하고, 다른 용기나 물 저장 시설로 옮길 수 있다', 'It can store and carry water and transfer it to other containers or water storage fixtures'), locale))

    if not compact:
        food_tasks = {'animal_butchery', 'fish_preparation', 'frog_preparation', 'food_portioning', 'food_preparation'}
        food_tools = [u for u in units if not used & set(u['fact_refs']) and purpose_tokens(u) - {None} <= food_tasks and purpose_tokens(u) & food_tasks
                      and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'tool'}]
        if len(set().union(*(purpose_tokens(u) for u in food_tools)) - {None}) > 1:
            emit(food_tools, lex.pair(('음식을 손질하는 데 쓸 수 있다', 'It can be used for food preparation'), locale))

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
        if wording:
            cooking_partners = [u for u in units if not used & set(u['fact_refs'])
                                and purpose_tokens(u) & {'food_preparation', 'food_ingredient_addition', 'grain_preparation'}
                                and any(f['payload'].get('role') in {'container', 'base'} for f in u['facts'])]
            if compact and wording[0] == '붕대 소독에 쓸 수 있다' and cooking_partners:
                emit([unit] + cooking_partners, lex.pair(('조리와 붕대 소독에 쓸 수 있다', 'It can be used for cooking and disinfecting bandaging'), locale))
            else:
                emit([unit], lex.pair(wording, locale))

    # A material's woodworking and building recipes share a supplied purpose.
    # Installation, repair, packaging and processing the item itself stay out.
    craft = {'woodworking', 'construction', 'metal_welding_construction', 'carpentry_menu_construction',
             'campfire_kit_preparation', 'furniture_crafting', 'tool_crafting',
             'spear_crafting', 'splint_crafting', 'trap_crafting', 'fishing_gear_crafting',
             'mattress_preparation', 'tent_kit_making', 'camping_kit_preparation', 'stone_tool_crafting', 'electronic_assembly', 'radio_crafting',
             'explosive_assembly', 'explosive_modification'}
    material_units = [u for u in units if not used & set(u['fact_refs'])
                      and purpose_tokens(u) - {None} <= craft and purpose_tokens(u) & craft
                      and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'material'}
                      and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} <= CONSTRUCTION_PREDICATES | {lex.source.WELDING_CONSTRUCTION}]
    selected = material_units
    activities = set().union(*(purpose_tokens(u) for u in selected)) if selected else set()
    minimum = 2 if not activities & {'electronic_assembly', 'radio_crafting', 'explosive_assembly', 'explosive_modification'} else 3
    if len(activities - {None}) >= (minimum if compact else 2):
        woodworking = bool(activities & {'woodworking', 'furniture_crafting'})
        building = bool(activities & {'construction', 'carpentry_menu_construction', 'metal_welding_construction'})
        electronics = bool(activities & {'electronic_assembly', 'radio_crafting'})
        devices = bool(activities & {'explosive_assembly', 'explosive_modification'})
        other = bool(activities - {None, 'woodworking', 'furniture_crafting', 'construction', 'carpentry_menu_construction', 'metal_welding_construction',
                                  'electronic_assembly', 'radio_crafting', 'explosive_assembly', 'explosive_modification'})
        labels = [lex.pair(pair, locale) for enabled, pair in (
            (woodworking, ('목공', 'woodworking')), (building, ('용접을 포함한 건축', 'construction including welding') if 'metal_welding_construction' in activities else ('건축', 'construction')),
            (electronics, ('전자 부품과 기기 제작', 'electronic-component and device crafting')),
            (devices, ('폭발물 등의 장치 제작과 작동 부품 장착' if 'explosive_modification' in activities else '장치 제작',
                       'crafting explosive or similar devices and fitting triggering components' if 'explosive_modification' in activities else 'device crafting')),
            (other, ('기타 제작' if electronics or devices else '물품 제작', 'other crafting' if electronics or devices else 'crafting'))) if enabled]
        selected += [u for u in units if u not in selected and not used & set(u['fact_refs'])
                     and all(f['fact_kind'] == 'use_context' for f in u['facts'])
                     and any(u['branch_refs'] == member['branch_refs'] for member in selected)]
        if building and compact:
            selected += select({'build_wooden_barricade'})
        repairs = [u for u in units if not used & set(u['fact_refs']) and 'repair' in purpose_tokens(u)
                   and any(f['payload'].get('role') == 'repair_material' for f in u['facts'])]
        if compact and repairs:
            labels.append(lex.pair(('호환 물품 수리', 'repairing compatible items'), locale))
            selected += repairs
        if not compact:
            building_contexts = {'woodworking', 'construction', 'carpentry_menu_construction', 'furniture_crafting', 'metal_welding_construction'}
            labels = [lex.pair(('용접을 포함한 건축', 'construction including welding') if 'metal_welding_construction' in activities else ('목공과 건축', 'woodworking and construction') if woodworking and building else ('목공', 'woodworking') if woodworking else ('건축', 'construction'), locale)] if activities & building_contexts else []
            objects = {'campfire_kit_preparation': ('모닥불 키트', 'campfire kits'), 'spear_crafting': ('창', 'spears'), 'splint_crafting': ('부목', 'splints'), 'trap_crafting': ('덫', 'traps'), 'fishing_gear_crafting': ('낚시 장비', 'fishing gear'), 'mattress_preparation': ('매트리스', 'mattresses'), 'tent_kit_making': ('텐트 키트', 'tent kits'), 'stone_tool_crafting': ('석제 도구', 'stone tools')}
            craft_names = [lex.pair(v, locale) for k,v in objects.items() if k in activities]
            if craft_names:
                labels.append(', '.join(craft_names) + ' 제작' if locale == 'ko' else 'making ' + en.join(craft_names))
            labels += list(dict.fromkeys(label for u in selected if not purpose_tokens(u) & (building_contexts | objects.keys()) for label in activity_labels(u, locale, False)))
        if compact and woodworking and building:
            labels[0:2] = ['목공과 ' + labels[1] if locale == 'ko' else 'woodworking and ' + labels[1]]
        if compact and devices and other and 'explosive_modification' not in activities:
            device_label = lex.pair(('장치 제작', 'device crafting'), locale)
            other_label = lex.pair(('기타 제작', 'other crafting'), locale)
            labels = [label for label in labels if label not in {device_label, other_label}]
            labels.append(lex.pair(('장치 등 물품 제작', 'crafting devices and other items'), locale))
        if not compact and locale == 'ko':
            craft = [label.removesuffix(' 제작') for label in labels if label.endswith(' 제작')]
            labels = [label for label in labels if not label.endswith(' 제작')]
            if craft:
                labels.append(', '.join(craft) + ' 제작')
        emit(selected, (', '.join(labels) + '에 재료로 쓸 수 있다') if locale == 'ko' else
             'It can be used as material for ' + en.join(labels))

    for activity, role, wording in (
        ('repair', 'repair_material', ('호환되는 손상 물품의 수리 재료로 사용할 수 있다', 'It can be used as material for repairing compatible damaged items')),
        ('blowtorch_refilling', 'fuel', ('토치에 프로판을 보충할 수 있다', 'It can supply propane for refilling blowtorches')),
    ):
        members = [u for u in units if not used & set(u['fact_refs']) and activity in purpose_tokens(u)
                   and any(f['payload'].get('role') == role for f in u['facts'])]
        # A context split from its role shares only that branch's purpose.
        members += [u for u in units if any(f['payload'].get('activity') == activity for f in u['facts'])
                    and all(f['fact_kind'] == 'use_context' for f in u['facts'])
                    and any(u['branch_refs'] == other['branch_refs'] for other in members)]
        emit(members, lex.pair(wording, locale))

    notes = select({'view_written_note_pages', 'record_written_notes'})
    if {f['payload'].get('function') for u in notes for f in u['facts']} == {'view_written_note_pages', 'record_written_notes'}:
        emit(notes, '메모를 읽고 적는 데 쓸 수 있다' if locale == 'ko' else 'It can be used for reading and writing notes')

    attachment = select({'attach_weapon_part'})
    detachment = select({'remove_weapon_part'})
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
    emit(magazine, '호환 총기에 끼워 사용할 수 있다' if locale == 'ko' else
         'It can be inserted into a compatible firearm')

    # The condition explicitly names wearing and the affected firearm scope.
    # Share this frame on both surfaces before generic clothing or effects can
    # claim its members. Unknown operations/scopes retain the scoped fallback.
    for unit in units:
        text = lex.reload_effect(unit, plan, locale, compact)
        if text is None:
            continue
        wear = select({'wear_on_body', 'wear_configured_clothing'})
        locations = [u for u in units if any(f['payload'].get('state') == 'worn_location'
                                           for f in u['facts'])]
        if not compact and wear and len(locations) == 1:
            text = lex.wearing(locations[0]['facts'][0]['payload']['value'], locale) + '. ' + text
        emit(wear + locations + [unit], text, ordered=True,
             reason='confirmed reload-speed multiplication with worn and ammunition scope; action duration is not inferred')

    # Recipe result groups refine the same forging purpose. Keep roles apart
    # and merge only when no distinguishing public condition remains.
    forging = {'metal_forging', 'shovel_smithing', 'smithing_parts'}
    for role in ('tool', 'material'):
        members = [u for u in units if not u['qualifier_refs']
                   and (purpose_tokens(u) - {None}) <= forging
                   and purpose_tokens(u) & forging
                   and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {role}]
        activities = set().union(*(purpose_tokens(u) for u in members)) if members else set()
        if 'metal_forging' in activities and len(activities & forging) > 1:
            text = (('금속을 단조하는 데 사용할 수 있다' if role == 'tool' else '금속 단조의 재료로 사용할 수 있다') if locale == 'ko'
                    else ('It can be used for metal forging' if role == 'tool' else 'It can be used as material for metal forging'))
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
                emit([u], target + ' 제작 재료로 사용할 수 있다' if locale == 'ko' else 'It can be used as material for making ' + target)

    fabric_result = plan.get('source_traits', {}).get('fabric_result')
    fabric_dirty = plan.get('source_traits', {}).get('fabric_dirty_result')
    recovered_name = fabric_result['names'][locale] if fabric_result else lex.pair(('옷감', 'fabric'), locale)
    compact_materials = {'Cotton': ('천 조각', 'cloth scraps'), 'Denim': ('데님 조각', 'denim strips'), 'Leather': ('가죽 조각', 'leather strips')}
    compact_recovery = lex.pair(compact_materials[plan['source_traits']['FabricType']], locale) if plan.get('source_traits', {}).get('FabricType') in compact_materials else recovered_name
    if fabric_result and fabric_result['item_id'] == 'Base.RippedSheets':
        compact_recovery = lex.pair(('천 조각', 'cloth scraps'), locale)

    # A wearable can provide recovered fabric, rope material and fire supplies.
    # Group these uses from their payloads, not a garment name or length budget.
    wearables = select({'wear_on_body', 'wear_configured_clothing'})
    fabric_uses = [u for u in units if any(f['payload'].get('activity') == 'fabric_recovery' for f in u['facts'])]
    rope_uses = [u for u in units if any(f['payload'].get('activity') == 'sheet_rope_making' for f in u['facts'])]
    if compact and not wearables and fabric_uses and rope_uses and fabric_result:
        text = ('찢어서 ' + object_name(compact_recovery) + ' 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다') if locale == 'ko' else (
            'It can be ripped for ' + compact_recovery + ' or used to make sheet rope')
        emit(fabric_uses + rope_uses, text)
    if compact and wearables and fabric_uses and plan.get('source_traits', {}).get('FabricType') in {'Cotton', 'Denim', 'Leather'}:
        places = [u for u in units if any(f['payload'].get('state') == 'worn_location' for f in u['facts'])]
        needs_scissors = plan['source_traits']['FabricType'] in {'Denim', 'Leather'}
        material = ('가위로 찢어서 ' if needs_scissors else '찢어서 ') + object_name(compact_recovery) + ' 획득'
        english = compact_recovery + ' recovered by ripping' + (' with scissors' if needs_scissors else '')
        if rope_uses:
            material += '할 수 있다. 시트 로프 제작 재료로 사용'
            english += ', or used to make sheet rope'
        fuel, tinder = select(FUEL), select(TINDER)
        text = '착용할 수 있고, ' + material + '할 수 있다' if locale == 'ko' else 'It can be worn or used as material for ' + english
        forms = select({'switch_declared_clothing_form'})
        if fuel or tinder:
            supplies = '나 '.join(word for members, word in ((fuel, '연료'), (tinder, '불쏘시개')) if members)
            supplies_en = en.join([word for members, word in ((fuel, 'fuel'), (tinder, 'tinder')) if members])
            text = ('착용하거나 찢어서 ' + object_name(compact_recovery) + ' 얻을 수 있다. ' + ('착용 모양을 바꿀 수도 있다. ' if forms else '') + ('시트 로프 제작에 쓸 수도 있다. ' if rope_uses else '') + supplies + '로도 쓸 수 있다') if locale == 'ko' else ('It can be worn in alternate forms or ripped to obtain ' if forms else 'It can be worn or ripped to obtain ') + compact_recovery + (', used to make sheet rope' if rope_uses else '') + ', or used as ' + supplies_en
            if needs_scissors:
                text += '. 찢을 때 가위를 쓴다' if locale == 'ko' else '. Fabric recovery requires scissors'
        emit(wearables + places + fabric_uses + rope_uses + fuel + tinder + (forms if fuel or tinder else []), text)

    # A confirmed food-preparation purpose contains dough preparation only
    # for the same participant role and without a separate public condition.
    # Role changes and scoped tasks such as slicing cooked food stay separate.
    for role, nouns in (('tool', ('도구', 'a tool')),):
        food = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
                and purpose_tokens(u) - {None} == {'food_preparation'}
                and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {role}]
        dough = [u for u in units if not used & set(u['fact_refs']) and not u['qualifier_refs']
                 and purpose_tokens(u) - {None} <= {'dough_preparation', 'cookie_preparation', 'batter_preparation'}
                 and purpose_tokens(u) & {'dough_preparation', 'cookie_preparation', 'batter_preparation'}
                 and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {role}]
        if food and dough:
            emit(food + dough, '음식 준비에 사용할 수 있다' if locale == 'ko'
                 else 'It can be used for food preparation',
                 reason='same-role food preparation includes dough preparation; distinct roles and public conditions remain separate')

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
        purpose = ('음식 준비' if food else '반죽 준비') if locale == 'ko' else (
            'food preparation' if food else dough_en + ' preparation')
        members = list(cooking)
        text = ('재료를 담아 요리할 수 있다' if food else '반죽을 담아 요리를 만드는 데 쓸 수 있다') if locale == 'ko' else ('It can hold ingredients for cooking' if food else 'It can hold ' + dough_en + ' for preparing food')
        if bowls:
            members += bowls + [u for u in units if 'food_portioning' in purpose_tokens(u) and any(f['payload'].get('role') in {'material', 'container'} for f in u['facts'])]
            text = (purpose + '나 조리한 음식을 나누어 담는 데 사용할 수 있다') if locale == 'ko' else ('It can be used for ' + purpose + ' and for holding portions of prepared meals')
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

    for relation in plan.get('use_relations', []):
        if relation['function'] == 'recipe_use' and relation.get('activity') in {'ammunition_disassembly', 'bottle_breaking'} and relation['input_role'] == 'transformation_target':
            members = [u for u in units if set(relation['fact_refs']) & set(u['fact_refs']) and not used & set(u['fact_refs'])]
            result_name = names(relation['results'])
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
                result_name = names(primary)
                text = ('나누어 ' + object_name(result_name) + ' 얻을 수 있다' if locale == 'ko'
                        else 'It can be portioned to obtain ' + result_name)
                for predicate in (lex.source.COOKED_SLICING, lex.source.DOUGH_SLICING, lex.source.PIZZA_SLICING, lex.source.MUFFIN_PORTIONING, lex.source.BISCUIT_PORTIONING):
                    if predicate in predicates:
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
                if not compact and returned:
                    text += ('. 함께 회수하는 물품: ' if locale == 'ko' else '. Also returns ') + names(returned)
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
        result_name = names(certain)
        tool_groups = [(' 또는 ' if locale == 'ko' else ' or ').join(dict.fromkeys(i['names'][locale] for i in group['items'])) for group in relation['tools']]
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
                text = '봉지를 열어 꺼낸 ' + object_name(result_name) + ' 파종하는 데 쓸 수 있다'
            if possible:
                text += '. ' + names(possible) + '도 나올 수 있다'
        else:
            action = 'prepared' if fn == 'prepare_frog_meat' else 'dismantled' if fn == 'dismantle_electronics' else 'opened'
            method = ' with ' + ('a ' if len(relation['tools']) == 1 and len(relation['tools'][0]['items']) == 1 and not tool_text.startswith(('a ', 'an ')) else '') + tool_text if tool_text else ''
            text = 'It can be ' + action + method + ' to obtain ' + result_name
            if relation['result_use'] == 'prepare_opened_food_ingredient':
                text += ' for use as a cooking ingredient'
            elif relation['result_use'] == 'sow_extracted_seeds':
                text += ' for sowing'
            if possible:
                text += '. ' + names(possible) + ' may also be recovered'
        if not compact and relation['result_use'] == 'sow_extracted_seeds':
            text += ('. 한 봉지에는 씨앗 ' + certain[0]['count'] + '개가 들어 있다' if locale == 'ko'
                     else '. Each packet contains ' + certain[0]['count'] + ' seeds')
        if fn in {'unpack_canned_food', 'unpack_jarred_food', 'unpack_eggs'}:
            edible = select({'eat_food', 'consume_edible_food'})
            consumption = relation.get('result_consumption')
            # Only the known generic consumption condition is abstracted here;
            # an additional result eligibility condition must not disappear.
            result_edible = consumption and {q['payload']['predicate'] for q in consumption['qualifiers']} <= {lex.source.CONSUMING}
            if edible or result_edible:
                drinking = bool(result_edible and consumption['fact']['payload']['function'] == 'drink_food_contents')
                # The opened food's admitted display name identifies what is
                # consumed. Reuse it in both uses rather than hiding it behind
                # "contents" or inferring a food name from the sealed item.
                opening = (method + action + ' ' + object_name(result_name) +
                           (' 마실 수 있다' if drinking else ' 먹을 수 있다') if locale == 'ko' else
                           'It can be opened' + method + (' to drink the ' if drinking else ' to eat the ') + result_name)
                cooking = (('꺼낸 ' + object_name(result_name) + ' 요리 재료로도 쓸 수 있다') if locale == 'ko'
                           else ('The extracted ' + result_name + ' can also be used as a cooking ingredient'))
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

    media = select({'control_device_media', 'tune_radio', 'select_tv_channel'})
    if media:
        media_functions = {f['payload'].get('function') for u in media for f in u['facts']}
        actions = [('control_device_media', ('기록 매체 재생', 'playing recorded media')),
                   ('tune_radio', ('라디오 방송 청취', 'listening to radio broadcasts')),
                   ('select_tv_channel', ('TV 방송 시청', 'watching television broadcasts'))]
        labels = [lex.pair(pair, locale) for fn, pair in actions if fn in media_functions]
        text = ('전원이 공급되면 ' + '·'.join(labels) + '에 쓸 수 있다') if locale == 'ko' else ('With power, it can be used for ' + en.join(labels))
        if locale == 'ko' and media_functions & {'tune_radio', 'select_tv_channel'}:
            verbs = []
            if 'control_device_media' in media_functions:
                verbs.append('기록 매체를 재생')
            if 'tune_radio' in media_functions:
                verbs.append('라디오 방송을 청취')
            if 'select_tv_channel' in media_functions:
                verbs.append('TV 방송을 시청')
            text = '전원이 공급되면 ' + '하거나 '.join(verbs) + '할 수 있다'
        outcomes = [u for u in units if not used & set(u['fact_refs']) and all(
            f['payload'].get('property') == 'delivered_media_code_outcome' for f in u['facts'])]
        if outcomes:
            text += ('. 내용에 따라 능력치·경험치·제작법 학습 효과를 얻을 수 있다' if locale == 'ko'
                     else '. Depending on the content, it can affect stats, XP or recipe knowledge')
        emit(media + outcomes, text)

    recordings = select({'insert_recorded_media'})
    if recordings:
        outcomes = [u for u in units if not used & set(u['fact_refs']) and all(
            f['payload'].get('property') == 'delivered_media_code_outcome' for f in u['facts'])]
        text = ('호환 재생 기기에 넣어 기록된 내용을 재생할 수 있다. 전원이 필요하다' if locale == 'ko'
                else 'Its recorded content can be played on a compatible device with power')
        if outcomes:
            text += ('. 내용에 따라 능력치·경험치·제작법 학습 효과를 얻을 수 있다' if locale == 'ko'
                     else '. Depending on the content, it can affect stats, XP or recipe knowledge')
        emit(recordings + outcomes, text)

    alarms = select({'set_alarm', 'stop_alarm'})
    if {f['payload'].get('function') for u in alarms for f in u['facts']} == {'set_alarm', 'stop_alarm'}:
        emit(alarms, '알람 시각과 켜짐 여부를 설정하고 울리는 알람을 끌 수 있다' if locale == 'ko'
             else 'Its alarm time and on/off state can be set, and a ringing alarm can be stopped')

    dismantled = select({'dismantle_electronics'})
    salvage_targets = [u for u in units if not used & set(u['fact_refs'])
        and any(f['payload'].get('activity') in {'electronic_salvage', 'radio_salvage'} for f in u['facts'])
        and any(f['payload'].get('role') == 'transformation_target' for f in u['facts'])]
    if dismantled and salvage_targets:
        text = '드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다' if locale == 'ko' else 'It can be dismantled with a screwdriver to recover electronic parts'
        emit(dismantled + salvage_targets, text)

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

    bandaging = select({'apply_bandage'})
    if bandaging:
        preparation = [u for u in units if not used & set(u['fact_refs']) and 'bandaging_material_preparation' in purpose_tokens(u)
                       and {r['item_id'] for rel in u.get('recipe_targets', []) for r in rel['results']} <= {'Base.AlcoholBandage', 'Base.AlcoholRippedSheets'}
                       and u.get('recipe_targets')]
        infection = [u for u in units if not used & set(u['fact_refs'])
                     and all(f['payload'].get('property') == 'bandage_patient_infection' for f in u['facts'])
                     and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.BANDAGE_INFECTION}]
        text = '상처에 감을 수 있다' if locale == 'ko' else 'It can be wrapped around wounds'
        if preparation:
            text += '. 소독해서 쓸 수도 있다' if locale == 'ko' else '. It can also be disinfected before use'
        if infection:
            text += ('. 감염된 상태로 쓰면 상처를 감염시킬 수 있다' if locale == 'ko'
                     else '. If infected, it can infect the wound')
        emit(bandaging + preparation + infection, text)

    if compact:
        medical = select({'apply_bandage', 'apply_splint', 'clean_burn'})
        if medical:
            functions = {f['payload'].get('function') for u in medical for f in u['facts']}
            labels = [lex.pair(pair, locale) for fn, pair in (
                ('apply_bandage', ('붕대', 'bandaging')), ('clean_burn', ('화상 세척', 'cleaning burns')),
                ('apply_splint', ('골절 고정', 'splinting fractures'))) if fn in functions]
            consequences = [u for u in units if not used & set(u['fact_refs'])
                and all(f['fact_kind'] == 'effect' and f['payload'].get('property') in {
                    'burn_wash_requirement', 'additional_pain', 'bandage_patient_infection', 'applied_bandage_life', 'splint_factor'} for f in u['facts'])]
            emit(medical + consequences, ', '.join(labels) + '에 쓸 수 있다' if locale == 'ko'
                 else 'It can be used for ' + en.join(labels))
        patch = select({'apply_garment_patch'})
        emit(patch, '의류의 구멍을 덧대거나 패딩을 추가할 수 있다' if locale == 'ko'
             else 'It can be used to patch garment holes or add padding')

    burns = select({'clean_burn'})
    if burns:
        consequences = [u for u in units if not used & set(u['fact_refs'])
            and all(f['fact_kind'] == 'effect' and f['payload'].get('property') in {'burn_wash_requirement', 'additional_pain'} for f in u['facts'])
            and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.BURN_CLEANING}]
        emit(burns + consequences, '세척이 필요한 화상을 씻는 데 쓸 수 있다' if locale == 'ko'
             else 'It can be used to clean burns that need washing')

    ropes = select({'supply_escape_rope', 'remove_installed_escape_rope', 'start_escape_rope_ascent'})
    if {f['payload'].get('function') for u in ropes for f in u['facts']} == {
            'supply_escape_rope', 'remove_installed_escape_rope', 'start_escape_rope_ascent'}:
        text = ('설치해 위층으로 올라가는 데 사용할 수 있다' if locale == 'ko'
                else 'It can be installed for climbing to an upper floor')
        if not compact:
            text += ('. 설치한 로프를 제거할 수 있다' if locale == 'ko'
                     else '. Once installed, it can be removed')
        emit(ropes, text)

    furniture = select({'place_moveable_furniture', 'remove_placed_furniture'})
    if {f['payload'].get('function') for u in furniture for f in u['facts']} == {'place_moveable_furniture', 'remove_placed_furniture'}:
        text = ('배치하거나 회수해 옮길 수 있다. 회수 중 파손될 수 있다' if locale == 'ko'
                else 'It can be placed or picked up to move it. Pickup can break it')
        emit(furniture, text)

    maps = select({'view_item_map', 'reveal_item_map_area', 'annotate_item_map', 'erase_item_map_annotations'})
    map_functions = {f['payload'].get('function') for u in maps for f in u['facts']}
    if {'view_item_map', 'annotate_item_map', 'erase_item_map_annotations'} <= map_functions:
        revealed = 'reveal_item_map_area' in map_functions
        text = (('지역 지도를 보고 해당 영역을 알려진 지역으로 표시할 수 있다' if revealed else '내용을 볼 수 있다') +
                '. 필기구로 글·기호를 남기고 지우개로 지울 수 있다') if locale == 'ko' else (
                ('It can be used to view a local map and mark its area as known' if revealed else 'It can be viewed') +
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
            view_text = (('지역 지도를 보고 해당 영역을 알려진 지역으로 표시할 수 있다'
                          if revealed else '내용을 볼 수 있다') if locale == 'ko' else
                         ('It can be used to view a local map and mark its area as known'
                          if revealed else 'It can be viewed'))
            emit(viewing, view_text)
            emit([u for u in maps if u not in viewing],
                 '필기구로 글·기호를 남기고 지우개로 지울 수 있다' if locale == 'ko'
                 else 'Notes or symbols can be added with a writing implement and removed with an eraser')

    nets = select({'place_fishing_net', 'check_fishing_net', 'remove_fishing_net'})
    if {f['payload'].get('function') for u in nets for f in u['facts']} == {'place_fishing_net', 'check_fishing_net', 'remove_fishing_net'}:
        text = ('물에 설치해 미끼 물고기를 잡을 수 있다. 어망이 파손될 수 있다' if locale == 'ko'
                else 'It can be placed in water to catch bait fish. The net can break')
        if not compact:
            text += ('. 설치한 어망을 회수할 수 있다' if locale == 'ko'
                     else '. The placed net can be retrieved')
        emit(nets, text)

    protection = select({'provide_equipped_rain_protection', 'reduce_foraging_rain_effect'})
    if len(protection) == 2:
        text = ('어느 손이든 들고 있으면 비를 가릴 수 있으며, 비가 야외 채집에 주는 불이익을 줄인다' if locale == 'ko'
                else 'Held in either hand, it can provide rain protection and reduces the rain contribution to outdoor foraging penalties')
        emit(protection, text)

    writing = select({'write_note_pages', 'annotate_map'})
    if len(writing) == 2:
        if not compact:
            emit([u for u in writing if 'write_note_pages' in purpose_tokens(u)],
                 '편집 가능한 메모를 작성할 수 있다' if locale == 'ko' else 'It can be used to write editable notes')
            emit([u for u in writing if 'annotate_map' in purpose_tokens(u)],
                 '지도에 글이나 기호를 남길 수 있다' if locale == 'ko'
                 else 'It can be used to add map text or symbols')
        else:
            emit(writing, '편집 가능한 메모를 쓰거나 지도에 글이나 기호를 남길 수 있다' if locale == 'ko'
                 else 'It can be used to write editable notes and add map text or symbols')

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
                if matches:
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
            emit(operations, ', '.join(words) + '에 사용할 수 있다' if locale == 'ko' else 'It can be used for ' + en.join(words), ordered=True)


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
        emit(storage, '물건을 보관하고 담은 채로 운반할 수 있다' if locale == 'ko' else
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
        if not compact:
            emit(members, lex.pair(wording, locale))

    # Tool participation and tool actions share the same subject. Group their
    # purposes, not their inventory/skill checks; never absorb an extra scope.
    if compact:
        tools = [u for u in units if not set(u['fact_refs']) & used
                 and {f['payload'].get('role') for f in u['facts'] if f['fact_kind'] == 'context_role'} == {'tool'}
                 and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} <= CONSTRUCTION_PREDICATES | TOOL_DETAIL_PREDICATES]
        additional_actions = {
            'convert_lamp_to_battery': ('조명 개조', 'converting lamps to battery power'),
            'dismantle_built_object': ('건축물 분해', 'dismantling structures'),
            'manage_weapon_attachments': ('호환 무기 부착물 장착과 제거', 'installing or removing compatible weapon parts'),
            'service_vehicle_parts': ('차량 부품 장착과 탈거', 'installing or removing vehicle parts'),
            'groom_beard': ('수염 손질·면도', 'trimming or shaving a beard'),
            'groom_hair': ('머리 손질', 'hair grooming'),
            'cut_bushes_and_vines': ('덤불·덩굴 제거', 'removing bushes and vines'),
        }
        actions = select({'build_wooden_barricade', 'remove_barricade', 'melee_attack'} | additional_actions.keys())
        if tools and actions:
            activities = sorted({f['payload']['activity'] for u in tools for f in u['facts'] if 'activity' in f['payload']}
                                | {(u.get('context') or {}).get('activity') for u in tools} - {None})
            labels, activity_order = tool_purposes(tools, locale, with_order=True)
            action_names = []
            functions = {f['payload'].get('function') for u in actions for f in u['facts']}
            if {'build_wooden_barricade', 'remove_barricade'} <= functions:
                action_names.append(('문과 창문의 판자 바리케이드 설치와 철거', 'installing or removing plank barricades on doors and windows'))
            elif 'build_wooden_barricade' in functions:
                action_names.append(('문과 창문의 판자 바리케이드 설치', 'installing plank barricades on doors and windows'))
            elif 'remove_barricade' in functions:
                action_names.append(('판자 바리케이드 철거', 'removing plank barricades'))
            other_functions = functions & additional_actions.keys()
            if {'manage_weapon_attachments', 'service_vehicle_parts'} <= other_functions:
                action_names.append(('차량 부품과 호환 무기 부착물의 탈부착', 'fitting and removing vehicle parts and compatible weapon attachments'))
                other_functions -= {'manage_weapon_attachments', 'service_vehicle_parts'}
            if {'groom_beard', 'groom_hair'} <= other_functions:
                action_names.append(('머리와 수염 손질', 'hair and beard grooming'))
                other_functions -= {'groom_beard', 'groom_hair'}
            action_names += [additional_actions[f] for f in sorted(other_functions)]
            if 'melee_attack' in functions:
                action_names.append(('근접 공격', 'melee attacks'))
            tools += [u for u in units if not set(u['fact_refs']) & used and u not in tools
                      and not any(f['fact_kind'] == 'context_role' for f in u['facts'])
                      and any(f['payload'].get('activity') in activities for f in u['facts'])
                      and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} <= CONSTRUCTION_PREDICATES | TOOL_DETAIL_PREDICATES]
            # Keep top-level purposes distinct from their member operations.
            # Electronic salvage and radio/TV salvage share an electronic-device
            # parent; lamp conversion joins that purpose without disappearing.
            action_labels = [lex.pair(n, locale) for n in action_names]
            melee_label = '근접 공격' if locale == 'ko' else 'melee attacks'
            if melee_label in action_labels:
                action_labels.remove(melee_label)
            def absorb(action, prefix):
                label = lex.pair(additional_actions[action], locale)
                target = next((n for n,t in enumerate(labels) if t.startswith(prefix)), None)
                if label in action_labels and target is not None:
                    if locale == 'ko':
                        labels[target] += ', ' + label
                    elif action == 'convert_lamp_to_battery':
                        operations = 'assembly and dismantling' if {'electronic_salvage', 'radio_salvage'} & set(activities) else 'assembly'
                        labels[target] += ', lamp conversion to battery power'
                    else:
                        labels[target] += ', structure disassembly'
                    action_labels.remove(label)
            absorb('convert_lamp_to_battery', '전자기기' if locale == 'ko' else 'making')
            absorb('dismantle_built_object', '목공' if locale == 'ko' else 'woodworking')
            purposes = labels + action_labels
            watermelon = 'watermelon_breaking' in activities and lex.pair(('수박 쪼개기', 'breaking a watermelon'), locale) in purposes
            if watermelon:
                purposes.remove(lex.pair(('수박 쪼개기', 'breaking a watermelon'), locale))
            text = (', '.join(purposes) + '에 쓸 수 있다' if locale == 'ko' else
                    'It can be used for ' + '; '.join(purposes)) if purposes else ''
            if watermelon:
                text += ('. ' if text else '') + lex.pair(('수박을 쪼개는 데 쓸 수 있다', 'It can be used to break a watermelon'), locale)
            extra = []
            if attachments:
                extra.append('제작한 창에 부착' if locale == 'ko' else 'be attached to a crafted spear')
            if 'melee_attack' in functions:
                extra.append('be used as a weapon' if locale == 'en' else '무기로 쓸')
            if extra:
                if locale == 'ko':
                    text += ('. 제작한 창에 부착하거나 무기로 쓸 수도 있다' if attachments and 'melee_attack' in functions else
                             '. 무기로도 쓸 수 있다' if 'melee_attack' in functions else '. 제작한 창에 부착할 수도 있다')
                else:
                    text += '. It can also ' + ' or '.join(extra)
            ordered_tools = sorted(tools, key=lambda u: min(activity_order.index(a) for a in purpose_tokens(u) if a in activity_order))
            # The overview explicitly names lamp conversion beside electronics
            # and disassembly beside woodworking, then vehicle/weapon work.
            members = list(ordered_tools)
            remaining_actions = list(actions)
            for fn, contexts in (('convert_lamp_to_battery', {'electronic_assembly', 'radio_crafting', 'electronic_salvage', 'radio_salvage'}),
                                 ('dismantle_built_object', {'woodworking', 'construction', 'carpentry_menu_construction', 'moving_furniture'})):
                selected = [u for u in remaining_actions if fn in purpose_tokens(u)]
                positions = [n for n, u in enumerate(members) if purpose_tokens(u) & contexts]
                if positions:
                    place = max(positions) + 1
                    members[place:place] = selected
                    remaining_actions = [u for u in remaining_actions if u not in selected]
            members += [u for u in adjacent(remaining_actions, purpose_tokens) if 'melee_attack' not in purpose_tokens(u)]
            members += attachments + [u for u in remaining_actions if 'melee_attack' in purpose_tokens(u)]
            emit(members, text, ordered=True)

    if compact and attachments and not any(set(u['fact_refs']) & used for u in attachments):
        emit(attachments, '제작한 창에 부착해 쓸 수 있다' if locale == 'ko' else 'It can be attached to a crafted spear')


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
        if 'wash_equipment' in functions: targets.append(('의류·장비', 'clothing and equipment'))
        emit(washing, ('몸과 의류, 장비를 물로 씻을 때 세척제로 사용할 수 있다' if len(targets) == 2 else targets[0][0] + '를 물로 씻을 때 세척제로 사용할 수 있다')
             if locale == 'ko' else 'It can be used as a cleaning supply for washing ' + en.join([t[1] for t in targets]) + ' with water')
    if compact and select(FUEL) and select(TINDER):
        emit(select(FUEL) + select(TINDER), '연료나 불쏘시개로 쓸 수 있다' if locale == 'ko' else 'It can be used as fuel or tinder')
    if not compact and select(FUEL) and select(TINDER):
        fuel, tinder = select(FUEL), select(TINDER)
        fuel_targets = list(dict.fromkeys(lex.pair(FUEL[f['payload']['function']], locale) for u in fuel for f in u['facts']))
        tinder_targets = list(dict.fromkeys(lex.pair(TINDER[f['payload']['function']], locale) for u in tinder for f in u['facts']))
        shared = [target for target in fuel_targets if target in tinder_targets]
        if shared:
            groups = [(shared, ('연료나 불쏘시개', 'fuel or tinder')),
                      ([t for t in fuel_targets if t not in shared], ('연료', 'fuel')),
                      ([t for t in tinder_targets if t not in shared], ('불쏘시개', 'tinder'))]
            clauses = [('·'.join(targets) + '의 ' + role[0] if locale == 'ko' else role[1] + ' for ' + ', '.join(targets))
                       for targets, role in groups if targets]
            emit(fuel + tinder, (', '.join(clauses) + '로 쓸 수 있다') if locale == 'ko' else
                 'It can be used as ' + '; '.join(clauses))
    for functions, role in ((FUEL, ('연료', 'fuel')), (TINDER, ('불쏘시개', 'tinder'))):
        members = select(functions)
        if not members: continue
        targets = [lex.pair(functions[f['payload']['function']], locale) for u in members for f in u['facts']]
        text = role[0] + '로 소모할 수 있다' if locale == 'ko' else 'It can be consumed as ' + role[1]
        if not compact:
            text = '·'.join(dict.fromkeys(targets)) + '의 ' + role[0] + '로 소모할 수 있다' if locale == 'ko' else text + ' for ' + en.join(list(dict.fromkeys(targets)))
        emit(members, text)
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
        recovered = compact_recovery if compact else recovered_name
        if fabric_dirty and not compact:
            recovered += (' 또는 ' if locale == 'ko' else ' or ') + fabric_dirty['names'][locale]
        text = (('가위로 ' if needs_scissors else '') + '찢어서 ' + object_name(recovered) + ' 얻을 수 있다') if locale == 'ko' else (
            'It can be ripped' + (' with scissors' if needs_scissors else '') + ' to obtain ' + recovered)
        emit(fabric, text)
    rope_materials = [u for u in rope_uses if not used & set(u['fact_refs'])]
    if rope_materials:
        emit(rope_materials, '시트 로프 제작 재료로 쓸 수 있다' if locale == 'ko'
             else 'It can be used' + ' as material for making sheet rope')
    friction = select({'light_campfire_by_friction', 'kindle_heat_sources'})
    if len(friction) == 2:
        text = ('나무 마찰로 불 피우기를 시도할 수 있다' if locale == 'ko' else
                'It can be used to attempt lighting fires by wood friction') if compact else (
                '나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다' if locale == 'ko' else
                'It can be used to attempt wood-friction ignition of campfires, non-propane barbecues, fireplaces, and drums containing logs')
        if not compact:
            text += '. 시도 중 지구력이 줄고 막대가 부러질 수 있다' if locale == 'ko' else '. Attempts spend endurance and may break the stick'
        emit(friction, text)
    plumbing = select({'plumb_external_water'})
    if plumbing:
        emit(plumbing, '외부 수원을 받을 수 있는 실내 설비의 배관을 연결할 수 있다' if locale == 'ko' else
             'It can be used to plumb indoor fixtures that accept an external water source')

    # Named ignition branches retain method/target compatibility without the
    # movement, inventory, repeated validity and per-action use-count prose.
    from .description_composition_families import IGNITION, IGNITION_TARGETS
    ignition = select(set(IGNITION) | {'request_corpse_burning'})
    candle_tools = [u for u in units if any(f['payload'].get('activity') == 'candle_lighting' for f in u['facts'])
                    and any(f['payload'].get('role') == 'tool' for f in u['facts'])]
    if compact and ignition:
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
            emit(ignition, '. '.join(clauses))
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
    if cooking_ingredients and included_dough:
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
        emit(washing + matching, '물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다' if locale == 'ko'
             else 'It can be washed with water into clean bandaging material')
    log_members = [u for u in units if not used & set(u['fact_refs']) and 'log_binding' in purpose_tokens(u)]
    unbundle = select({'unbundle_logs'})
    if log_members or unbundle:
        emit(log_members + unbundle, ('묶음을 풀어 통나무와 묶기 재료를 회수할 수 있다' if unbundle else '모아서 묶을 수 있다' if select({'supply_drum_logs'}) else '통나무를 묶는 데 쓸 수 있다')
             if locale == 'ko' else ('It can be unbundled to recover logs and binding materials' if unbundle
                                      else 'It can be bundled with other logs' if select({'supply_drum_logs'}) else 'It can be used to bind logs'))
    light = select({'control_portable_light'})
    own_lighting = select({'light_candle'})
    if light and own_lighting:
        targets = [u for u in units if not used & set(u['fact_refs'])
                   and any(f['payload'].get('activity') == 'candle_lighting' for f in u['facts'])
                   and any(f['payload'].get('role') == 'transformation_target' for f in u['facts'])]
        emit(light + own_lighting + targets, '발화 도구로 불을 붙여 휴대 조명으로 쓸 수 있다' if locale == 'ko'
             else 'It can be lit with a fire-starting item for use as a portable light')
    elif light:
        emit(light, '휴대 조명으로 쓸 수 있다' if locale == 'ko' else 'It can be used as a portable light')
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
        if relation['function'] == 'recipe_use' and (portion_input or processing_input or (upper_food and opened_recipe)):
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
        bowl_substep = (upper_food and 'portion_into_bowls' in functions and
                       ('food_portioning' in purpose_tokens(unit) or supplied_functions == {'portion_into_bowls'}))
        if set(unit['fact_refs']) <= lower_food_refs or bowl_substep:
            category, reason = 'internal', 'food input splitting/processing detail; independent admitted uses, tool roles and receiving vessels remain separate'
        if 'moving_furniture' in purpose_tokens(unit):
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
            if q['payload']['predicate'] in INTERNAL_QUALIFIERS or unrelated_sheet_conversion or other_food_state or vessel_recipe_details or tool_recipe_details:
                public['dispositions'].append({'fact_refs': q['fact_refs'], 'disposition': 'internal',
                    'applies_to_fact_refs': unit['fact_refs'],
                    'reason': 'general execution or redundant named-activity eligibility, not a distinguishing use condition'})
            else:
                if q['payload']['predicate'] not in lex.USE_QUALIFIERS:
                    raise ValueError('unclassified public qualifier: ' + q['payload']['predicate'])
                retained.append(qref)
                public['dispositions'].append({'fact_refs': q['fact_refs'],
                    'applies_to_fact_refs': unit['fact_refs'], 'disposition': 'supporting detail',
                    'reason': 'explicitly adopted use condition; frame or scoped wording owns public realization'})
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
                           if set(u['fact_refs']) & set(segment['fact_refs']))) - {None}
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
    groups = []
    for segment in output:
        if segment.get('continues_use') and groups:
            groups[-1].append(segment)
        else:
            groups.append([segment])
    groups.sort(key=lambda group: any(set(segment['fact_refs']) & transformed for segment in group))
    output = [segment for group in groups for segment in group]
    return output



