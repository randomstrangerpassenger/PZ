"""Validate scoped clean-checkout environment and result contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .iris_clean_checkout_validation_common import (
        CleanCheckoutError,
        git_identity,
        json_at_commit,
        resolved_repo,
        sha256_file,
        validate_external_environment,
    )
except ImportError:
    from iris_clean_checkout_validation_common import (
        CleanCheckoutError,
        git_identity,
        json_at_commit,
        resolved_repo,
        sha256_file,
        validate_external_environment,
    )


PHASE0_ENVIRONMENT_BINDING_PATH = (
    "Iris/validation/clean_checkout/authority/"
    "phase0_ratification_attempt_0002.json"
)
EVIDENCE_ROOT = Path("Iris/validation/clean_checkout/evidence")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CleanCheckoutError(message)


def validate_environment(
    repo: Path,
    commit: str,
    python_executable: Path,
    environment_receipt: Path,
) -> dict[str, Any]:
    subject = git_identity(repo, commit)
    phase0 = json_at_commit(
        repo,
        subject["commit"],
        PHASE0_ENVIRONMENT_BINDING_PATH,
    )
    expected = phase0["implementation_contract_delta"]["OR-06"]
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
) -> dict[str, Any]:
    run_a_path = run_a_path.resolve()
    run_b_path = run_b_path.resolve()
    run_a = json.loads(run_a_path.read_text(encoding="utf-8"))
    run_b = json.loads(run_b_path.read_text(encoding="utf-8"))
    _require(
        run_a.get("schema_version")
        == "iris-clean-checkout-canonical-result-v2",
        "Run A canonical result schema mismatch",
    )
    _require(
        run_b.get("schema_version")
        == "iris-clean-checkout-canonical-result-v2",
        "Run B canonical result schema mismatch",
    )
    _require(run_a.get("status") == "PASS", "Run A is not PASS")
    _require(run_b.get("status") == "PASS", "Run B is not PASS")
    _require(run_a == run_b, "Run A and Run B canonical results differ")
    return {
        "schema_version": "iris-clean-checkout-result-comparison-v1",
        "status": "PASS",
        "subject": run_a["subject"],
        "test_identity_count": run_a["test_identity_count"],
        "test_inventory_sha256": run_a["test_inventory_sha256"],
        "run_a_sha256": sha256_file(run_a_path),
        "run_b_sha256": sha256_file(run_b_path),
        "canonical_results_equal": True,
    }


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
