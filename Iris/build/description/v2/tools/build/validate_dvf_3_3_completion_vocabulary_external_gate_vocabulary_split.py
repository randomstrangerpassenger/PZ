from __future__ import annotations

import argparse
import json
from pathlib import Path

from dvf_3_3_completion_vocabulary_external_gate_vocabulary_split import validate_fixture_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the completion-vocabulary isolated fixture report.")
    parser.add_argument("--mode", required=True, choices=("fixture-check",))
    parser.add_argument("--fixture-root", type=Path, required=True)
    parser.add_argument("--report-path", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = validate_fixture_report(args.report_path, fixture_root=args.fixture_root)
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error_type": type(exc).__name__, "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
