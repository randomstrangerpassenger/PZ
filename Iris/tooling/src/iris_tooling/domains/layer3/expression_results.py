"""Independent off-live Layer 3 description producer, consumer and adoption.

Run as an installed module. The only writable authority is ROOT; prior loaders
are read-only dependencies. No current product, source reader or composer runs.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

from . import acquisition_consumption as combined
from . import acquisition_expression as routes
from . import expression_rules as rules
from . import description_projection as projection
from . import investigation as inv

ROOT = 'Iris/_docs/authority/dvf/layer3_expression'
CODE = 'Iris/tooling/src/iris_tooling/domains/layer3/'
MODULES = ('expression_rules', 'acquisition_expression', 'description_projection', 'expression_results')
CONTRACT = 'docs/iris_layer3_expression_contract.md'
TEST_SOURCE = 'Iris/build/description/v2/tests/test_layer3_expression_results.py'
GATE = 'test_layer3_expression_results.test_expression_contract'
SCHEMA = 'iris-layer3-expression-v1'
INPUTS = {
    'successor': {'path': 'Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json', 'sha256': '6735c3eadafaf4c4fd51ae56c8d0748d32903ee996d53ed43bca38822cf0932a'},
    'investigation': {'path': 'Iris/_docs/authority/dvf/layer3_investigation/manifest.json', 'sha256': '47be8947a0b18745560b1e7e2463adbe86ab878e5e9fefd461f2a838c164290e'},
    'semantic': {'path': 'Iris/_docs/authority/dvf/layer3_semantic_results/manifest.json', 'sha256': 'a3416672aa47fe4c6c84d9b8e9912377adda6e20e9eb679bf2d229cb9d3456bd'},
    'acquisition': {'path': 'Iris/_docs/authority/dvf/layer3_acquisition_results/manifest.json', 'sha256': '0281e7db661d2c37984568b715e53c97a3e78234b95b9fdfbb59ea1e31fa2a29'},
}
DENOMINATORS = {'targets': 2105, 'facts': 5290, 'fact_locale_pairs': 10580, 'acquisition_facts': 1057}


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write(path, value):
    path.write_bytes(canonical(value))


def qualify(authority, fact_id):
    # Both components are retained in each fact record; the delimiter is not
    # used for parsing. A bare ID is never a lookup key in the successor.
    return authority + '/' + fact_id


def installed_identity(root):
    expected = (root / 'Iris/tooling/.venv/Lib/site-packages').resolve()
    found = {}
    for module in (rules, routes, projection, sys.modules[__name__]):
        path = Path(module.__file__).resolve()
        inv.require(path.is_relative_to(expected), 'installed package required; source-root bootstrap forbidden')
        name = path.stem
        source = inv.local_path(root, CODE + name + '.py')
        inv.require(inv.sha(path) == inv.sha(source), 'stale installed module: ' + name)
        found[name] = {'path': path.relative_to(root).as_posix(), 'sha256': inv.sha(path)}
    inv.require(not any(Path(p).resolve() == (root / 'Iris/tooling/src').resolve() for p in sys.path if p), 'source-root override')
    return found


def read_inputs(root):
    manifests = {name: inv.bound_json(root, ref) for name, ref in INPUTS.items()}
    for manifest in manifests.values():
        for member in manifest['members']:
            inv.require(inv.binding(root, member['path']) == member, 'adopted member drift')
    data = combined.load(root, INPUTS['acquisition'], mode='adopted')
    inv.require(data['readpoints'] == {k: INPUTS[k] for k in ('semantic', 'acquisition')}, 'mixed input authorities')
    return normalize(data, inv.read_json(root / inv.ROOT / 'contract.json'))


def normalize(data, contract):
    """Detach the adopted resolver result; preserve qualified relationship edges.

    This pure helper permits synthetic fixtures, but never grants adoption.
    The public producer and loader can only obtain their inputs via read_inputs.
    """
    inv.require(data['mode'] == 'adopted', 'candidate input is not an adopted fact authority')
    facts, provenance = {}, {}
    targets = data['semantic']['target_ids']
    inv.require(targets == data['acquisition']['target_ids'] and len(targets) == len(set(targets)), 'target identity mismatch')
    for name in ('semantic', 'acquisition'):
        payload = data[name]
        inv.require(payload['status'] == 'adopted', 'mixed input lifecycle')
        authority = payload['authority_id']
        for fact in payload['facts']:
            ref = qualify(authority, fact['fact_id'])
            inv.require(ref not in facts and fact['status'] == 'accepted' and fact['item_id'] in targets, 'unknown/duplicate fact')
            row = {'ref': ref, 'authority_ref': authority, 'fact_id': fact['fact_id'],
                   'item_id': fact['item_id'], 'fact_kind': fact['fact_kind'], 'payload': deepcopy(fact['payload']),
                   'provenance_refs': [qualify(authority, p) for p in sorted(fact['provenance_refs'])],
                   'context_ref': qualify(authority, fact['context_fact_ref']) if 'context_fact_ref' in fact else None,
                   'applies_to_refs': sorted(qualify(authority, p) for p in fact.get('applies_to_fact_refs', [])),
                   'qualifier_refs': []}
            facts[ref] = row
            for p in fact['provenance_refs']:
                inv.require(p in payload['provenance'], 'unknown provenance')
                provenance[qualify(authority, p)] = deepcopy(payload['provenance'][p])
    for ref, row in facts.items():
        for dep in [*row['applies_to_refs'], *([row['context_ref']] if row['context_ref'] else [])]:
            inv.require(dep in facts and facts[dep]['item_id'] == row['item_id'] and facts[dep]['authority_ref'] == row['authority_ref'], 'unknown/cross-item dependency')
        if row['fact_kind'] == 'context_role':
            inv.require(row['context_ref'] and facts[row['context_ref']]['fact_kind'] == 'use_context', 'non-local role')
        if row['fact_kind'] in {'condition', 'constraint'}:
            inv.require(row['applies_to_refs'], 'orphan qualifier')
            for target in row['applies_to_refs']:
                inv.require(facts[target]['fact_kind'] not in {'condition', 'constraint'}, 'qualifier cycle')
                facts[target]['qualifier_refs'].append(ref)
    for row in facts.values():
        row['qualifier_refs'].sort()
    profiles = {p['profile_id']: p for p in contract['profiles']}
    inv.require(len(profiles) == len(contract['profiles']), 'duplicate profile')
    applications = inv.exact_rows(deepcopy(data['applications']))
    inv.require(set(applications) == set(targets), 'missing/unknown application')
    for item_id, application in applications.items():
        seen = set()
        for b in application['fact_question_bindings']:
            ref = qualify(b['authority_ref'], b['fact_ref'])
            key = canonical(b)
            inv.require(key not in seen and ref in facts and facts[ref]['item_id'] == item_id
                        and b['question_key'][0] == item_id and b['contribution'] in {'partial', 'whole_scope'}, 'unknown/duplicate contribution')
            seen.add(key)
    return {'targets': sorted(targets), 'facts': dict(sorted(facts.items())),
            'provenance': dict(sorted(provenance.items())), 'profiles': profiles,
            'applications': applications}


def selector_domain(inputs):
    return identity(sorted({identity([f['fact_kind'], f['payload']]) for f in inputs['facts'].values()}))


def read_review(root, inputs):
    review = inv.read_json(root / ROOT / 'review.json')
    inv.require(review['schema'] == SCHEMA and review['inputs'] == INPUTS, 'stale review inputs')
    inv.require(review['payload_domain_sha256'] == selector_domain(inputs), 'unreviewed payload branch')
    inv.require(review['profile_grammars'] == rules.PROFILE_GRAMMARS
                and set(inputs['profiles']) == set(rules.PROFILE_GRAMMARS), 'unreviewed profile grammar')
    inv.require(review['modules'] == [inv.binding(root, CODE + name + '.py') for name in MODULES], 'stale rule review')
    for locale in rules.LOCALES:
        inv.require(review['locales'][locale]['state'] == 'approved' and review['locales'][locale]['reviewer']
                    and review['locales'][locale]['findings'], 'expression_gap: unreviewed locale')
    return review


def _profiles(application, inputs):
    rows = []
    relations = application['fact_question_bindings']
    for route in sorted(application['routing'], key=lambda r: r['profile_id']):
        profile_id = route['profile_id']
        inv.require(profile_id in inputs['profiles'] and profile_id in rules.PROFILE_GRAMMARS, 'unknown profile')
        # Resolver can retain confirmed scopes while recording a conflicting
        # applicability observation. Keep those scopes exactly as supplied.
        if not route['scope_refs']:
            continue
        profile = inputs['profiles'][profile_id]
        refs = sorted({qualify(b['authority_ref'], b['fact_ref']) for b in relations
                       if b['question_key'][1] in profile['required_axes'] and b['question_key'][2] in route['scope_refs']})
        rows.append({'profile_id': profile_id, 'scope_refs': sorted(route['scope_refs']),
                     'applicability': route['state'], 'grammar': rules.PROFILE_GRAMMARS[profile_id], 'fact_refs': refs})
    return rows


def _selection(application, facts):
    obligations = []
    selected = set()
    axes = {(r['axis_id'], r['scope_ref']): r for r in application['required_axes']}
    for obligation in sorted(application['first_contact'], key=lambda r: (r['axis_id'], r['scope_ref'])):
        key = (obligation['axis_id'], obligation['scope_ref'])
        relations = sorted((deepcopy(b) for b in application['fact_question_bindings'] if tuple(b['question_key'][1:]) == key), key=canonical)
        refs = {qualify(b['authority_ref'], b['fact_ref']) for b in relations}
        axis = axes[key]
        result = axis['result']
        if axis['terminal'] and axis['state'] == 'resolved':
            refs.update(qualify(result['authority_ref'], f) for f in result['fact_refs'])
        inv.require(all(r in facts and facts[r]['item_id'] == application['item_id'] for r in refs), 'unknown first-contact contributor')
        state = 'accepted_contributors' if refs else ('scoped_not_applicable' if axis['state'] == 'evidence_backed_not_applicable' else 'upstream_gap')
        obligations.append({'question_key': [application['item_id'], *key], 'profile_refs': sorted(obligation['contributors']),
                            'state': state, 'upstream_state': axis['state'], 'contributions': relations,
                            'fact_refs': sorted(refs)})
        selected.update(refs)
    return selected, obligations


def _expand_qualifiers(selected, facts):
    # A first-contact condition must name the claim it qualifies. This does not
    # turn a partial question answer into a terminal result.
    refs = set(selected)
    for ref in sorted(selected):
        if facts[ref]['fact_kind'] in {'condition', 'constraint'}:
            refs.update(facts[ref]['applies_to_refs'])
    return refs


def expression(fact, facts, locale, review_id):
    if fact['fact_kind'] == 'acquisition':
        text, represented = routes.realize(fact, locale), [fact['ref']]
        dependencies = [{'fact_ref': fact['ref'], 'payload_path': path, 'kind': 'route_condition', 'projection': 'user_proposition'}
                        for path in routes.dependency_paths(fact)]
        rule = 'acquisition/' + fact['payload']['route']['method']
    else:
        text, represented = rules.qualified(fact, facts, locale)
        dependencies = [{'fact_ref': ref, 'kind': facts[ref]['fact_kind']} for ref in represented if ref != fact['ref']]
        rule = 'semantic/' + fact['fact_kind']
    inv.require(text.strip() and '\r' not in text and '\n' not in text, 'expression_gap: invalid logical row')
    row = {'locale': locale, 'resolution': 'expanded', 'text': text, 'claim_ref': fact['ref'], 'represented_fact_refs': represented,
           'dependency_refs': dependencies, 'rule_ref': rule + '/' + locale, 'review_ref': review_id + '/' + locale}
    return {'expression_id': identity(row), **row}


def _blocks(expressions, profiles, facts):
    """Union all profile contributions; never elect a representative owner.

    Context grammars connect roles to their own activity. Direct/effect grammars
    keep separate qualifier sets, so a poison condition cannot qualify thirst
    relief or mere drinking. Group only identical contributor signatures.
    """
    groups = defaultdict(list)
    for ex in expressions:
        owners = tuple((p['profile_id'], canonical(rules.composition_scope(p['profile_id'], facts[ex['claim_ref']])))
                       for p in profiles if set(p['fact_refs']) & set(ex['represented_fact_refs']))
        groups[owners].append(ex)
    blocks = []
    for owners, group in sorted(groups.items()):
        # Dependencies are adjacent to each sentence; grouping never widens them.
        group.sort(key=lambda e: (facts[e['claim_ref']]['fact_kind'], e['claim_ref']))
        blocks.append({'profile_refs': [p for p, _ in owners], 'composition': 'profiles' if owners else 'residual',
                       'composition_rules': [rules.PROFILE_GRAMMARS[p] for p, _ in owners],
                       'expression_refs': [e['expression_id'] for e in group],
                       'text': ' '.join(e['text'] for e in group),
                       'represented_fact_refs': sorted({r for e in group for r in e['represented_fact_refs']}),
                       'dependency_refs': sorted({canonical(d): d for e in group for d in e['dependency_refs']}.values(), key=canonical)})
    return blocks


def _coalesce_contexts(expressions, facts):
    """Remove duplicate activity mentions only under equal qualifier scope.

    Every role is retained. A role clause already says the activity and may
    carry its fact identity; stricter role conditions cannot replace the less
    restricted activity clause. This is mention deduplication, not fact fusion.
    """
    covered = set()
    for e in expressions:
        claim = facts[e['claim_ref']]
        context_ref = claim['context_ref']
        if context_ref and set(claim['qualifier_refs']) <= set(facts[context_ref]['qualifier_refs']):
            covered.add(context_ref)
    return [e for e in expressions if e['claim_ref'] not in covered]


def produce(inputs, review):
    """Pure deterministic composition; no I/O and no product writer dispatch."""
    facts, review_id = inputs['facts'], identity(review)
    inv.require(selector_domain(inputs) == review['payload_domain_sha256'], 'unreviewed payload branch')
    by_item = defaultdict(list)
    for fact in facts.values():
        by_item[fact['item_id']].append(fact)
    expressions, items = [], []
    for item_id in sorted(inputs['targets']):
        application = inputs['applications'][item_id]
        profiles = _profiles(application, inputs)
        selected, obligations = _selection(application, facts)
        selected_claims = _expand_qualifiers(selected, facts)
        accepted = {f['ref'] for f in by_item[item_id]}
        locales = {}
        for locale in rules.LOCALES:
            inv.require(review['locales'][locale]['state'] == 'approved', 'expression_gap: locale not approved')
            group = [expression(f, facts, locale, review_id) for f in sorted(by_item[item_id], key=lambda f: f['ref'])
                     if f['fact_kind'] not in {'condition', 'constraint'}]
            group = _coalesce_contexts(group, facts)
            expanded = _blocks(group, profiles, facts)
            represented = {r for e in group for r in e['represented_fact_refs']}
            inv.require(represented == accepted, 'expression_gap: expanded fact/dependency loss')
            units, detail_qualifiers = projection.compose(selected_claims, facts, locale)
            compact = []
            for unit in units:
                row = {**unit, 'locale': locale, 'resolution': 'compact', 'review_ref': review_id + '/' + locale,
                       'profile_refs': [p['profile_id'] for p in profiles if set(p['fact_refs']) & set(unit['represented_fact_refs'])]}
                compact.append({'expression_id': identity(row), **row})
            s2_refs = {r for e in compact for r in e['represented_fact_refs']}
            inv.require(selected <= s2_refs | set(detail_qualifiers) and s2_refs <= accepted, 'expression_gap: compact contributor loss')
            locales[locale] = {
                'expanded': expanded, 'expanded_represented_fact_refs': sorted(represented),
                's2': {'text': ' '.join(e['text'] for e in compact),
                       'logical_rows': int(bool(compact)),
                       'expression_refs': [e['expression_id'] for e in compact],
                       'represented_fact_refs': sorted(s2_refs),
                       'detail_qualifier_refs': detail_qualifiers,
                       'dependency_refs': sorted({canonical(d): d for e in compact for d in e['dependency_refs']}.values(), key=canonical),
                       'state': 'expressed' if compact else ('upstream_gap' if any(o['state'] == 'upstream_gap' for o in obligations)
                                                           else ('scoped_not_applicable' if obligations else 'no_first_contact'))},
                'tooltip_detail_omission_refs': sorted(accepted - s2_refs),
                'fact_expressions': {r: sorted(e['expression_id'] for e in group if r in e['represented_fact_refs']) for r in sorted(accepted)},
            }
            expressions.extend([*group, *compact])
        items.append({'item_id': item_id, 'profiles': profiles, 'first_contact_obligations': obligations,
                      'upstream': {k: deepcopy(application[k]) for k in ('scope_state', 'pending_scope_refs', 'coverage_gap_state', 'acquisition_state', 'item_investigation_state')},
                      'locales': locales})
    return {'schema': SCHEMA, 'status': 'candidate', 'completion': 'complete', 'inputs': deepcopy(INPUTS),
            'denominators': {'targets': len(items), 'facts': len(facts), 'fact_locale_pairs': len(facts) * 2,
                             'acquisition_facts': sum(f['fact_kind'] == 'acquisition' for f in facts.values())},
            'review_ref': review_id, 'facts': [facts[r] for r in sorted(facts)], 'provenance': inputs['provenance'],
            'expressions': sorted(expressions, key=lambda e: e['expression_id']), 'items': items,
            'expression_gaps': [], 'product_migration': 'deferred'}


def validate_payload(payload, inputs, review):
    """Consumer integrity: reject added, missing or reworded claims and refs.

    Reconstruction uses only the bound propositions and reviewed rules, never
    raw game sources. It is part of the loader contract, not another gate.
    """
    inv.require(payload == produce(inputs, review), 'description/reference/review drift')


def _output(root):
    return inv.local_path(root, ROOT)


def prepare(root):
    installed_identity(root)
    inputs = read_inputs(root)
    review = read_review(root, inputs)
    payload = produce(inputs, review)
    inv.require(payload['denominators'] == DENOMINATORS, 'exact denominator drift')
    directory = _output(root)
    receipt = inv.read_json(directory / 'adoption.json') if (directory / 'adoption.json').exists() else None
    inv.require(receipt is None or receipt.get('state') == 'superseded', 'adopted authority is immutable')
    directory.mkdir(parents=True, exist_ok=True)
    write(directory / 'descriptions.json', payload)
    paths = [ROOT + '/descriptions.json', ROOT + '/review.json', CONTRACT, TEST_SOURCE,
             *(CODE + name + '.py' for name in MODULES)]
    manifest = {'schema': SCHEMA, 'status': 'adoption_subject', 'inputs': INPUTS,
                'denominators': DENOMINATORS, 'data': inv.binding(root, paths[0]),
                'review': inv.binding(root, paths[1]), 'members': [inv.binding(root, p) for p in paths],
                'serialization': 'UTF-8; LF; sorted object keys; compact JSON; sorted identities; no semantic ordering',
                'gate': GATE, 'product_migration': 'deferred'}
    if receipt:
        manifest['supersedes'] = receipt['manifest']
    write(directory / 'manifest.json', manifest)
    return inv.binding(root, ROOT + '/manifest.json')


def load(root, ref, *, mode='adopted', inputs=None):
    inv.require(mode in {'candidate', 'adopted'}, 'unknown expression mode')
    inv.require(ref['path'] == ROOT + '/manifest.json', 'unexpected expression readpoint')
    manifest = inv.bound_json(root, ref)
    inv.require(manifest['schema'] == SCHEMA and manifest['status'] == 'adoption_subject'
                and manifest['inputs'] == INPUTS and manifest['denominators'] == DENOMINATORS
                and manifest['gate'] == GATE and manifest['product_migration'] == 'deferred', 'mixed/invalid expression manifest')
    expected = {ROOT + '/descriptions.json', ROOT + '/review.json', CONTRACT, TEST_SOURCE,
                *(CODE + n + '.py' for n in MODULES)}
    members = {r['path']: r for r in manifest['members']}
    inv.require(len(members) == len(manifest['members']) and set(members) == expected, 'unknown/missing/duplicate member')
    for binding in manifest['members']:
        inv.require(inv.binding(root, binding['path']) == binding, 'expression member drift')
    inv.require(manifest['data'] == members[ROOT + '/descriptions.json'] and manifest['review'] == members[ROOT + '/review.json'], 'unbound data member')
    # The optional shared input is internal to the single acceptance execution.
    # Public adopted consumption always reloads the adopted authorities.
    inv.require(inputs is None or mode == 'candidate', 'adopted input override forbidden')
    inputs = read_inputs(root) if inputs is None else inputs
    review = read_review(root, inputs)
    payload = inv.bound_json(root, manifest['data'])
    validate_payload(payload, inputs, review)
    if mode == 'adopted':
        receipt = inv.read_json(_output(root) / 'adoption.json')
        inv.require(receipt['state'] == 'adopted' and receipt['manifest'] == ref and receipt['gate'] == GATE
                    and receipt['gate_exit_code'] == 0 and receipt['authorization'], 'unadopted expression candidate')
        inv.require(manifest.get('supersedes') == receipt.get('superseded_result', {}).get('manifest'), 'superseded subject mismatch')
    return {'mode': mode, 'manifest': manifest, 'payload': payload}


def adopt(root, expected_sha256, gate_exit_code, authorization):
    inv.require(gate_exit_code == 0 and authorization.strip(), 'successful focused gate and owner authorization required')
    installed_identity(root)
    ref = inv.binding(root, ROOT + '/manifest.json')
    inv.require(ref['sha256'] == expected_sha256, 'candidate changed after acceptance')
    receipt_path = _output(root) / 'adoption.json'
    previous_bytes = receipt_path.read_bytes() if receipt_path.exists() else None
    previous = json.loads(previous_bytes) if previous_bytes else None
    inv.require(previous is None or previous.get('state') == 'superseded', 'adoption already exists')
    manifest = inv.read_json(_output(root) / 'manifest.json')
    inv.require(manifest.get('supersedes') == (previous['manifest'] if previous else None), 'superseded subject mismatch')
    # Candidate already occupies its final location. Re-materialize exact bytes,
    # then perform fail-closed adopted readback in this same state transition.
    manifest_path = _output(root) / 'manifest.json'
    manifest_path.write_bytes(manifest_path.read_bytes())
    try:
        receipt = {'schema': SCHEMA, 'state': 'adopted', 'manifest': ref,
                             'gate': GATE, 'gate_exit_code': gate_exit_code, 'authorization': authorization,
                             'product_migration': 'deferred'}
        if previous:
            receipt['superseded_result'] = previous
        write(receipt_path, receipt)
        load(root, ref, mode='adopted')
    except BaseException:
        if previous_bytes:
            receipt_path.write_bytes(previous_bytes)
        else:
            receipt_path.unlink(missing_ok=True)
        raise
    return ref


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'adopt'))
    parser.add_argument('--repository-root', type=Path, required=True)
    parser.add_argument('--candidate-sha256')
    parser.add_argument('--gate-exit-code', type=int)
    parser.add_argument('--authorization', default='')
    args = parser.parse_args(argv)
    root = args.repository_root.resolve()
    inv.require((root / '.git').exists(), 'explicit repository required')
    ref = prepare(root) if args.action == 'prepare' else adopt(root, args.candidate_sha256, args.gate_exit_code, args.authorization)
    print(json.dumps({'action': args.action, 'manifest': ref}, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
