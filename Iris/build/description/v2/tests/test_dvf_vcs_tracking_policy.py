from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]

CURRENT_REQUIRED = [
    "Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py",
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json",
]

FORBIDDEN_CURRENT_LOOKING = [
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
]

ROUND3_CLOSURE_PATH = "Iris/_docs/round3/round3_active_core_closure.json"


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )


def git_ls_files(path: str) -> list[str]:
    result = git("ls-files", "--", path)
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_check_ignore_no_index(path: str) -> tuple[bool, str | None]:
    result = git("check-ignore", "--no-index", "-v", path)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if result.returncode != 0 or not lines:
        return False, None
    source, _, _target = lines[-1].partition("\t")
    pattern = source.rsplit(":", 1)[-1]
    return not pattern.startswith("!"), pattern


def normalize_path(path: str) -> str:
    value = path.replace("\\", "/")
    if value.startswith("./"):
        value = value[2:]
    return value.lower()


def is_forbidden_current_looking_path(path: str) -> bool:
    normalized = normalize_path(path)
    forbidden = {normalize_path(candidate) for candidate in FORBIDDEN_CURRENT_LOOKING}
    return normalized in forbidden or normalized.endswith("/media/lua/shared/iris/irisdvfbridgedata.lua")


class DvfVcsTrackingPolicyTest(unittest.TestCase):
    def test_current_required_paths_are_tracked_and_not_ignored(self) -> None:
        for path in CURRENT_REQUIRED:
            with self.subTest(path=path):
                self.assertTrue(git_ls_files(path), f"{path} must be tracked")
                ignored, pattern = git_check_ignore_no_index(path)
                self.assertFalse(ignored, f"{path} is still ignored by {pattern!r}")

    def test_forbidden_current_looking_stale_paths_absent(self) -> None:
        for path in FORBIDDEN_CURRENT_LOOKING:
            with self.subTest(path=path):
                self.assertFalse(git_ls_files(path), f"{path} must not remain tracked")
                self.assertFalse((REPO / path).exists(), f"{path} must not remain in the working tree")

    def test_path_form_normalization_finds_stale_surfaces_only(self) -> None:
        positive_cases = [
            "media\\lua\\shared\\Iris\\IrisDvfBridgeData.lua",
            "media/lua/shared/Iris/IrisDvfBridgeData.lua",
            "Iris.zip/Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
        ]
        for path in positive_cases:
            with self.subTest(path=path):
                self.assertTrue(is_forbidden_current_looking_path(path))
        self.assertFalse(is_forbidden_current_looking_path("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua"))

    def test_package_script_keeps_stale_bridge_guard_surface(self) -> None:
        script = (REPO / "Iris/tools/package_iris.ps1").read_text(encoding="utf-8")
        for marker in [
            "IrisDvfBridgeData.lua",
            "c5ec93914f4a13c227bf1b3958908b860af768113700cecb4c4496b46ad411aa",
            "legacy_6_entry_payload_shape",
            "IrisLayer3Data.lua",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, script)

    def test_round3_current_route_tooling_allowlist_stays_narrow(self) -> None:
        closure = json.loads((REPO / ROUND3_CLOSURE_PATH).read_text(encoding="utf-8"))
        core_modules = set(closure["current_closure_modules"])
        tooling_modules = closure["current_route_allowed_tooling_modules"]
        tooling_rows = closure["current_route_allowed_tooling_rows"]
        policy = closure["current_route_allowed_tooling_policy"]

        self.assertEqual(closure["current_closure_count"], 12)
        self.assertEqual(len(core_modules), 12)
        self.assertEqual(tooling_modules, ["export_dvf_3_3_lua_bridge"])
        self.assertEqual(policy["max_allowed_modules"], 1)
        self.assertEqual(policy["core_closure_count_must_remain"], 12)
        self.assertTrue(policy["modules_are_not_current_core"])
        self.assertTrue(set(tooling_modules).isdisjoint(core_modules))
        self.assertEqual(len(tooling_rows), 1)
        self.assertEqual(tooling_rows[0]["module"], "export_dvf_3_3_lua_bridge")
        self.assertEqual(tooling_rows[0]["owner_class"], "current_regeneration_tooling")
        self.assertFalse(tooling_rows[0]["in_current_closure"])
        self.assertTrue(tooling_rows[0]["import_allowed_for_current_route"])


if __name__ == "__main__":
    unittest.main()
