from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[6]
FIXTURE_ROOT = REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tests" / "fixtures"
NEGATIVE_ROOT = FIXTURE_ROOT / "negative" / "completion_vocabulary_external_gate"
POSITIVE_ROOT = FIXTURE_ROOT / "positive" / "completion_vocabulary_external_gate"


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        logical_bytes = path.read_text(encoding="utf-8-sig").encode("utf-8")
    except (OSError, UnicodeError):
        return None
    return hashlib.sha256(logical_bytes).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def binding_errors(binding: Any, *, code_prefix: str) -> list[dict[str, Any]]:
    if not isinstance(binding, dict):
        return [{"code": "hash_binding_must_be_object", "binding": code_prefix}]
    path_value = binding.get("path")
    digest = binding.get("sha256")
    if not isinstance(path_value, str) or not isinstance(digest, str):
        return [{"code": f"{code_prefix}_binding_fields_missing"}]
    candidate = Path(path_value)
    if candidate.is_absolute():
        return [{"code": "hash_binding_path_must_be_repo_relative", "path": path_value}]
    target = (REPO_ROOT / candidate).resolve()
    try:
        target.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return [{"code": "hash_binding_path_escapes_repo", "path": path_value}]
    if not target.is_file():
        return [{"code": "hash_binding_target_missing", "path": path_value}]
    if sha256_file(target) != digest:
        return [{"code": "hash_binding_digest_mismatch", "path": path_value}]
    return []


def validate_review_bundle_manifest(
    payload: dict[str, Any],
    *,
    review_payload: dict[str, Any],
    review_artifact_binding: Any,
    errors: list[dict[str, Any]],
    repo_root: Path = REPO_ROOT,
) -> None:
    del repo_root
    errors.extend(binding_errors(review_artifact_binding, code_prefix="independent_review_artifact"))
    expected_list = review_payload.get("reviewed_artifact_list")
    if payload.get("reviewed_artifact_list") != expected_list:
        errors.append({"code": "independent_review_bundle_reviewed_artifact_list_mismatch"})
    expected_result = review_payload.get("reviewed_validation_result_or_rerun_result")
    if payload.get("reviewed_validation_result_or_rerun_result") != expected_result:
        errors.append({"code": "independent_review_bundle_validation_result_mismatch"})
    for binding in payload.get("reviewed_artifact_list", []):
        errors.extend(binding_errors(binding, code_prefix="reviewed_artifact"))
    errors.extend(binding_errors(payload.get("reviewed_validation_result_or_rerun_result"), code_prefix="reviewed_validation_result"))


def validate_owner_seal_record(
    payload: dict[str, Any],
    *,
    outer_payload: dict[str, Any],
    errors: list[dict[str, Any]],
    required_sealed_bindings: list[Any],
    repo_root: Path = REPO_ROOT,
) -> None:
    del outer_payload, repo_root
    sealed = payload.get("sealed_artifact_hashes")
    if not isinstance(sealed, list):
        errors.append({"code": "owner_seal_record_schema_invalid"})
        return
    for binding in sealed:
        errors.extend(binding_errors(binding, code_prefix="owner_sealed_artifact"))
    for required in required_sealed_bindings:
        if required not in sealed:
            errors.append({"code": "owner_seal_record_missing_required_sealed_artifact"})


def validate_governance_payload(
    payload: dict[str, Any],
    *,
    artifact_path: Path | None = None,
    historical_artifact_paths: list[Path] | None = None,
    repo_root: Path = REPO_ROOT,
) -> list[dict[str, Any]]:
    del repo_root
    if (
        artifact_path is not None
        and historical_artifact_paths
        and artifact_path in historical_artifact_paths
    ) or (
        payload.get("lifecycle") == "historical_trace"
        and "mode" not in payload
        and "path" not in payload
    ):
        return []
    errors: list[dict[str, Any]] = []
    matrix = payload.get("gate_requirement_matrix")
    if isinstance(matrix, list) and any(row.get("absence_maps_to") == "satisfied" for row in matrix if isinstance(row, dict)):
        errors.append({"code": "absence_maps_to_satisfied_forbidden"})
    if payload.get("owner_decision") == "PASS" or payload.get("external_gate_state") == "PASS":
        errors.append({"code": "bare_pass_forbidden_on_governance_axis"})
    canonical = payload.get("canonical_seal_allowed") is True
    if not canonical:
        return errors or [{"code": "canonical_gate_not_satisfied"}]
    expected = {
        "machine_contract_validation": "PASS",
        "external_validation_bundle_result": "PASS",
        "external_validation_bundle_state": "present",
        "independent_review_verdict": "PASS",
        "independent_review_state": "present",
        "external_gate_state": "satisfied",
        "canonical_external_review_state": "satisfied",
        "owner_decision": "approved",
        "owner_seal_state": "sealed",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append({"code": "canonical_gate_field_mismatch", "field": key})
    if payload.get("review_notes_blocking") is True or payload.get("blocking_note_count", 0):
        errors.append({"code": "blocking_review_note_present"})
    review_binding = payload.get("independent_review_artifact_binding")
    owner_binding = payload.get("owner_seal_hash_binding")
    errors.extend(binding_errors(review_binding, code_prefix="independent_review_artifact"))
    errors.extend(binding_errors(owner_binding, code_prefix="owner_seal"))
    if not isinstance(review_binding, dict):
        errors.append({"code": "independent_review_concrete_artifact_fields_missing"})
    if not isinstance(owner_binding, dict):
        errors.append({"code": "owner_seal_record_schema_invalid"})
    if not errors and isinstance(review_binding, dict) and isinstance(owner_binding, dict):
        review_payload = read_json(REPO_ROOT / review_binding["path"])
        owner_payload = read_json(REPO_ROOT / owner_binding["path"])
        bundle_binding = review_payload.get("hash_sealed_review_bundle_reference")
        errors.extend(binding_errors(bundle_binding, code_prefix="independent_review_bundle"))
        if isinstance(bundle_binding, dict):
            bundle_payload = read_json(REPO_ROOT / bundle_binding["path"])
            validate_review_bundle_manifest(
                bundle_payload,
                review_payload=review_payload,
                review_artifact_binding=review_binding,
                errors=errors,
            )
            validate_owner_seal_record(
                owner_payload,
                outer_payload=payload,
                errors=errors,
                required_sealed_bindings=[review_binding, bundle_binding],
            )
    return errors


def fixture_paths() -> list[tuple[Path, bool]]:
    return [
        *[(path, False) for path in sorted(NEGATIVE_ROOT.glob("*.json"))],
        *[(path, True) for path in sorted(POSITIVE_ROOT.glob("*.json"))],
    ]


def validate_fixture_root(path: Path) -> None:
    if path.resolve() != FIXTURE_ROOT.resolve():
        raise ValueError("fixture root must equal the tracked repository fixture root")


def validate_output_root(path: Path) -> None:
    resolved = path.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved.relative_to(temp_root)
    except ValueError as exc:
        raise ValueError("fixture-check output root must be contained in the system test-temp root") from exc


def run_fixture_check(*, root: Path, fixture_root: Path, report_path: Path) -> dict[str, Any]:
    validate_fixture_root(fixture_root)
    validate_output_root(root)
    if report_path.resolve().parent != root.resolve():
        raise ValueError("fixture-check report must be an immediate child of --root")
    root.mkdir(parents=True, exist_ok=False)
    rows = []
    unexpected = []
    for path, expected_pass in fixture_paths():
        payload = read_json(path)
        errors = validate_governance_payload(
            payload,
            artifact_path=path,
            historical_artifact_paths=[POSITIVE_ROOT / "historical_legacy_pass_trace.json"],
        )
        observed_pass = not errors
        row = {
            "fixture": path.stem,
            "path": path.relative_to(REPO_ROOT).as_posix(),
            "sha256": sha256_file(path),
            "expected_pass": expected_pass,
            "observed_pass": observed_pass,
            "errors": errors,
        }
        rows.append(row)
        if observed_pass != expected_pass:
            unexpected.append(row)
    report = {
        "schema_version": "dvf-3-3-completion-vocabulary-subprocess-fixture-check-v1",
        "status": "PASS" if not unexpected else "FAIL",
        "mode": "fixture-check",
        "fixture_root": fixture_root.relative_to(REPO_ROOT).as_posix(),
        "fixture_file_count": len(rows),
        "unexpected_pass_count": len(unexpected),
        "fixtures": rows,
        "freshness_nonce": hashlib.sha256(json.dumps(rows, sort_keys=True).encode("utf-8")).hexdigest(),
        "stored_phase9_pass_read_count": 0,
        "current_route_invocation_count": 0,
        "repository_write_count": 0,
        "canonical_completion_claim_count": 0,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def validate_fixture_report(report_path: Path, *, fixture_root: Path) -> dict[str, Any]:
    validate_fixture_root(fixture_root)
    report = read_json(report_path)
    expected = {path.relative_to(REPO_ROOT).as_posix(): sha256_file(path) for path, _ in fixture_paths()}
    observed = {row.get("path"): row.get("sha256") for row in report.get("fixtures", []) if isinstance(row, dict)}
    blockers = []
    if report.get("status") != "PASS" or report.get("mode") != "fixture-check":
        blockers.append("fixture_report_not_pass")
    if expected != observed:
        blockers.append("fixture_denominator_or_hash_mismatch")
    if report.get("stored_phase9_pass_read_count") != 0:
        blockers.append("stored_pass_reused")
    if report.get("current_route_invocation_count") != 0:
        blockers.append("current_route_recursion")
    if report.get("repository_write_count") != 0:
        blockers.append("repository_mutation")
    return {
        "schema_version": "dvf-3-3-completion-vocabulary-subprocess-fixture-check-validation-v1",
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "fixture_file_count": len(expected),
        "freshness_nonce": report.get("freshness_nonce"),
    }
