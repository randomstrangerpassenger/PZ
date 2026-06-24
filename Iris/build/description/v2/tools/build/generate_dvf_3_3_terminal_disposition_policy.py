#!/usr/bin/env python
from __future__ import annotations

import json

from dvf_3_3_terminal_disposition_adjudication_common import run_all


def main() -> int:
    report = run_all()
    print(json.dumps({"status": report["status"], "phase": "policy"}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
