from __future__ import annotations

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


class PackageLayer3ChunksOnlyContractTest(unittest.TestCase):
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
