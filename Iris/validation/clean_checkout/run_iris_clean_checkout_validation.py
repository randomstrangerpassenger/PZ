"""Build the B0 clean-checkout source and dependency census.

This command does not import or execute repository tests. It reads an exact Git
tree, parses tracked Python test sources, and writes all generated records to a
caller-supplied directory outside the checkout.
"""

from __future__ import annotations

import argparse
import ast
import configparser
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from .iris_clean_checkout_validation_common import (
        CleanCheckoutError,
        blob_id,
        bytes_at_commit,
        canonical_json_bytes,
        ensure_external_root,
        git_identity,
        git_text,
        json_at_commit,
        resolved_repo,
        sha256_bytes,
        sha256_file,
        tracked_paths,
        validate_external_environment,
        write_json_external,
    )
except ImportError:
    from iris_clean_checkout_validation_common import (
        CleanCheckoutError,
        blob_id,
        bytes_at_commit,
        canonical_json_bytes,
        ensure_external_root,
        git_identity,
        git_text,
        json_at_commit,
        resolved_repo,
        sha256_bytes,
        sha256_file,
        tracked_paths,
        validate_external_environment,
        write_json_external,
    )


TAXONOMY_PATH = "Iris/_docs/round3/round3_test_taxonomy.json"
REQUIRED_MANIFEST_PATH = (
    "Iris/_docs/round3/current_route_required_validations.json"
)
PYTEST_INI_PATH = "pytest.ini"
CANONICAL_GATE_PATH = (
    "Iris/validation/clean_checkout/contracts/canonical_gate.json"
)
PHASE0_ENVIRONMENT_BINDING_PATH = (
    "Iris/validation/clean_checkout/authority/"
    "phase0_ratification_attempt_0002.json"
)
OUTPUT_POLICY_PATH = (
    "Iris/validation/clean_checkout/contracts/output_policy.json"
)
REPOSITORY_IMPORT_PREFIXES = (
    "",
    "Iris",
    "Iris/evidence/rightclick",
    "Iris/build",
    "Iris/build/description/v2",
    "Iris/build/description/v2/tests",
    "Iris/build/description/v2/tools",
    "Iris/build/description/v2/tools/build",
    "Iris/build/tests",
)


def _test_sources(paths: list[str]) -> list[str]:
    return sorted(
        path
        for path in paths
        if Path(path).name.startswith("test_") and path.endswith(".py")
    )


def _parse_pytest_ini(payload: bytes) -> tuple[list[str], list[str], list[str]]:
    parser = configparser.ConfigParser()
    parser.read_string(payload.decode("utf-8"))
    section = parser["pytest"]
    testpaths = section.get("testpaths", "").split()
    addopts = section.get("addopts", "").split()
    ignored = sorted(
        token.split("=", 1)[1]
        for token in addopts
        if token.startswith("--ignore=")
    )
    norecursedirs = section.get("norecursedirs", "").split()
    return testpaths, ignored, norecursedirs


def _under_configured_root(path: str, testpaths: list[str]) -> bool:
    for configured in testpaths:
        configured = configured.rstrip("/")
        if path == configured or path.startswith(f"{configured}/"):
            return True
    return False


def _taxonomy_indexes(
    taxonomy: dict[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_id: dict[str, dict[str, Any]] = {}
    for row in taxonomy["rows"]:
        by_source[row["source_file"]].append(row)
        by_id[row["test_id"]] = row
    return by_source, by_id


def _required_test_ids(manifest: dict[str, Any]) -> set[str]:
    return {
        row["test_id"]
        for row in manifest.get("required_tests", [])
        if row.get("required") is True
    }


def _canonical_gate_sources(
    contract: dict[str, Any],
    taxonomy: dict[str, Any],
) -> list[str]:
    selection = contract["test_selection"]
    if selection["kind"] != "taxonomy_contract":
        raise CleanCheckoutError(
            f"unsupported test selection: {selection['kind']}"
        )
    excluded_paths = set(selection.get("excluded_paths", []))
    selected_paths = {
        row["source_file"]
        for row in taxonomy["rows"]
        if row["contract_class"] == selection["contract_class"]
        and row["state"] == selection["state"]
        and row["source_file"] not in excluded_paths
    }
    selected_paths.update(selection.get("additional_paths", []))
    if not selected_paths:
        raise CleanCheckoutError("canonical gate selected no test sources")
    return sorted(selected_paths)


def _imports(
    source: bytes,
    source_path: str,
    *,
    current_module: str | None = None,
    current_is_package: bool = False,
) -> list[tuple[str, bool]]:
    try:
        tree = ast.parse(source, filename=source_path)
    except SyntaxError as exc:
        raise CleanCheckoutError(f"cannot parse {source_path}: {exc}") from exc
    modules: set[tuple[str, bool]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update((alias.name, False) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                base = node.module
            elif current_module:
                package_parts = current_module.split(".")
                if not current_is_package:
                    package_parts = package_parts[:-1]
                trim_count = node.level - 1
                if trim_count:
                    package_parts = package_parts[:-trim_count]
                if node.module:
                    package_parts.extend(node.module.split("."))
                base = ".".join(package_parts)
            else:
                base = None
            if base:
                modules.add((base, False))
                modules.update(
                    (f"{base}.{alias.name}", True)
                    for alias in node.names
                    if alias.name != "*"
                )
    return sorted(modules)


def _module_candidates(module: str) -> list[str]:
    module_path = module.replace(".", "/")
    candidates: list[str] = []
    for prefix in REPOSITORY_IMPORT_PREFIXES:
        joined = f"{prefix}/{module_path}" if prefix else module_path
        candidates.extend((f"{joined}.py", f"{joined}/__init__.py"))
    return candidates


def _resolve_repository_module(
    module: str,
    tracked: set[str],
    discovery_root: Path | None,
) -> dict[str, Any]:
    candidates = _module_candidates(module)
    for candidate in candidates:
        if candidate in tracked:
            return {
                "resolved_path": candidate,
                "tracking_state": "tracked",
                "dependency_class": "required_tracked_source",
                "provenance": "exact_subject_tree",
            }
    for prefix in REPOSITORY_IMPORT_PREFIXES:
        joined = (
            f"{prefix}/{module.replace('.', '/')}"
            if prefix
            else module.replace(".", "/")
        )
        if any(path.startswith(f"{joined}/") for path in tracked):
            return {
                "resolved_path": f"{joined}/",
                "tracking_state": "tracked",
                "dependency_class": "required_tracked_source",
                "provenance": "exact_subject_tree_namespace_package",
            }
    if discovery_root is not None:
        for candidate in candidates:
            ambient_path = discovery_root / candidate
            if ambient_path.is_file():
                return {
                    "resolved_path": candidate,
                    "tracking_state": "ambient_untracked_or_ignored_candidate",
                    "dependency_class": "required_tracked_source",
                    "provenance": {
                        "discovery_path": ambient_path.as_posix(),
                        "sha256": sha256_file(ambient_path),
                    },
                }
        for prefix in REPOSITORY_IMPORT_PREFIXES:
            joined = (
                f"{prefix}/{module.replace('.', '/')}"
                if prefix
                else module.replace(".", "/")
            )
            ambient_directory = discovery_root / joined
            if ambient_directory.is_dir():
                return {
                    "resolved_path": f"{joined}/",
                    "tracking_state": "ambient_untracked_or_ignored_candidate",
                    "dependency_class": "required_tracked_source",
                    "provenance": {
                        "discovery_path": ambient_directory.as_posix(),
                        "sha256": None,
                    },
                }
    top_level = module.split(".", 1)[0]
    if top_level in sys.stdlib_module_names:
        return {
            "resolved_path": None,
            "tracking_state": "external_environment",
            "dependency_class": "external_environment_dependency",
            "provenance": "python_standard_library",
        }
    if top_level in {"pytest", "_pytest"}:
        return {
            "resolved_path": None,
            "tracking_state": "external_environment",
            "dependency_class": "external_environment_dependency",
            "provenance": "frozen_external_environment_receipt",
        }
    return {
        "resolved_path": None,
        "tracking_state": "unresolved",
        "dependency_class": "unresolved",
        "provenance": "static_import_resolution_found_no_tracked_or_discovery_candidate",
    }


def build_source_census(
    repo: Path,
    commit: str,
    output_root: Path,
    discovery_root: Path | None,
) -> dict[str, Any]:
    subject = git_identity(repo, commit)
    commit = subject["commit"]
    paths = tracked_paths(repo, commit)
    tracked = set(paths)
    sources = _test_sources(paths)
    taxonomy = json_at_commit(repo, commit, TAXONOMY_PATH)
    gate_contract = json_at_commit(repo, commit, CANONICAL_GATE_PATH)
    gate_sources = set(_canonical_gate_sources(gate_contract, taxonomy))
    required_manifest = json_at_commit(repo, commit, REQUIRED_MANIFEST_PATH)
    taxonomy_by_source, taxonomy_by_id = _taxonomy_indexes(taxonomy)
    required_ids = _required_test_ids(required_manifest)
    testpaths, ignored_paths, norecursedirs = _parse_pytest_ini(
        bytes_at_commit(repo, commit, PYTEST_INI_PATH)
    )

    source_rows: list[dict[str, Any]] = []
    dependency_rows: list[dict[str, Any]] = []
    required_sources = {
        row["source_file"]
        for test_id, row in taxonomy_by_id.items()
        if test_id in required_ids
    }

    for source_path in sources:
        taxonomy_rows = taxonomy_by_source.get(source_path, [])
        source_rows.append(
            {
                "source_path": source_path,
                "source_blob_id": blob_id(repo, commit, source_path),
                "configured_pytest_root": _under_configured_root(
                    source_path, testpaths
                ),
                "explicit_pytest_ignore": source_path in ignored_paths,
                "taxonomy_contract_classes": sorted(
                    {row["contract_class"] for row in taxonomy_rows}
                ),
                "taxonomy_identity_count": len(taxonomy_rows),
                "required_manifest_member": source_path in required_sources,
                "canonical_gate_member": source_path in gate_sources,
                "discovery_state": "tracked_source_not_live_collected",
            }
        )
        if source_path not in gate_sources:
            continue
        visited_modules: set[tuple[str, str | None]] = set()

        def visit_module(
            module: str,
            optional_submodule: bool,
            depth: int,
            parent_module: str | None,
        ) -> None:
            resolved = _resolve_repository_module(
                module, tracked, discovery_root
            )
            if (
                optional_submodule
                and resolved["tracking_state"] == "unresolved"
            ):
                return
            visit_key = (module, resolved["resolved_path"])
            if visit_key in visited_modules:
                return
            visited_modules.add(visit_key)
            dependency_rows.append(
                {
                    "test_source": source_path,
                    "import_module": module,
                    "dependency_depth": depth,
                    "parent_module": parent_module,
                    **resolved,
                }
            )
            resolved_path = resolved["resolved_path"]
            if (
                not resolved_path
                or not resolved_path.endswith(".py")
                or resolved["tracking_state"]
                not in {"tracked", "ambient_untracked_or_ignored_candidate"}
            ):
                return
            if resolved["tracking_state"] == "tracked":
                module_source = bytes_at_commit(repo, commit, resolved_path)
            elif discovery_root is not None:
                module_source = (discovery_root / resolved_path).read_bytes()
            else:
                return
            for child_module, child_optional in _imports(
                module_source,
                resolved_path,
                current_module=module,
                current_is_package=resolved_path.endswith("/__init__.py"),
            ):
                visit_module(
                    child_module,
                    child_optional,
                    depth + 1,
                    module,
                )

        for module, optional_submodule in _imports(
            bytes_at_commit(repo, commit, source_path), source_path
        ):
            visit_module(module, optional_submodule, 0, None)

    source_inventory = {
        "schema_version": "iris-clean-checkout-test-inventory-v1",
        "inventory_state": "source_census_pending_live_collection",
        "subject": subject,
        "pytest_configuration": {
            "testpaths": testpaths,
            "explicit_ignores": ignored_paths,
            "norecursedirs": norecursedirs,
        },
        "source_rows": source_rows,
        "identity_rows": [],
        "collection_errors": [],
        "counts": {
            "tracked_test_source_count": len(source_rows),
            "configured_root_source_count": sum(
                row["configured_pytest_root"] for row in source_rows
            ),
            "outside_configured_root_source_count": sum(
                not row["configured_pytest_root"] for row in source_rows
            ),
            "explicitly_ignored_source_count": sum(
                row["explicit_pytest_ignore"] for row in source_rows
            ),
            "taxonomy_fallback_identity_count": sum(
                row["taxonomy_identity_count"] for row in source_rows
            ),
            "live_collection_identity_count": 0,
        },
    }
    dependency_ledger = {
        "schema_version": "iris-clean-checkout-dependency-edge-ledger-v1",
        "ledger_state": "static_import_census",
        "subject": subject,
        "edges": dependency_rows,
        "counts": {
            "edge_count": len(dependency_rows),
            "tracked_dependency_edge_count": sum(
                row["tracking_state"] == "tracked"
                for row in dependency_rows
            ),
            "external_environment_edge_count": sum(
                row["tracking_state"] == "external_environment"
                for row in dependency_rows
            ),
            "ambient_dependency_candidate_edge_count": sum(
                row["tracking_state"]
                == "ambient_untracked_or_ignored_candidate"
                for row in dependency_rows
            ),
            "unresolved_edge_count": sum(
                row["tracking_state"] == "unresolved"
                for row in dependency_rows
            ),
        },
    }

    inventory_path = output_root / "test_inventory.json"
    dependency_path = output_root / "dependency_edge_ledger.json"
    inventory_sha256 = write_json_external(
        repo, inventory_path, source_inventory
    )
    dependency_sha256 = write_json_external(
        repo, dependency_path, dependency_ledger
    )
    d0_manifest = {
        "schema_version": "iris-clean-checkout-d0-manifest-v1",
        "manifest_state": "source_census_pending_live_collection",
        "subject": subject,
        "test_inventory": {
            "path": inventory_path.as_posix(),
            "sha256": inventory_sha256,
        },
        "dependency_edge_ledger": {
            "path": dependency_path.as_posix(),
            "sha256": dependency_sha256,
        },
        "tracked_test_source_count": len(source_rows),
        "live_collection_identity_count": None,
        "d0_frozen": False,
        "tests_executed": False,
    }
    d0_path = output_root / "d0_manifest.json"
    d0_sha256 = write_json_external(repo, d0_path, d0_manifest)
    return {
        "subject": subject,
        "test_inventory_path": inventory_path.as_posix(),
        "test_inventory_sha256": inventory_sha256,
        "dependency_edge_ledger_path": dependency_path.as_posix(),
        "dependency_edge_ledger_sha256": dependency_sha256,
        "d0_manifest_path": d0_path.as_posix(),
        "d0_manifest_sha256": d0_sha256,
        "counts": {
            **source_inventory["counts"],
            **dependency_ledger["counts"],
        },
    }


def _status_snapshot(repo: Path) -> str:
    return git_text(
        repo,
        "status",
        "--porcelain=v2",
        "--untracked-files=all",
        "--ignored=matching",
    )


def _load_pytest_result(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "schema_version": "iris-clean-checkout-pytest-result-v1",
            "mode": "unknown",
            "status": "FAIL",
            "pytest_version": None,
            "exit_status": None,
            "identity_rows": [],
            "collection_errors": [
                {
                    "node_id": "",
                    "message": "pytest result plugin did not write its result",
                }
            ],
            "counts": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def run_gate(
    repo: Path,
    commit: str,
    python_executable: Path,
    environment_receipt: Path,
    output_root: Path,
    *,
    collect_only: bool,
) -> dict[str, Any]:
    subject = git_identity(repo, commit)
    head = git_identity(repo, "HEAD")
    if head != subject:
        raise CleanCheckoutError(
            f"checkout HEAD does not match subject: {head} != {subject}"
        )
    before_status = _status_snapshot(repo)
    if before_status:
        raise CleanCheckoutError(
            "gate requires a clean checkout, including no ignored generated "
            f"state:\n{before_status}"
        )
    if any(output_root.iterdir()):
        raise CleanCheckoutError(
            f"output root must be empty before a gate run: {output_root}"
        )
    python_executable = python_executable.resolve()
    environment_receipt = environment_receipt.resolve()
    if not python_executable.is_file():
        raise CleanCheckoutError(
            f"external interpreter is missing: {python_executable}"
        )
    if not environment_receipt.is_file():
        raise CleanCheckoutError(
            f"environment receipt is missing: {environment_receipt}"
        )

    phase0 = json_at_commit(
        repo,
        subject["commit"],
        PHASE0_ENVIRONMENT_BINDING_PATH,
    )
    environment_contract = phase0["implementation_contract_delta"]["OR-06"]
    environment_verification = validate_external_environment(
        python_executable,
        environment_receipt,
        environment_contract,
    )
    contract = json_at_commit(
        repo, subject["commit"], CANONICAL_GATE_PATH
    )
    output_policy = json_at_commit(
        repo,
        subject["commit"],
        OUTPUT_POLICY_PATH,
    )
    if (
        output_policy["repository_local_generated_output_allowed"] is not False
        or output_policy["administrator_token_required"] is not False
        or output_policy["windows_privileged_auditing_required"] is not False
    ):
        raise CleanCheckoutError("unsupported clean-checkout output policy")
    command_contract = contract["command"]
    selection = contract["test_selection"]
    taxonomy = json_at_commit(
        repo, subject["commit"], selection["taxonomy_path"]
    )
    selected_paths = _canonical_gate_sources(contract, taxonomy)
    command = [
        str(python_executable),
        *command_contract["python_flags"],
        "-m",
        command_contract["module"],
        *command_contract["arguments"],
        *selected_paths,
    ]
    if collect_only:
        command.append("--collect-only")

    pytest_result_path = output_root / "pytest_result.json"
    system_temp = output_root / "system-temp"
    test_output = output_root / "test-output"
    system_temp.mkdir(parents=True, exist_ok=True)
    test_output.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    for variable in output_policy["cleared_ambient_environment"]:
        environment.pop(variable, None)
    environment.update(output_policy["required_environment"])
    environment.update(
        {
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PYTHONPYCACHEPREFIX": str(system_temp / "pycache"),
            "IRIS_CLEAN_CHECKOUT_PYTEST_RESULT": str(
                pytest_result_path
            ),
            "IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT": str(test_output),
            "TEMP": str(system_temp),
            "TMP": str(system_temp),
            "TMPDIR": str(system_temp),
        }
    )
    completed = subprocess.run(
        command,
        cwd=repo,
        env=environment,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_path = output_root / "pytest.stdout.txt"
    stderr_path = output_root / "pytest.stderr.txt"
    stdout_path.write_bytes(completed.stdout)
    stderr_path.write_bytes(completed.stderr)

    raw_result = _load_pytest_result(pytest_result_path)
    if not pytest_result_path.exists():
        write_json_external(repo, pytest_result_path, raw_result)
    after_status = _status_snapshot(repo)
    identity_rows = sorted(
        (
            {
                "node_id": row["node_id"],
                "source_path": row["source_path"],
                "outcome": row["outcome"],
            }
            for row in raw_result.get("identity_rows", [])
        ),
        key=lambda row: row["node_id"],
    )
    identity_projection = [
        {
            "node_id": row["node_id"],
            "source_path": row["source_path"],
        }
        for row in identity_rows
    ]
    inventory_hash = sha256_bytes(
        canonical_json_bytes(identity_projection)
    )
    expected_outcome = "collected" if collect_only else "passed"
    status = (
        "PASS"
        if completed.returncode == 0
        and raw_result.get("status") == "PASS"
        and not before_status
        and not after_status
        and identity_rows
        and all(
            row["outcome"] == expected_outcome
            for row in identity_rows
        )
        else "FAIL"
    )
    normalized_command = [
        "<external-python>",
        *command_contract["python_flags"],
        "-m",
        command_contract["module"],
        *command_contract["arguments"],
        *selected_paths,
    ]
    if collect_only:
        normalized_command.append("--collect-only")
    canonical_result = {
        "schema_version": "iris-clean-checkout-canonical-result-v2",
        "mode": "collect_only" if collect_only else "execute",
        "status": status,
        "subject": subject,
        "canonical_gate_blob_id": blob_id(
            repo, subject["commit"], CANONICAL_GATE_PATH
        ),
        "phase0_environment_binding_blob_id": blob_id(
            repo,
            subject["commit"],
            PHASE0_ENVIRONMENT_BINDING_PATH,
        ),
        "output_policy_blob_id": blob_id(
            repo,
            subject["commit"],
            OUTPUT_POLICY_PATH,
        ),
        "normalized_command": normalized_command,
        "environment_verification": environment_verification,
        "pytest_version": raw_result.get("pytest_version"),
        "test_identity_count": len(identity_rows),
        "test_inventory_sha256": inventory_hash,
        "identity_rows": identity_rows,
        "collection_error_count": len(
            raw_result.get("collection_errors", [])
        ),
        "repository_clean_before": not before_status,
        "repository_clean_after": not after_status,
    }
    canonical_path = output_root / "canonical_result.json"
    canonical_sha256 = write_json_external(
        repo, canonical_path, canonical_result
    )
    receipt = {
        "schema_version": "iris-clean-checkout-gate-run-receipt-v2",
        "status": status,
        "mode": canonical_result["mode"],
        "subject": subject,
        "checkout_path": repo.as_posix(),
        "actual_command": command,
        "environment_receipt_path": environment_receipt.as_posix(),
        "environment_verification": environment_verification,
        "python_executable_path": python_executable.as_posix(),
        "python_executable_sha256": environment_verification[
            "interpreter_sha256"
        ],
        "pytest_return_code": completed.returncode,
        "pytest_result": {
            "path": pytest_result_path.as_posix(),
            "sha256": sha256_file(pytest_result_path),
        },
        "stdout": {
            "path": stdout_path.as_posix(),
            "sha256": sha256_file(stdout_path),
        },
        "stderr": {
            "path": stderr_path.as_posix(),
            "sha256": sha256_file(stderr_path),
        },
        "canonical_result": {
            "path": canonical_path.as_posix(),
            "sha256": canonical_sha256,
        },
        "test_identity_count": len(identity_rows),
        "test_inventory_sha256": inventory_hash,
        "repository_status_before": before_status.splitlines(),
        "repository_status_after": after_status.splitlines(),
    }
    receipt_path = output_root / "run_receipt.json"
    receipt_sha256 = write_json_external(
        repo, receipt_path, receipt
    )
    return {
        "status": status,
        "mode": canonical_result["mode"],
        "subject": subject,
        "test_identity_count": len(identity_rows),
        "test_inventory_sha256": inventory_hash,
        "canonical_result_path": canonical_path.as_posix(),
        "canonical_result_sha256": canonical_sha256,
        "run_receipt_path": receipt_path.as_posix(),
        "run_receipt_sha256": receipt_sha256,
        "pytest_return_code": completed.returncode,
        "repository_clean_after": not after_status,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    source = subparsers.add_parser("source-census")
    source.add_argument("--repo", required=True)
    source.add_argument("--commit", required=True)
    source.add_argument("--output-root", required=True)
    source.add_argument("--discovery-root")
    gate = subparsers.add_parser("gate")
    gate.add_argument("--repo", required=True)
    gate.add_argument("--commit", required=True)
    gate.add_argument("--python", required=True)
    gate.add_argument("--environment-receipt", required=True)
    gate.add_argument("--output-root", required=True)
    gate.add_argument("--collect-only", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        repo = resolved_repo(args.repo)
        output_root = ensure_external_root(repo, args.output_root)
        if args.command == "source-census":
            discovery_root = (
                Path(args.discovery_root).resolve()
                if args.discovery_root
                else None
            )
            result = build_source_census(
                repo, args.commit, output_root, discovery_root
            )
        else:
            result = run_gate(
                repo,
                args.commit,
                Path(args.python),
                Path(args.environment_receipt),
                output_root,
                collect_only=args.collect_only,
            )
    except (CleanCheckoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("status", "PASS") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
