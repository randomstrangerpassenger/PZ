from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]


class RegistryRuntimeCompatibilityWindowsTest(unittest.TestCase):
    def test_wrapper_requires_both_fixed_routes(self) -> None:
        wrapper = (
            REPO_ROOT
            / "Iris"
            / "tools"
            / "inspect_registry_runtime_compatibility.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("windows_uv_python", wrapper)
        self.assertIn("windows_record_sidecar", wrapper)
        self.assertIn("--surface-validation", wrapper)
        self.assertIn("export_registry_runtime_records.py", wrapper)

    def test_windows_cardinality_loss_fixture_is_mapped(self) -> None:
        fixture = (
            REPO_ROOT
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "tests"
            / "fixtures"
            / "registry_runtime_compatibility"
            / "roadmap_fixtures.json"
        ).read_text(encoding="utf-8")
        self.assertIn('"fixture_id": "RTC-RM-08"', fixture)
        self.assertIn("cardinality loss", fixture)


if __name__ == "__main__":
    unittest.main()
