from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build.dvf_3_3_generation_contract import (
        DESCRIPTOR_NAME,
        RUNTIME_MANIFEST_NAME,
        RUNTIME_PUBLIC_CONTRACT_VERSION,
        SCHEMA_VERSION,
        canonical_input_identity,
        canonical_json_bytes,
        derive_generation_id,
        ensure_external_generation_root,
        generation_module_prefix,
        generator_identity,
        output_universe_sha256,
        sha256_file,
    )
    from tools.build.dvf_3_3_runtime_compatibility import (
        RuntimeCompatibilityError,
        validate_generation_runtime_compatibility,
    )
    from tools.build.export_dvf_3_3_lua_bridge import parse_chunk_manifest_modules
else:
    from .dvf_3_3_generation_contract import (
        DESCRIPTOR_NAME,
        RUNTIME_MANIFEST_NAME,
        RUNTIME_PUBLIC_CONTRACT_VERSION,
        SCHEMA_VERSION,
        canonical_input_identity,
        canonical_json_bytes,
        derive_generation_id,
        ensure_external_generation_root,
        generation_module_prefix,
        generator_identity,
        output_universe_sha256,
        sha256_file,
    )
    from .dvf_3_3_runtime_compatibility import (
        RuntimeCompatibilityError,
        validate_generation_runtime_compatibility,
    )
    from .export_dvf_3_3_lua_bridge import parse_chunk_manifest_modules


DESCRIPTOR_FIELDS = {
    "schema_version",
    "generation_id",
    "canonical_inputs",
    "generator",
    "runtime_public_contract",
    "outputs",
    "output_universe_sha256",
    "claims",
}
OUTPUT_FIELDS = {"path", "media_type", "raw_byte_sha256", "size"}


class CompleteGenerationValidationError(RuntimeError):
    def __init__(self, code: str, details: Any = None):
        message = code if details is None else f"{code}: {details}"
        super().__init__(message)
        self.code = code
        self.details = details


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CompleteGenerationValidationError(
                "DESCRIPTOR_DUPLICATE_FIELD",
                key,
            )
        result[key] = value
    return result


def _load_descriptor(path: Path) -> dict[str, Any]:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_no_duplicate_object,
        )
    except UnicodeDecodeError as exc:
        raise CompleteGenerationValidationError(
            "DESCRIPTOR_UTF8_INVALID",
            str(exc),
        ) from exc
    except json.JSONDecodeError as exc:
        raise CompleteGenerationValidationError(
            "DESCRIPTOR_JSON_INVALID",
            str(exc),
        ) from exc


def _contained(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise CompleteGenerationValidationError(
            "DESCRIPTOR_OUTPUT_PATH_INVALID",
            relative,
        )
    path = (root / candidate).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise CompleteGenerationValidationError(
            "DESCRIPTOR_OUTPUT_PATH_ESCAPE",
            relative,
        ) from exc
    return path


def validate_complete_generation(
    *,
    repository_root: Path,
    generation_root: Path,
    require_external: bool = True,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    generation_root = generation_root.resolve()
    if require_external:
        ensure_external_generation_root(repository_root, generation_root)
    descriptor_path = generation_root / DESCRIPTOR_NAME
    if not descriptor_path.is_file():
        raise CompleteGenerationValidationError("DESCRIPTOR_MISSING")
    descriptor = _load_descriptor(descriptor_path)
    if set(descriptor) != DESCRIPTOR_FIELDS:
        raise CompleteGenerationValidationError(
            "DESCRIPTOR_FIELD_SET_INVALID",
            {
                "missing": sorted(DESCRIPTOR_FIELDS - set(descriptor)),
                "extra": sorted(set(descriptor) - DESCRIPTOR_FIELDS),
            },
        )
    if descriptor["schema_version"] != SCHEMA_VERSION:
        raise CompleteGenerationValidationError("DESCRIPTOR_SCHEMA_INVALID")

    expected_inputs = canonical_input_identity(repository_root)
    if descriptor["canonical_inputs"] != expected_inputs:
        raise CompleteGenerationValidationError("CANONICAL_INPUT_IDENTITY_MISMATCH")
    expected_generator = generator_identity(repository_root)
    if descriptor["generator"] != expected_generator:
        raise CompleteGenerationValidationError("GENERATOR_IDENTITY_MISMATCH")
    expected_generation_id = derive_generation_id(expected_inputs, expected_generator)
    if descriptor["generation_id"] != expected_generation_id:
        raise CompleteGenerationValidationError("GENERATION_ID_MISMATCH")

    runtime_contract = descriptor["runtime_public_contract"]
    if runtime_contract.get("version") != RUNTIME_PUBLIC_CONTRACT_VERSION:
        raise CompleteGenerationValidationError("RUNTIME_PUBLIC_CONTRACT_MISMATCH")
    if runtime_contract.get("generation_module_prefix") != generation_module_prefix(
        expected_generation_id
    ):
        raise CompleteGenerationValidationError("RUNTIME_MODULE_PREFIX_MISMATCH")

    outputs = descriptor["outputs"]
    if not isinstance(outputs, list) or not outputs:
        raise CompleteGenerationValidationError("DESCRIPTOR_OUTPUTS_EMPTY")
    output_paths: list[str] = []
    for record in outputs:
        if not isinstance(record, dict) or set(record) != OUTPUT_FIELDS:
            raise CompleteGenerationValidationError("OUTPUT_RECORD_INVALID", record)
        relative = record["path"]
        if relative in output_paths:
            raise CompleteGenerationValidationError("OUTPUT_PATH_DUPLICATE", relative)
        output_paths.append(relative)
        path = _contained(generation_root, relative)
        if not path.is_file():
            raise CompleteGenerationValidationError("OUTPUT_FILE_MISSING", relative)
        if path.stat().st_size != record["size"]:
            raise CompleteGenerationValidationError("OUTPUT_SIZE_MISMATCH", relative)
        if sha256_file(path) != record["raw_byte_sha256"]:
            raise CompleteGenerationValidationError("OUTPUT_RAW_HASH_MISMATCH", relative)

    actual_files = {
        path.relative_to(generation_root).as_posix()
        for path in generation_root.rglob("*")
        if path.is_file()
    }
    expected_files = set(output_paths) | {DESCRIPTOR_NAME}
    if actual_files != expected_files:
        raise CompleteGenerationValidationError(
            "OUTPUT_FILE_UNIVERSE_MISMATCH",
            {
                "missing": sorted(expected_files - actual_files),
                "extra": sorted(actual_files - expected_files),
            },
        )
    if output_universe_sha256(outputs) != descriptor["output_universe_sha256"]:
        raise CompleteGenerationValidationError("OUTPUT_UNIVERSE_HASH_MISMATCH")

    manifest_path = generation_root / RUNTIME_MANIFEST_NAME
    modules = parse_chunk_manifest_modules(manifest_path.read_text(encoding="utf-8"))
    prefix = generation_module_prefix(expected_generation_id) + "/"
    if not modules or any(not module.startswith(prefix) for module in modules):
        raise CompleteGenerationValidationError("RUNTIME_MANIFEST_GENERATION_MIXED")

    try:
        compatibility = validate_generation_runtime_compatibility(
            generation_root=generation_root
        )
    except RuntimeCompatibilityError as exc:
        raise CompleteGenerationValidationError(exc.code, exc.details) from exc

    return {
        "schema_version": "dvf-3-3-complete-generation-validation-v1",
        "status": "PASS",
        "generation_id": expected_generation_id,
        "descriptor_raw_byte_sha256": sha256_file(descriptor_path),
        "descriptor_canonical_bytes": descriptor_path.read_bytes()
        == canonical_json_bytes(descriptor),
        "canonical_input_count": len(expected_inputs),
        "output_file_count": len(expected_files),
        "output_universe_sha256": descriptor["output_universe_sha256"],
        "generation_key_identity_validation": compatibility[
            "generation_key_identity_validation"
        ],
        "runtime_compatibility": compatibility,
        "protected_current_mutation_count": 0,
        "claims": {
            "rtc": "not_claimed",
            "authority_effect": "none",
            "publish": "not_claimed",
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generation-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--allow-repository-generation-root", action="store_true")
    args = parser.parse_args(argv)
    report = validate_complete_generation(
        repository_root=args.repository_root,
        generation_root=args.generation_root,
        require_external=not args.allow_repository_generation_root,
    )
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
