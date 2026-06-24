#!/usr/bin/env python
from __future__ import annotations

import json

from consumer_universe_denominator_lock_common import validate_all


def main() -> int:
    report, ok = validate_all()
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

