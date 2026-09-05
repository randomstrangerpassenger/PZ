"""One L3-04 G1 identity; fixtures plus candidate corpus, then limited adoption."""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest

from iris_tooling.domains.layer3 import acquisition_consumption as combined
from iris_tooling.domains.layer3 import acquisition_results as acquisition
from iris_tooling.domains.layer3 import acquisition_sources as sources
from iris_tooling.domains.layer3 import investigation as inv
from iris_tooling.domains.layer3 import semantic_model as model
from iris_tooling.domains.layer3 import semantic_results as semantic
from test_layer3_semantic_results import fixture as semantic_fixture

REPO = Path(__file__).resolve().parents[5]


def fixture(contract):
    path = 'scripts/fixture.txt'
    observation = {'source_path': path, 'source_sha256': 'a' * 64, 'locator': 'L1',
                   'content': {'raw': 'closed fixture source; Sample is created when fixture conditions hold',
                               'role': 'bounded-member-survey', 'line_count': 1, 'method': 'fixture source interpretation'}}
    oid = model.identity('obs', observation)
    hit = {'source_path': path, 'source_sha256': 'a' * 64, 'locator': 'L1',
           'content': {'raw': 'Base.Sample', 'role': 'identity-search-lead', 'item_id': 'Base.Sample'}}
    hid = model.identity('obs', hit)
    payload = {'schema_version': acquisition.SCHEMA, 'status': 'candidate', 'authority_id': 'acquisition-fixture',
               'registry_revision': contract['revision'], 'target_ids': ['Base.Sample'],
               'source_bindings': [{'path': path, 'sha256': 'a' * 64}],
               'observations': {oid: observation, hid: hit}, 'traces': {}, 'rules': acquisition.RULES,
               'facts': [], 'provenance': {}, 'negative_evidence': {},
               'families': {f: {'members': [path], 'observation_refs': [oid], 'method': 'fixture complete survey',
                                 'finding': 'Fixture path/consumer/conditions examined', 'consumer_trace': 'source -> factory -> delivery',
                                 'closed_negative_capable': False, 'trace_refs': [], 'unreviewed_trace_refs': []} for f in sources.FAMILIES},
               'coverage': [{'item_id': 'Base.Sample', 'family_id': f, 'outcome': 'interpretation_unresolved',
                             'attempt_ref': model.identity('attempt', ['Base.Sample', f]), 'survey_ref': f,
                             'observation_refs': [hid], 'query': {'exact': 'Base.Sample', 'unqualified_lead': 'Sample'},
                             'finding': 'Exact identity examined; additional paths open', 'dependency': 'additional engine path'} for f in sources.FAMILIES]}
    path_row = {'item_id': 'Base.Sample', 'path': path, 'line': 1, 'raw': 'Base.Sample', 'rule': 'foraging',
                'route': {'method': 'foraging', 'definition': 'sample'}, 'conditions': {'eligibility': 'fixture predicate'},
                'consumer_paths': [path], 'limitations': 'Additional unknown path is independent of this fact.'}
    acquisition.add_path(payload, path_row, {path: oid})
    acquisition.assemble_results(payload)
    return payload, path_row, {path: oid}


class Layer3AcquisitionResultsTest(unittest.TestCase):
    def test_acquisition_results_contract(self):
        mode = os.environ.get('IRIS_LAYER3_ACQUISITION_MODE', 'adopted')
        self.assertIn(mode, {'candidate', 'adopted'})
        manifest_path = os.environ.get('IRIS_LAYER3_ACQUISITION_MANIFEST', acquisition.ROOT + '/manifest.json')
        ref = inv.binding(REPO, manifest_path)
        loaded = combined.load(REPO, ref, mode=mode)
        payload, prior, applications = loaded['acquisition'], loaded['semantic'], loaded['applications']
        contract = inv.read_json(REPO / inv.ROOT / 'contract.json')
        inherited = inv.inherited_contract(REPO, contract['inherits'])
        manifest = inv.bound_json(REPO, ref)
        self.assertEqual(len(payload['target_ids']), 2105)
        self.assertEqual(payload['target_ids'], inv.targets(REPO))
        self.assertEqual(len(payload['coverage']), 2105 * 6)
        self.assertEqual((len(prior['facts']), len(prior['results'])), (4233, 9982))
        self.assertEqual(sum(a['item_investigation_state'] == 'complete' for a in applications), 0)
        for path, digest in manifest['protected'].items():
            member = inv.local_path(REPO, path)
            self.assertEqual(inv.sha(member) if member.exists() else None, digest, path)
        for path, digest in manifest['existing_registration'].items():
            self.assertEqual(model.identity('registration', acquisition.registration_projection(path, inv.read_json(REPO / path))), digest, path)
        if mode == 'adopted':
            registry = inv.read_json(REPO / acquisition.REGISTRY)
            self.assertEqual(sum(r['test_id'] == acquisition.TEST_ID for r in registry['required_tests']), 1)
            authority = inv.read_json(REPO / acquisition.AUTH)
            self.assertEqual([r['sha256'] for r in authority['entries'] if r.get('path') == ref['path']], [ref['sha256']])
            policy = inv.read_json(REPO / acquisition.POLICY)
            self.assertEqual([r['classification'] for r in policy['reviewed_sources'] if r['source_file'] == acquisition.TEST_SOURCE], ['current'])
            print(json.dumps({'mode': mode, 'manifest': ref, 'corpus': manifest['corpus'],
                              'questions': len(payload['results']), 'states': dict(Counter(r['state'] for r in payload['results'])),
                              'applications': len(applications)}))
            return

        # Reuse the survey's bound raw source observations for admission checks.
        # This is not another independent production or manual semantic audit.
        member_text = {o['source_path']: o['content']['raw'] for o in payload['observations'].values()
                       if o['content']['role'] == 'bounded-member-survey'}
        declarations = defaultdict(list)
        from iris_tooling.domains.layer3 import source_reader
        for path, raw in member_text.items():
            if path.startswith('scripts/'):
                for row in source_reader.declarations(raw, path):
                    if row['kind'] == 'item':
                        declarations[row['module'] + '.' + row['name']].append(row)
        scan = {'texts': member_text, 'declarations': declarations}
        expected_paths = sources.positive_paths(scan, payload['target_ids']) + sources.starter_paths(scan, payload['target_ids']) + sources.recovery_paths(scan, payload['target_ids'])
        expected = {model.fact_identity({'item_id': p['item_id'], 'fact_kind': 'acquisition',
                                         'payload': {'route': p['route'], 'conditions': p['conditions']}}) for p in expected_paths}
        self.assertEqual({f['fact_id'] for f in payload['facts']}, expected)
        worm = [f for f in payload['facts'] if f['item_id'] == 'Base.Worm']
        self.assertTrue({'foraging', 'incidental_plowing', 'incidental_ground_digging'} <= {f['payload']['route']['method'] for f in worm})
        generator = next(f for f in payload['facts'] if f['item_id'] == 'Base.Generator' and f['payload']['route']['method'] == 'world_generator_recovery')
        self.assertIn('not connected', generator['payload']['conditions']['eligibility'])
        engine = [t for t in payload['traces'].values() if t.get('function') == 'Commands.takeEngineParts']
        self.assertTrue(engine)
        self.assertTrue(all(any(c['source_path'].endswith('/ISTakeEngineParts.lua') for c in t['consumer_connections']) for t in engine))
        self.assertTrue(all('engine code absent' in t['finding'] for t in engine))
        self.assertEqual(payload['predecessor'], acquisition.predecessor(REPO))
        counts = payload['predecessor']['counts']
        self.assertEqual([counts[k] for k in ('H', 'B', 'intersection', 'H_only', 'B_only', 'union')], [1105, 55, 55, 1050, 0, 1105])
        self.assertTrue({'ko', 'en'} <= payload['predecessor']['locale_inventory'].keys())
        self.assertEqual(len({r['material_id'] for r in payload['predecessor']['records']}), len(payload['predecessor']['records']))
        book = [r for r in payload['predecessor']['records'] if r['item_id'] == 'Base.BookTrapping1']
        self.assertTrue(any(r['kind'] == 'product_role' and r['value'] == [] for r in book))
        self.assertEqual({r['locale'] for r in book if r['kind'] == 'product_expression' and r['claim_spans']}, {'ko', 'en'})
        self.assertEqual({i: r['declarations'] for i, r in payload['identity_uncertainty'].items()},
                         {'Base.Bag_PistolCase': 0, 'Base.Lemongrass': 0, 'Base.NoiseMaker': 0, 'Base.ShotgunCase1': 2})
        standalone = model.consume(prior, contract, inherited, loaded['readpoints']['semantic'])
        self.assertEqual([combined.non_acquisition_projection(a) for a in standalone],
                         [combined.non_acquisition_projection(a) for a in applications])

        base, path_row, members = fixture(contract)
        acquisition.validate_payload(base, contract, complete=True)
        # Additional uncertain paths do not force a confirmed answer unresolved.
        self.assertEqual(base['results'][0]['state'], 'resolved')
        sem = semantic_fixture(contract)
        apps = combined.consume_payloads(sem, base, contract, inherited, {'sha256': 'b' * 64}, {'sha256': 'c' * 64})
        self.assertEqual(apps[0]['acquisition_state'], 'resolved')
        self.assertEqual(apps[0]['item_investigation_state'], 'incomplete')
        unperformed = deepcopy(base)
        unperformed['coverage'][0].update(outcome='not_attempted', not_attempted_reason='Required source not yet examined')
        acquisition.assemble_results(unperformed)
        acquisition.validate_payload(unperformed, contract)
        self.assertEqual(unperformed['results'][0]['state'], 'not_investigated')
        self.assertEqual(unperformed['fact_question_bindings'][0]['contribution'], 'partial')
        open_apps = combined.consume_payloads(sem, unperformed, contract, inherited, {'sha256': 'b' * 64}, {'sha256': 'c' * 64})
        self.assertTrue(any(r['authority_ref'] == unperformed['authority_id'] for r in open_apps[0]['fact_question_bindings']))
        with self.assertRaises(ValueError):
            acquisition.validate_payload(unperformed, contract, complete=True)

        changes = [
            lambda p: p['target_ids'].append('Base.Sample'),
            lambda p: p['coverage'].pop(),
            lambda p: p['families'].pop('vehicle'),
            lambda p: p['coverage'][0].update(outcome='skipped'),
            lambda p: p['coverage'][0].update(outcome='access_failure', access_failure_target='scripts/fixture.txt', access_error='denied'),
            lambda p: p['families']['loot'].update(observation_refs=[]),
            lambda p: p['families']['loot'].update(consumer_trace=''),
            lambda p: p['results'][0].update(state='investigated_unresolved', fact_refs=[]),
            lambda p: p['results'][0].update(authority_ref='wrong'),
            lambda p: p['results'][0].update(registry_revision='stale'),
            lambda p: p['facts'][0]['payload'].update(conditions={}),
            lambda p: p['facts'][0].update(fact_kind='acquisition_unobtainable'),
            lambda p: p['fact_question_bindings'][0].update(question_key=['Base.Other', 'acquisition', 'item']),
            lambda p: p['facts'][0].update(provenance_refs=[]),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                broken = deepcopy(base)
                change(broken)
                with self.assertRaises(ValueError):
                    acquisition.validate_payload(broken, contract)
        unreviewed = deepcopy(base)
        trace = {'source_path': 'scripts/fixture.txt', 'locator': 'L1', 'assessment': 'unreviewed',
                 'method': 'caller collected', 'finding': 'interpretation not implemented', 'dependency': 'actual review'}
        tid = model.identity('trace', trace)
        unreviewed['traces'][tid] = trace
        for family in unreviewed['families'].values():
            family.update(trace_refs=[tid], unreviewed_trace_refs=[tid])
        with self.assertRaisesRegex(ValueError, 'source collection'):
            acquisition.validate_payload(unreviewed, contract)
        empty = deepcopy(base)
        empty.update(facts=[], provenance={})
        acquisition.assemble_results(empty)
        acquisition.validate_payload(empty, contract, complete=True)
        self.assertEqual(empty['results'][0]['state'], 'investigated_unresolved')
        self.assertFalse(empty['negative_evidence'])
        # A truly closed synthetic universe exercises inherited negative admission.
        # This fixture is not evidence or a rule for the real game snapshot.
        negative = deepcopy(empty)
        closure = {'source_path': 'scripts/fixture.txt', 'source_sha256': 'a' * 64, 'locator': 'L2',
                   'content': {'raw': 'Synthetic complete universe has no acquisition outputs or external dispatch.',
                               'role': 'closed-acquisition-enumeration', 'scope': 'item-global',
                               'excludes_dynamic_and_engine_omissions': True, 'enumerated_items': []}}
        cid = model.identity('obs', closure)
        negative['observations'][cid] = closure
        explanation = deepcopy(closure)
        explanation['content'].update(role='interpreted-acquisition', item_id='Base.Sample')
        eid = model.identity('obs', explanation)
        negative['observations'][eid] = explanation
        negative['rules'] = {'synthetic_closed': {'review_state': 'reviewed', 'interpretation': 'Synthetic complete empty acquisition universe only'}}
        evidence = {'item_id': 'Base.Sample', 'authority_ref': negative['authority_id'], 'closed_scope': True,
                    'coverage_complete': True, 'false_negative_limit': 'excluded_within_bound_scope',
                    'scope_description': 'Synthetic universe has no dynamic or engine omissions.',
                    'source_bindings': negative['source_bindings'], 'closure_observation_refs': [cid]}
        nid = model.identity('negative', evidence)
        negative['negative_evidence'] = {nid: evidence}
        fact = {'item_id': 'Base.Sample', 'fact_kind': 'acquisition_unobtainable', 'status': 'accepted',
                'payload': {'scope': 'item'}, 'negative_evidence_refs': [nid],
                'admission': {'rule_ref': 'synthetic_closed', 'supported': True}}
        fid = model.fact_identity(fact)
        provenance = {'item_id': 'Base.Sample', 'source_path': closure['source_path'], 'source_sha256': 'a' * 64,
                      'locator': 'L2', 'rule_ref': 'synthetic_closed', 'semantic_identity': fid,
                      'observation_refs': [cid, eid], 'proposition': model.canonical(fact['payload']),
                      'limitation': 'Synthetic fixture only, never transferred to a real item.'}
        pid = model.identity('prov', provenance)
        negative.update(facts=[{**fact, 'fact_id': fid, 'provenance_refs': [pid]}], provenance={pid: provenance})
        for family in negative['families'].values():
            family['closed_negative_capable'] = True
        acquisition.assemble_results(negative)
        acquisition.validate_payload(negative, contract, complete=True)
        self.assertEqual(combined.consume_payloads(sem, negative, contract, inherited, {'sha256': 'b' * 64}, {'sha256': 'c' * 64})[0]['acquisition_state'], 'resolved')
        partial = deepcopy(negative)
        partial['families']['dynamic']['closed_negative_capable'] = False
        with self.assertRaisesRegex(ValueError, 'partial family closure'):
            acquisition.validate_payload(partial, contract)
        contradicted = deepcopy(negative)
        contradicted['rules'].update(base['rules'])
        acquisition.add_path(contradicted, path_row, members)
        acquisition.assemble_results(contradicted)
        with self.assertRaisesRegex(ValueError, 'positive contradicts negative'):
            acquisition.validate_payload(contradicted, contract)
        # Metadata, input order and equal-meaning provenance cannot select a representative.
        multiple = deepcopy(base)
        acquisition.add_path(multiple, {**path_row, 'line': 2, 'limitations': 'second source occurrence'}, members)
        acquisition.add_path(multiple, {**path_row, 'conditions': {'eligibility': 'different fixture condition'}}, members)
        self.assertEqual(len(multiple['facts']), 2)
        self.assertEqual(len(multiple['facts'][0]['provenance_refs']), 2)
        other_source = 'scripts/other.txt'
        other_member = deepcopy(next(iter(base['observations'].values())))
        other_member.update(source_path=other_source, source_sha256='d' * 64)
        mid = model.identity('obs', other_member)
        multiple['source_bindings'].append({'path': other_source, 'sha256': 'd' * 64})
        multiple['observations'][mid] = other_member
        for family in multiple['families'].values():
            family['members'] = sorted([*family['members'], other_source])
            family['observation_refs'].append(mid)
        acquisition.add_path(multiple, {**path_row, 'path': other_source, 'consumer_paths': [other_source]}, {other_source: mid})
        self.assertEqual(len(multiple['facts'][0]['provenance_refs']), 3)
        acquisition.assemble_results(multiple)
        acquisition.validate_payload(multiple, contract, complete=True)
        reordered = deepcopy(multiple)
        reordered['facts'].reverse()
        reordered['coverage'].reverse()
        acquisition.assemble_results(reordered)
        self.assertEqual(multiple['results'], reordered['results'])
        for mode_change in ('status', 'authority_id'):
            mismatch = deepcopy(base)
            mismatch[mode_change] = 'adopted' if mode_change == 'status' else sem['authority_id']
            with self.assertRaises(ValueError):
                combined.consume_payloads(sem, mismatch, contract, inherited, {'sha256': 'b' * 64}, {'sha256': 'c' * 64})
        with self.assertRaises(ValueError):
            acquisition.output_directory(REPO, Path('../escape'))
        with self.assertRaises(ValueError):
            acquisition.output_directory(REPO, Path('Iris/media'))
        with self.assertRaises(ValueError):
            acquisition.output_directory(REPO, Path(manifest_path).parent)
        policy = inv.read_json(REPO / acquisition.POLICY)
        self.assertEqual(sum(r['source_file'] == acquisition.TEST_SOURCE for r in policy['reviewed_sources']), 1)
        print(json.dumps({'mode': mode, 'manifest': ref, 'corpus': manifest['corpus'],
                          'states': dict(Counter(r['state'] for r in payload['results'])),
                          'positive': len(payload['facts']), 'negative': len(payload['negative_evidence']),
                          'unreviewed_traces': sum(t['assessment'] == 'unreviewed' for t in payload['traces'].values())}))
        # This remains a real acceptance requirement. A partial survey cannot
        # turn a diagnostic contract success into G1/adoption success.
        acquisition.validate_payload(payload, contract, complete=True)
