from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import sys

from .acceptance_validation import (
    DEFAULT_FOUNDATION_ROOT,
    FoundationContractError,
    validate_foundation,
    validate_official_attempt,
)


REQUIREMENT_FLAGS = (
    "phase0",
    "phase1",
    "phase2",
    "phase3",
    "phase4",
    "phase5",
    "gate-candidate",
    "phase6",
    "independent-review",
    "owner-seal",
    "terminal-seal",
    "required-gate",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only validator for the Iris Publish Boundary G4 foundation or "
            "one explicit official phase requirement."
        )
    )
    parser.add_argument("--foundation-id")
    parser.add_argument("--attempt-id")
    parser.add_argument("--require-foundation-ready", action="store_true")
    for requirement in REQUIREMENT_FLAGS[:-1]:
        parser.add_argument(f"--require-{requirement}", action="store_true")
    parser.add_argument("--required-gate", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--attempt-root", type=Path)
    parser.add_argument(
        "--foundation-root",
        type=Path,
        default=DEFAULT_FOUNDATION_ROOT,
        help="Explicit foundation input root; defaults to the tracked G4 root.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        requirements = {
            name: getattr(
                args,
                (
                    "required_gate"
                    if name == "required-gate"
                    else f"require_{name.replace('-', '_')}"
                ),
            )
            for name in REQUIREMENT_FLAGS
        }
        selected = [name for name, enabled in requirements.items() if enabled]
        if args.require_foundation_ready:
            if (
                not args.foundation_id
                or args.attempt_id
                or selected
                or not args.no_write
            ):
                raise FoundationContractError(
                    "foundation validation requires foundation namespace, "
                    "--require-foundation-ready, and --no-write only"
                )
            result = validate_foundation(
                foundation_id=args.foundation_id,
                foundation_root=args.foundation_root.resolve(),
            )
        else:
            if args.foundation_id or not args.attempt_id or len(selected) != 1:
                raise FoundationContractError(
                    "official validation requires --attempt-id and exactly one "
                    "official requirement"
                )
            result = validate_official_attempt(
                attempt_id=args.attempt_id,
                requirement=selected[0],
                attempt_root=(
                    args.attempt_root.resolve()
                    if args.attempt_root is not None
                    else None
                ),
            )
    except FoundationContractError as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 5 if result.get("status") == "BLOCKED" else 0
