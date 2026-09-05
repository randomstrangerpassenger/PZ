"""One off-live description acceptance gate; not a regular registry entry.

Run installed iris_tooling with --noconftest and the tooling project config.
No historical/current-route runner, source-root bootstrap or external output.
"""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

from iris_tooling.domains.layer3 import expression_results as result
from iris_tooling.domains.layer3 import expression_rules as rules
from iris_tooling.domains.layer3 import description_projection as projection
from iris_tooling.domains.layer3 import investigation as inv

REPO = Path(__file__).resolve().parents[5]


def subset(inputs, *items):
    selected = deepcopy(inputs)
    selected['targets'] = sorted(items)
    selected['facts'] = {k: v for k, v in selected['facts'].items() if v['item_id'] in items}
    selected['applications'] = {k: v for k, v in selected['applications'].items() if k in items}
    refs = {r for f in selected['facts'].values() for r in f['provenance_refs']}
    selected['provenance'] = {k: v for k, v in selected['provenance'].items() if k in refs}
    return selected


def fixture_review(review, inputs):
    # A synthetic test domain is not a content review or an adopted authority.
    value = deepcopy(review)
    value['payload_domain_sha256'] = result.selector_domain(inputs)
    return value


def test_expression_contract(monkeypatch, tmp_path):
    assert sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
    installed = result.installed_identity(REPO)
    assert set(installed) == set(result.MODULES)
    protected = inv.bound_json(REPO, result.INPUTS['acquisition'])['protected']
    before = {p: inv.sha(inv.local_path(REPO, p)) if inv.local_path(REPO, p).exists() else None for p in protected}
    assert before == protected
    # Existing registration/current product remains byte-identical; no new
    # classification entry or complete-repository suite is required here.
    current = ('Iris/_docs/authority/iris_current_route_index.json',
               'Iris/_docs/authority/iris_current_authority_manifest.json',
               'Iris/_docs/round3/round3_pytest_source_classification.json',
               'Iris/tooling/pyproject.toml', 'Iris/tooling/uv.lock')
    current_before = {p: inv.sha(REPO / p) for p in current}
    print('Input and installed identity loaded', flush=True)
    inputs = result.read_inputs(REPO)
    review = result.read_review(REPO, inputs)
    ref = inv.binding(REPO, result.ROOT + '/manifest.json')
    loaded = result.load(REPO, ref, mode='candidate', inputs=inputs)
    payload = loaded['payload']
    assert payload['denominators'] == result.DENOMINATORS
    assert payload['completion'] == 'complete' and payload['expression_gaps'] == []
    assert payload['inputs'] == result.INPUTS and payload['product_migration'] == 'deferred'
    facts = {f['ref']: f for f in payload['facts']}
    expressions = {e['expression_id']: e for e in payload['expressions']}
    assert len(facts) == 5290 and len(expressions) == len(payload['expressions'])
    assert set(inputs['profiles']) == set(rules.PROFILE_GRAMMARS)
    assert Counter(f['fact_kind'] for f in facts.values()) == {
        'condition': 1850, 'constraint': 4, 'context_role': 566,
        'direct_function': 1141, 'effect': 110, 'use_context': 562, 'acquisition': 1057}
    items = {i['item_id']: i for i in payload['items']}
    assert list(items) == inputs['targets'] and len(items) == 2105
    all_pairs = set()
    acquisition_pairs = set()
    upstream_gaps = 0
    for item in payload['items']:
        accepted = {r for r, f in facts.items() if f['item_id'] == item['item_id']}
        app = inputs['applications'][item['item_id']]
        assert {p['profile_id'] for p in item['profiles']} == {p['profile_id'] for p in app['routing'] if p['scope_refs']}
        assert item['upstream']['item_investigation_state'] == 'incomplete'
        contributors = {r for o in item['first_contact_obligations'] for r in o['fact_refs']}
        for obligation in item['first_contact_obligations']:
            assert obligation['question_key'][0] == item['item_id']
            if obligation['state'] == 'upstream_gap':
                upstream_gaps += 1
                assert not obligation['fact_refs']
        for locale in rules.LOCALES:
            data = item['locales'][locale]
            assert set(data['expanded_represented_fact_refs']) == accepted
            assert set(data['fact_expressions']) == accepted
            for fact_ref, refs in data['fact_expressions'].items():
                assert refs and len(refs) == len(set(refs))
                for expression_id in refs:
                    e = expressions[expression_id]
                    assert e['locale'] == locale and fact_ref in e['represented_fact_refs']
                    assert e['review_ref'] == result.identity(review) + '/' + locale
                    assert e['text'] and '\n' not in e['text'] and '\r' not in e['text']
                all_pairs.add((fact_ref, locale))
                if facts[fact_ref]['fact_kind'] == 'acquisition':
                    acquisition_pairs.add((fact_ref, locale))
            s2 = data['s2']
            s2_refs = set(s2['represented_fact_refs'])
            omissions = set(data['tooltip_detail_omission_refs'])
            detail_qualifiers = set(s2['detail_qualifier_refs'])
            assert contributors <= s2_refs | detail_qualifiers and s2_refs <= accepted
            assert detail_qualifiers <= omissions and detail_qualifiers.isdisjoint(s2_refs)
            assert all(facts[r]['fact_kind'] in {'condition', 'constraint'}
                       and projection.qualifier_tag(facts[r]) is None for r in detail_qualifiers)
            assert s2_refs.isdisjoint(omissions) and s2_refs | omissions == accepted
            assert s2['logical_rows'] == int(bool(s2['text']))
            assert '\n' not in s2['text'] and '\r' not in s2['text']
            assert set(s2['expression_refs']) <= expressions.keys()
            assert s2_refs == {r for e in s2['expression_refs'] for r in expressions[e]['represented_fact_refs']}
            assert set(result.canonical(d) for d in s2['dependency_refs']) == {
                result.canonical(d) for e in s2['expression_refs'] for d in expressions[e]['dependency_refs']}
            for block in data['expanded']:
                assert block['text'] == ' '.join(expressions[e]['text'] for e in block['expression_refs'])
                assert block['represented_fact_refs']
                assert 'primary_profile' not in block and 'representative' not in block
    assert len(all_pairs) == 10580 and len(acquisition_pairs) == 2114 and upstream_gaps > 0

    # Dependency evidence is a real clause, not just a metadata attachment.
    for e in expressions.values():
        for filler in ('여러 용도로 사용할 수 있다', '생존에 유용하다', 'useful for survival', 'many uses', 'cannot be obtained', '획득할 수 없다'):
            assert filler not in e['text']
        if e['resolution'] == 'compact':
            assert e['claim_refs'] and set(e['claim_refs']) <= set(e['represented_fact_refs'])
            for word in ('inventory', 'eligibility', 'permission', 'adjacent', '소지품', '권한', '조건:'):
                assert word not in e['text']
            continue
        claim = facts[e['claim_ref']]
        refs = set(e['represented_fact_refs'])
        assert set(claim['qualifier_refs']) <= refs
        if claim['context_ref']:
            assert claim['context_ref'] in refs
            assert set(facts[claim['context_ref']]['qualifier_refs']) <= refs
        for dep in refs - {claim['ref']}:
            f = facts[dep]
            if f['fact_kind'] in {'condition', 'constraint'}:
                assert rules.predicate(f, e['locale']) in e['text']
        if claim['fact_kind'] == 'acquisition':
            paths = {d['payload_path'] for d in e['dependency_refs']}
            assert '/conditions/eligibility' in paths and '/conditions' not in paths
            for path in paths:
                value = claim['payload']
                for part in path.lstrip('/').split('/'):
                    value = value[part]
                assert value is not None
            for internal in ('selection weight', '가중치', '0~4', '0–4', '무작위 값', 'random draw',
                             'registry', '등록', 'callback', 'marker', 'destination', 'adjacent', '소지품', '조건 값'):
                assert internal not in e['text']

    # Real semantic examples, including unrelated acquisition routes omitted
    # normally from S2, and unresolved effect questions that cannot mint hunger.
    apple = items['Base.Apple']
    assert {'ingestion', 'cooking', 'crafting', 'direct'} <= {p['profile_id'] for p in apple['profiles']}
    assert apple['locales']['ko']['s2']['text'] == '먹을 수 있으며, 음식 준비와 조리의 재료로 사용할 수 있다.'
    assert apple['locales']['en']['s2']['text'] == 'It can be eaten and used as an ingredient in food preparation.'
    assert '허기' not in apple['locales']['ko']['s2']['text']
    water = items['Base.WaterBottleFull']['locales']['ko']['s2']['text']
    assert water == '마셔 갈증을 줄일 수 있으며, 오염된 물은 중독 수치를 높일 수 있다.'
    assert items['Base.WaterBottleFull']['locales']['en']['s2']['text'] == 'Drinking it can reduce thirst; tainted water can increase poison level.'
    water_menu = ' '.join(b['text'] for b in items['Base.WaterBottleFull']['locales']['ko']['expanded'])
    assert '0.1' in water_menu and '20 미만' in water_menu and '0.3 미만' in water_menu
    assert '0.1' not in water and '20 미만' not in water and '0.3 미만' not in water
    hammer = items['Base.Hammer']['locales']['en']['s2']['text']
    assert hammer == 'It serves as a tool for construction, moving furniture, woodworking, and can itself be repaired.'
    for locale, checks in {'ko': ('채집', '밭을 갈다가', '흙을 퍼 담다가'),
                           'en': ('foraging', 'plowing', 'shoveling')}.items():
        worm = items['Base.Worm']['locales'][locale]
        text = ' '.join(b['text'] for b in worm['expanded'])
        assert all(c in text for c in checks)
        assert all(facts[r]['fact_kind'] != 'acquisition' for r in worm['s2']['represented_fact_refs'])
    generator = ' '.join(b['text'] for b in items['Base.Generator']['locales']['en']['expanded'])
    assert generator == 'It can be obtained by picking up an existing, disconnected world generator, retaining its condition and remaining fuel.'
    assert 'craft' not in generator
    mouse = ' '.join(b['text'] for b in items['Base.DeadMouse']['locales']['en']['expanded'])
    assert 'Capture hours' not in mouse and '0:00' not in mouse
    for i in ('Base.Battery', 'Base.Hammer', 'Base.Notebook', 'Base.BookFirstAid3'):
        assert items[i]['locales']['ko']['s2']['text']

    # Second generation is deliberately reordered, within this same gate.
    reordered = deepcopy(inputs)
    reordered['facts'] = dict(reversed(list(reordered['facts'].items())))
    reordered['profiles'] = dict(reversed(list(reordered['profiles'].items())))
    for app in reordered['applications'].values():
        for name in ('routing', 'first_contact', 'fact_question_bindings', 'required_axes'):
            app[name].reverse()
    # Canonical fact records have stable identity order even when input maps do not.
    assert result.canonical(result.produce(reordered, review)) == result.canonical(payload)
    print('Full corpus, semantic branches and deterministic composition checked', flush=True)

    small = subset(inputs, 'Base.Apple', 'Base.WaterBottleFull')
    sr = fixture_review(review, small)
    base = result.produce(small, sr)
    mutations = (
        lambda p: p['facts'].append(deepcopy(p['facts'][0])),
        lambda p: p['expressions'][0].update(text='생존에 유용하다.'),
        lambda p: p['expressions'][0].update(locale='fr'),
        lambda p: p['expressions'][0].update(review_ref='stale'),
        lambda p: next(e for e in p['expressions'] if e['dependency_refs']).update(dependency_refs=[]),
        lambda p: p['items'][0]['locales']['ko']['s2'].update(text='first\nsecond'),
        lambda p: p['items'][0]['locales']['ko']['s2'].update(text=p['items'][0]['locales']['en']['s2']['text']),
        lambda p: p['items'][0]['locales']['ko'].update(tooltip_detail_omission_refs=[]),
        lambda p: p.update(inputs={}),
    )
    for change in mutations:
        broken = deepcopy(base)
        change(broken)
        with pytest.raises(ValueError):
            result.validate_payload(broken, small, sr)
    broken_review = deepcopy(sr)
    broken_review['locales']['ko']['state'] = 'pending'
    with pytest.raises(ValueError, match='locale not approved'):
        result.produce(small, broken_review)
    broken_inputs = deepcopy(small)
    next(iter(broken_inputs['facts'].values()))['payload']['unexpected'] = True
    with pytest.raises(ValueError, match='unreviewed payload'):
        result.produce(broken_inputs, sr)

    # A fact with no profile membership remains in expanded residual composition.
    residual = subset(inputs, 'Base.Battery')
    residual['applications']['Base.Battery']['fact_question_bindings'] = []
    residual['applications']['Base.Battery']['first_contact'] = []
    rp = result.produce(residual, fixture_review(review, residual))
    assert all(b['composition'] == 'residual' for b in rp['items'][0]['locales']['ko']['expanded'])
    assert rp['items'][0]['locales']['ko']['s2']['state'] == 'no_first_contact'

    # An acquisition route becomes S2 only if the actual obligation asks for it.
    contact = subset(inputs, 'Base.Worm')
    app = contact['applications']['Base.Worm']
    app['first_contact'].append({'axis_id': 'acquisition', 'scope_ref': 'item', 'contributors': ['direct']})
    cp = result.produce(contact, fixture_review(review, contact))
    cr = cp['items'][0]['locales']['ko']['s2']['represented_fact_refs']
    assert {r for r, f in contact['facts'].items() if f['fact_kind'] == 'acquisition'} <= set(cr)

    # Loader failures share the same filesystem input. In-memory mutations never
    # edit sealed members or create a directory per negative case.
    bound_json = inv.bound_json
    for change in (
        lambda m: m['members'].append(deepcopy(m['members'][0])),
        lambda m: m['members'][0].update(path='../escape.json'),
        lambda m: m['data'].update(sha256='0' * 64),
        lambda m: m['inputs']['semantic'].update(sha256='0' * 64),
    ):
        broken = deepcopy(loaded['manifest'])
        change(broken)
        with monkeypatch.context() as patch:
            patch.setattr(inv, 'bound_json', lambda root, binding: broken if binding == ref else bound_json(root, binding))
            with pytest.raises(ValueError):
                result.load(REPO, ref, mode='candidate', inputs=inputs)
    with pytest.raises(ValueError):
        result.load(REPO, {'path': '../escape.json', 'sha256': '0' * 64})
    with pytest.raises(ValueError):
        result.load(REPO, ref, mode='adopted', inputs=inputs)
    with pytest.raises(ValueError):
        result.adopt(REPO, ref['sha256'], 1, 'fixture')
    with pytest.raises(ValueError):
        result.adopt(REPO, '0' * 64, 0, 'fixture')

    # Fail-closed state transition leaves no completed receipt after readback
    # failure. One short repository-local scratch directory serves this contract.
    assert tmp_path.resolve().is_relative_to(REPO)
    (tmp_path / 'manifest.json').write_bytes((REPO / result.ROOT / 'manifest.json').read_bytes())
    previous = (REPO / result.ROOT / 'adoption.json').read_bytes()
    (tmp_path / 'adoption.json').write_bytes(previous)
    with monkeypatch.context() as patch:
        patch.setattr(result, '_output', lambda root: tmp_path)
        def fail_readback(*args, **kwargs):
            raise ValueError('fixture adopted readback failure')
        patch.setattr(result, 'load', fail_readback)
        with pytest.raises(ValueError, match='readback failure'):
            result.adopt(REPO, ref['sha256'], 0, 'fixture only')
    assert (tmp_path / 'adoption.json').read_bytes() == previous
    assert json.loads(previous)['state'] == 'superseded'
    after = {p: inv.sha(inv.local_path(REPO, p)) if inv.local_path(REPO, p).exists() else None for p in protected}
    assert after == before
    assert {p: inv.sha(REPO / p) for p in current} == current_before
    lengths = {}
    for locale in rules.LOCALES:
        values = sorted(len(i['locales'][locale]['s2']['text']) for i in payload['items'] if i['locales'][locale]['s2']['text'])
        lengths[locale] = {'nonempty': len(values), 'p50': values[(len(values) * 50 + 99) // 100 - 1],
                           'p95': values[(len(values) * 95 + 99) // 100 - 1], 'max': values[-1]}
    print(json.dumps({'gate': result.GATE, 'candidate': ref, **payload['denominators'],
                      'upstream_gap_obligations': upstream_gaps, 's2_lengths': lengths,
                      'installed_modules': installed}), flush=True)
