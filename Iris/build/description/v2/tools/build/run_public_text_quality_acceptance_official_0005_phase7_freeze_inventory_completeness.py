from __future__ import annotations

import argparse
import json
import sys

import public_text_quality_acceptance_official_0005_phase7_freeze_inventory_completeness as phase7
from public_text_quality_acceptance import ExternalInputRequired, FoundationContractError


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument(
        "--mode", required=True, choices=("contract", "freeze", "finalize", "handoff")
    )
    args = parser.parse_args()
    if args.attempt_id != "attempt-0005-official":
        return 2
    try:
        if args.mode == "contract":
            result = phase7.materialize_surface_contract()
        elif args.mode == "freeze":
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
        print(json.dumps({"status": "FAIL", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
