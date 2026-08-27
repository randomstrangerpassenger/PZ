from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections.abc import Sequence
import sys

from iris_tooling.build.repository_context import require_repository_context

from .audit import finalize_closeout, run_candidate
from .models import TooltipContractError


def main(argv: Sequence[str] | None = None) -> int:
    values = list(sys.argv[1:] if argv is None else argv)
    if values[:1] == ["finalize"]:
        parser = argparse.ArgumentParser(prog="iris-tooling finalize tooltip-t1")
        parser.add_argument("--candidate-root", type=Path, required=True)
        parser.add_argument("--candidate-run-receipt-sha256", required=True)
        parser.add_argument("--run-a-orchestration-receipt", type=Path, required=True)
        parser.add_argument("--run-b-orchestration-receipt", type=Path, required=True)
        parser.add_argument("--comparator-receipt", type=Path, required=True)
        parser.add_argument("--output-root", type=Path, required=True)
        args = parser.parse_args(values[1:])
        try:
            result = finalize_closeout(
                require_repository_context().repository_root,
                args.candidate_root,
                args.candidate_run_receipt_sha256,
                args.run_a_orchestration_receipt,
                args.run_b_orchestration_receipt,
                args.comparator_receipt,
                args.output_root,
            )
        except (OSError, TooltipContractError) as exc:
            print(f"tooltip-t1 finalization blocked: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    parser = argparse.ArgumentParser(prog="iris-tooling build tooltip-t1")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--decision-contract-sha256", required=True)
    parser.add_argument("--verify-invariants", action="store_true", required=True)
    args = parser.parse_args(values)
    try:
        result = run_candidate(
            require_repository_context().repository_root,
            args.output_root,
            args.decision_contract_sha256,
            verify_selection_invariants=args.verify_invariants,
        )
    except (OSError, TooltipContractError) as exc:
        print(f"tooltip-t1 blocked: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0
