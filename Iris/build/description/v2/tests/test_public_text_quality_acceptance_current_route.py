from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[5]
VALIDATOR = (
    REPO_ROOT
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "tools"
    / "build"
    / "validate_public_text_quality_acceptance_official_0005.py"
)
TOOLS_ROOT = VALIDATOR.parent
PHASE7_V2_VALIDATOR = TOOLS_ROOT / (
    "validate_public_text_quality_acceptance_official_0005_phase7_v2.py"
)


class PublicTextQualityAcceptanceCurrentRouteTest(unittest.TestCase):
    @staticmethod
    def _phase7_self_test() -> dict[str, object]:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(PHASE7_V2_VALIDATOR),
                "--attempt-id",
                "attempt-0005-official",
                "--self-test",
                "--no-write",
            ],
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        return json.loads(result.stdout)

    def test_phase7_schema_dispatch_accepts_historical_v1_and_current_v2(self) -> None:
        result = self._phase7_self_test()
        case = result["cases"]["historical_v1_and_current_v2_acceptance"]
        self.assertEqual(case["historical_dispatch"], "historical_v1")
        self.assertEqual(case["current_dispatch"], "current_v2_successor_0010")

    def test_phase7_schema_dispatch_rejects_unknown_and_malformed(self) -> None:
        case = self._phase7_self_test()["cases"][
            "unknown_and_malformed_schema_rejection"
        ]
        self.assertEqual(case["status"], "PASS")

    def test_phase7_schema_dispatch_rejects_successor_transaction_hash_mismatch(self) -> None:
        case = self._phase7_self_test()["cases"][
            "successor_transaction_hash_mismatch_rejection"
        ]
        self.assertEqual(case["status"], "PASS")
        self.assertEqual(case["mismatch_field_count"], 3)

    def test_phase7_freeze_document_replay_is_deterministic(self) -> None:
        case = self._phase7_self_test()["cases"]["deterministic_document_replay"]
        self.assertEqual(case["status"], "PASS")

    def test_required_gate_runs_standalone_subprocess(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(VALIDATOR),
                "--attempt-id",
                "attempt-0005-official",
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
