from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from generate_acquisition_master import load_jsonl, write_json, write_jsonl
from phase3_candidate_state_lib import DEFAULT_STAGING_DIR, default_phase3_paths

KNOWN_BATCH_REVIEW_RULES = (
    {
        "batch_id": "KNOWN_LAYER_COLLISION_PURE_FORAGING_ACCESSORIES",
        "bucket_id": "Wearable.6-G",
        "approval_reason_code": "MANUAL_REVIEW_REQUIRED",
        "candidate_reason_code": "LAYER_COLLISION",
        "handling_mode": "NO_RULE_CHANGE_BATCH_REVIEW",
        "description": "Wearable.6-G pure-foraging accessory subset. Keep candidate_state as manual and review as a known collision backlog batch.",
    },
)

KNOWN_HOTSPOT_CLUSTER_STATUS_ENUM = frozenset({"OPEN", "IN_REVIEW", "KEEP_HOLD", "APPROVED_SYNC", "SPLIT_FOR_REVIEW", "WONT_SYNC"})
HOTSPOT_CLUSTERS_FILE_NAME = "phase3_approval_hotspot_clusters.json"


def load_known_hotspot_clusters(path: Path) -> list[dict[str, Any]]:
    """Load hotspot cluster definitions from the single-source-of-truth JSON file."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        clusters: list[dict[str, Any]] = json.load(handle)
    return clusters


class HotspotValidationError(Exception):
    """Raised when hotspot cluster JSON fails validation."""


def validate_hotspot_clusters(
    clusters: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
) -> list[str]:
    """Validate hotspot cluster definitions against hold rows.

    Returns a list of warnings. Raises HotspotValidationError on hard failures.
    """
    warnings: list[str] = []
    errors: list[str] = []

    # Build hold row index
    hold_index: dict[str, dict[str, Any]] = {row["fulltype"]: row for row in hold_rows}

    # cluster_id uniqueness
    seen_cluster_ids: set[str] = set()
    # fulltype cross-cluster uniqueness
    all_fulltypes: dict[str, str] = {}  # fulltype -> cluster_id

    for cluster in clusters:
        cluster_id = cluster.get("cluster_id", "<missing>")

        if cluster_id in seen_cluster_ids:
            errors.append(f"Duplicate cluster_id: {cluster_id}")
        seen_cluster_ids.add(cluster_id)

        # cluster_status enum
        status = cluster.get("cluster_status", "<missing>")
        if status not in KNOWN_HOTSPOT_CLUSTER_STATUS_ENUM:
            errors.append(f"[{cluster_id}] Invalid cluster_status: {status!r}. Allowed: {sorted(KNOWN_HOTSPOT_CLUSTER_STATUS_ENUM)}")

        fulltypes = cluster.get("fulltypes", [])

        # fulltypes internal duplicate
        ft_set: set[str] = set()
        for ft in fulltypes:
            if ft in ft_set:
                errors.append(f"[{cluster_id}] Duplicate fulltype within cluster: {ft}")
            ft_set.add(ft)

        # cross-cluster fulltype
        for ft in fulltypes:
            if ft in all_fulltypes:
                errors.append(f"Fulltype {ft} belongs to multiple clusters: {all_fulltypes[ft]} and {cluster_id}")
            all_fulltypes[ft] = cluster_id

        # Validate against actual hold rows
        expected_state = cluster.get("candidate_state")
        expected_reason = cluster.get("candidate_reason_code")
        expected_approval = cluster.get("approval_reason_code")

        for ft in fulltypes:
            if ft not in hold_index:
                warnings.append(f"[{cluster_id}] fulltype {ft} not found in HOLD queue")
                continue
            row = hold_index[ft]
            if row["candidate_state"] != expected_state:
                errors.append(
                    f"[{cluster_id}] fulltype {ft} candidate_state mismatch: "
                    f"expected {expected_state}, got {row['candidate_state']}"
                )
            if row["candidate_reason_code"] != expected_reason:
                errors.append(
                    f"[{cluster_id}] fulltype {ft} candidate_reason_code mismatch: "
                    f"expected {expected_reason}, got {row['candidate_reason_code']}"
                )
            if row["approval_reason_code"] != expected_approval:
                errors.append(
                    f"[{cluster_id}] fulltype {ft} approval_reason_code mismatch: "
                    f"expected {expected_approval}, got {row['approval_reason_code']}"
                )

    if errors:
        raise HotspotValidationError("Hotspot cluster validation failed:\n" + "\n".join(f"  FAIL: {e}" for e in errors))

    return warnings


def build_known_hotspot_breakdown(
    clusters: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], set[tuple[str, str]]]:
    """Match hold rows against hotspot cluster definitions loaded from JSON."""
    hotspot_breakdown: list[dict[str, Any]] = []
    matched_keys: set[tuple[str, str]] = set()

    for cluster in clusters:
        cluster_fulltypes = set(cluster.get("fulltypes", []))
        cluster_rows = [
            row
            for row in hold_rows
            if row["fulltype"] in cluster_fulltypes
            and row["bucket_id"] == cluster["source_bucket"]
            and row["approval_reason_code"] == cluster["approval_reason_code"]
            and row["candidate_reason_code"] == cluster["candidate_reason_code"]
        ]
        if not cluster_rows:
            continue

        cluster_rows.sort(key=lambda row: row["fulltype"])
        for row in cluster_rows:
            matched_keys.add((row["bucket_id"], row["fulltype"]))

        hotspot_breakdown.append(
            {
                "cluster_id": cluster["cluster_id"],
                "source_bucket": cluster["source_bucket"],
                "hold_count": len(cluster_rows),
                "hotspot_type": cluster["hotspot_type"],
                "candidate_reason_code": cluster["candidate_reason_code"],
                "cluster_status": cluster["cluster_status"],
                "cluster_note_template": cluster.get("cluster_note_template", ""),
                "fulltypes": [row["fulltype"] for row in cluster_rows],
            }
        )

    hotspot_breakdown.sort(key=lambda h: (-h["hold_count"], h["cluster_id"]))
    return hotspot_breakdown, matched_keys


def sorted_counter(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def build_known_batch_review_breakdown(hold_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], set[tuple[str, str]]]:
    batch_breakdown: list[dict[str, Any]] = []
    matched_keys: set[tuple[str, str]] = set()

    for rule in KNOWN_BATCH_REVIEW_RULES:
        batch_rows = [
            row
            for row in hold_rows
            if row["bucket_id"] == rule["bucket_id"]
            and row["approval_reason_code"] == rule["approval_reason_code"]
            and row["candidate_reason_code"] == rule["candidate_reason_code"]
        ]
        if not batch_rows:
            continue

        batch_rows.sort(key=lambda row: row["fulltype"])
        for row in batch_rows:
            matched_keys.add((row["bucket_id"], row["fulltype"]))

        batch_breakdown.append(
            {
                "batch_id": rule["batch_id"],
                "bucket_id": rule["bucket_id"],
                "hold_count": len(batch_rows),
                "approval_reason_code": rule["approval_reason_code"],
                "candidate_reason_code": rule["candidate_reason_code"],
                "handling_mode": rule["handling_mode"],
                "description": rule["description"],
                "fulltypes": [row["fulltype"] for row in batch_rows],
            }
        )

    batch_breakdown.sort(key=lambda batch: (-batch["hold_count"], batch["batch_id"]))
    return batch_breakdown, matched_keys


def build_hold_reason_summary(
    *,
    sync_queue_path: Path,
    queue_rows: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
    hotspot_clusters: list[dict[str, Any]] | None = None,
    queue_source_label: str | None = None,
) -> dict[str, Any]:
    approval_reason_counts: Counter[str] = Counter()
    candidate_state_counts: Counter[str] = Counter()
    candidate_reason_counts: Counter[str] = Counter()
    bucket_groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    known_batch_review_breakdown, known_batch_row_keys = build_known_batch_review_breakdown(hold_rows)
    known_hotspot_breakdown, known_hotspot_row_keys = build_known_hotspot_breakdown(
        hotspot_clusters or [], hold_rows,
    )

    for row in hold_rows:
        approval_reason_counts[row["approval_reason_code"]] += 1
        candidate_state_counts[row["candidate_state"]] += 1
        candidate_reason_counts[row["candidate_reason_code"]] += 1
        bucket_groups[row["bucket_id"]].append(row)

    bucket_breakdown: list[dict[str, Any]] = []
    for bucket_id, rows in sorted(bucket_groups.items()):
        bucket_approval_counts: Counter[str] = Counter(row["approval_reason_code"] for row in rows)
        bucket_candidate_reason_counts: Counter[str] = Counter(row["candidate_reason_code"] for row in rows)
        bucket_breakdown.append(
            {
                "bucket_id": bucket_id,
                "hold_count": len(rows),
                "approval_reason_breakdown": sorted_counter(bucket_approval_counts),
                "candidate_reason_breakdown": sorted_counter(bucket_candidate_reason_counts),
            }
        )

    bucket_breakdown.sort(key=lambda bucket: (-bucket["hold_count"], bucket["bucket_id"]))

    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "queue_source": queue_source_label or str(sync_queue_path),
        "sync_queue_row_total": len(queue_rows),
        "hold_row_total": len(hold_rows),
        "known_batch_review_hold_row_total": len(known_batch_row_keys),
        "known_hotspot_hold_row_total": len(known_hotspot_row_keys),
        "general_hold_row_total": len(hold_rows) - len(known_batch_row_keys) - len(known_hotspot_row_keys),
        "known_batch_review_breakdown": known_batch_review_breakdown,
        "known_hotspot_breakdown": known_hotspot_breakdown,
        "approval_reason_breakdown": sorted_counter(approval_reason_counts),
        "candidate_state_breakdown": sorted_counter(candidate_state_counts),
        "candidate_reason_breakdown": sorted_counter(candidate_reason_counts),
        "bucket_breakdown": bucket_breakdown,
    }


def render_hold_review_backlog(
    *,
    summary: dict[str, Any],
    hold_rows: list[dict[str, Any]],
) -> str:
    lines: list[str] = [
        "# Phase 3 HOLD Review Backlog",
        "",
        "## Scope",
        "",
        f"- generated_at: `{summary['generated_at']}`",
        f"- queue source: `{summary['queue_source']}`",
        f"- sync queue rows: `{summary['sync_queue_row_total']}`",
        f"- hold rows: `{summary['hold_row_total']}`",
        "",
        "## Separation Guardrail",
        "",
        "- `candidate_state`는 유지한다.",
        "- 이 backlog는 `approval_state=HOLD` row만 추적한다.",
        "- approval review에서 필요한 note만 누적하고 Phase 2 acquisition이나 Phase 3 candidate 판단은 여기서 뒤집지 않는다.",
        "",
        "## Batch Review Separation",
        "",
        f"- known batch review rows: `{summary['known_batch_review_hold_row_total']}`",
        f"- known hotspot rows: `{summary['known_hotspot_hold_row_total']}`",
        f"- general HOLD rows: `{summary['general_hold_row_total']}`",
    ]

    known_batch_review_breakdown = summary["known_batch_review_breakdown"]
    if known_batch_review_breakdown:
        for batch in known_batch_review_breakdown:
            lines.append(
                f"- `{batch['batch_id']}` / `{batch['bucket_id']}`: `{batch['hold_count']}`"
                f" | `{batch['handling_mode']}`"
                f" | {batch['description']}"
            )
    else:
        lines.append("- known batch review groups: `0`")

    known_hotspot_breakdown = summary.get("known_hotspot_breakdown", [])
    if known_hotspot_breakdown:
        for hotspot in known_hotspot_breakdown:
            lines.append(
                f"- `{hotspot['cluster_id']}` / `{hotspot['source_bucket']}`: `{hotspot['hold_count']}`"
                f" | `{hotspot['hotspot_type']}`"
                f" | `{hotspot['cluster_status']}`"
            )
    else:
        lines.append("- known hotspot clusters: `0`")

    lines.extend(
        [
            "",
        "## By Approval Reason",
        "",
        ]
    )

    approval_reason_breakdown = summary["approval_reason_breakdown"]
    if approval_reason_breakdown:
        for reason_code, count in approval_reason_breakdown.items():
            lines.append(f"- `{reason_code}`: `{count}`")
    else:
        lines.append("- current HOLD rows: `0`")

    lines.extend(
        [
            "",
            "## By Candidate State",
            "",
        ]
    )
    candidate_state_breakdown = summary["candidate_state_breakdown"]
    if candidate_state_breakdown:
        for state, count in candidate_state_breakdown.items():
            lines.append(f"- `{state}`: `{count}`")
    else:
        lines.append("- current HOLD rows: `0`")

    lines.extend(
        [
            "",
            "## By Bucket",
            "",
        ]
    )
    bucket_breakdown = summary["bucket_breakdown"]
    if bucket_breakdown:
        for bucket in bucket_breakdown:
            reason_parts = [
                f"{reason}={count}" for reason, count in bucket["approval_reason_breakdown"].items()
            ]
            lines.append(
                f"- `{bucket['bucket_id']}`: `{bucket['hold_count']}`"
                + (f" ({', '.join(reason_parts)})" if reason_parts else "")
            )
    else:
        lines.append("- current HOLD buckets: `0`")

    lines.extend(
        [
            "",
            "## Current HOLD Rows",
            "",
        ]
    )
    if hold_rows:
        for row in hold_rows:
            note = row.get("approval_notes") or row.get("phase3_notes")
            line = (
                f"- `{row['bucket_id']} / {row['fulltype']}`"
                f" | `{row['approval_reason_code']}`"
                f" | `{row['candidate_reason_code']}`"
            )
            if note:
                line += f" | {note}"
            lines.append(line)
    else:
        lines.append("- current HOLD rows: `0`")

    lines.append("")
    return "\n".join(lines)


def build_phase3_hold_queue(
    *,
    sync_queue_path: Path,
    hold_queue_out: Path,
    reason_summary_out: Path,
    backlog_out: Path,
    hotspot_clusters_path: Path | None = None,
    queue_source_label: str | None = None,
) -> dict[str, Any]:
    queue_rows = load_jsonl(sync_queue_path)
    hold_rows = [row for row in queue_rows if row["approval_state"] == "HOLD"]
    hold_rows.sort(key=lambda row: (row["bucket_id"], row["fulltype"]))

    # Load and validate hotspot clusters from JSON (single source of truth)
    hotspot_clusters: list[dict[str, Any]] = []
    if hotspot_clusters_path is not None:
        hotspot_clusters = load_known_hotspot_clusters(hotspot_clusters_path)
        if hotspot_clusters:
            validation_warnings = validate_hotspot_clusters(hotspot_clusters, hold_rows)
            for warn in validation_warnings:
                print(f"  WARN: {warn}", file=sys.stderr)

    summary = build_hold_reason_summary(
        sync_queue_path=sync_queue_path,
        queue_rows=queue_rows,
        hold_rows=hold_rows,
        hotspot_clusters=hotspot_clusters,
        queue_source_label=queue_source_label,
    )
    backlog = render_hold_review_backlog(summary=summary, hold_rows=hold_rows)

    write_jsonl(hold_queue_out, hold_rows)
    write_json(reason_summary_out, summary)
    backlog_out.parent.mkdir(parents=True, exist_ok=True)
    backlog_out.write_text(backlog, encoding="utf-8")

    return {
        "hold_rows": hold_rows,
        "summary": summary,
        "hold_queue_out": hold_queue_out,
        "reason_summary_out": reason_summary_out,
        "backlog_out": backlog_out,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 3 HOLD queue cumulative artifacts from the sync queue.")
    parser.add_argument(
        "--staging-dir",
        type=Path,
        default=DEFAULT_STAGING_DIR,
        help="Phase2 staging directory that contains phase3/ outputs.",
    )
    parser.add_argument(
        "--sync-queue",
        type=Path,
        default=None,
        help="Optional sync queue path. Defaults to <staging-dir>/phase3/phase3_sync_queue.jsonl",
    )
    parser.add_argument(
        "--hold-queue-out",
        type=Path,
        default=None,
        help="Optional HOLD queue output path. Defaults to <staging-dir>/phase3/phase3_hold_queue_cumulative.jsonl",
    )
    parser.add_argument(
        "--reason-summary-out",
        type=Path,
        default=None,
        help="Optional HOLD reason summary output path. Defaults to <staging-dir>/phase3/phase3_hold_reason_summary.json",
    )
    parser.add_argument(
        "--backlog-out",
        type=Path,
        default=None,
        help="Optional HOLD backlog markdown path. Defaults to <staging-dir-parent>/phase3_hold_review_backlog.md",
    )
    parser.add_argument(
        "--hotspot-clusters",
        type=Path,
        default=None,
        help="Optional hotspot clusters JSON path. Defaults to <staging-dir>/phase3/phase3_approval_hotspot_clusters.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    defaults = default_phase3_paths(args.staging_dir)
    phase3_dir = defaults["phase3_dir"]
    result = build_phase3_hold_queue(
        sync_queue_path=args.sync_queue or (phase3_dir / "phase3_sync_queue.jsonl"),
        hold_queue_out=args.hold_queue_out or defaults["hold_queue"],
        reason_summary_out=args.reason_summary_out or defaults["hold_reason_summary"],
        backlog_out=args.backlog_out or defaults["hold_review_backlog"],
        hotspot_clusters_path=args.hotspot_clusters or (phase3_dir / HOTSPOT_CLUSTERS_FILE_NAME),
    )
    summary = result["summary"]
    print("Phase 3 HOLD queue artifacts generated")
    print(f"  HOLD rows: {summary['hold_row_total']}")
    print(f"  Known batch review: {summary['known_batch_review_hold_row_total']}")
    print(f"  Known hotspot: {summary['known_hotspot_hold_row_total']}")
    print(f"  General hold: {summary['general_hold_row_total']}")
    for reason_code, count in summary["approval_reason_breakdown"].items():
        print(f"  {reason_code}: {count}")
    print(f"  HOLD queue out: {result['hold_queue_out']}")
    print(f"  Reason summary out: {result['reason_summary_out']}")
    print(f"  Backlog out: {result['backlog_out']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
