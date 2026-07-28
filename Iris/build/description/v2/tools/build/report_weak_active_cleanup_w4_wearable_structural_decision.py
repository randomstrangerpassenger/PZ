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
from tools.build.report_weak_active_cleanup_w3_unknown_classification import (
    MAPPING_PATH as W3_MAPPING_PATH,
)


BW_DIR = ROOT / "staging" / "source_coverage" / "block_c" / "bw_wearable_package"

OUTPUT_DIR = ROOT / "staging" / "weak_active_cleanup" / "w4_wearable_structural_decision"
SUMMARY_PATH = OUTPUT_DIR / "w4_wearable_structural_decision_summary.json"
MAPPING_PATH = OUTPUT_DIR / "w4_wearable_structural_decision.json"
PROMOTED_FACTS_PATH = OUTPUT_DIR / "w4_wearable_promoted_candidate_facts.jsonl"
MEMO_PATH = OUTPUT_DIR / "wearable_decision_memo.md"


def build_w4_input_rows(
    *,
    w0_candidate_rows: list[dict[str, Any]],
    w3_mapping_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for row in w0_candidate_rows:
        primary_class = str(row.get("primary_classification") or "")
        if row.get("candidate_family") == "identity_fallback_active" and primary_class.startswith("Wearable."):
            cloned = dict(row)
            cloned["assigned_primary_classification"] = primary_class
            cloned["w4_input_source"] = "W0"
            rows.append(cloned)

    for row in w3_mapping_rows:
        if row.get("next_phase") != "W-4":
            continue
        cloned = {
            "item_id": row["item_id"],
            "display_name": row.get("display_name"),
            "display_category": row.get("display_category"),
            "type": row.get("type"),
            "body_location": row.get("body_location"),
            "primary_use": row.get("old_primary_use"),
            "identity_hint": row.get("identity_hint"),
            "assigned_primary_classification": row.get("assigned_primary_classification"),
            "candidate_family": "identity_fallback_active",
            "cleanup_scope": "weak_active",
            "w4_input_source": "W3",
        }
        rows.append(cloned)

    rows.sort(key=lambda row: (str(row.get("assigned_primary_classification") or ""), str(row["item_id"])))
    return rows


def build_mapping_row(
    *,
    row: dict[str, Any],
    bw_catalog: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    assigned_primary = str(row.get("assigned_primary_classification") or "")
    mapping: dict[str, Any] = {
        "item_id": row["item_id"],
        "display_name": row.get("display_name"),
        "display_category": row.get("display_category"),
        "body_location": row.get("body_location"),
        "old_primary_use": row.get("primary_use"),
        "identity_hint": row.get("identity_hint"),
        "assigned_primary_classification": assigned_primary,
        "w4_input_source": row.get("w4_input_source"),
    }

    if assigned_primary == "Wearable.6-F":
        cluster_info = bw_catalog["container_storage"]
        mapping.update(
            {
                "disposition": "promote_candidate",
                "weak_type": None,
                "proposed_cluster": "container_storage",
                "source_package": "BW",
                "source_path_after_mapping": "cluster_summary",
                "proposed_primary_use": cluster_info["canonical_primary_use"],
                "proposed_role": cluster_info["canonical_role"],
                "rationale": "Bag-class wearables have an existing container-storage cluster and should be promoted rather than retained on identity fallback.",
                "decision_reasons": ["wearable_subset:bag", "existing_cluster:container_storage"],
                "cluster_canonical_source": {
                    "package_id": cluster_info["package_id"],
                    "sample_item_ids": cluster_info["sample_item_ids"],
                },
            }
        )
        return mapping

    mapping.update(
        {
            "disposition": "retain_identity_fallback",
            "weak_type": "W2",
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "proposed_primary_use": None,
            "proposed_role": None,
            "rationale": "Outside the bag subset, wearable rows do not gain a representative 3-3 work context beyond wearing/appearance, so identity-level meaning is retained as semantic-adequate.",
            "decision_reasons": ["wearable_structural_decision", "non_bag_wearable_semantic_adequate"],
        }
    )
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
        fact = dict(facts_by_id[str(mapping["item_id"])])
        fact["primary_use"] = mapping["proposed_primary_use"]

        fact_origin = dict(fact.get("fact_origin") or {})
        fact_origin["primary_use"] = ["cluster_summary"]
        fact["fact_origin"] = fact_origin

        slot_meta = dict(fact.get("slot_meta") or {})
        slot_meta["weak_cleanup_w4"] = {
            "cleanup_phase": "W-4",
            "assigned_primary_classification": mapping["assigned_primary_classification"],
            "proposed_cluster": mapping["proposed_cluster"],
            "proposed_role": mapping["proposed_role"],
            "source_package": mapping["source_package"],
        }
        fact["slot_meta"] = slot_meta
        promoted_rows.append(fact)

    promoted_rows.sort(key=lambda row: str(row["item_id"]))
    return promoted_rows


def render_memo(summary: dict[str, Any]) -> str:
    class_counts = summary["assigned_primary_classification_counts"]
    return "\n".join(
        [
            "# W-4 Wearable Structural Decision Memo",
            "",
            "## Decision",
            "",
            "- `Wearable.6-F` only: promote through `container_storage`.",
            "- all other wearable subclasses: retain identity fallback as `W2 semantic-adequate`.",
            "",
            "## Scope",
            "",
            f"- W-0 wearable rows: `{summary['w0_existing_wearable_row_count']}`",
            f"- W-3 deferred wearable rows: `{summary['w3_deferred_row_count']}`",
            f"- total W-4 input rows: `{summary['actual_scope_row_count']}`",
            "",
            "## Assigned subclasses in scope",
            "",
            *[f"- `{key}`: `{value}`" for key, value in class_counts.items()],
            "",
            "## Rationale",
            "",
            "Bag rows already have an evidence-backed container context in the wearable package.",
            "For the remaining wearable rows, representative context collapses back to wearing/appearance, so forcing cluster summaries would violate the 3-3 boundary rather than improve it.",
            "",
        ]
    )


def build_w4_wearable_structural_decision(
    *,
    w0_candidate_list_path: Path = W0_CANDIDATE_LIST_PATH,
    w0_baseline_manifest_path: Path = W0_BASELINE_MANIFEST_PATH,
    integrated_facts_path: Path = INTEGRATED_FACTS_PATH,
    w3_mapping_path: Path = W3_MAPPING_PATH,
    bw_facts_path: Path = BW_DIR / "bw_wearable_facts.jsonl",
    bw_decisions_path: Path = BW_DIR / "bw_wearable_decisions.jsonl",
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    candidate_payload = load_json(w0_candidate_list_path)
    baseline_manifest = load_json(w0_baseline_manifest_path)
    integrated_facts = load_jsonl(integrated_facts_path)
    w3_mapping_payload = load_json(w3_mapping_path)

    input_rows = build_w4_input_rows(
        w0_candidate_rows=list(candidate_payload["rows"]),
        w3_mapping_rows=list(w3_mapping_payload["rows"]),
    )
    bw_catalog = cluster_catalog_from_package(
        facts_path=bw_facts_path,
        decisions_path=bw_decisions_path,
        package_id="BW",
    )
    mapping_rows = [build_mapping_row(row=row, bw_catalog=bw_catalog) for row in input_rows]
    promoted_candidate_facts = build_promoted_candidate_facts(
        mapping_rows=mapping_rows,
        integrated_facts=integrated_facts,
    )

    assigned_primary_counts = Counter(
        str(row.get("assigned_primary_classification") or "(unassigned)") for row in mapping_rows
    )
    disposition_counts = Counter(str(row["disposition"]) for row in mapping_rows)
    weak_type_counts = Counter(str(row["weak_type"]) for row in mapping_rows if row.get("weak_type"))
    input_source_counts = Counter(str(row["w4_input_source"]) for row in mapping_rows)
    proposed_cluster_counts = Counter(
        str(row["proposed_cluster"]) for row in mapping_rows if row.get("proposed_cluster")
    )

    summary = {
        "schema_version": "weak-active-cleanup-w4-wearable-structural-decision-v0",
        "authority": {
            "w0_candidate_list": str(w0_candidate_list_path),
            "w0_baseline_manifest": str(w0_baseline_manifest_path),
            "integrated_facts": str(integrated_facts_path),
            "w3_mapping": str(w3_mapping_path),
        },
        "policy_decision": {
            "bag_subset_promotable": True,
            "non_bag_wearables_semantic_adequate": True,
        },
        "actual_scope_row_count": len(mapping_rows),
        "w0_existing_wearable_row_count": input_source_counts.get("W0", 0),
        "w3_deferred_row_count": input_source_counts.get("W3", 0),
        "assigned_primary_classification_counts": normalize_counter(assigned_primary_counts),
        "disposition_counts": normalize_counter(disposition_counts),
        "weak_type_counts": normalize_counter(weak_type_counts),
        "proposed_cluster_counts": normalize_counter(proposed_cluster_counts),
        "w0_candidate_scope_counts": baseline_manifest.get("baseline_counts", {}).get("candidate_family_counts"),
        "output_paths": {
            "mapping": str(output_dir / MAPPING_PATH.name),
            "promoted_candidate_facts": str(output_dir / PROMOTED_FACTS_PATH.name),
            "memo": str(output_dir / MEMO_PATH.name),
        },
    }

    mapping_payload = {
        "schema_version": "weak-active-cleanup-w4-wearable-structural-decision-rows-v0",
        "summary_ref": str(output_dir / SUMMARY_PATH.name),
        "row_count": len(mapping_rows),
        "rows": mapping_rows,
    }

    dump_json(output_dir / SUMMARY_PATH.name, summary)
    dump_json(output_dir / MAPPING_PATH.name, mapping_payload)
    dump_jsonl(output_dir / PROMOTED_FACTS_PATH.name, promoted_candidate_facts)
    dump_text(output_dir / MEMO_PATH.name, render_memo(summary))

    return summary


def main() -> int:
    summary = build_w4_wearable_structural_decision()
    print("weak-active cleanup W-4 wearable structural decision generated")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
