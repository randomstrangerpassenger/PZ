from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
HARNESS = REPO / "Iris/test/lua/runtime_optimization_metrics_harness.lua"


class IrisViewModelAllocationContractTest(unittest.TestCase):
    def test_method_lists_are_module_constants_and_hints_are_once_per_item(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(HARNESS), str(REPO), "viewmodel"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        values = dict(line.split("=", 1) for line in completed.stdout.splitlines() if "=" in line)
        self.assertEqual("100", values["items"])
        self.assertEqual("100", values["capability_hint_builds"])
        self.assertEqual("0", values["method_list_allocations"])
        self.assertEqual("PASS", values["instance_isolation"])
        self.assertEqual("PASS", values["custom_hybrid_parity"])

    def test_dynamic_debug_owners_have_caller_side_guards(self) -> None:
        bootstrap = (REPO / "Iris/media/lua/client/Iris/Util/IrisModuleBootstrap.lua").read_text(encoding="utf-8")
        translation = (REPO / "Iris/media/lua/client/Iris/IrisTranslationLoader.lua").read_text(encoding="utf-8")
        item_index = (REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua").read_text(encoding="utf-8")
        controller = (REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua").read_text(encoding="utf-8")
        self.assertIn("isDebugEnabled", bootstrap)
        self.assertIn("local debugEnabled = bootstrap.isDebugEnabled()", translation)
        self.assertIn("local debugEnabled = bootstrap.isDebugEnabled()", item_index)
        self.assertIn("local dynamicDebug = debugEnabled and debug or nil", controller)


if __name__ == "__main__":
    unittest.main()
