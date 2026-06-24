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

from tools.build.build_post_cleanup_phase3_pkg3d_water_and_container_handling import (
    build_post_cleanup_phase3_pkg3d_water_and_container_handling,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg3DWaterAndContainerHandlingTest(unittest.TestCase):
    def test_build_pkg3d_promotes_only_empty_paint_bucket(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg3d_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            triage_rows_path = tmp / "pkg3_unclassified_triage_rows.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[b752e5e60a3d613a82c90f89df9358fb].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[b752e5e60a3d613a82c90f89df9358fb]
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[b66d73d33ba61fa5ac46fb93806fc252].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[b66d73d33ba61fa5ac46fb93806fc252]
            output_dir = tmp / "out"

            dump_json(
                triage_rows_path,
                {
                    "rows": [
                        {
                            "item_id": "Base.PaintbucketEmpty",
                            "display_name": "Empty Paint Bucket",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "water_and_container_handling",
                            "inferred_classification_label": "Resource.WaterAndContainerHandling",
                            "followon_package_id": "PKG-3D",
                        },
                        {
                            "item_id": "Base.WaterBleachBottle",
                            "display_name": "Bleach Bottle With Water",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "water_and_container_handling",
                            "inferred_classification_label": "Resource.WaterAndContainerHandling",
                            "followon_package_id": "PKG-3D",
                        },
                        {
                            "item_id": "Base.WaterBowl",
                            "display_name": "Bowl of Water",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "water_and_container_handling",
                            "inferred_classification_label": "Resource.WaterAndContainerHandling",
                            "followon_package_id": "PKG-3D",
                        },
                        {
                            "item_id": "Base.WaterPaintbucket",
                            "display_name": "Paint Bucket With Water",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "water_and_container_handling",
                            "inferred_classification_label": "Resource.WaterAndContainerHandling",
                            "followon_package_id": "PKG-3D",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "EMPTY_SAMPLE",
                        "identity_hint": "빈 깡통",
                        "primary_use": "빈 용기 정리 작업에서 남은 캔이나 용기를 비우고 따로 모아 다시 쓰거나 처리할 때 다룬다",
                        "acquisition_hint": "주방에서 발견된다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.PaintbucketEmpty",
                        "identity_hint": "재료",
                        "primary_use": "재료다",
                        "acquisition_hint": "공사 자재 보관 장소와 작업장에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.WaterBleachBottle",
                        "identity_hint": "수원",
                        "primary_use": None,
                        "acquisition_hint": "빈 용기에 물을 담아 얻는다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.WaterBowl",
                        "identity_hint": "수원",
                        "primary_use": None,
                        "acquisition_hint": "빈 용기에 물을 담아 얻는다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.WaterPaintbucket",
                        "identity_hint": "수원",
                        "primary_use": None,
                        "acquisition_hint": "빈 용기에 물을 담아 얻는다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "EMPTY_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "EMPTY_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "empty_container_reuse",
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
                        "item_id": "Base.PaintbucketEmpty",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.PaintbucketEmpty",
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
                        "hard_fail_codes": ["too_generic_use"],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "Base.WaterBleachBottle",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.WaterBleachBottle",
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
                        "item_id": "Base.WaterBowl",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.WaterBowl",
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
                        "item_id": "Base.WaterPaintbucket",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.WaterPaintbucket",
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

            summary = build_post_cleanup_phase3_pkg3d_water_and_container_handling(
                triage_rows_path=triage_rows_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 4)
            self.assertEqual(summary["promote_candidate_count"], 1)
            self.assertEqual(summary["residual_backlog_count"], 3)
            self.assertEqual(summary["proposed_cluster_counts"]["empty_container_reuse"], 1)
            self.assertEqual(summary["runtime_state_delta"]["active"], 0)
            self.assertEqual(summary["runtime_state_delta"]["silent"], 0)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg3d_water_and_container_handling_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(promoted_facts), 1)
            self.assertEqual(promoted_facts[0]["item_id"], "Base.PaintbucketEmpty")
            self.assertEqual(promoted_facts[0]["primary_use"], "빈 용기 정리 작업에서 남은 캔이나 용기를 비우고 따로 모아 다시 쓰거나 처리할 때 다룬다")

            residual = json.loads((output_dir / "pkg3d_water_and_container_handling_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.WaterBleachBottle"]["backlog_bucket"], "filled_utility_water_container_cluster_absent")
            self.assertEqual(residual_by_id["Base.WaterPaintbucket"]["backlog_bucket"], "filled_utility_water_container_cluster_absent")
            self.assertEqual(residual_by_id["Base.WaterBowl"]["backlog_bucket"], "filled_table_water_vessel_cluster_absent")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
