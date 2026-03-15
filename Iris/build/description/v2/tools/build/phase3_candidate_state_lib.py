from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from generate_acquisition_master import (
    REVIEW_FILE_SUFFIX,
    STAGING_DIR as DEFAULT_STAGING_DIR,
    SYSTEM_BLOCKLIST_BUCKET,
    load_json,
    load_jsonl,
    ordered_bucket_names,
    write_json,
)

PHASE3_DIR_NAME = "phase3"
OVERLAY_FILE_NAME = "candidate_state_phase3.review.jsonl"
SUMMARY_FILE_NAME = "phase3_candidate_state_summary.json"
BY_BUCKET_FILE_NAME = "phase3_candidate_state_by_bucket.json"
GAPS_FILE_NAME = "phase3_candidate_state_gaps.json"
HOLD_QUEUE_FILE_NAME = "phase3_hold_queue_cumulative.jsonl"
HOLD_REASON_SUMMARY_FILE_NAME = "phase3_hold_reason_summary.json"
HOLD_REVIEW_BACKLOG_FILE_NAME = "phase3_hold_review_backlog.md"

PHASE2_TARGET_DISPOSITIONS = {"ACQ_HINT", "ACQ_NULL"}
PHASE2_NULL_REASONS = {"STANDARDIZATION_IMPOSSIBLE", "UBIQUITOUS_ITEM"}

CANDIDATE_STATES = {"KEEP_SILENT", "PROMOTE_ACTIVE", "MANUAL_OVERRIDE_CANDIDATE"}

KEEP_REASON_CODES = {
    "ACQ_NULL",
    "GENERIC_BUCKET_LEVEL",
    "DUPLICATES_SUBCATEGORY",
    "INTERACTION_LAYER_ONLY",
    "LOW_ITEM_SPECIFICITY",
    "PROSE_VALUE_INSUFFICIENT",
}

PROMOTE_REASON_CODES = {
    "LOCATION_SPECIFIC",
    "METHOD_SPECIFIC",
    "LOCATION_METHOD_SPECIFIC",
    "CONTEXT_SPECIFIC",
    "IDENTITY_LINKED",
    "USE_CONTEXT_LINKED",
}

MANUAL_REASON_CODES = {
    "LAYER_COLLISION",
    "SPECIFICITY_BORDERLINE",
    "COMPOSE_STYLE_RISK",
    "MULTI_CLAUSE_COLLAPSE",
    "RULE_GAP",
}

ALL_REASON_CODES = KEEP_REASON_CODES | PROMOTE_REASON_CODES | MANUAL_REASON_CODES

COMPOSE_PROFILES = {
    "ACQ_ONLY_LOCATION",
    "ACQ_ONLY_METHOD",
    "ACQ_LOCATION_METHOD",
    "ACQ_CONTEXT_NOTE",
    "USE_PLUS_ACQ",
    "IDENTITY_PLUS_ACQ",
}

PHASE3_REVIEW_FIELDS = (
    "fulltype",
    "bucket_id",
    "phase2_acquisition_state_snapshot",
    "phase2_acquisition_hint_snapshot",
    "phase2_null_reason_snapshot",
    "phase2_snapshot_hash",
    "candidate_state",
    "candidate_reason_code",
    "candidate_compose_profile",
    "notes",
    "decision_version",
    "review_closed",
)

SUMMARY_FIELDS = (
    "review_target_total",
    "review_closed_total",
    "keep_silent_count",
    "promote_active_count",
    "manual_override_candidate_count",
    "active_rate",
    "manual_rate",
    "reason_code_breakdown",
    "compose_profile_breakdown",
    "invalid_combo_count",
    "snapshot_mismatch_count",
    "determinism_sha",
)


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def phase3_staging_dir(staging_dir: Path) -> Path:
    return staging_dir / PHASE3_DIR_NAME


def default_phase3_paths(staging_dir: Path) -> dict[str, Path]:
    phase3_dir = phase3_staging_dir(staging_dir)
    return {
        "phase3_dir": phase3_dir,
        "overlay": phase3_dir / OVERLAY_FILE_NAME,
        "summary": phase3_dir / SUMMARY_FILE_NAME,
        "by_bucket": phase3_dir / BY_BUCKET_FILE_NAME,
        "gaps": phase3_dir / GAPS_FILE_NAME,
        "hold_queue": phase3_dir / HOLD_QUEUE_FILE_NAME,
        "hold_reason_summary": phase3_dir / HOLD_REASON_SUMMARY_FILE_NAME,
        "hold_review_backlog": staging_dir.parent / HOLD_REVIEW_BACKLOG_FILE_NAME,
    }


def parse_phase2_review_bucket(path: Path) -> str:
    name = path.name
    if not name.endswith(REVIEW_FILE_SUFFIX):
        raise ValueError(f"Invalid phase2 review suffix: {path}")
    return name[: -len(REVIEW_FILE_SUFFIX)]


def phase2_snapshot_from_review_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "fulltype": row["item_id"],
        "bucket_id": row["coverage_bucket"],
        "phase2_acquisition_state_snapshot": row["coverage_disposition"],
        "phase2_acquisition_hint_snapshot": row["acquisition_hint"],
        "phase2_null_reason_snapshot": row["acquisition_null_reason"],
    }


def phase2_snapshot_hash_from_snapshot(snapshot: dict[str, Any]) -> str:
    return sha256_hex(snapshot)


def normalize_overlay_row(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in PHASE3_REVIEW_FIELDS}


def compute_overlay_determinism_sha(rows: list[dict[str, Any]]) -> str:
    normalized = [normalize_overlay_row(row) for row in rows]
    normalized.sort(key=lambda row: row["fulltype"])
    return sha256_hex(normalized)


def build_phase2_indices(staging_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], list[str]]:
    reviews_dir = staging_dir / "reviews"
    errors: list[str] = []
    phase2_targets: dict[str, dict[str, Any]] = {}
    phase2_all_rows: dict[str, dict[str, Any]] = {}

    if not reviews_dir.exists():
        return {}, {}, [f"Missing phase2 reviews directory: {reviews_dir}"]

    review_files = sorted(reviews_dir.glob(f"*{REVIEW_FILE_SUFFIX}"))
    if not review_files:
        return {}, {}, [f"No phase2 review files found in {reviews_dir}"]

    for path in review_files:
        bucket_from_file = parse_phase2_review_bucket(path)
        rows = load_jsonl(path)
        for index, row in enumerate(rows, start=1):
            prefix = f"[phase2:{path.name}:{index}]"
            item_id = row.get("item_id")
            if not item_id:
                errors.append(f"{prefix} missing item_id")
                continue
            if item_id in phase2_all_rows:
                errors.append(f"{prefix} duplicate item_id across phase2 review files: {item_id}")
                continue

            record = dict(row)
            record["_review_file"] = path.name
            record["_review_index"] = index
            record["_bucket_from_file"] = bucket_from_file
            phase2_all_rows[item_id] = record

            if row.get("coverage_bucket") != bucket_from_file:
                errors.append(
                    f"{prefix} coverage_bucket/file mismatch: row={row.get('coverage_bucket')} file={bucket_from_file}"
                )

            if row.get("candidate_state") != "UNSET":
                errors.append(f"{prefix} phase2 candidate_state must remain UNSET once overlay is enabled")
            if row.get("candidate_reason_code") is not None:
                errors.append(f"{prefix} phase2 candidate_reason_code must remain null once overlay is enabled")
            if row.get("candidate_compose_profile") is not None:
                errors.append(f"{prefix} phase2 candidate_compose_profile must remain null once overlay is enabled")

            disposition = row.get("coverage_disposition")
            if disposition not in PHASE2_TARGET_DISPOSITIONS:
                continue
            if row.get("coverage_bucket") == SYSTEM_BLOCKLIST_BUCKET:
                errors.append(f"{prefix} reviewable phase2 row cannot use {SYSTEM_BLOCKLIST_BUCKET}")
                continue

            snapshot = phase2_snapshot_from_review_row(row)
            phase2_targets[item_id] = {
                **snapshot,
                "phase2_snapshot_hash": phase2_snapshot_hash_from_snapshot(snapshot),
                "_source_review_file": path.name,
            }

    return phase2_targets, phase2_all_rows, errors


def make_gap_example(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "fulltype": row["fulltype"],
        "bucket_id": row["bucket_id"],
        "candidate_reason_code": row["candidate_reason_code"],
        "notes": row["notes"],
    }


def build_phase3_reports(
    overlay_rows: list[dict[str, Any]],
    *,
    invalid_combo_count: int = 0,
    snapshot_mismatch_count: int = 0,
) -> dict[str, Any]:
    normalized = [normalize_overlay_row(row) for row in overlay_rows]
    normalized.sort(key=lambda row: row["fulltype"])

    state_counts = Counter(row["candidate_state"] for row in normalized)
    reason_counts = Counter(row["candidate_reason_code"] for row in normalized)
    profile_counts = Counter(
        row["candidate_compose_profile"] for row in normalized if row.get("candidate_compose_profile") is not None
    )

    review_target_total = len(normalized)
    review_closed_total = sum(1 for row in normalized if row.get("review_closed") is True)
    active_rate = round(state_counts.get("PROMOTE_ACTIVE", 0) / review_target_total, 4) if review_target_total else 0.0
    manual_rate = (
        round(state_counts.get("MANUAL_OVERRIDE_CANDIDATE", 0) / review_target_total, 4) if review_target_total else 0.0
    )

    summary = {
        "review_target_total": review_target_total,
        "review_closed_total": review_closed_total,
        "keep_silent_count": state_counts.get("KEEP_SILENT", 0),
        "promote_active_count": state_counts.get("PROMOTE_ACTIVE", 0),
        "manual_override_candidate_count": state_counts.get("MANUAL_OVERRIDE_CANDIDATE", 0),
        "active_rate": active_rate,
        "manual_rate": manual_rate,
        "reason_code_breakdown": dict(sorted(reason_counts.items())),
        "compose_profile_breakdown": dict(sorted(profile_counts.items())),
        "invalid_combo_count": invalid_combo_count,
        "snapshot_mismatch_count": snapshot_mismatch_count,
        "determinism_sha": compute_overlay_determinism_sha(normalized),
    }

    rows_by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in normalized:
        rows_by_bucket[row["bucket_id"]].append(row)

    bucket_counts = Counter(row["bucket_id"] for row in normalized)
    buckets: list[dict[str, Any]] = []
    for bucket in ordered_bucket_names(bucket_counts):
        rows = rows_by_bucket[bucket]
        bucket_state_counts = Counter(row["candidate_state"] for row in rows)
        bucket_reason_counts = Counter(row["candidate_reason_code"] for row in rows)
        bucket_profile_counts = Counter(
            row["candidate_compose_profile"] for row in rows if row.get("candidate_compose_profile") is not None
        )
        buckets.append(
            {
                "bucket_id": bucket,
                "target_count": len(rows),
                "reviewed_count": sum(1 for row in rows if row.get("review_closed") is True),
                "keep_count": bucket_state_counts.get("KEEP_SILENT", 0),
                "promote_count": bucket_state_counts.get("PROMOTE_ACTIVE", 0),
                "manual_count": bucket_state_counts.get("MANUAL_OVERRIDE_CANDIDATE", 0),
                "reason_breakdown": dict(sorted(bucket_reason_counts.items())),
                "profile_breakdown": dict(sorted(bucket_profile_counts.items())),
            }
        )

    manual_rows = [row for row in normalized if row["candidate_state"] == "MANUAL_OVERRIDE_CANDIDATE"]
    manual_reason_counts = Counter(row["candidate_reason_code"] for row in manual_rows)
    manual_clusters = [
        {
            "reason_code": reason_code,
            "count": count,
            "example_fulltypes": sorted(
                row["fulltype"] for row in manual_rows if row["candidate_reason_code"] == reason_code
            )[:5],
        }
        for reason_code, count in sorted(manual_reason_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    style_risk_rows = [row for row in manual_rows if row["candidate_reason_code"] == "COMPOSE_STYLE_RISK"]
    style_risk_clusters = []
    if style_risk_rows:
        style_risk_clusters.append(
            {
                "reason_code": "COMPOSE_STYLE_RISK",
                "count": len(style_risk_rows),
                "example_fulltypes": sorted(row["fulltype"] for row in style_risk_rows)[:5],
            }
        )

    high_manual_buckets = []
    for bucket in buckets:
        if bucket["target_count"] == 0 or bucket["manual_count"] == 0:
            continue
        manual_bucket_rate = round(bucket["manual_count"] / bucket["target_count"], 4)
        if manual_bucket_rate < 0.2:
            continue
        high_manual_buckets.append(
            {
                "bucket_id": bucket["bucket_id"],
                "manual_count": bucket["manual_count"],
                "target_count": bucket["target_count"],
                "manual_rate": manual_bucket_rate,
            }
        )
    high_manual_buckets.sort(key=lambda item: (-item["manual_rate"], -item["manual_count"], item["bucket_id"]))

    gaps = {
        "manual_clusters": manual_clusters,
        "rule_gap_examples": [make_gap_example(row) for row in manual_rows if row["candidate_reason_code"] == "RULE_GAP"],
        "layer_collision_examples": [
            make_gap_example(row) for row in manual_rows if row["candidate_reason_code"] == "LAYER_COLLISION"
        ],
        "high_manual_buckets": high_manual_buckets,
        "style_risk_clusters": style_risk_clusters,
    }

    return {
        "summary": summary,
        "by_bucket": {"buckets": buckets},
        "gaps": gaps,
    }
