from __future__ import annotations

import argparse
import re
from pathlib import Path

from _common import ContractError, read_jsonl, stable_set, write_jsonl


def tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9]+", value.lower()) if token and token != "test"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a conservative protection map")
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
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
    write_jsonl(args.output, mapped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
