"""Offline description recovery. Historical inputs stay immutable.

This is the correction producer, not a validation registry. Git fallback is
limited to the five missing, hash-bound human contracts; it never substitutes
current source or product bytes. No work is performed at import time.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from . import investigation as inv
from . import semantic_model as model
from . import semantic_results as semantic
from . import source_reader as reader
from . import recovery_sources

AUTH = 'Iris/_docs/authority/dvf/'
FINAL_ROOT = AUTH + 'layer3_expression/successors'
ACCEPTANCE_COMMAND = 'uv run --project .\\Iris\\tooling python -I -B -m pytest --noconftest -c .\\Iris\\tooling\\pyproject.toml .\\Iris\\build\\description\\v2\\tests\\test_layer3_recovery.py -q'
CODE = 'Iris/tooling/src/iris_tooling/domains/layer3/'
POINTER = 'Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua'
PLAN = 'docs/iris_dvf_description_migration_question_adjudication_recovery_plan.md'
HUMANS = frozenset((
    'docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract.md',
    'docs/iris_dvf_layer3_multi_profile_investigation_completion_first_contact_contract.md',
    'docs/iris_dvf_layer3_semantic_investigation_question_results_contract.md',
    'docs/iris_layer3_acquisition_contract.md',
    'docs/iris_layer3_expression_contract.md',
))
READPOINTS = {
    'successor': AUTH + 'layer3_successor/contract_manifest.json',
    'definition': AUTH + 'layer3_investigation/manifest.json',
    'semantic': AUTH + 'layer3_semantic_results/manifest.json',
    'acquisition': AUTH + 'layer3_acquisition_results/manifest.json',
    'expression': AUTH + 'layer3_expression/manifest.json',
}
JOURNAL = 'lua/client/ISUI/ISUIWriteJournal.lua'
NOTE_EDIT = recovery_sources.NOTE_EDIT
CLAIM_FIELDS = ('identity_hint', 'primary_use', 'secondary_use', 'special_context',
                'acquisition_hint', 'processing_hint', 'limitation_hint', 'notes')


def canonical(value):
    return (model.canonical(value) + '\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def lua_string(literal):
    """Decode generated quoted Lua bytes without executing Lua."""
    inv.require(literal.startswith('"') and literal.endswith('"'), 'invalid Lua string')
    value, output, index = literal[1:-1], bytearray(), 0
    escapes = {'n': b'\n', 'r': b'\r', 't': b'\t', '"': b'"', "'": b"'", '\\': b'\\'}
    while index < len(value):
        if value[index] != '\\':
            output.extend(value[index].encode('utf-8'))
            index += 1
            continue
        index += 1
        inv.require(index < len(value), 'unfinished Lua escape')
        digits = re.match(r'[0-9]{1,3}', value[index:])
        if digits:
            number = int(digits[0])
            inv.require(number <= 255, 'invalid Lua byte')
            output.append(number)
            index += len(digits[0])
        else:
            inv.require(value[index] in escapes, 'unsupported Lua escape')
            output.extend(escapes[value[index]])
            index += 1
    return output.decode('utf-8')


class Inputs:
    """Exact local input reader; distinct historical hashes remain distinct."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.bindings = {}
        self.archived = {}

    def read(self, path, expected=None):
        local = inv.local_path(self.root, path)
        if local.is_file():
            raw = local.read_bytes()
        else:
            inv.require(path in HUMANS and expected, 'missing required input: ' + path)
            archive = inv.local_path(self.root, '.tmp/semantic/input/' + expected[:16] + '.md')
            if archive.exists():
                raw = archive.read_bytes()
                inv.require(digest(raw) == expected, 'archive collision')
            else:
                result = subprocess.run(['git', 'show', 'HEAD:' + path], cwd=self.root,
                                        capture_output=True, timeout=30, check=True)
                raw = result.stdout
                inv.require(digest(raw) == expected, 'historical input unavailable: ' + path)
                archive.parent.mkdir(parents=True, exist_ok=True)
                archive.write_bytes(raw)
            self.archived[path] = {'path': archive.relative_to(self.root).as_posix(),
                                   'sha256': expected, 'source': 'git HEAD:' + path}
        actual = digest(raw)
        inv.require(expected is None or actual == expected, 'input drift: ' + path)
        self.bindings[path] = {'path': path, 'sha256': actual}
        return raw

    def json(self, path, expected=None):
        return json.loads(self.read(path, expected))

    def bound(self, ref):
        return self.json(ref['path'], ref['sha256'])


def baseline(root):
    inputs = Inputs(root)
    manifests = {name: inputs.json(path) for name, path in READPOINTS.items()}
    # Supersedes describes a historical version at a reused path, not a live
    # dependency. Check the actual inheritance/readpoint edges independently.
    for manifest in manifests.values():
        for member in manifest['members']:
            inputs.read(member['path'], member['sha256'])
        for key in ('inherits', 'definition_readpoint', 'semantic_readpoint'):
            if key in manifest:
                inputs.bound(manifest[key])
        for ref in manifest.get('inputs', {}).values():
            inputs.bound(ref)
    contract = inputs.json(AUTH + 'layer3_investigation/contract.json')
    inherited = inputs.json(AUTH + 'layer3_successor/contract.json')
    semantic_data = inputs.bound(manifests['semantic']['corpus'])
    acquisition = inputs.bound(manifests['acquisition']['corpus'])
    expression = inputs.bound(manifests['expression']['data'])
    for payload in (contract, semantic_data, acquisition):
        for ref in payload.get('sources', []) + payload.get('source_bindings', []):
            inputs.read(ref['path'], ref['sha256'])
    target_ids = semantic_data['target_ids']
    inv.require(target_ids == sorted(set(target_ids)) and len(target_ids) == 2105,
                'baseline target identity')
    inv.require(target_ids == acquisition['target_ids'] == sorted(i['item_id'] for i in expression['items']),
                'baseline target mismatch')
    inv.require(len(semantic_data['results']) == 9982, 'baseline question identity')
    source_manifest = inputs.json(inv.DATA + 'dvf_3_3_input_manifest.json')
    structured = {}
    for name in ('facts', 'decisions'):
        ref = source_manifest[name]
        rows = [json.loads(line) for line in inputs.read(ref['path'], ref['sha256']).splitlines()]
        structured[name] = inv.exact_rows(rows)
        inv.require(sorted(structured[name]) == target_ids, 'predecessor target mismatch')
    pointer = inputs.read(POINTER).decode('utf-8-sig')
    generation = re.search(r'generation_id\s*=\s*"([^"]+)"', pointer)
    inv.require(generation is not None, 'unknown current product boundary')
    directory = 'Iris/media/lua/client/Iris/Data/IrisLayer3Generations/' + generation[1]
    descriptor = inputs.json(directory + '/generation_descriptor.json')
    inv.require(descriptor['generation_id'] == generation[1], 'generation mismatch')
    for ref in descriptor['canonical_inputs']:
        inputs.read(ref['path'], ref['raw_byte_sha256'])
    rendered_ref = next(r for r in descriptor['outputs'] if r['path'] == 'dvf_3_3_rendered.json')
    rendered = inputs.json(directory + '/' + rendered_ref['path'], rendered_ref['raw_byte_sha256'])
    return {'reader': inputs, 'manifests': manifests, 'contract': contract, 'inherited': inherited,
            'semantic': semantic_data, 'acquisition': acquisition, 'expression': expression,
            'structured': structured, 'rendered': rendered, 'generation': generation[1]}


def note_facts(base):
    """Source-confirmed independent viewing; no name-based admission or closure.

    The existing reading profile explicitly includes records. No definition
    revision is needed to express this function. Effects and whole question
    completion are separate investigations.
    """
    inputs = base['reader']
    from . import recovery_sources
    menu = inputs.read(semantic.MENU).decode('utf-8-sig')
    journal = inputs.read(JOURNAL).decode('utf-8-sig')
    required = ('testItem:getCategory() == "Literature" and testItem:canBeWrite()',
                'ContextMenu_Read_Note', 'ContextMenu_Write_Note', 'notebook:seePage(1)')
    inv.require(all(text in menu for text in required), 'note consumer changed')
    inv.require('notebook:getCustomPages():size()' in journal and 'notebook:seePage(i + 1)' in journal,
                'note page consumer changed')
    records = defaultdict(list)
    for ref in base['semantic']['source_bindings']:
        if ref['path'].startswith('scripts/'):
            for record in reader.declarations(inputs.read(ref['path'], ref['sha256']).decode('utf-8-sig'), ref['path']):
                if record['kind'] == 'item':
                    records[record['module'] + '.' + record['name']].append(record)
    builder = semantic.Builder({p: ref['sha256'] for p, ref in inputs.bindings.items()})
    consumer_refs = [builder.observe(semantic.MENU, 'L169-L170;L760-L770;L2097-L2116',
                                    {'selected_item': required[0], 'view_dispatch': required[1:],
                                     'editing_only': 'writing implement and other-user lock'}),
                     builder.observe(JOURNAL, 'L14-L360',
                                     {'page_loading': 'getCustomPages():size(); seePage(i + 1)',
                                      'viewing': 'defaultEntryText; newPage; editing flag is separate'})]
    for item in base['semantic']['target_ids']:
        rows = records.get(item, [])
        if len(rows) != 1:
            continue
        fields, conflicts = recovery_sources.stable_properties(rows[0])
        if not fields or fields.get('Type') != 'Literature' or fields.get('CanBeWrite', '').lower() != 'true':
            continue
        record = rows[0]
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{item}",
                              {'raw': record['raw'], 'clauses': record['clauses']})
        builder.fact(item, 'direct_function', {'function': 'view_written_note_pages'},
                     [ref, *consumer_refs], 'note_viewing', ['activity:reading', 'item:direct'])
        writing = next(f for f in base['semantic']['facts'] if f['item_id'] == item
                       and f['payload'] == {'function': 'record_written_notes'})
        builder.fact(item, 'constraint', {'predicate': NOTE_EDIT}, [ref, *consumer_refs],
                     'note_editing', ['activity:reading', 'item:direct'],
                     applies_to_fact_refs=[writing['fact_id']])
        saved = [builder.fact(item, 'effect', {'property': prop, 'direction': 'update'},
                              [ref, *consumer_refs], 'note_confirmation', ['activity:reading'])
                 for prop in ('written_note_pages', 'written_note_title')]
        builder.fact(item, 'condition', {'predicate': recovery_sources.NOTE_SAVE}, [ref, *consumer_refs],
                     'note_confirmation', ['activity:reading'], applies_to_fact_refs=saved)
        builder.fact(item, 'condition', {'predicate': NOTE_EDIT}, [ref, *consumer_refs],
                     'note_editing', ['activity:reading'], applies_to_fact_refs=saved)
        builder.fact(item, 'condition', {'predicate': recovery_sources.NOTE_LIMITS}, [ref, *consumer_refs],
                     'note_page_bounds', ['activity:reading'], applies_to_fact_refs=[writing['fact_id']])
        lock = builder.fact(item, 'effect', {'property': 'written_note_lock', 'direction': 'update'},
                            [ref, *consumer_refs], 'note_confirmation', ['activity:reading'])
        builder.fact(item, 'condition', {'predicate': recovery_sources.NOTE_LOCK}, [ref, *consumer_refs],
                     'note_confirmation', ['activity:reading'], applies_to_fact_refs=[lock])
        builder.fact(item, 'condition', {'predicate': recovery_sources.NOTE_ACCESS}, [ref, *consumer_refs],
                     'note_editing', ['activity:reading'], applies_to_fact_refs=[lock])
    return builder


def extend_question_instances(base, payload):
    """Merge source participation into the existing definition's question keys."""
    keys = {model.question_key(r): r for r in payload['results']}
    applications = {r['item_id']: r for r in payload['application_inputs']}
    instances = {}
    additions = [('crafting', 'B', item, links, base['participation_provenance'][item], 'source_recipe_operand')
                 for item, links in sorted(base.get('recovered_participation', {}).items())]
    additions.extend(('world_work', 'D', item, links, base['world_participation_provenance'][item], 'active_world_participation')
                     for item, links in sorted(base.get('recovered_world_participation', {}).items()))
    for profile_id, route_id, item, links, provenance_ref, instance_kind in additions:
        profile = next(p for p in base['contract']['profiles'] if p['profile_id'] == profile_id)
        scope = profile['routing']['scope']
        old_ref, previous = next((ref, a) for ref, a in base['semantic']['attempts'].items()
                                 if a['item_id'] == item and a['route'] == route_id)
        attempt = deepcopy(previous)
        merged = {model.canonical(p): p for p in [*attempt['finding'].get('participants', []), *links]}
        attempt['finding']['participants'] = [merged[k] for k in sorted(merged)]
        attempt['finding']['recovered_participation'] = deepcopy(links)
        if route_id == 'D':
            attempt['finding']['building_candidates'] = sorted(set(attempt['finding']['building_candidates']) |
                {p['observation_ref'] for p in links if p.get('source_instance_kind') == 'active_welding_participant'})
        attempt['finding']['previous_attempt_ref'] = old_ref
        evidence = sorted({r for p in links for r in p['evidence_refs']})
        attempt['observation_refs'] = sorted(set(attempt['observation_refs']) | set(evidence))
        attempt['unfinished_semantic_paths'] = sorted(set(attempt['unfinished_semantic_paths']) |
            {'Recovered source participation: role, declared requirements, called consumer and outcome.'})
        attempt['state'] = 'not_investigated'
        new_ref = model.identity('attempt', [item, route_id, attempt['observation_refs'], attempt['finding']])
        payload['attempts'][new_ref] = attempt
        application = applications[item]
        route = next(r for r in application['routes'] if r['profile_id'] == profile_id)
        old_route = deepcopy(route)
        route.update(state='confirmed_applicable', scope_refs=sorted(set(route['scope_refs']) | {scope}),
                     evidence_refs=sorted(set(route['evidence_refs']) | {new_ref}),
                     reason='Exact source participation opens this existing profile; semantic completion remains separate.')
        application['gap']['evidence_refs'] = sorted(set(application['gap']['evidence_refs']) | {new_ref})
        baseline_pending = [deepcopy(r) for r in base['semantic']['pending']
                            if r['item_id'] == item and r['profile_id'] == profile_id]
        for pending in payload['pending']:
            if pending['item_id'] == item and pending['profile_id'] == profile_id:
                pending.update(disposition='applicable', attempt_refs=sorted(set(pending['attempt_refs']) | {new_ref}))
        for axis in profile['required_axes']:
            if axis == 'acquisition':
                continue
            key = (item, axis, scope)
            lineage = {'baseline_absent': key not in keys, 'definition_readpoint': payload['definition_readpoint'],
                       'registry_revision': payload['registry_revision'], 'profile_id': profile_id,
                       'source_instance_kind': instance_kind,
                       'source_participants': deepcopy(links), 'previous_route': old_route,
                       'previous_pending': baseline_pending, 'previous_gap': deepcopy(
                           next(r['gap'] for r in base['semantic']['application_inputs'] if r['item_id'] == item)),
                       'finding_ref': new_ref, 'previous_attempt_ref': old_ref}
            instances[key] = lineage
            if key in keys:
                result = keys[key]
                result['attempt_refs'] = sorted(set(result['attempt_refs']) | {new_ref})
                result['provenance_refs'] = sorted(set(result['provenance_refs']) |
                                                  {provenance_ref})
                universe = next(r for r in payload['universe'] if tuple(r['question_key']) == key)
                universe['contributors'] = sorted(set(universe['contributors']) | {profile_id})
                universe['finding_refs'] = sorted(set(universe['finding_refs']) | {new_ref})
                continue
            result = {'item_id': item, 'axis_id': axis, 'scope_ref': scope, 'question_key': list(key),
                      'authority_ref': payload['authority_id'], 'registry_revision': payload['registry_revision'],
                      'state': 'not_investigated', 'attempt_refs': [new_ref],
                      'provenance_refs': [provenance_ref], 'fact_refs': [],
                      'question_coverage': 'partial', 'blockers': [attempt['dependency']],
                      'next_source_dependency': attempt['dependency'],
                      'not_investigated_reason': 'Recovered participation still needs local role and condition interpretation.',
                      'transition_reason': 'Same-definition source instance addition; no baseline question was replaced.'}
            payload['results'].append(result)
            keys[key] = result
            payload['universe'].append({'question_key': list(key), 'relation': 'newly_required',
                'before_revision': payload['registry_revision'], 'after_revision': payload['registry_revision'],
                'before_readpoint': payload['definition_readpoint'], 'after_authority': payload['authority_id'],
                'contributors': [profile_id], 'finding_refs': [new_ref]})
    payload['results'].sort(key=model.question_key)
    payload['universe'].sort(key=lambda r: tuple(r['question_key']))
    return instances


def semantic_candidate(base, found):
    """Apply admitted note facts while retaining unresolved, unreviewed work.

    The audit distinguishes pending reassessment from investigated uncertainty.
    A candidate with pending rows cannot be adopted or handed to B/C.
    """
    payload = deepcopy(base['semantic'])
    inv.require(payload['status'] == 'candidate', 'unexpected historical corpus lifecycle')
    aid = 'iris-layer3-semantic-results-recovery-1'
    payload['authority_id'] = aid
    instances = extend_question_instances(base, payload)
    new_items = {f['item_id'] for f in found.facts.values() if f['payload'] == {'function': 'view_written_note_pages'}}
    corrected = {}
    correction_reasons = {}
    withdrawn = {f['fact_id'] for f in payload['facts'] if f['item_id'] in base.get('unsupported_wear', {})
                 and f['payload'] == {'function': 'wear_on_body'}}
    withdrawn.update(f['fact_id'] for f in payload['facts'] if withdrawn.intersection(f.get('applies_to_fact_refs', [])))
    inv.require(not any(withdrawn.intersection(f.get('applies_to_fact_refs', [])) for f in found.facts.values()),
                'recovered fact still depends on withdrawn wear capability')
    withdrawals = [{'old_fact_ref': f['fact_id'], 'new_fact_ref': None, 'kind': 'withdrawal',
                    'reason': base['unsupported_wear'][f['item_id']]['reason'],
                    'source_refs': base['unsupported_wear'][f['item_id']]['source_refs']}
                   for f in payload['facts'] if f['fact_id'] in withdrawn]
    for fact in payload['facts']:
        if fact['item_id'] in new_items and fact['fact_kind'] == 'constraint':
            replacement = next(f for f in found.facts.values()
                               if f['item_id'] == fact['item_id'] and f['fact_kind'] == 'constraint')
            corrected[fact['fact_id']] = replacement['fact_id']
            correction_reasons[fact['fact_id']] = 'Own journal lock also disables editing until unlocked; read-only page viewing needs no pen.'
        elif fact['payload'] == {'predicate': 'Food is in inventory; any required companion item is present; satiety permits starting the eating action.'}:
            replacement = next(f for f in found.facts.values() if f['item_id'] == fact['item_id']
                               and f['admission']['rule_ref'] == 'native_food_conditions'
                               and f['applies_to_fact_refs'] == fact['applies_to_fact_refs'])
            corrected[fact['fact_id']] = replacement['fact_id']
            correction_reasons[fact['fact_id']] = 'Starting consumption permits low satiety OR calories below 1000; the former qualifier omitted the calorie alternative.'
    retained_facts = {f['fact_id']: f for f in payload['facts'] if f['fact_id'] not in corrected and f['fact_id'] not in withdrawn}
    payload['source_bindings'] = sorted({r['path']: r for r in
        [*payload['source_bindings'], *(base['reader'].bindings[o['source_path']] for o in found.observations.values())]}.values(), key=lambda r: r['path'])
    payload['observations'].update(found.observations)
    payload['provenance'].update(found.provenance)
    for rule, positive, limit in (
        ('note_viewing', 'Unique Literature/CanBeWrite declaration; selected writable-note branch opens stored pages in ISUIWriteJournal.',
         'Does not assert learning, mood changes, or engine persistence correctness.'),
        ('note_editing', 'Writing implement/ownership dispatch and journal initialise lock controls are separate from read-only page display.',
         'Owned locks must be unlocked before editing. Does not infer administrator write access from the constructor alone.'),
    ):
        payload['rules'][rule] = {'review_state': 'reviewed', 'revision': '1', 'positive': positive,
                                 'scope': 'native writable literature', 'exclusions': limit,
                                 'source_refs': [semantic.MENU, JOURNAL]}
    from . import recovery_sources
    for rule, review in recovery_sources.RULES.items():
        payload['rules'][rule] = {'review_state': 'reviewed', 'revision': '1', **review}
    # A recipe can rediscover the identical item/context/role proposition.
    # Semantic identity excludes provenance: retain that ID, dependencies and
    # prior evidence rather than minting a narrower context to avoid a collision.
    # The existing model requires a single admission rule per fact. Its successor
    # review admits the extra exact-identity evidence; provenance records retain
    # the contributing rule and original occurrence, without rewriting history.
    for fid, discovered in found.facts.items():
        previous = retained_facts.get(fid)
        merged = deepcopy(previous or discovered)
        inv.require(model.fact_identity(merged) == model.fact_identity(discovered) == fid,
                    'same-ID discovery changed semantic meaning')
        canonical_rule = merged['admission']['rule_ref']
        all_refs = set(merged['provenance_refs']) | set(discovered['provenance_refs'])
        joined_refs = []
        additions = []
        for pref in sorted(all_refs):
            provenance = payload['provenance'][pref]
            contributor = provenance['rule_ref']
            inv.require(payload['rules'][contributor].get('review_state') == 'reviewed',
                        'unreviewed same-meaning evidence contributor')
            if contributor != canonical_rule:
                rebound = {**deepcopy(provenance), 'rule_ref': canonical_rule,
                           'contributor_rule_ref': contributor, 'contributor_provenance_ref': pref}
                rebound_ref = model.identity('prov', rebound)
                payload['provenance'][rebound_ref] = rebound
                joined_refs.append(rebound_ref)
                additions.append({'provenance_ref': rebound_ref, 'source_occurrence_ref': pref,
                                  'contributor_rule_ref': contributor})
                review = payload['rules'][canonical_rule]
                contributors = review.setdefault('same_meaning_evidence_contributors', {})
                contributors[contributor] = deepcopy(payload['rules'][contributor])
                review['evidence_extension_scope'] = ('Additional reviewed source occurrences for an identical semantic fact only. '
                    'This does not alter its item, context, payload, qualifiers or dependency identity; source-specific conditions remain separate facts.')
            else:
                joined_refs.append(pref)
        merged['provenance_refs'] = sorted(set(joined_refs))
        if previous or additions:
            merged['evidence_additions'] = {'kind': 'same_meaning_evidence', 'previous_fact_ref': fid if previous else None,
                'contributions': additions, 'new_question_scopes': sorted(found.fact_scopes[fid])}
        retained_facts[fid] = merged
        # The audit and question-contribution pass see the same merged fact.
        found.facts[fid] = deepcopy(merged)
    payload['facts'] = [retained_facts[fid] for fid in sorted(retained_facts)]
    payload['fact_question_bindings'] = [b for b in payload['fact_question_bindings'] if b['fact_ref'] not in withdrawn]
    for binding in payload['fact_question_bindings']:
        binding['authority_ref'] = aid
        binding['fact_ref'] = corrected.get(binding['fact_ref'], binding['fact_ref'])
    existing_bindings = {(tuple(b['question_key']), b['fact_ref']) for b in payload['fact_question_bindings']}
    existing_keys = {model.question_key(r) for r in payload['results']}
    for fact in found.facts.values():
        for scope in sorted(found.fact_scopes[fact['fact_id']]):
            applicable = [(fact['item_id'], axis['axis_id'], scope) for axis in base['contract']['axes']
                          if fact['fact_kind'] in axis['allowed_result_kinds']
                          and (fact['item_id'], axis['axis_id'], scope) in existing_keys]
            inv.require(applicable, f"new fact needs bounded question definition admission: {fact['item_id']} {scope} {fact['fact_kind']} {fact['payload']}")
            for key in applicable:
                if (key, fact['fact_id']) not in existing_bindings:
                    payload['fact_question_bindings'].append({
                        'question_key': list(key), 'fact_ref': fact['fact_id'],
                        'authority_ref': aid, 'registry_revision': payload['registry_revision'], 'contribution': 'partial'})
                    existing_bindings.add((key, fact['fact_id']))
    for row in payload['universe']:
        row['after_authority'] = aid
    by_question = defaultdict(list)
    for binding in payload['fact_question_bindings']:
        by_question[tuple(binding['question_key'])].append(binding)
    audit = []
    previous_results = {model.question_key(r): r for r in base['semantic']['results']}
    for result in payload['results']:
        key = model.question_key(result)
        previous = previous_results.get(key)
        result['authority_ref'] = aid
        row = {'question_key': list(key), 'previous_result': deepcopy(previous),
               'attribution_status': 'not_reassessed', 'attribution_rule_ref': None,
               'accepted_partial_fact_refs': sorted(b['fact_ref'] for b in by_question[key]),
               'direct_evidence_refs': [], 'answered_scope': [], 'remaining_scope': [],
               'effective_blocker_refs': None,
               'remaining_work': 'Question-local source/axis adjudication not yet performed; historical state is not new evidence.'}
        if key in instances:
            row['instance_recovery'] = instances[key]
        if key[0] in new_items and key[2] == 'activity:reading':
            refs = sorted(p for p, v in found.provenance.items() if v['item_id'] == key[0])
            result['provenance_refs'] = refs
            row.update(attribution_status='attributed', attribution_rule_ref='native_note/' + key[1],
                       direct_evidence_refs=refs, remaining_work=None)
            if key[1] in {'operation', 'effects', 'conditions'}:
                fact_refs = sorted(b['fact_ref'] for b in by_question[key])
                answered = {
                    'operation': ['view stored pages', 'record or erase page content', 'rename', 'set or remove editing lock'],
                    'effects': ['OK writes page content and title to the item', 'lock controls immediately change ownership lock'],
                    'conditions': ['editing pen and ownership permission', 'own lock must be unlocked to edit',
                                   'page and entry limits', 'OK versus cancel for content/title', 'immediate lock changes'],
                }[key[1]]
                reason = ('The selected writable Literature branch owns this reading scope and bypasses ReadABook. '
                          'Journal initialise/onClick and onWriteSomethingClick establish: ' + '; '.join(answered) +
                          '. Source-defined item behavior is closed by explicit getters/setters and branch conditions; '
                          'controller UI integration remains outside offline runtime validation, not an invented item predicate.')
                result.update(state='resolved', fact_refs=fact_refs, question_coverage='whole_scope',
                              coverage_justification=reason, blockers=[], next_source_dependency=None,
                              transition_reason=reason)
                for binding in by_question[key]:
                    binding['contribution'] = 'whole_scope'
                row.update(answered_scope=answered,
                           remaining_scope=[], effective_blocker_refs=[])
        row['successor_result'] = deepcopy(result)
        audit.append(row)
    payload['fact_question_bindings'].sort(key=model.canonical)
    return payload, audit, [{'old_fact_ref': old, 'new_fact_ref': new,
                            'reason': correction_reasons[old]}
                           for old, new in sorted(corrected.items())] + withdrawals


def predecessor_inventory(base):
    """Observe every supplied field/surface without pretending to segment it.

    Pending prose is an explicit unfinished obligation. It is never classified
    as a grammatical connector or admitted as source-confirmed fact.
    """
    inputs = base['reader']
    english = {}
    index_path = 'Iris/media/lua/client/Iris/Data/Layer3English/Index.lua'
    index = inputs.read(index_path).decode('utf-8-sig')
    for module in re.findall(r'module\s*=\s*"([^"]+)"', index):
        text = inputs.read('Iris/media/lua/client/' + module + '.lua').decode('utf-8-sig')
        for match in re.finditer(r'\["([^"\n]+)"\]\s*=\s*("(?:\\.|[^"\\])*")', text):
            inv.require(match[1] not in english, 'duplicate English FullType')
            english[match[1]] = lua_string(match[2])
    previous = base['rendered']['entries']
    targets = base['semantic']['target_ids']
    inv.require(sorted(previous) == targets, 'rendered target mismatch')
    inv.require(not (set(english) - set(targets)), 'English target mismatch')
    rows, claims, clauses = [], [], []
    current = {r['item_id']: r for r in base['expression']['items']}
    for item in targets:
        texts = {'ko': previous[item].get('text_ko') or '', 'en': english.get(item) or ''}
        row_claims = []
        for field in CLAIM_FIELDS:
            value = base['structured']['facts'][item].get(field)
            if value is None or value == '':
                continue
            ref = model.identity('claim', [base['reader'].bindings[inv.DATA + 'dvf_3_3_facts.jsonl'], item, field, value])
            row_claims.append(ref)
            claims.append({'item_id': item, 'predecessor_claim_id': ref,
                           'predecessor_field_or_surface': field,
                           'predecessor_text_ref': {'path': inv.DATA + 'dvf_3_3_facts.jsonl', 'item_id': item, 'field': field, 'text': value},
                           'predecessor_source_leads': base['structured']['facts'][item].get('fact_origin', {}).get(field, []),
                           'candidate_successor_fact_refs': [], 'verified_source_refs': [],
                           'migration_disposition': 'pending_investigation',
                           'reason': 'Observed predecessor field; semantic decomposition and source/consumer assessment remain unfinished.',
                           'remaining_uncertainty': None, 'remaining_work': 'decompose and adjudicate',
                           'source_binding': 'predecessor_only', 'source_strength': 'not_admitted',
                           'owner_adoption_evidence': base['structured']['decisions'][item]['state'],
                           'review_state': 'pending', 'owner_presence_evidence': None})
        transitions = {}
        for locale, text in texts.items():
            # One exact surface obligation initially; sentence splitting alone
            # cannot certify independent semantic clause coverage.
            if text:
                clauses.append({'item_id': item, 'locale': locale, 'span': [0, len(text)],
                                'text': text, 'classification': 'unsegmented', 'claim_ids': [],
                                'classification_rule_ref': None})
            after = bool(current[item]['locales'][locale]['expanded'])
            transitions[locale] = ('nonempty' if text.strip() else 'blank') + '->' + ('nonempty' if after else 'blank')
        rows.append({'item_id': item, 'claim_ids': row_claims, 'predecessor_text': texts,
                     'baseline_transition': transitions, 'nonempty_internal_delta': 'not_adjudicated'})
    return {'items': rows, 'claims': claims, 'clauses': clauses,
            'locale_binding': 'Observed repository generation KO and English lookup; independent semantic locale parity remains unfinished.',
            'completion': 'partial'}


def completion(audit, inventory):
    return (all(r['attribution_status'] in {'attributed', 'attribution_failure'} for r in audit)
            and not any(r.get('remaining_work') for r in audit)
            and all(c['classification'] != 'unsegmented' for c in inventory['clauses'])
            and all(c['migration_disposition'] != 'pending_investigation' for c in inventory['claims'])
            and {c['predecessor_claim_id'] for c in inventory['conservation']}
                == {c['predecessor_claim_id'] for c in inventory['claims']}
            and all(c['conservation_status'] in {'conserved', 'responsibility_removed', 'bounded_unresolved'}
                    for c in inventory['conservation']))


def require_ready(report):
    """Incomplete investigations cannot become a consumable successor."""
    pending_questions = sum(r.get('attribution_status') not in {'attributed', 'attribution_failure'}
                            for r in report['question_reassessment'])
    pending_clauses = sum(c.get('classification') == 'unsegmented' for c in report['inventory']['clauses'])
    pending_claims = sum(c.get('migration_disposition') == 'pending_investigation'
                         for c in report['inventory']['claims'])
    unfinished_questions = sum(bool(r.get('remaining_work')) for r in report['question_reassessment'])
    inv.require(not (pending_questions or pending_clauses or pending_claims or unfinished_questions),
                f'recovery incomplete: {pending_questions} questions, {pending_clauses} unsegmented surfaces, '
                f'{pending_claims} claims pending investigation, {unfinished_questions} questions with unfinished local work')
    inv.require(report.get('completion') == 'complete' and completion(report['question_reassessment'], report['inventory']),
                'complete question adjudication and claim conservation required')


def installed_identity(root):
    path = Path(__file__).resolve()
    expected = (root / 'Iris/tooling/.venv/Lib/site-packages').resolve()
    inv.require(path.is_relative_to(expected), 'installed package required')
    inv.require(digest(path.read_bytes()) == inv.sha(root / CODE / 'recovery.py'), 'stale recovery installation')
    inv.require(sys.flags.isolated and sys.flags.dont_write_bytecode, 'isolated Python without bytecode required')


def acquisition_content(payload):
    """Acquisition meaning is invariant under a dependency-only successor."""
    content = deepcopy(payload)
    for key in ('authority_id', 'semantic_readpoint', 'binding_change'):
        content.pop(key, None)
    for row in [*content['results'], *content['fact_question_bindings']]:
        row['authority_ref'] = 'self'
    return content


def acquisition_successor(base, semantic_ref):
    payload = deepcopy(base['acquisition'])
    aid = 'iris-layer3-acquisition-results-recovery-1'
    payload['authority_id'] = aid
    payload['semantic_readpoint'] = semantic_ref
    for row in [*payload['results'], *payload['fact_question_bindings']]:
        row['authority_ref'] = aid
    content_hash = digest(canonical(acquisition_content(base['acquisition'])))
    inv.require(digest(canonical(acquisition_content(payload))) == content_hash, 'acquisition content drift')
    payload['binding_change'] = {
        'kind': 'dependency_only', 'predecessor': base['reader'].bindings[READPOINTS['acquisition']],
        'old_semantic': base['acquisition']['semantic_readpoint'], 'new_semantic': semantic_ref,
        'previous_content_sha256': content_hash, 'content_sha256': content_hash,
        'content_delta': 'none', 'dependency_binding_delta': 'semantic readpoint and self authority references',
    }
    return payload


def load_candidate(root, manifest_ref, *, consumable=True, baseline_inputs=None):
    """Load one exact candidate chain; partial output is audit-only.

    This is the successor's normal input boundary. It does not grant acceptance
    or adopt a current route, and is not an additional validation authority.
    """
    base = baseline_inputs if baseline_inputs is not None else baseline(root)
    reader = base['reader']
    manifest = reader.json(manifest_ref['path'], manifest_ref['sha256'])
    inv.require(manifest.get('schema') == 'iris-layer3-recovery-chain-v1'
                and manifest.get('status') == 'candidate', 'mixed candidate/adopted chain')
    members = manifest['members']
    inv.require(set(members) == {'semantic', 'acquisition', 'expression', 'audit'}, 'incomplete candidate chain')
    payloads = {name: reader.json(ref['path'], ref['sha256']) for name, ref in members.items()}
    return consume_candidate(base, manifest, payloads, consumable=consumable)


def consume_candidate(base, manifest, payloads, *, consumable=True):
    """Consume already byte-bound members through the normal domain checks."""
    reader = base['reader']
    members = manifest['members']
    semantic, acquisition, expression, audit = (payloads[k] for k in ('semantic', 'acquisition', 'expression', 'audit'))
    inv.require(semantic['status'] == acquisition['status'] == 'candidate', 'mixed candidate/adopted payload')
    inv.require(acquisition['semantic_readpoint'] == members['semantic']
                and expression['inputs']['semantic'] == members['semantic']
                and expression['inputs']['acquisition'] == members['acquisition'], 'incoherent candidate chain')
    inv.require(expression['inputs']['definition'] == manifest['definition']
                and expression['inputs']['successor'] == manifest['successor'], 'predecessor or stale expression envelope')
    inv.require(semantic['target_ids'] == acquisition['target_ids'] == [r['item_id'] for r in expression['items']],
                'case-sensitive target mismatch')
    change = acquisition['binding_change']
    inv.require(change['kind'] == 'dependency_only' and change['new_semantic'] == members['semantic']
                and change['content_sha256'] == change['previous_content_sha256']
                == digest(canonical(acquisition_content(acquisition))), 'acquisition binding-only content drift')
    # Reuse the already pinned predecessor bytes for semantic content equality;
    # a caller cannot merely rewrite the two advertised digests together.
    prior_manifest = reader.json(change['predecessor']['path'], change['predecessor']['sha256'])
    prior_ref = prior_manifest['corpus']
    prior = reader.json(prior_ref['path'], prior_ref['sha256'])
    inv.require(acquisition_content(prior) == acquisition_content(acquisition), 'acquisition predecessor content drift')
    inv.require(change['old_semantic'] == prior['semantic_readpoint'], 'stale acquisition predecessor dependency')
    for ref in audit['inputs']:
        reader.read(ref['path'], ref['sha256'])
    definition = reader.bound(manifest['definition'])
    contract_ref = next(r for r in definition['members'] if r['path'] == AUTH + 'layer3_investigation/contract.json')
    contract = reader.bound(contract_ref)
    model.validate_payload(semantic, contract)
    from . import acquisition_results
    acquisition_results.validate_payload(acquisition, contract)
    inv.require(semantic['definition_readpoint'] == acquisition['definition_readpoint'] == manifest['definition'],
                'definition dependency drift')
    result_rows = {model.question_key(r): r for r in semantic['results']}
    attribution = {tuple(r['question_key']): r for r in audit['question_reassessment']}
    inv.require(len(attribution) == len(audit['question_reassessment']) and attribution.keys() == result_rows.keys(),
                'missing or duplicate question attribution')
    baseline_results = {model.question_key(r): r for r in base['semantic']['results']}
    inv.require(baseline_results.keys() <= result_rows.keys(), 'lost baseline recovery question')
    for key, row in attribution.items():
        inv.require(row['previous_result'] == baseline_results.get(key), 'changed baseline question attribution')
        if key not in baseline_results:
            lineage = row.get('instance_recovery', {})
            inv.require(lineage.get('baseline_absent') is True
                        and lineage.get('definition_readpoint') == semantic['definition_readpoint']
                        and lineage.get('registry_revision') == semantic['registry_revision']
                        and (lineage.get('profile_id'), key[2]) in {('crafting', 'activity:crafting'), ('world_work', 'activity:world_work')}
                        and lineage.get('source_participants') and lineage.get('previous_route')
                        and lineage.get('previous_gap') and lineage.get('finding_ref') in semantic['attempts'],
                        'unbound same-definition question instance')
            attempt = semantic['attempts'][lineage['finding_ref']]
            profile_id = lineage['profile_id']
            inv.require(attempt['item_id'] == key[0] and attempt['route'] == ('B' if profile_id == 'crafting' else 'D')
                        and lineage['source_participants'] == attempt['finding'].get('recovered_participation')
                        and all(p['item_id'] == key[0]
                                and p.get('evidence_refs')
                                and set(p['evidence_refs']) <= semantic['observations'].keys()
                                for p in lineage['source_participants']), 'invalid source instance contribution')
            if profile_id == 'crafting':
                inv.require(lineage.get('source_instance_kind') == 'source_recipe_operand'
                            and all(p.get('numeric_suffix', {}).get('separator') in {';', '='}
                                    or (p.get('import_resolution', {}).get('resolved_item') == key[0]
                                        and p['import_resolution'].get('headers')
                                        and p['import_resolution'].get('explicit_imports'))
                                    or (p.get('group') and p.get('stable_group_resolution', {}).get('repeated_fields')
                                        and p['stable_group_resolution'].get('declaration_path')
                                        and (p['stable_group_resolution'].get('membership_tags')
                                             or p['stable_group_resolution'].get('membership_short_type') == key[0].split('.', 1)[1]))
                                    for p in lineage['source_participants']),
                            'invalid recovered recipe operand')
            else:
                inv.require(lineage.get('source_instance_kind') == 'active_world_participation'
                            and all(p.get('role') in {'material', 'tool'} and p.get('count', 0) > 0
                                    and (p.get('previous_observation_ref') in attempt['finding']['building_candidates']
                                         or (p.get('source_instance_kind') == 'active_welding_participant'
                                             and p['observation_ref'] in attempt['finding']['building_candidates']
                                             and p.get('operand') in {'need', 'use', 'equipment'}))
                                    and any(f['fact_id'] == p.get('role_fact_ref') and f['item_id'] == key[0]
                                            and f['fact_kind'] == 'context_role' and f['payload'] == {'role': p['role']}
                                            for f in semantic['facts'])
                                    and semantic['observations'][p['observation_ref']]['content'].get('required_item') == key[0]
                                    and semantic['observations'][p['observation_ref']]['content'].get('factory') == p.get('factory')
                                    for p in lineage['source_participants']), 'invalid recovered building material')
    for key, row in attribution.items():
        inv.require(row['successor_result'] == result_rows[key] and row.get('attribution_rule_ref')
                    and row.get('direct_evidence_refs'), 'unbound question attribution')
        inv.require(set(row['direct_evidence_refs']) <= (semantic['observations'].keys() | semantic['provenance'].keys()),
                    'missing question source')
        inv.require(row['attribution_status'] in {'attributed', 'attribution_failure'}, 'unassessed question')
        if row['attribution_status'] == 'attribution_failure':
            inputs = row.get('applied_inputs', {})
            inv.require('declarations' in inputs and (len(inputs['declarations']) != 1 or inputs.get('field_conflicts')),
                        'generic attribution failure without exact identity conflict')
        if result_rows[key].get('question_coverage') == 'whole_scope':
            inv.require(not row['remaining_scope'] and not row.get('remaining_work'), 'terminal question retains residual')
        else:
            inv.require(row['remaining_scope'] and all(r.get('meaning') and r.get('required_input') and r.get('reason')
                                                     for r in row['remaining_scope']), 'missing question-local residual')
            expected_blockers = [model.identity('residual', [list(key), r]) for r in row['remaining_scope']]
            inv.require(result_rows[key]['blockers'] == expected_blockers
                        and [r['ref'] for r in row['effective_blocker_refs']] == expected_blockers
                        and all(r['remaining_scope'] in row['remaining_scope']
                                and r['evidence_refs'] == row['direct_evidence_refs'] for r in row['effective_blocker_refs']),
                        'route blocker copied without question-local attribution')
    qualified = {f['ref']: f for f in expression['facts']}
    inv.require(len(qualified) == len(expression['facts']), 'duplicate expression fact')
    expected = {p['authority_id'] + '/' + f['fact_id']: f for p in (semantic, acquisition) for f in p['facts']}
    inv.require(qualified.keys() == expected.keys(), 'expression fact omission')
    for ref, fact in qualified.items():
        original = expected[ref]
        inv.require(fact['item_id'] == original['item_id'] and fact['payload'] == original['payload'], 'prose-only or altered expression fact')
    old_facts = {f['fact_id']: f for f in base['semantic']['facts']}
    new_facts = {f['fact_id']: f for f in semantic['facts']}
    withdrawn_inputs = {}
    for correction in audit['corrections']:
        old, new = correction['old_fact_ref'], correction['new_fact_ref']
        if correction.get('kind') == 'withdrawal':
            inv.require(old in old_facts and old not in new_facts and new is None
                        and correction.get('source_refs') and correction.get('reason'), 'broken withdrawal reference')
            item = old_facts[old]['item_id']
            if item not in withdrawn_inputs:
                from . import source_reader
                from . import recovery_sources
                refs = {r['path']: r for r in correction['source_refs']}
                inv.require(recovery_sources.BODY_LOCATIONS in refs and 'lua/client/TimedActions/ISWearClothing.lua' in refs,
                            'missing withdrawal consumer evidence')
                for ref in refs.values():
                    reader.read(ref['path'], ref['sha256'])
                records = [r for path, ref in refs.items() if path.startswith('scripts/')
                           for r in source_reader.declarations(reader.read(path, ref['sha256']).decode('utf-8-sig'), path)
                           if r['kind'] == 'item' and r['module'] + '.' + r['name'] == item]
                inv.require(len(records) == 1, 'ambiguous withdrawal declaration')
                fields, _ = recovery_sources.stable_properties(records[0])
                registry_ref = refs[recovery_sources.BODY_LOCATIONS]
                registry = reader.read(registry_ref['path'], registry_ref['sha256']).decode('utf-8-sig')
                locations = set(re.findall(r'^group:getOrCreateLocation\("([^"]+)"\)', registry, re.M))
                inv.require(fields.get('Type') == 'Clothing' and fields.get('OBSOLETE', '').lower() == 'true'
                            and fields.get('BodyLocation') and fields['BodyLocation'] not in locations,
                            'unsupported withdrawal reason')
                withdrawn_inputs[item] = fields
            inv.require(old_facts[old]['payload'] == {'function': 'wear_on_body'} or
                        (old_facts[old]['fact_kind'] in {'condition', 'constraint'} and all(
                            old_facts[r]['payload'] == {'function': 'wear_on_body'} for r in old_facts[old]['applies_to_fact_refs'])),
                        'withdrawal outside admitted wear defect')
            continue
        inv.require(old in old_facts and old not in new_facts and new in new_facts
                    and old_facts[old]['item_id'] == new_facts[new]['item_id']
                    and correction.get('reason'), 'broken correction reference')
    expressions = {e['expression_id']: e for e in expression['expressions']}
    inv.require(len(expressions) == len(expression['expressions']), 'duplicate expression identity')
    for item in expression['items']:
        inv.require(set(item['locales']) == {'ko', 'en'}, 'missing expression locale')
        expected_refs = {r for r, f in qualified.items() if f['item_id'] == item['item_id']}
        for locale in ('ko', 'en'):
            output = item['locales'][locale]
            inv.require(set(output['expanded_represented_fact_refs']) == expected_refs, 'expression fact omission')
            block_refs = {r for b in output['expanded'] for r in b['represented_fact_refs']}
            inv.require(block_refs == expected_refs, 'suppressed locale expanded expression')
            for block in output['expanded']:
                ids = block['expression_refs']
                inv.require(ids and all(e in expressions and expressions[e]['locale'] == locale
                                        and expressions[e]['resolution'] == 'expanded' for e in ids)
                            and block['text'] == ' '.join(expressions[e]['text'] for e in ids)
                            and set(block['represented_fact_refs']) == {r for e in ids for r in expressions[e]['represented_fact_refs']},
                            'expanded block/reference drift')
            for ref in expected_refs:
                ids = output['fact_expressions'].get(ref, [])
                inv.require(ids and all(e in expressions and expressions[e]['locale'] == locale
                                        and expressions[e]['text'] and ref in expressions[e]['represented_fact_refs'] for e in ids),
                            'missing fact-locale expression')
            compact = set(output['s2']['represented_fact_refs'])
            compact_ids = output['s2']['expression_refs']
            inv.require(all(e in expressions and expressions[e]['locale'] == locale
                            and expressions[e]['resolution'] == 'compact' for e in compact_ids)
                        and output['s2']['text'] == ' '.join(expressions[e]['text'] for e in compact_ids)
                        and compact == {r for e in compact_ids for r in expressions[e]['represented_fact_refs']},
                        'compact expression/reference drift')
            inv.require(compact <= expected_refs and set(output['tooltip_detail_omission_refs']) == expected_refs - compact,
                        'unaccounted compact omission')
    inv.require(manifest['focused_test'] in audit['inputs'], 'unbound focused acceptance source')
    inv.require(manifest['completion'] == audit['completion'] == expression['completion'], 'mixed completion state')
    from . import recovery_migration
    old_inventory = predecessor_inventory(base)
    originals = {r['item_id']: r['predecessor_text'] for r in old_inventory['items']}
    inventory = audit['inventory']
    inv.require([r['item_id'] for r in inventory['items']] == semantic['target_ids'], 'missing migration item')
    claims = {c['predecessor_claim_id']: c for c in inventory['claims']}
    inv.require(len(claims) == len(inventory['claims']), 'duplicate migration claim')
    for claim in claims.values():
        item, field, locator = claim['item_id'], claim['predecessor_field_or_surface'], claim['predecessor_text_ref']
        original = originals[item][field] if field in {'ko', 'en'} else base['structured']['facts'][item].get(field)
        inv.require(locator['text'] == original and claim.get('reason')
                    and claim.get('migration_disposition') in {'pending_investigation', 'already_represented', 'recovered',
                                                              'corrected', 'responsibility_removed', 'unresolved'},
                    'missing disposition or altered predecessor claim')
        start, end = locator['span']
        inv.require(0 <= start < end <= len(original), 'invalid predecessor span')
        meaning = recovery_migration.interpret(original[start:end], field)
        inv.require((claim['meaning'] is None and meaning is None) or
                    (meaning is not None and tuple(claim['meaning']) in meaning), 'unbound predecessor meaning')
    spans = defaultdict(list)
    for clause in inventory['clauses']:
        item, locale = clause['item_id'], clause['locale']
        start, end = clause['span']
        original = originals[item][locale]
        inv.require(0 <= start < end <= len(original) and clause['text'] == original[start:end], 'altered locale clause')
        spans[item, locale].append((start, end))
        meanings = recovery_migration.interpret(clause['text'])
        if clause['classification'] == 'non_semantic':
            inv.require(meanings == [] and clause['classification_rule_ref'] == 'whitespace_punctuation/1'
                        and clause['classification_reason'] == 'Exact whitespace/sentence punctuation contains no proposition.'
                        and not clause['claim_ids'], 'unsupported non-semantic clause classification')
        elif clause['classification'] == 'claim_ids':
            inv.require(meanings and clause['classification_rule_ref'] == 'predecessor_clauses/1'
                        and clause['claim_ids'] and set(clause['claim_ids']) <= claims.keys(), 'missing clause classification rule')
            inv.require({tuple(claims[r]['meaning']) for r in clause['claim_ids']} == set(meanings)
                        and all(claims[r]['item_id'] == item for r in clause['claim_ids']), 'missing independent clause meaning')
        else:
            inv.require(clause['classification'] == 'unsegmented' and meanings is None, 'invalid unsegmented clause')
    for item, locales in originals.items():
        for locale, text in locales.items():
            position = 0
            for start, end in sorted(spans[item, locale]):
                inv.require(start == position, 'locale clause coverage gap or overlap')
                position = end
            inv.require(position == len(text), 'locale clause coverage gap')
    conservation = {r['predecessor_claim_id']: r for r in inventory['conservation']}
    inv.require(len(conservation) == len(inventory['conservation']) and conservation.keys() <= claims.keys(),
                'duplicate or orphan conservation row')
    output_items = {r['item_id']: r for r in expression['items']}
    for claim_ref, row in conservation.items():
        claim = claims[claim_ref]
        inv.require(row['migration_disposition'] == claim['migration_disposition'], 'conservation disposition mismatch')
        if row['conservation_status'] == 'conserved':
            refs = set(row['successor_fact_refs'])
            inv.require(refs and refs == set(claim['candidate_successor_fact_refs']) and refs <= qualified.keys()
                        and set(row['locales']) == {'ko', 'en'}, 'missing conserved fact or locale')
            for locale, relation in row['locales'].items():
                output = output_items[claim['item_id']]['locales'][locale]
                inv.require(all(qualified[r]['item_id'] == claim['item_id'] for r in refs)
                            and refs <= set(output['expanded_represented_fact_refs'])
                            and relation['expanded_outcome'] == 'represented'
                            and set(relation['expanded_refs']) == {e for r in refs for e in output['fact_expressions'][r]},
                            'claim expression conservation failure')
                compact = refs & set(output['s2']['represented_fact_refs'])
                inv.require(set(relation['compact_fact_refs']) == compact
                            and set(relation['compact_omitted_fact_refs']) == refs - compact
                            and (compact == refs or relation.get('compact_omission_reason')),
                            'unjustified compact omission')
        elif row['conservation_status'] == 'bounded_unresolved':
            inv.require(claim['migration_disposition'] == 'unresolved' and claim.get('verified_source_refs')
                        and claim.get('remaining_uncertainty') == row['residual'] and not claim.get('remaining_work'),
                        'unbounded unresolved claim')
        elif row['conservation_status'] == 'responsibility_removed':
            inv.require(claim['migration_disposition'] == 'responsibility_removed'
                        and claim.get('owner_presence_evidence') and claim.get('verified_source_refs')
                        and row.get('removal_reason') == claim['reason'], 'unsupported responsibility removal')
        else:
            inv.require(not consumable and row['conservation_status'] == 'expression_failure', 'expression conservation failure')
    if consumable:
        require_ready(audit)
    # One required reconstruction: the consumer rejects altered wording,
    # reference scopes or applications, using the actual pinned producer.
    from . import recovery_expression
    rebuilt, applications = recovery_expression.prepare({**base, 'acquisition': acquisition}, semantic, expression['inputs'])
    rebuilt['completion'] = 'complete' if completion(audit['question_reassessment'], inventory) else 'partial'
    inv.require(rebuilt == expression and applications == audit['applications'], 'description/application/reference drift')
    inv.require(recovery_expression.projection_audit(rebuilt) == audit['expression_projection'],
                'expression projection boundary drift')
    return manifest, payloads


def handoff(manifest):
    members = manifest['members']
    return {
        'B': {'expression': members['expression'], 'view': 'items[].locales[ko/en].s2',
              'references': 'represented_fact_refs and dependency_refs', 'residual': members['audit']},
        'C': {'expression': members['expression'], 'view': 'items[].locales[ko/en].expanded',
              'references': 'context, condition and acquisition qualified refs', 'residual': members['audit']},
        'ceiling': 'Offline description successor only; replacement product preservation and runtime integration remain B/C work.',
    }


def load_adopted(root, adoption_ref):
    """Explicit opt-in readpoint; existing root authorities remain unchanged."""
    root = Path(root).resolve()
    path = inv.local_path(root, adoption_ref['path'])
    inv.require(path.is_relative_to(root / FINAL_ROOT) and path.name == 'adoption.json', 'unexpected successor adoption path')
    record = inv.bound_json(root, adoption_ref)
    inv.require(record.get('schema') == 'iris-layer3-recovery-adoption-v1' and record.get('state') == 'adopted'
                and record.get('authorization', '').strip(), 'unadopted recovery successor')
    acceptance = record['acceptance']
    inv.require(acceptance['exit_code'] == 0 and acceptance['command'] == ACCEPTANCE_COMMAND
                and acceptance['subject'] == record['manifest'], 'unaccepted recovery successor')
    manifest_path = inv.local_path(root, record['manifest']['path'])
    inv.require(manifest_path.parent == path.parent and manifest_path.name == 'manifest.json'
                and acceptance['candidate_environment'] == str(path.parent), 'adoption subject/path mismatch')
    manifest, payloads = load_candidate(root, record['manifest'], consumable=True)
    inv.require(record['handoff'] == handoff(manifest) and record['product_migration'] == 'deferred', 'mixed B/C handoff')
    return {'mode': 'adopted', 'manifest': manifest, 'payloads': payloads, 'adoption': record}


def adopt(root, directory, expected_sha256, gate_exit_code, authorization):
    """Record the exact accepted immutable chain and perform its adopted readback."""
    root = Path(root).resolve()
    directory = (root / directory).resolve() if not directory.is_absolute() else directory.resolve()
    inv.require(directory.is_relative_to(root / FINAL_ROOT), 'adoption requires a durable successor path')
    inv.require(gate_exit_code == 0 and authorization.strip(), 'exact acceptance exit zero and owner authorization required')
    manifest_path = directory / 'manifest.json'
    raw = manifest_path.read_bytes()
    inv.require(digest(raw) == expected_sha256, 'candidate changed after acceptance')
    manifest = json.loads(raw)
    inv.require(manifest.get('completion') == 'complete', 'partial adoption forbidden')
    ref = {'path': manifest_path.relative_to(root).as_posix(), 'sha256': expected_sha256}
    record = {'schema': 'iris-layer3-recovery-adoption-v1', 'state': 'adopted', 'manifest': ref,
        'authorization': authorization, 'product_migration': 'deferred', 'handoff': handoff(manifest),
        'acceptance': {'command': ACCEPTANCE_COMMAND, 'exit_code': gate_exit_code, 'subject': ref,
                       'candidate_environment': str(directory)}}
    path = directory / 'adoption.json'
    with path.open('xb') as stream:
        stream.write(canonical(record))
    adoption_ref = {'path': path.relative_to(root).as_posix(), 'sha256': digest(canonical(record))}
    try:
        # Acceptance already consumed this exact subject. The single normal
        # adopted readback is the required P8 check, not another gate tree.
        load_adopted(root, adoption_ref)
    except BaseException:
        path.unlink()
        raise
    return adoption_ref


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--adopt', action='store_true')
    parser.add_argument('--candidate-sha256')
    parser.add_argument('--gate-exit-code', type=int)
    parser.add_argument('--authorization', default='')
    args = parser.parse_args(argv)
    root = args.repository_root.resolve()
    installed_identity(root)
    if args.adopt:
        ref = adopt(root, args.output, args.candidate_sha256, args.gate_exit_code, args.authorization)
        print(json.dumps({'adoption': ref}), flush=True)
        return 0
    from . import recovery_adjudication, recovery_migration, recovery_expression
    output = args.output if args.output.is_absolute() else root / args.output
    output = output.resolve()
    inv.require(any(output.is_relative_to(root / parent) for parent in ('.tmp/semantic', FINAL_ROOT)), 'repository-local semantic or durable successor output required')
    inv.require(not output.exists(), 'candidate output must not already exist')
    base = baseline(root)
    found = note_facts(base)
    from . import recovery_sources
    recovery_sources.extend(base, found)
    payload, audit, corrections = semantic_candidate(base, found)
    recovery_adjudication.reassess(base, payload, audit)
    inventory = recovery_migration.extract(predecessor_inventory(base))
    for module in (recovery_expression, recovery_sources, recovery_migration, recovery_adjudication):
        installed = Path(module.__file__).resolve()
        inv.require(installed.is_relative_to(root / 'Iris/tooling/.venv/Lib/site-packages')
                    and inv.sha(installed) == inv.sha(root / CODE / (installed.stem + '.py')),
                    'stale recovery installation: ' + installed.stem)
    focused = 'Iris/build/description/v2/tests/test_layer3_recovery.py'
    for path in (CODE + 'recovery.py', CODE + 'recovery_expression.py', CODE + 'recovery_sources.py', CODE + 'recovery_migration.py', CODE + 'recovery_adjudication.py', PLAN, focused):
        base['reader'].read(path)
    relative = output.relative_to(root).as_posix()
    semantic_ref = {'path': relative + '/semantic.json', 'sha256': digest(canonical(payload))}
    acquisition = acquisition_successor(base, semantic_ref)
    acquisition_ref = {'path': relative + '/acquisition.json', 'sha256': digest(canonical(acquisition))}
    bindings = {'semantic': semantic_ref, 'acquisition': acquisition_ref,
                'definition': base['reader'].bindings[READPOINTS['definition']],
                'successor': base['reader'].bindings[READPOINTS['successor']]}
    expression, applications = recovery_expression.prepare({**base, 'acquisition': acquisition}, payload, bindings)
    recovery_migration.adjudicate(base, inventory, expression, payload)
    recovery_adjudication.reconcile_direct_claims(base, payload, audit, inventory)
    completed = completion(audit, inventory)
    state = 'complete' if completed else 'partial'
    expression['completion'] = state
    inventory['completion'] = state
    output.mkdir(parents=True)
    report = {'status': 'candidate', 'completion': state, 'adoption': 'requires_exact_acceptance' if completed else 'not_permitted',
              'inputs': sorted(base['reader'].bindings.values(), key=lambda r: r['path']),
              'historical_inputs': base['reader'].archived,
              'generation': base['generation'], 'definition_correction': None,
              'question_counts': {'baseline': len(base['semantic']['results']), 'successor': len(payload['results']),
                                  'added_instances': len(payload['results']) - len(base['semantic']['results'])},
              'recovered_facts': sorted(found.facts.values(), key=lambda f: f['fact_id']),
              'corrections': corrections, 'question_reassessment': audit,
              'inventory': inventory, 'applications': applications,
              'expression_projection': recovery_expression.projection_audit(expression),
              'acquisition_binding': {'content_delta': 'none', 'dependency_binding_delta': 'yes',
                  'predecessor': base['reader'].bindings[READPOINTS['acquisition']],
                  'old_semantic': base['acquisition']['semantic_readpoint'], 'new_semantic': semantic_ref},
              'remaining_work': [] if completed else ['full migration clause inventory and disposition',
                                 'baseline and added question-local attribution', 'combined successor and bilingual conservation']}
    (output / 'semantic.json').write_bytes(canonical(payload))
    (output / 'acquisition.json').write_bytes(canonical(acquisition))
    (output / 'descriptions.json').write_bytes(canonical(expression))
    (output / 'audit.json').write_bytes(canonical(report))
    manifest = {'schema': 'iris-layer3-recovery-chain-v1', 'status': 'candidate', 'completion': state,
                'definition': bindings['definition'], 'successor': bindings['successor'],
                'focused_test': base['reader'].bindings[focused],
                'members': {name: {'path': relative + '/' + filename, 'sha256': inv.sha(output / filename)}
                            for name, filename in [('semantic', 'semantic.json'), ('acquisition', 'acquisition.json'),
                                                   ('expression', 'descriptions.json'), ('audit', 'audit.json')]}}
    (output / 'manifest.json').write_bytes(canonical(manifest))
    print(json.dumps({'output': str(output), 'status': report['status'], 'completion': state,
                      'source_confirmed_facts': len(found.facts)}), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
