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

from tools.build.build_post_cleanup_phase3_pkg2_combat_reuse import (
    build_post_cleanup_phase3_pkg2_combat_reuse,
)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class PostCleanupPhase3Pkg2CombatReuseTest(unittest.TestCase):
    def test_build_pkg2_combat_reuse_promotes_only_safe_rows(self) -> None:
        tmp_root = ROOT / ".tmp_tests"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"post_cleanup_phase3_pkg2_{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            backlog_map_path = tmp / "weak_cleanup_to_source_backlog_map.json"
            base_facts_path = tmp / "dvf_3_3_facts.adopted DVF_AUTHORITY_ROLE_MIGRATION[667cc6017448a701af7ad75d3e315a51].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[667cc6017448a701af7ad75d3e315a51]
            base_decisions_path = tmp / "dvf_3_3_decisions.adopted DVF_AUTHORITY_ROLE_MIGRATION[9eea38faa713d3c99aed6661f871706e].jsonl" DVF_AUTHORITY_ROLE_MIGRATION[9eea38faa713d3c99aed6661f871706e]
            itemscript_path = tmp / "items_itemscript.json"
            output_dir = tmp / "out"

            dump_json(
                backlog_map_path,
                {
                    "rows": [
                        {"item_id": "Base.FlintKnife", "display_name": "Stone Knife", "primary_classification": "Combat.2-E", "candidate_family": "role_fallback_silent", "cleanup_phase": "W-5"},
                        {"item_id": "Base.ShotgunSawnoff", "display_name": "Sawn Off JS-2000 Shotgun", "primary_classification": "Combat.2-I", "candidate_family": "identity_fallback_active", "cleanup_phase": "W-2"},
                        {"item_id": "Base.BadmintonRacket", "display_name": "Badminton Racket", "primary_classification": "Combat.2-C", "candidate_family": "identity_fallback_active", "cleanup_phase": "W-2"},
                        {"item_id": "Base.Crowbar", "display_name": "Crowbar", "primary_classification": "Combat.2-B", "candidate_family": "identity_fallback_active", "cleanup_phase": "W-2"},
                    ]
                },
            )
            dump_json(itemscript_path, {"Base.ShotgunSawnoff": {"Type": "Weapon", "SubCategory": "Firearm", "AmmoType": "Base.ShotgunShells"}})

            dump_jsonl(
                base_facts_path,
                [
                    {"item_id": "MELEE_SAMPLE", "identity_hint": "즉석 둔기", "primary_use": "근접 전투 작업에서 휘둘러 공격하거나 밀어낼 때 쓴다", "acquisition_hint": "제작으로 얻는다", "fact_origin": {"primary_use": ["cluster_summary"]}},
                    {"item_id": "FIREARM_SAMPLE", "identity_hint": "화기", "primary_use": "사격 전투에 쓰는 화기다", "acquisition_hint": "총기 보관 장소에서 발견된다", "fact_origin": {"primary_use": ["cluster_summary"]}},
                    {"item_id": "Base.FlintKnife", "identity_hint": "제작 무기", "primary_use": None, "acquisition_hint": "나뭇가지와 깎인 돌, 천 조각이나 끈으로 제작한다", "fact_origin": {"primary_use": ["role_fallback"]}},
                    {"item_id": "Base.ShotgunSawnoff", "identity_hint": "근접 무기", "primary_use": "근접 전투에 쓰는 무기다", "acquisition_hint": "산탄총과 톱으로 절단해 만든다", "fact_origin": {"primary_use": ["identity_fallback"]}},
                    {"item_id": "Base.BadmintonRacket", "identity_hint": "스포츠 용품", "primary_use": "훈련이나 레저 활동에 쓰는 스포츠 용품이다", "acquisition_hint": "체육 용품 보관 장소에서 발견된다", "fact_origin": {"primary_use": ["identity_fallback"]}},
                    {"item_id": "Base.Crowbar", "identity_hint": "무기 겸용 도구", "primary_use": "근접 전투나 작업에 함께 쓰는 도구다", "acquisition_hint": "차고와 공구 상자에서 발견된다", "fact_origin": {"primary_use": ["identity_fallback"]}},
                ],
            )

            dump_jsonl(
                base_decisions_path,
                [
                    {"item_id": "MELEE_SAMPLE", "state": "active", "reason_code": "INTERACTION_CLUSTER_MERGED", "compose_profile": "interaction_output", "facts_ref": "MELEE_SAMPLE", "override_mode": "none", "manual_override_text_ko": None, "merge_case": "cluster_summary", "use_source": "cluster_summary", "selected_cluster": "melee_combat", "selected_role": "output", "selection_path": "frequency", "tie_break_applied": False, "tie_break_review_required": False, "manual_override_required": False, "cluster_used": True, "cluster_policy_status": None, "policy_excluded_reason_codes": [], "hard_fail_codes": [], "v9_warn": False},
                    {"item_id": "FIREARM_SAMPLE", "state": "active", "reason_code": "INTERACTION_CLUSTER_MERGED", "compose_profile": "interaction_tool", "facts_ref": "FIREARM_SAMPLE", "override_mode": "none", "manual_override_text_ko": None, "merge_case": "cluster_summary", "use_source": "cluster_summary", "selected_cluster": "ranged_firearm_combat", "selected_role": "tool", "selection_path": "frequency", "tie_break_applied": False, "tie_break_review_required": False, "manual_override_required": False, "cluster_used": True, "cluster_policy_status": None, "policy_excluded_reason_codes": [], "hard_fail_codes": [], "v9_warn": False},
                    {"item_id": "Base.FlintKnife", "state": "silent", "reason_code": "MISSING_PRIMARY_USE", "compose_profile": "interaction_output", "facts_ref": "Base.FlintKnife", "override_mode": "none", "manual_override_text_ko": None, "merge_case": "cluster_absent_keep_existing", "use_source": "role_fallback", "selected_cluster": None, "selected_role": None, "selection_path": "cluster_absent", "tie_break_applied": False, "tie_break_review_required": False, "manual_override_required": False, "cluster_used": False, "cluster_policy_status": None, "policy_excluded_reason_codes": [], "hard_fail_codes": [], "v9_warn": False},
                    {"item_id": "Base.ShotgunSawnoff", "state": "active", "reason_code": "INTERACTION_CLUSTER_MERGED", "compose_profile": "interaction_tool", "facts_ref": "Base.ShotgunSawnoff", "override_mode": "none", "manual_override_text_ko": None, "merge_case": "identity_fallback_keep_existing", "use_source": "identity_fallback", "selected_cluster": None, "selected_role": None, "selection_path": "frequency", "tie_break_applied": False, "tie_break_review_required": False, "manual_override_required": False, "cluster_used": False, "cluster_policy_status": None, "policy_excluded_reason_codes": [], "hard_fail_codes": [], "v9_warn": False},
                    {"item_id": "Base.BadmintonRacket", "state": "active", "reason_code": "INTERACTION_CLUSTER_MERGED", "compose_profile": "interaction_tool", "facts_ref": "Base.BadmintonRacket", "override_mode": "none", "manual_override_text_ko": None, "merge_case": "identity_fallback_keep_existing", "use_source": "identity_fallback", "selected_cluster": None, "selected_role": None, "selection_path": "frequency", "tie_break_applied": False, "tie_break_review_required": False, "manual_override_required": False, "cluster_used": False, "cluster_policy_status": None, "policy_excluded_reason_codes": [], "hard_fail_codes": [], "v9_warn": False},
                    {"item_id": "Base.Crowbar", "state": "active", "reason_code": "INTERACTION_CLUSTER_MERGED", "compose_profile": "interaction_tool", "facts_ref": "Base.Crowbar", "override_mode": "none", "manual_override_text_ko": None, "merge_case": "identity_fallback_keep_existing", "use_source": "identity_fallback", "selected_cluster": None, "selected_role": None, "selection_path": "frequency", "tie_break_applied": False, "tie_break_review_required": False, "manual_override_required": False, "cluster_used": False, "cluster_policy_status": None, "policy_excluded_reason_codes": [], "hard_fail_codes": [], "v9_warn": False},
                ],
            )

            summary = build_post_cleanup_phase3_pkg2_combat_reuse(backlog_map_path=backlog_map_path, base_facts_path=base_facts_path, base_decisions_path=base_decisions_path, itemscript_path=itemscript_path, output_dir=output_dir)

            self.assertEqual(summary["target_row_count"], 4)
            self.assertEqual(summary["promote_candidate_count"], 2)
            self.assertEqual(summary["residual_backlog_count"], 2)
            self.assertEqual(summary["identity_hint_override_count"], 1)
            self.assertEqual(summary["proposed_cluster_counts"]["melee_combat"], 1)
            self.assertEqual(summary["proposed_cluster_counts"]["ranged_firearm_combat"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["active"], 1)
            self.assertEqual(summary["projected_runtime_state_delta"]["silent"], -1)
            self.assertTrue(summary["validation"]["pass"])

            promoted_facts = [json.loads(line) for line in (output_dir / "pkg2_combat_reuse_promoted_candidate_facts.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
            facts_by_id = {row["item_id"]: row for row in promoted_facts}
            self.assertEqual(facts_by_id["Base.FlintKnife"]["primary_use"], "근접 전투 작업에서 휘둘러 공격하거나 밀어낼 때 쓴다")
            self.assertEqual(facts_by_id["Base.ShotgunSawnoff"]["identity_hint"], "산탄총")
            self.assertEqual(facts_by_id["Base.ShotgunSawnoff"]["primary_use"], "사격 전투에 쓰는 화기다")

            residual = json.loads((output_dir / "pkg2_combat_reuse_residual_backlog.json").read_text(encoding="utf-8"))
            residual_by_id = {row["item_id"]: row for row in residual["rows"]}
            self.assertEqual(residual_by_id["Base.BadmintonRacket"]["backlog_bucket"], "sports_tool_cluster_mismatch")
            self.assertEqual(residual_by_id["Base.Crowbar"]["backlog_bucket"], "multiuse_tool_cluster_absent")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
