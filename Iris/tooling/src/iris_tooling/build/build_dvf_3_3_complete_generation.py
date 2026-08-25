from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Sequence

if __package__ in {None, ""}:
    from iris_tooling.build.dvf_3_3_generation_contract import (
        CANONICAL_INPUTS,
        DEFAULT_CHUNK_SIZE,
        DESCRIPTOR_NAME,
        DETERMINISTIC_GENERATED_AT,
        RENDERED_NAME,
        RUNTIME_MANIFEST_NAME,
        RUNTIME_PUBLIC_CONTRACT_VERSION,
        SCHEMA_VERSION,
        canonical_input_identity,
        derive_generation_id,
        ensure_external_generation_root,
        generation_chunk_relative_root,
        generation_module_prefix,
        generator_identity,
        output_records,
        output_universe_sha256,
        repository_path,
        write_canonical_json,
    )
    from iris_tooling.build.export_dvf_3_3_lua_bridge import (
        with_runtime_aliases,
        write_chunked_lua_bridge,
    )
else:
    from .dvf_3_3_generation_contract import (
        CANONICAL_INPUTS,
        DEFAULT_CHUNK_SIZE,
        DESCRIPTOR_NAME,
        DETERMINISTIC_GENERATED_AT,
        RENDERED_NAME,
        RUNTIME_MANIFEST_NAME,
        RUNTIME_PUBLIC_CONTRACT_VERSION,
        SCHEMA_VERSION,
        canonical_input_identity,
        derive_generation_id,
        ensure_external_generation_root,
        generation_chunk_relative_root,
        generation_module_prefix,
        generator_identity,
        output_records,
        output_universe_sha256,
        repository_path,
        write_canonical_json,
    )
    from .export_dvf_3_3_lua_bridge import (
        with_runtime_aliases,
        write_chunked_lua_bridge,
    )


def _stable_pretty_json(path: Path, payload: Any) -> None:
    path.write_bytes(
        json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    )


def _write_runtime_pointer(path: Path, generation_id: str, chunk_count: int) -> None:
    chunk_prefix = generation_module_prefix(generation_id)
    generation_prefix = chunk_prefix.rsplit("/", 1)[0]
    lines = [
        "-- Generated generation pointer. This is the single runtime visibility switch.",
        "return {",
        '    schema_version = "iris_layer3_generation_pointer_v1",',
        f'    generation_id = "{generation_id}",',
        f'    index_module = "{generation_prefix}/IrisLayer3DataChunkIndex",',
        "    chunk_modules = {",
    ]
    lines.extend(
        f'        "{chunk_prefix}/Chunk{ordinal:03d}",'
        for ordinal in range(1, chunk_count + 1)
    )
    lines.extend(["    },", "}", ""])
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _paths(repository_root: Path) -> dict[str, Path]:
    return {
        "facts": repository_path(repository_root, CANONICAL_INPUTS[0]),
        "decisions": repository_path(repository_root, CANONICAL_INPUTS[1]),
        "overlay": repository_path(repository_root, CANONICAL_INPUTS[2]),
        "profiles": repository_path(repository_root, CANONICAL_INPUTS[3]),
        "identity_rules": repository_path(repository_root, CANONICAL_INPUTS[4]),
        "precedence_rules": repository_path(repository_root, CANONICAL_INPUTS[5]),
        "adopted_candidate": repository_path(repository_root, CANONICAL_INPUTS[6]),
    }


def build_complete_generation(
    *,
    repository_root: Path,
    output_root: Path,
    replace: bool = False,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    output_root = ensure_external_generation_root(repository_root, output_root)
    inputs = canonical_input_identity(repository_root)
    generator = generator_identity(repository_root)
    generation_id = derive_generation_id(inputs, generator)

    if output_root.exists() and not output_root.is_dir():
        raise RuntimeError(f"GENERATION_OUTPUT_ROOT_NOT_DIRECTORY: {output_root}")
    if output_root.exists() and not replace:
        descriptor_path = output_root / DESCRIPTOR_NAME
        if descriptor_path.is_file():
            descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
            if descriptor.get("generation_id") == generation_id:
                from iris_tooling.build.validate_dvf_3_3_complete_generation import (
                    validate_complete_generation,
                )

                validation = validate_complete_generation(
                    repository_root=repository_root,
                    generation_root=output_root,
                )
                return {
                    "status": "NOOP_ALREADY_GENERATED",
                    "generation_id": generation_id,
                    "output_root": str(output_root),
                    "protected_current_mutation_count": 0,
                    "validation": validation,
                }
        raise RuntimeError(f"GENERATION_OUTPUT_ROOT_ALREADY_EXISTS: {output_root}")

    output_root.parent.mkdir(parents=True, exist_ok=True)
    temporary_parent = Path(
        tempfile.mkdtemp(prefix=f".{output_root.name}.build-", dir=output_root.parent)
    )
    generation_root = temporary_parent / "generation"
    generation_root.mkdir()
    try:
        paths = _paths(repository_root)
        rendered_path = generation_root / RENDERED_NAME
        rendered = json.loads(paths["adopted_candidate"].read_text(encoding="utf-8"))
        rendered["meta"]["generated_at"] = DETERMINISTIC_GENERATED_AT
        _stable_pretty_json(rendered_path, rendered)

        runtime_entries, _ = with_runtime_aliases(rendered["entries"])
        runtime_manifest = generation_root / RUNTIME_MANIFEST_NAME
        runtime_chunk_root = generation_root / generation_chunk_relative_root(
            generation_id
        )
        write_chunked_lua_bridge(
            entries=runtime_entries,
            chunk_output_dir=runtime_chunk_root,
            chunk_manifest_path=runtime_manifest,
            chunk_size=DEFAULT_CHUNK_SIZE,
            chunk_module_prefix=generation_module_prefix(generation_id),
            bridge_context="historical",
        )
        _write_runtime_pointer(
            runtime_manifest,
            generation_id,
            (len(runtime_entries) + DEFAULT_CHUNK_SIZE - 1) // DEFAULT_CHUNK_SIZE,
        )

        outputs = output_records(generation_root)
        descriptor = {
            "schema_version": SCHEMA_VERSION,
            "generation_id": generation_id,
            "canonical_inputs": inputs,
            "generator": generator,
            "runtime_public_contract": {
                "version": RUNTIME_PUBLIC_CONTRACT_VERSION,
                "public_module": "Iris/Data/IrisLayer3DataChunks",
                "visibility_switch": RUNTIME_MANIFEST_NAME,
                "generation_module_prefix": generation_module_prefix(generation_id),
                "live_reload_supported": False,
            },
            "outputs": outputs,
            "output_universe_sha256": output_universe_sha256(outputs),
            "claims": {
                "generation_key_identity_validation": "requires_stateless_validation",
                "authority_effect": "none",
                "rtc": "not_claimed",
                "publish": "not_claimed",
            },
        }
        write_canonical_json(generation_root / DESCRIPTOR_NAME, descriptor)

        if output_root.exists():
            shutil.rmtree(output_root)
        generation_root.replace(output_root)
        return {
            "status": "BUILT",
            "generation_id": generation_id,
            "output_root": str(output_root),
            "descriptor_path": str(output_root / DESCRIPTOR_NAME),
            "output_file_count": len(outputs) + 1,
            "protected_current_mutation_count": 0,
        }
    finally:
        if temporary_parent.exists():
            shutil.rmtree(temporary_parent)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a deterministic, off-live DVF 3.3 complete generation."
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = build_complete_generation(
        repository_root=args.repository_root,
        output_root=args.output_root,
        replace=args.replace,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
