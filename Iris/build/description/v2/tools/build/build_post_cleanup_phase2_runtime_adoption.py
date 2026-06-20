from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.build_interaction_cluster_source_coverage_runtime import (
    CORE_PATH_KEYS,
    count_runtime_paths,
    count_use_sources,
    normalize_counter,
)
from tools.build.compose_layer3_text import STAGING_COMPOSE_CONTEXT, build_rendered
from tools.build.export_dvf_3_3_lua_bridge import export_lua_bridge
from tools.build.report_post_cleanup_phase2_adoption_scope import (
    ADOPTION_SCOPE_MANIFEST_PATH as PHASE2_ADOPTION_SCOPE_MANIFEST_PATH,
    build_post_cleanup_phase2_adoption_scope,
)
from tools.build.report_weak_active_cleanup_w2_existing_cluster_absorption import (
    dump_json,
    dump_jsonl,
    dump_text,
    load_json,
    load_jsonl,
)
from tools.build.report_weak_active_cleanup_w6_aggregate import (
    MATRIX_PATH as W6_MATRIX_PATH,
    POST_CLEANUP_FACTS_PATH as W6_POST_CLEANUP_FACTS_PATH,
)
from tools.build.validate_interaction_cluster_phase_d_runtime import (
    build_phase_d_runtime_report,
)


DATA_DIR = ROOT / "data"
SOURCE_RUNTIME_DIR = ROOT / "staging" / "interaction_cluster" / "source_coverage_runtime"
BASE_FACTS_PATH = SOURCE_RUNTIME_DIR / "dvf_3_3_facts.integrated.jsonl"
BASE_DECISIONS_PATH = SOURCE_RUNTIME_DIR / "dvf_3_3_decisions.integrated.jsonl"
BASE_RUNTIME_SUMMARY_PATH = SOURCE_RUNTIME_DIR / "source_coverage_runtime_summary.json"

OUTPUT_DIR = ROOT / "staging" / "post_cleanup_integrated_roadmap" / "phase2_runtime_adoption"
ADOPTED_FACTS_PATH = OUTPUT_DIR / "dvf_3_3_facts.adopted.jsonl"
ADOPTED_DECISIONS_PATH = OUTPUT_DIR / "dvf_3_3_decisions.adopted.jsonl"
ADOPTED_RENDERED_PATH = OUTPUT_DIR / "dvf_3_3_rendered.adopted.json"
ADOPTED_LUA_PATH = OUTPUT_DIR / "IrisLayer3Data.lua"
BRIDGE_REPORT_PATH = OUTPUT_DIR / "phase2_lua_bridge_report.json"
RUNTIME_REPORT_PATH = OUTPUT_DIR / "phase2_runtime_report.json"
RUNTIME_SUMMARY_PATH = OUTPUT_DIR / "adoption_runtime_summary.json"
DIFF_REPORT_PATH = OUTPUT_DIR / "adoption_diff_report.json"
CHECKLIST_PATH = OUTPUT_DIR / "in_game_validation_checklist.md"

ROLE_TO_COMPOSE_PROFILE = {
    "tool": "interaction_tool",
    "output": "interaction_output",
    "material": "interaction_component",
    "component": "interaction_component",
}


def cluster_defaults(decision_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    defaults: dict[str, dict[str, Any]] = {}
    for row in decision_rows:
        cluster = row.get("selected_cluster")
        if not cluster or cluster in defaults:
            continue
        defaults[str(cluster)] = {
            "selected_role": row.get("selected_role"),
            "compose_profile": row.get("compose_profile"),
        }
    return defaults


def matrix_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["item_id"]): row for row in rows}


def facts_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["item_id"]): row for row in rows}


def infer_cluster_and_role(
    *,
    item_id: str,
    candidate_fact: dict[str, Any],
    matrix_row: dict[str, Any] | None,
    cluster_default_map: dict[str, dict[str, Any]],
) -> tuple[str, str, str]:
    weak_cleanup_meta = candidate_fact.get("slot_meta", {}).get("weak_cleanup_w6", {})
    proposed_cluster = weak_cleanup_meta.get("proposed_cluster") or (matrix_row or {}).get("proposed_cluster")
    if not proposed_cluster:
        raise ValueError(f"Missing proposed cluster for adopted item {item_id}")

    defaults = cluster_default_map.get(str(proposed_cluster), {})
    selected_role = weak_cleanup_meta.get("proposed_role") or defaults.get("selected_role")
    if not selected_role:
        raise ValueError(f"Missing selected role for adopted item {item_id} / cluster {proposed_cluster}")

    compose_profile = defaults.get("compose_profile") or ROLE_TO_COMPOSE_PROFILE.get(str(selected_role))
    if not compose_profile:
        raise ValueError(
            f"Missing compose profile for adopted item {item_id} / role {selected_role} / cluster {proposed_cluster}"
        )

    return str(proposed_cluster), str(selected_role), str(compose_profile)


def overlay_adopted_rows(
    *,
    base_facts_rows: list[dict[str, Any]],
    base_decision_rows: list[dict[str, Any]],
    candidate_facts_rows: list[dict[str, Any]],
    adoption_scope_manifest: dict[str, Any],
    w6_matrix_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    adopt_ids = set(str(item_id) for item_id in adoption_scope_manifest["buckets"]["adopt_in_phase2"])
    keep_generated_ids = set(str(item_id) for item_id in adoption_scope_manifest["buckets"]["keep_generated"])
    keep_missing_ids = set(str(item_id) for item_id in adoption_scope_manifest["buckets"]["keep_missing"])

    base_facts_by_id = facts_index(base_facts_rows)
    base_decisions_by_id = facts_index(base_decision_rows)
    candidate_facts_by_id = facts_index(candidate_facts_rows)
    w6_matrix_by_id = matrix_index(w6_matrix_rows)
    cluster_default_map = cluster_defaults(base_decision_rows)

    adopted_facts_rows: list[dict[str, Any]] = []
    adopted_decision_rows: list[dict[str, Any]] = []
    adopted_ids_seen: list[str] = []

    for item_id in sorted(base_facts_by_id):
        fact_row = dict(base_facts_by_id[item_id])
        decision_row = dict(base_decisions_by_id[item_id])

        if item_id in adopt_ids:
            candidate_fact = dict(candidate_facts_by_id[item_id])
            proposed_cluster, selected_role, compose_profile = infer_cluster_and_role(
                item_id=item_id,
                candidate_fact=candidate_fact,
                matrix_row=w6_matrix_by_id.get(item_id),
                cluster_default_map=cluster_default_map,
            )

            fact_row = candidate_fact
            decision_row.update(
                {
                    "state": "active",
                    "reason_code": "POST_CLEANUP_ADOPTED",
                    "compose_profile": compose_profile,
                    "facts_ref": item_id,
                    "merge_case": "phase2_adoption_overlay",
                    "use_source": "cluster_summary",
                    "selected_cluster": proposed_cluster,
                    "selected_role": selected_role,
                    "selection_path": "phase2_adoption",
                    "cluster_used": True,
                    "cluster_policy_status": None,
                    "policy_excluded_reason_codes": [],
                    "hard_fail_codes": [],
                    "v9_warn": False,
                }
            )
            adopted_ids_seen.append(item_id)

        adopted_facts_rows.append(fact_row)
        adopted_decision_rows.append(decision_row)

    metadata = {
        "adopt_in_phase2_ids": sorted(adopt_ids),
        "keep_generated_ids": sorted(keep_generated_ids),
        "keep_missing_ids": sorted(keep_missing_ids),
        "adopted_ids_seen": adopted_ids_seen,
    }
    return adopted_facts_rows, adopted_decision_rows, metadata


def build_runtime_summary(
    *,
    facts_rows: list[dict[str, Any]],
    decision_rows: list[dict[str, Any]],
    rendered: dict[str, Any],
    adoption_scope_manifest: dict[str, Any],
    base_runtime_summary: dict[str, Any],
) -> dict[str, Any]:
    state_counts = Counter(str(row.get("state") or "(missing)") for row in decision_rows)
    path_counts = count_runtime_paths(fact_rows=facts_rows, decision_rows=decision_rows)
    decision_use_source_counts = count_use_sources(decision_rows)
    rendered_stats = rendered.get("meta", {}).get("stats", {})
    return {
        "schema_version": "post-cleanup-phase2-runtime-summary-v1",
        "base_runtime_summary_ref": str(BASE_RUNTIME_SUMMARY_PATH),
        "adoption_scope_ref": str(PHASE2_ADOPTION_SCOPE_MANIFEST_PATH),
        "row_count": len(facts_rows),
        "state_counts": normalize_counter(state_counts),
        "runtime_path_counts": normalize_counter(path_counts, keys=CORE_PATH_KEYS),
        "decision_use_source_counts": normalize_counter(decision_use_source_counts, keys=CORE_PATH_KEYS),
        "rendered_stats": rendered_stats,
        "adoption_counts": adoption_scope_manifest["counts"],
        "base_state_counts": base_runtime_summary["merged_state_counts"],
        "base_runtime_path_counts": base_runtime_summary["merged_runtime_path_counts"],
        "base_decision_use_source_counts": base_runtime_summary["decision_use_source_counts"],
    }


def build_diff_report(
    *,
    runtime_summary: dict[str, Any],
    base_runtime_summary: dict[str, Any],
    adoption_scope_manifest: dict[str, Any],
) -> dict[str, Any]:
    state_delta = {
        key: int(runtime_summary["state_counts"].get(key, 0))
        - int(base_runtime_summary["merged_state_counts"].get(key, 0))
        for key in sorted(
            set(runtime_summary["state_counts"]) | set(base_runtime_summary["merged_state_counts"])
        )
    }
    path_delta = {
        key: int(runtime_summary["runtime_path_counts"].get(key, 0))
        - int(base_runtime_summary["merged_runtime_path_counts"].get(key, 0))
        for key in CORE_PATH_KEYS
    }
    decision_use_source_delta = {
        key: int(runtime_summary["decision_use_source_counts"].get(key, 0))
        - int(base_runtime_summary["decision_use_source_counts"].get(key, 0))
        for key in CORE_PATH_KEYS
    }
    return {
        "schema_version": "post-cleanup-phase2-adoption-diff-v1",
        "base_runtime_summary_ref": str(BASE_RUNTIME_SUMMARY_PATH),
        "adoption_scope_ref": str(PHASE2_ADOPTION_SCOPE_MANIFEST_PATH),
        "state_delta": state_delta,
        "runtime_path_delta": path_delta,
        "decision_use_source_delta": decision_use_source_delta,
        "adopt_in_phase2_ids": adoption_scope_manifest["buckets"]["adopt_in_phase2"],
        "keep_missing_ids": adoption_scope_manifest["buckets"]["keep_missing"],
        "keep_generated_ids_sample": adoption_scope_manifest["buckets"]["keep_generated"][:20],
    }


def write_checklist(path: Path = CHECKLIST_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Phase 2 In-Game Validation Checklist",
                "",
                "1. Load the Phase 2 adopted runtime artifacts.",
                "2. Confirm one newly adopted item now shows 3-3 text in runtime:",
                "   - Base.WaterBottleFull",
                "   - Base.GlassTumbler",
                "   - Radio.RadioMag1",
                "3. Confirm a kept-missing adequate row still does not render:",
                "   - Base.Gloves_Surgical",
                "   - Base.Underwear1",
                "4. Confirm a kept-generated weak row still renders and was not demoted:",
                "   - Base.Bleach",
                "   - Base.BadmintonRacket",
                "5. Confirm no semantic quality indicator is shown in UI for this round.",
                "6. Confirm existing strong rows still render normally.",
                "",
                "Manual in-game validation is still required before treating the staged Phase 2 runtime as officially adopted.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def build_post_cleanup_phase2_runtime_adoption(
    *,
    adoption_scope_manifest_path: Path = PHASE2_ADOPTION_SCOPE_MANIFEST_PATH,
    base_facts_path: Path = BASE_FACTS_PATH,
    base_decisions_path: Path = BASE_DECISIONS_PATH,
    base_runtime_summary_path: Path = BASE_RUNTIME_SUMMARY_PATH,
    candidate_facts_path: Path = W6_POST_CLEANUP_FACTS_PATH,
    w6_matrix_path: Path = W6_MATRIX_PATH,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    if not adoption_scope_manifest_path.exists():
        build_post_cleanup_phase2_adoption_scope()

    adoption_scope_manifest = load_json(adoption_scope_manifest_path)
    base_facts_rows = load_jsonl(base_facts_path)
    base_decision_rows = load_jsonl(base_decisions_path)
    candidate_facts_rows = load_jsonl(candidate_facts_path)
    w6_matrix_rows = load_json(w6_matrix_path)["rows"]
    base_runtime_summary = load_json(base_runtime_summary_path)

    adopted_facts_rows, adopted_decision_rows, metadata = overlay_adopted_rows(
        base_facts_rows=base_facts_rows,
        base_decision_rows=base_decision_rows,
        candidate_facts_rows=candidate_facts_rows,
        adoption_scope_manifest=adoption_scope_manifest,
        w6_matrix_rows=w6_matrix_rows,
    )

    dump_jsonl(output_dir / ADOPTED_FACTS_PATH.name, adopted_facts_rows)
    dump_jsonl(output_dir / ADOPTED_DECISIONS_PATH.name, adopted_decision_rows)
    rendered = build_rendered(
        output_dir / ADOPTED_FACTS_PATH.name,
        output_dir / ADOPTED_DECISIONS_PATH.name,
        DATA_DIR / "compose_profiles.json",
        output_dir / ADOPTED_RENDERED_PATH.name,
        style_log_path=output_dir / (ADOPTED_RENDERED_PATH.stem + ".style_log.jsonl"),
        compose_context=STAGING_COMPOSE_CONTEXT,
    )
    bridge_report = export_lua_bridge(
        rendered_path=output_dir / ADOPTED_RENDERED_PATH.name,
        lua_output_path=output_dir / ADOPTED_LUA_PATH.name,
        report_path=output_dir / BRIDGE_REPORT_PATH.name,
        chunk_output_dir=output_dir / "IrisLayer3DataChunks",
        chunk_manifest_path=output_dir / "IrisLayer3DataChunks.lua",
    )
    runtime_report = build_phase_d_runtime_report(
        rendered_path=output_dir / ADOPTED_RENDERED_PATH.name,
        bridge_report_path=output_dir / BRIDGE_REPORT_PATH.name,
        layer3_data_path=output_dir / ADOPTED_LUA_PATH.name,
        output_path=output_dir / RUNTIME_REPORT_PATH.name,
    )

    runtime_summary = build_runtime_summary(
        facts_rows=adopted_facts_rows,
        decision_rows=adopted_decision_rows,
        rendered=rendered,
        adoption_scope_manifest=adoption_scope_manifest,
        base_runtime_summary=base_runtime_summary,
    )
    diff_report = build_diff_report(
        runtime_summary=runtime_summary,
        base_runtime_summary=base_runtime_summary,
        adoption_scope_manifest=adoption_scope_manifest,
    )
    dump_json(output_dir / RUNTIME_SUMMARY_PATH.name, runtime_summary)
    dump_json(output_dir / DIFF_REPORT_PATH.name, diff_report)
    checklist_path = write_checklist(output_dir / CHECKLIST_PATH.name)

    return {
        "schema_version": "post-cleanup-phase2-runtime-adoption-v1",
        "decision_status": adoption_scope_manifest["decision_selections"],
        "adopted_row_count": len(metadata["adopted_ids_seen"]),
        "runtime_summary_path": str(output_dir / RUNTIME_SUMMARY_PATH.name),
        "diff_report_path": str(output_dir / DIFF_REPORT_PATH.name),
        "bridge_report_path": str(output_dir / BRIDGE_REPORT_PATH.name),
        "runtime_report_path": str(output_dir / RUNTIME_REPORT_PATH.name),
        "checklist_path": str(checklist_path),
        "adopted_ids_seen": metadata["adopted_ids_seen"],
    }


def main() -> int:
    summary = build_post_cleanup_phase2_runtime_adoption()
    print("post-cleanup Phase 2 runtime adoption built")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
