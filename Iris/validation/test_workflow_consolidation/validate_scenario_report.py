from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import ContractError, read_json, require, write_json
except ImportError:
    from _common import ContractError, read_json, require, write_json


SCHEMA = "iris_test_workflow_scenario_report_v1"
ALLOWED_EXCLUSIONS = {
    "/execution_observations/timestamps",
    "/execution_observations/elapsed_ms",
    "/execution_observations/process_runtime_identities",
    "/execution_observations/external_paths",
    "/execution_observations/run_id",
    "/execution_observations/order_id",
    "/execution_observations/sample_id",
    "/execution_observations/raw_locations",
}


def validate(report: dict[str, Any]) -> dict[str, Any]:
    require(report.get("schema_version") == SCHEMA, "scenario report schema mismatch")
    core = report.get("deterministic_core")
    require(isinstance(core, dict), "deterministic_core is required")
    required = core.get("required_probe_inventory")
    probes = core.get("probe_results")
    require(isinstance(required, list) and len(required) == len(set(required)), "required probe inventory is invalid")
    require(isinstance(probes, list), "probe results are required")
    ids = [row.get("probe_id") for row in probes if isinstance(row, dict)]
    require(len(ids) == len(probes) and len(ids) == len(set(ids)), "duplicate or malformed probe result")
    require(set(ids) == set(required), "missing or unexpected probe result")
    edges = {tuple(edge) for edge in core.get("dependency_edges", []) if isinstance(edge, list) and len(edge) == 2}
    for row in probes:
        status = row.get("status")
        require(status in {"PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE"}, "invalid probe status")
        blocked_by = row.get("blocked_by", [])
        require(status != "BLOCKED" or bool(blocked_by), "BLOCKED probe lacks dependency")
        require(all((dependency, row["probe_id"]) in edges for dependency in blocked_by), "undeclared blocked_by dependency")
    exclusions = set(report.get("normalization_excluded_fields", []))
    require(exclusions <= ALLOWED_EXCLUSIONS, "undeclared normalization exclusion")
    expected = "PASS" if all(row["status"] in {"PASS", "NOT_APPLICABLE"} for row in probes) else "FAIL"
    require(core.get("scenario_disposition") == expected, "impossible scenario disposition")
    return {"schema_version": "iris_test_workflow_scenario_report_validation_v1", "status": "PASS", "probe_count": len(probes)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Iris scenario report")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_json(args.output, validate(read_json(args.report)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
