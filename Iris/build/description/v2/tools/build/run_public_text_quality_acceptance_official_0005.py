from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from public_text_quality_acceptance import (
    ExternalInputRequired,
    FoundationContractError,
)
from public_text_quality_acceptance_official_0005 import (
    ATTEMPT_ID,
    EVALUATION_SUBJECT_KIND,
    run_official_mode,
)


MODES = (
    "phase0-no-write-preflight",
    "phase0-binding",
    "phase1-contracts",
    "phase2-policy",
    "phase3-validator",
    "phase4-adversarial",
    "phase5-disposition",
    "phase6-gate-candidate",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--mode", required=True, choices=MODES)
    parser.add_argument(
        "--evaluation-subject-kind",
        choices=(EVALUATION_SUBJECT_KIND,),
    )
    parser.add_argument("--subject-handoff", type=Path)
    args = parser.parse_args(argv)
    if args.attempt_id != ATTEMPT_ID:
        print(
            json.dumps({"status": "FAIL", "error": "attempt ID mismatch"}),
            file=sys.stderr,
        )
        return 2
    try:
        result = run_official_mode(
            attempt_id=args.attempt_id,
            mode=args.mode,
            evaluation_subject_kind=args.evaluation_subject_kind,
            subject_handoff=(
                args.subject_handoff.resolve()
                if args.subject_handoff is not None
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
        return 2
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error": (
                        "unhandled attempt-0005 exception converted "
                        "to technical blocker"
                    ),
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


if __name__ == "__main__":
    raise SystemExit(main())
