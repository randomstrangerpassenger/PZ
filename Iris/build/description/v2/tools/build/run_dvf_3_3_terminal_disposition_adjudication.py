#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_terminal_disposition_adjudication_common import run_all, validate_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 terminal disposition adjudication.")
    parser.add_argument("--mode", choices=("generate", "validate", "all"), default="all")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    if args.mode in {"generate", "all"}:
        report = run_all()
        print(json.dumps({"status": report["status"], "machine_contract_status": report["machine_contract_status"]}, sort_keys=True))
        if report["status"] != "PASS":
            return 1
    if args.mode in {"validate", "all"}:
        report, ok = validate_all(require_complete=args.require_complete or args.mode == "all")
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
