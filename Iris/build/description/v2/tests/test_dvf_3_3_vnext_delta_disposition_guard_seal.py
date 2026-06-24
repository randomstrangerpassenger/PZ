from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal"
SCRIPT = REPO / "Iris/build/description/v2/tools/build/build_dvf_3_3_vnext_delta_disposition_guard_seal.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class DvfVnextDeltaDispositionGuardSealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            ["python", "-B", str(SCRIPT)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)

    def test_phase1_binds_sealed_per_row_delta_source_without_rediff(self) -> None:
        verdict = load_json(ROOT / "phase1/per_row_delta_source_verdict.json")
        self.assertEqual(verdict["status"], "PASS")
        self.assertTrue(verdict["source_exists"])
        self.assertTrue(verdict["sealed_2_4a_bound"])
        self.assertFalse(verdict["re_diff_used"])
        self.assertEqual(verdict["axis_expanded_text_ko_delta_count"], 2071)
        self.assertEqual(verdict["axis_expanded_state_delta_count"], 54)
        self.assertEqual(verdict["axis_expanded_delta_row_count"], 2125)

    def test_disposition_coverage_and_runtime_eligibility_are_closed(self) -> None:
        summary = load_json(ROOT / "phase4/disposition_summary.json")
        coverage = load_json(ROOT / "phase4/disposition_coverage_report.json")
        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["total_count"], 2125)
        self.assertEqual(summary["disposition_counts"], {"approved": 2017, "rejected": 108})
        self.assertEqual(summary["runtime_eligible_count"], 2017)
        self.assertEqual(coverage["undispositioned_count"], 0)
        self.assertEqual(coverage["ambiguous_count"], 0)
        self.assertEqual(coverage["missing_reviewer_identity_count"], 0)

        ledger = load_jsonl(ROOT / "phase4/delta_disposition_ledger.jsonl")
        self.assertTrue(all(row["disposition"] in {"approved", "rejected"} for row in ledger))
        self.assertFalse(any(row["disposition"] == "rejected" and row["runtime_eligible"] for row in ledger))

    def test_publish_state_branch_b_is_excluded_from_classification(self) -> None:
        report = load_json(ROOT / "phase3/publish_state_axis_disposition_report.json")
        self.assertEqual(report["publish_state_branch"], "B")
        self.assertTrue(report["classification_scope_excluded"])
        self.assertFalse(report["policy_mutation"])
        self.assertFalse(report["payload_equality_reopened"])
        self.assertEqual(report["classified_delta_denominator"], 2125)
        self.assertEqual(report["legacy_axis_disposition_count"], 2105)
        self.assertEqual(report["unaccounted_parity_axis_count"], 0)

    def test_guard_matrix_dual_zero_and_negative_cases_pass(self) -> None:
        matrix = load_json(ROOT / "phase6/guard_surface_matrix.json")
        dual_zero = load_json(ROOT / "phase8/dual_zero_verification_report.json")
        negative = load_json(ROOT / "phase8/negative_test_results.json")
        self.assertEqual(matrix["status"], "PASS")
        self.assertEqual(matrix["guard_count"], 8)
        self.assertEqual(dual_zero["status"], "PASS")
        self.assertEqual(dual_zero["static_forbidden_current_surface_hit_count"], 0)
        self.assertEqual(dual_zero["static_unclassified_residue_count"], 0)
        self.assertEqual(dual_zero["dynamic_forbidden_reach_count"], 0)
        self.assertTrue(dual_zero["allowed_non_current_residue_disposition_complete"])
        self.assertEqual(negative["status"], "PASS")
        self.assertEqual(negative["expected_fail_loud_count"], negative["observed_fail_loud_count"])

    def test_phase9_manifest_is_index_only_and_rejected_rows_are_absent(self) -> None:
        manifest = load_json(ROOT / "phase9/approved_cutover_input_delta_manifest.json")
        rejected_absence = load_json(ROOT / "phase9/rejected_delta_absence_from_cutover_input_report.json")
        self.assertTrue(manifest["manifest_index_only"])
        self.assertFalse(manifest["payload_generated"])
        self.assertFalse(manifest["cutover_input_usable"])
        self.assertEqual(manifest["approved_count"], 2017)
        self.assertEqual(manifest["rejected_count"], 108)
        self.assertEqual(rejected_absence["status"], "PASS")
        self.assertEqual(rejected_absence["rejected_present_in_approved_manifest_count"], 0)

    def test_final_contract_separates_guard_completion_from_cutover_usability(self) -> None:
        report = load_json(ROOT / "phase10/final_delta_disposition_guard_contract_report.json")
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["disposition_guard_seal_complete"])
        self.assertFalse(report["cutover_input_usable"])
        self.assertEqual(report["terminal"], "complete_disposition_guard_sealed_cutover_input_blocked")
        self.assertIn("no_current_cutover", report["non_claims"])


if __name__ == "__main__":
    unittest.main()
