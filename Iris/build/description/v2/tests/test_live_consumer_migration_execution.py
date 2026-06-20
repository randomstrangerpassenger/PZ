from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_live_consumer_migration_execution"
SCRIPT = TOOLS / "run_dvf_3_3_live_consumer_migration_execution.py"

sys.path.insert(0, str(TOOLS))

from dvf_3_3_live_consumer_migration_execution_common import validate_all  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class LiveConsumerMigrationExecutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "live consumer migration execution generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_phase1_reconciles_153_and_163_by_identity(self) -> None:
        report = load_json(ROOT / "phase1/migrated153_vs_sandbox163_reconciliation_report.json")
        disposition = load_json(ROOT / "phase1/reconciliation_set_difference_disposition.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["migrated_count"], 153)
        self.assertEqual(report["sandbox_mutation_count"], 163)
        self.assertEqual(report["migrated153_minus_sandbox163_count"], 0)
        self.assertEqual(report["sandbox163_minus_migrated153_count"], 10)
        self.assertTrue(all(row["forbidden_for_live_mutation"] for row in disposition["sandbox163_minus_migrated153"]))

    def test_phase2_splits_live_writable_and_evidence_only_rows(self) -> None:
        summary = load_json(ROOT / "phase2/live_target_derivation_summary.json")
        excluded = load_jsonl(ROOT / "phase2/excluded_non_live_target_ledger.jsonl")
        required = load_jsonl(ROOT / "phase2/live_mutation_required_ledger.jsonl")

        self.assertEqual(summary["total_migrated_rows"], 153)
        self.assertEqual(summary["live_mutation_required_count"], 109)
        self.assertEqual(summary["excluded_non_live_target_count"], 44)
        self.assertEqual(len(required), 109)
        self.assertEqual(len(excluded), 44)
        self.assertTrue(all(row["hard_forbidden_authority_surface"] for row in excluded))
        self.assertFalse(any(row["hard_forbidden_authority_surface"] for row in required))

    def test_phase3_blocks_live_apply_on_dirty_target_overlap(self) -> None:
        pre_apply = load_json(ROOT / "phase3/pre_apply_gate_report.json")
        isolation = load_json(ROOT / "phase3/dirty_target_isolation_report.json")
        patch_bundle = load_json(ROOT / "phase3/frozen_patch_bundle.json")
        apply_ledger = load_jsonl(ROOT / "phase4/live_apply_ledger.jsonl")
        apply_integrity = load_json(ROOT / "phase4/apply_integrity_report.json")

        self.assertEqual(pre_apply["status"], "BLOCKED")
        self.assertIn("blocked_dirty_target_overlap", pre_apply["block_codes"])
        self.assertNotIn("blocked_anchor_drift", pre_apply["block_codes"])
        self.assertEqual(pre_apply["anchor_drift_row_count"], 0)
        self.assertGreaterEqual(isolation["dirty_target_overlap_count"], 1)
        self.assertTrue(patch_bundle["line_grouped_patch_bundle"])
        self.assertEqual(patch_bundle["authorization_row_count"], 109)
        self.assertLess(patch_bundle["line_patch_count"], patch_bundle["authorization_row_count"])
        self.assertEqual(apply_ledger, [])
        self.assertEqual(apply_integrity["status"], "BLOCKED")

    def test_frozen_patch_bundle_rederives_current_line_anchors(self) -> None:
        patch_bundle = load_json(ROOT / "phase3/frozen_patch_bundle.json")
        rows = patch_bundle["rows"]
        runtime_line = next(
            row
            for row in rows
            if row["path"] == "Iris/build/description/v2/tools/build/validate_body_plan_full_runtime_regression_gate.py"
            and row["line"] == 63
        )
        volatile_rows = [row for row in rows if row.get("volatile_snapshot_artifact")]

        self.assertEqual(runtime_line["line_grouped_authorization_row_count"], 2)
        self.assertEqual(runtime_line["operation_kind"], "replace_line_exact_line_group")
        self.assertIn("DVF_AUTHORITY_ROLE_MIGRATION[f613f10e573175b7b39fa4ca00cd1d05]", runtime_line["after_anchor"])
        self.assertIn("DVF_AUTHORITY_ROLE_MIGRATION[cc544d465ae83b3be43b64e30cc02839]", runtime_line["after_anchor"])
        self.assertEqual(len(volatile_rows), 3)
        self.assertTrue(all(row["volatile_snapshot_exact_stdout_match_required"] is False for row in volatile_rows))
        self.assertTrue(all(row["line_grouped_authorization_row_count"] == 2 for row in volatile_rows))

    def test_phase5_and_closeout_do_not_count_sandbox_as_live_completion(self) -> None:
        separation = load_json(ROOT / "phase5/sandbox_live_separation_report.json")
        hard_forbidden = load_json(ROOT / "phase5/hard_forbidden_authority_surface_no_mutation_verdict.json")
        final = load_json(ROOT / "phase8/final_live_migration_execution_report.json")
        closeout = (REPO / "docs/dvf_3_3_live_consumer_migration_execution_closeout.md").read_text(encoding="utf-8").lower()

        self.assertEqual(separation["readiness_sandbox_mutation_rows_counted_as_live_completion"], 0)
        self.assertEqual(hard_forbidden["hard_forbidden_authority_surface_changed_count"], 0)
        self.assertEqual(final["status"], "BLOCKED")
        self.assertFalse(final["complete_seal_allowed"])
        self.assertFalse(final["sandbox_readiness_evidence_counted_as_live_completion"])
        self.assertIn("not counted as live completion", closeout)
        self.assertIn("no current authority recutover", closeout)
        self.assertIn("no release readiness", closeout)

    def test_validator_accepts_blocked_evidence_but_not_complete_claim(self) -> None:
        report, ok = validate_all(require_complete=False)
        complete_report, complete_ok = validate_all(require_complete=True, write_report=False)
        complete_codes = {error["code"] for error in complete_report["errors"]}

        self.assertTrue(ok, report["errors"])
        self.assertFalse(complete_ok)
        self.assertIn("complete_required_but_not_complete", complete_codes)
        self.assertIn("complete_required_pre_apply_not_pass", complete_codes)


if __name__ == "__main__":
    unittest.main()
