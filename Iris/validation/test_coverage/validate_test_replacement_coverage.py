"""Check that retained tests cover the declared protections of replaced tests."""

from __future__ import annotations

import argparse
from pathlib import Path

from source_metrics_io import ContractError, read_jsonl, write_json


VECTOR_KEYS = ("contract_ids", "input_partitions", "branch_conditions", "fail_closed_paths", "interaction_states")
ELIMINATION = {"eliminate_strongly_dominated", "replace_with_stronger_invariant"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate candidate dominance against a frozen map")
    parser.add_argument("--protection-map", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protection = {row["exact_test_id"]: row for row in read_jsonl(args.protection_map)}
    ledger = read_jsonl(args.ledger)
    errors: list[str] = []
    for row in ledger:
        disposition = row.get("disposition")
        if disposition not in ELIMINATION:
            continue
        candidate_id = row.get("predecessor_test_id")
        survivor_ids = row.get("successor_test_ids", [])
        if candidate_id not in protection or not survivor_ids or any(item not in protection for item in survivor_ids):
            errors.append(f"unmapped candidate/survivor: {candidate_id}")
            continue
        candidate = protection[candidate_id]
        for key in VECTOR_KEYS:
            survivor_values = {value for item in survivor_ids for value in protection[item].get(key, [])}
            survivor_values.update(row.get("replacement_vectors", {}).get(key, []))
            missing = set(candidate.get(key, [])) - survivor_values
            if missing:
                errors.append(f"{candidate_id} {key} not dominated: {sorted(missing)}")
        if row.get("branch_execution_evidence") not in {"static_proof", "targeted_coverage", "equivalent_trace", "not_material"}:
            errors.append(f"{candidate_id} lacks branch execution evidence")
        if not row.get("detection_parity") or not row.get("failure_localization_parity"):
            errors.append(f"{candidate_id} lacks detection/localization parity")
    write_json(args.output, {
        "schema_version": "iris_test_precision_lightweighting_dominance_validation_v1",
        "candidate_count": len(ledger),
        "errors": errors,
        "evidence_free_elimination_candidate": len(errors),
        "material_branch_evidence_gap": sum("branch execution" in item for item in errors),
        "status": "PASS" if not errors else "FAIL",
    })
    if errors:
        raise ContractError("dominance validation failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
