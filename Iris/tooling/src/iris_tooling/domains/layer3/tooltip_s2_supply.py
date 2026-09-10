"""Supply accepted description strings to Tooltip; never assemble product rows.

The payload is an offline input. Its exact canonical bytes are retained inside
the strict T1 subject, so an ephemeral input path is not a durable readpoint.
"""
from copy import deepcopy
import json
from pathlib import Path

from . import description_composition_results as descriptions
from . import description_composition_model as description_model
from iris_tooling.domains.tooltip_t1.contract import (
    canonical_bytes, fulltype_set_sha256, git_subject, parse_classifications,
    sha256_bytes, sha256_file, validate_layer3_owner_output,
)
from iris_tooling.domains.tooltip_t1.models import TooltipContractError

DESCRIPTION = {
    'path': descriptions.DEFAULT_OUTPUT,
    'sha256': 'ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0',
}
SCHEMA = 'iris-tooltip-s2-supply-v2'
STATES = {'present', 'absent', 'out_of_dvf_target'}
OWNER = 'Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json'
CONTRACT = 'Iris/_docs/authority/tooltip_t1/s2_supply_contract.json'


def require(condition, message):
    if not condition:
        raise TooltipContractError(message)


def current_support(root):
    """Reconcile the ratified predicate with the sealed T1 handoff, not Lua keys."""
    from iris_tooling.domains.tooltip_static_data_projection.contract import load_contract, read_handoff
    from iris_tooling.domains.tooltip_t1.audit import CLASSIFICATIONS, L3_POINTER, L3_GENERATIONS, L4_OWNER_INPUT, _generation_id
    from iris_tooling.domains.classification.layer2_validator import validate_owner_output
    from iris_tooling.domains.tooltip_t1.contract import validate_contracts, DECISION_CONTRACT
    validate_owner_output(root)
    validate_contracts(root, sha256_file(root / DECISION_CONTRACT))
    route = json.loads((root / 'Iris/_docs/authority/iris_current_route_index.json').read_bytes())
    locator = route['tooltip_t1_production_handoff']
    # This is consumption of the explicit legacy locator, not a new T2 output.
    handoff_root = Path(locator['final_root']).resolve()
    require(handoff_root.is_relative_to(root), 'admitted input outside selected repository')
    contract, _ = load_contract(root)
    accepted = read_handoff(handoff_root, locator, support_count=contract['support_count'],
                            support_sha256=contract['support_sha256'])
    generation = _generation_id((root / L3_POINTER).read_text(encoding='utf-8'))
    rendered_path = L3_GENERATIONS / generation / 'dvf_3_3_rendered.json'
    rendered = json.loads((root / rendered_path).read_bytes())
    descriptor = json.loads((root / L3_GENERATIONS / generation / 'generation_descriptor.json').read_bytes())
    rendered_ref = next(r for r in descriptor['outputs'] if r['path'] == rendered_path.name)
    require(descriptor['generation_id'] == generation
            and sha256_file(root / rendered_path) == rendered_ref['raw_byte_sha256'], 'current generation/rendered drift')
    layer4 = json.loads((root / L4_OWNER_INPUT).read_bytes())
    predicate = set(parse_classifications(root / CLASSIFICATIONS)) | set(rendered['entries']) | set(layer4['fulltypes'])
    require(predicate == {r['full_type'] for r in accepted.rows}, 'ratified predicate/admitted support mismatch')
    paths = [CLASSIFICATIONS, L3_POINTER, rendered_path, L4_OWNER_INPUT, Path(OWNER)]
    sources = {p.as_posix(): sha256_file(root / p) for p in paths}
    return accepted, generation, sources


def build(root, description_ref=None):
    root = Path(root).resolve()
    ref = description_ref or DESCRIPTION
    path = (root / ref['path']).resolve()
    require(path.is_relative_to(root / 'Iris/build/description/composition'), 'description outside corpus directory')
    require(sha256_file(path) == ref['sha256'], 'description bytes changed')
    corpus = descriptions.read_result(root, ref['path'])
    semantic = corpus['input']
    semantic_path = (root / semantic['path']).resolve()
    require(semantic_path == root / 'Iris/build/description/composition/blocks.json', 'unexpected semantic input')
    require(sha256_file(semantic_path) == semantic['sha256'], 'description semantic input drift')
    accepted, generation, sources = current_support(root)
    owner = json.loads((root / OWNER).read_bytes())
    _, absences = validate_layer3_owner_output(owner, expected_generation_id=generation)
    items = {i['item_id']: i for i in corpus['items']}
    support = {r['full_type'] for r in accepted.rows}
    require(set(absences) == support - items.keys(), 'T-D owner absence missing/extra')
    records = {}
    for key in sorted(support):
        if key not in items:
            records[key] = {'state': 'out_of_dvf_target', 'locales': None,
                            'owner_absence': deepcopy(absences[key])}
            continue
        item = items[key]
        locales = {loc: deepcopy(item['locales'][loc]['compact']) for loc in ('ko', 'en')}
        states = {view['state'] for view in locales.values()}
        require(len(states) == 1 and states <= {'present', 'absent'}, 'failed or inconsistent compact state')
        records[key] = {'state': next(iter(states)), 'locales': locales,
                        'details': {loc: deepcopy(item['locales'][loc]['expanded']) for loc in ('ko', 'en')},
                        'qualifiers': deepcopy(item['qualifiers']),
                        'relations': deepcopy(item['relations']),
                        'unresolved_relations': deepcopy(item['unresolved_relations'])}
    subject = git_subject(root)
    policy = json.loads((root / CONTRACT).read_bytes())
    require(policy['supply_schema'] == SCHEMA and set(policy['states']) == STATES
            and policy['support_predicate'] == 'current-owner-fulltype-union-v1'
            and policy['body_rewrite_allowed'] is False and policy['absence_fallback_allowed'] is False,
            'S2 successor contract mismatch')
    payload = {'schema_version': SCHEMA, 'binding': {
        'contract': {'path': CONTRACT, 'sha256': sha256_file(root / CONTRACT)},
        'expression': ref, 'semantic': {'path': semantic['path'], 'sha256': semantic['sha256']},
        'support': accepted.binding, 'target_ids': sorted(items),
        'target_sha256': fulltype_set_sha256(items),
        'outside_support': sorted(items.keys() - support),
        'absence_sha256': sha256_bytes(canonical_bytes(absences)),
        'sources': sources, 'producer': {
            'commit': subject['commit'], 'tree': subject['tree'],
            'files': {p: sha256_file(root / p) for p in (
                'Iris/tooling/src/iris_tooling/domains/layer3/description_composition_results.py',
                'Iris/tooling/src/iris_tooling/domains/layer3/description_composition_model.py',
                'Iris/tooling/src/iris_tooling/domains/layer3/tooltip_s2_supply.py')},
        },
    }, 'records': records}
    validate(payload)
    return payload


def validate(payload):
    require(payload.get('schema_version') == SCHEMA and set(payload) == {'schema_version', 'binding', 'records'},
            'S2 supply schema mismatch')
    binding, records = payload['binding'], payload['records']
    for name in ('contract', 'expression', 'semantic'):
        ref = binding[name]
        require(isinstance(ref['path'], str) and ref['path'] and len(ref['sha256']) == 64,
                'missing S2 source binding: ' + name)
    support = binding['support']
    require(len(records) == support['support_count']
            and fulltype_set_sha256(records) == support['support_sha256'], 'S2 supply support mismatch')
    targets = binding['target_ids']
    require(targets == sorted(set(targets)) and fulltype_set_sha256(targets) == binding['target_sha256'],
            'S2 target identity mismatch')
    require(binding['outside_support'] == sorted(set(targets) - records.keys()), 'S2 outside support mismatch')
    absences, items = {}, []
    from collections import Counter
    states = Counter()
    for key, row in records.items():
        require(row['state'] in STATES, 'unknown S2 disposition')
        if row['state'] == 'out_of_dvf_target':
            require(key not in targets and row['locales'] is None
                    and row['owner_absence']['exact_full_type'] == key
                    and row['owner_absence']['applicable_scope'] == key
                    and row['owner_absence']['disposition'] == 'approved_legitimate_absence', 'unbound outside-target absence')
            absences[key] = row['owner_absence']
            continue
        require(key in targets and set(row['locales']) == set(row['details']) == {'ko', 'en'}, 'S2 target/locale missing')
        item = {'item_id': key, 'qualifiers': row['qualifiers'], 'relations': row['relations'],
                'unresolved_relations': row['unresolved_relations'], 'locales': {}}
        for loc, view in row['locales'].items():
            require(view['state'] == row['state'] and '\n' not in view['text'] and '\r' not in view['text'],
                    'malformed compact state/text')
            require('detail_links' in view and all(isinstance(segment.get('qualifier_dispositions', []), list)
                                                  for segment in view['segments']),
                    'compact detail/qualifier links missing')
            item['locales'][loc] = {'compact': view, 'expanded': row['details'][loc]}
            for surface, value in item['locales'][loc].items():
                require(value['state'] != 'failed', 'failed description supplied')
                states[f"{loc}/{surface}/{value['state']}"] += 1
        items.append(item)
    description_model.validate_result({'schema': description_model.SCHEMA, 'version': description_model.VERSION,
        'input': binding['semantic'], 'producer': binding['producer'], 'items': items,
        'summary': {'targets': len(items), 'surfaces': sum(states.values()), 'states': dict(sorted(states.items()))}})
    require(sha256_bytes(canonical_bytes(absences)) == binding['absence_sha256'], 'S2 absence provenance drift')


def load(root, path, expected_sha256):
    raw = Path(path).read_bytes()
    require(sha256_bytes(raw) == expected_sha256, 'S2 supply input bytes changed')
    payload = json.loads(raw)
    require(canonical_bytes(payload) == raw, 'noncanonical S2 supply')
    validate(payload)
    require(payload == build(root, payload['binding']['expression']), 'S2 supply/source identity drift')
    return {'sha256': expected_sha256, 'payload': payload}


def validate_embedded(value):
    require(set(value) == {'sha256', 'payload'}
            and sha256_bytes(canonical_bytes(value['payload'])) == value['sha256'], 'durable S2 supply hash mismatch')
    validate(value['payload'])
    return value['payload']


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    root, output = args.repository_root.resolve(), args.output.resolve()
    require(output.is_relative_to(root / '.tmp') and not output.exists(), 'new repository-local supply output required')
    payload = build(root)
    raw = canonical_bytes(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(raw)
    print(json.dumps({'path': str(output), 'sha256': sha256_bytes(raw), 'records': len(payload['records'])}))


if __name__ == '__main__':
    main()
