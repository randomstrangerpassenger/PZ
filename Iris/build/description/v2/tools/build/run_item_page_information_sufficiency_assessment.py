from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

V2_ROOT = Path(__file__).resolve().parents[2]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.item_page_information_sufficiency import (
    AssessmentFailure,
    DEFAULT_CONTRACT_PATH,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_RATIFICATION_PATH,
    build_assessment,
    error_payload,
    write_bundle,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the read-only Iris item-page information-sufficiency assessment.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--ratification-contract", type=Path, default=DEFAULT_RATIFICATION_PATH)
    parser.add_argument("--require-ratified-policy", action="store_true", required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        bundle = build_assessment(
            args.contract.resolve(),
            args.ratification_contract.resolve(),
            require_ratified_policy=True,
        )
        write_bundle(bundle, args.output_root.resolve())
        summary = json.loads(bundle["assessment_summary.json"])
    except AssessmentFailure as exc:
        print(json.dumps(error_payload(exc), ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["execution_status"] == "PASS" else 6


if __name__ == "__main__":
    raise SystemExit(main())
