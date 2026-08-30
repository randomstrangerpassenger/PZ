#!/usr/bin/env python
"""Inventory build-tool callers, imports, subprocesses and shared I/O helpers.

The inventory is deliberately descriptive.  It does not move, delete, or
rewrite build tools and it keeps uncertain ownership visible instead of
turning a filename heuristic into authority.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROLES = {
    "active",
    "legacy-required",
    "completed-but-reproducible",
    "historical",
    "diagnostic",
    "test-only",
    "unknown",
}
HELPER_PATTERN = re.compile(
    r"(?:json|jsonl|hash|sha|write|dump|load|read|path|root|atomic|replace)",
    re.IGNORECASE,
)
HISTORICAL_PATTERN = re.compile(
    r"(?:legacy|historical|predecessor|old_|rollback|reproduction)",
    re.IGNORECASE,
)
DIAGNOSTIC_PATTERN = re.compile(
    r"(?:validate|validator|audit|diagnostic|report|inspect|check|guard|closure|seal)",
    re.IGNORECASE,
)
PRODUCER_PATTERN = re.compile(
    r"(?:build|compose|export|generate|materialize|render|compile)",
    re.IGNORECASE,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path, repository_root: Path) -> str:
    return path.resolve().relative_to(repository_root.resolve()).as_posix()


def display_path(path: Path, repository_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(repository_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def git_lines(repository_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repository_root), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr.strip()}"
        )
    return [line for line in result.stdout.splitlines() if line]


def repository_root_for(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"cannot resolve repository root: {result.stderr.strip()}")
    return Path(result.stdout.strip()).resolve()


def physical_line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8-sig", errors="replace").splitlines())


def nonblank_line_count(path: Path) -> int:
    return sum(
        1
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        if line.strip()
    )


def imported_module_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def local_import_stems(tree: ast.AST, known_stems: set[str]) -> set[str]:
    stems: set[str] = set()
    for name in imported_module_names(tree):
        candidate = name.split(".")[-1]
        if candidate in known_stems:
            stems.add(candidate)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module in {"tools.build", ".", None}:
            for alias in node.names:
                if alias.name in known_stems:
                    stems.add(alias.name)
    return stems


def sys_path_calls(tree: ast.AST) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        attribute = node.func
        owner = attribute.value
        if (
            attribute.attr in {"insert", "append"}
            and isinstance(owner, ast.Attribute)
            and owner.attr == "path"
            and isinstance(owner.value, ast.Name)
            and owner.value.id == "sys"
        ):
            rows.append({"method": attribute.attr, "line": node.lineno})
    return rows


def subprocess_aliases(tree: ast.AST) -> tuple[set[str], set[str]]:
    module_aliases: set[str] = set()
    function_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    module_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            for alias in node.names:
                function_aliases.add(alias.asname or alias.name)
    return module_aliases, function_aliases


def subprocess_calls(tree: ast.AST) -> list[dict[str, Any]]:
    module_aliases, function_aliases = subprocess_aliases(tree)
    rows: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name: str | None = None
        if isinstance(node.func, ast.Name) and node.func.id in function_aliases:
            name = node.func.id
        elif (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in module_aliases
        ):
            name = f"{node.func.value.id}.{node.func.attr}"
        if name:
            rows.append({"call": name, "line": node.lineno})
    return rows


def helper_definitions(tree: ast.AST) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and HELPER_PATTERN.search(node.name):
            rows.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "ast_node": type(node).__name__,
                }
            )
    return sorted(rows, key=lambda row: (row["line"], row["name"]))


def has_argparse(tree: ast.AST) -> bool:
    return "argparse" in imported_module_names(tree)


def has_main_guard(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        try:
            value = ast.literal_eval(node.test)
        except (ValueError, TypeError):
            value = None
        if value is False:
            continue
        if isinstance(node.test, ast.Compare) and "__name__" in ast.unparse(node.test):
            if "__main__" in ast.unparse(node.test):
                return True
    return False


def serialization_contracts(source: str, helpers: Iterable[dict[str, Any]]) -> list[str]:
    contracts: set[str] = set()
    helper_names = {row["name"] for row in helpers}
    if "json.dumps" in source or "json.dump" in source or any("json" in name for name in helper_names):
        ensure_ascii = "ensure_ascii=False" if "ensure_ascii=False" in source else "ensure_ascii-default"
        key_order = "sort_keys" if "sort_keys=True" in source else "insertion-order"
        indentation = "indent" if "indent=" in source else "compact-or-default"
        trailer = "trailing-newline" if re.search(r"write\([^\n]*(?:\\n|\\r)", source) else "trailer-unspecified"
        newline = "newline-lf" if 'newline="\\n"' in source or "newline='\\n'" in source else "platform-newline-possible"
        atomic = "atomic" if "replace(" in source or "os.replace" in source else "direct-write"
        contracts.add(
            ":".join(
                ["utf8-json", ensure_ascii, key_order, indentation, trailer, newline, atomic]
            )
        )
    if "sha256" in source or any("sha" in name or "hash" in name for name in helper_names):
        chunk = "8192" if "8192" in source else "chunk-size-owner-defined"
        contracts.add(f"sha256:{chunk}:missing-file-owner-defined")
    return sorted(contracts)


def classify_role(
    path: Path,
    repository_root: Path,
    closure: set[str],
    allowed: set[str],
    fan_in: int,
) -> tuple[str, str]:
    rel = relative(path, repository_root)
    stem = path.stem
    lowered = rel.lower()
    explicit_roles = {
        "Iris/build/description/v2/tools/build/export_registry_runtime_records.py": (
            "legacy-required",
            "public CLI/import adapter retained for the PowerShell Registry Runtime Compatibility route",
        ),
        "Iris/build/description/v2/tools/build/registry_runtime_record_paths.py": (
            "legacy-required",
            "stdlib-only leaf delegated by the retained Registry Runtime Compatibility adapter",
        ),
    }
    if rel in explicit_roles:
        return explicit_roles[rel]
    if "/tests/" in f"/{lowered}/" or path.name.startswith("test_"):
        return "test-only", "path is a test source"
    if stem in closure or stem in allowed:
        return "active", "listed by the current closure or allowed tooling manifest"
    if HISTORICAL_PATTERN.search(stem):
        return "historical", "filename indicates an explicitly preserved historical/legacy route"
    if DIAGNOSTIC_PATTERN.search(stem):
        return "diagnostic", "validator/audit/report naming; authority is not inferred"
    if PRODUCER_PATTERN.search(stem) and fan_in == 0:
        return "completed-but-reproducible", "producer with no static in-tree import caller"
    if fan_in > 0:
        return "legacy-required", "outside current closure but statically imported by repository tools"
    return "unknown", "no authoritative owner signal; retained and excluded from mutation"


@dataclass(frozen=True)
class ParsedFile:
    path: Path
    source: str
    tree: ast.AST | None
    parse_error: str | None


def parse_file(path: Path) -> ParsedFile:
    source = path.read_text(encoding="utf-8-sig", errors="replace")
    try:
        return ParsedFile(path, source, ast.parse(source, filename=str(path)), None)
    except SyntaxError as error:
        return ParsedFile(path, source, None, f"{error.msg}:{error.lineno}:{error.offset}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v2-root", type=Path, required=True)
    parser.add_argument("--build-tools-root", type=Path, required=True)
    parser.add_argument("--closure", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    v2_root = args.v2_root.resolve()
    build_tools_root = args.build_tools_root.resolve()
    closure_path = args.closure.resolve()
    repository_root = repository_root_for(v2_root)
    output_path = args.out if args.out.is_absolute() else repository_root / args.out
    output_path = output_path.resolve()

    closure_payload = json.loads(closure_path.read_text(encoding="utf-8"))
    closure_modules = set(closure_payload["current_closure_modules"])
    allowed_modules = set(closure_payload["current_route_allowed_tooling_modules"])
    tracked = set(git_lines(repository_root, "ls-files"))

    all_v2_python = sorted(v2_root.rglob("*.py"))
    code_v2_python = [path for path in all_v2_python if "staging" not in path.parts]
    build_python = sorted(build_tools_root.rglob("*.py"))
    build_direct = sorted(build_tools_root.glob("*.py"))
    known_stems = {path.stem for path in build_python}
    parsed = [parse_file(path) for path in code_v2_python]

    local_imports: dict[str, set[str]] = {}
    callers: dict[str, set[str]] = defaultdict(set)
    for item in parsed:
        imports = local_import_stems(item.tree, known_stems) if item.tree else set()
        rel = relative(item.path, repository_root)
        local_imports[rel] = imports
        for stem in imports:
            callers[stem].add(rel)

    tool_rows: list[dict[str, Any]] = []
    primary_roles = Counter()
    helper_count = 0
    sys_path_file_count = 0
    subprocess_file_count = 0
    argparse_file_count = 0
    bom_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []

    parsed_by_path = {item.path.resolve(): item for item in parsed}
    for path in build_python:
        item = parsed_by_path[path.resolve()]
        rel = relative(path, repository_root)
        tree = item.tree
        helper_rows = helper_definitions(tree) if tree else []
        sys_rows = sys_path_calls(tree) if tree else []
        process_rows = subprocess_calls(tree) if tree else []
        fan_in = len(callers.get(path.stem, set()))
        role, role_basis = classify_role(
            path, repository_root, closure_modules, allowed_modules, fan_in
        )
        assert role in ROLES
        primary_roles[role] += 1
        helper_count += len(helper_rows)
        sys_path_file_count += bool(sys_rows)
        subprocess_file_count += bool(process_rows)
        argparse_file_count += bool(tree and has_argparse(tree))
        raw = path.read_bytes()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        if has_bom:
            bom_rows.append(
                {
                    "path": rel,
                    "tracked": rel in tracked,
                    "sha256": sha256_bytes(raw),
                    "caller_count": fan_in,
                    "source_hash_consumer_status": "unresolved_requires_change_6b_review",
                }
            )

        row = {
            "path": rel,
            "stem": path.stem,
            "tracked": rel in tracked,
            "physical_lines": physical_line_count(path),
            "nonblank_lines": nonblank_line_count(path),
            "utf8_bom": has_bom,
            "parse_status": "passed" if tree else "failed",
            "parse_error": item.parse_error,
            "primary_role": role,
            "role_basis": role_basis,
            "validation_roles": [],
            "owner": (
                "round3_current_closure"
                if path.stem in closure_modules
                else "round3_allowed_tooling"
                if path.stem in allowed_modules
                else "iris_residual_refactor_change_5"
                if rel in {
                    "Iris/build/description/v2/tools/build/export_registry_runtime_records.py",
                    "Iris/build/description/v2/tools/build/registry_runtime_record_paths.py",
                }
                else "unconfirmed"
            ),
            "entrypoints": {
                "direct_script": bool(tree and has_main_guard(tree)),
                "python_m": bool(tree and has_main_guard(tree)),
                "package_import": bool(callers.get(path.stem)),
                "bare_import": any("tools.build." not in caller for caller in callers.get(path.stem, set())),
            },
            "static_callers": sorted(callers.get(path.stem, set())),
            "static_caller_count": fan_in,
            "local_import_stems": sorted(local_imports.get(rel, set())),
            "sys_path_calls": sys_rows,
            "argparse_imported": bool(tree and has_argparse(tree)),
            "subprocess_calls": process_rows,
            "subprocess_disposition": (
                {
                    "decision": "retain",
                    "reason": (
                        "no conversion is authorized without a complete function input/output, cwd, "
                        "environment, exit-code, stdout/stderr, timeout, and partial-artifact comparison"
                    ),
                }
                if process_rows
                else {"decision": "not_applicable", "reason": "no AST-detected subprocess call"}
            ),
            "helper_definitions": helper_rows,
            "serialization_hash_contract_ids": serialization_contracts(
                item.source, helper_rows
            ),
            "read_write_artifact_status": "requires_owner_contract_matrix",
        }
        tool_rows.append(row)

        if (
            path.parent == build_tools_root
            and path.stem not in closure_modules
            and path.stem not in allowed_modules
            and role != "unknown"
            and fan_in <= 2
            and not process_rows
            and row["physical_lines"] <= 400
        ):
            candidate_rows.append(
                {
                    "path": rel,
                    "stem": path.stem,
                    "primary_role": role,
                    "physical_lines": row["physical_lines"],
                    "static_caller_count": fan_in,
                    "static_callers": row["static_callers"],
                    "has_main_guard": row["entrypoints"]["direct_script"],
                    "candidate_status": "eligible_for_owner_inspection",
                }
            )

    candidate_rows.sort(
        key=lambda row: (
            row["static_caller_count"],
            row["physical_lines"],
            row["path"],
        )
    )
    registry_path = build_tools_root / "dvf_3_3_registry_authority_canonical_closure.py"
    registry_lines = {
        "path": relative(registry_path, repository_root),
        "physical": physical_line_count(registry_path),
        "nonblank": nonblank_line_count(registry_path),
        "disposition": "deferred_by_design_read_only",
    }

    payload = {
        "schema_version": "iris-residual-phase0-inventory-v1",
        "validation_status": "passed",
        "subject": {
            "commit": git_lines(repository_root, "rev-parse", "HEAD")[0],
            "tree": git_lines(repository_root, "rev-parse", "HEAD^{tree}")[0],
            "repository_root_name": repository_root.name,
        },
        "command_contract": {
            "v2_root": relative(v2_root, repository_root),
            "build_tools_root": relative(build_tools_root, repository_root),
            "closure": relative(closure_path, repository_root),
            "output": display_path(output_path, repository_root),
            "python_line_definition": {
                "physical": "splitlines including blank and comment lines",
                "nonblank": "splitlines whose stripped value is non-empty",
            },
            "staging_excluded_from_code_search": True,
            "staging_included_in_evidence_inventory": True,
            "tests_included_in_v2_recursive_count": True,
            "subprocess_detection": "AST import/from-import aliases and calls",
            "sys_path_detection": "AST sys.path.insert/append calls",
            "helper_detection": {
                "ast_nodes": ["FunctionDef", "AsyncFunctionDef"],
                "name_regex": HELPER_PATTERN.pattern,
            },
        },
        "counts": {
            "v2_python_recursive_all": len(all_v2_python),
            "v2_python_code_search_excluding_staging": len(code_v2_python),
            "build_tools_python_recursive": len(build_python),
            "build_tools_python_root_direct": len(build_direct),
            "build_tools_physical_lines": sum(row["physical_lines"] for row in tool_rows),
            "build_tools_nonblank_lines": sum(row["nonblank_lines"] for row in tool_rows),
            "sys_path_files_build_tools": sys_path_file_count,
            "sys_path_files_v2_code_search": sum(
                1 for item in parsed if item.tree and sys_path_calls(item.tree)
            ),
            "helper_definitions_build_tools": helper_count,
            "helper_definition_files_build_tools": sum(
                1 for row in tool_rows if row["helper_definitions"]
            ),
            "argparse_files_build_tools": argparse_file_count,
            "subprocess_files_build_tools": subprocess_file_count,
            "utf8_bom_files_build_tools": len(bom_rows),
            "tracked_build_tools": sum(row["tracked"] for row in tool_rows),
            "untracked_build_tools": sum(not row["tracked"] for row in tool_rows),
            "primary_roles": dict(sorted(primary_roles.items())),
        },
        "closure": {
            "manifest_path": relative(closure_path, repository_root),
            "manifest_sha256": sha256_file(closure_path),
            "current_closure_count": closure_payload["current_closure_count"],
            "current_closure_modules": sorted(closure_modules),
            "current_route_allowed_tooling_count": len(allowed_modules),
            "current_route_allowed_tooling_modules": sorted(allowed_modules),
            "current_route_allowed_tooling_policy": closure_payload[
                "current_route_allowed_tooling_policy"
            ],
        },
        "registry_giant": registry_lines,
        "bom_rows": bom_rows,
        "pilot_candidate_rows": candidate_rows,
        "tools": tool_rows,
        "unknown_paths": sorted(
            row["path"] for row in tool_rows if row["primary_role"] == "unknown"
        ),
        "claim_boundary": (
            "role heuristics are inventory dispositions only; unknown paths remain preserved "
            "and are ineligible for move/delete/commonization"
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "validation_status": payload["validation_status"],
                "build_tools_python_recursive": len(build_python),
                "output": display_path(output_path, repository_root),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
