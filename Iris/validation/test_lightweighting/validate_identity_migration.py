from __future__ import annotations

import argparse
from pathlib import Path

from _common import ContractError, read_json, read_jsonl, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate exact-current identity migration")
    parser.add_argument("--taxonomy", type=Path, required=True)
    parser.add_argument("--required", type=Path, required=True)
    parser.add_argument("--migration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    taxonomy = read_json(args.taxonomy)
    required = read_json(args.required)
    migrations = read_jsonl(args.migration)
    current_ids = {row["test_id"] for row in taxonomy.get("rows", [])}
    required_ids = {row["test_id"] for row in required.get("required_tests", []) if row.get("required") is not False}
    errors: list[str] = []
    for row in migrations:
        predecessor = row["predecessor_test_id"]
        successors = row.get("successor_test_ids", [])
        authority_role = row.get("authority_role", "exact current")
        if authority_role == "configured current non-exact":
            if predecessor in current_ids or predecessor in required_ids:
                errors.append(f"non-exact predecessor is exact-bound: {predecessor}")
            exact_bound_successors = sorted(
                value for value in successors if value in current_ids or value in required_ids
            )
            if exact_bound_successors:
                errors.append(
                    f"non-exact migration crosses exact authority for {predecessor}: "
                    f"{exact_bound_successors}"
                )
            if not successors:
                errors.append(f"non-exact migration has no successor: {predecessor}")
            if len(successors) != len(set(successors)):
                errors.append(f"dual successor binding for {predecessor}")
            continue
        if predecessor in current_ids:
            errors.append(f"stale predecessor remains current: {predecessor}")
        if predecessor in required_ids:
            errors.append(f"dangling predecessor remains required: {predecessor}")
        missing = [value for value in successors if value not in current_ids]
        if missing:
            errors.append(f"missing successors for {predecessor}: {missing}")
        if len(successors) != len(set(successors)):
            errors.append(f"dual successor binding for {predecessor}")
    affected_predecessors = {row["predecessor_test_id"] for row in migrations}
    affected_successors = {value for row in migrations for value in row.get("successor_test_ids", [])}
    dangling = sorted((required_ids & (affected_predecessors | affected_successors)) - current_ids)
    preexisting_required_not_in_taxonomy = sorted((required_ids - current_ids) - set(dangling))
    write_json(args.output, {
        "schema_version": "iris_test_precision_lightweighting_identity_validation_v1",
        "errors": errors,
        "dangling_required_validation": len(dangling),
        "preexisting_required_not_in_taxonomy_count": len(preexisting_required_not_in_taxonomy),
        "preexisting_required_not_in_taxonomy": preexisting_required_not_in_taxonomy,
        "stale_predecessor_binding": sum("stale predecessor" in item for item in errors),
        "dual_current_test_binding": sum("dual successor" in item for item in errors),
        "status": "PASS" if not errors else "FAIL",
    })
    if errors:
        raise ContractError("identity migration validation failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
