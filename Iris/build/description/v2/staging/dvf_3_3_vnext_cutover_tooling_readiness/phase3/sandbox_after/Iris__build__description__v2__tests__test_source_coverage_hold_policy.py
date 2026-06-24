from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_source_coverage_hold_policy import (
    build_hold_policy_summary,
    build_policy_note,
    build_rebuild_note,
    build_reentry_matrix,
    build_runtime_rebuild_checkpoint,
)


class SourceCoverageHoldPolicyTest(unittest.TestCase):
    def test_hold_policy_summary_matches_current_hold_subsets(self) -> None:
        summary = build_hold_policy_summary()

        self.assertEqual(summary["hold_item_count"], 180)
        self.assertEqual(summary["hold_subset_ids"], ["C1-H1", "C1-H2", "C1-RH"])

        rows = {row["subset_id"]: row for row in summary["rows"]}
        self.assertEqual(rows["C1-H1"]["item_count"], 94)
        self.assertEqual(rows["C1-H2"]["item_count"], 77)
        self.assertEqual(rows["C1-RH"]["item_count"], 9)
        self.assertEqual(rows["C1-H1"]["policy_track"], "state_overlay_excluded")
        self.assertEqual(rows["C1-H2"]["policy_track"], "state_overlay_excluded")
        self.assertEqual(rows["C1-RH"]["policy_track"], "manual_outlier_hold")

        matrix = build_reentry_matrix(summary)
        self.assertEqual(len(matrix["rows"]), 3)

    def test_rebuild_checkpoint_tracks_integrated_runtime_when_present(self) -> None:
        checkpoint = build_runtime_rebuild_checkpoint(
            {
                "projected_runtime": {
                    "projected_runtime_row_count": 2105,
                    "path_counts": {"cluster_summary": 1275},
                }
            }
        )

        self.assertEqual(checkpoint["status"], "ready_for_in_game_validation")
        self.assertEqual(checkpoint["current_runtime_artifact"], "source_coverage_runtime")
        self.assertEqual(checkpoint["current_phase_d_status"], "ready_for_in_game_validation")
        self.assertEqual(checkpoint["current_phase_d_rendered_entry_count"], 2105 DVF_AUTHORITY_ROLE_MIGRATION[17e9068ae556551cae8f8a37df32531a]) DVF_AUTHORITY_ROLE_MIGRATION[17e9068ae556551cae8f8a37df32531a]
        self.assertEqual(checkpoint["current_cluster_summary_count"], 1275)
        self.assertEqual(checkpoint["rendered_entry_gap_to_projected_runtime"], 0)
        self.assertEqual(checkpoint["rendered_entry_gap_to_projected_cluster_summary"], 0)
        self.assertFalse(checkpoint["historical_runtime_builder_uses_source_coverage"])
        self.assertTrue(checkpoint["integrated_source_coverage_runtime_exists"])
        self.assertTrue(checkpoint["integrated_projection_match"])

    def test_notes_capture_hold_and_rebuild_positions(self) -> None:
        summary = build_hold_policy_summary()
        policy_note = build_policy_note(summary)
        self.assertIn("## C1-H1 Medical body-state overlays", policy_note)
        self.assertIn("policy track: `manual_outlier_hold`", policy_note)

        checkpoint = build_runtime_rebuild_checkpoint(
            {
                "projected_runtime": {
                    "projected_runtime_row_count": 2105,
                    "path_counts": {"cluster_summary": 1275},
                }
            }
        )
        rebuild_note = build_rebuild_note(checkpoint)
        self.assertIn("status: `ready_for_in_game_validation`", rebuild_note)
        self.assertIn("current rendered entry count: `2105 DVF_AUTHORITY_ROLE_MIGRATION[723ffb3786d7de30506cd844f277d2a5]`", rebuild_note) DVF_AUTHORITY_ROLE_MIGRATION[723ffb3786d7de30506cd844f277d2a5]
        self.assertIn("current cluster_summary count: `1275`", rebuild_note)
        self.assertIn("projected runtime rows after staged C: `2105`", rebuild_note)


if __name__ == "__main__":
    unittest.main()
