"""Shared JSON/text I/O helpers for Iris build scripts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(
    path: Path,
    data: Any,
    *,
    indent: int | None = 2,
    sort_keys: bool = False,
    trailing_newline: bool = True,
) -> None:
    """Write a UTF-8 JSON file with Iris build defaults."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(
        data,
        ensure_ascii=False,
        indent=indent,
        sort_keys=sort_keys,
    )
    if trailing_newline:
        text += "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
