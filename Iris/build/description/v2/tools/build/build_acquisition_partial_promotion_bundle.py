from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .acquisition_lexical_utils import load_jsonl, write_json, write_jsonl
    from .build_acquisition_promotion_subset_preview import (
        apply_decisions_patch,
        apply_facts_patch,
        diff_rendered_entries,
    )
    from .compose_layer3_text import build_rendered, OVERLAY_PATH, STAGING_COMPOSE_CONTEXT
    from .validate_layer3_decisions import build_layer3_decisions_validation_report
except ImportError:
    from acquisition_lexical_utils import load_jsonl, write_json, write_jsonl
    from build_acquisition_promotion_subset_preview import (
        apply_decisions_patch,
        apply_facts_patch,
        diff_rendered_entries,
    )
    from compose_layer3_text import build_rendered, OVERLAY_PATH, STAGING_COMPOSE_CONTEXT
    from validate_layer3_decisions import build_layer3_decisions_validation_report


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_DIR = ROOT / "staging" / "second_pass_backlog_132" / "sprint7_residual_closure"
PHASE3_DIR = ROOT / "staging" / "acquisition" / "phase3_execution"
NULL_REASON_DIR = ROOT / "staging" / "acquisition" / "null_reason"
STAGING_DIR = ROOT / "staging" / "acquisition" / "promotion_bundle"
DATA_DIR = ROOT / "data"

FACTS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_facts.jsonl"
DECISIONS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_decisions.jsonl"
FACTS_PATCH_PATH = PHASE3_DIR / "acquisition_facts_patch.promote.jsonl"
DECISIONS_PATCH_PATH = NULL_REASON_DIR / "acquisition_null_reason_full_decisions_patch.review.jsonl"
FACTS_REVIEW_PATH = PHASE3_DIR / "acquisition_facts_patch.review.jsonl"
DECISIONS_VALIDATION_BASELINE_PATH = NULL_REASON_DIR / "acquisition_null_reason_full_preview_validation_report.json"

PROMOTED_FACTS_PATH = STAGING_DIR / "acquisition_partial_promoted_facts.jsonl"
PROMOTED_DECISIONS_PATH = STAGING_DIR / "acquisition_partial_promoted_decisions.jsonl"
BASELINE_RENDERED_PATH = STAGING_DIR / "acquisition_partial_baseline_rendered.json"
PROMOTED_RENDERED_PATH = STAGING_DIR / "acquisition_partial_promoted_rendered.json"
BASELINE_STYLE_LOG_PATH = STAGING_DIR / "acquisition_partial_baseline_style_log.jsonl"
PROMOTED_STYLE_LOG_PATH = STAGING_DIR / "acquisition_partial_promoted_style_log.jsonl"
VALIDATION_REPORT_PATH = STAGING_DIR / "acquisition_partial_promotion_validation_report.json"
REPORT_PATH = STAGING_DIR / "acquisition_partial_promotion_report.json"


def load_jsonl_map(path: Path) -> dict[str, dict[str, Any]]:
    return {row["item_id"]: row for row in load_jsonl(path)}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_acquisition_partial_promotion_bundle(
    *,
    facts_path: Path = FACTS_PATH,
    decisions_path: Path = DECISIONS_PATH,
    facts_patch_path: Path = FACTS_PATCH_PATH,
    decisions_patch_path: Path = DECISIONS_PATCH_PATH,
    facts_review_path: Path = FACTS_REVIEW_PATH,
    promoted_facts_path: Path = PROMOTED_FACTS_PATH,
    promoted_decisions_path: Path = PROMOTED_DECISIONS_PATH,
    baseline_rendered_path: Path = BASELINE_RENDERED_PATH,
    promoted_rendered_path: Path = PROMOTED_RENDERED_PATH,
    baseline_style_log_path: Path = BASELINE_STYLE_LOG_PATH,
    promoted_style_log_path: Path = PROMOTED_STYLE_LOG_PATH,
    validation_report_path: Path = VALIDATION_REPORT_PATH,
    report_path: Path = REPORT_PATH,
    overlay_path: Path | None = OVERLAY_PATH,
) -> dict[str, Any]:
    facts_rows = load_jsonl(facts_path)
    decisions_rows = load_jsonl(decisions_path)
    facts_patch_map = load_jsonl_map(facts_patch_path)
    decisions_patch_map = load_jsonl_map(decisions_patch_path)
    facts_review_rows = load_jsonl(facts_review_path)

    promoted_facts_rows = [
        apply_facts_patch(row, facts_patch_map[row["item_id"]]) if row["item_id"] in facts_patch_map else row
        for row in facts_rows
    ]
    promoted_decisions_rows = [
        apply_decisions_patch(row, decisions_patch_map[row["item_id"]]) if row["item_id"] in decisions_patch_map else row
        for row in decisions_rows
    ]

    write_jsonl(promoted_facts_path, promoted_facts_rows)
    write_jsonl(promoted_decisions_path, promoted_decisions_rows)

    build_rendered(
        facts_path,
        decisions_path,
        DATA_DIR / "compose_profiles.json",
        baseline_rendered_path,
        overlay_path=overlay_path,
        style_log_path=baseline_style_log_path,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )
    build_rendered(
        promoted_facts_path,
        promoted_decisions_path,
        DATA_DIR / "compose_profiles.json",
        promoted_rendered_path,
        overlay_path=overlay_path,
        style_log_path=promoted_style_log_path,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )

    rendered_changed_count, changed_items = diff_rendered_entries(
        baseline_rendered_path=baseline_rendered_path,
        promoted_rendered_path=promoted_rendered_path,
    )

    validation_report = build_layer3_decisions_validation_report(
        facts_path=promoted_facts_path,
        decisions_path=promoted_decisions_path,
        report_path=validation_report_path,
    )

    facts_review_pending = [row for row in facts_review_rows if row.get("patch_status") == "REVIEW_PENDING"]
    facts_promotion_ready = [row for row in facts_review_rows if row.get("patch_status") == "PROMOTION_READY"]
    expected_changed_items = sorted(
        row["item_id"]
        for row in facts_review_rows
        if row.get("patch_status") == "PROMOTION_READY"
        and row.get("current_acquisition_hint") != row.get("proposed_acquisition_hint")
    )
    changed_item_set = set(changed_items)
    expected_changed_item_set = set(expected_changed_items)
    unexpected_changed_items = sorted(changed_item_set - expected_changed_item_set)
    expected_but_unchanged_items = sorted(expected_changed_item_set - changed_item_set)

    report = {
        "schema_version": "acquisition-partial-promotion-report-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "facts_path": str(facts_path),
        "decisions_path": str(decisions_path),
        "facts_patch_path": str(facts_patch_path),
        "decisions_patch_path": str(decisions_patch_path),
        "promoted_facts_path": str(promoted_facts_path),
        "promoted_decisions_path": str(promoted_decisions_path),
        "facts_patch_count": len(facts_patch_map),
        "decisions_patch_count": len(decisions_patch_map),
        "facts_promotion_ready_count": len(facts_promotion_ready),
        "facts_review_pending_count": len(facts_review_pending),
        "facts_review_pending_samples": [row["item_id"] for row in facts_review_pending[:20]],
        "decisions_contract_hard_fail_count": validation_report["hard_fail_count"],
        "decisions_null_reason_missing_count": validation_report["null_reason_missing_count"],
        "decisions_null_reason_invalid_count": validation_report["null_reason_invalid_count"],
        "rendered_changed_count": rendered_changed_count,
        "rendered_changed_samples": changed_items[:20],
        "expected_rendered_change_candidate_count": len(expected_changed_items),
        "expected_rendered_change_candidate_samples": expected_changed_items[:20],
        "unexpected_rendered_changed_count": len(unexpected_changed_items),
        "unexpected_rendered_changed_samples": unexpected_changed_items[:20],
        "expected_but_unchanged_count": len(expected_but_unchanged_items),
        "expected_but_unchanged_samples": expected_but_unchanged_items[:20],
        "partial_promotion_ready": (
            validation_report["hard_fail_count"] == 0 and len(unexpected_changed_items) == 0
        ),
        "full_acquisition_promotion_ready": (
            validation_report["hard_fail_count"] == 0
            and len(unexpected_changed_items) == 0
            and len(facts_review_pending) == 0
        ),
        "full_promotion_blockers": [
            "facts_review_pending_rows_present" if len(facts_review_pending) > 0 else None,
            "unexpected_rendered_changes_present" if unexpected_changed_items else None,
        ],
        "closeout_snapshot": {
            "acquisition_rows": sum(1 for row in facts_rows if row.get("acquisition_hint") is not None),
            "mapped_facts_promoted": len(facts_patch_map),
            "null_reason_rows_explained": len(decisions_patch_map),
        },
    }
    report["full_promotion_blockers"] = [entry for entry in report["full_promotion_blockers"] if entry is not None]
    write_json(report_path, report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build acquisition partial promotion bundle and closeout report.")
    parser.add_argument("--facts-path", type=Path, default=FACTS_PATH)
    parser.add_argument("--decisions-path", type=Path, default=DECISIONS_PATH)
    parser.add_argument("--facts-patch-path", type=Path, default=FACTS_PATCH_PATH)
    parser.add_argument("--decisions-patch-path", type=Path, default=DECISIONS_PATCH_PATH)
    parser.add_argument("--facts-review-path", type=Path, default=FACTS_REVIEW_PATH)
    parser.add_argument("--promoted-facts-path", type=Path, default=PROMOTED_FACTS_PATH)
    parser.add_argument("--promoted-decisions-path", type=Path, default=PROMOTED_DECISIONS_PATH)
    parser.add_argument("--baseline-rendered-path", type=Path, default=BASELINE_RENDERED_PATH)
    parser.add_argument("--promoted-rendered-path", type=Path, default=PROMOTED_RENDERED_PATH)
    parser.add_argument("--baseline-style-log-path", type=Path, default=BASELINE_STYLE_LOG_PATH)
    parser.add_argument("--promoted-style-log-path", type=Path, default=PROMOTED_STYLE_LOG_PATH)
    parser.add_argument("--validation-report-path", type=Path, default=VALIDATION_REPORT_PATH)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_acquisition_partial_promotion_bundle(
        facts_path=args.facts_path,
        decisions_path=args.decisions_path,
        facts_patch_path=args.facts_patch_path,
        decisions_patch_path=args.decisions_patch_path,
        facts_review_path=args.facts_review_path,
        promoted_facts_path=args.promoted_facts_path,
        promoted_decisions_path=args.promoted_decisions_path,
        baseline_rendered_path=args.baseline_rendered_path,
        promoted_rendered_path=args.promoted_rendered_path,
        baseline_style_log_path=args.baseline_style_log_path,
        promoted_style_log_path=args.promoted_style_log_path,
        validation_report_path=args.validation_report_path,
        report_path=args.report_path,
    )
    print(
        "acquisition partial promotion bundle written:",
        report["facts_patch_count"],
        "facts patches +",
        report["decisions_patch_count"],
        "decisions patches ->",
        args.report_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
