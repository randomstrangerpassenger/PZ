from __future__ import annotations

import argparse
import json
import sys

import public_text_quality_acceptance_official_0005_phase7_freeze_inventory_completeness as phase7
from public_text_quality_acceptance import ExternalInputRequired, FoundationContractError


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--require-contract", action="store_true")
    group.add_argument("--require-freeze", action="store_true")
    group.add_argument("--require-review", action="store_true")
    group.add_argument("--require-owner-seal", action="store_true")
    group.add_argument("--require-terminal", action="store_true")
    args = parser.parse_args()
    if args.attempt_id != "attempt-0005-official":
        return 2
    try:
        if args.self_test:
            result = phase7.run_focused_tests()
        elif args.require_contract:
            contract = phase7._load_contract()
            result = phase7.validate_surface_contract_document(
                contract, require_all_paths=True
            )
        elif args.require_freeze:
            result = phase7.validate_freeze_bundle(require_tracked=True)
        elif args.require_review:
            result = phase7.validate_review()
        elif args.require_owner_seal:
            result = phase7.validate_owner_seal()
        else:
            result = phase7.validate_terminal()
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
