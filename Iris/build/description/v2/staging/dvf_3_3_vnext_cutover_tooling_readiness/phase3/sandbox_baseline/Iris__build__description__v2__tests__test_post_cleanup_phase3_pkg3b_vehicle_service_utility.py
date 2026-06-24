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

from tools.build.build_post_cleanup_phase3_pkg3b_vehicle_service_utility import (
    build_post_cleanup_phase3_pkg3b_vehicle_service_utility,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg3BVehicleServiceUtilityTest(unittest.TestCase):
    def test_build_pkg3b_promotes_only_empty_fuel_container(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg3b_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            triage_rows_path = tmp / "pkg3_unclassified_triage_rows.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[769864ebf94b4c72c37b339d60f0da62].jsonl"
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[97aad4ae2fc6273fe633f1869645ad2a].jsonl"
            output_dir = tmp / "out"

            dump_json(
                triage_rows_path,
                {
                    "rows": [
                        {
                            "item_id": "Base.EmptyPetrolCan",
                            "display_name": "Empty Gas Can",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "vehicle_service_utility",
                            "inferred_classification_label": "Tool.VehicleServiceUtility",
                            "followon_package_id": "PKG-3B",
                        },
                        {
                            "item_id": "Base.CarBatteryCharger",
                            "display_name": "Car Battery Charger",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "vehicle_service_utility",
                            "inferred_classification_label": "Tool.VehicleServiceUtility",
                            "followon_package_id": "PKG-3B",
                        },
                        {
                            "item_id": "Base.Jack",
                            "display_name": "Jack",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "vehicle_service_utility",
                            "inferred_classification_label": "Tool.VehicleServiceUtility",
                            "followon_package_id": "PKG-3B",
                        },
                        {
                            "item_id": "Base.LugWrench",
                            "display_name": "Lug Wrench",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "vehicle_service_utility",
                            "inferred_classification_label": "Tool.VehicleServiceUtility",
                            "followon_package_id": "PKG-3B",
                        },
                        {
                            "item_id": "Base.TirePump",
                            "display_name": "Tire Pump",
                            "candidate_family": "role_fallback_active",
                            "runtime_axis_current": "generated",
                            "runtime_state_current": "active",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "vehicle_service_utility",
                            "inferred_classification_label": "Tool.VehicleServiceUtility",
                            "followon_package_id": "PKG-3B",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "FUEL_SAMPLE",
                        "identity_hint": "차량 정비 소모품",
                        "primary_use": "연료 취급 작업에서 연료를 옮기거나 넣을 때 쓴다",
                        "acquisition_hint": "차량 정비 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.EmptyPetrolCan",
                        "identity_hint": "차량 정비 용품",
                        "primary_use": None,
                        "acquisition_hint": "차량 정비 장소와 차량 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.CarBatteryCharger",
                        "identity_hint": "도구",
                        "primary_use": "도구다",
                        "acquisition_hint": "차량 정비 장소와 차량 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.Jack",
                        "identity_hint": "도구",
                        "primary_use": "도구다",
                        "acquisition_hint": "차량 정비 장소와 차량 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.LugWrench",
                        "identity_hint": "도구",
                        "primary_use": "도구다",
                        "acquisition_hint": "차량 정비 장소와 차량 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.TirePump",
                        "identity_hint": "도구",
                        "primary_use": "도구다",
                        "acquisition_hint": "차량 정비 장소와 차량 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "FUEL_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "FUEL_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "fuel_handling",
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
                        "item_id": "Base.EmptyPetrolCan",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.EmptyPetrolCan",
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
                        "item_id": "Base.CarBatteryCharger",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.CarBatteryCharger",
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
                        "item_id": "Base.Jack",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Jack",
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
                        "item_id": "Base.LugWrench",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.LugWrench",
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
                        "item_id": "Base.TirePump",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.TirePump",
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

            summary = build_post_cleanup_phase3_pkg3b_vehicle_service_utility(
                triage_rows_path=triage_rows_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 5)
            self.assertEqual(summary["promote_candidate_count"], 1)
            self.assertEqual(summary["residual_backlog_count"], 4)
            self.assertEqual(summary["proposed_cluster_counts"]["fuel_handling"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["active"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["silent"], -1)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg3b_vehicle_service_utility_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(promoted_facts), 1)
            self.assertEqual(promoted_facts[0]["item_id"], "Base.EmptyPetrolCan")
            self.assertEqual(promoted_facts[0]["primary_use"], "연료 취급 작업에서 연료를 옮기거나 넣을 때 쓴다")

            promoted_decisions = [
                json.loads(line)
                for line in (output_dir / "pkg3b_vehicle_service_utility_promoted_candidate_decisions.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(promoted_decisions[0]["selected_role"], "tool")
            self.assertEqual(promoted_decisions[0]["compose_profile"], "interaction_tool")

            residual = json.loads((output_dir / "pkg3b_vehicle_service_utility_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.CarBatteryCharger"]["backlog_bucket"], "battery_charging_cluster_absent")
            self.assertEqual(residual_by_id["Base.Jack"]["backlog_bucket"], "vehicle_service_tool_cluster_absent")
            self.assertEqual(residual_by_id["Base.LugWrench"]["backlog_bucket"], "vehicle_service_tool_cluster_absent")
            self.assertEqual(residual_by_id["Base.TirePump"]["backlog_bucket"], "vehicle_service_tool_cluster_absent")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
