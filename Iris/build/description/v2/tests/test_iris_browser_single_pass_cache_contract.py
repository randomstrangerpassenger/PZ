from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]


class IrisBrowserSinglePassCacheContractTest(unittest.TestCase):
    def test_row_cache_and_scalar_classification_contract(self) -> None:
        browser = REPO / "Iris/media/lua/client/Iris/UI/Browser"
        data = (browser / "IrisBrowserData.lua").read_text(encoding="utf-8")
        projection = (browser / "IrisBrowserProjectionBuilder.lua").read_text(encoding="utf-8")
        lifecycle = (browser / "IrisBrowserLifecycle.lua").read_text(encoding="utf-8")
        metrics = (browser / "IrisBrowserMetrics.lua").read_text(encoding="utf-8")
        classification = (browser / "IrisBrowserClassificationIndex.lua").read_text(encoding="utf-8")
        query = (browser / "IrisBrowserQuery.lua").read_text(encoding="utf-8")
        variant = (browser / "IrisBrowserVariantIndex.lua").read_text(encoding="utf-8")

        self.assertIn("IrisBrowserLifecycle", data)
        self.assertIn("rowsByFullType", projection)
        self.assertIn('StaticData.get("classifications")', projection)
        self.assertNotIn("Tags.getTagsForItem(item)", projection)
        self.assertIn("function lifecycle.ensureReady()", lifecycle)
        self.assertIn("function lifecycle.resetForReload()", lifecycle)
        self.assertIn("function metrics.snapshot(state, generation)", metrics)
        self.assertNotIn("StaticData.get(\"classifications\")", data)
        self.assertIn("function IrisBrowserClassificationIndex.addTag", classification)
        self.assertNotIn("function IrisBrowserClassificationIndex.addItem", classification)
        self.assertIn("searchSnapshot", query)
        self.assertNotIn("table.sort(result", query)
        self.assertIn("categoryName .. \".\" .. subcategoryName", variant)
        self.assertIn("row.primaryTag", variant)

    def test_browser_acceptance_harness_exercises_single_pass_and_locale_owner(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
