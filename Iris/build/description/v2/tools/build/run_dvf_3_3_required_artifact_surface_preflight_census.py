#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_required_artifact_surface_preflight_census_common import (
    generate_artifacts,
    validate_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 required artifact surface preflight census.")
    parser.add_argument(
        "--mode",
        choices=("census", "standard", "validate", "all", "machine-pass"),
        default="standard",
    )
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    if args.mode in {"census", "standard", "all", "machine-pass"}:
        final = generate_artifacts(run_current_route=args.mode in {"standard", "all", "machine-pass"})
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "semantic_verdict": final.get("semantic_verdict"),
                    "artifact_disposition_state": final.get("artifact_disposition_state"),
                    "current_route_validation_state": final.get("current_route_validation_state"),
                },
                sort_keys=True,
            )
        )
        if args.mode == "census":
            return 0 if final.get("status") == "PASS" else 1

    if args.mode in {"validate", "standard", "all", "machine-pass"}:
        require_complete = args.require_complete or args.mode in {"standard", "all", "machine-pass"}
        report, ok = validate_artifacts(require_complete=require_complete)
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
