from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
DATA = REPO / "Iris/media/lua/client/Iris/Data"
VALIDATOR = REPO / "Iris/tools/validate_runtime_lookup_indexes.ps1"


class LookupPackageParityContractTest(unittest.TestCase):
    def run_validator(self, data_root: Path) -> subprocess.CompletedProcess[str]:
        powershell = shutil.which("powershell")
        self.assertIsNotNone(powershell, "required PowerShell executable is unavailable")
        return subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(VALIDATOR),
                "-DataRoot",
                str(data_root),
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )

    def copy_data(self, destination: Path) -> Path:
        target = destination / "Data"
        target.mkdir()
        for name in (
            "IrisLayer3DataChunkIndex.lua",
            "IrisRuntimeLookupPackageIdentity.json",
        ):
            shutil.copy2(DATA / name, target / name)
        shutil.copytree(DATA / "IrisLayer3DataChunks", target / "IrisLayer3DataChunks")
        shutil.copytree(DATA / "UseCaseDescriptions", target / "UseCaseDescriptions")
        return target

    def test_current_package_has_one_generation_and_full_denominators(self) -> None:
        completed = self.run_validator(DATA)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual("PASS", payload["status"])
        self.assertEqual(2105, payload["layer3_entry_count"])
        self.assertEqual(1631, payload["usecase_entry_count"])
        self.assertEqual(1631, payload["line_count_entry_count"])
        self.assertTrue(payload["generation_id"].startswith("lookup-"))
        self.assertEqual(64, len(payload["source_digest"]))

    def test_stale_or_mixed_generation_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data = self.copy_data(Path(temporary))
            manifest_path = data / "IrisRuntimeLookupPackageIdentity.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["generation_id"] = "lookup-stale"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            completed = self.run_validator(data)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn(
                "runtime_payload_lookup_package_generation_mismatch",
                completed.stdout + completed.stderr,
            )

    def test_chunk_hash_boundary_and_line_count_key_mismatches_fail_closed(self) -> None:
        mutations = (
            ("IrisLayer3DataChunks/Chunk001.lua", r'\["Base\.223Box"\]', '["Base.223BoxX"]'),
            ("UseCaseDescriptions/Chunk001.lua", 'chunk["Base.223Box"]', 'chunk["Base.223BoxX"]'),
            ("UseCaseDescriptions/LineCountIndex.lua", '["Base.223Box"] = 1', '["Base.223BoxX"] = 1'),
        )
        for relative, pattern, replacement in mutations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                data = self.copy_data(Path(temporary))
                path = data / relative
                original = path.read_text(encoding="utf-8")
                mutated, count = re.subn(pattern, replacement, original, count=1)
                self.assertEqual(1, count)
                path.write_text(mutated, encoding="utf-8", newline="\n")
                completed = self.run_validator(data)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn("runtime_payload_lookup_", completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
