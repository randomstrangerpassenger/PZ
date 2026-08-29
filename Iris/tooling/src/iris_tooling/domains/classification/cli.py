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
LAYER2_MANIFEST_NAME = "classification_layer2_candidate_manifest.json"
LAYER2_MANIFEST_SCHEMA = "iris.classification-layer2-candidate.v1"
LAYER2_OUTPUT_NAME = "classification_layer2_owner_output.json"
LAYER2_SOURCE_ROLE = "classification_owner_output_candidate"
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


def _layer2_manifest(candidate_root: Path) -> Path:
    from iris_tooling.domains.classification.layer2_contract import (
        ABSENCE_REGISTRY,
        OUTPUT_SCHEMA,
        RESOLUTION_CONTRACT,
        RESOLUTION_REGISTRY,
        SURFACE_CATALOG,
        canonical_bytes,
    )

    # The configured repository context is explicit; the manifest binds only
    # owner inputs, never run-local paths.
    repository_root = require_repository_context().repository_root
    source_paths = (
        RESOLUTION_CONTRACT,
        OUTPUT_SCHEMA,
        ABSENCE_REGISTRY,
        RESOLUTION_REGISTRY,
        SURFACE_CATALOG,
    )
    output = candidate_root / LAYER2_OUTPUT_NAME
    payload = {
        "schema": LAYER2_MANIFEST_SCHEMA,
        "source_role": LAYER2_SOURCE_ROLE,
        "target_relative_path": "Iris/build/classification/data/classification_layer2_owner_output.json",
        "output_sha256": _sha256(output),
        "source_sha256": {
            path.as_posix(): _sha256(repository_root / path)
            for path in source_paths
        },
    }
    path = candidate_root / LAYER2_MANIFEST_NAME
    path.write_bytes(canonical_bytes(payload))
    return path


def build_layer2_owner(candidate_root: Path) -> int:
    from iris_tooling.domains.classification.layer2_materializer import write_output
    from iris_tooling.domains.classification.layer2_validator import validate_owner_output

    root = _external_root(candidate_root, "--output-root", create=True)
    if any(root.iterdir()):
        raise SystemExit(f"--output-root must be empty: {root}")
    repository_root = require_repository_context().repository_root
    output = root / LAYER2_OUTPUT_NAME
    write_output(repository_root, output)
    report = validate_owner_output(repository_root, output)
    manifest = _layer2_manifest(root)
    print(
        "classification Layer 2 candidate PASS "
        f"status={report['status']} resolved={report['resolved_entry_count']} "
        f"remaining={report['remaining_entry_count']} manifest_sha256={_sha256(manifest)}"
    )
    return 0


def _load_layer2_manifest(candidate_root: Path, expected_sha256: str) -> dict[str, Any]:
    from iris_tooling.domains.classification.layer2_contract import (
        ABSENCE_REGISTRY,
        OUTPUT_SCHEMA,
        RESOLUTION_CONTRACT,
        RESOLUTION_REGISTRY,
        SURFACE_CATALOG,
    )

    if re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise SystemExit("--manifest-sha256 must be 64 lowercase hexadecimal characters")
    manifest_path = candidate_root / LAYER2_MANIFEST_NAME
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise SystemExit("Layer 2 candidate manifest is missing or unsafe")
    if _sha256(manifest_path) != expected_sha256:
        raise SystemExit("Layer 2 candidate manifest hash mismatch")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SystemExit(f"Layer 2 candidate manifest is invalid: {exc}") from exc
    if payload.get("schema") != LAYER2_MANIFEST_SCHEMA or payload.get("source_role") != LAYER2_SOURCE_ROLE:
        raise SystemExit("Layer 2 candidate manifest authority fields are invalid")
    if {path.name for path in candidate_root.iterdir()} != {LAYER2_OUTPUT_NAME, LAYER2_MANIFEST_NAME}:
        raise SystemExit("Layer 2 candidate directory contains an unexpected file set")
    output = candidate_root / LAYER2_OUTPUT_NAME
    if not output.is_file() or output.is_symlink() or output.resolve().parent != candidate_root:
        raise SystemExit("Layer 2 candidate output is missing or unsafe")
    if payload.get("output_sha256") != _sha256(output):
        raise SystemExit("Layer 2 candidate output hash mismatch")
    if payload.get("target_relative_path") != "Iris/build/classification/data/classification_layer2_owner_output.json":
        raise SystemExit("Layer 2 candidate target is invalid")
    source_sha256 = payload.get("source_sha256")
    source_paths = (
        RESOLUTION_CONTRACT,
        OUTPUT_SCHEMA,
        ABSENCE_REGISTRY,
        RESOLUTION_REGISTRY,
        SURFACE_CATALOG,
    )
    expected_source_keys = {path.as_posix() for path in source_paths}
    if not isinstance(source_sha256, dict) or set(source_sha256) != expected_source_keys:
        raise SystemExit("Layer 2 candidate source binding is invalid")
    repository_root = require_repository_context().repository_root
    for path in source_paths:
        if source_sha256[path.as_posix()] != _sha256(repository_root / path):
            raise SystemExit(f"Layer 2 candidate source hash mismatch: {path.as_posix()}")
    return payload


def validate_layer2_owner(candidate_root: Path, expected_manifest_sha256: str) -> int:
    from iris_tooling.domains.classification.layer2_validator import validate_owner_output

    root = _external_root(candidate_root, "--candidate-root")
    _load_layer2_manifest(root, expected_manifest_sha256)
    report = validate_owner_output(
        require_repository_context().repository_root,
        root / LAYER2_OUTPUT_NAME,
    )
    print(
        "classification Layer 2 validation PASS "
        f"status={report['status']} resolved={report['resolved_entry_count']} "
        f"remaining={report['remaining_entry_count']}"
    )
    return 0


def install_layer2_owner(
    candidate_root: Path,
    expected_manifest_sha256: str,
    *,
    output_path: Path | None = None,
) -> int:
    from iris_tooling.domains.classification.layer2_validator import validate_owner_output

    root = _external_root(candidate_root, "--candidate-root")
    _load_layer2_manifest(root, expected_manifest_sha256)
    validate_owner_output(
        require_repository_context().repository_root,
        root / LAYER2_OUTPUT_NAME,
    )
    if output_path is None:
        output_path = (
            require_repository_context().repository_root
            / "Iris/build/classification/data/classification_layer2_owner_output.json"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output_path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write((root / LAYER2_OUTPUT_NAME).read_bytes())
    try:
        os.replace(temporary, output_path)
    finally:
        temporary.unlink(missing_ok=True)
    print("classification Layer 2 install PASS files=1")
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
    layer2_build = subparsers.add_parser("build-layer2-owner")
    layer2_build.add_argument("--output-root", type=Path, required=True)
    layer2_validate = subparsers.add_parser("validate-layer2-owner")
    layer2_validate.add_argument("--candidate-root", type=Path, required=True)
    layer2_validate.add_argument("--manifest-sha256", required=True)
    layer2_install = subparsers.add_parser("install-layer2-owner")
    layer2_install.add_argument("--candidate-root", type=Path, required=True)
    layer2_install.add_argument("--manifest-sha256", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.action == "build":
        return build(args.output_root)
    if args.action == "install":
        return install(args.candidate_root, args.manifest_sha256)
    if args.action == "build-layer2-owner":
        return build_layer2_owner(args.output_root)
    if args.action == "validate-layer2-owner":
        return validate_layer2_owner(args.candidate_root, args.manifest_sha256)
    return install_layer2_owner(args.candidate_root, args.manifest_sha256)
