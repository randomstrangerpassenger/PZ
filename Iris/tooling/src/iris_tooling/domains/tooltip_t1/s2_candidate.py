"""Four-role candidate admission from an already admitted T1 support baseline.

This is a pre-activation product route, not a D6 re-adoption or a synthetic
final closeout. S1 retains its admitted identity and surfaces; S3/S4 use v3 roles.
Dirty checkouts are bound by actual input/producer bytes, never called clean.
"""
from copy import deepcopy
import json
from pathlib import Path

from iris_tooling.domains.layer3 import tooltip_s2_supply as supply
from . import audit
from .contract import canonical_bytes, sha256_bytes, sha256_file, git_subject
from .models import validate_handoff_row, SemanticSlotState

SCHEMA = 'iris-tooltip-s2-candidate-v2'
SUBJECT = 'subject_binding.json'
ROWS = 't2_handoff_input.jsonl'
RECEIPT = 'run_receipt.json'


def workspace(root, path):
    from iris_tooling.domains.tooltip_static_data_projection.install import local
    root, path = Path(root).resolve(), Path(path).resolve()
    supply.require(path.is_relative_to(root / '.tmp/tooltip') and path != root / '.tmp/tooltip',
                   'S2 candidate requires an isolated .tmp/tooltip child')
    return local(root, path.relative_to(root))


def source_binding(root):
    """Bind this producer, its actual inputs, runtime and packaging dependencies."""
    generation = audit._generation_id((root / audit.L3_POINTER).read_text(encoding='utf-8'))
    files = audit._source_hashes(root, generation)
    directories = ['Iris/media', 'Iris/tooling/src/iris_tooling/domains/' + 'tooltip_t1',
                   'Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection',
                   'Iris/tooling/src/iris_tooling/domains/layer3',
                   'Iris/tooling/src/iris_tooling/domains/classification',
                   'Iris/tooling/src/iris_tooling/domains/layer4',
                   'Iris/_docs/authority/tooltip_t1', 'Iris/_docs/authority/tooltip_t2',
                   'Iris/_docs/authority/tooltip_static_data_projection']
    for directory in directories:
        for path in sorted((root / directory).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                files[path.relative_to(root).as_posix()] = sha256_file(path)
    for name in ('Layer3PackageProjection.psm1', 'RuntimeLookupIndexIdentity.psm1', 'package_iris.ps1'):
        files['Iris/tools/' + name] = sha256_file(root / 'Iris/tools' / name)
    for name in ('upstream_recipe_nav_registry.json', 'evolved_recipe_owner.b41.json'):
        path = 'Iris/build/description/v2/data/' + name
        files[path] = sha256_file(root / path)
    for name in ('descriptions.json', 'blocks.json'):
        path = 'Iris/build/description/composition/' + name
        files[path] = sha256_file(root / path)
    return files


def acquisition_places(root):
    """Tooltip's place-only projection of accepted acquisition facts.

    A route with no place is absent here, not absent from Menu's expanded view.
    No procedure, chance, recommendation or guessed location is introduced.
    """
    import re
    from iris_tooling.domains.layer3 import composition_results
    from iris_tooling.domains.layer3.acquisition_expression import locations, ZONES
    semantic = composition_results.read_result(root)
    result = {}
    for item in semantic['items']:
        places, refs = {'ko': [], 'en': []}, []
        for block in item['blocks']:
            for branch in block['branches']:
                for fact in branch['facts']:
                    if fact['fact_kind'] != 'acquisition':
                        continue
                    payload = fact['payload']
                    method = payload['route']['method']
                    if method in {'foraging', 'foraging_crop_seed'}:
                        pair = {loc: ('채집: ' if loc == 'ko' else 'Foraging: ') + locations(payload, loc) for loc in places}
                    elif method == 'trapping':
                        zones = sorted(re.fullmatch(r'\.zone\["([^"]+)"\]', k)[1]
                            for k, value in payload['conditions']['definition'].items()
                            if k.startswith('.zone[') and float(value) > 0)
                        supply.require(zones and all(z in ZONES for z in zones), 'unknown trapping place')
                        pair = {loc: ('덫: ' if loc == 'ko' else 'Trapping: ') + ', '.join(
                            ZONES[z][0 if loc == 'ko' else 1] for z in zones) for loc in places}
                    elif method == 'fishing':
                        pair = {'ko': '낚시: 물가', 'en': 'Fishing: water'}
                    else:
                        continue
                    refs.append(fact['fact_ref'])
                    for loc in places:
                        if pair[loc] not in places[loc]:
                            places[loc].append(pair[loc])
        result[item['item_id']] = {'fact_refs': sorted(refs),
            'locales': {loc: ' / '.join(values) for loc, values in places.items()},
            'reason': None if refs else 'no accepted acquisition place'}
    return result


def candidate_rows(before, embedded, places, pools):
    rows = []
    for prior in before.rows:
        key = prior['full_type']
        # Preserve classification exactly. Historical S3/S4 are both L4 and
        # must not be copied into the new acquisition/one-interaction mapping.
        slots = [deepcopy(s) for s in prior['slots'] if s['slot_id'] == 'S1']
        s2 = audit._slot_supplied_s2(key, embedded)
        if s2.semantic_state == SemanticSlotState.SELECTED:
            slots.append({'slot_id': 'S2', 'semantic_identity': s2.semantic_identity,
                          'localized_surfaces': s2.localized_surfaces})
        place = places.get(key)
        if place and place['fact_refs']:
            slots.append({'slot_id': 'S3', 'semantic_identity': 'acquisition:' + sha256_bytes(canonical_bytes(place)),
                          'localized_surfaces': place['locales']})
        if pools[key]:
            first = pools[key][0]
            slots.append({'slot_id': 'S4', 'semantic_identity': first['id'],
                          'localized_surfaces': {loc: first[loc] for loc in ('ko', 'en')}})
        row = {**prior, 'slots': slots}
        validate_handoff_row(row)
        rows.append(row)
    return rows


def build(root, output):
    from iris_tooling.domains.tooltip_static_data_projection.contract import load_contract
    from iris_tooling.domains.tooltip_static_data_projection.projection import project
    from iris_tooling.domains.tooltip_static_data_projection.recipe_variants import DATA_ROOT, read_static_data
    root = Path(root).resolve()
    output = workspace(root, output)
    supply.require(not output.exists(), 'S2 candidate output already exists')
    sources = source_binding(root)
    payload = supply.build(root)
    before, _, _ = supply.current_support(root)
    contract, _ = load_contract(root)
    baseline, _, _ = project(before, contract)
    supply.require(baseline == read_static_data((root / DATA_ROOT / 'IrisTooltipStaticData.lua').read_bytes()),
                   'S2-only admission requires the admitted baseline static data')
    embedded = {'sha256': sha256_bytes(canonical_bytes(payload)), 'payload': payload}
    from iris_tooling.domains.tooltip_static_data_projection.recipe_variants import interaction_candidates
    places = acquisition_places(root)
    pools = interaction_candidates(root, payload['records'])
    rows = candidate_rows(before, embedded, places, pools)
    subject = {'schema_version': SCHEMA, 'git': git_subject(root), 'source_sha256': sources,
               'baseline': before.binding, 's2_supply': embedded,
               'acquisition_places': places, 'interactions': pools}
    subject_raw = canonical_bytes(subject)
    rows_raw = b''.join(canonical_bytes(row) for row in rows)
    receipt = {'schema_version': SCHEMA, 'state': 'candidate',
               'artifacts': {SUBJECT: sha256_bytes(subject_raw), ROWS: sha256_bytes(rows_raw)},
               'current_activation': 'deferred', 'pz_validation': 'unvalidated'}
    supply.require(sources == source_binding(root), 'S2 candidate source mutation')
    # Validate before publishing any member. The same decoder is used by T2.
    _decode(subject, rows, receipt, subject_raw, rows_raw, contract, before=before)
    output.mkdir(parents=True)
    (output / SUBJECT).write_bytes(subject_raw)
    (output / ROWS).write_bytes(rows_raw)
    (output / RECEIPT).write_bytes(canonical_bytes(receipt))
    return receipt


def _decode(subject, rows, receipt, subject_raw, rows_raw, contract, *, before):
    from iris_tooling.domains.tooltip_static_data_projection.contract import AcceptedInput, validate_supply_rows
    supply.require(subject['schema_version'] == receipt['schema_version'] == SCHEMA
                   and receipt['state'] == 'candidate'
                   and receipt['artifacts'] == {SUBJECT: sha256_bytes(subject_raw), ROWS: sha256_bytes(rows_raw)},
                   'S2 candidate member binding mismatch')
    supply.require(subject['baseline'] == before.binding, 'S2 candidate baseline binding mismatch')
    supply.require([r['full_type'] for r in rows] == [r['full_type'] for r in before.rows],
                   'S2 candidate exact support/order mismatch')
    validate_supply_rows(subject['s2_supply'], rows)
    supply.require(rows == candidate_rows(before, subject['s2_supply'], subject['acquisition_places'], subject['interactions']),
                   'candidate owner/role mapping drift')
    return AcceptedInput(tuple(rows), {
        'subject': {k: subject['git'][k] for k in ('commit', 'tree')},
        'candidate_subject_sha256': sha256_bytes(subject_raw),
        'artifact_sha256': receipt['artifacts'],
        'authority_contract_bundle_sha256': before.binding['authority_contract_bundle_sha256'],
        'support_count': contract['support_count'], 'support_sha256': contract['support_sha256'],
        's2_supply_sha256': subject['s2_supply']['sha256'],
        'description': subject['s2_supply']['payload']['binding']['expression'],
    })


def admit(root, candidate, receipt_sha256):
    from iris_tooling.domains.tooltip_static_data_projection.contract import read_object, load_contract
    root = Path(root).resolve()
    candidate = workspace(root, candidate)
    supply.require({p.name for p in candidate.iterdir()} == {SUBJECT, ROWS, RECEIPT}, 'S2 candidate membership mismatch')
    supply.require(sha256_file(candidate / RECEIPT) == receipt_sha256, 'S2 candidate receipt hash mismatch')
    subject, receipt = read_object(candidate / SUBJECT), read_object(candidate / RECEIPT)
    supply.require(subject['source_sha256'] == source_binding(root), 'S2 candidate source drift')
    supply.require(subject['git'] == git_subject(root), 'S2 candidate working subject drift')
    before, _, _ = supply.current_support(root)
    from iris_tooling.domains.tooltip_static_data_projection.recipe_variants import interaction_candidates
    supply.require(subject['acquisition_places'] == acquisition_places(root)
                   and subject['interactions'] == interaction_candidates(root, subject['s2_supply']['payload']['records']),
                   'candidate acquisition/interaction owner drift')
    contract, _ = load_contract(root)
    raw = (candidate / ROWS).read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    supply.require(raw == b''.join(canonical_bytes(row) for row in rows), 'S2 candidate noncanonical rows')
    return _decode(subject, rows, receipt, (candidate / SUBJECT).read_bytes(), raw, contract, before=before)
