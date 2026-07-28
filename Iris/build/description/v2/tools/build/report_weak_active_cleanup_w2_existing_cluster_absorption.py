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
B2_DIR = SOURCE_COVERAGE_DIR / "b2_literature_package"
B3_DIR = SOURCE_COVERAGE_DIR / "b3_resource_package"
B4_DIR = SOURCE_COVERAGE_DIR / "b4_residual_package"
C1RE_DIR = SOURCE_COVERAGE_DIR / "c1re_utility_misc_package"

OUTPUT_DIR = ROOT / "staging" / "weak_active_cleanup" / "w2_existing_cluster_absorption"
SUMMARY_PATH = OUTPUT_DIR / "w2_existing_cluster_absorption_summary.json"
MAPPING_PATH = OUTPUT_DIR / "w2_existing_cluster_absorption.json"
PROMOTED_FACTS_PATH = OUTPUT_DIR / "w2_promoted_candidate_facts.jsonl"
DISPOSITION_NOTE_PATH = OUTPUT_DIR / "w2_existing_cluster_absorption_note.md"

W1_TARGET_PRIMARY_CLASSES = {"Consumable.3-A", "Consumable.3-B", "Consumable.3-D", "Resource.4-B"}
ROADMAP_EXPECTED_TARGET_COUNT = 122


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


def lower_haystack(row: dict[str, Any]) -> str:
    return " ".join(
        str(value or "")
        for value in (
            row.get("item_id"),
            row.get("display_name"),
            row.get("identity_hint"),
            row.get("display_category"),
        )
    ).lower()


def is_firearm(row: dict[str, Any]) -> bool:
    haystack = lower_haystack(row)
    return any(token in haystack for token in ("pistol", "revolver", "shotgun"))


def build_disposition(*, row: dict[str, Any]) -> dict[str, Any]:
    primary_class = str(row.get("primary_classification") or "")
    identity_hint = str(row.get("identity_hint") or "")
    item_id = str(row.get("item_id") or "")
    reasons: list[str] = [f"primary_classification:{primary_class}"]

    if primary_class == "Consumable.3-C":
        reasons.append("medical_consumable_reverse_mapped_to_existing_cluster")
        return {
            "disposition": "promote_candidate",
            "weak_type": None,
            "proposed_cluster": "medical_treatment",
            "source_package": "B-1",
            "source_path_after_mapping": "cluster_summary",
            "rationale": "Existing medical-treatment cluster can absorb this medical consumable without importing 3-4 detail.",
            "mapping_reasons": reasons,
        }

    if primary_class == "Literature.5-C":
        reasons.append("map_item_reverse_mapped_to_existing_cluster")
        return {
            "disposition": "promote_candidate",
            "weak_type": None,
            "proposed_cluster": "map_reference",
            "source_package": "B-2",
            "source_path_after_mapping": "cluster_summary",
            "rationale": "Existing map-reference cluster already captures the representative 3-3 work context for map items.",
            "mapping_reasons": reasons,
        }

    if primary_class == "Tool.1-D":
        if item_id == "Base.Kettle":
            reasons.append("kettle_reverse_mapped_to_cooking_prep")
            return {
                "disposition": "promote_candidate",
                "weak_type": None,
                "proposed_cluster": "cooking_prep",
                "source_package": "C1-Re",
                "source_path_after_mapping": "cluster_summary",
                "rationale": "The kettle fits an existing cooking-prep cluster more cleanly than identity fallback.",
                "mapping_reasons": reasons,
            }
        reasons.append("tableware_reverse_mapped_to_kitchen_table_handling")
        return {
            "disposition": "promote_candidate",
            "weak_type": None,
            "proposed_cluster": "kitchen_table_handling",
            "source_package": "C1-Re",
            "source_path_after_mapping": "cluster_summary",
            "rationale": "Existing kitchen-table-handling cluster gives these vessels a clearer representative context than identity fallback.",
            "mapping_reasons": reasons,
        }

    if primary_class == "Resource.4-E":
        if item_id == "Base.Glue":
            reasons.append("generic_adhesive_spans_multiple_work_contexts")
            return {
                "disposition": "source_backlog_candidate",
                "weak_type": "W3",
                "proposed_cluster": None,
                "source_package": None,
                "source_path_after_mapping": "identity_fallback",
                "rationale": "Glue has meaningful use, but the current staged clusters do not provide a stable representative 3-3 context yet.",
                "mapping_reasons": reasons,
            }
        reasons.append("electronics_component_reverse_mapped_to_existing_cluster")
        return {
            "disposition": "promote_candidate",
            "weak_type": None,
            "proposed_cluster": "electronics_assembly",
            "source_package": "B-3",
            "source_path_after_mapping": "cluster_summary",
            "rationale": "Existing electronics-assembly cluster is a better 3-3 explanation for these electronic components than identity fallback.",
            "mapping_reasons": reasons,
        }

    if primary_class == "Resource.4-F" and item_id == "Base.Rope":
        reasons.extend(
            [
                "b3_material_exclusion_only",
                "b3_package_note_controlled_identity_fallback",
            ]
        )
        return {
            "disposition": "retain_identity_fallback",
            "weak_type": "W2",
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "rationale": "B-3 already records this row as controlled identity fallback with no evidence-aligned cluster path, so semantic-adequate retention is safer than forced promotion.",
            "mapping_reasons": reasons,
        }

    if primary_class.startswith("Combat."):
        if identity_hint == "조리 도구":
            reasons.append("combat_classified_cookware_reuses_existing_cooking_cluster")
            return {
                "disposition": "promote_candidate",
                "weak_type": None,
                "proposed_cluster": "cooking_prep",
                "source_package": "C1-Re",
                "source_path_after_mapping": "cluster_summary",
                "rationale": "These cookware rows already align with an existing cooking-prep cluster despite their combat classification.",
                "mapping_reasons": reasons,
            }
        if is_firearm(row):
            reasons.append("ranged_firearm_cluster_absent_in_staged_packages")
            return {
                "disposition": "source_backlog_candidate",
                "weak_type": "W3",
                "proposed_cluster": None,
                "source_package": None,
                "source_path_after_mapping": "identity_fallback",
                "rationale": "Representative firearm-use context exists, but no existing staged cluster summary can be reverse-applied yet.",
                "mapping_reasons": reasons,
            }
        if identity_hint == "폭발물" or item_id == "Base.Molotov":
            reasons.append("explosive_use_context_requires_new_source")
            return {
                "disposition": "source_backlog_candidate",
                "weak_type": "W3",
                "proposed_cluster": None,
                "source_package": None,
                "source_path_after_mapping": "identity_fallback",
                "rationale": "This explosive row needs a dedicated source path; existing staged clusters do not provide a safe reverse mapping.",
                "mapping_reasons": reasons,
            }
        if identity_hint == "근접 무기":
            reasons.append("explicit_melee_weapon_reverse_mapped_to_existing_cluster")
            return {
                "disposition": "promote_candidate",
                "weak_type": None,
                "proposed_cluster": "melee_combat",
                "source_package": "B-4",
                "source_path_after_mapping": "cluster_summary",
                "rationale": "Existing melee-combat cluster is specific enough for explicit melee-weapon rows.",
                "mapping_reasons": reasons,
            }
        reasons.append("meaningful_context_exists_but_existing_cluster_not_fit")
        return {
            "disposition": "source_backlog_candidate",
            "weak_type": "W3",
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": "identity_fallback",
            "rationale": "A stronger work context likely exists, but it is not covered by current staged clusters.",
            "mapping_reasons": reasons,
        }

    reasons.append("no_existing_cluster_absorption_rule")
    return {
        "disposition": "source_backlog_candidate",
        "weak_type": "W3",
        "proposed_cluster": None,
        "source_package": None,
        "source_path_after_mapping": "identity_fallback",
        "rationale": "This row remains a source-expansion candidate because no existing staged cluster matched safely.",
        "mapping_reasons": reasons,
    }


def build_mapping_row(
    *,
    row: dict[str, Any],
    catalogs_by_package: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    disposition_info = build_disposition(row=row)
    mapping: dict[str, Any] = {
        "item_id": row["item_id"],
        "display_name": row.get("display_name"),
        "primary_classification": row.get("primary_classification"),
        "classifications": row.get("classifications"),
        "old_primary_use": row.get("primary_use"),
        "identity_hint": row.get("identity_hint"),
        "cleanup_scope": row.get("cleanup_scope"),
        "candidate_family": row.get("candidate_family"),
        "mapping_reasons": disposition_info["mapping_reasons"],
        "disposition": disposition_info["disposition"],
        "weak_type": disposition_info["weak_type"],
        "proposed_cluster": disposition_info["proposed_cluster"],
        "source_package": disposition_info["source_package"],
        "source_path_after_mapping": disposition_info["source_path_after_mapping"],
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
        slot_meta["weak_cleanup_w2"] = {
            "cleanup_phase": "W-2",
            "proposed_cluster": mapping["proposed_cluster"],
            "proposed_role": mapping.get("proposed_role"),
            "source_package": mapping["source_package"],
        }
        fact["slot_meta"] = slot_meta
        promoted_rows.append(fact)

    promoted_rows.sort(key=lambda row: str(row["item_id"]))
    return promoted_rows


def render_disposition_note(summary: dict[str, Any]) -> str:
    class_counts = summary["actual_scope_counts_by_primary_classification"]
    cluster_counts = summary["proposed_cluster_counts"]
    weak_type_counts = summary["weak_type_counts"]
    disposition_counts = summary["disposition_counts"]
    return "\n".join(
        [
            "# W-2 Existing Cluster Absorption Note",
            "",
            "## Scope",
            "",
            f"- roadmap expected target count: `{summary['roadmap_expected_target_count']}`",
            f"- current artifact scope count: `{summary['actual_scope_row_count']}`",
            f"- scope delta vs roadmap: `{summary['actual_scope_row_count'] - summary['roadmap_expected_target_count']}`",
            "",
            "Current W-2 execution uses the current W-0 candidate inventory as authority.",
            "If this differs from earlier roadmap prose, the inventory artifact wins.",
            "",
            "## Actual scope by primary classification",
            "",
            *[f"- `{key}`: `{value}`" for key, value in class_counts.items()],
            "",
            "## Disposition",
            "",
            *[f"- `{key}`: `{value}`" for key, value in disposition_counts.items()],
            "",
            "Proposed clusters:",
            "",
            *(
                [f"- `{key}`: `{value}`" for key, value in cluster_counts.items()]
                if cluster_counts
                else ["- none"]
            ),
            "",
            "Weak-type counts:",
            "",
            *(
                [f"- `{key}`: `{value}`" for key, value in weak_type_counts.items()]
                if weak_type_counts
                else ["- none"]
            ),
            "",
            "## Interpretation",
            "",
            "This phase promotes only rows that can reuse an existing staged cluster without reopening 3-4 detail.",
            "Rows kept on identity fallback or sent to source backlog remain classification outputs only.",
            "",
        ]
    )


def build_w2_existing_cluster_absorption(
    *,
    w0_candidate_list_path: Path = W0_CANDIDATE_LIST_PATH,
    w0_baseline_manifest_path: Path = W0_BASELINE_MANIFEST_PATH,
    integrated_facts_path: Path = INTEGRATED_FACTS_PATH,
    b1_facts_path: Path = B1_DIR / "b1_consumable_facts.jsonl",
    b1_decisions_path: Path = B1_DIR / "b1_consumable_decisions.jsonl",
    b2_facts_path: Path = B2_DIR / "b2_literature_facts.jsonl",
    b2_decisions_path: Path = B2_DIR / "b2_literature_decisions.jsonl",
    b3_facts_path: Path = B3_DIR / "b3_resource_facts.jsonl",
    b3_decisions_path: Path = B3_DIR / "b3_resource_decisions.jsonl",
    b4_facts_path: Path = B4_DIR / "b4_residual_facts.jsonl",
    b4_decisions_path: Path = B4_DIR / "b4_residual_decisions.jsonl",
    c1re_facts_path: Path = C1RE_DIR / "c1re_utility_misc_facts.jsonl",
    c1re_decisions_path: Path = C1RE_DIR / "c1re_utility_misc_decisions.jsonl",
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
        and str(row.get("primary_classification") or "(missing)") != "(missing)"
        and not str(row.get("primary_classification") or "").startswith("Wearable.")
        and row.get("primary_classification") not in W1_TARGET_PRIMARY_CLASSES
    ]

    catalogs_by_package = {
        "B-1": cluster_catalog_from_package(
            facts_path=b1_facts_path,
            decisions_path=b1_decisions_path,
            package_id="B-1",
        ),
        "B-2": cluster_catalog_from_package(
            facts_path=b2_facts_path,
            decisions_path=b2_decisions_path,
            package_id="B-2",
        ),
        "B-3": cluster_catalog_from_package(
            facts_path=b3_facts_path,
            decisions_path=b3_decisions_path,
            package_id="B-3",
        ),
        "B-4": cluster_catalog_from_package(
            facts_path=b4_facts_path,
            decisions_path=b4_decisions_path,
            package_id="B-4",
        ),
        "C1-Re": cluster_catalog_from_package(
            facts_path=c1re_facts_path,
            decisions_path=c1re_decisions_path,
            package_id="C1-Re",
        ),
    }

    mapping_rows = [
        build_mapping_row(row=row, catalogs_by_package=catalogs_by_package) for row in target_rows
    ]
    mapping_rows.sort(key=lambda row: (row["primary_classification"], row["item_id"]))

    promoted_candidate_facts = build_promoted_candidate_facts(
        mapping_rows=mapping_rows,
        integrated_facts=integrated_facts,
    )

    actual_scope_counts: Counter[str] = Counter(
        str(row.get("primary_classification") or "(missing)") for row in target_rows
    )
    disposition_counts: Counter[str] = Counter(str(row["disposition"]) for row in mapping_rows)
    weak_type_counts: Counter[str] = Counter(
        str(row["weak_type"]) for row in mapping_rows if row.get("weak_type")
    )
    proposed_cluster_counts: Counter[str] = Counter(
        str(row["proposed_cluster"]) for row in mapping_rows if row.get("proposed_cluster")
    )

    summary = {
        "schema_version": "weak-active-cleanup-w2-existing-cluster-absorption-v0",
        "authority": {
            "w0_candidate_list": str(w0_candidate_list_path),
            "w0_baseline_manifest": str(w0_baseline_manifest_path),
            "integrated_facts": str(integrated_facts_path),
        },
        "scope_rule": {
            "candidate_family": "identity_fallback_active",
            "exclude_missing_primary_classification": True,
            "exclude_primary_classification_prefixes": ["Wearable."],
            "exclude_primary_classifications": sorted(W1_TARGET_PRIMARY_CLASSES),
        },
        "roadmap_expected_target_count": ROADMAP_EXPECTED_TARGET_COUNT,
        "actual_scope_row_count": len(target_rows),
        "actual_scope_counts_by_primary_classification": normalize_counter(actual_scope_counts),
        "promote_candidate_count": disposition_counts.get("promote_candidate", 0),
        "retain_identity_fallback_count": disposition_counts.get("retain_identity_fallback", 0),
        "source_backlog_candidate_count": disposition_counts.get("source_backlog_candidate", 0),
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
        "schema_version": "weak-active-cleanup-w2-existing-cluster-absorption-rows-v0",
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
    summary = build_w2_existing_cluster_absorption()
    print("weak-active cleanup W-2 existing cluster absorption generated")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
