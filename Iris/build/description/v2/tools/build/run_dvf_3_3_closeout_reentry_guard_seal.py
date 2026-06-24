#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_closeout_reentry_guard_seal_common import generate_artifacts, validate_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 closeout / reentry guard seal.")
    parser.add_argument("--mode", choices=("generate", "validate", "all"), default="all")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    if args.mode in {"generate", "all"}:
        final = generate_artifacts()
        print(
            json.dumps(
                {
                    "status": final["status"],
                    "machine_contract_status": final["machine_contract_status"],
                    "closeout_state": final["closeout_state"],
                    "canonical_seal_allowed": final["canonical_seal_allowed"],
                },
                sort_keys=True,
            )
        )
        if args.mode == "generate" and (
            final.get("status") != "PASS" or final.get("machine_contract_status") != "PASS"
        ):
            return 1
    if args.mode in {"validate", "all"}:
        report, ok = validate_all(require_complete=args.require_complete or args.mode == "all")
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
