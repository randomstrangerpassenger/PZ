from __future__ import annotations

import pytest

from Iris.validation.test_workflow_consolidation._common import ContractError
from Iris.validation.test_workflow_consolidation.validate_scenario_report import validate


def _report() -> dict[str, object]:
    return {
        "schema_version": "iris_test_workflow_scenario_report_v1",
        "deterministic_core": {
            "required_probe_inventory": ["probe"],
            "probe_results": [{"probe_id": "probe", "status": "PASS", "blocked_by": []}],
            "dependency_edges": [],
            "scenario_disposition": "PASS",
        },
        "execution_observations": {},
        "normalization_excluded_fields": [],
    }


def test_valid_report_passes() -> None:
    assert validate(_report())["status"] == "PASS"


def test_semantic_field_cannot_be_normalized_away() -> None:
    report = _report()
    report["normalization_excluded_fields"] = ["/deterministic_core/probe_results"]
    with pytest.raises(ContractError):
        validate(report)
