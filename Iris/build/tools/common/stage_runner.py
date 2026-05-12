"""Shared pipeline stage orchestration helpers."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from .io import write_json


T = TypeVar("T")


class StageRunner:
    """Small runner for shared pipeline stage scheduling and status handling."""

    def __init__(self, *, indent: str = "  ") -> None:
        self.indent = indent

    def announce(self, code: str, title: str) -> None:
        """Print a consistent short stage heading."""
        print(f"\n{self.indent}[{code}] {title}...")

    def run(
        self,
        action: Callable[[], T],
        *,
        failed: Callable[[T], bool] | None = None,
        abort_message: str | None = None,
    ) -> tuple[T, bool]:
        """Run one stage action and return ``(result, ok)``."""
        result = action()
        ok = not failed(result) if failed else True
        if not ok and abort_message:
            print(f"\n{abort_message}")
        return result, ok

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
