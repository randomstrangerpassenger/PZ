"""Stateless validation for a complete Layer 4 runtime projection."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .generate_layer4_runtime_projection import (
    CHUNK_ROOT_REL,
    DEFAULT_REPOSITORY_ROOT,
    FACADE_REL,
    Layer4GenerationError,
    render_projection,
)


class Layer4ValidationError(RuntimeError):
    pass


def _managed_paths(root: Path) -> set[Path]:
    paths: set[Path] = set()
    if (root / FACADE_REL).is_file():
        paths.add(FACADE_REL)
    chunk_root = root / CHUNK_ROOT_REL
    if chunk_root.is_dir():
        for path in chunk_root.iterdir():
            if path.is_file() and (
                re.fullmatch(r"Chunk\d{3}\.lua", path.name)
                or path.name in {"RequirementsLookup.lua", "ChunkIndex.lua", "LineCountIndex.lua"}
            ):
                paths.add(path.relative_to(root))
    return paths


def _assert_projection_bytes(root: Path, expected: dict[Path, bytes], label: str) -> None:
    actual_paths = _managed_paths(root)
    expected_paths = set(expected)
    if actual_paths != expected_paths:
        missing = sorted(str(path) for path in expected_paths - actual_paths)
        extra = sorted(str(path) for path in actual_paths - expected_paths)
        raise Layer4ValidationError(f"{label} file universe mismatch: missing={missing}, extra={extra}")
    mismatches = [str(path) for path, content in expected.items() if (root / path).read_bytes() != content]
    if mismatches:
        raise Layer4ValidationError(f"{label} source/order/schema mismatch: {mismatches}")


def validate_projection(
    candidate_root: Path,
    repository_root: Path,
    parity_root: Path | None = None,
) -> dict[str, int]:
    candidate_root = candidate_root.resolve()
    repository_root = repository_root.resolve()
    try:
        expected, metrics = render_projection(repository_root)
    except Layer4GenerationError as exc:
        raise Layer4ValidationError(str(exc)) from exc
    _assert_projection_bytes(candidate_root, expected, "candidate")

    recipe_lines = 0
    for relative_path in sorted(expected):
        if not relative_path.name.startswith("Chunk"):
            continue
        text = (candidate_root / relative_path).read_text(encoding="utf-8")
        for line in text.splitlines():
            if 'label_key = "uc.recipe.' not in line:
                continue
            recipe_lines += 1
            if not re.search(r", recipe_id = \"[^\"]+\"", line):
                raise Layer4ValidationError(f"{relative_path}: Recipe row lacks stable recipe_id")
            if not re.search(r"recipe_nav_ref = \{ recipe_id = \"[^\"]+\"", line):
                raise Layer4ValidationError(f"{relative_path}: navigation lacks stable recipe_id")
    if recipe_lines != metrics["recipe_row_count"]:
        raise Layer4ValidationError(
            f"Recipe row count mismatch: expected {metrics['recipe_row_count']}, got {recipe_lines}"
        )

    if parity_root is not None:
        _assert_projection_bytes(parity_root.resolve(), expected, "parity")
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", required=True, type=Path)
    parser.add_argument("--repository-root", type=Path, default=DEFAULT_REPOSITORY_ROOT)
    parser.add_argument("--parity-root", type=Path)
    args = parser.parse_args()
    try:
        metrics = validate_projection(args.candidate_root, args.repository_root, args.parity_root)
    except (Layer4ValidationError, OSError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print("PASS: Layer 4 runtime projection")
    print(json.dumps(metrics, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
