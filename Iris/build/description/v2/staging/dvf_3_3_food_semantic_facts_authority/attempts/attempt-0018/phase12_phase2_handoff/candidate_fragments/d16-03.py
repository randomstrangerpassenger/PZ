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
