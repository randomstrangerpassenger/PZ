from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from iar_public_text_assessment import (
    AssessmentFailure,
    DEFAULT_CONTRACT_PATH,
    execution_error_payload,
    validate_assessment,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only validator for a generic IAR public-text assessment."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--no-write", action="store_true", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = validate_assessment(
            args.input.resolve(),
            args.result.resolve(),
            contract_path=args.contract.resolve(),
        )
    except AssessmentFailure as exc:
        print(
            json.dumps(execution_error_payload(exc), ensure_ascii=False, sort_keys=True),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["assessment_status"] == "PASS" else 5


if __name__ == "__main__":
    raise SystemExit(main())
