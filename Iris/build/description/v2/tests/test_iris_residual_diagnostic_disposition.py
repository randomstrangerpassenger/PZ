from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
MODULE_PATH = REPO / "Iris/validation/residual_refactor/run_diagnostic_disposition.py"
SPEC = importlib.util.spec_from_file_location("iris_residual_diagnostic", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def create_junction(link: Path, target: Path) -> None:
    powershell = shutil.which("powershell")
    if powershell is None:
        raise unittest.SkipTest("Windows PowerShell 5.1 is required for the junction fixture")
    completed = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-Command",
            "& { param($link, $target) New-Item -ItemType Junction -Path $link -Target $target -ErrorAction Stop | Out-Null }",
            str(link),
            str(target),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)


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

    def test_external_raw_and_disposition_outputs_preserve_tagged_path_and_hash_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-diagnostic-external-") as temporary:
            external = Path(temporary).resolve()
            source_root = external / "source"
            raw_root = external / "raw-root"
            disposition_root = external / "disposition-root"
            for root in (source_root, raw_root, disposition_root):
                root.mkdir()
            runner = source_root / "diagnostic_runner.py"
            raw = {
                "success": False,
                "failures": [
                    {
                        "test_id": "test_external.Case.test_advisory",
                        "traceback": "AssertionError: external advisory",
                    }
                ],
                "errors": [],
            }
            runner.write_text(
                "import argparse,json\n"
                "p=argparse.ArgumentParser(); p.add_argument('--class'); p.add_argument('--out'); a=p.parse_args()\n"
                f"open(a.out, 'w', encoding='utf-8').write(json.dumps({raw!r}))\n"
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            fingerprint = MODULE.finding_rows(raw, REPO)[0]["traceback_fingerprint"]
            dispositions = source_root / "dispositions.json"
            dispositions.write_text(
                json.dumps(
                    {
                        "dispositions": [
                            {
                                "test_id": "test_external.Case.test_advisory",
                                "kind": "failure",
                                "traceback_fingerprint": fingerprint,
                                "owner": "residual_refactor_plan",
                                "reason": "external adapter fixture",
                                "expiry_readpoint": "2026-08-05",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            raw_out = raw_root / "raw.json"
            output = disposition_root / "disposition.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(MODULE_PATH),
                    "--runner",
                    str(runner),
                    "--raw-out",
                    str(raw_out),
                    "--dispositions",
                    str(dispositions),
                    "--out",
                    str(output),
                ],
                cwd=REPO,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            stdout = json.loads(completed.stdout)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(stdout["raw_exit_code"], 1)
            self.assertFalse(stdout["blocking"])
            self.assertEqual(stdout["output_sha256"], MODULE.sha256_file(output))
            self.assertEqual(report["raw_report_path"]["kind"], "external_absolute")
            self.assertEqual(report["raw_report_path"]["sha256"], MODULE.sha256_file(raw_out))
            self.assertEqual(report["dispositions_path"]["kind"], "external_absolute")
            self.assertEqual(
                report["dispositions_path"]["sha256"], MODULE.sha256_file(dispositions)
            )
            self.assertEqual(report["output_path"]["kind"], "external_absolute")
            self.assertFalse(report["output_path"]["exists_before_write"])
            self.assertEqual(report["output_path"]["write_disposition"], "create_new")
            self.assertEqual(report["command"]["argv"][-1]["kind"], "path")
            self.assertEqual(
                report["command"]["argv"][-1]["value"]["kind"], "external_absolute"
            )

    def test_unadopted_successor_policy_blocks_before_external_diagnostic_execution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-diagnostic-unadopted-") as temporary:
            root = Path(temporary).resolve()
            checkout = root / "checkout"
            raw_root = root / "raw-root"
            disposition_root = root / "disposition-root"
            for path in (checkout, raw_root, disposition_root):
                path.mkdir()
            initialized = subprocess.run(
                ["git", "init", "--quiet", str(checkout)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            raw_out = raw_root / "raw.json"
            output = disposition_root / "blocked.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(MODULE_PATH),
                    "--runner",
                    str(MODULE_PATH),
                    "--raw-out",
                    str(raw_out),
                    "--dispositions",
                    str(MODULE_PATH),
                    "--out",
                    str(output),
                ],
                cwd=checkout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertFalse(raw_out.exists())
            receipt = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(receipt["validation_status"], "blocked")
            self.assertEqual(receipt["execution_status"], "not_run")
            self.assertEqual(receipt["disposition"], "planned_change_not_adopted")
            self.assertTrue(receipt["blocking"])

    def test_junction_output_alias_into_checkout_is_rejected_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-diagnostic-junction-") as temporary:
            root = Path(temporary).resolve()
            checkout = root / "checkout"
            external = root / "external"
            repository_target = checkout / "junction-output-target"
            disposition_root = external / "disposition-root"
            for path in (checkout, external, repository_target, disposition_root):
                path.mkdir()
            initialized = subprocess.run(
                ["git", "init", "--quiet", str(checkout)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            raw_alias = external / "raw-junction"
            create_junction(raw_alias, repository_target)
            runner_marker = external / "runner-invoked.txt"
            runner = external / "runner.py"
            runner.write_text(
                f"from pathlib import Path\nPath({str(runner_marker)!r}).write_text('ran')\n",
                encoding="utf-8",
            )
            output = disposition_root / "disposition.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(MODULE_PATH),
                    "--runner",
                    str(runner),
                    "--raw-out",
                    str(raw_alias / "raw.json"),
                    "--dispositions",
                    str(runner),
                    "--out",
                    str(output),
                ],
                cwd=checkout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("reparse ancestor", completed.stderr)
            self.assertFalse(output.exists())
            self.assertFalse(runner_marker.exists())
            self.assertFalse(any(repository_target.iterdir()))


if __name__ == "__main__":
    unittest.main()
