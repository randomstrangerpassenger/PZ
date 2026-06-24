#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_closeout_reentry_guard_seal_common import validate_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 predecessor reentry guard.")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    report, ok = validate_all(require_complete=args.require_complete, section="predecessor")
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
