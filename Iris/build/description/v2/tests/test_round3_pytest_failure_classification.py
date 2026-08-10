from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[5]
CLASSIFIER_PATH = REPO / "Iris/_docs/round3/round3_pytest_failure_classifier.py"
SPEC = importlib.util.spec_from_file_location("round3_pytest_failure_classifier", CLASSIFIER_PATH)
assert SPEC is not None and SPEC.loader is not None
CLASSIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLASSIFIER)


class Round3PytestFailureClassificationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.classes = {
            "tests/current.py": "current",
            "tests/historical.py": "historical",
            "tests/diagnostic.py": "diagnostic",
            "tests/excluded.py": "excluded",
            "tests/mixed.py": "current",
        }

    def _classify(self, failure: dict, **kwargs) -> str:
        return CLASSIFIER.classify_failure(
            failure,
            source_classes=self.classes,
            mixed_sources={"tests/mixed.py"},
            modified_paths=set(kwargs.get("modified_paths", set())),
            mandatory_test_ids={"required.Test.test_gate"},
        )

    def test_fixed_priority_covers_current_modified_mandatory_and_advisory_classes(self) -> None:
        self.assertEqual("current", self._classify({"source_file": "tests/current.py"}))
        self.assertEqual(
            "modified",
            self._classify(
                {"source_file": "tests/historical.py"},
                modified_paths={"tests/historical.py"},
            ),
        )
        self.assertEqual(
            "mandatory",
            self._classify({"source_file": "tests/historical.py", "test_id": "required.Test.test_gate"}),
        )
        self.assertEqual("historical", self._classify({"source_file": "tests/historical.py"}))
        self.assertEqual("diagnostic", self._classify({"source_file": "tests/diagnostic.py"}))
        self.assertEqual("excluded-contract-drift", self._classify({"source_file": "tests/excluded.py"}))
        self.assertEqual("unknown", self._classify({"source_file": "tests/unknown.py"}))

    def test_source_level_mixed_error_is_unknown_and_blocks(self) -> None:
        result = CLASSIFIER.classify_report(
            [{"nodeid": "tests/mixed.py", "source_file": "tests/mixed.py", "source_level": True}],
            source_classes=self.classes,
            mixed_sources={"tests/mixed.py"},
            modified_paths=set(),
            mandatory_test_ids=set(),
        )
        self.assertEqual("unknown", result["failures"][0]["classification"])
        self.assertEqual("unvalidated_but_in_scope", result["scoped_status"])

    def test_modified_or_mandatory_dependency_cannot_hide_behind_historical_source(self) -> None:
        failure = {
            "nodeid": "tests/historical.py::Test::test_x",
            "dependency_paths": ["runtime/current.lua"],
        }
        modified = CLASSIFIER.classify_report(
            [failure],
            source_classes=self.classes,
            mixed_sources=set(),
            modified_paths={"runtime/current.lua"},
            mandatory_test_ids=set(),
        )
        self.assertEqual("modified", modified["failures"][0]["classification"])
        self.assertEqual(
            ["runtime/current.lua"],
            modified["failures"][0]["classification_basis"]["matched_paths"],
        )

        mandatory = CLASSIFIER.classify_report(
            [failure],
            source_classes=self.classes,
            mixed_sources=set(),
            modified_paths=set(),
            mandatory_test_ids=set(),
            mandatory_paths={"runtime/current.lua"},
        )
        self.assertEqual("mandatory", mandatory["failures"][0]["classification"])

    def test_cli_evidence_uses_the_exact_endpoint_range(self) -> None:
        base = "a" * 40
        endpoint = "b" * 40
        with mock.patch.object(
            CLASSIFIER,
            "_run_git",
            return_value=b"runtime/current.lua\n",
        ) as run_git:
            expanded, basis = CLASSIFIER.expand_cli_evidence({
                "modified_subject": {
                    "base_commit": base,
                    "endpoint": endpoint,
                },
                "failures": [],
            })
        run_git.assert_called_once_with(
            "diff", "--name-only", base, endpoint, "--"
        )
        self.assertEqual(["runtime/current.lua"], expanded["modified_paths"])
        self.assertEqual(
            ["diff", "--name-only", base, endpoint, "--"],
            basis["modified_diff_arguments"],
        )

    def test_manual_downgrade_is_rejected_but_escalation_is_allowed(self) -> None:
        with self.assertRaises(ValueError):
            CLASSIFIER.classify_report(
                [{"nodeid": "tests/current.py::Test::test_x"}],
                source_classes=self.classes,
                mixed_sources=set(),
                modified_paths=set(),
                mandatory_test_ids=set(),
                requested_downgrades={"tests/current.py::Test::test_x": "historical"},
            )
        result = CLASSIFIER.classify_report(
            [{"nodeid": "tests/historical.py::Test::test_x"}],
            source_classes=self.classes,
            mixed_sources=set(),
            modified_paths=set(),
            mandatory_test_ids=set(),
            requested_downgrades={"tests/historical.py::Test::test_x": "current"},
        )
        self.assertEqual("current", result["failures"][0]["classification"])
