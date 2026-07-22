from __future__ import annotations

import argparse
import json
import sys

from dvf_3_3_registry_authority_canonical_closure import (
    ALL_RUNNER_MODES,
    IMPLEMENTED_SCAFFOLD_MODES,
    ROUND_ID,
    run_preflight,
)


NOT_IMPLEMENTED_EXIT = 3


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "Registry Authority Canonical Closure bootstrap runner. "
            "The approved bootstrap implements preflight only."
        )
    )
    value.add_argument("--mode", required=True, choices=ALL_RUNNER_MODES)
    value.add_argument("--evidence-root")
    return value


def emit(payload: dict[str, object], *, stream: object = sys.stdout) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=stream)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.mode not in IMPLEMENTED_SCAFFOLD_MODES:
        emit(
            {
                "round_id": ROUND_ID,
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
        result = run_preflight(args.evidence_root)
    except Exception as exc:  # fail closed before any positive claim
        emit(
            {
                "round_id": ROUND_ID,
                "mode": args.mode,
                "status": "FAIL",
                "error_type": type(exc).__name__,
                "error": str(exc),
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
