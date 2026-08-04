#!/usr/bin/env python
"""Produce stable physical/validation artifact lifecycle census evidence."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "iris_repository_runtime_lightweighting_artifact_lifecycle_v1"
SCOPED_ROOTS = (
    "Iris/build/description/v2/staging",
    "Iris/build/description/v2/.tmp_tests",
    "Iris/build/description/v2/tests",
    "Iris/build/package",
    "Iris/output",
    "Iris/_archive",
    "Iris/_docs/round3",
    "Iris/_docs/refactor",
    "docs",
    "console_log.txt",
    ".tmp",
    ".tmp_tests",
    ".pytest_cache",
)
GIANT_SUFFIXES = {
    "phase2_inventory/allowed_occurrence_inventory.json",
    "phase2_inventory/legacy_active_silent_occurrence_inventory.jsonl",
    "phase3_adjudication/occurrence_adjudication_report.json",
    "phase5_guard/current_surface_guard_report.json",
}
TEXT_SUFFIXES = {".json", ".jsonl", ".lua", ".md", ".py", ".ps1", ".txt"}
LIFECYCLE_TRACKING_ADDITIONS = {
    f"Iris/_docs/refactor/repository_runtime_lightweighting/{name}"
    for name in (
        "validation_checkpoint_manifest.json",
        "bootstrap_validation_receipt.json",
        "baseline_inventory.json",
        "artifact_role_manifest.jsonl",
        "baseline_promotion_receipt.json",
        "baseline_adoption_receipt.json",
        "work_root_contract.json",
        "producer_migration_manifest.json",
        "pre_delete_current_route_receipt.json",
        "current_route_coverage_map.json",
        "archive_operation_manifest.json",
        "archive_restore_receipt.json",
        "archive_promotion_receipt.json",
    )
}


class LifecycleError(RuntimeError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8") + b"\n"
        for row in rows
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise LifecycleError(f"output already exists: {path}")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise LifecycleError(f"temporary output already exists: {temporary}")
    temporary.write_bytes(payload)
    try:
        os.link(temporary, path)
    except FileExistsError as error:
        raise LifecycleError(f"output already exists: {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def require_external(repo: Path, path: Path, role: str) -> Path:
    lexical = Path(os.path.abspath(path))
    try:
        lexical.relative_to(repo)
    except ValueError:
        pass
    else:
        raise LifecycleError(f"{role} lexical path must be outside repository: {lexical}")
    resolved = path.resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        pass
    else:
        raise LifecycleError(f"{role} must be outside repository: {resolved}")
    try:
        repo.relative_to(resolved)
    except ValueError:
        pass
    else:
        raise LifecycleError(f"{role} must not contain repository: {resolved}")
    return resolved


def git(repo: Path, *args: str, binary: bool = False) -> bytes | str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise LifecycleError(completed.stderr.decode("utf-8", errors="replace").strip())
    return completed.stdout if binary else completed.stdout.decode("utf-8", errors="surrogateescape")


def git_path_set(repo: Path, *args: str) -> set[str]:
    raw = git(repo, *args, binary=True)
    assert isinstance(raw, bytes)
    return {
        part.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for part in raw.split(b"\0")
        if part
    }


def repository_identity(repo: Path) -> dict[str, Any]:
    commit = str(git(repo, "rev-parse", "HEAD")).strip()
    tree = str(git(repo, "rev-parse", "HEAD^{tree}")).strip()
    raw_status = git(
        repo,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        binary=True,
    )
    assert isinstance(raw_status, bytes)
    timestamp = str(git(repo, "show", "-s", "--format=%cI", commit)).strip()
    return {
        "commit": commit,
        "tree": tree,
        "working_tree_state": "clean" if not raw_status else "dirty_or_untracked",
        "working_tree_status_sha256": sha256_bytes(raw_status),
        "working_tree_status_entry_count": len([part for part in raw_status.split(b"\0") if part]),
        "inventory_timestamp": timestamp,
    }


def walk_files(root: Path, rel_root: str) -> tuple[list[Path], list[dict[str, Any]]]:
    files: list[Path] = []
    unreadable: list[dict[str, Any]] = []

    def is_reparse(path: Path, entry: os.DirEntry[str] | None = None) -> bool:
        metadata = entry.stat(follow_symlinks=False) if entry is not None else path.lstat()
        return stat.S_ISLNK(metadata.st_mode) or bool(
            int(getattr(metadata, "st_file_attributes", 0)) & 0x400
        )

    def hold(path: Path) -> None:
        unreadable.append(
            {
                "path": path.as_posix(),
                "error_type": "ReparseOrSymlinkHold",
                "error": "reparse/symlink traversal is not admitted",
            }
        )

    def visit(directory: Path) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold())
        except OSError as error:
            unreadable.append(
                {
                    "path": directory.as_posix(),
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
            return
        for entry in entries:
            path = Path(entry.path)
            try:
                metadata = entry.stat(follow_symlinks=False)
                if is_reparse(path, entry):
                    hold(path)
                elif stat.S_ISDIR(metadata.st_mode):
                    visit(path)
                elif stat.S_ISREG(metadata.st_mode):
                    files.append(path)
            except OSError as error:
                unreadable.append(
                    {"path": path.as_posix(), "error_type": type(error).__name__, "error": str(error)}
                )

    try:
        root_metadata = root.lstat()
        if is_reparse(root):
            hold(root)
        elif stat.S_ISDIR(root_metadata.st_mode):
            visit(root)
        elif stat.S_ISREG(root_metadata.st_mode):
            files.append(root)
    except FileNotFoundError:
        pass
    except OSError as error:
        unreadable.append(
            {
                "path": root.as_posix(),
                "error_type": type(error).__name__,
                "error": str(error),
            }
        )
    return files, unreadable


def known_giant(path: str) -> bool:
    return any(path.endswith(suffix) for suffix in GIANT_SUFFIXES) and (
        "legacy_active_silent_current_surface_guard_round/" in path
    )


def classify(path: str, vcs_state: str, current_required_paths: set[str]) -> tuple[str, str, bool, str | None, list[str]]:
    lowered = path.lower()
    if known_giant(path):
        return (
            "diagnostic_only",
            "delete_candidate_after_guard_pilot",
            True,
            "build_legacy_active_silent_current_surface_guard_round.py",
            [
                "guard_backend_parity_pass",
                "single_serialization_pilot_pass",
                "zero_live_reference",
                "archive_restore_verified",
                "post_evidence_owner_approval",
            ],
        )
    if "/2105_baseline_consumption_audit/" in lowered:
        return (
            "historical_reproduction",
            "retained_historical_reproduction",
            False,
            None,
            ["consumer_migration_complete", "zero_live_reference", "archive_restore_verified"],
        )
    if any(token in lowered for token in ("/__pycache__/", "/.tmp_tests/", "/.pytest_cache/")) or lowered.startswith((".tmp_tests/", ".pytest_cache/")):
        return "disposable", "disposable", True, None, ["no_active_process", "exact_leaf_selection"]
    if lowered.startswith(".tmp/"):
        if "uv-cache" in lowered or "__pycache__" in lowered:
            return "disposable", "disposable", True, None, ["no_active_process", "exact_leaf_selection"]
        return "historical_reproduction", "retained_historical_reproduction", False, None, ["backup_owner_review"]
    if path.startswith("Iris/build/package/"):
        return "generated_projection", "disposable", True, "Iris/tools/package_iris.ps1", ["regenerable", "zero_live_reference"]
    if path.startswith(("Iris/output/", "Iris/_archive/")) or path.endswith(("console_log.txt", ".log")):
        return "historical_reproduction", "retained_historical_reproduction", False, None, ["consumer_graph_complete"]
    if path.startswith("Iris/media/lua/"):
        return "current_authority", "retained_current_required", False, None, []
    if path == "console_log.txt" or "playtest" in lowered or path.endswith(("console_log.txt", ".log")):
        return "historical_reproduction", "retained_historical_reproduction", False, None, ["consumer_graph_complete"]
    if path.startswith(("Iris/_docs/round3/", "Iris/_docs/refactor/", "docs/")):
        return "current_required_evidence", "retained_current_required", False, None, []
    if path.startswith("Iris/build/description/v2/tests/"):
        if path in current_required_paths:
            return "current_required_evidence", "retained_current_required", False, None, []
        return "historical_reproduction", "retained_historical_reproduction", False, None, ["taxonomy_role_preserved"]
    if path.startswith("Iris/build/description/v2/staging/"):
        return "historical_reproduction", "retained_historical_reproduction", False, None, ["role_specific_review"]
    return "unclassified", "unclassified_hold", False, None, ["role_classification", "consumer_graph_complete"]


def current_required_source_paths(repo: Path) -> set[str]:
    taxonomy_path = repo / "Iris/_docs/round3/round3_test_taxonomy.json"
    required_path = repo / "Iris/_docs/round3/current_route_required_validations.json"
    if not taxonomy_path.is_file() or not required_path.is_file():
        return set()
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    required = json.loads(required_path.read_text(encoding="utf-8"))
    by_id = {str(row.get("test_id")): row for row in taxonomy.get("rows", [])}
    return {
        str(by_id[test_id]["source_file"])
        for test_id in (str(row.get("test_id", "")) for row in required.get("required_tests", []))
        if test_id in by_id and by_id[test_id].get("source_file")
    }


def scoped_roots(
    repo: Path,
    unreadable: list[dict[str, Any]] | None = None,
) -> list[str]:
    roots = set(SCOPED_ROOTS)
    iris_root = repo / "Iris"
    holds = unreadable if unreadable is not None else []

    def visit(directory: Path) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold())
        except OSError as error:
            holds.append(
                {
                    "path": directory.as_posix(),
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
            return
        for entry in entries:
            path = Path(entry.path)
            try:
                metadata = entry.stat(follow_symlinks=False)
                reparse = stat.S_ISLNK(metadata.st_mode) or bool(
                    int(getattr(metadata, "st_file_attributes", 0)) & 0x400
                )
                if reparse:
                    holds.append(
                        {
                            "path": path.as_posix(),
                            "error_type": "ReparseOrSymlinkHold",
                            "error": "reparse/symlink traversal is not admitted",
                        }
                    )
                    continue
                if not stat.S_ISDIR(metadata.st_mode):
                    continue
                if path.name in {"__pycache__", ".pytest_cache", ".tmp", ".tmp_tests"}:
                    roots.add(path.relative_to(repo).as_posix())
                    continue
                visit(path)
            except OSError as error:
                holds.append(
                    {
                        "path": path.as_posix(),
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                )

    try:
        iris_metadata = iris_root.lstat()
        if stat.S_ISDIR(iris_metadata.st_mode) and not bool(
            int(getattr(iris_metadata, "st_file_attributes", 0)) & 0x400
        ):
            visit(iris_root)
    except FileNotFoundError:
        pass
    return sorted(roots)


def call_name(node: ast.Call) -> str:
    value = node.func
    parts: list[str] = []
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def text_tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_][A-Za-z0-9_.-]{2,}", text))


def reference_graph(
    repo: Path,
    rows: list[dict[str, Any]],
    tracked: set[str],
    untracked: set[str],
) -> dict[str, dict[str, Any]]:
    by_basename: dict[str, list[str]] = defaultdict(list)
    module_paths: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        if row.get("path_access") != "readable":
            continue
        relative = str(row["path"])
        basename = Path(relative).name
        by_basename[basename].append(relative)
        if relative.endswith(".py"):
            module_paths[Path(relative).stem].append(relative)

    all_axes: dict[str, dict[str, set[str]]] = {
        str(row["path"]): defaultdict(set) for row in rows
    }
    import_graph: dict[str, set[str]] = defaultdict(set)
    scan_holds: list[dict[str, str]] = []
    ignored = git_path_set(repo, "ls-files", "-z", "--others", "-i", "--exclude-standard")
    target_paths = {str(row["path"]) for row in rows}
    source_paths = sorted(tracked | untracked | ignored)
    for relative in source_paths:
        if relative in target_paths and known_giant(relative):
            continue
        if relative.endswith(".py") and relative not in module_paths[Path(relative).stem]:
            module_paths[Path(relative).stem].append(relative)
    for relative in source_paths:
        path = repo / relative
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        try:
            large_source = path.stat().st_size > 8 * 1024 * 1024
            if large_source:
                tokens: set[str] = set()
                overlap = ""
                with path.open("r", encoding="utf-8", errors="ignore") as handle:
                    while True:
                        chunk = handle.read(8 * 1024 * 1024)
                        if not chunk:
                            break
                        window = overlap + chunk
                        tokens.update(text_tokens(window))
                        overlap = window[-512:]
                text = ""
            else:
                text = path.read_text(encoding="utf-8", errors="ignore")
                tokens = text_tokens(text)
        except OSError as error:
            scan_holds.append({"path": relative, "error_type": type(error).__name__, "error": str(error)})
            continue
        hits = sorted(tokens.intersection(by_basename))
        if not hits and path.suffix.lower() != ".py":
            continue
        call_axes: dict[str, set[str]] = defaultdict(set)
        imported_names: set[str] = set()
        if path.suffix.lower() == ".py" and not large_source:
            try:
                tree = ast.parse(text, filename=relative)
            except SyntaxError:
                tree = None
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported_names.update(alias.name.rsplit(".", 1)[-1] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_names.add(node.module.rsplit(".", 1)[-1])
                        imported_names.update(alias.name.rsplit(".", 1)[-1] for alias in node.names if alias.name != "*")
                    elif isinstance(node, ast.Call):
                        name = call_name(node).lower()
                        literal_tokens: set[str] = set()
                        for child in ast.walk(node):
                            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                                literal_tokens.update(text_tokens(child.value))
                        for basename in literal_tokens.intersection(by_basename):
                            if "subprocess" in name or name.endswith(("run", "popen", "check_call", "check_output")):
                                call_axes[basename].add("subprocess_invocation")
                            elif name.endswith(("write_text", "write_bytes", "write_json", "dump", "writestr")):
                                call_axes[basename].add("producer_reference")
                            elif name.endswith(("read_text", "read_bytes", "load", "load_json")):
                                call_axes[basename].add("python_read")
                            elif name.endswith("open"):
                                modes = {
                                    child.value
                                    for child in ast.walk(node)
                                    if isinstance(child, ast.Constant) and isinstance(child.value, str)
                                }
                                call_axes[basename].add(
                                    "producer_reference" if modes.intersection({"w", "wb", "a", "ab", "x", "xb"}) else "python_read"
                                )
                for imported in imported_names:
                    for target_module in module_paths.get(imported, []):
                        if target_module != relative:
                            import_graph[relative].add(target_module)
                            if target_module in all_axes:
                                all_axes[target_module]["python_import"].add(relative)

        for basename in hits:
            for target in by_basename[basename]:
                if target == relative:
                    continue
                axes: set[str]
                if relative.startswith(("docs/", "Iris/_docs/")):
                    axes = {"documentation_owner_reference"}
                elif relative.startswith("Iris/validation/residual_refactor/"):
                    axes = {"lifecycle_evidence_reference"}
                elif path.suffix.lower() in {".json", ".jsonl"}:
                    axes = {"manifest_path"}
                elif relative.endswith("Iris/tools/package_iris.ps1") or "package" in path.stem.lower():
                    axes = {"package_reachability"}
                else:
                    axes = set(call_axes.get(basename, set()))
                    if path.suffix.lower() == ".py" and Path(target).stem in imported_names:
                        axes.add("python_import")
                    if not axes:
                        axes.add("python_string_reference")
                for axis in axes:
                    all_axes[target][axis].add(relative)

    live_axis_names = {
        "python_import",
        "python_read",
        "python_string_reference",
        "subprocess_invocation",
        "manifest_path",
        "package_reachability",
    }
    reverse_imports: dict[str, set[str]] = defaultdict(set)
    for importer, imported_paths in import_graph.items():
        for imported in imported_paths:
            reverse_imports[imported].add(importer)
    result: dict[str, dict[str, Any]] = {}
    for target, axes in all_axes.items():
        direct = set().union(*(paths for axis, paths in axes.items() if axis in live_axis_names)) if axes else set()
        transitive = set(direct)
        pending = list(direct)
        while pending:
            consumer = pending.pop()
            for importer in reverse_imports.get(consumer, set()):
                if importer not in transitive:
                    transitive.add(importer)
                    pending.append(importer)
        result[target] = {
            "consumer_axes": {axis: sorted(paths) for axis, paths in sorted(axes.items())},
            "direct_consumers": sorted(direct),
            "transitive_consumers": sorted(transitive - direct),
            "consumer_scan_holds": scan_holds,
            "zero_live_consumers": not direct and not transitive and not scan_holds,
        }
    return result


def build_rows(
    repo: Path,
    *,
    include_missing_giants: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tracked = git_path_set(repo, "ls-files", "-z")
    untracked = git_path_set(repo, "ls-files", "-z", "--others", "--exclude-standard")
    ignored = git_path_set(repo, "ls-files", "-z", "--others", "-i", "--exclude-standard")
    rows: list[dict[str, Any]] = []
    unreadable_rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    required_sources = current_required_source_paths(repo)
    resolved_scope_roots = scoped_roots(repo, unreadable_rows)
    for root_rel in resolved_scope_roots:
        root = repo / root_rel
        if not root.exists():
            rows.append(
                {
                    "schema_version": SCHEMA,
                    "logical_artifact_id": f"missing:{root_rel}",
                    "path": root_rel,
                    "path_access": "missing_referenced",
                    "vcs_state": "missing",
                    "producer": None,
                    "direct_consumers": [],
                    "transitive_consumers": [],
                    "route_class": "not_present",
                    "authority_role": "diagnostic_only",
                    "evidence_role": "disposable",
                    "regenerable": True,
                    "restore_source": None,
                    "delete_preconditions": [],
                    "delete_eligible": False,
                    "size_bytes": 0,
                    "sha256": None,
                }
            )
            continue
        files, unreadable = walk_files(root, root_rel)
        for issue in unreadable:
            try:
                relative = Path(os.path.abspath(issue["path"])).relative_to(repo).as_posix()
            except ValueError:
                relative = str(issue["path"]).replace("\\", "/")
            unreadable_rows.append({**issue, "path": relative})
        for path in files:
            try:
                relative = path.resolve().relative_to(repo).as_posix()
            except (OSError, ValueError) as error:
                unreadable_rows.append(
                    {"path": path.as_posix(), "error_type": type(error).__name__, "error": str(error)}
                )
                continue
            if relative in seen:
                continue
            seen.add(relative)
            vcs_state = "tracked" if relative in tracked else "ignored" if relative in ignored else "untracked" if relative in untracked else "filesystem_only"
            authority, evidence, regenerable, producer, preconditions = classify(relative, vcs_state, required_sources)
            try:
                size = path.stat().st_size
                digest = sha256_file(path)
                access = "readable"
            except OSError as error:
                unreadable_rows.append(
                    {"path": relative, "error_type": type(error).__name__, "error": str(error)}
                )
                continue
            rows.append(
                {
                    "schema_version": SCHEMA,
                    "logical_artifact_id": f"sha256:{digest}",
                    "path": relative,
                    "path_access": access,
                    "vcs_state": vcs_state,
                    "producer": producer,
                    "consumer_axes": {},
                    "direct_consumers": [],
                    "transitive_consumers": [],
                    "zero_live_consumers": False,
                    "route_class": (
                        "current" if authority in {"current_authority", "current_required_evidence"}
                        else "historical" if authority == "historical_reproduction"
                        else "diagnostic" if authority == "diagnostic_only"
                        else "projection"
                    ),
                    "authority_role": authority,
                    "evidence_role": evidence,
                    "regenerable": regenerable,
                    "restore_source": None if authority in {"current_authority", "current_required_evidence"} else "cold_archive_required_before_delete",
                    "delete_preconditions": preconditions,
                    "delete_eligible": False,
                    "size_bytes": size,
                    "sha256": digest,
                }
            )
    deduplicated_unreadable = {
        (str(issue["path"]), str(issue["error_type"])): issue
        for issue in unreadable_rows
    }
    unreadable_rows = [
        deduplicated_unreadable[key] for key in sorted(deduplicated_unreadable)
    ]
    for issue in unreadable_rows:
        rows.append(
            {
                "schema_version": SCHEMA,
                "logical_artifact_id": f"unreadable:{issue['path']}",
                "path": issue["path"],
                "path_access": "unreadable",
                "vcs_state": "unknown",
                "producer": None,
                "direct_consumers": [],
                "transitive_consumers": [],
                "route_class": "unreadable_hold",
                "authority_role": "diagnostic_only",
                "evidence_role": "unreadable_hold",
                "regenerable": False,
                "restore_source": None,
                "delete_preconditions": ["permission_recovery", "recensus"],
                "delete_eligible": False,
                "size_bytes": 0,
                "sha256": None,
                "error_type": issue["error_type"],
                "error": issue["error"],
            }
        )
    existing_paths = {str(row["path"]) for row in rows}
    if include_missing_giants:
        giant_root = "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round"
        for suffix in sorted(GIANT_SUFFIXES):
            relative = f"{giant_root}/{suffix}"
            if relative in existing_paths:
                continue
            rows.append(
                {
                    "schema_version": SCHEMA,
                    "logical_artifact_id": f"missing:{relative}",
                    "path": relative,
                    "path_access": "missing_referenced",
                    "vcs_state": "missing",
                    "producer": "build_legacy_active_silent_current_surface_guard_round.py",
                    "consumer_axes": {},
                    "direct_consumers": [],
                    "transitive_consumers": [],
                    "zero_live_consumers": False,
                    "route_class": "diagnostic",
                    "authority_role": "diagnostic_only",
                    "evidence_role": "missing_referenced_hold",
                    "regenerable": True,
                    "restore_source": None,
                    "delete_preconditions": ["materialize_physical_subject", "recensus"],
                    "delete_eligible": False,
                    "size_bytes": 0,
                    "sha256": None,
                }
            )
    rows = sorted(rows, key=lambda row: str(row["path"]))
    references = reference_graph(repo, rows, tracked, untracked)
    for row in rows:
        row.update(references.get(str(row["path"]), {}))
    return rows, unreadable_rows


def summary_for(repo: Path, subject_kind: str, identity: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    byte_by_role: dict[str, int] = defaultdict(int)
    byte_by_vcs: dict[str, int] = defaultdict(int)
    counts = Counter()
    for row in rows:
        size = int(row.get("size_bytes", 0))
        byte_by_role[str(row["authority_role"])] += size
        byte_by_vcs[str(row["vcs_state"])] += size
        counts[str(row["authority_role"])] += 1
    physical_bytes = sum(int(row.get("size_bytes", 0)) for row in rows)
    giant_rows = [
        row
        for row in rows
        if known_giant(str(row["path"]))
        and row.get("path_access") == "readable"
        and row.get("vcs_state") == "ignored"
        and row.get("sha256")
    ]
    unclassified_count = sum(row["authority_role"] == "unclassified" for row in rows)
    unreadable_count = sum(row["path_access"] == "unreadable" for row in rows)
    consumer_scan_holds = rows[0].get("consumer_scan_holds", []) if rows else []
    run_identity = sha256_bytes(
        canonical_json_bytes(
            {
                "subject_kind": subject_kind,
                "root": repo.as_posix(),
                "commit": identity["commit"],
                "tree": identity["tree"],
                "working_tree_status_sha256": identity["working_tree_status_sha256"],
            }
        )
    )
    phase0_inventory_path = repo / "Iris/_docs/refactor/residual_refactor/phase0_inventory.json"
    final_inventory_path = repo / "Iris/_docs/refactor/residual_refactor/final_inventory.json"
    inventory_producer_path = repo / "Iris/validation/residual_refactor/report_inventory.py"
    required_validation_path = repo / "Iris/_docs/round3/current_route_required_validations.json"

    def prior_counts(path: Path) -> dict[str, Any]:
        if not path.is_file():
            return {"path": path.relative_to(repo).as_posix(), "exists": False}
        payload = json.loads(path.read_text(encoding="utf-8"))
        counts_payload = payload.get("counts", {})
        return {
            "path": path.relative_to(repo).as_posix(),
            "exists": True,
            "sha256": sha256_file(path),
            "build_tools_python_recursive": counts_payload.get("build_tools_python_recursive"),
            "build_tools_python_root_direct": counts_payload.get("build_tools_python_root_direct"),
        }

    build_tools = repo / "Iris/build/description/v2/tools/build"
    current_recursive = len(list(build_tools.rglob("*.py"))) if build_tools.is_dir() else 0
    current_root_direct = len(list(build_tools.glob("*.py"))) if build_tools.is_dir() else 0
    tracked_paths = sorted(git_path_set(repo, "ls-files", "-z"))
    protected_tracked_paths = sorted(
        str(row["path"])
        for row in rows
        if row.get("vcs_state") == "tracked"
        and row.get("authority_role") in {"current_authority", "current_required_evidence"}
    )
    return {
        "schema_version": SCHEMA,
        "subject_kind": subject_kind,
        "physical_resolved_root": repo.as_posix(),
        **identity,
        "run_identity": run_identity,
        "scoped_roots": scoped_roots(repo),
        "file_count": len(rows),
        "physical_bytes": physical_bytes,
        "role_partition_bytes": dict(sorted(byte_by_role.items())),
        "vcs_partition_bytes": dict(sorted(byte_by_vcs.items())),
        "role_counts": dict(sorted(counts.items())),
        "unclassified_count": unclassified_count,
        "unreadable_count": unreadable_count,
        "consumer_scan_hold_count": len(consumer_scan_holds),
        "consumer_scan_holds": consumer_scan_holds,
        "current_required_count": sum(
            row["authority_role"] in {"current_authority", "current_required_evidence"} for row in rows
        ),
        "delete_eligible_count": sum(bool(row["delete_eligible"]) for row in rows),
        "ignored_giant_count": len(giant_rows),
        "ignored_giant_paths": [str(row["path"]) for row in giant_rows],
        "complete_accounting": unclassified_count == 0 and unreadable_count == 0 and not consumer_scan_holds,
        "archive_delete_allowed": False,
        "tracked_paths": tracked_paths,
        "tracked_path_count": len(tracked_paths),
        "tracked_path_set_sha256": sha256_bytes(canonical_json_bytes(tracked_paths)),
        "protected_tracked_paths": protected_tracked_paths,
        "protected_tracked_path_set_sha256": sha256_bytes(canonical_json_bytes(protected_tracked_paths)),
        "tool_role_inventory_axis": {
            "relationship": "additive_not_replacement",
            "producer": {
                "path": inventory_producer_path.relative_to(repo).as_posix(),
                "exists": inventory_producer_path.is_file(),
                "sha256": sha256_file(inventory_producer_path) if inventory_producer_path.is_file() else None,
            },
            "sealed_predecessor": prior_counts(phase0_inventory_path),
            "latest_predecessor": prior_counts(final_inventory_path),
            "current_physical_denominator": {
                "build_tools_python_recursive": current_recursive,
                "build_tools_python_root_direct": current_root_direct,
            },
        },
        "current_required_validation_identity": {
            "path": required_validation_path.relative_to(repo).as_posix(),
            "exists": required_validation_path.is_file(),
            "sha256": sha256_file(required_validation_path) if required_validation_path.is_file() else None,
        },
        "runtime_baseline": {
            "status": "pending_runtime_track_measurement",
            "required_metrics": [
                "boot_build_calls",
                "first_browser_open",
                "first_alt_tooltip",
                "first_detail_open",
                "loaded_chunk_module_set",
                "search_query_count",
            ],
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--subject-kind", choices=("physical_capacity_subject", "validation_subject"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--subject-receipt-out", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--tracking-transition-out", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        raise LifecycleError(f"not a Git checkout: {repo}")
    outputs = [
        require_external(repo, args.out, "manifest output"),
        require_external(repo, args.summary_out, "summary output"),
        require_external(repo, args.subject_receipt_out, "subject receipt output"),
    ]
    if args.tracking_transition_out:
        outputs.append(require_external(repo, args.tracking_transition_out, "tracking transition output"))
    if len({os.path.normcase(str(path)) for path in outputs}) != len(outputs):
        raise LifecycleError("output paths must be distinct")

    baseline: dict[str, Any] | None = None
    if args.tracking_transition_out:
        if not args.baseline:
            raise LifecycleError("--tracking-transition-out requires --baseline")
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        if baseline.get("physical_resolved_root") != repo.as_posix():
            raise LifecycleError("baseline physical subject mismatch")
        if baseline.get("subject_kind") != "physical_capacity_subject" or baseline.get("ignored_giant_count") != 4:
            raise LifecycleError("tracking transition requires an authoritative physical baseline")

    identity = repository_identity(repo)
    rows, _ = build_rows(
        repo,
        include_missing_giants=args.subject_kind == "physical_capacity_subject",
    )
    summary = summary_for(repo, args.subject_kind, identity, rows)
    if (
        args.subject_kind == "physical_capacity_subject"
        and args.baseline is None
        and summary["ignored_giant_count"] != 4
    ):
        raise LifecycleError(
            "baseline physical_capacity_subject requires all four readable ignored giant artifacts"
        )
    manifest_bytes = canonical_jsonl_bytes(rows)
    summary_bytes = canonical_json_bytes(summary)
    atomic_write(outputs[0], manifest_bytes)
    atomic_write(outputs[1], summary_bytes)
    receipt = {
        "schema_version": "iris_repository_runtime_lightweighting_subject_receipt_v1",
        "subject_kind": args.subject_kind,
        "physical_resolved_root": repo.as_posix(),
        "commit": identity["commit"],
        "tree": identity["tree"],
        "working_tree_state": identity["working_tree_state"],
        "working_tree_status_sha256": identity["working_tree_status_sha256"],
        "run_identity": summary["run_identity"],
        "manifest": {"path": outputs[0].as_posix(), "sha256": sha256_bytes(manifest_bytes), "bytes": len(manifest_bytes)},
        "summary": {"path": outputs[1].as_posix(), "sha256": sha256_bytes(summary_bytes), "bytes": len(summary_bytes)},
        "ignored_giant_count": summary["ignored_giant_count"],
        "unclassified_count": summary["unclassified_count"],
        "unreadable_count": summary["unreadable_count"],
        "consumer_scan_hold_count": summary["consumer_scan_hold_count"],
        "complete_accounting": summary["complete_accounting"],
    }
    atomic_write(outputs[2], canonical_json_bytes(receipt))

    transition_failed = False
    if args.tracking_transition_out:
        assert baseline is not None
        baseline_tracked = {str(path) for path in baseline.get("tracked_paths", [])}
        current_tracked = set(summary["tracked_paths"])
        protected = {str(path) for path in baseline.get("protected_tracked_paths", [])}
        producer_manifest_path = repo / "Iris/_docs/refactor/repository_runtime_lightweighting/producer_migration_manifest.json"
        producer_approved: set[str] = set()
        if producer_manifest_path.is_file():
            producer_manifest = json.loads(producer_manifest_path.read_text(encoding="utf-8"))
            producer_approved = {
                str(path) for path in producer_manifest.get("approved_newly_tracked_paths", [])
            }
        approved_additions = LIFECYCLE_TRACKING_ADDITIONS | producer_approved
        added = sorted(current_tracked - baseline_tracked)
        removed = sorted(baseline_tracked - current_tracked)
        unapproved_added = sorted(set(added) - approved_additions)
        unexpectedly_untracked_protected = sorted(protected.intersection(removed))
        transition_failed = bool(unapproved_added or removed)
        transition = {
            "schema_version": "iris_repository_runtime_lightweighting_tracking_transition_v1",
            "status": "FAIL" if transition_failed else "PASS",
            "subject_kind": args.subject_kind,
            "physical_resolved_root": repo.as_posix(),
            "baseline_run_identity": baseline.get("run_identity"),
            "final_run_identity": summary["run_identity"],
            "baseline_physical_bytes": baseline.get("physical_bytes"),
            "final_physical_bytes": summary["physical_bytes"],
            "physical_byte_delta": int(summary["physical_bytes"]) - int(baseline.get("physical_bytes", 0)),
            "baseline_tracked_path_set_sha256": baseline.get("tracked_path_set_sha256"),
            "final_tracked_path_set_sha256": summary["tracked_path_set_sha256"],
            "added_tracked_paths": added,
            "removed_tracked_paths": removed,
            "removed_tracked_count": len(removed),
            "approved_newly_tracked_paths": sorted(set(added).intersection(approved_additions)),
            "unexpectedly_untracked_protected_paths": unexpectedly_untracked_protected,
            "unexpectedly_untracked_protected_count": len(unexpectedly_untracked_protected),
            "unapproved_newly_tracked_paths": unapproved_added,
            "unapproved_newly_tracked_count": len(unapproved_added),
            "producer_migration_manifest": {
                "path": producer_manifest_path.relative_to(repo).as_posix(),
                "exists": producer_manifest_path.is_file(),
                "sha256": sha256_file(producer_manifest_path) if producer_manifest_path.is_file() else None,
            },
        }
        atomic_write(outputs[3], canonical_json_bytes(transition))
    if transition_failed:
        raise LifecycleError("tracking transition contains unapproved tracked-path changes")
    print(json.dumps({"status": "PASS", "file_count": len(rows), "physical_bytes": summary["physical_bytes"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LifecycleError, OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "FAIL", "error_type": type(error).__name__, "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(2)
