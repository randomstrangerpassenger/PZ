from __future__ import annotations

import copy
import json
from pathlib import Path
import random
import re
import subprocess

import pytest

from iris_tooling.domains.tooltip_t1.contract import CONTRACT_FILES, DECISION_CONTRACT, canonical_bytes, fulltype_set_sha256, sha256_bytes
from iris_tooling.domains.tooltip_t1.models import TooltipContractError
from iris_tooling.domains.tooltip_static_data_projection.contract import CLOSEOUT, CONTRACT, HANDOFF_FILES, MANIFEST_SCHEMA, ROUTE, admit, load_contract, read_handoff
from iris_tooling.domains.tooltip_static_data_projection.projection import project
from iris_tooling.domains.tooltip_static_data_projection.serialization import lua_bytes, manifest_bytes
from iris_tooling.domains.tooltip_static_data_projection.recipe_variants import (
    DATA_ROOT, VARIANTS_NAME, MISSING_NAME_EXCLUSIONS, current_variants,
    project_recipe_variants, read_static_data, variants_bytes,
    interaction_candidates, project_interaction_variants,
)


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def fixture_handoff(tmp_path):
    source = Path(__file__).resolve().parents[3]
    repo, root = tmp_path / "repo", tmp_path / "handoff"
    repo.mkdir()
    root.mkdir()
    _git(repo, "init")
    contract_hashes, bundle = {}, []
    for path in CONTRACT_FILES:
        value = json.loads((source / path).read_text(encoding="utf-8"))
        _write(repo / path, value)
        if path.name in {"tooltip_display_contract.json", "layer2_tooltip_input_contract.json"}:
            # Physical T1 provenance can contain mixed EOL; the bundle is canonical JSON.
            physical = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            (repo / path).write_bytes(physical.replace(b"\n", b"\r\n", 1))
        digest = sha256_bytes(canonical_bytes(value))
        contract_hashes[path.as_posix()] = sha256_bytes((repo / path).read_bytes())
        if path != DECISION_CONTRACT:
            bundle.append(f"{path.name}={digest}\n")
    contract_hashes["authority_contract_bundle_sha256"] = sha256_bytes("".join(bundle).encode())
    rows = [{
        "schema_version": "iris-tooltip-t2-handoff-v1", "subject_binding_ref": "subject_binding.json",
        "full_type": f"Base.Row{count}",
        "slots": [{"slot_id": f"S{slot}", "semantic_identity": f"identity:{count}:{slot}",
                   "localized_surfaces": {"ko": "[도구 - 수리]" if slot == 1 else f"문장 {slot}",
                                          "en": "[Tools - Repair]" if slot == 1 else f"Line {slot}"}}
                  for slot in range(5 - count, 5)],
    } for count in range(5)]
    contract, _ = load_contract(source)
    contract["support_count"] = len(rows)
    contract["support_sha256"] = fulltype_set_sha256(row["full_type"] for row in rows)
    _write(repo / CONTRACT, contract)
    _write(repo / MANIFEST_SCHEMA, json.loads((source / MANIFEST_SCHEMA).read_text(encoding="utf-8")))
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "T1 fixture")
    subject = {"commit": _git(repo, "rev-parse", "HEAD"), "tree": _git(repo, "rev-parse", "HEAD^{tree}"),
               "generation_id": "fixture", "input_sha256": {}, "contract_sha256": contract_hashes}
    subject["subject_identity_sha256"] = sha256_bytes(canonical_bytes(subject))
    subject.update(schema_version="iris-tooltip-t1-subject-binding-v1", working_tree_clean=True)
    _write(root / "subject_binding.json", subject)
    locator = {"adoption_state": "adopted", "contract_and_audit_axis": "complete",
               "formal_closeout_state": "complete", "T2_FULL_DATA_PROGRESSION": "OPEN", "production_t2_handoff": "present",
               "machine_subject": {key: subject[key] for key in ("commit", "tree")}, "final_root": root.as_posix()}
    rebind(root, locator, rows, contract, subject)
    _write(repo / ROUTE, {"tooltip_t1_production_handoff": locator})
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "adopt fixture")
    return repo, root, locator, rows, contract


def rebind(root, locator, rows, contract, subject=None):
    if subject is None:
        subject = json.loads((root / "subject_binding.json").read_bytes())
    (root / "t2_handoff_input.jsonl").write_bytes(b"".join(canonical_bytes(row) for row in rows))
    manifest = {
        "schema_version": "iris-tooltip-t2-handoff-manifest-v1", "subject": locator["machine_subject"],
        "support_count": contract["support_count"], "support_sha256": contract["support_sha256"],
        "handoff_row_count": contract["support_count"], "handoff_fulltype_sha256": contract["support_sha256"],
        "handoff_input_sha256": sha256_bytes((root / "t2_handoff_input.jsonl").read_bytes()),
        "authority_contract_bundle_sha256": subject["contract_sha256"]["authority_contract_bundle_sha256"],
        "candidate_run_receipt_sha256": "a" * 64,
    }
    _write(root / "t2_handoff_manifest.json", manifest)
    hashes = {name: sha256_bytes((root / name).read_bytes()) for name in HANDOFF_FILES}
    closeout = {key: locator[key] for key in ("contract_and_audit_axis", "formal_closeout_state", "T2_FULL_DATA_PROGRESSION", "production_t2_handoff")}
    closeout.update(subject=locator["machine_subject"], candidate_run_receipt={"sha256": "a" * 64}, strict_t2_handoff={
        "candidate_final_bytes_equal": True, "artifact_sha256": hashes.copy(),
        "support_count": contract["support_count"], "handoff_row_count": contract["support_count"], "support_sha256": contract["support_sha256"],
    })
    _write(root / CLOSEOUT, closeout)
    hashes[CLOSEOUT] = sha256_bytes((root / CLOSEOUT).read_bytes())
    locator["artifact_sha256"] = hashes


def test_s2_supply_and_owner_integration(tmp_path):
    """Real four-role candidate production and shared pre-game acceptance.

    No fabricated D6 admission/final closeout, no current activation.
    """
    from collections import Counter
    from iris_tooling.domains.layer3 import tooltip_s2_supply as supply
    from iris_tooling.domains.tooltip_t1 import audit
    from iris_tooling.domains.tooltip_t1 import s2_candidate
    from iris_tooling.domains.tooltip_static_data_projection import cli as t2_cli
    from iris_tooling.domains.tooltip_t1.models import Slot, SemanticSlotState, LocaleSurfaceReadiness
    from iris_tooling.domains.tooltip_static_data_projection import install
    from iris_tooling.domains.tooltip_static_data_projection.contract import validate_supply_rows
    from iris_tooling.domains.tooltip_static_data_projection.serialization import artifact_binding, RUN_RECEIPT, LUA_NAME, MANIFEST_NAME
    repository = Path(__file__).resolve().parents[3]
    assert tmp_path.resolve().is_relative_to(repository / '.tmp'), 'integration fixture must stay in selected repository'
    payload = supply.build(repository)
    assert payload == supply.build(repository), 'deterministic supply'
    embedded = {'sha256': sha256_bytes(canonical_bytes(payload)), 'payload': payload}
    before, _, _ = supply.current_support(repository)
    contract, contract_hash = load_contract(repository)
    baseline, _, _ = project(before, contract)
    assert baseline == read_static_data((repository / DATA_ROOT / LUA_NAME).read_bytes()), 'stale before handoff'
    handoff = tmp_path / 'h'
    receipt = s2_candidate.build(repository, handoff)
    second = tmp_path / 'i'
    assert receipt == s2_candidate.build(repository, second)
    for name in (s2_candidate.SUBJECT, s2_candidate.ROWS, s2_candidate.RECEIPT):
        assert (handoff / name).read_bytes() == (second / name).read_bytes()
    receipt_sha = sha256_bytes((handoff / 'run_receipt.json').read_bytes())
    rows = [json.loads(line) for line in (handoff / 't2_handoff_input.jsonl').read_bytes().splitlines()]
    accepted = s2_candidate.admit(repository, handoff, receipt_sha)
    with pytest.raises(TooltipContractError, match='receipt hash'):
        s2_candidate.admit(repository, handoff, '0' * 64)
    saved_subject = (handoff / s2_candidate.SUBJECT).read_bytes()
    bad_subject = json.loads(saved_subject)
    bad_subject['source_sha256']['Iris/tools/package_iris.ps1'] = '0' * 64
    (handoff / s2_candidate.SUBJECT).write_bytes(canonical_bytes(bad_subject))
    with pytest.raises(TooltipContractError, match='source drift'):
        s2_candidate.admit(repository, handoff, receipt_sha)
    (handoff / s2_candidate.SUBJECT).write_bytes(saved_subject)
    validate_supply_rows(embedded, rows)
    for row, prior in zip(accepted.rows, before.rows):
        assert [s for s in row['slots'] if s['slot_id'] == 'S1'] == [s for s in prior['slots'] if s['slot_id'] == 'S1']
    data, provenance, summary = project(accepted, contract)
    assert (data, provenance, summary) == project(accepted, contract)
    for key, supplied in payload['records'].items():
        if supplied['state'] == 'out_of_dvf_target':
            assert not any(s['slot_id'] == 'S2' for s in next(r for r in rows if r['full_type'] == key)['slots'])
    modified = copy.deepcopy(embedded)
    modified['payload']['records'][next(iter(data))]['state'] = 'unknown'
    modified['sha256'] = sha256_bytes(canonical_bytes(modified['payload']))
    with pytest.raises(TooltipContractError):
        supply.validate_embedded(modified)
    malformed_rows = copy.deepcopy(rows)
    next(s for r in malformed_rows for s in r['slots'] if s['slot_id'] == 'S2')['localized_surfaces']['en'] += ' changed'
    with pytest.raises(TooltipContractError, match='text drift'):
        validate_supply_rows(embedded, malformed_rows)
    t2 = tmp_path / 't'
    raw = lua_bytes(data)
    generated = t2_cli.build(repository, handoff, t2, s2_candidate=True, candidate_receipt_sha256=receipt_sha)
    other_t2 = tmp_path / 'u'
    assert generated == t2_cli.build(repository, second, other_t2, s2_candidate=True, candidate_receipt_sha256=receipt_sha)
    for name in (LUA_NAME, MANIFEST_NAME, RUN_RECEIPT):
        assert (t2 / name).read_bytes() == (other_t2 / name).read_bytes()
    assert (t2 / LUA_NAME).read_bytes() == raw
    candidate, other = tmp_path / 'c', tmp_path / 'd'
    owner = install.build(repository, t2, candidate)
    assert owner == install.build(repository, other_t2, other)
    pools = interaction_candidates(repository, data)
    new_variants = project_interaction_variants(data, rows, pools)
    assert variants_bytes(new_variants) == (candidate / VARIANTS_NAME).read_bytes()
    kinds = {v['kind'] for pool in pools.values() for v in pool}
    assert kinds == {'recipe', 'rightclick', 'evolved_recipe'}
    for key, entry in new_variants.items():
        assert [v['id'] for v in entry['variants']] == [v['id'] for v in pools[key]]
        for variant, choice in zip(entry['variants'], pools[key]):
            for loc in ('ko', 'en'):
                assert variant[loc][:-1] == data[key][loc][:-1]
                assert variant[loc][-1] == choice[loc]
                assert len(variant[loc]) <= 4
    places = s2_candidate.acquisition_places(repository)
    for row in rows:
        key = row['full_type']
        slot = next((s for s in row['slots'] if s['slot_id'] == 'S3'), None)
        place = places.get(key)
        assert bool(slot) == bool(place and place['fact_refs'])
        if slot:
            assert slot['localized_surfaces'] == place['locales']
            assert next(p for p in provenance[key]['lines'] if p['slot_id'] == 'S3')['role'] == 'acquisition_place'
    from iris_tooling.domains.layer3 import description_composition_results as description
    corpus = description.read_result(repository)
    for item in corpus['items']:
        if item['item_id'] not in payload['records']:
            continue
        record = payload['records'][item['item_id']]
        for loc in ('ko', 'en'):
            assert record['locales'][loc] == item['locales'][loc]['compact']
            assert record['details'][loc] == item['locales'][loc]['expanded']
    for defect in ('locale', 'failed', 'reason', 'schema', 'links'):
        bad = copy.deepcopy(payload)
        present = next(r for r in bad['records'].values() if r['state'] == 'present')
        absent = next(r for r in bad['records'].values() if r['state'] == 'absent')
        if defect == 'locale': del present['locales']['en']
        elif defect == 'failed': present['locales']['ko']['state'] = 'failed'
        elif defect == 'reason': absent['locales']['ko']['reason'] = None
        elif defect == 'schema': bad['schema_version'] = 'unsupported'
        else: present['locales']['ko']['detail_links'][0]['segment'] = 99999
        with pytest.raises((TooltipContractError, ValueError)):
            supply.validate(bad)
    for slot_id in ('S1', 'S3', 'S4'):
        malformed = copy.deepcopy(rows)
        next(s for r in malformed for s in r['slots'] if s['slot_id'] == slot_id)['localized_surfaces']['en'] += ' changed'
        subject = json.loads(saved_subject)
        with pytest.raises(TooltipContractError, match='owner/role'):
            s2_candidate._decode(subject, malformed, receipt, saved_subject,
                (handoff / s2_candidate.ROWS).read_bytes(), contract, before=before)
    assert all(entry['base'] == data[key] for key, entry in new_variants.items())
    staged = tmp_path / 's'
    assert install.stage(repository, candidate, staged) == owner['product_id']
    menu = DATA_ROOT / 'IrisLayer3DataCurrent.lua'
    assert (repository / menu).read_bytes() == (staged / menu).read_bytes()
    assert install.recover(repository, staged / 'journal') == 'rolled_back'
    assert (staged / DATA_ROOT / LUA_NAME).read_bytes() == (repository / DATA_ROOT / LUA_NAME).read_bytes()
    with pytest.raises(RuntimeError, match='interruption'):
        install.install(repository, candidate, staged, tmp_path / 'j', interrupt_after=1)
    assert (staged / DATA_ROOT / LUA_NAME).read_bytes() == (repository / DATA_ROOT / LUA_NAME).read_bytes()
    install.install(repository, candidate, staged, tmp_path / 'k')
    # Same source/package for syntax, runtime and install readback; bounded children.
    def command(args):
        print('starting:', subprocess.list2cmdline(args), flush=True)
        completed = subprocess.run(args, cwd=repository, capture_output=True, timeout=240)
        assert completed.returncode == 0, (args, completed.stdout[-6000:], completed.stderr[-6000:])
        print('fixture command exit=0:', subprocess.list2cmdline(args))
    expected = tmp_path / 'expected.lua'
    expected.write_bytes(raw)
    command(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
             str(repository / 'tools/check_lua_syntax.ps1')])
    command(['lua', str(repository / 'Iris/test/lua/tooltip_static_data_runtime_harness.lua'), str(staged), 'supply', str(expected)])
    package = staged / '.tmp/package'
    command(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(staged / 'Iris/tools/package_iris.ps1'),
             '-OutputRoot', str(package), '-Zip'])
    packaged_data = package / 'Iris/media/lua/client/Iris/Data'
    for name in (*install.FILES, install.OWNER_NAME):
        assert (packaged_data / name).read_bytes() == (candidate / name).read_bytes()
    for name in (LUA_NAME, VARIANTS_NAME):
        saved = (candidate / name).read_bytes()
        (candidate / name).write_bytes(b'bad')
        with pytest.raises(TooltipContractError):
            install.admit(candidate)
        (candidate / name).write_bytes(saved)
    print('S2 candidate (PZ pending; no current adoption):', dict(Counter(r['state'] for r in payload['records'].values())),
          'supply', embedded['sha256'], 'product', owner['product_id'], 'rows', summary['line_distribution'])


def test_package_rejects_tooltip_writer_lock():
    repository = Path(__file__).resolve().parents[3]
    # A package must reject even the first migration's partial write, before
    # IrisTooltipOwner.json exists. Reuse the repository-local test workspace.
    root = repository / '.tmp/tooltip/lock'
    assert not root.exists()
    root.mkdir()
    try:
        (root / 'IrisTooltip.lock').write_bytes(b'{}')
        module = repository / 'Iris/tools/Layer3PackageProjection.psm1'
        script = "Import-Module '" + str(module).replace("'", "''") + "'; try { Get-IrisTooltipOwner -DataRoot '" + str(root).replace("'", "''") + "'; exit 1 } catch { if ($_.Exception.Message -ne 'tooltip_install_in_progress') { throw }; exit 0 }"
        result = subprocess.run(['powershell', '-NoProfile', '-Command', script], capture_output=True, timeout=30)
        assert result.returncode == 0, (result.stdout, result.stderr)
    finally:
        (root / 'IrisTooltip.lock').unlink()
        root.rmdir()


@pytest.mark.parametrize("case", ["subject", "hash", "state", "exact_set", "schema", "locale"])
def test_admission(tmp_path, case):
    repo, root, locator, rows, contract = fixture_handoff(tmp_path)
    if case == "subject":
        locator["machine_subject"]["tree"] = "0" * 40
    elif case == "hash":
        locator["artifact_sha256"]["t2_handoff_input.jsonl"] = "0" * 64
    elif case == "state":
        locator["T2_FULL_DATA_PROGRESSION"] = "BLOCKED"
    else:
        if case == "exact_set":
            rows[0]["full_type"] = rows[0]["full_type"].lower()
        elif case == "schema":
            rows[1]["readiness"] = "ready"
        else:
            del rows[1]["slots"][0]["localized_surfaces"]["en"]
        rebind(root, locator, rows, contract)
    with pytest.raises(TooltipContractError):
        read_handoff(root, locator, support_count=contract["support_count"], support_sha256=contract["support_sha256"])


def test_projection(tmp_path):
    repo, root, _, rows, contract = fixture_handoff(tmp_path)
    accepted = admit(repo, root, contract)
    data, provenance, summary = project(accepted, contract)
    assert summary["line_distribution"] == {str(n): 1 for n in range(5)}
    for row in rows:
        key = row["full_type"]
        assert data[key] == {locale: [slot["localized_surfaces"][locale] for slot in row["slots"]] for locale in ("ko", "en")}
        assert provenance[key]["present_slots"] == [slot["slot_id"] for slot in row["slots"]]
        assert [line["semantic_identity"] for line in provenance[key]["lines"]] == [slot["semantic_identity"] for slot in row["slots"]]
        assert provenance[key]["line_count"]["ko"] == provenance[key]["line_count"]["en"]
    assert data["Base.Row4"]["ko"][0] == "[도구 - 수리]"
    assert data["Base.Row0"] == {"ko": [], "en": []}
    _, contract_hash = load_contract(repo)
    manifest = json.loads(manifest_bytes(accepted.binding, contract_hash, contract,
                                         lua_bytes(data), provenance, summary))
    schema = json.loads((repo / MANIFEST_SCHEMA).read_bytes())
    # The production schema's fixed denominator is reduced only for this mixed fixture.
    schema["properties"]["t1_input"]["properties"]["support_count"]["const"] = len(rows)
    schema["properties"]["t1_input"]["properties"]["support_sha256"]["const"] = contract["support_sha256"]
    schema["properties"]["generation_success_count"]["const"] = len(rows)
    schema["properties"]["fulltypes"]["minProperties"] = len(rows)
    schema["properties"]["fulltypes"]["maxProperties"] = len(rows)
    # Test-local assertions consume the actual serialized manifest and its declared
    # schema vocabulary. This is not an independent or general JSON Schema validator.
    pending = [(manifest, schema)]
    while pending:
        value, rule = pending.pop()
        if "const" in rule:
            assert type(value) is type(rule["const"]) and value == rule["const"]
        if "enum" in rule:
            assert value in rule["enum"]
        kind = rule.get("type")
        if kind == "object":
            assert isinstance(value, dict)
            assert set(rule.get("required", ())) <= set(value)
            properties = rule.get("properties", {})
            additional = rule.get("additionalProperties", True)
            if additional is False:
                assert set(value) <= set(properties)
            assert rule.get("minProperties", 0) <= len(value) <= rule.get("maxProperties", len(value))
            pending.extend((child, properties.get(key, additional)) for key, child in value.items()
                           if key in properties or isinstance(additional, dict))
        elif kind == "array":
            assert isinstance(value, list)
            assert len(value) <= rule.get("maxItems", len(value))
            if rule.get("uniqueItems"):
                assert len(value) == len(set(value))
            pending.extend((child, rule["items"]) for child in value)
        elif kind == "integer":
            assert type(value) is int
            assert rule.get("minimum", value) <= value <= rule.get("maximum", value)
        elif kind == "string":
            assert isinstance(value, str) and len(value) >= rule.get("minLength", 0)
            if "pattern" in rule:
                assert re.fullmatch(rule["pattern"], value)
    for row in manifest["fulltypes"].values():
        assert row["line_count"]["ko"] == row["line_count"]["en"] == len(row["lines"])
        for position, line in enumerate(row["lines"], 1):
            assert line["position"] == position
            assert line["role"] == contract["slot_roles"][line["slot_id"]]
            assert all(pair["source_sha256"] == pair["final_sha256"] for pair in line["surface_sha256"].values())

    # Opening-time presentation uses the same fixture family: deterministic
    # compilation, exact core/action preservation, and no invented locale names.
    assert read_static_data(lua_bytes(data)) == data
    identities = sorted(MISSING_NAME_EXCLUSIONS)
    owners = {"Base.Fixture": {"use_cases": [
        {"use_case_id": identity, "surface": "recipe_ui", "line_kind": "evidence",
         "stable_order_key": str(index), "evidence_sources": [
             {"source_type": "recipe_evidence", "decision": "PASS"}]}
        for index, identity in enumerate(identities)
    ] + [{"use_case_id": "action", "surface": "context_menu", "line_kind": "evidence",
          "stable_order_key": "z"}]}}
    base = {"Base.Fixture": {"ko": ["[도구 - 수리]", "설명", "기존 레시피 문장", "동작"],
                             "en": ["[Tools - Repair]", "Core", "Old recipe", "Action"]}}
    names = {identity: {"recipe_id": identity, "translated_name": f"제작 {index}",
                       "original_name": f"Craft {index}"} for index, identity in enumerate(identities)}
    old = {identity: {"localized_surfaces": {"ko": "기존 레시피 문장", "en": "Old recipe"}}
           for identity in identities}
    actions = {"action": {"ko": "동작", "en": "Action"}}
    companion = project_recipe_variants(base, owners, names, old, actions, contract)
    assert len(companion["Base.Fixture"]["variants"]) == 3  # Includes eligible over-capacity candidates.
    for index, view in enumerate(companion["Base.Fixture"]["variants"]):
        assert view == {"id": identities[index],
                        "ko": ["[도구 - 수리]", "설명", f"[레시피] 제작 {index}", "동작"],
                        "en": ["[Tools - Repair]", "Core", f"[Recipe] Craft {index}", "Action"]}
    reversed_owners = copy.deepcopy(owners)
    reversed_owners["Base.Fixture"]["use_cases"].reverse()
    assert variants_bytes(companion) == variants_bytes(project_recipe_variants(
        base, reversed_owners, dict(reversed(list(names.items()))), old, actions, contract))
    missing = copy.deepcopy(names)
    for record in missing.values():
        record["translated_name"] = ""
    omitted = project_recipe_variants(base, owners, missing, old, actions, contract)["Base.Fixture"]
    assert omitted["variants"] == []
    assert omitted["without_recipe"] == {"ko": ["[도구 - 수리]", "설명", "동작"],
                                         "en": ["[Tools - Repair]", "Core", "Action"]}
    for defect in ("stale_base", "unapproved", "unknown_missing_name"):
        bad_base, bad_owners, bad_names, bad_old = copy.deepcopy((base, owners, names, old))
        if defect == "stale_base":
            bad_base["Base.Fixture"]["en"][2] = "Wrong recipe"
        elif defect == "unapproved":
            bad_owners["Base.Fixture"]["use_cases"][0]["evidence_sources"][0]["decision"] = "FAIL"
        else:
            unknown = "uc.recipe.new_missing_name"
            bad_owners["Base.Fixture"]["use_cases"][0]["use_case_id"] = unknown
            bad_old[unknown] = bad_old.pop(identities[0])
            bad_names[unknown] = {"recipe_id": unknown, "original_name": "Untranslated"}
        with pytest.raises(TooltipContractError):
            project_recipe_variants(bad_base, bad_owners, bad_names, bad_old, actions, contract)
    source = Path(__file__).resolve().parents[3]
    actual = current_variants(source)
    assert variants_bytes(actual) == (source / DATA_ROOT / VARIANTS_NAME).read_bytes()
    cabbage = actual["farming.Cabbage"]["variants"]
    assert len(cabbage) == 1 and cabbage[0]["id"] == "uc.recipe.make_jar_of_cabbage"
    assert cabbage[0]["ko"][-1] == "[레시피] 병에 양배추 절이기"
    assert cabbage[0]["en"][-1] == "[Recipe] Make Jar of Cabbage"
    assert not MISSING_NAME_EXCLUSIONS.intersection(
        view["id"] for row in actual.values() for view in row["variants"])


def test_reader_order(tmp_path):
    _, root, locator, rows, contract = fixture_handoff(tmp_path)
    shuffled = copy.deepcopy(rows)
    random.Random(917).shuffle(shuffled)
    outputs, inputs = [], []
    for permutation in (rows, list(reversed(rows)), shuffled):
        rebind(root, locator, permutation, contract)
        accepted = read_handoff(root, locator, support_count=contract["support_count"], support_sha256=contract["support_sha256"])
        data, provenance, summary = project(accepted, contract)
        outputs.append((lua_bytes(data), provenance, summary))
        inputs.append(accepted.binding["artifact_sha256"]["t2_handoff_input.jsonl"])
    assert outputs[0] == outputs[1] == outputs[2]
    assert len(set(inputs)) == 3
