from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

try:
    from ._common import ContractError, git, require, subject_identity, write_json, write_jsonl
except ImportError:  # Direct script execution.
    from _common import ContractError, git, require, subject_identity, write_json, write_jsonl


SCHEMA = "iris_test_workflow_execution_census_v1"
TEST_ROOT = "Iris/build/description/v2/tests"
PILOT_FILE = f"{TEST_ROOT}/test_public_text_quality_acceptance_current_route.py"
PILOT_TESTS = {
    "test_phase7_schema_dispatch_accepts_historical_v1_and_current_v2",
    "test_phase7_schema_dispatch_rejects_unknown_and_malformed",
    "test_phase7_schema_dispatch_rejects_successor_transaction_hash_mismatch",
    "test_phase7_freeze_document_replay_is_deterministic",
}
MUST_ISOLATE_TERMS = (
    "tamper",
    "crash",
    "rollback",
    "concurrent",
    "lock",
    "source_write",
    "standalone_subprocess",
    "fresh_process",
    "recovery",
)


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def literal_strings(node: ast.AST) -> list[str]:
    return [value.value for value in ast.walk(node) if isinstance(value, ast.Constant) and isinstance(value.value, str)]


def function_rows(source: str, tree: ast.Module) -> Iterable[tuple[str, ast.AST]]:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            yield f"{source}::{node.name}", node
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_"):
                    yield f"{source}::{node.name}::{child.name}", child


def classify(node_id: str, source: str, function: ast.AST) -> tuple[str, str]:
    name = node_id.rsplit("::", 1)[-1]
    lowered = name.lower()
    if source == PILOT_FILE and name in PILOT_TESTS:
        return "candidate", "mandatory_public_text_phase7_pilot"
    if any(term in lowered for term in MUST_ISOLATE_TERMS):
        return "must_isolate", "fresh_or_mutating_failure_contract"
    calls = [dotted_name(value.func) for value in ast.walk(function) if isinstance(value, ast.Call)]
    if any(value in {"subprocess.run", "subprocess.Popen"} for value in calls):
        return "candidate", "explicit_subprocess_execution_candidate"
    return "preserve_independent", "no_proven_reusable_expensive_execution"


def census(repository: Path) -> dict[str, Any]:
    repository = repository.resolve()
    subject = subject_identity(repository)
    tracked = git(repository, "ls-files", "--", f"{TEST_ROOT}/test_*.py").splitlines()
    sources = sorted(value.replace("\\", "/") for value in tracked)
    require(sources, "configured test source inventory is empty")
    identities: list[dict[str, Any]] = []
    executions: list[dict[str, Any]] = []
    classifications: list[dict[str, Any]] = []
    producer_to_tests: dict[str, list[str]] = defaultdict(list)
    for source in sources:
        path = repository / source
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=source)
        except (OSError, SyntaxError) as error:
            raise ContractError(f"cannot parse test source {source}: {error}") from error
        for node_id, function in function_rows(source, tree):
            calls = [dotted_name(value.func) for value in ast.walk(function) if isinstance(value, ast.Call)]
            strings = literal_strings(function)
            referenced_names = {value.id for value in ast.walk(function) if isinstance(value, ast.Name)}
            producers = sorted(
                {
                    value.replace("\\", "/")
                    for value in strings
                    if value.endswith((".py", ".ps1")) and ("validat" in value.lower() or "run_" in value.lower())
                }
            )
            test_name = node_id.rsplit("::", 1)[-1]
            if source == PILOT_FILE and (
                "PHASE7_V2_VALIDATOR" in referenced_names or test_name in PILOT_TESTS
            ):
                producers.append("validate_public_text_quality_acceptance_official_0005_phase7_v2.py")
                producers = sorted(set(producers))
            for producer in producers:
                producer_to_tests[producer].append(node_id)
            disposition, reason = classify(node_id, source, function)
            authority_bound = any(token in " ".join(strings).lower() for token in ("taxonomy", "required_validation", "denominator"))
            identities.append(
                {
                    "schema_version": "iris_test_workflow_test_identity_v1",
                    "node_id": node_id,
                    "source_file": source,
                    "authority_bound": authority_bound,
                    "configured_route_member": True,
                }
            )
            executions.append(
                {
                    "schema_version": SCHEMA,
                    "node_id": node_id,
                    "static_observation": {
                        "subprocess_calls": sum(value in {"subprocess.run", "subprocess.Popen"} for value in calls),
                        "temporary_workspace_calls": sum("TemporaryDirectory" in value or value.endswith("mkdtemp") for value in calls),
                        "copy_calls": sum(value.startswith("shutil.copy") for value in calls),
                        "read_parse_hash_calls": sum(value.endswith(("read_text", "read_bytes", "loads", "sha256")) for value in calls),
                        "producer_signatures": producers,
                    },
                    "dynamic_observation": {"status": "DEFERRED_TO_PLAN_MEASUREMENT_SESSION"},
                }
            )
            classifications.append(
                {
                    "schema_version": "iris_test_workflow_classification_v1",
                    "node_id": node_id,
                    "primary_disposition": disposition,
                    "reason_code": reason,
                    "authority_bound": authority_bound,
                    "authority_transaction_disposition": "required_if_identity_changes" if authority_bound else "NOT_APPLICABLE",
                    "mutable_state_dependency": disposition == "must_isolate",
                }
            )
    duplications = []
    for producer, node_ids in sorted(producer_to_tests.items()):
        if len(node_ids) < 2:
            continue
        duplications.append(
            {
                "schema_version": "iris_test_workflow_duplication_v1",
                "invocation_identity": producer,
                "consumer_node_ids": sorted(node_ids),
                "consumer_count": len(node_ids),
                "disposition": "pilot" if producer.endswith("validate_public_text_quality_acceptance_official_0005_phase7_v2.py") else "candidate",
            }
        )
    mappings = [
        {
            "schema_version": "iris_test_workflow_contract_preservation_v1",
            "predecessor_test_id": row["node_id"],
            "contract_ids": [f"contract::{row['node_id']}"],
            "input_partition": "predecessor_declared_input",
            "negative_case_preserved": True,
            "expected_failure_signature": f"pytest-node::{row['node_id']}",
            "successor_scenario_id": "public-text-phase7-dispatch" if row["node_id"].rsplit("::", 1)[-1] in PILOT_TESTS and row["source_file"] == PILOT_FILE else row["node_id"],
            "successor_probe_id": row["node_id"].rsplit("::", 1)[-1],
            "must_isolate": next(value["primary_disposition"] for value in classifications if value["node_id"] == row["node_id"]) == "must_isolate",
            "authority_migration_required": False,
            "failure_localization_preserved": True,
        }
        for row in identities
    ]
    return {
        "subject": subject,
        "test_identity_census": identities,
        "execution_census": executions,
        "duplication_ledger": duplications,
        "classification_ledger": classifications,
        "contract_preservation_matrix": mappings,
        "scenario_dag": {
            "schema_version": "iris_test_workflow_scenario_dag_v1",
            "nodes": [{"scenario_id": "public-text-phase7-dispatch", "producer": "phase7_v2", "probe_count": 4}],
            "edges": [],
        },
    }


def write_census(result: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for key, filename in (
        ("test_identity_census", "test_identity_census.jsonl"),
        ("execution_census", "execution_census.jsonl"),
        ("duplication_ledger", "duplication_ledger.jsonl"),
        ("classification_ledger", "classification_ledger.jsonl"),
        ("contract_preservation_matrix", "contract_preservation_matrix.jsonl"),
    ):
        write_jsonl(output_root / filename, result[key])
    write_json(output_root / "scenario_dag.json", result["scenario_dag"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect the Iris execution consolidation census")
    parser.add_argument("--target-repository", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    write_census(census(args.target_repository), args.output_root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
