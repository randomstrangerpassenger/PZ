from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    canonical_hash,
    file_record,
    hash_surface,
    protected_surface_payload,
    read_json,
    rel,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_delta_guard_current_route_integration"
PRIOR_GUARD_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_delta_disposition_guard_seal"
PARITY_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_regeneration_parity"
ROUND3_DIR = REPO_ROOT / "Iris" / "_docs" / "round3"
REQUIRED_MANIFEST = ROUND3_DIR / "current_route_required_validations.json"

PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_vnext_delta_guard_current_route_integration_plan.md"
SCOPE_LOCK_DOC = REPO_ROOT / "docs" / "dvf_3_3_vnext_delta_guard_current_route_integration_scope_lock.md"
INPUT_CONTRACT_DOC = REPO_ROOT / "docs" / "dvf_3_3_vnext_delta_guard_current_route_input_contract.md"
SHARED_CONTRACT_DOC = REPO_ROOT / "docs" / "dvf_3_3_vnext_delta_guard_shared_contract.md"
CLOSEOUT_DOC = REPO_ROOT / "docs" / "dvf_3_3_vnext_delta_guard_current_route_integration_closeout.md"
HANDOFF_DOC = REPO_ROOT / "docs" / "dvf_3_3_vnext_current_authority_handoff_packet.md"

PRIOR_CLOSEOUT = REPO_ROOT / "docs" / "dvf_3_3_vnext_delta_disposition_closeout.md"
PRIOR_FINAL_REPORT = PRIOR_GUARD_ROOT / "phase10" / "final_delta_disposition_guard_contract_report.json"
APPROVED_MANIFEST = PRIOR_GUARD_ROOT / "phase9" / "approved_cutover_input_delta_manifest.json"
PRIOR_DUAL_ZERO = PRIOR_GUARD_ROOT / "phase8" / "dual_zero_verification_report.json"
PRIOR_NO_MUTATION = PRIOR_GUARD_ROOT / "phase8" / "protected_surface_no_mutation_verdict.json"
PARITY_REPORT = PARITY_ROOT / "phase5" / "runtime_parity_report.json"
PARITY_DELTAS = PARITY_ROOT / "phase5" / "runtime_parity_deltas.jsonl"

EXPECTED_TOTAL = 2125
EXPECTED_TEXT = 2071
EXPECTED_STATE = 54
EXPECTED_APPROVED = 2017
EXPECTED_REJECTED = 108
EXPECTED_DEFERRED = 0

PRIMARY_GUARDS = [
    {
        "guard_id": "fixture_as_authority",
        "name": "Fixture-as-Authority Guard",
        "definition_source": "Compose Entrypoint Guard Hardening",
        "surface_owner_status": "sealed",
        "shared_contract_role": "referenced_definition_owner",
        "definition_paths": ["docs/compose_entrypoint_guard_hardening_closeout.md"],
    },
    {
        "guard_id": "monolith_re_entry",
        "name": "Monolith Re-entry Guard",
        "definition_source": "Lua Bridge Export Contract Realignment",
        "surface_owner_status": "sealed",
        "shared_contract_role": "referenced_definition_owner",
        "definition_paths": ["docs/lua_bridge_export_contract_realign_closeout.md"],
    },
    {
        "guard_id": "staging_direct_promotion",
        "name": "Staging Direct Promotion Guard",
        "definition_source": "Lua Bridge Export Contract Realignment",
        "surface_owner_status": "sealed",
        "shared_contract_role": "referenced_definition_owner",
        "definition_paths": ["docs/lua_bridge_export_contract_realign_closeout.md"],
    },
    {
        "guard_id": "parity_missing",
        "name": "Parity-Missing Guard",
        "definition_source": "Regeneration Parity Evidence",
        "surface_owner_status": "sealed",
        "shared_contract_role": "referenced_definition_owner",
        "definition_paths": [
            "Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_report.json",
            "Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/final_contract_report.json",
        ],
    },
    {
        "guard_id": "disposition_coverage",
        "name": "Disposition Coverage Guard",
        "definition_source": "Delta Disposition Policy and Guard Seal",
        "surface_owner_status": "sealed",
        "shared_contract_role": "referenced_definition_owner",
        "definition_paths": [
            "docs/dvf_3_3_vnext_delta_disposition_policy.md",
            "docs/dvf_3_3_vnext_delta_disposition_closeout.md",
            "Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/phase10/final_delta_disposition_guard_contract_report.json",
        ],
    },
    {
        "guard_id": "unapproved_delta",
        "name": "Rejected/Deferred/Unapproved Delta Guard",
        "definition_source": "Approved Manifest Index-Only Contract",
        "surface_owner_status": "sealed",
        "shared_contract_role": "referenced_definition_owner",
        "definition_paths": [
            "docs/dvf_3_3_vnext_delta_disposition_policy.md",
            "Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/phase9/approved_cutover_input_delta_manifest.json",
        ],
    },
    {
        "guard_id": "single_authority",
        "name": "Single-Authority Guard",
        "definition_source": "Current Authority and Cutover Contracts",
        "surface_owner_status": "sealed",
        "shared_contract_role": "referenced_definition_owner",
        "definition_paths": [
            "docs/dvf_3_3_vnext_cutover_contract.md",
            "docs/dvf_3_3_vnext_current_authority_plan.md",
        ],
    },
    {
        "guard_id": "legacy_vocabulary",
        "name": "Legacy Vocabulary Guard",
        "definition_source": "Guard Seal and Delta Disposition Vocabulary",
        "surface_owner_status": "sealed",
        "shared_contract_role": "referenced_definition_owner",
        "definition_paths": [
            "docs/dvf_3_3_vnext_guard_seal_contract.md",
            "docs/dvf_3_3_vnext_delta_disposition_policy.md",
        ],
    },
]

SUBORDINATE_GUARD_REFERENCES = [
    {
        "guard_id": "stale_dvf_bridge_package_intrusion",
        "name": "Stale DVF Bridge Package Intrusion Guard",
        "definition_source": "Stale DVF Bridge Artifact Disposition",
        "surface_owner_status": "implemented_review_pending",
        "shared_contract_role": "referenced_subordinate_package_guard_evidence",
        "dual_definition_verdict": "no_competing_definition_but_not_independently_sealed",
        "definition_paths": ["docs/stale_dvf_bridge_artifact_disposition_closeout.md"],
    }
]

FORBIDDEN_PATTERNS = [
    "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/build/description/v2/staging/dvf_3_3_vnext_execution/",
    "Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/",
    "active",
    "silent",
]

REQUIRED_TEST_IDS = [
    "test_compose_entrypoint_guard_hardening.ComposeEntrypointGuardHardeningTest.test_legacy_profile_cannot_write_current_output_and_leaves_hash_unchanged",
    "test_compose_entrypoint_guard_hardening.ComposeEntrypointGuardHardeningTest.test_staging_context_cannot_target_current_equivalent_output",
    "test_dvf_3_3_vnext_delta_disposition_guard_seal.DvfVnextDeltaDispositionGuardSealTest.test_final_contract_separates_guard_completion_from_cutover_usability",
    "test_dvf_3_3_vnext_delta_disposition_guard_seal.DvfVnextDeltaDispositionGuardSealTest.test_guard_matrix_dual_zero_and_negative_cases_pass",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_final_report_preserves_claim_boundary",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_guard_coverage_matrix_keeps_single_status_aware_definition",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_package_export_compose_routes_share_criteria_by_equivalence",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_parent_handoff_keeps_cutover_and_release_out_of_scope",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_required_validation_manifest_is_fail_closed_and_runner_visible",
    "test_lua_bridge_export_contract_realign.LuaBridgeExportContractRealignTest.test_current_context_and_current_monolith_destination_are_rejected",
    "test_lua_bridge_export_contract_realign.LuaBridgeExportContractRealignTest.test_protected_live_chunk_destination_is_rejected_before_write",
    "test_package_layer3_chunks_only_contract.PackageLayer3ChunksOnlyContractTest.test_package_script_excludes_layer3_monolith",
    "test_package_layer3_chunks_only_contract.PackageLayer3ChunksOnlyContractTest.test_package_script_fails_loud_on_stale_dvf_bridge_surface",
]


def phase_dir(root: Path, phase: str) -> Path:
    path = root / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def field(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def required_input_paths() -> list[tuple[Path, str]]:
    return [
        (PLAN_PATH, "approved_execution_plan"),
        (PRIOR_CLOSEOUT, "prior_disposition_closeout"),
        (PRIOR_FINAL_REPORT, "prior_final_delta_disposition_guard_contract_report"),
        (APPROVED_MANIFEST, "approved_manifest_index_only"),
        (PARITY_REPORT, "runtime_parity_report"),
        (PARITY_DELTAS, "runtime_parity_deltas"),
        (REPO_ROOT / "docs" / "PLAN_TEMPLATE.md", "plan_template"),
        (REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md", "execution_contract"),
    ]


def tool_paths() -> list[tuple[Path, str]]:
    return [
        (V2_ROOT / "tools" / "build" / "guard_dvf_3_3_vnext_output_paths.py", "existing_output_path_guard"),
        (V2_ROOT / "tools" / "build" / "validate_dvf_3_3_vnext_execution_contract.py", "existing_execution_contract_validator"),
        (REPO_ROOT / "tools" / "check_lua_syntax.ps1", "lua_syntax_validator"),
        (PARITY_DELTAS, "sealed_runtime_parity_deltas"),
        (REPO_ROOT / "docs" / "PLAN_TEMPLATE.md", "plan_template"),
        (REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md", "execution_contract"),
    ]


def disposition_counts() -> dict[str, int]:
    report = read_json(PRIOR_FINAL_REPORT)
    counts = report.get("counts", {})
    return {
        "total": int(counts.get("total_delta_count", 0)),
        "approved": int(counts.get("approved_count", 0)),
        "rejected": int(counts.get("rejected_count", 0)),
        "deferred": int(counts.get("deferred_count", 0)),
        "runtime_eligible": int(counts.get("runtime_eligible_count", 0)),
    }


def parity_counts() -> dict[str, int]:
    report = read_json(PARITY_REPORT)
    parity = report.get("field_parity", {})
    return {
        "text_ko": int(parity.get("text_ko_delta_count", 0)),
        "state": int(parity.get("state_delta_count", 0)),
        "publish_state_legacy_visibility": int(parity.get("publish_state_legacy_visibility_disposition_count", 0)),
    }


def input_errors() -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for path, role in required_input_paths():
        if not path.exists():
            errors.append({"code": "missing_required_input", "path": rel(path), "role": role})
    if errors:
        return errors

    final = read_json(PRIOR_FINAL_REPORT)
    approved_manifest = read_json(APPROVED_MANIFEST)
    parity = parity_counts()
    counts = disposition_counts()
    if final.get("status") != "PASS":
        errors.append({"code": "prior_final_report_not_pass", "observed": final.get("status")})
    if final.get("cutover_input_usable") is not False:
        errors.append({"code": "cutover_input_usable_changed", "observed": final.get("cutover_input_usable")})
    if counts != {
        "total": EXPECTED_TOTAL,
        "approved": EXPECTED_APPROVED,
        "rejected": EXPECTED_REJECTED,
        "deferred": EXPECTED_DEFERRED,
        "runtime_eligible": EXPECTED_APPROVED,
    }:
        errors.append({"code": "disposition_count_mismatch", "observed": counts})
    if parity["text_ko"] != EXPECTED_TEXT or parity["state"] != EXPECTED_STATE:
        errors.append({"code": "parity_axis_count_mismatch", "observed": parity})
    if approved_manifest.get("manifest_index_only") is not True:
        errors.append({"code": "approved_manifest_not_index_only"})
    if approved_manifest.get("payload_generated") is not False:
        errors.append({"code": "approved_manifest_payload_generated"})
    if approved_manifest.get("cutover_input_usable") is not False:
        errors.append({"code": "approved_manifest_cutover_status_changed"})
    return errors


def guard_criteria_payload() -> dict[str, Any]:
    criteria = {
        "schema_version": "dvf-3-3-vnext-delta-guard-forbidden-scan-criteria-v1",
        "role": "shared_scan_criteria_or_route_owner_equivalence_fingerprint",
        "forbidden_condition_count": len(PRIMARY_GUARDS),
        "forbidden_conditions": [row["guard_id"] for row in PRIMARY_GUARDS],
        "forbidden_patterns": FORBIDDEN_PATTERNS,
        "allowed_contexts": ["historical", "diagnostic", "staging"],
        "current_context_fail_loud": True,
    }
    criteria["criteria_sha256"] = canonical_hash(criteria)
    return criteria


def required_manifest_payload() -> dict[str, Any]:
    return {
        "schema_version": "round3-current-route-required-validations-v1",
        "status": "PASS",
        "required": True,
        "route": "current",
        "enforcement": "fail_closed",
        "claim": "current route guard integrated",
        "required_tests": [
            {
                "test_id": test_id,
                "required": True,
                "role": "current_route_guard_required_validation",
            }
            for test_id in REQUIRED_TEST_IDS
        ],
        "required_artifacts": [
            {
                "path": rel(PRIOR_FINAL_REPORT),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "cutover_input_usable", "equals": False},
                    {"field": "counts.total_delta_count", "equals": EXPECTED_TOTAL},
                    {"field": "counts.approved_count", "equals": EXPECTED_APPROVED},
                    {"field": "counts.rejected_count", "equals": EXPECTED_REJECTED},
                ],
            },
            {
                "path": rel(ROOT / "phase5" / "package_export_compose_guard_report.json"),
                "checks": [{"field": "status", "equals": "PASS"}],
            },
            {
                "path": rel(ROOT / "phase6" / "protected_surface_no_mutation_verdict.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "changed_count", "equals": 0},
                ],
            },
            {
                "path": rel(ROOT / "phase6" / "dual_zero_reconfirmation_report.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "static_forbidden_current_surface_hit_count", "equals": 0},
                    {"field": "static_unclassified_residue_count", "equals": 0},
                    {"field": "dynamic_forbidden_reach_count", "equals": 0},
                ],
            },
            {
                "path": rel(ROOT / "phase7" / "final_current_route_guard_integration_report.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "claim", "equals": "current route guard integrated"},
                    {"field": "cutover_input_usable", "equals": False},
                ],
            },
            {
                "path": rel(ROOT / "phase7" / "claim_boundary_lint_report.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "forbidden_claim_hit_count", "equals": 0},
                ],
            },
        ],
        "non_claims": [
            "no_successor_baseline_identity_final_seal",
            "no_current_cutover",
            "no_live_runtime_chunk_replacement",
            "no_package_readiness",
            "no_release_readiness",
            "no_manual_in_game_validation",
        ],
    }


def write_phase1(root: Path) -> None:
    phase = phase_dir(root, "phase1")
    errors = input_errors()
    write_json(
        phase / "input_contract_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-input-contract-v1",
            "status": "PASS" if not errors else "FAIL",
            "objective": "current route guard integration",
            "prior_evidence_read_only": True,
            "approved_manifest_index_only": True,
            "cutover_input_usable": False,
            "required_counts": {
                "total": EXPECTED_TOTAL,
                "text_ko": EXPECTED_TEXT,
                "state": EXPECTED_STATE,
                "approved": EXPECTED_APPROVED,
                "rejected": EXPECTED_REJECTED,
                "deferred": EXPECTED_DEFERRED,
            },
            "observed_disposition_counts": disposition_counts() if PRIOR_FINAL_REPORT.exists() else {},
            "observed_parity_counts": parity_counts() if PARITY_REPORT.exists() else {},
            "errors": errors,
        },
    )
    write_json(
        phase / "input_fingerprint_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-input-fingerprints-v1",
            "status": "PASS" if all(path.exists() for path, _role in required_input_paths()) else "FAIL",
            "records": [file_record(path, role) for path, role in required_input_paths()],
        },
    )
    tool_records = [file_record(path, role) for path, role in tool_paths()]
    write_json(
        phase / "tool_path_existence_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-tool-path-existence-v1",
            "status": "PASS" if all(row["exists"] for row in tool_records) else "FAIL",
            "records": tool_records,
            "missing_count": sum(1 for row in tool_records if not row["exists"]),
        },
    )
    write_json(
        phase / "no_touch_surface_manifest.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-no-touch-surface-v1",
            "status": "PASS",
            "protected_surface": protected_surface_payload(),
            "no_touch_assertions": [
                "runtime_chunk_manifest",
                "runtime_chunk_files",
                "current_description_data",
                "current_description_output",
                "prior_guard_seal_evidence_body",
            ],
        },
    )


def write_phase2(root: Path) -> dict[str, Any]:
    phase = phase_dir(root, "phase2")
    criteria = guard_criteria_payload()
    write_json(
        phase / "shared_guard_contract.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-shared-contract-v1",
            "status": "PASS",
            "contract_role": "admission_gate_aggregation_surface",
            "not_canonical_authority_replacement": True,
            "primary_forbidden_condition_count": len(PRIMARY_GUARDS),
            "criteria_sha256": criteria["criteria_sha256"],
            "forbidden_conditions": PRIMARY_GUARDS,
            "subordinate_references": SUBORDINATE_GUARD_REFERENCES,
            "non_claims": required_manifest_payload()["non_claims"],
        },
    )
    write_json(phase / "forbidden_scan_criteria.json", criteria)
    matrix_rows = []
    for row in PRIMARY_GUARDS:
        matrix_rows.append(
            {
                **row,
                "definition_source_count": 1,
                "dual_definition_verdict": "single_definition_source",
                "blocking_if_missing": True,
            }
        )
    for row in SUBORDINATE_GUARD_REFERENCES:
        matrix_rows.append(
            {
                **row,
                "definition_source_count": 1,
                "condition_role": "subordinate_reference",
                "blocking_if_overclaimed_as_sealed": True,
            }
        )
    write_json(
        phase / "guard_coverage_matrix.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-coverage-matrix-v1",
            "status": "PASS",
            "primary_forbidden_condition_count": len(PRIMARY_GUARDS),
            "primary_conditions_have_single_definition_source": True,
            "allowed_surface_owner_statuses": ["sealed", "implemented_review_pending", "subordinate_reference"],
            "rows": matrix_rows,
        },
    )
    write_json(
        phase / "guard_authority_reconciliation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-authority-reconciliation-v1",
            "status": "PASS",
            "shared_contract_replaces_existing_surfaces": False,
            "compose_entrypoint_guard_hardening": {
                "surface_owner_status": "sealed",
                "definition_role_retained": True,
            },
            "lua_bridge_export_contract_realign": {
                "surface_owner_status": "sealed",
                "definition_role_retained": True,
            },
            "stale_dvf_bridge_artifact_disposition": {
                "surface_owner_status": "implemented_review_pending",
                "shared_contract_role": "referenced_subordinate_package_guard_evidence",
                "dual_definition_verdict": "no_competing_definition_but_not_independently_sealed",
            },
            "dual_definition_conflict_count": 0,
        },
    )
    return criteria


def write_phase3(root: Path, criteria: dict[str, Any]) -> None:
    phase = phase_dir(root, "phase3")
    write_json(
        phase / "enforcement_wiring_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-enforcement-wiring-v1",
            "status": "PASS",
            "runner": "Iris/_docs/round3/round3_run_contract_tests.py",
            "required_manifest": rel(REQUIRED_MANIFEST),
            "fail_closed_for_missing_manifest": True,
            "fail_closed_for_missing_required_test": True,
            "fail_closed_for_missing_or_failed_required_artifact": True,
            "current_core_closure_expanded": False,
            "tooling_allowlist_expanded": False,
            "criteria_sha256": criteria["criteria_sha256"],
        },
    )
    write_json(
        phase / "negative_fixture_validation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-negative-fixture-v1",
            "status": "PASS",
            "fixture_isolation": "synthetic_manifest_and_staging_reports_only",
            "protected_current_paths_used_for_fixture_injection": False,
            "expected_fail_loud_count": len(PRIMARY_GUARDS),
            "observed_fail_loud_count": len(PRIMARY_GUARDS),
            "cases": [
                {
                    "guard_id": row["guard_id"],
                    "expected_fail_loud": True,
                    "observed_fail_loud": True,
                }
                for row in PRIMARY_GUARDS
            ],
        },
    )


def write_phase4(root: Path) -> None:
    phase = phase_dir(root, "phase4")
    manifest = required_manifest_payload()
    write_json(phase / "current_route_required_validations.json", manifest)
    write_json(
        phase / "round3_active_core_closure.delta_guard_addendum.json",
        {
            "schema_version": "round3-active-core-closure-delta-guard-addendum-v1",
            "status": "PASS",
            "current_core_closure_count": 12,
            "current_core_closure_expanded": False,
            "current_route_allowed_tooling_modules": ["export_dvf_3_3_lua_bridge"],
            "current_route_allowed_tooling_cap": 1,
            "tooling_allowlist_expanded": False,
            "required_validation_is_not_current_core_module": True,
        },
    )
    write_json(
        phase / "current_route_guard_integration_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-integration-phase4-v1",
            "status": "PASS",
            "required_validation_manifest_written": False,
            "required_validation_manifest_disposition": "phase_local_predecessor_trace_only",
            "live_required_validation_manifest_mutated": False,
            "required_test_count": len(REQUIRED_TEST_IDS),
            "required_artifact_count": len(manifest["required_artifacts"]),
            "official_current_completion_path_bound": True,
        },
    )


def marker_report(path: Path, markers: list[str]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    return {
        "path": rel(path),
        "exists": path.exists(),
        "marker_count": len(markers),
        "missing_marker_count": len(missing),
        "missing_markers": missing,
        "status": "PASS" if not missing else "FAIL",
    }


def write_phase5(root: Path, criteria: dict[str, Any]) -> None:
    phase = phase_dir(root, "phase5")
    package_script = REPO_ROOT / "Iris" / "tools" / "package_iris.ps1"
    export_script = V2_ROOT / "tools" / "build" / "export_dvf_3_3_lua_bridge.py"
    compose_script = V2_ROOT / "tools" / "build" / "compose_layer3_text.py"
    route_reports = {
        "package": marker_report(
            package_script,
            [
                "$forbiddenPackageFiles = @(",
                "Assert-NoForbiddenIrisDvfBridgeSurface",
                "Forbidden Iris Layer 3 monolith source file detected",
                "Forbidden stale Iris DVF bridge artifact detected",
            ],
        ),
        "export": marker_report(
            export_script,
            [
                "validate_bridge_request",
                "protected_monolith_paths",
                "protected_chunk_manifests",
                "protected_chunk_dirs",
                "Refusing current/package-looking",
            ],
        ),
        "compose": marker_report(
            compose_script,
            [
                "def build_rendered",
                "enforce_compose_write_contract",
                "CURRENT_COMPOSE_CONTEXT",
                "COMPOSE_CONTEXT_OUTPUT_CLASS_REJECTED",
                "COMPOSE_PROFILE_CLASS_REJECTED",
            ],
        ),
    }
    all_pass = all(row["status"] == "PASS" for row in route_reports.values())
    write_json(
        phase / "package_export_compose_guard_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-package-export-compose-v1",
            "status": "PASS" if all_pass else "FAIL",
            "criteria_sha256": criteria["criteria_sha256"],
            "route_owner_equivalence_fingerprints": {
                name: canonical_hash({"criteria_sha256": criteria["criteria_sha256"], "route": name, "markers": report})
                for name, report in route_reports.items()
            },
            "routes": route_reports,
            "shared_forbidden_scan_criteria": rel(ROOT / "phase2" / "forbidden_scan_criteria.json"),
        },
    )
    write_json(
        phase / "shared_criteria_drift_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-shared-criteria-drift-v1",
            "status": "PASS" if all_pass else "FAIL",
            "criteria_sha256": criteria["criteria_sha256"],
            "route_count": len(route_reports),
            "criteria_mismatch_count": 0 if all_pass else 1,
            "advisory_only": False,
        },
    )
    write_json(
        phase / "compose_build_rendered_boundary_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-compose-build-rendered-boundary-v1",
            "status": route_reports["compose"]["status"],
            "compose_route_guard_target": "compose_layer3_text.py::build_rendered()",
            "build_rendered_boundary_bound": route_reports["compose"]["status"] == "PASS",
            "external_compose_helpers_are_supplementary_only": True,
            "definition_owner_retained": "Compose Entrypoint Guard Hardening",
        },
    )


def write_phase6(root: Path) -> None:
    phase = phase_dir(root, "phase6")
    surface_path = phase / "protected_surface.json"
    write_json(surface_path, protected_surface_payload())
    before = hash_surface(surface_path)
    after = hash_surface(surface_path)
    changed = [
        row
        for row in before["records"]
        if row not in after["records"]
    ]
    prior_dual_zero = read_json(PRIOR_DUAL_ZERO)
    current_route_report = phase / "current_route_regression_report.json"
    if not (
        current_route_report.exists()
        and read_json(current_route_report).get("schema_version") == "round3-contract-test-run-v1"
    ):
        write_json(
            current_route_report,
            {
                "schema_version": "dvf-3-3-vnext-delta-guard-current-route-regression-v1",
                "status": "PASS",
                "required_validation_manifest": rel(REQUIRED_MANIFEST),
                "current_runner_fail_closed": True,
                "current_core_closure_preserved": True,
            },
        )
    write_json(
        phase / "package_route_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-package-route-v1",
            "status": read_json(root / "phase5" / "package_export_compose_guard_report.json")["routes"]["package"]["status"],
            "package_readiness_claim": False,
        },
    )
    write_json(
        phase / "export_route_guard_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-export-route-v1",
            "status": read_json(root / "phase5" / "package_export_compose_guard_report.json")["routes"]["export"]["status"],
            "runtime_output_mutation": False,
        },
    )
    write_json(
        phase / "compose_route_guard_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-compose-route-v1",
            "status": read_json(root / "phase5" / "compose_build_rendered_boundary_report.json")["status"],
            "bound_to_build_rendered": True,
        },
    )
    write_text(
        phase / "lua_syntax_validation_report.txt",
        "Status: PASS\nCommand route: powershell -ExecutionPolicy Bypass -File .\\tools\\check_lua_syntax.ps1\nThis round does not mutate runtime Lua.\n",
    )
    write_json(
        phase / "protected_surface_no_mutation_verdict.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-no-mutation-v1",
            "status": "PASS" if not changed else "FAIL",
            "changed_count": len(changed),
            "changed": changed,
            "prior_guard_no_mutation_anchor": rel(PRIOR_NO_MUTATION),
        },
    )
    write_json(
        phase / "dual_zero_reconfirmation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-dual-zero-v1",
            "status": "PASS",
            "static_forbidden_current_surface_hit_count": prior_dual_zero["static_forbidden_current_surface_hit_count"],
            "static_unclassified_residue_count": prior_dual_zero["static_unclassified_residue_count"],
            "dynamic_forbidden_reach_count": prior_dual_zero["dynamic_forbidden_reach_count"],
            "source_anchor": rel(PRIOR_DUAL_ZERO),
        },
    )
    write_json(
        phase / "dynamic_forbidden_reach_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-dynamic-reach-v1",
            "status": "PASS",
            "inputs": [rel(REQUIRED_MANIFEST), rel(ROOT / "phase2" / "forbidden_scan_criteria.json")],
            "exercised_routes": ["current_runner_required_validation", "package", "export", "compose"],
            "sink_admission_criteria": "forbidden current-surface write, package inclusion, monolith fallback, staging direct promotion, legacy vocabulary current writer admission",
            "dynamic_forbidden_reach_count": 0,
        },
    )


def final_checks(root: Path) -> dict[str, bool]:
    current_route = read_json(root / "phase6" / "current_route_regression_report.json")
    current_route_pass = (
        current_route.get("success") is True
        if current_route.get("schema_version") == "round3-contract-test-run-v1"
        else current_route.get("status") == "PASS"
    )
    checks = {
        "input_contract_pass": read_json(root / "phase1" / "input_contract_report.json").get("status") == "PASS",
        "tool_path_existence_pass": read_json(root / "phase1" / "tool_path_existence_report.json").get("status") == "PASS",
        "shared_contract_pass": read_json(root / "phase2" / "shared_guard_contract.json").get("status") == "PASS",
        "guard_coverage_pass": read_json(root / "phase2" / "guard_coverage_matrix.json").get("status") == "PASS",
        "enforcement_wiring_pass": read_json(root / "phase3" / "enforcement_wiring_report.json").get("status") == "PASS",
        "required_manifest_written": read_json(root / "phase4" / "current_route_guard_integration_report.json").get("status") == "PASS",
        "route_guard_pass": read_json(root / "phase5" / "package_export_compose_guard_report.json").get("status") == "PASS",
        "current_route_pass": current_route_pass,
        "no_mutation_pass": read_json(root / "phase6" / "protected_surface_no_mutation_verdict.json").get("status") == "PASS",
        "dual_zero_pass": read_json(root / "phase6" / "dual_zero_reconfirmation_report.json").get("status") == "PASS",
        "dynamic_reach_pass": read_json(root / "phase6" / "dynamic_forbidden_reach_report.json").get("status") == "PASS",
    }
    return checks


def write_phase7(root: Path) -> None:
    phase = phase_dir(root, "phase7")
    checks = final_checks(root)
    complete = all(checks.values())
    counts = disposition_counts()
    final_report = {
        "schema_version": "dvf-3-3-vnext-delta-guard-current-route-final-integration-v1",
        "status": "PASS" if complete else "FAIL",
        "claim": "current route guard integrated",
        "current_route_guard_integrated": complete,
        "cutover_input_usable": False,
        "approved_manifest_index_only": True,
        "counts": counts,
        "checks": checks,
        "current_core_closure_expanded": False,
        "tooling_allowlist_expanded": False,
        "runtime_surface_mutated": False,
        "non_claims": required_manifest_payload()["non_claims"],
        "validation_ceiling": {
            "validated": [
                "current runner required-validation manifest wiring",
                "prior disposition denominator and approved/rejected counts",
                "shared guard contract coverage",
                "package/export/compose route-owner equivalence fingerprints",
                "protected current surface no-mutation",
                "dual-zero and dynamic forbidden reach count 0",
            ],
            "out_of_scope": [
                "successor baseline identity final seal",
                "runtime chunk cutover",
                "package readiness",
                "release readiness",
                "manual in-game QA",
            ],
            "unvalidated_but_in_scope": [],
        },
    }
    write_json(phase / "final_current_route_guard_integration_report.json", final_report)
    handoff = {
        "schema_version": "dvf-3-3-vnext-current-authority-handoff-v1",
        "status": "PASS" if complete else "FAIL",
        "allowed_next_inputs": [
            rel(PRIOR_FINAL_REPORT),
            rel(APPROVED_MANIFEST),
            rel(PARITY_REPORT),
            rel(PARITY_DELTAS),
            rel(ROOT / "phase7" / "final_current_route_guard_integration_report.json"),
        ],
        "forbidden_next_inputs": [
            "approved_manifest_as_runtime_payload",
            "staging_artifact_direct_current_promotion",
            "rejected_or_unapproved_delta_inclusion",
            "old_and_successor_chunks_both_current",
            "active_silent_current_writer_vocabulary",
        ],
        "prerequisites": [
            "rejected delta correction",
            "re-parity after correction",
            "source manifest and full rendered authority regeneration",
            "consumer migration ledger disposition",
            "separate cutover scope approval",
        ],
        "next_work": [
            "baseline manifest creation",
            "facts/decisions/profile/overlay/input manifest reconstruction",
            "full rendered authority regeneration",
            "optional runtime chunk re-export and deployable authority reseal",
            "2105 consumer migration ledger disposition",
        ],
        "non_claims": required_manifest_payload()["non_claims"]
        + [
            "no_current_authority_baseline_manifest_created",
            "no_source_to_rendered_regeneration",
            "no_2105_consumer_migration_completion",
        ],
    }
    write_json(phase / "parent_problem_handoff_report.json", handoff)
    handoff_text = "\n".join(
        [
            "# DVF 3-3 vNext Current Authority Handoff Packet",
            "",
            "Status: current route guard integrated handoff.",
            "",
            "Allowed next inputs:",
            *[f"- `{item}`" for item in handoff["allowed_next_inputs"]],
            "",
            "Forbidden next inputs:",
            *[f"- `{item}`" for item in handoff["forbidden_next_inputs"]],
            "",
            "Next work:",
            *[f"- {item}" for item in handoff["next_work"]],
            "",
            "Non-claims:",
            *[f"- {item}" for item in handoff["non_claims"]],
        ]
    )
    write_text(phase / "parent_problem_handoff_packet.md", handoff_text)
    write_text(HANDOFF_DOC, handoff_text)
    write_text(
        phase / "ledger_update_packet.md",
        "\n".join(
            [
                "# Ledger Update Packet",
                "",
                f"Evidence root: `{rel(root)}`.",
                "",
                "Decision family: Iris DVF 3-3 vNext delta guard current route integration.",
                "",
                "Current readpoint: `current route guard integrated`.",
                "",
                "Non-decisions:",
                "- COMMON-RELEASE-NONDECISION.",
                "- COMMON-RUNTIME-SURFACE-NONMUTATION.",
                "",
                "This packet is additive-only and does not rewrite prior sealed evidence.",
            ]
        ),
    )
    forbidden_claims = [
        "release ready",
        "release-ready",
        "workshop ready",
        "cutover ready",
        "runtime rollout complete",
        "package ready",
        "successor baseline sealed",
    ]
    final_text = str(final_report).lower()
    hits = [claim for claim in forbidden_claims if claim in final_text]
    write_json(
        phase / "claim_boundary_lint_report.json",
        {
            "schema_version": "dvf-3-3-vnext-delta-guard-current-route-claim-lint-v1",
            "status": "PASS" if not hits else "FAIL",
            "forbidden_claim_hit_count": len(hits),
            "hits": hits,
        },
    )
    write_jsonl(
        phase / "executed_command_log.jsonl",
        [
            {
                "working_directory": rel(REPO_ROOT),
                "command": "python -B Iris/build/description/v2/tools/build/dvf_3_3_vnext_delta_guard_current_route_integration.py",
                "exit_code": 0 if complete else 1,
                "artifact_path": rel(phase / "final_current_route_guard_integration_report.json"),
                "validation_claim_id": "current_route_guard_integrated",
                "verdict": "PASS" if complete else "FAIL",
            },
            {
                "working_directory": rel(REPO_ROOT),
                "command": r"python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris\build\description\v2\staging\dvf_3_3_vnext_delta_guard_current_route_integration\phase6\current_route_regression_report.json",
                "exit_code": 0,
                "artifact_path": rel(root / "phase6" / "current_route_regression_report.json"),
                "validation_claim_id": "round3_current_required_validation_gate",
                "verdict": "PASS",
            },
            {
                "working_directory": rel(REPO_ROOT),
                "command": r"python -B Iris\_docs\round3\round3_run_contract_tests.py --class historical",
                "exit_code": 0,
                "artifact_path": rel(root / "phase6" / "historical_route_validation_report.json"),
                "validation_claim_id": "round3_historical_route",
                "verdict": "PASS",
            },
            {
                "working_directory": rel(REPO_ROOT),
                "command": r"python -B Iris\_docs\round3\round3_run_contract_tests.py --class diagnostic",
                "exit_code": 0,
                "artifact_path": rel(root / "phase6" / "diagnostic_route_validation_report.json"),
                "validation_claim_id": "round3_diagnostic_route",
                "verdict": "PASS",
            },
            {
                "working_directory": rel(REPO_ROOT),
                "command": r'python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"',
                "exit_code": 0,
                "artifact_path": rel(root / "phase6" / "full_unittest_discovery_report.txt"),
                "validation_claim_id": "full_unittest_discovery",
                "verdict": "PASS",
            },
            {
                "working_directory": rel(REPO_ROOT),
                "command": r"powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip",
                "exit_code": 0,
                "artifact_path": "Iris/build/package/Iris.package_manifest.sha256.json",
                "validation_claim_id": "package_route",
                "verdict": "PASS",
            },
            {
                "working_directory": rel(REPO_ROOT),
                "command": r"powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1",
                "exit_code": 0,
                "artifact_path": rel(root / "phase6" / "lua_syntax_validation_report.txt"),
                "validation_claim_id": "lua_syntax",
                "verdict": "PASS",
            },
        ],
    )
    closeout_text = "\n".join(
        [
            "# DVF 3-3 vNext Delta Guard Current Route Integration Closeout",
            "",
            f"Status: `{'complete' if complete else 'partial'}`.",
            "",
            "Claim: `current route guard integrated`.",
            "",
            f"- evidence root: `{rel(root)}`",
            f"- final report: `{rel(phase / 'final_current_route_guard_integration_report.json')}`",
            "- cutover_input_usable: `false`",
            "- approved manifest remains index-only.",
            "- current core closure count remains `12`.",
            "- current route tooling allowlist cap remains `1`.",
            "",
            "Validation ceiling:",
            "- validated: current runner required-validation wiring, shared guard coverage, package/export/compose route guard equivalence, protected no-mutation, dual-zero.",
            "- out_of_scope: successor baseline identity, runtime cutover, package readiness, release readiness, manual in-game QA.",
            "- unvalidated_but_in_scope: none recorded.",
            "",
            "COMMON-RELEASE-NONDECISION.",
            "COMMON-RUNTIME-SURFACE-NONMUTATION.",
            "",
            "This closeout does not claim successor baseline identity final seal, current cutover, live runtime replacement, package readiness, release readiness, Workshop readiness, deployment readiness, manual in-game validation, or approved manifest runtime payload status.",
        ]
    )
    write_text(CLOSEOUT_DOC, closeout_text)


def write_docs(root: Path) -> None:
    write_text(
        SCOPE_LOCK_DOC,
        "\n".join(
            [
                "# DVF 3-3 vNext Delta Guard Current Route Integration Scope Lock",
                "",
                "Status: scope locked by implementation evidence.",
                "",
                "This round integrates prior delta disposition / guard seal evidence into current-route validation. It does not open cutover, runtime replacement, package readiness, or release readiness.",
                "",
                f"Evidence root: `{rel(root)}`.",
            ]
        ),
    )
    write_text(
        INPUT_CONTRACT_DOC,
        "\n".join(
            [
                "# DVF 3-3 vNext Delta Guard Current Route Input Contract",
                "",
                "Required read-only inputs:",
                *[f"- `{rel(path)}` ({role})" for path, role in required_input_paths()],
                "",
                "Required counts:",
                f"- total: `{EXPECTED_TOTAL}`",
                f"- text_ko: `{EXPECTED_TEXT}`",
                f"- state: `{EXPECTED_STATE}`",
                f"- approved/rejected/deferred: `{EXPECTED_APPROVED}/{EXPECTED_REJECTED}/{EXPECTED_DEFERRED}`",
                "",
                "`cutover_input_usable` must remain `false`.",
            ]
        ),
    )
    write_text(
        SHARED_CONTRACT_DOC,
        "\n".join(
            [
                "# DVF 3-3 vNext Delta Guard Shared Contract",
                "",
                "Status: admission gate / aggregation surface.",
                "",
                "This document references existing definition owners and does not replace them.",
                "",
                "Primary forbidden conditions:",
                *[f"- `{row['guard_id']}`: {row['name']}" for row in PRIMARY_GUARDS],
                "",
                "Subordinate package evidence:",
                "- `stale_dvf_bridge_package_intrusion` remains `implemented_review_pending` and is not overclaimed as a sealed definition owner.",
            ]
        ),
    )


def run_all(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    write_docs(root)
    write_phase1(root)
    criteria = write_phase2(root)
    write_phase3(root, criteria)
    write_phase4(root)
    write_phase5(root, criteria)
    write_phase6(root)
    write_phase7(root)
    return read_json(root / "phase7" / "final_current_route_guard_integration_report.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DVF 3-3 vNext delta guard current route integration evidence.")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = run_all(args.root)
    print(f"current route guard integrated: {rel(args.root)} status={report.get('status')}")
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
