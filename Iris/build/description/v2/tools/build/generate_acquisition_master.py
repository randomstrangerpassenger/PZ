from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
V2_ROOT = SCRIPT_DIR.parent.parent
IRIS_DIR = V2_ROOT.parent.parent.parent
INPUT_DIR = IRIS_DIR / "input"
OUTPUT_DIR = IRIS_DIR / "output"
STAGING_DIR = V2_ROOT / "staging"
REVIEWS_DIR = STAGING_DIR / "reviews"

MASTER_FILE_NAME = "acquisition_master.jsonl"
MANIFEST_FILE_NAME = "acquisition_master_manifest.json"
REVIEW_FILE_SUFFIX = ".acquisition.jsonl"
SYSTEM_BLOCKLIST_BUCKET = "SYSTEM_BLOCKLIST"

EXPECTED_COUNT_LOCK = {
    "master_total": 2285,
    "reviewable_total": 2079,
    "system_blocklist_total": 206,
}

SYSTEM_DISPLAY_CATEGORIES = frozenset(
    {
        "Appearance",
        "Bandage",
        "Corpse",
        "Hidden",
        "MaleBody",
        "Wound",
        "ZedDmg",
    }
)

MASTER_FIELDS = (
    "item_id",
    "display_name",
    "display_category",
    "type_value",
    "primary_subcategory",
    "all_tags",
    "coverage_bucket",
)

REVIEW_FIELDS = (
    "item_id",
    "display_name",
    "display_category",
    "type_value",
    "primary_subcategory",
    "coverage_bucket",
    "coverage_disposition",
    "acquisition_hint",
    "acquisition_null_reason",
    "candidate_state",
    "candidate_reason_code",
    "candidate_compose_profile",
    "notes",
)

SOURCE_PRIORITY = [
    "items_itemscript",
    "tags_by_fulltype",
    "local_iris_outputs_docs",
    "manual_samples",
]

REVIEW_WAVES = [
    ["Consumable.3-C", "Consumable.3-E", "Consumable.3-B", "Consumable.3-D", "Consumable.3-A"],
    ["Tool.1-L", "Resource.4-B", "Resource.4-A", "Resource.4-C", "Resource.4-D", "Resource.4-E", "Resource.4-F", "Vehicle.8-A", "Vehicle.8-B"],
    ["Literature.5-A", "Literature.5-B", "Literature.5-C", "Literature.5-D", "Tool.1-K", "Tool.1-I", "Tool.1-H", "Tool.1-D", "Tool.1-A", "Tool.1-B", "Tool.1-J"],
    ["Combat.2-A", "Combat.2-B", "Combat.2-C", "Combat.2-D", "Combat.2-E", "Combat.2-F", "Combat.2-G", "Combat.2-H", "Combat.2-I", "Combat.2-J", "Combat.2-K", "Combat.2-L"],
    ["Wearable.6-A", "Wearable.6-B", "Wearable.6-C", "Wearable.6-D", "Wearable.6-E", "Wearable.6-F", "Wearable.6-G", "Furniture.7-A", "Misc.9-A", SYSTEM_BLOCKLIST_BUCKET],
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ordered_bucket_names(bucket_counts: Counter[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    for wave in REVIEW_WAVES:
        for bucket in wave:
            if bucket in bucket_counts and bucket not in seen:
                ordered.append(bucket)
                seen.add(bucket)

    for bucket in sorted(bucket_counts):
        if bucket not in seen:
            ordered.append(bucket)

    return ordered


def build_master_rows(
    items_data: dict[str, dict[str, Any]],
    tags_items: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    unknown_no_tag: list[dict[str, Any]] = []

    for item_id in sorted(items_data):
        raw = items_data[item_id]
        tags = list(tags_items.get(item_id, []))
        display_category = raw.get("DisplayCategory")

        if tags:
            primary_subcategory = tags[0]
            coverage_bucket = primary_subcategory
        elif display_category in SYSTEM_DISPLAY_CATEGORIES:
            primary_subcategory = None
            coverage_bucket = SYSTEM_BLOCKLIST_BUCKET
        else:
            unknown_no_tag.append(
                {
                    "item_id": item_id,
                    "display_name": raw.get("DisplayName") or item_id,
                    "display_category": display_category,
                    "type_value": raw.get("Type"),
                }
            )
            continue

        row = {
            "item_id": item_id,
            "display_name": raw.get("DisplayName") or item_id,
            "display_category": display_category,
            "type_value": raw.get("Type"),
            "primary_subcategory": primary_subcategory,
            "all_tags": tags,
            "coverage_bucket": coverage_bucket,
        }
        rows.append(row)

    return rows, unknown_no_tag


def summarize_master_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    bucket_counts = Counter(row["coverage_bucket"] for row in rows)
    reviewable_total = sum(count for bucket, count in bucket_counts.items() if bucket != SYSTEM_BLOCKLIST_BUCKET)
    system_total = bucket_counts.get(SYSTEM_BLOCKLIST_BUCKET, 0)

    return {
        "master_total": len(rows),
        "reviewable_total": reviewable_total,
        "system_blocklist_total": system_total,
        "bucket_counts": {bucket: bucket_counts[bucket] for bucket in ordered_bucket_names(bucket_counts)},
    }


def assert_count_lock(summary: dict[str, Any]) -> None:
    mismatches: list[str] = []

    for key, expected in EXPECTED_COUNT_LOCK.items():
        actual = summary[key]
        if actual != expected:
            mismatches.append(f"{key}: expected {expected}, got {actual}")

    if mismatches:
        raise ValueError("Count lock mismatch:\n- " + "\n- ".join(mismatches))


def review_row_from_master(master_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": master_row["item_id"],
        "display_name": master_row["display_name"],
        "display_category": master_row["display_category"],
        "type_value": master_row["type_value"],
        "primary_subcategory": master_row["primary_subcategory"],
        "coverage_bucket": master_row["coverage_bucket"],
        "coverage_disposition": "UNREVIEWED",
        "acquisition_hint": None,
        "acquisition_null_reason": None,
        "candidate_state": "UNSET",
        "candidate_reason_code": None,
        "candidate_compose_profile": None,
        "notes": None,
    }


def review_path_for_bucket(reviews_dir: Path, bucket: str) -> Path:
    return reviews_dir / f"{bucket}{REVIEW_FILE_SUFFIX}"


def create_missing_review_templates(
    master_rows: list[dict[str, Any]],
    reviews_dir: Path,
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in master_rows:
        grouped[row["coverage_bucket"]].append(row)

    created: dict[str, int] = {}
    skipped: dict[str, int] = {}

    for bucket in ordered_bucket_names(Counter(grouped)):
        path = review_path_for_bucket(reviews_dir, bucket)
        if path.exists():
            skipped[bucket] = len(grouped[bucket])
            continue

        rows = [review_row_from_master(row) for row in grouped[bucket]]
        write_jsonl(path, rows)
        created[bucket] = len(rows)

    return {
        "created_files": created,
        "skipped_existing_files": skipped,
    }


def build_manifest(
    summary: dict[str, Any],
    *,
    items_path: Path,
    tags_path: Path,
    master_path: Path,
    reviews_dir: Path,
    count_lock_enforced: bool,
    template_stats: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at": utc_now_iso(),
        "count_lock": {
            "enforced": count_lock_enforced,
            "expected": EXPECTED_COUNT_LOCK,
            "actual": {
                "master_total": summary["master_total"],
                "reviewable_total": summary["reviewable_total"],
                "system_blocklist_total": summary["system_blocklist_total"],
            },
        },
        "paths": {
            "items_path": str(items_path),
            "tags_path": str(tags_path),
            "master_path": str(master_path),
            "reviews_dir": str(reviews_dir),
        },
        "source_sha256": {
            "items_itemscript": file_sha256(items_path),
            "tags_by_fulltype": file_sha256(tags_path),
        },
        "review_contract": {
            "source_priority": SOURCE_PRIORITY,
            "conflict_resolution": "higher_source_wins_then_standardization_impossible",
            "notes_required_when": [
                "ACQ_NULL + STANDARDIZATION_IMPOSSIBLE",
                "MANUAL_OVERRIDE_CANDIDATE",
            ],
        },
        "review_waves": REVIEW_WAVES,
        "pilot_bucket": "Consumable.3-C",
        "bucket_counts": summary["bucket_counts"],
        "template_init": template_stats,
    }


def format_unknown_no_tag(items: list[dict[str, Any]]) -> str:
    preview = items[:20]
    lines = [
        "Found no-tag non-system items; generator refuses to continue.",
        f"Total unknown items: {len(items)}",
    ]
    for item in preview:
        lines.append(
            "  - {item_id} (DisplayCategory={display_category}, Type={type_value}, DisplayName={display_name})".format(
                **item
            )
        )
    if len(items) > len(preview):
        lines.append(f"  ... +{len(items) - len(preview)} more")
    return "\n".join(lines)


def generate_acquisition_master(
    *,
    items_path: Path,
    tags_path: Path,
    staging_dir: Path,
    enforce_count_lock: bool = True,
) -> dict[str, Any]:
    items_data = load_json(items_path)
    tags_payload = load_json(tags_path)
    tags_items = tags_payload.get("items", {})

    master_rows, unknown_no_tag = build_master_rows(items_data, tags_items)
    if unknown_no_tag:
        raise ValueError(format_unknown_no_tag(unknown_no_tag))

    summary = summarize_master_rows(master_rows)
    if enforce_count_lock:
        assert_count_lock(summary)

    master_path = staging_dir / MASTER_FILE_NAME
    manifest_path = staging_dir / MANIFEST_FILE_NAME
    reviews_dir = staging_dir / "reviews"

    write_jsonl(master_path, master_rows)
    template_stats = create_missing_review_templates(master_rows, reviews_dir)

    manifest = build_manifest(
        summary,
        items_path=items_path,
        tags_path=tags_path,
        master_path=master_path,
        reviews_dir=reviews_dir,
        count_lock_enforced=enforce_count_lock,
        template_stats=template_stats,
    )
    write_json(manifest_path, manifest)

    return {
        "master_path": master_path,
        "manifest_path": manifest_path,
        "summary": summary,
        "template_stats": template_stats,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate DVF acquisition coverage staging files.")
    parser.add_argument(
        "--items-path",
        type=Path,
        default=INPUT_DIR / "items_itemscript.json",
        help="Path to items_itemscript.json",
    )
    parser.add_argument(
        "--tags-path",
        type=Path,
        default=OUTPUT_DIR / "tags_by_fulltype.json",
        help="Path to tags_by_fulltype.json",
    )
    parser.add_argument(
        "--staging-dir",
        type=Path,
        default=STAGING_DIR,
        help="Output staging directory",
    )
    parser.add_argument(
        "--skip-count-lock",
        action="store_true",
        help="Allow count drift for tests or exploratory runs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = generate_acquisition_master(
        items_path=args.items_path,
        tags_path=args.tags_path,
        staging_dir=args.staging_dir,
        enforce_count_lock=not args.skip_count_lock,
    )

    summary = result["summary"]
    template_stats = result["template_stats"]
    created = len(template_stats["created_files"])
    skipped = len(template_stats["skipped_existing_files"])

    print("Acquisition master generated")
    print(f"  Master total: {summary['master_total']}")
    print(f"  Reviewable total: {summary['reviewable_total']}")
    print(f"  System blocklist total: {summary['system_blocklist_total']}")
    print(f"  Review templates created: {created}")
    print(f"  Review templates kept: {skipped}")
    print(f"  Master path: {result['master_path']}")
    print(f"  Manifest path: {result['manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
