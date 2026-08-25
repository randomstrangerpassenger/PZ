from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    from iris_tooling.build.run_dvf_3_3_korean_prose_naturalization import (
        main as build_public_text,
    )

    return build_public_text(list(argv or ()))
