from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .acquisition_lexical_utils import load_jsonl, write_json, write_jsonl
    from .build_acquisition_partial_promotion_bundle import build_acquisition_partial_promotion_bundle
    from .build_acquisition_promotion_subset_preview import diff_rendered_entries
    from .compose_layer3_text import OVERLAY_PATH, STAGING_COMPOSE_CONTEXT, build_rendered
    from .export_dvf_3_3_lua_bridge import export_lua_bridge
    from .validate_interaction_cluster_phase_d_runtime import BULLET_COMPAT_PATH, build_phase_d_runtime_report
    from .validate_interaction_cluster_rendered import validate_rendered
    from .validate_layer3_decisions import build_layer3_decisions_validation_report
except ImportError:
    from acquisition_lexical_utils import load_jsonl, write_json, write_jsonl
    from build_acquisition_partial_promotion_bundle import build_acquisition_partial_promotion_bundle
    from build_acquisition_promotion_subset_preview import diff_rendered_entries
    from compose_layer3_text import OVERLAY_PATH, STAGING_COMPOSE_CONTEXT, build_rendered
    from export_dvf_3_3_lua_bridge import export_lua_bridge
    from validate_interaction_cluster_phase_d_runtime import BULLET_COMPAT_PATH, build_phase_d_runtime_report
    from validate_interaction_cluster_rendered import validate_rendered
    from validate_layer3_decisions import build_layer3_decisions_validation_report


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
AUTHORITY_DIR = ROOT / "staging" / "second_pass_backlog_132" / "sprint7_residual_closure"
PROMOTION_DIR = ROOT / "staging" / "acquisition" / "promotion_bundle"
PHASE3_DIR = ROOT / "staging" / "acquisition" / "phase3_execution"
NULL_REASON_DIR = ROOT / "staging" / "acquisition" / "null_reason"

AUTHORITY_FACTS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_facts.jsonl"
AUTHORITY_DECISIONS_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_decisions.jsonl"
AUTHORITY_RENDERED_PATH = AUTHORITY_DIR / "sprint7_overlay_preview.rendered.json"
AUTHORITY_RENDERED_VALIDATION_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_validation_report.json"
AUTHORITY_DECISIONS_VALIDATION_PATH = AUTHORITY_DIR / "sprint7_acquisition_decisions_validation_report.json"
AUTHORITY_RUNTIME_SUMMARY_PATH = AUTHORITY_DIR / "sprint7_runtime_summary.json"
AUTHORITY_RUNTIME_NOTE_PATH = AUTHORITY_DIR / "sprint7_runtime_note.md"
AUTHORITY_PROMOTION_NOTE_PATH = AUTHORITY_DIR / "sprint7_acquisition_promotion_note.md"
AUTHORITY_PROMOTION_REPORT_PATH = AUTHORITY_DIR / "sprint7_acquisition_promotion_report.json"
AUTHORITY_CHECKLIST_PATH = AUTHORITY_DIR / "sprint7_in_game_validation_checklist.md"
AUTHORITY_VALIDATION_PACK_PATH = AUTHORITY_DIR / "second_pass_in_game_validation_pack.md"
AUTHORITY_CLOSURE_REPORT_PATH = AUTHORITY_DIR / "second_pass_closure_report.md"
AUTHORITY_BASELINE_RENDERED_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_pre_acquisition.rendered.json"
AUTHORITY_BASELINE_RENDERED_VALIDATION_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_pre_acquisition_validation_report.json"
AUTHORITY_BASELINE_STYLE_LOG_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_pre_acquisition_style_log.jsonl"
AUTHORITY_PROMOTED_STYLE_LOG_PATH = AUTHORITY_DIR / "sprint7_overlay_preview_post_acquisition_style_log.jsonl"
AUTHORITY_LUA_PATH = AUTHORITY_DIR / "IrisLayer3Data.lua"
AUTHORITY_BRIDGE_REPORT_PATH = AUTHORITY_DIR / "sprint7_lua_bridge_report.json"
AUTHORITY_RUNTIME_REPORT_PATH = AUTHORITY_DIR / "sprint7_runtime_report.json"

FULL_FACTS_PATCH_PATH = PHASE3_DIR / "acquisition_facts_patch.full.promote.jsonl"
FULL_FACTS_REVIEW_PATH = PHASE3_DIR / "acquisition_facts_patch.semantic.review.jsonl"
FULL_DECISIONS_PATCH_PATH = NULL_REASON_DIR / "acquisition_null_reason_full_decisions_patch.review.jsonl"
FULL_BUNDLE_FACTS_PATH = PROMOTION_DIR / "acquisition_full_promoted_facts.jsonl"
FULL_BUNDLE_DECISIONS_PATH = PROMOTION_DIR / "acquisition_full_promoted_decisions.jsonl"
FULL_BUNDLE_BASELINE_RENDERED_PATH = PROMOTION_DIR / "acquisition_full_baseline_rendered.json"
FULL_BUNDLE_PROMOTED_RENDERED_PATH = PROMOTION_DIR / "acquisition_full_promoted_rendered.json"
FULL_BUNDLE_BASELINE_STYLE_LOG_PATH = PROMOTION_DIR / "acquisition_full_baseline_style_log.jsonl"
FULL_BUNDLE_PROMOTED_STYLE_LOG_PATH = PROMOTION_DIR / "acquisition_full_promoted_style_log.jsonl"
FULL_BUNDLE_DECISIONS_VALIDATION_PATH = PROMOTION_DIR / "acquisition_full_promotion_validation_report.json"
FULL_BUNDLE_REPORT_PATH = PROMOTION_DIR / "acquisition_full_promotion_report.json"

ACQUISITION_NOTE_MARKER = "## Acquisition Promotion"
ACQUISITION_CHECKLIST_MARKER = "## Acquisition Promotion Checks"
ACQUISITION_VALIDATION_PACK_MARKER = "## Priority D — Acquisition Promotion"
ACQUISITION_CLOSURE_MARKER = "## Acquisition Promotion"

PREFERRED_CHANGED_VALIDATION_ITEMS = (
    "Base.Axe",
    "Base.AssaultRifle",
    "Base.Bag_Schoolbag",
    "Base.Battery",
    "Base.BaseballBat",
    "Base.BellyButton_DangleGold",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_expected_changed_items(facts_review_path: Path) -> list[str]:
    return sorted(
        row["item_id"]
        for row in load_jsonl(facts_review_path)
        if row.get("patch_status") == "PROMOTION_READY"
        and row.get("current_acquisition_hint") != row.get("proposed_acquisition_hint")
    )


def build_promotion_note(report: dict[str, Any]) -> str:
    lines = [
        "# Sprint 7 Acquisition Promotion Note",
        "",
        f"- facts patch count: `{report['facts_patch_count']}`",
        f"- decisions patch count: `{report['decisions_patch_count']}`",
        f"- rendered changed count: `{report['rendered_changed_count']}`",
        f"- unexpected rendered changes: `{report['unexpected_rendered_changed_count']}`",
        f"- expected-but-unchanged count: `{report['expected_but_unchanged_count']}`",
        f"- introduced rendered fail / warn: `{report['introduced_rendered_hard_fail_count']} / {report['introduced_rendered_warn_count']}`",
        f"- rendered hard fail / warn: `{report['rendered_hard_fail_count']} / {report['rendered_warn_count']}`",
        f"- decisions hard fail: `{report['decisions_contract_hard_fail_count']}`",
        f"- runtime report status: `{report['runtime_report_status']}`",
        f"- authority preview ready: `{str(report['sprint7_authority_preview_ready']).lower()}`",
        "",
    ]
    return "\n".join(lines)


def build_runtime_note(existing_note_text: str, report: dict[str, Any]) -> str:
    base_text = existing_note_text
    if ACQUISITION_NOTE_MARKER in base_text:
        base_text = base_text.split(ACQUISITION_NOTE_MARKER, 1)[0].rstrip()
    else:
        base_text = base_text.rstrip()

    lines = [base_text, "", ACQUISITION_NOTE_MARKER, ""]
    lines.extend(
        [
            f"- facts patch count: `{report['facts_patch_count']}`",
            f"- decisions patch count: `{report['decisions_patch_count']}`",
            f"- rendered changed count: `{report['rendered_changed_count']}`",
            f"- unexpected rendered changes: `{report['unexpected_rendered_changed_count']}`",
            f"- expected-but-unchanged count: `{report['expected_but_unchanged_count']}`",
            f"- introduced rendered fail / warn: `{report['introduced_rendered_hard_fail_count']} / {report['introduced_rendered_warn_count']}`",
            f"- rendered hard fail / warn: `{report['rendered_hard_fail_count']} / {report['rendered_warn_count']}`",
            f"- decisions hard fail: `{report['decisions_contract_hard_fail_count']}`",
            f"- runtime report status: `{report['runtime_report_status']}`",
            f"- authority preview ready: `{str(report['sprint7_authority_preview_ready']).lower()}`",
            "",
        ]
    )
    return "\n".join(lines)


def replace_or_append_markdown_section(*, existing_text: str, marker: str, body: str) -> str:
    normalized_body = body.rstrip()
    if marker in existing_text:
        prefix = existing_text.split(marker, 1)[0].rstrip()
        return f"{prefix}\n\n{marker}\n\n{normalized_body}\n"
    prefix = existing_text.rstrip()
    if prefix:
        return f"{prefix}\n\n{marker}\n\n{normalized_body}\n"
    return f"{marker}\n\n{normalized_body}\n"


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


def select_null_reason_validation_items(
    *,
    facts_rows: list[dict[str, Any]],
    decisions_rows: list[dict[str, Any]],
    rendered_entries: dict[str, Any],
    max_per_reason: int = 3,
) -> dict[str, list[dict[str, str]]]:
    facts_by_id = {str(row["item_id"]): row for row in facts_rows}
    selected: dict[str, list[dict[str, str]]] = {
        "UBIQUITOUS_ITEM": [],
        "STANDARDIZATION_IMPOSSIBLE": [],
    }
    for decision in sorted(decisions_rows, key=lambda row: str(row["item_id"])):
        item_id = str(decision["item_id"])
        reason = str(decision.get("acquisition_null_reason") or "")
        if reason not in selected:
            continue
        if len(selected[reason]) >= max_per_reason:
            continue
        fact = facts_by_id.get(item_id)
        if fact is None or fact.get("acquisition_hint") is not None:
            continue
        selected[reason].append(
            {
                "item_id": item_id,
                "text_ko": str((rendered_entries.get(item_id) or {}).get("text_ko") or ""),
            }
        )
    return selected


def build_checklist_section(
    *,
    changed_samples: list[dict[str, str]],
    null_reason_samples: dict[str, list[dict[str, str]]],
) -> str:
    lines = [
        "1. Confirm representative acquisition-standardized rows show the updated acquisition surface:",
    ]
    for sample in changed_samples:
        lines.append(f"   - {sample['item_id']}")
        lines.append(f"     expected: `{sample['text_ko']}`")
    lines.append("2. Confirm acquisition-null rows still omit the acquisition block in runtime surfaces:")
    for reason in ("UBIQUITOUS_ITEM", "STANDARDIZATION_IMPOSSIBLE"):
        for sample in null_reason_samples[reason]:
            lines.append(f"   - {sample['item_id']} (`{reason}`)")
            lines.append("     expected behavior: acquisition sentence remains omitted in the rendered 3-3 body")
    lines.append("3. Record any mismatch as `item_id / observed text / expected text / surface` and keep the reason code if the row is acquisition-null.")
    return "\n".join(lines)


def build_validation_pack_section(
    *,
    changed_samples: list[dict[str, str]],
    null_reason_samples: dict[str, list[dict[str, str]]],
) -> str:
    lines = ["", "### Priority D1 — acquisition surface delta checks", ""]
    for sample in changed_samples:
        lines.append(f"- `{sample['item_id']}`")
        lines.append(f"  expected: `{sample['text_ko']}`")
    lines.extend(["", "### Priority D2 — acquisition-null omission checks", ""])
    for reason in ("UBIQUITOUS_ITEM", "STANDARDIZATION_IMPOSSIBLE"):
        for sample in null_reason_samples[reason]:
            lines.append(f"- `{sample['item_id']}`")
            lines.append(f"  expected reason: `{reason}`")
            lines.append("  expected behavior: acquisition sentence remains omitted in the rendered 3-3 body")
    lines.extend(["", "### Exit Note", "", "- Any acquisition mismatch should be recorded with `surface / item_id / observed text / expected text / null_reason`.", "- `STANDARDIZATION_IMPOSSIBLE` rows should stay omission-only; if a stable acquisition sentence appears, reopen facts instead of forcing the null reason."])
    return "\n".join(lines)


def build_closure_report_section(report: dict[str, Any]) -> str:
    lines = [
        f"- facts patch count: `{report['facts_patch_count']}`",
        f"- decisions patch count: `{report['decisions_patch_count']}`",
        f"- rendered changed count: `{report['rendered_changed_count']}`",
        f"- unexpected rendered changes: `{report['unexpected_rendered_changed_count']}`",
        f"- introduced rendered fail / warn: `{report['introduced_rendered_hard_fail_count']} / {report['introduced_rendered_warn_count']}`",
        f"- decisions hard fail: `{report['decisions_contract_hard_fail_count']}`",
        f"- authority preview ready: `{str(report['sprint7_authority_preview_ready']).lower()}`",
    ]
    return "\n".join(lines)


def update_runtime_summary(*, runtime_summary_path: Path, report: dict[str, Any]) -> dict[str, Any]:
    summary = load_json(runtime_summary_path) if runtime_summary_path.exists() else {
        "schema_version": "second-pass-sprint7-runtime-summary-v1"
    }
    summary["runtime_report_status"] = report["runtime_report_status"]
    summary["acquisition_promotion"] = {
        "generated_at": report["generated_at"],
        "bundle_report_ref": report["bundle_report_ref"],
        "facts_path": report["authority_facts_path"],
        "decisions_path": report["authority_decisions_path"],
        "rendered_path": report["authority_rendered_path"],
        "rendered_validation_ref": report["authority_rendered_validation_ref"],
        "decisions_validation_ref": report["authority_decisions_validation_ref"],
        "lua_bridge_ref": report["authority_bridge_report_ref"],
        "runtime_report_ref": report["authority_runtime_report_ref"],
        "facts_patch_count": report["facts_patch_count"],
        "decisions_patch_count": report["decisions_patch_count"],
        "promoted_acquisition_row_count": report["promoted_acquisition_row_count"],
        "null_reason_explained_count": report["null_reason_explained_count"],
        "rendered_changed_count": report["rendered_changed_count"],
        "expected_rendered_change_candidate_count": report["expected_rendered_change_candidate_count"],
        "unexpected_rendered_changed_count": report["unexpected_rendered_changed_count"],
        "expected_but_unchanged_count": report["expected_but_unchanged_count"],
        "rendered_hard_fail_count": report["rendered_hard_fail_count"],
        "rendered_warn_count": report["rendered_warn_count"],
        "introduced_rendered_hard_fail_count": report["introduced_rendered_hard_fail_count"],
        "introduced_rendered_warn_count": report["introduced_rendered_warn_count"],
        "decisions_contract_hard_fail_count": report["decisions_contract_hard_fail_count"],
        "sprint7_authority_preview_ready": report["sprint7_authority_preview_ready"],
    }
    write_json(runtime_summary_path, summary)
    return summary


def build_acquisition_sprint7_authority_promotion(
    *,
    authority_facts_path: Path = AUTHORITY_FACTS_PATH,
    authority_decisions_path: Path = AUTHORITY_DECISIONS_PATH,
    authority_rendered_path: Path = AUTHORITY_RENDERED_PATH,
    authority_rendered_validation_path: Path = AUTHORITY_RENDERED_VALIDATION_PATH,
    authority_decisions_validation_path: Path = AUTHORITY_DECISIONS_VALIDATION_PATH,
    authority_runtime_summary_path: Path = AUTHORITY_RUNTIME_SUMMARY_PATH,
    authority_runtime_note_path: Path = AUTHORITY_RUNTIME_NOTE_PATH,
    authority_promotion_note_path: Path = AUTHORITY_PROMOTION_NOTE_PATH,
    authority_promotion_report_path: Path = AUTHORITY_PROMOTION_REPORT_PATH,
    authority_checklist_path: Path = AUTHORITY_CHECKLIST_PATH,
    authority_validation_pack_path: Path = AUTHORITY_VALIDATION_PACK_PATH,
    authority_closure_report_path: Path = AUTHORITY_CLOSURE_REPORT_PATH,
    authority_baseline_rendered_path: Path = AUTHORITY_BASELINE_RENDERED_PATH,
    authority_baseline_rendered_validation_path: Path = AUTHORITY_BASELINE_RENDERED_VALIDATION_PATH,
    authority_baseline_style_log_path: Path = AUTHORITY_BASELINE_STYLE_LOG_PATH,
    authority_promoted_style_log_path: Path = AUTHORITY_PROMOTED_STYLE_LOG_PATH,
    authority_lua_path: Path = AUTHORITY_LUA_PATH,
    authority_bridge_report_path: Path = AUTHORITY_BRIDGE_REPORT_PATH,
    authority_runtime_report_path: Path = AUTHORITY_RUNTIME_REPORT_PATH,
    facts_patch_path: Path = FULL_FACTS_PATCH_PATH,
    facts_review_path: Path = FULL_FACTS_REVIEW_PATH,
    decisions_patch_path: Path = FULL_DECISIONS_PATCH_PATH,
    bundle_facts_path: Path = FULL_BUNDLE_FACTS_PATH,
    bundle_decisions_path: Path = FULL_BUNDLE_DECISIONS_PATH,
    bundle_baseline_rendered_path: Path = FULL_BUNDLE_BASELINE_RENDERED_PATH,
    bundle_promoted_rendered_path: Path = FULL_BUNDLE_PROMOTED_RENDERED_PATH,
    bundle_baseline_style_log_path: Path = FULL_BUNDLE_BASELINE_STYLE_LOG_PATH,
    bundle_promoted_style_log_path: Path = FULL_BUNDLE_PROMOTED_STYLE_LOG_PATH,
    bundle_decisions_validation_path: Path = FULL_BUNDLE_DECISIONS_VALIDATION_PATH,
    bundle_report_path: Path = FULL_BUNDLE_REPORT_PATH,
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
    bundle_report = build_acquisition_partial_promotion_bundle(
        facts_path=authority_facts_path,
        decisions_path=authority_decisions_path,
        facts_patch_path=facts_patch_path,
        decisions_patch_path=decisions_patch_path,
        facts_review_path=facts_review_path,
        promoted_facts_path=bundle_facts_path,
        promoted_decisions_path=bundle_decisions_path,
        baseline_rendered_path=bundle_baseline_rendered_path,
        promoted_rendered_path=bundle_promoted_rendered_path,
        baseline_style_log_path=bundle_baseline_style_log_path,
        promoted_style_log_path=bundle_promoted_style_log_path,
        validation_report_path=bundle_decisions_validation_path,
        report_path=bundle_report_path,
        overlay_path=overlay_path,
    )
    if not bundle_report.get("full_acquisition_promotion_ready"):
        raise ValueError("Acquisition bundle must be full-promotion-ready before authority promotion")

    promoted_facts_rows = load_jsonl(bundle_facts_path)
    promoted_decisions_rows = load_jsonl(bundle_decisions_path)

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

    write_jsonl(authority_facts_path, promoted_facts_rows)
    write_jsonl(authority_decisions_path, promoted_decisions_rows)

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
    rendered_entries = load_json(authority_rendered_path).get("entries", {})
    expected_changed_items = build_expected_changed_items(facts_review_path)
    changed_item_set = set(changed_items)
    expected_changed_item_set = set(expected_changed_items)
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

    report = {
        "schema_version": "sprint7-acquisition-authority-promotion-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bundle_report_ref": str(bundle_report_path),
        "authority_facts_path": str(authority_facts_path),
        "authority_decisions_path": str(authority_decisions_path),
        "authority_rendered_path": str(authority_rendered_path),
        "authority_baseline_rendered_validation_ref": str(authority_baseline_rendered_validation_path),
        "authority_rendered_validation_ref": str(authority_rendered_validation_path),
        "authority_decisions_validation_ref": str(authority_decisions_validation_path),
        "authority_bridge_report_ref": str(authority_bridge_report_path),
        "authority_runtime_report_ref": str(authority_runtime_report_path),
        "authority_runtime_summary_ref": str(authority_runtime_summary_path),
        "authority_runtime_note_ref": str(authority_runtime_note_path),
        "authority_promotion_note_ref": str(authority_promotion_note_path),
        "facts_patch_count": int(bundle_report["facts_patch_count"]),
        "decisions_patch_count": int(bundle_report["decisions_patch_count"]),
        "promoted_acquisition_row_count": sum(1 for row in promoted_facts_rows if row.get("acquisition_hint") is not None),
        "null_reason_explained_count": sum(1 for row in promoted_decisions_rows if row.get("acquisition_null_reason") is not None),
        "rendered_changed_count": rendered_changed_count,
        "rendered_changed_samples": changed_items[:20],
        "expected_rendered_change_candidate_count": len(expected_changed_items),
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
        "decisions_null_reason_missing_count": int(decisions_validation["null_reason_missing_count"]),
        "decisions_null_reason_invalid_count": int(decisions_validation["null_reason_invalid_count"]),
        "bundle_full_acquisition_promotion_ready": bool(bundle_report["full_acquisition_promotion_ready"]),
        "runtime_report_status": runtime_report.get("overall_status"),
        "bridge_runtime_entry_count": bridge_report.get("runtime_entry_count"),
        "sprint7_authority_preview_ready": (
            len(introduced_rendered_hard_fail_rows) == 0
            and len(introduced_rendered_warn_rows) == 0
            and decisions_validation["hard_fail_count"] == 0
            and len(unexpected_changed_items) == 0
            and runtime_report.get("overall_status") == "ready_for_in_game_validation"
        ),
    }
    write_json(authority_promotion_report_path, report)
    summary = update_runtime_summary(runtime_summary_path=authority_runtime_summary_path, report=report)

    runtime_note_text = authority_runtime_note_path.read_text(encoding="utf-8") if authority_runtime_note_path.exists() else "# Sprint 7 Runtime Note\n"
    authority_runtime_note_path.write_text(build_runtime_note(runtime_note_text, report), encoding="utf-8")
    authority_promotion_note_path.write_text(build_promotion_note(report), encoding="utf-8")
    changed_samples = select_changed_validation_items(
        changed_items=changed_items,
        rendered_entries=rendered_entries,
    )
    null_reason_samples = select_null_reason_validation_items(
        facts_rows=promoted_facts_rows,
        decisions_rows=promoted_decisions_rows,
        rendered_entries=rendered_entries,
    )
    checklist_text = authority_checklist_path.read_text(encoding="utf-8") if authority_checklist_path.exists() else "# Sprint 7 In-Game Validation Checklist\n"
    authority_checklist_path.write_text(
        replace_or_append_markdown_section(
            existing_text=checklist_text,
            marker=ACQUISITION_CHECKLIST_MARKER,
            body=build_checklist_section(
                changed_samples=changed_samples,
                null_reason_samples=null_reason_samples,
            ),
        ),
        encoding="utf-8",
    )
    validation_pack_text = authority_validation_pack_path.read_text(encoding="utf-8") if authority_validation_pack_path.exists() else "# Second Pass In-Game Validation Pack\n"
    authority_validation_pack_path.write_text(
        replace_or_append_markdown_section(
            existing_text=validation_pack_text,
            marker=ACQUISITION_VALIDATION_PACK_MARKER,
            body=build_validation_pack_section(
                changed_samples=changed_samples,
                null_reason_samples=null_reason_samples,
            ),
        ),
        encoding="utf-8",
    )
    closure_report_text = authority_closure_report_path.read_text(encoding="utf-8") if authority_closure_report_path.exists() else "# Second Pass Closure Report\n"
    authority_closure_report_path.write_text(
        replace_or_append_markdown_section(
            existing_text=closure_report_text,
            marker=ACQUISITION_CLOSURE_MARKER,
            body=build_closure_report_section(report),
        ),
        encoding="utf-8",
    )
    return {"report": report, "runtime_summary": summary}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote acquisition full bundle into sprint7 authority preview artifacts.")
    parser.add_argument("--authority-facts-path", type=Path, default=AUTHORITY_FACTS_PATH)
    parser.add_argument("--authority-decisions-path", type=Path, default=AUTHORITY_DECISIONS_PATH)
    parser.add_argument("--authority-rendered-path", type=Path, default=AUTHORITY_RENDERED_PATH)
    parser.add_argument("--authority-rendered-validation-path", type=Path, default=AUTHORITY_RENDERED_VALIDATION_PATH)
    parser.add_argument("--authority-decisions-validation-path", type=Path, default=AUTHORITY_DECISIONS_VALIDATION_PATH)
    parser.add_argument("--authority-runtime-summary-path", type=Path, default=AUTHORITY_RUNTIME_SUMMARY_PATH)
    parser.add_argument("--authority-runtime-note-path", type=Path, default=AUTHORITY_RUNTIME_NOTE_PATH)
    parser.add_argument("--authority-promotion-note-path", type=Path, default=AUTHORITY_PROMOTION_NOTE_PATH)
    parser.add_argument("--authority-promotion-report-path", type=Path, default=AUTHORITY_PROMOTION_REPORT_PATH)
    parser.add_argument("--authority-checklist-path", type=Path, default=AUTHORITY_CHECKLIST_PATH)
    parser.add_argument("--authority-validation-pack-path", type=Path, default=AUTHORITY_VALIDATION_PACK_PATH)
    parser.add_argument("--authority-closure-report-path", type=Path, default=AUTHORITY_CLOSURE_REPORT_PATH)
    parser.add_argument("--authority-baseline-rendered-path", type=Path, default=AUTHORITY_BASELINE_RENDERED_PATH)
    parser.add_argument("--authority-baseline-rendered-validation-path", type=Path, default=AUTHORITY_BASELINE_RENDERED_VALIDATION_PATH)
    parser.add_argument("--authority-baseline-style-log-path", type=Path, default=AUTHORITY_BASELINE_STYLE_LOG_PATH)
    parser.add_argument("--authority-promoted-style-log-path", type=Path, default=AUTHORITY_PROMOTED_STYLE_LOG_PATH)
    parser.add_argument("--authority-lua-path", type=Path, default=AUTHORITY_LUA_PATH)
    parser.add_argument("--authority-bridge-report-path", type=Path, default=AUTHORITY_BRIDGE_REPORT_PATH)
    parser.add_argument("--authority-runtime-report-path", type=Path, default=AUTHORITY_RUNTIME_REPORT_PATH)
    parser.add_argument("--facts-patch-path", type=Path, default=FULL_FACTS_PATCH_PATH)
    parser.add_argument("--facts-review-path", type=Path, default=FULL_FACTS_REVIEW_PATH)
    parser.add_argument("--decisions-patch-path", type=Path, default=FULL_DECISIONS_PATCH_PATH)
    parser.add_argument("--bundle-facts-path", type=Path, default=FULL_BUNDLE_FACTS_PATH)
    parser.add_argument("--bundle-decisions-path", type=Path, default=FULL_BUNDLE_DECISIONS_PATH)
    parser.add_argument("--bundle-baseline-rendered-path", type=Path, default=FULL_BUNDLE_BASELINE_RENDERED_PATH)
    parser.add_argument("--bundle-promoted-rendered-path", type=Path, default=FULL_BUNDLE_PROMOTED_RENDERED_PATH)
    parser.add_argument("--bundle-baseline-style-log-path", type=Path, default=FULL_BUNDLE_BASELINE_STYLE_LOG_PATH)
    parser.add_argument("--bundle-promoted-style-log-path", type=Path, default=FULL_BUNDLE_PROMOTED_STYLE_LOG_PATH)
    parser.add_argument("--bundle-decisions-validation-path", type=Path, default=FULL_BUNDLE_DECISIONS_VALIDATION_PATH)
    parser.add_argument("--bundle-report-path", type=Path, default=FULL_BUNDLE_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_acquisition_sprint7_authority_promotion(
        authority_facts_path=args.authority_facts_path,
        authority_decisions_path=args.authority_decisions_path,
        authority_rendered_path=args.authority_rendered_path,
        authority_rendered_validation_path=args.authority_rendered_validation_path,
        authority_decisions_validation_path=args.authority_decisions_validation_path,
        authority_runtime_summary_path=args.authority_runtime_summary_path,
        authority_runtime_note_path=args.authority_runtime_note_path,
        authority_promotion_note_path=args.authority_promotion_note_path,
        authority_promotion_report_path=args.authority_promotion_report_path,
        authority_checklist_path=args.authority_checklist_path,
        authority_validation_pack_path=args.authority_validation_pack_path,
        authority_closure_report_path=args.authority_closure_report_path,
        authority_baseline_rendered_path=args.authority_baseline_rendered_path,
        authority_baseline_rendered_validation_path=args.authority_baseline_rendered_validation_path,
        authority_baseline_style_log_path=args.authority_baseline_style_log_path,
        authority_promoted_style_log_path=args.authority_promoted_style_log_path,
        authority_lua_path=args.authority_lua_path,
        authority_bridge_report_path=args.authority_bridge_report_path,
        authority_runtime_report_path=args.authority_runtime_report_path,
        facts_patch_path=args.facts_patch_path,
        facts_review_path=args.facts_review_path,
        decisions_patch_path=args.decisions_patch_path,
        bundle_facts_path=args.bundle_facts_path,
        bundle_decisions_path=args.bundle_decisions_path,
        bundle_baseline_rendered_path=args.bundle_baseline_rendered_path,
        bundle_promoted_rendered_path=args.bundle_promoted_rendered_path,
        bundle_baseline_style_log_path=args.bundle_baseline_style_log_path,
        bundle_promoted_style_log_path=args.bundle_promoted_style_log_path,
        bundle_decisions_validation_path=args.bundle_decisions_validation_path,
        bundle_report_path=args.bundle_report_path,
    )
    print("sprint7 acquisition authority promotion written")
    print(json.dumps(payload["report"], ensure_ascii=False, indent=2))
    return 0 if payload["report"]["sprint7_authority_preview_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
