from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build import dvf_3_3_registry_runtime_compatibility as legacy_pure
    from tools.build.dvf_3_3_generation_contract import (
        RENDERED_NAME,
        RUNTIME_MANIFEST_NAME,
    )
    from tools.build.export_dvf_3_3_lua_bridge import with_runtime_aliases
else:
    from . import dvf_3_3_registry_runtime_compatibility as legacy_pure
    from .dvf_3_3_generation_contract import RENDERED_NAME, RUNTIME_MANIFEST_NAME
    from .export_dvf_3_3_lua_bridge import with_runtime_aliases


class RuntimeCompatibilityError(RuntimeError):
    def __init__(self, code: str, details: Any = None):
        message = code if details is None else f"{code}: {details}"
        super().__init__(message)
        self.code = code
        self.details = details


def _record_map(records: Sequence[Any]) -> dict[str, dict[str, Any]]:
    return {record.decoded_key: record.payload for record in records}


def validate_generation_runtime_compatibility(
    *,
    generation_root: Path,
) -> dict[str, Any]:
    generation_root = generation_root.resolve()
    descriptor = json.loads(
        (generation_root / "generation_descriptor.json").read_text(encoding="utf-8")
    )
    generation_id = descriptor.get("generation_id")
    if not isinstance(generation_id, str) or not generation_id:
        raise RuntimeCompatibilityError("GENERATION_ID_MISSING")

    rendered_path = generation_root / RENDERED_NAME
    manifest_path = generation_root / RUNTIME_MANIFEST_NAME
    chunk_dir = (
        generation_root
        / "runtime"
        / "IrisLayer3Generations"
        / generation_id
        / "Chunks"
    )
    rendered_records = legacy_pure.load_rendered_surface(
        rendered_path,
        repo=generation_root,
    )
    runtime_records, runtime_meta = legacy_pure.load_lua_surface(
        surface="runtime",
        manifest_path=manifest_path,
        chunk_dir=chunk_dir,
        repo=generation_root,
        manifest_module_re=re.compile(
            rf'"(?P<module>Iris/Data/IrisLayer3Generations/{re.escape(generation_id)}/Chunks/Chunk\d{{3}})"'
        ),
    )
    rendered_duplicates = legacy_pure.exact_duplicates(rendered_records)
    runtime_duplicates = legacy_pure.exact_duplicates(runtime_records)
    if rendered_duplicates:
        raise RuntimeCompatibilityError(
            "RENDERED_EXACT_KEY_DUPLICATE",
            rendered_duplicates,
        )
    if runtime_duplicates:
        raise RuntimeCompatibilityError(
            "RUNTIME_EXACT_KEY_DUPLICATE",
            runtime_duplicates,
        )

    rendered_map = _record_map(rendered_records)
    runtime_map = _record_map(runtime_records)
    expected_runtime_map, applied_aliases = with_runtime_aliases(rendered_map)
    expected_keys = set(expected_runtime_map)
    runtime_keys = set(runtime_map)
    if expected_keys != runtime_keys:
        raise RuntimeCompatibilityError(
            "RUNTIME_EXACT_KEY_UNIVERSE_MISMATCH",
            {
                "missing": sorted(expected_keys - runtime_keys),
                "extra": sorted(runtime_keys - expected_keys),
            },
        )

    mismatches: list[dict[str, str]] = []
    for key in sorted(expected_keys):
        expected = legacy_pure.runtime_projection(expected_runtime_map[key])
        actual = legacy_pure.runtime_projection(runtime_map[key])
        if expected != actual:
            mismatches.append(
                {
                    "full_type": key,
                    "expected_sha256": legacy_pure.payload_hash(expected),
                    "actual_sha256": legacy_pure.payload_hash(actual),
                }
            )
    if mismatches:
        raise RuntimeCompatibilityError(
            "RUNTIME_PAYLOAD_PROJECTION_MISMATCH",
            mismatches,
        )

    collision_groups = legacy_pure.collision_groups(runtime_records)
    return {
        "schema_version": "dvf-3-3-generation-key-identity-validation-v1",
        "generation_id": generation_id,
        "generation_key_identity_validation": "PASS",
        "rendered_exact_key_count": len(rendered_map),
        "runtime_exact_key_count": len(runtime_map),
        "runtime_projection_compared_key_count": len(expected_keys),
        "runtime_projection_payload_mismatch_count": 0,
        "exact_duplicate_count": 0,
        "ascii_lower_collision_group_count": len(collision_groups),
        "ascii_lower_collision_groups": collision_groups,
        "applied_runtime_aliases": applied_aliases,
        "runtime_manifest": runtime_meta,
        "claims": {
            "registry_runtime_compatibility": "not_claimed",
            "rtc": "not_claimed",
            "authority_effect": "none",
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generation-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = validate_generation_runtime_compatibility(
        generation_root=args.generation_root
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
