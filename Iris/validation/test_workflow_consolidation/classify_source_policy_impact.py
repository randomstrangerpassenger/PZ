from __future__ import annotations

import argparse
import configparser
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import ContractError, git, read_json, require, subject_identity, write_json
except ImportError:  # Direct script execution.
    from _common import ContractError, git, read_json, require, subject_identity, write_json


SCHEMA = "iris_test_workflow_source_policy_impact_v1"
SUCCESSOR_TEST_ROOT = "Iris/validation/test_workflow_consolidation/tests"


def policy_sources(payload: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, classification_key in (
        ("reviewed_sources", "classification"),
        ("planned_sources", "classification"),
        ("additional_sources", "classification"),
        ("excluded_sources", None),
        ("mixed_sources", "default_classification"),
    ):
        for row in payload.get(key, []):
            source = row.get("source_file")
            if source:
                result[source] = "excluded" if classification_key is None else str(row.get(classification_key, ""))
    return result


def pytest_testpaths(repository: Path) -> list[str]:
    parser = configparser.ConfigParser()
    parser.read(repository / "pytest.ini", encoding="utf-8")
    value = parser.get("pytest", "testpaths", fallback="")
    return [line.strip().replace("\\", "/") for line in value.splitlines() if line.strip()]


def is_under(source: str, prefix: str) -> bool:
    normalized = prefix.rstrip("/")
    return source == normalized or source.startswith(normalized + "/")


def collect_source(repository: Path, source: str) -> dict[str, Any]:
    command = [
        sys.executable,
        "-B",
        "-m",
        "pytest",
        "-s",
        "--collect-only",
        "-q",
        "-p",
        "no:cacheprovider",
        source,
    ]
    result = subprocess.run(
        command,
        cwd=repository,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    collected = [
        line.strip()
        for line in result.stdout.splitlines()
        if "::test_" in line and not line.lstrip().startswith("<")
    ]
    return {
        "command": command[1:],
        "exit_code": result.returncode,
        "collected_node_ids": collected,
        "collection_succeeded": result.returncode == 0,
    }


def classify(repository: Path) -> dict[str, Any]:
    repository = repository.resolve()
    subject = subject_identity(repository)
    source_policy = read_json(repository / "Iris/_docs/round3/round3_pytest_source_classification.json")
    policy = policy_sources(source_policy)
    testpaths = pytest_testpaths(repository)
    tracked = git(repository, "ls-files", "--", SUCCESSOR_TEST_ROOT).splitlines()
    sources = sorted(
        source.replace("\\", "/")
        for source in tracked
        if Path(source).name.startswith("test_") and source.endswith(".py")
    )
    require(sources, "no tracked successor test sources were found")
    rows: list[dict[str, Any]] = []
    for source in sources:
        default_member = any(is_under(source, prefix) for prefix in testpaths)
        controlled_member = (
            is_under(source, "Iris/build/description/v2/tests")
            or source in policy
        )
        collection = collect_source(repository, source)
        disposition = policy.get(source, "not_applicable")
        if default_member or controlled_member:
            disposition = policy.get(source, "BLOCKED")
        rows.append(
            {
                "source_file": source,
                "default_pytest_discovery_member": default_member,
                "round3_controlled_source_member": controlled_member,
                "explicit_path_only": not default_member and not controlled_member,
                "source_policy_disposition": disposition,
                "authority_transaction_required": default_member or controlled_member,
                "evidence_command_and_receipt": collection,
            }
        )
    errors = [
        row["source_file"]
        for row in rows
        if not row["evidence_command_and_receipt"]["collection_succeeded"]
        or row["source_policy_disposition"] == "BLOCKED"
    ]
    return {
        "schema_version": SCHEMA,
        "status": "PASS" if not errors else "FAIL",
        "target_subject": subject,
        "default_testpaths": testpaths,
        "expected_disposition": "not_applicable",
        "source_count": len(rows),
        "sources": rows,
        "blocking_sources": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify successor tracked test source policy impact")
    parser.add_argument("--target-repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = classify(args.target_repository)
    write_json(args.output, report)
    require(report["status"] == "PASS", "successor source-policy impact is blocking")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
