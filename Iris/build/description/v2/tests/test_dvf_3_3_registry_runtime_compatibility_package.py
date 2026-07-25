from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
PACKAGE_SCRIPT = REPO_ROOT / "Iris" / "tools" / "package_iris.ps1"


class RegistryRuntimeCompatibilityPackageTest(unittest.TestCase):
    def test_package_guard_parameters_are_unconditional_surface(self) -> None:
        text = PACKAGE_SCRIPT.read_text(encoding="utf-8")
        for token in (
            "RegistryCompatibilityContext",
            "RegistryCompatibilityPolicy",
            "RegistryCompatibilityDisposition",
            "RegistryCompatibilityBindingManifest",
            "RegistryCompatibilityRequiredGateState",
            "RegistryCompatibilityProbe",
            "RegistryCompatibilityReceipt",
            "--required-gate",
            "--surface-validation",
        ):
            self.assertIn(token, text)

    def test_partial_override_fails_before_package_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "package"
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(PACKAGE_SCRIPT),
                    "-OutputRoot",
                    str(output),
                    "-RegistryCompatibilityContext",
                    "candidate",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "partial_registry_compatibility_arguments_forbidden",
                completed.stderr,
            )
            self.assertFalse((output / "Iris").exists())
            self.assertFalse((output / "Iris.zip").exists())


if __name__ == "__main__":
    unittest.main()
