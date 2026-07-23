#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal import validate_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate DVF 3-3 vNext successor readpoint governance seal artifacts."
    )
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()
    report, ok = validate_artifacts(
        require_complete=args.require_complete,
        write_report=not args.no_write_report,
    )
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
