from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import ContractError, git, read_json, read_jsonl, require, write_json
except ImportError:
    from _common import ContractError, git, read_json, read_jsonl, require, write_json


AUTHORITY_AXES = {
    "source_classification",
    "denominator",
    "taxonomy",
    "required_validation",
    "evidence_mapping",
}
AUTHORITY_ARTIFACTS = {
    "source_classification": "Iris/_docs/round3/round3_pytest_source_classification.json",
    "denominator": "Iris/_docs/round3/round3_full_discovery_denominator.json",
    "taxonomy": "Iris/_docs/round3/round3_test_taxonomy.json",
    "required_validation": "Iris/_docs/round3/current_route_required_validations.json",
}
FIRST_REAL_MIGRATION_CHECKS = {
    "exact_live_binding_recensus",
    "migration_dry_run",
    "implementation_authority_single_transaction",
    "partial_and_rollback_failure_injection",
    "exact_configured_required_integrity_validation",
    "predecessor_mapping_preservation",
}


def observe_authority_axes(
    repository: Path, base: str
) -> dict[str, Any]:
    head = git(repository, "rev-parse", "HEAD")
    base_commit = git(repository, "rev-parse", base)

    def blob_at(subject: str, path: str) -> str:
        try:
            return git(repository, "rev-parse", f"{subject}:{path}")
        except ContractError:
            return "MISSING"

    identities: dict[str, dict[str, Any]] = {}
    changed: list[str] = []
    for axis, path in AUTHORITY_ARTIFACTS.items():
        before = blob_at(base_commit, path)
        after = blob_at(head, path)
        identities[axis] = {
            "path": path,
            "base_git_blob_id": before,
            "terminal_git_blob_id": after,
        }
        if before != after:
            changed.append(axis)
    changed_paths = {
        path.replace("\\", "/")
        for path in git(
            repository, "diff", "--name-only", base_commit, head
        ).splitlines()
        if path
    }
    evidence_mapping_paths = sorted(
        path
        for path in changed_paths
        if path.startswith("Iris/_docs/round3/")
        and path not in set(AUTHORITY_ARTIFACTS.values())
    )
    identities["evidence_mapping"] = {
        "paths": evidence_mapping_paths,
        "base_commit": base_commit,
        "terminal_commit": head,
    }
    if evidence_mapping_paths:
        changed.append("evidence_mapping")
    return {
        "base_commit": base_commit,
        "terminal_commit": head,
        "changed_axes": sorted(changed),
        "artifact_identities": identities,
    }


def _first_real_migration_valid(
    receipt: dict[str, Any] | None, adopted_family_ids: set[str]
) -> bool:
    if not isinstance(receipt, dict):
        return False
    checks = receipt.get("checks")
    return (
        receipt.get("schema_version")
        == "iris_test_workflow_first_real_authority_bound_migration_v1"
        and receipt.get("status") == "PASS"
        and receipt.get("family_id") in adopted_family_ids
        and isinstance(checks, dict)
        and set(checks) == FIRST_REAL_MIGRATION_CHECKS
        and all(value == "PASS" for value in checks.values())
    )


def validate_transactions(
    families: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    authority_observation: dict[str, Any],
    first_real_migration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    family_ids = [row.get("family_id") for row in families]
    require(all(isinstance(value, str) and value for value in family_ids), "family_id is required")
    require(len(family_ids) == len(set(family_ids)), "duplicate family_id")
    transaction_by_family = {row.get("family_id"): row for row in transactions}
    require(len(transaction_by_family) == len(transactions), "duplicate identity transaction")
    failures: list[str] = []
    adopted_family_ids = {
        str(row["family_id"])
        for row in families
        if row.get("disposition") == "adopted"
    }
    declared_changed_axes: set[str] = set()
    for family in families:
        if family.get("disposition") != "adopted":
            continue
        if not isinstance(family.get("authority_bound"), bool):
            failures.append(f"authority-bound-missing:{family['family_id']}")
        transaction = transaction_by_family.get(family["family_id"])
        if not transaction:
            failures.append(f"missing:{family['family_id']}")
            continue
        raw_changed = transaction.get("changed_authority_axes")
        if not isinstance(raw_changed, list) or len(raw_changed) != len(set(raw_changed)):
            failures.append(f"changed-axis-malformed:{family['family_id']}")
            continue
        changed = set(raw_changed)
        declared_changed_axes.update(changed)
        if not changed <= AUTHORITY_AXES:
            failures.append(f"unknown-axis:{family['family_id']}")
        if set(transaction.get("atomic_members", [])) != changed | {"implementation", "contract_mapping"}:
            failures.append(f"partial:{family['family_id']}")
        if family.get("authority_bound") is False and changed:
            failures.append(f"unbound-authority-change:{family['family_id']}")
        if transaction.get("schema_version") != "iris_test_workflow_identity_transaction_v1":
            failures.append(f"schema:{family['family_id']}")
        if transaction.get("status") != "PASS":
            failures.append(f"status:{family['family_id']}")
        if transaction.get("transaction_kind") not in {
            "identity_preserving",
            "authority_bound_migration",
        }:
            failures.append(f"kind:{family['family_id']}")
        implementation_paths = transaction.get("implementation_paths")
        if not isinstance(implementation_paths, list) or not implementation_paths or not all(
            isinstance(path, str) and path for path in implementation_paths
        ):
            failures.append(f"implementation-paths:{family['family_id']}")
        if transaction.get("predecessor_mapping_preserved") is not True:
            failures.append(f"predecessor:{family['family_id']}")
    observed_changed_axes = set(authority_observation.get("changed_axes", []))
    if not observed_changed_axes <= AUTHORITY_AXES:
        failures.append("observed-unknown-authority-axis")
    identities = authority_observation.get("artifact_identities")
    if not isinstance(identities, dict) or set(identities) != AUTHORITY_AXES:
        failures.append("authority-artifact-observation-incomplete")
    if declared_changed_axes != observed_changed_axes:
        failures.append("declared-observed-authority-axis-mismatch")
    migration_valid = _first_real_migration_valid(
        first_real_migration, adopted_family_ids
    )
    if observed_changed_axes and not migration_valid:
        failures.append("first-real-authority-bound-migration-unqualified")
    return {
        "schema_version": "iris_test_workflow_identity_transaction_validation_v1",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "adopted_family_count": len(adopted_family_ids),
        "observed_authority_axes": sorted(observed_changed_axes),
        "authority_artifact_identities": identities,
        "first_real_authority_bound_migration": "NOT_APPLICABLE_no_admitted_authority_family"
        if not observed_changed_axes
        else "PASS" if migration_valid else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate atomic Iris family identity transactions")
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--family-ledger", type=Path, required=True)
    parser.add_argument("--transactions", type=Path, required=True)
    parser.add_argument("--first-real-migration-receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_transactions(
        read_jsonl(args.family_ledger),
        read_jsonl(args.transactions),
        observe_authority_axes(args.repository.resolve(), args.base),
        read_json(args.first_real_migration_receipt)
        if args.first_real_migration_receipt
        else None,
    )
    write_json(args.output, report)
    require(report["status"] == "PASS", "identity transaction validation failed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
