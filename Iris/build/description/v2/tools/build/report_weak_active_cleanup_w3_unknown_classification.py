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
    W0_BASELINE_MANIFEST_PATH,
    W0_CANDIDATE_LIST_PATH,
    cluster_catalog_from_package,
    dump_json,
    dump_jsonl,
    dump_text,
    load_json,
    load_jsonl,
    normalize_counter,
)


SOURCE_COVERAGE_DIR = ROOT / "staging" / "source_coverage" / "block_c"
B1_DIR = SOURCE_COVERAGE_DIR / "b1_consumable_package"
B4_DIR = SOURCE_COVERAGE_DIR / "b4_residual_package"
BW_DIR = SOURCE_COVERAGE_DIR / "bw_wearable_package"

OUTPUT_DIR = ROOT / "staging" / "weak_active_cleanup" / "w3_unknown_classification"
SUMMARY_PATH = OUTPUT_DIR / "w3_unknown_classification_summary.json"
MAPPING_PATH = OUTPUT_DIR / "w3_unknown_classification_and_disposition.json"
PROMOTED_FACTS_PATH = OUTPUT_DIR / "w3_promoted_candidate_facts.jsonl"
NOTE_PATH = OUTPUT_DIR / "w3_unknown_classification_note.md"

ROADMAP_EXPECTED_TARGET_COUNT = 148


def build_w3_disposition(*, row: dict[str, Any]) -> dict[str, Any]:
    item_id = str(row.get("item_id") or "")
    display_category = str(row.get("display_category") or "")
    body_location = str(row.get("body_location") or "")
    identity_hint = str(row.get("identity_hint") or "")
    reasons: list[str] = [f"display_category:{display_category or '(missing)'}"]

    if display_category == "Bag":
        reasons.append("bag_rows_map_to_portable_storage_wearable_lane")
        return {
            "assigned_primary_classification": "Wearable.6-F",
            "assigned_classifications": ["Wearable.6-F"],
            "disposition": "promote_candidate",
            "next_phase": None,
            "weak_type": None,
            "proposed_cluster": "container_storage",
            "source_package": "BW",
            "source_path_after_mapping": "cluster_summary",
            "rationale": "These bag rows can be classified into Wearable.6-F and reverse-mapped to the existing portable-storage cluster immediately.",
            "classification_reasons": reasons,
        }

    if display_category == "Clothing":
        if body_location == "UnderwearTop":
            reasons.append("underwear_top_maps_to_wearable_6b")
            assigned = "Wearable.6-B"
        elif body_location in {"UnderwearBottom", "Underwear", "UnderwearExtra2", "UnderwearInner"}:
            reasons.append("underwear_bottom_maps_to_wearable_6c")
            assigned = "Wearable.6-C"
        elif body_location == "Tail":
            reasons.append("tail_costume_piece_maps_to_wearable_6g")
            assigned = "Wearable.6-G"
        else:
            reasons.append("fallback_clothing_maps_to_wearable_6b")
            assigned = "Wearable.6-B"
        return {
            "assigned_primary_classification": assigned,
            "assigned_classifications": [assigned],
            "disposition": "defer_to_w4",
            "next_phase": "W-4",
            "weak_type": None,
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "rationale": "This formerly unclassified wearable row should enter the wearable structural review after subclass assignment.",
            "classification_reasons": reasons,
        }

    if display_category == "Accessory":
        if body_location == "UnderwearExtra1":
            reasons.append("legwear_accessory_maps_to_wearable_6c")
            assigned = "Wearable.6-C"
            return {
                "assigned_primary_classification": assigned,
                "assigned_classifications": [assigned],
                "disposition": "defer_to_w4",
                "next_phase": "W-4",
                "weak_type": None,
                "proposed_cluster": None,
                "source_package": None,
                "source_path_after_mapping": "identity_fallback",
                "rationale": "Legwear accessories should be reviewed together with the wearable lane after subclass assignment.",
                "classification_reasons": reasons,
            }
        if body_location == "RightWrist" or identity_hint == "알람 시계" or "Watch" in item_id or item_id == "Base.DigitalWatch":
            reasons.append("timekeeping_accessory_maps_to_resource_4e")
            return {
                "assigned_primary_classification": "Resource.4-E",
                "assigned_classifications": ["Resource.4-E"],
                "disposition": "source_backlog_candidate",
                "next_phase": None,
                "weak_type": "W3",
                "proposed_cluster": None,
                "source_package": None,
                "source_path_after_mapping": "identity_fallback",
                "rationale": "Timekeeping accessories have meaningful device use, but no existing staged cluster summary can be reverse-applied yet.",
                "classification_reasons": reasons,
            }
        reasons.append("jewelry_accessory_maps_to_wearable_6g")
        assigned = "Wearable.6-G"
        return {
            "assigned_primary_classification": assigned,
            "assigned_classifications": [assigned],
            "disposition": "defer_to_w4",
            "next_phase": "W-4",
            "weak_type": None,
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "rationale": "Jewelry-style accessories should be routed into wearable review after subclass assignment.",
            "classification_reasons": reasons,
        }

    if display_category == "FirstAid":
        reasons.append("cataplasm_maps_to_medical_consumable_lane")
        return {
            "assigned_primary_classification": "Consumable.3-C",
            "assigned_classifications": ["Consumable.3-C"],
            "disposition": "promote_candidate",
            "next_phase": None,
            "weak_type": None,
            "proposed_cluster": "medical_treatment",
            "source_package": "B-1",
            "source_path_after_mapping": "cluster_summary",
            "rationale": "Prepared poultice rows can be reclassified into the medical-consumable lane and promoted through the existing medical-treatment cluster.",
            "classification_reasons": reasons,
        }

    if display_category == "Food":
        reasons.append("poured_beer_maps_to_ready_drink_lane")
        return {
            "assigned_primary_classification": "Consumable.3-D",
            "assigned_classifications": ["Consumable.3-D"],
            "disposition": "promote_candidate",
            "next_phase": None,
            "weak_type": None,
            "proposed_cluster": "comfort_consumption",
            "source_package": "B-1",
            "source_path_after_mapping": "cluster_summary",
            "rationale": "Prepared beer rows fit the existing comfort-consumption cluster better than identity fallback.",
            "classification_reasons": reasons,
        }

    if display_category == "Gardening":
        reasons.append("watering_can_maps_to_gardening_tool_lane")
        return {
            "assigned_primary_classification": "Tool.1-E",
            "assigned_classifications": ["Tool.1-E"],
            "disposition": "source_backlog_candidate",
            "next_phase": None,
            "weak_type": "W3",
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "rationale": "The gardening-tool context exists, but current staged clusters do not cover watering-can use yet.",
            "classification_reasons": reasons,
        }

    if display_category == "Trapping":
        reasons.append("trap_tools_map_to_hunting_tool_lane")
        return {
            "assigned_primary_classification": "Tool.1-G",
            "assigned_classifications": ["Tool.1-G"],
            "disposition": "source_backlog_candidate",
            "next_phase": None,
            "weak_type": "W3",
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "rationale": "Trapping tools need their own source-backed context; no existing staged cluster matches safely yet.",
            "classification_reasons": reasons,
        }

    if display_category == "Explosives":
        if item_id.startswith("Base.NoiseTrap"):
            reasons.append("noise_trap_reuses_existing_explosive_device_cluster")
            return {
                "assigned_primary_classification": "Resource.4-E",
                "assigned_classifications": ["Resource.4-E"],
                "disposition": "promote_candidate",
                "next_phase": None,
                "weak_type": None,
                "proposed_cluster": "explosive_devices",
                "source_package": "B-4",
                "source_path_after_mapping": "cluster_summary",
                "rationale": "Noise trap variants align with the existing distraction-device cluster from B-4.",
                "classification_reasons": reasons,
            }
        if item_id.startswith("Base.PipeBomb") or item_id.startswith("Base.SmokeBomb"):
            reasons.append("bomb_variant_maps_to_combat_2j_primary")
            assigned = "Combat.2-J"
        else:
            reasons.append("trap_variant_maps_to_resource_4e_primary")
            assigned = "Resource.4-E"
        return {
            "assigned_primary_classification": assigned,
            "assigned_classifications": [assigned],
            "disposition": "source_backlog_candidate",
            "next_phase": None,
            "weak_type": "W3",
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "rationale": "These explosive variants have meaningful interaction context, but current staged clusters do not support safe reverse mapping yet.",
            "classification_reasons": reasons,
        }

    if display_category in {"Electronics", "Paint", "Material"}:
        reasons.append("resource_like_unknown_maps_to_resource_4e")
        return {
            "assigned_primary_classification": "Resource.4-E",
            "assigned_classifications": ["Resource.4-E"],
            "disposition": "source_backlog_candidate",
            "next_phase": None,
            "weak_type": "W3",
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "rationale": "This resource-like row needs a new source path or cluster; existing staged clusters do not capture its representative 3-3 context yet.",
            "classification_reasons": reasons,
        }

    reasons.append("no_unknown_classification_rule")
    return {
        "assigned_primary_classification": None,
        "assigned_classifications": [],
        "disposition": "source_backlog_candidate",
        "next_phase": None,
        "weak_type": "W3",
        "proposed_cluster": None,
        "source_package": None,
        "source_path_after_mapping": "identity_fallback",
        "rationale": "No W-3 classification rule matched; this row stays on source backlog review.",
        "classification_reasons": reasons,
    }


def build_mapping_row(
    *,
    row: dict[str, Any],
    catalogs_by_package: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    disposition_info = build_w3_disposition(row=row)
    mapping: dict[str, Any] = {
        "item_id": row["item_id"],
        "display_name": row.get("display_name"),
        "display_category": row.get("display_category"),
        "type": row.get("type"),
        "body_location": row.get("body_location"),
        "old_primary_use": row.get("primary_use"),
        "identity_hint": row.get("identity_hint"),
        "assigned_primary_classification": disposition_info["assigned_primary_classification"],
        "assigned_classifications": disposition_info["assigned_classifications"],
        "disposition": disposition_info["disposition"],
        "next_phase": disposition_info["next_phase"],
        "weak_type": disposition_info["weak_type"],
        "proposed_cluster": disposition_info["proposed_cluster"],
        "source_package": disposition_info["source_package"],
        "source_path_after_mapping": disposition_info["source_path_after_mapping"],
        "classification_reasons": disposition_info["classification_reasons"],
        "rationale": disposition_info["rationale"],
    }

    package_id = disposition_info["source_package"]
    cluster_id = disposition_info["proposed_cluster"]
    if not package_id or not cluster_id:
        mapping["proposed_primary_use"] = None
        mapping["proposed_role"] = None
        return mapping

    cluster_info = catalogs_by_package.get(package_id, {}).get(cluster_id)
    if cluster_info is None:
        mapping.update(
            {
                "disposition": "source_backlog_candidate",
                "weak_type": "W3",
                "proposed_primary_use": None,
                "proposed_role": None,
                "source_path_after_mapping": "identity_fallback",
                "rationale": "A reverse-mapping rule matched, but the referenced staged package lacks canonical cluster phrasing.",
            }
        )
        return mapping

    mapping["proposed_primary_use"] = cluster_info["canonical_primary_use"]
    mapping["proposed_role"] = cluster_info["canonical_role"]
    mapping["cluster_canonical_source"] = {
        "package_id": cluster_info["package_id"],
        "sample_item_ids": cluster_info["sample_item_ids"],
    }
    return mapping


def build_promoted_candidate_facts(
    *,
    mapping_rows: list[dict[str, Any]],
    integrated_facts: list[dict[str, Any]],
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
        slot_meta["weak_cleanup_w3"] = {
            "cleanup_phase": "W-3",
            "assigned_primary_classification": mapping["assigned_primary_classification"],
            "proposed_cluster": mapping["proposed_cluster"],
            "proposed_role": mapping.get("proposed_role"),
            "source_package": mapping["source_package"],
        }
        fact["slot_meta"] = slot_meta
        promoted_rows.append(fact)

    promoted_rows.sort(key=lambda row: str(row["item_id"]))
    return promoted_rows


def render_note(summary: dict[str, Any]) -> str:
    assigned_counts = summary["assigned_primary_classification_counts"]
    disposition_counts = summary["disposition_counts"]
    cluster_counts = summary["proposed_cluster_counts"]
    deferred_counts = summary["deferred_to_phase_counts"]
    return "\n".join(
        [
            "# W-3 Unknown Classification Note",
            "",
            "## Scope",
            "",
            f"- roadmap expected target count: `{summary['roadmap_expected_target_count']}`",
            f"- current artifact scope count: `{summary['actual_scope_row_count']}`",
            f"- scope delta vs roadmap: `{summary['actual_scope_row_count'] - summary['roadmap_expected_target_count']}`",
            "",
            "Current W-3 execution uses missing primary-classification rows from the current W-0 candidate inventory as authority.",
            "",
            "## Assigned primary classifications",
            "",
            *[f"- `{key}`: `{value}`" for key, value in assigned_counts.items()],
            "",
            "## Disposition",
            "",
            *[f"- `{key}`: `{value}`" for key, value in disposition_counts.items()],
            "",
            "Promoted clusters:",
            "",
            *(
                [f"- `{key}`: `{value}`" for key, value in cluster_counts.items()]
                if cluster_counts
                else ["- none"]
            ),
            "",
            "Deferred phases:",
            "",
            *(
                [f"- `{key}`: `{value}`" for key, value in deferred_counts.items()]
                if deferred_counts
                else ["- none"]
            ),
            "",
            "## Interpretation",
            "",
            "This phase assigns missing subclass lanes first, then promotes only rows with an already-available staged cluster.",
            "Wearable rows without immediate cluster action are routed into W-4 rather than being forced into premature weak typing.",
            "",
        ]
    )


def build_w3_unknown_classification(
    *,
    w0_candidate_list_path: Path = W0_CANDIDATE_LIST_PATH,
    w0_baseline_manifest_path: Path = W0_BASELINE_MANIFEST_PATH,
    integrated_facts_path: Path = INTEGRATED_FACTS_PATH,
    b1_facts_path: Path = B1_DIR / "b1_consumable_facts.jsonl",
    b1_decisions_path: Path = B1_DIR / "b1_consumable_decisions.jsonl",
    b4_facts_path: Path = B4_DIR / "b4_residual_facts.jsonl",
    b4_decisions_path: Path = B4_DIR / "b4_residual_decisions.jsonl",
    bw_facts_path: Path = BW_DIR / "bw_wearable_facts.jsonl",
    bw_decisions_path: Path = BW_DIR / "bw_wearable_decisions.jsonl",
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    candidate_payload = load_json(w0_candidate_list_path)
    baseline_manifest = load_json(w0_baseline_manifest_path)
    integrated_facts = load_jsonl(integrated_facts_path)

    target_rows = [
        row
        for row in candidate_payload["rows"]
        if row.get("candidate_family") == "identity_fallback_active"
        and str(row.get("primary_classification") or "(missing)") == "(missing)"
    ]

    catalogs_by_package = {
        "B-1": cluster_catalog_from_package(
            facts_path=b1_facts_path,
            decisions_path=b1_decisions_path,
            package_id="B-1",
        ),
        "B-4": cluster_catalog_from_package(
            facts_path=b4_facts_path,
            decisions_path=b4_decisions_path,
            package_id="B-4",
        ),
        "BW": cluster_catalog_from_package(
            facts_path=bw_facts_path,
            decisions_path=bw_decisions_path,
            package_id="BW",
        ),
    }

    mapping_rows = [
        build_mapping_row(row=row, catalogs_by_package=catalogs_by_package) for row in target_rows
    ]
    mapping_rows.sort(key=lambda row: (str(row["assigned_primary_classification"]), row["item_id"]))

    promoted_candidate_facts = build_promoted_candidate_facts(
        mapping_rows=mapping_rows,
        integrated_facts=integrated_facts,
    )

    assigned_primary_counts = Counter(
        str(row.get("assigned_primary_classification") or "(unassigned)") for row in mapping_rows
    )
    disposition_counts = Counter(str(row["disposition"]) for row in mapping_rows)
    weak_type_counts = Counter(str(row["weak_type"]) for row in mapping_rows if row.get("weak_type"))
    proposed_cluster_counts = Counter(
        str(row["proposed_cluster"]) for row in mapping_rows if row.get("proposed_cluster")
    )
    deferred_counts = Counter(str(row["next_phase"]) for row in mapping_rows if row.get("next_phase"))

    summary = {
        "schema_version": "weak-active-cleanup-w3-unknown-classification-v0",
        "authority": {
            "w0_candidate_list": str(w0_candidate_list_path),
            "w0_baseline_manifest": str(w0_baseline_manifest_path),
            "integrated_facts": str(integrated_facts_path),
        },
        "scope_rule": {
            "candidate_family": "identity_fallback_active",
            "primary_classification": "(missing)",
        },
        "roadmap_expected_target_count": ROADMAP_EXPECTED_TARGET_COUNT,
        "actual_scope_row_count": len(target_rows),
        "assigned_primary_classification_counts": normalize_counter(assigned_primary_counts),
        "disposition_counts": normalize_counter(disposition_counts),
        "weak_type_counts": normalize_counter(weak_type_counts),
        "proposed_cluster_counts": normalize_counter(proposed_cluster_counts),
        "deferred_to_phase_counts": normalize_counter(deferred_counts),
        "w0_candidate_scope_counts": baseline_manifest.get("baseline_counts", {}).get("candidate_family_counts"),
        "output_paths": {
            "mapping": str(output_dir / MAPPING_PATH.name),
            "promoted_candidate_facts": str(output_dir / PROMOTED_FACTS_PATH.name),
            "note": str(output_dir / NOTE_PATH.name),
        },
    }

    mapping_payload = {
        "schema_version": "weak-active-cleanup-w3-unknown-classification-rows-v0",
        "summary_ref": str(output_dir / SUMMARY_PATH.name),
        "row_count": len(mapping_rows),
        "rows": mapping_rows,
    }

    dump_json(output_dir / SUMMARY_PATH.name, summary)
    dump_json(output_dir / MAPPING_PATH.name, mapping_payload)
    dump_jsonl(output_dir / PROMOTED_FACTS_PATH.name, promoted_candidate_facts)
    dump_text(output_dir / NOTE_PATH.name, render_note(summary))

    return summary


def main() -> int:
    summary = build_w3_unknown_classification()
    print("weak-active cleanup W-3 unknown classification generated")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
