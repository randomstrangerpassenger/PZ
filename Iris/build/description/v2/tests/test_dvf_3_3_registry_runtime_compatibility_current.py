from __future__ import annotations

import json
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
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "required_gate.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(VALIDATOR),
                    "--required-gate",
                    "--required-manifest",
                    str(REQUIRED_MANIFEST),
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
            self.assertEqual(
                payload["resolution_mode"],
                "post_adoption_live_manifest_default",
            )
            self.assertEqual(payload["required_gate_state"], "live_gate_adopted")


if __name__ == "__main__":
    unittest.main()
