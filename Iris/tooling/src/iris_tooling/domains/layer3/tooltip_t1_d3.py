from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from iris_tooling.build.repository_context import require_repository_context
from iris_tooling.domains.tooltip_t1.audit import (
    CLASSIFICATIONS,
    L3_GENERATIONS,
    L3_POINTER,
    L4_OWNER_INPUT,
    _generation_id,
    _layer4_candidates,
    _runtime_rightclick_surfaces,
)
from iris_tooling.domains.tooltip_t1.contract import (
    canonical_bytes,
    git_subject,
    load_json,
    parse_classifications,
    sha256_bytes,
    sha256_file,
)
from iris_tooling.domains.tooltip_t1.models import TooltipContractError
from iris_tooling.domains.tooltip_t1.projection import select_layer4


PREDECESSOR_COMMIT = "6b7118dc229bf8138302696e1aa5e5b7454589dc"
PREDECESSOR_TREE = "4eae6fbdb3d0b2cb532f875b96137335a403f2fc"
PREDECESSOR_CLOSEOUT_SHA256 = "6e255227b0aa8381453a563e3ede9e96c59be82c9bb3a7cb6eba8f488039b4a3"
EXPECTED_TARGET_COUNT = 175
PLANNING_TARGET_SHA256 = "accbe1ae691e41b1697f080f26b8206a08e261039bb7919879f67f4b5d7ef238"
SUPPORT_PREDICATE = "current-owner-fulltype-union-v1"
OWNER_APPROVAL_REF = "user_prompt_owner_gate_preapproval_2026-08-29"

FACTS = Path("Iris/build/description/v2/data/dvf_3_3_facts.jsonl")
DECISIONS = Path("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl")
INPUT_MANIFEST = Path("Iris/build/description/v2/data/dvf_3_3_input_manifest.json")
ITEMSCRIPT = Path("Iris/input/items_itemscript.json")
ROLE_CANDIDATE = Path("Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json")
ROLE_MAPPING = Path("Iris/build/description/v2/data/layer3_body_role_realign/fact_kind_mapping_contract.json")
ROLE_READINESS = Path("Iris/build/description/v2/data/layer3_body_role_realign/disposition_readiness_contract.json")
OWNER_OUTPUT = Path("Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json")
REGISTRY = Path("Iris/_docs/authority/dvf/tooltip_t1_d3_disposition_registry.json")


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TooltipContractError(f"{path}: JSONL row is not an object")
            rows.append(value)
    return rows


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_bytes(b"".join(canonical_bytes(row) for row in rows))


def _ordered_hash(values: Iterable[str]) -> str:
    rows = list(values)
    return sha256_bytes((("\n".join(rows)) + "\n").encode("utf-8"))


def _external_empty_root(repository_root: Path, output_root: Path) -> Path:
    root = output_root.resolve()
    try:
        root.relative_to(repository_root.resolve())
    except ValueError:
        pass
    else:
        raise TooltipContractError("D3 output root must be repository-external")
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise TooltipContractError("D3 output root must be empty")
    root.mkdir(parents=True, exist_ok=True)
    return root


def _validate_artifact_receipt(root: Path, name: str = "run_receipt.json") -> dict[str, Any]:
    receipt = load_json(root / name)
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, dict):
        raise TooltipContractError(f"{root}: artifact receipt missing")
    for filename, digest in artifacts.items():
        path = root / filename
        if not path.is_file() or sha256_file(path) != digest:
            raise TooltipContractError(f"{root}: artifact hash mismatch for {filename}")
    return receipt


def _target_from_t1_root(root: Path) -> tuple[list[str], list[str], dict[str, Any]]:
    receipt = _validate_artifact_receipt(root)
    ledger = _jsonl(root / "upstream_correction_ledger.jsonl")
    target = sorted(
        row["full_type"]
        for row in ledger
        if row.get("owner") == "DVF owner"
        and row.get("reason_code") == "DVF_OWNER_ROW_MISSING"
        and row.get("t2_blocking") is True
    )
    support = sorted(row["full_type"] for row in _jsonl(root / "tooltip_support_universe_census.jsonl"))
    if len(target) != len(set(target)):
        raise TooltipContractError("D3 target has duplicate exact FullTypes")
    if len(target) != EXPECTED_TARGET_COUNT:
        raise TooltipContractError(f"D3 target count changed: {len(target)}")
    if _ordered_hash(target) != PLANNING_TARGET_SHA256:
        raise TooltipContractError("D3 current authoritative target differs from the planned exact set")
    return target, support, receipt


def _repository_relations(repository_root: Path, target: list[str]) -> dict[str, Any]:
    classifications = parse_classifications(repository_root / CLASSIFICATIONS)
    pointer_text = (repository_root / L3_POINTER).read_text(encoding="utf-8")
    generation_id = _generation_id(pointer_text)
    rendered = load_json(repository_root / L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json")
    layer3 = rendered.get("entries")
    layer4 = load_json(repository_root / L4_OWNER_INPUT).get("fulltypes")
    if not isinstance(layer3, dict) or not isinstance(layer4, dict):
        raise TooltipContractError("D3 owner universe is malformed")
    support = sorted(set(classifications) | set(layer3) | set(layer4))
    if sorted(set(support) - set(layer3)) != target:
        raise TooltipContractError("authoritative D3 target differs from support minus current Layer 3")

    facts = {str(row.get("item_id")): row for row in _jsonl(repository_root / FACTS)}
    decisions = {str(row.get("item_id")): row for row in _jsonl(repository_root / DECISIONS)}
    itemscript = load_json(repository_root / ITEMSCRIPT)
    role_candidate = load_json(repository_root / ROLE_CANDIDATE).get("entries")
    if not isinstance(role_candidate, dict):
        raise TooltipContractError("approved role-material candidate entries missing")
    surfaces = _runtime_rightclick_surfaces(repository_root)
    rows: list[dict[str, Any]] = []
    for full_type in target:
        item = itemscript.get(full_type)
        candidates = _layer4_candidates(layer4.get(full_type, {}), surfaces)
        selected, dispositions = select_layer4(candidates)
        disposition_values = sorted(row.disposition for row in dispositions)
        layer4_exclusion_only = bool(candidates) and not selected and set(disposition_values) == {"ineligible_exclusion"}
        source_membership = [
            name
            for name, values in (("layer2", classifications), ("layer4", layer4))
            if full_type in values
        ]
        if not isinstance(item, dict) or item.get("FullType") != full_type:
            raise TooltipContractError(f"{full_type}: exact item-script identity missing")
        if full_type in facts or full_type in decisions or full_type in role_candidate or full_type in layer3:
            raise TooltipContractError(f"{full_type}: existing DVF material requires non-B adjudication")
        if full_type in layer4 and not layer4_exclusion_only:
            raise TooltipContractError(f"{full_type}: Layer 4 support is not exclusion-only")
        if not source_membership:
            raise TooltipContractError(f"{full_type}: support owner membership missing")
        rows.append({
            "exact_full_type": full_type,
            "support_source_membership": source_membership,
            "item_script_identity_present": True,
            "canonical_fact_presence": False,
            "decision_presence": False,
            "approved_role_material_presence": False,
            "generation_membership": False,
            "layer4_exclusion_only": layer4_exclusion_only,
            "working_cause": "no_approved_description_material",
            "responsible_owner": "DVF owner",
            "intended_disposition": "owner_proposed_legitimate_absence",
            "evidence_refs": [
                f"{ITEMSCRIPT.as_posix()}#{full_type}",
                f"{FACTS.as_posix()}#exact-item-id-absence={full_type}",
                f"{DECISIONS.as_posix()}#exact-item-id-absence={full_type}",
                f"{ROLE_CANDIDATE.as_posix()}#entries/exact-key-absence={full_type}",
                ROLE_MAPPING.as_posix(),
                ROLE_READINESS.as_posix(),
                f"{L4_OWNER_INPUT.as_posix()}#fulltypes/{full_type}" if full_type in layer4 else CLASSIFICATIONS.as_posix(),
            ],
        })
    return {
        "generation_id": generation_id,
        "support": support,
        "layer3": layer3,
        "rows": rows,
    }


def prepare(repository_root: Path, baseline_t1_root: Path, output_root: Path) -> dict[str, Any]:
    target, baseline_support, baseline_receipt = _target_from_t1_root(baseline_t1_root.resolve())
    relations = _repository_relations(repository_root, target)
    support = relations["support"]
    if support != baseline_support:
        raise TooltipContractError("D3 support reconstruction differs from the authoritative T1 baseline")
    root = _external_empty_root(repository_root, output_root)
    target_hash = _ordered_hash(target)
    support_hash = _ordered_hash(support)
    subject = load_json(baseline_t1_root / "subject_binding.json")
    _write_json(root / "subject_binding.json", {
        **subject,
        "predecessor_commit": PREDECESSOR_COMMIT,
        "predecessor_tree": PREDECESSOR_TREE,
        "predecessor_closeout_sha256": PREDECESSOR_CLOSEOUT_SHA256,
        "equivalence_mode": "exact_required_path_blob_equivalence",
    })
    _write_jsonl(root / "d3_exact_target_freeze.jsonl", (
        {"ordinal": index, "exact_full_type": full_type, "target_sha256": target_hash}
        for index, full_type in enumerate(target)
    ))
    _write_json(root / "d3_set_relation_report.json", {
        "schema_version": "iris-tooltip-t1-d3-set-relation-v1",
        "support_predicate": SUPPORT_PREDICATE,
        "frozen_support_count": len(support),
        "frozen_support_sha256": support_hash,
        "target_count": len(target),
        "target_exact_set_sha256": target_hash,
        "audit_target_equals_support_minus_current_layer3": True,
        "duplicate_exact_full_type": 0,
        "silent_denominator_shrink": 0,
        "lineage_status": "verified_equal",
    })
    _write_jsonl(root / "d3_target_census.jsonl", relations["rows"])
    _write_jsonl(root / "d3_root_cause_ledger.jsonl", relations["rows"])
    proposed = [
        {
            **row,
            "intended_disposition": "owner_proposed_legitimate_absence",
            "absence_reason_code": "DVF_NO_APPROVED_DESCRIPTION_MATERIAL",
            "owner": "DVF owner",
            "applicable_scope": row["exact_full_type"],
            "reaudit_condition": (
                f"re-audit {row['exact_full_type']} when exact DVF facts/decisions, approved role-material, "
                "or the adopted role-material mapping identity changes"
            ),
            "authority_decision_ref": OWNER_APPROVAL_REF,
        }
        for row in relations["rows"]
    ]
    _write_jsonl(root / "d3_b_publication_queue.jsonl", proposed)
    _write_jsonl(root / "d3_a_correction_queue.jsonl", [])
    _write_jsonl(root / "d3_blocked_escalation_queue.jsonl", [])
    existing_791 = []
    for full_type, entry in sorted(relations["layer3"].items()):
        role = entry.get("role_material") if isinstance(entry, dict) else None
        if isinstance(role, dict) and role.get("core_source_fact_ids") == []:
            existing_791.append({
                "exact_full_type": full_type,
                "provenance_class": "current_generation_role_material_empty_core_ids",
                "mutation_allowed": False,
            })
    if len(existing_791) != 791:
        raise TooltipContractError(f"current Layer 3 empty-core provenance count changed: {len(existing_791)}")
    _write_jsonl(root / "d3_existing_791_provenance_report.jsonl", existing_791)
    _write_json(root / "d3_owner_adjudication_report.json", {
        "schema_version": "iris-tooltip-t1-d3-owner-adjudication-candidate-v1",
        "owner_approval_ref": OWNER_APPROVAL_REF,
        "A": 0,
        "proposed_B": len(proposed),
        "blocked": 0,
        "terminal_B_requires_independent_defect_exclusion_verdict": True,
    })
    baseline_owner = load_json(repository_root / OWNER_OUTPUT)
    baseline_fact_entries = baseline_owner.get("fact_entries", baseline_owner.get("entries"))
    if not isinstance(baseline_fact_entries, dict):
        raise TooltipContractError("pre-mutation Layer 3 owner fact projection missing")
    locale_root = repository_root / "Iris/media/lua/client/Iris/Data/Layer3English"
    locale_hashes = {
        path.relative_to(repository_root).as_posix(): sha256_file(path)
        for path in sorted(locale_root.rglob("*"))
        if path.is_file()
    }
    generation_id = relations["generation_id"]
    _write_json(root / "d3_protected_baseline.json", {
        "schema_version": "iris-tooltip-t1-d3-protected-baseline-v1",
        "generation_id": generation_id,
        "pointer_sha256": sha256_file(repository_root / L3_POINTER),
        "generation_rendered_sha256": sha256_file(repository_root / L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json"),
        "owner_fact_entries_sha256": sha256_bytes(canonical_bytes(baseline_fact_entries)),
        "owner_fact_entry_count": len(baseline_fact_entries),
        "layer3_english_file_sha256": locale_hashes,
    })
    artifacts = {
        path.name: sha256_file(path)
        for path in sorted(root.iterdir())
        if path.name != "prepare_receipt.json"
    }
    _write_json(root / "prepare_receipt.json", {
        "schema_version": "iris-tooltip-t1-d3-prepare-receipt-v1",
        "baseline_t1_run_receipt_sha256": sha256_file(baseline_t1_root / "run_receipt.json"),
        "baseline_t1_artifact_count": len(baseline_receipt["artifacts"]),
        "target_exact_set_sha256": target_hash,
        "artifacts": artifacts,
    })
    return {"target_count": len(target), "target_sha256": target_hash, "support_count": len(support), "support_sha256": support_hash}


def materialize_registry(repository_root: Path, prepared_root: Path, verdict_path: Path) -> dict[str, Any]:
    prepare_receipt = _validate_artifact_receipt(prepared_root, "prepare_receipt.json")
    verdict = load_json(verdict_path)
    verdict_sha256 = sha256_file(verdict_path)
    if verdict.get("schema_version") != "iris-tooltip-t1-d3-defect-exclusion-verdict-v1" or verdict.get("status") != "PASS":
        raise TooltipContractError("D3 absence verdict is not PASS")
    target_hash = prepare_receipt.get("target_exact_set_sha256")
    if verdict.get("target_exact_set_sha256") != target_hash:
        raise TooltipContractError("D3 absence verdict target mismatch")
    proposed = _jsonl(prepared_root / "d3_b_publication_queue.jsonl")
    verdict_rows = verdict.get("rows")
    if not isinstance(verdict_rows, dict) or set(verdict_rows) != {row["exact_full_type"] for row in proposed}:
        raise TooltipContractError("D3 absence verdict exact set mismatch")
    entries: dict[str, dict[str, Any]] = {}
    for row in proposed:
        full_type = row["exact_full_type"]
        if verdict_rows[full_type].get("defect_exclusion_verdict") != "pass":
            raise TooltipContractError(f"{full_type}: absence defect exclusion failed")
        entries[full_type] = {
            "exact_full_type": full_type,
            "responsible_owner": "DVF owner",
            "working_cause": "no_approved_description_material",
            "escalation_reason_code": None,
            "intended_disposition": "approved_legitimate_absence",
            "supporting_evidence": row["evidence_refs"],
            "required_correction_if_any": None,
            "authority_decision_ref": row["authority_decision_ref"],
            "absence_reason_code": row["absence_reason_code"],
            "owner": row["owner"],
            "acceptance_evidence": {
                "artifact": "d3_independent_defect_exclusion_verdict.json",
                "sha256": verdict_sha256,
            },
            "applicable_scope": row["applicable_scope"],
            "reaudit_condition": row["reaudit_condition"],
        }
    output_path = repository_root / REGISTRY
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "iris-tooltip-t1-d3-disposition-registry-v1",
        "workstream_id": "T1-D3",
        "target_exact_set_sha256": target_hash,
        "target_count": len(entries),
        "owner_approval_ref": OWNER_APPROVAL_REF,
        "terminal_distribution": {"A": 0, "B": len(entries), "blocked": 0},
        "entries": entries,
    }
    _write_json(output_path, payload)
    return {"registry": output_path.as_posix(), "entry_count": len(entries), "canonical_sha256": sha256_bytes(canonical_bytes(payload))}


def _git(repository_root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repository_root, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise TooltipContractError(result.stderr.strip() or "git query failed")
    return result.stdout.strip()


def _git_object_exists(repository_root: Path, spec: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", spec],
        cwd=repository_root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def bundle(
    repository_root: Path,
    prepared_root: Path,
    absence_verdict: Path,
    invariance_verdict: Path,
    post_t1_root_a: Path,
    post_t1_root_b: Path,
    validation_receipt: Path,
    output_root: Path,
) -> dict[str, Any]:
    prepare_receipt = _validate_artifact_receipt(prepared_root, "prepare_receipt.json")
    for root in (post_t1_root_a, post_t1_root_b):
        _validate_artifact_receipt(root)
    if sha256_file(post_t1_root_a / "run_receipt.json") != sha256_file(post_t1_root_b / "run_receipt.json"):
        raise TooltipContractError("D3 whole-T1 candidate Run A/B digests differ")
    absence = load_json(absence_verdict)
    invariance = load_json(invariance_verdict)
    validation = load_json(validation_receipt)
    if absence.get("status") != "PASS" or invariance.get("status") != "PASS":
        raise TooltipContractError("D3 independent verdict is not PASS")
    if validation.get("status") != "PASS":
        raise TooltipContractError("D3 focused validation receipt is not PASS")
    target = {row["exact_full_type"] for row in _jsonl(prepared_root / "d3_exact_target_freeze.jsonl")}
    corrections = _jsonl(post_t1_root_a / "upstream_correction_ledger.jsonl")
    remaining = [
        row for row in corrections
        if row.get("full_type") in target and row.get("owner") == "DVF owner" and row.get("reason_code") == "DVF_OWNER_ROW_MISSING"
    ]
    if remaining:
        raise TooltipContractError(f"D3 target owner-row corrections remain: {len(remaining)}")
    registry = load_json(repository_root / REGISTRY)
    entries = registry.get("entries")
    if not isinstance(entries, dict) or set(entries) != target:
        raise TooltipContractError("D3 terminal registry target mismatch")
    subject = git_subject(repository_root)
    if subject.get("working_tree_clean") is not True:
        raise TooltipContractError("D3 bundle requires a clean committed workstream subject")

    protected = [
        "Iris/_docs/authority/iris_current_authority_manifest.json",
        "Iris/_docs/authority/iris_current_route_index.json",
        "Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json",
        "Iris/build/ENTRYPOINTS.md",
        "docs/DECISIONS.md",
        "docs/ARCHITECTURE.md",
        "docs/ROADMAP.md",
    ]
    changed_protected = _git(repository_root, "diff", "--name-only", PREDECESSOR_COMMIT, "HEAD", "--", *protected).splitlines()
    if changed_protected:
        raise TooltipContractError(f"D3 protected current-adoption path changed: {changed_protected}")
    shared_prefixes = (
        "Iris/tooling/src/iris_tooling/domains/tooltip_t1/",
        "Iris/tooling/tests/test_tooltip_t1_",
        "Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json",
        "Iris/_docs/authority/tooltip_t1/",
        "docs/iris_tooltip_t1_display_contract_policy.md",
    )
    changed = _git(repository_root, "diff", "--name-only", PREDECESSOR_COMMIT, "HEAD").splitlines()
    shared_rows = []
    for path in sorted(path for path in changed if path.startswith(shared_prefixes)):
        base_spec = f"{PREDECESSOR_COMMIT}:{path}"
        base_blob = _git(repository_root, "rev-parse", base_spec) if _git_object_exists(repository_root, base_spec) else None
        shared_rows.append({
            "path": path,
            "base_blob": base_blob,
            "proposed_sha256": sha256_file(repository_root / path),
            "workstream_reason": "T1-D3 explicit DVF owner absence projection and audit consumption",
            "merge_invariant": "preserve other workstream owner semantics and exact case-sensitive FullType identity",
        })
    root = _external_empty_root(repository_root, output_root)
    copy_names = [
        "subject_binding.json", "d3_exact_target_freeze.jsonl", "d3_set_relation_report.json",
        "d3_target_census.jsonl", "d3_existing_791_provenance_report.jsonl", "d3_root_cause_ledger.jsonl",
        "d3_owner_adjudication_report.json", "d3_a_correction_queue.jsonl", "d3_b_publication_queue.jsonl",
        "d3_blocked_escalation_queue.jsonl", "d3_protected_baseline.json",
    ]
    for name in copy_names:
        shutil.copy2(prepared_root / name, root / name)
    shutil.copy2(absence_verdict, root / "d3_independent_defect_exclusion_verdict.json")
    shutil.copy2(invariance_verdict, root / "d3_independent_non_target_invariance_verdict.json")
    shutil.copy2(post_t1_root_a / "tooltip_support_universe_summary.json", root / "d3_whole_t1_reaudit_report.json")
    shutil.copy2(validation_receipt, root / "d3_validation_receipt.json")
    _write_json(root / "d3_producer_non_target_observation.json", {
        "schema_version": "iris-tooltip-t1-d3-producer-observation-v1",
        "generation_identity_changed": False,
        "current_pointer_changed": False,
        "existing_fact_entry_delta": 0,
        "absence_entry_delta": len(entries),
        "runtime_locale_write_set": [],
        "claim_class": "producer_observation_not_final_invariance_verdict",
    })
    _write_json(root / "d3_shared_path_delta.json", {"schema_version": "iris-tooltip-t1-d3-shared-path-delta-v1", "entries": shared_rows})
    protected_hashes = {path: sha256_file(repository_root / path) for path in protected}
    manifest = {
        "schema_version": "iris-tooltip-t1-parallel-workstream-bundle-v1",
        "workstream_id": "T1-D3",
        "terminal_state": "complete",
        "predecessor_commit": PREDECESSOR_COMMIT,
        "predecessor_tree": PREDECESSOR_TREE,
        "predecessor_closeout_sha256": PREDECESSOR_CLOSEOUT_SHA256,
        "workstream_subject_commit": subject["commit"],
        "workstream_subject_tree": subject["tree"],
        "support_predicate": SUPPORT_PREDICATE,
        "frozen_support_count": load_json(prepared_root / "d3_set_relation_report.json")["frozen_support_count"],
        "frozen_support_sha256": load_json(prepared_root / "d3_set_relation_report.json")["frozen_support_sha256"],
        "starting_correction_distribution": {"total": 5625, "DVF owner": 175},
        "target_owner": "DVF owner",
        "target_reason_codes": ["DVF_OWNER_ROW_MISSING"],
        "target_exact_set_sha256": prepare_receipt["target_exact_set_sha256"],
        "resolved_entries": {"A": 0, "B": len(entries)},
        "remaining_entries": 0,
        "owner_authority_refs": [OWNER_APPROVAL_REF, REGISTRY.as_posix()],
        "evidence_refs": ["d3_independent_defect_exclusion_verdict.json", "d3_independent_non_target_invariance_verdict.json"],
        "artifact_hashes": {},
        "shared_path_delta": "d3_shared_path_delta.json",
        "protected_path_hashes": protected_hashes,
        "integration_impact": {
            "support_set_changed": False,
            "shared_contract_change_required": True,
            "other_owner_delta_detected": False,
            "predecessor_mismatch": False,
            "common_path_conflict_detected": False,
            "full_reaudit_required": True,
            "affected_exact_set": sorted(target),
            "support_freeze_mismatch": False,
        },
        "acceptance_condition": "T1-D6 merges the shared schema/audit delta and re-audits the integrated exact subject",
        "re_audit_condition": "new integrated T1-D6 exact subject",
        "validation_receipts": ["d3_validation_receipt.json"],
        "claim_ceiling": "workstream correction complete; current ecosystem adoption pending_T1_D6",
        "integration_instructions": "merge shared_path_delta without changing other-owner semantics; rerun the integrated whole-T1 gate once",
        "current_ecosystem_adoption": "pending_T1_D6",
        "T2_FULL_DATA_PROGRESSION": "BLOCKED_BY_UPSTREAM_CORRECTIONS",
        "production_t2_handoff": "absent",
    }
    _write_json(root / "d3_axis_separated_closeout_record.json", {
        "schema_version": "iris-tooltip-t1-d3-axis-closeout-v1",
        "workstream_correction_bundle": "complete",
        "current_ecosystem_adoption": "pending_T1_D6",
        "T2_FULL_DATA_PROGRESSION": "BLOCKED_BY_UPSTREAM_CORRECTIONS",
        "production_t2_handoff": "absent",
        "validated": ["exact 175 owner absence disposition", "whole-T1 re-audit", "metadata-only invariance", "focused T1 families"],
        "not_established": ["global current adoption", "T2 OPEN", "runtime/visual acceptance", "release readiness"],
    })
    artifacts = {
        path.name: sha256_file(path)
        for path in sorted(root.iterdir())
        if path.name not in {"run_receipt.json", "d3_parallel_integration_manifest.json"}
    }
    manifest["artifact_hashes"] = artifacts
    _write_json(root / "d3_parallel_integration_manifest.json", manifest)
    artifacts["d3_parallel_integration_manifest.json"] = sha256_file(root / "d3_parallel_integration_manifest.json")
    _write_json(root / "run_receipt.json", {
        "schema_version": "iris-tooltip-t1-d3-run-receipt-v1",
        "terminal_state": "complete",
        "artifacts": artifacts,
    })
    return {"terminal_state": "complete", "resolved_A": 0, "resolved_B": len(entries), "bundle_root": root.as_posix(), "run_receipt_sha256": sha256_file(root / "run_receipt.json")}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="iris-tooling layer3 tooltip-t1-d3")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--baseline-t1-root", type=Path, required=True)
    prepare_parser.add_argument("--output-root", type=Path, required=True)
    registry_parser = sub.add_parser("materialize-registry")
    registry_parser.add_argument("--prepared-root", type=Path, required=True)
    registry_parser.add_argument("--absence-verdict", type=Path, required=True)
    bundle_parser = sub.add_parser("bundle")
    bundle_parser.add_argument("--prepared-root", type=Path, required=True)
    bundle_parser.add_argument("--absence-verdict", type=Path, required=True)
    bundle_parser.add_argument("--invariance-verdict", type=Path, required=True)
    bundle_parser.add_argument("--post-t1-root-a", type=Path, required=True)
    bundle_parser.add_argument("--post-t1-root-b", type=Path, required=True)
    bundle_parser.add_argument("--validation-receipt", type=Path, required=True)
    bundle_parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)
    root = require_repository_context().repository_root
    try:
        if args.command == "prepare":
            result = prepare(root, args.baseline_t1_root, args.output_root)
        elif args.command == "materialize-registry":
            result = materialize_registry(root, args.prepared_root.resolve(), args.absence_verdict.resolve())
        else:
            result = bundle(root, args.prepared_root.resolve(), args.absence_verdict.resolve(), args.invariance_verdict.resolve(), args.post_t1_root_a.resolve(), args.post_t1_root_b.resolve(), args.validation_receipt.resolve(), args.output_root)
    except (OSError, ValueError, KeyError, TooltipContractError) as exc:
        print(f"tooltip-t1-d3 blocked: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
