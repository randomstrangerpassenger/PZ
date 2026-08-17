from __future__ import annotations

import pytest

from Iris.validation.test_workflow_consolidation._common import ContractError
from Iris.validation.test_workflow_consolidation.validate_scenario_report import validate


def _report() -> dict[str, object]:
    context = {
        "schema_version": "iris_test_workflow_scenario_context_v1",
        "scenario_id": "scenario",
        "validation_subject_commit": "commit",
        "validation_subject_tree": "tree",
        "route_class": "configured-current",
        "contract_identity": {"git_blob_id": "contract"},
        "input_identity": {"input": "fixture"},
        "locale": "C",
        "environment_contract": {"python": "fixture"},
        "workspace_mode": "read-only",
        "workspace_owner": "test",
        "producer_identity": {"git_blob_id": "producer"},
    }
    return {
        "schema_version": "iris_test_workflow_scenario_report_v1",
        "deterministic_core": {
            "schema_version": "iris_test_workflow_scenario_report_v1",
            "context": context,
            "execution_result": {
                "command_signature": ["python", "validator.py"],
                "exit_code": 0,
                "stdout_sha256": "a" * 64,
                "stderr_sha256": "b" * 64,
                "parsed_payload_identity": "c" * 64,
                "producer_invocation_count": 1,
                "observation_coverage": {"subprocess": "observed"},
            },
            "required_probe_inventory": ["probe"],
            "probe_results": [
                {
                    "probe_id": "probe",
                    "status": "PASS",
                    "reason": "contract satisfied",
                    "evidence_reference": "/cases/probe",
                    "blocked_by": [],
                }
            ],
            "dependency_edges": [],
            "cross_probe_adjudication": {
                "rule": "required_probe_conjunction",
                "authority_scope": "scenario_only",
            },
            "scenario_disposition": "PASS",
        },
        "execution_observations": {},
        "normalization_excluded_fields": [],
    }


def test_valid_report_passes() -> None:
    report = _report()
    assert validate(report, report["deterministic_core"]["context"])["status"] == "PASS"


def test_semantic_field_cannot_be_normalized_away() -> None:
    report = _report()
    report["normalization_excluded_fields"] = ["/deterministic_core/probe_results"]
    with pytest.raises(ContractError):
        validate(report, report["deterministic_core"]["context"])


def test_stale_context_identity_is_rejected() -> None:
    report = _report()
    expected = {**report["deterministic_core"]["context"], "validation_subject_tree": "new-tree"}
    with pytest.raises(ContractError, match="stale or unexpected"):
        validate(report, expected)


def test_route_or_authority_scope_contamination_is_rejected() -> None:
    report = _report()
    expected = dict(report["deterministic_core"]["context"])
    report["deterministic_core"]["context"]["route_class"] = "historical"
    with pytest.raises(ContractError, match="stale or unexpected"):
        validate(report, expected)
    report = _report()
    report["deterministic_core"]["cross_probe_adjudication"]["authority_scope"] = "registry"
    with pytest.raises(ContractError, match="authority scope"):
        validate(report, report["deterministic_core"]["context"])


def test_blocked_probe_requires_a_declared_failing_dependency() -> None:
    report = _report()
    core = report["deterministic_core"]
    core["required_probe_inventory"] = ["producer", "consumer"]
    core["probe_results"] = [
        {
            "probe_id": "producer",
            "status": "PASS",
            "reason": "producer passed",
            "evidence_reference": "/producer",
            "blocked_by": [],
        },
        {
            "probe_id": "consumer",
            "status": "BLOCKED",
            "reason": "claimed dependency failure",
            "evidence_reference": "/consumer",
            "blocked_by": ["producer"],
        },
    ]
    core["dependency_edges"] = [["producer", "consumer"]]
    core["scenario_disposition"] = "FAIL"
    with pytest.raises(ContractError, match="no failing dependency"):
        validate(report, core["context"])
