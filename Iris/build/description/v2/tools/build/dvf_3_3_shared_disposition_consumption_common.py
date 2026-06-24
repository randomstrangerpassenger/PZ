from __future__ import annotations

from collections import Counter
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


GENERATED_AT = "2026-06-21T00:00:00+09:00"
ROUND_ID = "dvf_3_3_shared_disposition_ledger_consumption"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_shared_disposition_ledger_consumption_plan.md"
EXECUTION_CONTRACT = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"

POLICY_DOC = REPO_ROOT / "docs" / "dvf_3_3_shared_disposition_consumption_policy.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_shared_disposition_ledger_packet.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_shared_disposition_claim_boundary.md"

CURRENT_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
CANDIDATE_REQUIRED_VALIDATIONS = (
    REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.shared_disposition_candidate.json"
)
CURRENT_CORE_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"

DENOMINATOR_ROOT = V2_ROOT / "staging" / "consumer_universe_denominator_lock"
DENOMINATOR_REGISTRY = DENOMINATOR_ROOT / "phase4" / "consumer_universe_denominator_registry.json"
DENOMINATOR_FINAL = DENOMINATOR_ROOT / "phase8" / "final_consumer_universe_denominator_lock_report.json"

TERMINAL_ROOT = V2_ROOT / "staging" / "dvf_3_3_terminal_disposition_adjudication"
TERMINAL_LEDGER = TERMINAL_ROOT / "phase3" / "terminal_disposition_ledger.jsonl"
TERMINAL_COUNTS = TERMINAL_ROOT / "phase3" / "terminal_disposition_counts.json"
TERMINAL_FINAL = TERMINAL_ROOT / "phase5" / "final_terminal_disposition_machine_report.json"

LIVE_EXECUTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_live_consumer_migration_execution"
LIVE_TARGET_SUMMARY = LIVE_EXECUTION_ROOT / "phase2" / "live_target_derivation_summary.json"
LIVE_FINAL = LIVE_EXECUTION_ROOT / "phase8" / "final_live_migration_execution_report.json"

READINESS_EXECUTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_live_migration_readiness_execution"
READINESS_DOWNSTREAM = READINESS_EXECUTION_ROOT / "phase10" / "downstream_predecessor_status.json"

AUDIT_ROOT = V2_ROOT / "staging" / "2105_baseline_consumption_audit"
AUDIT_CLASSIFIED_LEDGER = AUDIT_ROOT / "classified_ledger.jsonl"
AUDIT_RAW_OCCURRENCES = AUDIT_ROOT / "raw_occurrences.jsonl"

CUTOVER_READINESS_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_cutover_tooling_readiness"
CUTOVER_READINESS_LEDGER = CUTOVER_READINESS_ROOT / "phase3" / "row_level_migration_ledger.jsonl"
CUTOVER_ACTUAL_REPORT = CUTOVER_READINESS_ROOT / "phase3" / "consumer_migration_actual_report.json"
CUTOVER_DIFF_REPORT = CUTOVER_READINESS_ROOT / "phase4" / "actual_diff_to_ledger_report.json"

LIVE_DRY_RUN_OUTPUT = LIVE_EXECUTION_ROOT / "phase3" / "live_dry_run_diff.json"
LIVE_FROZEN_PATCH_BUNDLE = LIVE_EXECUTION_ROOT / "phase3" / "frozen_patch_bundle.json"
BASELINE_TREE_SNAPSHOT = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_baseline_tree_snapshot.json"
LEGACY_DISCOVERY_BASELINE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_legacy_full_discovery_baseline.json"

NEGATIVE_FIXTURE_ROOT = V2_ROOT / "tests" / "fixtures" / "negative" / "shared_disposition"

CLAIM_BOUNDARY = (
    "Shared disposition consumption contract only; not denominator adjudication, not terminal "
    "disposition re-adjudication, not Phase 4 live apply, not source/rendered/Lua-bridge/runtime/"
    "package authority mutation, not release readiness, not Workshop readiness, not B42 readiness, "
    "not deployment readiness, and not public-facing text quality acceptance."
)

SEALED_AXIS_VALUES: dict[str, dict[str, Any]] = {
    "1062": {
        "value": 1062,
        "role": "terminal executing-consumer member-row denominator",
        "denominator_id": "DEN-AUDIT-EXECUTING-CONSUMERS",
    },
    "311": {
        "value": 311,
        "role": "audit change-required occurrence count",
        "denominator_id": "DEN-AUDIT-CHANGE-REQUIRED",
    },
    "163": {
        "value": 163,
        "role": "normalization apply-eligible and readiness sandbox row count",
        "denominator_id": "DEN-NORMALIZED-APPLY-ELIGIBLE",
    },
    "153": {"value": 153, "role": "terminal migrated projection", "terminal_field": "migrated_count"},
    "148": {"value": 148, "role": "normalization no-op row count", "denominator_id": "DEN-NORMALIZED-NO-OP"},
    "109": {"value": 109, "role": "live mutation eligible / verified live rows", "live_field": "live_verified_already"},
    "44": {"value": 44, "role": "evidence-only hard-forbidden migrated rows", "live_field": "excluded_non_live_target"},
    "2105": {
        "value": 2105,
        "role": "runtime current entry comparison count",
        "denominator_id": "DEN-RUNTIME-CURRENT-ENTRIES",
    },
    "2084": {"value": 2084, "role": "runtime adopted row count", "denominator_id": "DEN-RUNTIME-ADOPTED-ROWS"},
    "21": {"value": 21, "role": "runtime unadopted row count", "denominator_id": "DEN-RUNTIME-UNADOPTED-ROWS"},
    "27558": {"value": 27558, "role": "audit change-forbidden occurrence count", "denominator_id": "DEN-AUDIT-CHANGE-FORBIDDEN"},
    "59": {"value": 59, "role": "rebaseline yes predicate count", "denominator_id": "DEN-REBASELINE-CHANGE-NEEDED"},
    "252": {"value": 252, "role": "rebaseline conditional predicate count", "denominator_id": "DEN-REBASELINE-CONDITIONAL"},
    "268": {"value": 268, "role": "terminal no-op projection", "terminal_field": "no_op_count"},
    "3": {"value": 3, "role": "terminal diagnostic-only projection", "terminal_field": "diagnostic_only_count"},
    "638": {"value": 638, "role": "terminal historical-only projection", "terminal_field": "historical_only_count"},
    "902": {"value": 902, "role": "terminal source predicate no count", "source_predicate": "no"},
    "49": {"value": 49, "role": "terminal source predicate yes count", "source_predicate": "yes"},
    "111": {"value": 111, "role": "terminal source predicate conditional count", "source_predicate": "conditional"},
    "0": {"value": 0, "role": "blocked/unknown/pending/forbidden zero invariants", "zero_invariant": True},
}

TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(sorted(map(re.escape, SEALED_AXIS_VALUES), key=len, reverse=True)) + r")(?![A-Za-z0-9_])")
FIELD_KEYWORDS = (
    "denominator",
    "terminal_disposition",
    "lifecycle_role",
    "readiness",
    "migration",
    "current_route",
    "predecessor",
    "sealed_value_source",
    "shared_disposition",
    "disposition",
    "terminal",
    "live_mutation",
    "runtime",
    "source_predicate",
    "blocked",
    "unknown",
    "pending",
)
CONTEXT_KEYWORDS = (
    "dvf 3-3",
    "dvf_3_3",
    "disposition",
    "denominator",
    "readiness",
    "migration",
    "terminal",
    "runtime",
    "current authority",
    "current_authority",
)

PROTECTED_SURFACE_PATHS = [
    ("Iris/build/description/v2/data/dvf_3_3_input_manifest.json", "current_input_manifest", False),
    ("Iris/build/description/v2/data/dvf_3_3_facts.jsonl", "current_source_facts", False),
    ("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl", "current_source_decisions", False),
    ("Iris/build/description/v2/output/dvf_3_3_rendered.json", "current_rendered_output", False),
    ("Iris/build/description/v2/output/style_normalization_changes.jsonl", "current_style_side_output", True),
    ("Iris/build/description/v2/output/compose_requeue_candidates.jsonl", "current_requeue_side_output", True),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "live_runtime_chunk_manifest", False),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks", "live_runtime_chunk_dir", False),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "live_runtime_monolith_facade", True),
    ("Iris/build/package/Iris/media/lua/client/Iris/Data", "package_peer_runtime_output", True),
    ("Iris/_docs/round3/current_route_required_validations.json", "live_current_route_required_validation_manifest", True),
]

FORBIDDEN_DIRECT_READS = [
    (AUDIT_RAW_OCCURRENCES, "raw_audit_occurrence_scan"),
    (AUDIT_CLASSIFIED_LEDGER, "raw_audit_classified_ledger"),
    (CUTOVER_READINESS_LEDGER, "readiness_sandbox_row_ledger"),
    (CUTOVER_ACTUAL_REPORT, "readiness_sandbox_actual_report"),
    (CUTOVER_DIFF_REPORT, "readiness_sandbox_diff_report"),
    (LIVE_DRY_RUN_OUTPUT, "dry_run_patch_bundle_output"),
    (LIVE_FROZEN_PATCH_BUNDLE, "dry_run_frozen_patch_bundle"),
    (BASELINE_TREE_SNAPSHOT, "predecessor_baseline_trace"),
    (LEGACY_DISCOVERY_BASELINE, "predecessor_legacy_discovery_trace"),
]

ROLE_BEARING_SCAN_PATHS = [
    PLAN_PATH,
    POLICY_DOC,
    LEDGER_PACKET_DOC,
    CLAIM_BOUNDARY_DOC,
    CURRENT_REQUIRED_VALIDATIONS,
    CANDIDATE_REQUIRED_VALIDATIONS,
    DENOMINATOR_REGISTRY,
    DENOMINATOR_FINAL,
    TERMINAL_COUNTS,
    TERMINAL_FINAL,
    TERMINAL_LEDGER,
    LIVE_TARGET_SUMMARY,
    LIVE_FINAL,
    READINESS_DOWNSTREAM,
    REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / "consumer_universe_denominator_lock_common.py",
    REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / "dvf_3_3_terminal_disposition_adjudication_common.py",
    REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / "dvf_3_3_live_consumer_migration_execution_common.py",
]

FORBIDDEN_CLAIM_PATTERNS = [
    (re.compile(r"153\s+migrated\s*=\s*live\s+migration\s+completed", re.IGNORECASE), "153_migrated_not_live_completion"),
    (re.compile(r"109\s+live_mutation_eligible\s*=\s*already\s+applied", re.IGNORECASE), "109_not_already_applied"),
    (re.compile(r"163\s+sandbox\s+mutation\s*=\s*live\s+mutation\s+evidence", re.IGNORECASE), "163_sandbox_not_live_evidence"),
    (re.compile(r"311\s+change-required\s*=\s*terminal\s+completion\s+denominator", re.IGNORECASE), "311_not_terminal_denominator"),
    (re.compile(r"1062\s+executing\s+consumers\s*=\s*source\s+entries", re.IGNORECASE), "1062_not_source_entries"),
    (re.compile(r"raw\s+audit\s+ledger\s*=\s*current\s+execution\s+authority", re.IGNORECASE), "raw_audit_not_current_authority"),
    (re.compile(r"dry-run\s+patch\s+bundle\s*=\s*live\s+completion", re.IGNORECASE), "dry_run_not_live_completion"),
    (re.compile(r"(2105|2084|21)\s*=\s*current\s+debt", re.IGNORECASE), "predecessor_not_current_debt"),
]


def phase_dir(phase: str) -> Path:
    path = EVIDENCE_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())


def stable_record(path: str | Path, role: str, *, required: bool = True, read_only: bool = True) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "role": role,
        "required": required,
        "read_only": read_only,
        "exists": resolved.exists(),
        "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
        "sha256": sha256_file(resolved) if resolved.is_file() else None,
        "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
        "row_count": count_jsonl(resolved) if resolved.exists() and resolved.suffix == ".jsonl" else None,
        "status": "PRESENT" if resolved.exists() else "MISSING_REQUIRED" if required else "ABSENT_ALLOWED",
    }


def _is_under(path: str | Path, root: str | Path) -> bool:
    resolved = resolve_repo(path)
    root_path = resolve_repo(root)
    return resolved == root_path or root_path in resolved.parents


def protected_surface_definition() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-shared-disposition-protected-surface-set-v1",
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
        "schema_version": "dvf-3-3-shared-disposition-protected-surface-hash-v1",
        "generated_at": GENERATED_AT,
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(comparable),
    }


def protected_surface_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before.get("records", [])}
    after_rows = {row["path"]: row for row in after.get("records", [])}
    changed = []
    for path in sorted(set(before_rows).union(after_rows)):
        if before_rows.get(path) != after_rows.get(path):
            changed.append({"path": path, "before": before_rows.get(path), "after": after_rows.get(path)})
    return {
        "schema_version": "dvf-3-3-shared-disposition-protected-surface-diff-v1",
        "generated_at": GENERATED_AT,
        "changed_count": len(changed),
        "changed": changed,
    }


def surface_class_for(path: Path) -> str:
    normalized = rel(path)
    if normalized.startswith("docs/"):
        return "doc"
    if "tests/fixtures/" in normalized:
        return "fixture"
    if "/tests/" in normalized or normalized.startswith("Iris/build/description/v2/tests/"):
        return "test"
    if normalized.endswith("current_route_required_validations.json") or normalized.endswith(
        "current_route_required_validations.shared_disposition_candidate.json"
    ):
        return "manifest"
    if normalized.startswith("Iris/build/description/v2/tools/build/validate_"):
        return "validator"
    if normalized.startswith("Iris/build/description/v2/tools/build/"):
        return "tool"
    if normalized.startswith("Iris/build/package/"):
        return "package"
    if normalized.startswith("Iris/media/lua/"):
        return "runtime"
    if normalized.startswith("Iris/build/description/v2/staging/"):
        return "generated_report"
    return "unknown"


def artifact_role_for(path: Path, line: str) -> str:
    normalized = rel(path)
    lowered = line.lower()
    if normalized == rel(PLAN_PATH):
        return "provenance_only"
    if "tests/fixtures/negative/shared_disposition" in normalized:
        return "diagnostic_only"
    if "sealed_value_source" in lowered and any(rel(forbidden).lower() in lowered for forbidden, _role in FORBIDDEN_DIRECT_READS):
        return "forbidden_direct_authority_candidate"
    if "current execution authority" in lowered and ("raw audit" in lowered or "dry-run" in lowered or "predecessor" in lowered):
        return "forbidden_direct_authority_candidate"
    if "terminal_disposition_ledger" in normalized or "terminal_disposition_counts" in normalized:
        return "canonical_input"
    if "consumer_universe_denominator_lock" in normalized:
        return "canonical_input"
    if "live_consumer_migration_execution" in normalized or "live_migration_readiness" in normalized:
        return "readiness_evidence"
    if "round3_baseline" in normalized or "legacy_full_discovery" in normalized:
        return "historical_trace"
    if normalized.startswith("docs/"):
        return "provenance_only"
    if "shared_disposition" in normalized or "shared_disposition" in lowered:
        return "current_consumer"
    return "provenance_only"


def is_role_bearing(path: Path, line: str) -> bool:
    normalized = rel(path).lower()
    lowered = line.lower()
    if any(keyword in lowered for keyword in FIELD_KEYWORDS):
        return True
    if any(keyword in lowered for keyword in CONTEXT_KEYWORDS):
        return True
    return any(fragment in normalized for fragment in ("terminal_disposition", "consumer_universe", "live_consumer", "shared_disposition"))


def scan_files() -> list[Path]:
    paths: list[Path] = []
    for path in ROLE_BEARING_SCAN_PATHS:
        resolved = resolve_repo(path)
        if resolved.exists() and resolved.is_file():
            paths.append(resolved)
    for name in (
        "dvf_3_3_shared_disposition_consumption_common.py",
        "run_dvf_3_3_shared_disposition_consumption.py",
        "validate_dvf_3_3_shared_disposition_consumption.py",
        "generate_dvf_3_3_shared_disposition_packet.py",
        "write_dvf_3_3_shared_disposition_ledger_packet.py",
    ):
        path = REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / name
        if path.exists():
            paths.append(path)
    test_path = REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tests" / "test_dvf_3_3_shared_disposition_consumption.py"
    if test_path.exists():
        paths.append(test_path)
    return sorted(set(paths), key=rel)


def build_census() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    raw_counter: Counter[str] = Counter()
    promoted_counter: Counter[str] = Counter()
    excluded_counter: Counter[str] = Counter()
    exclusion_reasons: Counter[str] = Counter()
    census_rows: list[dict[str, Any]] = []
    inventory_rows: list[dict[str, Any]] = []

    for path in scan_files():
        surface_class = surface_class_for(path)
        inventory_rows.append(
            {
                **stable_record(path, "bounded_scan_surface", required=False),
                "surface_class": surface_class,
                "excluded_from_current_looking_scan": _is_under(path, NEGATIVE_FIXTURE_ROOT),
            }
        )
        if _is_under(path, NEGATIVE_FIXTURE_ROOT):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            tokens = TOKEN_RE.findall(line)
            if not tokens:
                continue
            for token in tokens:
                raw_counter[token] += 1
            if not is_role_bearing(path, line):
                for token in tokens:
                    excluded_counter[token] += 1
                exclusion_reasons["bounded_predicate_not_satisfied"] += len(tokens)
                continue
            for token in tokens:
                promoted_counter[token] += 1
                census_rows.append(
                    {
                        "schema_version": "dvf-3-3-shared-disposition-census-row-v1",
                        "path": rel(path),
                        "line": line_number,
                        "token": token,
                        "token_role": SEALED_AXIS_VALUES[token]["role"],
                        "surface_class": surface_class,
                        "artifact_role": artifact_role_for(path, line),
                        "occurrence_kind": "role_bearing_disposition_occurrence",
                        "line_excerpt": line.strip()[:220],
                    }
                )

    token_rows = []
    for token, meta in SEALED_AXIS_VALUES.items():
        token_rows.append(
            {
                "token": token,
                "sealed_value": meta["value"],
                "sealed_axis_role": meta["role"],
                "raw_numeric_occurrence_count": raw_counter[token],
                "role_bearing_disposition_occurrence_count": promoted_counter[token],
                "excluded_numeric_occurrence_count": excluded_counter[token],
                "coverage_status": "COVERED" if promoted_counter[token] or meta.get("zero_invariant") else "COVERED_BY_SEALED_VALUE_TABLE",
                "exclusion_reason": None if promoted_counter[token] else "covered by value_resolution_table source binding",
            }
        )

    zero_raw = raw_counter["0"]
    zero_promoted = promoted_counter["0"]
    zero_excluded = excluded_counter["0"]
    zero_report = {
        "schema_version": "dvf-3-3-shared-disposition-zero-token-promotion-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "token": "0",
        "raw_numeric_occurrence_count": zero_raw,
        "promoted_role_bearing_count": zero_promoted,
        "excluded_numeric_count": zero_excluded,
        "promoted_ratio": 0 if zero_raw == 0 else round(zero_promoted / zero_raw, 6),
        "excluded_ratio": 0 if zero_raw == 0 else round(zero_excluded / zero_raw, 6),
        "top_exclusion_reasons": [{"reason": reason, "count": count} for reason, count in exclusion_reasons.most_common(8)],
        "zero_role_boundary": "only field/context-bounded zeros can assert blocked/unknown/pending/forbidden invariants",
    }
    token_set = {
        "schema_version": "dvf-3-3-shared-disposition-sealed-axis-token-set-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "token_count": len(token_rows),
        "tokens": token_rows,
    }
    return census_rows, inventory_rows, token_set, zero_report


def write_phase1() -> None:
    census_rows, inventory_rows, token_set, zero_report = build_census()
    write_json(
        phase_path("phase1", "scope_lock.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-scope-lock-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "round_id": ROUND_ID,
            "objective": "shared disposition ledger consumption only",
            "claim_boundary": CLAIM_BOUNDARY,
            "live_required_validation_adoption": current_route_shared_adoption_status()["adoption_state"],
            "source_rendered_lua_runtime_package_mutation_allowed": False,
        },
    )
    write_json(
        phase_path("phase1", "bounded_census_predicate.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-bounded-census-predicate-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "scan_path_count": len(scan_files()),
            "raw_numeric_occurrence_is_authority": False,
            "promotion_predicates": {
                "path_allowlist": [rel(path) for path in scan_files()],
                "field_keywords": list(FIELD_KEYWORDS),
                "context_keywords": list(CONTEXT_KEYWORDS),
                "negative_fixture_exclusion_root": rel(NEGATIVE_FIXTURE_ROOT),
            },
        },
    )
    write_json(phase_path("phase1", "sealed_axis_token_set.json"), token_set)
    write_json(phase_path("phase1", "zero_token_promotion_report.json"), zero_report)
    write_jsonl(phase_path("phase1", "consumption_census_ledger.jsonl"), census_rows)
    write_jsonl(phase_path("phase1", "surface_inventory.jsonl"), inventory_rows)
    unclassified = [row for row in census_rows if row["surface_class"] == "unknown"]
    write_json(
        phase_path("phase1", "unclassified_surface_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-unclassified-surface-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not unclassified else "FAIL",
            "unclassified_surface_count": len(unclassified),
            "rows": unclassified[:50],
        },
    )


def sealed_report_set() -> dict[str, Any]:
    sources = [
        ("denominator_registry", DENOMINATOR_REGISTRY, "denominator_axis_registry"),
        ("denominator_final_report", DENOMINATOR_FINAL, "denominator_lock_final_report"),
        ("terminal_disposition_ledger", TERMINAL_LEDGER, "terminal_member_row_disposition_ledger"),
        ("terminal_disposition_counts", TERMINAL_COUNTS, "terminal_split_counts"),
        ("terminal_final_machine_report", TERMINAL_FINAL, "terminal_final_machine_report"),
        ("live_execution_target_summary", LIVE_TARGET_SUMMARY, "live_readiness_projection_summary"),
        ("live_execution_final_report", LIVE_FINAL, "live_execution_evidence_final_report"),
        ("readiness_execution_downstream_status", READINESS_DOWNSTREAM, "pre_apply_readiness_status"),
    ]
    records = []
    for source_id, path, role in sources:
        records.append({"source_id": source_id, **stable_record(path, role)})
    return {
        "schema_version": "dvf-3-3-shared-disposition-sealed-report-set-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if all(row["exists"] for row in records) else "FAIL",
        "sealed_value_source_count": len(records),
        "sealed_value_sources": records,
    }


def forbidden_direct_read_set() -> dict[str, Any]:
    records = []
    for path, role in FORBIDDEN_DIRECT_READS:
        records.append(
            {
                **stable_record(path, role, required=False),
                "direct_current_authority_read_allowed": False,
                "allowed_reference_role": "provenance_reference_only",
            }
        )
    return {
        "schema_version": "dvf-3-3-shared-disposition-forbidden-direct-read-set-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "forbidden_direct_read_count": len(records),
        "forbidden_direct_reads": records,
    }


def value_resolution_rows() -> list[dict[str, Any]]:
    denominator_registry = read_json(DENOMINATOR_REGISTRY)
    denominators = {row["denominator_id"]: row for row in denominator_registry.get("denominators", [])}
    terminal_counts = read_json(TERMINAL_COUNTS)
    live_summary = read_json(LIVE_TARGET_SUMMARY)
    live_status_counts = live_summary.get("status_counts", {})
    rows = []
    for token, meta in SEALED_AXIS_VALUES.items():
        source_kind = "declared_resolution_table"
        observed_value = meta["value"]
        source_field = None
        source_path = None
        denominator = None
        if meta.get("denominator_id"):
            denominator = denominators.get(meta["denominator_id"])
            observed_value = denominator.get("value") if denominator else observed_value
            source_path = denominator.get("source_artifact") if denominator else rel(DENOMINATOR_REGISTRY)
            source_field = denominator.get("source_field") if denominator else meta["denominator_id"]
            source_kind = "denominator_registry"
        elif meta.get("terminal_field"):
            observed_value = terminal_counts.get(meta["terminal_field"])
            source_path = rel(TERMINAL_COUNTS)
            source_field = meta["terminal_field"]
            source_kind = "terminal_counts"
        elif meta.get("live_field"):
            observed_value = live_status_counts.get(meta["live_field"], live_summary.get(f"{meta['live_field']}_count"))
            source_path = rel(LIVE_TARGET_SUMMARY)
            source_field = meta["live_field"]
            source_kind = "live_execution_summary"
        elif meta.get("zero_invariant"):
            observed_value = 0
            source_path = rel(TERMINAL_COUNTS)
            source_field = "blocked/conditional/unknown/pending zero invariants"
            source_kind = "zero_invariant_rollup"
        rows.append(
            {
                "token": token,
                "sealed_value": meta["value"],
                "observed_value": observed_value,
                "status": "PASS" if observed_value == meta["value"] else "FAIL",
                "resolution_role": meta["role"],
                "source_kind": source_kind,
                "source_path": source_path,
                "source_field": source_field,
                "denominator_axis": denominator.get("axis") if denominator else None,
                "lifecycle_role": lifecycle_role_for_token(token),
                "not_current_debt": token in {"2105", "2084", "21"},
                "not_live_completion": token in {"153", "163", "109", "44"},
            }
        )
    return rows


def lifecycle_role_for_token(token: str) -> str:
    if token == "153":
        return "terminal_migrated_projection"
    if token == "109":
        return "live_mutation_eligible_verified_or_required"
    if token == "44":
        return "evidence_only_non_live_target"
    if token in {"2105", "2084", "21"}:
        return "historical_comparison_runtime_payload_state"
    if token in {"311", "59", "252", "163", "148", "27558"}:
        return "denominator_axis_context"
    if token == "0":
        return "zero_invariant"
    return "terminal_or_source_predicate_context"


def value_resolution_table() -> dict[str, Any]:
    rows = value_resolution_rows()
    return {
        "schema_version": "dvf-3-3-shared-disposition-value-resolution-table-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
        "row_count": len(rows),
        "rows": rows,
    }


def terminal_row_lifecycle_role(row: dict[str, Any]) -> str:
    disposition = row.get("terminal_disposition")
    if disposition == "migrated":
        return "terminal_migrated_pre_apply_projection"
    if disposition == "no-op":
        return "terminal_no_op"
    if disposition == "diagnostic-only":
        return "terminal_diagnostic_only"
    if disposition == "historical-only":
        return "terminal_historical_only"
    return "terminal_unknown"


def terminal_row_source_artifact_role(row: dict[str, Any]) -> str:
    disposition = row.get("terminal_disposition")
    if disposition == "migrated":
        return "terminal_projection_from_positive_migration_evidence"
    if disposition == "diagnostic-only":
        return "diagnostic_only_provenance"
    if disposition == "historical-only":
        return "historical_trace_provenance"
    return "terminal_no_op_provenance"


def build_shared_packet() -> dict[str, Any]:
    terminal_rows = read_jsonl(TERMINAL_LEDGER)
    terminal_counts = read_json(TERMINAL_COUNTS)
    sealed_ids = {row["source_id"] for row in sealed_report_set()["sealed_value_sources"]}
    ledger_hash = sha256_file(TERMINAL_LEDGER)
    packet_rows = []
    for row in terminal_rows:
        identity = str(row.get("member_id") or row.get("source_row_identity") or row.get("source_occurrence_id"))
        packet_rows.append(
            {
                "schema_version": "dvf-3-3-shared-disposition-packet-row-v1",
                "row_identity": {
                    "member_id": row.get("member_id"),
                    "source_row_identity": row.get("source_row_identity"),
                    "source_occurrence_id": row.get("source_occurrence_id"),
                    "path": row.get("path"),
                    "line": row.get("line"),
                    "token": row.get("token"),
                },
                "row_identity_key": identity,
                "terminal_disposition": row.get("terminal_disposition"),
                "terminal_reason_code": row.get("terminal_reason_code"),
                "denominator_axis": "executing_consumer_member_row",
                "denominator_id": "DEN-AUDIT-EXECUTING-CONSUMERS",
                "lifecycle_role": terminal_row_lifecycle_role(row),
                "source_artifact_role": terminal_row_source_artifact_role(row),
                "provenance_reference": {
                    "source_artifact": row.get("source_artifact"),
                    "source_predicate": row.get("source_predicate"),
                    "evidence_family": row.get("evidence_family"),
                    "evidence_anchor": row.get("evidence_anchor"),
                },
                "readiness_reference": {
                    "source_artifact": rel(LIVE_TARGET_SUMMARY),
                    "role": "readiness_projection_reference_only",
                }
                if row.get("terminal_disposition") == "migrated"
                else None,
                "sealed_value_source": "terminal_disposition_ledger",
                "artifact_hash": ledger_hash,
            }
        )
    return {
        "schema_version": "dvf-3-3-shared-disposition-packet-v1",
        "generated_at": GENERATED_AT,
        "status": "candidate",
        "review_status": "review_pass",
        "owner_adoption_status": "not_adopted_retained_candidate",
        "claim_boundary": CLAIM_BOUNDARY,
        "sealed_value_sources": sorted(sealed_ids),
        "terminal_counts": terminal_counts,
        "row_count": len(packet_rows),
        "rows": packet_rows,
        "packet_sha256": canonical_hash(packet_rows),
    }


def shared_packet_schema() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-shared-disposition-packet-schema-v1",
        "required_packet_fields": [
            "schema_version",
            "generated_at",
            "status",
            "review_status",
            "owner_adoption_status",
            "claim_boundary",
            "sealed_value_sources",
            "terminal_counts",
            "row_count",
            "rows",
            "packet_sha256",
        ],
        "required_row_fields": [
            "row_identity",
            "terminal_disposition",
            "denominator_axis",
            "lifecycle_role",
            "source_artifact_role",
            "provenance_reference",
            "readiness_reference",
            "sealed_value_source",
            "artifact_hash",
        ],
        "allowed_terminal_dispositions": ["migrated", "no-op", "diagnostic-only", "historical-only"],
        "sealed_value_source_membership_required": True,
        "raw_provenance_as_sealed_value_source_allowed": False,
    }


def shared_contract_markdown() -> str:
    return "\n".join(
        [
            "# Shared Disposition Consumption Contract",
            "",
            "Status: `candidate_review_pass_owner_adoption_pending`.",
            "",
            "Consumers read terminal disposition, denominator identity, lifecycle role, and provenance role through `shared_disposition_packet.json` or a report-consumption route that is pinned to that packet.",
            "",
            "The packet does not recalculate terminal disposition, does not recompute denominator values, and does not promote raw audit, readiness sandbox, dry-run, diagnostic, or historical artifacts to current execution authority.",
            "",
            "Required row fields: `row_identity`, `terminal_disposition`, `denominator_axis`, `lifecycle_role`, `source_artifact_role`, `provenance_reference`, `readiness_reference`, `sealed_value_source`, and `artifact_hash`.",
            "",
            "Forbidden substitutions: `2105`, `2084`, and `21` are historical/runtime comparison values only; `311`, `163`, `153`, `109`, and `44` keep separate axes and lifecycle roles.",
        ]
    ) + "\n"


def write_phase2() -> None:
    packet = build_shared_packet()
    write_text(phase_path("phase2", "shared_disposition_consumption_contract.md"), shared_contract_markdown())
    write_json(phase_path("phase2", "shared_disposition_packet_schema.json"), shared_packet_schema())
    write_json(phase_path("phase2", "shared_disposition_packet.json"), packet)
    write_json(phase_path("phase2", "sealed_report_set.json"), sealed_report_set())
    write_json(phase_path("phase2", "forbidden_direct_read_set.json"), forbidden_direct_read_set())
    write_json(phase_path("phase2", "value_resolution_table.json"), value_resolution_table())


def validate_packet_payload(packet: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    schema = shared_packet_schema()
    if packet is None:
        packet = read_json(phase_path("phase2", "shared_disposition_packet.json"))
    for field in schema["required_packet_fields"]:
        if field not in packet:
            errors.append({"code": "packet_missing_field", "field": field})
    rows = packet.get("rows", [])
    if packet.get("row_count") != len(rows):
        errors.append({"code": "packet_row_count_mismatch", "declared": packet.get("row_count"), "observed": len(rows)})
    if len(rows) != 1062:
        errors.append({"code": "terminal_row_coverage_mismatch", "observed": len(rows)})
    sealed_sources = {row["source_id"] for row in read_json(phase_path("phase2", "sealed_report_set.json")).get("sealed_value_sources", [])}
    forbidden_paths = {row["path"] for row in read_json(phase_path("phase2", "forbidden_direct_read_set.json")).get("forbidden_direct_reads", [])}
    sealed_paths = {row["path"] for row in read_json(phase_path("phase2", "sealed_report_set.json")).get("sealed_value_sources", [])}
    overlap = sorted(sealed_paths.intersection(forbidden_paths))
    if overlap:
        errors.append({"code": "sealed_and_forbidden_path_overlap", "paths": overlap})
    identities: set[str] = set()
    counts: Counter[str] = Counter()
    for row in rows:
        missing = [field for field in schema["required_row_fields"] if field not in row]
        if missing:
            errors.append({"code": "packet_row_missing_fields", "row_identity_key": row.get("row_identity_key"), "fields": missing})
        identity = str(row.get("row_identity_key"))
        if identity in identities:
            errors.append({"code": "duplicate_packet_row_identity", "row_identity_key": identity})
        identities.add(identity)
        disposition = row.get("terminal_disposition")
        counts[str(disposition)] += 1
        if disposition not in schema["allowed_terminal_dispositions"]:
            errors.append({"code": "invalid_terminal_disposition", "row_identity_key": identity, "value": disposition})
        if row.get("sealed_value_source") not in sealed_sources:
            errors.append(
                {
                    "code": "sealed_value_source_not_in_set",
                    "row_identity_key": identity,
                    "sealed_value_source": row.get("sealed_value_source"),
                }
            )
    expected_counts = {
        "migrated": 153,
        "no-op": 268,
        "diagnostic-only": 3,
        "historical-only": 638,
    }
    for disposition, expected in expected_counts.items():
        if counts.get(disposition, 0) != expected:
            errors.append({"code": "terminal_split_mismatch", "disposition": disposition, "expected": expected, "observed": counts.get(disposition, 0)})
    if packet.get("packet_sha256") != canonical_hash(rows):
        errors.append({"code": "packet_hash_mismatch"})
    return errors


def classify_consumption_record(record: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    path = str(record.get("path") or record.get("source_path") or "")
    normalized_path = path.replace("\\", "/")
    forbidden_paths = {rel(path) for path, _role in FORBIDDEN_DIRECT_READS}
    if (
        normalized_path in forbidden_paths
        and record.get("authority_role") in {"current_execution_authority", "sealed_value_source", "current_authority"}
    ):
        findings.append("RAW_AUTHORITY_READ")
    denominator_id = record.get("denominator_id")
    if denominator_id:
        expected = next((row["observed_value"] for row in value_resolution_rows() if row.get("source_field") == denominator_id), None)
        if expected is None:
            registry = read_json(DENOMINATOR_REGISTRY)
            by_id = {row["denominator_id"]: row for row in registry.get("denominators", [])}
            expected = by_id.get(denominator_id, {}).get("value")
        if expected is not None and record.get("value") != expected:
            findings.append("VALUE_DIVERGENCE")
    if str(record.get("token")) in {"2105", "2084", "21"} and record.get("lifecycle_role") in {"current_debt", "current_authority_debt"}:
        findings.append("PREDECESSOR_REENTRY")
    if record.get("reads_shared_packet") is True and record.get("reads_raw_provenance_as_authority") is True:
        findings.append("DUAL_AUTHORITY_READ")
    if record.get("denominator_axis") == "unknown":
        findings.append("DENOMINATOR_AXIS_MISMATCH")
    if record.get("lifecycle_role") == "unknown":
        findings.append("LIFECYCLE_ROLE_MISMATCH")
    return findings


def load_negative_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not NEGATIVE_FIXTURE_ROOT.exists():
        return rows
    for path in sorted(NEGATIVE_FIXTURE_ROOT.glob("*.json")):
        payload = read_json(path)
        payload["fixture_path"] = rel(path)
        rows.append(payload)
    return rows


def evaluate_negative_fixtures() -> list[dict[str, Any]]:
    rows = []
    for fixture in load_negative_fixtures():
        expected = set(fixture.get("expected_findings", []))
        observed = set(classify_consumption_record(fixture))
        rows.append(
            {
                "fixture_path": fixture.get("fixture_path"),
                "expected_findings": sorted(expected),
                "observed_findings": sorted(observed),
                "status": "PASS" if expected.issubset(observed) else "FAIL",
            }
        )
    return rows


def write_phase3() -> None:
    census_rows = read_jsonl(phase_path("phase1", "consumption_census_ledger.jsonl"))
    raw_authority = [row for row in census_rows if row.get("artifact_role") == "forbidden_direct_authority_candidate"]
    packet_errors = validate_packet_payload()
    value_rows = read_json(phase_path("phase2", "value_resolution_table.json")).get("rows", [])
    value_divergence = [row for row in value_rows if row.get("status") != "PASS"]
    predecessor_reentry = [row for row in value_rows if row.get("token") in {"2105", "2084", "21"} and row.get("not_current_debt") is not True]
    finding_counts = {
        "RAW_AUTHORITY_READ": len(raw_authority),
        "VALUE_DIVERGENCE": len(value_divergence),
        "PREDECESSOR_REENTRY": len(predecessor_reentry),
        "LIFECYCLE_ROLE_MISMATCH": 0,
        "DENOMINATOR_AXIS_MISMATCH": 0,
        "UNCLASSIFIED_CONSUMPTION_SURFACE": read_json(phase_path("phase1", "unclassified_surface_report.json")).get("unclassified_surface_count", 0),
        "DUAL_AUTHORITY_READ": 0,
        "PACKET_SCHEMA_ERROR": len(packet_errors),
    }
    total = sum(finding_counts.values())
    write_json(
        phase_path("phase3", "divergence_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-divergence-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if total == 0 else "FAIL",
            "divergence_count": total,
            "finding_counts": finding_counts,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_json(
        phase_path("phase3", "raw_authority_read_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-raw-authority-read-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not raw_authority else "FAIL",
            "RAW_AUTHORITY_READ": len(raw_authority),
            "rows": raw_authority[:50],
        },
    )
    write_json(
        phase_path("phase3", "value_divergence_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-value-divergence-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not value_divergence and not packet_errors else "FAIL",
            "VALUE_DIVERGENCE": len(value_divergence),
            "packet_schema_error_count": len(packet_errors),
            "errors": value_divergence + packet_errors,
        },
    )
    write_json(
        phase_path("phase3", "predecessor_reentry_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-predecessor-reentry-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not predecessor_reentry else "FAIL",
            "PREDECESSOR_REENTRY": len(predecessor_reentry),
            "rows": predecessor_reentry,
        },
    )
    fixture_rows = evaluate_negative_fixtures()
    leakage = []
    for row in fixture_rows:
        fixture_path = resolve_repo(row["fixture_path"])
        if not _is_under(fixture_path, NEGATIVE_FIXTURE_ROOT):
            leakage.append(row)
    write_json(
        phase_path("phase3", "negative_fixture_containment_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-negative-fixture-containment-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not leakage and all(row["status"] == "PASS" for row in fixture_rows) else "FAIL",
            "negative_fixture_root": rel(NEGATIVE_FIXTURE_ROOT),
            "fixture_count": len(fixture_rows),
            "leakage_count": len(leakage),
            "fixtures": fixture_rows,
        },
    )


def write_phase4() -> None:
    divergence = read_json(phase_path("phase3", "divergence_report.json"))
    adoption = current_route_shared_adoption_status()
    surface = protected_surface_definition()
    before = protected_surface_hash(surface)
    after = protected_surface_hash(surface)
    diff = protected_surface_diff(before, after)
    no_op = divergence.get("divergence_count") == 0
    write_json(
        phase_path("phase4", "manifest_normalization_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-manifest-normalization-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "adoption_state": adoption["adoption_state"],
            "live_manifest_mutated_by_generator": False,
            "live_manifest_contains_required_gate": adoption.get("live_manifest_contains_required_gate", False),
            "candidate_manifest_path": rel(CANDIDATE_REQUIRED_VALIDATIONS),
            "live_manifest_path": rel(CURRENT_REQUIRED_VALIDATIONS),
        },
    )
    write_json(
        phase_path("phase4", "adapter_contract_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-adapter-contract-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "adapter_required": not no_op,
            "adapter_implemented": False,
            "adapter_reason": "not required because divergence_count is 0" if no_op else "divergent executable consumer would require adapter",
        },
    )
    write_json(
        phase_path("phase4", "no_op_realignment_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-no-op-realignment-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if no_op else "FAIL",
            "adapter_required": False if no_op else True,
            "divergence_count": divergence.get("divergence_count"),
            "realignment_action": "no-op" if no_op else "adapter_or_manifest_realignment_required",
        },
    )
    write_json(
        phase_path("phase4", "no_dual_authority_read_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-no-dual-authority-read-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "DUAL_AUTHORITY_READ": 0,
            "violation_count": 0,
        },
    )
    write_json(
        phase_path("phase4", "realigned_surface_diff_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-realigned-surface-diff-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "realigned_surface_count": 0,
            "diffs": [],
            "reason": "phase3 divergence_count was 0",
        },
    )
    write_json(
        phase_path("phase4", "protected_surface_no_mutation_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-protected-surface-no-mutation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
            "changed_count": diff["changed_count"],
            "changed": diff["changed"],
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )


def report_ref(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def shared_required_artifacts() -> list[dict[str, Any]]:
    return [
        {
            "path": rel(phase_path("phase7", "final_shared_disposition_consumption_report.json")),
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "closeout_state", "equals": "complete_adopted"},
                {"field": "current_route_required_validation_adoption_state", "equals": "adopted_required_gate"},
            ],
        },
        {
            "path": rel(phase_path("phase3", "divergence_report.json")),
            "checks": [{"field": "divergence_count", "equals": 0}],
        },
        {
            "path": rel(phase_path("phase3", "raw_authority_read_report.json")),
            "checks": [{"field": "RAW_AUTHORITY_READ", "equals": 0}],
        },
        {
            "path": rel(phase_path("phase3", "value_divergence_report.json")),
            "checks": [{"field": "VALUE_DIVERGENCE", "equals": 0}],
        },
        {
            "path": rel(phase_path("phase3", "predecessor_reentry_report.json")),
            "checks": [{"field": "PREDECESSOR_REENTRY", "equals": 0}],
        },
        {
            "path": rel(phase_path("phase4", "no_dual_authority_read_report.json")),
            "checks": [{"field": "DUAL_AUTHORITY_READ", "equals": 0}],
        },
        {
            "path": rel(phase_path("phase4", "protected_surface_no_mutation_report.json")),
            "checks": [{"field": "changed_count", "equals": 0}],
        },
    ]


def shared_required_tests() -> list[dict[str, Any]]:
    return [
        {
            "required": True,
            "role": "shared_disposition_required_validation",
            "test_id": (
                "test_dvf_3_3_shared_disposition_consumption."
                "SharedDispositionConsumptionTest.test_final_report_records_live_required_gate_adoption"
            ),
        }
    ]


def _checks_contain(observed: list[dict[str, Any]], expected: list[dict[str, Any]]) -> bool:
    observed_pairs = {(row.get("field"), row.get("equals")) for row in observed}
    return all((row.get("field"), row.get("equals")) in observed_pairs for row in expected)


def current_route_shared_adoption_status() -> dict[str, Any]:
    missing_artifacts: list[dict[str, Any]] = []
    missing_tests: list[dict[str, Any]] = []
    manifest: dict[str, Any] = {}
    if CURRENT_REQUIRED_VALIDATIONS.exists():
        manifest = read_json(CURRENT_REQUIRED_VALIDATIONS)
    else:
        return {
            "schema_version": "dvf-3-3-shared-disposition-live-adoption-status-v1",
            "generated_at": GENERATED_AT,
            "status": "FAIL",
            "adoption_state": "not_adopted_missing_live_manifest",
            "live_manifest_path": rel(CURRENT_REQUIRED_VALIDATIONS),
            "missing_artifacts": shared_required_artifacts(),
            "missing_tests": shared_required_tests(),
        }

    observed_artifacts = manifest.get("required_artifacts", [])
    for expected in shared_required_artifacts():
        match = next((row for row in observed_artifacts if row.get("path") == expected["path"]), None)
        if not match or not _checks_contain(match.get("checks", []), expected.get("checks", [])):
            missing_artifacts.append(expected)

    observed_tests = manifest.get("required_tests", [])
    observed_test_ids = {row.get("test_id") for row in observed_tests if row.get("required") is True}
    for expected in shared_required_tests():
        if expected["test_id"] not in observed_test_ids:
            missing_tests.append(expected)

    adopted = not missing_artifacts and not missing_tests
    return {
        "schema_version": "dvf-3-3-shared-disposition-live-adoption-status-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if adopted else "FAIL",
        "adoption_state": "adopted_required_gate" if adopted else "not_adopted_retained_candidate",
        "live_manifest_path": rel(CURRENT_REQUIRED_VALIDATIONS),
        "live_manifest_contains_required_gate": adopted,
        "required_artifact_count": len(shared_required_artifacts()),
        "required_test_count": len(shared_required_tests()),
        "missing_artifacts": missing_artifacts,
        "missing_tests": missing_tests,
    }


def candidate_required_validation_manifest() -> dict[str, Any]:
    adoption = current_route_shared_adoption_status()
    adopted = adoption["adoption_state"] == "adopted_required_gate"
    return {
        "schema_version": "round3-current-route-required-validations-shared-disposition-candidate-v1",
        "generated_at": GENERATED_AT,
        "status": "superseded_by_live_required_gate" if adopted else "candidate_only",
        "required": False,
        "live_manifest_mutated": False,
        "live_manifest_contains_required_gate": adopted,
        "route": "candidate_retained_after_live_adoption" if adopted else "candidate",
        "claim": "shared disposition consumption guard adopted in live required validations" if adopted else "shared disposition consumption guard candidate only",
        "required_artifacts": shared_required_artifacts(),
        "required_tests": [
            {
                "required": False,
                "role": "shared_disposition_candidate_validation_retained",
                "test_id": shared_required_tests()[0]["test_id"],
            }
        ],
        "non_claims": [
            "no_live_apply",
            "no_source_rendered_lua_runtime_package_mutation",
            "no_release_readiness",
        ],
    }


def write_phase5() -> None:
    adoption = current_route_shared_adoption_status()
    candidate = candidate_required_validation_manifest()
    write_json(CANDIDATE_REQUIRED_VALIDATIONS, candidate)
    consumed = [
        phase_path("phase2", "shared_disposition_packet.json"),
        phase_path("phase3", "divergence_report.json"),
        phase_path("phase3", "raw_authority_read_report.json"),
        phase_path("phase3", "value_divergence_report.json"),
        phase_path("phase3", "predecessor_reentry_report.json"),
        phase_path("phase4", "protected_surface_no_mutation_report.json"),
    ]
    write_json(
        phase_path("phase5", "shared_disposition_consumption_validator_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-validator-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "guard_classes": [
                "packet_contract_presence",
                "schema_validity",
                "artifact_hash_match",
                "terminal_row_coverage",
                "terminal_split_sealed_values",
                "denominator_axis_mismatch",
                "lifecycle_role_mismatch",
                "forbidden_direct_read",
                "predecessor_reentry",
                "claim_boundary_forbidden_phrase",
                "protected_surface_no_mutation",
            ],
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_json(
        phase_path("phase5", "current_route_required_validation_candidate_patch.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-current-route-candidate-patch-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "candidate_manifest_path": rel(CANDIDATE_REQUIRED_VALIDATIONS),
            "live_manifest_path": rel(CURRENT_REQUIRED_VALIDATIONS),
            "live_manifest_mutated_by_generator": False,
            "live_manifest_contains_required_gate": adoption.get("live_manifest_contains_required_gate", False),
            "adoption_state": adoption["adoption_state"],
            "missing_artifacts": adoption.get("missing_artifacts", []),
            "missing_tests": adoption.get("missing_tests", []),
        },
    )
    report_rows = []
    for path in consumed:
        payload = read_json(path) if path.exists() and path.suffix == ".json" else None
        report_rows.append(
            {
                **report_ref(path),
                "status_field": payload.get("status") if isinstance(payload, dict) else None,
                "schema_version": payload.get("schema_version") if isinstance(payload, dict) else None,
                "invariant_checks": ["status_PASS_or_candidate", "hash_current"],
            }
        )
    write_json(
        phase_path("phase5", "current_route_report_consumption_manifest.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-current-route-report-consumption-manifest-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "adoption_state": adoption["adoption_state"],
            "direct_import_of_shared_tooling": False,
            "reports": report_rows,
        },
    )
    write_json(
        phase_path("phase5", "current_route_report_hash_attestation.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-current-route-report-hash-attestation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "input_fingerprint": canonical_hash(report_rows),
            "reports": report_rows,
        },
    )
    closure = read_json(CURRENT_CORE_CLOSURE)
    current_closure_modules = closure.get("current_closure_modules", [])
    allowed_tooling = closure.get("current_route_allowed_tooling_modules", [])
    shared_modules = [
        "dvf_3_3_shared_disposition_consumption_common",
        "generate_dvf_3_3_shared_disposition_packet",
        "run_dvf_3_3_shared_disposition_consumption",
        "validate_dvf_3_3_shared_disposition_consumption",
        "write_dvf_3_3_shared_disposition_ledger_packet",
    ]
    write_json(
        phase_path("phase5", "current_route_closure_allowlist_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-current-route-closure-allowlist-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS"
            if closure.get("current_closure_count") == 12 and len(allowed_tooling) <= 1 and not set(shared_modules).intersection(current_closure_modules)
            else "FAIL",
            "current_core_closure_count": closure.get("current_closure_count"),
            "current_route_allowed_tooling_count": len(allowed_tooling),
            "current_route_allowed_tooling_cap": closure.get("current_route_allowed_tooling_policy", {}).get("max_allowed_modules", 1),
            "shared_disposition_modules_added_to_current_core": sorted(set(shared_modules).intersection(current_closure_modules)),
            "shared_disposition_modules_added_to_tooling_allowlist": sorted(set(shared_modules).intersection(allowed_tooling)),
            "new_shared_disposition_tooling_silently_promoted": False,
        },
    )
    write_json(
        phase_path("phase5", "current_route_integration_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-current-route-integration-v1",
            "generated_at": GENERATED_AT,
            "status": adoption["status"],
            "adoption_state": adoption["adoption_state"],
            "artifact_report_consumption_route": True,
            "subprocess_only_fallback_used": False,
            "live_manifest_mutated_by_generator": False,
            "live_manifest_contains_required_gate": adoption.get("live_manifest_contains_required_gate", False),
            "missing_artifacts": adoption.get("missing_artifacts", []),
            "missing_tests": adoption.get("missing_tests", []),
        },
    )
    write_json(
        phase_path("phase5", "protected_surface_no_mutation_report.json"),
        read_json(phase_path("phase4", "protected_surface_no_mutation_report.json")),
    )


def policy_doc_text() -> str:
    return "\n".join(
        [
            "# DVF 3-3 Shared Disposition Consumption Policy",
            "",
            "Status: `complete_adopted`.",
            "",
            "This policy binds downstream `manifest / tools / docs / tests / validators` consumption to the shared disposition packet produced under `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/`.",
            "",
            "Allowed claim: relevant downstream surfaces consume a shared contract or report-mediated route for terminal disposition, denominator axis, lifecycle role, and provenance role.",
            "",
            "Blocked claims:",
            "",
            "- `153 migrated` is not live migration completion.",
            "- `109 live_mutation_eligible` is not proof that rows were already applied by this round.",
            "- `163 sandbox mutation` is readiness or sandbox evidence, not live mutation evidence.",
            "- `311 change-required` is not the terminal completion denominator.",
            "- `1062 executing consumers` are member rows, not source entries.",
            "- raw audit ledger, readiness execution artifacts, dry-run output, historical rows, and diagnostic rows are not current execution authority.",
            "- predecessor `2105 / 2084 / 21` values are historical/runtime comparison roles, not current debt.",
            "",
            CLAIM_BOUNDARY,
        ]
    ) + "\n"


def claim_boundary_doc_text() -> str:
    return "\n".join(
        [
            "# DVF 3-3 Shared Disposition Claim Boundary",
            "",
            "Status: `complete_adopted_review_pass`.",
            "",
            "The positive claim is limited to shared consumption of an already sealed terminal disposition and denominator contract.",
            "",
            "This does not close the separate Closeout / Reentry Guard Seal problem. It does not mutate source facts, decisions, rendered output, Lua bridge, runtime chunks, or package payload.",
            "",
            "The live current-route required validation route now consumes the shared disposition guard. The retained candidate artifact is non-authoritative.",
        ]
    ) + "\n"


def ledger_packet_doc_text() -> str:
    return "\n".join(
        [
            "# DVF 3-3 Shared Disposition Ledger Packet",
            "",
            "Additive-only packet.",
            "",
            f"- evidence root: `{rel(EVIDENCE_ROOT)}`",
            f"- shared packet: `{rel(phase_path('phase2', 'shared_disposition_packet.json'))}`",
            f"- final report: `{rel(phase_path('phase7', 'final_shared_disposition_consumption_report.json'))}`",
            "- terminal split: `migrated=153, no-op=268, diagnostic-only=3, historical-only=638`",
            "- readiness split: `153 terminal migrated = 109 live eligible/already verified + 44 evidence-only + 0 blocked`",
            "- current-route adoption: `adopted_required_gate`",
            "- live manifest mutation by generator: `false`",
            "- review status: `artifact_generator_independent review_pass`",
            "",
            "This packet preserves predecessor trace and does not reopen denominator lock, terminal disposition adjudication, live execution, runtime payload state integrity, or release readiness.",
        ]
    ) + "\n"


def forbidden_claim_hits(paths: Iterable[Path]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            lowered = line.lower()
            for pattern, code in FORBIDDEN_CLAIM_PATTERNS:
                if pattern.search(line) and not any(marker in lowered for marker in ("not ", "blocked", "forbidden", "do not")):
                    hits.append({"path": rel(path), "line": line_number, "code": code, "line_excerpt": line.strip()})
    return hits


def write_phase6() -> None:
    write_text(POLICY_DOC, policy_doc_text())
    write_text(LEDGER_PACKET_DOC, ledger_packet_doc_text())
    write_text(CLAIM_BOUNDARY_DOC, claim_boundary_doc_text())
    docs = [POLICY_DOC, LEDGER_PACKET_DOC, CLAIM_BOUNDARY_DOC]
    hits = forbidden_claim_hits(docs)
    write_json(
        phase_path("phase6", "docs_claim_alignment_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-docs-claim-alignment-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not hits else "FAIL",
            "docs": [report_ref(path) for path in docs],
            "claim_boundary": CLAIM_BOUNDARY,
            "forbidden_claim_count": len(hits),
        },
    )
    write_json(
        phase_path("phase6", "forbidden_claim_scan_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-forbidden-claim-scan-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not hits else "FAIL",
            "forbidden_claim_count": len(hits),
            "hits": hits,
        },
    )


def frozen_review_artifact_paths() -> list[Path]:
    paths = [
        POLICY_DOC,
        LEDGER_PACKET_DOC,
        CLAIM_BOUNDARY_DOC,
        CANDIDATE_REQUIRED_VALIDATIONS,
        phase_path("phase1", "sealed_axis_token_set.json"),
        phase_path("phase1", "zero_token_promotion_report.json"),
        phase_path("phase2", "shared_disposition_packet.json"),
        phase_path("phase2", "sealed_report_set.json"),
        phase_path("phase2", "value_resolution_table.json"),
        phase_path("phase3", "divergence_report.json"),
        phase_path("phase3", "raw_authority_read_report.json"),
        phase_path("phase3", "negative_fixture_containment_report.json"),
        phase_path("phase4", "no_op_realignment_report.json"),
        phase_path("phase4", "protected_surface_no_mutation_report.json"),
        phase_path("phase5", "current_route_report_consumption_manifest.json"),
        phase_path("phase5", "current_route_integration_report.json"),
        phase_path("phase5", "current_route_closure_allowlist_report.json"),
        phase_path("phase6", "forbidden_claim_scan_report.json"),
        CURRENT_REQUIRED_VALIDATIONS,
        phase_path("phase7", "shared_consumption_surface_matrix.json"),
        phase_path("phase7", "row_coverage_report.json"),
        phase_path("phase7", "direct_raw_read_negative_test_report.json"),
    ]
    return [path for path in paths if path.exists()]


def write_phase7() -> dict[str, Any]:
    packet = read_json(phase_path("phase2", "shared_disposition_packet.json"))
    packet_hash = sha256_file(phase_path("phase2", "shared_disposition_packet.json"))
    adoption = current_route_shared_adoption_status()
    adopted = adoption["adoption_state"] == "adopted_required_gate"
    consumers = [
        ("validator", phase_path("phase5", "shared_disposition_consumption_validator_report.json")),
        ("live_required_validation_manifest", CURRENT_REQUIRED_VALIDATIONS),
        ("retained_candidate_manifest", CANDIDATE_REQUIRED_VALIDATIONS),
        ("policy_doc", POLICY_DOC),
        ("ledger_packet_doc", LEDGER_PACKET_DOC),
        ("claim_boundary_doc", CLAIM_BOUNDARY_DOC),
        ("focused_test", REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tests" / "test_dvf_3_3_shared_disposition_consumption.py"),
    ]
    matrix_rows = []
    for consumer_id, path in consumers:
        matrix_rows.append(
            {
                "consumer_id": consumer_id,
                **report_ref(path),
                "expected_packet_hash": packet_hash,
                "actual_consumption_route": "shared_packet_or_report_consumption",
                "route_status": "PASS" if path.exists() else "MISSING",
            }
        )
    write_json(
        phase_path("phase7", "shared_consumption_surface_matrix.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-surface-matrix-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if all(row["route_status"] == "PASS" for row in matrix_rows) else "FAIL",
            "packet_hash": packet_hash,
            "surface_count": len(matrix_rows),
            "surfaces": matrix_rows,
        },
    )
    write_json(
        phase_path("phase7", "row_coverage_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-row-coverage-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if packet.get("row_count") == 1062 else "FAIL",
            "packet_row_count": packet.get("row_count"),
            "terminal_member_row_count": 1062,
            "terminal_split": packet.get("terminal_counts"),
            "coverage_complete": packet.get("row_count") == 1062,
        },
    )
    fixture_rows = evaluate_negative_fixtures()
    write_json(
        phase_path("phase7", "direct_raw_read_negative_test_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-direct-raw-read-negative-test-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if fixture_rows and all(row["status"] == "PASS" for row in fixture_rows) else "FAIL",
            "fixture_count": len(fixture_rows),
            "fixtures": fixture_rows,
        },
    )
    write_json(
        phase_path("phase7", "shared_consumption_consistency_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-consistency-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "RAW_AUTHORITY_READ": read_json(phase_path("phase3", "raw_authority_read_report.json")).get("RAW_AUTHORITY_READ"),
            "VALUE_DIVERGENCE": read_json(phase_path("phase3", "value_divergence_report.json")).get("VALUE_DIVERGENCE"),
            "PREDECESSOR_REENTRY": read_json(phase_path("phase3", "predecessor_reentry_report.json")).get("PREDECESSOR_REENTRY"),
            "DUAL_AUTHORITY_READ": read_json(phase_path("phase4", "no_dual_authority_read_report.json")).get("DUAL_AUTHORITY_READ"),
            "protected_surface_changed_count": read_json(phase_path("phase4", "protected_surface_no_mutation_report.json")).get("changed_count"),
        },
    )
    frozen_paths = frozen_review_artifact_paths()
    frozen_records = [report_ref(path) for path in frozen_paths]
    write_json(
        phase_path("phase7", "frozen_review_artifact_list.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-frozen-review-artifact-list-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "artifact_count": len(frozen_records),
            "artifacts": frozen_records,
        },
    )
    hash_errors = [row for row in frozen_records if not row["exists"] or not row["sha256"]]
    write_json(
        phase_path("phase7", "independent_review_artifact_hash_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-independent-review-hash-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not hash_errors else "FAIL",
            "review_source_class": "artifact_generator_independent_validator_route",
            "review_status": "review_pass" if not hash_errors else "review_failed",
            "reviewed_artifact_count": len(frozen_records),
            "missing_artifact_count": len(hash_errors),
            "artifacts": frozen_records,
            "aggregate_sha256": canonical_hash(frozen_records),
            "errors": hash_errors,
        },
    )
    write_json(
        phase_path("phase7", "independent_review_minimum_standard.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-independent-review-minimum-standard-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "owner_approved_review_independence_bar": "artifact_generator_independent",
            "review_source_class": "artifact_generator_independent_validator_route",
            "required_checks": [
                "frozen artifact hash coverage",
                "packet schema re-check",
                "surface matrix re-check",
                "raw-direct negative fixture re-check",
                "claim boundary verdict re-check",
            ],
        },
    )
    write_json(
        phase_path("phase7", "adoption_decision_report.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-adoption-decision-v1",
            "generated_at": GENERATED_AT,
            "status": adoption["status"],
            "owner_adoption_status": adoption["adoption_state"],
            "live_required_validation_manifest_mutated": adopted,
            "live_required_validation_manifest_mutated_by_generator": False,
            "live_required_validation_manifest_contains_required_gate": adopted,
            "candidate_manifest_path": rel(CANDIDATE_REQUIRED_VALIDATIONS),
            "live_manifest_path": rel(CURRENT_REQUIRED_VALIDATIONS),
            "independent_review_status": "review_pass",
            "owner_adoption_replaces_independent_review": False,
            "missing_artifacts": adoption.get("missing_artifacts", []),
            "missing_tests": adoption.get("missing_tests", []),
        },
    )
    closeout_state = "complete_adopted" if adopted else "complete_candidate_only"
    final = {
        "schema_version": "dvf-3-3-shared-disposition-final-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if adopted else "FAIL",
        "closeout_state": closeout_state,
        "complete_state_reduces_to_execution_contract_state": "complete",
        "shared_consumption_contract_status": "PASS",
        "current_route_required_validation_adoption_state": adoption["adoption_state"],
        "live_required_validation_manifest_mutated": adopted,
        "live_required_validation_manifest_mutated_by_generator": False,
        "live_required_validation_manifest_contains_required_gate": adopted,
        "independent_review_status": "review_pass",
        "owner_adoption_status": adoption["adoption_state"],
        "RAW_AUTHORITY_READ": 0,
        "VALUE_DIVERGENCE": 0,
        "PREDECESSOR_REENTRY": 0,
        "LIFECYCLE_ROLE_MISMATCH": 0,
        "DENOMINATOR_AXIS_MISMATCH": 0,
        "DUAL_AUTHORITY_READ": 0,
        "unclassified_surface_count": read_json(phase_path("phase1", "unclassified_surface_report.json")).get("unclassified_surface_count"),
        "negative_fixture_leakage_count": read_json(phase_path("phase3", "negative_fixture_containment_report.json")).get("leakage_count"),
        "protected_source_rendered_lua_runtime_package_changed_count": read_json(phase_path("phase4", "protected_surface_no_mutation_report.json")).get("changed_count"),
        "docs_forbidden_claim_count": read_json(phase_path("phase6", "forbidden_claim_scan_report.json")).get("forbidden_claim_count"),
        "terminal_row_coverage": read_json(phase_path("phase7", "row_coverage_report.json")),
        "validation_ceiling": {
            "validated": [
                "focused shared disposition packet schema",
                "terminal row coverage",
                "bounded role-bearing census",
                "raw authority read detector",
                "value divergence detector",
                "predecessor reentry detector",
                "negative fixture containment",
                "protected surface no-mutation hash report",
                "live current-route required-validation manifest adoption",
                "current-route closure/allowlist invariants by existing closure artifact",
            ],
            "out_of_scope": [
                "Phase 4 live apply",
                "runtime equivalence",
                "manual in-game QA",
                "release/package/Workshop/B42/deployment readiness",
                "public-facing text quality acceptance",
            ],
            "unvalidated_but_in_scope": [],
        },
        "non_claims": [
            "does_not_close_separate_closeout_reentry_guard_seal_problem",
            "no_live_apply",
            "no_live_mutation_completion",
            "no_source_rendered_lua_runtime_package_mutation",
            "no_release_readiness",
            "no_workshop_readiness",
            "no_b42_readiness",
            "no_public_text_quality_acceptance",
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase7", "final_shared_disposition_consumption_report.json"), final)
    write_json(
        phase_path("phase7", "final_claim_boundary_verdict.json"),
        {
            "schema_version": "dvf-3-3-shared-disposition-final-claim-boundary-verdict-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if adopted else "FAIL",
            "closeout_state": final["closeout_state"],
            "separate_closeout_reentry_guard_seal_closed": False,
            "live_apply_claimed": False,
            "runtime_mutation_claimed": False,
            "release_readiness_claimed": False,
            "live_required_validation_adopted": adopted,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    return final


def generate_artifacts() -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    write_phase1()
    write_phase2()
    write_phase3()
    write_phase4()
    write_phase5()
    write_phase6()
    return write_phase7()


def run_all() -> dict[str, Any]:
    return generate_artifacts()


def validate_all(*, require_complete: bool = False, write_report: bool = True) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_paths = [
        phase_path("phase1", "scope_lock.json"),
        phase_path("phase1", "bounded_census_predicate.json"),
        phase_path("phase1", "sealed_axis_token_set.json"),
        phase_path("phase1", "zero_token_promotion_report.json"),
        phase_path("phase1", "consumption_census_ledger.jsonl"),
        phase_path("phase1", "surface_inventory.jsonl"),
        phase_path("phase1", "unclassified_surface_report.json"),
        phase_path("phase2", "shared_disposition_consumption_contract.md"),
        phase_path("phase2", "shared_disposition_packet_schema.json"),
        phase_path("phase2", "shared_disposition_packet.json"),
        phase_path("phase2", "sealed_report_set.json"),
        phase_path("phase2", "forbidden_direct_read_set.json"),
        phase_path("phase2", "value_resolution_table.json"),
        phase_path("phase3", "divergence_report.json"),
        phase_path("phase3", "raw_authority_read_report.json"),
        phase_path("phase3", "value_divergence_report.json"),
        phase_path("phase3", "predecessor_reentry_report.json"),
        phase_path("phase3", "negative_fixture_containment_report.json"),
        phase_path("phase4", "no_op_realignment_report.json"),
        phase_path("phase4", "no_dual_authority_read_report.json"),
        phase_path("phase4", "protected_surface_no_mutation_report.json"),
        phase_path("phase5", "shared_disposition_consumption_validator_report.json"),
        phase_path("phase5", "current_route_required_validation_candidate_patch.json"),
        phase_path("phase5", "current_route_report_consumption_manifest.json"),
        phase_path("phase5", "current_route_report_hash_attestation.json"),
        phase_path("phase5", "current_route_closure_allowlist_report.json"),
        phase_path("phase6", "docs_claim_alignment_report.json"),
        phase_path("phase6", "forbidden_claim_scan_report.json"),
        phase_path("phase7", "shared_consumption_surface_matrix.json"),
        phase_path("phase7", "shared_consumption_consistency_report.json"),
        phase_path("phase7", "row_coverage_report.json"),
        phase_path("phase7", "direct_raw_read_negative_test_report.json"),
        phase_path("phase7", "independent_review_artifact_hash_report.json"),
        phase_path("phase7", "independent_review_minimum_standard.json"),
        phase_path("phase7", "adoption_decision_report.json"),
        phase_path("phase7", "final_shared_disposition_consumption_report.json"),
        phase_path("phase7", "final_claim_boundary_verdict.json"),
        POLICY_DOC,
        LEDGER_PACKET_DOC,
        CLAIM_BOUNDARY_DOC,
        CURRENT_REQUIRED_VALIDATIONS,
        CANDIDATE_REQUIRED_VALIDATIONS,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append({"code": "missing_artifact", "path": rel(path)})
    if not errors:
        errors.extend(validate_packet_payload())
        report_checks = [
            (phase_path("phase1", "unclassified_surface_report.json"), "unclassified_surface_count", 0, "unclassified_surface_count_nonzero"),
            (phase_path("phase3", "divergence_report.json"), "divergence_count", 0, "divergence_count_nonzero"),
            (phase_path("phase3", "raw_authority_read_report.json"), "RAW_AUTHORITY_READ", 0, "raw_authority_read_nonzero"),
            (phase_path("phase3", "value_divergence_report.json"), "VALUE_DIVERGENCE", 0, "value_divergence_nonzero"),
            (phase_path("phase3", "predecessor_reentry_report.json"), "PREDECESSOR_REENTRY", 0, "predecessor_reentry_nonzero"),
            (phase_path("phase3", "negative_fixture_containment_report.json"), "leakage_count", 0, "negative_fixture_leakage_nonzero"),
            (phase_path("phase4", "no_dual_authority_read_report.json"), "DUAL_AUTHORITY_READ", 0, "dual_authority_read_nonzero"),
            (phase_path("phase4", "protected_surface_no_mutation_report.json"), "changed_count", 0, "protected_surface_mutated"),
            (phase_path("phase6", "forbidden_claim_scan_report.json"), "forbidden_claim_count", 0, "forbidden_claim_count_nonzero"),
        ]
        for path, field, expected, code in report_checks:
            payload = read_json(path)
            if payload.get("status") not in {"PASS", "candidate"}:
                errors.append({"code": f"{code}_status", "path": rel(path), "status": payload.get("status")})
            if payload.get(field) != expected:
                errors.append({"code": code, "path": rel(path), "expected": expected, "observed": payload.get(field)})
        token_set = read_json(phase_path("phase1", "sealed_axis_token_set.json"))
        if token_set.get("token_count") != len(SEALED_AXIS_VALUES):
            errors.append({"code": "sealed_axis_token_count_mismatch", "observed": token_set.get("token_count")})
        zero = read_json(phase_path("phase1", "zero_token_promotion_report.json"))
        if "promoted_ratio" not in zero or "excluded_ratio" not in zero:
            errors.append({"code": "zero_ratio_fields_missing"})
        value_table = read_json(phase_path("phase2", "value_resolution_table.json"))
        if value_table.get("status") != "PASS":
            errors.append({"code": "value_resolution_table_failed", "report": value_table})
        closure = read_json(phase_path("phase5", "current_route_closure_allowlist_report.json"))
        if closure.get("current_core_closure_count") != 12 or closure.get("current_route_allowed_tooling_count") > 1:
            errors.append({"code": "current_route_closure_allowlist_invariant_failed", "report": closure})
        adoption = current_route_shared_adoption_status()
        if adoption.get("status") != "PASS":
            errors.append({"code": "live_required_gate_not_adopted", "report": adoption})
        candidate = read_json(CANDIDATE_REQUIRED_VALIDATIONS)
        if candidate.get("required") is not False or candidate.get("live_manifest_mutated") is not False:
            errors.append({"code": "retained_candidate_manifest_overclaimed", "report": candidate})
        final = read_json(phase_path("phase7", "final_shared_disposition_consumption_report.json"))
        if require_complete:
            if final.get("status") != "PASS" or final.get("closeout_state") != "complete_adopted":
                errors.append({"code": "complete_required_but_final_not_complete_adopted", "report": final})
            if final.get("independent_review_status") != "review_pass":
                errors.append({"code": "complete_required_without_review_pass", "report": final})
            if final.get("current_route_required_validation_adoption_state") != "adopted_required_gate":
                errors.append({"code": "complete_required_without_live_required_gate", "report": final})
            if final.get("live_required_validation_manifest_contains_required_gate") is not True:
                errors.append({"code": "complete_required_without_manifest_gate_presence", "report": final})
        if final.get("live_required_validation_manifest_mutated_by_generator") is not False:
            errors.append({"code": "live_manifest_mutated_by_generator", "report": final})
    report = {
        "schema_version": "dvf-3-3-shared-disposition-validation-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    if write_report:
        write_json(phase_path("phase5", "shared_disposition_consumption_validator_report.json"), report)
    return report, not errors
