from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
import subprocess
import sys

from .inputs import NaturalizationProvenanceInputs


def build_parser() -> argparse.ArgumentParser:
    from .naturalization_context import RUNNER_MODES

    parser = argparse.ArgumentParser(
        description=(
            "Build DVF 3-3 Korean prose naturalization evidence through the "
            "immutable Phase 8 Publish handoff boundary."
        )
    )
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--mode", required=True, choices=RUNNER_MODES)
    parser.add_argument("--attempt-root", type=Path)
    parser.add_argument("--roadmap-input", type=Path)
    parser.add_argument("--plan-review-input", type=Path)
    parser.add_argument("--cycle2-review-input", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    raw_arguments = list(argv) if argv is not None else sys.argv[1:]
    if raw_arguments and raw_arguments[0] == "acceptance":
        from .acceptance_cli import main as acceptance_main

        return acceptance_main(raw_arguments[1:])
    if raw_arguments and raw_arguments[0] == "acceptance-validate":
        from .acceptance_validation_cli import main as validation_main

        return validation_main(raw_arguments[1:])
    if raw_arguments and raw_arguments[0] == "naturalization":
        raw_arguments = raw_arguments[1:]

    from .naturalization_application import run_naturalization_mode
    from .naturalization_infrastructure import NaturalizationError

    args = build_parser().parse_args(raw_arguments)
    explicit_inputs = (
        args.roadmap_input,
        args.plan_review_input,
        args.cycle2_review_input,
    )
    try:
        if args.mode == "phase0-preflight":
            if any(path is None for path in explicit_inputs):
                raise NaturalizationError(
                    "phase0-preflight requires --roadmap-input, --plan-review-input, "
                    "and --cycle2-review-input"
                )
            provenance_inputs = NaturalizationProvenanceInputs(
                roadmap=args.roadmap_input.resolve(),
                plan_review=args.plan_review_input.resolve(),
                cycle2_review=args.cycle2_review_input.resolve(),
            )
        else:
            if any(path is not None for path in explicit_inputs):
                raise NaturalizationError(
                    "provenance input arguments are valid only for phase0-preflight"
                )
            provenance_inputs = None
        result = run_naturalization_mode(
            attempt_id=args.attempt_id,
            mode=args.mode,
            attempt_root=(args.attempt_root.resolve() if args.attempt_root else None),
            provenance_inputs=provenance_inputs,
        )
    except (NaturalizationError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 3 if "write-once conflict" in str(exc) else 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result.get("status") in {
        "blocked_prerequisite",
        "blocked_owner_approval_required",
        "blocked_facts_authority_information_insufficient",
        "blocked_human_review_required",
        "blocked_handoff_not_ready",
    }:
        return 4
    return 0 if result.get("status", "PASS") == "PASS" else 1


__all__ = ("build_parser", "main")
