"""Shared, dependency-free helpers for Iris clean-checkout validation."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


class CleanCheckoutError(RuntimeError):
    """Raised when a clean-checkout contract cannot be satisfied."""


def canonical_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


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
        ["git", "-C", str(repo), *args],
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
