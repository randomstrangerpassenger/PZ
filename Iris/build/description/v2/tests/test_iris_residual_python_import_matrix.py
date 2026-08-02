from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]


class IrisResidualPythonImportMatrixTest(unittest.TestCase):
    def test_direct_module_package_bare_import_and_bytes_match_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-residual-import-") as temp:
            report_path = Path(temp) / "matrix.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(REPO / "Iris/validation/residual_refactor/run_python_import_matrix.py"),
                    "--mode",
                    "Closeout",
                    "--python",
                    sys.executable,
                    "--out",
                    str(report_path),
                ],
                cwd=REPO,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["validation_status"], "passed")
            self.assertTrue(report["python_no_user_site"])
            self.assertTrue(report["pythonpath_removed"])
            self.assertEqual({row["validation_status"] for row in report["rows"]}, {"passed"})
            byte_row = next(
                row
                for row in report["rows"]
                if row["case_id"] == "compose_layer3_io.jsonl_byte_contract"
            )
            self.assertTrue(byte_row["byte_contract_equal"])
            self.assertFalse(byte_row["bom"])


if __name__ == "__main__":
    unittest.main()
