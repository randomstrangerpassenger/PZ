from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    from iris_tooling.build.build_iris_fixing_index_data import main as build_fixing
    from iris_tooling.build.build_iris_moveables_index_data import main as build_moveables
    from iris_tooling.build.build_iris_recipe_index_data import main as build_recipe

    if argv:
        raise SystemExit("classification does not accept positional arguments")
    for command in (build_fixing, build_moveables, build_recipe):
        result = command()
        if isinstance(result, int) and result != 0:
            return result
    return 0
