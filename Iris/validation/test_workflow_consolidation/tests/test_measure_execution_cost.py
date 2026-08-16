from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time

import pytest

from Iris.validation.test_workflow_consolidation._common import (
    ContractError,
    normalized_command_signature,
    require_path_outside_repositories,
)
from Iris.validation.test_workflow_consolidation.measure_execution_cost import (
    _read_events,
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


def test_candidate_schedule_rejects_missing_family_workload() -> None:
    with pytest.raises(ContractError, match="exactly one"):
        build_schedule(_contract(), [], "candidate-qualification")


def test_terminal_schedule_rejects_family_collision_with_builtin_workload() -> None:
    family = {
        "family_id": "configured-current",
        "disposition": "adopted",
        "terminal_measurement_workload": {
            "workload_id": "configured-current",
            "command": ["{python}", "-c", "pass"],
        },
    }
    with pytest.raises(ContractError, match="duplicate scheduled"):
        build_schedule(_contract(), [family], "terminal-acceptance")


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
        "canonical_input_paths": [".gitignore"],
        "expected_output_contract": {
            "valid_exit_codes": [0],
            "normalized_stdout": "fixture",
            "normalized_stderr": "fixture",
        },
        "input_identity": "fixture",
        "timeout_seconds": 5,
    }

    with pytest.raises(ContractError, match="ignored worktree state"):
        observe_command(repository, workload, tmp_path / "result", instrumented=False)


def test_observation_isolates_repository_output_and_uv_cache(tmp_path, monkeypatch) -> None:
    repository = tmp_path / "repo"
    output = repository / "Iris" / "output"
    output.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
    (repository / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
    (output / "seed.txt").write_text("seed", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", ".gitignore", "Iris/output/seed.txt"], check=True)
    subprocess.run(["git", "-C", str(repository), "commit", "-q", "-m", "fixture"], check=True)
    workload = {
        "command": [
            "{python}",
            "-c",
            (
                "import os, shutil; from pathlib import Path; "
                "root=Path(os.environ['IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT']); "
                "assert not root.exists(); "
                "shutil.copytree('Iris/output', root); "
                "assert (root/'seed.txt').read_text() == 'seed'; "
                "(root/'result.txt').write_text('result'); "
                "Path(os.environ['UV_CACHE_DIR']).mkdir()"
            ),
        ],
        "canonical_input_paths": [".gitignore"],
        "expected_output_contract": {
            "valid_exit_codes": [0],
            "normalized_stdout": "fixture",
            "normalized_stderr": "fixture",
        },
        "input_identity": "fixture",
        "timeout_seconds": 5,
        "valid_exit_codes": [0],
    }

    execution_parent = tmp_path / "short"
    monkeypatch.setenv("IRIS_WORKFLOW_EXECUTION_OUTPUT_PARENT", str(execution_parent))
    result_root = tmp_path / "result"
    observation = observe_command(repository, workload, result_root, instrumented=True)

    assert observation["contract_valid"] is True
    assert observation["operation_counts"]["copied_files"] == 1
    assert observation["operation_counts"]["copied_bytes"] == len("seed")
    assert observation["operation_counts"]["temporary_materializations"] == 1
    assert observation["measurement_boundary"] == {
        "starts_before_execution_root_and_legacy_output_materialization": True,
        "ends_after_child_process_completion": True,
        "legacy_output_copy_in_elapsed_time_and_operation_counts": True,
    }
    assert list(execution_parent.iterdir()) == []
    assert not (result_root / "t").exists()
    assert subprocess.run(
        ["git", "-C", str(repository), "status", "--short", "--ignored"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout == ""


def test_observation_timeout_reaps_descendant_after_atomic_job_assignment(tmp_path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
    marker = repository / "marker.txt"
    marker.write_text("fixture", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", "marker.txt"], check=True)
    subprocess.run(["git", "-C", str(repository), "commit", "-q", "-m", "fixture"], check=True)
    workload = {
        "command": [
            "{python}",
            "-c",
            (
                "import subprocess, sys; from pathlib import Path; "
                "child=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
                "Path(sys.argv[1]).joinpath('descendant.pid').write_text(str(child.pid)); "
                "child.wait()"
            ),
            "{result_root}",
        ],
        "canonical_input_paths": ["marker.txt"],
        "expected_output_contract": {
            "valid_exit_codes": [0],
            "normalized_stdout": "fixture",
            "normalized_stderr": "fixture",
        },
        "input_identity": "fixture",
        "timeout_seconds": 1,
    }
    observation = observe_command(repository, workload, tmp_path / "result", instrumented=False)

    assert observation["timed_out"] is True
    assert observation["contract_valid"] is False
    assert observation["elapsed_ms"] < 10_000
    descendant_pid = int((tmp_path / "result" / "descendant.pid").read_text(encoding="utf-8"))
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        try:
            os.kill(descendant_pid, 0)
        except OSError:
            break
        time.sleep(0.05)
    else:
        pytest.fail("timed-out measurement descendant remained alive")


def test_instrumented_observation_counts_copy2(tmp_path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
    source = repository / "source.txt"
    source.write_text("payload", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", "source.txt"], check=True)
    subprocess.run(["git", "-C", str(repository), "commit", "-q", "-m", "fixture"], check=True)
    workload = {
        "command": [
            "{python}",
            "-c",
            "from pathlib import Path; import shutil, sys; shutil.copy2('source.txt', Path(sys.argv[1]) / 'copy.txt')",
            "{result_root}",
        ],
        "canonical_input_paths": ["source.txt"],
        "expected_output_contract": {
            "valid_exit_codes": [0],
            "normalized_stdout": "fixture",
            "normalized_stderr": "fixture",
        },
        "input_identity": "fixture",
        "timeout_seconds": 5,
    }

    observation = observe_command(repository, workload, tmp_path / "result", instrumented=True)

    assert observation["operation_counts"]["copied_files"] == 1
    assert observation["operation_counts"]["copied_bytes"] == len("payload")
    assert observation["observer_integrity"]["status"] == "PASS"
    assert observation["observer_integrity"]["sequence_gap_count"] == 0


def test_observer_event_stream_requires_complete_contiguous_lifecycle(tmp_path) -> None:
    event_root = tmp_path / "events"
    event_root.mkdir()
    event_file = event_root / f"events-42-{'0' * 32}.jsonl"
    event_file.write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                {"kind": "observer_start", "pid": 42, "parent_pid": 1, "sequence": 1},
                {"kind": "copy", "pid": 42, "sequence": 3, "copied_bytes": 1},
                {"kind": "observer_complete", "pid": 42, "sequence": 4},
            )
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="sequence is incomplete"):
        _read_events(event_root, 42, 1)

    event_file.write_text(
        json.dumps({"kind": "observer_start", "pid": 42, "parent_pid": 1, "sequence": 1}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="lifecycle is incomplete"):
        _read_events(event_root, 42, 1)


def test_observer_event_stream_requires_expected_python_descendant_lifecycle(tmp_path) -> None:
    event_root = tmp_path / "events"
    event_root.mkdir()
    (event_root / f"events-42-{'0' * 32}.jsonl").write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                {"kind": "observer_start", "pid": 42, "parent_pid": 1, "sequence": 1},
                {
                    "kind": "subprocess",
                    "pid": 42,
                    "sequence": 2,
                    "child_pid": 43,
                    "python_observer_expected": True,
                },
                {"kind": "observer_complete", "pid": 42, "sequence": 3},
            )
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="expected Python descendant"):
        _read_events(event_root, 42, 1)

    (event_root / f"events-43-{'1' * 32}.jsonl").write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                {"kind": "observer_start", "pid": 43, "parent_pid": 42, "sequence": 1},
                {"kind": "observer_complete", "pid": 43, "sequence": 2},
            )
        )
        + "\n",
        encoding="utf-8",
    )
    _, integrity = _read_events(event_root, 42, 1)
    assert integrity["expected_python_descendant_count"] == 1
    assert integrity["missing_python_descendant_count"] == 0


def test_observer_event_stream_distinguishes_reused_process_ids(tmp_path) -> None:
    event_root = tmp_path / "events"
    event_root.mkdir()
    (event_root / f"events-42-{'0' * 32}.jsonl").write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                {"kind": "observer_start", "pid": 42, "parent_pid": 1, "sequence": 1},
                {
                    "kind": "subprocess",
                    "pid": 42,
                    "sequence": 2,
                    "child_pid": 43,
                    "python_observer_expected": True,
                },
                {
                    "kind": "subprocess",
                    "pid": 42,
                    "sequence": 3,
                    "child_pid": 43,
                    "python_observer_expected": True,
                },
                {"kind": "observer_complete", "pid": 42, "sequence": 4},
            )
        )
        + "\n",
        encoding="utf-8",
    )
    for token in ("1", "2"):
        (event_root / f"events-43-{token * 32}.jsonl").write_text(
            "\n".join(
                json.dumps(row)
                for row in (
                    {"kind": "observer_start", "pid": 43, "parent_pid": 42, "sequence": 1},
                    {"kind": "observer_complete", "pid": 43, "sequence": 2},
                )
            )
            + "\n",
            encoding="utf-8",
        )

    _, integrity = _read_events(event_root, 42, 1)
    assert integrity["observed_process_count"] == 3
    assert integrity["expected_python_descendant_count"] == 2


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
