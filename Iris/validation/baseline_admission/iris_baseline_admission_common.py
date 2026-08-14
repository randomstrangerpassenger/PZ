"""Shared primitives for the Iris validation-baseline admission boundary.

This module deliberately owns only validation evidence.  It never changes Iris
runtime, current-required manifests, or tracked evidence surfaces.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


S_BASE_COMMIT = "671c7b928ad5a1dbf26ea76949462fa8a7287903"
S_BASE_TREE = "20bbbdb919fa97a44e03c1f1cb9ea0a6973fb1db"
CONTEXT = "composite_baseline_admission_chain_stage_6"


@dataclass(frozen=True)
class AdmissionError(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_bytes(value)
    path.write_bytes(data)
    return sha256_bytes(data)


def read_json(path: Path, *, code: str = "receipt_unreadable") -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdmissionError(code, f"cannot read JSON: {path}") from exc
    if not isinstance(result, dict):
        raise AdmissionError(code, f"JSON root must be an object: {path}")
    return result


def repo_identity(repo: Path, revision: str = "HEAD") -> dict[str, str]:
    def git(*args: str) -> str:
        completed = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            raise AdmissionError("subject_identity_unavailable", completed.stderr.strip() or "git identity lookup failed")
        return completed.stdout.strip()

    commit = git("rev-parse", revision)
    tree = git("rev-parse", f"{commit}^{{tree}}")
    return {"commit": commit, "tree": tree}


def clean_worktree(repo: Path) -> bool:
    completed = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"],
        text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise AdmissionError("working_tree_state_unavailable", completed.stderr.strip())
    return not completed.stdout.strip()


def require_external(repo: Path, value: Path, label: str) -> Path:
    resolved_repo = repo.resolve()
    resolved = value.resolve()
    try:
        resolved.relative_to(resolved_repo)
    except ValueError:
        return resolved
    raise AdmissionError("durable_root_inside_subject_checkout", f"{label} must be repository-external: {resolved}")


def path_preflight(contract: dict[str, Any], checkout_root: Path) -> dict[str, Any]:
    budget = contract.get("budget")
    if not isinstance(budget, dict):
        raise AdmissionError("windows_path_contract_invalid", "budget is missing")
    required = ("longest_required_relative_path", "worst_case_generated_suffix", "separator_allowance", "safety_margin", "qualified_materialized_path_limit")
    try:
        values = {key: int(budget[key]) for key in required}
    except (KeyError, TypeError, ValueError) as exc:
        raise AdmissionError("windows_path_contract_invalid", "budget values are incomplete") from exc
    materialized = len(str(checkout_root)) + sum(values[key] for key in required[:-1])
    accepted = materialized <= values["qualified_materialized_path_limit"]
    return {
        "status": "PASS" if accepted else "REJECTED",
        "failure_code": None if accepted else "windows_path_contract_rejected",
        "checkout_root_length": len(str(checkout_root)),
        "materialized_path_length": materialized,
        "qualified_materialized_path_limit": values["qualified_materialized_path_limit"],
    }


def validate_registry(preconditions: dict[str, Any], fixtures: dict[str, Any]) -> dict[str, Any]:
    rows = preconditions.get("preconditions")
    cases = fixtures.get("fixtures")
    if not isinstance(rows, list) or not isinstance(cases, list):
        raise AdmissionError("admission_registry_invalid", "preconditions and fixtures must be lists")
    ids = [row.get("precondition_id") for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows) or any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        raise AdmissionError("admission_registry_invalid", "precondition IDs must be unique non-empty strings")
    mapped: set[str] = set()
    orphan: list[str] = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("fixture_id"), str):
            raise AdmissionError("admission_registry_invalid", "fixture IDs are required")
        references = case.get("invalidates")
        if not isinstance(references, list) or len(references) != 1:
            raise AdmissionError("admission_registry_invalid", "each fixture must invalidate exactly one predicate")
        mutation = case.get("mutation")
        expected_code = case.get("expected_rejection_code")
        if (
            not isinstance(mutation, dict)
            or mutation.get("field") != references[0]
            or "value" not in mutation
            or not isinstance(expected_code, str)
            or not expected_code
        ):
            raise AdmissionError(
                "admission_registry_invalid",
                "each fixture must declare its single-field mutation and expected rejection code",
            )
        value = references[0]
        if value not in ids:
            orphan.append(str(value))
        else:
            mapped.add(value)
    uncovered = sorted(set(ids) - mapped)
    return {
        "status": "PASS" if not uncovered and not orphan else "FAIL",
        "admission_precondition_count": len(ids),
        "negative_case_count": len(cases),
        "every_admission_precondition_has_negative_case": not uncovered,
        "uncovered_precondition_count": len(uncovered),
        "uncovered_precondition_ids": uncovered,
        "orphan_negative_case_count": len(orphan),
        "orphan_negative_references": orphan,
    }


def require_boolean(payload: dict[str, Any], field: str) -> None:
    if payload.get(field) is not True:
        raise AdmissionError(f"precondition_{field}_failed", f"{field} must be true")


def require_zero(payload: dict[str, Any], field: str) -> None:
    if payload.get(field) != 0:
        raise AdmissionError(f"precondition_{field}_failed", f"{field} must be zero")
