from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.build_dvf_3_3_complete_generation import build_complete_generation
from tools.build.dvf_3_3_runtime_compatibility import validate_generation_runtime_compatibility
from test_dvf_3_3_complete_generation import copy_generation_inputs


class DvfRuntimeCompatibilityTest(unittest.TestCase):
    def _report(self) -> dict:
        temporary = tempfile.TemporaryDirectory(prefix="iris-iar-runtime-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        repository = root / "repository"
        copy_generation_inputs(repository)
        generation = root / "generation"
        build_complete_generation(repository_root=repository, output_root=generation)
        return validate_generation_runtime_compatibility(generation_root=generation)

    def test_runtime_compatibility_named_checks(self) -> None:
        report = None
        with self.subTest(check_id="shared_generation_and_runtime_report"):
            try:
                report = self._report()
            except Exception as error:  # producer failure is distinct from blocked checks
                self.fail(f"runtime compatibility producer failed: {error}")
        if report is None:
            return

        with self.subTest(check_id="full_universe_and_payload_projection"):
            self.assertEqual(report["generation_key_identity_validation"], "PASS")
            self.assertEqual(report["runtime_projection_payload_mismatch_count"], 0)
            self.assertEqual(report["exact_duplicate_count"], 0)
            self.assertEqual(report["claims"]["rtc"], "not_claimed")

        with self.subTest(check_id="case_collision_boundary"):
            groups = [set(group["members"]) for group in report["ascii_lower_collision_groups"]]
            self.assertIn({"Base.LemonGrass", "Base.Lemongrass"}, groups)


if __name__ == "__main__":
    unittest.main()
