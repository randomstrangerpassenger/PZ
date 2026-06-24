#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_live_consumer_migration_execution_common import generate_artifacts, validate_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 live consumer migration execution evidence round.")
    parser.add_argument("--mode", choices=("generate", "validate", "all"), default="all")
    parser.add_argument("--allow-live-apply", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    if args.mode in {"generate", "all"}:
        final = generate_artifacts(allow_live_apply=args.allow_live_apply)
        print(json.dumps({"status": final["status"], "closeout_state": final["closeout_state"]}, sort_keys=True))
    if args.mode in {"validate", "all"}:
        report, ok = validate_all(require_complete=args.require_complete)
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
