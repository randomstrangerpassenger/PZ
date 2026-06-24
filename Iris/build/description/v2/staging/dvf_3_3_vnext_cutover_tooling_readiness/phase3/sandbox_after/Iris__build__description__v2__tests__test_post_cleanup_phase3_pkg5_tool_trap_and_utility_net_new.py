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

from tools.build.build_post_cleanup_phase3_pkg5_tool_trap_and_utility_net_new import (
    build_post_cleanup_phase3_pkg5_tool_trap_and_utility_net_new,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg5ToolTrapAndUtilityNetNewTest(unittest.TestCase):
    def test_build_pkg5_promotes_full_kettle_and_keeps_other_tool_cohorts_on_backlog(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg5_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            backlog_map_path = tmp / "weak_cleanup_to_source_backlog_map.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[dd071bf24b05e93f3a1b091ae5a59103].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[dd071bf24b05e93f3a1b091ae5a59103]
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[8d8be7d4c749faa7ba7cf2df2f0026c0].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[8d8be7d4c749faa7ba7cf2df2f0026c0]
            output_dir = tmp / "out"

            dump_json(
                backlog_map_path,
                {
                    "rows": [
                        {
                            "item_id": "Base.FullKettle",
                            "display_name": "Full Kettle",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "primary_classification": "Tool.1-D",
                            "cleanup_phase": "W-5",
                        },
                        {
                            "item_id": "Base.TrapBox",
                            "display_name": "Trap Box",
                            "candidate_family": "identity_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Tool.1-G",
                            "cleanup_phase": "W-2",
                        },
                        {
                            "item_id": "Base.Lighter",
                            "display_name": "Lighter",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "primary_classification": "Tool.1-H",
                            "cleanup_phase": "W-5",
                        },
                        {
                            "item_id": "Radio.RadioMakeShift",
                            "display_name": "Makeshift Radio",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "primary_classification": "Tool.1-I",
                            "cleanup_phase": "W-5",
                        },
                        {
                            "item_id": "farming.WateredCan",
                            "display_name": "Watered Can",
                            "candidate_family": "identity_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Tool.1-E",
                            "cleanup_phase": "W-2",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "Base.Pot",
                        "identity_hint": "조리 용기",
                        "primary_use": "조리 준비 작업에서 재료를 담거나 섞고 익히기 전에 다룰 때 쓴다",
                        "acquisition_hint": None,
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.FullKettle",
                        "identity_hint": "수원",
                        "primary_use": None,
                        "acquisition_hint": "빈 용기에 물을 채워 얻는다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.TrapBox",
                        "identity_hint": "덫 사냥 용품",
                        "primary_use": "덫 설치나 회수 작업에 쓰는 도구다",
                        "acquisition_hint": "제작으로 얻는다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.Lighter",
                        "identity_hint": "조명 기구",
                        "primary_use": None,
                        "acquisition_hint": "차량과 책상, 담배 판매대에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Radio.RadioMakeShift",
                        "identity_hint": "무전기",
                        "primary_use": None,
                        "acquisition_hint": "전자 부품으로 제작한다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "farming.WateredCan",
                        "identity_hint": "원예 용품",
                        "primary_use": "재배와 관리 작업에 쓰는 원예 용품이다",
                        "acquisition_hint": "원예 용품 취급 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "Base.Pot",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Pot",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "cooking_prep",
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
                        "item_id": "Base.FullKettle",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.FullKettle",
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
                        "item_id": "Base.TrapBox",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.TrapBox",
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
                        "item_id": "Base.Lighter",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Lighter",
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
                        "item_id": "Radio.RadioMakeShift",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Radio.RadioMakeShift",
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
                        "item_id": "farming.WateredCan",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "farming.WateredCan",
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
                ],
            )

            summary = build_post_cleanup_phase3_pkg5_tool_trap_and_utility_net_new(
                backlog_map_path=backlog_map_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 5)
            self.assertEqual(summary["promote_candidate_count"], 1)
            self.assertEqual(summary["residual_backlog_count"], 4)
            self.assertEqual(summary["identity_hint_override_count"], 1)
            self.assertEqual(summary["proposed_cluster_counts"]["cooking_prep"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["active"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["silent"], -1)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg5_tool_trap_and_utility_net_new_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual([row["item_id"] for row in promoted_facts], ["Base.FullKettle"])
            self.assertEqual(promoted_facts[0]["identity_hint"], "조리 용기")
            self.assertEqual(promoted_facts[0]["primary_use"], "조리 준비 작업에서 재료를 담거나 섞고 익히기 전에 다룰 때 쓴다")

            residual = json.loads((output_dir / "pkg5_tool_trap_and_utility_net_new_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.TrapBox"]["backlog_bucket"], "trap_tool_cluster_absent")
            self.assertEqual(residual_by_id["Base.Lighter"]["backlog_bucket"], "ignition_firestarter_cluster_absent")
            self.assertEqual(residual_by_id["Radio.RadioMakeShift"]["backlog_bucket"], "improvised_radio_cluster_absent")
            self.assertEqual(residual_by_id["farming.WateredCan"]["backlog_bucket"], "watering_can_cluster_absent")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
