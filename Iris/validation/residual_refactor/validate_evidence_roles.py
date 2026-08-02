#!/usr/bin/env python
"""Validate residual-refactor evidence role manifests without external deps."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_ROLES = {"current", "historical", "diagnostic"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def portable_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def validate_manifest(
    manifest: dict[str, Any], *, path: Path, repository_root: Path
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    def fail(code: str, detail: Any = None) -> None:
        row = {"code": code, "manifest": path.relative_to(repository_root).as_posix()}
        if detail is not None:
            row["detail"] = detail
        errors.append(row)

    required = {
        "schema_version",
        "role",
        "created_at",
        "producer",
        "producer_readpoint",
        "command",
        "subject",
        "inputs",
        "outputs",
        "mutable",
        "supersedes",
    }
    missing = sorted(required.difference(manifest))
    if missing:
        fail("missing_required_fields", missing)
        return errors
    if manifest["role"] not in ALLOWED_ROLES:
        fail("invalid_role", manifest["role"])
    if not isinstance(manifest["created_at"], str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        manifest["created_at"],
    ):
        fail("invalid_created_at")
    if not isinstance(manifest["producer"], str) or not manifest["producer"]:
        fail("invalid_producer")
    if not isinstance(manifest["command"], list) or not all(
        isinstance(part, str) and part for part in manifest["command"]
    ):
        fail("invalid_command")
    subject = manifest["subject"]
    if not isinstance(subject, dict):
        fail("invalid_subject")
    else:
        for key in ("commit", "tree"):
            value = subject.get(key)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
                fail("invalid_subject_identity", key)
        overlay = subject.get("overlay_sha256_or_null")
        if overlay is not None and not LOWER_SHA256.fullmatch(str(overlay)):
            fail("invalid_overlay_identity")
    if manifest["mutable"] is not False:
        fail("mutable_bundle_forbidden")
    if manifest["role"] == "diagnostic" and manifest.get("authority_claim") is not False:
        fail("diagnostic_authority_claim_forbidden")
    if manifest.get("index_projection") is True and manifest.get("authority_claim") is not False:
        fail("index_authority_claim_forbidden")

    for collection in ("inputs", "outputs"):
        rows = manifest.get(collection)
        if not isinstance(rows, list):
            fail("invalid_artifact_rows", collection)
            continue
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                fail("invalid_artifact_row", collection)
                continue
            item_path = row.get("path")
            expected_hash = row.get("sha256")
            if not portable_relative_path(item_path):
                fail("invalid_artifact_path", item_path)
                continue
            if item_path in seen:
                fail("duplicate_artifact_path", item_path)
            seen.add(item_path)
            if not LOWER_SHA256.fullmatch(str(expected_hash)):
                fail("invalid_artifact_hash", item_path)
                continue
            full_path = repository_root / item_path
            if row.get("exists", True):
                if not full_path.is_file():
                    fail("artifact_missing", item_path)
                elif sha256_file(full_path) != expected_hash:
                    fail("artifact_hash_mismatch", item_path)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--manifest", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    repository_root = repository_root_for(Path.cwd())
    evidence_root = (
        (repository_root / args.evidence_root).resolve()
        if not args.evidence_root.is_absolute()
        else args.evidence_root.resolve()
    )
    schema_path = (
        (repository_root / args.schema).resolve()
        if args.schema and not args.schema.is_absolute()
        else args.schema.resolve()
        if args.schema
        else evidence_root / "evidence_role.schema.json"
    )
    errors: list[dict[str, Any]] = []
    if not schema_path.is_file():
        errors.append({"code": "schema_missing", "path": str(schema_path)})
    else:
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            if schema.get("$id") != "iris-residual-evidence-role-v1":
                errors.append({"code": "schema_identity_mismatch"})
        except (OSError, json.JSONDecodeError) as error:
            errors.append({"code": "schema_invalid", "detail": str(error)})

    if args.manifest:
        manifests = [
            (repository_root / path).resolve() if not path.is_absolute() else path.resolve()
            for path in args.manifest
        ]
    else:
        manifests = sorted(evidence_root.glob("*.evidence.json"))
    for path in manifests:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append({"code": "manifest_invalid", "path": str(path), "detail": str(error)})
            continue
        if not isinstance(payload, dict):
            errors.append({"code": "manifest_not_object", "path": str(path)})
            continue
        errors.extend(validate_manifest(payload, path=path, repository_root=repository_root))

    report = {
        "schema_version": "iris-residual-evidence-role-validation-v1",
        "validation_status": "passed" if not errors else "failed",
        "schema": schema_path.relative_to(repository_root).as_posix()
        if schema_path.is_relative_to(repository_root)
        else str(schema_path),
        "manifest_count": len(manifests),
        "error_count": len(errors),
        "errors": errors,
    }
    if args.out:
        output = (
            (repository_root / args.out).resolve()
            if not args.out.is_absolute()
            else args.out.resolve()
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
