from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
HARNESS = REPO / "Iris/test/lua/lazy_lookup_acceptance_harness.lua"


class Layer3LazyLookupContractTest(unittest.TestCase):
    def test_layer3_lazy_lookup_contract(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(HARNESS), str(REPO), "layer3"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_LAYER3_LAZY_LOOKUP_PASS", completed.stdout)
        self.assertIn("parity_count=2105", completed.stdout)
        self.assertIn("first_lookup_loaded_chunks=1", completed.stdout)
        self.assertIn(
            "first_lookup_loaded_modules=Iris/Data/IrisLayer3DataChunks/Chunk001",
            completed.stdout,
        )
        self.assertIn("initial_loaded_chunks=2", completed.stdout)
        self.assertIn(
            "initial_loaded_modules=Iris/Data/IrisLayer3DataChunks/Chunk001,"
            "Iris/Data/IrisLayer3DataChunks/Chunk002",
            completed.stdout,
        )
        self.assertIn("router_unavailable_count=1", completed.stdout)
        self.assertIn("normal_miss_facade_loads=0", completed.stdout)


if __name__ == "__main__":
    unittest.main()
