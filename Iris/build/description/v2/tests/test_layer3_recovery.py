"""Off-live recovery acceptance, explicitly invoked and not registry-owned.

The current partial candidate must fail final acceptance until the remaining
semantic investigation, clause decomposition and conservation are implemented.
This source does not turn its own partial checks into a completion authority.
"""
from copy import deepcopy
import os
from pathlib import Path
import sys

import pytest

from iris_tooling.domains.layer3 import recovery
from iris_tooling.domains.layer3 import semantic_model
from iris_tooling.domains.layer3 import recovery_sources, source_reader

REPO = Path(__file__).resolve().parents[5]


def test_recovery_contract():
    assert sys.flags.isolated and sys.flags.dont_write_bytecode
    recovery.installed_identity(REPO)
    directory = Path(os.environ['IRIS_LAYER3_RECOVERY_CANDIDATE']).resolve()
    assert any(directory.is_relative_to(REPO / parent) for parent in ('.tmp/semantic', recovery.FINAL_ROOT))
    manifest_ref = {'path': (directory / 'manifest.json').relative_to(REPO).as_posix(),
                    'sha256': recovery.digest((directory / 'manifest.json').read_bytes())}
    base = recovery.baseline(REPO)
    manifest, payloads = recovery.load_candidate(REPO, manifest_ref, consumable=False, baseline_inputs=base)
    audit, semantic, acquisition, descriptions = (payloads[k] for k in ('audit', 'semantic', 'acquisition', 'expression'))
    bound = {r['path']: r for r in audit['inputs']}
    assert recovery.CODE + 'recovery.py' in bound
    assert recovery.CODE + 'recovery_expression.py' in bound
    assert recovery.POINTER in bound
    assert len(semantic['target_ids']) == 2105
    old_keys = {semantic_model.question_key(r) for r in base['semantic']['results']}
    new_keys = {semantic_model.question_key(r) for r in semantic['results']}
    audit_keys = {tuple(r['question_key']) for r in audit['question_reassessment']}
    assert old_keys <= new_keys == audit_keys
    assert len(old_keys) == 9982
    previous = {semantic_model.question_key(r): r for r in base['semantic']['results']}
    for row in audit['question_reassessment']:
        key = tuple(row['question_key'])
        assert row['previous_result'] == previous.get(key)
        if key not in old_keys:
            lineage = row['instance_recovery']
            assert lineage['baseline_absent'] and lineage['source_participants']
            assert lineage['definition_readpoint'] == semantic['definition_readpoint']
            assert lineage['registry_revision'] == base['semantic']['registry_revision']
            assert (lineage['profile_id'], key[2]) in {
                ('crafting', 'activity:crafting'), ('world_work', 'activity:world_work')}
    assert audit['question_counts'] == {'baseline': 9982, 'successor': len(new_keys),
                                        'added_instances': len(new_keys - old_keys)}
    # Rediscovering a cheese-sandwich ingredient is added evidence for the
    # existing food-preparation meaning, not a renamed context or correction.
    old_bread = [f for f in base['semantic']['facts'] if f['item_id'] == 'Base.BreadSlices'
                 and f['fact_kind'] == 'use_context' and f['payload'] == {'activity': 'food_preparation'}]
    assert len(old_bread) == 1
    same_bread = next(f for f in semantic['facts'] if f['fact_id'] == old_bread[0]['fact_id'])
    assert set(old_bread[0]['provenance_refs']) <= set(same_bread['provenance_refs'])
    assert same_bread['evidence_additions']['previous_fact_ref'] == old_bread[0]['fact_id']
    extra = [semantic['provenance'][p] for p in same_bread['provenance_refs']
             if semantic['provenance'][p].get('contributor_rule_ref') == 'food_preparation_recipes']
    assert extra and any('OnTest:Recipe.OnTest.WholeBreadSlices' in semantic['observations'][o]['content'].get('clauses', [])
                         for p in extra for o in p['observation_refs'])
    assert any(b['fact_ref'] == same_bread['fact_id'] and b['question_key'] == ['Base.BreadSlices', 'role', 'activity:crafting']
               for b in semantic['fact_question_bindings'])
    assert not any(c['old_fact_ref'] == same_bread['fact_id'] for c in audit['corrections'])
    # Shared in-memory grammar cases: participation does not resolve quantities.
    record = {'module': 'Base', 'clauses': ['Salt;1', '[Recipe.GetItemTypes.Sugar];2.5',
               'Salt=2', 'keep Salt;3', 'Salt;1;2', '[Unknown.Group];3', 'Result:Salt;2',
               'Salt = 3', 'keep [Recipe.GetItemTypes.Sugar] = 2']}
    fields = {'Base.Salt': {}, 'Base.SugarBrown': {'Tags': 'Sugar'}}
    groups = {'Recipe.GetItemTypes.Sugar': {'supported': True, 'tags': ['Sugar'], 'types': []}}
    old_rows, old_opaque = source_reader.recipe_participants(record, fields, groups)
    rows, opaque = recovery_sources.recipe_participants(record, fields, groups)
    assert all(r in rows for r in old_rows) and opaque == old_opaque
    added = [r for r in rows if 'numeric_suffix' in r]
    assert [(r['item_id'], r['role'], r['ordinal']) for r in added] == [
        ('Base.Salt', 'input', 0), ('Base.SugarBrown', 'input', 1), ('Base.Salt', 'keep', 3),
        ('Base.Salt', 'input', 7), ('Base.SugarBrown', 'keep', 8)]
    assert [r['numeric_suffix']['literal'] for r in added] == ['1', '2.5', '3', '3', '2']
    assert [r['numeric_suffix']['separator'] for r in added] == [';', ';', ';', '=', '=']
    assert all(r['numeric_suffix']['meaning'] == 'not interpreted; participation admission only' for r in added)
    headers = recovery_sources.module_imports('module farming { imports { Base, Extra }', 'scripts/farming.txt')
    record = {'module': 'farming', 'module_imports': headers, 'ambiguous_item_ids': ['Base.Ambiguous'],
              'clauses': ['Salt = 3', 'keep SugarBrown', 'Result:Output', 'Shadow', 'Base.Salt', 'Ambiguous', 'Shared']}
    fields.update({'Base.Output': {}, 'Base.Shadow': {}, 'farming.Shadow': {},
                   'Extra.Shared': {}, 'Base.Shared': {}, 'Extra.Ambiguous': {}})
    old_rows, old_opaque = source_reader.recipe_participants(record, fields, groups)
    rows, opaque = recovery_sources.recipe_participants(record, fields, groups)
    assert all(r in rows for r in old_rows) and opaque == old_opaque
    assert [(r['item_id'], r['role']) for r in rows if 'import_resolution' in r] == [
        ('Base.Salt', 'input'), ('Base.SugarBrown', 'keep'), ('Base.Output', 'result')]
    assert len(new_keys) == len(semantic['results'])  # union by item/axis/scope
    assert {('Base.WeldingMask', axis, 'activity:crafting') for axis in ('role', 'conditions')} <= new_keys - old_keys
    mask_row = next(r for r in audit['question_reassessment']
                    if r['question_key'] == ['Base.WeldingMask', 'role', 'activity:crafting'])
    mask_links = mask_row['instance_recovery']['source_participants']
    assert all(p['stable_group_resolution']['membership_tags'] == ['WeldingMask']
               and p['stable_group_resolution']['repeated_fields']['BloodLocation'] == ['Head', 'Head'] for p in mask_links)
    duplicate = {'clauses': ['Type=Clothing', 'BloodLocation=Head', 'BloodLocation=Head', 'Tags=WeldingMask']}
    assert source_reader.unique_properties(duplicate) is None
    assert recovery_sources.stable_properties(duplicate)[0]['Tags'] == 'WeldingMask'
    conflicting = {'clauses': [*duplicate['clauses'], 'Tags=Other']}
    assert 'Tags' not in recovery_sources.stable_properties(conflicting)[0]
    for row in audit['question_reassessment']:
        comparison = row.get('applied_inputs', {}).get('predecessor_comparison', {})
        if comparison.get('completion') == 'complete':
            assert comparison['compared'] and not comparison['pending_claim_refs'] and not comparison['unsegmented_surfaces']
    for item in ('Base.OilOlive', 'Base.OilVegetable', 'Base.SugarBrown', 'Base.SugarPacket', 'Base.Salt', 'Base.Margarine'):
        assert {(item, axis, 'activity:crafting') for axis in ('role', 'conditions')} <= new_keys - old_keys
    for item in ('Base.Stone', 'Base.SheetRope', 'Base.Mattress', 'Base.Doorknob', 'Base.Garbagebag',
                 'Base.Gravelbag', 'Base.Hinge', 'Base.BarbedWire', 'Base.Drawer', 'Base.Sandbag',
                 'Base.MetalPipe', 'Base.ScrapMetal', 'Base.MetalBar', 'Base.Wire', 'Base.WeldingRods', 'Base.WeldingMask'):
        assert {(item, axis, 'activity:world_work') for axis in ('role', 'conditions')} <= new_keys - old_keys
    assert [r['item_id'] for r in audit['inventory']['items']] == semantic['target_ids']
    assert acquisition['facts'] == base['acquisition']['facts']
    assert recovery.acquisition_content(acquisition) == recovery.acquisition_content(base['acquisition'])
    assert acquisition['authority_id'] != base['acquisition']['authority_id']
    assert all(r['authority_ref'] == acquisition['authority_id'] for r in acquisition['results'])
    assert acquisition['provenance'] == base['acquisition']['provenance']
    assert acquisition['semantic_readpoint'] == descriptions['inputs']['semantic']
    for name in ('semantic', 'acquisition'):
        ref = descriptions['inputs'][name]
        assert ref['path'] == (directory / (name + '.json')).relative_to(REPO).as_posix()
        assert ref['sha256'] == recovery.digest((directory / (name + '.json')).read_bytes())
    items = {i['item_id']: i for i in descriptions['items']}
    expected_notes = {'Base.Notebook', 'Base.Journal', 'Base.Doodle', 'Base.SheetPaper2'}
    viewing = [f for f in semantic['facts'] if f['payload'] == {'function': 'view_written_note_pages'}]
    assert {f['item_id'] for f in viewing} == expected_notes
    for item in expected_notes:
        results = {r['axis_id']: r for r in semantic['results']
                   if r['item_id'] == item and r['scope_ref'] == 'activity:reading'}
        assert results['operation']['state'] == 'resolved'
        assert results['conditions']['state'] == results['effects']['state'] == 'resolved'
        assert all(not r['blockers'] and r['question_coverage'] == 'whole_scope' for r in results.values())
        assert all('ISReadABook_SkillBook_and_ReadLiterature' not in r['blockers'] for r in results.values())
        ko = items[item]['locales']['ko']['s2']['text']
        en = items[item]['locales']['en']['s2']['text']
        assert '필기구 없이 읽을 수 있다' in ko and 'without a writing implement' in en
        assert '다른 사용자의 잠금이 없고 자신의 편집 잠금도 풀면' in ko
        assert 'no other user holding the lock' in en and 'editing lock unlocked' in en
        assert '내용과 제목' in ko and 'pages and titles' in en
        note_effects = {f['payload']['property'] for f in semantic['facts']
                        if f['item_id'] == item and f['fact_kind'] == 'effect'}
        assert note_effects == {'written_note_pages', 'written_note_title', 'written_note_lock'}
    # Actual language is part of P7, independently of reference coverage. These
    # expectations share the final candidate; no preview script is an authority.
    for locale, concepts in {
        'ko': ('가구 이동', '목공 작업', '건축 작업', '단조', '수리', '씻', '근접 공격'),
        'en': ('moving furniture', 'woodworking', 'construction', 'forging', 'repair', 'washed', 'melee attacks'),
    }.items():
        hammer = items['Base.Hammer']['locales'][locale]
        assert all(word in hammer['s2']['text'] for word in concepts)
        assert hammer['s2']['text'].count('도구로 쓰인다' if locale == 'ko' else 'It serves as a tool') == 1
        assert ('삽·손삽 단조' if locale == 'ko' else 'shovel and hand-shovel forging') not in hammer['s2']['text']
        assert hammer['s2']['detail_qualifier_refs']
        assert set(hammer['s2']['detail_qualifier_refs']) <= set(hammer['tooltip_detail_omission_refs'])
        assert 'IronIngot' not in hammer['s2']['text'] and '시간 200' not in hammer['s2']['text']
        apple = items['Base.Apple']['locales'][locale]['s2']['text']
        assert all(word in apple.lower() for word in (('먹', '요리 재료', '미끼', '익히지 않은') if locale == 'ko'
                                              else ('eaten', 'cooking ingredient', 'bait', 'uncooked')))
        chef = next(f['ref'] for f in descriptions['facts'] if f['item_id'] == 'Base.Apple'
                    and f['payload'] == {'property': 'food_chef_attribution', 'direction': 'set_transferring_character'})
        apple_output = items['Base.Apple']['locales'][locale]
        assert chef not in apple_output['s2']['represented_fact_refs']
        assert chef in apple_output['expanded_represented_fact_refs']
        assert any(d['fact_ref'] == chef and 'metadata' in d['reason'] for d in apple_output['s2']['detail_fact_omissions'])
        assert ('조리자' if locale == 'ko' else 'chef') not in apple
        assert all(word in items['Base.Notebook']['locales'][locale]['s2']['text']
                   for word in (('모닥불', '연료', '불쏘시개', '소모', '통나무가 든 드럼', '불이 꺼진') if locale == 'ko'
                                else ('campfires', 'fuel', 'tinder', 'consumed', 'drums containing logs', 'unlit')))
        assert items['Base.Notebook']['locales'][locale]['s2']['text'].count('불쏘시개' if locale == 'ko' else 'as tinder') == 1
        assert all(word not in hammer['s2']['text'] for word in
                   (('못 두 개', '하나씩', '이동하면', '문을 닫아') if locale == 'ko'
                    else ('two nails', 'one at a time', 'movement interrupts', 'Keep the door closed')))
        assert ('못 두 개' if locale == 'ko' else 'two nails') in ' '.join(b['text'] for b in hammer['expanded'])
        molotov = items['Base.Molotov']['locales'][locale]['s2']['text']
        assert ('차량 밖에서 투척 공격' if locale == 'ko' else 'throwing attacks outside a vehicle') in molotov
        assert all(word not in molotov for word in (('요청', '밀치기') if locale == 'ko' else ('request', 'shoving')))
        notebook_detail = ' '.join(b['text'] for b in items['Base.Notebook']['locales'][locale]['expanded'])
        assert ('물품 전체를 소모' if locale == 'ko' else 'whole item is consumed') in notebook_detail
        assert all(word not in notebook_detail for word in
                   (('착용 중', '옷은 벗고', '용기는 비워') if locale == 'ko'
                    else ('worn clothing', 'clothing must', 'containers empty')))
    # Exercise the shared rule's actual outputs, including its wider tinder
    # population, while retaining all canonical facts and audit boundaries.
    affected = {f['item_id'] for f in descriptions['facts'] if f['payload'].get('predicate') in
                {recovery_sources.INDUSTRIAL_TINDER, recovery_sources.HEAT_FRICTION, recovery_sources.HEARTH_FUEL}}
    for item_id in affected:
        for locale in ('ko', 'en'):
            output = items[item_id]['locales'][locale]
            assert not any(token in ' '.join(b['text'] for b in output['expanded']) for token in
                           ('클라이언트', '비활성 상태', '배수형 물품', 'client furnace', 'drainable is used once'))
    assert audit['expression_projection']
    for row in descriptions['expressions']:
        assert not any(token in row['text'] for token in ('equipment washing', '콜백', 'callback',
                                                         'RecipeManager', 'BSItem_OnCreate', 'ZombRand'))
        if row['locale'] == 'en':
            assert not any('가' <= char <= '힣' for char in row['text'])
    assert all(len(pair) == 2 for pair in recovery_sources.EFFECTS.values())
    for correction in audit['corrections']:
        assert correction['old_fact_ref'] not in {f['fact_id'] for f in semantic['facts']}
        if correction.get('kind') == 'withdrawal':
            assert correction['new_fact_ref'] is None
            assert correction['source_refs'] and correction['reason']
        else:
            assert correction['new_fact_ref'] in {f['fact_id'] for f in semantic['facts']}
    # Reuse byte-bound members and the normal consumer. Only the mutated
    # section is copied; no gate-specific filesystem trees are created.
    def rejects(section, mutate, message):
        original = payloads[section]
        payloads[section] = deepcopy(original)
        try:
            mutate(payloads[section])
            with pytest.raises(ValueError, match=message):
                recovery.consume_candidate(base, manifest, payloads, consumable=False)
        finally:
            payloads[section] = original

    def add_prose_only_fact(payload):
        fact = deepcopy(next(f for f in payload['facts'] if f['fact_kind'] == 'direct_function'))
        fact['payload'] = {'function': 'unsupported predecessor prose'}
        fact['fact_id'] = semantic_model.fact_identity(fact)
        payload['facts'].append(fact)

    rejects('semantic', lambda p: p.update(target_ids=[s.lower() for s in p['target_ids']]), 'target mismatch')
    rejects('semantic', lambda p: p.update(status='adopted'), 'mixed candidate/adopted')
    rejects('semantic', add_prose_only_fact, 'proposition/fact mismatch')
    rejects('semantic', lambda p: p.update(source_bindings=[r for r in p['source_bindings']
            if r['path'] != next(iter(p['observations'].values()))['source_path']]), 'unbound observation')
    rejects('audit', lambda p: p['question_reassessment'].pop(), 'question attribution')
    rejects('audit', lambda p: next(r for r in p['question_reassessment']
            if r['successor_result']['state'] == 'investigated_unresolved').update(direct_evidence_refs=[]), 'question attribution')
    rejects('audit', lambda p: next(r for r in p['question_reassessment']
            if r['successor_result']['state'] == 'investigated_unresolved').update(effective_blocker_refs=[]), 'route blocker copied')
    rejects('audit', lambda p: next(r for r in p['question_reassessment']
            if r.get('applied_inputs') and len(r['applied_inputs']['declarations']) == 1
            and not r['applied_inputs']['field_conflicts']).update(attribution_status='attribution_failure'), 'generic attribution failure')
    rejects('audit', lambda p: next(r for r in p['question_reassessment']
            if r['successor_result']['state'] == 'resolved').update(remaining_scope=[{'meaning': 'still open'}]), 'terminal question retains residual')
    rejects('audit', lambda p: p['corrections'][0].update(new_fact_ref='missing'), 'broken correction reference')
    rejects('expression', lambda p: p['facts'].pop(), 'expression fact omission')
    rejects('expression', lambda p: p['items'][0]['locales'].pop('en'), 'missing expression locale')
    rejects('expression', lambda p: next(i for i in p['items'] if i['locales']['en']['expanded']).get('locales')['en'].update(expanded=[]), 'suppressed locale')
    rejects('expression', lambda p: p['inputs'].update(semantic=base['acquisition']['semantic_readpoint']), 'incoherent candidate chain')
    rejects('audit', lambda p: next(r for r in p['inputs'] if r['path'] == recovery.POINTER).update(sha256='0' * 64), 'input drift')
    rejects('audit', lambda p: p['inventory']['claims'][0].pop('migration_disposition'), 'missing disposition')
    rejects('audit', lambda p: next(c for c in p['inventory']['clauses'] if c['classification'] == 'claim_ids').update(
        classification='non_semantic', claim_ids=[], classification_rule_ref='whitespace_punctuation/1',
        classification_reason='Exact whitespace/sentence punctuation contains no proposition.'), 'non-semantic clause classification')
    rejects('audit', lambda p: next(c for c in p['inventory']['clauses'] if c['classification'] == 'claim_ids').update(
        classification_rule_ref=None), 'missing clause classification rule')
    rejects('audit', lambda p: next(c for c in p['inventory']['clauses'] if c['classification'] == 'claim_ids').update(
        classification='unsegmented'), 'invalid unsegmented clause')
    rejects('audit', lambda p: next(c for c in p['inventory']['clauses'] if c['classification'] == 'non_semantic').update(
        classification_reason='connector'), 'non-semantic clause classification')
    # Small negative mutations reuse the same candidate and original checks.
    broken = deepcopy(semantic)
    broken['results'].append(deepcopy(broken['results'][0]))
    with pytest.raises(ValueError, match='result/universe mismatch'):
        semantic_model.validate_payload(broken, base['contract'])
    broken = deepcopy(semantic)
    next(f for f in broken['facts'] if f['payload'] == {'predicate': recovery.NOTE_EDIT})['applies_to_fact_refs'] = ['missing']
    with pytest.raises(ValueError, match='semantic correction requires new ID'):
        semantic_model.validate_payload(broken, base['contract'])
    # The normal consumer already performed the one required expression and
    # application reconstruction against this exact candidate.
    # A successful note correction or a populated 9,982-row audit is not A1-A7.
    recovery.require_ready(audit)
