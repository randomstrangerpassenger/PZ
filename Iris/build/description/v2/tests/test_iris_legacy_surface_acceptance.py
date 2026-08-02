from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
sys.path.insert(0, str(REPO / "Iris" / "test"))
from core_refactor_evidence import load_bound_evidence  # noqa: E402


class LegacySurfaceAcceptanceTest(unittest.TestCase):
    def test_pz_capability_tooltip_taxonomy_and_variant_adapter(self) -> None:
        before = load_bound_evidence(
            REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.jsonl"
        )
        after = load_bound_evidence(
            REPO, "Iris/_docs/refactor/core_refactor/phase5_legacy_surface_acceptance.jsonl"
        )
        rows = {row["case_id"]: row for row in after}
        self.assertEqual(
            {
                "legacy_acceptance.capability_tooltip",
                "legacy_acceptance.taxonomy_projection",
                "legacy_acceptance.variant_adapter",
            },
            rows.keys(),
        )
        self.assertTrue(all(row["owner_change"] == 6 for row in after))
        self.assertTrue(all(row["status"] == "pass" for row in after))
        self.assertTrue(all(row["time_axis"] == "post_refactor_acceptance" for row in after))

        old = next(row for row in before if row["case_id"] == "legacy.pz_surface")["observed"]
        new = rows["legacy_acceptance.capability_tooltip"]["observed"]
        self.assertEqual(old["capabilities"], new["capabilities"])
        self.assertEqual(old["tags"], new["tags"])
        self.assertEqual(old["tooltip_tags"], new["tooltip_tags"])
        self.assertTrue(new["has_scrap_capability"])

        taxonomy = rows["legacy_acceptance.taxonomy_projection"]["observed"]
        self.assertEqual(("Tool", "1-B"), (taxonomy["category"], taxonomy["subcategory"]))
        self.assertGreaterEqual(taxonomy["tag_count"], 2)
        self.assertTrue(rows["legacy_acceptance.variant_adapter"]["observed"]["sorted_by_display"])

    def test_actual_standalone_missing_module_and_global_fallback(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/legacy_surface_adapter_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_LEGACY_ADAPTER_PASS", completed.stdout)
        self.assertIn("missing_load_calls=1", completed.stdout)
        self.assertIn("global_fallback=true", completed.stdout)
        self.assertIn("capability_preserved=true", completed.stdout)

    def test_compatibility_boundary_source_and_manifest_guards(self) -> None:
        browser_root = REPO / "Iris/media/lua/client/Iris/UI/Browser"
        query = (browser_root / "IrisBrowserQuery.lua").read_text(encoding="utf-8")
        variant = (browser_root / "IrisBrowserVariantIndex.lua").read_text(encoding="utf-8")
        static_data = (REPO / "Iris/media/lua/client/Iris/API/StaticData.lua").read_text(encoding="utf-8")
        self.assertNotIn("IrisData", query)
        self.assertIn("function IrisBrowserVariantIndex.getGroupVariants", variant)
        self.assertIn("function StaticData.getLegacyIrisData", static_data)
        self.assertEqual(1, static_data.count("type(IrisData)"))

        lua_files = list((REPO / "Iris/media/lua/client/Iris").rglob("*.lua"))
        group_definitions = [
            path.relative_to(REPO).as_posix()
            for path in lua_files
            if "function IrisBrowserData.getGroupVariants" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(["Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua"], group_definitions)

        supported = json.loads(
            (REPO / "Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json").read_text(encoding="utf-8")
        )
        surfaces = {row["symbol"]: row for row in supported["surfaces"]}
        self.assertEqual("(groupId)->table|nil", surfaces["IrisBrowserData.getGroupVariants"]["signature_or_shape"])
        self.assertEqual("supported_adapter", surfaces["IrisBrowserData.getGroupVariants"]["support_status"])
        self.assertEqual("supported", surfaces["IrisAPI.getCapabilities"]["support_status"])
        self.assertEqual("supported", surfaces["IrisAPI.hasCapability"]["support_status"])

        for path in (
            browser_root / "IrisBrowserVariantIndex.lua",
            browser_root / "IrisBrowserCategoryIndex.lua",
            REPO / "Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua",
        ):
            text = path.read_text(encoding="utf-8").lower()
            for forbidden in ("recommendation =", "priorityscore =", "qualityscore ="):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
