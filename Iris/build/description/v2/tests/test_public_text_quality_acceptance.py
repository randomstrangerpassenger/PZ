from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
TOOLS = V2_ROOT / "tools" / "build"
RUNNER = TOOLS / "run_public_text_quality_acceptance.py"
VALIDATOR = TOOLS / "validate_public_text_quality_acceptance.py"
NATURALIZATION_HANDOFF = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "attempt-0011-handoff"
    / "phase8"
    / "publish_acceptance_handoff_manifest.json"
)
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as ptqa


class PublicTextQualityAcceptanceTest(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_disposition_state_machine_is_exactly_one_and_fail_closed(self) -> None:
        cases = (
            ((1, 0, 0, 0), "blocked"),
            ((0, 1, 0, 0), "blocked"),
            ((0, 0, 1, 0), "deferred_internal_debt"),
            ((0, 0, 0, 1), "deferred_internal_debt"),
            ((0, 0, 0, 0), "accepted"),
        )
        for counts, expected in cases:
            actual = ptqa.determine_qualified_disposition(
                technical_blocker_count=counts[0],
                effective_blocking_finding_count=counts[1],
                advisory_debt_count=counts[2],
                active_waiver_count=counts[3],
            )
            self.assertEqual(actual, expected)
            self.assertIn(actual, ptqa.QUALIFIED_DISPOSITIONS)

    def test_foundation_cli_build_and_no_write_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "foundation"
            foundation_id = "cli-foundation-v1"
            build = self.run_cli(
                str(RUNNER),
                "--foundation-id",
                foundation_id,
                "--mode",
                "foundation-build",
                "--foundation-root",
                str(root),
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            contract = root / ptqa.FOUNDATION_CONTRACT_NAME
            readiness = root / ptqa.READINESS_REPORT_NAME
            before = {
                "contract": contract.read_bytes(),
                "readiness": readiness.read_bytes(),
            }
            validate = self.run_cli(
                str(VALIDATOR),
                "--foundation-id",
                foundation_id,
                "--require-foundation-ready",
                "--no-write",
                "--foundation-root",
                str(root),
            )
            self.assertEqual(
                validate.returncode,
                0,
                validate.stdout + validate.stderr,
            )
            result = json.loads(validate.stdout)
            self.assertTrue(result["foundation_contract_ready_for_remediation"])
            self.assertEqual(result["authority_effect"], "none")
            self.assertEqual(result["official_disposition"], "not_issued")
            self.assertFalse(result["live_gate_adopted"])
            self.assertEqual(result["policy_closure_state"], "not_started")
            self.assertEqual(before["contract"], contract.read_bytes())
            self.assertEqual(before["readiness"], readiness.read_bytes())

    def test_foundation_cli_rejects_attempt_namespace_and_implicit_mode(self) -> None:
        rejected_attempt = self.run_cli(
            str(RUNNER),
            "--foundation-id",
            "bad",
            "--mode",
            "foundation-build",
            "--attempt-id",
            "forbidden",
        )
        self.assertNotEqual(rejected_attempt.returncode, 0)
        missing_mode = self.run_cli(
            str(RUNNER),
            "--foundation-id",
            "bad",
        )
        self.assertNotEqual(missing_mode.returncode, 0)

    def test_foundation_cli_rejects_noncanonical_repository_write_root(self) -> None:
        forbidden_root = V2_ROOT / "data" / "forbidden-foundation-root"
        result = self.run_cli(
            str(RUNNER),
            "--foundation-id",
            "bad-root",
            "--mode",
            "foundation-build",
            "--foundation-root",
            str(forbidden_root),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("exact tracked S1 foundation root", result.stderr)
        self.assertFalse(forbidden_root.exists())

    def test_tampered_contract_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "foundation"
            foundation_id = "tamper-foundation-v1"
            build = self.run_cli(
                str(RUNNER),
                "--foundation-id",
                foundation_id,
                "--mode",
                "foundation-build",
                "--foundation-root",
                str(root),
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            contract_path = root / ptqa.FOUNDATION_CONTRACT_NAME
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["authority_effect"] = "official"
            contract_path.write_text(
                json.dumps(contract, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n",
                encoding="utf-8",
            )
            validate = self.run_cli(
                str(VALIDATOR),
                "--foundation-id",
                foundation_id,
                "--require-foundation-ready",
                "--no-write",
                "--foundation-root",
                str(root),
            )
            self.assertEqual(validate.returncode, 2)
            self.assertIn("deterministic candidate-independent projection", validate.stderr)

    def test_write_once_conflict_returns_distinct_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "foundation"
            foundation_id = "write-once-foundation-v1"
            build = self.run_cli(
                str(RUNNER),
                "--foundation-id",
                foundation_id,
                "--mode",
                "foundation-build",
                "--foundation-root",
                str(root),
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            readiness = root / ptqa.READINESS_REPORT_NAME
            readiness.write_text("{}\n", encoding="utf-8")
            rerun = self.run_cli(
                str(RUNNER),
                "--foundation-id",
                foundation_id,
                "--mode",
                "foundation-build",
                "--foundation-root",
                str(root),
            )
            self.assertEqual(rerun.returncode, 3)
            self.assertIn("write-once conflict", rerun.stderr)

    def test_official_candidate_projection_excludes_emission_ineligible_roles(
        self,
    ) -> None:
        handoff = ptqa.validate_candidate_handoff(NATURALIZATION_HANDOFF)
        snapshot = ptqa.compute_candidate_metric_snapshot(handoff)
        metrics = {row["metric_id"]: row for row in snapshot["metric_rows"]}
        self.assertEqual(snapshot["required_body_plan_role_count"], 3131)
        self.assertEqual(
            metrics["unsatisfied_required_body_plan_role"]["numerator"], 0
        )
        self.assertEqual(metrics["equivalence_proof_failure"]["numerator"], 0)
        self.assertEqual(
            metrics["repeated_skeleton_concentration"]["numerator"], 450
        )
        self.assertEqual(
            metrics["repeated_skeleton_concentration"]["denominator"], 2084
        )

    def test_official_candidate_has_only_sealed_advisory_debt(self) -> None:
        handoff = ptqa.validate_candidate_handoff(NATURALIZATION_HANDOFF)
        snapshot = ptqa.compute_candidate_metric_snapshot(handoff)
        foundation = ptqa.load_json_strict(
            ptqa.DEFAULT_FOUNDATION_ROOT / ptqa.FOUNDATION_CONTRACT_NAME
        )
        results = ptqa._metric_threshold_results(
            snapshot,
            {"policy_projection": foundation["policy_candidate"]},
        )
        unsatisfied = [
            (row["metric_id"], row["disposition_class"])
            for row in results
            if not row["threshold_satisfied"]
        ]
        self.assertEqual(
            unsatisfied,
            [("repeated_skeleton_concentration", "advisory_debt")],
        )
        fixture = ptqa.load_json_strict(ptqa.FIXTURE_MANIFEST)
        self.assertTrue(
            all(
                "fixture_id" in row and "trace_id" not in row
                for row in fixture["fixtures"]
            )
        )


if __name__ == "__main__":
    unittest.main()
