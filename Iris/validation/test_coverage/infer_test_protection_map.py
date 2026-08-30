"""Infer declared protection conditions from test names and explicit migrations.

This is a name-derived map, not a measurement of executed branch coverage.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from source_metrics_io import ContractError, read_jsonl, stable_set, write_jsonl


def tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9]+", value.lower()) if token and token != "test"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a conservative protection map")
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fault-matrix-output", type=Path)
    parser.add_argument("--predecessor-protection-map", type=Path)
    parser.add_argument("--migration", type=Path)
    args = parser.parse_args()
    rows = read_jsonl(args.inventory)
    mapped = []
    for row in rows:
        test_id = str(row["exact_test_id"])
        name = test_id.rsplit(".", 1)[-1]
        parts = tokens(name)
        failure = [token for token in parts if token in {
            "fail", "fails", "reject", "rejects", "missing", "invalid", "tamper", "tampered",
            "stale", "dangling", "dual", "outside", "malformed", "unchanged", "without",
        }]
        contract_id = "contract:" + name
        mapped.append({
            **row,
            "contract_owner": row["source_file"],
            "contract_ids": [contract_id],
            "production_targets": [],
            "branch_conditions": ["name-derived:" + token for token in parts if token in {"default", "diagnostic", "current", "legacy", "optional"}],
            "input_partitions": ["name-derived:" + token for token in parts if token in {"missing", "malformed", "outside", "legacy", "default", "diagnostic"}],
            "interaction_states": [],
            "failure_conditions": [f"failure:{name}:{token}" for token in stable_set(failure)],
            "fail_closed_paths": [f"fail-closed:{name}"] if failure else [],
            "oracle": "existing_assertions",
            "environment_boundary": "repository_external_or_test_fixture",
        })
    if len(mapped) != len(rows):
        raise ContractError("inventory to protection-map reconciliation failed")
    if args.predecessor_protection_map or args.migration:
        if not args.predecessor_protection_map or not args.migration:
            raise ContractError("predecessor protection map and migration must be supplied together")
        predecessor = {row["exact_test_id"]: row for row in read_jsonl(args.predecessor_protection_map)}
        by_id = {row["exact_test_id"]: row for row in mapped}
        for migration in read_jsonl(args.migration):
            source = predecessor.get(migration["predecessor_test_id"])
            if source is None:
                raise ContractError(f"migration predecessor is absent: {migration['predecessor_test_id']}")
            for successor_id in migration.get("successor_test_ids", []):
                successor = by_id.get(successor_id)
                if successor is None:
                    raise ContractError(f"migration successor is absent: {successor_id}")
                for key in (
                    "contract_ids", "branch_conditions", "input_partitions", "interaction_states",
                    "failure_conditions", "fail_closed_paths",
                ):
                    successor[key] = stable_set([*successor.get(key, []), *source.get(key, [])])
    write_jsonl(args.output, mapped)
    if args.fault_matrix_output:
        fault_to_tests: dict[str, list[str]] = {}
        for row in mapped:
            for key in ("failure_conditions", "fail_closed_paths"):
                for fault_id in row[key]:
                    fault_to_tests.setdefault(fault_id, []).append(row["exact_test_id"])
        write_jsonl(
            args.fault_matrix_output,
            (
                {
                    "fault_id": fault_id,
                    "injection_kind": "contract_equivalent_name_derived_v1",
                    "detecting_test_ids": stable_set(test_ids),
                    "critical": True,
                }
                for fault_id, test_ids in sorted(fault_to_tests.items())
            ),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
