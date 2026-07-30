from __future__ import annotations

import argparse
import json
import sys

from public_text_quality_acceptance import FoundationContractError
from public_text_quality_acceptance_official_0005 import (
    ATTEMPT_ID,
    validate_official_attempt,
)


REQUIREMENTS = {
    "phase0": "--require-phase0",
    "phase1": "--require-phase1",
    "phase2": "--require-phase2",
    "phase3": "--require-phase3",
    "phase4": "--require-phase4",
    "phase5": "--require-phase5",
    "gate-candidate": "--require-gate-candidate",
    "required-gate": "--required-gate",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    for option in REQUIREMENTS.values():
        parser.add_argument(option, action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    selected = [
        requirement
        for requirement, option in REQUIREMENTS.items()
        if getattr(
            args,
            option.removeprefix("--").replace("-", "_"),
        )
    ]
    if args.attempt_id != ATTEMPT_ID or len(selected) != 1:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error": (
                        "exactly one attempt-0005 requirement is required"
                    ),
                }
            ),
            file=sys.stderr,
        )
        return 2
    try:
        result = validate_official_attempt(
            attempt_id=args.attempt_id,
            requirement=selected[0],
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
