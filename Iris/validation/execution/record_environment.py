"""Record an interpreter and installed wheel against their exact repository source."""

from __future__ import annotations

import argparse
import json
import os
import platform
import site
import stat
import subprocess
import sys
from pathlib import Path

from checkout_environment import (
    _distribution_rows,
    _environment_file_rows,
    canonical_compact_json_bytes,
    canonical_json_bytes,
    sha256_bytes,
    sha256_file,
)


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def _git_bytes(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            completed.stderr.decode("utf-8", errors="replace").strip()
            or f"git {' '.join(args)} failed"
        )
    return completed.stdout


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _repo_relative(repo: Path, path: Path) -> str:
    return path.resolve().relative_to(repo.resolve()).as_posix()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment-root", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-tree", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--authority-record-out", type=Path, required=True)
    parser.add_argument("--current-locator-out", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    environment_root = args.environment_root.resolve()
    project_path = args.project.resolve()
    lock_path = args.lock.resolve()
    wheel_path = args.wheel.resolve()
    receipt_path = args.out.resolve()
    authority_record_path = args.authority_record_out.resolve()
    locator_path = args.current_locator_out.resolve()
    repo = Path(
        _git(project_path.parent, "rev-parse", "--show-toplevel")
    ).resolve()

    if Path(sys.prefix).resolve() != environment_root:
        raise RuntimeError("writer must run from the target external environment")
    if Path(sys.base_prefix).resolve() == environment_root:
        raise RuntimeError("target interpreter is not a dedicated virtual environment")
    if _git(repo, "rev-parse", "HEAD") != args.source_commit:
        raise RuntimeError("source commit is not the exact writer checkout HEAD")
    if _git(repo, "rev-parse", "HEAD^{tree}") != args.source_tree:
        raise RuntimeError("source tree does not match the exact writer checkout")
    # The receipt binds superproject blobs/tree. A dirty nested worktree does
    # not alter that identity and may belong to an unrelated user-owned task.
    if _git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignore-submodules=dirty",
    ):
        raise RuntimeError("environment authority writer requires a clean implementation subject")

    project_relative = _repo_relative(repo, project_path)
    lock_relative = _repo_relative(repo, lock_path)
    source_relative = "Iris/tooling/src/iris_tooling"
    project_bytes = _git_bytes(repo, "show", f"{args.source_commit}:{project_relative}")
    lock_bytes = _git_bytes(repo, "show", f"{args.source_commit}:{lock_relative}")
    project_blob = _git(repo, "rev-parse", f"{args.source_commit}:{project_relative}")
    lock_blob = _git(repo, "rev-parse", f"{args.source_commit}:{lock_relative}")
    source_tree = _git(repo, "rev-parse", f"{args.source_commit}:{source_relative}")
    if _git(repo, "hash-object", f"--path={project_relative}", str(project_path)) != project_blob:
        raise RuntimeError("pyproject bytes differ from the implementation commit")
    if _git(repo, "hash-object", f"--path={lock_relative}", str(lock_path)) != lock_blob:
        raise RuntimeError("uv.lock bytes differ from the implementation commit")

    distributions = _distribution_rows()
    iris_distribution = next(
        (row for row in distributions if row["normalized_name"] == "iris_tooling"),
        None,
    )
    if iris_distribution is None:
        raise RuntimeError("installed iris-tooling distribution is missing")

    receipt_path.parent.mkdir(parents=True, exist_ok=False)
    environment_rows = _environment_file_rows(environment_root)
    manifest_bytes = b"".join(
        canonical_compact_json_bytes(row) for row in environment_rows
    )
    manifest_path = receipt_path.parent / "environment_content_manifest.jsonl"
    _write(manifest_path, manifest_bytes)
    pyvenv_path = environment_root / "pyvenv.cfg"
    package_set_sha256 = sha256_bytes(canonical_compact_json_bytes(distributions))
    receipt = {
        "schema_version": "iris_clean_checkout_external_environment_receipt_v1",
        "provisioning_mode": "wave_bound_exact_wheel_external_environment",
        "environment_root": environment_root.as_posix(),
        "interpreter": {
            "path": Path(sys.executable).resolve().as_posix(),
            "sha256": sha256_file(Path(sys.executable).resolve()),
            "base_interpreter_path": Path(sys._base_executable).resolve().as_posix(),
            "base_interpreter_sha256": sha256_file(Path(sys._base_executable).resolve()),
            "python_version": sys.version,
            "implementation": platform.python_implementation(),
            "architecture": platform.architecture()[0],
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "isolation": {
            "dedicated_virtual_environment": True,
            "include_system_site_packages": False,
            "python_no_user_site": os.environ.get("PYTHONNOUSERSITE") == "1",
            "python_path_cleared": not bool(os.environ.get("PYTHONPATH")),
            "user_site_enabled": bool(site.ENABLE_USER_SITE),
        },
        "pyvenv_cfg": {
            "path": "pyvenv.cfg",
            "sha256": sha256_file(pyvenv_path),
        },
        "environment_content_manifest": {
            "path": manifest_path.name,
            "sha256": sha256_bytes(manifest_bytes),
            "file_count": len(environment_rows),
        },
        "package_count": len(distributions),
        "package_set_sha256": package_set_sha256,
        "packages": distributions,
        "project_binding": {
            "source_commit": args.source_commit,
            "source_tree": args.source_tree,
            "source_package_path": source_relative,
            "source_package_git_tree": source_tree,
            "project_path": project_relative,
            "project_blob": project_blob,
            "project_sha256": sha256_bytes(project_bytes),
            "lock_path": lock_relative,
            "lock_blob": lock_blob,
            "lock_sha256": sha256_bytes(lock_bytes),
            "wheel_path": wheel_path.as_posix(),
            "wheel_sha256": sha256_file(wheel_path),
            "installed_distribution": iris_distribution,
        },
    }
    receipt_bytes = canonical_compact_json_bytes(receipt)
    _write(receipt_path, receipt_bytes)
    receipt_sha256 = sha256_bytes(receipt_bytes)
    sidecar = receipt_path.parent / "environment_receipt.sha256"
    _write(sidecar, f"{receipt_sha256}  {receipt_path.name}\n".encode("ascii"))
    for path in (manifest_path, receipt_path, sidecar):
        path.chmod(path.stat().st_mode & ~stat.S_IWRITE)

    wave_id = authority_record_path.stem.removeprefix(
        "responsibility_refactor_environment_"
    ).removesuffix("_v1")
    environment_contract = {
        "external_environment_root": environment_root.as_posix(),
        "interpreter_sha256": receipt["interpreter"]["sha256"],
        "immutable_environment_receipt_path": receipt_path.as_posix(),
        "immutable_environment_receipt_sha256": receipt_sha256,
        "environment_content_manifest_sha256": receipt["environment_content_manifest"]["sha256"],
        "package_set_sha256": package_set_sha256,
    }
    record = {
        "schema_version": "iris-responsibility-refactor-environment-authority-v1",
        "wave_id": wave_id,
        "implementation": {"commit": args.source_commit, "tree": args.source_tree},
        "project_binding": receipt["project_binding"],
        "environment_contract": environment_contract,
    }
    record_bytes = canonical_json_bytes(record)
    _write(authority_record_path, record_bytes)
    locator = {
        "schema_version": "iris-responsibility-refactor-environment-locator-v1",
        "record_path": _repo_relative(repo, authority_record_path),
        "record_sha256": sha256_bytes(record_bytes),
    }
    _write(locator_path, canonical_json_bytes(locator))
    print(f"environment authority created: wave={wave_id} receipt_sha256={receipt_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
