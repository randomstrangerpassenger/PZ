"""One-off reading aid for this review; not an Iris validator or authority."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

from iris_tooling.domains.layer3 import description_composition_results as descriptions

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract():
    result = descriptions.read_result(ROOT)
    source = json.loads((ROOT / result['input']['path']).read_text(encoding='utf-8'))
    inputs = {i['item_id']: i for i in source['items']}
    patterns, rows = [], []
    lookup = {}
    for item in result['items']:
        origin = inputs[item['item_id']]
        facts = {f['fact_ref']: f for b in origin['blocks'] for branch in b['branches'] for f in branch['facts']}
        qs = {q['qualifier_id']: q for q in origin['qualifiers']}
        surfaces = {}
        for loc in ('ko', 'en'):
            for depth in ('compact', 'expanded'):
                row = item['locales'][loc][depth]
                refs = []
                for seg in row['segments']:
                    meanings = []
                    for ref in seg['fact_refs']:
                        if ref not in facts:
                            continue
                        f = facts[ref]
                        meanings.append({'kind': f['fact_kind'], 'payload': f['payload'],
                            'conditions': sorted(q['payload']['predicate'] for q in qs.values() if ref in q['applies_to_fact_refs'])})
                    record = {'locale': loc, 'depth': depth, 'text': seg['text'],
                        'expression': seg['expression'], 'meanings': sorted(meanings, key=lambda x: json.dumps(x, sort_keys=True)),
                        'placement': seg.get('placement_reason'),
                        'dispositions': sorted([{'predicate': qs[d['qualifier_ref']]['payload']['predicate'],
                            'placement': d['placement'], 'text': d['text']} for d in seg.get('qualifier_dispositions', [])], key=lambda x: json.dumps(x, sort_keys=True))}
                    key = json.dumps(record, ensure_ascii=False, sort_keys=True)
                    if key not in lookup:
                        lookup[key] = len(patterns)
                        patterns.append(record)
                    refs.append(lookup[key])
                surfaces[loc + '/' + depth] = {'state': row['state'], 'reason': row['reason'], 'patterns': refs}
        rows.append({'item': item['item_id'], 'surfaces': surfaces,
            'input_blocks': len(origin['blocks']), 'input_classes': sorted({b['class'] for b in origin['blocks']}),
            'unresolved': len(origin['unresolved_relations'])})
    report = {'subject': digest(ROOT / descriptions.DEFAULT_OUTPUT), 'input': result['input'],
        'producer': result['producer'], 'schema': result['schema'], 'version': result['version'],
        'producer_drift': [p for p, h in result['producer']['files'].items() if digest(ROOT / p) != h],
        'input_matches': digest(ROOT / result['input']['path']) == result['input']['sha256'],
        'summary': result['summary'], 'patterns': patterns, 'items': rows,
        'note': 'Extraction only. Pattern and item records do not imply language acceptance. Exact refs remain in the identified corpus.'}
    (OUT / 'reading.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('subject', 'schema', 'version', 'producer_drift', 'input_matches', 'summary')}, ensure_ascii=False))
    print('patterns', len(patterns), Counter((p['locale'], p['depth']) for p in patterns))


def show():
    data = json.loads((OUT / 'reading.json').read_text(encoding='utf-8'))
    mode = sys.argv[1]
    start, end = map(int, sys.argv[2:4])
    if mode == 'detail':
        unique = {}
        for n, p in enumerate(data['patterns']):
            if p['depth'] == 'expanded' and not any(m['kind'] == 'acquisition' for m in p['meanings']):
                unique.setdefault((p['locale'], p['text']), []).append(n)
        for index, ((loc, text), ids) in enumerate(unique.items()):
            if start <= index < end:
                print(index, loc, ids, text)
        print('total', len(unique))
    elif mode in ('compact', 'expanded'):
        pairs = {}
        for row in data['items']:
            ko = row['surfaces']['ko/' + mode]['patterns']
            en = row['surfaces']['en/' + mode]['patterns']
            # Different locales may coordinate different numbers of clauses.
            # Pair only segments with exactly the same meaning set.
            for a in ko:
                candidates = [b for b in en if data['patterns'][a]['meanings'] == data['patterns'][b]['meanings']]
                if len(candidates) != 1:
                    continue
                b = candidates[0]
                p, q = data['patterns'][a], data['patterns'][b]
                key = (p['text'], q['text'])
                pairs.setdefault(key, []).append((row['item'], a, b))
        for n, ((ko, en), members) in enumerate(pairs.items()):
            if start <= n < end:
                print(n, members[0], 'uses', len(members))
                print(ko)
                print(en)
        print('total paired texts', len(pairs))
    elif mode == 'patterns':
        for n in range(start, min(end, len(data['patterns']))):
            p = data['patterns'][n]
            print(n, p['locale'], p['depth'], p['text'])
            if '--meaning' in sys.argv:
                print(json.dumps(p['meanings'], ensure_ascii=False))
    elif mode == 'items':
        for row in data['items'][start:end]:
            print(row['item'], json.dumps(row['surfaces'], ensure_ascii=False, separators=(',', ':')), 'blocks', row['input_blocks'], row['input_classes'], 'unresolved', row['unresolved'])


def delta():
    before = descriptions.read_result(ROOT, 'Iris/build/description/composition/quality_review/before.json')
    after = descriptions.read_result(ROOT)
    changed, texts = [], {}
    for old, new in zip(before['items'], after['items'], strict=True):
        for loc in ('ko', 'en'):
            for depth in ('compact', 'expanded'):
                a, b = old['locales'][loc][depth], new['locales'][loc][depth]
                if a != b:
                    changed.append([new['item_id'], loc, depth, a['text'] != b['text']])
                    old_segments = {s['text'] for s in a['segments']}
                    for s in b['segments']:
                        if s['text'] not in old_segments:
                            texts.setdefault((loc, depth, s['text']), []).append(new['item_id'])
    print('changed', Counter((loc, depth, text_changed) for _, loc, depth, text_changed in changed))
    start, end = map(int, sys.argv[2:4])
    for n, ((loc, depth, text), members) in enumerate(texts.items()):
        if start <= n < end:
            print(n, loc, depth, len(members), members[0], text)
    print('new texts', len(texts), 'subject', digest(ROOT / descriptions.DEFAULT_OUTPUT))


def coverage():
    """Record pending keys; this deliberately does not grant prose acceptance."""
    before = descriptions.read_result(ROOT, 'Iris/build/description/composition/quality_review/before.json')
    result = descriptions.read_result(ROOT)
    source = json.loads((ROOT / result['input']['path']).read_text(encoding='utf-8'))
    records = []
    distribution = Counter()
    changes = Counter()
    for old, item, origin in zip(before['items'], result['items'], source['items'], strict=True):
        row = {'item_id': item['item_id'], 'surfaces': {}, 'input_blocks': len(origin['blocks']),
               'input_classes': sorted({b['class'] for b in origin['blocks']})}
        for loc in ('ko', 'en'):
            for depth in ('compact', 'expanded'):
                surface = item['locales'][loc][depth]
                key = loc + '/' + depth
                state = surface['state']
                changed = old['locales'][loc][depth] != surface
                distribution[state] += 1
                if changed:
                    changes[key] += 1
                absence = None
                if state == 'absent':
                    if not origin['blocks']:
                        absence = 'no accepted blocks in the current input'
                    elif depth == 'compact' and row['input_classes'] == ['acquisition']:
                        absence = 'only acquisition blocks; compact excludes acquisition'
                row['surfaces'][key] = {'state': state, 'reason': surface['reason'], 'changed': changed,
                    'disposition': 'normal_absence' if absence else 'pending_full_item_review',
                    'absence_basis': absence}
        records.append(row)
    report = {'status': 'partial', 'subject_path': descriptions.DEFAULT_OUTPUT,
        'subject_sha256': digest(ROOT / descriptions.DEFAULT_OUTPUT), 'schema': result['schema'], 'version': result['version'],
        'baseline_sha256': digest(ROOT / 'Iris/build/description/composition/quality_review/before.json'),
        'input': result['input'], 'producer': result['producer'],
        'input_matches': digest(ROOT / result['input']['path']) == result['input']['sha256'],
        'distribution': {s: distribution[s] for s in ('present', 'absent', 'failed')},
        'changed_surfaces': dict(changes),
        'reading_scope': 'Baseline compact wording triage; expanded detail entries 0-84; named predicate/source and grammar review; all 104 new final segment texts reread. No full item-combination acceptance is claimed.',
        'correction_readback': 'The 104 new final wordings were read in delta order 0-103 for scope, neutrality and detail. Scope fixtures and full input/ref comparison are in the existing focused test. These observations do not accept every affected item combination.',
        'test': {'command': r'uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py -q',
                 'cwd': str(ROOT), 'exit': 0, 'result': '1 passed in 4.74s'},
        'items': records,
        'note': 'One-off execution evidence. Not a validator, quality authority, seal or acceptance receipt.'}
    (OUT / 'review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('subject_sha256', 'distribution', 'changed_surfaces', 'input_matches')}, ensure_ascii=False))


def combinations():
    """Read current full semantic combinations; never updates acceptance."""
    result = descriptions.read_result(ROOT)
    source = json.loads((ROOT / result['input']['path']).read_text(encoding='utf-8'))
    groups = {}
    previous = {}
    if '--changed' in sys.argv:
        previous = {i['item_id']: i for i in json.loads((ROOT / 'Iris/build/description/composition/quality_review/read.json').read_text(encoding='utf-8'))['items']}
    for item, origin in zip(result['items'], source['items'], strict=True):
        if previous and item == previous[item['item_id']]:
            continue
        facts = {f['fact_ref']: (f['fact_kind'], f['payload']) for b in origin['blocks']
                 for br in b['branches'] for f in br['facts']}
        semantic = {ref for ref, (kind, _) in facts.items() if kind != 'acquisition'}
        def claims(refs):
            return sorted([facts[r] for r in refs if r in semantic], key=lambda v: json.dumps(v, sort_keys=True))
        surfaces = {}
        for loc in ('ko', 'en'):
            for depth in ('compact', 'expanded'):
                segments = item['locales'][loc][depth]['segments']
                surfaces[loc + '/' + depth] = [s['text'] for s in segments if set(s['fact_refs']) & semantic]
        meanings = {
            'branches': sorted([claims(br['facts'][n]['fact_ref'] for n in range(len(br['facts'])))
                for b in origin['blocks'] if b['class'] != 'acquisition' for br in b['branches']], key=str),
            'conditions': sorted([(q['payload']['predicate'], claims(q['applies_to_fact_refs'])) for q in origin['qualifiers']
                if set(q['applies_to_fact_refs']) & semantic], key=str),
            'relations': sorted([(r['kind'], claims(r.get('fact_refs', []))) for b in origin['blocks'] if b['class'] != 'acquisition'
                for r in b['relations']], key=str),
            'unresolved': origin['unresolved_relations'],
        }
        # Strip no semantics: unresolved identities deliberately keep unusual
        # combinations separate. Acquisition is read separately by route.
        key = json.dumps([surfaces, meanings], ensure_ascii=False, sort_keys=True)
        groups.setdefault(key, []).append(item['item_id'])
    start, end = map(int, sys.argv[2:4])
    from iris_tooling.domains.layer3 import recovery_sources as vocabulary
    names = {v: k for k, v in vars(vocabulary).items() if isinstance(v, str)}
    if '--record-read' in sys.argv:
        report = json.loads((OUT / 'review.json').read_text(encoding='utf-8'))
        subject = digest(ROOT / descriptions.DEFAULT_OUTPUT)
        history = report.setdefault('continued_reading', {})
        entry = history.setdefault(subject, {'semantic_items_read': [], 'note':
            'Explicit author reading record of actual text combinations and shared input meanings. Acquisition and exact final binding remain pending; not automated acceptance.'})
        members = [item for n, ids in enumerate(groups.values()) if start <= n < end for item in ids]
        entry['semantic_items_read'] = sorted(set(entry['semantic_items_read']) | set(members))
        (OUT / 'review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Recorded actual semantic reading', start, end, len(members), 'items; acquisition/final binding still pending')
        return
    text_ids, meaning_ids, component_ids = {}, {}, {}
    for n, (key, members) in enumerate(groups.items()):
        surfaces, meanings = json.loads(key)
        definitions = []
        coordinates = {}
        for label, texts in surfaces.items():
            coordinates[label] = []
            for text in texts:
                text_key = (label, text)
                if text_key not in text_ids:
                    text_ids[text_key] = len(text_ids)
                    definitions.append(('T' + str(text_ids[text_key]), label, text))
                coordinates[label].append(text_ids[text_key])
        meaning_key = json.dumps(meanings, ensure_ascii=False, sort_keys=True)
        fresh_meaning = meaning_key not in meaning_ids
        if fresh_meaning:
            meaning_ids[meaning_key] = len(meaning_ids)
        components, component_definitions = {}, []
        for kind, values in meanings.items():
            components[kind] = []
            for value in values:
                component_key = json.dumps([kind, value], ensure_ascii=False, sort_keys=True)
                if component_key not in component_ids:
                    component_ids[component_key] = len(component_ids)
                    shown = [names.get(value[0], value[0]), value[1]] if kind == 'conditions' else value
                    component_definitions.append((component_ids[component_key], kind, shown))
                components[kind].append(component_ids[component_key])
        if not start <= n < end:
            continue
        print('GROUP', n, 'MEMBERS', ', '.join(members))
        if '--reuse' in sys.argv:
            for definition in definitions:
                if '--changed' in sys.argv:
                    _, label, wording = definition
                    loc, depth = label.split('/')
                    prior = previous[members[0]]['locales'][loc][depth]['segments']
                    current = next(i for i in result['items'] if i['item_id'] == members[0])['locales'][loc][depth]['segments']
                    segment = next(s for s in current if s['text'] == wording)
                    same = next((n for n, s in enumerate(prior) if s == segment), None)
                    if same is not None:
                        print(definition[0], label, 'UNCHANGED read.json', members[0], 'segment', same)
                        continue
                print(*definition)
            print('ORDER', coordinates, 'MEANING', meaning_ids[meaning_key])
            if '--changed' not in sys.argv:
                for index, kind, value in component_definitions:
                    print('M' + str(index), kind, json.dumps(value, ensure_ascii=False))
                print('INPUT', components)
            else:
                print('INPUT unchanged blocks.json; original reading includes these exact members and scopes')
            continue
        else:
            for label, texts in surfaces.items():
                print(label, ' '.join(texts))
        print('CLAIMS', json.dumps(meanings['branches'], ensure_ascii=False))
        print('SCOPE', json.dumps([(names.get(p, p), claims) for p, claims in meanings['conditions']], ensure_ascii=False))
        print('REL', json.dumps(meanings['relations'], ensure_ascii=False), 'UNRESOLVED', json.dumps(meanings['unresolved'], ensure_ascii=False))
    print('TOTAL GROUPS', len(groups), 'subject', digest(ROOT / descriptions.DEFAULT_OUTPUT))


def acquisitions():
    result = descriptions.read_result(ROOT)
    source = json.loads((ROOT / result['input']['path']).read_text(encoding='utf-8'))
    groups = {}
    for item, origin in zip(result['items'], source['items']):
        if item['item_id'] != origin['item_id']:
            raise ValueError('item order differs')
        branches = [b for b in origin['blocks'] if b['class'] == 'acquisition']
        refs = {f['fact_ref'] for b in branches for branch in b['branches'] for f in branch['facts']}
        if not refs:
            continue
        from iris_tooling.domains.layer3 import acquisition_expression as acquisition
        facts = []
        for b in branches:
            for branch in b['branches']:
                for f in branch['facts']:
                    payload = f['payload']
                    route, c = payload['route'], payload['conditions']
                    if route['method'] in ('foraging', 'foraging_crop_seed'):
                        cats = c['category_conditions']
                        category_zones = {z for cat in cats.values() for z, w in acquisition.weights(cat['zoneChance']) if float(w) > 0}
                        facts.append({'method': route['method'], 'crop': route.get('crop_item'),
                            'zones': [z for z, w in acquisition.weights(c['zones']) if float(w) > 0 and z in category_zones],
                            'months': acquisition.array(c['months']), 'skill': c['skill'], 'outside': c['forceOutside'],
                            'recipes': acquisition.array(c['recipes']),
                            'natural': all(acquisition.array(cat['validFloors']) != ['ANY'] for cat in cats.values()),
                            'eligibility': c['eligibility'], 'seed_branch': c.get('seed_branch')})
                    else:
                        facts.append(payload)
        surfaces = {loc + '/' + depth: [s['text'] for s in item['locales'][loc][depth]['segments'] if refs.intersection(s['fact_refs'])]
                    for loc in ('ko', 'en') for depth in ('compact', 'expanded')}
        key = json.dumps([facts, surfaces], ensure_ascii=False, sort_keys=True)
        groups.setdefault(key, []).append(item['item_id'])
    start, end = map(int, sys.argv[2:4])
    for index, (key, ids) in enumerate(groups.items()):
        if start <= index < end:
            print('ROUTES', index, 'MEMBERS', ', '.join(ids), key)
    print('TOTAL ROUTE COMBINATIONS', len(groups))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        extract()
    elif sys.argv[1] == 'preserve':
        target = descriptions._path(ROOT, 'Iris/build/description/composition/quality_review/before.json')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as out:
            out.write((ROOT / descriptions.DEFAULT_OUTPUT).read_bytes())
        print(target)
    elif sys.argv[1] == 'generate':
        _, result = descriptions.produce(ROOT)
        print(descriptions.write_result(ROOT, result))
        print(json.dumps(result['summary'], ensure_ascii=False))
    elif sys.argv[1] == 'delta':
        delta()
    elif sys.argv[1] == 'coverage':
        coverage()
    elif sys.argv[1] == 'combinations':
        combinations()
    elif sys.argv[1] == 'acquisitions':
        acquisitions()
    else:
        show()
