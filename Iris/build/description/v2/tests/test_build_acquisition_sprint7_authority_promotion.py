from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.build_acquisition_sprint7_authority_promotion import build_acquisition_sprint7_authority_promotion


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


class BuildAcquisitionSprint7AuthorityPromotionTest(unittest.TestCase):
    def test_promotes_full_acquisition_bundle_into_sprint7_authority_preview(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_acquisition_sprint7_authority_promotion"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            authority_dir = tmp_dir / "authority"
            bundle_dir = tmp_dir / "bundle"
            input_dir = tmp_dir / "input"

            authority_facts_path = authority_dir / "facts.jsonl"
            authority_decisions_path = authority_dir / "decisions.jsonl"
            authority_rendered_path = authority_dir / "rendered.json"
            authority_rendered_validation_path = authority_dir / "rendered_validation.json"
            authority_decisions_validation_path = authority_dir / "decisions_validation.json"
            authority_runtime_summary_path = authority_dir / "runtime_summary.json"
            authority_runtime_note_path = authority_dir / "runtime_note.md"
            authority_promotion_note_path = authority_dir / "promotion_note.md"
            authority_promotion_report_path = authority_dir / "promotion_report.json"
            authority_checklist_path = authority_dir / "checklist.md"
            authority_validation_pack_path = authority_dir / "validation_pack.md"
            authority_closure_report_path = authority_dir / "closure_report.md"
            authority_baseline_rendered_path = authority_dir / "baseline_rendered.json"
            authority_baseline_rendered_validation_path = authority_dir / "baseline_rendered_validation.json"
            authority_baseline_style_log_path = authority_dir / "baseline_style.jsonl"
            authority_promoted_style_log_path = authority_dir / "promoted_style.jsonl"
            authority_lua_path = authority_dir / "IrisLayer3Data.lua"
            authority_bridge_report_path = authority_dir / "bridge_report.json"
            authority_runtime_report_path = authority_dir / "runtime_report.json"

            facts_patch_path = input_dir / "facts_patch.full.promote.jsonl"
            facts_review_path = input_dir / "facts_patch.semantic.review.jsonl"
            decisions_patch_path = input_dir / "decisions_patch.review.jsonl"
            bundle_facts_path = bundle_dir / "promoted_facts.jsonl"
            bundle_decisions_path = bundle_dir / "promoted_decisions.jsonl"
            bundle_baseline_rendered_path = bundle_dir / "baseline_rendered.json"
            bundle_promoted_rendered_path = bundle_dir / "promoted_rendered.json"
            bundle_baseline_style_log_path = bundle_dir / "baseline_style.jsonl"
            bundle_promoted_style_log_path = bundle_dir / "promoted_style.jsonl"
            bundle_decisions_validation_path = bundle_dir / "decisions_validation.json"
            bundle_report_path = bundle_dir / "promotion_report.json"
            overlay_path = tmp_dir / "overlay.jsonl"

            layer3_renderer_path = tmp_dir / "mod" / "layer3_renderer.lua"
            boot_path = tmp_dir / "mod" / "AIrisBoot.lua"
            main_path = tmp_dir / "mod" / "IrisMain.lua"
            context_menu_path = tmp_dir / "mod" / "IrisContextMenu.lua"
            bullet_compat_path = tmp_dir / "mod" / "IrisBulletReloadCompat.lua"
            browser_path = tmp_dir / "mod" / "IrisBrowser.lua"
            panel_path = tmp_dir / "mod" / "IrisWikiPanel.lua"
            wiki_sections_path = tmp_dir / "mod" / "IrisWikiSections.lua"

            write_jsonl(
                authority_facts_path,
                [
                    {
                        "item_id": "Base.One",
                        "identity_hint": "공구",
                        "primary_use": "작업할 때 쓴다",
                        "acquisition_hint": "공구 보관 장소",
                        "fact_origin": {"identity_hint": ["seed"], "primary_use": ["seed"], "acquisition_hint": ["seed"]},
                        "slot_meta": {},
                    },
                    {
                        "item_id": "Base.Two",
                        "identity_hint": "소품",
                        "primary_use": "장식할 때 쓴다",
                        "acquisition_hint": None,
                        "fact_origin": {"identity_hint": ["seed"], "primary_use": ["seed"], "acquisition_hint": ["seed"]},
                        "slot_meta": {},
                    },
                ],
            )
            write_jsonl(
                authority_decisions_path,
                [
                    {
                        "item_id": "Base.One",
                        "facts_ref": "Base.One",
                        "state": "active",
                        "acquisition_null_reason": None,
                        "compose_profile": "interaction_output",
                        "selected_cluster": None,
                        "hard_fail_codes": [],
                        "v9_warn": False,
                    },
                    {
                        "item_id": "Base.Two",
                        "facts_ref": "Base.Two",
                        "state": "active",
                        "acquisition_null_reason": None,
                        "compose_profile": "interaction_output",
                        "selected_cluster": None,
                        "hard_fail_codes": [],
                        "v9_warn": False,
                    },
                ],
            )
            write_jsonl(
                facts_patch_path,
                [
                    {
                        "item_id": "Base.One",
                        "proposed_acquisition_hint": "공구 보관 코너에서 발견된다",
                        "proposed_slot_meta_patch": {"acquisition_hint": {"canonical_key": "tool_corner", "source_origin": "semantic_draft"}},
                    }
                ],
            )
            write_jsonl(decisions_patch_path, [{"item_id": "Base.Two", "proposed_acquisition_null_reason": "UBIQUITOUS_ITEM"}])
            write_jsonl(
                facts_review_path,
                [
                    {
                        "item_id": "Base.One",
                        "patch_status": "PROMOTION_READY",
                        "current_acquisition_hint": "공구 보관 장소",
                        "proposed_acquisition_hint": "공구 보관 코너에서 발견된다",
                    },
                    {
                        "item_id": "Base.Two",
                        "patch_status": "PROMOTION_READY",
                        "current_acquisition_hint": None,
                        "proposed_acquisition_hint": None,
                    },
                ],
            )
            write_json(authority_runtime_summary_path, {"schema_version": "second-pass-sprint7-runtime-summary-v1", "runtime_report_status": "ready_for_in_game_validation"})
            authority_runtime_note_path.write_text("# Sprint 7 Runtime Note\n\n- baseline ready: `true`\n", encoding="utf-8")
            authority_checklist_path.write_text("# Sprint 7 In-Game Validation Checklist\n", encoding="utf-8")
            authority_validation_pack_path.write_text("# Second Pass In-Game Validation Pack\n", encoding="utf-8")
            authority_closure_report_path.write_text("# Second Pass Closure Report\n", encoding="utf-8")
            overlay_path.write_text("", encoding="utf-8")

            layer3_renderer_path.parent.mkdir(parents=True, exist_ok=True)
            layer3_renderer_path.write_text(
                'require, "Iris/Data/IrisLayer3DataChunks"\nsafeRequire("Iris/Data/IrisLayer3DataChunks")\nlocal publish_state = "internal_only"\n',
                encoding="utf-8",
            )
            boot_path.write_text('require, "Iris/IrisMain"\n', encoding="utf-8")
            main_path.write_text('require, "Iris/Compat/IrisBulletReloadCompat"\nBulletReloadCompat.install()\nrequire, "Iris/UI/Wiki/IrisContextMenu"\nhookContextMenu()\n', encoding="utf-8")
            context_menu_path.write_text("\n".join(["OnFillInventoryObjectContextMenu.Add", "Iris: View More", "resolveFirstInventoryItem", "candidate:getItems()", "container:get(0)"]), encoding="utf-8")
            bullet_compat_path.write_text("\n".join(["function IrisBulletReloadCompat.install() end", "_irisSafeBulletReloadPatchApplied", "buildAmmoReloadTooltipDescription"]), encoding="utf-8")
            browser_path.write_text("renderLayer3Section(item)\n", encoding="utf-8")
            panel_path.write_text("renderLayer3Section(item)\n", encoding="utf-8")
            wiki_sections_path.write_text('renderLayer3Section\nrequire, "Iris/Data/layer3_renderer"\n', encoding="utf-8")

            payload = build_acquisition_sprint7_authority_promotion(
                authority_facts_path=authority_facts_path,
                authority_decisions_path=authority_decisions_path,
                authority_rendered_path=authority_rendered_path,
                authority_rendered_validation_path=authority_rendered_validation_path,
                authority_decisions_validation_path=authority_decisions_validation_path,
                authority_runtime_summary_path=authority_runtime_summary_path,
                authority_runtime_note_path=authority_runtime_note_path,
                authority_promotion_note_path=authority_promotion_note_path,
                authority_promotion_report_path=authority_promotion_report_path,
                authority_checklist_path=authority_checklist_path,
                authority_validation_pack_path=authority_validation_pack_path,
                authority_closure_report_path=authority_closure_report_path,
                authority_baseline_rendered_path=authority_baseline_rendered_path,
                authority_baseline_rendered_validation_path=authority_baseline_rendered_validation_path,
                authority_baseline_style_log_path=authority_baseline_style_log_path,
                authority_promoted_style_log_path=authority_promoted_style_log_path,
                authority_lua_path=authority_lua_path,
                authority_bridge_report_path=authority_bridge_report_path,
                authority_runtime_report_path=authority_runtime_report_path,
                facts_patch_path=facts_patch_path,
                facts_review_path=facts_review_path,
                decisions_patch_path=decisions_patch_path,
                bundle_facts_path=bundle_facts_path,
                bundle_decisions_path=bundle_decisions_path,
                bundle_baseline_rendered_path=bundle_baseline_rendered_path,
                bundle_promoted_rendered_path=bundle_promoted_rendered_path,
                bundle_baseline_style_log_path=bundle_baseline_style_log_path,
                bundle_promoted_style_log_path=bundle_promoted_style_log_path,
                bundle_decisions_validation_path=bundle_decisions_validation_path,
                bundle_report_path=bundle_report_path,
                overlay_path=overlay_path,
                layer3_renderer_path=layer3_renderer_path,
                boot_path=boot_path,
                main_path=main_path,
                context_menu_path=context_menu_path,
                bullet_compat_path=bullet_compat_path,
                browser_path=browser_path,
                panel_path=panel_path,
                wiki_sections_path=wiki_sections_path,
            )

            report = payload["report"]
            promoted_facts = [json.loads(line) for line in authority_facts_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            promoted_decisions = [json.loads(line) for line in authority_decisions_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            updated_summary = json.loads(authority_runtime_summary_path.read_text(encoding="utf-8"))
            updated_note = authority_runtime_note_path.read_text(encoding="utf-8")
            updated_checklist = authority_checklist_path.read_text(encoding="utf-8")
            updated_validation_pack = authority_validation_pack_path.read_text(encoding="utf-8")
            updated_closure_report = authority_closure_report_path.read_text(encoding="utf-8")

            self.assertEqual(promoted_facts[0]["acquisition_hint"], "공구 보관 코너에서 발견된다")
            self.assertEqual(promoted_facts[0]["slot_meta"]["acquisition_hint"]["canonical_key"], "tool_corner")
            self.assertEqual(promoted_decisions[1]["acquisition_null_reason"], "UBIQUITOUS_ITEM")
            self.assertEqual(report["decisions_contract_hard_fail_count"], 0)
            self.assertEqual(report["rendered_hard_fail_count"], 0)
            self.assertEqual(report["introduced_rendered_hard_fail_count"], 0)
            self.assertEqual(report["introduced_rendered_warn_count"], 0)
            self.assertTrue(report["sprint7_authority_preview_ready"])
            self.assertIn("acquisition_promotion", updated_summary)
            self.assertIn("## Acquisition Promotion", updated_note)
            self.assertIn("## Acquisition Promotion Checks", updated_checklist)
            self.assertIn("Base.One", updated_checklist)
            self.assertIn("## Priority D — Acquisition Promotion", updated_validation_pack)
            self.assertIn("## Acquisition Promotion", updated_closure_report)
            self.assertFalse(authority_lua_path.exists())
            self.assertTrue(authority_lua_path.with_name("IrisLayer3DataChunks.lua").exists())
            self.assertTrue((authority_lua_path.with_name("IrisLayer3DataChunks") / "Chunk001.lua").exists())
            self.assertTrue(authority_bridge_report_path.exists())
            self.assertTrue(authority_runtime_report_path.exists())
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
