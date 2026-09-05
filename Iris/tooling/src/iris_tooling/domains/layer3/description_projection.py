"""First-contact synthesis of accepted claims, not truncation of expanded prose."""
from collections import defaultdict

from . import expression_rules as rules
from .investigation import require

# Reviewed projection of the exact accepted predicate branches. None means
# ordinary execution/detail, retained by expanded and tracked as detail in S2.
# A nonempty tag identifies a first-contact semantic distinction, not importance.
QUALIFIERS = dict.fromkeys(rules.PREDICATES)
QUALIFIERS.update({
    'A compatible empty flashlight or duck device is supplied; transferred charge is the charge remaining in the battery selected by the recipe.': 'device_scope',
    "Reading progress yields a multiplier above the current one, and the reader is within this book's supported training level range.": 'training_scope',
    'The consumed water is tainted, current poison level is below 20, and current sickness is below 0.3.': 'tainted_water',
    'Editing needs an available writing implement and must not be locked by another user.': 'writing_implement',
})


def qualifier_tag(fact):
    value = fact['payload']['predicate']
    require(value in QUALIFIERS, 'expression_gap: unreviewed compact qualifier')
    return QUALIFIERS[value]


def compose(selected, facts, locale):
    """All contributors survive either as a clause or a named detail qualifier.

    Combinations are semantic grammars: ingestion plus ingredient, water plus
    thirst/taint, reading plus learning, drying plus wetness, and equal-scope
    roles across activities. Every uncombined claim gets its own specific clause.
    """
    remaining = {r for r in selected if facts[r]['fact_kind'] not in {'condition', 'constraint'}}
    units = []

    def find(kind, key, value):
        return {r for r in remaining if facts[r]['fact_kind'] == kind and facts[r]['payload'].get(key) == value}

    def related(claims):
        refs = set(claims)
        refs.update(facts[r]['context_ref'] for r in claims if facts[r]['context_ref'])
        qualifiers = {q for r in refs for q in facts[r]['qualifier_refs']}
        return refs, qualifiers

    def emit(pair, claims, grammar, tags=()):
        require(claims, 'empty compact claim')
        refs, qualifiers = related(claims)
        meaningful = {q for q in qualifiers if qualifier_tag(facts[q])}
        require(all(qualifier_tag(facts[q]) in tags for q in meaningful), 'expression_gap: compact scope loss')
        refs.update(meaningful)
        units.append({'text': rules.phrase(pair, locale), 'claim_refs': sorted(claims),
                      'represented_fact_refs': sorted(refs),
                      'dependency_refs': [{'fact_ref': q, 'kind': facts[q]['fact_kind'],
                                           'projection': qualifier_tag(facts[q]) if q in meaningful else 'context'}
                                          for q in sorted(refs - set(claims))],
                      'rule_ref': 'compact/' + grammar + '/' + locale})
        remaining.difference_update(refs)

    eating = find('direct_function', 'function', 'eat_food')
    ingredient = {r for r in find('context_role', 'role', 'ingredient')
                  if facts[facts[r]['context_ref']]['payload']['activity'] == 'food_preparation'}
    if eating and ingredient:
        emit(('먹을 수 있으며, 음식 준비와 조리의 재료로 사용할 수 있다.',
              'It can be eaten and used as an ingredient in food preparation.'), eating | ingredient, 'ingestion_preparation')

    drinking = find('direct_function', 'function', 'drink_stored_water')
    thirst = find('effect', 'property', 'thirst')
    poison = find('effect', 'property', 'poison_level')
    if drinking and thirst:
        if poison:
            emit(('마셔 갈증을 줄일 수 있으며, 오염된 물은 중독 수치를 높일 수 있다.',
                  'Drinking it can reduce thirst; tainted water can increase poison level.'),
                 drinking | thirst | poison, 'water_effects', ('tainted_water',))
        else:
            emit(('마셔 갈증을 줄일 수 있다.', 'Drinking it can reduce thirst.'), drinking | thirst, 'water_thirst')

    reading = find('direct_function', 'function', 'read_literature')
    learning = {r for r in remaining if facts[r]['fact_kind'] == 'effect'
                and facts[r]['payload'].get('property', '').endswith('_experience_multiplier')}
    if reading and learning:
        names = [rules.SKILLS[facts[r]['payload']['property'].removesuffix('_experience_multiplier')]
                 for r in sorted(learning)]
        ko = '·'.join(n[0] for n in names)
        en = ', '.join(n[1] for n in names)
        emit((f'읽을 수 있으며, 학습 수준이 맞으면 {ko} 경험치 배율을 높일 수 있다.',
              f'It can be read to increase the {en} experience multiplier within its supported training levels.'),
             reading | learning, 'reading_learning', ('training_scope',))

    drying = find('direct_function', 'function', 'dry_the_body')
    wetness = find('effect', 'property', 'body_wetness')
    if drying and wetness:
        emit(('몸의 물기를 닦아 젖은 정도를 줄일 수 있다.', 'It can dry the body and reduce wetness.'),
             drying | wetness, 'drying_effect')

    tools = find('context_role', 'role', 'tool')
    repair_targets = find('context_role', 'role', 'repair_target')
    if tools and repair_targets:
        activities = sorted({facts[facts[r]['context_ref']]['payload']['activity'] for r in tools})
        require(all(facts[facts[r]['context_ref']]['payload']['activity'] == 'repair' for r in repair_targets), 'unreviewed repair context')
        ko = '·'.join(rules.CONTEXTS[a][0] for a in activities)
        en = ', '.join(rules.CONTEXTS[a][1] for a in activities)
        emit((f'{ko}에 도구로 쓰이며, 물품 수리의 대상이기도 하다.',
              f'It serves as a tool for {en}, and can itself be repaired.'),
             tools | repair_targets, 'tool_contexts_and_repair_target')

    # Equal-role, equal-first-contact-scope activities share a clause. Context
    # names retain each concrete activity; role facts are never globalized.
    role_groups = defaultdict(set)
    for r in sorted(remaining):
        f = facts[r]
        if f['fact_kind'] == 'context_role':
            _, qs = related({r})
            tags = tuple(sorted({qualifier_tag(facts[q]) for q in qs if qualifier_tag(facts[q])}))
            role_groups[f['payload']['role'], tags].add(r)
    for (role, tags), refs in sorted(role_groups.items()):
        activities = sorted({facts[facts[r]['context_ref']]['payload']['activity'] for r in refs})
        ko = '·'.join(rules.CONTEXTS[a][0] for a in activities)
        en = ', '.join(rules.CONTEXTS[a][1] for a in activities)
        if role == 'power_supply':
            require(activities == ['portable_device_power'] and tags == ('device_scope',), 'unreviewed device scope')
            pair = ('호환되는 빈 손전등이나 오리 모양 장치에 남은 전원을 공급할 수 있다.',
                    'It can supply its remaining charge to a compatible empty flashlight or duck device.')
        elif role == 'repair_target':
            require(activities == ['repair'], 'unreviewed repair role')
            pair = ('물품 수리의 대상이다.', 'It can be repaired.')
        else:
            noun = rules.ROLES[role]
            pair = (f'{ko}에 {noun[0]}로 쓰인다.', f'It serves as {noun[1]} in {en}.')
        emit(pair, refs, 'context_roles', tags)

    for r in sorted(remaining.copy()):
        if r not in remaining:
            continue
        f = facts[r]
        if f['fact_kind'] == 'acquisition':
            # Only reached when a real first-contact obligation contributes it.
            from . import acquisition_expression
            refs, _ = related({r})
            units.append({'text': acquisition_expression.realize(f, locale), 'claim_refs': [r],
                          'represented_fact_refs': sorted(refs),
                          'dependency_refs': [{'fact_ref': r, 'payload_path': p, 'kind': 'route_condition'}
                                              for p in acquisition_expression.dependency_paths(f)],
                          'rule_ref': 'compact/acquisition/' + locale})
            remaining.remove(r)
        elif f['fact_kind'] == 'direct_function' and f['payload']['function'] == 'record_written_notes':
            emit(('필기구로 글을 적어 기록할 수 있다.', 'It can hold notes written with a writing implement.'),
                 {r}, 'writing', ('writing_implement',))
        elif f['fact_kind'] == 'effect' and f['payload']['property'] == 'poison_level':
            emit(('오염된 물을 마시면 중독 수치가 높아질 수 있다.', 'Drinking tainted water can increase poison level.'),
                 {r}, 'tainted_water', ('tainted_water',))
        elif f['fact_kind'] == 'effect' and f['payload']['property'].endswith('_experience_multiplier'):
            skill = rules.SKILLS[f['payload']['property'].removesuffix('_experience_multiplier')]
            emit((f'학습 수준이 맞으면 독서로 {skill[0]} 경험치 배율을 높일 수 있다.',
                  f'Reading can increase the {skill[1]} experience multiplier within its supported training levels.'),
                 {r}, 'learning', ('training_scope',))
        else:
            # Known specific function/effect/activity; never a generic filler.
            ko, _ = rules.core(f, facts, 'ko')
            en, _ = rules.core(f, facts, 'en')
            emit((ko + '.', en + '.'), {r}, 'specific_claim')
    represented = {r for u in units for r in u['represented_fact_refs']}
    detail = selected - represented
    require(all(facts[r]['fact_kind'] in {'condition', 'constraint'} and qualifier_tag(facts[r]) is None
                for r in detail), 'expression_gap: compact contributor not accounted for')
    return units, sorted(detail)
