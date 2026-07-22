from __future__ import annotations

import argparse
import json
import sys

from dvf_3_3_registry_authority_canonical_closure import (
    ROUND_ID,
    validate_preflight,
)


NOT_IMPLEMENTED_EXIT = 3


FUTURE_REQUIRE_FLAGS = (
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
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "Registry Authority Canonical Closure bootstrap validator. "
            "The approved bootstrap validates preflight only."
        )
    )
    group = value.add_mutually_exclusive_group(required=True)
    group.add_argument("--require-preflight", action="store_true")
    for flag in FUTURE_REQUIRE_FLAGS:
        group.add_argument(f"--{flag}", action="store_true")
    value.add_argument("--evidence-root")
    value.add_argument("--no-write", action="store_true")
    return value


def emit(payload: dict[str, object], *, stream: object = sys.stdout) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=stream)


def selected_future_flag(args: argparse.Namespace) -> str | None:
    for flag in FUTURE_REQUIRE_FLAGS:
        if getattr(args, flag.replace("-", "_")):
            return flag
    return None


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    future = selected_future_flag(args)
    if future is not None:
        emit(
            {
                "round_id": ROUND_ID,
                "requirement": future,
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
        result = validate_preflight(args.evidence_root)
    except Exception as exc:
        emit(
            {
                "round_id": ROUND_ID,
                "requirement": "preflight",
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
