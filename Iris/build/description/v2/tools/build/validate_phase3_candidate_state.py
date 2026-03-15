from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from generate_acquisition_master import load_json, load_jsonl
from phase3_candidate_state_lib import (
    ALL_REASON_CODES,
    BY_BUCKET_FILE_NAME,
    CANDIDATE_STATES,
    COMPOSE_PROFILES,
    DEFAULT_STAGING_DIR,
    GAPS_FILE_NAME,
    KEEP_REASON_CODES,
    MANUAL_REASON_CODES,
    OVERLAY_FILE_NAME,
    PHASE2_NULL_REASONS,
    PHASE2_TARGET_DISPOSITIONS,
    PHASE3_REVIEW_FIELDS,
    PROMOTE_REASON_CODES,
    SUMMARY_FILE_NAME,
    SYSTEM_BLOCKLIST_BUCKET,
    build_phase2_indices,
    build_phase3_reports,
    compute_overlay_determinism_sha,
    default_phase3_paths,
    is_blank,
    normalize_overlay_row,
)

SHA256_HEX_LEN = 64


def validate_required_keys(row: dict[str, Any], expected: tuple[str, ...], prefix: str, errors: list[str]) -> None:
    row_keys = set(row.keys())
    expected_keys = set(expected)
    missing = expected_keys - row_keys
    extra = row_keys - expected_keys
    if missing:
        errors.append(f"{prefix} missing keys: {sorted(missing)}")
    if extra:
        errors.append(f"{prefix} unexpected keys: {sorted(extra)}")


def compare_report_payload(label: str, path: Path, expected: dict[str, Any], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing {label} report: {path}")
        return
    actual = load_json(path)
    if actual != expected:
        errors.append(f"[{label}] report contents do not match computed payload: {path}")


def validate_phase3_candidate_state(
    *,
    staging_dir: Path,
    overlay_path: Path | None = None,
    summary_path: Path | None = None,
    by_bucket_path: Path | None = None,
    gaps_path: Path | None = None,
    require_complete: bool = False,
    compare_overlay_path: Path | None = None,
    compare_report_payloads: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    default_paths = default_phase3_paths(staging_dir)
    overlay_path = overlay_path or default_paths["overlay"]
    use_default_report_paths = compare_report_payloads and overlay_path == default_paths["overlay"]
    summary_path = summary_path or (
        default_paths["summary"] if use_default_report_paths and default_paths["summary"].exists() else None
    )
    by_bucket_path = by_bucket_path or (
        default_paths["by_bucket"] if use_default_report_paths and default_paths["by_bucket"].exists() else None
    )
    gaps_path = gaps_path or (default_paths["gaps"] if use_default_report_paths and default_paths["gaps"].exists() else None)

    phase2_targets, phase2_all_rows, phase2_errors = build_phase2_indices(staging_dir)
    errors.extend(phase2_errors)

    if not overlay_path.exists():
        return {"pass": False, "errors": [f"Missing phase3 overlay: {overlay_path}"], "warnings": warnings}

    overlay_rows = load_jsonl(overlay_path)
    normalized_rows: list[dict[str, Any]] = []
    seen_fulltypes: set[str] = set()
    decision_versions: set[str] = set()
    invalid_combo_count = 0
    snapshot_mismatch_count = 0

    for index, row in enumerate(overlay_rows, start=1):
        prefix = f"[{overlay_path.name}:{index}]"
        validate_required_keys(row, PHASE3_REVIEW_FIELDS, prefix, errors)

        fulltype = row.get("fulltype")
        if not fulltype:
            errors.append(f"{prefix} missing fulltype")
            continue
        if fulltype in seen_fulltypes:
            errors.append(f"{prefix} duplicate fulltype in overlay: {fulltype}")
            continue
        seen_fulltypes.add(fulltype)

        phase2_row = phase2_all_rows.get(fulltype)
        source = phase2_targets.get(fulltype)
        if source is None:
            if phase2_row is None:
                errors.append(f"{prefix} fulltype not present in phase2 review dataset: {fulltype}")
            else:
                disposition = phase2_row.get("coverage_disposition")
                if disposition == "UNREVIEWED":
                    errors.append(f"{prefix} phase2 source is still UNREVIEWED; overlay requires closed phase2 input")
                elif disposition == "SYSTEM_EXCLUDED" or phase2_row.get("coverage_bucket") == SYSTEM_BLOCKLIST_BUCKET:
                    errors.append(f"{prefix} phase2 source is SYSTEM_EXCLUDED; overlay contamination is not allowed")
                else:
                    errors.append(f"{prefix} fulltype is not a reviewable phase2 target: {fulltype}")
            continue

        row_snapshot_mismatch = False
        expected_snapshot = {
            "bucket_id": source["bucket_id"],
            "phase2_acquisition_state_snapshot": source["phase2_acquisition_state_snapshot"],
            "phase2_acquisition_hint_snapshot": source["phase2_acquisition_hint_snapshot"],
            "phase2_null_reason_snapshot": source["phase2_null_reason_snapshot"],
            "phase2_snapshot_hash": source["phase2_snapshot_hash"],
        }
        for field, expected_value in expected_snapshot.items():
            if row.get(field) != expected_value:
                row_snapshot_mismatch = True
                errors.append(
                    f"{prefix} snapshot mismatch for {field}: overlay={row.get(field)!r} phase2={expected_value!r}"
                )

        state_snapshot = row.get("phase2_acquisition_state_snapshot")
        hint_snapshot = row.get("phase2_acquisition_hint_snapshot")
        null_reason_snapshot = row.get("phase2_null_reason_snapshot")
        if state_snapshot not in PHASE2_TARGET_DISPOSITIONS:
            row_snapshot_mismatch = True
            errors.append(f"{prefix} invalid phase2_acquisition_state_snapshot: {state_snapshot!r}")
        elif state_snapshot == "ACQ_HINT":
            if not isinstance(hint_snapshot, str) or not hint_snapshot.strip():
                row_snapshot_mismatch = True
                errors.append(f"{prefix} ACQ_HINT snapshot requires non-empty phase2_acquisition_hint_snapshot")
            if null_reason_snapshot is not None:
                row_snapshot_mismatch = True
                errors.append(f"{prefix} ACQ_HINT snapshot must keep phase2_null_reason_snapshot=null")
        elif state_snapshot == "ACQ_NULL":
            if hint_snapshot is not None:
                row_snapshot_mismatch = True
                errors.append(f"{prefix} ACQ_NULL snapshot must keep phase2_acquisition_hint_snapshot=null")
            if null_reason_snapshot not in PHASE2_NULL_REASONS:
                row_snapshot_mismatch = True
                errors.append(f"{prefix} ACQ_NULL snapshot requires valid phase2_null_reason_snapshot")

        snapshot_hash = row.get("phase2_snapshot_hash")
        if not isinstance(snapshot_hash, str) or len(snapshot_hash) != SHA256_HEX_LEN:
            row_snapshot_mismatch = True
            errors.append(f"{prefix} phase2_snapshot_hash must be a 64-char sha256 hex string")

        candidate_state = row.get("candidate_state")
        candidate_reason_code = row.get("candidate_reason_code")
        candidate_compose_profile = row.get("candidate_compose_profile")
        notes = row.get("notes")

        row_invalid_combo = False
        if candidate_state not in CANDIDATE_STATES:
            row_invalid_combo = True
            errors.append(f"{prefix} invalid candidate_state: {candidate_state!r}")
        if is_blank(candidate_reason_code):
            row_invalid_combo = True
            errors.append(f"{prefix} missing candidate_reason_code")
        elif candidate_reason_code not in ALL_REASON_CODES:
            row_invalid_combo = True
            errors.append(f"{prefix} invalid candidate_reason_code: {candidate_reason_code!r}")

        decision_version = row.get("decision_version")
        if not isinstance(decision_version, str) or not decision_version.strip():
            errors.append(f"{prefix} decision_version must be a non-empty string")
        else:
            decision_versions.add(decision_version)

        if row.get("review_closed") is not True:
            errors.append(f"{prefix} review_closed must be true in the persisted overlay")

        if candidate_state == "KEEP_SILENT":
            if candidate_reason_code not in KEEP_REASON_CODES:
                row_invalid_combo = True
                errors.append(f"{prefix} KEEP_SILENT requires a KEEP reason_code")
            if candidate_compose_profile is not None:
                row_invalid_combo = True
                errors.append(f"{prefix} KEEP_SILENT must not set candidate_compose_profile")
            if not is_blank(notes):
                row_invalid_combo = True
                errors.append(f"{prefix} KEEP_SILENT must not use notes")
        elif candidate_state == "PROMOTE_ACTIVE":
            if candidate_reason_code not in PROMOTE_REASON_CODES:
                row_invalid_combo = True
                errors.append(f"{prefix} PROMOTE_ACTIVE requires a PROMOTE reason_code")
            if candidate_compose_profile not in COMPOSE_PROFILES:
                row_invalid_combo = True
                errors.append(f"{prefix} PROMOTE_ACTIVE requires a valid candidate_compose_profile")
            if not is_blank(notes):
                row_invalid_combo = True
                errors.append(f"{prefix} PROMOTE_ACTIVE must not use notes")
        elif candidate_state == "MANUAL_OVERRIDE_CANDIDATE":
            if candidate_reason_code not in MANUAL_REASON_CODES:
                row_invalid_combo = True
                errors.append(f"{prefix} MANUAL_OVERRIDE_CANDIDATE requires a MANUAL reason_code")
            if candidate_compose_profile is not None:
                row_invalid_combo = True
                errors.append(f"{prefix} MANUAL_OVERRIDE_CANDIDATE must not set candidate_compose_profile")
            if is_blank(notes):
                row_invalid_combo = True
                errors.append(f"{prefix} MANUAL_OVERRIDE_CANDIDATE requires notes")

        if row_invalid_combo:
            invalid_combo_count += 1
        if row_snapshot_mismatch:
            snapshot_mismatch_count += 1

        normalized_rows.append(normalize_overlay_row(row))

    if len(decision_versions) > 1:
        errors.append(f"[overlay] decision_version must be consistent within one overlay file: {sorted(decision_versions)}")

    if require_complete:
        missing_fulltypes = sorted(set(phase2_targets) - seen_fulltypes)
        if missing_fulltypes:
            preview = missing_fulltypes[:10]
            suffix = f" ... +{len(missing_fulltypes) - 10}" if len(missing_fulltypes) > 10 else ""
            errors.append(f"[overlay] missing phase3 rows for {len(missing_fulltypes)} phase2 targets: {preview}{suffix}")

    reports = build_phase3_reports(
        normalized_rows,
        invalid_combo_count=invalid_combo_count,
        snapshot_mismatch_count=snapshot_mismatch_count,
    )

    if compare_report_payloads and summary_path is not None:
        compare_report_payload("summary", summary_path, reports["summary"], errors)
    if compare_report_payloads and by_bucket_path is not None:
        compare_report_payload("by_bucket", by_bucket_path, reports["by_bucket"], errors)
    if compare_report_payloads and gaps_path is not None:
        compare_report_payload("gaps", gaps_path, reports["gaps"], errors)

    if compare_overlay_path is not None:
        if not compare_overlay_path.exists():
            errors.append(f"Missing comparison overlay: {compare_overlay_path}")
        else:
            compare_rows = load_jsonl(compare_overlay_path)
            compare_sha = compute_overlay_determinism_sha(compare_rows)
            if compare_sha != reports["summary"]["determinism_sha"]:
                errors.append(
                    "[determinism] compare_overlay produced a different determinism_sha: "
                    f"{compare_sha} != {reports['summary']['determinism_sha']}"
                )
            compare_reports = build_phase3_reports(compare_rows)
            if compare_reports["summary"] != reports["summary"]:
                errors.append("[determinism] compare_overlay produced a different summary breakdown")

    manual_rate = reports["summary"]["manual_rate"]
    if manual_rate > 0.2:
        warnings.append(f"manual_rate is high: {manual_rate}")

    dominant_reason = None
    dominant_count = 0
    for reason_code, count in reports["summary"]["reason_code_breakdown"].items():
        if count > dominant_count:
            dominant_reason = reason_code
            dominant_count = count
    if dominant_reason is not None and reports["summary"]["review_target_total"] > 0:
        dominance = dominant_count / reports["summary"]["review_target_total"]
        if dominance > 0.6:
            warnings.append(f"reason_code concentration is high: {dominant_reason}={dominant_count}")

    for bucket in reports["by_bucket"]["buckets"]:
        if bucket["target_count"] == 0 or bucket["manual_count"] == 0:
            continue
        manual_bucket_rate = bucket["manual_count"] / bucket["target_count"]
        if manual_bucket_rate > 0.3 and bucket["manual_count"] >= 3:
            warnings.append(
                f"manual concentration is high in {bucket['bucket_id']}: "
                f"{bucket['manual_count']}/{bucket['target_count']}"
            )

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "phase2_target_total": len(phase2_targets),
            "overlay_rows": len(overlay_rows),
            "decision_versions": sorted(decision_versions),
            "require_complete": require_complete,
            "invalid_combo_count": invalid_combo_count,
            "snapshot_mismatch_count": snapshot_mismatch_count,
        },
        "reports": reports,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase 3 candidate-state overlay files.")
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
        help=f"Overlay path. Default: <staging-dir>/phase3/{OVERLAY_FILE_NAME}",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help=f"Optional summary path. Default if present: <staging-dir>/phase3/{SUMMARY_FILE_NAME}",
    )
    parser.add_argument(
        "--by-bucket",
        type=Path,
        default=None,
        help=f"Optional by-bucket path. Default if present: <staging-dir>/phase3/{BY_BUCKET_FILE_NAME}",
    )
    parser.add_argument(
        "--gaps",
        type=Path,
        default=None,
        help=f"Optional gaps path. Default if present: <staging-dir>/phase3/{GAPS_FILE_NAME}",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Fail if overlay does not cover every closed phase2 target row.",
    )
    parser.add_argument(
        "--compare-overlay",
        type=Path,
        default=None,
        help="Optional second overlay file for 2-run determinism checks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_phase3_candidate_state(
        staging_dir=args.staging_dir,
        overlay_path=args.overlay,
        summary_path=args.summary,
        by_bucket_path=args.by_bucket,
        gaps_path=args.gaps,
        require_complete=args.require_complete,
        compare_overlay_path=args.compare_overlay,
    )
    if result["pass"]:
        stats = result["stats"]
        print("Phase 3 candidate-state validation passed")
        print(f"  Phase2 targets: {stats['phase2_target_total']}")
        print(f"  Overlay rows: {stats['overlay_rows']}")
        print(f"  Invalid combos: {stats['invalid_combo_count']}")
        print(f"  Snapshot mismatches: {stats['snapshot_mismatch_count']}")
        if result["warnings"]:
            print(f"  Warnings: {len(result['warnings'])}")
        return 0

    print(f"Phase 3 candidate-state validation failed ({len(result['errors'])} errors)")
    for error in result["errors"][:50]:
        print(f"  - {error}")
    if len(result["errors"]) > 50:
        print(f"  ... +{len(result['errors']) - 50} more")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
