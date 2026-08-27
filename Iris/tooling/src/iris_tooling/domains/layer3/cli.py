from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    values = list(argv or ())
    if values == ["publish-tooltip-t1-owner"]:
        from iris_tooling.build.build_layer3_english_localization import main as publish

        return publish()
    from iris_tooling.build.compose_layer3_text import main as compose

    return compose(values)
