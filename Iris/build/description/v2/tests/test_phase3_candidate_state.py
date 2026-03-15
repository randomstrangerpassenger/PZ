from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
BUILD_DIR = TESTS_DIR.parent / "tools" / "build"
sys.path.insert(0, str(BUILD_DIR))

from generate_acquisition_master import REVIEW_FILE_SUFFIX, write_json  # noqa: E402
from phase3_candidate_state_lib import OVERLAY_FILE_NAME, default_phase3_paths  # noqa: E402
from phase3_candidate_state_lib import phase2_snapshot_from_review_row  # noqa: E402
from phase3_candidate_state_lib import phase2_snapshot_hash_from_snapshot  # noqa: E402
from report_phase3_candidate_state import build_reports  # noqa: E402
from validate_phase3_candidate_state import validate_phase3_candidate_state  # noqa: E402


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
    candidate_state: str = "UNSET",
    candidate_reason_code: str | None = None,
    candidate_compose_profile: str | None = None,
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
        "candidate_state": candidate_state,
        "candidate_reason_code": candidate_reason_code,
        "candidate_compose_profile": candidate_compose_profile,
        "notes": notes,
    }


def make_overlay_row(
    phase2_row: dict,
    *,
    candidate_state: str,
    candidate_reason_code: str,
    candidate_compose_profile: str | None,
    notes: str | None,
    decision_version: str = "phase3-candidate-state-v1",
) -> dict:
    snapshot = phase2_snapshot_from_review_row(phase2_row)
    return {
        **snapshot,
        "phase2_snapshot_hash": phase2_snapshot_hash_from_snapshot(snapshot),
        "candidate_state": candidate_state,
        "candidate_reason_code": candidate_reason_code,
        "candidate_compose_profile": candidate_compose_profile,
        "notes": notes,
        "decision_version": decision_version,
        "review_closed": True,
    }


class Phase3CandidateStateTests(unittest.TestCase):
    def test_validator_accepts_valid_overlay_and_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"
            phase3_dir = staging_dir / "phase3"

            row_keep = make_phase2_row(
                item_id="Base.GenericBag",
                bucket="Tool.1-L",
                disposition="ACQ_HINT",
                acquisition_hint="식료품점에서 발견된다",
                acquisition_null_reason=None,
            )
            row_promote = make_phase2_row(
                item_id="Base.DoctorBag",
                bucket="Tool.1-L",
                disposition="ACQ_HINT",
                acquisition_hint="의사 차량에서 발견된다",
                acquisition_null_reason=None,
            )
            row_manual = make_phase2_row(
                item_id="Base.PistolCase",
                bucket="Tool.1-L",
                disposition="ACQ_NULL",
                acquisition_hint=None,
                acquisition_null_reason="STANDARDIZATION_IMPOSSIBLE",
                notes="명시적 근거가 분산되어 표준 문장으로 닫히지 않는다.",
            )

            write_jsonl(reviews_dir / f"Tool.1-L{REVIEW_FILE_SUFFIX}", [row_keep, row_promote, row_manual])

            overlay_rows = [
                make_overlay_row(
                    row_keep,
                    candidate_state="KEEP_SILENT",
                    candidate_reason_code="GENERIC_BUCKET_LEVEL",
                    candidate_compose_profile=None,
                    notes=None,
                ),
                make_overlay_row(
                    row_promote,
                    candidate_state="PROMOTE_ACTIVE",
                    candidate_reason_code="LOCATION_SPECIFIC",
                    candidate_compose_profile="ACQ_ONLY_LOCATION",
                    notes=None,
                ),
                make_overlay_row(
                    row_manual,
                    candidate_state="MANUAL_OVERRIDE_CANDIDATE",
                    candidate_reason_code="RULE_GAP",
                    candidate_compose_profile=None,
                    notes="전용 케이스 배치 근거가 빈약하여 자동 판정으로 닫을 수 없다.",
                ),
            ]
            write_jsonl(phase3_dir / OVERLAY_FILE_NAME, overlay_rows)

            reports = build_reports(staging_dir, require_complete=True)
            paths = default_phase3_paths(staging_dir)
            write_json(paths["summary"], reports["summary"])
            write_json(paths["by_bucket"], reports["by_bucket"])
            write_json(paths["gaps"], reports["gaps"])

            result = validate_phase3_candidate_state(
                staging_dir=staging_dir,
                require_complete=True,
                summary_path=paths["summary"],
                by_bucket_path=paths["by_bucket"],
                gaps_path=paths["gaps"],
            )

            self.assertTrue(result["pass"], result["errors"])
            self.assertEqual(3, result["reports"]["summary"]["review_target_total"])
            self.assertEqual(1, result["reports"]["summary"]["promote_active_count"])
            self.assertEqual(1, result["reports"]["summary"]["manual_override_candidate_count"])
            self.assertEqual("RULE_GAP", result["reports"]["gaps"]["rule_gap_examples"][0]["candidate_reason_code"])

    def test_validator_rejects_snapshot_mismatch(self) -> None:
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
            overlay_row["phase2_acquisition_hint_snapshot"] = "가정집에서 발견된다"
            write_jsonl(phase3_dir / OVERLAY_FILE_NAME, [overlay_row])

            result = validate_phase3_candidate_state(staging_dir=staging_dir)
            self.assertFalse(result["pass"])
            self.assertTrue(any("snapshot mismatch" in error for error in result["errors"]))

    def test_validator_rejects_invalid_manual_combo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"
            phase3_dir = staging_dir / "phase3"

            phase2_row = make_phase2_row(
                item_id="Base.Case",
                bucket="Tool.1-L",
                disposition="ACQ_NULL",
                acquisition_hint=None,
                acquisition_null_reason="STANDARDIZATION_IMPOSSIBLE",
                notes="소스가 충돌한다.",
            )
            write_jsonl(reviews_dir / f"Tool.1-L{REVIEW_FILE_SUFFIX}", [phase2_row])

            overlay_row = make_overlay_row(
                phase2_row,
                candidate_state="MANUAL_OVERRIDE_CANDIDATE",
                candidate_reason_code="RULE_GAP",
                candidate_compose_profile=None,
                notes=None,
            )
            write_jsonl(phase3_dir / OVERLAY_FILE_NAME, [overlay_row])

            result = validate_phase3_candidate_state(staging_dir=staging_dir)
            self.assertFalse(result["pass"])
            self.assertTrue(any("MANUAL_OVERRIDE_CANDIDATE requires notes" in error for error in result["errors"]))

    def test_validator_rejects_phase2_candidate_contamination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"
            phase3_dir = staging_dir / "phase3"

            contaminated_phase2_row = make_phase2_row(
                item_id="Base.Bandage",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="약국이나 병원에서 발견된다",
                acquisition_null_reason=None,
                candidate_state="PROMOTE_ACTIVE",
                candidate_reason_code="LOCATION_SPECIFIC",
                candidate_compose_profile="legacy",
            )
            write_jsonl(reviews_dir / f"Consumable.3-C{REVIEW_FILE_SUFFIX}", [contaminated_phase2_row])

            clean_phase2_row = make_phase2_row(
                item_id="Base.Bandage",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="약국이나 병원에서 발견된다",
                acquisition_null_reason=None,
            )
            overlay_row = make_overlay_row(
                clean_phase2_row,
                candidate_state="PROMOTE_ACTIVE",
                candidate_reason_code="LOCATION_SPECIFIC",
                candidate_compose_profile="ACQ_ONLY_LOCATION",
                notes=None,
            )
            write_jsonl(phase3_dir / OVERLAY_FILE_NAME, [overlay_row])

            result = validate_phase3_candidate_state(staging_dir=staging_dir)
            self.assertFalse(result["pass"])
            self.assertTrue(any("phase2 candidate_state must remain UNSET" in error for error in result["errors"]))

    def test_validator_custom_overlay_does_not_compare_against_existing_canonical_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"
            phase3_dir = staging_dir / "phase3"

            canonical_phase2_row = make_phase2_row(
                item_id="Base.CanonicalBandage",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="병원에서 발견된다",
                acquisition_null_reason=None,
            )
            custom_phase2_row = make_phase2_row(
                item_id="Base.CustomPistol",
                bucket="Combat.2-G",
                disposition="ACQ_HINT",
                acquisition_hint="총기 매장에서 발견된다",
                acquisition_null_reason=None,
            )
            write_jsonl(reviews_dir / f"Consumable.3-C{REVIEW_FILE_SUFFIX}", [canonical_phase2_row])
            write_jsonl(reviews_dir / f"Combat.2-G{REVIEW_FILE_SUFFIX}", [custom_phase2_row])

            canonical_overlay = [
                make_overlay_row(
                    canonical_phase2_row,
                    candidate_state="PROMOTE_ACTIVE",
                    candidate_reason_code="LOCATION_SPECIFIC",
                    candidate_compose_profile="ACQ_ONLY_LOCATION",
                    notes=None,
                )
            ]
            write_jsonl(phase3_dir / OVERLAY_FILE_NAME, canonical_overlay)

            canonical_reports = build_reports(staging_dir)
            paths = default_phase3_paths(staging_dir)
            write_json(paths["summary"], canonical_reports["summary"])
            write_json(paths["by_bucket"], canonical_reports["by_bucket"])
            write_json(paths["gaps"], canonical_reports["gaps"])

            custom_overlay_path = phase3_dir / "wave1_combat2g_candidate_state.review.jsonl"
            write_jsonl(
                custom_overlay_path,
                [
                    make_overlay_row(
                        custom_phase2_row,
                        candidate_state="PROMOTE_ACTIVE",
                        candidate_reason_code="LOCATION_SPECIFIC",
                        candidate_compose_profile="ACQ_ONLY_LOCATION",
                        notes=None,
                    )
                ],
            )

            result = validate_phase3_candidate_state(
                staging_dir=staging_dir,
                overlay_path=custom_overlay_path,
            )

            self.assertTrue(result["pass"], result["errors"])

    def test_build_reports_ignores_stale_canonical_report_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            staging_dir = Path(tmp_dir_str) / "staging"
            reviews_dir = staging_dir / "reviews"
            phase3_dir = staging_dir / "phase3"

            phase2_row = make_phase2_row(
                item_id="Base.Bandage",
                bucket="Consumable.3-C",
                disposition="ACQ_HINT",
                acquisition_hint="병원에서 발견된다",
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
            write_jsonl(phase3_dir / OVERLAY_FILE_NAME, [overlay_row])

            # Stale canonical reports should not block report regeneration.
            write_json(phase3_dir / "phase3_candidate_state_summary.json", {"stale": True})
            write_json(phase3_dir / "phase3_candidate_state_by_bucket.json", {"stale": True})
            write_json(phase3_dir / "phase3_candidate_state_gaps.json", {"stale": True})

            reports = build_reports(staging_dir)

            self.assertEqual(1, reports["summary"]["review_target_total"])
            self.assertEqual(1, reports["summary"]["promote_active_count"])


if __name__ == "__main__":
    unittest.main()
