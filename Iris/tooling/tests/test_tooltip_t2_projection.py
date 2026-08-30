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
from iris_tooling.domains.tooltip_t2.contract import CLOSEOUT, CONTRACT, HANDOFF_FILES, MANIFEST_SCHEMA, ROUTE, admit, load_contract, read_handoff
from iris_tooling.domains.tooltip_t2.projection import project
from iris_tooling.domains.tooltip_t2.serialization import lua_bytes, manifest_bytes


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
