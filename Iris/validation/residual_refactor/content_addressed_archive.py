#!/usr/bin/env python
"""Create, verify, and restore the deterministic Iris historical archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


PROFILE = "content_addressed_zip_v2"
SCHEMA = "iris_content_addressed_archive_manifest_v2"
MANIFEST_MEMBER = "manifest.json"
ZIP_DATE = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644


class ArchiveError(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_path(value: object, label: str) -> str:
    text = str(value)
    posix = PurePosixPath(text)
    windows = PureWindowsPath(text)
    if (
        not text
        or "\\" in text
        or posix.is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise ArchiveError(f"{label} is not a canonical repository-relative path: {text}")
    return text


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArchiveError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ArchiveError(f"expected JSON object: {path}")
    return value


def regular_file(path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return not bool(getattr(path.lstat(), "st_file_attributes", 0) & reparse_flag)


def has_link_or_reparse_ancestor(root: Path, target: Path) -> bool:
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    current = root
    for part in target.relative_to(root).parts:
        current = current / part
        if not os.path.lexists(current):
            continue
        metadata = current.lstat()
        if current.is_symlink() or bool(getattr(metadata, "st_file_attributes", 0) & reparse_flag):
            return True
    return False


def git_blob(repository: Path, commit: str, logical_path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repository), "show", f"{commit}:{logical_path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise ArchiveError(f"tracked archive source is unavailable: {logical_path}")
    return result.stdout


def custody_bytes(repository: Path, custody: Path, logical_path: str) -> bytes:
    custody_root = custody.resolve()
    target = custody_root.joinpath(*PurePosixPath(logical_path).parts)
    if (
        not target.is_relative_to(custody_root)
        or has_link_or_reparse_ancestor(custody_root, target)
        or not regular_file(target)
    ):
        raise ArchiveError(f"custody archive source is unsafe or absent: {logical_path}")
    tracked = subprocess.run(
        ["git", "-C", str(repository), "ls-files", "--error-unmatch", "--", logical_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if tracked.returncode == 0:
        raise ArchiveError(f"custody-only source is tracked: {logical_path}")
    return target.read_bytes()


def source_rows(
    repository: Path, commit: str, custody: Path, selection: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    rows = selection.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ArchiveError("archive selection rows must be a nonempty list")
    logical_seen: set[str] = set()
    objects: dict[str, bytes] = {}
    result: list[dict[str, Any]] = []
    for selected in rows:
        if not isinstance(selected, dict):
            raise ArchiveError("archive selection row must be an object")
        logical = canonical_path(selected.get("logical_path"), "logical_path")
        if logical in logical_seen:
            raise ArchiveError(f"duplicate archive logical path: {logical}")
        logical_seen.add(logical)
        domain = selected.get("source_domain")
        if domain == "tracked_git_blob":
            payload = git_blob(repository, commit, logical)
        elif domain == "custody_file":
            payload = custody_bytes(repository, custody, logical)
        else:
            raise ArchiveError(f"unsupported archive source domain: {domain}")
        object_id = sha256(payload)
        expected = selected.get("source_sha256")
        if expected is not None and expected != object_id:
            raise ArchiveError(f"archive selection hash mismatch: {logical}")
        expected_bytes = selected.get("source_bytes")
        if expected_bytes is not None and expected_bytes != len(payload):
            raise ArchiveError(f"archive selection size mismatch: {logical}")
        previous = objects.setdefault(object_id, payload)
        if previous != payload:
            raise ArchiveError(f"SHA-256 object collision: {object_id}")
        result.append(
            {
                "logical_path": logical,
                "object_sha256": object_id,
                "bytes": len(payload),
                "mode": "100644",
                "source_domain": domain,
                "role": str(selected.get("role", "historical_reproduction")),
            }
        )
    return sorted(result, key=lambda row: row["logical_path"]), objects


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = FILE_MODE << 16
    info.flag_bits = 0
    return info


def create_archive(
    repository: Path,
    commit: str,
    custody: Path,
    selection_path: Path,
    archive_path: Path,
    store_identifier: str,
) -> dict[str, Any]:
    if archive_path.exists():
        raise ArchiveError(f"archive output already exists: {archive_path}")
    selection = load_object(selection_path)
    rows, objects = source_rows(repository, commit, custody, selection)
    manifest = {
        "schema_version": SCHEMA,
        "profile": PROFILE,
        "compression": "zip_deflate_level_9",
        "canonical_member_metadata": "dos_epoch_1980_unix_regular_0644",
        "source_commit": commit,
        "selection_sha256": sha256_file(selection_path),
        "logical_file_count": len(rows),
        "logical_source_bytes": sum(row["bytes"] for row in rows),
        "unique_object_count": len(objects),
        "unique_object_bytes": sum(len(value) for value in objects.values()),
        "rows": rows,
    }
    members: dict[str, bytes] = {MANIFEST_MEMBER: canonical_json(manifest)}
    members.update({f"objects/{object_id}": payload for object_id, payload in objects.items()})
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("xb") as output:
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(members):
                archive.writestr(zip_info(name), members[name], compresslevel=9)
    verified = verify_archive(archive_path)
    return {
        "schema_version": "iris_content_addressed_archive_create_receipt_v2",
        "status": "PASS",
        "profile": PROFILE,
        "store_identifier": store_identifier,
        "archive_sha256": sha256_file(archive_path),
        "archive_bytes": archive_path.stat().st_size,
        "manifest_sha256": sha256(members[MANIFEST_MEMBER]),
        **verified,
    }


def verify_archive(archive_path: Path) -> dict[str, Any]:
    if not regular_file(archive_path):
        raise ArchiveError("archive is absent or not a regular file")
    with zipfile.ZipFile(archive_path, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if names != sorted(names) or len(names) != len(set(names)) or MANIFEST_MEMBER not in names:
            raise ArchiveError("archive member order, uniqueness, or manifest is invalid")
        for info in infos:
            canonical_path(info.filename, "archive member")
            if (
                info.date_time != ZIP_DATE
                or info.compress_type != zipfile.ZIP_DEFLATED
                or info.create_system != 3
                or info.external_attr >> 16 != FILE_MODE
            ):
                raise ArchiveError(f"archive member metadata mismatch: {info.filename}")
        manifest_raw = archive.read(MANIFEST_MEMBER)
        manifest = json.loads(manifest_raw)
        if manifest.get("schema_version") != SCHEMA or manifest.get("profile") != PROFILE:
            raise ArchiveError("archive manifest schema/profile mismatch")
        rows = manifest.get("rows")
        if not isinstance(rows, list) or rows != sorted(rows, key=lambda row: row["logical_path"]):
            raise ArchiveError("archive logical rows are invalid or noncanonical")
        logical_seen: set[str] = set()
        required_objects: set[str] = set()
        logical_bytes = 0
        for row in rows:
            logical = canonical_path(row.get("logical_path"), "logical path")
            if logical in logical_seen:
                raise ArchiveError(f"duplicate logical path: {logical}")
            logical_seen.add(logical)
            object_id = str(row.get("object_sha256"))
            if len(object_id) != 64 or any(char not in "0123456789abcdef" for char in object_id):
                raise ArchiveError(f"invalid object identity: {object_id}")
            required_objects.add(object_id)
            payload = archive.read(f"objects/{object_id}")
            if sha256(payload) != object_id or len(payload) != row.get("bytes"):
                raise ArchiveError(f"object hash/size mismatch: {object_id}")
            logical_bytes += len(payload)
        actual_objects = {name.removeprefix("objects/") for name in names if name.startswith("objects/")}
        if actual_objects != required_objects:
            raise ArchiveError("archive object set mismatch")
        unique_bytes = sum(len(archive.read(f"objects/{object_id}")) for object_id in actual_objects)
        if (
            manifest.get("logical_file_count") != len(rows)
            or manifest.get("logical_source_bytes") != logical_bytes
            or manifest.get("unique_object_count") != len(actual_objects)
            or manifest.get("unique_object_bytes") != unique_bytes
        ):
            raise ArchiveError("archive manifest count/byte summary mismatch")
    return {
        "logical_file_count": len(rows),
        "logical_source_bytes": logical_bytes,
        "unique_object_count": len(actual_objects),
        "unique_object_bytes": unique_bytes,
        "selection_sha256": manifest["selection_sha256"],
        "source_commit": manifest["source_commit"],
    }


def restore_archive(archive_path: Path, restore_root: Path) -> dict[str, Any]:
    if (
        not restore_root.is_dir()
        or restore_root.is_symlink()
        or has_link_or_reparse_ancestor(restore_root.parent, restore_root)
        or any(restore_root.iterdir())
    ):
        raise ArchiveError("restore root must be an existing empty directory")
    verified = verify_archive(archive_path)
    with zipfile.ZipFile(archive_path, "r") as archive:
        manifest = json.loads(archive.read(MANIFEST_MEMBER))
        for row in manifest["rows"]:
            logical = canonical_path(row["logical_path"], "restore logical path")
            target = (restore_root / logical).resolve()
            if restore_root.resolve() not in target.parents:
                raise ArchiveError(f"restore path escaped root: {logical}")
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                with target.open("xb") as handle:
                    handle.write(archive.read(f"objects/{row['object_sha256']}"))
            except FileExistsError as exc:
                raise ArchiveError(f"restore target already exists: {logical}") from exc
    for row in manifest["rows"]:
        payload = (restore_root / row["logical_path"]).read_bytes()
        if len(payload) != row["bytes"] or sha256(payload) != row["object_sha256"]:
            raise ArchiveError(f"restored file identity mismatch: {row['logical_path']}")
    return {
        "schema_version": "iris_content_addressed_archive_restore_receipt_v2",
        "status": "PASS",
        "archive_sha256": sha256_file(archive_path),
        "restored_file_count": verified["logical_file_count"],
        "restored_bytes": verified["logical_source_bytes"],
        "logical_tree_parity": True,
    }


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(canonical_json(value))
    except FileExistsError as exc:
        raise ArchiveError(f"receipt already exists: {path}") from exc


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--repository-root", type=Path, required=True)
    create.add_argument("--commit", required=True)
    create.add_argument("--custody-root", type=Path, required=True)
    create.add_argument("--selection", type=Path, required=True)
    create.add_argument("--archive", type=Path, required=True)
    create.add_argument("--store-identifier", required=True)
    create.add_argument("--receipt", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--archive", type=Path, required=True)
    verify.add_argument("--receipt", type=Path)
    restore = commands.add_parser("restore")
    restore.add_argument("--archive", type=Path, required=True)
    restore.add_argument("--restore-root", type=Path, required=True)
    restore.add_argument("--receipt", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "create":
            result = create_archive(
                args.repository_root.resolve(),
                args.commit,
                args.custody_root.resolve(),
                args.selection.resolve(),
                args.archive.resolve(),
                args.store_identifier,
            )
            write_new(args.receipt.resolve(), result)
        elif args.command == "verify":
            result = {"schema_version": "iris_content_addressed_archive_verify_receipt_v2", "status": "PASS", "archive_sha256": sha256_file(args.archive.resolve()), **verify_archive(args.archive.resolve())}
            if args.receipt:
                write_new(args.receipt.resolve(), result)
        else:
            result = restore_archive(args.archive.resolve(), args.restore_root.resolve())
            write_new(args.receipt.resolve(), result)
    except (ArchiveError, OSError, json.JSONDecodeError, zipfile.BadZipFile, KeyError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
