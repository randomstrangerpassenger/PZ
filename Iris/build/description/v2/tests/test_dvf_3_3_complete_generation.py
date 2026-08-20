from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.build.build_dvf_3_3_complete_generation import build_complete_generation
from tools.build.dvf_3_3_generation_contract import CANONICAL_INPUTS, DESCRIPTOR_NAME, GENERATOR_IMPLEMENTATION_FILES
from tools.build.validate_dvf_3_3_complete_generation import CompleteGenerationValidationError, validate_complete_generation


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]


def copy_generation_inputs(target: Path) -> None:
    for relative in (*CANONICAL_INPUTS, *GENERATOR_IMPLEMENTATION_FILES):
        source = REPOSITORY_ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def file_bytes(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


class DvfCompleteGenerationTest(unittest.TestCase):
    def test_complete_generation_is_path_independent_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-iar-generation-") as temporary:
            root = Path(temporary)
            repository = root / "repository"
            copy_generation_inputs(repository)
            run_a = root / "a" / "generation"
            run_b = root / "long-unicode-경로" / "generation"
            first = build_complete_generation(repository_root=repository, output_root=run_a)
            second = build_complete_generation(repository_root=repository, output_root=run_b)
            self.assertEqual(first["generation_id"], second["generation_id"])
            self.assertEqual(file_bytes(run_a), file_bytes(run_b))
            noop = build_complete_generation(repository_root=repository, output_root=run_a)
            self.assertEqual(noop["status"], "NOOP_ALREADY_GENERATED")
            self.assertEqual(noop["protected_current_mutation_count"], 0)

    def test_descriptor_is_content_identity_not_lifecycle_authority(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-iar-descriptor-") as temporary:
            root = Path(temporary)
            repository = root / "repository"
            copy_generation_inputs(repository)
            generation = root / "generation"
            build_complete_generation(repository_root=repository, output_root=generation)
            descriptor = json.loads((generation / DESCRIPTOR_NAME).read_text(encoding="utf-8"))
            forbidden = {"attempt_id", "transaction_id", "nonce", "receipt_path", "owner_seal", "candidate_path", "generated_at"}
            self.assertTrue(forbidden.isdisjoint(descriptor))
            self.assertEqual(descriptor["claims"]["authority_effect"], "none")

    def test_complete_generation_failure_matrix_fails_closed(self) -> None:
        cases = [
            ("descriptor_field", "DESCRIPTOR_FIELD_SET_INVALID"),
            ("input_hash", "CANONICAL_INPUT_IDENTITY_MISMATCH"),
            ("output_hash", "OUTPUT_RAW_HASH_MISMATCH"),
            ("extra_file", "OUTPUT_FILE_UNIVERSE_MISMATCH"),
            ("missing_file", "OUTPUT_FILE_MISSING"),
            ("chunk_reorder", "OUTPUT_RAW_HASH_MISMATCH"),
        ]
        for mutation, code in cases:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(prefix="iris-iar-negative-") as temporary:
                root = Path(temporary)
                repository = root / "repository"
                copy_generation_inputs(repository)
                generation = root / "generation"
                build_complete_generation(repository_root=repository, output_root=generation)
                descriptor_path = generation / DESCRIPTOR_NAME
                descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
                if mutation == "descriptor_field":
                    descriptor["transaction_id"] = "forbidden"
                    descriptor_path.write_text(json.dumps(descriptor), encoding="utf-8")
                elif mutation == "input_hash":
                    descriptor["canonical_inputs"][0]["raw_byte_sha256"] = "0" * 64
                    descriptor_path.write_text(json.dumps(descriptor), encoding="utf-8")
                elif mutation == "output_hash":
                    target = generation / descriptor["outputs"][0]["path"]
                    target.write_bytes(target.read_bytes() + b"tamper")
                elif mutation == "extra_file":
                    (generation / "extra.lua").write_text("return {}", encoding="utf-8")
                elif mutation == "missing_file":
                    (generation / descriptor["outputs"][0]["path"]).unlink()
                elif mutation == "chunk_reorder":
                    manifest = generation / "runtime" / "IrisLayer3DataChunks.lua"
                    lines = manifest.read_text(encoding="utf-8").splitlines()
                    indexes = [index for index, line in enumerate(lines) if "/Chunks/Chunk" in line]
                    lines[indexes[0]], lines[indexes[1]] = lines[indexes[1]], lines[indexes[0]]
                    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
                with self.assertRaises(CompleteGenerationValidationError) as raised:
                    validate_complete_generation(repository_root=repository, generation_root=generation)
                self.assertEqual(raised.exception.code, code)


if __name__ == "__main__":
    unittest.main()
