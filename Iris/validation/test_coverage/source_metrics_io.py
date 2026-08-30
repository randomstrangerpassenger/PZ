"""Read test sources, measure function spans, and serialize coverage evidence."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


SCHEMA_PREFIX = "iris_test_precision_lightweighting"


class ContractError(ValueError):
    """Raised when round evidence is incomplete or inconsistent."""


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ContractError(f"{path}:{number}: JSONL row must be an object")
            rows.append(value)
    return rows


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = b"".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in rows
    )
    path.write_bytes(payload)


def repo_path(repo: Path, value: str | Path) -> Path:
    candidate = (repo / value).resolve()
    try:
        candidate.relative_to(repo.resolve())
    except ValueError as error:
        raise ContractError(f"path escapes repository: {value}") from error
    return candidate


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise ContractError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def subject_identity(repo: Path) -> dict[str, str]:
    return {
        "commit": git(repo, "rev-parse", "HEAD"),
        "tree": git(repo, "rev-parse", "HEAD^{tree}"),
    }


def physical_loc(path: Path) -> int:
    data = path.read_bytes()
    if not data:
        return 0
    return len(data.splitlines())


def ast_test_methods(path: Path) -> list[dict[str, Any]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rows: list[dict[str, Any]] = []
    for parent in ast.walk(tree):
        if not isinstance(parent, (ast.ClassDef, ast.Module)):
            continue
        owner = parent.name if isinstance(parent, ast.ClassDef) else None
        for node in parent.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                end = node.end_lineno or node.lineno
                rows.append({
                    "owner": owner,
                    "name": node.name,
                    "lineno": node.lineno,
                    "end_lineno": end,
                    "loc": end - node.lineno + 1,
                })
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def stable_set(value: Iterable[Any]) -> list[Any]:
    return sorted(set(value))
