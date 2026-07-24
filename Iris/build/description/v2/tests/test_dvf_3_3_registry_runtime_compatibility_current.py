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
            os.environ.get("IRIS_RTC_REQUIRED_MANIFEST", str(REQUIRED_MANIFEST))
        )
        candidate_probe = (
            os.environ.get("IRIS_RTC_CANDIDATE_MANIFEST_PROBE") == "1"
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
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "PASS")
            self.assertEqual(payload["implementation_toolchain_drift_count"], 0)
            self.assertEqual(payload["required_tool_missing_count"], 0)
            self.assertEqual(payload["required_tool_untracked_count"], 0)
            self.assertEqual(payload["required_tool_ignored_count"], 0)
            self.assertEqual(payload["unclassified_tool_dependency_count"], 0)
            self.assertEqual(payload["durable_bundle_role_count"], 11)
            if candidate_probe:
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
                self.assertEqual(
                    payload["resolution_mode"],
                    "post_adoption_live_manifest_default",
                )
                self.assertEqual(
                    payload["required_gate_state"],
                    "live_gate_adopted",
                )


if __name__ == "__main__":
    unittest.main()
