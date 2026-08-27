"""Shared pipeline stage orchestration helpers."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from iris_tooling.execution import PhaseRunner

from .io import write_json


class StageRunner(PhaseRunner):
    """Small runner for shared pipeline stage scheduling and status handling."""

    def __init__(self, *, indent: str = "  ") -> None:
        super().__init__()
        self.indent = indent

    def announce(self, code: str, title: str) -> None:
        """Print a consistent short stage heading."""
        print(f"\n{self.indent}[{code}] {title}...")

    def save_json(
        self,
        path: Path,
        data: Any,
        *,
        indent: int | None = 2,
        trailing_newline: bool = False,
        on_saved: Callable[[Path], None] | None = None,
    ) -> None:
        """Save one JSON artifact with shared pipeline defaults."""
        write_json(path, data, indent=indent, trailing_newline=trailing_newline)
        if on_saved:
            on_saved(path)
