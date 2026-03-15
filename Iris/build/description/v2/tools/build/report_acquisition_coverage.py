from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from generate_acquisition_master import (
    MANIFEST_FILE_NAME,
    MASTER_FILE_NAME,
    REVIEW_FILE_SUFFIX,
    STAGING_DIR as DEFAULT_STAGING_DIR,
    SYSTEM_BLOCKLIST_BUCKET,
    load_json,
    load_jsonl,
    ordered_bucket_names,
)
from validate_acquisition_coverage import parse_review_bucket, validate_acquisition_coverage

SUMMARY_FILE_NAME = "acquisition_coverage_summary.json"
BY_BUCKET_FILE_NAME = "acquisition_coverage_by_bucket.json"
GAPS_FILE_NAME = "acquisition_coverage_gaps.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def load_review_rows(reviews_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(reviews_dir.glob(f"*{REVIEW_FILE_SUFFIX}")):
        bucket = parse_review_bucket(path)
        for row in load_jsonl(path):
            row = dict(row)
            row["_review_file"] = path.name
            row["_review_bucket"] = bucket
            rows.append(row)
    return rows


def build_bucket_progress(
    master_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    master_by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    review_by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in master_rows:
        master_by_bucket[row["coverage_bucket"]].append(row)
    for row in review_rows:
        review_by_bucket[row["coverage_bucket"]].append(row)

    ordered_buckets = ordered_bucket_names(Counter(row["coverage_bucket"] for row in master_rows))
    bucket_progress: dict[str, dict[str, Any]] = {}

    for bucket in ordered_buckets:
        bucket_reviews = review_by_bucket.get(bucket, [])
        disposition_counts = Counter(row["coverage_disposition"] for row in bucket_reviews)
        candidate_counts = Counter(
            row["candidate_state"] for row in bucket_reviews if row.get("candidate_state") and row["candidate_state"] != "UNSET"
        )
        reviewed_count = sum(1 for row in bucket_reviews if row["coverage_disposition"] != "UNREVIEWED")
        remaining_count = len(master_by_bucket[bucket]) - reviewed_count
        bucket_progress[bucket] = {
            "total_count": len(master_by_bucket[bucket]),
            "reviewed_count": reviewed_count,
            "remaining_count": remaining_count,
            "acq_hint_count": disposition_counts.get("ACQ_HINT", 0),
            "acq_null_count": disposition_counts.get("ACQ_NULL", 0),
            "system_excluded_count": disposition_counts.get("SYSTEM_EXCLUDED", 0),
            "promote_active_count": candidate_counts.get("PROMOTE_ACTIVE", 0),
            "keep_silent_count": candidate_counts.get("KEEP_SILENT", 0),
            "manual_override_candidate_count": candidate_counts.get("MANUAL_OVERRIDE_CANDIDATE", 0),
        }

    return bucket_progress


def build_reports(staging_dir: Path) -> dict[str, Any]:
    validation = validate_acquisition_coverage(staging_dir=staging_dir, require_complete=False)
    if not validation["pass"]:
        raise ValueError("Cannot build report from invalid staging dataset.")

    master_rows = load_jsonl(staging_dir / MASTER_FILE_NAME)
    review_rows = load_review_rows(staging_dir / "reviews")
    manifest = load_json(staging_dir / MANIFEST_FILE_NAME) if (staging_dir / MANIFEST_FILE_NAME).exists() else {}

    disposition_counts = Counter(row["coverage_disposition"] for row in review_rows)
    null_reason_breakdown = Counter(
        row["acquisition_null_reason"]
        for row in review_rows
        if row["coverage_disposition"] == "ACQ_NULL" and row.get("acquisition_null_reason")
    )
    candidate_counts = Counter(
        row["candidate_state"]
        for row in review_rows
        if row.get("candidate_state") and row["candidate_state"] != "UNSET"
    )

    total = len(master_rows)
    unreviewed = disposition_counts.get("UNREVIEWED", 0)
    closed = total - unreviewed
    reviewable_total = sum(1 for row in master_rows if row["coverage_bucket"] != SYSTEM_BLOCKLIST_BUCKET)
    reviewable_closed = disposition_counts.get("ACQ_HINT", 0) + disposition_counts.get("ACQ_NULL", 0)

    bucket_progress = build_bucket_progress(master_rows, review_rows)
    top_remaining = sorted(
        (
            {"bucket": bucket, "remaining_count": stats["remaining_count"]}
            for bucket, stats in bucket_progress.items()
            if stats["remaining_count"] > 0
        ),
        key=lambda item: (-item["remaining_count"], item["bucket"]),
    )[:10]

    unreviewed_items_by_bucket: dict[str, list[str]] = defaultdict(list)
    for row in review_rows:
        if row["coverage_disposition"] == "UNREVIEWED":
            unreviewed_items_by_bucket[row["coverage_bucket"]].append(row["item_id"])

    summary = {
        "generated_at": utc_now_iso(),
        "count_lock": manifest.get("count_lock", {}),
        "total": total,
        "closed": closed,
        "unreviewed": unreviewed,
        "acquisition_review_completion_pct": round((closed / total) * 100, 2) if total else 0.0,
        "reviewable_total": reviewable_total,
        "reviewable_closed": reviewable_closed,
        "system_excluded_total": sum(1 for row in master_rows if row["coverage_bucket"] == SYSTEM_BLOCKLIST_BUCKET),
        "acq_hint_count": disposition_counts.get("ACQ_HINT", 0),
        "acq_null_count": disposition_counts.get("ACQ_NULL", 0),
        "system_excluded_count": disposition_counts.get("SYSTEM_EXCLUDED", 0),
        "null_reason_breakdown": dict(sorted(null_reason_breakdown.items())),
        "promote_active_count": candidate_counts.get("PROMOTE_ACTIVE", 0),
        "keep_silent_count": candidate_counts.get("KEEP_SILENT", 0),
        "manual_override_candidate_count": candidate_counts.get("MANUAL_OVERRIDE_CANDIDATE", 0),
        "top_remaining_buckets": top_remaining,
    }

    by_bucket = {
        "generated_at": utc_now_iso(),
        "bucket_progress": bucket_progress,
    }

    gaps = {
        "generated_at": utc_now_iso(),
        "unreviewed_total": unreviewed,
        "top_remaining_buckets": top_remaining,
        "unreviewed_items_by_bucket": {
            bucket: sorted(item_ids) for bucket, item_ids in sorted(unreviewed_items_by_bucket.items())
        },
    }

    return {
        "summary": summary,
        "by_bucket": by_bucket,
        "gaps": gaps,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build DVF acquisition coverage reports.")
    parser.add_argument(
        "--staging-dir",
        type=Path,
        default=DEFAULT_STAGING_DIR,
        help="Staging directory created by generate_acquisition_master.py",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reports = build_reports(args.staging_dir)

    write_json(args.staging_dir / SUMMARY_FILE_NAME, reports["summary"])
    write_json(args.staging_dir / BY_BUCKET_FILE_NAME, reports["by_bucket"])
    write_json(args.staging_dir / GAPS_FILE_NAME, reports["gaps"])

    summary = reports["summary"]
    print("Acquisition coverage report generated")
    print(f"  Total: {summary['total']}")
    print(f"  Closed: {summary['closed']}")
    print(f"  Unreviewed: {summary['unreviewed']}")
    print(f"  Completion %: {summary['acquisition_review_completion_pct']}")
    print(f"  ACQ_HINT: {summary['acq_hint_count']}")
    print(f"  ACQ_NULL: {summary['acq_null_count']}")
    print(f"  SYSTEM_EXCLUDED: {summary['system_excluded_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
