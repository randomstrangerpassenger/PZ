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

from tools.build.build_post_cleanup_phase2_runtime_adoption import (
    build_post_cleanup_phase2_runtime_adoption,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase2RuntimeAdoptionTest(unittest.TestCase):
    def test_build_phase2_runtime_adoption_overlays_adopt_rows(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase2_runtime_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            adoption_scope_manifest_path = tmp / "adoption_scope_manifest.json"
            base_facts_path = tmp / "dvf_3_3_facts.integrated.jsonl"
            base_decisions_path = tmp / "dvf_3_3_decisions.integrated.jsonl"
            base_runtime_summary_path = tmp / "source_coverage_runtime_summary.json"
            candidate_facts_path = tmp / "integrated_facts.post_cleanup_candidate.jsonl"
            w6_matrix_path = tmp / "weak_active_disposition_matrix.json"
            output_dir = tmp / "out"

            dump_json(
                adoption_scope_manifest_path,
                {
                    "counts": {
                        "adopt_in_phase2": 1,
                        "keep_generated": 2,
                        "keep_missing": 2,
                        "demote_to_missing": 0,
                        "pending_extra_gate": 0,
                    },
                    "buckets": {
                        "adopt_in_phase2": ["D"],
                        "keep_generated": ["A", "F"],
                        "keep_missing": ["E", "G"],
                        "demote_to_missing": [],
                        "pending_extra_gate": [],
                    },
                    "decision_selections": {
                        "generated_weak_runtime_treatment": "keep_generated_no_indicator",
                        "missing_strong_adopt_timing": "adopt_in_phase2",
                        "missing_adequate_adopt_policy": "keep_missing",
                        "missing_weak_priority_policy": "lower_than_generated_weak",
                        "ui_quality_indicator_direction": "no_ui_exposure",
                    },
                },
            )
            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "A",
                        "identity_hint": "기존 강한 항목",
                        "acquisition_hint": "기존 획득",
                        "primary_use": "기존 강한 설명",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "D",
                        "identity_hint": "수원",
                        "acquisition_hint": "빈 용기에 물을 담아 얻는다",
                        "primary_use": None,
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "E",
                        "identity_hint": "의료 보호구",
                        "acquisition_hint": "의료 보관 장소에서 발견된다",
                        "primary_use": None,
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "F",
                        "identity_hint": "도구",
                        "acquisition_hint": "기존 획득",
                        "primary_use": "약하지만 출력 가능한 설명",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "G",
                        "identity_hint": "약한 누락 항목",
                        "acquisition_hint": "기존 획득",
                        "primary_use": None,
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                ],
            )
            dump_jsonl(
                base_decisions_path,
                [
                    {
                        "item_id": "A",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_output",
                        "facts_ref": "A",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "cluster_over_role_fallback",
                        "use_source": "cluster_summary",
                        "selected_cluster": "study_reference",
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
                        "item_id": "D",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "D",
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
                        "item_id": "E",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "E",
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
                        "item_id": "F",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "F",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "identity_fallback_keep_existing",
                        "use_source": "role_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "frequency",
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
                        "item_id": "G",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "G",
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
            dump_json(
                base_runtime_summary_path,
                {
                    "merged_state_counts": {"active": 2, "silent": 3},
                    "decision_use_source_counts": {
                        "cluster_summary": 1,
                        "identity_fallback": 0,
                        "role_fallback": 4,
                        "direct_use": 0,
                    },
                    "merged_runtime_path_counts": {
                        "cluster_summary": 1,
                        "identity_fallback": 1,
                        "role_fallback": 3,
                        "direct_use": 0,
                    },
                },
            )
            dump_jsonl(
                candidate_facts_path,
                [
                    {
                        "item_id": "D",
                        "identity_hint": "수원",
                        "acquisition_hint": "빈 용기에 물을 담아 얻는다",
                        "primary_use": "음료 섭취 작업에서 마시거나 나눠 마실 때 쓴다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                        "slot_meta": {
                            "weak_cleanup_w6": {
                                "proposed_cluster": "beverage_consumption",
                                "proposed_role": "output",
                                "source_package": "B-1",
                            }
                        },
                    },
                    {
                        "item_id": "E",
                        "identity_hint": "의료 보호구",
                        "acquisition_hint": "의료 보관 장소에서 발견된다",
                        "primary_use": None,
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                ],
            )
            dump_json(
                w6_matrix_path,
                {
                    "rows": [
                        {
                            "item_id": "D",
                            "runtime_axis_current": "missing",
                            "semantic_status_after_cleanup": "semantic-strong",
                            "proposed_cluster": "beverage_consumption",
                        },
                        {
                            "item_id": "E",
                            "runtime_axis_current": "missing",
                            "semantic_status_after_cleanup": "semantic-adequate",
                            "proposed_cluster": None,
                        },
                        {
                            "item_id": "F",
                            "runtime_axis_current": "generated",
                            "semantic_status_after_cleanup": "semantic-weak",
                            "proposed_cluster": None,
                        },
                    ]
                },
            )

            summary = build_post_cleanup_phase2_runtime_adoption(
                adoption_scope_manifest_path=adoption_scope_manifest_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                base_runtime_summary_path=base_runtime_summary_path,
                candidate_facts_path=candidate_facts_path,
                w6_matrix_path=w6_matrix_path,
                output_dir=output_dir,
            )

            self.assertEqual(summary["adopted_row_count"], 1)
            self.assertEqual(summary["adopted_ids_seen"], ["D"])

            facts = [
                json.loads(line)
                for line in (output_dir / "dvf_3_3_facts.adopted.jsonl").read_text(encoding="utf-8").splitlines()  # DVF_AUTHORITY_ROLE_MIGRATION[c99752b3ded3b5c1b7d96e009e10bd9c]
                if line.strip()
            ]
            facts_by_id = {row["item_id"]: row for row in facts}
            self.assertEqual(facts_by_id["D"]["primary_use"], "음료 섭취 작업에서 마시거나 나눠 마실 때 쓴다")
            self.assertIsNone(facts_by_id["E"]["primary_use"])

            decisions = [
                json.loads(line)
                for line in (output_dir / "dvf_3_3_decisions.adopted.jsonl").read_text(encoding="utf-8").splitlines()  # DVF_AUTHORITY_ROLE_MIGRATION[68ce23b4e801e2c62ae3037621943b60]
                if line.strip()
            ]
            decisions_by_id = {row["item_id"]: row for row in decisions}
            self.assertEqual(decisions_by_id["D"]["state"], "active")
            self.assertEqual(decisions_by_id["D"]["use_source"], "cluster_summary")
            self.assertEqual(decisions_by_id["D"]["compose_profile"], "interaction_output")
            self.assertEqual(decisions_by_id["E"]["state"], "silent")

            runtime_summary = json.loads(
                (output_dir / "adoption_runtime_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(runtime_summary["state_counts"]["active"], 3)
            self.assertEqual(runtime_summary["state_counts"]["silent"], 2)

            diff_report = json.loads(
                (output_dir / "adoption_diff_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(diff_report["state_delta"]["active"], 1)
            self.assertEqual(diff_report["state_delta"]["silent"], -1)

            rendered = json.loads(
                (output_dir / "dvf_3_3_rendered.adopted.json").read_text(encoding="utf-8")  # DVF_AUTHORITY_ROLE_MIGRATION[80e55aec0697fe4009b777b33b881b81]
            )
            self.assertEqual(rendered["entries"]["D"]["source"], "composed")
            self.assertIsNone(rendered["entries"]["E"]["text_ko"])

            self.assertFalse((output_dir / "IrisLayer3Data.lua").exists())
            self.assertTrue((output_dir / "IrisLayer3DataChunks.lua").exists())
            self.assertTrue((output_dir / "IrisLayer3DataChunks" / "Chunk001.lua").exists())
            self.assertTrue((output_dir / "phase2_runtime_report.json").exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
