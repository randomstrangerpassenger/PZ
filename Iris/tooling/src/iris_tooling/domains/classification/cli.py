from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from iris_tooling.build.repository_context import require_repository_context


MANIFEST_NAME = "classification_candidate_manifest.json"
MANIFEST_SCHEMA = "iris.classification-candidate.v1"
SOURCE_ROLE = "external_classification_candidate"
RUNTIME_RELATIVE_ROOT = Path("Iris/media/lua/client/Iris/Data")
ALLOWED_FILES = (
    "IrisFixingIndexData.lua",
    "IrisMoveablesIndexData.lua",
    "IrisRecipeIndexData.lua",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _external_root(raw_path: Path, label: str, *, create: bool = False) -> Path:
    repository_root = require_repository_context().repository_root.resolve()
    root = raw_path.resolve()
    if root == repository_root or repository_root in root.parents:
        raise SystemExit(f"{label} must resolve outside the repository: {root}")
    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise SystemExit(f"{label} must be a real directory: {root}")
    if create:
        root.mkdir(parents=True, exist_ok=True)
    elif not root.is_dir():
        raise SystemExit(f"{label} does not exist: {root}")
    return root


def _candidate_rows(candidate_root: Path) -> list[dict[str, str]]:
    return [
        {
            "filename": filename,
            "target_relative_path": (RUNTIME_RELATIVE_ROOT / filename).as_posix(),
            "sha256": _sha256(candidate_root / filename),
        }
        for filename in ALLOWED_FILES
    ]


def _write_manifest(candidate_root: Path) -> Path:
    manifest_path = candidate_root / MANIFEST_NAME
    payload = {
        "schema": MANIFEST_SCHEMA,
        "source_role": SOURCE_ROLE,
        "files": _candidate_rows(candidate_root),
    }
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest_path


def build(candidate_root: Path) -> int:
    root = _external_root(candidate_root, "--output-root", create=True)
    if any(root.iterdir()):
        raise SystemExit(f"--output-root must be empty: {root}")

    from iris_tooling.build.build_iris_fixing_index_data import main as build_fixing
    from iris_tooling.build.build_iris_moveables_index_data import main as build_moveables
    from iris_tooling.build.build_iris_recipe_index_data import main as build_recipe

    builders = (
        (build_fixing, root / ALLOWED_FILES[0]),
        (build_moveables, root / ALLOWED_FILES[1]),
        (build_recipe, root / ALLOWED_FILES[2]),
    )
    for command, output in builders:
        result = command(["--output", str(output)])
        if isinstance(result, int) and result != 0:
            return result
    manifest_path = _write_manifest(root)
    print(f"classification candidate PASS manifest_sha256={_sha256(manifest_path)}")
    return 0


def _load_verified_manifest(candidate_root: Path, expected_sha256: str) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise SystemExit("--manifest-sha256 must be 64 lowercase hexadecimal characters")
    manifest_path = candidate_root / MANIFEST_NAME
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise SystemExit(f"candidate manifest is missing or unsafe: {manifest_path}")
    actual_manifest_sha256 = _sha256(manifest_path)
    if actual_manifest_sha256 != expected_sha256:
        raise SystemExit("candidate manifest hash mismatch")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SystemExit(f"candidate manifest is invalid: {exc}") from exc
    if payload.get("schema") != MANIFEST_SCHEMA or payload.get("source_role") != SOURCE_ROLE:
        raise SystemExit("candidate manifest authority fields are invalid")
    actual_names = {path.name for path in candidate_root.iterdir()}
    expected_names = set(ALLOWED_FILES) | {MANIFEST_NAME}
    if actual_names != expected_names:
        raise SystemExit("candidate directory contains an unexpected file set")

    rows = payload.get("files")
    if not isinstance(rows, list) or len(rows) != len(ALLOWED_FILES):
        raise SystemExit("candidate manifest file set is invalid")
    expected_targets = {
        filename: (RUNTIME_RELATIVE_ROOT / filename).as_posix()
        for filename in ALLOWED_FILES
    }
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("candidate manifest row is invalid")
        filename = row.get("filename")
        if filename not in expected_targets or filename in seen:
            raise SystemExit("candidate manifest filename set is invalid")
        if row.get("target_relative_path") != expected_targets[filename]:
            raise SystemExit(f"candidate target is invalid: {filename}")
        source = candidate_root / filename
        if not source.is_file() or source.is_symlink() or source.resolve().parent != candidate_root:
            raise SystemExit(f"candidate source is missing or unsafe: {filename}")
        if row.get("sha256") != _sha256(source):
            raise SystemExit(f"candidate hash mismatch: {filename}")
        seen.add(filename)
    if seen != set(ALLOWED_FILES):
        raise SystemExit("candidate manifest filename set is incomplete")
    return payload


def install(
    candidate_root: Path,
    expected_manifest_sha256: str,
    *,
    runtime_data_root: Path | None = None,
) -> int:
    root = _external_root(candidate_root, "--candidate-root")
    payload = _load_verified_manifest(root, expected_manifest_sha256)
    if runtime_data_root is None:
        runtime_data_root = require_repository_context().repository_root / RUNTIME_RELATIVE_ROOT
    runtime_data_root.mkdir(parents=True, exist_ok=True)

    for row in payload["files"]:
        source = root / row["filename"]
        target = runtime_data_root / row["filename"]
        with tempfile.NamedTemporaryFile(dir=runtime_data_root, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(source.read_bytes())
        try:
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
    print(f"classification install PASS files={len(ALLOWED_FILES)}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iris-tooling classification",
        description="Build external classification candidates or install a hash-bound candidate.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--output-root", type=Path, required=True)
    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("--candidate-root", type=Path, required=True)
    install_parser.add_argument("--manifest-sha256", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.action == "build":
        return build(args.output_root)
    return install(args.candidate_root, args.manifest_sha256)
