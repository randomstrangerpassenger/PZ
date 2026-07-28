from __future__ import annotations

import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))


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
                        "authority_state": "approved",
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
