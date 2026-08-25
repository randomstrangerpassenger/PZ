from __future__ import annotations

from collections.abc import Sequence
import sys


def main(argv: Sequence[str] | None = None) -> int:
    from iris_tooling.build.export_dvf_3_3_lua_bridge import main as export

    previous = sys.argv
    sys.argv = ["iris-tooling layer4", *list(argv or ())]
    try:
        return export()
    finally:
        sys.argv = previous
