from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Callable

try:
    from . import public_text_quality_acceptance as ptqa
except ImportError:
    import public_text_quality_acceptance as ptqa


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]

CONTRACT_ID = "iar_public_text_assessment_v1"
SYNC_CONTRACT_ID = "iris_iar_naturalization_parallel_execution_sync_v3"
SYNC_PROJECTION_SHA256 = (
    "984415c349444dd90ed966490c7619cf32077525276d07616c5698051197b0e8"
)
INPUT_SCHEMA_VERSION = "iar_public_text_assessment_input_v1"
RESULT_SCHEMA_VERSION = "iar_public_text_assessment_result_v1"
EXECUTION_ERROR_SCHEMA_VERSION = "iar_public_text_assessment_execution_error_v1"
CONTRACT_SCHEMA_VERSION = "iar_public_text_assessment_contract_v1"
RESULT_HASH_ALGORITHM = "sha256_canonical_json_without_result_hash_v1"
RAW_IDENTITY_ALGORITHM = "sha256_raw_bytes_v1"
TEXT_IDENTITY_ALGORITHM = ptqa.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID

DEFAULT_CONTRACT_PATH = (
    V2_ROOT
    / "data"
    / "iar_public_text_assessment"
    / "iar_public_text_assessment_contract.json"
)

SUBJECT_KIND_PATTERN = re.compile(r"^(?:dvf|qg)_[a-z0-9][a-z0-9_]*$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

SUBJECT_FAILURE_DOMAINS = ("source", "facts", "compiler", "candidate")
TECHNICAL_FAILURE_DOMAINS = ("iar", "environment", "orchestration")
ALL_FAILURE_DOMAINS = (*SUBJECT_FAILURE_DOMAINS, *TECHNICAL_FAILURE_DOMAINS)


@dataclass(frozen=True)
class AssessmentFailure(RuntimeError):
    domain: str
    code: str
    detail: str

    def __str__(self) -> str:
        return f"{self.domain}:{self.code}:{self.detail}"


def _fail(domain: str, code: str, detail: str) -> None:
    if domain not in ALL_FAILURE_DOMAINS:
        raise AssertionError(f"invalid assessment failure domain: {domain}")
    raise AssessmentFailure(domain=domain, code=code, detail=detail)


def _require_sha256(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
        _fail("iar", "invalid_sha256", label)
    return value


def _require_exact_keys(
    value: Any,
    *,
    expected: tuple[str, ...],
    label: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("iar", "schema_type_mismatch", label)
    if set(value) != set(expected):
        _fail("iar", "schema_key_mismatch", label)
    return value


def _repo_path(value: Any, *, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        _fail("iar", "non_posix_repository_path", label)
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        _fail("iar", "repository_path_escape", label)
    path = REPO_ROOT.joinpath(*pure.parts)
    try:
        contained = path.resolve().is_relative_to(REPO_ROOT.resolve())
    except OSError:
        _fail("environment", "repository_path_unresolvable", label)
    if not contained:
        _fail("iar", "repository_path_escape", label)
    return path


def _portable_repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        _fail("iar", "artifact_outside_repository", path.name)
    raise AssertionError("unreachable")


def _load_json(path: Path, *, label: str) -> Any:
    try:
        return ptqa.load_json_strict(path)
    except FileNotFoundError:
        _fail("environment", "missing_artifact", label)
    except PermissionError:
        _fail("environment", "unreadable_artifact", label)
    except (json.JSONDecodeError, ptqa.FoundationContractError):
        _fail("iar", "invalid_json_artifact", label)
    except OSError:
        _fail("environment", "unreadable_artifact", label)
    raise AssertionError("unreachable")


def _verify_artifact_record(
    record: Any,
    *,
    label: str,
) -> tuple[Path, dict[str, Any]]:
    row = _require_exact_keys(
        record,
        expected=("path", "sha256", "identity_algorithm"),
        label=label,
    )
    path = _repo_path(row["path"], label=f"{label}.path")
    expected_hash = _require_sha256(row["sha256"], label=f"{label}.sha256")
    algorithm = row["identity_algorithm"]
    if not path.is_file():
        _fail("environment", "missing_artifact", label)
    try:
        if algorithm == RAW_IDENTITY_ALGORITHM:
            actual_hash = ptqa.sha256_file(path)
            if actual_hash != expected_hash:
                _fail("environment", "raw_hash_mismatch", label)
            identity = {
                "path": _portable_repo_path(path),
                "sha256": expected_hash,
                "identity_algorithm": algorithm,
                "identity_status": "PASS",
            }
        elif algorithm == TEXT_IDENTITY_ALGORITHM:
            # This is the existing Foundation text-constituent identity contract.
            existing = ptqa._head_text_constituent_record(path, expected_hash)
            if existing.get("match") is not True:
                _fail("environment", "text_identity_mismatch", label)
            identity = {
                "path": _portable_repo_path(path),
                "sha256": expected_hash,
                "identity_algorithm": algorithm,
                "identity_status": "PASS",
                "authority_git_blob_raw_sha256": existing[
                    "authority_git_blob_raw_sha256"
                ],
                "authority_lf_canonical_sha256": existing[
                    "authority_lf_canonical_sha256"
                ],
                "working_lf_canonical_sha256": existing[
                    "working_lf_canonical_sha256"
                ],
                "declared_representation_kinds": existing[
                    "declared_representation_kinds"
                ],
            }
        else:
            _fail("iar", "unknown_identity_algorithm", label)
    except ptqa.FoundationContractError:
        _fail("environment", "text_identity_mismatch", label)
    return path, identity


def load_contract(path: Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_json(path, label="assessment_contract")
    _require_exact_keys(
        contract,
        expected=(
            "schema_version",
            "assessment_input_hash_algorithm",
            "contract_hash_algorithm",
            "contract_id",
            "contract_version",
            "synchronization_contract_id",
            "synchronization_projection_sha256",
            "input_schema_version",
            "result_schema_version",
            "result_hash_algorithm",
            "supported_identity_algorithms",
            "supported_metric_sources",
            "supported_policy_schemas",
            "failure_attribution_domains",
            "metric_failure_attribution",
            "forbidden_dependencies",
            "authority_effect",
        ),
        label="assessment_contract",
    )
    expected_scalars = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "assessment_input_hash_algorithm": "sha256_canonical_json_v1",
        "contract_hash_algorithm": "sha256_canonical_json_v1",
        "contract_id": CONTRACT_ID,
        "contract_version": "1.0.0",
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "synchronization_projection_sha256": SYNC_PROJECTION_SHA256,
        "input_schema_version": INPUT_SCHEMA_VERSION,
        "result_schema_version": RESULT_SCHEMA_VERSION,
        "result_hash_algorithm": RESULT_HASH_ALGORITHM,
        "authority_effect": "none",
    }
    for key, expected in expected_scalars.items():
        if contract.get(key) != expected:
            _fail("iar", "contract_scalar_mismatch", key)
    if contract.get("supported_identity_algorithms") != [
        RAW_IDENTITY_ALGORITHM,
        TEXT_IDENTITY_ALGORITHM,
    ]:
        _fail("iar", "identity_algorithm_contract_mismatch", "contract")
    if contract.get("supported_metric_sources") != [
        "bound_metric_evidence_manifest_v1",
        "naturalization_handoff_v1",
    ]:
        _fail("iar", "metric_source_contract_mismatch", "contract")
    if contract.get("supported_policy_schemas") != [
        "public_text_quality_foundation_contract_v2",
        "public_text_quality_acceptance_policy_candidate_v1",
        "public_text_quality_acceptance_policy_v1",
    ]:
        _fail("iar", "policy_schema_contract_mismatch", "contract")
    domains = contract.get("failure_attribution_domains")
    if domains != {
        "subject_defect": list(SUBJECT_FAILURE_DOMAINS),
        "technical_failure": list(TECHNICAL_FAILURE_DOMAINS),
    }:
        _fail("iar", "failure_domain_contract_mismatch", "contract")
    attribution = contract.get("metric_failure_attribution")
    if not isinstance(attribution, dict) or any(
        value not in SUBJECT_FAILURE_DOMAINS for value in attribution.values()
    ):
        _fail("iar", "metric_attribution_contract_mismatch", "contract")
    forbidden = contract.get("forbidden_dependencies")
    if forbidden != [
        "attempt_id",
        "owner_input_or_seal",
        "transaction_or_live_adoption_receipt",
        "freeze_or_terminal",
        "session_specific_handoff",
    ]:
        _fail("iar", "forbidden_dependency_contract_mismatch", "contract")
    return contract


def _load_input(path: Path) -> dict[str, Any]:
    value = _load_json(path, label="assessment_input")
    row = _require_exact_keys(
        value,
        expected=(
            "schema_version",
            "contract_id",
            "subject",
            "policy",
            "applicable_metrics",
            "metric_source",
            "human_review_result",
            "authority_effect",
        ),
        label="assessment_input",
    )
    if row["schema_version"] != INPUT_SCHEMA_VERSION:
        _fail("iar", "input_schema_mismatch", "assessment_input")
    if row["contract_id"] != CONTRACT_ID:
        _fail("iar", "input_contract_mismatch", "assessment_input")
    if row["authority_effect"] != "none":
        _fail("iar", "authority_effect_mismatch", "assessment_input")
    forbidden_keys = {
        "attempt_id",
        "owner_input",
        "owner_seal",
        "transaction",
        "live_adoption_receipt",
        "freeze",
        "terminal",
        "handoff_output",
    }

    def walk(child: Any) -> None:
        if isinstance(child, dict):
            if forbidden_keys.intersection(child):
                _fail("iar", "forbidden_attempt_governance_dependency", "input")
            for nested in child.values():
                walk(nested)
        elif isinstance(child, list):
            for nested in child:
                walk(nested)

    walk(row)
    return row


def _subject_records(
    input_value: dict[str, Any],
) -> tuple[dict[str, Any], Path, Path, dict[str, Any], dict[str, Any]]:
    subject = _require_exact_keys(
        input_value["subject"],
        expected=(
            "kind",
            "path",
            "sha256",
            "identity_algorithm",
            "manifest_path",
            "manifest_sha256",
            "manifest_identity_algorithm",
        ),
        label="subject",
    )
    kind = subject.get("kind")
    if not isinstance(kind, str) or not SUBJECT_KIND_PATTERN.fullmatch(kind):
        _fail("iar", "unsupported_subject_kind", "subject.kind")
    subject_path, subject_identity = _verify_artifact_record(
        {
            "path": subject["path"],
            "sha256": subject["sha256"],
            "identity_algorithm": subject["identity_algorithm"],
        },
        label="subject",
    )
    manifest_path, manifest_identity = _verify_artifact_record(
        {
            "path": subject["manifest_path"],
            "sha256": subject["manifest_sha256"],
            "identity_algorithm": subject["manifest_identity_algorithm"],
        },
        label="subject_manifest",
    )
    return subject, subject_path, manifest_path, subject_identity, manifest_identity


def _policy_projection(
    input_value: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    policy = _require_exact_keys(
        input_value["policy"],
        expected=(
            "path",
            "sha256",
            "identity_algorithm",
            "ruleset_id",
            "ruleset_sha256",
        ),
        label="policy",
    )
    policy_path, policy_identity = _verify_artifact_record(
        {
            "path": policy["path"],
            "sha256": policy["sha256"],
            "identity_algorithm": policy["identity_algorithm"],
        },
        label="policy",
    )
    policy_document = _load_json(policy_path, label="policy")
    schema = policy_document.get("schema_version")
    if schema == ptqa.FOUNDATION_SCHEMA_VERSION:
        projection = policy_document.get("policy_candidate")
        registry_rows = policy_document.get("metric_registry_candidate", {}).get(
            "registrations"
        )
    elif schema == "public_text_quality_acceptance_policy_candidate_v1":
        projection = policy_document
        registry_rows = None
    elif schema == "public_text_quality_acceptance_policy_v1":
        projection = policy_document.get("policy_projection")
        registry_rows = None
    else:
        _fail("iar", "unsupported_policy_schema", str(schema))
    if not isinstance(projection, dict):
        _fail("iar", "missing_policy_projection", "policy")
    ruleset_id = policy.get("ruleset_id")
    ruleset = projection.get(ruleset_id)
    if not isinstance(ruleset, dict) or not ruleset:
        _fail("iar", "missing_policy_ruleset", str(ruleset_id))
    ruleset_sha = ptqa.canonical_hash(ruleset)
    if ruleset_sha != _require_sha256(
        policy.get("ruleset_sha256"), label="policy.ruleset_sha256"
    ):
        _fail("iar", "policy_ruleset_hash_mismatch", str(ruleset_id))
    registry: dict[str, dict[str, Any]] = {}
    if registry_rows is not None:
        if not isinstance(registry_rows, list):
            _fail("iar", "invalid_metric_registry", "policy")
        for row in registry_rows:
            if not isinstance(row, dict) or not isinstance(row.get("metric_id"), str):
                _fail("iar", "invalid_metric_registry", "policy")
            if row["metric_id"] in registry:
                _fail("iar", "duplicate_metric_registration", row["metric_id"])
            registry[row["metric_id"]] = row
    return policy, ruleset, registry, policy_identity


def _validate_metric_rows(rows: Any, *, label: str) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or not rows:
        _fail("iar", "empty_metric_rows", label)
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, value in enumerate(rows):
        row = _require_exact_keys(
            value,
            expected=(
                "metric_id",
                "denominator_id",
                "disposition_class",
                "numerator",
                "denominator",
                "exact_ratio",
            ),
            label=f"{label}[{index}]",
        )
        metric_id = row.get("metric_id")
        denominator_id = row.get("denominator_id")
        numerator = row.get("numerator")
        denominator = row.get("denominator")
        if not isinstance(metric_id, str) or not metric_id or metric_id in seen:
            _fail("iar", "duplicate_or_invalid_metric_id", str(metric_id))
        if not isinstance(denominator_id, str) or not denominator_id:
            _fail("iar", "invalid_denominator_id", metric_id)
        if type(numerator) is not int or numerator < 0:
            _fail("iar", "invalid_metric_numerator", metric_id)
        if type(denominator) is not int or denominator <= 0:
            _fail("iar", "invalid_metric_denominator", metric_id)
        if row.get("disposition_class") not in ptqa.DISPOSITION_CLASSES:
            _fail("iar", "invalid_disposition_class", metric_id)
        if row.get("exact_ratio") != {
            "numerator": numerator,
            "denominator": denominator,
        }:
            _fail("iar", "metric_ratio_mismatch", metric_id)
        seen.add(metric_id)
        validated.append(dict(row))
    return validated


def _metric_rows_from_source(
    input_value: dict[str, Any],
    *,
    subject: dict[str, Any],
    subject_path: Path,
    subject_manifest_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source = _require_exact_keys(
        input_value["metric_source"],
        expected=("adapter", "path", "sha256", "identity_algorithm"),
        label="metric_source",
    )
    source_path, source_identity = _verify_artifact_record(
        {
            "path": source["path"],
            "sha256": source["sha256"],
            "identity_algorithm": source["identity_algorithm"],
        },
        label="metric_source",
    )
    adapter = source.get("adapter")
    if adapter == "bound_metric_evidence_manifest_v1":
        if source_path.resolve() != subject_manifest_path.resolve():
            _fail("iar", "metric_manifest_role_mismatch", "metric_source")
        manifest = _load_json(source_path, label="metric_source")
        _require_exact_keys(
            manifest,
            expected=(
                "schema_version",
                "subject_kind",
                "subject_path",
                "subject_sha256",
                "metric_rows",
            ),
            label="bound_metric_evidence_manifest",
        )
        if manifest.get("schema_version") != "iar_bound_metric_evidence_manifest_v1":
            _fail("iar", "metric_manifest_schema_mismatch", "metric_source")
        if (
            manifest.get("subject_kind") != subject["kind"]
            or manifest.get("subject_path") != subject["path"]
            or manifest.get("subject_sha256") != subject["sha256"]
        ):
            _fail("iar", "metric_manifest_subject_binding_mismatch", "metric_source")
        return _validate_metric_rows(
            manifest.get("metric_rows"), label="metric_source.metric_rows"
        ), source_identity
    if adapter == "naturalization_handoff_v1":
        if subject.get("kind") != "dvf_3_3_korean_naturalization_candidate":
            _fail("iar", "naturalization_adapter_subject_kind_mismatch", "subject")
        try:
            validation = ptqa.validate_candidate_handoff(source_path)
            snapshot = ptqa.compute_candidate_metric_snapshot(validation)
            candidate_path = ptqa._handoff_path(validation, "candidate_rendered_hash")
            candidate_manifest_path = ptqa._handoff_path(
                validation, "candidate_manifest_hash"
            )
        except ptqa.FoundationContractError as exc:
            _fail("iar", "naturalization_evidence_contract_failure", str(exc))
        if candidate_path.resolve() != subject_path.resolve():
            _fail("iar", "naturalization_subject_role_mismatch", "subject")
        if candidate_manifest_path.resolve() != subject_manifest_path.resolve():
            _fail("iar", "naturalization_manifest_role_mismatch", "subject")
        return _validate_metric_rows(
            snapshot.get("metric_rows"), label="naturalization_metric_rows"
        ), source_identity
    _fail("iar", "unsupported_metric_source_adapter", str(adapter))
    raise AssertionError("unreachable")


def _validate_human_review(
    input_value: dict[str, Any],
    *,
    metric_rows: list[dict[str, Any]],
    metric_source_path: Path,
) -> dict[str, Any] | None:
    required = any(
        row["metric_id"] == "human_review_blocker_required_denominator"
        for row in metric_rows
    )
    record = input_value.get("human_review_result")
    if record is None:
        if required:
            _fail("iar", "missing_required_human_review", "human_review_result")
        return None
    path, identity = _verify_artifact_record(record, label="human_review_result")
    if required:
        source = input_value["metric_source"]
        if source.get("adapter") == "naturalization_handoff_v1":
            try:
                validation = ptqa.validate_candidate_handoff(metric_source_path)
                row = validation["constituents"]["human_review_decision_hash"]
            except ptqa.FoundationContractError as exc:
                _fail("iar", "naturalization_evidence_contract_failure", str(exc))
            if (
                _portable_repo_path(path) != row.get("path")
                or record.get("sha256") != row.get("sha256")
            ):
                _fail("iar", "human_review_binding_mismatch", "human_review_result")
    return identity


def _applicable_metric_declarations(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        _fail("iar", "empty_applicable_metrics", "applicable_metrics")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, child in enumerate(value):
        row = _require_exact_keys(
            child,
            expected=("metric_id", "denominator_id", "denominator"),
            label=f"applicable_metrics[{index}]",
        )
        metric_id = row.get("metric_id")
        if not isinstance(metric_id, str) or metric_id in seen:
            _fail("iar", "duplicate_or_invalid_metric_id", str(metric_id))
        if not isinstance(row.get("denominator_id"), str):
            _fail("iar", "invalid_denominator_id", metric_id)
        if type(row.get("denominator")) is not int or row["denominator"] <= 0:
            _fail("iar", "invalid_metric_denominator", metric_id)
        seen.add(metric_id)
        rows.append(dict(row))
    return rows


def build_assessment(
    input_path: Path,
    *,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_contract(contract_path)
    input_value = _load_input(input_path)
    (
        subject,
        subject_path,
        subject_manifest_path,
        subject_identity,
        subject_manifest_identity,
    ) = _subject_records(input_value)
    policy, ruleset, registry, policy_identity = _policy_projection(input_value)
    metric_source_path = _repo_path(
        input_value["metric_source"]["path"], label="metric_source.path"
    )
    metric_rows, metric_source_identity = _metric_rows_from_source(
        input_value,
        subject=subject,
        subject_path=subject_path,
        subject_manifest_path=subject_manifest_path,
    )
    human_review_identity = _validate_human_review(
        input_value,
        metric_rows=metric_rows,
        metric_source_path=metric_source_path,
    )
    declarations = _applicable_metric_declarations(
        input_value["applicable_metrics"]
    )
    actual_declarations = [
        {
            "metric_id": row["metric_id"],
            "denominator_id": row["denominator_id"],
            "denominator": row["denominator"],
        }
        for row in metric_rows
    ]
    if declarations != actual_declarations:
        _fail("iar", "applicable_metric_denominator_mismatch", "applicable_metrics")

    attribution_map = contract["metric_failure_attribution"]
    evaluated_metrics: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for row in metric_rows:
        metric_id = row["metric_id"]
        policy_row = ruleset.get(metric_id)
        if not isinstance(policy_row, dict):
            _fail("iar", "policy_missing_applicable_metric", metric_id)
        if policy_row.get("disposition_class") != row["disposition_class"]:
            _fail("iar", "policy_disposition_mismatch", metric_id)
        registration = registry.get(metric_id)
        if registration is not None and (
            registration.get("denominator_id") != row["denominator_id"]
            or registration.get("disposition_class") != row["disposition_class"]
        ):
            _fail("iar", "metric_registry_mismatch", metric_id)
        attribution = attribution_map.get(metric_id)
        if attribution not in SUBJECT_FAILURE_DOMAINS:
            _fail("iar", "metric_attribution_missing", metric_id)
        try:
            satisfied = ptqa.evaluate_threshold(
                numerator=row["numerator"],
                denominator=row["denominator"],
                threshold=policy_row["threshold"],
            )
        except ptqa.FoundationContractError:
            _fail("iar", "invalid_policy_threshold", metric_id)
        evaluated = {
            **row,
            "threshold": policy_row["threshold"],
            "threshold_satisfied": satisfied,
            "failure_attribution": attribution,
            "raw_metric_mutated": False,
        }
        evaluated_metrics.append(evaluated)
        if not satisfied and row["disposition_class"] != "non_claim":
            findings.append(
                {
                    "metric_id": metric_id,
                    "disposition_class": row["disposition_class"],
                    "numerator": row["numerator"],
                    "denominator": row["denominator"],
                    "threshold": policy_row["threshold"],
                    "failure_attribution": attribution,
                    "finding_kind": "policy_threshold_unsatisfied",
                }
            )

    subject_counts = {domain: 0 for domain in SUBJECT_FAILURE_DOMAINS}
    for finding in findings:
        subject_counts[finding["failure_attribution"]] += 1
    technical_counts = {domain: 0 for domain in TECHNICAL_FAILURE_DOMAINS}
    status = "PASS" if not findings else "FAIL"
    input_sha = ptqa.canonical_hash(input_value)
    contract_sha = ptqa.canonical_hash(contract)
    result_core = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "contract_id": CONTRACT_ID,
        "contract": {
            "path": _portable_repo_path(contract_path),
            "sha256": contract_sha,
            "identity_algorithm": "sha256_canonical_json_v1",
        },
        "assessment_input": {
            "sha256": input_sha,
            "identity_algorithm": "sha256_canonical_json_v1",
        },
        "subject": {
            "kind": subject["kind"],
            "path": subject["path"],
            "sha256": subject["sha256"],
            "identity_algorithm": subject["identity_algorithm"],
            "manifest_path": subject["manifest_path"],
            "manifest_sha256": subject["manifest_sha256"],
            "identity": subject_identity,
            "manifest_identity": subject_manifest_identity,
        },
        "policy": {
            "path": policy["path"],
            "sha256": policy["sha256"],
            "identity_algorithm": policy["identity_algorithm"],
            "ruleset_id": policy["ruleset_id"],
            "ruleset_sha256": policy["ruleset_sha256"],
            "identity": policy_identity,
        },
        "metric_source": {
            "adapter": input_value["metric_source"]["adapter"],
            "identity": metric_source_identity,
        },
        "human_review_result": human_review_identity,
        "metric_count": len(evaluated_metrics),
        "metrics": evaluated_metrics,
        "metric_projection_sha256": ptqa.canonical_hash(evaluated_metrics),
        "structured_findings": findings,
        "finding_count": len(findings),
        "failure_attribution": {
            "subject_defect_counts": subject_counts,
            "technical_failure_counts": technical_counts,
            "temporary_orchestration_failure_count": 0,
        },
        "status": status,
        "result_hash_algorithm": RESULT_HASH_ALGORITHM,
        "authority_effect": "none",
    }
    return {
        **result_core,
        "deterministic_result_hash": ptqa.canonical_hash(result_core),
    }


def materialize_assessment(
    input_path: Path,
    output_path: Path,
    *,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
    writer: Callable[[Path, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    result = build_assessment(input_path, contract_path=contract_path)
    selected_writer = writer or ptqa.write_once_or_same
    try:
        selected_writer(output_path, result)
    except AssessmentFailure:
        raise
    except Exception:
        _fail("orchestration", "result_materialization_failed", output_path.name)
    return result


def validate_assessment(
    input_path: Path,
    result_path: Path,
    *,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    result = _load_json(result_path, label="assessment_result")
    if not isinstance(result, dict):
        _fail("iar", "result_schema_type_mismatch", "assessment_result")
    if result.get("schema_version") != RESULT_SCHEMA_VERSION:
        _fail("iar", "result_schema_mismatch", "assessment_result")
    declared_hash = result.get("deterministic_result_hash")
    _require_sha256(declared_hash, label="deterministic_result_hash")
    result_core = dict(result)
    del result_core["deterministic_result_hash"]
    if ptqa.canonical_hash(result_core) != declared_hash:
        _fail("iar", "result_hash_mismatch", "assessment_result")
    expected = build_assessment(input_path, contract_path=contract_path)
    if result != expected:
        _fail("iar", "deterministic_replay_mismatch", "assessment_result")
    try:
        actual_bytes = result_path.read_bytes()
    except OSError:
        _fail("environment", "unreadable_artifact", "assessment_result")
    if (
        ptqa.normalize_text_line_endings(actual_bytes)
        != ptqa.pretty_json_bytes(expected)
    ):
        _fail("iar", "noncanonical_result_serialization", "assessment_result")
    return {
        "schema_version": "iar_public_text_assessment_validation_v1",
        "status": "PASS",
        "assessment_status": result["status"],
        "subject_kind": result["subject"]["kind"],
        "subject_sha256": result["subject"]["sha256"],
        "policy_sha256": result["policy"]["sha256"],
        "ruleset_sha256": result["policy"]["ruleset_sha256"],
        "metric_count": result["metric_count"],
        "finding_count": result["finding_count"],
        "deterministic_result_hash": declared_hash,
        "no_write": True,
        "authority_effect": "none",
    }


def execution_error_payload(failure: AssessmentFailure) -> dict[str, Any]:
    subject_counts = {domain: 0 for domain in SUBJECT_FAILURE_DOMAINS}
    technical_counts = {domain: 0 for domain in TECHNICAL_FAILURE_DOMAINS}
    if failure.domain in subject_counts:
        subject_counts[failure.domain] = 1
    else:
        technical_counts[failure.domain] = 1
    core = {
        "schema_version": EXECUTION_ERROR_SCHEMA_VERSION,
        "contract_id": CONTRACT_ID,
        "status": "FAIL",
        "assessment_completed": False,
        "failure_attribution": {
            "domain": failure.domain,
            "code": failure.code,
            "subject_defect_counts": subject_counts,
            "technical_failure_counts": technical_counts,
            "temporary_orchestration_failure_count": (
                1 if failure.domain == "orchestration" else 0
            ),
        },
        "authority_effect": "none",
    }
    return {**core, "deterministic_error_hash": ptqa.canonical_hash(core)}
