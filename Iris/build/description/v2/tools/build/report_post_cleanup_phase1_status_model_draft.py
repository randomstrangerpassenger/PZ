from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_post_cleanup_phase0_input_freeze import (
    BASELINE_MANIFEST_PATH as PHASE0_BASELINE_MANIFEST_PATH,
    build_post_cleanup_phase0_input_freeze,
)
from tools.build.report_weak_active_cleanup_w2_existing_cluster_absorption import (
    dump_json,
    dump_text,
    load_json,
)
from tools.build.report_weak_active_cleanup_w6_aggregate import (
    FULL_CLASSIFICATION_PATH as W6_FULL_CLASSIFICATION_PATH,
    MATRIX_PATH as W6_MATRIX_PATH,
)


OUTPUT_DIR = ROOT / "staging" / "post_cleanup_integrated_roadmap" / "phase1_status_model_draft"
SPEC_PATH = OUTPUT_DIR / "2_stage_status_model_spec.md"
DECISIONS_PATH = OUTPUT_DIR / "status_model_decisions.json"
UI_DECISION_NOTE_PATH = OUTPUT_DIR / "ui_quality_indicator_decision.md"
TRANSITION_RULES_PATH = OUTPUT_DIR / "runtime_state_transition_rules.md"
COMBINATION_MATRIX_PATH = OUTPUT_DIR / "status_combination_matrix.json"

COMBINATION_ORDER = (
    ("generated", "strong"),
    ("generated", "adequate"),
    ("generated", "weak"),
    ("missing", "strong"),
    ("missing", "adequate"),
    ("missing", "weak"),
)


def semantic_value(raw_status: str) -> str:
    return str(raw_status).replace("semantic-", "")


def runtime_semantic_key(*, runtime_axis: str, semantic_axis: str) -> str:
    return f"{runtime_axis}::{semantic_axis}"


def top_item_samples(rows: list[dict[str, Any]], *, limit: int = 10) -> list[str]:
    return [str(row["item_id"]) for row in rows[:limit]]


def build_combination_matrix_rows(
    *,
    matrix_rows: list[dict[str, Any]],
    full_runtime_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cleanup_grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    full_runtime_counts: Counter[str] = Counter()

    for row in matrix_rows:
        key = runtime_semantic_key(
            runtime_axis=str(row["runtime_axis_current"]),
            semantic_axis=semantic_value(str(row["semantic_status_after_cleanup"])),
        )
        cleanup_grouped[key].append(row)

    for row in full_runtime_rows:
        key = runtime_semantic_key(
            runtime_axis=str(row["runtime_axis_current"]),
            semantic_axis=semantic_value(str(row["semantic_status_after_cleanup"])),
        )
        full_runtime_counts[key] += 1

    rows: list[dict[str, Any]] = []
    for runtime_axis, semantic_axis in COMBINATION_ORDER:
        key = runtime_semantic_key(runtime_axis=runtime_axis, semantic_axis=semantic_axis)
        cleanup_rows = cleanup_grouped[key]
        cleanup_rows.sort(key=lambda row: str(row["item_id"]))

        rule_status = "fixed"
        decision_ids: list[str] = []
        provisional_runtime_treatment = "keep_current_behavior"
        if key == "generated::weak":
            rule_status = "open"
            decision_ids = ["generated_weak_runtime_treatment"]
            provisional_runtime_treatment = "keep_generated_pending_phase1_decision"
        elif key == "missing::strong":
            rule_status = "open"
            decision_ids = ["missing_strong_adopt_timing"]
            provisional_runtime_treatment = "adopt_candidate_pending_phase1_decision"
        elif key == "missing::adequate":
            rule_status = "open"
            decision_ids = ["missing_adequate_adopt_policy"]
            provisional_runtime_treatment = "adopt_review_pending_phase1_decision"
        elif key == "missing::weak":
            rule_status = "open"
            decision_ids = ["missing_weak_priority_policy"]
            provisional_runtime_treatment = "keep_missing_backlog_priority_pending_phase1_decision"
        elif key == "generated::strong":
            provisional_runtime_treatment = "keep_generated_runtime_consumed"
        elif key == "generated::adequate":
            provisional_runtime_treatment = "keep_generated_runtime_consumed"

        rows.append(
            {
                "combination_key": key,
                "runtime_axis": runtime_axis,
                "semantic_axis": semantic_axis,
                "cleanup_scope_count": len(cleanup_rows),
                "full_runtime_count": full_runtime_counts[key],
                "rule_status": rule_status,
                "decision_ids": decision_ids,
                "provisional_runtime_treatment": provisional_runtime_treatment,
                "sample_item_ids": top_item_samples(cleanup_rows),
            }
        )
    return rows


def build_status_model_decisions(*, combination_rows: list[dict[str, Any]]) -> dict[str, Any]:
    combo_by_key = {row["combination_key"]: row for row in combination_rows}
    ui_cleanup_scope_count = sum(
        row["cleanup_scope_count"]
        for row in combination_rows
        if row["semantic_axis"] in {"strong", "weak"}
    )
    ui_full_runtime_count = sum(
        row["full_runtime_count"]
        for row in combination_rows
        if row["semantic_axis"] in {"strong", "weak"}
    )
    return {
        "schema_version": "post-cleanup-phase1-status-model-decisions-v0",
        "phase": "Phase 1",
        "decision_count": 5,
        "decision_status": "pending",
        "decisions": [
            {
                "decision_id": "generated_weak_runtime_treatment",
                "status": "pending",
                "affected_combination": "generated::weak",
                "affected_cleanup_scope_count": combo_by_key["generated::weak"]["cleanup_scope_count"],
                "affected_full_runtime_count": combo_by_key["generated::weak"]["full_runtime_count"],
                "question": "generated::weak rows should stay runtime-consumed, gain a weaker quality presentation, or be demoted to missing.",
                "options": [
                    {"option_id": "A", "label": "keep_generated_no_indicator"},
                    {"option_id": "B", "label": "keep_generated_with_quality_indicator"},
                    {"option_id": "C", "label": "demote_to_missing"},
                ],
            },
            {
                "decision_id": "missing_strong_adopt_timing",
                "status": "pending",
                "affected_combination": "missing::strong",
                "affected_cleanup_scope_count": combo_by_key["missing::strong"]["cleanup_scope_count"],
                "affected_full_runtime_count": combo_by_key["missing::strong"]["full_runtime_count"],
                "question": "missing::strong rows should be adopted immediately or only after a separate validation gate.",
                "options": [
                    {"option_id": "A", "label": "adopt_in_phase2"},
                    {"option_id": "B", "label": "adopt_after_extra_validation_gate"},
                ],
            },
            {
                "decision_id": "missing_adequate_adopt_policy",
                "status": "pending",
                "affected_combination": "missing::adequate",
                "affected_cleanup_scope_count": combo_by_key["missing::adequate"]["cleanup_scope_count"],
                "affected_full_runtime_count": combo_by_key["missing::adequate"]["full_runtime_count"],
                "question": "missing::adequate rows should be adopted if an identity-level runtime-consumable primary_use is acceptable, or remain missing.",
                "options": [
                    {"option_id": "A", "label": "adopt_if_runtime_consumable_identity_body_exists"},
                    {"option_id": "B", "label": "keep_missing"},
                ],
            },
            {
                "decision_id": "missing_weak_priority_policy",
                "status": "pending",
                "affected_combination": "missing::weak",
                "affected_cleanup_scope_count": combo_by_key["missing::weak"]["cleanup_scope_count"],
                "affected_full_runtime_count": combo_by_key["missing::weak"]["full_runtime_count"],
                "question": "missing::weak rows should be prioritized above, below, or alongside generated::weak backlog work.",
                "options": [
                    {"option_id": "A", "label": "higher_than_generated_weak"},
                    {"option_id": "B", "label": "lower_than_generated_weak"},
                    {"option_id": "C", "label": "same_priority_as_generated_weak"},
                ],
            },
            {
                "decision_id": "ui_quality_indicator_direction",
                "status": "pending",
                "affected_combination": "ui-contract",
                "affected_cleanup_scope_count": ui_cleanup_scope_count,
                "affected_full_runtime_count": ui_full_runtime_count,
                "question": "semantic quality should remain internal-only, be exposed for strong rows, or be exposed only for weak rows.",
                "options": [
                    {"option_id": "A", "label": "no_ui_exposure"},
                    {"option_id": "B", "label": "strong_only_indicator"},
                    {"option_id": "C", "label": "weak_only_indicator"},
                ],
            },
        ],
    }


def render_spec(
    *,
    manifest: dict[str, Any],
    combination_rows: list[dict[str, Any]],
) -> str:
    combo_by_key = {row["combination_key"]: row for row in combination_rows}
    return "\n".join(
        [
            "# 2-Stage Status Model Spec (Draft)",
            "",
            "## Scope",
            "",
            f"- cleanup scope rows: `{manifest['frozen_counts']['cleanup_scope_row_count']}`",
            f"- full runtime rows: `{manifest['frozen_counts']['full_runtime_row_count']}`",
            f"- backlog rows: `{manifest['frozen_counts']['backlog_row_count']}`",
            "",
            "## Runtime axis",
            "",
            "- `generated`: runtime-consumable body exists, so runtime can consume the row.",
            "- `missing`: runtime-consumable body does not exist, so runtime cannot consume the row.",
            "",
            "`active/silent` are current-surface reference labels only; the runtime axis definition itself is based on runtime-consumable body presence.",
            "",
            "## Semantic axis",
            "",
            "- `strong`: representative work context is cluster-summary justified.",
            "- `adequate`: identity-level meaning is structurally acceptable as the final 3-3 state.",
            "- `weak`: source is insufficient or unmapped and needs follow-up source work.",
            "- `semantic-silent`: reserved only; current count is `0`.",
            "",
            "## Combination inventory",
            "",
            f"- `generated::strong`: cleanup `{combo_by_key['generated::strong']['cleanup_scope_count']}`, full runtime `{combo_by_key['generated::strong']['full_runtime_count']}`",
            f"- `generated::adequate`: cleanup `{combo_by_key['generated::adequate']['cleanup_scope_count']}`, full runtime `{combo_by_key['generated::adequate']['full_runtime_count']}`",
            f"- `generated::weak`: cleanup `{combo_by_key['generated::weak']['cleanup_scope_count']}`, full runtime `{combo_by_key['generated::weak']['full_runtime_count']}`",
            f"- `missing::strong`: cleanup `{combo_by_key['missing::strong']['cleanup_scope_count']}`, full runtime `{combo_by_key['missing::strong']['full_runtime_count']}`",
            f"- `missing::adequate`: cleanup `{combo_by_key['missing::adequate']['cleanup_scope_count']}`, full runtime `{combo_by_key['missing::adequate']['full_runtime_count']}`",
            f"- `missing::weak`: cleanup `{combo_by_key['missing::weak']['cleanup_scope_count']}`, full runtime `{combo_by_key['missing::weak']['full_runtime_count']}`",
            "",
            "## Provisional runtime handling draft",
            "",
            "- `generated::strong`: keep runtime-consumed.",
            "- `generated::adequate`: keep runtime-consumed.",
            "- `generated::weak`: keep or demote is still open in Phase 1.",
            "- `missing::strong`: adopt timing is still open in Phase 1.",
            "- `missing::adequate`: adopt policy is still open in Phase 1.",
            "- `missing::weak`: runtime remains missing; backlog priority rule is still open in Phase 1.",
            "",
            "This draft is a Phase 1 input artifact, not the final runtime contract.",
            "",
        ]
    )


def render_transition_rules(*, combination_rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Runtime State Transition Rules (Draft)",
        "",
        "These rules are provisional until the five Phase 1 decisions are closed.",
        "",
        "## Fixed combinations",
        "",
        "- `generated::strong` -> keep `generated` and treat as runtime-consumable strong row.",
        "- `generated::adequate` -> keep `generated` and treat as runtime-consumable adequate row.",
        "",
        "## Open combinations",
        "",
        "- `generated::weak` -> default draft state is keep-generated pending policy decision; demotion to `missing` is still an open option.",
        "- `missing::strong` -> draft state is adopt candidate pending adopt-timing decision.",
        "- `missing::adequate` -> draft state is adopt review pending adequate-adopt decision.",
        "- `missing::weak` -> keep `missing` and route to source backlog; only its relative execution priority remains open.",
        "",
        "## Hold reminder",
        "",
        "- `hold` is not a semantic-axis value.",
        "- `hold` is a later backlog-operating status that may be assigned after Phase 3 package work if a row still should not be closed through source packaging.",
        "",
        "## Combination summary",
        "",
    ]
    for row in combination_rows:
        lines.append(
            f"- `{row['combination_key']}`: cleanup `{row['cleanup_scope_count']}`, full runtime `{row['full_runtime_count']}`, rule status `{row['rule_status']}`"
        )
    lines.append("")
    return "\n".join(lines)


def render_ui_decision_note(*, decisions: dict[str, Any], combination_rows: list[dict[str, Any]]) -> str:
    decision = next(
        item for item in decisions["decisions"] if item["decision_id"] == "ui_quality_indicator_direction"
    )
    strong_cleanup_scope_count = sum(
        row["cleanup_scope_count"] for row in combination_rows if row["semantic_axis"] == "strong"
    )
    weak_cleanup_scope_count = sum(
        row["cleanup_scope_count"] for row in combination_rows if row["semantic_axis"] == "weak"
    )
    strong_full_runtime_count = sum(
        row["full_runtime_count"] for row in combination_rows if row["semantic_axis"] == "strong"
    )
    weak_full_runtime_count = sum(
        row["full_runtime_count"] for row in combination_rows if row["semantic_axis"] == "weak"
    )
    return "\n".join(
        [
            "# UI Quality Indicator Decision Note",
            "",
            "## Separation rule",
            "",
            "- runtime contract and UI contract must stay separate",
            "- this note exists so UI exposure direction can be discussed without mutating the status-model runtime axis itself",
            "",
            "## Current decision status",
            "",
            f"- decision id: `{decision['decision_id']}`",
            f"- decision status: `{decision['status']}`",
            f"- strong cleanup-scope rows potentially affected: `{strong_cleanup_scope_count}`",
            f"- weak cleanup-scope rows potentially affected: `{weak_cleanup_scope_count}`",
            f"- strong full-runtime rows potentially affected: `{strong_full_runtime_count}`",
            f"- weak full-runtime rows potentially affected: `{weak_full_runtime_count}`",
            "",
            "## Allowed options",
            "",
            "- `A`: no UI exposure; semantic quality remains internal-only",
            "- `B`: expose only strong rows in UI",
            "- `C`: expose only weak rows in UI",
            "",
            "The selected UI direction must be recorded in `status_model_decisions.json`, while this note keeps the reasoning and rejected alternatives separate from the runtime contract itself.",
            "",
        ]
    )


def build_post_cleanup_phase1_status_model_draft(
    *,
    phase0_manifest_path: Path = PHASE0_BASELINE_MANIFEST_PATH,
    w6_matrix_path: Path = W6_MATRIX_PATH,
    w6_full_classification_path: Path = W6_FULL_CLASSIFICATION_PATH,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    if not phase0_manifest_path.exists():
        build_post_cleanup_phase0_input_freeze()

    phase0_manifest = load_json(phase0_manifest_path)
    matrix_rows = load_json(w6_matrix_path)["rows"]
    full_runtime_rows = load_json(w6_full_classification_path)["rows"]

    combination_rows = build_combination_matrix_rows(
        matrix_rows=matrix_rows,
        full_runtime_rows=full_runtime_rows,
    )
    decisions = build_status_model_decisions(combination_rows=combination_rows)

    dump_text(output_dir / SPEC_PATH.name, render_spec(manifest=phase0_manifest, combination_rows=combination_rows))
    dump_json(output_dir / DECISIONS_PATH.name, decisions)
    dump_text(
        output_dir / UI_DECISION_NOTE_PATH.name,
        render_ui_decision_note(decisions=decisions, combination_rows=combination_rows),
    )
    dump_text(
        output_dir / TRANSITION_RULES_PATH.name,
        render_transition_rules(combination_rows=combination_rows),
    )
    dump_json(
        output_dir / COMBINATION_MATRIX_PATH.name,
        {
            "schema_version": "post-cleanup-phase1-status-combination-matrix-v0",
            "phase0_manifest_ref": str(phase0_manifest_path),
            "row_count": len(combination_rows),
            "rows": combination_rows,
        },
    )

    summary = {
        "schema_version": "post-cleanup-phase1-status-model-draft-v0",
        "phase0_manifest_ref": str(phase0_manifest_path),
        "combination_row_count": len(combination_rows),
        "decision_count": decisions["decision_count"],
        "output_paths": {
            "spec": str(output_dir / SPEC_PATH.name),
            "decisions": str(output_dir / DECISIONS_PATH.name),
            "ui_note": str(output_dir / UI_DECISION_NOTE_PATH.name),
            "transition_rules": str(output_dir / TRANSITION_RULES_PATH.name),
            "combination_matrix": str(output_dir / COMBINATION_MATRIX_PATH.name),
        },
    }
    return summary


def main() -> int:
    summary = build_post_cleanup_phase1_status_model_draft()
    print("post-cleanup Phase 1 status model draft generated")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
