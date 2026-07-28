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
B2_DIR = SOURCE_COVERAGE_DIR / "b2_literature_package"
C1B_DIR = SOURCE_COVERAGE_DIR / "c1b_portable_storage_package"

OUTPUT_DIR = ROOT / "staging" / "weak_active_cleanup" / "w5_role_fallback_cleanup"
SUMMARY_PATH = OUTPUT_DIR / "w5_role_fallback_cleanup_summary.json"
MAPPING_PATH = OUTPUT_DIR / "w5_role_fallback_cleanup.json"
PROMOTED_FACTS_PATH = OUTPUT_DIR / "w5_role_fallback_promoted_candidate_facts.jsonl"
NOTE_PATH = OUTPUT_DIR / "w5_role_fallback_cleanup_note.md"


def active_transition_reason(row: dict[str, Any]) -> str:
    display_category = str(row.get("display_category") or "")
    if display_category == "Water":
        return "Water rows have a clear hydration or utility context, so primary-use generation should be reviewed in W-6."
    if display_category == "Fishing":
        return "Fishing rows have obvious activity context and should be reconsidered for activation rather than kept silent."
    if display_category in {"Camping", "Gardening", "Communications", "LightSource", "Household", "Junk", "Security", "VehicleMaintenance", "WaterContainer", "Food", "Literature", "FirstAid", "WeaponCrafted"}:
        return "This silent row has enough item-level meaning to justify active-transition review in W-6."
    return "Primary-use generation appears feasible enough to keep this row in active-transition review rather than silent retention."


def build_mapping_row(
    *,
    row: dict[str, Any],
    container_catalog: dict[str, dict[str, Any]],
    literature_catalog: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    family = str(row.get("candidate_family") or "")
    mapping: dict[str, Any] = {
        "item_id": row["item_id"],
        "display_name": row.get("display_name"),
        "display_category": row.get("display_category"),
        "primary_classification": row.get("primary_classification"),
        "identity_hint": row.get("identity_hint"),
        "old_primary_use": row.get("primary_use"),
        "candidate_family": family,
    }

    if family == "role_fallback_active":
        if str(row.get("display_category") or "") == "Container":
            cluster_info = container_catalog["container_storage"]
            mapping.update(
                {
                    "disposition": "promote_candidate",
                    "next_phase": None,
                    "weak_type": None,
                    "proposed_cluster": "container_storage",
                    "source_package": "C1-B",
                    "source_path_after_mapping": "cluster_summary",
                    "proposed_primary_use": cluster_info["canonical_primary_use"],
                    "proposed_role": cluster_info["canonical_role"],
                    "rationale": "Container rows should not stay on hollow role fallback when an existing storage cluster is available.",
                }
            )
            return mapping
        if row["item_id"] == "Base.SheetRope":
            mapping.update(
                {
                    "disposition": "retain_identity_fallback",
                    "next_phase": None,
                    "weak_type": "W2",
                    "proposed_cluster": None,
                    "source_package": None,
                    "source_path_after_mapping": "identity_fallback",
                    "proposed_primary_use": None,
                    "proposed_role": None,
                    "rationale": "Sheet rope behaves like the rope lane: identity-level meaning is retainable, but no representative cluster is justified.",
                }
            )
            return mapping
        mapping.update(
            {
                "disposition": "source_backlog_candidate",
                "next_phase": None,
                "weak_type": "W3",
                "proposed_cluster": None,
                "source_package": None,
                "source_path_after_mapping": "role_fallback",
                "proposed_primary_use": None,
                "proposed_role": None,
                "rationale": "This active row still has only a hollow role fallback and needs new source work rather than forced wording.",
            }
        )
        return mapping

    if family == "role_fallback_silent":
        if str(row.get("primary_classification") or "") == "Literature.5-B":
            cluster_info = literature_catalog["study_reference"]
            mapping.update(
                {
                    "disposition": "promote_candidate",
                    "next_phase": None,
                    "weak_type": None,
                    "proposed_cluster": "study_reference",
                    "source_package": "B-2",
                    "source_path_after_mapping": "cluster_summary",
                    "proposed_primary_use": cluster_info["canonical_primary_use"],
                    "proposed_role": cluster_info["canonical_role"],
                    "rationale": "These skill-book rows already fit the existing study-reference cluster and should leave silent state.",
                }
            )
            return mapping
        mapping.update(
            {
                "disposition": "active_transition_candidate",
                "next_phase": "W-6",
                "weak_type": None,
                "proposed_cluster": None,
                "source_package": None,
                "source_path_after_mapping": None,
                "proposed_primary_use": None,
                "proposed_role": None,
                "rationale": active_transition_reason(row),
            }
        )
        return mapping

    mapping.update(
        {
            "disposition": "unhandled",
            "next_phase": None,
            "weak_type": None,
            "proposed_cluster": None,
            "source_package": None,
            "source_path_after_mapping": None,
            "proposed_primary_use": None,
            "proposed_role": None,
            "rationale": "Unexpected candidate family.",
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
        slot_meta["weak_cleanup_w5"] = {
            "cleanup_phase": "W-5",
            "proposed_cluster": mapping["proposed_cluster"],
            "proposed_role": mapping["proposed_role"],
            "source_package": mapping["source_package"],
            "candidate_family": mapping["candidate_family"],
        }
        fact["slot_meta"] = slot_meta
        promoted_rows.append(fact)

    promoted_rows.sort(key=lambda row: str(row["item_id"]))
    return promoted_rows


def render_note(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# W-5 Role Fallback Cleanup Note",
            "",
            f"- active role-fallback rows: `{summary['active_row_count']}`",
            f"- silent role-fallback rows: `{summary['silent_row_count']}`",
            f"- total W-5 scope: `{summary['actual_scope_row_count']}`",
            "",
            "Disposition counts:",
            "",
            *[f"- `{key}`: `{value}`" for key, value in summary["disposition_counts"].items()],
            "",
            "Promoted clusters:",
            "",
            *(
                [f"- `{key}`: `{value}`" for key, value in summary["proposed_cluster_counts"].items()]
                if summary["proposed_cluster_counts"]
                else ["- none"]
            ),
            "",
            "Role-fallback silent rows are not rewritten directly in this phase.",
            "Rows marked `active_transition_candidate` move into W-6 for semantic legitimacy review before any runtime change.",
            "",
        ]
    )


def build_w5_role_fallback_cleanup(
    *,
    w0_candidate_list_path: Path = W0_CANDIDATE_LIST_PATH,
    w0_baseline_manifest_path: Path = W0_BASELINE_MANIFEST_PATH,
    integrated_facts_path: Path = INTEGRATED_FACTS_PATH,
    b2_facts_path: Path = B2_DIR / "b2_literature_facts.jsonl",
    b2_decisions_path: Path = B2_DIR / "b2_literature_decisions.jsonl",
    c1b_facts_path: Path = C1B_DIR / "c1b_portable_storage_facts.jsonl",
    c1b_decisions_path: Path = C1B_DIR / "c1b_portable_storage_decisions.jsonl",
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    candidate_payload = load_json(w0_candidate_list_path)
    baseline_manifest = load_json(w0_baseline_manifest_path)
    integrated_facts = load_jsonl(integrated_facts_path)

    target_rows = [
        row
        for row in candidate_payload["rows"]
        if row.get("candidate_family") in {"role_fallback_active", "role_fallback_silent"}
    ]

    literature_catalog = cluster_catalog_from_package(
        facts_path=b2_facts_path,
        decisions_path=b2_decisions_path,
        package_id="B-2",
    )
    container_catalog = cluster_catalog_from_package(
        facts_path=c1b_facts_path,
        decisions_path=c1b_decisions_path,
        package_id="C1-B",
    )

    mapping_rows = [
        build_mapping_row(
            row=row,
            container_catalog=container_catalog,
            literature_catalog=literature_catalog,
        )
        for row in target_rows
    ]
    mapping_rows.sort(key=lambda row: (row["candidate_family"], str(row.get("display_category") or ""), row["item_id"]))

    promoted_candidate_facts = build_promoted_candidate_facts(
        mapping_rows=mapping_rows,
        integrated_facts=integrated_facts,
    )

    active_row_count = sum(1 for row in mapping_rows if row["candidate_family"] == "role_fallback_active")
    silent_row_count = sum(1 for row in mapping_rows if row["candidate_family"] == "role_fallback_silent")
    disposition_counts = Counter(str(row["disposition"]) for row in mapping_rows)
    weak_type_counts = Counter(str(row["weak_type"]) for row in mapping_rows if row.get("weak_type"))
    proposed_cluster_counts = Counter(
        str(row["proposed_cluster"]) for row in mapping_rows if row.get("proposed_cluster")
    )
    next_phase_counts = Counter(str(row["next_phase"]) for row in mapping_rows if row.get("next_phase"))

    summary = {
        "schema_version": "weak-active-cleanup-w5-role-fallback-cleanup-v0",
        "authority": {
            "w0_candidate_list": str(w0_candidate_list_path),
            "w0_baseline_manifest": str(w0_baseline_manifest_path),
            "integrated_facts": str(integrated_facts_path),
        },
        "actual_scope_row_count": len(mapping_rows),
        "active_row_count": active_row_count,
        "silent_row_count": silent_row_count,
        "disposition_counts": normalize_counter(disposition_counts),
        "weak_type_counts": normalize_counter(weak_type_counts),
        "proposed_cluster_counts": normalize_counter(proposed_cluster_counts),
        "next_phase_counts": normalize_counter(next_phase_counts),
        "w0_candidate_scope_counts": baseline_manifest.get("baseline_counts", {}).get("candidate_family_counts"),
        "output_paths": {
            "mapping": str(output_dir / MAPPING_PATH.name),
            "promoted_candidate_facts": str(output_dir / PROMOTED_FACTS_PATH.name),
            "note": str(output_dir / NOTE_PATH.name),
        },
    }

    mapping_payload = {
        "schema_version": "weak-active-cleanup-w5-role-fallback-cleanup-rows-v0",
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
    summary = build_w5_role_fallback_cleanup()
    print("weak-active cleanup W-5 role fallback cleanup generated")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
