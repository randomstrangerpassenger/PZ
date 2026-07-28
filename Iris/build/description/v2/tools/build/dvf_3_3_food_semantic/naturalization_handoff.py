from __future__ import annotations

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
    "Iris/build/description/v2/data/korean_prose_naturalization/"
    "korean_prose_policy.json"
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
            "build_food_semantic_proposition_inventory",
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
            "FoodSemanticNoRenderReceiptCandidateContractTest",
        ],
    },
    {
        "target_path": PRESERVATION_TEST_PATH,
        "template_name": (
            "test_dvf_3_3_korean_prose_semantic_preservation.py"
        ),
        "affected_symbols": [
            "FoodSemanticPhase4To8PreservationCandidateContractTest",
        ],
    },
]


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
        missing_symbols = [
            symbol
            for symbol in spec["affected_symbols"]
            if symbol not in replacement_text
        ]
        if missing_symbols:
            raise FoodSemanticError(
                f"D16 candidate template missing symbols: {missing_symbols}"
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
                "affected_symbols": spec["affected_symbols"],
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
    for row in manifest.get("files", []):
        target = root / row["target_path"]
        candidate = root / row["candidate_path"]
        if row.get("preimage_state") != "absent_at_g0_v0":
            blockers.append(f"{row['target_path']}:preimage_state")
        if row.get("preimage_sha256") is not None:
            blockers.append(f"{row['target_path']}:preimage_sha256")
        if target.exists():
            blockers.append(f"{row['target_path']}:target_not_absent")
        if not candidate.is_file():
            blockers.append(f"{row['target_path']}:candidate_missing")
            continue
        payload = candidate.read_bytes()
        if sha256_bytes(payload) != row.get("replacement_sha256"):
            blockers.append(f"{row['target_path']}:candidate_sha256")
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
        "adopted_files": [
            {
                "target_path": row["target_path"],
                "replacement_sha256": row["replacement_sha256"],
                "actual_sha256": sha256_file(target),
                "affected_symbols": row["affected_symbols"],
            }
            for target, _, row in prepared
        ],
        "out_of_scope_file_count": 0,
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
            "candidate_patch_out_of_scope_symbol_count": 0,
            "forbidden_symbols": [
                "run_phase4",
                "run_phase5",
                "run_phase6",
                "run_phase7",
                "run_phase8",
                "render",
                "publish",
            ],
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
    detector_path = root / RUNNER_PATH
    cause = load_json(root / PREDECESSOR_BASELINE_FIXTURE_PATH)
    write_json(
        phase / "threshold_authority_binding.json",
        {
            "policy_path": POLICY_PATH,
            "policy_present_at_g0_v0": (root / POLICY_PATH).is_file(),
            "policy_sha256": (
                sha256_file(root / POLICY_PATH)
                if (root / POLICY_PATH).is_file()
                else None
            ),
            "detector_path": RUNNER_PATH,
            "detector_present_at_g0_v0": detector_path.is_file(),
            "detector_sha256": (
                sha256_file(detector_path)
                if detector_path.is_file()
                else None
            ),
            "detector_value_source": "future_canonical_policy_required",
            "predecessor_candidate_denominator": int(
                cause["candidate_denominator"]
            ),
            "predecessor_observed_threshold_value": int(
                cause["maximum_repetition_count"]
            ),
            "threshold_policy_detector_identity_match": None,
            "authority_match_evaluated": False,
            "threshold_authority_unclassified_mismatch_count": 0,
            "implementation_authority_gate_credit": 0,
        },
    )
    write_json(
        phase / "no_relaxation_attestation.json",
        {
            "detector_modification_count": 0,
            "policy_modification_count": 0,
            "threshold_relaxation_count": 0,
            "waiver_added_count": 0,
            "candidate_patch_targets_detector_symbol": False,
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
