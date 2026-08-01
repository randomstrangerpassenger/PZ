from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from iar_public_text_assessment import (
    AssessmentFailure,
    DEFAULT_CONTRACT_PATH,
    execution_error_payload,
    materialize_assessment,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one attempt-independent IAR public-text assessment."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = materialize_assessment(
            args.input.resolve(),
            args.output.resolve(),
            contract_path=args.contract.resolve(),
        )
    except AssessmentFailure as exc:
        print(
            json.dumps(execution_error_payload(exc), ensure_ascii=False, sort_keys=True),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PASS" else 5


if __name__ == "__main__":
    raise SystemExit(main())
