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

from tools.build.build_post_cleanup_phase3_pkg4_combat_devices_and_firearms import (
    build_post_cleanup_phase3_pkg4_combat_devices_and_firearms,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg4CombatDevicesAndFirearmsTest(unittest.TestCase):
    def test_build_pkg4_promotes_triggered_bombs_and_keeps_firearms_backlog(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg4_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            backlog_map_path = tmp / "weak_cleanup_to_source_backlog_map.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[b836df5994524da9a8d47c5f0348bc68].jsonl"
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[7d770d13d84116139c9adaa0b9614dfd].jsonl"
            output_dir = tmp / "out"

            dump_json(
                backlog_map_path,
                {
                    "rows": [
                        {
                            "item_id": "Base.Molotov",
                            "display_name": "Molotov Cocktail",
                            "candidate_family": "identity_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Combat.2-J",
                            "cleanup_phase": "W-2",
                        },
                        {
                            "item_id": "Base.PipeBombRemote",
                            "display_name": "Remote Pipe Bomb",
                            "candidate_family": "identity_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Combat.2-J",
                            "cleanup_phase": "W-3",
                        },
                        {
                            "item_id": "Base.SmokeBombTriggered",
                            "display_name": "Smoke Bomb with Timer",
                            "candidate_family": "identity_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Combat.2-J",
                            "cleanup_phase": "W-3",
                        },
                        {
                            "item_id": "Base.Pistol",
                            "display_name": "M9 Pistol",
                            "candidate_family": "identity_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "primary_classification": "Combat.2-G",
                            "cleanup_phase": "W-2",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "DEVICE_SAMPLE",
                        "identity_hint": "폭발물",
                        "primary_use": "폭발물 운용 작업에서 기폭 장치를 갖춘 폭발물을 설치할 때 다룬다",
                        "acquisition_hint": "폭발물을 개조해 얻는다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.Molotov",
                        "identity_hint": "폭발물",
                        "primary_use": "설치하거나 투척해 기폭하는 전투 작업에 쓰는 폭발물이다",
                        "acquisition_hint": "술병이나 빈 병, 천 조각과 휘발유로 제작한다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.PipeBombRemote",
                        "identity_hint": "폭발물",
                        "primary_use": "설치하거나 투척해 기폭하는 전투 작업에 쓰는 폭발물이다",
                        "acquisition_hint": "폭발물을 개조해 얻는다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.SmokeBombTriggered",
                        "identity_hint": "폭발물",
                        "primary_use": "설치하거나 투척해 기폭하는 전투 작업에 쓰는 폭발물이다",
                        "acquisition_hint": "폭발물을 개조해 얻는다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.Pistol",
                        "identity_hint": "근접 무기",
                        "primary_use": "근접 전투에 쓰는 무기다",
                        "acquisition_hint": "총기 매장과 은닉 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "DEVICE_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_output",
                        "facts_ref": "DEVICE_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "explosive_devices",
                        "selected_role": "output",
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
                        "item_id": "Base.Molotov",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Molotov",
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
                        "item_id": "Base.PipeBombRemote",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.PipeBombRemote",
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
                        "item_id": "Base.SmokeBombTriggered",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.SmokeBombTriggered",
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
                        "item_id": "Base.Pistol",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Pistol",
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
                        "hard_fail_codes": ["too_generic_use"],
                        "v9_warn": True,
                    },
                ],
            )

            summary = build_post_cleanup_phase3_pkg4_combat_devices_and_firearms(
                backlog_map_path=backlog_map_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 4)
            self.assertEqual(summary["promote_candidate_count"], 2)
            self.assertEqual(summary["residual_backlog_count"], 2)
            self.assertEqual(summary["proposed_cluster_counts"]["explosive_devices"], 2)
            self.assertEqual(summary["runtime_state_delta"]["active"], 0)
            self.assertEqual(summary["runtime_state_delta"]["silent"], 0)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg4_combat_devices_and_firearms_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual([row["item_id"] for row in promoted_facts], ["Base.PipeBombRemote", "Base.SmokeBombTriggered"])
            self.assertEqual(promoted_facts[0]["primary_use"], "폭발물 운용 작업에서 기폭 장치를 갖춘 폭발물을 설치할 때 다룬다")

            residual = json.loads((output_dir / "pkg4_combat_devices_and_firearms_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.Molotov"]["backlog_bucket"], "thrown_incendiary_cluster_absent")
            self.assertEqual(residual_by_id["Base.Pistol"]["backlog_bucket"], "handgun_firearm_cluster_absent")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
