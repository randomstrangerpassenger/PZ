from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


JSONL_BYTE_CONTRACT = "unsorted-json-platform-newline-with-trailer"
FILE_HASH_CONTRACT = "sha256-binary-chunks-8192"


def _serialize_jsonl_row(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False)


def _iter_binary_chunks(path: Path):
    with path.open("rb") as handle:
        yield from iter(lambda: handle.read(8192), b"")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_optional_jsonl_map(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    return {entry["item_id"]: entry for entry in load_jsonl(path)}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(_serialize_jsonl_row(row))
            handle.write("\n")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for chunk in _iter_binary_chunks(path):
        digest.update(chunk)
    return digest.hexdigest()


def entries_sha256(entries: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(entries, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
