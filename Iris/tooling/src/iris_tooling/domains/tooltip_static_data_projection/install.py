"""Tooltip-owned candidate assembly and recoverable, isolated installation.

Current activation belongs to the B/C joint adoption. These entry points build
and exercise the same two-file install unit without changing that current.
"""
import json
import os
from pathlib import Path
import shutil

from iris_tooling.domains.tooltip_t1.contract import canonical_bytes, sha256_bytes, sha256_file
from .contract import read_object, require
from .recipe_variants import (
    DATA_ROOT, OWNER_ROOT, VARIANTS_NAME, project_recipe_variants, read_static_data,
    variants_bytes, _runtime_rightclick_surfaces, load_contract,
    interaction_candidates, project_interaction_variants,
)
from .serialization import LUA_NAME, MANIFEST_NAME, RUN_RECEIPT, artifact_binding

OWNER_NAME = 'IrisTooltipOwner.json'
SCHEMA = 'iris-tooltip-product-v1'
FILES = (LUA_NAME, VARIANTS_NAME)


def local(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe Tooltip member')
    target = root / relative
    require(target.resolve().is_relative_to(root), 'Tooltip path escapes root')
    cursor = target
    while cursor != root:
        require(not cursor.is_symlink() and not cursor.is_junction(), 'Tooltip reparse path')
        cursor = cursor.parent
    return target


def build(root, t2_root, output):
    """Accept an actual T2 run and attach QG's single-interaction choices."""
    root, t2_root, output = Path(root).resolve(), Path(t2_root).resolve(), Path(output).resolve()
    require(not output.exists(), 'Tooltip candidate output already exists')
    receipt = read_object(t2_root / RUN_RECEIPT)
    manifest = read_object(t2_root / MANIFEST_NAME)
    raw = (t2_root / LUA_NAME).read_bytes()
    require(receipt['schema_version'] == 'iris-tooltip-t2-run-receipt-v1' and receipt['state'] == 'generated'
            and receipt['artifacts'] == {name: artifact_binding((t2_root / name).read_bytes())
                                        for name in (LUA_NAME, MANIFEST_NAME)}, 'T2 candidate member drift')
    require(manifest['t1_input'] == receipt['t1_input'] and receipt['t1_input'].get('s2_supply_sha256')
            and manifest['lua'] == {'file_name': LUA_NAME, **artifact_binding(raw)}, 'Tooltip requires admitted S2 T2 input')
    data = read_static_data(raw)
    contract, _ = load_contract(root)
    paths = [OWNER_ROOT / name for name in ('upstream_usecases_by_fulltype.json',
             'upstream_recipe_nav_registry.json', 'tooltip_t1_layer4_recipe_locale_owner_input.json',
             'evolved_recipe_owner.b41.json')]
    if 'candidate_subject_sha256' in receipt['t1_input']:
        rows = [{'full_type': key, 'slots': [
            {'slot_id': line['slot_id'], 'semantic_identity': line['semantic_identity'],
             'localized_surfaces': {loc: data[key][loc][i] for loc in ('ko', 'en')}}
            for i, line in enumerate(record['lines'])]} for key, record in manifest['fulltypes'].items()]
        variants = project_interaction_variants(data, rows, interaction_candidates(root, data))
    else:
        usecases, navigation, locales = [json.loads((root / p).read_bytes()) for p in paths[:3]]
        variants = project_recipe_variants(data, usecases['fulltypes'], navigation['entries'], locales['entries'],
                                          _runtime_rightclick_surfaces(root), contract)
    files = {LUA_NAME: raw, VARIANTS_NAME: variants_bytes(variants)}
    # Bind the staged runtime and Menu, so stale source cannot enter packaging.
    sources = {p.relative_to(root).as_posix(): sha256_file(p)
               for p in sorted((root / 'Iris/media').rglob('*')) if p.is_file()}
    sources.update({p.as_posix(): sha256_file(root / p) for p in paths})
    producer_paths = [
        'Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/' + name
        for name in ('install.py', 'recipe_variants.py', 'serialization.py')
    ] + ['Iris/tools/' + name for name in ('package_iris.ps1', 'Layer3PackageProjection.psm1', 'RuntimeLookupIndexIdentity.psm1')]
    sources.update({p: sha256_file(root / p) for p in producer_paths})
    identity = {'t2_receipt_sha256': sha256_file(t2_root / RUN_RECEIPT),
                't1_input': receipt['t1_input'], 'sources': sources,
                'files': {name: sha256_bytes(value) for name, value in files.items()}}
    owner = {'schema_version': SCHEMA, 'owner': 'Tooltip',
             'product_id': 'ttp-' + sha256_bytes(canonical_bytes(identity)), 'identity_json': canonical_bytes(identity).decode('utf-8'),
             'files': identity['files'],
             'predecessor_facades': {name: sources[(DATA_ROOT / name).as_posix()] for name in FILES}}
    output.mkdir(parents=True)
    for name, value in files.items():
        (output / name).write_bytes(value)
    (output / OWNER_NAME).write_bytes(canonical_bytes(owner))
    return owner


def admit(candidate):
    candidate = Path(candidate).resolve()
    owner = read_object(local(candidate, OWNER_NAME))
    identity = json.loads(owner['identity_json'])
    require(owner['schema_version'] == SCHEMA and owner['owner'] == 'Tooltip'
            and owner['identity_json'].encode('utf-8') == canonical_bytes(identity)
            and owner['product_id'] == 'ttp-' + sha256_bytes(canonical_bytes(identity))
            and owner['files'] == identity['files'] and set(owner['files']) == set(FILES)
            and owner['predecessor_facades'] == {name: identity['sources'][(DATA_ROOT / name).as_posix()] for name in FILES},
            'Tooltip owner identity mismatch')
    require({p.name for p in candidate.iterdir()} == {*FILES, OWNER_NAME}, 'Tooltip candidate membership mismatch')
    for name, digest in owner['files'].items():
        require(sha256_file(local(candidate, name)) == digest, 'Tooltip member hash mismatch: ' + name)
    return owner


def atomic_write(path, raw):
    pending = path.with_name(path.name + '.stage')
    require(not pending.exists(), 'unfinished Tooltip write')
    with pending.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(pending, path)


def recover(repository, journal):
    state = read_object(local(journal, 'transaction.json'))
    target = local(repository, state['target'])
    require(target.is_relative_to(Path(repository).resolve() / '.tmp'), 'rollback outside isolated workspace')
    if state['state'] == 'rolled_back':
        return state['state']
    lock = local(target, 'IrisTooltip.lock')
    if state['state'] != 'complete' or lock.exists():
        require(read_object(lock) == {'journal': str(Path(journal).resolve()), 'product_id': state['product_id']},
                'Tooltip rollback writer lock mismatch')
    for index, entry in reversed(list(enumerate(state['members']))):
        path = local(target, entry['name'])
        actual = sha256_file(path) if path.exists() else None
        require(actual in (entry['before'], entry['after']), 'Tooltip rollback concurrent writer')
        pending = path.with_name(path.name + '.stage')
        if pending.exists():
            # A killed writer can leave incomplete staged bytes. The exclusive
            # journal lock and unchanged current member own this pending path.
            require(lock.exists(), 'unowned pending Tooltip write')
            pending.unlink()
        if entry['before'] is None:
            if path.exists():
                path.unlink()
        else:
            raw = local(journal, str(index)).read_bytes()
            require(sha256_bytes(raw) == entry['before'], 'Tooltip rollback backup mismatch')
            atomic_write(path, raw)
    state['state'] = 'rolled_back'
    atomic_write(Path(journal) / 'transaction.json', canonical_bytes(state))
    if lock.exists():
        lock.unlink()
    return state['state']


def install(repository, candidate, isolated_root, journal, *, interrupt_after=None):
    repository, isolated_root, journal = map(lambda p: Path(p).resolve(), (repository, isolated_root, journal))
    require(isolated_root.is_relative_to(repository / '.tmp') and journal.is_relative_to(repository / '.tmp'),
            'B install is isolated; current activation requires joint B/C adoption')
    local(repository, isolated_root.relative_to(repository))
    local(repository, journal.relative_to(repository))
    owner = admit(candidate)
    target = isolated_root / DATA_ROOT
    require(target.is_dir() and not journal.exists(), 'isolated runtime/journal boundary invalid')
    lock = local(target, 'IrisTooltip.lock')
    require(not lock.exists(), 'Tooltip writer locked; recover its journal first')
    for relative, digest in json.loads(owner['identity_json'])['sources'].items():
        if relative.startswith('Iris/media/'):
            require(sha256_file(local(isolated_root, relative)) == digest, 'isolated runtime/source drift: ' + relative)
    names = [*FILES, OWNER_NAME]
    journal.mkdir(parents=True)
    entries = []
    for index, name in enumerate(names):
        path = local(target, name)
        before = path.read_bytes() if path.exists() else None
        if before is not None:
            (journal / str(index)).write_bytes(before)
        entries.append({'name': name, 'before': sha256_bytes(before) if before is not None else None,
                        'after': sha256_file(local(candidate, name))})
    state = {'state': 'prepared', 'target': target.relative_to(repository).as_posix(),
             'product_id': owner['product_id'], 'members': entries}
    (journal / 'transaction.json').write_bytes(canonical_bytes(state))
    with lock.open('xb') as stream:
        stream.write(canonical_bytes({'journal': str(journal), 'product_id': owner['product_id']}))
    try:
        for index, name in enumerate(names):
            path = local(target, name)
            require((sha256_file(path) if path.exists() else None) == entries[index]['before'], 'Tooltip concurrent writer')
            atomic_write(path, local(candidate, name).read_bytes())
            if interrupt_after == index + 1:
                raise RuntimeError('injected Tooltip interruption')
    except BaseException:
        recover(repository, journal)
        raise
    state['state'] = 'complete'
    atomic_write(journal / 'transaction.json', canonical_bytes(state))
    lock.unlink()
    return owner['product_id']


def stage(repository, candidate, output):
    repository, output = Path(repository).resolve(), Path(output).resolve()
    require(output.is_relative_to(repository / '.tmp') and not output.exists(), 'new isolated staging root required')
    local(repository, output.relative_to(repository))
    owner = admit(candidate)
    for relative, digest in json.loads(owner['identity_json'])['sources'].items():
        require(sha256_file(local(repository, relative)) == digest, 'Tooltip candidate/source drift: ' + relative)
    shutil.copytree(repository / 'Iris/media', output / 'Iris/media')
    for name in ('mod.info', 'poster.png'):
        if (repository / 'Iris' / name).exists():
            shutil.copyfile(repository / 'Iris' / name, output / 'Iris' / name)
    (output / 'Iris/tools').mkdir()
    for name in ('package_iris.ps1', 'Layer3PackageProjection.psm1', 'RuntimeLookupIndexIdentity.psm1'):
        shutil.copyfile(repository / 'Iris/tools' / name, output / 'Iris/tools' / name)
    return install(repository, candidate, output, output / 'journal')
