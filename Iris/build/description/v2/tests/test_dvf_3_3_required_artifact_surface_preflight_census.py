from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census"
RUNNER = TOOLS / "run_dvf_3_3_required_artifact_surface_preflight_census.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_required_artifact_surface_preflight_census.py"

sys.path.insert(0, str(TOOLS))

from dvf_3_3_required_artifact_surface_preflight_census_common import (  # noqa: E402
    EXPECTED_REQUIRED_ARTIFACT_COUNT,
    derive_resolution_verdict,
    synthetic_fail_closed_matrix_rows,
    vcs_state,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfRequiredArtifactSurfacePreflightCensusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        final = ROOT / "census_p8_closeout_no_mutation/final_preflight_census_report.json"
        if final.exists():
            payload = load_json(final)
            if payload.get("status") == "PASS":
                return
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "census"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "required artifact surface preflight census generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_denominator_and_vcs_tuple_coverage_are_manifest_derived(self) -> None:
        universe = load_json(ROOT / "census_p1_denominator_lock/required_artifact_universe.json")
        denominator = load_json(ROOT / "census_p1_denominator_lock/census_denominator_declaration.json")
        disjoint = load_json(ROOT / "census_p1_denominator_lock/output_root_disjointness_report.json")
        vcs_summary = load_json(ROOT / "census_p2_vcs_census/required_artifact_vcs_summary.json")

        self.assertEqual(universe["status"], "PASS")
        self.assertEqual(universe["required_artifact_count"], denominator["derived_required_artifact_count"])
        self.assertEqual(universe["required_artifact_count"], vcs_summary["vcs_tuple_count"])
        self.assertEqual(denominator["expected_current_readpoint_required_artifact_count"], EXPECTED_REQUIRED_ARTIFACT_COUNT)
        self.assertTrue(denominator["denominator_substitution_rejected"])
        self.assertEqual(disjoint["status"], "PASS")
        self.assertEqual(disjoint["required_artifact_intersection_count"], 0)
        self.assertTrue(vcs_summary["check_ignore_no_index_is_diagnostic_only"])

    def test_field_join_and_hash_partition_keep_predicates_separate(self) -> None:
        universe = load_json(ROOT / "census_p1_denominator_lock/required_artifact_universe.json")
        field_join = load_json(ROOT / "census_p3_field_join/field_pass_vcs_state_join_report.json")
        hash_summary = load_json(ROOT / "census_p4_hash_partition/hash_candidate_summary.json")
        non_hash_summary = load_json(ROOT / "census_p4_hash_partition/non_hash_candidate_summary.json")

        self.assertTrue(field_join["field_pass_does_not_imply_vcs_pass"])
        self.assertTrue(field_join["vcs_pass_does_not_imply_field_pass"])
        self.assertEqual(field_join["field_inventory_count"], universe["required_artifact_count"])
        self.assertEqual(
            hash_summary["hash_candidate_count"] + non_hash_summary["non_hash_candidate_count"],
            universe["required_artifact_count"],
        )
        self.assertFalse(hash_summary["sealed_hash_produced"])
        self.assertFalse(hash_summary["reproducibility_claimed"])
        self.assertTrue(non_hash_summary["local_provenance_hash_is_not_sealed_hash"])

    def test_synthetic_fail_closed_matrix_and_ignored_semantics(self) -> None:
        rows = synthetic_fail_closed_matrix_rows()
        self.assertTrue(rows)
        self.assertTrue(all(row["status"] == "PASS" for row in rows))
        by_id = {row["case_id"]: row for row in rows}
        self.assertEqual(by_id["post_dirty_gt_zero"]["observed"], "blocked")
        self.assertEqual(by_id["owner_disposition_pending_gt_zero"]["observed"], "disposition_required")
        self.assertEqual(by_id["post_all_clear"]["observed"], "ready")

        blocked = derive_resolution_verdict(
            post_counts={
                "denominator_mismatch": False,
                "missing": 0,
                "dirty": 0,
                "tracked": EXPECTED_REQUIRED_ARTIFACT_COUNT,
                "untracked": 0,
                "effectively_ignored": 1,
                "tracked_but_ignore_matched": 1,
                "untracked_ignored": 0,
                "vcs_query_error": 0,
                "invalid_json": 0,
                "field_mismatch": 0,
                "missing_required_field": 0,
                "field_fail": 0,
                "non_hash_candidate": 0,
            },
            current_route_status="PASS",
            current_route_required=True,
            accepted_tracked_rule_match_count=0,
        )
        self.assertEqual(blocked["semantic_verdict"], "blocked")

        accepted = derive_resolution_verdict(
            post_counts={
                "denominator_mismatch": False,
                "missing": 0,
                "dirty": 0,
                "tracked": EXPECTED_REQUIRED_ARTIFACT_COUNT,
                "untracked": 0,
                "effectively_ignored": 1,
                "tracked_but_ignore_matched": 1,
                "untracked_ignored": 0,
                "vcs_query_error": 0,
                "invalid_json": 0,
                "field_mismatch": 0,
                "missing_required_field": 0,
                "field_fail": 0,
                "non_hash_candidate": 0,
            },
            current_route_status="PASS",
            current_route_required=True,
            accepted_tracked_rule_match_count=1,
        )
        self.assertEqual(accepted["semantic_verdict"], "ready")

    def test_current_route_collection_isolation_and_final_non_claims(self) -> None:
        collection = load_json(ROOT / "census_p7_validation/current_route_collection_isolation_report.json")
        final = load_json(ROOT / "census_p8_closeout_no_mutation/final_preflight_census_report.json")
        compatibility = load_json(ROOT / "census_p8_closeout_no_mutation/main_plan_compatibility_packet.json")

        self.assertEqual(collection["status"], "PASS")
        self.assertEqual(collection["focused_census_test_selected_count"], 0)
        self.assertEqual(collection["focused_census_test_required_count"], 0)
        self.assertFalse(collection["round_introduced_collection_regression"])
        self.assertEqual(final["status"], "PASS")
        self.assertIn(final["semantic_verdict"], {"ready", "blocked", "disposition_required"})
        self.assertEqual(final["canonical_verdict_token"], "not_claimed")
        self.assertEqual(final["independent_review_gate"], "BLOCKED")
        self.assertFalse(compatibility["does_not_claim_release_readiness"] is False)
        self.assertTrue(compatibility["does_not_claim_parent_machine_pass"])
        self.assertTrue(compatibility["does_not_claim_canonical_seal"])

        result = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
