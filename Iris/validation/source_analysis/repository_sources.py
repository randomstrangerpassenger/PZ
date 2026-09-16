"""Static repository source and dependency inventory."""
from __future__ import annotations

import ast
import configparser
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from Iris.validation.execution.checkout_environment import (
    CleanCheckoutError,
    blob_id,
    bytes_at_commit,
    git_identity,
    json_at_commit,
    sha256_file,
    tracked_paths,
    write_json_external,
)


from Iris.validation.execution.repository_contracts import (
    CANONICAL_GATE_PATH,
    FULL_REPOSITORY_GATE_PATH,
    PYTEST_INI_PATH,
    REPOSITORY_IMPORT_PREFIXES,
    REQUIRED_MANIFEST_PATH,
    TAXONOMY_PATH,
)
from Iris.validation.execution.repository_contracts import _validate_consumer_integration_evidence


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
    for row in contract["source_disposition_policy"].get(
        "evidence_only_sources", []
    ):
        if row.get("physical_preservation") != "executable_source":
            raise CleanCheckoutError(
                "evidence-only executable source lacks physical preservation"
            )
        roles[row["path"]] = {
            "execution_role": "not_required",
            "authority_class": "evidence_only_executable_source",
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
        sources = sorted(
            set(sources)
            | (
                set(_explicit_current_required_paths(gate_contract))
                & tracked
            )
        )
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
            "evidence_only_source_count": sum(
                row.get("authority_class")
                == "evidence_only_executable_source"
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
