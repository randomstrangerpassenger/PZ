from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_post_cleanup_phase0_input_freeze import (
    BASELINE_MANIFEST_PATH as PHASE0_BASELINE_MANIFEST_PATH,
)
from tools.build.report_post_cleanup_phase1_status_model_draft import (
    COMBINATION_MATRIX_PATH as PHASE1_DRAFT_COMBINATION_MATRIX_PATH,
)
from tools.build.report_weak_active_cleanup_w2_existing_cluster_absorption import (
    dump_json,
    dump_text,
    load_json,
    load_jsonl,
)
from tools.build.report_weak_active_cleanup_w6_aggregate import (
    MATRIX_PATH as W6_MATRIX_PATH,
    POST_CLEANUP_FACTS_PATH as W6_POST_CLEANUP_FACTS_PATH,
)


OUTPUT_DIR = ROOT / "staging" / "post_cleanup_integrated_roadmap" / "phase1_status_model"
SPEC_PATH = OUTPUT_DIR / "2_stage_status_model_spec.md"
DECISIONS_PATH = OUTPUT_DIR / "status_model_decisions.json"
UI_DECISION_NOTE_PATH = OUTPUT_DIR / "ui_quality_indicator_decision.md"
TRANSITION_RULES_PATH = OUTPUT_DIR / "runtime_state_transition_rules.md"
COMBINATION_MATRIX_PATH = OUTPUT_DIR / "status_combination_matrix.json"

FINAL_SELECTIONS = {
    "generated_weak_runtime_treatment": "A",
    "missing_strong_adopt_timing": "A",
    "missing_adequate_adopt_policy": "B",
    "missing_weak_priority_policy": "B",
    "ui_quality_indicator_direction": "A",
}


def semantic_value(raw_status: str) -> str:
    return str(raw_status).replace("semantic-", "")


def runtime_semantic_key(*, runtime_axis: str, semantic_axis: str) -> str:
    return f"{runtime_axis}::{semantic_axis}"


def selected_label(*, decision: dict[str, Any], option_id: str) -> str:
    for option in decision["options"]:
        if option["option_id"] == option_id:
            return str(option["label"])
    raise KeyError(option_id)


def build_candidate_fact_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["item_id"]): row for row in rows}


def build_cleanup_grouped_rows(
    matrix_rows: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in matrix_rows:
        key = runtime_semantic_key(
            runtime_axis=str(row["runtime_axis_current"]),
            semantic_axis=semantic_value(str(row["semantic_status_after_cleanup"])),
        )
        grouped.setdefault(key, []).append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: str(row["item_id"]))
    return grouped


def candidate_body_summary(
    *, rows: list[dict[str, Any]], candidate_facts_by_id: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    with_body: list[str] = []
    without_body: list[str] = []
    for row in rows:
        fact = candidate_facts_by_id.get(str(row["item_id"]), {})
        primary_use = fact.get("primary_use")
        if isinstance(primary_use, str) and primary_use.strip():
            with_body.append(str(row["item_id"]))
        else:
            without_body.append(str(row["item_id"]))
    return {
        "runtime_consumable_candidate_count": len(with_body),
        "runtime_consumable_candidate_item_ids": with_body,
        "missing_runtime_consumable_candidate_count": len(without_body),
        "missing_runtime_consumable_candidate_item_ids": without_body,
    }


def enrich_combination_rows(
    *,
    draft_rows: list[dict[str, Any]],
    cleanup_grouped_rows: dict[str, list[dict[str, Any]]],
    candidate_facts_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched_rows: list[dict[str, Any]] = []
    for row in draft_rows:
        key = str(row["combination_key"])
        cleanup_rows = cleanup_grouped_rows.get(key, [])
        coverage = candidate_body_summary(
            rows=cleanup_rows,
            candidate_facts_by_id=candidate_facts_by_id,
        )

        final_runtime_treatment = "keep_generated_runtime_consumed"
        phase2_scope_action = "keep_generated"
        backlog_priority = None
        selected_option_id = None

        if key == "generated::weak":
            selected_option_id = FINAL_SELECTIONS["generated_weak_runtime_treatment"]
            final_runtime_treatment = "keep_generated_runtime_consumed"
            phase2_scope_action = "keep_generated"
            backlog_priority = "higher_than_missing_weak"
        elif key == "missing::strong":
            selected_option_id = FINAL_SELECTIONS["missing_strong_adopt_timing"]
            final_runtime_treatment = "adopt_in_phase2_after_standard_validation"
            phase2_scope_action = "adopt_in_phase2"
        elif key == "missing::adequate":
            selected_option_id = FINAL_SELECTIONS["missing_adequate_adopt_policy"]
            final_runtime_treatment = "keep_missing_until_runtime_consumable_identity_body_exists"
            phase2_scope_action = "keep_missing"
        elif key == "missing::weak":
            selected_option_id = FINAL_SELECTIONS["missing_weak_priority_policy"]
            final_runtime_treatment = "keep_missing_source_backlog"
            phase2_scope_action = "keep_missing"
            backlog_priority = "lower_than_generated_weak"

        enriched_rows.append(
            {
                **row,
                "rule_status": "closed",
                "candidate_body_summary": coverage,
                "selected_option_id": selected_option_id,
                "final_runtime_treatment": final_runtime_treatment,
                "phase2_scope_action": phase2_scope_action,
                "phase3_backlog_priority": backlog_priority,
            }
        )
    return enriched_rows


def build_closed_decisions(
    *,
    draft_decisions: dict[str, Any],
    combination_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    combo_by_key = {row["combination_key"]: row for row in combination_rows}
    closed_rows: list[dict[str, Any]] = []
    for decision in draft_decisions["decisions"]:
        decision_id = str(decision["decision_id"])
        selected_option_id = FINAL_SELECTIONS[decision_id]
        label = selected_label(decision=decision, option_id=selected_option_id)
        rationale = ""
        effect = ""

        if decision_id == "generated_weak_runtime_treatment":
            rationale = (
                "Weak-active cleanup is a structuring pass rather than a purge pass. "
                "The 133 generated::weak rows already have runtime-consumable bodies, and this round did not establish a structural reason to demote them to missing."
            )
            effect = "keep generated::weak rows runtime-consumed and leave semantic quality internal-only for now"
        elif decision_id == "missing_strong_adopt_timing":
            coverage = combo_by_key["missing::strong"]["candidate_body_summary"]
            rationale = (
                f"All {coverage['runtime_consumable_candidate_count']} missing::strong rows already have runtime-consumable candidate bodies, "
                "so standard Phase 2 validation is sufficient and no extra adoption gate is required."
            )
            effect = "route missing::strong rows into Phase 2 adoption validation and rebuild"
        elif decision_id == "missing_adequate_adopt_policy":
            coverage = combo_by_key["missing::adequate"]["candidate_body_summary"]
            rationale = (
                f"The current cleanup output provides runtime-consumable candidate bodies for only {coverage['runtime_consumable_candidate_count']} of "
                f"{combo_by_key['missing::adequate']['cleanup_scope_count']} missing::adequate rows. "
                "Adopting them now would violate the adequate-adopt gate."
            )
            effect = "keep missing::adequate rows missing until an identity-level runtime-consumable body exists"
        elif decision_id == "missing_weak_priority_policy":
            rationale = (
                "Generated::weak rows are already visible in the current runtime and therefore affect current trust and output quality. "
                "Missing::weak rows remain invisible, so they stay lower in execution priority."
            )
            effect = "prioritize generated::weak backlog work ahead of missing::weak backlog work"
        elif decision_id == "ui_quality_indicator_direction":
            rationale = (
                "Phase 1 is closing the runtime contract, not expanding UI semantics. "
                "Keeping semantic quality internal-only prevents the UI contract from distorting the adoption decision."
            )
            effect = "do not expose strong/weak quality indicators in runtime UI during this round"

        closed_rows.append(
            {
                **decision,
                "status": "closed",
                "selected_option_id": selected_option_id,
                "selected_label": label,
                "decision_effect": effect,
                "rationale": rationale,
            }
        )

    return {
        "schema_version": "post-cleanup-phase1-status-model-decisions-v1",
        "phase": "Phase 1",
        "decision_count": len(closed_rows),
        "decision_status": "closed",
        "decisions": closed_rows,
    }


def render_spec(
    *,
    phase0_manifest: dict[str, Any],
    decisions: dict[str, Any],
    combination_rows: list[dict[str, Any]],
) -> str:
    combo_by_key = {row["combination_key"]: row for row in combination_rows}
    decisions_by_id = {row["decision_id"]: row for row in decisions["decisions"]}
    return "\n".join(
        [
            "# 2-Stage Status Model Spec",
            "",
            "## Scope",
            "",
            f"- cleanup scope rows: `{phase0_manifest['frozen_counts']['cleanup_scope_row_count']}`",
            f"- full runtime rows: `{phase0_manifest['frozen_counts']['full_runtime_row_count']}`",
            f"- backlog rows: `{phase0_manifest['frozen_counts']['backlog_row_count']}`",
            "",
            "## Runtime axis",
            "",
            "- `generated`: runtime-consumable body exists, so runtime can consume the row.",
            "- `missing`: runtime-consumable body does not exist, so runtime cannot consume the row.",
            "",
            "## Semantic axis",
            "",
            "- `strong`: representative work context is cluster-summary justified.",
            "- `adequate`: identity-level meaning is structurally acceptable as the final 3-3 state.",
            "- `weak`: source is insufficient or unmapped and needs follow-up source work.",
            "- `semantic-silent`: reserved only; current count is `0`.",
            "",
            "## Closed combination rules",
            "",
            f"- `generated::strong`: keep runtime-consumed. full runtime `{combo_by_key['generated::strong']['full_runtime_count']}`",
            f"- `generated::adequate`: keep runtime-consumed. full runtime `{combo_by_key['generated::adequate']['full_runtime_count']}`",
            f"- `generated::weak`: keep runtime-consumed without UI indicator. cleanup `{combo_by_key['generated::weak']['cleanup_scope_count']}`",
            f"- `missing::strong`: adopt in Phase 2 after standard validation. cleanup `{combo_by_key['missing::strong']['cleanup_scope_count']}`",
            f"- `missing::adequate`: keep missing. runtime-consumable candidate bodies `{combo_by_key['missing::adequate']['candidate_body_summary']['runtime_consumable_candidate_count']}` / `{combo_by_key['missing::adequate']['cleanup_scope_count']}`",
            f"- `missing::weak`: keep missing and treat as lower-priority backlog than generated::weak. cleanup `{combo_by_key['missing::weak']['cleanup_scope_count']}`",
            "",
            "## Decision closure",
            "",
            f"- `generated_weak_runtime_treatment`: `{decisions_by_id['generated_weak_runtime_treatment']['selected_label']}`",
            f"- `missing_strong_adopt_timing`: `{decisions_by_id['missing_strong_adopt_timing']['selected_label']}`",
            f"- `missing_adequate_adopt_policy`: `{decisions_by_id['missing_adequate_adopt_policy']['selected_label']}`",
            f"- `missing_weak_priority_policy`: `{decisions_by_id['missing_weak_priority_policy']['selected_label']}`",
            f"- `ui_quality_indicator_direction`: `{decisions_by_id['ui_quality_indicator_direction']['selected_label']}`",
            "",
            "This artifact closes Phase 1 and is the authority for Phase 2 adoption scope freeze.",
            "",
        ]
    )


def render_transition_rules(*, combination_rows: list[dict[str, Any]]) -> str:
    combo_by_key = {row["combination_key"]: row for row in combination_rows}
    return "\n".join(
        [
            "# Runtime State Transition Rules",
            "",
            "## Fixed runtime handling",
            "",
            "- `generated::strong` -> keep `generated` and keep runtime-consumed.",
            "- `generated::adequate` -> keep `generated` and keep runtime-consumed.",
            "- `generated::weak` -> keep `generated`; do not demote in this round.",
            "- `missing::strong` -> transition `missing -> generated` only if Phase 2 candidate validation passes.",
            "- `missing::adequate` -> keep `missing` until an identity-level runtime-consumable body exists.",
            "- `missing::weak` -> keep `missing` and route to source backlog.",
            "",
            "## Backlog priority",
            "",
            "- `generated::weak` backlog priority: higher than `missing::weak`.",
            "- `missing::weak` backlog priority: lower than `generated::weak`.",
            "",
            "## Combination summary",
            "",
            f"- `generated::strong`: `{combo_by_key['generated::strong']['final_runtime_treatment']}`",
            f"- `generated::adequate`: `{combo_by_key['generated::adequate']['final_runtime_treatment']}`",
            f"- `generated::weak`: `{combo_by_key['generated::weak']['final_runtime_treatment']}`",
            f"- `missing::strong`: `{combo_by_key['missing::strong']['final_runtime_treatment']}`",
            f"- `missing::adequate`: `{combo_by_key['missing::adequate']['final_runtime_treatment']}`",
            f"- `missing::weak`: `{combo_by_key['missing::weak']['final_runtime_treatment']}`",
            "",
        ]
    )


def render_ui_decision_note(*, decisions: dict[str, Any], combination_rows: list[dict[str, Any]]) -> str:
    decision = next(
        row for row in decisions["decisions"] if row["decision_id"] == "ui_quality_indicator_direction"
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
            "# UI Quality Indicator Decision",
            "",
            "## Final direction",
            "",
            f"- selected option: `{decision['selected_label']}`",
            f"- decision effect: {decision['decision_effect']}",
            "",
            "## Affected scope",
            "",
            f"- strong cleanup-scope rows: `{strong_cleanup_scope_count}`",
            f"- weak cleanup-scope rows: `{weak_cleanup_scope_count}`",
            f"- strong full-runtime rows: `{strong_full_runtime_count}`",
            f"- weak full-runtime rows: `{weak_full_runtime_count}`",
            "",
            "## Rationale",
            "",
            decision["rationale"],
            "",
            "The runtime contract remains authoritative; UI quality exposure stays out of the Phase 2 adoption scope.",
            "",
        ]
    )


def build_post_cleanup_phase1_status_model_final(
    *,
    phase0_manifest_path: Path = PHASE0_BASELINE_MANIFEST_PATH,
    phase1_draft_combination_matrix_path: Path = PHASE1_DRAFT_COMBINATION_MATRIX_PATH,
    phase1_draft_decisions_path: Path = (
        ROOT / "staging" / "post_cleanup_integrated_roadmap" / "phase1_status_model_draft" / "status_model_decisions.json"
    ),
    w6_matrix_path: Path = W6_MATRIX_PATH,
    w6_post_cleanup_facts_path: Path = W6_POST_CLEANUP_FACTS_PATH,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    phase0_manifest = load_json(phase0_manifest_path)
    draft_matrix = load_json(phase1_draft_combination_matrix_path)
    draft_decisions = load_json(phase1_draft_decisions_path)
    w6_matrix_rows = load_json(w6_matrix_path)["rows"]
    candidate_facts_by_id = build_candidate_fact_index(load_jsonl(w6_post_cleanup_facts_path))
    cleanup_grouped_rows = build_cleanup_grouped_rows(w6_matrix_rows)
    combination_rows = enrich_combination_rows(
        draft_rows=draft_matrix["rows"],
        cleanup_grouped_rows=cleanup_grouped_rows,
        candidate_facts_by_id=candidate_facts_by_id,
    )
    decisions = build_closed_decisions(
        draft_decisions=draft_decisions,
        combination_rows=combination_rows,
    )

    dump_text(
        output_dir / SPEC_PATH.name,
        render_spec(
            phase0_manifest=phase0_manifest,
            decisions=decisions,
            combination_rows=combination_rows,
        ),
    )
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
            "schema_version": "post-cleanup-phase1-status-combination-matrix-v1",
            "phase0_manifest_ref": str(phase0_manifest_path),
            "decision_status": "closed",
            "row_count": len(combination_rows),
            "rows": combination_rows,
        },
    )

    return {
        "schema_version": "post-cleanup-phase1-status-model-v1",
        "phase0_manifest_ref": str(phase0_manifest_path),
        "decision_status": decisions["decision_status"],
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


def main() -> int:
    summary = build_post_cleanup_phase1_status_model_final()
    print("post-cleanup Phase 1 status model finalized")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
