#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation import (
    generate_artifacts,
    validate_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run DVF 3-3 current-route authority required-evidence final reconciliation."
    )
    parser.add_argument(
        "--mode",
        choices=("census", "standard", "validate", "all", "machine-pass"),
        default="standard",
    )
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    if args.mode in {"census", "standard", "all", "machine-pass"}:
        final = generate_artifacts(run_current_route=args.mode in {"all", "machine-pass"})
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "predecessor_plan_document_complete": final.get("predecessor_plan_document_complete"),
                    "parent_intake_ready": final.get("parent_intake_ready"),
                    "preflight_consumption_state": final.get("preflight_consumption_state"),
                    "disposition_consumption_state": final.get("disposition_consumption_state"),
                    "dedicated_tooling_state": final.get("dedicated_tooling_state"),
                    "parent_machine_pass_claimed": final.get("parent_machine_pass_claimed"),
                },
                sort_keys=True,
            )
        )
        if args.mode == "census":
            return 0 if final.get("status") == "PASS" else 1

    if args.mode in {"validate", "standard", "all", "machine-pass"}:
        require_complete = args.require_complete or args.mode in {"all", "machine-pass"}
        report, ok = validate_artifacts(require_complete=require_complete)
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
