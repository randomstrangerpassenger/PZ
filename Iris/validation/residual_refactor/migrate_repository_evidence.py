#!/usr/bin/env python
"""Create or reconstruct the lifecycle-manifest v2 evidence bundle."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from repository_evidence_codec import (
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
    source_path = repo / "Iris/validation/residual_refactor/report_inventory.py"
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
        raise MigrationError("report_inventory.py directly references lifecycle v1 artifacts")
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
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "create":
            migrate(args)
        else:
            reconstruct(args)
    except (MigrationError, RepositoryEvidenceCodecError, OSError, ValueError) as error:
        print(f"repository evidence migration failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"command": args.command, "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

