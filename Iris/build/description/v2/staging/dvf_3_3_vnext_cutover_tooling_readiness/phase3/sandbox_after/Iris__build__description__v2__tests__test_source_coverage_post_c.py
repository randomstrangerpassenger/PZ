from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_source_coverage_post_c import (
    build_hold_note,
    build_post_c_note,
    build_post_c_summary,
)


class SourceCoveragePostCTest(unittest.TestCase):
    def test_post_c_projection_matches_current_staged_packages(self) -> None:
        summary = build_post_c_summary()

        self.assertEqual(summary["package_totals"]["package_count"], 10)
        self.assertEqual(summary["package_totals"]["item_count"], 466)
        self.assertEqual(summary["package_totals"]["gate_pass_count"], 10)
        self.assertEqual(summary["package_totals"]["gate_fail_count"], 0)
        self.assertEqual(summary["replacement_totals"]["package_count"], 2)
        self.assertEqual(summary["replacement_totals"]["ready_row_count"], 12)
        self.assertEqual(summary["replacement_totals"]["parked_row_count"], 3)
        self.assertEqual(
            summary["replacement_totals"]["path_count_delta"],
            {
                "cluster_summary": 0,
                "direct_use": 12,
                "identity_fallback": 0,
                "role_fallback": -12,
            },
        )
        self.assertEqual(
            summary["package_totals"]["use_source_counts"],
            {
                "cluster_summary": 466,
                "direct_use": 0,
                "identity_fallback": 0,
                "role_fallback": 0,
            },
        )
        self.assertEqual(
            summary["projected_runtime"]["path_counts"],
            {
                "cluster_summary": 1275,
                "direct_use": 12,
                "identity_fallback": 718,
                "role_fallback": 100,
            },
        )
        self.assertEqual(summary["projected_runtime"]["replacement_applied_count"], 12)
        self.assertEqual(summary["projected_runtime"]["projected_runtime_row_count"], 2105 DVF_AUTHORITY_ROLE_MIGRATION[5226d2288963ac77b31c95b9469ebde6]) DVF_AUTHORITY_ROLE_MIGRATION[5226d2288963ac77b31c95b9469ebde6]
        self.assertEqual(summary["projected_runtime"]["projected_active_count"], 2030)
        self.assertEqual(summary["projected_runtime"]["projected_silent_count"], 75)
        self.assertEqual(summary["direct_use_decision"]["status"], "artifact_backed_replacement_lane")
        self.assertEqual(summary["remaining_uncovered_after_staged_c"]["item_count"], 180)
        self.assertEqual(
            summary["remaining_uncovered_after_staged_c"]["hold_subset_ids"],
            ["C1-H1", "C1-H2", "C1-RH"],
        )

    def test_notes_capture_hold_transition(self) -> None:
        summary = build_post_c_summary()

        post_c_note = build_post_c_note(summary)
        hold_note = build_hold_note(summary)

        self.assertIn("replacement-ready rows: `12`", post_c_note)
        self.assertIn("projected runtime rows after staged `C`: `2105`", post_c_note)
        self.assertIn("- `direct_use`: `12`", post_c_note)
        self.assertIn("hold item count: `180`", post_c_note)
        self.assertIn("## C1-H1 Medical body-state overlays", hold_note)
        self.assertIn("## C1-RH Residual odd-hold", hold_note)


if __name__ == "__main__":
    unittest.main()
