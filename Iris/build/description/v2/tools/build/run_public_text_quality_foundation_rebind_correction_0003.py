from __future__ import annotations

import argparse
import json
import sys

from public_text_quality_foundation_rebind_correction_0003 import (
    FoundationRebindError,
    build_rebind,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the append-only correction-0003 G4 current-input readiness "
            "successor using the established Foundation rebind contract."
        )
    )
    parser.add_argument("--rebind-id", required=True)
    parser.add_argument(
        "--mode",
        required=True,
        choices=("readiness-successor-build",),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = build_rebind(args.rebind_id)
    except FoundationRebindError as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
