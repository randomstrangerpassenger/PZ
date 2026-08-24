from __future__ import annotations

import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
RUNNER_PATH = REPO / "Iris/_docs/round3/round3_run_contract_tests.py"


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "round3_run_contract_tests_applicability", RUNNER_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError("current-route runner is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Round3CurrentRouteApplicabilityTest(unittest.TestCase):
    def test_applicability_authority_hash_uses_decoded_eol_identity(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority = root / "authority.json"
            canonical = b'{"authority":"current"}\n'
            authority.write_bytes(canonical.replace(b"\n", b"\r\n"))
            manifest = {
                "applicability_overrides": {
                    "schema_version": "round3-current-route-applicability-v1",
                    "current_authority_basis_path": "authority.json",
                    "current_authority_sha256": hashlib.sha256(canonical).hexdigest(),
                    "historical_optional_evidence": {
                        "tests": [],
                        "artifacts": [],
                    },
                },
                "required_tests": [{"test_id": "current.test"}],
                "required_artifacts": [],
            }
            original_repo = runner.REPO
            runner.REPO = root
            try:
                runner.validate_applicability_overrides(manifest)
            finally:
                runner.REPO = original_repo

    def test_required_validation_payload_reports_both_applicability_denominators(self) -> None:
        runner = load_runner()
        manifest = {
            "required_tests": [
                {"test_id": "current.test", "applicability": "current_product_required"},
                {
                    "test_id": "historical.test",
                    "applicability": "historical_optional_evidence",
                },
            ],
            "required_artifacts": [
                {
                    "path": "missing-history.json",
                    "applicability": "historical_optional_evidence",
                }
            ],
        }
        result = unittest.TestResult()
        payload = runner.required_validation_payload(
            manifest=manifest,
            selected_ids=["current.test"],
            result=result,
        )
        self.assertEqual(payload["required_test_count"], 1)
        self.assertEqual(payload["required_artifact_count"], 0)
        self.assertEqual(
            payload["historical_optional_evidence"],
            {
                "test_count": 1,
                "artifact_count": 1,
                "tests": ["historical.test"],
                "artifacts": ["missing-history.json"],
            },
        )

    def test_historical_optional_tests_are_retained_but_not_selected(self) -> None:
        runner = load_runner()
        manifest = {
            "required_tests": [
                {"test_id": "current.test", "applicability": "current_product_required"},
                {
                    "test_id": "historical.test",
                    "applicability": "historical_optional_evidence",
                    "authority_basis_path": "history/evidence.json",
                    "current_authority_sha256": "a" * 64,
                },
            ]
        }
        self.assertEqual(runner.required_test_ids(manifest), ["current.test"])
        self.assertEqual(
            runner.combined_test_ids(
                ["current.test", "historical.test"], manifest
            ),
            ["current.test"],
        )
        self.assertEqual(
            runner.historical_optional_test_ids(manifest), ["historical.test"]
        )

    def test_historical_optional_artifact_is_not_synthesized_or_required(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing.json"
            relative = missing.relative_to(missing.anchor).as_posix()
            manifest = {
                "required_artifacts": [
                    {
                        "path": relative,
                        "applicability": "historical_optional_evidence",
                        "authority_basis_path": "history/manifest.json",
                        "current_authority_sha256": "b" * 64,
                    }
                ]
            }
            original_repo = runner.REPO
            runner.REPO = Path(missing.anchor)
            try:
                self.assertEqual(runner.artifact_check_errors(manifest), [])
                self.assertFalse(missing.exists())
            finally:
                runner.REPO = original_repo

    def test_unclassified_missing_artifact_remains_fail_closed(self) -> None:
        runner = load_runner()
        manifest = {"required_artifacts": [{"path": "missing-current.json"}]}
        errors = runner.artifact_check_errors(manifest)
        self.assertEqual(errors[0]["code"], "missing_required_artifact")


if __name__ == "__main__":
    unittest.main()
