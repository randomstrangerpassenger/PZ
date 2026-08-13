from __future__ import annotations

import hashlib
import subprocess

import pytest

from Iris.validation.test_workflow_consolidation._common import (
    ContractError,
    normalized_command_signature,
    require_path_outside_repositories,
)
from Iris.validation.test_workflow_consolidation.measure_execution_cost import (
    bootstrap_interval,
    build_schedule,
    candidate_elapsed_samples,
    count_producer_invocations,
    effective_regression_ceiling_ms,
    observe_command,
    protocol_identity,
    summarize_workload,
    targeted_summary_accepted,
    resource_estimate,
    write_receipt_after_contract_check,
    workload_schedule,
)


def _contract() -> dict[str, object]:
    command = ["{python}", "-c", "pass"]
    return {
        "workloads": [
            {"workload_id": "mandatory_pilot", "command": command, "timeout_seconds": 1},
            {
                "workload_id": "configured-current",
                "role": "configured_route_performance_observation",
                "command": command,
                "timeout_seconds": 1,
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


def test_contract_drift_does_not_emit_pass_receipt(tmp_path) -> None:
    contract = tmp_path / "measurement-contract.json"
    contract.write_bytes(b"changed")
    output = tmp_path / "receipt.json"
    with pytest.raises(ContractError):
        write_receipt_after_contract_check(
            output,
            {"status": "PASS"},
            contract,
            b"initial",
        )
    assert not output.exists()


def test_protocol_identity_uses_committed_blob_bytes(tmp_path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
    contract = repository / "measurement_contract.json"
    committed = b'{"schema_version":"iris_test_workflow_measurement_contract_v1"}\n'
    contract.write_bytes(committed)
    subprocess.run(["git", "-C", str(repository), "add", "measurement_contract.json"], check=True)
    subprocess.run(["git", "-C", str(repository), "commit", "-q", "-m", "fixture"], check=True)
    contract.write_bytes(committed.replace(b"\n", b"\r\n"))

    identity = protocol_identity(contract)

    assert identity["raw_sha256"] == hashlib.sha256(committed).hexdigest()
    assert identity["raw_sha256"] != hashlib.sha256(contract.read_bytes()).hexdigest()


def test_repository_local_result_root_is_rejected_before_creation(tmp_path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    output = repository / "evidence"

    with pytest.raises(ContractError):
        require_path_outside_repositories(output, (repository,), label="measurement output root")

    assert not output.exists()


def test_relative_workload_executable_is_rejected(tmp_path) -> None:
    with pytest.raises(ContractError):
        normalized_command_signature(["python", "tool.py"], tmp_path, {})


def test_observation_rejects_ignored_checkout_mutation(tmp_path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
    (repository / ".gitignore").write_text("cache/\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", ".gitignore"], check=True)
    subprocess.run(["git", "-C", str(repository), "commit", "-q", "-m", "fixture"], check=True)
    workload = {
        "command": [
            "{python}",
            "-c",
            "from pathlib import Path; Path('cache').mkdir(); Path('cache/result').write_text('x')",
        ],
        "timeout_seconds": 5,
    }

    with pytest.raises(ContractError, match="ignored worktree state"):
        observe_command(repository, workload, tmp_path / "result", instrumented=False)


def test_first_candidate_estimate_uses_declared_timeout_without_prior_receipt() -> None:
    family = {
        "family_id": "family-z",
        "disposition": "candidate",
        "candidate_measurement_workload": {
            "workload_id": "family-z",
            "command": ["{python}", "-c", "pass"],
            "timeout_seconds": 2,
        },
    }
    schedule = build_schedule(_contract(), [family], "candidate-qualification")
    estimate = resource_estimate(schedule, {"samples": []}, None)
    assert estimate["workload_estimation_basis"]["family-z"] == (
        "declared_timeout_upper_bound_first_candidate_session"
    )
    assert estimate["expected_p50_duration_ms"] == 48_000.0


def test_direct_producer_command_is_counted_with_child_invocations() -> None:
    assert count_producer_invocations(
        ["python", "tools/producer.py"],
        [{"argv": ["python", "tools/producer.py"]}],
        ["producer.py"],
    ) == 2


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


def test_targeted_acceptance_rejects_work_introduced_on_zero_baseline_axis() -> None:
    summary = {
        "improved_beyond_observed_noise": True,
        "operation_axes": {
            "producer_invocations": {
                "applicability": "APPLICABLE",
                "strictly_reduced": True,
                "regressed_from_zero": False,
            },
            "copied_files": {
                "applicability": "NOT_APPLICABLE",
                "strictly_reduced": False,
                "regressed_from_zero": True,
            },
        },
    }
    assert targeted_summary_accepted(summary) is False


def test_qualification_uses_stricter_percent_regression_cap() -> None:
    gate = effective_regression_ceiling_ms(
        [30_000.0, 30_000.0],
        {
            "maximum_acceptable_regression_ms": 20_000,
            "maximum_acceptable_regression_pct": 10,
        },
    )
    assert gate["effective_regression_ceiling_ms"] == 3_000.0


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
