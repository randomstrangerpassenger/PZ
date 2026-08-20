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
    DEFAULT_RATIFICATION_PATH,
    build_assessment,
    error_payload,
    validate_bundle,
    validate_canonical_successor_binding,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="No-write validator for Iris item-page information sufficiency.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--ratification-contract", type=Path, default=DEFAULT_RATIFICATION_PATH)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--compare-result-root", type=Path, required=True)
    parser.add_argument("--require-full-universe", action="store_true", required=True)
    parser.add_argument("--require-matrix-totality", action="store_true", required=True)
    parser.add_argument("--require-derivation-reachability", action="store_true", required=True)
    parser.add_argument("--require-canonical-successor-binding", action="store_true", required=True)
    parser.add_argument("--no-write", action="store_true", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        bundle = build_assessment(
            args.contract.resolve(),
            args.ratification_contract.resolve(),
            require_ratified_policy=True,
        )
        report = validate_bundle(
            bundle,
            args.result_root.resolve(),
            args.compare_result_root.resolve() if args.compare_result_root else None,
        )
        validation = json.loads(bundle["validation_report.json"])
        checks = validation["checks"]
        if args.require_full_universe and not checks["denominator_row_set_equal"]:
            raise AssessmentFailure("validation", "full_universe_validation_failed", "denominator_row_set_equal")
        if args.require_matrix_totality and not checks["matrix_total_function"]:
            raise AssessmentFailure("validation", "matrix_totality_validation_failed", "matrix_total_function")
        if args.require_derivation_reachability and not checks["derivation_level_evidence_limited_reachable"]:
            raise AssessmentFailure("validation", "derivation_reachability_validation_failed", "evidence_limited")
        report["canonical_successor_binding"] = validate_canonical_successor_binding(report["result_sha256"])
    except AssessmentFailure as exc:
        print(json.dumps(error_payload(exc), ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 6


if __name__ == "__main__":
    raise SystemExit(main())
