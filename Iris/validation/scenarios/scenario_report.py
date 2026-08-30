"""Immutable scenario context, execution result and dependent-probe report models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Iterator

from .scenario_evidence import canonical_bytes, require, sha256_bytes


class FrozenMap(Mapping[str, Any]):
    __slots__ = ("_items", "_index")

    def __init__(self, value: Mapping[str, Any]):
        self._items = tuple(sorted((str(key), freeze(item)) for key, item in value.items()))
        self._index = dict(self._items)

    def __getitem__(self, key: str) -> Any:
        return self._index[key]

    def __iter__(self) -> Iterator[str]:
        return iter(key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __hash__(self) -> int:
        return hash(self._items)

    def to_dict(self) -> dict[str, Any]:
        return {key: thaw(value) for key, value in self._items}


def freeze(value: Any) -> Any:
    if isinstance(value, FrozenMap):
        return value
    if isinstance(value, Mapping):
        return FrozenMap(value)
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    require(value is None or isinstance(value, (str, int, float, bool)), f"unsupported immutable value: {type(value)}")
    return value


def thaw(value: Any) -> Any:
    if isinstance(value, FrozenMap):
        return value.to_dict()
    if isinstance(value, tuple):
        return [thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class ScenarioContext:
    schema_version: str
    scenario_id: str
    validation_subject_commit: str
    validation_subject_tree: str
    route_class: str
    contract_identity: FrozenMap
    input_identity: FrozenMap
    locale: str
    environment_contract: FrozenMap
    workspace_mode: str
    workspace_owner: str
    producer_identity: FrozenMap

    def __post_init__(self) -> None:
        require(
            self.schema_version == "iris_test_workflow_scenario_context_v1",
            "unsupported scenario context schema",
        )
        for label, value in (
            ("scenario_id", self.scenario_id),
            ("validation_subject_commit", self.validation_subject_commit),
            ("validation_subject_tree", self.validation_subject_tree),
            ("route_class", self.route_class),
            ("locale", self.locale),
            ("workspace_mode", self.workspace_mode),
            ("workspace_owner", self.workspace_owner),
        ):
            require(bool(value), f"{label} is required")


@dataclass(frozen=True)
class ExecutionResult:
    command_signature: tuple[str, ...]
    exit_code: int
    stdout_sha256: str
    stderr_sha256: str
    parsed_payload_identity: str
    parsed_payload: FrozenMap
    producer_invocation_count: int
    observation_coverage: FrozenMap

    @classmethod
    def from_payload(
        cls,
        *,
        command_signature: tuple[str, ...],
        exit_code: int,
        stdout: bytes,
        stderr: bytes,
        payload: Mapping[str, Any],
        producer_invocation_count: int,
        observation_coverage: Mapping[str, Any],
    ) -> "ExecutionResult":
        frozen_payload = FrozenMap(payload)
        return cls(
            command_signature=command_signature,
            exit_code=exit_code,
            stdout_sha256=sha256_bytes(stdout),
            stderr_sha256=sha256_bytes(stderr),
            parsed_payload_identity=sha256_bytes(canonical_bytes(thaw(frozen_payload))),
            parsed_payload=frozen_payload,
            producer_invocation_count=producer_invocation_count,
            observation_coverage=FrozenMap(observation_coverage),
        )


@dataclass(frozen=True)
class ProbeResult:
    probe_id: str
    status: str
    reason: str
    evidence_reference: str
    blocked_by: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require(bool(self.probe_id), "probe_id is required")
        require(self.status in {"PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE"}, "unsupported probe status")
        require(bool(self.reason), "probe reason is required")
        require(bool(self.evidence_reference), "probe evidence reference is required")
        require(self.status != "BLOCKED" or bool(self.blocked_by), "BLOCKED probe requires blocked_by")
        require(self.status == "BLOCKED" or not self.blocked_by, "only BLOCKED probes may declare blocked_by")


@dataclass(frozen=True)
class ScenarioReport:
    context: ScenarioContext
    execution_result: ExecutionResult
    required_probe_inventory: tuple[str, ...]
    probe_results: tuple[ProbeResult, ...]
    dependency_edges: tuple[tuple[str, str], ...] = ()
    execution_observations: FrozenMap = field(default_factory=lambda: FrozenMap({}))

    def __post_init__(self) -> None:
        required = self.required_probe_inventory
        probe_ids = tuple(row.probe_id for row in self.probe_results)
        require(len(required) == len(set(required)), "duplicate required probe")
        require(len(probe_ids) == len(set(probe_ids)), "duplicate probe result")
        require(set(required) == set(probe_ids), "required probe/result mismatch")

    def deterministic_core(self) -> dict[str, Any]:
        probes = [
            {
                "probe_id": row.probe_id,
                "status": row.status,
                "reason": row.reason,
                "evidence_reference": row.evidence_reference,
                "blocked_by": list(row.blocked_by),
            }
            for row in self.probe_results
        ]
        return {
            "schema_version": "iris_test_workflow_scenario_report_v1",
            "context": thaw(freeze(self.context.__dict__)),
            "execution_result": {
                "command_signature": list(self.execution_result.command_signature),
                "exit_code": self.execution_result.exit_code,
                "stdout_sha256": self.execution_result.stdout_sha256,
                "stderr_sha256": self.execution_result.stderr_sha256,
                "parsed_payload_identity": self.execution_result.parsed_payload_identity,
                "producer_invocation_count": self.execution_result.producer_invocation_count,
                "observation_coverage": thaw(self.execution_result.observation_coverage),
            },
            "required_probe_inventory": list(self.required_probe_inventory),
            "probe_results": probes,
            "dependency_edges": [list(edge) for edge in self.dependency_edges],
            "cross_probe_adjudication": {
                "rule": "required_probe_conjunction",
                "authority_scope": "scenario_only",
            },
            "scenario_disposition": "PASS" if all(row.status in {"PASS", "NOT_APPLICABLE"} for row in self.probe_results) else "FAIL",
        }

    def deterministic_bytes(self) -> bytes:
        return canonical_bytes(self.deterministic_core())

    def to_report(self) -> dict[str, Any]:
        return {
            "schema_version": "iris_test_workflow_scenario_report_v1",
            "deterministic_core": self.deterministic_core(),
            "execution_observations": thaw(self.execution_observations),
            "normalization_excluded_fields": [],
        }
