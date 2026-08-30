"""Check scenario identities, probe dependencies and the resulting scenario status."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    from .scenario_evidence import ContractError, read_json, require, write_json
except ImportError:
    from scenario_evidence import ContractError, read_json, require, write_json


SCHEMA = "iris_test_workflow_scenario_report_v1"
CONTEXT_SCHEMA = "iris_test_workflow_scenario_context_v1"
CONTEXT_FIELDS = {
    "schema_version",
    "scenario_id",
    "validation_subject_commit",
    "validation_subject_tree",
    "route_class",
    "contract_identity",
    "input_identity",
    "locale",
    "environment_contract",
    "workspace_mode",
    "workspace_owner",
    "producer_identity",
}
EXECUTION_RESULT_FIELDS = {
    "command_signature",
    "exit_code",
    "stdout_sha256",
    "stderr_sha256",
    "parsed_payload_identity",
    "producer_invocation_count",
    "observation_coverage",
}
CORE_FIELDS = {
    "schema_version",
    "context",
    "execution_result",
    "required_probe_inventory",
    "probe_results",
    "dependency_edges",
    "cross_probe_adjudication",
    "scenario_disposition",
}
PROBE_FIELDS = {
    "probe_id",
    "status",
    "reason",
    "evidence_reference",
    "blocked_by",
}
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


def _nonempty_mapping(value: object) -> bool:
    return isinstance(value, dict) and bool(value)


def validate(
    report: dict[str, Any], expected_context: dict[str, Any]
) -> dict[str, Any]:
    require(report.get("schema_version") == SCHEMA, "scenario report schema mismatch")
    require(
        set(report)
        == {
            "schema_version",
            "deterministic_core",
            "execution_observations",
            "normalization_excluded_fields",
        },
        "scenario report contains missing or unexpected top-level fields",
    )
    core = report.get("deterministic_core")
    require(
        isinstance(core, dict) and set(core) == CORE_FIELDS,
        "deterministic_core is malformed",
    )
    require(core.get("schema_version") == SCHEMA, "deterministic_core schema mismatch")
    context = core.get("context")
    require(isinstance(context, dict) and set(context) == CONTEXT_FIELDS, "scenario context is malformed")
    require(context.get("schema_version") == CONTEXT_SCHEMA, "scenario context schema mismatch")
    require(context == expected_context, "stale or unexpected scenario context identity")
    require(
        all(context.get(key) for key in ("scenario_id", "validation_subject_commit", "validation_subject_tree", "route_class", "locale", "workspace_mode", "workspace_owner")),
        "scenario context identity is incomplete",
    )
    require(
        all(_nonempty_mapping(context.get(key)) for key in ("contract_identity", "input_identity", "environment_contract", "producer_identity")),
        "scenario context mapping identity is incomplete",
    )
    execution = core.get("execution_result")
    require(
        isinstance(execution, dict) and set(execution) == EXECUTION_RESULT_FIELDS,
        "execution result identity is malformed",
    )
    require(
        isinstance(execution.get("command_signature"), list)
        and bool(execution["command_signature"]),
        "execution command signature is missing",
    )
    require(isinstance(execution.get("exit_code"), int), "execution exit code is missing")
    require(
        all(
            isinstance(execution.get(key), str)
            and len(execution[key]) == 64
            and all(character in "0123456789abcdef" for character in execution[key])
            for key in ("stdout_sha256", "stderr_sha256", "parsed_payload_identity")
        ),
        "execution output identity is malformed",
    )
    require(
        isinstance(execution.get("producer_invocation_count"), int)
        and execution["producer_invocation_count"] >= 1,
        "producer invocation count is invalid",
    )
    require(_nonempty_mapping(execution.get("observation_coverage")), "observation coverage is missing")
    required = core.get("required_probe_inventory")
    probes = core.get("probe_results")
    require(isinstance(required, list) and bool(required) and len(required) == len(set(required)), "required probe inventory is invalid")
    require(isinstance(probes, list), "probe results are required")
    require(
        all(isinstance(row, dict) and set(row) == PROBE_FIELDS for row in probes),
        "probe result shape is malformed",
    )
    ids = [row.get("probe_id") for row in probes if isinstance(row, dict)]
    require(len(ids) == len(probes) and len(ids) == len(set(ids)), "duplicate or malformed probe result")
    require(set(ids) == set(required), "missing or unexpected probe result")
    raw_edges = core.get("dependency_edges")
    require(isinstance(raw_edges, list), "dependency edges are required")
    edges = {
        tuple(edge)
        for edge in raw_edges
        if isinstance(edge, list) and len(edge) == 2
    }
    require(len(edges) == len(raw_edges), "duplicate or malformed dependency edge")
    require(
        all(source in ids and target in ids and source != target for source, target in edges),
        "dependency edge references an unknown or identical probe",
    )
    closure = {probe_id: set() for probe_id in ids}
    for source, target in edges:
        closure[target].add(source)
    pending = {probe_id: set(dependencies) for probe_id, dependencies in closure.items()}
    while pending:
        ready = {probe_id for probe_id, dependencies in pending.items() if not dependencies}
        require(bool(ready), "dependency graph contains a cycle")
        pending = {
            probe_id: dependencies - ready
            for probe_id, dependencies in pending.items()
            if probe_id not in ready
        }
    probe_by_id = {row["probe_id"]: row for row in probes}
    for row in probes:
        status = row.get("status")
        require(status in {"PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE"}, "invalid probe status")
        require(isinstance(row.get("reason"), str) and bool(row["reason"]), "probe reason is required")
        require(
            isinstance(row.get("evidence_reference"), str)
            and bool(row["evidence_reference"]),
            "probe evidence reference is required",
        )
        blocked_by = row.get("blocked_by", [])
        require(isinstance(blocked_by, list) and len(blocked_by) == len(set(blocked_by)), "blocked_by is malformed")
        require(status != "BLOCKED" or bool(blocked_by), "BLOCKED probe lacks dependency")
        require(status == "BLOCKED" or not blocked_by, "non-BLOCKED probe declares blocked_by")
        require(all((dependency, row["probe_id"]) in edges for dependency in blocked_by), "undeclared blocked_by dependency")
        if status == "BLOCKED":
            require(
                all(probe_by_id[dependency]["status"] in {"FAIL", "BLOCKED"} for dependency in blocked_by),
                "BLOCKED probe has no failing dependency",
            )
        incoming = [source for source, target in edges if target == row["probe_id"]]
        if status in {"PASS", "NOT_APPLICABLE"}:
            require(
                all(probe_by_id[source]["status"] in {"PASS", "NOT_APPLICABLE"} for source in incoming),
                "passing probe has a failed dependency",
            )
    adjudication = core.get("cross_probe_adjudication")
    require(
        adjudication
        == {
            "rule": "required_probe_conjunction",
            "authority_scope": "scenario_only",
        },
        "cross-probe adjudication or authority scope mismatch",
    )
    observations = report.get("execution_observations")
    require(isinstance(observations, dict), "execution observations are malformed")
    raw_exclusions = report.get("normalization_excluded_fields")
    require(
        isinstance(raw_exclusions, list)
        and len(raw_exclusions) == len(set(raw_exclusions)),
        "normalization exclusions are malformed",
    )
    exclusions = set(raw_exclusions)
    require(exclusions <= ALLOWED_EXCLUSIONS, "undeclared normalization exclusion")
    expected = "PASS" if all(row["status"] in {"PASS", "NOT_APPLICABLE"} for row in probes) else "FAIL"
    require(core.get("scenario_disposition") == expected, "impossible scenario disposition")
    return {"schema_version": "iris_test_workflow_scenario_report_validation_v1", "status": "PASS", "probe_count": len(probes)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Iris scenario report")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-context", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_json(args.output, validate(read_json(args.report), read_json(args.expected_context)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
