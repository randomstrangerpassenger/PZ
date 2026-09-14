"""Produce once, persist, and read descriptions without invoking a producer."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from . import composition_results as inputs
from . import description_composition_model as model
from . import description_composition_planner as planner
from . import description_composition_lexicon as lex
from . import description_composition_ko as ko
from . import description_composition_en as en
from . import description_composition_families as families
from . import description_composition_uses as uses
from .composition_model import canonical

DEFAULT_OUTPUT = "Iris/build/description/composition/descriptions.json"
CODE = "Iris/tooling/src/iris_tooling/domains/layer3/"


def _links(units, plan):
    result = {name: sorted({v for u in units for v in u[name]})
              for name in ("block_refs", "branch_refs", "fact_refs", "qualifier_refs", "relation_refs")}
    result['qualifier_refs'] = [q for q in result['qualifier_refs'] if lex.public_qualifier(plan['qualifiers'][q])]
    result["qualifier_applications"] = [{"qualifier_id": q,
        "applies_to_fact_refs": plan["qualifiers"][q]["applies_to_fact_refs"]} for q in result["qualifier_refs"]]
    result["fact_refs"] = sorted(set(result["fact_refs"]) | {
        ref for q in result["qualifier_refs"] for ref in plan["qualifiers"][q]["fact_refs"]})
    result['use_order'] = list(dict.fromkeys(r for u in units for r in u['fact_refs']))
    return result


def _role(unit):
    contexts = [f["payload"]["activity"] for f in unit["facts"] if f["fact_kind"] == "use_context"]
    roles = sorted(f["payload"]["role"] for f in unit["facts"] if f["fact_kind"] == "context_role")
    if not contexts and unit.get("context"):
        contexts = [unit["context"]["activity"]]
    return contexts, roles


def _activity_labels(unit, locale, compact=False):
    return uses.activity_labels(unit, locale, compact)


def _forging_tool(units, plan, locale):
    if not units or not all(_role(u) == (['metal_forging'], ['tool']) for u in units):
        return None
    targets = list(dict.fromkeys(r['names'][locale] for u in units for rel in u.get('recipe_targets', [])
                                for r in rel['results'] if r['kind'] == 'declared'))
    if len(targets) != 1:
        return None
    declared_name = plan.get('source_traits', {}).get('display_names', {}).get('en', '')
    mold = declared_name.endswith((' Mold', ' Mould'))
    return (ko.object_name(targets[0]) + ' 단조할 때 ' + ('틀' if mold else '도구') + '로 쓸 수 있다') if locale == 'ko' else ('It can be used as ' + ('a mold' if mold else 'a tool') + ' for forging ' + targets[0])

def _core(unit, locale, compact=False):
    grammar = ko if locale == "ko" else en
    contexts, roles = _role(unit)
    if contexts == ['food_preparation'] and roles == ['ingredient']:
        return lex.pair(('요리 재료로 쓸 수 있다', 'It can be used as a cooking ingredient'), locale)
    if contexts == ['sheet_rope_making'] and roles == ['material']:
        return lex.pair(('아이템 자체를 시트 로프 제작 재료로 쓸 수 있다',
                         'The item itself can be used as material for making sheet rope'), locale)
    if contexts == ['food_ingredient_addition'] and roles == ['base']:
        return lex.pair(('재료를 더해 요리를 만들 수 있다', 'Ingredients can be added to prepare food'), locale)
    if contexts == ['fish_preparation'] and roles == ['ingredient']:
        return lex.pair(('도구로 손질해 생선살을 얻을 수 있다', 'It can be filleted with a cutting tool'), locale)
    if contexts:
        names = _activity_labels(unit, locale, compact)
        if roles:
            return grammar.role(names, roles)
        return names[0] + "에 쓸 수 있다" if locale == "ko" else "It can be used for " + names[0]
    if len(unit["facts"]) != 1:
        raise ValueError("unsupported unbound branch")
    return lex.core(unit["facts"][0], locale, compact)


def _expanded(plan, locale):
    prefix, used = uses.frames(plan, locale, _links, False)
    remaining = dict(plan, units=[u for u in plan['units'] if not set(u['fact_refs']) & used])
    segments = prefix + _expanded_remaining(remaining, locale)
    supporting = {r for u in plan['units'] if u.get('public_disposition') == 'supporting detail' for r in u['fact_refs']}
    anchors = {r for u in plan['units'] for r in u['fact_refs']}
    return sorted(segments, key=lambda s: bool(set(s['fact_refs']) & anchors)
                  and (set(s['fact_refs']) & anchors) <= supporting)


def _expanded_remaining(plan, locale):
    grammar = ko if locale == "ko" else en
    segments, used = families.detail_frames(plan, locale, _links)
    # A closed semantic frame can express multiple exact application scopes
    # (for example reading and its supported XP multiplier). Reuse it only
    # when it actually contains all of its selected public conditions; frames
    # delegating detail to expanded cannot satisfy their own delegation here.
    candidates, _ = families.frames(dict(plan, units=[dict(u, detail_reason=None)
        for u in plan['units'] if not set(u['fact_refs']) & used]), locale, _links, expanded=True)
    for segment in candidates:
        if any(d['placement'] == 'expanded' for d in segment.get('qualifier_dispositions', [])):
            continue
        segments.append(segment)
        used.update(segment['fact_refs'])
    # Frames inspect the full scoped evidence. Fallback cannot turn unused
    # execution predicates into public detail simply because they remain.
    plan = dict(plan, units=[dict(u, qualifier_refs=[q for q in u['qualifier_refs']
                    if lex.public_qualifier(plan['qualifiers'][q])]) for u in plan['units']])
    # A split context and role in the same source branch describe one activity.
    # Keep their exact application records separate, but read the shared
    # conditions once and explicitly continue with the role-only requirements.
    for context in plan['units']:
        activities, roles = _role(context)
        if not activities or roles or set(context['fact_refs']) & used:
            continue
        siblings = [u for u in plan['units'] if u is not context and
                    u['branch_refs'] == context['branch_refs'] and _role(u)[0] == activities
                    and _role(u)[1] and not set(u['fact_refs']) & used]
        if not siblings:
            continue
        role = siblings[0]
        shared = {plan['qualifiers'][q]['payload']['predicate'] for q in context['qualifier_refs']}
        role_predicates = {plan['qualifiers'][q]['payload']['predicate'] for q in role['qualifier_refs']}
        if not shared and len(siblings) == 1:
            # The bare context and its role are the same source-branch use.
            # Keep the qualifier application on the role, not on the context.
            conditions = lex.qualifier_clauses([plan['qualifiers'][q] for q in role['qualifier_refs']], locale)
            segments.append({'text': grammar.qualified([_core(role, locale)], conditions),
                             **_links([context, role], plan), 'expression': 'context_role_scope'})
            used.update(context['fact_refs'] + role['fact_refs'])
            continue
        if not shared or not shared <= role_predicates or any(
            {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} != role_predicates for u in siblings):
            continue
        conditions = lex.qualifier_clauses([plan['qualifiers'][q] for q in context['qualifier_refs']], locale)
        segments.append({'text': grammar.qualified([_core(context, locale)], conditions),
                         **_links([context], plan), 'expression': 'exact_scope'})
        extra = lex.qualifier_clauses([plan['qualifiers'][q] for q in role['qualifier_refs']
                     if plan['qualifiers'][q]['payload']['predicate'] not in shared], locale)
        role_core = grammar.role(_activity_labels(role, locale), _role(role)[1])
        continuation = ('앞의 조건에서 ' + role_core if locale == 'ko' else 'Under those conditions, ' + role_core[0].lower() + role_core[1:])
        segments.append({'text': grammar.qualified([continuation], extra),
                         **_links([role], plan), 'expression': 'exact_scope'})
        used.update(context['fact_refs'] + role['fact_refs'])
        for other in siblings[1:]:
            other_core = grammar.role(_activity_labels(other, locale), _role(other)[1])
            continuation = ('같은 조건에서 ' + other_core if locale == 'ko' else 'Under the same conditions, ' + other_core[0].lower() + other_core[1:])
            segments.append({'text': continuation + '.', **_links([other], plan), 'expression': 'exact_scope'})
            used.update(other['fact_refs'])
    groups = defaultdict(list)
    for unit in plan["units"]:
        if set(unit['fact_refs']) & used:
            continue
        contexts, roles = _role(unit)
        # Exact qualifier identity and class delimit the scope of sharing.
        # Equal grammatical roles do not make furniture moving and radio
        # crafting one use. Share only the same activity and condition meaning.
        family = ("role", tuple(roles), tuple(contexts)) if contexts and roles else (
            "clauses", canonical([f['payload'] for f in unit['facts']]))
        candle_activity = {"light_candle": "candle_lighting", "extinguish_candle": "candle_extinguishing"}.get(
            unit["facts"][0]["payload"].get("function"))
        if candle_activity:
            family = ("candle", candle_activity)
        elif roles == ["transformation_target"] and contexts in (["candle_lighting"], ["candle_extinguishing"]):
            family = ("candle", contexts[0])
        if unit["facts"][0]["fact_kind"] == "acquisition":
            family = ("route", tuple(unit["fact_refs"]))
        scope = canonical([plan['qualifiers'][q]['payload'] for q in unit['qualifier_refs']])
        groups[(scope, family)].append(unit)
    for (_, family), units in sorted(groups.items(), key=lambda entry:
            min({'use': 0, 'result/target': 1, 'supporting detail': 2}.get(u.get('public_disposition'), 3) for u in entry[1])):
        qrefs = tuple(units[0]['qualifier_refs'])
        if family[0] == "candle" and len(units) > 1:
            clauses = [lex.pair(("초에 불을 붙일 수 있다", "The candle can be lit") if family[1] == "candle_lighting"
                               else ("켜진 초를 끄는 제작법에 쓸 수 있다", "It can be supplied to the lit-candle extinguishing recipe"), locale)]
        elif family[0] == "role":
            activities = [label for u in units for label in _activity_labels(u, locale)]
            # Equal activity names only coalesce with equal role AND scope.
            clauses = ([_core(units[0], locale)] if all(_role(u) in ((['food_ingredient_addition'], ['base']), (['sheet_rope_making'], ['material']), (['fish_preparation'], ['ingredient'])) for u in units)
                       else [grammar.role(list(dict.fromkeys(activities)), list(family[1]))])
        else:
            clauses = _clauses(units, plan, locale)
        # The unresolved wear statement is independently worded with its
        # possibility qualifier; do not restate it as a fishing consequence.
        independent_wear = (len(units) == 1 and units[0]["facts"][0]["payload"] ==
                            {"property": "item_condition", "direction": "decrease"}
                            and any(plan["qualifiers"][q]["payload"]["predicate"] == lex.source.SPEAR_FISHING_WEAR for q in qrefs))
        spear_tool_wear = (len(units) == 1 and units[0]["facts"][0]["payload"] ==
                           {"property": "item_condition", "direction": "decrease"}
                           and any(plan["qualifiers"][q]["payload"]["predicate"] == lex.source.SPEAR_TOOL_WEAR for q in qrefs))
        rod_break = all(f['payload'] == {'property': 'fishing_rod_form', 'direction': 'replace_on_line_break'} for u in units for f in u['facts'])
        if independent_wear or spear_tool_wear or rod_break:
            clauses = [lex.qualifier(plan["qualifiers"][q], locale) for q in qrefs]
            conditions = []
        else:
            mood_cap = all(f['fact_kind'] == 'effect' and f['payload'].get('direction') == 'cap_at_reading_start'
                           for u in units for f in u['facts'])
            chef_transfer = all(f['payload'] == {'property': 'food_chef_attribution', 'direction': 'set_transferring_character'}
                                for u in units for f in u['facts'])
            fish_size = all(f['payload'] == {'property': 'fish_size_nutrition', 'direction': 'initialize_from_registered_size'}
                            for u in units for f in u['facts'])
            conditions = lex.qualifier_clauses([plan["qualifiers"][q] for q in qrefs
                if not (mood_cap and plan['qualifiers'][q]['payload']['predicate'] == lex.source.READ_MOOD)
                and not (chef_transfer and plan['qualifiers'][q]['payload']['predicate'] == lex.source.FOOD_TRANSFER)
                and not (fish_size and plan['qualifiers'][q]['payload']['predicate'] == lex.source.FISH_CREATED)], locale)
        targets = list(dict.fromkeys(r['names'][locale] for u in units for rel in u.get('recipe_targets', [])
                                    for r in rel['results'] if r['kind'] == 'declared'))
        returns = list(dict.fromkeys(r['names'][locale] for u in units for rel in u.get('recipe_targets', [])
                                    for r in rel['results'] if r['kind'] == 'callback_unconditional'))
        text = grammar.qualified(clauses, conditions)
        # Concrete activity names already identify these purposes. Individual
        # recipe variants and full support inventories are L4 detail.
        purpose_named = all(_role(u)[0] and all(c not in {
            'package_opening', 'item_packaging', 'seed_packaging',
            'ammunition_disassembly', 'bottle_breaking', 'spear_reclaim',
            'fabric_recovery', 'electronic_salvage', 'radio_salvage',
            'metal_forging',
        } for c in _role(u)[0]) for u in units)
        if targets and not purpose_named and not (len(targets) > 1 and all(_role(u)[0] == ['metal_forging'] for u in units)):
            if len(targets) == 1 and all(_role(u)[0] == ['metal_forging'] and _role(u)[1] == ['tool'] for u in units):
                text = _forging_tool(units, plan, locale) + '.'
            else:
                text += (' 제작 대상: ' + '·'.join(targets) + '.') if locale == 'ko' else (' Crafting targets include ' + en.join(targets) + '.')
        if returns:
            text += (' 함께 회수하는 물품: ' + '·'.join(returns) + '.') if locale == 'ko' else (' Also returns ' + en.join(returns) + '.')
        if family[0] == "route":
            text = ("획득 경로: " if locale == "ko" else "Acquisition route: ") + text
        expression = 'equivalent_scope' if len({tuple(u['qualifier_refs']) for u in units}) > 1 else 'exact_scope'
        segments.append({"text": text, **_links(units, plan), "expression": expression})
    return segments


def _clauses(units, plan, locale, compact=False):
    functions = {f["payload"].get("function") for u in units for f in u["facts"]}
    properties = {f["payload"].get("property") for u in units for f in u["facts"]}
    fact_refs = {r for u in units for r in u["fact_refs"]}
    result_refs = {r for relation in plan["relations"] if relation["kind"] == "result"
                   for r in relation.get("fact_refs", [])}
    facts = [f for u in units for f in u['facts']]
    moods = {'boredom': ('지루함', 'boredom'), 'stress': ('스트레스', 'stress'),
             'unhappiness': ('불행', 'unhappiness')}
    if facts and all(f['fact_kind'] == 'effect' and f['payload'].get('direction') == 'cap_at_reading_start'
                     and f['payload'].get('property') in moods for f in facts):
        names = [lex.pair(moods[f['payload']['property']], locale) for f in facts]
        return [('독서 중 ' + '·'.join(names) + ' 수치가 읽기 시작 때보다 높아지지 않게 한다')
                if locale == 'ko' else ('Reading keeps ' + en.join(names) + ' at or below the respective reading-start values')]
    if functions == {"use_furnace_bellows", None} and properties == {"forge_temperature", None} and fact_refs <= result_refs:
        return [lex.pair(("풀무로 화로의 열을 높일 수 있다", "Bellows can raise furnace heat"), locale)]
    # This coalescing is licensed by the actual function/result relations and
    # the grouping's exact common qualifier scope, not by surface strings.
    if functions == {"wash_carried_equipment", None} and fact_refs <= result_refs:
        removed = []
        if "item_surface_blood" in properties:
            removed.append("피" if locale == "ko" else "blood")
        if "clothing_surface_dirt" in properties:
            removed.append("옷의 때" if locale == "ko" else "clothing dirt")
        covered = {"item_surface_blood", "clothing_surface_dirt", "clothing_wetness", None}
        if removed and properties <= covered:
            text = ("물로 " + "와 ".join(removed) + "를 씻어낼 수 있다" if locale == "ko"
                    else "Washing with water removes " + en.join(removed))
            if "clothing_wetness" in properties:
                text += (". 세척한 옷은 완전히 젖는다" if locale == "ko" else ". Washed clothing becomes fully wet")
            return [text]
    ordered = units if compact else sorted(units, key=lambda u:
        ({"direct_function": 0, "use_context": 1, "context_role": 1, "effect": 2, "state": 3}.get(u["facts"][0]["fact_kind"], 4), u["fact_refs"]))
    return [_core(u, locale, compact) for u in ordered]


FUEL_FUNCTIONS = {"supply_campfire_fuel", "supply_hearth_fuel", "supply_furnace_fuel"}
TINDER_FUNCTIONS = {"provide_campfire_tinder", "provide_hearth_tinder", "provide_industrial_tinder"}


def _compact(plan, locale):
    prefix, used = uses.frames(plan, locale, _links, True)
    remaining = dict(plan, has_public_prefix=bool(prefix), units=[u for u in plan['units'] if not set(u['fact_refs']) & used])
    return prefix + _compact_remaining(remaining, locale)


def _compact_liquid_containers(segments, plan, locale):
    """Coordinate only capabilities shared by each admitted liquid.

    No full vanilla function signature is required. A mod container with
    water only, fuel only or a subset of operations uses the same path.
    Unknown and mixed-purpose segments retain their original wording.
    """
    capabilities = {
        'store_water': ('물', 'water', {'store'}),
        'carry_water': ('물', 'water', {'carry'}),
        'receive_poured_water': ('물', 'water', {'receive'}),
        'fill_petrol_container': ('연료', 'fuel', {'receive'}),
        'transfer_vehicle_fuel': ('연료', 'fuel', {'receive', 'supply'}),
    }
    selected, liquids = [], {}
    for segment in segments:
        refs = set(segment['fact_refs'])
        payloads = [f['payload'] for u in plan['units'] for f in u['facts'] if f['fact_ref'] in refs]
        if not payloads or segment.get('qualifier_refs') or not all(p.get('function') in capabilities for p in payloads):
            continue
        selected.append(segment)
        for payload in payloads:
            ko_name, en_name, operations = capabilities[payload['function']]
            name = ko_name if locale == 'ko' else en_name
            liquids.setdefault(name, set()).update(operations)
    if len(selected) < 2:
        return segments
    groups = {}
    for liquid, operations in liquids.items():
        groups.setdefault(tuple(o for o in ('receive', 'store', 'carry', 'supply') if o in operations), []).append(liquid)
    clauses = []
    for operations, names in groups.items():
        noun = ko.object_name('이나 '.join(names)) if locale == 'ko' else ' or '.join(names)
        ko_verbs = {'store': ('보관하거나', '보관할 수 있다'), 'carry': ('운반하거나', '운반할 수 있다'),
                    'receive': ('담거나', '담을 수 있다'), 'supply': ('공급하거나', '공급할 수 있다')}
        en_verbs = {'store': 'store', 'carry': 'carry', 'receive': 'receive', 'supply': 'supply'}
        if locale == 'ko':
            purposes = [o for o in operations if o != 'receive']
            if 'receive' in operations and purposes:
                clauses.append(noun + ' 담아 ' + ' '.join([ko_verbs[o][0] for o in purposes[:-1]] + [ko_verbs[purposes[-1]][1]]))
            else:
                clauses.append(noun + ' ' + ' '.join([ko_verbs[o][0] for o in operations[:-1]] + [ko_verbs[operations[-1]][1]]))
        else:
            clauses.append('It can ' + en.join([en_verbs[o] for o in operations]) + ' ' + noun)
    members = [u for u in plan['units'] if any(set(u['fact_refs']) & set(s['fact_refs']) for s in selected)]
    combined = {'text': '. '.join(clauses) + '.', **_links([dict(u, qualifier_refs=[]) for u in members], plan),
                'expression': 'public_use', 'qualifier_dispositions': [],
                'placement_reason': 'liquid-specific capabilities; no capability transferred between liquids'}
    return [combined if s is selected[0] else s for s in segments if s is selected[0] or s not in selected]


def _compact_supporting_details(segments, plan):
    """Place packaging and individual recipe-tool examples below an overview.

    Bundling participation is kept in Expanded for every participant;
    the generic material role does not identify which input is bundled.
    A sole use is never removed.
    """
    details = []
    for segment in segments:
        units = [u for u in plan['units'] if set(u['fact_refs']) & set(segment['fact_refs'])]
        def supporting(unit):
            contexts, roles = _role(unit)
            functions = {f['payload'].get('function') for f in unit['facts']} - {None}
            return (bool(functions) and functions <= {'pack_into_box'} or
                    set(contexts) == {'item_packaging'} or
                    set(contexts) == {'log_binding'} and set(roles) <= {'material'} or
                    bool(contexts) and set(contexts) <= planner.PRODUCT_CONTEXTS and set(roles) == {'tool'})
        if units and all(supporting(u) for u in units):
            details.append(segment)
    return [s for s in segments if s not in details] if len(details) < len(segments) else segments


def _compact_materials(segments, plan, locale):
    """Summarize treatment/repair roles without erasing crafting fields."""
    medical = {'apply_bandage', 'clean_burn', 'apply_splint', 'apply_garment_patch'}
    selected, members = [], []
    for segment in segments:
        units = [u for u in plan['units'] if set(u['fact_refs']) & set(segment['fact_refs'])]
        functions = {f['payload'].get('function') for u in units for f in u['facts']} - {None}
        if functions and functions <= medical and all(set(_role(u)[0]) <= {'bandaging_material_preparation', 'splint_crafting'} for u in units):
            selected.append(segment)
            members.extend(u for u in units if u not in members)
    functions = {f['payload'].get('function') for u in members for f in u['facts']}
    if 'apply_garment_patch' not in functions or not functions & {'apply_bandage', 'clean_burn', 'apply_splint'}:
        return segments
    # The independent medical and garment roles remain; more specific patch
    # and treatment actions are useful in Expanded. Other segment facts,
    # including material fields, taint risks and fuel uses, remain untouched.
    text = lex.pair(('응급처치와 의류 수선에 쓸 수 있다' if 'apply_splint' in functions else '상처 처치나 의류 수선에 쓸 수 있다',
                     'It can be used for first aid or clothing repairs' if 'apply_splint' in functions else 'It can be used for wound care or clothing repairs'), locale) + '.'
    # Contamination transfer is a use consequence, explained with bandaging
    # in Expanded. It does not define the combined treatment/repair purpose.
    summary = {'text': text, **_links([dict(u, qualifier_refs=[]) for u in members], plan),
               'expression': 'public_use', 'placement_reason': 'medical and garment overview; independent crafting fields retained',
               'qualifier_dispositions': []}
    output = []
    for segment in segments:
        if segment is selected[0]:
            output.append(summary)
        if segment not in selected:
            output.append(segment)
    return output


def _compact_roles(segments, plan, locale):
    """Share grammar between adjacent role clauses, retaining purpose order."""
    grammar = ko if locale == 'ko' else en
    output = []
    group = []
    role = None
    def flush():
        if len(group) < 2:
            output.extend(s for s, _ in group)
        else:
            units = [u for _, members in group for u in members]
            activities = list(dict.fromkeys(label for u in units for label in _activity_labels(u, locale, True)))
            output.append({'text': grammar.role(activities, role, compact=True) + '.',
                           **_links(units, plan), 'expression': 'capability_overview',
                           'qualifier_dispositions': []})
        group.clear()
    for segment in segments:
        members = [u for u in plan['units'] if set(u['fact_refs']) & set(segment['fact_refs'])]
        roles = [_role(u)[1] for u in members]
        eligible = (segment['expression'] == 'capability_overview' and not segment['qualifier_refs']
                    and members and all(_role(u)[0] and _role(u)[1] for u in members)
                    and all(r == roles[0] for r in roles))
        if not eligible or role != roles[0]:
            flush()
        if eligible:
            role = roles[0]
            group.append((segment, members))
        else:
            output.append(segment)
            role = None
    flush()
    return output


def _compact_purposes(segments, plan, locale):
    """Summarize related purposes; specific tasks and targets belong in Expanded.

    Match admitted functions/participant roles, never item IDs or prose length.
    Keep unrecognized purposes and their conditions in their existing segments.
    """
    def payloads(segment):
        refs = set(segment['fact_refs'])
        values = [f['payload'] for u in plan['units'] for f in u['facts'] if f['fact_ref'] in refs]
        # Match the same purpose vocabulary as the earlier role-aware frame;
        # extra recipe evidence must not make an equivalent purpose ineligible.
        return [{**p, 'activity': 'metal_forging'} if p.get('activity') in uses.FORGING_ACTIVITIES else p
                for p in values]
    def summary(selected, text, reason):
        refs = {r for s in selected for r in s['fact_refs']}
        members = [u for u in plan['units'] if refs & set(u['fact_refs'])]
        value = {'text': lex.pair(text, locale) + '.', **_links([dict(u, qualifier_refs=[]) for u in members], plan),
                 'expression': 'public_use', 'placement_reason': reason, 'qualifier_dispositions': []}
        value['use_order'] = list(dict.fromkeys(r for s in selected for r in s.get('use_order', s['fact_refs'])))
        result = []
        for segment in segments:
            if segment is selected[0]: result.append(value)
            if segment not in selected: result.append(segment)
        return result
    # A fuel vessel's source and destination menus describe fuel supply. The
    # fire-starting supply role stays explicit; it is never called an igniter.
    fuel_functions = {'fill_petrol_container', 'transfer_vehicle_fuel', 'refuel_generator',
                      'request_corpse_burning', 'light_campfire_with_petrol',
                      'ignite_hearth_with_petrol', 'ignite_industrial_fire_with_petrol'}
    selected = [s for s in segments if payloads(s) and all(p.get('function') in fuel_functions for p in payloads(s))]
    functions = {p.get('function') for s in selected for p in payloads(s)}
    if functions >= {'fill_petrol_container', 'transfer_vehicle_fuel', 'refuel_generator', 'light_campfire_with_petrol'}:
        segments = summary(selected, ('연료를 담아 차량·발전기에 공급하거나 불을 붙이는 연료로 쓸 수 있다',
                            'It can carry fuel for vehicles and generators or supply fuel for lighting fires'),
                           'fuel supply overview; source menus and individual burning targets remain in Expanded')
    for segment in list(segments):
        ps = payloads(segment)
        if {p.get('function') for p in ps} - {None} == {'melee_attack'} and {p.get('activity') for p in ps} - {None} == {'watermelon_breaking'}:
            segments = summary([segment], ('무기로 쓸 수 있다', 'It can be used as a weapon'),
                               'weapon overview; the preparation task remains in Expanded')
    # Electronic work, woodworking and mechanical attachment work form a
    # concrete workshop-tool overview when all three are actually admitted.
    electronic = {'radio_crafting', 'radio_salvage', 'electronic_assembly', 'electronic_salvage'}
    maintenance = {'manage_weapon_attachments', 'service_vehicle_parts', 'dismantle_built_object', 'convert_lamp_to_battery', 'melee_attack'}
    selected = [s for s in segments if payloads(s) and all(
        p.get('activity') in electronic | {'woodworking', 'spear_upgrade'} or p.get('function') in maintenance or
        p.get('role') in {'tool', 'attachment'} for p in payloads(s))]
    ps = [p for s in selected for p in payloads(s)]
    activities = {p.get('activity') for p in ps}
    functions = {p.get('function') for p in ps}
    if activities & electronic and 'woodworking' in activities and functions >= {'manage_weapon_attachments', 'service_vehicle_parts'}:
        text = ('전자기기 제작·분해·개조와 목공·정비 작업에 쓸 수 있다',
                'It can be used for electronics work, woodworking and mechanical maintenance')
        if 'melee_attack' in functions:
            text = (text[0] + '. 무기로도 쓸 수 있다', text[1] + '. It can also serve as a weapon')
        segments = summary(selected, text, 'workshop tool fields; exact targets and individual attachment operations remain in Expanded')
    # Remaining compound families share a purpose, not necessarily a verb.
    # These closed sets were reviewed against every compound candidate.
    families = [
        ({'metal_welding_construction', 'welded_parts', 'construction'},
         {'remove_metal_barricade', 'build_metal_barricade', 'dismantle_burnt_vehicle'}, {'material', 'tool'},
         {'metal_welding_construction', 'welded_parts'}, {'dismantle_burnt_vehicle'},
         ('금속 제작·건축과 금속 바리케이드나 불탄 차량 등의 해체에 용접 도구로 쓸 수 있다',
          'It can serve as a welding tool for metalwork and construction, or dismantling metal barricades and burnt vehicles, for example')),
        ({'shovel_smithing', 'metal_forging', 'woodworking', 'construction', 'watermelon_breaking'},
         {'remove_barricade', 'build_wooden_barricade', 'melee_attack'}, {'tool'},
         {'metal_forging', 'woodworking'}, {'build_wooden_barricade', 'melee_attack'},
         ('금속 단조, 목공과 건축에 쓸 수 있다. 무기로도 쓸 수 있다',
          'It can be used for metal forging, woodworking and construction. It can also be used as a weapon')),
        (set(), {'collect_ground_into_bag', 'dig_grave', 'fill_grave', 'dig_furrow', 'remove_farm_plant', 'clear_burnt_floor_ashes'}, set(),
         set(), {'collect_ground_into_bag', 'dig_furrow', 'clear_burnt_floor_ashes'},
         ('땅을 파고 정리하거나 흙·자갈 등을 포대에 담는 데 쓸 수 있다',
          'It can be used to dig and clear ground or collect materials such as soil and gravel into bags')),
    ]
    for allowed_activities, allowed_functions, roles, required_activities, required_functions, text in families:
        selected = [s for s in segments if payloads(s) and all(p.get('activity') in allowed_activities or
                    p.get('function') in allowed_functions or p.get('role') in roles for p in payloads(s))]
        ps = [p for s in selected for p in payloads(s)]
        if selected and required_activities <= {p.get('activity') for p in ps} and required_functions <= {p.get('function') for p in ps}:
            segments = summary(selected, text, 'shared purpose family; individual operations and targets remain in Expanded')
    cutting = {'food_portioning', 'animal_butchery', 'fish_preparation', 'frog_preparation', 'woodworking',
               'spear_crafting', 'trap_crafting', 'fishing_gear_crafting', 'explosive_assembly',
               'pumpkin_carving', 'spear_upgrade', 'shotgun_modification'}
    selected = [s for s in segments if payloads(s) and all(p.get('activity') in cutting or
                p.get('function') in {'melee_attack', 'cut_bushes_and_vines', 'dismantle_built_object'} or
                p.get('role') in {'tool', 'attachment'} for p in payloads(s))]
    ps = [p for s in selected for p in payloads(s)]
    activities = {p.get('activity') for p in ps}; functions = {p.get('function') for p in ps}
    if activities & {'food_portioning', 'animal_butchery', 'fish_preparation', 'frog_preparation'} and 'woodworking' in activities and activities & {'spear_crafting', 'trap_crafting', 'fishing_gear_crafting', 'explosive_assembly'}:
        ko_text, en_text = '음식·목재 손질과 장비 제작', 'food and wood preparation or equipment making'
        if 'shotgun_modification' in activities: ko_text += '·개조'; en_text += ' and modification'
        if 'dismantle_built_object' in functions: ko_text += ', 건축물 해체'; en_text += ', or dismantling structures'
        ko_text += '에 쓸 수 있다'; en_text = 'It can be used for ' + en_text
        if 'cut_bushes_and_vines' in functions: ko_text += '. 덤불과 덩굴을 제거할 수도 있다'; en_text += '. It can also clear bushes and vines'
        if 'melee_attack' in functions: ko_text += '. 무기로도 쓸 수 있다'; en_text += '. It can also serve as a weapon'
        segments = summary(selected, (ko_text, en_text), 'cutting and fabrication purposes; named targets and spear attachment remain in Expanded')
    return segments


def _compact_remaining(plan, locale):
    grammar = ko if locale == "ko" else en
    frames, used = families.frames(plan, locale, _links)
    plan = dict(plan, units=[dict(u, qualifier_refs=[q for q in u['qualifier_refs']
                    if lex.public_qualifier(plan['qualifiers'][q])]) for u in plan['units']])
    groups = defaultdict(list)
    decisions = {}
    role_contexts = {c for u in plan["units"] if not u["detail_reason"] and not (set(u["fact_refs"]) & used) and _role(u)[1]
                     for c in _role(u)[0]}
    covered_contexts = []
    for u in plan["units"]:
        if u["detail_reason"] or set(u["fact_refs"]) & used:
            continue
        contexts, roles = _role(u)
        fn = u["facts"][0]["payload"].get("function")
        conditions = []
        for qref in u["qualifier_refs"]:
            wording, reason = lex.compact_qualifier(plan["qualifiers"][qref], locale, u)
            inline = lex.INLINE_CONDITIONS.get((plan["qualifiers"][qref]["payload"]["predicate"], fn))
            if fn in lex.CONTROL_NOUNS and lex.CONTROL_NOUNS[fn][0] == "firearm" and wording is None:
                inline = lex.CONTROL_NOUNS[fn][1]
            decisions[(tuple(u["fact_refs"]), qref)] = {"qualifier_ref": qref,
                "applies_to_fact_refs": u["fact_refs"], "placement": "compact_summary" if wording else "expanded",
                "text": wording, "reason": reason}
            if inline:
                decisions[(tuple(u["fact_refs"]), qref)].update(
                    placement="compact_core", text=lex.pair(inline, locale),
                    reason=("capability names its applicable operation; exact slot, capacity and execution conditions remain expanded"
                            if fn in lex.CONTROL_NOUNS and lex.CONTROL_NOUNS[fn][0] == 'firearm'
                            else "condition integrated into the capability; remaining execution detail is expanded"))
                wording = None
            if wording:
                conditions.append(qref)
        if contexts and not roles and all(c in role_contexts for c in contexts):
            covered_contexts.append(u)
            continue
        if contexts and roles:
            key = ("role", tuple(roles), tuple(conditions), tuple(contexts))
        elif fn in FUEL_FUNCTIONS:
            key = ("fuel", tuple(conditions))
        elif fn in TINDER_FUNCTIONS:
            key = ("tinder", tuple(conditions))
        elif fn in lex.CONTROL_NOUNS:
            key = ("control", lex.CONTROL_NOUNS[fn][0], tuple(conditions))
        else:
            key = ("function", tuple(u["qualifier_refs"]), canonical([f['payload'] for f in u['facts']]))
        groups[key].append(u)
    for u in covered_contexts:
        target = next(members for key, members in groups.items() if key[0] == "role"
                      and any(set(_role(u)[0]) & set(_role(m)[0]) for m in members))
        target.append(u)
    if ("fuel", ()) in groups and ("tinder", ()) in groups:
        groups[("consumption",)] = groups.pop(("fuel", ())) + groups.pop(("tinder", ()))
    segments = list(frames)
    for key, units in groups.items():
        if key[0] == "role":
            activities = list(dict.fromkeys(label for u in units for label in _activity_labels(u, locale, True)))
            text = (_forging_tool(units, plan, locale) or (_core(units[0], locale, True) if all(_role(u) in ((['food_ingredient_addition'], ['base']), (['fish_preparation'], ['ingredient'])) for u in units)
                    else grammar.role(activities, list(key[1]), compact=True))) + "."
            reason = "existential activity/role overview; exact recipe targets and eligibility in expanded"
        elif key[0] == "consumption":
            text = lex.pair(("연료나 불쏘시개로 쓸 수 있다",
                             "It can be used as fuel or tinder"), locale) + "."
            reason = "distinct fuel and tinder uses; their targets remain in expanded"
        elif key[0] in {"fuel", "tinder"}:
            text = lex.pair(("연료로 소모할 수 있다", "It can be consumed as fuel")
                            if key[0] == "fuel" else
                            ("불쏘시개로 쓸 수 있다", "It can be used as tinder"), locale) + "."
            reason = "fuel/tinder role overview; distinct targets and local supply conditions in expanded"
        elif key[0] == "control":
            operations = [u['facts'][0]['payload']['function'] for u in units]
            paired = []
            combined_wording = {}
            if key[1] == 'firearm':
                for members, phrase in (
                    ({'receive_weapon_upgrade', 'detach_weapon_upgrade'}, ('드라이버로 호환 부품 교체', 'exchanging compatible parts with a screwdriver')),
                    ({'receive_firearm_magazine', 'eject_firearm_magazine'}, ('호환 탄창 삽입·배출', 'inserting and ejecting compatible magazines')),
                    ({'load_firearm_rounds', 'unload_firearm_rounds'}, ('호환 탄약 장전·제거', 'loading and unloading matching rounds')),
                ):
                    if members <= set(operations):
                        wording = lex.pair(phrase, locale)
                        paired.append(wording)
                        combined_wording.update({fn: wording for fn in members})
                        operations = [fn for fn in operations if fn not in members]
            for u in units:
                fn = u['facts'][0]['payload']['function']
                if fn in combined_wording:
                    for qref in u['qualifier_refs']:
                        decision = decisions[(tuple(u['fact_refs']), qref)]
                        if decision['placement'] == 'compact_core':
                            decision['text'] = combined_wording[fn]
            nouns = paired + [lex.pair(lex.CONTROL_NOUNS[fn][1], locale) for fn in operations]
            if locale == "ko":
                text = "·".join(nouns) + (" 기능을 지원한다." if key[1] in {"device", "firearm"} else "에 쓸 수 있다.")
            else:
                text = ("It supports " if key[1] in {"device", "firearm"} else "It can be used for ") + en.join(nouns) + "."
            reason = "parallel named operations share their subject; actual operations and conditions stay individually linked"
        else:
            text = grammar.parallel(_clauses(units, plan, locale, compact=True))
            reason = "function capability; local execution and outcomes remain in expanded"
        conditions = []
        dispositions = []
        emitted = set()
        for u in units:
            for qref in u["qualifier_refs"]:
                decision = decisions[(tuple(u["fact_refs"]), qref)]
                dispositions.append(decision)
                condition_key = lex.COMPACT_CONDITION_GROUPS.get(
                    plan["qualifiers"][qref]["payload"]["predicate"], qref)
                if decision["placement"] == "compact_summary" and condition_key not in emitted:
                    conditions.append(decision["text"])
                    emitted.add(condition_key)
        if conditions:
            text = grammar.qualified([text.removesuffix(".")], conditions)
        segments.append({"text": text, **_links(units, plan), "expression": "capability_overview",
                         "placement_reason": reason, "qualifier_dispositions": dispositions})
    # Coordinate adjacent grammatical peers only. A shared modal never moves
    # a later purpose across an intervening independent use.
    return segments


def compose_item(item):
    preserved = planner.plan(item)
    try:
        plan = uses.prepare(preserved)
        planning_error = None
    except (KeyError, ValueError, TypeError) as exc:
        plan = dict(preserved, units=[], dispositions=[])
        planning_error = 'public planning failure: ' + str(exc)
    output = {"item_id": item["item_id"], "relations": plan["relations"],
              "preserved_fact_refs": sorted({r for u in preserved['units'] for r in u['fact_refs']} |
                                            {r for q in preserved['qualifiers'].values() for r in q['fact_refs']}),
              "internal_uses": [{"fact_refs": d["fact_refs"], "reason": d["reason"]}
                                for d in plan["dispositions"] if d["disposition"] in {"internal", "self-management"}
                                and "applies_to_fact_refs" not in d],
              "public_plan": plan["dispositions"],
              "use_relations": plan['use_relations'],
              "unresolved_relations": plan["unresolved_relations"],
              "qualifiers": [plan["qualifiers"][q] for q in sorted(plan["qualifiers"])], "locales": {}}
    for locale in model.LOCALES:
        surfaces = {}
        purpose_order = []
        for surface, realize in (("compact", _compact), ("expanded", _expanded)):
            reason = None
            try:
                if planning_error:
                    raise ValueError(planning_error)
                segments = realize(plan, locale)
                segments = uses.arrange(segments, plan)
                if surface == 'compact':
                    segments = _compact_materials(segments, plan, locale)
                    segments = _compact_roles(segments, plan, locale)
                    segments = _compact_purposes(segments, plan, locale)
                    # Shorter overviews must not reorder the existing detail
                    # traversal when they combine non-adjacent operations.
                    purpose_order = list(dict.fromkeys(r for s in segments
                                                       for r in s.get('use_order', s['fact_refs'])))
                    segments = _compact_liquid_containers(segments, plan, locale)
                    segments = _compact_supporting_details(segments, plan)
                if surface == 'expanded':
                    # Follow the same authored purpose traversal as compact,
                    # while keeping each independently realized use intact.
                    order = purpose_order
                    positions = {r: n for n, r in enumerate(order)}
                    segments.sort(key=lambda s: min((positions[r] for r in s['fact_refs'] if r in positions), default=len(order)))
                    segments = uses.arrange(segments, plan)
                segments = uses.finish_units(segments, plan, locale)
                # Public prose only: U+00B7 does not render in the user's PZ font.
                # Evidence, identifiers and runtime readers remain untouched.
                for segment in segments:
                    segment['text'] = segment['text'].replace('·', ', ')
                    for detail in segment.get('qualifier_dispositions', []):
                        if detail.get('text'):
                            detail['text'] = detail['text'].replace('·', ', ')
                state = "present" if segments else "absent"
                if not segments:
                    reason = ("accepted facts retained only as acquisition, self-management or internal information"
                              if preserved["units"] else "no accepted use facts in the adopted input")
            except (KeyError, ValueError, TypeError) as exc:
                segments, state = [], "failed"
                reason = "composition rule failure: " + str(exc)
            surfaces[surface] = {"item_id": item["item_id"], "locale": locale, "surface": surface,
                                 "state": state, "reason": reason, "segments": segments,
                                 "text": "".join(("" if n == 0 else " " if surface == "compact" or s.get('continues_use') else "\n") + s["text"]
                                                 for n, s in enumerate(segments))}
            if surface == 'expanded':
                units = []
                for n, segment in enumerate(segments):
                    if segment.get('continues_use') and units:
                        units[-1]['last_segment'] = n + 1
                    else:
                        units.append({'first_segment': n + 1, 'last_segment': n + 1})
                surfaces[surface]['use_units'] = units
        compact, expanded = surfaces["compact"], surfaces["expanded"]
        compact["detail_links"] = []
        if expanded["state"] == "present":
            compact["detail_links"] = [
                {"segment": n, "fact_refs": s["fact_refs"],
                 "reason": "full local meaning, qualifier scope, outcomes and acquisition routes"}
                for n, s in enumerate(expanded["segments"])]
        elif compact["state"] == "present":
            compact.update(state="failed", text="", segments=[],
                           reason="expanded meaning unavailable; cannot preserve compact detail placement")
        output["locales"][locale] = surfaces
    return output


def compose(source, identity, producer):
    result = {"schema": model.SCHEMA, "version": model.VERSION, "input": identity,
              "producer": producer, "physical_fit": "unmeasured; B must check PZ font and viewport",
              "items": [compose_item(item) for item in source["items"]]}
    counts = Counter(f"{loc}/{surface}/{row['state']}" for item in result["items"]
                     for loc, surfaces in item["locales"].items() for surface, row in surfaces.items())
    result["summary"] = {"targets": len(result["items"]), "surfaces": sum(counts.values()),
                         "states": dict(sorted(counts.items()))}
    return model.validate_result(result)


def produce(root: Path):
    root = Path(root).resolve()
    source = inputs.read_result(root)
    identity = {"path": inputs.DEFAULT_OUTPUT,
                "sha256": hashlib.sha256((root / inputs.DEFAULT_OUTPUT).read_bytes()).hexdigest(),
                "schema": source["schema"], "source": source["source"], "summary": source["summary"]}
    # Identify the actual vocabulary and grammar consumed; no copies or seals.
    names = ["description_composition_" + suffix + ".py" for suffix in
             ("model", "planner", "lexicon", "ko", "en", "families", "uses", "results")]
    names += ["expression_rules.py", "recovery_expression.py", "recovery_sources.py", "acquisition_expression.py"]
    producer = {"version": model.VERSION, "files": {
        CODE + name: hashlib.sha256((root / CODE / name).read_bytes()).hexdigest() for name in names}}
    return source, compose(source, identity, producer)


def _path(root, path):
    root = Path(root).resolve()
    target = (root / path).resolve()
    model.require(target.is_relative_to(root / "Iris/build/description/composition"),
                  "description path escapes its output directory")
    model.require(target != root / inputs.DEFAULT_OUTPUT, "cannot overwrite semantic input")
    return target


def write_result(root, result, path=DEFAULT_OUTPUT):
    target = _path(root, path)
    model.validate_result(result)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    temporary.write_bytes(model.canonical(result))
    temporary.replace(target)
    return target


def read_result(root, path=DEFAULT_OUTPUT):
    return model.validate_result(json.loads(_path(root, path).read_text(encoding="utf-8")))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=Path.cwd())
    args = cli.parse_args()
    _, result = produce(args.root)
    print(write_result(args.root, result))
    print(json.dumps(result["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
