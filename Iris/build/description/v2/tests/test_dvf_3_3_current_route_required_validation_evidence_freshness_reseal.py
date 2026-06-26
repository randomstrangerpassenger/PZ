from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal"
RUNNER = TOOLS / "run_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py"
INNER_CURRENT_ROUTE = os.environ.get("DVF_RESEAL_INNER_CURRENT_ROUTE") == "1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if INNER_CURRENT_ROUTE:
            return
        final_report = ROOT / "phase6/final_current_route_required_validation_evidence_freshness_reseal_report.json"
        if final_report.exists():
            payload = load_json(final_report)
            if payload.get("status") == "PASS" and payload.get("machine_contract_status") == "PASS":
                return
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "machine-pass"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "required-validation evidence freshness reseal runner failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def negative_fixture_synthetic_pass(self) -> None:
        self.assertTrue(True)

    @unittest.skip("negative fixture skipped required test")
    def negative_fixture_synthetic_skip(self) -> None:
        self.fail("skip fixture should not execute")

    def test_current_source_identity_redrive_and_drift_field_check_pass(self) -> None:
        source = load_json(ROOT / "phase2/current_checkout_source_identity_redrive_report.json")
        drift = load_json(ROOT / "phase2/drift_verification_field_check_report.json")

        self.assertEqual(source["status"], "PASS")
        self.assertEqual(source["authority_role"], "successor_current_source_authority")
        self.assertEqual(source["successor_universe_count"], 2105)
        self.assertTrue(source["checks"]["facts_match_manifest"])
        self.assertTrue(source["checks"]["decisions_match_manifest"])
        self.assertTrue(source["checks"]["overlay_match_manifest"])
        self.assertEqual(drift["status"], "PASS")
        self.assertEqual(drift["mismatch_count"], 0)
        self.assertEqual(drift["drift_evidence_role"], "read_only_governance_evidence")

    def test_live_manifest_update_is_additive_and_governance_only(self) -> None:
        update = load_json(ROOT / "phase3/live_required_manifest_update_report.json")
        taxonomy = load_json(ROOT / "phase3/taxonomy_separation_report.json")
        diff = load_json(ROOT / "phase3/additive_diff_bijection_report.json")
        live = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")

        self.assertEqual(update["status"], "PASS")
        self.assertEqual(update["removed_existing_entries"], 0)
        self.assertEqual(update["modified_existing_entries"], 0)
        self.assertEqual(update["duplicate_entries"], 0)
        self.assertFalse(update["source_runtime_package_authority_mutated"])
        self.assertFalse(update["candidate_manifest_adopted"])
        self.assertEqual(taxonomy["status"], "PASS")
        self.assertFalse(taxonomy["runtime_authority_mutation"])
        self.assertEqual(taxonomy["external_bundle_reseal_requirement_surface"], "wrapper_final_validation")
        self.assertEqual(diff["status"], "PASS")
        required_tests = {row["test_id"] for row in live["required_tests"]}
        current_route_test = (
            "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
            "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest."
            "test_current_source_identity_redrive_and_drift_field_check_pass"
        )
        post_run_tests = {
            (
                "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
                "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest."
                "test_external_bundle_and_final_report_are_fresh_when_not_in_inner_runner"
            ),
            (
                "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal."
                "DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest."
                "test_final_state_keeps_machine_pass_separate_from_canonical_complete"
            ),
        }
        self.assertIn(current_route_test, required_tests)
        self.assertFalse(required_tests.intersection(post_run_tests))

    def test_external_bundle_and_final_report_are_fresh_when_not_in_inner_runner(self) -> None:
        if INNER_CURRENT_ROUTE:
            self.assertTrue((ROOT / "phase3/additive_diff_bijection_report.json").exists())
            return

        bundle = load_json(ROOT / "phase5/external_validation_bundle_manifest.json")
        hash_report = load_json(ROOT / "phase5/external_validation_bundle_hash_report.json")
        freshness = load_json(ROOT / "phase5/external_validation_bundle_freshness_report.json")
        final = load_json(ROOT / "phase6/final_current_route_required_validation_evidence_freshness_reseal_report.json")

        self.assertEqual(bundle["status"], "PASS")
        self.assertEqual(bundle["normalized_content_sha256"], hash_report["bundle_normalized_content_sha256"])
        self.assertTrue(hash_report["bundle_normalized_hash_matches_manifest"])
        self.assertEqual(freshness["status"], "PASS")
        self.assertTrue(freshness["external_bundle_target_matches_phase0_pin"])
        self.assertTrue(freshness["bundle_readpoint_matches_runner_output"])
        self.assertTrue(freshness["bundle_manifest_hash_matches_live_manifest_hash"])
        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["external_bundle_freshness_status"], "PASS")
        self.assertEqual(final["missing_required_test_count"], 0)
        self.assertEqual(final["skipped_required_test_count"], 0)
        self.assertEqual(final["failed_required_test_count"], 0)
        self.assertEqual(final["failed_required_artifact_field_check_count"], 0)

    def test_negative_fixtures_remain_fail_closed_without_live_mutation(self) -> None:
        if INNER_CURRENT_ROUTE and not (ROOT / "phase1/harness_negative_fixture_matrix.json").exists():
            self.assertTrue((ROOT / "phase3/additive_diff_bijection_report.json").exists())
            return

        matrix = load_json(ROOT / "phase1/harness_negative_fixture_matrix.json")

        self.assertEqual(matrix["status"], "PASS")
        self.assertFalse(matrix["live_manifest_mutated"])
        fixtures = {row["fixture"]: row for row in matrix["fixtures"]}
        for fixture in {
            "known_stale_bundle",
            "candidate_manifest_reference",
            "skipped_required_test",
            "failed_field_check",
        }:
            self.assertIn(fixture, fixtures)
            self.assertTrue(fixtures[fixture]["expected_failure_preserved"])
            self.assertFalse(fixtures[fixture]["live_mutation_performed"])
            self.assertIn("expected_error_code", fixtures[fixture])
        for fixture in {"known_stale_bundle", "skipped_required_test", "failed_field_check"}:
            observed = fixtures[fixture]["observed_runner"]
            self.assertNotEqual(observed["exit_code"], 0)
            self.assertIn(fixtures[fixture]["expected_error_code"], observed["observed_error_codes"])
            self.assertFalse(fixtures[fixture]["observed_wrapper_guard"])
        candidate_guard = fixtures["candidate_manifest_reference"]["observed_wrapper_guard"]
        self.assertEqual(candidate_guard["observed_status"], "FAIL")
        self.assertEqual(candidate_guard["observed_error_code"], "candidate_manifest_override_surface_absent")
        self.assertNotEqual(candidate_guard["actual_wrapper_exit_code"], 0)
        self.assertIn("--required-validations", candidate_guard["actual_wrapper_stderr_tail"])
        self.assertEqual(fixtures["candidate_manifest_reference"]["observed_runner"]["exit_code"], 0)

    def test_final_state_keeps_machine_pass_separate_from_canonical_complete(self) -> None:
        if INNER_CURRENT_ROUTE:
            self.assertTrue((ROOT / "phase2/owner_reserved_decision_gate_report.json").exists())
            return

        final = load_json(ROOT / "phase6/final_current_route_required_validation_evidence_freshness_reseal_report.json")
        review = load_json(ROOT / "phase6/independent_review_artifact_hash_report.json")
        owner_seal = load_json(ROOT / "phase6/owner_seal_report.json")

        self.assertEqual(final["evidence_freshness_reseal_closeout_state"], "complete")
        self.assertFalse(final["standalone_complete_claimed"])
        self.assertTrue(final["canonical_complete_allowed"])
        self.assertEqual(final["independent_review_status"], "PASS")
        self.assertEqual(final["owner_seal_status"], "PASS")
        self.assertTrue(final["canonical_complete_requirements"]["machine_validation_pass"])
        self.assertTrue(final["canonical_complete_requirements"]["non_claude_independent_review_pass"])
        self.assertTrue(final["canonical_complete_requirements"]["owner_seal_pass"])
        self.assertEqual(owner_seal["status"], "PASS")
        self.assertEqual(owner_seal["owner_seal_status"], "PASS")
        self.assertTrue(owner_seal["canonical_complete_allowed"])
        self.assertFalse(final["post_run_surface_tests_are_current_route_required"])
        self.assertEqual(final["post_run_surface_tests_in_live_manifest"], [])
        self.assertEqual(review["status"], "PASS")
        self.assertEqual(review["mismatch_count"], 0)
        self.assertEqual(review["independent_review_status"], "PASS")
        self.assertEqual(review["owner_seal_status"], "PASS")
        self.assertTrue(review["canonical_complete_allowed"])

        result = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), "--require-complete"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(ROOT / "phase6/validation_report.require_complete.json")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["error_count"], 0)
        self.assertEqual(report["validation_report_scope"], "machine_pass_artifact_set_and_owner_sealed_canonical_closeout")
        self.assertEqual(report["require_complete_semantics"], "complete_machine_pass_artifact_set_plus_axis_qualified_canonical_seal_state")
        self.assertTrue(report["canonical_complete_claimed"])
        self.assertTrue(report["canonical_complete_allowed"])
        self.assertTrue(report["independent_review_required_for_canonical_complete"])
        self.assertTrue(report["owner_seal_required_for_canonical_complete"])


if __name__ == "__main__":
    unittest.main()
