from __future__ import annotations

import argparse
import json
import sys

from dvf_3_3_registry_authority_canonical_closure import (
    CYCLE_ID,
    IMPLEMENTED_VALIDATIONS,
    ROUND_ID,
    validate_execution_entry,
    validate_implementation,
    validate_practical_closeout_review,
    validate_practical_final_validation,
    validate_practical_gate_adoption,
    validate_practical_gate_candidate,
    validate_practical_implementation,
    validate_practical_owner_seal,
    validate_practical_preflight,
    validate_practical_review,
    validate_practical_terminal_seal,
    validate_preflight,
    validate_preimplementation_reviews,
)


NOT_IMPLEMENTED_EXIT = 3


ALL_REQUIRE_FLAGS = (
    "require-preimplementation-reviews",
    "require-execution-entry",
    "require-implementation",
    "require-gate-candidate",
    "require-machine-complete",
    "require-independent-review",
    "require-final-inputs",
    "require-top-doc-owner-application",
    "require-post-external",
    "require-terminal-seal",
    "require-practical-preflight",
    "require-practical-review",
    "require-practical-implementation",
    "require-practical-gate-candidate",
    "require-practical-gate-adoption",
    "require-practical-final-validation",
    "require-practical-closeout-review",
    "require-practical-owner-seal",
    "require-practical-terminal-seal",
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "Registry Authority Canonical Closure attempt validator. "
            "Implemented requirements cover Entry, review materialization, "
            "Execution Entry, and WP-1 through WP-7 implementation evidence."
        )
    )
    group = value.add_mutually_exclusive_group(required=True)
    group.add_argument("--require-preflight", action="store_true")
    for flag in ALL_REQUIRE_FLAGS:
        group.add_argument(f"--{flag}", action="store_true")
    value.add_argument("--evidence-root")
    value.add_argument("--attempt-id", required=True)
    value.add_argument("--no-write", action="store_true")
    return value


def emit(payload: dict[str, object], *, stream: object = sys.stdout) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=stream)


def selected_requirement(args: argparse.Namespace) -> str:
    if args.require_preflight:
        return "require-preflight"
    for flag in ALL_REQUIRE_FLAGS:
        if getattr(args, flag.replace("-", "_")):
            return flag
    raise ValueError("no validation requirement selected")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    requirement = selected_requirement(args)
    if requirement not in IMPLEMENTED_VALIDATIONS:
        emit(
            {
                "round_id": ROUND_ID,
                "cycle_id": CYCLE_ID,
                "attempt_id": args.attempt_id,
                "requirement": requirement,
                "status": "not_implemented",
                "exit_code": NOT_IMPLEMENTED_EXIT,
                "evidence_written": False,
                "wp_execution_allowed": False,
                "finalization_allowed": False,
            },
            stream=sys.stderr,
        )
        return NOT_IMPLEMENTED_EXIT

    try:
        if requirement == "require-preflight":
            result = validate_preflight(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-preimplementation-reviews":
            result = validate_preimplementation_reviews(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-execution-entry":
            result = validate_execution_entry(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-implementation":
            if args.attempt_id.endswith("-practical"):
                result = validate_practical_implementation(
                    args.evidence_root, attempt_id=args.attempt_id
                )
            else:
                result = validate_implementation(
                    args.evidence_root, attempt_id=args.attempt_id
                )
        elif requirement == "require-practical-preflight":
            result = validate_practical_preflight(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-practical-review":
            result = validate_practical_review(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-practical-implementation":
            result = validate_practical_implementation(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-practical-gate-candidate":
            result = validate_practical_gate_candidate(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-practical-gate-adoption":
            result = validate_practical_gate_adoption(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-practical-final-validation":
            result = validate_practical_final_validation(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-practical-closeout-review":
            result = validate_practical_closeout_review(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-practical-owner-seal":
            result = validate_practical_owner_seal(
                args.evidence_root, attempt_id=args.attempt_id
            )
        elif requirement == "require-practical-terminal-seal":
            result = validate_practical_terminal_seal(
                args.evidence_root, attempt_id=args.attempt_id
            )
        else:
            result = validate_implementation(
                args.evidence_root, attempt_id=args.attempt_id
            )
    except Exception as exc:
        emit(
            {
                "round_id": ROUND_ID,
                "cycle_id": CYCLE_ID,
                "attempt_id": args.attempt_id,
                "requirement": requirement,
                "status": "FAIL",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "wp_execution_allowed": False,
            },
            stream=sys.stderr,
        )
        return 2
    emit(result)
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
