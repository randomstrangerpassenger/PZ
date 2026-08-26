from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import sys

from .acceptance_context import DEFAULT_FOUNDATION_ROOT, OFFICIAL_MODES
from .acceptance_disposition import run_official_mode
from .acceptance_foundation_application import build_foundation
from .acceptance_infrastructure import ExternalInputRequired, FoundationContractError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build either the candidate-independent G4 foundation or one explicit "
            "official Iris Publish Boundary public-text acceptance phase."
        )
    )
    parser.add_argument("--foundation-id")
    parser.add_argument("--attempt-id")
    parser.add_argument(
        "--mode", required=True, choices=("foundation-build", *OFFICIAL_MODES)
    )
    parser.add_argument(
        "--evaluation-subject-kind",
        choices=(
            "current_runtime_payload",
            "dvf_3_3_korean_naturalization_candidate",
        ),
    )
    parser.add_argument("--subject-handoff", type=Path)
    parser.add_argument("--attempt-root", type=Path)
    parser.add_argument(
        "--foundation-root",
        type=Path,
        default=DEFAULT_FOUNDATION_ROOT,
        help="Explicit foundation output root; defaults to the tracked G4 root.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.mode == "foundation-build":
            if (
                not args.foundation_id
                or args.attempt_id
                or args.attempt_root
                or args.evaluation_subject_kind
                or args.subject_handoff
            ):
                raise FoundationContractError(
                    "foundation-build requires only foundation namespace arguments"
                )
            result = build_foundation(
                foundation_id=args.foundation_id,
                foundation_root=args.foundation_root.resolve(),
            )
        else:
            if not args.attempt_id or args.foundation_id:
                raise FoundationContractError(
                    "official modes require --attempt-id and forbid --foundation-id"
                )
            result = run_official_mode(
                attempt_id=args.attempt_id,
                mode=args.mode,
                evaluation_subject_kind=args.evaluation_subject_kind,
                subject_handoff=(
                    args.subject_handoff.resolve()
                    if args.subject_handoff is not None
                    else None
                ),
                attempt_root=(
                    args.attempt_root.resolve()
                    if args.attempt_root is not None
                    else None
                ),
            )
    except ExternalInputRequired as exc:
        print(
            json.dumps(
                {
                    "status": "WAITING_FOR_EXTERNAL_INPUT",
                    "error": str(exc),
                    "input_kind": exc.input_kind,
                    "input_path": str(exc.path),
                    **exc.details,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 4
    except FoundationContractError as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 3 if "write-once conflict" in str(exc) else 2
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error": "unhandled runner exception converted to technical blocker",
                    "exception_type": type(exc).__name__,
                    "technical_blocker_count": 1,
                    "official_disposition": "blocked",
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


__all__ = ("build_parser", "main")
