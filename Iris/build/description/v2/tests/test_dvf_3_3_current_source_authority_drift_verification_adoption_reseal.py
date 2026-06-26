from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_adoption_reseal"
RUNNER = TOOLS / "run_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py"
INNER_CURRENT_ROUTE = os.environ.get("DVF_ADOPTION_RESEAL_INNER_CURRENT_ROUTE") == "1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfCurrentSourceAuthorityDriftVerificationAdoptionResealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if INNER_CURRENT_ROUTE:
            return
        final_report = ROOT / "phase6/final_current_source_authority_drift_verification_adoption_reseal_report.json"
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
                "current source authority drift adoption reseal runner failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def negative_fixture_synthetic_pass(self) -> None:
        self.assertTrue(True)

    @unittest.skip("negative fixture skipped required test")
    def negative_fixture_synthetic_skip(self) -> None:
        self.fail("skip fixture should not execute")

    def test_branch_selection_contract_and_rederivation_pass(self) -> None:
        rederived = load_json(ROOT / "phase0/sealed_reseal_record_live_manifest_rederivation_report.json")
        branch = load_json(ROOT / "phase3/branch_selection_contract_report.json")
        source = load_json(ROOT / "phase2/current_source_identity_redrive_report.json")

        self.assertEqual(rederived["status"], "PASS")
        self.assertTrue(rederived["live_manifest_consumes_drift_via_evidence_freshness_reseal"])
        self.assertFalse(rederived["sealed_live_divergence_detected"])
        self.assertEqual(branch["status"], "PASS")
        self.assertEqual(branch["selected_branch"], "branch_a_required_gate_adopted")
        self.assertTrue(branch["owner_decision_after_machine_predicates"])
        self.assertEqual(source["status"], "PASS")
        self.assertEqual(source["authority_role"], "successor_current_source_authority")
        self.assertEqual(source["successor_universe_count"], 2105)

    def test_live_manifest_adoption_is_additive_and_governance_only(self) -> None:
        adoption = load_json(ROOT / "phase3/live_manifest_adoption_report.json")
        single_writer = load_json(ROOT / "phase3/live_manifest_single_writer_report.json")
        taxonomy = load_json(ROOT / "phase3/taxonomy_single_writer_report.json")
        separation = load_json(ROOT / "phase3/taxonomy_separation_additive_compatibility_report.json")
        b_marker = load_json(ROOT / "phase3/b_marked_schema_supported_marker_validation_report.json")
        live = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")

        self.assertEqual(adoption["status"], "PASS")
        self.assertEqual(adoption["required_gate_adoption_status"], "adopted_required_gate")
        self.assertEqual(adoption["removed_existing_entries"], 0)
        self.assertEqual(adoption["modified_existing_entries"], 0)
        self.assertEqual(adoption["duplicate_entries"], 0)
        self.assertFalse(adoption["source_runtime_package_authority_mutated"])
        self.assertEqual(single_writer["status"], "PASS")
        self.assertEqual(taxonomy["taxonomy_writer_mode"], "non_writer_required_manifest_union")
        self.assertFalse(taxonomy["taxonomy_mutated"])
        self.assertTrue(separation["evidence_freshness_reseal_taxonomy_separation_preserved"])
        self.assertFalse(separation["runtime_authority_mutation"])
        self.assertEqual(b_marker["applicability"], "not_applicable_selected_branch_a")
        required_tests = {row["test_id"] for row in live["required_tests"]}
        for test_id in [
            (
                "test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal."
                "DvfCurrentSourceAuthorityDriftVerificationAdoptionResealTest."
                "test_branch_selection_contract_and_rederivation_pass"
            ),
            (
                "test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal."
                "DvfCurrentSourceAuthorityDriftVerificationAdoptionResealTest."
                "test_live_manifest_adoption_is_additive_and_governance_only"
            ),
            (
                "test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal."
                "DvfCurrentSourceAuthorityDriftVerificationAdoptionResealTest."
                "test_negative_fixture_matrix_passes_without_live_mutation"
            ),
        ]:
            self.assertIn(test_id, required_tests)

    def test_negative_fixture_matrix_passes_without_live_mutation(self) -> None:
        matrix = load_json(ROOT / "phase6/negative_fixture_matrix_report.json")

        self.assertEqual(matrix["status"], "PASS")
        self.assertFalse(matrix["live_manifest_mutated"])
        fixtures = {row["fixture"]: row for row in matrix["fixtures"]}
        for fixture, error_code in {
            "missing_artifact": "missing_required_artifact",
            "field_mismatch": "required_artifact_field_mismatch",
            "skipped_required_test": "skipped_required_test",
        }.items():
            self.assertIn(fixture, fixtures)
            self.assertEqual(fixtures[fixture]["status"], "PASS")
            self.assertTrue(fixtures[fixture]["expected_failure_preserved"])
            self.assertFalse(fixtures[fixture]["live_mutation_performed"])
            self.assertEqual(fixtures[fixture]["expected_error_code"], error_code)
            self.assertIn(error_code, fixtures[fixture]["observed_runner"]["observed_error_codes"])

    def test_final_report_preserves_scope_ceiling_and_guard_checklist(self) -> None:
        if INNER_CURRENT_ROUTE:
            self.assertTrue((ROOT / "phase3/branch_selection_contract_report.json").exists())
            return

        final = load_json(ROOT / "phase6/final_current_source_authority_drift_verification_adoption_reseal_report.json")
        checklist = load_json(ROOT / "phase5/implementation_compression_guard_checklist.json")
        owner = load_json(ROOT / "phase6/owner_seal_report.json")
        review = load_json(ROOT / "phase6/independent_review_artifact_hash_report.json")

        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["selected_branch"], "branch_a_required_gate_adopted")
        self.assertEqual(final["closeout_state"], "current_source_authority_drift_adoption_reseal_complete")
        self.assertEqual(final["clean_checkout_reproducibility_proof_status"], "out_of_scope_not_claimed")
        self.assertEqual(final["original_required_evidence_reproducibility_preflight_status"], "not_closed_by_this_plan")
        self.assertIn("plan-structure PASS", final["plan_structure_pass_limitation"])
        self.assertEqual(final["protected_source_rendered_lua_runtime_package_changed_count"], 0)
        self.assertEqual(checklist["status"], "PASS")
        self.assertEqual(checklist["omitted_required_guard_count"], 0)
        self.assertEqual(owner["owner_seal_status"], "PASS")
        self.assertEqual(review["status"], "PASS")
        self.assertEqual(review["mismatch_count"], 0)

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


if __name__ == "__main__":
    unittest.main()
