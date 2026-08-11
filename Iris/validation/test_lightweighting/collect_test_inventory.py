from __future__ import annotations

import argparse
from pathlib import Path

from _common import (
    ContractError,
    ast_test_methods,
    physical_loc,
    read_json,
    repo_path,
    sha256_file,
    stable_set,
    subject_identity,
    git,
    write_json,
    write_jsonl,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect the fixed Iris test-lightweighting universe")
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--taxonomy", default="Iris/_docs/round3/round3_test_taxonomy.json")
    parser.add_argument("--required", default="Iris/_docs/round3/current_route_required_validations.json")
    parser.add_argument("--support-source", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scenario-output", type=Path, required=True)
    parser.add_argument("--complexity-output", type=Path, required=True)
    parser.add_argument("--large-method-threshold", type=int, default=100)
    args = parser.parse_args()

    repo = args.repo.resolve()
    taxonomy_path = repo_path(repo, args.taxonomy)
    required_path = repo_path(repo, args.required)
    taxonomy = read_json(taxonomy_path)
    required = read_json(required_path)
    rows = taxonomy.get("rows")
    if not isinstance(rows, list):
        raise ContractError("taxonomy rows are missing")
    required_ids = {
        row["test_id"] for row in required.get("required_tests", []) if row.get("required") is not False
    }
    exact_sources = stable_set(row["source_file"] for row in rows)
    configured_sources = stable_set(
        line
        for line in git(
            repo,
            "ls-files",
            "Iris/build/description/v2/tests/*.py",
            "Iris/build/tests/*.py",
        ).splitlines()
        if Path(line).name.startswith("test_")
    )
    support_sources = stable_set(args.support_source)
    universe_paths = stable_set([*configured_sources, *support_sources])
    inventory: list[dict[str, object]] = []
    methods: list[dict[str, object]] = []
    for relative in universe_paths:
        path = repo_path(repo, relative)
        if not path.is_file():
            raise ContractError(f"test-support source is missing: {relative}")
        file_methods = ast_test_methods(path) if path.suffix == ".py" else []
        inventory.append({
            "source_file": relative,
            "physical_loc": physical_loc(path),
            "sha256": sha256_file(path),
            "configured_source": relative in configured_sources,
            "exact_source": relative in exact_sources,
            "mandatory_plan_local_support": relative in support_sources,
            "test_method_count": len(file_methods),
        })
        methods.extend({"source_file": relative, **row} for row in file_methods)

    node_rows = []
    for row in rows:
        test_id = row["test_id"]
        node_rows.append({
            "source_file": row["source_file"],
            "pytest_node_id": f"{row['source_file']}::{test_id.rsplit('.', 2)[-2]}::{test_id.rsplit('.', 1)[-1]}",
            "exact_test_id": test_id,
            "route": row.get("contract_class", "current"),
            "authority_role": row.get("routing_status", "exact_current"),
            "required_validation_bindings": [test_id] if test_id in required_ids else [],
            "regression_provenance": row.get("reason", ""),
        })

    write_jsonl(args.output, node_rows)
    write_jsonl(
        args.scenario_output,
        ({"scenario_id": row["exact_test_id"], "executed_case_count": 1, "input_row_count": 1}
         for row in node_rows),
    )
    locs = [int(row["physical_loc"]) for row in inventory]
    threshold = args.large_method_threshold
    write_json(args.complexity_output, {
        "schema_version": "iris_test_precision_lightweighting_complexity_v1",
        "subject": subject_identity(repo),
        "selection_rule": "taxonomy_sources_plus_explicit_round_support_v1",
        "physical_line_rule": "bytes_splitlines_v1",
        "large_method_metric_definition": "python_ast_test_method_source_span_v1",
        "large_test_method_loc_threshold": threshold,
        "pytest_node_id_count": len(node_rows),
        "semantic_scenario_count": len(node_rows),
        "executed_case_count": len(node_rows),
        "input_row_count": len(node_rows),
        "test_support_file_universe": inventory,
        "test_support_LOC": sum(locs),
        "files_ge_500_count": sum(value >= 500 for value in locs),
        "files_ge_1000_count": sum(value >= 1000 for value in locs),
        "large_test_method_count": sum(int(row["loc"]) >= threshold for row in methods),
        "max_test_method_LOC": max((int(row["loc"]) for row in methods), default=0),
        "large_test_methods": [row for row in methods if int(row["loc"]) >= threshold],
        "taxonomy_sha256": sha256_file(taxonomy_path),
        "required_validations_sha256": sha256_file(required_path),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
