"""Bounded successor composition for source-confirmed recovery meanings.

Existing supported meanings use L3-05's pure composer. Closed new
function/state/effect/qualifier groups are composed here. No dictionaries are patched,
no adopted status is fabricated, and predecessor INPUTS never leave this module.
"""
from collections import defaultdict
from copy import deepcopy
import re

from . import acquisition_consumption as combined
from . import expression_results as expression
from . import expression_rules
from . import investigation as inv
from . import recovery
from . import recovery_sources
from . import description_projection as projection

from .recovery_phrase_views import (
    COMPACT_CONTEXTS,
    CONTEXTS,
    DETAIL_FACTS,
    EFFECT_VIEWS,
    FUNCTION_VIEWS,
    PROJECTION_NOTES,
    QUALIFIER_VIEWS,
    ROLES,
    _public_view,
    _views,
)


# These are language views of the source-bound predicates, not new facts or
# validation authority. The complete predicate and provenance stay in facts.
# Compact does not inherit the expanded sentence: only an explicitly reviewed
# first-contact distinction is projected; ordinary execution stays in detail.


# Older and more complete source predicates can describe the same player-facing
# condition. They retain distinct fact identities even when their prose agrees.


# Public projections are authored independently at each resolution. The source
# predicate remains canonical and is referenced in the existing audit member;
# an implementation branch is not a player condition or a promised outcome.


# The following controls shared the expanded-to-compact copy rule. Keep their
# confirmed purpose and meaningful prerequisites; procedural and source notes
# must not become repeated first-contact qualifications.


def projection_audit(descriptions):
    """Source remainders belong to the existing audit, not the user surface."""
    refs = defaultdict(list)
    for fact in descriptions['facts']:
        predicate = fact['payload'].get('predicate')
        if predicate in PROJECTION_NOTES:
            refs[predicate].append(fact['ref'])
    return [{'fact_refs': sorted(refs[predicate]), 'boundary': PROJECTION_NOTES[predicate],
             'expanded': list(QUALIFIER_VIEWS[predicate]['expanded']),
             'compact': list(QUALIFIER_VIEWS[predicate]['compact']) if QUALIFIER_VIEWS[predicate]['compact'] else None}
            for predicate in sorted(refs)]


def _subject_types(semantic):
    """Read existing exact declarations; repeated observations are not items.

    Physical declaration identity retains path, source hash and line span.
    Distinct declarations or conflicting Type values never select a winner.
    No additional source files are read for expression projection.
    """
    wanted = {f['item_id'] for f in semantic['facts'] if f['payload'].get('predicate') in
              {recovery_sources.CAMP_FUEL_USE, recovery_sources.CAMP_TINDER_USE, recovery_sources.HEARTH_FUEL}}
    records = defaultdict(dict)
    for observation in semantic['observations'].values():
        locator = observation.get('locator', '')
        item_id = locator.rsplit(':', 1)[-1]
        content = observation['content']
        if item_id not in wanted or not content.get('clauses'):
            continue
        header = re.match(r'\s*item\s+([\w.]+)\s*\{', content.get('raw', ''))
        if not header or header[1] not in {item_id, item_id.split('.', 1)[1]}:
            continue
        key = (observation['source_path'], observation['source_sha256'], locator.split(':', 1)[0],
               tuple(content['clauses']))
        records[item_id][key] = content
    result = {}
    for item_id, declarations in records.items():
        if len(declarations) == 1:
            fields, _ = recovery_sources.stable_properties(next(iter(declarations.values())))
            if fields.get('Type'):
                result[item_id] = fields['Type']
    return result


def _context_core(fact, facts, locale):
    context = facts[fact['context_ref']] if fact['context_ref'] else fact
    activity = context['payload']['activity']
    inv.require(activity in CONTEXTS, 'unreviewed recovery context: ' + activity)
    name = CONTEXTS[activity][0 if locale == 'ko' else 1]
    if fact['fact_kind'] == 'use_context':
        return name + '에 쓰인다.' if locale == 'ko' else 'It is used for ' + name + '.'
    role = fact['payload']['role']
    inv.require(role in ROLES, 'unreviewed recovery role: ' + role)
    return _role_text([name], role, locale)


def _role_text(names, role, locale):
    if role == 'repair_target':
        return '수리할 수 있는 물품이다.' if locale == 'ko' else 'It can be repaired.'
    noun = ROLES[role][0 if locale == 'ko' else 1]
    if locale == 'ko':
        ending = (ord(noun[-1]) - ord('가')) % 28
        return '·'.join(names) + '에서 ' + noun + ('로' if ending in {0, 8} else '으로') + ' 쓰인다.'
    joined = names[0] if len(names) == 1 else (' and '.join(names) if len(names) == 2 else ', '.join(names[:-1]) + ', and ' + names[-1])
    return 'It serves as ' + noun + ' for ' + joined + '.'


def _qualifier_view(fact, locale, resolution, subject_types):
    predicate = fact['payload']['predicate']
    item_type = subject_types.get(fact['item_id'])
    if resolution == 'expanded' and item_type:
        if predicate in {recovery_sources.CAMP_FUEL_USE, recovery_sources.CAMP_TINDER_USE}:
            ko = '즐겨찾기에서 해제해야 하며 사용하면 소모한다.'
            en = 'It must not be a favorite and is consumed when used.'
            if item_type == 'Clothing':
                ko += ' 착용 중이라면 벗어야 한다.'
                en += ' It must be unequipped if worn.'
            elif item_type == 'Container':
                ko += ' 안에 든 물품을 비워야 한다.'
                en += ' Its contents must be emptied.'
            if predicate == recovery_sources.CAMP_TINDER_USE:
                ko += ' 점화 도구가 필요하다.'
                en += ' A fire-starting item is needed.'
            return ko if locale == 'ko' else en
        if predicate == recovery_sources.HEARTH_FUEL:
            pair = (('연료로 한 번 사용하며 이동하면 작업이 중단된다.', 'One use is consumed as fuel; movement interrupts the action.')
                    if item_type == 'Drainable' else
                    ('연료로 물품 전체를 소모하며 이동하면 작업이 중단된다.', 'The whole item is consumed as fuel; movement interrupts the action.'))
            return pair[0 if locale == 'ko' else 1]
    if predicate in QUALIFIER_VIEWS:
        pair = QUALIFIER_VIEWS[predicate][resolution]
        return pair[0 if locale == 'ko' else 1] if pair else None
    if predicate in expression_rules.PREDICATES:
        if resolution == 'compact' and projection.qualifier_tag(fact) is None:
            return None
        return expression_rules.predicate(fact, locale)
    inv.require(False, 'unreviewed recovery qualifier view: ' + predicate)


def _coalesce_expanded(rows, cores, facts, locale, review_ref, subject_types):
    # These conjunctions realize all matched propositions, including effects.
    # No item name or profile winner controls them.
    combined_rows = []

    def combine(wanted, pair):
        matches = [row for row in rows if (facts[row['claim_ref']]['fact_kind'],
                   tuple(sorted(facts[row['claim_ref']]['payload'].items()))) in wanted]
        if len(matches) != len(wanted):
            return
        refs = {r for row in matches for r in row['represented_fact_refs']}
        row = {'locale': locale, 'resolution': 'expanded', 'text': pair[0 if locale == 'ko' else 1],
               'claim_ref': min(r['claim_ref'] for r in matches), 'claim_refs': sorted(r['claim_ref'] for r in matches),
               'represented_fact_refs': sorted(refs),
               'dependency_refs': sorted({expression.canonical(d): d for e in matches for d in e['dependency_refs']}.values(), key=expression.canonical),
               'rule_ref': 'recovered_expanded/2/combined/' + locale, 'review_ref': review_ref}
        combined_rows.append({'expression_id': expression.identity(row), **row})
        rows[:] = [r for r in rows if r not in matches]

    note_claims = {('direct_function', (('function', f),)) for f in ('view_written_note_pages', 'record_written_notes')}
    note_claims.update(('effect', (('direction', 'update'), ('property', p))) for p in
                       ('written_note_pages', 'written_note_title', 'written_note_lock'))
    combine(note_claims, (
        '저장된 메모는 필기구 없이 읽을 수 있다. 내용과 제목을 작성하려면 필기구가 있고 다른 사용자가 잠그지 않은 상태에서 자신의 편집 잠금도 풀어야 한다. 쪽수와 입력 길이 제한 안에서 편집하고 확인하면 저장한다. 편집 잠금은 설정·해제 즉시 적용되며 쪽 편집을 취소해도 되돌려지지 않는다.',
        'Stored notes can be read without a writing implement. Writing pages and titles requires a writing implement, no lock held by another user and an unlocked editing state. Edit within the page and entry limits and confirm to save. Setting or removing the editing lock applies immediately and survives cancellation of page edits.'))
    combine({('direct_function', (('function', 'wash_carried_equipment'),)),
             ('effect', (('direction', 'remove_by_washing'), ('property', 'item_surface_blood')))}, (
        '접근 가능한 물 공급원에서 소지한 물품을 씻어 피를 지울 수 있다. 세제는 필수가 아니다.',
        'The carried item can be washed at an accessible water source to remove blood. Soap is optional.'))
    covered = set()
    for row in rows:
        claim = facts[row['claim_ref']]
        context = claim['context_ref']
        if context:
            role_scope = {_qualifier_view(facts[q], locale, 'expanded', subject_types) for q in claim['qualifier_refs']}
            context_scope = {_qualifier_view(facts[q], locale, 'expanded', subject_types) for q in facts[context]['qualifier_refs']}
            if role_scope <= context_scope:
                covered.add(context)
    groups = defaultdict(list)
    for row in rows:
        if row['claim_ref'] not in covered:
            implied = {recovery_sources.FOOD_TRANSFER} if facts[row['claim_ref']]['payload'] == {
                'property': 'food_chef_attribution', 'direction': 'set_transferring_character'} else set()
            qualifiers = tuple(sorted({_qualifier_view(facts[q], locale, 'expanded', subject_types)
                for q in row['represented_fact_refs'] if facts[q]['fact_kind'] in {'condition', 'constraint'}
                and facts[q]['payload']['predicate'] not in implied}))
            groups[qualifiers].append(row)
    result = []
    for qualifiers, group in sorted(groups.items()):
        claims = sorted(row['claim_ref'] for row in group)
        texts = list(dict.fromkeys(cores[r] for r in claims))
        row = {'locale': locale, 'resolution': 'expanded', 'text': ' '.join([*texts, *qualifiers]),
               'claim_ref': claims[0], 'claim_refs': claims,
               'represented_fact_refs': sorted({r for e in group for r in e['represented_fact_refs']}),
               'dependency_refs': sorted({expression.canonical(d): d for e in group for d in e['dependency_refs']}.values(), key=expression.canonical),
               'rule_ref': 'recovered_expanded/2/' + locale, 'review_ref': review_ref}
        result.append({'expression_id': expression.identity(row), **row})
    return [*combined_rows, *result]


def _compact_recovery(selected, facts, cores, locale, review_ref, subject_types):
    remaining = expression._expand_qualifiers(selected, facts) & set(cores)
    details = {r: DETAIL_FACTS[(facts[r]['fact_kind'], tuple(sorted(facts[r]['payload'].items())))]
               for r in remaining if (facts[r]['fact_kind'], tuple(sorted(facts[r]['payload'].items()))) in DETAIL_FACTS}
    remaining.difference_update(details)
    rows = []

    def related(refs):
        mentioned = set(refs) | {facts[r]['context_ref'] for r in refs if facts[r]['context_ref']}
        qualifiers = {q for r in mentioned for q in facts[r]['qualifier_refs']}
        return mentioned, qualifiers

    def scopes(refs):
        return tuple(sorted({view for q in related(refs)[1]
                             if (view := _qualifier_view(facts[q], locale, 'compact', subject_types))}))

    def emit(refs, text, grammar, *, phrased=(), covered_contexts=()):
        mentioned, qualifiers = related(refs)
        meaningful = {q for q in qualifiers if _qualifier_view(facts[q], locale, 'compact', subject_types)}
        additions = sorted({_qualifier_view(facts[q], locale, 'compact', subject_types) for q in meaningful} - set(phrased))
        mentioned.update(meaningful)
        row = {'locale': locale, 'resolution': 'compact', 'text': ' '.join([text, *additions]),
               'claim_refs': sorted(refs), 'represented_fact_refs': sorted(mentioned),
               'dependency_refs': [{'fact_ref': q, 'kind': facts[q]['fact_kind'],
                                    'projection': 'first_contact_scope' if q in meaningful else 'context'}
                                   for q in sorted(mentioned - refs)],
               'rule_ref': 'recovered_compact/2/' + grammar + '/' + locale, 'review_ref': review_ref}
        rows.append({'expression_id': expression.identity(row), **row})
        removable = set(refs) | meaningful | set(covered_contexts)
        for r in mentioned - removable:
            if facts[r]['fact_kind'] != 'use_context' or scopes({r}) == scopes(refs):
                removable.add(r)
        remaining.difference_update(removable)

    def find(kind, key, value):
        return {r for r in remaining if facts[r]['fact_kind'] == kind and facts[r]['payload'].get(key) == value}

    # Reading without a pen and writing with a pen are distinct contributions.
    viewing = find('direct_function', 'function', 'view_written_note_pages')
    writing = find('direct_function', 'function', 'record_written_notes')
    pages = find('effect', 'property', 'written_note_pages')
    titles = find('effect', 'property', 'written_note_title')
    locks = find('effect', 'property', 'written_note_lock')
    if viewing and writing and pages and titles and locks:
        refs = viewing | writing | pages | titles | locks
        note_scope = _qualifier_view(next(facts[q] for q in related(refs)[1]
                                         if facts[q]['payload']['predicate'] == recovery.NOTE_EDIT), locale, 'compact', subject_types)
        emit(refs, ('저장된 메모는 필기구 없이 읽을 수 있다. 다른 사용자의 잠금이 없고 자신의 편집 잠금도 풀면 필기구로 내용과 제목을 작성·저장할 수 있다. 편집 잠금을 설정하거나 해제할 수도 있다.' if locale == 'ko' else
                    'Stored notes can be read without a writing implement. With no other user holding the lock and its editing lock unlocked, pages and titles can be written and saved with a writing implement. The editing lock can also be set or removed.'),
             'note_read_write_lock', phrased=(note_scope,))

    eating = find('direct_function', 'function', 'eat_food') | find('direct_function', 'function', 'consume_edible_food')
    ingredients = {r for r in find('context_role', 'role', 'ingredient')
                   if facts[facts[r]['context_ref']]['payload'] == {'activity': 'food_preparation'}}
    if eating and ingredients and not scopes(eating | ingredients):
        emit(eating | ingredients, ('먹거나 요리 재료로 쓸 수 있다.' if locale == 'ko' else
                                    'It can be eaten or used as a cooking ingredient.'), 'food_and_ingredient')

    bait = find('direct_function', 'function', 'supply_trap_bait')
    bait_predicates = {facts[q]['payload']['predicate'] for q in related(bait)[1]}
    if bait and bait_predicates == {recovery_sources.FOOD_TRAP_BAIT}:
        emit(bait, ('추가 재료가 없는 익히지 않은 음식은 동물에 맞는 경우 설치된 덫의 미끼로 넣을 수 있다.' if locale == 'ko' else
                    'Uncooked food without added ingredients can bait a placed trap when accepted by the target animal.'),
             'eligible_trap_bait', phrased=scopes(bait))

    washing = find('direct_function', 'function', 'wash_carried_equipment')
    blood = {r for r in find('effect', 'property', 'item_surface_blood')
             if facts[r]['payload']['direction'] == 'remove_by_washing'}
    if washing and blood and scopes(washing) == scopes(blood):
        emit(washing | blood, ('물로 씻어 묻은 피를 지울 수 있다.' if locale == 'ko' else
                               'It can be washed with water to remove blood.'), 'washing_blood')

    # One proposition per function, with every supported target retained.
    # Only qualifiers authored into the combined sentence are discharged;
    # an additional/changed condition still accompanies its contributors.
    camp = [('모닥불', 'campfires')]
    hearth = [('프로판을 쓰지 않는 바비큐', 'non-propane barbecues'), ('벽난로', 'fireplaces')]
    drum = [('통나무가 든 드럼', 'drums containing logs')]

    def target_group(definitions):
        refs, labels, predicates = set(), [], set()
        for function, targets, predicate in definitions:
            matched = find('direct_function', 'function', function)
            if matched:
                refs.update(matched)
                labels.extend(targets)
                predicates.add(predicate)
        names = list(dict.fromkeys(pair[0 if locale == 'ko' else 1] for pair in labels))
        joined = ('' if not names else '·'.join(names) if locale == 'ko' else
                  names[0] if len(names) == 1 else
                  ' and '.join(names) if len(names) == 2 else ', '.join(names[:-1]) + ', and ' + names[-1])
        phrased = {_qualifier_view(facts[q], locale, 'compact', subject_types)
                   for q in related(refs)[1] if facts[q]['payload']['predicate'] in predicates}
        return refs, joined, phrased

    fuel, targets, phrased = target_group((
        ('supply_campfire_fuel', camp, recovery_sources.CAMP_FUEL_USE),
        ('supply_hearth_fuel', hearth, recovery_sources.HEARTH_FUEL),
        ('supply_furnace_fuel', [('연료가 부족한 화로', 'furnaces with fuel capacity remaining')], recovery_sources.FURNACE_FUEL),
    ))
    if fuel:
        emit(fuel, (targets + '의 연료로 소모할 수 있다.' if locale == 'ko' else
                    'It can be consumed as fuel for ' + targets + '.'), 'fuel_targets', phrased=phrased)

    tinder, targets, phrased = target_group((
        ('provide_campfire_tinder', camp, recovery_sources.CAMP_TINDER_USE),
        ('provide_hearth_tinder', hearth, recovery_sources.HEARTH_TINDER),
        ('provide_industrial_tinder', drum, recovery_sources.INDUSTRIAL_TINDER),
    ))
    if tinder:
        emit(tinder, ('점화 도구와 함께 불이 꺼진 ' + targets + '의 불쏘시개로 소모할 수 있다.' if locale == 'ko' else
                      'With a fire-starting item, it can be consumed as tinder for unlit ' + targets + '.'),
             'tinder_targets', phrased=phrased)

    friction, targets, phrased = target_group((
        ('light_campfire_by_friction', camp, recovery_sources.CAMP_FRICTION),
        ('kindle_heat_sources', [*hearth, *drum], recovery_sources.HEAT_FRICTION),
    ))
    if friction:
        emit(friction, ('연료가 있고 불이 꺼진 ' + targets + '의 마찰 점화에 쓸 수 있다. 구멍 낸 판자와 막대 또는 나뭇가지, 지구력이 필요하며 점화는 확률적이고 막대가 부서질 수 있다.' if locale == 'ko' else
                        'It can be used for friction lighting of fueled, unlit ' + targets + '. Notched wood, a stick or branch, and endurance are needed; ignition is random and the stick may break.'),
             'friction_targets', phrased=phrased)

    throwing = find('direct_function', 'function', 'request_physics_attack')
    if throwing:
        phrased = {_qualifier_view(facts[q], locale, 'compact', subject_types)
                   for q in related(throwing)[1] if facts[q]['payload']['predicate'] == recovery_sources.PHYSICS_ATTACK}
        emit(throwing, ('차량 밖에서 투척 공격에 사용할 수 있다.' if locale == 'ko' else
                        'It can be used for throwing attacks outside a vehicle.'), 'throwing_use', phrased=phrased)

    # These direct functions already say both the activity and this item's
    # role. Preserve all contributors while stating the proposition once.
    for activity, role, name in (
            ('battery_insertion', 'power_receiver', 'accept_battery_charge'),
            ('battery_removal', 'power_receiver', 'remove_device_battery'),
            ('electronic_salvage', 'transformation_target', 'dismantle_electronics')):
        direct = find('direct_function', 'function', name)
        roles = {r for r in find('context_role', 'role', role)
                 if facts[facts[r]['context_ref']]['payload'] == {'activity': activity}}
        for d in sorted(direct):
            same = {r for r in roles if scopes({r}) == scopes({d})}
            if activity == 'electronic_salvage':
                # SCRAP_RECOVERY states a result boundary, not an extra entry
                # prerequisite. It can accompany the shared operation once.
                result_view = QUALIFIER_VIEWS[recovery_sources.SCRAP_RECOVERY]['compact'][0 if locale == 'ko' else 1]
                same |= {r for r in roles if set(scopes({r})) <= set(scopes({d}))
                         and set(scopes({d})) - set(scopes({r})) == {result_view}}
            if same:
                emit({d} | same, cores[d], 'function_with_equivalent_context_role',
                     covered_contexts={facts[r]['context_ref'] for r in same})

    # Role clauses name their own context once. Equal projected conditions can
    # share a role sentence; a more restricted role cannot hide a broader use.
    groups = defaultdict(set)
    for r in sorted(remaining):
        f = facts[r]
        if f['fact_kind'] == 'context_role':
            groups[f['payload']['role'], scopes({r})].add(r)
    for (role, _), refs in sorted(groups.items()):
        activities = sorted({facts[facts[r]['context_ref']]['payload']['activity'] for r in refs})
        labels = list(dict.fromkeys(COMPACT_CONTEXTS[a][0 if locale == 'ko' else 1] for a in activities))
        text = _role_text(labels, role, locale)
        emit(refs, text, 'context_roles')
    specific_groups = defaultdict(set)
    for r in sorted(remaining):
        specific_groups[scopes({r})].add(r)
    for _, refs in sorted(specific_groups.items()):
        refs &= remaining
        if refs:
            emit(refs, ' '.join(dict.fromkeys(cores[r] for r in sorted(refs))), 'equal_scope_claims')
    represented = {r for row in rows for r in row['represented_fact_refs']}
    detail = selected - represented
    inv.require(all(r in details or facts[r]['fact_kind'] in {'condition', 'constraint'}
                    and _qualifier_view(facts[r], locale, 'compact', subject_types) is None for r in detail),
                'recovery compact contributor loss')
    return rows, sorted(detail - details.keys()), [{'fact_ref': r, 'reason': details[r]} for r in sorted(details)]


def normalize(semantic, acquisition, applications, contract):
    inv.require(semantic['status'] == acquisition['status'] == 'candidate', 'mixed candidate/adopted')
    inv.require(semantic['target_ids'] == acquisition['target_ids'], 'candidate target mismatch')
    facts, provenance = {}, {}
    for payload in (semantic, acquisition):
        aid = payload['authority_id']
        for fact in payload['facts']:
            ref = expression.qualify(aid, fact['fact_id'])
            inv.require(ref not in facts, 'duplicate qualified fact')
            facts[ref] = {'ref': ref, 'authority_ref': aid, 'fact_id': fact['fact_id'],
                          'item_id': fact['item_id'], 'fact_kind': fact['fact_kind'],
                          'payload': deepcopy(fact['payload']),
                          'provenance_refs': sorted(expression.qualify(aid, p) for p in fact['provenance_refs']),
                          'context_ref': expression.qualify(aid, fact['context_fact_ref']) if 'context_fact_ref' in fact else None,
                          'applies_to_refs': sorted(expression.qualify(aid, p) for p in fact.get('applies_to_fact_refs', [])),
                          'qualifier_refs': []}
            for p in fact['provenance_refs']:
                inv.require(p in payload['provenance'], 'missing provenance')
                provenance[expression.qualify(aid, p)] = deepcopy(payload['provenance'][p])
    for fact in facts.values():
        refs = fact['applies_to_refs'] + ([fact['context_ref']] if fact['context_ref'] else [])
        for ref in refs:
            inv.require(ref in facts and facts[ref]['item_id'] == fact['item_id']
                        and facts[ref]['authority_ref'] == fact['authority_ref'], 'broken correction reference')
        for ref in fact['applies_to_refs']:
            inv.require(facts[ref]['fact_kind'] not in {'condition', 'constraint'}, 'qualifier cycle')
            facts[ref]['qualifier_refs'].append(fact['ref'])
    for fact in facts.values():
        fact['qualifier_refs'].sort()
    return {'targets': semantic['target_ids'], 'facts': dict(sorted(facts.items())), 'subject_types': _subject_types(semantic),
            'provenance': dict(sorted(provenance.items())),
            'profiles': {p['profile_id']: p for p in contract['profiles']},
            'applications': inv.exact_rows(applications)}


def produce(inputs, bindings):
    facts = inputs['facts']
    subject_types = inputs['subject_types']
    island = {r for r, f in facts.items() if f['payload'] in
              ({'function': 'view_written_note_pages'}, {'predicate': recovery.NOTE_EDIT})
              or f['payload'].get('function') in recovery_sources.FUNCTIONS
              or (f['payload'].get('property'), f['payload'].get('direction')) in recovery_sources.EFFECTS
              or f['payload'].get('state') in {'worn_location', 'reading_page_count', 'skill_book_max_multiplier', 'skill_book_progress_step'}
              or f['payload'].get('predicate') in QUALIFIER_VIEWS}
    edges = defaultdict(set)
    for ref, fact in facts.items():
        for other in fact['applies_to_refs'] + ([fact['context_ref']] if fact['context_ref'] else []):
            edges[ref].add(other)
            edges[other].add(ref)
    pending = list(island)
    while pending:
        additions = edges[pending.pop()] - island
        pending.extend(additions)
        island.update(additions)
    inv.require(all(set(facts[r]['qualifier_refs']) <= island for r in island), 'note island has external qualifier')
    inv.require(all(not facts[r]['context_ref'] or facts[r]['context_ref'] in island for r in island), 'note island has external context')
    regular = deepcopy(inputs)
    regular['facts'] = {r: f for r, f in regular['facts'].items() if r not in island}
    regular['provenance'] = {r: p for r, p in regular['provenance'].items()
                             if any(r in f['provenance_refs'] for f in regular['facts'].values())}
    for app in regular['applications'].values():
        app['fact_question_bindings'] = [b for b in app['fact_question_bindings']
            if expression.qualify(b['authority_ref'], b['fact_ref']) not in island]
        # The pure composer reads resolved result contributors separately.
        for axis in app['required_axes']:
            result = axis.get('result')
            if result:
                result['fact_refs'] = [f for f in result.get('fact_refs', [])
                    if expression.qualify(result['authority_ref'], f) not in island]
    review = {'payload_domain_sha256': expression.selector_domain(regular),
              'locales': {loc: {'state': 'approved'} for loc in ('ko', 'en')},
              'review_boundary': 'Existing supported L3-05 rules; recovery groups use explicit source-reviewed bilingual rules.'}
    body = expression.produce(regular, review)
    # Pure composition's fixed envelope is an internal intermediate only.
    body['inputs'] = deepcopy(bindings)
    body['schema'] = 'iris-layer3-recovery-expression-v1'
    body['facts'] = [facts[r] for r in sorted(facts)]
    body['provenance'] = inputs['provenance']
    body['denominators']['facts'] = len(facts)
    body['denominators']['fact_locale_pairs'] = 2 * len(facts)
    body['completion'] = 'partial'
    regular_expressions = {e['expression_id']: e for e in body['expressions']}
    replaced_compact_ids = set()
    body['review_ref'] = expression.identity({'inputs': bindings, 'rule': 'recovered_meanings/1',
        'functions': recovery_sources.FUNCTIONS, 'function_views': FUNCTION_VIEWS,
        'qualifiers': QUALIFIER_VIEWS, 'projection_notes': PROJECTION_NOTES, 'contexts': CONTEXTS, 'roles': ROLES,
        'compact_contexts': COMPACT_CONTEXTS, 'detail_facts': sorted((list(k), v) for k, v in DETAIL_FACTS.items()),
        'effects': sorted((list(k), v) for k, v in {**recovery_sources.EFFECTS, **EFFECT_VIEWS}.items()),
        'body_locations': recovery_sources.BODY_LABELS})
    by_item = defaultdict(set)
    for ref in island:
        by_item[facts[ref]['item_id']].add(ref)
    for item in body['items']:
        item_id = item['item_id']
        app = inputs['applications'][item_id]
        profiles = expression._profiles(app, inputs)
        selected, obligations = expression._selection(app, facts)
        item['profiles'], item['first_contact_obligations'] = profiles, obligations
        for locale in ('ko', 'en'):
            rendered = item['locales'][locale]
            note_expressions = []
            cores = {}
            for ref in sorted(by_item[item_id]):
                fact = facts[ref]
                if fact['fact_kind'] in {'condition', 'constraint'}:
                    continue
                function = fact['payload'].get('function')
                contexts = [fact['context_ref']] if fact['context_ref'] else []
                qualifier_refs = sorted(set(fact['qualifier_refs']) |
                                        {q for c in contexts for q in facts[c]['qualifier_refs']})
                represented = sorted({ref, *contexts, *qualifier_refs})
                if function == 'view_written_note_pages':
                    text = ('저장된 메모 페이지를 열어 볼 수 있다. 필기구가 없어도 열람할 수 있다.' if locale == 'ko'
                            else 'Stored note pages can be viewed without a writing implement.')
                elif function == 'record_written_notes':
                    inv.require(function == 'record_written_notes', 'unsupported note function')
                    inv.require(any(facts[q]['payload'] == {'predicate': recovery.NOTE_EDIT}
                                    for q in fact['qualifier_refs']),
                                'missing note editing qualifier')
                    text = ('글을 적어 기록할 수 있다.' if locale == 'ko' else 'Written notes can be recorded.')
                else:
                    if fact['fact_kind'] == 'state':
                        state, value = fact['payload']['state'], fact['payload']['value']
                        if state == 'worn_location':
                            location = recovery_sources.BODY_LABELS[value][0 if locale == 'ko' else 1]
                            text = ('착용 위치는 ' + location + ' 자리다.' if locale == 'ko' else
                                    'It uses the ' + location + ' equipment slot.')
                        else:
                            inv.require(type(value) is int and value > 0, 'invalid reading parameter')
                            texts = {
                                'reading_page_count': (f'전체 쪽수는 {value}쪽이다.', f'The book has {value} pages.'),
                                'skill_book_max_multiplier': (f'이 책의 경험치 획득 배율은 최대 {value}배다.', f'This book provides an XP gain multiplier of up to {value}.'),
                                'skill_book_progress_step': (f'독서 진행 {value}% 단위로 경험치 배율을 계산한다.', f'The XP multiplier is calculated in {value}% reading-progress steps.'),
                            }
                            inv.require(state in texts, 'unsupported recovered state')
                            text = texts[state][0 if locale == 'ko' else 1]
                    elif fact['fact_kind'] == 'effect':
                        effect = (fact['payload']['property'], fact['payload']['direction'])
                        inv.require(effect in recovery_sources.EFFECTS, 'unsupported recovered effect')
                        pair = EFFECT_VIEWS.get(effect, recovery_sources.EFFECTS[effect])
                        inv.require(len(pair) == 2, 'recovery effect must have exactly two locales')
                        text = pair[0 if locale == 'ko' else 1]
                    else:
                        if function in recovery_sources.FUNCTIONS:
                            pair = FUNCTION_VIEWS.get(function, recovery_sources.FUNCTIONS[function][1:])
                            text = pair[0 if locale == 'ko' else 1]
                        elif fact['fact_kind'] in {'use_context', 'context_role'}:
                            text = _context_core(fact, facts, locale)
                        else:
                            text, core_contexts = expression_rules.core(fact, facts, locale)
                            inv.require(core_contexts == contexts, 'inconsistent role context')
                cores[ref] = text.rstrip('.') + '.'
                qualifier_texts = []
                for qualifier in qualifier_refs:
                    predicate = facts[qualifier]['payload']['predicate']
                    if function == 'record_written_notes' and predicate == recovery.NOTE_EDIT:
                        continue
                    view = _qualifier_view(facts[qualifier], locale, 'expanded', subject_types)
                    if view and view not in qualifier_texts:
                        qualifier_texts.append(view)
                text = ' '.join([cores[ref], *qualifier_texts])
                deps = [{'fact_ref': q, 'kind': facts[q]['fact_kind']} for q in [*contexts, *qualifier_refs]]
                row = {'locale': locale, 'resolution': 'expanded', 'text': text, 'claim_ref': ref,
                       'represented_fact_refs': represented, 'dependency_refs': deps,
                       'rule_ref': 'recovered_meanings/1/' + locale, 'review_ref': body['review_ref'] + '/' + locale}
                expanded = {'expression_id': expression.identity(row), **row}
                note_expressions.append(expanded)
            note_expressions = _coalesce_expanded(note_expressions, cores, facts, locale, body['review_ref'] + '/' + locale, subject_types)
            for expanded in note_expressions:
                for represented_ref in expanded['represented_fact_refs']:
                    rendered['fact_expressions'].setdefault(represented_ref, []).append(expanded['expression_id'])
            rendered['expanded'].extend(expression._blocks(note_expressions, profiles, facts))
            actual_refs = {r for e in note_expressions for r in e['represented_fact_refs']}
            inv.require(actual_refs == by_item[item_id], 'unsupported recovered expression group')
            rendered['expanded_represented_fact_refs'] = sorted(set(rendered['expanded_represented_fact_refs']) | actual_refs)
            s2 = rendered['s2']
            compact_expressions = []
            if by_item[item_id]:
                # Mixed old/new contributors share one first-contact grammar.
                # Supported cores still come from the historical pure rules;
                # unchanged acquisition units retain their existing realization.
                semantic_selected = {r for r in selected if facts[r]['fact_kind'] != 'acquisition'}
                for ref in expression._expand_qualifiers(semantic_selected, facts) - cores.keys():
                    f = facts[ref]
                    if f['fact_kind'] in {'condition', 'constraint'}:
                        continue
                    if f['fact_kind'] in {'context_role', 'use_context'}:
                        cores[ref] = _context_core(f, facts, locale)
                    else:
                        cores[ref] = expression_rules.core(f, facts, locale)[0].rstrip('.') + '.'
                compact_expressions, detail_qualifiers, detail_facts = _compact_recovery(
                    semantic_selected, facts, cores, locale, body['review_ref'] + '/' + locale, subject_types)
                retained = []
                for ref in s2['expression_refs']:
                    row = regular_expressions[ref]
                    if all(facts[r]['fact_kind'] == 'acquisition' for r in row['claim_refs']):
                        retained.append(row)
                    else:
                        replaced_compact_ids.add(ref)
                all_compact = [*retained, *compact_expressions]
                s2.update(text=' '.join(e['text'] for e in all_compact), logical_rows=int(bool(all_compact)),
                    expression_refs=[e['expression_id'] for e in all_compact],
                    represented_fact_refs=sorted({r for e in all_compact for r in e['represented_fact_refs']}),
                    dependency_refs=sorted({expression.canonical(d): d for e in all_compact for d in e['dependency_refs']}.values(), key=expression.canonical),
                    detail_qualifier_refs=detail_qualifiers, detail_fact_omissions=detail_facts,
                    state='expressed' if all_compact else ('upstream_gap' if any(o['state'] == 'upstream_gap' for o in obligations) else 'no_first_contact'))
            rendered['tooltip_detail_omission_refs'] = sorted(set(rendered['expanded_represented_fact_refs']) - set(s2['represented_fact_refs']))
            body['expressions'].extend([*note_expressions, *compact_expressions])
    body['expressions'] = [e for e in body['expressions'] if e['expression_id'] not in replaced_compact_ids]
    body['expressions'].sort(key=lambda e: e['expression_id'])
    return body


def prepare(base, semantic, bindings):
    acquisition = deepcopy(base['acquisition'])
    applications = combined.consume_payloads(semantic, acquisition, base['contract'], base['inherited'],
                                             bindings['semantic'], bindings['acquisition'])
    inputs = normalize(semantic, acquisition, applications, base['contract'])
    return produce(inputs, bindings), applications
