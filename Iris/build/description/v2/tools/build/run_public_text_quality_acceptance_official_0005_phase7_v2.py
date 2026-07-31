from __future__ import annotations

import argparse
import json
import sys

import public_text_quality_acceptance_official_0005_phase7_v2 as phase7
from public_text_quality_acceptance import ExternalInputRequired, FoundationContractError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--mode", required=True, choices=("freeze", "finalize"))
    args = parser.parse_args(argv)
    if args.attempt_id != "attempt-0005-official":
        print(json.dumps({"status": "FAIL", "error": "attempt ID mismatch"}), file=sys.stderr)
        return 2
    try:
        result = phase7.materialize_freeze() if args.mode == "freeze" else phase7.finalize_terminal()
    except ExternalInputRequired as exc:
        print(json.dumps({"status": "WAITING_FOR_EXTERNAL_INPUT", "input_kind": exc.input_kind, "input_path": str(exc.path), **exc.details}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 4
    except FoundationContractError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
