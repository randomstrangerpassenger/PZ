from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    from .pipeline_v24 import main as run_v24

    return run_v24(list(argv or ()))
