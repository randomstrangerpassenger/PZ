from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


IRIS_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_SCRIPT_PATH = IRIS_ROOT / "tools" / "package_iris.ps1"
LOOKUP_VALIDATOR_PATH = IRIS_ROOT / "tools" / "validate_runtime_lookup_indexes.ps1"
PROJECTION_VALIDATOR_PATH = IRIS_ROOT / "tools" / "validate_layer3_package_projection.ps1"
REPO_ROOT = IRIS_ROOT.parent
# The canonical runner supplies its external TEMP/TMP root. Do not escape it.
EXTERNAL_TEMP_ROOT = Path(tempfile.gettempdir())


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_package(*arguments: str) -> subprocess.CompletedProcess[str]:
    powershell = shutil.which("powershell")
    if powershell is None:
        raise AssertionError("powershell executable is required")
    return subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PACKAGE_SCRIPT_PATH),
            *arguments,
        ],
        cwd=REPO_ROOT,
        env={**os.environ, "UV_PYTHON": sys.executable, "UV_PYTHON_DOWNLOADS": "never"},
        text=True,
        capture_output=True,
        check=False,
    )


def run_lookup_validator(data_root: Path) -> subprocess.CompletedProcess[str]:
    powershell = shutil.which("powershell")
    if powershell is None:
        raise AssertionError("powershell executable is required")
    return subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LOOKUP_VALIDATOR_PATH),
            "-DataRoot",
            str(data_root),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_projection_validator(data_root: Path) -> subprocess.CompletedProcess[str]:
    powershell = shutil.which("powershell")
    if powershell is None:
        raise AssertionError("powershell executable is required")
    return subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PROJECTION_VALIDATOR_PATH),
            "-DataRoot",
            str(data_root),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class PackageLayer3ChunksOnlyContractTest(unittest.TestCase):
    def repository_package_tree_identity(self) -> tuple[tuple[str, str], ...]:
        root = IRIS_ROOT / "build/package"
        if not root.exists():
            return ()
        return tuple(
            (path.relative_to(root).as_posix(), sha256_file(path))
            for path in sorted(root.rglob("*"))
            if path.is_file()
        )

    def external_lookup_data_copy(self, temporary: str) -> Path:
        source = IRIS_ROOT / "media/lua/client/Iris/Data"
        data = Path(temporary) / "Data"
        data.mkdir()
        pointer = (source / "IrisLayer3DataCurrent.lua").read_text(encoding="utf-8")
        generation_id = re.search(r"dvf33-[0-9a-f]{64}", pointer).group(0)
        generation = source / "IrisLayer3Generations" / generation_id
        index_text = (generation / "IrisLayer3DataChunkIndex.lua").read_text(encoding="utf-8")
        index_text = index_text.replace(
            f"Iris/Data/IrisLayer3Generations/{generation_id}/Chunks",
            "Iris/Data/IrisLayer3DataChunks",
        )
        (data / "IrisLayer3DataChunkIndex.lua").write_text(
            index_text, encoding="utf-8", newline="\n"
        )
        shutil.copytree(generation / "Chunks", data / "IrisLayer3DataChunks")
        shutil.copytree(source / "UseCaseDescriptions", data / "UseCaseDescriptions")
        return data

    def test_runtime_package_rejects_named_output_root_guards_without_write(self) -> None:
        cases = {
            "missing_output_root": (
                ("-PackageApplicability", "current_runtime_payload"),
                "runtime_package_explicit_output_root_required",
            ),
            "repository_output_root": (
                (
                    "-OutputRoot",
                    str(REPO_ROOT),
                    "-PackageApplicability",
                    "current_runtime_payload",
                ),
                "runtime_package_output_root_must_be_external",
            ),
        }
        for case_id, (arguments, expected_error) in cases.items():
            with self.subTest(case_id=case_id):
                before = self.repository_package_tree_identity()
                completed = run_package(*arguments)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(expected_error, completed.stdout + completed.stderr)
                self.assertEqual(before, self.repository_package_tree_identity())

    def test_runtime_package_rejects_reparse_alias_into_repository_without_write(self) -> None:
        before = self.repository_package_tree_identity()
        with tempfile.TemporaryDirectory(dir=EXTERNAL_TEMP_ROOT) as temporary:
            alias = Path(temporary) / "repository-alias"
            created = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(alias), str(REPO_ROOT)],
                text=True,
                capture_output=True,
                check=False,
            )
            if created.returncode != 0 or not alias.exists():
                raise AssertionError(
                    "Windows junction support is required for package output safety: "
                    + created.stdout
                    + created.stderr
                )
            try:
                completed = run_package(
                    "-OutputRoot",
                    str(alias),
                    "-PackageApplicability",
                    "current_runtime_payload",
                )
            finally:
                os.rmdir(alias)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "runtime_package_output_root_reparse_component",
                completed.stdout + completed.stderr,
            )
        self.assertEqual(before, self.repository_package_tree_identity())

    def test_lookup_validator_rejects_named_failure_variants(self) -> None:
        cases = (
            (
                "schema",
                "IrisLayer3DataChunkIndex.lua",
                "text_transform",
                lambda text: text.replace(
                    'schema_version = "iris_layer3_chunk_range_index_v1"',
                    'schema_version = "invalid"',
                    1,
                ),
                "runtime_payload_lookup_index_",
            ),
            (
                "module",
                "IrisLayer3DataChunkIndex.lua",
                "text_transform",
                lambda text: text.replace(
                    'module = "Iris/Data/IrisLayer3DataChunks/Chunk001"',
                    'module = "Iris/Data/UseCaseDescriptions/Chunk001"',
                    1,
                ),
                "runtime_payload_lookup_index_",
            ),
            (
                "range",
                "IrisLayer3DataChunkIndex.lua",
                "text_transform",
                lambda text: text.replace('first = "Base.223Box"', 'first = "Base.ZZZ"', 1),
                "runtime_payload_lookup_index_",
            ),
            (
                "line_count",
                "UseCaseDescriptions/LineCountIndex.lua",
                "text_transform",
                lambda text: text.replace('["Base.223Box"] = 1,', '["Base.223Box"] = 999,', 1),
                "runtime_payload_lookup_index_",
            ),
            (
                "line_count_duplicate_and_omission",
                "UseCaseDescriptions/LineCountIndex.lua",
                "text_transform",
                lambda text: text.replace(
                    '["Base.223Bullets"] = 2,',
                    '["Base.223Box"] = 1,',
                    1,
                ),
                "runtime_payload_lookup_index_",
            ),
            (
                "line_count_alternate_format_duplicate_override",
                "UseCaseDescriptions/LineCountIndex.lua",
                "text_transform",
                lambda text: text.replace(
                    '        ["Base.223Box"] = 1,',
                    (
                        '        ["Base.223Box"] = 1,\n'
                        '        ["Base.223Box"]=999,'
                    ),
                    1,
                ),
                "runtime_payload_lookup_index_",
            ),
            (
                "stale_layer3_internal_hash",
                "IrisLayer3DataChunkIndex.lua",
                "internal_hash",
                None,
                "runtime_payload_lookup_index_hash_mismatch",
            ),
            (
                "mutated_layer3_chunk",
                "IrisLayer3DataChunks/Chunk001.lua",
                "append_raw",
                None,
                "runtime_payload_lookup_index_hash_mismatch",
            ),
            (
                "mutated_usecase_chunk",
                "UseCaseDescriptions/Chunk001.lua",
                "append_raw",
                None,
                "runtime_payload_lookup_index_hash_mismatch",
            ),
            (
                "missing_usecase_chunk",
                "UseCaseDescriptions/Chunk001.lua",
                "unlink",
                None,
                "runtime_payload_lookup_index_target_missing",
            ),
        )
        for case_id, relative, mutation, transform, expected_error in cases:
            with self.subTest(case_id=case_id), tempfile.TemporaryDirectory(
                dir=EXTERNAL_TEMP_ROOT
            ) as temporary:
                data = self.external_lookup_data_copy(temporary)
                target = data / relative
                if mutation == "text_transform":
                    original = target.read_text(encoding="utf-8")
                    changed = transform(original)
                    self.assertNotEqual(original, changed)
                    target.write_text(changed, encoding="utf-8", newline="\n")
                elif mutation == "internal_hash":
                    original = target.read_text(encoding="utf-8")
                    changed, count = re.subn(
                        r'sha256 = "[0-9a-f]{64}"',
                        'sha256 = "' + ("0" * 64) + '"',
                        original,
                        count=1,
                    )
                    self.assertEqual(1, count)
                    target.write_text(changed, encoding="utf-8", newline="\n")
                elif mutation == "append_raw":
                    target.write_bytes(target.read_bytes() + b"\n")
                else:
                    self.assertEqual(mutation, "unlink")
                    target.unlink()
                completed = run_lookup_validator(data)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(expected_error, completed.stdout + completed.stderr)

    def test_runtime_package_rejects_undeclared_chunk_file_before_write(self) -> None:
        pointer = (IRIS_ROOT / "media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua").read_text(encoding="utf-8")
        generation_id = re.search(r'dvf33-[0-9a-f]{64}', pointer).group(0)
        chunk_root = IRIS_ROOT / "media/lua/client/Iris/Data/IrisLayer3Generations" / generation_id / "Chunks"
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
                "runtime_payload_stateless_generation_file_universe_mismatch",
                completed.stdout + completed.stderr,
            )
            self.assertFalse((output / "Iris").exists())
            self.assertFalse(stale.exists())

    def test_runtime_package_rejects_nested_chunk_entry_before_write(self) -> None:
        pointer = (IRIS_ROOT / "media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua").read_text(encoding="utf-8")
        generation_id = re.search(r'dvf33-[0-9a-f]{64}', pointer).group(0)
        chunk_root = IRIS_ROOT / "media/lua/client/Iris/Data/IrisLayer3Generations" / generation_id / "Chunks"
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
                "runtime_payload_stateless_generation_file_universe_mismatch",
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
            generation_id = receipt["generation_id"]
            package_generations = sorted(
                path.name
                for path in (package / "IrisLayer3Generations").iterdir()
                if path.is_dir()
            )
            self.assertEqual([generation_id], package_generations)
            self.assertFalse((package / "IrisLayer3DataChunks").exists())
            self.assertEqual(
                sha256_file(live / "IrisLayer3DataChunks.lua"),
                sha256_file(package / "IrisLayer3DataChunks.lua"),
            )
            expected_support = {
                "IrisLayer3DataChunks.lua",
                "IrisLayer3DataChunkIndex.lua",
                "IrisLayer3DataLookup.lua",
                "UseCaseDescriptions/ChunkIndex.lua",
                "UseCaseDescriptions/LineCountIndex.lua",
                "IrisUseCaseDescriptionsLookup.lua",
                "IrisRuntimeLookupDiagnostics.lua",
                "IrisRuntimeLookupPackageIdentity.json",
                "IrisUseCaseDescriptions.lua",
                "UseCaseDescriptions/RequirementsLookup.lua",
            }
            self.assertEqual(expected_support, {row["path"] for row in receipt["support_files"]})
            for name in expected_support:
                self.assertEqual(sha256_file(live / name), sha256_file(package / name))
            package_script = PACKAGE_SCRIPT_PATH.read_text(encoding="utf-8")
            self.assertEqual(
                2,
                package_script.count(
                    "Assert-RuntimeLookupPackageParity -DataRoot"
                ),
            )

    def test_package_projection_validator_rejects_extra_generation_and_pointer_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(dir=EXTERNAL_TEMP_ROOT) as temporary:
            output = Path(temporary)
            completed = run_package(
                "-OutputRoot",
                str(output),
                "-PackageApplicability",
                "current_runtime_payload",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = output / "Iris/media/lua/client/Iris/Data"
            generations = data / "IrisLayer3Generations"
            current = next(path for path in generations.iterdir() if path.is_dir())

            extra = generations / ("dvf33-" + ("0" * 64))
            shutil.copytree(current, extra)
            extra_result = run_projection_validator(data)
            self.assertNotEqual(extra_result.returncode, 0)
            self.assertIn(
                "layer3_package_generation_count_invalid",
                extra_result.stdout + extra_result.stderr,
            )
            shutil.rmtree(extra)

            pointer = data / "IrisLayer3DataCurrent.lua"
            original = pointer.read_text(encoding="utf-8")
            pointer.write_text(
                original.replace(current.name, "dvf33-" + ("1" * 64)),
                encoding="utf-8",
                newline="\n",
            )
            pointer_result = run_projection_validator(data)
            self.assertNotEqual(pointer_result.returncode, 0)
            self.assertIn(
                "layer3_package_generation_pointer_mismatch",
                pointer_result.stdout + pointer_result.stderr,
            )

    def test_rtc_certified_payload_still_requires_rtc_guard(self) -> None:
        required_manifest = json.loads(
            (
                REPO_ROOT
                / "Iris/validation/execution/required_validations.json"
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
                    / "Iris/validation/execution/required_validations.json"
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

    def test_package_script_preserves_forbidden_surface_guards(self) -> None:
        script = PACKAGE_SCRIPT_PATH.read_text(encoding="utf-8")
        cases = {
            "layer3_monolith": (
                "$forbiddenPackageFiles = @(",
                "'media\\lua\\client\\Iris\\Data\\IrisLayer3Data.lua'",
                "Forbidden Iris Layer 3 monolith source file detected",
                "Forbidden Iris package monolith output detected",
                "forbidden_files = $forbiddenPackageFiles",
            ),
            "stale_dvf_bridge": (
                "Assert-NoForbiddenIrisDvfBridgeSurface",
                "Forbidden stale Iris DVF bridge artifact detected",
                "media\\lua\\shared\\Iris\\IrisDvfBridgeData.lua",
                "IrisDvfBridgeData.lua",
                "c5ec93914f4a13c227bf1b3958908b860af768113700cecb4c4496b46ad411aa",
                "interaction-cluster-rendered-v0",
                "legacy_6_entry_payload_shape",
            ),
        }
        for case_id, markers in cases.items():
            with self.subTest(case_id=case_id):
                for marker in markers:
                    self.assertIn(marker, script)
                self.assertNotIn("Remove-Item -LiteralPath $candidate -Force", script)

if __name__ == "__main__":
    unittest.main()
