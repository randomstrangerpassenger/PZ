from __future__ import annotations

import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as ptqa


class PublicTextQualityMetricContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = ptqa.build_foundation_contract("test-foundation-v1")

    def test_metric_and_denominator_registries_are_closed_and_complete(self) -> None:
        report = ptqa.validate_foundation_contract(
            self.contract,
            expected_foundation_id="test-foundation-v1",
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["metric_count"], 21)
        self.assertEqual(report["denominator_count"], 15)
        self.assertEqual(report["raw_detector_count"], 7)
        self.assertEqual(report["unknown_metric_count"], 0)
        self.assertEqual(report["unknown_denominator_count"], 0)
        self.assertEqual(report["unmapped_raw_detector_count"], 0)

    def test_disposition_class_enum_has_only_three_machine_tokens(self) -> None:
        registry = self.contract["metric_registry_candidate"]
        self.assertEqual(
            registry["disposition_class_enum"],
            ["blocking_gate", "advisory_debt", "non_claim"],
        )
        annotations = {row["annotation"] for row in registry["registrations"]}
        self.assertIn("diagnostic_breakdown", annotations)
        self.assertNotIn("diagnostic_breakdown", registry["disposition_class_enum"])
        self.assertNotIn("separate_adoption_axis", registry["disposition_class_enum"])

    def test_current_quality_and_unadopted_axes_are_separate(self) -> None:
        rows = {
            row["metric_id"]: row
            for row in self.contract["metric_registry_candidate"]["registrations"]
        }
        for metric_id in (
            "coverage_quality_weak",
            "coverage_quality_adequate",
            "coverage_quality_strong",
        ):
            self.assertEqual(
                rows[metric_id]["denominator_id"],
                "quality_evaluable_adopted_item_v1",
            )
        self.assertEqual(
            rows["unadopted"]["denominator_id"],
            "current_item_universe_v1",
        )
        self.assertEqual(rows["unadopted"]["disposition_class"], "non_claim")
        self.assertEqual(rows["unadopted"]["annotation"], "separate_adoption_axis")

    def test_row_and_occurrence_metrics_are_not_aliased(self) -> None:
        rows = {
            row["metric_id"]: row
            for row in self.contract["metric_registry_candidate"]["registrations"]
        }
        self.assertEqual(
            rows["missing_any_required_section_row"]["denominator_id"],
            "quality_evaluable_adopted_item_v1",
        )
        self.assertEqual(
            rows["missing_required_section_occurrence"]["denominator_id"],
            "required_section_opportunity_v1",
        )
        self.assertEqual(
            rows["missing_any_required_section_row"]["disposition_class"],
            "blocking_gate",
        )
        self.assertEqual(
            rows["missing_required_section_occurrence"]["disposition_class"],
            "advisory_debt",
        )

    def test_subject_applicability_is_explicit(self) -> None:
        for row in self.contract["metric_registry_candidate"]["registrations"]:
            applicable = row["applicable_subject_kinds"]
            self.assertTrue(applicable)
            self.assertTrue(set(applicable).issubset(ptqa.EVALUATION_SUBJECT_KINDS))
            self.assertNotEqual(
                applicable,
                list(ptqa.EVALUATION_SUBJECT_KINDS),
                f"{row['metric_id']} must not silently apply to both subjects",
            )

    def test_equivalence_proof_has_a_transformation_denominator(self) -> None:
        rows = {
            row["metric_id"]: row
            for row in self.contract["metric_registry_candidate"]["registrations"]
        }
        self.assertEqual(
            rows["equivalence_proof_failure"]["denominator_id"],
            "naturalization_fusion_suppression_transformation_v1",
        )

    def test_structural_status_partition_is_closed(self) -> None:
        self.assertEqual(
            ptqa.CANDIDATE_STRUCTURAL_STATUSES,
            (
                "emitted_direct",
                "satisfied_by_verified_fusion",
                "satisfied_by_verified_suppression",
                "not_required",
                "missing",
            ),
        )
        self.assertNotIn(
            "not_required",
            ptqa.SATISFIED_REQUIRED_STRUCTURAL_STATUSES,
        )
        self.assertNotIn("missing", ptqa.SATISFIED_REQUIRED_STRUCTURAL_STATUSES)

    def test_exact_rational_threshold_has_no_binary_float_path(self) -> None:
        threshold = {
            "operator": "le",
            "value": {"numerator": 1, "denominator": 20},
        }
        self.assertTrue(
            ptqa.evaluate_threshold(
                numerator=5,
                denominator=100,
                threshold=threshold,
            )
        )
        self.assertFalse(
            ptqa.evaluate_threshold(
                numerator=6,
                denominator=100,
                threshold=threshold,
            )
        )
        with self.assertRaises(ptqa.FoundationContractError):
            ptqa.evaluate_threshold(
                numerator=0,
                denominator=0,
                threshold={"operator": "eq", "value": {"integer": 0}},
            )


if __name__ == "__main__":
    unittest.main()
