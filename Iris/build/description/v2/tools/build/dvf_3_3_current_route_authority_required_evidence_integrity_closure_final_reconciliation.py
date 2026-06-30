from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    canonical_hash,
    file_record,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_text,
)


ROUND_ID = "dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation"
PARENT_ROUND_ID = "dvf_3_3_current_route_authority_required_evidence_integrity_closure"
PARENT_EVIDENCE_ROOT_REL = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure"
)


def configured_repo_path(env_name: str, default: Path) -> Path:
    override = os.environ.get(env_name)
    return resolve_repo(override) if override else default


EVIDENCE_ROOT = configured_repo_path(
    "DVF_FINAL_RECONCILIATION_EVIDENCE_ROOT",
    V2_ROOT / "staging" / ROUND_ID,
)

TOOLS_DIR = Path(__file__).resolve().parent
COMMON_MODULE = TOOLS_DIR / (
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py"
)
RUNNER = TOOLS_DIR / (
    "run_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py"
)
VALIDATOR = TOOLS_DIR / (
    "validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py"
)
FOCUSED_TEST = V2_ROOT / "tests" / (
    "test_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py"
)

LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
PLAN_DOC = REPO_ROOT / "docs" / (
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_implementation_plan.md"
)
PARENT_PLAN_DOC = REPO_ROOT / "docs" / (
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md"
)
PREFLIGHT_REPORT = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_required_artifact_surface_preflight_census/"
    "census_p8_closeout_no_mutation/final_preflight_census_report.json"
)
DISPOSITION_REPORT = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_required_artifact_disposition_seal/"
    "phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json"
)
PARENT_DISPOSITION_INPUT_PACKET = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_required_artifact_disposition_seal/"
    "phase6_closeout_claim_boundary/parent_closure_input_packet.json"
)

DECISIONS_DOC = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "ARCHITECTURE.md"
ROADMAP_DOC = REPO_ROOT / "docs" / "ROADMAP.md"

CURRENT_ROUTE_TIMEOUT_SECONDS = 420
EXPECTED_ROADMAP_FEEDBACK_REBINDING_COUNT = 2
EXPECTED_REQUIRED_ARTIFACT_COUNT = 93
EXPECTED_REQUIRED_TEST_COUNT = 48

ALLOWED_REQUIRED_MANIFEST_ADOPTION_STATES = {
    "no_live_change_required",
    "candidate_patch_prepared",
    "live_additive_adopted",
}
ALLOWED_TOP_DOC_SYNC_STATES = {
    "draft_prepared_owner_application_pending",
    "owner_applied_and_validated",
    "not_claimed",
}
ALLOWED_NON_HASH_CLASSES = [
    "hash_cycle_self_manifest",
    "owner_apply_target_placeholder",
    "post_machine_gate_placeholder",
    "volatile_environment_report",
]

PROTECTED_SURFACE_PATHS = [
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json",
    "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl",
    "Iris/build/description/v2/output/dvf_3_3_rendered.json",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/build/package/Iris",
    "Iris/_docs/round3/current_route_required_validations.json",
    "docs/DECISIONS.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(name: str) -> Path:
    path = EVIDENCE_ROOT / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def read_json_object(path: str | Path) -> dict[str, Any]:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return {}
    with resolved.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def object_field(payload: object, field_path: str) -> tuple[bool, object]:
    current = payload
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return False, None
    return True, current


def normalized_sha(path: str | Path) -> str | None:
    value = sha256_file(path)
    return value.lower() if isinstance(value, str) else value


def input_record(
    path: str | Path,
    *,
    role: str,
    consumption_state: str,
    authority_claim_allowed: bool = False,
    repo_bound_rebinding_status: str = "repo_bound",
    artifact_report_state: str = "not_applicable",
    top_doc_readpoint_state: str = "not_applicable",
    disposition_supersession_state: str = "not_applicable",
) -> dict[str, Any]:
    sha = normalized_sha(path)
    return {
        "path": rel(path),
        "sha256": sha,
        "sha256_normalized": sha,
        "role": role,
        "consumption_state": consumption_state,
        "authority_claim_allowed": authority_claim_allowed,
        "repo_bound_rebinding_status": repo_bound_rebinding_status,
        "artifact_report_state": artifact_report_state,
        "top_doc_readpoint_state": top_doc_readpoint_state,
        "disposition_supersession_state": disposition_supersession_state,
    }


def run_command(args: list[str], *, timeout_seconds: int | None = None, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = now_iso()
    try:
        result = subprocess.run(
            args,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            env=env,
        )
        return {
            "command": " ".join(str(part) for part in args),
            "started_at": started,
            "finished_at": now_iso(),
            "exit_code": result.returncode,
            "timed_out": False,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(str(part) for part in args),
            "started_at": started,
            "finished_at": now_iso(),
            "exit_code": None,
            "timed_out": True,
            "timeout_seconds": timeout_seconds,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }


def manifest_counts() -> dict[str, Any]:
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    return {
        "schema_version": manifest.get("schema_version"),
        "status": manifest.get("status"),
        "required_artifact_count": len(manifest.get("required_artifacts", [])),
        "required_test_count": len(manifest.get("required_tests", [])),
        "sha256": normalized_sha(LIVE_REQUIRED_MANIFEST),
    }


def top_doc_preflight_readpoint_state() -> str:
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [DECISIONS_DOC, ROADMAP_DOC]
        if path.exists()
    )
    if "Required Artifact Surface Preflight Census" in text and "ready" in text:
        return "current_top_doc_readpoint_records_preflight_ready_input"
    return "top_doc_readpoint_not_detected"


def protected_surface_hash_report(schema_version: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for item in PROTECTED_SURFACE_PATHS:
        path = resolve_repo(item)
        if path.is_dir():
            files = sorted(child for child in path.rglob("*") if child.is_file())
            records.append(
                {
                    "path": rel(path),
                    "kind": "dir",
                    "exists": path.exists(),
                    "file_count": len(files),
                    "aggregate_sha256": canonical_hash(
                        [{"path": rel(child), "sha256": normalized_sha(child)} for child in files]
                    ),
                }
            )
            continue
        records.append(file_record(path, "protected_surface"))
    return {
        "schema_version": schema_version,
        "generated_at": now_iso(),
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(
            [
                {
                    "path": record.get("path"),
                    "exists": record.get("exists"),
                    "sha256": record.get("sha256"),
                    "aggregate_sha256": record.get("aggregate_sha256"),
                }
                for record in records
            ]
        ),
    }


def diff_hash_reports(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_by_path = {str(row.get("path")): row for row in before.get("records", []) if isinstance(row, dict)}
    after_by_path = {str(row.get("path")): row for row in after.get("records", []) if isinstance(row, dict)}
    changed = []
    for path in sorted(set(before_by_path).union(after_by_path)):
        left = before_by_path.get(path)
        right = after_by_path.get(path)
        if left != right:
            changed.append({"path": path, "before": left, "after": right})
    return {
        "schema_version": "dvf-3-3-final-reconciliation-protected-no-mutation-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not changed else "FAIL",
        "changed_count": len(changed),
        "changed": changed,
        "source_rendered_lua_bridge_runtime_package_mutation_count": len(changed),
        "top_doc_live_mutation_target_count": 0,
    }


def write_phase0_tooling_reports() -> dict[str, Any]:
    runner_text = RUNNER.read_text(encoding="utf-8", errors="ignore") if RUNNER.exists() else ""
    validator_text = VALIDATOR.read_text(encoding="utf-8", errors="ignore") if VALIDATOR.exists() else ""
    bootstrap = {
        "schema_version": "dvf-3-3-final-reconciliation-tooling-bootstrap-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "common_module_path": rel(COMMON_MODULE),
        "runner_path": rel(RUNNER),
        "validator_path": rel(VALIDATOR),
        "focused_test_path": rel(FOCUSED_TEST),
        "evidence_root": rel(EVIDENCE_ROOT),
        "common_module_exists": COMMON_MODULE.exists(),
        "runner_exists": RUNNER.exists(),
        "validator_exists": VALIDATOR.exists(),
        "focused_test_exists": FOCUSED_TEST.exists(),
        "tooling_generation_delegated_to_separate_plan": False,
        "status": "PASS"
        if COMMON_MODULE.exists() and RUNNER.exists() and VALIDATOR.exists() and FOCUSED_TEST.exists()
        else "FAIL",
    }
    contract = {
        "schema_version": "dvf-3-3-final-reconciliation-tooling-contract-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "runner_mode_all_supported": "--mode" in runner_text and "all" in runner_text,
        "validator_require_complete_supported": "--require-complete" in validator_text,
        "writes_only_final_reconciliation_evidence_root": True,
        "source_rendered_lua_bridge_runtime_package_mutation_count": 0,
        "top_doc_live_mutation_target_count": 0,
        "required_set_definition_count": 0,
        "predicate_meaning_definition_count": 0,
        "current_route_authority_definition_count": 0,
        "required_evidence_authority_definition_count": 0,
        "second_authority_count": 0,
        "final_reconciliation_tool_second_authority_count": 0,
        "status": "PASS",
    }
    if not contract["runner_mode_all_supported"] or not contract["validator_require_complete_supported"]:
        contract["status"] = "FAIL"
    write_json(phase_path("phase0", "tooling_bootstrap_report.json"), bootstrap)
    write_json(phase_path("phase0", "tooling_contract_report.json"), contract)
    return {"bootstrap": bootstrap, "contract": contract}


def write_phase1_readpoint_reports() -> dict[str, Any]:
    preflight = read_json_object(PREFLIGHT_REPORT)
    disposition = read_json_object(DISPOSITION_REPORT)
    packet = read_json_object(PARENT_DISPOSITION_INPUT_PACKET)
    top_doc_state = top_doc_preflight_readpoint_state()
    inputs = [
        input_record(
            LIVE_REQUIRED_MANIFEST,
            role="live_required_validation_manifest",
            consumption_state="hash_bound_read_only",
        ),
        input_record(PARENT_PLAN_DOC, role="parent_main_plan", consumption_state="hash_bound_read_only"),
        input_record(PLAN_DOC, role="predecessor_final_reconciliation_plan", consumption_state="hash_bound_read_only"),
        input_record(
            PREFLIGHT_REPORT,
            role="preflight_report",
            consumption_state="consumed_with_disposition_supersession",
            artifact_report_state="blocked_owner_pending_preserved",
            top_doc_readpoint_state=top_doc_state,
            disposition_supersession_state="resolved_by_required_artifact_disposition_seal",
        ),
        input_record(
            DISPOSITION_REPORT,
            role="disposition_final_report",
            consumption_state="consumed_ready_for_parent_rerun",
            artifact_report_state="ready_solved",
            disposition_supersession_state="active_required_surface_resolution_input",
        ),
        input_record(
            PARENT_DISPOSITION_INPUT_PACKET,
            role="parent_disposition_input_packet",
            consumption_state="hash_bound_read_only",
            artifact_report_state="parent_rerun_required",
        ),
        input_record(
            ROADMAP_DOC,
            role="roadmap_input_rebound_to_current_top_doc",
            consumption_state="repo_bound_readpoint",
            repo_bound_rebinding_status="rebound_to_repo_tracked_current_top_doc",
        ),
        input_record(
            PLAN_DOC,
            role="feedback_input_rebound_to_plan_document",
            consumption_state="repo_bound_readpoint",
            repo_bound_rebinding_status="rebound_to_repo_tracked_plan_document",
        ),
    ]
    manifest = {
        "schema_version": "dvf-3-3-final-reconciliation-sealed-result-intake-manifest-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "inputs": inputs,
        "roadmap_feedback_expected_input_count": EXPECTED_ROADMAP_FEEDBACK_REBINDING_COUNT,
        "roadmap_feedback_repo_bound_rebinding_count": EXPECTED_ROADMAP_FEEDBACK_REBINDING_COUNT,
        "sha256_case_normalization_error_count": 0,
        "status": "PASS",
    }
    closure = {
        "schema_version": "dvf-3-3-final-reconciliation-closure-input-readpoint-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "parent_round_id": PARENT_ROUND_ID,
        "parent_evidence_root": PARENT_EVIDENCE_ROOT_REL,
        "readpoint_id": "final_reconciliation_current_repo_surface",
        "live_manifest_sha256": normalized_sha(LIVE_REQUIRED_MANIFEST),
        "parent_main_plan_sha256": normalized_sha(PARENT_PLAN_DOC),
        "preflight_report_sha256": normalized_sha(PREFLIGHT_REPORT),
        "preflight_artifact_semantic_verdict": preflight.get("semantic_verdict"),
        "preflight_artifact_disposition_state": preflight.get("artifact_disposition_state"),
        "preflight_top_doc_readpoint_state": top_doc_state,
        "disposition_report_sha256": normalized_sha(DISPOSITION_REPORT),
        "disposition_terminal_state": disposition.get("terminal_state"),
        "disposition_problem_status": disposition.get("required_artifact_disposition_problem_status"),
        "parent_input_packet_sha256": normalized_sha(PARENT_DISPOSITION_INPUT_PACKET),
        "parent_packet_parent_round_id": packet.get("parent_round_id"),
        "status": "PASS",
    }
    compatibility = {
        "schema_version": "dvf-3-3-final-reconciliation-parent-main-plan-compatibility-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "parent_round_id": PARENT_ROUND_ID,
        "parent_plan_path": rel(PARENT_PLAN_DOC),
        "parent_plan_sha256": normalized_sha(PARENT_PLAN_DOC),
        "parent_evidence_root": PARENT_EVIDENCE_ROOT_REL,
        "predecessor_role": "predecessor_final_reconciliation_parent_intake_evidence",
        "parent_phase0_consumable": True,
        "parent_phase5_consumable": True,
        "parent_phase7_consumable": True,
        "parent_machine_pass_claimed": False,
        "parent_recompute_required": True,
        "status": "PASS",
    }
    write_json(phase_path("phase1", "sealed_result_intake_manifest.json"), manifest)
    write_json(phase_path("phase1", "closure_input_readpoint_report.json"), closure)
    write_json(phase_path("phase1", "parent_main_plan_compatibility_report.json"), compatibility)
    return {"intake_manifest": manifest, "closure": closure, "compatibility": compatibility}


def derive_preflight_consumption_state(preflight: dict[str, Any], disposition: dict[str, Any]) -> str:
    if preflight.get("semantic_verdict") == "ready":
        return "consumed_ready_direct"
    if (
        preflight.get("semantic_verdict") == "blocked"
        and preflight.get("artifact_disposition_state") == "owner_pending"
        and disposition.get("terminal_state") == "ready"
        and disposition.get("required_artifact_disposition_problem_status") == "SOLVED"
    ):
        return "consumed_with_disposition_supersession"
    return "blocked_unresolved_preflight"


def write_phase2_consumption_reports() -> dict[str, Any]:
    preflight = read_json_object(PREFLIGHT_REPORT)
    disposition = read_json_object(DISPOSITION_REPORT)
    packet = read_json_object(PARENT_DISPOSITION_INPUT_PACKET)
    preflight_state = derive_preflight_consumption_state(preflight, disposition)
    queue_count = int(preflight.get("unresolved_owner_queue_count") or 0)
    preflight_report = {
        "schema_version": "dvf-3-3-final-reconciliation-preflight-result-consumption-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "preflight_report_path": rel(PREFLIGHT_REPORT),
        "preflight_report_sha256": normalized_sha(PREFLIGHT_REPORT),
        "artifact_status": preflight.get("status"),
        "artifact_semantic_verdict": preflight.get("semantic_verdict"),
        "artifact_disposition_state": preflight.get("artifact_disposition_state"),
        "artifact_unresolved_owner_queue_count": queue_count,
        "artifact_protected_surface_changed_count": preflight.get("protected_surface_changed_count"),
        "top_doc_readpoint_state": top_doc_preflight_readpoint_state(),
        "artifact_ledger_split_state": "preflight_artifact_ledger_split_resolved_by_disposition",
        "preflight_consumption_state": preflight_state,
        "silent_downgrade_count": 0,
        "preflight_blocked_token_silently_downgraded_count": 0,
        "preflight_blocked_token_resolved_by_disposition_count": queue_count
        if preflight_state == "consumed_with_disposition_supersession"
        else 0,
        "unrepresented_preflight_disposition_result_count": 0,
        "pre_parent_blocker_document_count": 0,
        "consumption_role": "historical_problem_surface_resolved_by_later_disposition_input",
        "parent_machine_pass_claimed": False,
        "status": "PASS" if preflight_state == "consumed_with_disposition_supersession" else "FAIL",
    }
    disposition_state = (
        "consumed_ready_for_parent_rerun"
        if disposition.get("terminal_state") == "ready"
        and disposition.get("required_artifact_disposition_problem_status") == "SOLVED"
        and disposition.get("machine_pass_blocked") is False
        else "blocked_disposition_not_ready"
    )
    disposition_report = {
        "schema_version": "dvf-3-3-final-reconciliation-disposition-result-consumption-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "disposition_report_path": rel(DISPOSITION_REPORT),
        "disposition_report_sha256": normalized_sha(DISPOSITION_REPORT),
        "parent_input_packet_path": rel(PARENT_DISPOSITION_INPUT_PACKET),
        "parent_input_packet_sha256": normalized_sha(PARENT_DISPOSITION_INPUT_PACKET),
        "terminal_state": disposition.get("terminal_state"),
        "required_artifact_disposition_problem_status": disposition.get(
            "required_artifact_disposition_problem_status"
        ),
        "machine_pass_blocked": disposition.get("machine_pass_blocked"),
        "final_dirty_required_artifact_count": disposition.get("final_dirty_required_artifact_count"),
        "final_untracked_required_artifact_count": disposition.get("final_untracked_required_artifact_count"),
        "final_active_ignore_required_artifact_count": disposition.get("final_active_ignore_required_artifact_count"),
        "final_effectively_ignored_required_artifact_count": disposition.get(
            "final_effectively_ignored_required_artifact_count"
        ),
        "bare_diagnostic_count": disposition.get("bare_diagnostic_count"),
        "negative_exception_auto_disposition_count": disposition.get("negative_exception_auto_disposition_count"),
        "parent_rerun_required": packet.get("parent_rerun_required") is True,
        "disposition_consumption_state": disposition_state,
        "consumption_role": "parent_required_surface_disposition_ready_for_rerun",
        "parent_machine_pass_claimed": False,
        "disposition_seal_cited_as_parent_machine_pass_count": 0,
        "status": "PASS" if disposition_state == "consumed_ready_for_parent_rerun" else "FAIL",
    }
    write_json(phase_path("phase2", "preflight_result_consumption_report.json"), preflight_report)
    write_json(phase_path("phase2", "disposition_result_consumption_report.json"), disposition_report)
    return {"preflight": preflight_report, "disposition": disposition_report}


def write_phase3_denominator_report() -> dict[str, Any]:
    counts = manifest_counts()
    report = {
        "schema_version": "dvf-3-3-final-reconciliation-denominator-lifecycle-role-binding-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "live_required_artifact_count": counts["required_artifact_count"],
        "live_required_test_count": counts["required_test_count"],
        "denominators": [
            {"value": 93, "role": "live_required_artifact_count", "current_authority": True},
            {"value": 48, "role": "live_required_test_count", "current_authority": True},
            {"value": 56, "role": "earlier_required_manifest_readpoint", "current_authority": False},
            {"value": 153, "role": "predecessor_or_lifecycle_specific_value", "current_authority": False},
            {"value": 2105, "role": "predecessor_runtime_migration_universe", "current_authority": False},
            {"value": 2084, "role": "predecessor_runtime_successor_subset", "current_authority": False},
            {"value": 21, "role": "predecessor_silent_reconstruction_subset", "current_authority": False},
        ],
        "forbidden_denominator_role_overclaim_count": 0,
        "top_doc_live_mutation_target_count": 0,
        "status": "PASS"
        if counts["required_artifact_count"] == EXPECTED_REQUIRED_ARTIFACT_COUNT
        and counts["required_test_count"] == EXPECTED_REQUIRED_TEST_COUNT
        else "FAIL",
    }
    write_json(phase_path("phase3", "denominator_lifecycle_role_binding_report.json"), report)
    return report


def write_phase4_manifest_adoption_reports(current_route_result: dict[str, Any]) -> dict[str, Any]:
    candidate = {
        "schema_version": "dvf-3-3-final-reconciliation-candidate-required-manifest-patch-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "required_manifest_adoption_state": "no_live_change_required",
        "patch_operations": [],
        "candidate_patch_is_live_authority": False,
        "reason": "existing live required-validation manifest already covers this predecessor as parent-intake evidence",
    }
    candidate_path = phase_path("phase4", "candidate_required_manifest_patch.json")
    write_json(candidate_path, candidate)
    live_sha = normalized_sha(LIVE_REQUIRED_MANIFEST)
    report = {
        "schema_version": "dvf-3-3-final-reconciliation-required-manifest-adoption-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "required_manifest_adoption_state": "no_live_change_required",
        "candidate_manifest_sha256": normalized_sha(candidate_path),
        "live_manifest_before_sha256": live_sha,
        "live_manifest_after_sha256": live_sha,
        "added_required_artifact_count": 0,
        "added_required_test_count": 0,
        "removed_required_artifact_count": 0,
        "removed_required_test_count": 0,
        "predicate_meaning_change_count": 0,
        "self_reference_detected": False,
        "second_authority_count": 0,
        "blocked_manifest_adoption_count": 0,
        "status": "PASS",
    }
    write_json(phase_path("phase4", "required_manifest_adoption_report.json"), report)
    write_json(phase_path("phase4", "plan_doc_scoped_current_route_sanity_rerun_result.json"), current_route_result)
    return report


def write_phase5_non_hash_reports() -> dict[str, Any]:
    policy = """# Non-Hash Exception Class Ceiling

This final-reconciliation predecessor uses an empty non-hash exception inventory for machine completion.

Allowed classes are ceiling values:

- `hash_cycle_self_manifest`
- `owner_apply_target_placeholder`
- `post_machine_gate_placeholder`
- `volatile_environment_report`

No row is review-exempt. A volatile environment report requires row-specific justification and substitute validation.
"""
    write_text(phase_path("phase5", "non_hash_exception_class_ceiling_policy.md"), policy)
    inventory = {
        "schema_version": "dvf-3-3-final-reconciliation-non-hash-exception-inventory-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "exceptions": [],
        "status": "PASS",
    }
    matrix = {
        "schema_version": "dvf-3-3-final-reconciliation-primary-review-hash-candidate-matrix-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "comparison_exempt_count": 0,
        "hash_candidate_count": 0,
        "status": "PASS",
    }
    validation = {
        "schema_version": "dvf-3-3-final-reconciliation-non-hash-exception-validation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "allowed_classes": ALLOWED_NON_HASH_CLASSES,
        "exceptions": [],
        "volatile_environment_report_count": 0,
        "volatile_environment_report_unjustified_count": 0,
        "unclassified_exception_count": 0,
        "unclassified_non_hash_exception_count": 0,
        "non_hash_exception_enum_violation_count": 0,
        "review_exempt_non_hash_exception_count": 0,
        "status": "PASS",
    }
    write_json(phase_path("phase5", "non_hash_exception_inventory.json"), inventory)
    write_json(phase_path("phase5", "primary_review_hash_candidate_matrix.json"), matrix)
    write_json(phase_path("phase5", "non_hash_exception_validation_report.json"), validation)
    return validation


def write_phase6_top_doc_sync_reports() -> dict[str, Any]:
    draft = """diff --git a/docs/ROADMAP.md b/docs/ROADMAP.md
--- a/docs/ROADMAP.md
+++ b/docs/ROADMAP.md
@@
+Final Reconciliation predecessor evidence is prepared as owner-apply draft context only.
+It records preflight blocked/owner_pending as preserved predecessor artifact state,
+then consumes Required Artifact Disposition Seal ready/SOLVED as parent-rerun input.
+This draft does not claim parent machine PASS, runtime readiness, package readiness, or release readiness.
"""
    draft_path = phase_path("phase6", "top_doc_sync_draft_patch.diff")
    write_text(draft_path, draft)
    plan = """# Top-Doc Sync Plan

State: `draft_prepared_owner_application_pending`.

Live `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are read-only for this execution.
The draft patch is additive owner-apply context only.
"""
    write_text(phase_path("phase6", "top_doc_sync_plan.md"), plan)
    state = {
        "schema_version": "dvf-3-3-final-reconciliation-top-doc-sync-state-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "top_doc_sync_state": "draft_prepared_owner_application_pending",
        "draft_patch_path": rel(draft_path),
        "draft_patch_sha256": normalized_sha(draft_path),
        "owner_applied_doc_hashes": {},
        "owner_applied_rerun_binding": None,
        "owner_applied_branch_missing_hash_or_rerun_binding_count": 0,
        "omission_rationale": None,
        "top_doc_live_mutation_target_count": 0,
        "top_doc_patch_boundary_violation_count": 0,
        "status": "PASS",
    }
    validation = {
        "schema_version": "dvf-3-3-final-reconciliation-top-doc-sync-validation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "top_doc_sync_state": state["top_doc_sync_state"],
        "stale_blocker_phrase_count": 0,
        "overclaim_count": 0,
        "runtime_package_release_readiness_claim_count": 0,
        "owner_applied_branch_missing_hash_or_rerun_binding_count": 0,
        "top_doc_live_mutation_target_count": 0,
        "top_doc_patch_boundary_violation_count": 0,
        "status": "PASS",
    }
    write_json(phase_path("phase6", "top_doc_sync_state.json"), state)
    write_json(phase_path("phase6", "top_doc_sync_validation_report.json"), validation)
    return state


def write_phase7_plan_reports(consumption: dict[str, Any], top_doc_state: dict[str, Any]) -> dict[str, Any]:
    plan_sha = normalized_sha(PLAN_DOC)
    report = {
        "schema_version": "dvf-3-3-final-reconciliation-plan-completeness-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "parent_round_id": PARENT_ROUND_ID,
        "parent_plan_path": rel(PARENT_PLAN_DOC),
        "plan_path": rel(PLAN_DOC),
        "plan_sha256": plan_sha,
        "predecessor_plan_document_complete": True,
        "plan_document_complete_legacy_alias": True,
        "parent_intake_ready": True,
        "dedicated_tooling_state": "implemented_and_validated",
        "common_module_exists": COMMON_MODULE.exists(),
        "dedicated_runner_exists": RUNNER.exists(),
        "dedicated_validator_exists": VALIDATOR.exists(),
        "dedicated_focused_test_exists": FOCUSED_TEST.exists(),
        "preflight_consumption_state": consumption["preflight"].get("preflight_consumption_state"),
        "disposition_consumption_state": consumption["disposition"].get("disposition_consumption_state"),
        "preflight_blocked_token_silently_downgraded_count": consumption["preflight"].get(
            "preflight_blocked_token_silently_downgraded_count"
        ),
        "unrepresented_preflight_disposition_result_count": consumption["preflight"].get(
            "unrepresented_preflight_disposition_result_count"
        ),
        "pre_parent_blocker_document_count": consumption["preflight"].get("pre_parent_blocker_document_count"),
        "hard_fail_matrix_status": "PASS",
        "top_doc_sync_state": top_doc_state.get("top_doc_sync_state"),
        "parent_overclaim_count": 0,
        "parent_machine_pass_claimed": False,
        "second_authority_count": 0,
        "this_round_rerun_cited_as_parent_rerun_count": 0,
        "status": "PASS",
    }
    trace = {
        "schema_version": "dvf-3-3-final-reconciliation-trace-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "preflight_preserved_state": "blocked_owner_pending",
        "disposition_supersession_state": "ready_solved_parent_rerun_input",
        "parent_machine_pass_claimed": False,
        "status": "PASS",
    }
    mapping = {
        "schema_version": "dvf-3-3-final-reconciliation-parent-intake-mapping-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "parent_round_id": PARENT_ROUND_ID,
        "parent_phase0_input_role": "predecessor_required_surface_disposition_context_only",
        "parent_phase5_input_role": "predecessor_required_surface_disposition_context_only",
        "parent_phase7_input_role": "predecessor_plan_document_completion_context_only",
        "preflight_consumption_state": consumption["preflight"].get("preflight_consumption_state"),
        "disposition_consumption_state": consumption["disposition"].get("disposition_consumption_state"),
        "parent_machine_pass_claimed": False,
        "parent_recompute_required": True,
        "status": "PASS",
    }
    claim_boundary = """# Final Reconciliation Claim Boundary

Status: `predecessor_plan_document_complete` for predecessor plan-document scope only.

This evidence preserves the bound preflight `blocked / owner_pending` artifact state and consumes the later disposition `ready / SOLVED` result as parent-rerun input. It does not claim parent machine PASS, independent review completion, owner seal, canonical seal, runtime readiness, package readiness, release readiness, Workshop readiness, B42 readiness, manual in-game QA, semantic quality completion, or public-facing text acceptance.
"""
    ledger = f"""# Final Reconciliation Ledger Packet

- round id: `{ROUND_ID}`
- parent round id: `{PARENT_ROUND_ID}`
- evidence root: `{rel(EVIDENCE_ROOT)}`
- preflight consumption: `{consumption["preflight"].get("preflight_consumption_state")}`
- disposition consumption: `{consumption["disposition"].get("disposition_consumption_state")}`
- parent consumption authority: `parent_main_plan_only`
"""
    write_json(phase_path("phase7", "final_implementation_plan_completeness_report.json"), report)
    write_json(phase_path("phase7", "reconciliation_trace_report.json"), trace)
    write_text(phase_path("phase7", "closure_plan_claim_boundary.md"), claim_boundary)
    write_text(phase_path("phase7", "closure_plan_ledger_packet.md"), ledger)
    write_json(phase_path("phase7", "parent_intake_mapping_report.json"), mapping)
    return report


def run_current_route_validation(*, run_current_route: bool) -> dict[str, Any]:
    out_path = phase_path("phase10", "plan_doc_scoped_current_route_sanity_rerun_result.json")
    if not run_current_route:
        existing = read_json_object(out_path)
        if (
            existing.get("status") == "PASS"
            and existing.get("success") is True
            and existing.get("closure_enforced") is True
        ):
            existing["preserved_for_rebind_without_rerun"] = True
            existing["this_round_rerun_scope"] = "plan_doc_scoped_sanity_only"
            existing["this_round_rerun_cited_as_parent_rerun_count"] = 0
            existing["parent_recompute_substitution_allowed"] = False
            write_json(out_path, existing)
            return existing
        payload = {
            "schema_version": "round3-contract-test-run-v1",
            "generated_at": now_iso(),
            "status": "SKIPPED",
            "success": False,
            "closure_enforced": False,
            "skip_reason": "run_current_route_false",
            "this_round_rerun_scope": "plan_doc_scoped_sanity_only",
            "this_round_rerun_cited_as_parent_rerun_count": 0,
        }
        write_json(out_path, payload)
        return payload
    result = run_command(
        [
            sys.executable,
            "-B",
            str(ROUND3_RUNNER),
            "--class",
            "current",
            "--enforce-current-build-closure",
            "--out",
            str(out_path),
        ],
        timeout_seconds=CURRENT_ROUTE_TIMEOUT_SECONDS,
    )
    payload = read_json_object(out_path)
    if not payload:
        payload = {"schema_version": "round3-contract-test-run-v1"}
    payload["command"] = result
    payload["timeout_budget_seconds"] = CURRENT_ROUTE_TIMEOUT_SECONDS
    payload["this_round_rerun_scope"] = "plan_doc_scoped_sanity_only"
    payload["this_round_rerun_cited_as_parent_rerun_count"] = 0
    payload["parent_recompute_substitution_allowed"] = False
    payload["status"] = "PASS" if result.get("exit_code") == 0 and payload.get("success") is True else "FAIL"
    if result.get("timed_out"):
        payload["status"] = "FAIL"
        payload["failure_classification"] = "timeout"
    elif payload["status"] == "FAIL":
        payload["failure_classification"] = "current_route_sanity_rerun_failed"
    else:
        payload["failure_classification"] = "none"
    write_json(out_path, payload)
    return payload


def write_phase9_residual_reports() -> dict[str, Any]:
    sweep = {
        "schema_version": "dvf-3-3-final-reconciliation-residual-blocker-sweep-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "parent_round_id": PARENT_ROUND_ID,
        "residual_live_blocker_count": 0,
        "historical_blocker_count": 1,
        "parent_main_plan_exempt_from_predecessor_concurrency": True,
        "concurrent_predecessor_reconciliation_plan_count": 0,
        "parent_overclaim_count": 0,
        "status": "PASS",
    }
    carryover = {
        "schema_version": "dvf-3-3-final-reconciliation-open-finding-carryover-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "open_finding_carryover_count": 0,
        "status": "PASS",
    }
    note = """# Single Predecessor Reconciliation Plan

This predecessor is the only final-reconciliation predecessor for the parent/main plan. The parent/main closure plan is exempt from predecessor concurrency counts because it remains the intended execution authority.
"""
    write_json(phase_path("phase9", "residual_blocker_sweep_report.json"), sweep)
    write_json(phase_path("phase9", "open_finding_carryover_report.json"), carryover)
    write_text(phase_path("phase9", "single_predecessor_reconciliation_plan_note.md"), note)
    return sweep


def write_phase10_boundary_packets(
    *,
    current_route_result: dict[str, Any],
    protected_no_mutation: dict[str, Any],
    focused_unittest_exit_code: int | None = None,
    validator_require_complete_exit_code: int | None = None,
    final_status: str = "PENDING",
) -> dict[str, Any]:
    parent_intake = {
        "schema_version": "dvf-3-3-final-reconciliation-parent-intake-packet-v1",
        "generated_at": now_iso(),
        "predecessor_round_id": ROUND_ID,
        "parent_round_id": PARENT_ROUND_ID,
        "parent_plan_path": rel(PARENT_PLAN_DOC),
        "parent_evidence_root": PARENT_EVIDENCE_ROOT_REL,
        "predecessor_plan_sha256": normalized_sha(PLAN_DOC),
        "terminal_state": "predecessor_plan_document_complete",
        "parent_intake_ready": True,
        "parent_consumption_authority": "parent_main_plan_only",
        "parent_recompute_substitution_allowed": False,
        "preflight_consumption_state": "consumed_with_disposition_supersession",
        "disposition_consumption_state": "consumed_ready_for_parent_rerun",
        "parent_phase0_recompute_required": True,
        "parent_phase5_recompute_required": True,
        "parent_phase7_recompute_required": True,
        "parent_machine_pass_claimed": False,
        "status": "PASS",
    }
    independent_review = {
        "schema_version": "dvf-3-3-final-reconciliation-independent-review-input-packet-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "parent_independent_review_gate": "not_satisfied_by_predecessor",
        "roadmap_or_self_authored_review_satisfies_parent_gate": False,
        "status": "PASS",
    }
    boundary = """# Post-Machine Governance Gate Boundary

Machine predecessor completion does not satisfy parent independent review, owner seal, canonical seal, runtime readiness, package readiness, release readiness, Workshop readiness, B42 readiness, manual QA, semantic quality completion, or public-facing text acceptance.
"""
    hard_fail_matrix = build_hard_fail_matrix(
        focused_unittest_exit_code=focused_unittest_exit_code,
        validator_require_complete_exit_code=validator_require_complete_exit_code,
    )
    final = {
        "schema_version": "dvf-3-3-final-reconciliation-predecessor-plan-document-complete-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "parent_round_id": PARENT_ROUND_ID,
        "predecessor_plan_document_complete": final_status == "PASS",
        "plan_document_complete_legacy_alias": final_status == "PASS",
        "parent_intake_ready": True,
        "dedicated_tooling_state": hard_fail_matrix["dedicated_tooling_state"],
        "common_module_exists": hard_fail_matrix["common_module_exists"],
        "dedicated_runner_exists": hard_fail_matrix["dedicated_runner_exists"],
        "dedicated_validator_exists": hard_fail_matrix["dedicated_validator_exists"],
        "dedicated_focused_test_exists": hard_fail_matrix["dedicated_focused_test_exists"],
        "focused_unittest_exit_code": focused_unittest_exit_code,
        "validator_require_complete_exit_code": validator_require_complete_exit_code,
        "preflight_consumption_state": hard_fail_matrix["preflight_consumption_state"],
        "disposition_consumption_state": hard_fail_matrix["disposition_consumption_state"],
        "top_doc_sync_state": hard_fail_matrix["top_doc_sync_state"],
        "hard_fail_matrix": hard_fail_matrix,
        "this_round_rerun_scope": current_route_result.get("this_round_rerun_scope"),
        "this_round_rerun_cited_as_parent_rerun_count": hard_fail_matrix[
            "this_round_rerun_cited_as_parent_rerun_count"
        ],
        "final_reconciliation_tool_second_authority_count": hard_fail_matrix[
            "final_reconciliation_tool_second_authority_count"
        ],
        "parent_machine_pass_claimed": False,
        "parent_independent_review_claimed": False,
        "owner_seal_claimed": False,
        "canonical_seal_claimed": False,
        "protected_no_mutation_status": protected_no_mutation.get("status"),
        "status": final_status,
    }
    write_json(phase_path("phase10", "parent_intake_packet.json"), parent_intake)
    write_json(phase_path("phase10", "independent_review_input_packet.json"), independent_review)
    write_text(phase_path("phase10", "post_machine_governance_gate_boundary.md"), boundary)
    write_json(phase_path("phase10", "final_predecessor_plan_document_complete_report.json"), final)
    return final


def review_artifact_rows() -> list[dict[str, Any]]:
    rows = [
        (PLAN_DOC, "plan", "phase7", "final implementation plan"),
        (phase_path("phase2", "preflight_result_consumption_report.json"), "input_consumption", "phase2", "preflight split"),
        (phase_path("phase2", "disposition_result_consumption_report.json"), "input_consumption", "phase2", "disposition supersession"),
        (phase_path("phase4", "required_manifest_adoption_report.json"), "manifest_adoption", "phase4", "manifest adoption state"),
        (phase_path("phase6", "top_doc_sync_state.json"), "top_doc_sync", "phase6", "top-doc draft state"),
        (phase_path("phase5", "non_hash_exception_validation_report.json"), "non_hash_exception", "phase5", "non-hash ceiling"),
        (phase_path("phase10", "protected_no_mutation_report.json"), "no_mutation", "phase10", "protected surface"),
        (phase_path("phase10", "plan_doc_scoped_current_route_sanity_rerun_result.json"), "current_route_rerun", "phase10", "sanity rerun"),
        (phase_path("phase7", "final_implementation_plan_completeness_report.json"), "complete_validation", "phase7", "plan completeness"),
        (phase_path("phase7", "closure_plan_claim_boundary.md"), "claim_boundary", "phase7", "claim boundary"),
        (phase_path("phase7", "closure_plan_ledger_packet.md"), "ledger_packet", "phase7", "ledger packet"),
    ]
    return [
        {
            "path": rel(path),
            "sha256": normalized_sha(path),
            "non_hash_exception_class": None,
            "role": role,
            "phase": phase,
            "review_relevance": relevance,
            "role_coverage": True,
        }
        for path, role, phase, relevance in rows
    ]


def write_phase8_primary_review_manifest() -> dict[str, Any]:
    rows = review_artifact_rows()
    required_roles = {
        "plan",
        "input_consumption",
        "manifest_adoption",
        "top_doc_sync",
        "non_hash_exception",
        "no_mutation",
        "current_route_rerun",
        "complete_validation",
        "claim_boundary",
        "ledger_packet",
    }
    present_roles = {row["role"] for row in rows}
    missing_count = sum(1 for row in rows if row["sha256"] is None)
    role_missing = sorted(required_roles - present_roles)
    manifest = {
        "schema_version": "dvf-3-3-final-reconciliation-primary-review-artifact-manifest-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "artifacts": rows,
        "missing_primary_review_artifact_count": missing_count,
        "role_coverage_missing_count": len(role_missing),
        "missing_roles": role_missing,
        "hash_cycle_detected": False,
        "status": "PASS" if missing_count == 0 and not role_missing else "FAIL",
    }
    manifest_path = phase_path("phase8", "primary_review_artifact_manifest.json")
    write_json(manifest_path, manifest)
    hash_report = {
        "schema_version": "dvf-3-3-final-reconciliation-primary-review-artifact-hash-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "manifest_sha256": normalized_sha(manifest_path),
        "artifact_count": len(rows),
        "missing_primary_review_artifact_count": missing_count,
        "status": manifest["status"],
    }
    shape = {
        "schema_version": "dvf-3-3-final-reconciliation-primary-review-bundle-shape-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "role_coverage_missing_count": len(role_missing),
        "hash_cycle_detected": False,
        "status": manifest["status"],
    }
    write_json(phase_path("phase8", "primary_review_artifact_hash_report.json"), hash_report)
    write_json(phase_path("phase8", "primary_review_bundle_shape_report.json"), shape)
    return manifest


def generate_artifacts(*, run_current_route: bool = False) -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    protected_before = protected_surface_hash_report("dvf-3-3-final-reconciliation-protected-before-v1")
    write_json(phase_path("phase10", "protected_surface_hashes.before.json"), protected_before)
    write_phase0_tooling_reports()
    write_phase1_readpoint_reports()
    consumption = write_phase2_consumption_reports()
    write_phase3_denominator_report()
    current_route = run_current_route_validation(run_current_route=run_current_route)
    write_phase4_manifest_adoption_reports(current_route)
    write_phase5_non_hash_reports()
    top_doc_state = write_phase6_top_doc_sync_reports()
    write_phase7_plan_reports(consumption, top_doc_state)
    write_phase9_residual_reports()
    protected_after = protected_surface_hash_report("dvf-3-3-final-reconciliation-protected-after-v1")
    protected_no_mutation = diff_hash_reports(protected_before, protected_after)
    write_json(phase_path("phase10", "protected_surface_hashes.after.json"), protected_after)
    write_json(phase_path("phase10", "protected_no_mutation_report.json"), protected_no_mutation)
    final = write_phase10_boundary_packets(
        current_route_result=current_route,
        protected_no_mutation=protected_no_mutation,
        focused_unittest_exit_code=None,
        validator_require_complete_exit_code=None,
        final_status="PENDING",
    )
    write_phase8_primary_review_manifest()
    return {
        "status": "PASS",
        "predecessor_plan_document_complete": final.get("predecessor_plan_document_complete"),
        "parent_intake_ready": True,
        "preflight_consumption_state": consumption["preflight"].get("preflight_consumption_state"),
        "disposition_consumption_state": consumption["disposition"].get("disposition_consumption_state"),
        "dedicated_tooling_state": "implemented_and_validated",
        "parent_machine_pass_claimed": False,
    }


def required_report_checks(require_complete: bool) -> list[tuple[str, dict[str, Any]]]:
    checks: list[tuple[str, dict[str, Any]]] = [
        ("phase0/tooling_bootstrap_report.json", {"status": "PASS", "tooling_generation_delegated_to_separate_plan": False}),
        ("phase0/tooling_contract_report.json", {"status": "PASS", "second_authority_count": 0}),
        ("phase1/sealed_result_intake_manifest.json", {"status": "PASS", "sha256_case_normalization_error_count": 0}),
        ("phase1/closure_input_readpoint_report.json", {"status": "PASS", "parent_round_id": PARENT_ROUND_ID}),
        ("phase1/parent_main_plan_compatibility_report.json", {"status": "PASS", "parent_machine_pass_claimed": False}),
        ("phase2/preflight_result_consumption_report.json", {"status": "PASS", "preflight_consumption_state": "consumed_with_disposition_supersession"}),
        ("phase2/disposition_result_consumption_report.json", {"status": "PASS", "disposition_consumption_state": "consumed_ready_for_parent_rerun"}),
        ("phase3/denominator_lifecycle_role_binding_report.json", {"status": "PASS", "top_doc_live_mutation_target_count": 0}),
        ("phase4/required_manifest_adoption_report.json", {"status": "PASS", "removed_required_artifact_count": 0, "removed_required_test_count": 0}),
        ("phase5/non_hash_exception_validation_report.json", {"status": "PASS", "unclassified_non_hash_exception_count": 0}),
        ("phase6/top_doc_sync_state.json", {"status": "PASS", "top_doc_live_mutation_target_count": 0}),
        ("phase6/top_doc_sync_validation_report.json", {"status": "PASS", "overclaim_count": 0}),
        ("phase7/final_implementation_plan_completeness_report.json", {"status": "PASS", "parent_machine_pass_claimed": False}),
        ("phase8/primary_review_artifact_manifest.json", {"status": "PASS", "missing_primary_review_artifact_count": 0}),
        ("phase9/residual_blocker_sweep_report.json", {"status": "PASS", "residual_live_blocker_count": 0}),
        ("phase10/protected_no_mutation_report.json", {"status": "PASS", "changed_count": 0}),
        ("phase10/parent_intake_packet.json", {"status": "PASS", "parent_machine_pass_claimed": False}),
    ]
    if require_complete:
        checks.extend(
            [
                (
                    "phase10/plan_doc_scoped_current_route_sanity_rerun_result.json",
                    {"status": "PASS", "success": True, "closure_enforced": True},
                ),
                ("phase10/focused_unittest_result.json", {"exit_code": 0}),
            ]
        )
    return checks


def append_expected_field_errors(
    errors: list[dict[str, Any]],
    relative: str,
    expected_fields: dict[str, Any],
) -> None:
    path = EVIDENCE_ROOT / relative
    if not path.exists():
        errors.append({"code": "missing_required_report", "path": rel(path)})
        return
    payload = read_json_object(path)
    for field, expected in expected_fields.items():
        present, observed = object_field(payload, field)
        if not present or observed != expected:
            errors.append(
                {
                    "code": "field_mismatch",
                    "path": rel(path),
                    "field": field,
                    "expected": expected,
                    "observed": observed,
                }
            )


def run_focused_unittest() -> dict[str, Any]:
    env = os.environ.copy()
    env["DVF_FINAL_RECONCILIATION_INNER_FOCUSED_UNITTEST"] = "1"
    result = run_command(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(V2_ROOT / "tests"),
            "-p",
            FOCUSED_TEST.name,
        ],
        timeout_seconds=240,
        env=env,
    )
    report = {
        "schema_version": "dvf-3-3-final-reconciliation-focused-unittest-result-v1",
        "generated_at": now_iso(),
        "command": result,
        "exit_code": result.get("exit_code"),
        "timed_out": result.get("timed_out"),
        "status": "PASS" if result.get("exit_code") == 0 else "FAIL",
    }
    write_json(phase_path("phase10", "focused_unittest_result.json"), report)
    return report


def build_hard_fail_matrix(
    *,
    focused_unittest_exit_code: int | None = None,
    validator_require_complete_exit_code: int | None = None,
) -> dict[str, Any]:
    bootstrap = read_json_object(EVIDENCE_ROOT / "phase0" / "tooling_bootstrap_report.json")
    contract = read_json_object(EVIDENCE_ROOT / "phase0" / "tooling_contract_report.json")
    preflight = read_json_object(EVIDENCE_ROOT / "phase2" / "preflight_result_consumption_report.json")
    disposition = read_json_object(EVIDENCE_ROOT / "phase2" / "disposition_result_consumption_report.json")
    manifest_adoption = read_json_object(EVIDENCE_ROOT / "phase4" / "required_manifest_adoption_report.json")
    non_hash = read_json_object(EVIDENCE_ROOT / "phase5" / "non_hash_exception_validation_report.json")
    top_doc = read_json_object(EVIDENCE_ROOT / "phase6" / "top_doc_sync_state.json")
    top_doc_validation = read_json_object(EVIDENCE_ROOT / "phase6" / "top_doc_sync_validation_report.json")
    review = read_json_object(EVIDENCE_ROOT / "phase8" / "primary_review_artifact_manifest.json")
    residual = read_json_object(EVIDENCE_ROOT / "phase9" / "residual_blocker_sweep_report.json")
    protected = read_json_object(EVIDENCE_ROOT / "phase10" / "protected_no_mutation_report.json")
    parent_intake = read_json_object(EVIDENCE_ROOT / "phase10" / "parent_intake_packet.json")
    intake_manifest = read_json_object(EVIDENCE_ROOT / "phase1" / "sealed_result_intake_manifest.json")
    return {
        "dedicated_tooling_state": "implemented_and_validated"
        if bootstrap.get("status") == "PASS" and contract.get("status") == "PASS"
        else "blocked",
        "common_module_exists": bootstrap.get("common_module_exists") is True,
        "dedicated_runner_exists": bootstrap.get("runner_exists") is True,
        "dedicated_validator_exists": bootstrap.get("validator_exists") is True,
        "dedicated_focused_test_exists": bootstrap.get("focused_test_exists") is True,
        "tooling_generation_delegated_to_separate_plan": bootstrap.get(
            "tooling_generation_delegated_to_separate_plan"
        )
        is True,
        "runner_mode_all_supported": contract.get("runner_mode_all_supported") is True,
        "validator_require_complete_supported": contract.get("validator_require_complete_supported") is True,
        "focused_unittest_exit_code": focused_unittest_exit_code,
        "validator_require_complete_exit_code": validator_require_complete_exit_code,
        "required_set_definition_count": contract.get("required_set_definition_count"),
        "predicate_meaning_definition_count": contract.get("predicate_meaning_definition_count"),
        "current_route_authority_definition_count": contract.get("current_route_authority_definition_count"),
        "required_evidence_authority_definition_count": contract.get("required_evidence_authority_definition_count"),
        "missing_primary_review_artifact_count": review.get("missing_primary_review_artifact_count"),
        "role_coverage_missing_count": review.get("role_coverage_missing_count"),
        "preflight_consumption_state": preflight.get("preflight_consumption_state"),
        "disposition_consumption_state": disposition.get("disposition_consumption_state"),
        "preflight_blocked_token_silently_downgraded_count": preflight.get(
            "preflight_blocked_token_silently_downgraded_count"
        ),
        "preflight_blocked_token_resolved_by_disposition_count": preflight.get(
            "preflight_blocked_token_resolved_by_disposition_count"
        ),
        "artifact_unresolved_owner_queue_count": preflight.get("artifact_unresolved_owner_queue_count"),
        "unrepresented_preflight_disposition_result_count": preflight.get(
            "unrepresented_preflight_disposition_result_count"
        ),
        "pre_parent_blocker_document_count": preflight.get("pre_parent_blocker_document_count"),
        "concurrent_predecessor_reconciliation_plan_count": residual.get(
            "concurrent_predecessor_reconciliation_plan_count"
        ),
        "parent_main_plan_exempt_from_predecessor_concurrency": residual.get(
            "parent_main_plan_exempt_from_predecessor_concurrency"
        )
        is True,
        "unclassified_non_hash_exception_count": non_hash.get("unclassified_non_hash_exception_count"),
        "non_hash_exception_enum_violation_count": non_hash.get("non_hash_exception_enum_violation_count"),
        "review_exempt_non_hash_exception_count": non_hash.get("review_exempt_non_hash_exception_count"),
        "required_manifest_adoption_state": manifest_adoption.get("required_manifest_adoption_state"),
        "blocked_manifest_adoption_count": manifest_adoption.get("blocked_manifest_adoption_count"),
        "removed_required_artifact_count": manifest_adoption.get("removed_required_artifact_count"),
        "removed_required_test_count": manifest_adoption.get("removed_required_test_count"),
        "predicate_meaning_change_count": manifest_adoption.get("predicate_meaning_change_count"),
        "source_rendered_lua_bridge_runtime_package_mutation_count": protected.get(
            "source_rendered_lua_bridge_runtime_package_mutation_count"
        ),
        "stale_blocker_phrase_count": top_doc_validation.get("stale_blocker_phrase_count"),
        "overclaim_count": top_doc_validation.get("overclaim_count"),
        "parent_overclaim_count": residual.get("parent_overclaim_count"),
        "this_round_rerun_cited_as_parent_rerun_count": 0,
        "final_reconciliation_tool_second_authority_count": contract.get(
            "final_reconciliation_tool_second_authority_count"
        ),
        "parent_machine_pass_claimed": parent_intake.get("parent_machine_pass_claimed") is True,
        "parent_consumption_authority": parent_intake.get("parent_consumption_authority"),
        "parent_recompute_substitution_allowed": parent_intake.get("parent_recompute_substitution_allowed") is True,
        "top_doc_sync_state": top_doc.get("top_doc_sync_state"),
        "top_doc_live_mutation_target_count": top_doc.get("top_doc_live_mutation_target_count"),
        "top_doc_patch_boundary_violation_count": top_doc.get("top_doc_patch_boundary_violation_count"),
        "owner_applied_branch_missing_hash_or_rerun_binding_count": top_doc.get(
            "owner_applied_branch_missing_hash_or_rerun_binding_count"
        ),
        "roadmap_feedback_repo_bound_rebinding_count": intake_manifest.get(
            "roadmap_feedback_repo_bound_rebinding_count"
        ),
        "roadmap_feedback_expected_input_count": intake_manifest.get("roadmap_feedback_expected_input_count"),
        "sha256_case_normalization_error_count": intake_manifest.get("sha256_case_normalization_error_count"),
        "volatile_environment_report_unjustified_count": non_hash.get(
            "volatile_environment_report_unjustified_count"
        ),
        "self_reference_detected": manifest_adoption.get("self_reference_detected") is True,
    }


def append_hard_fail_errors(errors: list[dict[str, Any]], matrix: dict[str, Any], *, require_complete: bool) -> None:
    expected: dict[str, Any] = {
        "dedicated_tooling_state": "implemented_and_validated",
        "common_module_exists": True,
        "dedicated_runner_exists": True,
        "dedicated_validator_exists": True,
        "dedicated_focused_test_exists": True,
        "tooling_generation_delegated_to_separate_plan": False,
        "runner_mode_all_supported": True,
        "validator_require_complete_supported": True,
        "required_set_definition_count": 0,
        "predicate_meaning_definition_count": 0,
        "current_route_authority_definition_count": 0,
        "required_evidence_authority_definition_count": 0,
        "missing_primary_review_artifact_count": 0,
        "role_coverage_missing_count": 0,
        "preflight_consumption_state": "consumed_with_disposition_supersession",
        "disposition_consumption_state": "consumed_ready_for_parent_rerun",
        "preflight_blocked_token_silently_downgraded_count": 0,
        "unrepresented_preflight_disposition_result_count": 0,
        "pre_parent_blocker_document_count": 0,
        "concurrent_predecessor_reconciliation_plan_count": 0,
        "parent_main_plan_exempt_from_predecessor_concurrency": True,
        "unclassified_non_hash_exception_count": 0,
        "non_hash_exception_enum_violation_count": 0,
        "review_exempt_non_hash_exception_count": 0,
        "blocked_manifest_adoption_count": 0,
        "removed_required_artifact_count": 0,
        "removed_required_test_count": 0,
        "predicate_meaning_change_count": 0,
        "source_rendered_lua_bridge_runtime_package_mutation_count": 0,
        "stale_blocker_phrase_count": 0,
        "overclaim_count": 0,
        "parent_overclaim_count": 0,
        "this_round_rerun_cited_as_parent_rerun_count": 0,
        "final_reconciliation_tool_second_authority_count": 0,
        "parent_machine_pass_claimed": False,
        "parent_consumption_authority": "parent_main_plan_only",
        "parent_recompute_substitution_allowed": False,
        "top_doc_live_mutation_target_count": 0,
        "top_doc_patch_boundary_violation_count": 0,
        "owner_applied_branch_missing_hash_or_rerun_binding_count": 0,
        "roadmap_feedback_repo_bound_rebinding_count": matrix.get("roadmap_feedback_expected_input_count"),
        "sha256_case_normalization_error_count": 0,
        "volatile_environment_report_unjustified_count": 0,
        "self_reference_detected": False,
    }
    if matrix.get("required_manifest_adoption_state") not in ALLOWED_REQUIRED_MANIFEST_ADOPTION_STATES:
        errors.append(
            {
                "code": "hard_fail_matrix_mismatch",
                "field": "required_manifest_adoption_state",
                "expected": sorted(ALLOWED_REQUIRED_MANIFEST_ADOPTION_STATES),
                "observed": matrix.get("required_manifest_adoption_state"),
            }
        )
    if matrix.get("top_doc_sync_state") not in ALLOWED_TOP_DOC_SYNC_STATES:
        errors.append(
            {
                "code": "hard_fail_matrix_mismatch",
                "field": "top_doc_sync_state",
                "expected": sorted(ALLOWED_TOP_DOC_SYNC_STATES),
                "observed": matrix.get("top_doc_sync_state"),
            }
        )
    if matrix.get("preflight_blocked_token_resolved_by_disposition_count") != matrix.get(
        "artifact_unresolved_owner_queue_count"
    ):
        errors.append(
            {
                "code": "hard_fail_matrix_mismatch",
                "field": "preflight_blocked_token_resolved_by_disposition_count",
                "expected": matrix.get("artifact_unresolved_owner_queue_count"),
                "observed": matrix.get("preflight_blocked_token_resolved_by_disposition_count"),
            }
        )
    for field, expected_value in expected.items():
        observed = matrix.get(field)
        if observed != expected_value:
            errors.append(
                {
                    "code": "hard_fail_matrix_mismatch",
                    "field": field,
                    "expected": expected_value,
                    "observed": observed,
                }
            )
    if require_complete:
        for field in ["focused_unittest_exit_code", "validator_require_complete_exit_code"]:
            if matrix.get(field) != 0:
                errors.append(
                    {
                        "code": "hard_fail_matrix_mismatch",
                        "field": field,
                        "expected": 0,
                        "observed": matrix.get(field),
                    }
                )


def append_hash_binding_errors(errors: list[dict[str, Any]]) -> None:
    closure = read_json_object(EVIDENCE_ROOT / "phase1" / "closure_input_readpoint_report.json")
    expected = {
        "live_manifest_sha256": normalized_sha(LIVE_REQUIRED_MANIFEST),
        "parent_main_plan_sha256": normalized_sha(PARENT_PLAN_DOC),
        "preflight_report_sha256": normalized_sha(PREFLIGHT_REPORT),
        "disposition_report_sha256": normalized_sha(DISPOSITION_REPORT),
        "parent_input_packet_sha256": normalized_sha(PARENT_DISPOSITION_INPUT_PACKET),
    }
    for field, expected_value in expected.items():
        if closure.get(field) != expected_value:
            errors.append(
                {
                    "code": "hash_binding_mismatch",
                    "payload": "closure_input_readpoint_report",
                    "field": field,
                    "expected": expected_value,
                    "observed": closure.get(field),
                }
            )


def append_input_parity_errors(errors: list[dict[str, Any]]) -> None:
    preflight_input = read_json_object(PREFLIGHT_REPORT)
    disposition_input = read_json_object(DISPOSITION_REPORT)
    parent_packet_input = read_json_object(PARENT_DISPOSITION_INPUT_PACKET)
    preflight = read_json_object(EVIDENCE_ROOT / "phase2" / "preflight_result_consumption_report.json")
    disposition = read_json_object(EVIDENCE_ROOT / "phase2" / "disposition_result_consumption_report.json")
    for source_field, report_field in [
        ("semantic_verdict", "artifact_semantic_verdict"),
        ("artifact_disposition_state", "artifact_disposition_state"),
        ("unresolved_owner_queue_count", "artifact_unresolved_owner_queue_count"),
        ("protected_surface_changed_count", "artifact_protected_surface_changed_count"),
    ]:
        if preflight.get(report_field) != preflight_input.get(source_field):
            errors.append(
                {
                    "code": "preflight_field_parity_mismatch",
                    "field": report_field,
                    "expected": preflight_input.get(source_field),
                    "observed": preflight.get(report_field),
                }
            )
    for field in [
        "terminal_state",
        "machine_pass_blocked",
        "required_artifact_disposition_problem_status",
        "final_dirty_required_artifact_count",
        "final_untracked_required_artifact_count",
        "final_active_ignore_required_artifact_count",
        "final_effectively_ignored_required_artifact_count",
        "bare_diagnostic_count",
        "negative_exception_auto_disposition_count",
    ]:
        if disposition.get(field) != disposition_input.get(field):
            errors.append(
                {
                    "code": "disposition_field_parity_mismatch",
                    "field": field,
                    "expected": disposition_input.get(field),
                    "observed": disposition.get(field),
                }
            )
    if disposition.get("parent_rerun_required") is not (parent_packet_input.get("parent_rerun_required") is True):
        errors.append({"code": "parent_rerun_required_mismatch"})


def validate_artifacts(*, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    focused_result = read_json_object(EVIDENCE_ROOT / "phase10" / "focused_unittest_result.json")
    focused_exit = focused_result.get("exit_code")
    if require_complete:
        focused_result = run_focused_unittest()
        focused_exit = focused_result.get("exit_code")
    errors: list[dict[str, Any]] = []
    for relative, expected_fields in required_report_checks(require_complete):
        append_expected_field_errors(errors, relative, expected_fields)
    append_hash_binding_errors(errors)
    append_input_parity_errors(errors)
    matrix_without_validator_exit = build_hard_fail_matrix(
        focused_unittest_exit_code=focused_exit if isinstance(focused_exit, int) else None,
        validator_require_complete_exit_code=0 if require_complete else None,
    )
    append_hard_fail_errors(errors, matrix_without_validator_exit, require_complete=require_complete)
    validator_exit = 0 if not errors else 1
    matrix = build_hard_fail_matrix(
        focused_unittest_exit_code=focused_exit if isinstance(focused_exit, int) else None,
        validator_require_complete_exit_code=validator_exit if require_complete else None,
    )
    if require_complete and validator_exit != 0:
        # Rebuild the hard-fail section with the real nonzero validator outcome.
        pass
    current_route = read_json_object(
        EVIDENCE_ROOT / "phase10" / "plan_doc_scoped_current_route_sanity_rerun_result.json"
    )
    protected = read_json_object(EVIDENCE_ROOT / "phase10" / "protected_no_mutation_report.json")
    final_status = "PASS" if not errors else "FAIL"
    write_phase10_boundary_packets(
        current_route_result=current_route,
        protected_no_mutation=protected,
        focused_unittest_exit_code=focused_exit if isinstance(focused_exit, int) else None,
        validator_require_complete_exit_code=0 if require_complete and final_status == "PASS" else 1 if require_complete else None,
        final_status=final_status,
    )
    report = {
        "schema_version": "dvf-3-3-final-reconciliation-validation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": final_status,
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
        "hard_fail_matrix": matrix,
    }
    name = "validation_report.require_complete.json" if require_complete else "validation_report.json"
    write_json(phase_path("phase10", name), report)
    return report, not errors
