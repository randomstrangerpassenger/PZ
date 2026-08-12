from __future__ import annotations

from Iris.validation.test_workflow_consolidation.measure_execution_cost import (
    bootstrap_interval,
    build_schedule,
    candidate_elapsed_samples,
    workload_schedule,
)
from Iris.validation.test_workflow_consolidation._common import ContractError
import pytest


def _contract() -> dict[str, object]:
    command = ["{python}", "-c", "pass"]
    return {
        "workloads": [
            {"workload_id": "mandatory_pilot", "command": command},
            {
                "workload_id": "configured-current",
                "role": "configured_route_performance_observation",
                "command": command,
            },
        ],
        "schedule": {
            "targeted_measured_blocks": 5,
            "configured_measured_blocks": 10,
        },
        "statistics": {
            "bootstrap_seed": 1729,
            "bootstrap_iterations": 10000,
            "maximum_acceptable_regression_ms": 60000,
        },
    }


def test_schedule_uses_frozen_abba_alternation() -> None:
    rows = workload_schedule("pilot", 2)
    assert [row["arm"] for row in rows[:4]] == ["A", "B", "B", "A"]
    assert [row["arm"] for row in rows[4:8]] == ["A", "B", "B", "A"]
    assert [row["arm"] for row in rows[8:12]] == ["B", "A", "A", "B"]


def test_terminal_schedule_resolves_parameterized_family_formula() -> None:
    family = {
        "family_id": "family-z",
        "disposition": "adopted",
        "terminal_measurement_workload": {
            "workload_id": "family-z",
            "command": ["{python}", "-c", "pass"],
        },
    }
    schedule = build_schedule(_contract(), [family], "terminal-acceptance")
    assert schedule["adopted_nonpilot_family_ids"] == ["family-z"]
    assert schedule["total_execution_positions"] == 92
    assert schedule["measured_block_count"] == 20


def test_bootstrap_interval_is_seed_deterministic() -> None:
    first = bootstrap_interval([1.0, 2.0, 3.0], 1729, 10000)
    second = bootstrap_interval([1.0, 2.0, 3.0], 1729, 10000)
    assert first == second


def test_adopted_family_estimate_fails_closed_without_candidate_receipt() -> None:
    with pytest.raises(ContractError):
        candidate_elapsed_samples(None, ["family-z"])
