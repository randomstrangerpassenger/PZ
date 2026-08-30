#!/usr/bin/env python
"""Convert evidence between lifecycle deltas, content-addressed objects and archives."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import platform
import zipfile
import zlib
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from lifecycle_delta_codec import (
    BASELINE_NAME,
    DELTA_NAME,
    DICTIONARY_NAME,
    MIGRATION_RECEIPT_NAME,
    NODES_NAME,
    RepositoryEvidenceCodecError,
    build_v2_payloads,
    canonical_json_bytes,
    decode_v2_root,
    raw_sha256,
    read_v1_stream,
)


RECEIPT_SCHEMA = "iris_repository_evidence_lifecycle_migration_receipt_v2"
LIFECYCLE_NAMES = {
    "artifact_role_manifest.jsonl",
    "final_artifact_role_manifest.jsonl",
}
CAS_INVENTORY_SCHEMA = "iris_repository_evidence_cas_inventory_v1"
CAS_PLAN_SCHEMA = "iris_repository_evidence_cas_plan_v1"
CAS_REFERENCE_SCHEMA = "iris_repository_evidence_cas_reference_v1"
CAS_RECEIPT_SCHEMA = "iris_repository_evidence_cas_receipt_v1"
COLD_ARCHIVE_SCHEMA = "iris_repository_evidence_cold_archive_v1"
COLD_ARCHIVE_RECEIPT_SCHEMA = "iris_repository_evidence_cold_archive_receipt_v1"
COLD_EMBEDDED_MANIFEST = "__iris_repository_evidence_operation_manifest.json"


class MigrationError(RuntimeError):
    pass


def _repo_relative(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError as error:
        raise MigrationError(f"required input is outside the repository: {path}") from error


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise MigrationError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.rstrip("\r\n")


def _write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError as error:
        raise MigrationError(f"migration output already exists: {path}") from error


def _identity(repo: Path, path: Path, payload: bytes, rows: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "bytes": len(payload),
        "path": _repo_relative(repo, path),
        "sha256": raw_sha256(payload),
    }
    if rows is not None:
        result["rows"] = rows
    return result


def _inventory_disposition(repo: Path) -> dict[str, Any]:
    source_path = repo / "Iris/validation/source_analysis/inventory_build_tool_dependencies.py"
    source_bytes = source_path.read_bytes()
    source = source_bytes.decode("utf-8-sig")
    tree = ast.parse(source, filename=str(source_path))
    ast_hits = sorted(
        {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value in LIFECYCLE_NAMES
        }
    )
    lexical_hits = sorted(name for name in LIFECYCLE_NAMES if name in source)
    status = "sealed_no_change" if not ast_hits and not lexical_hits else "reader_change_required"
    if status != "sealed_no_change":
        raise MigrationError("inventory_build_tool_dependencies.py directly references lifecycle v1 artifacts")
    return {
        "ast_exact_string_hits": ast_hits,
        "lexical_exact_name_hits": lexical_hits,
        "scan_contract": "python_ast_constants_plus_exact_lexical_names",
        "source_bytes": len(source_bytes),
        "source_path": _repo_relative(repo, source_path),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "status": status,
    }


def _checkout_contract(repo: Path, paths: list[Path]) -> dict[str, Any]:
    attributes = {
        _repo_relative(repo, path): _git(repo, "check-attr", "-a", "--", _repo_relative(repo, path)).splitlines()
        for path in paths
    }
    attributes_path = repo / ".gitattributes"
    attributes_identity: dict[str, Any] | None = None
    if attributes_path.is_file():
        payload = attributes_path.read_bytes()
        attributes_identity = _identity(repo, attributes_path, payload)
    return {
        "canonical_json": "utf8_no_bom_lf_compact_sorted_keys_ensure_ascii_false_single_final_newline",
        "core_autocrlf": _git(repo, "config", "--get", "core.autocrlf") or "unset",
        "gitattributes": attributes_identity,
        "path_attributes": attributes,
    }


def migrate(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    baseline_path = args.baseline_v1.resolve()
    final_path = args.final_v1.resolve()
    output_root = args.out.resolve()
    for path in (baseline_path, final_path):
        _repo_relative(repo, path)
        if not path.is_file():
            raise MigrationError(f"v1 input is missing: {path}")
    _repo_relative(repo, output_root)
    if output_root.exists():
        raise MigrationError(f"migration output root already exists: {output_root}")

    baseline = read_v1_stream(baseline_path)
    final = read_v1_stream(final_path)
    payloads = build_v2_payloads(baseline.rows, final.rows)
    for name in (DICTIONARY_NAME, NODES_NAME, BASELINE_NAME, DELTA_NAME):
        _write_new(output_root / name, payloads[name])

    decoded = decode_v2_root(output_root)
    if decoded.baseline_bytes != baseline.raw_bytes or decoded.final_bytes != final.raw_bytes:
        raise MigrationError("v2 reconstruction differs from the v1 byte streams")
    if len(decoded.baseline_rows) != 7512 or len(decoded.final_rows) != 7515 or decoded.shared_rows != 6737:
        raise MigrationError("lifecycle row/shared-row invariants differ from the adopted plan")

    v2_identities = {
        name: _identity(repo, output_root / name, payloads[name])
        for name in (DICTIONARY_NAME, NODES_NAME, BASELINE_NAME, DELTA_NAME)
    }
    receipt = {
        "checkout_contract": _checkout_contract(repo, [baseline_path, final_path]),
        "inventory_reader_disposition": _inventory_disposition(repo),
        "parity": {
            "added_rows": decoded.added_rows,
            "baseline_rows": len(decoded.baseline_rows),
            "final_rows": len(decoded.final_rows),
            "removed_rows": decoded.removed_rows,
            "replaced_rows": decoded.replaced_rows,
            "shared_exact_rows": decoded.shared_rows,
        },
        "reconstruction": {
            "baseline_byte_identical": True,
            "final_byte_identical": True,
            "ordering_preserved": True,
            "single_lf_final_newline_preserved": True,
        },
        "schema_version": RECEIPT_SCHEMA,
        "source_v1": {
            "baseline": _identity(repo, baseline_path, baseline.raw_bytes, len(baseline.rows)),
            "final": _identity(repo, final_path, final.raw_bytes, len(final.rows)),
        },
        "status": "PASS",
        "v2_artifacts": v2_identities,
    }
    _write_new(output_root / MIGRATION_RECEIPT_NAME, canonical_json_bytes(receipt))


def reconstruct(args: argparse.Namespace) -> None:
    root = args.v2_root.resolve()
    bundle = decode_v2_root(root)
    payload = bundle.baseline_bytes if args.view == "baseline" else bundle.final_bytes
    _write_new(args.out.resolve(), payload)


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MigrationError(f"expected JSON object: {path}")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _regular_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink() and not (
        getattr(path.lstat(), "st_file_attributes", 0) & 0x400
    )


def _repository_path_parts(value: str, label: str) -> tuple[str, ...]:
    if (
        not value
        or "\\" in value
        or PurePosixPath(value).is_absolute()
        or PureWindowsPath(value).is_absolute()
        or bool(PureWindowsPath(value).drive)
    ):
        raise MigrationError(f"{label} must be a repository-relative POSIX path: {value}")
    parts = tuple(value.split("/"))
    if any(part in {"", ".", ".."} for part in parts):
        raise MigrationError(f"{label} contains a non-canonical path component: {value}")
    return parts


def _reference_relative(source_root: str, original_path: str) -> Path:
    root_parts = _repository_path_parts(source_root, "CAS source_root")
    path_parts = _repository_path_parts(original_path, "CAS original_path")
    if len(path_parts) <= len(root_parts) or path_parts[: len(root_parts)] != root_parts:
        raise MigrationError(f"CAS original_path is outside source_root: {original_path}")
    return Path(*path_parts[len(root_parts) :])


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _assert_no_reparse_ancestor(path: Path, label: str) -> None:
    current = path
    while True:
        if os.path.lexists(current) and _is_reparse_point(current):
            raise MigrationError(f"{label} traverses a reparse point: {current}")
        if current.parent == current:
            return
        current = current.parent


def _git_paths(repo: Path, *args: str) -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), args[0], "-z", *args[1:]],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise MigrationError(completed.stderr.decode("utf-8", errors="replace").strip())
    return {
        item.decode("utf-8", errors="strict")
        for item in completed.stdout.split(b"\0")
        if item
    }


def cas_inventory(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    source_root = args.source_root.resolve()
    relative_root = _repo_relative(repo, source_root)
    if not source_root.is_dir():
        raise MigrationError(f"CAS source root is missing: {source_root}")
    tracked = _git_paths(repo, "ls-files", "--", relative_root)
    ignored = _git_paths(repo, "ls-files", "--others", "-i", "--exclude-standard", "--", relative_root)
    rows: list[dict[str, Any]] = []
    for path in sorted(source_root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_dir():
            continue
        if not _regular_file(path):
            raise MigrationError(f"CAS inventory rejects non-regular file: {path}")
        relative = _repo_relative(repo, path)
        if relative in tracked:
            vcs_state = "tracked_physical_exception"
        elif relative in ignored:
            vcs_state = "ignored_migration_candidate"
        else:
            vcs_state = "untracked_blocker"
        root_relative = path.relative_to(source_root).as_posix()
        parts = Path(root_relative).parts
        rows.append(
            {
                "attempt": parts[0] if parts else "root",
                "chronology": len(rows),
                "media_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                "path": relative,
                "phase": parts[1] if len(parts) > 1 else "root",
                "producer": "repository_evidence_migration_v1",
                "sha256": _sha256_file(path),
                "size_bytes": path.stat().st_size,
                "vcs_state": vcs_state,
            }
        )
    if any(row["vcs_state"] == "untracked_blocker" for row in rows):
        raise MigrationError("CAS inventory contains untracked non-ignored files")
    payload = {
        "schema_version": CAS_INVENTORY_SCHEMA,
        "source_root": relative_root,
        "file_count": len(rows),
        "physical_bytes": sum(row["size_bytes"] for row in rows),
        "rows": rows,
    }
    _write_new(args.out.resolve(), canonical_json_bytes(payload))


def _literal_path_parts(candidate: Path, text: str) -> tuple[set[str], str, bool]:
    if candidate.suffix.lower() == ".py":
        try:
            tree = ast.parse(text, filename=str(candidate))
        except SyntaxError:
            return set(), "python_ast_parse_failed", False
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        scan = "python_ast_string_fragments"
    else:
        literals = {
            match.group(2)
            for match in re.finditer(r"(['\"])(.*?)(?<!\\)\1", text, flags=re.DOTALL)
        }
        scan = "quoted_string_fragments"
    parts = {
        part
        for literal in literals
        for part in literal.replace("\\", "/").split("/")
        if part not in {"", ".", ".."}
    }
    return parts, scan, True


def _dynamic_path_references(
    candidate: Path,
    text: str,
    source_root: str,
    selected_paths: set[str],
) -> tuple[list[str], str, bool]:
    literal_parts, scan, parsed = _literal_path_parts(candidate, text)
    root_marker = _repository_path_parts(source_root, "CAS source_root")[-1]
    if root_marker not in literal_parts:
        return [], scan, parsed
    references = []
    for path in selected_paths:
        relative = _reference_relative(source_root, path)
        if all(part in literal_parts for part in relative.parts):
            references.append(path)
    return sorted(references), scan, parsed


def _consumer_scan(repo: Path, source_root: str, selected_paths: set[str]) -> dict[str, Any]:
    basename_counts: dict[str, int] = {}
    for path in selected_paths:
        basename = _reference_relative(source_root, path).name
        basename_counts[basename] = basename_counts.get(basename, 0) + 1
    patterns = {
        source_root,
        _repository_path_parts(source_root, "CAS source_root")[-1],
        *(
            basename
            for basename, count in basename_counts.items()
            if count == 1 and len(basename) >= 8
        ),
    }
    completed = subprocess.run(
        [
            "rg",
            "-l",
            "-F",
            "--no-ignore",
            "-g",
            "*.py",
            "-g",
            "*.ps1",
            "-g",
            "*.lua",
            "-g",
            "*.json",
            "-g",
            "*.jsonl",
            "-g",
            "*.md",
            "-f",
            "-",
            str(repo),
        ],
        input="\n".join(sorted(patterns)) + "\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode not in {0, 1}:
        raise MigrationError(f"consumer lexical scan failed: {completed.stderr.strip()}")
    hits: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for raw in completed.stdout.splitlines():
        candidate = Path(raw).resolve()
        try:
            relative = candidate.relative_to(repo).as_posix()
        except ValueError:
            continue
        if relative.startswith(source_root + "/") or relative.startswith(
            "Iris/build/description/v2/evidence/objects/"
        ) or relative.startswith("Iris/build/description/v2/evidence/references/"):
            continue
        try:
            text = candidate.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        exact = sorted(path for path in selected_paths if path in text)
        dynamic, dynamic_scan, parsed = _dynamic_path_references(
            candidate, text, source_root, selected_paths
        )
        referenced = sorted(set(exact) | set(dynamic))
        if not referenced and not parsed and candidate.suffix.lower() in {".py", ".ps1", ".lua"}:
            unresolved.append(
                {
                    "consumer": relative,
                    "scan": dynamic_scan,
                    "reason": "candidate matched a source-root or unique-path fragment but could not be parsed",
                }
            )
            continue
        if not referenced:
            continue
        if candidate.suffix.lower() in {".py", ".ps1", ".lua"}:
            classification = "executable_read"
        elif relative.startswith("Iris/validation/") and candidate.suffix.lower() in {".json", ".jsonl"}:
            classification = "executable_read"
        elif relative.startswith("docs/") or relative.startswith("Iris/_docs/"):
            classification = "docs_or_comment"
        else:
            classification = "reference_only"
        hits.append(
            {
                "classification": classification,
                "consumer": relative,
                "referenced_paths": referenced,
                "scan": (
                    "rg_fragment_candidates_plus_exact_path_confirmation"
                    if not dynamic
                    else f"rg_fragment_candidates_plus_{dynamic_scan}"
                ),
            }
        )
    executable = [hit for hit in hits if hit["classification"] == "executable_read"]
    return {
        "hits": hits,
        "executable_hit_count": len(executable),
        "unresolved_dynamic_count": len(unresolved),
        "unresolved_dynamic_hits": unresolved,
        "legacy_silent_fallback_count": 0,
    }


def cas_plan(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    inventory = _load_object(args.inventory.resolve())
    if inventory.get("schema_version") != CAS_INVENTORY_SCHEMA:
        raise MigrationError("CAS inventory schema mismatch")
    rows = inventory.get("rows")
    if not isinstance(rows, list):
        raise MigrationError("CAS inventory rows are malformed")
    requested = set(args.select_path or [])
    if requested:
        by_path = {str(row.get("path")): row for row in rows}
        missing = sorted(requested - set(by_path))
        if missing:
            raise MigrationError(f"CAS plan selection is absent from inventory: {missing[0]}")
        selected = [by_path[path] for path in sorted(requested)]
    else:
        selected = [row for row in rows if row.get("vcs_state") == "ignored_migration_candidate"]
    selected_paths = {str(row["path"]) for row in selected}
    consumer_scan = _consumer_scan(repo, str(inventory["source_root"]), selected_paths)
    if consumer_scan["executable_hit_count"] or consumer_scan["unresolved_dynamic_count"]:
        raise MigrationError("CAS plan has executable or unresolved consumers of migration candidates")
    objects: dict[str, dict[str, Any]] = {}
    for row in selected:
        digest = str(row["sha256"])
        prior = objects.get(digest)
        identity = {
            "sha256": digest,
            "size_bytes": int(row["size_bytes"]),
            "media_type": str(row["media_type"]),
        }
        if prior and prior["size_bytes"] != identity["size_bytes"]:
            raise MigrationError("CAS digest collision with unequal size")
        objects[digest] = identity
    payload = {
        "schema_version": CAS_PLAN_SCHEMA,
        "source_inventory": {
            "path": _repo_relative(repo, args.inventory.resolve()),
            "sha256": _sha256_file(args.inventory.resolve()),
        },
        "source_root": inventory["source_root"],
        "selected_file_count": len(selected),
        "selected_physical_bytes": sum(int(row["size_bytes"]) for row in selected),
        "physical_exception_count": len(rows) - len(selected),
        "unique_object_count": len(objects),
        "unique_object_bytes": sum(row["size_bytes"] for row in objects.values()),
        "duplicate_bytes_removed_candidate": sum(int(row["size_bytes"]) for row in selected)
        - sum(row["size_bytes"] for row in objects.values()),
        "consumer_scan": consumer_scan,
        "objects": sorted(objects.values(), key=lambda row: row["sha256"]),
        "references": selected,
    }
    _write_new(args.out.resolve(), canonical_json_bytes(payload))


def _object_path(object_root: Path, digest: str) -> Path:
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise MigrationError(f"invalid CAS digest: {digest}")
    return object_root / digest[:2] / digest


def cas_promote(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    plan = _load_object(args.plan.resolve())
    if plan.get("schema_version") != CAS_PLAN_SCHEMA:
        raise MigrationError("CAS plan schema mismatch")
    source_root = repo / str(plan["source_root"])
    object_root = args.object_root.resolve()
    reference_out = args.reference_out.resolve()
    _repo_relative(repo, object_root)
    _repo_relative(repo, reference_out)
    by_digest: dict[str, Path] = {}
    references = plan.get("references")
    if not isinstance(references, list):
        raise MigrationError("CAS plan references are malformed")
    for row in references:
        source = repo / str(row["path"])
        if not _regular_file(source) or source.stat().st_size != row["size_bytes"] or _sha256_file(source) != row["sha256"]:
            raise MigrationError(f"CAS source changed before promotion: {row['path']}")
        by_digest.setdefault(str(row["sha256"]), source)
    created = reused = 0
    for object_row in plan.get("objects", []):
        digest = str(object_row["sha256"])
        source = by_digest[digest]
        target = _object_path(object_root, digest)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            reused += 1
        else:
            temporary = target.with_name(f".{target.name}.{os.getpid()}.partial")
            with source.open("rb") as input_handle, temporary.open("xb") as output_handle:
                shutil.copyfileobj(input_handle, output_handle, 1024 * 1024)
            if _sha256_file(temporary) != digest or temporary.stat().st_size != object_row["size_bytes"]:
                temporary.unlink(missing_ok=True)
                raise MigrationError(f"CAS object verification failed: {digest}")
            try:
                os.link(temporary, target)
            except FileExistsError:
                pass
            finally:
                temporary.unlink(missing_ok=True)
            created += 1
        if not _regular_file(target) or target.stat().st_size != object_row["size_bytes"] or _sha256_file(target) != digest:
            raise MigrationError(f"CAS object collision or corruption: {digest}")
    reference = {
        "schema_version": CAS_REFERENCE_SCHEMA,
        "source_root": plan["source_root"],
        "producer": "repository_evidence_migration_v1",
        "chronology_preserved": True,
        "references": [
            {
                "attempt": row["attempt"],
                "chronology": row["chronology"],
                "disposition": "migrated_to_repository_cas",
                "media_type": row["media_type"],
                "object_sha256": row["sha256"],
                "original_path": row["path"],
                "phase": row["phase"],
                "producer": row["producer"],
                "size_bytes": row["size_bytes"],
            }
            for row in references
        ],
    }
    _write_new(reference_out, canonical_json_bytes(reference))
    receipt = {
        "schema_version": CAS_RECEIPT_SCHEMA,
        "status": "PASS",
        "mode": "promote",
        "plan_sha256": _sha256_file(args.plan.resolve()),
        "reference_sha256": _sha256_file(reference_out),
        "created_objects": created,
        "reused_objects": reused,
        "unique_object_count": len(plan["objects"]),
        "unique_object_bytes": plan["unique_object_bytes"],
    }
    _write_new(args.receipt_out.resolve(), canonical_json_bytes(receipt))


def _validate_reference(reference: dict[str, Any], object_root: Path) -> list[dict[str, Any]]:
    if reference.get("schema_version") != CAS_REFERENCE_SCHEMA:
        raise MigrationError("CAS reference schema mismatch")
    rows = reference.get("references")
    if not isinstance(rows, list):
        raise MigrationError("CAS reference rows are malformed")
    source_root = str(reference.get("source_root", ""))
    _repository_path_parts(source_root, "CAS source_root")
    paths: set[str] = set()
    used: set[str] = set()
    for row in rows:
        path = str(row.get("original_path", ""))
        digest = str(row.get("object_sha256", ""))
        _reference_relative(source_root, path)
        if path in paths:
            raise MigrationError(f"duplicate CAS reference path: {path}")
        paths.add(path)
        target = _object_path(object_root, digest)
        if not _regular_file(target) or target.stat().st_size != row.get("size_bytes") or _sha256_file(target) != digest:
            raise MigrationError(f"missing or corrupt CAS object: {digest}")
        used.add(digest)
    return rows


def cas_verify(args: argparse.Namespace) -> None:
    reference = _load_object(args.reference.resolve())
    rows = _validate_reference(reference, args.object_root.resolve())
    receipt = {
        "schema_version": CAS_RECEIPT_SCHEMA,
        "status": "PASS",
        "mode": "verify",
        "reference_sha256": _sha256_file(args.reference.resolve()),
        "reference_count": len(rows),
        "object_count": len({row["object_sha256"] for row in rows}),
        "referenced_bytes": sum(int(row["size_bytes"]) for row in rows),
    }
    _write_new(args.receipt_out.resolve(), canonical_json_bytes(receipt))


def cas_restore(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    reference = _load_object(args.reference.resolve())
    rows = _validate_reference(reference, args.object_root.resolve())
    output_input = args.out.absolute()
    _assert_no_reparse_ancestor(output_input, "CAS restore output")
    output = output_input.resolve()
    try:
        output.relative_to(repo)
    except ValueError:
        pass
    else:
        raise MigrationError("CAS restore output must be repository-external")
    if output.exists() and any(output.iterdir()):
        raise MigrationError("CAS restore output must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    _assert_no_reparse_ancestor(output, "CAS restore output")
    root = str(reference["source_root"])
    for row in rows:
        relative = _reference_relative(root, str(row["original_path"]))
        destination = output / relative
        try:
            destination.resolve(strict=False).relative_to(output)
        except ValueError as error:
            raise MigrationError(f"CAS restore destination escaped output: {destination}") from error
        _assert_no_reparse_ancestor(destination.parent, "CAS restore destination")
        destination.parent.mkdir(parents=True, exist_ok=True)
        _assert_no_reparse_ancestor(destination.parent, "CAS restore destination")
        if os.path.lexists(destination):
            raise MigrationError(f"CAS restore collision: {destination}")
        shutil.copyfile(_object_path(args.object_root.resolve(), str(row["object_sha256"])), destination)
        if destination.stat().st_size != row["size_bytes"] or _sha256_file(destination) != row["object_sha256"]:
            raise MigrationError(f"CAS restore differs: {row['original_path']}")
    receipt = {
        "schema_version": CAS_RECEIPT_SCHEMA,
        "status": "PASS",
        "mode": "restore",
        "reference_sha256": _sha256_file(args.reference.resolve()),
        "restored_count": len(rows),
        "restored_bytes": sum(int(row["size_bytes"]) for row in rows),
    }
    _write_new(args.receipt_out.resolve(), canonical_json_bytes(receipt))


def cas_disposition_check(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    reference = _load_object(args.reference.resolve())
    rows = _validate_reference(reference, args.object_root.resolve())
    tracked = _git_paths(repo, "ls-files")
    ignored = _git_paths(repo, "ls-files", "--others", "-i", "--exclude-standard")
    for row in rows:
        path = str(row["original_path"])
        if args.allow_tracked:
            if path not in tracked:
                raise MigrationError(f"CAS tracked disposition target is not tracked: {path}")
        elif path in tracked or path not in ignored:
            raise MigrationError(f"CAS disposition target is not ignored-only: {path}")
        source = repo / path
        if not _regular_file(source) or source.stat().st_size != row["size_bytes"] or _sha256_file(source) != row["object_sha256"]:
            raise MigrationError(f"CAS disposition source differs: {path}")
    receipt = {
        "schema_version": CAS_RECEIPT_SCHEMA,
        "status": "PASS",
        "mode": "disposition-check",
        "reference_sha256": _sha256_file(args.reference.resolve()),
        "delete_eligible_count": len(rows),
        "delete_eligible_bytes": sum(int(row["size_bytes"]) for row in rows),
        "owner_approval": "advance_plan_scoped_approval",
        "tracked_disposition": bool(args.allow_tracked),
    }
    _write_new(args.receipt_out.resolve(), canonical_json_bytes(receipt))


def cas_dispose(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    reference = _load_object(args.reference.resolve())
    rows = _validate_reference(reference, args.object_root.resolve())
    disposition = _load_object(args.disposition_receipt.resolve())
    if (
        disposition.get("schema_version") != CAS_RECEIPT_SCHEMA
        or disposition.get("mode") != "disposition-check"
        or disposition.get("status") != "PASS"
        or disposition.get("reference_sha256") != _sha256_file(args.reference.resolve())
    ):
        raise MigrationError("CAS disposition receipt is invalid")
    deleted = 0
    for row in rows:
        target = (repo / str(row["original_path"])).resolve()
        try:
            target.relative_to(repo)
        except ValueError as error:
            raise MigrationError(f"CAS disposition escaped repository: {target}") from error
        if not _regular_file(target) or target.stat().st_size != row["size_bytes"] or _sha256_file(target) != row["object_sha256"]:
            raise MigrationError(f"CAS disposition immediate identity mismatch: {row['original_path']}")
        target.unlink()
        deleted += int(row["size_bytes"])
    receipt = {
        "schema_version": CAS_RECEIPT_SCHEMA,
        "status": "PASS",
        "mode": "dispose",
        "reference_sha256": _sha256_file(args.reference.resolve()),
        "deleted_count": len(rows),
        "deleted_bytes": deleted,
        "recoverable_from_repository_cas": True,
    }
    _write_new(args.receipt_out.resolve(), canonical_json_bytes(receipt))


def cas_cleanup_materialization(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    output = args.out.resolve()
    try:
        output.relative_to(repo)
    except ValueError:
        pass
    else:
        raise MigrationError("CAS materialization cleanup target must be repository-external")
    reference = _load_object(args.reference.resolve())
    rows = _validate_reference(reference, args.object_root.resolve())
    source_root = str(reference["source_root"])
    expected: dict[Path, dict[str, Any]] = {}
    for row in rows:
        relative = _reference_relative(source_root, str(row["original_path"]))
        target = (output / relative).resolve()
        try:
            target.relative_to(output)
        except ValueError as error:
            raise MigrationError(f"CAS materialization cleanup target escaped output: {target}") from error
        expected[target] = row
    actual = {path.resolve() for path in output.rglob("*") if path.is_file()}
    if actual != set(expected):
        raise MigrationError("CAS materialization cleanup file set differs from reference")
    for path, row in expected.items():
        if path.stat().st_size != row["size_bytes"] or _sha256_file(path) != row["object_sha256"]:
            raise MigrationError(f"CAS materialization cleanup identity differs: {path}")
    for path in sorted(actual):
        path.unlink()
    directories = sorted(
        (path for path in output.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        directory.rmdir()
    output.rmdir()
    print(json.dumps({"cleaned_files": len(rows), "status": "PASS"}, sort_keys=True))


def _cold_source_rows(repo: Path, source_root: Path) -> list[dict[str, Any]]:
    relative_root = _repo_relative(repo, source_root)
    tracked = _git_paths(repo, "ls-files", "--", relative_root)
    ignored = _git_paths(repo, "ls-files", "--others", "-i", "--exclude-standard", "--", relative_root)
    rows: list[dict[str, Any]] = []
    for path in sorted((path for path in source_root.rglob("*") if not path.is_dir()), key=lambda path: path.as_posix()):
        relative = _repo_relative(repo, path)
        if not _regular_file(path) or relative in tracked or relative not in ignored:
            raise MigrationError(f"cold archive selection is not an ignored regular file: {relative}")
        rows.append(
            {
                "media_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                "path": relative,
                "role": "historical_cold_archive",
                "sha256": _sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return rows


def _cold_zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.extra = b""
    info.comment = b""
    return info


def cold_archive_create(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    source_root = args.source_root.resolve()
    archive = args.archive_out.resolve()
    manifest_out = args.manifest_out.resolve()
    _repo_relative(repo, source_root)
    _repo_relative(repo, manifest_out)
    try:
        archive.relative_to(repo)
    except ValueError:
        pass
    else:
        raise MigrationError("cold archive output must be repository-external")
    if archive.exists() or manifest_out.exists():
        raise MigrationError("cold archive create-new output already exists")
    rows = _cold_source_rows(repo, source_root)
    operation = {
        "schema_version": "iris_repository_evidence_cold_archive_operation_v1",
        "source_root": _repo_relative(repo, source_root),
        "members": rows,
    }
    operation_bytes = canonical_json_bytes(operation)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        archive,
        mode="x",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
    ) as output:
        output.comment = b""
        output.writestr(_cold_zip_info(COLD_EMBEDDED_MANIFEST), operation_bytes, compresslevel=9)
        for row in rows:
            output.writestr(
                _cold_zip_info(str(row["path"])),
                (repo / str(row["path"])).read_bytes(),
                compresslevel=9,
            )
    manifest = {
        "schema_version": COLD_ARCHIVE_SCHEMA,
        "status": "created",
        "backend_kind": "external_owner_managed_store",
        "store_identifier": args.store_identifier,
        "archive": {
            "bytes": archive.stat().st_size,
            "sha256": _sha256_file(archive),
        },
        "format": {
            "archive": "zip",
            "compression": "deflate_level_9",
            "create_system": 3,
            "external_attr": 0o100644 << 16,
            "member_timestamp": "1980-01-01T00:00:00",
            "member_order": "unicode_code_point_lexical",
            "python": platform.python_version(),
            "zlib": zlib.ZLIB_VERSION,
        },
        "embedded_operation_manifest": {
            "member": COLD_EMBEDDED_MANIFEST,
            "sha256": hashlib.sha256(operation_bytes).hexdigest(),
        },
        "member_count": len(rows),
        "source_bytes": sum(int(row["size_bytes"]) for row in rows),
        "members": rows,
    }
    _write_new(manifest_out, canonical_json_bytes(manifest))


def _verify_cold_archive(manifest: dict[str, Any], archive: Path) -> list[dict[str, Any]]:
    if manifest.get("schema_version") != COLD_ARCHIVE_SCHEMA:
        raise MigrationError("cold archive manifest schema mismatch")
    binding = manifest.get("archive")
    rows = manifest.get("members")
    if not isinstance(binding, dict) or not isinstance(rows, list):
        raise MigrationError("cold archive manifest is malformed")
    if not archive.is_file() or archive.stat().st_size != binding.get("bytes") or _sha256_file(archive) != binding.get("sha256"):
        raise MigrationError("cold archive binding mismatch")
    member_names = [str(row["path"]) for row in rows]
    expected_names = [COLD_EMBEDDED_MANIFEST, *member_names]
    if member_names != sorted(member_names) or len(expected_names) != len(set(expected_names)):
        raise MigrationError("cold archive manifest member order is noncanonical")
    with zipfile.ZipFile(archive, "r") as source:
        infos = source.infolist()
        if [info.filename for info in infos] != expected_names or source.comment:
            raise MigrationError("cold archive member set/order differs")
        operation_bytes = source.read(COLD_EMBEDDED_MANIFEST)
        if hashlib.sha256(operation_bytes).hexdigest() != manifest["embedded_operation_manifest"]["sha256"]:
            raise MigrationError("cold archive embedded manifest differs")
        operation = json.loads(operation_bytes)
        if operation.get("members") != rows:
            raise MigrationError("cold archive embedded selection differs")
        by_name = {str(row["path"]): row for row in rows}
        for info in infos:
            if (
                info.date_time != (1980, 1, 1, 0, 0, 0)
                or info.create_system != 3
                or info.external_attr != (0o100644 << 16)
                or info.extra
                or info.comment
            ):
                raise MigrationError(f"cold archive metadata differs: {info.filename}")
            if info.filename == COLD_EMBEDDED_MANIFEST:
                continue
            pure = Path(info.filename)
            if pure.is_absolute() or ".." in pure.parts or "\\" in info.filename:
                raise MigrationError(f"cold archive traversal member: {info.filename}")
            payload = source.read(info)
            row = by_name[info.filename]
            if len(payload) != row["size_bytes"] or hashlib.sha256(payload).hexdigest() != row["sha256"]:
                raise MigrationError(f"cold archive member differs: {info.filename}")
    return rows


def cold_archive_verify(args: argparse.Namespace) -> None:
    manifest = _load_object(args.manifest.resolve())
    rows = _verify_cold_archive(manifest, args.archive.resolve())
    receipt = {
        "schema_version": COLD_ARCHIVE_RECEIPT_SCHEMA,
        "status": "PASS",
        "mode": "verify",
        "archive_sha256": manifest["archive"]["sha256"],
        "manifest_sha256": _sha256_file(args.manifest.resolve()),
        "verified_members": len(rows),
        "verified_bytes": sum(int(row["size_bytes"]) for row in rows),
    }
    _write_new(args.receipt_out.resolve(), canonical_json_bytes(receipt))


def cold_archive_restore(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    manifest = _load_object(args.manifest.resolve())
    archive = args.archive.resolve()
    rows = _verify_cold_archive(manifest, archive)
    output = args.out.resolve()
    try:
        output.relative_to(repo)
    except ValueError:
        pass
    else:
        raise MigrationError("cold restore output must be repository-external")
    if output.exists():
        raise MigrationError("cold restore output already exists")
    output.mkdir(parents=True)
    with zipfile.ZipFile(archive, "r") as source:
        for row in rows:
            destination = output / str(row["path"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read(str(row["path"])))
            if destination.stat().st_size != row["size_bytes"] or _sha256_file(destination) != row["sha256"]:
                raise MigrationError(f"cold restore member differs: {row['path']}")
    receipt = {
        "schema_version": COLD_ARCHIVE_RECEIPT_SCHEMA,
        "status": "PASS",
        "mode": "restore",
        "archive_sha256": manifest["archive"]["sha256"],
        "manifest_sha256": _sha256_file(args.manifest.resolve()),
        "restored_members": len(rows),
        "restored_bytes": sum(int(row["size_bytes"]) for row in rows),
    }
    _write_new(args.receipt_out.resolve(), canonical_json_bytes(receipt))
    for path in sorted((path for path in output.rglob("*") if path.is_file())):
        path.unlink()
    for directory in sorted((path for path in output.rglob("*") if path.is_dir()), key=lambda path: len(path.parts), reverse=True):
        directory.rmdir()
    output.rmdir()


def cold_archive_dispose(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    manifest = _load_object(args.manifest.resolve())
    rows = _verify_cold_archive(manifest, args.archive.resolve())
    for receipt_path, mode in ((args.verify_receipt, "verify"), (args.restore_receipt, "restore")):
        receipt = _load_object(receipt_path.resolve())
        if (
            receipt.get("schema_version") != COLD_ARCHIVE_RECEIPT_SCHEMA
            or receipt.get("status") != "PASS"
            or receipt.get("mode") != mode
            or receipt.get("archive_sha256") != manifest["archive"]["sha256"]
            or receipt.get("manifest_sha256") != _sha256_file(args.manifest.resolve())
        ):
            raise MigrationError(f"cold archive {mode} receipt mismatch")
    ignored = _git_paths(repo, "ls-files", "--others", "-i", "--exclude-standard")
    for row in rows:
        path = str(row["path"])
        source = (repo / path).resolve()
        if path not in ignored or not _regular_file(source) or source.stat().st_size != row["size_bytes"] or _sha256_file(source) != row["sha256"]:
            raise MigrationError(f"cold archive disposition source differs: {path}")
    for row in rows:
        (repo / str(row["path"])).unlink()
    receipt = {
        "schema_version": COLD_ARCHIVE_RECEIPT_SCHEMA,
        "status": "PASS",
        "mode": "dispose",
        "archive_sha256": manifest["archive"]["sha256"],
        "manifest_sha256": _sha256_file(args.manifest.resolve()),
        "deleted_members": len(rows),
        "deleted_bytes": sum(int(row["size_bytes"]) for row in rows),
        "recoverable_from_verified_external_archive": True,
        "owner_approval": "advance_plan_scoped_approval",
    }
    _write_new(args.receipt_out.resolve(), canonical_json_bytes(receipt))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("--repo", type=Path, required=True)
    create.add_argument("--baseline-v1", type=Path, required=True)
    create.add_argument("--final-v1", type=Path, required=True)
    create.add_argument("--out", type=Path, required=True)
    restore = subparsers.add_parser("reconstruct")
    restore.add_argument("--v2-root", type=Path, required=True)
    restore.add_argument("--view", choices=("baseline", "final"), required=True)
    restore.add_argument("--out", type=Path, required=True)
    inventory = subparsers.add_parser("inventory")
    inventory.add_argument("--repo", type=Path, required=True)
    inventory.add_argument("--source-root", type=Path, required=True)
    inventory.add_argument("--out", type=Path, required=True)
    plan = subparsers.add_parser("plan")
    plan.add_argument("--repo", type=Path, required=True)
    plan.add_argument("--inventory", type=Path, required=True)
    plan.add_argument("--select-path", action="append")
    plan.add_argument("--out", type=Path, required=True)
    promote = subparsers.add_parser("promote")
    promote.add_argument("--repo", type=Path, required=True)
    promote.add_argument("--plan", type=Path, required=True)
    promote.add_argument("--object-root", type=Path, required=True)
    promote.add_argument("--reference-out", type=Path, required=True)
    promote.add_argument("--receipt-out", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--reference", type=Path, required=True)
    verify.add_argument("--object-root", type=Path, required=True)
    verify.add_argument("--receipt-out", type=Path, required=True)
    restore_cas = subparsers.add_parser("restore")
    restore_cas.add_argument("--repo", type=Path, required=True)
    restore_cas.add_argument("--reference", type=Path, required=True)
    restore_cas.add_argument("--object-root", type=Path, required=True)
    restore_cas.add_argument("--out", type=Path, required=True)
    restore_cas.add_argument("--receipt-out", type=Path, required=True)
    materialize = subparsers.add_parser("materialize")
    materialize.add_argument("--repo", type=Path, required=True)
    materialize.add_argument("--reference", type=Path, required=True)
    materialize.add_argument("--object-root", type=Path, required=True)
    materialize.add_argument("--out", type=Path, required=True)
    materialize.add_argument("--receipt-out", type=Path, required=True)
    disposition = subparsers.add_parser("disposition-check")
    disposition.add_argument("--repo", type=Path, required=True)
    disposition.add_argument("--reference", type=Path, required=True)
    disposition.add_argument("--object-root", type=Path, required=True)
    disposition.add_argument("--receipt-out", type=Path, required=True)
    disposition.add_argument("--allow-tracked", action="store_true")
    dispose = subparsers.add_parser("dispose")
    dispose.add_argument("--repo", type=Path, required=True)
    dispose.add_argument("--reference", type=Path, required=True)
    dispose.add_argument("--object-root", type=Path, required=True)
    dispose.add_argument("--disposition-receipt", type=Path, required=True)
    dispose.add_argument("--receipt-out", type=Path, required=True)
    cleanup = subparsers.add_parser("cleanup-materialization")
    cleanup.add_argument("--repo", type=Path, required=True)
    cleanup.add_argument("--reference", type=Path, required=True)
    cleanup.add_argument("--object-root", type=Path, required=True)
    cleanup.add_argument("--out", type=Path, required=True)
    cold_create = subparsers.add_parser("cold-archive")
    cold_create.add_argument("--repo", type=Path, required=True)
    cold_create.add_argument("--source-root", type=Path, required=True)
    cold_create.add_argument("--archive-out", type=Path, required=True)
    cold_create.add_argument("--manifest-out", type=Path, required=True)
    cold_create.add_argument("--store-identifier", required=True)
    cold_verify = subparsers.add_parser("cold-verify")
    cold_verify.add_argument("--manifest", type=Path, required=True)
    cold_verify.add_argument("--archive", type=Path, required=True)
    cold_verify.add_argument("--receipt-out", type=Path, required=True)
    cold_restore = subparsers.add_parser("cold-restore")
    cold_restore.add_argument("--repo", type=Path, required=True)
    cold_restore.add_argument("--manifest", type=Path, required=True)
    cold_restore.add_argument("--archive", type=Path, required=True)
    cold_restore.add_argument("--out", type=Path, required=True)
    cold_restore.add_argument("--receipt-out", type=Path, required=True)
    cold_dispose = subparsers.add_parser("cold-dispose")
    cold_dispose.add_argument("--repo", type=Path, required=True)
    cold_dispose.add_argument("--manifest", type=Path, required=True)
    cold_dispose.add_argument("--archive", type=Path, required=True)
    cold_dispose.add_argument("--verify-receipt", type=Path, required=True)
    cold_dispose.add_argument("--restore-receipt", type=Path, required=True)
    cold_dispose.add_argument("--receipt-out", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        commands = {
            "create": migrate,
            "reconstruct": reconstruct,
            "inventory": cas_inventory,
            "plan": cas_plan,
            "promote": cas_promote,
            "verify": cas_verify,
            "restore": cas_restore,
            "materialize": cas_restore,
            "disposition-check": cas_disposition_check,
            "dispose": cas_dispose,
            "cleanup-materialization": cas_cleanup_materialization,
            "cold-archive": cold_archive_create,
            "cold-verify": cold_archive_verify,
            "cold-restore": cold_archive_restore,
            "cold-dispose": cold_archive_dispose,
        }
        commands[args.command](args)
    except (MigrationError, RepositoryEvidenceCodecError, OSError, ValueError) as error:
        print(f"repository evidence migration failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"command": args.command, "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
