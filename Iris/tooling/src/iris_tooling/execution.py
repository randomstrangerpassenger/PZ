from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
import hashlib
import json
import sys
import time
from typing import Any, Generic, TypeVar, cast


TDomain = TypeVar("TDomain")
TResult = TypeVar("TResult")

CANONICAL_RESULT_SCHEMA = "iris-tooling-canonical-semantic-result-v1"
EXECUTION_ENVELOPE_SCHEMA = "iris-tooling-execution-envelope-v1"
MACHINE_RESULT_SCHEMA = "iris-tooling-machine-result-v1"


class ResultContractError(ValueError):
    """Raised when a public result has an unknown or malformed identity."""


class TerminalStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class Issue:
    code: str
    message: str
    phase: str
    severity: Severity
    failure_identity: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "phase": self.phase,
            "severity": self.severity.value,
            "failure_identity": self.failure_identity,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> Issue:
        try:
            return cls(
                code=str(value["code"]),
                message=str(value["message"]),
                phase=str(value["phase"]),
                severity=Severity(value["severity"]),
                failure_identity=str(value["failure_identity"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ResultContractError(f"invalid Issue payload: {exc}") from exc


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    role: str
    locator: str
    content_sha256: str

    def __post_init__(self) -> None:
        if len(self.content_sha256) != 64 or any(
            character not in "0123456789abcdef" for character in self.content_sha256
        ):
            raise ResultContractError("artifact content_sha256 must be lowercase SHA-256")

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "locator": self.locator,
            "content_sha256": self.content_sha256,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ArtifactRef:
        try:
            return cls(
                role=str(value["role"]),
                locator=str(value["locator"]),
                content_sha256=str(value["content_sha256"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ResultContractError(f"invalid ArtifactRef payload: {exc}") from exc


@dataclass(frozen=True, slots=True)
class PhaseInput(Generic[TDomain]):
    phase: str
    payload: TDomain
    dependencies: tuple[str, ...] = ()
    reuse_key: str | None = None


@dataclass(frozen=True, slots=True)
class PhaseOutput(Generic[TDomain]):
    phase: str
    status: TerminalStatus
    payload: TDomain
    issues: tuple[Issue, ...] = ()
    artifacts: tuple[ArtifactRef, ...] = ()
    elapsed_seconds: float = field(default=0.0, compare=False)
    reused: bool = field(default=False, compare=False)


@dataclass(frozen=True, slots=True)
class CanonicalSemanticResult(Generic[TDomain]):
    discriminator: str
    status: TerminalStatus
    payload: TDomain
    issues: tuple[Issue, ...] = ()
    artifacts: tuple[ArtifactRef, ...] = ()
    schema_version: str = CANONICAL_RESULT_SCHEMA

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "discriminator": self.discriminator,
            "status": self.status.value,
            "payload": self.payload,
            "issues": [issue.to_dict() for issue in self.issues],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }

    def canonical_bytes(self) -> bytes:
        return (
            json.dumps(
                self.to_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any],
        *,
        expected_discriminator: str,
    ) -> CanonicalSemanticResult[Any]:
        schema = value.get("schema_version")
        discriminator = value.get("discriminator")
        if schema != CANONICAL_RESULT_SCHEMA:
            raise ResultContractError(f"unsupported canonical result schema: {schema!r}")
        if discriminator != expected_discriminator:
            raise ResultContractError(
                f"unsupported canonical result discriminator: {discriminator!r}"
            )
        try:
            issues = tuple(Issue.from_dict(row) for row in value.get("issues", ()))
            artifacts = tuple(
                ArtifactRef.from_dict(row) for row in value.get("artifacts", ())
            )
            return cls(
                discriminator=expected_discriminator,
                status=TerminalStatus(value["status"]),
                payload=value["payload"],
                issues=issues,
                artifacts=artifacts,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ResultContractError(f"invalid canonical result payload: {exc}") from exc


@dataclass(frozen=True, slots=True)
class ExecutionEnvelope:
    run_id: str
    elapsed_seconds: float
    observed_at: str
    process: Mapping[str, Any]
    environment: Mapping[str, Any]
    canonical_result_sha256: str
    canonical_result_locator: str
    schema_version: str = EXECUTION_ENVELOPE_SCHEMA

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "elapsed_seconds": self.elapsed_seconds,
            "observed_at": self.observed_at,
            "process": dict(self.process),
            "environment": dict(self.environment),
            "canonical_result_sha256": self.canonical_result_sha256,
            "canonical_result_locator": self.canonical_result_locator,
        }


@dataclass(frozen=True, slots=True)
class MachineResult:
    exit_code: int
    canonical_result_sha256: str
    canonical_result_locator: str
    execution_envelope_locator: str
    schema_version: str = MACHINE_RESULT_SCHEMA

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "exit_code": self.exit_code,
            "canonical_result_sha256": self.canonical_result_sha256,
            "canonical_result_locator": self.canonical_result_locator,
            "execution_envelope_locator": self.execution_envelope_locator,
        }


def terminal_exit_code(status: TerminalStatus) -> int:
    return {TerminalStatus.PASS: 0, TerminalStatus.FAIL: 1, TerminalStatus.BLOCKED: 2}[
        status
    ]


def exception_issue(exc: BaseException, *, phase: str) -> Issue:
    identity_source = f"{type(exc).__module__}.{type(exc).__qualname__}:{exc}"
    return Issue(
        code="unhandled_exception",
        message=str(exc) or type(exc).__qualname__,
        phase=phase,
        severity=Severity.ERROR,
        failure_identity=hashlib.sha256(identity_source.encode("utf-8")).hexdigest(),
    )


def emit_machine_result(result: MachineResult, *, diagnostic: str | None = None) -> None:
    if diagnostic:
        print(diagnostic, file=sys.stderr)
    print(
        json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )


class PhaseRunner:
    """Thin dependency, run-local reuse, metric, issue, and artifact coordinator."""

    def __init__(self) -> None:
        self._outputs: dict[str, PhaseOutput[Any]] = {}
        self._reuse: dict[str, PhaseOutput[Any]] = {}

    @property
    def outputs(self) -> Mapping[str, PhaseOutput[Any]]:
        return dict(self._outputs)

    def run_phase(
        self,
        phase_input: PhaseInput[TDomain],
        action: Callable[[TDomain], TResult],
        *,
        failed: Callable[[TResult], bool] | None = None,
    ) -> PhaseOutput[TResult]:
        missing = [
            dependency
            for dependency in phase_input.dependencies
            if dependency not in self._outputs
            or self._outputs[dependency].status is not TerminalStatus.PASS
        ]
        if missing:
            issue = Issue(
                code="phase_dependency_unsatisfied",
                message=f"unsatisfied dependencies: {', '.join(missing)}",
                phase=phase_input.phase,
                severity=Severity.ERROR,
                failure_identity="|".join(missing),
            )
            output = PhaseOutput(
                phase=phase_input.phase,
                status=TerminalStatus.BLOCKED,
                payload=cast(TResult, None),
                issues=(issue,),
            )
            self._outputs[phase_input.phase] = output
            return output
        if phase_input.reuse_key is not None and phase_input.reuse_key in self._reuse:
            reused = self._reuse[phase_input.reuse_key]
            output = PhaseOutput(
                phase=phase_input.phase,
                status=reused.status,
                payload=cast(TResult, reused.payload),
                issues=reused.issues,
                artifacts=reused.artifacts,
                reused=True,
            )
            self._outputs[phase_input.phase] = output
            return output

        started = time.perf_counter()
        try:
            payload = action(phase_input.payload)
            status = TerminalStatus.FAIL if failed and failed(payload) else TerminalStatus.PASS
            issues: tuple[Issue, ...] = ()
        except Exception as exc:
            payload = cast(TResult, None)
            status = TerminalStatus.BLOCKED
            issues = (exception_issue(exc, phase=phase_input.phase),)
        output = PhaseOutput(
            phase=phase_input.phase,
            status=status,
            payload=payload,
            issues=issues,
            elapsed_seconds=time.perf_counter() - started,
        )
        self._outputs[phase_input.phase] = output
        if phase_input.reuse_key is not None:
            self._reuse[phase_input.reuse_key] = output
        return output

    def run(
        self,
        action: Callable[[], TResult],
        *,
        failed: Callable[[TResult], bool] | None = None,
        abort_message: str | None = None,
    ) -> tuple[TResult, bool]:
        result = action()
        ok = not failed(result) if failed else True
        if not ok and abort_message:
            print(f"\n{abort_message}", file=sys.stderr)
        return result, ok


def decode_legacy_result(
    value: Mapping[str, Any], *, discriminator: str
) -> CanonicalSemanticResult[Any]:
    legacy_status = str(value["status"])
    if legacy_status == "PASS":
        status = TerminalStatus.PASS
    elif legacy_status == "FAIL":
        status = TerminalStatus.FAIL
    else:
        status = TerminalStatus.BLOCKED
    payload = {
        "legacy_status": legacy_status,
        "data": {key: item for key, item in value.items() if key != "status"},
    }
    return CanonicalSemanticResult(
        discriminator=discriminator,
        status=status,
        payload=payload,
    )


def encode_legacy_result(result: CanonicalSemanticResult[Mapping[str, Any]]) -> dict[str, Any]:
    payload = dict(result.payload)
    if set(payload) == {"legacy_status", "data"} and isinstance(
        payload["data"], Mapping
    ):
        return {"status": payload["legacy_status"], **dict(payload["data"])}
    return {"status": result.status.value, **payload}


__all__: Sequence[str] = (
    "ArtifactRef",
    "CANONICAL_RESULT_SCHEMA",
    "CanonicalSemanticResult",
    "ExecutionEnvelope",
    "Issue",
    "MachineResult",
    "PhaseInput",
    "PhaseOutput",
    "PhaseRunner",
    "ResultContractError",
    "Severity",
    "TerminalStatus",
    "decode_legacy_result",
    "emit_machine_result",
    "encode_legacy_result",
    "exception_issue",
    "terminal_exit_code",
)
