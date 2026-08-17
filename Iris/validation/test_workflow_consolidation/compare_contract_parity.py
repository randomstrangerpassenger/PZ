from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import ContractError, read_json, read_jsonl, require, write_json
except ImportError:
    from _common import ContractError, read_json, read_jsonl, require, write_json


def compare(matrix: list[dict[str, Any]], before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_probes = {row["probe_id"]: row for row in before["deterministic_core"]["probe_results"]}
    after_probes = {row["probe_id"]: row for row in after["deterministic_core"]["probe_results"]}
    rows = []
    for mapping in matrix:
        probe_id = mapping["successor_probe_id"]
        old_id = mapping["predecessor_test_id"]
        predecessor = before_probes.get(old_id) or before_probes.get(probe_id)
        successor = after_probes.get(probe_id)
        parity = bool(predecessor and successor and predecessor.get("status") == successor.get("status"))
        rows.append({"predecessor_test_id": old_id, "successor_probe_id": probe_id, "status": "PASS" if parity else "FAIL"})
    status = "PASS" if rows and all(row["status"] == "PASS" for row in rows) else "FAIL"
    return {"schema_version": "iris_test_workflow_contract_parity_v1", "status": status, "mappings": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare predecessor and successor contract reports")
    parser.add_argument("--contract-map", type=Path, required=True)
    parser.add_argument("--before-report", type=Path, required=True)
    parser.add_argument("--after-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(read_jsonl(args.contract_map), read_json(args.before_report), read_json(args.after_report))
    write_json(args.output, result)
    require(result["status"] == "PASS", "contract parity failed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
