from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
HARNESS = REPO / "Iris/test/lua/lazy_lookup_acceptance_harness.lua"


class UseCaseLazyLookupContractTest(unittest.TestCase):
    def test_usecase_lazy_lookup_contract(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(HARNESS), str(REPO), "usecase"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_USECASE_LAZY_LOOKUP_PASS", completed.stdout)
        self.assertIn("parity_count=1631", completed.stdout)
        self.assertIn("line_count_loaded_chunks=0", completed.stdout)
        self.assertIn("first_lookup_loaded_chunks=1", completed.stdout)
        self.assertIn(
            "first_lookup_loaded_modules=Iris/Data/UseCaseDescriptions/Chunk001",
            completed.stdout,
        )
        self.assertIn(
            "initial_loaded_modules=Iris/Data/UseCaseDescriptions/Chunk001,"
            "Iris/Data/UseCaseDescriptions/Chunk002",
            completed.stdout,
        )
        self.assertIn("router_unavailable_count=1", completed.stdout)
        self.assertIn("normal_miss_facade_loads=0", completed.stdout)


if __name__ == "__main__":
    unittest.main()
