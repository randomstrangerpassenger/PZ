#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_current_route_authority_required_evidence_integrity_closure import (
    generate_artifacts,
    validate_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run DVF 3-3 current-route authority required-evidence integrity closure."
    )
    parser.add_argument("--mode", choices=("scaffold", "census", "validate", "all"), default="census")
    args = parser.parse_args()

    if args.mode in {"scaffold", "census", "all"}:
        final = generate_artifacts(mode=args.mode)
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "round_id": final.get("round_id"),
                    "machine_pass_governance_only": final.get("machine_pass_governance_only"),
                    "parent_machine_pass_claimed": final.get("parent_machine_pass_claimed"),
                    "top_doc_sync_state": final.get("top_doc_sync_state"),
                    "phase0_entry_allowed": final.get("phase0_entry_allowed"),
                },
                sort_keys=True,
            )
        )
        if args.mode == "scaffold":
            return 0 if final.get("status") == "PASS" else 1

    if args.mode in {"validate", "census", "all"}:
        require_complete = args.mode == "all"
        report, ok = validate_artifacts(require_complete=require_complete)
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
