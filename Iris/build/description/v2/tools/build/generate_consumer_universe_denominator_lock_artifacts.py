#!/usr/bin/env python
from __future__ import annotations

import json

from consumer_universe_denominator_lock_common import run_all


def main() -> int:
    report = run_all()
    print(json.dumps({"status": report["status"], "machine_contract_status": report["machine_contract_status"]}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

