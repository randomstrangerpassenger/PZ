from __future__ import annotations

from iris_tooling.common import serialization

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


class PublicTextEmissionError(RuntimeError):
    """Raised when a write-once output conflicts with existing bytes."""


def canonical_json_bytes(value: Any) -> bytes:
    return serialization.compact_json_bytes(value)


def pretty_json_bytes(value: Any) -> bytes:
    return serialization.pretty_json_bytes(value)


def sha256_bytes(value: bytes) -> str:
    return serialization.raw_sha256(value)


def write_once_or_same(path: Path, payload: bytes) -> str:
    if path.exists():
        if path.read_bytes() != payload:
            raise PublicTextEmissionError(f"write-once conflict: {path}")
        return sha256_bytes(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return sha256_bytes(payload)


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(row) for row in rows)
