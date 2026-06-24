from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SCRIPT = REPO / "Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py"
ROOT = REPO / "Iris/build/description/v2/staging/runtime_payload_state_integrity"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class RuntimePayloadStateIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--mode", "validate"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(f"runtime payload state integrity generation failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

    def test_phase0_inventory_resolves_current_payload_shape(self) -> None:
        inventory = load_json(ROOT / "phase0/runtime_payload_state_inventory.json")
        field_identity = load_json(ROOT / "phase0/field_identity_resolution.json")
        publish = load_json(ROOT / "phase0/publish_state_authority_resolution.json")
        unadopted = load_jsonl(ROOT / "phase0/unadopted_payload_rows.jsonl")

        self.assertEqual(inventory["status"], "PASS")
        self.assertEqual(inventory["current_runtime_entry_count"], 2105)
        self.assertEqual(inventory["current_runtime_unadopted_count"], 21)
        self.assertEqual(inventory["current_like_forbidden_count"], 0)
        self.assertEqual(inventory["current_like_unclassified_count"], 0)
        self.assertEqual(inventory["runtime_rendered_missing_count"], 0)
        self.assertEqual(inventory["runtime_extra_key_count"], 0)
        self.assertEqual(len(unadopted), 21)
        self.assertTrue(all(row["text_ko_value_state"] in {"missing", "null_or_nil"} for row in unadopted))
        self.assertTrue(all(row["publish_axis"] == "missing" for row in unadopted))

        self.assertEqual(field_identity["status"], "PASS")
        self.assertEqual(field_identity["runtime_state_present_count"], 0)
        self.assertEqual(field_identity["adoption_state_present_count"], 0)
        self.assertEqual(field_identity["source_value_counts"]["unadopted"], 21)
        self.assertEqual(publish["status"], "PASS")
        self.assertEqual(publish["current_like_publish_state_row_count"], 0)
        self.assertGreaterEqual(publish["predecessor_residue_count"], 2)

    def test_matrix_and_validator_fail_closed_without_runtime_mutation(self) -> None:
        matrix = load_json(ROOT / "phase3/runtime_payload_shape_matrix.json")
        validation = load_json(ROOT / "phase4/payload_shape_validation_report.json")
        guard = load_json(ROOT / "phase4/current_route_payload_state_guard_report.json")
        dual_zero = load_json(ROOT / "phase4/dual_zero_payload_shape_guard_report.json")
        no_mutation = load_json(ROOT / "phase4/protected_surface_no_mutation_verdict.json")
        negative = load_json(ROOT / "phase4/negative_forbidden_combination_fixture_report.json")

        self.assertEqual(matrix["status"], "PASS")
        self.assertEqual(matrix["forbidden_current_like_count"], 0)
        self.assertEqual(matrix["unclassified_current_like_count"], 0)
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(validation["negative_fixture"]["forbidden_fixture_count"], 1)
        self.assertEqual(negative["forbidden_fixture_count"], 1)
        self.assertEqual(guard["status"], "PASS")
        self.assertEqual(guard["static_forbidden_current_count"], 0)
        self.assertEqual(guard["static_unclassified_current_count"], 0)
        self.assertEqual(guard["dynamic_forbidden_reach_count"], 0)
        self.assertEqual(dual_zero["status"], "PASS")
        self.assertEqual(dual_zero["static_forbidden_current_count"], 0)
        self.assertEqual(no_mutation["status"], "PASS")
        self.assertEqual(no_mutation["changed_count"], 0)

    def test_runtime_consumer_and_closeout_preserve_governance_gates(self) -> None:
        display = load_json(ROOT / "phase5b/display_resolution_parity_report.json")
        closeout = (REPO / "docs/runtime_payload_state_integrity_closeout.md").read_text(encoding="utf-8")
        contract = (REPO / "docs/runtime_payload_shape_contract.md").read_text(encoding="utf-8")
        independent = (ROOT / "phase7/independent_review.md").read_text(encoding="utf-8")
        author_record = (ROOT / "phase2/author_reserved_branch_decision_record.md").read_text(encoding="utf-8")

        self.assertEqual(display["status"], "PASS")
        self.assertEqual(display["checked_key_count"], 21)
        self.assertEqual(display["display_body_present_count"], 0)
        self.assertIn("implemented_guard_pass_author_review_pending", closeout)
        self.assertIn("author-reserved", closeout)
        self.assertIn("independent review", closeout)
        self.assertIn("Runtime Lua remains a renderer", contract)
        self.assertIn("blocked_external_gate", independent)
        self.assertIn("pending_author_selection", author_record)


if __name__ == "__main__":
    unittest.main()
