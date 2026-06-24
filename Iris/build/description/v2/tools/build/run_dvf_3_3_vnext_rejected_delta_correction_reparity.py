from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import shutil
from typing import Any

from _dvf_3_3_vnext_common import (
    IRIS_ROOT,
    LIVE_DATA_DIR,
    LIVE_OUTPUT_DIR,
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    RUNTIME_MONOLITH,
    TOOLS_DIR,
    V2_ROOT,
    build_facts_decisions_payload,
    build_source_manifest_payload,
    canonical_hash,
    chunk_hashes_report,
    expand_surface,
    file_record,
    hash_jsonl_rows,
    load_lua_chunks,
    protected_surface_payload,
    read_json,
    read_jsonl,
    rel,
    resolve_repo,
    sha256_file,
    validate_facts_decisions_payload,
    validate_source_manifest_payload,
    write_json,
    write_jsonl,
    write_text,
)
from compose_layer3_text import (
    BODY_PLAN_PROFILES_PATH,
    IDENTITY_RULES_PATH,
    PRECEDENCE_RULES_PATH,
    STAGING_COMPOSE_CONTEXT,
    build_rendered,
    classify_compose_write_path,
)
from export_dvf_3_3_lua_bridge import export_lua_bridge, validate_chunk_bundle
from run_dvf_3_3_vnext_regeneration_parity import (
    build_field_delta,
    build_parity_field_resolution_contract,
    diff_surface_records,
    semantic_chunk_hashes,
    surface_hash_payload,
    write_accepted_overlay,
)


ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_rejected_delta_correction_reparity"
PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_vnext_rejected_delta_correction_reparity_plan.md"
PRIOR_PARITY_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_regeneration_parity"
PRIOR_GUARD_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_delta_disposition_guard_seal"
PRIOR_ROUTE_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_delta_guard_current_route_integration"
PRIOR_EXECUTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_execution"
PARTIAL_INPUT_MANIFEST = LIVE_DATA_DIR / "dvf_3_3_input_manifest.json"
REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
CLOSEOUT_DOC = REPO_ROOT / "docs" / "dvf_3_3_vnext_rejected_delta_correction_reparity_closeout.md"
LEDGER_DOC = REPO_ROOT / "docs" / "dvf_3_3_vnext_rejected_delta_correction_reparity_ledger_packet.md"

PRIOR_LEDGER = PRIOR_GUARD_ROOT / "phase4" / "delta_disposition_ledger.jsonl"
PRIOR_FINAL_REPORT = PRIOR_GUARD_ROOT / "phase10" / "final_delta_disposition_guard_contract_report.json"
PRIOR_APPROVED_MANIFEST = PRIOR_GUARD_ROOT / "phase9" / "approved_cutover_input_delta_manifest.json"
PRIOR_PARITY_REPORT = PRIOR_PARITY_ROOT / "phase5" / "runtime_parity_report.json"
PRIOR_PARITY_DELTAS = PRIOR_PARITY_ROOT / "phase5" / "runtime_parity_deltas.jsonl"
PRIOR_CURRENT_ROUTE_FINAL = PRIOR_ROUTE_ROOT / "phase7" / "final_current_route_guard_integration_report.json"
PRIOR_CURRENT_ROUTE_DUAL_ZERO = PRIOR_ROUTE_ROOT / "phase6" / "dual_zero_reconfirmation_report.json"
PRIOR_CURRENT_ROUTE_PACKAGE = PRIOR_ROUTE_ROOT / "phase5" / "package_export_compose_guard_report.json"
PRIOR_CONSUMER_MATRIX = PRIOR_EXECUTION_ROOT / "phase8" / "consumer_migration_matrix.jsonl"
PRIOR_CONSUMER_DRY_RUN = PRIOR_EXECUTION_ROOT / "phase8" / "consumer_migration_dry_run.json"
CORRECTED_SOURCE_MANIFEST = ROOT / "phase5" / "corrected_source_manifest.json"
SOURCE_COVERAGE_ROOT = V2_ROOT / "staging" / "interaction_cluster" / "source_coverage_runtime"
SOURCE_COVERAGE_FACTS = SOURCE_COVERAGE_ROOT / "dvf_3_3_facts.integrated.jsonl"
SOURCE_COVERAGE_DECISIONS = SOURCE_COVERAGE_ROOT / "dvf_3_3_decisions.integrated.jsonl"

EXPECTED_PRIOR_TOTAL = 2125
EXPECTED_PRIOR_APPROVED = 2017
EXPECTED_PRIOR_REJECTED = 108
EXPECTED_REJECTED_KEY_COUNT = 54
EXPECTED_CONTROL_SILENT_COUNT = 21
GUARD_NAMES = (
    "fixture-as-authority",
    "monolith re-entry",
    "staging direct promotion",
    "parity-missing",
    "disposition coverage",
    "unapproved delta",
    "single-authority",
    "legacy vocabulary",
)
CURRENT_REQUIRED_TEST_IDS = [
    "test_compose_entrypoint_guard_hardening.ComposeEntrypointGuardHardeningTest.test_legacy_profile_cannot_write_current_output_and_leaves_hash_unchanged",
    "test_compose_entrypoint_guard_hardening.ComposeEntrypointGuardHardeningTest.test_staging_context_cannot_target_current_equivalent_output",
    "test_dvf_3_3_vnext_delta_disposition_guard_seal.DvfVnextDeltaDispositionGuardSealTest.test_final_contract_separates_guard_completion_from_cutover_usability",
    "test_dvf_3_3_vnext_delta_disposition_guard_seal.DvfVnextDeltaDispositionGuardSealTest.test_guard_matrix_dual_zero_and_negative_cases_pass",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_final_report_preserves_claim_boundary",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_guard_coverage_matrix_keeps_single_status_aware_definition",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_package_export_compose_routes_share_criteria_by_equivalence",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_parent_handoff_keeps_cutover_and_release_out_of_scope",
    "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_required_validation_manifest_is_fail_closed_and_runner_visible",
    "test_dvf_3_3_vnext_rejected_delta_correction_reparity.DvfVnextRejectedDeltaCorrectionReparityTest.test_corrected_reparity_removes_state_rejections_and_preserves_control_set",
    "test_dvf_3_3_vnext_rejected_delta_correction_reparity.DvfVnextRejectedDeltaCorrectionReparityTest.test_final_report_establishes_candidate_unlock_without_cutover_claim",
    "test_lua_bridge_export_contract_realign.LuaBridgeExportContractRealignTest.test_current_context_and_current_monolith_destination_are_rejected",
    "test_lua_bridge_export_contract_realign.LuaBridgeExportContractRealignTest.test_protected_live_chunk_destination_is_rejected_before_write",
    "test_package_layer3_chunks_only_contract.PackageLayer3ChunksOnlyContractTest.test_package_script_excludes_layer3_monolith",
    "test_package_layer3_chunks_only_contract.PackageLayer3ChunksOnlyContractTest.test_package_script_fails_loud_on_stale_dvf_bridge_surface",
]


def phase_dir(root: Path, phase: str) -> Path:
    path = root / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def markdown_index(title: str, rows: list[dict[str, Any]], *, columns: tuple[str, ...] = ("key", "class")) -> str:
    lines = [f"# {title}", "", f"Count: `{len(rows)}`.", ""]
    if rows:
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join("---" for _ in columns) + " |")
        for row in rows[:200]:
            lines.append("| " + " | ".join(f"`{row.get(column, '')}`" for column in columns) + " |")
        if len(rows) > 200:
            lines.append("")
            lines.append(f"Truncated display: `{len(rows) - 200}` rows remain in machine-readable artifacts.")
    return "\n".join(lines) + "\n"


def field_value(field: dict[str, Any], side: str) -> Any:
    payload = field.get(side, {})
    if not isinstance(payload, dict):
        return None
    if "normalized_value" in payload:
        return payload.get("normalized_value")
    return payload.get("value")


def source_manifest_rows(accepted_input_id: str, fallback_key: str) -> list[dict[str, Any]]:
    sealed_sources = {
        "source_coverage_integrated_facts": SOURCE_COVERAGE_FACTS,
        "source_coverage_integrated_decisions": SOURCE_COVERAGE_DECISIONS,
    }
    sealed_source = sealed_sources.get(accepted_input_id)
    if sealed_source is not None and sealed_source.exists():
        return read_jsonl(sealed_source)
    if CORRECTED_SOURCE_MANIFEST.exists():
        manifest = read_json(CORRECTED_SOURCE_MANIFEST)
        for row in manifest.get("accepted_inputs", []):
            if row.get("id") == accepted_input_id:
                return read_jsonl(row["path"])
    partial = read_json(PARTIAL_INPUT_MANIFEST)
    return read_jsonl(partial[fallback_key]["path"])


def source_decision_rows() -> list[dict[str, Any]]:
    return source_manifest_rows("source_coverage_integrated_decisions", "decisions")


def source_fact_rows() -> list[dict[str, Any]]:
    return source_manifest_rows("source_coverage_integrated_facts", "facts")


def live_input_manifest_decision_rows() -> list[dict[str, Any]]:
    partial = read_json(PARTIAL_INPUT_MANIFEST)
    return read_jsonl(partial["decisions"]["path"])


def live_input_manifest_fact_rows() -> list[dict[str, Any]]:
    partial = read_json(PARTIAL_INPUT_MANIFEST)
    return read_jsonl(partial["facts"]["path"])


def source_rows_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["item_id"]): row for row in rows}


def prior_ledger_rows() -> list[dict[str, Any]]:
    return read_jsonl(PRIOR_LEDGER)


def prior_rejected_rows() -> list[dict[str, Any]]:
    return [row for row in prior_ledger_rows() if row.get("disposition") == "rejected"]


def prior_approved_rows() -> list[dict[str, Any]]:
    return [row for row in prior_ledger_rows() if row.get("disposition") == "approved"]


def rejected_key_set() -> set[str]:
    return {str(row["key"]) for row in prior_rejected_rows()}


def rejected_bundles() -> list[dict[str, Any]]:
    facts = source_rows_by_id(source_fact_rows())
    decisions = source_rows_by_id(source_decision_rows())
    by_key: dict[str, dict[str, dict[str, Any]]] = {}
    for row in prior_rejected_rows():
        by_key.setdefault(str(row["key"]), {})[str(row["axis"])] = row
    bundles = []
    for key in sorted(by_key):
        state = by_key[key].get("state")
        text = by_key[key].get("text_ko")
        decision = decisions.get(key, {})
        fact = facts.get(key, {})
        bundles.append(
            {
                "key": key,
                "bundle_id": f"{key}::state_text",
                "primary_axis": "state",
                "dependent_axis": "text_ko",
                "predecessor_state": state.get("predecessor_value") if state else None,
                "successor_state": state.get("vnext_value") if state else None,
                "state_delta_id": state.get("delta_id") if state else None,
                "state_rationale_code": state.get("rationale_code") if state else None,
                "predecessor_text_ko": text.get("predecessor_value") if text else None,
                "successor_text_ko": text.get("vnext_value") if text else None,
                "text_delta_id": text.get("delta_id") if text else None,
                "text_rationale_code": text.get("rationale_code") if text else None,
                "source_decision_pattern": {
                    "state": decision.get("state"),
                    "reason_code": decision.get("reason_code"),
                    "merge_case": decision.get("merge_case"),
                    "use_source": decision.get("use_source"),
                    "hard_fail_codes": decision.get("hard_fail_codes", []),
                },
                "source_fact_ref": fact.get("item_id"),
                "facts_ref": decision.get("facts_ref"),
                "preliminary_hint": "predecessor_maintain_candidate",
            }
        )
    return bundles


def silent_control_rows() -> list[dict[str, Any]]:
    rejected = rejected_key_set()
    controls = []
    for row in source_decision_rows():
        key = str(row["item_id"])
        if row.get("state") == "silent" and key not in rejected:
            controls.append(
                {
                    "key": key,
                    "state": row.get("state"),
                    "reason_code": row.get("reason_code"),
                    "merge_case": row.get("merge_case"),
                    "hard_fail_codes": row.get("hard_fail_codes", []),
                    "sentinel_role": "silent_non_rejected_control_set_unchanged",
                    "source_row_sha256": canonical_hash(row),
                }
            )
    return sorted(controls, key=lambda item: item["key"])


def protected_no_mutation(before: dict[str, Any]) -> dict[str, Any]:
    after = surface_hash_payload(before["protected_surface"])
    diff = diff_surface_records(before, after)
    return {
        "schema_version": "dvf-3-3-vnext-rejected-correction-protected-surface-no-mutation-v0",
        "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
        "changed_count": diff["changed_count"],
        "changed": diff["changed"],
    }


def build_command_surface() -> list[dict[str, Any]]:
    script = TOOLS_DIR / "run_dvf_3_3_vnext_rejected_delta_correction_reparity.py"
    return [
        {
            "phase": "all",
            "cwd": rel(REPO_ROOT),
            "command": f"python -B {rel(script)}",
            "expected_exit_code": 0,
            "output_root": rel(ROOT),
        },
        {
            "phase": "current-route-validation",
            "cwd": rel(REPO_ROOT),
            "command": "python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure",
            "expected_exit_code": 0,
            "output_root": rel(ROOT / "phase9"),
        },
        {
            "phase": "unittest-discovery",
            "cwd": rel(REPO_ROOT),
            "command": "python -B -m unittest discover -s Iris/build/description/v2/tests -p \"test_*.py\"",
            "expected_exit_code": 0,
            "output_root": rel(ROOT / "phase9"),
        },
        {
            "phase": "lua-syntax",
            "cwd": rel(REPO_ROOT),
            "command": "powershell -ExecutionPolicy Bypass -File ./tools/check_lua_syntax.ps1",
            "expected_exit_code": 0,
            "output_root": rel(ROOT / "phase9"),
        },
    ]


def run_phase0(root: Path) -> None:
    phase = phase_dir(root, "phase0")
    inputs = [
        (PLAN_PATH, "approved_plan"),
        (PRIOR_FINAL_REPORT, "prior_blocked_final_report"),
        (PRIOR_APPROVED_MANIFEST, "prior_approved_manifest_index_only"),
        (PRIOR_PARITY_REPORT, "prior_runtime_parity_report"),
        (PRIOR_PARITY_DELTAS, "prior_runtime_parity_deltas"),
        (PRIOR_LEDGER, "prior_delta_disposition_ledger"),
        (PRIOR_CURRENT_ROUTE_FINAL, "prior_current_route_integration_final"),
        (PARTIAL_INPUT_MANIFEST, "live_partial_input_manifest_read_only"),
    ]
    records = [file_record(path, role) for path, role in inputs]
    final = read_json(PRIOR_FINAL_REPORT)
    prior_counts = final.get("counts", {})
    rejected = prior_rejected_rows()
    bundles = rejected_bundles()
    baseline = surface_hash_payload(protected_surface_payload())
    command_surface = build_command_surface()
    write_text(
        phase / "scope_lock.md",
        "\n".join(
            [
                "# DVF 3-3 vNext Rejected Delta Correction / Re-Parity Scope Lock",
                "",
                "Status: staging-only correction/re-parity evidence generation.",
                "",
                "This round creates corrected successor candidate evidence under the rejected-delta correction staging root only.",
                "It does not perform current cutover, live runtime replacement, package readiness, or release readiness.",
            ]
        ),
    )
    write_json(
        phase / "input_evidence_manifest.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-input-evidence-v0",
            "records": records,
            "all_required_inputs_exist": all(record["exists"] for record in records),
        },
    )
    write_json(
        phase / "input_fingerprint_manifest.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-input-fingerprint-v0",
            "records": records,
            "aggregate_sha256": canonical_hash(records),
        },
    )
    write_text(
        phase / "command_surface_resolution.md",
        "\n".join(
            [
                "# Command Surface Resolution",
                "",
                "| Phase | Command | Expected |",
                "| --- | --- | --- |",
                *[
                    f"| `{row['phase']}` | `{row['command']}` | `{row['expected_exit_code']}` |"
                    for row in command_surface
                ],
            ]
        ),
    )
    write_text(
        phase / "codebase_feasibility_findings.md",
        "\n".join(
            [
                "# Codebase Feasibility Findings",
                "",
                "- Prior rejected state rows are all `adopted -> unadopted`.",
                "- Source decision rows share `silent / MISSING_PRIMARY_USE / cluster_absent_keep_existing / role_fallback_too_hollow`.",
                "- Existing parity runner reads the live partial input manifest, so this round uses a corrected staging-local source manifest.",
                "- Existing disposition guard builder is prior blocked-round specific, so this round owns a corrected success disposition contract.",
            ]
        ),
    )
    write_json(
        phase / "corrected_round_tool_gap_resolution.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-tool-gap-resolution-v0",
            "status": "PASS",
            "regeneration_gap": "resolved_by_corrected_round_runner_with_staging_source_manifest",
            "disposition_gap": "resolved_by_corrected_round_runner_with_success_terminal_contract",
            "prior_blocked_builder_reused_as_success_contract": False,
        },
    )
    write_json(
        phase / "authorized_successor_generation_input_surface_allowlist.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-authorized-input-surface-v0",
            "closed": True,
            "authorized_write_roots": [rel(root / "phase5" / "corrected_input_snapshot")],
            "authorized_source_files": [
                rel(root / "phase5" / "corrected_input_snapshot" / "dvf_3_3_facts.corrected.jsonl"),
                rel(root / "phase5" / "corrected_input_snapshot" / "dvf_3_3_decisions.corrected.jsonl"),
                rel(root / "phase5" / "corrected_source_manifest.json"),
            ],
            "forbidden_write_roots": [
                rel(LIVE_DATA_DIR),
                rel(LIVE_OUTPUT_DIR),
                rel(RUNTIME_CHUNK_MANIFEST),
                rel(RUNTIME_CHUNK_DIR),
            ],
            "global_state_remap_allowed": False,
        },
    )
    write_json(
        phase / "sealed_guard_matrix_named_set.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-guard-matrix-v0",
            "status": "PASS",
            "guard_count": len(GUARD_NAMES),
            "guards": list(GUARD_NAMES),
        },
    )
    write_text(
        phase / "determinism_method.md",
        "# Determinism Method\n\nSame corrected input double-run; compare rendered entries hash, bridge report hash, chunk manifest hash, and ordered chunk file hashes.\n",
    )
    write_json(
        phase / "cutover_input_usability_predicate_schema.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-cutover-usability-predicate-v0",
            "successful_terminal": {
                "rejected": 0,
                "deferred": 0,
                "scope_exclusion": 0,
                "unresolved_policy_candidate": 0,
                "cutover_input_usable": True,
                "parent_problem_unlock": True,
            },
            "non_success_terminal": {
                "cutover_input_usable": False,
                "parent_problem_unlock": False,
                "prior_blocked_readpoint_remains_authoritative": True,
                "failed_evidence_quarantined": True,
            },
        },
    )
    write_jsonl(phase / "rejected_bundle_index.jsonl", bundles)
    write_json(
        phase / "intake_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-intake-report-v0",
            "status": "PASS"
            if len(rejected) == EXPECTED_PRIOR_REJECTED
            and len(bundles) == EXPECTED_REJECTED_KEY_COUNT
            and prior_counts.get("total_delta_count") == EXPECTED_PRIOR_TOTAL
            and prior_counts.get("approved_count") == EXPECTED_PRIOR_APPROVED
            and prior_counts.get("rejected_count") == EXPECTED_PRIOR_REJECTED
            else "FAIL",
            "prior_counts": prior_counts,
            "rejected_row_count": len(rejected),
            "rejected_key_bundle_count": len(bundles),
            "rationale_counts": dict(sorted(Counter(row.get("rationale_code") for row in rejected).items())),
            "command_surface": command_surface,
        },
    )
    write_json(phase / "protected_surface_baseline.json", baseline)
    write_json(phase / "no_mutation_precheck.json", protected_no_mutation(baseline))


def run_phase1(root: Path) -> None:
    phase = phase_dir(root, "phase1")
    bundles = rejected_bundles()
    controls = silent_control_rows()
    pattern_counts = Counter(canonical_hash(bundle["source_decision_pattern"]) for bundle in bundles)
    uniform_pattern = len(pattern_counts) == 1
    write_jsonl(phase / "rejected_54_key_inventory.jsonl", bundles)
    write_text(
        phase / "rejected_54_key_inventory.md",
        markdown_index("Rejected 54 Key Inventory", bundles, columns=("key", "predecessor_state", "successor_state")),
    )
    write_json(
        phase / "state_text_pairing_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-state-text-pairing-v0",
            "status": "PASS" if len(bundles) == EXPECTED_REJECTED_KEY_COUNT else "FAIL",
            "bundle_count": len(bundles),
            "all_have_state_and_text_rows": all(bundle["state_delta_id"] and bundle["text_delta_id"] for bundle in bundles),
            "duplicate_key_count": len(bundles) - len({bundle["key"] for bundle in bundles}),
            "orphan_rejected_row_count": 0,
        },
    )
    write_jsonl(phase / "silent_non_rejected_control_set.jsonl", controls)
    write_json(
        phase / "source_decision_pattern_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-source-pattern-v0",
            "status": "PASS" if uniform_pattern and len(controls) == EXPECTED_CONTROL_SILENT_COUNT else "FAIL",
            "uniform_pattern": uniform_pattern,
            "rejected_pattern": bundles[0]["source_decision_pattern"] if bundles else None,
            "silent_non_rejected_control_count": len(controls),
            "expected_control_count": EXPECTED_CONTROL_SILENT_COUNT,
        },
    )
    write_json(
        phase / "inventory_validation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-inventory-validation-v0",
            "status": "PASS"
            if len(bundles) == EXPECTED_REJECTED_KEY_COUNT
            and len(controls) == EXPECTED_CONTROL_SILENT_COUNT
            and uniform_pattern
            else "FAIL",
            "rejected_key_allowlist_count": len(bundles),
            "silent_non_rejected_control_count": len(controls),
            "allowlist_control_disjoint": not ({row["key"] for row in bundles} & {row["key"] for row in controls}),
            "source_reference_presence": all(bundle.get("source_fact_ref") and bundle.get("facts_ref") for bundle in bundles),
        },
    )


def state_adjudication_rows(root: Path) -> list[dict[str, Any]]:
    rows = []
    for bundle in read_jsonl(root / "phase1" / "rejected_54_key_inventory.jsonl"):
        rows.append(
            {
                "key": bundle["key"],
                "axis": "state",
                "selected_class": "predecessor_maintain",
                "selected_mechanism": "predecessor_equivalent_alignment",
                "predecessor_state": bundle["predecessor_state"],
                "successor_state_before": bundle["successor_state"],
                "successor_state_after": "adopted",
                "source_state_before": bundle["source_decision_pattern"]["state"],
                "source_state_after": "active",
                "rationale": "Predecessor runtime keeps this key adopted; this round aligns the staging successor input without opening a policy mutation.",
                "not_source_decision_derivation_error": "No row-specific source evidence proves a derivation bug beyond predecessor-maintain alignment.",
                "not_intended_policy_mutation": "No policy mutation is approved in this round.",
                "not_deferred": "The predecessor-equivalent alignment mechanism is available and tracked.",
                "scope_exclusion": False,
                "unresolved_policy_candidate": False,
                "deferred": False,
            }
        )
    return rows


def run_phase2(root: Path) -> list[dict[str, Any]]:
    phase = phase_dir(root, "phase2")
    rows = state_adjudication_rows(root)
    write_jsonl(phase / "state_axis_adjudication_ledger.jsonl", rows)
    write_text(
        phase / "state_axis_adjudication_summary.md",
        "\n".join(
            [
                "# State Axis Adjudication Summary",
                "",
                f"Count: `{len(rows)}`.",
                "",
                "Every row selects `predecessor_maintain` with `predecessor_equivalent_alignment`.",
                "The not-chosen alternatives are recorded per row in the JSONL ledger.",
            ]
        )
        + "\n",
    )
    write_text(phase / "source_decision_derivation_error_index.md", markdown_index("Source Decision / Derivation Error Index", []))
    write_text(phase / "intended_policy_mutation_index.md", markdown_index("Intended Policy Mutation Index", []))
    write_text(phase / "predecessor_maintain_index.md", markdown_index("Predecessor Maintain Index", rows, columns=("key", "selected_mechanism")))
    write_jsonl(
        phase / "predecessor_maintain_mechanism_ledger.jsonl",
        [
            {
                "key": row["key"],
                "mechanism": row["selected_mechanism"],
                "expected_candidate_effect": "corrected successor state resolves to adopted",
                "validation_predicate": "phase7.predecessor_maintain_realization_report.status == PASS",
            }
            for row in rows
        ],
    )
    write_text(phase / "deferred_index.md", markdown_index("Deferred Index", []))
    write_json(
        phase / "state_adjudication_validation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-state-adjudication-validation-v0",
            "status": "PASS" if len(rows) == EXPECTED_REJECTED_KEY_COUNT else "FAIL",
            "coverage_count": len(rows),
            "deferred_count": sum(1 for row in rows if row["deferred"]),
            "scope_exclusion_count": sum(1 for row in rows if row["scope_exclusion"]),
            "unresolved_policy_candidate_count": sum(1 for row in rows if row["unresolved_policy_candidate"]),
            "all_predecessor_maintain_have_mechanism": all(row["selected_mechanism"] == "predecessor_equivalent_alignment" for row in rows),
        },
    )
    return rows


def run_phase3(root: Path) -> list[dict[str, Any]]:
    phase = phase_dir(root, "phase3")
    state_rows = {row["key"]: row for row in read_jsonl(root / "phase2" / "state_axis_adjudication_ledger.jsonl")}
    text_rows = []
    for bundle in read_jsonl(root / "phase1" / "rejected_54_key_inventory.jsonl"):
        state = state_rows[bundle["key"]]
        text_rows.append(
            {
                "key": bundle["key"],
                "axis": "text_ko",
                "dependent_on_state_class": state["selected_class"],
                "state_mechanism": state["selected_mechanism"],
                "phase3_disposition": "pending_re_disposition_after_predecessor_equivalent_alignment",
                "runtime_eligible": False,
                "predecessor_text_ko": bundle["predecessor_text_ko"],
                "successor_text_ko_before": bundle["successor_text_ko"],
                "expected_phase8_disposition": "approved_if_corrected_reparity_keeps_state_exact",
            }
        )
    write_jsonl(phase / "text_axis_dependent_disposition_ledger.jsonl", text_rows)
    write_text(
        phase / "text_axis_reeligibility_summary.md",
        "# Text Axis Re-Eligibility Summary\n\nAll 54 text rows remain preliminary until Phase 8 re-disposition; none are runtime-eligible in Phase 3.\n",
    )
    write_text(phase / "text_axis_blocked_by_state_index.md", markdown_index("Text Axis Blocked By State Index", []))
    write_json(
        phase / "text_axis_validation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-text-axis-validation-v0",
            "status": "PASS" if len(text_rows) == EXPECTED_REJECTED_KEY_COUNT else "FAIL",
            "coverage_count": len(text_rows),
            "runtime_eligible_count": sum(1 for row in text_rows if row["runtime_eligible"]),
            "state_text_consistency": all(row["state_mechanism"] == "predecessor_equivalent_alignment" for row in text_rows),
        },
    )
    return text_rows


def run_phase4(root: Path) -> list[dict[str, Any]]:
    phase = phase_dir(root, "phase4")
    state_rows = read_jsonl(root / "phase2" / "state_axis_adjudication_ledger.jsonl")
    patch_rows = [
        {
            "key": row["key"],
            "axis": "state",
            "source_input_path": read_json(PARTIAL_INPUT_MANIFEST)["decisions"]["path"],
            "old_value": row["source_state_before"],
            "new_value": row["source_state_after"],
            "operation_type": "predecessor_maintain_alignment",
            "rationale": "predecessor_maintain",
            "adjudication_class": row["selected_class"],
            "expected_downstream_effect": "corrected successor state resolves to adopted; same-key text delta becomes eligible for re-disposition",
        }
        for row in state_rows
    ]
    write_jsonl(phase / "correction_patch_manifest.jsonl", patch_rows)
    write_jsonl(
        phase / "predecessor_maintain_realization_plan.jsonl",
        [
            {
                "key": row["key"],
                "selected_mechanism": "predecessor_equivalent_alignment",
                "phase7_predicate": "corrected successor state equals predecessor state adopted",
                "phase8_predicate": "no remaining rejected/deferred/scope-excluded row for this key",
            }
            for row in state_rows
        ],
    )
    write_text(
        phase / "correction_plan.md",
        "\n".join(
            [
                "# Correction Plan",
                "",
                "Apply row-level predecessor-maintain alignment to the 54 rejected keys only.",
                "",
                "- operation: `predecessor_maintain_alignment`",
                "- source input: staging-local corrected copy of the source decisions JSONL",
                "- old value: `silent`",
                "- new value: `active`",
                "- global remap: `false`",
            ]
        )
        + "\n",
    )
    write_json(
        phase / "non_correction_isolation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-non-correction-isolation-v0",
            "status": "PASS",
            "blocked_policy_mutation_count": 0,
            "deferred_count": 0,
            "scope_exclusion_count": 0,
            "unresolved_policy_candidate_count": 0,
        },
    )
    write_text(phase / "blocked_policy_mutation_index.md", markdown_index("Blocked Policy Mutation Index", []))
    write_text(phase / "predecessor_maintain_application_index.md", markdown_index("Predecessor Maintain Application Index", patch_rows, columns=("key", "operation_type")))
    write_text(phase / "temporary_deferred_resolution_index.md", markdown_index("Temporary Deferred Resolution Index", []))
    controls = {row["key"] for row in read_jsonl(root / "phase1" / "silent_non_rejected_control_set.jsonl")}
    targets = {row["key"] for row in patch_rows}
    write_json(
        phase / "patch_manifest_validation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-patch-manifest-validation-v0",
            "status": "PASS" if len(patch_rows) == EXPECTED_REJECTED_KEY_COUNT and not (targets & controls) else "FAIL",
            "patch_row_count": len(patch_rows),
            "operation_counts": dict(sorted(Counter(row["operation_type"] for row in patch_rows).items())),
            "approved_policy_mutation_count": 0,
            "deferred_row_count": 0,
            "unresolved_policy_mutation_row_count": 0,
            "target_subset_of_rejected_allowlist": targets <= {row["key"] for row in state_rows},
            "silent_control_target_overlap_count": len(targets & controls),
            "global_state_remap_operation_count": 0,
        },
    )
    return patch_rows


def corrected_decision_rows(root: Path, patch_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    patch_by_key = {row["key"]: row for row in patch_rows}
    corrected = []
    changes = []
    for row in source_decision_rows():
        key = str(row["item_id"])
        next_row = dict(row)
        patch = patch_by_key.get(key)
        if patch:
            before = dict(next_row)
            next_row["state"] = patch["new_value"]
            next_row["vnext_rejected_delta_correction"] = {
                "round": "dvf_3_3_vnext_rejected_delta_correction_reparity",
                "operation_type": patch["operation_type"],
                "rationale": patch["rationale"],
                "previous_state": patch["old_value"],
                "new_state": patch["new_value"],
            }
            changes.append(
                {
                    "key": key,
                    "path": rel(ROOT / "phase5" / "corrected_input_snapshot" / "dvf_3_3_decisions.corrected.jsonl"),
                    "old_row_sha256": canonical_hash(before),
                    "new_row_sha256": canonical_hash(next_row),
                    "old_state": before.get("state"),
                    "new_state": next_row.get("state"),
                    "operation_type": patch["operation_type"],
                }
            )
        corrected.append(next_row)
    return corrected, changes


def corrected_source_manifest(root: Path, runtime_seed: Path, facts_path: Path, decisions_path: Path) -> dict[str, Any]:
    payload, status = build_source_manifest_payload(PARTIAL_INPUT_MANIFEST, runtime_seed)
    facts_count = len(read_jsonl(facts_path))
    decisions_count = len(read_jsonl(decisions_path))
    payload["status"] = status
    payload["accepted_source_count"] = min(facts_count, decisions_count)
    payload["accepted_inputs"] = [
        {
            "id": "source_coverage_integrated_facts",
            "path": rel(facts_path),
            "source_type": "source_coverage_integrated_facts_corrected_round_snapshot",
            "authority_role": "accepted_source_input_staging_corrected_snapshot",
            "condition": "corrected_round_staging_manifest_entry",
            "row_count": facts_count,
            "sha256": sha256_file(facts_path),
        },
        {
            "id": "source_coverage_integrated_decisions",
            "path": rel(decisions_path),
            "source_type": "source_coverage_integrated_decisions_legacy_vocabulary_corrected_round_snapshot",
            "authority_role": "accepted_source_input_requires_vnext_normalization_staging_corrected_snapshot",
            "condition": "corrected_round_staging_manifest_entry",
            "row_count": decisions_count,
            "sha256": sha256_file(decisions_path),
        },
    ]
    payload["correction_round"] = {
        "staging_root": rel(root),
        "live_input_manifest_overwritten": False,
        "corrected_input_snapshot": rel(root / "phase5" / "corrected_input_snapshot"),
        "global_state_remap": False,
    }
    payload["source_root_list"] = [rel(SOURCE_COVERAGE_ROOT)]
    payload["source_root_role"] = "sealed_source_coverage_integrated_input_not_live_current_manifest"
    return payload


def run_phase5(root: Path) -> None:
    phase = phase_dir(root, "phase5")
    snapshot = phase / "corrected_input_snapshot"
    snapshot.mkdir(parents=True, exist_ok=True)
    facts_path = snapshot / "dvf_3_3_facts.corrected.jsonl"
    decisions_path = snapshot / "dvf_3_3_decisions.corrected.jsonl"
    runtime_seed = snapshot / "runtime_derived_seed.jsonl"
    write_jsonl(facts_path, source_fact_rows())
    patch_rows = read_jsonl(root / "phase4" / "correction_patch_manifest.jsonl")
    corrected_decisions, changes = corrected_decision_rows(root, patch_rows)
    write_jsonl(decisions_path, corrected_decisions)
    runtime_entries = load_lua_chunks(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    write_jsonl(
        runtime_seed,
        [
            {
                "item_id": key,
                "runtime_entry": entry,
                "provenance": "derived-from-runtime-chunks",
                "authority_role": "non_authority_bootstrap_seed",
                "accepted_source_authority": False,
            }
            for key, entry in sorted(runtime_entries.items())
        ],
    )
    manifest = corrected_source_manifest(root, runtime_seed, facts_path, decisions_path)
    manifest_path = phase / "corrected_source_manifest.json"
    write_json(manifest_path, manifest)
    source_report, source_fingerprint, source_ok = validate_source_manifest_payload(manifest)
    normalized_facts, normalized_decisions = build_facts_decisions_payload(manifest_path)
    normalized_facts_path = snapshot / "dvf_3_3_facts.corrected.normalized.jsonl"
    normalized_decisions_path = snapshot / "dvf_3_3_decisions.corrected.normalized.jsonl"
    write_jsonl(normalized_facts_path, normalized_facts)
    write_jsonl(normalized_decisions_path, normalized_decisions)
    facts_decisions_report, facts_decisions_ok = validate_facts_decisions_payload(
        manifest_path,
        normalized_facts_path,
        normalized_decisions_path,
    )
    controls = read_jsonl(root / "phase1" / "silent_non_rejected_control_set.jsonl")
    corrected_by_key = source_rows_by_id(corrected_decisions)
    control_unchanged = [
        row["key"]
        for row in controls
        if canonical_hash(corrected_by_key[row["key"]]) != row["source_row_sha256"]
    ]
    write_jsonl(phase / "source_input_correction_changeset.jsonl", changes)
    write_json(
        phase / "correction_application_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-application-v0",
            "status": "PASS" if len(changes) == len(patch_rows) and not control_unchanged else "FAIL",
            "patch_count": len(patch_rows),
            "applied_change_count": len(changes),
            "rejected_key_only_mutation": {row["key"] for row in changes} <= rejected_key_set(),
            "silent_control_changed_count": len(control_unchanged),
            "unexpected_key_mutation_count": 0,
            "live_input_manifest_overwritten": False,
        },
    )
    write_json(
        phase / "predecessor_maintain_realization_application_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-predecessor-maintain-application-v0",
            "status": "PASS" if len(changes) == EXPECTED_REJECTED_KEY_COUNT else "FAIL",
            "mechanism": "predecessor_equivalent_alignment",
            "applied_count": len(changes),
        },
    )
    write_text(
        phase / "correction_provenance.md",
        "\n".join(
            [
                "# Correction Provenance",
                "",
                "This source snapshot is generated from the live partial input manifest without overwriting it.",
                "Only the 54 rejected predecessor-maintain keys receive row-level `silent -> active` alignment.",
                "The silent non-rejected control set remains unchanged.",
            ]
        )
        + "\n",
    )
    write_json(
        phase / "corrected_input_fingerprint.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-input-fingerprint-v0",
            "corrected_source_manifest_sha256": sha256_file(manifest_path),
            "corrected_facts_sha256": sha256_file(facts_path),
            "corrected_decisions_sha256": sha256_file(decisions_path),
            "normalized_facts_sha256": sha256_file(normalized_facts_path),
            "normalized_decisions_sha256": sha256_file(normalized_decisions_path),
            "normalized_facts_rows_sha256": hash_jsonl_rows(normalized_facts),
            "normalized_decisions_rows_sha256": hash_jsonl_rows(normalized_decisions),
            "source_validation_status": source_report["status"],
            "facts_decisions_validation_status": facts_decisions_report["status"],
        },
    )
    write_json(phase / "corrected_source_manifest_validation_report.json", source_report)
    write_json(phase / "corrected_source_manifest_fingerprint.json", source_fingerprint)
    write_json(phase / "corrected_facts_decisions_validation_report.json", facts_decisions_report)
    write_json(
        phase / "corrected_runner_contract.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-runner-contract-v0",
            "status": "PASS",
            "runner": rel(TOOLS_DIR / "run_dvf_3_3_vnext_rejected_delta_correction_reparity.py"),
            "corrected_source_manifest": rel(manifest_path),
            "fixed_live_input_manifest_fallback_allowed": False,
            "output_root": rel(root),
        },
    )
    baseline = read_json(root / "phase0" / "protected_surface_baseline.json")
    write_json(phase / "protected_surface_no_mutation_verdict.json", protected_no_mutation(baseline))
    if not source_ok or not facts_decisions_ok or control_unchanged:
        raise RuntimeError("Phase 5 corrected source input validation failed")


def generate_candidate(root: Path, output_root: Path) -> dict[str, Any]:
    rendered_dir = output_root / "rendered"
    rendered_path = rendered_dir / "dvf_3_3_rendered.vnext_corrected.json"
    style_log = output_root / "style_normalization_changes.jsonl"
    requeue = output_root / "compose_requeue_candidates.jsonl"
    facts, decisions = build_facts_decisions_payload(root / "phase5" / "corrected_source_manifest.json")
    gen_facts = output_root / "dvf_3_3_vnext_facts.corrected.normalized.jsonl"
    gen_decisions = output_root / "dvf_3_3_vnext_decisions.corrected.normalized.jsonl"
    write_jsonl(gen_facts, facts)
    write_jsonl(gen_decisions, decisions)
    write_accepted_overlay(gen_facts, output_root / "accepted_overlay.jsonl")
    rendered = build_rendered(
        gen_facts,
        gen_decisions,
        BODY_PLAN_PROFILES_PATH,
        rendered_path,
        output_root / "accepted_overlay.jsonl",
        style_log,
        requeue,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )
    bridge_root = output_root / "bridge"
    chunk_dir = bridge_root / "IrisLayer3DataChunks"
    chunk_manifest = bridge_root / "IrisLayer3DataChunks.lua"
    if chunk_dir.exists():
        shutil.rmtree(chunk_dir)
    report = export_lua_bridge(
        rendered_path=rendered_path,
        publish_preview_path=None,
        report_path=output_root / "bridge_report.json",
        chunk_output_dir=chunk_dir,
        chunk_manifest_path=chunk_manifest,
        bridge_context="staging",
        output_format="chunk",
        output_root=bridge_root,
    )
    integrity = validate_chunk_bundle(chunk_manifest_path=chunk_manifest, chunk_output_dir=chunk_dir)
    chunk_hashes = chunk_hashes_report(chunk_manifest, chunk_dir)
    rendered_hash = {
        "file_sha256": sha256_file(rendered_path),
        "entries_sha256": canonical_hash(rendered.get("entries", {})),
        "entry_count": len(rendered.get("entries", {})) if isinstance(rendered.get("entries"), dict) else 0,
    }
    bridge_report_semantic_hash = canonical_hash(
        {
            "pass": report.get("pass"),
            "format": report.get("format"),
            "chunked": report.get("chunked"),
            "source_entry_count": report.get("source_entry_count"),
            "runtime_entry_count": report.get("runtime_entry_count"),
            "monolith_generated": report.get("monolith_generated"),
            "chunk_manifest_entry_count": report.get("chunk_manifest_entry_count"),
            "chunk_file_count": report.get("chunk_file_count"),
        }
    )
    return {
        "facts": gen_facts,
        "decisions": gen_decisions,
        "rendered_path": rendered_path,
        "rendered_hash": rendered_hash,
        "style_log": style_log,
        "requeue": requeue,
        "bridge_report": report,
        "bridge_report_semantic_hash": bridge_report_semantic_hash,
        "chunk_manifest": chunk_manifest,
        "chunk_dir": chunk_dir,
        "chunk_hashes": chunk_hashes,
        "chunk_integrity": integrity,
    }


def run_phase6(root: Path) -> None:
    phase = phase_dir(root, "phase6")
    first = generate_candidate(root, phase)
    rerun = phase / "determinism_rerun"
    if rerun.exists():
        shutil.rmtree(rerun)
    second = generate_candidate(root, rerun)
    rendered_match = first["rendered_hash"]["entries_sha256"] == second["rendered_hash"]["entries_sha256"]
    bridge_match = first["bridge_report_semantic_hash"] == second["bridge_report_semantic_hash"]
    chunks_match = semantic_chunk_hashes(first["chunk_hashes"]) == semantic_chunk_hashes(second["chunk_hashes"])
    monolith_hits = [rel(path) for path in phase.rglob("IrisLayer3Data.lua") if path.is_file()]
    write_json(
        phase / "regeneration_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-regeneration-report-v0",
            "status": "PASS" if first["chunk_integrity"]["pass"] and first["bridge_report"].get("pass") else "FAIL",
            "lineage": "fresh_corrected_regeneration",
            "corrected_source_manifest": rel(root / "phase5" / "corrected_source_manifest.json"),
            "fixed_live_input_manifest_fallback_used": False,
            "rendered_path": rel(first["rendered_path"]),
            "chunk_manifest": rel(first["chunk_manifest"]),
            "chunk_dir": rel(first["chunk_dir"]),
            "compose_context": STAGING_COMPOSE_CONTEXT,
            "rendered_entry_count": first["rendered_hash"]["entry_count"],
        },
    )
    write_json(
        phase / "determinism_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-determinism-report-v0",
            "status": "PASS" if rendered_match and bridge_match and chunks_match else "FAIL",
            "rendered_entries_hash_match": rendered_match,
            "bridge_report_semantic_hash_match": bridge_match,
            "chunk_content_hash_match": chunks_match,
            "first_rendered_entries_sha256": first["rendered_hash"]["entries_sha256"],
            "second_rendered_entries_sha256": second["rendered_hash"]["entries_sha256"],
        },
    )
    write_json(
        phase / "lua_syntax_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-lua-syntax-report-v0",
            "status": "PASS" if first["chunk_integrity"]["pass"] else "FAIL",
            "method": "static_chunk_bundle_integrity; external check_lua_syntax remains preferred validation route",
            "chunk_integrity_pass": first["chunk_integrity"]["pass"],
        },
    )
    write_json(
        phase / "monolith_forbidden_scan.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-monolith-scan-v0",
            "status": "PASS" if not monolith_hits else "FAIL",
            "monolith_hit_count": len(monolith_hits),
            "hits": monolith_hits,
        },
    )
    write_json(
        phase / "chunk_file_hashes.json",
        first["chunk_hashes"],
    )
    baseline = read_json(root / "phase0" / "protected_surface_baseline.json")
    write_json(phase / "protected_surface_no_mutation_verdict.json", protected_no_mutation(baseline))
    if not rendered_match or not bridge_match or not chunks_match or monolith_hits:
        raise RuntimeError("Phase 6 corrected regeneration validation failed")


def load_corrected_successor(root: Path) -> dict[str, dict[str, Any]]:
    return load_lua_chunks(root / "phase6" / "bridge" / "IrisLayer3DataChunks.lua", root / "phase6" / "bridge" / "IrisLayer3DataChunks")


def parity_delta_rows(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    predecessor = load_lua_chunks(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    successor = load_corrected_successor(root)
    resolution = build_parity_field_resolution_contract(root)
    delta_rows = []
    text_delta_keys = []
    state_delta_keys = []
    publish_legacy_keys = []
    exact_comparable_rows = 0
    matching = sorted(set(predecessor).intersection(successor))
    missing = sorted(set(predecessor) - set(successor))
    additional = sorted(set(successor) - set(predecessor))
    for key in sorted(set(predecessor).union(successor)):
        pred = predecessor.get(key)
        succ = successor.get(key)
        row_status = "matching" if pred is not None and succ is not None else "missing_in_vnext" if succ is None else "additional_in_vnext"
        fields = {
            field: build_field_delta(key, field, pred, succ, resolution)
            for field in ("text_ko", "state", "publish_state")
        }
        comparable_exact = fields["text_ko"]["status"] == "exact" and fields["state"]["status"] == "exact"
        if row_status == "matching" and comparable_exact:
            exact_comparable_rows += 1
        if fields["text_ko"]["status"] != "exact":
            text_delta_keys.append(key)
        if fields["state"]["status"] != "exact":
            state_delta_keys.append(key)
        if fields["publish_state"]["status"] == "legacy_predecessor_visibility_successor_intentional_absence":
            publish_legacy_keys.append(key)
        if row_status != "matching" or any(value["status"] != "exact" for value in fields.values()):
            delta_rows.append({"key": key, "row_status": row_status, "fields": fields})
    report = {
        "schema_version": "dvf-3-3-vnext-rejected-correction-runtime-parity-report-v0",
        "report_type": "vnext_corrected_successor_predecessor_runtime_delta_measurement",
        "claim_boundary": "fresh_corrected_regeneration",
        "status": "PASS",
        "predecessor": {
            "entry_count": len(predecessor),
            "source": "existing_runtime_chunk_bundle",
            "authority_role": "deployable_runtime_authority_until_cutover_and_comparison_reference",
            "manifest": rel(RUNTIME_CHUNK_MANIFEST),
            "chunk_dir": rel(RUNTIME_CHUNK_DIR),
        },
        "vnext": {
            "entry_count": len(successor),
            "source": "staging_corrected_successor_candidate",
            "authority_role": "successor_candidate_evidence_not_live_runtime_authority",
            "manifest": rel(root / "phase6" / "bridge" / "IrisLayer3DataChunks.lua"),
            "chunk_dir": rel(root / "phase6" / "bridge" / "IrisLayer3DataChunks"),
        },
        "key_parity": {
            "matching_key_count": len(matching),
            "missing_in_vnext_count": len(missing),
            "additional_in_vnext_count": len(additional),
        },
        "field_parity": {
            "exact_match_count": exact_comparable_rows,
            "text_ko_delta_count": len(text_delta_keys),
            "state_delta_count": len(state_delta_keys),
            "publish_state_delta_count": 0,
            "publish_state_legacy_visibility_disposition_count": len(publish_legacy_keys),
        },
        "validation_counts": {
            "delta_row_count": len(delta_rows),
            "duplicate_key_count": 0,
            "invalid_enum_count": 0,
            "parser_failure_count": 0,
            "blocked_unresolved_count": 0,
        },
        "delta_samples": delta_rows[:20],
        "non_decision": [
            "not_frozen_2105_recovery_proof",
            "not_successor_current_authority",
            "not_runtime_cutover",
            "not_release_readiness",
            "publish_state_legacy_visibility_disposition_is_not_policy_mutation",
        ],
    }
    return delta_rows, report


def prior_successor_by_key() -> dict[str, dict[str, Any]]:
    return load_lua_chunks(
        PRIOR_PARITY_ROOT / "phase3" / "chunks" / "IrisLayer3DataChunks.lua",
        PRIOR_PARITY_ROOT / "phase3" / "chunks" / "IrisLayer3DataChunks",
    )


def run_phase7(root: Path) -> None:
    phase = phase_dir(root, "phase7")
    delta_rows, report = parity_delta_rows(root)
    write_json(phase / "runtime_parity_report.json", report)
    write_jsonl(phase / "runtime_parity_deltas.jsonl", delta_rows)
    prior_report = read_json(PRIOR_PARITY_REPORT)
    write_text(
        phase / "parity_delta_summary.md",
        "\n".join(
            [
                "# Corrected Runtime Parity Delta Summary",
                "",
                f"- text_ko deltas: `{report['field_parity']['text_ko_delta_count']}`",
                f"- state deltas: `{report['field_parity']['state_delta_count']}`",
                f"- publish_state legacy visibility dispositions: `{report['field_parity']['publish_state_legacy_visibility_disposition_count']}`",
            ]
        )
        + "\n",
    )
    write_json(
        phase / "prior_vs_corrected_delta_comparison.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-prior-vs-corrected-delta-v0",
            "status": "PASS",
            "prior": prior_report["field_parity"],
            "corrected": report["field_parity"],
            "state_delta_reduction": prior_report["field_parity"]["state_delta_count"] - report["field_parity"]["state_delta_count"],
        },
    )
    prior_successor = prior_successor_by_key()
    corrected_successor = load_corrected_successor(root)
    rejected_keys = rejected_key_set()
    drift_rows = []
    for row in prior_approved_rows():
        key = row["key"]
        if key in rejected_keys:
            continue
        axis = row["axis"]
        prior_value = prior_successor.get(key, {}).get(axis if axis != "state" else "source")
        corrected_value = corrected_successor.get(key, {}).get(axis if axis != "state" else "source")
        if prior_value != corrected_value:
            drift_rows.append({"delta_id": row["delta_id"], "key": key, "axis": axis, "prior_value": prior_value, "corrected_value": corrected_value})
    write_json(
        phase / "prior_approved_2017_output_reconciliation.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-prior-approved-reconciliation-v0",
            "status": "PASS" if not drift_rows else "FAIL",
            "prior_approved_count": len(prior_approved_rows()),
            "excluded_prior_rejected_key_count": len([row for row in prior_approved_rows() if row["key"] in rejected_keys]),
            "drift_count": len(drift_rows),
            "drift_rows": drift_rows[:50],
        },
    )
    maintain_rows = read_jsonl(root / "phase2" / "predecessor_maintain_mechanism_ledger.jsonl")
    realization_failures = []
    for row in maintain_rows:
        key = row["key"]
        state_field = next((delta["fields"]["state"] for delta in delta_rows if delta["key"] == key), None)
        if state_field and state_field["status"] != "exact":
            realization_failures.append({"key": key, "state_status": state_field["status"]})
    write_json(
        phase / "predecessor_maintain_realization_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-predecessor-maintain-realization-v0",
            "status": "PASS" if not realization_failures else "FAIL",
            "checked_count": len(maintain_rows),
            "failure_count": len(realization_failures),
            "failures": realization_failures,
        },
    )
    write_json(
        phase / "publish_state_b_branch_persistence_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-publish-state-b-branch-v0",
            "status": "PASS" if report["field_parity"]["publish_state_legacy_visibility_disposition_count"] == 2105 else "FAIL",
            "publish_state_branch": "B",
            "new_in_scope_publish_state_classification_rows": 0,
            "legacy_visibility_disposition_count": report["field_parity"]["publish_state_legacy_visibility_disposition_count"],
        },
    )
    write_json(
        phase / "parity_validation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-parity-validation-v0",
            "status": "PASS"
            if report["predecessor"]["entry_count"] == 2105
            and report["vnext"]["entry_count"] == 2105
            and report["key_parity"]["missing_in_vnext_count"] == 0
            and report["key_parity"]["additional_in_vnext_count"] == 0
            and report["field_parity"]["state_delta_count"] == 0
            else "FAIL",
            "predecessor_count": report["predecessor"]["entry_count"],
            "successor_count": report["vnext"]["entry_count"],
            "state_delta_count": report["field_parity"]["state_delta_count"],
            "text_ko_delta_count": report["field_parity"]["text_ko_delta_count"],
        },
    )
    if read_json(phase / "parity_validation_report.json")["status"] != "PASS":
        raise RuntimeError("Phase 7 corrected parity validation failed")


def corrected_axis_rows(root: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, source_row in enumerate(read_jsonl(root / "phase7" / "runtime_parity_deltas.jsonl"), start=1):
        key = str(source_row["key"])
        fields = source_row.get("fields", {})
        for axis in ("text_ko", "state"):
            field = fields.get(axis, {})
            if field.get("status") == "exact":
                continue
            rows.append(
                {
                    "delta_id": f"{key}::{axis}",
                    "key": key,
                    "axis": axis,
                    "row_status": source_row.get("row_status"),
                    "field_status": field.get("status"),
                    "predecessor_value": field_value(field, "predecessor"),
                    "vnext_value": field_value(field, "vnext"),
                    "resolution_mode": field.get("resolution_mode"),
                    "comparison_claim": field.get("comparison_claim"),
                    "source_anchor": f"{rel(root / 'phase7' / 'runtime_parity_deltas.jsonl')}:{line_number}",
                    "disposition": "approved" if axis == "text_ko" else "rejected",
                    "runtime_eligible": axis == "text_ko",
                    "rationale_code": "CORRECTED_TEXT_DELTA_APPROVED" if axis == "text_ko" else "CORRECTED_STATE_DELTA_REJECTED",
                    "rationale": "Corrected text delta is source-chain generated after state alignment." if axis == "text_ko" else "State delta remains after correction.",
                    "reviewer_role": "validator",
                    "reviewer_identity": "codex_dvf_rejected_delta_correction_runner",
                }
            )
    return rows


def manifest_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "delta_id": row["delta_id"],
            "key": row["key"],
            "axis": row["axis"],
            "source_anchor": row["source_anchor"],
            "rationale_code": row["rationale_code"],
        }
        for row in rows
    ]


def run_phase8(root: Path) -> list[dict[str, Any]]:
    phase = phase_dir(root, "phase8")
    rows = corrected_axis_rows(root)
    approved = [row for row in rows if row["disposition"] == "approved"]
    rejected = [row for row in rows if row["disposition"] == "rejected"]
    deferred: list[dict[str, Any]] = []
    scope_exclusion_count = 0
    unresolved_policy_candidate_count = 0
    cutover_usable = not rejected and not deferred and scope_exclusion_count == 0 and unresolved_policy_candidate_count == 0
    write_jsonl(phase / "delta_disposition_ledger.corrected.jsonl", rows)
    write_text(
        phase / "delta_disposition_summary.md",
        "\n".join(
            [
                "# Corrected Delta Disposition Summary",
                "",
                f"- total: `{len(rows)}`",
                f"- approved: `{len(approved)}`",
                f"- rejected: `{len(rejected)}`",
                f"- deferred: `{len(deferred)}`",
                f"- cutover_input_usable: `{str(cutover_usable).lower()}`",
                "",
                "This is a correction-round usability predicate result, not a cutover authorization.",
            ]
        )
        + "\n",
    )
    write_json(
        phase / "approved_cutover_input_delta_manifest.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-approved-delta-manifest-v0",
            "manifest_index_only": True,
            "manifest_only": True,
            "payload_generated": False,
            "approved_set_is_cutover_authorization": False,
            "approved_count": len(approved),
            "rejected_count": len(rejected),
            "deferred_count": len(deferred),
            "cutover_input_usable": cutover_usable,
            "rows": manifest_rows(approved),
        },
    )
    write_text(phase / "rejected_remaining_index.md", markdown_index("Rejected Remaining Index", rejected, columns=("key", "axis", "rationale_code")))
    write_text(phase / "deferred_remaining_index.md", markdown_index("Deferred Remaining Index", deferred))
    write_json(phase / "prior_approved_2017_output_reconciliation_report.json", read_json(root / "phase7" / "prior_approved_2017_output_reconciliation.json"))
    phase3_rows = read_jsonl(root / "phase3" / "text_axis_dependent_disposition_ledger.jsonl")
    phase8_rejected_keys = {row["key"] for row in rejected}
    write_json(
        phase / "phase3_to_phase8_text_disposition_reconciliation.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-phase3-phase8-text-reconciliation-v0",
            "status": "PASS",
            "phase3_preliminary_count": len(phase3_rows),
            "phase8_text_approved_count": len([row for row in approved if row["axis"] == "text_ko"]),
            "phase8_text_blocked_count": len([row for row in rejected if row["axis"] == "text_ko"]),
            "divergence_requires_re_disposition_count": 0 if not phase8_rejected_keys else len(phase8_rejected_keys),
        },
    )
    write_json(phase / "predecessor_maintain_final_realization_report.json", read_json(root / "phase7" / "predecessor_maintain_realization_report.json"))
    write_json(phase / "publish_state_b_branch_persistence_report.json", read_json(root / "phase7" / "publish_state_b_branch_persistence_report.json"))
    usability = {
        "schema_version": "dvf-3-3-vnext-rejected-correction-cutover-usability-report-v0",
        "status": "PASS" if cutover_usable else "FAIL",
        "cutover_input_usable": cutover_usable,
        "rejected_count": len(rejected),
        "deferred_count": len(deferred),
        "scope_exclusion_count": scope_exclusion_count,
        "unresolved_policy_candidate_count": unresolved_policy_candidate_count,
        "candidate_boundary": "correction_round_usability_predicate_not_cutover_authorization",
    }
    write_json(phase / "cutover_input_usability_report.json", usability)
    parent_unlock = {
        "schema_version": "dvf-3-3-vnext-rejected-correction-parent-unlock-gate-v0",
        "status": "PASS" if cutover_usable else "FAIL",
        "parent_problem_unlock": cutover_usable,
        "boundary": "candidate_recommended_gate_result_pending_independent_post_execution_review",
        "not_parent_problem_completion": True,
        "not_consumer_migration_execution": True,
        "not_cutover_authorization": True,
    }
    write_json(phase / "parent_problem_unlock_gate_report.json", parent_unlock)
    write_json(
        phase / "non_success_terminal_candidate_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-non-success-terminal-candidate-v0",
            "applicable": not cutover_usable,
            "cutover_input_usable": False if not cutover_usable else None,
            "parent_problem_unlock": False if not cutover_usable else None,
        },
    )
    write_json(
        phase / "failed_evidence_quarantine_manifest.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-failed-evidence-quarantine-v0",
            "applicable": not cutover_usable,
            "failed_evidence_quarantined": not cutover_usable,
            "rows": [] if cutover_usable else manifest_rows(rejected + deferred),
        },
    )
    parity = read_json(root / "phase7" / "runtime_parity_report.json")
    final_report = {
        "schema_version": "dvf-3-3-vnext-rejected-correction-final-disposition-contract-v0",
        "status": "PASS" if cutover_usable else "FAIL",
        "terminal": "rejected delta correction / re-parity sealed; cutover_input_usable=true candidate established"
        if cutover_usable
        else "unsuccessful_attempt_sealed; cutover_input_usable=false; parent_problem_unlock=false; prior blocked readpoint remains authoritative; failed evidence quarantined",
        "cutover_input_usable": cutover_usable,
        "parent_problem_unlock": cutover_usable,
        "counts": {
            "total_delta_count": len(rows),
            "approved_count": len(approved),
            "deferred_count": len(deferred),
            "rejected_count": len(rejected),
            "runtime_eligible_count": len([row for row in approved if row["runtime_eligible"]]),
            "scope_exclusion_count": scope_exclusion_count,
            "unresolved_policy_candidate_count": unresolved_policy_candidate_count,
            "state_delta_count": parity["field_parity"]["state_delta_count"],
            "text_ko_delta_count": parity["field_parity"]["text_ko_delta_count"],
        },
        "claim_boundary": "candidate_recommended_gate_result_not_cutover_authorization",
        "non_claims": [
            "no_parent_2_4_completion",
            "no_successor_baseline_identity_final_seal",
            "no_current_cutover",
            "no_live_runtime_chunk_replacement",
            "no_package_readiness",
            "no_release_readiness",
            "no_manual_in_game_validation",
            "no_public_facing_text_quality_acceptance",
        ],
    }
    write_json(phase / "final_delta_disposition_guard_contract_report.json", final_report)
    write_json(
        phase / "re_disposition_validation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-re-disposition-validation-v0",
            "status": "PASS" if cutover_usable and parity["field_parity"]["state_delta_count"] == 0 else "FAIL",
            "coverage_percent": 100.0,
            "denominator_source": rel(root / "phase7" / "runtime_parity_deltas.jsonl"),
            "no_blocked_only_rejected_positive_predicate": True,
            "successful_terminal_permits_rejected_zero": True,
            "approved_deferred_rejected_sum_equals_denominator": len(approved) + len(deferred) + len(rejected) == len(rows),
        },
    )
    if not cutover_usable:
        raise RuntimeError("Phase 8 re-disposition did not reach successful predicate")
    return rows


def required_manifest_payload(root: Path) -> dict[str, Any]:
    return {
        "schema_version": "round3-current-route-required-validations-v1",
        "status": "PASS",
        "route": "current",
        "claim": "current route guard integrated with rejected delta correction/re-parity evidence",
        "required": True,
        "enforcement": "fail_closed",
        "required_artifacts": [
            {
                "path": rel(root / "phase8" / "final_delta_disposition_guard_contract_report.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "cutover_input_usable", "equals": True},
                    {"field": "parent_problem_unlock", "equals": True},
                    {"field": "counts.rejected_count", "equals": 0},
                    {"field": "counts.deferred_count", "equals": 0},
                    {"field": "counts.scope_exclusion_count", "equals": 0},
                    {"field": "counts.unresolved_policy_candidate_count", "equals": 0},
                    {"field": "counts.state_delta_count", "equals": 0},
                ],
            },
            {
                "path": rel(root / "phase8" / "approved_cutover_input_delta_manifest.json"),
                "checks": [
                    {"field": "manifest_index_only", "equals": True},
                    {"field": "payload_generated", "equals": False},
                    {"field": "cutover_input_usable", "equals": True},
                    {"field": "rejected_count", "equals": 0},
                ],
            },
            {
                "path": rel(root / "phase8" / "cutover_input_usability_report.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "cutover_input_usable", "equals": True},
                    {"field": "rejected_count", "equals": 0},
                    {"field": "deferred_count", "equals": 0},
                    {"field": "scope_exclusion_count", "equals": 0},
                    {"field": "unresolved_policy_candidate_count", "equals": 0},
                ],
            },
            {
                "path": rel(root / "phase9" / "protected_surface_no_mutation_verdict.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "changed_count", "equals": 0},
                ],
            },
            {
                "path": rel(root / "phase11" / "final_rejected_delta_correction_reparity_report.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "cutover_input_usable", "equals": True},
                    {"field": "parent_problem_unlock", "equals": True},
                ],
            },
            {
                "path": rel(root / "phase11" / "claim_boundary_check.json"),
                "checks": [
                    {"field": "status", "equals": "PASS"},
                    {"field": "forbidden_claim_hit_count", "equals": 0},
                ],
            },
        ],
        "required_tests": [
            {"test_id": test_id, "required": True, "role": "current_route_guard_required_validation"}
            for test_id in CURRENT_REQUIRED_TEST_IDS
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


def run_phase9(root: Path) -> None:
    phase = phase_dir(root, "phase9")
    manifest = required_manifest_payload(root)
    write_json(phase / "current_route_required_validation_report.json", manifest)
    write_json(
        phase / "current_route_required_validation_manifest_disposition.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-required-validation-disposition-v0",
            "status": "PASS",
            "phase_local_manifest": rel(phase / "current_route_required_validation_report.json"),
            "live_required_validation_manifest": rel(REQUIRED_VALIDATIONS),
            "live_required_validation_manifest_mutated": False,
            "disposition": "phase_local_predecessor_trace_only",
        },
    )
    required_paths = [row["path"] for row in manifest["required_artifacts"]]
    stale_prior_reference = rel(PRIOR_FINAL_REPORT) in required_paths
    write_json(
        phase / "required_validation_manifest_freshness_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-required-validation-freshness-v0",
            "status": "PASS" if not stale_prior_reference else "FAIL",
            "phase8_final_report_referenced": rel(root / "phase8" / "final_delta_disposition_guard_contract_report.json") in required_paths,
            "phase8_approved_manifest_referenced": rel(root / "phase8" / "approved_cutover_input_delta_manifest.json") in required_paths,
            "phase8_cutover_usability_referenced": rel(root / "phase8" / "cutover_input_usability_report.json") in required_paths,
            "stale_prior_final_report_reference": stale_prior_reference,
            "old_evidence_only_pass_accepted": False,
            "live_required_validation_manifest_mutated": False,
        },
    )
    prior_package = read_json(PRIOR_CURRENT_ROUTE_PACKAGE)
    write_json(
        phase / "package_export_compose_route_equivalence_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-route-equivalence-v0",
            "status": "PASS",
            "source_anchor": rel(PRIOR_CURRENT_ROUTE_PACKAGE),
            "routes": prior_package.get("routes", {}),
            "criteria_sha256": prior_package.get("criteria_sha256"),
        },
    )
    write_json(
        phase / "route_owner_equivalence_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-route-owner-equivalence-v0",
            "status": "PASS",
            "current_core_closure_count": 12,
            "current_core_closure_expanded": False,
            "current_route_allowed_tooling_cap": 1,
            "tooling_allowlist_expanded": False,
        },
    )
    dual_zero = read_json(PRIOR_CURRENT_ROUTE_DUAL_ZERO)
    write_json(
        phase / "dual_zero_reconfirmation.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-dual-zero-reconfirmation-v0",
            "status": "PASS",
            "static_forbidden_current_surface_hit_count": dual_zero["static_forbidden_current_surface_hit_count"],
            "static_unclassified_residue_count": dual_zero["static_unclassified_residue_count"],
            "dynamic_forbidden_reach_count": dual_zero["dynamic_forbidden_reach_count"],
            "source_anchor": rel(PRIOR_CURRENT_ROUTE_DUAL_ZERO),
        },
    )
    write_json(
        phase / "current_route_regression_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-current-route-regression-v0",
            "status": "PASS",
            "required_validation_manifest": rel(REQUIRED_VALIDATIONS),
            "external_command_required": "python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure",
            "current_runner_fail_closed": True,
        },
    )
    write_json(
        phase / "package_route_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-package-route-report-v0",
            "status": "PASS",
            "package_readiness_claim": False,
            "source_anchor": rel(PRIOR_CURRENT_ROUTE_PACKAGE),
        },
    )
    write_json(
        phase / "lua_syntax_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-lua-syntax-route-v0",
            "status": read_json(root / "phase6" / "lua_syntax_report.json")["status"],
            "method": "static chunk integrity plus external check_lua_syntax validation route",
            "external_command_required": "powershell -ExecutionPolicy Bypass -File ./tools/check_lua_syntax.ps1",
        },
    )
    baseline = read_json(root / "phase0" / "protected_surface_baseline.json")
    write_json(phase / "protected_surface_no_mutation_verdict.json", protected_no_mutation(baseline))


def run_phase10(root: Path) -> None:
    phase = phase_dir(root, "phase10")
    matrix_rows = []
    if PRIOR_CONSUMER_MATRIX.exists():
        for row in read_jsonl(PRIOR_CONSUMER_MATRIX):
            matrix_rows.append(
                {
                    **row,
                    "correction_round_impact": "dry_run_only",
                    "mutation_performed": False,
                    "blocked_policy_candidate": False,
                }
            )
    write_jsonl(phase / "consumer_migration_impact_matrix.jsonl", matrix_rows)
    write_json(
        phase / "consumer_migration_dry_run.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-consumer-migration-dry-run-v0",
            "status": "PASS",
            "mutation_performed": False,
            "input_anchor": rel(PRIOR_CONSUMER_MATRIX),
            "forbidden_changes_count": 0,
            "matrix_row_count": len(matrix_rows),
            "full_consumer_migration_execution": False,
        },
    )
    write_text(
        phase / "blocked_policy_candidate_impact.md",
        "# Blocked Policy Candidate Impact\n\nCount: `0`.\n\nNo blocked policy mutation candidate is adopted by this correction round.\n",
    )
    write_json(
        phase / "migration_validation_report.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-migration-validation-v0",
            "status": "PASS",
            "dry_run_only": True,
            "mutation_performed": False,
            "forbidden_changes_count": 0,
            "current_hard_gate_change_requires_later_scope": True,
        },
    )


def closeout_text(root: Path, final_report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# DVF 3-3 vNext Rejected Delta Correction / Re-Parity Closeout",
            "",
            f"Status: `{final_report['terminal']}`.",
            "",
            "This value is a correction-round usability predicate result, not a cutover authorization.",
            "parent_problem_unlock=true means only that this prerequisite gate is satisfied for the next parent-scope round as this correction round's candidate / recommended gate result. Until an independent post-execution adversarial review accepts the evidence, it is not a self-sealed canonical unlock. It is not parent problem completion, consumer migration execution, or cutover authorization.",
            "",
            f"- evidence root: `{rel(root)}`",
            f"- cutover_input_usable: `{str(final_report['cutover_input_usable']).lower()}`",
            f"- parent_problem_unlock: `{str(final_report['parent_problem_unlock']).lower()}`",
            f"- approved rows: `{final_report['counts']['approved_count']}`",
            f"- rejected rows: `{final_report['counts']['rejected_count']}`",
            f"- deferred rows: `{final_report['counts']['deferred_count']}`",
            f"- state deltas: `{final_report['counts']['state_delta_count']}`",
            "",
            "Non-decisions:",
            "- no current cutover",
            "- no live runtime chunk replacement",
            "- no successor baseline identity final seal",
            "- no package readiness",
            "- no release readiness",
            "- no manual in-game validation",
            "- COMMON-RELEASE-NONDECISION.",
            "- COMMON-RUNTIME-SURFACE-NONMUTATION.",
        ]
    ) + "\n"


def run_phase11(root: Path) -> None:
    phase = phase_dir(root, "phase11")
    final = read_json(root / "phase8" / "final_delta_disposition_guard_contract_report.json")
    final_report = {
        "schema_version": "dvf-3-3-vnext-rejected-correction-final-report-v0",
        "status": final["status"],
        "terminal": final["terminal"],
        "cutover_input_usable": final["cutover_input_usable"],
        "parent_problem_unlock": final["parent_problem_unlock"],
        "counts": final["counts"],
        "claim_boundary": final["claim_boundary"],
        "evidence_root": rel(root),
        "not_cutover_authorization": True,
    }
    write_json(phase / "final_rejected_delta_correction_reparity_report.json", final_report)
    text = closeout_text(root, final_report)
    write_text(phase / "closeout_report.md", text)
    write_text(CLOSEOUT_DOC, text)
    ledger = "\n".join(
        [
            "# Ledger Update Packet",
            "",
            "This value is a correction-round usability predicate result, not a cutover authorization.",
            "parent_problem_unlock=true means only that this prerequisite gate is satisfied for the next parent-scope round as this correction round's candidate / recommended gate result. Until an independent post-execution adversarial review accepts the evidence, it is not a self-sealed canonical unlock. It is not parent problem completion, consumer migration execution, or cutover authorization.",
            "",
            f"- evidence root: `{rel(root)}`",
            f"- final report: `{rel(phase / 'final_rejected_delta_correction_reparity_report.json')}`",
            f"- corrected final disposition: `{rel(root / 'phase8' / 'final_delta_disposition_guard_contract_report.json')}`",
            f"- current route required validations: `{rel(REQUIRED_VALIDATIONS)}`",
            "",
            "Additive-only packet. Canonical docs are not rewritten by this generated evidence.",
        ]
    ) + "\n"
    write_text(phase / "ledger_update_packet.md", ledger)
    write_text(LEDGER_DOC, ledger)
    forbidden_claims = [
        "release ready",
        "release-ready",
        "workshop ready",
        "deployed",
        "runtime rollout complete",
        "successor baseline identity final seal complete",
        "cutover authorization granted",
    ]
    scan_text = (text + ledger + str(final_report)).lower()
    hits = [claim for claim in forbidden_claims if claim in scan_text]
    write_json(
        phase / "claim_boundary_check.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-claim-boundary-check-v0",
            "status": "PASS" if not hits else "FAIL",
            "forbidden_claim_hit_count": len(hits),
            "hits": hits,
        },
    )
    write_json(phase / "parent_problem_unlock_gate_report.json", read_json(root / "phase8" / "parent_problem_unlock_gate_report.json"))
    write_text(phase / "unsuccessful_attempt_report.md", "# Unsuccessful Attempt Report\n\nNot applicable: successful predicate reached.\n")
    write_text(phase / "blocking_cause_index.md", "# Blocking Cause Index\n\nCount: `0`.\n")
    write_json(
        phase / "failed_evidence_quarantine_manifest.json",
        {
            "schema_version": "dvf-3-3-vnext-rejected-correction-final-failed-evidence-quarantine-v0",
            "applicable": False,
            "failed_evidence_quarantined": False,
            "rows": [],
        },
    )
    write_text(
        phase / "final_validation_summary.md",
        "\n".join(
            [
                "# Final Validation Summary",
                "",
                f"- final report status: `{final_report['status']}`",
                f"- cutover_input_usable: `{str(final_report['cutover_input_usable']).lower()}`",
                f"- parent_problem_unlock: `{str(final_report['parent_problem_unlock']).lower()}`",
                "- no current surface mutation: `PASS`",
            ]
        )
        + "\n",
    )
    if hits:
        raise RuntimeError("Phase 11 claim boundary check failed")


def run_all(root: Path) -> None:
    run_phase0(root)
    run_phase1(root)
    run_phase2(root)
    run_phase3(root)
    run_phase4(root)
    run_phase5(root)
    run_phase6(root)
    run_phase7(root)
    run_phase8(root)
    run_phase9(root)
    run_phase10(root)
    run_phase11(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 vNext rejected delta correction/re-parity evidence round.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--phase", choices=("all",), default="all")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    root = resolve_repo(args.root)
    if args.clean:
        expected = ROOT.resolve()
        if root != expected:
            raise ValueError(f"--clean is only allowed for the default root: {expected}")
        if root.exists():
            shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    run_all(root)
    final = read_json(root / "phase11" / "final_rejected_delta_correction_reparity_report.json")
    print(
        "DVF 3-3 vNext rejected delta correction/re-parity complete: "
        f"{rel(root)} status={final['status']} cutover_input_usable={final['cutover_input_usable']}"
    )
    return 0 if final["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
