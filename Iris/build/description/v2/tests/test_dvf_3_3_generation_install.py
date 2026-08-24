from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.build_dvf_3_3_complete_generation import build_complete_generation
from tools.build.install_dvf_3_3_complete_generation import GenerationInstallError, current_generation_id, install_complete_generation
from test_dvf_3_3_complete_generation import copy_generation_inputs


def prepare_repository(root: Path) -> tuple[Path, Path, bytes]:
    repository = root / "repository"
    copy_generation_inputs(repository)
    decision = repository / "Iris/_docs/round3/iar_stateful_architecture_retirement/r2_runtime_layout_owner_decision.json"
    decision.parent.mkdir(parents=True, exist_ok=True)
    decision.write_text(json.dumps({
        "schema_version": "iris-iar-retirement-r2-owner-decision-v1",
        "selection": "B",
        "exact_subject": {"commit": "fixture-commit", "tree": "fixture-tree", "implementation_files": []},
    }), encoding="utf-8")
    legacy_manifest = b'return require("Iris/Data/IrisLayer3DataChunks/Chunk001")\n'
    manifest = repository / "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_bytes(legacy_manifest)
    descriptor = repository / "Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json"
    descriptor.parent.mkdir(parents=True, exist_ok=True)
    descriptor.write_text(json.dumps({"transaction_id": "test"}), encoding="utf-8")
    generation = root / "candidate"
    build_complete_generation(repository_root=repository, output_root=generation)
    return repository, generation, legacy_manifest


class DvfGenerationInstallTest(unittest.TestCase):
    def test_install_uses_one_manifest_switch_and_reapply_is_noop(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-iar-install-") as temporary:
            repository, generation, _ = prepare_repository(Path(temporary))
            result = install_complete_generation(
                repository_root=repository,
                generation_root=generation,
                expected_predecessor_generation_id="legacy:test",
            )
            self.assertEqual(result["status"], "INSTALLED")
            self.assertEqual(result["visibility_switch_count"], 1)
            self.assertEqual(current_generation_id(repository), result["generation_id"])
            noop = install_complete_generation(
                repository_root=repository,
                generation_root=generation,
                expected_predecessor_generation_id=result["generation_id"],
            )
            self.assertEqual(noop["status"], "NOOP_ALREADY_CURRENT")
            self.assertEqual(noop["protected_current_mutation_count"], 0)

    def test_failure_injection_preserves_predecessor_visibility(self) -> None:
        failure_steps = ("candidate_copy", "generation_publish", "before_visibility_switch", "visibility_switch", "after_visibility_switch")
        with tempfile.TemporaryDirectory(prefix="iris-iar-injection-") as temporary:
            root = Path(temporary)
            seed_ready = False
            with self.subTest(step="shared_immutable_seed"):
                try:
                    seed_repository, seed_generation, legacy_manifest = prepare_repository(root / "seed")
                    seed_ready = True
                except Exception as error:
                    self.fail(f"generation install negative seed failed: {error}")
            if not seed_ready:
                for failure_step in failure_steps:
                    with self.subTest(step=failure_step):
                        self.skipTest("blocked_by:shared_immutable_seed")
                return

            for failure_step in failure_steps:
                with self.subTest(step=failure_step):
                    case_root = root / "cases" / failure_step
                    repository = case_root / "repository"
                    generation = case_root / "candidate"
                    shutil.copytree(seed_repository, repository)
                    shutil.copytree(seed_generation, generation)
                    with self.assertRaises(GenerationInstallError):
                        install_complete_generation(
                            repository_root=repository,
                            generation_root=generation,
                            expected_predecessor_generation_id="legacy:test",
                            inject_failure=failure_step,
                        )
                    manifest = repository / "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua"
                    pointer = repository / "Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"
                    self.assertEqual(manifest.read_bytes(), legacy_manifest)
                    self.assertFalse(pointer.exists())
                    self.assertEqual(current_generation_id(repository), "legacy:test")

    def test_expected_predecessor_and_concurrent_install_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-iar-guards-") as temporary:
            repository, generation, _ = prepare_repository(Path(temporary))
            with self.assertRaises(GenerationInstallError) as stale:
                install_complete_generation(
                    repository_root=repository,
                    generation_root=generation,
                    expected_predecessor_generation_id="wrong",
                )
            self.assertEqual(stale.exception.code, "EXPECTED_PREDECESSOR_MISMATCH")
            lock = repository / "Iris/media/lua/client/Iris/Data/IrisLayer3Generations/.install.lock"
            lock.parent.mkdir(parents=True, exist_ok=True)
            lock.write_text("other", encoding="utf-8")
            with self.assertRaises(GenerationInstallError) as concurrent:
                install_complete_generation(
                    repository_root=repository,
                    generation_root=generation,
                    expected_predecessor_generation_id="legacy:test",
                )
            self.assertEqual(concurrent.exception.code, "CONCURRENT_INSTALL_REJECTED")


if __name__ == "__main__":
    unittest.main()
