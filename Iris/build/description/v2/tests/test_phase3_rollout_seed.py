from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
BUILD_DIR = TESTS_DIR.parent / "tools" / "build"
sys.path.insert(0, str(BUILD_DIR))

from build_phase3_rollout_seed import build_phase3_rollout_seed  # noqa: E402
from generate_acquisition_master import REVIEW_FILE_SUFFIX, load_json, load_jsonl  # noqa: E402
from phase3_candidate_state_lib import OVERLAY_FILE_NAME  # noqa: E402
from phase3_candidate_state_lib import phase2_snapshot_from_review_row  # noqa: E402
from phase3_candidate_state_lib import phase2_snapshot_hash_from_snapshot  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def make_phase2_row(
    *,
    item_id: str,
    bucket: str,
    disposition: str,
    acquisition_hint: str | None,
    acquisition_null_reason: str | None,
    notes: str | None = None,
) -> dict:
    return {
        "item_id": item_id,
        "display_name": item_id,
        "display_category": "Test",
        "type_value": "Normal",
        "primary_subcategory": bucket,
        "coverage_bucket": bucket,
        "coverage_disposition": disposition,
        "acquisition_hint": acquisition_hint,
        "acquisition_null_reason": acquisition_null_reason,
        "candidate_state": "UNSET",
        "candidate_reason_code": None,
        "candidate_compose_profile": None,
        "notes": notes,
    }


def make_overlay_row(
    phase2_row: dict,
    *,
    candidate_state: str,
    candidate_reason_code: str,
    candidate_compose_profile: str | None,
    notes: str | None,
) -> dict:
    snapshot = phase2_snapshot_from_review_row(phase2_row)
    return {
        **snapshot,
        "phase2_snapshot_hash": phase2_snapshot_hash_from_snapshot(snapshot),
        "candidate_state": candidate_state,
        "candidate_reason_code": candidate_reason_code,
        "candidate_compose_profile": candidate_compose_profile,
        "notes": notes,
        "decision_version": "phase3-candidate-state-v1",
        "review_closed": True,
    }


class Phase3RolloutSeedTests(unittest.TestCase):
    def test_build_phase3_rollout_seed_merges_reports_and_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"
            phase3_dir = staging_dir / "phase3"

            pilot_a_phase2 = make_phase2_row(
                item_id="Base.Bandage",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="약국이나 병원에서 발견된다",
                acquisition_null_reason=None,
            )
            pilot_b_phase2 = make_phase2_row(
                item_id="Base.DoctorBag",
                bucket="Tool.1-L",
                disposition="ACQ_HINT",
                acquisition_hint="의사 차량에서 발견된다",
                acquisition_null_reason=None,
            )
            manual_phase2 = make_phase2_row(
                item_id="Base.Handbag",
                bucket="Tool.1-L",
                disposition="ACQ_NULL",
                acquisition_hint=None,
                acquisition_null_reason="STANDARDIZATION_IMPOSSIBLE",
                notes="표준 문장 근거가 약하다.",
            )
            write_jsonl(reviews_dir / f"Consumable.3-C{REVIEW_FILE_SUFFIX}", [pilot_a_phase2])
            write_jsonl(reviews_dir / f"Tool.1-L{REVIEW_FILE_SUFFIX}", [pilot_b_phase2, manual_phase2])

            pilot_a_overlay = phase3_dir / "pilotA_candidate_state.review.jsonl"
            pilot_b_overlay = phase3_dir / "pilotB_candidate_state.review.jsonl"

            write_jsonl(
                pilot_a_overlay,
                [
                    make_overlay_row(
                        pilot_a_phase2,
                        candidate_state="PROMOTE_ACTIVE",
                        candidate_reason_code="LOCATION_SPECIFIC",
                        candidate_compose_profile="ACQ_ONLY_LOCATION",
                        notes=None,
                    )
                ],
            )
            write_jsonl(
                pilot_b_overlay,
                [
                    make_overlay_row(
                        pilot_b_phase2,
                        candidate_state="PROMOTE_ACTIVE",
                        candidate_reason_code="USE_CONTEXT_LINKED",
                        candidate_compose_profile="USE_PLUS_ACQ",
                        notes=None,
                    ),
                    make_overlay_row(
                        manual_phase2,
                        candidate_state="MANUAL_OVERRIDE_CANDIDATE",
                        candidate_reason_code="LAYER_COLLISION",
                        candidate_compose_profile=None,
                        notes="3-4 상호작용층과 겹친다.",
                    ),
                ],
            )

            result = build_phase3_rollout_seed(
                staging_dir=staging_dir,
                overlay_paths=[pilot_a_overlay, pilot_b_overlay],
            )

            overlay_rows = load_jsonl(phase3_dir / OVERLAY_FILE_NAME)
            queue_rows = load_jsonl(phase3_dir / "phase3_sync_queue.jsonl")
            hold_rows = load_jsonl(phase3_dir / "phase3_hold_queue_cumulative.jsonl")
            summary = load_json(phase3_dir / "phase3_candidate_state_summary.json")
            hold_summary = load_json(phase3_dir / "phase3_hold_reason_summary.json")
            hold_backlog = (staging_dir.parent / "phase3_hold_review_backlog.md").read_text(encoding="utf-8")

            self.assertEqual(3, result["overlay_row_count"])
            self.assertEqual(3, len(overlay_rows))
            self.assertEqual(3, len(queue_rows))
            self.assertEqual(2, len(hold_rows))
            self.assertEqual(2, summary["promote_active_count"])
            self.assertEqual(1, summary["manual_override_candidate_count"])
            self.assertEqual(2, hold_summary["hold_row_total"])
            self.assertEqual("phase3_sync_queue.jsonl", Path(hold_summary["queue_source"]).name)
            self.assertIn("Base.Handbag", hold_backlog)
            self.assertTrue(all(row["source_overlay"] == OVERLAY_FILE_NAME for row in queue_rows))
            self.assertTrue(all(row["source_overlay"] == OVERLAY_FILE_NAME for row in hold_rows))
            self.assertEqual("APPROVE_SYNC", queue_rows[0]["approval_state"])
            self.assertEqual("HOLD", queue_rows[-1]["approval_state"])

    def test_build_phase3_rollout_seed_rejects_duplicate_fulltypes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"
            phase3_dir = staging_dir / "phase3"

            phase2_row = make_phase2_row(
                item_id="Base.Bandage",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="약국이나 병원에서 발견된다",
                acquisition_null_reason=None,
            )
            write_jsonl(reviews_dir / f"Consumable.3-C{REVIEW_FILE_SUFFIX}", [phase2_row])

            overlay_row = make_overlay_row(
                phase2_row,
                candidate_state="PROMOTE_ACTIVE",
                candidate_reason_code="LOCATION_SPECIFIC",
                candidate_compose_profile="ACQ_ONLY_LOCATION",
                notes=None,
            )
            overlay_one = phase3_dir / "pilotA_candidate_state.review.jsonl"
            overlay_two = phase3_dir / "pilotB_candidate_state.review.jsonl"
            write_jsonl(overlay_one, [overlay_row])
            write_jsonl(overlay_two, [overlay_row])

            with self.assertRaisesRegex(ValueError, "Duplicate fulltype"):
                build_phase3_rollout_seed(
                    staging_dir=staging_dir,
                    overlay_paths=[overlay_one, overlay_two],
                )


if __name__ == "__main__":
    unittest.main()
