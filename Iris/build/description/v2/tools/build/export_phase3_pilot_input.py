from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from generate_acquisition_master import REVIEW_FILE_SUFFIX, load_jsonl, write_json, write_jsonl
from phase3_candidate_state_lib import (
    PHASE2_TARGET_DISPOSITIONS,
    build_phase2_indices,
    phase2_snapshot_from_review_row,
    phase2_snapshot_hash_from_snapshot,
    sha256_hex,
)


def build_pilot_snapshot_rows(review_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    snapshot_rows: list[dict[str, Any]] = []
    for row in review_rows:
        snapshot = phase2_snapshot_from_review_row(row)
        snapshot_rows.append(
            {
                **snapshot,
                "phase2_snapshot_hash": phase2_snapshot_hash_from_snapshot(snapshot),
            }
        )
    snapshot_rows.sort(key=lambda row: row["fulltype"])
    return snapshot_rows


def compute_snapshot_dataset_sha(snapshot_rows: list[dict[str, Any]]) -> str:
    return sha256_hex(snapshot_rows)


def build_manifest(
    *,
    pilot_name: str,
    bucket_id: str,
    source_review_file: str,
    review_rows: list[dict[str, Any]],
    snapshot_rows: list[dict[str, Any]],
    snapshot_dataset_sha: str,
) -> dict[str, Any]:
    disposition_counts = Counter(row["coverage_disposition"] for row in review_rows)
    return {
        "pilot_name": pilot_name,
        "bucket_id": bucket_id,
        "source_review_file": source_review_file,
        "row_count": len(review_rows),
        "coverage_disposition_breakdown": dict(sorted(disposition_counts.items())),
        "contamination": {
            "system_excluded": 0,
            "unreviewed": 0,
        },
        "fulltypes": [row["fulltype"] for row in snapshot_rows],
        "phase2_snapshot_sha256": snapshot_dataset_sha,
    }


def export_phase3_pilot_input(
    *,
    staging_dir: Path,
    bucket_id: str,
    pilot_name: str,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    phase2_targets, _, phase2_errors = build_phase2_indices(staging_dir)
    if phase2_errors:
        raise ValueError("Phase 2 review dataset is not clean enough for Phase 3 pilot export:\n- " + "\n- ".join(phase2_errors))

    review_path = staging_dir / "reviews" / f"{bucket_id}{REVIEW_FILE_SUFFIX}"
    if not review_path.exists():
        raise ValueError(f"Missing phase2 review file for bucket {bucket_id}: {review_path}")

    review_rows = load_jsonl(review_path)
    if not review_rows:
        raise ValueError(f"Phase2 review file is empty: {review_path}")

    contamination = Counter()
    closed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(review_rows, start=1):
        if row.get("coverage_bucket") != bucket_id:
            raise ValueError(
                f"[{review_path.name}:{index}] coverage_bucket/file mismatch: "
                f"{row.get('coverage_bucket')} != {bucket_id}"
            )

        disposition = row.get("coverage_disposition")
        if disposition in PHASE2_TARGET_DISPOSITIONS:
            closed_rows.append(row)
            continue
        if disposition == "UNREVIEWED":
            contamination["unreviewed"] += 1
        elif disposition == "SYSTEM_EXCLUDED":
            contamination["system_excluded"] += 1
        else:
            raise ValueError(f"[{review_path.name}:{index}] unsupported coverage_disposition: {disposition!r}")

    if contamination:
        raise ValueError(
            "Pilot input must be a closed Phase 2 slice. "
            f"Found contamination in {review_path.name}: {dict(sorted(contamination.items()))}"
        )

    if not closed_rows:
        raise ValueError(f"No closed Phase 2 rows found for bucket {bucket_id}")

    missing_targets = sorted(row["item_id"] for row in closed_rows if row["item_id"] not in phase2_targets)
    if missing_targets:
        preview = missing_targets[:10]
        suffix = f" ... +{len(missing_targets) - 10}" if len(missing_targets) > 10 else ""
        raise ValueError(f"Closed rows are missing from phase2 target index: {preview}{suffix}")

    snapshot_rows = build_pilot_snapshot_rows(closed_rows)
    snapshot_dataset_sha = compute_snapshot_dataset_sha(snapshot_rows)

    out_dir = out_dir or (staging_dir / "phase3")
    manifest_path = out_dir / f"{pilot_name}_input_manifest.json"
    snapshot_path = out_dir / f"{pilot_name}_phase2_snapshot.jsonl"
    hash_path = out_dir / f"{pilot_name}_phase2_snapshot_hash.txt"

    manifest = build_manifest(
        pilot_name=pilot_name,
        bucket_id=bucket_id,
        source_review_file=review_path.name,
        review_rows=closed_rows,
        snapshot_rows=snapshot_rows,
        snapshot_dataset_sha=snapshot_dataset_sha,
    )

    write_json(manifest_path, manifest)
    write_jsonl(snapshot_path, snapshot_rows)
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    hash_path.write_text(snapshot_dataset_sha + "\n", encoding="utf-8")

    return {
        "manifest_path": manifest_path,
        "snapshot_path": snapshot_path,
        "hash_path": hash_path,
        "manifest": manifest,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a closed Phase 2 pilot slice for Phase 3 review.")
    parser.add_argument(
        "--staging-dir",
        type=Path,
        required=True,
        help="Phase2 staging directory that contains reviews/ and phase3/.",
    )
    parser.add_argument(
        "--bucket",
        type=str,
        required=True,
        help="Phase2 coverage_bucket to export.",
    )
    parser.add_argument(
        "--pilot-name",
        type=str,
        required=True,
        help="Pilot name prefix used in output file names, for example pilotA.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Optional output directory. Defaults to <staging-dir>/phase3.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = export_phase3_pilot_input(
        staging_dir=args.staging_dir,
        bucket_id=args.bucket,
        pilot_name=args.pilot_name,
        out_dir=args.out_dir,
    )
    manifest = result["manifest"]
    print("Phase 3 pilot input exported")
    print(f"  Pilot: {manifest['pilot_name']}")
    print(f"  Bucket: {manifest['bucket_id']}")
    print(f"  Row count: {manifest['row_count']}")
    print(f"  Snapshot sha256: {manifest['phase2_snapshot_sha256']}")
    print(f"  Manifest path: {result['manifest_path']}")
    print(f"  Snapshot path: {result['snapshot_path']}")
    print(f"  Hash path: {result['hash_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
