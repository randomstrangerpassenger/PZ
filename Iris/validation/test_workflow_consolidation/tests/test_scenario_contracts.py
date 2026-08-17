from __future__ import annotations

import pytest

from Iris.validation.test_workflow_consolidation._common import ContractError
from Iris.validation.test_workflow_consolidation.scenario_contracts import ExecutionResult, FrozenMap, ProbeResult


def test_execution_payload_is_deeply_immutable() -> None:
    result = ExecutionResult.from_payload(
        command_signature=("python", "validator.py"),
        exit_code=0,
        stdout=b"{}",
        stderr=b"",
        payload={"cases": {"one": [1, 2]}},
        producer_invocation_count=1,
        observation_coverage={"subprocess": "observed"},
    )
    assert isinstance(result.parsed_payload["cases"], FrozenMap)
    with pytest.raises(TypeError):
        result.parsed_payload["cases"]["one"] = ()


def test_blocked_probe_requires_dependency() -> None:
    with pytest.raises(ContractError):
        ProbeResult("probe", "BLOCKED", "producer failed", "receipt")
