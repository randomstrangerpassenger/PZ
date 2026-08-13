from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import ContractError, read_jsonl, require, write_json
except ImportError:
    from _common import ContractError, read_jsonl, require, write_json


AUTHORITY_AXES = {
    "source_classification",
    "denominator",
    "taxonomy",
    "required_validation",
    "evidence_mapping",
}


def validate_transactions(families: list[dict[str, Any]], transactions: list[dict[str, Any]]) -> dict[str, Any]:
    family_ids = [row.get("family_id") for row in families]
    require(all(isinstance(value, str) and value for value in family_ids), "family_id is required")
    require(len(family_ids) == len(set(family_ids)), "duplicate family_id")
    transaction_by_family = {row.get("family_id"): row for row in transactions}
    require(len(transaction_by_family) == len(transactions), "duplicate identity transaction")
    failures: list[str] = []
    for family in families:
        if family.get("disposition") != "adopted":
            continue
        transaction = transaction_by_family.get(family["family_id"])
        if not transaction:
            failures.append(f"missing:{family['family_id']}")
            continue
        changed = set(transaction.get("changed_authority_axes", []))
        if not changed <= AUTHORITY_AXES:
            failures.append(f"unknown-axis:{family['family_id']}")
        if changed and set(transaction.get("atomic_members", [])) != changed | {"implementation", "contract_mapping"}:
            failures.append(f"partial:{family['family_id']}")
        if transaction.get("predecessor_mapping_preserved") is not True:
            failures.append(f"predecessor:{family['family_id']}")
    return {
        "schema_version": "iris_test_workflow_identity_transaction_validation_v1",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "adopted_family_count": sum(row.get("disposition") == "adopted" for row in families),
        "first_real_authority_bound_migration": "NOT_APPLICABLE_no_admitted_authority_family"
        if not any(row.get("changed_authority_axes") for row in transactions)
        else "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate atomic Iris family identity transactions")
    parser.add_argument("--family-ledger", type=Path, required=True)
    parser.add_argument("--transactions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_transactions(read_jsonl(args.family_ledger), read_jsonl(args.transactions))
    write_json(args.output, report)
    require(report["status"] == "PASS", "identity transaction validation failed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
