from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest import mock
import uuid


ROUND_ID = "dvf_3_3_registry_authority_canonical_closure"
REPO_ROOT = Path(__file__).resolve().parents[5]
V2_ROOT = REPO_ROOT / "Iris" / "build" / "description" / "v2"
TOOLS_ROOT = V2_ROOT / "tools" / "build"
COMMON = TOOLS_ROOT / f"{ROUND_ID}.py"
RUNNER = TOOLS_ROOT / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS_ROOT / f"validate_{ROUND_ID}.py"
FOCUSED_TEST = Path(__file__).resolve()
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
ATTEMPTS_ROOT = EVIDENCE_ROOT / "attempts"
BOOTSTRAP_MANIFEST = EVIDENCE_ROOT / "phase0" / "bootstrap_scaffold_hash_manifest.json"
COMPOSE_TOOL = TOOLS_ROOT / "compose_layer3_text.py"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_script(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(path), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_common_module():
    spec = importlib.util.spec_from_file_location(
        "registry_authority_common_for_test", COMMON
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {COMMON}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegistryAuthorityBootstrapScaffoldTest(unittest.TestCase):
    def temporary_evidence_root(self) -> Path:
        return ATTEMPTS_ROOT / f"attempt-9999-{uuid.uuid4().hex[:12]}"

    def test_bootstrap_manifest_matches_closed_scaffold_path_set(self) -> None:
        payload = json.loads(BOOTSTRAP_MANIFEST.read_text(encoding="utf-8"))
        expected_paths = [COMMON, RUNNER, VALIDATOR, FOCUSED_TEST]
        rows = payload["scaffold_paths"]
        self.assertEqual(
            [row["path"] for row in rows],
            [path.relative_to(REPO_ROOT).as_posix() for path in expected_paths],
        )
        self.assertTrue(all(row["exists"] for row in rows))
        self.assertTrue(all(row["byte_length"] > 0 for row in rows))
        self.assertTrue(all(len(row["sha256"]) == 64 for row in rows))
        self.assertTrue(
            any(
                row["sha256"] != sha256_file(REPO_ROOT / row["path"])
                for row in rows
            ),
            "Entry scaffold manifest must stay frozen after implementation changes",
        )
        self.assertEqual(
            payload["capabilities"]["implemented_success_modes"],
            ["preflight", "materialize-preimplementation-reviews"],
        )
        self.assertEqual(
            payload["capabilities"]["implemented_success_validations"],
            [
                "require-preflight",
                "require-preimplementation-reviews",
                "require-execution-entry",
            ],
        )
        self.assertTrue(payload["capabilities"]["review_materialization_present"])
        self.assertTrue(payload["capabilities"]["execution_entry_validation_present"])
        self.assertFalse(payload["capabilities"]["aggregate_mode_present"])
        self.assertFalse(payload["capabilities"]["wp_implementation_present"])
        self.assertFalse(payload["capabilities"]["gate_adoption_present"])
        self.assertFalse(payload["capabilities"]["finalization_producer_present"])
        self.assertFalse(payload["capabilities"]["owner_or_reviewer_verdict_authoring_present"])
        self.assertFalse(payload["capabilities"]["current_or_protected_writer_present"])
        self.assertTrue(payload["capabilities"]["attempt_evidence_write_once_present"])
        self.assertTrue(payload["capabilities"]["failure_history_write_once_present"])

    def test_scaffold_sources_parse_and_common_uses_stdlib_only(self) -> None:
        for path in (COMMON, RUNNER, VALIDATOR, FOCUSED_TEST):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        common_tree = ast.parse(COMMON.read_text(encoding="utf-8"))
        imported_roots = set()
        for node in ast.walk(common_tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertLessEqual(
            imported_roots,
            {
                "__future__",
                "ast",
                "datetime",
                "fnmatch",
                "hashlib",
                "json",
                "os",
                "pathlib",
                "queue",
                "re",
                "secrets",
                "shutil",
                "subprocess",
                "sys",
                "threading",
                "time",
                "typing",
                "zipfile",
            },
        )

    def test_aggregate_all_mode_is_rejected_before_writes(self) -> None:
        root = self.temporary_evidence_root()
        self.assertFalse(root.exists())
        result = run_script(
            RUNNER,
            "--mode",
            "all",
            "--attempt-id",
            root.name,
            "--evidence-root",
            str(root),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(root.exists())

    def test_non_entry_modes_are_inert_and_write_nothing(self) -> None:
        for mode in ("wp1", "gate-candidate", "adopt-gate", "finalize"):
            with self.subTest(mode=mode):
                root = self.temporary_evidence_root()
                result = run_script(
                    RUNNER,
                    "--mode",
                    mode,
                    "--attempt-id",
                    root.name,
                    "--evidence-root",
                    str(root),
                )
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                payload = json.loads(result.stderr.strip())
                self.assertEqual(payload["status"], "not_implemented")
                self.assertFalse(payload["evidence_written"])
                self.assertFalse(payload["wp_execution_allowed"])
                self.assertFalse(payload["gate_adoption_allowed"])
                self.assertFalse(payload["finalization_allowed"])
                self.assertFalse(root.exists())

    def test_implementation_validator_fails_closed_without_evidence(self) -> None:
        root = self.temporary_evidence_root()
        result = run_script(
            VALIDATOR,
            "--require-implementation",
            "--attempt-id",
            root.name,
            "--evidence-root",
            str(root),
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        payload = json.loads(result.stdout.strip())
        self.assertEqual(payload["status"], "FAIL")
        self.assertGreater(payload["blocker_count"], 0)
        self.assertFalse(root.exists())

    def test_preflight_without_external_authority_fails_closed(self) -> None:
        root = self.temporary_evidence_root()
        try:
            result = run_script(
                RUNNER,
                "--mode",
                "preflight",
                "--attempt-id",
                root.name,
                "--evidence-root",
                str(root),
            )
            self.assertNotEqual(result.returncode, 0)
            report_path = root / "phase0" / "preflight_report.json"
            review_path = root / "phase3" / "preimplementation_review_input_manifest.json"
            self.assertTrue(report_path.is_file())
            self.assertTrue(review_path.is_file())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            review = json.loads(review_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "FAIL")
            self.assertGreater(report["blocker_count"], 0)
            self.assertFalse(report["wp_execution_allowed"])
            self.assertFalse(report["canonical_closure_claimed"])
            self.assertFalse(report["owner_seal_claimed"])
            self.assertFalse(report["independent_review_claimed"])
            self.assertEqual(review["status"], "BLOCKED")
            self.assertFalse(review["tool_may_author_review_verdict"])
            entry = run_script(
                VALIDATOR,
                "--require-execution-entry",
                "--attempt-id",
                root.name,
                "--evidence-root",
                str(root),
                "--no-write",
            )
            self.assertNotEqual(entry.returncode, 0)
            entry_payload = json.loads(entry.stdout.strip())
            self.assertNotIn(
                "entry_lua_environment_drift", entry_payload.get("blockers", [])
            )
        finally:
            if root.exists():
                resolved = root.resolve()
                resolved.relative_to(ATTEMPTS_ROOT.resolve())
                shutil.rmtree(resolved)

    def test_validator_rejects_missing_preflight_evidence(self) -> None:
        root = self.temporary_evidence_root()
        result = run_script(
            VALIDATOR,
            "--require-preflight",
            "--attempt-id",
            root.name,
            "--evidence-root",
            str(root),
            "--no-write",
        )
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout.strip())
        self.assertEqual(payload["status"], "FAIL")
        self.assertGreater(payload["blocker_count"], 0)
        self.assertFalse(payload["canonical_closure_claimed"])
        self.assertFalse(payload["owner_seal_claimed"])
        self.assertFalse(root.exists())

    def test_same_attempt_cannot_overwrite_failed_preflight_evidence(self) -> None:
        root = self.temporary_evidence_root()
        args = (
            "--mode",
            "preflight",
            "--attempt-id",
            root.name,
            "--evidence-root",
            str(root),
        )
        try:
            first = run_script(RUNNER, *args)
            self.assertNotEqual(first.returncode, 0)
            report = root / "phase0" / "preflight_report.json"
            self.assertTrue(report.is_file())
            before_hash = sha256_file(report)
            second = run_script(RUNNER, *args)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(sha256_file(report), before_hash)
            self.assertIn("write-once", second.stderr)
        finally:
            if root.exists():
                resolved = root.resolve()
                resolved.relative_to(ATTEMPTS_ROOT.resolve())
                shutil.rmtree(resolved)

    def test_pre_entry_exception_record_is_write_once(self) -> None:
        root = self.temporary_evidence_root()
        root.mkdir(parents=True)
        (root / "partial.marker").write_text("partial\n", encoding="utf-8")
        args = (
            "--mode",
            "preflight",
            "--attempt-id",
            root.name,
            "--evidence-root",
            str(root),
        )
        try:
            first = run_script(RUNNER, *args)
            self.assertNotEqual(first.returncode, 0)
            failure = root / "attempt_failures" / "preflight.json"
            self.assertTrue(failure.is_file())
            before_hash = sha256_file(failure)
            second = run_script(RUNNER, *args)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(sha256_file(failure), before_hash)
            payload = json.loads(second.stderr.strip())
            self.assertEqual(
                payload["failure_record"]["reason"],
                "failure_record_already_preserved",
            )
        finally:
            if root.exists():
                resolved = root.resolve()
                resolved.relative_to(ATTEMPTS_ROOT.resolve())
                shutil.rmtree(resolved)

    def test_preserved_owner_input_tree_hash_is_revalidated(self) -> None:
        common = load_common_module()
        predecessor_id = "attempt-0006-entry"
        archive = (
            EVIDENCE_ROOT / "superseded_owner_inputs" / predecessor_id
        ).resolve()
        self.assertTrue(archive.is_dir())
        row = {
            "preserved_owner_inputs_path": archive.relative_to(REPO_ROOT).as_posix(),
            "preserved_owner_inputs_tree_sha256": common.directory_tree_hash(archive),
        }
        preserved, blockers = common.validate_preserved_owner_input_archive(
            row,
            predecessor_id=predecessor_id,
            attempt_archive=EVIDENCE_ROOT / "attempts" / predecessor_id,
        )
        self.assertEqual(preserved, archive)
        self.assertEqual(blockers, [])
        row["preserved_owner_inputs_tree_sha256"] = "0" * 64
        preserved, blockers = common.validate_preserved_owner_input_archive(
            row,
            predecessor_id=predecessor_id,
            attempt_archive=EVIDENCE_ROOT / "attempts" / predecessor_id,
        )
        self.assertIsNone(preserved)
        self.assertIn(
            "attempt_registration_predecessor_owner_inputs_hash_mismatch:attempt-0006-entry",
            blockers,
        )

    def test_directory_tree_hash_includes_extended_length_file(self) -> None:
        common = load_common_module()
        root = self.temporary_evidence_root()
        relative = (
            Path("extended-" + "d" * 80)
            / ("review-" + "f" * 120 + ".md")
        )
        target = common.filesystem_path(root / relative)
        try:
            target.parent.mkdir(parents=True)
            target.write_bytes(b"long-path-review-evidence\n")
            self.assertEqual(
                common.directory_tree_hash(root),
                common.canonical_hash(
                    [
                        {
                            "path": relative.as_posix(),
                            "sha256": hashlib.sha256(
                                b"long-path-review-evidence\n"
                            ).hexdigest(),
                        }
                    ]
                ),
            )
        finally:
            extended_root = common.filesystem_path(root)
            if extended_root.is_dir():
                shutil.rmtree(extended_root)


class RegistryAuthorityCanonicalClosureImplementationTest(unittest.TestCase):
    def temporary_evidence_root(self) -> Path:
        return ATTEMPTS_ROOT / f"attempt-9999-{uuid.uuid4().hex[:12]}"

    def test_registry_authority_required_gate_contract(self) -> None:
        common = load_common_module()
        root = self.temporary_evidence_root()
        try:
            reports = common.build_wp7_reports(
                root,
                [{"schema_version": "fixture-prerequisite-v1", "status": "PASS"}],
            )
            self.assertEqual([row["status"] for row in reports], ["PASS", "PASS"])
            contract = json.loads(
                (
                    root
                    / "phase4"
                    / "wp7_registry_authority_required_gate_contract_report.json"
                ).read_text(encoding="utf-8")
            )
            self.assertFalse(contract["required_gate_adopted"])
            self.assertFalse(contract["canonical_closure_claimed"])
            self.assertFalse(contract["machine_pass_claimed"])
            self.assertTrue(contract["candidate_specific_authorization_required"])
            self.assertFalse(
                contract["canonical_complete_without_required_gate_adoption_allowed"]
            )
        finally:
            if root.exists():
                resolved = root.resolve()
                resolved.relative_to(ATTEMPTS_ROOT.resolve())
                shutil.rmtree(resolved)

    def test_successful_implementation_attempt_cannot_gain_late_failure_record(self) -> None:
        common = load_common_module()
        root = self.temporary_evidence_root()
        terminal = root / "phase4" / "implementation_scope_report.json"
        try:
            terminal.parent.mkdir(parents=True)
            terminal.write_text('{"status":"PASS"}\n', encoding="utf-8")
            result = common.record_attempt_failure_once(
                root,
                attempt_id=root.name,
                mode="implementation",
                error_type="FileExistsError",
                error="write-once replay",
            )
            self.assertFalse(result["written"])
            self.assertEqual(result["reason"], "terminal_claim_output_already_exists")
            self.assertFalse((root / "attempt_failures" / "implementation.json").exists())
        finally:
            if root.exists():
                resolved = root.resolve()
                resolved.relative_to(ATTEMPTS_ROOT.resolve())
                shutil.rmtree(resolved)

    def test_practical_failure_record_terminates_all_same_attempt_writes(self) -> None:
        common = load_common_module()
        root = ATTEMPTS_ROOT / (
            f"attempt-9999-{uuid.uuid4().hex[:8]}-practical"
        )
        failure = root / "attempt_failures" / "practical-gate-candidate.json"
        try:
            common.write_json_once(
                failure,
                {
                    "attempt_id": root.name,
                    "mode": "practical-gate-candidate",
                    "status": "FAIL",
                },
            )
            before = sha256_file(failure)
            with self.assertRaisesRegex(
                RuntimeError,
                "practical attempt already terminated",
            ):
                common.require_practical_attempt_open(root)
            self.assertEqual(
                common.practical_attempt_failure_blockers(root),
                [
                    "practical_attempt_terminal_failure_present:"
                    "practical-gate-candidate.json"
                ],
            )
            later = common.record_attempt_failure_once(
                root,
                attempt_id=root.name,
                mode="practical-adopt-gate",
                error_type="RuntimeError",
                error="same-attempt continuation refused",
            )
            self.assertFalse(later["written"])
            self.assertEqual(
                later["reason"],
                "attempt_terminal_failure_already_preserved",
            )
            self.assertEqual(sha256_file(failure), before)
            self.assertFalse(
                (
                    root
                    / "attempt_failures"
                    / "practical-adopt-gate.json"
                ).exists()
            )
            snapshot = common.validate_practical_preflight_snapshot(
                root,
                attempt_id=root.name,
            )
            self.assertIn(
                "practical_attempt_terminal_failure_present:"
                "practical-gate-candidate.json",
                snapshot["blockers"],
            )
        finally:
            extended_root = common.filesystem_path(root)
            if extended_root.is_dir():
                shutil.rmtree(extended_root)

    def test_write_json_once_supports_long_nonce_consumption_path(self) -> None:
        common = load_common_module()
        root = ATTEMPTS_ROOT / (
            f"attempt-9999-{uuid.uuid4().hex[:8]}-practical"
        )
        nonce_path = (
            root
            / "phase4"
            / "gate_adoption"
            / "nonce_consumption"
            / ("f" * 64 + ".json")
        )
        try:
            common.write_json_once(nonce_path, {"status": "CONSUMED"})
            self.assertEqual(
                common.read_json_object(nonce_path),
                {"status": "CONSUMED"},
            )
            normal_children = [
                nonce_path.parent / child.name
                for child in common.filesystem_path(nonce_path.parent).glob(
                    "*.json"
                )
            ]
            self.assertEqual(normal_children, [nonce_path])
            self.assertEqual(
                common.repo_relative(normal_children[0]),
                nonce_path.relative_to(REPO_ROOT).as_posix(),
            )
            with self.assertRaises(FileExistsError):
                common.write_json_once(nonce_path, {"status": "REUSED"})
        finally:
            extended_root = common.filesystem_path(root)
            if extended_root.is_dir():
                shutil.rmtree(extended_root)

    def test_partial_terminal_write_records_one_immutable_implementation_failure(self) -> None:
        common = load_common_module()
        root = self.temporary_evidence_root()
        phase4 = root / "phase4"
        completion = phase4 / "wp_completion_summary.md"
        try:
            completion.parent.mkdir(parents=True)
            completion.write_text("preexisting fault fixture\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                common.write_implementation_terminal_outputs(
                    phase4,
                    scope={"status": "PASS"},
                    no_mutation={"status": "PASS"},
                    tooling={"status": "PASS"},
                    focused={"status": "PENDING_PLAN_STEP_6"},
                    completion_text="new completion\n",
                )
            self.assertFalse((phase4 / "implementation_scope_report.json").exists())
            first = common.record_attempt_failure_once(
                root,
                attempt_id=root.name,
                mode="implementation",
                error_type="FileExistsError",
                error="penultimate write fault",
            )
            self.assertTrue(first["written"])
            failure = root / "attempt_failures" / "implementation.json"
            before = sha256_file(failure)
            second = common.record_attempt_failure_once(
                root,
                attempt_id=root.name,
                mode="implementation",
                error_type="FileExistsError",
                error="same attempt replay",
            )
            self.assertFalse(second["written"])
            self.assertEqual(second["reason"], "failure_record_already_preserved")
            self.assertEqual(sha256_file(failure), before)
        finally:
            if root.exists():
                resolved = root.resolve()
                resolved.relative_to(ATTEMPTS_ROOT.resolve())
                shutil.rmtree(resolved)

    def test_command_order_failure_anchor_rejects_same_attempt_rewrite(self) -> None:
        common = load_common_module()
        predecessor_id = "attempt-0020-entry"
        attempt_archive = ATTEMPTS_ROOT / predecessor_id
        owner_archive = (
            EVIDENCE_ROOT / "superseded_owner_inputs" / predecessor_id
        )
        anchor = common.TRUSTED_EXECUTION_SEQUENCE_FAILURE_ANCHORS[predecessor_id]
        record = {
            "schema_version": (
                f"{common.SCHEMA_PREFIX}-execution-sequence-failure-v1"
            ),
            "cycle_id": ROUND_ID,
            "attempt_id": predecessor_id,
            "status": "FAIL",
            "failure_class": "command_order_violation",
            "missing_required_predecessor_command": common.FOCUSED_TEST_COMMAND,
            "observed_completed_command": "implementation",
            "focused_test_executed_before_implementation": False,
            "same_attempt_claim_continuation_allowed": False,
            "new_attempt_required": True,
            "failure_history_preserved": True,
            "claim_output_overwritten": False,
            "wp_execution_allowed": False,
            "gate_adoption_allowed": False,
            "live_gate_adopted": False,
            "protected_mutation_count": 0,
            "execution_base_commit": anchor["execution_base_commit"],
            "attempt_evidence_tree_sha256": anchor["attempt_evidence_tree_sha256"],
            "preflight_report_path": common.repo_relative(
                attempt_archive / "phase0" / "preflight_report.json"
            ),
            "preflight_report_sha256": anchor["preflight_report_sha256"],
            "materialization_report_path": common.repo_relative(
                attempt_archive
                / "phase3"
                / "preimplementation_review_materialization_report.json"
            ),
            "materialization_report_sha256": anchor[
                "materialization_report_sha256"
            ],
            "blocker_zero_record_path": common.repo_relative(
                attempt_archive / "phase3" / "blocker_zero_record.json"
            ),
            "blocker_zero_record_sha256": anchor["blocker_zero_record_sha256"],
            "focused_test_result_report_path": common.repo_relative(
                attempt_archive / "phase4" / "focused_test_result_report.json"
            ),
            "focused_test_result_report_sha256": anchor[
                "focused_test_result_report_sha256"
            ],
            "focused_test_preimplementation_receipt_path": common.repo_relative(
                attempt_archive / "phase4" / common.FOCUSED_TEST_RECEIPT_NAME
            ),
            "focused_test_preimplementation_receipt_present": False,
            "implementation_scope_report_path": common.repo_relative(
                attempt_archive / "phase4" / "implementation_scope_report.json"
            ),
            "implementation_scope_report_sha256": anchor[
                "implementation_scope_report_sha256"
            ],
            "focused_test_base_file_sha256": anchor["focused_test_base_file_sha256"],
            "implementation_common_base_file_sha256": anchor[
                "implementation_common_base_file_sha256"
            ],
            "implementation_runner_base_file_sha256": anchor[
                "implementation_runner_base_file_sha256"
            ],
            "owner_identity": "workspace_owner",
            "recorder_identity": "/root",
            "recorded_at": "2026-07-23T12:00:00+00:00",
            "implementation_command_receipt": {
                "session_id": 54414,
                "exit_code": 0,
                "first_phase4_evidence_at_utc": "2026-07-23T11:55:18+00:00",
                "terminal_at_utc": "2026-07-23T11:57:17+00:00",
                "terminal_result": {
                    "status": "PASS",
                    "attempt_id": predecessor_id,
                    "blocker_count": 0,
                },
            },
        }

        def fake_sha256(path: Path) -> str | None:
            return {
                "execution_sequence_failure_record.json": anchor[
                    "sequence_failure_record_sha256"
                ],
                "preflight_report.json": anchor["preflight_report_sha256"],
                "preimplementation_review_materialization_report.json": anchor[
                    "materialization_report_sha256"
                ],
                "blocker_zero_record.json": anchor["blocker_zero_record_sha256"],
                "focused_test_result_report.json": anchor[
                    "focused_test_result_report_sha256"
                ],
                "implementation_scope_report.json": anchor[
                    "implementation_scope_report_sha256"
                ],
            }.get(path.name)

        def fake_read_json(path: Path) -> dict[str, object]:
            return {
                "preflight_report.json": {"status": "PASS"},
                "preimplementation_review_materialization_report.json": {
                    "status": "PASS"
                },
                "blocker_zero_record.json": {
                    "status": "PASS",
                    "critical_count": 0,
                    "important_count": 0,
                },
                "focused_test_result_report.json": {
                    "status": "PENDING_PLAN_STEP_6",
                    "test_executed_inside_implementation_mode": False,
                },
                "implementation_scope_report.json": {
                    "schema_version": (
                        f"{common.SCHEMA_PREFIX}-implementation-scope-v1"
                    ),
                    "status": "PASS",
                    "attempt_id": predecessor_id,
                },
            }.get(path.name, {})

        with (
            mock.patch.object(common, "sha256_file", side_effect=fake_sha256),
            mock.patch.object(
                common,
                "directory_tree_hash",
                side_effect=lambda path: (
                    anchor["attempt_evidence_tree_sha256"]
                    if path == attempt_archive
                    else anchor["owner_inputs_tree_sha256"]
                ),
            ),
            mock.patch.object(
                common,
                "git_blob_sha256",
                side_effect=[
                    anchor["focused_test_base_file_sha256"],
                    anchor["implementation_common_base_file_sha256"],
                    anchor["implementation_runner_base_file_sha256"],
                ]
                * 2,
            ),
            mock.patch.object(common, "read_json_object", side_effect=fake_read_json),
            mock.patch.object(common, "path_is_file", return_value=False),
        ):
            self.assertTrue(
                common.valid_execution_sequence_failure_record(
                    record,
                    predecessor_id=predecessor_id,
                    attempt_archive=attempt_archive,
                    owner_archive=owner_archive,
                )
            )
            forged = dict(record)
            forged["focused_test_executed_before_implementation"] = True
            self.assertFalse(
                common.valid_execution_sequence_failure_record(
                    forged,
                    predecessor_id=predecessor_id,
                    attempt_archive=attempt_archive,
                    owner_archive=owner_archive,
                )
            )

    def test_focused_test_inventory_is_exact_and_unique(self) -> None:
        common = load_common_module()
        inventory = common.focused_test_inventory()
        self.assertEqual(inventory, sorted(set(inventory)))
        self.assertIn(
            (
                "test_dvf_3_3_registry_authority_canonical_closure."
                "RegistryAuthorityCanonicalClosureImplementationTest."
                "test_command_order_failure_anchor_rejects_same_attempt_rewrite"
            ),
            inventory,
        )
        self.assertIn(
            (
                "test_dvf_3_3_registry_authority_canonical_closure."
                "RegistryAuthorityCanonicalClosureImplementationTest."
                "test_focused_test_inventory_is_exact_and_unique"
            ),
            inventory,
        )

    def test_wp6_negative_fixtures_detect_path_hash_and_package_reentry(self) -> None:
        common = load_common_module()
        root = self.temporary_evidence_root()
        try:
            report = common.build_wp6_negative_fixture_report(root)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                set(report["expected_violation_kinds"]),
                set(report["observed_violation_kinds"]),
            )
            self.assertEqual(
                set(report["negative_dataflow_cases"]),
                {
                    "python_split_concatenation_and_loader_alias",
                    "lua_concatenation_and_loader_alias",
                    "powershell_join_path_and_copy_alias",
                    "python_unresolved_taint_loader_fail_closed",
                    "lua_unresolved_taint_loader_fail_closed",
                    "powershell_unresolved_taint_copy_fail_closed",
                    "powershell_named_join_path_unresolved_taint_fail_closed",
                    "python_repo_anchor_required_current_exact_edge",
                    "python_contained_generated_fixture_classified_non_live",
                    "python_contained_v2_tmp_tests_classified_non_live",
                    "python_contained_attribute_assignment_classified_non_live",
                    "python_contained_temporary_directory_owner_classified_non_live",
                    "python_contained_mkdtemp_classified_non_live",
                    "python_contained_helper_return_classified_non_live",
                    "python_local_tempfile_factory_name_collision_fail_closed",
                    "python_method_tempfile_factory_name_collision_fail_closed",
                    "python_direct_import_tempfile_factory_name_collision_fail_closed",
                    "python_module_import_tempfile_factory_name_collision_fail_closed",
                },
            )
            self.assertEqual(
                set(report["negative_consumer_roots"]),
                {"current_route", "runtime_shared", "required_tests"},
            )
            self.assertTrue(report["same_raw_discovery_path_as_live_graph"])
            self.assertEqual(
                set(report["required_structural_discovery_kinds"]),
                set(report["observed_discovery_kinds"]),
            )
            self.assertEqual(
                set(report["expected_unresolved_taint_sources"]),
                set(report["observed_unresolved_taint_sources"]),
            )
            self.assertEqual(len(report["expected_unresolved_taint_sources"]), 4)
            self.assertEqual(report["unexpected_discovery_blockers"], [])
            self.assertTrue(report["fixture_executable_denominator"]["complete"])
            self.assertTrue(report["repo_anchor_current_edge_detected"])
            self.assertTrue(report["contained_python_fixture_classified"])
            self.assertGreaterEqual(
                report["contained_python_fixture_reference_count"], 6
            )
            self.assertTrue(report["tempfile_name_collisions_fail_closed"])
            self.assertTrue(report["powershell_named_join_path_fail_closed"])
            self.assertEqual(
                len(report["tempfile_name_collision_unresolved_blockers"]), 4
            )
            self.assertEqual(
                report["tempfile_name_collision_contained_references"], []
            )
            self.assertEqual(report["real_current_or_package_mutation_count"], 0)
        finally:
            if root.exists():
                resolved = root.resolve()
                resolved.relative_to(ATTEMPTS_ROOT.resolve())
                shutil.rmtree(resolved)

    def test_wp6_live_denominator_closes_dependencies_and_vcs_inventory(self) -> None:
        common = load_common_module()
        scan_files, blockers, denominator = (
            common.registry_reference_scan_files()
        )
        self.assertEqual(blockers, [])
        self.assertTrue(denominator["complete"])
        self.assertTrue(
            denominator[
                "vcs_tracked_untracked_ignored_dirty_enumeration_succeeded"
            ]
        )
        self.assertTrue(
            denominator["vcs_executable_inventory_partition_complete"]
        )
        self.assertTrue(denominator["tracked_inventory_partition_complete"])
        self.assertTrue(denominator["required_executable_inclusion_complete"])
        self.assertTrue(denominator["live_seed_inclusion_complete"])
        self.assertTrue(denominator["live_seed_tracked_complete"])
        self.assertFalse(
            denominator["non_live_inventory_scanned_as_current_readpoints"]
        )
        vcs_count = denominator["vcs_executable_inventory_count"]
        self.assertEqual(
            vcs_count,
            denominator["vcs_live_admitted_count"]
            + denominator["vcs_non_live_classified_count"],
        )
        rows = denominator["vcs_executable_classification_rows"]
        self.assertEqual(len(rows), vcs_count)
        self.assertEqual(
            len({row["path"] for row in rows}),
            vcs_count,
        )
        admitted_paths = {
            common.repo_relative(path)
            for path in scan_files
        }
        live_rows = {
            row["path"]
            for row in rows
            if row["admission"] == "live_current_readpoint"
        }
        non_live_rows = {
            row["path"]
            for row in rows
            if row["admission"] == "classified_non_live"
        }
        self.assertEqual(live_rows, admitted_paths)
        self.assertTrue(live_rows.isdisjoint(non_live_rows))
        self.assertEqual(len(live_rows | non_live_rows), vcs_count)
        runtime_dependency = (
            "Iris/build/description/v2/tools/build/"
            "runtime_payload_state_integrity.py"
        )
        self.assertIn(runtime_dependency, live_rows)
        self.assertTrue(
            any(
                edge["source"].endswith(
                    "/tests/test_runtime_payload_state_integrity.py"
                )
                and edge["dependency"] == runtime_dependency
                for edge in denominator["execution_dependency_edges"]
            )
        )
        gate_dependency_prefix = (
            "Iris/build/description/v2/tools/build/"
        )
        gate_dependencies = {
            gate_dependency_prefix
            + "run_dvf_3_3_core_registry_boundary_required_gate_adoption.py",
            gate_dependency_prefix
            + "validate_dvf_3_3_core_registry_boundary_required_gate_adoption.py",
        }
        self.assertTrue(gate_dependencies.issubset(live_rows))
        gate_test_suffix = (
            "/tests/"
            "test_dvf_3_3_core_registry_boundary_required_gate_adoption.py"
        )
        gate_edges = {
            edge["dependency"]
            for edge in denominator["execution_dependency_edges"]
            if edge["source"].endswith(gate_test_suffix)
        }
        self.assertTrue(gate_dependencies.issubset(gate_edges))
        self.assertTrue(
            all(
                row["admission"] == "classified_non_live"
                for row in rows
                if row["classification"]
                == "historical_or_staging_evidence"
            )
        )

    def test_wp6_wp2_ledger_binding_rejects_truncated_jsonl(self) -> None:
        common = load_common_module()
        root = self.temporary_evidence_root()
        phase4 = root / "phase4"
        phase4.mkdir(parents=True)
        ledger_path = (
            phase4 / "wp2_artifact_role_classification_ledger.jsonl"
        )
        census_path = (
            phase4 / "wp2_current_checkout_artifact_surface_census.json"
        )
        row = {
            "path": (
                "Iris/build/description/v2/output/dvf_3_3_rendered.json"
            ),
            "kind": "file",
            "role": "current",
            "current_reentry_allowed": True,
        }
        try:
            ledger_path.write_text(
                json.dumps(row, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            census_path.write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "normalized_ledger_sha256": common.canonical_hash(
                            [row]
                        ),
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            rows, binding = common.wp2_role_ledger_binding(root)
            self.assertEqual(rows, [row])
            self.assertEqual(binding["status"], "PASS")
            self.assertTrue(binding["exact_hash_match"])

            ledger_path.write_text(
                ledger_path.read_text(encoding="utf-8") + "{truncated\n",
                encoding="utf-8",
            )
            _, rejected = common.wp2_role_ledger_binding(root)
            self.assertEqual(rejected["status"], "FAIL")
            self.assertIn(
                "wp2_role_ledger_json_invalid:2",
                rejected["blockers"],
            )
            self.assertIn(
                "wp2_role_ledger_line_parse_count_mismatch",
                rejected["blockers"],
            )
        finally:
            if root.exists():
                resolved = root.resolve()
                resolved.relative_to(ATTEMPTS_ROOT.resolve())
                shutil.rmtree(resolved)

    def test_wp6_lua_module_table_requires_all_distinct_literals(self) -> None:
        common = load_common_module()
        source = (
            V2_ROOT
            / ".tmp_tests"
            / "registry_module_table_loader.lua"
        )
        prefix = (
            "local safeRequire = require\n"
            "local DEFINITIONS = {\n"
        )
        suffix = (
            "}\n"
            "local definition = DEFINITIONS[key]\n"
            "safeRequire(definition.module)\n"
        )
        positive = (
            prefix
            + "  one = { module = 'Iris/Data/IrisCapabilities' },\n"
            + "  two = { module = 'Iris/Data/IrisClassifications' },\n"
            + suffix
        )
        reads, blockers = common.lua_structural_registry_reads(
            source,
            positive,
            input_path_by_name={},
        )
        self.assertEqual(blockers, [])
        self.assertEqual(
            {row[0] for row in reads},
            {
                "Iris/media/lua/client/Iris/Data/IrisCapabilities.lua",
                "Iris/media/lua/client/Iris/Data/IrisClassifications.lua",
            },
        )

        nonliteral = (
            prefix
            + "  one = { module = dynamicModule },\n"
            + suffix
        )
        _, nonliteral_blockers = common.lua_structural_registry_reads(
            source,
            nonliteral,
            input_path_by_name={},
        )
        self.assertTrue(
            any(
                blocker.startswith(
                    "incomplete_lua_module_table_reference:"
                )
                for blocker in nonliteral_blockers
            )
        )
        self.assertTrue(
            any(
                blocker.startswith(
                    "unresolved_registry_loader_reference:"
                )
                for blocker in nonliteral_blockers
            )
        )

        duplicate = (
            prefix
            + "  one = { module = 'Iris/Data/IrisCapabilities' },\n"
            + "  two = { module = 'Iris/Data/IrisCapabilities' },\n"
            + suffix
        )
        _, duplicate_blockers = common.lua_structural_registry_reads(
            source,
            duplicate,
            input_path_by_name={},
        )
        self.assertTrue(
            any(
                blocker.startswith(
                    "incomplete_lua_module_table_reference:"
                )
                for blocker in duplicate_blockers
            )
        )

    def test_default_current_compose_is_rejected_without_mutation(self) -> None:
        protected = (
            V2_ROOT / "output" / "dvf_3_3_rendered.json",
            V2_ROOT / "output" / "style_normalization_changes.jsonl",
            V2_ROOT / "output" / "compose_requeue_candidates.jsonl",
        )
        before = {path: sha256_file(path) if path.is_file() else None for path in protected}
        result = run_script(COMPOSE_TOOL)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "REGISTRY_REAL_CURRENT_PROTECTED_WRITE_DISABLED",
            result.stdout + result.stderr,
        )
        after = {path: sha256_file(path) if path.is_file() else None for path in protected}
        self.assertEqual(before, after)

    def test_round3_preimport_guard_detects_bare_import_before_sentinel(self) -> None:
        runner = load_module(ROUND3_RUNNER, "round3_runner_for_registry_test")
        fixture_root = EVIDENCE_ROOT / "_scaffold_tests" / uuid.uuid4().hex
        fixture_path = fixture_root / "test_preimport_bypass.py"
        sentinel = fixture_root / "sentinel.txt"
        fixture_root.mkdir(parents=True)
        fixture_path.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            "TOOLS_ROOT = Path('Iris/build/description/v2/tools/build')\n"
            "sys.path.insert(0, str(TOOLS_ROOT))\n"
            "import dvf_3_3_completion_vocabulary_external_gate_vocabulary_split as bypass\n"
            f"Path({str(sentinel)!r}).write_text('imported', encoding='utf-8')\n",
            encoding="utf-8",
        )
        try:
            rows = runner.tools_build_import_candidates(fixture_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(
                rows[0]["module"],
                "dvf_3_3_completion_vocabulary_external_gate_vocabulary_split",
            )
            self.assertTrue(rows[0]["literal_tools_sys_path_present"])
            self.assertFalse(sentinel.exists())
        finally:
            if fixture_root.exists():
                resolved = fixture_root.resolve()
                resolved.relative_to(EVIDENCE_ROOT.resolve())
                shutil.rmtree(resolved)


if __name__ == "__main__":
    unittest.main()
