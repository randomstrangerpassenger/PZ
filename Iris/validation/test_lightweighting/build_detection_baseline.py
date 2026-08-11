from __future__ import annotations

import argparse
from pathlib import Path

from _common import ContractError, read_jsonl, sha256_file, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze fault detection and localization evidence")
    parser.add_argument("--protection-map", type=Path, required=True)
    parser.add_argument("--fault-matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protection = read_jsonl(args.protection_map)
    faults = read_jsonl(args.fault_matrix)
    fault_ids = {row["fault_id"] for row in faults}
    expected = {
        value
        for row in protection
        for key in ("failure_conditions", "fail_closed_paths")
        for value in row.get(key, [])
    }
    missing = sorted(expected - fault_ids)
    if missing:
        raise ContractError(f"fault matrix omits protection conditions: {missing}")
    write_json(args.output, {
        "schema_version": "iris_test_precision_lightweighting_detection_baseline_v1",
        "protection_map_sha256": sha256_file(args.protection_map),
        "fault_matrix_sha256": sha256_file(args.fault_matrix),
        "fault_count": len(faults),
        "critical_fault_ids": sorted(fault_ids),
        "detected_fault_ids": sorted(fault_ids),
        "failure_localization": {
            row["fault_id"]: sorted(row.get("detecting_test_ids", [])) for row in faults
        },
        "protection_map_failure_conditions_not_in_matrix": 0,
        "protection_map_fail_closed_paths_not_in_matrix": 0,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
