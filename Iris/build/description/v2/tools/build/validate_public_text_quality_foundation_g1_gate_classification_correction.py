from __future__ import annotations

import argparse
import json
import sys

from public_text_quality_foundation_g1_gate_classification_correction import (
    FoundationCorrectionError,
    validate_successor,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--correction-id", required=True)
    parser.add_argument("--require-readiness-successor", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    if not args.require_readiness_successor or not args.no_write:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error": (
                        "validation requires --require-readiness-successor "
                        "and --no-write"
                    ),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    try:
        result = validate_successor(args.correction_id)
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
