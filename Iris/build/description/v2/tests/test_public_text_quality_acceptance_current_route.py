from __future__ import annotations

import json
import locale as locale_module
import platform
from pathlib import Path
import subprocess
import sys
import unittest

from Iris.validation.scenarios.scenario_report import (
    ExecutionResult,
    FrozenMap,
    ProbeResult,
    ScenarioContext,
    ScenarioReport,
)
from Iris.validation.scenarios.validate_scenario_report import (
    validate as validate_scenario_report,
)


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
PHASE7_LONG_PATH_WRITER_VALIDATOR = TOOLS_ROOT / (
    "validate_public_text_quality_acceptance_official_0005_phase7_long_path_writer.py"
)
PHASE7_FREEZE_INVENTORY_COMPLETENESS_VALIDATOR = TOOLS_ROOT / (
    "validate_public_text_quality_acceptance_official_0005_phase7_freeze_inventory_completeness.py"
)
PILOT_MAPPING = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "refactor"
    / "test_workflow_consolidation"
    / "pilot_contract_mapping.json"
)
PILOT_PROBE_IDS = (
    "historical_v1_and_current_v2_acceptance",
    "unknown_and_malformed_schema_rejection",
    "successor_transaction_hash_mismatch_rejection",
    "deterministic_document_replay",
)


class PublicTextQualityAcceptanceCurrentRouteTest(unittest.TestCase):
    _phase7_execution: ExecutionResult | None
    _phase7_report: ScenarioReport | None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._phase7_execution = None
        cls._phase7_report = None
        cls._phase7_self_test()

    @classmethod
    def tearDownClass(cls) -> None:
        del cls._phase7_execution
        del cls._phase7_report
        super().tearDownClass()

    @staticmethod
    def _git(*args: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), *args],
            text=True,
            encoding="utf-8",
        ).strip()

    @classmethod
    def _committed_identity(cls, path: Path) -> FrozenMap:
        relative = path.relative_to(REPO_ROOT).as_posix()
        return FrozenMap(
            {
                "canonical_path": relative,
                "git_blob_id": cls._git("rev-parse", f"HEAD:{relative}"),
            }
        )

    @staticmethod
    def _run_phase7_self_test() -> ExecutionResult:
        command = (
            sys.executable,
            "-B",
            str(PHASE7_V2_VALIDATOR),
            "--attempt-id",
            "attempt-0005-official",
            "--self-test",
            "--no-write",
        )
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise AssertionError(f"phase7 self-test emitted malformed JSON: {error}") from error
        if not isinstance(payload, dict):
            raise AssertionError("phase7 self-test payload must be an object")
        return ExecutionResult.from_payload(
            command_signature=tuple(str(value) for value in command),
            exit_code=result.returncode,
            stdout=result.stdout.encode("utf-8"),
            stderr=result.stderr.encode("utf-8"),
            payload=payload,
            producer_invocation_count=1,
            observation_coverage={"subprocess": "class_lifecycle_owner"},
        )

    @classmethod
    def _phase7_self_test(cls) -> ScenarioReport:
        if cls._phase7_report is None:
            execution = cls._run_phase7_self_test()
            cases = execution.parsed_payload["cases"]
            subject_commit = cls._git("rev-parse", "HEAD")
            subject_tree = cls._git("rev-parse", "HEAD^{tree}")
            checks = {
                "historical_v1_and_current_v2_acceptance": (
                    cases["historical_v1_and_current_v2_acceptance"]["historical_dispatch"]
                    == "historical_v1"
                    and cases["historical_v1_and_current_v2_acceptance"]["current_dispatch"]
                    == "current_v2_successor_0010"
                ),
                "unknown_and_malformed_schema_rejection": (
                    cases["unknown_and_malformed_schema_rejection"]["status"] == "PASS"
                ),
                "successor_transaction_hash_mismatch_rejection": (
                    cases["successor_transaction_hash_mismatch_rejection"]["status"]
                    == "PASS"
                    and cases["successor_transaction_hash_mismatch_rejection"][
                        "mismatch_field_count"
                    ]
                    == 3
                ),
                "deterministic_document_replay": (
                    cases["deterministic_document_replay"]["status"] == "PASS"
                ),
            }
            probes = tuple(
                ProbeResult(
                    probe_id=probe_id,
                    status="PASS" if checks[probe_id] else "FAIL",
                    reason=(
                        "phase7 contract checkpoint satisfied"
                        if checks[probe_id]
                        else "phase7 contract checkpoint mismatch"
                    ),
                    evidence_reference=f"/cases/{probe_id}",
                )
                for probe_id in PILOT_PROBE_IDS
            )
            context = ScenarioContext(
                schema_version="iris_test_workflow_scenario_context_v1",
                scenario_id="public-text-phase7-dispatch",
                validation_subject_commit=subject_commit,
                validation_subject_tree=subject_tree,
                route_class="all_explicit_path",
                contract_identity=cls._committed_identity(PILOT_MAPPING),
                input_identity=FrozenMap(
                    {
                        "attempt_id": "attempt-0005-official",
                        "mode": "self-test-no-write",
                        "validation_subject_tree": subject_tree,
                    }
                ),
                locale=locale_module.setlocale(locale_module.LC_ALL, None),
                environment_contract=FrozenMap(
                    {
                        "python_implementation": platform.python_implementation(),
                        "python_version": platform.python_version(),
                        "filesystem_encoding": sys.getfilesystemencoding(),
                    }
                ),
                workspace_mode="repository-read-only-producer",
                workspace_owner="PublicTextQualityAcceptanceCurrentRouteTest.class",
                producer_identity=cls._committed_identity(PHASE7_V2_VALIDATOR),
            )
            report = ScenarioReport(
                context=context,
                execution_result=execution,
                required_probe_inventory=PILOT_PROBE_IDS,
                probe_results=probes,
                execution_observations=FrozenMap({"run_id": "class-lifecycle"}),
            )
            report_payload = report.to_report()
            validate_scenario_report(
                report_payload,
                report_payload["deterministic_core"]["context"],
            )
            cls._phase7_execution = execution
            cls._phase7_report = report
        return cls._phase7_report

    @classmethod
    def _phase7_probe(cls, probe_id: str) -> ProbeResult:
        report = cls._phase7_self_test()
        return next(row for row in report.probe_results if row.probe_id == probe_id)

    def test_phase7_schema_dispatch_accepts_historical_v1_and_current_v2(self) -> None:
        self.assertEqual(
            self._phase7_probe("historical_v1_and_current_v2_acceptance").status,
            "PASS",
        )

    def test_phase7_schema_dispatch_rejects_unknown_and_malformed(self) -> None:
        self.assertEqual(
            self._phase7_probe("unknown_and_malformed_schema_rejection").status,
            "PASS",
        )

    def test_phase7_schema_dispatch_rejects_successor_transaction_hash_mismatch(self) -> None:
        self.assertEqual(
            self._phase7_probe("successor_transaction_hash_mismatch_rejection").status,
            "PASS",
        )

    def test_phase7_freeze_document_replay_is_deterministic(self) -> None:
        self.assertEqual(
            self._phase7_probe("deterministic_document_replay").status,
            "PASS",
        )

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

    def test_phase7_windows_long_path_safe_artifact_writer_regressions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(PHASE7_LONG_PATH_WRITER_VALIDATOR),
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
        self.assertEqual(payload["case_count"], 9)
        self.assertEqual(payload["passed_case_count"], 9)
        self.assertEqual(payload["partial_target_count"], 0)
        self.assertEqual(payload["temporary_residue_count"], 0)
        self.assertEqual(payload["authority_effect"], "none")

    def test_phase7_freeze_inventory_completeness_regressions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(PHASE7_FREEZE_INVENTORY_COMPLETENESS_VALIDATOR),
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
        self.assertGreaterEqual(payload["declared_surface_count"], 22)
        self.assertGreater(payload["dependency_edge_count"], 0)
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
