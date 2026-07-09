#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dvf_3_3_dvf_system_naming_realignment import EVIDENCE_ROOT, validate_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 DVF System naming realignment artifacts.")
    parser.add_argument("--root", type=Path, default=EVIDENCE_ROOT)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--skip-route-requirements", action="store_true")
    args = parser.parse_args()

    report, ok = validate_artifacts(
        args.root,
        require_complete=args.require_complete,
        skip_route_requirements=args.skip_route_requirements,
    )
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
