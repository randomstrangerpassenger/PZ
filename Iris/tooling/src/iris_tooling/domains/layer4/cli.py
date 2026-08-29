from __future__ import annotations

from collections.abc import Sequence
import sys


def main(argv: Sequence[str] | None = None) -> int:
    values = list(argv or ())
    if values[:1] == ["tooltip-t1-d4"]:
        from .tooltip_t1_d4 import main as d4

        return d4(values[1:])
    from iris_tooling.build.export_dvf_3_3_lua_bridge import main as export

    previous = sys.argv
    sys.argv = ["iris-tooling layer4", *values]
    try:
        return export()
    finally:
        sys.argv = previous
