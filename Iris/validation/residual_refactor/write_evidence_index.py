#!/usr/bin/env python
"""Write a non-authoritative projection of residual-refactor evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    repository_root = repository_root_for(Path.cwd())
    evidence_root = (
        (repository_root / args.evidence_root).resolve()
        if not args.evidence_root.is_absolute()
        else args.evidence_root.resolve()
    )
    output = (
        (repository_root / args.out).resolve()
        if not args.out.is_absolute()
        else args.out.resolve()
    )
    rows: list[dict[str, Any]] = []
    for manifest_path in sorted(evidence_root.glob("*.evidence.json")):
        if manifest_path.resolve() == output:
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows.append(
            {
                "manifest_path": manifest_path.relative_to(repository_root).as_posix(),
                "manifest_sha256": sha256_file(manifest_path),
                "role": manifest.get("role"),
                "producer": manifest.get("producer"),
                "subject": manifest.get("subject"),
                "output_count": len(manifest.get("outputs", [])),
            }
        )
    payload = {
        "schema_version": "iris-residual-evidence-index-v1",
        "application_status": "applied",
        "validation_status": "passed",
        "authority_claim": False,
        "index_projection": True,
        "claim_boundary": (
            "convenience projection only; not Artifact Registry, seal, cutover, "
            "required-validation, or current authority"
        ),
        "evidence_root": evidence_root.relative_to(repository_root).as_posix(),
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "validation_status": "passed",
                "authority_claim": False,
                "row_count": len(rows),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
