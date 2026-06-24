#!/usr/bin/env python
from __future__ import annotations

import json

from consumer_universe_denominator_lock_common import validate_claim_guard


def main() -> int:
    report, ok = validate_claim_guard()
    print(json.dumps({"status": report["status"], "failure_count": report["failure_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

