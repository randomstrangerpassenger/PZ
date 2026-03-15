from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from generate_acquisition_master import write_json
from phase3_candidate_state_lib import DEFAULT_STAGING_DIR, default_phase3_paths
from validate_phase3_candidate_state import validate_phase3_candidate_state


def build_reports(
    staging_dir: Path,
    *,
    overlay_path: Path | None = None,
    require_complete: bool = False,
) -> dict[str, Any]:
    result = validate_phase3_candidate_state(
        staging_dir=staging_dir,
        overlay_path=overlay_path,
        require_complete=require_complete,
        summary_path=None,
        by_bucket_path=None,
        gaps_path=None,
        compare_report_payloads=False,
    )
    if not result["pass"]:
        raise ValueError("Cannot build Phase 3 report from invalid overlay dataset.")
    return result["reports"]


def resolve_output_paths(
    staging_dir: Path,
    *,
    summary_path: Path | None,
    by_bucket_path: Path | None,
    gaps_path: Path | None,
) -> dict[str, Path]:
    defaults = default_phase3_paths(staging_dir)
    return {
        "summary": summary_path or defaults["summary"],
        "by_bucket": by_bucket_path or defaults["by_bucket"],
        "gaps": gaps_path or defaults["gaps"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 3 candidate-state reports.")
    parser.add_argument(
        "--staging-dir",
        type=Path,
        default=DEFAULT_STAGING_DIR,
        help="Phase2 staging directory that contains reviews/ and phase3/.",
    )
    parser.add_argument(
        "--overlay",
        type=Path,
        default=None,
        help="Optional overlay path. Defaults to <staging-dir>/phase3/candidate_state_phase3.review.jsonl",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Require overlay coverage for every closed phase2 target row.",
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reports = build_reports(
        staging_dir=args.staging_dir,
        overlay_path=args.overlay,
        require_complete=args.require_complete,
    )
    paths = resolve_output_paths(
        args.staging_dir,
        summary_path=args.summary_out,
        by_bucket_path=args.by_bucket_out,
        gaps_path=args.gaps_out,
    )
    write_json(paths["summary"], reports["summary"])
    write_json(paths["by_bucket"], reports["by_bucket"])
    write_json(paths["gaps"], reports["gaps"])

    summary = reports["summary"]
    print("Phase 3 candidate-state reports generated")
    print(f"  Review target total: {summary['review_target_total']}")
    print(f"  Review closed total: {summary['review_closed_total']}")
    print(f"  Promote active: {summary['promote_active_count']}")
    print(f"  Keep silent: {summary['keep_silent_count']}")
    print(f"  Manual override candidate: {summary['manual_override_candidate_count']}")
    print(f"  Determinism sha: {summary['determinism_sha']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
