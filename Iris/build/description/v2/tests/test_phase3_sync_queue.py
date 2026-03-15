from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
BUILD_DIR = TESTS_DIR.parent / "tools" / "build"
sys.path.insert(0, str(BUILD_DIR))

from build_phase3_sync_queue import build_phase3_sync_queue  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def make_overlay_row(
    *,
    fulltype: str,
    bucket_id: str,
    candidate_state: str,
    candidate_reason_code: str,
    candidate_compose_profile: str | None,
    notes: str | None = None,
) -> dict:
    return {
        "fulltype": fulltype,
        "bucket_id": bucket_id,
        "phase2_acquisition_state_snapshot": "ACQ_HINT",
        "phase2_acquisition_hint_snapshot": "test",
        "phase2_null_reason_snapshot": None,
        "phase2_snapshot_hash": "f" * 64,
        "candidate_state": candidate_state,
        "candidate_reason_code": candidate_reason_code,
        "candidate_compose_profile": candidate_compose_profile,
        "notes": notes,
        "decision_version": "phase3-candidate-state-v1",
        "review_closed": True,
    }


class Phase3SyncQueueTests(unittest.TestCase):
    def test_build_phase3_sync_queue_maps_states(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            overlay_path = tmp_dir / "pilot.review.jsonl"
            write_jsonl(
                overlay_path,
                [
                    make_overlay_row(
                        fulltype="Base.Bandage",
                        bucket_id="Consumable.3-C",
                        candidate_state="PROMOTE_ACTIVE",
                        candidate_reason_code="LOCATION_SPECIFIC",
                        candidate_compose_profile="ACQ_ONLY_LOCATION",
                    ),
                    make_overlay_row(
                        fulltype="Base.DoctorBag",
                        bucket_id="Tool.1-L",
                        candidate_state="PROMOTE_ACTIVE",
                        candidate_reason_code="USE_CONTEXT_LINKED",
                        candidate_compose_profile="USE_PLUS_ACQ",
                    ),
                    make_overlay_row(
                        fulltype="Base.Handbag",
                        bucket_id="Tool.1-L",
                        candidate_state="MANUAL_OVERRIDE_CANDIDATE",
                        candidate_reason_code="LAYER_COLLISION",
                        candidate_compose_profile=None,
                        notes="3-4 상호작용층과 겹친다.",
                    ),
                    make_overlay_row(
                        fulltype="Base.PaperBag",
                        bucket_id="Tool.1-L",
                        candidate_state="KEEP_SILENT",
                        candidate_reason_code="GENERIC_BUCKET_LEVEL",
                        candidate_compose_profile=None,
                    ),
                ],
            )

            queue_rows = build_phase3_sync_queue([overlay_path])

            self.assertEqual(3, len(queue_rows))
            self.assertEqual("APPROVE_SYNC", queue_rows[0]["approval_state"])
            self.assertEqual("DIRECT_ACQUISITION_READY", queue_rows[0]["approval_reason_code"])
            self.assertEqual("HOLD", queue_rows[2]["approval_state"])
            self.assertEqual("MANUAL_REVIEW_REQUIRED", queue_rows[2]["approval_reason_code"])

    def test_build_phase3_sync_queue_rejects_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            overlay_one = tmp_dir / "pilotA.review.jsonl"
            overlay_two = tmp_dir / "pilotB.review.jsonl"

            row = make_overlay_row(
                fulltype="Base.Bandage",
                bucket_id="Consumable.3-C",
                candidate_state="PROMOTE_ACTIVE",
                candidate_reason_code="LOCATION_SPECIFIC",
                candidate_compose_profile="ACQ_ONLY_LOCATION",
            )
            write_jsonl(overlay_one, [row])
            write_jsonl(overlay_two, [row])

            with self.assertRaisesRegex(ValueError, "Duplicate fulltype"):
                build_phase3_sync_queue([overlay_one, overlay_two])


if __name__ == "__main__":
    unittest.main()
