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
    def test_food_semantic_receipt_requires_four_exact_identities(self):
        from tools.build.run_dvf_3_3_korean_prose_naturalization import (
            build_food_semantic_no_render_receipt,
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
            facts.write_text(
                json.dumps(
                    {
                        "item_id": "Base.Test",
                        "food_semantic_assertions": [
                            {
                                "proposition_id": "fsp:approved",
                                "fact_axis": "meal_role",
                                "fact_value": "meal",
                                "authority_class": "curated",
                                "authority_state": "owner_approved",
                                "lineage_id": "approval:test",
                            }
                        ],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            schema.write_text('{"schema_version":"fixture"}\n', encoding="utf-8")
            proposition_license.write_text(
                '{"schema_version":"fixture"}\n', encoding="utf-8"
            )

            def digest(path: Path) -> str:
                return hashlib.sha256(path.read_bytes()).hexdigest()

            manifest.write_text(
                json.dumps(
                    {"facts": {"path": str(facts), "sha256": digest(facts)}},
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            receipt = build_food_semantic_no_render_receipt(
                facts_path=facts,
                manifest_path=manifest,
                schema_path=schema,
                proposition_license_path=proposition_license,
                explicit_non_current_input_override=True,
            )
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
            }
            self.assertEqual(receipt["opened_input_count"], 4)
            self.assertEqual(receipt["current_facts_read_count"], 0)
            self.assertEqual(receipt["render_write_count"], 0)
            self.assertEqual(receipt["food_semantic_proposition_count"], 1)
            self.assertEqual(
                validate_food_semantic_consumed_input_receipt(
                    receipt,
                    selected,
                    repository_root=root,
                )["status"],
                "PASS",
            )

            wrong_predecessor = dict(selected)
            wrong_predecessor["successor_facts_sha256"] = "e" * 64
            predecessor_drift = validate_food_semantic_consumed_input_receipt(
                receipt,
                wrong_predecessor,
                repository_root=root,
            )
            self.assertEqual(predecessor_drift["status"], "FAIL")
            self.assertIn("facts_sha256", predecessor_drift["mismatches"])

            wrong_candidate = dict(selected)
            wrong_candidate["successor_input_manifest_sha256"] = "f" * 64
            candidate_drift = validate_food_semantic_consumed_input_receipt(
                receipt,
                wrong_candidate,
                repository_root=root,
            )
            self.assertEqual(candidate_drift["status"], "FAIL")
            self.assertIn("manifest_sha256", candidate_drift["mismatches"])

            with self.assertRaises(ValueError):
                build_food_semantic_no_render_receipt(
                    facts_path=facts,
                    facts_sha256="0" * 64,
                    manifest_path=manifest,
                    schema_path=schema,
                    proposition_license_path=proposition_license,
                    explicit_non_current_input_override=True,
                )
            with self.assertRaises(ValueError):
                build_food_semantic_no_render_receipt(
                    facts_path=facts,
                    manifest_path=manifest,
                    schema_path=schema,
                    proposition_license_path=proposition_license,
                    explicit_non_current_input_override=False,
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
                build_food_semantic_no_render_receipt(
                    facts_path=facts,
                    manifest_path=bad_manifest,
                    schema_path=schema,
                    proposition_license_path=proposition_license,
                    explicit_non_current_input_override=True,
                )
# END DVF FOOD SEMANTIC CANDIDATE PATCH
