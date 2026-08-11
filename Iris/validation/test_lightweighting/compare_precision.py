from __future__ import annotations

import argparse
from pathlib import Path

from _common import ContractError, read_json, read_jsonl, write_json


PRECISION_KEYS = ("contract_ids", "input_partitions", "branch_conditions", "fail_closed_paths", "interaction_states")


def union(rows: list[dict], key: str) -> set[str]:
    return {value for row in rows for value in row.get(key, [])}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare fixed-domain Iris test precision")
    parser.add_argument("--before-map", type=Path, required=True)
    parser.add_argument("--after-map", type=Path, required=True)
    parser.add_argument("--before-complexity", type=Path, required=True)
    parser.add_argument("--after-complexity", type=Path, required=True)
    parser.add_argument("--removed-scenarios", type=int, required=True)
    parser.add_argument("--gross-removed-nodes", type=int, required=True)
    parser.add_argument("--localization-split-added-nodes", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before_rows = read_jsonl(args.before_map)
    after_rows = read_jsonl(args.after_map)
    before = read_json(args.before_complexity)
    after = read_json(args.after_complexity)
    losses = {key: sorted(union(before_rows, key) - union(after_rows, key)) for key in PRECISION_KEYS}
    deltas = {
        "pytest_node_count_delta": after["pytest_node_id_count"] - before["pytest_node_id_count"],
        "test_support_LOC_delta": after["test_support_LOC"] - before["test_support_LOC"],
        "files_ge_500_delta": after["files_ge_500_count"] - before["files_ge_500_count"],
        "files_ge_1000_delta": after["files_ge_1000_count"] - before["files_ge_1000_count"],
        "large_test_method_count_delta": after["large_test_method_count"] - before["large_test_method_count"],
    }
    precision_regression = sum(len(value) for value in losses.values())
    a1 = (
        deltas["pytest_node_count_delta"] < 0
        and args.removed_scenarios > 0
        and deltas["test_support_LOC_delta"] < 0
        and deltas["files_ge_500_delta"] < 0
        and deltas["files_ge_1000_delta"] < 0
        and deltas["large_test_method_count_delta"] < 0
    )
    material = args.removed_scenarios > 0 or any(value < 0 for value in deltas.values())
    outcome = "reduced" if a1 else ("mixed_reduction" if material else "measured_no_op")
    report = {
        "schema_version": "iris_test_precision_lightweighting_precision_comparison_v1",
        **deltas,
        "removed_redundant_executed_scenario_count": args.removed_scenarios,
        "gross_removed_node_count": args.gross_removed_nodes,
        "localization_split_added_node_count": args.localization_split_added_nodes,
        "net_node_delta": args.localization_split_added_nodes - args.gross_removed_nodes,
        "losses": losses,
        "precision_regression": precision_regression,
        "reduction_axis_values_recorded": True,
        "a1_all_reduction_conditions_satisfied": a1,
        "reduction_outcome": outcome,
        "large_file_metric_definition_matches_baseline": before["selection_rule"] == after["selection_rule"],
        "large_method_metric_definition_matches_baseline": (
            before["large_method_metric_definition"] == after["large_method_metric_definition"]
            and before["large_test_method_loc_threshold"] == after["large_test_method_loc_threshold"]
        ),
    }
    write_json(args.output, report)
    if precision_regression:
        raise ContractError("precision regression detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
