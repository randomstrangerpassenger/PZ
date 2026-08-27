from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from iris_tooling.execution import PhaseRunner


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def output_root(*, repository_root: Path) -> Path:
    raw = os.environ.get("IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT")
    if not raw:
        raise ValueError(
            "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT is required; "
            "repository-local output fallback is unsupported"
        )
    candidate = Path(raw)
    if not candidate.is_absolute():
        raise ValueError("IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT must be absolute")
    resolved = candidate.resolve()
    repository = repository_root.resolve()
    if resolved == repository or repository in resolved.parents:
        raise ValueError("right-click output override must be outside the repository")
    return resolved


def pipeline_banner(title: str, width: int = 60) -> None:
    bar = "=" * width
    print(bar)
    print(f"  {title}")
    print(bar)


class StageRunner(PhaseRunner):
    """Right-click I/O adapter over the shared thin phase runner."""

    def save_json(
        self,
        path: Path,
        data: Any,
        *,
        indent: int | None = 2,
        trailing_newline: bool = False,
        on_saved: Callable[[Path], None] | None = None,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(data, ensure_ascii=False, indent=indent)
        if trailing_newline:
            text += "\n"
        path.write_text(text, encoding="utf-8", newline="\n")
        if on_saved:
            on_saved(path)
