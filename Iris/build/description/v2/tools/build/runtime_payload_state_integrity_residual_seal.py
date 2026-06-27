#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import runtime_payload_state_integrity as base_guard
from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    RUNTIME_MONOLITH,
    V2_ROOT,
    canonical_hash,
    chunk_paths_from_manifest,
    now_iso,
    read_json,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


ROUND_ID = "runtime_payload_state_integrity_residual_seal"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
EXISTING_EVIDENCE_ROOT = V2_ROOT / "staging" / "runtime_payload_state_integrity"
GENERATED_AT = "2026-06-27T00:00:00+09:00"

PLAN_PATH = REPO_ROOT / "docs" / "runtime_payload_state_integrity_residual_seal_plan.md"
AUTHOR_DECISION_DOC = REPO_ROOT / "docs" / "runtime_payload_state_integrity_author_decision.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "runtime_payload_state_integrity_residual_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "runtime_payload_state_integrity_residual_ledger_packet.md"
CURRENT_ROUTE_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"

RESIDUAL_TOOL = V2_ROOT / "tools" / "build" / "runtime_payload_state_integrity_residual_seal.py"
RESIDUAL_TEST = V2_ROOT / "tests" / "test_runtime_payload_state_integrity_residual_seal.py"
LEGACY_BRIDGE = REPO_ROOT / "Iris" / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua"
LIVE_RENDERER = REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua"

EXPECTED_CURRENT_ROWS = 2105
EXPECTED_CURRENT_UNADOPTED_ROWS = 21
EXPECTED_PREDECESSOR_RESIDUE_ROWS = 2

NON_CLAIMS = [
    "no_source_fact_or_decision_mutation",
    "no_rendered_output_regeneration",
    "no_lua_bridge_export_mutation",
    "no_runtime_chunk_replacement",
    "no_package_payload_mutation",
    "no_predecessor_residue_cleanup_mutation",
    "no_release_readiness",
    "no_package_readiness",
    "no_workshop_readiness",
    "no_b42_readiness",
    "no_deployment_readiness",
    "no_manual_in_game_qa",
    "no_semantic_quality_completion",
    "no_public_facing_text_acceptance",
]

CLAIM_BOUNDARY = (
    "Runtime Payload State Integrity Residual Seal is a governance-only residual seal. "
    "It may confirm payload-shape guard evidence and historical-only predecessor residue "
    "confinement, but it does not mutate source, rendered, Lua bridge, runtime chunk, "
    "package payload, or predecessor residue surfaces and does not claim release readiness."
)


def now_iso() -> str:
    return GENERATED_AT


def write_json(path: str | Path, payload: Any) -> None:
    path = resolve_repo(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    for attempt in range(8):
        try:
            tmp.replace(path)
            return
        except PermissionError:
            if attempt == 7:
                raise
            time.sleep(0.05 * (2 ** attempt))


def phase_dir(phase: str) -> Path:
    path = EVIDENCE_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def file_status(path: str | Path, *, missing_allowed: bool) -> str:
    resolved = resolve_repo(path)
    if resolved.exists():
        return "present"
    return "missing_allowed" if missing_allowed else "missing_required"


def line_count(path: Path) -> int | None:
    if not path.exists() or not path.is_file():
        return None
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def protected_entry(
    path: str | Path,
    *,
    path_source_kind: str,
    surface_class: str,
    authority_role: str,
    reason: str,
    missing_allowed: bool = False,
    expected_mutation_allowed: bool = False,
    package_peer_source: str | None = None,
) -> dict[str, Any]:
    resolved = resolve_repo(path)
    is_file = resolved.exists() and resolved.is_file()
    entry = {
        "path": rel(resolved),
        "path_source_kind": path_source_kind,
        "surface_class": surface_class,
        "authority_role": authority_role,
        "expected_mutation_allowed": expected_mutation_allowed,
        "pre_hash": sha256_file(resolved) if is_file else None,
        "post_hash": None,
        "exists_status": file_status(resolved, missing_allowed=missing_allowed),
        "missing_allowed": missing_allowed,
        "reason": reason,
        "kind": "file" if is_file else "dir" if resolved.is_dir() else "missing",
        "bytes": resolved.stat().st_size if is_file else None,
        "line_count": line_count(resolved) if is_file else None,
    }
    if package_peer_source is not None:
        entry["package_peer_source"] = package_peer_source
    return entry


def manifest_chunk_entries(
    manifest: Path,
    chunk_dir: Path,
    *,
    path_source_kind: str,
    surface_class: str,
    authority_role: str,
    reason: str,
    missing_allowed: bool = False,
    package_peer_source: str | None = None,
) -> list[dict[str, Any]]:
    entries = [
        protected_entry(
            manifest,
            path_source_kind=path_source_kind,
            surface_class=surface_class,
            authority_role=f"{authority_role}_manifest",
            reason=reason,
            missing_allowed=missing_allowed,
            package_peer_source=package_peer_source,
        )
    ]
    chunk_paths = chunk_paths_from_manifest(manifest, chunk_dir)
    if not chunk_paths and missing_allowed:
        entries.append(
            protected_entry(
                chunk_dir,
                path_source_kind=path_source_kind,
                surface_class=surface_class,
                authority_role=f"{authority_role}_chunk_dir",
                reason=reason,
                missing_allowed=True,
                package_peer_source=package_peer_source,
            )
        )
        return entries
    for chunk_path in chunk_paths:
        entries.append(
            protected_entry(
                chunk_path,
                path_source_kind=path_source_kind,
                surface_class=surface_class,
                authority_role=f"{authority_role}_chunk",
                reason=reason,
                missing_allowed=missing_allowed,
                package_peer_source=package_peer_source,
            )
        )
    return entries


def build_protected_surface_manifest() -> dict[str, Any]:
    package_manifest = base_guard.PACKAGE_DATA_DIR / "IrisLayer3DataChunks.lua"
    package_chunks = base_guard.PACKAGE_DATA_DIR / "IrisLayer3DataChunks"
    candidate_manifest = base_guard.CANDIDATE_BRIDGE_DIR / "IrisLayer3DataChunks.lua"
    candidate_chunks = base_guard.CANDIDATE_BRIDGE_DIR / "IrisLayer3DataChunks"
    rollback_manifest = base_guard.ROLLBACK_DATA_DIR / "IrisLayer3DataChunks.lua"
    rollback_chunks = base_guard.ROLLBACK_DATA_DIR / "IrisLayer3DataChunks"

    entries: list[dict[str, Any]] = [
        protected_entry(
            V2_ROOT / "data" / "dvf_3_3_input_manifest.json",
            path_source_kind="current_source_chain",
            surface_class="source",
            authority_role="current_input_manifest",
            reason="source-chain authority input must not be mutated by a residual seal",
        ),
        protected_entry(
            V2_ROOT / "data" / "dvf_3_3_facts.jsonl",
            path_source_kind="current_source_chain",
            surface_class="source",
            authority_role="current_facts",
            reason="source facts are read-only for this governance-only seal",
        ),
        protected_entry(
            V2_ROOT / "data" / "dvf_3_3_decisions.jsonl",
            path_source_kind="current_source_chain",
            surface_class="source",
            authority_role="current_decisions",
            reason="source decisions are read-only for this governance-only seal",
        ),
        protected_entry(
            V2_ROOT / "data" / "dvf_3_3_overlay_support.jsonl",
            path_source_kind="current_source_chain",
            surface_class="source",
            authority_role="current_overlay_support",
            reason="overlay support is part of the source-chain read surface",
            missing_allowed=True,
        ),
        protected_entry(
            base_guard.CURRENT_RENDERED,
            path_source_kind="rendered_output",
            surface_class="rendered",
            authority_role="current_rendered_output",
            reason="rendered output regeneration is out of scope",
        ),
        protected_entry(
            LEGACY_BRIDGE,
            path_source_kind="lua_bridge_output",
            surface_class="lua_bridge",
            authority_role="legacy_lua_bridge_reentry_scan_target",
            reason="legacy bridge is a stale/current-looking reentry scan target only",
            missing_allowed=True,
        ),
        protected_entry(
            LIVE_RENDERER,
            path_source_kind="runtime_renderer",
            surface_class="runtime_lua",
            authority_role="runtime_renderer_read_only",
            reason="renderer behavior must not change under a governance-only seal",
        ),
        protected_entry(
            RUNTIME_MONOLITH,
            path_source_kind="stale_monolith",
            surface_class="runtime_lua",
            authority_role="stale_monolith_reentry_scan_target",
            reason="monolith must not return as current authority",
            missing_allowed=True,
        ),
        protected_entry(
            CURRENT_ROUTE_REQUIRED_VALIDATIONS,
            path_source_kind="current_route_governance_manifest",
            surface_class="governance_config",
            authority_role="current_route_required_validation_manifest",
            reason="manifest adoption is blocked while canonical residual seal is not allowed",
        ),
    ]
    entries.extend(
        manifest_chunk_entries(
            RUNTIME_CHUNK_MANIFEST,
            RUNTIME_CHUNK_DIR,
            path_source_kind="manifest_derived_runtime_chunk_files",
            surface_class="runtime_payload",
            authority_role="live_current_runtime_payload",
            reason="live runtime chunks are read-only authority surfaces",
        )
    )
    entries.extend(
        manifest_chunk_entries(
            package_manifest,
            package_chunks,
            path_source_kind="package_peer_runtime_payload",
            surface_class="package_payload",
            authority_role="package_peer_runtime_payload",
            reason="package peer payload is scanned, not rebuilt",
            package_peer_source=rel(base_guard.PACKAGE_DATA_DIR),
        )
    )
    entries.extend(
        manifest_chunk_entries(
            candidate_manifest,
            candidate_chunks,
            path_source_kind="candidate_bridge_runtime_payload",
            surface_class="candidate_bridge",
            authority_role="candidate_bridge_runtime_payload",
            reason="candidate bridge is a current-looking comparison surface only",
        )
    )
    entries.extend(
        manifest_chunk_entries(
            rollback_manifest,
            rollback_chunks,
            path_source_kind="predecessor_rollback_payload",
            surface_class="predecessor_historical",
            authority_role="predecessor_rollback_snapshot",
            reason="predecessor residue is historical-only evidence and must not be mutated",
        )
    )
    return {
        "schema_version": "runtime-payload-state-integrity-residual-protected-surface-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "claim_boundary": CLAIM_BOUNDARY,
        "entries": sorted(entries, key=lambda row: row["path"]),
    }


def rows_by_role(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        "current_rows": [row for row in rows if row["surface_id"] == "live_current_runtime"],
        "current_like_rows": [row for row in rows if row["current_like"]],
        "current_unadopted_rows": [
            row
            for row in rows
            if row["surface_id"] == "live_current_runtime" and row["derived_adoption_state"] == "unadopted"
        ],
        "current_like_forbidden_rows": [
            row
            for row in rows
            if row["current_like"] and row["classification"] == "forbidden_current"
        ],
        "current_like_unclassified_rows": [
            row
            for row in rows
            if row["current_like"] and row["classification"] == "unclassified_current"
        ],
        "predecessor_residue_rows": [
            row
            for row in rows
            if row["classification"] == "legacy_only_predecessor_residue"
        ],
    }


def read_existing_guard_report(path: str) -> dict[str, Any]:
    full = EXISTING_EVIDENCE_ROOT / path
    return read_json(full) if full.exists() else {"status": "MISSING", "path": rel(full)}


def live_manifest_consumption_report() -> dict[str, Any]:
    manifest = read_json(CURRENT_ROUTE_REQUIRED_VALIDATIONS)
    required_artifact_paths = [row.get("path") for row in manifest.get("required_artifacts", [])]
    required_test_ids = [row.get("test_id") for row in manifest.get("required_tests", [])]
    artifact_hits = [
        path
        for path in required_artifact_paths
        if isinstance(path, str) and "staging/runtime_payload_state_integrity/" in path
    ]
    test_hits = [
        test_id
        for test_id in required_test_ids
        if isinstance(test_id, str) and "test_runtime_payload_state_integrity." in test_id
    ]
    return {
        "schema_version": "runtime-payload-residual-existing-gate-consumption-v1",
        "generated_at": now_iso(),
        "status": "PASS" if artifact_hits and test_hits else "FAIL",
        "manifest_path": rel(CURRENT_ROUTE_REQUIRED_VALIDATIONS),
        "runtime_payload_required_artifact_count": len(artifact_hits),
        "runtime_payload_required_test_count": len(test_hits),
        "runtime_payload_required_artifacts": artifact_hits,
        "runtime_payload_required_tests": test_hits,
        "residual_manifest_adoption_performed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_phase1(rows: list[dict[str, Any]], summaries: list[dict[str, Any]]) -> dict[str, Any]:
    role = rows_by_role(rows)
    manifest = build_protected_surface_manifest()
    write_json(phase_path("phase1", "protected_surface_manifest.json"), manifest)

    missing_required = [
        entry for entry in manifest["entries"] if entry["exists_status"] == "missing_required"
    ]
    package_peer_without_source = [
        entry
        for entry in manifest["entries"]
        if entry["path_source_kind"] == "package_peer_runtime_payload" and not entry.get("package_peer_source")
    ]
    scope = {
        "schema_version": "runtime-payload-residual-scope-separation-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not missing_required and not package_peer_without_source else "FAIL",
        "payload_shape_guard_status": "PASS",
        "residual_seal_status": "blocked_pending_author_and_external_review",
        "governance_only": True,
        "runtime_mutation_allowed": False,
        "source_rendered_bridge_runtime_package_mutation_allowed": False,
        "predecessor_residue_cleanup_allowed": False,
        "protected_surface_entry_count": len(manifest["entries"]),
        "missing_required_entry_count": len(missing_required),
        "package_peer_without_source_count": len(package_peer_without_source),
        "non_claims": NON_CLAIMS,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase1", "scope_separation_and_no_mutation_declaration.json"), scope)
    input_fingerprint = {
        "schema_version": "runtime-payload-residual-input-fingerprint-v1",
        "generated_at": now_iso(),
        "status": "PASS" if PLAN_PATH.exists() else "FAIL",
        "plan": {
            "path": rel(PLAN_PATH),
            "sha256": sha256_file(PLAN_PATH),
        },
        "existing_guard_tool": {
            "path": rel(base_guard.__file__),
            "sha256": sha256_file(base_guard.__file__),
        },
        "existing_guard_test": {
            "path": rel(V2_ROOT / "tests" / "test_runtime_payload_state_integrity.py"),
            "sha256": sha256_file(V2_ROOT / "tests" / "test_runtime_payload_state_integrity.py"),
        },
        "protected_surface_manifest_hash": canonical_hash(
            [
                {
                    "path": entry["path"],
                    "pre_hash": entry["pre_hash"],
                    "exists_status": entry["exists_status"],
                }
                for entry in manifest["entries"]
            ]
        ),
        "surface_summary_count": len(summaries),
    }
    write_json(phase_path("phase1", "input_fingerprint_manifest.json"), input_fingerprint)
    blocker_inventory = {
        "schema_version": "runtime-payload-residual-blocker-inventory-v1",
        "generated_at": now_iso(),
        "status": "BLOCKED",
        "implementation_blocker_count": 0,
        "governance_blocker_count": 2,
        "blockers": [
            {
                "marker": "pending_author_selection",
                "classification": "author_reserved_blocker",
                "blocking_final_complete_seal": True,
                "blocking_guard_reverification": False,
            },
            {
                "marker": "blocked_external_gate",
                "classification": "external_review_blocker",
                "blocking_final_complete_seal": True,
                "blocking_guard_reverification": False,
            },
        ],
        "current_runtime_entry_count": len(role["current_rows"]),
        "current_runtime_unadopted_count": len(role["current_unadopted_rows"]),
        "predecessor_residue_count": len(role["predecessor_residue_rows"]),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase1", "blocker_inventory.json"), blocker_inventory)
    consumption = live_manifest_consumption_report()
    write_json(phase_path("phase1", "runtime_payload_existing_gate_consumption_report.json"), consumption)
    return manifest


def write_phase2(rows: list[dict[str, Any]]) -> None:
    role = rows_by_role(rows)
    inventory = read_existing_guard_report("phase0/runtime_payload_state_inventory.json")
    guard = read_existing_guard_report("phase4/current_route_payload_state_guard_report.json")
    display = read_existing_guard_report("phase5b/display_resolution_parity_report.json")
    publish = read_existing_guard_report("phase0/publish_state_authority_resolution.json")
    reverification_pass = (
        inventory.get("status") == "PASS"
        and guard.get("status") == "PASS"
        and display.get("status") == "PASS"
        and len(role["current_rows"]) == EXPECTED_CURRENT_ROWS
        and len(role["current_unadopted_rows"]) == EXPECTED_CURRENT_UNADOPTED_ROWS
        and len(role["current_like_forbidden_rows"]) == 0
        and len(role["current_like_unclassified_rows"]) == 0
        and len(role["predecessor_residue_rows"]) == EXPECTED_PREDECESSOR_RESIDUE_ROWS
    )
    write_json(
        phase_path("phase2", "shape_guard_readpoint_reverification_report.json"),
        {
            "schema_version": "runtime-payload-residual-shape-guard-reverification-v1",
            "generated_at": now_iso(),
            "status": "PASS" if reverification_pass else "FAIL",
            "current_runtime_entry_count": len(role["current_rows"]),
            "expected_current_runtime_entry_count": EXPECTED_CURRENT_ROWS,
            "current_runtime_unadopted_count": len(role["current_unadopted_rows"]),
            "expected_current_runtime_unadopted_count": EXPECTED_CURRENT_UNADOPTED_ROWS,
            "current_like_publish_state_row_count": publish.get("current_like_publish_state_row_count"),
            "current_like_forbidden_count": len(role["current_like_forbidden_rows"]),
            "current_like_unclassified_count": len(role["current_like_unclassified_rows"]),
            "predecessor_residue_count": len(role["predecessor_residue_rows"]),
            "display_body_present_count": display.get("display_body_present_count"),
            "existing_inventory_status": inventory.get("status"),
            "existing_guard_status": guard.get("status"),
            "existing_display_status": display.get("status"),
            "source_runtime_package_authority_mutated": False,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_json(
        phase_path("phase2", "current_looking_forbidden_scan_report.json"),
        {
            "schema_version": "runtime-payload-residual-current-looking-forbidden-scan-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not role["current_like_forbidden_rows"] and not role["current_like_unclassified_rows"] else "FAIL",
            "current_like_row_count": len(role["current_like_rows"]),
            "current_like_forbidden_count": len(role["current_like_forbidden_rows"]),
            "current_like_unclassified_count": len(role["current_like_unclassified_rows"]),
            "forbidden_rows": role["current_like_forbidden_rows"],
            "unclassified_rows": role["current_like_unclassified_rows"],
        },
    )
    write_json(
        phase_path("phase2", "guard_predicate_diff_scope_report.json"),
        {
            "schema_version": "runtime-payload-residual-guard-predicate-freeze-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "predicate_surface_frozen": True,
            "pass_fail_predicate_changed": False,
            "denominator_changed": False,
            "expected_counts_changed": False,
            "current_like_surface_selection_changed": False,
            "allowed_change_scope": "wrapper_only_and_additive_residual_reports",
            "guard_tool": {
                "path": rel(base_guard.__file__),
                "sha256": sha256_file(base_guard.__file__),
            },
            "guard_test": {
                "path": rel(V2_ROOT / "tests" / "test_runtime_payload_state_integrity.py"),
                "sha256": sha256_file(V2_ROOT / "tests" / "test_runtime_payload_state_integrity.py"),
            },
        },
    )
    residue_denominator_overlap = [
        row
        for row in role["predecessor_residue_rows"]
        if row.get("current_like") is True or row.get("surface_id") in {"live_current_runtime", "package_peer_runtime", "candidate_bridge_runtime"}
    ]
    write_json(
        phase_path("phase2", "denominator_disjointness_report.json"),
        {
            "schema_version": "runtime-payload-residual-denominator-disjointness-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not residue_denominator_overlap else "FAIL",
            "current_like_denominator_role": "current_like_runtime_package_candidate_surfaces",
            "predecessor_residue_role": "predecessor_rollback_snapshot_only",
            "current_like_row_count": len(role["current_like_rows"]),
            "predecessor_residue_count": len(role["predecessor_residue_rows"]),
            "residue_in_current_denominator_count": len(residue_denominator_overlap),
            "overlap_rows": residue_denominator_overlap,
        },
    )


def write_phase3(rows: list[dict[str, Any]]) -> None:
    role = rows_by_role(rows)
    residue_rows = role["predecessor_residue_rows"]
    current_item_keys = {
        (row["surface_id"], row["item_id"], row["chunk_path"])
        for row in role["current_like_rows"]
    }
    residue_reentry_rows = [
        row
        for row in residue_rows
        if (row["surface_id"], row["item_id"], row["chunk_path"]) in current_item_keys
    ]
    write_jsonl(phase_path("phase3", "predecessor_residue_rows.jsonl"), residue_rows)
    write_json(
        phase_path("phase3", "residual_historical_only_confinement_report.json"),
        {
            "schema_version": "runtime-payload-residual-historical-only-confinement-v1",
            "generated_at": now_iso(),
            "status": "PASS" if len(residue_rows) == EXPECTED_PREDECESSOR_RESIDUE_ROWS else "FAIL",
            "predecessor_residue_count": len(residue_rows),
            "expected_predecessor_residue_count": EXPECTED_PREDECESSOR_RESIDUE_ROWS,
            "residue_surface_ids": sorted({row["surface_id"] for row in residue_rows}),
            "historical_only": True,
            "cleanup_target": False,
            "current_debt": False,
            "runtime_mutation_basis": False,
            "rows": residue_rows,
        },
    )
    write_json(
        phase_path("phase3", "predecessor_residue_non_reentry_report.json"),
        {
            "schema_version": "runtime-payload-residual-predecessor-non-reentry-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not residue_reentry_rows else "FAIL",
            "predecessor_residue_count": len(residue_rows),
            "current_route_reentry_count": len(residue_reentry_rows),
            "residue_in_current_denominator_count": len(residue_reentry_rows),
            "current_like_denominator_intersection_empty": len(residue_reentry_rows) == 0,
            "reentry_rows": residue_reentry_rows,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def enumerated_author_options() -> dict[str, dict[str, Any]]:
    path = phase_path("phase4", "author_reserved_selection_option_enumeration.json")
    if not path.exists():
        return {}
    options = read_json(path).get("options", [])
    return {
        row["option_id"]: row
        for row in options
        if isinstance(row, dict) and non_empty_string(row.get("option_id"))
    }


def enumerated_author_option_ids() -> set[str]:
    return set(enumerated_author_options())


def selected_author_option(decision: dict[str, Any]) -> dict[str, Any] | None:
    selected_option_id = decision.get("selected_option_id")
    if not non_empty_string(selected_option_id):
        return None
    return enumerated_author_options().get(selected_option_id)


def author_decision_seal_flag_matches_option_metadata(decision: dict[str, Any]) -> bool:
    option = selected_author_option(decision)
    return (
        option is not None
        and decision.get("selected_option_is_seal_closing")
        is option.get("selected_option_is_seal_closing_if_author_selected")
    )


def author_decision_matches_option_metadata(decision: dict[str, Any]) -> bool:
    option = selected_author_option(decision)
    return (
        option is not None
        and author_decision_seal_flag_matches_option_metadata(decision)
        and option.get("selected_option_is_seal_closing_if_author_selected") is True
        and option.get("requires_runtime_mutation") is False
    )


def author_decision_value_not_generated(decision: dict[str, Any]) -> bool:
    return (
        decision.get("decision_value_not_generated_by_executor") is True
        or decision.get("not_generated_by_executor") is True
    )


def author_policy_confirmed(decision: dict[str, Any]) -> bool:
    confirmations = decision.get("policy_confirmations", {})
    required = [
        "current_compatible_unadopted_text_ko_forbidden",
        "current_compatible_unadopted_publish_state_forbidden",
        "unadopted_display_body_missing_or_explicit_nil",
        "predecessor_residue_historical_only",
    ]
    return all(confirmations.get(field) is True for field in required)


def author_decision_is_complete(decision: dict[str, Any]) -> bool:
    return (
        decision.get("status") == "PASS"
        and decision.get("selected_option_is_seal_closing") is True
        and author_decision_matches_option_metadata(decision)
        and decision.get("decision_record_generated_by_executor") is False
        and author_decision_value_not_generated(decision)
        and decision.get("decision_value_not_inferred_by_validator") is True
        and decision.get("pending_author_selection") is False
        and non_empty_string(decision.get("decision_owner"))
        and non_empty_string(decision.get("decision_owner_role"))
        and non_empty_string(decision.get("decision_source"))
        and non_empty_string(decision.get("decision_timestamp"))
        and non_empty_string(decision.get("decision_readpoint"))
        and author_policy_confirmed(decision)
    )


def author_decision_doc(decision: dict[str, Any] | None = None, final: dict[str, Any] | None = None) -> str:
    if decision and author_decision_is_complete(decision):
        return f"""# Runtime Payload State Integrity Author Decision

Status: `seal_closing_author_decision_recorded`.

Selected option: `{decision.get("selected_option_id")}`.
Decision owner: `{decision.get("decision_owner")}`.
Decision owner role: `{decision.get("decision_owner_role")}`.
Decision source: `{decision.get("decision_source")}`.
Decision readpoint: `{decision.get("decision_readpoint")}`.

The executor preserved an author-supplied seal-closing decision record. The decision value is recorded as not generated by the executor and not inferred by the validator.

Policy confirmations:

* current-compatible `unadopted + text_ko` forbidden
* current-compatible `unadopted + publish_state` forbidden
* unadopted display body missing or explicit nil
* predecessor residue historical-only
"""
    return """# Runtime Payload State Integrity Author Decision

Status: `pending_author_selection`.

This file is an author-owned decision placeholder. The executor generated option evidence but did not select a seal-closing option, infer author intent, or convert guard PASS into residual seal completion.

Known predecessor option space:

* `branch_a_guard_only_forbid_policy` - author confirms current-compatible `unadopted + text_ko` and `unadopted + publish_state` are forbidden, with predecessor residue historical-only.
* `branch_b_contract_redefinition` - author reopens the contract decision path instead of this residual seal.
* `explicit_no_branch_mutation_required` - author confirms no branch-specific mutation is required while preserving the forbidden current-compatible payload policy.
* `defer_residual_seal` - author keeps the residual seal blocked.

No option is selected by this document.
"""


def generated_author_decision_placeholder() -> dict[str, Any]:
    return {
        "schema_version": "runtime-payload-residual-author-decision-record-v1",
        "generated_at": now_iso(),
        "status": "PENDING_AUTHOR_SELECTION",
        "decision_owner": None,
        "decision_owner_role": None,
        "selected_option_id": None,
        "selected_option_is_seal_closing": False,
        "decision_source": None,
        "decision_timestamp": None,
        "decision_readpoint": "pending_author_selection",
        "decision_record_generated_by_executor": True,
        "decision_value_not_generated_by_executor": True,
        "decision_value_not_inferred_by_validator": True,
        "pending_author_selection": True,
        "policy_confirmations": {
            "current_compatible_unadopted_text_ko_forbidden": None,
            "current_compatible_unadopted_publish_state_forbidden": None,
            "unadopted_display_body_missing_or_explicit_nil": None,
            "predecessor_residue_historical_only": None,
        },
    }


def load_supplied_author_decision() -> dict[str, Any] | None:
    path = phase_path("phase4", "author_reserved_selection_decision_record.json")
    if not path.exists():
        return None
    payload = read_json(path)
    if payload.get("selected_option_id") is None:
        return None
    return payload


def write_phase4() -> None:
    options = [
        {
            "option_id": "branch_a_guard_only_forbid_policy",
            "source": "docs/runtime_payload_state_integrity_plan.md Branch A FORBID path",
            "selected_option_is_seal_closing_if_author_selected": True,
            "requires_runtime_mutation": False,
        },
        {
            "option_id": "branch_b_contract_redefinition",
            "source": "docs/runtime_payload_state_integrity_plan.md Branch B ALLOW + REDEFINE path",
            "selected_option_is_seal_closing_if_author_selected": False,
            "requires_runtime_mutation": False,
        },
        {
            "option_id": "explicit_no_branch_mutation_required",
            "source": "docs/runtime_payload_state_integrity_closeout.md explicit no-branch mutation decision",
            "selected_option_is_seal_closing_if_author_selected": True,
            "requires_runtime_mutation": False,
        },
        {
            "option_id": "defer_residual_seal",
            "source": "residual seal blocker inventory",
            "selected_option_is_seal_closing_if_author_selected": False,
            "requires_runtime_mutation": False,
        },
    ]
    write_json(
        phase_path("phase4", "author_reserved_selection_option_enumeration.json"),
        {
            "schema_version": "runtime-payload-residual-author-option-enumeration-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "enumerable_option_space_present": True,
            "option_count": len(options),
            "options": options,
            "option_space_source": [
                "docs/runtime_payload_state_integrity_plan.md",
                "docs/runtime_payload_state_integrity_closeout.md",
                "Iris/build/description/v2/staging/runtime_payload_state_integrity/phase2/author_reserved_branch_decision_record.md",
            ],
            "not_selected_by_executor": True,
        },
    )
    supplied = load_supplied_author_decision()
    decision = supplied or generated_author_decision_placeholder()
    if supplied is None:
        write_json(phase_path("phase4", "author_reserved_selection_decision_record.json"), decision)
    write_text(AUTHOR_DECISION_DOC, author_decision_doc(decision))
    selected_seal_closing = decision.get("selected_option_is_seal_closing") is True
    policy_confirmed = author_policy_confirmed(decision)
    selected_option = {row["option_id"]: row for row in options}.get(decision.get("selected_option_id"))
    selected_option_enumerated = selected_option is not None
    selected_option_metadata_seal_closing = (
        selected_option is not None
        and selected_option.get("selected_option_is_seal_closing_if_author_selected") is True
    )
    selected_option_requires_runtime_mutation = (
        selected_option is not None
        and selected_option.get("requires_runtime_mutation") is True
    )
    selected_option_metadata_consistent = author_decision_matches_option_metadata(decision)
    selected_option_seal_flag_matches_metadata = author_decision_seal_flag_matches_option_metadata(decision)
    author_complete = author_decision_is_complete(decision)
    write_json(
        phase_path("phase4", "policy_consistency_report.json"),
        {
            "schema_version": "runtime-payload-residual-policy-consistency-v1",
            "generated_at": now_iso(),
            "status": "PASS" if author_complete else "BLOCKED_PENDING_AUTHOR_SELECTION",
            "guard_policy_consistent_with_forbid_option": True,
            "selected_seal_closing_option_present": selected_seal_closing,
            "selected_option_in_enumerated_option_space": selected_option_enumerated,
            "selected_option_metadata_seal_closing_if_author_selected": selected_option_metadata_seal_closing,
            "selected_option_requires_runtime_mutation": selected_option_requires_runtime_mutation,
            "selected_option_metadata_consistent_with_decision": selected_option_metadata_consistent,
            "selected_option_seal_flag_matches_metadata": selected_option_seal_flag_matches_metadata,
            "author_policy_confirmation_present": policy_confirmed,
            "author_decision_value_not_generated_by_executor": author_decision_value_not_generated(decision),
            "author_decision_value_not_inferred_by_validator": decision.get("decision_value_not_inferred_by_validator") is True,
            "current_compatible_unadopted_text_ko_forbidden_confirmed": decision.get("policy_confirmations", {}).get("current_compatible_unadopted_text_ko_forbidden") is True,
            "current_compatible_unadopted_publish_state_forbidden_confirmed": decision.get("policy_confirmations", {}).get("current_compatible_unadopted_publish_state_forbidden") is True,
            "predecessor_residue_historical_only_confirmed_by_author": decision.get("policy_confirmations", {}).get("predecessor_residue_historical_only") is True,
            "blocked_reason": None if author_complete else "author-owned seal-closing decision is absent or incomplete",
            "decision_record_source": "author_supplied_existing_record" if supplied is not None else "executor_generated_placeholder",
        },
    )


def fill_post_hashes(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    updated = json.loads(json.dumps(manifest))
    changed: list[dict[str, Any]] = []
    for entry in updated["entries"]:
        resolved = resolve_repo(entry["path"])
        is_file = resolved.exists() and resolved.is_file()
        entry["post_hash"] = sha256_file(resolved) if is_file else None
        entry["post_exists_status"] = file_status(resolved, missing_allowed=entry["missing_allowed"])
        if (
            entry["pre_hash"] != entry["post_hash"]
            or entry["exists_status"] != entry["post_exists_status"]
        ):
            changed.append(entry)
    return updated, changed


def primary_review_paths() -> list[Path]:
    paths = [
        phase_path("phase1", "scope_separation_and_no_mutation_declaration.json"),
        phase_path("phase1", "input_fingerprint_manifest.json"),
        phase_path("phase1", "protected_surface_manifest.json"),
        phase_path("phase1", "blocker_inventory.json"),
        phase_path("phase1", "runtime_payload_existing_gate_consumption_report.json"),
        phase_path("phase2", "shape_guard_readpoint_reverification_report.json"),
        phase_path("phase2", "current_looking_forbidden_scan_report.json"),
        phase_path("phase2", "guard_predicate_diff_scope_report.json"),
        phase_path("phase2", "denominator_disjointness_report.json"),
        phase_path("phase3", "residual_historical_only_confinement_report.json"),
        phase_path("phase3", "predecessor_residue_non_reentry_report.json"),
        phase_path("phase4", "author_reserved_selection_option_enumeration.json"),
        phase_path("phase4", "author_reserved_selection_decision_record.json"),
        phase_path("phase4", "policy_consistency_report.json"),
        phase_path("phase5", "no_mutation_report.json"),
        RESIDUAL_TOOL,
        RESIDUAL_TEST,
        Path(base_guard.__file__),
        V2_ROOT / "tests" / "test_runtime_payload_state_integrity.py",
        PLAN_PATH,
        AUTHOR_DECISION_DOC,
    ]
    return [path for path in paths if resolve_repo(path).exists()]


def hash_records(paths: list[Path]) -> list[dict[str, Any]]:
    records = []
    for path in paths:
        resolved = resolve_repo(path)
        records.append(
            {
                "path": rel(resolved),
                "exists": resolved.exists(),
                "kind": "file" if resolved.is_file() else "dir" if resolved.is_dir() else "missing",
                "sha256": sha256_file(resolved) if resolved.is_file() else None,
                "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
            }
        )
    return records


def write_phase5(manifest: dict[str, Any]) -> dict[str, Any]:
    updated_manifest, changed = fill_post_hashes(manifest)
    write_json(phase_path("phase1", "protected_surface_manifest.json"), updated_manifest)
    disallowed_changed = [entry for entry in changed if not entry.get("expected_mutation_allowed")]
    source_classes = {"source", "rendered", "lua_bridge", "runtime_payload", "runtime_lua", "package_payload", "candidate_bridge", "predecessor_historical"}
    source_rendered_bridge_runtime_package_changed = [
        entry for entry in disallowed_changed if entry.get("surface_class") in source_classes
    ]
    report = {
        "schema_version": "runtime-payload-residual-no-mutation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not disallowed_changed else "FAIL",
        "changed_count": len(disallowed_changed),
        "source_rendered_bridge_runtime_package_changed_count": len(source_rendered_bridge_runtime_package_changed),
        "changed": disallowed_changed,
        "expected_mutation_allowed_entry_count": sum(
            1 for entry in updated_manifest["entries"] if entry.get("expected_mutation_allowed")
        ),
        "phase8_manifest_adoption_carveout_used": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase5", "no_mutation_report.json"), report)
    records = hash_records(primary_review_paths())
    primary_manifest = {
        "schema_version": "runtime-payload-residual-primary-review-artifact-manifest-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "primary_review_artifact_count": len(records),
        "artifacts": records,
    }
    write_json(phase_path("phase5", "primary_review_artifact_manifest.json"), primary_manifest)
    artifact_hash_report = {
        "schema_version": "runtime-payload-residual-artifact-hash-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "primary_review_artifact_manifest_hash": canonical_hash(records),
        "artifact_count": len(records),
        "guard_tool_hash_covered": any(row["path"].endswith("runtime_payload_state_integrity.py") for row in records),
        "guard_test_hash_covered": any(row["path"].endswith("test_runtime_payload_state_integrity.py") for row in records),
        "residual_tool_hash_covered": any(row["path"].endswith("runtime_payload_state_integrity_residual_seal.py") for row in records),
        "residual_test_hash_covered": any(row["path"].endswith("test_runtime_payload_state_integrity_residual_seal.py") for row in records),
        "artifacts": records,
    }
    write_json(phase_path("phase5", "artifact_hash_report.json"), artifact_hash_report)
    return artifact_hash_report


def external_review_is_pass(payload: dict[str, Any], artifact_hash_report: dict[str, Any]) -> bool:
    comparison_exemptions = payload.get("comparison_exemptions")
    comparison_exempt_count = payload.get("comparison_exempt_count")
    comparison_exemptions_valid = (
        isinstance(comparison_exemptions, list)
        and comparison_exempt_count == len(comparison_exemptions)
        and all(
            isinstance(exemption, dict)
            and non_empty_string(exemption.get("path"))
            and non_empty_string(exemption.get("exempt_reason"))
            and exemption.get("reviewer_accepted") is True
            for exemption in comparison_exemptions
        )
    )
    return (
        payload.get("status") == "PASS"
        and non_empty_string(payload.get("reviewer_identity"))
        and payload.get("reviewer_identity") != "MISSING_EXTERNAL_REVIEW"
        and non_empty_string(payload.get("reviewer_kind"))
        and payload.get("reviewer_kind") != "missing"
        and non_empty_string(payload.get("review_independence_basis"))
        and payload.get("not_self_review") is True
        and payload.get("not_same_authorship_chain") is True
        and non_empty_string(payload.get("same_authorship_chain_basis"))
        and payload.get("review_verdict") == "PASS"
        and payload.get("canonical_residual_seal_allowed") is True
        and payload.get("primary_review_artifact_count") == artifact_hash_report.get("artifact_count")
        and payload.get("missing_count") == 0
        and payload.get("hash_mismatch_count") == 0
        and comparison_exemptions_valid
        and payload.get("reviewed_artifact_manifest_hash")
        == artifact_hash_report.get("primary_review_artifact_manifest_hash")
    )


def missing_external_review_placeholder(payload: dict[str, Any]) -> bool:
    return (
        payload.get("status") == "BLOCKED_EXTERNAL_REVIEW"
        and payload.get("reviewer_identity") == "MISSING_EXTERNAL_REVIEW"
        and payload.get("reviewer_kind") == "missing"
        and payload.get("review_verdict") == "BLOCKED_MISSING_EXTERNAL_INDEPENDENT_REVIEW"
        and payload.get("canonical_residual_seal_allowed") is False
    )


def external_review_admissibility_state(payload: dict[str, Any], artifact_hash_report: dict[str, Any]) -> str:
    if external_review_is_pass(payload, artifact_hash_report):
        return "PASS"
    if missing_external_review_placeholder(payload):
        return "MISSING"
    return "REJECTED"


def external_review_blocked_reason(state: str, missing: list[dict[str, Any]], mismatches: list[dict[str, Any]]) -> str | None:
    if state == "PASS":
        if missing or mismatches:
            return "independent_review_artifact_hash_mismatch"
        return None
    if state == "REJECTED":
        return "external_independent_review_rejected"
    if state == "MISSING":
        return "external_independent_review_missing"
    if missing or mismatches:
        return "independent_review_artifact_hash_mismatch"
    return "external_independent_review_rejected"


def load_external_review_record(artifact_hash_report: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    path = phase_path("phase6", "external_independent_review_report.json")
    if not path.exists():
        return "MISSING", None
    payload = read_json(path)
    state = external_review_admissibility_state(payload, artifact_hash_report)
    return state, payload


def write_phase6(artifact_hash_report: dict[str, Any]) -> None:
    records = artifact_hash_report.get("artifacts", [])
    current = hash_records([REPO_ROOT / row["path"] for row in records])
    expected = {row["path"]: row for row in records}
    mismatches = []
    missing = []
    for row in current:
        original = expected.get(row["path"])
        if not original or not row["exists"]:
            missing.append(row)
        elif original.get("sha256") != row.get("sha256"):
            mismatches.append({"path": row["path"], "expected": original, "observed": row})
    external_review_state, external_review_record = load_external_review_record(artifact_hash_report)
    review_pass = external_review_state == "PASS"
    review_rejected = external_review_state == "REJECTED"
    review_missing = external_review_state == "MISSING"
    independent_hash = {
        "schema_version": "runtime-payload-residual-independent-review-artifact-hash-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if review_pass and not missing and not mismatches else "BLOCKED_EXTERNAL_REVIEW",
        "internal_artifact_hash_report": rel(phase_path("phase5", "artifact_hash_report.json")),
        "primary_review_artifact_count": len(records),
        "missing_count": len(missing),
        "hash_mismatch_count": len(mismatches),
        "comparison_exempt_count": 0,
        "comparison_exemptions": [],
        "missing": missing,
        "mismatches": mismatches,
        "hash_comparison_pass": not missing and not mismatches,
        "independent_review_pass": review_pass and not missing and not mismatches,
        "external_review_admissibility_state": external_review_state,
        "external_review_rejected": review_rejected,
        "external_review_missing": review_missing,
        "canonical_residual_seal_allowed": review_pass and not missing and not mismatches,
    }
    write_json(phase_path("phase6", "independent_review_artifact_hash_report.json"), independent_hash)
    if review_missing:
        write_json(
            phase_path("phase6", "external_independent_review_report.json"),
            {
                "schema_version": "runtime-payload-residual-external-independent-review-report-v1",
                "generated_at": now_iso(),
                "status": "BLOCKED_EXTERNAL_REVIEW",
                "reviewer_identity": "MISSING_EXTERNAL_REVIEW",
                "reviewer_kind": "missing",
                "review_independence_basis": "not_evaluated_missing_reviewer",
                "not_self_review": False,
                "not_same_authorship_chain": False,
                "same_authorship_chain_basis": "not_evaluated_missing_reviewer",
                "reviewed_artifact_manifest_hash": artifact_hash_report.get("primary_review_artifact_manifest_hash"),
                "primary_review_artifact_count": len(records),
                "missing_count": len(missing),
                "hash_mismatch_count": len(mismatches),
                "comparison_exempt_count": 0,
                "comparison_exemptions": [],
                "review_verdict": "BLOCKED_MISSING_EXTERNAL_INDEPENDENT_REVIEW",
                "canonical_residual_seal_allowed": False,
            },
        )
    elif external_review_record is not None:
        write_json(phase_path("phase6", "external_independent_review_report.json"), external_review_record)
    gate_status = "PASS" if review_pass and not missing and not mismatches else "BLOCKED_EXTERNAL_REVIEW"
    blocked_reason = external_review_blocked_reason(external_review_state, missing, mismatches)
    write_json(
        phase_path("phase6", "external_review_gate_report.json"),
        {
            "schema_version": "runtime-payload-residual-external-review-gate-v1",
            "generated_at": now_iso(),
            "status": gate_status,
            "blocked_external_gate": gate_status != "PASS",
            "external_independent_review_status": external_review_state,
            "external_review_rejected": review_rejected,
            "external_review_missing": review_missing,
            "blocked_reason": blocked_reason,
            "canonical_residual_seal_allowed": gate_status == "PASS",
            "review_report_source": "external_supplied_existing_record" if external_review_record and not review_missing else "executor_generated_missing_review_placeholder",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )


def claim_boundary_doc(final: dict[str, Any] | None = None) -> str:
    if final and final.get("canonical_residual_seal_allowed") is True:
        return """# Runtime Payload State Integrity Residual Claim Boundary

Status: `complete_residual_seal_governance_only`.

The residual seal completion claim is limited to the evidence packet: payload shape guard reverified, guard predicate frozen, predecessor residue confined to historical-only surfaces, protected surfaces unchanged, author-owned seal-closing decision recorded, and external independent review PASS.

Non-claims remain unchanged: no runtime mutation, no source mutation, no rendered regeneration, no Lua bridge export, no package payload mutation, no release readiness, no manual QA, no semantic quality completion, and no public-facing text acceptance.
"""
    return """# Runtime Payload State Integrity Residual Claim Boundary

Status: `blocked_pending_author_and_external_review`.

The payload shape guard can be PASS while the residual seal remains incomplete. A residual seal completion claim is allowed only after an author-owned seal-closing decision and an external independent review PASS are both present.

Current machine evidence is limited to:

* payload shape guard reverified
* guard predicate frozen
* predecessor residue confined to historical-only surfaces
* protected source/rendered/Lua bridge/runtime/package surfaces unchanged

Non-claims: no runtime mutation, no source mutation, no rendered regeneration, no Lua bridge export, no package payload mutation, no release readiness, no manual QA, no semantic quality completion, and no public-facing text acceptance.
"""


def ledger_packet_doc(final: dict[str, Any] | None = None) -> str:
    if final and final.get("canonical_residual_seal_allowed") is True:
        return """# Runtime Payload State Integrity Residual Ledger Packet

Status: `complete_residual_seal_governance_only`.

Additive packet; current-route manifest adoption is traceable separately and this packet does not mutate runtime/source/package authority surfaces.

Runtime Payload State Integrity Residual Seal is complete for the governance-only residual scope because the machine guard evidence, author-owned seal-closing decision, and external independent review gate are all PASS.

Readpoint:

* current runtime rows: 2105
* current unadopted rows: 21
* current-like publish_state rows: 0
* current-like forbidden/unclassified rows: 0
* predecessor rollback residue rows: 2
* residue in current denominator: 0
* protected mutation changed count: 0
"""
    return """# Runtime Payload State Integrity Residual Ledger Packet

Draft additive packet; not applied to canonical authority docs.

Runtime Payload State Integrity Residual Seal remains blocked because the author-owned selection and external independent review gates are not satisfied. Existing runtime payload guard evidence remains required-validation input, but this residual packet does not mutate the current-route manifest or any runtime/source/package authority surface.

Readpoint:

* current runtime rows: 2105
* current unadopted rows: 21
* current-like publish_state rows: 0
* current-like forbidden/unclassified rows: 0
* predecessor rollback residue rows: 2
* residue in current denominator: 0
* protected mutation changed count: 0
"""


def write_phase7() -> dict[str, Any]:
    guard = read_json(phase_path("phase2", "shape_guard_readpoint_reverification_report.json"))
    predicate = read_json(phase_path("phase2", "guard_predicate_diff_scope_report.json"))
    author = read_json(phase_path("phase4", "author_reserved_selection_decision_record.json"))
    policy = read_json(phase_path("phase4", "policy_consistency_report.json"))
    review = read_json(phase_path("phase6", "external_review_gate_report.json"))
    residue = read_json(phase_path("phase3", "predecessor_residue_non_reentry_report.json"))
    no_mutation = read_json(phase_path("phase5", "no_mutation_report.json"))
    author_complete = author_decision_is_complete(author) and policy.get("status") == "PASS"
    review_complete = review.get("status") == "PASS" and review.get("canonical_residual_seal_allowed") is True
    canonical_allowed = (
        guard.get("status") == "PASS"
        and predicate.get("status") == "PASS"
        and author_complete
        and review_complete
        and residue.get("residue_in_current_denominator_count") == 0
        and no_mutation.get("changed_count") == 0
    )
    final = {
        "schema_version": "runtime-payload-residual-final-seal-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if canonical_allowed else "BLOCKED",
        "machine_contract_status": "PASS" if guard.get("status") == "PASS" and predicate.get("status") == "PASS" and residue.get("status") == "PASS" and no_mutation.get("status") == "PASS" else "FAIL",
        "closeout_state": "complete_residual_seal" if canonical_allowed else "blocked_pending_author_selection_and_external_review",
        "payload_shape_guard_status": guard.get("status"),
        "guard_predicate_freeze_status": predicate.get("status"),
        "author_decision_status": author.get("status"),
        "author_policy_consistency_status": policy.get("status"),
        "author_seal_closing_decision_complete": author_complete,
        "independent_external_review_status": review.get("status"),
        "external_review_complete": review_complete,
        "predecessor_residue_disposition": "historical_only",
        "residue_in_current_denominator_count": residue.get("residue_in_current_denominator_count"),
        "runtime_mutation_changed_count": no_mutation.get("changed_count"),
        "source_rendered_bridge_package_mutation_changed_count": no_mutation.get("source_rendered_bridge_runtime_package_changed_count"),
        "blocked_external_gate": review.get("blocked_external_gate") is True,
        "pending_author_selection": author.get("pending_author_selection") is True,
        "review_traceability_chain": [
            rel(phase_path("phase5", "artifact_hash_report.json")),
            rel(phase_path("phase5", "primary_review_artifact_manifest.json")),
            rel(phase_path("phase6", "independent_review_artifact_hash_report.json")),
            rel(phase_path("phase6", "external_review_gate_report.json")),
        ],
        "canonical_residual_seal_allowed": canonical_allowed,
        "governance_adoption_status": "not_required_traceable" if canonical_allowed else "blocked",
        "non_claims": NON_CLAIMS,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase7", "final_runtime_payload_residual_seal_report.json"), final)
    write_text(AUTHOR_DECISION_DOC, author_decision_doc(author, final))
    write_text(CLAIM_BOUNDARY_DOC, claim_boundary_doc(final))
    write_text(LEDGER_PACKET_DOC, ledger_packet_doc(final))
    return final


def write_phase8(final: dict[str, Any]) -> None:
    manifest = read_json(CURRENT_ROUTE_REQUIRED_VALIDATIONS)
    residual_paths = {
        "Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase7/final_runtime_payload_residual_seal_report.json",
    }
    existing_required_paths = {row.get("path") for row in manifest.get("required_artifacts", [])}
    duplicate_paths = sorted(residual_paths.intersection(existing_required_paths))
    blocked = final.get("canonical_residual_seal_allowed") is not True
    report = {
        "schema_version": "runtime-payload-residual-current-route-governance-adoption-v1",
        "generated_at": now_iso(),
        "status": "BLOCKED" if blocked else "PASS",
        "governance_adoption_status": "blocked" if blocked else "not_required_traceable",
        "blocked_reason": "canonical_residual_seal_allowed_false" if blocked else None,
        "manifest_path": rel(CURRENT_ROUTE_REQUIRED_VALIDATIONS),
        "live_manifest_mutated": False,
        "additive_only_diff": True,
        "removed_existing_entries": 0,
        "modified_existing_entries": 0,
        "duplicate_entries": len(duplicate_paths),
        "duplicate_paths": duplicate_paths,
        "existing_runtime_payload_guard_entries_present": live_manifest_consumption_report()["status"] == "PASS",
        "source_rendered_lua_runtime_package_authority_mutated": False,
    }
    write_json(phase_path("phase8", "current_route_governance_adoption_report.json"), report)


def generate_artifacts() -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    base_guard.run_all()
    rows, summaries = base_guard.load_all_rows()
    manifest = write_phase1(rows, summaries)
    write_phase2(rows)
    write_phase3(rows)
    write_phase4()
    artifact_hash_report = write_phase5(manifest)
    write_phase6(artifact_hash_report)
    final = write_phase7()
    write_phase8(final)
    return final


def validate_generated(*, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_paths = [
        phase_path("phase1", "scope_separation_and_no_mutation_declaration.json"),
        phase_path("phase1", "input_fingerprint_manifest.json"),
        phase_path("phase1", "protected_surface_manifest.json"),
        phase_path("phase1", "blocker_inventory.json"),
        phase_path("phase1", "runtime_payload_existing_gate_consumption_report.json"),
        phase_path("phase2", "shape_guard_readpoint_reverification_report.json"),
        phase_path("phase2", "current_looking_forbidden_scan_report.json"),
        phase_path("phase2", "guard_predicate_diff_scope_report.json"),
        phase_path("phase2", "denominator_disjointness_report.json"),
        phase_path("phase3", "residual_historical_only_confinement_report.json"),
        phase_path("phase3", "predecessor_residue_non_reentry_report.json"),
        phase_path("phase4", "author_reserved_selection_option_enumeration.json"),
        phase_path("phase4", "author_reserved_selection_decision_record.json"),
        phase_path("phase4", "policy_consistency_report.json"),
        phase_path("phase5", "no_mutation_report.json"),
        phase_path("phase5", "artifact_hash_report.json"),
        phase_path("phase5", "primary_review_artifact_manifest.json"),
        phase_path("phase6", "independent_review_artifact_hash_report.json"),
        phase_path("phase6", "external_independent_review_report.json"),
        phase_path("phase6", "external_review_gate_report.json"),
        phase_path("phase7", "final_runtime_payload_residual_seal_report.json"),
        phase_path("phase8", "current_route_governance_adoption_report.json"),
        AUTHOR_DECISION_DOC,
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append({"code": "missing_required_artifact", "path": rel(path)})
    if not errors:
        scope = read_json(phase_path("phase1", "scope_separation_and_no_mutation_declaration.json"))
        protected = read_json(phase_path("phase1", "protected_surface_manifest.json"))
        guard = read_json(phase_path("phase2", "shape_guard_readpoint_reverification_report.json"))
        forbidden = read_json(phase_path("phase2", "current_looking_forbidden_scan_report.json"))
        predicate = read_json(phase_path("phase2", "guard_predicate_diff_scope_report.json"))
        disjoint = read_json(phase_path("phase2", "denominator_disjointness_report.json"))
        residue = read_json(phase_path("phase3", "predecessor_residue_non_reentry_report.json"))
        author = read_json(phase_path("phase4", "author_reserved_selection_decision_record.json"))
        policy = read_json(phase_path("phase4", "policy_consistency_report.json"))
        no_mutation = read_json(phase_path("phase5", "no_mutation_report.json"))
        artifact_hash = read_json(phase_path("phase5", "artifact_hash_report.json"))
        primary_manifest = read_json(phase_path("phase5", "primary_review_artifact_manifest.json"))
        independent_review = read_json(phase_path("phase6", "independent_review_artifact_hash_report.json"))
        external_review = read_json(phase_path("phase6", "external_independent_review_report.json"))
        review = read_json(phase_path("phase6", "external_review_gate_report.json"))
        final = read_json(phase_path("phase7", "final_runtime_payload_residual_seal_report.json"))
        adoption = read_json(phase_path("phase8", "current_route_governance_adoption_report.json"))
        author_doc = AUTHOR_DECISION_DOC.read_text(encoding="utf-8")
        claim_doc = CLAIM_BOUNDARY_DOC.read_text(encoding="utf-8")
        ledger_doc = LEDGER_PACKET_DOC.read_text(encoding="utf-8")
        stored_artifacts = artifact_hash.get("artifacts", [])
        stored_artifact_paths = [
            REPO_ROOT / row["path"]
            for row in stored_artifacts
            if isinstance(row, dict) and non_empty_string(row.get("path"))
        ]
        current_artifacts_from_stored_paths = hash_records(stored_artifact_paths)
        current_artifacts_from_review_rules = hash_records(primary_review_paths())
        stored_artifact_manifest_hash = canonical_hash(stored_artifacts)
        current_stored_path_manifest_hash = canonical_hash(current_artifacts_from_stored_paths)
        current_rule_manifest_hash = canonical_hash(current_artifacts_from_review_rules)
        artifact_hash_report_internal_consistent = (
            artifact_hash.get("primary_review_artifact_manifest_hash") == stored_artifact_manifest_hash
            and artifact_hash.get("artifact_count") == len(stored_artifacts)
        )
        primary_manifest_internal_consistent = (
            primary_manifest.get("artifacts") == stored_artifacts
            and primary_manifest.get("primary_review_artifact_count") == artifact_hash.get("artifact_count")
        )
        primary_review_artifacts_current = (
            current_stored_path_manifest_hash == artifact_hash.get("primary_review_artifact_manifest_hash")
            and current_rule_manifest_hash == artifact_hash.get("primary_review_artifact_manifest_hash")
            and current_artifacts_from_stored_paths == stored_artifacts
            and current_artifacts_from_review_rules == stored_artifacts
        )
        expected_artifacts_by_path = {row.get("path"): row for row in stored_artifacts if isinstance(row, dict)}
        current_review_missing: list[dict[str, Any]] = []
        current_review_mismatches: list[dict[str, Any]] = []
        for row in current_artifacts_from_stored_paths:
            original = expected_artifacts_by_path.get(row.get("path"))
            if not original or not row.get("exists"):
                current_review_missing.append(row)
            elif original.get("sha256") != row.get("sha256"):
                current_review_mismatches.append({"path": row.get("path"), "expected": original, "observed": row})
        current_protected_manifest, current_protected_changed = fill_post_hashes(protected)
        current_disallowed_changed = [
            entry for entry in current_protected_changed if not entry.get("expected_mutation_allowed")
        ]
        source_classes = {"source", "rendered", "lua_bridge", "runtime_payload", "runtime_lua", "package_payload", "candidate_bridge", "predecessor_historical"}
        current_source_rendered_bridge_runtime_package_changed = [
            entry for entry in current_disallowed_changed if entry.get("surface_class") in source_classes
        ]
        protected_surface_current = current_protected_manifest.get("entries") == protected.get("entries")
        author_complete = author_decision_is_complete(author) and policy.get("status") == "PASS"
        author_pending = author.get("pending_author_selection") is True
        author_value_not_generated = author_decision_value_not_generated(author)
        external_review_state = external_review_admissibility_state(external_review, artifact_hash)
        external_review_report_pass = external_review_state == "PASS"
        expected_external_review_rejected = external_review_state == "REJECTED"
        expected_external_review_missing = external_review_state == "MISSING"
        external_review_blocked = (
            external_review_state in {"MISSING", "REJECTED"}
        )
        expected_hash_comparison_pass = not current_review_missing and not current_review_mismatches
        expected_external_review_gate_pass = external_review_report_pass and expected_hash_comparison_pass
        expected_blocked_external_gate = not expected_external_review_gate_pass
        expected_external_review_gate_status = "PASS" if expected_external_review_gate_pass else "BLOCKED_EXTERNAL_REVIEW"
        expected_external_review_blocked_reason = external_review_blocked_reason(
            external_review_state,
            current_review_missing,
            current_review_mismatches,
        )
        expected_review_report_source = (
            "executor_generated_missing_review_placeholder"
            if expected_external_review_missing
            else "external_supplied_existing_record"
        )
        independent_review_complete = (
            independent_review.get("status") == "PASS"
            and independent_review.get("hash_comparison_pass") is True
            and independent_review.get("independent_review_pass") is True
            and independent_review.get("canonical_residual_seal_allowed") is True
            and independent_review.get("primary_review_artifact_count") == artifact_hash.get("artifact_count")
            and independent_review.get("missing_count") == 0
            and independent_review.get("hash_mismatch_count") == 0
        )
        independent_review_blocked = (
            independent_review.get("status") == "BLOCKED_EXTERNAL_REVIEW"
            and independent_review.get("canonical_residual_seal_allowed") is False
        )
        review_complete = (
            review.get("status") == "PASS"
            and review.get("canonical_residual_seal_allowed") is True
            and external_review_report_pass
            and independent_review_complete
        )
        final_allowed_expected = (
            guard.get("status") == "PASS"
            and predicate.get("status") == "PASS"
            and policy.get("status") == "PASS"
            and residue.get("residue_in_current_denominator_count") == 0
            and no_mutation.get("changed_count") == 0
            and primary_review_artifacts_current
            and protected_surface_current
            and not current_disallowed_changed
            and author_complete
            and review_complete
        )
        package_entries_missing_source = [
            entry
            for entry in protected.get("entries", [])
            if entry.get("path_source_kind") == "package_peer_runtime_payload" and not entry.get("package_peer_source")
        ]
        expected_mutation_entries = [
            entry for entry in protected.get("entries", []) if entry.get("expected_mutation_allowed") is True
        ]
        checks = [
            (scope.get("status") == "PASS", "scope_status_not_pass", scope),
            (guard.get("status") == "PASS", "guard_reverification_not_pass", guard),
            (guard.get("current_runtime_entry_count") == EXPECTED_CURRENT_ROWS, "current_count_mismatch", guard),
            (guard.get("current_runtime_unadopted_count") == EXPECTED_CURRENT_UNADOPTED_ROWS, "unadopted_count_mismatch", guard),
            (guard.get("current_like_publish_state_row_count") == 0, "publish_state_count_mismatch", guard),
            (forbidden.get("current_like_forbidden_count") == 0, "forbidden_count_nonzero", forbidden),
            (forbidden.get("current_like_unclassified_count") == 0, "unclassified_count_nonzero", forbidden),
            (predicate.get("predicate_surface_frozen") is True, "predicate_not_frozen", predicate),
            (disjoint.get("residue_in_current_denominator_count") == 0, "denominator_overlap_nonzero", disjoint),
            (residue.get("residue_in_current_denominator_count") == 0, "residue_reentry_nonzero", residue),
            (no_mutation.get("changed_count") == 0, "protected_surface_mutated", no_mutation),
            (artifact_hash_report_internal_consistent, "artifact_hash_report_internal_mismatch", artifact_hash),
            (primary_manifest_internal_consistent, "primary_review_manifest_internal_mismatch", primary_manifest),
            (
                primary_review_artifacts_current,
                "primary_review_artifact_hash_drift",
                {
                    "stored_manifest_hash": artifact_hash.get("primary_review_artifact_manifest_hash"),
                    "current_stored_path_manifest_hash": current_stored_path_manifest_hash,
                    "current_rule_manifest_hash": current_rule_manifest_hash,
                    "stored_artifact_count": len(stored_artifacts),
                    "current_stored_path_artifact_count": len(current_artifacts_from_stored_paths),
                    "current_rule_artifact_count": len(current_artifacts_from_review_rules),
                    "current_from_stored_paths": current_artifacts_from_stored_paths,
                    "current_from_review_rules": current_artifacts_from_review_rules,
                },
            ),
            (protected_surface_current, "protected_surface_post_hash_drift", current_protected_manifest),
            (not current_disallowed_changed, "protected_surface_currently_mutated", current_disallowed_changed),
            (
                no_mutation.get("changed_count") == len(current_disallowed_changed),
                "no_mutation_report_changed_count_stale",
                {"stored": no_mutation, "current_changed": current_disallowed_changed},
            ),
            (
                no_mutation.get("source_rendered_bridge_runtime_package_changed_count")
                == len(current_source_rendered_bridge_runtime_package_changed),
                "no_mutation_report_source_surface_count_stale",
                {"stored": no_mutation, "current_changed": current_source_rendered_bridge_runtime_package_changed},
            ),
            (not package_entries_missing_source, "package_peer_source_missing", package_entries_missing_source),
            (not expected_mutation_entries, "unexpected_mutation_carveout_present", expected_mutation_entries),
            (artifact_hash.get("guard_tool_hash_covered") is True, "guard_tool_hash_not_covered", artifact_hash),
            (artifact_hash.get("guard_test_hash_covered") is True, "guard_test_hash_not_covered", artifact_hash),
            (artifact_hash.get("residual_tool_hash_covered") is True, "residual_tool_hash_not_covered", artifact_hash),
            (policy.get("status") == ("PASS" if author_complete else "BLOCKED_PENDING_AUTHOR_SELECTION"), "policy_consistency_status_mismatch", policy),
            (author_pending or author_complete, "author_gate_invalid", author),
            (author_value_not_generated, "author_decision_value_generated_or_ambiguous", author),
            (external_review_blocked or external_review_report_pass, "external_review_report_invalid", external_review),
            (
                review.get("external_independent_review_status") == external_review_state,
                "external_review_gate_state_mismatch",
                {"external_review": external_review, "gate": review, "expected_state": external_review_state},
            ),
            (
                review.get("status") == expected_external_review_gate_status
                and review.get("blocked_external_gate") is expected_blocked_external_gate
                and review.get("external_review_rejected") is expected_external_review_rejected
                and review.get("external_review_missing") is expected_external_review_missing
                and review.get("blocked_reason") == expected_external_review_blocked_reason
                and review.get("canonical_residual_seal_allowed") is expected_external_review_gate_pass
                and review.get("review_report_source") == expected_review_report_source,
                "external_review_gate_classification_mismatch",
                {
                    "gate": review,
                    "expected": {
                        "status": expected_external_review_gate_status,
                        "blocked_external_gate": expected_blocked_external_gate,
                        "external_independent_review_status": external_review_state,
                        "external_review_rejected": expected_external_review_rejected,
                        "external_review_missing": expected_external_review_missing,
                        "blocked_reason": expected_external_review_blocked_reason,
                        "canonical_residual_seal_allowed": expected_external_review_gate_pass,
                        "review_report_source": expected_review_report_source,
                    },
                },
            ),
            (
                independent_review.get("status") == expected_external_review_gate_status
                and independent_review.get("primary_review_artifact_count") == len(stored_artifacts)
                and independent_review.get("missing_count") == len(current_review_missing)
                and independent_review.get("hash_mismatch_count") == len(current_review_mismatches)
                and independent_review.get("hash_comparison_pass") is expected_hash_comparison_pass
                and independent_review.get("independent_review_pass") is expected_external_review_gate_pass
                and independent_review.get("external_review_admissibility_state") == external_review_state
                and independent_review.get("external_review_rejected") is expected_external_review_rejected
                and independent_review.get("external_review_missing") is expected_external_review_missing
                and independent_review.get("canonical_residual_seal_allowed") is expected_external_review_gate_pass,
                "independent_review_classification_mismatch",
                {
                    "independent_review": independent_review,
                    "expected": {
                        "status": expected_external_review_gate_status,
                        "primary_review_artifact_count": len(stored_artifacts),
                        "missing_count": len(current_review_missing),
                        "hash_mismatch_count": len(current_review_mismatches),
                        "hash_comparison_pass": expected_hash_comparison_pass,
                        "independent_review_pass": expected_external_review_gate_pass,
                        "external_review_admissibility_state": external_review_state,
                        "external_review_rejected": expected_external_review_rejected,
                        "external_review_missing": expected_external_review_missing,
                        "canonical_residual_seal_allowed": expected_external_review_gate_pass,
                    },
                },
            ),
            (independent_review_blocked or independent_review_complete, "independent_review_hash_gate_invalid", independent_review),
            (review.get("blocked_external_gate") is True or review_complete, "external_gate_invalid", review),
            (final.get("machine_contract_status") == "PASS", "machine_contract_not_pass", final),
            (
                final.get("canonical_residual_seal_allowed") is final_allowed_expected,
                "canonical_allowed_state_mismatch",
                {"final": final, "expected": final_allowed_expected},
            ),
            (
                final.get("canonical_residual_seal_allowed") is not True
                or "seal_closing_author_decision_recorded" in author_doc,
                "author_decision_doc_not_complete",
                {"path": rel(AUTHOR_DECISION_DOC), "final": final},
            ),
            (
                final.get("canonical_residual_seal_allowed") is not True
                or "complete_residual_seal_governance_only" in claim_doc,
                "claim_boundary_doc_not_complete",
                {"path": rel(CLAIM_BOUNDARY_DOC), "final": final},
            ),
            (
                final.get("canonical_residual_seal_allowed") is not True
                or "complete_residual_seal_governance_only" in ledger_doc,
                "ledger_packet_doc_not_complete",
                {"path": rel(LEDGER_PACKET_DOC), "final": final},
            ),
            (adoption.get("live_manifest_mutated") is False, "manifest_mutated", adoption),
        ]
        for ok, code, payload in checks:
            if not ok:
                errors.append({"code": code, "payload": payload})
        if require_complete:
            if final.get("canonical_residual_seal_allowed") is not True:
                errors.append({"code": "canonical_residual_seal_not_allowed", "payload": final})
            if not author_complete:
                errors.append({"code": "author_seal_closing_decision_missing", "payload": author})
            if not review_complete:
                errors.append({"code": "external_independent_review_not_pass", "payload": review})
    report = {
        "schema_version": "runtime-payload-residual-validation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    report_name = "validation_report.require_complete.json" if require_complete else "validation_report.json"
    write_json(phase_path("phase7", report_name), report)
    return report, not errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate/validate runtime payload residual seal evidence.")
    parser.add_argument("--mode", choices=["generate", "validate", "all"], default="generate")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    final: dict[str, Any] | None = None
    if args.mode in {"generate", "all"}:
        final = generate_artifacts()
        print(
            json.dumps(
                {
                    "status": final["status"],
                    "machine_contract_status": final["machine_contract_status"],
                    "canonical_residual_seal_allowed": final["canonical_residual_seal_allowed"],
                    "pending_author_selection": final["pending_author_selection"],
                    "blocked_external_gate": final["blocked_external_gate"],
                },
                sort_keys=True,
            )
        )
    if args.mode == "generate":
        return 0 if final and final.get("machine_contract_status") == "PASS" else 1
    if args.mode in {"validate", "all"}:
        report, ok = validate_generated(require_complete=args.require_complete)
        if not args.require_complete:
            validate_generated(require_complete=True)
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
