from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


IRIS_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_SCRIPT_PATH = IRIS_ROOT / "tools" / "package_iris.ps1"
ACTIVE_LAYER3_MONOLITH_PATH = (
    IRIS_ROOT
    / "media"
    / "lua"
    / "client"
    / "Iris"
    / "Data"
    / "IrisLayer3Data.lua"
)
REPO_ROOT = IRIS_ROOT.parent
ROOT_STALE_DVF_BRIDGE_PATH = (
    REPO_ROOT / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua"
)
IRIS_STALE_DVF_BRIDGE_PATH = (
    IRIS_ROOT / "media" / "lua" / "shared" / "Iris" / "IrisDvfBridgeData.lua"
)
EXTERNAL_TEMP_ROOT = Path(
    r"C:\Users\Public\Documents\ESTsoft\CreatorTemp"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_package(*arguments: str) -> subprocess.CompletedProcess[str]:
    powershell = shutil.which("powershell")
    if powershell is None:
        raise AssertionError("powershell executable is required")
    return subprocess.run(
        [
            powershell,
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PACKAGE_SCRIPT_PATH),
            *arguments,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class PackageLayer3ChunksOnlyContractTest(unittest.TestCase):
    def test_runtime_package_rejects_undeclared_chunk_file_before_write(self) -> None:
        chunk_root = (
            IRIS_ROOT / "media/lua/client/Iris/Data/IrisLayer3DataChunks"
        )
        stale = chunk_root / "stale.lua"
        self.assertFalse(stale.exists())
        with tempfile.TemporaryDirectory(dir=EXTERNAL_TEMP_ROOT) as temporary:
            output = Path(temporary)
            try:
                stale.write_text("return {}\n", encoding="utf-8")
                completed = run_package(
                    "-OutputRoot",
                    str(output),
                    "-PackageApplicability",
                    "current_runtime_payload",
                )
            finally:
                stale.unlink(missing_ok=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "runtime_payload_chunk_surface_mismatch",
                completed.stdout + completed.stderr,
            )
            self.assertFalse((output / "Iris").exists())
            self.assertFalse(stale.exists())

    def test_runtime_package_rejects_nested_chunk_entry_before_write(self) -> None:
        chunk_root = (
            IRIS_ROOT / "media/lua/client/Iris/Data/IrisLayer3DataChunks"
        )
        nested = chunk_root / "nested-fixture"
        nested_file = nested / "Chunk9999.lua"
        self.assertFalse(nested.exists())
        with tempfile.TemporaryDirectory(dir=EXTERNAL_TEMP_ROOT) as temporary:
            output = Path(temporary)
            try:
                nested.mkdir()
                nested_file.write_text("return {}\n", encoding="utf-8")
                completed = run_package(
                    "-OutputRoot",
                    str(output),
                    "-PackageApplicability",
                    "current_runtime_payload",
                )
            finally:
                nested_file.unlink(missing_ok=True)
                if nested.exists():
                    nested.rmdir()
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "runtime_payload_chunk_surface_mismatch",
                completed.stdout + completed.stderr,
            )
            self.assertFalse((output / "Iris").exists())
            self.assertFalse(nested.exists())

    def test_current_runtime_payload_package_does_not_require_rtc_bundle(self) -> None:
        with tempfile.TemporaryDirectory(dir=EXTERNAL_TEMP_ROOT) as temporary:
            output = Path(temporary)
            completed = run_package(
                "-OutputRoot",
                str(output),
                "-PackageApplicability",
                "current_runtime_payload",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            receipt = json.loads(
                (output / "runtime_payload_package_identity.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(receipt["status"], "PASS")
            self.assertEqual(receipt["applicability"], "current_runtime_payload")
            self.assertEqual(receipt["chunk_count"], 11)
            self.assertTrue(receipt["bidirectional_file_set_equal"])
            self.assertEqual(receipt["hash_mismatch_count"], 0)
            self.assertEqual(receipt["forbidden_file_count"], 0)
            live = IRIS_ROOT / "media/lua/client/Iris/Data"
            package = output / "Iris/media/lua/client/Iris/Data"
            self.assertEqual(
                sha256_file(live / "IrisLayer3DataChunks.lua"),
                sha256_file(package / "IrisLayer3DataChunks.lua"),
            )

    def test_rtc_certified_payload_still_requires_rtc_guard(self) -> None:
        required_manifest = json.loads(
            (
                REPO_ROOT
                / "Iris/_docs/round3/current_route_required_validations.json"
            ).read_text(encoding="utf-8")
        )
        selection = required_manifest["registry_runtime_compatibility"]
        bundle = REPO_ROOT / selection["bundle_root"]
        with tempfile.TemporaryDirectory(dir=EXTERNAL_TEMP_ROOT) as temporary:
            output = Path(temporary)
            completed = run_package(
                "-OutputRoot",
                str(output),
                "-PackageApplicability",
                "rtc_certified_payload",
                "-RegistryCompatibilityContext",
                "canonical_durable",
                "-RegistryCompatibilityPolicy",
                str(bundle / "registry_runtime_compatibility_policy.json"),
                "-RegistryCompatibilityDisposition",
                str(bundle / "current_collision_disposition.json"),
                "-RegistryCompatibilityBindingManifest",
                str(bundle / "candidate_contract_binding_manifest.json"),
                "-RegistryCompatibilityRequiredGateState",
                "live_gate_adopted",
                "-RegistryCompatibilityRequiredManifest",
                str(
                    REPO_ROOT
                    / "Iris/_docs/round3/current_route_required_validations.json"
                ),
            )
            self.assertNotEqual(completed.returncode, 0)
            combined = completed.stdout + completed.stderr
            self.assertTrue(
                "durable_bundle_destination_drift" in combined
                or "binding_leaf_missing" in combined
                or "implementation_toolchain_freshness_failed" in combined,
                combined,
            )
            self.assertFalse((output / "Iris").exists())

    def test_mixed_package_applicability_fails_before_write(self) -> None:
        with tempfile.TemporaryDirectory(dir=EXTERNAL_TEMP_ROOT) as temporary:
            output = Path(temporary)
            completed = run_package(
                "-OutputRoot",
                str(output),
                "-PackageApplicability",
                "current_runtime_payload",
                "-RegistryCompatibilityContext",
                "candidate",
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "package_applicability_mixed_or_ambiguous",
                completed.stdout + completed.stderr,
            )
            self.assertFalse((output / "Iris").exists())

    def test_package_script_excludes_layer3_monolith(self) -> None:
        script = PACKAGE_SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("$forbiddenPackageFiles = @(", script)
        self.assertIn("'media\\lua\\client\\Iris\\Data\\IrisLayer3Data.lua'", script)
        self.assertIn("Forbidden Iris Layer 3 monolith source file detected", script)
        self.assertIn("Forbidden Iris package monolith output detected", script)
        self.assertNotIn("Remove-Item -LiteralPath $candidate -Force", script)
        self.assertIn("forbidden_files = $forbiddenPackageFiles", script)

    def test_workspace_copy_flow_excludes_layer3_monolith(self) -> None:
        self.assertFalse(ACTIVE_LAYER3_MONOLITH_PATH.exists())

    def test_package_script_fails_loud_on_stale_dvf_bridge_surface(self) -> None:
        script = PACKAGE_SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("Assert-NoForbiddenIrisDvfBridgeSurface", script)
        self.assertIn("Forbidden stale Iris DVF bridge artifact detected", script)
        self.assertIn("media\\lua\\shared\\Iris\\IrisDvfBridgeData.lua", script)
        self.assertIn("IrisDvfBridgeData.lua", script)
        self.assertIn(
            "c5ec93914f4a13c227bf1b3958908b860af768113700cecb4c4496b46ad411aa",
            script,
        )
        self.assertIn("interaction-cluster-rendered-v0", script)
        self.assertIn("legacy_6_entry_payload_shape", script)
        self.assertNotIn("Remove-Item -LiteralPath $candidate -Force", script)

    def test_workspace_copy_flow_excludes_stale_dvf_bridge(self) -> None:
        self.assertFalse(ROOT_STALE_DVF_BRIDGE_PATH.exists())
        self.assertFalse(IRIS_STALE_DVF_BRIDGE_PATH.exists())


if __name__ == "__main__":
    unittest.main()
