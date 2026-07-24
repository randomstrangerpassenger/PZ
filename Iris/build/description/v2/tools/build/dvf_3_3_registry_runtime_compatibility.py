#!/usr/bin/env python3
"""Canonical algorithms for the DVF 3.3 Registry Runtime Compatibility round.

This module deliberately keeps repository census and identity algorithms in one
place.  Callers use the standalone validator or runner; the bridge exporter,
PowerShell package command, and Windows wrapper must not import this module.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


ROUND_ID = "dvf_3_3_registry_runtime_compatibility"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
ROUTE_CLASSES = {
    "executable_current",
    "test_current",
    "operator_current",
    "diagnostic",
    "historical_non_executable",
    "static_reference",
    "unknown",
}
TARGET_TOKENS = (
    "export_dvf_3_3_lua_bridge",
    "export_lua_bridge",
    "package_iris.ps1",
)
PRODUCTION_INTEGRATION_PATHS = {
    "Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py",
    "Iris/tools/package_iris.ps1",
    "Iris/_docs/round3/current_route_required_validations.json",
}
PREINTEGRATION_NEW_PATHS = {
    "Iris/build/description/v2/tools/build/dvf_3_3_registry_runtime_compatibility.py",
    "Iris/build/description/v2/tools/build/run_dvf_3_3_registry_runtime_compatibility.py",
    "Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py",
    "Iris/build/description/v2/tools/build/export_registry_runtime_records.py",
    "Iris/tools/inspect_registry_runtime_compatibility.ps1",
}
PREINTEGRATION_GOVERNANCE_PATHS = {".gitignore"}
PREINTEGRATION_NEW_PREFIXES = (
    "Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_",
    "Iris/build/description/v2/tests/fixtures/registry_runtime_compatibility/",
)
HISTORICAL_MARKERS = (
    "/.tmp/",
    "/_archive/",
    "/archive/",
    "/backup/",
    "/staging/",
    "/_docs/round1/",
    "/_docs/round2/",
    "/_docs/refactor/_done/",
    "retained_historical",
    "baseline_tree_snapshot",
    "disposition_candidates",
    "disposition_manifest",
    "test_collectability_signals",
    "test_taxonomy",
)
TEXT_SUFFIXES = {
    ".cfg",
    ".cmd",
    ".json",
    ".jsonl",
    ".lua",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


class CompatibilityError(RuntimeError):
    """Typed fail-closed error emitted by canonical compatibility algorithms."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class SnapshotFile:
    path: str
    blob_sha: str
    data: bytes


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def run_git(
    repo: Path,
    *args: str,
    check: bool = True,
    text: bool = False,
) -> subprocess.CompletedProcess[Any]:
    command = [
        "git",
        "-c",
        f"safe.directory={repo.as_posix()}",
        "-c",
        "core.longpaths=true",
        "-C",
        str(repo),
        *args,
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=text,
        encoding="utf-8" if text else None,
    )
    if check and result.returncode != 0:
        stderr = result.stderr if text else result.stderr.decode("utf-8", "replace")
        raise CompatibilityError(
            "git_command_failed",
            f"{' '.join(command)} failed ({result.returncode}): {stderr}",
        )
    return result


def git_text(repo: Path, *args: str) -> str:
    return run_git(repo, *args, text=True).stdout.strip()


def normalized_relative(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError as exc:
        raise CompatibilityError(
            "path_outside_repository",
            f"Path must stay inside repository: {path}",
        ) from exc


def ensure_commit(repo: Path, commit: str) -> str:
    resolved = git_text(repo, "rev-parse", "--verify", f"{commit}^{{commit}}")
    if resolved != commit:
        raise CompatibilityError(
            "authority_baseline_not_exact_commit",
            f"Expected full commit {commit}, resolved {resolved}",
        )
    return resolved


def list_snapshot_paths(repo: Path, commit: str) -> list[tuple[str, str]]:
    result = run_git(repo, "ls-tree", "-r", "-z", commit)
    rows: list[tuple[str, str]] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        metadata, raw_path = raw.split(b"\t", 1)
        fields = metadata.decode("ascii").split()
        if len(fields) != 3 or fields[1] != "blob":
            continue
        path = raw_path.decode("utf-8", "surrogateescape")
        rows.append((path, fields[2]))
    return rows


def read_snapshot_blob(repo: Path, commit: str, path: str, blob_sha: str) -> SnapshotFile:
    result = run_git(repo, "cat-file", "blob", blob_sha)
    return SnapshotFile(path=path, blob_sha=blob_sha, data=result.stdout)


def is_text_candidate(path: str, data: bytes) -> bool:
    if Path(path).suffix.lower() not in TEXT_SUFFIXES:
        return False
    return b"\0" not in data[:8192]


def contains_target(text: str) -> bool:
    lower = text.lower()
    return any(token.lower() in lower for token in TARGET_TOKENS)


def historical_path(path: str) -> bool:
    marker_path = f"/{path.lower().replace(chr(92), '/')}/"
    return any(marker in marker_path for marker in HISTORICAL_MARKERS)


def test_path(path: str) -> bool:
    lower = path.lower()
    name = Path(lower).name
    return "/tests/" in f"/{lower}" or name.startswith("test_")


def source_location(line: int, column: int | None = None) -> str:
    return f"{line}:{column + 1}" if column is not None else str(line)


def line_at(text: str, line: int) -> str:
    lines = text.splitlines()
    return lines[line - 1].strip() if 0 < line <= len(lines) else ""


def invocation_kind_from_line(path: str, line: str) -> str:
    lower = line.lower()
    suffix = Path(path).suffix.lower()
    if "package_iris.ps1" in lower:
        if suffix == ".ps1":
            return "powershell_invocation"
        if '"command"' in lower or "'command'" in lower:
            return "command_manifest"
        if any(token in lower for token in ("powershell ", ".\\iris\\tools\\", "./iris/tools/")):
            return "operator_command"
        return "package_path_reference"
    if "export_lua_bridge" in line:
        return "export_function_reference"
    if "export_dvf_3_3_lua_bridge" in lower:
        if any(token in lower for token in ("python ", "uv run", "subprocess")):
            return "exporter_cli"
        return "exporter_module_reference"
    return "token_reference"


def classify_route(path: str, kind: str, line: str) -> str:
    normalized = path.replace("\\", "/")
    lower = normalized.lower()
    suffix = Path(lower).suffix
    if historical_path(normalized):
        return "historical_non_executable"
    if normalized in PRODUCTION_INTEGRATION_PATHS:
        return "static_reference"
    if test_path(normalized):
        return "test_current"
    if kind in {
        "python_direct_import",
        "python_direct_call",
        "python_subprocess_invocation",
        "powershell_invocation",
    }:
        return "executable_current"
    if suffix == ".py":
        return "diagnostic"
    if suffix == ".ps1":
        return "static_reference"
    if suffix == ".md":
        commandish = any(
            token in line.lower()
            for token in ("powershell ", "uv run ", "python ", ".\\iris\\", "./iris/")
        )
        return "operator_current" if commandish else "static_reference"
    if suffix in {".json", ".jsonl", ".yaml", ".yml", ".toml"}:
        if kind == "command_manifest":
            return "operator_current"
        return "static_reference"
    if suffix in {".cmd", ".sh"}:
        return "executable_current"
    if suffix in {".lua", ".txt", ".cfg"}:
        return "static_reference"
    return "unknown"


def migration_disposition(route: str, kind: str) -> dict[str, Any]:
    if route in {"historical_non_executable", "static_reference", "diagnostic"}:
        return {
            "migration_required": False,
            "required_invocation": "no executable migration; retain classified reference",
            "policy_resolution": "not_applicable",
            "updated_status": "classified_no_migration",
            "regression_test_id": "not_applicable",
            "unresolved_status": None,
        }
    if kind == "python_direct_call":
        return {
            "migration_required": True,
            "required_invocation": (
                "explicit compatibility invocation contract before adoption, or the "
                "post-adoption canonical default wrapper"
            ),
            "policy_resolution": "option_a_explicit_or_live_manifest_default",
            "updated_status": "planned_explicit_contract_or_default_wrapper",
            "regression_test_id": (
                "RegistryRuntimeCompatibilityBridgeTest."
                "test_direct_call_requires_bound_contract_before_adoption"
            ),
            "unresolved_status": None,
        }
    if route == "test_current":
        return {
            "migration_required": False,
            "required_invocation": (
                "retain test reference; executable calls are covered by their own AST rows"
            ),
            "policy_resolution": "option_a_row_level_call_binding",
            "updated_status": "covered_by_ast_call_disposition",
            "regression_test_id": (
                "RegistryRuntimeCompatibilityContractTest."
                "test_caller_inventory_has_no_unknown_or_unmigrated_rows"
            ),
            "unresolved_status": None,
        }
    return {
        "migration_required": False,
        "required_invocation": (
            "complete omission resolves only through the exact live required-validation "
            "manifest after adoption; partial overrides remain forbidden"
        ),
        "policy_resolution": "option_a_live_manifest_selected_bundle",
        "updated_status": "covered_by_post_adoption_default_route",
        "regression_test_id": (
            "RegistryRuntimeCompatibilityCurrentRouteTest."
            "test_default_route_resolves_only_after_live_adoption"
        ),
        "unresolved_status": None,
    }


def ast_rows(path: str, text: str) -> list[tuple[int, int, str, str]]:
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError:
        return []
    rows: list[tuple[int, int, str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = {alias.name for alias in node.names}
            if "export_dvf_3_3_lua_bridge" in module or "export_lua_bridge" in names:
                rows.append(
                    (
                        node.lineno,
                        node.col_offset,
                        "python_direct_import",
                        line_at(text, node.lineno),
                    )
                )
        elif isinstance(node, ast.Import):
            if any("export_dvf_3_3_lua_bridge" in alias.name for alias in node.names):
                rows.append(
                    (
                        node.lineno,
                        node.col_offset,
                        "python_direct_import",
                        line_at(text, node.lineno),
                    )
                )
        elif isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name == "export_lua_bridge":
                rows.append(
                    (
                        node.lineno,
                        node.col_offset,
                        "python_direct_call",
                        line_at(text, node.lineno),
                    )
                )
                continue
            constants = [
                child.value
                for child in ast.walk(node)
                if isinstance(child, ast.Constant) and isinstance(child.value, str)
            ]
            if any(contains_target(value) for value in constants):
                invocation_functions = {
                    "run",
                    "call",
                    "check_call",
                    "check_output",
                    "Popen",
                    "system",
                }
                if func_name in invocation_functions:
                    rows.append(
                        (
                            node.lineno,
                            node.col_offset,
                            "python_subprocess_invocation",
                            line_at(text, node.lineno),
                        )
                    )
    return rows


def make_inventory_row(
    *,
    snapshot: SnapshotFile,
    line_number: int,
    column: int | None,
    kind: str,
    invocation: str,
    command_origin: str,
) -> dict[str, Any]:
    route = classify_route(snapshot.path, kind, invocation)
    disposition = migration_disposition(route, kind)
    seed = canonical_json_bytes(
        {
            "caller_path": snapshot.path,
            "line": line_number,
            "column": column,
            "invocation_kind": kind,
            "current_invocation": invocation,
        }
    )
    return {
        "inventory_row_id": f"caller-{sha256_bytes(seed)[:20]}",
        "caller_path": snapshot.path,
        "caller_sha256": sha256_bytes(snapshot.data),
        "caller_blob_sha1": snapshot.blob_sha,
        "source_location": source_location(line_number, column),
        "command_origin": command_origin,
        "invocation_kind": kind,
        "route_class": route,
        "current_invocation": invocation,
        **disposition,
    }


def scan_snapshot(repo: Path, commit: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    snapshot_paths = list_snapshot_paths(repo, commit)
    blob_by_path = dict(snapshot_paths)
    scanned_text_count = sum(
        Path(path).suffix.lower() in TEXT_SUFFIXES for path, _ in snapshot_paths
    )
    grep = run_git(
        repo,
        "grep",
        "-l",
        "-I",
        "-E",
        "(export_dvf_3_3_lua_bridge|export_lua_bridge|package_iris\\.ps1)",
        commit,
        "--",
        ".",
        check=False,
        text=True,
    )
    if grep.returncode not in {0, 1}:
        raise CompatibilityError(
            "caller_census_git_grep_failed",
            f"git grep failed ({grep.returncode}): {grep.stderr}",
        )
    prefix = f"{commit}:"
    matched_paths = sorted(
        line[len(prefix) :] if line.startswith(prefix) else line
        for line in grep.stdout.splitlines()
        if line
    )
    matched_file_count = 0
    parse_failure_paths: list[str] = []
    for path in matched_paths:
        blob_sha = blob_by_path.get(path)
        if blob_sha is None:
            raise CompatibilityError(
                "caller_census_blob_missing",
                f"Matched path is absent from baseline tree: {path}",
            )
        suffix = Path(path).suffix.lower()
        if suffix not in TEXT_SUFFIXES:
            continue
        snapshot = read_snapshot_blob(repo, commit, path, blob_sha)
        if not is_text_candidate(path, snapshot.data):
            continue
        try:
            text = snapshot.data.decode("utf-8")
        except UnicodeDecodeError:
            parse_failure_paths.append(path)
            continue
        if not contains_target(text):
            continue
        matched_file_count += 1
        seen: set[tuple[int, int | None, str]] = set()
        if suffix == ".py":
            for line, column, kind, invocation in ast_rows(path, text):
                key = (line, column, kind)
                seen.add(key)
                rows.append(
                    make_inventory_row(
                        snapshot=snapshot,
                        line_number=line,
                        column=column,
                        kind=kind,
                        invocation=invocation,
                        command_origin="python_ast",
                    )
                )
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not contains_target(line):
                continue
            kind = invocation_kind_from_line(path, line)
            if any(existing_line == line_number for existing_line, _, _ in seen):
                # Keep one AST authority row for imports/calls.  If the line carries a
                # second target token, the complete source line remains in that row.
                continue
            command_origin = (
                "powershell_exact_token"
                if suffix == ".ps1"
                else "repository_exact_token_scan"
            )
            rows.append(
                make_inventory_row(
                    snapshot=snapshot,
                    line_number=line_number,
                    column=None,
                    kind=kind,
                    invocation=line.strip(),
                    command_origin=command_origin,
                )
            )
    rows.sort(
        key=lambda row: (
            row["caller_path"],
            tuple(int(part) for part in row["source_location"].split(":")),
            row["invocation_kind"],
            row["inventory_row_id"],
        )
    )
    duplicate_ids = [
        row_id
        for row_id, count in Counter(row["inventory_row_id"] for row in rows).items()
        if count != 1
    ]
    diagnostics = {
        "tracked_blob_count": len(snapshot_paths),
        "scanned_text_blob_count": scanned_text_count,
        "matched_file_count": matched_file_count,
        "utf8_parse_failure_count": len(parse_failure_paths),
        "utf8_parse_failure_paths": sorted(parse_failure_paths),
        "duplicate_inventory_row_id_count": len(duplicate_ids),
        "duplicate_inventory_row_ids": sorted(duplicate_ids),
    }
    return rows, diagnostics


def migration_matrix(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    dispositions = [
        {
            "inventory_row_id": row["inventory_row_id"],
            "caller_path": row["caller_path"],
            "route_class": row["route_class"],
            "migration_required": row["migration_required"],
            "migration_disposition": row["updated_status"],
            "policy_resolution": row["policy_resolution"],
            "regression_test_id": row["regression_test_id"],
            "unresolved_status": row["unresolved_status"],
        }
        for row in rows
    ]
    ids = [row["inventory_row_id"] for row in rows]
    disposition_ids = [row["inventory_row_id"] for row in dispositions]
    return {
        "schema_version": "rtc-invocation-migration-matrix-v1",
        "round_id": ROUND_ID,
        "inventory_row_count": len(rows),
        "disposition_row_count": len(dispositions),
        "inventory_orphan_count": len(set(ids) - set(disposition_ids)),
        "disposition_orphan_count": len(set(disposition_ids) - set(ids)),
        "duplicate_disposition_count": sum(
            count - 1 for count in Counter(disposition_ids).values() if count > 1
        ),
        "unknown_invocation_count": sum(
            row["route_class"] == "unknown" for row in rows
        ),
        "unmigrated_invocation_count": sum(
            row["unresolved_status"] is not None for row in rows
        ),
        "dispositions": dispositions,
    }


def parse_porcelain_v1_z(raw: bytes) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    parts = raw.split(b"\0")
    index = 0
    while index < len(parts):
        part = parts[index]
        index += 1
        if not part:
            continue
        decoded = part.decode("utf-8", "surrogateescape")
        if len(decoded) < 4:
            continue
        status = decoded[:2]
        path = decoded[3:].replace("\\", "/")
        prior = ""
        if status[0] in {"R", "C"} and index < len(parts):
            prior = parts[index].decode("utf-8", "surrogateescape").replace("\\", "/")
            index += 1
        entries.append({"status": status, "path": path, "prior_path": prior})
    return entries


def compare_original_dirty_docs(
    *,
    execution_repo: Path,
    original_repo: Path,
    baseline_commit: str,
) -> dict[str, Any]:
    status = run_git(original_repo, "status", "--porcelain=v1", "-z")
    dirty = parse_porcelain_v1_z(status.stdout)
    baseline_paths = {path: blob for path, blob in list_snapshot_paths(execution_repo, baseline_commit)}
    rows: list[dict[str, Any]] = []
    for entry in dirty:
        path = entry["path"]
        suffix = Path(path).suffix.lower()
        if suffix not in TEXT_SUFFIXES:
            continue
        live_path = original_repo / Path(path)
        working_bytes = live_path.read_bytes() if live_path.is_file() else b""
        baseline_blob = baseline_paths.get(path)
        baseline_bytes = (
            read_snapshot_blob(execution_repo, baseline_commit, path, baseline_blob).data
            if baseline_blob
            else b""
        )
        working_text = working_bytes.decode("utf-8", "replace")
        baseline_text = baseline_bytes.decode("utf-8", "replace")
        rows.append(
            {
                "path": path,
                "status": entry["status"],
                "baseline_present": baseline_blob is not None,
                "baseline_sha256": sha256_bytes(baseline_bytes),
                "original_worktree_sha256": sha256_bytes(working_bytes),
                "baseline_target_token_line_count": sum(
                    contains_target(line) for line in baseline_text.splitlines()
                ),
                "original_target_token_line_count": sum(
                    contains_target(line) for line in working_text.splitlines()
                ),
                "authority_consumption": "preservation_only_not_consumed",
            }
        )
    rows.sort(key=lambda row: row["path"])
    return {
        "schema_version": "rtc-original-dirty-doc-invocation-comparison-v1",
        "round_id": ROUND_ID,
        "baseline_commit": baseline_commit,
        "original_worktree_path": str(original_repo.resolve()),
        "dirty_text_path_count": len(rows),
        "dirty_original_docs_consumed_as_authority_count": 0,
        "top_doc_application_mode": "owner_application_pending",
        "rows": rows,
    }


def preintegration_scope(repo: Path) -> dict[str, Any]:
    status = parse_porcelain_v1_z(
        run_git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
    )
    violations: list[dict[str, str]] = []
    allowed: list[dict[str, str]] = []
    for row in status:
        path = row["path"]
        is_allowed = (
            path in PREINTEGRATION_NEW_PATHS
            or path in PREINTEGRATION_GOVERNANCE_PATHS
            or any(path.startswith(prefix) for prefix in PREINTEGRATION_NEW_PREFIXES)
        )
        if is_allowed:
            allowed.append(row)
        else:
            violations.append(row)
    existing_new_paths = sorted(
        path for path in PREINTEGRATION_NEW_PATHS if (repo / Path(path)).exists()
    )
    ignored_new_paths = git_ignored(repo, existing_new_paths)
    for path in ignored_new_paths:
        violations.append({"status": "!!", "path": path, "prior_path": ""})
    production_mutations = sorted(
        row["path"] for row in status if row["path"] in PRODUCTION_INTEGRATION_PATHS
    )
    for path in production_mutations:
        violations.append({"status": "production", "path": path, "prior_path": ""})
    return {
        "preintegration_changed_path_count": len(status),
        "preintegration_allowed_new_path_count": len(allowed),
        "preintegration_tool_scope_violation_count": len(violations),
        "preintegration_existing_new_path_count": len(existing_new_paths),
        "preintegration_ignored_new_path_count": len(ignored_new_paths),
        "preintegration_ignored_new_paths": ignored_new_paths,
        "preintegration_production_mutation_count": len(production_mutations),
        "preintegration_production_mutation_paths": production_mutations,
        "allowed_rows": allowed,
        "violation_rows": violations,
    }


def git_ignored(repo: Path, paths: Iterable[str]) -> list[str]:
    path_list = sorted(set(paths))
    if not path_list:
        return []
    # Per-path calls keep the result portable and deterministic without relying
    # on shell or ambient stdin behavior.
    ignored: list[str] = []
    for path in path_list:
        outcome = run_git(repo, "check-ignore", "-q", "--", path, check=False)
        if outcome.returncode == 0:
            ignored.append(path)
    return ignored


def command_census(args: argparse.Namespace) -> int:
    repo = Path(args.repo_root).resolve()
    original_repo = Path(args.original_worktree).resolve()
    out_dir = Path(args.out_dir).resolve()
    baseline = ensure_commit(repo, args.authority_baseline)
    rows, diagnostics = scan_snapshot(repo, baseline)
    matrix = migration_matrix(rows)
    dirty_comparison = compare_original_dirty_docs(
        execution_repo=repo,
        original_repo=original_repo,
        baseline_commit=baseline,
    )
    route_counts = Counter(row["route_class"] for row in rows)
    ignored_paths = git_ignored(repo, (row["caller_path"] for row in rows))
    inventory = {
        "schema_version": "rtc-exporter-package-invocation-inventory-v1",
        "round_id": ROUND_ID,
        "invocation_inventory_authority_baseline": "owner_approved_clean_baseline",
        "authority_baseline_commit": baseline,
        "scan_denominator": (
            "all tracked UTF-8 text blobs at the exact owner-approved baseline; "
            "historical/generated evidence remains classified in the denominator"
        ),
        "target_tokens": list(TARGET_TOKENS),
        "route_class_enum": sorted(ROUTE_CLASSES),
        "inventory_row_count": len(rows),
        "route_class_counts": dict(sorted(route_counts.items())),
        "invocation_inventory_unknown_count": route_counts["unknown"],
        "caller_ignored_path_count": len(ignored_paths),
        "caller_ignored_paths": ignored_paths,
        "diagnostics": diagnostics,
        "rows": rows,
    }
    scope = preintegration_scope(repo)
    implementation_entry = json.loads(
        Path(args.gate_b_report).read_text(encoding="utf-8")
    )
    predicates = {
        "implementation_entry_allowed": bool(
            implementation_entry.get("implementation_entry_allowed")
        ),
        "invocation_inventory_authority_baseline": (
            inventory["invocation_inventory_authority_baseline"]
        ),
        "invocation_inventory_unknown_count": inventory[
            "invocation_inventory_unknown_count"
        ],
        "invocation_migration_plan_unresolved_count": matrix[
            "unmigrated_invocation_count"
        ]
        + matrix["inventory_orphan_count"]
        + matrix["disposition_orphan_count"]
        + matrix["duplicate_disposition_count"],
        "dirty_original_docs_consumed_as_authority_count": dirty_comparison[
            "dirty_original_docs_consumed_as_authority_count"
        ],
        "preintegration_tool_scope_violation_count": scope[
            "preintegration_tool_scope_violation_count"
        ],
    }
    production_allowed = (
        predicates["implementation_entry_allowed"] is True
        and predicates["invocation_inventory_authority_baseline"]
        == "owner_approved_clean_baseline"
        and predicates["invocation_inventory_unknown_count"] == 0
        and predicates["invocation_migration_plan_unresolved_count"] == 0
        and predicates["dirty_original_docs_consumed_as_authority_count"] == 0
        and predicates["preintegration_tool_scope_violation_count"] == 0
    )
    gate = {
        "schema_version": "rtc-production-integration-gate-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "gate": "C",
        "gate_b_report_path": normalized_relative(repo, Path(args.gate_b_report)),
        "gate_b_report_sha256": sha256_file(Path(args.gate_b_report)),
        "predicates": predicates,
        "preintegration_scope": scope,
        "production_integration_allowed": production_allowed,
        "open_blocker_count": 0 if production_allowed else 1,
    }
    write_json(out_dir / "exporter_package_invocation_inventory.json", inventory)
    write_json(out_dir / "invocation_migration_matrix.json", matrix)
    write_json(out_dir / "original_dirty_doc_invocation_comparison.json", dirty_comparison)
    write_json(out_dir / "production_integration_gate_report.json", gate)
    print(json.dumps(gate, ensure_ascii=False, sort_keys=True))
    return 0 if production_allowed else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DVF 3.3 Registry Runtime Compatibility canonical algorithms."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    census = subparsers.add_parser(
        "caller-census",
        help="Build the Gate C exporter/package caller census and migration matrix.",
    )
    census.add_argument("--repo-root", required=True)
    census.add_argument("--original-worktree", required=True)
    census.add_argument("--authority-baseline", required=True)
    census.add_argument("--gate-b-report", required=True)
    census.add_argument("--attempt-id", required=True)
    census.add_argument("--out-dir", required=True)
    census.set_defaults(handler=command_census)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except CompatibilityError as exc:
        print(
            json.dumps(
                {
                    "round_id": ROUND_ID,
                    "status": "BLOCKED",
                    "failure_code": exc.code,
                    "message": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
