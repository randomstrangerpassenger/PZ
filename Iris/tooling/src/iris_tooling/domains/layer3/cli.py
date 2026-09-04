from __future__ import annotations

from collections.abc import Sequence
import json


def main(argv: Sequence[str] | None = None) -> int:
    values = list(argv or ())
    if values[:1] == ["investigate"]:
        from .investigation import main as investigate

        return investigate(values[1:])
    if values[:1] == ["compose-successor"]:
        import argparse
        from pathlib import Path
        from iris_tooling.build.compose_layer3_text import build_shared_successor
        from iris_tooling.build.repository_context import require_repository_context

        parser = argparse.ArgumentParser(prog="iris-tooling build layer3 compose-successor")
        parser.add_argument("--output", type=Path, required=True)
        args = parser.parse_args(values[1:])
        print(json.dumps(build_shared_successor(require_repository_context().repository_root,
                                                args.output), ensure_ascii=False, sort_keys=True))
        return 0
    if values == ["publish-tooltip-t1-owner"]:
        from iris_tooling.build.build_layer3_english_localization import publish_tooltip_t1_owner_only
        from iris_tooling.build.repository_context import require_repository_context

        print(json.dumps(
            publish_tooltip_t1_owner_only(require_repository_context().repository_root),
            ensure_ascii=False,
            sort_keys=True,
        ))
        return 0
    if values[:1] == ["prepare-tooltip-t1-d3"]:
        from .tooltip_t1_d3 import main as d3_main

        return d3_main(["prepare", *values[1:]])
    if values[:1] == ["materialize-tooltip-t1-d3-registry"]:
        from .tooltip_t1_d3 import main as d3_main

        return d3_main(["materialize-registry", *values[1:]])
    if values[:1] == ["validate-tooltip-t1-d3-absence"]:
        from iris_tooling.domains.tooltip_t1.d3_invariance import main as invariance_main

        return invariance_main(["absence", *values[1:]])
    if values[:1] == ["compare-tooltip-t1-d3"]:
        from iris_tooling.domains.tooltip_t1.d3_invariance import main as invariance_main

        return invariance_main(["compare", *values[1:]])
    if values[:1] == ["bundle-tooltip-t1-d3"]:
        from .tooltip_t1_d3 import main as d3_main

        return d3_main(["bundle", *values[1:]])
    from iris_tooling.build.compose_layer3_text import main as compose

    return compose(values)
