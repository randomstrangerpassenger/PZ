from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_weak_active_cleanup_w2_existing_cluster_absorption import (
    INTEGRATED_FACTS_PATH,
    W0_CANDIDATE_LIST_PATH,
    cluster_catalog_from_package,
    dump_json,
    dump_jsonl,
    load_json,
    load_jsonl,
    normalize_counter,
)
from tools.build.report_weak_active_cleanup_w1_consumable_reverse_mapping import (
    MAPPING_PATH as W1_MAPPING_PATH,
    PROMOTED_FACTS_PATH as W1_PROMOTED_FACTS_PATH,
)
from tools.build.report_weak_active_cleanup_w2_existing_cluster_absorption import (
    MAPPING_PATH as W2_MAPPING_PATH,
    PROMOTED_FACTS_PATH as W2_PROMOTED_FACTS_PATH,
)
from tools.build.report_weak_active_cleanup_w3_unknown_classification import (
    MAPPING_PATH as W3_MAPPING_PATH,
    PROMOTED_FACTS_PATH as W3_PROMOTED_FACTS_PATH,
)
from tools.build.report_weak_active_cleanup_w4_wearable_structural_decision import (
    MAPPING_PATH as W4_MAPPING_PATH,
    PROMOTED_FACTS_PATH as W4_PROMOTED_FACTS_PATH,
)
from tools.build.report_weak_active_cleanup_w5_role_fallback_cleanup import (
    MAPPING_PATH as W5_MAPPING_PATH,
    PROMOTED_FACTS_PATH as W5_PROMOTED_FACTS_PATH,
)


SOURCE_COVERAGE_DIR = ROOT / "staging" / "source_coverage" / "block_c"
B1_DIR = SOURCE_COVERAGE_DIR / "b1_consumable_package"
C1B_DIR = SOURCE_COVERAGE_DIR / "c1b_portable_storage_package"
C1RE_DIR = SOURCE_COVERAGE_DIR / "c1re_utility_misc_package"

OUTPUT_DIR = ROOT / "staging" / "weak_active_cleanup" / "w6_aggregate"
MATRIX_PATH = OUTPUT_DIR / "weak_active_disposition_matrix.json"
STATUS_MODEL_PATH = OUTPUT_DIR / "status_model_input_from_weak_cleanup.json"
BACKLOG_PATH = OUTPUT_DIR / "weak_cleanup_to_source_backlog_map.json"
FULL_CLASSIFICATION_PATH = OUTPUT_DIR / "full_runtime_fourway_classification.json"
POST_CLEANUP_FACTS_PATH = OUTPUT_DIR / "integrated_facts.post_cleanup_candidate.jsonl"
SUMMARY_PATH = OUTPUT_DIR / "weak_cleanup_aggregate_summary.json"

WATER_BEVERAGE_ITEMS = {
    "Base.BeerWaterFull",
    "Base.GlassTumblerWater",
    "Base.PlasticCupWater",
    "Base.WaterBottleFull",
    "Base.WaterPopBottle",
    "Base.WaterMug",
    "Base.WaterMugRed",
    "Base.WaterMugSpiffo",
    "Base.WaterMugWhite",
    "Base.WaterTeacup",
    "Base.GlassWineWater",
    "Base.WhiskeyWaterFull",
    "Base.WineWaterFull",
    "farming.MayonnaiseWaterFull",
    "farming.RemouladeWaterFull",
}

W6_WEARABLE_ADEQUATE_ASSIGNMENTS = {
    "Base.Underwear1": "Wearable.6-C",
    "Base.Underwear2": "Wearable.6-C",
    "Base.Locket": "Wearable.6-G",
    "Base.WeldingMask": "Wearable.6-A",
}


def load_phase_rows(path: Path) -> list[dict[str, Any]]:
    return list(load_json(path)["rows"])


def load_phase_promoted_rows(path: Path) -> list[dict[str, Any]]:
    return load_jsonl(path)


def build_promoted_candidate_facts_from_mapping_rows(
    *,
    mapping_rows: list[dict[str, Any]],
    integrated_facts: list[dict[str, Any]],
    cleanup_phase: str,
) -> list[dict[str, Any]]:
    facts_by_id = {str(row["item_id"]): row for row in integrated_facts}
    promoted_rows: list[dict[str, Any]] = []

    for mapping in mapping_rows:
        if mapping.get("disposition") != "promote_candidate":
            continue
        item_id = str(mapping["item_id"])
        fact = dict(facts_by_id[item_id])
        fact["primary_use"] = mapping["proposed_primary_use"]

        fact_origin = dict(fact.get("fact_origin") or {})
        fact_origin["primary_use"] = ["cluster_summary"]
        fact["fact_origin"] = fact_origin

        slot_meta = dict(fact.get("slot_meta") or {})
        slot_meta["weak_cleanup_w6"] = {
            "cleanup_phase": cleanup_phase,
            "proposed_cluster": mapping["proposed_cluster"],
            "proposed_role": mapping.get("proposed_role"),
            "source_package": mapping["source_package"],
            "candidate_family": mapping.get("candidate_family"),
        }
        fact["slot_meta"] = slot_meta
        promoted_rows.append(fact)

    promoted_rows.sort(key=lambda row: str(row["item_id"]))
    return promoted_rows


def runtime_axis_from_candidate_family(candidate_family: str) -> str:
    return "missing" if candidate_family == "role_fallback_silent" else "generated"


def semantic_status_from_row(row: dict[str, Any]) -> str:
    disposition = str(row.get("disposition") or "")
    weak_type = str(row.get("weak_type") or "")
    if disposition == "promote_candidate":
        return "semantic-strong"
    if disposition == "retain_identity_fallback" and weak_type == "W2":
        return "semantic-adequate"
    if disposition == "silent_keep":
        return "silent"
    if disposition == "active_transition_candidate":
        return "semantic-weak"
    if disposition == "source_backlog_candidate":
        return "semantic-weak"
    return "semantic-weak"


def build_transition_promotion_row(
    *,
    phase_row: dict[str, Any],
    assigned_primary_classification: str | None,
    source_package: str,
    cluster_id: str,
    cluster_info: dict[str, Any],
    rationale: str,
) -> dict[str, Any]:
    finalized = dict(phase_row)
    finalized.update(
        {
            "disposition": "promote_candidate",
            "next_phase": None,
            "weak_type": None,
            "assigned_primary_classification": assigned_primary_classification,
            "proposed_cluster": cluster_id,
            "source_package": source_package,
            "source_path_after_mapping": "cluster_summary",
            "proposed_primary_use": cluster_info["canonical_primary_use"],
            "proposed_role": cluster_info["canonical_role"],
            "rationale": rationale,
        }
    )
    return finalized


def finalize_w5_transition_row(
    *,
    candidate_row: dict[str, Any],
    phase_row: dict[str, Any],
    catalogs_by_package: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    if str(phase_row.get("disposition") or "") != "active_transition_candidate":
        return dict(phase_row)

    item_id = str(phase_row["item_id"])
    assigned_primary_classification = str(
        phase_row.get("assigned_primary_classification")
        or candidate_row.get("primary_classification")
        or W6_WEARABLE_ADEQUATE_ASSIGNMENTS.get(item_id)
        or ""
    )

    if item_id in WATER_BEVERAGE_ITEMS:
        cluster_info = catalogs_by_package.get("B-1", {}).get("beverage_consumption")
        if cluster_info is not None:
            return build_transition_promotion_row(
                phase_row=phase_row,
                assigned_primary_classification=assigned_primary_classification or None,
                source_package="B-1",
                cluster_id="beverage_consumption",
                cluster_info=cluster_info,
                rationale="W-6 confirmed that this water row can reuse the existing beverage-consumption cluster rather than staying in transition review.",
            )

    if item_id == "Base.BucketEmpty":
        cluster_info = catalogs_by_package.get("C1-B", {}).get("container_storage")
        if cluster_info is not None:
            return build_transition_promotion_row(
                phase_row=phase_row,
                assigned_primary_classification=assigned_primary_classification or None,
                source_package="C1-B",
                cluster_id="container_storage",
                cluster_info=cluster_info,
                rationale="W-6 confirmed that the empty bucket fits the existing container-storage cluster as a portable contents carrier.",
            )

    if item_id in {"Base.GlassTumbler", "Base.GlassWine"}:
        cluster_info = catalogs_by_package.get("C1-Re", {}).get("kitchen_table_handling")
        if cluster_info is not None:
            return build_transition_promotion_row(
                phase_row=phase_row,
                assigned_primary_classification=assigned_primary_classification or None,
                source_package="C1-Re",
                cluster_id="kitchen_table_handling",
                cluster_info=cluster_info,
                rationale="W-6 confirmed that this empty glass is better explained by the existing kitchen-table-handling cluster than by a silent slot.",
            )

    if assigned_primary_classification.startswith("Wearable."):
        finalized = dict(phase_row)
        finalized.update(
            {
                "disposition": "retain_identity_fallback",
                "next_phase": None,
                "weak_type": "W2",
                "assigned_primary_classification": assigned_primary_classification,
                "proposed_cluster": None,
                "source_package": None,
                "source_path_after_mapping": "identity_fallback",
                "proposed_primary_use": None,
                "proposed_role": None,
                "rationale": "W-6 applies the wearable structural decision: this row is better treated as semantic-adequate identity retention than as a forced active rewrite.",
            }
        )
        return finalized

    finalized = dict(phase_row)
    finalized.update(
        {
            "disposition": "source_backlog_candidate",
            "next_phase": None,
            "weak_type": "W3",
            "assigned_primary_classification": assigned_primary_classification or None,
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": None,
            "proposed_primary_use": None,
            "proposed_role": None,
            "rationale": "W-6 confirmed that this row has item-level meaning, but no safe staged cluster-summary reverse mapping yet; it stays on source backlog rather than forced activation.",
        }
    )
    return finalized


def build_matrix_row(
    *,
    candidate_row: dict[str, Any],
    phase_row: dict[str, Any],
    phase_name: str,
) -> dict[str, Any]:
    candidate_family = str(candidate_row.get("candidate_family") or "")
    runtime_axis = runtime_axis_from_candidate_family(candidate_family)
    semantic_status = semantic_status_from_row(phase_row)
    primary_classification = phase_row.get("assigned_primary_classification")
    if primary_classification is None:
        primary_classification = candidate_row.get("primary_classification")
    return {
        "item_id": candidate_row["item_id"],
        "display_name": candidate_row.get("display_name"),
        "candidate_family": candidate_family,
        "runtime_axis_current": runtime_axis,
        "runtime_state_current": candidate_row.get("runtime_state"),
        "provenance_path_current": candidate_row.get("provenance_path"),
        "primary_classification": primary_classification,
        "cleanup_phase": phase_name,
        "final_disposition": phase_row.get("disposition"),
        "weak_type": phase_row.get("weak_type"),
        "semantic_status_after_cleanup": semantic_status,
        "proposed_cluster": phase_row.get("proposed_cluster"),
        "source_package": phase_row.get("source_package"),
        "next_phase": phase_row.get("next_phase"),
        "rationale": phase_row.get("rationale"),
    }


def build_status_model_row(matrix_row: dict[str, Any]) -> dict[str, Any]:
    semantic = str(matrix_row["semantic_status_after_cleanup"]).replace("semantic-", "")
    return {
        "item_id": matrix_row["item_id"],
        "runtime_axis": matrix_row["runtime_axis_current"],
        "semantic_axis": semantic,
        "cleanup_phase": matrix_row["cleanup_phase"],
        "final_disposition": matrix_row["final_disposition"],
        "weak_type": matrix_row["weak_type"],
    }


def build_full_runtime_classification(
    *,
    integrated_facts: list[dict[str, Any]],
    matrix_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in integrated_facts:
        item_id = str(fact["item_id"])
        matrix_row = matrix_by_id.get(item_id)
        if matrix_row is None:
            rows.append(
                {
                    "item_id": item_id,
                    "semantic_status_after_cleanup": "semantic-strong",
                    "runtime_axis_current": "generated",
                }
            )
            continue
        rows.append(
            {
                "item_id": item_id,
                "semantic_status_after_cleanup": matrix_row["semantic_status_after_cleanup"],
                "runtime_axis_current": matrix_row["runtime_axis_current"],
            }
        )
    return rows


def build_post_cleanup_candidate_facts(
    *,
    integrated_facts: list[dict[str, Any]],
    promoted_rows_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in integrated_facts:
        item_id = str(fact["item_id"])
        rows.append(dict(promoted_rows_by_id.get(item_id) or fact))
    return rows


def build_w6_aggregate(
    *,
    w0_candidate_list_path: Path = W0_CANDIDATE_LIST_PATH,
    integrated_facts_path: Path = INTEGRATED_FACTS_PATH,
    w1_mapping_path: Path = W1_MAPPING_PATH,
    w1_promoted_path: Path = W1_PROMOTED_FACTS_PATH,
    w2_mapping_path: Path = W2_MAPPING_PATH,
    w2_promoted_path: Path = W2_PROMOTED_FACTS_PATH,
    w3_mapping_path: Path = W3_MAPPING_PATH,
    w3_promoted_path: Path = W3_PROMOTED_FACTS_PATH,
    w4_mapping_path: Path = W4_MAPPING_PATH,
    w4_promoted_path: Path = W4_PROMOTED_FACTS_PATH,
    w5_mapping_path: Path = W5_MAPPING_PATH,
    w5_promoted_path: Path = W5_PROMOTED_FACTS_PATH,
    b1_facts_path: Path = B1_DIR / "b1_consumable_facts.jsonl",
    b1_decisions_path: Path = B1_DIR / "b1_consumable_decisions.jsonl",
    c1b_facts_path: Path = C1B_DIR / "c1b_portable_storage_facts.jsonl",
    c1b_decisions_path: Path = C1B_DIR / "c1b_portable_storage_decisions.jsonl",
    c1re_facts_path: Path = C1RE_DIR / "c1re_utility_misc_facts.jsonl",
    c1re_decisions_path: Path = C1RE_DIR / "c1re_utility_misc_decisions.jsonl",
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    candidate_rows = {row["item_id"]: row for row in load_json(w0_candidate_list_path)["rows"]}
    integrated_facts = load_jsonl(integrated_facts_path)

    w1_rows = {row["item_id"]: row for row in load_phase_rows(w1_mapping_path)}
    w2_rows = {row["item_id"]: row for row in load_phase_rows(w2_mapping_path)}
    w3_rows_all = load_phase_rows(w3_mapping_path)
    w3_rows = {
        row["item_id"]: row for row in w3_rows_all if str(row.get("disposition") or "") != "defer_to_w4"
    }
    w4_rows = {row["item_id"]: row for row in load_phase_rows(w4_mapping_path)}
    catalogs_by_package = {
        "B-1": cluster_catalog_from_package(
            facts_path=b1_facts_path,
            decisions_path=b1_decisions_path,
            package_id="B-1",
        ),
        "C1-B": cluster_catalog_from_package(
            facts_path=c1b_facts_path,
            decisions_path=c1b_decisions_path,
            package_id="C1-B",
        ),
        "C1-Re": cluster_catalog_from_package(
            facts_path=c1re_facts_path,
            decisions_path=c1re_decisions_path,
            package_id="C1-Re",
        ),
    }
    raw_w5_rows = load_phase_rows(w5_mapping_path)
    finalized_w5_transition_rows: list[dict[str, Any]] = []
    w5_rows: dict[str, dict[str, Any]] = {}
    for row in raw_w5_rows:
        item_id = str(row["item_id"])
        finalized_row = finalize_w5_transition_row(
            candidate_row=candidate_rows[item_id],
            phase_row=row,
            catalogs_by_package=catalogs_by_package,
        )
        w5_rows[item_id] = finalized_row
        if str(row.get("disposition") or "") == "active_transition_candidate":
            finalized_w5_transition_rows.append(finalized_row)

    final_phase_lookup: dict[str, tuple[str, dict[str, Any]]] = {}
    for phase_name, rows in (
        ("W-1", w1_rows),
        ("W-2", w2_rows),
        ("W-3", w3_rows),
        ("W-4", w4_rows),
        ("W-5", w5_rows),
    ):
        for item_id, row in rows.items():
            final_phase_lookup[item_id] = (phase_name, row)

    matrix_rows = [
        build_matrix_row(
            candidate_row=candidate_rows[item_id],
            phase_row=phase_row,
            phase_name=phase_name,
        )
        for item_id, (phase_name, phase_row) in final_phase_lookup.items()
    ]
    matrix_rows.sort(key=lambda row: row["item_id"])
    matrix_by_id = {row["item_id"]: row for row in matrix_rows}

    status_model_rows = [build_status_model_row(row) for row in matrix_rows]
    status_model_rows.sort(key=lambda row: row["item_id"])

    backlog_rows = [
        row for row in matrix_rows if row["semantic_status_after_cleanup"] == "semantic-weak"
    ]
    backlog_rows.sort(key=lambda row: row["item_id"])

    full_runtime_rows = build_full_runtime_classification(
        integrated_facts=integrated_facts,
        matrix_by_id=matrix_by_id,
    )
    full_runtime_rows.sort(key=lambda row: row["item_id"])

    promoted_rows_by_id: dict[str, dict[str, Any]] = {}
    for promoted_path in (
        w1_promoted_path,
        w2_promoted_path,
        w3_promoted_path,
        w4_promoted_path,
        w5_promoted_path,
    ):
        for row in load_phase_promoted_rows(promoted_path):
            promoted_rows_by_id[str(row["item_id"])] = row
    for row in build_promoted_candidate_facts_from_mapping_rows(
        mapping_rows=finalized_w5_transition_rows,
        integrated_facts=integrated_facts,
        cleanup_phase="W-6",
    ):
        promoted_rows_by_id[str(row["item_id"])] = row

    post_cleanup_candidate_facts = build_post_cleanup_candidate_facts(
        integrated_facts=integrated_facts,
        promoted_rows_by_id=promoted_rows_by_id,
    )

    semantic_counts = Counter(row["semantic_status_after_cleanup"] for row in matrix_rows)
    runtime_semantic_counts = Counter(
        f"{row['runtime_axis_current']}::{row['semantic_status_after_cleanup']}" for row in matrix_rows
    )
    full_runtime_semantic_counts = Counter(
        row["semantic_status_after_cleanup"] for row in full_runtime_rows
    )
    silent_review_rows = [
        row for row in matrix_rows if str(row.get("candidate_family") or "") == "role_fallback_silent"
    ]
    silent_review_disposition_counts = Counter(
        str(row["final_disposition"]) for row in silent_review_rows
    )
    silent_review_semantic_counts = Counter(
        str(row["semantic_status_after_cleanup"]) for row in silent_review_rows
    )

    summary = {
        "schema_version": "weak-active-cleanup-w6-aggregate-v1",
        "matrix_row_count": len(matrix_rows),
        "status_model_row_count": len(status_model_rows),
        "backlog_row_count": len(backlog_rows),
        "full_runtime_row_count": len(full_runtime_rows),
        "semantic_status_counts": normalize_counter(semantic_counts),
        "runtime_semantic_status_counts": normalize_counter(runtime_semantic_counts),
        "full_runtime_semantic_status_counts": normalize_counter(full_runtime_semantic_counts),
        "silent_review_row_count": len(silent_review_rows),
        "silent_review_disposition_counts": normalize_counter(silent_review_disposition_counts),
        "silent_review_semantic_counts": normalize_counter(silent_review_semantic_counts),
        "output_paths": {
            "matrix": str(output_dir / MATRIX_PATH.name),
            "status_model": str(output_dir / STATUS_MODEL_PATH.name),
            "backlog_map": str(output_dir / BACKLOG_PATH.name),
            "full_classification": str(output_dir / FULL_CLASSIFICATION_PATH.name),
            "post_cleanup_candidate_facts": str(output_dir / POST_CLEANUP_FACTS_PATH.name),
        },
    }

    dump_json(output_dir / MATRIX_PATH.name, {"rows": matrix_rows})
    dump_json(output_dir / STATUS_MODEL_PATH.name, {"rows": status_model_rows})
    dump_json(output_dir / BACKLOG_PATH.name, {"rows": backlog_rows})
    dump_json(output_dir / FULL_CLASSIFICATION_PATH.name, {"rows": full_runtime_rows})
    dump_jsonl(output_dir / POST_CLEANUP_FACTS_PATH.name, post_cleanup_candidate_facts)
    dump_json(output_dir / SUMMARY_PATH.name, summary)

    return summary


def main() -> int:
    summary = build_w6_aggregate()
    print("weak-active cleanup W-6 aggregate generated")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
