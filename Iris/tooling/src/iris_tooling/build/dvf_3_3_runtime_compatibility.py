from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence

if __package__ in {None, ""}:
    from iris_tooling.build.dvf_3_3_generation_contract import (
        RENDERED_NAME,
        RUNTIME_MANIFEST_NAME,
        sha256_file,
    )
    from iris_tooling.build.export_dvf_3_3_lua_bridge import with_runtime_aliases
else:
    from .dvf_3_3_generation_contract import (
        RENDERED_NAME,
        RUNTIME_MANIFEST_NAME,
        sha256_file,
    )
    from .export_dvf_3_3_lua_bridge import with_runtime_aliases


RUNTIME_PAYLOAD_FIELDS = ("source", "text_ko", "publish_state")
LUA_ENTRY_RE = re.compile(
    r'^\s{4}\[(?P<token>"(?:\\.|[^"\\])*")\]\s*=\s*\{\s*$'
)
LUA_FIELD_RE = re.compile(
    r'^\s{8}\["(?P<field>source|text_ko|publish_state)"\]\s*=\s*'
    r'(?P<token>"(?:\\.|[^"\\])*")\s*,\s*$'
)


class _ObjectPairs(list[tuple[str, Any]]):
    pass


class RuntimeCompatibilityError(RuntimeError):
    def __init__(self, code: str, details: Any = None):
        message = code if details is None else f"{code}: {details}"
        super().__init__(message)
        self.code = code
        self.details = details


def _pairs_to_value(value: Any) -> Any:
    if isinstance(value, _ObjectPairs):
        return {key: _pairs_to_value(member) for key, member in value}
    if isinstance(value, list):
        return [_pairs_to_value(member) for member in value]
    return value


def _load_rendered_records(path: Path) -> list[tuple[str, dict[str, Any]]]:
    try:
        document = json.loads(
            path.read_bytes().decode("utf-8"),
            object_pairs_hook=_ObjectPairs,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeCompatibilityError("RENDERED_JSON_INVALID", str(exc)) from exc
    if not isinstance(document, _ObjectPairs):
        raise RuntimeCompatibilityError("RENDERED_ROOT_INVALID")
    entries_values = [value for key, value in document if key == "entries"]
    if len(entries_values) != 1 or not isinstance(entries_values[0], _ObjectPairs):
        raise RuntimeCompatibilityError("RENDERED_ENTRIES_INVALID")
    records: list[tuple[str, dict[str, Any]]] = []
    for key, payload in entries_values[0]:
        converted = _pairs_to_value(payload)
        if not isinstance(key, str) or not isinstance(converted, dict):
            raise RuntimeCompatibilityError("RENDERED_ENTRY_INVALID", key)
        records.append((key, converted))
    return records


def _decode_lua_string(token: str) -> str:
    if len(token) < 2 or token[0] != '"' or token[-1] != '"':
        raise RuntimeCompatibilityError("LUA_STRING_TOKEN_INVALID", token)
    output = bytearray()
    simple = {
        "a": 0x07,
        "b": 0x08,
        "f": 0x0C,
        "n": 0x0A,
        "r": 0x0D,
        "t": 0x09,
        "v": 0x0B,
        "\\": 0x5C,
        '"': 0x22,
        "'": 0x27,
    }
    index = 1
    while index < len(token) - 1:
        character = token[index]
        if character != "\\":
            output.extend(character.encode("utf-8"))
            index += 1
            continue
        index += 1
        if index >= len(token) - 1:
            raise RuntimeCompatibilityError("LUA_STRING_ESCAPE_TRUNCATED", token)
        escaped = token[index]
        if escaped in simple:
            output.append(simple[escaped])
            index += 1
            continue
        if escaped.isdigit():
            end = index
            while end < min(index + 3, len(token) - 1) and token[end].isdigit():
                end += 1
            value = int(token[index:end], 10)
            if value > 255:
                raise RuntimeCompatibilityError("LUA_DECIMAL_ESCAPE_OUT_OF_RANGE", token)
            output.append(value)
            index = end
            continue
        if escaped == "x":
            digits = token[index + 1 : index + 3]
            if len(digits) != 2 or not all(
                character in "0123456789abcdefABCDEF" for character in digits
            ):
                raise RuntimeCompatibilityError("LUA_HEX_ESCAPE_INVALID", token)
            output.append(int(digits, 16))
            index += 3
            continue
        raise RuntimeCompatibilityError("LUA_ESCAPE_UNSUPPORTED", escaped)
    try:
        return output.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeCompatibilityError("LUA_STRING_UTF8_INVALID", token) from exc


def _load_runtime_records(
    *,
    generation_root: Path,
    manifest_path: Path,
    chunk_dir: Path,
    generation_id: str,
) -> tuple[list[tuple[str, dict[str, Any]]], dict[str, Any]]:
    module_re = re.compile(
        rf'"(?P<module>Iris/Data/IrisLayer3Generations/{re.escape(generation_id)}/Chunks/Chunk\d{{3}})"'
    )
    modules = module_re.findall(manifest_path.read_text(encoding="utf-8"))
    if not modules:
        raise RuntimeCompatibilityError("RUNTIME_MANIFEST_EMPTY")
    chunk_paths = [chunk_dir / f"{module.rsplit('/', 1)[-1]}.lua" for module in modules]
    missing = [path.as_posix() for path in chunk_paths if not path.is_file()]
    if missing:
        raise RuntimeCompatibilityError("RUNTIME_CHUNK_MISSING", missing)

    records: list[tuple[str, dict[str, Any]]] = []
    for chunk_path in chunk_paths:
        current_key: str | None = None
        current_payload: dict[str, Any] = {}
        for line_number, line in enumerate(
            chunk_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            entry_match = LUA_ENTRY_RE.match(line)
            if entry_match:
                if current_key is not None:
                    raise RuntimeCompatibilityError(
                        "RUNTIME_ENTRY_NESTED", f"{chunk_path}:{line_number}"
                    )
                current_key = _decode_lua_string(entry_match.group("token"))
                current_payload = {}
                continue
            if current_key is None:
                continue
            field_match = LUA_FIELD_RE.match(line)
            if field_match:
                field = field_match.group("field")
                if field in current_payload:
                    raise RuntimeCompatibilityError(
                        "RUNTIME_PAYLOAD_FIELD_DUPLICATE",
                        f"{chunk_path}:{line_number}:{field}",
                    )
                current_payload[field] = _decode_lua_string(field_match.group("token"))
                continue
            if line.strip() == "},":
                records.append((current_key, current_payload))
                current_key = None
                current_payload = {}
        if current_key is not None:
            raise RuntimeCompatibilityError("RUNTIME_ENTRY_UNCLOSED", chunk_path.as_posix())

    return records, {
        "manifest_path": manifest_path.relative_to(generation_root).as_posix(),
        "manifest_sha256": sha256_file(manifest_path),
        "chunk_count": len(chunk_paths),
        "chunk_paths": [path.relative_to(generation_root).as_posix() for path in chunk_paths],
        "chunk_hashes": [sha256_file(path) for path in chunk_paths],
    }


def _duplicates(records: Sequence[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[int]] = {}
    for ordinal, (key, _) in enumerate(records, start=1):
        grouped.setdefault(key, []).append(ordinal)
    return [
        {"decoded_key": key, "occurrence_count": len(ordinals), "ordinals": ordinals}
        for key, ordinals in sorted(grouped.items())
        if len(ordinals) > 1
    ]


def _record_map(
    records: Sequence[tuple[str, dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    return {key: payload for key, payload in records}


def _runtime_projection(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        field: payload[field]
        for field in RUNTIME_PAYLOAD_FIELDS
        if field in payload and payload[field] is not None
    }


def _payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _ascii_lower(value: str) -> str:
    return value.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))


def _collision_groups(
    records: Sequence[tuple[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    grouped: dict[str, set[str]] = {}
    for key, _ in records:
        grouped.setdefault(_ascii_lower(key), set()).add(key)
    return [
        {"ascii_lower_key": key, "members": sorted(members)}
        for key, members in sorted(grouped.items())
        if len(members) > 1
    ]


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
    rendered_records = _load_rendered_records(rendered_path)
    runtime_records, runtime_meta = _load_runtime_records(
        generation_root=generation_root,
        manifest_path=manifest_path,
        chunk_dir=chunk_dir,
        generation_id=generation_id,
    )
    rendered_duplicates = _duplicates(rendered_records)
    runtime_duplicates = _duplicates(runtime_records)
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
        expected = _runtime_projection(expected_runtime_map[key])
        actual = _runtime_projection(runtime_map[key])
        if expected != actual:
            mismatches.append(
                {
                    "full_type": key,
                    "expected_sha256": _payload_hash(expected),
                    "actual_sha256": _payload_hash(actual),
                }
            )
    if mismatches:
        raise RuntimeCompatibilityError(
            "RUNTIME_PAYLOAD_PROJECTION_MISMATCH",
            mismatches,
        )

    collision_groups = _collision_groups(runtime_records)
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
