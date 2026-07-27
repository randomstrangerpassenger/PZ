from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.compose_layer3_body_profile import (
    build_single_proposition_equivalence_proof,
)
from tools.build.run_dvf_3_3_korean_prose_naturalization import (
    proposition_id_for,
    proof_valid,
)


class KoreanProseSemanticPreservationTest(unittest.TestCase):
    def test_proposition_identity_includes_origin_and_value(self) -> None:
        base = proposition_id_for("Base.Test", "primary_use", "수리에 쓴다", ["direct_use"])
        changed_value = proposition_id_for(
            "Base.Test", "primary_use", "제작에 쓴다", ["direct_use"]
        )
        changed_origin = proposition_id_for(
            "Base.Test", "primary_use", "수리에 쓴다", ["cluster_summary"]
        )
        self.assertNotEqual(base, changed_value)
        self.assertNotEqual(base, changed_origin)

    def test_typed_equivalence_proof_binds_provenance_sets(self) -> None:
        proposition = {
            "proposition_id": "Base.Test#use",
            "source_path": "facts.jsonl",
            "source_field": "facts.primary_use",
            "semantic_key": "use-key",
            "qualifier": "none",
            "condition": "none",
            "modality": "asserted",
        }
        proof = build_single_proposition_equivalence_proof(
            item_id="Base.Test",
            requirement_id="Base.Test#context_support",
            proposition=proposition,
            surviving_clause_id="Base.Test#clause-001",
        )
        self.assertTrue(proof_valid(proof))
        proof["surviving_trace_provenance_set"] = ["other.jsonl#facts.primary_use"]
        self.assertFalse(proof_valid(proof))

    def test_negative_fixture_covers_all_required_failures(self) -> None:
        path = (
            V2_ROOT
            / "data"
            / "korean_prose_naturalization"
            / "semantic_negative_fixtures.jsonl"
        )
        reasons = {
            json.loads(line)["expected_failure_reason"]
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        }
        self.assertEqual(
            reasons,
            {
                "unsupported_use_insertion",
                "strengthened_modality",
                "limitation_deleted",
                "context_qualifier_deleted",
                "cross_item_proposition",
                "trace_missing",
                "invalid_suppression_reason",
                "source_candidate_key_swap",
            },
        )


if __name__ == "__main__":
    unittest.main()
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
