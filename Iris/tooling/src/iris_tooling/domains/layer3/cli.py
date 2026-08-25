from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    from iris_tooling.build.compose_layer3_text import main as compose

    return compose(list(argv or ()))
