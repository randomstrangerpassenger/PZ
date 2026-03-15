from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SCRIPT_DIR.parent
DVF_DIR = TOOLS_DIR / "dvf"
V2_ROOT = TOOLS_DIR.parent

sys.path.insert(0, str(DVF_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from generate_acquisition_master import (  # noqa: E402
    EXPECTED_COUNT_LOCK,
    MANIFEST_FILE_NAME,
    MASTER_FIELDS,
    MASTER_FILE_NAME,
    REVIEW_FIELDS,
    REVIEW_FILE_SUFFIX,
    REVIEW_WAVES,
    SOURCE_PRIORITY,
    STAGING_DIR as DEFAULT_STAGING_DIR,
    SYSTEM_BLOCKLIST_BUCKET,
    file_sha256,
    load_json,
    load_jsonl,
    ordered_bucket_names,
)
from validate_layer3_decisions import ACTIVE_REASON_CODES, SILENT_REASON_CODES  # noqa: E402
from validate_layer3_facts import (  # noqa: E402
    JOSA_TOKEN_RE,
    NON_DECIMAL_PERIOD_RE,
    SLOT_CHAR_FAIL,
    SLOT_CHAR_WARN,
)

ALLOWED_DISPOSITIONS = {"UNREVIEWED", "ACQ_HINT", "ACQ_NULL", "SYSTEM_EXCLUDED"}
ALLOWED_NULL_REASONS = {"STANDARDIZATION_IMPOSSIBLE", "UBIQUITOUS_ITEM"}
ALLOWED_CANDIDATE_STATES = {"UNSET", "KEEP_SILENT", "PROMOTE_ACTIVE", "MANUAL_OVERRIDE_CANDIDATE"}
DERIVED_FIELDS = (
    "item_id",
    "display_name",
    "display_category",
    "type_value",
    "primary_subcategory",
    "coverage_bucket",
)


def parse_review_bucket(path: Path) -> str:
    name = path.name
    if not name.endswith(REVIEW_FILE_SUFFIX):
        raise ValueError(f"Invalid review file suffix: {path}")
    return name[: -len(REVIEW_FILE_SUFFIX)]


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate_required_keys(row: dict[str, Any], expected: tuple[str, ...], prefix: str, errors: list[str]) -> None:
    row_keys = set(row.keys())
    expected_keys = set(expected)
    missing = expected_keys - row_keys
    extra = row_keys - expected_keys

    if missing:
        errors.append(f"{prefix} missing keys: {sorted(missing)}")
    if extra:
        errors.append(f"{prefix} unexpected keys: {sorted(extra)}")


def validate_acquisition_hint_text(item_id: str, value: Any, forbidden_patterns: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"[{item_id}].acquisition_hint"

    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix} must be a non-empty string")
        return errors

    if "\n" in value:
        errors.append(f"{prefix} contains a newline")
    if NON_DECIMAL_PERIOD_RE.search(value):
        errors.append(f"{prefix} contains a non-decimal period")

    length = len(value)
    if length > SLOT_CHAR_FAIL:
        errors.append(f"{prefix} exceeds char limit: {length} > {SLOT_CHAR_FAIL}")
    elif length > SLOT_CHAR_WARN:
        errors.append(f"{prefix} exceeds warning threshold: {length} > {SLOT_CHAR_WARN}")

    for pattern in forbidden_patterns.get("hard_fail_patterns", []):
        if pattern in value:
            errors.append(f"{prefix} contains forbidden pattern: '{pattern}'")

    for pattern in forbidden_patterns.get("inference_patterns", []):
        if pattern in value:
            errors.append(f"{prefix} contains inference pattern: '{pattern}'")

    for pattern in forbidden_patterns.get("warning_patterns", []):
        if pattern in value:
            errors.append(f"{prefix} contains disallowed detail pattern: '{pattern}'")

    for pattern in forbidden_patterns.get("layer_boundary_patterns", {}).get("layer5_internal", []):
        if re.search(pattern, value):
            errors.append(f"{prefix} leaks internal layer detail: '{pattern}'")

    matches = JOSA_TOKEN_RE.findall(value)
    if matches:
        errors.append(f"{prefix} contains unresolved josa tokens: {matches}")

    return errors


def load_profiles(profiles_path: Path) -> set[str]:
    profiles = load_json(profiles_path)
    return set(profiles.keys())


def validate_acquisition_coverage(
    *,
    staging_dir: Path,
    require_complete: bool = False,
    forbidden_path: Path | None = None,
    profiles_path: Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    master_path = staging_dir / MASTER_FILE_NAME
    manifest_path = staging_dir / MANIFEST_FILE_NAME
    reviews_dir = staging_dir / "reviews"
    data_dir = V2_ROOT / "data"
    forbidden_path = forbidden_path or (data_dir / "forbidden_patterns.json")
    profiles_path = profiles_path or (data_dir / "compose_profiles.json")

    if not master_path.exists():
        return {"pass": False, "errors": [f"Missing master file: {master_path}"], "warnings": []}
    if not reviews_dir.exists():
        return {"pass": False, "errors": [f"Missing reviews directory: {reviews_dir}"], "warnings": []}
    if not forbidden_path.exists():
        return {"pass": False, "errors": [f"Missing forbidden patterns: {forbidden_path}"], "warnings": []}
    if not profiles_path.exists():
        return {"pass": False, "errors": [f"Missing compose profiles: {profiles_path}"], "warnings": []}

    forbidden_patterns = load_json(forbidden_path)
    valid_profiles = load_profiles(profiles_path)
    master_rows = load_jsonl(master_path)
    master_map: dict[str, dict[str, Any]] = {}

    for row in master_rows:
        prefix = f"[master:{row.get('item_id', '?')}]"
        validate_required_keys(row, MASTER_FIELDS, prefix, errors)
        item_id = row.get("item_id")
        if not item_id:
            errors.append(f"{prefix} missing item_id")
            continue
        if item_id in master_map:
            errors.append(f"{prefix} duplicate item_id in master")
            continue
        master_map[item_id] = row

    if manifest_path.exists():
        manifest = load_json(manifest_path)
        count_lock = manifest.get("count_lock", {})
        actual_counts = count_lock.get("actual", {})
        if count_lock.get("enforced", True):
            for key, expected in EXPECTED_COUNT_LOCK.items():
                if actual_counts.get(key) != expected:
                    errors.append(
                        f"[manifest] count_lock.actual.{key} mismatch: expected {expected}, got {actual_counts.get(key)}"
                    )
        master_counter = Counter(row["coverage_bucket"] for row in master_rows)
        derived_actual_counts = {
            "master_total": len(master_rows),
            "reviewable_total": sum(count for bucket, count in master_counter.items() if bucket != SYSTEM_BLOCKLIST_BUCKET),
            "system_blocklist_total": master_counter.get(SYSTEM_BLOCKLIST_BUCKET, 0),
        }
        for key, value in derived_actual_counts.items():
            if actual_counts.get(key) != value:
                errors.append(
                    f"[manifest] count_lock.actual.{key} inconsistent with master: manifest={actual_counts.get(key)} master={value}"
                )
        if manifest.get("source_sha256", {}).get("items_itemscript") is None:
            errors.append("[manifest] missing source_sha256.items_itemscript")
        if manifest.get("source_sha256", {}).get("tags_by_fulltype") is None:
            errors.append("[manifest] missing source_sha256.tags_by_fulltype")

    review_files = sorted(reviews_dir.glob(f"*{REVIEW_FILE_SUFFIX}"))
    if not review_files:
        errors.append(f"No review files found in {reviews_dir}")

    expected_buckets = {row["coverage_bucket"] for row in master_rows}
    actual_buckets = {parse_review_bucket(path) for path in review_files}
    missing_buckets = expected_buckets - actual_buckets
    extra_buckets = actual_buckets - expected_buckets
    if missing_buckets:
        errors.append(f"Missing review files for buckets: {sorted(missing_buckets)}")
    if extra_buckets:
        errors.append(f"Unexpected review files for buckets: {sorted(extra_buckets)}")

    review_map: dict[str, dict[str, Any]] = {}
    review_counts_by_bucket: dict[str, int] = {}

    for path in review_files:
        bucket = parse_review_bucket(path)
        rows = load_jsonl(path)
        review_counts_by_bucket[bucket] = len(rows)
        for index, row in enumerate(rows, start=1):
            prefix = f"[{path.name}:{index}]"
            validate_required_keys(row, REVIEW_FIELDS, prefix, errors)

            item_id = row.get("item_id")
            if not item_id:
                errors.append(f"{prefix} missing item_id")
                continue

            if item_id in review_map:
                errors.append(f"{prefix} duplicate item_id across review files: {item_id}")
                continue
            review_map[item_id] = row

            if row.get("coverage_bucket") != bucket:
                errors.append(
                    f"{prefix} coverage_bucket/file mismatch: row={row.get('coverage_bucket')} file={bucket}"
                )

            master_row = master_map.get(item_id)
            if master_row is None:
                errors.append(f"{prefix} item_id not present in master: {item_id}")
                continue

            for field in DERIVED_FIELDS:
                if row.get(field) != master_row.get(field):
                    errors.append(
                        f"{prefix} derived field drift for {field}: review={row.get(field)!r} master={master_row.get(field)!r}"
                    )

            disposition = row.get("coverage_disposition")
            if disposition not in ALLOWED_DISPOSITIONS:
                errors.append(f"{prefix} invalid coverage_disposition: {disposition!r}")
                continue

            candidate_state = row.get("candidate_state")
            if candidate_state not in ALLOWED_CANDIDATE_STATES:
                errors.append(f"{prefix} invalid candidate_state: {candidate_state!r}")

            acquisition_hint = row.get("acquisition_hint")
            null_reason = row.get("acquisition_null_reason")
            notes = row.get("notes")
            candidate_reason = row.get("candidate_reason_code")
            candidate_profile = row.get("candidate_compose_profile")

            if null_reason is not None and null_reason not in ALLOWED_NULL_REASONS:
                errors.append(f"{prefix} invalid acquisition_null_reason: {null_reason!r}")

            if disposition == "UNREVIEWED":
                if require_complete:
                    errors.append(f"{prefix} remains UNREVIEWED under --require-complete")
                if not is_blank(acquisition_hint):
                    errors.append(f"{prefix} UNREVIEWED row must not have acquisition_hint")
                if null_reason is not None:
                    errors.append(f"{prefix} UNREVIEWED row must not have acquisition_null_reason")
                if candidate_state != "UNSET":
                    errors.append(f"{prefix} UNREVIEWED row must keep candidate_state=UNSET")
                if candidate_reason is not None or candidate_profile is not None:
                    errors.append(f"{prefix} UNREVIEWED row must not set candidate metadata")
                continue

            if disposition == "ACQ_HINT":
                if null_reason is not None:
                    errors.append(f"{prefix} ACQ_HINT row must keep acquisition_null_reason=null")
                errors.extend(validate_acquisition_hint_text(item_id, acquisition_hint, forbidden_patterns))

            elif disposition == "ACQ_NULL":
                if not is_blank(acquisition_hint):
                    errors.append(f"{prefix} ACQ_NULL row must keep acquisition_hint=null")
                if null_reason is None:
                    errors.append(f"{prefix} ACQ_NULL row requires acquisition_null_reason")
                if null_reason == "STANDARDIZATION_IMPOSSIBLE" and is_blank(notes):
                    errors.append(f"{prefix} STANDARDIZATION_IMPOSSIBLE requires notes")

            elif disposition == "SYSTEM_EXCLUDED":
                if row.get("coverage_bucket") != SYSTEM_BLOCKLIST_BUCKET:
                    errors.append(f"{prefix} SYSTEM_EXCLUDED allowed only in {SYSTEM_BLOCKLIST_BUCKET}")
                if not is_blank(acquisition_hint):
                    errors.append(f"{prefix} SYSTEM_EXCLUDED row must keep acquisition_hint=null")
                if null_reason is not None:
                    errors.append(f"{prefix} SYSTEM_EXCLUDED row must keep acquisition_null_reason=null")
                if candidate_state != "UNSET":
                    errors.append(f"{prefix} SYSTEM_EXCLUDED row must keep candidate_state=UNSET")
                if candidate_reason is not None or candidate_profile is not None:
                    errors.append(f"{prefix} SYSTEM_EXCLUDED row must not set candidate metadata")

            if not is_blank(acquisition_hint) and null_reason is not None:
                errors.append(f"{prefix} cannot set acquisition_hint and acquisition_null_reason at the same time")

            if candidate_state == "UNSET":
                if candidate_reason is not None or candidate_profile is not None:
                    errors.append(f"{prefix} candidate_state=UNSET requires candidate metadata to be null")
            elif candidate_state == "KEEP_SILENT":
                if candidate_reason is not None and candidate_reason not in SILENT_REASON_CODES:
                    errors.append(f"{prefix} KEEP_SILENT candidate_reason_code must be a silent reason")
                if candidate_profile is not None:
                    errors.append(f"{prefix} KEEP_SILENT must not set candidate_compose_profile")
            elif candidate_state == "PROMOTE_ACTIVE":
                if candidate_reason is not None and candidate_reason not in ACTIVE_REASON_CODES:
                    errors.append(f"{prefix} PROMOTE_ACTIVE candidate_reason_code must be an active reason")
                if candidate_profile is not None and candidate_profile not in valid_profiles:
                    errors.append(f"{prefix} invalid candidate_compose_profile: {candidate_profile!r}")
            elif candidate_state == "MANUAL_OVERRIDE_CANDIDATE":
                if row.get("coverage_bucket") == SYSTEM_BLOCKLIST_BUCKET:
                    errors.append(f"{prefix} MANUAL_OVERRIDE_CANDIDATE not allowed in {SYSTEM_BLOCKLIST_BUCKET}")
                if candidate_reason is not None and candidate_reason not in ACTIVE_REASON_CODES:
                    errors.append(f"{prefix} MANUAL_OVERRIDE_CANDIDATE candidate_reason_code must be an active reason")
                if candidate_profile is not None and candidate_profile not in valid_profiles:
                    errors.append(f"{prefix} invalid candidate_compose_profile: {candidate_profile!r}")
                if is_blank(notes):
                    errors.append(f"{prefix} MANUAL_OVERRIDE_CANDIDATE requires notes")

    missing_review_rows = sorted(set(master_map) - set(review_map))
    extra_review_rows = sorted(set(review_map) - set(master_map))
    if missing_review_rows:
        errors.append(
            f"Missing review rows for {len(missing_review_rows)} master items: {missing_review_rows[:10]}"
            + (f" ... +{len(missing_review_rows) - 10}" if len(missing_review_rows) > 10 else "")
        )
    if extra_review_rows:
        errors.append(
            f"Unexpected review rows for {len(extra_review_rows)} items: {extra_review_rows[:10]}"
            + (f" ... +{len(extra_review_rows) - 10}" if len(extra_review_rows) > 10 else "")
        )

    for bucket in ordered_bucket_names(Counter(row["coverage_bucket"] for row in master_rows)):
        expected_rows = sum(1 for row in master_rows if row["coverage_bucket"] == bucket)
        actual_rows = review_counts_by_bucket.get(bucket)
        if actual_rows is None:
            continue
        if actual_rows != expected_rows:
            errors.append(
                f"[bucket:{bucket}] review row count mismatch: expected {expected_rows}, got {actual_rows}"
            )

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "master_rows": len(master_rows),
            "review_rows": len(review_map),
            "bucket_files": len(review_files),
            "require_complete": require_complete,
        },
        "review_contract": {
            "source_priority": SOURCE_PRIORITY,
            "review_waves": REVIEW_WAVES,
            "staging_dir": str(staging_dir),
            "master_sha256": file_sha256(master_path),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate DVF acquisition coverage staging files.")
    parser.add_argument(
        "--staging-dir",
        type=Path,
        default=DEFAULT_STAGING_DIR,
        help="Staging directory created by generate_acquisition_master.py",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Fail if any row remains UNREVIEWED.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_acquisition_coverage(
        staging_dir=args.staging_dir,
        require_complete=args.require_complete,
    )

    if result["pass"]:
        stats = result["stats"]
        print("Acquisition coverage validation passed")
        print(f"  Master rows: {stats['master_rows']}")
        print(f"  Review rows: {stats['review_rows']}")
        print(f"  Bucket files: {stats['bucket_files']}")
        print(f"  Require complete: {stats['require_complete']}")
        return 0

    print(f"Acquisition coverage validation failed ({len(result['errors'])} errors)")
    max_preview = 50
    for error in result["errors"][:max_preview]:
        print(f"  - {error}")
    if len(result["errors"]) > max_preview:
        print(f"  ... +{len(result['errors']) - max_preview} more")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
