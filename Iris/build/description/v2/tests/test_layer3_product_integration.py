"""The required product contract: canonical expanded C and accepted B together."""
from collections import Counter
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

import pytest

from iris_tooling.domains.layer3 import product_projection as product
from iris_tooling.domains.layer3 import product_install as install

ROOT = Path(__file__).resolve().parents[5]


def command(argv, cwd, checkpoint, product_id):
    print(f'{checkpoint}: candidate={product_id} command={subprocess.list2cmdline(argv)}', flush=True)
    # One shared stream, bounded children, and progress visible while running.
    with subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
        started = time.monotonic()
        while True:
            try:
                output, _ = process.communicate(timeout=30)
                break
            except subprocess.TimeoutExpired:
                elapsed = time.monotonic() - started
                print(f'{checkpoint}: running pid={process.pid} elapsed={elapsed:.0f}s candidate={product_id}', flush=True)
                if elapsed > 240:
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
                    output, _ = process.communicate()
                    pytest.fail(f'{checkpoint}: TIMEOUT candidate={product_id} command={argv!r}\n{output[-12000:]!r}', pytrace=False)
    print(output.decode('utf-8', errors='replace')[-12000:], flush=True)
    print(f'{checkpoint}: exit={process.returncode} candidate={product_id}', flush=True)
    assert process.returncode == 0, f'{checkpoint}: command={argv!r} exit={process.returncode}'
    return output


def test_product_contract(tmp_path, monkeypatch):
    candidate_zip = os.environ.get('IRIS_MENU_TOOLTIP_CANDIDATE')
    if candidate_zip:
        monkeypatch.setattr(product, 'ACCEPTED_TOOLTIP', product.binding(ROOT, candidate_zip))
        monkeypatch.setattr(product, 'ACCEPTED_DESCRIPTION', product.DESCRIPTION)
    # pytest's nested directory is deliberately not used for generation paths.
    # This same execution boundary owns two products, one stage and one ZIP.
    parent = ROOT / '.tmp/menu'
    parent.mkdir(parents=True, exist_ok=True)
    import tempfile
    resume = os.environ.get('IRIS_MENU_RESUME_PACKAGE')
    workspace = Path(resume).resolve() if resume else Path(tempfile.mkdtemp(prefix='run-', dir=parent))
    assert workspace.is_relative_to(parent.resolve())
    print(f'workspace={workspace}', flush=True)
    before = (ROOT / product.DATA_ROOT / 'IrisLayer3DataCurrent.lua').read_bytes()
    payload, blocks = product.read_menu_inputs(ROOT)
    accepted, owner = product.accepted_tooltip(ROOT)
    assert len(payload['items']) == 2105
    states = Counter(row['locales'][lang]['expanded']['state'] for row in payload['items'] for lang in product.LOCALES)
    assert states == {'present': 3952, 'absent': 258}
    for lang in product.LOCALES:
        assert sum(r['locales'][lang]['compact']['state']=='absent' and r['locales'][lang]['expanded']['state']=='present' for r in payload['items']) == 0
        assert sum(r['locales'][lang]['expanded']['state']=='absent' for r in payload['items']) == 129
    print('input: states=4210 present=3952 absent=258 acquisition supplied separately', flush=True)
    first, second = workspace / 'a', workspace / 'b'
    manifest = install.admit(first) if resume else product.build_menu_product(ROOT, first)
    other = install.admit(second) if resume else product.build_menu_product(ROOT, second)
    if resume:
        # Explicit continuation of this exact candidate, not a reusable PASS
        # receipt. The caller reports the earlier command's completed stages.
        for ref in manifest['identity']['owners'] + manifest['identity']['producer']:
            assert product.binding(ROOT, ref['path']) == ref
        print('resume: existing product/stage; rerun model and package, reuse completed syntax', flush=True)
    pid = manifest['product_id']
    assert manifest == other and install.inventory(first) == install.inventory(second)
    menu, trace = product.expanded_projection(payload, blocks)
    assert trace == manifest['menu']
    source = {r['item_id']: r for r in payload['items']}
    multi = []
    for key, row in source.items():
        assert trace[key]['source'] == row  # Includes all scopes, unresolved and optional metadata.
        for lang in product.LOCALES:
            expected = row['locales'][lang]['expanded']
            actual = menu[key][lang]
            assert actual['text'] == expected['text'] and actual['blocks'] == [s['text'] for s in expected['segments']]
            covered = []
            for unit in actual['units']:
                positions = list(range(unit['first_segment']-1, unit['last_segment']))
                covered.extend(positions)
                assert unit['text'] == ' '.join(expected['segments'][i]['text'] for i in positions)
            assert covered == list(range(len(expected['segments'])))
            for link in trace[key]['locales'][lang]['detail_links']:
                unit = actual['units'][link['unit']-1]
                assert link['runtime_segment'] == link['segment']+1
                assert unit['first_segment'] <= link['runtime_segment'] <= unit['last_segment']
            if any(len(s['branch_refs']) > 1 for s in expected['segments']):
                multi.append(key)
    # Public-use selection may make the fuel overview the first standalone unit.
    # Source segment coverage and relation-aware cuts are checked above.
    assert len(menu['Base.Plank']['ko']['units']) > 1
    assert len(menu['Base.Lipstick']['ko']['units']) == 2
    assert len(menu['Base.Socks_Ankle']['ko']['units']) == 4
    # Optional dispositions are not required by the reader or projection.
    optional = deepcopy(payload)
    for row in optional['items']:
        for loc in row['locales'].values():
            for surface in loc.values():
                for segment in surface['segments']:
                    segment.pop('qualifier_dispositions', None)
    assert product.expanded_projection(optional, blocks)[0] == menu
    print(f'conservation: product={pid} states=4210 refs/scopes/order/detail-links retained; two builds byte-equal', flush=True)
    stage = workspace / 's'
    if not resume:
        install.stage(ROOT, first, stage)
    for name in manifest['b_preserved']:
        assert (stage / name).read_bytes() == accepted[name]
    assert json.loads((stage / product.DATA_ROOT / 'IrisTooltipOwner.json').read_bytes()) == owner
    print(f'stage-b-identity: product={pid} preserved={len(manifest["b_preserved"])}', flush=True)
    samples = ['Base.Plank', 'Base.Lipstick', 'Base.Baseball', 'Base.BackgammonBoard', 'Base.Hammer']
    samples += [max(menu, key=lambda k: len(menu[k]['en']['text'])), multi[0]]
    fixture = workspace / 'menu.lua'
    fixture.write_bytes(product.table_bytes({'product_id':pid, 'menu':menu, 'samples':sorted(set(samples))}))
    static = product.read_static_data(accepted[(product.DATA_ROOT / 'IrisTooltipStaticData.lua').as_posix()])
    b_fixture = workspace / 'tooltip.lua'
    b_fixture.write_bytes(product.table_bytes(static))
    lua = shutil.which('lua')
    assert lua, 'BLOCKED: Lua runtime unavailable'
    syntax = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command',
              '& .\\tools\\check_lua_syntax.ps1 -Roots @("Iris/media/lua", "' + (stage / 'Iris/media/lua').relative_to(ROOT).as_posix() + '")']
    harness = str(ROOT / 'Iris/test/lua/detail_view_model_locale_harness.lua')
    if not resume:
        command(syntax, ROOT, 'lua-syntax', pid)
    command([lua, harness, str(stage), 'expanded', str(fixture)], ROOT, 'lua-model', pid)
    command([lua, str(ROOT / 'Iris/test/lua/tooltip_static_data_runtime_harness.lua'), str(stage), 'supply', str(b_fixture)], ROOT, 'b-runtime', pid)
    command([lua, str(ROOT / 'Iris/test/lua/browser_interaction_density_acceptance_harness.lua'), str(stage)], ROOT, 'l4-model', pid)
    # Mutate and restore this stage in one package-admission invocation. These
    # are fault fixtures, never candidate output or owner observation evidence.
    admission = r'''
$ErrorActionPreference = 'Stop'
Import-Module '__MODULE__'
$data = '__DATA__'
$base = Join-Path $data 'IrisLayer3ProductGenerations'
function Reject([scriptblock]$Action, [string]$Reason) {
    try { & $Action; throw 'fixture_was_accepted' }
    catch { if ($_.Exception.Message -notlike ('*' + $Reason + '*')) { throw }; Write-Output ('rejected: ' + $Reason) }
}
$file = Join-Path $data 'IrisTooltipStaticData.lua'
$raw = [IO.File]::ReadAllBytes($file)
try { [IO.File]::WriteAllBytes($file, [byte[]](1,2,3)); Reject { Get-IrisProductDescriptor -DataRoot $data } 'tooltip_member_hash_mismatch' }
finally { [IO.File]::WriteAllBytes($file, $raw) }
$file = Join-Path $data 'IrisTooltipOwner.json'
$raw = [IO.File]::ReadAllBytes($file)
try { $owner = [Text.Encoding]::UTF8.GetString($raw) | ConvertFrom-Json; $owner.product_id = 'ttp-' + ('0' * 64); [IO.File]::WriteAllText($file, ($owner | ConvertTo-Json -Depth 30)); Reject { Get-IrisProductDescriptor -DataRoot $data } 'tooltip_owner_identity_hash_mismatch' }
finally { [IO.File]::WriteAllBytes($file, $raw) }
$legacy = Join-Path $data 'Layer3English'
try { [IO.Directory]::CreateDirectory($legacy) | Out-Null; Reject { Assert-IrisLayer3PackageProjection -DataRoot $data } 'product_legacy_payload_present' }
finally { [IO.Directory]::Delete($legacy) }
foreach ($name in @('IrisTooltip.lock', 'IrisLayer3Product.lock')) {
    $lock = Join-Path $data $name
    try { [IO.File]::WriteAllText($lock, 'fixture'); Reject { Assert-IrisLayer3PackageProjection -DataRoot $data } 'install_in_progress' }
    finally { [IO.File]::Delete($lock) }
}
'''.replace('__MODULE__', str(stage / 'Iris/tools/Layer3PackageProjection.psm1')).replace('__DATA__', str(stage / product.DATA_ROOT))
    package_source = (stage / 'Iris/tools/package_iris.ps1').read_text(encoding='utf-8')
    hash_function = package_source[package_source.index('function Get-FileHash {'):package_source.index('$scriptRoot =')]
    command(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', hash_function + admission], ROOT, 'package-admission', pid)
    package = workspace / 'p'
    package_command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(stage / 'Iris/tools/package_iris.ps1'),
                       '-OutputRoot', str(package), '-PackageApplicability', 'current_runtime_payload', '-Zip']
    command(package_command, ROOT, 'package', pid)
    installed = workspace / 'z'
    with zipfile.ZipFile(package / 'Iris.zip') as archive:
        names = [n for n in archive.namelist() if not n.endswith('/')]
        assert len(names) == len(set(names))
        for n in names:
            product.local(installed, n)
        actual = {n: product.digest(archive.read(n)) for n in names}
        assert actual == {'Iris/'+n: sha for n,sha in install.inventory(package / 'Iris').items()}
        for name in manifest['b_preserved']:
            assert archive.read(name) == accepted[name]
        archive.extractall(installed)
    assert install.inventory(stage / 'Iris/media') == install.inventory(installed / 'Iris/media')
    command([lua, harness, str(installed), 'expanded', str(fixture)], ROOT, 'zip-c-pointer', pid)
    # Actual admission failures share the same product/stage; no gate trees.
    member = first / 'Index.lua'
    raw = member.read_bytes()
    member.write_bytes(raw + b'-- drift\n')
    with pytest.raises(ValueError, match='member mismatch'):
        install.admit(first)
    member.write_bytes(raw)
    with pytest.raises(ValueError):
        product.local(first, '../escape')
    with pytest.raises(ValueError):
        product.new_output(ROOT, ROOT / 'Iris/media')
    drift = workspace / 'drift'
    drift.write_bytes(b'drift')
    original_local = install.local
    ref = manifest['identity']['producer'][0]['path']
    with monkeypatch.context() as patch:
        patch.setattr(install, 'local', lambda root,path: drift if root==ROOT and path==ref else original_local(root,path))
        with pytest.raises(ValueError, match='source drift'):
            install.stage(ROOT, first, workspace / 'unused')
    for lockname in ('IrisTooltip.lock', 'IrisLayer3Product.lock'):
        lock = stage / product.DATA_ROOT / lockname
        lock.write_text('locked')
        with pytest.raises(ValueError, match='locked'):
            install.stage(stage, first, stage / '.tmp/menu/unused')
        lock.unlink()
    # v2 never uses live promote, whose successor-owner refusal is preserved.
    with pytest.raises(ValueError, match='Tooltip successor'):
        install.promote(stage, first, stage, stage / '.tmp/j', expected_pointer_sha256='', observation={}, package_path=package/'Iris.zip', game_closed=True)
    pointer = stage / product.DATA_ROOT / product.POINTER
    original = pointer.read_bytes()
    pointer.write_bytes(b'return {}\n')
    damaged = install.inventory(stage / 'Iris/media')
    with pytest.raises(InterruptedError):
        install.restore_candidate(ROOT, first, stage, stage / '.tmp/j0', interrupt_after=0)
    assert install.inventory(stage / 'Iris/media') == damaged
    assert install.recover(stage, stage / '.tmp/j0') == 'rolled_back'
    original_write = install.atomic_write
    def interrupted(path, raw):
        original_write(path,raw)
        if path == pointer:
            raise KeyboardInterrupt('candidate pointer interruption')
    with monkeypatch.context() as patch:
        patch.setattr(install, 'atomic_write', interrupted)
        with pytest.raises(KeyboardInterrupt):
            install.restore_candidate(ROOT, first, stage, stage / '.tmp/j1')
    assert install.recover(stage, stage / '.tmp/j1') == 'rolled_back'
    assert install.inventory(stage / 'Iris/media') == damaged
    assert install.restore_candidate(ROOT, first, stage, stage / '.tmp/j2') == 'complete'
    assert install.restore_candidate(ROOT, first, stage, stage / '.tmp/j3') == 'no_op'
    assert pointer.read_bytes() == original
    assert (ROOT / product.DATA_ROOT / 'IrisLayer3DataCurrent.lua').read_bytes() == before
    print(f'recovery: candidate={pid} interrupted/rollback/idempotence/source-pointer preserved', flush=True)
    print(f'CANDIDATE product={pid} zip={package / "Iris.zip"} sha256={product.digest((package / "Iris.zip").read_bytes())}', flush=True)
