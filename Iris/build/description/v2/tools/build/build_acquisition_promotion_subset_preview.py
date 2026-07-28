from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .acquisition_lexical_utils import load_jsonl, write_json, write_jsonl
    from .compose_layer3_text import build_rendered, load_json, OVERLAY_PATH, STAGING_COMPOSE_CONTEXT
except ImportError:
    from acquisition_lexical_utils import load_jsonl, write_json, write_jsonl
    from compose_layer3_text import build_rendered, load_json, OVERLAY_PATH, STAGING_COMPOSE_CONTEXT


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_DIR = ROOT / "staging" / "second_pass_backlog_132" / "sprint7_residual_closure"
PHASE3_DIR = ROOT / "staging" / "acquisition" / "phase3_execution"
STAGING_DIR = ROOT / "staging" / "acquisition" / "phase5_subset_preview"
DATA_DIR = ROOT / "data"

FACTS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_facts.jsonl"
DECISIONS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_decisions.jsonl"
FACTS_PATCH_PROMOTE_PATH = PHASE3_DIR / "acquisition_facts_patch.promote.jsonl"
DECISIONS_PATCH_PROMOTE_PATH = PHASE3_DIR / "acquisition_decisions_patch.promote.jsonl"

PREVIEW_FACTS_PATH = STAGING_DIR / "acquisition_promotion_subset_preview_facts.jsonl"
PREVIEW_DECISIONS_PATH = STAGING_DIR / "acquisition_promotion_subset_preview_decisions.jsonl"
BASELINE_RENDERED_PATH = STAGING_DIR / "acquisition_subset_baseline_rendered.json"
PROMOTED_RENDERED_PATH = STAGING_DIR / "acquisition_subset_promoted_rendered.json"
BASELINE_STYLE_LOG_PATH = STAGING_DIR / "acquisition_subset_baseline_style_log.jsonl"
PROMOTED_STYLE_LOG_PATH = STAGING_DIR / "acquisition_subset_promoted_style_log.jsonl"
REPORT_PATH = STAGING_DIR / "acquisition_promotion_subset_preview_report.json"


def load_jsonl_map(path: Path) -> dict[str, dict[str, Any]]:
    return {row["item_id"]: row for row in load_jsonl(path)}


def apply_facts_patch(facts_row: dict[str, Any], patch_row: dict[str, Any]) -> dict[str, Any]:
    updated = dict(facts_row)
    updated["acquisition_hint"] = patch_row.get("proposed_acquisition_hint")

    slot_meta = dict(updated.get("slot_meta") or {})
    proposed_slot_meta_patch = dict(patch_row.get("proposed_slot_meta_patch") or {})
    acquisition_patch = proposed_slot_meta_patch.get("acquisition_hint")
    if acquisition_patch is not None:
        slot_meta["acquisition_hint"] = acquisition_patch
    updated["slot_meta"] = slot_meta
    return updated


def apply_decisions_patch(decisions_row: dict[str, Any], patch_row: dict[str, Any]) -> dict[str, Any]:
    updated = dict(decisions_row)
    updated["acquisition_null_reason"] = patch_row.get("proposed_acquisition_null_reason")
    return updated


def diff_rendered_entries(
    *,
    baseline_rendered_path: Path,
    promoted_rendered_path: Path,
) -> tuple[int, list[str]]:
    baseline = load_json(baseline_rendered_path)
    promoted = load_json(promoted_rendered_path)
    baseline_entries = baseline.get("entries", {})
    promoted_entries = promoted.get("entries", {})

    changed_items: list[str] = []
    for item_id in sorted(set(baseline_entries) | set(promoted_entries)):
        baseline_entry = baseline_entries.get(item_id)
        promoted_entry = promoted_entries.get(item_id)
        if json.dumps(baseline_entry, ensure_ascii=False, sort_keys=True) != json.dumps(
            promoted_entry,
            ensure_ascii=False,
            sort_keys=True,
        ):
            changed_items.append(item_id)
    return len(changed_items), changed_items


def build_acquisition_promotion_subset_preview(
    *,
    facts_path: Path = FACTS_PATH,
    decisions_path: Path = DECISIONS_PATH,
    facts_patch_promote_path: Path = FACTS_PATCH_PROMOTE_PATH,
    decisions_patch_promote_path: Path = DECISIONS_PATCH_PROMOTE_PATH,
    preview_facts_path: Path = PREVIEW_FACTS_PATH,
    preview_decisions_path: Path = PREVIEW_DECISIONS_PATH,
    baseline_rendered_path: Path = BASELINE_RENDERED_PATH,
    promoted_rendered_path: Path = PROMOTED_RENDERED_PATH,
    baseline_style_log_path: Path = BASELINE_STYLE_LOG_PATH,
    promoted_style_log_path: Path = PROMOTED_STYLE_LOG_PATH,
    report_path: Path = REPORT_PATH,
    overlay_path: Path | None = OVERLAY_PATH,
) -> dict[str, Any]:
    facts_rows = load_jsonl(facts_path)
    decisions_rows = load_jsonl(decisions_path)
    facts_patch_map = load_jsonl_map(facts_patch_promote_path)
    decisions_patch_map = load_jsonl_map(decisions_patch_promote_path) if decisions_patch_promote_path.exists() else {}

    preview_facts_rows = [
        apply_facts_patch(row, facts_patch_map[row["item_id"]]) if row["item_id"] in facts_patch_map else row
        for row in facts_rows
    ]
    preview_decisions_rows = [
        apply_decisions_patch(row, decisions_patch_map[row["item_id"]]) if row["item_id"] in decisions_patch_map else row
        for row in decisions_rows
    ]

    write_jsonl(preview_facts_path, preview_facts_rows)
    write_jsonl(preview_decisions_path, preview_decisions_rows)

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
        preview_facts_path,
        preview_decisions_path,
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

    report = {
        "schema_version": "acquisition-promotion-subset-preview-report-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "facts_path": str(facts_path),
        "decisions_path": str(decisions_path),
        "facts_patch_promote_path": str(facts_patch_promote_path),
        "decisions_patch_promote_path": str(decisions_patch_promote_path),
        "facts_patch_count": len(facts_patch_map),
        "decisions_patch_count": len(decisions_patch_map),
        "preview_facts_path": str(preview_facts_path),
        "preview_decisions_path": str(preview_decisions_path),
        "baseline_rendered_path": str(baseline_rendered_path),
        "promoted_rendered_path": str(promoted_rendered_path),
        "rendered_changed_count": rendered_changed_count,
        "rendered_changed_samples": changed_items[:20],
    }
    write_json(report_path, report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build preview for promotion-ready acquisition subset and compare rendered output.")
    parser.add_argument("--facts-path", type=Path, default=FACTS_PATH)
    parser.add_argument("--decisions-path", type=Path, default=DECISIONS_PATH)
    parser.add_argument("--facts-patch-promote-path", type=Path, default=FACTS_PATCH_PROMOTE_PATH)
    parser.add_argument("--decisions-patch-promote-path", type=Path, default=DECISIONS_PATCH_PROMOTE_PATH)
    parser.add_argument("--preview-facts-path", type=Path, default=PREVIEW_FACTS_PATH)
    parser.add_argument("--preview-decisions-path", type=Path, default=PREVIEW_DECISIONS_PATH)
    parser.add_argument("--baseline-rendered-path", type=Path, default=BASELINE_RENDERED_PATH)
    parser.add_argument("--promoted-rendered-path", type=Path, default=PROMOTED_RENDERED_PATH)
    parser.add_argument("--baseline-style-log-path", type=Path, default=BASELINE_STYLE_LOG_PATH)
    parser.add_argument("--promoted-style-log-path", type=Path, default=PROMOTED_STYLE_LOG_PATH)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_acquisition_promotion_subset_preview(
        facts_path=args.facts_path,
        decisions_path=args.decisions_path,
        facts_patch_promote_path=args.facts_patch_promote_path,
        decisions_patch_promote_path=args.decisions_patch_promote_path,
        preview_facts_path=args.preview_facts_path,
        preview_decisions_path=args.preview_decisions_path,
        baseline_rendered_path=args.baseline_rendered_path,
        promoted_rendered_path=args.promoted_rendered_path,
        baseline_style_log_path=args.baseline_style_log_path,
        promoted_style_log_path=args.promoted_style_log_path,
        report_path=args.report_path,
    )
    print(
        "acquisition promotion subset preview written:",
        report["facts_patch_count"],
        "facts patches ->",
        args.report_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
