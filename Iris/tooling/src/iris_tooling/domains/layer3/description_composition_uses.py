"""Public use frames over structured A relations and admitted participant roles.

Execution evidence stays in the input. Only claims actually expressed are linked
as public facts; no procedure refs are attached to a shorter unrelated sentence.
"""
from copy import deepcopy
import re
from . import description_composition_lexicon as lex
from . import description_composition_en as en
from . import description_composition_ko as ko

FORGING_ACTIVITIES = {'metal_forging', 'shovel_smithing', 'smithing_parts'}

MAINTENANCE = {'wash_carried_equipment', 'receive_garment_patch', 'remove_garment_patch',
               'rename_selected_item', 'rename_prepared_food'}
WASH_RESULTS = {'item_surface_blood', 'clothing_surface_dirt', 'clothing_wetness',
                'washed_surface_blood', 'washed_surface_dirt', 'food_chef_attribution'}
FUEL = {'supply_campfire_fuel': ('모닥불', 'campfires'),
        'supply_hearth_fuel': ('프로판을 쓰지 않는 바비큐와 벽난로', 'non-propane barbecues and fireplaces'),
        'supply_furnace_fuel': ('화로', 'furnaces')}
TINDER = {'provide_campfire_tinder': ('모닥불', 'campfires'),
          'provide_hearth_tinder': ('프로판을 쓰지 않는 바비큐와 벽난로', 'non-propane barbecues and fireplaces'),
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
     'apply_bandage', 'apply_splint', 'apply_poultice', 'bandaging_material_preparation', 'disinfect_wound', 'splint_crafting'),
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
    'avoid_first_door_alarm_trigger', 'pickup_floor_glass',
    'set_device_timer', 'retrieve_placed_device',
    'place_noise_device', 'place_trigger_device',
}
INTERNAL_PROPERTIES = WASH_RESULTS | {
    'treatment_panic', 'additional_pain',
    'written_note_title', 'written_note_pages', 'written_note_lock',
    'reading_page_progress', 'doctor_experience', 'food_preservation_age',
    'fish_size_nutrition', 'installed_vehicle_part_condition',
    'splint_factor', 'poultice_factor', 'applied_bandage_life', 'crop_water_level',
    'installed_vehicle_battery_charge', 'fishing_rod_form',
    'item_condition', 'held_stone_hammer_condition', 'installed_tire_air_or_attachment',
    'hand_scratch', 'hand_embedded_glass', 'delivered_media_code_outcome', 'inventory_presence',
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


def device_category(result, locale):
    traits = result.get('declared_traits', {})
    def positive(key):
        try:
            return float(traits.get(key, 0)) > 0
        except ValueError:
            return False
    for enabled, label in (
        (str(traits.get('RemoteController', '')).lower() == 'true', ('원격 조종기', 'remote controllers')),
        (positive('FirePower'), ('화염 장치', 'incendiary devices')),
        (positive('ExplosionPower'), ('폭발 장치', 'explosive devices')),
        (positive('SmokeRange'), ('연막 장치', 'smoke devices')),
        (positive('NoiseRange'), ('소음 발생 장치', 'noise-making devices')),
    ):
        if enabled:
            return lex.pair(label, locale)
    return None


def activity_labels(unit, locale, compact=False):
    contexts = list(dict.fromkeys(f['payload']['activity'] for f in unit['facts'] if f['fact_kind'] == 'use_context'))
    if not contexts and unit.get('context'):
        contexts = [unit['context']['activity']]
    roles = {f['payload'].get('role') for f in unit['facts']}
    if 'tool' in roles and contexts == ['moving_furniture']:
        return [lex.pair(('일부 가구 집기와 설치', 'picking up or placing certain furniture'), locale)]
    if 'tool' in roles and contexts == ['fabric_recovery'] and all(
            f.get('admission_rule_ref') == 'fabric_conditions' for f in unit['facts']):
        return [lex.pair(('데님이나 가죽 의류 자르기', 'recovering strips from denim or leather clothing'), locale)]
    relations = unit.get('recipe_targets', [])
    targets = {r['item_id']: r['names'][locale] for relation in relations
               for r in relation['results'] if r['kind'] == 'declared'}
    exact = bool(targets) and all(len(r['results']) == 1 and r['results'][0]['kind'] == 'declared'
                                  for r in relations)
    if contexts in (['electronic_assembly'], ['explosive_assembly']) and exact:
        labels = list(dict.fromkeys(device_category(r, locale) or (r['names'][locale] if locale == 'ko' else en.object_phrase(r))
                                   for relation in relations for r in relation['results']))
        return [label + ' 제작' if locale == 'ko' else 'making ' + label for label in labels]
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
    if contexts == ['pumpkin_carving'] and exact and len(targets) == 1:
        name = next(iter(targets.values()))
        return [name + ' 만들기' if locale == 'ko' else 'making ' + name]
    if contexts == ['grain_preparation'] and unit.get('subject_names') and 'ingredient' in roles:
        return [lex.pair(('요리 준비', 'preparing dishes'), locale)]
    if contexts == ['tent_kit_making'] and exact:
        return [lex.pair(('텐트', 'tents'), locale)]
    if not compact and contexts == ['food_portioning'] and 'tool' in roles:
        foods = {i['item_id']: i['names'][locale] for rel in relations for i in rel.get('inputs', [])
                 if i['declared_traits'].get('Type') == 'Food'}
        if foods:
            labels = list(dict.fromkeys(n if locale == 'ko' else n.lower() for n in foods.values()))
            names = ', '.join(labels) if locale == 'ko' else en.join(labels)
            return [ko.object_name(names) + ' 나누는 데' if locale == 'ko' else 'cutting up ' + names]
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
    family(FORGING_ACTIVITIES, '금속 단조', 'metal forging')
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
        labels.append(lex.pair(('목공과 건축' if 'woodworking' in woodworking and len(woodworking)>1 else '목공' if woodworking=={'woodworking'} else '건축',
                               'woodworking and construction' if 'woodworking' in woodworking and len(woodworking)>1 else 'woodworking' if woodworking=={'woodworking'} else 'construction'), locale))
    if woodworking and 'moving_furniture' in remaining:
        remaining.remove('moving_furniture')
        order.append('moving_furniture')
        if locale == 'ko':
            labels[-1] += '·가구 작업'
        else:
            labels[-1] = ('woodworking, construction and furniture work' if len(woodworking)>1 else 'woodworking and furniture work' if woodworking=={'woodworking'} else 'construction and furniture work')
    if {'fishing_gear_crafting', 'spear_crafting'} <= remaining:
        family({'fishing_gear_crafting', 'spear_crafting'}, '낚시 장비와 창 제작', 'fishing-gear and spear crafting')
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
            if payload.get('property') in INTERNAL_PROPERTIES or payload.get('direction') == 'cap_at_reading_start':
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


def target_groups(targets, locale, introduction):
    """Group already admitted repair targets; labels never infer compatibility."""
    labels = {
        'vehicle': ('차량 부품', 'Vehicle parts'), 'instrument': ('악기', 'Musical instruments'),
        'sport': ('스포츠 용품', 'Sports equipment'), 'gardening': ('원예 도구', 'Gardening tools'), 'spear': ('창', 'Spears'),
        'axe': ('도끼', 'Axes'), 'blade': ('칼날 도구', 'Bladed tools'),
        'blunt': ('둔기와 도구', 'Blunt weapons and tools'), 'other': ('그 밖의 대상', 'Other listed items'),
    }
    records = {}
    for target in targets:
        fields = target.get('declared_traits', {})
        categories = set(fields.get('Categories', '').split(';'))
        display = fields.get('DisplayCategory')
        tags = set(fields.get('Tags', '').split(';'))
        key = ('vehicle' if display == 'VehicleMaintenance' else 'instrument' if display == 'Instrument' else
               'sport' if display == 'Sports' else 'gardening' if display == 'Gardening' or 'DigPlow' in tags else
               'spear' if 'Spear' in categories else
               'axe' if 'Axe' in categories else 'blade' if categories & {'SmallBlade', 'LongBlade'} else
               'blunt' if categories & {'Blunt', 'SmallBlunt'} else 'other')
        name = target['names'][locale]
        record = records.setdefault(name, {'label': name, 'item_ids': [], 'categories': set()})
        if target['item_id'] not in record['item_ids']:
            record['item_ids'].append(target['item_id'])
        record['categories'].add(key)
    return grouped_detail(records, labels, locale, introduction)


def grouped_detail(records, labels, locale, introduction):
    buckets = {key: [] for key in labels}
    for record in records.values():
        keys = record.pop('categories')
        key = next(iter(keys)) if len(keys) == 1 else 'other'
        buckets[key].append(record)
    groups = [{'key': key, 'label': lex.pair(labels[key], locale), 'entries': entries, 'count': len(entries), 'presentation': 'inline' if len(entries) == 1 else 'disclosure'}
              for key, entries in buckets.items() if entries]
    return {'introduction': introduction, 'groups': groups, 'group_count': len(groups)}


def learning_groups(recipes, locale, introduction):
    """Group admitted lessons by declared result categories, preserving recipe keys.

    Fold when distinct named families each contain related lessons. A long
    homogeneous list, unrelated singletons or unknown outputs offer no benefit.
    Declared results classify existing lessons; they never add result-use facts.
    """
    labels = {'material': ('재료', 'Materials'), 'household': ('생활용품', 'Household items'),
              'cooking': ('조리용품', 'Cooking items'), 'food': ('음식', 'Food'),
              'medical': ('응급처치 용품', 'First-aid supplies'),
              'tools': ('도구와 무기', 'Tools and weapons'),
              'ammo': ('탄약 관련 물품', 'Ammunition-related items'),
              'sports': ('스포츠 용품', 'Sports equipment'),
              'electronic': ('전자 장치', 'Electronic devices'),
              'explosive': ('폭발물과 장치', 'Explosives and devices'),
              'fishing': ('낚시 장비', 'Fishing equipment'), 'trapping': ('덫', 'Traps'),
              'other': ('그 밖의 학습 항목', 'Other lessons')}
    categories = {'Material': 'material', 'Household': 'household', 'Cooking': 'cooking', 'Food': 'food',
                  'FirstAid': 'medical', 'Tool': 'tools', 'ToolWeapon': 'tools', 'Weapon': 'tools',
                  'Gardening': 'tools', 'Ammo': 'ammo', 'Sports': 'sports', 'Electronics': 'electronic',
                  'Explosives': 'explosive', 'Fishing': 'fishing', 'Trapping': 'trapping'}
    records = {}
    for recipe in recipes:
        name = recipe['names'][locale]
        record = records.setdefault(name, {'label': name, 'recipe_keys': [], 'categories': set()})
        record['recipe_keys'].append(recipe['key'])
        results = recipe.get('declared_results', [])
        record['categories'].update(categories.get(x['declared_traits'].get('DisplayCategory'), 'other') for x in results)
        if not results:
            record['categories'].add('other')
    detail = grouped_detail(records, labels, locale, introduction)
    coherent = [g for g in detail['groups'] if g['key'] != 'other' and g['count'] > 1]
    return detail if len(coherent) > 1 else None


def scoped_groups(source_groups, entries, locale, introduction):
    """Keep the source's mapped/some scope beside each existing target name."""
    records, labels, scopes = {}, {}, {}
    position = 0
    for ordinal, group in enumerate(source_groups):
        key = 'scope_' + str(ordinal + 1)
        labels[key] = tuple(('일부 ' if lang == 'ko' else 'Some ') + (', '.join(t[lang] for t in group['targets']) if lang == 'ko' else en.join([t[lang] for t in group['targets']]))
                            if group['scope'] == 'some' else (', '.join(t[lang] for t in group['targets']) if lang == 'ko' else en.join([t[lang] for t in group['targets']])) for lang in ('ko', 'en'))
        scopes[key] = group['scope']
        for target in group['targets']:
            name = entries[position]
            position += 1
            records[name] = {'label': name, 'target_keys': [target['key']], 'categories': {key}}
    detail = grouped_detail(records, labels, locale, introduction)
    for group in detail['groups']:
        group['scope'] = scopes[group['key']]
    return detail


def detail_text(summary, introduction, entries, *, compact, relationship, inline=None):
    """Choose structure by the relationship, never by text length or item ID.

    Lessons have individual contents. Scoped target groups need their scope
    beside each name; heterogeneous compatibility sets need named choices.
    A single action with a homogeneous target family stays an inline sentence.
    """
    if compact:
        return summary
    if relationship == 'homogeneous_targets':
        return inline or summary
    if relationship not in {'learning_content', 'scoped_target_groups', 'compatibility_choices'}:
        raise ValueError('unreviewed public detail relationship: ' + relationship)
    if not entries:
        return inline or summary
    return introduction.rstrip('.') + '.\n' + '\n'.join('- ' + entry for entry in entries)


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

    transmission = select({'toggle_radio_microphone'})
    if transmission:
        emit(transmission, lex.pair(('무전으로 말을 송신할 수 있다' if compact else
             '전원을 켜고 마이크 음소거를 해제하면 말을 송신할 수 있다. 같은 주파수에 맞춘 통신 범위 안의 무전기로 받을 수 있다',
             'It can transmit speech by radio' if compact else
             'When powered on with its microphone unmuted, it can transmit speech to radios tuned to the same frequency within range'), locale))
    media = select({'control_device_media', 'tune_radio', 'select_tv_channel'})
    if media:
        media_functions = {f['payload'].get('function') for u in media for f in u['facts']}
        media_type = plan.get('source_traits', {}).get('AcceptMediaType')
        actions = [('control_device_media', ('기록 매체 재생', 'playing CDs' if media_type == '0' else 'playing VHS tapes' if media_type == '1' else 'playing compatible recordings')),
                   ('tune_radio', ('라디오 방송 청취', 'listening to radio broadcasts')),
                   ('select_tv_channel', ('TV 방송 시청', 'watching television broadcasts'))]
        labels = [lex.pair(pair, locale) for fn, pair in actions if fn in media_functions]
        text = ('' + '·'.join(labels) + '에 쓸 수 있다') if locale == 'ko' else ('It can be used for ' + en.join(labels))
        if locale == 'ko':
            verbs = []
            if 'control_device_media' in media_functions:
                media_type = plan.get('source_traits', {}).get('AcceptMediaType')
                verbs.append('CD에 담긴 소리를 재생' if media_type == '0' else 'VHS 테이프에 담긴 영상을 재생' if media_type == '1' else '기록된 내용을 재생')
            if 'tune_radio' in media_functions:
                verbs.append('라디오 방송을 청취')
            if 'select_tv_channel' in media_functions:
                verbs.append('TV 방송을 시청')
            text = '' + '하거나 '.join(verbs) + '할 수 있다'
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
        category = plan.get('source_traits', {}).get('MediaCategory')
        if category == 'CDs':
            text = ('CD 플레이어로 녹음된 소리를 들을 수 있다' if locale == 'ko' else 'Its recorded audio can be heard with a CD player')
        elif category in {'Home-VHS', 'Retail-VHS'}:
            text = ('VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다' if locale == 'ko' else 'Its recorded video can be watched on a TV that supports VHS playback')
        else:
            text = ('호환 기기로 녹음·녹화된 내용을 감상할 수 있다' if locale == 'ko' else 'Its recording can be enjoyed with a compatible player')
        if outcomes:
            text += ('. 내용에 따라 능력치·경험치·제작법 학습 효과를 얻을 수 있다' if locale == 'ko'
                     else '. Depending on the content, it can affect stats, XP or recipe knowledge')
        content = select({fn for fn in functions if fn and fn.startswith('recorded_content_')})
        content_fns = {f['payload']['function'].removeprefix('recorded_content_') for u in content for f in u['facts']}
        positive = []
        if 'boredom' in content_fns:
            positive.append(('지루함을 달래', 'relieve boredom'))
        if {'skills', 'recipes'} <= content_fns:
            positive.append(('기술과 제작법을 배우', 'learn skills and recipes'))
        elif 'skills' in content_fns:
            positive.append(('기술을 익히', 'develop skills'))
        elif 'recipes' in content_fns:
            positive.append(('제작법을 배우', 'learn recipes'))
        if positive:
            text += ('. 내용에 따라 ' + '거나 '.join(v[0] for v in positive) + '는 데도 쓸 수 있다') if locale == 'ko' else '. Depending on the recording, it can also help you ' + ' or '.join(v[1] for v in positive)
            if compact and category in {'Home-VHS', 'Retail-VHS'} and not outcomes:
                endings = {'지루함을 달래': '지루함을 달랠', '기술과 제작법을 배우': '기술과 제작법을 배울',
                           '기술을 익히': '기술을 익힐', '제작법을 배우': '제작법을 배울'}
                ability = '거나 '.join([v[0] for v in positive[:-1]] + [endings[positive[-1][0]]])
                text = ('녹화 영상을 감상하고, 내용에 따라 ' + ability + ' 수 있다') if locale == 'ko' else ('Its video can be enjoyed and, depending on the recording, help you ' + ' or '.join(v[1] for v in positive))
        if not compact and {'stress', 'panic'} <= content_fns:
            text += lex.pair(('. 일부 내용은 스트레스나 공포를 느끼게 할 수 있다', '. Some recordings can also cause stress or panic'), locale)
        elif not compact and 'stress' in content_fns:
            text += lex.pair(('. 일부 내용은 스트레스를 느끼게 할 수 있다', '. Some recordings can also cause stress'), locale)
        emit(recordings + outcomes + content, text)

    alarms = select({'set_alarm', 'stop_alarm'})
    if {f['payload'].get('function') for u in alarms for f in u['facts']} == {'set_alarm', 'stop_alarm'}:
        emit(alarms, '원하는 시각에 알람이 울리도록 맞추거나 알람을 끌 수 있다' if locale == 'ko'
             else 'Its alarm can be set to ring at a chosen time or switched off')

    dismantled = select({'dismantle_electronics'})
    salvage_targets = [u for u in units if not used & set(u['fact_refs'])
        and any(f['payload'].get('activity') in {'electronic_salvage', 'radio_salvage'} for f in u['facts'])
        and any(f['payload'].get('role') == 'transformation_target' for f in u['facts'])]
    if dismantled and salvage_targets:
        text = '드라이버로 분해해 전자 부품을 얻을 수 있다' if locale == 'ko' else 'It can be dismantled with a screwdriver to recover electronic parts'
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
        text = '상처를 덮어 처치할 수 있다' if locale == 'ko' else 'It can be used to cover and dress wounds'
        if preparation:
            text += '. 소독해서 쓸 수도 있다' if locale == 'ko' else '. It can also be disinfected before use'
        if infection and not compact:
            text += ('. 감염된 재료를 쓰면 상처가 감염될 수 있다' if locale == 'ko'
                     else '. Infected material can cause wound infection')
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
        emit(burns + consequences, '화상을 씻는 데 쓸 수 있다' if locale == 'ko'
             else 'It can be used to clean burns')

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
