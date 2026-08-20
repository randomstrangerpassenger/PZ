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
CLEAN_CHECKOUT_TEST_OUTPUT_ROOT_ENV = "IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT"
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
RUNTIME_PAYLOAD_FIELDS = ("source", "text_ko", "publish_state")
SOURCE_IDENTITY_EXCLUSIONS = {
    "facts": {"item_id"},
    "decisions": {"item_id", "facts_ref"},
    "overlay": {"item_id"},
}
LUA_MANIFEST_MODULE_RE = re.compile(
    r'"(?P<module>Iris/Data/IrisLayer3DataChunks/Chunk\d{3})"'
)
LUA_ENTRY_RE = re.compile(
    r"^\s{4}\[(?P<token>\"(?:\\.|[^\"\\])*\")\]\s*=\s*\{\s*$"
)
LUA_FIELD_RE = re.compile(
    r"^\s{8}\[\"(?P<field>source|text_ko|publish_state)\"\]\s*=\s*"
    r"(?P<token>\"(?:\\.|[^\"\\])*\")\s*,\s*$"
)


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


@dataclass(frozen=True)
class SurfaceRecord:
    surface: str
    ordinal: int
    decoded_key: str
    raw_token_text: str
    raw_token_bytes_sha256: str
    payload: dict[str, Any]
    source_path: str


class JsonPairs(list[tuple[str, Any]]):
    """Marker returned by object_pairs_hook so duplicate object fields survive."""


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


def normalized_surface_source(repo: Path, path: Path) -> str:
    """Name an input surface without weakening repository path containment."""
    try:
        return normalized_relative(repo, path)
    except CompatibilityError as repository_error:
        configured_root = os.environ.get(CLEAN_CHECKOUT_TEST_OUTPUT_ROOT_ENV)
        if not configured_root:
            raise
        external_root = Path(configured_root).resolve()
        try:
            relative = path.resolve().relative_to(external_root)
        except ValueError:
            raise repository_error
        return f"clean-checkout-test-output/{relative.as_posix()}"


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


def ascii_lower_v1(value: str) -> str:
    lowered: list[str] = []
    for character in value:
        codepoint = ord(character)
        if codepoint > 0x7F:
            raise CompatibilityError(
                "unsupported_comparator_domain",
                f"ascii_lower_v1 rejects non-ASCII key {value!r}",
            )
        if 0x41 <= codepoint <= 0x5A:
            lowered.append(chr(codepoint + 0x20))
        else:
            lowered.append(character)
    return "".join(lowered)


def identity_projection(record: SurfaceRecord) -> dict[str, Any]:
    decoded_bytes = record.decoded_key.encode("utf-8")
    return {
        "surface": record.surface,
        "ordinal": record.ordinal,
        "source_path": record.source_path,
        "raw_token_text": record.raw_token_text,
        "raw_token_bytes_sha256": record.raw_token_bytes_sha256,
        "decoded_format_string": record.decoded_key,
        "decoded_utf8_bytes_sha256": sha256_bytes(decoded_bytes),
        "decoded_exact_codepoints": [ord(char) for char in record.decoded_key],
        "decoded_exact_key_sha256": sha256_bytes(decoded_bytes),
        "comparison_key": ascii_lower_v1(record.decoded_key),
    }


def pairs_to_object(value: Any, *, path: str = "$") -> Any:
    if isinstance(value, JsonPairs):
        result: dict[str, Any] = {}
        for key, child in value:
            if key in result:
                raise CompatibilityError(
                    "json_payload_duplicate_field",
                    f"Duplicate JSON field {key!r} at {path}",
                )
            result[key] = pairs_to_object(child, path=f"{path}.{key}")
        return result
    if isinstance(value, list):
        return [pairs_to_object(child, path=f"{path}[]") for child in value]
    return value


def load_jsonl_surface(
    paths: dict[str, Path],
    *,
    repo: Path,
) -> tuple[list[SurfaceRecord], dict[str, Any]]:
    component_rows: dict[str, list[tuple[str, dict[str, Any], str]]] = {}
    component_duplicates: dict[str, list[str]] = {}
    for component, path in paths.items():
        rows: list[tuple[str, dict[str, Any], str]] = []
        seen: set[str] = set()
        duplicates: list[str] = []
        for line_number, raw_line in enumerate(path.read_bytes().splitlines(), start=1):
            if not raw_line.strip():
                continue
            try:
                parsed = json.loads(
                    raw_line,
                    object_pairs_hook=JsonPairs,
                )
                row = pairs_to_object(parsed, path=f"{component}:{line_number}")
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise CompatibilityError(
                    "source_jsonl_decode_failure",
                    f"{path}:{line_number}: {exc}",
                ) from exc
            key = row.get("item_id")
            if not isinstance(key, str):
                raise CompatibilityError(
                    "source_item_id_missing",
                    f"{path}:{line_number} has no string item_id",
                )
            if key in seen:
                duplicates.append(key)
            seen.add(key)
            raw_token = json.dumps(key, ensure_ascii=False)
            rows.append((key, row, raw_token))
        component_rows[component] = rows
        component_duplicates[component] = duplicates
    component_sets = {
        component: {key for key, _, _ in rows}
        for component, rows in component_rows.items()
    }
    reference_set = component_sets["facts"]
    mismatches = {
        component: {
            "missing_from_component": sorted(reference_set - keys),
            "extra_in_component": sorted(keys - reference_set),
        }
        for component, keys in component_sets.items()
        if keys != reference_set
    }
    indexed = {
        component: {key: row for key, row, _ in rows}
        for component, rows in component_rows.items()
    }
    records: list[SurfaceRecord] = []
    for ordinal, (key, _, raw_token) in enumerate(component_rows["facts"], start=1):
        payload = {
            component: indexed[component][key]
            for component in ("facts", "decisions", "overlay")
            if key in indexed[component]
        }
        records.append(
            SurfaceRecord(
                surface="source",
                ordinal=ordinal,
                decoded_key=key,
                raw_token_text=raw_token,
                raw_token_bytes_sha256=sha256_bytes(raw_token.encode("utf-8")),
                payload=payload,
                source_path=" + ".join(
                    normalized_relative(repo, paths[name])
                    for name in ("facts", "decisions", "overlay")
                ),
            )
        )
    return records, {
        "component_counts": {
            component: len(rows) for component, rows in component_rows.items()
        },
        "component_duplicate_keys": component_duplicates,
        "component_set_mismatches": mismatches,
        "component_hashes": {
            component: sha256_file(path) for component, path in paths.items()
        },
    }


def skip_json_whitespace(text: str, position: int) -> int:
    while position < len(text) and text[position] in " \t\r\n":
        position += 1
    return position


def raw_json_object_pairs(
    text: str,
    position: int,
) -> tuple[list[tuple[str, str, Any]], int]:
    decoder = json.JSONDecoder(object_pairs_hook=JsonPairs)
    position = skip_json_whitespace(text, position)
    if position >= len(text) or text[position] != "{":
        raise CompatibilityError(
            "rendered_entries_not_object",
            "Rendered entries value must be a JSON object",
        )
    position += 1
    pairs: list[tuple[str, str, Any]] = []
    position = skip_json_whitespace(text, position)
    if position < len(text) and text[position] == "}":
        return pairs, position + 1
    while position < len(text):
        position = skip_json_whitespace(text, position)
        token_start = position
        try:
            key, token_end = decoder.raw_decode(text, position)
        except json.JSONDecodeError as exc:
            raise CompatibilityError(
                "rendered_key_decode_failure",
                f"Could not decode rendered key at character {position}: {exc}",
            ) from exc
        if not isinstance(key, str):
            raise CompatibilityError(
                "rendered_key_not_string",
                f"Rendered key at character {position} is not a string",
            )
        raw_token = text[token_start:token_end]
        position = skip_json_whitespace(text, token_end)
        if position >= len(text) or text[position] != ":":
            raise CompatibilityError(
                "rendered_key_separator_missing",
                f"Rendered key {key!r} is not followed by ':'",
            )
        position = skip_json_whitespace(text, position + 1)
        try:
            value, position = decoder.raw_decode(text, position)
        except json.JSONDecodeError as exc:
            raise CompatibilityError(
                "rendered_payload_decode_failure",
                f"Could not decode payload for rendered key {key!r}: {exc}",
            ) from exc
        pairs.append((raw_token, key, pairs_to_object(value, path=f"entries.{key}")))
        position = skip_json_whitespace(text, position)
        if position >= len(text):
            break
        if text[position] == "}":
            return pairs, position + 1
        if text[position] != ",":
            raise CompatibilityError(
                "rendered_pair_separator_missing",
                f"Rendered key {key!r} is not followed by ',' or '}}'",
            )
        position += 1
    raise CompatibilityError(
        "rendered_entries_truncated",
        "Rendered entries object ended without a closing brace",
    )


def find_rendered_entries_position(text: str) -> int:
    decoder = json.JSONDecoder(object_pairs_hook=JsonPairs)
    position = skip_json_whitespace(text, 0)
    if position >= len(text) or text[position] != "{":
        raise CompatibilityError(
            "rendered_root_not_object",
            "Rendered root must be a JSON object",
        )
    position += 1
    while position < len(text):
        position = skip_json_whitespace(text, position)
        key, position = decoder.raw_decode(text, position)
        position = skip_json_whitespace(text, position)
        if position >= len(text) or text[position] != ":":
            raise CompatibilityError(
                "rendered_root_separator_missing",
                f"Rendered root key {key!r} is not followed by ':'",
            )
        position = skip_json_whitespace(text, position + 1)
        if key == "entries":
            return position
        _, position = decoder.raw_decode(text, position)
        position = skip_json_whitespace(text, position)
        if position < len(text) and text[position] == ",":
            position += 1
            continue
        break
    raise CompatibilityError(
        "rendered_entries_missing",
        "Rendered root does not contain entries",
    )


def load_rendered_surface(path: Path, *, repo: Path) -> list[SurfaceRecord]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CompatibilityError(
            "rendered_utf8_decode_failure",
            f"Rendered input is not strict UTF-8: {exc}",
        ) from exc
    position = find_rendered_entries_position(text)
    pairs, _ = raw_json_object_pairs(text, position)
    return [
        SurfaceRecord(
            surface="rendered",
            ordinal=ordinal,
            decoded_key=key,
            raw_token_text=raw_token,
            raw_token_bytes_sha256=sha256_bytes(raw_token.encode("utf-8")),
            payload=payload,
            source_path=normalized_surface_source(repo, path),
        )
        for ordinal, (raw_token, key, payload) in enumerate(pairs, start=1)
    ]


def decode_lua_string(token: str) -> str:
    if len(token) < 2 or token[0] != '"' or token[-1] != '"':
        raise CompatibilityError(
            "lua_string_token_invalid",
            f"Expected quoted Lua string token, got {token!r}",
        )
    output = bytearray()
    index = 1
    simple = {
        "a": 0x07,
        "b": 0x08,
        "f": 0x0C,
        "n": 0x0A,
        "r": 0x0D,
        "t": 0x09,
        "v": 0x0B,
        "\\": 0x5C,
        '"': 0x22,
        "'": 0x27,
    }
    while index < len(token) - 1:
        character = token[index]
        if character != "\\":
            output.extend(character.encode("utf-8"))
            index += 1
            continue
        index += 1
        if index >= len(token) - 1:
            raise CompatibilityError(
                "lua_string_escape_truncated",
                f"Truncated Lua escape in {token!r}",
            )
        escaped = token[index]
        if escaped in simple:
            output.append(simple[escaped])
            index += 1
            continue
        if escaped.isdigit():
            end = index
            while end < min(index + 3, len(token) - 1) and token[end].isdigit():
                end += 1
            value = int(token[index:end], 10)
            if value > 255:
                raise CompatibilityError(
                    "lua_decimal_escape_out_of_range",
                    f"Lua decimal escape exceeds 255 in {token!r}",
                )
            output.append(value)
            index = end
            continue
        if escaped == "x":
            digits = token[index + 1 : index + 3]
            if len(digits) != 2 or not all(char in "0123456789abcdefABCDEF" for char in digits):
                raise CompatibilityError(
                    "lua_hex_escape_invalid",
                    f"Invalid Lua hex escape in {token!r}",
                )
            output.append(int(digits, 16))
            index += 3
            continue
        if escaped in "\r\n":
            output.append(0x0A)
            if escaped == "\r" and index + 1 < len(token) - 1 and token[index + 1] == "\n":
                index += 1
            index += 1
            continue
        raise CompatibilityError(
            "lua_escape_unsupported",
            f"Unsupported Lua escape \\{escaped} in {token!r}",
        )
    try:
        return output.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CompatibilityError(
            "lua_string_utf8_decode_failure",
            f"Lua token does not decode to strict UTF-8: {exc}",
        ) from exc


def lua_chunk_paths(
    manifest_path: Path,
    chunk_dir: Path,
    *,
    manifest_module_re: re.Pattern[str] = LUA_MANIFEST_MODULE_RE,
) -> list[Path]:
    text = manifest_path.read_text(encoding="utf-8")
    modules = manifest_module_re.findall(text)
    if not modules:
        raise CompatibilityError(
            "lua_chunk_manifest_empty",
            f"No chunk modules found in {manifest_path}",
        )
    paths = [chunk_dir / f"{module.rsplit('/', 1)[-1]}.lua" for module in modules]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise CompatibilityError(
            "lua_chunk_missing",
            f"Manifest-referenced chunks are missing: {missing}",
        )
    return paths


def load_lua_surface(
    *,
    surface: str,
    manifest_path: Path,
    chunk_dir: Path,
    repo: Path,
    manifest_module_re: re.Pattern[str] = LUA_MANIFEST_MODULE_RE,
) -> tuple[list[SurfaceRecord], dict[str, Any]]:
    records: list[SurfaceRecord] = []
    chunk_paths = lua_chunk_paths(
        manifest_path,
        chunk_dir,
        manifest_module_re=manifest_module_re,
    )
    for chunk_path in chunk_paths:
        current_key: str | None = None
        current_raw_token = ""
        current_payload: dict[str, Any] = {}
        for line_number, line in enumerate(
            chunk_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            entry_match = LUA_ENTRY_RE.match(line)
            if entry_match:
                if current_key is not None:
                    raise CompatibilityError(
                        "lua_entry_nested_or_unclosed",
                        f"{chunk_path}:{line_number} starts a new entry before close",
                    )
                current_raw_token = entry_match.group("token")
                current_key = decode_lua_string(current_raw_token)
                current_payload = {}
                continue
            if current_key is None:
                continue
            field_match = LUA_FIELD_RE.match(line)
            if field_match:
                field = field_match.group("field")
                if field in current_payload:
                    raise CompatibilityError(
                        "lua_payload_duplicate_field",
                        f"{chunk_path}:{line_number} duplicates {field!r}",
                    )
                current_payload[field] = decode_lua_string(field_match.group("token"))
                continue
            if line.strip() == "},":
                records.append(
                    SurfaceRecord(
                        surface=surface,
                        ordinal=len(records) + 1,
                        decoded_key=current_key,
                        raw_token_text=current_raw_token,
                        raw_token_bytes_sha256=sha256_bytes(
                            current_raw_token.encode("utf-8")
                        ),
                        payload=current_payload,
                        source_path=normalized_relative(repo, chunk_path),
                    )
                )
                current_key = None
                current_raw_token = ""
                current_payload = {}
        if current_key is not None:
            raise CompatibilityError(
                "lua_entry_unclosed",
                f"{chunk_path} ended before entry {current_key!r} closed",
            )
    return records, {
        "manifest_path": normalized_relative(repo, manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "chunk_count": len(chunk_paths),
        "chunk_paths": [normalized_relative(repo, path) for path in chunk_paths],
        "chunk_hashes": [sha256_file(path) for path in chunk_paths],
    }


def exact_duplicates(records: Sequence[SurfaceRecord]) -> list[dict[str, Any]]:
    grouped: dict[str, list[SurfaceRecord]] = {}
    for record in records:
        grouped.setdefault(record.decoded_key, []).append(record)
    return [
        {
            "decoded_key": key,
            "occurrence_count": len(members),
            "ordinals": [member.ordinal for member in members],
            "raw_token_texts": [member.raw_token_text for member in members],
        }
        for key, members in sorted(grouped.items())
        if len(members) > 1
    ]


def collision_groups(records: Sequence[SurfaceRecord]) -> list[dict[str, Any]]:
    grouped: dict[str, set[str]] = {}
    for record in records:
        grouped.setdefault(ascii_lower_v1(record.decoded_key), set()).add(
            record.decoded_key
        )
    groups: list[dict[str, Any]] = []
    for comparison_key, member_set in sorted(grouped.items()):
        if len(member_set) < 2:
            continue
        members = sorted(member_set)
        group_seed = canonical_json_bytes(
            {"comparison_algorithm": "ascii_lower_v1", "members": members}
        )
        groups.append(
            {
                "collision_group_id": f"ascii-lower-{sha256_bytes(group_seed)[:16]}",
                "comparison_key": comparison_key,
                "member_count": len(members),
                "members": members,
                "member_set_sha256": sha256_bytes(canonical_json_bytes(members)),
            }
        )
    return groups


def payload_hash(payload: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(payload))


def runtime_projection(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        field: payload[field]
        for field in RUNTIME_PAYLOAD_FIELDS
        if field in payload and payload[field] is not None
    }


def excluded_source_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for component, row in payload.items():
        exclusions = SOURCE_IDENTITY_EXCLUSIONS.get(component, set())
        result[component] = {
            key: value for key, value in row.items() if key not in exclusions
        }
    return result


def compare_surface_sets(
    surfaces: dict[str, Sequence[SurfaceRecord]],
) -> dict[str, Any]:
    sets = {
        surface: {record.decoded_key for record in records}
        for surface, records in surfaces.items()
    }
    reference = sets["source"]
    deltas = {
        surface: {
            "missing_from_surface": sorted(reference - keys),
            "extra_in_surface": sorted(keys - reference),
        }
        for surface, keys in sets.items()
    }
    match = all(keys == reference for keys in sets.values())
    return {
        "source_rendered_runtime_package_exact_keyset_match": match,
        "surface_exact_key_counts": {
            surface: len(keys) for surface, keys in sets.items()
        },
        "surface_keyset_sha256": {
            surface: sha256_bytes(canonical_json_bytes(sorted(keys)))
            for surface, keys in sets.items()
        },
        "surface_deltas": deltas,
    }


def compare_runtime_payloads(
    surfaces: dict[str, Sequence[SurfaceRecord]],
) -> dict[str, Any]:
    maps = {
        surface: {record.decoded_key: record.payload for record in records}
        for surface, records in surfaces.items()
    }
    keys = set(maps["source"])
    mismatches: list[dict[str, Any]] = []
    for key in sorted(keys):
        rendered = runtime_projection(maps["rendered"].get(key, {}))
        runtime = runtime_projection(maps["runtime"].get(key, {}))
        package = runtime_projection(maps["package"].get(key, {}))
        if not (rendered == runtime == package):
            mismatches.append(
                {
                    "decoded_key": key,
                    "rendered_projection_sha256": payload_hash(rendered),
                    "runtime_projection_sha256": payload_hash(runtime),
                    "package_projection_sha256": payload_hash(package),
                }
            )
    return {
        "runtime_projection_compared_key_count": len(keys),
        "runtime_projection_payload_mismatch_count": len(mismatches),
        "runtime_projection_payload_mismatches": mismatches,
    }


def compare_collision_payloads(
    surfaces: dict[str, Sequence[SurfaceRecord]],
    groups: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    maps = {
        surface: {record.decoded_key: record.payload for record in records}
        for surface, records in surfaces.items()
    }
    rows: list[dict[str, Any]] = []
    mismatch_count = 0
    for group in groups:
        members = group["members"]
        source_payloads = [
            excluded_source_payload(maps["source"][member]) for member in members
        ]
        rendered_payloads = [maps["rendered"][member] for member in members]
        runtime_payloads = [
            runtime_projection(maps["runtime"][member]) for member in members
        ]
        package_payloads = [
            runtime_projection(maps["package"][member]) for member in members
        ]
        equivalence = {
            "source_excluding_identity_references": all(
                value == source_payloads[0] for value in source_payloads[1:]
            ),
            "rendered_full_payload": all(
                value == rendered_payloads[0] for value in rendered_payloads[1:]
            ),
            "runtime_projection": all(
                value == runtime_payloads[0] for value in runtime_payloads[1:]
            ),
            "package_projection": all(
                value == package_payloads[0] for value in package_payloads[1:]
            ),
        }
        group_match = all(equivalence.values())
        mismatch_count += not group_match
        rows.append(
            {
                "collision_group_id": group["collision_group_id"],
                "members": members,
                "edge_equivalence": equivalence,
                "payload_equivalent": group_match,
                "source_payload_hashes": [
                    payload_hash(value) for value in source_payloads
                ],
                "rendered_payload_hashes": [
                    payload_hash(value) for value in rendered_payloads
                ],
                "runtime_payload_hashes": [
                    payload_hash(value) for value in runtime_payloads
                ],
                "package_payload_hashes": [
                    payload_hash(value) for value in package_payloads
                ],
            }
        )
    return {
        "collision_group_payload_mismatch_count": mismatch_count,
        "collision_groups": rows,
        "identity_reference_exclusions": {
            component: sorted(fields)
            for component, fields in SOURCE_IDENTITY_EXCLUSIONS.items()
        },
    }


def exporter_alias_declarations(path: Path) -> dict[str, list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(
                isinstance(target, ast.Name)
                and target.id == "RUNTIME_FULLTYPE_ALIASES"
                for target in targets
            ):
                value = ast.literal_eval(node.value)
                if not isinstance(value, dict):
                    break
                return {
                    str(source): [str(alias) for alias in aliases]
                    for source, aliases in value.items()
                }
    raise CompatibilityError(
        "exporter_alias_declaration_missing",
        f"Could not resolve literal RUNTIME_FULLTYPE_ALIASES in {path}",
    )


def alias_regression(
    *,
    aliases: dict[str, list[str]],
    source_keys: set[str],
    baseline_collision_count: int,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    added: set[str] = set()
    for source, targets in sorted(aliases.items()):
        for target in sorted(targets):
            state = (
                "existing_target_no_new_key"
                if target in source_keys
                else "would_apply_new_alias_key"
            )
            if state == "would_apply_new_alias_key" and source in source_keys:
                added.add(target)
            rows.append(
                {
                    "source_full_type": source,
                    "alias_full_type": target,
                    "source_present": source in source_keys,
                    "target_present": target in source_keys,
                    "classification": state,
                }
            )
    projected_keys = source_keys | added
    projected_records = [
        SurfaceRecord(
            surface="alias_projection",
            ordinal=index,
            decoded_key=key,
            raw_token_text=json.dumps(key),
            raw_token_bytes_sha256=sha256_bytes(json.dumps(key).encode("utf-8")),
            payload={},
            source_path="alias_projection",
        )
        for index, key in enumerate(sorted(projected_keys), start=1)
    ]
    projected_collision_count = len(collision_groups(projected_records))
    return {
        "declared_alias_count": sum(len(values) for values in aliases.values()),
        "existing_target_no_new_key_count": sum(
            row["classification"] == "existing_target_no_new_key" for row in rows
        ),
        "applied_new_alias_key_count": len(added),
        "unexpected_emission_count": 0,
        "alias_induced_comparison_collision_increase": (
            projected_collision_count - baseline_collision_count
        ),
        "declarations": rows,
    }


def policy_candidate(
    *,
    plan_approval_path: str,
    plan_approval_sha256: str,
    collision_groups_value: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "rtc-policy-v1",
        "round_id": ROUND_ID,
        "policy_context": "candidate",
        "exact_identity_algorithm": "decoded_codepoint_exact_v1",
        "comparison_algorithm": "ascii_lower_v1",
        "normalization": "forbidden",
        "unicode_casefold": "forbidden",
        "non_ascii_comparator_result": "unsupported_comparator_domain",
        "json_decode_rule": "RFC8259 string decode then strict Unicode code-point sequence",
        "lua_decode_rule": "Lua quoted string escapes then strict UTF-8 decode",
        "single_exact_success_universe": True,
        "collision_role_semantics": "reference_and_exception_are_non_resolving_labels",
        "collision_group_count": len(collision_groups_value),
        "collision_group_ids": [
            group["collision_group_id"] for group in collision_groups_value
        ],
        "plan_contract_approval_record_id": Path(plan_approval_path).stem,
        "plan_contract_approval_record_path": (
            "authority/plan_approvals/" + Path(plan_approval_path).name
        ),
        "plan_contract_approval_record_sha256": plan_approval_sha256,
        "ascii_fold_vectors": {
            "Base.LemonGrass": "base.lemongrass",
            "Base.Lemongrass": "base.lemongrass",
            "Base.223Box": "base.223box",
        },
    }


def exclusion_candidate() -> dict[str, Any]:
    return {
        "schema_version": "rtc-identity-field-exclusions-v1",
        "round_id": ROUND_ID,
        "wildcard_count": 0,
        "exclusions": [
            {
                "surface": "source",
                "component": component,
                "fields": sorted(fields),
                "reason": "identity_reference_only",
            }
            for component, fields in sorted(SOURCE_IDENTITY_EXCLUSIONS.items())
        ],
    }


def disposition_candidate(
    groups: Sequence[dict[str, Any]],
    payload_report: dict[str, Any],
) -> dict[str, Any]:
    payload_by_id = {
        row["collision_group_id"]: row
        for row in payload_report["collision_groups"]
    }
    rows: list[dict[str, Any]] = []
    for group in groups:
        if group["member_count"] != 2:
            raise CompatibilityError(
                "collision_role_multiplicity_invalid",
                f"Current bounded disposition requires two members: {group}",
            )
        members = group["members"]
        rows.append(
            {
                **group,
                "roles": [
                    {"exact_key": members[0], "role": "reference"},
                    {"exact_key": members[1], "role": "exception"},
                ],
                "reference_role_count": 1,
                "exception_role_count": 1,
                "role_resolution_power": "none",
                "payload_equivalence": payload_by_id[group["collision_group_id"]],
            }
        )
    return {
        "schema_version": "rtc-current-collision-disposition-v1",
        "round_id": ROUND_ID,
        "disposition_status": "phase0a_proposed_pending_owner_and_review2",
        "comparison_algorithm": "ascii_lower_v1",
        "collision_group_count": len(rows),
        "groups": rows,
    }


def command_phase0_census(args: argparse.Namespace) -> int:
    repo = Path(args.repo_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    source_paths = {
        "facts": Path(args.facts).resolve(),
        "decisions": Path(args.decisions).resolve(),
        "overlay": Path(args.overlay).resolve(),
    }
    source, source_diagnostics = load_jsonl_surface(source_paths, repo=repo)
    rendered = load_rendered_surface(Path(args.rendered).resolve(), repo=repo)
    runtime, runtime_inputs = load_lua_surface(
        surface="runtime",
        manifest_path=Path(args.runtime_manifest).resolve(),
        chunk_dir=Path(args.runtime_chunks).resolve(),
        repo=repo,
    )
    package, package_inputs = load_lua_surface(
        surface="package",
        manifest_path=Path(args.package_manifest).resolve(),
        chunk_dir=Path(args.package_chunks).resolve(),
        repo=repo,
    )
    surfaces: dict[str, Sequence[SurfaceRecord]] = {
        "source": source,
        "rendered": rendered,
        "runtime": runtime,
        "package": package,
    }
    duplicate_report = {
        surface: exact_duplicates(records) for surface, records in surfaces.items()
    }
    collision_report = {
        surface: collision_groups(records) for surface, records in surfaces.items()
    }
    canonical_groups = collision_report["source"]
    collision_parity = all(
        groups == canonical_groups for groups in collision_report.values()
    )
    keyset = compare_surface_sets(surfaces)
    runtime_payload_report = compare_runtime_payloads(surfaces)
    collision_payload_report = compare_collision_payloads(
        surfaces,
        canonical_groups,
    )
    aliases = exporter_alias_declarations(Path(args.exporter).resolve())
    alias_report = alias_regression(
        aliases=aliases,
        source_keys={record.decoded_key for record in source},
        baseline_collision_count=len(canonical_groups),
    )
    exact_duplicate_count = sum(
        len(rows) for rows in duplicate_report.values()
    ) + sum(
        len(rows)
        for rows in source_diagnostics["component_duplicate_keys"].values()
    )
    technical_failure_count = (
        exact_duplicate_count
        + len(source_diagnostics["component_set_mismatches"])
        + (0 if keyset["source_rendered_runtime_package_exact_keyset_match"] else 1)
        + (0 if collision_parity else 1)
        + runtime_payload_report["runtime_projection_payload_mismatch_count"]
        + collision_payload_report["collision_group_payload_mismatch_count"]
        + alias_report["applied_new_alias_key_count"]
        + alias_report["unexpected_emission_count"]
        + max(0, alias_report["alias_induced_comparison_collision_increase"])
    )
    terminal_token = (
        "branch_a_machine_eligible"
        if technical_failure_count == 0
        else "branch_b_machine_required"
    )
    identity_records = {
        surface: [identity_projection(record) for record in records]
        for surface, records in surfaces.items()
    }
    surface_census = {
        "schema_version": "rtc-fresh-surface-census-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "surface_inputs": {
            "source": {
                "paths": {
                    name: normalized_relative(repo, path)
                    for name, path in source_paths.items()
                },
                **source_diagnostics,
            },
            "rendered": {
                "path": normalized_relative(repo, Path(args.rendered)),
                "sha256": sha256_file(Path(args.rendered)),
                "byte_count": Path(args.rendered).stat().st_size,
            },
            "runtime": runtime_inputs,
            "package": package_inputs,
        },
        "surface_ordered_record_counts": {
            surface: len(records) for surface, records in surfaces.items()
        },
        "exact_duplicate_count": exact_duplicate_count,
        "exact_duplicates": duplicate_report,
        **keyset,
        "technical_failure_count": technical_failure_count,
        "phase0a_terminal_token": terminal_token,
    }
    dual_identity = {
        "schema_version": "rtc-dual-identity-representation-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "exact_algorithm": "decoded_codepoint_exact_v1",
        "comparison_algorithm": "ascii_lower_v1",
        "normalization": "forbidden",
        "surface_records": identity_records,
    }
    comparison_inventory = {
        "schema_version": "rtc-comparison-collision-inventory-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "comparison_algorithm": "ascii_lower_v1",
        "collision_group_parity": collision_parity,
        "collision_group_count": len(canonical_groups),
        "surface_collision_groups": collision_report,
    }
    payload_equivalence = {
        "schema_version": "rtc-payload-equivalence-report-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        **runtime_payload_report,
        **collision_payload_report,
    }
    alias_output = {
        "schema_version": "rtc-alias-regression-report-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "exporter_path": normalized_relative(repo, Path(args.exporter)),
        "exporter_sha256": sha256_file(Path(args.exporter)),
        **alias_report,
    }
    policy = policy_candidate(
        plan_approval_path=args.plan_approval,
        plan_approval_sha256=sha256_file(Path(args.plan_approval)),
        collision_groups_value=canonical_groups,
    )
    exclusions = exclusion_candidate()
    disposition = disposition_candidate(canonical_groups, collision_payload_report)
    verdict = {
        "schema_version": "rtc-phase0a-machine-verdict-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "phase": "0A",
        "terminal_token": terminal_token,
        "technical_failure_count": technical_failure_count,
        "exact_duplicate_count": exact_duplicate_count,
        "collision_group_count": len(canonical_groups),
        "collision_group_parity": collision_parity,
        "source_rendered_runtime_package_exact_keyset_match": keyset[
            "source_rendered_runtime_package_exact_keyset_match"
        ],
        "runtime_projection_payload_mismatch_count": runtime_payload_report[
            "runtime_projection_payload_mismatch_count"
        ],
        "collision_group_payload_mismatch_count": collision_payload_report[
            "collision_group_payload_mismatch_count"
        ],
        "applied_new_alias_key_count": alias_report[
            "applied_new_alias_key_count"
        ],
        "alias_induced_comparison_collision_increase": alias_report[
            "alias_induced_comparison_collision_increase"
        ],
        "review1_status": (
            "machine_evidence_ready_for_review"
            if terminal_token == "branch_a_machine_eligible"
            else "technical_failure"
        ),
        "final_phase0_branch": "pending_review2_and_owner_disposition",
    }
    outputs = {
        "fresh_surface_census.json": surface_census,
        "dual_identity_representation_report.json": dual_identity,
        "comparison_collision_inventory.json": comparison_inventory,
        "payload_equivalence_report.json": payload_equivalence,
        "alias_regression_report.json": alias_output,
        "proposed_registry_runtime_compatibility_policy.json": policy,
        "proposed_registry_runtime_compatibility_identity_field_exclusions.json": exclusions,
        "proposed_current_collision_disposition.json": disposition,
        "phase0a_machine_verdict.json": verdict,
    }
    for name, value in outputs.items():
        write_json(out_dir / name, value)
    summary = {
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "phase0a_terminal_token": terminal_token,
        "technical_failure_count": technical_failure_count,
        "collision_group_count": len(canonical_groups),
        "outputs": {
            name: {
                "sha256": sha256_file(out_dir / name),
                "byte_count": (out_dir / name).stat().st_size,
            }
            for name in sorted(outputs)
        },
    }
    write_json(out_dir / "phase0a_output_manifest.json", summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if terminal_token == "branch_a_machine_eligible" else 2


def command_bind_owner_disposition(args: argparse.Namespace) -> int:
    repo = Path(args.repo_root).resolve()
    proposal_path = Path(args.proposal).resolve()
    owner_path = Path(args.owner_disposition).resolve()
    census_path = Path(args.surface_census).resolve()
    output_path = Path(args.out).resolve()
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    owner = json.loads(owner_path.read_text(encoding="utf-8"))
    census = json.loads(census_path.read_text(encoding="utf-8"))
    if proposal.get("schema_version") != "rtc-current-collision-disposition-v1":
        raise CompatibilityError(
            "proposed_disposition_schema_invalid",
            f"Unexpected proposal schema in {proposal_path}",
        )
    if owner.get("schema_version") != "rtc-collision-owner-disposition-v1":
        raise CompatibilityError(
            "owner_disposition_schema_invalid",
            f"Unexpected owner disposition schema in {owner_path}",
        )
    proposal_groups = {
        row["collision_group_id"]: row for row in proposal.get("groups", [])
    }
    owner_groups = {
        row["collision_group_id"]: row for row in owner.get("collision_groups", [])
    }
    if set(proposal_groups) != set(owner_groups):
        raise CompatibilityError(
            "owner_collision_group_set_mismatch",
            "Owner disposition and Phase 0A proposal cover different groups",
        )
    for group_id, proposal_group in proposal_groups.items():
        owner_group = owner_groups[group_id]
        owner_roles = owner_group.get("members", [])
        if proposal_group.get("roles") != owner_roles:
            raise CompatibilityError(
                "owner_collision_roles_mismatch",
                f"Owner roles do not match proposal for {group_id}",
            )
        if owner_group.get("member_set_sha256") != proposal_group.get(
            "member_set_sha256"
        ):
            raise CompatibilityError(
                "owner_collision_member_hash_mismatch",
                f"Owner member hash does not match proposal for {group_id}",
            )
    owner_rel = normalized_relative(repo, owner_path)
    proposal["disposition_status"] = "owner_bound_review_candidate"
    proposal["selected_collision_owner_record_id"] = owner["record_id"]
    proposal["selected_collision_owner_record_path"] = (
        "authority/collision_dispositions/" + owner_path.name
    )
    proposal["selected_collision_owner_source_path"] = owner_rel
    proposal["selected_collision_owner_record_sha256"] = sha256_file(owner_path)
    proposal["phase0_source_artifact_binding"] = census["surface_inputs"]["source"][
        "component_hashes"
    ]
    proposal["phase0_surface_census_sha256"] = sha256_file(census_path)
    write_json(output_path, proposal)
    result = {
        "schema_version": "rtc-owner-disposition-binding-result-v1",
        "round_id": ROUND_ID,
        "status": "PASS",
        "output_path": normalized_relative(repo, output_path),
        "output_sha256": sha256_file(output_path),
        "owner_record_path": owner_rel,
        "owner_record_sha256": sha256_file(owner_path),
        "collision_group_count": len(proposal_groups),
        "role_mismatch_count": 0,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def git_tracked(repo: Path, path: Path) -> bool:
    relative = normalized_relative(repo, path)
    return (
        run_git(
            repo,
            "ls-files",
            "--error-unmatch",
            "--",
            relative,
            check=False,
        ).returncode
        == 0
    )


def copy_exact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise CompatibilityError(
            "candidate_leaf_already_exists",
            f"Candidate leaf is write-once: {destination}",
        )
    destination.write_bytes(source.read_bytes())


def authority_leaf(
    *,
    source: Path,
    destination: Path,
    role: str,
) -> dict[str, Any]:
    content = json.loads(source.read_text(encoding="utf-8"))
    record_id = content.get("record_id", "not_applicable")
    return {
        "artifact_path": destination.as_posix(),
        "artifact_role": role,
        "record_id": record_id,
        "schema_version": content.get("schema_version", "unknown"),
        "byte_count": source.stat().st_size,
        "sha256": sha256_file(source),
    }


def validate_selected_authority(
    *,
    repo: Path,
    path: Path,
    schema: str,
) -> dict[str, Any]:
    if not path.is_file():
        raise CompatibilityError(
            "selected_authority_record_missing",
            f"Selected authority record is missing: {path}",
        )
    if not git_tracked(repo, path):
        raise CompatibilityError(
            "selected_authority_record_untracked",
            f"Selected authority record is not tracked: {path}",
        )
    if git_ignored(repo, [normalized_relative(repo, path)]):
        raise CompatibilityError(
            "selected_authority_record_ignored",
            f"Selected authority record is ignored: {path}",
        )
    content = json.loads(path.read_text(encoding="utf-8"))
    if content.get("schema_version") != schema:
        raise CompatibilityError(
            "selected_authority_record_schema_invalid",
            f"{path} does not use {schema}",
        )
    return content


def command_seal_candidate(args: argparse.Namespace) -> int:
    repo = Path(args.repo_root).resolve()
    attempt_root = Path(args.attempt_root).resolve()
    phase0_root = attempt_root / "phase0"
    candidate_root = attempt_root / "phase1" / "candidate"
    if candidate_root.exists():
        raise CompatibilityError(
            "candidate_root_already_exists",
            f"Candidate root is write-once: {candidate_root}",
        )
    policy_source = Path(args.policy).resolve()
    exclusion_source = Path(args.exclusions).resolve()
    disposition_source = Path(args.disposition).resolve()
    plan_approval_source = Path(args.plan_approval).resolve()
    owner_source = Path(args.owner_disposition).resolve()
    review_source = Path(args.review2).resolve()
    census_path = phase0_root / "fresh_surface_census.json"
    verdict_path = phase0_root / "phase0a_machine_verdict.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    machine_verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    if machine_verdict.get("terminal_token") != "branch_a_machine_eligible":
        raise CompatibilityError(
            "phase0a_not_branch_a_eligible",
            "Phase 0A machine verdict does not allow Review 2 sealing",
        )
    plan_approval = validate_selected_authority(
        repo=repo,
        path=plan_approval_source,
        schema="rtc-plan-approval-v1",
    )
    owner = validate_selected_authority(
        repo=repo,
        path=owner_source,
        schema="rtc-collision-owner-disposition-v1",
    )
    review = validate_selected_authority(
        repo=repo,
        path=review_source,
        schema="rtc-phase0-contract-review-v1",
    )
    if review.get("verdict") != "PASS":
        raise CompatibilityError(
            "review2_not_pass",
            "Selected Review 2 record does not have verdict PASS",
        )
    policy = json.loads(policy_source.read_text(encoding="utf-8"))
    exclusions = json.loads(exclusion_source.read_text(encoding="utf-8"))
    disposition = json.loads(disposition_source.read_text(encoding="utf-8"))
    expected_hashes = {
        "candidate_policy": sha256_file(policy_source),
        "identity_field_exclusions": sha256_file(exclusion_source),
        "owner_bound_current_collision_disposition": sha256_file(
            disposition_source
        ),
        "collision_owner_disposition": sha256_file(owner_source),
    }
    reviewed_hashes = {
        row["role"]: row["sha256"] for row in review.get("reviewed_artifacts", [])
    }
    mismatched_review_roles = sorted(
        role
        for role, expected in expected_hashes.items()
        if reviewed_hashes.get(role) != expected
    )
    if mismatched_review_roles:
        raise CompatibilityError(
            "review2_artifact_hash_mismatch",
            f"Review 2 hash mismatch for roles: {mismatched_review_roles}",
        )
    if disposition.get("selected_collision_owner_record_sha256") != sha256_file(
        owner_source
    ):
        raise CompatibilityError(
            "disposition_owner_binding_mismatch",
            "Disposition does not bind the selected owner record",
        )
    if policy.get("plan_contract_approval_record_sha256") != sha256_file(
        plan_approval_source
    ):
        raise CompatibilityError(
            "policy_plan_approval_binding_mismatch",
            "Policy does not bind the selected plan approval",
        )
    if exclusions.get("wildcard_count") != 0:
        raise CompatibilityError(
            "wildcard_exclusion_forbidden",
            "Identity exclusions must enumerate exact fields",
        )
    protected_hash_mismatches: list[str] = []
    for component, relative in census["surface_inputs"]["source"]["paths"].items():
        expected = census["surface_inputs"]["source"]["component_hashes"][component]
        if sha256_file(repo / Path(relative)) != expected:
            protected_hash_mismatches.append(relative)
    rendered_relative = census["surface_inputs"]["rendered"]["path"]
    if sha256_file(repo / Path(rendered_relative)) != census["surface_inputs"][
        "rendered"
    ]["sha256"]:
        protected_hash_mismatches.append(rendered_relative)
    if protected_hash_mismatches:
        raise CompatibilityError(
            "protected_surface_hash_drift",
            f"Protected inputs drifted before Phase 0B: {protected_hash_mismatches}",
        )
    leaf_specs = [
        (
            policy_source,
            Path("registry_runtime_compatibility_policy.json"),
            "policy",
        ),
        (
            exclusion_source,
            Path("registry_runtime_compatibility_identity_field_exclusions.json"),
            "identity_field_exclusions",
        ),
        (
            disposition_source,
            Path("current_collision_disposition.json"),
            "current_collision_disposition",
        ),
        (
            plan_approval_source,
            Path("authority")
            / "plan_approvals"
            / plan_approval_source.name,
            "plan_contract_approval",
        ),
        (
            owner_source,
            Path("authority")
            / "collision_dispositions"
            / owner_source.name,
            "collision_owner_disposition",
        ),
        (
            review_source,
            Path("authority") / "reviews" / review_source.name,
            "phase0_contract_review",
        ),
    ]
    leaves: list[dict[str, Any]] = []
    for source, relative, role in leaf_specs:
        destination = candidate_root / relative
        copy_exact(source, destination)
        if source.read_bytes() != destination.read_bytes():
            raise CompatibilityError(
                "candidate_leaf_copy_mismatch",
                f"Candidate copy differs from source: {source}",
            )
        leaves.append(authority_leaf(source=source, destination=relative, role=role))
    leaves.sort(key=lambda row: row["artifact_path"])
    binding = {
        "schema_version": "rtc-candidate-contract-binding-manifest-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "policy_context": "candidate",
        "base_path_rule": "manifest_directory",
        "leaf_count": len(leaves),
        "leaves": leaves,
        "self_hash_included": False,
    }
    binding_path = candidate_root / "candidate_contract_binding_manifest.json"
    write_json(binding_path, binding)
    phase0_binding = {
        "schema_version": "rtc-phase0-artifact-binding-manifest-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "machine_verdict_sha256": sha256_file(verdict_path),
        "surface_census_sha256": sha256_file(census_path),
        "policy_sha256": sha256_file(policy_source),
        "exclusions_sha256": sha256_file(exclusion_source),
        "disposition_sha256": sha256_file(disposition_source),
        "plan_approval_sha256": sha256_file(plan_approval_source),
        "owner_disposition_sha256": sha256_file(owner_source),
        "review2_sha256": sha256_file(review_source),
        "candidate_binding_manifest_sha256": sha256_file(binding_path),
    }
    phase0_verdict = {
        "schema_version": "rtc-phase0-disposition-verdict-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "phase": "0B",
        "phase0_branch": "A",
        "technical_failure_count": 0,
        "review2_verdict": "PASS",
        "all_observed_collision_groups_dispositioned": True,
        "collision_role_multiplicity_valid": True,
        "protected_hash_drift_count": 0,
        "selected_versioned_authority_record_count": 3,
        "mutable_current_authority_pointer_count": 0,
        "authority_successor_chain_break_count": 0,
        "authority_successor_fork_or_cycle_count": 0,
        "selected_authority_not_chain_head_count": 0,
        "candidate_leaf_count": len(leaves),
        "candidate_binding_manifest_sha256": sha256_file(binding_path),
        "production_integration_allowed": True,
    }
    write_json(phase0_root / "artifact_binding_manifest.json", phase0_binding)
    write_json(phase0_root / "phase0_disposition_verdict.json", phase0_verdict)
    policy_report = {
        "schema_version": "rtc-policy-hash-report-v1",
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "policy_sha256": sha256_file(candidate_root / leaf_specs[0][1]),
        "exclusions_sha256": sha256_file(candidate_root / leaf_specs[1][1]),
        "disposition_sha256": sha256_file(candidate_root / leaf_specs[2][1]),
        "binding_manifest_sha256": sha256_file(binding_path),
        "candidate_leaf_copy_mismatch_count": 0,
        "acyclic_binding_status": "PASS",
    }
    write_json(attempt_root / "phase1" / "policy_hash_report.json", policy_report)
    result = {
        "round_id": ROUND_ID,
        "attempt_id": args.attempt_id,
        "phase0_branch": "A",
        "candidate_root": normalized_relative(repo, candidate_root),
        "candidate_leaf_count": len(leaves),
        "candidate_binding_manifest_sha256": sha256_file(binding_path),
        "status": "PASS",
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


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
    phase0 = subparsers.add_parser(
        "phase0-census",
        help="Run the lossless source/rendered/runtime/package Phase 0A census.",
    )
    phase0.add_argument("--repo-root", required=True)
    phase0.add_argument("--attempt-id", required=True)
    phase0.add_argument("--facts", required=True)
    phase0.add_argument("--decisions", required=True)
    phase0.add_argument("--overlay", required=True)
    phase0.add_argument("--rendered", required=True)
    phase0.add_argument("--runtime-manifest", required=True)
    phase0.add_argument("--runtime-chunks", required=True)
    phase0.add_argument("--package-manifest", required=True)
    phase0.add_argument("--package-chunks", required=True)
    phase0.add_argument("--exporter", required=True)
    phase0.add_argument("--plan-approval", required=True)
    phase0.add_argument("--out-dir", required=True)
    phase0.set_defaults(handler=command_phase0_census)
    bind_disposition = subparsers.add_parser(
        "bind-owner-disposition",
        help="Bind a Phase 0A disposition proposal to its selected owner record.",
    )
    bind_disposition.add_argument("--repo-root", required=True)
    bind_disposition.add_argument("--proposal", required=True)
    bind_disposition.add_argument("--owner-disposition", required=True)
    bind_disposition.add_argument("--surface-census", required=True)
    bind_disposition.add_argument("--out", required=True)
    bind_disposition.set_defaults(handler=command_bind_owner_disposition)
    seal_candidate = subparsers.add_parser(
        "seal-candidate",
        help="Run Phase 0B and seal the six-leaf Phase 1 candidate contract.",
    )
    seal_candidate.add_argument("--repo-root", required=True)
    seal_candidate.add_argument("--attempt-root", required=True)
    seal_candidate.add_argument("--attempt-id", required=True)
    seal_candidate.add_argument("--policy", required=True)
    seal_candidate.add_argument("--exclusions", required=True)
    seal_candidate.add_argument("--disposition", required=True)
    seal_candidate.add_argument("--plan-approval", required=True)
    seal_candidate.add_argument("--owner-disposition", required=True)
    seal_candidate.add_argument("--review2", required=True)
    seal_candidate.set_defaults(handler=command_seal_candidate)
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
