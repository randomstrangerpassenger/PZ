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

from tools.build.build_post_cleanup_phase3_pkg3g_household_access_and_safety import (
    build_post_cleanup_phase3_pkg3g_household_access_and_safety,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg3GHouseholdAccessAndSafetyTest(unittest.TestCase):
    def test_build_pkg3g_promotes_only_padlock(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg3g_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            triage_rows_path = tmp / "pkg3_unclassified_triage_rows.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[1fa581bc7b2f1065f074943843155b10].jsonl"
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[2d5d2856ac75a05f136efe54cfb2be91].jsonl"
            output_dir = tmp / "out"

            dump_json(
                triage_rows_path,
                {
                    "rows": [
                        {
                            "item_id": "Base.Extinguisher",
                            "display_name": "Extinguisher",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "household_access_and_safety",
                            "inferred_classification_label": "Tool.HouseholdAccessAndSafety",
                            "followon_package_id": "PKG-3G",
                        },
                        {
                            "item_id": "Base.Lamp",
                            "display_name": "Lamp",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "household_access_and_safety",
                            "inferred_classification_label": "Tool.HouseholdAccessAndSafety",
                            "followon_package_id": "PKG-3G",
                        },
                        {
                            "item_id": "Base.Padlock",
                            "display_name": "Padlock",
                            "candidate_family": "role_fallback_silent",
                            "runtime_axis_current": "missing",
                            "runtime_state_current": "silent",
                            "cleanup_phase": "W-5",
                            "triage_cohort": "household_access_and_safety",
                            "inferred_classification_label": "Tool.HouseholdAccessAndSafety",
                            "followon_package_id": "PKG-3G",
                        },
                    ]
                },
            )

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "PADLOCK_SAMPLE",
                        "identity_hint": "번호 자물쇠",
                        "primary_use": "보안 작업에서 자물쇠나 차량, 문 장치를 열거나 잠글 때 다룬다",
                        "acquisition_hint": "보안 장비 보관 장소와 문 잠금 장치에서 발견된다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "Base.Extinguisher",
                        "identity_hint": "가정용 소모품",
                        "primary_use": None,
                        "acquisition_hint": "작업장과 안전 장비 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.Lamp",
                        "identity_hint": "생활용품",
                        "primary_use": None,
                        "acquisition_hint": "전자제품 매장과 전자 부품 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "Base.Padlock",
                        "identity_hint": "열쇠",
                        "primary_use": None,
                        "acquisition_hint": "공구점과 보관 장소에서 발견된다",
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "PADLOCK_SAMPLE",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "PADLOCK_SAMPLE",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_summary",
                        "use_source": "cluster_summary",
                        "selected_cluster": "security_access",
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
                        "item_id": "Base.Extinguisher",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Extinguisher",
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
                        "item_id": "Base.Lamp",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Lamp",
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
                        "item_id": "Base.Padlock",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "Base.Padlock",
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
                ],
            )

            summary = build_post_cleanup_phase3_pkg3g_household_access_and_safety(
                triage_rows_path=triage_rows_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["target_row_count"], 3)
            self.assertEqual(summary["promote_candidate_count"], 1)
            self.assertEqual(summary["residual_backlog_count"], 2)
            self.assertEqual(summary["proposed_cluster_counts"]["security_access"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["active"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["silent"], -1)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [
                json.loads(line)
                for line in (output_dir / "pkg3g_household_access_and_safety_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(promoted_facts), 1)
            self.assertEqual(promoted_facts[0]["item_id"], "Base.Padlock")
            self.assertEqual(promoted_facts[0]["primary_use"], "보안 작업에서 자물쇠나 차량, 문 장치를 열거나 잠글 때 다룬다")

            promoted_decisions = [
                json.loads(line)
                for line in (output_dir / "pkg3g_household_access_and_safety_promoted_candidate_decisions.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(promoted_decisions[0]["selected_role"], "tool")
            self.assertEqual(promoted_decisions[0]["compose_profile"], "interaction_tool")

            residual = json.loads((output_dir / "pkg3g_household_access_and_safety_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.Extinguisher"]["backlog_bucket"], "safety_equipment_cluster_absent")
            self.assertEqual(residual_by_id["Base.Lamp"]["backlog_bucket"], "household_lighting_cluster_absent")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
