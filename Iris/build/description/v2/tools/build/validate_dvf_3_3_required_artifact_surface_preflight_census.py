#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

import dvf_3_3_required_artifact_surface_preflight_census_common as census


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 required artifact surface preflight census.")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if args.root:
        census.EVIDENCE_ROOT = args.root.resolve()
    report, ok = census.validate_artifacts(require_complete=args.require_complete)
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
