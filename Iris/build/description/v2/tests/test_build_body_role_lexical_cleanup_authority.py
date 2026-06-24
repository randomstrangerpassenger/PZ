from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.build_body_role_lexical_cleanup_authority import (
    build_body_role_lexical_cleanup_authority,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


class BuildBodyRoleLexicalCleanupAuthorityTest(unittest.TestCase):
    def test_applies_cleanup_and_rebuilds_authority_preview(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_body_role_lexical_cleanup_authority"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            authority_dir = tmp_dir / "authority"
            overlay_path = tmp_dir / "overlay.jsonl"
            mod_dir = tmp_dir / "mod"

            authority_facts_path = authority_dir / "facts.jsonl"
            authority_decisions_path = authority_dir / "decisions.jsonl"
            authority_rendered_path = authority_dir / "rendered.json"
            authority_rendered_validation_path = authority_dir / "rendered_validation.json"
            authority_decisions_validation_path = authority_dir / "decisions_validation.json"
            authority_runtime_summary_path = authority_dir / "runtime_summary.json"
            authority_runtime_note_path = authority_dir / "runtime_note.md"
            authority_cleanup_note_path = authority_dir / "cleanup_note.md"
            authority_cleanup_report_path = authority_dir / "cleanup_report.json"
            authority_baseline_facts_path = authority_dir / "baseline_facts.jsonl"
            authority_baseline_decisions_path = authority_dir / "baseline_decisions.jsonl"
            authority_baseline_rendered_path = authority_dir / "baseline_rendered.json"
            authority_baseline_rendered_validation_path = authority_dir / "baseline_rendered_validation.json"
            authority_baseline_style_log_path = authority_dir / "baseline_style.jsonl"
            authority_promoted_style_log_path = authority_dir / "promoted_style.jsonl"
            authority_lua_path = authority_dir / "IrisLayer3Data.lua"
            authority_bridge_report_path = authority_dir / "bridge_report.json"
            authority_runtime_report_path = authority_dir / "runtime_report.json"

            layer3_renderer_path = mod_dir / "layer3_renderer.lua"
            boot_path = mod_dir / "AIrisBoot.lua"
            main_path = mod_dir / "IrisMain.lua"
            context_menu_path = mod_dir / "IrisContextMenu.lua"
            bullet_compat_path = mod_dir / "IrisBulletReloadCompat.lua"
            browser_path = mod_dir / "IrisBrowser.lua"
            panel_path = mod_dir / "IrisWikiPanel.lua"
            wiki_sections_path = mod_dir / "IrisWikiSections.lua"

            write_jsonl(
                authority_facts_path,
                [
                    {
                        "item_id": "Base.One",
                        "identity_hint": "재료",
                        "primary_use": "건축 준비 작업에서 자재를 가공하거나 맞출 때 쓴다",
                        "acquisition_hint": None,
                        "fact_origin": {"identity_hint": ["seed"], "primary_use": ["cluster_summary"], "acquisition_hint": ["seed"]},
                        "slot_meta": {"interaction_cluster": {"selected_cluster": "construction_prep"}},
                    },
                    {
                        "item_id": "Base.Two",
                        "identity_hint": "가방",
                        "primary_use": "보관이나 휴대 작업에 쓰는 가방이다",
                        "acquisition_hint": None,
                        "fact_origin": {"identity_hint": ["seed"], "primary_use": ["cluster_summary"], "acquisition_hint": ["seed"]},
                        "slot_meta": {"interaction_cluster": {"selected_cluster": None}},
                    },
                    {
                        "item_id": "Base.AssaultRifle",
                        "identity_hint": "근접 무기",
                        "primary_use": "사격 전투에 쓰는 화기다",
                        "acquisition_hint": None,
                        "fact_origin": {"identity_hint": ["seed"], "primary_use": ["cluster_summary"], "acquisition_hint": ["seed"]},
                        "slot_meta": {"interaction_cluster": {"selected_cluster": "ranged_firearm_combat"}},
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
                        "compose_profile": "interaction_output",
                        "selected_cluster": "construction_prep",
                        "selected_role": "tool",
                        "hard_fail_codes": [],
                        "v9_warn": False,
                        "acquisition_null_reason": "UBIQUITOUS_ITEM",
                    },
                    {
                        "item_id": "Base.Two",
                        "facts_ref": "Base.Two",
                        "state": "active",
                        "compose_profile": "interaction_output",
                        "selected_cluster": None,
                        "selected_role": None,
                        "hard_fail_codes": [],
                        "v9_warn": False,
                        "acquisition_null_reason": "UBIQUITOUS_ITEM",
                    },
                    {
                        "item_id": "Base.AssaultRifle",
                        "facts_ref": "Base.AssaultRifle",
                        "state": "active",
                        "compose_profile": "interaction_output",
                        "selected_cluster": "ranged_firearm_combat",
                        "selected_role": "tool",
                        "hard_fail_codes": [],
                        "v9_warn": False,
                        "acquisition_null_reason": "UBIQUITOUS_ITEM",
                    },
                ],
            )
            write_json(authority_runtime_summary_path, {"schema_version": "second-pass-sprint7-runtime-summary-v1"})
            authority_runtime_note_path.write_text("# Sprint 7 Runtime Note\n", encoding="utf-8")
            overlay_path.write_text("", encoding="utf-8")

            mod_dir.mkdir(parents=True, exist_ok=True)
            layer3_renderer_path.write_text(
                'require, "Iris/Data/IrisLayer3DataChunks"\nsafeRequire("Iris/Data/IrisLayer3DataChunks")\nlocal publish_state = "internal_only"\n',
                encoding="utf-8",
            )
            boot_path.write_text('require, "Iris/IrisMain"\n', encoding="utf-8")
            main_path.write_text('require, "Iris/Compat/IrisBulletReloadCompat"\nBulletReloadCompat.install()\nrequire, "Iris/UI/Wiki/IrisContextMenu"\nhookContextMenu()\n', encoding="utf-8")
            context_menu_path.write_text(
                "\n".join(
                    [
                        "OnFillInventoryObjectContextMenu.Add",
                        "Iris: View More",
                        "resolveFirstInventoryItem",
                        "candidate:getItems()",
                        "container:get(0)",
                    ]
                ),
                encoding="utf-8",
            )
            bullet_compat_path.write_text(
                "\n".join(
                    [
                        "function IrisBulletReloadCompat.install() end",
                        "_irisSafeBulletReloadPatchApplied",
                        "buildAmmoReloadTooltipDescription",
                    ]
                ),
                encoding="utf-8",
            )
            browser_path.write_text("renderLayer3Section(item)\n", encoding="utf-8")
            panel_path.write_text("renderLayer3Section(item)\n", encoding="utf-8")
            wiki_sections_path.write_text('renderLayer3Section\nrequire, "Iris/Data/layer3_renderer"\n', encoding="utf-8")

            payload = build_body_role_lexical_cleanup_authority(
                authority_facts_path=authority_facts_path,
                authority_decisions_path=authority_decisions_path,
                authority_rendered_path=authority_rendered_path,
                authority_rendered_validation_path=authority_rendered_validation_path,
                authority_decisions_validation_path=authority_decisions_validation_path,
                authority_runtime_summary_path=authority_runtime_summary_path,
                authority_runtime_note_path=authority_runtime_note_path,
                authority_cleanup_note_path=authority_cleanup_note_path,
                authority_cleanup_report_path=authority_cleanup_report_path,
                authority_baseline_facts_path=authority_baseline_facts_path,
                authority_baseline_decisions_path=authority_baseline_decisions_path,
                authority_baseline_rendered_path=authority_baseline_rendered_path,
                authority_baseline_rendered_validation_path=authority_baseline_rendered_validation_path,
                authority_baseline_style_log_path=authority_baseline_style_log_path,
                authority_promoted_style_log_path=authority_promoted_style_log_path,
                authority_lua_path=authority_lua_path,
                authority_bridge_report_path=authority_bridge_report_path,
                authority_runtime_report_path=authority_runtime_report_path,
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

            promoted_facts = [
                json.loads(line)
                for line in authority_facts_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            updated_summary = json.loads(authority_runtime_summary_path.read_text(encoding="utf-8"))
            updated_note = authority_runtime_note_path.read_text(encoding="utf-8")

            self.assertEqual(promoted_facts[0]["primary_use"], "건축 시 자재를 가공하거나 맞출 때 쓴다")
            self.assertEqual(promoted_facts[1]["primary_use"], "소지품을 담는 배낭이다")
            self.assertEqual(promoted_facts[1]["secondary_use"], "등에 착용해 추가 수납 공간을 제공한다")
            self.assertEqual(promoted_facts[2]["identity_hint"], "소총")
            self.assertEqual(payload["report"]["changed_facts_count"], 3)
            self.assertEqual(payload["report"]["residual_translationese_count"], 0)
            self.assertEqual(payload["report"]["introduced_rendered_hard_fail_count"], 0)
            self.assertEqual(payload["report"]["introduced_rendered_warn_count"], 0)
            self.assertTrue(payload["report"]["sprint7_authority_preview_ready"])
            self.assertIn("body_role_lexical_cleanup", updated_summary)
            self.assertIn("## Body-Role Lexical Cleanup", updated_note)
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
