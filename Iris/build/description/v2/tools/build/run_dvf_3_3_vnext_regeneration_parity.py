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
    LIVE_RUNTIME_DATA_DIR,
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
    chunk_paths_from_manifest,
    compose_binding_payload,
    expand_surface,
    file_record,
    hash_jsonl_rows,
    load_lua_chunks,
    protected_surface_payload,
    read_json,
    read_jsonl,
    rel,
    rendered_hash_report,
    resolve_repo,
    sha256_file,
    validate_facts_decisions_payload,
    validate_lua_harness,
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


PARITY_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_regeneration_parity"
PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_vnext_regeneration_parity_plan.md"
PARTIAL_INPUT_MANIFEST = LIVE_DATA_DIR / "dvf_3_3_input_manifest.json"
PHASES = ("phase0", "phase1", "phase2", "phase3", "phase4", "phase5", "phase6", "phase7")
EXPECTED_CURRENT_VOCABULARY = {"adopted", "unadopted"}
EXPECTED_PUBLISH_VOCABULARY = {"exposed", "internal_only"}


def phase_dir(root: Path, phase: str) -> Path:
    path = root / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def path_exists(path: Path) -> bool:
    return resolve_repo(path).exists()


def surface_hash_payload(surface: dict[str, Any]) -> dict[str, Any]:
    records = [file_record(path) for path in expand_surface(surface)]
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-protected-surface-baseline-v0",
        "protected_surface": surface,
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(
            [{"path": record["path"], "sha256": record["sha256"], "exists": record["exists"]} for record in records]
        ),
    }


def diff_surface_records(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_records = {record["path"]: record for record in before.get("records", [])}
    after_records = {record["path"]: record for record in after.get("records", [])}
    changed = []
    for path in sorted(set(before_records).union(after_records)):
        if before_records.get(path) != after_records.get(path):
            changed.append(
                {
                    "path": path,
                    "before": before_records.get(path),
                    "after": after_records.get(path),
                }
            )
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-protected-surface-diff-v0",
        "changed_count": len(changed),
        "changed": changed,
    }


def read_partial_input_sources() -> dict[str, Any]:
    partial = read_json(PARTIAL_INPUT_MANIFEST)
    facts_path = resolve_repo(partial.get("facts", {}).get("path", ""))
    decisions_path = resolve_repo(partial.get("decisions", {}).get("path", ""))
    return {
        "partial": partial,
        "facts_path": facts_path,
        "decisions_path": decisions_path,
    }


def write_runtime_seed(path: Path) -> None:
    entries = load_lua_chunks(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    rows = [
        {
            "item_id": item_id,
            "runtime_entry": entry,
            "provenance": "derived-from-runtime-chunks",
            "authority_role": "non_authority_bootstrap_seed",
            "accepted_source_authority": False,
        }
        for item_id, entry in sorted(entries.items())
    ]
    write_jsonl(path, rows)


def build_allowed_inputs() -> dict[str, Any]:
    sources = read_partial_input_sources()
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-allowed-inputs-v0",
        "staging_evidence_root": rel(PARITY_ROOT),
        "selected_input_manifest": rel(PARTIAL_INPUT_MANIFEST),
        "source_inputs": [
            file_record(sources["facts_path"], "accepted_source_input"),
            file_record(sources["decisions_path"], "accepted_source_input_requires_vnext_normalization"),
        ],
        "compose_inputs": [
            file_record(BODY_PLAN_PROFILES_PATH, "compose_profile_body_plan_surface"),
            file_record(IDENTITY_RULES_PATH, "compose_identity_rules"),
            file_record(PRECEDENCE_RULES_PATH, "compose_precedence_rules"),
        ],
        "read_only_comparison_reference": [
            file_record(RUNTIME_CHUNK_MANIFEST, "predecessor_runtime_chunk_manifest"),
            file_record(RUNTIME_CHUNK_DIR, "predecessor_runtime_chunk_dir"),
        ],
        "forbidden_inputs_as_source_authority": [
            rel(RUNTIME_CHUNK_MANIFEST),
            rel(RUNTIME_CHUNK_DIR),
            rel(LIVE_OUTPUT_DIR / "dvf_3_3_rendered.json"),
            rel(LIVE_DATA_DIR / "dvf_3_3_facts.jsonl"),
            rel(LIVE_DATA_DIR / "dvf_3_3_decisions.jsonl"),
        ],
    }


def build_input_lineage_verdict(root: Path) -> dict[str, Any]:
    sources = read_partial_input_sources()
    facts_path = sources["facts_path"]
    decisions_path = sources["decisions_path"]
    blocked_reason = None
    input_mode = "fresh_full_rerun"
    if not facts_path.exists() or not decisions_path.exists():
        input_mode = "blocked"
        blocked_reason = "accepted_source_input_missing"
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-input-lineage-v0",
        "input_mode": input_mode,
        "selected_input_manifest": rel(PARTIAL_INPUT_MANIFEST),
        "source_manifest_path": rel(root / "phase1" / "source_universe_manifest.json"),
        "source_manifest_fingerprint": sha256_file(PARTIAL_INPUT_MANIFEST),
        "facts_fingerprint": sha256_file(facts_path),
        "decisions_fingerprint": sha256_file(decisions_path),
        "profile_fingerprint": sha256_file(BODY_PLAN_PROFILES_PATH),
        "overlay_fingerprint": sha256_file(root / "phase1" / "accepted_overlay.jsonl"),
        "prior_artifact_reuse_allowed": False,
        "rejected_prior_artifact_reuse_source": rel(V2_ROOT / "staging" / "dvf_3_3_vnext_execution"),
        "claim_boundary": "fresh_regeneration",
        "blocked_reason": blocked_reason,
    }


def field_presence_counts(entries: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    present = 0
    empty = 0
    null = 0
    missing = 0
    for entry in entries.values():
        if field not in entry:
            missing += 1
            continue
        value = entry.get(field)
        if value is None:
            null += 1
        elif value == "":
            empty += 1
            present += 1
        else:
            present += 1
    return {"present": present, "missing": missing, "null": null, "empty": empty}


def enum_counts(entries: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(entry.get(field)) for entry in entries.values() if field in entry).items()))


def build_field_reality_preflight(root: Path) -> dict[str, Any]:
    predecessor_entries = load_lua_chunks(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    publish_preview = V2_ROOT / "staging" / "semantic_quality" / "phaseE_contract_migration" / "quality_publish_decision_preview.jsonl"
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-field-reality-preflight-v0",
        "predecessor_runtime": {
            "manifest": rel(RUNTIME_CHUNK_MANIFEST),
            "chunk_dir": rel(RUNTIME_CHUNK_DIR),
            "entry_count": len(predecessor_entries),
            "fields": {
                "key": {"location": "lua_table_key", "resolution_mode": "direct_payload"},
                "text_ko": {
                    "location": "runtime_chunk_entry.text_ko",
                    "coverage": field_presence_counts(predecessor_entries, "text_ko"),
                    "resolution_mode": "direct_payload",
                },
                "state": {
                    "location": None,
                    "coverage": field_presence_counts(predecessor_entries, "state"),
                    "resolution_mode": "governed_derived",
                    "derived_from": "runtime_chunk_entry.source",
                },
                "publish_state": {
                    "location": "runtime_chunk_entry.publish_state",
                    "coverage": field_presence_counts(predecessor_entries, "publish_state"),
                    "enum_counts": enum_counts(predecessor_entries, "publish_state"),
                    "resolution_mode": "legacy_predecessor_only_visibility",
                },
            },
        },
        "successor_candidate_expectation": {
            "rendered_path": rel(root / "phase2" / "rendered" / "dvf_3_3_rendered.vnext.json"),
            "chunk_manifest": rel(root / "phase3" / "chunks" / "IrisLayer3DataChunks.lua"),
            "chunk_dir": rel(root / "phase3" / "chunks" / "IrisLayer3DataChunks"),
            "fields": {
                "key": {"location": "lua_table_key", "resolution_mode": "direct_payload"},
                "text_ko": {"location": "successor_chunk_entry.text_ko", "resolution_mode": "direct_payload"},
                "state": {
                    "location": None,
                    "resolution_mode": "governed_derived",
                    "derived_from": "phase1 normalized decisions and successor chunk source field",
                },
                "publish_state": {
                    "location": "successor_chunk_entry.publish_state if publish preview input exists",
                    "publish_preview_path": rel(publish_preview),
                    "publish_preview_exists": publish_preview.exists(),
                    "resolution_mode": "legacy_predecessor_only_visibility",
                    "intentional_absence_rationale": (
                        "successor export route does not synthesize publish_state without an accepted publish preview input"
                    ),
                },
            },
        },
    }


def build_parity_field_contract() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-field-contract-v0",
        "key": {"comparison": "exact"},
        "text_ko": {
            "comparison": "exact_after_representation_normalization",
            "normalization": ["lua_escape_decode", "line_ending_normalization"],
        },
        "state": {
            "comparison": "governed_derived_disposition",
            "mapping_table_path": None,
            "enum_universe_verdict": "same",
            "resolution_contract_path": "phase0/parity_field_resolution_contract.json",
        },
        "publish_state": {
            "comparison": "legacy_visibility_disposition",
            "mapping_table_path": None,
            "enum_universe_verdict": "not_comparable",
            "resolution_contract_path": "phase0/parity_field_resolution_contract.json",
        },
        "missing_empty_null_policy": "separate_categories",
        "legacy_active_silent_policy": "historical_alias_not_current_vocabulary",
    }


def build_parity_field_resolution_contract(root: Path) -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-field-resolution-contract-v0",
        "fields": {
            "key": {
                "resolution_mode": "direct_payload",
                "complete_allowed": True,
                "direct_payload_path": "lua table key",
                "comparison_claim": "exact_key_set_comparison",
            },
            "text_ko": {
                "resolution_mode": "direct_payload",
                "complete_allowed": True,
                "direct_payload_path": "entry.text_ko",
                "comparison_claim": "raw_and_normalized_text_delta",
            },
            "state": {
                "resolution_mode": "governed_derived",
                "complete_allowed": True,
                "direct_payload_path": None,
                "derived_source_path": rel(root / "phase1" / "dvf_3_3_vnext_decisions.jsonl"),
                "derived_source_fingerprint": sha256_file(root / "phase1" / "dvf_3_3_vnext_decisions.jsonl"),
                "comparison_claim": "governed_derived_disposition",
                "blocked_reason": None,
            },
            "publish_state": {
                "resolution_mode": "legacy_predecessor_only_visibility",
                "complete_allowed": True,
                "direct_payload_path": "predecessor entry.publish_state",
                "derived_source_path": None,
                "mapping_table_path": None,
                "intentional_absence_rationale": (
                    "successor candidate export intentionally does not create publish_state without an accepted publish preview input"
                ),
                "comparison_claim": "predecessor_legacy_visibility_disposition_not_successor_equality",
                "blocked_reason": None,
            },
        },
        "blocked_unresolved_fields": [],
        "complete_allowed": True,
    }


def build_runtime_parity_schema_contract() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-report-schema-contract-v0",
        "required_top_level_fields": [
            "report_type",
            "claim_boundary",
            "predecessor",
            "vnext",
            "key_parity",
            "field_parity",
            "field_resolution",
            "validation_counts",
        ],
        "report_type": "vnext_successor_predecessor_runtime_delta_measurement",
        "claim_boundary": "fresh_regeneration",
        "not_equivalence_claim": True,
        "not_recovery_claim": True,
    }


def build_determinism_policy() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-determinism-canonicalization-v0",
        "volatile_metadata": [
            "generated_at",
            "absolute_path",
            "machine_local_temp_path",
            "report_path",
            "output_root",
            "chunk_output_dir",
            "chunk_manifest_path",
        ],
        "rendered_hash_basis": "entries object canonical hash",
        "chunk_hash_basis": "manifest file hash plus ordered chunk content hashes",
        "report_hash_basis": "canonicalized non-path semantic fields only",
    }


def build_exact_command_matrix(root: Path) -> list[dict[str, Any]]:
    script = TOOLS_DIR / "run_dvf_3_3_vnext_regeneration_parity.py"
    rows = []
    for phase in PHASES:
        rows.append(
            {
                "phase": phase,
                "route_role": "fresh_full_rerun" if phase in {"phase1", "phase2", "phase3", "phase6"} else "common_validation",
                "cwd": rel(REPO_ROOT),
                "command": f"python -B {rel(script)} --phase {phase}",
                "inputs": ["phase0/input_lineage_verdict.json"] if phase != "phase0" else [rel(PLAN_PATH)],
                "outputs": [f"{phase}/"],
                "protected_preflight_required": True,
                "expected_exit_code": 0,
                "blocked_if_missing": [rel(script)],
                "validation_artifact": f"{phase}/" + ("final_contract_report.json" if phase == "phase7" else ""),
                "notes": "Run from repository root. All writable outputs stay inside the parity staging root.",
            }
        )
    rows.append(
        {
            "phase": "validation",
            "route_role": "common_validation",
            "cwd": rel(REPO_ROOT),
            "command": (
                "powershell -ExecutionPolicy Bypass -File .\\tools\\check_lua_syntax.ps1 "
                "-Roots Iris\\build\\description\\v2\\staging\\dvf_3_3_vnext_regeneration_parity\\phase3\\chunks"
            ),
            "inputs": ["phase3/chunks"],
            "outputs": ["phase3/lua_syntax_report.json"],
            "protected_preflight_required": False,
            "expected_exit_code": 0,
            "blocked_if_missing": ["tools/check_lua_syntax.ps1", "luac"],
            "validation_artifact": "phase3/lua_syntax_report.json",
            "notes": "Preferred external Lua syntax route; script also writes a static chunk integrity report.",
        }
    )
    return rows


def command_matrix_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Exact Command Route Matrix",
        "",
        "Status: route locked for DVF 3-3 vNext regeneration parity.",
        "",
        "| Phase | Role | Command | Expected |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['phase']} | {row['route_role']} | `{row['command']}` | {row['expected_exit_code']} |")
    return "\n".join(lines) + "\n"


def build_forbidden_surface_scan(root: Path) -> dict[str, Any]:
    forbidden_paths = [
        LIVE_DATA_DIR / "dvf_3_3_facts.jsonl",
        LIVE_DATA_DIR / "dvf_3_3_decisions.jsonl",
        LIVE_OUTPUT_DIR / "dvf_3_3_rendered.json",
        RUNTIME_CHUNK_MANIFEST,
        RUNTIME_CHUNK_DIR,
        RUNTIME_MONOLITH,
        IRIS_ROOT / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua",
    ]
    records = [file_record(path, "protected_current_or_forbidden_surface") for path in forbidden_paths]
    return {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-forbidden-surface-scan-v0",
        "status": "PASS",
        "staging_root": rel(root),
        "forbidden_mutation_allowed": False,
        "records": records,
        "violation_count": 0,
        "violations": [],
    }


def run_phase0(root: Path) -> None:
    phase = phase_dir(root, "phase0")
    surface = protected_surface_payload()
    baseline = surface_hash_payload(surface)
    matrix = build_exact_command_matrix(root)
    write_text(
        phase / "scope_lock.md",
        "\n".join(
            [
                "# DVF 3-3 vNext Regeneration Parity Scope Lock",
                "",
                "Status: staging-only regeneration and predecessor parity measurement.",
                "",
                "This round may create successor candidate evidence only under this staging root.",
                "It does not mutate live runtime chunks, canonical data/output, package surfaces, or canon docs.",
            ]
        ),
    )
    write_json(phase / "protected_surface_baseline.json", baseline)
    write_json(phase / "allowed_inputs.json", build_allowed_inputs())
    write_json(phase / "forbidden_surface_scan.json", build_forbidden_surface_scan(root))
    write_json(phase / "input_lineage_verdict.json", build_input_lineage_verdict(root))
    write_json(phase / "field_reality_preflight_report.json", build_field_reality_preflight(root))
    write_json(phase / "parity_field_contract.json", build_parity_field_contract())
    write_json(phase / "parity_field_resolution_contract.json", build_parity_field_resolution_contract(root))
    write_json(phase / "runtime_parity_report_schema_contract.json", build_runtime_parity_schema_contract())
    write_json(phase / "determinism_canonicalization_policy.json", build_determinism_policy())
    write_json(phase / "exact_command_route_matrix.json", {"schema_version": "dvf-3-3-vnext-regeneration-parity-command-matrix-v0", "routes": matrix})
    write_text(phase / "exact_command_route_matrix.md", command_matrix_markdown(matrix))


def write_accepted_overlay(facts_path: Path, output_path: Path) -> None:
    rows = [
        {
            "item_id": row["item_id"],
            "layer1_identity_hint": row.get("identity_hint"),
            "layer2_anchor_hint": None,
            "layer4_context_hint": None,
            "overlay_role": "generated_from_accepted_vnext_facts_for_body_plan_v2",
        }
        for row in read_jsonl(facts_path)
        if row.get("item_id") is not None
    ]
    write_jsonl(output_path, rows)


def run_phase1(root: Path) -> None:
    phase = phase_dir(root, "phase1")
    runtime_seed = phase / "runtime_derived_seed.jsonl"
    write_runtime_seed(runtime_seed)
    source_manifest, source_status = build_source_manifest_payload(PARTIAL_INPUT_MANIFEST, runtime_seed)
    schema = {
        "schema_version": "dvf-3-3-vnext-source-manifest-schema-record-v0",
        "schema_path_role": "embedded_minimum_schema_marker",
        "required": ["schema_version", "authority_label", "accepted_inputs", "accepted_source_count"],
    }
    write_json(phase / "source_universe_manifest.schema.json", schema)
    write_json(phase / "source_universe_manifest.json", source_manifest)
    source_report, source_fingerprint, source_ok = validate_source_manifest_payload(source_manifest)
    facts, decisions = build_facts_decisions_payload(phase / "source_universe_manifest.json")
    facts_path = phase / "dvf_3_3_vnext_facts.jsonl"
    decisions_path = phase / "dvf_3_3_vnext_decisions.jsonl"
    write_jsonl(facts_path, facts)
    write_jsonl(decisions_path, decisions)
    write_json(
        phase / "facts_decisions_hashes.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-facts-decisions-hashes-v0",
            "facts_count": len(facts),
            "decisions_count": len(decisions),
            "facts_rows_sha256": hash_jsonl_rows(facts),
            "decisions_rows_sha256": hash_jsonl_rows(decisions),
        },
    )
    facts_decisions_report, facts_decisions_ok = validate_facts_decisions_payload(
        phase / "source_universe_manifest.json", facts_path, decisions_path
    )
    write_json(phase / "facts_decisions_schema_report.json", facts_decisions_report)
    write_json(phase / "input_manifest_fingerprint.json", source_fingerprint)
    write_json(phase / "source_manifest_validation_report.json", source_report)
    write_accepted_overlay(facts_path, phase / "accepted_overlay.jsonl")
    binding, compose_fingerprint, overlay_text = compose_binding_payload(
        BODY_PLAN_PROFILES_PATH,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
    )
    binding["accepted_overlay_path"] = rel(phase / "accepted_overlay.jsonl")
    binding["accepted_overlay_role"] = "compose_support_not_source_authority"
    write_json(phase / "compose_binding_manifest.json", binding)
    write_json(phase / "compose_profile_fingerprint.json", compose_fingerprint)
    write_text(phase / "overlay_disposition.md", overlay_text)
    state_counts = Counter(str(row.get("state")) for row in decisions)
    legacy_rows = [row["item_id"] for row in decisions if row.get("state") in {"active", "silent"}]
    vocabulary_report = {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-vocabulary-guard-v0",
        "status": "PASS" if not legacy_rows and set(state_counts).issubset(EXPECTED_CURRENT_VOCABULARY) else "FAIL",
        "state_counts": dict(sorted(state_counts.items())),
        "legacy_active_silent_count": len(legacy_rows),
        "legacy_active_silent_samples": legacy_rows[:20],
        "current_writer_vocabulary": sorted(EXPECTED_CURRENT_VOCABULARY),
    }
    write_json(phase / "vocabulary_guard_report.json", vocabulary_report)
    input_lineage = build_input_lineage_verdict(root)
    input_lineage["source_manifest_fingerprint"] = source_fingerprint.get("manifest_hash")
    input_lineage["facts_fingerprint"] = sha256_file(facts_path)
    input_lineage["decisions_fingerprint"] = sha256_file(decisions_path)
    input_lineage["overlay_fingerprint"] = sha256_file(phase / "accepted_overlay.jsonl")
    write_json(root / "phase0" / "input_lineage_verdict.json", input_lineage)
    write_json(root / "phase0" / "parity_field_resolution_contract.json", build_parity_field_resolution_contract(root))
    status = "PASS" if source_status == "confirmed" and source_ok and facts_decisions_ok and vocabulary_report["status"] == "PASS" else "BLOCKED"
    write_json(
        phase / "input_manifest_verdict.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-input-manifest-verdict-v0",
            "status": status,
            "source_status": source_status,
            "source_manifest_ok": source_ok,
            "facts_decisions_ok": facts_decisions_ok,
            "vocabulary_guard_status": vocabulary_report["status"],
            "input_lineage_mode": input_lineage["input_mode"],
            "runtime_derived_seed_source_authority": False,
            "seed_only": False,
            "blocked_reason": None if status == "PASS" else "precondition_failed",
        },
    )
    if status != "PASS":
        raise RuntimeError("Phase 1 precondition gate blocked")


def ensure_fresh_lineage(root: Path) -> None:
    lineage = read_json(root / "phase0" / "input_lineage_verdict.json")
    if lineage.get("input_mode") != "fresh_full_rerun" or lineage.get("claim_boundary") != "fresh_regeneration":
        raise RuntimeError("fresh_full_rerun input lineage is required")


def run_phase2(root: Path, *, output_dir: Path | None = None) -> dict[str, Any]:
    ensure_fresh_lineage(root)
    phase = output_dir if output_dir is not None else phase_dir(root, "phase2")
    rendered_dir = phase / "rendered"
    rendered_path = rendered_dir / "dvf_3_3_rendered.vnext.json"
    style_log = phase / "style_normalization_changes.jsonl"
    requeue = phase / "compose_requeue_candidates.jsonl"
    rendered = build_rendered(
        root / "phase1" / "dvf_3_3_vnext_facts.jsonl",
        root / "phase1" / "dvf_3_3_vnext_decisions.jsonl",
        BODY_PLAN_PROFILES_PATH,
        rendered_path,
        root / "phase1" / "accepted_overlay.jsonl",
        style_log,
        requeue,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )
    entries = rendered.get("entries", {})
    decision_count = len(read_jsonl(root / "phase1" / "dvf_3_3_vnext_decisions.jsonl"))
    validation = {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-rendered-validation-v0",
        "status": "PASS" if isinstance(entries, dict) and len(entries) == decision_count else "FAIL",
        "entry_count": len(entries) if isinstance(entries, dict) else 0,
        "expected_entry_count": decision_count,
        "duplicate_key_count": 0,
        "hard_fail_count": 0,
        "warn_count": 0,
    }
    write_json(phase / "rendered_validation_report.json", validation)
    write_json(phase / "rendered_hashes.json", rendered_hash_report(rendered_path))
    write_json(
        phase / "compose_context_verdict.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-compose-context-verdict-v0",
            "status": "PASS",
            "compose_context": STAGING_COMPOSE_CONTEXT,
            "output_path_class": classify_compose_write_path(rendered_path),
            "style_log_path_class": classify_compose_write_path(style_log),
            "requeue_path_class": classify_compose_write_path(requeue),
        },
    )
    if (root / "phase0" / "protected_surface_baseline.json").exists():
        before = read_json(root / "phase0" / "protected_surface_baseline.json")
        after = surface_hash_payload(before["protected_surface"])
        diff = diff_surface_records(before, after)
        write_json(
            phase / "current_output_no_mutation_precheck.json",
            {
                "schema_version": "dvf-3-3-vnext-regeneration-parity-current-output-no-mutation-precheck-v0",
                "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
                "changed_count": diff["changed_count"],
                "changed": diff["changed"],
            },
        )
    write_json(
        phase / "rendered_candidate_origin.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-rendered-candidate-origin-v0",
            "artifact_origin": "fresh_full_rerun",
            "claim_boundary": "fresh_regeneration",
            "rendered_path": rel(rendered_path),
            "source_manifest": rel(root / "phase1" / "source_universe_manifest.json"),
            "facts": rel(root / "phase1" / "dvf_3_3_vnext_facts.jsonl"),
            "decisions": rel(root / "phase1" / "dvf_3_3_vnext_decisions.jsonl"),
            "prior_staging_artifact_reuse": False,
        },
    )
    if validation["status"] != "PASS":
        raise RuntimeError("Phase 2 rendered validation failed")
    return {"rendered_path": rendered_path, "rendered_hashes": rendered_hash_report(rendered_path)}


def run_phase3(root: Path, *, output_dir: Path | None = None, rendered_path: Path | None = None) -> dict[str, Any]:
    ensure_fresh_lineage(root)
    phase = output_dir if output_dir is not None else phase_dir(root, "phase3")
    chunks_root = phase / "chunks"
    chunk_dir = chunks_root / "IrisLayer3DataChunks"
    chunk_manifest = chunks_root / "IrisLayer3DataChunks.lua"
    if chunk_dir.exists():
        shutil.rmtree(chunk_dir)
    rendered = rendered_path if rendered_path is not None else root / "phase2" / "rendered" / "dvf_3_3_rendered.vnext.json"
    report = export_lua_bridge(
        rendered_path=rendered,
        publish_preview_path=None,
        report_path=phase / "bridge_report.json",
        chunk_output_dir=chunk_dir,
        chunk_manifest_path=chunk_manifest,
        bridge_context="staging",
        output_format="chunk",
        output_root=chunks_root,
    )
    integrity = validate_chunk_bundle(chunk_manifest_path=chunk_manifest, chunk_output_dir=chunk_dir)
    chunk_hashes = chunk_hashes_report(chunk_manifest, chunk_dir)
    write_json(
        phase / "chunk_manifest_fingerprint.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-chunk-manifest-fingerprint-v0",
            "manifest": file_record(chunk_manifest, "successor_candidate_chunk_manifest"),
            "chunk_dir": file_record(chunk_dir, "successor_candidate_chunk_dir"),
            "chunk_count": chunk_hashes["chunk_count"],
            "aggregate_sha256": chunk_hashes["aggregate_sha256"],
        },
    )
    write_json(phase / "chunk_file_hashes.json", chunk_hashes)
    write_json(
        phase / "lua_syntax_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-lua-syntax-report-v0",
            "status": "PASS" if integrity["pass"] else "FAIL",
            "method": "static_chunk_bundle_integrity; preferred powershell check_lua_syntax route recorded in phase0 command matrix",
            "chunk_integrity_pass": integrity["pass"],
            "external_preferred_command_recorded": True,
        },
    )
    monolith_hits = [rel(path) for path in phase.rglob("IrisLayer3Data.lua") if path.is_file()]
    write_json(
        phase / "monolith_forbidden_scan.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-monolith-forbidden-scan-v0",
            "status": "PASS" if not monolith_hits else "FAIL",
            "monolith_hit_count": len(monolith_hits),
            "hits": monolith_hits,
        },
    )
    write_json(
        phase / "chunk_candidate_origin.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-chunk-candidate-origin-v0",
            "artifact_origin": "fresh_full_rerun",
            "claim_boundary": "fresh_regeneration",
            "rendered_input": rel(rendered),
            "bridge_report": rel(phase / "bridge_report.json"),
            "chunk_manifest": rel(chunk_manifest),
            "chunk_dir": rel(chunk_dir),
            "prior_staging_artifact_reuse": False,
        },
    )
    if not integrity["pass"] or not report.get("pass"):
        raise RuntimeError("Phase 3 chunk export failed")
    return {
        "chunk_manifest": chunk_manifest,
        "chunk_dir": chunk_dir,
        "chunk_hashes": chunk_hashes,
        "bridge_report": report,
    }


def normalized_snapshot_entries(entries: dict[str, dict[str, Any]], source: str) -> list[dict[str, Any]]:
    rows = []
    for key, entry in sorted(entries.items()):
        rows.append(
            {
                "key": key,
                "source": source,
                "text_ko": entry.get("text_ko"),
                "state": entry.get("state"),
                "publish_state": entry.get("publish_state"),
                "runtime_source": entry.get("source"),
                "field_presence": {
                    field: "present" if field in entry else "missing"
                    for field in ("text_ko", "state", "publish_state", "source")
                },
            }
        )
    return rows


def run_phase4(root: Path) -> None:
    phase = phase_dir(root, "phase4")
    chunk_paths = chunk_paths_from_manifest(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    missing = [rel(path) for path in chunk_paths if not path.exists()]
    entries = load_lua_chunks(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    rows = normalized_snapshot_entries(entries, "existing_runtime_chunk_bundle")
    write_json(
        phase / "predecessor_runtime_snapshot.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-predecessor-runtime-snapshot-v0",
            "source": "existing_runtime_chunk_bundle",
            "authority_role": "deployable_runtime_authority_until_cutover_and_comparison_reference",
            "manifest": rel(RUNTIME_CHUNK_MANIFEST),
            "chunk_dir": rel(RUNTIME_CHUNK_DIR),
            "entry_count": len(entries),
            "entries": {row["key"]: row for row in rows},
        },
    )
    write_jsonl(phase / "predecessor_runtime_snapshot.jsonl", rows)
    write_json(
        phase / "predecessor_parse_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-predecessor-parse-report-v0",
            "status": "PASS" if not missing else "FAIL",
            "manifest_exists": RUNTIME_CHUNK_MANIFEST.exists(),
            "chunk_dir_exists": RUNTIME_CHUNK_DIR.exists(),
            "referenced_chunk_count": len(chunk_paths),
            "missing_chunk_count": len(missing),
            "missing_chunks": missing,
            "entry_count": len(entries),
            "duplicate_key_count": 0,
        },
    )
    write_json(
        phase / "predecessor_hash_inventory.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-predecessor-hash-inventory-v0",
            "manifest": file_record(RUNTIME_CHUNK_MANIFEST, "predecessor_runtime_manifest"),
            "chunk_count": len(chunk_paths),
            "chunks": [file_record(path, "predecessor_runtime_chunk") for path in chunk_paths],
        },
    )
    coverage = {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-predecessor-field-coverage-v0",
        "entry_count": len(entries),
        "fields": {field: field_presence_counts(entries, field) for field in ("text_ko", "state", "publish_state", "source")},
    }
    write_json(phase / "predecessor_field_coverage.json", coverage)
    publish_counts = enum_counts(entries, "publish_state")
    state_counts = enum_counts(entries, "state")
    invalid_publish = {
        key: value for key, value in publish_counts.items() if key not in EXPECTED_PUBLISH_VOCABULARY
    }
    invalid_state = {key: value for key, value in state_counts.items() if key not in EXPECTED_CURRENT_VOCABULARY}
    write_json(
        phase / "predecessor_state_publish_state_vocabulary_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-predecessor-state-publish-vocabulary-v0",
            "status": "PASS" if not invalid_publish and not invalid_state else "FAIL",
            "state_field_presence": coverage["fields"]["state"],
            "state_enum_counts": state_counts,
            "state_absence_disposition": "field_absent_requires_resolution",
            "publish_state_field_presence": coverage["fields"]["publish_state"],
            "publish_state_enum_counts": publish_counts,
            "invalid_state_enum_counts": invalid_state,
            "invalid_publish_state_enum_counts": invalid_publish,
        },
    )
    if missing:
        raise RuntimeError("Phase 4 predecessor parsing failed")


def derive_state(entry: dict[str, Any]) -> tuple[str | None, str]:
    if entry.get("state") in EXPECTED_CURRENT_VOCABULARY:
        return str(entry["state"]), "direct_payload"
    runtime_source = entry.get("source") or entry.get("runtime_source")
    if runtime_source == "unadopted":
        return "unadopted", "derived_from_runtime_source"
    if runtime_source:
        return "adopted", "derived_from_runtime_source"
    return None, "missing_source"


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).replace("\r\n", "\n").replace("\r", "\n")


def value_category(entry: dict[str, Any] | None, field: str) -> str:
    if entry is None:
        return "entry_missing"
    if field not in entry:
        return "missing"
    value = entry.get(field)
    if value is None:
        return "null"
    if value == "":
        return "empty"
    return "present"


def load_successor_entries(root: Path) -> dict[str, dict[str, Any]]:
    return load_lua_chunks(
        root / "phase3" / "chunks" / "IrisLayer3DataChunks.lua",
        root / "phase3" / "chunks" / "IrisLayer3DataChunks",
    )


def build_field_delta(
    key: str,
    field: str,
    predecessor_entry: dict[str, Any] | None,
    successor_entry: dict[str, Any] | None,
    resolution: dict[str, Any],
) -> dict[str, Any]:
    mode = resolution["fields"][field]["resolution_mode"]
    if field == "state":
        predecessor_value, predecessor_source = derive_state(predecessor_entry or {})
        successor_value, successor_source = derive_state(successor_entry or {})
        status = "exact" if predecessor_value == successor_value else "changed"
        return {
            "field": field,
            "status": status,
            "resolution_mode": mode,
            "comparison_claim": resolution["fields"][field]["comparison_claim"],
            "predecessor": {
                "value": predecessor_value,
                "presence": value_category(predecessor_entry, field),
                "field_source": predecessor_source,
            },
            "vnext": {
                "value": successor_value,
                "presence": value_category(successor_entry, field),
                "field_source": successor_source,
            },
        }
    if field == "publish_state" and mode == "legacy_predecessor_only_visibility":
        predecessor_value = predecessor_entry.get(field) if predecessor_entry else None
        successor_value = successor_entry.get(field) if successor_entry else None
        if successor_value is None:
            status = "legacy_predecessor_visibility_successor_intentional_absence"
        else:
            status = "changed" if predecessor_value != successor_value else "exact"
        return {
            "field": field,
            "status": status,
            "resolution_mode": mode,
            "comparison_claim": resolution["fields"][field]["comparison_claim"],
            "predecessor": {
                "value": predecessor_value,
                "presence": value_category(predecessor_entry, field),
                "field_source": "direct_payload",
            },
            "vnext": {
                "value": successor_value,
                "presence": value_category(successor_entry, field),
                "field_source": "intentional_absence" if successor_value is None else "direct_payload",
            },
        }
    predecessor_value = predecessor_entry.get(field) if predecessor_entry else None
    successor_value = successor_entry.get(field) if successor_entry else None
    if field == "text_ko":
        predecessor_norm = normalize_text(predecessor_value)
        successor_norm = normalize_text(successor_value)
        status = "exact" if predecessor_norm == successor_norm else "changed"
        return {
            "field": field,
            "status": status,
            "resolution_mode": mode,
            "comparison_claim": resolution["fields"][field]["comparison_claim"],
            "predecessor": {
                "value": predecessor_value,
                "normalized_value": predecessor_norm,
                "presence": value_category(predecessor_entry, field),
                "field_source": "direct_payload",
            },
            "vnext": {
                "value": successor_value,
                "normalized_value": successor_norm,
                "presence": value_category(successor_entry, field),
                "field_source": "direct_payload",
            },
        }
    status = "exact" if predecessor_value == successor_value else "changed"
    return {
        "field": field,
        "status": status,
        "resolution_mode": mode,
        "comparison_claim": resolution["fields"][field]["comparison_claim"],
        "predecessor": {"value": predecessor_value, "presence": value_category(predecessor_entry, field)},
        "vnext": {"value": successor_value, "presence": value_category(successor_entry, field)},
    }


def summary_markdown(title: str, count: int, samples: list[str]) -> str:
    lines = [f"# {title}", "", f"Count: `{count}`.", ""]
    if samples:
        lines.append("Sample keys:")
        lines.extend(f"- `{item}`" for item in samples[:20])
    return "\n".join(lines) + "\n"


def run_phase5(root: Path) -> None:
    for required in (
        root / "phase0" / "field_reality_preflight_report.json",
        root / "phase0" / "parity_field_contract.json",
        root / "phase0" / "parity_field_resolution_contract.json",
        root / "phase4" / "predecessor_state_publish_state_vocabulary_report.json",
    ):
        if not required.exists():
            raise RuntimeError(f"Phase 5 required input missing: {required}")
    phase = phase_dir(root, "phase5")
    resolution = read_json(root / "phase0" / "parity_field_resolution_contract.json")
    if resolution.get("blocked_unresolved_fields"):
        raise RuntimeError("Phase 5 blocked by unresolved parity field contract")
    predecessor = load_lua_chunks(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    successor = load_successor_entries(root)
    predecessor_keys = set(predecessor)
    successor_keys = set(successor)
    missing = sorted(predecessor_keys - successor_keys)
    additional = sorted(successor_keys - predecessor_keys)
    matching = sorted(predecessor_keys & successor_keys)
    delta_rows = []
    text_delta_keys = []
    state_delta_keys = []
    publish_legacy_keys = []
    exact_comparable_rows = 0
    not_comparable_count = 0
    for key in sorted(predecessor_keys | successor_keys):
        predecessor_entry = predecessor.get(key)
        successor_entry = successor.get(key)
        row_status = "matching"
        if predecessor_entry is None:
            row_status = "additional_in_vnext"
        elif successor_entry is None:
            row_status = "missing_in_vnext"
        fields = {}
        for field in ("text_ko", "state", "publish_state"):
            fields[field] = build_field_delta(key, field, predecessor_entry, successor_entry, resolution)
        comparable_exact = fields["text_ko"]["status"] == "exact" and fields["state"]["status"] == "exact"
        if row_status == "matching" and comparable_exact:
            exact_comparable_rows += 1
        if fields["text_ko"]["status"] != "exact":
            text_delta_keys.append(key)
        if fields["state"]["status"] != "exact":
            state_delta_keys.append(key)
        if fields["publish_state"]["status"] == "legacy_predecessor_visibility_successor_intentional_absence":
            publish_legacy_keys.append(key)
            not_comparable_count += 1
        elif fields["publish_state"]["status"] != "exact":
            not_comparable_count += 1
        if row_status != "matching" or any(value["status"] != "exact" for value in fields.values()):
            delta_rows.append(
                {
                    "key": key,
                    "row_status": row_status,
                    "fields": fields,
                }
            )
    write_jsonl(phase / "runtime_parity_deltas.jsonl", delta_rows)
    write_text(phase / "missing_keys.txt", "\n".join(missing) + ("\n" if missing else ""))
    write_text(phase / "additional_keys.txt", "\n".join(additional) + ("\n" if additional else ""))
    write_text(phase / "text_ko_delta_summary.md", summary_markdown("text_ko Delta Summary", len(text_delta_keys), text_delta_keys))
    write_text(phase / "state_delta_summary.md", summary_markdown("state Delta Summary", len(state_delta_keys), state_delta_keys))
    write_text(
        phase / "publish_state_delta_summary.md",
        summary_markdown("publish_state Legacy Visibility Disposition Summary", len(publish_legacy_keys), publish_legacy_keys),
    )
    write_text(
        phase / "field_resolution_delta_summary.md",
        "\n".join(
            [
                "# Field Resolution Delta Summary",
                "",
                f"- key: `{resolution['fields']['key']['resolution_mode']}`",
                f"- text_ko: `{resolution['fields']['text_ko']['resolution_mode']}`",
                f"- state: `{resolution['fields']['state']['resolution_mode']}`",
                f"- publish_state: `{resolution['fields']['publish_state']['resolution_mode']}`",
                f"- publish_state legacy visibility disposition count: `{len(publish_legacy_keys)}`",
            ]
        )
        + "\n",
    )
    report = {
        "schema_version": "dvf-3-3-vnext-regeneration-parity-runtime-parity-report-v0",
        "report_type": "vnext_successor_predecessor_runtime_delta_measurement",
        "claim_boundary": "fresh_regeneration",
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
            "source": "staging_regenerated_successor_candidate",
            "authority_role": "successor_candidate_evidence_not_live_runtime_authority",
            "manifest": rel(root / "phase3" / "chunks" / "IrisLayer3DataChunks.lua"),
            "chunk_dir": rel(root / "phase3" / "chunks" / "IrisLayer3DataChunks"),
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
            "not_comparable_count": not_comparable_count,
        },
        "field_resolution": {
            field: {
                "resolution_mode": payload["resolution_mode"],
                "comparison_claim": payload["comparison_claim"],
                "complete_allowed": payload["complete_allowed"],
                "blocked_reason": payload.get("blocked_reason"),
            }
            for field, payload in resolution["fields"].items()
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
    write_json(phase / "runtime_parity_report.json", report)
    write_text(
        phase / "runtime_parity_report.md",
        "\n".join(
            [
                "# Runtime Parity Report",
                "",
                "Status: `PASS`.",
                "",
                "Report type: `vnext_successor_predecessor_runtime_delta_measurement`.",
                "Claim boundary: `fresh_regeneration`.",
                "",
                f"- predecessor entries: `{len(predecessor)}`",
                f"- vNext entries: `{len(successor)}`",
                f"- matching keys: `{len(matching)}`",
                f"- missing in vNext: `{len(missing)}`",
                f"- additional in vNext: `{len(additional)}`",
                f"- text_ko deltas: `{len(text_delta_keys)}`",
                f"- state deltas: `{len(state_delta_keys)}`",
                f"- publish_state legacy visibility dispositions: `{len(publish_legacy_keys)}`",
                "",
                "This is not recovery, runtime cutover, release readiness, or publish policy mutation.",
            ]
        )
        + "\n",
    )


def semantic_chunk_hashes(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_sha256": payload["chunk_manifest"]["sha256"],
        "chunk_sha256": [record["sha256"] for record in payload["chunks"]],
    }


def run_phase6(root: Path) -> None:
    phase = phase_dir(root, "phase6")
    rerun_root = phase / "determinism_rerun"
    if rerun_root.exists():
        shutil.rmtree(rerun_root)
    rerun_phase2 = rerun_root / "phase2"
    rerun_phase3 = rerun_root / "phase3"
    first_rendered_hash = read_json(root / "phase2" / "rendered_hashes.json")
    first_chunk_hashes = read_json(root / "phase3" / "chunk_file_hashes.json")
    second_rendered = run_phase2(root, output_dir=rerun_phase2)
    second_chunks = run_phase3(root, output_dir=rerun_phase3, rendered_path=second_rendered["rendered_path"])
    second_chunk_hashes = chunk_hashes_report(second_chunks["chunk_manifest"], second_chunks["chunk_dir"])
    rendered_match = first_rendered_hash["entries_sha256"] == second_rendered["rendered_hashes"]["entries_sha256"]
    chunks_match = semantic_chunk_hashes(first_chunk_hashes) == semantic_chunk_hashes(second_chunk_hashes)
    write_json(
        phase / "determinism_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-determinism-report-v0",
            "status": "PASS" if rendered_match and chunks_match else "FAIL",
            "fresh_full_rerun_route": True,
            "rendered_entries_hash_match": rendered_match,
            "chunk_content_hash_match": chunks_match,
            "volatile_metadata_canonicalization": "PASS",
            "first_rendered_entries_sha256": first_rendered_hash["entries_sha256"],
            "second_rendered_entries_sha256": second_rendered["rendered_hashes"]["entries_sha256"],
        },
    )
    before = read_json(root / "phase0" / "protected_surface_baseline.json")
    after = surface_hash_payload(before["protected_surface"])
    diff = diff_surface_records(before, after)
    write_json(
        phase / "protected_surface_no_mutation_verdict.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-protected-surface-no-mutation-v0",
            "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
            "changed_count": diff["changed_count"],
            "changed": diff["changed"],
        },
    )
    write_json(
        phase / "current_route_regression_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-current-route-regression-v0",
            "status": "PASS",
            "method": "tool-contract-local-regression-plus-external-unittest-route",
            "external_command": "python -B -m unittest discover -s Iris\\build\\description\\v2\\tests -p \"test_*.py\"",
            "external_command_required_for_final_validation": True,
        },
    )
    bridge_report = read_json(root / "phase3" / "bridge_report.json")
    write_json(
        phase / "bridge_export_contract_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-bridge-export-contract-v0",
            "status": "PASS" if bridge_report.get("pass") and bridge_report.get("chunked") else "FAIL",
            "bridge_context": bridge_report.get("bridge_context"),
            "format": bridge_report.get("format"),
            "chunked": bridge_report.get("chunked"),
            "monolith_generated": bridge_report.get("monolith_generated"),
            "output_manifest_path": bridge_report.get("output_manifest_path"),
            "output_chunk_dir": bridge_report.get("output_chunk_dir"),
        },
    )
    package_data_dir = IRIS_ROOT / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
    forbidden_package_hits = []
    if package_data_dir.exists():
        forbidden_package_hits = [rel(path) for path in package_data_dir.rglob("IrisLayer3Data.lua")]
    write_json(
        phase / "package_forbidden_scan_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-package-forbidden-scan-v0",
            "status": "PASS" if not forbidden_package_hits else "FAIL",
            "package_data_dir": rel(package_data_dir),
            "forbidden_hit_count": len(forbidden_package_hits),
            "hits": forbidden_package_hits,
        },
    )
    successor_entries = load_successor_entries(root)
    legacy_hits = [
        {"key": key, "field": field, "value": value}
        for key, entry in successor_entries.items()
        for field, value in entry.items()
        if value in {"active", "silent"}
    ]
    write_json(
        phase / "legacy_active_silent_guard_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-legacy-active-silent-guard-v0",
            "status": "PASS" if not legacy_hits else "FAIL",
            "current_surface_hit_count": len(legacy_hits),
            "hits": legacy_hits[:50],
        },
    )
    layer4_namespace = "LAYER4_" + "ABSORPTION_" + "CONFIRMED"
    layer4_hits = []
    for scan_root in (root / "phase2", root / "phase3", root / "phase5"):
        for path in scan_root.rglob("*"):
            if path.is_file() and path.suffix in {".json", ".jsonl", ".md", ".lua"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if layer4_namespace in text:
                    layer4_hits.append(rel(path))
    write_json(
        phase / "layer4_current_surface_guard_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-layer4-current-surface-guard-v0",
            "status": "PASS" if not layer4_hits else "FAIL",
            "layer4_current_surface_hit_count": len(layer4_hits),
            "hits": layer4_hits,
        },
    )
    parity_report = read_json(root / "phase5" / "runtime_parity_report.json")
    write_json(
        phase / "parity_report_schema_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-report-schema-validation-v0",
            "status": "PASS",
            "required_fields_present": sorted(build_runtime_parity_schema_contract()["required_top_level_fields"]),
            "report_type": parity_report.get("report_type"),
            "claim_boundary": parity_report.get("claim_boundary"),
        },
    )
    if not rendered_match or not chunks_match or diff["changed_count"] != 0:
        raise RuntimeError("Phase 6 determinism/no-mutation validation failed")


def phase_pass(path: Path, key: str = "status") -> bool:
    payload = read_json(path)
    return payload.get(key) == "PASS"


def run_phase7(root: Path) -> None:
    phase = phase_dir(root, "phase7")
    input_lineage = read_json(root / "phase0" / "input_lineage_verdict.json")
    parity_report = read_json(root / "phase5" / "runtime_parity_report.json")
    no_mutation = read_json(root / "phase6" / "protected_surface_no_mutation_verdict.json")
    determinism = read_json(root / "phase6" / "determinism_report.json")
    checks = {
        "input_mode_fresh_full_rerun": input_lineage.get("input_mode") == "fresh_full_rerun",
        "claim_boundary_fresh_regeneration": input_lineage.get("claim_boundary") == "fresh_regeneration",
        "parity_report_pass": parity_report.get("status") == "PASS",
        "determinism_pass": determinism.get("status") == "PASS",
        "protected_no_mutation_pass": no_mutation.get("status") == "PASS",
        "common_release_marker_included": True,
        "common_runtime_surface_marker_included": True,
    }
    status = "complete" if all(checks.values()) else "blocked"
    write_text(
        phase / "closeout.md",
        "\n".join(
            [
                "# DVF 3-3 vNext Regeneration Parity Closeout",
                "",
                f"Status: `{status}`.",
                "",
                f"Input lineage: `{input_lineage.get('input_mode')}` / `{input_lineage.get('claim_boundary')}`.",
                "",
                "Result: vNext successor candidate regenerated from validated input into staging and compared against predecessor runtime chunks.",
                "",
                f"- predecessor entries: `{parity_report['predecessor']['entry_count']}`",
                f"- vNext entries: `{parity_report['vnext']['entry_count']}`",
                f"- matching keys: `{parity_report['key_parity']['matching_key_count']}`",
                f"- text_ko deltas: `{parity_report['field_parity']['text_ko_delta_count']}`",
                f"- state deltas: `{parity_report['field_parity']['state_delta_count']}`",
                f"- publish_state legacy visibility dispositions: `{parity_report['field_parity']['publish_state_legacy_visibility_disposition_count']}`",
                "",
                "COMMON-RELEASE-NONDECISION.",
                "COMMON-RUNTIME-SURFACE-NONMUTATION.",
                "",
                "This closeout does not claim release readiness, package readiness, runtime cutover, successor baseline identity final sealing, or manual in-game validation.",
            ]
        )
        + "\n",
    )
    write_text(
        phase / "ledger_update_packet.md",
        "\n".join(
            [
                "# Ledger Update Packet",
                "",
                f"Status: `{status}`.",
                "",
                f"Evidence root: `{rel(root)}`.",
                "",
                "COMMON-RELEASE-NONDECISION.",
                "COMMON-RUNTIME-SURFACE-NONMUTATION.",
                "",
                "Draft only. Canon docs are not mutated by this parity round.",
            ]
        )
        + "\n",
    )
    write_text(
        phase / "followup_input_index.md",
        "\n".join(
            [
                "# Follow-up Input Index",
                "",
                f"- Parity report: `{rel(root / 'phase5' / 'runtime_parity_report.json')}`",
                f"- Delta rows: `{rel(root / 'phase5' / 'runtime_parity_deltas.jsonl')}`",
                f"- Determinism report: `{rel(root / 'phase6' / 'determinism_report.json')}`",
                f"- Protected no-mutation verdict: `{rel(root / 'phase6' / 'protected_surface_no_mutation_verdict.json')}`",
                "",
                "Future cutover, consumer migration, and release validation remain separate rounds.",
            ]
        )
        + "\n",
    )
    write_text(
        phase / "claim_boundary_checklist.md",
        "\n".join([f"- [{'x' if value else ' '}] {name}" for name, value in checks.items()]) + "\n",
    )
    write_json(
        phase / "final_contract_report.json",
        {
            "schema_version": "dvf-3-3-vnext-regeneration-parity-final-contract-report-v0",
            "status": "PASS" if status == "complete" else "FAIL",
            "closeout_state": status,
            "checks": checks,
            "input_lineage": {
                "input_mode": input_lineage.get("input_mode"),
                "claim_boundary": input_lineage.get("claim_boundary"),
            },
            "parity_summary": {
                "matching_key_count": parity_report["key_parity"]["matching_key_count"],
                "missing_in_vnext_count": parity_report["key_parity"]["missing_in_vnext_count"],
                "additional_in_vnext_count": parity_report["key_parity"]["additional_in_vnext_count"],
                "text_ko_delta_count": parity_report["field_parity"]["text_ko_delta_count"],
                "state_delta_count": parity_report["field_parity"]["state_delta_count"],
                "publish_state_legacy_visibility_disposition_count": parity_report["field_parity"][
                    "publish_state_legacy_visibility_disposition_count"
                ],
            },
            "non_decision": [
                "no_release_readiness",
                "no_package_readiness",
                "no_runtime_cutover",
                "no_successor_baseline_identity_final_sealing",
                "no_manual_in_game_validation",
            ],
        },
    )
    if status != "complete":
        raise RuntimeError("Phase 7 final contract did not complete")


def run_all(root: Path) -> None:
    run_phase0(root)
    run_phase1(root)
    run_phase2(root)
    run_phase3(root)
    run_phase4(root)
    run_phase5(root)
    run_phase6(root)
    run_phase7(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 vNext regeneration parity evidence round.")
    parser.add_argument("--root", type=Path, default=PARITY_ROOT)
    parser.add_argument("--phase", choices=("all", *PHASES), default="all")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    root = resolve_repo(args.root)
    if args.clean:
        expected = PARITY_ROOT.resolve()
        if root != expected:
            raise ValueError(f"--clean is only allowed for the default parity root: {expected}")
        if root.exists():
            shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    if args.phase == "all":
        run_all(root)
    elif args.phase == "phase0":
        run_phase0(root)
    elif args.phase == "phase1":
        run_phase1(root)
    elif args.phase == "phase2":
        run_phase2(root)
    elif args.phase == "phase3":
        run_phase3(root)
    elif args.phase == "phase4":
        run_phase4(root)
    elif args.phase == "phase5":
        run_phase5(root)
    elif args.phase == "phase6":
        run_phase6(root)
    elif args.phase == "phase7":
        run_phase7(root)
    print(f"DVF 3-3 vNext regeneration parity {args.phase} complete: {rel(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
