from __future__ import annotations

import json
import shutil
import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.build_post_cleanup_phase3_pkg3a_construction_repair_materials import (
    build_post_cleanup_phase3_pkg3a_construction_repair_materials,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg3AConstructionRepairMaterialsTest(unittest.TestCase):
    def test_build_pkg3a_promotes_only_safe_material_rows(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg3a_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            triage_rows_path = tmp / "pkg3_unclassified_triage_rows.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[bc90772a80695c2de29f423d5caa14db].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[bc90772a80695c2de29f423d5caa14db]
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[75dd6c39324cec11d473f930226c614c].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[75dd6c39324cec11d473f930226c614c]
            output_dir = tmp / "out"

            dump_json(
                triage_rows_path,
                {
                    "rows": [
                        {
                            "item_id": "Base.Hinge",
                            "display_name": "Door Hinge",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "construction_repair_materials",
                            "inferred_classification_label": "Construction.RepairMaterials",
                            "followon_package_id": "PKG-3A",
                        },
                        {
                            "item_id": "Base.Pipe",
                            "display_name": "Plastic Pipe",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "construction_repair_materials",
                            "inferred_classification_label": "Construction.RepairMaterials",
                            "followon_package_id": "PKG-3A",
                        },
                        {
                            "item_id": "Base.ScrapMetal",
                            "display_name": "Scrap Metal",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "construction_repair_materials",
                            "inferred_classification_label": "Construction.RepairMaterials",
                            "followon_package_id": "PKG-3A",
                        },
                        {
                            "item_id": "Base.BarbedWire",
                            "display_name": "Barbed Wire",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "construction_repair_materials",
                            "inferred_classification_label": "Construction.RepairMaterials",
                            "followon_package_id": "PKG-3A",
                        },
                        {
                            "item_id": "Base.ConcretePowder",
                            "display_name": "Bag of Concrete Powder",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "construction_repair_materials",
                            "inferred_classification_label": "Construction.RepairMaterials",
                            "followon_package_id": "PKG-3A",
                        },
                        {
                            "item_id": "Base.Scotchtape",
                            "display_name": "Adhesive Tape",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "construction_repair_materials",
                            "inferred_classification_label": "Construction.RepairMaterials",
                            "followon_package_id": "PKG-3A",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "CONSTRUCTION_SAMPLE",
                        "identity_hint": "재료",
                        "primary_use": "건축 준비 작업에서 자재를 가공하거나 맞출 때 쓴다",
                        "acquisition_hint": "건축 자재 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "RECLAIM_SAMPLE",
                        "identity_hint": "쓸모없는 금속",
                        "primary_use": "자재 정리 작업에서 거친 재료나 남은 부품을 모아 다음 제작용으로 분류할 때 다룬다",
                        "acquisition_hint": "해체 현장에서 나온다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.Hinge",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "공사 자재 보관 장소와 작업장에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.Pipe",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "공사 자재 보관 장소와 작업장에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.ScrapMetal",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "공사 자재 보관 장소와 작업장에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.BarbedWire",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "공사 자재 보관 장소와 작업장에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.ConcretePowder",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "공사 자재 보관 장소와 작업장에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.Scotchtape",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "공사 자재 보관 장소와 작업장에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "CONSTRUCTION_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "CONSTRUCTION_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "construction_prep",
                        "selected_role": "tool",
                        "selection_path": "frequency",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": True,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": [],
                        "v9_warn": False,
                    },
                    {
                        "item_id": "RECLAIM_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "RECLAIM_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "reclaimed_material_sorting",
                        "selected_role": "item",
                        "selection_path": "frequency",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": True,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": [],
                        "v9_warn": False,
                    },
                    {
                        "item_id": "Base.Hinge",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Hinge",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_absent_keep_existing",
                        "use_source": "role_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "cluster_absent",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": False,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": ["too_generic_use"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.Pipe",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Pipe",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_absent_keep_existing",
                        "use_source": "role_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "cluster_absent",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": False,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": ["too_generic_use"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.ScrapMetal",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.ScrapMetal",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_absent_keep_existing",
                        "use_source": "role_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "cluster_absent",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": False,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": ["too_generic_use"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.BarbedWire",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.BarbedWire",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_absent_keep_existing",
                        "use_source": "role_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "cluster_absent",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": False,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": ["too_generic_use"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.ConcretePowder",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.ConcretePowder",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_absent_keep_existing",
                        "use_source": "role_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "cluster_absent",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": False,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": ["too_generic_use"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.Scotchtape",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Scotchtape",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_absent_keep_existing",
                        "use_source": "role_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "cluster_absent",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": False,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": ["too_generic_use"],
                        "v9_warn": True,
                    },
                ],
            )

            summary = build_post_cleanup_phase3_pkg3a_construction_repair_materials(
                triage_rows_path=triage_rows_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 6)
            self.assertEqual(summary["promote_candidate_count"], 3)
            self.assertEqual(summary["residual_backlog_count"], 3)
            self.assertEqual(summary["proposed_cluster_counts"]["construction_prep"], 2)
            self.assertEqual(summary["proposed_cluster_counts"]["reclaimed_material_sorting"], 1)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg3a_construction_repair_materials_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            facts_by_id = {row["item_id"]: row for row in promoted_facts}
            self.assertEqual(facts_by_id["Base.Hinge"]["primary_use"], "건축 준비 작업에서 자재를 가공하거나 맞출 때 쓴다")
            self.assertEqual(facts_by_id["Base.Pipe"]["primary_use"], "건축 준비 작업에서 자재를 가공하거나 맞출 때 쓴다")
            self.assertEqual(facts_by_id["Base.ScrapMetal"]["primary_use"], "자재 정리 작업에서 거친 재료나 남은 부품을 모아 다음 제작용으로 분류할 때 다룬다")

            residual = json.loads((output_dir / "pkg3a_construction_repair_materials_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.BarbedWire"]["backlog_bucket"], "fence_material_cluster_absent")
            self.assertEqual(residual_by_id["Base.ConcretePowder"]["backlog_bucket"], "powder_mixing_cluster_absent")
            self.assertEqual(residual_by_id["Base.Scotchtape"]["backlog_bucket"], "adhesive_repair_context_too_broad")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
