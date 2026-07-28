from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_post_cleanup_phase1_status_model_final import (
    COMBINATION_MATRIX_PATH as PHASE1_COMBINATION_MATRIX_PATH,
    DECISIONS_PATH as PHASE1_DECISIONS_PATH,
    build_post_cleanup_phase1_status_model_final,
)
from tools.build.report_weak_active_cleanup_w2_existing_cluster_absorption import (
    dump_json,
    load_json,
    load_jsonl,
)
from tools.build.report_weak_active_cleanup_w6_aggregate import (
    MATRIX_PATH as W6_MATRIX_PATH,
    POST_CLEANUP_FACTS_PATH as W6_POST_CLEANUP_FACTS_PATH,
)


OUTPUT_DIR = ROOT / "staging" / "post_cleanup_integrated_roadmap" / "phase2_runtime_adoption"
ADOPTION_SCOPE_MANIFEST_PATH = OUTPUT_DIR / "adoption_scope_manifest.json"


def semantic_value(raw_status: str) -> str:
    return str(raw_status).replace("semantic-", "")


def runtime_semantic_key(*, runtime_axis: str, semantic_axis: str) -> str:
    return f"{runtime_axis}::{semantic_axis}"


def load_candidate_fact_index(path: Path) -> dict[str, dict[str, Any]]:
    return {str(row["item_id"]): row for row in load_jsonl(path)}


def selected_decision_map(decisions: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row["decision_id"]): row for row in decisions["decisions"]}


def build_post_cleanup_phase2_adoption_scope(
    *,
    phase1_decisions_path: Path = PHASE1_DECISIONS_PATH,
    phase1_combination_matrix_path: Path = PHASE1_COMBINATION_MATRIX_PATH,
    w6_matrix_path: Path = W6_MATRIX_PATH,
    candidate_facts_path: Path = W6_POST_CLEANUP_FACTS_PATH,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    if not phase1_decisions_path.exists() or not phase1_combination_matrix_path.exists():
        build_post_cleanup_phase1_status_model_final()

    decisions = load_json(phase1_decisions_path)
    combination_matrix = load_json(phase1_combination_matrix_path)
    w6_rows = load_json(w6_matrix_path)["rows"]
    candidate_facts_by_id = load_candidate_fact_index(candidate_facts_path)
    decision_by_id = selected_decision_map(decisions)
    combination_by_key = {row["combination_key"]: row for row in combination_matrix["rows"]}

    adopt_in_phase2: list[str] = []
    keep_generated: list[str] = []
    keep_missing: list[str] = []
    demote_to_missing: list[str] = []
    pending_extra_gate: list[str] = []

    for row in sorted(w6_rows, key=lambda item: str(item["item_id"])):
        item_id = str(row["item_id"])
        combination_key = runtime_semantic_key(
            runtime_axis=str(row["runtime_axis_current"]),
            semantic_axis=semantic_value(str(row["semantic_status_after_cleanup"])),
        )

        if combination_key in {"generated::strong", "generated::adequate"}:
            keep_generated.append(item_id)
            continue

        if combination_key == "generated::weak":
            selected_option = decision_by_id["generated_weak_runtime_treatment"]["selected_option_id"]
            if selected_option in {"A", "B"}:
                keep_generated.append(item_id)
            else:
                demote_to_missing.append(item_id)
            continue

        if combination_key == "missing::strong":
            selected_option = decision_by_id["missing_strong_adopt_timing"]["selected_option_id"]
            if selected_option == "A":
                adopt_in_phase2.append(item_id)
            else:
                pending_extra_gate.append(item_id)
            continue

        if combination_key == "missing::adequate":
            selected_option = decision_by_id["missing_adequate_adopt_policy"]["selected_option_id"]
            candidate_primary_use = candidate_facts_by_id.get(item_id, {}).get("primary_use")
            if selected_option == "A" and isinstance(candidate_primary_use, str) and candidate_primary_use.strip():
                adopt_in_phase2.append(item_id)
            else:
                keep_missing.append(item_id)
            continue

        if combination_key == "missing::weak":
            keep_missing.append(item_id)
            continue

        raise ValueError(f"Unsupported combination for adoption scope: {combination_key}")

    manifest = {
        "schema_version": "post-cleanup-phase2-adoption-scope-v1",
        "phase1_decisions_ref": str(phase1_decisions_path),
        "phase1_combination_matrix_ref": str(phase1_combination_matrix_path),
        "candidate_facts_ref": str(candidate_facts_path),
        "decision_selections": {
            decision_id: row["selected_label"] for decision_id, row in decision_by_id.items()
        },
        "counts": {
            "adopt_in_phase2": len(adopt_in_phase2),
            "keep_generated": len(keep_generated),
            "keep_missing": len(keep_missing),
            "demote_to_missing": len(demote_to_missing),
            "pending_extra_gate": len(pending_extra_gate),
        },
        "combination_actions": {
            key: {
                "phase2_scope_action": row["phase2_scope_action"],
                "final_runtime_treatment": row["final_runtime_treatment"],
            }
            for key, row in combination_by_key.items()
        },
        "backlog_priority": {
            "generated::weak": combination_by_key["generated::weak"]["phase3_backlog_priority"],
            "missing::weak": combination_by_key["missing::weak"]["phase3_backlog_priority"],
        },
        "buckets": {
            "adopt_in_phase2": adopt_in_phase2,
            "keep_generated": keep_generated,
            "keep_missing": keep_missing,
            "demote_to_missing": demote_to_missing,
            "pending_extra_gate": pending_extra_gate,
        },
        "gates": [
            "missing::strong rows enter Phase 2 validation before adoption rebuild",
            "missing::adequate rows remain missing unless an identity-level runtime-consumable body exists",
            "generated::weak rows remain runtime-consumed in this round",
            "missing::weak rows remain missing and stay lower priority than generated::weak backlog work",
        ],
    }
    dump_json(output_dir / ADOPTION_SCOPE_MANIFEST_PATH.name, manifest)
    return manifest


def main() -> int:
    manifest = build_post_cleanup_phase2_adoption_scope()
    print("post-cleanup Phase 2 adoption scope generated")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
