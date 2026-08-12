from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_PREFIX = "iris_test_workflow_consolidation"


class ContractError(ValueError):
    """Raised when successor evidence is missing or internally inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(
            dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        + b"\n"
        for row in rows
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"cannot read JSON contract {path}: {error}") from error


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ContractError(f"cannot read JSONL contract {path}: {error}") from error
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ContractError(f"{path}:{number}: malformed JSON: {error}") from error
        require(isinstance(row, dict), f"{path}:{number}: row must be an object")
        rows.append(row)
    return rows


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_jsonl(rows))


def resolve_within(root: Path, value: str | Path) -> Path:
    resolved_root = root.resolve()
    candidate = (resolved_root / value).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ContractError(f"path escapes declared root: {value}") from error
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


def repository_root(path: Path) -> Path:
    return Path(git(path, "rev-parse", "--show-toplevel")).resolve()


def subject_identity(repo: Path, *, require_clean: bool = True) -> dict[str, Any]:
    identity: dict[str, Any] = {
        "commit": git(repo, "rev-parse", "HEAD"),
        "tree": git(repo, "rev-parse", "HEAD^{tree}"),
        "clean": not bool(git(repo, "status", "--short")),
    }
    if require_clean:
        require(identity["clean"], f"target checkout is dirty: {repo}")
    return identity


def interpreter_identity() -> dict[str, str]:
    return {
        "executable": str(Path(sys.executable).resolve()),
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "cache_tag": str(sys.implementation.cache_tag),
    }


def environment_identity() -> dict[str, Any]:
    selected_environment = {
        key: os.environ.get(key)
        for key in (
            "CI",
            "LANG",
            "LC_ALL",
            "PYTHONHASHSEED",
            "PYTHONUTF8",
            "TZ",
        )
    }
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "locale_encoding": sys.getdefaultencoding(),
        "filesystem_encoding": sys.getfilesystemencoding(),
        "selected_environment": selected_environment,
    }


def normalized_command_signature(
    argv: list[str], cwd: Path, environment_contract: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "executable": str(Path(argv[0]).resolve()) if argv else "",
        "ordered_argv": argv[1:],
        "cwd_role": "target_repository_root",
        "environment_contract": dict(environment_contract),
    }


def percentile(values: list[float], fraction: float) -> float:
    require(values, "cannot calculate a percentile of an empty sample")
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight

