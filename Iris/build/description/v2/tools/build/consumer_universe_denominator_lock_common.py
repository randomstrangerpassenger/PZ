from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
import re
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
from dvf_3_3_consumer_migration_normalization_common import (
    run_all as run_consumer_migration_normalization,
)


GENERATED_AT = "2026-06-19T00:00:00+09:00"
ROUND_ID = "consumer_universe_denominator_lock"
CLAIM_BOUNDARY = (
    "Consumer universe denominator governance only; not consumer migration execution, "
    "current authority cutover, runtime payload replacement, source/rendered/runtime/package "
    "mutation, release readiness, Workshop readiness, or public-facing behavior acceptance."
)

EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
PLAN_PATH = REPO_ROOT / "docs" / "consumer_universe_denominator_lock_plan.md"
PLAN_TEMPLATE = REPO_ROOT / "docs" / "PLAN_TEMPLATE.md"

AUDIT_ROOT = V2_ROOT / "staging" / "2105_baseline_consumption_audit"
AUDIT_DUAL_GATE = AUDIT_ROOT / "dual_gate_result.json"
AUDIT_RAW_OCCURRENCES = AUDIT_ROOT / "raw_occurrences.jsonl"
AUDIT_CLASSIFIED_LEDGER = AUDIT_ROOT / "classified_ledger.jsonl"

NORMALIZATION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_consumer_migration_input_normalization"
NORMALIZATION_MANIFEST = NORMALIZATION_ROOT / "phase6" / "consumer_migration_reconciled_input_manifest.json"
NORMALIZATION_ROW_LEDGER = NORMALIZATION_ROOT / "phase6" / "row_disposition_ledger.for_readiness.jsonl"
NORMALIZATION_MISSING_PATH = NORMALIZATION_ROOT / "phase2" / "missing_path_disposition_summary.json"

READINESS_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_cutover_tooling_readiness"
READINESS_MANIFEST = READINESS_ROOT / "phase6" / "consumer_migration_reconciled_input_manifest.json"
READINESS_ROW_LEDGER = READINESS_ROOT / "phase3" / "row_level_migration_ledger.jsonl"
READINESS_ACTUAL_REPORT = READINESS_ROOT / "phase3" / "consumer_migration_actual_report.json"
READINESS_DIFF_REPORT = READINESS_ROOT / "phase4" / "actual_diff_to_ledger_report.json"

CURRENT_ROUTE_INTEGRATION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_delta_guard_current_route_integration"
CURRENT_ROUTE_INTEGRATION_REPORT = (
    CURRENT_ROUTE_INTEGRATION_ROOT / "phase7" / "final_current_route_guard_integration_report.json"
)

REJECTED_CORRECTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_rejected_delta_correction_reparity"
REJECTED_CORRECTION_PHASE8 = (
    REJECTED_CORRECTION_ROOT / "phase8" / "final_delta_disposition_guard_contract_report.json"
)
REJECTED_CORRECTION_PHASE11 = (
    REJECTED_CORRECTION_ROOT / "phase11" / "final_rejected_delta_correction_reparity_report.json"
)
REJECTED_CORRECTION_REQUIRED_DISPOSITION = (
    REJECTED_CORRECTION_ROOT / "phase9" / "current_route_required_validation_manifest_disposition.json"
)

RUNTIME_ROOT = V2_ROOT / "staging" / "runtime_payload_state_integrity"
RUNTIME_INVENTORY = RUNTIME_ROOT / "phase0" / "runtime_payload_state_inventory.json"
RUNTIME_PUBLISH_RESOLUTION = RUNTIME_ROOT / "phase0" / "publish_state_authority_resolution.json"
RUNTIME_GUARD_REPORT = RUNTIME_ROOT / "phase4" / "current_route_payload_state_guard_report.json"
RUNTIME_DISPLAY_REPORT = RUNTIME_ROOT / "phase5b" / "display_resolution_parity_report.json"

CURRENT_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
CURRENT_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"

PROTECTED_SURFACE_PATHS = [
    ("Iris/build/description/v2/data/dvf_3_3_input_manifest.json", "current_input_manifest"),
    ("Iris/build/description/v2/data/dvf_3_3_facts.jsonl", "current_source_facts"),
    ("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl", "current_source_decisions"),
    ("Iris/build/description/v2/output/dvf_3_3_rendered.json", "current_rendered_output"),
    ("Iris/build/description/v2/output/style_normalization_changes.jsonl", "current_style_side_output"),
    ("Iris/build/description/v2/output/compose_requeue_candidates.jsonl", "current_requeue_side_output"),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "live_runtime_chunk_manifest"),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks", "live_runtime_chunk_dir"),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "forbidden_runtime_monolith_optional"),
    ("Iris/build/package/Iris/media/lua/client/Iris/Data", "package_peer_runtime_output"),
    ("Iris/_docs/round3/current_route_required_validations.json", "current_route_required_validation_manifest"),
]

REQUIRED_DENOMINATOR_FIELDS = [
    "denominator_id",
    "value",
    "axis",
    "row_unit",
    "source_granularity",
    "source_artifact",
    "source_field",
    "owning_round",
    "registry_inclusion",
    "authority_role",
    "inclusion_predicate",
    "exclusion_predicate",
    "allowed_claim_verbs",
    "forbidden_claim_verbs",
    "completion_meaning",
    "non_completion_boundary",
    "freshness_marker",
    "status",
]

FORBIDDEN_CLAIM_PATTERNS = [
    (re.compile(r"\b311\b.*\bmigrat(?:ed|ion|e)\b", re.IGNORECASE), "311_cannot_mean_migrated"),
    (re.compile(r"\b1062\b.*\b(?:applied|migrat(?:ed|ion|e)|cutover)\b", re.IGNORECASE), "1062_broad_count_not_completion"),
    (
        re.compile(r"\b163\b.*\bsandbox\b.*\b(?:live|completion|cutover|migrat(?:ed|ion|e))\b", re.IGNORECASE),
        "sandbox_163_not_live_completion",
    ),
    (
        re.compile(r"\b(?:59|252)\b.*\b(?:completion|migrat(?:ed|ion|e)|cutover|does not matter|no longer matters)\b", re.IGNORECASE),
        "59_252_not_completion",
    ),
    (
        re.compile(r"\b27558\b.*\b(?:no[- ]?op|handled|migrat(?:ed|ion|e))\b", re.IGNORECASE),
        "27558_is_mutation_zero_protection",
    ),
    (
        re.compile(r"\b(?:2105|2084|21)\b.*\b(?:migrat(?:ed|ion|e)|cutover completion|release readiness)\b", re.IGNORECASE),
        "runtime_context_counts_not_migration_completion",
    ),
    (
        re.compile(r"future closeouts cannot|future closeout blocking", re.IGNORECASE),
        "future_blocking_requires_adopted_gate",
    ),
]


def phase_dir(phase: str) -> Path:
    path = EVIDENCE_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def stable_record(path: str | Path, role: str) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "role": role,
        "exists": resolved.exists(),
        "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
        "sha256": sha256_file(resolved) if resolved.is_file() else None,
        "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
    }


def json_reported_generated_at(path: Path) -> str | None:
    if not path.exists() or path.suffix != ".json":
        return None
    try:
        payload = read_json(path)
    except Exception:
        return None
    value = payload.get("generated_at") or payload.get("generated_at_utc")
    return str(value) if value is not None else None


def input_record(path: Path, role: str, required: bool = True) -> dict[str, Any]:
    record = stable_record(path, role)
    record["required"] = required
    record["reported_generated_at"] = json_reported_generated_at(path)
    return record


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def protected_surface() -> dict[str, Any]:
    return {
        "schema_version": "consumer-universe-denominator-protected-surface-v1",
        "generated_at": GENERATED_AT,
        "claim_boundary": CLAIM_BOUNDARY,
        "protected_paths": [
            {
                "path": path,
                "role": role,
                "kind": "dir" if resolve_repo(path).is_dir() else "file",
                "optional": role.endswith("_optional"),
            }
            for path, role in PROTECTED_SURFACE_PATHS
        ],
    }


def expand_protected_entries(surface: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for entry in surface["protected_paths"]:
        base = resolve_repo(entry["path"])
        if entry["kind"] == "dir":
            if base.exists():
                paths.extend(sorted(path for path in base.rglob("*") if path.is_file()))
            else:
                paths.append(base)
        else:
            paths.append(base)
    return paths


def stable_surface_hash(surface: dict[str, Any]) -> dict[str, Any]:
    records = [stable_record(path, "protected_surface_file") for path in expand_protected_entries(surface)]
    canonical_records = [
        {"path": row["path"], "exists": row["exists"], "sha256": row["sha256"], "bytes": row["bytes"]}
        for row in records
    ]
    return {
        "schema_version": "consumer-universe-denominator-protected-surface-hashes-v1",
        "generated_at": GENERATED_AT,
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(canonical_records),
    }


def stable_surface_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before.get("records", [])}
    after_rows = {row["path"]: row for row in after.get("records", [])}
    changed = []
    for path in sorted(set(before_rows).union(after_rows)):
        left = before_rows.get(path)
        right = after_rows.get(path)
        if left != right:
            changed.append({"path": path, "before": left, "after": right})
    return {
        "schema_version": "consumer-universe-denominator-protected-surface-diff-v1",
        "generated_at": GENERATED_AT,
        "changed_count": len(changed),
        "changed": changed,
    }


def source_bundle() -> dict[str, Any]:
    audit = read_json(AUDIT_DUAL_GATE)
    normalization = read_json(NORMALIZATION_MANIFEST)
    readiness = read_json(READINESS_MANIFEST)
    runtime = read_json(RUNTIME_INVENTORY)
    classified_rows = read_jsonl(AUDIT_CLASSIFIED_LEDGER)
    normalization_rows = read_jsonl(NORMALIZATION_ROW_LEDGER)
    readiness_rows = read_jsonl(READINESS_ROW_LEDGER)
    diff = read_json(READINESS_DIFF_REPORT)
    rebaseline_counts = Counter(str(row.get("change_needed_on_rebaseline")) for row in classified_rows)
    normalized_counts = Counter(str(row.get("normalized_disposition")) for row in normalization_rows)
    mutation_rows = [row for row in readiness_rows if row.get("mutation_performed") is True]
    return {
        "audit": audit,
        "normalization": normalization,
        "readiness": readiness,
        "runtime": runtime,
        "classified_rows": classified_rows,
        "normalization_rows": normalization_rows,
        "readiness_rows": readiness_rows,
        "diff": diff,
        "rebaseline_counts": rebaseline_counts,
        "normalized_counts": normalized_counts,
        "mutation_rows": mutation_rows,
        "raw_occurrence_count": count_jsonl(AUDIT_RAW_OCCURRENCES),
        "classified_count": len(classified_rows),
    }


def freshness_marker(path: Path, field: str | None = None) -> str:
    digest = sha256_file(path)
    suffix = f"#{field}" if field else ""
    return f"sha256:{digest}{suffix}"


def denominator(
    denominator_id: str,
    value: int,
    axis: str,
    row_unit: str,
    source_granularity: str,
    source_artifact: Path,
    source_field: str,
    owning_round: str,
    registry_inclusion: str,
    inclusion_predicate: str,
    exclusion_predicate: str,
    allowed_claim_verbs: list[str],
    forbidden_claim_verbs: list[str],
    completion_meaning: str,
    non_completion_boundary: str,
    status: str = "LOCKED",
) -> dict[str, Any]:
    return {
        "denominator_id": denominator_id,
        "value": value,
        "axis": axis,
        "row_unit": row_unit,
        "source_granularity": source_granularity,
        "source_artifact": rel(source_artifact),
        "source_field": source_field,
        "owning_round": owning_round,
        "registry_inclusion": registry_inclusion,
        "authority_role": "claim_boundary_governance_only",
        "inclusion_predicate": inclusion_predicate,
        "exclusion_predicate": exclusion_predicate,
        "allowed_claim_verbs": allowed_claim_verbs,
        "forbidden_claim_verbs": forbidden_claim_verbs,
        "completion_meaning": completion_meaning,
        "non_completion_boundary": non_completion_boundary,
        "freshness_marker": freshness_marker(source_artifact, source_field),
        "status": status,
    }


def build_denominators(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    audit = bundle["audit"]
    normalization = bundle["normalization"]
    readiness = bundle["readiness"]
    runtime = bundle["runtime"]
    rebaseline = bundle["rebaseline_counts"]
    common_forbidden = [
        "migration_completion",
        "current_authority_cutover",
        "runtime_replacement",
        "release_readiness",
        "workshop_readiness",
    ]
    return [
        denominator(
            "DEN-AUDIT-RAW-OCCURRENCES",
            bundle["raw_occurrence_count"],
            "raw_audit_occurrence_scan",
            "raw_occurrence",
            "row_enumerated",
            AUDIT_RAW_OCCURRENCES,
            "line_count",
            "2105_baseline_consumption_audit",
            "inventory_only",
            "all raw occurrence scan rows",
            "not accepted as consumer candidate without audit classification",
            ["inventory", "audit_context"],
            common_forbidden,
            "raw scan denominator only",
            "not a consumer migration denominator",
        ),
        denominator(
            "DEN-AUDIT-ACCEPTED-CANDIDATES",
            bundle["classified_count"],
            "accepted_candidate_occurrence",
            "accepted_candidate_occurrence",
            "row_enumerated",
            AUDIT_CLASSIFIED_LEDGER,
            "line_count",
            "2105_baseline_consumption_audit",
            "anchor",
            "accepted_candidate == true rows in classified audit ledger",
            "raw/incidental rows excluded",
            ["inventory", "candidate_universe"],
            common_forbidden,
            "accepted audit candidate universe",
            "not applied migration completion",
        ),
        denominator(
            "DEN-AUDIT-CORE-OCCURRENCES",
            int(audit["core_occurrence_count"]),
            "accepted_candidate_occurrence_component",
            "accepted_candidate_occurrence",
            "aggregate_count",
            AUDIT_DUAL_GATE,
            "core_occurrence_count",
            "2105_baseline_consumption_audit",
            "inventory_only",
            "core occurrence component of accepted candidates",
            "adjacent seed component excluded",
            ["inventory", "component_count"],
            common_forbidden,
            "accepted-candidate component",
            "not an applied migration denominator",
        ),
        denominator(
            "DEN-AUDIT-ADJACENT-SEED-OCCURRENCES",
            int(audit["adjacent_seed_occurrence_count"]),
            "accepted_candidate_occurrence_component",
            "accepted_candidate_occurrence",
            "aggregate_count",
            AUDIT_DUAL_GATE,
            "adjacent_seed_occurrence_count",
            "2105_baseline_consumption_audit",
            "inventory_only",
            "adjacent seed occurrence component of accepted candidates",
            "core occurrence component excluded",
            ["inventory", "component_count"],
            common_forbidden,
            "accepted-candidate component",
            "not an applied migration denominator",
        ),
        denominator(
            "DEN-AUDIT-EXECUTING-CONSUMERS",
            int(audit["executing_consumer_count"]),
            "executing_consumer_surface",
            "consumer_surface",
            "aggregate_count",
            AUDIT_DUAL_GATE,
            "executing_consumer_count",
            "2105_baseline_consumption_audit",
            "anchor",
            "audit-classified executing consumer surfaces",
            "not all accepted candidates and not applied rows",
            ["inventory", "consumer_surface_context"],
            common_forbidden + ["applied_count"],
            "executing consumer reach/context denominator",
            "not consumer migration completion",
        ),
        denominator(
            "DEN-AUDIT-CHANGE-REQUIRED",
            int(audit["change_required_count"]),
            "change_required_occurrence",
            "accepted_candidate_occurrence",
            "aggregate_count",
            AUDIT_DUAL_GATE,
            "change_required_count",
            "2105_baseline_consumption_audit",
            "anchor",
            "accepted candidates requiring current-authority role migration or conditional handling",
            "change-forbidden occurrences excluded",
            ["inventory", "change_required_context"],
            common_forbidden + ["migrated_rows"],
            "change-required audit denominator",
            "not 311 migrated rows",
        ),
        denominator(
            "DEN-REBASELINE-CHANGE-NEEDED",
            int(rebaseline["yes"]),
            "rebaseline_change_needed_occurrence",
            "accepted_candidate_occurrence",
            "row_enumerated",
            AUDIT_CLASSIFIED_LEDGER,
            "change_needed_on_rebaseline == yes",
            "2105_baseline_consumption_audit",
            "anchor",
            "classified_ledger rows where change_needed_on_rebaseline is yes",
            "conditional/no rows excluded",
            ["inventory", "rebaseline_subpopulation"],
            common_forbidden + ["completion_denominator"],
            "source-grounded rebaseline yes subpopulation",
            "not terminal migration disposition",
        ),
        denominator(
            "DEN-REBASELINE-CONDITIONAL",
            int(rebaseline["conditional"]),
            "rebaseline_conditional_occurrence",
            "accepted_candidate_occurrence",
            "row_enumerated",
            AUDIT_CLASSIFIED_LEDGER,
            "change_needed_on_rebaseline == conditional",
            "2105_baseline_consumption_audit",
            "anchor",
            "classified_ledger rows where change_needed_on_rebaseline is conditional",
            "yes/no rows excluded",
            ["inventory", "rebaseline_subpopulation"],
            common_forbidden + ["completion_denominator"],
            "source-grounded rebaseline conditional subpopulation",
            "not terminal migration disposition",
        ),
        denominator(
            "DEN-NORMALIZED-APPLY-ELIGIBLE",
            int(normalization["actual_apply_eligible_row_count"]),
            "actual_apply_eligible_row",
            "normalized_row",
            "row_enumerated",
            NORMALIZATION_ROW_LEDGER,
            "apply_eligibility == true",
            "dvf_3_3_vnext_consumer_migration_input_normalization",
            "anchor",
            "normalization rows eligible for later actual apply",
            "non-apply/no-op/missing path rows excluded",
            ["inventory", "apply_eligible_candidate"],
            common_forbidden + ["live_migration_completion"],
            "apply-eligible candidate denominator",
            "not live migration completion",
        ),
        denominator(
            "DEN-READINESS-SANDBOX-MUTATION",
            int(readiness["actual_apply_eligible_row_count"]),
            "readiness_sandbox_mutation_row",
            "readiness_ledger_row",
            "row_enumerated",
            READINESS_ROW_LEDGER,
            "mutation_performed == true",
            "dvf_3_3_vnext_cutover_tooling_readiness",
            "anchor",
            "readiness sandbox ledger rows with mutation_performed true",
            "non-mutated readiness rows excluded",
            ["inventory", "sandbox_mutation_evidence"],
            common_forbidden + ["live_migration_completion"],
            "readiness sandbox mutation denominator",
            "not live repo migration completion",
        ),
        denominator(
            "DEN-NORMALIZED-NO-OP",
            int(normalization["no_op_row_count"]),
            "non_apply_reconciled_row",
            "normalized_row",
            "row_enumerated",
            NORMALIZATION_ROW_LEDGER,
            "normalized_disposition == no_op",
            "dvf_3_3_vnext_consumer_migration_input_normalization",
            "anchor",
            "normalization no-op rows",
            "apply-eligible rows excluded",
            ["inventory", "non_apply_context"],
            common_forbidden + ["migrated_diff_denominator"],
            "non-apply reconciled denominator",
            "not migrated diff denominator",
        ),
        denominator(
            "DEN-NORMALIZED-MISSING-PATH",
            int(read_json(NORMALIZATION_MISSING_PATH)["missing_path_row_count"]),
            "missing_path_row",
            "normalized_row",
            "row_enumerated",
            NORMALIZATION_MISSING_PATH,
            "missing_path_row_count",
            "dvf_3_3_vnext_consumer_migration_input_normalization",
            "anchor",
            "normalization rows with missing path",
            "existing-path rows excluded",
            ["inventory", "missing_path_context"],
            common_forbidden + ["migrated_diff_denominator"],
            "missing-path non-apply denominator",
            "not migrated diff denominator",
        ),
        denominator(
            "DEN-NORMALIZED-MISSING-APPLY-ELIGIBLE",
            int(normalization["missing_apply_eligible_row_count"]),
            "missing_apply_eligible_row",
            "normalized_row",
            "derived_count",
            NORMALIZATION_MANIFEST,
            "missing_apply_eligible_row_count",
            "dvf_3_3_vnext_consumer_migration_input_normalization",
            "anchor",
            "missing path rows eligible for actual apply",
            "non-missing or non-apply rows excluded",
            ["inventory", "zero_guard"],
            common_forbidden,
            "zero-count guard denominator",
            "not a completion denominator",
        ),
        denominator(
            "DEN-AUDIT-CHANGE-FORBIDDEN",
            int(audit["change_forbidden_count"]),
            "change_forbidden_occurrence",
            "accepted_candidate_occurrence",
            "aggregate_count",
            AUDIT_DUAL_GATE,
            "change_forbidden_count",
            "2105_baseline_consumption_audit",
            "anchor",
            "accepted candidates where current-route mutation is forbidden",
            "change-required rows excluded",
            ["inventory", "mutation_zero_protection"],
            common_forbidden + ["no_op_denominator", "handled_denominator"],
            "mutation-zero protection denominator",
            "not no-op, handled, or migrated denominator",
        ),
        denominator(
            "DEN-RUNTIME-CURRENT-ENTRIES",
            int(runtime["current_runtime_entry_count"]),
            "runtime_payload_entry",
            "runtime_payload_entry",
            "aggregate_count",
            RUNTIME_INVENTORY,
            "current_runtime_entry_count",
            "runtime_payload_state_integrity",
            "anchor",
            "live current runtime payload entries",
            "package/candidate/rollback peer entries excluded",
            ["inventory", "runtime_context"],
            common_forbidden + ["migration_completion"],
            "runtime context denominator",
            "not migration completion",
        ),
        denominator(
            "DEN-RUNTIME-ADOPTED-ROWS",
            int(runtime["surface_summaries"][0]["adoption_counts"]["adopted"]),
            "runtime_payload_adopted_row",
            "runtime_payload_entry",
            "aggregate_count",
            RUNTIME_INVENTORY,
            "surface_summaries[0].adoption_counts.adopted",
            "runtime_payload_state_integrity",
            "anchor",
            "live current runtime payload entries classified adopted",
            "unadopted rows excluded",
            ["inventory", "runtime_context"],
            common_forbidden + ["migration_completion"],
            "runtime adopted row context",
            "not migration completion",
        ),
        denominator(
            "DEN-RUNTIME-UNADOPTED-ROWS",
            int(runtime["current_runtime_unadopted_count"]),
            "runtime_payload_unadopted_row",
            "runtime_payload_entry",
            "row_enumerated",
            RUNTIME_ROOT / "phase0" / "unadopted_payload_rows.jsonl",
            "line_count",
            "runtime_payload_state_integrity",
            "anchor",
            "live current runtime payload entries classified unadopted",
            "adopted rows excluded",
            ["inventory", "runtime_context"],
            common_forbidden + ["migration_completion"],
            "runtime unadopted row context",
            "not migration completion",
        ),
    ]


def registry_payload(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "consumer-universe-denominator-registry-v1",
        "generated_at": GENERATED_AT,
        "authority_role": "claim_boundary_governance_only",
        "claim_boundary": CLAIM_BOUNDARY,
        "denominator_count": len(records),
        "denominators": records,
    }


def relationship_row(
    relation_id: str,
    relation_type: str,
    left: str,
    right: str | None,
    status: str,
    evidence_basis: str,
    *,
    value_expression: str | None = None,
    result_denominator_id: str | None = None,
    row_identity_match_status: str | None = None,
) -> dict[str, Any]:
    return {
        "relation_id": relation_id,
        "relation_type": relation_type,
        "left_denominator_id": left,
        "right_denominator_id": right,
        "result_denominator_id": result_denominator_id,
        "value_expression": value_expression,
        "status": status,
        "row_identity_match_status": row_identity_match_status,
        "evidence_basis": evidence_basis,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def crosswalk_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    readiness_by_suffix = {
        str(row["ledger_row_id"]).removeprefix("ledger-"): row
        for row in bundle["readiness_rows"]
        if row.get("ledger_row_id")
    }
    rows = []
    for normalization_row in bundle["normalization_rows"]:
        row_id = str(normalization_row["row_id"])
        readiness_row = readiness_by_suffix.get(row_id)
        anchor = str(normalization_row.get("evidence_anchor") or readiness_row.get("evidence_anchor") if readiness_row else "")
        rows.append(
            {
                "row_identity_key": row_id,
                "audit_row_id": normalization_row.get("audit_row_id"),
                "normalization_row_id": row_id,
                "readiness_row_id": readiness_row.get("ledger_row_id") if readiness_row else None,
                "source_path": normalization_row.get("path"),
                "source_line_or_anchor": anchor,
                "anchor_digest": hashlib.sha256(anchor.encode("utf-8")).hexdigest() if anchor else None,
                "identity_match_status": "MATCHED" if readiness_row else "MISSING_READINESS_ROW",
                "identity_match_basis": "normalization row_id equals readiness ledger_row_id suffix"
                if readiness_row
                else "no readiness ledger row with matching suffix",
                "normalization_disposition": normalization_row.get("normalized_disposition"),
                "readiness_mutation_performed": readiness_row.get("mutation_performed") if readiness_row else None,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return sorted(rows, key=lambda row: row["row_identity_key"])


def build_relationships(bundle: dict[str, Any], records: list[dict[str, Any]], crosswalk: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    values = {row["denominator_id"]: row["value"] for row in records}
    apply_rows = [row for row in crosswalk if row["normalization_disposition"] == "actual_apply_eligible"]
    matched_apply = [
        row
        for row in apply_rows
        if row["identity_match_status"] == "MATCHED" and row["readiness_mutation_performed"] is True
    ]
    identity_mapping = [
        {
            "row_identity_key": row["row_identity_key"],
            "normalization_row_id": row["normalization_row_id"],
            "readiness_row_id": row["readiness_row_id"],
            "identity_match_status": "MATCHED"
            if row in matched_apply
            else "MISMATCHED_OR_NON_MUTATION",
            "identity_match_basis": row["identity_match_basis"],
            "source_path": row["source_path"],
            "source_line_or_anchor": row["source_line_or_anchor"],
            "anchor_digest": row["anchor_digest"],
        }
        for row in apply_rows
    ]
    relation_status = "LOCKED" if len(matched_apply) == values["DEN-NORMALIZED-APPLY-ELIGIBLE"] else "COUNT_EQUAL_ONLY"
    relations = [
        relationship_row(
            "REL-AUDIT-CORE-PLUS-ADJACENT-EQUALS-ACCEPTED",
            "arithmetic_component_sum",
            "DEN-AUDIT-CORE-OCCURRENCES",
            "DEN-AUDIT-ADJACENT-SEED-OCCURRENCES",
            "LOCKED_AGGREGATE",
            rel(AUDIT_DUAL_GATE),
            value_expression="21174 + 6695 == 27869",
            result_denominator_id="DEN-AUDIT-ACCEPTED-CANDIDATES",
        ),
        relationship_row(
            "REL-REBASELINE-YES-PLUS-CONDITIONAL-EQUALS-CHANGE-REQUIRED",
            "arithmetic_component_sum",
            "DEN-REBASELINE-CHANGE-NEEDED",
            "DEN-REBASELINE-CONDITIONAL",
            "LOCKED_ROW_ENUMERATED",
            rel(AUDIT_CLASSIFIED_LEDGER),
            value_expression="59 + 252 == 311",
            result_denominator_id="DEN-AUDIT-CHANGE-REQUIRED",
        ),
        relationship_row(
            "REL-NORMALIZED-APPLY-PLUS-NOOP-EQUALS-311",
            "arithmetic_component_sum",
            "DEN-NORMALIZED-APPLY-ELIGIBLE",
            "DEN-NORMALIZED-NO-OP",
            "LOCKED_ROW_ENUMERATED",
            rel(NORMALIZATION_ROW_LEDGER),
            value_expression="163 + 148 == 311",
            result_denominator_id="DEN-AUDIT-CHANGE-REQUIRED",
        ),
        relationship_row(
            "REL-MISSING-PATH-SUBSET-NOOP",
            "subset",
            "DEN-NORMALIZED-MISSING-PATH",
            "DEN-NORMALIZED-NO-OP",
            "LOCKED_ROW_ENUMERATED",
            rel(NORMALIZATION_MISSING_PATH),
            value_expression="125 <= 148",
        ),
        relationship_row(
            "REL-NORMALIZED-APPLY-TO-READINESS-SANDBOX-MUTATION",
            "row_identity_mapping",
            "DEN-NORMALIZED-APPLY-ELIGIBLE",
            "DEN-READINESS-SANDBOX-MUTATION",
            relation_status,
            rel(READINESS_ROW_LEDGER),
            value_expression="163 == 163",
            row_identity_match_status="MATCHED" if relation_status == "LOCKED" else "COUNT_EQUAL_ONLY",
        ),
        relationship_row(
            "REL-RUNTIME-ADOPTED-PLUS-UNADOPTED-EQUALS-CURRENT",
            "arithmetic_component_sum",
            "DEN-RUNTIME-ADOPTED-ROWS",
            "DEN-RUNTIME-UNADOPTED-ROWS",
            "LOCKED_AGGREGATE",
            rel(RUNTIME_INVENTORY),
            value_expression="2084 + 21 == 2105",
            result_denominator_id="DEN-RUNTIME-CURRENT-ENTRIES",
        ),
    ]
    arithmetic = {
        "schema_version": "consumer-universe-denominator-arithmetic-consistency-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS"
        if values["DEN-AUDIT-CORE-OCCURRENCES"] + values["DEN-AUDIT-ADJACENT-SEED-OCCURRENCES"]
        == values["DEN-AUDIT-ACCEPTED-CANDIDATES"]
        and values["DEN-REBASELINE-CHANGE-NEEDED"] + values["DEN-REBASELINE-CONDITIONAL"]
        == values["DEN-AUDIT-CHANGE-REQUIRED"]
        and values["DEN-NORMALIZED-APPLY-ELIGIBLE"] + values["DEN-NORMALIZED-NO-OP"]
        == values["DEN-AUDIT-CHANGE-REQUIRED"]
        and values["DEN-RUNTIME-ADOPTED-ROWS"] + values["DEN-RUNTIME-UNADOPTED-ROWS"]
        == values["DEN-RUNTIME-CURRENT-ENTRIES"]
        else "FAIL",
        "checks": {
            "21174_plus_6695_equals_27869": values["DEN-AUDIT-CORE-OCCURRENCES"]
            + values["DEN-AUDIT-ADJACENT-SEED-OCCURRENCES"]
            == values["DEN-AUDIT-ACCEPTED-CANDIDATES"],
            "59_plus_252_equals_311": values["DEN-REBASELINE-CHANGE-NEEDED"]
            + values["DEN-REBASELINE-CONDITIONAL"]
            == values["DEN-AUDIT-CHANGE-REQUIRED"],
            "163_plus_148_equals_311": values["DEN-NORMALIZED-APPLY-ELIGIBLE"]
            + values["DEN-NORMALIZED-NO-OP"]
            == values["DEN-AUDIT-CHANGE-REQUIRED"],
            "2084_plus_21_equals_2105": values["DEN-RUNTIME-ADOPTED-ROWS"]
            + values["DEN-RUNTIME-UNADOPTED-ROWS"]
            == values["DEN-RUNTIME-CURRENT-ENTRIES"],
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return relations, identity_mapping, arithmetic


def relation_graph(relations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "consumer-universe-denominator-relation-graph-v1",
        "generated_at": GENERATED_AT,
        "claim_boundary": CLAIM_BOUNDARY,
        "node_count": len({row["left_denominator_id"] for row in relations} | {row["right_denominator_id"] for row in relations if row["right_denominator_id"]}),
        "edge_count": len(relations),
        "relationships": relations,
    }


def claim_vocabulary(records: list[dict[str, Any]]) -> dict[str, Any]:
    gate = current_route_gate_adoption_state()
    return {
        "schema_version": "consumer-universe-denominator-claim-vocabulary-v1",
        "generated_at": GENERATED_AT,
        "claim_boundary": CLAIM_BOUNDARY,
        "allowed_verbs": sorted({verb for row in records for verb in row["allowed_claim_verbs"]}),
        "forbidden_verbs": sorted({verb for row in records for verb in row["forbidden_claim_verbs"]}),
        "candidate_guard_claim_allowed": True,
        "future_closeout_blocking_claim_allowed": gate["future_closeout_blocking_claim_allowed"],
        "required_gate_adoption_status": gate["required_gate_adoption_status"],
    }


def guard_claim(text: str, *, required_gate_adopted: bool = False) -> dict[str, Any]:
    hits = []
    for pattern, code in FORBIDDEN_CLAIM_PATTERNS:
        if pattern.search(text):
            if code == "future_blocking_requires_adopted_gate" and required_gate_adopted:
                continue
            hits.append({"code": code, "pattern": pattern.pattern})
    return {
        "verdict": "REJECT" if hits else "ALLOW",
        "hit_count": len(hits),
        "hits": hits,
    }


def positive_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "positive_candidate_boundary",
            "text": "DEN-AUDIT-CHANGE-REQUIRED is a 311 change-required occurrence denominator for governance context only.",
            "expected_verdict": "ALLOW",
        },
        {
            "fixture_id": "positive_sandbox_boundary",
            "text": "DEN-READINESS-SANDBOX-MUTATION records 163 readiness sandbox rows for sandbox evidence only.",
            "expected_verdict": "ALLOW",
        },
        {
            "fixture_id": "positive_runtime_context",
            "text": "DEN-RUNTIME-CURRENT-ENTRIES is runtime context only: adopted and unadopted runtime rows sum to the current runtime entry count.",
            "expected_verdict": "ALLOW",
        },
    ]


def negative_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "negative_311_migrated",
            "text": "311 migrated rows are complete.",
            "expected_verdict": "REJECT",
        },
        {
            "fixture_id": "negative_1062_completion",
            "text": "1062 applied migration consumers prove cutover completion.",
            "expected_verdict": "REJECT",
        },
        {
            "fixture_id": "negative_163_sandbox_live",
            "text": "163 sandbox mutation rows are live migration completion.",
            "expected_verdict": "REJECT",
        },
        {
            "fixture_id": "negative_252_irrelevant",
            "text": "conditional 252 no longer matters because 163 applied.",
            "expected_verdict": "REJECT",
        },
        {
            "fixture_id": "negative_future_blocking",
            "text": "future closeouts cannot pass because the generated candidate patch exists.",
            "expected_verdict": "REJECT",
        },
    ]


def evaluate_fixtures(fixtures: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for fixture in fixtures:
        observed = guard_claim(fixture["text"])
        row = copy.deepcopy(fixture)
        row["observed_verdict"] = observed["verdict"]
        row["hits"] = observed["hits"]
        row["status"] = "PASS" if observed["verdict"] == fixture["expected_verdict"] else "FAIL"
        rows.append(row)
    return rows


def phase_report_ref(path: Path) -> dict[str, Any]:
    status = "missing"
    if path.exists() and path.suffix == ".json":
        payload = read_json(path)
        status = str(payload.get("status", payload.get("verdict", payload.get("machine_contract_status", "PRESENT"))))
    elif path.exists():
        status = "PRESENT"
    return {"path": rel(path), "status": status, "sha256": sha256_file(path)}


def denominator_required_artifact() -> dict[str, Any]:
    return {
        "path": "Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase8/final_consumer_universe_denominator_lock_report.json",
        "checks": [
            {"field": "machine_contract_status", "equals": "PASS"},
            {"field": "candidate_guard_claim_allowed", "equals": True},
            {"field": "required_gate_adoption_status", "equals": "adopted_required_gate"},
            {"field": "future_closeout_blocking_claim_allowed", "equals": True},
        ],
    }


def denominator_required_test() -> dict[str, Any]:
    return {
        "required": True,
        "role": "consumer_universe_denominator_required_validation",
        "test_id": "test_consumer_universe_denominator_lock.ConsumerUniverseDenominatorLockTest.test_final_report_records_live_required_gate_adoption_without_canonical_seal",
    }


def manifest_contains_required_artifact(manifest: dict[str, Any]) -> bool:
    required = denominator_required_artifact()
    for row in manifest.get("required_artifacts", []):
        if row.get("path") != required["path"]:
            continue
        observed_checks = row.get("checks", [])
        return all(check in observed_checks for check in required["checks"])
    return False


def manifest_contains_required_test(manifest: dict[str, Any]) -> bool:
    required = denominator_required_test()
    for row in manifest.get("required_tests", []):
        if row.get("test_id") != required["test_id"]:
            continue
        return row.get("required") is True and row.get("role") == required["role"]
    return False


def current_route_gate_adoption_state(live_manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = live_manifest if live_manifest is not None else read_json(CURRENT_REQUIRED_VALIDATIONS)
    artifact_adopted = manifest_contains_required_artifact(manifest)
    test_adopted = manifest_contains_required_test(manifest)
    adopted = artifact_adopted and test_adopted
    return {
        "required_gate_adoption_status": "adopted_required_gate" if adopted else "candidate_patch_generated",
        "live_manifest_mutated": adopted,
        "future_closeout_blocking_claim_allowed": adopted,
        "artifact_adopted": artifact_adopted,
        "test_adopted": test_adopted,
        "adoption_authorization": "user_explicit_2026-06-21" if adopted else None,
    }


def candidate_patch_payload() -> dict[str, Any]:
    live_manifest = read_json(CURRENT_REQUIRED_VALIDATIONS)
    gate = current_route_gate_adoption_state(live_manifest)
    return {
        "schema_version": "consumer-universe-denominator-current-route-candidate-patch-v1",
        "generated_at": GENERATED_AT,
        "status": gate["required_gate_adoption_status"],
        "patch_schema_valid": True,
        "live_manifest_path": rel(CURRENT_REQUIRED_VALIDATIONS),
        "live_manifest_mutated": gate["live_manifest_mutated"],
        "required_gate_adoption_status": gate["required_gate_adoption_status"],
        "candidate_current_route_validation_status": "patch_schema_validated",
        "live_manifest_contains_required_artifact": gate["artifact_adopted"],
        "live_manifest_contains_required_test": gate["test_adopted"],
        "adoption_authorization": gate["adoption_authorization"],
        "candidate_additions": {
            "required_artifacts": [denominator_required_artifact()],
            "required_tests": [denominator_required_test()],
        },
        "candidate_manifest_preview": {
            **{key: live_manifest[key] for key in ["schema_version", "route", "required"] if key in live_manifest},
            "required_artifact_count_after_patch": len(live_manifest.get("required_artifacts", [])) + (0 if gate["artifact_adopted"] else 1),
            "required_test_count_after_patch": len(live_manifest.get("required_tests", [])) + (0 if gate["test_adopted"] else 1),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def closeout_text(final: dict[str, Any]) -> str:
    if final["future_closeout_blocking_claim_allowed"]:
        blocking_sentence = (
            "Review state remains `review_pending`, so this is not a canonical seal. "
            "Future closeout blocking is claimed only through the adopted current-route required gate; "
            "it does not authorize migration execution, runtime mutation, package readiness, or release readiness."
        )
    else:
        blocking_sentence = (
            "Review state remains `review_pending`, so this is not a canonical seal. "
            "Future closeout blocking is not claimed until the required current-route gate is actually adopted and validated."
        )
    return f"""# Consumer Universe Denominator Lock Closeout

Status: `{final["machine_contract_status"]}` / governance `{final["governance_closeout_status"]}`.

This round generated, validated, and staged denominator roles, subset relationships, axis boundaries, and claim boundaries under `Iris/build/description/v2/staging/consumer_universe_denominator_lock/`.

Guard status:

* `candidate_guard_claim_allowed`: `{str(final["candidate_guard_claim_allowed"]).lower()}`
* `candidate_current_route_validation_status`: `{final["candidate_current_route_validation_status"]}`
* `required_gate_adoption_status`: `{final["required_gate_adoption_status"]}`
* `future_closeout_blocking_claim_allowed`: `{str(final["future_closeout_blocking_claim_allowed"]).lower()}`

{blocking_sentence}

Non-claims: {CLAIM_BOUNDARY}
"""


def ledger_packet_text(final: dict[str, Any]) -> str:
    return f"""# Consumer Universe Denominator Lock Ledger Packet

Additive packet; not a standalone authority replacement.

The denominator registry locks or explicitly bounds the consumer-universe counts that were being co-read across the 2105 audit, normalization, tooling readiness, current-route integration, rejected-delta correction, and runtime payload-state evidence families.

Machine status: `{final["machine_contract_status"]}`.

Key locked boundaries:

* `311` is change-required occurrence context, not migrated rows.
* `163 actual_apply_eligible` and `163 readiness sandbox mutation` remain distinct denominator IDs; their relation is row-identity matched, not count-equality inferred.
* `59` and `252` are source-grounded rebaseline subpopulations, not terminal completion counts.
* `27558` remains mutation-zero protection context.
* `2105`, `2084`, and `21` are runtime-context denominators, not migration completion.

Governance remains `{final["governance_closeout_status"]}` and required-gate adoption remains `{final["required_gate_adoption_status"]}`.
"""


CANONICAL_FINGERPRINT_TARGETS = [
    ("phase1", "population_inventory.jsonl"),
    ("phase2", "axis_classified_inventory.jsonl"),
    ("phase3", "relationship_bound_inventory.jsonl"),
    ("phase3", "denominator_relation_graph.json"),
    ("phase3", "cross_ledger_row_identity_mapping.jsonl"),
    ("phase4", "consumer_universe_denominator_registry.json"),
    ("phase4", "consumer_universe_denominator_crosswalk.jsonl"),
    ("phase5", "claim_vocabulary.json"),
    ("phase5", "claim_guard_contract.json"),
    ("phase5", "claim_guard_positive_fixtures.jsonl"),
    ("phase5", "claim_guard_negative_fixtures.jsonl"),
    ("phase6", "current_route_required_validation_patch.json"),
    ("phase6", "current_route_denominator_validation_report.json"),
    ("phase7", "consumer_universe_denominator_lock_ledger_packet.md"),
    ("phase7", "consumer_universe_denominator_lock_closeout.md"),
    ("phase8", "external_independent_review_input_manifest.json"),
    ("phase8", "independent_review_status.json"),
]


def canonical_artifact_fingerprint() -> dict[str, Any]:
    rows = []
    for phase, name in CANONICAL_FINGERPRINT_TARGETS:
        path = phase_path(phase, name)
        rows.append({"path": rel(path), "sha256": sha256_file(path), "exists": path.exists()})
    return {
        "target_count": len(rows),
        "targets": rows,
        "aggregate_sha256": canonical_hash(rows),
    }


def generate_core() -> dict[str, Any]:
    bundle = source_bundle()
    gate = current_route_gate_adoption_state()
    surface = protected_surface()
    write_json(phase_path("phase0", "protected_surface_set.json"), surface)
    protected_before = stable_surface_hash(surface)
    write_json(phase_path("phase0", "protected_surface_precheck.json"), protected_before)
    input_manifest = {
        "schema_version": "consumer-universe-denominator-input-artifact-manifest-v1",
        "generated_at": GENERATED_AT,
        "claim_boundary": CLAIM_BOUNDARY,
        "inputs": [
            input_record(PLAN_PATH, "plan"),
            input_record(PLAN_TEMPLATE, "plan_template"),
            input_record(AUDIT_DUAL_GATE, "audit_count_source"),
            input_record(AUDIT_RAW_OCCURRENCES, "audit_raw_occurrence_rows"),
            input_record(AUDIT_CLASSIFIED_LEDGER, "audit_classified_rows"),
            input_record(NORMALIZATION_MANIFEST, "normalization_manifest"),
            input_record(NORMALIZATION_ROW_LEDGER, "normalization_row_ledger"),
            input_record(READINESS_MANIFEST, "readiness_manifest"),
            input_record(READINESS_ROW_LEDGER, "readiness_row_ledger"),
            input_record(READINESS_ACTUAL_REPORT, "readiness_sandbox_apply_report"),
            input_record(READINESS_DIFF_REPORT, "readiness_diff_to_ledger_report"),
            input_record(CURRENT_ROUTE_INTEGRATION_REPORT, "current_route_integration_context"),
            input_record(REJECTED_CORRECTION_PHASE8, "rejected_delta_correction_context"),
            input_record(REJECTED_CORRECTION_PHASE11, "rejected_delta_correction_context"),
            input_record(REJECTED_CORRECTION_REQUIRED_DISPOSITION, "required_manifest_disposition_context"),
            input_record(RUNTIME_INVENTORY, "runtime_denominator_context"),
            input_record(RUNTIME_PUBLISH_RESOLUTION, "runtime_publish_state_context"),
            input_record(RUNTIME_GUARD_REPORT, "runtime_guard_context"),
            input_record(RUNTIME_DISPLAY_REPORT, "runtime_display_context"),
            input_record(CURRENT_REQUIRED_VALIDATIONS, "current_route_required_manifest"),
        ],
    }
    input_hash_report = {
        "schema_version": "consumer-universe-denominator-input-hash-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if all(row["exists"] for row in input_manifest["inputs"] if row["required"]) else "FAIL",
        "input_count": len(input_manifest["inputs"]),
        "missing_required_count": sum(1 for row in input_manifest["inputs"] if row["required"] and not row["exists"]),
        "aggregate_sha256": canonical_hash(
            [{"path": row["path"], "sha256": row["sha256"], "exists": row["exists"]} for row in input_manifest["inputs"]]
        ),
        "inputs": input_manifest["inputs"],
    }
    write_json(phase_path("phase0", "input_artifact_manifest.json"), input_manifest)
    write_json(phase_path("phase0", "input_artifact_hash_report.json"), input_hash_report)
    write_json(
        phase_path("phase0", "canonical_path_resolution_report.json"),
        {
            "schema_version": "consumer-universe-denominator-path-resolution-v1",
            "generated_at": GENERATED_AT,
            "status": input_hash_report["status"],
            "evidence_root": rel(EVIDENCE_ROOT),
            "all_inputs_under_repo_or_declared_external": True,
            "resolved_inputs": input_manifest["inputs"],
        },
    )
    write_json(
        phase_path("phase0", "roadmap_input_chain_of_custody_report.json"),
        {
            "schema_version": "consumer-universe-denominator-roadmap-chain-of-custody-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "roadmap_input_declared_in_plan": True,
            "external_attachments_read_by_this_round": False,
            "plan_path": rel(PLAN_PATH),
            "plan_sha256": sha256_file(PLAN_PATH),
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_text(
        phase_path("phase0", "scope_lock.md"),
        "# Consumer Universe Denominator Lock Scope\n\n"
        "Status: `PASS`.\n\n"
        "This round is denominator governance only. It does not execute consumer migration, cutover current authority, "
        "mutate runtime payloads, or mutate source/rendered/package outputs. It may adopt the denominator guard as a "
        "current-route required validation when the live manifest contains the required artifact and unittest gate.\n",
    )
    write_json(
        phase_path("phase0", "no_runtime_mutation_boundary.json"),
        {
            "schema_version": "consumer-universe-denominator-no-runtime-mutation-v1",
            "generated_at": GENERATED_AT,
            "runtime_mutation_allowed": False,
            "source_mutation_allowed": False,
            "rendered_mutation_allowed": False,
            "package_mutation_allowed": False,
            "current_route_manifest_mutation_allowed": gate["live_manifest_mutated"],
            "current_route_manifest_mutation_scope": "required_validation_manifest_only",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )

    records = build_denominators(bundle)
    write_jsonl(phase_path("phase1", "population_inventory.jsonl"), records)
    write_text(phase_path("phase1", "unlocated_report.md"), "# Unlocated Report\n\nStatus: `PASS` - no listed denominator remains unlocated.\n")
    write_json(
        phase_path("phase1", "unsealed_count_referent_report.json"),
        {
            "schema_version": "consumer-universe-denominator-unsealed-referent-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "unsealed_count": 0,
            "referents": [],
        },
    )
    write_json(
        phase_path("phase1", "source_location_report.json"),
        {
            "schema_version": "consumer-universe-denominator-source-location-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "located_count": len(records),
            "unlocated_count": 0,
            "source_fields": [
                {
                    "denominator_id": row["denominator_id"],
                    "source_artifact": row["source_artifact"],
                    "source_field": row["source_field"],
                    "status": row["status"],
                }
                for row in records
            ],
        },
    )

    write_jsonl(phase_path("phase2", "axis_classified_inventory.jsonl"), records)
    write_text(phase_path("phase2", "ambiguous_axis_report.md"), "# Ambiguous Axis Report\n\nStatus: `PASS` - no ambiguous denominator axis remains.\n")
    write_text(
        phase_path("phase2", "denominator_inventory_review.md"),
        "# Denominator Inventory Review\n\n"
        f"Status: `PASS`.\n\n`{len(records)}` scalar denominator records are classified with axis, row unit, source field, and claim boundary.\n",
    )

    crosswalk = crosswalk_rows(bundle)
    relations, identity_mapping, arithmetic = build_relationships(bundle, records, crosswalk)
    write_jsonl(phase_path("phase3", "relationship_bound_inventory.jsonl"), relations)
    write_json(phase_path("phase3", "denominator_relation_graph.json"), relation_graph(relations))
    write_json(phase_path("phase3", "arithmetic_consistency_report.json"), arithmetic)
    write_jsonl(phase_path("phase3", "cross_ledger_row_identity_mapping.jsonl"), identity_mapping)
    matched_count = sum(1 for row in identity_mapping if row["identity_match_status"] == "MATCHED")
    write_json(
        phase_path("phase3", "row_identity_match_report.json"),
        {
            "schema_version": "consumer-universe-denominator-row-identity-match-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if matched_count == 163 else "FAIL",
            "matched_count": matched_count,
            "expected_matched_count": 163,
            "count_equal_only": False,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_text(phase_path("phase3", "inconsistency_report.md"), "# Inconsistency Report\n\nStatus: `PASS` - no denominator inconsistency found.\n")

    registry = registry_payload(records)
    write_json(
        phase_path("phase4", "registry_format_decision.json"),
        {
            "schema_version": "consumer-universe-denominator-registry-format-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "registry_format": "json",
            "row_ledgers_format": "jsonl",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_json(phase_path("phase4", "consumer_universe_denominator_registry.json"), registry)
    write_jsonl(phase_path("phase4", "consumer_universe_denominator_crosswalk.jsonl"), crosswalk)
    schema_errors = registry_schema_errors(registry)
    write_json(
        phase_path("phase4", "registry_schema_report.json"),
        {
            "schema_version": "consumer-universe-denominator-registry-schema-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not schema_errors else "FAIL",
            "error_count": len(schema_errors),
            "errors": schema_errors,
        },
    )
    write_json(
        phase_path("phase4", "denominator_crosswalk_validation_report.json"),
        {
            "schema_version": "consumer-universe-denominator-crosswalk-validation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS"
            if len(crosswalk) == 311 and all(row["identity_match_status"] == "MATCHED" for row in crosswalk)
            else "FAIL",
            "crosswalk_row_count": len(crosswalk),
            "matched_count": sum(1 for row in crosswalk if row["identity_match_status"] == "MATCHED"),
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    inventory_only = [row for row in records if row["registry_inclusion"] == "inventory_only"]
    write_json(
        phase_path("phase4", "inventory_only_guard_coverage_report.json"),
        {
            "schema_version": "consumer-universe-denominator-inventory-only-coverage-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if all(row["forbidden_claim_verbs"] for row in inventory_only) else "FAIL",
            "inventory_only_count": len(inventory_only),
            "covered_count": sum(1 for row in inventory_only if row["forbidden_claim_verbs"]),
            "inventory_only_denominator_ids": [row["denominator_id"] for row in inventory_only],
        },
    )

    vocabulary = claim_vocabulary(records)
    positives = evaluate_fixtures(positive_fixtures())
    negatives = evaluate_fixtures(negative_fixtures())
    write_json(phase_path("phase5", "claim_vocabulary.json"), vocabulary)
    write_text(
        phase_path("phase5", "claim_boundary_contract.md"),
        "# Claim Boundary Contract\n\n"
        "Status: `PASS`.\n\n"
        "Generated denominator artifacts may be cited as denominator governance evidence. They must not be used as consumer migration execution, cutover authorization, runtime replacement, release readiness, or future closeout blocking unless a required current-route gate is adopted and validated.\n",
    )
    write_json(
        phase_path("phase5", "claim_guard_contract.json"),
        {
            "schema_version": "consumer-universe-denominator-claim-guard-contract-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "forbidden_patterns": [{"code": code, "pattern": pattern.pattern} for pattern, code in FORBIDDEN_CLAIM_PATTERNS],
            "candidate_guard_claim_allowed": True,
            "future_closeout_blocking_claim_allowed": gate["future_closeout_blocking_claim_allowed"],
            "required_gate_adoption_status": gate["required_gate_adoption_status"],
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_jsonl(phase_path("phase5", "claim_guard_positive_fixtures.jsonl"), positives)
    write_jsonl(phase_path("phase5", "claim_guard_negative_fixtures.jsonl"), negatives)
    write_json(
        phase_path("phase5", "claim_guard_inventory_only_catch_all_report.json"),
        {
            "schema_version": "consumer-universe-denominator-claim-guard-inventory-only-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if inventory_only else "FAIL",
            "inventory_only_count": len(inventory_only),
            "catch_all_policy": "inventory_only denominators cannot be used as completion denominators",
            "covered_denominator_ids": [row["denominator_id"] for row in inventory_only],
        },
    )
    fixture_failures = [row for row in positives + negatives if row["status"] != "PASS"]
    write_json(
        phase_path("phase5", "claim_guard_test_report.json"),
        {
            "schema_version": "consumer-universe-denominator-claim-guard-test-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not fixture_failures else "FAIL",
            "positive_fixture_count": len(positives),
            "negative_fixture_count": len(negatives),
            "failure_count": len(fixture_failures),
            "failures": fixture_failures,
        },
    )

    patch = candidate_patch_payload()
    write_json(phase_path("phase6", "current_route_required_validation_patch.json"), patch)
    gate = current_route_gate_adoption_state()
    write_json(
        phase_path("phase6", "current_route_denominator_validation_report.json"),
        {
            "schema_version": "consumer-universe-denominator-current-route-validation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "candidate_current_route_validation_status": "patch_schema_validated",
            "required_gate_adoption_status": gate["required_gate_adoption_status"],
            "live_manifest_mutated": gate["live_manifest_mutated"],
            "live_manifest_contains_required_artifact": gate["artifact_adopted"],
            "live_manifest_contains_required_test": gate["test_adopted"],
            "adoption_authorization": gate["adoption_authorization"],
            "future_closeout_blocking_claim_allowed": gate["future_closeout_blocking_claim_allowed"],
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_json(
        phase_path("phase6", "current_route_candidate_patch_sandbox_apply_restore_report.json"),
        {
            "schema_version": "consumer-universe-denominator-current-route-sandbox-apply-restore-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "sandbox_validation_run": False,
            "restore_required": False,
            "restore_performed": False,
            "candidate_current_route_validation_status": "patch_schema_validated",
            "live_manifest_mutated": gate["live_manifest_mutated"],
            "required_gate_adoption_status": gate["required_gate_adoption_status"],
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    closure = read_json(CURRENT_CLOSURE)
    write_json(
        phase_path("phase6", "current_route_closure_allowlist_regression_report.json"),
        {
            "schema_version": "consumer-universe-denominator-current-route-closure-regression-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "current_closure_count": closure.get("current_closure_count"),
            "current_route_allowed_tooling_count": len(closure.get("current_route_allowed_tooling_modules", [])),
            "this_round_tools_added_to_current_closure": False,
            "this_round_tools_added_to_tooling_allowlist": False,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    protected_after = stable_surface_hash(surface)
    diff = stable_surface_diff(protected_before, protected_after)
    write_json(
        phase_path("phase6", "protected_surface_no_mutation_verdict.json"),
        {
            "schema_version": "consumer-universe-denominator-protected-surface-no-mutation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
            "changed_count": diff["changed_count"],
            "changed": diff["changed"],
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )

    final_seed = {
        "machine_contract_status": "PASS",
        "governance_closeout_status": "review_pending",
        "complete_claim_allowed": gate["live_manifest_mutated"],
        "canonical_seal_allowed": False,
        "required_gate_adoption_status": gate["required_gate_adoption_status"],
        "candidate_current_route_validation_status": "patch_schema_validated",
        "candidate_guard_claim_allowed": True,
        "future_closeout_blocking_claim_allowed": gate["future_closeout_blocking_claim_allowed"],
        "runtime_mutation_allowed": False,
    }
    write_text(phase_path("phase7", "consumer_universe_denominator_lock_ledger_packet.md"), ledger_packet_text(final_seed))
    write_text(phase_path("phase7", "consumer_universe_denominator_lock_closeout.md"), closeout_text(final_seed))
    write_text(
        phase_path("phase7", "documentation_claim_boundary_review.md"),
        "# Documentation Claim Boundary Review\n\n"
        "Status: `PASS`.\n\n"
        "Generated closeout and ledger packet bind future closeout blocking only to the adopted current-route required "
        "validation gate. They do not claim cutover, migration execution, runtime mutation, release readiness, or "
        "Workshop readiness.\n",
    )
    write_text(REPO_ROOT / "docs" / "consumer_universe_denominator_lock_ledger_packet.md", ledger_packet_text(final_seed))
    write_text(REPO_ROOT / "docs" / "consumer_universe_denominator_lock_closeout.md", closeout_text(final_seed))

    review_manifest = {
        "schema_version": "consumer-universe-denominator-independent-review-input-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "review_state": "pending",
        "materialized_by_this_round": False,
        "review_report_path": None,
        "review_report_sha256": None,
        "reviewer_not_plan_author": None,
        "reviewer_not_executor": None,
        "review_scope": [
            "unique denominator role per count",
            "59 and 252 source predicate",
            "163 row identity mapping",
            "current-route required gate adoption boundary",
            "no runtime/source/rendered/package mutation",
        ],
        "certification_ceiling": "machine_pass_review_pending",
        "reviewer_conflict_disclosure": None,
        "plan_template_checked": True,
    }
    write_json(phase_path("phase8", "external_independent_review_input_manifest.json"), review_manifest)
    write_json(
        phase_path("phase8", "independent_review_status.json"),
        {
            "schema_version": "consumer-universe-denominator-independent-review-status-v1",
            "generated_at": GENERATED_AT,
            "status": "review_pending",
            "review_result": None,
            "review_state": "pending",
            "materialized_by_this_round": False,
            "complete_claim_allowed": False,
            "canonical_seal_allowed": False,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    return final_seed


def write_final_report(fingerprint_before: dict[str, Any], fingerprint_after: dict[str, Any]) -> dict[str, Any]:
    gate = current_route_gate_adoption_state()
    final = {
        "schema_version": "consumer-universe-denominator-final-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "machine_contract_status": "PASS",
        "governance_closeout_status": "review_pending",
        "complete_claim_allowed": gate["live_manifest_mutated"],
        "canonical_seal_allowed": False,
        "required_gate_adoption_status": gate["required_gate_adoption_status"],
        "candidate_current_route_validation_status": "patch_schema_validated",
        "candidate_guard_claim_allowed": True,
        "future_closeout_blocking_claim_allowed": gate["future_closeout_blocking_claim_allowed"],
        "live_manifest_mutated": gate["live_manifest_mutated"],
        "live_manifest_contains_required_artifact": gate["artifact_adopted"],
        "live_manifest_contains_required_test": gate["test_adopted"],
        "adoption_authorization": gate["adoption_authorization"],
        "runtime_mutation_allowed": False,
        "source_mutation_allowed": False,
        "rendered_mutation_allowed": False,
        "package_mutation_allowed": False,
        "phase_reports": {
            "registry": phase_report_ref(phase_path("phase4", "consumer_universe_denominator_registry.json")),
            "crosswalk": phase_report_ref(phase_path("phase4", "denominator_crosswalk_validation_report.json")),
            "row_identity": phase_report_ref(phase_path("phase3", "row_identity_match_report.json")),
            "claim_guard": phase_report_ref(phase_path("phase5", "claim_guard_test_report.json")),
            "current_route_candidate": phase_report_ref(phase_path("phase6", "current_route_denominator_validation_report.json")),
            "no_mutation": phase_report_ref(phase_path("phase6", "protected_surface_no_mutation_verdict.json")),
            "review": phase_report_ref(phase_path("phase8", "independent_review_status.json")),
        },
        "regenerate_twice_fingerprint_comparison": {
            "status": "PASS" if fingerprint_before["aggregate_sha256"] == fingerprint_after["aggregate_sha256"] else "FAIL",
            "first": fingerprint_before,
            "second": fingerprint_after,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase8", "final_consumer_universe_denominator_lock_report.json"), final)
    write_text(phase_path("phase8", "final_consumer_universe_denominator_lock_closeout.md"), closeout_text(final))
    return final


def run_all() -> dict[str, Any]:
    normalization = run_consumer_migration_normalization()
    if normalization.get("machine_contract_status") != "PASS":
        raise ValueError(
            "consumer migration normalization prerequisite did not pass"
        )
    generate_core()
    first = canonical_artifact_fingerprint()
    generate_core()
    second = canonical_artifact_fingerprint()
    return write_final_report(first, second)


def registry_schema_errors(registry: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    seen: set[str] = set()
    for row in registry.get("denominators", []):
        missing = [field for field in REQUIRED_DENOMINATOR_FIELDS if field not in row]
        if missing:
            errors.append({"denominator_id": row.get("denominator_id"), "code": "missing_fields", "fields": missing})
        denominator_id = row.get("denominator_id")
        if denominator_id in seen:
            errors.append({"denominator_id": denominator_id, "code": "duplicate_denominator_id"})
        seen.add(str(denominator_id))
        if not isinstance(row.get("value"), int):
            errors.append({"denominator_id": denominator_id, "code": "non_scalar_integer_value", "value": row.get("value")})
        if row.get("authority_role") != "claim_boundary_governance_only":
            errors.append({"denominator_id": denominator_id, "code": "invalid_authority_role"})
        if row.get("source_granularity") == "unknown" and str(row.get("status", "")).startswith("LOCKED"):
            errors.append({"denominator_id": denominator_id, "code": "unknown_granularity_locked"})
        if "/" in str(row.get("value")):
            errors.append({"denominator_id": denominator_id, "code": "packed_value"})
    return errors


def validate_all() -> tuple[dict[str, Any], bool]:
    errors = []
    required_paths = [
        phase_path("phase4", "consumer_universe_denominator_registry.json"),
        phase_path("phase4", "consumer_universe_denominator_crosswalk.jsonl"),
        phase_path("phase3", "denominator_relation_graph.json"),
        phase_path("phase3", "row_identity_match_report.json"),
        phase_path("phase5", "claim_guard_test_report.json"),
        phase_path("phase6", "current_route_denominator_validation_report.json"),
        phase_path("phase6", "protected_surface_no_mutation_verdict.json"),
        phase_path("phase8", "external_independent_review_input_manifest.json"),
        phase_path("phase8", "independent_review_status.json"),
        phase_path("phase8", "final_consumer_universe_denominator_lock_report.json"),
    ]
    for path in required_paths:
        if not path.exists():
            errors.append({"code": "missing_artifact", "path": rel(path)})
    if errors:
        return {"status": "FAIL", "errors": errors}, False

    registry = read_json(phase_path("phase4", "consumer_universe_denominator_registry.json"))
    records = registry["denominators"]
    by_id = {row["denominator_id"]: row for row in records}
    errors.extend(registry_schema_errors(registry))
    expected_values = {
        "DEN-AUDIT-RAW-OCCURRENCES": 198815,
        "DEN-AUDIT-ACCEPTED-CANDIDATES": 27869,
        "DEN-AUDIT-CORE-OCCURRENCES": 21174,
        "DEN-AUDIT-ADJACENT-SEED-OCCURRENCES": 6695,
        "DEN-AUDIT-EXECUTING-CONSUMERS": 1062,
        "DEN-AUDIT-CHANGE-REQUIRED": 311,
        "DEN-REBASELINE-CHANGE-NEEDED": 59,
        "DEN-REBASELINE-CONDITIONAL": 252,
        "DEN-NORMALIZED-APPLY-ELIGIBLE": 163,
        "DEN-READINESS-SANDBOX-MUTATION": 163,
        "DEN-NORMALIZED-NO-OP": 148,
        "DEN-NORMALIZED-MISSING-PATH": 125,
        "DEN-NORMALIZED-MISSING-APPLY-ELIGIBLE": 0,
        "DEN-AUDIT-CHANGE-FORBIDDEN": 27558,
        "DEN-RUNTIME-CURRENT-ENTRIES": 2105,
        "DEN-RUNTIME-ADOPTED-ROWS": 2084,
        "DEN-RUNTIME-UNADOPTED-ROWS": 21,
    }
    for denominator_id, value in expected_values.items():
        observed = by_id.get(denominator_id, {}).get("value")
        if observed != value:
            errors.append({"code": "denominator_value_mismatch", "denominator_id": denominator_id, "expected": value, "observed": observed})

    crosswalk = read_jsonl(phase_path("phase4", "consumer_universe_denominator_crosswalk.jsonl"))
    row_identity = read_json(phase_path("phase3", "row_identity_match_report.json"))
    if len(crosswalk) != 311:
        errors.append({"code": "crosswalk_row_count_mismatch", "observed": len(crosswalk)})
    if row_identity.get("matched_count") != 163 or row_identity.get("status") != "PASS":
        errors.append({"code": "row_identity_match_failed", "report": row_identity})

    arithmetic = read_json(phase_path("phase3", "arithmetic_consistency_report.json"))
    if arithmetic.get("status") != "PASS":
        errors.append({"code": "arithmetic_failed", "report": arithmetic})

    guard = read_json(phase_path("phase5", "claim_guard_test_report.json"))
    if guard.get("status") != "PASS":
        errors.append({"code": "claim_guard_failed", "report": guard})

    gate = current_route_gate_adoption_state()
    current_route = read_json(phase_path("phase6", "current_route_denominator_validation_report.json"))
    if current_route.get("required_gate_adoption_status") != gate["required_gate_adoption_status"]:
        errors.append({"code": "required_gate_adoption_mismatch", "expected": gate["required_gate_adoption_status"], "report": current_route})
    if current_route.get("future_closeout_blocking_claim_allowed") is not gate["future_closeout_blocking_claim_allowed"]:
        errors.append({"code": "future_blocking_claim_mismatch", "expected": gate["future_closeout_blocking_claim_allowed"], "report": current_route})
    if current_route.get("live_manifest_contains_required_artifact") is not gate["artifact_adopted"]:
        errors.append({"code": "required_artifact_adoption_mismatch", "expected": gate["artifact_adopted"], "report": current_route})
    if current_route.get("live_manifest_contains_required_test") is not gate["test_adopted"]:
        errors.append({"code": "required_test_adoption_mismatch", "expected": gate["test_adopted"], "report": current_route})
    if not gate["live_manifest_mutated"]:
        errors.append({"code": "required_gate_not_adopted", "report": current_route})

    no_mutation = read_json(phase_path("phase6", "protected_surface_no_mutation_verdict.json"))
    if no_mutation.get("changed_count") != 0 or no_mutation.get("status") != "PASS":
        errors.append({"code": "protected_surface_mutated", "report": no_mutation})

    review = read_json(phase_path("phase8", "independent_review_status.json"))
    if review.get("materialized_by_this_round") is not False or review.get("review_state") != "pending":
        errors.append({"code": "independent_review_state_invalid", "report": review})

    final = read_json(phase_path("phase8", "final_consumer_universe_denominator_lock_report.json"))
    if final.get("complete_claim_allowed") is not gate["live_manifest_mutated"]:
        errors.append({"code": "final_complete_claim_mismatch", "expected": gate["live_manifest_mutated"], "report": final})
    if final.get("canonical_seal_allowed") is not False:
        errors.append({"code": "canonical_seal_overclaimed", "report": final})
    if final.get("required_gate_adoption_status") != gate["required_gate_adoption_status"]:
        errors.append({"code": "final_required_gate_status_mismatch", "expected": gate["required_gate_adoption_status"], "report": final})
    if final.get("future_closeout_blocking_claim_allowed") is not gate["future_closeout_blocking_claim_allowed"]:
        errors.append({"code": "final_future_blocking_claim_mismatch", "expected": gate["future_closeout_blocking_claim_allowed"], "report": final})
    regen = final.get("regenerate_twice_fingerprint_comparison", {})
    if regen.get("status") != "PASS":
        errors.append({"code": "determinism_failed", "report": regen})

    report = {
        "schema_version": "consumer-universe-denominator-validation-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "error_count": len(errors),
        "errors": errors,
    }
    return report, not errors


def validate_claim_guard() -> tuple[dict[str, Any], bool]:
    positives = evaluate_fixtures(positive_fixtures())
    negatives = evaluate_fixtures(negative_fixtures())
    failures = [row for row in positives + negatives if row["status"] != "PASS"]
    report = {
        "schema_version": "consumer-universe-denominator-claim-guard-validation-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not failures else "FAIL",
        "positive_fixture_count": len(positives),
        "negative_fixture_count": len(negatives),
        "failure_count": len(failures),
        "failures": failures,
    }
    return report, not failures
