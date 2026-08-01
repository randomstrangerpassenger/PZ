from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import uuid
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
RUNNER_PATH = REPO / "Iris/_docs/round3/round3_run_contract_tests.py"
FRESHNESS_TOOL_PATH = REPO / "Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py"


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "round3_run_contract_tests_applicability", RUNNER_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError("current-route runner is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_freshness_tool():
    tools_root = str(FRESHNESS_TOOL_PATH.parent)
    if tools_root not in sys.path:
        sys.path.insert(0, tools_root)
    spec = importlib.util.spec_from_file_location(
        "freshness_reseal_cleanup_for_test", FRESHNESS_TOOL_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError("freshness reseal tool is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Round3CurrentRouteApplicabilityTest(unittest.TestCase):
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

    def test_windows_disposable_cleanup_removes_long_path_without_residue(self) -> None:
        tool = load_freshness_tool()
        root = (
            Path(r"C:\Users\Public\Documents\ESTsoft\CreatorTemp")
            / f"route-cleanup-{uuid.uuid4().hex[:8]}"
        )
        long_file = root / ("n" * 120) / ("e" * 110 + ".json")
        extended_parent = Path("\\\\?\\" + str(long_file.parent))
        extended_file = Path("\\\\?\\" + str(long_file))
        extended_parent.mkdir(parents=True)
        extended_file.write_text("{}\n", encoding="utf-8")
        tool.remove_disposable_tree(root)
        self.assertFalse(root.exists())

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
