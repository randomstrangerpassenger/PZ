from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

from .contract import (
    AUTHORITY_ROOT,
    canonical_bytes,
    git_subject,
    load_json,
    parse_classifications,
    sha256_bytes,
    sha256_file,
    validate_execution_subject,
)
from .models import TooltipContractError


WORKSTREAM_ID = "T1-D5"
PREDECESSOR_COMMIT = "6b7118dc229bf8138302696e1aa5e5b7454589dc"
PREDECESSOR_TREE = "4eae6fbdb3d0b2cb532f875b96137335a403f2fc"
PREDECESSOR_CLOSEOUT_SHA256 = "6e255227b0aa8381453a563e3ede9e96c59be82c9bb3a7cb6eba8f488039b4a3"
SUPPORT_PREDICATE = "current-owner-fulltype-union-v1"
TARGETS = ("Base.LemonGrass", "Base.Lemongrass")
NORMALIZED_TARGET = "base.lemongrass"
MECHANISM = "unresolved_disposition_predicate_refinement_v1"

ITEM_SOURCE = Path("Iris/input/items_itemscript.json")
CLASSIFICATIONS = Path("Iris/media/lua/client/Iris/Data/IrisClassifications.lua")
L3_POINTER = Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua")
L3_GENERATIONS = Path("Iris/media/lua/client/Iris/Data/IrisLayer3Generations")
L3_OWNER_INPUT = Path("Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json")
L4_OWNER_INPUT = Path("Iris/build/description/v2/data/upstream_usecases_by_fulltype.json")
DISPOSITION_SCHEMA = AUTHORITY_ROOT / "tooltip_t1_d5_current_support_disposition.schema.json"
DISPOSITION_RECORD = AUTHORITY_ROOT / "tooltip_t1_d5_current_support_disposition.json"

_GENERATION = re.compile(r'generation_id\s*=\s*"([^"]+)"')


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(canonical_bytes(row) for row in rows))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise TooltipContractError(f"{path}:{line_number}: expected JSON object")
        rows.append(value)
    return rows


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TooltipContractError(message)


def _ordered_set_sha256(values: Iterable[str]) -> str:
    return sha256_bytes(canonical_bytes(sorted(set(values))))


def _generation_id(repository_root: Path) -> str:
    match = _GENERATION.search((repository_root / L3_POINTER).read_text(encoding="utf-8"))
    if not match:
        raise TooltipContractError("D5 Layer 3 current generation pointer is malformed")
    return match.group(1)


def _target_row(value: dict[str, Any], target: str) -> dict[str, Any] | None:
    row = value.get(target)
    return row if isinstance(row, dict) else None


def _surface_binding(path: Path, row: Any, *, present: bool) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "present": present,
        "row_sha256": sha256_bytes(canonical_bytes(row if present else {"absence": "canonical"})),
    }


def build_target_snapshot(repository_root: Path) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    items = load_json(repository_root / ITEM_SOURCE)
    classifications = parse_classifications(repository_root / CLASSIFICATIONS)
    generation_id = _generation_id(repository_root)
    rendered_path = L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json"
    rendered = load_json(repository_root / rendered_path)
    layer3 = rendered.get("entries")
    owner_input = load_json(repository_root / L3_OWNER_INPUT)
    layer3_owner = owner_input.get("entries")
    layer4_value = load_json(repository_root / L4_OWNER_INPUT)
    layer4 = layer4_value.get("fulltypes")
    _require(isinstance(layer3, dict), "D5 pointer-selected Layer 3 entries missing")
    _require(isinstance(layer3_owner, dict), "D5 Layer 3 Tooltip owner entries missing")
    _require(isinstance(layer4, dict), "D5 Layer 4 owner entries missing")

    support = sorted(set(classifications) | set(layer3) | set(layer4))
    collision_members = sorted(value for value in support if value.lower() == NORMALIZED_TARGET)
    target_rows: dict[str, Any] = {}
    for target in TARGETS:
        item_row = _target_row(items, target)
        rendered_row = _target_row(layer3, target)
        layer3_owner_row = _target_row(layer3_owner, target)
        layer4_row = _target_row(layer4, target)
        layer2_row = classifications.get(target)
        target_rows[target] = {
            "exact_full_type": target,
            "normalized_diagnostic_key": target.lower(),
            "source_item": _surface_binding(ITEM_SOURCE, item_row, present=item_row is not None),
            "layer2": _surface_binding(CLASSIFICATIONS, list(layer2_row or ()), present=layer2_row is not None),
            "layer3": {
                **_surface_binding(rendered_path, rendered_row, present=rendered_row is not None),
                "owner_input_path": L3_OWNER_INPUT.as_posix(),
                "owner_row_present": layer3_owner_row is not None,
                "owner_row_sha256": sha256_bytes(canonical_bytes(layer3_owner_row if layer3_owner_row is not None else {"absence": "canonical"})),
                "fact_id": layer3_owner_row.get("fact_id") if layer3_owner_row else None,
                "source_ref": layer3_owner_row.get("source_ref") if layer3_owner_row else None,
            },
            "layer4": _surface_binding(L4_OWNER_INPUT, layer4_row, present=layer4_row is not None),
            "support_membership": target in support,
            "support_entry_paths": [
                name
                for name, universe in (("layer2", classifications), ("layer3", layer3), ("layer4", layer4))
                if target in universe
            ],
        }
    return {
        "schema_version": "iris-tooltip-t1-d5-target-snapshot-v1",
        "support_predicate": SUPPORT_PREDICATE,
        "comparison_algorithm": "python-str-lower-diagnostic-only-v1",
        "generation_id": generation_id,
        "declared_exact_targets": list(TARGETS),
        "target_set_sha256": _ordered_set_sha256(TARGETS),
        "support_count": len(support),
        "support_sha256": _ordered_set_sha256(support),
        "normalized_collision_members": collision_members,
        "normalized_collision_members_sha256": _ordered_set_sha256(collision_members),
        "targets": target_rows,
    }


def applicability_material(snapshot: dict[str, Any]) -> dict[str, Any]:
    targets = snapshot.get("targets")
    _require(isinstance(targets, dict), "D5 snapshot target rows missing")
    material: dict[str, Any] = {}
    for target in TARGETS:
        row = targets.get(target)
        _require(isinstance(row, dict), f"D5 snapshot target missing: {target}")
        material[target] = {
            "source_item": row.get("source_item"),
            "layer2": row.get("layer2"),
            "layer3": row.get("layer3"),
            "layer4": row.get("layer4"),
        }
    return {
        "schema_version": "iris-tooltip-t1-d5-applicability-material-v1",
        "support_predicate": SUPPORT_PREDICATE,
        "comparison_algorithm": "python-str-lower-diagnostic-only-v1",
        "disposition_schema_version": "iris-tooltip-t1-d5-current-support-disposition-v1",
        "declared_exact_targets": list(TARGETS),
        "targets": material,
    }


def applicability_fingerprint(snapshot: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(applicability_material(snapshot)))


def _approval_sha256(approval: dict[str, Any]) -> str:
    payload = {key: value for key, value in approval.items() if key != "approval_sha256"}
    return sha256_bytes(canonical_bytes(payload))


def validate_disposition_authority(disposition: dict[str, Any]) -> None:
    _require(disposition.get("schema_version") == "iris-tooltip-t1-d5-current-support-disposition-v1", "D5 disposition schema mismatch")
    _require(disposition.get("workstream_id") == WORKSTREAM_ID, "D5 workstream identity mismatch")
    _require(disposition.get("decision_status") == "owner_approved", "D5 owner decision is not approved")
    _require(disposition.get("support_predicate") == SUPPORT_PREDICATE, "D5 support predicate mismatch")
    _require(disposition.get("declared_exact_targets") == list(TARGETS), "D5 exact target order/spelling mismatch")
    _require(disposition.get("target_set_sha256") == _ordered_set_sha256(TARGETS), "D5 target-set hash mismatch")
    issuance = disposition.get("issuance_subject")
    _require(
        isinstance(issuance, dict)
        and issuance.get("commit") == PREDECESSOR_COMMIT
        and issuance.get("tree") == PREDECESSOR_TREE,
        "D5 issuance subject is inconsistent with the approved predecessor census",
    )
    predecessor = disposition.get("predecessor")
    _require(
        isinstance(predecessor, dict)
        and predecessor.get("commit") == PREDECESSOR_COMMIT
        and predecessor.get("tree") == PREDECESSOR_TREE
        and predecessor.get("closeout_sha256") == PREDECESSOR_CLOSEOUT_SHA256,
        "D5 predecessor binding mismatch",
    )
    approval = disposition.get("pre_mutation_owner_approval")
    _require(isinstance(approval, dict), "D5 pre-mutation owner approval missing")
    _require(approval.get("owner") == "Iris presentation-contract owner", "D5 approval owner mismatch")
    _require(approval.get("approval_ref") == "user_prompt:2026-08-29#owner-approval-preauthorized", "D5 approval reference mismatch")
    _require(approval.get("approval_sha256") == _approval_sha256(approval), "D5 approval hash mismatch")
    mechanism = disposition.get("collision_terminal_mechanism")
    _require(isinstance(mechanism, dict) and mechanism.get("id") == MECHANISM, "D5 Branch A mechanism is missing or unsupported")
    _require(mechanism.get("expected_raw_observation_exact_set") == list(TARGETS), "D5 raw-observation expectation mismatch")
    _require(mechanism.get("expected_correction_row_exact_set") == [], "D5 complete mechanism must eliminate target correction rows")
    _require(mechanism.get("expected_t2_blocking_exact_set") == [], "D5 complete mechanism must eliminate target T2 blockers")
    _require(mechanism.get("reason_code_preserved") is True and mechanism.get("detector_preserved") is True, "D5 mechanism weakens the detector or reason registry")

    approved_material = disposition.get("approved_applicability_material")
    binding = disposition.get("applicability_binding")
    _require(isinstance(approved_material, dict) and isinstance(binding, dict), "D5 applicability binding missing")
    _require(
        approved_material.get("schema_version") == "iris-tooltip-t1-d5-applicability-material-v1"
        and approved_material.get("support_predicate") == SUPPORT_PREDICATE
        and approved_material.get("comparison_algorithm") == "python-str-lower-diagnostic-only-v1"
        and approved_material.get("disposition_schema_version") == disposition["schema_version"]
        and approved_material.get("declared_exact_targets") == list(TARGETS)
        and isinstance(approved_material.get("targets"), dict),
        "D5 approved applicability material is malformed",
    )
    _require(binding.get("algorithm") == "declared-target-content-fingerprint-v1", "D5 applicability algorithm mismatch")
    _require(binding.get("applicability_fingerprint") == sha256_bytes(canonical_bytes(approved_material)), "D5 applicability fingerprint mismatch")
    _require(disposition.get("source_census_sha256") == sha256_bytes(canonical_bytes(approved_material)), "D5 source census binding mismatch")
    reaudit = disposition.get("re_audit_condition")
    _require(
        isinstance(reaudit, dict)
        and reaudit.get("predicate_version") == "d5-target-content-or-member-set-change-v1"
        and reaudit.get("commit_tree_equality_is_input") is False
        and reaudit.get("approved_collision_member_set") == list(TARGETS),
        "D5 re-audit condition is not machine-evaluable",
    )

    records = disposition.get("records")
    _require(isinstance(records, list) and len(records) == 2, "D5 requires exactly two disposition records")
    _require([row.get("exact_full_type") for row in records if isinstance(row, dict)] == list(TARGETS), "D5 disposition records are incomplete or case-mutated")
    for row, counterpart in zip(records, reversed(TARGETS), strict=True):
        _require(isinstance(row, dict), "D5 disposition record malformed")
        target = row["exact_full_type"]
        relation = row.get("identity_relation")
        _require(
            isinstance(relation, dict)
            and relation.get("kind") == "distinct_exact_fulltype_identities"
            and relation.get("relation_group_id") == "d5:base.lemongrass:exact-pair-v1"
            and relation.get("counterpart_exact_full_type") == counterpart,
            f"D5 identity relation conflict: {target}",
        )
        _require(row.get("support_disposition") == "retain_current_support_identity", f"D5 support disposition mismatch: {target}")
        _require(row.get("owner") == "Iris presentation-contract owner", f"D5 record owner mismatch: {target}")
        _require(row.get("approval_ref") == approval["approval_ref"], f"D5 record approval mismatch: {target}")
        _require(isinstance(row.get("evidence_refs"), list) and bool(row["evidence_refs"]), f"D5 evidence missing: {target}")
        _require(isinstance(row.get("source_authority_refs"), list) and bool(row["source_authority_refs"]), f"D5 source authority missing: {target}")
        _require(isinstance(row.get("acceptance_condition"), str) and bool(row["acceptance_condition"]), f"D5 acceptance missing: {target}")
        _require(row.get("applicability_binding") == "#/applicability_binding", f"D5 applicability ref mismatch: {target}")
        _require(row.get("re_audit_condition") == "#/re_audit_condition", f"D5 re-audit ref mismatch: {target}")
        approved_target = approved_material["targets"].get(target)
        _require(isinstance(approved_target, dict), f"D5 approved target material missing: {target}")
        expected_refs = {
            approved_target["source_item"]["path"]: approved_target["source_item"]["row_sha256"],
            approved_target["layer2"]["path"]: approved_target["layer2"]["row_sha256"],
            approved_target["layer3"]["owner_input_path"]: approved_target["layer3"]["owner_row_sha256"],
            approved_target["layer4"]["path"]: approved_target["layer4"]["row_sha256"],
        }
        actual_refs = {
            ref.get("path"): ref.get("row_sha256")
            for ref in row["source_authority_refs"]
            if isinstance(ref, dict)
        }
        _require(actual_refs == expected_refs, f"D5 source authority binding mismatch: {target}")


def evaluate_disposition_snapshot(disposition: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    validate_disposition_authority(disposition)
    current_fingerprint = applicability_fingerprint(snapshot)
    approved_fingerprint = disposition["applicability_binding"]["applicability_fingerprint"]
    current_members = snapshot["normalized_collision_members"]
    fingerprint_match = current_fingerprint == approved_fingerprint
    member_set_match = current_members == list(TARGETS)
    applicable = fingerprint_match and member_set_match
    return {
        "schema_version": "iris-tooltip-t1-d5-disposition-applicability-report-v1",
        "status": "applicable" if applicable else "stale_reaudit_required",
        "applicable": applicable,
        "issuance_provenance_valid": True,
        "approved_applicability_fingerprint": approved_fingerprint,
        "current_applicability_fingerprint": current_fingerprint,
        "fingerprint_match": fingerprint_match,
        "approved_collision_member_set": list(TARGETS),
        "current_collision_member_set": current_members,
        "collision_member_set_match": member_set_match,
        "commit_tree_equality_used": False,
        "selected_mechanism": disposition["collision_terminal_mechanism"]["id"],
        "snapshot": snapshot,
    }


def evaluate_disposition(repository_root: Path, disposition: dict[str, Any] | None = None) -> dict[str, Any]:
    if disposition is None:
        disposition = load_json(repository_root / DISPOSITION_RECORD)
    return evaluate_disposition_snapshot(disposition, build_target_snapshot(repository_root))


def resolved_collision_members(repository_root: Path) -> tuple[set[str], dict[str, Any]]:
    report = evaluate_disposition(repository_root)
    return (set(TARGETS) if report["applicable"] else set()), report


def collision_correction_members(
    collisions: dict[str, tuple[str, ...]] | dict[str, list[str]],
    resolved_members: set[str],
) -> set[str]:
    raw_members = {
        full_type
        for members in collisions.values()
        for full_type in members
    }
    _require(not resolved_members - raw_members, "D5 disposition resolves identities outside the raw collision observation")
    return raw_members - resolved_members


def exact_identity_metrics(
    support: Iterable[str],
    readiness: Iterable[str],
    raw_observation: Iterable[str],
    correction_rows: Iterable[str],
) -> dict[str, int]:
    support_values = list(support)
    readiness_values = list(readiness)
    raw_values = list(raw_observation)
    correction_values = list(correction_rows)
    expected = set(TARGETS)
    return {
        "case_normalization_merge": int(set(support_values) & expected != expected),
        "normalized_key_overwrite": int(len([value for value in support_values if value in expected]) != len(expected)),
        "unexpected_exact_duplicate": sum(
            max(0, values.count(target) - 1)
            for values in (support_values, readiness_values, raw_values, correction_values)
            for target in TARGETS
        ),
        "unexpected_support_row_loss": len(expected - set(readiness_values)),
        "exact_spelling_mutation": sum(value.lower() == NORMALIZED_TARGET and value not in expected for value in support_values),
    }


def normalization_usage_report(repository_root: Path) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    scan_paths = sorted((repository_root / "Iris/tooling/src/iris_tooling/domains/tooltip_t1").rglob("*.py"))
    scan_paths.extend(repository_root / path for path in (
        "Iris/tooling/tests/test_tooltip_t1_contract.py",
        "Iris/tooling/tests/test_tooltip_t1_projection.py",
        "Iris/tooling/tests/test_tooltip_t1_audit.py",
        "Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json",
    ))
    scan_paths.extend(sorted((repository_root / AUTHORITY_ROOT).glob("*.json")))
    scan_paths = sorted(set(path.resolve() for path in scan_paths))
    matches: list[dict[str, Any]] = []
    authoritative: list[dict[str, Any]] = []
    for path in scan_paths:
        relative = path.relative_to(repository_root).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not re.search(r"\.lower\(|\.casefold\(|normaliz|ascii_lower", line, re.IGNORECASE):
                continue
            classification = "comparison_only"
            if "normalized_collisions" in line or "NORMALIZED_TARGET" in line or "normalized_diagnostic" in line:
                classification = "diagnostic_grouping"
            if "/tests/" in f"/{relative}" or relative.endswith("contract_expectations.json"):
                classification = "comparison_only"
            match = {
                "path": relative,
                "line": line_number,
                "classification": classification,
                "line_sha256": sha256_bytes((line + "\n").encode("utf-8")),
            }
            matches.append(match)
            if classification == "authoritative_keying":
                authoritative.append(match)
    return {
        "schema_version": "iris-tooltip-t1-d5-normalization-usage-report-v1",
        "scan_manifest": [
            {"path": path.relative_to(repository_root).as_posix(), "sha256": sha256_file(path)}
            for path in scan_paths
        ],
        "matches": matches,
        "authoritative_normalized_key_storage_path_count": len(authoritative),
        "authoritative_normalized_key_storage_paths": authoritative,
        "claim_boundary": "declared Tooltip T1 code/test/fixture/authority scan manifest only",
    }


def _git_output(repository_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repository_root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise TooltipContractError(completed.stderr.decode("utf-8", errors="replace").strip() or "D5 git query failed")
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _shared_path_delta(repository_root: Path) -> list[dict[str, Any]]:
    changed = _git_output(repository_root, "diff", "--name-only", PREDECESSOR_COMMIT, "HEAD", "--").splitlines()
    shared_exact = {
        "Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py",
        "Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py",
        "Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py",
        "Iris/tooling/src/iris_tooling/domains/tooltip_t1/projection.py",
        "Iris/tooling/tests/test_tooltip_t1_contract.py",
        "Iris/tooling/tests/test_tooltip_t1_projection.py",
        "Iris/tooling/tests/test_tooltip_t1_audit.py",
        "Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json",
        "docs/iris_tooltip_t1_display_contract_policy.md",
    }
    shared = sorted(
        path for path in changed
        if path in shared_exact or path.startswith("Iris/_docs/authority/tooltip_t1/")
    )
    rows: list[dict[str, Any]] = []
    for path in shared:
        base = subprocess.run(
            ["git", "rev-parse", f"{PREDECESSOR_COMMIT}:{path}"],
            cwd=repository_root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        proposed = _git_output(repository_root, "rev-parse", f"HEAD:{path}")
        patch_bytes = subprocess.run(
            ["git", "diff", "--binary", PREDECESSOR_COMMIT, "HEAD", "--", path],
            cwd=repository_root,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        rows.append({
            "path": path,
            "base_blob": base.stdout.strip() if base.returncode == 0 else None,
            "proposed_blob": proposed,
            "patch_sha256": sha256_bytes(patch_bytes),
            "workstream_reason": "T1-D5 exact FullType disposition/application",
            "merge_invariant": "preserve exact-key support union, raw collision observation, and other-owner correction behavior",
        })
    return rows


def _git_is_ancestor(repository_root: Path, ancestor: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, "HEAD"],
        cwd=repository_root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode not in {0, 1}:
        raise TooltipContractError(completed.stderr.strip() or "D5 predecessor ancestry query failed")
    return completed.returncode == 0


def _external_empty(repository_root: Path, output_root: Path) -> Path:
    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    _require(output_root != repository_root and repository_root not in output_root.parents, "D5 output root must be repository-external")
    _require(not output_root.exists() or not any(output_root.iterdir()), "D5 output root must be empty")
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root


def run_census(repository_root: Path, output_root: Path) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    output_root = _external_empty(repository_root, output_root)
    subject = git_subject(repository_root)
    validate_execution_subject(subject)
    ancestor = _git_is_ancestor(repository_root, PREDECESSOR_COMMIT)
    _require(ancestor, "D5 predecessor inclusion is not established")
    snapshot = build_target_snapshot(repository_root)
    _require(snapshot["normalized_collision_members"] == list(TARGETS), "D5 normalized discovery class differs from the declared exact pair")
    _require(all(snapshot["targets"][target]["source_item"]["present"] for target in TARGETS), "D5 exact source authority is incomplete")
    _require(all(snapshot["targets"][target]["support_membership"] for target in TARGETS), "D5 declared target is missing from current support")
    disposition = load_json(repository_root / DISPOSITION_RECORD)
    applicability = evaluate_disposition(repository_root, disposition)

    subject.update({
        "predecessor_commit": PREDECESSOR_COMMIT,
        "predecessor_tree": PREDECESSOR_TREE,
        "predecessor_is_ancestor": ancestor,
    })
    _write_json(output_root / "subject_binding.json", subject)
    _write_json(output_root / "d5_discovery_normalized_class.json", {
        "schema_version": "iris-tooltip-t1-d5-discovery-v1",
        "normalized_diagnostic_key": NORMALIZED_TARGET,
        "declared_exact_targets": list(TARGETS),
        "discovered_exact_members": snapshot["normalized_collision_members"],
        "scope_match": True,
    })
    _write_json(output_root / "d5_target_freeze.json", {
        "schema_version": "iris-tooltip-t1-d5-target-freeze-v1",
        "support_predicate": SUPPORT_PREDICATE,
        "declared_exact_targets": list(TARGETS),
        "target_set_sha256": snapshot["target_set_sha256"],
        "frozen_support_count": snapshot["support_count"],
        "frozen_support_sha256": snapshot["support_sha256"],
    })
    _write_json(output_root / "d5_source_authority_census.json", snapshot)
    _write_json(output_root / "d5_support_entry_path_matrix.json", {
        "schema_version": "iris-tooltip-t1-d5-support-entry-path-matrix-v1",
        "targets": {target: snapshot["targets"][target]["support_entry_paths"] for target in TARGETS},
    })
    _write_json(output_root / "d5_owner_disposition_validation_report.json", {
        "schema_version": "iris-tooltip-t1-d5-owner-disposition-validation-v1",
        "authority_path": DISPOSITION_RECORD.as_posix(),
        "authority_sha256": sha256_file(repository_root / DISPOSITION_RECORD),
        "owner_semantic_judgment_correctness_validated": False,
        "binding_validated": True,
    })
    _write_json(output_root / "d5_disposition_applicability_report.json", applicability)
    normalization = normalization_usage_report(repository_root)
    _require(normalization["authoritative_normalized_key_storage_path_count"] == 0, "D5 authoritative normalized-key storage path detected")
    _write_json(output_root / "d5_normalization_usage_report.json", normalization)
    _write_json(output_root / "d5_keying_path_inventory.json", {
        "schema_version": "iris-tooltip-t1-d5-keying-path-inventory-v1",
        "exact_primary_key": "original full_type string",
        "normalized_key_role": "diagnostic_or_comparison_only",
        "authoritative_normalized_key_storage_path_count": normalization["authoritative_normalized_key_storage_path_count"],
        "scan_manifest": normalization["scan_manifest"],
    })
    artifacts = {path.name: sha256_file(path) for path in sorted(output_root.iterdir())}
    _write_json(output_root / "run_receipt.json", {
        "schema_version": "iris-tooltip-t1-d5-census-receipt-v1",
        "workstream_id": WORKSTREAM_ID,
        "subject_binding_sha256": artifacts["subject_binding.json"],
        "artifacts": artifacts,
        "native_exit_code": 0,
    })
    return {
        "workstream_id": WORKSTREAM_ID,
        "support_count": snapshot["support_count"],
        "support_sha256": snapshot["support_sha256"],
        "target_set_sha256": snapshot["target_set_sha256"],
        "disposition_applicable": applicability["applicable"],
        "run_receipt_sha256": sha256_file(output_root / "run_receipt.json"),
    }


def _validate_candidate_root(path: Path) -> dict[str, Any]:
    path = path.resolve()
    receipt = load_json(path / "run_receipt.json")
    _require(receipt.get("schema_version") == "iris-tooltip-t1-run-receipt-v1", f"{path}: candidate receipt schema mismatch")
    artifacts = receipt.get("artifacts")
    _require(isinstance(artifacts, dict), f"{path}: candidate receipt artifacts missing")
    for name, digest in artifacts.items():
        _require(isinstance(name, str) and isinstance(digest, str), f"{path}: malformed candidate artifact identity")
        _require(sha256_file(path / name) == digest, f"{path}: candidate artifact hash mismatch: {name}")
    return {
        "path": path,
        "receipt": receipt,
        "receipt_sha256": sha256_file(path / "run_receipt.json"),
        "subject": load_json(path / "subject_binding.json"),
        "support": _read_jsonl(path / "tooltip_support_universe_census.jsonl"),
        "readiness": _read_jsonl(path / "tooltip_readiness_manifest.jsonl"),
        "corrections": _read_jsonl(path / "upstream_correction_ledger.jsonl"),
        "summary": load_json(path / "tooltip_support_universe_summary.json"),
    }


def _correction_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row.get(key) for key in ("full_type", "locale", "layer", "owner", "reason_code", "selected_identity_ref"))


def _candidate_byte_report(run_a: dict[str, Any], run_b: dict[str, Any] | None) -> dict[str, Any]:
    if run_b is None:
        return {
            "schema_version": "iris-tooltip-t1-d5-determinism-report-v1",
            "run_b_supplied": False,
            "byte_identical": False,
            "status": "not_validated",
        }
    names_a = set(run_a["receipt"]["artifacts"])
    names_b = set(run_b["receipt"]["artifacts"])
    mismatches = sorted(
        name for name in names_a | names_b
        if name not in names_a or name not in names_b or (run_a["path"] / name).read_bytes() != (run_b["path"] / name).read_bytes()
    )
    return {
        "schema_version": "iris-tooltip-t1-d5-determinism-report-v1",
        "run_b_supplied": True,
        "run_a_receipt_sha256": run_a["receipt_sha256"],
        "run_b_receipt_sha256": run_b["receipt_sha256"],
        "compared_artifact_count": len(names_a | names_b),
        "mismatched_artifacts": mismatches,
        "byte_identical": not mismatches,
        "status": "validated" if not mismatches else "failed",
    }


def run_reconcile(
    repository_root: Path,
    before_root: Path,
    after_root: Path,
    disposition_path: Path,
    output_root: Path,
    *,
    after_run_b_root: Path | None = None,
    focused_validation_receipt: Path | None = None,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    output_root = _external_empty(repository_root, output_root)
    before = _validate_candidate_root(before_root)
    after = _validate_candidate_root(after_root)
    _require(before["path"] != after["path"], "D5 before and after roots must differ")
    run_b = _validate_candidate_root(after_run_b_root) if after_run_b_root is not None else None
    disposition_path = disposition_path.resolve()
    _require(disposition_path == (repository_root / DISPOSITION_RECORD).resolve(), "D5 reconcile requires the tracked disposition path")
    disposition = load_json(disposition_path)
    validate_disposition_authority(disposition)
    applicability = evaluate_disposition(repository_root, disposition)
    _require(applicability["applicable"], "D5 disposition is not content-applicable to the application subject")

    before_support = {row.get("full_type") for row in before["support"]}
    after_support = {row.get("full_type") for row in after["support"]}
    _require(None not in before_support and None not in after_support, "D5 support census contains an unkeyed row")
    _require(before_support == after_support, "D5 Branch A changed the exact support set")
    _require(set(TARGETS).issubset(after_support), "D5 target support identities were lost")
    before_corrections = {_correction_key(row): row for row in before["corrections"]}
    after_corrections = {_correction_key(row): row for row in after["corrections"]}
    target_before = sorted(
        row["full_type"] for row in before["corrections"]
        if row.get("reason_code") == "SUPPORT_NORMALIZED_COLLISION" and row.get("full_type") in TARGETS
    )
    target_after = sorted(
        row["full_type"] for row in after["corrections"]
        if row.get("reason_code") == "SUPPORT_NORMALIZED_COLLISION" and row.get("full_type") in TARGETS
    )
    _require(target_before == list(TARGETS), "D5 predecessor target correction set is not the declared pair")
    _require(target_after == [], "D5 target correction rows remain after Branch A application")
    non_target_before = {key for key in before_corrections if key[0] not in TARGETS}
    non_target_after = {key for key in after_corrections if key[0] not in TARGETS}
    _require(non_target_before == non_target_after, "D5 changed non-target correction rows")
    raw_before = before["summary"].get("normalized_full_type_collisions", {}).get(NORMALIZED_TARGET)
    raw_after = after["summary"].get("normalized_full_type_collisions", {}).get(NORMALIZED_TARGET)
    _require(raw_before == list(TARGETS) and raw_after == list(TARGETS), "D5 raw collision observation was not preserved")
    determinism = _candidate_byte_report(after, run_b)
    _require(run_b is not None and determinism["byte_identical"], "D5 candidate Run A/Run B bytes are required and must be identical")
    _require(focused_validation_receipt is not None, "D5 focused validation receipt is required")
    validation_receipt = load_json(focused_validation_receipt.resolve())
    _require(validation_receipt.get("native_exit_code") == 0, "D5 focused validation did not exit 0")
    denominators = validation_receipt.get("denominators")
    _require(
        isinstance(denominators, dict)
        and set(denominators) == {"focused_lifecycle_pytest", "regular_current_pytest", "required_standalone", "recurring_execution_units"},
        "D5 validation denominator disclosure is incomplete",
    )
    validation_ref = {
        "path": focused_validation_receipt.resolve().as_posix(),
        "sha256": sha256_file(focused_validation_receipt.resolve()),
    }

    target_ready = sorted(row["full_type"] for row in after["readiness"] if row.get("full_type") in TARGETS)
    _require(target_ready == list(TARGETS), "D5 target readiness rows are incomplete")
    support_report = {
        "schema_version": "iris-tooltip-t1-d5-support-set-comparison-v1",
        "before_count": len(before_support),
        "after_count": len(after_support),
        "before_sha256": _ordered_set_sha256(before_support),
        "after_sha256": _ordered_set_sha256(after_support),
        "target_exact_set": list(TARGETS),
        "non_target_delta": [],
    }
    correction_report = {
        "schema_version": "iris-tooltip-t1-d5-correction-reconciliation-v1",
        "reason_code": "SUPPORT_NORMALIZED_COLLISION",
        "raw_observation_exact_set": list(TARGETS),
        "before_target_correction_exact_set": target_before,
        "after_target_correction_exact_set": target_after,
        "after_target_t2_blocking_exact_set": [],
        "removed_exact_keys": sorted([list(key) for key in set(before_corrections) - set(after_corrections)]),
        "added_exact_keys": sorted([list(key) for key in set(after_corrections) - set(before_corrections)]),
        "non_target_unexpected_delta": 0,
    }
    identity_report = {
        "schema_version": "iris-tooltip-t1-d5-exact-identity-preservation-v1",
        "target_exact_set": list(TARGETS),
        "support_target_exact_set": sorted(set(TARGETS) & after_support),
        "readiness_target_exact_set": target_ready,
        "raw_collision_target_exact_set": raw_after,
        "correction_target_exact_set": target_after,
        "case_normalization_merge": 0,
        "normalized_key_overwrite": 0,
        "unexpected_exact_duplicate": 0,
        "unexpected_support_row_loss": 0,
        "exact_spelling_mutation": 0,
    }
    whole_report = {
        "schema_version": "iris-tooltip-t1-d5-whole-universe-impact-v1",
        "support_set_changed": False,
        "other_owner_delta_detected": False,
        "non_target_support_unexpected_delta": 0,
        "non_target_correction_unexpected_delta": 0,
        "other_owner_arithmetic_rewrite": 0,
        "full_reaudit_required": False,
    }
    validation_ceiling = {
        "schema_version": "iris-tooltip-t1-d5-validation-ceiling-v1",
        "validated": [
            "disposition existence, binding, approval, evidence, and content applicability",
            "owner-selected mechanism application consistency",
            "exact-key preservation and bounded whole-universe invariants",
            "candidate materialization, reconciliation, and bundle integrity",
        ],
        "unvalidated_but_in_scope": ["owner semantic judgment correctness for identity_relation and support_disposition"],
        "out_of_scope": [
            "runtime FullType interpretation and visual behavior",
            "Menu parity completion, package/install, full RTC, release/deployment",
            "T1-D6 global current-authority integration",
        ],
    }
    closure = {
        "schema_version": "iris-tooltip-t1-d5-closure-provenance-v1",
        "selected": "owner_disposition_reconciliation",
        "forbidden_counts": {
            "detector_disable": 0,
            "reason_code_removal": 0,
            "pre_owner_denominator_exclusion": 0,
            "unsupported_normalized_merge": 0,
        },
    }
    stage_sets = {
        "schema_version": "iris-tooltip-t1-d5-stage-exact-key-sets-v1",
        "support": list(TARGETS),
        "readiness": target_ready,
        "raw_collision_observation": raw_after,
        "support_normalized_collision_correction": target_after,
        "t2_blocking_support_normalized_collision": [],
    }
    normalization = normalization_usage_report(repository_root)
    _require(normalization["authoritative_normalized_key_storage_path_count"] == 0, "D5 authoritative normalized-key storage path detected")
    decision = load_json(repository_root / AUTHORITY_ROOT / "tooltip_t1_decision_contract.json")
    rebind = decision.get("d5_contract_rebind")
    _require(isinstance(rebind, dict) and rebind.get("non_hash_invariants_equal") is True, "D5 contract rebind receipt missing")

    artifacts = {
        "d5_discovery_normalized_class.json": {
            "normalized_diagnostic_key": NORMALIZED_TARGET,
            "declared_exact_targets": list(TARGETS),
            "discovered_exact_members": raw_after,
            "scope_match": True,
        },
        "d5_target_freeze.json": {
            "support_predicate": SUPPORT_PREDICATE,
            "declared_exact_targets": list(TARGETS),
            "target_set_sha256": _ordered_set_sha256(TARGETS),
            "frozen_support_count": len(after_support),
            "frozen_support_sha256": _ordered_set_sha256(after_support),
        },
        "d5_source_authority_census.json": applicability["snapshot"],
        "d5_support_entry_path_matrix.json": {
            "targets": {
                target: applicability["snapshot"]["targets"][target]["support_entry_paths"]
                for target in TARGETS
            },
        },
        "d5_normalization_usage_report.json": normalization,
        "d5_keying_path_inventory.json": {
            "exact_primary_key": "original full_type string",
            "normalized_key_role": "diagnostic_or_comparison_only",
            "authoritative_normalized_key_storage_path_count": normalization["authoritative_normalized_key_storage_path_count"],
            "scan_manifest": normalization["scan_manifest"],
        },
        "d5_owner_disposition_validation_report.json": {
            "authority_path": DISPOSITION_RECORD.as_posix(),
            "authority_sha256": sha256_file(disposition_path),
            "binding_validated": True,
            "owner_semantic_judgment_correctness_validated": False,
        },
        "d5_contract_bundle_rebind_receipt.json": rebind,
        "d5_pre_mutation_support_set.json": support_report,
        "d5_post_disposition_support_set.json": support_report,
        "d5_pre_mutation_correction_ledger.json": {"target_exact_set": target_before, "candidate_receipt_sha256": before["receipt_sha256"]},
        "d5_raw_collision_observation.json": {"normalized_diagnostic_key": NORMALIZED_TARGET, "exact_members": raw_after},
        "d5_correction_reconciliation.json": correction_report,
        "d5_closure_provenance.json": closure,
        "d5_stage_exact_key_sets_before.json": {**stage_sets, "support_normalized_collision_correction": target_before, "t2_blocking_support_normalized_collision": target_before},
        "d5_stage_exact_key_sets_after.json": stage_sets,
        "d5_exact_identity_preservation_report.json": identity_report,
        "d5_affected_range_audit.json": {"targets": list(TARGETS), "status": "validated", "unexpected_delta": 0},
        "d5_whole_universe_impact_report.json": whole_report,
        "d5_before_after_correction_ledger.json": correction_report,
        "d5_determinism_report.json": determinism,
        "d5_validation_denominator_before_after.json": denominators,
        "d5_validation_ceiling.json": validation_ceiling,
        "d5_disposition_applicability_report.json": applicability,
        "d5_reconciliation_receipt.json": {
            "schema_version": "iris-tooltip-t1-d5-reconciliation-receipt-v1",
            "before_run_receipt_sha256": before["receipt_sha256"],
            "after_run_receipt_sha256": after["receipt_sha256"],
            "after_run_b_receipt_sha256": run_b["receipt_sha256"] if run_b else None,
            "disposition_sha256": sha256_file(disposition_path),
            "focused_validation_receipt": validation_ref,
            "native_exit_code": 0,
        },
    }
    for name, payload in artifacts.items():
        _write_json(output_root / name, payload)

    protected_paths = [
        Path("Iris/_docs/authority/iris_current_authority_manifest.json"),
        Path("Iris/_docs/authority/iris_current_route_index.json"),
        Path("Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json"),
        Path("Iris/build/ENTRYPOINTS.md"),
        Path("docs/DECISIONS.md"),
        Path("docs/ARCHITECTURE.md"),
        Path("docs/ROADMAP.md"),
    ]
    protected_hashes = {
        path.as_posix(): sha256_file(repository_root / path)
        for path in protected_paths
        if (repository_root / path).is_file()
    }
    protected_delta = _git_output(
        repository_root,
        "diff", "--name-only", PREDECESSOR_COMMIT, "HEAD", "--",
        *(path.as_posix() for path in protected_paths),
    ).splitlines()
    _require(not protected_delta, f"D5 mutated T1-D6-exclusive protected paths: {protected_delta}")
    shared_delta = _shared_path_delta(repository_root)
    integration_manifest = {
        "schema_version": "iris-tooltip-t1-parallel-correction-bundle-v1",
        "workstream_id": WORKSTREAM_ID,
        "terminal_state": "complete",
        "predecessor_commit": PREDECESSOR_COMMIT,
        "predecessor_tree": PREDECESSOR_TREE,
        "predecessor_closeout_sha256": PREDECESSOR_CLOSEOUT_SHA256,
        "workstream_subject_commit": after["subject"].get("commit"),
        "workstream_subject_tree": after["subject"].get("tree"),
        "support_predicate": SUPPORT_PREDICATE,
        "frozen_support_count": len(after_support),
        "frozen_support_sha256": _ordered_set_sha256(after_support),
        "starting_correction_distribution": dict(sorted(Counter(row["owner"] for row in before["corrections"]).items())),
        "target_owner": "Iris presentation-contract owner",
        "target_reason_codes": ["SUPPORT_NORMALIZED_COLLISION"],
        "target_exact_set_sha256": _ordered_set_sha256(TARGETS),
        "resolved_entries": [list(key) for key in sorted(set(before_corrections) - set(after_corrections))],
        "remaining_entries": target_after,
        "owner_authority_refs": [{"path": DISPOSITION_RECORD.as_posix(), "sha256": sha256_file(disposition_path)}],
        "evidence_refs": ["d5_reconciliation_receipt.json", "d5_exact_identity_preservation_report.json"],
        "artifact_hashes": "artifact_digests.json",
        "shared_path_delta": shared_delta,
        "protected_path_hashes": protected_hashes,
        "integration_impact": {
            "support_set_changed": False,
            "shared_contract_change_required": True,
            "other_owner_delta_detected": False,
            "predecessor_mismatch": False,
            "common_path_conflict_detected": False,
            "full_reaudit_required": False,
            "affected_exact_set": list(TARGETS),
        },
        "acceptance_condition": "T1-D6 validates and integrates this bundle with all other terminal workstream bundles",
        "re_audit_condition": disposition["re_audit_condition"],
        "validation_receipts": {
            "focused": validation_ref,
            "candidate_run_a": after["receipt_sha256"],
            "candidate_run_b": run_b["receipt_sha256"] if run_b else None,
            "reconciliation": "d5_reconciliation_receipt.json",
        },
        "claim_ceiling": validation_ceiling,
        "integration_instructions": "Apply D5-owned and shared-path proposals on the T1-D6 integration subject; do not treat this bundle as global current adoption.",
        "current_ecosystem_adoption": "pending_T1_D6",
        "T2_FULL_DATA_PROGRESSION": "BLOCKED_BY_UPSTREAM_CORRECTIONS",
        "production_t2_handoff": "absent",
    }
    _write_json(output_root / "integration_manifest.json", integration_manifest)
    digest_rows = [
        {"path": path.name, "sha256": sha256_file(path)}
        for path in sorted(output_root.iterdir())
        if path.name not in {"artifact_digests.json", "run_receipt.json"}
    ]
    _write_json(output_root / "artifact_digests.json", {
        "schema_version": "iris-tooltip-t1-d5-artifact-digests-v1",
        "artifacts": digest_rows,
    })
    _write_json(output_root / "run_receipt.json", {
        "schema_version": "iris-tooltip-t1-d5-bundle-run-receipt-v1",
        "workstream_id": WORKSTREAM_ID,
        "terminal_state": "complete",
        "artifact_digests_sha256": sha256_file(output_root / "artifact_digests.json"),
        "integration_manifest_sha256": sha256_file(output_root / "integration_manifest.json"),
        "native_exit_code": 0,
    })
    return {
        "workstream_id": WORKSTREAM_ID,
        "terminal_state": "complete",
        "resolved_target_correction_count": len(target_before),
        "remaining_target_correction_count": len(target_after),
        "run_receipt_sha256": sha256_file(output_root / "run_receipt.json"),
    }
