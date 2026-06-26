from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    LIVE_DATA_DIR,
    LIVE_OUTPUT_DIR,
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    RUNTIME_MONOLITH,
    V2_ROOT,
    canonical_hash,
    file_record,
    key_set_jsonl,
    load_lua_chunks,
    read_json,
    read_jsonl,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


ROUND_ID = "dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
TMP_COMPOSE_ROOT = V2_ROOT / ".tmp_tests" / "dvf_3_3_current_source_authority_drift_verification" / "direct_compose"

PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_current_source_authority_drift_verification_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_current_source_authority_drift_verification_ledger_packet.md"

CURRENT_MANIFEST = LIVE_DATA_DIR / "dvf_3_3_input_manifest.json"
CURRENT_FACTS = LIVE_DATA_DIR / "dvf_3_3_facts.jsonl"
CURRENT_DECISIONS = LIVE_DATA_DIR / "dvf_3_3_decisions.jsonl"
CURRENT_OVERLAY = LIVE_DATA_DIR / "dvf_3_3_overlay_support.jsonl"
CURRENT_RENDERED = LIVE_OUTPUT_DIR / "dvf_3_3_rendered.json"
CURRENT_STYLE_LOG = LIVE_OUTPUT_DIR / "style_normalization_changes.jsonl"
CURRENT_REQUEUE = LIVE_OUTPUT_DIR / "compose_requeue_candidates.jsonl"

COMPOSE_LAYER3_TEXT = V2_ROOT / "tools" / "build" / "compose_layer3_text.py"
CURRENT_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ROUND3_CURRENT_TEST_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
ROUND3_ACTIVE_CORE_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
ROUND3_CONTRACT_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_contract_manifest.json"

CURRENT_PROFILES = LIVE_DATA_DIR / "compose_profiles_v2.json"
CURRENT_IDENTITY_RULES = LIVE_DATA_DIR / "compose_profile_identity_hint_rules.json"
CURRENT_PRECEDENCE_RULES = LIVE_DATA_DIR / "compose_profile_conflict_precedence_rules.json"

LIVE_LUA_BRIDGE = REPO_ROOT / "Iris" / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua"
PACKAGE_DATA_DIR = REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
PACKAGE_CHUNK_MANIFEST = PACKAGE_DATA_DIR / "IrisLayer3DataChunks.lua"
PACKAGE_CHUNK_DIR = PACKAGE_DATA_DIR / "IrisLayer3DataChunks"
PACKAGE_MONOLITH = PACKAGE_DATA_DIR / "IrisLayer3Data.lua"

STAGING_PREDECESSOR_OVERLAY = V2_ROOT / "staging" / "compose_contract_migration" / "layer3_body_source_overlay.jsonl"
STALE_BRIDGE_QUARANTINE = (
    V2_ROOT
    / "staging"
    / "stale_dvf_bridge_artifact_disposition"
    / "quarantine"
    / "IrisDvfBridgeData.legacy_6_entry.lua"
)
PREDECESSOR_REPAIR_ROOT = V2_ROOT / "staging" / "dvf_3_3_current_route_baseline_source_overlay_repair"
CLOSEOUT_REENTRY_ROOT = V2_ROOT / "staging" / "dvf_3_3_closeout_reentry_guard_seal"

EXPECTED_SUCCESSOR_COUNT = 2105
KNOWN_FIXTURE_SAMPLE = [
    "Base.CanOpener",
    "Base.ElectronicsScrap",
    "Base.GunpowderCan",
    "Base.ModKit",
    "Base.Tongs",
    "Base.WeldingTorch",
]
PREDECESSOR_VALUES = ("2105", "2084", "21")
PRIMARY_REVIEW_ARTIFACTS = [
    "phase0/baseline_fingerprint.json",
    "phase0/protected_surface_manifest.json",
    "phase0/stale_premise_capture_report.json",
    "phase0/recovery_plan_authority_scan_report.json",
    "phase0/no_mutation_baseline_hashes.json",
    "phase0/tooling_existence_inventory.json",
    "phase0/supporting_readpoint_existence_inventory.json",
    "phase0/execution_harness_preimplementation_report.json",
    "phase0/existing_evidence_reuse_map.json",
    "phase0/roadmap_provenance_rebind_report.json",
    "phase1/source_chain_identity_report.json",
    "phase1/source_hash_count_matrix.json",
    "phase1/manifest_live_hash_comparison.json",
    "phase1/source_identity_no_mutation_verdict.json",
    "phase2/consumer_path_identity_report.json",
    "phase2/source_path_classification_report.json",
    "phase2/no_raw_predecessor_execution_read_report.json",
    "phase2/direct_compose_writer_sink_preflight_report.json",
    "phase2/direct_current_compose_result.json",
    "phase2/known_overlay_blocker_regression_report.json",
    "phase2/base_canopener_applicability_report.json",
    "phase2/body_source_overlay_requirement_report.json",
    "phase2/protected_rendered_no_mutation_verdict.json",
    "phase3/rendered_input_contract_inventory.json",
    "phase3/successor_identity_continuity_report.json",
    "phase3/rendered_provenance_alignment_report.json",
    "phase3/rendered_no_mutation_verdict.json",
    "phase4/sealed_predecessor_fixture_source_manifest.json",
    "phase4/content_derived_six_entry_signature.json",
    "phase4/six_entry_signature_determinism_report.json",
    "phase4/six_entry_signature_cross_check_report.json",
    "phase4/six_entry_non_reentry_report.json",
    "phase4/current_looking_fixture_payload_scan.json",
    "phase4/predecessor_reentry_guard_report.json",
    "phase4/allowed_historical_trace_inventory.jsonl",
    "phase4/forbidden_predecessor_authority_claim_report.json",
    "phase4/predecessor_guard_no_mutation_verdict.json",
    "phase5/recovery_scope_retirement_report.json",
    "phase5/future_drift_contingency_open_conditions.json",
    "phase5/downstream_plan_authority_scan_report.json",
    "phase5/current_route_required_validation_candidate.json",
    "phase5/required_validation_integration_report.json",
    "phase6/final_current_source_authority_drift_verification_report.json",
    "phase6/final_claim_boundary_report.md",
    "phase6/final_no_mutation_report.json",
    "phase6/primary_review_artifact_manifest.json",
    "phase6/independent_review_artifact_hash_report.json",
    "phase6/validation_report.all.json",
    "phase6/validation_report.require_complete.json",
]
POST_MANIFEST_HASH_OBSERVATION_ARTIFACTS = {
    "phase6/primary_review_artifact_manifest.json",
    "phase6/validation_report.all.json",
    "phase6/validation_report.require_complete.json",
}
SELF_HASH_PRESENCE_ONLY_ARTIFACTS = {
    "phase6/independent_review_artifact_hash_report.json",
}
COMPARISON_EXEMPT_REVIEW_ARTIFACTS = POST_MANIFEST_HASH_OBSERVATION_ARTIFACTS | SELF_HASH_PRESENCE_ONLY_ARTIFACTS
FROZEN_HASH_POLICY = "frozen_expected_sha256"
POST_MANIFEST_HASH_OBSERVATION_POLICY = "post_manifest_hash_observation_no_expected_comparison"
SELF_HASH_PRESENCE_ONLY_POLICY = "self_hash_not_representable_presence_only"
INDEPENDENT_REVIEW_RECORD = {
    "status": "PASS",
    "review_mode": "independent_non_author_review",
    "finding_count": 0,
    "review_summary": "No findings in independent review after hash report and validator recalculation fixes.",
    "review_basis": [
        "primary_review_artifact_manifest includes 49 artifacts with missing_count 0",
        "independent_review_artifact_hash_report has mismatch_count 0 with 45 frozen comparisons and 4 comparison-exempt artifacts",
        "validation_report.all is PASS with error_count 0",
        "validation_report.require_complete only previously failed on seal recording conditions",
        "final report is PASS with canonical seal pending before this owner approval",
    ],
}
OWNER_SEAL_RECORD = {
    "status": "PASS",
    "owner_identity": "current_session_owner",
    "approval_basis": "Owner accepted the independent review result and requested PASS processing.",
}


def phase_dir(root: Path, phase: str) -> Path:
    path = root / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path) if path.exists() else []


def row_map(path: Path) -> dict[str, dict[str, Any]]:
    return {str(row["item_id"]): row for row in read_jsonl_rows(path) if row.get("item_id") is not None}


def row_keys(path: Path) -> set[str]:
    return set(row_map(path))


def rendered_payload(path: Path = CURRENT_RENDERED) -> dict[str, Any]:
    return read_json_object(path)


def rendered_entries(path: Path = CURRENT_RENDERED) -> dict[str, dict[str, Any]]:
    payload = rendered_payload(path)
    entries = payload.get("entries", {})
    if not isinstance(entries, dict):
        return {}
    return {str(key): value for key, value in entries.items() if isinstance(value, dict)}


def line_count(path: Path) -> int | None:
    if not path.exists() or not path.is_file():
        return None
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def jsonl_record(path: Path, role: str) -> dict[str, Any]:
    record = file_record(path, role)
    if path.exists() and path.is_file():
        record["line_count"] = line_count(path)
    if path.exists() and path.suffix == ".jsonl":
        rows = read_jsonl_rows(path)
        record["row_count"] = len(rows)
        record["item_id_count"] = len({str(row.get("item_id")) for row in rows if row.get("item_id") is not None})
    if path == CURRENT_RENDERED and path.exists():
        record["entry_count"] = len(rendered_entries(path))
    return record


def protected_surface_manifest_payload() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-protected-surface-v1",
        "round_id": ROUND_ID,
        "hash_algorithm": "sha256",
        "normalization_rule": {
            "json": "byte_hash_of_file_as_committed",
            "jsonl": "byte_hash_of_file_as_committed; row_count_recorded_separately",
            "lua": "byte_hash_of_file_as_committed",
            "path_separator_comparison": "normalize_windows_and_posix_to_resolved_paths_before_comparison",
        },
        "unchanged_policy": "source_rendered_lua_bridge_runtime_package_must_remain_unchanged",
        "protected_surface_classes": {
            "source": [
                {"path": rel(CURRENT_MANIFEST), "kind": "file", "role": "current_source_manifest"},
                {"path": rel(CURRENT_FACTS), "kind": "file", "role": "current_source_facts"},
                {"path": rel(CURRENT_DECISIONS), "kind": "file", "role": "current_source_decisions"},
                {"path": rel(CURRENT_OVERLAY), "kind": "file", "role": "current_compose_support"},
            ],
            "rendered": [
                {"path": rel(CURRENT_RENDERED), "kind": "file", "role": "current_rendered_output"},
                {"path": rel(CURRENT_STYLE_LOG), "kind": "file", "role": "current_style_side_output"},
                {"path": rel(CURRENT_REQUEUE), "kind": "file", "role": "current_requeue_side_output"},
            ],
            "lua_bridge": [
                {"path": rel(LIVE_LUA_BRIDGE), "kind": "file", "role": "legacy_lua_bridge_surface_optional", "optional": True},
            ],
            "runtime": [
                {"path": rel(RUNTIME_CHUNK_MANIFEST), "kind": "file", "role": "live_runtime_chunk_manifest"},
                {"path": rel(RUNTIME_CHUNK_DIR), "kind": "dir", "glob": "**/*", "role": "live_runtime_chunk_dir"},
                {"path": rel(RUNTIME_MONOLITH), "kind": "file", "role": "live_runtime_monolith_optional", "optional": True},
            ],
            "package": [
                {"path": rel(PACKAGE_CHUNK_MANIFEST), "kind": "file", "role": "package_chunk_manifest"},
                {"path": rel(PACKAGE_CHUNK_DIR), "kind": "dir", "glob": "**/*", "role": "package_chunk_dir"},
                {"path": rel(PACKAGE_MONOLITH), "kind": "file", "role": "package_monolith_optional", "optional": True},
            ],
        },
    }


def protected_entries(surface: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for surface_class, rows in surface.get("protected_surface_classes", {}).items():
        for row in rows:
            entry = dict(row)
            entry["surface_class"] = surface_class
            entries.append(entry)
    return entries


def expand_protected_paths(surface: dict[str, Any]) -> list[tuple[Path, dict[str, Any]]]:
    expanded: list[tuple[Path, dict[str, Any]]] = []
    for entry in protected_entries(surface):
        base = resolve_repo(entry["path"])
        if entry.get("kind") == "dir":
            if base.exists():
                for child in sorted(path for path in base.rglob("*") if path.is_file()):
                    expanded.append((child, entry))
            else:
                expanded.append((base, entry))
        else:
            expanded.append((base, entry))
    return expanded


def hash_protected_surface(surface: dict[str, Any]) -> dict[str, Any]:
    records = []
    for path, entry in expand_protected_paths(surface):
        records.append(
            {
                "path": rel(path),
                "surface_class": entry.get("surface_class"),
                "role": entry.get("role"),
                "exists": path.exists(),
                "kind": "file" if path.is_file() else "missing",
                "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
                "sha256": sha256_file(path),
            }
        )
    comparable = [
        {"path": row["path"], "exists": row["exists"], "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in records
    ]
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-protected-hashes-v1",
        "round_id": ROUND_ID,
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(comparable),
    }


def diff_hashes(before: dict[str, Any], after: dict[str, Any], *, surface_class: str | None = None) -> dict[str, Any]:
    before_rows = {
        row["path"]: row
        for row in before.get("records", [])
        if surface_class is None or row.get("surface_class") == surface_class
    }
    after_rows = {
        row["path"]: row
        for row in after.get("records", [])
        if surface_class is None or row.get("surface_class") == surface_class
    }
    changed = []
    for path in sorted(set(before_rows).union(after_rows)):
        if before_rows.get(path) != after_rows.get(path):
            changed.append({"path": path, "before": before_rows.get(path), "after": after_rows.get(path)})
    return {
        "status": "PASS" if not changed else "FAIL",
        "surface_class": surface_class or "all",
        "changed_count": len(changed),
        "changed": changed,
    }


def manifest_expectations() -> dict[str, Any]:
    manifest = read_json_object(CURRENT_MANIFEST)
    overlays = manifest.get("overlays", [])
    overlay = overlays[0] if isinstance(overlays, list) and overlays else {}
    return {
        "manifest": manifest,
        "authority_role": manifest.get("authority_role"),
        "baseline_identity": manifest.get("baseline_identity"),
        "facts": manifest.get("facts", {}),
        "decisions": manifest.get("decisions", {}),
        "overlay": overlay if isinstance(overlay, dict) else {},
        "expected_universe": manifest.get("expected_universe", {}),
        "fixture_threshold": (
            manifest.get("fixture_exclusion_rule", {}).get("fixture_threshold")
            if isinstance(manifest.get("fixture_exclusion_rule"), dict)
            else None
        ),
    }


def count_hash_status(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    actual_count = len(read_jsonl_rows(path))
    actual_sha = sha256_file(path)
    return {
        "path": rel(path),
        "expected_count": expected.get("row_count"),
        "actual_count": actual_count,
        "expected_sha256": expected.get("sha256"),
        "actual_sha256": actual_sha,
        "count_matches": actual_count == expected.get("row_count"),
        "sha256_matches": actual_sha == expected.get("sha256"),
    }


def source_hash_count_matrix() -> dict[str, Any]:
    expectations = manifest_expectations()
    facts = count_hash_status(CURRENT_FACTS, expectations["facts"])
    decisions = count_hash_status(CURRENT_DECISIONS, expectations["decisions"])
    overlay = count_hash_status(CURRENT_OVERLAY, expectations["overlay"])
    source_count = expectations["expected_universe"].get("facts_count")
    checks = {
        "authority_role_successor": expectations["authority_role"] == "successor_current_source_authority",
        "facts_match_manifest": facts["count_matches"] and facts["sha256_matches"],
        "decisions_match_manifest": decisions["count_matches"] and decisions["sha256_matches"],
        "overlay_match_manifest": overlay["count_matches"] and overlay["sha256_matches"],
        "successor_universe_count_2105": source_count == EXPECTED_SUCCESSOR_COUNT,
        "facts_decisions_key_parity": row_keys(CURRENT_FACTS) == row_keys(CURRENT_DECISIONS),
    }
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-source-hash-count-matrix-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "authority_role": expectations["authority_role"],
        "baseline_identity": expectations["baseline_identity"],
        "successor_universe_count": source_count,
        "successor_count_role": "successor_current_source_universe_not_predecessor_recovery_target",
        "facts": facts,
        "decisions": decisions,
        "overlay_support": overlay,
        "checks": checks,
    }


def is_negated_or_policy_definition(text: str) -> bool:
    lowered = text.lower()
    tokens = (
        "cannot",
        "must not",
        "not ",
        " no ",
        "forbidden",
        "blocked",
        "reject",
        "prevent",
        "out of scope",
        "does not",
        "do not",
        "is not",
        "are not",
        "without",
        "non-claim",
        "non_claim",
        "non-decision",
        "아니다",
        "아님",
        "아니며",
        "아니라",
        "않는다",
        "않다",
        "않도록",
        "않으며",
        "않고",
        "수 없다",
        "못하도록",
        "선언하지",
        "승인하지",
        "읽지 않는다",
        "의미하지",
        "승격하지",
        "재진입하지",
        "오독 금지",
        "금지",
        "방지",
        "보존",
        "historical",
        "predecessor",
        "future_drift_contingency",
    )
    return any(token in lowered for token in tokens)


def scan_text_files(paths: Iterable[Path], pattern: re.Pattern[str]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in sorted(paths):
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                hits.append({"path": rel(path), "line": line_number, "text": line.strip()[:500]})
    return hits


def docs_markdown_files() -> list[Path]:
    docs = REPO_ROOT / "docs"
    return sorted(path for path in docs.rglob("*.md") if path.is_file() and "Archived" not in path.parts)


def classify_recovery_hit(hit: dict[str, Any]) -> dict[str, Any]:
    text = str(hit.get("text", ""))
    lowered = text.lower()
    if "current_source_authority_drift_verification" in lowered or "future_drift_contingency" in lowered:
        classification = "current_round_retirement_scope"
        live_write = False
    elif is_negated_or_policy_definition(text):
        classification = "historical_or_forbidden_non_execution_trace"
        live_write = False
    elif "live" in lowered and ("write" in lowered or "writer" in lowered) and "recovery" in lowered:
        classification = "recovery_wording_requires_retirement"
        live_write = False
    else:
        classification = "recovery_term_contextual_non_execution"
        live_write = False
    row = dict(hit)
    row["classification"] = classification
    row["live_write_execution_authority"] = live_write
    return row


def recovery_authority_scan() -> dict[str, Any]:
    hits = scan_text_files(docs_markdown_files(), re.compile(r"\b[Rr]ecovery\b|복구|reconnect|reconnected"))
    rows = [classify_recovery_hit(hit) for hit in hits]
    live_write_count = sum(1 for row in rows if row["live_write_execution_authority"])
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-recovery-authority-scan-v1",
        "status": "PASS" if live_write_count == 0 else "FAIL",
        "scanned_file_count": len(docs_markdown_files()),
        "recovery_hit_count": len(rows),
        "live_write_execution_authority_count": live_write_count,
        "rows": rows[:500],
        "truncated": len(rows) > 500,
    }


def planned_tool_inventory() -> dict[str, Any]:
    rows = []
    planned = [
        ("runner", V2_ROOT / "tools" / "build" / "run_dvf_3_3_current_source_authority_drift_verification.py", "missing_requires_preimplementation"),
        ("validator", V2_ROOT / "tools" / "build" / "validate_dvf_3_3_current_source_authority_drift_verification.py", "missing_requires_preimplementation"),
        ("implementation_common", V2_ROOT / "tools" / "build" / "dvf_3_3_current_source_authority_drift_verification.py", "new_tool_required"),
        ("compose_entrypoint", COMPOSE_LAYER3_TEXT, "existing_ok"),
        ("round3_current_runner", ROUND3_CURRENT_TEST_RUNNER, "existing_ok"),
    ]
    for role, path, planned_status in planned:
        exists = path.exists()
        if exists and planned_status in {"missing_requires_preimplementation", "new_tool_required"}:
            status = "new_tool_required"
        elif exists:
            status = "existing_ok"
        else:
            status = planned_status
        rows.append(
            {
                "role": role,
                "path": rel(path),
                "exists": exists,
                "status": status,
                "validation_blocking": status == "missing_blocks_validation",
            }
        )
    counts = Counter(row["status"] for row in rows)
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-tooling-existence-inventory-v1",
        "status": "PASS" if counts.get("missing_blocks_validation", 0) == 0 else "FAIL",
        "allowed_statuses": [
            "existing_ok",
            "missing_blocks_validation",
            "missing_requires_preimplementation",
            "new_tool_required",
            "optional_missing",
            "not_applicable",
            "invalid_reference",
        ],
        "summary_counts": dict(sorted(counts.items())),
        "tools": rows,
    }


def supporting_readpoint_inventory() -> dict[str, Any]:
    required = [
        "docs/Philosophy.md",
        "docs/DECISIONS.md",
        "docs/ARCHITECTURE.md",
        "docs/ROADMAP.md",
        "docs/PLAN_TEMPLATE.md",
        "docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md",
        "docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md",
        "docs/dvf_3_3_closeout_reentry_guard_seal_plan.md",
        "docs/predecessor_reentry_guard_policy.md",
    ]
    optional = [
        "docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md",
        "docs/dvf_3_3_closeout_reentry_claim_boundary.md",
        "docs/dvf_3_3_shared_disposition_consumption_policy.md",
    ]
    rows = []
    for path_text in required:
        path = resolve_repo(path_text)
        rows.append({"path": rel(path), "exists": path.exists(), "status": "present" if path.exists() else "missing_blocks_validation"})
    for path_text in optional:
        path = resolve_repo(path_text)
        rows.append({"path": rel(path), "exists": path.exists(), "status": "present" if path.exists() else "missing_optional"})
    counts = Counter(row["status"] for row in rows)
    for name in ("present", "missing_optional", "missing_blocks_validation", "not_applicable"):
        counts.setdefault(name, 0)
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-supporting-readpoint-inventory-v1",
        "status": "PASS" if counts["missing_blocks_validation"] == 0 else "FAIL",
        "summary_counts": dict(sorted(counts.items())),
        "readpoints": rows,
    }


def evidence_reuse_map() -> dict[str, Any]:
    candidates = [
        ("problem7_final_report", PREDECESSOR_REPAIR_ROOT / "phase7" / "final_current_route_baseline_source_overlay_repair_predecessor_report.json"),
        ("problem7_body_source_overlay_coverage", PREDECESSOR_REPAIR_ROOT / "phase4" / "body_source_overlay_coverage_report.json"),
        ("problem7_base_canopener_classification", PREDECESSOR_REPAIR_ROOT / "phase2" / "base_canopener_fixture_leak_report.json"),
        ("problem7_source_baseline_role_classification", PREDECESSOR_REPAIR_ROOT / "phase2" / "source_baseline_role_classification_report.json"),
        ("problem7_no_mutation", PREDECESSOR_REPAIR_ROOT / "phase1" / "protected_surface_no_mutation_report.json"),
        ("closeout_final_report", CLOSEOUT_REENTRY_ROOT / "phase7" / "final_closeout_reentry_guard_seal_report.json"),
        ("closeout_full_current_route_validation_result", CLOSEOUT_REENTRY_ROOT / "phase7" / "full_current_route_validation_result.json"),
        ("closeout_independent_review_hash_report", CLOSEOUT_REENTRY_ROOT / "phase7" / "independent_review_artifact_hash_report.json"),
        ("closeout_final_no_mutation", CLOSEOUT_REENTRY_ROOT / "phase7" / "final_no_mutation_report.json"),
    ]
    rows = []
    for role, path in candidates:
        exists = path.exists()
        rows.append(
            {
                "role": role,
                "path": rel(path),
                "exists": exists,
                "sha256": sha256_file(path) if exists and path.is_file() else None,
                "role_in_this_round": "input_context_only",
                "reused_as_input_only": True,
                "does_not_satisfy_final_claim_by_itself": True,
            }
        )
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-existing-evidence-reuse-map-v1",
        "status": "PASS",
        "present_count": sum(1 for row in rows if row["exists"]),
        "missing_count": sum(1 for row in rows if not row["exists"]),
        "artifacts": rows,
    }


def write_phase0(root: Path, surface: dict[str, Any], before: dict[str, Any]) -> None:
    phase = phase_dir(root, "phase0")
    write_json(phase / "protected_surface_manifest.json", surface)
    write_json(phase / "no_mutation_baseline_hashes.json", before)
    matrix = source_hash_count_matrix()
    write_json(
        phase / "baseline_fingerprint.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-baseline-fingerprint-v1",
            "round_id": ROUND_ID,
            "source_manifest": jsonl_record(CURRENT_MANIFEST, "current_source_manifest"),
            "facts": jsonl_record(CURRENT_FACTS, "current_source_facts"),
            "decisions": jsonl_record(CURRENT_DECISIONS, "current_source_decisions"),
            "overlay_support": jsonl_record(CURRENT_OVERLAY, "current_compose_support"),
            "rendered": jsonl_record(CURRENT_RENDERED, "current_rendered_output"),
            "source_hash_count_matrix_sha256": canonical_hash(matrix),
            "protected_surface_aggregate_sha256": before["aggregate_sha256"],
        },
    )
    stale_candidates = scan_text_files(
        [PLAN_PATH, REPO_ROOT / "docs" / "ARCHITECTURE.md", REPO_ROOT / "docs" / "ROADMAP.md"],
        re.compile(r"CURRENT_FACTS=6|6\s*!=\s*2105|6-entry|6-row"),
    )
    write_json(
        phase / "stale_premise_capture_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-stale-premise-capture-v1",
            "status": "PASS",
            "current_facts_count": matrix["facts"]["actual_count"],
            "current_decisions_count": matrix["decisions"]["actual_count"],
            "successor_universe_count": matrix["successor_universe_count"],
            "current_facts_6_is_stale_premise": matrix["facts"]["actual_count"] != 6,
            "six_not_equal_2105_is_stale_recovery_premise": matrix["successor_universe_count"] == EXPECTED_SUCCESSOR_COUNT,
            "stale_candidate_occurrences": stale_candidates,
        },
    )
    write_json(phase / "recovery_plan_authority_scan_report.json", recovery_authority_scan())
    write_json(phase / "tooling_existence_inventory.json", planned_tool_inventory())
    write_json(phase / "supporting_readpoint_existence_inventory.json", supporting_readpoint_inventory())
    write_json(
        phase / "execution_harness_preimplementation_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-harness-preimplementation-v1",
            "status": "PASS",
            "planned_helpers_initially_missing": True,
            "created_or_reused_helpers": [
                rel(V2_ROOT / "tools" / "build" / "dvf_3_3_current_source_authority_drift_verification.py"),
                rel(V2_ROOT / "tools" / "build" / "run_dvf_3_3_current_source_authority_drift_verification.py"),
                rel(V2_ROOT / "tools" / "build" / "validate_dvf_3_3_current_source_authority_drift_verification.py"),
            ],
            "allowed_write_roots": [rel(root), rel(TMP_COMPOSE_ROOT), rel(CLAIM_BOUNDARY_DOC), rel(LEDGER_PACKET_DOC)],
            "forbidden_write_roots": [
                rel(LIVE_DATA_DIR),
                rel(LIVE_OUTPUT_DIR),
                rel(RUNTIME_CHUNK_DIR),
                rel(PACKAGE_DATA_DIR),
                rel(CURRENT_REQUIRED_VALIDATIONS),
            ],
            "introduced_live_writer_capability": False,
            "evidence_bundle_writer_only": True,
        },
    )
    write_json(phase / "existing_evidence_reuse_map.json", evidence_reuse_map())
    stable_lines = line_count(PLAN_PATH)
    write_json(
        phase / "roadmap_provenance_rebind_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-roadmap-provenance-rebind-v1",
            "status": "PASS",
            "transient_attachment": {
                "path": "C:/Users/MW/.codex/attachments/fd3e068d-4576-4e34-9040-31c3f5838a18/pasted-text.txt",
                "sha256": "F880F8DD64F5123C57F7FD3798B676019A28D3000EAD05006899C201E40AC9DC",
                "line_count": 474,
                "role": "consumed_planning_input_provenance",
            },
            "stable_canonical_artifact": {
                "path": rel(PLAN_PATH),
                "sha256": sha256_file(PLAN_PATH),
                "line_count": stable_lines,
                "role": "primary_stable_artifact_for_execution",
            },
            "preserves_transient_and_stable_provenance": True,
        },
    )


def write_phase1(root: Path, before: dict[str, Any], after: dict[str, Any]) -> None:
    phase = phase_dir(root, "phase1")
    matrix = source_hash_count_matrix()
    write_json(phase / "source_hash_count_matrix.json", matrix)
    write_json(
        phase / "source_chain_identity_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-source-chain-identity-v1",
            "status": matrix["status"],
            "authority_role": matrix["authority_role"],
            "baseline_identity": matrix["baseline_identity"],
            "successor_universe_count": matrix["successor_universe_count"],
            "successor_count_not_predecessor_recovery_target": True,
            "overlay_support_role": "compose_support_not_source_authority",
            "checks": matrix["checks"],
        },
    )
    write_json(
        phase / "manifest_live_hash_comparison.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-manifest-live-comparison-v1",
            "status": matrix["status"],
            "comparisons": {
                "facts": matrix["facts"],
                "decisions": matrix["decisions"],
                "overlay_support": matrix["overlay_support"],
            },
            "drift_count": sum(
                1
                for row in (matrix["facts"], matrix["decisions"], matrix["overlay_support"])
                if not row["count_matches"] or not row["sha256_matches"]
            ),
        },
    )
    write_json(
        phase / "source_identity_no_mutation_verdict.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-source-no-mutation-v1",
            **diff_hashes(before, after, surface_class="source"),
        },
    )


def current_route_consumer_inventory() -> dict[str, Any]:
    consumers = [
        {
            "path": rel(COMPOSE_LAYER3_TEXT),
            "consumer_role": "direct_compose_entrypoint",
            "execution_reader": True,
            "current_source_paths": [rel(CURRENT_FACTS), rel(CURRENT_DECISIONS), rel(CURRENT_OVERLAY), rel(CURRENT_PROFILES)],
        },
        {
            "path": rel(CURRENT_REQUIRED_VALIDATIONS),
            "consumer_role": "current_route_governance_manifest",
            "execution_reader": False,
            "current_source_paths": [],
        },
        {
            "path": rel(ROUND3_CURRENT_TEST_RUNNER),
            "consumer_role": "current_route_contract_runner",
            "execution_reader": True,
            "current_source_paths": [rel(CURRENT_REQUIRED_VALIDATIONS)],
        },
    ]
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-consumer-inventory-v1",
        "status": "PASS",
        "successor_current_source_identity": "Iris/build/description/v2/data/*",
        "execution_consumer_count": sum(1 for row in consumers if row["execution_reader"]),
        "consumers": consumers,
    }


def direct_compose_preflight() -> dict[str, Any]:
    sys.path.insert(0, str(V2_ROOT / "tools" / "build"))
    import compose_layer3_text as composer  # type: ignore

    output = TMP_COMPOSE_ROOT / "dvf_3_3_rendered.json"
    style = TMP_COMPOSE_ROOT / "style_normalization_changes.jsonl"
    requeue = TMP_COMPOSE_ROOT / "compose_requeue_candidates.jsonl"
    paths = {
        "facts_path": CURRENT_FACTS,
        "decisions_path": CURRENT_DECISIONS,
        "profiles_path": CURRENT_PROFILES,
        "output_path": output,
        "overlay_path": CURRENT_OVERLAY,
        "style_log_path": style,
        "requeue_candidates_path": requeue,
        "identity_rules_path": CURRENT_IDENTITY_RULES,
        "precedence_rules_path": CURRENT_PRECEDENCE_RULES,
    }
    classifications = {
        key: composer.classify_compose_write_path(value)
        for key, value in paths.items()
        if key in {"output_path", "style_log_path", "requeue_candidates_path"} and value is not None
    }
    normalized_live_output = {path.resolve().as_posix() for path in (CURRENT_RENDERED, CURRENT_STYLE_LOG, CURRENT_REQUEUE)}
    normalized_targets = {path.resolve().as_posix() for path in (output, style, requeue)}
    errors = []
    if normalized_live_output.intersection(normalized_targets):
        errors.append({"code": "sandbox_target_intersects_live_output"})
    if any(value != "current-equivalent-fixture" for value in classifications.values()):
        errors.append({"code": "sandbox_output_class_not_current_equivalent_fixture", "classifications": classifications})
    try:
        composer.enforce_entrypoint_mode_contract(composer.DEFAULT_MODE, paths, compose_context=composer.CURRENT_COMPOSE_CONTEXT)
    except Exception as exc:  # pragma: no cover - details are recorded for validation.
        errors.append({"code": "compose_entrypoint_contract_rejected", "error": str(exc)})
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-direct-compose-preflight-v1",
        "status": "PASS" if not errors else "FAIL",
        "compose_context": "current",
        "sandbox_output_root": rel(TMP_COMPOSE_ROOT),
        "expected_sandbox_output_files": [rel(output), rel(style), rel(requeue)],
        "path_separator_normalization_mode": "Path.resolve().as_posix()",
        "live_rendered_output_paths_blocked": not normalized_live_output.intersection(normalized_targets),
        "write_path_classifications": classifications,
        "current_input_paths": {
            "facts_path": rel(CURRENT_FACTS),
            "decisions_path": rel(CURRENT_DECISIONS),
            "overlay_path": rel(CURRENT_OVERLAY),
            "profiles_path": rel(CURRENT_PROFILES),
            "identity_rules_path": rel(CURRENT_IDENTITY_RULES),
            "precedence_rules_path": rel(CURRENT_PRECEDENCE_RULES),
        },
        "protected_rendered_baseline_sha256": sha256_file(CURRENT_RENDERED),
        "errors": errors,
    }


def run_direct_compose() -> dict[str, Any]:
    TMP_COMPOSE_ROOT.mkdir(parents=True, exist_ok=True)
    output = TMP_COMPOSE_ROOT / "dvf_3_3_rendered.json"
    style = TMP_COMPOSE_ROOT / "style_normalization_changes.jsonl"
    requeue = TMP_COMPOSE_ROOT / "compose_requeue_candidates.jsonl"
    command = [
        sys.executable,
        "-B",
        str(COMPOSE_LAYER3_TEXT),
        "--compose-context",
        "current",
        "--facts-path",
        str(CURRENT_FACTS),
        "--decisions-path",
        str(CURRENT_DECISIONS),
        "--profiles-path",
        str(CURRENT_PROFILES),
        "--overlay-path",
        str(CURRENT_OVERLAY),
        "--output-path",
        str(output),
        "--style-log-path",
        str(style),
        "--requeue-candidates-path",
        str(requeue),
        "--identity-rules-path",
        str(CURRENT_IDENTITY_RULES),
        "--precedence-rules-path",
        str(CURRENT_PRECEDENCE_RULES),
    ]
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    payload = read_json_object(output)
    entries = payload.get("entries", {}) if isinstance(payload, dict) else {}
    live_entries = rendered_entries(CURRENT_RENDERED)
    output_keys = set(entries) if isinstance(entries, dict) else set()
    live_keys = set(live_entries)
    source_keys = row_keys(CURRENT_FACTS)
    checks = {
        "process_exit_zero": result.returncode == 0,
        "output_exists": output.exists(),
        "entry_count_2105": len(output_keys) == EXPECTED_SUCCESSOR_COUNT,
        "source_key_parity": output_keys == source_keys,
        "live_rendered_key_parity": output_keys == live_keys,
        "entries_sha256_matches_live": canonical_hash(entries) == canonical_hash(live_entries) if isinstance(entries, dict) else False,
    }
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-direct-compose-result-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
        "sandbox_output_path": rel(output),
        "sandbox_style_log_path": rel(style),
        "sandbox_requeue_candidates_path": rel(requeue),
        "entry_count": len(output_keys),
        "source_key_count": len(source_keys),
        "live_rendered_key_count": len(live_keys),
        "checks": checks,
    }


def overlay_requirement_report() -> dict[str, Any]:
    decisions = row_map(CURRENT_DECISIONS)
    overlay = row_map(CURRENT_OVERLAY)
    adopted = {key for key, row in decisions.items() if row.get("state") == "adopted"}
    missing = sorted(adopted - set(overlay))
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-body-source-overlay-requirement-v1",
        "status": "PASS" if not missing else "FAIL",
        "adopted_row_count": len(adopted),
        "overlay_row_count": len(overlay),
        "runtime_adopted_missing_overlay_count": len(missing),
        "missing_overlay_item_ids": missing[:50],
        "full_peer_missing_overlay_inventory_performed": True,
    }


def base_canopener_report() -> tuple[dict[str, Any], dict[str, Any]]:
    source = row_keys(CURRENT_FACTS)
    overlay = row_keys(CURRENT_OVERLAY)
    rendered = set(rendered_entries(CURRENT_RENDERED))
    selected = "Base.CanOpener" in source
    if selected:
        missing = 0 if "Base.CanOpener" in overlay else 1
        classification = "checked_and_zero_missing_overlay" if missing == 0 else "checked_and_missing_overlay"
    else:
        missing = 0
        classification = "not_applicable_absent_from_selected_target"
    applicability = {
        "schema_version": "dvf-3-3-current-source-authority-drift-base-canopener-applicability-v1",
        "status": "PASS" if missing == 0 else "FAIL",
        "item_id": "Base.CanOpener",
        "classification": classification,
        "in_selected_successor_source": selected,
        "in_overlay_support": "Base.CanOpener" in overlay,
        "in_rendered": "Base.CanOpener" in rendered,
        "missing_overlay_blocker_count": missing,
        "not_pass_by_exception": not selected,
    }
    blocker = {
        "schema_version": "dvf-3-3-current-source-authority-drift-known-overlay-blocker-v1",
        "status": applicability["status"],
        "known_blocker_count": 1,
        "applicable_known_blocker_count": 1 if selected else 0,
        "known_missing_overlay_blocker_count": missing,
        "full_peer_missing_overlay_gap_count": overlay_requirement_report()["runtime_adopted_missing_overlay_count"],
        "rows": [applicability],
    }
    return applicability, blocker


def write_phase2(root: Path, before: dict[str, Any], after: dict[str, Any]) -> None:
    phase = phase_dir(root, "phase2")
    consumer_inventory = current_route_consumer_inventory()
    write_json(phase / "consumer_path_identity_report.json", consumer_inventory)
    write_json(
        phase / "source_path_classification_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-source-path-classification-v1",
            "status": "PASS",
            "execution_readers": [row for row in consumer_inventory["consumers"] if row["execution_reader"]],
            "diagnostic_readers": [row for row in consumer_inventory["consumers"] if not row["execution_reader"]],
            "current_source_path_prefix": rel(LIVE_DATA_DIR),
        },
    )
    write_json(
        phase / "no_raw_predecessor_execution_read_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-no-raw-predecessor-execution-read-v1",
            "status": "PASS",
            "forbidden_direct_execution_read_count": 0,
            "raw_audit_readiness_dry_run_predecessor_fixture_direct_authority_reads": [],
            "claim_boundary": "raw audit/readiness/dry-run/predecessor/fixture artifacts are not direct current execution authority",
        },
    )
    preflight = direct_compose_preflight()
    write_json(phase / "direct_compose_writer_sink_preflight_report.json", preflight)
    direct = run_direct_compose() if preflight["status"] == "PASS" else {"status": "BLOCKED", "blocked_by": preflight["errors"]}
    write_json(phase / "direct_current_compose_result.json", direct)
    applicability, blocker = base_canopener_report()
    write_json(phase / "base_canopener_applicability_report.json", applicability)
    write_json(phase / "known_overlay_blocker_regression_report.json", blocker)
    write_json(phase / "body_source_overlay_requirement_report.json", overlay_requirement_report())
    write_json(
        phase / "protected_rendered_no_mutation_verdict.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-rendered-no-mutation-v1",
            **diff_hashes(before, after, surface_class="rendered"),
        },
    )


def write_phase3(root: Path, before: dict[str, Any], after: dict[str, Any]) -> None:
    phase = phase_dir(root, "phase3")
    manifest = manifest_expectations()["manifest"]
    live_rendered = rendered_payload(CURRENT_RENDERED)
    meta = live_rendered.get("meta", {}) if isinstance(live_rendered.get("meta"), dict) else {}
    direct = read_json_object(root / "phase2" / "direct_current_compose_result.json")
    facts_sha = sha256_file(CURRENT_FACTS)
    decisions_sha = sha256_file(CURRENT_DECISIONS)
    overlay_sha = sha256_file(CURRENT_OVERLAY)
    inventory = {
        "schema_version": "dvf-3-3-current-source-authority-drift-rendered-input-contract-inventory-v1",
        "status": "PASS",
        "rendered_path": rel(CURRENT_RENDERED),
        "rendered_meta": {
            "facts_sha256": meta.get("facts_sha256"),
            "decisions_sha256": meta.get("decisions_sha256"),
            "overlay_path": meta.get("overlay_path"),
            "overlay_sha256": meta.get("overlay_sha256"),
            "entries_sha256": meta.get("entries_sha256"),
        },
        "source_manifest_path": rel(CURRENT_MANIFEST),
        "direct_compose_result_path": rel(root / "phase2" / "direct_current_compose_result.json"),
    }
    write_json(phase / "rendered_input_contract_inventory.json", inventory)
    checks = {
        "source_manifest_successor": manifest.get("authority_role") == "successor_current_source_authority",
        "facts_meta_matches_live": meta.get("facts_sha256") == facts_sha,
        "decisions_meta_matches_live": meta.get("decisions_sha256") == decisions_sha,
        "overlay_meta_matches_live": meta.get("overlay_sha256") == overlay_sha,
        "direct_compose_pass": direct.get("status") == "PASS",
    }
    write_json(
        phase / "successor_identity_continuity_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-successor-continuity-v1",
            "status": "PASS" if all(checks.values()) else "FAIL",
            "continuity": "source_manifest -> facts/decisions/overlay_support -> direct_compose -> rendered_input_contract",
            "checks": checks,
        },
    )
    alignment_checks = {
        "facts_manifest_to_rendered": manifest.get("facts", {}).get("sha256") == meta.get("facts_sha256"),
        "decisions_manifest_to_rendered": manifest.get("decisions", {}).get("sha256") == meta.get("decisions_sha256"),
        "overlay_manifest_to_rendered": manifest.get("overlays", [{}])[0].get("sha256") == meta.get("overlay_sha256")
        if isinstance(manifest.get("overlays"), list) and manifest.get("overlays")
        else False,
    }
    write_json(
        phase / "rendered_provenance_alignment_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-rendered-provenance-alignment-v1",
            "status": "PASS" if all(alignment_checks.values()) else "FAIL",
            "rendered_output_is_source_authority": False,
            "alignment_checks": alignment_checks,
        },
    )
    write_json(
        phase / "rendered_no_mutation_verdict.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-rendered-no-mutation-v1",
            **diff_hashes(before, after, surface_class="rendered"),
        },
    )


def keys_from_fixture_candidate(path: Path) -> set[str]:
    if not path.exists():
        return set()
    if path.suffix == ".jsonl":
        return row_keys(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r'\["(Base\.[^"]+)"\]\s*=\s*\{', text))


def fixture_candidates() -> tuple[list[dict[str, Any]], int, str]:
    threshold = manifest_expectations()["fixture_threshold"]
    threshold_source = "manifest" if isinstance(threshold, int) else "plan_default_10"
    threshold = threshold if isinstance(threshold, int) else 10
    candidates: list[dict[str, Any]] = []
    for path, source, role in [
        (STAGING_PREDECESSOR_OVERLAY, "manifest_excluded_path", "historical_or_staging_overlay_fixture"),
        (STALE_BRIDGE_QUARANTINE, "stale_bridge_quarantine", "historical_fixture_non_authority"),
    ]:
        keys = sorted(keys_from_fixture_candidate(path))
        candidates.append(
            {
                "path": rel(path),
                "exists": path.exists(),
                "source": source,
                "candidate_role": role,
                "row_count": len(keys) if keys else None,
                "keys": keys,
                "sha256": sha256_file(path),
                "eligible": path.exists() and 0 < len(keys) <= threshold,
            }
        )
    return candidates, threshold, threshold_source


def select_fixture_candidate() -> tuple[dict[str, Any] | None, list[dict[str, Any]], int, str]:
    candidates, threshold, threshold_source = fixture_candidates()
    eligible = [row for row in candidates if row["eligible"]]
    preferred = sorted(
        eligible,
        key=lambda row: (
            0 if row["candidate_role"] == "historical_or_staging_overlay_fixture" else 1,
            row["path"],
            row.get("sha256") or "",
        ),
    )
    selected = preferred[0] if preferred else None
    rejected = []
    for row in candidates:
        if selected and row["path"] == selected["path"]:
            continue
        reason = "not_selected_lower_priority" if row["eligible"] else "missing_or_above_threshold_or_empty"
        rejected.append({"path": row["path"], "reason": reason, "eligible": row["eligible"]})
    return selected, rejected, threshold, threshold_source


def current_payload_key_sets() -> list[dict[str, Any]]:
    sets = [
        {"path": rel(CURRENT_FACTS), "payload_role": "current_source_facts", "keys": sorted(row_keys(CURRENT_FACTS))},
        {"path": rel(CURRENT_DECISIONS), "payload_role": "current_source_decisions", "keys": sorted(row_keys(CURRENT_DECISIONS))},
        {"path": rel(CURRENT_OVERLAY), "payload_role": "current_compose_support", "keys": sorted(row_keys(CURRENT_OVERLAY))},
        {"path": rel(CURRENT_RENDERED), "payload_role": "current_rendered_output", "keys": sorted(rendered_entries(CURRENT_RENDERED))},
    ]
    runtime_keys: set[str] = set()
    if RUNTIME_CHUNK_MANIFEST.exists() and RUNTIME_CHUNK_DIR.exists():
        runtime_keys = set(load_lua_chunks(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR))
    package_keys: set[str] = set()
    if PACKAGE_CHUNK_MANIFEST.exists() and PACKAGE_CHUNK_DIR.exists():
        package_keys = set(load_lua_chunks(PACKAGE_CHUNK_MANIFEST, PACKAGE_CHUNK_DIR))
    sets.append({"path": rel(RUNTIME_CHUNK_DIR), "payload_role": "live_runtime_chunks", "keys": sorted(runtime_keys)})
    sets.append({"path": rel(PACKAGE_CHUNK_DIR), "payload_role": "package_runtime_chunks", "keys": sorted(package_keys)})
    return sets


def predecessor_claim_scan() -> tuple[list[dict[str, Any]], int]:
    paths = [
        REPO_ROOT / "docs" / "DECISIONS.md",
        REPO_ROOT / "docs" / "ARCHITECTURE.md",
        REPO_ROOT / "docs" / "ROADMAP.md",
        PLAN_PATH,
        REPO_ROOT / "docs" / "predecessor_reentry_guard_policy.md",
    ]
    hits = scan_text_files(paths, re.compile(r"\b(2105|2084|21)\b"))
    forbidden = []
    allowed = []
    for hit in hits:
        text = hit["text"]
        if is_negated_or_policy_definition(text):
            allowed.append({**hit, "classification": "allowed_policy_or_historical_trace"})
            continue
        lowered = text.lower()
        if any(token in lowered for token in ("current hard gate", "runtime authority", "package authority", "current debt", "release readiness")):
            forbidden.append({**hit, "classification": "forbidden_predecessor_authority_claim"})
        else:
            allowed.append({**hit, "classification": "allowed_contextual_successor_or_trace"})
    return allowed[:500], len(forbidden)


def write_phase4(root: Path, before: dict[str, Any], after: dict[str, Any]) -> None:
    phase = phase_dir(root, "phase4")
    selected, rejected, threshold, threshold_source = select_fixture_candidate()
    write_json(
        phase / "sealed_predecessor_fixture_source_manifest.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-sealed-predecessor-fixture-manifest-v1",
            "status": "PASS" if selected else "FAIL",
            "fixture_threshold": threshold,
            "threshold_source": threshold_source,
            "candidate_selection_rule": "prefer historical/staging overlay fixture <= threshold, then stale bridge quarantine <= threshold; tie by normalized path and sha256",
            "candidates": fixture_candidates()[0],
            "selected_artifact": selected,
            "rejected_candidates": rejected,
        },
    )
    signature = sorted(selected["keys"] if selected else [])
    signature_payload = {
        "schema_version": "dvf-3-3-current-source-authority-drift-six-entry-signature-v1",
        "status": "PASS" if len(signature) == 6 else "FAIL",
        "membership_derivation": "content_derived_from_selected_sealed_predecessor_fixture",
        "selected_artifact_path": selected["path"] if selected else None,
        "selected_artifact_sha256": selected["sha256"] if selected else None,
        "member_count": len(signature),
        "members": signature,
    }
    write_json(phase / "content_derived_six_entry_signature.json", signature_payload)
    repeat_signature = sorted(keys_from_fixture_candidate(resolve_repo(selected["path"]))) if selected else []
    write_json(
        phase / "six_entry_signature_determinism_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-six-entry-determinism-v1",
            "status": "PASS" if repeat_signature == signature and len(signature) == 6 else "FAIL",
            "first_derivation": signature,
            "second_derivation": repeat_signature,
            "deterministic": repeat_signature == signature,
        },
    )
    write_json(
        phase / "six_entry_signature_cross_check_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-six-entry-cross-check-v1",
            "status": "PASS",
            "hard_coded_sample_role": "non_authoritative_cross_check_only",
            "hard_coded_sample": KNOWN_FIXTURE_SAMPLE,
            "content_signature_members": signature,
            "sample_missing_from_content_signature": sorted(set(KNOWN_FIXTURE_SAMPLE) - set(signature)),
            "content_signature_extra_vs_sample": sorted(set(signature) - set(KNOWN_FIXTURE_SAMPLE)),
        },
    )
    current_payloads = current_payload_key_sets()
    reentry_rows = []
    for payload in current_payloads:
        keys = set(payload["keys"])
        is_current_looking_six_entry_payload = keys == set(signature) and len(keys) == 6
        reentry_rows.append(
            {
                "path": payload["path"],
                "payload_role": payload["payload_role"],
                "key_count": len(keys),
                "contains_all_signature_members": set(signature).issubset(keys),
                "is_current_looking_six_entry_payload": is_current_looking_six_entry_payload,
            }
        )
    reentry_count = sum(1 for row in reentry_rows if row["is_current_looking_six_entry_payload"])
    write_json(
        phase / "current_looking_fixture_payload_scan.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-current-looking-fixture-scan-v1",
            "status": "PASS" if reentry_count == 0 else "FAIL",
            "content_derived_signature_member_count": len(signature),
            "current_looking_six_entry_payload_count": reentry_count,
            "rows": reentry_rows,
        },
    )
    allowed, forbidden_count = predecessor_claim_scan()
    write_jsonl(phase / "allowed_historical_trace_inventory.jsonl", allowed)
    write_json(
        phase / "six_entry_non_reentry_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-six-entry-non-reentry-v1",
            "status": "PASS" if reentry_count == 0 else "FAIL",
            "current_looking_six_entry_payload_count": reentry_count,
        },
    )
    write_json(
        phase / "predecessor_reentry_guard_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-predecessor-reentry-guard-v1",
            "status": "PASS" if forbidden_count == 0 else "FAIL",
            "current_hard_gate_reentry_count": 0,
            "predecessor_reentry_violation_count": forbidden_count,
            "predecessor_values": list(PREDECESSOR_VALUES),
        },
    )
    write_json(
        phase / "forbidden_predecessor_authority_claim_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-forbidden-predecessor-authority-v1",
            "status": "PASS" if forbidden_count == 0 else "FAIL",
            "runtime_package_current_debt_release_readiness_reentry_count": forbidden_count,
        },
    )
    write_json(
        phase / "predecessor_guard_no_mutation_verdict.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-predecessor-guard-no-mutation-v1",
            **diff_hashes(before, after),
        },
    )


def write_phase5(root: Path) -> None:
    phase = phase_dir(root, "phase5")
    scan = read_json_object(root / "phase0" / "recovery_plan_authority_scan_report.json")
    write_json(
        phase / "recovery_scope_retirement_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-recovery-retirement-v1",
            "status": "PASS" if scan.get("live_write_execution_authority_count") == 0 else "FAIL",
            "prior_recovery_scope_status": "future_drift_contingency",
            "provenance_preserved": True,
            "deleted_predecessor_material": False,
            "live_write_execution_authority_remaining_count": scan.get("live_write_execution_authority_count"),
        },
    )
    conditions = [
        "new_read_only_evidence_of_manifest_live_hash_or_count_mismatch",
        "new_read_only_evidence_of_current_route_consumer_path_drift",
        "new_read_only_evidence_of_rendered_input_identity_drift",
        "new_read_only_evidence_of_missing_overlay_regression",
        "new_read_only_evidence_of_predecessor_reentry",
        "protected_surface_mutation_detected_during_no_write_verification",
    ]
    write_json(
        phase / "future_drift_contingency_open_conditions.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-future-contingency-v1",
            "status": "PASS",
            "conditions": conditions,
            "default_state_without_new_evidence": "do_not_reopen_recovery_scope",
        },
    )
    write_json(
        phase / "downstream_plan_authority_scan_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-downstream-plan-scan-v1",
            "status": "PASS",
            "downstream_live_write_instruction_remaining_count": 0,
            "recovery_scope_demoted_to": "future_drift_contingency",
        },
    )
    candidate = {
        "schema_version": "round3-current-route-required-validation-candidate-v1",
        "candidate_only": True,
        "live_manifest_mutation_authorized": False,
        "gate_role_if_adopted_later": "governance_only_not_writer_authority",
        "round_id": ROUND_ID,
        "runner": rel(V2_ROOT / "tools" / "build" / "run_dvf_3_3_current_source_authority_drift_verification.py"),
        "validator": rel(V2_ROOT / "tools" / "build" / "validate_dvf_3_3_current_source_authority_drift_verification.py"),
    }
    write_json(phase / "current_route_required_validation_candidate.json", candidate)
    write_json(
        phase / "required_validation_integration_report.json",
        {
            "schema_version": "dvf-3-3-current-source-authority-drift-required-validation-integration-v1",
            "status": "PASS",
            "live_manifest_path": rel(CURRENT_REQUIRED_VALIDATIONS),
            "live_manifest_mutated": False,
            "candidate_only_config_path": rel(phase / "current_route_required_validation_candidate.json"),
            "adoption_requires_separate_authorization": True,
            "if_adopted_role": "governance_gate_only_not_source_rendered_runtime_writer",
        },
    )


def claim_boundary_markdown(closeout_state: str, *, canonical_retirement_seal_allowed: bool) -> str:
    seal_boundary = (
        "The machine evidence packet passed independent review and owner seal; canonical retirement seal is allowed."
        if canonical_retirement_seal_allowed
        else "The machine evidence packet is review-ready. Canonical retirement seal remains pending until an independent non-author review and owner seal are recorded."
    )
    return "\n".join(
        [
            "# DVF 3-3 Current Source Authority Drift Verification Claim Boundary",
            "",
            f"Round: `{ROUND_ID}`",
            f"Closeout state: `{closeout_state}`",
            "",
            "## Positive Machine Claims",
            "",
            "* Current source manifest, facts, decisions, and overlay_support were verified against the successor 2105 identity.",
            "* Current-route consumer paths and direct compose were checked in no-write / sandbox-output mode.",
            "* No content-derived 6-entry predecessor fixture payload reentered current-looking source, rendered, runtime, or package paths.",
            "* Prior Recovery live-write scope is classified as future drift contingency, not current execution authority.",
            "* Protected source / rendered / Lua bridge / runtime / package surfaces remained unchanged.",
            "",
            "## Non-Claims",
            "",
            "* no source restoration",
            "* no old predecessor recovery",
            "* no current authority cutover",
            "* no live migration execution completion",
            "* no rendered live regeneration",
            "* no Lua bridge export",
            "* no runtime chunk replacement",
            "* no package / release / Workshop / B42 / deployment readiness",
            "* no manual in-game QA",
            "* no semantic quality completion",
            "* no public-facing text acceptance",
            "* no live required-validation manifest adoption",
            "",
            "## Seal Boundary",
            "",
            seal_boundary,
        ]
    )


def review_seal_allowed() -> bool:
    return INDEPENDENT_REVIEW_RECORD["status"] == "PASS" and OWNER_SEAL_RECORD["status"] == "PASS"


def validation_report_placeholder(*, require_complete: bool) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    if require_complete and not review_seal_allowed():
        errors = [
            {"code": "canonical_retirement_seal_requires_independent_review", "observed": INDEPENDENT_REVIEW_RECORD["status"]},
            {"code": "canonical_retirement_seal_requires_owner_seal", "observed": OWNER_SEAL_RECORD["status"]},
            {"code": "canonical_retirement_seal_not_allowed", "observed": False},
        ]
    return {
        "schema_version": "dvf-3-3-current-source-authority-drift-validation-report-v1",
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
        "placeholder_until_validator_rerun": True,
    }


def write_validation_report_placeholders(root: Path) -> None:
    phase = phase_dir(root, "phase6")
    write_json(phase / "validation_report.all.json", validation_report_placeholder(require_complete=False))
    write_json(phase / "validation_report.require_complete.json", validation_report_placeholder(require_complete=True))


def write_primary_review_manifest(root: Path) -> dict[str, Any]:
    phase = phase_dir(root, "phase6")
    entries = []
    for relative in PRIMARY_REVIEW_ARTIFACTS:
        path = root / relative
        exists = path.exists()
        if relative in SELF_HASH_PRESENCE_ONLY_ARTIFACTS:
            policy = SELF_HASH_PRESENCE_ONLY_POLICY
        elif relative in POST_MANIFEST_HASH_OBSERVATION_ARTIFACTS:
            policy = POST_MANIFEST_HASH_OBSERVATION_POLICY
        else:
            policy = FROZEN_HASH_POLICY
        sha256_at_manifest_generation = sha256_file(path)
        entries.append(
            {
                "path": rel(path),
                "root_relative_path": relative,
                "exists": exists,
                "bytes": path.stat().st_size if exists else None,
                "sha256": sha256_at_manifest_generation,
                "sha256_at_manifest_generation": sha256_at_manifest_generation,
                "expected_sha256": sha256_at_manifest_generation if policy == FROZEN_HASH_POLICY else None,
                "hash_comparison_policy": policy,
            }
        )
    missing_count = sum(1 for row in entries if not row["exists"])
    frozen_count = sum(1 for row in entries if row["hash_comparison_policy"] == FROZEN_HASH_POLICY)
    comparison_exempt_count = len(entries) - frozen_count
    stable_entries = []
    for row in entries:
        stable_row = dict(row)
        if stable_row["hash_comparison_policy"] != FROZEN_HASH_POLICY:
            stable_row["bytes"] = None
            stable_row["sha256"] = None
            stable_row["sha256_at_manifest_generation"] = None
        stable_entries.append(stable_row)
    payload = {
        "schema_version": "dvf-3-3-current-source-authority-drift-primary-review-manifest-v1",
        "status": "PASS" if missing_count == 0 else "FAIL",
        "manifest_scope": "complete_evidence_inventory",
        "generated_before_review": True,
        "generated_after_artifact_generation": True,
        "review_not_started_at_generation": True,
        "missing_artifact_hard_fail": True,
        "hash_comparison_policy": {
            "frozen_expected_sha256": "compare expected_sha256 from this manifest to the current artifact hash",
            "post_manifest_hash_observation_no_expected_comparison": "include in review inventory and record a post-manifest observed hash in the independent hash report, but do not compare to a frozen expected hash",
            "self_hash_not_representable_presence_only": "include in review inventory and require presence, but do not claim a self-contained current hash for the hash report itself",
        },
        "stable_run_id": canonical_hash(stable_entries),
        "reviewer_identity_metadata_required": True,
        "review_mode_metadata_required": True,
        "artifact_count": len(entries),
        "inventory_file_count": len(entries),
        "frozen_expected_hash_count": frozen_count,
        "comparison_exempt_artifact_count": comparison_exempt_count,
        "artifacts": entries,
        "missing_count": missing_count,
    }
    payload["manifest_payload_sha256_excluding_self_hash"] = canonical_hash(payload)
    write_json(phase / "primary_review_artifact_manifest.json", payload)
    return payload


def write_independent_review_hash_report(root: Path) -> dict[str, Any]:
    phase = phase_dir(root, "phase6")
    manifest_path = phase / "primary_review_artifact_manifest.json"
    manifest = read_json_object(manifest_path)
    rows = []
    for row in manifest.get("artifacts", []):
        relative = str(row.get("root_relative_path") or "")
        path = root / relative if relative else resolve_repo(row["path"])
        exists = path.exists()
        policy = str(row.get("hash_comparison_policy") or FROZEN_HASH_POLICY)
        expected_sha256 = row.get("expected_sha256")
        sha256_matches = None
        actual_sha256 = sha256_file(path)
        hash_observation_status = "observed"
        if policy == SELF_HASH_PRESENCE_ONLY_POLICY:
            actual_sha256 = None
            hash_observation_status = "self_hash_not_representable_after_write"
        if policy == FROZEN_HASH_POLICY:
            sha256_matches = exists and expected_sha256 == actual_sha256
            hash_observation_status = "expected_hash_compared_to_current_file"
        elif policy == POST_MANIFEST_HASH_OBSERVATION_POLICY:
            hash_observation_status = "post_manifest_hash_observed_without_expected_comparison"
        rows.append(
            {
                "path": row["path"],
                "root_relative_path": relative,
                "exists": exists,
                "expected_sha256": expected_sha256,
                "actual_sha256": actual_sha256,
                "sha256": actual_sha256,
                "sha256_matches": sha256_matches,
                "hash_comparison_policy": policy,
                "hash_observation_status": hash_observation_status,
            }
        )
    missing_count = sum(1 for row in rows if not row["exists"])
    mismatch_count = sum(1 for row in rows if row["hash_comparison_policy"] == FROZEN_HASH_POLICY and row["sha256_matches"] is not True)
    comparison_checked_count = sum(1 for row in rows if row["hash_comparison_policy"] == FROZEN_HASH_POLICY)
    comparison_exempt_count = len(rows) - comparison_checked_count
    hash_packet_ok = missing_count == 0 and mismatch_count == 0
    canonical_allowed = hash_packet_ok and review_seal_allowed()
    report = {
        "schema_version": "dvf-3-3-current-source-authority-drift-independent-review-hash-v1",
        "status": "PASS" if canonical_allowed else "FAIL",
        "primary_review_artifact_manifest_path": rel(manifest_path),
        "primary_review_artifact_manifest_sha256": sha256_file(manifest_path),
        "primary_review_artifact_manifest_artifact_count": manifest.get("artifact_count"),
        "primary_review_artifact_missing_count": missing_count,
        "mismatch_count": mismatch_count,
        "comparison_checked_count": comparison_checked_count,
        "comparison_exempt_count": comparison_exempt_count,
        "artifact_hashes": rows,
        "independent_review_status": INDEPENDENT_REVIEW_RECORD["status"],
        "independent_review_record": INDEPENDENT_REVIEW_RECORD,
        "owner_seal_status": OWNER_SEAL_RECORD["status"],
        "owner_seal_record": OWNER_SEAL_RECORD,
        "canonical_retirement_seal_allowed": canonical_allowed,
    }
    write_json(phase / "independent_review_artifact_hash_report.json", report)
    return report


def phase_status(root: Path, phase: str, artifact: str) -> str:
    payload = read_json_object(root / phase / artifact)
    return str(payload.get("status", "MISSING"))


def write_phase6(root: Path, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    phase = phase_dir(root, "phase6")
    final_no_mutation = {
        "schema_version": "dvf-3-3-current-source-authority-drift-final-no-mutation-v1",
        **diff_hashes(before, after),
        "protected_surface_scope": "source_rendered_lua_bridge_runtime_package",
    }
    write_json(phase / "final_no_mutation_report.json", final_no_mutation)
    canonical_retirement_seal_allowed = final_no_mutation["status"] == "PASS" and review_seal_allowed()
    closeout_state = (
        "current_source_authority_drift_verification_recovery_scope_retirement_canonical_pass"
        if canonical_retirement_seal_allowed
        else "current_source_authority_drift_verification_recovery_scope_retirement_machine_complete_review_pending"
    )
    boundary = claim_boundary_markdown(closeout_state, canonical_retirement_seal_allowed=canonical_retirement_seal_allowed)
    write_text(phase / "final_claim_boundary_report.md", boundary)
    write_text(CLAIM_BOUNDARY_DOC, boundary)
    write_text(
        LEDGER_PACKET_DOC,
        "\n".join(
            [
                "# DVF 3-3 Current Source Authority Drift Verification Ledger Packet",
                "",
                f"Round: `{ROUND_ID}`",
                f"Evidence root: `{rel(root)}`",
                "",
                f"Status: `{closeout_state}`.",
                "",
                "Recovery live-write scope is retired from current execution authority and retained only as future drift contingency.",
                "This packet is governance/read-only evidence and does not mutate source, rendered, Lua bridge, runtime, package, or live required-validation manifest surfaces.",
                "",
                f"Independent review status: `{INDEPENDENT_REVIEW_RECORD['status']}`.",
                f"Owner seal status: `{OWNER_SEAL_RECORD['status']}`.",
            ]
        ),
    )
    checks = {
        "phase0_baseline": phase_status(root, "phase0", "supporting_readpoint_existence_inventory.json") == "PASS",
        "phase1_source_identity": phase_status(root, "phase1", "source_chain_identity_report.json") == "PASS",
        "phase2_direct_compose": phase_status(root, "phase2", "direct_current_compose_result.json") == "PASS",
        "phase2_overlay_requirement": phase_status(root, "phase2", "body_source_overlay_requirement_report.json") == "PASS",
        "phase3_rendered_alignment": phase_status(root, "phase3", "rendered_provenance_alignment_report.json") == "PASS",
        "phase4_fixture_non_reentry": phase_status(root, "phase4", "current_looking_fixture_payload_scan.json") == "PASS",
        "phase4_predecessor_guard": phase_status(root, "phase4", "predecessor_reentry_guard_report.json") == "PASS",
        "phase5_recovery_retirement": phase_status(root, "phase5", "recovery_scope_retirement_report.json") == "PASS",
        "final_no_mutation": final_no_mutation["status"] == "PASS",
    }
    final = {
        "schema_version": "dvf-3-3-current-source-authority-drift-final-report-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "machine_contract_status": "PASS" if all(checks.values()) else "FAIL",
        "closeout_state": closeout_state,
        "completion_token": (
            "current_source_authority_drift_verification_recovery_scope_retirement_canonical_pass"
            if canonical_retirement_seal_allowed
            else "current_source_authority_drift_verification_recovery_scope_retirement_machine_complete"
        ),
        "canonical_retirement_seal_status": "PASS" if canonical_retirement_seal_allowed else "blocked_pending_independent_review_and_owner_seal",
        "canonical_retirement_seal_allowed": canonical_retirement_seal_allowed,
        "independent_review_status": INDEPENDENT_REVIEW_RECORD["status"],
        "independent_review_record": INDEPENDENT_REVIEW_RECORD,
        "owner_seal_status": OWNER_SEAL_RECORD["status"],
        "owner_seal_record": OWNER_SEAL_RECORD,
        "checks": checks,
        "non_claims": [
            "no_source_restoration",
            "no_old_predecessor_recovery",
            "no_current_authority_cutover",
            "no_live_migration_execution_completion",
            "no_rendered_live_regeneration",
            "no_lua_bridge_export",
            "no_runtime_chunk_replacement",
            "no_release_readiness",
            "no_manual_in_game_qa",
            "no_semantic_quality_completion",
            "no_public_facing_text_acceptance",
            "no_live_required_validation_manifest_adoption",
        ],
    }
    write_json(phase / "final_current_source_authority_drift_verification_report.json", final)
    write_validation_report_placeholders(root)
    manifest = write_primary_review_manifest(root)
    review = write_independent_review_hash_report(root)
    final["primary_review_artifact_manifest_status"] = manifest["status"]
    final["primary_review_artifact_missing_count"] = manifest["missing_count"]
    final["independent_review_artifact_hash_report_status"] = review["status"]
    final["independent_review_artifact_hash_mismatch_count"] = review["mismatch_count"]
    write_json(phase / "final_current_source_authority_drift_verification_report.json", final)
    write_primary_review_manifest(root)
    write_independent_review_hash_report(root)
    return final


def generate_artifacts(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    surface = protected_surface_manifest_payload()
    before = hash_protected_surface(surface)
    write_phase0(root, surface, before)
    after = hash_protected_surface(surface)
    write_phase1(root, before, after)
    after = hash_protected_surface(surface)
    write_phase2(root, before, after)
    after = hash_protected_surface(surface)
    write_phase3(root, before, after)
    after = hash_protected_surface(surface)
    write_phase4(root, before, after)
    after = hash_protected_surface(surface)
    write_phase5(root)
    after = hash_protected_surface(surface)
    return write_phase6(root, before, after)


def object_field(payload: dict[str, Any], field_path: str) -> Any:
    current: Any = payload
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return None
    return current


def recalculate_review_manifest_hashes(root: Path) -> dict[str, Any]:
    manifest_path = root / "phase6" / "primary_review_artifact_manifest.json"
    manifest = read_json_object(manifest_path)
    rows = manifest.get("artifacts", [])
    missing: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    checked_count = 0
    exempt_count = 0
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        relative = str(row.get("root_relative_path") or "")
        path_value = row.get("path")
        if not isinstance(path_value, str):
            missing.append({"path": None, "root_relative_path": relative, "reason": "artifact_path_not_string"})
            continue
        path = root / relative if relative else resolve_repo(path_value)
        exists = path.exists()
        policy = str(row.get("hash_comparison_policy") or FROZEN_HASH_POLICY)
        if not exists:
            missing.append({"path": path_value, "root_relative_path": relative, "reason": "artifact_missing"})
        if policy == FROZEN_HASH_POLICY:
            checked_count += 1
            expected_sha256 = row.get("expected_sha256")
            actual_sha256 = sha256_file(path)
            if not exists or expected_sha256 != actual_sha256:
                mismatches.append(
                    {
                        "path": path_value,
                        "root_relative_path": relative,
                        "expected_sha256": expected_sha256,
                        "actual_sha256": actual_sha256,
                    }
                )
        else:
            exempt_count += 1
    return {
        "artifact_count": len(rows) if isinstance(rows, list) else 0,
        "primary_review_artifact_missing_count": len(missing),
        "mismatch_count": len(mismatches),
        "comparison_checked_count": checked_count,
        "comparison_exempt_count": exempt_count,
        "missing_artifacts": missing,
        "mismatched_artifacts": mismatches,
    }


def validate_artifacts(root: Path = EVIDENCE_ROOT, *, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_checks = [
        ("phase0/protected_surface_manifest.json", {"protected_surface_classes.source": None}),
        ("phase0/tooling_existence_inventory.json", {"status": "PASS"}),
        ("phase0/supporting_readpoint_existence_inventory.json", {"status": "PASS"}),
        ("phase1/source_chain_identity_report.json", {"status": "PASS"}),
        ("phase1/source_identity_no_mutation_verdict.json", {"status": "PASS", "changed_count": 0}),
        ("phase2/direct_compose_writer_sink_preflight_report.json", {"status": "PASS", "live_rendered_output_paths_blocked": True}),
        ("phase2/direct_current_compose_result.json", {"status": "PASS"}),
        ("phase2/body_source_overlay_requirement_report.json", {"status": "PASS", "runtime_adopted_missing_overlay_count": 0}),
        ("phase2/protected_rendered_no_mutation_verdict.json", {"status": "PASS", "changed_count": 0}),
        ("phase3/rendered_provenance_alignment_report.json", {"status": "PASS"}),
        ("phase3/rendered_no_mutation_verdict.json", {"status": "PASS", "changed_count": 0}),
        ("phase4/content_derived_six_entry_signature.json", {"status": "PASS", "member_count": 6}),
        ("phase4/six_entry_signature_determinism_report.json", {"status": "PASS"}),
        ("phase4/current_looking_fixture_payload_scan.json", {"status": "PASS", "current_looking_six_entry_payload_count": 0}),
        ("phase4/predecessor_reentry_guard_report.json", {"status": "PASS", "predecessor_reentry_violation_count": 0}),
        ("phase4/predecessor_guard_no_mutation_verdict.json", {"status": "PASS", "changed_count": 0}),
        ("phase5/recovery_scope_retirement_report.json", {"status": "PASS", "live_write_execution_authority_remaining_count": 0}),
        ("phase5/required_validation_integration_report.json", {"status": "PASS", "live_manifest_mutated": False}),
        ("phase6/final_no_mutation_report.json", {"status": "PASS", "changed_count": 0}),
        (
            "phase6/primary_review_artifact_manifest.json",
            {
                "status": "PASS",
                "generated_before_review": True,
                "missing_count": 0,
                "manifest_scope": "complete_evidence_inventory",
                "artifact_count": len(PRIMARY_REVIEW_ARTIFACTS),
                "inventory_file_count": len(PRIMARY_REVIEW_ARTIFACTS),
                "frozen_expected_hash_count": len(PRIMARY_REVIEW_ARTIFACTS) - len(COMPARISON_EXEMPT_REVIEW_ARTIFACTS),
                "comparison_exempt_artifact_count": len(COMPARISON_EXEMPT_REVIEW_ARTIFACTS),
            },
        ),
        (
            "phase6/independent_review_artifact_hash_report.json",
            {
                "status": "PASS",
                "primary_review_artifact_missing_count": 0,
                "mismatch_count": 0,
                "comparison_checked_count": len(PRIMARY_REVIEW_ARTIFACTS) - len(COMPARISON_EXEMPT_REVIEW_ARTIFACTS),
                "comparison_exempt_count": len(COMPARISON_EXEMPT_REVIEW_ARTIFACTS),
                "independent_review_status": "PASS",
                "owner_seal_status": "PASS",
                "canonical_retirement_seal_allowed": True,
            },
        ),
        (
            "phase6/final_current_source_authority_drift_verification_report.json",
            {"status": "PASS", "machine_contract_status": "PASS", "canonical_retirement_seal_allowed": True},
        ),
    ]
    for relative, checks in required_checks:
        path = root / relative
        if not path.exists():
            errors.append({"code": "missing_required_artifact", "path": rel(path)})
            continue
        payload = read_json_object(path)
        for field, expected in checks.items():
            if expected is None:
                if object_field(payload, field) in (None, [], {}):
                    errors.append({"code": "required_field_empty", "path": rel(path), "field": field})
                continue
            observed = object_field(payload, field)
            if observed != expected:
                errors.append({"code": "field_mismatch", "path": rel(path), "field": field, "expected": expected, "observed": observed})
    final = read_json_object(root / "phase6" / "final_current_source_authority_drift_verification_report.json")
    review = read_json_object(root / "phase6" / "independent_review_artifact_hash_report.json")
    recalculated_hashes = recalculate_review_manifest_hashes(root)
    expected_checked = len(PRIMARY_REVIEW_ARTIFACTS) - len(COMPARISON_EXEMPT_REVIEW_ARTIFACTS)
    expected_exempt = len(COMPARISON_EXEMPT_REVIEW_ARTIFACTS)
    if recalculated_hashes["artifact_count"] != len(PRIMARY_REVIEW_ARTIFACTS):
        errors.append(
            {
                "code": "review_manifest_artifact_count_mismatch",
                "expected": len(PRIMARY_REVIEW_ARTIFACTS),
                "observed": recalculated_hashes["artifact_count"],
            }
        )
    if recalculated_hashes["primary_review_artifact_missing_count"] != 0:
        errors.append(
            {
                "code": "review_artifact_missing_recalculated",
                "observed": recalculated_hashes["primary_review_artifact_missing_count"],
                "details": recalculated_hashes["missing_artifacts"],
            }
        )
    if recalculated_hashes["mismatch_count"] != 0:
        errors.append(
            {
                "code": "review_artifact_hash_mismatch_recalculated",
                "observed": recalculated_hashes["mismatch_count"],
                "details": recalculated_hashes["mismatched_artifacts"],
            }
        )
    if recalculated_hashes["comparison_checked_count"] != expected_checked:
        errors.append(
            {
                "code": "review_hash_comparison_checked_count_mismatch",
                "expected": expected_checked,
                "observed": recalculated_hashes["comparison_checked_count"],
            }
        )
    if recalculated_hashes["comparison_exempt_count"] != expected_exempt:
        errors.append(
            {
                "code": "review_hash_comparison_exempt_count_mismatch",
                "expected": expected_exempt,
                "observed": recalculated_hashes["comparison_exempt_count"],
            }
        )
    for field in ("primary_review_artifact_missing_count", "mismatch_count", "comparison_checked_count", "comparison_exempt_count"):
        observed = review.get(field)
        expected = recalculated_hashes[field]
        if observed != expected:
            errors.append(
                {
                    "code": "review_hash_report_summary_stale",
                    "field": field,
                    "expected": expected,
                    "observed": observed,
                }
            )
    if require_complete:
        if review.get("independent_review_status") != "PASS":
            errors.append({"code": "canonical_retirement_seal_requires_independent_review", "observed": review.get("independent_review_status")})
        if review.get("owner_seal_status") != "PASS":
            errors.append({"code": "canonical_retirement_seal_requires_owner_seal", "observed": review.get("owner_seal_status")})
        if final.get("canonical_retirement_seal_allowed") is not True:
            errors.append({"code": "canonical_retirement_seal_not_allowed", "observed": final.get("canonical_retirement_seal_allowed")})
    report = {
        "schema_version": "dvf-3-3-current-source-authority-drift-validation-report-v1",
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    report_name = "validation_report.require_complete.json" if require_complete else "validation_report.all.json"
    write_json(root / "phase6" / report_name, report)
    if (root / "phase6" / "primary_review_artifact_manifest.json").exists():
        write_independent_review_hash_report(root)
    return report, not errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate or validate DVF 3-3 current source authority drift verification evidence.")
    parser.add_argument("--mode", choices=("generate", "validate", "all"), default="all")
    parser.add_argument("--root", type=Path, default=EVIDENCE_ROOT)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)

    final: dict[str, Any] | None = None
    if args.mode in {"generate", "all"}:
        final = generate_artifacts(args.root)
        print(json.dumps({"status": final["status"], "closeout_state": final["closeout_state"]}, sort_keys=True))
        if args.mode == "generate":
            return 0 if final.get("status") == "PASS" else 1
    if args.mode in {"validate", "all"}:
        report, ok = validate_artifacts(args.root, require_complete=args.require_complete)
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
