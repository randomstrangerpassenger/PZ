#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_legacy_combined_route_axis_inventory import generate_artifacts, validate_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run DVF 3-3 legacy combined route axis inventory routing preflight."
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
                    "semantic_verdict": final.get("semantic_verdict"),
                    "blocker_count": final.get("blocker_count"),
                    "legacy_combined_route_pass_is_dvf_core_pass": final.get(
                        "legacy_combined_route_pass_is_dvf_core_pass"
                    ),
                },
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        if args.mode == "scaffold":
            return 0 if final.get("status") == "PASS" else 1

    if args.mode in {"validate", "census", "all"}:
        report, ok = validate_artifacts(require_complete=args.mode == "all")
        print(
            json.dumps(
                {"status": report["status"], "error_count": report["error_count"]},
                sort_keys=True,
            )
        )
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

