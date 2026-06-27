from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_durable_current_authority_surface_alignment"
RUNNER = TOOLS / "run_dvf_3_3_durable_current_authority_surface_alignment.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_durable_current_authority_surface_alignment.py"
INNER_CURRENT_ROUTE = os.environ.get("DVF_DURABLE_SURFACE_INNER_CURRENT_ROUTE") == "1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfDurableCurrentAuthoritySurfaceAlignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if INNER_CURRENT_ROUTE:
            return
        final_report = ROOT / "phase7/final_durable_current_authority_surface_alignment_report.json"
        if final_report.exists():
            payload = load_json(final_report)
            if payload.get("status") == "PASS" and payload.get("machine_plan_pass") is True:
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
                "durable current authority surface alignment runner failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_inventory_tracking_and_import_boundary_pass(self) -> None:
        inventory = load_json(ROOT / "phase1/durable_surface_inventory.json")
        guard = load_json(ROOT / "phase4/vcs_durability_guard_report.json")
        import_boundary = load_json(ROOT / "phase4/current_route_import_boundary_report.json")
        reconciliation = load_json(ROOT / "phase4/current_required_evidence_reconciliation_report.json")

        self.assertEqual(inventory["status"], "PASS")
        self.assertGreater(inventory["inventory_row_count"], 0)
        self.assertEqual(inventory["unclassified_current_required_path_count"], 0)
        self.assertEqual(guard["status"], "PASS")
        self.assertEqual(guard["post_reconciliation_untracked_ignored_required_artifact_count"], 0)
        self.assertEqual(guard["governance_backbone_problem_count"], 0)
        self.assertEqual(guard["essential_guard_problem_count"], 0)
        self.assertEqual(guard["runtime_chunk_problem_count"], 0)
        self.assertEqual(import_boundary["status"], "PASS")
        self.assertEqual(import_boundary["unallowlisted_import_count"], 0)
        self.assertTrue(import_boundary["current_route_tooling_allowlist_unchanged"])
        self.assertTrue(import_boundary["current_core_closure_count_unchanged"])
        self.assertFalse(reconciliation["broad_staging_root_unignored"])
        self.assertFalse(reconciliation["non_required_staging_byproduct_tracking_requirement"])

    def test_live_manifest_adoption_is_additive_and_governance_only(self) -> None:
        adoption = load_json(ROOT / "phase5/live_manifest_adoption_report.json")
        diff = load_json(ROOT / "phase5/required_validation_manifest_diff_report.json")
        live = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")

        self.assertEqual(adoption["status"], "PASS")
        self.assertEqual(adoption["required_gate_adoption_status"], "adopted_required_gate")
        self.assertEqual(adoption["removed_existing_entries"], 0)
        self.assertEqual(adoption["modified_existing_entries"], 0)
        self.assertEqual(adoption["duplicate_entries"], 0)
        self.assertFalse(adoption["source_rendered_lua_runtime_package_authority_mutated"])
        self.assertEqual(diff["removed_existing_entries"], 0)
        self.assertEqual(diff["modified_existing_entries"], 0)
        required_tests = {row["test_id"] for row in live["required_tests"]}
        for test_id in [
            (
                "test_dvf_3_3_durable_current_authority_surface_alignment."
                "DvfDurableCurrentAuthoritySurfaceAlignmentTest."
                "test_inventory_tracking_and_import_boundary_pass"
            ),
            (
                "test_dvf_3_3_durable_current_authority_surface_alignment."
                "DvfDurableCurrentAuthoritySurfaceAlignmentTest."
                "test_live_manifest_adoption_is_additive_and_governance_only"
            ),
            (
                "test_dvf_3_3_durable_current_authority_surface_alignment."
                "DvfDurableCurrentAuthoritySurfaceAlignmentTest."
                "test_final_report_preserves_non_claims_and_bounded_sufficiency"
            ),
        ]:
            self.assertIn(test_id, required_tests)

    def test_final_report_preserves_non_claims_and_bounded_sufficiency(self) -> None:
        if INNER_CURRENT_ROUTE:
            self.assertTrue((ROOT / "phase4/vcs_durability_guard_report.json").exists())
            return

        final = load_json(ROOT / "phase7/final_durable_current_authority_surface_alignment_report.json")
        sufficiency = load_json(ROOT / "phase7/durable_surface_sufficiency_report.json")
        rendered = load_json(ROOT / "phase6/rendered_output_disposition_report.json")
        protected = load_json(ROOT / "phase6/protected_surface_no_mutation_report.json")
        review = load_json(ROOT / "phase7/independent_review_artifact_hash_report.json")

        self.assertEqual(final["status"], "PASS")
        self.assertTrue(final["machine_plan_pass"])
        self.assertEqual(final["closeout_state"], "complete_governance_only")
        self.assertEqual(final["bounded_durable_surface_sufficiency"], "PASS")
        self.assertEqual(final["durable_boundary_empirical_reproduction"], "deferred")
        self.assertTrue(final["deferred_reason_non_empty"])
        self.assertEqual(final["post_reconciliation_untracked_ignored_required_artifact_count"], 0)
        self.assertEqual(final["unallowlisted_import_count"], 0)
        self.assertEqual(final["unresolved_review_required_disposition_count"], 0)
        self.assertEqual(sufficiency["status"], "PASS")
        self.assertEqual(sufficiency["bounded_durable_surface_sufficiency"], "PASS")
        self.assertFalse(rendered["authority_claim"])
        self.assertEqual(rendered["unresolved_review_required_disposition_count"], 0)
        self.assertEqual(protected["changed_count"], 0)
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


if __name__ == "__main__":
    unittest.main()
