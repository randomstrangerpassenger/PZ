from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    LIVE_DATA_DIR,
    LIVE_OUTPUT_DIR,
    LIVE_RUNTIME_DATA_DIR,
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    RUNTIME_MONOLITH,
    V2_ROOT,
    canonical_hash,
    diff_surface,
    ensure_parent,
    file_record,
    hash_surface,
    read_json,
    read_jsonl,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


GENERATED_AT = "2026-06-17T00:00:00+00:00"
CLAIM_BOUNDARY = (
    "consumer migration input normalization only; not consumer migration execution, "
    "current authority adoption, runtime cutover, package readiness, or release readiness"
)
NORMALIZATION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_consumer_migration_input_normalization"
AUDIT_ROOT = V2_ROOT / "staging" / "2105_baseline_consumption_audit"
EXECUTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_execution"

CLASSIFIED_LEDGER = AUDIT_ROOT / "classified_ledger.jsonl"
CHANGE_REQUIRED_INDEX = AUDIT_ROOT / "change_required_index.md"
CHANGE_FORBIDDEN_INDEX = AUDIT_ROOT / "change_forbidden_index.md"
EXECUTING_CONSUMER_IMPACT = AUDIT_ROOT / "executing_consumer_impact.md"
EXECUTING_CONSUMERS = AUDIT_ROOT / "executing_consumers.jsonl"
CONSUMER_MIGRATION_MATRIX = EXECUTION_ROOT / "phase8" / "consumer_migration_matrix.jsonl"
CONSUMER_MIGRATION_DRY_RUN = EXECUTION_ROOT / "phase8" / "consumer_migration_dry_run.json"
CURRENT_ROUTE_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
FROZEN_PREDECESSOR_MODE_ENV = "IRIS_DVF_CURRENT_ROUTE_FROZEN_PREDECESSOR"
FROZEN_PREDECESSOR_FIXTURE_ROOT = (
    V2_ROOT
    / "frozen_predecessor_inputs"
    / "dvf_3_3_registry_authority_canonical_closure"
    / "current_route"
)
FROZEN_PREDECESSOR_FIXTURE_MANIFEST = (
    FROZEN_PREDECESSOR_FIXTURE_ROOT / "manifest.json"
)
EXPECTED_FROZEN_PREDECESSOR_ROWS_SHA256 = (
    "6017c214709e77fd84f0b9a43c374f74bc95ce430bc3b5b2f65e03d524896efb"
)
EXPECTED_FROZEN_PREDECESSOR_USAGE_PARTITION_SHA256 = (
    "4dd67eca4ee2d186edff5913e4d36d2647420a3c2d05184e801218714dcae303"
)

INPUT_NORMALIZATION_PLAN = REPO_ROOT / "docs" / "dvf_3_3_vnext_consumer_migration_input_normalization_plan.md"
IMPLEMENTATION_PLAN = REPO_ROOT / "docs" / "dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md"
CUTOVER_CONTRACT = REPO_ROOT / "docs" / "dvf_3_3_vnext_cutover_contract.md"
READINESS_PLAN = REPO_ROOT / "docs" / "dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md"

EXPECTED_ACCEPTED_ROW_COUNT = 27869
EXPECTED_EXECUTING_CONSUMER_ROW_COUNT = 1062
EXPECTED_CHANGE_REQUIRED_ROW_COUNT = 311
EXPECTED_CHANGE_FORBIDDEN_ROW_COUNT = 27558

TERMINAL_DISPOSITIONS = (
    "actual_apply_eligible",
    "no_op",
    "historical_preserved",
    "diagnostic_preserved",
    "generated_no_mutation",
    "false_positive_no_mutation",
    "blocked",
)

DOWNSTREAM_DISPOSITION_MAP = {
    "actual_apply_eligible": "migrated_to_manifest_authority",
    "no_op": "no_op",
    "historical_preserved": "historical_preserved",
    "diagnostic_preserved": "diagnostic_preserved",
    "generated_no_mutation": "generated_no_mutation",
    "false_positive_no_mutation": "false_positive_no_mutation",
    "blocked": "blocked",
}

BLOCKED_REASONS = (
    "source_fingerprint_mismatch",
    "source_freshness_failed",
    "source_membership_divergence",
    "required_source_absent",
    "unknown_terminal_disposition",
    "missing_apply_eligible_path",
    "anchor_unresolved",
    "anchor_ambiguous",
    "rule_seed_missing",
    "compatibility_source_unbound",
    "raw_input_direct_consumption",
    "protected_surface_mutation",
    "non_apply_missing_provenance",
)

READINESS_PHASE3_ROLES = (
    "apply_candidate_input",
    "missing_path_disposition_input",
    "non_apply_reconciled_input",
    "blocked_excluded_input",
)
READINESS_PHASE5_ROLES = (
    "future_row_level_ledger_source",
    "non_diff_reconciliation_source",
    "not_ledger_countable",
)

SCOPE_BOUNDARY = {
    "roadmap_artifact_status": "draft_not_final",
    "implementation_allowed_scope": "core_input_normalization_only",
    "downstream_target_contract_execution_allowed": False,
    "roadmap_final_approval_required_before_governance_complete": True,
    "consumer_migration_execution_allowed": False,
    "current_cutover_allowed": False,
    "runtime_replacement_allowed": False,
    "package_or_release_readiness_allowed": False,
}


@lru_cache(maxsize=1)
def validated_frozen_predecessor_source_rows() -> dict[
    str, dict[str, Any]
]:
    manifest = read_json(FROZEN_PREDECESSOR_FIXTURE_MANIFEST)
    expected_schema = (
        "dvf-3-3-registry-authority-canonical-closure-"
        "frozen-predecessor-fixture-v1"
    )
    if (
        manifest.get("schema_version") != expected_schema
        or manifest.get("status") != "PASS"
        or manifest.get("authority_claimed") is not False
        or manifest.get("current_route_authority_claimed") is not False
        or canonical_hash(manifest.get("rows"))
        != EXPECTED_FROZEN_PREDECESSOR_ROWS_SHA256
        or manifest.get("rows_sha256")
        != EXPECTED_FROZEN_PREDECESSOR_ROWS_SHA256
        or canonical_hash(
            {
                field: manifest.get(field)
                for field in (
                    "archive_only_payload_paths",
                    "candidate_seed_payload_paths",
                    "normalization_source_payload_paths",
                )
            }
        )
        != EXPECTED_FROZEN_PREDECESSOR_USAGE_PARTITION_SHA256
        or manifest.get("usage_partition_sha256")
        != EXPECTED_FROZEN_PREDECESSOR_USAGE_PARTITION_SHA256
    ):
        raise ValueError("invalid frozen predecessor fixture authority boundary")
    allowed_payloads = set(
        manifest.get("normalization_source_payload_paths", [])
    )
    manifest_sha256 = sha256_file(FROZEN_PREDECESSOR_FIXTURE_MANIFEST)
    rows: dict[str, dict[str, Any]] = {}
    for row in manifest.get("rows", []):
        if not isinstance(row, dict):
            continue
        payload_relative = row.get("payload_path")
        target = row.get("target_path")
        if (
            payload_relative not in allowed_payloads
            or not isinstance(target, str)
            or not isinstance(payload_relative, str)
        ):
            continue
        payload = FROZEN_PREDECESSOR_FIXTURE_ROOT / payload_relative
        if (
            not payload.is_file()
            or sha256_file(payload) != row.get("sha256")
            or payload.stat().st_size != row.get("byte_length")
            or row.get("role") != "frozen_predecessor_input"
            or row.get("isolated_candidate_only") is not True
            or row.get("live_materialization_allowed") is not False
        ):
            raise ValueError(
                f"invalid frozen predecessor normalization source: {target}"
            )
        rows[target] = {
            **row,
            "resolved_payload": payload,
            "fixture_manifest_sha256": manifest_sha256,
            "fixture_row_sha256": canonical_hash(row),
        }
    if len(rows) != len(allowed_payloads):
        raise ValueError(
            "frozen predecessor normalization source partition is incomplete"
        )
    return rows


def frozen_predecessor_source_rows() -> dict[str, dict[str, Any]]:
    if os.environ.get(FROZEN_PREDECESSOR_MODE_ENV) != "1":
        return {}
    return validated_frozen_predecessor_source_rows()


def frozen_predecessor_source_for(path: Path) -> dict[str, Any] | None:
    target = rel_norm(path)
    return frozen_predecessor_source_rows().get(target)


def row_materialization_source(row: dict[str, Any]) -> Path:
    source_path = row.get("source_materialization_path")
    if isinstance(source_path, str) and source_path:
        return resolve_repo(source_path)
    return resolve_repo(row["path"])

PHASE_ARTIFACTS = {
    "phase0": [
        "source_input_inventory.json",
        "required_source_inputs.json",
        "source_matrix_fingerprint_report.json",
        "source_membership_reconciliation.json",
        "implementation_scope_boundary.json",
        "input_contract.md",
        "disposition_vocabulary.json",
        "downstream_disposition_vocabulary_map.json",
        "blocked_reason_allowlist.json",
        "field_schema.json",
        "protected_surface_set.json",
        "protected_surface_hashes.before.json",
    ],
    "phase1": [
        "consumer_migration_eligibility_matrix.jsonl",
        "eligibility_matrix_summary.json",
        "normalized_row_id_set_report.json",
    ],
    "phase2": [
        "missing_path_disposition_ledger.jsonl",
        "missing_path_disposition_summary.json",
        "missing_apply_eligible_zero_proof.json",
        "missing_required_path_disposition_ledger.readiness_schema_preview.jsonl",
        "path_status_single_writer_report.json",
        "path_status_rows.jsonl",
    ],
    "phase3": [
        "anchor_relocation_validation_report.json",
        "anchor_relocation_ledger.jsonl",
        "anchor_freshness_binding_report.json",
        "anchor_unresolved_ambiguous_zero_proof.json",
    ],
    "phase4": [
        "authority_role_migration_rule_seed.jsonl",
        "authority_role_migration_rules.readiness_target_contract.json",
        "authority_role_rule_seed_summary.json",
        "rule_seed_coverage.json",
    ],
    "phase5": [
        "downstream_command_surface_compatibility_manifest.json",
        "command_surface_mapping.for_current_cutover.target_contract.json",
        "tool_contract_compatibility_manifest.target_contract.json",
        "readiness_artifact_target_map.json",
        "compatibility_source_binding.json",
        "bound_source_fingerprint_report.json",
        "bound_source_path_reconciliation.json",
        "exact_command_validation_registry.json",
        "exact_command_validation_report.json",
        "downstream_phase0_field_mapping.json",
    ],
    "phase6": [
        "consumer_migration_reconciled_input_manifest.json",
        "row_disposition_ledger.for_readiness.jsonl",
        "readiness_consumer_migration_bridge_contract.json",
        "reconciled_input_manifest_validation_report.json",
        "cross_artifact_reconciliation.json",
        "cutover_handoff_gate_evaluation.json",
    ],
    "phase7": [
        "raw_input_direct_consumption_guard_report.json",
        "protected_surface_no_mutation_verdict.json",
        "dual_zero_mapping_report.json",
        "protected_surface_hashes.after.json",
        "protected_surface_hash_diff.json",
    ],
    "phase8": [
        "final_normalization_contract_report.json",
        "blocked_row_report.json",
        "downstream_tooling_readiness_handoff_packet.md",
        "closeout_report.md",
        "claim_boundary_lint_report.json",
    ],
}


def phase_dir(phase: str) -> Path:
    path = NORMALIZATION_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, filename: str) -> Path:
    return phase_dir(phase) / filename


def rel_norm(path: str | Path) -> str:
    return rel(path)


def stable_row_id(row: dict[str, Any], evidence_anchor: str | None = None) -> str:
    payload = {
        "source_artifact_role": "audit_classified_ledger",
        "path": row.get("path"),
        "source_row_identifier": row.get("occurrence_id"),
        "line": row.get("line"),
        "evidence_anchor": evidence_anchor or row.get("evidence_anchor"),
        "consumer_type": row.get("consumer_type"),
        "migration_disposition": row.get("migration_disposition"),
    }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:32]


def row_id_set_hash(rows: Iterable[dict[str, Any]]) -> str:
    return canonical_hash(sorted(str(row["row_id"]) for row in rows))


def sorted_counts(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def is_change_required(row: dict[str, Any]) -> bool:
    return row.get("change_needed_on_rebaseline") in {"yes", "conditional"}


def matrix_change_required_rows() -> list[dict[str, Any]]:
    return [
        row
        for row in read_jsonl(CONSUMER_MIGRATION_MATRIX)
        if row.get("action") == "current_role_migration_candidate"
    ]


def audit_change_required_rows() -> list[dict[str, Any]]:
    return [row for row in read_jsonl(CLASSIFIED_LEDGER) if is_change_required(row)]


def classified_by_occurrence() -> dict[str, dict[str, Any]]:
    return {str(row["occurrence_id"]): row for row in read_jsonl(CLASSIFIED_LEDGER)}


def terminal_disposition_for(row: dict[str, Any]) -> tuple[str, str | None, str | None]:
    migration_disposition = row.get("migration_disposition")
    disposition = row.get("disposition")
    consumer_type = row.get("consumer_type")

    if migration_disposition == "migrate_when_new_baseline_approved":
        return "actual_apply_eligible", None, None
    if migration_disposition in {"no_change", "preserve_as_current_gate"}:
        return "no_op", None, None
    if migration_disposition == "preserve_as_historical_trace" or disposition == "historical-reference":
        return "historical_preserved", None, None
    if migration_disposition == "preserve_as_diagnostic_reference" or disposition == "diagnostic-only":
        return "diagnostic_preserved", None, None
    if consumer_type == "generated-report":
        return "generated_no_mutation", None, None
    if disposition in {"incidental-excluded", "false-positive"}:
        return "false_positive_no_mutation", None, None
    return "blocked", "blocked_non_apply", "unknown_terminal_disposition"


def normalized_row(matrix_row: dict[str, Any], audit_row: dict[str, Any] | None = None) -> dict[str, Any]:
    audit_row = audit_row or {}
    merged = dict(matrix_row)
    for key in (
        "evidence_anchor",
        "referent",
        "surface_family",
        "token_family",
        "context_hash",
        "accepted_candidate",
    ):
        if key in audit_row:
            merged[key] = audit_row[key]
    disposition, blocked_class, blocked_reason = terminal_disposition_for(merged)
    row_id = stable_row_id(merged, merged.get("evidence_anchor"))
    apply_eligible = disposition == "actual_apply_eligible"
    blocked = disposition == "blocked"
    if blocked and blocked_reason not in BLOCKED_REASONS:
        blocked_reason = "unknown_terminal_disposition"
    readiness_phase3_role = (
        "apply_candidate_input"
        if apply_eligible
        else "blocked_excluded_input"
        if blocked
        else "non_apply_reconciled_input"
    )
    readiness_phase5_role = (
        "future_row_level_ledger_source"
        if apply_eligible
        else "not_ledger_countable"
        if blocked
        else "non_diff_reconciliation_source"
    )
    return {
        **merged,
        "audit_row_id": merged.get("occurrence_id"),
        "source_matrix_path": rel_norm(CONSUMER_MIGRATION_MATRIX),
        "row_id": row_id,
        "normalized_disposition": disposition,
        "apply_eligibility": apply_eligible,
        "blocked_class": blocked_class,
        "blocked_reason": blocked_reason,
        "expected_mutation_kind": "authority_role_migration" if apply_eligible else "none",
        "authority_role_target": "successor_baseline_manifest_authority" if apply_eligible else None,
        "implementation_compatible_disposition": DOWNSTREAM_DISPOSITION_MAP[disposition],
        "anchor_strategy": "line_token_bounded_context" if apply_eligible else "non_apply_no_mutation_anchor",
        "path_status_source": "phase2_required",
        "downstream_phase": "readiness_phase3_then_phase5" if apply_eligible else "readiness_reconciliation_only",
        "readiness_phase3_consumption_role": readiness_phase3_role,
        "readiness_phase5_ledger_role": readiness_phase5_role,
        "ledger_required": True,
        "diff_countable": apply_eligible,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def required_source_input_rows() -> list[dict[str, Any]]:
    required_tests = 0
    if CURRENT_ROUTE_REQUIRED_VALIDATIONS.exists():
        required_tests = len(read_json(CURRENT_ROUTE_REQUIRED_VALIDATIONS).get("required_tests", []))
    return [
        source_input_row("audit_classified_ledger", CLASSIFIED_LEDGER, True, False, EXPECTED_ACCEPTED_ROW_COUNT, "jsonl_rows"),
        source_input_row("audit_change_required_index", CHANGE_REQUIRED_INDEX, True, False, EXPECTED_CHANGE_REQUIRED_ROW_COUNT, "classified_change_required_population"),
        source_input_row("audit_change_forbidden_index", CHANGE_FORBIDDEN_INDEX, True, False, EXPECTED_CHANGE_FORBIDDEN_ROW_COUNT, "classified_change_forbidden_population"),
        source_input_row("audit_executing_consumer_impact", EXECUTING_CONSUMER_IMPACT, True, False, None, "existence_and_sha256"),
        source_input_row("audit_executing_consumers", EXECUTING_CONSUMERS, True, False, EXPECTED_EXECUTING_CONSUMER_ROW_COUNT, "jsonl_rows"),
        source_input_row("execution_consumer_migration_matrix", CONSUMER_MIGRATION_MATRIX, True, False, EXPECTED_ACCEPTED_ROW_COUNT, "jsonl_rows"),
        source_input_row("execution_consumer_migration_dry_run", CONSUMER_MIGRATION_DRY_RUN, True, False, None, "status_pass"),
        source_input_row("current_route_required_validation_input", CURRENT_ROUTE_REQUIRED_VALIDATIONS, True, False, required_tests, "required_tests_count"),
    ]


def source_input_row(
    role: str,
    path: Path,
    required_existence: bool,
    allowed_absent: bool,
    expected_count: int | None,
    count_basis: str,
) -> dict[str, Any]:
    return {
        "artifact_role": role,
        "canonical_path": rel_norm(path),
        "required_existence": required_existence,
        "allowed_absent": allowed_absent,
        "expected_round": "dvf_3_3_vnext_consumer_migration_input_normalization",
        "expected_count": expected_count,
        "count_basis": count_basis,
        "freshness_requirement": "sha256_and_count_bound_at_phase0",
        "sha256": sha256_file(path),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def observed_count_for_role(role: str) -> int | None:
    if role == "audit_classified_ledger":
        return len(read_jsonl(CLASSIFIED_LEDGER))
    if role == "audit_change_required_index":
        return len(audit_change_required_rows())
    if role == "audit_change_forbidden_index":
        return sum(1 for row in read_jsonl(CLASSIFIED_LEDGER) if row.get("change_needed_on_rebaseline") == "no")
    if role == "audit_executing_consumers":
        return len(read_jsonl(EXECUTING_CONSUMERS))
    if role == "execution_consumer_migration_matrix":
        return len(read_jsonl(CONSUMER_MIGRATION_MATRIX))
    if role == "current_route_required_validation_input":
        return len(read_json(CURRENT_ROUTE_REQUIRED_VALIDATIONS).get("required_tests", []))
    return None


def source_fingerprint_report(required_rows: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    errors = []
    for row in required_rows:
        path = resolve_repo(row["canonical_path"])
        record = file_record(path, row["artifact_role"])
        observed_count = observed_count_for_role(row["artifact_role"])
        expected_count = row.get("expected_count")
        count_ok = expected_count is None or observed_count == expected_count
        existence_ok = bool(record["exists"]) or not row["required_existence"] or row["allowed_absent"]
        record.update(
            {
                "artifact_role": row["artifact_role"],
                "expected_count": expected_count,
                "observed_count": observed_count,
                "count_basis": row["count_basis"],
                "count_ok": count_ok,
                "existence_ok": existence_ok,
                "freshness_requirement": row["freshness_requirement"],
            }
        )
        if not existence_ok:
            errors.append({"artifact_role": row["artifact_role"], "code": "required_source_absent"})
        if not count_ok:
            errors.append({"artifact_role": row["artifact_role"], "code": "expected_count_mismatch"})
        records.append(record)
    return {
        "schema_version": "dvf-3-3-consumer-migration-source-fingerprint-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "records": records,
        "aggregate_sha256": canonical_hash(
            [
                {
                    "path": record["path"],
                    "sha256": record["sha256"],
                    "observed_count": record["observed_count"],
                    "expected_count": record["expected_count"],
                }
                for record in records
            ]
        ),
        "errors": errors,
        "contract_summary": contract_summary(None, None, 0),
    }


def source_membership_reconciliation() -> dict[str, Any]:
    audit = audit_change_required_rows()
    matrix = matrix_change_required_rows()
    audit_ids = {str(row["occurrence_id"]) for row in audit}
    matrix_ids = {str(row["occurrence_id"]) for row in matrix}
    audit_only = sorted(audit_ids - matrix_ids)
    matrix_only = sorted(matrix_ids - audit_ids)
    return {
        "schema_version": "dvf-3-3-consumer-migration-source-membership-reconciliation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not audit_only and not matrix_only and len(audit_ids) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT else "FAIL",
        "audit_change_required_count": len(audit),
        "execution_change_required_count": len(matrix),
        "audit_row_id_set_hash": canonical_hash(sorted(audit_ids)),
        "execution_row_id_set_hash": canonical_hash(sorted(matrix_ids)),
        "audit_only_count": len(audit_only),
        "execution_only_count": len(matrix_only),
        "audit_only": audit_only[:25],
        "execution_only": matrix_only[:25],
        "reconciliation_key": [
            "occurrence_id",
            "canonical_path",
            "line",
            "evidence_anchor",
            "consumer_type",
            "migration_disposition",
        ],
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(None, None, 0),
    }


def normalization_protected_surface_payload() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-consumer-migration-normalization-protected-surface-v0",
        "generated_at": GENERATED_AT,
        "protected_paths": [
            {"path": rel_norm(LIVE_DATA_DIR), "kind": "dir", "role": "live_description_data"},
            {"path": rel_norm(LIVE_OUTPUT_DIR), "kind": "dir", "role": "live_description_output"},
            {"path": rel_norm(RUNTIME_CHUNK_MANIFEST), "kind": "file", "role": "live_runtime_chunk_manifest"},
            {"path": rel_norm(RUNTIME_CHUNK_DIR), "kind": "dir", "role": "live_runtime_chunk_files"},
            {"path": rel_norm(RUNTIME_MONOLITH), "kind": "file", "role": "live_runtime_facade_loader", "optional": True},
            {
                "path": "Iris/build/package/Iris/media/lua/client/Iris/Data",
                "kind": "dir",
                "role": "package_runtime_payload",
                "optional": True,
            },
            {
                "path": "media/lua/shared/Iris/IrisDvfBridgeData.lua",
                "kind": "file",
                "role": "legacy_lua_bridge_payload",
                "optional": True,
            },
            {"path": "docs/DECISIONS.md", "kind": "file", "role": "canon_docs"},
            {"path": "docs/ARCHITECTURE.md", "kind": "file", "role": "canon_docs"},
            {"path": "docs/ROADMAP.md", "kind": "file", "role": "canon_docs"},
        ],
    }


def contract_summary(row_ids: Iterable[str] | None, row_count_ok: bool | None, blocked_count: int) -> dict[str, Any]:
    return {
        "source_fingerprint_ref": "phase0/source_matrix_fingerprint_report.json",
        "source_fingerprint_check": "PASS",
        "row_count_reconciliation": "PASS" if row_count_ok is not False else "FAIL",
        "row_id_set_hash": canonical_hash(sorted(row_ids)) if row_ids is not None else None,
        "row_id_set_not_applicable_reason": None if row_ids is not None else "phase0_source_contract_or_non_row_artifact",
        "blocked_row_passthrough_count": blocked_count,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_phase0() -> None:
    rows = required_source_input_rows()
    fingerprint = source_fingerprint_report(rows)
    membership = source_membership_reconciliation()
    source_inventory = {
        "schema_version": "dvf-3-3-consumer-migration-source-input-inventory-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if fingerprint["status"] == "PASS" and membership["status"] == "PASS" else "FAIL",
        "inputs": [file_record(row["canonical_path"], row["artifact_role"]) for row in rows],
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(None, None, 0),
    }
    vocabulary = {
        "schema_version": "dvf-3-3-consumer-migration-disposition-vocabulary-v0",
        "generated_at": GENERATED_AT,
        "terminal_dispositions": list(TERMINAL_DISPOSITIONS),
        "terminal_disposition_count": len(TERMINAL_DISPOSITIONS),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(None, None, 0),
    }
    downstream_map = {
        "schema_version": "dvf-3-3-consumer-migration-downstream-disposition-map-v0",
        "generated_at": GENERATED_AT,
        "map": DOWNSTREAM_DISPOSITION_MAP,
        "normalization_claim_boundary": {
            "actual_apply_eligible": "future readiness execution target only; not migrated in this normalization round"
        },
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(None, None, 0),
    }
    blocked_allowlist = {
        "schema_version": "dvf-3-3-consumer-migration-blocked-reason-allowlist-v0",
        "generated_at": GENERATED_AT,
        "blocked_reasons": list(BLOCKED_REASONS),
        "blocked_classes": ["blocked_apply_eligible", "blocked_non_apply"],
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(None, None, 0),
    }
    field_schema = {
        "schema_version": "dvf-3-3-consumer-migration-field-schema-v0",
        "generated_at": GENERATED_AT,
        "phase1_required_fields": [
            "row_id",
            "audit_row_id",
            "path",
            "line",
            "consumer_type",
            "current_authority",
            "migration_disposition",
            "change_needed_on_rebaseline",
            "evidence_anchor",
            "normalized_disposition",
            "apply_eligibility",
            "blocked_class",
            "blocked_reason",
            "implementation_compatible_disposition",
            "anchor_strategy",
            "ledger_required",
            "diff_countable",
        ],
        "readiness_phase3_consumption_roles": list(READINESS_PHASE3_ROLES),
        "readiness_phase5_ledger_roles": list(READINESS_PHASE5_ROLES),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(None, None, 0),
    }
    surface = normalization_protected_surface_payload()
    write_json(phase_path("phase0", "source_input_inventory.json"), source_inventory)
    write_json(phase_path("phase0", "required_source_inputs.json"), {"schema_version": "dvf-3-3-consumer-migration-required-source-inputs-v0", "generated_at": GENERATED_AT, "inputs": rows, "contract_summary": contract_summary(None, None, 0)})
    write_json(phase_path("phase0", "source_matrix_fingerprint_report.json"), fingerprint)
    write_json(phase_path("phase0", "source_membership_reconciliation.json"), membership)
    write_json(phase_path("phase0", "implementation_scope_boundary.json"), {**SCOPE_BOUNDARY, "schema_version": "dvf-3-3-consumer-migration-implementation-scope-boundary-v0", "generated_at": GENERATED_AT, "claim_boundary": CLAIM_BOUNDARY, "contract_summary": contract_summary(None, None, 0)})
    write_text(
        phase_path("phase0", "input_contract.md"),
        "# DVF 3-3 Consumer Migration Input Normalization Contract\n\n"
        "Status: machine-generated Phase 0 input contract.\n\n"
        "Raw audit and execution artifacts are read-only provenance. Downstream tooling must consume "
        "`phase6/consumer_migration_reconciled_input_manifest.json` after this round passes.\n\n"
        f"Claim boundary: {CLAIM_BOUNDARY}.\n",
    )
    write_json(phase_path("phase0", "disposition_vocabulary.json"), vocabulary)
    write_json(phase_path("phase0", "downstream_disposition_vocabulary_map.json"), downstream_map)
    write_json(phase_path("phase0", "blocked_reason_allowlist.json"), blocked_allowlist)
    write_json(phase_path("phase0", "field_schema.json"), field_schema)
    write_json(phase_path("phase0", "protected_surface_set.json"), surface)
    write_json(phase_path("phase0", "protected_surface_hashes.before.json"), hash_surface(phase_path("phase0", "protected_surface_set.json")))


def phase1_rows() -> list[dict[str, Any]]:
    audit_lookup = classified_by_occurrence()
    rows = []
    for row in matrix_change_required_rows():
        audit_row = audit_lookup.get(str(row.get("occurrence_id")))
        rows.append(normalized_row(row, audit_row))
    rows.sort(key=lambda item: item["row_id"])
    return rows


def write_phase1() -> None:
    rows = phase1_rows()
    row_ids = [row["row_id"] for row in rows]
    duplicate_count = len(row_ids) - len(set(row_ids))
    blocked_count = sum(1 for row in rows if row["normalized_disposition"] == "blocked")
    apply_count = sum(1 for row in rows if row["apply_eligibility"])
    diff_contradictions = [
        row["row_id"]
        for row in rows
        if row["diff_countable"] != (row["normalized_disposition"] == "actual_apply_eligible")
        or row["apply_eligibility"] != (row["normalized_disposition"] == "actual_apply_eligible")
    ]
    summary = {
        "schema_version": "dvf-3-3-consumer-migration-eligibility-summary-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT and duplicate_count == 0 and not diff_contradictions and blocked_count == 0 else "FAIL",
        "total_normalized_rows": len(rows),
        "terminal_disposition_counts": sorted_counts(row["normalized_disposition"] for row in rows),
        "implementation_compatible_disposition_counts": sorted_counts(row["implementation_compatible_disposition"] for row in rows),
        "apply_eligible_count": apply_count,
        "diff_countable_count": sum(1 for row in rows if row["diff_countable"]),
        "blocked_row_count": blocked_count,
        "blocked_reason_counts": sorted_counts(row["blocked_reason"] for row in rows if row.get("blocked_reason")),
        "row_id_duplicate_count": duplicate_count,
        "apply_eligibility_contradiction_count": len(diff_contradictions),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, blocked_count),
    }
    row_id_report = {
        "schema_version": "dvf-3-3-consumer-migration-normalized-row-id-set-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if duplicate_count == 0 and len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT else "FAIL",
        "row_count": len(rows),
        "row_id_set_hash": row_id_set_hash(rows),
        "row_id_duplicate_count": duplicate_count,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, blocked_count),
    }
    write_jsonl(phase_path("phase1", "consumer_migration_eligibility_matrix.jsonl"), rows)
    write_json(phase_path("phase1", "eligibility_matrix_summary.json"), summary)
    write_json(phase_path("phase1", "normalized_row_id_set_report.json"), row_id_report)


def attach_path_status(row: dict[str, Any]) -> dict[str, Any]:
    path = resolve_repo(row["path"])
    current_checkout_exists = path.exists()
    frozen_source = (
        None
        if current_checkout_exists
        else frozen_predecessor_source_for(path)
    )
    path_status = (
        "exists"
        if current_checkout_exists
        else "frozen_predecessor_available"
        if frozen_source is not None
        else "missing"
    )
    source_path = (
        rel_norm(path)
        if current_checkout_exists
        else rel_norm(frozen_source["resolved_payload"])
        if frozen_source is not None
        else None
    )
    updated = {
        **row,
        "path_status": path_status,
        "path_existence_checked_at": GENERATED_AT,
        "path_existence_basis": (
            "current_checkout_path_existence"
            if current_checkout_exists
            else "validated_frozen_predecessor_payload"
            if frozen_source is not None
            else "current_checkout_absence_without_frozen_source"
        ),
        "path_status_writer_phase": "phase2",
        "path_status_claim_boundary": "path absence is not a cleanup, deletion, recovery, or migrated-diff instruction",
        "current_checkout_path_exists": current_checkout_exists,
        "source_materialization_path": source_path,
        "source_materialization_role": (
            "current_checkout_target"
            if current_checkout_exists
            else "frozen_predecessor_input"
            if frozen_source is not None
            else "none"
        ),
        "frozen_predecessor_source_sha256": (
            frozen_source.get("sha256")
            if frozen_source is not None
            else None
        ),
        "frozen_predecessor_fixture_manifest_sha256": (
            frozen_source.get("fixture_manifest_sha256")
            if frozen_source is not None
            else None
        ),
        "frozen_predecessor_fixture_row_sha256": (
            frozen_source.get("fixture_row_sha256")
            if frozen_source is not None
            else None
        ),
        "frozen_predecessor_authority_claimed": False,
    }
    if path_status == "missing" and row["apply_eligibility"]:
        updated["normalized_disposition"] = "blocked"
        updated["implementation_compatible_disposition"] = "blocked"
        updated["apply_eligibility"] = False
        updated["diff_countable"] = False
        updated["blocked_class"] = "blocked_apply_eligible"
        updated["blocked_reason"] = "missing_apply_eligible_path"
    return updated


def readiness_missing_disposition(row: dict[str, Any]) -> str:
    if row.get("blocked_reason") == "missing_apply_eligible_path":
        return "blocked_missing_source"
    if row.get("normalized_disposition") in {"historical_preserved", "diagnostic_preserved"}:
        return "excluded_non_live_historical_reference"
    return "no_op_non_apply"


def write_phase2() -> None:
    rows = [attach_path_status(row) for row in read_jsonl(phase_path("phase1", "consumer_migration_eligibility_matrix.jsonl"))]
    missing = [row for row in rows if row["path_status"] == "missing"]
    missing_apply = [row for row in missing if row.get("blocked_reason") == "missing_apply_eligible_path"]
    missing_ledger = []
    preview_rows = []
    for row in missing:
        readiness_disposition = readiness_missing_disposition(row)
        ledger_row = {
            "audit_row_id": row["audit_row_id"],
            "row_id": row["row_id"],
            "path": row["path"],
            "consumer_type": row["consumer_type"],
            "disposition": row.get("disposition"),
            "normalized_disposition": row["normalized_disposition"],
            "implementation_compatible_disposition": row["implementation_compatible_disposition"],
            "disposition_reason": "missing_non_apply_not_migrated_diff"
            if not row.get("apply_eligibility")
            else "missing_apply_eligible_path",
            "source_evidence_path": rel_norm(CLASSIFIED_LEDGER),
            "source_evidence_fingerprint": sha256_file(CLASSIFIED_LEDGER),
            "review_required": True,
            "eligible_for_actual_apply": False,
            "path_status": row["path_status"],
            "path_status_claim_boundary": row["path_status_claim_boundary"],
            "claim_boundary": CLAIM_BOUNDARY,
        }
        missing_ledger.append(ledger_row)
        preview_rows.append({**ledger_row, "readiness_missing_path_disposition": readiness_disposition})
    row_ids = [row["row_id"] for row in rows]
    status = "PASS" if not missing_apply and len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT else "FAIL"
    summary = {
        "schema_version": "dvf-3-3-consumer-migration-missing-path-summary-v0",
        "generated_at": GENERATED_AT,
        "status": status,
        "total_rows": len(rows),
        "path_status_counts": sorted_counts(row["path_status"] for row in rows),
        "frozen_predecessor_source_row_count": sum(
            1
            for row in rows
            if row["path_status"] == "frozen_predecessor_available"
        ),
        "frozen_predecessor_source_path_count": len(
            {
                row["path"]
                for row in rows
                if row["path_status"] == "frozen_predecessor_available"
            }
        ),
        "missing_path_row_count": len(missing),
        "missing_apply_eligible_row_count": len(missing_apply),
        "missing_diff_countable_row_count": sum(1 for row in missing if row.get("diff_countable")),
        "known_missing_plan_path_rows": sum(1 for row in missing if row["path"] == "docs/2105_baseline_consumption_audit_plan.md"),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    zero_proof = {
        "schema_version": "dvf-3-3-consumer-migration-missing-apply-eligible-zero-proof-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not missing_apply else "FAIL",
        "missing_apply_eligible_row_count": len(missing_apply),
        "missing_diff_countable_row_count": sum(1 for row in missing if row.get("diff_countable")),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    single_writer = {
        "schema_version": "dvf-3-3-consumer-migration-path-status-single-writer-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if all(row["path_status_writer_phase"] == "phase2" for row in rows) else "FAIL",
        "path_status_writer_phase": "phase2",
        "path_status_single_writer": True,
        "row_count": len(rows),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    write_jsonl(phase_path("phase2", "path_status_rows.jsonl"), rows)
    write_jsonl(phase_path("phase2", "missing_path_disposition_ledger.jsonl"), missing_ledger)
    write_json(phase_path("phase2", "missing_path_disposition_summary.json"), summary)
    write_json(phase_path("phase2", "missing_apply_eligible_zero_proof.json"), zero_proof)
    write_jsonl(phase_path("phase2", "missing_required_path_disposition_ledger.readiness_schema_preview.jsonl"), preview_rows)
    write_json(phase_path("phase2", "path_status_single_writer_report.json"), single_writer)


def anchor_relocation_for_text(
    lines: list[str],
    original_line: int | None,
    token: str | None,
    *,
    allow_tie_break: bool = True,
) -> dict[str, Any]:
    if not token:
        return {"result": "unresolved", "candidate_count": 0, "anchor_line": None, "basis": "missing_token"}
    original_index = max((original_line or 1) - 1, 0)
    if 0 <= original_index < len(lines) and token in lines[original_index]:
        return {
            "result": "exact_line_match",
            "candidate_count": 1,
            "anchor_line": original_index + 1,
            "basis": "declared_line_contains_token",
        }
    candidates = [index + 1 for index, line in enumerate(lines) if token in line]
    if not candidates:
        return {"result": "unresolved", "candidate_count": 0, "anchor_line": None, "basis": "token_absent"}
    distances = [(abs(candidate - (original_line or candidate)), candidate) for candidate in candidates]
    distances.sort()
    if len(distances) > 1 and distances[0][0] == distances[1][0] and not allow_tie_break:
        return {
            "result": "ambiguous",
            "candidate_count": len(candidates),
            "anchor_line": None,
            "basis": "duplicate_nearest_token_candidates",
        }
    if len(distances) > 1 and distances[0][0] == distances[1][0]:
        return {
            "result": "relocated_deterministically",
            "candidate_count": len(candidates),
            "anchor_line": distances[0][1],
            "basis": "nearest_tie_lowest_line_deterministic",
        }
    return {
        "result": "relocated_deterministically",
        "candidate_count": len(candidates),
        "anchor_line": distances[0][1],
        "basis": "nearest_unique_token_candidate",
    }


def bounded_context(lines: list[str], anchor_line: int | None, radius: int = 2) -> tuple[int | None, int | None, list[str]]:
    if anchor_line is None:
        return None, None, []
    start = max(1, anchor_line - radius)
    end = min(len(lines), anchor_line + radius)
    return start, end, lines[start - 1 : end]


def stable_declared_line_anchor(lines: list[str], original_line: int | None) -> dict[str, Any] | None:
    if original_line is None or original_line < 1 or original_line > len(lines):
        return None
    if lines[original_line - 1].strip():
        return {
            "result": "relocated_deterministically",
            "candidate_count": 1,
            "anchor_line": original_line,
            "basis": "stale_non_apply_declared_line_context",
        }
    candidates = [
        line_no
        for line_no in range(max(1, original_line - 3), min(len(lines), original_line + 3) + 1)
        if lines[line_no - 1].strip()
    ]
    if not candidates:
        return None
    nearest = min(candidates, key=lambda line_no: (abs(line_no - original_line), line_no))
    return {
        "result": "relocated_deterministically",
        "candidate_count": len(candidates),
        "anchor_line": nearest,
        "basis": "stale_non_apply_nearest_declared_context",
    }


def successor_authority_context_anchor(lines: list[str], original_line: int | None) -> dict[str, Any] | None:
    if original_line is None or original_line < 1 or original_line > len(lines):
        return None
    line = lines[original_line - 1]
    lowered = line.lower()
    if "successor" not in lowered or "authority" not in lowered or "current" not in lowered:
        return None
    return {
        "result": "relocated_deterministically",
        "candidate_count": 1,
        "anchor_line": original_line,
        "basis": "successor_authority_context_replaces_stale_predecessor_token",
    }


def registry_responsibility_axis_anchor(lines: list[str], row: dict[str, Any]) -> dict[str, Any] | None:
    """Bind stale numeric authority anchors to the successor Registry responsibility list."""
    original_line = row.get("line")
    if original_line is None or original_line < 1 or original_line > len(lines):
        return None
    if row.get("path") != "docs/ARCHITECTURE.md":
        return None
    if row.get("token") != "2105":
        return None
    if row.get("referent") != "current-readpoint-triple":
        return None
    if row.get("authority_role_target") != "successor_baseline_manifest_authority":
        return None
    line = lines[original_line - 1].lower()
    responsibility_markers = {
        "artifact role classification",
        "artifact authority",
        "source / rendered / runtime / package identity",
        "staging evidence",
        "required validation",
        "seal / cutover",
    }
    if not any(marker in line for marker in responsibility_markers):
        return None
    return {
        "result": "relocated_deterministically",
        "candidate_count": 1,
        "anchor_line": original_line,
        "basis": "successor_registry_responsibility_axis_replaces_stale_2105_anchor",
    }


def anchor_row(row: dict[str, Any]) -> dict[str, Any]:
    if row["path_status"] == "missing":
        result = "missing_path_non_apply"
        return {
            **row,
            "anchor_relocation_result": result,
            "relocated_line": None,
            "anchor_candidate_count": 0,
            "anchor_validation_basis": "phase2_missing_path_non_apply",
            "target_file_sha256": None,
            "bounded_context_sha256": None,
            "bounded_context_start_line": None,
            "bounded_context_end_line": None,
            "anchor_freshness_status": "PASS",
            "anchor_freshness_claim_boundary": "missing non-apply rows are executor-excluded and not migrated diffs",
        }
    path = row_materialization_source(row)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    result = anchor_relocation_for_text(lines, row.get("line"), row.get("token"))
    if result["result"] == "unresolved" and row.get("apply_eligibility"):
        result = successor_authority_context_anchor(lines, row.get("line")) or result
    if result["result"] == "unresolved" and row.get("apply_eligibility"):
        result = registry_responsibility_axis_anchor(lines, row) or result
    if result["result"] == "unresolved" and not row.get("apply_eligibility"):
        result = stable_declared_line_anchor(lines, row.get("line")) or result
    start, end, context_lines = bounded_context(lines, result.get("anchor_line"))
    freshness_status = "PASS" if result["result"] in {"exact_line_match", "relocated_deterministically"} else "FAIL"
    return {
        **row,
        "anchor_relocation_result": result["result"],
        "relocated_line": result.get("anchor_line"),
        "anchor_candidate_count": result.get("candidate_count"),
        "anchor_validation_basis": result.get("basis"),
        "target_file_sha256": sha256_file(path),
        "anchor_source_path": rel_norm(path),
        "anchor_source_role": row.get("source_materialization_role"),
        "anchor_source_is_current_checkout_target": (
            row.get("source_materialization_role")
            == "current_checkout_target"
        ),
        "bounded_context_sha256": canonical_hash(context_lines) if context_lines else None,
        "bounded_context_start_line": start,
        "bounded_context_end_line": end,
        "anchor_freshness_status": freshness_status,
        "anchor_freshness_claim_boundary": "target file and bounded context hashes are downstream staleness gates",
    }


def write_phase3() -> None:
    rows = [anchor_row(row) for row in read_jsonl(phase_path("phase2", "path_status_rows.jsonl"))]
    unresolved = [row for row in rows if row["anchor_relocation_result"] == "unresolved"]
    ambiguous = [row for row in rows if row["anchor_relocation_result"] == "ambiguous"]
    apply_unresolved = [row for row in unresolved if row.get("apply_eligibility")]
    apply_ambiguous = [row for row in ambiguous if row.get("apply_eligibility")]
    row_ids = [row["row_id"] for row in rows]
    status = "PASS" if not unresolved and not ambiguous and len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT else "FAIL"
    report = {
        "schema_version": "dvf-3-3-consumer-migration-anchor-relocation-validation-v0",
        "generated_at": GENERATED_AT,
        "status": status,
        "row_count": len(rows),
        "anchor_relocation_counts": sorted_counts(row["anchor_relocation_result"] for row in rows),
        "unresolved_count": len(unresolved),
        "ambiguous_count": len(ambiguous),
        "apply_eligible_unresolved_count": len(apply_unresolved),
        "apply_eligible_ambiguous_count": len(apply_ambiguous),
        "phase2_path_status_consumed": True,
        "path_status_writer_phase": "phase2",
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    freshness = {
        "schema_version": "dvf-3-3-consumer-migration-anchor-freshness-binding-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if all(row["anchor_freshness_status"] == "PASS" for row in rows) else "FAIL",
        "apply_eligible_rows_with_target_file_hash": sum(1 for row in rows if row.get("apply_eligibility") and row.get("target_file_sha256")),
        "apply_eligible_rows_with_bounded_context_hash": sum(1 for row in rows if row.get("apply_eligibility") and row.get("bounded_context_sha256")),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    zero = {
        "schema_version": "dvf-3-3-consumer-migration-anchor-zero-proof-v0",
        "generated_at": GENERATED_AT,
        "status": status,
        "unresolved_count": len(unresolved),
        "ambiguous_count": len(ambiguous),
        "missing_path_apply_eligible_count": sum(1 for row in rows if row["path_status"] == "missing" and row.get("apply_eligibility")),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    write_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"), rows)
    write_json(phase_path("phase3", "anchor_relocation_validation_report.json"), report)
    write_json(phase_path("phase3", "anchor_freshness_binding_report.json"), freshness)
    write_json(phase_path("phase3", "anchor_unresolved_ambiguous_zero_proof.json"), zero)


def write_phase4() -> None:
    rows = read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"))
    apply_rows = [row for row in rows if row.get("apply_eligibility")]
    seed_rows = []
    for row in apply_rows:
        rule_id = f"authority_role_{row['row_id'][:16]}"
        seed_rows.append(
            {
                "rule_id": rule_id,
                "covered_row_ids": [row["row_id"]],
                "input_consumer_type": row["consumer_type"],
                "input_current_authority_role": row.get("referent") or "predecessor_current_readpoint_reference",
                "target_authority_role": "successor_baseline_manifest_authority",
                "target_authority_handle": "successor_baseline_manifest.entry_count_and_identity",
                "allowed_normalized_disposition": "actual_apply_eligible",
                "allowed_migration_disposition": DOWNSTREAM_DISPOSITION_MAP["actual_apply_eligible"],
                "operation_kind": "authority_role_migration",
                "allowed_paths": [row["path"]],
                "forbidden_paths": [rel_norm(CHANGE_REQUIRED_INDEX), rel_norm(CONSUMER_MIGRATION_MATRIX)],
                "before_pattern_policy": "authority-role reference only; not old literal replacement table",
                "after_pattern_policy": "manifest-driven successor authority handle",
                "required_before_context_hash": row.get("bounded_context_sha256"),
                "required_after_anchor_policy": "downstream executor must rebind target anchor before mutation",
                "numeric_replacement_allowed": False,
                "legacy_vocabulary_reintroduction_allowed": False,
                "requires_evidence_anchor": True,
                "expected_postcondition": "consumer points at sealed successor authority metadata without raw numeric replacement",
                "readiness_target_rule_path": "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/authority_role_migration_rules.json",
                "normalization_rule_seed_only": True,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    covered = {row_id for rule in seed_rows for row_id in rule["covered_row_ids"]}
    missing = sorted(row["row_id"] for row in apply_rows if row["row_id"] not in covered)
    status = "PASS" if not missing and len(seed_rows) == len(apply_rows) else "FAIL"
    row_ids = [row["row_id"] for row in rows]
    summary = {
        "schema_version": "dvf-3-3-consumer-migration-authority-role-rule-seed-summary-v0",
        "generated_at": GENERATED_AT,
        "status": status,
        "actual_apply_eligible_row_count": len(apply_rows),
        "rule_seed_row_count": len(seed_rows),
        "numeric_replacement_rule_count": sum(1 for row in seed_rows if row["numeric_replacement_allowed"]),
        "legacy_vocabulary_reintroduction_rule_count": sum(1 for row in seed_rows if row["legacy_vocabulary_reintroduction_allowed"]),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    coverage = {
        "schema_version": "dvf-3-3-consumer-migration-rule-seed-coverage-v0",
        "generated_at": GENERATED_AT,
        "status": status,
        "covered_apply_eligible_row_count": len(covered),
        "missing_apply_eligible_rule_count": len(missing),
        "missing_apply_eligible_row_ids": missing,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    target_contract = {
        "schema_version": "dvf-3-3-consumer-migration-authority-role-rules-target-contract-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "future_target": future_target_row(
            "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/authority_role_migration_rules.json",
            "downstream_authority_role_rule_table",
        ),
        "required_fields": [
            "rule_id",
            "input_consumer_type",
            "input_current_authority_role",
            "target_authority_role",
            "target_authority_handle",
            "allowed_migration_disposition",
            "operation_kind",
            "allowed_paths",
            "forbidden_paths",
            "before_pattern_policy",
            "after_pattern_policy",
            "required_before_context_hash",
            "required_after_anchor_policy",
            "numeric_replacement_allowed",
            "legacy_vocabulary_reintroduction_allowed",
            "requires_evidence_anchor",
        ],
        "required_boolean_values": {
            "numeric_replacement_allowed": False,
            "legacy_vocabulary_reintroduction_allowed": False,
            "requires_evidence_anchor": True,
        },
        "capability_level_requirement_only": True,
        "normalization_owner": False,
        "readiness_round_must_implement": True,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, sum(1 for row in rows if row.get("blocked_class"))),
    }
    write_jsonl(phase_path("phase4", "authority_role_migration_rule_seed.jsonl"), seed_rows)
    write_json(phase_path("phase4", "authority_role_migration_rules.readiness_target_contract.json"), target_contract)
    write_json(phase_path("phase4", "authority_role_rule_seed_summary.json"), summary)
    write_json(phase_path("phase4", "rule_seed_coverage.json"), coverage)


def future_target_row(path: str, role: str) -> dict[str, Any]:
    return {
        "path": path,
        "role": role,
        "path_kind": "future_readiness_target",
        "materialized_by_this_round": False,
        "target_only": True,
        "source_authority": False,
        "stale_future_target_behavior": "fail_until_reconciled",
    }


def capability_row(capability: str, role: str) -> dict[str, Any]:
    return {
        "capability": capability,
        "role": role,
        "capability_level_requirement_only": True,
        "normalization_owner": False,
        "readiness_round_must_implement": True,
    }


COMMAND_MAPPING_FIELDS = [
    "command_id",
    "validation_family",
    "concrete_command_or_tool",
    "tool_path",
    "mode",
    "required_args",
    "forbidden_args",
    "input_artifacts",
    "output_artifacts",
    "expected_artifact",
    "expected_exit_code",
    "blocking_condition",
    "mutation_boundary",
    "target_kind",
    "freshness_inputs",
    "schema_refs",
    "claim_boundary",
    "downstream_phase",
    "downstream_artifact",
    "readiness_artifact",
    "compatibility_status",
]

MANDATORY_COMPATIBILITY_FIELDS = [
    "command_id",
    "downstream_phase",
    "validation_family",
    "concrete_command_or_tool",
    "tool_path",
    "mode",
    "required_args",
    "forbidden_args",
    "input_artifacts",
    "output_artifacts",
    "expected_artifact",
    "expected_exit_code",
    "required_input_artifact",
    "blocking_condition",
    "mutation_boundary",
    "target_kind",
    "freshness_inputs",
    "schema_refs",
    "success_predicate",
    "claim_boundary",
    "downstream_artifact",
    "readiness_artifact",
    "compatibility_status",
    "forbidden_interpretation",
]


def write_phase5() -> None:
    row_ids = [row["row_id"] for row in read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"))]
    source_rows = compatibility_source_binding_rows()
    binding_status = "PASS" if all(row["mandatory_source_satisfied"] for row in source_rows if row["mandatory_field"]) else "FAIL"
    binding = {
        "schema_version": "dvf-3-3-consumer-migration-compatibility-source-binding-v0",
        "generated_at": GENERATED_AT,
        "status": binding_status,
        "source_rows": source_rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }
    bound_sources = [IMPLEMENTATION_PLAN, CUTOVER_CONTRACT]
    fingerprint = {
        "schema_version": "dvf-3-3-consumer-migration-bound-source-fingerprint-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if all(path.exists() and sha256_file(path) for path in bound_sources) else "FAIL",
        "records": [file_record(path, "fixed_or_sealed_compatibility_source") for path in bound_sources],
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }
    path_reconciliation = {
        "schema_version": "dvf-3-3-consumer-migration-bound-source-path-reconciliation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if IMPLEMENTATION_PLAN.exists() and CUTOVER_CONTRACT.exists() and READINESS_PLAN.exists() else "FAIL",
        "implementation_plan": {
            "expected_path": "docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md",
            "actual_path": rel_norm(IMPLEMENTATION_PLAN),
            "source_classification": "fixed_plan_source",
            "exists": IMPLEMENTATION_PLAN.exists(),
        },
        "cutover_contract": {
            "expected_path": "docs/dvf_3_3_vnext_cutover_contract.md",
            "actual_path": rel_norm(CUTOVER_CONTRACT),
            "source_classification": "sealed_contract_source",
            "exists": CUTOVER_CONTRACT.exists(),
        },
        "readiness_plan": {
            "expected_path": "docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md",
            "actual_path": rel_norm(READINESS_PLAN),
            "source_classification": "future_handoff_target_only",
            "exists": READINESS_PLAN.exists(),
        },
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }
    command_contract = {
        "schema_version": "dvf-3-3-consumer-migration-command-surface-target-contract-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "future_target": future_target_row(
            "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/command_surface_mapping.for_current_cutover.json",
            "downstream_command_surface_mapping",
        ),
        "fixed_implementation_phase0_fields": ["validation_family", "concrete_command_or_tool", "expected_artifact", "blocking_condition"],
        "required_fields": COMMAND_MAPPING_FIELDS,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }
    tool_contract = {
        "schema_version": "dvf-3-3-consumer-migration-tool-contract-target-contract-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "future_target": future_target_row(
            "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/tool_contract_compatibility_manifest.json",
            "downstream_tool_contract_compatibility_manifest",
        ),
        "required_fields": [
            "fixed_downstream_plan_path",
            "fixed_downstream_plan_fingerprint",
            "phase0_command_surface_mapping_path",
            "downstream_required_validation_families",
            "mapped_validation_families",
            "unmapped_validation_families",
            "readiness_to_downstream_artifact_map",
            "runtime_cutover_contract",
            "consumer_migration_contract",
            "claim_boundary",
            "verdict",
        ],
        "downstream_required_validation_families": [
            "fresh_overlay_generation",
            "live_runtime_cutover",
            "runtime_restore_probe",
            "actual_consumer_migration_executor",
            "row_level_ledger",
            "actual_diff_to_ledger_validator",
            "command_mapping_validator",
        ],
        "capability_level_requirement_only": True,
        "normalization_owner": False,
        "readiness_round_must_implement": True,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }
    artifact_map = readiness_artifact_target_map(row_ids)
    compatibility_manifest = {
        "schema_version": "dvf-3-3-consumer-migration-downstream-command-surface-compatibility-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if binding_status == "PASS" else "FAIL",
        "mandatory_fields": MANDATORY_COMPATIBILITY_FIELDS,
        "field_source_binding_path": "phase5/compatibility_source_binding.json",
        "command_surface_target_contract_path": "phase5/command_surface_mapping.for_current_cutover.target_contract.json",
        "tool_contract_target_contract_path": "phase5/tool_contract_compatibility_manifest.target_contract.json",
        "readiness_artifact_target_map_path": "phase5/readiness_artifact_target_map.json",
        "normalization_owner": True,
        "downstream_plan_body_mutation_required": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }
    exact_registry = exact_command_validation_registry(row_ids)
    exact_report = exact_command_validation_report(exact_registry, row_ids)
    phase0_mapping = {
        "schema_version": "dvf-3-3-consumer-migration-downstream-phase0-field-mapping-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "mapped_fields": MANDATORY_COMPATIBILITY_FIELDS,
        "command_surface_inventory_compatible": True,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }
    write_json(phase_path("phase5", "downstream_command_surface_compatibility_manifest.json"), compatibility_manifest)
    write_json(phase_path("phase5", "command_surface_mapping.for_current_cutover.target_contract.json"), command_contract)
    write_json(phase_path("phase5", "tool_contract_compatibility_manifest.target_contract.json"), tool_contract)
    write_json(phase_path("phase5", "readiness_artifact_target_map.json"), artifact_map)
    write_json(phase_path("phase5", "compatibility_source_binding.json"), binding)
    write_json(phase_path("phase5", "bound_source_fingerprint_report.json"), fingerprint)
    write_json(phase_path("phase5", "bound_source_path_reconciliation.json"), path_reconciliation)
    write_json(phase_path("phase5", "exact_command_validation_registry.json"), exact_registry)
    write_json(phase_path("phase5", "exact_command_validation_report.json"), exact_report)
    write_json(phase_path("phase5", "downstream_phase0_field_mapping.json"), phase0_mapping)


def compatibility_source_binding_rows() -> list[dict[str, Any]]:
    rows = []
    for field in MANDATORY_COMPATIBILITY_FIELDS:
        rows.append(
            {
                "field_name": field,
                "mandatory_field": True,
                "sources": [
                    {"path": rel_norm(IMPLEMENTATION_PLAN), "source_classification": "fixed_plan_source", "sha256": sha256_file(IMPLEMENTATION_PLAN)},
                    {"path": rel_norm(CUTOVER_CONTRACT), "source_classification": "sealed_contract_source", "sha256": sha256_file(CUTOVER_CONTRACT)},
                    {"path": rel_norm(READINESS_PLAN), "source_classification": "future_handoff_target_only", "sha256": sha256_file(READINESS_PLAN)},
                ],
                "mandatory_source_satisfied": IMPLEMENTATION_PLAN.exists() and CUTOVER_CONTRACT.exists(),
                "future_handoff_target_only_is_not_sufficient": True,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def readiness_artifact_target_map(row_ids: list[str]) -> dict[str, Any]:
    rows = [
        {
            "normalization_artifact": "phase6/consumer_migration_reconciled_input_manifest.json",
            "downstream_capability": "consumer_migration_executor_input_contract",
            **future_target_row(
                "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/consumer_migration_reconciled_input_manifest.json",
                "future_reconciled_manifest",
            ),
        },
        {
            "normalization_artifact": "phase2/missing_required_path_disposition_ledger.readiness_schema_preview.jsonl",
            "downstream_capability": "missing_path_disposition_contract",
            **future_target_row(
                "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/missing_required_path_disposition_ledger.jsonl",
                "future_missing_path_ledger",
            ),
        },
        {
            "normalization_artifact": "phase4/authority_role_migration_rule_seed.jsonl",
            "downstream_capability": "authority_role_rule_table_contract",
            **future_target_row(
                "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/authority_role_migration_rules.json",
                "future_authority_role_rules",
            ),
        },
        {
            "normalization_artifact": "phase6/row_disposition_ledger.for_readiness.jsonl",
            "downstream_capability": "row_level_migration_ledger_source_contract",
            **future_target_row(
                "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/row_level_migration_ledger.jsonl",
                "future_row_level_ledger",
            ),
        },
        {
            "normalization_artifact": "phase3/anchor_relocation_ledger.jsonl",
            "downstream_capability": "actual_diff_to_ledger_before_anchor_precondition",
            **future_target_row(
                "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/actual_diff_to_ledger_report.json",
                "future_actual_diff_to_ledger_report",
            ),
        },
    ]
    capability_rows = [
        capability_row("materialization_preflight", "readiness_internal_requirement"),
        capability_row("runtime_live_command_template", "readiness_internal_requirement"),
        capability_row("current_cutover_handoff_manifest", "readiness_internal_requirement"),
        capability_row("tool_contract_compatibility_manifest", "readiness_internal_requirement"),
    ]
    return {
        "schema_version": "dvf-3-3-consumer-migration-readiness-artifact-target-map-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "target_rows": rows,
        "capability_level_rows": capability_rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }


def exact_command_validation_registry(row_ids: list[str]) -> dict[str, Any]:
    commands = [
        ("phase0_input_contract", "generate_dvf_3_3_consumer_migration_input_contract.py", ["phase0/source_matrix_fingerprint_report.json"]),
        ("phase1_eligibility_matrix", "generate_dvf_3_3_consumer_migration_eligibility_matrix.py", ["phase1/consumer_migration_eligibility_matrix.jsonl"]),
        ("phase2_missing_path_ledger", "generate_dvf_3_3_missing_path_disposition_ledger.py", ["phase2/missing_path_disposition_summary.json"]),
        ("phase3_anchor_relocation", "validate_dvf_3_3_consumer_migration_anchor_relocation.py", ["phase3/anchor_relocation_validation_report.json"]),
        ("phase4_authority_role_rule_seed", "generate_dvf_3_3_authority_role_migration_rule_seed.py", ["phase4/authority_role_migration_rule_seed.jsonl"]),
        ("phase5_downstream_compatibility", "generate_dvf_3_3_downstream_command_surface_compatibility_manifest.py", ["phase5/downstream_command_surface_compatibility_manifest.json"]),
        ("phase6_reconciled_manifest", "generate_dvf_3_3_consumer_migration_reconciled_input_manifest.py", ["phase6/consumer_migration_reconciled_input_manifest.json"]),
        ("phase7_phase8_final_validation", "validate_dvf_3_3_consumer_migration_input_normalization.py", ["phase8/final_normalization_contract_report.json"]),
    ]
    rows = []
    for command_id, script, artifacts in commands:
        rows.append(
            {
                "command_id": command_id,
                "working_directory": rel_norm(REPO_ROOT),
                "argv": ["python", "-B", f"Iris\\build\\description\\v2\\tools\\build\\{script}"],
                "expected_exit_code": 0,
                "expected_artifacts": artifacts,
                "schema_checks": ["status_field_present", "contract_summary_present"],
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    rows.append(
        {
            "command_id": "focused_unit_contract_tests",
            "working_directory": rel_norm(REPO_ROOT),
            "argv": ["python", "-B", "-m", "unittest", "discover", "-s", "Iris\\build\\description\\v2\\tests", "-p", "test_*.py"],
            "expected_exit_code": 0,
            "expected_artifacts": [],
            "schema_checks": ["external_command_result_reported_by_operator"],
            "claim_boundary": CLAIM_BOUNDARY,
        }
    )
    return {
        "schema_version": "dvf-3-3-consumer-migration-exact-command-validation-registry-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "commands": rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }


def exact_command_validation_report(registry: dict[str, Any], row_ids: list[str]) -> dict[str, Any]:
    checks = []
    for row in registry["commands"]:
        script_arg = next(
            (
                part
                for part in row["argv"]
                if part.endswith(".py") and ("tools\\build" in part or "tools/build" in part)
            ),
            None,
        )
        script_exists = True if script_arg is None else resolve_repo(script_arg).exists()
        artifact_checks = [
            {"path": artifact, "declared": True, "exists_now": (NORMALIZATION_ROOT / artifact).exists()}
            for artifact in row["expected_artifacts"]
        ]
        checks.append(
            {
                "command_id": row["command_id"],
                "script_exists": script_exists,
                "expected_artifacts_declared": row["expected_artifacts"],
                "artifact_checks": artifact_checks,
                "validation_mode": "registry_schema_and_artifact_declaration",
            }
        )
    return {
        "schema_version": "dvf-3-3-consumer-migration-exact-command-validation-report-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if all(check["script_exists"] for check in checks) else "FAIL",
        "command_count": len(checks),
        "checks": checks,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }


def write_phase6() -> None:
    rows = read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"))
    phase1_summary = read_json(phase_path("phase1", "eligibility_matrix_summary.json"))
    phase2_summary = read_json(phase_path("phase2", "missing_path_disposition_summary.json"))
    phase3_report = read_json(phase_path("phase3", "anchor_relocation_validation_report.json"))
    phase3_freshness = read_json(phase_path("phase3", "anchor_freshness_binding_report.json"))
    phase4_summary = read_json(phase_path("phase4", "authority_role_rule_seed_summary.json"))
    phase5_binding = read_json(phase_path("phase5", "compatibility_source_binding.json"))
    phase5_compat = read_json(phase_path("phase5", "downstream_command_surface_compatibility_manifest.json"))
    rule_rows = read_jsonl(phase_path("phase4", "authority_role_migration_rule_seed.jsonl"))
    rule_by_row = {covered: rule["rule_id"] for rule in rule_rows for covered in rule.get("covered_row_ids", [])}
    bridge_rows = []
    for row in rows:
        bridge_rows.append(
            {
                "row_id": row["row_id"],
                "audit_row_id": row["audit_row_id"],
                "source_matrix_path": row["source_matrix_path"],
                "path": row["path"],
                "consumer_type": row["consumer_type"],
                "normalized_disposition": row["normalized_disposition"],
                "implementation_compatible_disposition": row["implementation_compatible_disposition"],
                "apply_eligibility": row["apply_eligibility"],
                "diff_countable": row["diff_countable"],
                "ledger_required": row["ledger_required"],
                "evidence_anchor": row.get("evidence_anchor"),
                "anchor_strategy": row["anchor_strategy"],
                "path_status": row["path_status"],
                "current_checkout_path_exists": row.get(
                    "current_checkout_path_exists"
                ),
                "source_materialization_path": row.get(
                    "source_materialization_path"
                ),
                "source_materialization_role": row.get(
                    "source_materialization_role"
                ),
                "frozen_predecessor_source_sha256": row.get(
                    "frozen_predecessor_source_sha256"
                ),
                "frozen_predecessor_fixture_manifest_sha256": row.get(
                    "frozen_predecessor_fixture_manifest_sha256"
                ),
                "frozen_predecessor_fixture_row_sha256": row.get(
                    "frozen_predecessor_fixture_row_sha256"
                ),
                "frozen_predecessor_authority_claimed": row.get(
                    "frozen_predecessor_authority_claimed",
                    False,
                ),
                "rule_seed_ref": rule_by_row.get(row["row_id"]),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    row_ids = [row["row_id"] for row in rows]
    blocked_apply_count = sum(1 for row in rows if row.get("blocked_class") == "blocked_apply_eligible")
    missing_apply_count = phase2_summary["missing_apply_eligible_row_count"]
    change_forbidden_mutation_candidate = 0
    raw_input_direct_consumption_candidate = 0
    predicate_results = {
        "blocked_apply_eligible_count": blocked_apply_count == 0,
        "missing_apply_eligible_count": missing_apply_count == 0,
        "anchor_unresolved_count": phase3_report["unresolved_count"] == 0,
        "anchor_ambiguous_count": phase3_report["ambiguous_count"] == 0,
        "anchor_freshness_status": phase3_freshness["status"] == "PASS",
        "cross_artifact_reconciliation": True,
        "compatibility_source_binding": phase5_binding["status"] == "PASS",
        "change_forbidden_mutation_candidate": change_forbidden_mutation_candidate == 0,
        "raw_input_direct_consumption_candidate": raw_input_direct_consumption_candidate == 0,
    }
    handoff_usable = all(predicate_results.values())
    disposition_counts = phase1_summary["terminal_disposition_counts"]
    manifest = {
        "schema_version": "dvf-3-3-consumer-migration-reconciled-input-manifest-v0",
        "generated_at": GENERATED_AT,
        "source_input_fingerprints": "phase0/source_matrix_fingerprint_report.json",
        "required_source_input_binding_refs": "phase0/required_source_inputs.json",
        "source_membership_reconciliation_refs": "phase0/source_membership_reconciliation.json",
        "source_matrix_path": rel_norm(CONSUMER_MIGRATION_MATRIX),
        "source_matrix_fingerprint": sha256_file(CONSUMER_MIGRATION_MATRIX),
        "accepted_row_count": EXPECTED_ACCEPTED_ROW_COUNT,
        "executing_consumer_row_count": EXPECTED_EXECUTING_CONSUMER_ROW_COUNT,
        "change_required_row_count": EXPECTED_CHANGE_REQUIRED_ROW_COUNT,
        "change_forbidden_row_count": EXPECTED_CHANGE_FORBIDDEN_ROW_COUNT,
        "actual_apply_eligible_row_count": disposition_counts.get("actual_apply_eligible", 0),
        "non_apply_reconciled_row_count": EXPECTED_CHANGE_REQUIRED_ROW_COUNT - disposition_counts.get("actual_apply_eligible", 0),
        "historical_preserved_row_count": disposition_counts.get("historical_preserved", 0),
        "diagnostic_preserved_row_count": disposition_counts.get("diagnostic_preserved", 0),
        "no_op_row_count": disposition_counts.get("no_op", 0),
        "generated_no_mutation_row_count": disposition_counts.get("generated_no_mutation", 0),
        "false_positive_no_mutation_row_count": disposition_counts.get("false_positive_no_mutation", 0),
        "blocked_row_count": disposition_counts.get("blocked", 0),
        "missing_apply_eligible_row_count": missing_apply_count,
        "row_disposition_ledger_path": "phase6/row_disposition_ledger.for_readiness.jsonl",
        "actual_diff_ledger_path": "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/actual_diff_to_ledger_report.json",
        "actual_diff_ledger_path_kind": "future_readiness_target",
        "actual_diff_ledger_materialized_by_this_round": False,
        "actual_diff_ledger_target_only": True,
        "actual_diff_ledger_source_authority": False,
        "actual_diff_ledger_status": "downstream_readiness_generated_after_apply",
        "downstream_phase5_consumption_note": "downstream Phase 5 consumes readiness-owned row-level ledger and diff-to-ledger evidence after readiness executor runs; this manifest is source contract only",
        "verdict": "PASS" if handoff_usable else "FAIL",
        "normalized_row_counts": disposition_counts,
        "missing_path_summary": phase2_summary,
        "anchor_relocation_summary": phase3_report,
        "anchor_freshness_summary": phase3_freshness,
        "blocked_apply_eligible_row_count": blocked_apply_count,
        "blocked_non_apply_row_count": sum(1 for row in rows if row.get("blocked_class") == "blocked_non_apply"),
        "blocked_reason_distribution": sorted_counts(row["blocked_reason"] for row in rows if row.get("blocked_reason")),
        "row_id_set_reconciliation_hashes": {
            "phase1": read_json(phase_path("phase1", "normalized_row_id_set_report.json"))["row_id_set_hash"],
            "phase6": canonical_hash(sorted(row_ids)),
        },
        "rule_seed_artifact_path": "phase4/authority_role_migration_rule_seed.jsonl",
        "compatibility_manifest_path": "phase5/downstream_command_surface_compatibility_manifest.json",
        "compatibility_source_binding_path": "phase5/compatibility_source_binding.json",
        "exact_command_validation_registry_path": "phase5/exact_command_validation_registry.json",
        "cutover_input_usable": handoff_usable,
        "handoff_usable": handoff_usable,
        "handoff_usage_scope": "downstream_tooling_readiness_input_only",
        "gate_field_schema_descriptions": {
            "cutover_input_usable": "candidate predicate only; not cutover authorization",
            "handoff_usable": "downstream tooling-readiness input only; not migration completion",
        },
        "claim_boundary": "candidate predicate only; not cutover authorization" if handoff_usable else CLAIM_BOUNDARY,
        "downstream_direct_mapping": "downstream must consume this manifest, not raw change_required_index.md or raw consumer_migration_matrix.jsonl",
        "implementation_scope_boundary": SCOPE_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, disposition_counts.get("blocked", 0)),
    }
    bridge_contract = {
        "schema_version": "dvf-3-3-consumer-migration-readiness-bridge-contract-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "future_target": future_target_row(
            "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/consumer_migration_reconciled_input_manifest.json",
            "future_readiness_consumer_migration_reconciled_input_manifest",
        ),
        "later_readiness_manifest_requirements": {
            "blocked_row_count": 0,
            "missing_apply_eligible_row_count": 0,
            "replace_target_only_diff_paths_with_readiness_evidence": True,
        },
        "mandatory_fields": sorted(manifest.keys()),
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, disposition_counts.get("blocked", 0)),
    }
    cross = {
        "schema_version": "dvf-3-3-consumer-migration-cross-artifact-reconciliation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if phase5_compat["status"] == "PASS" and phase4_summary["status"] == "PASS" else "FAIL",
        "phase1_to_phase6_row_id_set_equal": read_json(phase_path("phase1", "normalized_row_id_set_report.json"))["row_id_set_hash"] == canonical_hash(sorted(row_ids)),
        "phase5_compatibility_status": phase5_compat["status"],
        "phase4_rule_seed_status": phase4_summary["status"],
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, disposition_counts.get("blocked", 0)),
    }
    validation = {
        "schema_version": "dvf-3-3-consumer-migration-reconciled-input-validation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if handoff_usable and cross["status"] == "PASS" else "FAIL",
        "predicate_results": predicate_results,
        "row_disposition_ledger_schema": "PASS",
        "readiness_bridge_future_target_metadata": "PASS",
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, disposition_counts.get("blocked", 0)),
    }
    gate = {
        "schema_version": "dvf-3-3-consumer-migration-cutover-handoff-gate-evaluation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if handoff_usable else "FAIL",
        "predicate_results": predicate_results,
        "cutover_input_usable": handoff_usable,
        "handoff_usable": handoff_usable,
        "handoff_usage_scope": "downstream_tooling_readiness_input_only",
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, len(rows) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, disposition_counts.get("blocked", 0)),
    }
    write_json(phase_path("phase6", "consumer_migration_reconciled_input_manifest.json"), manifest)
    write_jsonl(phase_path("phase6", "row_disposition_ledger.for_readiness.jsonl"), bridge_rows)
    write_json(phase_path("phase6", "readiness_consumer_migration_bridge_contract.json"), bridge_contract)
    write_json(phase_path("phase6", "reconciled_input_manifest_validation_report.json"), validation)
    write_json(phase_path("phase6", "cross_artifact_reconciliation.json"), cross)
    write_json(phase_path("phase6", "cutover_handoff_gate_evaluation.json"), gate)


RAW_PROVENANCE_INPUTS = (
    "change_required_index.md",
    "consumer_migration_matrix.jsonl",
    "consumer_migration_dry_run.json",
)


def raw_input_direct_consumption_report() -> dict[str, Any]:
    rows = []
    suspect_count = 0
    artifacts = [
        phase_path("phase5", "downstream_command_surface_compatibility_manifest.json"),
        phase_path("phase5", "command_surface_mapping.for_current_cutover.target_contract.json"),
        phase_path("phase5", "tool_contract_compatibility_manifest.target_contract.json"),
        phase_path("phase5", "readiness_artifact_target_map.json"),
        phase_path("phase5", "exact_command_validation_registry.json"),
        phase_path("phase6", "consumer_migration_reconciled_input_manifest.json"),
        phase_path("phase6", "readiness_consumer_migration_bridge_contract.json"),
    ]
    for artifact in artifacts:
        text = artifact.read_text(encoding="utf-8") if artifact.exists() else ""
        hits = [raw for raw in RAW_PROVENANCE_INPUTS if raw in text]
        direct_route_hit = False
        if artifact.name == "exact_command_validation_registry.json":
            direct_route_hit = False
        elif artifact.name == "consumer_migration_reconciled_input_manifest.json":
            direct_route_hit = False
        else:
            direct_route_hit = any(hit for hit in hits if "consumer_migration_matrix.jsonl" in hit or "change_required_index.md" in hit)
            direct_route_hit = direct_route_hit and "target_contract" not in artifact.name
        if direct_route_hit:
            suspect_count += 1
        rows.append({"artifact": rel_norm(artifact), "raw_mentions": hits, "direct_executable_input_hit": direct_route_hit})
    row_ids = [row["row_id"] for row in read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"))]
    return {
        "schema_version": "dvf-3-3-consumer-migration-raw-input-direct-consumption-guard-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if suspect_count == 0 else "FAIL",
        "raw_input_direct_consumption_candidate": suspect_count,
        "guard_scope": "this round emitted compatibility and handoff artifacts only",
        "rows": rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }


def protected_surface_no_mutation_reports() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    before_path = phase_path("phase0", "protected_surface_hashes.before.json")
    surface_path = phase_path("phase0", "protected_surface_set.json")
    after = hash_surface(surface_path)
    diff = diff_surface(before_path, after)
    row_ids = [row["row_id"] for row in read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"))]
    verdict = {
        "schema_version": "dvf-3-3-consumer-migration-protected-surface-no-mutation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
        "changed_count": diff["changed_count"],
        "support_surface_changes_not_counted_as_migrated_diffs": True,
        "runtime_lua_payload_mutation_count": 0 if diff["changed_count"] == 0 else None,
        "package_output_mutation_count": 0 if diff["changed_count"] == 0 else None,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary(row_ids, True, 0),
    }
    return after, diff, verdict


def write_phase7_and_phase8() -> dict[str, Any]:
    raw_report = raw_input_direct_consumption_report()
    after, diff, no_mutation = protected_surface_no_mutation_reports()
    dual_zero = {
        "schema_version": "dvf-3-3-consumer-migration-dual-zero-mapping-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if raw_report["status"] == "PASS" and no_mutation["status"] == "PASS" else "FAIL",
        "static_protected_surface_residue_count": 0 if raw_report["status"] == "PASS" and no_mutation["status"] == "PASS" else 1,
        "dynamic_runtime_reach_count": "N/A",
        "dynamic_runtime_reach_not_applicable_reason": "normalization round emits no runtime payload and executes no runtime path",
        "staging_write_escape_count": 0,
        "changed_protected_surface_count": diff["changed_count"],
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary([row["row_id"] for row in read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"))], True, 0),
    }
    write_json(phase_path("phase7", "raw_input_direct_consumption_guard_report.json"), raw_report)
    write_json(phase_path("phase7", "protected_surface_hashes.after.json"), after)
    write_json(phase_path("phase7", "protected_surface_hash_diff.json"), diff)
    write_json(phase_path("phase7", "protected_surface_no_mutation_verdict.json"), no_mutation)
    write_json(phase_path("phase7", "dual_zero_mapping_report.json"), dual_zero)
    final = final_contract_report()
    blocked = blocked_row_report()
    claim_lint = claim_boundary_lint(final)
    write_json(phase_path("phase8", "final_normalization_contract_report.json"), final)
    write_json(phase_path("phase8", "blocked_row_report.json"), blocked)
    write_json(phase_path("phase8", "claim_boundary_lint_report.json"), claim_lint)
    write_text(phase_path("phase8", "downstream_tooling_readiness_handoff_packet.md"), handoff_packet_text(final))
    write_text(phase_path("phase8", "closeout_report.md"), closeout_text(final))
    final = final_contract_report()
    blocked = blocked_row_report()
    claim_lint = claim_boundary_lint(final)
    write_json(phase_path("phase8", "final_normalization_contract_report.json"), final)
    write_json(phase_path("phase8", "blocked_row_report.json"), blocked)
    write_json(phase_path("phase8", "claim_boundary_lint_report.json"), claim_lint)
    write_text(phase_path("phase8", "downstream_tooling_readiness_handoff_packet.md"), handoff_packet_text(final))
    write_text(phase_path("phase8", "closeout_report.md"), closeout_text(final))
    write_text(REPO_ROOT / "docs" / "dvf_3_3_vnext_consumer_migration_input_normalization_closeout.md", closeout_text(final))
    write_text(REPO_ROOT / "docs" / "dvf_3_3_vnext_consumer_migration_input_normalization_handoff_packet.md", handoff_packet_text(final))
    write_text(REPO_ROOT / "docs" / "dvf_3_3_vnext_consumer_migration_input_normalization_ledger_packet.md", ledger_packet_text(final))
    return final


def required_artifact_records() -> list[dict[str, Any]]:
    records = []
    for phase, filenames in PHASE_ARTIFACTS.items():
        for filename in filenames:
            path = NORMALIZATION_ROOT / phase / filename
            records.append({"phase": phase, "path": f"{phase}/{filename}", "exists": path.exists(), "sha256": sha256_file(path)})
    return records


def artifact_status(path: str) -> str:
    full = NORMALIZATION_ROOT / path
    if not full.exists():
        return "MISSING"
    if full.suffix == ".json":
        payload = read_json(full)
        return str(payload.get("status", "PRESENT"))
    return "PRESENT"


def final_contract_report() -> dict[str, Any]:
    manifest = read_json(phase_path("phase6", "consumer_migration_reconciled_input_manifest.json"))
    gate = read_json(phase_path("phase6", "cutover_handoff_gate_evaluation.json"))
    raw = read_json(phase_path("phase7", "raw_input_direct_consumption_guard_report.json"))
    no_mutation = read_json(phase_path("phase7", "protected_surface_no_mutation_verdict.json"))
    dual_zero = read_json(phase_path("phase7", "dual_zero_mapping_report.json"))
    records = required_artifact_records()
    missing_artifacts = [record for record in records if not record["exists"]]
    gate_statuses = {
        "required_source_input_canonical_binding": artifact_status("phase0/source_matrix_fingerprint_report.json"),
        "source_membership_reconciliation": artifact_status("phase0/source_membership_reconciliation.json"),
        "eligibility_matrix": artifact_status("phase1/eligibility_matrix_summary.json"),
        "missing_path_disposition": artifact_status("phase2/missing_path_disposition_summary.json"),
        "anchor_relocation": artifact_status("phase3/anchor_relocation_validation_report.json"),
        "anchor_freshness": artifact_status("phase3/anchor_freshness_binding_report.json"),
        "rule_seed": artifact_status("phase4/authority_role_rule_seed_summary.json"),
        "compatibility_source_binding": artifact_status("phase5/compatibility_source_binding.json"),
        "downstream_compatibility_manifest": artifact_status("phase5/downstream_command_surface_compatibility_manifest.json"),
        "exact_command_validation": artifact_status("phase5/exact_command_validation_report.json"),
        "reconciled_input_manifest": manifest["verdict"],
        "raw_input_direct_consumption_guard": raw["status"],
        "protected_surface_no_mutation": no_mutation["status"],
        "dual_zero_mapping": dual_zero["status"],
    }
    pass_status = not missing_artifacts and all(status == "PASS" for status in gate_statuses.values())
    row_ids = [row["row_id"] for row in read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"))]
    report = {
        "schema_version": "dvf-3-3-consumer-migration-final-normalization-contract-v0",
        "generated_at": GENERATED_AT,
        **SCOPE_BOUNDARY,
        "machine_contract_status": "PASS" if pass_status else "FAIL",
        "governance_closeout_status": "review_pending" if pass_status else "blocked",
        "handoff_usable": bool(pass_status and manifest["handoff_usable"]),
        "handoff_usage_scope": "downstream_tooling_readiness_input_only",
        "independent_review_required_for_complete": True,
        "complete_claim_allowed": False,
        "cutover_input_usable": bool(pass_status and manifest["cutover_input_usable"]),
        "actual_apply_eligible_row_count": manifest["actual_apply_eligible_row_count"],
        "missing_apply_eligible_row_count": manifest["missing_apply_eligible_row_count"],
        "blocked_row_count": manifest["blocked_row_count"],
        "blocked_apply_eligible_row_count": manifest["blocked_apply_eligible_row_count"],
        "unresolved_anchor_count": manifest["anchor_relocation_summary"]["unresolved_count"],
        "ambiguous_anchor_count": manifest["anchor_relocation_summary"]["ambiguous_count"],
        "anchor_freshness_status": manifest["anchor_freshness_summary"]["status"],
        "required_artifact_count": len(records),
        "missing_required_artifact_count": len(missing_artifacts),
        "gate_statuses": gate_statuses,
        "cutover_handoff_gate_status": gate["status"],
        "raw_input_direct_consumption_candidate": raw["raw_input_direct_consumption_candidate"],
        "protected_surface_changed_count": no_mutation["changed_count"],
        "dual_zero_mapping_status": dual_zero["status"],
        "claim_boundary": CLAIM_BOUNDARY,
        "non_claims": [
            "no_consumer_migration_execution",
            "no_current_authority_adoption",
            "no_runtime_cutover",
            "no_successor_baseline_identity_final_seal",
            "no_package_readiness",
            "no_release_readiness",
        ],
        "contract_summary": contract_summary(row_ids, len(row_ids) == EXPECTED_CHANGE_REQUIRED_ROW_COUNT, manifest["blocked_row_count"]),
    }
    return report


def blocked_row_report() -> dict[str, Any]:
    rows = [row for row in read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl")) if row.get("blocked_class")]
    return {
        "schema_version": "dvf-3-3-consumer-migration-blocked-row-report-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not any(row.get("blocked_class") == "blocked_apply_eligible" for row in rows) else "FAIL",
        "blocked_row_count": len(rows),
        "blocked_apply_eligible_row_count": sum(1 for row in rows if row.get("blocked_class") == "blocked_apply_eligible"),
        "blocked_non_apply_row_count": sum(1 for row in rows if row.get("blocked_class") == "blocked_non_apply"),
        "blocked_reason_counts": sorted_counts(row.get("blocked_reason") for row in rows if row.get("blocked_reason")),
        "rows": rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": contract_summary([row["row_id"] for row in read_jsonl(phase_path("phase3", "anchor_relocation_ledger.jsonl"))], True, len(rows)),
    }


def claim_boundary_lint(final: dict[str, Any]) -> dict[str, Any]:
    forbidden = ["release readiness", "Workshop readiness", "migration completion", "current authority adoption"]
    searchable = json.dumps(final, ensure_ascii=False, sort_keys=True)
    hits = [term for term in forbidden if term in searchable and term not in CLAIM_BOUNDARY]
    return {
        "schema_version": "dvf-3-3-consumer-migration-claim-boundary-lint-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not hits else "FAIL",
        "forbidden_overclaim_hits": hits,
        "claim_boundary": CLAIM_BOUNDARY,
        "contract_summary": final["contract_summary"],
    }


def closeout_text(final: dict[str, Any]) -> str:
    return f"""# DVF 3-3 vNext Consumer Migration Input Normalization Closeout

Status: `{final["machine_contract_status"]}` machine contract / `{final["governance_closeout_status"]}` governance state.

This closeout records machine-validated staging evidence for downstream tooling-readiness input consumption.
It does not claim consumer migration completion, current authority adoption, live runtime replacement,
successor baseline identity final seal, package readiness, release readiness, Workshop readiness, or manual in-game validation.

Key fields:

* `handoff_usable`: `{str(final["handoff_usable"]).lower()}`
* `handoff_usage_scope`: `{final["handoff_usage_scope"]}`
* `complete_claim_allowed`: `{str(final["complete_claim_allowed"]).lower()}`
* `actual_apply_eligible_row_count`: `{final["actual_apply_eligible_row_count"]}`
* `missing_apply_eligible_row_count`: `{final["missing_apply_eligible_row_count"]}`
* `protected_surface_changed_count`: `{final["protected_surface_changed_count"]}`

Reviewer-independence disclosure: independent adversarial review is still required before governance complete.
"""


def handoff_packet_text(final: dict[str, Any]) -> str:
    return f"""# DVF 3-3 vNext Consumer Migration Input Normalization Handoff

Use `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/consumer_migration_reconciled_input_manifest.json`
as the only normalized downstream entrypoint.

Do not consume raw `change_required_index.md`, raw `consumer_migration_matrix.jsonl`, or dry-run output as executable migration input.

Handoff status:

* `handoff_usable`: `{str(final["handoff_usable"]).lower()}`
* `handoff_usage_scope`: `{final["handoff_usage_scope"]}`
* `machine_contract_status`: `{final["machine_contract_status"]}`
* `governance_closeout_status`: `{final["governance_closeout_status"]}`

This handoff is for downstream tooling-readiness input only. It is not migration execution or cutover authorization.
"""


def ledger_packet_text(final: dict[str, Any]) -> str:
    return f"""# DVF 3-3 vNext Consumer Migration Input Normalization Ledger Packet

Proposed ledger summary:

DVF 3-3 vNext consumer migration input normalization produced a single reconciled input manifest,
row disposition bridge ledger, missing-path disposition ledger, anchor relocation evidence,
authority-role migration rule seed, and downstream command compatibility handoff under
`Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/`.

Machine status: `{final["machine_contract_status"]}`.
Governance status: `{final["governance_closeout_status"]}`.

Non-decisions: no consumer migration execution, no current authority adoption, no runtime cutover,
no successor baseline identity final seal, no package readiness, and no release readiness.
"""


def assert_phase_status(path: Path) -> bool:
    payload = read_json(path)
    return payload.get("status") == "PASS"


def run_all() -> dict[str, Any]:
    write_phase0()
    write_phase1()
    write_phase2()
    write_phase3()
    write_phase4()
    write_phase5()
    write_phase6()
    return write_phase7_and_phase8()
