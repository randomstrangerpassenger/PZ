"""Bind checkout, interpreter, installed package and external-output identities."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import site
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


class CleanCheckoutError(RuntimeError):
    """Raised when a clean-checkout contract cannot be satisfied."""


def canonical_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def canonical_compact_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolved_repo(path: str | Path) -> Path:
    repo = Path(path).resolve()
    if not (repo / ".git").exists():
        raise CleanCheckoutError(f"not a Git checkout: {repo}")
    return repo


def ensure_external_root(repo: Path, output_root: str | Path) -> Path:
    root = Path(output_root).resolve()
    try:
        root.relative_to(repo)
    except ValueError:
        pass
    else:
        raise CleanCheckoutError(
            f"output root must be outside the checkout: {root}"
        )
    try:
        repo.relative_to(root)
    except ValueError:
        pass
    else:
        raise CleanCheckoutError(
            f"output root must not contain the checkout: {root}"
        )
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_json_external(repo: Path, path: Path, payload: Any) -> str:
    target = path.resolve()
    try:
        target.relative_to(repo)
    except ValueError:
        pass
    else:
        raise CleanCheckoutError(f"refusing repository-local output: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = canonical_json_bytes(payload)
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_bytes(encoded)
    os.replace(temporary, target)
    return sha256_bytes(encoded)


def git_bytes(repo: Path, *args: str, check: bool = True) -> bytes:
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise CleanCheckoutError(
            f"git {' '.join(args)} failed ({completed.returncode}): {stderr}"
        )
    return completed.stdout


def git_text(repo: Path, *args: str, check: bool = True) -> str:
    return git_bytes(repo, *args, check=check).decode(
        "utf-8", errors="surrogateescape"
    )


def git_identity(repo: Path, commit: str) -> dict[str, str]:
    resolved_commit = git_text(
        repo, "rev-parse", f"{commit}^{{commit}}"
    ).strip()
    tree = git_text(repo, "rev-parse", f"{resolved_commit}^{{tree}}").strip()
    return {"commit": resolved_commit, "tree": tree}


def tracked_paths(repo: Path, commit: str) -> list[str]:
    raw = git_bytes(repo, "ls-tree", "-rz", "--name-only", commit)
    return sorted(
        part.decode("utf-8", errors="surrogateescape")
        for part in raw.split(b"\0")
        if part
    )


def blob_id(repo: Path, commit: str, relative_path: str) -> str:
    return git_text(repo, "rev-parse", f"{commit}:{relative_path}").strip()


def bytes_at_commit(repo: Path, commit: str, relative_path: str) -> bytes:
    return git_bytes(repo, "show", f"{commit}:{relative_path}")


def json_at_commit(repo: Path, commit: str, relative_path: str) -> Any:
    return json.loads(bytes_at_commit(repo, commit, relative_path))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CleanCheckoutError(message)


def _same_path(left: str | Path, right: str | Path) -> bool:
    return os.path.normcase(str(Path(left).resolve())) == os.path.normcase(
        str(Path(right).resolve())
    )


def _environment_file_rows(
    environment_root: Path,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    files = (
        candidate
        for candidate in environment_root.rglob("*")
        if candidate.is_file()
    )
    for path in sorted(
        files,
        key=lambda item: item.relative_to(environment_root).as_posix(),
    ):
        rows.append(
            {
                "path": path.relative_to(environment_root).as_posix(),
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
        )
    return rows


def _distribution_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name")
        _require(
            bool(name),
            f"distribution without Name metadata: {distribution}",
        )
        files: list[dict[str, object]] = []
        for entry in sorted(
            distribution.files or (),
            key=lambda item: item.as_posix(),
        ):
            resolved = Path(distribution.locate_file(entry)).resolve()
            if not resolved.is_file():
                continue
            files.append(
                {
                    "path": entry.as_posix(),
                    "sha256": sha256_file(resolved),
                    "size": resolved.stat().st_size,
                }
            )
        dist_info = Path(distribution._path).resolve()  # noqa: SLF001
        record = dist_info / "RECORD"
        rows.append(
            {
                "name": name,
                "normalized_name": name.lower().replace("-", "_"),
                "version": distribution.version,
                "dist_info": dist_info.name,
                "record_path": (
                    record.relative_to(Path(sys.prefix).resolve()).as_posix()
                    if record.is_file()
                    else None
                ),
                "record_sha256": (
                    sha256_file(record) if record.is_file() else None
                ),
                "installed_file_count": len(files),
                "installed_file_manifest_sha256": hashlib.sha256(
                    canonical_compact_json_bytes(files)
                ).hexdigest(),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            str(row["normalized_name"]),
            str(row["version"]),
        ),
    )


CURRENT_ENVIRONMENT_LOCATOR = "Iris/validation/execution/current_environment.json"


def resolve_current_environment_authority(
    repo: Path,
    subject_commit: str,
) -> dict[str, Any]:
    """Resolve and validate the stable current environment authority."""

    locator_path = repo / CURRENT_ENVIRONMENT_LOCATOR
    locator_bytes = locator_path.read_bytes()
    locator = json.loads(locator_bytes)
    _require(
        locator_bytes == canonical_json_bytes(locator),
        "current environment locator is not canonical JSON",
    )
    _require(
        locator.get("schema_version")
        == "iris-responsibility-refactor-environment-locator-v1",
        "current environment locator schema mismatch",
    )
    record_relative = str(locator.get("record_path", ""))
    record_path = (repo / record_relative).resolve()
    try:
        record_path.relative_to(repo.resolve())
    except ValueError as exc:
        raise CleanCheckoutError("environment authority record escapes repository") from exc
    record_bytes = record_path.read_bytes()
    _require(
        sha256_bytes(record_bytes) == locator.get("record_sha256"),
        "current environment authority record hash mismatch",
    )
    record = json.loads(record_bytes)
    _require(
        record_bytes == canonical_json_bytes(record),
        "environment authority record is not canonical JSON",
    )
    _require(
        record.get("schema_version")
        == "iris-responsibility-refactor-environment-authority-v1",
        "environment authority record schema mismatch",
    )
    implementation = record["implementation"]
    ancestor = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "merge-base",
            "--is-ancestor",
            implementation["commit"],
            subject_commit,
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _require(
        ancestor.returncode == 0,
        "environment implementation commit is not an ancestor of the subject",
    )
    _require(
        git_identity(repo, implementation["commit"])["tree"]
        == implementation["tree"],
        "environment implementation tree mismatch",
    )
    binding = record["project_binding"]
    for path_key, blob_key, sha_key in (
        ("project_path", "project_blob", "project_sha256"),
        ("lock_path", "lock_blob", "lock_sha256"),
    ):
        relative = binding[path_key]
        actual = bytes_at_commit(repo, subject_commit, relative)
        _require(
            blob_id(repo, subject_commit, relative) == binding[blob_key],
            f"current {path_key} blob differs from environment authority",
        )
        _require(
            sha256_bytes(actual) == binding[sha_key],
            f"current {path_key} bytes differ from environment authority",
        )
    source_path = binding["source_package_path"]
    _require(
        blob_id(repo, subject_commit, source_path)
        == binding["source_package_git_tree"],
        "current iris_tooling source tree differs from environment authority",
    )
    wheel_path = Path(binding["wheel_path"])
    _require(wheel_path.is_file(), "environment authority wheel is missing")
    _require(
        sha256_file(wheel_path) == binding["wheel_sha256"],
        "environment authority wheel hash mismatch",
    )
    environment_contract = dict(record["environment_contract"])
    environment_contract["project_binding"] = binding
    return {
        "locator_path": CURRENT_ENVIRONMENT_LOCATOR,
        "locator_sha256": sha256_bytes(locator_bytes),
        "record_path": record_relative,
        "record_sha256": sha256_bytes(record_bytes),
        "record": record,
        "environment_contract": environment_contract,
    }


def validate_external_environment(
    python_executable: Path,
    receipt_path: Path,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """Fail closed unless the running environment matches current authority."""

    python_executable = python_executable.resolve()
    receipt_path = receipt_path.resolve()
    receipt_root = receipt_path.parent
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    actual_receipt_sha256 = sha256_bytes(receipt_bytes)

    _require(
        _same_path(
            receipt_path,
            expected["immutable_environment_receipt_path"],
        ),
        "environment receipt path differs from the current binding",
    )
    _require(
        actual_receipt_sha256
        == expected["immutable_environment_receipt_sha256"],
        "environment receipt hash differs from the current binding",
    )
    _require(
        receipt_bytes == canonical_compact_json_bytes(receipt),
        "environment receipt is not canonical JSON",
    )
    _require(
        receipt.get("schema_version")
        == "iris_clean_checkout_external_environment_receipt_v1",
        "environment receipt schema mismatch",
    )
    if "project_binding" in expected:
        _require(
            receipt.get("project_binding") == expected["project_binding"],
            "environment receipt project binding differs from current authority",
        )
    _require(
        _same_path(sys.executable, python_executable),
        "orchestrator must run under the resolved external interpreter",
    )
    _require(
        sha256_file(python_executable) == expected["interpreter_sha256"],
        "external interpreter hash differs from the current binding",
    )

    environment_root = Path(receipt["environment_root"]).resolve()
    _require(
        _same_path(
            environment_root,
            expected["external_environment_root"],
        ),
        "environment root differs from the current binding",
    )
    _require(
        _same_path(Path(sys.prefix), environment_root),
        f"interpreter prefix mismatch: {sys.prefix}",
    )
    _require(
        not _same_path(Path(sys.base_prefix), environment_root),
        "interpreter is not a dedicated virtual environment",
    )
    interpreter = receipt["interpreter"]
    _require(
        _same_path(python_executable, interpreter["path"]),
        "resolved interpreter path mismatch",
    )
    _require(
        sha256_file(python_executable) == interpreter["sha256"],
        "interpreter hash mismatch",
    )
    _require(
        sha256_file(Path(sys._base_executable).resolve())
        == interpreter["base_interpreter_sha256"],
        "base interpreter hash mismatch",
    )
    _require(
        sys.version == interpreter["python_version"],
        "Python version mismatch",
    )
    _require(
        platform.python_implementation() == interpreter["implementation"],
        "Python implementation mismatch",
    )
    _require(
        platform.architecture()[0] == interpreter["architecture"],
        "Python architecture mismatch",
    )

    isolation = receipt["isolation"]
    _require(
        isolation["dedicated_virtual_environment"] is True,
        "dedicated virtual environment flag is false",
    )
    _require(
        isolation["include_system_site_packages"] is False,
        "system site packages are included",
    )
    _require(
        os.environ.get("PYTHONNOUSERSITE") == "1",
        "PYTHONNOUSERSITE is not 1",
    )
    _require(
        not os.environ.get("PYTHONPATH"),
        "PYTHONPATH is not cleared",
    )
    _require(not site.ENABLE_USER_SITE, "user site is enabled")

    pyvenv_cfg = environment_root / receipt["pyvenv_cfg"]["path"]
    _require(
        sha256_file(pyvenv_cfg) == receipt["pyvenv_cfg"]["sha256"],
        "pyvenv.cfg hash mismatch",
    )
    _require(
        "include-system-site-packages = false"
        in pyvenv_cfg.read_text(encoding="utf-8").lower(),
        "pyvenv.cfg enables system site packages",
    )

    manifest_binding = receipt["environment_content_manifest"]
    manifest_path = receipt_root / manifest_binding["path"]
    manifest_bytes = manifest_path.read_bytes()
    recorded_rows = [
        json.loads(line)
        for line in manifest_bytes.decode("utf-8").splitlines()
        if line
    ]
    current_rows = _environment_file_rows(environment_root)
    _require(
        sha256_bytes(manifest_bytes) == manifest_binding["sha256"],
        "environment content manifest hash mismatch",
    )
    _require(
        manifest_binding["sha256"]
        == expected["environment_content_manifest_sha256"],
        "environment content manifest differs from the current binding",
    )
    _require(
        len(recorded_rows) == manifest_binding["file_count"],
        "environment content manifest count mismatch",
    )
    _require(
        current_rows == recorded_rows,
        "environment contents differ from the immutable manifest",
    )

    current_packages = _distribution_rows()
    _require(
        current_packages == receipt["packages"],
        "installed package identity differs from the receipt",
    )
    _require(
        len(current_packages) == receipt["package_count"],
        "installed package count mismatch",
    )
    package_set_sha256 = hashlib.sha256(
        canonical_compact_json_bytes(current_packages)
    ).hexdigest()
    _require(
        package_set_sha256 == receipt["package_set_sha256"],
        "package-set hash mismatch",
    )
    _require(
        package_set_sha256 == expected["package_set_sha256"],
        "package set differs from the current binding",
    )

    hash_path = receipt_root / "environment_receipt.sha256"
    recorded_receipt_sha256 = hash_path.read_text(
        encoding="utf-8"
    ).split()[0]
    _require(
        recorded_receipt_sha256 == actual_receipt_sha256,
        "environment receipt sidecar hash mismatch",
    )
    expected_receipt_files = {
        "environment_content_manifest.jsonl",
        "environment_receipt.json",
        "environment_receipt.sha256",
    }
    actual_receipt_files = {
        path.name for path in receipt_root.iterdir() if path.is_file()
    }
    _require(
        actual_receipt_files == expected_receipt_files,
        "unexpected file in immutable receipt root",
    )
    for path in receipt_root.iterdir():
        if path.is_file():
            _require(
                not bool(path.stat().st_mode & stat.S_IWRITE),
                f"receipt file is writable: {path}",
            )

    return {
        "status": "PASS",
        "environment_receipt_sha256": actual_receipt_sha256,
        "environment_content_manifest_sha256": manifest_binding["sha256"],
        "environment_file_count": len(current_rows),
        "interpreter_sha256": interpreter["sha256"],
        "package_count": len(current_packages),
        "package_set_sha256": package_set_sha256,
    }
