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
import shutil
import stat
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from Iris.validation.clean_checkout import (
    iris_clean_checkout_validation_common as clean_checkout_common,
)
from Iris.validation.clean_checkout.iris_clean_checkout_validation_common import (
    CleanCheckoutError,
    blob_id,
    bytes_at_commit,
    canonical_compact_json_bytes,
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
FULL_REPOSITORY_GATE_PATH = (
    "Iris/validation/clean_checkout/contracts/full_repository_gate.json"
)
PHASE0_ENVIRONMENT_BINDING_PATH = (
    "Iris/validation/clean_checkout/authority/"
    "phase0_ratification_attempt_0002.json"
)
OUTPUT_POLICY_PATH = (
    "Iris/validation/clean_checkout/contracts/output_policy.json"
)
EVIDENCE_OWNER_APPROVAL_PATH = (
    "Iris/_docs/refactor/repository_evidence_lightweighting/"
    "owner_policy_approval.json"
)
RUNNER_PATH = (
    "Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py"
)
COMMON_MODULE_PATH = (
    "Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py"
)
REPOSITORY_IMPORT_PREFIXES = (
    "",
    "Iris",
    "Iris/_docs/round3/registry_runtime_compatibility/bootstrap",
    "Iris/evidence/rightclick",
    "Iris/build",
    "Iris/build/description/v2",
    "Iris/build/description/v2/tests",
    "Iris/build/description/v2/tools",
    "Iris/build/description/v2/tools/build",
    "Iris/build/tests",
    "Iris/test",
    "Iris/validation/clean_checkout",
    "Iris/validation/clean_checkout/tests",
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


def _full_required_pytest_sources(
    contract: dict[str, Any],
    taxonomy: dict[str, Any],
) -> list[str]:
    selection = contract["required_pytest_selection"]
    selected_paths = {
        row["source_file"]
        for row in taxonomy["rows"]
        if row["contract_class"] == selection["contract_class"]
        and row["state"] == selection["state"]
    }
    selected_paths.update(selection["additional_source_paths"])
    selected_paths.update(_explicit_current_required_paths(contract))
    selected_paths.update(
        node_id.split("::", 1)[0]
        for node_id in selection["additional_node_ids"]
    )
    if not selected_paths:
        raise CleanCheckoutError("full repository gate selected no pytest sources")
    return sorted(selected_paths)


def _explicit_current_required_paths(
    contract: dict[str, Any],
) -> list[str]:
    rows = contract["source_disposition_policy"].get(
        "explicit_current_required_sources", []
    )
    paths: list[str] = []
    for row in rows:
        path = row.get("path")
        reason = row.get("reason")
        if (
            not isinstance(path, str)
            or not path
            or path != path.strip()
            or "\\" in path
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            raise CleanCheckoutError(
                "invalid explicit current-required source declaration"
            )
        paths.append(path)
    if len(paths) != len(set(paths)):
        raise CleanCheckoutError(
            "duplicate explicit current-required source declaration"
        )
    return sorted(paths)


def _full_required_source_roles(
    contract: dict[str, Any],
    taxonomy: dict[str, Any],
) -> dict[str, dict[str, str]]:
    selection = contract["required_pytest_selection"]
    roles: dict[str, dict[str, str]] = {}
    current_sources = {
        row["source_file"]
        for row in taxonomy["rows"]
        if row["contract_class"] == selection["contract_class"]
        and row["state"] == selection["state"]
    }
    for path in current_sources:
        roles[path] = {
            "execution_role": "required_pytest",
            "authority_class": "required_tracked_source",
            "classification_basis": "round3_current_ok_taxonomy",
        }
    for path in selection["additional_source_paths"]:
        roles[path] = {
            "execution_role": "required_pytest",
            "authority_class": "required_tracked_source",
            "classification_basis": "full_gate_additional_source",
        }
    for node_id in selection["additional_node_ids"]:
        path = node_id.split("::", 1)[0]
        roles[path] = {
            "execution_role": "mixed_required_pytest",
            "authority_class": "required_tracked_source",
            "classification_basis": "full_gate_explicit_required_identities",
        }
    for row in contract["required_standalone_validations"]:
        roles[row["path"]] = {
            "execution_role": "required_standalone_command",
            "authority_class": "required_tracked_source",
            "classification_basis": row["command_id"],
        }
    for row in contract["source_disposition_policy"].get(
        "explicit_historical_optional_sources", []
    ):
        roles[row["path"]] = {
            "execution_role": "not_required",
            "authority_class": "historical_optional_evidence",
            "classification_basis": row["reason"],
        }
    for row in contract["source_disposition_policy"].get(
        "explicit_dedicated_route_sources", []
    ):
        if row.get("owner_decision") != "not_applicable_dedicated_route":
            raise CleanCheckoutError(
                "dedicated-route source lacks explicit owner disposition"
            )
        roles[row["path"]] = {
            "execution_role": "not_required",
            "authority_class": "dedicated_route_validation",
            "classification_basis": row["reason"],
        }
    for row in contract["source_disposition_policy"].get(
        "hermetic_test_fixture_sources", []
    ):
        roles[row["path"]] = {
            "execution_role": "not_required",
            "authority_class": "hermetic_test_fixture",
            "classification_basis": row["reason"],
        }
    for row in contract["source_disposition_policy"][
        "obsolete_or_misrouted_sources"
    ]:
        roles[row["path"]] = {
            "execution_role": "not_required",
            "authority_class": "obsolete_or_misrouted_test_dependency",
            "classification_basis": row["reason"],
        }
    for path in _explicit_current_required_paths(contract):
        roles[path] = {
            "execution_role": "required_pytest",
            "authority_class": "required_tracked_source",
            "classification_basis": "explicit_current_required_source",
        }
    return roles


def _classify_full_test_source(
    source_path: str,
    roles: dict[str, dict[str, str]],
) -> dict[str, str]:
    if source_path in roles:
        return roles[source_path]
    if (
        source_path.startswith("Iris/build/description/v2/tests/test_")
        and source_path.endswith(".py")
    ):
        return {
            "execution_role": "not_required",
            "authority_class": "historical_optional_evidence",
            "classification_basis": (
                "tracked description-v2 test source without a current, ok "
                "Round 3 taxonomy identity"
            ),
        }
    raise CleanCheckoutError(
        f"unclassified tracked test source in full gate: {source_path}"
    )


def _validate_explicit_current_required_classifications(
    contract: dict[str, Any],
    classifications: dict[str, dict[str, str]],
) -> None:
    for path in _explicit_current_required_paths(contract):
        classification = classifications.get(path)
        if (
            classification is None
            or classification.get("execution_role") != "required_pytest"
            or classification.get("authority_class")
            != "required_tracked_source"
            or classification.get("classification_basis")
            != "explicit_current_required_source"
        ):
            raise CleanCheckoutError(
                "explicit current-required source was classified as "
                f"historical/optional or omitted: {path}"
            )


def _validate_explicit_required_dependencies(
    contract: dict[str, Any],
    tracked: set[str],
    gate_sources: set[str],
) -> list[dict[str, str]]:
    rows = contract.get("required_test_dependency_policy", {}).get(
        "explicit_direct_dependencies", []
    )
    validated: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    required_keys = {
        "test_source",
        "path",
        "relationship",
        "dependency_role",
        "authority_class",
        "reason",
    }
    for row in rows:
        if not isinstance(row, dict) or set(row) != required_keys:
            raise CleanCheckoutError(
                "invalid explicit required-test dependency schema"
            )
        test_source = row["test_source"]
        path = row["path"]
        key = (test_source, path)
        if (
            not isinstance(test_source, str)
            or test_source not in gate_sources
            or not isinstance(path, str)
            or path not in tracked
            or key in seen
            or row["relationship"] != "direct"
            or not isinstance(row["dependency_role"], str)
            or not row["dependency_role"].strip()
            or row["authority_class"] != "required_tracked_source"
            or not isinstance(row["reason"], str)
            or not row["reason"].strip()
        ):
            raise CleanCheckoutError(
                "invalid explicit required-test dependency: "
                f"{test_source!r} -> {path!r}"
            )
        seen.add(key)
        validated.append({key: row[key] for key in sorted(required_keys)})
    return sorted(
        validated,
        key=lambda row: (row["test_source"], row["path"]),
    )


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


def _required_dependency_paths(
    repo: Path,
    commit: str,
    source_paths: set[str],
    tracked: set[str],
) -> set[str]:
    resolved_paths: set[str] = set()
    visited_modules: set[tuple[str, str | None]] = set()

    def visit_module(module: str, optional_submodule: bool) -> None:
        resolved = _resolve_repository_module(module, tracked, None)
        if optional_submodule and resolved["tracking_state"] == "unresolved":
            return
        visit_key = (module, resolved["resolved_path"])
        if visit_key in visited_modules:
            return
        visited_modules.add(visit_key)
        resolved_path = resolved["resolved_path"]
        if not isinstance(resolved_path, str):
            return
        resolved_paths.add(resolved_path)
        if (
            not resolved_path.endswith(".py")
            or resolved["tracking_state"] != "tracked"
        ):
            return
        for child_module, child_optional in _imports(
            bytes_at_commit(repo, commit, resolved_path),
            resolved_path,
            current_module=module,
            current_is_package=resolved_path.endswith("/__init__.py"),
        ):
            visit_module(child_module, child_optional)

    for source_path in sorted(source_paths):
        for module, optional_submodule in _imports(
            bytes_at_commit(repo, commit, source_path),
            source_path,
        ):
            visit_module(module, optional_submodule)
    return resolved_paths


def _validate_explicit_tool_dispositions(
    contract: dict[str, Any],
    tracked: set[str],
    required_dependency_paths: set[str],
) -> list[dict[str, str]]:
    rows = contract["tool_disposition_policy"]["explicit_tool_roles"]
    compiler_paths = set(
        contract["g5_required_evidence"]["compiler_identity"][
            "ordered_paths"
        ]
    )
    validated: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        path = row.get("path")
        if (
            not isinstance(path, str)
            or not path
            or path in seen
            or path not in tracked
            or row.get("execution_role") != "not_required"
            or row.get("authority_class")
            != "historical_optional_evidence"
            or row.get("tool_role")
            != "attempt_generation_evidence_tooling"
            or row.get("attempt_id")
            != contract["g5_required_evidence"]["primary_attempt_id"]
            or not isinstance(row.get("reason"), str)
            or not row["reason"].strip()
        ):
            raise CleanCheckoutError(
                f"invalid explicit G5 tool disposition: {path!r}"
            )
        if path in compiler_paths:
            raise CleanCheckoutError(
                f"G5 evidence tool is a compiler constituent: {path}"
            )
        if path in required_dependency_paths:
            raise CleanCheckoutError(
                f"G5 evidence tool is a required-test dependency: {path}"
            )
        seen.add(path)
        validated.append(
            {
                "path": path,
                "execution_role": row["execution_role"],
                "authority_class": row["authority_class"],
                "tool_role": row["tool_role"],
                "attempt_id": row["attempt_id"],
            }
        )
    return sorted(validated, key=lambda row: row["path"])


def _validate_consumer_integration_evidence(
    repo: Path,
    commit: str,
    contract: dict[str, Any],
    tracked: set[str],
    required_dependency_paths: set[str],
) -> list[dict[str, str]]:
    rows = contract.get("consumer_integration_evidence_policy", {}).get(
        "explicit_evidence_roles", []
    )
    validated: list[dict[str, str]] = []
    seen: set[str] = set()
    required_keys = {
        "evidence_id",
        "path",
        "sha256",
        "deterministic_result_hash",
        "execution_role",
        "authority_class",
        "evidence_role",
        "reason",
    }
    for row in rows:
        if not isinstance(row, dict) or set(row) != required_keys:
            raise CleanCheckoutError(
                "invalid consumer integration evidence schema"
            )
        path = row["path"]
        if (
            not isinstance(path, str)
            or path not in tracked
            or path in seen
            or path in required_dependency_paths
            or row["execution_role"] != "not_required"
            or row["authority_class"] != "historical_optional_evidence"
            or row["evidence_role"] != "consumer_integration_evidence"
            or not isinstance(row["evidence_id"], str)
            or not row["evidence_id"].strip()
            or not isinstance(row["reason"], str)
            or not row["reason"].strip()
        ):
            raise CleanCheckoutError(
                f"invalid consumer integration evidence disposition: {path!r}"
            )
        payload = bytes_at_commit(repo, commit, path)
        if sha256_bytes(payload) != row["sha256"]:
            raise CleanCheckoutError(
                f"consumer integration evidence SHA-256 mismatch: {path}"
            )
        try:
            result = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CleanCheckoutError(
                f"consumer integration evidence is not strict JSON: {path}"
            ) from exc
        if (
            not isinstance(result, dict)
            or result.get("deterministic_result_hash")
            != row["deterministic_result_hash"]
        ):
            raise CleanCheckoutError(
                "consumer integration evidence deterministic result hash "
                f"mismatch: {path}"
            )
        seen.add(path)
        validated.append({key: row[key] for key in sorted(required_keys)})
    return sorted(validated, key=lambda row: row["path"])


def _line_ending_sha256_variants(payload: bytes) -> set[str]:
    normalized = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return {
        sha256_bytes(normalized),
        sha256_bytes(normalized.replace(b"\n", b"\r\n")),
        sha256_bytes(normalized.replace(b"\n", b"\r")),
    }


def _normalized_compiler_rows(
    repo: Path, commit: str, ordered_paths: list[str]
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in ordered_paths:
        canonical = (
            bytes_at_commit(repo, commit, path)
            .replace(b"\r\n", b"\n")
            .replace(b"\r", b"\n")
        )
        rows.append({"path": path, "sha256_lf": sha256_bytes(canonical)})
    return rows


def _compiler_aggregate_sha256(
    algorithm_id: str, ordered_files: list[dict[str, str]]
) -> str:
    payload = {
        "algorithm_id": algorithm_id,
        "ordered_files": [
            {"path": row["path"], "sha256": row["sha256_lf"]}
            for row in ordered_files
        ],
    }
    return sha256_bytes(canonical_compact_json_bytes(payload))


def _git_is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-C",
            str(repo),
            "merge-base",
            "--is-ancestor",
            ancestor,
            descendant,
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


def _git_commit_is_available(repo: Path, commit: str) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-C",
            str(repo),
            "rev-parse",
            "--verify",
            f"{commit}^{{commit}}",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


def _validate_g5_compiler_identity_transition(
    repo: Path,
    subject_commit: str,
    compiler: dict[str, Any],
    transition: dict[str, Any],
    allow_owner_pruned_current_basis: bool,
) -> dict[str, Any]:
    expected_compiler_keys = {
        "algorithm_id",
        "historical_attested_aggregate_sha256",
        "current_aggregate_sha256",
        "ordered_paths",
        "successor_transition",
    }
    if set(compiler) != expected_compiler_keys:
        raise CleanCheckoutError("invalid G5 compiler identity contract schema")
    ordered_paths = compiler["ordered_paths"]
    if (
        not isinstance(ordered_paths, list)
        or len(ordered_paths) != 9
        or len(ordered_paths) != len(set(ordered_paths))
        or any(not isinstance(path, str) or not path for path in ordered_paths)
    ):
        raise CleanCheckoutError("invalid G5 compiler ordered path contract")
    expected_transition_keys = {
        "schema_version",
        "status",
        "authority",
        "record_mode",
        "claim_boundary",
        "algorithm_id",
        "historical_gate_integration_basis",
        "current_identity_basis",
        "changed_rows",
        "changed_constituent_count",
        "unchanged_constituent_count",
        "non_claims",
    }
    if (
        set(transition) != expected_transition_keys
        or transition["schema_version"]
        != "iris-clean-checkout-g5-compiler-identity-successor-v1"
        or transition["status"] != "PASS"
        or transition["algorithm_id"] != compiler["algorithm_id"]
        or not isinstance(transition["non_claims"], list)
        or not transition["non_claims"]
        or any(
            not isinstance(row, str) or not row.strip()
            for row in transition["non_claims"]
        )
    ):
        raise CleanCheckoutError("invalid G5 compiler successor transition schema")

    expected_basis_keys = {"commit", "tree", "aggregate_sha256", "ordered_files"}

    current_basis_was_pruned = False

    def validate_basis(name: str) -> tuple[dict[str, Any], list[dict[str, str]], str]:
        nonlocal current_basis_was_pruned
        basis = transition[name]
        if not isinstance(basis, dict) or set(basis) != expected_basis_keys:
            raise CleanCheckoutError(f"invalid G5 compiler {name} schema")
        basis_is_available = _git_commit_is_available(repo, basis["commit"])
        if not basis_is_available:
            if name != "current_identity_basis" or not allow_owner_pruned_current_basis:
                raise CleanCheckoutError(
                    f"G5 compiler {name} Git object is unavailable"
                )
            current_basis_was_pruned = True
            actual_rows = basis["ordered_files"]
        else:
            identity = git_identity(repo, basis["commit"])
            if identity != {"commit": basis["commit"], "tree": basis["tree"]}:
                raise CleanCheckoutError(f"G5 compiler {name} identity mismatch")
            actual_rows = _normalized_compiler_rows(
                repo, basis["commit"], ordered_paths
            )
        if basis["ordered_files"] != actual_rows:
            raise CleanCheckoutError(f"G5 compiler {name} ordered files mismatch")
        aggregate = _compiler_aggregate_sha256(
            compiler["algorithm_id"], actual_rows
        )
        if basis["aggregate_sha256"] != aggregate:
            raise CleanCheckoutError(f"G5 compiler {name} aggregate mismatch")
        return basis, actual_rows, aggregate

    historical, historical_rows, historical_aggregate = validate_basis(
        "historical_gate_integration_basis"
    )
    current_basis, current_basis_rows, current_aggregate = validate_basis(
        "current_identity_basis"
    )
    if current_basis_was_pruned:
        if not _git_is_ancestor(repo, historical["commit"], subject_commit):
            raise CleanCheckoutError("G5 compiler historical ancestry mismatch")
    elif (
        not _git_is_ancestor(repo, historical["commit"], current_basis["commit"])
        or not _git_is_ancestor(repo, current_basis["commit"], subject_commit)
    ):
        raise CleanCheckoutError("G5 compiler successor ancestry mismatch")
    subject_rows = _normalized_compiler_rows(repo, subject_commit, ordered_paths)
    if subject_rows != current_basis_rows:
        raise CleanCheckoutError("G5 current compiler identity changed after bridge basis")
    if not current_basis_was_pruned:
        for path in ordered_paths:
            basis_last_writer = git_text(
                repo,
                "log",
                "-1",
                "--format=%H",
                current_basis["commit"],
                "--",
                path,
            ).strip()
            subject_last_writer = git_text(
                repo,
                "log",
                "-1",
                "--format=%H",
                subject_commit,
                "--",
                path,
            ).strip()
            if (
                subject_last_writer != basis_last_writer
                or blob_id(repo, subject_commit, path)
                != blob_id(repo, current_basis["commit"], path)
            ):
                raise CleanCheckoutError(
                    f"G5 compiler path changed after bridge basis: {path}"
                )
    if (
        compiler["historical_attested_aggregate_sha256"]
        != historical_aggregate
        or compiler["current_aggregate_sha256"] != current_aggregate
    ):
        raise CleanCheckoutError("G5 compiler contract aggregate split mismatch")

    historical_by_path = {row["path"]: row for row in historical_rows}
    current_by_path = {row["path"]: row for row in current_basis_rows}
    expected_changed_rows: list[dict[str, str]] = []
    for path in ordered_paths:
        historical_sha = historical_by_path[path]["sha256_lf"]
        current_sha = current_by_path[path]["sha256_lf"]
        if historical_sha == current_sha:
            continue
        provenance_commit = (
            subject_commit if current_basis_was_pruned else current_basis["commit"]
        )
        last_writer_commit = git_text(
            repo,
            "log",
            "-1",
            "--format=%H",
            provenance_commit,
            "--",
            path,
        ).strip()
        last_writer_identity = git_identity(repo, last_writer_commit)
        if (
            not _git_is_ancestor(
                repo, last_writer_commit, provenance_commit
            )
            or _normalized_compiler_rows(repo, last_writer_commit, [path])[0][
                "sha256_lf"
            ]
            != current_sha
        ):
            raise CleanCheckoutError(
                f"G5 compiler last-writer provenance mismatch: {path}"
            )
        expected_changed_rows.append(
            {
                "path": path,
                "historical_sha256_lf": historical_sha,
                "current_sha256_lf": current_sha,
                "current_last_writer_commit": last_writer_identity["commit"],
                "current_last_writer_tree": last_writer_identity["tree"],
            }
        )
    if transition["changed_rows"] != expected_changed_rows:
        raise CleanCheckoutError("G5 compiler derived changed-row mismatch")
    if (
        transition["changed_constituent_count"] != len(expected_changed_rows)
        or transition["unchanged_constituent_count"]
        != len(ordered_paths) - len(expected_changed_rows)
    ):
        raise CleanCheckoutError("G5 compiler transition count mismatch")
    return {
        "algorithm_id": compiler["algorithm_id"],
        "ordered_path_count": len(ordered_paths),
        "historical_attested_aggregate_sha256": historical_aggregate,
        "current_aggregate_sha256": current_aggregate,
        "changed_constituent_count": len(expected_changed_rows),
        "unchanged_constituent_count": len(ordered_paths)
        - len(expected_changed_rows),
        "current_basis_validation_mode": (
            "owner_pruned_revalidated_from_subject"
            if current_basis_was_pruned
            else "exact_git_object"
        ),
    }


def _validate_g5_required_evidence(
    repo: Path,
    commit: str,
    contract: dict[str, Any],
    tracked: set[str],
) -> dict[str, Any]:
    owner_approval = json_at_commit(repo, commit, EVIDENCE_OWNER_APPROVAL_PATH)
    pruned_history = owner_approval["decisions"].get(
        "pruned_git_history_validation"
    )
    allow_owner_pruned_current_basis = bool(
        isinstance(pruned_history, dict)
        and pruned_history.get("approved") is True
        and pruned_history.get("checkpoint_id") == "terminal_successor_c50"
        and pruned_history.get("disposition")
        == "revalidate_recorded_compiler_rows_against_reachable_subject"
    )
    g5 = contract["g5_required_evidence"]
    binding_rows: list[dict[str, Any]] = []
    binding_by_id: dict[str, dict[str, Any]] = {}
    for binding in g5["evidence_bindings"]:
        binding_id = binding["binding_id"]
        path = binding["path"]
        if binding_id in binding_by_id or path not in tracked:
            raise CleanCheckoutError(
                f"invalid or untracked G5 evidence binding: {binding_id}"
            )
        raw = bytes_at_commit(repo, commit, path)
        raw_sha256 = sha256_bytes(raw)
        if raw_sha256 != binding["git_blob_raw_sha256"]:
            raise CleanCheckoutError(
                f"G5 Git-blob raw identity mismatch: {binding_id}"
            )
        hash_mode = binding["hash_mode"]
        if hash_mode == "git_blob_raw_sha256":
            declared_match = raw_sha256 == binding["declared_sha256"]
        elif hash_mode == "line_ending_equivalent_text_sha256_v1":
            declared_match = (
                binding["declared_sha256"]
                in _line_ending_sha256_variants(raw)
            )
        else:
            raise CleanCheckoutError(
                f"unsupported G5 evidence hash mode: {hash_mode}"
            )
        if not declared_match:
            raise CleanCheckoutError(
                f"G5 declared evidence identity mismatch: {binding_id}"
            )
        row = {
            "binding_id": binding_id,
            "path": path,
            "hash_mode": hash_mode,
            "declared_sha256": binding["declared_sha256"],
            "git_blob_raw_sha256": raw_sha256,
            "declared_identity_match": True,
        }
        binding_rows.append(row)
        binding_by_id[binding_id] = binding

    compiler = g5["compiler_identity"]
    for path in compiler["ordered_paths"]:
        if path not in tracked:
            raise CleanCheckoutError(
                f"G5 compiler constituent is not tracked: {path}"
            )
    transition_binding = compiler["successor_transition"]
    if (
        set(transition_binding)
        != {"path", "git_blob_raw_sha256", "hash_mode"}
        or transition_binding["hash_mode"] != "git_blob_raw_sha256"
        or transition_binding["path"] not in tracked
    ):
        raise CleanCheckoutError("invalid G5 compiler successor binding")
    transition_raw = bytes_at_commit(
        repo, commit, transition_binding["path"]
    )
    transition_sha256 = sha256_bytes(transition_raw)
    if transition_sha256 != transition_binding["git_blob_raw_sha256"]:
        raise CleanCheckoutError("G5 compiler successor raw identity mismatch")
    transition = json.loads(transition_raw)
    compiler_validation = _validate_g5_compiler_identity_transition(
        repo,
        commit,
        compiler,
        transition,
        allow_owner_pruned_current_basis,
    )
    compiler_validation["successor_transition"] = {
        "path": transition_binding["path"],
        "git_blob_raw_sha256": transition_sha256,
        "hash_mode": transition_binding["hash_mode"],
        "schema_version": transition["schema_version"],
        "status": transition["status"],
    }
    historical_aggregate_sha256 = compiler_validation[
        "historical_attested_aggregate_sha256"
    ]

    handoff = json_at_commit(
        repo,
        commit,
        binding_by_id["phase8_handoff"]["path"],
    )
    path_constituents = {
        row["path"]: row
        for row in handoff["constituents"]
        if isinstance(row.get("path"), str)
    }
    expected_constituent_paths = set(
        g5["handoff_path_bearing_constituents"]
    )
    if set(path_constituents) != expected_constituent_paths:
        raise CleanCheckoutError(
            "G5 handoff path-bearing constituent set mismatch"
        )
    for path, row in path_constituents.items():
        if path not in tracked:
            raise CleanCheckoutError(
                f"G5 handoff constituent is not tracked: {path}"
            )
        if row["sha256"] not in _line_ending_sha256_variants(
            bytes_at_commit(repo, commit, path)
        ):
            raise CleanCheckoutError(
                f"G5 handoff constituent identity mismatch: {path}"
            )
    handoff_by_id = {row["id"]: row for row in handoff["constituents"]}
    if (
        handoff["naturalization_attempt_id"] != g5["primary_attempt_id"]
        or handoff_by_id["compiler_implementation_hash"]["value"]
        != historical_aggregate_sha256
        or handoff_by_id["candidate_rendered_hash"]["sha256"]
        != binding_by_id["candidate"]["declared_sha256"]
    ):
        raise CleanCheckoutError("G5 handoff binding mismatch")

    phase8_closeout = json_at_commit(
        repo,
        commit,
        binding_by_id["phase8_closeout"]["path"],
    )
    if (
        phase8_closeout["naturalization_attempt_id"]
        != g5["primary_attempt_id"]
        or phase8_closeout["candidate_rendered_sha256"]
        != binding_by_id["candidate"]["declared_sha256"]
        or phase8_closeout["publish_acceptance_handoff_manifest_sha256"]
        != binding_by_id["phase8_handoff"]["declared_sha256"]
    ):
        raise CleanCheckoutError("G5 Phase 8 closeout binding mismatch")

    terminal = json_at_commit(
        repo,
        commit,
        binding_by_id["terminal_closeout"]["path"],
    )
    if (
        terminal["attempts"]["primary"] != g5["primary_attempt_id"]
        or terminal["attempts"]["replay"] != g5["replay_attempt_id"]
        or terminal["compiler_identity"]["aggregate_sha256"]
        != historical_aggregate_sha256
        or terminal["phase0_through_phase6_ab"]["candidate_sha256"]
        != binding_by_id["candidate"]["declared_sha256"]
        or terminal["phase0_through_phase6_ab"]["trace_sha256"]
        != binding_by_id["trace"]["declared_sha256"]
        or terminal["phase8_handoff"]["handoff_sha256"]
        != binding_by_id["phase8_handoff"]["declared_sha256"]
        or terminal["phase8_handoff"]["phase8_closeout_sha256"]
        != binding_by_id["phase8_closeout"]["declared_sha256"]
    ):
        raise CleanCheckoutError("G5 terminal closeout binding mismatch")

    g4_required_paths = g5["g4_required_paths"]
    if (
        len(g4_required_paths) != len(set(g4_required_paths))
        or not expected_constituent_paths.issubset(g4_required_paths)
        or binding_by_id["phase8_handoff"]["path"]
        not in g4_required_paths
        or transition_binding["path"] not in g4_required_paths
    ):
        raise CleanCheckoutError("invalid G5-to-G4 required path contract")
    missing_g4_paths = sorted(set(g4_required_paths) - tracked)
    if missing_g4_paths:
        raise CleanCheckoutError(
            "G5-to-G4 required path is not tracked: "
            + ", ".join(missing_g4_paths)
        )
    return {
        "status": "PASS",
        "primary_attempt_id": g5["primary_attempt_id"],
        "replay_attempt_id": g5["replay_attempt_id"],
        "binding_rows": sorted(
            binding_rows, key=lambda row: row["binding_id"]
        ),
        "compiler_identity": compiler_validation,
        "handoff_path_bearing_constituent_count": len(
            path_constituents
        ),
        "g4_required_path_count": len(g4_required_paths),
        "candidate_trace_handoff_identity": "PASS",
    }


def _active_ignored_paths(repo: Path, paths: list[str]) -> list[str]:
    ignored: list[str] = []
    for path in paths:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "check-ignore",
                "--no-index",
                "-q",
                "--",
                path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode == 0:
            ignored.append(path)
        elif completed.returncode != 1:
            raise CleanCheckoutError(
                "cannot inspect active ignore state for "
                f"{path}: {completed.stderr.decode(errors='replace')}"
            )
    return ignored


def build_source_census(
    repo: Path,
    commit: str,
    output_root: Path,
    discovery_root: Path | None,
    *,
    full_repository: bool = False,
) -> dict[str, Any]:
    subject = git_identity(repo, commit)
    commit = subject["commit"]
    paths = tracked_paths(repo, commit)
    tracked = set(paths)
    sources = _test_sources(paths)
    taxonomy = json_at_commit(repo, commit, TAXONOMY_PATH)
    gate_contract_path = (
        FULL_REPOSITORY_GATE_PATH
        if full_repository
        else CANONICAL_GATE_PATH
    )
    gate_contract = json_at_commit(repo, commit, gate_contract_path)
    if full_repository:
        source_roles = _full_required_source_roles(
            gate_contract, taxonomy
        )
        source_classifications = {
            source_path: _classify_full_test_source(
                source_path, source_roles
            )
            for source_path in sources
        }
        _validate_explicit_current_required_classifications(
            gate_contract,
            source_classifications,
        )
        gate_sources = {
            source_path
            for source_path, classification in source_classifications.items()
            if classification["execution_role"]
            in {
                "required_pytest",
                "mixed_required_pytest",
                "required_standalone_command",
            }
        }
    else:
        source_classifications = {}
        gate_sources = set(_canonical_gate_sources(gate_contract, taxonomy))
    explicit_dependency_rows = (
        _validate_explicit_required_dependencies(
            gate_contract,
            tracked,
            gate_sources,
        )
        if full_repository
        else []
    )
    explicit_dependencies_by_source: dict[str, list[dict[str, str]]] = (
        defaultdict(list)
    )
    for row in explicit_dependency_rows:
        explicit_dependencies_by_source[row["test_source"]].append(row)
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
        source_row = {
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
        if full_repository:
            source_row.update(source_classifications[source_path])
        source_rows.append(source_row)
        if source_path not in gate_sources:
            continue
        for row in explicit_dependencies_by_source[source_path]:
            dependency_rows.append(
                {
                    "test_source": source_path,
                    "import_module": None,
                    "dependency_depth": 0,
                    "parent_module": None,
                    "resolved_path": row["path"],
                    "tracking_state": "tracked",
                    "dependency_class": row["authority_class"],
                    "provenance": (
                        "explicit_full_gate_direct_dependency_contract"
                    ),
                    "dependency_role": row["dependency_role"],
                    "relationship": row["relationship"],
                }
            )
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

    tool_disposition_rows: list[dict[str, str]] = []
    consumer_integration_evidence_rows: list[dict[str, str]] = []
    if full_repository:
        required_dependency_paths = {
            row["resolved_path"]
            for row in dependency_rows
            if row["tracking_state"] == "tracked"
            and isinstance(row["resolved_path"], str)
        }
        tool_disposition_rows = _validate_explicit_tool_dispositions(
            gate_contract,
            tracked,
            required_dependency_paths,
        )
        consumer_integration_evidence_rows = (
            _validate_consumer_integration_evidence(
                repo,
                commit,
                gate_contract,
                tracked,
                required_dependency_paths,
            )
        )

    source_inventory = {
        "schema_version": "iris-clean-checkout-test-inventory-v1",
        "inventory_state": "source_census_pending_live_collection",
        "gate_scope": (
            "full_required_repository"
            if full_repository
            else "scoped_technical_debt_gate"
        ),
        "subject": subject,
        "pytest_configuration": {
            "testpaths": testpaths,
            "explicit_ignores": ignored_paths,
            "norecursedirs": norecursedirs,
        },
        "source_rows": source_rows,
        "tool_disposition_rows": tool_disposition_rows,
        "consumer_integration_evidence_rows": (
            consumer_integration_evidence_rows
        ),
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
            "required_source_count": len(gate_sources),
            "historical_optional_source_count": sum(
                row.get("authority_class") == "historical_optional_evidence"
                for row in source_rows
            ),
            "obsolete_or_misrouted_source_count": sum(
                row.get("authority_class")
                == "obsolete_or_misrouted_test_dependency"
                for row in source_rows
            ),
            "hermetic_test_fixture_source_count": sum(
                row.get("authority_class") == "hermetic_test_fixture"
                for row in source_rows
            ),
            "attempt_generation_evidence_tool_count": len(
                tool_disposition_rows
            ),
            "consumer_integration_evidence_count": len(
                consumer_integration_evidence_rows
            ),
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
        "gate_scope": source_inventory["gate_scope"],
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


def _status_snapshot(repo: Path, *, include_ignored: bool = True) -> str:
    arguments = [
        "status",
        "--porcelain=v2",
        "--untracked-files=all",
    ]
    if include_ignored:
        arguments.append("--ignored=matching")
    return git_text(repo, *arguments)


def _ignored_status_snapshot(repo: Path) -> str:
    return "\n".join(
        row
        for row in _status_snapshot(repo, include_ignored=True).splitlines()
        if row.startswith("! ")
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
            "UV_CACHE_DIR": str(system_temp / "uv-cache"),
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


def _require_disjoint_external_roots(
    repo: Path,
    work_root: Path,
    result_root: Path,
) -> None:
    ensure_external_root(repo, work_root)
    ensure_external_root(repo, result_root)
    for left, right in ((work_root, result_root), (result_root, work_root)):
        try:
            left.relative_to(right)
        except ValueError:
            continue
        raise CleanCheckoutError(
            f"work and result roots must be disjoint: {work_root}, {result_root}"
        )


def _require_empty_directory(path: Path, role: str) -> None:
    if any(path.iterdir()):
        raise CleanCheckoutError(f"{role} must be empty before execution: {path}")


def _run_subprocess(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _raise_process_failure(
    label: str,
    command: list[str],
    completed: subprocess.CompletedProcess[bytes],
) -> None:
    if completed.returncode == 0:
        return
    stdout = completed.stdout.decode("utf-8", errors="replace").strip()
    stderr = completed.stderr.decode("utf-8", errors="replace").strip()
    raise CleanCheckoutError(
        f"{label} failed ({completed.returncode}): {' '.join(command)}"
        f"\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    )


def _safe_checkout_target(checkout: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise CleanCheckoutError(
            f"unsafe repository-relative materialization target: {relative_path}"
        )
    target = (checkout / relative).resolve()
    try:
        target.relative_to(checkout)
    except ValueError as exc:
        raise CleanCheckoutError(
            f"materialization target escapes checkout: {relative_path}"
        ) from exc
    return target


def _materialize_frozen_predecessor_fixture(
    checkout: Path,
    contract: dict[str, Any],
) -> dict[str, Any]:
    fixture_contract = contract["bootstrap"][
        "frozen_predecessor_fixture"
    ]
    manifest_path = _safe_checkout_target(
        checkout, fixture_contract["manifest_path"]
    )
    if sha256_file(manifest_path) != fixture_contract["manifest_sha256"]:
        raise CleanCheckoutError("frozen predecessor fixture manifest hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version")
        != (
            "dvf-3-3-registry-authority-canonical-closure-"
            "frozen-predecessor-fixture-v1"
        )
        or manifest.get("status") != "PASS"
        or manifest.get("authority_claimed") is not False
        or manifest.get("current_route_authority_claimed") is not False
        or manifest.get("candidate_discard_required") is not True
    ):
        raise CleanCheckoutError(
            "frozen predecessor fixture authority boundary is invalid"
        )
    partition_name = fixture_contract["materialized_partition"]
    payload_paths = manifest.get(partition_name)
    if not isinstance(payload_paths, list) or not payload_paths:
        raise CleanCheckoutError(
            f"frozen predecessor partition is empty: {partition_name}"
        )
    rows_by_payload = {
        row["payload_path"]: row
        for row in manifest.get("rows", [])
        if isinstance(row, dict) and isinstance(row.get("payload_path"), str)
    }
    if set(payload_paths) - set(rows_by_payload):
        raise CleanCheckoutError(
            "frozen predecessor partition references an unknown payload"
        )
    fixture_root = manifest_path.parent
    materialized_rows: list[dict[str, Any]] = []
    for payload_relative in payload_paths:
        row = rows_by_payload[payload_relative]
        if (
            row.get("role") != "frozen_predecessor_input"
            or row.get("isolated_candidate_only") is not True
            or row.get("live_materialization_allowed") is not False
        ):
            raise CleanCheckoutError(
                f"invalid frozen predecessor row: {payload_relative}"
            )
        payload = _safe_checkout_target(
            fixture_root, payload_relative
        )
        if (
            not payload.is_file()
            or sha256_file(payload) != row.get("sha256")
            or payload.stat().st_size != row.get("byte_length")
        ):
            raise CleanCheckoutError(
                f"frozen predecessor payload mismatch: {payload_relative}"
            )
        target = _safe_checkout_target(checkout, row["target_path"])
        previous_sha256 = sha256_file(target) if target.is_file() else None
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(payload, target)
        if sha256_file(target) != row["sha256"]:
            raise CleanCheckoutError(
                f"frozen predecessor copy mismatch: {row['target_path']}"
            )
        materialized_rows.append(
            {
                "target_path": row["target_path"],
                "sha256": row["sha256"],
                "byte_length": row["byte_length"],
                "preexisting_sha256": previous_sha256,
                "authority_class": fixture_contract["authority_class"],
                "producer": (
                    "tracked_hash_bound_frozen_predecessor_fixture"
                ),
            }
        )
    return {
        "status": "PASS",
        "manifest_path": fixture_contract["manifest_path"],
        "manifest_sha256": fixture_contract["manifest_sha256"],
        "partition": partition_name,
        "materialized_file_count": len(materialized_rows),
        "rows": materialized_rows,
    }


def _materialize_package_runtime_mirror(
    source_repo: Path,
    commit: str,
    checkout: Path,
    contract: dict[str, Any],
) -> dict[str, Any]:
    mirror = contract["bootstrap"]["package_runtime_mirror"]
    source_manifest_relative = mirror["source_manifest"]
    source_directory_relative = mirror["source_directory"]
    source_manifest = _safe_checkout_target(
        checkout, source_manifest_relative
    )
    source_directory = _safe_checkout_target(
        checkout, source_directory_relative
    )
    if not source_manifest.is_file() or not source_directory.is_dir():
        raise CleanCheckoutError("tracked package mirror source is missing")
    source_files = [source_manifest, *sorted(source_directory.iterdir())]
    if any(not path.is_file() for path in source_files):
        raise CleanCheckoutError(
            "package mirror source directory contains a non-file entry"
        )
    tracked = set(tracked_paths(source_repo, commit))
    source_relatives = [
        path.relative_to(checkout).as_posix() for path in source_files
    ]
    untracked_sources = sorted(set(source_relatives) - tracked)
    if untracked_sources:
        raise CleanCheckoutError(
            "package mirror source is not tracked at the subject commit: "
            + ", ".join(untracked_sources)
        )

    target_manifest = _safe_checkout_target(
        checkout, mirror["target_manifest"]
    )
    target_directory = _safe_checkout_target(
        checkout, mirror["target_directory"]
    )
    target_manifest.parent.mkdir(parents=True, exist_ok=True)
    target_directory.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    destinations = [
        target_manifest,
        *[target_directory / path.name for path in source_files[1:]],
    ]
    for source, target in zip(source_files, destinations, strict=True):
        shutil.copyfile(source, target)
        source_hash = sha256_file(source)
        if sha256_file(target) != source_hash:
            raise CleanCheckoutError(
                f"package mirror copy mismatch: {target}"
            )
        rows.append(
            {
                "source_path": source.relative_to(checkout).as_posix(),
                "target_path": target.relative_to(checkout).as_posix(),
                "sha256": source_hash,
                "byte_length": source.stat().st_size,
                "authority_class": mirror["authority_class"],
                "producer": mirror["producer"],
            }
        )
    return {
        "status": "PASS",
        "materialized_file_count": len(rows),
        "rows": rows,
    }


def _normalized_test_id(node_id: str) -> str:
    parts = node_id.split("::")
    stem = Path(parts[0]).stem
    if len(parts) == 1:
        return stem
    leaf = parts[-1].split("[", 1)[0]
    if len(parts) >= 3:
        parent = parts[-2].split("[", 1)[0]
        return f"{stem}.{parent}.{leaf}"
    return f"{stem}.{leaf}"


def _status_counts(status: str) -> dict[str, int]:
    rows = status.splitlines()
    return {
        "status_row_count": len(rows),
        "tracked_change_count": sum(
            row.startswith(("1 ", "2 ", "u ")) for row in rows
        ),
        "untracked_path_count": sum(row.startswith("? ") for row in rows),
        "ignored_path_count": sum(row.startswith("! ") for row in rows),
    }


def _implementation_identity(
    repo: Path,
    commit: str,
) -> dict[str, Any]:
    runner_path = Path(__file__).resolve()
    common_path = Path(clean_checkout_common.__file__).resolve()
    expected_runner = (repo / RUNNER_PATH).resolve()
    expected_common = (repo / COMMON_MODULE_PATH).resolve()
    if runner_path != expected_runner:
        raise CleanCheckoutError(
            "runner was imported from a different checkout: "
            f"{runner_path} != {expected_runner}"
        )
    if common_path != expected_common:
        raise CleanCheckoutError(
            "common module was imported from a different checkout: "
            f"{common_path} != {expected_common}"
        )
    expected_runner_blob = blob_id(repo, commit, RUNNER_PATH)
    expected_common_blob = blob_id(repo, commit, COMMON_MODULE_PATH)
    working_runner_blob = git_text(
        repo,
        "hash-object",
        f"--path={RUNNER_PATH}",
        str(runner_path),
    ).strip()
    working_common_blob = git_text(
        repo,
        "hash-object",
        f"--path={COMMON_MODULE_PATH}",
        str(common_path),
    ).strip()
    if working_runner_blob != expected_runner_blob:
        raise CleanCheckoutError("runner working file differs from subject blob")
    if working_common_blob != expected_common_blob:
        raise CleanCheckoutError(
            "imported common working file differs from subject blob"
        )
    return {
        "runner": {
            "logical_path": RUNNER_PATH,
            "actual_path": runner_path.as_posix(),
            "git_blob_id": expected_runner_blob,
            "working_git_blob_id": working_runner_blob,
            "working_sha256": sha256_file(runner_path),
        },
        "imported_common": {
            "logical_path": COMMON_MODULE_PATH,
            "actual_path": common_path.as_posix(),
            "module_file": common_path.as_posix(),
            "git_blob_id": expected_common_blob,
            "working_git_blob_id": working_common_blob,
            "working_sha256": sha256_file(common_path),
        },
    }


def _remove_disposable_checkout(path: Path) -> None:
    removal_path: str | Path = path
    if os.name == "nt":
        resolved = str(path.resolve())
        if resolved.startswith("\\\\"):
            removal_path = "\\\\?\\UNC\\" + resolved[2:]
        else:
            removal_path = "\\\\?\\" + resolved

    def make_writable_and_retry(
        function: Any,
        target: str,
        _: Any,
    ) -> None:
        os.chmod(target, stat.S_IWRITE)
        function(target)

    shutil.rmtree(removal_path, onerror=make_writable_and_retry)


def run_full_repository_gate(
    repo: Path,
    commit: str,
    python_executable: Path,
    environment_receipt: Path,
    work_root: Path,
    result_root: Path,
    execution_context: str = "standalone_full_gate",
    predecessor_stage_receipt_set_sha256: str | None = None,
    qualification_contract_sha256: str | None = None,
    predecessor_stage_receipt_set: Path | None = None,
    qualification_contract: Path | None = None,
) -> dict[str, Any]:
    subject = git_identity(repo, commit)
    implementation_identity = _implementation_identity(
        repo, subject["commit"]
    )
    head = git_identity(repo, "HEAD")
    if head != subject:
        raise CleanCheckoutError(
            f"source checkout HEAD does not match subject: {head} != {subject}"
        )
    before_status = _status_snapshot(repo, include_ignored=False)
    if before_status:
        raise CleanCheckoutError(
            "full gate requires no tracked or non-ignored untracked source "
            f"checkout changes:\n{before_status}"
        )
    ignored_status_before = _ignored_status_snapshot(repo)
    if execution_context == "composite_baseline_admission_chain_stage_6":
        identities = (
            predecessor_stage_receipt_set_sha256,
            qualification_contract_sha256,
        )
        if any(
            not isinstance(value, str)
            or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)
            for value in identities
        ):
            raise CleanCheckoutError(
                "composite baseline-admission full gate requires lowercase "
                "SHA-256 predecessor-stage and qualification-contract identities"
            )
        if (
            predecessor_stage_receipt_set is None
            or qualification_contract is None
            or not predecessor_stage_receipt_set.is_file()
            or not qualification_contract.is_file()
            or sha256_file(predecessor_stage_receipt_set)
            != predecessor_stage_receipt_set_sha256
            or sha256_file(qualification_contract)
            != qualification_contract_sha256
        ):
            raise CleanCheckoutError(
                "composite baseline-admission identity inputs are missing or "
                "do not match their declared SHA-256 values"
            )
    _require_disjoint_external_roots(repo, work_root, result_root)
    _require_empty_directory(work_root, "work root")
    _require_empty_directory(result_root, "result root")

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
        repo, subject["commit"], FULL_REPOSITORY_GATE_PATH
    )
    output_policy = json_at_commit(
        repo, subject["commit"], OUTPUT_POLICY_PATH
    )
    if (
        contract["claim_boundary"]["independent_operator_required"] is not False
        or contract["claim_boundary"]["windows_privileged_auditing_required"]
        is not False
        or output_policy["repository_local_generated_output_allowed"] is not False
        or output_policy["administrator_token_required"] is not False
        or output_policy["windows_privileged_auditing_required"] is not False
    ):
        raise CleanCheckoutError("unsupported full-gate privilege policy")
    checkout = work_root / ("x" if os.name == "nt" else "execution-checkout")
    maximum_checkout_root_length = contract["execution_workspace"][
        "windows_maximum_execution_checkout_root_length"
    ]
    if (
        os.name == "nt"
        and len(str(checkout)) > maximum_checkout_root_length
    ):
        raise CleanCheckoutError(
            "Windows execution checkout root is too long for the declared "
            f"path budget ({len(str(checkout))} > "
            f"{maximum_checkout_root_length}): {checkout}"
        )

    taxonomy = json_at_commit(repo, subject["commit"], TAXONOMY_PATH)
    required_manifest = json_at_commit(
        repo, subject["commit"], REQUIRED_MANIFEST_PATH
    )
    historical_optional_test_ids = {
        row["test_id"]
        for row in required_manifest["applicability_overrides"]
        ["historical_optional_evidence"]["tests"]
    }
    selection = contract["required_pytest_selection"]
    current_sources = sorted(
        {
            row["source_file"]
            for row in taxonomy["rows"]
            if row["contract_class"] == selection["contract_class"]
            and row["state"] == selection["state"]
        }
    )
    current_ids = {
        row["test_id"]
        for row in taxonomy["rows"]
        if row["contract_class"] == selection["contract_class"]
        and row["state"] == selection["state"]
    }
    tracked = tracked_paths(repo, subject["commit"])
    tracked_set = set(tracked)
    if os.name == "nt":
        longest_relative_path = max(tracked, key=len)
        maximum_materialized_path_length = contract["execution_workspace"][
            "windows_maximum_materialized_path_length"
        ]
        longest_materialized_path_length = len(
            str(checkout / longest_relative_path)
        )
        if longest_materialized_path_length > maximum_materialized_path_length:
            raise CleanCheckoutError(
                "Windows execution checkout cannot safely expose the longest "
                "tracked path to repository validators "
                f"({longest_materialized_path_length} > "
                f"{maximum_materialized_path_length}): "
                f"{longest_relative_path}"
            )
    test_sources = _test_sources(tracked)
    source_roles = _full_required_source_roles(contract, taxonomy)
    source_classifications = {
        source_path: _classify_full_test_source(source_path, source_roles)
        for source_path in test_sources
    }
    _validate_explicit_current_required_classifications(
        contract,
        source_classifications,
    )
    required_sources = {
        source_path
        for source_path, classification in source_classifications.items()
        if classification["execution_role"]
        in {
            "required_pytest",
            "mixed_required_pytest",
            "required_standalone_command",
        }
    }
    declared_required_sources = {
        source_path
        for source_path, classification in source_roles.items()
        if classification["execution_role"]
        in {
            "required_pytest",
            "mixed_required_pytest",
            "required_standalone_command",
        }
    }
    missing_required_sources = sorted(
        declared_required_sources - tracked_set
    )
    if missing_required_sources:
        raise CleanCheckoutError(
            "full-gate required source is not tracked: "
            + ", ".join(missing_required_sources)
        )
    required_dependency_paths = _required_dependency_paths(
        repo,
        subject["commit"],
        required_sources,
        tracked_set,
    )
    explicit_dependency_rows = _validate_explicit_required_dependencies(
        contract,
        tracked_set,
        required_sources,
    )
    required_dependency_paths.update(
        row["path"] for row in explicit_dependency_rows
    )
    tool_disposition_rows = _validate_explicit_tool_dispositions(
        contract,
        tracked_set,
        required_dependency_paths,
    )
    consumer_integration_evidence_rows = (
        _validate_consumer_integration_evidence(
            repo,
            subject["commit"],
            contract,
            tracked_set,
            required_dependency_paths,
        )
    )
    required_dependency_inventory_sha256 = sha256_bytes(
        canonical_json_bytes(sorted(required_dependency_paths))
    )
    g5_validation = _validate_g5_required_evidence(
        repo,
        subject["commit"],
        contract,
        tracked_set,
    )
    g5_contract = contract["g5_required_evidence"]
    required_input_paths = sorted(
        {
            *g5_contract["g4_required_paths"],
            *(
                row["path"]
                for row in g5_contract["evidence_bindings"]
            ),
        }
    )

    environment = os.environ.copy()
    for variable in output_policy["cleared_ambient_environment"]:
        environment.pop(variable, None)
    environment.update(output_policy["required_environment"])
    environment.update(contract["bootstrap"]["required_environment"])
    system_temp = result_root / "system-temp"
    system_temp.mkdir(parents=True)
    environment.update(
        {
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PYTHONPYCACHEPREFIX": str(system_temp / "pycache"),
            "UV_CACHE_DIR": str(system_temp / "uv-cache"),
            "TEMP": str(system_temp),
            "TMP": str(system_temp),
            "TMPDIR": str(system_temp),
        }
    )

    clone_command = [
        "git",
        "-c",
        "core.longpaths=true",
        "clone",
        "--no-local",
        "--no-checkout",
        str(repo),
        str(checkout),
    ]
    clone_result = _run_subprocess(
        clone_command, cwd=work_root, environment=environment
    )
    _raise_process_failure("external checkout clone", clone_command, clone_result)
    checkout_command = [
        "git",
        "-c",
        "core.longpaths=true",
        "-C",
        str(checkout),
        "checkout",
        "--detach",
        subject["commit"],
    ]
    checkout_result = _run_subprocess(
        checkout_command, cwd=work_root, environment=environment
    )
    _raise_process_failure(
        "external checkout materialization",
        checkout_command,
        checkout_result,
    )

    cleanup_status = "not_attempted"
    pytest_completed: subprocess.CompletedProcess[bytes] | None = None
    raw_result: dict[str, Any] = {}
    standalone_rows: list[dict[str, Any]] = []
    execution_status_baseline = ""
    execution_status_after = ""
    fixture_result: dict[str, Any] = {}
    mirror_result: dict[str, Any] = {}
    ignored_required_paths: list[str] = []
    try:
        initial_execution_status = _status_snapshot(checkout)
        if initial_execution_status:
            raise CleanCheckoutError(
                "external execution checkout is not initially clean:\n"
                + initial_execution_status
            )
        ignored_required_paths = _active_ignored_paths(
            checkout,
            required_input_paths,
        )
        if ignored_required_paths:
            raise CleanCheckoutError(
                "G5 or G4 required input is actively ignored: "
                + ", ".join(ignored_required_paths)
            )
        fixture_result = _materialize_frozen_predecessor_fixture(
            checkout, contract
        )
        mirror_result = _materialize_package_runtime_mirror(
            repo, subject["commit"], checkout, contract
        )
        isolated_temp_root = checkout / ".dvf_tmp"
        isolated_temp_root.mkdir()
        environment["IRIS_DVF_ISOLATED_TEMP_ROOT"] = str(
            isolated_temp_root
        )
        execution_status_baseline = _status_snapshot(checkout)
        materialization_receipt = {
            "schema_version": (
                "iris-clean-checkout-full-materialization-receipt-v1"
            ),
            "status": "PASS",
            "subject": subject,
            "fixture": fixture_result,
            "package_runtime_mirror": mirror_result,
        }
        materialization_path = result_root / "materialization_receipt.json"
        materialization_sha256 = write_json_external(
            repo, materialization_path, materialization_receipt
        )

        pytest_result_path = result_root / "full_pytest_result.json"
        environment["IRIS_CLEAN_CHECKOUT_PYTEST_RESULT"] = str(
            pytest_result_path
        )
        environment["IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT"] = str(
            result_root / "test-output"
        )
        pytest_legacy_output_root = (
            result_root
            / "test-output"
            / "pytest-legacy-output"
            / "Iris-output"
        )
        pytest_legacy_output_root.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        environment[
            "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"
        ] = str(pytest_legacy_output_root)
        command_contract = contract["command"]
        additional_source_option = selection["additional_source_option"]
        explicit_current_sources = _explicit_current_required_paths(contract)
        declared_additional_sources = [
            *selection["additional_source_paths"],
            *explicit_current_sources,
        ]
        additional_source_arguments = [
            argument
            for path in declared_additional_sources
            for argument in (additional_source_option, path)
        ]
        pytest_selection = [
            *current_sources,
            *declared_additional_sources,
            *selection["additional_node_ids"],
        ]
        pytest_command = [
            str(python_executable),
            *command_contract["python_flags"],
            "-m",
            command_contract["module"],
            *command_contract["arguments"],
            *additional_source_arguments,
            *pytest_selection,
        ]
        pytest_completed = _run_subprocess(
            pytest_command,
            cwd=checkout,
            environment=environment,
        )
        pytest_stdout_path = result_root / "full_pytest.stdout.txt"
        pytest_stderr_path = result_root / "full_pytest.stderr.txt"
        pytest_stdout_path.write_bytes(pytest_completed.stdout)
        pytest_stderr_path.write_bytes(pytest_completed.stderr)
        raw_result = _load_pytest_result(pytest_result_path)
        if not pytest_result_path.exists():
            write_json_external(repo, pytest_result_path, raw_result)

        standalone_root = result_root / "standalone"
        standalone_root.mkdir()
        for row in contract["required_standalone_validations"]:
            standalone_output_root = (
                result_root
                / "test-output"
                / "standalone-output-projections"
                / row["command_id"]
                / "Iris-output"
            )
            standalone_output_root.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            shutil.copytree(
                checkout / "Iris" / "output",
                standalone_output_root,
            )
            standalone_environment = dict(environment)
            standalone_environment[
                "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"
            ] = str(standalone_output_root)
            command = [
                str(python_executable),
                *command_contract["python_flags"],
                row["path"],
            ]
            completed = _run_subprocess(
                command,
                cwd=checkout,
                environment=standalone_environment,
            )
            stdout_path = standalone_root / f"{row['command_id']}.stdout.txt"
            stderr_path = standalone_root / f"{row['command_id']}.stderr.txt"
            stdout_path.write_bytes(completed.stdout)
            stderr_path.write_bytes(completed.stderr)
            standalone_rows.append(
                {
                    "command_id": row["command_id"],
                    "path": row["path"],
                    "return_code": completed.returncode,
                    "status": (
                        "PASS" if completed.returncode == 0 else "FAIL"
                    ),
                    "output_projection": (
                        "repository_external_seeded_copy"
                    ),
                    "stdout_sha256": sha256_file(stdout_path),
                    "stderr_sha256": sha256_file(stderr_path),
                }
            )
        execution_status_after = _status_snapshot(checkout)
    finally:
        if checkout.exists():
            try:
                _remove_disposable_checkout(checkout)
                cleanup_status = "PASS"
            except OSError:
                cleanup_status = "FAIL"
        else:
            cleanup_status = "PASS"

    if pytest_completed is None:
        raise CleanCheckoutError("pytest execution did not start")
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
    actual_current_ids = {
        _normalized_test_id(row["node_id"])
        for row in identity_rows
        if row["source_path"] in current_sources
    }
    actual_current_ids -= historical_optional_test_ids
    current_identity_set_equal = actual_current_ids == current_ids
    actual_node_ids = {row["node_id"] for row in identity_rows}
    explicit_node_set_equal = (
        set(selection["additional_node_ids"])
        <= actual_node_ids
    )
    actual_sources = {row["source_path"] for row in identity_rows}
    expected_sources = {
        *current_sources,
        *selection["additional_source_paths"],
        *_explicit_current_required_paths(contract),
        *(
            node_id.split("::", 1)[0]
            for node_id in selection["additional_node_ids"]
        ),
    }
    selected_source_set_equal = actual_sources == expected_sources
    identity_projection = [
        {
            "node_id": row["node_id"],
            "source_path": row["source_path"],
        }
        for row in identity_rows
    ]
    inventory_hash = sha256_bytes(canonical_json_bytes(identity_projection))
    after_status = _status_snapshot(repo, include_ignored=False)
    ignored_status_after = _ignored_status_snapshot(repo)
    ignored_status_unchanged = ignored_status_after == ignored_status_before
    execution_status_unchanged = (
        execution_status_after == execution_status_baseline
    )
    execution_mutation_rows = sorted(
        set(execution_status_after.splitlines())
        ^ set(execution_status_baseline.splitlines())
    )
    pytest_pass = (
        pytest_completed.returncode == 0
        and raw_result.get("status") == "PASS"
        and identity_rows
        and all(row["outcome"] == "passed" for row in identity_rows)
        and current_identity_set_equal
        and explicit_node_set_equal
        and selected_source_set_equal
    )
    standalone_pass = bool(standalone_rows) and all(
        row["status"] == "PASS" for row in standalone_rows
    )
    status = (
        "PASS"
        if pytest_pass
        and standalone_pass
        and not before_status
        and not after_status
        and ignored_status_unchanged
        and execution_status_unchanged
        and cleanup_status == "PASS"
        and not any(work_root.iterdir())
        else "FAIL"
    )
    source_counts = {
        "tracked_test_source_count": len(test_sources),
        "required_source_count": len(required_sources),
        "historical_optional_source_count": sum(
            row["authority_class"] == "historical_optional_evidence"
            for row in source_classifications.values()
        ),
        "obsolete_or_misrouted_source_count": sum(
            row["authority_class"]
            == "obsolete_or_misrouted_test_dependency"
            for row in source_classifications.values()
        ),
        "hermetic_test_fixture_source_count": sum(
            row["authority_class"] == "hermetic_test_fixture"
            for row in source_classifications.values()
        ),
    }
    canonical_standalone = [
        {
            "command_id": row["command_id"],
            "path": row["path"],
            "return_code": row["return_code"],
            "status": row["status"],
        }
        for row in standalone_rows
    ]
    canonical_result = {
        "schema_version": "iris-clean-checkout-canonical-full-result-v1",
        "status": status,
        "subject": subject,
        "execution_context": execution_context,
        "predecessor_stage_receipt_set_sha256": predecessor_stage_receipt_set_sha256,
        "qualification_contract_sha256": qualification_contract_sha256,
        "full_repository_gate_blob_id": blob_id(
            repo, subject["commit"], FULL_REPOSITORY_GATE_PATH
        ),
        "implementation_identity": implementation_identity,
        "taxonomy_blob_id": blob_id(
            repo, subject["commit"], TAXONOMY_PATH
        ),
        "environment_verification": environment_verification,
        "source_classification_counts": source_counts,
        "required_dependency_inventory": {
            "path_count": len(required_dependency_paths),
            "sha256": required_dependency_inventory_sha256,
            "explicit_direct_dependency_rows": explicit_dependency_rows,
            "unresolved_count": 0,
        },
        "consumer_integration_evidence_rows": (
            consumer_integration_evidence_rows
        ),
        "tool_disposition_rows": tool_disposition_rows,
        "g5_required_evidence": g5_validation,
        "ignored_required_input_count": len(ignored_required_paths),
        "pytest_identity_count": len(identity_rows),
        "standalone_validation_count": len(standalone_rows),
        "required_execution_unit_count": (
            len(identity_rows) + len(standalone_rows)
        ),
        "test_inventory_sha256": inventory_hash,
        "identity_rows": identity_rows,
        "standalone_rows": canonical_standalone,
        "current_taxonomy_identity_set_equal": current_identity_set_equal,
        "explicit_node_set_present": explicit_node_set_equal,
        "selected_source_set_equal": selected_source_set_equal,
        "collection_error_count": len(
            raw_result.get("collection_errors", [])
        ),
        "bootstrap": {
            "frozen_predecessor_manifest_sha256": fixture_result[
                "manifest_sha256"
            ],
            "frozen_predecessor_materialized_file_count": fixture_result[
                "materialized_file_count"
            ],
            "package_runtime_mirror_file_count": mirror_result[
                "materialized_file_count"
            ],
            "package_runtime_mirror_rows": mirror_result["rows"],
        },
        "source_checkout_clean_before": not before_status,
        "source_checkout_clean_after": not after_status,
        "source_checkout_ignored_state_unchanged": ignored_status_unchanged,
        "external_execution_status_unchanged": execution_status_unchanged,
        "external_execution_mutation_count": len(execution_mutation_rows),
        "external_execution_checkout_cleanup_status": cleanup_status,
        "external_work_root_empty_after": not any(work_root.iterdir()),
    }
    canonical_path = result_root / "canonical_full_result.json"
    canonical_sha256 = write_json_external(
        repo, canonical_path, canonical_result
    )
    receipt = {
        "schema_version": "iris-clean-checkout-full-run-receipt-v1",
        "status": status,
        "subject": subject,
        "execution_context": execution_context,
        "predecessor_stage_receipt_set_sha256": predecessor_stage_receipt_set_sha256,
        "qualification_contract_sha256": qualification_contract_sha256,
        "python_executable_path": python_executable.as_posix(),
        "environment_receipt_path": environment_receipt.as_posix(),
        "implementation_identity": implementation_identity,
        "materialization_receipt": {
            "path": materialization_path.as_posix(),
            "sha256": materialization_sha256,
        },
        "pytest_return_code": pytest_completed.returncode,
        "pytest_result": {
            "path": pytest_result_path.as_posix(),
            "sha256": sha256_file(pytest_result_path),
        },
        "pytest_stdout": {
            "path": pytest_stdout_path.as_posix(),
            "sha256": sha256_file(pytest_stdout_path),
        },
        "pytest_stderr": {
            "path": pytest_stderr_path.as_posix(),
            "sha256": sha256_file(pytest_stderr_path),
        },
        "standalone_rows": standalone_rows,
        "canonical_result": {
            "path": canonical_path.as_posix(),
            "sha256": canonical_sha256,
        },
        "source_repository_status_before": before_status.splitlines(),
        "source_repository_status_after": after_status.splitlines(),
        "source_repository_ignored_status_before": (
            ignored_status_before.splitlines()
        ),
        "source_repository_ignored_status_after": (
            ignored_status_after.splitlines()
        ),
        "source_repository_ignored_state_unchanged": ignored_status_unchanged,
        "required_input_path_count": len(required_input_paths),
        "ignored_required_input_paths": ignored_required_paths,
        "external_execution_status_baseline": (
            execution_status_baseline.splitlines()
        ),
        "external_execution_status_after": (
            execution_status_after.splitlines()
        ),
        "external_execution_status_unchanged": execution_status_unchanged,
        "external_execution_mutation_count": len(execution_mutation_rows),
        "external_execution_mutation_rows": execution_mutation_rows,
        "external_execution_status_counts": _status_counts(
            execution_status_after
        ),
        "external_execution_checkout_cleanup_status": cleanup_status,
        "external_work_root_empty_after": not any(work_root.iterdir()),
    }
    receipt_path = result_root / "full_run_receipt.json"
    receipt_sha256 = write_json_external(repo, receipt_path, receipt)
    return {
        "status": status,
        "subject": subject,
        "pytest_identity_count": len(identity_rows),
        "standalone_validation_count": len(standalone_rows),
        "required_execution_unit_count": (
            len(identity_rows) + len(standalone_rows)
        ),
        "test_inventory_sha256": inventory_hash,
        "canonical_result_path": canonical_path.as_posix(),
        "canonical_result_sha256": canonical_sha256,
        "run_receipt_path": receipt_path.as_posix(),
        "run_receipt_sha256": receipt_sha256,
        "source_checkout_clean_after": not after_status,
        "external_work_root_empty_after": not any(work_root.iterdir()),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    source = subparsers.add_parser("source-census")
    source.add_argument("--repo", required=True)
    source.add_argument("--commit", required=True)
    source.add_argument("--output-root", required=True)
    source.add_argument("--discovery-root")
    source.add_argument("--full-repository", action="store_true")
    gate = subparsers.add_parser("gate")
    gate.add_argument("--repo", required=True)
    gate.add_argument("--commit", required=True)
    gate.add_argument("--python", required=True)
    gate.add_argument("--environment-receipt", required=True)
    gate.add_argument("--output-root", required=True)
    gate.add_argument("--collect-only", action="store_true")
    full_gate = subparsers.add_parser("full-gate")
    full_gate.add_argument("--repo", required=True)
    full_gate.add_argument("--commit", required=True)
    full_gate.add_argument("--python", required=True)
    full_gate.add_argument("--environment-receipt", required=True)
    full_gate.add_argument("--work-root", required=True)
    full_gate.add_argument("--result-root", required=True)
    full_gate.add_argument("--execution-context", default="standalone_full_gate")
    full_gate.add_argument("--predecessor-stage-receipt-set-sha256")
    full_gate.add_argument("--qualification-contract-sha256")
    full_gate.add_argument("--predecessor-stage-receipt-set")
    full_gate.add_argument("--qualification-contract")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        repo = resolved_repo(args.repo)
        if args.command == "source-census":
            output_root = ensure_external_root(repo, args.output_root)
            discovery_root = (
                Path(args.discovery_root).resolve()
                if args.discovery_root
                else None
            )
            result = build_source_census(
                repo,
                args.commit,
                output_root,
                discovery_root,
                full_repository=args.full_repository,
            )
        elif args.command == "gate":
            output_root = ensure_external_root(repo, args.output_root)
            result = run_gate(
                repo,
                args.commit,
                Path(args.python),
                Path(args.environment_receipt),
                output_root,
                collect_only=args.collect_only,
            )
        else:
            work_root = ensure_external_root(repo, args.work_root)
            result_root = ensure_external_root(repo, args.result_root)
            result = run_full_repository_gate(
                repo,
                args.commit,
                Path(args.python),
                Path(args.environment_receipt),
                work_root,
                result_root,
                args.execution_context,
                args.predecessor_stage_receipt_set_sha256,
                args.qualification_contract_sha256,
                (
                    Path(args.predecessor_stage_receipt_set)
                    if args.predecessor_stage_receipt_set
                    else None
                ),
                (
                    Path(args.qualification_contract)
                    if args.qualification_contract
                    else None
                ),
            )
    except (CleanCheckoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("status", "PASS") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
