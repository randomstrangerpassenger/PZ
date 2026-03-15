from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
BUILD_DIR = TESTS_DIR.parent / "tools" / "build"
sys.path.insert(0, str(BUILD_DIR))

from export_phase3_pilot_input import export_phase3_pilot_input  # noqa: E402
from generate_acquisition_master import REVIEW_FILE_SUFFIX  # noqa: E402
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
        "notes": None,
    }


class Phase3PilotInputTests(unittest.TestCase):
    def test_export_phase3_pilot_input_writes_manifest_snapshot_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"

            row_one = make_phase2_row(
                item_id="Base.Bandage",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="약국이나 병원에서 발견된다",
                acquisition_null_reason=None,
            )
            row_two = make_phase2_row(
                item_id="Base.AlcoholWipes",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="의료 시설이나 구급 차량에서 발견된다",
                acquisition_null_reason=None,
            )
            write_jsonl(reviews_dir / f"Consumable.3-C{REVIEW_FILE_SUFFIX}", [row_one, row_two])

            result = export_phase3_pilot_input(
                staging_dir=staging_dir,
                bucket_id="Consumable.3-C",
                pilot_name="pilotA",
            )

            manifest = result["manifest"]
            self.assertEqual("pilotA", manifest["pilot_name"])
            self.assertEqual("Consumable.3-C", manifest["bucket_id"])
            self.assertEqual(2, manifest["row_count"])
            self.assertEqual({"ACQ_HINT": 2}, manifest["coverage_disposition_breakdown"])
            self.assertEqual(
                ["Base.AlcoholWipes", "Base.Bandage"],
                manifest["fulltypes"],
            )

            snapshot_rows = [
                json.loads(line)
                for line in result["snapshot_path"].read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            expected_snapshot = []
            for row in [row_one, row_two]:
                snapshot = phase2_snapshot_from_review_row(row)
                expected_snapshot.append(
                    {
                        **snapshot,
                        "phase2_snapshot_hash": phase2_snapshot_hash_from_snapshot(snapshot),
                    }
                )
            expected_snapshot.sort(key=lambda row: row["fulltype"])

            self.assertEqual(expected_snapshot, snapshot_rows)
            self.assertEqual(
                manifest["phase2_snapshot_sha256"],
                result["hash_path"].read_text(encoding="utf-8").strip(),
            )

    def test_export_phase3_pilot_input_rejects_unreviewed_contamination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"

            clean_row = make_phase2_row(
                item_id="Base.Bandage",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="약국이나 병원에서 발견된다",
                acquisition_null_reason=None,
            )
            unreviewed_row = make_phase2_row(
                item_id="Base.BandageDirty",
                bucket="Consumable.3-C",
                disposition="UNREVIEWED",
                acquisition_hint=None,
                acquisition_null_reason=None,
            )
            write_jsonl(reviews_dir / f"Consumable.3-C{REVIEW_FILE_SUFFIX}", [clean_row, unreviewed_row])

            with self.assertRaisesRegex(ValueError, "closed Phase 2 slice"):
                export_phase3_pilot_input(
                    staging_dir=staging_dir,
                    bucket_id="Consumable.3-C",
                    pilot_name="pilotA",
                )


if __name__ == "__main__":
    unittest.main()
