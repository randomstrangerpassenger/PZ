#!/usr/bin/env python3
"""Post-adoption governance closeout for Registry Runtime Compatibility."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from tools.build import dvf_3_3_registry_runtime_compatibility as rtc


FINAL_BINDING_FIELDS = (
    "pre_adoption_live_manifest_sha256",
    "post_adoption_live_manifest_sha256",
    "selected_durable_bundle_id",
    "selected_bundle_manifest_sha256",
    "adopted_row_identity",
)

CLOSEOUT_ROLE_FILES = {
    "post_adoption_current_route_result": "post_adoption_current_route_result.json",
    "live_gate_package_finalization_result": "live_gate_package_finalization_result.json",
    "final_machine_report": "final_machine_report.json",
    "independent_review": "independent_review_gate_report.json",
    "owner_canonical_seal": "owner_canonical_seal_gate_report.json",
    "final_compatibility_report": "final_registry_runtime_compatibility_report.json",
    "final_claim_scan_report": "final_claim_scan_report.json",
    "closeout_content_manifest": "closeout_content_manifest.json",
    "terminal_hash_seal": "terminal_hash_seal.json",
}

FIRST_SEVEN_ROLES = (
    "post_adoption_current_route_result",
    "live_gate_package_finalization_result",
    "final_machine_report",
    "independent_review",
    "owner_canonical_seal",
    "final_compatibility_report",
    "final_claim_scan_report",
)

NINE_PACKET_ROLES = (
    *FIRST_SEVEN_ROLES,
    "closeout_content_manifest",
    "terminal_hash_seal",
)


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise rtc.CompatibilityError(
            "closeout_json_invalid",
            f"Cannot read JSON {path}: {exc}",
        ) from exc
    if not isinstance(value, dict):
        raise rtc.CompatibilityError(
            "closeout_json_not_object",
            f"JSON root must be an object: {path}",
        )
    return value


def contained_repo_path(repo_root: Path, relative: str) -> Path:
    candidate = (repo_root / Path(relative)).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise rtc.CompatibilityError(
            "closeout_repository_path_escape",
            f"Path escapes repository: {relative}",
        ) from exc
    return candidate


def write_json_idempotent(path: Path, payload: dict[str, Any]) -> None:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"
    if path.exists():
        if path.read_bytes() != encoded:
            raise rtc.CompatibilityError(
                "closeout_write_once_conflict",
                f"Write-once artifact already differs: {path}",
            )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)


def load_bootstrap_module(repo_root: Path) -> Any:
    path = (
        repo_root
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "bootstrap"
        / "reserve_registry_runtime_compatibility_attempt.py"
    )
    spec = importlib.util.spec_from_file_location("rtc_bootstrap_for_closeout", path)
    if spec is None or spec.loader is None:
        raise rtc.CompatibilityError(
            "closeout_bootstrap_dependency_missing",
            f"Cannot load bootstrap module: {path}",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def event_ledger_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "attempt_events.jsonl"
    )


def lifecycle_ledger_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "bundle_lifecycle_events.jsonl"
    )


def durable_attempt_root(repo_root: Path, attempt_id: str) -> Path:
    return (
        repo_root
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "attempts"
        / attempt_id
    )


def require_open_attempt(repo_root: Path, attempt_id: str) -> tuple[Any, Any]:
    bootstrap = load_bootstrap_module(repo_root)
    state = bootstrap.replay_event_ledger(event_ledger_path(repo_root))
    if state.open_attempt_ids != (attempt_id,):
        raise rtc.CompatibilityError(
            "closeout_open_attempt_mismatch",
            f"Expected one open attempt {attempt_id}, got {state.open_attempt_ids}",
        )
    return bootstrap, state


def lifecycle_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous_hash = "0" * 64
    for sequence, raw_line in enumerate(path.read_bytes().splitlines(keepends=True), 1):
        if not raw_line.endswith(b"\n"):
            raise rtc.CompatibilityError(
                "closeout_lifecycle_truncated_line",
                f"Lifecycle event {sequence} lacks LF",
            )
        row = json.loads(raw_line.decode("utf-8"))
        if (
            row.get("event_sequence") != sequence
            or row.get("previous_event_sha256") != previous_hash
        ):
            raise rtc.CompatibilityError(
                "closeout_lifecycle_chain_invalid",
                f"Lifecycle chain differs at event {sequence}",
            )
        previous_hash = rtc.sha256_bytes(raw_line)
        rows.append(row)
    return rows


def selected_lifecycle_event(
    repo_root: Path,
    bundle_id: str,
) -> dict[str, Any]:
    selected = [
        row
        for row in lifecycle_rows(lifecycle_ledger_path(repo_root))
        if row.get("bundle_id") == bundle_id
    ]
    if (
        not selected
        or selected[-1].get("current_state") != "live_required_gate_adopted"
    ):
        raise rtc.CompatibilityError(
            "closeout_selected_bundle_not_live",
            f"Selected bundle is not live: {bundle_id}",
        )
    event = selected[-1]
    record_path = contained_repo_path(repo_root, str(event["record_path"]))
    if (
        not record_path.is_file()
        or rtc.sha256_file(record_path) != event.get("record_sha256")
    ):
        raise rtc.CompatibilityError(
            "closeout_lifecycle_record_invalid",
            f"Lifecycle record is missing or changed: {record_path}",
        )
    return event


def final_binding(payload: dict[str, Any]) -> dict[str, Any]:
    missing = [
        field for field in FINAL_BINDING_FIELDS if payload.get(field) in (None, "")
    ]
    if missing:
        raise rtc.CompatibilityError(
            "closeout_final_binding_incomplete",
            f"Final binding fields are missing: {missing}",
        )
    return {field: payload[field] for field in FINAL_BINDING_FIELDS}


def assert_same_final_binding(
    expected: dict[str, Any],
    observed: dict[str, Any],
    artifact: str,
) -> None:
    if final_binding(expected) != final_binding(observed):
        raise rtc.CompatibilityError(
            "closeout_final_binding_mismatch",
            f"{artifact} does not bind the final machine identity",
        )


def validate_toolchain_freshness(
    *,
    repo_root: Path,
    attempt_root: Path,
    output: Path,
) -> dict[str, Any]:
    manifest_path = attempt_root / "phase1" / "implementation_toolchain_manifest.json"
    manifest = read_json_object(manifest_path)
    rows = manifest.get("rows")
    if not isinstance(rows, list):
        raise rtc.CompatibilityError(
            "closeout_toolchain_manifest_invalid",
            "Implementation toolchain rows are missing",
        )
    drift: list[str] = []
    missing: list[str] = []
    untracked: list[str] = []
    ignored: list[str] = []
    for row in rows:
        relative = str(row.get("path", ""))
        path = contained_repo_path(repo_root, relative)
        if not path.is_file():
            missing.append(relative)
            continue
        if (
            path.stat().st_size != row.get("byte_count")
            or rtc.sha256_file(path) != row.get("sha256")
        ):
            drift.append(relative)
        if not rtc.git_tracked(repo_root, path):
            untracked.append(relative)
        if rtc.git_ignored(repo_root, [relative]):
            ignored.append(relative)
    report = {
        "schema_version": "rtc-implementation-toolchain-freshness-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": manifest.get("attempt_id"),
        "checkpoint": "before_final_machine_report",
        "status": (
            "PASS"
            if not drift and not missing and not untracked and not ignored
            else "FAIL"
        ),
        "implementation_toolchain_manifest_sha256": rtc.sha256_file(manifest_path),
        "implementation_toolchain_drift_count": len(drift),
        "implementation_toolchain_drift_paths": drift,
        "required_tool_missing_count": len(missing),
        "required_tool_missing": missing,
        "required_tool_untracked_count": len(untracked),
        "required_tool_untracked": untracked,
        "required_tool_ignored_count": len(ignored),
        "required_tool_ignored": ignored,
        "unclassified_tool_dependency_count": manifest.get(
            "unclassified_tool_dependency_count"
        ),
    }
    write_json_idempotent(output, report)
    if report["status"] != "PASS":
        raise rtc.CompatibilityError(
            "closeout_toolchain_freshness_failed",
            f"Implementation toolchain drifted: {report}",
        )
    return report


def prepare_final_machine(
    *,
    repo_root: Path,
    attempt_root: Path,
    attempt_id: str,
    implementation_identity: str,
) -> dict[str, Any]:
    if rtc.git_text(repo_root, "status", "--porcelain", "--untracked-files=no"):
        raise rtc.CompatibilityError(
            "closeout_final_machine_worktree_not_clean",
            "Final machine preparation requires no tracked changes",
        )
    _, state = require_open_attempt(repo_root, attempt_id)
    phase5 = attempt_root / "phase5"
    phase6 = attempt_root / "phase6"
    adoption_path = phase5 / "phase5_adoption_result.json"
    current_route_path = phase5 / "post_adoption_current_route_result.json"
    package_path = phase5 / "live_gate_package_finalization_result.json"
    gate_c_path = attempt_root / "phase0" / "production_integration_gate_report.json"
    phase4_path = attempt_root / "phase4" / "phase4_run_result.json"
    adoption = read_json_object(adoption_path)
    current_route = read_json_object(current_route_path)
    package = read_json_object(package_path)
    gate_c = read_json_object(gate_c_path)
    phase4 = read_json_object(phase4_path)
    predicates = gate_c.get("predicates")
    if (
        adoption.get("attempt_id") != attempt_id
        or adoption.get("status") != "PASS"
        or adoption.get("candidate_manifest_route_status") != "PASS"
        or adoption.get("official_current_route_status") != "PASS"
        or adoption.get("live_gate_package_status") != "PASS"
        or adoption.get("default_route_compatibility_status") != "PASS"
        or current_route.get("success") is not True
        or current_route.get("contract_class") != "current"
        or package.get("status") != "PASS"
        or gate_c.get("production_integration_allowed") is not True
        or not isinstance(predicates, dict)
        or predicates.get("invocation_inventory_unknown_count") != 0
        or predicates.get("invocation_migration_plan_unresolved_count") != 0
        or predicates.get("dirty_original_docs_consumed_as_authority_count") != 0
        or predicates.get("preintegration_tool_scope_violation_count") != 0
        or phase4.get("status") != "PASS"
    ):
        raise rtc.CompatibilityError(
            "closeout_machine_input_not_pass",
            "Phase 4/5 or Gate C evidence is not a complete machine PASS",
        )
    live_manifest_path = (
        repo_root
        / "Iris"
        / "_docs"
        / "round3"
        / "current_route_required_validations.json"
    )
    live_manifest = read_json_object(live_manifest_path)
    selection = live_manifest.get("registry_runtime_compatibility")
    if not isinstance(selection, dict):
        raise rtc.CompatibilityError(
            "closeout_live_selection_missing",
            "Live required manifest has no selected compatibility bundle",
        )
    binding = {
        "pre_adoption_live_manifest_sha256": adoption[
            "pre_adoption_live_manifest_sha256"
        ],
        "post_adoption_live_manifest_sha256": adoption[
            "post_adoption_live_manifest_sha256"
        ],
        "selected_durable_bundle_id": adoption["bundle_id"],
        "selected_bundle_manifest_sha256": adoption["bundle_manifest_sha256"],
        "adopted_row_identity": selection["adopted_row_identity"],
    }
    if (
        selection.get("bundle_id") != binding["selected_durable_bundle_id"]
        or selection.get("bundle_manifest_sha256")
        != binding["selected_bundle_manifest_sha256"]
        or rtc.sha256_file(live_manifest_path)
        != binding["post_adoption_live_manifest_sha256"]
    ):
        raise rtc.CompatibilityError(
            "closeout_live_binding_mismatch",
            "Live manifest and Phase 5 binding differ",
        )
    lifecycle = selected_lifecycle_event(
        repo_root,
        str(binding["selected_durable_bundle_id"]),
    )
    freshness_path = (
        phase6 / "implementation_toolchain_freshness_before_final_machine.json"
    )
    freshness = validate_toolchain_freshness(
        repo_root=repo_root,
        attempt_root=attempt_root,
        output=freshness_path,
    )
    report = {
        "schema_version": "rtc-final-machine-report-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "status": "PASS",
        "machine_contract_status": "PASS",
        "claim_scope": "machine_and_live_adoption_evidence_only",
        "compatibility_pass_claimed": False,
        "implementation_identity": implementation_identity,
        **binding,
        "phase5_adoption_result_path": rtc.normalized_relative(
            repo_root, adoption_path
        ),
        "phase5_adoption_result_sha256": rtc.sha256_file(adoption_path),
        "post_adoption_current_route_result_path": rtc.normalized_relative(
            repo_root, current_route_path
        ),
        "post_adoption_current_route_result_sha256": rtc.sha256_file(
            current_route_path
        ),
        "live_gate_package_finalization_result_path": rtc.normalized_relative(
            repo_root, package_path
        ),
        "live_gate_package_finalization_result_sha256": rtc.sha256_file(package_path),
        "implementation_toolchain_freshness_path": rtc.normalized_relative(
            repo_root, freshness_path
        ),
        "implementation_toolchain_freshness_sha256": rtc.sha256_file(
            freshness_path
        ),
        "implementation_toolchain_drift_count": freshness[
            "implementation_toolchain_drift_count"
        ],
        "gate_c_report_path": rtc.normalized_relative(repo_root, gate_c_path),
        "gate_c_report_sha256": rtc.sha256_file(gate_c_path),
        "invocation_inventory_unknown_count": 0,
        "invocation_migration_plan_unresolved_count": 0,
        "dirty_original_docs_consumed_as_authority_count": 0,
        "preintegration_tool_scope_violation_count": 0,
        "source_rendered_runtime_package_exact_keyset_match": package[
            "source_rendered_runtime_package_exact_keyset_match"
        ],
        "surface_exact_key_counts": package["surface_exact_key_counts"],
        "exact_duplicate_count": package["exact_duplicate_count"],
        "unauthorized_collision_count": package["unauthorized_collision_count"],
        "collision_group_payload_mismatch_count": package[
            "collision_group_payload_mismatch_count"
        ],
        "runtime_projection_payload_mismatch_count": package[
            "runtime_projection_payload_mismatch_count"
        ],
        "applied_new_alias_key_count": package["applied_new_alias_key_count"],
        "unexpected_emission_count": package["unexpected_emission_count"],
        "alias_induced_comparison_collision_increase": package[
            "alias_induced_comparison_collision_increase"
        ],
        "active_core_closure_mutation_count": adoption[
            "active_core_closure_mutation_count"
        ],
        "selected_lifecycle_event_path": lifecycle["record_path"],
        "selected_lifecycle_event_sha256": lifecycle["record_sha256"],
        "attempt_event_prefix_sha256": state.prefix_sha256,
        "independent_review_status": "pending",
        "owner_canonical_seal_status": "pending",
        "closeout_state": "compatibility_machine_pass_governance_pending",
    }
    output = phase6 / "final_machine_report.json"
    write_json_idempotent(output, report)
    return report


def independent_review_required_artifacts(
    *,
    repo_root: Path,
    attempt_root: Path,
    final_machine_path: Path,
    runner_path: Path,
    validator_path: Path,
) -> dict[str, str]:
    live_manifest_path = (
        repo_root
        / "Iris"
        / "_docs"
        / "round3"
        / "current_route_required_validations.json"
    )
    live_manifest = read_json_object(live_manifest_path)
    selection = live_manifest["registry_runtime_compatibility"]
    bundle_root = contained_repo_path(repo_root, str(selection["bundle_root"]))
    paths = (
        final_machine_path,
        attempt_root / "phase5" / "phase5_adoption_result.json",
        runner_path,
        validator_path,
        Path(__file__).resolve(),
        live_manifest_path,
        bundle_root / "durable_bundle_manifest.json",
    )
    return {
        rtc.normalized_relative(repo_root, path): rtc.sha256_file(path)
        for path in paths
    }


def validate_independent_review_payload(
    *,
    review: dict[str, Any],
    final_machine: dict[str, Any],
    required_artifacts: dict[str, str],
) -> dict[str, Any]:
    eligibility = review.get("eligibility")
    artifacts = review.get("artifacts_reviewed")
    reruns = review.get("rerun_commands")
    if (
        review.get("schema_version") != "rtc-independent-review-v1"
        or review.get("round_id") != rtc.ROUND_ID
        or review.get("attempt_id") != final_machine.get("attempt_id")
        or review.get("status") != "PASS"
        or review.get("verdict") != "PASS"
        or not isinstance(eligibility, dict)
        or not isinstance(artifacts, list)
        or not isinstance(reruns, list)
        or not reruns
    ):
        raise rtc.CompatibilityError(
            "closeout_independent_review_invalid",
            "Independent review schema, verdict, or reruns are incomplete",
        )
    required_eligibility = (
        "not_roadmap_author",
        "not_plan_author_or_coauthor",
        "not_implementation_author_or_coauthor",
        "not_owner_or_disposition_signer",
        "distinct_agent_and_session_identity",
    )
    if any(eligibility.get(field) is not True for field in required_eligibility):
        raise rtc.CompatibilityError(
            "closeout_independent_reviewer_ineligible",
            "Independent reviewer eligibility predicates are not all true",
        )
    if (
        review.get("reviewer_identity") in (None, "")
        or review.get("reviewer_identity")
        == final_machine.get("implementation_identity")
        or review.get("same_implementation_agent_or_session_identity") is not False
    ):
        raise rtc.CompatibilityError(
            "closeout_independent_reviewer_identity_conflict",
            "Reviewer identity is not independent",
        )
    if (
        review.get("open_critical_finding_count") != 0
        or review.get("open_major_finding_count") != 0
        or review.get("unresolved_finding_count") != 0
    ):
        raise rtc.CompatibilityError(
            "closeout_independent_review_open_findings",
            "Independent review has unresolved findings",
        )
    observed = {
        str(row.get("path", "")): str(row.get("sha256", ""))
        for row in artifacts
        if isinstance(row, dict)
    }
    missing = {
        path: sha
        for path, sha in required_artifacts.items()
        if observed.get(path) != sha
    }
    if missing:
        raise rtc.CompatibilityError(
            "closeout_independent_review_coverage_incomplete",
            f"Review did not bind required artifacts: {missing}",
        )
    if any(
        not isinstance(row, dict)
        or row.get("exit_code") != 0
        or row.get("status") != "PASS"
        or not row.get("command")
        for row in reruns
    ):
        raise rtc.CompatibilityError(
            "closeout_independent_review_rerun_failed",
            "Independent review rerun evidence is incomplete or failed",
        )
    assert_same_final_binding(final_machine, review, "independent review")
    return review


def validate_independent_review(
    *,
    repo_root: Path,
    attempt_root: Path,
    attempt_id: str,
    review_path: Path,
    runner_path: Path,
    validator_path: Path,
) -> dict[str, Any]:
    phase6 = attempt_root / "phase6"
    expected_path = (phase6 / "independent_review_gate_report.json").resolve()
    if review_path.resolve() != expected_path:
        raise rtc.CompatibilityError(
            "closeout_independent_review_path_invalid",
            "Review must use the attempt-local write-once path",
        )
    final_path = phase6 / "final_machine_report.json"
    final_machine = read_json_object(final_path)
    review = read_json_object(review_path)
    validate_independent_review_payload(
        review=review,
        final_machine=final_machine,
        required_artifacts=independent_review_required_artifacts(
            repo_root=repo_root,
            attempt_root=attempt_root,
            final_machine_path=final_path,
            runner_path=runner_path,
            validator_path=validator_path,
        ),
    )
    receipt = {
        "schema_version": "rtc-independent-review-validation-receipt-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "status": "PASS",
        "review_path": rtc.normalized_relative(repo_root, review_path),
        "review_sha256": rtc.sha256_file(review_path),
        "reviewer_identity": review["reviewer_identity"],
        "verdict": review["verdict"],
        **final_binding(final_machine),
    }
    write_json_idempotent(
        phase6 / "independent_review_validation_receipt.json",
        receipt,
    )
    return receipt


def validate_owner_seal_payload(
    *,
    repo_root: Path,
    owner_seal: dict[str, Any],
    final_machine: dict[str, Any],
    final_machine_path: Path,
    independent_review_path: Path,
) -> dict[str, Any]:
    if (
        owner_seal.get("schema_version") != "rtc-owner-canonical-seal-v1"
        or owner_seal.get("round_id") != rtc.ROUND_ID
        or owner_seal.get("attempt_id") != final_machine.get("attempt_id")
        or owner_seal.get("owner_identity") in (None, "")
        or owner_seal.get("owner_explicitly_approved") is not True
        or owner_seal.get("owner_seal_status") != "PASS"
        or owner_seal.get("canonical_seal_status") != "PASS"
        or owner_seal.get("final_signoff_status") != "PASS"
        or owner_seal.get("owner_is_independent_reviewer") is not False
    ):
        raise rtc.CompatibilityError(
            "closeout_owner_seal_invalid",
            "Owner seal is incomplete or does not explicitly approve",
        )
    if (
        owner_seal.get("final_machine_report_path")
        != rtc.normalized_relative(repo_root, final_machine_path)
        or owner_seal.get("final_machine_report_sha256")
        != rtc.sha256_file(final_machine_path)
        or owner_seal.get("independent_review_path")
        != rtc.normalized_relative(repo_root, independent_review_path)
        or owner_seal.get("independent_review_sha256")
        != rtc.sha256_file(independent_review_path)
    ):
        raise rtc.CompatibilityError(
            "closeout_owner_seal_binding_mismatch",
            "Owner seal does not bind exact machine and review bytes",
        )
    assert_same_final_binding(final_machine, owner_seal, "owner seal")
    return owner_seal


def closeout_role_row(root: Path, role: str, path: Path) -> dict[str, Any]:
    return {
        "role": role,
        "path": path.relative_to(root).as_posix(),
        "schema_version": read_json_object(path).get("schema_version"),
        "byte_count": path.stat().st_size,
        "sha256": rtc.sha256_file(path),
    }


def build_closeout_staging(
    *,
    repo_root: Path,
    attempt_root: Path,
    attempt_id: str,
    final_machine_path: Path,
    independent_review_path: Path,
    owner_seal_path: Path,
    state: Any,
) -> Path:
    phase5 = attempt_root / "phase5"
    staging = attempt_root / "closeout-staging"
    if staging.exists():
        raise rtc.CompatibilityError(
            "closeout_staging_exists",
            "Closeout staging already exists; inspect it before retrying",
        )
    staging.mkdir(parents=True)
    final_machine = read_json_object(final_machine_path)
    binding = final_binding(final_machine)
    sources = {
        "post_adoption_current_route_result": phase5
        / "post_adoption_current_route_result.json",
        "live_gate_package_finalization_result": phase5
        / "live_gate_package_finalization_result.json",
        "final_machine_report": final_machine_path,
        "independent_review": independent_review_path,
        "owner_canonical_seal": owner_seal_path,
    }
    for role, source in sources.items():
        shutil.copyfile(source, staging / CLOSEOUT_ROLE_FILES[role])
    final_report = {
        "schema_version": "rtc-final-compatibility-report-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "status": "PASS",
        "machine_contract_status": "PASS",
        "independent_review_status": "PASS",
        "owner_seal_status": "PASS",
        "formal_claim": "Registry Runtime Compatibility PASS",
        "closeout_state": "registry_runtime_compatibility_canonical_complete",
        **binding,
        "final_machine_report_sha256": rtc.sha256_file(final_machine_path),
        "independent_review_sha256": rtc.sha256_file(independent_review_path),
        "owner_canonical_seal_sha256": rtc.sha256_file(owner_seal_path),
    }
    write_json_idempotent(
        staging / CLOSEOUT_ROLE_FILES["final_compatibility_report"],
        final_report,
    )
    claim_scan = {
        "schema_version": "rtc-final-claim-scan-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "status": "PASS",
        "formal_claim_count": 1,
        "exact_axis_qualified_claim_count": 1,
        "bare_pass_claim_count": 0,
        "bare_runtime_compatibility_claim_count": 0,
        "claim": final_report["formal_claim"],
        **binding,
    }
    write_json_idempotent(
        staging / CLOSEOUT_ROLE_FILES["final_claim_scan_report"],
        claim_scan,
    )
    content_manifest = {
        "schema_version": "rtc-closeout-content-manifest-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "role_count": 7,
        "rows": [
            closeout_role_row(
                staging,
                role,
                staging / CLOSEOUT_ROLE_FILES[role],
            )
            for role in FIRST_SEVEN_ROLES
        ],
        **binding,
    }
    content_path = staging / CLOSEOUT_ROLE_FILES["closeout_content_manifest"]
    write_json_idempotent(content_path, content_manifest)
    lifecycle = selected_lifecycle_event(
        repo_root,
        str(binding["selected_durable_bundle_id"]),
    )
    reservation_path = durable_attempt_root(repo_root, attempt_id) / "reservation_record.json"
    terminal_seal = {
        "schema_version": "rtc-terminal-hash-seal-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "status": "PASS",
        "closeout_content_manifest_sha256": rtc.sha256_file(content_path),
        "selected_lifecycle_event_path": lifecycle["record_path"],
        "selected_lifecycle_event_sha256": lifecycle["record_sha256"],
        "reservation_record_path": rtc.normalized_relative(
            repo_root, reservation_path
        ),
        "reservation_record_sha256": rtc.sha256_file(reservation_path),
        "attempt_event_prefix_sha256": state.prefix_sha256,
        **binding,
    }
    write_json_idempotent(
        staging / CLOSEOUT_ROLE_FILES["terminal_hash_seal"],
        terminal_seal,
    )
    packet = {
        "schema_version": "rtc-durable-closeout-packet-manifest-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "status": "PASS",
        "required_role_count": 9,
        "rows": [
            closeout_role_row(
                staging,
                role,
                staging / CLOSEOUT_ROLE_FILES[role],
            )
            for role in NINE_PACKET_ROLES
        ],
        "artifact_missing_count": 0,
        "hash_mismatch_count": 0,
        **binding,
    }
    write_json_idempotent(
        staging / "durable_closeout_packet_manifest.json",
        packet,
    )
    return staging


def commit_closeout_packet(
    *,
    repo_root: Path,
    attempt_root: Path,
    attempt_id: str,
    staging: Path,
) -> tuple[Path, Path, str]:
    bootstrap = load_bootstrap_module(repo_root)
    durable_attempt = durable_attempt_root(repo_root, attempt_id)
    durable_closeout = durable_attempt / "closeout"
    if durable_closeout.exists():
        raise rtc.CompatibilityError(
            "closeout_destination_exists",
            "Durable closeout destination already exists",
        )
    staging.replace(durable_closeout)
    packet_path = durable_closeout / "durable_closeout_packet_manifest.json"
    packet = read_json_object(packet_path)
    if (
        packet.get("required_role_count") != 9
        or packet.get("artifact_missing_count") != 0
        or packet.get("hash_mismatch_count") != 0
    ):
        raise rtc.CompatibilityError(
            "closeout_packet_invalid",
            "Durable closeout packet role contract is incomplete",
        )
    evidence_path = durable_attempt / "evidence_manifest.json"
    evidence = {
        "schema_version": "rtc-attempt-evidence-manifest-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "terminal_state": "registry_runtime_compatibility_canonical_complete",
        "local_supporting_evidence_available": True,
        "durable_closeout_path": rtc.normalized_relative(
            repo_root, durable_closeout
        ),
        "durable_closeout_packet_manifest_sha256": rtc.sha256_file(packet_path),
        "claim_scope": "registry_runtime_compatibility_canonical_complete",
        **final_binding(packet),
    }
    bootstrap.exclusive_write(
        evidence_path,
        rtc.canonical_json_bytes(evidence),
    )
    stage_paths = [
        rtc.normalized_relative(repo_root, durable_closeout),
        rtc.normalized_relative(repo_root, evidence_path),
    ]
    rtc.run_git(repo_root, "add", "--", *stage_paths)
    expected = {
        rtc.normalized_relative(repo_root, path)
        for path in durable_closeout.rglob("*")
        if path.is_file()
    }
    expected.add(rtc.normalized_relative(repo_root, evidence_path))
    staged = set(
        rtc.git_text(repo_root, "diff", "--cached", "--name-only").splitlines()
    )
    if staged != expected:
        raise rtc.CompatibilityError(
            "closeout_stage_scope_violation",
            f"Unexpected closeout staged paths: {sorted(staged)}",
        )
    rtc.run_git(
        repo_root,
        "commit",
        "-m",
        f"chore(rtc): publish {attempt_id} durable closeout",
    )
    return packet_path, evidence_path, rtc.git_text(repo_root, "rev-parse", "HEAD")


def append_success_terminal(
    *,
    repo_root: Path,
    attempt_root: Path,
    attempt_id: str,
    packet_path: Path,
    evidence_path: Path,
    closeout_commit: str,
) -> dict[str, Any]:
    bootstrap = load_bootstrap_module(repo_root)
    common_dir = Path(
        rtc.git_text(
            repo_root,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        )
    ).resolve()
    coordination_key = rtc.sha256_bytes(str(common_dir).lower().encode("utf-8"))[:24]
    mutex_name = f"IrisRegistryRuntimeCompatibility-{coordination_key}"
    durable_attempt = durable_attempt_root(repo_root, attempt_id)
    ledger = event_ledger_path(repo_root)
    with bootstrap.NamedMutex(mutex_name, timeout_seconds=60):
        if rtc.git_text(repo_root, "status", "--porcelain"):
            raise rtc.CompatibilityError(
                "closeout_terminal_worktree_not_clean",
                "Success terminal requires a clean worktree",
            )
        if rtc.git_text(repo_root, "rev-parse", "HEAD") != closeout_commit:
            raise rtc.CompatibilityError(
                "closeout_commit_not_branch_tip",
                "Closeout commit must be branch tip before terminal append",
            )
        state = bootstrap.replay_event_ledger(ledger)
        if state.open_attempt_ids != (attempt_id,):
            raise rtc.CompatibilityError(
                "closeout_terminal_open_attempt_mismatch",
                f"Expected open attempt {attempt_id}, got {state.open_attempt_ids}",
            )
        packet = read_json_object(packet_path)
        binding = final_binding(packet)
        lifecycle = selected_lifecycle_event(
            repo_root,
            str(binding["selected_durable_bundle_id"]),
        )
        terminal_seal_path = (
            packet_path.parent / CLOSEOUT_ROLE_FILES["terminal_hash_seal"]
        )
        terminal_path = durable_attempt / "terminal_record.json"
        terminal = {
            "schema_version": "rtc-attempt-terminal-v1",
            "round_id": rtc.ROUND_ID,
            "attempt_id": attempt_id,
            "event_type": "terminal",
            "terminal_state": "registry_runtime_compatibility_canonical_complete",
            "compatibility_pass_claimed": True,
            "formal_claim": "Registry Runtime Compatibility PASS",
            "durable_closeout_packet_commit": closeout_commit,
            "durable_closeout_packet_manifest_path": rtc.normalized_relative(
                repo_root, packet_path
            ),
            "durable_closeout_packet_manifest_sha256": rtc.sha256_file(packet_path),
            "terminal_hash_seal_path": rtc.normalized_relative(
                repo_root, terminal_seal_path
            ),
            "terminal_hash_seal_sha256": rtc.sha256_file(terminal_seal_path),
            "evidence_manifest_path": rtc.normalized_relative(
                repo_root, evidence_path
            ),
            "evidence_manifest_sha256": rtc.sha256_file(evidence_path),
            "selected_lifecycle_event_path": lifecycle["record_path"],
            "selected_lifecycle_event_sha256": lifecycle["record_sha256"],
            "previous_event_prefix_sha256": state.prefix_sha256,
            **binding,
        }
        bootstrap.exclusive_write(
            terminal_path,
            rtc.canonical_json_bytes(terminal),
        )
        event = {
            "schema_version": "rtc-attempt-event-v1",
            "event_sequence": state.event_count + 1,
            "round_id": rtc.ROUND_ID,
            "attempt_id": attempt_id,
            "event_type": "terminal",
            "terminal_state": "registry_runtime_compatibility_canonical_complete",
            "record_path": rtc.normalized_relative(repo_root, terminal_path),
            "record_sha256": rtc.sha256_file(terminal_path),
            "durable_closeout_packet_commit": closeout_commit,
            "previous_event_sha256": state.last_event_sha256,
            "previous_event_prefix_sha256": state.prefix_sha256,
        }
        bootstrap.append_durable(ledger, rtc.canonical_json_bytes(event))
        post_state = bootstrap.replay_event_ledger(ledger)
        if post_state.open_attempt_ids:
            raise rtc.CompatibilityError(
                "closeout_terminal_left_open_attempt",
                f"Open attempts remain: {post_state.open_attempt_ids}",
            )
        stage_paths = [
            rtc.normalized_relative(repo_root, terminal_path),
            rtc.normalized_relative(repo_root, ledger),
        ]
        rtc.run_git(repo_root, "add", "--", *stage_paths)
        staged = set(
            rtc.git_text(repo_root, "diff", "--cached", "--name-only").splitlines()
        )
        if staged != set(stage_paths):
            raise rtc.CompatibilityError(
                "closeout_terminal_stage_scope_violation",
                f"Unexpected terminal staged paths: {sorted(staged)}",
            )
        rtc.run_git(
            repo_root,
            "commit",
            "-m",
            f"chore(rtc): terminal {attempt_id} canonical complete",
        )
        terminal_commit = rtc.git_text(repo_root, "rev-parse", "HEAD")
        bootstrap.append_durable(
            bootstrap.shared_ledger_path(repo_root),
            rtc.canonical_json_bytes(
                {
                    "schema_version": "rtc-shared-terminal-v1",
                    "round_id": rtc.ROUND_ID,
                    "attempt_id": attempt_id,
                    "terminal_state": "registry_runtime_compatibility_canonical_complete",
                    "terminal_commit": terminal_commit,
                    "committed_event_prefix_sha256": post_state.prefix_sha256,
                    "event_record_sha256": rtc.sha256_file(terminal_path),
                }
            ),
        )
    receipt = {
        "schema_version": "rtc-closeout-terminal-receipt-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "status": "PASS",
        "closeout_commit": closeout_commit,
        "terminal_commit": terminal_commit,
        "event_prefix_after_sha256": post_state.prefix_sha256,
        "post_terminal_open_attempt_ids": [],
        **binding,
    }
    write_json_idempotent(
        attempt_root / "closeout_terminal_receipt.json",
        receipt,
    )
    return receipt


def finalize_closeout(
    *,
    repo_root: Path,
    attempt_root: Path,
    attempt_id: str,
    independent_review_path: Path,
    owner_seal_path: Path,
    runner_path: Path,
    validator_path: Path,
) -> dict[str, Any]:
    if rtc.git_text(repo_root, "status", "--porcelain", "--untracked-files=no"):
        raise rtc.CompatibilityError(
            "closeout_worktree_not_clean",
            "Closeout requires no tracked worktree changes",
        )
    phase6 = attempt_root / "phase6"
    final_machine_path = phase6 / "final_machine_report.json"
    final_machine = read_json_object(final_machine_path)
    validate_independent_review(
        repo_root=repo_root,
        attempt_root=attempt_root,
        attempt_id=attempt_id,
        review_path=independent_review_path,
        runner_path=runner_path,
        validator_path=validator_path,
    )
    review = read_json_object(independent_review_path)
    owner_seal = read_json_object(owner_seal_path)
    validate_owner_seal_payload(
        repo_root=repo_root,
        owner_seal=owner_seal,
        final_machine=final_machine,
        final_machine_path=final_machine_path,
        independent_review_path=independent_review_path,
    )
    _, state = require_open_attempt(repo_root, attempt_id)
    staging = build_closeout_staging(
        repo_root=repo_root,
        attempt_root=attempt_root,
        attempt_id=attempt_id,
        final_machine_path=final_machine_path,
        independent_review_path=independent_review_path,
        owner_seal_path=owner_seal_path,
        state=state,
    )
    packet_path, evidence_path, closeout_commit = commit_closeout_packet(
        repo_root=repo_root,
        attempt_root=attempt_root,
        attempt_id=attempt_id,
        staging=staging,
    )
    return append_success_terminal(
        repo_root=repo_root,
        attempt_root=attempt_root,
        attempt_id=attempt_id,
        packet_path=packet_path,
        evidence_path=evidence_path,
        closeout_commit=closeout_commit,
    )


def required_review_artifact_rows(
    *,
    repo_root: Path,
    attempt_root: Path,
    runner_path: Path,
    validator_path: Path,
) -> list[dict[str, str]]:
    final_path = attempt_root / "phase6" / "final_machine_report.json"
    return [
        {"path": path, "sha256": sha}
        for path, sha in sorted(
            independent_review_required_artifacts(
                repo_root=repo_root,
                attempt_root=attempt_root,
                final_machine_path=final_path,
                runner_path=runner_path,
                validator_path=validator_path,
            ).items()
        )
    ]
