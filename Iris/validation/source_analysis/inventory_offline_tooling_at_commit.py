"""Build a read-only inventory for Iris offline tooling.

The inventory is descriptive evidence, not a new authority taxonomy.  Source
bytes are read from an exact Git commit.  A caller may additionally provide a
clean materialized checkout to keep tracked and physical denominators separate.
All generated files are written below a repository-external output root.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from Iris.validation.execution.checkout_environment import (
    CleanCheckoutError,
    blob_id,
    bytes_at_commit,
    canonical_json_bytes,
    ensure_external_root,
    git_identity,
    json_at_commit,
    resolved_repo,
    sha256_bytes,
    sha256_file,
    tracked_paths,
    write_json_external,
)


TOOLS_ROOT = "Iris/build/description/v2/tools/build"
STAGING_ROOT = "Iris/build/description/v2/staging"
CLOSURE_PATH = "Iris/_docs/round3/round3_active_core_closure.json"
OUTPUT_ISOLATION_SCHEMA_PATH = (
    "Iris/validation/execution/contracts/"
    "output_isolation_batch_registry.schema.json"
)
HELPER_NAMES = {
    "load_json",
    "write_json",
    "load_jsonl",
    "write_jsonl",
    "write_text",
    "sha256_file",
    "file_sha256",
    "now_iso",
}
WRITE_CALL_NAMES = {
    "dump",
    "dumps",
    "mkdir",
    "open",
    "replace",
    "rename",
    "write",
    "write_bytes",
    "write_text",
    "writelines",
}
PROVIDER_STEM_PATTERN = re.compile(
    r"(?:^_|_)(?:common|paths?|io|contract)(?:_|$)"
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CleanCheckoutError(message)


def _relative_python_paths(paths: Iterable[str]) -> list[str]:
    prefix = f"{TOOLS_ROOT}/"
    return sorted(
        path
        for path in paths
        if path.startswith(prefix) and path.endswith(".py")
    )


def _root_direct(paths: Iterable[str]) -> list[str]:
    prefix = f"{TOOLS_ROOT}/"
    return sorted(
        path
        for path in paths
        if path.startswith(prefix)
        and path.endswith(".py")
        and "/" not in path[len(prefix) :]
    )


def _node_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _import_stems(tree: ast.AST) -> set[str]:
    stems: set[str] = set()
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        for module in modules:
            stems.add(module.rsplit(".", 1)[-1])
    return stems


def _parents_depths(tree: ast.AST) -> list[int]:
    depths: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        value = node.value
        if not isinstance(value, ast.Attribute) or value.attr != "parents":
            continue
        index = node.slice
        if isinstance(index, ast.Constant) and isinstance(index.value, int):
            depths.add(index.value)
    return sorted(depths)


def _call_names(tree: ast.AST) -> list[str]:
    return sorted(
        {
            name
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            for name in [_node_name(node.func)]
            if name
        }
    )


def _function_names(tree: ast.AST) -> list[str]:
    return sorted(
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )


def _top_level_write_calls(tree: ast.AST) -> list[str]:
    names: set[str] = set()
    if not isinstance(tree, ast.Module):
        return []
    for statement in tree.body:
        if isinstance(
            statement,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            continue
        for node in ast.walk(statement):
            if isinstance(node, ast.Call):
                name = _node_name(node.func)
                if name in WRITE_CALL_NAMES:
                    names.add(name)
    return sorted(names)


def _literal_write_targets(tree: ast.AST) -> list[str]:
    targets: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _node_name(node.func)
        if name not in WRITE_CALL_NAMES or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            targets.add(first.value)
    return sorted(targets)


def _has_main_guard(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        if not isinstance(node.left, ast.Name) or node.left.id != "__name__":
            continue
        if any(
            isinstance(value, ast.Constant) and value.value == "__main__"
            for value in node.comparators
        ):
            return True
    return False


def _classify_role(
    stem: str,
    *,
    current_core: set[str],
    allowed_tooling: set[str],
    calls: set[str],
    has_main_guard: bool,
) -> tuple[str, str, str]:
    if stem in current_core:
        return (
            "active",
            "owner_bound",
            "current core closure manifest",
        )
    if stem in allowed_tooling:
        return (
            "active_tooling",
            "owner_bound",
            "approved current-route tooling manifest",
        )
    lowered = stem.casefold()
    if lowered.startswith("test_"):
        return "test_only", "owner_unknown", "test filename"
    if "historical" in lowered or "predecessor" in lowered:
        return "historical", "owner_unknown", "historical filename marker"
    if lowered.startswith(("validate_", "report_", "audit_", "check_", "inspect_")):
        return "diagnostic", "owner_unknown", "validator/report filename"
    if has_main_guard and calls & WRITE_CALL_NAMES:
        return (
            "completed_or_active_producer",
            "owner_unknown",
            "executable with statically observed write-capable call",
        )
    if PROVIDER_STEM_PATTERN.search(lowered):
        return "legacy_required", "owner_unknown", "shared support provider"
    return "unknown_role", "owner_unknown", "no owner-approved role evidence"


def _execution_role(
    stem: str,
    role: str,
    *,
    calls: set[str],
    has_main_guard: bool,
) -> str:
    if role in {"diagnostic", "test_only"} and not (calls & WRITE_CALL_NAMES):
        return "read_only_validator"
    if role == "historical":
        return "historical_replay"
    if has_main_guard and calls & WRITE_CALL_NAMES:
        authority_tokens = {
            "adoption",
            "apply",
            "cutover",
            "promotion",
            "publish",
            "seal",
        }
        if authority_tokens & set(stem.casefold().split("_")):
            return "explicit_authority_writer"
        return "disposable_producer"
    if role == "unknown_role":
        return "unknown"
    return "read_only_validator"


def _serialization_observations(
    source: str,
    *,
    calls: set[str],
) -> list[str]:
    rows: list[str] = []
    if {"dump", "dumps", "load", "loads"} & calls:
        rows.append("json_api_observed")
    if "ensure_ascii=False" in source.replace(" ", ""):
        rows.append("ensure_ascii_false_literal")
    if "sort_keys=True" in source.replace(" ", ""):
        rows.append("sort_keys_true_literal")
    if "indent=2" in source.replace(" ", ""):
        rows.append("indent_2_literal")
    if "encoding=\"utf-8\"" in source.replace(" ", "") or "encoding='utf-8'" in source.replace(" ", ""):
        rows.append("utf8_literal")
    if "hashlib.sha256" in source:
        rows.append("sha256_observed")
    if "datetime.now" in source or "time.time" in source:
        rows.append("wall_clock_observed")
    return sorted(rows)


def _analyze_tools(
    repo: Path,
    commit: str,
    paths: list[str],
    *,
    current_core: set[str],
    allowed_tooling: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    parsed: dict[str, dict[str, Any]] = {}
    stem_to_path = {Path(path).stem: path for path in paths}
    for path in paths:
        payload = bytes_at_commit(repo, commit, path)
        source = payload.decode("utf-8-sig", errors="surrogateescape")
        parse_error: str | None = None
        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as exc:
            tree = ast.Module(body=[], type_ignores=[])
            parse_error = f"{exc.__class__.__name__}: {exc}"
        calls = set(_call_names(tree))
        functions = _function_names(tree)
        top_level_write_calls = _top_level_write_calls(tree)
        role, owner_status, role_basis = _classify_role(
            Path(path).stem,
            current_core=current_core,
            allowed_tooling=allowed_tooling,
            calls=calls,
            has_main_guard=_has_main_guard(tree),
        )
        parsed[path] = {
            "path": path,
            "stem": Path(path).stem,
            "git_blob_id": blob_id(repo, commit, path),
            "sha256": sha256_bytes(payload),
            "size": len(payload),
            "physical_lines": len(payload.splitlines()),
            "parse_error": parse_error,
            "imports": sorted(_import_stems(tree)),
            "parents_depths": _parents_depths(tree),
            "sys_path_mutation": "sys.path" in source and any(
                token in source for token in (".append(", ".insert(")
            ),
            "argparse_observed": "argparse" in _import_stems(tree),
            "subprocess_observed": "subprocess" in _import_stems(tree),
            "has_main_guard": _has_main_guard(tree),
            "direct_script_supported": _has_main_guard(tree),
            "module_execution_candidate": _has_main_guard(tree),
            "bare_import_bootstrap_observed": (
                "sys.path" in source
                and any(token in source for token in (".append(", ".insert("))
            ),
            "function_names": functions,
            "helper_definitions": sorted(set(functions) & HELPER_NAMES),
            "call_names": sorted(calls),
            "write_capable_calls": sorted(calls & WRITE_CALL_NAMES),
            "import_time_write_capable_calls": top_level_write_calls,
            "execution_time_write_capable_calls": sorted(
                (calls & WRITE_CALL_NAMES) - set(top_level_write_calls)
            ),
            "observed_literal_write_targets": _literal_write_targets(tree),
            "serialization_observations": _serialization_observations(
                source, calls=calls
            ),
            "classified_role": role,
            "owner_status": owner_status,
            "owner": (
                "round3_active_core_closure"
                if owner_status == "owner_bound"
                else "unconfirmed"
            ),
            "role_basis": role_basis,
            "execution_role": _execution_role(
                Path(path).stem,
                role,
                calls=calls,
                has_main_guard=_has_main_guard(tree),
            ),
            "disposition": (
                "move_delete_consolidate_forbidden"
                if owner_status == "owner_unknown" or role == "unknown_role"
                else "preserve"
            ),
            "unresolved_question": (
                "confirm owner, role, caller contract, and retention authority"
                if owner_status == "owner_unknown" or role == "unknown_role"
                else None
            ),
            "decision_owner": (
                "repository_owner"
                if owner_status == "owner_unknown" or role == "unknown_role"
                else "round3_active_core_closure"
            ),
        }

    caller_sets: defaultdict[str, set[str]] = defaultdict(set)
    edges: set[tuple[str, str]] = set()
    all_python = [
        path
        for path in tracked_paths(repo, commit)
        if path.endswith(".py")
        and path.startswith("Iris/build/description/v2/")
    ]
    for caller in all_python:
        source = bytes_at_commit(repo, commit, caller).decode(
            "utf-8-sig", errors="surrogateescape"
        )
        try:
            imports = _import_stems(ast.parse(source, filename=caller))
        except SyntaxError:
            imports = set()
        for imported in sorted(imports & set(stem_to_path)):
            provider = stem_to_path[imported]
            caller_sets[provider].add(caller)
            edges.add((caller, provider))

    rows: list[dict[str, Any]] = []
    for path in sorted(parsed):
        row = parsed[path]
        callers = sorted(caller_sets[path])
        row["static_callers"] = callers
        row["static_caller_count"] = len(callers)
        row["static_tool_callers"] = [
            caller
            for caller in callers
            if caller.startswith(f"{TOOLS_ROOT}/")
        ]
        row["static_test_callers"] = [
            caller for caller in callers if "/tests/" in caller
        ]
        row["static_tool_caller_count"] = len(row["static_tool_callers"])
        row["static_test_caller_count"] = len(row["static_test_callers"])
        row["caller_axis"] = (
            "caller_observed" if callers else "no_caller_observed"
        )
        row["shared_module_provider"] = bool(
            callers or PROVIDER_STEM_PATTERN.search(row["stem"])
        )
        rows.append(row)
    return rows, [
        {"caller": caller, "provider": provider}
        for caller, provider in sorted(edges)
    ]


def _materialized_identity(
    materialized_root: Path | None,
    relative_paths: Iterable[str],
) -> dict[str, dict[str, Any]]:
    if materialized_root is None:
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for relative in sorted(relative_paths):
        path = materialized_root / relative
        if path.is_file():
            rows[relative] = {
                "working_sha256": sha256_file(path),
                "working_size": path.stat().st_size,
            }
    return rows


def _physical_tool_paths(materialized_root: Path | None) -> list[str]:
    if materialized_root is None:
        return []
    root = materialized_root / TOOLS_ROOT
    return sorted(
        path.relative_to(materialized_root).as_posix()
        for path in root.rglob("*.py")
        if path.is_file()
    )


def _retention_family(relative: str) -> tuple[str, str]:
    lowered = relative.casefold()
    if any(token in lowered for token in ("sealed", "closeout", "receipt")):
        return "sealed_or_closeout_evidence", "path-marker heuristic"
    if any(token in lowered for token in ("tmp", "sandbox", "probe", "preview")):
        return "backup_sandbox_or_probe", "path-marker heuristic"
    if "candidate" in lowered:
        return "disposable_intermediate_candidate", "path-marker heuristic"
    if "fixture" in lowered or "reproduc" in lowered:
        return "reproducibility_fixture_or_input", "path-marker heuristic"
    return "retention_unresolved", "no owner-approved retention evidence"


def _retention_inventory(
    repo: Path,
    commit: str,
    materialized_root: Path | None,
) -> dict[str, Any]:
    tracked = {
        path
        for path in tracked_paths(repo, commit)
        if path.startswith(f"{STAGING_ROOT}/")
    }
    physical: list[str]
    if materialized_root is None:
        physical = sorted(tracked)
    else:
        staging = materialized_root / STAGING_ROOT
        physical = sorted(
            path.relative_to(materialized_root).as_posix()
            for path in staging.rglob("*")
            if path.is_file()
        )
    rows = []
    family_counts: Counter[str] = Counter()
    for relative in physical:
        family, basis = _retention_family(relative)
        family_counts[family] += 1
        path = materialized_root / relative if materialized_root else None
        rows.append(
            {
                "path": relative,
                "tracked": relative in tracked,
                "size": path.stat().st_size if path and path.is_file() else None,
                "retention_family": family,
                "classification_basis": basis,
                "owner": "unconfirmed",
                "mutation_disposition": "move_delete_forbidden",
            }
        )
    return {
        "schema_version": "iris-offline-tool-retention-inventory-v1",
        "subject": git_identity(repo, commit),
        "tracked_count": len(tracked),
        "physical_count": len(physical),
        "family_counts": dict(sorted(family_counts.items())),
        "no_move_no_delete": True,
        "rows": rows,
    }


def build_inventory(
    repo: Path,
    commit: str,
    output_root: Path,
    *,
    materialized_root: Path | None,
    unknown_role_ceiling: int | None,
) -> dict[str, Any]:
    subject = git_identity(repo, commit)
    all_tracked = tracked_paths(repo, subject["commit"])
    tracked_tools = _relative_python_paths(all_tracked)
    closure = json_at_commit(repo, subject["commit"], CLOSURE_PATH)
    current_core = set(closure["current_closure_modules"])
    allowed_tooling = set(
        closure["current_route_allowed_tooling_modules"]
    )
    if materialized_root is not None:
        materialized_root = materialized_root.resolve()
        _require(
            git_identity(materialized_root, "HEAD") == subject,
            "materialized checkout does not match the exact subject",
        )

    tools, edges = _analyze_tools(
        repo,
        subject["commit"],
        tracked_tools,
        current_core=current_core,
        allowed_tooling=allowed_tooling,
    )
    working = _materialized_identity(materialized_root, tracked_tools)
    for row in tools:
        row.update(working.get(row["path"], {}))

    physical_tools = _physical_tool_paths(materialized_root)
    denominators = [
        {
            "denominator_id": "tools_build_recursive_tracked",
            "root": TOOLS_ROOT,
            "scan_method": "git ls-tree exact commit recursive *.py",
            "inclusion_rule": "tracked Python descendants",
            "exclusion_rule": "untracked and ignored files",
            "count": len(tracked_tools),
        },
        {
            "denominator_id": "tools_build_root_direct_tracked",
            "root": TOOLS_ROOT,
            "scan_method": "git ls-tree exact commit root-direct *.py",
            "inclusion_rule": "tracked direct Python children",
            "exclusion_rule": "descendants, untracked and ignored files",
            "count": len(_root_direct(tracked_tools)),
        },
        {
            "denominator_id": "current_core",
            "root": CLOSURE_PATH,
            "scan_method": "round3 active-core closure manifest",
            "inclusion_rule": "manifest modules",
            "exclusion_rule": "allowed tooling and all other tools",
            "count": len(current_core),
        },
        {
            "denominator_id": "allowed_tooling",
            "root": CLOSURE_PATH,
            "scan_method": "round3 approved-tooling manifest",
            "inclusion_rule": "manifest approved tooling modules",
            "exclusion_rule": "current core and all other tools",
            "count": len(allowed_tooling),
        },
    ]
    if materialized_root is not None:
        denominators.extend(
            [
                {
                    "denominator_id": "tools_build_recursive_physical",
                    "root": TOOLS_ROOT,
                    "scan_method": "materialized checkout recursive *.py",
                    "inclusion_rule": "all accessible physical Python descendants",
                    "exclusion_rule": "inaccessible paths",
                    "count": len(physical_tools),
                },
                {
                    "denominator_id": "tools_build_root_direct_physical",
                    "root": TOOLS_ROOT,
                    "scan_method": "materialized checkout root-direct *.py",
                    "inclusion_rule": "all accessible direct Python children",
                    "exclusion_rule": "descendants and inaccessible paths",
                    "count": len(_root_direct(physical_tools)),
                },
            ]
        )
    for row in denominators:
        row["subject"] = subject
        row["set_sha256"] = sha256_bytes(
            canonical_json_bytes(
                sorted(
                    tracked_tools
                    if row["denominator_id"] == "tools_build_recursive_tracked"
                    else _root_direct(tracked_tools)
                    if row["denominator_id"] == "tools_build_root_direct_tracked"
                    else current_core
                    if row["denominator_id"] == "current_core"
                    else allowed_tooling
                    if row["denominator_id"] == "allowed_tooling"
                    else physical_tools
                    if row["denominator_id"] == "tools_build_recursive_physical"
                    else _root_direct(physical_tools)
                )
            )
        )

    role_counts = Counter(row["classified_role"] for row in tools)
    owner_counts = Counter(row["owner_status"] for row in tools)
    caller_counts = Counter(row["caller_axis"] for row in tools)
    unknown_count = role_counts["unknown_role"]
    approved_ceiling = (
        55 if unknown_role_ceiling is None else unknown_role_ceiling
    )
    _require(
        unknown_count <= approved_ceiling,
        f"unknown role count {unknown_count} exceeds ceiling {approved_ceiling}",
    )
    role_manifest = {
        "schema_version": "iris-offline-tool-role-manifest-v1",
        "subject": subject,
        "denominator_id": "tools_build_recursive_tracked",
        "total": len(tools),
        "role_axis": {
            "classified_role": len(tools) - unknown_count,
            "unknown_role": unknown_count,
            "detail_counts": dict(sorted(role_counts.items())),
        },
        "owner_axis": dict(sorted(owner_counts.items())),
        "caller_axis": dict(sorted(caller_counts.items())),
        "owner_decision": {
            "predecessor_seed_unknown_role_count": 55,
            "unknown_role_ceiling": approved_ceiling,
            "basis": (
                "sealed predecessor seed 55 unless an explicit owner-approved "
                "ceiling is supplied; "
                "unknown rows remain move/delete/consolidate forbidden"
            ),
            "physical_move_approved": False,
            "retention_mutation_approved": False,
        },
        "rows": [
            {
                "path": row["path"],
                "role": row["classified_role"],
                "execution_role": row["execution_role"],
                "owner_status": row["owner_status"],
                "caller_axis": row["caller_axis"],
                "basis": row["role_basis"],
                "disposition": row["disposition"],
                "unresolved_question": row["unresolved_question"],
                "decision_owner": row["decision_owner"],
            }
            for row in tools
        ],
    }
    shared_manifest = {
        "schema_version": "iris-offline-tool-shared-module-manifest-v1",
        "subject": subject,
        "providers": [
            {
                "path": row["path"],
                "stem": row["stem"],
                "owner": row["owner"],
                "current_route": row["stem"] in current_core
                or row["stem"] in allowed_tooling,
                "fan_in_all": row["static_caller_count"],
                "fan_in_tools_only": sum(
                    caller.startswith(f"{TOOLS_ROOT}/")
                    for caller in row["static_callers"]
                ),
                "fan_in_tests": sum(
                    "/tests/" in caller for caller in row["static_callers"]
                ),
                "contract_overlap_status": "requires_owner_contract_matrix",
            }
            for row in tools
            if row["shared_module_provider"]
        ],
        "edges": edges,
    }
    serialization_manifest = {
        "schema_version": "iris-offline-tool-serialization-census-v1",
        "subject": subject,
        "contract_family_policy": "inventory_only_no_global_writer_inference",
        "rows": [
            {
                "path": row["path"],
                "helper_definitions": row["helper_definitions"],
                "observations": row["serialization_observations"],
                "owner": row["owner"],
                "migration_disposition": "not_selected",
            }
            for row in tools
            if row["helper_definitions"] or row["serialization_observations"]
        ],
    }
    retention = _retention_inventory(
        repo, subject["commit"], materialized_root
    )
    registry = {
        "schema_version": "iris-receipt-migration-batch-registry-v1",
        "subject": subject,
        "source_denominator_id": "tools_build_recursive_tracked",
        "source_denominator_set_sha256": next(
            row["set_sha256"]
            for row in denominators
            if row["denominator_id"] == "tools_build_recursive_tracked"
        ),
        "authority_effect": "none",
        "batches": [],
        "non_claim": "no subprocess or receipt migration batch is selected",
    }

    denominator_payload = {
        "schema_version": "iris-offline-tool-denominator-registry-v1",
        "subject": subject,
        "rows": denominators,
    }
    tool_inventory_payload = {
        "schema_version": "iris-offline-tool-inventory-v1",
        "subject": subject,
        "tracked_tool_count": len(tools),
        "rows": tools,
    }
    denominator_path = output_root / "manifests" / "denominator_registry.json"
    tool_inventory_path = output_root / "manifests" / "tool_inventory.json"
    denominator_hash = sha256_bytes(canonical_json_bytes(denominator_payload))
    tool_inventory_hash = sha256_bytes(
        canonical_json_bytes(tool_inventory_payload)
    )
    isolation_registry_path = (
        output_root / "manifests" / "output_isolation_batch_registry.json"
    )
    isolation_ratification_path = (
        output_root
        / "manifests"
        / "output_isolation_batch_registry.ratification.json"
    )
    isolation_registry = {
        "schema_version": "iris-output-isolation-batch-registry-v1",
        "schema": {
            "path": OUTPUT_ISOLATION_SCHEMA_PATH,
            "git_blob_id": blob_id(
                repo, subject["commit"], OUTPUT_ISOLATION_SCHEMA_PATH
            ),
            "sha256": sha256_bytes(
                bytes_at_commit(
                    repo, subject["commit"], OUTPUT_ISOLATION_SCHEMA_PATH
                )
            ),
        },
        "subject": subject,
        "registry_owner": (
            "Iris Repository Validation / Clean-Checkout "
            "Reproducibility Authority"
        ),
        "source_denominator": {
            "path": denominator_path.as_posix(),
            "sha256": denominator_hash,
            "denominator_id": "tools_build_recursive_tracked",
            "set_sha256": registry["source_denominator_set_sha256"],
        },
        "census_manifest": {
            "path": tool_inventory_path.as_posix(),
            "sha256": tool_inventory_hash,
        },
        "owner_ratification": {
            "required": True,
            "path": isolation_ratification_path.as_posix(),
        },
        "selected_rows": [],
        "selected_owner_unknown_count": 0,
        "selected_unknown_role_count": 0,
        "mutation_fail_closed_on_registry_drift": True,
        "mutation_disposition": "no_selected_change2_source_mutation",
    }
    isolation_registry_hash = sha256_bytes(
        canonical_json_bytes(isolation_registry)
    )
    isolation_ratification = {
        "schema_version": "iris-output-isolation-owner-ratification-v1",
        "subject": subject,
        "decision_owner": "repository_owner",
        "authorization_basis": (
            "The owner instruction for this task pre-authorizes required "
            "owner decisions; no selected producer mutation is present."
        ),
        "registry": {
            "path": isolation_registry_path.as_posix(),
            "sha256": isolation_registry_hash,
            "schema_version": "iris-output-isolation-batch-registry-v1",
        },
        "census_manifest": {
            "path": tool_inventory_path.as_posix(),
            "sha256": tool_inventory_hash,
        },
        "denominator_manifest": {
            "path": denominator_path.as_posix(),
            "sha256": denominator_hash,
        },
        "selected_row_count": 0,
        "source_mutation_authorized": False,
        "registry_drift_fail_closed": True,
    }
    outputs = {
        "denominator_registry.json": denominator_payload,
        "tool_inventory.json": tool_inventory_payload,
        "shared_module_manifest.json": shared_manifest,
        "serialization_contract_census.json": serialization_manifest,
        "tool_role_manifest.json": role_manifest,
        "retention_inventory.json": retention,
        "receipt_migration_batch_registry.json": registry,
        "output_isolation_batch_registry.json": isolation_registry,
        "output_isolation_batch_registry.ratification.json": (
            isolation_ratification
        ),
    }
    output_rows = []
    for name, payload in outputs.items():
        path = output_root / "manifests" / name
        digest = write_json_external(repo, path, payload)
        output_rows.append(
            {"path": path.as_posix(), "sha256": digest}
        )
    index = {
        "schema_version": "iris-offline-tool-inventory-index-v1",
        "status": "PASS",
        "subject": subject,
        "output_rows": output_rows,
        "source_mutation_authorized": False,
        "authority_effect": "none",
        "no_move_no_delete": True,
    }
    index_path = output_root / "inventory_index.json"
    index_sha256 = write_json_external(repo, index_path, index)
    return {
        "status": "PASS",
        "subject": subject,
        "tracked_tool_count": len(tools),
        "unknown_role_count": unknown_count,
        "inventory_index_path": index_path.as_posix(),
        "inventory_index_sha256": index_sha256,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory Iris offline tools from an exact Git subject."
    )
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--materialized-root")
    parser.add_argument("--unknown-role-ceiling", type=int)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        repo = resolved_repo(args.repo)
        output_root = ensure_external_root(repo, args.output_root)
        _require(
            not any(output_root.iterdir()),
            f"output root must be empty: {output_root}",
        )
        result = build_inventory(
            repo,
            args.commit,
            output_root,
            materialized_root=(
                Path(args.materialized_root)
                if args.materialized_root
                else None
            ),
            unknown_role_ceiling=args.unknown_role_ceiling,
        )
    except (CleanCheckoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
