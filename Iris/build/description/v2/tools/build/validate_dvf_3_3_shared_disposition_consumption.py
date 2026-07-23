#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_shared_disposition_consumption_common import (
    classify_consumption_record,
    validate_all,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 shared disposition consumption artifacts.")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--probe-classifiers", action="store_true")
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()
    if args.probe_classifiers:
        records = [
            {
                "path": (
                    "Iris/build/description/v2/staging/"
                    "2105_baseline_consumption_audit/classified_ledger.jsonl"
                ),
                "authority_role": "current_execution_authority",
            },
            {
                "denominator_id": "DEN-AUDIT-EXECUTING-CONSUMERS",
                "value": 1063,
            },
            {"token": "2105", "lifecycle_role": "current_debt"},
        ]
        payload = {
            "status": "PASS",
            "classifications": [
                classify_consumption_record(record)
                for record in records
            ],
        }
        print(json.dumps(payload, sort_keys=True))
        return 0
    report, ok = validate_all(
        require_complete=args.require_complete,
        write_report=not args.no_write_report,
    )
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
