#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_predecessor_stale_artifact_reentry_guard_common import validate_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 predecessor/stale artifact reentry guard.")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    report, ok = validate_artifacts(require_complete=args.require_complete)
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
