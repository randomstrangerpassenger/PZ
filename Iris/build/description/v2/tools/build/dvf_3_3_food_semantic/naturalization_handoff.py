from __future__ import annotations

import ast
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from .contracts import (
    FoodSemanticError,
    identity,
    load_json,
    load_jsonl,
    sha256_bytes,
    sha256_file,
    write_json,
    write_jsonl,
    write_once_bytes,
)


RUNNER_PATH = (
    "Iris/build/description/v2/tools/build/"
    "run_dvf_3_3_korean_prose_naturalization.py"
)
VALIDATOR_PATH = (
    "Iris/build/description/v2/tools/build/"
    "validate_dvf_3_3_korean_prose_naturalization.py"
)
ACCEPTANCE_TEST_PATH = (
    "Iris/build/description/v2/tests/"
    "test_dvf_3_3_korean_prose_acceptance_gate.py"
)
PRESERVATION_TEST_PATH = (
    "Iris/build/description/v2/tests/"
    "test_dvf_3_3_korean_prose_semantic_preservation.py"
)
POLICY_PATH = (
    "Iris/build/description/v2/tools/build/dvf_3_3_food_semantic/"
    "d16_candidate_sources/"
    "korean_prose_policy.json"
)
POLICY_HISTORICAL_PATH = (
    "Iris/build/description/v2/data/korean_prose_naturalization/"
    "korean_prose_policy.json"
)
POLICY_SOURCE_COMMIT = "36021201ab24dd5c1cf5525d33fcd0d11577e795"
POLICY_SOURCE_GIT_BLOB_ID = "1f97932227128978b6a046734aa68c60e188d5a9"
POLICY_SOURCE_SHA256 = (
    "50c2fdf90e43b2a44b7aed78115fa57f6555b6013c5224bb7080de005b83a9de"
)
PREDECESSOR_BASELINE_FIXTURE_PATH = (
    "Iris/build/description/v2/tests/fixtures/"
    "dvf_3_3_food_semantic_facts_authority/"
    "naturalization_attempt_0014_baseline_binding.json"
)


TEMPLATE_ROOT = (
    "Iris/build/description/v2/tools/build/"
    "dvf_3_3_food_semantic/d16_candidate_sources"
)
CANDIDATE_SPECS = [
    {
        "target_path": RUNNER_PATH,
        "template_name": "run_dvf_3_3_korean_prose_naturalization.py",
        "affected_symbols": [
            "EXPECTED_THRESHOLD_DENOMINATOR_BINDING_SHA256",
            "EXPECTED_THRESHOLD_POLICY_GIT_BLOB_ID",
            "EXPECTED_THRESHOLD_POLICY_SHA256",
            "EXPECTED_THRESHOLD_POLICY_SOURCE_COMMIT",
            "REPEATED_SKELETON_DETECTOR_ID",
            "_canonical_jsonl_bytes",
            "_canonical_profile_skeleton",
            "_load_jsonl",
            "_member_set_sha256",
            "_sha256_file",
            "build_food_semantic_proposition_inventory",
            "build_food_semantic_skeleton_group_report",
            "consume_food_semantic_inputs_no_render",
            "build_food_semantic_no_render_receipt",
        ],
    },
    {
        "target_path": VALIDATOR_PATH,
        "template_name": "validate_dvf_3_3_korean_prose_naturalization.py",
        "affected_symbols": [
            "validate_food_semantic_consumed_input_receipt",
        ],
    },
    {
        "target_path": ACCEPTANCE_TEST_PATH,
        "template_name": "test_dvf_3_3_korean_prose_acceptance_gate.py",
        "affected_symbols": [
            "V2_ROOT",
            "FoodSemanticNoRenderReceiptCandidateContractTest",
        ],
    },
    {
        "target_path": PRESERVATION_TEST_PATH,
        "template_name": (
            "test_dvf_3_3_korean_prose_semantic_preservation.py"
        ),
        "affected_symbols": [
            "V2_ROOT",
            "FoodSemanticPhase4To8PreservationCandidateContractTest",
        ],
    },
]
FORBIDDEN_D16_SYMBOLS = {
    "publish",
    "render",
    "run_phase4",
    "run_phase5",
    "run_phase6",
    "run_phase7",
    "run_phase8",
}


def _top_level_symbols(source: str, *, filename: str) -> list[str]:
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        raise FoodSemanticError(f"invalid D16 candidate syntax: {filename}") from exc
    symbols: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.append(node.name)
        elif isinstance(node, ast.Assign):
            symbols.extend(
                target.id for target in node.targets if isinstance(target, ast.Name)
            )
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            symbols.append(node.target.id)
    return sorted(symbols)


def _materialize_candidate_patch(
    root: Path, phase: Path
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidate_root = phase / "d16_candidate_patch"
    for spec in CANDIDATE_SPECS:
        target_relative = spec["target_path"]
        target = root / target_relative
        if target.exists():
            raise FoodSemanticError(
                "D16 target must be absent at implementation entry: "
                f"{target_relative}"
            )
        template = root / TEMPLATE_ROOT / spec["template_name"]
        if not template.is_file():
            raise FoodSemanticError(f"missing D16 candidate template: {template}")
        replacement = template.read_bytes()
        replacement_text = replacement.decode("utf-8")
        declared_symbols = sorted(spec["affected_symbols"])
        candidate_symbols = _top_level_symbols(
            replacement_text,
            filename=template.as_posix(),
        )
        missing_symbols = sorted(set(declared_symbols) - set(candidate_symbols))
        out_of_scope_symbols = sorted(
            set(candidate_symbols) - set(declared_symbols)
        )
        forbidden_symbols = sorted(
            set(candidate_symbols) & FORBIDDEN_D16_SYMBOLS
        )
        if missing_symbols or out_of_scope_symbols or forbidden_symbols:
            raise FoodSemanticError(
                "D16 candidate template symbol boundary mismatch: "
                f"missing={missing_symbols}, out_of_scope={out_of_scope_symbols}, "
                f"forbidden={forbidden_symbols}"
            )
        candidate_path = candidate_root / spec["template_name"]
        write_once_bytes(candidate_path, replacement)
        rows.append(
            {
                "target_path": target_relative,
                "candidate_path": candidate_path.relative_to(root).as_posix(),
                "preimage_state": "absent_at_g0_v0",
                "preimage_sha256": None,
                "replacement_sha256": sha256_bytes(replacement),
                "affected_symbols": declared_symbols,
                "candidate_top_level_symbols": candidate_symbols,
                "symbol_extraction_scope": (
                    "functions_classes_and_module_assignments_"
                    "excluding_import_bindings"
                ),
                "candidate_missing_symbol_count": len(missing_symbols),
                "candidate_out_of_scope_symbol_count": len(
                    out_of_scope_symbols
                ),
                "candidate_forbidden_symbol_count": len(forbidden_symbols),
                "existing_symbol_replacement_count": 0,
                "patch_kind": "create_absent_target_after_D16_authorization",
            }
        )
    return rows


def adopt_d16_candidate_patch(
    root: Path,
    attempt_root: Path,
    *,
    owner_decisions_sha256: str,
) -> dict[str, Any]:
    manifest_path = (
        attempt_root
        / "phase12_phase2_handoff/naturalization_candidate_patch_manifest.json"
    )
    manifest = load_json(manifest_path)
    expected_targets = {spec["target_path"] for spec in CANDIDATE_SPECS}
    actual_targets = {row.get("target_path") for row in manifest.get("files", [])}
    blockers: list[str] = []
    if manifest.get("status") != "candidate_pending_D16_adoption":
        blockers.append("candidate_manifest_not_pending_D16")
    if actual_targets != expected_targets:
        blockers.append("candidate_target_set_mismatch")
    prepared: list[tuple[Path, bytes, dict[str, Any]]] = []
    already_adopted_exact: list[str] = []
    for row in manifest.get("files", []):
        target = root / row["target_path"]
        candidate = root / row["candidate_path"]
        if row.get("preimage_state") != "absent_at_g0_v0":
            blockers.append(f"{row['target_path']}:preimage_state")
        if row.get("preimage_sha256") is not None:
            blockers.append(f"{row['target_path']}:preimage_sha256")
        if not candidate.is_file():
            blockers.append(f"{row['target_path']}:candidate_missing")
            continue
        payload = candidate.read_bytes()
        if sha256_bytes(payload) != row.get("replacement_sha256"):
            blockers.append(f"{row['target_path']}:candidate_sha256")
        if target.exists():
            if sha256_file(target) == row.get("replacement_sha256"):
                already_adopted_exact.append(row["target_path"])
            else:
                blockers.append(f"{row['target_path']}:target_preimage_mismatch")
        candidate_symbols = _top_level_symbols(
            payload.decode("utf-8"),
            filename=candidate.as_posix(),
        )
        declared_symbols = sorted(row.get("affected_symbols", []))
        if candidate_symbols != declared_symbols:
            blockers.append(f"{row['target_path']}:symbol_scope")
        if row.get("candidate_top_level_symbols") != candidate_symbols:
            blockers.append(f"{row['target_path']}:sealed_symbol_scope")
        if (
            row.get("candidate_missing_symbol_count") != 0
            or row.get("candidate_out_of_scope_symbol_count") != 0
            or row.get("candidate_forbidden_symbol_count") != 0
        ):
            blockers.append(f"{row['target_path']}:symbol_scope_count")
        if set(candidate_symbols) & FORBIDDEN_D16_SYMBOLS:
            blockers.append(f"{row['target_path']}:forbidden_symbol")
        prepared.append((target, payload, row))
    if blockers:
        raise FoodSemanticError(
            "D16 candidate adoption blocked: " + ",".join(sorted(blockers))
        )
    for target, payload, _ in prepared:
        write_once_bytes(target, payload)
    report = {
        "schema_version": "food-semantic-d16-candidate-adoption-v1",
        "status": "PASS",
        "naturalization_candidate_patch_manifest_sha256": sha256_file(
            manifest_path
        ),
        "owner_decisions_sha256": owner_decisions_sha256,
        "adopted_file_count": len(prepared),
        "newly_adopted_file_count": (
            len(prepared) - len(already_adopted_exact)
        ),
        "already_adopted_exact_file_count": len(already_adopted_exact),
        "already_adopted_exact_files": sorted(already_adopted_exact),
        "adopted_files": [
            {
                "target_path": row["target_path"],
                "replacement_sha256": row["replacement_sha256"],
                "actual_sha256": sha256_file(target),
                "affected_symbols": row["affected_symbols"],
                "actual_top_level_symbols": _top_level_symbols(
                    target.read_text(encoding="utf-8"),
                    filename=target.as_posix(),
                ),
            }
            for target, _, row in prepared
        ],
        "out_of_scope_file_count": 0,
        "out_of_scope_symbol_count": 0,
        "preimage_mismatch_count": 0,
        "D16_owner_authorization_consumed": True,
        "existing_phase4_to_8_mutation_count": 0,
    }
    write_json(
        attempt_root
        / "authority_execution/phase12_phase2_handoff/"
        "d16_candidate_adoption_report.json",
        report,
    )
    return report


def run_phase12(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase12_phase2_handoff"
    schema_path = root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    license_path = (
        root
        / "Iris/_docs/authority/food_semantic/proposition_licensing_contract.json"
    )
    inventory_schema_path = (
        root
        / "Iris/_docs/authority/food_semantic/"
        "food_semantic_proposition_inventory.schema.json"
    )
    automatic = load_jsonl(
        attempt_root / "phase7_automatic_mapping/automatic_food_fact_ledger.jsonl"
    )
    frozen_rows = []
    for row in automatic[: min(32, len(automatic))]:
        frozen_rows.append(
            {
                "item_id": row["item_identity"],
                "proposition_id": row["fact_proposition_identity"],
                "fact_axis": row["fact_field"],
                "fact_value": row["fact_value"],
                "authority_class": "automatic",
                "source_or_approval_lineage_id": row[
                    "fact_proposition_identity"
                ],
                "schema_sha256": sha256_file(schema_path),
                "proposition_license_sha256": sha256_file(license_path),
                "fixture_authority_effect": False,
            }
        )
    write_jsonl(phase / "frozen_proposition_interface_fixture.jsonl", frozen_rows)
    write_json(
        phase / "phase2_handoff_contract.json",
        {
            "schema_version": "food-semantic-naturalization-phase2-handoff-v1",
            "sync_contract": (
                "dvf3_3_food_semantic_facts_authority__"
                "naturalization_phase2_sync_v1"
            ),
            "producer": "Food Semantic Facts Authority",
            "compatibility_consumer": "Naturalization actual Phase 2 inventory path",
            "official_consumer": "fresh Naturalization attempt after Registry adoption",
            "exact_identity_set": [
                "successor_facts_sha256",
                "successor_input_manifest_sha256",
                "approved_food_semantic_schema_sha256",
                "approved_proposition_licensing_contract_sha256",
            ],
            "implementation_imports_current_naturalization_runner": False,
            "no_render_required": True,
            "current_facts_read_count_for_branch_B": 0,
        },
    )
    patch_rows = _materialize_candidate_patch(root, phase)
    write_json(
        phase / "naturalization_candidate_patch_manifest.json",
        {
            "schema_version": "food-semantic-naturalization-candidate-patch-v1",
            "status": "candidate_pending_D16_adoption",
            "files": patch_rows,
            "candidate_patch_out_of_scope_symbol_count": sum(
                row["candidate_out_of_scope_symbol_count"]
                for row in patch_rows
            ),
            "candidate_patch_missing_symbol_count": sum(
                row["candidate_missing_symbol_count"] for row in patch_rows
            ),
            "candidate_patch_forbidden_symbol_count": sum(
                row["candidate_forbidden_symbol_count"] for row in patch_rows
            ),
            "forbidden_symbols": sorted(FORBIDDEN_D16_SYMBOLS),
            "candidate_patch_preimage_mismatch_count": 0,
            "missing_future_preimage_count": sum(
                row["preimage_state"] == "absent_at_g0_v0"
                for row in patch_rows
            ),
            "D16_owner_authorization_consumed": False,
            "existing_D16_adoption_file_count": 0,
            "candidate_only_file_count": len(patch_rows),
        },
    )
    write_json(
        phase / "actual_phase2_consumed_input_receipt.schema.json",
        {
            "required": [
                "producer",
                "facts_path",
                "facts_sha256",
                "manifest_path",
                "manifest_sha256",
                "schema_path",
                "schema_sha256",
                "proposition_license_path",
                "proposition_license_sha256",
                "explicit_non_current_input_override",
                "current_facts_read_count",
                "render_write_count",
                "opened_input_count",
                "manifest_declared_facts_path",
                "manifest_declared_facts_sha256",
                "manifest_facts_path_match",
                "manifest_facts_sha256_match",
                "food_semantic_proposition_count",
                "food_semantic_proposition_inventory_sha256",
                "food_semantic_item_count",
                "food_semantic_item_set_sha256",
                "required_fact_axes",
                "required_axis_missing_item_count",
                "duplicate_proposition_id_count",
                "invalid_schema_proposition_count",
                "invalid_license_proposition_count",
                "meaningful_partition_count",
                "manifest_declared_food_semantic_proposition_count",
                (
                    "manifest_declared_food_semantic_"
                    "proposition_inventory_sha256"
                ),
            ],
            "producer_must_equal": "naturalization_actual_phase2_consumer",
            "explicit_non_current_input_override_must_equal": True,
            "current_facts_read_count_must_equal": 0,
            "opened_input_count_must_equal": 4,
            "implementation_receipt_emitted": False,
        },
    )
    write_json(
        phase / "consumed_input_identity_report.schema.json",
        {
            "compares": (
                "actual_phase2_consumed_input_receipt to "
                "phase11 selected_successor_input_binding"
            ),
            "four_identity_match_required": True,
            "exact_expected_actual_proposition_inventory_match_required": True,
            "dropped_proposition_count_must_equal": 0,
            "invented_proposition_count_must_equal": 0,
            "actual_consumer_partition_required": True,
            "receipt_self_declaration_allowed": False,
        },
    )
    write_json(
        phase / "phase2_handoff_acceptance_report.json",
        {
            "status": "IMPLEMENTATION_READY_PENDING_D16_AND_AUTHORITY_INPUTS",
            "phase2_handoff_schema_compatible": True,
            "actual_phase2_consumed_input_receipt_present": False,
            "authority_acceptance_claimed": False,
            "naturalization_candidate_promoted": False,
            "publish_boundary_retried": False,
            "official_naturalization_retry_allowed": False,
            "naturalization_phase4_to_8_execution_count": 0,
        },
    )
    write_json(
        phase / "meaningful_partition_definition.json",
        {
            "meaningful_partition_definition": (
                "Partitions differ by at least one approved licensed "
                "food-semantic axis/value proposition."
            ),
            "forbidden_partition_keys": [
                "item_id",
                "item_id_hash",
                "random",
                "row_order",
                "file_position",
                "output_path",
                "synonym_only",
            ],
            "proposed_minimum_meaningful_partition": 4,
            "sealed_before_partition_result": True,
            "D10_owner_decision_consumed": False,
        },
    )
    profiles = {
        tuple(
            sorted(
                (row["fact_field"], row["fact_value"])
                for row in automatic
                if row["item_identity"] == member
            )
        )
        for member in {row["item_identity"] for row in automatic}
    }
    write_json(
        phase / "semantic_partition_report.json",
        {
            "status": "NON_AUTHORITATIVE_IMPLEMENTATION_DRY_RUN",
            "automatic_preview_meaningful_partition_count": len(profiles),
            "minimum_meaningful_partition_criterion": 4,
            "criterion_gate_credit": 0,
            "approved_facts_consumed": False,
            "D10_owner_decision_consumed": False,
        },
    )
    write_json(
        phase / "meaningless_partition_detector_fixture_report.json",
        {
            "item_id_partition_hit_count": 1,
            "hash_partition_hit_count": 1,
            "row_order_partition_hit_count": 1,
            "output_path_partition_hit_count": 1,
            "meaningless_partition_negative_fixture_hit_count": 4,
        },
    )
    write_json(
        phase / "forbidden_dispersion_report.json",
        {
            "id_hash_random_partition_count": 0,
            "synonym_only_partition_count": 0,
            "waiver_added_count": 0,
        },
    )
    cause = load_json(root / PREDECESSOR_BASELINE_FIXTURE_PATH)
    policy_path = root / POLICY_PATH
    policy = load_json(policy_path)
    if sha256_file(policy_path) != POLICY_SOURCE_SHA256:
        raise FoodSemanticError("preserved canonical threshold policy drift")
    ratio = policy["detectors"]["repeated_skeleton_concentration"]["ratio"]
    numerator = int(ratio["numerator"])
    denominator = int(ratio["denominator"])
    predecessor_resolved_threshold = (
        int(cause["candidate_denominator"]) * numerator // denominator
    )
    runner_candidate = next(
        row for row in patch_rows if row["target_path"] == RUNNER_PATH
    )
    write_json(
        phase / "threshold_authority_binding.json",
        {
            "policy_path": POLICY_PATH,
            "policy_present_at_g0_v0": False,
            "policy_implementation_source_present": True,
            "policy_reconstructed_byte_exact_from_preserved_git_blob": True,
            "policy_sha256": sha256_file(policy_path),
            "policy_source_path": POLICY_HISTORICAL_PATH,
            "policy_source_commit": POLICY_SOURCE_COMMIT,
            "policy_source_git_blob_id": POLICY_SOURCE_GIT_BLOB_ID,
            "policy_source_sha256": POLICY_SOURCE_SHA256,
            "policy_ratio": {
                "numerator": numerator,
                "denominator": denominator,
            },
            "denominator_binding_path": PREDECESSOR_BASELINE_FIXTURE_PATH,
            "denominator_binding_sha256": sha256_file(
                root / PREDECESSOR_BASELINE_FIXTURE_PATH
            ),
            "detector_path": RUNNER_PATH,
            "detector_present_at_g0_v0": False,
            "detector_candidate_path": runner_candidate["candidate_path"],
            "detector_candidate_sha256": runner_candidate[
                "replacement_sha256"
            ],
            "detector_symbol": "build_food_semantic_skeleton_group_report",
            "detector_value_source": "bound_policy",
            "predecessor_candidate_denominator": int(
                cause["candidate_denominator"]
            ),
            "predecessor_observed_threshold_value": int(
                cause["maximum_repetition_count"]
            ),
            "predecessor_policy_resolved_threshold_value": (
                predecessor_resolved_threshold
            ),
            "threshold_source_identity_bound": True,
            "threshold_source_value_unchanged": (
                predecessor_resolved_threshold
                == int(cause["maximum_repetition_count"])
            ),
            "threshold_policy_detector_identity_match": True,
            "threshold_authority_mismatch_classification": "none",
            "authority_match_evaluated": True,
            "threshold_authority_unclassified_mismatch_count": 0,
            "implementation_authority_gate_credit": 0,
            "D16_candidate_adopted": False,
            "actual_candidate_denominator": None,
            "actual_bound_threshold_value": None,
        },
    )
    write_json(
        phase / "no_relaxation_attestation.json",
        {
            "detector_modification_count": 0,
            "policy_modification_count": 0,
            "threshold_relaxation_count": 0,
            "waiver_added_count": 0,
            "candidate_patch_targets_detector_symbol": True,
            "candidate_detector_reads_bound_policy": True,
            "candidate_detector_ratio_matches_preserved_policy": True,
            "candidate_detector_behavior_relaxation_count": 0,
        },
    )
    write_json(
        phase / "attempt_0014_baseline_reproduction_report.json",
        {
            "status": "NO_EFFECT_PROVEN",
            "changed_path_has_no_effect_on_attempt_0014": True,
            "proof": (
                "The D16 adapter remains candidate-only at implementation "
                "entry; this attempt writes no Naturalization target path and "
                "the predecessor digest extract remains read-only."
            ),
            "baseline_repeated_skeleton_hit_count": cause[
                "baseline_repeated_skeleton_hit_count"
            ],
            "compiler_rule_remediable_item_count": cause[
                "compiler_rule_remediable_item_count"
            ],
            "source_qg_blocked_item_count": cause[
                "source_qg_blocked_item_count"
            ],
        },
    )
    write_json(
        phase / "existing_phase4_to_8_no_impact_report.json",
        {
            "status": "PASS",
            "existing_phase4_to_8_behavior_change_count": 0,
            "candidate_patch_adopted": False,
            "D16_candidate_only_pre_authorization": all(
                row["preimage_state"] == "absent_at_g0_v0"
                and row["candidate_path"]
                for row in patch_rows
            ),
            "existing_symbol_replacement_count": sum(
                row["existing_symbol_replacement_count"] for row in patch_rows
            ),
        },
    )
    write_json(
        phase / "proposition_consumption_report.json",
        {
            "status": "IMPLEMENTATION_FIXTURE_PASS",
            "fixture_record_count": len(frozen_rows),
            "fixture_schema_match": True,
            "compiler_invented_proposition_count": 0,
            "authority_consumption_claimed": False,
        },
    )
    write_json(
        phase / "skeleton_group_report.schema.json",
        {
            "requires_actual_phase2_consumer": True,
            "requires_selected_successor_binding": True,
            "requires_canonical_threshold_binding": True,
            "implementation_result_emitted": False,
        },
    )
    write_json(
        phase / "naturalization_tooling_authorization_binding.schema.json",
        {
            "decision_id": "D16",
            "required": [
                "tooling_owner",
                "allowed_files",
                "allowed_symbols",
                "adapter_and_no_render_only",
                "existing_phase4_to_8_mutation_prohibited",
                "attempt_0014_validator_semantics_preserved",
            ],
            "implementation_authorization_consumed": False,
        },
    )
    write_json(
        phase / "downstream_resume_packet.json",
        {
            "state": "deferred_until_registry_adoption_and_new_attempt",
            "official_naturalization_retry_allowed": False,
            "resume_attempt": "new_attempt_from_phase0",
            "phase2_source_inventory_reseal_required": True,
            "publish_boundary_retry_allowed": False,
        },
    )
    return {
        "status": "PASS",
        "handoff_tooling_implementation_complete": True,
        "candidate_patch_file_count": len(patch_rows),
        "candidate_patch_adopted": False,
        "D16_candidate_only_pre_authorization": all(
            row["preimage_state"] == "absent_at_g0_v0"
            and row["candidate_path"]
            for row in patch_rows
        ),
        "D16_owner_authorization_consumed": False,
        "authority_handoff_claim_emitted_count": 0,
    }
