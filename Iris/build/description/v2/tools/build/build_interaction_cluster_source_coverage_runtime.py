from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from shutil import copyfile
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.compose_layer3_text import STAGING_COMPOSE_CONTEXT, build_rendered
from tools.build.export_dvf_3_3_lua_bridge import export_lua_bridge
from tools.build.report_source_coverage_post_b import PACKAGE_SPECS as B_PACKAGE_SPECS
from tools.build.report_source_coverage_post_c import (
    PACKAGE_SPECS as C_PACKAGE_SPECS,
    ROLE_FALLBACK_REPLACEMENT_INDEX_PATH,
)
from tools.build.validate_interaction_cluster_phase_d_runtime import build_phase_d_runtime_report


DATA_DIR = ROOT / "data"
SOURCE_COVERAGE_DIR = ROOT / "staging" / "source_coverage"
POST_C_SUMMARY_PATH = SOURCE_COVERAGE_DIR / "post_c" / "post_c_projection_summary.json"

HISTORICAL_RUNTIME_DIR = ROOT / "staging" / "interaction_cluster" / "historical_snapshot" / "full_runtime"
HISTORICAL_FACTS_PATH = HISTORICAL_RUNTIME_DIR / "dvf_3_3_facts.full.jsonl"
HISTORICAL_DECISIONS_PATH = HISTORICAL_RUNTIME_DIR / "dvf_3_3_decisions.full.jsonl"
HISTORICAL_SUMMARY_PATH = HISTORICAL_RUNTIME_DIR / "historical_runtime_summary.json"

INTEGRATED_RUNTIME_DIR = ROOT / "staging" / "interaction_cluster" / "source_coverage_runtime"
INTEGRATED_FACTS_PATH = INTEGRATED_RUNTIME_DIR / "dvf_3_3_facts.integrated.jsonl"
INTEGRATED_DECISIONS_PATH = INTEGRATED_RUNTIME_DIR / "dvf_3_3_decisions.integrated.jsonl"
INTEGRATED_RENDERED_PATH = INTEGRATED_RUNTIME_DIR / "dvf_3_3_rendered.integrated.json"
INTEGRATED_BRIDGE_REPORT_PATH = INTEGRATED_RUNTIME_DIR / "phase_d_lua_bridge_report.integrated.json"
INTEGRATED_RUNTIME_REPORT_PATH = INTEGRATED_RUNTIME_DIR / "phase_d_runtime_report.integrated.json"
INTEGRATED_SUMMARY_PATH = INTEGRATED_RUNTIME_DIR / "source_coverage_runtime_summary.json"
INTEGRATED_NOTE_PATH = INTEGRATED_RUNTIME_DIR / "source_coverage_runtime_note.md"

IRIS_MOD_ROOT = ROOT.parents[3] / "Iris"
WORKSPACE_LAYER3_DATA_PATH = (
    IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3Data.lua"
)
WORKSPACE_LAYER3_BACKUP_PATH = INTEGRATED_RUNTIME_DIR / "IrisLayer3Data.pre_source_coverage_runtime.backup.lua"

CORE_PATH_KEYS = ("cluster_summary", "identity_fallback", "role_fallback", "direct_use")
PACKAGE_SPECS = [*B_PACKAGE_SPECS, *C_PACKAGE_SPECS]


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


def dump_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_counter(counter: Counter[str], *, keys: tuple[str, ...] | None = None) -> dict[str, int]:
    normalized = dict(sorted(counter.items()))
    for key in keys or ():
        normalized.setdefault(key, 0)
    return normalized


def item_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {str(row["item_id"]) for row in rows}


def load_package_payload(spec: dict[str, Any]) -> dict[str, Any]:
    summary_path = SOURCE_COVERAGE_DIR / "block_c" / spec["directory"] / spec["summary_name"]
    summary = load_json(summary_path)

    facts_path = Path(summary["paths"]["facts"])
    decisions_path = Path(summary["paths"]["decisions"])
    rendered_path = Path(summary["paths"]["rendered"])

    facts_rows = load_jsonl(facts_path)
    decisions_rows = load_jsonl(decisions_path)
    rendered = load_json(rendered_path)

    facts_ids = item_ids(facts_rows)
    decisions_ids = item_ids(decisions_rows)
    rendered_ids = set(rendered.get("entries", {}).keys())
    expected_count = int(summary.get("item_count", 0))

    if facts_ids != decisions_ids or facts_ids != rendered_ids:
        raise ValueError(f"Package {spec['group_id']} item-id sets are inconsistent")
    if len(facts_ids) != expected_count:
        raise ValueError(
            f"Package {spec['group_id']} expected {expected_count} rows but found {len(facts_ids)}"
        )

    return {
        "group_id": spec["group_id"],
        "summary_path": str(summary_path),
        "item_count": expected_count,
        "facts_path": str(facts_path),
        "decisions_path": str(decisions_path),
        "rendered_path": str(rendered_path),
        "facts_rows": facts_rows,
        "decisions_rows": decisions_rows,
    }


def load_replacement_payloads() -> list[dict[str, Any]]:
    replacement_index = load_json(ROLE_FALLBACK_REPLACEMENT_INDEX_PATH)
    payloads: list[dict[str, Any]] = []

    for package in replacement_index.get("packages", []):
        facts_path = Path(package["paths"]["facts"])
        decisions_path = Path(package["paths"]["decisions"])
        rendered_path = Path(package["paths"]["rendered"])

        facts_rows = load_jsonl(facts_path)
        decisions_rows = load_jsonl(decisions_path)
        rendered = load_json(rendered_path)

        facts_ids = item_ids(facts_rows)
        decisions_ids = item_ids(decisions_rows)
        rendered_ids = set(rendered.get("entries", {}).keys())
        expected_count = int(package.get("ready_row_count", 0))

        if facts_ids != decisions_ids or facts_ids != rendered_ids:
            raise ValueError(f"Replacement package {package['package_id']} item-id sets are inconsistent")
        if len(facts_ids) != expected_count:
            raise ValueError(
                f"Replacement package {package['package_id']} expected {expected_count} rows but found {len(facts_ids)}"
            )

        payloads.append(
            {
                "group_id": package["package_id"],
                "summary_path": str(ROLE_FALLBACK_REPLACEMENT_INDEX_PATH),
                "item_count": expected_count,
                "facts_path": str(facts_path),
                "decisions_path": str(decisions_path),
                "rendered_path": str(rendered_path),
                "facts_rows": facts_rows,
                "decisions_rows": decisions_rows,
            }
        )

    return payloads


def merge_rows(
    *,
    historical_rows: list[dict[str, Any]],
    package_payloads: list[dict[str, Any]],
    row_kind: str,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    merged_rows, duplicates, _ = merge_rows_with_sources(
        historical_rows=historical_rows,
        package_payloads=package_payloads,
        row_kind=row_kind,
    )
    return merged_rows, duplicates


def merge_rows_with_sources(
    *,
    historical_rows: list[dict[str, Any]],
    package_payloads: list[dict[str, Any]],
    row_kind: str,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, str]]:
    merged_by_item: dict[str, dict[str, Any]] = {}
    source_by_item: dict[str, str] = {}
    duplicates: list[dict[str, str]] = []

    for row in historical_rows:
        item_id = str(row["item_id"])
        merged_by_item[item_id] = row
        source_by_item[item_id] = "historical_full_runtime"

    for payload in package_payloads:
        package_rows = payload[f"{row_kind}_rows"]
        for row in package_rows:
            item_id = str(row["item_id"])
            if item_id in merged_by_item:
                duplicates.append(
                    {
                        "item_id": item_id,
                        "row_kind": row_kind,
                        "existing_source": source_by_item[item_id],
                        "incoming_source": payload["group_id"],
                    }
                )
                continue
            merged_by_item[item_id] = row
            source_by_item[item_id] = payload["group_id"]

    merged_rows = [merged_by_item[item_id] for item_id in sorted(merged_by_item)]
    return merged_rows, duplicates, source_by_item


def apply_replacement_rows(
    *,
    merged_rows: list[dict[str, Any]],
    source_by_item: dict[str, str],
    replacement_payloads: list[dict[str, Any]],
    row_kind: str,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    replaced_by_item = {str(row["item_id"]): row for row in merged_rows}
    updated_source_by_item = dict(source_by_item)
    missing_targets: list[dict[str, str]] = []
    replacements: list[dict[str, str]] = []

    for payload in replacement_payloads:
        package_rows = payload[f"{row_kind}_rows"]
        for row in package_rows:
            item_id = str(row["item_id"])
            if item_id not in replaced_by_item:
                missing_targets.append(
                    {
                        "item_id": item_id,
                        "row_kind": row_kind,
                        "incoming_source": payload["group_id"],
                    }
                )
                continue
            replacements.append(
                {
                    "item_id": item_id,
                    "row_kind": row_kind,
                    "existing_source": updated_source_by_item.get(item_id, "(missing)"),
                    "incoming_source": payload["group_id"],
                }
            )
            replaced_by_item[item_id] = row
            updated_source_by_item[item_id] = payload["group_id"]

    replacement_rows = [replaced_by_item[item_id] for item_id in sorted(replaced_by_item)]
    return replacement_rows, missing_targets, replacements, updated_source_by_item


def count_use_sources(decision_rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in decision_rows:
        counts[str(row.get("use_source") or "(missing)")] += 1
    return counts


def count_runtime_paths(
    *,
    fact_rows: list[dict[str, Any]],
    decision_rows: list[dict[str, Any]],
) -> Counter[str]:
    fact_map = {str(row["item_id"]): row for row in fact_rows}
    counts: Counter[str] = Counter()

    for decision in decision_rows:
        item_id = str(decision["item_id"])
        fact_origin = fact_map.get(item_id, {}).get("fact_origin") or {}
        primary_use_sources = fact_origin.get("primary_use") or []
        primary_use_source = str(primary_use_sources[0]) if primary_use_sources else None

        if primary_use_source in CORE_PATH_KEYS:
            counts[primary_use_source] += 1
            continue

        counts[str(decision.get("use_source") or "(missing)")] += 1
    return counts


def build_projection_comparison(
    *,
    post_c_summary: dict[str, Any],
    fact_rows: list[dict[str, Any]],
    decision_rows: list[dict[str, Any]],
    rendered: dict[str, Any],
) -> dict[str, Any]:
    projected_runtime = post_c_summary["projected_runtime"]
    actual_path_counts = count_runtime_paths(fact_rows=fact_rows, decision_rows=decision_rows)
    rendered_stats = rendered.get("meta", {}).get("stats", {})
    actual_active = int(rendered_stats.get("active_composed", 0)) + int(
        rendered_stats.get("active_override", 0)
    )
    actual_silent = int(rendered_stats.get("silent", 0))
    actual_total = len(rendered.get("entries", {}))

    expected_path_counts = {
        key: int(projected_runtime["path_counts"].get(key, 0))
        for key in CORE_PATH_KEYS
    }
    actual_core_path_counts = {key: int(actual_path_counts.get(key, 0)) for key in CORE_PATH_KEYS}

    checks = {
        "runtime_row_count": {
            "expected": int(projected_runtime["projected_runtime_row_count"]),
            "actual": actual_total,
        },
        "active_count": {
            "expected": int(projected_runtime["projected_active_count"]),
            "actual": actual_active,
        },
        "silent_count": {
            "expected": int(projected_runtime["projected_silent_count"]),
            "actual": actual_silent,
        },
        "path_counts": {
            "expected": expected_path_counts,
            "actual": actual_core_path_counts,
        },
    }

    return {
        "checks": checks,
        "matches_projection": all(
            check["expected"] == check["actual"] for check in checks.values()
        ),
        "actual_path_counts": normalize_counter(actual_path_counts, keys=CORE_PATH_KEYS),
    }


def build_source_coverage_runtime() -> dict[str, Any]:
    INTEGRATED_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    historical_summary = load_json(HISTORICAL_SUMMARY_PATH)
    post_c_summary = load_json(POST_C_SUMMARY_PATH)
    package_payloads = [load_package_payload(spec) for spec in PACKAGE_SPECS]
    replacement_payloads = load_replacement_payloads()

    historical_facts_rows = load_jsonl(HISTORICAL_FACTS_PATH)
    historical_decisions_rows = load_jsonl(HISTORICAL_DECISIONS_PATH)

    merged_facts_rows, fact_duplicates, fact_sources = merge_rows_with_sources(
        historical_rows=historical_facts_rows,
        package_payloads=package_payloads,
        row_kind="facts",
    )
    merged_decision_rows, decision_duplicates, decision_sources = merge_rows_with_sources(
        historical_rows=historical_decisions_rows,
        package_payloads=package_payloads,
        row_kind="decisions",
    )

    duplicate_item_ids = fact_duplicates + decision_duplicates
    if duplicate_item_ids:
        raise ValueError(f"Duplicate item ids detected while merging: {duplicate_item_ids[:5]}")

    merged_facts_rows, fact_missing_replacements, fact_replacements, fact_sources = apply_replacement_rows(
        merged_rows=merged_facts_rows,
        source_by_item=fact_sources,
        replacement_payloads=replacement_payloads,
        row_kind="facts",
    )
    merged_decision_rows, decision_missing_replacements, decision_replacements, decision_sources = apply_replacement_rows(
        merged_rows=merged_decision_rows,
        source_by_item=decision_sources,
        replacement_payloads=replacement_payloads,
        row_kind="decisions",
    )

    replacement_missing_item_ids = fact_missing_replacements + decision_missing_replacements
    if replacement_missing_item_ids:
        raise ValueError(
            f"Replacement targets missing while merging: {replacement_missing_item_ids[:5]}"
        )

    if item_ids(merged_facts_rows) != item_ids(merged_decision_rows):
        raise ValueError("Merged facts and decisions do not cover the same item ids")

    dump_jsonl(INTEGRATED_FACTS_PATH, merged_facts_rows)
    dump_jsonl(INTEGRATED_DECISIONS_PATH, merged_decision_rows)

    rendered = build_rendered(
        INTEGRATED_FACTS_PATH,
        INTEGRATED_DECISIONS_PATH,
        DATA_DIR / "compose_profiles.json",
        INTEGRATED_RENDERED_PATH,
        style_log_path=INTEGRATED_RENDERED_PATH.with_suffix(".style_log.jsonl"),
        compose_context=STAGING_COMPOSE_CONTEXT,
    )

    if WORKSPACE_LAYER3_DATA_PATH.exists():
        copyfile(WORKSPACE_LAYER3_DATA_PATH, WORKSPACE_LAYER3_BACKUP_PATH)

    bridge_report = export_lua_bridge(
        rendered_path=INTEGRATED_RENDERED_PATH,
        lua_output_path=WORKSPACE_LAYER3_DATA_PATH,
        report_path=INTEGRATED_BRIDGE_REPORT_PATH,
    )
    runtime_report = build_phase_d_runtime_report(
        rendered_path=INTEGRATED_RENDERED_PATH,
        bridge_report_path=INTEGRATED_BRIDGE_REPORT_PATH,
        output_path=INTEGRATED_RUNTIME_REPORT_PATH,
    )

    projection_comparison = build_projection_comparison(
        post_c_summary=post_c_summary,
        fact_rows=merged_facts_rows,
        decision_rows=merged_decision_rows,
        rendered=rendered,
    )
    decision_use_source_counts = count_use_sources(merged_decision_rows)
    merged_runtime_path_counts = count_runtime_paths(
        fact_rows=merged_facts_rows,
        decision_rows=merged_decision_rows,
    )
    merged_state_counts = Counter(str(row.get("state") or "(missing)") for row in merged_decision_rows)

    summary = {
        "schema_version": "interaction-cluster-source-coverage-runtime-v0",
        "inputs": {
            "historical_runtime_summary": str(HISTORICAL_SUMMARY_PATH),
            "post_c_summary": str(POST_C_SUMMARY_PATH),
            "replacement_index": str(ROLE_FALLBACK_REPLACEMENT_INDEX_PATH),
        },
        "package_group_ids": [payload["group_id"] for payload in package_payloads],
        "package_count": len(package_payloads),
        "package_item_count": sum(payload["item_count"] for payload in package_payloads),
        "replacement_group_ids": [payload["group_id"] for payload in replacement_payloads],
        "replacement_package_count": len(replacement_payloads),
        "replacement_item_count": sum(payload["item_count"] for payload in replacement_payloads),
        "historical_runtime_row_count": int(historical_summary["rendered_entry_count"]),
        "merged_runtime_row_count": len(merged_facts_rows),
        "merged_state_counts": normalize_counter(merged_state_counts),
        "decision_use_source_counts": normalize_counter(decision_use_source_counts, keys=CORE_PATH_KEYS),
        "merged_runtime_path_counts": normalize_counter(merged_runtime_path_counts, keys=CORE_PATH_KEYS),
        "projection_comparison": projection_comparison,
        "bridge_runtime_entry_count": int(bridge_report["runtime_entry_count"]),
        "bridge_alias_count": len(bridge_report.get("applied_aliases", [])),
        "runtime_status": runtime_report["overall_status"],
        "duplicate_item_ids": duplicate_item_ids,
        "replacement_missing_item_ids": replacement_missing_item_ids,
        "replacement_applied_item_ids": sorted({row["item_id"] for row in fact_replacements}),
        "paths": {
            "facts": str(INTEGRATED_FACTS_PATH),
            "decisions": str(INTEGRATED_DECISIONS_PATH),
            "rendered": str(INTEGRATED_RENDERED_PATH),
            "bridge_report": str(INTEGRATED_BRIDGE_REPORT_PATH),
            "runtime_report": str(INTEGRATED_RUNTIME_REPORT_PATH),
            "workspace_layer3_data": str(WORKSPACE_LAYER3_DATA_PATH),
            "workspace_layer3_backup": (
                str(WORKSPACE_LAYER3_BACKUP_PATH) if WORKSPACE_LAYER3_BACKUP_PATH.exists() else None
            ),
        },
    }

    dump_json(INTEGRATED_SUMMARY_PATH, summary)
    INTEGRATED_NOTE_PATH.write_text(build_runtime_note(summary), encoding="utf-8")
    return summary


def build_runtime_note(summary: dict[str, Any]) -> str:
    comparison = summary["projection_comparison"]
    checks = comparison["checks"]
    lines = [
        "# Source-Coverage Runtime Note",
        "",
        f"- additive package count merged: `{summary['package_count']}`",
        f"- additive package item count merged: `{summary['package_item_count']}`",
        f"- replacement package count applied: `{summary['replacement_package_count']}`",
        f"- replacement item count applied: `{summary['replacement_item_count']}`",
        f"- historical runtime rows: `{summary['historical_runtime_row_count']}`",
        f"- merged runtime rows: `{summary['merged_runtime_row_count']}`",
        f"- runtime status: `{summary['runtime_status']}`",
        f"- projection match: `{str(comparison['matches_projection']).lower()}`",
        "",
        "## Projection comparison",
        "",
        f"- runtime rows: expected `{checks['runtime_row_count']['expected']}`, actual `{checks['runtime_row_count']['actual']}`",
        f"- active rows: expected `{checks['active_count']['expected']}`, actual `{checks['active_count']['actual']}`",
        f"- silent rows: expected `{checks['silent_count']['expected']}`, actual `{checks['silent_count']['actual']}`",
        "",
        "Path counts:",
        "",
    ]
    for key in CORE_PATH_KEYS:
        lines.append(
            f"- `{key}`: expected `{checks['path_counts']['expected'][key]}`, actual `{checks['path_counts']['actual'][key]}`"
        )
    lines.extend(
        [
            "",
            "## Runtime bridge",
            "",
            f"- workspace layer3 data: `{summary['paths']['workspace_layer3_data']}`",
            f"- bridge runtime entry count: `{summary['bridge_runtime_entry_count']}`",
            f"- bridge alias count: `{summary['bridge_alias_count']}`",
            "- manual in-game validation is still required even when the automated runtime report is ready.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    summary = build_source_coverage_runtime()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["runtime_status"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
