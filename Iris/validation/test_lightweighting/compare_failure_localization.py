from __future__ import annotations

import argparse
from pathlib import Path

from _common import ContractError, read_json, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare fixed-domain failure localization")
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before = read_json(args.before)
    after = read_json(args.after)
    before_map = before.get("failure_localization", {})
    after_map = after.get("failure_localization", {})
    missing_faults = sorted(set(before_map) - set(after_map))
    unlocalized = sorted(key for key in before_map if not after_map.get(key))
    report = {
        "schema_version": "iris_test_precision_lightweighting_failure_localization_comparison_v1",
        "missing_faults": missing_faults,
        "unlocalized_faults": unlocalized,
        "failure_localization_regression": len(missing_faults) + len(unlocalized),
    }
    write_json(args.output, report)
    if report["failure_localization_regression"]:
        raise ContractError("failure localization regressed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
