from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity"
SCRIPT = REPO / "Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_rejected_delta_correction_reparity.py"
REQUIRED_MANIFEST = REPO / "Iris/_docs/round3/current_route_required_validations.json"
PRIOR_FINAL = (
    "Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/"
    "phase10/final_delta_disposition_guard_contract_report.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class DvfVnextRejectedDeltaCorrectionReparityTest(unittest.TestCase):
    live_manifest_before: dict | None = None
    live_manifest_after: dict | None = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.live_manifest_before = load_json(REQUIRED_MANIFEST) if REQUIRED_MANIFEST.exists() else None
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        cls.live_manifest_after = load_json(REQUIRED_MANIFEST) if REQUIRED_MANIFEST.exists() else None

    def test_corrected_reparity_removes_state_rejections_and_preserves_control_set(self) -> None:
        inventory = load_jsonl(ROOT / "phase1/rejected_54_key_inventory.jsonl")
        controls = load_jsonl(ROOT / "phase1/silent_non_rejected_control_set.jsonl")
        application = load_json(ROOT / "phase5/correction_application_report.json")
        parity = load_json(ROOT / "phase7/runtime_parity_report.json")
        maintain = load_json(ROOT / "phase7/predecessor_maintain_realization_report.json")

        self.assertEqual(len(inventory), 54)
        self.assertEqual(len(controls), 21)
        self.assertEqual(application["status"], "PASS")
        self.assertEqual(application["applied_change_count"], 54)
        self.assertEqual(application["silent_control_changed_count"], 0)
        self.assertEqual(parity["status"], "PASS")
        self.assertEqual(parity["predecessor"]["entry_count"], 2105)
        self.assertEqual(parity["vnext"]["entry_count"], 2105)
        self.assertEqual(parity["key_parity"]["missing_in_vnext_count"], 0)
        self.assertEqual(parity["key_parity"]["additional_in_vnext_count"], 0)
        self.assertEqual(parity["field_parity"]["state_delta_count"], 0)
        self.assertEqual(maintain["status"], "PASS")
        self.assertEqual(maintain["checked_count"], 54)
        self.assertEqual(maintain["failure_count"], 0)

    def test_re_disposition_establishes_cutover_usable_candidate(self) -> None:
        final = load_json(ROOT / "phase8/final_delta_disposition_guard_contract_report.json")
        approved_manifest = load_json(ROOT / "phase8/approved_cutover_input_delta_manifest.json")
        usability = load_json(ROOT / "phase8/cutover_input_usability_report.json")
        redisposition = load_json(ROOT / "phase8/re_disposition_validation_report.json")

        self.assertEqual(final["status"], "PASS")
        self.assertTrue(final["cutover_input_usable"])
        self.assertTrue(final["parent_problem_unlock"])
        self.assertEqual(final["counts"]["rejected_count"], 0)
        self.assertEqual(final["counts"]["deferred_count"], 0)
        self.assertEqual(final["counts"]["scope_exclusion_count"], 0)
        self.assertEqual(final["counts"]["unresolved_policy_candidate_count"], 0)
        self.assertEqual(final["counts"]["state_delta_count"], 0)
        self.assertTrue(approved_manifest["manifest_index_only"])
        self.assertFalse(approved_manifest["payload_generated"])
        self.assertFalse(approved_manifest["approved_set_is_cutover_authorization"])
        self.assertTrue(approved_manifest["cutover_input_usable"])
        self.assertEqual(approved_manifest["rejected_count"], 0)
        self.assertEqual(usability["status"], "PASS")
        self.assertEqual(redisposition["status"], "PASS")

    def test_current_route_required_validation_manifest_uses_new_evidence(self) -> None:
        manifest = load_json(ROOT / "phase9/current_route_required_validation_report.json")
        freshness = load_json(ROOT / "phase9/required_validation_manifest_freshness_report.json")
        disposition = load_json(ROOT / "phase9/current_route_required_validation_manifest_disposition.json")
        required_paths = {row["path"] for row in manifest["required_artifacts"]}
        required_ids = {row["test_id"] for row in manifest["required_tests"]}

        self.assertEqual(self.live_manifest_after, self.live_manifest_before)
        self.assertFalse(disposition["live_required_validation_manifest_mutated"])
        self.assertTrue(manifest["required"])
        self.assertEqual(manifest["enforcement"], "fail_closed")
        self.assertIn(
            "Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/"
            "phase8/final_delta_disposition_guard_contract_report.json",
            required_paths,
        )
        self.assertNotIn(PRIOR_FINAL, required_paths)
        self.assertEqual(freshness["status"], "PASS")
        self.assertTrue(freshness["phase8_final_report_referenced"])
        self.assertFalse(freshness["stale_prior_final_report_reference"])
        self.assertFalse(freshness["live_required_validation_manifest_mutated"])
        self.assertIn(
            "test_dvf_3_3_vnext_rejected_delta_correction_reparity."
            "DvfVnextRejectedDeltaCorrectionReparityTest."
            "test_corrected_reparity_removes_state_rejections_and_preserves_control_set",
            required_ids,
        )
        self.assertIn(
            "test_dvf_3_3_vnext_rejected_delta_correction_reparity."
            "DvfVnextRejectedDeltaCorrectionReparityTest."
            "test_final_report_establishes_candidate_unlock_without_cutover_claim",
            required_ids,
        )

    def test_final_report_establishes_candidate_unlock_without_cutover_claim(self) -> None:
        report = load_json(ROOT / "phase11/final_rejected_delta_correction_reparity_report.json")
        claim = load_json(ROOT / "phase11/claim_boundary_check.json")
        closeout = (REPO / "docs/dvf_3_3_vnext_rejected_delta_correction_reparity_closeout.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["cutover_input_usable"])
        self.assertTrue(report["parent_problem_unlock"])
        self.assertTrue(report["not_cutover_authorization"])
        self.assertEqual(report["counts"]["rejected_count"], 0)
        self.assertEqual(report["counts"]["deferred_count"], 0)
        self.assertEqual(claim["status"], "PASS")
        self.assertEqual(claim["forbidden_claim_hit_count"], 0)
        self.assertIn("not a cutover authorization", closeout)
        self.assertIn("no live runtime chunk replacement", closeout)
        self.assertIn("COMMON-RELEASE-NONDECISION", closeout)


if __name__ == "__main__":
    unittest.main()
