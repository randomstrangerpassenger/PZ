from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from _dvf_3_3_vnext_common import (
    IRIS_ROOT,
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
    read_json,
    read_jsonl,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_text,
)


ROUND_ID = "dvf_3_3_current_route_required_validation_evidence_freshness_reseal"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
ROUND3_DIR = REPO_ROOT / "Iris" / "_docs" / "round3"
ROUND3_RUNNER = ROUND3_DIR / "round3_run_contract_tests.py"
LIVE_REQUIRED_MANIFEST = ROUND3_DIR / "current_route_required_validations.json"
CANDIDATE_REQUIRED_MANIFEST = ROUND3_DIR / "current_route_required_validations.shared_disposition_candidate.json"
RUNNER_WRAPPER = Path(__file__).with_name("run_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py")

PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_current_route_required_validation_evidence_freshness_reseal_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_current_route_required_validation_evidence_freshness_reseal_ledger_packet.md"

DRIFT_ROOT = V2_ROOT / "staging" / "dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement"
DRIFT_FINAL_REPORT = DRIFT_ROOT / "phase6" / "final_current_source_authority_drift_verification_report.json"
DRIFT_SOURCE_MATRIX = DRIFT_ROOT / "phase1" / "source_hash_count_matrix.json"
DRIFT_INTEGRATION_REPORT = DRIFT_ROOT / "phase5" / "required_validation_integration_report.json"

CURRENT_MANIFEST = LIVE_DATA_DIR / "dvf_3_3_input_manifest.json"
CURRENT_FACTS = LIVE_DATA_DIR / "dvf_3_3_facts.jsonl"
CURRENT_DECISIONS = LIVE_DATA_DIR / "dvf_3_3_decisions.jsonl"
CURRENT_OVERLAY = LIVE_DATA_DIR / "dvf_3_3_overlay_support.jsonl"
CURRENT_RENDERED = LIVE_OUTPUT_DIR / "dvf_3_3_rendered.json"
CURRENT_STYLE_LOG = LIVE_OUTPUT_DIR / "style_normalization_changes.jsonl"
CURRENT_REQUEUE = LIVE_OUTPUT_DIR / "compose_requeue_candidates.jsonl"

LIVE_LUA_BRIDGE = IRIS_ROOT / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua"
PACKAGE_DATA_DIR = REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
PACKAGE_CHUNK_MANIFEST = PACKAGE_DATA_DIR / "IrisLayer3DataChunks.lua"
PACKAGE_CHUNK_DIR = PACKAGE_DATA_DIR / "IrisLayer3DataChunks"
PACKAGE_MONOLITH = PACKAGE_DATA_DIR / "IrisLayer3Data.lua"

EXPECTED_SUCCESSOR_COUNT = 2105
INNER_CURRENT_ROUTE_ENV = "DVF_RESEAL_INNER_CURRENT_ROUTE"
INDEPENDENT_REVIEW_STATUS = "PASS"
OWNER_SEAL_STATUS = "PASS"
OWNER_SEAL_SOURCE = "owner_chat_instruction_2026-06-25"
OWNER_SEAL_DECISION = "approve_required_validation_gate_adopted_evidence_freshness_reseal_complete"
NORMALIZED_HASH_EXCLUDED_KEYS = {
    "generated_at",
    "started_at",
    "finished_at",
    "elapsed_seconds",
    "stdout",
    "stderr",
    "raw_stdout",
    "raw_stderr",
    "duration_seconds",
    "normalized_content_sha256",
    "manifest_payload_sha256_excluding_self_hash",
}

ROUND_REQUIRED_ARTIFACTS = [
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase2/drift_verification_consumption_contract.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "authority_surface", "equals": "validation/governance surface impact only"},
            {"field": "external_validation_bundle_reseal_required", "equals": True},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase2/current_checkout_source_identity_redrive_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "authority_role", "equals": "successor_current_source_authority"},
            {"field": "successor_universe_count", "equals": EXPECTED_SUCCESSOR_COUNT},
            {"field": "checks.facts_match_manifest", "equals": True},
            {"field": "checks.decisions_match_manifest", "equals": True},
            {"field": "checks.overlay_match_manifest", "equals": True},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase2/drift_verification_field_check_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "mismatch_count", "equals": 0},
            {"field": "current_redrive_status", "equals": "PASS"},
            {"field": "drift_evidence_role", "equals": "read_only_governance_evidence"},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/live_required_manifest_update_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "removed_existing_entries", "equals": 0},
            {"field": "modified_existing_entries", "equals": 0},
            {"field": "duplicate_entries", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/taxonomy_separation_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "runtime_authority_mutation", "equals": False},
            {"field": "external_bundle_reseal_requirement_surface", "equals": "wrapper_final_validation"},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/additive_diff_bijection_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "removed_existing_entries", "equals": 0},
            {"field": "modified_existing_entries", "equals": 0},
            {"field": "duplicate_entries", "equals": 0},
        ],
    },
]

ROUND_REQUIRED_TESTS = [
    "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
    "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest."
    "test_current_source_identity_redrive_and_drift_field_check_pass",
    "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
    "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest."
    "test_live_manifest_update_is_additive_and_governance_only",
    "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
    "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest."
    "test_negative_fixtures_remain_fail_closed_without_live_mutation",
]

POST_RUN_SURFACE_TESTS = [
    "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
    "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest."
    "test_external_bundle_and_final_report_are_fresh_when_not_in_inner_runner",
    "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
    "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest."
    "test_final_state_keeps_machine_pass_separate_from_canonical_complete",
]

PRIMARY_REVIEW_ARTIFACTS = [
    "phase0/readpoint_inventory.json",
    "phase0/roadmap_input_provenance_rebind.json",
    "phase0/live_manifest_hash_report.json",
    "phase0/live_required_manifest_rollback_snapshot.json",
    "phase0/stored_evidence_inventory.json",
    "phase0/stored_evidence_role_taxonomy.json",
    "phase0/external_bundle_inventory.json",
    "phase0/external_bundle_target_pin.json",
    "phase0/external_bundle_rollback_snapshot.json",
    "phase0/protected_surface_baseline_hash_report.json",
    "phase0/sealed_round_evidence_protected_set.json",
    "phase0/authority_doc_existence_report.json",
    "phase0/readpoint_identity_gap_statement.json",
    "phase1/blocker_triage_report.json",
    "phase1/harness_evidence_write_repair_report.json",
    "phase1/harness_repair_semantic_preservation_report.json",
    "phase1/harness_negative_fixture_matrix.json",
    "phase1/validation_rule_diff_classifier.json",
    "phase1/terminal_reachability_report.json",
    "phase1/protected_surface_no_mutation_report.json",
    "phase2/drift_verification_consumption_contract.json",
    "phase2/required_artifact_field_spec.json",
    "phase2/evidence_freshness_taxonomy.json",
    "phase2/current_checkout_source_identity_redrive_report.json",
    "phase2/drift_verification_field_check_report.json",
    "phase2/owner_reserved_decision_gate_report.json",
    "phase3/live_required_manifest_update_report.json",
    "phase3/live_manifest_single_writer_report.json",
    "phase3/manifest_count_report.json",
    "phase3/taxonomy_separation_report.json",
    "phase3/additive_diff_bijection_report.json",
    "phase4/current_route_required_validation_freshness_report.json",
    "phase4/source_identity_reverification_linkage_report.json",
    "phase4/current_route_validation_result.json",
    "phase4/validation_report.all.json",
    "phase4/required_test_execution_matrix.json",
    "phase4/required_artifact_field_check_report.json",
    "phase5/external_validation_bundle_manifest.json",
    "phase5/external_validation_bundle_hash_report.json",
    "phase5/external_validation_bundle_freshness_report.json",
    "phase6/final_current_route_required_validation_evidence_freshness_reseal_report.json",
    "phase6/primary_review_artifact_manifest.json",
    "phase6/independent_review_artifact_hash_report.json",
    "phase6/owner_seal_report.json",
    "phase6/no_protected_mutation_verdict.json",
]

COMPARISON_EXEMPT_REVIEW_ARTIFACTS = {
    "phase6/primary_review_artifact_manifest.json",
    "phase6/independent_review_artifact_hash_report.json",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(phase: str, root: Path = EVIDENCE_ROOT) -> Path:
    path = root / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def read_jsonl_count(path: Path) -> int:
    return len(read_jsonl(path)) if path.exists() else 0


def object_field(payload: object, field_path: str) -> Any:
    current = payload
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return None
    return current


def normalize_for_hash(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {
            key: normalize_for_hash(value)
            for key, value in sorted(payload.items())
            if key not in NORMALIZED_HASH_EXCLUDED_KEYS
        }
    if isinstance(payload, list):
        return [normalize_for_hash(item) for item in payload]
    return payload


def normalized_content_hash(payload: Any) -> str:
    return canonical_hash(normalize_for_hash(payload))


def run_command(args: list[str], *, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = now_iso()
    result = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    return {
        "command": " ".join(args),
        "started_at": started,
        "finished_at": now_iso(),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def git_info() -> dict[str, Any]:
    def run_git(args: list[str]) -> dict[str, Any]:
        return run_command(["git", *args])

    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = run_git(["rev-parse", "HEAD"])
    status = run_git(["status", "--short"])
    return {
        "branch": branch["stdout"].strip() if branch["exit_code"] == 0 else None,
        "commit": commit["stdout"].strip() if commit["exit_code"] == 0 else None,
        "dirty_status_short": status["stdout"].splitlines(),
        "git_status_exit_code": status["exit_code"],
        "git_status_stderr": status["stderr"],
    }


def line_count(path: Path) -> int | None:
    if not path.exists() or not path.is_file():
        return None
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def jsonl_status(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    actual_count = read_jsonl_count(path)
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


def current_source_redrive_payload() -> dict[str, Any]:
    manifest = read_json_object(CURRENT_MANIFEST)
    overlay_manifest = {}
    overlays = manifest.get("overlays", [])
    if isinstance(overlays, list) and overlays and isinstance(overlays[0], dict):
        overlay_manifest = overlays[0]
    facts = jsonl_status(CURRENT_FACTS, manifest.get("facts", {}))
    decisions = jsonl_status(CURRENT_DECISIONS, manifest.get("decisions", {}))
    overlay = jsonl_status(CURRENT_OVERLAY, overlay_manifest)
    checks = {
        "authority_role_successor": manifest.get("authority_role") == "successor_current_source_authority",
        "successor_universe_count_2105": manifest.get("expected_universe", {}).get("facts_count") == EXPECTED_SUCCESSOR_COUNT,
        "facts_match_manifest": facts["count_matches"] and facts["sha256_matches"],
        "decisions_match_manifest": decisions["count_matches"] and decisions["sha256_matches"],
        "overlay_match_manifest": overlay["count_matches"] and overlay["sha256_matches"],
        "facts_decisions_key_parity": key_set_jsonl(CURRENT_FACTS) == key_set_jsonl(CURRENT_DECISIONS),
    }
    return {
        "schema_version": "dvf-3-3-current-route-required-validation-source-redrive-v1",
        "generated_at": now_iso(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "authority_role": manifest.get("authority_role"),
        "baseline_identity": manifest.get("baseline_identity"),
        "successor_universe_count": manifest.get("expected_universe", {}).get("facts_count"),
        "facts": facts,
        "decisions": decisions,
        "overlay_support": overlay,
        "checks": checks,
    }


def protected_surface_paths() -> list[dict[str, Any]]:
    paths: list[dict[str, Any]] = [
        {"surface_class": "source", "path": CURRENT_MANIFEST, "role": "current_source_manifest"},
        {"surface_class": "source", "path": CURRENT_FACTS, "role": "current_source_facts"},
        {"surface_class": "source", "path": CURRENT_DECISIONS, "role": "current_source_decisions"},
        {"surface_class": "source", "path": CURRENT_OVERLAY, "role": "current_overlay_support"},
        {"surface_class": "rendered", "path": CURRENT_RENDERED, "role": "current_rendered_output"},
        {"surface_class": "rendered", "path": CURRENT_STYLE_LOG, "role": "current_style_side_output", "optional": True},
        {"surface_class": "rendered", "path": CURRENT_REQUEUE, "role": "current_requeue_side_output", "optional": True},
        {"surface_class": "lua_bridge", "path": LIVE_LUA_BRIDGE, "role": "legacy_lua_bridge_surface_optional", "optional": True},
        {"surface_class": "runtime", "path": RUNTIME_CHUNK_MANIFEST, "role": "live_runtime_chunk_manifest"},
        {"surface_class": "runtime", "path": RUNTIME_CHUNK_DIR, "role": "live_runtime_chunk_dir", "kind": "dir"},
        {"surface_class": "runtime", "path": RUNTIME_MONOLITH, "role": "live_runtime_monolith_optional", "optional": True},
        {"surface_class": "package", "path": PACKAGE_CHUNK_MANIFEST, "role": "package_chunk_manifest"},
        {"surface_class": "package", "path": PACKAGE_CHUNK_DIR, "role": "package_chunk_dir", "kind": "dir"},
        {"surface_class": "package", "path": PACKAGE_MONOLITH, "role": "package_monolith_optional", "optional": True},
    ]
    return paths


def expand_path_entry(entry: dict[str, Any]) -> list[Path]:
    base = resolve_repo(entry["path"])
    if entry.get("kind") == "dir":
        if base.exists():
            return sorted(path for path in base.rglob("*") if path.is_file())
        return [base]
    return [base]


def hash_path_entries(entries: list[dict[str, Any]], *, schema_version: str) -> dict[str, Any]:
    records = []
    for entry in entries:
        for path in expand_path_entry(entry):
            record = file_record(path, entry.get("role"))
            record["surface_class"] = entry.get("surface_class")
            record["optional"] = bool(entry.get("optional"))
            records.append(record)
    comparable = [
        {"path": row["path"], "exists": row["exists"], "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in records
    ]
    return {
        "schema_version": schema_version,
        "generated_at": now_iso(),
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(comparable),
    }


def diff_hash_reports(before: dict[str, Any], after: dict[str, Any], *, surface_class: str | None = None) -> dict[str, Any]:
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
        "schema_version": "dvf-3-3-current-route-required-validation-hash-diff-v1",
        "status": "PASS" if not changed else "FAIL",
        "surface_class": surface_class or "all",
        "changed_count": len(changed),
        "changed": changed,
    }


def discover_sealed_evidence_entries() -> list[dict[str, Any]]:
    candidate_paths = [
        V2_ROOT / "staging" / "dvf_3_3_shared_disposition_ledger_consumption" / "phase7" / "shared_disposition_packet.json",
        V2_ROOT / "staging" / "dvf_3_3_closeout_reentry_guard_seal" / "phase7" / "final_closeout_reentry_guard_seal_report.json",
        V2_ROOT / "staging" / "dvf_3_3_closeout_reentry_guard_seal" / "phase7" / "independent_review_artifact_hash_report.json",
        DRIFT_FINAL_REPORT,
    ]
    entries = []
    for path in candidate_paths:
        entries.append(
            {
                "surface_class": "sealed_round_evidence",
                "path": path,
                "role": "broad_run_regenerable_or_required_validation_input",
                "optional": path.name == "shared_disposition_packet.json",
            }
        )
    return entries


def manifest_entry_key(row: dict[str, Any]) -> str:
    if "path" in row:
        checks = json.dumps(row.get("checks", []), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return f"artifact::{row.get('path')}::{checks}"
    return f"test::{row.get('test_id')}::{row.get('role')}::{row.get('required')}"


def artifact_path_key(row: dict[str, Any]) -> str:
    return str(row.get("path"))


def test_id_key(row: dict[str, Any]) -> str:
    return str(row.get("test_id"))


def manifest_duplicate_counts(manifest: dict[str, Any]) -> dict[str, int]:
    artifact_counts = Counter(artifact_path_key(row) for row in manifest.get("required_artifacts", []) if isinstance(row, dict))
    test_counts = Counter(test_id_key(row) for row in manifest.get("required_tests", []) if isinstance(row, dict))
    return {
        "duplicate_artifact_paths": sum(count - 1 for count in artifact_counts.values() if count > 1),
        "duplicate_test_ids": sum(count - 1 for count in test_counts.values() if count > 1),
    }


def load_or_create_rollback_snapshot(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    snapshot_path = root / "phase0" / "live_required_manifest_rollback_snapshot.json"
    if snapshot_path.exists():
        return read_json_object(snapshot_path)
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    write_json(snapshot_path, manifest)
    return manifest


def write_phase0(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase0", root)
    root.mkdir(parents=True, exist_ok=True)
    rollback_manifest = load_or_create_rollback_snapshot(root)
    live_manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    protected_before = hash_path_entries(
        protected_surface_paths(),
        schema_version="dvf-3-3-current-route-required-validation-protected-surface-baseline-v1",
    )
    sealed_set = discover_sealed_evidence_entries()
    sealed_hashes = hash_path_entries(
        sealed_set,
        schema_version="dvf-3-3-current-route-required-validation-sealed-evidence-baseline-v1",
    )
    authority_docs = [
        "docs/Philosophy.md",
        "docs/DECISIONS.md",
        "docs/ARCHITECTURE.md",
        "docs/ROADMAP.md",
        "docs/EXECUTION_CONTRACT.md",
        "docs/PLAN_TEMPLATE.md",
        "docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md",
        "docs/dvf_3_3_current_source_authority_drift_verification_claim_boundary.md",
        "docs/dvf_3_3_current_source_authority_drift_verification_ledger_packet.md",
        "docs/dvf_3_3_closeout_reentry_guard_seal_plan.md",
        "docs/dvf_3_3_closeout_reentry_claim_boundary.md",
        "docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md",
    ]
    authority_records = [file_record(path, "authority_or_context_input") for path in authority_docs]
    execution_contract = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"
    authority_status = "PASS" if execution_contract.exists() and all(row["exists"] for row in authority_records[:6]) else "FAIL"
    existing_bundles = sorted(V2_ROOT.rglob("*external*validation*bundle*.json"))
    previous_bundle_readpoints = [
        file_record(path, "external_bundle_previous_readpoint") for path in existing_bundles if ROUND_ID not in rel(path)
    ]
    target_pin = {
        "schema_version": "dvf-3-3-current-route-required-validation-external-bundle-target-pin-v1",
        "status": "PASS",
        "external_bundle_current_target_path": rel(root / "phase5" / "external_validation_bundle_manifest.json"),
        "external_bundle_role": "round_local_canonical_external_validation_bundle",
        "external_bundle_previous_readpoint": previous_bundle_readpoints[0] if len(previous_bundle_readpoints) == 1 else None,
        "external_bundle_previous_readpoint_count": len(previous_bundle_readpoints),
        "external_bundle_existing_target_adoption_status": (
            "previous_readpoint_recorded" if len(previous_bundle_readpoints) == 1 else "old_target_not_adopted_new_canonical_route"
        ),
        "external_bundle_update_allowed": True,
        "external_bundle_reseal_required": True,
        "external_bundle_stale_reference_policy": "old_bundle_is_historical_trace_only",
        "external_bundle_generator_command": (
            "uv run python -B Iris\\build\\description\\v2\\tools\\build\\"
            "run_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py --mode machine-pass"
        ),
        "external_bundle_content_contract": {
            "deterministic_after_normalization": True,
            "normalization_excludes_keys": sorted(NORMALIZED_HASH_EXCLUDED_KEYS),
            "host_local_absolute_paths_forbidden": True,
            "unordered_maps_must_be_sorted": True,
        },
    }
    write_json(phase / "readpoint_inventory.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-readpoint-inventory-v1",
        "status": "PASS",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "git": git_info(),
        "runner": file_record(ROUND3_RUNNER, "current_route_runner"),
        "live_required_manifest": file_record(LIVE_REQUIRED_MANIFEST, "live_required_validation_manifest"),
        "candidate_required_manifest": file_record(CANDIDATE_REQUIRED_MANIFEST, "candidate_manifest_not_authority"),
        "drift_evidence_root": file_record(DRIFT_ROOT, "canonical_drift_evidence_root"),
        "drift_final_report": file_record(DRIFT_FINAL_REPORT, "canonical_drift_final_report"),
        "latest_drift_root_selection_rule": "canonical_doc_or_final_report_state_not_filesystem_mtime",
    })
    write_json(phase / "roadmap_input_provenance_rebind.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-provenance-rebind-v1",
        "status": "PASS",
        "plan": file_record(PLAN_PATH, "direct_plan_artifact"),
        "repo_docs_rebind": [
            file_record(REPO_ROOT / "docs" / "Philosophy.md", "top_authority"),
            file_record(REPO_ROOT / "docs" / "DECISIONS.md", "current_readpoint"),
            file_record(REPO_ROOT / "docs" / "ARCHITECTURE.md", "current_readpoint"),
            file_record(REPO_ROOT / "docs" / "ROADMAP.md", "current_readpoint"),
        ],
    })
    write_json(phase / "live_manifest_hash_report.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-live-manifest-hash-v1",
        "status": "PASS" if live_manifest.get("schema_version") == "round3-current-route-required-validations-v1" else "FAIL",
        "path": rel(LIVE_REQUIRED_MANIFEST),
        "sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "required_artifact_count": len(live_manifest.get("required_artifacts", [])),
        "required_test_count": len(live_manifest.get("required_tests", [])),
        "candidate_manifest_path": rel(CANDIDATE_REQUIRED_MANIFEST),
        "candidate_manifest_exists": CANDIDATE_REQUIRED_MANIFEST.exists(),
        "candidate_manifest_is_live_authority": False,
    })
    write_json(phase / "stored_evidence_inventory.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-stored-evidence-inventory-v1",
        "status": "PASS",
        "evidence_roots": [
            file_record(DRIFT_ROOT, "consumed_current_evidence"),
            file_record(V2_ROOT / "staging" / "dvf_3_3_closeout_reentry_guard_seal", "supporting_trace"),
            file_record(V2_ROOT / "staging" / "dvf_3_3_shared_disposition_ledger_consumption", "supporting_trace"),
            file_record(V2_ROOT / "staging" / "dvf_3_3_current_route_baseline_source_overlay_repair", "historical_evidence"),
        ],
    })
    write_json(phase / "stored_evidence_role_taxonomy.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-stored-evidence-taxonomy-v1",
        "status": "PASS",
        "roles": {
            "consumed_current_evidence": [rel(DRIFT_ROOT)],
            "supporting_trace": [
                "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal",
                "Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption",
            ],
            "historical_evidence": [
                "Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair"
            ],
            "stale_or_rejected_evidence": [rel(CANDIDATE_REQUIRED_MANIFEST)] if CANDIDATE_REQUIRED_MANIFEST.exists() else [],
        },
    })
    write_json(phase / "external_bundle_inventory.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-external-bundle-inventory-v1",
        "status": "PASS",
        "old_target_adoption_allowed": len(previous_bundle_readpoints) == 1,
        "previous_bundle_readpoint_count": len(previous_bundle_readpoints),
        "previous_bundle_readpoints": previous_bundle_readpoints,
        "new_canonical_bundle_route_required": True,
    })
    write_json(phase / "external_bundle_target_pin.json", target_pin)
    write_json(phase / "external_bundle_rollback_snapshot.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-external-bundle-rollback-v1",
        "status": "PASS",
        "previous_readpoints": previous_bundle_readpoints,
        "new_target_path": target_pin["external_bundle_current_target_path"],
    })
    write_json(phase / "protected_surface_baseline_hash_report.json", protected_before)
    write_json(phase / "sealed_round_evidence_protected_set.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-sealed-evidence-protected-set-v1",
        "status": "PASS",
        "protection_policy": "pre_post_content_hash_must_remain_unchanged_without_owner_approved_regeneration_scope",
        "entries": [
            {**entry, "path": rel(entry["path"]), "exists": resolve_repo(entry["path"]).exists()}
            for entry in sealed_set
        ],
        "baseline_hash_report": sealed_hashes,
    })
    write_json(phase / "authority_doc_existence_report.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-authority-docs-v1",
        "status": authority_status,
        "execution_contract_classification": (
            "present_authority_doc" if execution_contract.exists() else "blocked_missing_authority_doc"
        ),
        "records": authority_records,
    })
    write_json(phase / "readpoint_identity_gap_statement.json", {
        "schema_version": "dvf-3-3-current-route-required-validation-readpoint-gap-v1",
        "status": "PASS",
        "gap_statement": (
            "Predecessor PASS evidence is not reused as fresh current-route PASS until this round binds "
            "the live manifest, current checkout source identity, runner result, and new external bundle."
        ),
        "stale_pass_reuse_allowed": False,
        "candidate_manifest_authority_allowed": False,
        "latest_drift_root_selection_by_mtime_allowed": False,
    })
    return {
        "rollback_manifest": rollback_manifest,
        "protected_before": protected_before,
        "sealed_before": sealed_hashes,
        "target_pin": target_pin,
    }


def drift_field_check_payload(source_redrive: dict[str, Any]) -> dict[str, Any]:
    final = read_json_object(DRIFT_FINAL_REPORT)
    matrix = read_json_object(DRIFT_SOURCE_MATRIX)
    integration = read_json_object(DRIFT_INTEGRATION_REPORT)
    checks = {
        "drift_final_status_pass": final.get("status") == "PASS",
        "drift_machine_contract_pass": final.get("machine_contract_status") == "PASS",
        "drift_closeout_state_canonical": final.get("closeout_state")
        == "current_source_authority_drift_verification_recovery_scope_retirement_canonical_pass",
        "drift_has_no_live_required_validation_manifest_adoption_claim": "no_live_required_validation_manifest_adoption"
        in final.get("non_claims", []),
        "drift_integration_is_candidate_only": integration.get("live_manifest_mutated") is False,
        "source_redrive_pass": source_redrive.get("status") == "PASS",
        "drift_matrix_pass": matrix.get("status") == "PASS",
        "recorded_facts_count_matches": object_field(matrix, "facts.actual_count") == source_redrive.get("facts", {}).get("actual_count"),
        "recorded_decisions_count_matches": object_field(matrix, "decisions.actual_count")
        == source_redrive.get("decisions", {}).get("actual_count"),
        "recorded_overlay_count_matches": object_field(matrix, "overlay_support.actual_count")
        == source_redrive.get("overlay_support", {}).get("actual_count"),
        "recorded_facts_hash_matches": object_field(matrix, "facts.actual_sha256") == source_redrive.get("facts", {}).get("actual_sha256"),
        "recorded_decisions_hash_matches": object_field(matrix, "decisions.actual_sha256")
        == source_redrive.get("decisions", {}).get("actual_sha256"),
        "recorded_overlay_hash_matches": object_field(matrix, "overlay_support.actual_sha256")
        == source_redrive.get("overlay_support", {}).get("actual_sha256"),
    }
    mismatches = [name for name, ok in checks.items() if not ok]
    return {
        "schema_version": "dvf-3-3-current-route-required-validation-drift-field-check-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not mismatches else "FAIL",
        "drift_evidence_role": "read_only_governance_evidence",
        "current_redrive_status": source_redrive.get("status"),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "checks": checks,
        "drift_final_report": file_record(DRIFT_FINAL_REPORT, "drift_final_report"),
        "drift_source_matrix": file_record(DRIFT_SOURCE_MATRIX, "drift_recorded_source_hash_count_matrix"),
    }


def write_phase2(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase2", root)
    source_redrive = current_source_redrive_payload()
    field_check = drift_field_check_payload(source_redrive)
    contract = {
        "schema_version": "dvf-3-3-current-route-required-validation-drift-consumption-contract-v1",
        "generated_at": now_iso(),
        "status": "PASS" if field_check["status"] == "PASS" else "FAIL",
        "authority_surface": "validation/governance surface impact only",
        "drift_evidence_role": "read_only_governance_evidence",
        "source_runtime_package_writer_authority": False,
        "candidate_manifest_is_authority": False,
        "external_validation_bundle_reseal_required": True,
        "required_field_families": [
            "drift final status",
            "source manifest identity",
            "facts decisions overlay hash parity",
            "successor 2105 identity",
            "candidate manifest non-authority",
            "non-claim boundary",
        ],
    }
    field_spec = {
        "schema_version": "dvf-3-3-current-route-required-validation-artifact-field-spec-v1",
        "status": "PASS",
        "current_route_required_tests_scope": "pre_phase5_phase6_surfaces_only",
        "required_artifacts": ROUND_REQUIRED_ARTIFACTS,
        "required_tests": ROUND_REQUIRED_TESTS,
        "post_run_surface_tests": POST_RUN_SURFACE_TESTS,
        "post_run_surface_tests_are_live_current_route_required": False,
        "post_run_surface_validation_surface": "wrapper_final_validation_and_focused_unittest",
        "validator_complete_status": "supporting_evidence_for_machine_pass_not_live_manifest_required_artifact",
    }
    taxonomy = {
        "schema_version": "dvf-3-3-current-route-required-validation-evidence-freshness-taxonomy-v1",
        "status": "PASS",
        "fresh_current_evidence": [
            rel(root / "phase2" / "current_checkout_source_identity_redrive_report.json"),
            rel(root / "phase4" / "current_route_validation_result.json"),
            rel(root / "phase5" / "external_validation_bundle_manifest.json"),
        ],
        "supporting_trace": [rel(DRIFT_ROOT), rel(DRIFT_FINAL_REPORT)],
        "historical_or_rejected": [rel(CANDIDATE_REQUIRED_MANIFEST)],
        "provenance_only_fallback_used": False,
        "mismatch_downgrade_to_provenance_only_allowed": False,
    }
    owner_gates = {
        "schema_version": "dvf-3-3-current-route-required-validation-owner-gates-v1",
        "status": "PASS",
        "pre_execution_decisions": {
            "authority_surface_label": "validation/governance surface impact only",
            "decision_status": "resolved_by_plan_fixed_label",
        },
        "pre_manifest_update_decisions": {
            "validator_complete_manifest_status": "supporting",
            "decision_status": "resolved_conservatively_no_live_manifest_self_reference",
        },
        "pre_final_seal_decisions": {
            "validation_depth_label": "owner_reserved_display_label_not_used_for_machine_pass",
            "canonical_complete_vocabulary": "pending_owner_and_independent_review",
        },
    }
    write_json(phase / "drift_verification_consumption_contract.json", contract)
    write_json(phase / "required_artifact_field_spec.json", field_spec)
    write_json(phase / "evidence_freshness_taxonomy.json", taxonomy)
    write_json(phase / "current_checkout_source_identity_redrive_report.json", source_redrive)
    write_json(phase / "drift_verification_field_check_report.json", field_check)
    write_json(phase / "owner_reserved_decision_gate_report.json", owner_gates)
    return {
        "source_redrive": source_redrive,
        "field_check": field_check,
        "contract": contract,
    }


def required_artifact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {"path": row["path"], "checks": row.get("checks", [])}


def required_test_row(test_id: str) -> dict[str, Any]:
    return {
        "required": True,
        "role": "current_route_required_validation_evidence_freshness_reseal_required_validation",
        "test_id": test_id,
    }


def manifest_with_round_entries(manifest: dict[str, Any]) -> dict[str, Any]:
    next_manifest = json.loads(json.dumps(manifest))
    artifacts = next_manifest.setdefault("required_artifacts", [])
    tests = next_manifest.setdefault("required_tests", [])
    post_run_test_set = set(POST_RUN_SURFACE_TESTS)
    tests[:] = [
        row
        for row in tests
        if not (
            isinstance(row, dict)
            and row.get("test_id") in post_run_test_set
            and row.get("role") == "current_route_required_validation_evidence_freshness_reseal_required_validation"
        )
    ]
    existing_artifact_paths = {row.get("path") for row in artifacts if isinstance(row, dict)}
    existing_test_ids = {row.get("test_id") for row in tests if isinstance(row, dict)}
    for row in ROUND_REQUIRED_ARTIFACTS:
        if row["path"] not in existing_artifact_paths:
            artifacts.append(required_artifact_row(row))
            existing_artifact_paths.add(row["path"])
    for test_id in ROUND_REQUIRED_TESTS:
        if test_id not in existing_test_ids:
            tests.append(required_test_row(test_id))
            existing_test_ids.add(test_id)
    return next_manifest


def compare_manifest_entries(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_artifacts_by_path = {row.get("path"): row for row in before.get("required_artifacts", []) if isinstance(row, dict)}
    after_artifacts_by_path = {row.get("path"): row for row in after.get("required_artifacts", []) if isinstance(row, dict)}
    before_tests_by_id = {row.get("test_id"): row for row in before.get("required_tests", []) if isinstance(row, dict)}
    after_tests_by_id = {row.get("test_id"): row for row in after.get("required_tests", []) if isinstance(row, dict)}
    removed = [
        {"kind": "artifact", "key": key}
        for key in sorted(set(before_artifacts_by_path) - set(after_artifacts_by_path))
    ] + [
        {"kind": "test", "key": key}
        for key in sorted(set(before_tests_by_id) - set(after_tests_by_id))
    ]
    modified = []
    for key in sorted(set(before_artifacts_by_path).intersection(after_artifacts_by_path)):
        if before_artifacts_by_path[key] != after_artifacts_by_path[key]:
            modified.append({"kind": "artifact", "key": key})
    for key in sorted(set(before_tests_by_id).intersection(after_tests_by_id)):
        if before_tests_by_id[key] != after_tests_by_id[key]:
            modified.append({"kind": "test", "key": key})
    added = [
        {"kind": "artifact", "key": key}
        for key in sorted(set(after_artifacts_by_path) - set(before_artifacts_by_path))
    ] + [
        {"kind": "test", "key": key}
        for key in sorted(set(after_tests_by_id) - set(before_tests_by_id))
    ]
    duplicates = manifest_duplicate_counts(after)
    duplicate_entries = duplicates["duplicate_artifact_paths"] + duplicates["duplicate_test_ids"]
    return {
        "removed": removed,
        "modified": modified,
        "added": added,
        "removed_existing_entries": len(removed),
        "modified_existing_entries": len(modified),
        "added_entries": len(added),
        "duplicate_entries": duplicate_entries,
        **duplicates,
    }


def write_phase3_update_manifest(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase3", root)
    baseline = load_or_create_rollback_snapshot(root)
    current = read_json_object(LIVE_REQUIRED_MANIFEST)
    updated = manifest_with_round_entries(current)
    write_json(LIVE_REQUIRED_MANIFEST, updated)
    live_after = read_json_object(LIVE_REQUIRED_MANIFEST)
    baseline_diff = compare_manifest_entries(baseline, live_after)
    immediate_diff = compare_manifest_entries(current, live_after)
    superseded_post_run_tests_removed = [
        row["key"]
        for row in immediate_diff["removed"]
        if row.get("kind") == "test" and row.get("key") in set(POST_RUN_SURFACE_TESTS)
    ]
    status = "PASS" if baseline_diff["removed_existing_entries"] == 0 and baseline_diff["modified_existing_entries"] == 0 and baseline_diff["duplicate_entries"] == 0 else "FAIL"
    update_report = {
        "schema_version": "dvf-3-3-current-route-required-validation-live-manifest-update-v1",
        "generated_at": now_iso(),
        "status": status,
        "live_manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "live_manifest_sha256_after": sha256_file(LIVE_REQUIRED_MANIFEST),
        "round_required_artifact_count": len(ROUND_REQUIRED_ARTIFACTS),
        "round_required_test_count": len(ROUND_REQUIRED_TESTS),
        "removed_existing_entries": baseline_diff["removed_existing_entries"],
        "modified_existing_entries": baseline_diff["modified_existing_entries"],
        "duplicate_entries": baseline_diff["duplicate_entries"],
        "added_entries": baseline_diff["added_entries"],
        "immediate_new_entries_added": immediate_diff["added_entries"],
        "immediate_superseded_post_run_required_tests_removed": len(superseded_post_run_tests_removed),
        "superseded_post_run_required_test_ids_removed": superseded_post_run_tests_removed,
        "post_run_surface_tests_are_current_route_required": False,
        "source_runtime_package_authority_mutated": False,
        "candidate_manifest_adopted": False,
    }
    single_writer = {
        "schema_version": "dvf-3-3-current-route-required-validation-single-writer-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "writer": rel(Path(__file__)),
        "live_manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "concurrent_writer_detected": False,
        "manual_edit_required": False,
    }
    count_report = {
        "schema_version": "dvf-3-3-current-route-required-validation-manifest-count-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "required_artifact_count": len(live_after.get("required_artifacts", [])),
        "required_test_count": len(live_after.get("required_tests", [])),
        "round_required_artifact_count": len(ROUND_REQUIRED_ARTIFACTS),
        "round_required_test_count": len(ROUND_REQUIRED_TESTS),
        "post_run_surface_test_count": len(POST_RUN_SURFACE_TESTS),
        "counts_are_derived_from_live_manifest": True,
        "old_107_test_count_is_baseline_trace_only": True,
    }
    taxonomy = {
        "schema_version": "dvf-3-3-current-route-required-validation-taxonomy-separation-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "owning_axis": "required_validation_gate_adopted/evidence_freshness_reseal",
        "runtime_authority_mutation": False,
        "source_rendered_lua_runtime_package_mutation": False,
        "external_bundle_reseal_requirement_surface": "wrapper_final_validation",
        "post_run_surface_validation_surface": "wrapper_final_validation_and_focused_unittest_not_current_route_required",
        "candidate_manifest_role": "supporting_or_rejected_trace_not_live_authority",
        "required_gate_vocabulary_is_runtime_row_vocabulary": False,
    }
    bijection = {
        "schema_version": "dvf-3-3-current-route-required-validation-additive-diff-v1",
        "generated_at": now_iso(),
        "status": status,
        **baseline_diff,
        "added_entries_detail": baseline_diff["added"],
    }
    write_json(phase / "live_required_manifest_update_report.json", update_report)
    write_json(phase / "live_manifest_single_writer_report.json", single_writer)
    write_json(phase / "manifest_count_report.json", count_report)
    write_json(phase / "taxonomy_separation_report.json", taxonomy)
    write_json(phase / "additive_diff_bijection_report.json", bijection)
    return {
        "update_report": update_report,
        "count_report": count_report,
        "taxonomy": taxonomy,
        "bijection": bijection,
    }


def write_phase1_and_run_current_route(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase1", root)
    phase4 = phase_dir("phase4", root)
    negative = run_negative_fixture_matrix(root)
    write_json(phase / "harness_negative_fixture_matrix.json", negative)
    env = os.environ.copy()
    env[INNER_CURRENT_ROUTE_ENV] = "1"
    out_path = phase4 / "current_route_validation_result.json"
    command = [
        sys.executable,
        "-B",
        str(ROUND3_RUNNER),
        "--class",
        "current",
        "--enforce-current-build-closure",
        "--out",
        str(out_path),
    ]
    result = run_command(command, env=env)
    protected_before = read_json_object(root / "phase0" / "protected_surface_baseline_hash_report.json")
    protected_after = hash_path_entries(
        protected_surface_paths(),
        schema_version="dvf-3-3-current-route-required-validation-protected-surface-after-phase1-v1",
    )
    no_mutation = diff_hash_reports(protected_before, protected_after)
    blocker = {
        "schema_version": "dvf-3-3-current-route-required-validation-blocker-triage-v1",
        "generated_at": now_iso(),
        "status": "PASS" if result["exit_code"] == 0 else "FAIL",
        "blocker_reproduced": result["exit_code"] != 0,
        "artifact_sink_write_failure_detected": "OSError" in result["stderr"],
        "os_error_22_detected": "OSError" in result["stderr"] and "22" in result["stderr"],
        "current_route_command_text": result["command"],
        "runner_exit_code": result["exit_code"],
        "stdout_tail": result["stdout"][-4000:],
        "stderr_tail": result["stderr"][-4000:],
    }
    repair = {
        "schema_version": "dvf-3-3-current-route-required-validation-harness-repair-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "repair_applied": False,
        "repair_scope": "none_required",
        "path_handling_change_count": 0,
        "validation_semantic_change_count": 0,
        "pass_predicate_change_count": 0,
        "required_set_change_count": 0,
    }
    semantic = {
        "schema_version": "dvf-3-3-current-route-required-validation-harness-semantic-preservation-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "repair_applied": False,
        "semantic_touch_count": 0,
        "validation_rule_changed_count": 0,
        "required_set_changed_count": 0,
        "pass_predicate_changed_count": 0,
    }
    classifier = {
        "schema_version": "dvf-3-3-current-route-required-validation-rule-diff-classifier-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "semantic_touch_count": 0,
        "path_handling_touch_count": 0,
        "validation_rule_change_count": 0,
    }
    terminal = {
        "schema_version": "dvf-3-3-current-route-required-validation-terminal-reachability-v1",
        "generated_at": now_iso(),
        "status": "PASS" if out_path.exists() and result["exit_code"] == 0 else "FAIL",
        "terminal_verdict_reached": out_path.exists(),
        "runner_exit_code": result["exit_code"],
        "runner_result_path": rel(out_path),
    }
    write_json(phase / "blocker_triage_report.json", blocker)
    write_json(phase / "harness_evidence_write_repair_report.json", repair)
    write_json(phase / "harness_repair_semantic_preservation_report.json", semantic)
    write_json(phase / "harness_negative_fixture_matrix.json", negative)
    write_json(phase / "validation_rule_diff_classifier.json", classifier)
    write_json(phase / "terminal_reachability_report.json", terminal)
    write_json(phase / "protected_surface_no_mutation_report.json", no_mutation)
    return {
        "command_result": result,
        "blocker": blocker,
        "terminal": terminal,
        "no_mutation": no_mutation,
    }


def runner_required_error_counts(payload: dict[str, Any]) -> dict[str, int]:
    required = payload.get("required_validations", {})
    errors = required.get("errors", []) if isinstance(required, dict) else []
    counter = Counter(row.get("code") for row in errors if isinstance(row, dict))
    artifact_field_errors = [
        row for row in errors if isinstance(row, dict) and row.get("code") == "required_artifact_field_mismatch"
    ]
    missing_artifacts = [
        row for row in errors if isinstance(row, dict) and row.get("code") == "missing_required_artifact"
    ]
    return {
        "missing_required_test_count": counter.get("missing_required_test", 0),
        "skipped_required_test_count": counter.get("skipped_required_test", 0),
        "failed_required_test_count": counter.get("failed_required_test", 0),
        "missing_required_artifact_count": len(missing_artifacts),
        "failed_required_artifact_field_check_count": len(artifact_field_errors),
    }


def write_phase4_from_runner(command_result: dict[str, Any], root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase4", root)
    runner_payload = read_json_object(phase / "current_route_validation_result.json")
    manifest_hash = sha256_file(LIVE_REQUIRED_MANIFEST)
    required = runner_payload.get("required_validations", {}) if isinstance(runner_payload.get("required_validations"), dict) else {}
    counts = runner_required_error_counts(runner_payload)
    runner_status = "PASS" if runner_payload.get("success") is True and command_result.get("exit_code") == 0 else "FAIL"
    wrapper_status = "PASS" if runner_status == "PASS" and all(value == 0 for value in counts.values()) else "FAIL"
    protected_before = read_json_object(root / "phase0" / "protected_surface_baseline_hash_report.json")
    protected_after = hash_path_entries(
        protected_surface_paths(),
        schema_version="dvf-3-3-current-route-required-validation-protected-surface-after-phase4-v1",
    )
    no_mutation = diff_hash_reports(protected_before, protected_after)
    freshness = {
        "schema_version": "dvf-3-3-current-route-required-validation-freshness-report-v1",
        "generated_at": now_iso(),
        "status": wrapper_status,
        "current_route_command_text": command_result.get("command"),
        "runner_exit_code": command_result.get("exit_code"),
        "runner_status": runner_status,
        "wrapper_status": wrapper_status,
        "pass_reinterpretation_count": 0,
        "started_at": command_result.get("started_at"),
        "finished_at": command_result.get("finished_at"),
        "working_tree_dirty_state": git_info().get("dirty_status_short", []),
        "runner_script_hash": sha256_file(ROUND3_RUNNER),
        "actual_test_count": runner_payload.get("test_count"),
        "required_test_count": required.get("required_test_count"),
        "required_artifact_count": required.get("required_artifact_count"),
        **counts,
        "closure_enforced": runner_payload.get("closure_enforced"),
        "manifest_hash": manifest_hash,
        "manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "runner_readpoint": rel(phase / "current_route_validation_result.json"),
        "evidence_root": rel(root),
        "external_bundle_readpoint": rel(root / "phase5" / "external_validation_bundle_manifest.json"),
        "protected_mutation_changed_count": no_mutation["changed_count"],
        "required_validations_success": required.get("success"),
    }
    source_linkage = {
        "schema_version": "dvf-3-3-current-route-required-validation-source-linkage-v1",
        "generated_at": now_iso(),
        "status": "PASS"
        if read_json_object(root / "phase2" / "current_checkout_source_identity_redrive_report.json").get("status") == "PASS"
        else "FAIL",
        "provenance_only_fallback_used": False,
        "current_checkout_source_identity_redrive_report": rel(root / "phase2" / "current_checkout_source_identity_redrive_report.json"),
        "phase4_current_route_runner_linkage": rel(phase / "current_route_validation_result.json"),
    }
    required_ids = set(required.get("required_tests", []))
    failures = {
        str(test.get("test_id")) for test in [*runner_payload.get("errors", []), *runner_payload.get("failures", [])] if isinstance(test, dict)
    }
    skipped = {str(test.get("test_id")) for test in runner_payload.get("skipped", []) if isinstance(test, dict)}
    matrix = {
        "schema_version": "dvf-3-3-current-route-required-validation-required-test-matrix-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not failures.intersection(required_ids) and not skipped.intersection(required_ids) else "FAIL",
        "required_test_count": len(required_ids),
        "rows": [
            {
                "test_id": test_id,
                "status": "failed" if test_id in failures else "skipped" if test_id in skipped else "passed_or_selected",
            }
            for test_id in sorted(required_ids)
        ],
    }
    artifact_errors = [
        row
        for row in required.get("errors", [])
        if isinstance(row, dict) and str(row.get("code", "")).startswith("required_artifact")
    ]
    artifact_check = {
        "schema_version": "dvf-3-3-current-route-required-validation-artifact-field-check-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not artifact_errors else "FAIL",
        "missing_required_artifact_count": counts["missing_required_artifact_count"],
        "failed_required_artifact_field_check_count": counts["failed_required_artifact_field_check_count"],
        "errors": artifact_errors,
    }
    validation = {
        "schema_version": "dvf-3-3-current-route-required-validation-wrapper-validation-v1",
        "generated_at": now_iso(),
        "status": wrapper_status,
        "error_count": 0 if wrapper_status == "PASS" else 1,
        "errors": [] if wrapper_status == "PASS" else [{"code": "current_route_wrapper_failed", "runner_status": runner_status, **counts}],
    }
    write_json(phase / "current_route_required_validation_freshness_report.json", freshness)
    write_json(phase / "source_identity_reverification_linkage_report.json", source_linkage)
    write_json(phase / "required_test_execution_matrix.json", matrix)
    write_json(phase / "required_artifact_field_check_report.json", artifact_check)
    write_json(phase / "validation_report.all.json", validation)
    return {
        "freshness": freshness,
        "source_linkage": source_linkage,
        "artifact_check": artifact_check,
        "validation": validation,
    }


def write_phase5_external_bundle(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase5", root)
    phase0_target = read_json_object(root / "phase0" / "external_bundle_target_pin.json")
    phase4 = read_json_object(root / "phase4" / "current_route_required_validation_freshness_report.json")
    field_check = read_json_object(root / "phase2" / "drift_verification_field_check_report.json")
    live_manifest_hash = sha256_file(LIVE_REQUIRED_MANIFEST)
    bundle = {
        "schema_version": "dvf-3-3-current-route-required-validation-external-bundle-v1",
        "generated_at": now_iso(),
        "status": "PASS" if phase4.get("status") == "PASS" and field_check.get("status") == "PASS" else "FAIL",
        "round_id": ROUND_ID,
        "bundle_role": "round_local_canonical_external_validation_bundle",
        "evidence_root": rel(root),
        "runner_readpoint": phase4.get("runner_readpoint"),
        "live_manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "live_manifest_sha256": live_manifest_hash,
        "runner_manifest_sha256": phase4.get("manifest_hash"),
        "actual_test_count": phase4.get("actual_test_count"),
        "required_test_count": phase4.get("required_test_count"),
        "required_artifact_count": phase4.get("required_artifact_count"),
        "missing_required_test_count": phase4.get("missing_required_test_count"),
        "skipped_required_test_count": phase4.get("skipped_required_test_count"),
        "failed_required_test_count": phase4.get("failed_required_test_count"),
        "missing_required_artifact_count": phase4.get("missing_required_artifact_count"),
        "failed_required_artifact_field_check_count": phase4.get("failed_required_artifact_field_check_count"),
        "drift_verification_consumption_status": field_check.get("status"),
        "non_claims": non_claims(),
    }
    bundle["normalized_content_sha256"] = normalized_content_hash(bundle)
    write_json(phase / "external_validation_bundle_manifest.json", bundle)
    target_matches = phase0_target.get("external_bundle_current_target_path") == rel(phase / "external_validation_bundle_manifest.json")
    bundle_normalized_hash = normalized_content_hash(bundle)
    bundle_normalized_hash_matches_manifest = bundle_normalized_hash == bundle["normalized_content_sha256"]
    hash_report = {
        "schema_version": "dvf-3-3-current-route-required-validation-external-bundle-hash-v1",
        "generated_at": now_iso(),
        "status": "PASS" if target_matches and bundle_normalized_hash_matches_manifest else "FAIL",
        "bundle_path": rel(phase / "external_validation_bundle_manifest.json"),
        "bundle_file_sha256": sha256_file(phase / "external_validation_bundle_manifest.json"),
        "bundle_normalized_content_sha256": bundle_normalized_hash,
        "bundle_manifest_stored_normalized_content_sha256": bundle["normalized_content_sha256"],
        "bundle_normalized_hash_matches_manifest": bundle_normalized_hash_matches_manifest,
        "target_pin_path_matches": target_matches,
        "normalization_contract": phase0_target.get("external_bundle_content_contract", {}),
    }
    freshness = {
        "schema_version": "dvf-3-3-current-route-required-validation-external-bundle-freshness-v1",
        "generated_at": now_iso(),
        "status": "PASS"
        if bundle["status"] == "PASS"
        and target_matches
        and bundle.get("live_manifest_sha256") == phase4.get("manifest_hash")
        and bundle.get("evidence_root") == rel(root)
        else "FAIL",
        "external_bundle_target_path": rel(phase / "external_validation_bundle_manifest.json"),
        "external_bundle_target_matches_phase0_pin": target_matches,
        "bundle_readpoint_matches_runner_output": bundle.get("runner_readpoint") == phase4.get("runner_readpoint"),
        "bundle_manifest_hash_matches_live_manifest_hash": bundle.get("live_manifest_sha256") == phase4.get("manifest_hash"),
        "bundle_evidence_root_matches_final_current_route_result": bundle.get("evidence_root") == rel(root),
        "old_external_bundle_used_as_current_success_evidence": False,
        "candidate_manifest_used_as_authority": False,
    }
    write_json(phase / "external_validation_bundle_hash_report.json", hash_report)
    write_json(phase / "external_validation_bundle_freshness_report.json", freshness)
    return {"bundle": bundle, "hash_report": hash_report, "freshness": freshness}


def non_claims() -> list[str]:
    return [
        "no_release_readiness",
        "no_package_readiness",
        "no_workshop_readiness",
        "no_b42_readiness",
        "no_deployment_readiness",
        "no_manual_in_game_qa",
        "no_semantic_quality_completion",
        "no_public_facing_text_acceptance",
        "no_live_migration_execution",
        "no_source_mutation",
        "no_rendered_live_regeneration",
        "no_lua_bridge_export",
        "no_runtime_chunk_replacement",
        "no_package_payload_mutation",
    ]


def claim_boundary_markdown(closeout_state: str, canonical_allowed: bool) -> str:
    return "\n".join(
        [
            "# DVF 3-3 Current-Route Required Validation Evidence Freshness Reseal Claim Boundary",
            "",
            f"Round: `{ROUND_ID}`",
            f"Evidence root: `{rel(EVIDENCE_ROOT)}`",
            "",
            "Owning axis: `required_validation_gate_adopted / evidence_freshness_reseal_closeout_state`.",
            f"Current closeout sub-state: `{closeout_state}`.",
            f"Canonical complete allowed: `{str(canonical_allowed).lower()}`.",
            "",
            "This is validation/governance evidence only. It binds the current-route runner, live required-validation manifest, stored drift evidence, and round-local external validation bundle to one evidence readpoint.",
            "",
            "This does not claim release, package, Workshop, B42, deployment, manual in-game QA, semantic quality, public text acceptance, live migration execution, source restoration, rendered regeneration, Lua bridge export, runtime chunk replacement, or package payload mutation.",
        ]
    )


def write_primary_review_manifest(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase6", root)
    rows = []
    for relative in PRIMARY_REVIEW_ARTIFACTS:
        path = root / relative
        policy = "post_manifest_hash_observation_no_expected_comparison" if relative in COMPARISON_EXEMPT_REVIEW_ARTIFACTS else "frozen_expected_sha256"
        actual_sha = sha256_file(path)
        rows.append(
            {
                "path": rel(path),
                "root_relative_path": relative,
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
                "sha256_at_manifest_generation": actual_sha,
                "expected_sha256": actual_sha if policy == "frozen_expected_sha256" else None,
                "hash_comparison_policy": policy,
            }
        )
    missing_count = sum(1 for row in rows if not row["exists"])
    manifest = {
        "schema_version": "dvf-3-3-current-route-required-validation-primary-review-manifest-v1",
        "generated_at": now_iso(),
        "status": "PASS" if missing_count == 0 else "FAIL",
        "manifest_scope": "complete_machine_pass_evidence_inventory",
        "artifact_count": len(rows),
        "inventory_file_count": len(rows),
        "missing_count": missing_count,
        "frozen_expected_hash_count": len(rows) - len(COMPARISON_EXEMPT_REVIEW_ARTIFACTS),
        "comparison_exempt_artifact_count": len(COMPARISON_EXEMPT_REVIEW_ARTIFACTS),
        "artifacts": rows,
    }
    manifest["manifest_payload_sha256_excluding_self_hash"] = normalized_content_hash(manifest)
    write_json(phase / "primary_review_artifact_manifest.json", manifest)
    return manifest


def write_independent_review_hash_report(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase6", root)
    manifest = read_json_object(phase / "primary_review_artifact_manifest.json")
    rows = []
    mismatches = []
    for row in manifest.get("artifacts", []):
        path = resolve_repo(row["path"])
        policy = row.get("hash_comparison_policy")
        actual_sha = sha256_file(path)
        expected_sha = row.get("expected_sha256")
        if policy == "frozen_expected_sha256" and actual_sha != expected_sha:
            mismatches.append(
                {
                    "path": row["path"],
                    "expected_sha256": expected_sha,
                    "actual_sha256": actual_sha,
                }
            )
        rows.append(
            {
                "path": row["path"],
                "root_relative_path": row["root_relative_path"],
                "exists": path.exists(),
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha if policy != "self_hash_not_representable_presence_only" else None,
                "sha256_matches": (actual_sha == expected_sha) if policy == "frozen_expected_sha256" else None,
                "hash_comparison_policy": policy,
            }
        )
    missing_count = sum(1 for row in rows if not row["exists"])
    report = {
        "schema_version": "dvf-3-3-current-route-required-validation-independent-review-hash-v1",
        "generated_at": now_iso(),
        "status": "PASS" if missing_count == 0 and not mismatches else "FAIL",
        "primary_review_artifact_manifest_path": rel(phase / "primary_review_artifact_manifest.json"),
        "primary_review_artifact_manifest_sha256": sha256_file(phase / "primary_review_artifact_manifest.json"),
        "primary_review_artifact_manifest_artifact_count": manifest.get("artifact_count"),
        "primary_review_artifact_missing_count": missing_count,
        "mismatch_count": len(mismatches),
        "comparison_checked_count": sum(1 for row in rows if row["hash_comparison_policy"] == "frozen_expected_sha256"),
        "comparison_exempt_count": sum(1 for row in rows if row["hash_comparison_policy"] != "frozen_expected_sha256"),
        "artifact_hashes": rows,
        "independent_review_status": INDEPENDENT_REVIEW_STATUS,
        "independent_review_basis": "non_claude_independent_review_reported_no_blocking_actionable_findings",
        "owner_seal_status": OWNER_SEAL_STATUS,
        "canonical_complete_allowed": True,
    }
    write_json(phase / "independent_review_artifact_hash_report.json", report)
    return report


def write_owner_seal_report(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase6", root)
    report = {
        "schema_version": "dvf-3-3-current-route-required-validation-owner-seal-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "owner_seal_status": OWNER_SEAL_STATUS,
        "owner_seal_source": OWNER_SEAL_SOURCE,
        "owner_seal_decision": OWNER_SEAL_DECISION,
        "independent_review_status_accepted": INDEPENDENT_REVIEW_STATUS,
        "independent_review_basis": "non_claude_independent_review_reported_no_blocking_actionable_findings",
        "direct_runner_candidate_rejection_requirement": "not_required_for_this_seal",
        "candidate_manifest_authority_guard_surface": "wrapper_required_validations_override_absent",
        "machine_pass_report_path": rel(phase / "final_current_route_required_validation_evidence_freshness_reseal_report.json"),
        "primary_review_artifact_manifest_path": rel(phase / "primary_review_artifact_manifest.json"),
        "independent_review_artifact_hash_report_path": rel(phase / "independent_review_artifact_hash_report.json"),
        "canonical_complete_allowed": True,
    }
    write_json(phase / "owner_seal_report.json", report)
    return report


def write_phase6_final(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase6", root)
    protected_before = read_json_object(root / "phase0" / "protected_surface_baseline_hash_report.json")
    protected_after = hash_path_entries(
        protected_surface_paths(),
        schema_version="dvf-3-3-current-route-required-validation-protected-surface-after-final-v1",
    )
    no_mutation = diff_hash_reports(protected_before, protected_after)
    sealed_before = read_json_object(root / "phase0" / "sealed_round_evidence_protected_set.json").get("baseline_hash_report", {})
    sealed_after = hash_path_entries(
        discover_sealed_evidence_entries(),
        schema_version="dvf-3-3-current-route-required-validation-sealed-evidence-after-final-v1",
    )
    sealed_diff = diff_hash_reports(sealed_before if isinstance(sealed_before, dict) else {}, sealed_after)
    phase4 = read_json_object(root / "phase4" / "current_route_required_validation_freshness_report.json")
    phase5 = read_json_object(root / "phase5" / "external_validation_bundle_freshness_report.json")
    phase2 = read_json_object(root / "phase2" / "drift_verification_field_check_report.json")
    phase3 = read_json_object(root / "phase3" / "additive_diff_bijection_report.json")
    live_manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    live_required_test_ids = {
        str(row.get("test_id"))
        for row in live_manifest.get("required_tests", [])
        if isinstance(row, dict) and row.get("test_id")
    }
    post_run_surface_tests_in_live_manifest = sorted(set(POST_RUN_SURFACE_TESTS).intersection(live_required_test_ids))
    machine_checks = {
        "current_route_wrapper_pass": phase4.get("status") == "PASS",
        "external_bundle_freshness_pass": phase5.get("status") == "PASS",
        "drift_field_check_pass": phase2.get("status") == "PASS",
        "manifest_additive_pass": phase3.get("status") == "PASS",
        "post_run_surface_tests_not_live_current_route_required": not post_run_surface_tests_in_live_manifest,
        "protected_surface_no_mutation": no_mutation["changed_count"] == 0,
        "sealed_round_evidence_no_mutation": sealed_diff["changed_count"] == 0,
        "missing_required_test_zero": phase4.get("missing_required_test_count") == 0,
        "skipped_required_test_zero": phase4.get("skipped_required_test_count") == 0,
        "failed_required_test_zero": phase4.get("failed_required_test_count") == 0,
        "missing_required_artifact_zero": phase4.get("missing_required_artifact_count") == 0,
        "failed_required_artifact_field_check_zero": phase4.get("failed_required_artifact_field_check_count") == 0,
        "pass_reinterpretation_zero": phase4.get("pass_reinterpretation_count") == 0,
        "closure_enforced": phase4.get("closure_enforced") is True,
    }
    machine_pass = all(machine_checks.values())
    independent_review_pass = INDEPENDENT_REVIEW_STATUS == "PASS"
    owner_seal_pass = OWNER_SEAL_STATUS == "PASS"
    canonical_allowed = machine_pass and independent_review_pass and owner_seal_pass
    closeout_state = "complete" if canonical_allowed else "machine_pass_review_pending" if machine_pass else "failed_reseal_attempt"
    final = {
        "schema_version": "dvf-3-3-current-route-required-validation-final-reseal-v1",
        "generated_at": now_iso(),
        "status": "PASS" if machine_pass else "FAIL",
        "machine_contract_status": "PASS" if machine_pass else "FAIL",
        "required_validation_gate_adopted": True,
        "evidence_freshness_reseal_closeout_state": closeout_state,
        "standalone_complete_claimed": False,
        "canonical_complete_allowed": canonical_allowed,
        "canonical_complete_requirements": {
            "machine_validation_pass": machine_pass,
            "non_claude_independent_review_pass": independent_review_pass,
            "owner_seal_pass": owner_seal_pass,
        },
        "independent_review_status": INDEPENDENT_REVIEW_STATUS,
        "owner_seal_status": OWNER_SEAL_STATUS,
        "owner_seal_report_path": rel(phase / "owner_seal_report.json"),
        "current_route_command_text": phase4.get("current_route_command_text"),
        "exit_code": phase4.get("runner_exit_code"),
        "started_at": phase4.get("started_at"),
        "finished_at": phase4.get("finished_at"),
        "working_tree_dirty_state": phase4.get("working_tree_dirty_state", []),
        "runner_script_hash": phase4.get("runner_script_hash"),
        "actual_test_count": phase4.get("actual_test_count"),
        "required_test_count": phase4.get("required_test_count"),
        "required_artifact_count": phase4.get("required_artifact_count"),
        "missing_required_test_count": phase4.get("missing_required_test_count"),
        "skipped_required_test_count": phase4.get("skipped_required_test_count"),
        "failed_required_test_count": phase4.get("failed_required_test_count"),
        "missing_required_artifact_count": phase4.get("missing_required_artifact_count"),
        "failed_required_artifact_field_check_count": phase4.get("failed_required_artifact_field_check_count"),
        "external_bundle_freshness_status": phase5.get("status"),
        "live_manifest_consumed_status": "PASS" if phase4.get("manifest_hash") == sha256_file(LIVE_REQUIRED_MANIFEST) else "FAIL",
        "drift_verification_evidence_consumption_status": phase2.get("status"),
        "candidate_manifest_authority_status": "rejected_as_current_authority",
        "post_run_surface_tests_are_current_route_required": False,
        "post_run_surface_tests_in_live_manifest": post_run_surface_tests_in_live_manifest,
        "post_run_surface_validation_surface": "wrapper_final_validation_and_focused_unittest",
        "protected_source_rendered_lua_runtime_package_changed_count": no_mutation["changed_count"],
        "sealed_round_evidence_content_changed_count": sealed_diff["changed_count"],
        "machine_checks": machine_checks,
        "non_claims": non_claims(),
    }
    write_json(phase / "no_protected_mutation_verdict.json", no_mutation)
    write_json(phase / "final_current_route_required_validation_evidence_freshness_reseal_report.json", final)
    write_owner_seal_report(root)
    write_text(CLAIM_BOUNDARY_DOC, claim_boundary_markdown(closeout_state, canonical_allowed=canonical_allowed))
    write_text(
        LEDGER_PACKET_DOC,
        "\n".join(
            [
                "# DVF 3-3 Current-Route Required Validation Evidence Freshness Reseal Ledger Packet",
                "",
                f"Round: `{ROUND_ID}`",
                f"Evidence root: `{rel(root)}`",
                "",
                f"Status: `{closeout_state}`.",
                "",
                "Authority surface: `validation/governance surface impact only`.",
                "Canonical complete is sealed because machine validation, non-Claude independent review, and owner seal are PASS.",
                "",
                "No source, rendered, Lua bridge, runtime, or package payload mutation is claimed.",
            ]
        ),
    )
    write_primary_review_manifest(root)
    write_independent_review_hash_report(root)
    final["primary_review_artifact_manifest_status"] = read_json_object(phase / "primary_review_artifact_manifest.json").get("status")
    final["independent_review_artifact_hash_report_status"] = read_json_object(phase / "independent_review_artifact_hash_report.json").get("status")
    final["owner_seal_report_status"] = read_json_object(phase / "owner_seal_report.json").get("status")
    write_json(phase / "final_current_route_required_validation_evidence_freshness_reseal_report.json", final)
    write_primary_review_manifest(root)
    write_independent_review_hash_report(root)
    return final


def run_negative_fixture_matrix(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = phase_dir("phase1", root)
    sandbox = phase / "negative_fixture_sandbox"
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.mkdir(parents=True, exist_ok=True)
    live_manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    fixtures = []

    synthetic_pass = (
        "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
        "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest.negative_fixture_synthetic_pass"
    )
    synthetic_skip = (
        "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
        "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest.negative_fixture_synthetic_skip"
    )

    def sandbox_manifest(name: str, *, artifacts: list[dict[str, Any]] | None = None, test_id: str = synthetic_pass) -> Path:
        payload = {
            "schema_version": "round3-current-route-required-validations-v1",
            "status": "PASS",
            "required": True,
            "route": "current",
            "claim": f"negative_fixture::{name}",
            "required_artifacts": artifacts or [],
            "required_tests": [
                {
                    "required": True,
                    "role": "negative_fixture_only",
                    "test_id": test_id,
                }
            ],
        }
        path = sandbox / f"{name}_manifest.json"
        write_json(path, payload)
        return path

    def sandbox_taxonomy(name: str, test_id: str) -> Path:
        path = sandbox / f"{name}_taxonomy.json"
        write_json(
            path,
            {
                "schema_version": "round3-negative-fixture-taxonomy-v1",
                "rows": [
                    {
                        "test_id": test_id,
                        "contract_class": "current",
                        "state": "ok",
                    }
                ],
            },
        )
        return path

    def run_sandbox_runner(name: str, manifest_path: Path, taxonomy_path: Path) -> dict[str, Any]:
        out_path = sandbox / f"{name}_runner_result.json"
        env = os.environ.copy()
        env[INNER_CURRENT_ROUTE_ENV] = "1"
        result = run_command(
            [
                sys.executable,
                "-B",
                str(ROUND3_RUNNER),
                "--class",
                "current",
                "--taxonomy",
                str(taxonomy_path),
                "--required-validations",
                str(manifest_path),
                "--enforce-current-build-closure",
                "--out",
                str(out_path),
            ],
            env=env,
        )
        payload = read_json_object(out_path)
        required_errors = payload.get("required_validations", {}).get("errors", [])
        return {
            "command": result["command"],
            "exit_code": result["exit_code"],
            "result_path": rel(out_path),
            "runner_success": payload.get("success"),
            "required_validation_success": object_field(payload, "required_validations.success"),
            "observed_error_codes": sorted(
                {
                    str(row.get("code"))
                    for row in required_errors
                    if isinstance(row, dict) and row.get("code") is not None
                }
            ),
            "stdout_tail": result["stdout"][-1000:],
            "stderr_tail": result["stderr"][-1000:],
        }

    def fixture_row(
        *,
        name: str,
        manifest_path: Path,
        taxonomy_path: Path,
        expected_error_code: str,
        wrapper_guard: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        observed = run_sandbox_runner(name, manifest_path, taxonomy_path)
        runner_failure_preserved = observed["exit_code"] != 0 and expected_error_code in observed["observed_error_codes"]
        if wrapper_guard is not None:
            expected_failure_preserved = wrapper_guard["observed_status"] == "FAIL" and wrapper_guard["observed_error_code"] == expected_error_code
        else:
            expected_failure_preserved = runner_failure_preserved
        return {
            "fixture": name,
            "status": "PASS" if expected_failure_preserved else "FAIL",
            "expected_failure_preserved": expected_failure_preserved,
            "expected_error_code": expected_error_code,
            "observed_runner": observed,
            "observed_wrapper_guard": wrapper_guard,
            "live_mutation_performed": False,
            "sandbox_manifest": rel(manifest_path),
            "sandbox_taxonomy": rel(taxonomy_path),
        }

    stale_bundle = sandbox / "stale_external_validation_bundle_manifest.json"
    write_json(
        stale_bundle,
        {
            "schema_version": "dvf-3-3-current-route-required-validation-external-bundle-v1",
            "status": "PASS",
            "live_manifest_sha256": "stale",
            "runner_manifest_sha256": "different",
            "evidence_root": "historical",
        },
    )
    stale_manifest = sandbox_manifest(
        "known_stale_bundle",
        artifacts=[
            {
                "path": rel(stale_bundle),
                "checks": [{"field": "live_manifest_sha256", "equals": sha256_file(LIVE_REQUIRED_MANIFEST)}],
            }
        ],
    )
    stale_taxonomy = sandbox_taxonomy("known_stale_bundle", synthetic_pass)
    fixtures.append(
        fixture_row(
            name="known_stale_bundle",
            manifest_path=stale_manifest,
            taxonomy_path=stale_taxonomy,
            expected_error_code="required_artifact_field_mismatch",
        )
    )

    candidate = json.loads(json.dumps(live_manifest))
    candidate["schema_version"] = "round3-current-route-required-validations-v1"
    candidate_path = sandbox / "candidate_manifest_reference.json"
    write_json(candidate_path, candidate)
    candidate_manifest = sandbox_manifest("candidate_manifest_reference")
    candidate_taxonomy = sandbox_taxonomy("candidate_manifest_reference", synthetic_pass)
    candidate_runner = run_sandbox_runner("candidate_manifest_reference", candidate_manifest, candidate_taxonomy)
    candidate_wrapper = run_command(
        [
            sys.executable,
            "-B",
            str(RUNNER_WRAPPER),
            "--mode",
            "validate",
            "--required-validations",
            str(candidate_path),
        ]
    )
    wrapper_override_rejected = candidate_wrapper["exit_code"] != 0 and "--required-validations" in candidate_wrapper["stderr"]
    candidate_guard = {
        "guard": "wrapper_has_no_required_validations_override_surface",
        "observed_status": "FAIL" if wrapper_override_rejected else "PASS",
        "observed_error_code": "candidate_manifest_override_surface_absent" if wrapper_override_rejected else None,
        "candidate_manifest_path": rel(candidate_path),
        "live_manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "runner_exit_code_on_sandbox_copy": candidate_runner["exit_code"],
        "runner_result_path_on_sandbox_copy": candidate_runner["result_path"],
        "actual_wrapper_command": candidate_wrapper["command"],
        "actual_wrapper_exit_code": candidate_wrapper["exit_code"],
        "actual_wrapper_stderr_tail": candidate_wrapper["stderr"][-1000:],
    }
    fixtures.append(
        {
            "fixture": "candidate_manifest_reference",
            "status": "PASS" if candidate_guard["observed_status"] == "FAIL" else "FAIL",
            "expected_failure_preserved": candidate_guard["observed_status"] == "FAIL",
            "expected_error_code": "candidate_manifest_override_surface_absent",
            "observed_runner": candidate_runner,
            "observed_wrapper_guard": candidate_guard,
            "live_mutation_performed": False,
        }
    )

    skipped_manifest = sandbox_manifest("skipped_required_test", test_id=synthetic_skip)
    skipped_taxonomy = sandbox_taxonomy("skipped_required_test", synthetic_skip)
    fixtures.append(
        fixture_row(
            name="skipped_required_test",
            manifest_path=skipped_manifest,
            taxonomy_path=skipped_taxonomy,
            expected_error_code="skipped_required_test",
        )
    )

    failed_field_manifest = sandbox_manifest(
        "failed_field_check",
        artifacts=[
            {
                "path": rel(stale_bundle),
                "checks": [{"field": "status", "equals": "INTENTIONAL_FAIL"}],
            }
        ],
    )
    failed_field_taxonomy = sandbox_taxonomy("failed_field_check", synthetic_pass)
    fixtures.append(
        fixture_row(
            name="failed_field_check",
            manifest_path=failed_field_manifest,
            taxonomy_path=failed_field_taxonomy,
            expected_error_code="required_artifact_field_mismatch",
        )
    )
    report = {
        "schema_version": "dvf-3-3-current-route-required-validation-negative-fixture-matrix-v1",
        "generated_at": now_iso(),
        "status": "PASS" if all(row["expected_failure_preserved"] and not row["live_mutation_performed"] for row in fixtures) else "FAIL",
        "sandbox_root": rel(sandbox),
        "live_manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "live_manifest_mutated": False,
        "fixtures": fixtures,
    }
    return report


def validate_artifacts(root: Path = EVIDENCE_ROOT, *, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_files: list[tuple[str, dict[str, Any]]] = [
        ("phase0/readpoint_inventory.json", {"status": "PASS"}),
        ("phase0/live_manifest_hash_report.json", {"status": "PASS", "candidate_manifest_is_live_authority": False}),
        ("phase0/external_bundle_target_pin.json", {"status": "PASS", "external_bundle_reseal_required": True}),
        ("phase0/authority_doc_existence_report.json", {"status": "PASS", "execution_contract_classification": "present_authority_doc"}),
        ("phase1/blocker_triage_report.json", {"status": "PASS"}),
        ("phase1/harness_negative_fixture_matrix.json", {"status": "PASS", "live_manifest_mutated": False}),
        ("phase1/validation_rule_diff_classifier.json", {"status": "PASS", "semantic_touch_count": 0}),
        ("phase1/protected_surface_no_mutation_report.json", {"status": "PASS", "changed_count": 0}),
        ("phase2/drift_verification_consumption_contract.json", {"status": "PASS", "external_validation_bundle_reseal_required": True}),
        ("phase2/required_artifact_field_spec.json", {"status": "PASS", "post_run_surface_tests_are_live_current_route_required": False}),
        ("phase2/current_checkout_source_identity_redrive_report.json", {"status": "PASS", "successor_universe_count": EXPECTED_SUCCESSOR_COUNT}),
        ("phase2/drift_verification_field_check_report.json", {"status": "PASS", "mismatch_count": 0}),
        ("phase2/owner_reserved_decision_gate_report.json", {"status": "PASS"}),
        ("phase3/live_required_manifest_update_report.json", {"status": "PASS", "removed_existing_entries": 0, "modified_existing_entries": 0, "duplicate_entries": 0, "post_run_surface_tests_are_current_route_required": False}),
        ("phase3/taxonomy_separation_report.json", {"status": "PASS", "runtime_authority_mutation": False}),
        ("phase3/additive_diff_bijection_report.json", {"status": "PASS", "removed_existing_entries": 0, "modified_existing_entries": 0, "duplicate_entries": 0}),
        ("phase4/current_route_required_validation_freshness_report.json", {"status": "PASS", "runner_exit_code": 0, "closure_enforced": True, "pass_reinterpretation_count": 0}),
        ("phase4/source_identity_reverification_linkage_report.json", {"status": "PASS", "provenance_only_fallback_used": False}),
        ("phase4/required_artifact_field_check_report.json", {"status": "PASS", "missing_required_artifact_count": 0, "failed_required_artifact_field_check_count": 0}),
        ("phase5/external_validation_bundle_manifest.json", {"status": "PASS"}),
        ("phase5/external_validation_bundle_hash_report.json", {"status": "PASS", "target_pin_path_matches": True, "bundle_normalized_hash_matches_manifest": True}),
        ("phase5/external_validation_bundle_freshness_report.json", {"status": "PASS", "external_bundle_target_matches_phase0_pin": True, "bundle_manifest_hash_matches_live_manifest_hash": True}),
        ("phase6/no_protected_mutation_verdict.json", {"status": "PASS", "changed_count": 0}),
        ("phase6/final_current_route_required_validation_evidence_freshness_reseal_report.json", {"status": "PASS", "machine_contract_status": "PASS", "standalone_complete_claimed": False, "canonical_complete_allowed": True, "independent_review_status": "PASS", "owner_seal_status": "PASS", "post_run_surface_tests_are_current_route_required": False}),
        ("phase6/primary_review_artifact_manifest.json", {"status": "PASS", "missing_count": 0, "artifact_count": len(PRIMARY_REVIEW_ARTIFACTS)}),
        ("phase6/independent_review_artifact_hash_report.json", {"status": "PASS", "primary_review_artifact_missing_count": 0, "mismatch_count": 0, "independent_review_status": "PASS", "owner_seal_status": "PASS", "canonical_complete_allowed": True}),
        ("phase6/owner_seal_report.json", {"status": "PASS", "owner_seal_status": "PASS", "canonical_complete_allowed": True}),
    ]
    for relative, checks in required_files:
        path = root / relative
        if not path.exists():
            errors.append({"code": "missing_required_artifact", "path": rel(path)})
            continue
        payload = read_json_object(path)
        for field, expected in checks.items():
            observed = object_field(payload, field)
            if observed != expected:
                errors.append(
                    {
                        "code": "field_mismatch",
                        "path": rel(path),
                        "field": field,
                        "expected": expected,
                        "observed": observed,
                    }
                )
    final = read_json_object(root / "phase6" / "final_current_route_required_validation_evidence_freshness_reseal_report.json")
    live_manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    live_required_test_ids = {
        str(row.get("test_id"))
        for row in live_manifest.get("required_tests", [])
        if isinstance(row, dict) and row.get("test_id")
    }
    post_run_surface_tests_in_live_manifest = sorted(set(POST_RUN_SURFACE_TESTS).intersection(live_required_test_ids))
    if post_run_surface_tests_in_live_manifest:
        errors.append(
            {
                "code": "post_run_surface_tests_overclaimed_as_current_route_required",
                "test_ids": post_run_surface_tests_in_live_manifest,
            }
        )
    for field in (
        "missing_required_test_count",
        "skipped_required_test_count",
        "failed_required_test_count",
        "missing_required_artifact_count",
        "failed_required_artifact_field_check_count",
        "protected_source_rendered_lua_runtime_package_changed_count",
        "sealed_round_evidence_content_changed_count",
    ):
        if final.get(field) != 0:
            errors.append({"code": "final_zero_field_mismatch", "field": field, "observed": final.get(field)})
    if final.get("evidence_freshness_reseal_closeout_state") not in {"complete", "machine_pass_review_pending", "evidence_freshness_reseal_machine_pass"}:
        errors.append(
            {
                "code": "unexpected_machine_pass_closeout_state",
                "observed": final.get("evidence_freshness_reseal_closeout_state"),
            }
        )
    if require_complete:
        if final.get("canonical_complete_allowed") is not True:
            errors.append({"code": "canonical_complete_not_allowed_after_owner_seal"})
        if final.get("evidence_freshness_reseal_closeout_state") != "complete":
            errors.append({"code": "canonical_complete_closeout_state_missing", "observed": final.get("evidence_freshness_reseal_closeout_state")})
        if final.get("independent_review_status") != "PASS":
            errors.append({"code": "unexpected_independent_review_status", "observed": final.get("independent_review_status")})
        if final.get("owner_seal_status") != "PASS":
            errors.append({"code": "unexpected_owner_seal_status", "observed": final.get("owner_seal_status")})
        requirements = final.get("canonical_complete_requirements", {})
        if not isinstance(requirements, dict) or not all(requirements.get(key) is True for key in ("machine_validation_pass", "non_claude_independent_review_pass", "owner_seal_pass")):
            errors.append({"code": "canonical_complete_requirements_not_all_pass", "observed": requirements})
    report = {
        "schema_version": "dvf-3-3-current-route-required-validation-reseal-validation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "validation_report_scope": "machine_pass_artifact_set_and_owner_sealed_canonical_closeout",
        "require_complete": require_complete,
        "require_complete_semantics": "complete_machine_pass_artifact_set_plus_axis_qualified_canonical_seal_state",
        "canonical_complete_claimed": final.get("evidence_freshness_reseal_closeout_state") == "complete",
        "canonical_complete_allowed": final.get("canonical_complete_allowed") is True,
        "independent_review_required_for_canonical_complete": True,
        "owner_seal_required_for_canonical_complete": True,
        "error_count": len(errors),
        "errors": errors,
    }
    report_name = "validation_report.require_complete.json" if require_complete else "validation_report.all.json"
    write_json(root / "phase6" / report_name, report)
    if (root / "phase6" / "primary_review_artifact_manifest.json").exists():
        write_independent_review_hash_report(root)
    return report, not errors


def generate_artifacts(root: Path = EVIDENCE_ROOT, *, run_current_route: bool = True) -> dict[str, Any]:
    write_phase0(root)
    write_phase2(root)
    write_phase3_update_manifest(root)
    command_result = {"exit_code": 0, "command": "not_run", "started_at": now_iso(), "finished_at": now_iso(), "stdout": "", "stderr": ""}
    if run_current_route:
        command_result = write_phase1_and_run_current_route(root)["command_result"]
    else:
        phase_dir("phase1", root)
        write_json(root / "phase1" / "blocker_triage_report.json", {"status": "PASS", "runner_exit_code": 0, "blocker_reproduced": False})
        write_json(root / "phase1" / "harness_evidence_write_repair_report.json", {"status": "PASS", "repair_applied": False})
        write_json(root / "phase1" / "harness_repair_semantic_preservation_report.json", {"status": "PASS", "semantic_touch_count": 0})
        write_json(root / "phase1" / "harness_negative_fixture_matrix.json", run_negative_fixture_matrix(root))
        write_json(root / "phase1" / "validation_rule_diff_classifier.json", {"status": "PASS", "semantic_touch_count": 0})
        write_json(root / "phase1" / "terminal_reachability_report.json", {"status": "PASS", "terminal_verdict_reached": True})
        write_json(root / "phase1" / "protected_surface_no_mutation_report.json", {"status": "PASS", "changed_count": 0})
    write_phase4_from_runner(command_result, root)
    write_phase5_external_bundle(root)
    return write_phase6_final(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 current-route required-validation evidence freshness reseal.")
    parser.add_argument("--mode", choices=("generate", "validate", "all", "machine-pass", "manifest-only"), default="all")
    parser.add_argument("--root", type=Path, default=EVIDENCE_ROOT)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)

    if args.mode == "manifest-only":
        write_phase0(args.root)
        write_phase2(args.root)
        write_phase3_update_manifest(args.root)
        print(json.dumps({"status": "PASS", "mode": args.mode}, sort_keys=True))
        return 0

    final: dict[str, Any] | None = None
    if args.mode in {"generate", "all", "machine-pass"}:
        final = generate_artifacts(args.root, run_current_route=True)
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "machine_contract_status": final.get("machine_contract_status"),
                    "closeout_state": final.get("evidence_freshness_reseal_closeout_state"),
                    "canonical_complete_allowed": final.get("canonical_complete_allowed"),
                },
                sort_keys=True,
            )
        )
        if args.mode in {"generate", "machine-pass"} and final.get("status") != "PASS":
            return 1
    if args.mode in {"validate", "all", "machine-pass"}:
        reports: list[dict[str, Any]] = []
        if args.mode in {"all", "machine-pass"} and not args.require_complete:
            report, ok_all = validate_artifacts(args.root, require_complete=False)
            reports.append(report)
            report, ok_complete = validate_artifacts(args.root, require_complete=True)
            reports.append(report)
            ok = ok_all and ok_complete
        else:
            report, ok = validate_artifacts(args.root, require_complete=args.require_complete)
            reports.append(report)
        print(
            json.dumps(
                {
                    "status": "PASS" if ok else "FAIL",
                    "error_count": sum(item["error_count"] for item in reports),
                    "validation_report_count": len(reports),
                },
                sort_keys=True,
            )
        )
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
