from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]


class IrisResidualRuntimeAcceptanceTest(unittest.TestCase):
    def test_runtime_acceptance_harness_passes_all_registered_axes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-residual-runtime-") as temp:
            output = Path(temp) / "runtime.jsonl"
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(REPO / "Iris/test/run_residual_refactor_acceptance.ps1"),
                    "-Mode",
                    "Acceptance",
                    "-RepositoryRoot",
                    str(REPO),
                    "-OutputPath",
                    str(output),
                ],
                cwd=REPO,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertGreaterEqual(len(rows), 7)
            self.assertEqual({row["status"] for row in rows}, {"pass"})
            self.assertEqual(
                {row["axis"] for row in rows},
                {
                    "presentation_order",
                    "browser_determinism",
                    "mutation_isolation",
                    "wiki_units",
                    "tooltip_lines",
                    "lazy_debug",
                },
            )
            binding = json.loads(output.with_suffix(".binding.json").read_text(encoding="utf-8"))
            self.assertEqual(binding["validation_status"], "passed")
            self.assertEqual(binding["row_count"], len(rows))


if __name__ == "__main__":
    unittest.main()
