#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_predecessor_stale_artifact_reentry_guard_common import (
    generate_artifacts,
    validate_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 predecessor/stale artifact reentry guard.")
    parser.add_argument("--mode", choices=("preflight", "generate", "validate", "all", "machine-pass"), default="all")
    parser.add_argument("--go-no-go", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    if args.mode == "preflight":
        final = generate_artifacts(preflight_only=True)
        print(json.dumps({"status": final.get("status"), "closeout_state": final.get("closeout_state")}, sort_keys=True))
        return 0 if final.get("status") == "PASS" else 1

    if args.mode in {"generate", "all", "machine-pass"}:
        final = generate_artifacts(run_current_route=args.mode in {"all", "machine-pass"})
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "machine_contract_status": final.get("machine_contract_status"),
                    "current_route_validation_state": final.get("current_route_validation_state"),
                },
                sort_keys=True,
            )
        )
        if args.mode == "generate":
            return 0 if final.get("machine_contract_status") == "PASS" else 1

    if args.mode in {"validate", "all", "machine-pass"}:
        require_complete = args.require_complete or args.mode in {"all", "machine-pass"}
        report, ok = validate_artifacts(require_complete=require_complete)
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
