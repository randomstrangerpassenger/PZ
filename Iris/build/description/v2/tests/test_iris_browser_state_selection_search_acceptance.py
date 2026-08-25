from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())


class BrowserStateSelectionSearchAcceptanceTest(unittest.TestCase):
    def test_actual_standalone_lua_state_and_cache_contracts(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/browser_state_acceptance_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_BROWSER_STANDALONE_PASS", completed.stdout)
        self.assertIn("normalized_getter_calls=6", completed.stdout)
        self.assertIn("optional_load_calls=2", completed.stdout)
        self.assertIn("folded_cache_entries=1", completed.stdout)
        self.assertIn("get_all_items_calls=1", completed.stdout)
        self.assertIn("recovery_get_all_items_calls=2", completed.stdout)
        self.assertIn("prefix_reuse_count=1", completed.stdout)
        self.assertIn("tooltip_cache_hits=1", completed.stdout)

    def test_browserdata_compatibility_and_logging_source_guards(self) -> None:
        browser_root = REPO / "Iris/media/lua/client/Iris/UI/Browser"
        data_path = browser_root / "IrisBrowserData.lua"
        data_text = data_path.read_text(encoding="utf-8")
        self.assertEqual(1, data_text.count("IrisBrowserData._built ="))
        self.assertIn("function IrisBrowserData.getBuildState()", data_text)
        self.assertIn("function IrisBrowserData.isReady()", data_text)
        self.assertIn("function IrisBrowserData.ensureReady()", data_text)
        self.assertIn("function IrisBrowserData.getInstrumentation()", data_text)
        self.assertIn("IrisBrowserLifecycle", data_text)
        self.assertIn("IrisBrowserMetrics", data_text)

        projection = (browser_root / "IrisBrowserProjectionBuilder.lua").read_text(encoding="utf-8")
        lifecycle = (browser_root / "IrisBrowserLifecycle.lua").read_text(encoding="utf-8")
        metrics = (browser_root / "IrisBrowserMetrics.lua").read_text(encoding="utf-8")
        self.assertIn("function IrisBrowserProjectionBuilder.build", projection)
        self.assertIn("function IrisBrowserLifecycle.create", lifecycle)
        self.assertIn("function IrisBrowserMetrics.create", metrics)
        self.assertNotIn("function IrisBrowserData.ensureReady", lifecycle)

        main = (REPO / "Iris/media/lua/client/Iris/IrisMain.lua").read_text(encoding="utf-8")
        self.assertIn('ready = "BrowserData demand-build boundary ready"', main)
        self.assertNotIn("invoke = buildBrowserData", main)
        self.assertNotIn("local function buildBrowserData", main)

        forbidden = []
        for path in browser_root.glob("*.lua"):
            if path == data_path:
                continue
            text = path.read_text(encoding="utf-8")
            if "IrisBrowserData._built" in text or "BrowserData._built" in text:
                forbidden.append(path.name)
        self.assertEqual([], forbidden)

        controller = (browser_root / "IrisBrowserListController.lua").read_text(encoding="utf-8")
        self.assertIn("resolveSelectedPayload", controller)
        self.assertNotIn("for k, v in pairs(item)", controller)
        self.assertNotIn("for k, v in pairs(itemData)", controller)

        query = (browser_root / "IrisBrowserQuery.lua").read_text(encoding="utf-8")
        self.assertIn("searchSnapshot", query)
        self.assertIn("rowsByFullType", query)
        self.assertIn("prefixReuseCount", query)
        self.assertIn("copyRows", query)
        self.assertNotIn("table.sort(result", query)
        classification = (browser_root / "IrisBrowserClassificationIndex.lua").read_text(encoding="utf-8")
        self.assertIn("function IrisBrowserClassificationIndex.addTag", classification)
        self.assertNotIn("function IrisBrowserClassificationIndex.addItem", classification)
        static_data = (REPO / "Iris/media/lua/client/Iris/API/StaticData.lua").read_text(encoding="utf-8")
        self.assertIn("function StaticData.getFailureReason(key)", static_data)
        self.assertIn("function StaticData.reset(key)", static_data)


if __name__ == "__main__":
    unittest.main()
