#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_dvf_3_3_durable_current_authority_surface_alignment import EVIDENCE_ROOT, validate_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate DVF 3-3 durable current authority surface alignment artifacts."
    )
    parser.add_argument("--root", type=Path, default=EVIDENCE_ROOT)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    report, ok = validate_artifacts(args.root, require_complete=args.require_complete)
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
