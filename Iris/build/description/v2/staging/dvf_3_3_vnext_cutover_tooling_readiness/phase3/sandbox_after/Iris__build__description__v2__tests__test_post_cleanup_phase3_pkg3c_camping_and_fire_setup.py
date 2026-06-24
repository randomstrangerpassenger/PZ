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

from tools.build.build_post_cleanup_phase3_pkg3c_camping_and_fire_setup import (
    build_post_cleanup_phase3_pkg3c_camping_and_fire_setup,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg3CCampingAndFireSetupTest(unittest.TestCase):
    def test_build_pkg3c_promotes_only_tent_rows(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg3c_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            triage_rows_path = tmp / "pkg3_unclassified_triage_rows.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[59e16814924fd61f73d3c7c81cfaefb8].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[59e16814924fd61f73d3c7c81cfaefb8]
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[85bfc2486399d58ef98ef6c1f89435e7].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[85bfc2486399d58ef98ef6c1f89435e7]
            output_dir = tmp / "out"

            dump_json(
                triage_rows_path,
                {
                    "rows": [
                        {
                            "item_id": "camping.CampingTent",
                            "display_name": "Tent",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "camping_and_fire_setup",
                            "inferred_classification_label": "Tool.CampingAndFireSetup",
                            "followon_package_id": "PKG-3C",
                        },
                        {
                            "item_id": "camping.CampingTentKit",
                            "display_name": "Tent Kit",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "camping_and_fire_setup",
                            "inferred_classification_label": "Tool.CampingAndFireSetup",
                            "followon_package_id": "PKG-3C",
                        },
                        {
                            "item_id": "Base.FireWoodKit",
                            "display_name": "Kindling",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "camping_and_fire_setup",
                            "inferred_classification_label": "Tool.CampingAndFireSetup",
                            "followon_package_id": "PKG-3C",
                        },
                        {
                            "item_id": "Base.PercedWood",
                            "display_name": "Notched Wooden Plank",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "camping_and_fire_setup",
                            "inferred_classification_label": "Tool.CampingAndFireSetup",
                            "followon_package_id": "PKG-3C",
                        },
                        {
                            "item_id": "camping.CampfireKit",
                            "display_name": "Campfire Materials",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "camping_and_fire_setup",
                            "inferred_classification_label": "Tool.CampingAndFireSetup",
                            "followon_package_id": "PKG-3C",
                        },
                        {
                            "item_id": "camping.SteelAndFlint",
                            "display_name": "Flint and Steel",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "camping_and_fire_setup",
                            "inferred_classification_label": "Tool.CampingAndFireSetup",
                            "followon_package_id": "PKG-3C",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "SHELTER_SAMPLE",
                        "identity_hint": "재료",
                        "primary_use": "야영 준비 작업에서 임시 거처를 설치할 때 쓴다",
                        "acquisition_hint": "야영 장비와 함께 발견된다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "camping.CampingTent",
                        "identity_hint": "캠핑 용품",
                        "primary_use": None,
                        "acquisition_hint": "캠핑 장비 취급 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "camping.CampingTentKit",
                        "identity_hint": "캠핑 용품",
                        "primary_use": None,
                        "acquisition_hint": "캠핑 장비 취급 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.FireWoodKit",
                        "identity_hint": "캠핑 용품",
                        "primary_use": None,
                        "acquisition_hint": "캠핑 장비 취급 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.PercedWood",
                        "identity_hint": "캠핑 용품",
                        "primary_use": None,
                        "acquisition_hint": "나무 판재를 가공해 얻는다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "camping.CampfireKit",
                        "identity_hint": "캠핑 용품",
                        "primary_use": None,
                        "acquisition_hint": "캠핑 장비 취급 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "camping.SteelAndFlint",
                        "identity_hint": "도구",
                        "primary_use": "도구다",
                        "acquisition_hint": "캠핑 장비 취급 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "SHELTER_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_component",
                        "facts_ref": "SHELTER_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "field_shelter_setup",
                        "selected_role": "material",
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
                        "item_id": "camping.CampingTent",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "camping.CampingTent",
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
                        "hard_fail_codes": ["role_fallback_too_hollow"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "camping.CampingTentKit",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "camping.CampingTentKit",
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
                        "hard_fail_codes": ["role_fallback_too_hollow"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.FireWoodKit",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.FireWoodKit",
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
                        "hard_fail_codes": ["role_fallback_too_hollow"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.PercedWood",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.PercedWood",
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
                        "hard_fail_codes": ["role_fallback_too_hollow"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "camping.CampfireKit",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "camping.CampfireKit",
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
                        "hard_fail_codes": ["role_fallback_too_hollow"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "camping.SteelAndFlint",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "camping.SteelAndFlint",
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

            summary = build_post_cleanup_phase3_pkg3c_camping_and_fire_setup(
                triage_rows_path=triage_rows_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 6)
            self.assertEqual(summary["promote_candidate_count"], 2)
            self.assertEqual(summary["residual_backlog_count"], 4)
            self.assertEqual(summary["proposed_cluster_counts"]["field_shelter_setup"], 2)
            self.assertEqual(summary["projected_runtime_state_delta"]["active"], 2)
            self.assertEqual(summary["projected_runtime_state_delta"]["silent"], -2)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg3c_camping_and_fire_setup_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            facts_by_id = {row["item_id"]: row for row in promoted_facts}
            self.assertEqual(facts_by_id["camping.CampingTent"]["primary_use"], "야영 준비 작업에서 임시 거처를 설치할 때 쓴다")
            self.assertEqual(facts_by_id["camping.CampingTentKit"]["primary_use"], "야영 준비 작업에서 임시 거처를 설치할 때 쓴다")

            residual = json.loads((output_dir / "pkg3c_camping_and_fire_setup_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.FireWoodKit"]["backlog_bucket"], "campfire_material_cluster_absent")
            self.assertEqual(residual_by_id["Base.PercedWood"]["backlog_bucket"], "campfire_material_cluster_absent")
            self.assertEqual(residual_by_id["camping.CampfireKit"]["backlog_bucket"], "campfire_material_cluster_absent")
            self.assertEqual(residual_by_id["camping.SteelAndFlint"]["backlog_bucket"], "firestarter_tool_cluster_absent")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
