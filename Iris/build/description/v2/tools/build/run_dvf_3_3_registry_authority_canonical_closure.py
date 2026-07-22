from __future__ import annotations

import argparse
import json
import sys

from dvf_3_3_registry_authority_canonical_closure import (
    ALL_RUNNER_MODES,
    CYCLE_ID,
    IMPLEMENTED_RUNNER_MODES,
    ROUND_ID,
    materialize_preimplementation_reviews,
    record_attempt_failure_once,
    run_implementation,
    run_preflight,
)


NOT_IMPLEMENTED_EXIT = 3


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "Registry Authority Canonical Closure write-once attempt runner. "
            "Implemented modes cover Entry, byte-identical Phase 3 review "
            "materialization, and WP-1 through WP-7 implementation evidence."
        )
    )
    value.add_argument("--mode", required=True, choices=ALL_RUNNER_MODES)
    value.add_argument("--attempt-id", required=True)
    value.add_argument("--evidence-root")
    return value


def emit(payload: dict[str, object], *, stream: object = sys.stdout) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=stream)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.mode not in IMPLEMENTED_RUNNER_MODES:
        emit(
            {
                "round_id": ROUND_ID,
                "cycle_id": CYCLE_ID,
                "attempt_id": args.attempt_id,
                "mode": args.mode,
                "status": "not_implemented",
                "exit_code": NOT_IMPLEMENTED_EXIT,
                "evidence_written": False,
                "wp_execution_allowed": False,
                "gate_adoption_allowed": False,
                "finalization_allowed": False,
                "owner_or_reviewer_verdict_authored": False,
            },
            stream=sys.stderr,
        )
        return NOT_IMPLEMENTED_EXIT

    try:
        if args.mode == "preflight":
            result = run_preflight(args.evidence_root, attempt_id=args.attempt_id)
        elif args.mode == "materialize-preimplementation-reviews":
            result = materialize_preimplementation_reviews(
                args.evidence_root, attempt_id=args.attempt_id
            )
        else:
            result = run_implementation(
                args.evidence_root, attempt_id=args.attempt_id
            )
    except Exception as exc:  # fail closed before any positive claim
        try:
            failure_record = record_attempt_failure_once(
                args.evidence_root,
                attempt_id=args.attempt_id,
                mode=args.mode,
                error_type=type(exc).__name__,
                error=str(exc),
            )
        except Exception as failure_record_exc:
            failure_record = {
                "written": False,
                "reason": "failure_record_unavailable",
                "error_type": type(failure_record_exc).__name__,
                "error": str(failure_record_exc),
            }
        emit(
            {
                "round_id": ROUND_ID,
                "cycle_id": CYCLE_ID,
                "attempt_id": args.attempt_id,
                "mode": args.mode,
                "status": "FAIL",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "failure_record": failure_record,
                "wp_execution_allowed": False,
                "owner_or_reviewer_verdict_authored": False,
            },
            stream=sys.stderr,
        )
        return 2

    emit(result)
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
