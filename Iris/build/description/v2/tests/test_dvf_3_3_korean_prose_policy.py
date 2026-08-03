from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))


class KoreanProsePolicyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = V2_ROOT / "data" / "korean_prose_naturalization"
        self.policy = json.loads(
            (self.data / "korean_prose_policy.json").read_text(encoding="utf-8")
        )
        self.foundation = json.loads(
            (
                REPO_ROOT
                / "Iris"
                / "_docs"
                / "round3"
                / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
                / "foundation"
                / "public_text_quality_foundation_contract.json"
            ).read_text(encoding="utf-8")
        )

    def test_raw_detector_registry_matches_foundation_precommit(self) -> None:
        expected = [
            row["detector_id"]
            for row in self.foundation["detector_mapping_candidate"]["mappings"]
        ]
        self.assertEqual(self.policy["raw_detector_ids"], expected)
        self.assertEqual(set(self.policy["detectors"]), set(expected))

    def test_realization_policy_does_not_own_publish_disposition(self) -> None:
        self.assertFalse(self.policy["acceptance_threshold_owned_here"])
        self.assertFalse(self.policy["waiver_owned_here"])
        self.assertFalse(self.policy["item_or_aggregate_disposition_owned_here"])
        self.assertNotIn("aggregate_disposition_enum", self.policy)

    def test_structural_applicability_is_source_bound_and_noninventive(self) -> None:
        contract = self.policy["structural_applicability_contract"]
        self.assertEqual(
            contract["rule_id"],
            "source_bound_profile_role_applicability_v1",
        )
        self.assertEqual(
            contract[
                "profile_required_role_with_no_approved_source_proposition"
            ],
            "candidate_optional_owner_approved_exclusion",
        )
        self.assertFalse(contract["source_proposition_invention_allowed"])
        self.assertFalse(contract["current_compose_profiles_mutated"])
        self.assertFalse(contract["current_source_authority_mutated"])

    def test_current_snapshot_is_not_semantic_authority(self) -> None:
        snapshot = json.loads(
            (self.data / "current_surface_snapshot_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(snapshot["semantic_authority"])
        self.assertFalse(snapshot["candidate_answer_corpus"])

    def test_case_variant_fixture_keys_remain_distinct(self) -> None:
        rows = [
            json.loads(line)
            for line in (self.data / "gold_corpus.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line
        ]
        keys = {row["item_id"] for row in rows}
        self.assertIn("Base.LemonGrass", keys)
        self.assertIn("Base.Lemongrass", keys)
        self.assertEqual(len({"Base.LemonGrass", "Base.Lemongrass"} & keys), 2)


if __name__ == "__main__":
    unittest.main()
