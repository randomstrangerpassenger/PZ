from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .repository_context import require_repository_context


V2_ROOT = require_repository_context().description_v2_root
REPOSITORY_ROOT = require_repository_context().repository_root

SCHEMA_VERSION = "dvf-3-3-complete-generation-v1"
GENERATOR_CONTRACT_VERSION = "dvf-3-3-stateless-generation-contract-v1"
RUNTIME_PUBLIC_CONTRACT_VERSION = "iris-layer3-data-public-facade-v2"
RUNTIME_GENERATION_ROOT_MODULE = "Iris/Data/IrisLayer3Generations"
DEFAULT_CHUNK_SIZE = 200
DESCRIPTOR_NAME = "generation_descriptor.json"
RENDERED_NAME = "dvf_3_3_rendered.json"
RUNTIME_MANIFEST_NAME = "runtime/IrisLayer3DataCurrent.lua"
DETERMINISTIC_GENERATED_AT = "content-derived-generation"

CANONICAL_INPUTS = (
    "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl",
    "Iris/build/description/v2/data/compose_profiles_v2.json",
    "Iris/build/description/v2/data/compose_profile_identity_hint_rules.json",
    "Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json",
    "Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json",
)

GENERATOR_IMPLEMENTATION_FILES = (
    "Iris/build/description/v2/tools/build/dvf_3_3_generation_contract.py",
    "Iris/build/description/v2/tools/build/build_dvf_3_3_complete_generation.py",
    "Iris/build/description/v2/tools/build/compose_layer3_io.py",
    "Iris/build/description/v2/tools/build/compose_layer3_text.py",
    "Iris/build/description/v2/tools/build/compose_layer3_body_profile.py",
    "Iris/build/description/v2/tools/build/compose_layer3_render.py",
    "Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py",
)

PROTECTED_CURRENT_PATHS = (
    "Iris/build/description/v2/output/dvf_3_3_rendered.json",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
    "Iris/media/lua/client/Iris/Data/IrisLayer3Generations",
    "Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json",
)


class GenerationContractError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def write_canonical_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def repository_path(repository_root: Path, relative_path: str) -> Path:
    candidate = (repository_root / relative_path).resolve()
    try:
        candidate.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise GenerationContractError(
            "GENERATION_PATH_ESCAPE",
            f"Repository-relative path escapes the repository: {relative_path}",
        ) from exc
    return candidate


def ordered_file_identity(
    repository_root: Path,
    relative_paths: Iterable[str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relative_path in relative_paths:
        path = repository_path(repository_root, relative_path)
        if not path.is_file():
            raise GenerationContractError(
                "GENERATION_REQUIRED_FILE_MISSING",
                relative_path,
            )
        records.append(
            {
                "path": relative_path.replace("\\", "/"),
                "raw_byte_sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
        )
    return records


def canonical_input_identity(repository_root: Path) -> list[dict[str, Any]]:
    return ordered_file_identity(repository_root, CANONICAL_INPUTS)


def generator_identity(repository_root: Path) -> dict[str, Any]:
    return {
        "contract_version": GENERATOR_CONTRACT_VERSION,
        "implementation_files": ordered_file_identity(
            repository_root,
            GENERATOR_IMPLEMENTATION_FILES,
        ),
        "serializer": "utf-8-json-sort-keys-compact-lf-v1",
        "chunking": {
            "algorithm": "ordinal-exact-key-sort-fixed-size-v1",
            "chunk_size": DEFAULT_CHUNK_SIZE,
        },
    }


def generation_seed(
    canonical_inputs: list[dict[str, Any]],
    generator: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "canonical_inputs": canonical_inputs,
        "generator": generator,
        "runtime_public_contract_version": RUNTIME_PUBLIC_CONTRACT_VERSION,
    }


def derive_generation_id(
    canonical_inputs: list[dict[str, Any]],
    generator: dict[str, Any],
) -> str:
    digest = sha256_bytes(canonical_json_bytes(generation_seed(canonical_inputs, generator)))
    return f"dvf33-{digest}"


def generation_module_prefix(generation_id: str) -> str:
    return f"{RUNTIME_GENERATION_ROOT_MODULE}/{generation_id}/Chunks"


def generation_chunk_relative_root(generation_id: str) -> str:
    return f"runtime/IrisLayer3Generations/{generation_id}/Chunks"


def media_type_for(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {
        ".json": "application/json",
        ".jsonl": "application/x-ndjson",
        ".lua": "text/x-lua",
    }.get(suffix, "application/octet-stream")


def output_records(generation_root: Path) -> list[dict[str, Any]]:
    paths = sorted(
        path
        for path in generation_root.rglob("*")
        if path.is_file() and path.name != DESCRIPTOR_NAME
    )
    return [
        {
            "path": path.relative_to(generation_root).as_posix(),
            "media_type": media_type_for(path.name),
            "raw_byte_sha256": sha256_file(path),
            "size": path.stat().st_size,
        }
        for path in paths
    ]


def output_universe_sha256(outputs: list[dict[str, Any]]) -> str:
    return sha256_bytes(canonical_json_bytes(outputs))


def ensure_external_generation_root(
    repository_root: Path,
    generation_root: Path,
) -> Path:
    repository = repository_root.resolve()
    target = generation_root.resolve()
    try:
        target.relative_to(repository)
    except ValueError:
        pass
    else:
        raise GenerationContractError(
            "GENERATION_OUTPUT_ROOT_NOT_EXTERNAL",
            str(target),
        )
    for relative in PROTECTED_CURRENT_PATHS:
        protected = repository_path(repository, relative)
        try:
            target.relative_to(protected)
        except ValueError:
            try:
                protected.relative_to(target)
            except ValueError:
                continue
        raise GenerationContractError(
            "GENERATION_OUTPUT_OVERLAPS_PROTECTED_CURRENT",
            f"{target} <-> {protected}",
        )
    return target
