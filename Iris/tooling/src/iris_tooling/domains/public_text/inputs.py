from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PublicTextInputError(ValueError):
    """Raised when a strict public-text input cannot be decoded."""


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PublicTextInputError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_bytes(raw: bytes, *, label: str) -> Any:
    try:
        return json.loads(
            raw.decode("utf-8-sig"), object_pairs_hook=_reject_duplicates
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PublicTextInputError(f"cannot read strict JSON: {label}") from exc


def load_json(path: Path) -> Any:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PublicTextInputError(f"cannot read strict JSON: {path}") from exc
    return load_json_bytes(raw, label=str(path))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        raise PublicTextInputError(f"cannot read strict JSONL: {path}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            continue
        try:
            value = json.loads(raw_line, object_pairs_hook=_reject_duplicates)
        except json.JSONDecodeError as exc:
            raise PublicTextInputError(
                f"cannot read strict JSONL: {path}:{line_number}"
            ) from exc
        if not isinstance(value, dict):
            raise PublicTextInputError(
                f"JSONL row must be object: {path}:{line_number}"
            )
        rows.append(value)
    return rows
