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

from tools.build.build_post_cleanup_phase3_pkg6_residual_tail import (
    build_post_cleanup_phase3_pkg6_residual_tail,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg6ResidualTailTest(unittest.TestCase):
    def test_build_pkg6_promotes_bucket_water_and_bleach_only(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg6_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            backlog_map_path = tmp / "weak_cleanup_to_source_backlog_map.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[e403d8b1a57cbb35c7f5f81a0568084b].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[e403d8b1a57cbb35c7f5f81a0568084b]
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[00ef7fe9a578dbbd4e716f868717bb43].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[00ef7fe9a578dbbd4e716f868717bb43]
            output_dir = tmp / "out"

            dump_json(
                backlog_map_path,
                {
                    "rows": [
                        {
                            "item_id": "Base.BucketWaterFull",
                            "display_name": "Bucket of Water",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "primary_classification": "Resource.4-A",
                            "cleanup_phase": "W-6",
                        },
                        {
                            "item_id": "Base.Bleach",
                            "display_name": "Bleach",
                            "candidate_family": "identity_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Combat.2-F",
                            "cleanup_phase": "W-1",
                        },
                        {
                            "item_id": "Base.Notebook",
                            "display_name": "Notebook",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "primary_classification": "Literature.5-D",
                            "cleanup_phase": "W-6",
                        },
                        {
                            "item_id": "Base.SheetPaper2",
                            "display_name": "Paper",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "primary_classification": "Literature.5-D",
                            "cleanup_phase": "W-6",
                        },
                        {
                            "item_id": "Base.PlasterPowder",
                            "display_name": "Plaster Powder",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Resource.4-A",
                            "cleanup_phase": "W-2",
                        },
                        {
                            "item_id": "Base.LeatherStrips",
                            "display_name": "Leather Strips",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Consumable.3-C",
                            "cleanup_phase": "W-5",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "Base.BucketEmpty",
                        "identity_hint": "물통",
                        "primary_use": "보관 작업에서 소지품이나 내용물을 담아 휴대하거나 나눠 옮길 때 다룬다",
                        "acquisition_hint": "물 양동이를 비워 구한다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.CleaningLiquid",
                        "identity_hint": "세정액",
                        "primary_use": "생활 관리 작업에서 몸과 주변을 닦고 정리하거나 실내에 필요한 소모품을 챙길 때 다룬다",
                        "acquisition_hint": None,
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.BucketWaterFull",
                        "identity_hint": "수원",
                        "primary_use": None,
                        "acquisition_hint": "양동이에 물을 담아 만든다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.Bleach",
                        "identity_hint": "생활 소모품",
                        "primary_use": "일반 소비 작업에 쓰는 생활 소모품이다",
                        "acquisition_hint": None,
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.Notebook",
                        "identity_hint": "서적",
                        "primary_use": None,
                        "acquisition_hint": "문구 매대에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.SheetPaper2",
                        "identity_hint": "서적",
                        "primary_use": None,
                        "acquisition_hint": "사무용품 보관함에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.PlasterPowder",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "건축 자재 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.LeatherStrips",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "가죽 의류를 찢어 얻는다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "Base.BucketEmpty",
                        "state": "active",
                        "reason_code": "POST_CLEANUP_ADOPTED",
                        "compose_profile": "interaction_output",
                        "facts_ref": "Base.BucketEmpty",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "phase2_adoption_overlay",
                        "use_source": "cluster_summary",
                        "selected_cluster": "container_storage",
                        "selected_role": "output",
                        "selection_path": "phase2_adoption",
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
                        "item_id": "Base.CleaningLiquid",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.CleaningLiquid",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "household_upkeep_supply",
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
                        "item_id": "Base.BucketWaterFull",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.BucketWaterFull",
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
                        "cluster_policy_status": "policy_excluded",
                        "policy_excluded_reason_codes": ["action_only_not_representative"],
                        "hard_fail_codes": ["role_fallback_too_hollow"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.Bleach",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Bleach",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_absent_keep_existing",
                        "use_source": "identity_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "cluster_absent",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": False,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": [],
                        "v9_warn": False,
                    },
                    {
                        "item_id": "Base.Notebook",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Notebook",
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
                        "item_id": "Base.SheetPaper2",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.SheetPaper2",
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
                        "item_id": "Base.PlasterPowder",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.PlasterPowder",
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
                        "cluster_policy_status": "policy_excluded",
                        "policy_excluded_reason_codes": ["niche_recipe_not_representative"],
                        "hard_fail_codes": ["too_generic_use", "role_fallback_too_hollow"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.LeatherStrips",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.LeatherStrips",
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
                        "hard_fail_codes": ["too_generic_use", "role_fallback_too_hollow"],
                        "v9_warn": True,
                    },
                ],
            )

            summary = build_post_cleanup_phase3_pkg6_residual_tail(
                backlog_map_path=backlog_map_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 6)
            self.assertEqual(summary["promote_candidate_count"], 2)
            self.assertEqual(summary["residual_backlog_count"], 4)
            self.assertEqual(summary["identity_hint_override_count"], 2)
            self.assertEqual(summary["proposed_cluster_counts"]["container_storage"], 1)
            self.assertEqual(summary["proposed_cluster_counts"]["household_upkeep_supply"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["active"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["silent"], -1)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg6_residual_tail_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            promoted_by_id = {row["item_id"]: row for row in promoted_facts}
            self.assertEqual(promoted_by_id["Base.BucketWaterFull"]["identity_hint"], "물통")
            self.assertEqual(promoted_by_id["Base.Bleach"]["identity_hint"], "표백제")
            self.assertEqual(promoted_by_id["Base.BucketWaterFull"]["primary_use"], "보관 작업에서 소지품이나 내용물을 담아 휴대하거나 나눠 옮길 때 다룬다")
            self.assertEqual(promoted_by_id["Base.Bleach"]["primary_use"], "생활 관리 작업에서 몸과 주변을 닦고 정리하거나 실내에 필요한 소모품을 챙길 때 다룬다")

            residual = json.loads((output_dir / "pkg6_residual_tail_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.Notebook"]["backlog_bucket"], "writing_material_cluster_absent")
            self.assertEqual(residual_by_id["Base.SheetPaper2"]["backlog_bucket"], "writing_material_cluster_absent")
            self.assertEqual(residual_by_id["Base.PlasterPowder"]["backlog_bucket"], "powder_mixing_cluster_absent")
            self.assertEqual(residual_by_id["Base.LeatherStrips"]["backlog_bucket"], "leather_strip_multiuse_cluster_absent")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
