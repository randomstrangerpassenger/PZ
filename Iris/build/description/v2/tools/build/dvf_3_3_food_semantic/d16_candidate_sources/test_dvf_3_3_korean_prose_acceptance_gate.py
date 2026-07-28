from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))


# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
class FoodSemanticNoRenderReceiptCandidateContractTest(unittest.TestCase):
    def test_food_semantic_receipt_requires_exact_projection(self):
        from tools.build.run_dvf_3_3_korean_prose_naturalization import (
            consume_food_semantic_inputs_no_render,
        )
        from tools.build.validate_dvf_3_3_korean_prose_naturalization import (
            validate_food_semantic_consumed_input_receipt,
        )

        staging = V2_ROOT / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=staging) as temp_dir:
            root = Path(temp_dir)
            facts = root / "successor.jsonl"
            manifest = root / "successor-manifest.json"
            schema = root / "food-schema.json"
            proposition_license = root / "food-license.json"
            threshold_policy = (
                V2_ROOT
                / "tools/build/dvf_3_3_food_semantic/"
                "d16_candidate_sources/korean_prose_policy.json"
            )
            threshold_denominator_binding = (
                V2_ROOT
                / "tests/fixtures/dvf_3_3_food_semantic_facts_authority/"
                "naturalization_attempt_0014_baseline_binding.json"
            )
            facts.write_text(
                json.dumps(
                    {
                        "item_id": "Base.Test",
                        "food_semantic_assertions": [
                            {
                                "proposition_id": "fsp:consumption",
                                "fact_axis": "consumption_form",
                                "fact_value": "solid_food",
                                "authority_class": "curated",
                                "authority_state": "owner_approved",
                                "lineage_id": "approval:consumption",
                            },
                            {
                                "proposition_id": "fsp:meal",
                                "fact_axis": "meal_role",
                                "fact_value": "meal",
                                "authority_class": "curated",
                                "authority_state": "owner_approved",
                                "lineage_id": "approval:meal",
                            }
                        ],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            schema.write_text(
                json.dumps(
                    {
                        "schema_version": "fixture",
                        "axes": [
                            {
                                "axis": "consumption_form",
                                "cardinality": "one_or_more",
                                "values": [{"value": "solid_food"}],
                            },
                            {
                                "axis": "meal_role",
                                "cardinality": "one_or_more",
                                "values": [{"value": "meal"}],
                            },
                        ],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            proposition_license.write_text(
                json.dumps(
                    {
                        "schema_version": "fixture",
                        "licenses": [
                            {
                                "fact_axis": "consumption_form",
                                "fact_value": "solid_food",
                                "automatic_eligible": False,
                                "curated_allowed": True,
                            },
                            {
                                "fact_axis": "meal_role",
                                "fact_value": "meal",
                                "automatic_eligible": False,
                                "curated_allowed": True,
                            },
                        ],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )

            def digest(path: Path) -> str:
                return hashlib.sha256(path.read_bytes()).hexdigest()

            item_set_sha256 = hashlib.sha256(
                b"Base.Test\n"
            ).hexdigest()
            expected_inventory_rows = [
                {
                    "item_id": "Base.Test",
                    "proposition_id": "fsp:consumption",
                    "fact_axis": "consumption_form",
                    "fact_value": "solid_food",
                    "authority_class": "curated",
                    "source_or_approval_lineage_id": "approval:consumption",
                    "schema_sha256": digest(schema),
                    "proposition_license_sha256": digest(
                        proposition_license
                    ),
                },
                {
                    "item_id": "Base.Test",
                    "proposition_id": "fsp:meal",
                    "fact_axis": "meal_role",
                    "fact_value": "meal",
                    "authority_class": "curated",
                    "source_or_approval_lineage_id": "approval:meal",
                    "schema_sha256": digest(schema),
                    "proposition_license_sha256": digest(
                        proposition_license
                    ),
                },
            ]
            expected_inventory_bytes = "".join(
                json.dumps(
                    row,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
                for row in expected_inventory_rows
            ).encode("utf-8")
            expected_inventory_sha256 = hashlib.sha256(
                expected_inventory_bytes
            ).hexdigest()
            manifest.write_text(
                json.dumps(
                    {
                        "facts": {
                            "path": str(facts),
                            "sha256": digest(facts),
                        },
                        "food_semantic_authority": {
                            "schema_sha256": digest(schema),
                            "proposition_license_sha256": digest(
                                proposition_license
                            ),
                            "target_member_count": 1,
                            "target_member_set_sha256": item_set_sha256,
                            "required_fact_axes": [
                                "consumption_form",
                                "meal_role",
                            ],
                            "proposition_count": 2,
                            "proposition_inventory_sha256": (
                                expected_inventory_sha256
                            ),
                        },
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            consumed = consume_food_semantic_inputs_no_render(
                facts_path=facts,
                manifest_path=manifest,
                schema_path=schema,
                proposition_license_path=proposition_license,
                explicit_non_current_input_override=True,
                threshold_policy_path=threshold_policy,
                threshold_denominator_binding_path=(
                    threshold_denominator_binding
                ),
            )
            receipt = consumed["receipt"]
            inventory_bytes = "".join(
                json.dumps(
                    row,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
                for row in consumed["inventory"]
            ).encode("utf-8")
            expected_projection = {
                "inventory_sha256": expected_inventory_sha256,
                "proposition_count": 2,
                "item_count": 1,
                "item_set_sha256": item_set_sha256,
                "required_fact_axes": [
                    "consumption_form",
                    "meal_role",
                ],
                "minimum_meaningful_partition": 1,
                "meaningful_partition_count": 1,
            }
            selected = {
                "successor_facts_path": str(facts),
                "successor_facts_sha256": digest(facts),
                "successor_input_manifest_path": str(manifest),
                "successor_input_manifest_sha256": digest(manifest),
                "approved_food_semantic_schema_path": str(schema),
                "approved_food_semantic_schema_sha256": digest(schema),
                "approved_proposition_licensing_contract_path": str(
                    proposition_license
                ),
                "approved_proposition_licensing_contract_sha256": digest(
                    proposition_license
                ),
                "target_member_count": 1,
                "target_member_set_sha256": item_set_sha256,
                "required_fact_axes": [
                    "consumption_form",
                    "meal_role",
                ],
                "minimum_meaningful_partition": 1,
            }
            self.assertEqual(inventory_bytes, expected_inventory_bytes)
            self.assertEqual(receipt["opened_input_count"], 4)
            self.assertEqual(receipt["current_facts_read_count"], 0)
            self.assertEqual(receipt["render_write_count"], 0)
            self.assertEqual(receipt["food_semantic_proposition_count"], 2)
            self.assertEqual(consumed["skeleton_group_report"]["status"], "PASS")
            self.assertEqual(
                consumed["threshold_authority_binding"][
                    "detector_value_source"
                ],
                "bound_policy",
            )
            self.assertEqual(
                validate_food_semantic_consumed_input_receipt(
                    receipt,
                    selected,
                    repository_root=root,
                    expected_projection=expected_projection,
                )["status"],
                "PASS",
            )

            wrong_predecessor = dict(selected)
            wrong_predecessor["successor_facts_sha256"] = "e" * 64
            predecessor_drift = validate_food_semantic_consumed_input_receipt(
                receipt,
                wrong_predecessor,
                repository_root=root,
                expected_projection=expected_projection,
            )
            self.assertEqual(predecessor_drift["status"], "FAIL")
            self.assertIn("facts_sha256", predecessor_drift["mismatches"])

            wrong_candidate = dict(selected)
            wrong_candidate["successor_input_manifest_sha256"] = "f" * 64
            candidate_drift = validate_food_semantic_consumed_input_receipt(
                receipt,
                wrong_candidate,
                repository_root=root,
                expected_projection=expected_projection,
            )
            self.assertEqual(candidate_drift["status"], "FAIL")
            self.assertIn("manifest_sha256", candidate_drift["mismatches"])

            dropped = dict(receipt)
            dropped["food_semantic_proposition_count"] = 1
            self.assertEqual(
                validate_food_semantic_consumed_input_receipt(
                    dropped,
                    selected,
                    repository_root=root,
                    expected_projection=expected_projection,
                )["status"],
                "FAIL",
            )
            invented = dict(receipt)
            invented["food_semantic_proposition_inventory_sha256"] = "0" * 64
            self.assertEqual(
                validate_food_semantic_consumed_input_receipt(
                    invented,
                    selected,
                    repository_root=root,
                    expected_projection=expected_projection,
                )["status"],
                "FAIL",
            )
            missing_axis = dict(receipt)
            missing_axis["required_axis_missing_item_count"] = 1
            self.assertEqual(
                validate_food_semantic_consumed_input_receipt(
                    missing_axis,
                    selected,
                    repository_root=root,
                    expected_projection=expected_projection,
                )["status"],
                "FAIL",
            )
            oversized_skeleton = dict(receipt)
            oversized_skeleton["maximum_same_skeleton_group"] = (
                receipt["bound_threshold_value"] + 1
            )
            self.assertEqual(
                validate_food_semantic_consumed_input_receipt(
                    oversized_skeleton,
                    selected,
                    repository_root=root,
                    expected_projection=expected_projection,
                )["status"],
                "FAIL",
            )

            with self.assertRaises(ValueError):
                consume_food_semantic_inputs_no_render(
                    facts_path=facts,
                    facts_sha256="0" * 64,
                    manifest_path=manifest,
                    schema_path=schema,
                    proposition_license_path=proposition_license,
                    explicit_non_current_input_override=True,
                    threshold_policy_path=threshold_policy,
                    threshold_denominator_binding_path=(
                        threshold_denominator_binding
                    ),
                )
            with self.assertRaises(ValueError):
                consume_food_semantic_inputs_no_render(
                    facts_path=facts,
                    manifest_path=manifest,
                    schema_path=schema,
                    proposition_license_path=proposition_license,
                    explicit_non_current_input_override=False,
                    threshold_policy_path=threshold_policy,
                    threshold_denominator_binding_path=(
                        threshold_denominator_binding
                    ),
                )
            bad_manifest = root / "wrong-candidate-manifest.json"
            bad_manifest.write_text(
                json.dumps(
                    {"facts": {"path": str(facts), "sha256": "9" * 64}},
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
                )
            with self.assertRaises(ValueError):
                consume_food_semantic_inputs_no_render(
                    facts_path=facts,
                    manifest_path=bad_manifest,
                    schema_path=schema,
                    proposition_license_path=proposition_license,
                    explicit_non_current_input_override=True,
                    threshold_policy_path=threshold_policy,
                    threshold_denominator_binding_path=(
                        threshold_denominator_binding
                    ),
                )
# END DVF FOOD SEMANTIC CANDIDATE PATCH
