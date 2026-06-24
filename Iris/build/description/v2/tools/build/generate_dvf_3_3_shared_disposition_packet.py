#!/usr/bin/env python
from __future__ import annotations

import json

from dvf_3_3_shared_disposition_consumption_common import generate_artifacts


def main() -> int:
    report = generate_artifacts()
    print(json.dumps({"status": report["status"], "closeout_state": report["closeout_state"]}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
