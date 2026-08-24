from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]


class IrisObjectAccessFastPathTest(unittest.TestCase):
    def test_fixed_arity_lua_result_shape_parity(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/fixtures/object_access_fast_path_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_OBJECT_ACCESS_FAST_PATH_PASS", completed.stdout)
        self.assertIn("generic_routing=predecessor", completed.stdout)

    def test_generic_production_path_is_not_routed_without_new_pz_evidence(self) -> None:
        source = (REPO / "Iris/media/lua/client/Iris/Util/IrisObjectAccess.lua").read_text(encoding="utf-8")
        generic = source.split("function IrisObjectAccess.call(target", 1)[1].split(
            "function IrisObjectAccess.invokeMethod", 1
        )[0]
        self.assertIn("local args = {...}", generic)
        self.assertNotIn("call0(", generic)
        self.assertNotIn("call1(", generic)


if __name__ == "__main__":
    unittest.main()
