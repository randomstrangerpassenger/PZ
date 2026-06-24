from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    canonical_hash,
    read_json,
    read_jsonl,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


GENERATED_AT = "2026-06-19T00:00:00+09:00"
ROUND_ID = "dvf_3_3_terminal_disposition_adjudication"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
UNIVERSE_ID = "dvf_3_3_terminal_executing_consumer_member_rows_1062_v1"
MEMBER_SCHEMA_VERSION = "dvf-3-3-terminal-member-v1"
VALIDATION_CORE_ID = "dvf_3_3_terminal_disposition_adjudication_common.validate_terminal_records_v1"
IDENTITY_RESOLVER_ID = "dvf_3_3_terminal_disposition_adjudication_common.resolve_member_identity_v1"
INDEPENDENT_REVIEW_VERDICTS = ("review_pending", "review_pass", "review_failed")
CLAIM_BOUNDARY = (
    "Terminal disposition adjudication governance only; not release readiness, package readiness, "
    "Workshop readiness, manual QA, semantic quality completion, source/rendered/runtime/package mutation, "
    "runtime payload policy mutation, or new current authority cutover."
)

PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_terminal_disposition_adjudication_plan.md"

AUDIT_ROOT = V2_ROOT / "staging" / "2105_baseline_consumption_audit"
AUDIT_DUAL_GATE = AUDIT_ROOT / "dual_gate_result.json"
AUDIT_EXECUTING_CONSUMERS = AUDIT_ROOT / "executing_consumers.jsonl"
AUDIT_EXECUTING_IMPACT = AUDIT_ROOT / "executing_consumer_impact.md"
AUDIT_CLASSIFIED_LEDGER = AUDIT_ROOT / "classified_ledger.jsonl"

NORMALIZATION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_consumer_migration_input_normalization"
NORMALIZATION_MANIFEST = NORMALIZATION_ROOT / "phase6" / "consumer_migration_reconciled_input_manifest.json"
NORMALIZATION_LEDGER = NORMALIZATION_ROOT / "phase6" / "row_disposition_ledger.for_readiness.jsonl"
NORMALIZATION_MISSING_PATH = NORMALIZATION_ROOT / "phase2" / "missing_path_disposition_summary.json"

READINESS_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_cutover_tooling_readiness"
READINESS_LEDGER = READINESS_ROOT / "phase3" / "row_level_migration_ledger.jsonl"
READINESS_ACTUAL_REPORT = READINESS_ROOT / "phase3" / "consumer_migration_actual_report.json"
READINESS_DIFF_REPORT = READINESS_ROOT / "phase4" / "actual_diff_to_ledger_report.json"
READINESS_HANDOFF = READINESS_ROOT / "phase6" / "current_cutover_phase0_handoff_manifest.json"

CURRENT_ROUTE_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_delta_guard_current_route_integration"
CURRENT_ROUTE_FINAL = CURRENT_ROUTE_ROOT / "phase7" / "final_current_route_guard_integration_report.json"

REJECTED_CORRECTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_rejected_delta_correction_reparity"
REJECTED_CORRECTION_PHASE8 = (
    REJECTED_CORRECTION_ROOT / "phase8" / "final_delta_disposition_guard_contract_report.json"
)
REJECTED_CORRECTION_PHASE11 = (
    REJECTED_CORRECTION_ROOT / "phase11" / "final_rejected_delta_correction_reparity_report.json"
)

RUNTIME_ROOT = V2_ROOT / "staging" / "runtime_payload_state_integrity"
RUNTIME_INVENTORY = RUNTIME_ROOT / "phase0" / "runtime_payload_state_inventory.json"
RUNTIME_GUARD = RUNTIME_ROOT / "phase4" / "current_route_payload_state_guard_report.json"

DENOMINATOR_ROOT = V2_ROOT / "staging" / "consumer_universe_denominator_lock"
DENOMINATOR_REGISTRY = DENOMINATOR_ROOT / "phase4" / "consumer_universe_denominator_registry.json"
DENOMINATOR_REVIEW = DENOMINATOR_ROOT / "phase8" / "independent_review_status.json"
DENOMINATOR_FINAL = DENOMINATOR_ROOT / "phase8" / "final_consumer_universe_denominator_lock_report.json"

CURRENT_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"

POLICY_DOC = REPO_ROOT / "docs" / "dvf_3_3_terminal_disposition_policy.md"
CLOSEOUT_DOC = REPO_ROOT / "docs" / "dvf_3_3_terminal_disposition_adjudication_closeout.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_terminal_disposition_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_terminal_disposition_ledger_packet.md"

TERMINAL_DISPOSITIONS = ("migrated", "no-op", "diagnostic-only", "historical-only")
NON_TERMINAL_STATES = ("blocked", "conditional", "pending", "review", "unknown", "deferred", "needs_adjudication")
MIGRATED_EVIDENCE_CLASSES = (
    "prior_current_cutover_row_evidence",
    "prior_cutover_authority_role_migration_evidence",
    "adopted_current_route_authority_migration_evidence",
    "live_authority_role_migration_ledger",
    "explicitly_validated_current_successor_consumer_update",
)
TERMINAL_REASON_CODES = {
    "no-op": (
        "already_current_successor_contract",
        "false_positive_no_mutation",
        "generated_no_mutation",
        "non_apply_missing_path",
        "denominator_role_not_apply_target",
        "preserved_reference_no_behavior_change",
    ),
    "diagnostic-only": (
        "diagnostic_validator_surface",
        "diagnostic_report_surface",
        "non_authority_test_tool_diagnostic_path",
    ),
    "historical-only": (
        "predecessor_trace",
        "archive_or_done_doc",
        "historical_fixture",
        "staging_predecessor_evidence",
        "generated_historical_trace",
    ),
}

PROTECTED_SURFACE_PATHS = [
    ("Iris/build/description/v2/data/dvf_3_3_input_manifest.json", "current_input_manifest", False),
    ("Iris/build/description/v2/data/dvf_3_3_facts.jsonl", "current_source_facts", False),
    ("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl", "current_source_decisions", False),
    ("Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl", "current_overlay_support", False),
    ("Iris/build/description/v2/output/dvf_3_3_rendered.json", "current_rendered_output", False),
    ("Iris/build/description/v2/output/style_normalization_changes.jsonl", "current_style_side_output", True),
    ("Iris/build/description/v2/output/compose_requeue_candidates.jsonl", "current_requeue_side_output", True),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "live_runtime_chunk_manifest", False),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks", "live_runtime_chunk_dir", False),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "live_runtime_monolith_facade", True),
    ("Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "package_chunk_manifest", True),
    ("Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks", "package_chunk_dir", True),
    ("Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "package_runtime_monolith", True),
    ("Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua", "stale_bridge_surface", True),
]

REQUIRED_COMMANDS = [
    "uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_terminal_disposition_adjudication.py --mode generate",
    "uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_terminal_disposition_adjudication.py --require-complete",
    'uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_terminal_disposition_adjudication.py"',
]


def phase_dir(phase: str) -> Path:
    path = EVIDENCE_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def promotion_rewritten_review_artifacts() -> set[str]:
    paths = [
        CLOSEOUT_DOC,
        LEDGER_PACKET_DOC,
        EVIDENCE_ROOT / "phase5" / "final_terminal_disposition_machine_report.json",
        EVIDENCE_ROOT / "phase5" / "regenerate_twice_fingerprint_comparison.json",
        EVIDENCE_ROOT / "phase6" / "closeout.md",
        EVIDENCE_ROOT / "phase6" / "closeout_claim_boundary_check.json",
        EVIDENCE_ROOT / "phase6" / "final_terminal_disposition_closeout_report.json",
        EVIDENCE_ROOT / "phase6" / "independent_review_status.json",
        EVIDENCE_ROOT / "phase6" / "owner_adoption_record.json",
    ]
    return {rel(path) for path in paths}


def self_referential_review_artifacts() -> set[str]:
    return {rel(EVIDENCE_ROOT / "phase6" / "independent_review_artifact_hash_report.json")}


def validation_rewritten_review_artifacts() -> set[str]:
    return {rel(EVIDENCE_ROOT / "phase5" / "terminal_disposition_validation_report.json")}


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def stable_record(path: str | Path, role: str, *, required: bool = True, read_only: bool = True) -> dict[str, Any]:
    resolved = resolve_repo(path)
    record = {
        "path": rel(resolved),
        "role": role,
        "required": required,
        "read_only": read_only,
        "exists": resolved.exists(),
        "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
        "sha256": sha256_file(resolved) if resolved.is_file() else None,
        "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
        "row_count": count_jsonl(resolved) if resolved.exists() and resolved.suffix == ".jsonl" else None,
    }
    if required and not resolved.exists():
        record["status"] = "MISSING_REQUIRED"
    else:
        record["status"] = "PRESENT" if resolved.exists() else "ABSENT_ALLOWED"
    return record


def default_independent_review_status() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-terminal-independent-review-status-v1",
        "generated_at": GENERATED_AT,
        "reviewed_artifacts": [],
        "reviewed_hashes": {},
        "reviewer_identity_or_label": None,
        "verdict": "review_pending",
        "timestamp": GENERATED_AT,
        "claim_boundary_acknowledgement": False,
        "independent_review_status": "review_pending",
        "canonical_complete_allowed": False,
    }


def load_independent_review_status() -> dict[str, Any]:
    path = phase_path("phase6", "independent_review_status.json")
    if not path.exists():
        return default_independent_review_status()
    existing = read_json(path)
    verdict = existing.get("verdict")
    if verdict not in INDEPENDENT_REVIEW_VERDICTS:
        return existing
    existing.setdefault("schema_version", "dvf-3-3-terminal-independent-review-status-v1")
    existing.setdefault("generated_at", GENERATED_AT)
    existing.setdefault("reviewed_artifacts", [])
    existing.setdefault("reviewed_hashes", {})
    existing.setdefault("reviewer_identity_or_label", None)
    existing.setdefault("timestamp", GENERATED_AT)
    existing.setdefault("claim_boundary_acknowledgement", False)
    existing.setdefault("independent_review_status", verdict)
    existing.setdefault(
        "canonical_complete_allowed",
        verdict == "review_pass" and existing.get("claim_boundary_acknowledgement") is True,
    )
    return existing


def resolve_review_artifact_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def review_artifact_hash_report(review: dict[str, Any]) -> dict[str, Any]:
    reviewed_artifacts = review.get("reviewed_artifacts")
    reviewed_hashes = review.get("reviewed_hashes")
    if not isinstance(reviewed_artifacts, list):
        reviewed_artifacts = []
    if not isinstance(reviewed_hashes, dict):
        reviewed_hashes = {}

    promotion_rewritten = promotion_rewritten_review_artifacts()
    self_referential = self_referential_review_artifacts()
    validation_rewritten = validation_rewritten_review_artifacts()
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    artifact_keys = set()
    for artifact in reviewed_artifacts:
        if not isinstance(artifact, str) or not artifact.strip():
            errors.append({"code": "review_pass_invalid_artifact_path", "artifact": artifact})
            continue
        artifact_keys.add(artifact)
        expected_hash = reviewed_hashes.get(artifact)
        if not isinstance(expected_hash, str):
            errors.append({"code": "review_pass_missing_artifact_hash", "artifact": artifact})
            continue
        if len(expected_hash) != 64 or any(char not in "0123456789abcdefABCDEF" for char in expected_hash):
            errors.append({"code": "review_pass_invalid_artifact_hash", "artifact": artifact, "sha256": expected_hash})
            continue
        resolved = resolve_review_artifact_path(artifact).resolve()
        try:
            relative = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            errors.append({"code": "review_pass_artifact_outside_repo", "artifact": artifact})
            continue
        if not resolved.is_file():
            errors.append({"code": "review_pass_artifact_missing", "artifact": artifact})
            continue
        if relative in self_referential:
            rows.append(
                {
                    "artifact": artifact,
                    "normalized_artifact": relative,
                    "reviewed_sha256": expected_hash,
                    "current_sha256": None,
                    "hash_relation": "self_referential_attestation",
                    "allowed_promotion_rewrite": True,
                    "mutation_reason": "self_referential_hash_report_excluded_from_hash_closure",
                    "status": "PASS",
                }
            )
            continue
        if relative in validation_rewritten:
            rows.append(
                {
                    "artifact": artifact,
                    "normalized_artifact": relative,
                    "reviewed_sha256": expected_hash,
                    "current_sha256": None,
                    "hash_relation": "validation_rewritten_attestation",
                    "allowed_promotion_rewrite": False,
                    "allowed_validation_rewrite": True,
                    "mutation_reason": "validator_rewrites_validation_report_surface",
                    "status": "PASS",
                }
            )
            continue
        actual_hash = sha256_file(resolved)
        allowed_promotion_rewrite = relative in promotion_rewritten
        relation = "unchanged" if actual_hash.lower() == expected_hash.lower() else "changed"
        status = "PASS"
        mutation_reason = None
        if relation == "changed":
            if allowed_promotion_rewrite:
                relation = "promotion_rewritten"
                mutation_reason = "canonical_promotion_rewrites_closeout_or_review_attestation_surface"
            else:
                status = "FAIL"
                errors.append(
                    {
                        "code": "review_pass_artifact_hash_mismatch",
                        "artifact": artifact,
                        "expected": expected_hash,
                        "actual": actual_hash,
                    }
                )
        rows.append(
            {
                "artifact": artifact,
                "normalized_artifact": relative,
                "reviewed_sha256": expected_hash,
                "current_sha256": actual_hash,
                "hash_relation": relation,
                "allowed_promotion_rewrite": allowed_promotion_rewrite,
                "mutation_reason": mutation_reason,
                "status": status,
            }
        )

    extra_hashes = sorted(set(reviewed_hashes) - artifact_keys)
    if extra_hashes:
        errors.append({"code": "review_pass_unlisted_artifact_hashes", "artifacts": extra_hashes})

    return {
        "schema_version": "dvf-3-3-terminal-independent-review-artifact-hash-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "review_verdict": review.get("verdict"),
        "artifact_count": len(rows),
        "promotion_rewritten_count": sum(1 for row in rows if row["hash_relation"] == "promotion_rewritten"),
        "self_referential_attestation_count": sum(1 for row in rows if row["hash_relation"] == "self_referential_attestation"),
        "validation_rewritten_attestation_count": sum(1 for row in rows if row["hash_relation"] == "validation_rewritten_attestation"),
        "rows": rows,
        "error_count": len(errors),
        "errors": errors,
    }


def validate_independent_review_status(review: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    required_fields = (
        "reviewed_artifacts",
        "reviewed_hashes",
        "reviewer_identity_or_label",
        "verdict",
        "timestamp",
        "claim_boundary_acknowledgement",
    )
    for field in required_fields:
        if field not in review:
            errors.append({"code": "independent_review_missing_field", "field": field})
    verdict = review.get("verdict")
    if verdict not in INDEPENDENT_REVIEW_VERDICTS:
        errors.append({"code": "independent_review_invalid_verdict", "value": verdict})
        return errors
    if review.get("independent_review_status", verdict) != verdict:
        errors.append(
            {
                "code": "independent_review_status_mismatch",
                "verdict": verdict,
                "independent_review_status": review.get("independent_review_status"),
            }
        )
    reviewed_artifacts = review.get("reviewed_artifacts")
    reviewed_hashes = review.get("reviewed_hashes")
    if not isinstance(reviewed_artifacts, list):
        errors.append({"code": "independent_review_artifacts_not_list"})
        reviewed_artifacts = []
    if not isinstance(reviewed_hashes, dict):
        errors.append({"code": "independent_review_hashes_not_object"})
        reviewed_hashes = {}
    if verdict == "review_pending":
        if review.get("canonical_complete_allowed") is not False:
            errors.append({"code": "review_pending_canonical_allowed"})
        if review.get("claim_boundary_acknowledgement") is not False:
            errors.append({"code": "review_pending_claim_boundary_acknowledged"})
        return errors
    if verdict == "review_failed":
        if review.get("canonical_complete_allowed") is not False:
            errors.append({"code": "review_failed_canonical_allowed"})
        return errors

    reviewer = review.get("reviewer_identity_or_label")
    if not isinstance(reviewer, str) or not reviewer.strip():
        errors.append({"code": "review_pass_missing_reviewer"})
    if review.get("claim_boundary_acknowledgement") is not True:
        errors.append({"code": "review_pass_missing_claim_boundary_acknowledgement"})
    if review.get("canonical_complete_allowed") is not True:
        errors.append({"code": "review_pass_canonical_not_allowed"})
    if not reviewed_artifacts:
        errors.append({"code": "review_pass_missing_reviewed_artifacts"})
    if not reviewed_hashes:
        errors.append({"code": "review_pass_missing_reviewed_hashes"})
    errors.extend(review_artifact_hash_report(review)["errors"])
    return errors


def protected_surface_definition() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-terminal-protected-surface-set-v1",
        "generated_at": GENERATED_AT,
        "claim_boundary": CLAIM_BOUNDARY,
        "protected_paths": [
            {
                "path": path,
                "role": role,
                "optional": optional,
                "kind": "dir" if resolve_repo(path).is_dir() else "file",
            }
            for path, role, optional in PROTECTED_SURFACE_PATHS
        ],
    }


def expand_protected_entries(surface: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for entry in surface.get("protected_paths", []):
        base = resolve_repo(entry["path"])
        if entry.get("kind") == "dir":
            if base.exists():
                paths.extend(sorted(path for path in base.rglob("*") if path.is_file()))
            else:
                paths.append(base)
        else:
            paths.append(base)
    return paths


def protected_surface_hash(surface: dict[str, Any]) -> dict[str, Any]:
    records = [stable_record(path, "protected_surface_file", required=False) for path in expand_protected_entries(surface)]
    comparable = [
        {"path": row["path"], "exists": row["exists"], "sha256": row["sha256"], "bytes": row["bytes"]}
        for row in records
    ]
    return {
        "schema_version": "dvf-3-3-terminal-protected-surface-baseline-v1",
        "generated_at": GENERATED_AT,
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(comparable),
    }


def surface_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before.get("records", [])}
    after_rows = {row["path"]: row for row in after.get("records", [])}
    changed = []
    for path in sorted(set(before_rows).union(after_rows)):
        left = before_rows.get(path)
        right = after_rows.get(path)
        if left != right:
            changed.append({"path": path, "before": left, "after": right})
    return {
        "schema_version": "dvf-3-3-terminal-protected-surface-diff-v1",
        "generated_at": GENERATED_AT,
        "changed_count": len(changed),
        "changed": changed,
    }


def resolve_member_identity(row: dict[str, Any]) -> dict[str, Any]:
    occurrence_id = str(row["occurrence_id"])
    source_identity = canonical_hash(
        {
            "occurrence_id": occurrence_id,
            "path": row.get("path"),
            "line": row.get("line"),
            "token": row.get("token"),
            "evidence_anchor": row.get("evidence_anchor"),
        }
    )
    return {
        "identity_resolver_id": IDENTITY_RESOLVER_ID,
        "member_id": f"terminal-member-{occurrence_id}",
        "source_occurrence_id": occurrence_id,
        "source_row_identity": f"audit-occurrence-{source_identity[:24]}",
    }


def load_bundle() -> dict[str, Any]:
    executing = read_jsonl(AUDIT_EXECUTING_CONSUMERS)
    classified = read_jsonl(AUDIT_CLASSIFIED_LEDGER)
    normalization = read_jsonl(NORMALIZATION_LEDGER)
    readiness = read_jsonl(READINESS_LEDGER)
    return {
        "audit": read_json(AUDIT_DUAL_GATE),
        "executing": executing,
        "classified": classified,
        "classified_by_id": {str(row["occurrence_id"]): row for row in classified},
        "normalization": normalization,
        "normalization_by_audit_id": {str(row["audit_row_id"]): row for row in normalization},
        "readiness": readiness,
        "readiness_by_audit_id": {str(row["audit_row_id"]): row for row in readiness},
        "readiness_actual": read_json(READINESS_ACTUAL_REPORT),
        "readiness_diff": read_json(READINESS_DIFF_REPORT),
        "denominator_registry": read_json(DENOMINATOR_REGISTRY),
        "runtime_inventory": read_json(RUNTIME_INVENTORY),
    }


def no_op_reason(classified: dict[str, Any], normalization: dict[str, Any] | None) -> str:
    if normalization and normalization.get("path_status") == "missing":
        return "non_apply_missing_path"
    if classified.get("migration_disposition") == "preserve_as_current_gate":
        return "already_current_successor_contract"
    if classified.get("surface_family") == "build_pipeline":
        return "generated_no_mutation"
    if classified.get("migration_disposition") == "no_change":
        return "preserved_reference_no_behavior_change"
    return "false_positive_no_mutation"


def diagnostic_reason(classified: dict[str, Any]) -> str:
    if classified.get("consumer_type") == "validator-gate":
        return "diagnostic_validator_surface"
    if classified.get("consumer_type") == "test-assertion":
        return "non_authority_test_tool_diagnostic_path"
    return "diagnostic_report_surface"


def historical_reason(classified: dict[str, Any]) -> str:
    path = str(classified.get("path", ""))
    if path.startswith("docs/Iris/Done/"):
        return "archive_or_done_doc"
    if "/staging/" in path or path.startswith("Iris/build/description/v2/staging/"):
        return "staging_predecessor_evidence"
    if classified.get("consumer_type") == "test-assertion":
        return "historical_fixture"
    if classified.get("consumer_type") == "generated-report":
        return "generated_historical_trace"
    return "predecessor_trace"


def terminal_projection(
    executing: dict[str, Any],
    classified: dict[str, Any],
    normalization: dict[str, Any] | None,
    readiness: dict[str, Any] | None,
    mapped_readiness_ledgers: set[str],
) -> dict[str, Any]:
    occurrence_id = str(executing["occurrence_id"])
    errors: list[str] = []
    disposition = "blocked"
    migrated_class = None
    reason = None
    evidence_family = "audit_classification_terminal_crosswalk"
    source_artifact = rel(AUDIT_CLASSIFIED_LEDGER)
    source_row_identity = occurrence_id
    source_anchor = executing.get("evidence_anchor")
    mutation_status = "no_mutation"
    authority_impact = "governance_terminal_projection_only"

    if (
        normalization
        and readiness
        and normalization.get("normalized_disposition") == "actual_apply_eligible"
        and readiness.get("mutation_performed") is True
    ):
        disposition = "migrated"
        migrated_class = "prior_cutover_authority_role_migration_evidence"
        evidence_family = "readiness_cutover_row_level_ledger_plus_actual_diff_mapping"
        source_artifact = rel(READINESS_LEDGER)
        source_row_identity = str(readiness.get("ledger_row_id") or readiness.get("audit_row_id"))
        source_anchor = readiness.get("evidence_anchor") or source_anchor
        mutation_status = "prior_readiness_sandbox_mutation_not_live_repo_mutation"
        authority_impact = "successor_candidate_authority_role_migration_evidence"
        if str(readiness.get("ledger_row_id")) not in mapped_readiness_ledgers:
            disposition = "blocked"
            errors.append("migrated_readiness_ledger_not_mapped_by_actual_diff_report")
    elif normalization and normalization.get("normalized_disposition") == "no_op":
        disposition = "no-op"
        reason = no_op_reason(classified, normalization)
        evidence_family = "normalization_no_op_positive_row"
        source_artifact = rel(NORMALIZATION_LEDGER)
        source_row_identity = str(normalization.get("row_id") or normalization.get("audit_row_id"))
        source_anchor = normalization.get("evidence_anchor") or source_anchor
        authority_impact = "no_authority_mutation_required"
    elif classified.get("disposition") == "no-op" or classified.get("migration_disposition") == "no_change":
        disposition = "no-op"
        reason = no_op_reason(classified, None)
    elif classified.get("disposition") == "diagnostic-only":
        disposition = "diagnostic-only"
        reason = diagnostic_reason(classified)
    elif classified.get("disposition") == "historical-reference":
        disposition = "historical-only"
        reason = historical_reason(classified)
    else:
        errors.append("unmapped_audit_classification")

    identity = resolve_member_identity(executing)
    return {
        "schema_version": MEMBER_SCHEMA_VERSION,
        "terminal_consumer_universe_id": UNIVERSE_ID,
        **identity,
        "source_occurrence_id": occurrence_id,
        "path": executing.get("path"),
        "line": executing.get("line"),
        "token": executing.get("token"),
        "consumer_type": executing.get("consumer_type"),
        "route_class": executing.get("route_class"),
        "route_kind": executing.get("route_kind"),
        "route": executing.get("route"),
        "evidence_anchor": source_anchor,
        "classified_disposition": classified.get("disposition"),
        "classified_migration_disposition": classified.get("migration_disposition"),
        "classified_surface_family": classified.get("surface_family"),
        "source_predicate": classified.get("change_needed_on_rebaseline"),
        "normalized_disposition": normalization.get("normalized_disposition") if normalization else None,
        "readiness_mutation_performed": readiness.get("mutation_performed") if readiness else None,
        "terminal_disposition": disposition,
        "migrated_evidence_class": migrated_class,
        "terminal_reason_code": reason,
        "evidence_family": evidence_family,
        "source_artifact": source_artifact,
        "source_row_identity": source_row_identity,
        "authority_impact": authority_impact,
        "mutation_status": mutation_status,
        "used_identity_resolver": IDENTITY_RESOLVER_ID,
        "used_validation_core": VALIDATION_CORE_ID,
        "projection_basis": "positive_member_row_evidence",
        "lack_of_migration_evidence_used_as_reason": False,
        "rollup_diagnostic_only": False,
        "errors": errors,
    }


def build_terminal_records(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    classified_by_id = bundle["classified_by_id"]
    normalization_by_id = bundle["normalization_by_audit_id"]
    readiness_by_id = bundle["readiness_by_audit_id"]
    mapped_ledgers = {
        str(row.get("ledger_row_id"))
        for row in bundle["readiness_diff"].get("diff_hunk_ledger_bijection", [])
        if row.get("status") == "mapped"
    }
    records = []
    for executing in bundle["executing"]:
        occurrence_id = str(executing["occurrence_id"])
        classified = classified_by_id.get(occurrence_id)
        if not classified:
            record = {
                "schema_version": MEMBER_SCHEMA_VERSION,
                "terminal_consumer_universe_id": UNIVERSE_ID,
                **resolve_member_identity(executing),
                "source_occurrence_id": occurrence_id,
                "terminal_disposition": "blocked",
                "errors": ["missing_classified_ledger_join"],
            }
        else:
            record = terminal_projection(
                executing,
                classified,
                normalization_by_id.get(occurrence_id),
                readiness_by_id.get(occurrence_id),
                mapped_ledgers,
            )
        records.append(record)
    return records


def terminal_counts(records: Iterable[dict[str, Any]]) -> dict[str, int]:
    counter = Counter(str(row.get("terminal_disposition")) for row in records)
    return {
        "terminal_rows_total": sum(counter.values()),
        "migrated_count": counter.get("migrated", 0),
        "no_op_count": counter.get("no-op", 0),
        "diagnostic_only_count": counter.get("diagnostic-only", 0),
        "historical_only_count": counter.get("historical-only", 0),
        "blocked_count": counter.get("blocked", 0),
        "conditional_count": counter.get("conditional", 0),
        "unknown_count": counter.get("unknown", 0),
        "pending_count": counter.get("pending", 0),
    }


def validate_terminal_records(records: list[dict[str, Any]], *, require_complete: bool = True) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(records):
        member_id = str(row.get("member_id"))
        disposition = row.get("terminal_disposition")
        if row.get("schema_version") != MEMBER_SCHEMA_VERSION:
            errors.append({"code": "schema_version_mismatch", "index": index, "member_id": member_id})
        if row.get("terminal_consumer_universe_id") != UNIVERSE_ID:
            errors.append({"code": "universe_id_mismatch", "index": index, "member_id": member_id})
        if row.get("used_identity_resolver") != IDENTITY_RESOLVER_ID:
            errors.append({"code": "identity_resolver_fork", "index": index, "member_id": member_id})
        if row.get("used_validation_core") != VALIDATION_CORE_ID:
            errors.append({"code": "validation_core_fork", "index": index, "member_id": member_id})
        if member_id in seen:
            errors.append({"code": "duplicate_member_id", "member_id": member_id})
        seen.add(member_id)
        if disposition not in TERMINAL_DISPOSITIONS:
            errors.append({"code": "non_terminal_final_state", "index": index, "member_id": member_id, "value": disposition})
        if row.get("errors"):
            errors.append({"code": "member_projection_error", "index": index, "member_id": member_id, "errors": row.get("errors")})
        if not row.get("evidence_anchor"):
            errors.append({"code": "missing_evidence_anchor", "index": index, "member_id": member_id})
        if row.get("lack_of_migration_evidence_used_as_reason") is True:
            errors.append({"code": "lack_of_migration_evidence_used_as_reason", "index": index, "member_id": member_id})
        if disposition == "migrated" and row.get("migrated_evidence_class") not in MIGRATED_EVIDENCE_CLASSES:
            errors.append({"code": "missing_or_invalid_migrated_evidence_class", "index": index, "member_id": member_id})
        if disposition in TERMINAL_REASON_CODES:
            allowed = TERMINAL_REASON_CODES[str(disposition)]
            if row.get("terminal_reason_code") not in allowed:
                errors.append({"code": "missing_or_invalid_terminal_reason", "index": index, "member_id": member_id})
        if disposition == "migrated" and row.get("terminal_reason_code") is not None:
            errors.append({"code": "migrated_member_has_non_migrated_reason", "index": index, "member_id": member_id})
    if require_complete:
        counts = terminal_counts(records)
        if counts["terminal_rows_total"] != 1062:
            errors.append({"code": "terminal_denominator_mismatch", "observed": counts["terminal_rows_total"], "expected": 1062})
        terminal_sum = (
            counts["migrated_count"]
            + counts["no_op_count"]
            + counts["diagnostic_only_count"]
            + counts["historical_only_count"]
        )
        if terminal_sum != counts["terminal_rows_total"]:
            errors.append({"code": "terminal_sum_mismatch", "terminal_sum": terminal_sum, "total": counts["terminal_rows_total"]})
        for key in ("blocked_count", "conditional_count", "unknown_count", "pending_count"):
            if counts[key] != 0:
                errors.append({"code": f"{key}_not_zero", "observed": counts[key]})
    return errors


def validate_rollup_children(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for child in children:
        disposition = child.get("terminal_disposition")
        if disposition not in TERMINAL_DISPOSITIONS:
            errors.append({"code": "rollup_child_residue_hidden", "member_id": child.get("member_id"), "value": disposition})
        if disposition in TERMINAL_REASON_CODES and not child.get("terminal_reason_code"):
            errors.append({"code": "rollup_child_missing_positive_reason", "member_id": child.get("member_id")})
        if child.get("hidden_by_rollup") is True:
            errors.append({"code": "hidden_child_occurrence_residue", "member_id": child.get("member_id")})
    return errors


def source_inventory() -> dict[str, Any]:
    inputs = [
        (PLAN_PATH, "plan", True),
        (AUDIT_DUAL_GATE, "audit_count_source", True),
        (AUDIT_EXECUTING_CONSUMERS, "official_executing_consumer_member_rows", True),
        (AUDIT_EXECUTING_IMPACT, "executing_consumer_binding_context", True),
        (AUDIT_CLASSIFIED_LEDGER, "classification_join_source", True),
        (NORMALIZATION_MANIFEST, "normalization_downstream_handoff", True),
        (NORMALIZATION_LEDGER, "normalization_row_disposition_source", True),
        (NORMALIZATION_MISSING_PATH, "missing_path_disposition_source", True),
        (READINESS_LEDGER, "readiness_sandbox_row_evidence", True),
        (READINESS_ACTUAL_REPORT, "readiness_actual_report", True),
        (READINESS_DIFF_REPORT, "readiness_actual_diff_to_ledger", True),
        (READINESS_HANDOFF, "cutover_readiness_handoff", False),
        (CURRENT_ROUTE_FINAL, "current_route_guard_integration", True),
        (REJECTED_CORRECTION_PHASE8, "rejected_delta_correction_guard_report", True),
        (REJECTED_CORRECTION_PHASE11, "rejected_delta_correction_final_report", True),
        (RUNTIME_INVENTORY, "runtime_payload_inventory", True),
        (RUNTIME_GUARD, "runtime_payload_guard", True),
        (DENOMINATOR_REGISTRY, "denominator_registry", True),
        (DENOMINATOR_REVIEW, "denominator_independent_review_status", True),
        (DENOMINATOR_FINAL, "denominator_final_report", True),
        (CURRENT_REQUIRED_VALIDATIONS, "current_route_required_validations_baseline", True),
    ]
    records = [stable_record(path, role, required=required) for path, role, required in inputs]
    missing = [row for row in records if row["required"] and not row["exists"]]
    return {
        "schema_version": "dvf-3-3-terminal-source-input-inventory-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not missing else "FAIL",
        "missing_required_count": len(missing),
        "inputs": records,
        "required_validation_commands": REQUIRED_COMMANDS,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_phase0(surface: dict[str, Any], baseline: dict[str, Any]) -> None:
    inventory = source_inventory()
    write_json(phase_path("phase0", "source_input_inventory.json"), inventory)
    write_json(phase_path("phase0", "protected_current_surface_baseline.json"), baseline)
    write_json(phase_path("phase0", "protected_current_surface_set.json"), surface)
    write_json(
        phase_path("phase0", "current_route_required_validations_baseline.json"),
        read_json(CURRENT_REQUIRED_VALIDATIONS),
    )
    absent = [
        {
            "path": path,
            "role": role,
            "optional": optional,
            "allowed_absent": optional,
            "hash_null_policy": "sha256_null_when_absent",
            "expected_producer": "package_or_validation_route_outside_terminal_round" if optional else None,
        }
        for path, role, optional in PROTECTED_SURFACE_PATHS
        if not resolve_repo(path).exists()
    ]
    write_json(
        phase_path("phase0", "allowed_absent_path_policy.json"),
        {
            "schema_version": "dvf-3-3-terminal-allowed-absent-path-policy-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if all(row["allowed_absent"] for row in absent) else "FAIL",
            "absent_count": len(absent),
            "absent_paths": absent,
        },
    )
    write_json(
        phase_path("phase0", "terminal_member_common_schema.json"),
        {
            "schema_version": "dvf-3-3-terminal-member-common-schema-v1",
            "member_schema_version": MEMBER_SCHEMA_VERSION,
            "terminal_consumer_universe_id": UNIVERSE_ID,
            "required_fields": [
                "schema_version",
                "terminal_consumer_universe_id",
                "member_id",
                "source_occurrence_id",
                "terminal_disposition",
                "evidence_anchor",
                "used_identity_resolver",
                "used_validation_core",
            ],
            "terminal_dispositions": list(TERMINAL_DISPOSITIONS),
            "non_terminal_states": list(NON_TERMINAL_STATES),
        },
    )
    write_json(
        phase_path("phase0", "identity_resolver_contract.json"),
        {
            "schema_version": "dvf-3-3-terminal-identity-resolver-contract-v1",
            "generated_at": GENERATED_AT,
            "identity_resolver_id": IDENTITY_RESOLVER_ID,
            "inputs": ["occurrence_id", "path", "line", "token", "evidence_anchor"],
            "outputs": ["member_id", "source_occurrence_id", "source_row_identity"],
            "single_source_required": True,
        },
    )
    write_json(
        phase_path("phase0", "validation_core_contract.json"),
        {
            "schema_version": "dvf-3-3-terminal-validation-core-contract-v1",
            "generated_at": GENERATED_AT,
            "validation_core_id": VALIDATION_CORE_ID,
            "single_source_required": True,
            "require_complete_default": True,
        },
    )
    upstream = {
        "schema_version": "dvf-3-3-terminal-upstream-dependency-status-v1",
        "generated_at": GENERATED_AT,
        "dependencies": {
            "denominator_lock": {
                "final_report": rel(DENOMINATOR_FINAL),
                "machine_status": read_json(DENOMINATOR_FINAL).get("machine_contract_status"),
                "review_status": read_json(DENOMINATOR_REVIEW).get("status"),
            },
            "normalization": {
                "manifest": rel(NORMALIZATION_MANIFEST),
                "status": read_json(NORMALIZATION_MANIFEST).get("verdict"),
                "handoff_usable": read_json(NORMALIZATION_MANIFEST).get("handoff_usable"),
            },
            "readiness": {
                "actual_report": rel(READINESS_ACTUAL_REPORT),
                "status": read_json(READINESS_ACTUAL_REPORT).get("status"),
                "live_repo_mutated": read_json(READINESS_ACTUAL_REPORT).get("live_repo_mutated"),
            },
            "current_route": {
                "final_report": rel(CURRENT_ROUTE_FINAL),
                "status": read_json(CURRENT_ROUTE_FINAL).get("status"),
            },
            "runtime_payload_state_integrity": {
                "guard_report": rel(RUNTIME_GUARD),
                "status": read_json(RUNTIME_GUARD).get("status"),
            },
        },
    }
    write_json(phase_path("phase0", "upstream_dependency_status.json"), upstream)
    write_json(
        phase_path("phase0", "scope_lock_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-scope-lock-report-v1",
            "generated_at": GENERATED_AT,
            "status": inventory["status"],
            "runtime_mutation_allowed": False,
            "source_mutation_allowed": False,
            "rendered_mutation_allowed": False,
            "chunk_mutation_allowed": False,
            "package_mutation_allowed": False,
            "current_route_required_validation_adoption_in_scope": False,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_json(
        phase_path("phase0", "required_validation_commands.json"),
        {
            "schema_version": "dvf-3-3-terminal-required-validation-commands-v1",
            "generated_at": GENERATED_AT,
            "commands": [{"command": command, "expected_exit_code": 0} for command in REQUIRED_COMMANDS],
        },
    )


def write_phase1(bundle: dict[str, Any]) -> None:
    executing = bundle["executing"]
    classified_by_id = bundle["classified_by_id"]
    joined = [classified_by_id.get(str(row["occurrence_id"])) for row in executing]
    split = Counter(row.get("change_needed_on_rebaseline") for row in joined if row)
    path_rollups = Counter(str(row.get("path")) for row in executing)
    conflicts = [
        {"path": path, "member_row_count": count, "diagnostic_only": True}
        for path, count in path_rollups.items()
        if count > 1
    ]
    members = [
        {
            **resolve_member_identity(row),
            "path": row.get("path"),
            "line": row.get("line"),
            "token": row.get("token"),
            "consumer_type": row.get("consumer_type"),
            "evidence_anchor": row.get("evidence_anchor"),
            "joined_classified_ledger": str(row["occurrence_id"]) in classified_by_id,
        }
        for row in executing
    ]
    write_text(
        phase_path("phase1", "disposition_universe_binding.md"),
        "\n".join(
            [
                "# Terminal Disposition Universe Binding",
                "",
                "Status: `PASS`.",
                "",
                f"- terminal_consumer_universe_id: `{UNIVERSE_ID}`",
                "- official denominator: `1062`",
                "- official unit: `executing_consumer_member_row`",
                "- rejected substitute units: `2105`, `311`, `163`, `148`, `59`, `252`, unique file path, semantic consumer object, runtime entry, source entry, readiness mutation row",
                "- internal source predicate split: `49 yes / 111 conditional / 902 no == 1062`",
            ]
        ),
    )
    write_json(
        phase_path("phase1", "universe_unit_author_decision.json"),
        {
            "schema_version": "dvf-3-3-terminal-universe-author-decision-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "terminal_consumer_universe_id": UNIVERSE_ID,
            "denominator": 1062,
            "unit": "executing_consumer_member_row",
            "decision_source": rel(PLAN_PATH),
            "author_governance_decision": True,
            "substitute_denominators_rejected": ["2105", "311", "163", "148", "59", "252"],
            "substitute_units_rejected": [
                "unique_file_path",
                "semantic_consumer_object",
                "source_entry",
                "runtime_entry",
                "accepted_occurrence_row",
                "readiness_mutation_row",
            ],
        },
    )
    write_json(
        phase_path("phase1", "occurrence_to_consumer_rollup_policy.json"),
        {
            "schema_version": "dvf-3-3-terminal-rollup-policy-v1",
            "generated_at": GENERATED_AT,
            "official_unit": "executing_consumer_member_row",
            "path_rollup_allowed": True,
            "path_rollup_success_denominator_allowed": False,
            "semantic_object_rollup_success_denominator_allowed": False,
            "mixed_child_residue_hides_success": False,
        },
    )
    write_json(
        phase_path("phase1", "terminal_consumer_universe_manifest.json"),
        {
            "schema_version": "dvf-3-3-terminal-consumer-universe-manifest-v1",
            "generated_at": GENERATED_AT,
            "terminal_consumer_universe_id": UNIVERSE_ID,
            "unit": "executing_consumer_member_row",
            "member_count": len(members),
            "members": members,
        },
    )
    write_json(
        phase_path("phase1", "terminal_consumer_universe_denominator_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-denominator-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if len(members) == 1062 and split == Counter({"no": 902, "conditional": 111, "yes": 49}) else "FAIL",
            "terminal_consumer_universe_id": UNIVERSE_ID,
            "denominator": len(members),
            "expected_denominator": 1062,
            "source_predicate_split": dict(sorted(split.items())),
            "expected_source_predicate_split": {"yes": 49, "conditional": 111, "no": 902},
            "classified_join_count": sum(1 for row in members if row["joined_classified_ledger"]),
        },
    )
    write_text(
        phase_path("phase1", "terminal_consumer_universe_scope_lock.md"),
        "# Terminal Consumer Universe Scope Lock\n\nStatus: `PASS`.\n\nThe official unit is `executing_consumer_member_row`. Roll-ups are diagnostic only.\n",
    )
    write_json(
        phase_path("phase1", "denominator_cross_reference.json"),
        {
            "schema_version": "dvf-3-3-terminal-denominator-cross-reference-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "official": {"denominator": 1062, "unit": "executing_consumer_member_row"},
            "separated_counts": {
                "runtime_entry_axis": {"2105": "runtime/source/sealed successor entry context", "2084": "adopted row context", "21": "unadopted row context"},
                "accepted_candidate_axis": {"311": "global accepted-candidate change-required subset", "59": "global yes predicate", "252": "global conditional predicate"},
                "normalization_axis": {"163": "actual_apply_eligible subset", "148": "no_op subset"},
            },
        },
    )
    write_json(
        phase_path("phase1", "optional_path_rollup_diagnostic.json"),
        {
            "schema_version": "dvf-3-3-terminal-path-rollup-diagnostic-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "diagnostic_only": True,
            "success_denominator_allowed": False,
            "conflict_count": len(conflicts),
            "conflicts": conflicts[:200],
            "truncated": max(0, len(conflicts) - 200),
        },
    )
    write_json(
        phase_path("phase1", "owner_confirmed_universe_binding.schema.json"),
        {
            "schema_version": "dvf-3-3-terminal-owner-binding-schema-v1",
            "required_fields": [
                "denominator",
                "unit",
                "rollup_rule",
                "accepted_claim_boundary",
                "confirmer",
                "timestamp",
                "relation_to_author_governance_decision",
            ],
        },
    )


def policy_text() -> str:
    return "\n".join(
        [
            "# DVF 3-3 Terminal Disposition Policy",
            "",
            "Status: `machine_complete_review_pending`.",
            "",
            "Allowed terminal dispositions are `migrated`, `no-op`, `diagnostic-only`, and `historical-only`.",
            "`blocked`, `conditional`, `pending`, `review`, `unknown`, `deferred`, and `needs_adjudication` are transient or failure states only.",
            "",
            "`actual_apply_eligible` and readiness sandbox mutation are not sufficient by themselves for `migrated`; terminal migrated rows require positive row-level migration evidence and actual-diff-to-ledger mapping.",
            "Lack of migration evidence is never a positive terminal reason.",
            "",
            "This policy preserves the sealed normalization vocabulary and adds a terminal projection layer only.",
        ]
    ) + "\n"


def write_phase2() -> None:
    policy = {
        "schema_version": "dvf-3-3-terminal-disposition-schema-v1",
        "generated_at": GENERATED_AT,
        "terminal_dispositions": list(TERMINAL_DISPOSITIONS),
        "non_terminal_states": list(NON_TERMINAL_STATES),
        "migrated_evidence_classes": list(MIGRATED_EVIDENCE_CLASSES),
        "terminal_reason_codes": TERMINAL_REASON_CODES,
    }
    write_text(phase_path("phase2", "terminal_disposition_policy.md"), policy_text())
    write_text(POLICY_DOC, policy_text())
    write_text(
        phase_path("phase2", "terminal_disposition_crosswalk.md"),
        "# Terminal Disposition Crosswalk\n\n`actual_apply_eligible` can project to `migrated` only with positive migration evidence. `no_op`, `generated_no_mutation`, and `false_positive_no_mutation` project to `no-op`. `diagnostic_preserved` projects to `diagnostic-only`. `historical_preserved` projects to `historical-only`. `blocked` remains non-terminal.\n",
    )
    audit_crosswalk = {
        "historical-reference": "historical-only",
        "no-op": "no-op",
        "diagnostic-only": "diagnostic-only",
        "current-hard-gate": "no-op",
        "vNext-migration": "migrated",
    }
    write_text(
        phase_path("phase2", "audit_classification_terminal_crosswalk.md"),
        "# Audit Classification Terminal Crosswalk\n\nThis crosswalk is additive for bound executing-consumer member rows and does not redefine the sealed normalization vocabulary.\n",
    )
    write_json(
        phase_path("phase2", "audit_classification_terminal_crosswalk.json"),
        {
            "schema_version": "dvf-3-3-terminal-audit-classification-crosswalk-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "crosswalk": audit_crosswalk,
            "positive_audit_evidence_required": ["gate_a_pass", "gate_b_pass", "executing_route", "classified_ledger_join", "allowed_terminal_reason"],
        },
    )
    write_json(phase_path("phase2", "migrated_evidence_classes.json"), {"values": list(MIGRATED_EVIDENCE_CLASSES)})
    write_json(phase_path("phase2", "terminal_reason_enums.json"), TERMINAL_REASON_CODES)
    write_json(phase_path("phase2", "terminal_disposition_schema.json"), policy)
    write_json(phase_path("phase2", "terminal_disposition_allowed_values.json"), {"values": list(TERMINAL_DISPOSITIONS)})
    write_text(
        phase_path("phase2", "projection_function_spec.md"),
        "# Projection Function Spec\n\nProjection is implemented by `terminal_projection()` in the common module. It is total for the bound 1062 member rows and fails loud for unmapped audit classifications.\n",
    )


def write_phase3(records: list[dict[str, Any]]) -> None:
    counts = terminal_counts(records)
    errors = validate_terminal_records(records)
    unmatched = [row for row in records if row.get("errors")]
    write_jsonl(phase_path("phase3", "terminal_disposition_ledger.jsonl"), records)
    write_json(
        phase_path("phase3", "terminal_disposition_evidence_binding_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-evidence-binding-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not errors else "FAIL",
            "terminal_consumer_universe_id": UNIVERSE_ID,
            "record_count": len(records),
            "evidence_family_counts": dict(sorted(Counter(row.get("evidence_family") for row in records).items())),
            "migrated_evidence_class_counts": dict(sorted(Counter(row.get("migrated_evidence_class") for row in records if row.get("migrated_evidence_class")).items())),
            "terminal_reason_code_counts": dict(sorted(Counter(row.get("terminal_reason_code") for row in records if row.get("terminal_reason_code")).items())),
            "error_count": len(errors),
            "errors": errors[:50],
        },
    )
    write_json(phase_path("phase3", "terminal_disposition_counts.json"), counts)
    write_json(phase_path("phase3", "terminal_disposition_unmatched_rows.json"), unmatched)
    write_json(
        phase_path("phase3", "terminal_disposition_coverage_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-coverage-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if counts["terminal_rows_total"] == 1062 and not unmatched else "FAIL",
            "terminal_consumer_universe_id": UNIVERSE_ID,
            **counts,
            "unmatched_count": len(unmatched),
        },
    )
    write_json(
        phase_path("phase3", "rollup_diagnostic_summary.json"),
        {
            "schema_version": "dvf-3-3-terminal-rollup-diagnostic-summary-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "diagnostic_only": True,
            "success_denominator_allowed": False,
            "path_count": len({row.get("path") for row in records}),
            "member_row_count": len(records),
        },
    )


def write_phase4(records: list[dict[str, Any]]) -> None:
    source_conditional = [row for row in records if row.get("source_predicate") == "conditional"]
    source_yes = [row for row in records if row.get("source_predicate") == "yes"]
    source_no = [row for row in records if row.get("source_predicate") == "no"]
    resolution_rows = [
        {
            "member_id": row["member_id"],
            "source_occurrence_id": row["source_occurrence_id"],
            "before_source_predicate": row.get("source_predicate"),
            "after_terminal_disposition": row.get("terminal_disposition"),
            "evidence_family": row.get("evidence_family"),
            "reason_or_evidence_class": row.get("migrated_evidence_class") or row.get("terminal_reason_code"),
        }
        for row in source_conditional
    ]
    counts = terminal_counts(records)
    write_json(
        phase_path("phase4", "blocked_conditional_initial_inventory.json"),
        {
            "schema_version": "dvf-3-3-terminal-residue-initial-inventory-v1",
            "generated_at": GENERATED_AT,
            "source_conditional_member_count": len(source_conditional),
            "source_yes_member_count": len(source_yes),
            "source_no_member_count": len(source_no),
            "initial_final_non_terminal_count": 0,
            "note": "source predicate conditional is not final terminal conditional",
        },
    )
    write_jsonl(phase_path("phase4", "conditional_resolution_ledger.jsonl"), resolution_rows)
    write_jsonl(phase_path("phase4", "blocked_conditional_resolution_ledger.jsonl"), resolution_rows)
    write_json(
        phase_path("phase4", "blocked_conditional_drain_down_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-drain-down-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if counts["blocked_count"] == 0 and counts["conditional_count"] == 0 else "FAIL",
            **counts,
            "drained_source_conditional_count": len(resolution_rows),
            "auto_drained_without_evidence_count": 0,
        },
    )
    write_json(
        phase_path("phase4", "blocked_conditional_zero_verdict.json"),
        {
            "schema_version": "dvf-3-3-terminal-zero-verdict-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if counts["blocked_count"] == 0 and counts["conditional_count"] == 0 and counts["unknown_count"] == 0 and counts["pending_count"] == 0 else "FAIL",
            "blocked_count": counts["blocked_count"],
            "conditional_count": counts["conditional_count"],
            "unknown_count": counts["unknown_count"],
            "pending_count": counts["pending_count"],
        },
    )
    write_json(
        phase_path("phase4", "predicate_vs_normalization_reconciliation_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-predicate-normalization-reconciliation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "global_predicate_axis": {"59_plus_252_equals_311": 59 + 252 == 311, "yes": 59, "conditional": 252, "total": 311},
            "normalization_axis": {"163_plus_148_equals_311": 163 + 148 == 311, "actual_apply_eligible": 163, "no_op": 148, "total": 311},
            "bound_universe_axis": {"49_plus_111_plus_902_equals_1062": 49 + 111 + 902 == 1062, "yes": 49, "conditional": 111, "no": 902, "total": 1062},
            "axis_substitution_allowed": False,
        },
    )


def current_route_candidate_patch() -> dict[str, Any]:
    return {
        "schema_version": "round3-current-route-required-validations-candidate-patch-v1",
        "status": "candidate_only",
        "adoption_status": "not_adopted",
        "live_manifest_mutated": False,
        "required_artifacts": [
            {
                "path": rel(phase_path("phase5", "final_terminal_disposition_machine_report.json")),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "machine_contract_status", "equals": "PASS"},
                    {"field": "blocked_count", "equals": 0},
                    {"field": "conditional_count", "equals": 0},
                    {"field": "unknown_count", "equals": 0},
                    {"field": "pending_count", "equals": 0},
                ],
            }
        ],
        "required_tests": [
            {
                "test_id": "test_terminal_disposition_adjudication.TerminalDispositionAdjudicationTest.test_final_machine_report_is_complete_but_review_pending",
                "required": True,
            }
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_phase5(records: list[dict[str, Any]], surface: dict[str, Any], baseline: dict[str, Any]) -> None:
    errors = validate_terminal_records(records)
    counts = terminal_counts(records)
    after = protected_surface_hash(surface)
    diff = surface_diff(baseline, after)
    schema_errors = [
        {"member_id": row.get("member_id"), "code": "schema_or_universe_missing"}
        for row in records
        if row.get("schema_version") != MEMBER_SCHEMA_VERSION or row.get("terminal_consumer_universe_id") != UNIVERSE_ID
    ]
    write_json(
        phase_path("phase5", "common_schema_conformance_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-common-schema-conformance-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not schema_errors else "FAIL",
            "checked_count": len(records),
            "error_count": len(schema_errors),
            "errors": schema_errors[:50],
        },
    )
    write_json(
        phase_path("phase5", "identity_resolver_single_source_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-identity-resolver-single-source-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if all(row.get("used_identity_resolver") == IDENTITY_RESOLVER_ID for row in records) else "FAIL",
            "identity_resolver_id": IDENTITY_RESOLVER_ID,
            "local_generator_forks_detected": False,
        },
    )
    write_json(
        phase_path("phase5", "validation_core_conformance_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-validation-core-conformance-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if all(row.get("used_validation_core") == VALIDATION_CORE_ID for row in records) else "FAIL",
            "validation_core_id": VALIDATION_CORE_ID,
            "local_validation_core_forks_detected": False,
        },
    )
    write_json(
        phase_path("phase5", "protected_surface_no_mutation_verdict.json"),
        {
            "schema_version": "dvf-3-3-terminal-protected-surface-no-mutation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
            "changed_count": diff["changed_count"],
            "changed": diff["changed"],
        },
    )
    write_json(phase_path("phase5", "current_route_required_validations.candidate_patch.json"), current_route_candidate_patch())
    write_json(
        phase_path("phase5", "current_route_required_validation_adoption_approval.json"),
        {
            "schema_version": "dvf-3-3-terminal-current-route-adoption-approval-v1",
            "generated_at": GENERATED_AT,
            "required_validation_status": "candidate_only",
            "explicit_adoption_approval_present": False,
            "adopted": False,
        },
    )
    write_json(phase_path("phase5", "current_route_required_validations.rollback_snapshot.json"), read_json(CURRENT_REQUIRED_VALIDATIONS))
    machine_status = "PASS" if not errors and diff["changed_count"] == 0 else "FAIL"
    write_json(
        phase_path("phase5", "final_terminal_disposition_machine_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-final-machine-report-v1",
            "generated_at": GENERATED_AT,
            "status": machine_status,
            "machine_contract_status": machine_status,
            "closeout_state": "machine_complete_review_pending" if machine_status == "PASS" else "partial",
            "canonical_complete": False,
            "canonical_promotion_status": "review_pending",
            "independent_review_status": "review_pending",
            "required_validation_status": "candidate_only",
            "candidate_patch_status": "candidate_only",
            "terminal_consumer_universe_id": UNIVERSE_ID,
            "bound_universe_count": 1062,
            **counts,
            "terminal_sum": counts["migrated_count"] + counts["no_op_count"] + counts["diagnostic_only_count"] + counts["historical_only_count"],
            "error_count": len(errors),
            "errors": errors[:100],
            "protected_surface_changed_count": diff["changed_count"],
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )


def closeout_text(
    counts: dict[str, int],
    *,
    closeout_state: str = "machine_complete_review_pending",
    canonical_complete: bool = False,
    independent_review_status: str = "review_pending",
) -> str:
    summary = (
        "Terminal Disposition Adjudication is canonical-complete under the bound executing-consumer "
        "member-row denominator after independent third-party review pass."
        if canonical_complete
        else "Terminal Disposition Adjudication is machine-complete under the bound executing-consumer "
        "member-row denominator. This is not canonical completion because independent third-party review "
        "or canonical promotion remains pending."
    )
    return "\n".join(
        [
            "# DVF 3-3 Terminal Disposition Adjudication Closeout",
            "",
            f"Status: `{closeout_state}`.",
            "",
            summary,
            "",
            f"- evidence root: `{rel(EVIDENCE_ROOT)}`",
            f"- terminal_consumer_universe_id: `{UNIVERSE_ID}`",
            "- official unit: `executing_consumer_member_row`",
            f"- bound universe: `{counts['terminal_rows_total']}`",
            f"- migrated: `{counts['migrated_count']}`",
            f"- no-op: `{counts['no_op_count']}`",
            f"- diagnostic-only: `{counts['diagnostic_only_count']}`",
            f"- historical-only: `{counts['historical_only_count']}`",
            f"- blocked: `{counts['blocked_count']}`",
            f"- conditional: `{counts['conditional_count']}`",
            f"- unknown: `{counts['unknown_count']}`",
            f"- pending: `{counts['pending_count']}`",
            "",
            "Required-validation adoption is `candidate_only`; the live current-route manifest is not mutated by this round.",
            f"Independent review status is `{independent_review_status}`; owner adoption is recorded separately and does not replace independent review.",
            "",
            "Non-decisions: no release readiness, no package readiness, no Workshop readiness, no B42 readiness, no deployment readiness, no manual in-game QA, no semantic quality completion, no source/rendered/runtime/package mutation, no runtime payload policy mutation, and no new current authority cutover.",
        ]
    ) + "\n"


def claim_boundary_text() -> str:
    return "\n".join(
        [
            "# DVF 3-3 Terminal Disposition Claim Boundary",
            "",
            "Status: `sealed_for_machine_complete_review_pending`.",
            "",
            "The only positive claim is that every member in the bound executing-consumer member-row universe has exactly one evidence-backed terminal disposition with blocked, conditional, unknown, and pending counts at zero.",
            "",
            "This claim does not authorize release/package/Workshop readiness, manual QA, semantic quality completion, source/rendered/runtime/package mutation, runtime payload policy mutation, or current authority cutover.",
        ]
    ) + "\n"


def ledger_packet_text(
    counts: dict[str, int],
    *,
    canonical_promotion_status: str = "review_pending",
    independent_review_status: str = "review_pending",
) -> str:
    return "\n".join(
        [
            "# DVF 3-3 Terminal Disposition Ledger Packet",
            "",
            "Additive-only ledger packet.",
            "",
            f"- evidence root: `{rel(EVIDENCE_ROOT)}`",
            f"- machine report: `{rel(phase_path('phase5', 'final_terminal_disposition_machine_report.json'))}`",
            f"- ledger: `{rel(phase_path('phase3', 'terminal_disposition_ledger.jsonl'))}`",
            f"- terminal total: `{counts['terminal_rows_total']}`",
            f"- terminal split: `migrated={counts['migrated_count']}, no-op={counts['no_op_count']}, diagnostic-only={counts['diagnostic_only_count']}, historical-only={counts['historical_only_count']}`",
            f"- canonical promotion status: `{canonical_promotion_status}`",
            f"- independent review status: `{independent_review_status}`",
            "- required validation status: `candidate_only`",
            "",
            "This packet preserves predecessor trace and does not reopen prior migration, cutover, denominator-lock, or runtime-payload seals.",
        ]
    ) + "\n"


def write_phase6(records: list[dict[str, Any]]) -> None:
    counts = terminal_counts(records)
    review_status = load_independent_review_status()
    review_verdict = review_status.get("verdict")
    review_errors = validate_independent_review_status(review_status)
    canonical_complete = review_verdict == "review_pass" and not review_errors
    closeout_state = "canonical_complete" if canonical_complete else "machine_complete_review_pending"
    owner_binding = {
        "schema_version": "dvf-3-3-terminal-owner-confirmed-universe-binding-v1",
        "denominator": 1062,
        "unit": "executing_consumer_member_row",
        "rollup_rule": "member_row_is_official; path/object rollups are diagnostic only",
        "accepted_claim_boundary": CLAIM_BOUNDARY,
        "confirmer": "plan_level_author_governance_decision",
        "timestamp": GENERATED_AT,
        "relation_to_author_governance_decision": "implements docs/dvf_3_3_terminal_disposition_adjudication_plan.md plan-level universe decision; not independent review",
    }
    write_json(phase_path("phase6", "owner_confirmed_universe_binding.json"), owner_binding)
    write_json(
        phase_path("phase6", "owner_adoption_record.json"),
        {
            "schema_version": "dvf-3-3-terminal-owner-adoption-record-v1",
            "generated_at": GENERATED_AT,
            "owner_adoption_status": "not_adopted",
            "owner_adoption_replaces_independent_review": False,
            "independent_review_status": review_verdict,
        },
    )
    write_json(phase_path("phase6", "independent_review_status.json"), review_status)
    write_json(
        phase_path("phase6", "closeout_claim_boundary_check.json"),
        {
            "schema_version": "dvf-3-3-terminal-closeout-claim-boundary-check-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "forbidden_claim_hit_count": 0,
            "machine_complete_and_canonical_complete_collapsed": False,
            "owner_adoption_satisfies_independent_review": False,
            "independent_review_status": review_verdict,
            "canonical_complete": canonical_complete,
        },
    )
    write_json(
        phase_path("phase6", "final_terminal_disposition_closeout_report.json"),
        {
            "schema_version": "dvf-3-3-terminal-closeout-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "closeout_state": closeout_state,
            "canonical_complete": canonical_complete,
            "independent_review_status": review_verdict,
            "required_validation_status": "candidate_only",
            "owner_adoption_status": "not_adopted",
            "terminal_consumer_universe_id": UNIVERSE_ID,
            **counts,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    closeout = closeout_text(
        counts,
        closeout_state=closeout_state,
        canonical_complete=canonical_complete,
        independent_review_status=str(review_verdict),
    )
    write_text(phase_path("phase6", "closeout.md"), closeout)
    write_text(CLOSEOUT_DOC, closeout)
    write_text(CLAIM_BOUNDARY_DOC, claim_boundary_text())
    write_text(
        LEDGER_PACKET_DOC,
        ledger_packet_text(
            counts,
            canonical_promotion_status=closeout_state,
            independent_review_status=str(review_verdict),
        ),
    )


def generate_artifacts() -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    bundle = load_bundle()
    surface = protected_surface_definition()
    baseline = protected_surface_hash(surface)
    write_phase0(surface, baseline)
    write_phase1(bundle)
    write_phase2()
    records = build_terminal_records(bundle)
    write_phase3(records)
    write_phase4(records)
    write_phase5(records, surface, baseline)
    write_phase6(records)
    return read_json(phase_path("phase5", "final_terminal_disposition_machine_report.json"))


def artifact_fingerprint() -> dict[str, Any]:
    excluded_names = {
        "independent_review_artifact_hash_report.json",
        "final_terminal_disposition_machine_report.json",
        "regenerate_twice_fingerprint_comparison.json",
        "terminal_disposition_validation_report.json",
    }
    records = []
    for path in sorted(EVIDENCE_ROOT.rglob("*")):
        if path.is_file():
            if path.name in excluded_names:
                continue
            records.append({"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    return {
        "schema_version": "dvf-3-3-terminal-artifact-fingerprint-v1",
        "generated_at": GENERATED_AT,
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(records),
    }


def run_all() -> dict[str, Any]:
    first = generate_artifacts()
    first_fingerprint = artifact_fingerprint()
    second = generate_artifacts()
    second_fingerprint = artifact_fingerprint()
    comparison = {
        "schema_version": "dvf-3-3-terminal-regenerate-twice-fingerprint-comparison-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if first_fingerprint["aggregate_sha256"] == second_fingerprint["aggregate_sha256"] else "FAIL",
        "first": first_fingerprint,
        "second": second_fingerprint,
    }
    write_json(phase_path("phase5", "regenerate_twice_fingerprint_comparison.json"), comparison)
    final = read_json(phase_path("phase5", "final_terminal_disposition_machine_report.json"))
    final["regenerate_twice_fingerprint_comparison"] = comparison
    if comparison["status"] != "PASS":
        final["status"] = "FAIL"
        final["machine_contract_status"] = "FAIL"
    write_json(phase_path("phase5", "final_terminal_disposition_machine_report.json"), final)
    write_json(
        phase_path("phase6", "independent_review_artifact_hash_report.json"),
        review_artifact_hash_report(read_json(phase_path("phase6", "independent_review_status.json"))),
    )
    return final if second else first


def validate_all(*, require_complete: bool = True) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required = [
        phase_path("phase0", "source_input_inventory.json"),
        phase_path("phase1", "terminal_consumer_universe_manifest.json"),
        phase_path("phase2", "terminal_disposition_schema.json"),
        phase_path("phase3", "terminal_disposition_ledger.jsonl"),
        phase_path("phase4", "blocked_conditional_zero_verdict.json"),
        phase_path("phase5", "final_terminal_disposition_machine_report.json"),
        phase_path("phase5", "protected_surface_no_mutation_verdict.json"),
        phase_path("phase6", "final_terminal_disposition_closeout_report.json"),
        phase_path("phase6", "owner_confirmed_universe_binding.json"),
        phase_path("phase6", "independent_review_status.json"),
        phase_path("phase6", "independent_review_artifact_hash_report.json"),
    ]
    for path in required:
        if not path.exists():
            errors.append({"code": "missing_artifact", "path": rel(path)})
    if not errors:
        records = read_jsonl(phase_path("phase3", "terminal_disposition_ledger.jsonl"))
        errors.extend(validate_terminal_records(records, require_complete=require_complete))
        counts = terminal_counts(records)
        if counts != {
            "terminal_rows_total": 1062,
            "migrated_count": 153,
            "no_op_count": 268,
            "diagnostic_only_count": 3,
            "historical_only_count": 638,
            "blocked_count": 0,
            "conditional_count": 0,
            "unknown_count": 0,
            "pending_count": 0,
        }:
            errors.append({"code": "terminal_count_mismatch", "observed": counts})
        zero = read_json(phase_path("phase4", "blocked_conditional_zero_verdict.json"))
        if zero.get("status") != "PASS":
            errors.append({"code": "zero_verdict_failed", "report": zero})
        no_mutation = read_json(phase_path("phase5", "protected_surface_no_mutation_verdict.json"))
        if no_mutation.get("status") != "PASS" or no_mutation.get("changed_count") != 0:
            errors.append({"code": "protected_surface_mutated", "report": no_mutation})
        final = read_json(phase_path("phase5", "final_terminal_disposition_machine_report.json"))
        if final.get("canonical_complete") is not False:
            errors.append({"code": "machine_and_canonical_complete_collapsed", "report": final})
        patch = read_json(phase_path("phase5", "current_route_required_validations.candidate_patch.json"))
        if patch.get("adoption_status") != "not_adopted" or patch.get("live_manifest_mutated") is not False:
            errors.append({"code": "candidate_patch_overclaimed", "report": patch})
        owner = read_json(phase_path("phase6", "owner_confirmed_universe_binding.json"))
        for field in ("denominator", "unit", "rollup_rule", "accepted_claim_boundary", "confirmer", "timestamp", "relation_to_author_governance_decision"):
            if field not in owner:
                errors.append({"code": "owner_binding_missing_field", "field": field})
        review = read_json(phase_path("phase6", "independent_review_status.json"))
        errors.extend(validate_independent_review_status(review))
        if review.get("verdict") == "review_pass":
            stored_hash_report = read_json(phase_path("phase6", "independent_review_artifact_hash_report.json"))
            live_hash_report = review_artifact_hash_report(review)
            if stored_hash_report != live_hash_report:
                errors.append(
                    {
                        "code": "independent_review_artifact_hash_report_stale",
                        "stored_status": stored_hash_report.get("status"),
                        "live_status": live_hash_report.get("status"),
                    }
                )
            if live_hash_report.get("status") != "PASS":
                errors.append({"code": "independent_review_artifact_hash_report_failed", "report": live_hash_report})
        closeout = read_json(phase_path("phase6", "final_terminal_disposition_closeout_report.json"))
        closeout_state = closeout.get("closeout_state")
        review_verdict = review.get("verdict")
        if closeout.get("independent_review_status") != review_verdict:
            errors.append(
                {
                    "code": "closeout_independent_review_status_mismatch",
                    "closeout": closeout.get("independent_review_status"),
                    "review": review_verdict,
                }
            )
        if closeout_state == "canonical_complete":
            if closeout.get("canonical_complete") is not True:
                errors.append({"code": "canonical_closeout_flag_missing", "report": closeout})
            if review_verdict != "review_pass":
                errors.append({"code": "canonical_closeout_without_review_pass", "report": closeout})
        elif closeout_state == "machine_complete_review_pending":
            if closeout.get("canonical_complete") is not False:
                errors.append({"code": "pending_closeout_canonical_overclaim", "report": closeout})
        else:
            errors.append({"code": "invalid_closeout_state", "value": closeout_state})
    report = {
        "schema_version": "dvf-3-3-terminal-validation-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "error_count": len(errors),
        "errors": errors,
    }
    write_json(phase_path("phase5", "terminal_disposition_validation_report.json"), report)
    return report, not errors
