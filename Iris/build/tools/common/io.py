"""Shared JSON/text I/O helpers for Iris build scripts."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def repository_external_output_root(
    *,
    environment_variable: str,
    default_root: Path,
    repository_root: Path,
) -> Path:
    """Resolve an optional output override without weakening the repo boundary."""
    raw_value = os.environ.get(environment_variable)
    if not raw_value:
        return default_root
    candidate = Path(raw_value)
    if not candidate.is_absolute():
        raise ValueError(
            f"{environment_variable} must be an absolute path"
        )
    resolved_candidate = candidate.resolve()
    resolved_repository = repository_root.resolve()
    if (
        resolved_candidate == resolved_repository
        or resolved_repository in resolved_candidate.parents
    ):
        raise ValueError(
            f"{environment_variable} must be outside the repository"
        )
    return resolved_candidate


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
