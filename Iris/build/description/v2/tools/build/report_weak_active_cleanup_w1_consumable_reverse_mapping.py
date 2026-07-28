from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


INTEGRATED_RUNTIME_DIR = ROOT / "staging" / "interaction_cluster" / "source_coverage_runtime"
INTEGRATED_FACTS_PATH = INTEGRATED_RUNTIME_DIR / "dvf_3_3_facts.integrated.jsonl"

W0_OUTPUT_DIR = ROOT / "staging" / "weak_active_cleanup" / "w0"
W0_CANDIDATE_LIST_PATH = W0_OUTPUT_DIR / "weak_active_candidate_list.json"
W0_BASELINE_MANIFEST_PATH = W0_OUTPUT_DIR / "weak_cleanup_baseline_manifest.json"

SOURCE_COVERAGE_DIR = ROOT / "staging" / "source_coverage" / "block_c"
B1_DIR = SOURCE_COVERAGE_DIR / "b1_consumable_package"
B3_DIR = SOURCE_COVERAGE_DIR / "b3_resource_package"

OUTPUT_DIR = ROOT / "staging" / "weak_active_cleanup" / "w1_consumable_reverse_mapping"
SUMMARY_PATH = OUTPUT_DIR / "w1_consumable_reverse_mapping_summary.json"
MAPPING_PATH = OUTPUT_DIR / "w1_consumable_reverse_mapping.json"
PROMOTED_FACTS_PATH = OUTPUT_DIR / "w1_consumable_promoted_candidate_facts.jsonl"
DISPOSITION_NOTE_PATH = OUTPUT_DIR / "w1_consumable_disposition_note.md"

TARGET_PRIMARY_CLASSES = ("Consumable.3-A", "Consumable.3-B", "Consumable.3-D", "Resource.4-B")
ROADMAP_EXPECTED_COUNTS = {
    "Consumable.3-A": 66,
    "Consumable.3-B": 6,
    "Consumable.3-D": 3,
    "Resource.4-B": 10,
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def dump_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def normalize_counter(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def cluster_catalog_from_package(
    *,
    facts_path: Path,
    decisions_path: Path,
    package_id: str,
) -> dict[str, dict[str, Any]]:
    facts = load_jsonl(facts_path)
    decisions = load_jsonl(decisions_path)
    facts_by_id = {str(row["item_id"]): row for row in facts}

    grouped_primary_use: defaultdict[str, Counter[str]] = defaultdict(Counter)
    grouped_roles: defaultdict[str, Counter[str]] = defaultdict(Counter)
    grouped_item_ids: defaultdict[str, list[str]] = defaultdict(list)

    for decision in decisions:
        if str(decision.get("use_source") or "") != "cluster_summary":
            continue
        cluster_id = str(decision.get("selected_cluster") or "")
        if not cluster_id:
            continue
        item_id = str(decision["item_id"])
        fact = facts_by_id[item_id]
        primary_use = str(fact.get("primary_use") or "")
        selected_role = str(decision.get("selected_role") or "")

        grouped_primary_use[cluster_id][primary_use] += 1
        grouped_roles[cluster_id][selected_role] += 1
        grouped_item_ids[cluster_id].append(item_id)

    catalog: dict[str, dict[str, Any]] = {}
    for cluster_id in sorted(grouped_primary_use):
        primary_use_counts = grouped_primary_use[cluster_id]
        role_counts = grouped_roles[cluster_id]
        canonical_primary_use, primary_use_count = primary_use_counts.most_common(1)[0]
        canonical_role, role_count = role_counts.most_common(1)[0]
        catalog[cluster_id] = {
            "cluster_id": cluster_id,
            "package_id": package_id,
            "canonical_primary_use": canonical_primary_use,
            "canonical_primary_use_count": primary_use_count,
            "canonical_role": canonical_role,
            "canonical_role_count": role_count,
            "sample_item_ids": sorted(grouped_item_ids[cluster_id])[:10],
        }
    return catalog


def is_comfort_item(row: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(value or "")
        for value in (
            row.get("item_id"),
            row.get("display_name"),
            row.get("identity_hint"),
        )
    ).lower()
    return "wine" in haystack or "beer" in haystack


def is_beverage_item(row: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(value or "")
        for value in (
            row.get("item_id"),
            row.get("display_name"),
            row.get("identity_hint"),
            row.get("display_category"),
        )
    ).lower()
    tokens = ("drink", "beverage", "cuppa", "mug", "tea", "coffee")
    return any(token in haystack for token in tokens)


def choose_cluster_for_target(row: dict[str, Any]) -> tuple[str | None, str | None, list[str]]:
    primary_class = str(row.get("primary_classification") or "")
    reasons: list[str] = [f"primary_classification:{primary_class}"]

    if primary_class == "Resource.4-B":
        reasons.append("resource_4b_reverse_mapped_to_b3_cooking_prep")
        return "cooking_prep", "B-3", reasons

    if primary_class == "Consumable.3-B" and str(row.get("item_id")) == "Base.Bleach":
        reasons.append("bleach_matches_b1_cluster_absent_identity_fallback_case")
        return None, None, reasons

    if is_comfort_item(row):
        reasons.append("comfort_pattern_match")
        return "comfort_consumption", "B-1", reasons

    if primary_class in {"Consumable.3-B", "Consumable.3-D"} or is_beverage_item(row):
        reasons.append("beverage_pattern_match")
        return "beverage_consumption", "B-1", reasons

    if primary_class == "Consumable.3-A":
        reasons.append("consumable_3a_default_food_consumption")
        return "food_consumption", "B-1", reasons

    reasons.append("no_mapping_rule")
    return None, None, reasons


def build_mapping_row(
    *,
    row: dict[str, Any],
    cluster_catalog: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    cluster_id, source_package, reasons = choose_cluster_for_target(row)
    mapping: dict[str, Any] = {
        "item_id": row["item_id"],
        "display_name": row.get("display_name"),
        "primary_classification": row.get("primary_classification"),
        "classifications": row.get("classifications"),
        "old_primary_use": row.get("primary_use"),
        "identity_hint": row.get("identity_hint"),
        "cleanup_scope": row.get("cleanup_scope"),
        "candidate_family": row.get("candidate_family"),
        "mapping_reasons": reasons,
    }

    if cluster_id is None or source_package is None:
        mapping.update(
            {
                "disposition": "weak_type_required",
                "weak_type": "W3",
                "proposed_cluster": None,
                "proposed_primary_use": None,
                "source_package": None,
                "source_path_after_mapping": None,
                "rationale": "No direct reverse mapping rule matched; source expansion remains the safer follow-up.",
            }
        )
        return mapping

    cluster_info = cluster_catalog.get(cluster_id)
    if cluster_info is None:
        mapping.update(
            {
                "disposition": "weak_type_required",
                "weak_type": "W3",
                "proposed_cluster": cluster_id,
                "proposed_primary_use": None,
                "source_package": source_package,
                "source_path_after_mapping": None,
                "rationale": "Reverse mapping rule matched, but no canonical cluster phrasing was found in staged package artifacts.",
            }
        )
        return mapping

    mapping.update(
        {
            "disposition": "promote_candidate",
            "weak_type": None,
            "proposed_cluster": cluster_id,
            "proposed_role": cluster_info["canonical_role"],
            "proposed_primary_use": cluster_info["canonical_primary_use"],
            "source_package": source_package,
            "source_path_after_mapping": "cluster_summary",
            "rationale": "Existing staged package cluster can be reverse-applied without reopening 3-4 detail structure.",
            "cluster_canonical_source": {
                "package_id": cluster_info["package_id"],
                "sample_item_ids": cluster_info["sample_item_ids"],
            },
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
        item_id = str(mapping["item_id"])
        fact = dict(facts_by_id[item_id])
        fact["primary_use"] = mapping["proposed_primary_use"]

        fact_origin = dict(fact.get("fact_origin") or {})
        fact_origin["primary_use"] = ["cluster_summary"]
        fact["fact_origin"] = fact_origin

        slot_meta = dict(fact.get("slot_meta") or {})
        slot_meta["weak_cleanup_w1"] = {
            "cleanup_phase": "W-1",
            "proposed_cluster": mapping["proposed_cluster"],
            "proposed_role": mapping.get("proposed_role"),
            "source_package": mapping["source_package"],
        }
        fact["slot_meta"] = slot_meta
        promoted_rows.append(fact)

    promoted_rows.sort(key=lambda row: str(row["item_id"]))
    return promoted_rows


def render_disposition_note(summary: dict[str, Any]) -> str:
    cluster_counts = summary["proposed_cluster_counts"]
    class_counts = summary["actual_scope_counts_by_primary_classification"]
    weak_type_counts = summary["weak_type_counts"]
    return "\n".join(
        [
            "# W-1 Consumable Reverse Mapping Note",
            "",
            "## Scope",
            "",
            f"- roadmap expected target count: `{summary['roadmap_expected_target_count']}`",
            f"- current artifact scope count: `{summary['actual_scope_row_count']}`",
            f"- scope delta vs roadmap: `{summary['actual_scope_row_count'] - summary['roadmap_expected_target_count']}`",
            "",
            "Current W-1 execution uses the current W-0 candidate inventory as authority.",
            "If this differs from earlier roadmap prose, the inventory artifact wins.",
            "",
            "## Actual scope by primary classification",
            "",
            *[f"- `{key}`: `{value}`" for key, value in class_counts.items()],
            "",
            "## Reverse-mapping result",
            "",
            f"- promote candidates: `{summary['promote_candidate_count']}`",
            f"- weak-type-required rows: `{summary['weak_type_required_count']}`",
            "",
            "Proposed clusters:",
            "",
            *[f"- `{key}`: `{value}`" for key, value in cluster_counts.items()],
            "",
            "Weak-type rows:",
            "",
            *(
                [f"- `{key}`: `{value}`" for key, value in weak_type_counts.items()]
                if weak_type_counts
                else ["- none"]
            ),
            "",
            "## Interpretation",
            "",
            "This phase produces reverse-mapping candidates only.",
            "It does not rewrite the integrated runtime artifacts directly.",
            "",
        ]
    )


def build_w1_consumable_reverse_mapping(
    *,
    w0_candidate_list_path: Path = W0_CANDIDATE_LIST_PATH,
    w0_baseline_manifest_path: Path = W0_BASELINE_MANIFEST_PATH,
    integrated_facts_path: Path = INTEGRATED_FACTS_PATH,
    b1_facts_path: Path = B1_DIR / "b1_consumable_facts.jsonl",
    b1_decisions_path: Path = B1_DIR / "b1_consumable_decisions.jsonl",
    b3_facts_path: Path = B3_DIR / "b3_resource_facts.jsonl",
    b3_decisions_path: Path = B3_DIR / "b3_resource_decisions.jsonl",
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    candidate_payload = load_json(w0_candidate_list_path)
    baseline_manifest = load_json(w0_baseline_manifest_path)
    integrated_facts = load_jsonl(integrated_facts_path)

    candidate_rows = list(candidate_payload["rows"])
    target_rows = [
        row
        for row in candidate_rows
        if row.get("candidate_family") == "identity_fallback_active"
        and row.get("primary_classification") in TARGET_PRIMARY_CLASSES
    ]

    b1_catalog = cluster_catalog_from_package(
        facts_path=b1_facts_path,
        decisions_path=b1_decisions_path,
        package_id="B-1",
    )
    b3_catalog = cluster_catalog_from_package(
        facts_path=b3_facts_path,
        decisions_path=b3_decisions_path,
        package_id="B-3",
    )
    cluster_catalog = {**b1_catalog, **b3_catalog}

    mapping_rows = [build_mapping_row(row=row, cluster_catalog=cluster_catalog) for row in target_rows]
    mapping_rows.sort(key=lambda row: (row["primary_classification"], row["item_id"]))

    promoted_candidate_facts = build_promoted_candidate_facts(
        mapping_rows=mapping_rows,
        integrated_facts=integrated_facts,
    )

    actual_scope_counts: Counter[str] = Counter(
        str(row.get("primary_classification") or "(missing)") for row in target_rows
    )
    proposed_cluster_counts: Counter[str] = Counter(
        str(row["proposed_cluster"]) for row in mapping_rows if row.get("proposed_cluster")
    )
    disposition_counts: Counter[str] = Counter(str(row["disposition"]) for row in mapping_rows)
    weak_type_counts: Counter[str] = Counter(
        str(row["weak_type"]) for row in mapping_rows if row.get("weak_type")
    )

    summary = {
        "schema_version": "weak-active-cleanup-w1-consumable-reverse-mapping-v0",
        "authority": {
            "w0_candidate_list": str(w0_candidate_list_path),
            "w0_baseline_manifest": str(w0_baseline_manifest_path),
            "integrated_facts": str(integrated_facts_path),
        },
        "scope_rule": {
            "candidate_family": "identity_fallback_active",
            "primary_classifications": list(TARGET_PRIMARY_CLASSES),
        },
        "roadmap_expected_target_count": sum(ROADMAP_EXPECTED_COUNTS.values()),
        "roadmap_expected_counts_by_primary_classification": ROADMAP_EXPECTED_COUNTS,
        "actual_scope_row_count": len(target_rows),
        "actual_scope_counts_by_primary_classification": normalize_counter(actual_scope_counts),
        "promote_candidate_count": disposition_counts.get("promote_candidate", 0),
        "weak_type_required_count": disposition_counts.get("weak_type_required", 0),
        "disposition_counts": normalize_counter(disposition_counts),
        "weak_type_counts": normalize_counter(weak_type_counts),
        "proposed_cluster_counts": normalize_counter(proposed_cluster_counts),
        "w0_candidate_scope_counts": baseline_manifest.get("baseline_counts", {}).get("candidate_family_counts"),
        "output_paths": {
            "mapping": str(output_dir / MAPPING_PATH.name),
            "promoted_candidate_facts": str(output_dir / PROMOTED_FACTS_PATH.name),
            "disposition_note": str(output_dir / DISPOSITION_NOTE_PATH.name),
        },
    }

    mapping_payload = {
        "schema_version": "weak-active-cleanup-w1-consumable-reverse-mapping-rows-v0",
        "summary_ref": str(output_dir / SUMMARY_PATH.name),
        "row_count": len(mapping_rows),
        "rows": mapping_rows,
    }

    dump_json(output_dir / SUMMARY_PATH.name, summary)
    dump_json(output_dir / MAPPING_PATH.name, mapping_payload)
    dump_jsonl(output_dir / PROMOTED_FACTS_PATH.name, promoted_candidate_facts)
    dump_text(output_dir / DISPOSITION_NOTE_PATH.name, render_disposition_note(summary))

    return summary


def main() -> int:
    summary = build_w1_consumable_reverse_mapping()
    print("weak-active cleanup W-1 consumable reverse mapping generated")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
