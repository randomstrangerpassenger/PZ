from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
MODULE_PATH = REPO / "Iris/validation/residual_refactor/run_diagnostic_disposition.py"
SPEC = importlib.util.spec_from_file_location("iris_residual_diagnostic", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class IrisResidualDiagnosticDispositionTest(unittest.TestCase):
    def test_fingerprints_and_raw_exit_dispositions_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-residual-overlay-a-") as first, tempfile.TemporaryDirectory(
            prefix="iris-residual-overlay-b-"
        ) as second:
            first_root = Path(first)
            second_root = Path(second)
            trace_a = (
                f'File "{first_root}\\tests\\test_one.py", line 7, in test_one\r\n'
                "AssertionError: stable message\r\n"
            )
            trace_b = (
                f'File "{second_root}/tests/test_one.py", line 7, in test_one\n'
                "AssertionError: stable message\n"
            )
            fingerprint_a = MODULE.traceback_fingerprint(
                trace_a, repository_root=REPO, overlay_roots=[first_root]
            )
            fingerprint_b = MODULE.traceback_fingerprint(
                trace_b, repository_root=REPO, overlay_roots=[second_root]
            )
            self.assertEqual(fingerprint_a, fingerprint_b)
            changed = MODULE.traceback_fingerprint(
                trace_b.replace("stable message", "changed message"),
                repository_root=REPO,
                overlay_roots=[second_root],
            )
            self.assertNotEqual(fingerprint_a, changed)
            temp_a = MODULE.traceback_fingerprint(
                "File C:/work/disposable-a/case.py\nValueError: stable",
                repository_root=REPO,
                temporary_basenames=["disposable-a"],
            )
            temp_b = MODULE.traceback_fingerprint(
                "File C:/work/disposable-b/case.py\r\nValueError: stable",
                repository_root=REPO,
                temporary_basenames=["disposable-b"],
            )
            self.assertEqual(temp_a, temp_b)
            changed_exception = MODULE.traceback_fingerprint(
                trace_b.replace("AssertionError", "ValueError"),
                repository_root=REPO,
                overlay_roots=[second_root],
            )
            self.assertNotEqual(fingerprint_b, changed_exception)

        raw = {
            "success": False,
            "failures": [{"test_id": "test_one.Case.test_one", "traceback": "AssertionError: stable"}],
            "errors": [],
        }
        fingerprint = MODULE.finding_rows(raw, REPO)[0]["traceback_fingerprint"]
        dispositions = {
            "dispositions": [
                {
                    "test_id": "test_one.Case.test_one",
                    "kind": "failure",
                    "traceback_fingerprint": fingerprint,
                    "owner": "residual_refactor_plan",
                    "reason": "known advisory fixture",
                    "expiry_readpoint": "2026-08-03",
                }
            ]
        }
        exit_code, report = MODULE.evaluate(
            raw_exit_code=1,
            raw_report=raw,
            dispositions=dispositions,
            repository_root=REPO,
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["validation_status"], "passed")
        self.assertFalse(report["blocking"])
        raw["errors"].append({"test_id": "test_new.Case.test_new", "traceback": "ValueError: new"})
        exit_code, report = MODULE.evaluate(
            raw_exit_code=1,
            raw_report=raw,
            dispositions=dispositions,
            repository_root=REPO,
        )
        self.assertNotEqual(exit_code, 0)
        self.assertTrue(report["blocking"])
        exit_code, report = MODULE.evaluate(
            raw_exit_code=2,
            raw_report=raw,
            dispositions=dispositions,
            repository_root=REPO,
        )
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(report["execution_status"], "failed")
        exit_code, report = MODULE.evaluate(
            raw_exit_code=0,
            raw_report={"success": True, "failures": [], "errors": []},
            dispositions={"dispositions": []},
            repository_root=REPO,
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["finding_status"], "passed")
        exit_code, _ = MODULE.evaluate(
            raw_exit_code=1,
            raw_report=None,
            dispositions={"dispositions": []},
            repository_root=REPO,
        )
        self.assertNotEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
