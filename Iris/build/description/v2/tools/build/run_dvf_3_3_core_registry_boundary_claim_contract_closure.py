#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_core_registry_boundary_claim_contract_closure import generate_artifacts, validate_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run DVF 3-3 Core / Registry boundary claim contract closure."
    )
    parser.add_argument("--mode", choices=("scaffold", "census", "validate", "all"), default="census")
    args = parser.parse_args()

    final = None
    if args.mode in {"scaffold", "census", "all"}:
        final = generate_artifacts(mode=args.mode)
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "round_id": final.get("round_id"),
                    "claim_boundary_split_complete": final.get("claim_boundary_split_complete"),
                    "predecessor_inventory_freshness_status": final.get(
                        "predecessor_inventory_freshness_status"
                    ),
                    "required_gate_adopted": final.get("required_gate_adopted"),
                },
                sort_keys=True,
            )
        )

    if args.mode in {"validate", "census", "all"}:
        report, ok = validate_artifacts(require_complete=args.mode == "all")
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0 if final and final.get("claim_boundary_split_complete") else 1


if __name__ == "__main__":
    raise SystemExit(main())
