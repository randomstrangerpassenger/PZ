"""Independent L3-04 candidate production, admission and immutable readpoints."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import re

from . import acquisition_sources as sources
from . import investigation as inv
from . import semantic_results as semantic
from .semantic_model import canonical, fact_identity, identity, question_key

ROOT = 'Iris/_docs/authority/dvf/layer3_acquisition_results'
HUMAN = 'docs/iris_layer3_acquisition_contract.md'
CLOSEOUT = 'docs/iris_layer3_acquisition_closeout.md'
TEST_SOURCE = 'Iris/build/description/v2/tests/test_layer3_acquisition_results.py'
TEST_ID = 'test_layer3_acquisition_results.Layer3AcquisitionResultsTest.test_acquisition_results_contract'
ENTRY = 'layer3_acquisition_results'
SCHEMA = 'iris-layer3-acquisition-results-v1'
ROUTE = 'Iris/_docs/authority/iris_current_route_index.json'
AUTH = 'Iris/_docs/authority/iris_current_authority_manifest.json'
REGISTRY = 'Iris/validation/execution/required_validations.json'
POLICY = 'Iris/_docs/round3/round3_pytest_source_classification.json'
FACTS = 'Iris/build/description/v2/data/dvf_3_3_facts.jsonl'
DECISIONS = 'Iris/build/description/v2/data/dvf_3_3_decisions.jsonl'
POINTER = 'Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua'
SATISFIED = {'found', 'not_found', 'interpretation_unresolved'}
OUTCOMES = SATISFIED | {'not_attempted', 'access_failure'}
RULES = {
    'conditional_recovery': {'review_state': 'reviewed', 'revision': '1', 'family': 'dynamic',
                             'precondition': 'Reviewed exact creation and delivery, unique nonobsolete declaration, actual caller plus validity and truth-changing branch conditions.',
                             'interpretation': 'Broad world/material recovery, replacement and incidental output with source-local eligibility preserved.',
                             'exceptions': 'Symbolic identity, engine-only dispatch, previews and commented code are not admitted by this rule.'},
    'new_game': {'review_state': 'reviewed', 'revision': '1', 'family': 'dynamic',
                 'precondition': 'Exact item with unique declaration in registered SpawnItems.OnNewGame; all branch and nested bag predicates preserved.',
                 'interpretation': 'New player inventory delivery with starter kit/difficulty and item state conditions.',
                 'exceptions': 'No default server SpawnItems option or mismatched OnGameStart dispatch inferred.'},
    'foraging': {'review_state': 'reviewed', 'revision': '1', 'family': 'foraging',
                 'precondition': 'Unique exact registered forageDefs type and nonobsolete script declaration; literal effective conditions; only reviewed item-preserving spawn callbacks.',
                 'interpretation': sources.LIMITS['foraging'], 'exceptions': 'Only reviewed literal generator templates are expanded; duplicate types, unknown callbacks and unqualified identities remain leads.'},
    'fishing': {'review_state': 'reviewed', 'revision': '1', 'family': 'fishing_trapping',
                'precondition': 'Exact item assigned once to a registered fishes/trashItems record; unique script declaration; original selection/CreateItem/AddItem consumer.',
                'interpretation': 'Conditional fishing catch with complete property/lure expressions and action/stock/random/line constraints.',
                'exceptions': 'No probability, guaranteed catch or unreviewed runtime table extension.'},
    'trapping': {'review_state': 'reviewed', 'revision': '1', 'family': 'fishing_trapping',
                 'precondition': 'Exact item assigned once to a registered Animals record; unique declaration; checkForAnimal/removeAnimal and player command path.',
                 'interpretation': 'Conditional animal recovery with trap, bait, zone, time, freshness, proximity and random selection constraints.',
                 'exceptions': 'No probability, guaranteed catch or runtime extension claim.'},
}


def product_path(root: Path) -> str:
    pointer = inv.local_path(root, POINTER).read_text(encoding='utf-8-sig')
    match = re.search(r'generation_id\s*=\s*"(dvf33-[0-9a-f]+)"', pointer)
    inv.require(match is not None, 'invalid product pointer')
    return 'Iris/media/lua/client/Iris/Data/IrisLayer3Generations/' + match[1] + '/dvf_3_3_rendered.json'


def walk(value, locator=''):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, locator + '/' + key.replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list) and value:
        for i, child in enumerate(value):
            yield from walk(child, locator + '/' + str(i))
    else:
        yield locator, value


def predecessor(root: Path) -> dict:
    """Conservative material census, independent of successor fact production.

    Every locale expression surface is retained, including empty ref arrays.
    This superset avoids treating a missing typed ref as missing public prose.
    None of these expressions can supply successor truth or negative evidence.
    """
    product = product_path(root)
    inputs = [inv.binding(root, p) for p in (FACTS, DECISIONS, POINTER, product)]
    hashes = {r['path']: r['sha256'] for r in inputs}
    records, locales = [], defaultdict(set)
    hints, slots = set(), set()
    places = {'school': ('학교', 'schools'), 'bookstore': ('서점', 'bookstores'),
              'library': ('도서관', 'libraries'), 'home_shelf': ('가정집 책장', 'home bookshelves'),
              'book_crate': ('책 상자', 'book crates'), 'post_office': ('우체국', 'post offices'),
              'postal_vehicle': ('우편 차량', 'postal vehicles')}

    def add(path, item, kind, locator, value, locale=None, support=None):
        key = {'input_path': path, 'input_sha256': hashes[path], 'item_id': item,
               'kind': kind, 'locator': locator, 'locale': locale}
        claims = []
        if isinstance(value, str):
            for place, tokens in places.items():
                for token in tokens:
                    start = value.find(token)
                    if start >= 0:
                        claims.append({'place_claim': place, 'start': start, 'end': start + len(token), 'raw': token,
                                       'disposition': 'lead-only', 'reason': 'Predecessor location expression; current namespace/engine eligibility not closed.'})
        records.append({**key, 'material_id': identity('material', key), 'value': value,
                        'support': support, 'claim_spans': claims,
                        'disposition': 'unverified' if kind == 'absence' else 'lead-only',
                        'reason': 'Predecessor absence is not successor negative evidence.' if kind == 'absence' else 'Discovery material only; successor evidence comes from raw source.'})

    for row in inv.read_rows(root / FACTS):
        item = row['item_id']
        if row.get('acquisition_hint'):
            hints.add(item)
            add(FACTS, item, 'hint', '/acquisition_hint', row['acquisition_hint'], support=row.get('fact_origin', {}).get('acquisition_hint'))
        # B is specifically the plan's Book source-slot set. Other acquisition
        # slots remain in M and its kind counts, but do not change that denominator.
        if item.startswith('Base.Book') and row.get('slot_meta', {}).get('body_material', {}).get('source_slots', {}).get('acquisition_hint'):
            slots.add(item)
        for locator, value in walk(row.get('slot_meta', {}), '/slot_meta'):
            if 'acquisition' in locator:
                add(FACTS, item, 'source_slot', locator, value, support=row.get('slot_meta', {}).get('body_material', {}).get('source_refs', []))
    for row in inv.read_rows(root / DECISIONS):
        if row.get('acquisition_null_reason'):
            add(DECISIONS, row['item_id'], 'absence', '/acquisition_null_reason', row['acquisition_null_reason'])
    entries = inv.read_json(root / product)['entries']
    locale_claims = defaultdict(dict)
    for item, row in entries.items():
        for locator, value in walk(row):
            leaf = locator.rsplit('/', 1)[-1]
            locale = leaf if re.fullmatch(r'[a-z]{2}(?:-[A-Z]{2})?', leaf) else (leaf[5:] if leaf.startswith('text_') else None)
            if locale is not None and isinstance(value, str):
                locales[locale].add(locator)
                add(product, item, 'product_expression', locator, value, locale)
                if '/menu/' in locator:
                    locale_claims[item][locale] = sorted(p for p, tokens in places.items() if any(t in value for t in tokens))
            elif 'acquisition' in locator:
                add(product, item, 'product_role', locator, value)
    mismatches = [{'item_id': item, 'claims': values, 'disposition': 'unverified',
                   'finding': 'Locale acquisition claim sets differ or an expression locale is absent.'}
                  for item, values in locale_claims.items() if any(values.values()) and
                  (set(values) != set(locales) or len({tuple(v) for v in values.values()}) != 1)]
    return {'inputs': inputs, 'selector_revision': '1',
            'selector': 'nonempty hint/origin; every acquisition slot_meta leaf and body source refs; nonempty acquisition_null_reason; every product acquisition leaf (including empty refs), and every locale expression as a conservative whole-span acquisition candidate; nested place claims retained.',
            'locale_inventory': {k: sorted(v) for k, v in sorted(locales.items())}, 'locale_mismatches': mismatches,
            'records': sorted(records, key=lambda r: r['material_id']),
            'counts': {'H': len(hints), 'B': len(slots), 'intersection': len(hints & slots),
                       'H_only': len(hints - slots), 'B_only': len(slots - hints), 'union': len(hints | slots),
                       'by_kind': dict(Counter(r['kind'] for r in records)),
                       'items_by_kind': {k: len({r['item_id'] for r in records if r['kind'] == k}) for k in sorted({r['kind'] for r in records})}}}


def add_path(payload: dict, path: dict, member_refs: dict) -> None:
    """Production and fixtures share this semantic identity/provenance operation."""
    hashes = {s['path']: s['sha256'] for s in payload['source_bindings']}
    observation = {'source_path': path['path'], 'source_sha256': hashes[path['path']],
                   'locator': f"L{path['line']}", 'content': {'raw': path['raw'], 'role': 'interpreted-acquisition', 'item_id': path['item_id']}}
    oid = identity('obs', observation)
    payload['observations'][oid] = observation
    for pair in payload.get('coverage', []):
        if pair['item_id'] == path['item_id'] and pair['family_id'] == path.get('family'):
            pair['observation_refs'] = sorted(set(pair['observation_refs']) | {oid})
            if pair['outcome'] in SATISFIED:
                pair.update(outcome='found', finding='Independently confirmed conditional path; source-family survey and remaining paths retained.')
    fact = {'item_id': path['item_id'], 'fact_kind': 'acquisition', 'status': 'accepted',
            'payload': {'route': path['route'], 'conditions': path['conditions']}}
    fid = fact_identity(fact)
    prov = {'item_id': path['item_id'], 'source_path': path['path'], 'source_sha256': hashes[path['path']],
            'locator': observation['locator'], 'rule_ref': path['rule'], 'semantic_identity': fid,
            'observation_refs': sorted({oid, *(member_refs[p] for p in path['consumer_paths'])}),
            'proposition': canonical(fact['payload']), 'limitation': path['limitations']}
    pid = identity('prov', prov)
    payload['provenance'][pid] = prov
    existing = next((f for f in payload['facts'] if f['fact_id'] == fid), None)
    if existing is None:
        existing = {**fact, 'fact_id': fid, 'provenance_refs': [], 'admission': {'rule_ref': path['rule'], 'supported': True}}
        payload['facts'].append(existing)
    existing['provenance_refs'] = sorted(set(existing['provenance_refs']) | {pid})


def assemble_results(payload: dict) -> None:
    aid, revision = payload['authority_id'], payload['registry_revision']
    by_item, pairs = defaultdict(list), defaultdict(list)
    for fact in payload['facts']:
        by_item[fact['item_id']].append(fact)
    for pair in payload['coverage']:
        pairs[pair['item_id']].append(pair)
    results, bindings = [], []
    for item in payload['target_ids']:
        facts = sorted(by_item[item], key=lambda f: f['fact_id'])
        performed = len(pairs[item]) == len(payload['families']) and all(p['outcome'] in SATISFIED for p in pairs[item])
        state = 'not_investigated' if not performed else ('resolved' if facts else 'investigated_unresolved')
        key = [item, 'acquisition', 'item']
        row = {'item_id': item, 'axis_id': 'acquisition', 'scope_ref': 'item', 'question_key': key,
               'authority_ref': aid, 'registry_revision': revision, 'state': state,
               'attempt_refs': sorted(p['attempt_ref'] for p in pairs[item]),
               'fact_refs': [f['fact_id'] for f in facts] if state == 'resolved' else [],
               'provenance_refs': sorted({p for f in facts for p in f['provenance_refs']}),
               'limitations': sorted({p['dependency'] for p in pairs[item]}),
               'blockers': [] if state == 'resolved' else ['no_admissible_path' if performed else 'required_investigation_missing'],
               'next_source_dependency': 'Resolve remaining source-local namespace/engine/callback identity boundaries; not a claim of game-wide absence.'}
        if state == 'resolved':
            row.update(question_coverage='whole_scope', coverage_justification='All required family surveys performed and an independently admitted positive path or item-global closed-negative answer exists; unrelated unknown paths do not negate a positive answer.')
        elif state == 'not_investigated':
            row['not_investigated_reason'] = 'At least one required source-family observation was not performed.'
        results.append(row)
        bindings.extend({'question_key': key, 'fact_ref': f['fact_id'], 'authority_ref': aid,
                         'registry_revision': revision, 'contribution': 'whole_scope' if state == 'resolved' else 'partial'} for f in facts)
    payload.update(results=results, fact_question_bindings=bindings)


def validate_payload(payload: dict, contract: dict, *, complete: bool = False) -> None:
    """All open/terminal rows are validated before they can reach the resolver."""
    req = inv.require
    req(payload.get('schema_version') == SCHEMA and payload.get('status') in {'candidate', 'adopted'}, 'invalid acquisition schema/status')
    req(payload.get('registry_revision') == contract['revision'] and bool(payload.get('authority_id')), 'stale acquisition definition')
    targets = payload['target_ids']
    req(targets == sorted(set(targets)) and bool(targets), 'duplicate/empty target')
    families = payload['families']
    req(set(families) == set(sources.FAMILIES), 'family denominator drift')
    hashes = {s['path']: s['sha256'] for s in payload['source_bindings']}
    req(len(hashes) == len(payload['source_bindings']) and bool(hashes), 'duplicate/empty source binding')
    req(set().union(*(set(f['members']) for f in families.values())) == set(hashes), 'unassigned source member')
    obs = payload['observations']
    for oid, o in obs.items():
        req(o.get('source_path') in hashes and o.get('source_sha256') == hashes[o['source_path']] and o.get('locator')
            and o.get('content', {}).get('raw') is not None and oid == identity('obs', o), 'unbound observation identity')
    traces = payload['traces']
    for tid, trace in traces.items():
        req(tid == identity('trace', trace) and trace.get('source_path') in hashes and trace.get('locator')
            and trace.get('assessment') in {'assessed', 'unreviewed'} and trace.get('method')
            and trace.get('finding') and trace.get('dependency'), 'invalid interpretation trace')
    for family, survey in families.items():
        req(survey.get('members') == sorted(set(survey['members'])) and bool(survey['members'])
            and set(survey['members']) <= hashes.keys(), 'invalid family members')
        refs = survey.get('observation_refs', [])
        req(len(refs) == len(set(refs)) and set(refs) <= obs.keys()
            and {obs[r]['source_path'] for r in refs} == set(survey['members']), 'incomplete source-member survey')
        req(survey.get('method') and survey.get('finding') and survey.get('consumer_trace'), 'shallow family survey')
        req(all(obs[r]['content'].get('role') == 'bounded-member-survey'
                and obs[r]['content'].get('method') and obs[r]['content'].get('line_count', 0) > 0 for r in refs), 'missing performed member observation')
        required_traces = sorted(t for t, row in traces.items() if row['source_path'] in survey['members'])
        req(survey.get('trace_refs') == required_traces, 'missing interpretation obligation')
        req(survey.get('unreviewed_trace_refs') == sorted(t for t in required_traces if traces[t]['assessment'] != 'assessed'), 'hidden unreviewed interpretation')
    expected = {(i, f) for i in targets for f in sources.FAMILIES}
    pairs = {(p['item_id'], p['family_id']): p for p in payload['coverage']}
    req(len(pairs) == len(payload['coverage']) and set(pairs) == expected, 'coverage Q mismatch')
    attempts = set()
    for (item, family), pair in pairs.items():
        req(pair.get('outcome') in OUTCOMES and pair.get('survey_ref') == family, 'unknown coverage outcome/survey')
        req(not families[family]['unreviewed_trace_refs'] or pair['outcome'] not in SATISFIED,
            'source collection cannot substitute for unperformed semantic investigation')
        req(pair.get('attempt_ref') == identity('attempt', [item, family]) and pair['attempt_ref'] not in attempts, 'invalid attempt identity')
        attempts.add(pair['attempt_ref'])
        req(pair.get('query') == {'exact': item, 'unqualified_lead': item.split('.', 1)[1]}
            and pair.get('finding') and pair.get('dependency'), 'missing exact query/finding/dependency')
        refs = pair.get('observation_refs', [])
        req(len(refs) == len(set(refs)) and set(refs) <= obs.keys(), 'dangling coverage observation')
        req(all(obs[r]['source_path'] in families[family]['members'] and obs[r]['content'].get('item_id') == item for r in refs), 'cross-item/family observation')
        req(pair['outcome'] != 'not_found' or not refs, 'miss contradicts observations')
        req(pair['outcome'] not in {'found', 'interpretation_unresolved'} or bool(refs), 'found without observation')
        if pair['outcome'] == 'access_failure':
            req(pair.get('access_failure_target') in families[family]['members'] and pair.get('access_error'), 'missing access attempt')
        if pair['outcome'] == 'not_attempted':
            req(pair.get('not_attempted_reason'), 'missing non-investigation reason')
    prov = payload['provenance']
    for pid, p in prov.items():
        req(pid == identity('prov', p) and p.get('item_id') in targets and p.get('source_path') in hashes
            and p.get('source_sha256') == hashes[p['source_path']] and p.get('locator'), 'unbound provenance')
        req(p.get('rule_ref') in payload['rules'] and p.get('observation_refs')
            and set(p['observation_refs']) <= obs.keys() and p.get('proposition') and p.get('limitation'), 'missing interpretation lineage')
        req(any(obs[r]['content'].get('role') == 'interpreted-acquisition' and obs[r]['content'].get('item_id') == p['item_id'] for r in p['observation_refs']), 'token-only admission')
    facts = {f['fact_id']: f for f in payload['facts']}
    req(len(facts) == len(payload['facts']), 'duplicate fact identity')
    for fid, fact in facts.items():
        req(fid == fact_identity(fact) and fact.get('item_id') in targets and fact.get('status') == 'accepted', 'invalid semantic fact identity')
        req(fact.get('fact_kind') in {'acquisition', 'acquisition_unobtainable'}, 'non-acquisition fact')
        value = fact.get('payload', {})
        if fact['fact_kind'] == 'acquisition':
            req(set(value) == {'route', 'conditions'} and value['route'] and value['conditions'].get('eligibility'), 'missing fact-local path conditions')
        else:
            req(value.get('scope') == 'item' and fact.get('negative_evidence_refs'), 'missing global negative scope')
            req(not any(f['item_id'] == fact['item_id'] and f['fact_kind'] == 'acquisition' for f in facts.values()), 'positive contradicts negative')
            for neg_ref in fact['negative_evidence_refs']:
                evidence = payload.get('negative_evidence', {}).get(neg_ref, {})
                req(neg_ref == identity('negative', evidence) and evidence.get('item_id') == fact['item_id'] and evidence.get('authority_ref') == payload['authority_id']
                    and evidence.get('closed_scope') is True and evidence.get('coverage_complete') is True
                    and evidence.get('false_negative_limit') == 'excluded_within_bound_scope'
                    and evidence.get('scope_description') and evidence.get('source_bindings') == payload['source_bindings'], 'unsupported closed negative')
                refs = evidence.get('closure_observation_refs', [])
                req(refs and set(refs) <= obs.keys() and all(f.get('closed_negative_capable') is True for f in families.values()), 'partial family closure')
                req({obs[r]['source_path'] for r in refs} == set(hashes), 'negative source coverage incomplete')
                req(all(obs[r]['content'].get('role') == 'closed-acquisition-enumeration'
                        and obs[r]['content'].get('scope') == 'item-global'
                        and obs[r]['content'].get('excludes_dynamic_and_engine_omissions') is True
                        and isinstance(obs[r]['content'].get('enumerated_items'), list)
                        and fact['item_id'] not in obs[r]['content']['enumerated_items'] for r in refs), 'absence search is not a complete acquisition enumeration')
        refs = fact.get('provenance_refs', [])
        req(refs and len(refs) == len(set(refs)) and set(refs) <= prov.keys(), 'dangling fact provenance')
        admission = fact.get('admission', {})
        req(admission.get('supported') is True and admission.get('rule_ref') in payload['rules']
            and payload['rules'][admission['rule_ref']].get('review_state') == 'reviewed', 'unsupported interpretation rule')
        req(all(prov[r]['item_id'] == fact['item_id'] and prov[r]['semantic_identity'] == fid
                and prov[r]['rule_ref'] == admission['rule_ref'] and prov[r]['proposition'] == canonical(value) for r in refs), 'fact/provenance disagreement')
    referenced_negative = {r for f in facts.values() for r in f.get('negative_evidence_refs', [])}
    req(referenced_negative == set(payload.get('negative_evidence', {})), 'orphan negative evidence')
    results = {question_key(r): r for r in payload['results']}
    req(len(results) == len(payload['results']) and set(results) == {(i, 'acquisition', 'item') for i in targets}, 'acquisition result universe mismatch')
    by_item = defaultdict(list)
    for f in facts.values():
        by_item[f['item_id']].append(f)
    for key, row in results.items():
        item = key[0]
        req(row.get('authority_ref') == payload['authority_id'] and row.get('registry_revision') == contract['revision'], 'unbound/stale open result')
        own = [pairs[(item, f)] for f in sources.FAMILIES]
        req(row.get('attempt_refs') == sorted(p['attempt_ref'] for p in own), 'unbound result attempts')
        performed = all(p['outcome'] in SATISFIED for p in own)
        expected_state = 'not_investigated' if not performed else ('resolved' if by_item[item] else 'investigated_unresolved')
        req(row.get('state') == expected_state, 'state/coverage/confirmed-path mismatch')
        req(row.get('limitations') and row.get('next_source_dependency'), 'lost open dependencies')
        refs = sorted(f['fact_id'] for f in by_item[item])
        req(row.get('fact_refs') == (refs if expected_state == 'resolved' else []), 'wrong terminal/partial fact refs')
        req(row.get('provenance_refs') == sorted({p for f in by_item[item] for p in f['provenance_refs']}), 'wrong result provenance')
        if expected_state == 'resolved':
            req(row.get('question_coverage') == 'whole_scope' and row.get('coverage_justification'), 'missing answer coverage')
        else:
            req(row.get('blockers'), 'missing open blocker')
        if expected_state == 'not_investigated':
            req(row.get('not_investigated_reason'), 'missing unperformed reason')
        req(not complete or expected_state != 'not_investigated', 'complete requires not_investigated=0')
    required = {(f['item_id'], fid) for fid, f in facts.items()}
    seen = set()
    for relation in payload['fact_question_bindings']:
        key = tuple(relation.get('question_key', []))
        req(key in results and relation.get('fact_ref') in facts, 'dangling fact/question relation')
        pair = (key[0], relation['fact_ref'])
        req(pair in required and pair not in seen and relation.get('authority_ref') == payload['authority_id']
            and relation.get('registry_revision') == contract['revision'], 'cross-item/duplicate/unbound contribution')
        req(relation.get('contribution') == ('whole_scope' if results[key]['state'] == 'resolved' else 'partial'), 'incorrect contribution scope')
        seen.add(pair)
    req(seen == required, 'unconsumed acquisition facts')


def prepare(root: Path) -> dict:
    contract = inv.read_json(root / inv.ROOT / 'contract.json')
    target_ids = inv.targets(root)
    inv.require(len(target_ids) == 2105, 'target count drift')
    scan = sources.survey(root, target_ids)
    print(json.dumps({'stage': 'source_survey', 'sources': len(scan['source_bindings']), 'pairs': len(scan['coverage'])}), flush=True)
    payload = {'schema_version': SCHEMA, 'status': 'candidate', 'authority_id': 'iris-layer3-acquisition-results-1',
               'registry_revision': contract['revision'], 'target_ids': target_ids, 'target_set_sha256': inv.set_digest(target_ids),
               'definition_readpoint': inv.binding(root, inv.ROOT + '/manifest.json'), 'inherits': contract['inherits'],
               'semantic_readpoint': inv.binding(root, semantic.ROOT + '/manifest.json'), 'inventory_revision': '1',
               **{k: scan[k] for k in ('source_bindings', 'families', 'observations', 'coverage', 'traces')},
               'rules': RULES, 'facts': [], 'provenance': {}, 'negative_evidence': {},
               'identity_uncertainty': {i: {'declarations': len(scan['declarations'].get(i, [])),
                                            'disposition': 'exact identity retained; no alias or loader winner inferred'}
                                        for i in ('Base.Bag_PistolCase', 'Base.Lemongrass', 'Base.NoiseMaker', 'Base.ShotgunCase1')}}
    for path in sources.positive_paths(scan, target_ids) + sources.starter_paths(scan, target_ids) + sources.recovery_paths(scan, target_ids):
        add_path(payload, path, scan['member_refs'])
    payload['facts'].sort(key=lambda f: f['fact_id'])
    assemble_results(payload)
    payload['predecessor'] = predecessor(root)
    return payload


def output_directory(root: Path, output: Path) -> Path:
    root = root.resolve()
    candidate = Path(os.path.abspath(root / output))
    inv.require(candidate.is_relative_to(root), 'output escapes repository')
    candidate = candidate.resolve()
    inv.require(candidate.is_relative_to(root) and (candidate.is_relative_to(root / '.tmp/acquisition') or candidate == root / ROOT), 'not an acquisition output directory')
    inv.require(not candidate.exists() or not any(candidate.iterdir()), 'candidate must be empty; no authority overwrite')
    return candidate


def registration_projection(path: str, value: dict) -> dict:
    """Preexisting shared entries, excluding only the planned additive registration."""
    value = json.loads(json.dumps(value))
    if path == ROUTE:
        value.pop(ENTRY, None)
    elif path == AUTH:
        value['entries'] = [r for r in value['entries'] if r.get('path') != ROOT + '/manifest.json']
    elif path == REGISTRY:
        value['required_tests'] = [r for r in value['required_tests'] if r.get('test_id') != TEST_ID]
    elif path == POLICY:
        value['reviewed_sources'] = [r for r in value['reviewed_sources'] if r.get('source_file') != TEST_SOURCE]
        value.pop('source_set_binding', None)  # The existing discovery reader checks the updated denominator.
    return value


def load_manifest(root: Path, ref: dict, *, mode: str) -> tuple[dict, dict]:
    inv.require(mode in {'candidate', 'adopted'}, 'unknown acquisition mode')
    manifest = inv.bound_json(root, ref)
    inv.require(manifest.get('schema_version') == 'iris-layer3-acquisition-manifest-v1'
                and manifest.get('status') == 'adoption_subject' and manifest.get('adoption_requires') == TEST_ID, 'invalid acquisition manifest')
    members = {r['path']: r for r in manifest['members']}
    inv.require(len(members) == len(manifest['members']) and manifest['corpus'] == members.get(manifest['corpus']['path']), 'missing/duplicate acquisition member')
    for member in members.values():
        inv.require(inv.binding(root, member['path']) == member, 'acquisition member drift')
    payload = inv.bound_json(root, manifest['corpus'])
    inv.require(payload['status'] == 'candidate' and payload['definition_readpoint'] == manifest['definition_readpoint']
                and payload['semantic_readpoint'] == manifest['semantic_readpoint'] and payload['inherits'] == manifest['inherits']
                and payload['authority_id'] == manifest['authority_id'], 'acquisition readpoint mismatch')
    definition = inv.bound_json(root, manifest['definition_readpoint'])
    for member in definition['members']:
        inv.require(inv.binding(root, member['path']) == member, 'definition member drift')
    inv.inherited_contract(root, payload['inherits'])
    for source in payload['source_bindings'] + payload['predecessor']['inputs']:
        inv.require(inv.binding(root, source['path']) == source, 'acquisition input drift')
    inv.require(payload['target_ids'] == inv.targets(root) and payload['target_set_sha256'] == definition['target_set_sha256'], 'exact target drift')
    validate_payload(payload, inv.read_json(root / inv.ROOT / 'contract.json'), complete=mode == 'adopted')
    if mode == 'adopted':
        route = inv.read_json(root / ROUTE).get(ENTRY, {})
        inv.require(route.get('state') == 'adopted' and route.get('manifest_path') == ref['path']
                    and route.get('manifest_sha256') == ref['sha256'] and route.get('validation_identity') == TEST_ID, 'unadopted acquisition subject')
        closeout = inv.local_path(root, route['adoption_result']).read_text(encoding='utf-8-sig')
        inv.require('G1_EXIT_CODE=0' in closeout and ref['sha256'] in closeout and manifest['corpus']['sha256'] in closeout, 'missing successful exact subject')
        payload = {**payload, 'status': 'adopted'}
    return manifest, payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.repository_root.resolve()
    inv.require((root / '.git').exists(), 'explicit repository root required')
    directory = output_directory(root, args.output)
    payload = prepare(root)
    directory.mkdir(parents=True, exist_ok=True)
    inv.write_json(directory / 'corpus.json', payload)
    member_paths = [str((directory / 'corpus.json').relative_to(root).as_posix()), HUMAN, TEST_SOURCE,
                    *('Iris/tooling/src/iris_tooling/domains/layer3/' + n + '.py' for n in ('acquisition_sources', 'acquisition_results', 'acquisition_consumption'))]
    baseline = inv.read_json(root / '.tmp/acquisition/baseline.json')
    manifest = {'schema_version': 'iris-layer3-acquisition-manifest-v1', 'status': 'adoption_subject',
                'authority_id': payload['authority_id'], 'corpus': inv.binding(root, member_paths[0]),
                'members': [inv.binding(root, p) for p in member_paths], 'adoption_requires': TEST_ID,
                **{k: payload[k] for k in ('definition_readpoint', 'semantic_readpoint', 'inherits')},
                'protected': baseline['protected'], 'product_migration_state': 'deferred',
                'existing_registration': {p: identity('registration', registration_projection(p, v)) for p, v in baseline['configs'].items()},
                'census': {'targets': len(payload['target_ids']), 'questions': len(payload['results']),
                           'states': dict(Counter(r['state'] for r in payload['results'])), 'positive': len(payload['facts']), 'negative': 0,
                           'coverage': {f: dict(Counter(p['outcome'] for p in payload['coverage'] if p['family_id'] == f)) for f in sources.FAMILIES}}}
    inv.write_json(directory / 'manifest.json', manifest)
    print(json.dumps({'stage': 'candidate_written', 'manifest': str(directory / 'manifest.json'), **manifest['census']}, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
