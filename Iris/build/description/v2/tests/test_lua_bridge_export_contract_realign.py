from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.export_dvf_3_3_lua_bridge import (
    BRIDGE_CHUNK_DIR,
    BRIDGE_CHUNK_MANIFEST_PATH,
    BRIDGE_DATA_PATH,
    BridgeExportContractError,
    export_lua_bridge,
    validate_chunk_bundle,
)


def reset_tmp_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_rendered(path: Path, *, count: int = 6) -> None:
    entries = {
        "Base.CanOpener": {
            "text_ko": "Can opener text.",
            "source": "composed",
        }
    }
    for index in range(2, count + 1):
        entries[f"Base.Item{index:03d}"] = {
            "text_ko": f"Item {index} text.",
            "source": "composed",
        }
    path.write_text(
        json.dumps(
            {
                "meta": {
                    "version": "test-v0",
                    "stats": {
                        "total": count,
                        "adopted_override": 0,
                        "adopted_composed": count,
                        "unadopted": 0,
                    },
                },
                "entries": entries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


class LuaBridgeExportContractRealignTest(unittest.TestCase):
    def test_default_route_writes_chunk_bundle_under_pinned_staging_root(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_lua_bridge_default_contract")
        try:
            rendered_path = tmp / "rendered.json"
            report_path = tmp / "bridge_report.json"
            legacy_lua_path = tmp / "IrisLayer3Data.lua"
            output_root = tmp / "default"
            write_rendered(rendered_path, count=6)

            report = export_lua_bridge(
                rendered_path=rendered_path,
                report_path=report_path,
                output_root=output_root,
                lua_output_path=legacy_lua_path,
                chunk_size=3,
            )

            manifest_path = output_root / "IrisLayer3DataChunks.lua"
            chunk_dir = output_root / "IrisLayer3DataChunks"
            self.assertTrue(manifest_path.exists())
            self.assertTrue((chunk_dir / "Chunk001.lua").exists())
            self.assertFalse(legacy_lua_path.exists())
            self.assertEqual(report["bridge_context"], "staging")
            self.assertEqual(report["format"], "chunk")
            self.assertEqual(report["authority_kind"], "chunk_bridge_output")
            self.assertEqual(report["output_manifest_path"], str(manifest_path))
            self.assertEqual(report["output_chunk_dir"], str(chunk_dir))
            self.assertEqual(report["input_scale"], "fixture")
            self.assertEqual(report["input_authority_status"], "fixture_non_authority")
            self.assertFalse(report["monolith_generated"])
            self.assertTrue(report["chunked"])
            self.assertEqual(report["adopted_count"], 6)
            self.assertEqual(report["unadopted_count"], 0)
            self.assertIsNotNone(report["manifest_hash"])
            self.assertEqual(len(report["chunk_hashes"]), report["chunk_count"])
            self.assertTrue(report["chunk_integrity"]["pass"])
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_protected_live_chunk_destination_is_rejected_before_write(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_lua_bridge_live_chunk_rejection")
        try:
            rendered_path = tmp / "rendered.json"
            write_rendered(rendered_path)

            with self.assertRaises(BridgeExportContractError):
                export_lua_bridge(
                    rendered_path=rendered_path,
                    report_path=tmp / "bridge_report.json",
                    chunk_manifest_path=BRIDGE_CHUNK_MANIFEST_PATH,
                    chunk_output_dir=BRIDGE_CHUNK_DIR,
                )
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_current_context_and_current_monolith_destination_are_rejected(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_lua_bridge_current_rejection")
        try:
            rendered_path = tmp / "rendered.json"
            write_rendered(rendered_path)

            with self.assertRaises(BridgeExportContractError):
                export_lua_bridge(
                    rendered_path=rendered_path,
                    report_path=tmp / "current_context_report.json",
                    bridge_context="current",
                )
            with self.assertRaises(BridgeExportContractError):
                export_lua_bridge(
                    rendered_path=rendered_path,
                    report_path=tmp / "live_monolith_report.json",
                    bridge_context="historical",
                    output_format="monolith",
                    lua_output_path=BRIDGE_DATA_PATH,
                )
            with self.assertRaises(BridgeExportContractError):
                export_lua_bridge(
                    rendered_path=rendered_path,
                    report_path=tmp / "staging_monolith_report.json",
                    bridge_context="staging",
                    output_format="monolith",
                    lua_output_path=tmp / "IrisLayer3Data.lua",
                )
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_explicit_historical_and_diagnostic_monolith_routes_are_preserved(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_lua_bridge_monolith_routes")
        try:
            rendered_path = tmp / "rendered.json"
            write_rendered(rendered_path, count=2)

            historical_report = export_lua_bridge(
                rendered_path=rendered_path,
                report_path=tmp / "historical_report.json",
                bridge_context="historical",
                output_format="monolith",
                lua_output_path=tmp / "historical" / "IrisLayer3Data.lua",
            )
            diagnostic_report = export_lua_bridge(
                rendered_path=rendered_path,
                report_path=tmp / "diagnostic_report.json",
                bridge_context="diagnostic",
                output_format="monolith",
                lua_output_path=tmp / "diagnostic" / "IrisLayer3Data.lua",
            )

            self.assertTrue((tmp / "historical" / "IrisLayer3Data.lua").exists())
            self.assertTrue((tmp / "diagnostic" / "IrisLayer3Data.lua").exists())
            self.assertEqual(historical_report["authority_kind"], "historical_monolith")
            self.assertEqual(diagnostic_report["authority_kind"], "diagnostic_monolith")
            self.assertTrue(historical_report["monolith_generated"])
            self.assertTrue(diagnostic_report["monolith_generated"])
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_chunk_bundle_determinism(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_lua_bridge_determinism")
        try:
            rendered_path = tmp / "rendered.json"
            write_rendered(rendered_path, count=6)

            first = export_lua_bridge(
                rendered_path=rendered_path,
                report_path=tmp / "first_report.json",
                output_root=tmp / "first",
                chunk_size=2,
            )
            second = export_lua_bridge(
                rendered_path=rendered_path,
                report_path=tmp / "second_report.json",
                output_root=tmp / "second",
                chunk_size=2,
            )

            self.assertEqual(first["manifest_hash"], second["manifest_hash"])
            self.assertEqual(
                [row["sha256"] for row in first["chunk_hashes"]],
                [row["sha256"] for row in second["chunk_hashes"]],
            )
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_chunk_integrity_reports_missing_orphan_and_duplicate_chunks(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_lua_bridge_integrity")
        try:
            manifest_path = tmp / "IrisLayer3DataChunks.lua"
            chunk_dir = tmp / "IrisLayer3DataChunks"
            chunk_dir.mkdir(parents=True)
            manifest_path.write_text(
                "\n".join(
                    [
                        "local chunkModules = {",
                        '    "Iris/Data/IrisLayer3DataChunks/Chunk001",',
                        '    "Iris/Data/IrisLayer3DataChunks/Chunk003",',
                        '    "Iris/Data/IrisLayer3DataChunks/Chunk004",',
                        "}",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (chunk_dir / "Chunk001.lua").write_text(
                "\n".join(
                    [
                        "return {",
                        '    ["Base.Duplicate"] = {',
                        '        ["text_ko"] = "one",',
                        "    },",
                        "}",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (chunk_dir / "Chunk002.lua").write_text("return {}\n", encoding="utf-8")
            (chunk_dir / "Chunk003.lua").write_text(
                "\n".join(
                    [
                        "return {",
                        '    ["Base.Duplicate"] = {',
                        '        ["text_ko"] = "two",',
                        "    },",
                        "}",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_chunk_bundle(
                chunk_manifest_path=manifest_path,
                chunk_output_dir=chunk_dir,
            )

            self.assertFalse(report["pass"])
            self.assertEqual(report["missing_chunks"], ["Chunk004.lua"])
            self.assertEqual(report["orphan_chunks"], ["Chunk002.lua"])
            self.assertEqual(report["duplicate_keys"][0]["full_type"], "Base.Duplicate")
            self.assertIn("manifest_references_missing_chunks", report["failures"])
            self.assertIn("chunk_dir_has_orphan_chunks", report["failures"])
            self.assertIn("duplicate_full_type_across_chunks", report["failures"])
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_bridge_report_forbidden_claim_scan(self) -> None:
        tmp = reset_tmp_dir(ROOT / "tests" / "_tmp_lua_bridge_forbidden_claims")
        try:
            rendered_path = tmp / "rendered.json"
            write_rendered(rendered_path)
            report = export_lua_bridge(
                rendered_path=rendered_path,
                report_path=tmp / "bridge_report.json",
                output_root=tmp / "default",
            )
            report_text = json.dumps(report, ensure_ascii=False)
            forbidden_claims = [
                "release readiness",
                "package readiness",
                "runtime rollout",
                "current baseline replacement",
                "live chunk replacement",
                "Browser/Wiki/Tooltip behavior change",
                "quality exposure",
            ]
            for claim in forbidden_claims:
                self.assertNotIn(claim, report_text)
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
