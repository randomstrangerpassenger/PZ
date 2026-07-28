from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .acquisition_lexical_utils import load_jsonl, write_json, write_jsonl
    from .body_role_lexical_cleanup import cleanup_facts_rows
    from .build_acquisition_promotion_subset_preview import diff_rendered_entries
    from .compose_layer3_text import OVERLAY_PATH, STAGING_COMPOSE_CONTEXT, build_rendered
    from .export_dvf_3_3_lua_bridge import export_lua_bridge
    from .validate_interaction_cluster_phase_d_runtime import BULLET_COMPAT_PATH, build_phase_d_runtime_report
    from .validate_interaction_cluster_rendered import validate_rendered
    from .validate_layer3_decisions import build_layer3_decisions_validation_report
except ImportError:
    from acquisition_lexical_utils import load_jsonl, write_json, write_jsonl
    from body_role_lexical_cleanup import cleanup_facts_rows
    from build_acquisition_promotion_subset_preview import diff_rendered_entries
    from compose_layer3_text import OVERLAY_PATH, STAGING_COMPOSE_CONTEXT, build_rendered
    from export_dvf_3_3_lua_bridge import export_lua_bridge
    from validate_interaction_cluster_phase_d_runtime import BULLET_COMPAT_PATH, build_phase_d_runtime_report
    from validate_interaction_cluster_rendered import validate_rendered
    from validate_layer3_decisions import build_layer3_decisions_validation_report


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
AUTHORITY_DIR = ROOT / "staging" / "second_pass_backlog_132" / "sprint7_residual_closure"

AUTHORITY_FACTS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_facts.jsonl"
AUTHORITY_DECISIONS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_decisions.jsonl"
AUTHORITY_RENDERED_PATH = AUTHORITY_DIR / "sprint7_overlay_preview.rendered.json"
AUTHORITY_RENDERED_VALIDATION_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_validation_report.json"
AUTHORITY_DECISIONS_VALIDATION_PATH = AUTHORITY_DIR / "sprint7_body_role_lexical_decisions_validation_report.json"
AUTHORITY_RUNTIME_SUMMARY_PATH = AUTHORITY_DIR / "sprint7_runtime_summary.json"
AUTHORITY_RUNTIME_NOTE_PATH = AUTHORITY_DIR / "sprint7_runtime_note.md"
AUTHORITY_CLEANUP_NOTE_PATH = AUTHORITY_DIR / "sprint7_body_role_lexical_cleanup_note.md"
AUTHORITY_CLEANUP_REPORT_PATH = AUTHORITY_DIR / "sprint7_body_role_lexical_cleanup_report.json"
AUTHORITY_BASELINE_FACTS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_pre_body_role_lexical_facts.jsonl"
AUTHORITY_BASELINE_DECISIONS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_pre_body_role_lexical_decisions.jsonl"
AUTHORITY_BASELINE_RENDERED_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_pre_body_role_lexical.rendered.json"
AUTHORITY_BASELINE_RENDERED_VALIDATION_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_pre_body_role_lexical_validation_report.json"
AUTHORITY_BASELINE_STYLE_LOG_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_pre_body_role_lexical_style_log.jsonl"
AUTHORITY_PROMOTED_STYLE_LOG_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_post_body_role_lexical_style_log.jsonl"
AUTHORITY_LUA_PATH = AUTHORITY_DIR / "IrisLayer3Data.lua"
AUTHORITY_BRIDGE_REPORT_PATH = AUTHORITY_DIR / "sprint7_lua_bridge_report.json"
AUTHORITY_RUNTIME_REPORT_PATH = AUTHORITY_DIR / "sprint7_runtime_report.json"

BODY_ROLE_LEXICAL_NOTE_MARKER = "## Body-Role Lexical Cleanup"

PREFERRED_CHANGED_VALIDATION_ITEMS = (
    "Base.223Box",
    "Base.Bowl",
    "Base.Hinge",
    "Base.TreeBranch",
    "Base.CarBattery1",
    "farming.BroccoliBagSeed",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_cleanup_note(report: dict[str, Any]) -> str:
    lines = [
        "# Sprint 7 Body-Role Lexical Cleanup Note",
        "",
        f"- changed facts count: `{report['changed_facts_count']}`",
        f"- rendered changed count: `{report['rendered_changed_count']}`",
        f"- unexpected rendered changes: `{report['unexpected_rendered_changed_count']}`",
        f"- expected-but-unchanged count: `{report['expected_but_unchanged_count']}`",
        f"- introduced rendered fail / warn: `{report['introduced_rendered_hard_fail_count']} / {report['introduced_rendered_warn_count']}`",
        f"- decisions hard fail: `{report['decisions_contract_hard_fail_count']}`",
        f"- residual translationese count: `{report['residual_translationese_count']}`",
        f"- runtime report status: `{report['runtime_report_status']}`",
        f"- authority preview ready: `{str(report['sprint7_authority_preview_ready']).lower()}`",
        "",
    ]
    return "\n".join(lines)


def build_runtime_note(existing_note_text: str, report: dict[str, Any]) -> str:
    base_text = existing_note_text
    if BODY_ROLE_LEXICAL_NOTE_MARKER in base_text:
        base_text = base_text.split(BODY_ROLE_LEXICAL_NOTE_MARKER, 1)[0].rstrip()
    else:
        base_text = base_text.rstrip()

    lines = [base_text, "", BODY_ROLE_LEXICAL_NOTE_MARKER, ""]
    lines.extend(
        [
            f"- changed facts count: `{report['changed_facts_count']}`",
            f"- rendered changed count: `{report['rendered_changed_count']}`",
            f"- unexpected rendered changes: `{report['unexpected_rendered_changed_count']}`",
            f"- expected-but-unchanged count: `{report['expected_but_unchanged_count']}`",
            f"- introduced rendered fail / warn: `{report['introduced_rendered_hard_fail_count']} / {report['introduced_rendered_warn_count']}`",
            f"- decisions hard fail: `{report['decisions_contract_hard_fail_count']}`",
            f"- residual translationese count: `{report['residual_translationese_count']}`",
            f"- runtime report status: `{report['runtime_report_status']}`",
            f"- authority preview ready: `{str(report['sprint7_authority_preview_ready']).lower()}`",
            "",
        ]
    )
    return "\n".join(lines)


def update_runtime_summary(*, runtime_summary_path: Path, report: dict[str, Any]) -> dict[str, Any]:
    summary = load_json(runtime_summary_path) if runtime_summary_path.exists() else {
        "schema_version": "second-pass-sprint7-runtime-summary-v1"
    }
    summary["runtime_report_status"] = report["runtime_report_status"]
    summary["body_role_lexical_cleanup"] = {
        "generated_at": report["generated_at"],
        "facts_path": report["authority_facts_path"],
        "decisions_path": report["authority_decisions_path"],
        "rendered_path": report["authority_rendered_path"],
        "cleanup_report_ref": report["cleanup_report_ref"],
        "rendered_validation_ref": report["authority_rendered_validation_ref"],
        "decisions_validation_ref": report["authority_decisions_validation_ref"],
        "lua_bridge_ref": report["authority_bridge_report_ref"],
        "runtime_report_ref": report["authority_runtime_report_ref"],
        "changed_facts_count": report["changed_facts_count"],
        "rendered_changed_count": report["rendered_changed_count"],
        "unexpected_rendered_changed_count": report["unexpected_rendered_changed_count"],
        "expected_but_unchanged_count": report["expected_but_unchanged_count"],
        "rendered_hard_fail_count": report["rendered_hard_fail_count"],
        "rendered_warn_count": report["rendered_warn_count"],
        "introduced_rendered_hard_fail_count": report["introduced_rendered_hard_fail_count"],
        "introduced_rendered_warn_count": report["introduced_rendered_warn_count"],
        "decisions_contract_hard_fail_count": report["decisions_contract_hard_fail_count"],
        "residual_translationese_count": report["residual_translationese_count"],
        "sprint7_authority_preview_ready": report["sprint7_authority_preview_ready"],
    }
    write_json(runtime_summary_path, summary)
    return summary


def select_changed_validation_items(
    *,
    changed_items: list[str],
    rendered_entries: dict[str, Any],
    max_count: int = 6,
) -> list[dict[str, str]]:
    selected: list[str] = []
    changed_set = set(changed_items)
    for item_id in PREFERRED_CHANGED_VALIDATION_ITEMS:
        if item_id in changed_set and item_id in rendered_entries:
            selected.append(item_id)
    for item_id in changed_items:
        if item_id in rendered_entries and item_id not in selected:
            selected.append(item_id)
        if len(selected) >= max_count:
            break
    return [
        {
            "item_id": item_id,
            "text_ko": str(rendered_entries[item_id].get("text_ko") or ""),
        }
        for item_id in selected[:max_count]
    ]


def build_body_role_lexical_cleanup_authority(
    *,
    authority_facts_path: Path = AUTHORITY_FACTS_PATH,
    authority_decisions_path: Path = AUTHORITY_DECISIONS_PATH,
    authority_rendered_path: Path = AUTHORITY_RENDERED_PATH,
    authority_rendered_validation_path: Path = AUTHORITY_RENDERED_VALIDATION_PATH,
    authority_decisions_validation_path: Path = AUTHORITY_DECISIONS_VALIDATION_PATH,
    authority_runtime_summary_path: Path = AUTHORITY_RUNTIME_SUMMARY_PATH,
    authority_runtime_note_path: Path = AUTHORITY_RUNTIME_NOTE_PATH,
    authority_cleanup_note_path: Path = AUTHORITY_CLEANUP_NOTE_PATH,
    authority_cleanup_report_path: Path = AUTHORITY_CLEANUP_REPORT_PATH,
    authority_baseline_facts_path: Path = AUTHORITY_BASELINE_FACTS_PATH,
    authority_baseline_decisions_path: Path = AUTHORITY_BASELINE_DECISIONS_PATH,
    authority_baseline_rendered_path: Path = AUTHORITY_BASELINE_RENDERED_PATH,
    authority_baseline_rendered_validation_path: Path = AUTHORITY_BASELINE_RENDERED_VALIDATION_PATH,
    authority_baseline_style_log_path: Path = AUTHORITY_BASELINE_STYLE_LOG_PATH,
    authority_promoted_style_log_path: Path = AUTHORITY_PROMOTED_STYLE_LOG_PATH,
    authority_lua_path: Path = AUTHORITY_LUA_PATH,
    authority_bridge_report_path: Path = AUTHORITY_BRIDGE_REPORT_PATH,
    authority_runtime_report_path: Path = AUTHORITY_RUNTIME_REPORT_PATH,
    compose_profiles_path: Path = DATA_DIR / "compose_profiles.json",
    overlay_path: Path | None = OVERLAY_PATH,
    layer3_renderer_path: Path | None = None,
    boot_path: Path | None = None,
    main_path: Path | None = None,
    context_menu_path: Path | None = None,
    bullet_compat_path: Path | None = None,
    browser_path: Path | None = None,
    panel_path: Path | None = None,
    wiki_sections_path: Path | None = None,
) -> dict[str, Any]:
    baseline_facts_rows = load_jsonl(authority_facts_path)
    baseline_decisions_rows = load_jsonl(authority_decisions_path)
    write_jsonl(authority_baseline_facts_path, baseline_facts_rows)
    write_jsonl(authority_baseline_decisions_path, baseline_decisions_rows)

    build_rendered(
        authority_facts_path,
        authority_decisions_path,
        compose_profiles_path,
        authority_baseline_rendered_path,
        overlay_path=overlay_path,
        style_log_path=authority_baseline_style_log_path,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )
    baseline_rendered_validation = validate_rendered(
        decisions_path=authority_decisions_path,
        rendered_path=authority_baseline_rendered_path,
        report_path=authority_baseline_rendered_validation_path,
    )

    cleaned_facts_rows, cleanup_summary = cleanup_facts_rows(baseline_facts_rows)
    write_jsonl(authority_facts_path, cleaned_facts_rows)

    build_rendered(
        authority_facts_path,
        authority_decisions_path,
        compose_profiles_path,
        authority_rendered_path,
        overlay_path=overlay_path,
        style_log_path=authority_promoted_style_log_path,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )

    rendered_changed_count, changed_items = diff_rendered_entries(
        baseline_rendered_path=authority_baseline_rendered_path,
        promoted_rendered_path=authority_rendered_path,
    )
    changed_item_set = set(changed_items)
    expected_changed_item_set = set(cleanup_summary["changed_item_ids"])
    unexpected_changed_items = sorted(changed_item_set - expected_changed_item_set)
    expected_but_unchanged_items = sorted(expected_changed_item_set - changed_item_set)

    rendered_validation = validate_rendered(
        decisions_path=authority_decisions_path,
        rendered_path=authority_rendered_path,
        report_path=authority_rendered_validation_path,
    )
    baseline_hard_fail_rows = set(baseline_rendered_validation["hard_fail_rows"])
    promoted_hard_fail_rows = set(rendered_validation["hard_fail_rows"])
    baseline_warn_rows = set(baseline_rendered_validation["warn_rows"])
    promoted_warn_rows = set(rendered_validation["warn_rows"])
    introduced_rendered_hard_fail_rows = sorted(promoted_hard_fail_rows - baseline_hard_fail_rows)
    introduced_rendered_warn_rows = sorted(promoted_warn_rows - baseline_warn_rows)
    resolved_rendered_hard_fail_rows = sorted(baseline_hard_fail_rows - promoted_hard_fail_rows)
    resolved_rendered_warn_rows = sorted(baseline_warn_rows - promoted_warn_rows)

    decisions_validation = build_layer3_decisions_validation_report(
        facts_path=authority_facts_path,
        decisions_path=authority_decisions_path,
        report_path=authority_decisions_validation_path,
    )
    bridge_report = export_lua_bridge(
        rendered_path=authority_rendered_path,
        lua_output_path=authority_lua_path,
        report_path=authority_bridge_report_path,
        chunk_output_dir=authority_lua_path.with_name("IrisLayer3DataChunks"),
        chunk_manifest_path=authority_lua_path.with_name("IrisLayer3DataChunks.lua"),
    )

    runtime_report_kwargs: dict[str, Any] = {
        "rendered_path": authority_rendered_path,
        "bridge_report_path": authority_bridge_report_path,
        "layer3_chunk_manifest_path": authority_lua_path.with_name("IrisLayer3DataChunks.lua"),
        "layer3_chunk_dir": authority_lua_path.with_name("IrisLayer3DataChunks"),
        "output_path": authority_runtime_report_path,
    }
    if layer3_renderer_path is not None:
        runtime_report_kwargs["layer3_renderer_path"] = layer3_renderer_path
    if boot_path is not None:
        runtime_report_kwargs["boot_path"] = boot_path
    if main_path is not None:
        runtime_report_kwargs["main_path"] = main_path
    if context_menu_path is not None:
        runtime_report_kwargs["context_menu_path"] = context_menu_path
    if bullet_compat_path is not None:
        runtime_report_kwargs["bullet_compat_path"] = bullet_compat_path
    if browser_path is not None:
        runtime_report_kwargs["browser_path"] = browser_path
    if panel_path is not None:
        runtime_report_kwargs["panel_path"] = panel_path
    if wiki_sections_path is not None:
        runtime_report_kwargs["wiki_sections_path"] = wiki_sections_path
    runtime_report = build_phase_d_runtime_report(**runtime_report_kwargs)

    rendered_entries = load_json(authority_rendered_path).get("entries", {})
    changed_samples = select_changed_validation_items(
        changed_items=cleanup_summary["changed_item_ids"],
        rendered_entries=rendered_entries,
    )
    residual_translationese_count = sum(cleanup_summary["residual_translationese_counts"].values())

    report = {
        "schema_version": "sprint7-body-role-lexical-cleanup-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authority_facts_path": str(authority_facts_path),
        "authority_decisions_path": str(authority_decisions_path),
        "authority_rendered_path": str(authority_rendered_path),
        "authority_rendered_validation_ref": str(authority_rendered_validation_path),
        "authority_decisions_validation_ref": str(authority_decisions_validation_path),
        "authority_bridge_report_ref": str(authority_bridge_report_path),
        "authority_runtime_report_ref": str(authority_runtime_report_path),
        "authority_runtime_summary_ref": str(authority_runtime_summary_path),
        "cleanup_report_ref": str(authority_cleanup_report_path),
        "changed_facts_count": int(cleanup_summary["changed_count"]),
        "changed_rule_counts": cleanup_summary["rule_counts"],
        "changed_item_samples": cleanup_summary["changed_item_ids"][:20],
        "rendered_changed_count": rendered_changed_count,
        "rendered_changed_samples": changed_items[:20],
        "unexpected_rendered_changed_count": len(unexpected_changed_items),
        "unexpected_rendered_changed_samples": unexpected_changed_items[:20],
        "expected_but_unchanged_count": len(expected_but_unchanged_items),
        "expected_but_unchanged_samples": expected_but_unchanged_items[:20],
        "baseline_rendered_hard_fail_count": int(baseline_rendered_validation["hard_fail_count"]),
        "baseline_rendered_warn_count": int(baseline_rendered_validation["warn_count"]),
        "rendered_hard_fail_count": int(rendered_validation["hard_fail_count"]),
        "rendered_warn_count": int(rendered_validation["warn_count"]),
        "introduced_rendered_hard_fail_count": len(introduced_rendered_hard_fail_rows),
        "introduced_rendered_hard_fail_samples": introduced_rendered_hard_fail_rows[:20],
        "introduced_rendered_warn_count": len(introduced_rendered_warn_rows),
        "introduced_rendered_warn_samples": introduced_rendered_warn_rows[:20],
        "resolved_rendered_hard_fail_count": len(resolved_rendered_hard_fail_rows),
        "resolved_rendered_hard_fail_samples": resolved_rendered_hard_fail_rows[:20],
        "resolved_rendered_warn_count": len(resolved_rendered_warn_rows),
        "resolved_rendered_warn_samples": resolved_rendered_warn_rows[:20],
        "decisions_contract_hard_fail_count": int(decisions_validation["hard_fail_count"]),
        "runtime_report_status": runtime_report.get("overall_status"),
        "bridge_runtime_entry_count": bridge_report.get("runtime_entry_count"),
        "residual_translationese_count": residual_translationese_count,
        "residual_translationese_counts": cleanup_summary["residual_translationese_counts"],
        "changed_validation_samples": changed_samples,
        "sprint7_authority_preview_ready": (
            len(introduced_rendered_hard_fail_rows) == 0
            and len(introduced_rendered_warn_rows) == 0
            and decisions_validation["hard_fail_count"] == 0
            and len(unexpected_changed_items) == 0
            and residual_translationese_count == 0
            and runtime_report.get("overall_status") == "ready_for_in_game_validation"
        ),
    }
    write_json(authority_cleanup_report_path, report)
    summary = update_runtime_summary(runtime_summary_path=authority_runtime_summary_path, report=report)

    runtime_note_text = authority_runtime_note_path.read_text(encoding="utf-8") if authority_runtime_note_path.exists() else "# Sprint 7 Runtime Note\n"
    authority_runtime_note_path.write_text(build_runtime_note(runtime_note_text, report), encoding="utf-8")
    authority_cleanup_note_path.write_text(build_cleanup_note(report), encoding="utf-8")
    return {"report": report, "runtime_summary": summary}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply body-role lexical cleanup to sprint7 authority facts.")
    parser.add_argument("--authority-facts-path", type=Path, default=AUTHORITY_FACTS_PATH)
    parser.add_argument("--authority-decisions-path", type=Path, default=AUTHORITY_DECISIONS_PATH)
    parser.add_argument("--authority-rendered-path", type=Path, default=AUTHORITY_RENDERED_PATH)
    parser.add_argument("--authority-rendered-validation-path", type=Path, default=AUTHORITY_RENDERED_VALIDATION_PATH)
    parser.add_argument("--authority-decisions-validation-path", type=Path, default=AUTHORITY_DECISIONS_VALIDATION_PATH)
    parser.add_argument("--authority-runtime-summary-path", type=Path, default=AUTHORITY_RUNTIME_SUMMARY_PATH)
    parser.add_argument("--authority-runtime-note-path", type=Path, default=AUTHORITY_RUNTIME_NOTE_PATH)
    parser.add_argument("--authority-cleanup-note-path", type=Path, default=AUTHORITY_CLEANUP_NOTE_PATH)
    parser.add_argument("--authority-cleanup-report-path", type=Path, default=AUTHORITY_CLEANUP_REPORT_PATH)
    parser.add_argument("--authority-baseline-facts-path", type=Path, default=AUTHORITY_BASELINE_FACTS_PATH)
    parser.add_argument("--authority-baseline-decisions-path", type=Path, default=AUTHORITY_BASELINE_DECISIONS_PATH)
    parser.add_argument("--authority-baseline-rendered-path", type=Path, default=AUTHORITY_BASELINE_RENDERED_PATH)
    parser.add_argument("--authority-baseline-rendered-validation-path", type=Path, default=AUTHORITY_BASELINE_RENDERED_VALIDATION_PATH)
    parser.add_argument("--authority-baseline-style-log-path", type=Path, default=AUTHORITY_BASELINE_STYLE_LOG_PATH)
    parser.add_argument("--authority-promoted-style-log-path", type=Path, default=AUTHORITY_PROMOTED_STYLE_LOG_PATH)
    parser.add_argument("--authority-lua-path", type=Path, default=AUTHORITY_LUA_PATH)
    parser.add_argument("--authority-bridge-report-path", type=Path, default=AUTHORITY_BRIDGE_REPORT_PATH)
    parser.add_argument("--authority-runtime-report-path", type=Path, default=AUTHORITY_RUNTIME_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_body_role_lexical_cleanup_authority(
        authority_facts_path=args.authority_facts_path,
        authority_decisions_path=args.authority_decisions_path,
        authority_rendered_path=args.authority_rendered_path,
        authority_rendered_validation_path=args.authority_rendered_validation_path,
        authority_decisions_validation_path=args.authority_decisions_validation_path,
        authority_runtime_summary_path=args.authority_runtime_summary_path,
        authority_runtime_note_path=args.authority_runtime_note_path,
        authority_cleanup_note_path=args.authority_cleanup_note_path,
        authority_cleanup_report_path=args.authority_cleanup_report_path,
        authority_baseline_facts_path=args.authority_baseline_facts_path,
        authority_baseline_decisions_path=args.authority_baseline_decisions_path,
        authority_baseline_rendered_path=args.authority_baseline_rendered_path,
        authority_baseline_rendered_validation_path=args.authority_baseline_rendered_validation_path,
        authority_baseline_style_log_path=args.authority_baseline_style_log_path,
        authority_promoted_style_log_path=args.authority_promoted_style_log_path,
        authority_lua_path=args.authority_lua_path,
        authority_bridge_report_path=args.authority_bridge_report_path,
        authority_runtime_report_path=args.authority_runtime_report_path,
    )
    print("sprint7 body-role lexical cleanup written")
    print(json.dumps(payload["report"], ensure_ascii=False, indent=2))
    return 0 if payload["report"]["sprint7_authority_preview_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
