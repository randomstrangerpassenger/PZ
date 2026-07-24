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

from tools.build.build_post_cleanup_phase3_pkg1_resource4e import (
    build_post_cleanup_phase3_pkg1_resource4e,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg1Resource4ETest(unittest.TestCase):
    def test_build_pkg1_resource4e_promotes_only_safe_reuse_rows(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg1_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            backlog_map_path = tmp / "weak_cleanup_to_source_backlog_map.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[59dca9e5d27835f7873b52fed0d917be].jsonl"
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[af200262c865de689e351bad5e82eef3].jsonl"
            output_dir = tmp / "out"

            dump_json(
                backlog_map_path,
                {
                    "rows": [
                        {
                            "item_id": "Base.LightBulbBlue",
                            "display_name": "Blue Light Bulb",
                            "primary_classification": "Resource.4-E",
                            "candidate_family": "identity_fallback_active",
                            "cleanup_phase": "W-3",
                        },
                        {
                            "item_id": "Base.WristWatch_Right_ClassicBlack",
                            "display_name": "Classic Wrist Watch with Black Strap",
                            "primary_classification": "Resource.4-E",
                            "candidate_family": "identity_fallback_active",
                            "cleanup_phase": "W-3",
                        },
                        {
                            "item_id": "Base.FlameTrapRemote",
                            "display_name": "Remote Flame Trap",
                            "primary_classification": "Resource.4-E",
                            "candidate_family": "identity_fallback_active",
                            "cleanup_phase": "W-3",
                        },
                        {
                            "item_id": "Base.PaintBlack",
                            "display_name": "Black Paint",
                            "primary_classification": "Resource.4-E",
                            "candidate_family": "identity_fallback_active",
                            "cleanup_phase": "W-3",
                        },
                        {
                            "item_id": "Base.WeldingRods",
                            "display_name": "Welding Rods",
                            "primary_classification": "Resource.4-E",
                            "candidate_family": "identity_fallback_active",
                            "cleanup_phase": "W-3",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "ELECTRONICS_SAMPLE",
                        "identity_hint": "전자 부품이다",
                        "primary_use": "전자 작업에서 기기를 분해하거나 회로를 맞출 때 다룬다",
                        "acquisition_hint": "전자 장비에서 분해한다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "WATCH_SAMPLE",
                        "identity_hint": "손목시계다",
                        "primary_use": "착용 작업에서 손목에 시계를 채워 시간을 확인하거나 알람을 맞출 때 다룬다",
                        "acquisition_hint": "액세서리 상자에서 발견된다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "EXPLOSIVE_SAMPLE",
                        "identity_hint": "폭발 장치다",
                        "primary_use": "폭발물 운용 작업에서 기폭 장치를 갖춘 폭발물을 설치할 때 다룬다",
                        "acquisition_hint": "제작으로 얻는다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.LightBulbBlue",
                        "identity_hint": "전구다",
                        "primary_use": "전구다",
                        "acquisition_hint": "전기 설비에서 발견된다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.WristWatch_Right_ClassicBlack",
                        "identity_hint": "손목시계다",
                        "primary_use": "손목시계다",
                        "acquisition_hint": "액세서리에서 발견된다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.FlameTrapRemote",
                        "identity_hint": "폭발물이다",
                        "primary_use": "폭발물이다",
                        "acquisition_hint": "제작으로 얻는다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.PaintBlack",
                        "identity_hint": "페인트다",
                        "primary_use": "페인트다",
                        "acquisition_hint": "공사 자재 보관소에서 발견된다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "Base.WeldingRods",
                        "identity_hint": "용접 재료다",
                        "primary_use": "용접 재료다",
                        "acquisition_hint": "금속 작업 공간에서 발견된다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "ELECTRONICS_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_component",
                        "facts_ref": "ELECTRONICS_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "electronics_assembly",
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
                        "item_id": "WATCH_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "WATCH_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "wristwatch_wear",
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
                        "item_id": "EXPLOSIVE_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_output",
                        "facts_ref": "EXPLOSIVE_SAMPLE",
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
                        "item_id": "Base.LightBulbBlue",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_component",
                        "facts_ref": "Base.LightBulbBlue",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "identity_fallback_keep_existing",
                        "use_source": "identity_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "frequency",
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
                        "item_id": "Base.WristWatch_Right_ClassicBlack",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.WristWatch_Right_ClassicBlack",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "identity_fallback_keep_existing",
                        "use_source": "identity_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "frequency",
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
                        "item_id": "Base.FlameTrapRemote",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_output",
                        "facts_ref": "Base.FlameTrapRemote",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "identity_fallback_keep_existing",
                        "use_source": "identity_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "frequency",
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
                        "item_id": "Base.PaintBlack",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.PaintBlack",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "identity_fallback_keep_existing",
                        "use_source": "identity_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "frequency",
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
                        "item_id": "Base.WeldingRods",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.WeldingRods",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "identity_fallback_keep_existing",
                        "use_source": "identity_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "frequency",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": False,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": [],
                        "v9_warn": False,
                    },
                ],
            )

            summary = build_post_cleanup_phase3_pkg1_resource4e(
                backlog_map_path=backlog_map_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 5)
            self.assertEqual(summary["promote_candidate_count"], 3)
            self.assertEqual(summary["residual_backlog_count"], 2)
            self.assertEqual(summary["proposed_cluster_counts"]["electronics_assembly"], 1)
            self.assertEqual(summary["proposed_cluster_counts"]["wristwatch_wear"], 1)
            self.assertEqual(summary["proposed_cluster_counts"]["explosive_devices"], 1)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg1_resource4e_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            facts_by_id = {row["item_id"]: row for row in promoted_facts}
            self.assertEqual(facts_by_id["Base.LightBulbBlue"]["primary_use"], "전자 작업에서 기기를 분해하거나 회로를 맞출 때 다룬다")
            self.assertEqual(facts_by_id["Base.WristWatch_Right_ClassicBlack"]["primary_use"], "착용 작업에서 손목에 시계를 채워 시간을 확인하거나 알람을 맞출 때 다룬다")
            self.assertEqual(facts_by_id["Base.FlameTrapRemote"]["primary_use"], "폭발물 운용 작업에서 기폭 장치를 갖춘 폭발물을 설치할 때 다룬다")

            promoted_decisions = [
                json.loads(line)
                for line in (output_dir / "pkg1_resource4e_promoted_candidate_decisions.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            decisions_by_id = {row["item_id"]: row for row in promoted_decisions}
            self.assertEqual(decisions_by_id["Base.LightBulbBlue"]["compose_profile"], "interaction_component")
            self.assertEqual(decisions_by_id["Base.WristWatch_Right_ClassicBlack"]["compose_profile"], "interaction_tool")
            self.assertEqual(decisions_by_id["Base.FlameTrapRemote"]["compose_profile"], "interaction_output")
            self.assertEqual(decisions_by_id["Base.FlameTrapRemote"]["use_source"], "cluster_summary")

            residual = json.loads((output_dir / "pkg1_resource4e_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.PaintBlack"]["backlog_bucket"], "painting_cluster_absent")
            self.assertEqual(residual_by_id["Base.WeldingRods"]["backlog_bucket"], "metalwork_material_role_mismatch")

            rendered = json.loads((output_dir / "pkg1_resource4e_promoted_candidate.rendered.json").read_text(encoding="utf-8"))
            self.assertEqual(rendered["meta"]["stats"]["total"], 3)
            self.assertIn("Base.LightBulbBlue", rendered["entries"])
            self.assertIn("Base.WristWatch_Right_ClassicBlack", rendered["entries"])
            self.assertIn("Base.FlameTrapRemote", rendered["entries"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
