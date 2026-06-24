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

from tools.build.build_post_cleanup_phase3_runtime_integration import (
    build_post_cleanup_phase3_runtime_integration,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


class PostCleanupPhase3RuntimeIntegrationTest(unittest.TestCase):
    def test_build_phase3_runtime_integration_overlays_promoted_rows_and_aggregates_backlog(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_runtime_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[3db8a64aa44d99e66454b9c4d818c039].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[3db8a64aa44d99e66454b9c4d818c039]
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[ad7a8274ac2e909701b9fe13c5415b11].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[ad7a8274ac2e909701b9fe13c5415b11]
            base_runtime_summary_path = tmp / "adoption_runtime_summary.json"
            package_a_dir = tmp / "pkg_a"
            package_b_dir = tmp / "pkg_b"
            output_dir = tmp / "out"

            dump_jsonl(
                base_facts_path,
                [
                    {
                        "item_id": "A",
                        "identity_hint": "학습 자료",
                        "acquisition_hint": "책장에서 찾는다",
                        "primary_use": "학습 작업에서 정보를 익힐 때 쓴다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    },
                    {
                        "item_id": "B",
                        "identity_hint": "연료 용기",
                        "acquisition_hint": "차고에서 발견된다",
                        "primary_use": "연료를 담는 용기다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    },
                    {
                        "item_id": "C",
                        "identity_hint": "야영 장비",
                        "acquisition_hint": "캠핑 용품 보관 장소에서 발견된다",
                        "primary_use": None,
                        "fact_origin": {"primary_use": ["role_fallback"]},
                    },
                    {
                        "item_id": "D",
                        "identity_hint": "필기 재료",
                        "acquisition_hint": "사무용품 보관 장소에서 발견된다",
                        "primary_use": "기록에 쓰는 재료다",
                        "fact_origin": {"primary_use": ["identity_fallback"]},
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
                        "item_id": "B",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "B",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "identity_fallback_keep_existing",
                        "use_source": "identity_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "identity_fallback",
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
                        "item_id": "C",
                        "state": "silent",
                        "reason_code": "MISSING_PRIMARY_USE",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "C",
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
                        "hard_fail_codes": [],
                        "v9_warn": True,
                    },
                    {
                        "item_id": "D",
                        "state": "active",
                        "reason_code": "INTERACTION_CLUSTER_MERGED",
                        "compose_profile": "interaction_component",
                        "facts_ref": "D",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "identity_fallback_keep_existing",
                        "use_source": "identity_fallback",
                        "selected_cluster": None,
                        "selected_role": None,
                        "selection_path": "identity_fallback",
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
            dump_json(
                base_runtime_summary_path,
                {
                    "state_counts": {"active": 3, "silent": 1},
                    "runtime_path_counts": {
                        "cluster_summary": 1,
                        "identity_fallback": 2,
                        "role_fallback": 1,
                        "direct_use": 0,
                    },
                    "decision_use_source_counts": {
                        "cluster_summary": 1,
                        "identity_fallback": 2,
                        "role_fallback": 1,
                        "direct_use": 0,
                    },
                },
            )

            dump_jsonl(
                package_a_dir / "promoted_facts.jsonl",
                [
                    {
                        "item_id": "B",
                        "identity_hint": "연료 용기",
                        "acquisition_hint": "차고에서 발견된다",
                        "primary_use": "연료 취급 작업에서 연료를 옮기거나 넣을 때 쓴다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    }
                ],
            )
            dump_jsonl(
                package_a_dir / "promoted_decisions.jsonl",
                [
                    {
                        "item_id": "B",
                        "state": "active",
                        "reason_code": "PHASE3_PACKAGE_PROMOTED",
                        "compose_profile": "interaction_tool",
                        "facts_ref": "B",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "phase3_package_overlay",
                        "use_source": "cluster_summary",
                        "selected_cluster": "fuel_handling",
                        "selected_role": "tool",
                        "selection_path": "phase3_package",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": True,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": [],
                        "v9_warn": False,
                    }
                ],
            )
            dump_json(
                package_a_dir / "residual_backlog.json",
                {
                    "row_count": 1,
                    "rows": [
                        {
                            "item_id": "E",
                            "display_name": "Trap Tool",
                            "backlog_bucket": "trap_tool_cluster_absent",
                        }
                    ],
                },
            )

            dump_jsonl(
                package_b_dir / "promoted_facts.jsonl",
                [
                    {
                        "item_id": "C",
                        "identity_hint": "야영 장비",
                        "acquisition_hint": "캠핑 용품 보관 장소에서 발견된다",
                        "primary_use": "야영 설치 작업에서 임시 거처를 펼치고 세울 때 쓴다",
                        "fact_origin": {"primary_use": ["cluster_summary"]},
                    }
                ],
            )
            dump_jsonl(
                package_b_dir / "promoted_decisions.jsonl",
                [
                    {
                        "item_id": "C",
                        "state": "active",
                        "reason_code": "PHASE3_PACKAGE_PROMOTED",
                        "compose_profile": "interaction_output",
                        "facts_ref": "C",
                        "override_mode": "none",
                        "manual_override_text_ko": None,
                        "merge_case": "phase3_package_overlay",
                        "use_source": "cluster_summary",
                        "selected_cluster": "field_shelter_setup",
                        "selected_role": "output",
                        "selection_path": "phase3_package",
                        "tie_break_applied": False,
                        "tie_break_review_required": False,
                        "manual_override_required": False,
                        "cluster_used": True,
                        "cluster_policy_status": None,
                        "policy_excluded_reason_codes": [],
                        "hard_fail_codes": [],
                        "v9_warn": False,
                    }
                ],
            )
            dump_json(
                package_b_dir / "residual_backlog.json",
                {
                    "row_count": 2,
                    "rows": [
                        {
                            "item_id": "F",
                            "display_name": "Notebook",
                            "backlog_bucket": "writing_material_cluster_absent",
                        },
                        {
                            "item_id": "G",
                            "display_name": "Paper",
                            "backlog_bucket": "writing_material_cluster_absent",
                        },
                    ],
                },
            )

            summary = build_post_cleanup_phase3_runtime_integration(
                base_facts_path=base_facts_path,
                base_decisions_path=base_decisions_path,
                base_runtime_summary_path=base_runtime_summary_path,
                package_artifacts=[
                    {
                        "package_id": "PKG-A",
                        "package_title": "Fuel Handling",
                        "dir": package_a_dir,
                        "promoted_facts": "promoted_facts.jsonl",
                        "promoted_decisions": "promoted_decisions.jsonl",
                        "residual_backlog": "residual_backlog.json",
                    },
                    {
                        "package_id": "PKG-B",
                        "package_title": "Field Shelter",
                        "dir": package_b_dir,
                        "promoted_facts": "promoted_facts.jsonl",
                        "promoted_decisions": "promoted_decisions.jsonl",
                        "residual_backlog": "residual_backlog.json",
                    },
                ],
                output_dir=output_dir,
            )

            self.assertEqual(summary["promoted_row_count"], 2)
            self.assertEqual(summary["residual_backlog_count"], 3)
            self.assertTrue(summary["validation"]["pass"])
            self.assertEqual(summary["runtime_report_status"], "ready_for_in_game_validation")

            runtime_summary = load_json(Path(summary["runtime_summary_path"]))
            self.assertEqual(runtime_summary["state_counts"]["active"], 4)
            self.assertNotIn("silent", runtime_summary["state_counts"])
            self.assertEqual(runtime_summary["runtime_path_counts"]["cluster_summary"], 3)
            self.assertEqual(runtime_summary["runtime_path_counts"]["identity_fallback"], 1)
            self.assertEqual(runtime_summary["runtime_path_counts"]["role_fallback"], 0)
            self.assertEqual(runtime_summary["phase3_promote_count"], 2)
            self.assertEqual(runtime_summary["phase3_residual_backlog_count"], 3)
            self.assertEqual(runtime_summary["package_promote_counts"], {"PKG-A": 1, "PKG-B": 1})
            self.assertEqual(runtime_summary["package_residual_counts"], {"PKG-A": 1, "PKG-B": 2})
            self.assertEqual(
                runtime_summary["residual_backlog_bucket_counts"],
                {
                    "trap_tool_cluster_absent": 1,
                    "writing_material_cluster_absent": 2,
                },
            )

            diff_report = load_json(Path(summary["diff_report_path"]))
            self.assertEqual(diff_report["state_delta"], {"active": 1, "silent": -1})
            self.assertEqual(
                diff_report["runtime_path_delta"],
                {
                    "cluster_summary": 2,
                    "direct_use": 0,
                    "identity_fallback": -1,
                    "role_fallback": -1,
                },
            )

            promoted_index = load_json(output_dir / "phase3_promoted_item_index.json")
            self.assertEqual(promoted_index["row_count"], 2)
            promoted_rows = {row["item_id"]: row for row in promoted_index["rows"]}
            self.assertEqual(promoted_rows["B"]["runtime_state_before"], "active")
            self.assertEqual(promoted_rows["B"]["runtime_state_after"], "active")
            self.assertEqual(promoted_rows["C"]["runtime_state_before"], "silent")
            self.assertEqual(promoted_rows["C"]["runtime_state_after"], "active")

            integrated_decisions = {row["item_id"]: row for row in load_jsonl(output_dir / "dvf_3_3_decisions.phase3_integrated.jsonl")}
            self.assertEqual(integrated_decisions["B"]["selected_cluster"], "fuel_handling")
            self.assertEqual(integrated_decisions["C"]["selected_cluster"], "field_shelter_setup")
            self.assertEqual(integrated_decisions["C"]["state"], "active")

            residual_aggregate = load_json(output_dir / "phase3_residual_backlog_aggregate.json")
            self.assertEqual(residual_aggregate["row_count"], 3)
            self.assertEqual(
                {row["source_package_id"] for row in residual_aggregate["rows"]},
                {"PKG-A", "PKG-B"},
            )
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
