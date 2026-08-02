#!/usr/bin/env python
"""Write an immutable role manifest for plan-local closeout evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_root_for(path: Path) -> Path:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip())
    return Path(completed.stdout.strip()).resolve()


def git_value(repository_root: Path, expression: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository_root), "rev-parse", expression],
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=True,
    ).stdout.strip()


def artifact_row(repository_root: Path, value: Path) -> dict[str, object]:
    path = (repository_root / value).resolve() if not value.is_absolute() else value.resolve()
    relative = path.relative_to(repository_root).as_posix()
    return {"path": relative, "sha256": sha256_file(path), "exists": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=("current", "historical", "diagnostic"), required=True)
    parser.add_argument("--producer", required=True)
    parser.add_argument("--producer-readpoint", required=True)
    parser.add_argument("--command-json", required=True)
    parser.add_argument("--input", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--subject-commit")
    parser.add_argument("--subject-tree")
    args = parser.parse_args()

    repository_root = repository_root_for(Path.cwd())
    command = json.loads(args.command_json)
    if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
        raise ValueError("--command-json must be a non-empty JSON string array")
    commit = args.subject_commit or git_value(repository_root, "HEAD")
    tree = args.subject_tree or git_value(repository_root, f"{commit}^{{tree}}")
    payload = {
        "schema_version": "iris-residual-evidence-role-v1",
        "role": args.role,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "producer": args.producer,
        "producer_readpoint": args.producer_readpoint,
        "command": command,
        "subject": {"commit": commit, "tree": tree, "overlay_sha256_or_null": None},
        "inputs": [artifact_row(repository_root, path) for path in args.input],
        "outputs": [artifact_row(repository_root, path) for path in args.output],
        "mutable": False,
        "supersedes": [],
        "authority_claim": False,
    }
    output = (repository_root / args.out).resolve() if not args.out.is_absolute() else args.out.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"role": args.role, "output_count": len(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
