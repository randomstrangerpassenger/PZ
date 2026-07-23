#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from dvf_3_3_predecessor_stale_artifact_reentry_guard_common import (
    DISPOSITIONS,
    ROUND_REQUIRED_ARTIFACTS,
    ROUND_REQUIRED_TESTS,
    classify_claim_text,
    negative_fixture_rows,
    validate_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 predecessor/stale artifact reentry guard.")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--probe-contract", action="store_true")
    args = parser.parse_args()
    if args.probe_contract:
        claim_inputs = [
            "The stale bridge is current authority.",
            "Stale bridge cannot become current authority.",
            "레거시 bridge는 현재 권위가 아니다.",
        ]
        payload = {
            "status": "PASS",
            "dispositions": list(DISPOSITIONS),
            "round_required_artifacts": list(ROUND_REQUIRED_ARTIFACTS),
            "round_required_tests": list(ROUND_REQUIRED_TESTS),
            "negative_fixture_rows": negative_fixture_rows(),
            "claim_classifications": {
                text: classify_claim_text(text)
                for text in claim_inputs
            },
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0
    report, ok = validate_artifacts(require_complete=args.require_complete)
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
