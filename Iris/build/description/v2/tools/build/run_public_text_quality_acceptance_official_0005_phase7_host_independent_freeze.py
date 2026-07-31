from __future__ import annotations

import argparse
import json
import sys

import public_text_quality_acceptance_official_0005_phase7_host_independent_freeze as phase7
from public_text_quality_acceptance import ExternalInputRequired, FoundationContractError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--mode", required=True, choices=("freeze", "finalize", "handoff"))
    args = parser.parse_args(argv)
    if args.attempt_id != "attempt-0005-official":
        print(json.dumps({"status": "FAIL", "error": "attempt ID mismatch"}), file=sys.stderr)
        return 2
    try:
        if args.mode == "freeze":
            result = phase7.materialize_freeze()
        elif args.mode == "finalize":
            result = phase7.finalize_terminal()
        else:
            result = phase7.materialize_g5_handoff()
    except ExternalInputRequired as exc:
        print(
            json.dumps(
                {
                    "status": "WAITING_FOR_EXTERNAL_INPUT",
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
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
