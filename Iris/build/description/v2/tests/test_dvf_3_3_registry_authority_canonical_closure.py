from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
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


class RegistryAuthorityBootstrapScaffoldTest(unittest.TestCase):
    def temporary_evidence_root(self) -> Path:
        return ATTEMPTS_ROOT / f"attempt-9999-{uuid.uuid4().hex[:12]}"

    def test_bootstrap_manifest_matches_closed_scaffold_path_set(self) -> None:
        payload = json.loads(BOOTSTRAP_MANIFEST.read_text(encoding="utf-8"))
        expected_paths = [COMMON, RUNNER, VALIDATOR, FOCUSED_TEST]
        expected_rows = []
        for path in expected_paths:
            checkout_bytes = path.read_bytes()
            expected_rows.append(
                {
                    "path": path.relative_to(REPO_ROOT).as_posix(),
                    "exists": path.is_file(),
                    "byte_length": len(checkout_bytes),
                    "sha256": hashlib.sha256(checkout_bytes).hexdigest(),
                }
            )
        self.assertEqual(payload["scaffold_paths"], expected_rows)
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
                "datetime",
                "hashlib",
                "json",
                "os",
                "pathlib",
                "re",
                "shutil",
                "subprocess",
                "typing",
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
        for mode in ("implementation", "wp1", "gate-candidate", "adopt-gate", "finalize"):
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

    def test_post_entry_validator_requirements_are_inert(self) -> None:
        root = self.temporary_evidence_root()
        result = run_script(
            VALIDATOR,
            "--require-implementation",
            "--attempt-id",
            root.name,
            "--evidence-root",
            str(root),
        )
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        payload = json.loads(result.stderr.strip())
        self.assertEqual(payload["status"], "not_implemented")
        self.assertFalse(payload["evidence_written"])
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


if __name__ == "__main__":
    unittest.main()
