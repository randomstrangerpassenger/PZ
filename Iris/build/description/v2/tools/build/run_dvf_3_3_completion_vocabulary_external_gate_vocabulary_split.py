from __future__ import annotations

import argparse
import json
from pathlib import Path

from dvf_3_3_completion_vocabulary_external_gate_vocabulary_split import run_fixture_check


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the completion-vocabulary isolated fixture contract.")
    parser.add_argument("--mode", required=True, choices=("fixture-check",))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--fixture-root", type=Path, required=True)
    parser.add_argument("--report-path", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run_fixture_check(root=args.root, fixture_root=args.fixture_root, report_path=args.report_path)
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error_type": type(exc).__name__, "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": report["status"], "fixture_file_count": report["fixture_file_count"], "freshness_nonce": report["freshness_nonce"]}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
