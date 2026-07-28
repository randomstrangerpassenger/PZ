from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
VALIDATOR = (
    REPO_ROOT
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "tools"
    / "build"
    / "validate_dvf_3_3_registry_runtime_compatibility.py"
)
REQUIRED_MANIFEST = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "current_route_required_validations.json"
)


class RegistryRuntimeCompatibilityCurrentRouteTest(unittest.TestCase):
    def test_required_gate_runs_standalone_subprocess(self) -> None:
        required_manifest = Path(
            os.environ.get(
                "IRIS_RTC_TEST_ONLY_EXPLICIT_REQUIRED_MANIFEST",
                str(REQUIRED_MANIFEST),
            )
        )
        candidate_probe = (
            os.environ.get("IRIS_RTC_TEST_ONLY_CANDIDATE_MANIFEST_PROBE")
            == "1"
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "required_gate.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(VALIDATOR),
                    "--required-gate",
                    "--required-manifest",
                    str(required_manifest),
                    "--out",
                    str(output),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            if candidate_probe:
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(payload["status"], "PASS")
                self.assertEqual(
                    payload["implementation_toolchain_drift_count"],
                    0,
                )
                self.assertEqual(payload["required_tool_missing_count"], 0)
                self.assertEqual(payload["required_tool_untracked_count"], 0)
                self.assertEqual(payload["required_tool_ignored_count"], 0)
                self.assertEqual(
                    payload["unclassified_tool_dependency_count"],
                    0,
                )
                self.assertEqual(payload["durable_bundle_role_count"], 11)
                self.assertEqual(
                    payload["resolution_mode"],
                    "candidate_required_manifest_override",
                )
                self.assertEqual(payload["required_gate_state"], "not_adopted")
                self.assertEqual(
                    payload["candidate_manifest_route_status"],
                    "PASS",
                )
            else:
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertEqual(payload["status"], "BLOCKED")
                self.assertEqual(
                    payload["failure_code"],
                    "registry_runtime_compatibility_current_source_stale",
                )
                self.assertFalse((Path(temporary) / "required-gate-temp").exists())

    def test_explicit_canonical_surface_validation_cannot_bypass_staleness(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "surface.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(VALIDATOR),
                    "--surface-validation",
                    "--surface-input-manifest",
                    str(root / "unread-surface.json"),
                    "--policy-context",
                    "canonical_durable",
                    "--policy",
                    str(root / "unread-policy.json"),
                    "--disposition",
                    str(root / "unread-disposition.json"),
                    "--binding-manifest",
                    str(root / "unread-binding.json"),
                    "--out",
                    str(output),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertEqual(
                payload["failure_code"],
                "registry_runtime_compatibility_current_source_stale",
            )
            self.assertFalse((root / "unread-surface.json").exists())


if __name__ == "__main__":
    unittest.main()
