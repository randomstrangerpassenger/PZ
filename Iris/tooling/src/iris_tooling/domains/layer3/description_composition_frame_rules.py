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


