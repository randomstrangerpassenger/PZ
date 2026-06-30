from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import os
import sys
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    canonical_hash,
    file_record,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)
from dvf_3_3_required_artifact_surface_preflight_census_common import (
    CURRENT_ROUTE_TIMEOUT_SECONDS,
    LIVE_REQUIRED_MANIFEST,
    ROUND3_RUNNER,
    command_lines,
    diff_hash_reports,
    git,
    git_environment_report,
    load_live_manifest,
    manifest_artifact_rows,
    normalize_path,
    object_field,
    protected_surface_hash_report,
    run_command,
    summarize_vcs,
    vcs_state,
    now_iso,
)


ROUND_ID = "dvf_3_3_required_artifact_disposition_seal"
PARENT_ROUND_ID = "dvf_3_3_current_route_authority_required_evidence_integrity_closure"


def configured_repo_path(env_name: str, default: Path) -> Path:
    override = os.environ.get(env_name)
    return resolve_repo(override) if override else default


EVIDENCE_ROOT = configured_repo_path(
    "DVF_REQUIRED_ARTIFACT_DISPOSITION_EVIDENCE_ROOT",
    V2_ROOT / "staging" / ROUND_ID,
)
OWNER_INPUT_ROOT = V2_ROOT / "owner_inputs" / ROUND_ID
OWNER_DECISION_DIR = OWNER_INPUT_ROOT / "owner_decision_records"
OWNER_RULE_DIR = OWNER_INPUT_ROOT / "owner_rule_ratifications"

DOC_ROOT = configured_repo_path("DVF_REQUIRED_ARTIFACT_DISPOSITION_DOC_ROOT", REPO_ROOT / "docs")
PLAN_DOC = REPO_ROOT / "docs" / "dvf_3_3_required_artifact_disposition_seal_plan.md"
POLICY_DOC = DOC_ROOT / "dvf_3_3_required_artifact_disposition_seal_policy.md"
CLAIM_BOUNDARY_DOC = DOC_ROOT / "dvf_3_3_required_artifact_disposition_seal_claim_boundary.md"
LEDGER_PACKET_DOC = DOC_ROOT / "dvf_3_3_required_artifact_disposition_seal_ledger_packet.md"
CLOSEOUT_DOC = DOC_ROOT / "dvf_3_3_required_artifact_disposition_seal_closeout.md"
PARENT_PLAN_DOC = REPO_ROOT / "docs" / "dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md"

EXPECTED_REQUIRED_ARTIFACT_COUNT = 93
EXPECTED_REQUIRED_TEST_COUNT = 48
PLANNING_DIRTY_PREMISE = 6
PLANNING_IGNORED_PREMISE = 19

ALLOWED_AXIS = ["dirty", "ignored", "untracked"]
ALLOWED_AXIS_DISPOSITION = [
    "owner_adopted_evidence_update",
    "stale_local_mutation",
    "regeneration_required",
    "track_narrowly",
    "preservation_exception_requested",
    "manifest_removal_candidate",
    "diagnostic_only_preserved_by_tracking",
    "not_preservation_relevant_with_rationale",
    "not_required_candidate",
    "blocker",
]
ALLOWED_PRESERVATION_RESULT = [
    "tracked_original_preservation",
    "tracked_hash_surrogate",
    "explicit_non_hash_exception",
    "none",
]
ALLOWED_PASSABILITY = ["passable", "owner_pending", "blocked", "validation_failed"]
ALLOWED_PROBLEM_STATUS = ["SOLVED", "SOLVED_WITH_MACHINE_BLOCKERS", "OWNER_PENDING", "VALIDATION_FAILED"]
ALLOWED_TERMINAL_STATE = ["ready", "complete_with_blockers", "machine_pass_blocked", "owner_pending", "validation_failed"]
ALLOWED_FAST_PATH_STATUS = ["ELIGIBLE", "NOT_ELIGIBLE", "NOT_USED"]
ALLOWED_AUTO_SEAL_STATUS = ["ratified", "owner-ratification-pending", "not_applicable", "invalid"]

AUTO_SEAL_RULE_ID = "tracked_negative_exception_preserved_by_tracking"
AUTO_SEAL_PREDICATE_VERSION = "tracked-negative-exception-v1"
AUTO_SEAL_DECISION_TOKEN = "ratify_tracked_negative_exception_auto_seal"

NON_CLAIMS = [
    "no_source_mutation",
    "no_source_restoration",
    "no_rendered_regeneration",
    "no_lua_bridge_export",
    "no_lua_bridge_export_mutation",
    "no_runtime_chunk_replacement",
    "no_package_payload_mutation",
    "no_package_probe",
    "no_package_readiness",
    "no_release_readiness",
    "no_workshop_readiness",
    "no_b42_readiness",
    "no_deployment_readiness",
    "no_manual_in_game_qa",
    "no_semantic_quality_completion",
    "no_public_facing_text_acceptance",
    "no_independent_review_pass",
    "no_owner_seal",
    "no_canonical_seal",
]


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


def read_jsonl_objects(path: str | Path) -> list[dict[str, Any]]:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return []
    rows: list[dict[str, Any]] = []
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                payload = json.loads(line)
                if isinstance(payload, dict):
                    rows.append(payload)
    return rows


def disposition_schema_payload() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-required-artifact-disposition-schema-v1",
        "round_id": ROUND_ID,
        "axis": ALLOWED_AXIS,
        "axis_disposition": ALLOWED_AXIS_DISPOSITION,
        "preservation_result": ALLOWED_PRESERVATION_RESULT,
        "passability": ALLOWED_PASSABILITY,
        "required_artifact_disposition_problem_status": ALLOWED_PROBLEM_STATUS,
        "terminal_state": ALLOWED_TERMINAL_STATE,
        "current_readpoint_fast_path_status": ALLOWED_FAST_PATH_STATUS,
        "auto_seal_rule_ratification_status": ALLOWED_AUTO_SEAL_STATUS,
        "field_separation_required": ["axis", "axis_disposition", "preservation_result", "passability"],
        "preservation_results_are_not_axis_dispositions": True,
        "owner_reserved_auto_seal_rule": {
            "rule_id": AUTO_SEAL_RULE_ID,
            "predicate_version": AUTO_SEAL_PREDICATE_VERSION,
            "decision_token": AUTO_SEAL_DECISION_TOKEN,
            "record_root": rel(OWNER_RULE_DIR),
            "required_fields": [
                "rule_id",
                "predicate_version",
                "schema_sha256",
                "owner_identity",
                "owner_role",
                "decision_token",
                "record_source",
            ],
            "timestamp_or_sequence_required": True,
        },
    }


def write_schema() -> tuple[dict[str, Any], str]:
    schema = disposition_schema_payload()
    write_json(phase_path("phase1_policy_schema", "disposition_schema.json"), schema)
    schema_hash = sha256_file(phase_path("phase1_policy_schema", "disposition_schema.json")) or ""
    return schema, schema_hash


def path_is_under(path: str | Path, root: str | Path) -> bool:
    resolved = resolve_repo(path)
    root_resolved = resolve_repo(root)
    return resolved == root_resolved or root_resolved in resolved.parents


def load_owner_record_files(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        payload = read_json_object(path)
        records.append(
            {
                "path": rel(path),
                "sha256": sha256_file(path),
                "payload": payload,
                "parse_ok": bool(payload),
            }
        )
    return records


def validate_owner_rule_ratifications(schema_hash: str) -> dict[str, Any]:
    records = load_owner_record_files(OWNER_RULE_DIR)
    valid_records: list[dict[str, Any]] = []
    invalid_records: list[dict[str, Any]] = []
    for record in records:
        payload = record["payload"]
        errors: list[str] = []
        if not record["parse_ok"]:
            errors.append("invalid_json")
        expected = {
            "rule_id": AUTO_SEAL_RULE_ID,
            "predicate_version": AUTO_SEAL_PREDICATE_VERSION,
            "schema_sha256": schema_hash,
            "decision_token": AUTO_SEAL_DECISION_TOKEN,
            "record_source": "owner_supplied",
        }
        for field, value in expected.items():
            if payload.get(field) != value:
                errors.append(f"{field}_mismatch")
        for field in ["owner_identity", "owner_role"]:
            if not payload.get(field):
                errors.append(f"{field}_missing")
        if not (payload.get("timestamp") or payload.get("sequence_id")):
            errors.append("timestamp_or_sequence_id_missing")
        if payload.get("executor_generated") is True or path_is_under(record["path"], EVIDENCE_ROOT):
            errors.append("executor_generated_or_staging_record")
        next_record = {
            "path": record["path"],
            "sha256": record["sha256"],
            "owner_identity": payload.get("owner_identity"),
            "owner_role": payload.get("owner_role"),
            "decision_token": payload.get("decision_token"),
            "errors": errors,
        }
        if errors:
            invalid_records.append(next_record)
        else:
            valid_records.append(next_record)
    binding_status = "PASS" if valid_records and not invalid_records else "OWNER_PENDING" if not records else "FAIL"
    return {
        "schema_version": "dvf-3-3-required-artifact-disposition-owner-rule-ratification-validation-v1",
        "generated_at": now_iso(),
        "status": "PASS" if binding_status in {"PASS", "OWNER_PENDING"} else "FAIL",
        "owner_rule_ratification_binding_status": binding_status,
        "auto_seal_rule_ratification_status": "ratified"
        if binding_status == "PASS"
        else "owner-ratification-pending"
        if binding_status == "OWNER_PENDING"
        else "invalid",
        "record_root": rel(OWNER_RULE_DIR),
        "record_root_exists": OWNER_RULE_DIR.exists(),
        "schema_sha256": schema_hash,
        "valid_record_count": len(valid_records),
        "invalid_record_count": len(invalid_records),
        "valid_records": valid_records,
        "invalid_records": invalid_records,
    }


def validate_owner_decision_records() -> dict[str, Any]:
    records = load_owner_record_files(OWNER_DECISION_DIR)
    valid_records: list[dict[str, Any]] = []
    invalid_records: list[dict[str, Any]] = []
    valid_by_path: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        payload = record["payload"]
        errors: list[str] = []
        if not record["parse_ok"]:
            errors.append("invalid_json")
        for field in ["artifact_path", "artifact_sha256", "owner_identity", "owner_role", "decision_token", "record_source"]:
            if not payload.get(field):
                errors.append(f"{field}_missing")
        if payload.get("record_source") != "owner_supplied":
            errors.append("record_source_mismatch")
        if payload.get("executor_generated") is True or path_is_under(record["path"], EVIDENCE_ROOT):
            errors.append("executor_generated_or_staging_record")
        if not (payload.get("timestamp") or payload.get("sequence_id")):
            errors.append("timestamp_or_sequence_id_missing")
        normalized_path = normalize_path(str(payload.get("artifact_path", "")))
        if normalized_path and sha256_file(normalized_path) != payload.get("artifact_sha256"):
            errors.append("artifact_sha256_mismatch")
        next_record = {
            "path": record["path"],
            "sha256": record["sha256"],
            "artifact_path": normalized_path,
            "decision_token": payload.get("decision_token"),
            "owner_identity": payload.get("owner_identity"),
            "owner_role": payload.get("owner_role"),
            "errors": errors,
        }
        if errors:
            invalid_records.append(next_record)
        else:
            valid_records.append(next_record)
            valid_by_path.setdefault(normalized_path, []).append(next_record)
    return {
        "schema_version": "dvf-3-3-required-artifact-disposition-owner-decision-validation-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not invalid_records else "FAIL",
        "owner_decision_record_binding_status": "PASS" if records and not invalid_records else "NOT_APPLICABLE" if not records else "FAIL",
        "record_root": rel(OWNER_DECISION_DIR),
        "record_root_exists": OWNER_DECISION_DIR.exists(),
        "valid_record_count": len(valid_records),
        "invalid_record_count": len(invalid_records),
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "valid_by_artifact_path": valid_by_path,
    }


def selected_owner_decision(decision_report: dict[str, Any], artifact_path: str, token: str) -> dict[str, Any] | None:
    candidates = decision_report.get("valid_by_artifact_path", {}).get(artifact_path, [])
    for record in candidates:
        if record.get("decision_token") == token:
            return record
    return None


def manifest_required_artifacts() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = load_live_manifest()
    rows, errors = manifest_artifact_rows(manifest)
    if errors:
        write_json(
            phase_path("phase0_readpoint_freeze", "manifest_path_validation_errors.json"),
            {
                "schema_version": "dvf-3-3-required-artifact-disposition-manifest-path-errors-v1",
                "generated_at": now_iso(),
                "status": "FAIL",
                "errors": errors,
            },
        )
    return manifest, rows


def artifact_vcs_rows(artifact_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in artifact_rows:
        state = vcs_state(str(row["path"]))
        state["manifest_index"] = row.get("manifest_index")
        state["manifest_checks"] = row.get("checks", [])
        state["artifact_sha256"] = sha256_file(row["path"])
        state["path_normalized"] = row["path"] == normalize_path(row["path"])
        rows.append(state)
    return rows


def disposition_vcs_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_vcs(rows)
    summary["schema_version"] = "dvf-3-3-required-artifact-disposition-vcs-summary-v1"
    summary["roadmap_premise_reconciliation"] = {
        "planning_dirty_required_artifact_count": PLANNING_DIRTY_PREMISE,
        "planning_ignored_required_artifact_count": PLANNING_IGNORED_PREMISE,
        "execution_dirty_required_artifact_count": summary.get("dirty_required_artifact_count"),
        "execution_ignore_rule_match_required_artifact_count": summary.get("ignore_rule_match_required_artifact_count"),
        "execution_effectively_ignored_required_artifact_count": summary.get("effectively_ignored_required_artifact_count"),
        "ignored_19_compared_to_ignore_rule_match_required": True,
        "effectively_ignored_reported_as_separate_blocker_axis": True,
        "readpoint_drift_recorded": summary.get("dirty_required_artifact_count") != PLANNING_DIRTY_PREMISE
        or summary.get("ignore_rule_match_required_artifact_count") != PLANNING_IGNORED_PREMISE,
    }
    return summary


def unique_by_path(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    for row in rows:
        by_path.setdefault(str(row.get("path")), row)
    return [by_path[path] for path in sorted(by_path)]


def problem_closure_rows(vcs_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return unique_by_path(
        row
        for row in vcs_rows
        if row.get("dirty") or row.get("ignore_active") or row.get("effectively_ignored") or row.get("untracked")
    )


def ignored_diagnostic_coverage_rows(vcs_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return unique_by_path(row for row in vcs_rows if row.get("ignore_rule_match") or row.get("effectively_ignored"))


def fast_path_status(summary: dict[str, Any]) -> str:
    if (
        summary.get("dirty_required_artifact_count") == 0
        and summary.get("untracked_required_artifact_count") == 0
        and summary.get("active_ignore_required_artifact_count") == 0
        and summary.get("effectively_ignored_required_artifact_count") == 0
    ):
        return "ELIGIBLE"
    return "NOT_ELIGIBLE"


def write_phase0_readpoint() -> dict[str, Any]:
    phase = phase_dir("phase0_readpoint_freeze")
    manifest, artifact_rows = manifest_required_artifacts()
    vcs_rows = artifact_vcs_rows(artifact_rows)
    summary = disposition_vcs_summary(vcs_rows)
    problem_rows = problem_closure_rows(vcs_rows)
    ignored_rows = ignored_diagnostic_coverage_rows(vcs_rows)
    denominator = {
        "schema_version": "dvf-3-3-required-artifact-disposition-denominator-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "manifest_schema": manifest.get("schema_version"),
        "manifest_route": manifest.get("route"),
        "manifest_status": manifest.get("status"),
        "required_artifact_count": len(artifact_rows),
        "required_test_count": len(manifest.get("required_tests", [])),
        "expected_required_artifact_count_is_planning_observation": EXPECTED_REQUIRED_ARTIFACT_COUNT,
        "expected_required_test_count_is_planning_observation": EXPECTED_REQUIRED_TEST_COUNT,
        "denominator_source": "live_current_route_required_validations_manifest",
        "artifact_paths": [row["path"] for row in artifact_rows],
    }
    denominator["required_artifact_denominator_sha256"] = canonical_hash(denominator["artifact_paths"])
    write_json(phase / "required_artifact_denominator.json", denominator)
    write_jsonl(phase / "required_artifact_vcs_rows.jsonl", vcs_rows)
    write_json(phase / "required_artifact_vcs_summary.json", summary)
    write_json(
        phase / "problem_closure_denominator.json",
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-problem-denominator-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "definition": "dirty union active ignored union effectively ignored union untracked required artifacts",
            "problem_closure_denominator_count": len(problem_rows),
            "paths": [row["path"] for row in problem_rows],
            "rows": problem_rows,
        },
    )
    write_json(
        phase / "ignored_diagnostic_coverage_denominator.json",
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-ignored-coverage-denominator-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "definition": "full ignore_rule_match-required population union every effectively_ignored required artifact",
            "ignored_diagnostic_coverage_denominator_count": len(ignored_rows),
            "ignore_rule_match_required_count": summary.get("ignore_rule_match_required_artifact_count"),
            "effectively_ignored_required_artifact_count": summary.get("effectively_ignored_required_artifact_count"),
            "paths": [row["path"] for row in ignored_rows],
            "rows": ignored_rows,
        },
    )
    protected_before = protected_surface_hash_report(
        "dvf-3-3-required-artifact-disposition-protected-baseline-v1"
    )
    write_json(phase / "protected_surface_baseline_hashes.json", protected_before)
    protected_derivation = {
        "schema_version": "dvf-3-3-required-artifact-disposition-protected-surface-derivation-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "protected_surface_derivation_status": "PASS",
        "derived_from_preflight_census_protected_surface": True,
        "generated_evidence_artifacts_excluded_from_protected_rendered_authority": True,
        "source_rendered_lua_bridge_runtime_package_mutation_authorized": False,
        "protected_record_count": protected_before.get("record_count"),
        "protected_paths": [record.get("path") for record in protected_before.get("records", [])],
    }
    write_json(phase / "protected_surface_derivation_report.json", protected_derivation)
    status_result = git(["status", "--porcelain=v1", "--ignored=matching"])
    write_json(phase / "git_environment_report.json", git_environment_report(status_result))
    readpoint_id = canonical_hash(
        {
            "manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
            "denominator_sha256": denominator["required_artifact_denominator_sha256"],
            "vcs_summary": {
                "dirty": summary.get("dirty_required_artifact_count"),
                "ignore_rule_match": summary.get("ignore_rule_match_required_artifact_count"),
                "effectively_ignored": summary.get("effectively_ignored_required_artifact_count"),
                "untracked": summary.get("untracked_required_artifact_count"),
            },
        }
    )
    readpoint = {
        "schema_version": "dvf-3-3-required-artifact-disposition-readpoint-freeze-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "round_id": ROUND_ID,
        "readpoint_id": readpoint_id,
        "evidence_root": rel(EVIDENCE_ROOT),
        "plan": file_record(PLAN_DOC, "direct_plan_artifact"),
        "parent_plan": file_record(PARENT_PLAN_DOC, "parent_closure_plan"),
        "manifest": file_record(LIVE_REQUIRED_MANIFEST, "live_current_route_required_validation_manifest"),
        "required_artifact_count": len(artifact_rows),
        "required_test_count": len(manifest.get("required_tests", [])),
        "problem_closure_denominator_count": len(problem_rows),
        "ignored_diagnostic_coverage_denominator_count": len(ignored_rows),
        "current_readpoint_fast_path_status": fast_path_status(summary),
        "dirty_uses_content_diff_only": True,
        "ignore_rule_match_and_effectively_ignored_are_separate": True,
        "existing_untracked_required_artifacts_enter_disposition_route": True,
        "output_root_disjoint_from_required_artifacts": rel(EVIDENCE_ROOT) not in set(denominator["artifact_paths"]),
    }
    write_json(phase / "readpoint_freeze_report.json", readpoint)
    return {
        "manifest": manifest,
        "artifact_rows": artifact_rows,
        "vcs_rows": vcs_rows,
        "vcs_summary": summary,
        "problem_rows": problem_rows,
        "ignored_coverage_rows": ignored_rows,
        "denominator": denominator,
        "protected_before": protected_before,
        "protected_derivation": protected_derivation,
        "readpoint": readpoint,
    }


def write_phase1_policy_schema(schema_hash: str, owner_rule_report: dict[str, Any]) -> None:
    matrix = {
        "schema_version": "dvf-3-3-required-artifact-disposition-passability-matrix-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "rows": [
            {
                "axis_disposition": "diagnostic_only_preserved_by_tracking",
                "preservation_result": "tracked_original_preservation",
                "passability": "passable",
                "requires_owner_rule_ratification": True,
                "requires_per_artifact_owner_decision": False,
            },
            {
                "axis_disposition": "owner_adopted_evidence_update",
                "preservation_result": "tracked_original_preservation",
                "passability": "passable",
                "requires_owner_decision": True,
                "requires_final_content_dirty_zero": True,
            },
            {
                "axis_disposition": "regeneration_required",
                "preservation_result": "tracked_hash_surrogate",
                "passability": "passable",
                "requires_surrogate_freshness": True,
                "requires_protected_surface_intersection_zero": True,
            },
            {
                "axis_disposition": "preservation_exception_requested",
                "preservation_result": "explicit_non_hash_exception",
                "passability": "owner_pending",
                "requires_owner_decision": True,
                "requires_claim_boundary": True,
            },
            {
                "axis_disposition": "blocker",
                "preservation_result": "none",
                "passability": "blocked",
                "prevents_machine_pass": True,
            },
        ],
    }
    write_json(phase_path("phase1_policy_schema", "disposition_passability_matrix.json"), matrix)
    write_json(
        phase_path("phase1_policy_schema", "auto_seal_rule_ratification_validation_report.json"),
        owner_rule_report,
    )
    write_text(
        phase_path("phase1_policy_schema", "disposition_classification_contract.md"),
        f"""# Required Artifact Disposition Classification Contract

Status: `schema_bound`.

The canonical enum source is `phase1_policy_schema/disposition_schema.json` with sha256 `{schema_hash}`.

Each active row must keep `axis`, `axis_disposition`, `preservation_result`, and `passability` separate. `tracked_hash_surrogate` and `explicit_non_hash_exception` are preservation results, not axis dispositions.

Automatic tracked negative-exception preservation is passable only when an owner-supplied rule ratification record validates. Without that record, matching rows remain `owner_pending`.
""",
    )
    write_text(
        POLICY_DOC,
        f"""# DVF 3-3 Required Artifact Disposition Seal Policy

Status: governance-only / schema-bound.

Canonical schema: `Iris/build/description/v2/staging/{ROUND_ID}/phase1_policy_schema/disposition_schema.json`

Schema sha256: `{schema_hash}`

Allowed axes: `{', '.join(ALLOWED_AXIS)}`.
Allowed axis dispositions: `{', '.join(ALLOWED_AXIS_DISPOSITION)}`.
Allowed preservation results: `{', '.join(ALLOWED_PRESERVATION_RESULT)}`.
Allowed passability values: `{', '.join(ALLOWED_PASSABILITY)}`.

Owner decisions and owner rule ratifications must be supplied under `Iris/build/description/v2/owner_inputs/{ROUND_ID}/`. Staging artifacts may validate and reference those records but cannot create or replace them.

This policy does not authorize source, rendered, Lua bridge, runtime, package, release, manual QA, semantic quality, public-facing text, owner seal, or canonical seal mutation.
""",
    )


def has_auto_negative_exception_predicate(row: dict[str, Any]) -> bool:
    return (
        row.get("tracked") is True
        and row.get("ignore_rule_match") is True
        and row.get("ignore_rule_is_negative_exception") is True
        and row.get("ignore_active") is False
        and row.get("effectively_ignored") is False
        and row.get("dirty") is False
        and row.get("untracked") is False
    )


def base_disposition_row(axis: str, row: dict[str, Any], row_id: int) -> dict[str, Any]:
    return {
        "row_id": f"{axis}-{row_id:04d}",
        "axis": axis,
        "path": row.get("path"),
        "artifact_sha256": row.get("artifact_sha256"),
        "manifest_index": row.get("manifest_index"),
        "vcs_tuple": {
            "tracked": row.get("tracked"),
            "untracked": row.get("untracked"),
            "dirty": row.get("dirty"),
            "dirty_staged": row.get("dirty_staged"),
            "dirty_unstaged": row.get("dirty_unstaged"),
            "ignore_rule_match": row.get("ignore_rule_match"),
            "ignore_rule_is_negative_exception": row.get("ignore_rule_is_negative_exception"),
            "ignore_active": row.get("ignore_active"),
            "effectively_ignored": row.get("effectively_ignored"),
            "git_ignore_source": row.get("git_ignore_source"),
            "ignore_match_pattern": row.get("ignore_match_pattern"),
        },
    }


def build_dirty_dispositions(vcs_rows: list[dict[str, Any]], owner_decisions: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    dirty_rows = [row for row in vcs_rows if row.get("dirty")]
    for index, row in enumerate(dirty_rows, 1):
        record = selected_owner_decision(owner_decisions, str(row.get("path")), "adopt_evidence_update")
        next_row = base_disposition_row("dirty", row, index)
        if record:
            next_row.update(
                {
                    "axis_disposition": "owner_adopted_evidence_update",
                    "preservation_result": "tracked_original_preservation",
                    "passability": "blocked",
                    "owner_decision_status": "PASS",
                    "owner_decision_record": {"path": record["path"], "sha256": record["sha256"]},
                    "owner_adoption_dirty_clean_status": "FAIL",
                    "rationale": "owner adoption exists, but current content dirty remains until a clean final recensus proves preservation",
                }
            )
        else:
            next_row.update(
                {
                    "axis_disposition": "blocker",
                    "preservation_result": "none",
                    "passability": "blocked",
                    "owner_decision_status": "missing",
                    "owner_adoption_dirty_clean_status": "not_applicable",
                    "rationale": "dirty required artifact has no owner adoption, deterministic regeneration proof, or clean VCS preservation",
                }
            )
        rows.append(next_row)
    return rows


def build_ignored_dispositions(
    ignored_rows: list[dict[str, Any]],
    owner_rule_report: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    binding_pass = owner_rule_report.get("owner_rule_ratification_binding_status") == "PASS"
    rule_record = None
    if owner_rule_report.get("valid_records"):
        rule_record = {
            "path": owner_rule_report["valid_records"][0]["path"],
            "sha256": owner_rule_report["valid_records"][0]["sha256"],
        }
    for index, row in enumerate(ignored_rows, 1):
        next_row = base_disposition_row("ignored", row, index)
        if has_auto_negative_exception_predicate(row):
            next_row.update(
                {
                    "axis_disposition": "diagnostic_only_preserved_by_tracking",
                    "preservation_result": "tracked_original_preservation",
                    "passability": "passable" if binding_pass else "owner_pending",
                    "auto_seal_rule_id": AUTO_SEAL_RULE_ID,
                    "auto_seal_predicate_version": AUTO_SEAL_PREDICATE_VERSION,
                    "auto_seal_rule_state": "ratified" if binding_pass else "owner-ratification-pending",
                    "auto_seal_rule_ratification_status": "ratified" if binding_pass else "owner-ratification-pending",
                    "owner_rule_ratification_record": rule_record,
                    "per_artifact_owner_decision_required": False,
                    "rationale": "tracked required artifact is preserved by original tracking and a negative .gitignore exception; automatic passability is owner-rule-gated",
                }
            )
        elif row.get("tracked") and not row.get("dirty") and not row.get("untracked") and not row.get("effectively_ignored"):
            next_row.update(
                {
                    "axis_disposition": "not_preservation_relevant_with_rationale",
                    "preservation_result": "tracked_original_preservation",
                    "passability": "passable",
                    "auto_seal_rule_state": "not_applicable",
                    "auto_seal_rule_ratification_status": "not_applicable",
                    "rationale": "ignore diagnostic does not make the tracked clean required artifact effectively ignored",
                }
            )
        else:
            next_row.update(
                {
                    "axis_disposition": "blocker",
                    "preservation_result": "none",
                    "passability": "blocked",
                    "auto_seal_rule_state": "not_applicable",
                    "auto_seal_rule_ratification_status": "not_applicable",
                    "rationale": "ignored required artifact is not safely preserved by tracking at this readpoint",
                }
            )
        rows.append(next_row)
    return rows


def build_untracked_dispositions(vcs_rows: list[dict[str, Any]], already_disposed: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    untracked_rows = [row for row in vcs_rows if row.get("untracked") and row.get("path") not in already_disposed]
    for index, row in enumerate(untracked_rows, 1):
        next_row = base_disposition_row("untracked", row, index)
        next_row.update(
            {
                "axis_disposition": "blocker",
                "preservation_result": "none",
                "passability": "blocked",
                "rationale": "untracked required artifact cannot be considered preserved without narrow tracking, surrogate, exception, or owner-approved removal",
            }
        )
        rows.append(next_row)
    return rows


def write_phase2_dirty(dirty_rows: list[dict[str, Any]]) -> None:
    write_jsonl(phase_path("phase2_dirty_disposition", "dirty_required_artifact_disposition_ledger.jsonl"), dirty_rows)
    write_json(
        phase_path("phase2_dirty_disposition", "dirty_required_artifact_diff_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-dirty-diff-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "dirty_required_artifact_count": len(dirty_rows),
            "dirty_uses_content_diff_only": True,
            "paths": [row["path"] for row in dirty_rows],
        },
    )
    owner_adopted = [row for row in dirty_rows if row.get("axis_disposition") == "owner_adopted_evidence_update"]
    regeneration = [row for row in dirty_rows if row.get("axis_disposition") == "regeneration_required"]
    blockers = [row for row in dirty_rows if row.get("passability") == "blocked"]
    write_json(
        phase_path("phase2_dirty_disposition", "owner_adopted_update_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-owner-adopted-dirty-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "owner_adopted_dirty_count": len(owner_adopted),
            "owner_adoption_dirty_clean_status": "PASS" if not owner_adopted else "FAIL",
            "rows": owner_adopted,
        },
    )
    write_json(
        phase_path("phase2_dirty_disposition", "regeneration_required_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-regeneration-required-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "regeneration_required_count": len(regeneration),
            "regeneration_required_protected_surface_intersection_count": 0,
            "rows": regeneration,
        },
    )
    write_json(
        phase_path("phase2_dirty_disposition", "dirty_blocker_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-dirty-blocker-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "dirty_blocker_count": len(blockers),
            "rows": blockers,
        },
    )


def write_phase3_ignored(
    ignored_rows: list[dict[str, Any]],
    untracked_rows: list[dict[str, Any]],
    coverage_rows: list[dict[str, Any]],
    problem_rows: list[dict[str, Any]],
    vcs_summary: dict[str, Any],
) -> None:
    write_jsonl(
        phase_path("phase3_ignored_disposition", "ignored_required_artifact_disposition_ledger.jsonl"),
        ignored_rows,
    )
    write_json(
        phase_path("phase3_ignored_disposition", "ignored_rule_match_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-ignore-rule-match-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "ignore_rule_match_required_count": vcs_summary.get("ignore_rule_match_required_artifact_count"),
            "active_ignore_required_artifact_count": vcs_summary.get("active_ignore_required_artifact_count"),
            "ignored_19_compared_to_ignore_rule_match_required": True,
            "rows": [row for row in coverage_rows if row.get("ignore_rule_match")],
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "effectively_ignored_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-effectively-ignored-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "effectively_ignored_required_artifact_count": vcs_summary.get("effectively_ignored_required_artifact_count"),
            "rows": [row for row in coverage_rows if row.get("effectively_ignored")],
        },
    )
    bare_count = max(0, len(coverage_rows) - len(ignored_rows))
    negative_auto = [row for row in ignored_rows if row.get("auto_seal_rule_state") == "ratified"]
    negative_candidates = [
        row for row in ignored_rows if row.get("axis_disposition") == "diagnostic_only_preserved_by_tracking"
    ]
    blockers = [row for row in [*ignored_rows, *untracked_rows] if row.get("passability") == "blocked"]
    write_json(
        phase_path("phase3_ignored_disposition", "ignored_diagnostic_coverage_denominator_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-ignored-coverage-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "ignored_diagnostic_coverage_denominator_count": len(coverage_rows),
            "disposed_coverage_row_count": len(ignored_rows),
            "bare_diagnostic_count": bare_count,
            "paths": [row["path"] for row in coverage_rows],
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "problem_closure_denominator_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-problem-closure-denominator-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "problem_closure_denominator_count": len(problem_rows),
            "paths": [row["path"] for row in problem_rows],
            "rows": problem_rows,
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "negative_exception_auto_disposition_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-negative-exception-auto-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "negative_exception_candidate_count": len(negative_candidates),
            "negative_exception_auto_disposition_count": len(negative_auto),
            "owner_ratification_required_before_passable": True,
            "rows": negative_candidates,
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "bare_diagnostic_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-bare-diagnostic-report-v1",
            "generated_at": now_iso(),
            "status": "PASS" if bare_count == 0 else "FAIL",
            "bare_diagnostic_count": bare_count,
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "untracked_required_artifact_disposition_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-untracked-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "untracked_required_artifact_count": vcs_summary.get("untracked_required_artifact_count"),
            "untracked_disposition_row_count": len(untracked_rows),
            "rows": untracked_rows,
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "narrow_tracking_exception_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-narrow-tracking-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "broad_staging_unignore_count": broad_staging_unignore_count(),
            "track_narrowly_count": sum(1 for row in [*ignored_rows, *untracked_rows] if row.get("axis_disposition") == "track_narrowly"),
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "hash_surrogate_binding_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-hash-surrogate-binding-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "tracked_hash_surrogate_count": sum(1 for row in [*ignored_rows, *untracked_rows] if row.get("preservation_result") == "tracked_hash_surrogate"),
            "surrogate_freshness_status": "NOT_APPLICABLE",
            "surrogate_regeneration_mismatch_count": 0,
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "non_hash_exception_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-non-hash-exception-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "explicit_non_hash_exception_count": sum(1 for row in [*ignored_rows, *untracked_rows] if row.get("preservation_result") == "explicit_non_hash_exception"),
        },
    )
    write_json(
        phase_path("phase3_ignored_disposition", "ignored_blocker_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-ignored-blocker-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "ignored_or_untracked_blocker_count": len(blockers),
            "rows": blockers,
        },
    )


def referenced_owner_record_paths(disposition_rows: list[dict[str, Any]], owner_rule_report: dict[str, Any]) -> list[str]:
    paths: set[str] = set()
    for row in disposition_rows:
        for key in ["owner_decision_record", "owner_rule_ratification_record"]:
            record = row.get(key)
            if isinstance(record, dict) and record.get("path"):
                paths.add(str(record["path"]))
    if owner_rule_report.get("owner_rule_ratification_binding_status") == "PASS":
        for record in owner_rule_report.get("valid_records", []):
            paths.add(str(record["path"]))
    return sorted(paths)


def owner_input_vcs_report(paths: list[str]) -> dict[str, Any]:
    rows = [vcs_state(path) for path in paths]
    tracked = sum(1 for row in rows if row.get("tracked"))
    effectively_ignored = sum(1 for row in rows if row.get("effectively_ignored"))
    dirty = sum(1 for row in rows if row.get("dirty"))
    untracked = sum(1 for row in rows if row.get("untracked"))
    status = "PASS" if not paths or (tracked == len(paths) and effectively_ignored == 0 and dirty == 0 and untracked == 0) else "FAIL"
    return {
        "schema_version": "dvf-3-3-required-artifact-disposition-owner-input-vcs-preservation-v1",
        "generated_at": now_iso(),
        "status": status,
        "owner_input_record_vcs_preservation_status": status if paths else "NOT_APPLICABLE",
        "owner_input_record_count": len(paths),
        "owner_input_record_tracked_count": tracked,
        "owner_input_record_effectively_ignored_count": effectively_ignored,
        "owner_input_record_dirty_count": dirty,
        "owner_input_record_untracked_count": untracked,
        "rows": rows,
    }


def broad_staging_unignore_count() -> int:
    gitignore = REPO_ROOT / ".gitignore"
    if not gitignore.exists():
        return 0
    forbidden = {
        "!Iris/build/description/v2/staging/*",
        "!Iris/build/description/v2/staging/**",
    }
    count = 0
    for line in gitignore.read_text(encoding="utf-8").splitlines():
        if line.strip() in forbidden:
            count += 1
    return count


def write_phase4_manifest_guard(
    disposition_rows: list[dict[str, Any]],
    owner_decision_report: dict[str, Any],
    owner_rule_report: dict[str, Any],
    owner_vcs_report: dict[str, Any],
) -> None:
    removal_candidates = [row for row in disposition_rows if row.get("axis_disposition") == "manifest_removal_candidate"]
    blockers = [row for row in disposition_rows if row.get("passability") == "blocked"]
    owner_pending = [row for row in disposition_rows if row.get("passability") == "owner_pending"]
    write_json(
        phase_path("phase4_manifest_guard_integration", "manifest_removal_proposal.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-manifest-removal-proposal-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "manifest_removal_candidate_count": len(removal_candidates),
            "live_manifest_mutated": False,
            "rows": removal_candidates,
        },
    )
    write_json(
        phase_path("phase4_manifest_guard_integration", "live_manifest_disposition_integration_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-live-manifest-integration-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "live_manifest_mutated": False,
            "candidate_manifest_created": False,
            "required_gate_adoption_status": "not_adopted_by_this_round",
            "governance_only": True,
        },
    )
    write_json(
        phase_path("phase4_manifest_guard_integration", "manifest_diff_scope_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-manifest-diff-scope-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "existing_required_artifact_removed_count": 0,
            "existing_required_test_removed_count": 0,
            "candidate_live_manifest_separation": True,
        },
    )
    write_json(
        phase_path("phase4_manifest_guard_integration", "blocker_propagation_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-blocker-propagation-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "blocker_count": len(blockers),
            "owner_pending_count": len(owner_pending),
            "machine_pass_blocked": bool(blockers or owner_pending),
            "blockers": blockers,
            "owner_pending_rows": owner_pending,
        },
    )
    write_json(
        phase_path("phase4_manifest_guard_integration", "new_required_artifact_preservation_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-new-required-artifact-preservation-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "new_required_artifact_preservation_status": "NOT_APPLICABLE",
            "new_required_artifact_count": 0,
            "self_reference_cycle_count": 0,
            "broad_staging_unignore_count": broad_staging_unignore_count(),
        },
    )
    write_json(
        phase_path("phase4_manifest_guard_integration", "owner_decision_record_validation_report.json"),
        owner_decision_report,
    )
    write_json(
        phase_path("phase4_manifest_guard_integration", "owner_input_record_vcs_preservation_report.json"),
        owner_vcs_report,
    )
    write_json(
        phase_path("phase4_manifest_guard_integration", "owner_rule_ratification_consumption_report.json"),
        owner_rule_report,
    )


def validate_rows(
    rows: list[dict[str, Any]],
    *,
    schema: dict[str, Any],
    owner_rule_binding_status: str,
    final_vcs_by_path: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    final_vcs_by_path = final_vcs_by_path or {}
    for row in rows:
        row_id = row.get("row_id")
        for field, allowed in [
            ("axis", schema["axis"]),
            ("axis_disposition", schema["axis_disposition"]),
            ("preservation_result", schema["preservation_result"]),
            ("passability", schema["passability"]),
        ]:
            if row.get(field) not in allowed:
                errors.append({"code": "enum_mismatch", "row_id": row_id, "field": field, "observed": row.get(field)})
        if row.get("axis_disposition") in schema["preservation_result"]:
            errors.append({"code": "preservation_result_used_as_axis_disposition", "row_id": row_id})
        if row.get("axis_disposition") == "blocker" and row.get("passability") == "passable":
            errors.append({"code": "blocker_marked_passable", "row_id": row_id})
        if row.get("passability") == "passable" and row.get("preservation_result") == "tracked_hash_surrogate":
            binding = row.get("surrogate_binding")
            if not isinstance(binding, dict):
                errors.append({"code": "missing_surrogate_binding", "row_id": row_id})
            if row.get("surrogate_freshness_status") != "PASS":
                errors.append({"code": "surrogate_freshness_not_pass", "row_id": row_id})
        if row.get("preservation_result") == "explicit_non_hash_exception":
            if not row.get("claim_boundary"):
                errors.append({"code": "missing_exception_claim_boundary", "row_id": row_id})
            if row.get("passability") == "passable" and row.get("owner_decision_status") != "PASS":
                errors.append({"code": "exception_passable_without_owner_decision", "row_id": row_id})
        if row.get("axis_disposition") == "owner_adopted_evidence_update":
            if row.get("owner_decision_status") != "PASS":
                errors.append({"code": "owner_adopted_missing_owner_decision", "row_id": row_id})
            final_vcs = final_vcs_by_path.get(str(row.get("path")), {})
            if row.get("passability") == "passable" and final_vcs.get("dirty"):
                errors.append({"code": "owner_adopted_dirty_still_dirty", "row_id": row_id})
        if row.get("axis_disposition") == "diagnostic_only_preserved_by_tracking":
            predicate = row.get("vcs_tuple", {})
            final_vcs = final_vcs_by_path.get(str(row.get("path")), {})
            predicate_ok = (
                predicate.get("tracked") is True
                and predicate.get("ignore_rule_match") is True
                and predicate.get("ignore_rule_is_negative_exception") is True
                and predicate.get("ignore_active") is False
                and predicate.get("effectively_ignored") is False
                and predicate.get("dirty") is False
                and predicate.get("untracked") is False
            )
            if row.get("passability") == "passable":
                if owner_rule_binding_status != "PASS":
                    errors.append({"code": "auto_seal_passable_without_owner_rule_ratification", "row_id": row_id})
                if not predicate_ok:
                    errors.append({"code": "auto_seal_predicate_not_satisfied", "row_id": row_id})
                if final_vcs and row_has_final_preservation_regression(final_vcs):
                    errors.append({"code": "auto_seal_final_vcs_not_preserved", "row_id": row_id})
            if row.get("auto_seal_rule_state") == "owner-ratification-pending" and row.get("passability") != "owner_pending":
                errors.append({"code": "pending_auto_seal_not_owner_pending", "row_id": row_id})
        if row.get("axis") == "untracked" and not row.get("axis_disposition"):
            errors.append({"code": "untracked_required_artifact_without_disposition", "row_id": row_id})
    return errors


def negative_fixture_matrix(schema: dict[str, Any]) -> dict[str, Any]:
    valid_tuple = {
        "tracked": True,
        "untracked": False,
        "dirty": False,
        "ignore_rule_match": True,
        "ignore_rule_is_negative_exception": True,
        "ignore_active": False,
        "effectively_ignored": False,
    }
    fixtures = [
        (
            "unknown_axis_disposition",
            {
                "row_id": "fixture-001",
                "axis": "ignored",
                "axis_disposition": "tracked_hash_surrogate",
                "preservation_result": "none",
                "passability": "passable",
                "vcs_tuple": valid_tuple,
            },
        ),
        (
            "missing_surrogate_binding",
            {
                "row_id": "fixture-002",
                "axis": "ignored",
                "axis_disposition": "regeneration_required",
                "preservation_result": "tracked_hash_surrogate",
                "passability": "passable",
                "surrogate_freshness_status": "PASS",
                "vcs_tuple": valid_tuple,
            },
        ),
        (
            "stale_surrogate_freshness",
            {
                "row_id": "fixture-003",
                "axis": "ignored",
                "axis_disposition": "regeneration_required",
                "preservation_result": "tracked_hash_surrogate",
                "passability": "passable",
                "surrogate_binding": {"source_hash": "old"},
                "surrogate_freshness_status": "FAIL",
                "vcs_tuple": valid_tuple,
            },
        ),
        (
            "owner_adopted_still_dirty",
            {
                "row_id": "fixture-004",
                "axis": "dirty",
                "path": "fixture.json",
                "axis_disposition": "owner_adopted_evidence_update",
                "preservation_result": "tracked_original_preservation",
                "passability": "passable",
                "owner_decision_status": "PASS",
                "vcs_tuple": {"dirty": True},
            },
        ),
        (
            "exception_without_claim_boundary",
            {
                "row_id": "fixture-005",
                "axis": "ignored",
                "axis_disposition": "preservation_exception_requested",
                "preservation_result": "explicit_non_hash_exception",
                "passability": "passable",
                "owner_decision_status": "PASS",
                "vcs_tuple": valid_tuple,
            },
        ),
        (
            "auto_seal_missing_owner_rule",
            {
                "row_id": "fixture-006",
                "axis": "ignored",
                "axis_disposition": "diagnostic_only_preserved_by_tracking",
                "preservation_result": "tracked_original_preservation",
                "passability": "passable",
                "auto_seal_rule_state": "ratified",
                "vcs_tuple": valid_tuple,
            },
        ),
        (
            "near_miss_auto_seal_dirty",
            {
                "row_id": "fixture-007",
                "axis": "ignored",
                "axis_disposition": "diagnostic_only_preserved_by_tracking",
                "preservation_result": "tracked_original_preservation",
                "passability": "passable",
                "auto_seal_rule_state": "ratified",
                "vcs_tuple": {**valid_tuple, "dirty": True},
            },
        ),
        (
            "near_miss_auto_seal_untracked",
            {
                "row_id": "fixture-008",
                "axis": "ignored",
                "axis_disposition": "diagnostic_only_preserved_by_tracking",
                "preservation_result": "tracked_original_preservation",
                "passability": "passable",
                "auto_seal_rule_state": "ratified",
                "vcs_tuple": {**valid_tuple, "tracked": False, "untracked": True},
            },
        ),
        (
            "near_miss_auto_seal_active_ignore",
            {
                "row_id": "fixture-009",
                "axis": "ignored",
                "axis_disposition": "diagnostic_only_preserved_by_tracking",
                "preservation_result": "tracked_original_preservation",
                "passability": "passable",
                "auto_seal_rule_state": "ratified",
                "vcs_tuple": {**valid_tuple, "ignore_active": True},
            },
        ),
        (
            "near_miss_auto_seal_non_negative",
            {
                "row_id": "fixture-010",
                "axis": "ignored",
                "axis_disposition": "diagnostic_only_preserved_by_tracking",
                "preservation_result": "tracked_original_preservation",
                "passability": "passable",
                "auto_seal_rule_state": "ratified",
                "vcs_tuple": {**valid_tuple, "ignore_rule_is_negative_exception": False},
            },
        ),
    ]
    rows = []
    for case_id, row in fixtures:
        errors = validate_rows([row], schema=schema, owner_rule_binding_status="OWNER_PENDING", final_vcs_by_path={"fixture.json": {"dirty": True}})
        rows.append(
            {
                "case_id": case_id,
                "expected": "FAIL_CLOSED",
                "observed": "FAIL_CLOSED" if errors else "UNEXPECTED_PASS",
                "status": "PASS" if errors else "FAIL",
                "errors": errors,
            }
        )
    report = {
        "schema_version": "dvf-3-3-required-artifact-disposition-negative-fixture-matrix-v1",
        "generated_at": now_iso(),
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
        "case_count": len(rows),
        "rows": rows,
    }
    return report


def run_current_route_validation(run: bool) -> dict[str, Any]:
    out_path = phase_path("phase5_fail_closed_validation", "current_route_validation_result.json")
    if not run:
        payload = {
            "schema_version": "round3-contract-test-run-v1",
            "generated_at": now_iso(),
            "status": "SKIPPED",
            "success": False,
            "closure_enforced": False,
            "skip_reason": "run_current_route_false",
        }
        write_json(out_path, payload)
        return payload
    env = os.environ.copy()
    env["DVF_REQUIRED_ARTIFACT_DISPOSITION_INNER_CURRENT_ROUTE"] = "1"
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
        env=env,
    )
    payload = read_json_object(out_path)
    if not payload:
        payload = {"schema_version": "round3-contract-test-run-v1"}
    payload["command"] = result
    payload["timeout_budget_seconds"] = CURRENT_ROUTE_TIMEOUT_SECONDS
    payload["status"] = "PASS" if result.get("exit_code") == 0 and payload.get("success") is True else "FAIL"
    if result.get("timed_out"):
        payload["status"] = "FAIL"
        payload["failure_classification"] = "timeout"
    elif payload["status"] == "FAIL":
        payload["failure_classification"] = "current_route_regression_or_preexisting_failure"
    else:
        payload["failure_classification"] = "none"
    write_json(out_path, payload)
    return payload


def write_phase5_validation(
    schema: dict[str, Any],
    disposition_rows: list[dict[str, Any]],
    owner_rule_report: dict[str, Any],
    protected_before: dict[str, Any],
    run_current_route: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    negative = negative_fixture_matrix(schema)
    write_json(phase_path("phase5_fail_closed_validation", "negative_fixture_matrix.json"), negative)
    current_route = run_current_route_validation(run_current_route)
    protected_after = protected_surface_hash_report(
        "dvf-3-3-required-artifact-disposition-protected-after-v1"
    )
    no_mutation = diff_hash_reports(protected_before, protected_after)
    write_json(phase_path("phase5_fail_closed_validation", "protected_surface_no_mutation_report.json"), no_mutation)
    validation_errors = validate_rows(
        disposition_rows,
        schema=schema,
        owner_rule_binding_status=str(owner_rule_report.get("owner_rule_ratification_binding_status")),
    )
    fail_closed = {
        "schema_version": "dvf-3-3-required-artifact-disposition-fail-closed-validation-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not validation_errors and negative.get("status") == "PASS" and no_mutation.get("changed_count") == 0 else "FAIL",
        "disposition_validation_error_count": len(validation_errors),
        "disposition_validation_errors": validation_errors,
        "negative_fixture_matrix_status": negative.get("status"),
        "protected_surface_changed_count": no_mutation.get("changed_count"),
        "current_route_validation_state": current_route.get("status"),
        "current_route_regression_separate_from_disposition_validator": True,
    }
    write_json(phase_path("phase5_fail_closed_validation", "fail_closed_validation_report.json"), fail_closed)
    return fail_closed, no_mutation, current_route


def terminal_from_state(
    *,
    validation_failed: bool,
    blocker_count: int,
    owner_pending_count: int,
    ready_conditions_met: bool,
) -> tuple[str, str, str, bool]:
    if validation_failed:
        return "validation_failed", "VALIDATION_FAILED", "validation_failed", True
    if blocker_count:
        return "complete_with_blockers", "SOLVED_WITH_MACHINE_BLOCKERS", "blocked", True
    if owner_pending_count:
        return "owner_pending", "OWNER_PENDING", "owner_pending", True
    if ready_conditions_met:
        return "ready", "SOLVED", "ready", False
    return "validation_failed", "VALIDATION_FAILED", "validation_failed", True


def final_recensus(artifact_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = artifact_vcs_rows(artifact_rows)
    summary = disposition_vcs_summary(rows)
    return rows, summary


FINAL_PRESERVATION_ZERO_FIELDS = [
    "dirty_required_artifact_count",
    "untracked_required_artifact_count",
    "active_ignore_required_artifact_count",
    "effectively_ignored_required_artifact_count",
]


def int_field(payload: dict[str, Any], field: str) -> int:
    value = payload.get(field, 0)
    return value if isinstance(value, int) else 0


def final_vcs_preservation_ready(summary: dict[str, Any]) -> bool:
    return all(int_field(summary, field) == 0 for field in FINAL_PRESERVATION_ZERO_FIELDS)


def final_vcs_preservation_regression_count(summary: dict[str, Any]) -> int:
    return sum(int_field(summary, field) for field in FINAL_PRESERVATION_ZERO_FIELDS)


def owner_input_vcs_preserved(owner_vcs_report: dict[str, Any]) -> bool:
    return (
        owner_vcs_report.get("status") == "PASS"
        and owner_vcs_report.get("owner_input_record_vcs_preservation_status") in {"PASS", "NOT_APPLICABLE"}
    )


def row_has_final_preservation_regression(row: dict[str, Any]) -> bool:
    return bool(row.get("dirty") or row.get("untracked") or row.get("ignore_active") or row.get("effectively_ignored"))


def axis_for_final_preservation_regression(row: dict[str, Any]) -> str:
    if row.get("dirty"):
        return "dirty"
    if row.get("untracked"):
        return "untracked"
    return "ignored"


def write_phase6_closeout(
    context: dict[str, Any],
    schema_hash: str,
    disposition_rows: list[dict[str, Any]],
    owner_decision_report: dict[str, Any],
    owner_rule_report: dict[str, Any],
    owner_vcs_report: dict[str, Any],
    fail_closed: dict[str, Any],
    no_mutation: dict[str, Any],
    current_route: dict[str, Any],
) -> dict[str, Any]:
    final_rows, final_summary = final_recensus(context["artifact_rows"])
    final_vcs_by_path = {str(row["path"]): row for row in final_rows}
    existing_disposition_paths = {
        str(row.get("path"))
        for row in disposition_rows
        if row.get("path")
    }
    late_preservation_blocker_rows = [
        row
        for row in final_rows
        if row_has_final_preservation_regression(row) and str(row.get("path")) not in existing_disposition_paths
    ]
    for index, row in enumerate(late_preservation_blocker_rows, 1):
        axis = axis_for_final_preservation_regression(row)
        next_row = base_disposition_row(axis, row, index)
        next_row.update(
            {
                "row_id": f"{axis}-final-{index:04d}",
                "axis_disposition": "blocker",
                "preservation_result": "none",
                "passability": "blocked",
                "owner_decision_status": "missing",
                "owner_adoption_dirty_clean_status": "FAIL",
                "rationale": "final recensus found a required artifact VCS preservation regression after the initial disposition pass; machine PASS remains blocked until a clean recensus or owner-approved preservation route exists",
            }
        )
        disposition_rows.append(next_row)
    final_row_errors = validate_rows(
        disposition_rows,
        schema=disposition_schema_payload(),
        owner_rule_binding_status=str(owner_rule_report.get("owner_rule_ratification_binding_status")),
        final_vcs_by_path=final_vcs_by_path,
    )
    write_jsonl(phase_path("phase6_closeout_claim_boundary", "disposition_ledger.jsonl"), disposition_rows)
    write_json(
        phase_path("phase6_closeout_claim_boundary", "final_recensus_report.json"),
        {
            "schema_version": "dvf-3-3-required-artifact-disposition-final-recensus-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "rows": final_rows,
            "summary": final_summary,
        },
    )
    owner_pending_count = sum(1 for row in disposition_rows if row.get("passability") == "owner_pending")
    blocker_count = sum(1 for row in disposition_rows if row.get("passability") == "blocked")
    bare_report = read_json_object(
        phase_path("phase3_ignored_disposition", "bare_diagnostic_report.json")
    )
    bare_count = int(bare_report.get("bare_diagnostic_count", 0))
    negative_auto_report = read_json_object(
        phase_path("phase3_ignored_disposition", "negative_exception_auto_disposition_report.json")
    )
    current_route_required_complete = current_route.get("status") == "PASS"
    final_vcs_ready = final_vcs_preservation_ready(final_summary)
    owner_input_preserved = owner_input_vcs_preserved(owner_vcs_report)
    validation_failed = (
        fail_closed.get("status") != "PASS"
        or no_mutation.get("changed_count") != 0
        or bool(final_row_errors)
        or bare_count != 0
        or broad_staging_unignore_count() != 0
        or not final_vcs_ready
        or not owner_input_preserved
    )
    ready_conditions_met = (
        not validation_failed
        and blocker_count == 0
        and owner_pending_count == 0
        and current_route_required_complete
        and final_vcs_ready
        and bare_count == 0
        and owner_input_preserved
        and owner_rule_report.get("owner_rule_ratification_binding_status") in {"PASS", "NOT_APPLICABLE"}
    )
    terminal_state, problem_status, artifact_state, machine_pass_blocked = terminal_from_state(
        validation_failed=validation_failed,
        blocker_count=blocker_count,
        owner_pending_count=owner_pending_count,
        ready_conditions_met=ready_conditions_met,
    )
    fast_path = context["readpoint"].get("current_readpoint_fast_path_status")
    fast_path_used = (
        terminal_state == "ready"
        and fast_path == "ELIGIBLE"
        and bare_count == 0
        and final_vcs_ready
        and owner_input_preserved
        and owner_rule_report.get("owner_rule_ratification_binding_status") == "PASS"
    )
    dirty_axis_verdict = "ready_clean" if final_summary.get("dirty_required_artifact_count") == 0 else "blocked_dirty_not_preserved"
    if any(row.get("axis") == "dirty" and row.get("passability") == "owner_pending" for row in disposition_rows):
        dirty_axis_verdict = "owner_pending"
    ignored_axis_verdict = "ready_preserved"
    if any(row.get("axis") in {"ignored", "untracked"} and row.get("passability") == "blocked" for row in disposition_rows):
        ignored_axis_verdict = "blocked_not_preserved"
    if not final_vcs_ready:
        ignored_axis_verdict = "blocked_not_preserved"
    if any(row.get("axis") in {"ignored", "untracked"} and row.get("passability") == "owner_pending" for row in disposition_rows):
        ignored_axis_verdict = "owner_pending"
    final_report = {
        "schema_version": "dvf-3-3-required-artifact-disposition-final-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not validation_failed else "FAIL",
        "round_id": ROUND_ID,
        "readpoint_id": context["readpoint"].get("readpoint_id"),
        "required_artifact_disposition_problem_status": problem_status,
        "terminal_state": terminal_state,
        "ready": terminal_state == "ready",
        "current_readpoint_fast_path_status": fast_path,
        "fast_path_used": fast_path_used,
        "dirty_axis_verdict": dirty_axis_verdict,
        "ignored_axis_verdict": ignored_axis_verdict,
        "artifact_disposition_state": artifact_state,
        "blocker_count": blocker_count,
        "owner_pending_count": owner_pending_count,
        "surrogate_freshness_status": "NOT_APPLICABLE",
        "new_required_artifact_preservation_status": "NOT_APPLICABLE",
        "auto_seal_rule_ratification_status": owner_rule_report.get("auto_seal_rule_ratification_status"),
        "owner_input_record_vcs_preservation_status": owner_vcs_report.get("owner_input_record_vcs_preservation_status"),
        "no_guess_entry_ready": terminal_state == "ready",
        "problem_closure_denominator_count": len(context["problem_rows"]),
        "ignored_diagnostic_coverage_denominator_count": len(context["ignored_coverage_rows"]),
        "ignore_rule_match_required_count": final_summary.get("ignore_rule_match_required_artifact_count"),
        "active_ignore_required_artifact_count": final_summary.get("active_ignore_required_artifact_count"),
        "effectively_ignored_required_artifact_count": final_summary.get("effectively_ignored_required_artifact_count"),
        "negative_exception_auto_disposition_count": negative_auto_report.get("negative_exception_auto_disposition_count", 0),
        "bare_diagnostic_count": bare_count,
        "untracked_required_artifact_count": final_summary.get("untracked_required_artifact_count"),
        "owner_decision_record_binding_status": owner_decision_report.get("owner_decision_record_binding_status"),
        "owner_rule_ratification_binding_status": owner_rule_report.get("owner_rule_ratification_binding_status"),
        "owner_input_record_tracked_count": owner_vcs_report.get("owner_input_record_tracked_count"),
        "owner_input_record_effectively_ignored_count": owner_vcs_report.get("owner_input_record_effectively_ignored_count"),
        "owner_input_record_dirty_count": owner_vcs_report.get("owner_input_record_dirty_count"),
        "regeneration_required_protected_surface_intersection_count": 0,
        "protected_surface_derivation_status": context["protected_derivation"].get("protected_surface_derivation_status"),
        "surrogate_regeneration_mismatch_count": 0,
        "machine_pass_blocked": machine_pass_blocked,
        "final_dirty_required_artifact_count": final_summary.get("dirty_required_artifact_count"),
        "final_untracked_required_artifact_count": final_summary.get("untracked_required_artifact_count"),
        "final_active_ignore_required_artifact_count": final_summary.get("active_ignore_required_artifact_count"),
        "final_effectively_ignored_required_artifact_count": final_summary.get("effectively_ignored_required_artifact_count"),
        "final_vcs_preservation_status": "PASS" if final_vcs_ready else "FAIL",
        "final_vcs_preservation_regression_count": final_vcs_preservation_regression_count(final_summary),
        "final_vcs_preservation_blocker_count": len(late_preservation_blocker_rows),
        "final_vcs_preservation_blocker_rows": [row.get("path") for row in late_preservation_blocker_rows],
        "final_dirty_blocker_count": len([row for row in late_preservation_blocker_rows if row.get("dirty")]),
        "final_dirty_blocker_rows": [row.get("path") for row in late_preservation_blocker_rows if row.get("dirty")],
        "current_route_validation_state": current_route.get("status"),
        "current_route_regression_required_for_ready": True,
        "independent_review_gate": "BLOCKED",
        "owner_seal_status": "not_claimed",
        "canonical_seal_status": "not_claimed",
        "non_claims": NON_CLAIMS,
        "validation_errors": final_row_errors,
    }
    final_path = phase_path("phase6_closeout_claim_boundary", "final_required_artifact_disposition_report.json")
    write_json(final_path, final_report)
    verdict = {
        "schema_version": "dvf-3-3-required-artifact-disposition-closure-readiness-verdict-v1",
        "generated_at": now_iso(),
        "status": "PASS" if terminal_state in {"ready", "owner_pending", "complete_with_blockers"} else "FAIL",
        "terminal_state": terminal_state,
        "required_artifact_disposition_problem_status": problem_status,
        "ready": terminal_state == "ready",
        "machine_pass_blocked": machine_pass_blocked,
        "classification_complete": terminal_state in {"ready", "owner_pending", "complete_with_blockers"},
        "parent_rerun_required": True,
    }
    write_json(phase_path("phase6_closeout_claim_boundary", "closure_readiness_verdict.json"), verdict)
    write_json(
        phase_path("phase6_closeout_claim_boundary", "owner_input_record_vcs_preservation_report.json"),
        owner_vcs_report,
    )
    final_recensus_path = phase_path("phase6_closeout_claim_boundary", "final_recensus_report.json")
    ledger_path = phase_path("phase6_closeout_claim_boundary", "disposition_ledger.jsonl")
    parent_packet = {
        "schema_version": "dvf-3-3-required-artifact-disposition-parent-input-packet-v1",
        "generated_at": now_iso(),
        "status": "PASS" if terminal_state in {"ready", "owner_pending", "complete_with_blockers"} else "FAIL",
        "parent_round_id": PARENT_ROUND_ID,
        "predecessor_round_id": ROUND_ID,
        "readpoint_id": context["readpoint"].get("readpoint_id"),
        "current_route_manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "required_artifact_denominator_sha256": context["denominator"].get("required_artifact_denominator_sha256"),
        "final_recensus_report_sha256": sha256_file(final_recensus_path),
        "disposition_ledger_sha256": sha256_file(ledger_path),
        "final_disposition_report_sha256": sha256_file(final_path),
        "terminal_state": terminal_state,
        "required_artifact_disposition_problem_status": problem_status,
        "machine_pass_blocked": machine_pass_blocked,
        "parent_rerun_required": True,
        "does_not_claim_parent_machine_pass": True,
        "does_not_claim_canonical_seal": True,
    }
    write_json(phase_path("phase6_closeout_claim_boundary", "parent_closure_input_packet.json"), parent_packet)
    compatibility = {
        "schema_version": "dvf-3-3-required-artifact-disposition-parent-compatibility-contract-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "parent_round_id": PARENT_ROUND_ID,
        "predecessor_round_id": ROUND_ID,
        "readpoint_id": context["readpoint"].get("readpoint_id"),
        "current_route_manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "required_artifact_denominator_sha256": context["denominator"].get("required_artifact_denominator_sha256"),
        "final_recensus_report_sha256": sha256_file(final_recensus_path),
        "disposition_ledger_sha256": sha256_file(ledger_path),
        "owner_rule_ratification_validation_report_sha256": sha256_file(
            phase_path("phase1_policy_schema", "auto_seal_rule_ratification_validation_report.json")
        ),
        "owner_input_record_vcs_preservation_report_sha256": sha256_file(
            phase_path("phase6_closeout_claim_boundary", "owner_input_record_vcs_preservation_report.json")
        ),
        "protected_surface_derivation_report_sha256": sha256_file(
            phase_path("phase0_readpoint_freeze", "protected_surface_derivation_report.json")
        ),
        "terminal_state": terminal_state,
        "parent_rerun_required": True,
        "ready_does_not_map_to_parent_machine_pass": True,
    }
    write_json(phase_path("phase6_closeout_claim_boundary", "parent_compatibility_contract.json"), compatibility)
    mapping = {
        "schema_version": "dvf-3-3-required-artifact-disposition-parent-terminal-state-mapping-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "mappings": {
            "ready": "parent_required_surface_disposition_ready_for_rerun",
            "complete_with_blockers": "blocked_with_required_surface_disposition_packet / no-authority-mutation",
            "owner_pending": "blocked_with_required_surface_disposition_packet / owner_adjudication_required",
            "validation_failed": "blocked / no-authority-mutation",
            "machine_pass_blocked": "blocked_with_required_surface_disposition_packet / no-authority-mutation",
        },
        "observed_terminal_state": terminal_state,
        "observed_parent_mapping": {
            "ready": "parent_required_surface_disposition_ready_for_rerun",
            "complete_with_blockers": "blocked_with_required_surface_disposition_packet / no-authority-mutation",
            "owner_pending": "blocked_with_required_surface_disposition_packet / owner_adjudication_required",
            "validation_failed": "blocked / no-authority-mutation",
            "machine_pass_blocked": "blocked_with_required_surface_disposition_packet / no-authority-mutation",
        }[terminal_state],
        "parent_machine_pass_claimed": False,
    }
    write_json(phase_path("phase6_closeout_claim_boundary", "parent_terminal_state_mapping.json"), mapping)
    write_closeout_docs(final_report, parent_packet)
    return final_report


def write_closeout_docs(final_report: dict[str, Any], parent_packet: dict[str, Any]) -> None:
    non_claims = "\n".join(f"- `{item}`" for item in NON_CLAIMS)
    terminal = final_report.get("terminal_state")
    write_text(
        CLAIM_BOUNDARY_DOC,
        f"""# DVF 3-3 Required Artifact Disposition Seal Claim Boundary

Status: `{terminal}`.

This round is governance-only. It derives the required artifact denominator from the live current-route required-validation manifest, assigns disposition rows for dirty / ignored / untracked required-artifact surfaces, and emits a parent closure input packet.

`ready` means only `parent_required_surface_disposition_ready_for_rerun`. It does not claim parent machine PASS. `complete_with_blockers` means classification-complete with `machine_pass_blocked=true` and `ready=false`; it is not closeout-complete.

Current terminal state: `{terminal}`.
Required artifact disposition problem status: `{final_report.get("required_artifact_disposition_problem_status")}`.
Machine pass blocked: `{final_report.get("machine_pass_blocked")}`.

Non-claims:

{non_claims}
""",
    )
    write_text(
        LEDGER_PACKET_DOC,
        f"""# DVF 3-3 Required Artifact Disposition Seal Ledger Packet

- evidence root: `Iris/build/description/v2/staging/{ROUND_ID}`
- final report: `Iris/build/description/v2/staging/{ROUND_ID}/phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json`
- parent packet: `Iris/build/description/v2/staging/{ROUND_ID}/phase6_closeout_claim_boundary/parent_closure_input_packet.json`
- terminal state: `{terminal}`
- machine pass blocked: `{final_report.get("machine_pass_blocked")}`
- ready: `{final_report.get("ready")}`
- parent rerun required: `{parent_packet.get("parent_rerun_required")}`

If `complete_with_blockers` appears in this packet, it means classification-complete only and must be read with `machine_pass_blocked=true` and `ready=false`. Owner pending rows require owner-supplied input records; staging evidence cannot replace them.

Independent review, owner seal, canonical seal, runtime readiness, package readiness, release readiness, manual QA, semantic quality completion, and public-facing text acceptance remain non-claims.
""",
    )
    write_text(
        CLOSEOUT_DOC,
        f"""# DVF 3-3 Required Artifact Disposition Seal Closeout

Terminal state: `{terminal}`.

The final report is governance-only and parent-rerun-bound. Parent closure must recompute Phase 0 / Phase 5 required-surface evidence and current-route validation before any parent machine PASS claim.
""",
    )


def generate_artifacts(*, run_current_route: bool = False) -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    context = write_phase0_readpoint()
    schema, schema_hash = write_schema()
    owner_rule_report = validate_owner_rule_ratifications(schema_hash)
    write_phase1_policy_schema(schema_hash, owner_rule_report)
    owner_decision_report = validate_owner_decision_records()
    dirty_rows = build_dirty_dispositions(context["vcs_rows"], owner_decision_report)
    write_phase2_dirty(dirty_rows)
    ignored_rows = build_ignored_dispositions(context["ignored_coverage_rows"], owner_rule_report)
    disposed_paths = {str(row.get("path")) for row in [*dirty_rows, *ignored_rows]}
    untracked_rows = build_untracked_dispositions(context["vcs_rows"], disposed_paths)
    write_phase3_ignored(ignored_rows, untracked_rows, context["ignored_coverage_rows"], context["problem_rows"], context["vcs_summary"])
    disposition_rows = [*dirty_rows, *ignored_rows, *untracked_rows]
    owner_paths = referenced_owner_record_paths(disposition_rows, owner_rule_report)
    owner_vcs_report = owner_input_vcs_report(owner_paths)
    write_phase4_manifest_guard(disposition_rows, owner_decision_report, owner_rule_report, owner_vcs_report)
    fail_closed, no_mutation, current_route = write_phase5_validation(
        schema,
        disposition_rows,
        owner_rule_report,
        context["protected_before"],
        run_current_route,
    )
    final = write_phase6_closeout(
        context,
        schema_hash,
        disposition_rows,
        owner_decision_report,
        owner_rule_report,
        owner_vcs_report,
        fail_closed,
        no_mutation,
        current_route,
    )
    return final


def required_report_checks(require_complete: bool) -> list[tuple[str, dict[str, Any]]]:
    checks = [
        ("phase0_readpoint_freeze/readpoint_freeze_report.json", {"status": "PASS"}),
        ("phase0_readpoint_freeze/required_artifact_denominator.json", {"status": "PASS"}),
        ("phase0_readpoint_freeze/problem_closure_denominator.json", {"status": "PASS"}),
        ("phase0_readpoint_freeze/ignored_diagnostic_coverage_denominator.json", {"status": "PASS"}),
        ("phase0_readpoint_freeze/protected_surface_derivation_report.json", {"protected_surface_derivation_status": "PASS"}),
        ("phase1_policy_schema/disposition_schema.json", {"preservation_results_are_not_axis_dispositions": True}),
        ("phase1_policy_schema/disposition_passability_matrix.json", {"status": "PASS"}),
        ("phase1_policy_schema/auto_seal_rule_ratification_validation_report.json", {"status": "PASS"}),
        ("phase2_dirty_disposition/dirty_required_artifact_diff_report.json", {"status": "PASS"}),
        ("phase3_ignored_disposition/ignored_diagnostic_coverage_denominator_report.json", {"status": "PASS", "bare_diagnostic_count": 0}),
        ("phase3_ignored_disposition/bare_diagnostic_report.json", {"status": "PASS", "bare_diagnostic_count": 0}),
        ("phase3_ignored_disposition/narrow_tracking_exception_report.json", {"status": "PASS", "broad_staging_unignore_count": 0}),
        ("phase4_manifest_guard_integration/live_manifest_disposition_integration_report.json", {"live_manifest_mutated": False}),
        ("phase4_manifest_guard_integration/manifest_diff_scope_report.json", {"existing_required_artifact_removed_count": 0, "existing_required_test_removed_count": 0}),
        ("phase4_manifest_guard_integration/blocker_propagation_report.json", {"status": "PASS"}),
        ("phase4_manifest_guard_integration/new_required_artifact_preservation_report.json", {"status": "PASS"}),
        ("phase4_manifest_guard_integration/owner_decision_record_validation_report.json", {"status": "PASS"}),
        ("phase4_manifest_guard_integration/owner_input_record_vcs_preservation_report.json", {"status": "PASS"}),
        ("phase5_fail_closed_validation/negative_fixture_matrix.json", {"status": "PASS"}),
        ("phase5_fail_closed_validation/fail_closed_validation_report.json", {"status": "PASS"}),
        ("phase5_fail_closed_validation/protected_surface_no_mutation_report.json", {"status": "PASS", "changed_count": 0}),
        ("phase6_closeout_claim_boundary/final_recensus_report.json", {"status": "PASS"}),
        ("phase6_closeout_claim_boundary/owner_input_record_vcs_preservation_report.json", {"status": "PASS"}),
        ("phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json", {"independent_review_gate": "BLOCKED"}),
        ("phase6_closeout_claim_boundary/closure_readiness_verdict.json", {"parent_rerun_required": True}),
        ("phase6_closeout_claim_boundary/parent_closure_input_packet.json", {"parent_round_id": PARENT_ROUND_ID, "predecessor_round_id": ROUND_ID, "parent_rerun_required": True}),
        ("phase6_closeout_claim_boundary/parent_compatibility_contract.json", {"parent_round_id": PARENT_ROUND_ID, "predecessor_round_id": ROUND_ID, "parent_rerun_required": True}),
        ("phase6_closeout_claim_boundary/parent_terminal_state_mapping.json", {"parent_machine_pass_claimed": False}),
    ]
    if require_complete:
        checks.append(("phase5_fail_closed_validation/current_route_validation_result.json", {"status": "PASS", "success": True, "closure_enforced": True}))
    return checks


def validate_artifacts(*, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    for relative, expected_fields in required_report_checks(require_complete):
        path = EVIDENCE_ROOT / relative
        if not path.exists():
            errors.append({"code": "missing_required_report", "path": rel(path)})
            continue
        payload = read_json_object(path)
        for field, expected in expected_fields.items():
            _present, observed = object_field(payload, field)
            if observed != expected:
                errors.append({"code": "field_mismatch", "path": rel(path), "field": field, "expected": expected, "observed": observed})
    schema = read_json_object(EVIDENCE_ROOT / "phase1_policy_schema" / "disposition_schema.json")
    disposition_rows = read_jsonl_objects(EVIDENCE_ROOT / "phase6_closeout_claim_boundary" / "disposition_ledger.jsonl")
    owner_rule_report = read_json_object(EVIDENCE_ROOT / "phase1_policy_schema" / "auto_seal_rule_ratification_validation_report.json")
    final_recensus_report = read_json_object(EVIDENCE_ROOT / "phase6_closeout_claim_boundary" / "final_recensus_report.json")
    final_recensus_rows = final_recensus_report.get("rows", []) if isinstance(final_recensus_report.get("rows"), list) else []
    final_vcs_by_path = {
        str(row.get("path")): row
        for row in final_recensus_rows
        if isinstance(row, dict) and row.get("path")
    }
    row_errors = validate_rows(
        disposition_rows,
        schema=schema or disposition_schema_payload(),
        owner_rule_binding_status=str(owner_rule_report.get("owner_rule_ratification_binding_status")),
        final_vcs_by_path=final_vcs_by_path,
    )
    errors.extend(row_errors)
    denominator = read_json_object(EVIDENCE_ROOT / "phase0_readpoint_freeze" / "required_artifact_denominator.json")
    vcs_summary = read_json_object(EVIDENCE_ROOT / "phase0_readpoint_freeze" / "required_artifact_vcs_summary.json")
    ignored_coverage = read_json_object(EVIDENCE_ROOT / "phase3_ignored_disposition" / "ignored_diagnostic_coverage_denominator_report.json")
    final = read_json_object(EVIDENCE_ROOT / "phase6_closeout_claim_boundary" / "final_required_artifact_disposition_report.json")
    owner_vcs_report = read_json_object(EVIDENCE_ROOT / "phase6_closeout_claim_boundary" / "owner_input_record_vcs_preservation_report.json")
    parent_packet = read_json_object(EVIDENCE_ROOT / "phase6_closeout_claim_boundary" / "parent_closure_input_packet.json")
    compatibility = read_json_object(EVIDENCE_ROOT / "phase6_closeout_claim_boundary" / "parent_compatibility_contract.json")
    if denominator and vcs_summary:
        if denominator.get("required_artifact_count") != vcs_summary.get("vcs_tuple_count"):
            errors.append({"code": "denominator_vcs_tuple_mismatch"})
    if ignored_coverage:
        disposed = len([row for row in disposition_rows if row.get("axis") == "ignored"])
        if disposed != ignored_coverage.get("ignored_diagnostic_coverage_denominator_count"):
            errors.append({"code": "ignored_coverage_disposition_mismatch", "disposed": disposed, "coverage": ignored_coverage.get("ignored_diagnostic_coverage_denominator_count")})
        if ignored_coverage.get("bare_diagnostic_count") != 0:
            errors.append({"code": "bare_diagnostic_rows_present"})
    final_summary = final_recensus_report.get("summary", {}) if isinstance(final_recensus_report.get("summary"), dict) else {}
    if final_summary:
        if not final_vcs_preservation_ready(final_summary) and final.get("terminal_state") == "ready":
            errors.append({"code": "ready_with_final_vcs_preservation_regression"})
        for summary_field, final_field in [
            ("dirty_required_artifact_count", "final_dirty_required_artifact_count"),
            ("untracked_required_artifact_count", "final_untracked_required_artifact_count"),
            ("active_ignore_required_artifact_count", "final_active_ignore_required_artifact_count"),
            ("effectively_ignored_required_artifact_count", "final_effectively_ignored_required_artifact_count"),
        ]:
            if final and final.get(final_field) != final_summary.get(summary_field):
                errors.append(
                    {
                        "code": "final_report_recensus_count_mismatch",
                        "summary_field": summary_field,
                        "final_field": final_field,
                        "summary": final_summary.get(summary_field),
                        "final": final.get(final_field),
                    }
                )
        if final and final.get("final_vcs_preservation_status") != ("PASS" if final_vcs_preservation_ready(final_summary) else "FAIL"):
            errors.append({"code": "final_vcs_preservation_status_mismatch"})
    if owner_vcs_report:
        if not owner_input_vcs_preserved(owner_vcs_report):
            errors.append({"code": "owner_input_record_vcs_preservation_not_pass"})
        if final and final.get("owner_input_record_vcs_preservation_status") != owner_vcs_report.get("owner_input_record_vcs_preservation_status"):
            errors.append({"code": "owner_input_record_vcs_preservation_status_mismatch"})
    if final:
        terminal = final.get("terminal_state")
        problem_status = final.get("required_artifact_disposition_problem_status")
        if terminal not in ALLOWED_TERMINAL_STATE:
            errors.append({"code": "unknown_terminal_state", "observed": terminal})
        if problem_status not in ALLOWED_PROBLEM_STATUS:
            errors.append({"code": "unknown_problem_status", "observed": problem_status})
        if terminal == "ready" and problem_status != "SOLVED":
            errors.append({"code": "ready_without_solved_problem_status"})
        if terminal == "ready":
            if final.get("ready") is not True or final.get("machine_pass_blocked") is not False or final.get("status") != "PASS":
                errors.append({"code": "ready_state_contract_mismatch"})
            if final.get("owner_rule_ratification_binding_status") != "PASS":
                errors.append({"code": "ready_without_owner_rule_ratification_pass"})
            if final.get("owner_input_record_vcs_preservation_status") not in {"PASS", "NOT_APPLICABLE"}:
                errors.append({"code": "ready_without_owner_input_vcs_preservation_pass"})
            if final.get("bare_diagnostic_count") != 0:
                errors.append({"code": "ready_with_bare_diagnostics"})
            for field in [
                "final_dirty_required_artifact_count",
                "final_untracked_required_artifact_count",
                "final_active_ignore_required_artifact_count",
                "final_effectively_ignored_required_artifact_count",
                "final_vcs_preservation_regression_count",
            ]:
                if final.get(field) != 0:
                    errors.append({"code": "ready_with_final_vcs_regression_count", "field": field, "observed": final.get(field)})
        if terminal == "complete_with_blockers" and (final.get("machine_pass_blocked") is not True or final.get("ready") is not False):
            errors.append({"code": "complete_with_blockers_missing_machine_block"})
        if terminal == "owner_pending" and problem_status != "OWNER_PENDING":
            errors.append({"code": "owner_pending_problem_status_mismatch"})
        for forbidden in ["release_readiness", "package_readiness", "runtime_readiness", "canonical_seal_allowed"]:
            if final.get(forbidden) is True:
                errors.append({"code": "forbidden_claim", "field": forbidden})
        if require_complete and final.get("terminal_state") == "ready" and final.get("current_route_validation_state") != "PASS":
            errors.append({"code": "ready_without_current_route_pass"})
        if final.get("fast_path_used") is True:
            if final.get("current_readpoint_fast_path_status") != "ELIGIBLE":
                errors.append({"code": "fast_path_used_when_not_eligible"})
            if final.get("owner_rule_ratification_binding_status") != "PASS":
                errors.append({"code": "fast_path_used_without_owner_rule_pass"})
            if final.get("owner_input_record_vcs_preservation_status") not in {"PASS", "NOT_APPLICABLE"}:
                errors.append({"code": "fast_path_used_without_owner_input_vcs_preservation"})
            if final.get("bare_diagnostic_count") != 0:
                errors.append({"code": "fast_path_used_with_bare_diagnostics"})
            for field in [
                "final_dirty_required_artifact_count",
                "final_untracked_required_artifact_count",
                "final_active_ignore_required_artifact_count",
                "final_effectively_ignored_required_artifact_count",
                "final_vcs_preservation_regression_count",
            ]:
                if final.get(field) != 0:
                    errors.append({"code": "fast_path_used_with_final_vcs_regression", "field": field, "observed": final.get(field)})
    if parent_packet and compatibility:
        for field in ["current_route_manifest_sha256", "required_artifact_denominator_sha256", "final_recensus_report_sha256", "disposition_ledger_sha256"]:
            if parent_packet.get(field) != compatibility.get(field):
                errors.append({"code": "parent_hash_binding_mismatch", "field": field})
        if parent_packet.get("does_not_claim_parent_machine_pass") is not True:
            errors.append({"code": "parent_machine_pass_claimed"})
    for doc in [POLICY_DOC, CLAIM_BOUNDARY_DOC, LEDGER_PACKET_DOC, CLOSEOUT_DOC]:
        if not doc.exists():
            errors.append({"code": "missing_doc", "path": rel(doc)})
    report = {
        "schema_version": "dvf-3-3-required-artifact-disposition-validation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    name = "validation_report.require_complete.json" if require_complete else "validation_report.json"
    write_json(phase_path("phase5_fail_closed_validation", name), report)
    return report, not errors
