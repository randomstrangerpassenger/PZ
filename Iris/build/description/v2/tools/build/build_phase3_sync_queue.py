from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from generate_acquisition_master import load_jsonl, write_jsonl

QUEUE_VERSION = "phase3-sync-queue-v1"

DIRECT_APPROVE_REASON_CODES = {
    "LOCATION_SPECIFIC",
    "METHOD_SPECIFIC",
    "LOCATION_METHOD_SPECIFIC",
}

CONTEXTUAL_HOLD_REASON_CODES = {
    "CONTEXT_SPECIFIC",
    "USE_CONTEXT_LINKED",
    "IDENTITY_LINKED",
}

MANUAL_HOLD_REASON_CODES = {
    "LAYER_COLLISION",
    "SPECIFICITY_BORDERLINE",
    "COMPOSE_STYLE_RISK",
    "MULTI_CLAUSE_COLLAPSE",
    "RULE_GAP",
}

APPROVAL_STATES = {"APPROVE_SYNC", "HOLD", "REJECT"}
APPROVAL_REASON_CODES = {
    "DIRECT_ACQUISITION_READY",
    "CONTEXTUAL_PROMOTE_REVIEW",
    "MANUAL_REVIEW_REQUIRED",
    "SYNC_REJECTED",
}


def build_sync_queue_row(row: dict[str, Any], *, source_overlay: str) -> dict[str, Any]:
    candidate_state = row["candidate_state"]
    candidate_reason_code = row["candidate_reason_code"]

    if candidate_state == "PROMOTE_ACTIVE":
        if candidate_reason_code in DIRECT_APPROVE_REASON_CODES:
            approval_state = "APPROVE_SYNC"
            approval_reason_code = "DIRECT_ACQUISITION_READY"
            approval_notes = None
        elif candidate_reason_code in CONTEXTUAL_HOLD_REASON_CODES:
            approval_state = "HOLD"
            approval_reason_code = "CONTEXTUAL_PROMOTE_REVIEW"
            approval_notes = "Context-linked promote requires canon voice and layer-fit review before sync."
        else:
            raise ValueError(
                f"Unsupported PROMOTE_ACTIVE reason_code for sync queue mapping: {candidate_reason_code}"
            )
    elif candidate_state == "MANUAL_OVERRIDE_CANDIDATE":
        if candidate_reason_code not in MANUAL_HOLD_REASON_CODES:
            raise ValueError(
                f"Unsupported MANUAL_OVERRIDE_CANDIDATE reason_code for sync queue mapping: {candidate_reason_code}"
            )
        approval_state = "HOLD"
        approval_reason_code = "MANUAL_REVIEW_REQUIRED"
        approval_notes = row.get("notes")
    else:
        raise ValueError(f"Sync queue only accepts PROMOTE_ACTIVE or MANUAL_OVERRIDE_CANDIDATE rows, got {candidate_state}")

    return {
        "fulltype": row["fulltype"],
        "bucket_id": row["bucket_id"],
        "source_overlay": source_overlay,
        "candidate_state": candidate_state,
        "candidate_reason_code": candidate_reason_code,
        "candidate_compose_profile": row.get("candidate_compose_profile"),
        "phase3_notes": row.get("notes"),
        "approval_state": approval_state,
        "approval_reason_code": approval_reason_code,
        "approval_notes": approval_notes,
        "phase3_decision_version": row["decision_version"],
        "queue_version": QUEUE_VERSION,
    }


def build_phase3_sync_queue(
    overlay_paths: list[Path],
    *,
    source_overlay_name: str | None = None,
) -> list[dict[str, Any]]:
    queue_rows: list[dict[str, Any]] = []
    seen_fulltypes: set[str] = set()

    for overlay_path in overlay_paths:
        rows = load_jsonl(overlay_path)
        for row in rows:
            candidate_state = row["candidate_state"]
            if candidate_state == "KEEP_SILENT":
                continue

            fulltype = row["fulltype"]
            if fulltype in seen_fulltypes:
                raise ValueError(f"Duplicate fulltype across sync queue inputs: {fulltype}")
            seen_fulltypes.add(fulltype)

            queue_rows.append(
                build_sync_queue_row(
                    row,
                    source_overlay=source_overlay_name or overlay_path.name,
                )
            )

    queue_rows.sort(key=lambda row: (row["bucket_id"], row["fulltype"]))
    return queue_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Phase 3 sync approval queue from pilot overlays.")
    parser.add_argument(
        "--overlay",
        type=Path,
        action="append",
        required=True,
        help="Phase 3 overlay path. Repeat for multiple pilot overlays.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output jsonl path for the sync approval queue.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue_rows = build_phase3_sync_queue(args.overlay)
    write_jsonl(args.out, queue_rows)

    approval_counts = Counter(row["approval_state"] for row in queue_rows)
    print("Phase 3 sync approval queue generated")
    print(f"  Queue rows: {len(queue_rows)}")
    for approval_state in sorted(approval_counts):
        print(f"  {approval_state}: {approval_counts[approval_state]}")
    print(f"  Output path: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
