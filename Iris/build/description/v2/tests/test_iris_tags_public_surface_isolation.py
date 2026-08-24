from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]


class IrisTagsPublicSurfaceIsolationTest(unittest.TestCase):
    def test_public_exports_remain_frozen_and_backing_tables_are_unreachable(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/fixtures/tags_public_surface_isolation_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_TAGS_PUBLIC_SURFACE_ISOLATION_PASS", completed.stdout)
        self.assertIn("exported=getTags,getTagsForItem,hasTag,isClassified", completed.stdout)

    def test_tags_and_iris_api_do_not_export_browser_raw_accessors(self) -> None:
        tags = (REPO / "Iris/media/lua/client/Iris/API/Tags.lua").read_text(encoding="utf-8")
        api = (REPO / "Iris/media/lua/client/Iris/IrisAPI.lua").read_text(encoding="utf-8")
        self.assertNotIn("getRaw", tags)
        self.assertNotIn("getBacking", tags)
        self.assertEqual('IrisAPI.Tags = require("Iris/API/Tags")', next(
            line for line in api.splitlines() if line.startswith("IrisAPI.Tags =")
        ))


if __name__ == "__main__":
    unittest.main()
