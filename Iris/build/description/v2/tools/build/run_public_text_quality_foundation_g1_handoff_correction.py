from __future__ import annotations

import argparse
import json
import sys

from public_text_quality_foundation_g1_handoff_correction import (
    FoundationCorrectionError,
    build_successor,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the append-only G4 Foundation G1 gate and text-constituent "
            "freshness correction readiness successor."
        )
    )
    parser.add_argument("--correction-id", required=True)
    parser.add_argument(
        "--mode",
        required=True,
        choices=("readiness-successor-build",),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = build_successor(args.correction_id)
    except FoundationCorrectionError as exc:
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
