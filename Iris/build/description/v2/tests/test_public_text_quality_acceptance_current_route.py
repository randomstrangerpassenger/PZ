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
PHASE7_TERMINAL_VALIDATOR = TOOLS_ROOT / (
    "validate_public_text_quality_acceptance_official_0005_phase7_terminal_validation.py"
)
PHASE7_HOST_INDEPENDENT_VALIDATOR = TOOLS_ROOT / (
    "validate_public_text_quality_acceptance_official_0005_phase7_host_independent_freeze.py"
)
PHASE7_REPLAY_SERIALIZATION_VALIDATOR = TOOLS_ROOT / (
    "validate_public_text_quality_acceptance_official_0005_phase7_replay_serialization.py"
)
PHASE7_EVALUATION_SUBJECT_TEXT_IDENTITY_VALIDATOR = TOOLS_ROOT / (
    "validate_public_text_quality_acceptance_official_0005_phase7_evaluation_subject_text_identity.py"
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

    def test_phase7_terminal_validation_complete_dag_regressions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(PHASE7_TERMINAL_VALIDATOR),
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
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertGreaterEqual(payload["case_count"], 20)
        self.assertEqual(
            payload["current_schema_dispatch"],
            "current_v2_terminal_validation_0002",
        )
        self.assertEqual(payload["historical_schema_dispatch"], "historical_v1")
        self.assertEqual(payload["protected_surface_mutation_count"], 0)
        self.assertEqual(payload["runtime_lua_package_mutation_count"], 0)

    def test_phase7_host_independent_freeze_inventory_regressions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(PHASE7_HOST_INDEPENDENT_VALIDATOR),
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
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["case_count"], 9)
        self.assertEqual(payload["passed_case_count"], 9)
        self.assertEqual(payload["claim_bearing_artifact_count"], 139)
        self.assertEqual(payload["terminal_dag_node_count"], 25)
        self.assertEqual(payload["terminal_dag_edge_count"], 38)
        self.assertEqual(payload["authority_effect"], "none")

    def test_phase7_replay_serialization_regressions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(PHASE7_REPLAY_SERIALIZATION_VALIDATOR),
                "--attempt-id",
                "attempt-0005-official",
                "--self-test",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["case_count"], 8)
        self.assertEqual(payload["passed_case_count"], 8)
        self.assertEqual(payload["canonical_tracked_inventory_count"], 139)
        self.assertEqual(payload["fake_zero_count_field_count"], 0)
        self.assertEqual(payload["authority_effect"], "none")

    def test_phase7_evaluation_subject_text_identity_regressions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(PHASE7_EVALUATION_SUBJECT_TEXT_IDENTITY_VALIDATOR),
                "--attempt-id",
                "attempt-0005-official",
                "--self-test",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["case_count"], 11)
        self.assertEqual(payload["passed_case_count"], 11)
        self.assertEqual(
            payload["evaluation_subject_sealed_sha256"],
            "ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437",
        )
        self.assertEqual(
            payload["evaluation_subject_head_blob_raw_sha256"],
            "522ab2773476eb97688c0f2adc14e52bbb58f30ce7cf48a7d7a2282e428964a5",
        )
        self.assertEqual(payload["authority_effect"], "none")

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
