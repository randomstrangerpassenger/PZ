"""Validate scoped clean-checkout environment and result contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from iris_tooling.execution import decode_legacy_result, encode_legacy_result

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from Iris.validation.clean_checkout import (
    iris_clean_checkout_validation_common as clean_checkout_common,
)
from Iris.validation.clean_checkout.iris_clean_checkout_validation_common import (
    CleanCheckoutError,
    blob_id,
    canonical_json_bytes,
    git_identity,
    git_text,
    json_at_commit,
    resolved_repo,
    resolve_current_environment_authority,
    sha256_bytes,
    sha256_file,
    validate_external_environment,
)


EVIDENCE_ROOT = Path("Iris/validation/clean_checkout/evidence")
VALIDATOR_PATH = (
    "Iris/validation/clean_checkout/validate_iris_clean_checkout_validation.py"
)
COMMON_MODULE_PATH = (
    "Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py"
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CleanCheckoutError(message)


def _implementation_identity(
    repo: Path,
    commit: str,
) -> dict[str, Any]:
    validator_path = Path(__file__).resolve()
    common_path = Path(clean_checkout_common.__file__).resolve()
    expected_validator = (repo / VALIDATOR_PATH).resolve()
    expected_common = (repo / COMMON_MODULE_PATH).resolve()
    _require(
        validator_path == expected_validator,
        "compare validator was imported from a different checkout",
    )
    _require(
        common_path == expected_common,
        "compare common module was imported from a different checkout",
    )
    expected_validator_blob = blob_id(repo, commit, VALIDATOR_PATH)
    expected_common_blob = blob_id(repo, commit, COMMON_MODULE_PATH)
    working_validator_blob = git_text(
        repo,
        "hash-object",
        f"--path={VALIDATOR_PATH}",
        str(validator_path),
    ).strip()
    working_common_blob = git_text(
        repo,
        "hash-object",
        f"--path={COMMON_MODULE_PATH}",
        str(common_path),
    ).strip()
    _require(
        working_validator_blob == expected_validator_blob,
        "compare validator working file differs from subject blob",
    )
    _require(
        working_common_blob == expected_common_blob,
        "compare common working file differs from subject blob",
    )
    return {
        "validator": {
            "logical_path": VALIDATOR_PATH,
            "actual_path": validator_path.as_posix(),
            "git_blob_id": expected_validator_blob,
            "working_git_blob_id": working_validator_blob,
            "working_sha256": sha256_file(validator_path),
        },
        "imported_common": {
            "logical_path": COMMON_MODULE_PATH,
            "actual_path": common_path.as_posix(),
            "module_file": common_path.as_posix(),
            "git_blob_id": expected_common_blob,
            "working_git_blob_id": working_common_blob,
            "working_sha256": sha256_file(common_path),
        },
    }


def validate_environment(
    repo: Path,
    commit: str,
    python_executable: Path,
    environment_receipt: Path,
) -> dict[str, Any]:
    subject = git_identity(repo, commit)
    expected = resolve_current_environment_authority(
        repo, subject["commit"]
    )["environment_contract"]
    return {
        "schema_version": "iris-clean-checkout-environment-validation-v1",
        "subject": subject,
        "environment": validate_external_environment(
            python_executable,
            environment_receipt,
            expected,
        ),
        "status": "PASS",
    }


def validate_result_pair(
    run_a_path: Path,
    run_b_path: Path,
    *,
    repo: Path | None = None,
    commit: str | None = None,
) -> dict[str, Any]:
    run_a_path = run_a_path.resolve()
    run_b_path = run_b_path.resolve()
    run_a_bytes = run_a_path.read_bytes()
    run_b_bytes = run_b_path.read_bytes()
    _require(
        not run_a_bytes.startswith(b"\xef\xbb\xbf"),
        "Run A canonical result contains a UTF-8 BOM",
    )
    _require(
        not run_b_bytes.startswith(b"\xef\xbb\xbf"),
        "Run B canonical result contains a UTF-8 BOM",
    )
    _require(
        run_a_bytes == run_b_bytes,
        "Run A and Run B canonical result bytes differ",
    )
    run_a = json.loads(run_a_bytes)
    run_b = json.loads(run_b_bytes)
    _require(
        isinstance(run_a, dict) and isinstance(run_b, dict),
        "canonical results must be JSON objects",
    )
    _require(
        run_a_bytes == canonical_json_bytes(run_a),
        "Run A canonical result does not use canonical JSON bytes",
    )
    _require(
        run_b_bytes == canonical_json_bytes(run_b),
        "Run B canonical result does not use canonical JSON bytes",
    )
    supported_schemas = {
        "iris-clean-checkout-canonical-result-v2",
        "iris-clean-checkout-canonical-full-result-v1",
    }
    _require(
        run_a.get("schema_version") in supported_schemas,
        "Run A canonical result schema mismatch",
    )
    _require(
        run_b.get("schema_version") == run_a.get("schema_version"),
        "Run B canonical result schema mismatch",
    )
    _require(run_a.get("status") == "PASS", "Run A is not PASS")
    _require(run_b.get("status") == "PASS", "Run B is not PASS")
    _require(run_a == run_b, "Run A and Run B canonical results differ")
    _require(
        isinstance(run_a.get("subject"), dict),
        "canonical result subject is missing",
    )
    _require(
        isinstance(run_a.get("test_inventory_sha256"), str),
        "canonical result test inventory hash is missing",
    )
    result = {
        "schema_version": "iris-clean-checkout-result-comparison-v1",
        "status": "PASS",
        "subject": run_a["subject"],
        "test_identity_count": run_a.get(
            "test_identity_count",
            run_a.get("pytest_identity_count"),
        ),
        "required_execution_unit_count": run_a.get(
            "required_execution_unit_count"
        ),
        "test_inventory_sha256": run_a["test_inventory_sha256"],
        "run_a_sha256": sha256_bytes(run_a_bytes),
        "run_b_sha256": sha256_bytes(run_b_bytes),
        "canonical_result_raw_bytes_equal": True,
        "canonical_results_equal": True,
    }
    if repo is not None or commit is not None:
        _require(
            repo is not None and commit is not None,
            "repo and commit must be provided together",
        )
        subject = git_identity(repo, commit)
        _require(
            run_a["subject"] == subject,
            "Run subject differs from compare subject",
        )
        result["implementation_identity"] = _implementation_identity(
            repo, subject["commit"]
        )
    return encode_legacy_result(
        decode_legacy_result(
            result,
            discriminator="iris.validation.clean-checkout-comparison.v1",
        )
    )


def validate_change2_evidence(repo: Path) -> dict[str, Any]:
    root = repo / EVIDENCE_ROOT
    gate = json.loads((root / "gate_manifest.json").read_text("utf-8"))
    preservation = json.loads(
        (root / "preservation_baseline_record.json").read_text("utf-8")
    )
    transitions = json.loads(
        (root / "commit_transition_ledger.json").read_text("utf-8")
    )
    failures = json.loads(
        (root / "failure_disposition_ledger.json").read_text("utf-8")
    )

    _require(
        gate["terminal_claim"]
        == "Iris clean-checkout technical-debt gate reproducibility PASS",
        "gate manifest claim exceeds the owner-scoped claim",
    )
    preservation_identity = git_identity(
        repo,
        preservation["preservation"]["commit"],
    )
    _require(
        preservation_identity["tree"]
        == preservation["preservation"]["tree"],
        "preservation commit/tree binding mismatch",
    )
    v0_entries = [
        row
        for row in transitions["entries"]
        if row["identity"] == "V0" and row["state"] == "bound"
    ]
    _require(len(v0_entries) == 1, "transition ledger must bind one V0")
    _require(
        v0_entries[0]["commit"] == gate["validated_subject"]["commit"]
        and v0_entries[0]["tree"] == gate["validated_subject"]["tree"],
        "gate manifest and transition ledger bind different V0 identities",
    )
    coverage = failures["coverage_summary"]
    accounted = (
        coverage["covered_origin_surface_count"]
        + coverage["insufficient_preserved_evidence_count"]
        + coverage["unreconciled_origin_surface_count"]
        + coverage["excluded_by_owner_scope_count"]
    )
    _require(
        coverage["origin_surface_total_count"] == accounted,
        "origin observation accounting equation does not balance",
    )
    _require(
        failures["origin_command_provenance_status"] == "unidentifiable",
        "origin command provenance must remain unidentifiable",
    )
    _require(
        coverage["origin_failure_surface_coverage_status"]
        == "not_applicable_to_scoped_gate",
        "origin coverage must not be presented as scoped-gate coverage",
    )
    return {
        "schema_version": "iris-clean-checkout-change2-validation-v1",
        "status": "PASS",
        "preservation": preservation_identity,
        "validated_subject": gate["validated_subject"],
        "origin_command_provenance_status": "unidentifiable",
        "origin_failure_surface_coverage_status": (
            "not_applicable_to_scoped_gate"
        ),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    environment = subparsers.add_parser("environment")
    environment.add_argument("--repo", required=True)
    environment.add_argument("--commit", required=True)
    environment.add_argument("--python", required=True)
    environment.add_argument("--environment-receipt", required=True)
    comparison = subparsers.add_parser("compare-results")
    comparison.add_argument("--run-a", required=True)
    comparison.add_argument("--run-b", required=True)
    comparison.add_argument("--repo")
    comparison.add_argument("--commit")
    evidence = subparsers.add_parser("change2-evidence")
    evidence.add_argument("--repo", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "environment":
            result = validate_environment(
                resolved_repo(args.repo),
                args.commit,
                Path(args.python),
                Path(args.environment_receipt),
            )
        elif args.command == "compare-results":
            result = validate_result_pair(
                Path(args.run_a),
                Path(args.run_b),
                repo=(resolved_repo(args.repo) if args.repo else None),
                commit=args.commit,
            )
        else:
            result = validate_change2_evidence(resolved_repo(args.repo))
    except (CleanCheckoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
