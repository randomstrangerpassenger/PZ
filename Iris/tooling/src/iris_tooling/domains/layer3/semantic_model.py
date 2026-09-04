"""L3-03 semantic identity, admission and structured consumption contract."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json

from . import investigation as inv

SCHEMA = 'iris-layer3-semantic-results-v1'
KINDS = {'use_context', 'context_role', 'direct_function', 'effect', 'state', 'condition', 'constraint'}
PAYLOAD_FIELDS = {'use_context': {'activity'}, 'context_role': {'role'},
                  'direct_function': {'function'}, 'effect': {'property', 'direction'},
                  'state': {'state', 'value'}, 'condition': {'predicate'}, 'constraint': {'predicate'}}
RELATIONS = {'retained', 'changed', 'superseded', 'newly_required', 'no_longer_required'}


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def identity(prefix: str, value) -> str:
    return prefix + ':' + hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def fact_identity(fact: dict) -> str:
    # Dependency refs are themselves semantic identities. Locator, review and
    # registry metadata never participate. Dependency order has no meaning.
    return identity('fact', {key: (sorted(fact[key]) if key == 'applies_to_fact_refs' else fact[key])
                            for key in ('item_id', 'fact_kind', 'payload', 'context_fact_ref', 'applies_to_fact_refs')
                            if key in fact})


def question_key(result: dict) -> tuple[str, str, str]:
    key = tuple(result.get(k) for k in ('item_id', 'axis_id', 'scope_ref'))
    inv.require(all(isinstance(k, str) and bool(k) for k in key), 'invalid question key')
    if 'question_key' in result:
        inv.require(result['question_key'] == list(key), 'noncanonical question key')
    return key


def validate_payload(payload: dict, contract: dict) -> None:
    """Validate every fact and open result, not just terminal references."""
    inv.require(payload.get('schema_version') == SCHEMA and payload.get('status') in {'candidate', 'adopted'},
                'invalid semantic result schema/status')
    aid = payload.get('authority_id')
    inv.require(bool(aid) and payload.get('registry_revision') == contract['revision'], 'stale definition')
    targets = payload['target_ids']
    inv.require(targets == sorted(set(targets)), 'duplicate/unsorted target')
    sources = {r['path']: r['sha256'] for r in payload['source_bindings']}
    inv.require(len(sources) == len(payload['source_bindings']) and bool(sources), 'duplicate/empty source')
    observations = payload['observations']
    provenance = payload['provenance']
    rules = payload['rules']
    for oid, observation in observations.items():
        inv.require(observation.get('source_path') in sources and observation.get('locator')
                    and observation.get('source_sha256') == sources[observation['source_path']], 'unbound observation')
        inv.require(oid == identity('obs', {k: observation[k] for k in ('source_path', 'source_sha256', 'locator', 'content')}),
                    'observation identity mismatch')
    for pid, provenance_row in provenance.items():
        inv.require(provenance_row.get('source_path') in sources
                    and provenance_row.get('source_sha256') == sources[provenance_row['source_path']]
                    and provenance_row.get('locator') and provenance_row.get('observation_refs')
                    and set(provenance_row['observation_refs']) <= observations.keys(), 'unbound provenance')
        inv.require(provenance_row.get('rule_ref') in rules and provenance_row.get('proposition'), 'missing interpretation')
    facts = {f['fact_id']: f for f in payload['facts']}
    inv.require(len(facts) == len(payload['facts']), 'duplicate fact ID')
    for fid, fact in facts.items():
        kind = fact.get('fact_kind')
        inv.require(kind in KINDS and fact.get('status') == 'accepted' and fact.get('item_id') in targets,
                    'invalid accepted fact')
        inv.require(isinstance(fact.get('payload'), dict) and set(fact['payload']) == PAYLOAD_FIELDS[kind]
                    and all(v is not None and v != '' for v in fact['payload'].values()), 'invalid kind payload')
        inv.require(fid == fact_identity(fact), 'semantic correction requires new ID and rebinding')
        refs = fact.get('provenance_refs', [])
        inv.require(bool(refs) and len(refs) == len(set(refs)) and set(refs) <= provenance.keys(), 'dangling fact provenance')
        inv.require(all(provenance[p]['item_id'] == fact['item_id']
                        and provenance[p]['semantic_identity'] == fid for p in refs), 'proposition/fact mismatch')
        admission = fact.get('admission', {})
        inv.require(admission.get('rule_ref') in rules and admission.get('supported') is True
                    and rules[admission['rule_ref']].get('review_state') == 'reviewed'
                    and all(provenance[p]['rule_ref'] == admission['rule_ref'] for p in refs), 'unsupported admission')
        if kind == 'context_role':
            context = facts.get(fact.get('context_fact_ref'), {})
            inv.require(context.get('item_id') == fact['item_id'] and context.get('fact_kind') == 'use_context',
                        'cross-item/missing context')
        else:
            inv.require('context_fact_ref' not in fact, 'unexpected context binding')
        if kind in {'condition', 'constraint'}:
            refs = fact.get('applies_to_fact_refs', [])
            inv.require(bool(refs) and len(refs) == len(set(refs))
                        and all(facts.get(r, {}).get('item_id') == fact['item_id']
                                and facts[r]['fact_kind'] not in {'condition', 'constraint'} for r in refs),
                        'invalid qualifier dependency')
        else:
            inv.require('applies_to_fact_refs' not in fact, 'unexpected qualifier binding')
    attempts = payload['attempts']
    for attempt_id, attempt in attempts.items():
        inv.require(attempt.get('item_id') in targets and attempt.get('route') in 'ABCDE'
                    and attempt.get('observation_refs') and set(attempt['observation_refs']) <= observations.keys()
                    and attempt.get('method') and attempt.get('finding') and attempt.get('dependency'),
                    'missing performed investigation evidence')
    axes = {a['axis_id']: a for a in contract['axes']}
    universe = {tuple(r['question_key']): r for r in payload['universe']}
    inv.require(len(universe) == len(payload['universe']), 'duplicate universe key')
    before, after = set(), set()
    for key, row in universe.items():
        inv.require(len(key) == 3 and key[0] in targets and key[1] in axes and key[1] != 'acquisition'
                    and row['relation'] in RELATIONS, 'invalid universe relation')
        inv.require(row['before_revision'] == contract['revision'] and row['after_revision'] == contract['revision'],
                    'unjustified definition revision')
        if row['relation'] != 'newly_required': before.add(key)
        if row['relation'] != 'no_longer_required': after.add(key)
        if row['relation'] != 'retained':
            inv.require(row.get('finding_refs') and set(row['finding_refs']) <= attempts.keys(), 'unjustified universe change')
    inv.require(len(before) == payload['baseline_key_count'], 'lost predecessor keys')
    results = {question_key(r): r for r in payload['results']}
    inv.require(len(results) == len(payload['results']) and results.keys() == after, 'result/universe mismatch')
    for key, result in results.items():
        inv.require(result.get('authority_ref') == aid and result.get('registry_revision') == contract['revision'], 'stale result metadata')
        state = result.get('state')
        inv.require(state in inv.STATES, 'unknown result state')
        refs = result.get('attempt_refs', [])
        inv.require(bool(refs) and set(refs) <= attempts.keys()
                    and all(attempts[r]['item_id'] == key[0] for r in refs), 'unbound result attempt')
        inv.require(state != 'not_investigated' or result.get('not_investigated_reason'), 'unexplained non-investigation')
        prov = result.get('provenance_refs', [])
        inv.require(bool(prov) and set(prov) <= provenance.keys()
                    and all(provenance[p]['item_id'] == key[0] for p in prov), 'unbound open/terminal evidence')
        fact_refs = result.get('fact_refs', [])
        if state in {'not_investigated', 'investigated_unresolved'}:
            inv.require(not fact_refs and result.get('blockers') and result.get('next_source_dependency'), 'invalid open result')
        else:
            inv.require(result.get('question_coverage') == 'whole_scope' and result.get('coverage_justification'), 'partial terminal')
            if state == 'resolved':
                inv.require(bool(fact_refs) and len(fact_refs) == len(set(fact_refs))
                            and all(r in facts and facts[r]['item_id'] == key[0]
                                    and facts[r]['fact_kind'] in axes[key[1]]['allowed_result_kinds'] for r in fact_refs),
                            'wrong terminal fact')
            else:
                inv.require(not fact_refs and result.get('scope_complete') is True
                            and result.get('negative_scope') == list(key)
                            and result.get('exclusion_predicate') and result.get('closed_source_refs')
                            and set(result['closed_source_refs']) <= sources.keys(), 'unclosed negative')
    seen = set()
    for relation in payload['fact_question_bindings']:
        key = tuple(relation['question_key'])
        fid = relation['fact_ref']
        inv.require((key, fid) not in seen, 'duplicate fact/question binding')
        seen.add((key, fid))
        inv.require(key in results and fid in facts and facts[fid]['item_id'] == key[0]
                    and facts[fid]['fact_kind'] in axes[key[1]]['allowed_result_kinds'], 'wrong binding subject/kind')
        inv.require(relation.get('registry_revision') == contract['revision'] and relation.get('authority_ref') == aid,
                    'stale binding')
        inv.require(relation.get('contribution') in {'partial', 'whole_scope'}, 'unknown contribution')
        if relation['contribution'] == 'whole_scope':
            inv.require(results[key]['state'] == 'resolved' and fid in results[key]['fact_refs'], 'partial fact promoted to terminal')
    for fid, fact in facts.items():
        inv.require(any(ref == fid for _, ref in seen), 'unconsumed accepted fact')
    pending = {(r['item_id'], r['profile_id']) for r in payload['pending']}
    inv.require(len(pending) == len(payload['pending']) and len(pending) == payload['baseline_pending_count'], 'lost pending membership')
    for row in payload['pending']:
        inv.require(row['disposition'] in {'applicable', 'scoped_exclusion', 'pending_with_blocker', 'not_investigated'}
                    and row['attempt_refs'] and set(row['attempt_refs']) <= attempts.keys(), 'unsupported pending disposition')


def consume(payload: dict, contract: dict, inherited: dict, binding: dict) -> list[dict]:
    validate_payload(payload, contract)
    by_item, contributions = defaultdict(list), defaultdict(list)
    for result in payload['results']: by_item[result['item_id']].append(result)
    for relation in payload['fact_question_bindings']: contributions[relation['question_key'][0]].append(relation)
    authority = {payload['authority_id']: {**payload, 'binding': binding}}
    return [inv.resolve_item(row['item_id'], contract, row['routes'], row['gap'], inherited,
                             by_item[row['item_id']], authority,
                             fact_question_bindings=contributions[row['item_id']], result_mode=payload['status'])
            for row in payload['application_inputs']]


def census(payload: dict, applications: list[dict]) -> dict:
    return {'targets': len(payload['target_ids']), 'baseline_keys': payload['baseline_key_count'],
            'current_keys': len(payload['results']),
            'states': dict(Counter(r['state'] for r in payload['results'])),
            'axes': dict(Counter(r['axis_id'] for r in payload['results'])),
            'scopes': dict(Counter(r['scope_ref'] for r in payload['results'])),
            'fact_kinds': dict(Counter(r['fact_kind'] for r in payload['facts'])),
            'blockers': dict(Counter(b for r in payload['results'] for b in r.get('blockers', []))),
            'carry_forward': dict(Counter(r['relation'] for r in payload['universe'])),
            'pending_dispositions': dict(Counter(r['disposition'] for r in payload['pending'])),
            'pending_profiles': dict(Counter(r['profile_id'] for r in payload['pending'])),
            'partial_questions': len({tuple(r['question_key']) for r in payload['fact_question_bindings'] if r['contribution'] == 'partial'}),
            'item_complete': sum(a['item_investigation_state'] == 'complete' for a in applications),
            'acquisition_states': dict(Counter(a['acquisition_state'] for a in applications))}
