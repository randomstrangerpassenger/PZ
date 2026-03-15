from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from build_phase3_hold_queue import build_phase3_hold_queue
from build_phase3_sync_queue import build_phase3_sync_queue
from generate_acquisition_master import load_jsonl, write_json, write_jsonl
from phase3_candidate_state_lib import DEFAULT_STAGING_DIR, default_phase3_paths, normalize_overlay_row
from report_phase3_candidate_state import build_reports
from validate_phase3_candidate_state import validate_phase3_candidate_state


def merge_overlay_rows(overlay_paths: list[Path]) -> list[dict[str, Any]]:
    merged_rows: list[dict[str, Any]] = []
    seen_fulltypes: set[str] = set()

    for overlay_path in overlay_paths:
        rows = load_jsonl(overlay_path)
        for row in rows:
            fulltype = row["fulltype"]
            if fulltype in seen_fulltypes:
                raise ValueError(f"Duplicate fulltype across rollout seed inputs: {fulltype}")
            seen_fulltypes.add(fulltype)
            merged_rows.append(normalize_overlay_row(row))

    merged_rows.sort(key=lambda row: (row["bucket_id"], row["fulltype"]))
    return merged_rows


def build_phase3_rollout_seed(
    *,
    staging_dir: Path,
    overlay_paths: list[Path],
    overlay_out: Path | None = None,
    summary_out: Path | None = None,
    by_bucket_out: Path | None = None,
    gaps_out: Path | None = None,
    sync_queue_out: Path | None = None,
    hold_queue_out: Path | None = None,
    hold_reason_summary_out: Path | None = None,
    hold_review_backlog_out: Path | None = None,
) -> dict[str, Any]:
    if not overlay_paths:
        raise ValueError("At least one overlay path is required to build the rollout seed.")

    defaults = default_phase3_paths(staging_dir)
    overlay_out = overlay_out or defaults["overlay"]
    summary_out = summary_out or defaults["summary"]
    by_bucket_out = by_bucket_out or defaults["by_bucket"]
    gaps_out = gaps_out or defaults["gaps"]
    sync_queue_out = sync_queue_out or (defaults["phase3_dir"] / "phase3_sync_queue.jsonl")
    hold_queue_out = hold_queue_out or defaults["hold_queue"]
    hold_reason_summary_out = hold_reason_summary_out or defaults["hold_reason_summary"]
    hold_review_backlog_out = hold_review_backlog_out or defaults["hold_review_backlog"]

    merged_rows = merge_overlay_rows(overlay_paths)

    temp_overlay_out = overlay_out.with_name(f"{overlay_out.name}.tmp")
    temp_summary_out = summary_out.with_name(f"{summary_out.name}.tmp")
    temp_by_bucket_out = by_bucket_out.with_name(f"{by_bucket_out.name}.tmp")
    temp_gaps_out = gaps_out.with_name(f"{gaps_out.name}.tmp")
    temp_sync_queue_out = sync_queue_out.with_name(f"{sync_queue_out.name}.tmp")
    temp_hold_queue_out = hold_queue_out.with_name(f"{hold_queue_out.name}.tmp")
    temp_hold_reason_summary_out = hold_reason_summary_out.with_name(f"{hold_reason_summary_out.name}.tmp")
    temp_hold_review_backlog_out = hold_review_backlog_out.with_name(f"{hold_review_backlog_out.name}.tmp")

    write_jsonl(temp_overlay_out, merged_rows)

    reports = build_reports(staging_dir=staging_dir, overlay_path=temp_overlay_out, require_complete=False)
    write_json(temp_summary_out, reports["summary"])
    write_json(temp_by_bucket_out, reports["by_bucket"])
    write_json(temp_gaps_out, reports["gaps"])

    queue_rows = build_phase3_sync_queue([temp_overlay_out], source_overlay_name=overlay_out.name)
    write_jsonl(temp_sync_queue_out, queue_rows)
    hold_result = build_phase3_hold_queue(
        sync_queue_path=temp_sync_queue_out,
        hold_queue_out=temp_hold_queue_out,
        reason_summary_out=temp_hold_reason_summary_out,
        backlog_out=temp_hold_review_backlog_out,
        queue_source_label=str(sync_queue_out),
    )

    validation = validate_phase3_candidate_state(
        staging_dir=staging_dir,
        overlay_path=temp_overlay_out,
        summary_path=temp_summary_out,
        by_bucket_path=temp_by_bucket_out,
        gaps_path=temp_gaps_out,
        require_complete=False,
    )
    if not validation["pass"]:
        raise ValueError("Rollout seed validation failed:\n- " + "\n- ".join(validation["errors"]))

    temp_overlay_out.replace(overlay_out)
    temp_summary_out.replace(summary_out)
    temp_by_bucket_out.replace(by_bucket_out)
    temp_gaps_out.replace(gaps_out)
    temp_sync_queue_out.replace(sync_queue_out)
    temp_hold_queue_out.replace(hold_queue_out)
    temp_hold_reason_summary_out.replace(hold_reason_summary_out)
    temp_hold_review_backlog_out.replace(hold_review_backlog_out)

    return {
        "overlay_out": overlay_out,
        "summary_out": summary_out,
        "by_bucket_out": by_bucket_out,
        "gaps_out": gaps_out,
        "sync_queue_out": sync_queue_out,
        "hold_queue_out": hold_queue_out,
        "hold_reason_summary_out": hold_reason_summary_out,
        "hold_review_backlog_out": hold_review_backlog_out,
        "overlay_row_count": len(merged_rows),
        "queue_row_count": len(queue_rows),
        "reports": reports,
        "hold_summary": hold_result["summary"],
        "validation_warnings": validation["warnings"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a canonical Phase 3 rollout seed from validated overlay slices.")
    parser.add_argument(
        "--staging-dir",
        type=Path,
        default=DEFAULT_STAGING_DIR,
        help="Phase2 staging directory that contains reviews/ and phase3/.",
    )
    parser.add_argument(
        "--overlay",
        type=Path,
        action="append",
        required=True,
        help="Validated Phase 3 overlay path to merge into the canonical rollout seed. Repeat for multiple inputs.",
    )
    parser.add_argument(
        "--overlay-out",
        type=Path,
        default=None,
        help="Optional canonical overlay output path. Defaults to <staging-dir>/phase3/candidate_state_phase3.review.jsonl",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=None,
        help="Optional summary output path. Defaults to <staging-dir>/phase3/phase3_candidate_state_summary.json",
    )
    parser.add_argument(
        "--by-bucket-out",
        type=Path,
        default=None,
        help="Optional by-bucket output path. Defaults to <staging-dir>/phase3/phase3_candidate_state_by_bucket.json",
    )
    parser.add_argument(
        "--gaps-out",
        type=Path,
        default=None,
        help="Optional gaps output path. Defaults to <staging-dir>/phase3/phase3_candidate_state_gaps.json",
    )
    parser.add_argument(
        "--sync-queue-out",
        type=Path,
        default=None,
        help="Optional sync queue output path. Defaults to <staging-dir>/phase3/phase3_sync_queue.jsonl",
    )
    parser.add_argument(
        "--hold-queue-out",
        type=Path,
        default=None,
        help="Optional HOLD queue output path. Defaults to <staging-dir>/phase3/phase3_hold_queue_cumulative.jsonl",
    )
    parser.add_argument(
        "--hold-reason-summary-out",
        type=Path,
        default=None,
        help="Optional HOLD reason summary output path. Defaults to <staging-dir>/phase3/phase3_hold_reason_summary.json",
    )
    parser.add_argument(
        "--hold-review-backlog-out",
        type=Path,
        default=None,
        help="Optional HOLD backlog markdown path. Defaults to <staging-dir-parent>/phase3_hold_review_backlog.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_phase3_rollout_seed(
        staging_dir=args.staging_dir,
        overlay_paths=args.overlay,
        overlay_out=args.overlay_out,
        summary_out=args.summary_out,
        by_bucket_out=args.by_bucket_out,
        gaps_out=args.gaps_out,
        sync_queue_out=args.sync_queue_out,
        hold_queue_out=args.hold_queue_out,
        hold_reason_summary_out=args.hold_reason_summary_out,
        hold_review_backlog_out=args.hold_review_backlog_out,
    )
    summary = result["reports"]["summary"]
    hold_summary = result["hold_summary"]
    print("Phase 3 rollout seed built")
    print(f"  Overlay rows: {result['overlay_row_count']}")
    print(f"  Queue rows: {result['queue_row_count']}")
    print(f"  HOLD rows: {hold_summary['hold_row_total']}")
    print(f"  Promote active: {summary['promote_active_count']}")
    print(f"  Manual override candidate: {summary['manual_override_candidate_count']}")
    print(f"  Overlay out: {result['overlay_out']}")
    print(f"  Summary out: {result['summary_out']}")
    print(f"  By-bucket out: {result['by_bucket_out']}")
    print(f"  Gaps out: {result['gaps_out']}")
    print(f"  Sync queue out: {result['sync_queue_out']}")
    print(f"  HOLD queue out: {result['hold_queue_out']}")
    print(f"  HOLD reason summary out: {result['hold_reason_summary_out']}")
    print(f"  HOLD review backlog out: {result['hold_review_backlog_out']}")
    if result["validation_warnings"]:
        print(f"  Validation warnings: {len(result['validation_warnings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
