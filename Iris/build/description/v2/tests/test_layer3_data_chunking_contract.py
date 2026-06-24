from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IRIS_MOD_ROOT = ROOT.parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.export_dvf_3_3_lua_bridge import (
    export_lua_bridge,
    write_chunked_lua_bridge_from_monolith,
)


def reset_tmp_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


class Layer3DataChunkingContractTest(unittest.TestCase):
    def test_export_lua_bridge_writes_optional_chunk_manifest(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_layer3_data_chunking")
        try:
            rendered_path = tmp / "rendered.json"
            lua_output_path = tmp / "IrisLayer3Data.lua"
            chunk_output_dir = tmp / "IrisLayer3DataChunks"
            chunk_manifest_path = tmp / "IrisLayer3DataChunks.lua"
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
                            },
                            "Base.Wrench": {
                                "text_ko": "정비 작업에 쓰는 공구다.",
                                "source": "composed",
                            },
                            "Base.Hammer": {
                                "text_ko": "못질에 쓰는 도구다.",
                                "source": "composed",
                            },
                            "Base.Tongs": {
                                "text_ko": "집게로 물건을 잡는 도구다.",
                                "source": "composed",
                            },
                            "Base.Saw": {
                                "text_ko": "목재 절단에 쓰는 도구다.",
                                "source": "composed",
                            },
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            report = export_lua_bridge(
                rendered_path=rendered_path,
                report_path=report_path,
                chunk_output_dir=chunk_output_dir,
                chunk_manifest_path=chunk_manifest_path,
                chunk_size=2,
                output_root=tmp,
            )

            self.assertFalse(lua_output_path.exists())
            self.assertTrue(chunk_manifest_path.exists())
            self.assertTrue((chunk_output_dir / "Chunk001.lua").exists())
            self.assertTrue((chunk_output_dir / "Chunk002.lua").exists())
            self.assertTrue((chunk_output_dir / "Chunk003.lua").exists())
            self.assertEqual(report["source_entry_count"], 5)
            self.assertEqual(report["runtime_entry_count"], 6)
            self.assertTrue(report["chunked"])
            self.assertEqual(report["chunk_size"], 2)
            self.assertEqual(report["chunk_count"], 3)
            self.assertEqual(len(report["chunk_modules"]), 3)

            manifest_text = chunk_manifest_path.read_text(encoding="utf-8")
            self.assertIn('local chunkModules = {', manifest_text)
            self.assertIn('"Iris/Data/IrisLayer3DataChunks/Chunk001"', manifest_text)
            self.assertIn('"Iris/Data/IrisLayer3DataChunks/Chunk003"', manifest_text)
            self.assertIn("IrisLayer3Data = data", manifest_text)
            self.assertIn("return data", manifest_text)

            chunk_text = "\n".join(
                path.read_text(encoding="utf-8") for path in sorted(chunk_output_dir.glob("Chunk*.lua"))
            )
            self.assertIn("return {", chunk_text)
            self.assertIn('["Base.CanOpener"]', chunk_text)
            self.assertIn('["Base.TinOpener"]', chunk_text)
            self.assertIn('["text_ko"] = "', chunk_text)
            self.assertNotIn('["quality_flag"]', chunk_text)
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_export_lua_bridge_default_keeps_monolith_only_contract(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_layer3_data_default")
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
                report_path=report_path,
                output_root=tmp,
            )

            self.assertFalse(lua_output_path.exists())
            self.assertTrue((tmp / "IrisLayer3DataChunks.lua").exists())
            self.assertTrue((tmp / "IrisLayer3DataChunks" / "Chunk001.lua").exists())
            self.assertTrue(report["chunked"])
            self.assertEqual(report["chunk_count"], 1)
            self.assertFalse(report["monolith_generated"])
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_layer3_renderer_uses_chunk_manifest_without_monolith_fallback(self) -> None:
        renderer_path = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua"
        renderer_text = renderer_path.read_text(encoding="utf-8")

        self.assertIn('safeRequire("Iris/Data/IrisLayer3DataChunks")', renderer_text)
        self.assertIn('require, "Iris/Data/IrisLayer3DataChunks"', renderer_text)
        self.assertNotIn('safeRequire("Iris/Data/IrisLayer3Data")', renderer_text)
        self.assertNotIn('require, "Iris/Data/IrisLayer3Data"', renderer_text)
        self.assertIn("IrisLayer3Data = chunkLoaded", renderer_text)

    def test_existing_monolith_can_generate_chunk_bundle_without_rewriting_monolith(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_layer3_existing_monolith_chunking")
        try:
            monolith_path = tmp / "IrisLayer3Data.lua"
            chunk_output_dir = tmp / "IrisLayer3DataChunks"
            chunk_manifest_path = tmp / "IrisLayer3DataChunks.lua"
            monolith_text = "\n".join(
                [
                    "-- Auto-generated by export_dvf_3_3_lua_bridge.py.",
                    "-- Do not edit manually. Rebuild from Iris/build/description/v2/output/dvf_3_3_rendered.json.",
                    "",
                    "local data = {",
                    '    ["Base.CanOpener"] = {',
                    '        ["publish_state"] = "exposed",',
                    '        ["source"] = "composed_v2_preview",',
                    '        ["text_ko"] = "\\237\\134\\181\\236\\161\\176\\235\\166\\188 \\236\\151\\176\\235\\139\\164.",',
                    "    },",
                    '    ["Base.Hammer"] = {',
                    '        ["publish_state"] = "exposed",',
                    '        ["source"] = "composed_v2_preview",',
                    '        ["text_ko"] = "\\235\\167\\157\\236\\185\\152\\235\\165\\188 \\236\\147\\180\\235\\139\\164.",',
                    "    },",
                    '    ["Base.Wrench"] = {',
                    '        ["publish_state"] = "internal_only",',
                    '        ["source"] = "composed_v2_preview",',
                    '        ["text_ko"] = "\\236\\160\\149\\235\\185\\132\\236\\151\\144 \\236\\147\\180\\235\\139\\164.",',
                    "    },",
                    "}",
                    "",
                    "IrisLayer3Data = data",
                    "",
                    "return data",
                    "",
                ]
            )
            monolith_path.write_text(monolith_text, encoding="utf-8")

            report = write_chunked_lua_bridge_from_monolith(
                lua_input_path=monolith_path,
                chunk_output_dir=chunk_output_dir,
                chunk_manifest_path=chunk_manifest_path,
                chunk_size=2,
            )

            self.assertEqual(report["entry_count"], 3)
            self.assertEqual(report["chunk_count"], 2)
            self.assertEqual(monolith_path.read_text(encoding="utf-8"), monolith_text)
            self.assertTrue((chunk_output_dir / "Chunk001.lua").exists())
            self.assertTrue((chunk_output_dir / "Chunk002.lua").exists())
            manifest_text = chunk_manifest_path.read_text(encoding="utf-8")
            self.assertIn('"Iris/Data/IrisLayer3DataChunks/Chunk001"', manifest_text)
            self.assertIn("IrisLayer3Data = data", manifest_text)
            chunk_text = (chunk_output_dir / "Chunk001.lua").read_text(encoding="utf-8")
            self.assertIn('["Base.CanOpener"]', chunk_text)
            self.assertIn('["Base.Hammer"]', chunk_text)
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_workspace_active_media_excludes_layer3_monolith(self) -> None:
        layer3_data_path = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3Data.lua"
        chunk_manifest_path = (
            IRIS_MOD_ROOT
            / "media"
            / "lua"
            / "client"
            / "Iris"
            / "Data"
            / "IrisLayer3DataChunks.lua"
        )
        chunk_dir = chunk_manifest_path.with_suffix("")

        self.assertFalse(layer3_data_path.exists())
        self.assertTrue(chunk_manifest_path.exists())
        self.assertTrue((chunk_dir / "Chunk001.lua").exists())


if __name__ == "__main__":
    unittest.main()
