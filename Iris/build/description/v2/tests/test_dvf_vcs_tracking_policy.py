from __future__ import annotations

import json
import importlib
import subprocess
import unittest
from pathlib import Path

from iris_tooling.build.repository_context import configure_repository


REPO = Path(__file__).resolve().parents[5]

CURRENT_REQUIRED = [
    "Iris/tooling/src/iris_tooling/build/export_dvf_3_3_lua_bridge.py",
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
    def test_vcs_path_dispositions(self) -> None:
        cases = (
            *(("required", path) for path in CURRENT_REQUIRED),
            *(("forbidden", path) for path in FORBIDDEN_CURRENT_LOOKING),
        )
        for disposition, path in cases:
            with self.subTest(disposition=disposition, path=path):
                tracked = git_ls_files(path)
                if disposition == "required":
                    self.assertTrue(tracked, f"{path} must be tracked")
                    ignored, pattern = git_check_ignore_no_index(path)
                    self.assertFalse(ignored, f"{path} is still ignored by {pattern!r}")
                else:
                    self.assertFalse(tracked, f"{path} must not remain tracked")
                    self.assertFalse(
                        (REPO / path).exists(),
                        f"{path} must not remain in the working tree",
                    )

        current_build = REPO / "Iris/tooling/src/iris_tooling/build"
        predecessor_build = REPO / "Iris/build/description/v2/tools/build"
        current_implementation_names = {
            path.name
            for path in current_build.rglob("*.py")
            if path.name != "__init__.py"
        }
        remaining_predecessor_copies = sorted(
            path.relative_to(REPO).as_posix()
            for path in predecessor_build.rglob("*.py")
            if path.name in current_implementation_names
        )
        self.assertEqual(remaining_predecessor_copies, [])

        current_reference_surfaces = (
            current_build,
            REPO / "Iris/tooling/src/iris_tooling/domains",
            REPO / "Iris/validation/execution/run_repository_tests.py",
            REPO / "Iris/build/rightclick_evidence_pipeline.py",
            REPO / "Iris/build/recipe_evidence_pipeline.py",
            REPO / "Iris/build/tools/common",
        )
        forbidden_references = []
        for surface in current_reference_surfaces:
            paths = surface.rglob("*.py") if surface.is_dir() else (surface,)
            for source in paths:
                text = source.read_text(encoding="utf-8")
                if (
                    "Iris/build/description/v2/tools/build/" in text
                    or "build.description.v2.tools.build" in text
                ):
                    forbidden_references.append(source.relative_to(REPO).as_posix())
        self.assertEqual(forbidden_references, [])

        configure_repository(REPO)
        exporter = importlib.import_module(
            "iris_tooling.build.export_dvf_3_3_lua_bridge"
        )
        self.assertEqual(
            exporter.__spec__.name,
            "iris_tooling.build.export_dvf_3_3_lua_bridge",
        )
        self.assertNotIn(
            "Iris/build/description/v2/tools/build",
            Path(exporter.__file__).resolve().as_posix(),
        )

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

    def test_round3_current_route_tooling_allowlist_stays_narrow(self) -> None:
        closure = json.loads((REPO / ROUND3_CLOSURE_PATH).read_text(encoding="utf-8"))
        core_modules = set(closure["current_closure_modules"])
        tooling_modules = closure["current_route_allowed_tooling_modules"]
        tooling_rows = closure["current_route_allowed_tooling_rows"]
        policy = closure["current_route_allowed_tooling_policy"]

        self.assertEqual(closure["current_closure_count"], 12)
        self.assertEqual(len(core_modules), 12)
        self.assertEqual(
            tooling_modules,
            [
                "export_dvf_3_3_lua_bridge",
                "iar_public_text_assessment",
                "public_text_quality_acceptance",
                "naturalization_compiler_identity",
                "dvf_3_3_generation_contract",
                "build_dvf_3_3_complete_generation",
                "validate_dvf_3_3_complete_generation",
                "install_dvf_3_3_complete_generation",
                "dvf_3_3_runtime_compatibility",
            ],
        )
        self.assertEqual(policy["max_allowed_modules"], 9)
        self.assertEqual(policy["core_closure_count_must_remain"], 12)
        self.assertTrue(policy["modules_are_not_current_core"])
        self.assertTrue(set(tooling_modules).isdisjoint(core_modules))
        self.assertEqual(len(tooling_rows), 9)
        self.assertEqual(tooling_rows[0]["module"], "export_dvf_3_3_lua_bridge")
        self.assertEqual(tooling_rows[0]["owner_class"], "current_regeneration_tooling")
        self.assertFalse(tooling_rows[0]["in_current_closure"])
        self.assertTrue(tooling_rows[0]["import_allowed_for_current_route"])
        self.assertEqual(
            [row["module"] for row in tooling_rows[1:4]],
            [
                "iar_public_text_assessment",
                "public_text_quality_acceptance",
                "naturalization_compiler_identity",
            ],
        )
        for row in tooling_rows[1:4]:
            self.assertEqual(row["owner_class"], "reusable_iar_validation_tooling")
        self.assertEqual(
            [row["owner_class"] for row in tooling_rows[4:]],
            [
                "stateless_generation_contract",
                "stateless_generation_tooling",
                "stateless_generation_validation",
                "protected_generation_installer",
                "generation_key_identity_validation",
            ],
        )
        for row in tooling_rows[4:]:
            self.assertFalse(row["in_current_closure"])
            self.assertTrue(row["import_allowed_for_current_route"])
            self.assertFalse(row["in_current_closure"])
            self.assertTrue(row["import_allowed_for_current_route"])


if __name__ == "__main__":
    unittest.main()
