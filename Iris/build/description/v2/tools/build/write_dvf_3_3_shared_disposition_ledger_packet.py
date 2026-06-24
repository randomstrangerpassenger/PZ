#!/usr/bin/env python
from __future__ import annotations

import json

from dvf_3_3_shared_disposition_consumption_common import generate_artifacts


def main() -> int:
    final = generate_artifacts()
    print(json.dumps({"status": final["status"], "ledger_packet": "docs/dvf_3_3_shared_disposition_ledger_packet.md"}, sort_keys=True))
    return 0 if final["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
