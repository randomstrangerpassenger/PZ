from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .acquisition_lexical_utils import load_jsonl, write_json
except ImportError:
    from acquisition_lexical_utils import load_jsonl, write_json


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_DIR = ROOT / "staging" / "second_pass_backlog_132" / "sprint7_residual_closure"
STAGING_DIR = ROOT / "staging" / "acquisition" / "phase4_validator"

FACTS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_facts.jsonl"
DECISIONS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_decisions.jsonl"
REPORT_PATH = STAGING_DIR / "layer3_decisions_validation_report.json"

NULL_REASON_ENUM = {"UBIQUITOUS_ITEM", "STANDARDIZATION_IMPOSSIBLE"}


def load_jsonl_map(path: Path) -> dict[str, dict[str, Any]]:
    return {row["item_id"]: row for row in load_jsonl(path)}


def build_layer3_decisions_validation_report(
    *,
    facts_path: Path = FACTS_PATH,
    decisions_path: Path = DECISIONS_PATH,
    report_path: Path = REPORT_PATH,
) -> dict[str, Any]:
    facts_map = load_jsonl_map(facts_path)
    decisions_map = load_jsonl_map(decisions_path)

    missing_decisions = sorted(item_id for item_id in facts_map if item_id not in decisions_map)
    missing_facts = sorted(item_id for item_id in decisions_map if item_id not in facts_map)
    facts_ref_mismatches: list[dict[str, Any]] = []
    null_reason_missing: list[str] = []
    null_reason_invalid: list[dict[str, Any]] = []
    null_reason_present_with_non_null_fact: list[str] = []

    for item_id, decisions_row in decisions_map.items():
        facts_row = facts_map.get(item_id)
        if facts_row is None:
            continue
        if decisions_row.get("facts_ref") not in {None, item_id}:
            facts_ref_mismatches.append(
                {
                    "item_id": item_id,
                    "facts_ref": decisions_row.get("facts_ref"),
                }
            )

        acquisition_hint = facts_row.get("acquisition_hint")
        acquisition_null_reason = decisions_row.get("acquisition_null_reason")
        if acquisition_hint is None:
            if acquisition_null_reason is None:
                null_reason_missing.append(item_id)
            elif acquisition_null_reason not in NULL_REASON_ENUM:
                null_reason_invalid.append(
                    {
                        "item_id": item_id,
                        "acquisition_null_reason": acquisition_null_reason,
                    }
                )
        elif acquisition_null_reason is not None:
            null_reason_present_with_non_null_fact.append(item_id)

    report = {
        "schema_version": "layer3-decisions-validation-report-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "facts_path": str(facts_path),
        "decisions_path": str(decisions_path),
        "facts_row_count": len(facts_map),
        "decisions_row_count": len(decisions_map),
        "missing_decisions_count": len(missing_decisions),
        "missing_decisions_samples": missing_decisions[:20],
        "missing_facts_count": len(missing_facts),
        "missing_facts_samples": missing_facts[:20],
        "facts_ref_mismatch_count": len(facts_ref_mismatches),
        "facts_ref_mismatch_samples": facts_ref_mismatches[:20],
        "null_reason_missing_count": len(null_reason_missing),
        "null_reason_missing_samples": null_reason_missing[:20],
        "null_reason_invalid_count": len(null_reason_invalid),
        "null_reason_invalid_samples": null_reason_invalid[:20],
        "null_reason_present_with_non_null_fact_count": len(null_reason_present_with_non_null_fact),
        "null_reason_present_with_non_null_fact_samples": null_reason_present_with_non_null_fact[:20],
        "hard_fail_count": (
            len(missing_decisions)
            + len(missing_facts)
            + len(facts_ref_mismatches)
            + len(null_reason_missing)
            + len(null_reason_invalid)
            + len(null_reason_present_with_non_null_fact)
        ),
    }
    write_json(report_path, report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate layer3 facts/decisions cross-file acquisition contract.")
    parser.add_argument("--facts-path", type=Path, default=FACTS_PATH)
    parser.add_argument("--decisions-path", type=Path, default=DECISIONS_PATH)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_layer3_decisions_validation_report(
        facts_path=args.facts_path,
        decisions_path=args.decisions_path,
        report_path=args.report_path,
    )
    print(
        "layer3 decisions validation written:",
        report["facts_row_count"],
        "facts rows ->",
        args.report_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
