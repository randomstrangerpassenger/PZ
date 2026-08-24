from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]


class IrisLineCountLazyValidationTest(unittest.TestCase):
    def test_first_demand_metadata_state_matrix(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/fixtures/line_count_lazy_validation_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_LINE_COUNT_LAZY_VALIDATION_PASS", completed.stdout)
        self.assertIn("matrix=valid,chunk-invalid,line-invalid,mismatch", completed.stdout)

    def test_lookup_module_has_no_top_level_index_require(self) -> None:
        source = (REPO / "Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua").read_text(
            encoding="utf-8"
        )
        prefix = source.split("local function ensureIndexMetadataSnapshot()", 1)[0]
        self.assertNotIn('safeRequire("Iris/Data/UseCaseDescriptions/ChunkIndex")', prefix)
        self.assertNotIn('safeRequire("Iris/Data/UseCaseDescriptions/LineCountIndex")', prefix)
        self.assertIn("crossCheckState", source)
        self.assertIn("not_applicable", source)


if __name__ == "__main__":
    unittest.main()
