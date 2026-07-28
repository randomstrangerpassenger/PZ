from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STAGING_ROOT = ROOT / "staging" / "source_coverage"

BLOCK_A_SUMMARY_PATH = STAGING_ROOT / "block_a" / "block_a_baseline_summary.json"
TIER_SELECTION_PATH = STAGING_ROOT / "block_b" / "tier_selection.json"
INVENTORY_PATH = STAGING_ROOT / "block_b" / "uncovered_group_inventory.json"

OUTPUT_DIR = STAGING_ROOT / "post_b"
SUMMARY_PATH = OUTPUT_DIR / "post_b_projection_summary.json"
NOTE_PATH = OUTPUT_DIR / "post_b_remeasurement_note.md"
C1_HOLD_NOTE_PATH = OUTPUT_DIR / "c1_hold_note.md"

PACKAGE_SPECS = [
    {
        "group_id": "B-1",
        "directory": "b1_consumable_package",
        "summary_name": "b1_consumable_package_summary.json",
        "coverage_name": "b1_consumable_coverage_report.json",
    },
    {
        "group_id": "B-2",
        "directory": "b2_literature_package",
        "summary_name": "b2_literature_package_summary.json",
        "coverage_name": "b2_literature_coverage_report.json",
    },
    {
        "group_id": "B-3",
        "directory": "b3_resource_package",
        "summary_name": "b3_resource_package_summary.json",
        "coverage_name": "b3_resource_coverage_report.json",
    },
    {
        "group_id": "B-W",
        "directory": "bw_wearable_package",
        "summary_name": "bw_wearable_package_summary.json",
        "coverage_name": "bw_wearable_coverage_report.json",
    },
    {
        "group_id": "B-4",
        "directory": "b4_residual_package",
        "summary_name": "b4_residual_package_summary.json",
        "coverage_name": "b4_residual_coverage_report.json",
    },
]
CORE_PATH_KEYS = ("cluster_summary", "identity_fallback", "role_fallback", "direct_use")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def dump_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def counter_from_mapping(mapping: dict[str, Any] | None) -> Counter[str]:
    return Counter({key: int(value) for key, value in (mapping or {}).items()})


def normalize_counter(counter: Counter[str], *, include_core_paths: bool = False) -> dict[str, int]:
    normalized = dict(sorted(counter.items()))
    if include_core_paths:
        for key in CORE_PATH_KEYS:
            normalized.setdefault(key, 0)
    return normalized


def build_tier_lookup(tier_selection: dict[str, Any]) -> dict[str, str]:
    tiers = tier_selection.get("tiers", {})
    tier_lookup: dict[str, str] = {}
    for tier_name, rows in tiers.items():
        for row in rows:
            tier_lookup[row["group_id"]] = tier_name
    return tier_lookup


def aggregate_source_signal_counts(summary: dict[str, Any]) -> Counter[str]:
    totals: Counter[str] = Counter()
    source_signals = summary.get("source_signals", {})
    for key, value in source_signals.items():
        if key == "item_count" or key == "counts_by_cluster":
            continue
        if key.endswith("_count") and isinstance(value, int):
            totals[key] += value
    return totals


def load_package_rows(
    inventory_rows: dict[str, dict[str, Any]],
    tier_lookup: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    package_rows: list[dict[str, Any]] = []

    cluster_counts: Counter[str] = Counter()
    use_source_counts: Counter[str] = Counter()
    selection_path_counts: Counter[str] = Counter()
    source_signal_totals: Counter[str] = Counter()
    identity_fallback_item_ids: list[str] = []
    silent_demoted_item_ids: list[str] = []

    totals = {
        "package_count": 0,
        "item_count": 0,
        "rendered_entry_count": 0,
        "smoke_sample_count": 0,
        "coverage_cluster_absent_count": 0,
        "coverage_generic_fallback_count": 0,
        "coverage_direct_use_candidate_count": 0,
        "coverage_direct_use_preserved_count": 0,
        "coverage_manual_override_required_count": 0,
        "render_hard_fail_count": 0,
        "render_warn_count": 0,
        "gate_pass_count": 0,
        "gate_fail_count": 0,
        "gate_warning_count": 0,
        "silent_demotion_count": 0,
    }

    for spec in PACKAGE_SPECS:
        group_id = spec["group_id"]
        directory = STAGING_ROOT / "block_c" / spec["directory"]
        summary_path = directory / spec["summary_name"]
        coverage_path = directory / spec["coverage_name"]

        summary = load_json(summary_path)
        coverage = load_json(coverage_path)
        inventory_row = inventory_rows[group_id]
        gate_report = summary.get("gate_report", {})
        warnings = gate_report.get("warnings", [])
        identity_fallbacks = summary.get("identity_fallbacks", {})
        silent_demotions = summary.get("silent_demotions", {})

        cluster_counts.update(counter_from_mapping(summary.get("source_signals", {}).get("counts_by_cluster")))
        use_source_counts.update(counter_from_mapping(summary.get("decision_summary", {}).get("use_source_counts")))
        selection_path_counts.update(
            counter_from_mapping(summary.get("decision_summary", {}).get("selection_path_counts"))
        )
        source_signal_totals.update(aggregate_source_signal_counts(summary))
        identity_fallback_item_ids.extend(identity_fallbacks.get("item_ids", []))
        silent_demoted_item_ids.extend(silent_demotions.get("item_ids", []))

        totals["package_count"] += 1
        totals["item_count"] += int(summary.get("item_count", 0))
        totals["rendered_entry_count"] += int(summary.get("rendered_entry_count", 0))
        totals["smoke_sample_count"] += int(summary.get("smoke_sample_count", 0))
        totals["coverage_cluster_absent_count"] += int(coverage.get("cluster_absent_count", 0))
        totals["coverage_generic_fallback_count"] += int(coverage.get("generic_fallback_count", 0))
        totals["coverage_direct_use_candidate_count"] += int(coverage.get("direct_use_candidate_count", 0))
        totals["coverage_direct_use_preserved_count"] += int(coverage.get("direct_use_preserved_count", 0))
        totals["coverage_manual_override_required_count"] += int(
            coverage.get("manual_override_required_count", 0)
        )
        totals["render_hard_fail_count"] += int(summary.get("render_validation", {}).get("hard_fail_count", 0))
        totals["render_warn_count"] += int(summary.get("render_validation", {}).get("warn_count", 0))
        totals["gate_warning_count"] += len(warnings)
        totals["silent_demotion_count"] += int(silent_demotions.get("demoted_count", 0))

        if gate_report.get("pass"):
            totals["gate_pass_count"] += 1
        else:
            totals["gate_fail_count"] += 1

        package_rows.append(
            {
                "group_id": group_id,
                "tier": tier_lookup[group_id],
                "label": inventory_row["label"],
                "kind": inventory_row["kind"],
                "item_count": int(summary.get("item_count", 0)),
                "top_levels": inventory_row.get("top_levels", []),
                "selected_cluster_counts": normalize_counter(
                    counter_from_mapping(summary.get("decision_summary", {}).get("selected_cluster_counts"))
                ),
                "use_source_counts": normalize_counter(
                    counter_from_mapping(summary.get("decision_summary", {}).get("use_source_counts")),
                    include_core_paths=True,
                ),
                "selection_path_counts": normalize_counter(
                    counter_from_mapping(summary.get("decision_summary", {}).get("selection_path_counts"))
                ),
                "source_signal_counts": normalize_counter(aggregate_source_signal_counts(summary)),
                "coverage": {
                    "assignment_rate": coverage.get("assignment_rate"),
                    "cluster_absent_count": int(coverage.get("cluster_absent_count", 0)),
                    "generic_fallback_count": int(coverage.get("generic_fallback_count", 0)),
                    "direct_use_candidate_count": int(coverage.get("direct_use_candidate_count", 0)),
                    "direct_use_preserved_count": int(coverage.get("direct_use_preserved_count", 0)),
                },
                "render_validation": {
                    "hard_fail_count": int(summary.get("render_validation", {}).get("hard_fail_count", 0)),
                    "warn_count": int(summary.get("render_validation", {}).get("warn_count", 0)),
                },
                "identity_fallbacks": {
                    "fallback_count": int(identity_fallbacks.get("fallback_count", 0)),
                    "item_ids": identity_fallbacks.get("item_ids", []),
                },
                "silent_demotions": {
                    "demoted_count": int(silent_demotions.get("demoted_count", 0)),
                    "item_ids": silent_demotions.get("item_ids", []),
                },
                "gate": {
                    "pass": bool(gate_report.get("pass")),
                    "warning_count": len(warnings),
                },
                "paths": {
                    "summary": str(summary_path),
                    "coverage_report": str(coverage_path),
                    "rendered": summary.get("paths", {}).get("rendered"),
                    "note": str(directory / f"{spec['directory']}_note.md"),
                },
            }
        )

    aggregate_payload = {
        "package_count": totals["package_count"],
        "item_count": totals["item_count"],
        "rendered_entry_count": totals["rendered_entry_count"],
        "smoke_sample_count": totals["smoke_sample_count"],
        "source_signal_counts": normalize_counter(source_signal_totals),
        "selected_cluster_counts": normalize_counter(cluster_counts),
        "use_source_counts": normalize_counter(use_source_counts, include_core_paths=True),
        "selection_path_counts": normalize_counter(selection_path_counts),
        "coverage_cluster_absent_count": totals["coverage_cluster_absent_count"],
        "coverage_generic_fallback_count": totals["coverage_generic_fallback_count"],
        "coverage_direct_use_candidate_count": totals["coverage_direct_use_candidate_count"],
        "coverage_direct_use_preserved_count": totals["coverage_direct_use_preserved_count"],
        "coverage_manual_override_required_count": totals["coverage_manual_override_required_count"],
        "render_hard_fail_count": totals["render_hard_fail_count"],
        "render_warn_count": totals["render_warn_count"],
        "gate_pass_count": totals["gate_pass_count"],
        "gate_fail_count": totals["gate_fail_count"],
        "gate_warning_count": totals["gate_warning_count"],
        "silent_demotion_count": totals["silent_demotion_count"],
        "identity_fallback_item_ids": identity_fallback_item_ids,
        "silent_demoted_item_ids": silent_demoted_item_ids,
    }
    return package_rows, aggregate_payload


def build_projected_runtime(
    block_a_summary: dict[str, Any],
    aggregate_payload: dict[str, Any],
) -> dict[str, Any]:
    baseline_runtime = block_a_summary["runtime_path_distribution"]
    baseline_path_counts = counter_from_mapping(baseline_runtime.get("path_counts"))
    baseline_active_path_counts = counter_from_mapping(baseline_runtime.get("active_path_counts"))
    baseline_silent_path_counts = counter_from_mapping(baseline_runtime.get("silent_path_counts"))
    staged_use_source_counts = counter_from_mapping(aggregate_payload.get("use_source_counts"))

    projected_path_counts = baseline_path_counts + staged_use_source_counts
    projected_active_path_counts = baseline_active_path_counts + staged_use_source_counts
    projected_silent_path_counts = baseline_silent_path_counts.copy()

    added_active_count = int(aggregate_payload["item_count"]) - int(aggregate_payload["silent_demotion_count"])

    return {
        "projection_type": "staged_package_projection",
        "assumptions": [
            "This is derived from staged B-package summaries, not from a rebuilt integrated runtime batch.",
            "All staged package rows are treated as active additions unless a package explicitly records silent demotions.",
        ],
        "baseline_runtime_row_count": int(baseline_runtime["runtime_row_count"]),
        "baseline_active_count": int(baseline_runtime["active_count"]),
        "baseline_silent_count": int(baseline_runtime["silent_count"]),
        "added_row_count": int(aggregate_payload["item_count"]),
        "added_active_count": added_active_count,
        "added_silent_count": int(aggregate_payload["silent_demotion_count"]),
        "projected_runtime_row_count": int(baseline_runtime["runtime_row_count"]) + int(aggregate_payload["item_count"]),
        "projected_active_count": int(baseline_runtime["active_count"]) + added_active_count,
        "projected_silent_count": int(baseline_runtime["silent_count"])
        + int(aggregate_payload["silent_demotion_count"]),
        "path_count_delta": normalize_counter(staged_use_source_counts, include_core_paths=True),
        "path_counts": normalize_counter(projected_path_counts, include_core_paths=True),
        "active_path_counts": normalize_counter(projected_active_path_counts, include_core_paths=True),
        "silent_path_counts": normalize_counter(projected_silent_path_counts, include_core_paths=True),
    }


def build_direct_use_decision(
    aggregate_payload: dict[str, Any],
    projected_runtime: dict[str, Any],
) -> dict[str, Any]:
    candidate_count = int(aggregate_payload["coverage_direct_use_candidate_count"])
    preserved_count = int(aggregate_payload["coverage_direct_use_preserved_count"])
    projected_direct_use = int(projected_runtime["path_counts"]["direct_use"])

    if candidate_count == 0 and preserved_count == 0 and projected_direct_use == 0:
        return {
            "decision": "hold",
            "status": "keep_current_policy",
            "signals": [
                "all_staged_b_packages_report_zero_direct_use_candidates",
                "all_staged_b_packages_report_zero_preserved_direct_use_rows",
                "projected_runtime_direct_use_count_remains_zero",
            ],
            "rationale": [
                "Post-B projection still shows no direct-use rows in the runtime path distribution.",
                "Opening direct_use now would be plan-driven speculation instead of artifact-driven expansion.",
                "Revisit only after a later runtime rebuild or C-group work produces real direct-use rows.",
            ],
        }
    return {
        "decision": "review_required",
        "status": "open_question",
        "signals": [
            "staged_packages_exposed_direct_use_candidates",
        ],
        "rationale": [
            "A later review pass is required because staged package coverage surfaced direct-use candidates.",
        ],
    }


def build_c1_hold_payload(inventory_rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    row = inventory_rows["C-1"]
    display_category_counts = dict(
        sorted(
            row.get("display_category_counts", {}).items(),
            key=lambda item: (-item[1], item[0]),
        )
    )
    return {
        "group_id": row["group_id"],
        "label": row["label"],
        "status": "hold",
        "item_count": int(row["item_count"]),
        "kind": row["kind"],
        "coverage_group": row["coverage_group"],
        "top_levels": row.get("top_levels", []),
        "display_category_counts": display_category_counts,
        "sample_item_ids": row.get("sample_item_ids", []),
        "sample_display_names": row.get("sample_display_names", []),
        "hold_reasons": [
            "Rows are outside current runtime coverage and outside current IrisData classification.",
            "B-group staged packages are complete, so the remaining backlog is now an explicit classification-expansion lane.",
            "C-group work should open only after a narrower classification/freeze target is defined.",
        ],
        "release_gate": [
            "Select a narrower C-scope subset instead of treating all 646 rows as one package.",
            "Add or project classification coverage for the chosen subset before drafting source packages.",
            "Keep the post-B direct_use hold unless later artifacts surface real direct-use rows.",
        ],
    }


def build_post_b_summary() -> dict[str, Any]:
    block_a_summary = load_json(BLOCK_A_SUMMARY_PATH)
    tier_selection = load_json(TIER_SELECTION_PATH)
    inventory = load_json(INVENTORY_PATH)
    inventory_rows = {row["group_id"]: row for row in inventory["rows"]}
    tier_lookup = build_tier_lookup(tier_selection)

    package_rows, aggregate_payload = load_package_rows(inventory_rows, tier_lookup)
    projected_runtime = build_projected_runtime(block_a_summary, aggregate_payload)
    direct_use_decision = build_direct_use_decision(aggregate_payload, projected_runtime)
    c1_hold_payload = build_c1_hold_payload(inventory_rows)

    return {
        "schema_version": "source-coverage-post-b-projection-v0",
        "inputs": {
            "block_a_summary": str(BLOCK_A_SUMMARY_PATH),
            "tier_selection": str(TIER_SELECTION_PATH),
            "uncovered_group_inventory": str(INVENTORY_PATH),
        },
        "execution_checkpoint": {
            "completed_b_groups": [spec["group_id"] for spec in PACKAGE_SPECS],
            "execution_order": tier_selection.get("execution_order", []),
            "all_b_groups_staged": True,
            "tier1_complete": True,
            "tier2_complete": True,
            "remaining_hold_group_ids": ["C-1"],
        },
        "baseline_counts": {
            "all_items_count": int(block_a_summary["counts"]["all_items_count"]),
            "runtime_items_count": int(block_a_summary["counts"]["runtime_items_count"]),
            "uncovered_items_count": int(block_a_summary["counts"]["uncovered_items_count"]),
            "b_group_count": int(block_a_summary["counts"]["b_group_count"]),
            "c_group_count": int(block_a_summary["counts"]["c_group_count"]),
        },
        "package_rows": package_rows,
        "package_totals": aggregate_payload,
        "projected_runtime": projected_runtime,
        "direct_use_decision": direct_use_decision,
        "remaining_uncovered_after_staged_b": {
            "item_count": int(c1_hold_payload["item_count"]),
            "group_ids": ["C-1"],
        },
        "c1_hold": c1_hold_payload,
        "output_paths": {
            "summary": str(SUMMARY_PATH),
            "note": str(NOTE_PATH),
            "c1_hold_note": str(C1_HOLD_NOTE_PATH),
        },
    }


def build_post_b_note(summary: dict[str, Any]) -> str:
    package_totals = summary["package_totals"]
    projected_runtime = summary["projected_runtime"]
    direct_use_decision = summary["direct_use_decision"]
    c1_hold = summary["c1_hold"]
    lines = [
        "# Post-B Remeasurement Note",
        "",
        "This checkpoint aggregates staged `B`-group package outputs.",
        "It is a projection from package artifacts, not a rebuilt integrated runtime batch.",
        "",
        "## Execution status",
        "",
        f"- completed staged `B` lanes: `{', '.join(summary['execution_checkpoint']['completed_b_groups'])}`",
        f"- staged `B` coverage rows: `{package_totals['item_count']}`",
        f"- packages passing gate: `{package_totals['gate_pass_count']}/{package_totals['package_count']}`",
        f"- remaining explicit hold lane: `C-1` (`{c1_hold['item_count']}` rows)",
        "",
        "## Projected runtime totals",
        "",
        f"- baseline runtime rows: `{projected_runtime['baseline_runtime_row_count']}`",
        f"- projected runtime rows after staged `B`: `{projected_runtime['projected_runtime_row_count']}`",
        f"- projected active rows: `{projected_runtime['projected_active_count']}`",
        f"- projected silent rows: `{projected_runtime['projected_silent_count']}`",
        "",
        "Projected path distribution:",
        "",
        f"- `cluster_summary`: `{projected_runtime['path_counts']['cluster_summary']}`",
        f"- `identity_fallback`: `{projected_runtime['path_counts']['identity_fallback']}`",
        f"- `role_fallback`: `{projected_runtime['path_counts']['role_fallback']}`",
        f"- `direct_use`: `{projected_runtime['path_counts']['direct_use']}`",
        "",
        "Path deltas contributed by staged packages:",
        "",
        f"- `cluster_summary`: `+{projected_runtime['path_count_delta']['cluster_summary']}`",
        f"- `identity_fallback`: `+{projected_runtime['path_count_delta']['identity_fallback']}`",
        f"- `role_fallback`: `+{projected_runtime['path_count_delta']['role_fallback']}`",
        f"- `direct_use`: `+{projected_runtime['path_count_delta']['direct_use']}`",
        "",
        "## Direct-use decision",
        "",
        f"- decision: `{direct_use_decision['decision']}`",
        f"- direct-use candidate count across staged packages: `{package_totals['coverage_direct_use_candidate_count']}`",
        f"- direct-use preserved count across staged packages: `{package_totals['coverage_direct_use_preserved_count']}`",
        f"- projected runtime `direct_use` count: `{projected_runtime['path_counts']['direct_use']}`",
        "- result: keep `direct_use` on hold until a later integrated rebuild or `C`-group work surfaces real direct-use rows.",
        "",
        "## Residual hold",
        "",
        f"- `C-1` remains the only uncovered hold lane with `{c1_hold['item_count']}` rows.",
        "- these rows are still outside both current runtime coverage and current `IrisData` classification.",
        "- next work is not another `B` package; it is a narrower `C` classification/input expansion target.",
    ]
    return "\n".join(lines) + "\n"


def build_c1_hold_note(summary: dict[str, Any]) -> str:
    c1_hold = summary["c1_hold"]
    display_category_lines = [
        f"- `{category}`: `{count}`"
        for category, count in c1_hold["display_category_counts"].items()
    ]
    sample_ids = ", ".join(c1_hold["sample_item_ids"][:10])
    lines = [
        "# C-1 Hold Note",
        "",
        "`C-1` stays on explicit hold after the staged `B`-group checkpoint.",
        "",
        "## Current size",
        "",
        f"- item count: `{c1_hold['item_count']}`",
        f"- label: `{c1_hold['label']}`",
        f"- kind: `{c1_hold['kind']}`",
        "",
        "## Why it is still on hold",
        "",
    ]
    lines.extend(f"- {reason}" for reason in c1_hold["hold_reasons"])
    lines.extend(
        [
            "",
            "## Dominant display categories",
            "",
        ]
    )
    lines.extend(display_category_lines)
    lines.extend(
        [
            "",
            "## Sample item ids",
            "",
            f"- `{sample_ids}`",
            "",
            "## Release gate",
            "",
        ]
    )
    lines.extend(f"- {rule}" for rule in c1_hold["release_gate"])
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = build_post_b_summary()
    dump_json(SUMMARY_PATH, summary)
    dump_markdown(NOTE_PATH, build_post_b_note(summary))
    dump_markdown(C1_HOLD_NOTE_PATH, build_c1_hold_note(summary))


if __name__ == "__main__":
    main()
