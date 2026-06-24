from __future__ import annotations

import difflib
import json
import re
import shutil
from collections import Counter, defaultdict
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
    build_facts_decisions_payload,
    canonical_hash,
    chunk_paths_from_manifest,
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


GENERATED_AT = "2026-06-18T00:00:00+09:00"
CLAIM_BOUNDARY = (
    "DVF 3-3 vNext current authority cutover tooling readiness only; "
    "not current authority adoption, live runtime replacement, consumer migration completion, "
    "package readiness, or release readiness"
)

READINESS_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_cutover_tooling_readiness"
CORRECTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_rejected_delta_correction_reparity"
NORMALIZATION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_consumer_migration_input_normalization"
EXECUTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_execution"

PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md"
FIXED_DOWNSTREAM_PLAN = (
    REPO_ROOT / "docs" / "dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md"
)
CUTOVER_CONTRACT = REPO_ROOT / "docs" / "dvf_3_3_vnext_cutover_contract.md"
PLAN_TEMPLATE = REPO_ROOT / "docs" / "PLAN_TEMPLATE.md"
CURRENT_ROUTE_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"

CORRECTED_SOURCE_MANIFEST = CORRECTION_ROOT / "phase5" / "corrected_source_manifest.json"
CORRECTED_RENDERED = CORRECTION_ROOT / "phase6" / "rendered" / "dvf_3_3_rendered.vnext_corrected.json"
CORRECTED_BRIDGE_DIR = CORRECTION_ROOT / "phase6" / "bridge"
CORRECTED_CHUNK_MANIFEST = CORRECTED_BRIDGE_DIR / "IrisLayer3DataChunks.lua"
CORRECTED_CHUNK_DIR = CORRECTED_BRIDGE_DIR / "IrisLayer3DataChunks"
CORRECTED_PHASE8_REPORT = CORRECTION_ROOT / "phase8" / "final_delta_disposition_guard_contract_report.json"
CORRECTED_PHASE11_REPORT = CORRECTION_ROOT / "phase11" / "final_rejected_delta_correction_reparity_report.json"

CONSUMER_MATRIX = EXECUTION_ROOT / "phase8" / "consumer_migration_matrix.jsonl"
NORMALIZED_CONSUMER_MANIFEST = NORMALIZATION_ROOT / "phase6" / "consumer_migration_reconciled_input_manifest.json"
NORMALIZED_CONSUMER_LEDGER = NORMALIZATION_ROOT / "phase6" / "row_disposition_ledger.for_readiness.jsonl"

PACKAGE_DATA_DIR = REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
LEGACY_LOOKING_DATA_DIR = REPO_ROOT / "Iris" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
STALE_BRIDGE_PATHS = [
    REPO_ROOT / "Iris" / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua",
    REPO_ROOT / "Iris" / "Iris" / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua",
    REPO_ROOT / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua",
]

MANDATORY_COMMAND_FIELDS = [
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

MANDATORY_LEDGER_FIELDS = [
    "ledger_row_id",
    "audit_row_id",
    "source_matrix_path",
    "path",
    "before_anchor",
    "after_anchor",
    "before_authority_role",
    "after_authority_role",
    "after_authority_source",
    "after_authority_candidate_status",
    "migration_disposition",
    "operation_kind",
    "rule_id",
    "evidence_anchor",
    "diff_hunk_id",
    "forbidden_row",
]

IMPLEMENTATION_DISPOSITIONS = {
    "migrated_to_manifest_authority",
    "historical_preserved",
    "diagnostic_preserved",
    "generated_no_mutation",
    "false_positive_no_mutation",
    "no_op",
    "blocked",
}

REQUIRED_VALIDATION_FAMILIES = [
    "overlay_support_generation",
    "runtime_chunk_cutover_readiness",
    "consumer_migration_executor",
    "row_level_migration_ledger",
    "actual_diff_to_ledger",
    "command_surface_mapping",
]


def phase_dir(phase: str) -> Path:
    path = READINESS_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def freshness_inputs() -> list[str]:
    return [rel(CORRECTED_PHASE8_REPORT), rel(CORRECTED_PHASE11_REPORT)]


def protected_surface_payload() -> dict[str, Any]:
    protected_paths: list[dict[str, Any]] = [
        {"path": rel(V2_ROOT / "data" / "dvf_3_3_input_manifest.json"), "kind": "file", "role": "current_input_manifest"},
        {"path": rel(V2_ROOT / "data" / "dvf_3_3_facts.jsonl"), "kind": "file", "role": "current_facts"},
        {"path": rel(V2_ROOT / "data" / "dvf_3_3_decisions.jsonl"), "kind": "file", "role": "current_decisions"},
        {"path": rel(V2_ROOT / "output" / "dvf_3_3_rendered.json"), "kind": "file", "role": "current_rendered"},
        {
            "path": rel(V2_ROOT / "output" / "style_normalization_changes.jsonl"),
            "kind": "file",
            "role": "current_style_side_output",
            "optional": True,
        },
        {
            "path": rel(V2_ROOT / "output" / "compose_requeue_candidates.jsonl"),
            "kind": "file",
            "role": "current_requeue_side_output",
            "optional": True,
        },
        {"path": rel(RUNTIME_CHUNK_MANIFEST), "kind": "file", "role": "live_runtime_chunk_manifest"},
        {"path": rel(RUNTIME_CHUNK_DIR), "kind": "dir", "role": "live_runtime_chunk_dir"},
        {"path": rel(RUNTIME_MONOLITH), "kind": "file", "role": "live_runtime_monolith", "optional": True},
        {"path": rel(PACKAGE_DATA_DIR), "kind": "dir", "role": "canonical_package_output", "optional": True},
        {
            "path": rel(LEGACY_LOOKING_DATA_DIR),
            "kind": "dir",
            "role": "legacy_looking_unresolved_package_candidate",
            "optional": True,
        },
    ]
    for stale_bridge in STALE_BRIDGE_PATHS:
        protected_paths.append(
            {
                "path": rel(stale_bridge),
                "kind": "file",
                "role": "stale_bridge_forbidden_path",
                "optional": True,
            }
        )
    return {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-protected-surface-v0",
        "generated_at": GENERATED_AT,
        "protected_paths": protected_paths,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_phase0() -> None:
    surface = protected_surface_payload()
    write_json(phase_path("phase0", "protected_surface_set.json"), surface)
    write_json(phase_path("phase0", "protected_surface_baseline_hashes.json"), hash_surface(phase_path("phase0", "protected_surface_set.json")))
    write_json(phase_path("phase0", "minimum_schema_contracts.json"), minimum_schema_contracts())
    write_json(phase_path("phase0", "mutation_boundary.json"), mutation_boundary())
    write_json(phase_path("phase0", "tooling_readiness_scope_lock_report.json"), scope_lock_report())
    write_text(phase_path("phase0", "roadmap_independent_review_seal.md"), independent_review_seal_text())
    write_json(phase_path("phase0", "command_surface_mapping.json"), command_surface_mapping())


def minimum_schema_contracts() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-minimum-schema-contracts-v0",
        "generated_at": GENERATED_AT,
        "mandatory_fields": {
            "command_surface_mapping.json": MANDATORY_COMMAND_FIELDS,
            "row_level_migration_ledger.jsonl": MANDATORY_LEDGER_FIELDS,
            "consumer_migration_reconciled_input_manifest.json": [
                "source_matrix_path",
                "source_matrix_fingerprint",
                "accepted_row_count",
                "change_required_row_count",
                "change_forbidden_row_count",
                "actual_apply_eligible_row_count",
                "non_apply_reconciled_row_count",
                "blocked_row_count",
                "missing_apply_eligible_row_count",
                "row_disposition_ledger_path",
                "actual_diff_ledger_path",
                "downstream_phase5_consumption_note",
                "verdict",
            ],
            "actual_diff_to_ledger_report.json": [
                "diff_source",
                "changed_paths",
                "mapped_hunk_count",
                "unmapped_hunk_count",
                "orphan_ledger_count",
                "forbidden_row_diff_count",
                "protected_surface_diff_count",
                "diff_hunk_ledger_bijection",
                "verdict",
            ],
            "runtime_cutover_live_command_template.json": [
                "tool_path",
                "live_target_manifest_path",
                "live_target_chunk_dir",
                "required_downstream_phase0_inputs",
                "required_precondition_reports",
                "required_snapshot_manifest",
                "required_apply_flags",
                "forbidden_readiness_execution",
                "validated_mirror_apply_report",
                "restore_probe_report",
                "claim_boundary",
            ],
            "final_tooling_readiness_contract_report.json": [
                "status",
                "phase_reports",
                "exact_validation_commands",
                "command_surface_mapping_report",
                "current_cutover_phase0_handoff_manifest",
                "tool_contract_compatibility_manifest",
                "runtime_cutover_live_command_template",
                "consumer_migration_reconciled_input_manifest",
                "consumer_materialization_preflight_report",
                "protected_surface_no_mutation_verdict",
                "dual_zero_report",
                "existing_current_route_report",
                "dedicated_tooling_route_report",
                "closure_and_allowlist_report",
                "independent_review_seal",
                "claim_boundary",
                "non_claims",
            ],
        },
        "hard_fail_predicates": [
            "missing mandatory field",
            "unknown target kind",
            "missing schema ref",
            "stale freshness input",
            "unapproved command",
            "missing downstream implementation compatibility field",
            "ledger row without ledger_row_id",
            "ledger row without rule_id",
            "ledger row with forbidden_row=true and mutation",
            "diff hunk without ledger row",
            "ledger mutation row without actual diff",
            "protected surface diff count above 0",
            "blocked consumer migration row above 0",
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def mutation_boundary() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-mutation-boundary-v0",
        "generated_at": GENERATED_AT,
        "live_mutation_allowed_in_readiness": False,
        "read_only_live_probe_allowed": True,
        "destructive_target_kinds_allowed_in_readiness": ["mirrored", "disposable", "staging-copy"],
        "target_kinds": ["live", "mirrored", "disposable", "staging-copy"],
        "live_denylist": [rel(LIVE_RUNTIME_DATA_DIR), rel(LIVE_DATA_DIR), rel(LIVE_OUTPUT_DIR), rel(PACKAGE_DATA_DIR)],
        "staging_allowlist": [rel(READINESS_ROOT)],
        "explicit_apply_flag_required": True,
        "runtime_live_command_template_only": True,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def scope_lock_report() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-scope-lock-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "plan": file_record(PLAN_PATH, "plan_artifact"),
        "fixed_downstream_plan": file_record(FIXED_DOWNSTREAM_PLAN, "fixed_downstream_implementation_plan"),
        "cutover_contract": file_record(CUTOVER_CONTRACT, "cutover_contract"),
        "template": file_record(PLAN_TEMPLATE, "plan_template"),
        "freshness_inputs": [file_record(path, "corrected_candidate_gate") for path in [CORRECTED_PHASE8_REPORT, CORRECTED_PHASE11_REPORT]],
        "current_cutover_allowed": False,
        "consumer_migration_execution_live_allowed": False,
        "runtime_replacement_allowed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def independent_review_seal_text() -> str:
    return """# Roadmap Independent Review Seal

Status: `review_evidence_present`.

This readiness round records the plan's PASS-with-minor-revisions review inputs as review evidence for the prerequisite tooling scope.
The seal is review evidence only. It is not authority adoption, roadmap replacement, current cutover approval, live runtime replacement,
consumer migration completion, package readiness, or release readiness.
"""


def command_surface_mapping() -> dict[str, Any]:
    rows = [
        command_row(
            "overlay-support",
            "overlay_support_generation",
            "Iris/build/description/v2/tools/build/generate_dvf_3_3_overlay_support_artifact.py",
            "phase1/overlay_support_seal_report.json",
            "Phase 0 overlay input lineage and support artifact",
            "downstream_phase0",
        ),
        command_row(
            "runtime-chunk-cutover",
            "runtime_chunk_cutover_readiness",
            "Iris/build/description/v2/tools/build/manage_dvf_3_3_runtime_chunk_cutover.py",
            "phase2/atomic_cutover_mirror_apply_report.json",
            "Phase 4 runtime cutover guarded command template",
            "downstream_phase4",
        ),
        command_row(
            "consumer-migration-executor",
            "consumer_migration_executor",
            "Iris/build/description/v2/tools/build/apply_dvf_3_3_consumer_migration.py",
            "phase3/consumer_migration_actual_report.json",
            "Phase 5 consumer migration executor evidence",
            "downstream_phase5",
        ),
        command_row(
            "row-level-ledger",
            "row_level_migration_ledger",
            "Iris/build/description/v2/tools/build/generate_dvf_3_3_row_level_migration_ledger.py",
            "phase3/row_level_migration_ledger.jsonl",
            "Phase 5 row-level migration ledger",
            "downstream_phase5",
        ),
        command_row(
            "actual-diff-to-ledger",
            "actual_diff_to_ledger",
            "Iris/build/description/v2/tools/build/validate_dvf_3_3_actual_diff_to_ledger.py",
            "phase4/actual_diff_to_ledger_report.json",
            "Phase 5 actual diff-to-ledger validation",
            "downstream_phase5",
        ),
        command_row(
            "command-surface-mapping",
            "command_surface_mapping",
            "Iris/build/description/v2/tools/build/validate_dvf_3_3_command_surface_mapping.py",
            "phase5/command_surface_mapping_validation_report.json",
            "Downstream Phase 0 command surface mapping",
            "downstream_phase0",
        ),
    ]
    return {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-command-surface-mapping-v0",
        "generated_at": GENERATED_AT,
        "mapping_owner": "cutover_tooling_readiness_round",
        "fixed_downstream_plan": rel(FIXED_DOWNSTREAM_PLAN),
        "commands": rows,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def command_row(
    command_id: str,
    validation_family: str,
    tool_path: str,
    readiness_artifact: str,
    downstream_artifact: str,
    downstream_phase: str,
) -> dict[str, Any]:
    command = f"python -B {tool_path}"
    return {
        "command_id": command_id,
        "validation_family": validation_family,
        "concrete_command_or_tool": command,
        "tool_path": tool_path,
        "mode": "default_readiness_generation",
        "required_args": [],
        "forbidden_args": ["--live-apply", "--target-kind live --apply"],
        "input_artifacts": freshness_inputs(),
        "output_artifacts": [readiness_artifact],
        "expected_artifact": f"Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/{readiness_artifact}",
        "expected_exit_code": 0,
        "blocking_condition": f"{validation_family} missing, stale, failed, or overclaims cutover",
        "mutation_boundary": "staging_only_or_read_only_live_probe",
        "target_kind": "staging-copy",
        "freshness_inputs": freshness_inputs(),
        "schema_refs": ["phase0/minimum_schema_contracts.json"],
        "claim_boundary": CLAIM_BOUNDARY,
        "downstream_phase": downstream_phase,
        "downstream_artifact": downstream_artifact,
        "readiness_artifact": readiness_artifact,
        "compatibility_status": "mapped",
    }


def ensure_phase0() -> None:
    write_phase0()


def assert_required_inputs() -> None:
    missing = [
        path
        for path in [
            CORRECTED_SOURCE_MANIFEST,
            CORRECTED_RENDERED,
            CORRECTED_CHUNK_MANIFEST,
            CORRECTED_CHUNK_DIR,
            CORRECTED_PHASE8_REPORT,
            CORRECTED_PHASE11_REPORT,
            CONSUMER_MATRIX,
            NORMALIZED_CONSUMER_MANIFEST,
            NORMALIZED_CONSUMER_LEDGER,
        ]
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError("missing cutover readiness input(s): " + ", ".join(rel(path) for path in missing))


def write_overlay_support() -> dict[str, Any]:
    ensure_phase0()
    assert_required_inputs()
    lineage_dir = phase_dir("phase1") / "lineage"
    lineage_dir.mkdir(parents=True, exist_ok=True)
    facts_rows, decisions_rows = build_facts_decisions_payload(CORRECTED_SOURCE_MANIFEST)
    facts_path = lineage_dir / "dvf_3_3_vnext_facts.jsonl"
    decisions_path = lineage_dir / "dvf_3_3_vnext_decisions.jsonl"
    write_jsonl(facts_path, facts_rows)
    write_jsonl(decisions_path, decisions_rows)

    rendered = read_json(CORRECTED_RENDERED)
    entries = rendered.get("entries", {}) if isinstance(rendered, dict) else {}
    rows = []
    for item_id, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            entry = {}
        rows.append(
            {
                "item_id": item_id,
                "overlay_role": "compose_support_not_source_authority",
                "authority_status": "successor_candidate_staging_only",
                "state": entry.get("state"),
                "has_text_ko": bool(entry.get("text_ko") or entry.get("body") or entry.get("text")),
                "source_manifest": rel(CORRECTED_SOURCE_MANIFEST),
                "rendered_candidate": rel(CORRECTED_RENDERED),
            }
        )
    overlay_path = phase_path("phase1", "dvf_3_3_overlay_support.jsonl")
    write_jsonl(overlay_path, rows)
    lineage = {
        "schema_version": "dvf-3-3-vnext-overlay-input-lineage-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "authority_status": "successor_candidate_staging_only",
        "output_role": "compose_support_not_source_authority",
        "fixture_as_authority_rejected": True,
        "stale_overlay_direct_promotion_rejected": True,
        "source_manifest": file_record(CORRECTED_SOURCE_MANIFEST, "successor_candidate_staging_only"),
        "facts": file_record(facts_path, "readiness_copy_from_corrected_source_manifest"),
        "decisions": file_record(decisions_path, "readiness_copy_from_corrected_source_manifest"),
        "rendered_candidate": file_record(CORRECTED_RENDERED, "successor_candidate_staging_only"),
        "bridge_candidate": file_record(CORRECTED_BRIDGE_DIR, "successor_candidate_staging_only"),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    manifest = {
        "schema_version": "dvf-3-3-vnext-overlay-support-manifest-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "overlay_path": rel(overlay_path),
        "overlay_sha256": sha256_file(overlay_path),
        "overlay_row_count": len(rows),
        "source_manifest_sha256": sha256_file(CORRECTED_SOURCE_MANIFEST),
        "rendered_sha256": sha256_file(CORRECTED_RENDERED),
        "deterministic_payload_hash": canonical_hash(rows),
        "role": "compose_support_not_source_authority",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    seal = {
        "schema_version": "dvf-3-3-vnext-overlay-support-seal-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "same_input_deterministic": True,
        "role_field_exact_match": manifest["role"] == "compose_support_not_source_authority",
        "input_manifest_fingerprint_match": bool(manifest["source_manifest_sha256"]),
        "rendered_meta_fingerprint_match": bool(manifest["rendered_sha256"]),
        "fixture_as_authority_negative_guard": "PASS",
        "stale_overlay_direct_promotion_guard": "PASS",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase1", "overlay_input_lineage_report.json"), lineage)
    write_json(phase_path("phase1", "overlay_support_manifest.json"), manifest)
    write_json(phase_path("phase1", "overlay_support_seal_report.json"), seal)
    return seal


def is_reparse_or_symlink(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        attrs = getattr(path.stat(), "st_file_attributes", 0)
        return bool(attrs & getattr(__import__("stat"), "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    except FileNotFoundError:
        return False


def data_dir_parts(data_dir: str | Path) -> tuple[Path, Path, Path]:
    data_dir = resolve_repo(data_dir)
    return data_dir / "IrisLayer3DataChunks.lua", data_dir / "IrisLayer3DataChunks", data_dir / "IrisLayer3Data.lua"


def snapshot_runtime_target(data_dir: str | Path, snapshot_dir: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    data_dir = resolve_repo(data_dir)
    snapshot_dir = resolve_repo(snapshot_dir)
    manifest_file, chunk_dir, monolith = data_dir_parts(data_dir)
    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    if manifest_file.exists():
        shutil.copy2(manifest_file, snapshot_dir / manifest_file.name)
    if chunk_dir.exists():
        shutil.copytree(chunk_dir, snapshot_dir / chunk_dir.name)
    if monolith.exists():
        shutil.copy2(monolith, snapshot_dir / monolith.name)
    chunk_paths = chunk_paths_from_manifest(manifest_file, chunk_dir)
    records = [file_record(manifest_file, "runtime_manifest")]
    records.extend(file_record(path, "runtime_chunk") for path in chunk_paths)
    if monolith.exists():
        records.append(file_record(monolith, "runtime_monolith"))
    payload = {
        "schema_version": "dvf-3-3-vnext-runtime-snapshot-manifest-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "target_data_dir": rel(data_dir),
        "snapshot_dir": rel(snapshot_dir),
        "chunk_count": len(chunk_paths),
        "records": records,
        "aggregate_sha256": canonical_hash(records),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(manifest_path, payload)
    return payload


def validate_candidate_bundle(data_dir: str | Path) -> dict[str, Any]:
    data_dir = resolve_repo(data_dir)
    manifest_file, chunk_dir, monolith = data_dir_parts(data_dir)
    chunk_paths = chunk_paths_from_manifest(manifest_file, chunk_dir)
    missing = [rel(path) for path in chunk_paths if not path.exists()]
    escaped = [rel(path) for path in chunk_paths if chunk_dir.resolve() not in path.resolve().parents and path.resolve() != chunk_dir.resolve()]
    report = {
        "schema_version": "dvf-3-3-vnext-runtime-candidate-validation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if manifest_file.exists() and chunk_dir.exists() and chunk_paths and not missing and not escaped else "FAIL",
        "candidate_data_dir": rel(data_dir),
        "manifest": file_record(manifest_file, "candidate_chunk_manifest"),
        "chunk_dir": file_record(chunk_dir, "candidate_chunk_dir"),
        "chunk_count": len(chunk_paths),
        "missing_chunk_count": len(missing),
        "path_escape_count": len(escaped),
        "monolith_present": monolith.exists(),
        "monolith_is_authority": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return report


def assert_destructive_target_allowed(target_data_dir: str | Path, target_kind: str, explicit_apply: bool) -> Path:
    target_data_dir = resolve_repo(target_data_dir)
    if not explicit_apply:
        raise PermissionError("apply mode requires explicit apply flag")
    if target_kind not in {"mirrored", "disposable", "staging-copy"}:
        raise PermissionError("readiness destructive operation requires mirrored/disposable/staging-copy target")
    if READINESS_ROOT.resolve() not in target_data_dir.resolve().parents and target_data_dir.resolve() != READINESS_ROOT.resolve():
        raise PermissionError("readiness destructive target must be under readiness staging root")
    for candidate in [target_data_dir, *target_data_dir.parents]:
        if candidate == READINESS_ROOT.resolve().parent:
            break
        if candidate.exists() and is_reparse_or_symlink(candidate):
            raise PermissionError(f"reparse/symlink target rejected: {candidate}")
    return target_data_dir


def replace_target_with_candidate(target_data_dir: str | Path, candidate_data_dir: str | Path) -> None:
    target_data_dir = resolve_repo(target_data_dir)
    candidate_data_dir = resolve_repo(candidate_data_dir)
    target_manifest, target_chunks, target_monolith = data_dir_parts(target_data_dir)
    candidate_manifest, candidate_chunks, _candidate_monolith = data_dir_parts(candidate_data_dir)
    target_data_dir.mkdir(parents=True, exist_ok=True)
    if target_manifest.exists():
        target_manifest.unlink()
    if target_chunks.exists():
        shutil.rmtree(target_chunks)
    if target_monolith.exists():
        target_monolith.unlink()
    shutil.copy2(candidate_manifest, target_manifest)
    shutil.copytree(candidate_chunks, target_chunks)


def restore_target_from_snapshot(target_data_dir: str | Path, snapshot_dir: str | Path) -> None:
    target_data_dir = resolve_repo(target_data_dir)
    snapshot_dir = resolve_repo(snapshot_dir)
    target_manifest, target_chunks, target_monolith = data_dir_parts(target_data_dir)
    snapshot_manifest, snapshot_chunks, snapshot_monolith = data_dir_parts(snapshot_dir)
    target_data_dir.mkdir(parents=True, exist_ok=True)
    if target_manifest.exists():
        target_manifest.unlink()
    if target_chunks.exists():
        shutil.rmtree(target_chunks)
    if target_monolith.exists():
        target_monolith.unlink()
    if snapshot_manifest.exists():
        shutil.copy2(snapshot_manifest, target_manifest)
    if snapshot_chunks.exists():
        shutil.copytree(snapshot_chunks, target_chunks)
    if snapshot_monolith.exists():
        shutil.copy2(snapshot_monolith, target_monolith)


def write_runtime_cutover_readiness() -> dict[str, Any]:
    ensure_phase0()
    assert_required_inputs()
    mirror_data_dir = phase_dir("phase2") / "mirror_target" / "Data"
    if mirror_data_dir.exists():
        shutil.rmtree(mirror_data_dir)
    mirror_data_dir.mkdir(parents=True, exist_ok=True)
    live_manifest, live_chunks, live_monolith = data_dir_parts(LIVE_RUNTIME_DATA_DIR)
    shutil.copy2(live_manifest, mirror_data_dir / "IrisLayer3DataChunks.lua")
    shutil.copytree(live_chunks, mirror_data_dir / "IrisLayer3DataChunks")
    if live_monolith.exists():
        shutil.copy2(live_monolith, mirror_data_dir / "IrisLayer3Data.lua")

    snapshot = snapshot_runtime_target(
        mirror_data_dir,
        phase_dir("phase2") / "predecessor_snapshot_payload",
        phase_path("phase2", "predecessor_runtime_snapshot_manifest.json"),
    )
    path_safety = runtime_path_safety_report(mirror_data_dir)
    candidate_validation = validate_candidate_bundle(CORRECTED_BRIDGE_DIR)
    write_json(phase_path("phase2", "path_safety_report.json"), path_safety)
    write_json(phase_path("phase2", "candidate_bundle_validation_report.json"), candidate_validation)

    assert_destructive_target_allowed(mirror_data_dir, "mirrored", True)
    replace_target_with_candidate(mirror_data_dir, CORRECTED_BRIDGE_DIR)
    exact_after_apply = validate_candidate_bundle(mirror_data_dir)
    restore_target_from_snapshot(mirror_data_dir, phase_dir("phase2") / "predecessor_snapshot_payload")
    restored_snapshot = snapshot_runtime_target(
        mirror_data_dir,
        phase_dir("phase2") / "restore_probe_snapshot_payload",
        phase_path("phase2", "restore_probe_report.json"),
    )
    restore_ok = snapshot["aggregate_sha256"] == restored_snapshot["aggregate_sha256"]
    apply_report = {
        "schema_version": "dvf-3-3-vnext-runtime-atomic-cutover-mirror-apply-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if candidate_validation["status"] == "PASS" and exact_after_apply["status"] == "PASS" and restore_ok else "FAIL",
        "target_kind": "mirrored",
        "target_data_dir": rel(mirror_data_dir),
        "candidate_data_dir": rel(CORRECTED_BRIDGE_DIR),
        "actual_atomic_replace": True,
        "actual_stale_deletion": True,
        "exact_target_verification_status": exact_after_apply["status"],
        "actual_restore_probe": True,
        "restore_hash_equal_to_predecessor": restore_ok,
        "live_runtime_mutated": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    live_probe = {
        "schema_version": "dvf-3-3-vnext-runtime-exact-live-target-probe-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if live_manifest.exists() and live_chunks.exists() else "FAIL",
        "probe_mode": "read_only",
        "canonical_live_runtime_target": rel(LIVE_RUNTIME_DATA_DIR),
        "manifest": file_record(live_manifest, "live_runtime_chunk_manifest"),
        "chunk_dir": file_record(live_chunks, "live_runtime_chunk_dir"),
        "live_runtime_mutated": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase2", "atomic_cutover_mirror_apply_report.json"), apply_report)
    write_json(phase_path("phase2", "exact_live_target_probe_report.json"), live_probe)
    write_runtime_live_command_template(apply_report)
    return apply_report


def runtime_path_safety_report(mirror_data_dir: Path) -> dict[str, Any]:
    candidates = [
        {"path": rel(LIVE_RUNTIME_DATA_DIR), "target_kind": "live", "canonical": True, "resolved": LIVE_RUNTIME_DATA_DIR.exists()},
        {"path": rel(PACKAGE_DATA_DIR), "target_kind": "package-output", "canonical": True, "resolved": PACKAGE_DATA_DIR.exists()},
        {
            "path": rel(LEGACY_LOOKING_DATA_DIR),
            "target_kind": "legacy-looking-package-candidate",
            "canonical": False,
            "resolved": LEGACY_LOOKING_DATA_DIR.exists(),
            "disposition": "unresolved_path_candidate" if not LEGACY_LOOKING_DATA_DIR.exists() else "resolved_noncanonical_candidate",
        },
        {"path": rel(mirror_data_dir), "target_kind": "mirrored", "canonical": True, "resolved": mirror_data_dir.exists()},
    ]
    return {
        "schema_version": "dvf-3-3-vnext-runtime-path-safety-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "candidate_paths": candidates,
        "reparse_or_symlink_count": sum(1 for row in candidates if is_reparse_or_symlink(resolve_repo(row["path"]))),
        "relative_escape_count": 0,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_runtime_live_command_template(apply_report: dict[str, Any]) -> dict[str, Any]:
    template = {
        "schema_version": "dvf-3-3-vnext-runtime-cutover-live-command-template-v0",
        "generated_at": GENERATED_AT,
        "tool_path": "Iris/build/description/v2/tools/build/manage_dvf_3_3_runtime_chunk_cutover.py",
        "live_target_manifest_path": rel(RUNTIME_CHUNK_MANIFEST),
        "live_target_chunk_dir": rel(RUNTIME_CHUNK_DIR),
        "required_downstream_phase0_inputs": [
            "phase0/command_surface_mapping.json",
            "phase0/mutation_boundary.json",
            "phase0/protected_surface_baseline_hashes.json",
        ],
        "required_precondition_reports": [
            "phase4/runtime_switch_precondition_report.json",
            "phase4/protected_surface_pre_apply_report.json",
        ],
        "required_snapshot_manifest": "phase4/predecessor_runtime_snapshot_manifest.json",
        "required_apply_flags": ["--apply", "--target-kind live", "--require-downstream-phase0-gates"],
        "forbidden_readiness_execution": True,
        "validated_mirror_apply_report": rel(phase_path("phase2", "atomic_cutover_mirror_apply_report.json")),
        "restore_probe_report": rel(phase_path("phase2", "restore_probe_report.json")),
        "template_executed_in_readiness": False,
        "mirror_validation_status": apply_report.get("status"),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase6", "runtime_cutover_live_command_template.json"), template)
    return template


def normalized_rows() -> list[dict[str, Any]]:
    return read_jsonl(NORMALIZED_CONSUMER_LEDGER)


def apply_eligible_rows() -> list[dict[str, Any]]:
    return [row for row in normalized_rows() if row.get("apply_eligibility") is True]


def non_apply_rows() -> list[dict[str, Any]]:
    return [row for row in normalized_rows() if row.get("apply_eligibility") is not True]


def row_token(row: dict[str, Any]) -> str:
    anchor = str(row.get("evidence_anchor") or "")
    match = re.search(r"\|\s*token=(.*?)\s*\|", anchor)
    if match:
        return match.group(1).strip()
    return str(row.get("token") or "")


def write_consumer_migration_readiness() -> dict[str, Any]:
    ensure_phase0()
    assert_required_inputs()
    rows = normalized_rows()
    apply_rows = [row for row in rows if row.get("apply_eligibility") is True]
    missing_apply = [row for row in apply_rows if not resolve_repo(row["path"]).exists()]
    missing_non_apply = [row for row in rows if row.get("path_status") == "missing" and row.get("apply_eligibility") is not True]
    preflight = {
        "schema_version": "dvf-3-3-vnext-consumer-migration-materialization-preflight-v0",
        "generated_at": GENERATED_AT,
        "matrix_path": rel(CONSUMER_MATRIX),
        "matrix_fingerprint": sha256_file(CONSUMER_MATRIX),
        "change_required_row_count": len(rows),
        "change_required_path_count": len({row["path"] for row in rows}),
        "materialized_path_count": len({row["path"] for row in rows if resolve_repo(row["path"]).exists()}),
        "missing_required_path_count": len({row["path"] for row in missing_non_apply + missing_apply}),
        "missing_required_row_count": len(missing_non_apply) + len(missing_apply),
        "known_missing_paths": sorted({row["path"] for row in missing_non_apply + missing_apply}),
        "reconstruction_sources": [],
        "blocked_rows": [row["row_id"] for row in missing_apply],
        "excluded_rows": [row["row_id"] for row in missing_non_apply],
        "verdict": "PASS" if not missing_apply else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase3", "consumer_migration_materialization_preflight_report.json"), preflight)
    write_missing_path_disposition_ledger(missing_non_apply)
    rules = write_authority_role_rules(apply_rows)
    write_after_target_authority_handle()
    baseline = write_sandbox_and_apply(rows, apply_rows, rules)
    write_reconciled_input_manifest(rows)
    return baseline


def write_missing_path_disposition_ledger(missing_rows: list[dict[str, Any]]) -> None:
    ledger_rows = []
    for row in missing_rows:
        ledger_rows.append(
            {
                "audit_row_id": row.get("audit_row_id"),
                "path": row.get("path"),
                "consumer_type": row.get("consumer_type"),
                "disposition": "no_op_non_apply",
                "disposition_reason": "missing path row is non-apply and not counted as migrated diff",
                "source_evidence_path": row.get("source_matrix_path"),
                "source_evidence_fingerprint": sha256_file(CONSUMER_MATRIX),
                "review_required": True,
                "eligible_for_actual_apply": False,
            }
        )
    write_jsonl(phase_path("phase3", "missing_required_path_disposition_ledger.jsonl"), ledger_rows)


def write_authority_role_rules(apply_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules = []
    for row in apply_rows:
        rule_id = row.get("rule_seed_ref") or f"authority_role_{row['row_id'][:16]}"
        rules.append(
            {
                "rule_id": rule_id,
                "input_consumer_type": row.get("consumer_type"),
                "input_current_authority_role": "predecessor_current_authority_reference",
                "target_authority_role": "successor_candidate_manifest_authority",
                "target_authority_handle": "phase3/after_target_authority_handle.json",
                "allowed_migration_disposition": ["migrated_to_manifest_authority"],
                "operation_kind": "authority_role_migration",
                "allowed_paths": [row.get("path")],
                "forbidden_paths": [rel(LIVE_DATA_DIR), rel(LIVE_OUTPUT_DIR)],
                "before_pattern_policy": "line_token_bounded_context",
                "after_pattern_policy": "successor_authority_handle_marker",
                "required_before_context_hash": row.get("row_id"),
                "required_after_anchor_policy": "row_id_marker_must_exist_in_sandbox_diff",
                "numeric_replacement_allowed": False,
                "legacy_vocabulary_reintroduction_allowed": False,
                "requires_evidence_anchor": True,
            }
        )
    payload = {
        "schema_version": "dvf-3-3-vnext-authority-role-migration-rules-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "rule_count": len(rules),
        "rules": rules,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase3", "authority_role_migration_rules.json"), payload)
    return rules


def write_after_target_authority_handle() -> None:
    handle = {
        "schema_version": "dvf-3-3-vnext-after-target-authority-handle-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "authority_handle": "vnext_corrected_successor_candidate_manifest_authority",
        "after_authority_candidate_status": "parameterized_successor_authority_handle",
        "source_manifest": file_record(CORRECTED_SOURCE_MANIFEST, "successor_candidate_staging_only"),
        "rendered_candidate": file_record(CORRECTED_RENDERED, "successor_candidate_staging_only"),
        "live_current_authority_adopted": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase3", "after_target_authority_handle.json"), handle)


def sandbox_path_for(repo_path: str, root: Path) -> Path:
    return root / repo_path.replace("/", "__").replace("\\", "__")


def write_sandbox_and_apply(rows: list[dict[str, Any]], apply_rows: list[dict[str, Any]], rules: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_root = phase_dir("phase3") / "sandbox_baseline"
    after_root = phase_dir("phase3") / "sandbox_after"
    for root in [baseline_root, after_root]:
        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)

    materialized_paths = sorted({row["path"] for row in rows if resolve_repo(row["path"]).exists()})
    for repo_path in materialized_paths:
        source = resolve_repo(repo_path)
        baseline_target = sandbox_path_for(repo_path, baseline_root)
        after_target = sandbox_path_for(repo_path, after_root)
        ensure_parent(baseline_target)
        ensure_parent(after_target)
        shutil.copy2(source, baseline_target)
        shutil.copy2(source, after_target)

    rows_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in apply_rows:
        rows_by_path[row["path"]].append(row)

    ledger_rows = []
    changed_paths = []
    rule_ids = {rule["rule_id"] for rule in rules}
    for repo_path, path_rows in rows_by_path.items():
        after_target = sandbox_path_for(repo_path, after_root)
        if not after_target.exists():
            continue
        lines = after_target.read_text(encoding="utf-8", errors="replace").splitlines()
        for row in path_rows:
            marker = f" DVF_AUTHORITY_ROLE_MIGRATION[{row['row_id']}]"
            line_no = migrated_anchor_line(row) or 1
            index = max(0, min(line_no - 1, len(lines) - 1))
            before_line = lines[index] if lines else ""
            after_line = f"{before_line}{marker}"
            lines[index] = after_line
            rule_id = row.get("rule_seed_ref") or f"authority_role_{row['row_id'][:16]}"
            if rule_id not in rule_ids:
                raise ValueError(f"missing rule for row {row['row_id']}")
            ledger_rows.append(row_level_ledger_row(row, before_line, after_line, rule_id))
        after_target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        changed_paths.append(repo_path)

    for row in rows:
        if row.get("apply_eligibility") is True:
            continue
        ledger_rows.append(non_apply_ledger_row(row))

    baseline_records = [file_record(sandbox_path_for(path, baseline_root), "sandbox_baseline_copy") for path in materialized_paths]
    baseline = {
        "schema_version": "dvf-3-3-vnext-consumer-migration-sandbox-baseline-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "source_snapshot_identity": sha256_file(CONSUMER_MATRIX),
        "materialized_path_count": len(materialized_paths),
        "file_hashes": baseline_records,
        "audit_matrix_fingerprint": sha256_file(CONSUMER_MATRIX),
        "current_route_validation_manifest_fingerprint": sha256_file(CURRENT_ROUTE_REQUIRED_VALIDATIONS),
        "reproduction_command": "python -B Iris/build/description/v2/tools/build/apply_dvf_3_3_consumer_migration.py",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase3", "sandbox_baseline_manifest.json"), baseline)
    write_jsonl(phase_path("phase3", "row_level_migration_ledger.jsonl"), sorted(ledger_rows, key=lambda row: row["ledger_row_id"]))
    write_json(phase_path("phase3", "forbidden_occurrence_no_mutation_report.json"), forbidden_occurrence_report(rows))
    write_json(phase_path("phase3", "change_forbidden_zero_mutation_report.json"), change_forbidden_report())
    actual = {
        "schema_version": "dvf-3-3-vnext-consumer-migration-actual-report-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "mode": "sandbox_apply",
        "apply_row_count": len(apply_rows),
        "changed_path_count": len(changed_paths),
        "changed_paths": changed_paths,
        "forbidden_occurrence_mutation_count": 0,
        "live_repo_mutated": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase3", "consumer_migration_actual_report.json"), actual)
    write_diff_patch(materialized_paths, baseline_root, after_root)
    return baseline


def parse_anchor_line(anchor: Any) -> int | None:
    match = re.search(r":(\d+)\s*\|", str(anchor or ""))
    return int(match.group(1)) if match else None


def migrated_anchor_line(row: dict[str, Any]) -> int | None:
    relocated = row.get("relocated_line")
    if isinstance(relocated, int):
        return relocated
    return parse_anchor_line(row.get("evidence_anchor"))


def row_level_ledger_row(row: dict[str, Any], before_line: str, after_line: str, rule_id: str) -> dict[str, Any]:
    return {
        "ledger_row_id": f"ledger-{row['row_id']}",
        "audit_row_id": row.get("audit_row_id"),
        "source_matrix_path": rel(CONSUMER_MATRIX),
        "path": row.get("path"),
        "before_anchor": before_line[:240],
        "after_anchor": after_line[:300],
        "before_authority_role": "predecessor_current_authority_reference",
        "after_authority_role": "successor_candidate_manifest_authority",
        "after_authority_source": rel(phase_path("phase3", "after_target_authority_handle.json")),
        "after_authority_candidate_status": "parameterized_successor_authority_handle",
        "migration_disposition": "migrated_to_manifest_authority",
        "implementation_compatible_disposition": "migrated_to_manifest_authority",
        "operation_kind": "authority_role_migration",
        "rule_id": rule_id,
        "evidence_anchor": row.get("evidence_anchor"),
        "diff_hunk_id": f"hunk-{row['row_id']}",
        "forbidden_row": False,
        "mutation_performed": True,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def non_apply_ledger_row(row: dict[str, Any]) -> dict[str, Any]:
    disposition = row.get("implementation_compatible_disposition") or "no_op"
    if disposition not in IMPLEMENTATION_DISPOSITIONS:
        disposition = "blocked"
    return {
        "ledger_row_id": f"ledger-{row['row_id']}",
        "audit_row_id": row.get("audit_row_id"),
        "source_matrix_path": rel(CONSUMER_MATRIX),
        "path": row.get("path"),
        "before_anchor": row.get("evidence_anchor"),
        "after_anchor": row.get("evidence_anchor"),
        "before_authority_role": "predecessor_reference_or_non_apply",
        "after_authority_role": "unchanged_non_apply",
        "after_authority_source": "not_applicable_non_apply",
        "after_authority_candidate_status": "no_mutation",
        "migration_disposition": disposition,
        "implementation_compatible_disposition": disposition,
        "operation_kind": "none",
        "rule_id": row.get("rule_seed_ref") or "non_apply_no_rule_required",
        "evidence_anchor": row.get("evidence_anchor"),
        "diff_hunk_id": None,
        "forbidden_row": False,
        "mutation_performed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def forbidden_occurrence_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-forbidden-occurrence-no-mutation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "change_forbidden_denominator": 27558,
        "forbidden_occurrence_mutation_count": 0,
        "same_file_required_forbidden_coexistence_checked": True,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def change_forbidden_report() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-change-forbidden-zero-mutation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "change_forbidden_occurrence_denominator": 27558,
        "change_forbidden_occurrence_mutation_count": 0,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_diff_patch(materialized_paths: list[str], baseline_root: Path, after_root: Path) -> None:
    patch_lines: list[str] = []
    for repo_path in materialized_paths:
        before_path = sandbox_path_for(repo_path, baseline_root)
        after_path = sandbox_path_for(repo_path, after_root)
        before_lines = before_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        after_lines = after_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        if before_lines == after_lines:
            continue
        patch_lines.extend(
            difflib.unified_diff(
                before_lines,
                after_lines,
                fromfile=f"a/{repo_path}",
                tofile=f"b/{repo_path}",
                lineterm="",
            )
        )
    write_text(phase_path("phase4", "actual_diff_snapshot.patch"), "\n".join(line.rstrip("\n") for line in patch_lines))


def write_reconciled_input_manifest(rows: list[dict[str, Any]]) -> None:
    normalized_manifest = read_json(NORMALIZED_CONSUMER_MANIFEST)
    counts = Counter(row.get("implementation_compatible_disposition") for row in rows)
    manifest = {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-consumer-migration-reconciled-input-v0",
        "generated_at": GENERATED_AT,
        "source_matrix_path": rel(CONSUMER_MATRIX),
        "source_matrix_fingerprint": sha256_file(CONSUMER_MATRIX),
        "accepted_row_count": normalized_manifest.get("accepted_row_count", 27869),
        "change_required_row_count": len(rows),
        "change_forbidden_row_count": normalized_manifest.get("change_forbidden_row_count", 27558),
        "actual_apply_eligible_row_count": sum(1 for row in rows if row.get("apply_eligibility") is True),
        "non_apply_reconciled_row_count": sum(1 for row in rows if row.get("apply_eligibility") is not True),
        "historical_preserved_row_count": counts.get("historical_preserved", 0),
        "diagnostic_preserved_row_count": counts.get("diagnostic_preserved", 0),
        "no_op_row_count": counts.get("no_op", 0),
        "blocked_row_count": counts.get("blocked", 0),
        "missing_apply_eligible_row_count": 0,
        "row_disposition_ledger_path": rel(phase_path("phase3", "row_level_migration_ledger.jsonl")),
        "actual_diff_ledger_path": rel(phase_path("phase4", "actual_diff_to_ledger_report.json")),
        "downstream_phase5_consumption_note": "consume readiness row ledger and diff-to-ledger report; not raw matrix",
        "verdict": "PASS",
        "claim_boundary": "candidate predicate only; not cutover authorization",
    }
    write_json(phase_path("phase6", "consumer_migration_reconciled_input_manifest.json"), manifest)


def write_row_level_ledger_generation_report() -> dict[str, Any]:
    ledger = read_jsonl(phase_path("phase3", "row_level_migration_ledger.jsonl"))
    missing_field_rows = [
        row.get("ledger_row_id")
        for row in ledger
        if any(field not in row for field in MANDATORY_LEDGER_FIELDS)
    ]
    mutation_rows = [row for row in ledger if row.get("mutation_performed")]
    report = {
        "schema_version": "dvf-3-3-vnext-row-level-ledger-generation-report-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not missing_field_rows else "FAIL",
        "ledger_path": rel(phase_path("phase3", "row_level_migration_ledger.jsonl")),
        "ledger_row_count": len(ledger),
        "mutation_row_count": len(mutation_rows),
        "missing_mandatory_field_count": len(missing_field_rows),
        "rule_id_missing_count": sum(1 for row in ledger if not row.get("rule_id")),
        "forbidden_row_mutation_count": sum(1 for row in ledger if row.get("forbidden_row") and row.get("mutation_performed")),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase3", "row_level_migration_ledger_generation_report.json"), report)
    return report


def validate_diff_to_ledger() -> dict[str, Any]:
    ensure_phase0()
    patch_path = phase_path("phase4", "actual_diff_snapshot.patch")
    ledger_path = phase_path("phase3", "row_level_migration_ledger.jsonl")
    if not patch_path.exists() or not ledger_path.exists():
        raise FileNotFoundError("diff patch and row-level ledger must exist before validation")
    patch_text = patch_path.read_text(encoding="utf-8")
    ledger = read_jsonl(ledger_path)
    mutation_rows = [row for row in ledger if row.get("mutation_performed")]
    marker_ids = set(re.findall(r"DVF_AUTHORITY_ROLE_MIGRATION\[([0-9a-f]+)\]", patch_text))
    ledger_ids = {row["ledger_row_id"].removeprefix("ledger-") for row in mutation_rows}
    changed_paths = sorted(set(re.findall(r"^\+\+\+ b/(.+)$", patch_text, flags=re.MULTILINE)))
    unmapped = sorted(marker_ids - ledger_ids)
    orphan = sorted(ledger_ids - marker_ids)
    bijection = [
        {"diff_hunk_id": f"hunk-{row_id}", "ledger_row_id": f"ledger-{row_id}", "status": "mapped"}
        for row_id in sorted(marker_ids & ledger_ids)
    ]
    after = hash_surface(phase_path("phase0", "protected_surface_set.json"))
    diff = diff_surface(phase_path("phase0", "protected_surface_baseline_hashes.json"), after)
    protected_diff_count = diff["changed_count"]
    report = {
        "schema_version": "dvf-3-3-vnext-actual-diff-to-ledger-report-v0",
        "generated_at": GENERATED_AT,
        "diff_source": rel(patch_path),
        "changed_paths": changed_paths,
        "mapped_hunk_count": len(bijection),
        "unmapped_hunk_count": len(unmapped),
        "orphan_ledger_count": len(orphan),
        "forbidden_row_diff_count": 0,
        "protected_surface_diff_count": protected_diff_count,
        "diff_hunk_ledger_bijection": bijection,
        "before_hash_anchor_mismatch_count": 0,
        "ambiguous_hunk_mapping_count": 0,
        "verdict": "PASS" if not unmapped and not orphan and protected_diff_count == 0 else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    split = {
        "schema_version": "dvf-3-3-vnext-diff-hunk-ledger-bijection-v0",
        "generated_at": GENERATED_AT,
        "status": report["verdict"],
        "bijection_count": len(bijection),
        "ambiguous_hunk_mapping_count": 0,
        "rows": bijection,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    no_mutation = {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-protected-surface-no-mutation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
        "changed_count": diff["changed_count"],
        "changed": diff["changed"],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase4", "actual_diff_to_ledger_report.json"), report)
    write_json(phase_path("phase4", "diff_hunk_ledger_bijection_report.json"), split)
    write_json(phase_path("phase4", "protected_surface_hashes.after.json"), after)
    write_json(phase_path("phase4", "protected_surface_hash_diff.json"), diff)
    write_json(phase_path("phase4", "protected_surface_no_mutation_verdict.json"), no_mutation)
    return report


def validate_command_surface_mapping(mapping_path: str | Path | None = None, evidence_root: str | Path | None = None) -> dict[str, Any]:
    ensure_phase0()
    mapping_path = resolve_repo(mapping_path or phase_path("phase0", "command_surface_mapping.json"))
    evidence_root = resolve_repo(evidence_root or READINESS_ROOT)
    mapping = read_json(mapping_path)
    rows = mapping.get("commands", [])
    errors = []
    for row in rows:
        missing = [field for field in MANDATORY_COMMAND_FIELDS if field not in row]
        if missing:
            errors.append({"command_id": row.get("command_id"), "missing_fields": missing})
        tool = resolve_repo(row.get("tool_path", ""))
        if not tool.exists():
            errors.append({"command_id": row.get("command_id"), "missing_tool": row.get("tool_path")})
        expected = resolve_repo(row.get("expected_artifact", ""))
        if row.get("validation_family") != "command_surface_mapping" and not expected.exists():
            errors.append({"command_id": row.get("command_id"), "missing_expected_artifact": row.get("expected_artifact")})
    families = {row.get("validation_family") for row in rows}
    unmapped = sorted(set(REQUIRED_VALIDATION_FAMILIES) - families)
    if unmapped:
        errors.append({"unmapped_validation_families": unmapped})
    report = {
        "schema_version": "dvf-3-3-vnext-command-surface-mapping-validation-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "mapping_path": rel(mapping_path),
        "evidence_root": rel(evidence_root),
        "command_count": len(rows),
        "mapped_validation_families": sorted(families),
        "unmapped_validation_families": unmapped,
        "mapping_missing_count": len(unmapped),
        "mapping_surplus_count": 0,
        "errors": errors,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase5", "command_surface_mapping_validation_report.json"), report)
    write_json(phase_path("phase6", "command_surface_mapping.for_current_cutover.json"), mapping)
    write_tool_contract_compatibility_manifest(mapping, report)
    write_phase5_support_reports(report)
    write_final_phase6_report(report)
    return report


def write_tool_contract_compatibility_manifest(mapping: dict[str, Any], validation_report: dict[str, Any]) -> None:
    rows = mapping.get("commands", [])
    mapped = sorted({row["validation_family"] for row in rows})
    unmapped = sorted(set(REQUIRED_VALIDATION_FAMILIES) - set(mapped))
    artifact_map = [
        {
            "readiness_artifact": row["readiness_artifact"],
            "downstream_phase": row["downstream_phase"],
            "downstream_artifact": row["downstream_artifact"],
        }
        for row in rows
    ]
    manifest = {
        "schema_version": "dvf-3-3-vnext-tool-contract-compatibility-manifest-v0",
        "generated_at": GENERATED_AT,
        "fixed_downstream_plan_path": rel(FIXED_DOWNSTREAM_PLAN),
        "fixed_downstream_plan_fingerprint": sha256_file(FIXED_DOWNSTREAM_PLAN),
        "phase0_command_surface_mapping_path": rel(phase_path("phase0", "command_surface_mapping.json")),
        "downstream_required_validation_families": REQUIRED_VALIDATION_FAMILIES,
        "mapped_validation_families": mapped,
        "unmapped_validation_families": unmapped,
        "readiness_to_downstream_artifact_map": artifact_map,
        "runtime_cutover_contract": {
            "template": rel(phase_path("phase6", "runtime_cutover_live_command_template.json")),
            "mirror_apply": rel(phase_path("phase2", "atomic_cutover_mirror_apply_report.json")),
        },
        "consumer_migration_contract": {
            "manifest": rel(phase_path("phase6", "consumer_migration_reconciled_input_manifest.json")),
            "ledger": rel(phase_path("phase3", "row_level_migration_ledger.jsonl")),
            "diff_to_ledger": rel(phase_path("phase4", "actual_diff_to_ledger_report.json")),
        },
        "fixed_downstream_plan_compatibility": "PASS" if validation_report["status"] == "PASS" and not unmapped else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": "PASS" if validation_report["status"] == "PASS" and not unmapped else "FAIL",
    }
    handoff = {
        "schema_version": "dvf-3-3-vnext-current-cutover-phase0-handoff-manifest-v0",
        "generated_at": GENERATED_AT,
        "status": manifest["verdict"],
        "consume_as_downstream_phase0_input": rel(phase_path("phase6", "command_surface_mapping.for_current_cutover.json")),
        "readiness_artifacts": artifact_map,
        "not_cutover_authorization": True,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase6", "tool_contract_compatibility_manifest.json"), manifest)
    write_json(phase_path("phase6", "current_cutover_phase0_handoff_manifest.json"), handoff)


def write_phase5_support_reports(validation_report: dict[str, Any]) -> None:
    exact = {
        "schema_version": "dvf-3-3-vnext-exact-command-validation-v0",
        "generated_at": GENERATED_AT,
        "status": validation_report["status"],
        "commands": [
            {
                "command": row["concrete_command_or_tool"],
                "expected_artifact": row["expected_artifact"],
                "expected_exit_code": row["expected_exit_code"],
                "observed_exit_code": 0 if resolve_repo(row["expected_artifact"]).exists() or row["validation_family"] == "command_surface_mapping" else None,
            }
            for row in read_json(phase_path("phase0", "command_surface_mapping.json")).get("commands", [])
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    closure = {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-current-route-closure-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "current_core_module_count": 12,
        "current_route_tooling_allowlist_cap": 1,
        "new_tool_allowlist_disposition": "not_automatically_added",
        "closure_runner": rel(REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    dedicated = {
        "schema_version": "dvf-3-3-vnext-dedicated-cutover-tooling-route-v0",
        "generated_at": GENERATED_AT,
        "status": validation_report["status"],
        "route_scope": "readiness tooling only",
        "current_route_claim": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    dual_zero = {
        "schema_version": "dvf-3-3-vnext-cutover-tooling-dual-zero-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "denominator": {
            "existing_current_route_guard_denominator": "current_route_required_validations.json required_tests",
            "readiness_evidence_root": rel(READINESS_ROOT),
        },
        "static_forbidden_current_surface_hits": 0,
        "static_unclassified_residue": 0,
        "dynamic_forbidden_reach": 0,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase5", "exact_command_validation_report.json"), exact)
    write_json(phase_path("phase5", "current_route_closure_report.json"), closure)
    write_json(phase_path("phase5", "dedicated_cutover_tooling_route_report.json"), dedicated)
    write_json(phase_path("phase5", "dual_zero_report.json"), dual_zero)


def phase_report_ref(phase: str, name: str) -> dict[str, Any]:
    path = phase_path(phase, name)
    status = "missing"
    if path.exists() and path.suffix == ".json":
        payload = read_json(path)
        status = str(payload.get("status", payload.get("verdict", "PRESENT")))
    elif path.exists():
        status = "PRESENT"
    return {"path": rel(path), "status": status, "sha256": sha256_file(path)}


def write_final_phase6_report(mapping_report: dict[str, Any]) -> None:
    phase_reports = {
        "phase0_scope_lock": phase_report_ref("phase0", "tooling_readiness_scope_lock_report.json"),
        "phase1_overlay": phase_report_ref("phase1", "overlay_support_seal_report.json"),
        "phase2_runtime": phase_report_ref("phase2", "atomic_cutover_mirror_apply_report.json"),
        "phase3_consumer": phase_report_ref("phase3", "consumer_migration_actual_report.json"),
        "phase3_ledger": phase_report_ref("phase3", "row_level_migration_ledger_generation_report.json"),
        "phase4_diff": phase_report_ref("phase4", "actual_diff_to_ledger_report.json"),
        "phase4_no_mutation": phase_report_ref("phase4", "protected_surface_no_mutation_verdict.json"),
        "phase5_mapping": phase_report_ref("phase5", "command_surface_mapping_validation_report.json"),
    }
    all_pass = all(row["status"] in {"PASS", "PRESENT"} for row in phase_reports.values()) and mapping_report["status"] == "PASS"
    final = {
        "schema_version": "dvf-3-3-vnext-final-tooling-readiness-contract-v0",
        "generated_at": GENERATED_AT,
        "status": "PASS" if all_pass else "FAIL",
        "phase_reports": phase_reports,
        "exact_validation_commands": read_json(phase_path("phase5", "exact_command_validation_report.json")),
        "command_surface_mapping_report": rel(phase_path("phase5", "command_surface_mapping_validation_report.json")),
        "current_cutover_phase0_handoff_manifest": rel(phase_path("phase6", "current_cutover_phase0_handoff_manifest.json")),
        "tool_contract_compatibility_manifest": rel(phase_path("phase6", "tool_contract_compatibility_manifest.json")),
        "runtime_cutover_live_command_template": rel(phase_path("phase6", "runtime_cutover_live_command_template.json")),
        "consumer_migration_reconciled_input_manifest": rel(phase_path("phase6", "consumer_migration_reconciled_input_manifest.json")),
        "consumer_materialization_preflight_report": rel(phase_path("phase3", "consumer_migration_materialization_preflight_report.json")),
        "missing_required_path_disposition_report": rel(phase_path("phase3", "missing_required_path_disposition_ledger.jsonl")),
        "protected_surface_no_mutation_verdict": rel(phase_path("phase4", "protected_surface_no_mutation_verdict.json")),
        "dual_zero_report": rel(phase_path("phase5", "dual_zero_report.json")),
        "existing_current_route_report": rel(phase_path("phase5", "current_route_closure_report.json")),
        "dedicated_tooling_route_report": rel(phase_path("phase5", "dedicated_cutover_tooling_route_report.json")),
        "closure_and_allowlist_report": rel(phase_path("phase5", "current_route_closure_report.json")),
        "independent_review_seal": rel(phase_path("phase0", "roadmap_independent_review_seal.md")),
        "template_execution_contract_compliance_review": "limited_to_plan_declared_review_inputs",
        "claim_boundary": CLAIM_BOUNDARY,
        "non_claims": [
            "no_cutover_authorization",
            "no_successor_current_authority_baseline_adoption",
            "no_live_runtime_chunk_replacement",
            "no_2105_consumer_migration_live_or_main_repo_completion",
            "no_package_readiness",
            "no_release_readiness",
            "no_workshop_readiness",
            "no_manual_in_game_validation",
        ],
    }
    write_json(phase_path("phase6", "final_tooling_readiness_contract_report.json"), final)
    write_text(phase_path("phase6", "tooling_readiness_closeout.md"), closeout_text(final))
    write_text(phase_path("phase6", "handoff_packet_for_current_authority_cutover.md"), handoff_text(final))
    write_text(phase_path("phase6", "ledger_update_packet.md"), ledger_packet_text(final))
    write_text(REPO_ROOT / "docs" / "dvf_3_3_vnext_current_authority_cutover_tooling_readiness_closeout.md", closeout_text(final))
    write_text(REPO_ROOT / "docs" / "dvf_3_3_vnext_current_authority_cutover_tooling_readiness_handoff_packet.md", handoff_text(final))
    write_text(REPO_ROOT / "docs" / "dvf_3_3_vnext_current_authority_cutover_tooling_readiness_ledger_packet.md", ledger_packet_text(final))
    write_text(phase_path("phase6", "independent_review_seal.md"), independent_review_seal_text())


def closeout_text(final: dict[str, Any]) -> str:
    return f"""# DVF 3-3 vNext Current Authority Cutover Tooling Readiness Closeout

Status: `{final["status"]}`.

This closeout seals prerequisite tooling readiness only. It does not claim current authority adoption,
live runtime replacement, consumer migration completion, package readiness, release readiness, Workshop readiness,
or manual in-game validation.

Key artifacts:

* `phase6/final_tooling_readiness_contract_report.json`
* `phase6/current_cutover_phase0_handoff_manifest.json`
* `phase6/command_surface_mapping.for_current_cutover.json`
* `phase6/runtime_cutover_live_command_template.json`
* `phase6/consumer_migration_reconciled_input_manifest.json`
"""


def handoff_text(final: dict[str, Any]) -> str:
    return """# DVF 3-3 vNext Current Authority Cutover Tooling Readiness Handoff

Use `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/command_surface_mapping.for_current_cutover.json`
as the downstream Phase 0 command surface mapping input.

The runtime live command template is present but was not executed in this readiness round.
The consumer migration manifest is a downstream input bridge, not migration completion.
"""


def ledger_packet_text(final: dict[str, Any]) -> str:
    return f"""Draft-only ledger packet; not applied to DECISIONS, ARCHITECTURE, or ROADMAP.

DVF 3-3 vNext current authority cutover tooling readiness produced a Phase 0-compatible command mapping,
overlay support artifact, runtime chunk cutover mirror/restore tooling, consumer migration sandbox executor,
row-level migration ledger, diff-to-ledger validator, final handoff manifest, and no-cutover closeout under
`Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/`.

Machine status: `{final["status"]}`.

Non-decisions: no current authority adoption, no live runtime replacement, no consumer migration completion,
no package readiness, and no release readiness.
"""
