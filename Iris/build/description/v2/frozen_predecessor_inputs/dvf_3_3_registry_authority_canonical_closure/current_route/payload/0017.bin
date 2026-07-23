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
from tools.build.report_post_cleanup_phase2_adoption_validation import (
    build_post_cleanup_phase2_adoption_validation,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase2AdoptionValidationTest(unittest.TestCase):
    def test_build_phase2_validation_checks_adopt_subset(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase2_validation_{uuid.uuid4().hex}"
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
                        "keep_generated": 0,
                        "keep_missing": 1,
                        "demote_to_missing": 0,
                        "pending_extra_gate": 0,
                    },
                    "buckets": {
                        "adopt_in_phase2": ["D"],
                        "keep_generated": [],
                        "keep_missing": ["E"],
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
                ],
            )
            dump_jsonl(
                base_decisions_path,
                [
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
                ],
            )
            dump_json(
                base_runtime_summary_path,
                {
                    "merged_state_counts": {"active": 0, "silent": 2},
                    "decision_use_source_counts": {
                        "cluster_summary": 0,
                        "identity_fallback": 0,
                        "role_fallback": 2,
                        "direct_use": 0,
                    },
                    "merged_runtime_path_counts": {
                        "cluster_summary": 0,
                        "identity_fallback": 0,
                        "role_fallback": 2,
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
                    ]
                },
            )

            build_post_cleanup_phase2_runtime_adoption(
                adoption_scope_manifest_path=adoption_scope_manifest_path,
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                base_runtime_summary_path=base_runtime_summary_path,
                candidate_facts_path=candidate_facts_path,
                w6_matrix_path=w6_matrix_path,
                output_dir=output_dir,
            )
            payload = build_post_cleanup_phase2_adoption_validation(
                adoption_scope_manifest_path=adoption_scope_manifest_path,
                adopted DVF_AUTHORITY_ROLE_MIGRATION[7fef130945f605a93e1d84c8d48f7fc2]_facts_path=output_dir / "dvf_3_3_facts.adopted.jsonl",
                adopted DVF_AUTHORITY_ROLE_MIGRATION[c7c2d397895dd7cc9c3e0af761c2e4f7]_decisions_path=output_dir / "dvf_3_3_decisions.adopted.jsonl",
                adopted DVF_AUTHORITY_ROLE_MIGRATION[7c04a78cf259cdfaa5864ad89065e601]_rendered_path=output_dir / "dvf_3_3_rendered.adopted.json",
                output_dir=output_dir,
            )

            self.assertTrue(payload["pass"])
            self.assertEqual(payload["counts"]["expected_adopt_count"], 1)
            self.assertEqual(payload["counts"]["validated_fact_count"], 1)
            self.assertEqual(payload["checks"]["subset_hard_fail_count"], 0)
            self.assertEqual(payload["checks"]["missing_primary_use_ids"], [])

            persisted = json.loads(
                (output_dir / "adoption_validation_report.json").read_text(encoding="utf-8")
            )
            self.assertTrue(persisted["pass"])
            self.assertEqual(persisted["validated_item_ids"], ["D"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
