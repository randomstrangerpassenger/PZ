from __future__ import annotations

import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as ptqa


class PublicTextQualityAcceptanceFixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = ptqa.build_foundation_contract("fixture-foundation-v1")
        self.manifest = ptqa.load_json_strict(ptqa.FIXTURE_MANIFEST)

    def test_roadmap_mandatory_and_plan_additive_fixture_contract(self) -> None:
        report = ptqa.validate_fixture_manifest(self.manifest, self.contract)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["roadmap_mandatory_fixture_count"], 36)
        self.assertGreaterEqual(report["plan_additive_fixture_count"], 1)
        self.assertGreaterEqual(report["total_fixture_count"], 37)
        self.assertEqual(report["fixture_without_origin_count"], 0)
        self.assertEqual(report["fixture_failure_count"], 0)
        self.assertTrue(all(row["fixture_pass"] for row in report["results"]))

    def test_roadmap_trace_ids_are_exact_and_unique(self) -> None:
        roadmap_ids = [
            row["fixture_id"]
            for row in self.manifest["fixtures"]
            if row["origin"] == "roadmap_mandatory"
        ]
        self.assertEqual(
            roadmap_ids,
            [f"PTQA-RM-{index:02d}" for index in range(1, 37)],
        )
        all_ids = [row["fixture_id"] for row in self.manifest["fixtures"]]
        self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_additive_fixtures_cover_cross_plan_fail_closed_boundaries(self) -> None:
        additive = {
            row["fixture_id"]: row
            for row in self.manifest["fixtures"]
            if row["origin"] == "plan_additive"
        }
        self.assertEqual(additive["PTQA-PA-02"]["expected_outcome"], "accepted")
        self.assertEqual(additive["PTQA-PA-03"]["expected_outcome"], "blocked")
        self.assertEqual(additive["PTQA-PA-05"]["expected_outcome"], "blocked")
        self.assertEqual(additive["PTQA-PA-06"]["expected_outcome"], "blocked")
        self.assertEqual(additive["PTQA-PA-07"]["expected_outcome"], "blocked")
        self.assertEqual(additive["PTQA-PA-08"]["expected_outcome"], "blocked")

    def test_fixture_evaluator_is_production_module_not_test_copy(self) -> None:
        source = Path(ptqa.__file__).read_text(encoding="utf-8")
        self.assertIn("def validate_fixture_manifest(", source)
        self.assertIn("def determine_qualified_disposition(", source)
        self.assertFalse(hasattr(sys.modules[__name__], "_fixture_outcome"))


if __name__ == "__main__":
    unittest.main()
