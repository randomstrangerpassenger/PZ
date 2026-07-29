from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
VALIDATOR = (
    REPO_ROOT
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "tools"
    / "build"
    / "validate_public_text_quality_acceptance_official_0004.py"
)


class PublicTextQualityAcceptanceCurrentRouteTest(unittest.TestCase):
    def test_required_gate_runs_standalone_subprocess(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(VALIDATOR),
                "--attempt-id",
                "attempt-0004-official",
                "--required-gate",
                "--no-write",
            ],
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["qualified_disposition"], "accepted")
        self.assertFalse(payload["publish_boundary_pass_claimed"])
        self.assertFalse(payload["package_or_release_ready_claimed"])


if __name__ == "__main__":
    unittest.main()
