from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STAGING_ROOT = ROOT / "staging" / "source_coverage"
HISTORICAL_RUNTIME_DIR = ROOT / "staging" / "interaction_cluster" / "historical_snapshot" / "full_runtime"

POST_B_SUMMARY_PATH = STAGING_ROOT / "post_b" / "post_b_projection_summary.json"
C1_SCOPE_PARTITION_PATH = STAGING_ROOT / "c1_scope" / "c1_subset_partition.json"
C1R_SCOPE_PARTITION_PATH = STAGING_ROOT / "c1r_scope" / "c1r_subset_partition.json"
HISTORICAL_FACTS_PATH = HISTORICAL_RUNTIME_DIR / "dvf_3_3_facts.full.jsonl"
HISTORICAL_DECISIONS_PATH = HISTORICAL_RUNTIME_DIR / "dvf_3_3_decisions.full.jsonl"
ROLE_FALLBACK_REPLACEMENT_INDEX_PATH = (
    STAGING_ROOT / "block_c" / "role_fallback_hollow_post_apply_preview_index.json"
)

OUTPUT_DIR = STAGING_ROOT / "post_c"
SUMMARY_PATH = OUTPUT_DIR / "post_c_projection_summary.json"
NOTE_PATH = OUTPUT_DIR / "post_c_remeasurement_note.md"
HOLD_NOTE_PATH = OUTPUT_DIR / "c_hold_note.md"

PACKAGE_SPECS = [
    {
        "group_id": "C1-A",
        "label": "Vehicle maintenance",
        "directory": "c1a_vehicle_package",
        "summary_name": "c1a_vehicle_package_summary.json",
        "coverage_name": "c1a_vehicle_coverage_report.json",
    },
    {
        "group_id": "C1-C",
        "label": "Moveable furniture",
        "directory": "c1c_moveable_package",
        "summary_name": "c1c_moveable_package_summary.json",
        "coverage_name": "c1c_moveable_coverage_report.json",
    },
    {
        "group_id": "C1-B",
        "label": "Portable storage",
        "directory": "c1b_portable_storage_package",
        "summary_name": "c1b_portable_storage_package_summary.json",
        "coverage_name": "c1b_portable_storage_coverage_report.json",
    },
    {
        "group_id": "C1-E",
        "label": "Security",
        "directory": "c1e_security_package",
        "summary_name": "c1e_security_package_summary.json",
        "coverage_name": "c1e_security_coverage_report.json",
    },
    {
        "group_id": "C1-D",
        "label": "Appearance",
        "directory": "c1d_appearance_package",
        "summary_name": "c1d_appearance_package_summary.json",
        "coverage_name": "c1d_appearance_coverage_report.json",
    },
    {
        "group_id": "C1-RA",
        "label": "Desk and pocket smalls",
        "directory": "c1ra_desk_pocket_package",
        "summary_name": "c1ra_desk_pocket_package_summary.json",
        "coverage_name": "c1ra_desk_pocket_coverage_report.json",
    },
    {
        "group_id": "C1-RB",
        "label": "Household care",
        "directory": "c1rb_household_care_package",
        "summary_name": "c1rb_household_care_package_summary.json",
        "coverage_name": "c1rb_household_care_coverage_report.json",
    },
    {
        "group_id": "C1-RD",
        "label": "Scrap and empty-material",
        "directory": "c1rd_scrap_empty_package",
        "summary_name": "c1rd_scrap_empty_package_summary.json",
        "coverage_name": "c1rd_scrap_empty_coverage_report.json",
    },
    {
        "group_id": "C1-RC",
        "label": "Play, media, and novelty",
        "directory": "c1rc_play_media_package",
        "summary_name": "c1rc_play_media_package_summary.json",
        "coverage_name": "c1rc_play_media_coverage_report.json",
    },
    {
        "group_id": "C1-RE",
        "label": "Utility miscellany",
        "directory": "c1re_utility_misc_package",
        "summary_name": "c1re_utility_misc_package_summary.json",
        "coverage_name": "c1re_utility_misc_coverage_report.json",
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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


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


def combine_counters(*counters: Counter[str]) -> Counter[str]:
    combined: Counter[str] = Counter()
    for counter in counters:
        for key, value in counter.items():
            combined[key] += int(value)
    return combined


def diff_counters(after: Counter[str], before: Counter[str]) -> Counter[str]:
    delta: Counter[str] = Counter()
    for key in set(before) | set(after):
        value = int(after.get(key, 0)) - int(before.get(key, 0))
        if value != 0:
            delta[key] = value
    return delta


def resolve_runtime_path(*, fact_row: dict[str, Any], decision_row: dict[str, Any]) -> str:
    fact_origin = fact_row.get("fact_origin") or {}
    primary_use_sources = fact_origin.get("primary_use") or []
    primary_use_source = str(primary_use_sources[0]) if primary_use_sources else None
    if primary_use_source in CORE_PATH_KEYS:
        return primary_use_source
    return str(decision_row.get("use_source") or "(missing)")


def split_state_path_counts(
    *,
    fact_rows: list[dict[str, Any]],
    decision_rows: list[dict[str, Any]],
) -> tuple[Counter[str], Counter[str], Counter[str], Counter[str]]:
    fact_map = {str(row["item_id"]): row for row in fact_rows}
    path_counts: Counter[str] = Counter()
    active_path_counts: Counter[str] = Counter()
    silent_path_counts: Counter[str] = Counter()
    state_counts: Counter[str] = Counter()

    for decision_row in decision_rows:
        item_id = str(decision_row["item_id"])
        fact_row = fact_map[item_id]
        state = str(decision_row.get("state") or "(missing)")
        path_key = resolve_runtime_path(fact_row=fact_row, decision_row=decision_row)
        path_counts[path_key] += 1
        state_counts[state] += 1
        if state == "silent":
            silent_path_counts[path_key] += 1
        else:
            active_path_counts[path_key] += 1

    return path_counts, active_path_counts, silent_path_counts, state_counts


def load_package_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    package_rows: list[dict[str, Any]] = []
    selected_cluster_counts: Counter[str] = Counter()
    use_source_counts: Counter[str] = Counter()
    selection_path_counts: Counter[str] = Counter()

    totals = {
        "package_count": 0,
        "item_count": 0,
        "rendered_entry_count": 0,
        "smoke_sample_count": 0,
        "coverage_cluster_absent_count": 0,
        "coverage_generic_fallback_count": 0,
        "coverage_direct_use_candidate_count": 0,
        "coverage_direct_use_preserved_count": 0,
        "render_hard_fail_count": 0,
        "render_warn_count": 0,
        "gate_pass_count": 0,
        "gate_fail_count": 0,
        "gate_warning_count": 0,
    }

    for spec in PACKAGE_SPECS:
        directory = STAGING_ROOT / "block_c" / spec["directory"]
        summary_path = directory / spec["summary_name"]
        coverage_path = directory / spec["coverage_name"]
        summary = load_json(summary_path)
        coverage = load_json(coverage_path)
        gate_report = summary.get("gate_report", {})
        warnings = gate_report.get("warnings", [])

        selected_cluster_counts.update(counter_from_mapping(summary.get("decision_summary", {}).get("selected_cluster_counts")))
        use_source_counts.update(counter_from_mapping(summary.get("decision_summary", {}).get("use_source_counts")))
        selection_path_counts.update(counter_from_mapping(summary.get("decision_summary", {}).get("selection_path_counts")))

        totals["package_count"] += 1
        totals["item_count"] += int(summary.get("item_count", 0))
        totals["rendered_entry_count"] += int(summary.get("rendered_entry_count", 0))
        totals["smoke_sample_count"] += int(summary.get("smoke_sample_count", 0))
        totals["coverage_cluster_absent_count"] += int(coverage.get("cluster_absent_count", 0))
        totals["coverage_generic_fallback_count"] += int(coverage.get("generic_fallback_count", 0))
        totals["coverage_direct_use_candidate_count"] += int(coverage.get("direct_use_candidate_count", 0))
        totals["coverage_direct_use_preserved_count"] += int(coverage.get("direct_use_preserved_count", 0))
        totals["render_hard_fail_count"] += int(summary.get("render_validation", {}).get("hard_fail_count", 0))
        totals["render_warn_count"] += int(summary.get("render_validation", {}).get("warn_count", 0))
        totals["gate_warning_count"] += len(warnings)
        if gate_report.get("pass"):
            totals["gate_pass_count"] += 1
        else:
            totals["gate_fail_count"] += 1

        package_rows.append(
            {
                "group_id": spec["group_id"],
                "label": spec["label"],
                "item_count": int(summary.get("item_count", 0)),
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
                "render_validation": {
                    "hard_fail_count": int(summary.get("render_validation", {}).get("hard_fail_count", 0)),
                    "warn_count": int(summary.get("render_validation", {}).get("warn_count", 0)),
                },
                "coverage": {
                    "cluster_absent_count": int(coverage.get("cluster_absent_count", 0)),
                    "generic_fallback_count": int(coverage.get("generic_fallback_count", 0)),
                    "direct_use_candidate_count": int(coverage.get("direct_use_candidate_count", 0)),
                    "direct_use_preserved_count": int(coverage.get("direct_use_preserved_count", 0)),
                },
                "gate": {
                    "pass": bool(gate_report.get("pass")),
                    "warning_count": len(warnings),
                },
                "paths": {
                    "summary": str(summary_path),
                    "coverage_report": str(coverage_path),
                    "rendered": summary.get("paths", {}).get("rendered"),
                },
            }
        )

    aggregate_payload = {
        "package_count": totals["package_count"],
        "item_count": totals["item_count"],
        "rendered_entry_count": totals["rendered_entry_count"],
        "smoke_sample_count": totals["smoke_sample_count"],
        "selected_cluster_counts": normalize_counter(selected_cluster_counts),
        "use_source_counts": normalize_counter(use_source_counts, include_core_paths=True),
        "selection_path_counts": normalize_counter(selection_path_counts),
        "coverage_cluster_absent_count": totals["coverage_cluster_absent_count"],
        "coverage_generic_fallback_count": totals["coverage_generic_fallback_count"],
        "coverage_direct_use_candidate_count": totals["coverage_direct_use_candidate_count"],
        "coverage_direct_use_preserved_count": totals["coverage_direct_use_preserved_count"],
        "render_hard_fail_count": totals["render_hard_fail_count"],
        "render_warn_count": totals["render_warn_count"],
        "gate_pass_count": totals["gate_pass_count"],
        "gate_fail_count": totals["gate_fail_count"],
        "gate_warning_count": totals["gate_warning_count"],
    }
    return package_rows, aggregate_payload


def load_replacement_payload() -> dict[str, Any]:
    replacement_index = load_json(ROLE_FALLBACK_REPLACEMENT_INDEX_PATH)
    historical_facts_map = {
        str(row["item_id"]): row for row in load_jsonl(HISTORICAL_FACTS_PATH)
    }
    historical_decisions_map = {
        str(row["item_id"]): row for row in load_jsonl(HISTORICAL_DECISIONS_PATH)
    }

    package_rows: list[dict[str, Any]] = []
    historical_path_counts: Counter[str] = Counter()
    replacement_path_counts: Counter[str] = Counter()
    historical_active_path_counts: Counter[str] = Counter()
    replacement_active_path_counts: Counter[str] = Counter()
    historical_silent_path_counts: Counter[str] = Counter()
    replacement_silent_path_counts: Counter[str] = Counter()
    historical_state_counts: Counter[str] = Counter()
    replacement_state_counts: Counter[str] = Counter()
    missing_historical_targets: list[str] = []

    for package in replacement_index.get("packages", []):
        facts_path = Path(package["paths"]["facts"])
        decisions_path = Path(package["paths"]["decisions"])
        facts_rows = load_jsonl(facts_path)
        decisions_rows = load_jsonl(decisions_path)

        fact_ids = {str(row["item_id"]) for row in facts_rows}
        decision_ids = {str(row["item_id"]) for row in decisions_rows}
        expected_count = int(package.get("ready_row_count", 0))
        if fact_ids != decision_ids:
            raise ValueError(f"Replacement package {package['package_id']} item-id sets are inconsistent")
        if len(fact_ids) != expected_count:
            raise ValueError(
                f"Replacement package {package['package_id']} expected {expected_count} rows but found {len(fact_ids)}"
            )

        package_historical_facts_rows: list[dict[str, Any]] = []
        package_historical_decisions_rows: list[dict[str, Any]] = []
        for item_id in sorted(fact_ids):
            historical_fact_row = historical_facts_map.get(item_id)
            historical_decision_row = historical_decisions_map.get(item_id)
            if historical_fact_row is None or historical_decision_row is None:
                missing_historical_targets.append(item_id)
                continue
            package_historical_facts_rows.append(historical_fact_row)
            package_historical_decisions_rows.append(historical_decision_row)

        if missing_historical_targets:
            missing_targets = ", ".join(sorted(set(missing_historical_targets))[:8])
            raise ValueError(f"Replacement package targets missing from historical runtime: {missing_targets}")

        package_historical_path_counts, package_historical_active_path_counts, package_historical_silent_path_counts, package_historical_state_counts = split_state_path_counts(
            fact_rows=package_historical_facts_rows,
            decision_rows=package_historical_decisions_rows,
        )
        package_replacement_path_counts, package_replacement_active_path_counts, package_replacement_silent_path_counts, package_replacement_state_counts = split_state_path_counts(
            fact_rows=facts_rows,
            decision_rows=decisions_rows,
        )

        historical_path_counts = combine_counters(historical_path_counts, package_historical_path_counts)
        replacement_path_counts = combine_counters(replacement_path_counts, package_replacement_path_counts)
        historical_active_path_counts = combine_counters(
            historical_active_path_counts,
            package_historical_active_path_counts,
        )
        replacement_active_path_counts = combine_counters(
            replacement_active_path_counts,
            package_replacement_active_path_counts,
        )
        historical_silent_path_counts = combine_counters(
            historical_silent_path_counts,
            package_historical_silent_path_counts,
        )
        replacement_silent_path_counts = combine_counters(
            replacement_silent_path_counts,
            package_replacement_silent_path_counts,
        )
        historical_state_counts = combine_counters(historical_state_counts, package_historical_state_counts)
        replacement_state_counts = combine_counters(replacement_state_counts, package_replacement_state_counts)

        package_rows.append(
            {
                "package_id": package["package_id"],
                "ready_row_count": expected_count,
                "parked_row_count": int(package.get("parked_row_count", 0)),
                "historical_path_counts": normalize_counter(
                    package_historical_path_counts,
                    include_core_paths=True,
                ),
                "replacement_path_counts": normalize_counter(
                    package_replacement_path_counts,
                    include_core_paths=True,
                ),
                "path_count_delta": normalize_counter(
                    diff_counters(package_replacement_path_counts, package_historical_path_counts),
                    include_core_paths=True,
                ),
                "state_count_delta": normalize_counter(
                    diff_counters(package_replacement_state_counts, package_historical_state_counts)
                ),
                "direct_use_preserved_count": int(
                    package.get("gate_report", {})
                    .get("metrics", {})
                    .get("direct_use_preserved_count", 0)
                ),
                "special_context_preserved_count": int(
                    package.get("gate_report", {})
                    .get("metrics", {})
                    .get("special_context_preserved_count", 0)
                ),
                "paths": {
                    "facts": str(facts_path),
                    "decisions": str(decisions_path),
                    "rendered": package["paths"]["rendered"],
                },
            }
        )

    path_count_delta = diff_counters(replacement_path_counts, historical_path_counts)
    active_path_count_delta = diff_counters(
        replacement_active_path_counts,
        historical_active_path_counts,
    )
    silent_path_count_delta = diff_counters(
        replacement_silent_path_counts,
        historical_silent_path_counts,
    )
    state_count_delta = diff_counters(replacement_state_counts, historical_state_counts)

    return {
        "package_count": int(replacement_index.get("totals", {}).get("package_count", 0)),
        "ready_row_count": int(replacement_index.get("totals", {}).get("ready_row_count", 0)),
        "parked_row_count": int(replacement_index.get("totals", {}).get("parked_row_count", 0)),
        "gate_pass_count": int(replacement_index.get("totals", {}).get("gate_pass_count", 0)),
        "direct_use_expected_count": int(
            replacement_index.get("totals", {}).get("direct_use_expected_count", 0)
        ),
        "direct_use_preserved_count": int(
            replacement_index.get("totals", {}).get("direct_use_preserved_count", 0)
        ),
        "special_context_expected_count": int(
            replacement_index.get("totals", {}).get("special_context_expected_count", 0)
        ),
        "special_context_preserved_count": int(
            replacement_index.get("totals", {}).get("special_context_preserved_count", 0)
        ),
        "path_count_delta": normalize_counter(path_count_delta, include_core_paths=True),
        "active_path_count_delta": normalize_counter(
            active_path_count_delta,
            include_core_paths=True,
        ),
        "silent_path_count_delta": normalize_counter(
            silent_path_count_delta,
            include_core_paths=True,
        ),
        "state_count_delta": normalize_counter(state_count_delta),
        "row_count_delta": int(sum(path_count_delta.values())),
        "active_count_delta": int(state_count_delta.get("active", 0)),
        "silent_count_delta": int(state_count_delta.get("silent", 0)),
        "package_rows": package_rows,
        "inputs": {
            "replacement_index": str(ROLE_FALLBACK_REPLACEMENT_INDEX_PATH),
            "historical_facts": str(HISTORICAL_FACTS_PATH),
            "historical_decisions": str(HISTORICAL_DECISIONS_PATH),
        },
    }


def build_projected_runtime(
    post_b_summary: dict[str, Any],
    aggregate_payload: dict[str, Any],
    replacement_payload: dict[str, Any],
) -> dict[str, Any]:
    baseline_runtime = post_b_summary["projected_runtime"]
    baseline_path_counts = counter_from_mapping(baseline_runtime.get("path_counts"))
    baseline_active_path_counts = counter_from_mapping(baseline_runtime.get("active_path_counts"))
    baseline_silent_path_counts = counter_from_mapping(baseline_runtime.get("silent_path_counts"))
    staged_use_source_counts = counter_from_mapping(aggregate_payload.get("use_source_counts"))
    replacement_path_delta = counter_from_mapping(replacement_payload.get("path_count_delta"))
    replacement_active_path_delta = counter_from_mapping(
        replacement_payload.get("active_path_count_delta")
    )
    replacement_silent_path_delta = counter_from_mapping(
        replacement_payload.get("silent_path_count_delta")
    )

    projected_path_counts = combine_counters(
        baseline_path_counts,
        staged_use_source_counts,
        replacement_path_delta,
    )
    projected_active_path_counts = combine_counters(
        baseline_active_path_counts,
        staged_use_source_counts,
        replacement_active_path_delta,
    )
    projected_silent_path_counts = combine_counters(
        baseline_silent_path_counts,
        replacement_silent_path_delta,
    )
    path_count_delta = combine_counters(staged_use_source_counts, replacement_path_delta)

    return {
        "projection_type": "staged_package_projection_with_replacements",
        "assumptions": [
            "This is derived from staged C-package summaries on top of the staged post-B checkpoint.",
            "Staged C package rows are treated as active additions because none record silent demotions.",
            "C1-F/C1-G post-apply previews are treated as deterministic replacements over existing historical runtime rows.",
        ],
        "baseline_runtime_row_count": int(baseline_runtime["projected_runtime_row_count"]),
        "baseline_active_count": int(baseline_runtime["projected_active_count"]),
        "baseline_silent_count": int(baseline_runtime["projected_silent_count"]),
        "added_row_count": int(aggregate_payload["item_count"]),
        "replacement_row_delta_count": int(replacement_payload["row_count_delta"]),
        "replacement_applied_count": int(replacement_payload["ready_row_count"]),
        "replacement_parked_count": int(replacement_payload["parked_row_count"]),
        "added_active_count": int(aggregate_payload["item_count"]),
        "replacement_active_count_delta": int(replacement_payload["active_count_delta"]),
        "added_silent_count": 0,
        "replacement_silent_count_delta": int(replacement_payload["silent_count_delta"]),
        "projected_runtime_row_count": int(baseline_runtime["projected_runtime_row_count"])
        + int(aggregate_payload["item_count"])
        + int(replacement_payload["row_count_delta"]),
        "projected_active_count": int(baseline_runtime["projected_active_count"])
        + int(aggregate_payload["item_count"])
        + int(replacement_payload["active_count_delta"]),
        "projected_silent_count": int(baseline_runtime["projected_silent_count"])
        + int(replacement_payload["silent_count_delta"]),
        "path_count_delta": normalize_counter(path_count_delta, include_core_paths=True),
        "additive_path_count_delta": normalize_counter(
            staged_use_source_counts,
            include_core_paths=True,
        ),
        "replacement_path_count_delta": normalize_counter(
            replacement_path_delta,
            include_core_paths=True,
        ),
        "path_counts": normalize_counter(projected_path_counts, include_core_paths=True),
        "active_path_counts": normalize_counter(projected_active_path_counts, include_core_paths=True),
        "silent_path_counts": normalize_counter(projected_silent_path_counts, include_core_paths=True),
    }


def build_direct_use_decision(
    aggregate_payload: dict[str, Any],
    replacement_payload: dict[str, Any],
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
                "all_staged_c_packages_report_zero_direct_use_candidates",
                "all_staged_c_packages_report_zero_preserved_direct_use_rows",
                "projected_runtime_direct_use_count_remains_zero",
            ],
        }
    replacement_ready_count = int(replacement_payload.get("ready_row_count", 0))
    replacement_preserved_count = int(replacement_payload.get("direct_use_preserved_count", 0))
    if replacement_ready_count > 0 and replacement_preserved_count > 0 and projected_direct_use > 0:
        return {
            "decision": "review_required",
            "status": "artifact_backed_replacement_lane",
            "signals": [
                "post_apply_replacement_preview_reports_ready_direct_use_rows",
                "replacement_lane_preserved_direct_use_rows",
                "projected_runtime_direct_use_count_is_nonzero",
            ],
        }
    return {
        "decision": "review_required",
        "status": "open_question",
        "signals": ["staged_packages_exposed_direct_use_candidates"],
    }


def summarize_hold_rows(rows: list[dict[str, Any]], subset_id: str, label: str, reasons: list[str]) -> dict[str, Any]:
    display_category_counts: Counter[str] = Counter()
    for row in rows:
        display_category_counts[str(row.get("display_category") or "(none)")] += 1
    return {
        "subset_id": subset_id,
        "label": label,
        "status": "hold",
        "item_count": len(rows),
        "display_category_counts": dict(sorted(display_category_counts.items(), key=lambda item: (-item[1], item[0]))),
        "sample_item_ids": [row["item_id"] for row in rows[:12]],
        "hold_reasons": reasons,
    }


def build_hold_payload() -> dict[str, Any]:
    c1_rows = load_json(C1_SCOPE_PARTITION_PATH)["rows"]
    c1r_rows = load_json(C1R_SCOPE_PARTITION_PATH)["rows"]

    h1_rows = [row for row in c1_rows if row.get("subset_id") == "C1-H1"]
    h2_rows = [row for row in c1_rows if row.get("subset_id") == "C1-H2"]
    rh_rows = [row for row in c1r_rows if row.get("residual_subset_id") == "C1-RH"]

    hold_rows = [
        summarize_hold_rows(
            h1_rows,
            "C1-H1",
            "Medical body-state overlays",
            [
                "Rows are body-overlay state variants, not ordinary player-facing item usages.",
                "Packaging them as item clusters would blur state rendering with normal item semantics.",
            ],
        ),
        summarize_hold_rows(
            h2_rows,
            "C1-H2",
            "Zed-damage overlays",
            [
                "Rows are corpse/body damage overlays rather than discrete usage items.",
                "They require a separate body-state policy instead of source-package expansion.",
            ],
        ),
        summarize_hold_rows(
            rh_rows,
            "C1-RH",
            "Residual odd-hold",
            [
                "Rows remain low-cohesion outliers such as corpses, hidden props, or implicit body/equipment placeholders.",
                "Creating another residual cluster here would collapse unlike concepts without a stable player-facing frame.",
            ],
        ),
    ]

    return {
        "hold_subset_ids": [row["subset_id"] for row in hold_rows],
        "item_count": sum(row["item_count"] for row in hold_rows),
        "rows": hold_rows,
    }


def build_post_c_summary() -> dict[str, Any]:
    post_b_summary = load_json(POST_B_SUMMARY_PATH)
    package_rows, aggregate_payload = load_package_rows()
    replacement_payload = load_replacement_payload()
    projected_runtime = build_projected_runtime(post_b_summary, aggregate_payload, replacement_payload)
    direct_use_decision = build_direct_use_decision(
        aggregate_payload,
        replacement_payload,
        projected_runtime,
    )
    hold_payload = build_hold_payload()

    return {
        "schema_version": "source-coverage-post-c-projection-v0",
        "inputs": {
            "post_b_summary": str(POST_B_SUMMARY_PATH),
            "c1_scope_partition": str(C1_SCOPE_PARTITION_PATH),
            "c1r_scope_partition": str(C1R_SCOPE_PARTITION_PATH),
            "role_fallback_replacement_index": str(ROLE_FALLBACK_REPLACEMENT_INDEX_PATH),
        },
        "execution_checkpoint": {
            "completed_c_groups": [spec["group_id"] for spec in PACKAGE_SPECS],
            "completed_replacement_groups": [
                row["package_id"] for row in replacement_payload["package_rows"]
            ],
            "all_executable_residual_subsets_staged": True,
            "remaining_hold_subset_ids": hold_payload["hold_subset_ids"],
        },
        "package_rows": package_rows,
        "package_totals": aggregate_payload,
        "replacement_totals": replacement_payload,
        "projected_runtime": projected_runtime,
        "direct_use_decision": direct_use_decision,
        "remaining_uncovered_after_staged_c": {
            "item_count": hold_payload["item_count"],
            "hold_subset_ids": hold_payload["hold_subset_ids"],
        },
        "hold_payload": hold_payload,
        "output_paths": {
            "summary": str(SUMMARY_PATH),
            "note": str(NOTE_PATH),
            "hold_note": str(HOLD_NOTE_PATH),
        },
    }


def build_post_c_note(summary: dict[str, Any]) -> str:
    package_totals = summary["package_totals"]
    replacement_totals = summary["replacement_totals"]
    projected_runtime = summary["projected_runtime"]
    hold_payload = summary["hold_payload"]
    lines = [
        "# Post-C Remeasurement Note",
        "",
        "This checkpoint aggregates staged `C`-group package outputs plus post-apply replacement previews on top of the staged post-`B` projection.",
        "",
        "## Execution status",
        "",
        f"- completed staged `C` lanes: `{', '.join(summary['execution_checkpoint']['completed_c_groups'])}`",
        f"- staged `C` coverage rows: `{package_totals['item_count']}`",
        f"- packages passing gate: `{package_totals['gate_pass_count']}/{package_totals['package_count']}`",
        f"- replacement-ready rows: `{replacement_totals['ready_row_count']}`",
        f"- replacement parked rows: `{replacement_totals['parked_row_count']}`",
        f"- remaining hold rows after staged `C`: `{hold_payload['item_count']}`",
        "",
        "## Projected runtime totals",
        "",
        f"- baseline staged post-`B` runtime rows: `{projected_runtime['baseline_runtime_row_count']}`",
        f"- projected runtime rows after staged `C`: `{projected_runtime['projected_runtime_row_count']}`",
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
        "Replacement lane delta:",
        "",
        f"- role_fallback -> direct_use replacements: `{replacement_totals['ready_row_count']}`",
        f"- replacement path delta: `{replacement_totals['path_count_delta']}`",
        "",
        "## Residual hold after staged C",
        "",
        f"- hold subsets: `{', '.join(hold_payload['hold_subset_ids'])}`",
        f"- hold item count: `{hold_payload['item_count']}`",
        "- remaining work is now hold-policy review plus later integrated remeasurement, not another executable residual source package.",
    ]
    return "\n".join(lines) + "\n"


def build_hold_note(summary: dict[str, Any]) -> str:
    lines = [
        "# C Hold Note",
        "",
        "All executable `C` residual/source lanes are now staged.",
        "The remaining rows stay on explicit hold because they are overlays, hidden props, or low-cohesion outliers.",
        "",
    ]
    for row in summary["hold_payload"]["rows"]:
        lines.extend(
            [
                f"## {row['subset_id']} {row['label']}",
                "",
                f"- item count: `{row['item_count']}`",
                "- hold reasons:",
            ]
        )
        lines.extend(f"  - {reason}" for reason in row["hold_reasons"])
        lines.append("- sample item ids:")
        sample_ids = ", ".join(row["sample_item_ids"][:8])
        lines.append(f"  - `{sample_ids}`")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    summary = build_post_c_summary()
    dump_json(SUMMARY_PATH, summary)
    dump_markdown(NOTE_PATH, build_post_c_note(summary))
    dump_markdown(HOLD_NOTE_PATH, build_hold_note(summary))


if __name__ == "__main__":
    main()
