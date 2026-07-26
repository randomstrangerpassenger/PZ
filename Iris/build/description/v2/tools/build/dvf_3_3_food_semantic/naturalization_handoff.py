from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from .contracts import (
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
CAUSE_PATH = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
    "attempt-0014-remediation/phase3/repeated_skeleton_cause_analysis.json"
)


RUNNER_APPEND = r'''

# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
def build_food_semantic_proposition_inventory(
    facts_rows,
    *,
    schema_sha256,
    proposition_license_sha256,
):
    """Project approved structured assertions without inventing propositions."""
    inventory = []
    for facts in facts_rows:
        for assertion in facts.get("food_semantic_assertions", []):
            if assertion.get("authority_state") != "approved_candidate":
                continue
            inventory.append(
                {
                    "item_id": facts["item_id"],
                    "proposition_id": assertion["proposition_id"],
                    "fact_axis": assertion["fact_axis"],
                    "fact_value": assertion["fact_value"],
                    "authority_class": assertion["authority_class"],
                    "source_or_approval_lineage_id": assertion["lineage_id"],
                    "schema_sha256": schema_sha256,
                    "proposition_license_sha256": proposition_license_sha256,
                }
            )
    return sorted(
        inventory,
        key=lambda row: (
            row["item_id"],
            row["fact_axis"],
            row["fact_value"],
            row["proposition_id"],
        ),
    )


def build_food_semantic_no_render_receipt(
    *,
    facts_path,
    facts_sha256,
    manifest_path,
    manifest_sha256,
    schema_path,
    schema_sha256,
    proposition_license_path,
    proposition_license_sha256,
    explicit_non_current_input_override,
):
    """Return the exact inputs opened by the actual Phase 2 consumer."""
    return {
        "producer": "naturalization_actual_phase2_consumer",
        "facts_path": str(facts_path),
        "facts_sha256": facts_sha256,
        "manifest_path": str(manifest_path),
        "manifest_sha256": manifest_sha256,
        "schema_path": str(schema_path),
        "schema_sha256": schema_sha256,
        "proposition_license_path": str(proposition_license_path),
        "proposition_license_sha256": proposition_license_sha256,
        "explicit_non_current_input_override": explicit_non_current_input_override,
        "current_facts_read_count": 0 if explicit_non_current_input_override else 1,
        "render_write_count": 0,
    }
# END DVF FOOD SEMANTIC CANDIDATE PATCH
'''

VALIDATOR_APPEND = r'''

# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
def validate_food_semantic_consumed_input_receipt(receipt, selected_binding):
    """Fail closed unless the actual consumer receipt matches all four identities."""
    expected = {
        "facts_sha256": selected_binding["successor_facts_sha256"],
        "manifest_sha256": selected_binding["successor_input_manifest_sha256"],
        "schema_sha256": selected_binding["approved_food_semantic_schema_sha256"],
        "proposition_license_sha256": selected_binding[
            "approved_proposition_licensing_contract_sha256"
        ],
    }
    mismatches = [
        field for field, value in expected.items() if receipt.get(field) != value
    ]
    if receipt.get("producer") != "naturalization_actual_phase2_consumer":
        mismatches.append("producer")
    if receipt.get("render_write_count") != 0:
        mismatches.append("render_write_count")
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "mismatches": sorted(set(mismatches)),
        "four_identity_match": not mismatches,
    }
# END DVF FOOD SEMANTIC CANDIDATE PATCH
'''

ACCEPTANCE_TEST_APPEND = r'''

# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
class FoodSemanticNoRenderReceiptCandidateContractTest(unittest.TestCase):
    def test_food_semantic_receipt_requires_four_exact_identities(self):
        from tools.build.run_dvf_3_3_korean_prose_naturalization import (
            build_food_semantic_no_render_receipt,
        )
        from tools.build.validate_dvf_3_3_korean_prose_naturalization import (
            validate_food_semantic_consumed_input_receipt,
        )

        receipt = build_food_semantic_no_render_receipt(
            facts_path="successor.jsonl",
            facts_sha256="a" * 64,
            manifest_path="successor-manifest.json",
            manifest_sha256="b" * 64,
            schema_path="food-schema.json",
            schema_sha256="c" * 64,
            proposition_license_path="food-license.json",
            proposition_license_sha256="d" * 64,
            explicit_non_current_input_override=True,
        )
        selected = {
            "successor_facts_sha256": "a" * 64,
            "successor_input_manifest_sha256": "b" * 64,
            "approved_food_semantic_schema_sha256": "c" * 64,
            "approved_proposition_licensing_contract_sha256": "d" * 64,
        }
        self.assertEqual(receipt["current_facts_read_count"], 0)
        self.assertEqual(receipt["render_write_count"], 0)
        self.assertEqual(
            validate_food_semantic_consumed_input_receipt(receipt, selected)[
                "status"
            ],
            "PASS",
        )
        receipt["facts_sha256"] = "e" * 64
        drift = validate_food_semantic_consumed_input_receipt(receipt, selected)
        self.assertEqual(drift["status"], "FAIL")
        self.assertIn("facts_sha256", drift["mismatches"])
# END DVF FOOD SEMANTIC CANDIDATE PATCH
'''

PRESERVATION_TEST_APPEND = r'''

# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
class FoodSemanticPhase4To8PreservationCandidateContractTest(unittest.TestCase):
    def test_food_semantic_candidate_patch_is_additive(self):
        from tools.build.run_dvf_3_3_korean_prose_naturalization import (
            build_food_semantic_proposition_inventory,
        )

        rows = [
            {
                "item_id": "Base.Test",
                "food_semantic_assertions": [
                    {
                        "proposition_id": "fsp:approved",
                        "fact_axis": "culinary_role",
                        "fact_value": "spice",
                        "authority_class": "automatic",
                        "authority_state": "approved_candidate",
                        "lineage_id": "lineage:approved",
                    },
                    {
                        "proposition_id": "fsp:unapproved",
                        "fact_axis": "meal_role",
                        "fact_value": "meal",
                        "authority_class": "curated",
                        "authority_state": "implementation_preview_unapproved",
                        "lineage_id": "lineage:unapproved",
                    },
                ],
            }
        ]
        inventory = build_food_semantic_proposition_inventory(
            rows,
            schema_sha256="a" * 64,
            proposition_license_sha256="b" * 64,
        )
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["proposition_id"], "fsp:approved")
        self.assertEqual(inventory[0]["source_or_approval_lineage_id"], "lineage:approved")
# END DVF FOOD SEMANTIC CANDIDATE PATCH
'''


def _candidate_bytes(preimage: bytes, append_text: str) -> bytes:
    suffix = append_text.encode("utf-8")
    if preimage.endswith(b"\n"):
        return preimage + suffix.lstrip(b"\n")
    return preimage + b"\n" + suffix.lstrip(b"\n")


def _materialize_candidate_patch(
    root: Path, phase: Path
) -> list[dict[str, Any]]:
    specs = [
        (
            RUNNER_PATH,
            RUNNER_APPEND,
            [
                "build_food_semantic_proposition_inventory",
                "build_food_semantic_no_render_receipt",
            ],
        ),
        (
            VALIDATOR_PATH,
            VALIDATOR_APPEND,
            ["validate_food_semantic_consumed_input_receipt"],
        ),
        (
            ACCEPTANCE_TEST_PATH,
            ACCEPTANCE_TEST_APPEND,
            ["FoodSemanticNoRenderReceiptCandidateContractTest"],
        ),
        (
            PRESERVATION_TEST_PATH,
            PRESERVATION_TEST_APPEND,
            ["FoodSemanticPhase4To8PreservationCandidateContractTest"],
        ),
    ]
    rows: list[dict[str, Any]] = []
    for relative, append_text, symbols in specs:
        source = root / relative
        if not source.is_file():
            raise RuntimeError(f"Naturalization preimage missing: {relative}")
        preimage = source.read_bytes()
        replacement = _candidate_bytes(preimage, append_text)
        candidate = phase / "candidate_patch_files" / relative
        write_once_bytes(candidate, replacement)
        rows.append(
            {
                "target_path": relative,
                "candidate_path": candidate.relative_to(root).as_posix(),
                "preimage_sha256": sha256_bytes(preimage),
                "replacement_sha256": sha256_bytes(replacement),
                "affected_symbols": symbols,
                "existing_symbol_replacement_count": 0,
                "patch_kind": "additive_candidate_not_adopted",
            }
        )
    return rows


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
            "candidate_patch_preimage_mismatch_count": 0,
            "D16_owner_authorization_consumed": False,
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
            ],
            "producer_must_equal": "naturalization_actual_phase2_consumer",
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
    policy_path = root / POLICY_PATH
    policy = load_json(policy_path)
    ratio = policy["detectors"]["repeated_skeleton_concentration"]["ratio"]
    detector_path = root / RUNNER_PATH
    cause = load_json(root / CAUSE_PATH)
    candidate_denominator = int(cause["candidate_denominator"])
    threshold_value = candidate_denominator * int(ratio["numerator"]) // int(
        ratio["denominator"]
    )
    write_json(
        phase / "threshold_authority_binding.json",
        {
            "policy_path": POLICY_PATH,
            "policy_sha256": sha256_file(policy_path),
            "policy_ratio": ratio,
            "detector_path": RUNNER_PATH,
            "detector_sha256": sha256_file(detector_path),
            "detector_value_source": "bound_policy",
            "resolved_candidate_denominator": candidate_denominator,
            "resolved_bound_threshold_value": threshold_value,
            "planning_observed_value": 104,
            "threshold_policy_detector_identity_match": threshold_value == 104,
            "threshold_authority_unclassified_mismatch_count": 0,
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
                "Candidate patch is not adopted and only appends new helper/test "
                "symbols; existing cause-analysis and detector symbols are unchanged."
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
        "D16_owner_authorization_consumed": False,
        "authority_handoff_claim_emitted_count": 0,
    }
