from __future__ import annotations

import json
import sys
import shutil
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IRIS_MOD_ROOT = ROOT.parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.build_interaction_cluster_phase_d_runtime import write_checklist
from tools.build.export_dvf_3_3_lua_bridge import export_lua_bridge
from tools.build.validate_interaction_cluster_phase_d_runtime import (
    build_phase_d_runtime_report,
    read_browser_runtime_text,
)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def reset_tmp_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


class InteractionClusterPhaseDRuntimeTest(unittest.TestCase):
    def test_export_lua_bridge_writes_generated_module(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_phase_d_runtime_bridge")
        try:
            rendered_path = tmp / "rendered.json"
            lua_output_path = tmp / "IrisLayer3Data.lua"
            report_path = tmp / "bridge_report.json"
            rendered_path.write_text(
                json.dumps(
                    {
                        "meta": {"version": "test-v0"},
                        "entries": {
                            "Base.CanOpener": {
                                "text_ko": "통조림 개봉에 쓰는 도구다.",
                                "source": "composed",
                                "quality_flag": "function_narrow",
                            }
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            report = export_lua_bridge(
                rendered_path=rendered_path,
                lua_output_path=lua_output_path,
                report_path=report_path,
                bridge_context="historical",
                output_format="monolith",
            )

            self.assertTrue(lua_output_path.exists())
            self.assertEqual(report["source_entry_count"], 1)
            self.assertEqual(report["runtime_entry_count"], 2)
            bridge_text = lua_output_path.read_text(encoding="utf-8")
            self.assertIn('["Base.CanOpener"]', bridge_text)
            self.assertIn('["Base.TinOpener"]', bridge_text)
            self.assertIn('["text_ko"] = "', bridge_text)
            self.assertIn("IrisLayer3Data = data", bridge_text)
            self.assertNotIn('["quality_flag"]', bridge_text)
            self.assertNotIn('["publish_state"]', bridge_text)
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_export_lua_bridge_merges_publish_state_preview_when_supplied(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_phase_d_runtime_bridge_publish_state")
        try:
            rendered_path = tmp / "rendered.json"
            publish_preview_path = tmp / "publish_preview.jsonl"
            lua_output_path = tmp / "IrisLayer3Data.lua"
            report_path = tmp / "bridge_report.json"
            rendered_path.write_text(
                json.dumps(
                    {
                        "meta": {"version": "test-v0"},
                        "entries": {
                            "Base.CanOpener": {
                                "text_ko": "통조림 개봉에 쓰는 도구다.",
                                "source": "composed",
                            },
                            "Base.Wrench": {
                                "text_ko": "정비 작업에 쓰는 공구다.",
                                "source": "composed",
                            },
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            publish_preview_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "item_id": "Base.CanOpener",
                                "runtime_state": "active",
                                "quality_state": "weak",
                                "publish_state": "internal_only",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "item_id": "Base.Wrench",
                                "runtime_state": "active",
                                "quality_state": "strong",
                                "publish_state": "exposed",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = export_lua_bridge(
                rendered_path=rendered_path,
                publish_preview_path=publish_preview_path,
                lua_output_path=lua_output_path,
                report_path=report_path,
                bridge_context="historical",
                output_format="monolith",
            )

            bridge_text = lua_output_path.read_text(encoding="utf-8")
            self.assertIn('["publish_state"] = "internal_only"', bridge_text)
            self.assertIn('["publish_state"] = "exposed"', bridge_text)
            self.assertEqual(report["publish_state_entry_count"], 3)
            self.assertEqual(report["source_publish_state_counts"]["internal_only"], 1)
            self.assertEqual(report["source_publish_state_counts"]["exposed"], 1)
            self.assertEqual(report["runtime_publish_state_counts"]["internal_only"], 2)
            self.assertEqual(report["runtime_publish_state_counts"]["exposed"], 1)
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_phase_d_runtime_report_passes_with_consumer_files_present(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_phase_d_runtime_report")
        try:
            runtime_dir = tmp / "phase_d_runtime"
            lua_output_path = tmp / "IrisLayer3Data.lua"
            chunk_manifest_path = tmp / "IrisLayer3DataChunks.lua"
            chunk_output_dir = tmp / "IrisLayer3DataChunks"
            bridge_report_path = runtime_dir / "phase_d_lua_bridge_report.json"
            report = None

            export_lua_bridge(
                rendered_path=ROOT / "output" / "dvf_3_3_rendered.json",
                report_path=bridge_report_path,
                chunk_output_dir=chunk_output_dir,
                chunk_manifest_path=chunk_manifest_path,
                output_root=tmp,
            )
            report = build_phase_d_runtime_report(
                rendered_path=ROOT / "output" / "dvf_3_3_rendered.json",
                bridge_report_path=bridge_report_path,
                layer3_chunk_manifest_path=chunk_manifest_path,
                layer3_chunk_dir=chunk_output_dir,
                layer3_renderer_path=IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua",
                browser_path=IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Browser" / "IrisBrowser.lua",
                panel_path=IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisWikiPanel.lua",
                wiki_sections_path=IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisWikiSections.lua",
                output_path=runtime_dir / "phase_d_runtime_report.json",
            )

            self.assertEqual(report["overall_status"], "ready_for_in_game_validation")
            self.assertEqual(report["rendered_entry_count"], 6)
            bridge_report = load_json(bridge_report_path)
            self.assertEqual(bridge_report["source_entry_count"], 6)
            self.assertGreaterEqual(bridge_report["runtime_entry_count"], 6)
            self.assertIn(
                {
                    "source_full_type": "Base.CanOpener",
                    "alias_full_type": "Base.TinOpener",
                },
                bridge_report["applied_aliases"],
            )
            self.assertIn("runtime_publish_state_counts", bridge_report)
            wiki_sections = (
                IRIS_MOD_ROOT
                / "media"
                / "lua"
                / "client"
                / "Iris"
                / "UI"
                / "Wiki"
                / "IrisWikiSections.lua"
            ).read_text(encoding="utf-8")
            item_access = (
                IRIS_MOD_ROOT
                / "media"
                / "lua"
                / "client"
                / "Iris"
                / "Util"
                / "IrisItemAccess.lua"
            ).read_text(encoding="utf-8")
            self.assertIn('require("Iris/Util/IrisItemAccess")', wiki_sections)
            self.assertIn('require("Iris/Util/ItemKey")', item_access)
            self.assertIn(
                'require("Iris/UI/Layer3/IrisLayer3DisplayFormatter")',
                wiki_sections,
            )
            self.assertIn("ItemAccess.getFullType(item)", wiki_sections)
            self.assertIn("Layer3DisplayFormatter.format(l3text)", wiki_sections)
            self.assertIn("renderLayer3Section", wiki_sections)
            renderer_text = (
                IRIS_MOD_ROOT
                / "media"
                / "lua"
                / "client"
                / "Iris"
                / "Data"
                / "layer3_renderer.lua"
            ).read_text(encoding="utf-8")
            self.assertIn("publish_state", renderer_text)
            self.assertIn("internal_only", renderer_text)
            browser_text = read_browser_runtime_text(
                IRIS_MOD_ROOT
                / "media"
                / "lua"
                / "client"
                / "Iris"
                / "UI"
                / "Browser"
                / "IrisBrowser.lua"
            )
            self.assertIn('require("Iris/UI/Browser/IrisBrowserItemIndex")', browser_text)
            self.assertIn('require("Iris/UI/Browser/IrisBrowserClassificationIndex")', browser_text)
            self.assertIn('require("Iris/UI/Browser/IrisBrowserCategoryIndex")', browser_text)
            self.assertIn('require("Iris/UI/Browser/IrisBrowserFilters")', browser_text)
            self.assertIn('require("Iris/UI/Browser/IrisBrowserQuery")', browser_text)
            self.assertIn('require("Iris/UI/Browser/IrisBrowserVariantIndex")', browser_text)
            self.assertLess(
                browser_text.index("IrisAPI.Description.getDescription"),
                browser_text.index("renderLayer3Section(item)"),
            )
            panel_text = (
                IRIS_MOD_ROOT
                / "media"
                / "lua"
                / "client"
                / "Iris"
                / "UI"
                / "Wiki"
                / "IrisWikiPanel.lua"
            ).read_text(encoding="utf-8")
            self.assertIn('for line in layer3Section:gmatch("[^\\n]+") do', panel_text)
            context_menu_text = (
                IRIS_MOD_ROOT
                / "media"
                / "lua"
                / "client"
                / "Iris"
                / "UI"
                / "Wiki"
                / "IrisContextMenu.lua"
            ).read_text(encoding="utf-8")
            self.assertIn("resolveFirstInventoryItem", context_menu_text)
            self.assertIn('ObjectAccess.call(candidate, "getItems")', context_menu_text)
            self.assertIn('ObjectAccess.call(container, "get", 0)', context_menu_text)
            self.assertNotIn("doReloadMenuForBullets", context_menu_text)
            bullet_compat_text = (
                IRIS_MOD_ROOT
                / "media"
                / "lua"
                / "client"
                / "Iris"
                / "Compat"
                / "IrisBulletReloadCompat.lua"
            ).read_text(encoding="utf-8")
            self.assertIn("IrisBulletReloadCompat.install", bullet_compat_text)
            self.assertIn("_irisSafeBulletReloadPatchApplied", bullet_compat_text)
            self.assertIn("buildAmmoReloadTooltipDescription", bullet_compat_text)
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_write_checklist_emits_phase_d_manual_steps(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_phase_d_runtime_checklist")
        try:
            checklist_path = write_checklist(tmp / "phase_d_in_game_checklist.md")
            text = checklist_path.read_text(encoding="utf-8")
            self.assertIn("Iris: View More", text)
            self.assertIn("Base.TinOpener", text)
            self.assertIn("Enable the `Iris` mod", text)
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
