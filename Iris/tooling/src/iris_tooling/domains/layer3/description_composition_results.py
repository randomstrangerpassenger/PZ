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

def _core(unit, locale, compact=False):
    grammar = ko if locale == "ko" else en
    contexts, roles = _role(unit)
    if contexts == ['sheet_rope_making'] and roles == ['material']:
        return lex.pair(('아이템 자체를 시트 로프 제작 재료로 쓸 수 있다',
                         'The item itself can be used as material for making sheet rope'), locale)
    if contexts == ['food_ingredient_addition'] and roles == ['base']:
        return lex.pair(('재료를 더해 요리를 만들 수 있다', 'Ingredients can be added to prepare food'), locale)
    if contexts == ['fish_preparation'] and roles == ['ingredient']:
        return lex.pair(('생선을 손질해 살을 얻을 수 있다', 'It can be filleted'), locale)
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
                text = (targets[0] + ' 단조에 사용할 수 있다.') if locale == 'ko' else ('It can be used for forging ' + targets[0] + '.')
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


def _compact_materials(segments, plan, locale):
    """Summarize admitted multipurpose materials; expanded owns the inventory.

    Only the existing crafting, medical, garment and wood-use relationships
    license these phrases. Unsupported roles or actions retain normal wording.
    """
    members = [u for u in plan['units'] if any(set(u['fact_refs']) & set(s['fact_refs']) for s in segments)]
    material = [u for u in members if _role(u)[1] == ['material']]
    activities = {a for u in material for a in _role(u)[0]}
    if len(activities) < 3:
        return segments
    functions = {f['payload']['function'] for u in members for f in u['facts'] if 'function' in f['payload']}
    allowed = FUEL_FUNCTIONS | TINDER_FUNCTIONS | {'apply_bandage', 'clean_burn', 'apply_splint',
                                                 'apply_garment_patch', 'melee_attack'}
    if not functions <= allowed:
        return segments
    if any(roles and roles != ['material'] and not (roles == ['tool'] and contexts == ['watermelon_breaking'])
           for u in members for contexts, roles in [_role(u)]):
        return segments
    first_aid = bool(functions & {'apply_bandage', 'clean_burn'})
    garment = 'apply_garment_patch' in functions
    wood = 'woodworking' in activities
    construction = bool(activities & {'construction', 'carpentry_menu_construction'})
    if not (first_aid or garment or wood or construction):
        return segments
    labels = [lex.pair(pair, locale) for enabled, pair in (
        (first_aid, ('응급처치', 'first aid')), (garment, ('의류 수선', 'clothing repairs')),
        (wood, ('목공', 'woodworking')), (construction, ('건축', 'construction')))
        if enabled]
    # In a first-aid summary, bandage/splint preparation is already named by
    # its purpose. Other admitted manufacture uses remain a crafting summary.
    covered = {'woodworking', 'construction', 'carpentry_menu_construction'}
    if first_aid:
        covered |= {'bandaging_material_preparation', 'splint_crafting'}
    crafting = bool(activities - covered)
    if locale == 'ko':
        subject = labels[0]
        if len(labels) > 1:
            ending = labels[-2][-1]
            final = (ord(ending) - ord('가')) % 28 if '가' <= ending <= '힣' else 0
            subject = ', '.join(labels[:-1]) + ('과 ' if final else '와 ') + labels[-1]
        if first_aid or garment:
            text = subject + '에 쓸 수 있다'
            if crafting:
                text = subject + '에 쓰거나 제작 재료로 사용할 수 있다'
        else:
            text = subject + '의 재료로 사용할 수 있다'
            if crafting:
                text = subject + '이나 다른 물품을 만드는 재료로 사용할 수 있다'
        text += '.'
    else:
        text = 'It can be used as material for ' + en.join(labels + (['crafting'] if crafting else [])) + '.'
    extra = []
    if 'apply_splint' in functions and not first_aid:
        extra.append(lex.pair(('골절 고정', 'splinting fractures'), locale))
    if any(_role(u) == (['watermelon_breaking'], ['tool']) for u in members):
        extra.append(lex.pair(('수박 쪼개기', 'breaking a watermelon'), locale))
    weapon = 'melee_attack' in functions
    fuel, tinder = bool(functions & FUEL_FUNCTIONS), bool(functions & TINDER_FUNCTIONS)
    fuel_label = lex.pair(('연료나 불쏘시개' if fuel and tinder else '연료' if fuel else '불쏘시개',
                           'fuel or tinder' if fuel and tinder else 'fuel' if fuel else 'tinder'), locale)
    if locale == 'ko':
        if extra:
            text += ' ' + '이나 '.join(extra) + '에 쓸 수 있다.'
        if weapon:
            text += ' 무기로도 쓸 수 있다.'
        if fuel or tinder:
            text += ' ' + fuel_label + '로도 쓸 수 있다.'
    else:
        if extra:
            text += ' It can also be used for ' + en.join(extra) + '.'
        if weapon:
            text += ' It can also be used as a weapon.'
        if fuel or tinder:
            text += ' It can also be used as ' + fuel_label + '.'
    # This overview authors a new traversal. Carry the references in that
    # very order so expanded follows its purposes instead of the input order.
    links = _links([dict(u, qualifier_refs=[]) for u in members], plan)
    traversal = []
    def visit(tokens):
        traversal.extend(u for u in members if uses.purpose_tokens(u) & tokens and u not in traversal)
    if first_aid:
        visit({'apply_bandage', 'clean_burn', 'apply_splint', 'bandaging_material_preparation', 'splint_crafting'})
    if garment:
        visit({'apply_garment_patch'})
    if wood:
        visit({'woodworking'})
    if construction:
        visit({'construction', 'carpentry_menu_construction'})
    visit(activities - covered)
    visit({'watermelon_breaking'})
    visit({'apply_splint', 'melee_attack'})
    visit(set(FUEL_FUNCTIONS) | set(TINDER_FUNCTIONS))
    traversal.extend(u for u in members if u not in traversal)
    links['use_order'] = list(dict.fromkeys(r for u in traversal for r in u['fact_refs']))
    return [{'text': text, **links, 'expression': 'public_use',
             'placement_reason': 'existing purpose relationships summarized; independent detail retained in expanded',
             'qualifier_dispositions': []}]


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


def _compact_remaining(plan, locale):
    grammar = ko if locale == "ko" else en
    frames, used = families.frames(plan, locale, _links)
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
            text = (_core(units[0], locale, True) if all(_role(u) in ((['food_ingredient_addition'], ['base']), (['fish_preparation'], ['ingredient'])) for u in units)
                    else grammar.role(activities, list(key[1]), compact=True)) + "."
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
                if surface == 'expanded':
                    # Follow the same authored purpose traversal as compact,
                    # while keeping each independently realized use intact.
                    order = list(dict.fromkeys(r for s in surfaces['compact']['segments']
                                                for r in s.get('use_order', s['fact_refs'])))
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
