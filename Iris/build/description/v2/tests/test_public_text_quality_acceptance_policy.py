from __future__ import annotations

import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as ptqa


class PublicTextQualityAcceptancePolicyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = ptqa.build_foundation_contract("test-foundation-v1")
        self.policy = self.contract["policy_candidate"]

    def test_policy_is_candidate_not_ratified_authority(self) -> None:
        self.assertEqual(
            self.policy["authority_state"],
            "development_foundation_candidate",
        )
        self.assertEqual(self.policy["authority_effect"], "none")
        self.assertFalse(self.policy["official_policy_ratified"])
        self.assertEqual(self.contract["official_disposition"], "not_issued")
        self.assertFalse(self.contract["live_gate_adopted"])
        self.assertEqual(self.contract["policy_closure_state"], "not_started")
        self.assertFalse(self.contract["policy_seal_created"])
        self.assertFalse(self.contract["terminal_seal_created"])

    def test_default_exception_and_waiver_sets_are_empty(self) -> None:
        self.assertEqual(self.policy["default_exceptions"], [])
        self.assertEqual(self.policy["waiver_contract"]["default_set"], [])
        self.assertFalse(
            self.policy["waiver_contract"]["technical_or_freshness_scope_allowed"]
        )
        self.assertFalse(
            self.policy["waiver_contract"]["raw_metric_mutation_allowed"]
        )
        self.assertFalse(
            self.policy["waiver_contract"]["waiver_can_create_clean_accepted"]
        )
        self.assertEqual(
            self.policy["waiver_contract"]["allowed_waived_disposition"],
            "deferred_internal_debt",
        )

    def test_current_zero_tolerance_metrics_are_precommitted(self) -> None:
        current = self.policy["current_runtime_payload_thresholds"]
        for metric_id in (
            "coverage_quality_weak",
            "missing_any_required_section_row",
        ):
            self.assertEqual(current[metric_id]["disposition_class"], "blocking_gate")
            self.assertEqual(
                current[metric_id]["threshold"],
                {"operator": "eq", "value": {"integer": 0}},
            )
        self.assertEqual(
            current["missing_required_section_occurrence"]["disposition_class"],
            "advisory_debt",
        )
        self.assertEqual(current["unadopted"]["disposition_class"], "non_claim")

    def test_detector_mapping_is_exact_and_has_no_runtime_default(self) -> None:
        mappings = self.contract["detector_mapping_candidate"]["mappings"]
        self.assertEqual(
            [row["detector_id"] for row in mappings],
            list(ptqa.RAW_DETECTOR_IDS),
        )
        policy_rows = self.policy["naturalization_candidate_thresholds"]
        for row in mappings:
            self.assertEqual(
                policy_rows[row["detector_id"]]["disposition_class"],
                row["disposition_class"],
            )
            self.assertEqual(
                policy_rows[row["detector_id"]]["threshold"],
                row["threshold"],
            )
        self.assertEqual(
            self.contract["detector_mapping_candidate"][
                "unknown_or_unmapped_detector_effect"
            ],
            "technical_blocker",
        )

    def test_human_review_selection_is_deterministic_and_scope_bounded(self) -> None:
        review = self.contract["human_review_selection_contract"]
        self.assertEqual(
            review["algorithm_id"],
            "deterministic_stratified_sha256_rank_v1",
        )
        self.assertEqual(
            review["required_denominator_id"],
            "naturalization_human_review_required_v1",
        )
        self.assertEqual(
            review["human_only_claim_scope"],
            "selected_required_denominator_only",
        )
        self.assertTrue(
            review[
                "corpus_wide_human_only_zero_claim_requires_full_corpus_review"
            ]
        )

    def test_sync_projection_matches_both_plan_contract(self) -> None:
        projection = self.contract["synchronization_projection"]
        self.assertEqual(
            projection["synchronization_contract_id"],
            ptqa.SYNC_CONTRACT_ID,
        )
        self.assertEqual(
            projection["canonical_stage_order"],
            [
                "S0_plan_sync",
                "S1_publish_foundation",
                "S2_naturalization_build",
                "S3_publish_official_attempt",
                "S4_naturalization_finalize",
            ],
        )
        self.assertEqual(
            projection["foundation_required_state"],
            {
                "foundation_contract_ready_for_remediation": True,
                "authority_effect": "none",
                "official_disposition": "not_issued",
                "live_gate_adopted": False,
                "policy_closure_state": "not_started",
            },
        )
        self.assertFalse(
            projection["blocked_immediate_allowed_for_synchronized_candidate"]
        )
        self.assertEqual(
            projection["candidate_runtime_parity_reason"],
            "candidate_not_registry_adopted",
        )

    def test_policy_has_no_candidate_result_dependency(self) -> None:
        constraints = self.policy["threshold_rationale_constraints"]
        self.assertFalse(constraints["candidate_metric_dependency_allowed"])
        self.assertFalse(constraints["current_payload_result_dependency_allowed"])
        self.assertFalse(constraints["historical_threshold_inheritance_allowed"])
        self.assertEqual(self.contract["candidate_content_dependency_count"], 0)
        self.assertEqual(self.contract["candidate_metric_dependency_count"], 0)

    def test_item_and_aggregate_disposition_mappings_are_explicit(self) -> None:
        item_mapping = self.policy["item_disposition_mapping"]
        self.assertEqual(item_mapping["technical_blocker"], "blocked")
        self.assertEqual(
            item_mapping["advisory_debt_unsatisfied"],
            "deferred_internal_debt",
        )
        self.assertEqual(
            self.policy["aggregate_disposition_enum"],
            ["accepted", "blocked", "deferred_internal_debt"],
        )
        freshness = self.contract["freshness_contract"]
        self.assertFalse(freshness["same_version_threshold_or_mapping_mutation_allowed"])
        self.assertFalse(freshness["last_known_good_disposition_fallback_allowed"])


if __name__ == "__main__":
    unittest.main()
