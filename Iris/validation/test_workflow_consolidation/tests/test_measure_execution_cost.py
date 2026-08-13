from __future__ import annotations

import pytest

from Iris.validation.test_workflow_consolidation._common import ContractError
from Iris.validation.test_workflow_consolidation.measure_execution_cost import (
    bootstrap_interval,
    build_schedule,
    candidate_elapsed_samples,
    summarize_workload,
    targeted_summary_accepted,
    workload_schedule,
)


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
            "maximum_acceptable_regression_pct": 10,
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


def test_candidate_schedule_selects_the_declared_nonpilot_workload() -> None:
    family = {
        "family_id": "family-z",
        "disposition": "candidate",
        "candidate_measurement_workload": {
            "workload_id": "family-z",
            "command": ["{python}", "-c", "pass"],
        },
    }
    schedule = build_schedule(_contract(), [family], "candidate-qualification")
    assert [row["workload_id"] for row in schedule["workloads"]] == ["family-z"]
    assert schedule["total_execution_positions"] == 24


def test_bootstrap_interval_is_seed_deterministic() -> None:
    first = bootstrap_interval([1.0, 2.0, 3.0], 1729, 10000)
    second = bootstrap_interval([1.0, 2.0, 3.0], 1729, 10000)
    assert first == second


def test_adopted_family_estimate_fails_closed_without_candidate_receipt() -> None:
    with pytest.raises(ContractError):
        candidate_elapsed_samples(None, ["family-z"])


def _sample(arm: str, position: int, elapsed_ms: float, producer_count: int) -> dict[str, object]:
    return {
        "phase": "measured",
        "arm": arm,
        "position": position,
        "block": 1,
        "observation": {
            "elapsed_ms": elapsed_ms,
            "contract_valid": True,
            "operation_counts": {
                "producer_invocations": producer_count,
                "eligible_subprocesses": producer_count,
                "temporary_materializations": 0,
                "copied_files": 0,
                "copied_bytes": 0,
            },
        },
    }


def test_targeted_acceptance_requires_every_applicable_axis_to_reduce() -> None:
    summary = {
        "improved_beyond_observed_noise": True,
        "operation_axes": {
            "producer_invocations": {"applicability": "APPLICABLE", "strictly_reduced": True},
            "eligible_subprocesses": {"applicability": "APPLICABLE", "strictly_reduced": False},
            "copied_files": {"applicability": "NOT_APPLICABLE", "strictly_reduced": False},
        },
    }
    assert targeted_summary_accepted(summary) is False


def test_configured_route_applies_percent_and_absolute_regression_caps() -> None:
    samples = [
        _sample("A", 1, 100.0, 0),
        _sample("B", 2, 109.0, 0),
        _sample("B", 3, 109.0, 0),
        _sample("A", 4, 100.0, 0),
    ]
    statistics_contract = {
        "bootstrap_seed": 1729,
        "bootstrap_iterations": 10000,
        "maximum_acceptable_regression_ms": 20,
        "maximum_acceptable_regression_pct": 5,
    }
    summary = summarize_workload(
        samples,
        {"workload_id": "configured-current", "role": "configured_route_performance_observation"},
        statistics_contract,
    )
    gate = summary["configured_route_no_regression"]
    assert gate["effective_regression_ceiling_ms"] == 5.0
    assert gate["status"] == "FAIL"


def test_failed_warmup_invalidates_workload_summary() -> None:
    samples = [
        {
            **_sample("A", 1, 100.0, 1),
            "phase": "warmup",
            "observation": {
                **_sample("A", 1, 100.0, 1)["observation"],
                "contract_valid": False,
            },
        },
        _sample("A", 1, 100.0, 1),
        _sample("B", 2, 90.0, 0),
        _sample("B", 3, 90.0, 0),
        _sample("A", 4, 100.0, 1),
    ]
    summary = summarize_workload(
        samples,
        {"workload_id": "mandatory_pilot"},
        {"bootstrap_seed": 1729, "bootstrap_iterations": 10000},
    )
    assert summary["valid"] is False
