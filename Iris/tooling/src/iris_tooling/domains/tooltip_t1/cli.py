from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections.abc import Sequence
import sys

from iris_tooling.build.repository_context import require_repository_context

from .audit import finalize_closeout, run_candidate
from .d2 import finalize_bundle as finalize_d2_bundle, materialize as materialize_d2
from .d5 import run_census, run_reconcile
from .models import TooltipContractError


def main(argv: Sequence[str] | None = None) -> int:
    values = list(sys.argv[1:] if argv is None else argv)
    if values[:1] == ["d2-materialize"]:
        parser = argparse.ArgumentParser(prog="iris-tooling build tooltip-t1 d2-materialize")
        parser.add_argument("--output-root", type=Path, required=True)
        parser.add_argument("--run-a-root", type=Path)
        parser.add_argument("--baseline-audit-root", type=Path)
        parser.add_argument("--candidate-audit-root", type=Path)
        parser.add_argument("--bundle-root", type=Path)
        parser.add_argument("--focused-tooltip-exit-code", type=int)
        parser.add_argument("--browser-harness-exit-code", type=int)
        parser.add_argument("--lua-syntax-exit-code", type=int)
        parser.add_argument("--git-diff-check-exit-code", type=int)
        args = parser.parse_args(values[1:])
        try:
            repository_root = require_repository_context().repository_root
            result: dict[str, object] = {"relation": materialize_d2(repository_root, args.output_root)}
            bundle_values = (
                args.run_a_root,
                args.baseline_audit_root,
                args.candidate_audit_root,
                args.bundle_root,
                args.focused_tooltip_exit_code,
                args.browser_harness_exit_code,
                args.lua_syntax_exit_code,
                args.git_diff_check_exit_code,
            )
            if any(value is not None for value in bundle_values):
                if not all(value is not None for value in bundle_values):
                    raise TooltipContractError("D2 bundle finalization arguments are incomplete")
                result["bundle"] = finalize_d2_bundle(
                    repository_root,
                    args.run_a_root,
                    args.output_root,
                    args.baseline_audit_root,
                    args.candidate_audit_root,
                    args.bundle_root,
                    {
                        "focused_tooltip_exit_code": args.focused_tooltip_exit_code,
                        "browser_harness_exit_code": args.browser_harness_exit_code,
                        "lua_syntax_exit_code": args.lua_syntax_exit_code,
                        "git_diff_check_exit_code": args.git_diff_check_exit_code,
                    },
                )
        except (OSError, TooltipContractError, json.JSONDecodeError) as exc:
            print(f"tooltip-t1 D2 materialization blocked: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    if values[:1] == ["d5-census"]:
        parser = argparse.ArgumentParser(prog="iris-tooling build tooltip-t1 d5-census")
        parser.add_argument("--output-root", type=Path, required=True)
        args = parser.parse_args(values[1:])
        try:
            result = run_census(require_repository_context().repository_root, args.output_root)
        except (OSError, TooltipContractError) as exc:
            print(f"tooltip-t1 D5 census blocked: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    if values[:1] == ["d5-reconcile"]:
        parser = argparse.ArgumentParser(prog="iris-tooling build tooltip-t1 d5-reconcile")
        parser.add_argument("--before-root", type=Path, required=True)
        parser.add_argument("--after-root", type=Path, required=True)
        parser.add_argument("--after-run-b-root", type=Path)
        parser.add_argument("--disposition", type=Path, required=True)
        parser.add_argument("--focused-validation-receipt", type=Path)
        parser.add_argument("--output-root", type=Path, required=True)
        args = parser.parse_args(values[1:])
        try:
            result = run_reconcile(
                require_repository_context().repository_root,
                args.before_root,
                args.after_root,
                args.disposition,
                args.output_root,
                after_run_b_root=args.after_run_b_root,
                focused_validation_receipt=args.focused_validation_receipt,
            )
        except (OSError, TooltipContractError, json.JSONDecodeError) as exc:
            print(f"tooltip-t1 D5 reconciliation blocked: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
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
    parser.add_argument("--layer2-menu-relation", type=Path)
    args = parser.parse_args(values)
    try:
        result = run_candidate(
            require_repository_context().repository_root,
            args.output_root,
            args.decision_contract_sha256,
            verify_selection_invariants=args.verify_invariants,
            layer2_menu_relation=args.layer2_menu_relation,
        )
    except (OSError, TooltipContractError) as exc:
        print(f"tooltip-t1 blocked: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0
