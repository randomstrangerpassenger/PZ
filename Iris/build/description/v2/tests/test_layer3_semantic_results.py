"""L3-03 G1: one public contract test, one real corpus consumption."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

from iris_tooling.domains.layer3 import investigation as inv
from iris_tooling.domains.layer3 import semantic_model as model
from iris_tooling.domains.layer3 import semantic_results as semantic
from iris_tooling.domains.layer3 import source_reader as reader
from iris_tooling.domains.layer3 import interpretations as meaning

REPO = Path(__file__).resolve().parents[5]
AUTH = 'Iris/_docs/authority/iris_current_authority_manifest.json'
ROUTE = 'Iris/_docs/authority/iris_current_route_index.json'
REGISTRY = 'Iris/validation/execution/required_validations.json'
POLICY = 'Iris/_docs/round3/round3_pytest_source_classification.json'


def fixture(contract, activity='woodworking'):
    item = 'Base.Sample'
    b = semantic.Builder({'scripts/fixture.txt': 'a' * 64})
    obs = b.observe('scripts/fixture.txt', 'L1:recipe:Woodwork', {'raw': 'keep Sample; woodworking fixture'})
    b.activity(item, activity, 'tool', [obs], 'woodwork', ['activity:crafting'], 'The fixture recipe is eligible.')
    aid = 'fixture'
    results, universe, bindings = [], [], []
    for axis in ('role', 'conditions'):
        key = [item, axis, 'activity:crafting']
        results.append({'item_id': item, 'axis_id': axis, 'scope_ref': key[2], 'question_key': key,
                        'registry_revision': contract['revision'], 'authority_ref': aid,
                        'state': 'investigated_unresolved', 'attempt_refs': ['attempt'],
                        'provenance_refs': list(b.provenance), 'fact_refs': [],
                        'blockers': ['runtime_state'], 'next_source_dependency': 'runtime_state'})
        universe.append({'question_key': key, 'relation': 'retained', 'before_revision': contract['revision'],
                         'after_revision': contract['revision'], 'contributors': ['crafting']})
        kinds = next(a['allowed_result_kinds'] for a in contract['axes'] if a['axis_id'] == axis)
        bindings.extend({'question_key': key, 'fact_ref': f['fact_id'], 'registry_revision': contract['revision'],
                         'authority_ref': aid, 'contribution': 'partial'} for f in b.facts.values() if f['fact_kind'] in kinds)
    routes = [{'profile_id': p['profile_id'],
               'state': 'confirmed_applicable' if p['profile_id'] == 'crafting' else 'evidence_backed_not_applicable',
               'scope_refs': ['activity:crafting'] if p['profile_id'] == 'crafting' else [],
               'evidence_refs': [obs], 'reason': 'Independent fixture scope only'} for p in contract['profiles']]
    return {'schema_version': model.SCHEMA, 'status': 'candidate', 'authority_id': aid,
            'registry_revision': contract['revision'], 'target_ids': [item],
            'source_bindings': [{'path': 'scripts/fixture.txt', 'sha256': 'a' * 64}],
            'observations': b.observations, 'provenance': b.provenance, 'rules': semantic.rule_records(),
            'facts': list(b.facts.values()), 'results': results, 'universe': universe,
            'baseline_key_count': 2, 'baseline_pending_count': 0, 'pending': [],
            'fact_question_bindings': bindings,
            'attempts': {'attempt': {'item_id': item, 'route': 'B', 'observation_refs': [obs],
                                      'method': 'fixture source interpretation', 'finding': 'retained woodworking tool', 'dependency': 'runtime_state'}},
            'application_inputs': [{'item_id': item, 'routes': routes,
                                    'gap': {'state': 'investigated_unresolved', 'kind': 'evidence_gap',
                                            'question': 'Other behavior?', 'missing': 'runtime', 'next': 'runtime'}}]}


class Layer3SemanticResultsTest(unittest.TestCase):
    def test_semantic_results_contract(self):
        mode = os.environ.get('IRIS_LAYER3_SEMANTIC_MODE')
        self.assertIn(mode, (None, 'adoption'))
        manifest_path = os.environ.get('IRIS_LAYER3_SEMANTIC_MANIFEST', semantic.ROOT + '/manifest.json')
        self.assertEqual(manifest_path, semantic.ROOT + '/manifest.json')
        baseline = None
        if mode == 'adoption':
            value = os.environ.get('IRIS_LAYER3_SEMANTIC_BASELINE')
            self.assertTrue(value, 'Missing adoption baseline')
            path = Path(value)
            self.assertTrue(path.is_absolute() and path.resolve().is_relative_to(REPO))
            baseline = json.loads(path.read_text(encoding='utf-8-sig'))
            self.assertEqual(len(baseline['protected']), 33)
            self.assertEqual(len(baseline['generation_members']), 14)
            self.assertEqual(set(baseline['configs']), {AUTH, ROUTE, REGISTRY, POLICY})
            self.assertEqual(baseline['execution_start_head'], subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip())
        ref = inv.binding(REPO, manifest_path)
        manifest, payload = semantic.load_manifest(REPO, ref, mode='candidate')
        self.assertEqual(manifest['adoption_requires'], semantic.TEST_ID)
        contract = inv.read_json(REPO / inv.ROOT / 'contract.json')
        inv.validate_contract(contract)
        inherited = inv.inherited_contract(REPO, contract['inherits'])
        self.assertEqual(payload['target_ids'], inv.targets(REPO))
        self.assertEqual(len(payload['target_ids']), 2105)
        self.assertEqual(payload['target_set_sha256'], '122ca07c483ff8e4af9ef83bfb8d28c950802a124aba1668c234bce3477b2fdb')
        self.assertEqual(payload['definition_readpoint'], inv.binding(REPO, inv.ROOT + '/manifest.json'))
        self.assertEqual(payload['inherits'], contract['inherits'])
        old = inv.read_rows(REPO / inv.ROOT / 'applications.jsonl')
        old_keys = {(a['item_id'], a['axis_id'], a['scope_ref']) for row in old for a in row['required_axes'] if a['axis_id'] != 'acquisition'}
        self.assertEqual(len(old_keys), 8882)
        self.assertEqual(old_keys, {tuple(r['question_key']) for r in payload['universe'] if r['relation'] != 'newly_required'})
        self.assertEqual({(r['item_id'], p['profile_id']) for r in old for p in r['pending_scope_refs']},
                         {(r['item_id'], r['profile_id']) for r in payload['pending']})
        pending_counts = Counter(r['profile_id'] for r in payload['pending'])
        self.assertEqual([pending_counts[k] for k in ('crafting', 'cooking', 'world_work')], [1779, 1879, 2085])
        self.assertEqual(set(payload['source_capability']), set('ABCDE'))
        self.assertEqual({(a['item_id'], a['route']) for a in payload['attempts'].values()},
                         {(item, route) for item in payload['target_ids'] for route in 'ABCDE'})
        for route, capability in payload['source_capability'].items():
            self.assertTrue(capability['source_observation_refs'])
            self.assertTrue(set(capability['source_observation_refs']) <= payload['observations'].keys())
        for attempt in payload['attempts'].values():
            self.assertEqual(attempt['state'], 'investigated_unresolved')
            self.assertEqual(attempt['unfinished_semantic_paths'], [])
        for row in payload['source_interpretations']['actions'].values():
            self.assertEqual(row['state'], 'investigated_unresolved')
            self.assertTrue(row['finding'] and row['source_paths'] and row['observation_refs'])
            self.assertTrue(set(row['observation_refs']) <= payload['observations'].keys())
        for recipe_ref, row in payload['source_interpretations']['recipes'].items():
            self.assertIn(recipe_ref, payload['observations'])
            self.assertEqual(row['state'], 'investigated_unresolved')
            self.assertEqual(row['unfinished_callbacks'], [])
            self.assertEqual(row['defined_but_unreviewed_callbacks'], [])
            self.assertTrue(set(row['reviewed_callback_groups']) <= payload['source_interpretations']['callback_readings'].keys())
            self.assertTrue(row['consumer_interpretation'])
            self.assertTrue(set(row['callback_observation_refs']) <= payload['observations'].keys())
        # This is the only full-corpus resolver invocation. All census and
        # conservation checks below share its returned applications.
        actual = model.consume(payload, contract, inherited, ref)
        summary = model.census(payload, actual)
        self.assertEqual(summary, manifest['census'])
        self.assertEqual(len(actual), 2105)
        self.assertEqual(summary['item_complete'], 0)
        self.assertEqual(summary['acquisition_states'], {'not_investigated': 2105})
        self.assertNotIn('not_investigated', summary['states'])
        self.assertNotIn('not_investigated', summary['pending_dispositions'])
        self.assertEqual(sum(len(a['fact_question_bindings']) for a in actual), len(payload['fact_question_bindings']))
        self.assertEqual(payload['review']['state'], 'reviewed')
        self.assertEqual(set(payload['review']['rules']), set(payload['rules']))
        self.assertEqual(payload['review']['unhandled_defects'], [])
        self.assertTrue({'food', 'tool', 'weapon', 'clothing', 'multi_use', 'low_information'} <=
                        {s['stratum'] for s in payload['review']['samples']})
        for sample in payload['review']['samples']:
            self.assertTrue(sample['finding'] and sample['attempt_refs'])
            self.assertTrue(set(sample['attempt_refs']) <= payload['attempts'].keys())
            self.assertTrue(set(sample['fact_refs']) <= {f['fact_id'] for f in payload['facts']})
        self.assertEqual({a['item_id'] for a in payload['anomalies']},
                         {'Base.Bag_PistolCase', 'Base.Lemongrass', 'Base.NoiseMaker', 'Base.ShotgunCase1'})
        self.assertEqual([len(a['raw_candidates']) for a in payload['anomalies']], [0, 0, 0, 2])
        by_item = inv.exact_rows(actual)
        facts = defaultdict_facts(payload['facts'])
        self.assertIn('eat_food', [f['payload'].get('function') for f in facts['Base.DogfoodOpen']])
        self.assertNotIn('eat_food', [f['payload'].get('function') for f in facts.get('Base.Dogfood', [])])
        self.assertEqual({f['payload']['activity'] for f in facts['Base.Hammer'] if f['fact_kind'] == 'use_context'},
                         {'woodworking', 'construction', 'repair', 'moving_furniture'})
        water_effects = {f['payload']['property']: f for f in facts['Base.BucketWaterFull'] if f['fact_kind'] == 'effect'}
        self.assertEqual(set(water_effects), {'thirst', 'poison_level'})
        self.assertEqual(water_effects['thirst']['payload']['direction'], 'decrease')
        self.assertEqual(water_effects['poison_level']['payload']['direction'], 'increase')
        poison_conditions = [f['payload']['predicate'] for f in facts['Base.BucketWaterFull']
                             if water_effects['poison_level']['fact_id'] in f.get('applies_to_fact_refs', [])]
        self.assertTrue(any('below 20' in p and 'below 0.3' in p for p in poison_conditions))
        self.assertTrue(any('thirst 0.1' in p and 'inventory' in p for p in poison_conditions))
        self.assertIn('Trapping_experience_multiplier', [f['payload'].get('property') for f in facts['Base.BookTrapping1']])
        self.assertIn('store_and_retrieve_items', [f['payload'].get('function') for f in facts['Base.Bag_Schoolbag']])
        self.assertIn('portable_device_power', [f['payload'].get('activity') for f in facts['Base.Battery']])
        self.assertIn('fabric_recovery', [f['payload'].get('activity') for f in facts['Base.Shirt_Denim']])
        self.assertFalse(any(f['fact_kind'] == 'effect' for f in facts['Base.Apple']))
        self.assertTrue(by_item['Base.Notebook']['fact_question_bindings'])
        self.assertTrue(all(a['state'] == 'investigated_unresolved' for a in by_item['Base.Apple']['required_axes'] if a['axis_id'] != 'acquisition'))
        self.assertTrue(any(r['state'] == 'evidence_backed_not_applicable' for r in payload['results'] if r['item_id'] == 'Base.Dogfood'))
        navigation = inv.read_json(REPO / ROUTE)
        link = navigation[semantic.ENTRY]
        self.assertEqual(link['manifest_path'], ref['path'])
        self.assertEqual(link['manifest_sha256'], ref['sha256'])
        self.assertIn(link['state'], ('prepared', 'adopted'))
        registry, policy = inv.read_json(REPO / REGISTRY), inv.read_json(REPO / POLICY)
        self.assertEqual(sum(r['test_id'] == semantic.TEST_ID for r in registry['required_tests']), 1)
        self.assertEqual(sum(r['source_file'] == semantic.TEST_SOURCE for r in policy['planned_sources']), 1)
        if baseline is not None:
            for protected in baseline['protected']:
                self.assertEqual(inv.binding(REPO, protected['path']), protected)
            stripped = deepcopy(navigation)
            stripped.pop(semantic.ENTRY)
            self.assertEqual(stripped, baseline['configs'][ROUTE])
            current = inv.read_json(REPO / AUTH)
            entries = [e for e in current['entries'] if e.get('path') == ref['path']]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['sha256'], ref['sha256'])
            current['entries'].remove(entries[0])
            self.assertEqual(current, baseline['configs'][AUTH])
            registry['required_tests'] = [r for r in registry['required_tests'] if r['test_id'] != semantic.TEST_ID]
            self.assertEqual(registry, baseline['configs'][REGISTRY])
            policy['planned_sources'] = [r for r in policy['planned_sources'] if r['source_file'] != semantic.TEST_SOURCE]
            policy['source_set_binding'] = baseline['configs'][POLICY]['source_set_binding']
            self.assertEqual(policy, baseline['configs'][POLICY])
        self._small_cases(contract, inherited)
        print('Semantic census: ' + json.dumps(summary, sort_keys=True))

    def _small_cases(self, contract, inherited):
        # Function discovery alone is not semantic investigation/admission.
        unread = meaning.recipe_analysis({'clauses': ['OnCreate:NewCallback']}, [], {'NewCallback'}, {'NewCallback': ['source']})
        self.assertEqual(unread['state'], 'not_investigated')
        self.assertEqual(unread['defined_but_unreviewed_callbacks'], ['NewCallback'])
        # Independent source expectations: repeated fields, quoted commas/braces,
        # nested comments, alternative groups, module identity and duplicate items.
        raw = '''module Base { /* outer /* nested */ ignored */
 item X { Type=Normal, Tags=Hammer, Tags=Saw, DisplayName="a,b{c}", }
 item X { Type=Food, } item x { Type=Normal, }
 recipe Work { keep [Recipe.GetItemTypes.Hammer]/x, destroy X, Result:x=2, } }'''
        records = reader.declarations(raw, 'scripts/fixture.txt')
        self.assertEqual([r['name'] for r in records], ['X', 'X', 'x', 'Work'])
        self.assertEqual(reader.properties(records[0])['Tags'], ['Hammer', 'Saw'])
        self.assertIsNone(reader.unique_properties(records[0]))
        groups = reader.groups('function Recipe.GetItemTypes.Hammer(scriptItems)\n scriptItems:addAll(getScriptManager():getItemsTag("Hammer"))\nend')
        links, opaque = reader.recipe_participants(records[-1], {'Base.X': {'Tags': 'Hammer'}, 'Base.x': {'Type': 'Normal'}}, groups)
        self.assertEqual({(r['item_id'], r['role']) for r in links},
                         {('Base.X', 'keep'), ('Base.x', 'keep'), ('Base.X', 'destroy'), ('Base.x', 'result')})
        self.assertFalse(opaque)
        self.assertEqual(reader.literal_hits('-- "Sample"\n if item:getType() == "Sample" then', {'Sample'}), [{'line': 2, 'token': 'Sample'}])
        self.assertNotEqual(inv.set_digest(['Base.X']), inv.set_digest(['Base.x']))
        small = fixture(contract)
        model.validate_payload(small, contract)
        output = model.consume(small, contract, inherited, {'path': 'fixture.json', 'sha256': 'b' * 64})[0]
        self.assertEqual(output['acquisition_state'], 'not_investigated')
        self.assertEqual(len(output['fact_question_bindings']), 3)
        reordered = deepcopy(small)
        reordered['facts'].reverse()
        self.assertEqual(model.consume(reordered, contract, inherited, {'path': 'fixture.json', 'sha256': 'b' * 64}), [output])
        self.assertEqual({f['fact_id'] for f in fixture(contract)['facts']}, {f['fact_id'] for f in small['facts']})
        corrected = fixture(contract, activity='repair')
        self.assertFalse({f['fact_id'] for f in corrected['facts']} & {f['fact_id'] for f in small['facts']})
        corrected_output = model.consume(corrected, contract, inherited, {'path': 'correction.json', 'sha256': 'c' * 64})[0]
        self.assertEqual({tuple(r['question_key']) for r in corrected_output['fact_question_bindings']},
                         {tuple(r['question_key']) for r in output['fact_question_bindings']})
        closed = deepcopy(small)
        for result in closed['results']:
            result.update(state='resolved', question_coverage='whole_scope', coverage_justification='Independent closed fixture, not PZ coverage.',
                          fact_refs=[r['fact_ref'] for r in closed['fact_question_bindings'] if r['question_key'] == result['question_key']])
        for relation in closed['fact_question_bindings']: relation['contribution'] = 'whole_scope'
        closed_output = model.consume(closed, contract, inherited, {'path': 'fixture.json', 'sha256': 'b' * 64})[0]
        self.assertTrue(all(a['terminal'] for a in closed_output['required_axes'] if a['axis_id'] != 'acquisition'))
        self.assertEqual(closed_output['item_investigation_state'], 'incomplete')
        authority = {closed['authority_id']: {**closed, 'binding': {'sha256': 'b' * 64}}}
        role_axis = next(a for a in contract['axes'] if a['axis_id'] == 'role')
        role_result = next(r for r in closed['results'] if r['axis_id'] == 'role')
        for change in ('context', 'qualifier'):
            bad = deepcopy(authority)
            if change == 'context':
                next(f for f in bad['fixture']['facts'] if f['fact_kind'] == 'context_role')['context_fact_ref'] = 'absent'
                axis, result = role_axis, role_result
            else:
                q = next(f for f in bad['fixture']['facts'] if f['fact_kind'] == 'condition')
                q['applies_to_fact_refs'] = [q['fact_id']]
                axis = next(a for a in contract['axes'] if a['axis_id'] == 'conditions')
                result = next(r for r in closed['results'] if r['axis_id'] == 'conditions')
            with self.subTest(dependency=change), self.assertRaises(ValueError):
                inv.terminal_result('Base.Sample', axis, result, inherited, bad, result_mode='candidate')
        fact = deepcopy(small['facts'][0])
        fact.update(registry_revision='unrelated', authority_ref='unrelated', reviewed_at='later')
        self.assertEqual(model.fact_identity(fact), fact['fact_id'])
        fact['payload']['activity'] = 'repair'
        self.assertNotEqual(model.fact_identity(fact), fact['fact_id'])
        mutations = {
            'duplicate fact': lambda p: p['facts'].append(deepcopy(p['facts'][0])),
            'payload correction without rebinding': lambda p: p['facts'][0]['payload'].update(activity='repair'),
            'unsupported fact': lambda p: p['facts'][0]['admission'].update(supported=False),
            'unbound provenance': lambda p: p['provenance'].clear(),
            'unbound open attempt': lambda p: p['results'][0].update(attempt_refs=['missing']),
            'cross item': lambda p: p['results'][0].update(item_id='Base.Other'),
            'wrong scope': lambda p: p['results'][0].update(scope_ref='other'),
            'duplicate result': lambda p: p['results'].append(deepcopy(p['results'][0])),
            'stale result': lambda p: p['results'][0].update(registry_revision='other'),
            'four-component key': lambda p: p['universe'][0]['question_key'].append('revision'),
            'acquisition result': lambda p: p['results'][0].update(axis_id='acquisition'),
            'dangling binding': lambda p: p['fact_question_bindings'][0].update(fact_ref='missing'),
            'partial promoted': lambda p: p['fact_question_bindings'][0].update(contribution='whole_scope'),
            'terminal without coverage': lambda p: p['results'][0].update(state='resolved'),
            'unclosed negative': lambda p: p['results'][0].update(state='evidence_backed_not_applicable'),
            'open fact refs': lambda p: p['results'][0].update(fact_refs=[p['facts'][0]['fact_id']]),
            'invalid kind': lambda p: p['facts'][0].update(fact_kind='primary_use'),
        }
        for name, change in mutations.items():
            with self.subTest(case=name):
                bad = deepcopy(small)
                change(bad)
                # Rendered hints cannot repair missing structured evidence.
                bad.update(prose='A useful tool', profile_label='tool', layer4_display='recipe')
                with self.assertRaises(ValueError): model.validate_payload(bad, contract)
        with patch.object(inv, 'bound_json', return_value=small):
            with self.assertRaises(ValueError): inv.load_result_authorities(REPO, [{'path': 'fixture', 'sha256': 'a' * 64}])
        with self.assertRaises(ValueError): semantic.output_directory(REPO, REPO / 'Iris/media')
        with self.assertRaises(ValueError): semantic.output_directory(REPO, REPO / inv.ROOT)
        with self.assertRaises(ValueError): semantic.output_directory(REPO, REPO.parent / 'outside')
        with self.assertRaises(SystemExit): semantic.main([])
        from iris_tooling.domains.layer3 import cli
        with patch.object(semantic, 'main', return_value=17) as handler:
            self.assertEqual(cli.main(['semantic-results', '--output', 'candidate']), 17)
            handler.assert_called_once_with(['--output', 'candidate'])
        with patch.object(inv, 'main', return_value=18) as handler:
            self.assertEqual(cli.main(['investigate']), 18)
            handler.assert_called_once_with([])
        composer = ModuleType('iris_tooling.build.compose_layer3_text')
        composer.main = Mock(return_value=19)
        with patch.dict(sys.modules, {'iris_tooling.build.compose_layer3_text': composer}):
            self.assertEqual(cli.main(['existing-composer-option']), 19)
        composer.main.assert_called_once_with(['existing-composer-option'])


def defaultdict_facts(facts):
    result = {}
    for fact in facts: result.setdefault(fact['item_id'], []).append(fact)
    return result
